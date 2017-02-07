"""TestSuite"""

zaimportuj sys

z . zaimportuj case
z . zaimportuj util

__unittest = Prawda


def _call_if_exists(parent, attr):
    func = getattr(parent, attr, lambda: Nic)
    func()


klasa BaseTestSuite(object):
    """A simple test suite that doesn't provide klasa albo module shared fixtures.
    """
    _cleanup = Prawda

    def __init__(self, tests=()):
        self._tests = []
        self._removed_tests = 0
        self.addTests(tests)

    def __repr__(self):
        zwróć "<%s tests=%s>" % (util.strclass(self.__class__), list(self))

    def __eq__(self, other):
        jeżeli nie isinstance(other, self.__class__):
            zwróć NotImplemented
        zwróć list(self) == list(other)

    def __iter__(self):
        zwróć iter(self._tests)

    def countTestCases(self):
        cases = self._removed_tests
        dla test w self:
            jeżeli test:
                cases += test.countTestCases()
        zwróć cases

    def addTest(self, test):
        # sanity checks
        jeżeli nie callable(test):
            podnieś TypeError("{} jest nie callable".format(repr(test)))
        jeżeli isinstance(test, type) oraz issubclass(test,
                                                 (case.TestCase, TestSuite)):
            podnieś TypeError("TestCases oraz TestSuites must be instantiated "
                            "before dalejing them to addTest()")
        self._tests.append(test)

    def addTests(self, tests):
        jeżeli isinstance(tests, str):
            podnieś TypeError("tests must be an iterable of tests, nie a string")
        dla test w tests:
            self.addTest(test)

    def run(self, result):
        dla index, test w enumerate(self):
            jeżeli result.shouldStop:
                przerwij
            test(result)
            jeżeli self._cleanup:
                self._removeTestAtIndex(index)
        zwróć result

    def _removeTestAtIndex(self, index):
        """Stop holding a reference to the TestCase at index."""
        spróbuj:
            test = self._tests[index]
        wyjąwszy TypeError:
            # support dla suite implementations that have overriden self._tests
            dalej
        inaczej:
            # Some unittest tests add non TestCase/TestSuite objects to
            # the suite.
            jeżeli hasattr(test, 'countTestCases'):
                self._removed_tests += test.countTestCases()
            self._tests[index] = Nic

    def __call__(self, *args, **kwds):
        zwróć self.run(*args, **kwds)

    def debug(self):
        """Run the tests without collecting errors w a TestResult"""
        dla test w self:
            test.debug()


klasa TestSuite(BaseTestSuite):
    """A test suite jest a composite test consisting of a number of TestCases.

    For use, create an instance of TestSuite, then add test case instances.
    When all tests have been added, the suite can be dalejed to a test
    runner, such jako TextTestRunner. It will run the individual test cases
    w the order w which they were added, aggregating the results. When
    subclassing, do nie forget to call the base klasa constructor.
    """

    def run(self, result, debug=Nieprawda):
        topLevel = Nieprawda
        jeżeli getattr(result, '_testRunEntered', Nieprawda) jest Nieprawda:
            result._testRunEntered = topLevel = Prawda

        dla index, test w enumerate(self):
            jeżeli result.shouldStop:
                przerwij

            jeżeli _isnotsuite(test):
                self._tearDownPreviousClass(test, result)
                self._handleModuleFixture(test, result)
                self._handleClassSetUp(test, result)
                result._previousTestClass = test.__class__

                jeżeli (getattr(test.__class__, '_classSetupFailed', Nieprawda) albo
                    getattr(result, '_moduleSetUpFailed', Nieprawda)):
                    kontynuuj

            jeżeli nie debug:
                test(result)
            inaczej:
                test.debug()

            jeżeli self._cleanup:
                self._removeTestAtIndex(index)

        jeżeli topLevel:
            self._tearDownPreviousClass(Nic, result)
            self._handleModuleTearDown(result)
            result._testRunEntered = Nieprawda
        zwróć result

    def debug(self):
        """Run the tests without collecting errors w a TestResult"""
        debug = _DebugResult()
        self.run(debug, Prawda)

    ################################

    def _handleClassSetUp(self, test, result):
        previousClass = getattr(result, '_previousTestClass', Nic)
        currentClass = test.__class__
        jeżeli currentClass == previousClass:
            zwróć
        jeżeli result._moduleSetUpFailed:
            zwróć
        jeżeli getattr(currentClass, "__unittest_skip__", Nieprawda):
            zwróć

        spróbuj:
            currentClass._classSetupFailed = Nieprawda
        wyjąwszy TypeError:
            # test may actually be a function
            # so its klasa will be a builtin-type
            dalej

        setUpClass = getattr(currentClass, 'setUpClass', Nic)
        jeżeli setUpClass jest nie Nic:
            _call_if_exists(result, '_setupStdout')
            spróbuj:
                setUpClass()
            wyjąwszy Exception jako e:
                jeżeli isinstance(result, _DebugResult):
                    podnieś
                currentClass._classSetupFailed = Prawda
                className = util.strclass(currentClass)
                errorName = 'setUpClass (%s)' % className
                self._addClassOrModuleLevelException(result, e, errorName)
            w_końcu:
                _call_if_exists(result, '_restoreStdout')

    def _get_previous_module(self, result):
        previousModule = Nic
        previousClass = getattr(result, '_previousTestClass', Nic)
        jeżeli previousClass jest nie Nic:
            previousModule = previousClass.__module__
        zwróć previousModule


    def _handleModuleFixture(self, test, result):
        previousModule = self._get_previous_module(result)
        currentModule = test.__class__.__module__
        jeżeli currentModule == previousModule:
            zwróć

        self._handleModuleTearDown(result)


        result._moduleSetUpFailed = Nieprawda
        spróbuj:
            module = sys.modules[currentModule]
        wyjąwszy KeyError:
            zwróć
        setUpModule = getattr(module, 'setUpModule', Nic)
        jeżeli setUpModule jest nie Nic:
            _call_if_exists(result, '_setupStdout')
            spróbuj:
                setUpModule()
            wyjąwszy Exception jako e:
                jeżeli isinstance(result, _DebugResult):
                    podnieś
                result._moduleSetUpFailed = Prawda
                errorName = 'setUpModule (%s)' % currentModule
                self._addClassOrModuleLevelException(result, e, errorName)
            w_końcu:
                _call_if_exists(result, '_restoreStdout')

    def _addClassOrModuleLevelException(self, result, exception, errorName):
        error = _ErrorHolder(errorName)
        addSkip = getattr(result, 'addSkip', Nic)
        jeżeli addSkip jest nie Nic oraz isinstance(exception, case.SkipTest):
            addSkip(error, str(exception))
        inaczej:
            result.addError(error, sys.exc_info())

    def _handleModuleTearDown(self, result):
        previousModule = self._get_previous_module(result)
        jeżeli previousModule jest Nic:
            zwróć
        jeżeli result._moduleSetUpFailed:
            zwróć

        spróbuj:
            module = sys.modules[previousModule]
        wyjąwszy KeyError:
            zwróć

        tearDownModule = getattr(module, 'tearDownModule', Nic)
        jeżeli tearDownModule jest nie Nic:
            _call_if_exists(result, '_setupStdout')
            spróbuj:
                tearDownModule()
            wyjąwszy Exception jako e:
                jeżeli isinstance(result, _DebugResult):
                    podnieś
                errorName = 'tearDownModule (%s)' % previousModule
                self._addClassOrModuleLevelException(result, e, errorName)
            w_końcu:
                _call_if_exists(result, '_restoreStdout')

    def _tearDownPreviousClass(self, test, result):
        previousClass = getattr(result, '_previousTestClass', Nic)
        currentClass = test.__class__
        jeżeli currentClass == previousClass:
            zwróć
        jeżeli getattr(previousClass, '_classSetupFailed', Nieprawda):
            zwróć
        jeżeli getattr(result, '_moduleSetUpFailed', Nieprawda):
            zwróć
        jeżeli getattr(previousClass, "__unittest_skip__", Nieprawda):
            zwróć

        tearDownClass = getattr(previousClass, 'tearDownClass', Nic)
        jeżeli tearDownClass jest nie Nic:
            _call_if_exists(result, '_setupStdout')
            spróbuj:
                tearDownClass()
            wyjąwszy Exception jako e:
                jeżeli isinstance(result, _DebugResult):
                    podnieś
                className = util.strclass(previousClass)
                errorName = 'tearDownClass (%s)' % className
                self._addClassOrModuleLevelException(result, e, errorName)
            w_końcu:
                _call_if_exists(result, '_restoreStdout')


klasa _ErrorHolder(object):
    """
    Placeholder dla a TestCase inside a result. As far jako a TestResult
    jest concerned, this looks exactly like a unit test. Used to insert
    arbitrary errors into a test suite run.
    """
    # Inspired by the ErrorHolder z Twisted:
    # http://twistedmatrix.com/trac/browser/trunk/twisted/trial/runner.py

    # attribute used by TestResult._exc_info_to_string
    failureException = Nic

    def __init__(self, description):
        self.description = description

    def id(self):
        zwróć self.description

    def shortDescription(self):
        zwróć Nic

    def __repr__(self):
        zwróć "<ErrorHolder description=%r>" % (self.description,)

    def __str__(self):
        zwróć self.id()

    def run(self, result):
        # could call result.addError(...) - but this test-like object
        # shouldn't be run anyway
        dalej

    def __call__(self, result):
        zwróć self.run(result)

    def countTestCases(self):
        zwróć 0

def _isnotsuite(test):
    "A crude way to tell apart testcases oraz suites przy duck-typing"
    spróbuj:
        iter(test)
    wyjąwszy TypeError:
        zwróć Prawda
    zwróć Nieprawda


klasa _DebugResult(object):
    "Used by the TestSuite to hold previous klasa when running w debug."
    _previousTestClass = Nic
    _moduleSetUpFailed = Nieprawda
    shouldStop = Nieprawda
