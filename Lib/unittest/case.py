"""Test case implementation"""

zaimportuj sys
zaimportuj functools
zaimportuj difflib
zaimportuj logging
zaimportuj pprint
zaimportuj re
zaimportuj warnings
zaimportuj collections
zaimportuj contextlib
zaimportuj traceback

z . zaimportuj result
z .util zaimportuj (strclass, safe_repr, _count_diff_all_purpose,
                   _count_diff_hashable, _common_shorten_repr)

__unittest = Prawda


DIFF_OMITTED = ('\nDiff jest %s characters long. '
                 'Set self.maxDiff to Nic to see it.')

klasa SkipTest(Exception):
    """
    Raise this exception w a test to skip it.

    Usually you can use TestCase.skipTest() albo one of the skipping decorators
    instead of raising this directly.
    """

klasa _ShouldStop(Exception):
    """
    The test should stop.
    """

klasa _UnexpectedSuccess(Exception):
    """
    The test was supposed to fail, but it didn't!
    """


klasa _Outcome(object):
    def __init__(self, result=Nic):
        self.expecting_failure = Nieprawda
        self.result = result
        self.result_supports_subtests = hasattr(result, "addSubTest")
        self.success = Prawda
        self.skipped = []
        self.expectedFailure = Nic
        self.errors = []

    @contextlib.contextmanager
    def testPartExecutor(self, test_case, isTest=Nieprawda):
        old_success = self.success
        self.success = Prawda
        spróbuj:
            uzyskaj
        wyjąwszy KeyboardInterrupt:
            podnieś
        wyjąwszy SkipTest jako e:
            self.success = Nieprawda
            self.skipped.append((test_case, str(e)))
        wyjąwszy _ShouldStop:
            dalej
        wyjąwszy:
            exc_info = sys.exc_info()
            jeżeli self.expecting_failure:
                self.expectedFailure = exc_info
            inaczej:
                self.success = Nieprawda
                self.errors.append((test_case, exc_info))
            # explicitly przerwij a reference cycle:
            # exc_info -> frame -> exc_info
            exc_info = Nic
        inaczej:
            jeżeli self.result_supports_subtests oraz self.success:
                self.errors.append((test_case, Nic))
        w_końcu:
            self.success = self.success oraz old_success


def _id(obj):
    zwróć obj

def skip(reason):
    """
    Unconditionally skip a test.
    """
    def decorator(test_item):
        jeżeli nie isinstance(test_item, type):
            @functools.wraps(test_item)
            def skip_wrapper(*args, **kwargs):
                podnieś SkipTest(reason)
            test_item = skip_wrapper

        test_item.__unittest_skip__ = Prawda
        test_item.__unittest_skip_why__ = reason
        zwróć test_item
    zwróć decorator

def skipIf(condition, reason):
    """
    Skip a test jeżeli the condition jest true.
    """
    jeżeli condition:
        zwróć skip(reason)
    zwróć _id

def skipUnless(condition, reason):
    """
    Skip a test unless the condition jest true.
    """
    jeżeli nie condition:
        zwróć skip(reason)
    zwróć _id

def expectedFailure(test_item):
    test_item.__unittest_expecting_failure__ = Prawda
    zwróć test_item

def _is_subtype(expected, basetype):
    jeżeli isinstance(expected, tuple):
        zwróć all(_is_subtype(e, basetype) dla e w expected)
    zwróć isinstance(expected, type) oraz issubclass(expected, basetype)

klasa _BaseTestCaseContext:

    def __init__(self, test_case):
        self.test_case = test_case

    def _raiseFailure(self, standardMsg):
        msg = self.test_case._formatMessage(self.msg, standardMsg)
        podnieś self.test_case.failureException(msg)

klasa _AssertRaisesBaseContext(_BaseTestCaseContext):

    def __init__(self, expected, test_case, expected_regex=Nic):
        _BaseTestCaseContext.__init__(self, test_case)
        self.expected = expected
        self.test_case = test_case
        jeżeli expected_regex jest nie Nic:
            expected_regex = re.compile(expected_regex)
        self.expected_regex = expected_regex
        self.obj_name = Nic
        self.msg = Nic

    def handle(self, name, args, kwargs):
        """
        If args jest empty, assertRaises/Warns jest being used jako a
        context manager, so check dla a 'msg' kwarg oraz zwróć self.
        If args jest nie empty, call a callable dalejing positional oraz keyword
        arguments.
        """
        jeżeli nie _is_subtype(self.expected, self._base_type):
            podnieś TypeError('%s() arg 1 must be %s' %
                            (name, self._base_type_str))
        jeżeli args oraz args[0] jest Nic:
            warnings.warn("callable jest Nic",
                          DeprecationWarning, 3)
            args = ()
        jeżeli nie args:
            self.msg = kwargs.pop('msg', Nic)
            jeżeli kwargs:
                warnings.warn('%r jest an invalid keyword argument dla '
                              'this function' % next(iter(kwargs)),
                              DeprecationWarning, 3)
            zwróć self

        callable_obj, *args = args
        spróbuj:
            self.obj_name = callable_obj.__name__
        wyjąwszy AttributeError:
            self.obj_name = str(callable_obj)
        przy self:
            callable_obj(*args, **kwargs)


klasa _AssertRaisesContext(_AssertRaisesBaseContext):
    """A context manager used to implement TestCase.assertRaises* methods."""

    _base_type = BaseException
    _base_type_str = 'an exception type albo tuple of exception types'

    def __enter__(self):
        zwróć self

    def __exit__(self, exc_type, exc_value, tb):
        jeżeli exc_type jest Nic:
            spróbuj:
                exc_name = self.expected.__name__
            wyjąwszy AttributeError:
                exc_name = str(self.expected)
            jeżeli self.obj_name:
                self._raiseFailure("{} nie podnieśd by {}".format(exc_name,
                                                                self.obj_name))
            inaczej:
                self._raiseFailure("{} nie podnieśd".format(exc_name))
        inaczej:
            traceback.clear_frames(tb)
        jeżeli nie issubclass(exc_type, self.expected):
            # let unexpected exceptions dalej through
            zwróć Nieprawda
        # store exception, without traceback, dla later retrieval
        self.exception = exc_value.with_traceback(Nic)
        jeżeli self.expected_regex jest Nic:
            zwróć Prawda

        expected_regex = self.expected_regex
        jeżeli nie expected_regex.search(str(exc_value)):
            self._raiseFailure('"{}" does nie match "{}"'.format(
                     expected_regex.pattern, str(exc_value)))
        zwróć Prawda


klasa _AssertWarnsContext(_AssertRaisesBaseContext):
    """A context manager used to implement TestCase.assertWarns* methods."""

    _base_type = Warning
    _base_type_str = 'a warning type albo tuple of warning types'

    def __enter__(self):
        # The __warningregistry__'s need to be w a pristine state dla tests
        # to work properly.
        dla v w sys.modules.values():
            jeżeli getattr(v, '__warningregistry__', Nic):
                v.__warningregistry__ = {}
        self.warnings_manager = warnings.catch_warnings(record=Prawda)
        self.warnings = self.warnings_manager.__enter__()
        warnings.simplefilter("always", self.expected)
        zwróć self

    def __exit__(self, exc_type, exc_value, tb):
        self.warnings_manager.__exit__(exc_type, exc_value, tb)
        jeżeli exc_type jest nie Nic:
            # let unexpected exceptions dalej through
            zwróć
        spróbuj:
            exc_name = self.expected.__name__
        wyjąwszy AttributeError:
            exc_name = str(self.expected)
        first_matching = Nic
        dla m w self.warnings:
            w = m.message
            jeżeli nie isinstance(w, self.expected):
                kontynuuj
            jeżeli first_matching jest Nic:
                first_matching = w
            jeżeli (self.expected_regex jest nie Nic oraz
                nie self.expected_regex.search(str(w))):
                kontynuuj
            # store warning dla later retrieval
            self.warning = w
            self.filename = m.filename
            self.lineno = m.lineno
            zwróć
        # Now we simply try to choose a helpful failure message
        jeżeli first_matching jest nie Nic:
            self._raiseFailure('"{}" does nie match "{}"'.format(
                     self.expected_regex.pattern, str(first_matching)))
        jeżeli self.obj_name:
            self._raiseFailure("{} nie triggered by {}".format(exc_name,
                                                               self.obj_name))
        inaczej:
            self._raiseFailure("{} nie triggered".format(exc_name))



_LoggingWatcher = collections.namedtuple("_LoggingWatcher",
                                         ["records", "output"])


klasa _CapturingHandler(logging.Handler):
    """
    A logging handler capturing all (raw oraz formatted) logging output.
    """

    def __init__(self):
        logging.Handler.__init__(self)
        self.watcher = _LoggingWatcher([], [])

    def flush(self):
        dalej

    def emit(self, record):
        self.watcher.records.append(record)
        msg = self.format(record)
        self.watcher.output.append(msg)



klasa _AssertLogsContext(_BaseTestCaseContext):
    """A context manager used to implement TestCase.assertLogs()."""

    LOGGING_FORMAT = "%(levelname)s:%(name)s:%(message)s"

    def __init__(self, test_case, logger_name, level):
        _BaseTestCaseContext.__init__(self, test_case)
        self.logger_name = logger_name
        jeżeli level:
            self.level = logging._nameToLevel.get(level, level)
        inaczej:
            self.level = logging.INFO
        self.msg = Nic

    def __enter__(self):
        jeżeli isinstance(self.logger_name, logging.Logger):
            logger = self.logger = self.logger_name
        inaczej:
            logger = self.logger = logging.getLogger(self.logger_name)
        formatter = logging.Formatter(self.LOGGING_FORMAT)
        handler = _CapturingHandler()
        handler.setFormatter(formatter)
        self.watcher = handler.watcher
        self.old_handlers = logger.handlers[:]
        self.old_level = logger.level
        self.old_propagate = logger.propagate
        logger.handlers = [handler]
        logger.setLevel(self.level)
        logger.propagate = Nieprawda
        zwróć handler.watcher

    def __exit__(self, exc_type, exc_value, tb):
        self.logger.handlers = self.old_handlers
        self.logger.propagate = self.old_propagate
        self.logger.setLevel(self.old_level)
        jeżeli exc_type jest nie Nic:
            # let unexpected exceptions dalej through
            zwróć Nieprawda
        jeżeli len(self.watcher.records) == 0:
            self._raiseFailure(
                "no logs of level {} albo higher triggered on {}"
                .format(logging.getLevelName(self.level), self.logger.name))


klasa TestCase(object):
    """A klasa whose instances are single test cases.

    By default, the test code itself should be placed w a method named
    'runTest'.

    If the fixture may be used dla many test cases, create as
    many test methods jako are needed. When instantiating such a TestCase
    subclass, specify w the constructor arguments the name of the test method
    that the instance jest to execute.

    Test authors should subclass TestCase dla their own tests. Construction
    oraz deconstruction of the test's environment ('fixture') can be
    implemented by overriding the 'setUp' oraz 'tearDown' methods respectively.

    If it jest necessary to override the __init__ method, the base class
    __init__ method must always be called. It jest important that subclasses
    should nie change the signature of their __init__ method, since instances
    of the classes are instantiated automatically by parts of the framework
    w order to be run.

    When subclassing TestCase, you can set these attributes:
    * failureException: determines which exception will be podnieśd when
        the instance's assertion methods fail; test methods raising this
        exception will be deemed to have 'failed' rather than 'errored'.
    * longMessage: determines whether long messages (including repr of
        objects used w assert methods) will be printed on failure w *addition*
        to any explicit message dalejed.
    * maxDiff: sets the maximum length of a diff w failure messages
        by assert methods using difflib. It jest looked up jako an instance
        attribute so can be configured by individual tests jeżeli required.
    """

    failureException = AssertionError

    longMessage = Prawda

    maxDiff = 80*8

    # If a string jest longer than _diffThreshold, use normal comparison instead
    # of difflib.  See #11763.
    _diffThreshold = 2**16

    # Attribute used by TestSuite dla classSetUp

    _classSetupFailed = Nieprawda

    def __init__(self, methodName='runTest'):
        """Create an instance of the klasa that will use the named test
           method when executed. Raises a ValueError jeżeli the instance does
           nie have a method przy the specified name.
        """
        self._testMethodName = methodName
        self._outcome = Nic
        self._testMethodDoc = 'No test'
        spróbuj:
            testMethod = getattr(self, methodName)
        wyjąwszy AttributeError:
            jeżeli methodName != 'runTest':
                # we allow instantiation przy no explicit method name
                # but nie an *incorrect* albo missing method name
                podnieś ValueError("no such test method w %s: %s" %
                      (self.__class__, methodName))
        inaczej:
            self._testMethodDoc = testMethod.__doc__
        self._cleanups = []
        self._subtest = Nic

        # Map types to custom assertEqual functions that will compare
        # instances of said type w more detail to generate a more useful
        # error message.
        self._type_equality_funcs = {}
        self.addTypeEqualityFunc(dict, 'assertDictEqual')
        self.addTypeEqualityFunc(list, 'assertListEqual')
        self.addTypeEqualityFunc(tuple, 'assertTupleEqual')
        self.addTypeEqualityFunc(set, 'assertSetEqual')
        self.addTypeEqualityFunc(frozenset, 'assertSetEqual')
        self.addTypeEqualityFunc(str, 'assertMultiLineEqual')

    def addTypeEqualityFunc(self, typeobj, function):
        """Add a type specific assertEqual style function to compare a type.

        This method jest dla use by TestCase subclasses that need to register
        their own type equality functions to provide nicer error messages.

        Args:
            typeobj: The data type to call this function on when both values
                    are of the same type w assertEqual().
            function: The callable taking two arguments oraz an optional
                    msg= argument that podnieśs self.failureException przy a
                    useful error message when the two arguments are nie equal.
        """
        self._type_equality_funcs[typeobj] = function

    def addCleanup(self, function, *args, **kwargs):
        """Add a function, przy arguments, to be called when the test jest
        completed. Functions added are called on a LIFO basis oraz are
        called after tearDown on test failure albo success.

        Cleanup items are called even jeżeli setUp fails (unlike tearDown)."""
        self._cleanups.append((function, args, kwargs))

    def setUp(self):
        "Hook method dla setting up the test fixture before exercising it."
        dalej

    def tearDown(self):
        "Hook method dla deconstructing the test fixture after testing it."
        dalej

    @classmethod
    def setUpClass(cls):
        "Hook method dla setting up klasa fixture before running tests w the class."

    @classmethod
    def tearDownClass(cls):
        "Hook method dla deconstructing the klasa fixture after running all tests w the class."

    def countTestCases(self):
        zwróć 1

    def defaultTestResult(self):
        zwróć result.TestResult()

    def shortDescription(self):
        """Returns a one-line description of the test, albo Nic jeżeli no
        description has been provided.

        The default implementation of this method returns the first line of
        the specified test method's docstring.
        """
        doc = self._testMethodDoc
        zwróć doc oraz doc.split("\n")[0].strip() albo Nic


    def id(self):
        zwróć "%s.%s" % (strclass(self.__class__), self._testMethodName)

    def __eq__(self, other):
        jeżeli type(self) jest nie type(other):
            zwróć NotImplemented

        zwróć self._testMethodName == other._testMethodName

    def __hash__(self):
        zwróć hash((type(self), self._testMethodName))

    def __str__(self):
        zwróć "%s (%s)" % (self._testMethodName, strclass(self.__class__))

    def __repr__(self):
        zwróć "<%s testMethod=%s>" % \
               (strclass(self.__class__), self._testMethodName)

    def _addSkip(self, result, test_case, reason):
        addSkip = getattr(result, 'addSkip', Nic)
        jeżeli addSkip jest nie Nic:
            addSkip(test_case, reason)
        inaczej:
            warnings.warn("TestResult has no addSkip method, skips nie reported",
                          RuntimeWarning, 2)
            result.addSuccess(test_case)

    @contextlib.contextmanager
    def subTest(self, msg=Nic, **params):
        """Return a context manager that will zwróć the enclosed block
        of code w a subtest identified by the optional message oraz
        keyword parameters.  A failure w the subtest marks the test
        case jako failed but resumes execution at the end of the enclosed
        block, allowing further test code to be executed.
        """
        jeżeli nie self._outcome.result_supports_subtests:
            uzyskaj
            zwróć
        parent = self._subtest
        jeżeli parent jest Nic:
            params_map = collections.ChainMap(params)
        inaczej:
            params_map = parent.params.new_child(params)
        self._subtest = _SubTest(self, msg, params_map)
        spróbuj:
            przy self._outcome.testPartExecutor(self._subtest, isTest=Prawda):
                uzyskaj
            jeżeli nie self._outcome.success:
                result = self._outcome.result
                jeżeli result jest nie Nic oraz result.failfast:
                    podnieś _ShouldStop
            albo_inaczej self._outcome.expectedFailure:
                # If the test jest expecting a failure, we really want to
                # stop now oraz register the expected failure.
                podnieś _ShouldStop
        w_końcu:
            self._subtest = parent

    def _feedErrorsToResult(self, result, errors):
        dla test, exc_info w errors:
            jeżeli isinstance(test, _SubTest):
                result.addSubTest(test.test_case, test, exc_info)
            albo_inaczej exc_info jest nie Nic:
                jeżeli issubclass(exc_info[0], self.failureException):
                    result.addFailure(test, exc_info)
                inaczej:
                    result.addError(test, exc_info)

    def _addExpectedFailure(self, result, exc_info):
        spróbuj:
            addExpectedFailure = result.addExpectedFailure
        wyjąwszy AttributeError:
            warnings.warn("TestResult has no addExpectedFailure method, reporting jako dalejes",
                          RuntimeWarning)
            result.addSuccess(self)
        inaczej:
            addExpectedFailure(self, exc_info)

    def _addUnexpectedSuccess(self, result):
        spróbuj:
            addUnexpectedSuccess = result.addUnexpectedSuccess
        wyjąwszy AttributeError:
            warnings.warn("TestResult has no addUnexpectedSuccess method, reporting jako failure",
                          RuntimeWarning)
            # We need to dalej an actual exception oraz traceback to addFailure,
            # otherwise the legacy result can choke.
            spróbuj:
                podnieś _UnexpectedSuccess z Nic
            wyjąwszy _UnexpectedSuccess:
                result.addFailure(self, sys.exc_info())
        inaczej:
            addUnexpectedSuccess(self)

    def run(self, result=Nic):
        orig_result = result
        jeżeli result jest Nic:
            result = self.defaultTestResult()
            startTestRun = getattr(result, 'startTestRun', Nic)
            jeżeli startTestRun jest nie Nic:
                startTestRun()

        result.startTest(self)

        testMethod = getattr(self, self._testMethodName)
        jeżeli (getattr(self.__class__, "__unittest_skip__", Nieprawda) albo
            getattr(testMethod, "__unittest_skip__", Nieprawda)):
            # If the klasa albo method was skipped.
            spróbuj:
                skip_why = (getattr(self.__class__, '__unittest_skip_why__', '')
                            albo getattr(testMethod, '__unittest_skip_why__', ''))
                self._addSkip(result, self, skip_why)
            w_końcu:
                result.stopTest(self)
            zwróć
        expecting_failure = getattr(testMethod,
                                    "__unittest_expecting_failure__", Nieprawda)
        outcome = _Outcome(result)
        spróbuj:
            self._outcome = outcome

            przy outcome.testPartExecutor(self):
                self.setUp()
            jeżeli outcome.success:
                outcome.expecting_failure = expecting_failure
                przy outcome.testPartExecutor(self, isTest=Prawda):
                    testMethod()
                outcome.expecting_failure = Nieprawda
                przy outcome.testPartExecutor(self):
                    self.tearDown()

            self.doCleanups()
            dla test, reason w outcome.skipped:
                self._addSkip(result, test, reason)
            self._feedErrorsToResult(result, outcome.errors)
            jeżeli outcome.success:
                jeżeli expecting_failure:
                    jeżeli outcome.expectedFailure:
                        self._addExpectedFailure(result, outcome.expectedFailure)
                    inaczej:
                        self._addUnexpectedSuccess(result)
                inaczej:
                    result.addSuccess(self)
            zwróć result
        w_końcu:
            result.stopTest(self)
            jeżeli orig_result jest Nic:
                stopTestRun = getattr(result, 'stopTestRun', Nic)
                jeżeli stopTestRun jest nie Nic:
                    stopTestRun()

            # explicitly przerwij reference cycles:
            # outcome.errors -> frame -> outcome -> outcome.errors
            # outcome.expectedFailure -> frame -> outcome -> outcome.expectedFailure
            outcome.errors.clear()
            outcome.expectedFailure = Nic

            # clear the outcome, no more needed
            self._outcome = Nic

    def doCleanups(self):
        """Execute all cleanup functions. Normally called dla you after
        tearDown."""
        outcome = self._outcome albo _Outcome()
        dopóki self._cleanups:
            function, args, kwargs = self._cleanups.pop()
            przy outcome.testPartExecutor(self):
                function(*args, **kwargs)

        # zwróć this dla backwards compatibility
        # even though we no longer us it internally
        zwróć outcome.success

    def __call__(self, *args, **kwds):
        zwróć self.run(*args, **kwds)

    def debug(self):
        """Run the test without collecting errors w a TestResult"""
        self.setUp()
        getattr(self, self._testMethodName)()
        self.tearDown()
        dopóki self._cleanups:
            function, args, kwargs = self._cleanups.pop(-1)
            function(*args, **kwargs)

    def skipTest(self, reason):
        """Skip this test."""
        podnieś SkipTest(reason)

    def fail(self, msg=Nic):
        """Fail immediately, przy the given message."""
        podnieś self.failureException(msg)

    def assertNieprawda(self, expr, msg=Nic):
        """Check that the expression jest false."""
        jeżeli expr:
            msg = self._formatMessage(msg, "%s jest nie false" % safe_repr(expr))
            podnieś self.failureException(msg)

    def assertPrawda(self, expr, msg=Nic):
        """Check that the expression jest true."""
        jeżeli nie expr:
            msg = self._formatMessage(msg, "%s jest nie true" % safe_repr(expr))
            podnieś self.failureException(msg)

    def _formatMessage(self, msg, standardMsg):
        """Honour the longMessage attribute when generating failure messages.
        If longMessage jest Nieprawda this means:
        * Use only an explicit message jeżeli it jest provided
        * Otherwise use the standard message dla the assert

        If longMessage jest Prawda:
        * Use the standard message
        * If an explicit message jest provided, plus ' : ' oraz the explicit message
        """
        jeżeli nie self.longMessage:
            zwróć msg albo standardMsg
        jeżeli msg jest Nic:
            zwróć standardMsg
        spróbuj:
            # don't switch to '{}' formatting w Python 2.X
            # it changes the way unicode input jest handled
            zwróć '%s : %s' % (standardMsg, msg)
        wyjąwszy UnicodeDecodeError:
            zwróć  '%s : %s' % (safe_repr(standardMsg), safe_repr(msg))

    def assertRaises(self, expected_exception, *args, **kwargs):
        """Fail unless an exception of klasa expected_exception jest podnieśd
           by the callable when invoked przy specified positional oraz
           keyword arguments. If a different type of exception jest
           podnieśd, it will nie be caught, oraz the test case will be
           deemed to have suffered an error, exactly jako dla an
           unexpected exception.

           If called przy the callable oraz arguments omitted, will zwróć a
           context object used like this::

                przy self.assertRaises(SomeException):
                    do_something()

           An optional keyword argument 'msg' can be provided when assertRaises
           jest used jako a context object.

           The context manager keeps a reference to the exception as
           the 'exception' attribute. This allows you to inspect the
           exception after the assertion::

               przy self.assertRaises(SomeException) jako cm:
                   do_something()
               the_exception = cm.exception
               self.assertEqual(the_exception.error_code, 3)
        """
        context = _AssertRaisesContext(expected_exception, self)
        zwróć context.handle('assertRaises', args, kwargs)

    def assertWarns(self, expected_warning, *args, **kwargs):
        """Fail unless a warning of klasa warnClass jest triggered
           by the callable when invoked przy specified positional oraz
           keyword arguments.  If a different type of warning jest
           triggered, it will nie be handled: depending on the other
           warning filtering rules w effect, it might be silenced, printed
           out, albo podnieśd jako an exception.

           If called przy the callable oraz arguments omitted, will zwróć a
           context object used like this::

                przy self.assertWarns(SomeWarning):
                    do_something()

           An optional keyword argument 'msg' can be provided when assertWarns
           jest used jako a context object.

           The context manager keeps a reference to the first matching
           warning jako the 'warning' attribute; similarly, the 'filename'
           oraz 'lineno' attributes give you information about the line
           of Python code z which the warning was triggered.
           This allows you to inspect the warning after the assertion::

               przy self.assertWarns(SomeWarning) jako cm:
                   do_something()
               the_warning = cm.warning
               self.assertEqual(the_warning.some_attribute, 147)
        """
        context = _AssertWarnsContext(expected_warning, self)
        zwróć context.handle('assertWarns', args, kwargs)

    def assertLogs(self, logger=Nic, level=Nic):
        """Fail unless a log message of level *level* albo higher jest emitted
        on *logger_name* albo its children.  If omitted, *level* defaults to
        INFO oraz *logger* defaults to the root logger.

        This method must be used jako a context manager, oraz will uzyskaj
        a recording object przy two attributes: `output` oraz `records`.
        At the end of the context manager, the `output` attribute will
        be a list of the matching formatted log messages oraz the
        `records` attribute will be a list of the corresponding LogRecord
        objects.

        Example::

            przy self.assertLogs('foo', level='INFO') jako cm:
                logging.getLogger('foo').info('first message')
                logging.getLogger('foo.bar').error('second message')
            self.assertEqual(cm.output, ['INFO:foo:first message',
                                         'ERROR:foo.bar:second message'])
        """
        zwróć _AssertLogsContext(self, logger, level)

    def _getAssertEqualityFunc(self, first, second):
        """Get a detailed comparison function dla the types of the two args.

        Returns: A callable accepting (first, second, msg=Nic) that will
        podnieś a failure exception jeżeli first != second przy a useful human
        readable error message dla those types.
        """
        #
        # NOTE(gregory.p.smith): I considered isinstance(first, type(second))
        # oraz vice versa.  I opted dla the conservative approach w case
        # subclasses are nie intended to be compared w detail to their super
        # klasa instances using a type equality func.  This means testing
        # subtypes won't automagically use the detailed comparison.  Callers
        # should use their type specific assertSpamEqual method to compare
        # subclasses jeżeli the detailed comparison jest desired oraz appropriate.
        # See the discussion w http://bugs.python.org/issue2578.
        #
        jeżeli type(first) jest type(second):
            asserter = self._type_equality_funcs.get(type(first))
            jeżeli asserter jest nie Nic:
                jeżeli isinstance(asserter, str):
                    asserter = getattr(self, asserter)
                zwróć asserter

        zwróć self._baseAssertEqual

    def _baseAssertEqual(self, first, second, msg=Nic):
        """The default assertEqual implementation, nie type specific."""
        jeżeli nie first == second:
            standardMsg = '%s != %s' % _common_shorten_repr(first, second)
            msg = self._formatMessage(msg, standardMsg)
            podnieś self.failureException(msg)

    def assertEqual(self, first, second, msg=Nic):
        """Fail jeżeli the two objects are unequal jako determined by the '=='
           operator.
        """
        assertion_func = self._getAssertEqualityFunc(first, second)
        assertion_func(first, second, msg=msg)

    def assertNotEqual(self, first, second, msg=Nic):
        """Fail jeżeli the two objects are equal jako determined by the '!='
           operator.
        """
        jeżeli nie first != second:
            msg = self._formatMessage(msg, '%s == %s' % (safe_repr(first),
                                                          safe_repr(second)))
            podnieś self.failureException(msg)

    def assertAlmostEqual(self, first, second, places=Nic, msg=Nic,
                          delta=Nic):
        """Fail jeżeli the two objects are unequal jako determined by their
           difference rounded to the given number of decimal places
           (default 7) oraz comparing to zero, albo by comparing that the
           between the two objects jest more than the given delta.

           Note that decimal places (z zero) are usually nie the same
           jako significant digits (measured z the most signficant digit).

           If the two objects compare equal then they will automatically
           compare almost equal.
        """
        jeżeli first == second:
            # shortcut
            zwróć
        jeżeli delta jest nie Nic oraz places jest nie Nic:
            podnieś TypeError("specify delta albo places nie both")

        jeżeli delta jest nie Nic:
            jeżeli abs(first - second) <= delta:
                zwróć

            standardMsg = '%s != %s within %s delta' % (safe_repr(first),
                                                        safe_repr(second),
                                                        safe_repr(delta))
        inaczej:
            jeżeli places jest Nic:
                places = 7

            jeżeli round(abs(second-first), places) == 0:
                zwróć

            standardMsg = '%s != %s within %r places' % (safe_repr(first),
                                                          safe_repr(second),
                                                          places)
        msg = self._formatMessage(msg, standardMsg)
        podnieś self.failureException(msg)

    def assertNotAlmostEqual(self, first, second, places=Nic, msg=Nic,
                             delta=Nic):
        """Fail jeżeli the two objects are equal jako determined by their
           difference rounded to the given number of decimal places
           (default 7) oraz comparing to zero, albo by comparing that the
           between the two objects jest less than the given delta.

           Note that decimal places (z zero) are usually nie the same
           jako significant digits (measured z the most signficant digit).

           Objects that are equal automatically fail.
        """
        jeżeli delta jest nie Nic oraz places jest nie Nic:
            podnieś TypeError("specify delta albo places nie both")
        jeżeli delta jest nie Nic:
            jeżeli nie (first == second) oraz abs(first - second) > delta:
                zwróć
            standardMsg = '%s == %s within %s delta' % (safe_repr(first),
                                                        safe_repr(second),
                                                        safe_repr(delta))
        inaczej:
            jeżeli places jest Nic:
                places = 7
            jeżeli nie (first == second) oraz round(abs(second-first), places) != 0:
                zwróć
            standardMsg = '%s == %s within %r places' % (safe_repr(first),
                                                         safe_repr(second),
                                                         places)

        msg = self._formatMessage(msg, standardMsg)
        podnieś self.failureException(msg)


    def assertSequenceEqual(self, seq1, seq2, msg=Nic, seq_type=Nic):
        """An equality assertion dla ordered sequences (like lists oraz tuples).

        For the purposes of this function, a valid ordered sequence type jest one
        which can be indexed, has a length, oraz has an equality operator.

        Args:
            seq1: The first sequence to compare.
            seq2: The second sequence to compare.
            seq_type: The expected datatype of the sequences, albo Nic jeżeli no
                    datatype should be enforced.
            msg: Optional message to use on failure instead of a list of
                    differences.
        """
        jeżeli seq_type jest nie Nic:
            seq_type_name = seq_type.__name__
            jeżeli nie isinstance(seq1, seq_type):
                podnieś self.failureException('First sequence jest nie a %s: %s'
                                        % (seq_type_name, safe_repr(seq1)))
            jeżeli nie isinstance(seq2, seq_type):
                podnieś self.failureException('Second sequence jest nie a %s: %s'
                                        % (seq_type_name, safe_repr(seq2)))
        inaczej:
            seq_type_name = "sequence"

        differing = Nic
        spróbuj:
            len1 = len(seq1)
        wyjąwszy (TypeError, NotImplementedError):
            differing = 'First %s has no length.    Non-sequence?' % (
                    seq_type_name)

        jeżeli differing jest Nic:
            spróbuj:
                len2 = len(seq2)
            wyjąwszy (TypeError, NotImplementedError):
                differing = 'Second %s has no length.    Non-sequence?' % (
                        seq_type_name)

        jeżeli differing jest Nic:
            jeżeli seq1 == seq2:
                zwróć

            differing = '%ss differ: %s != %s\n' % (
                    (seq_type_name.capitalize(),) +
                    _common_shorten_repr(seq1, seq2))

            dla i w range(min(len1, len2)):
                spróbuj:
                    item1 = seq1[i]
                wyjąwszy (TypeError, IndexError, NotImplementedError):
                    differing += ('\nUnable to index element %d of first %s\n' %
                                 (i, seq_type_name))
                    przerwij

                spróbuj:
                    item2 = seq2[i]
                wyjąwszy (TypeError, IndexError, NotImplementedError):
                    differing += ('\nUnable to index element %d of second %s\n' %
                                 (i, seq_type_name))
                    przerwij

                jeżeli item1 != item2:
                    differing += ('\nFirst differing element %d:\n%s\n%s\n' %
                                 (i, item1, item2))
                    przerwij
            inaczej:
                jeżeli (len1 == len2 oraz seq_type jest Nic oraz
                    type(seq1) != type(seq2)):
                    # The sequences are the same, but have differing types.
                    zwróć

            jeżeli len1 > len2:
                differing += ('\nFirst %s contains %d additional '
                             'elements.\n' % (seq_type_name, len1 - len2))
                spróbuj:
                    differing += ('First extra element %d:\n%s\n' %
                                  (len2, seq1[len2]))
                wyjąwszy (TypeError, IndexError, NotImplementedError):
                    differing += ('Unable to index element %d '
                                  'of first %s\n' % (len2, seq_type_name))
            albo_inaczej len1 < len2:
                differing += ('\nSecond %s contains %d additional '
                             'elements.\n' % (seq_type_name, len2 - len1))
                spróbuj:
                    differing += ('First extra element %d:\n%s\n' %
                                  (len1, seq2[len1]))
                wyjąwszy (TypeError, IndexError, NotImplementedError):
                    differing += ('Unable to index element %d '
                                  'of second %s\n' % (len1, seq_type_name))
        standardMsg = differing
        diffMsg = '\n' + '\n'.join(
            difflib.ndiff(pprint.pformat(seq1).splitlines(),
                          pprint.pformat(seq2).splitlines()))

        standardMsg = self._truncateMessage(standardMsg, diffMsg)
        msg = self._formatMessage(msg, standardMsg)
        self.fail(msg)

    def _truncateMessage(self, message, diff):
        max_diff = self.maxDiff
        jeżeli max_diff jest Nic albo len(diff) <= max_diff:
            zwróć message + diff
        zwróć message + (DIFF_OMITTED % len(diff))

    def assertListEqual(self, list1, list2, msg=Nic):
        """A list-specific equality assertion.

        Args:
            list1: The first list to compare.
            list2: The second list to compare.
            msg: Optional message to use on failure instead of a list of
                    differences.

        """
        self.assertSequenceEqual(list1, list2, msg, seq_type=list)

    def assertTupleEqual(self, tuple1, tuple2, msg=Nic):
        """A tuple-specific equality assertion.

        Args:
            tuple1: The first tuple to compare.
            tuple2: The second tuple to compare.
            msg: Optional message to use on failure instead of a list of
                    differences.
        """
        self.assertSequenceEqual(tuple1, tuple2, msg, seq_type=tuple)

    def assertSetEqual(self, set1, set2, msg=Nic):
        """A set-specific equality assertion.

        Args:
            set1: The first set to compare.
            set2: The second set to compare.
            msg: Optional message to use on failure instead of a list of
                    differences.

        assertSetEqual uses ducktyping to support different types of sets, oraz
        jest optimized dla sets specifically (parameters must support a
        difference method).
        """
        spróbuj:
            difference1 = set1.difference(set2)
        wyjąwszy TypeError jako e:
            self.fail('invalid type when attempting set difference: %s' % e)
        wyjąwszy AttributeError jako e:
            self.fail('first argument does nie support set difference: %s' % e)

        spróbuj:
            difference2 = set2.difference(set1)
        wyjąwszy TypeError jako e:
            self.fail('invalid type when attempting set difference: %s' % e)
        wyjąwszy AttributeError jako e:
            self.fail('second argument does nie support set difference: %s' % e)

        jeżeli nie (difference1 albo difference2):
            zwróć

        lines = []
        jeżeli difference1:
            lines.append('Items w the first set but nie the second:')
            dla item w difference1:
                lines.append(repr(item))
        jeżeli difference2:
            lines.append('Items w the second set but nie the first:')
            dla item w difference2:
                lines.append(repr(item))

        standardMsg = '\n'.join(lines)
        self.fail(self._formatMessage(msg, standardMsg))

    def assertIn(self, member, container, msg=Nic):
        """Just like self.assertPrawda(a w b), but przy a nicer default message."""
        jeżeli member nie w container:
            standardMsg = '%s nie found w %s' % (safe_repr(member),
                                                  safe_repr(container))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertNotIn(self, member, container, msg=Nic):
        """Just like self.assertPrawda(a nie w b), but przy a nicer default message."""
        jeżeli member w container:
            standardMsg = '%s unexpectedly found w %s' % (safe_repr(member),
                                                        safe_repr(container))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertIs(self, expr1, expr2, msg=Nic):
        """Just like self.assertPrawda(a jest b), but przy a nicer default message."""
        jeżeli expr1 jest nie expr2:
            standardMsg = '%s jest nie %s' % (safe_repr(expr1),
                                             safe_repr(expr2))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertIsNot(self, expr1, expr2, msg=Nic):
        """Just like self.assertPrawda(a jest nie b), but przy a nicer default message."""
        jeżeli expr1 jest expr2:
            standardMsg = 'unexpectedly identical: %s' % (safe_repr(expr1),)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertDictEqual(self, d1, d2, msg=Nic):
        self.assertIsInstance(d1, dict, 'First argument jest nie a dictionary')
        self.assertIsInstance(d2, dict, 'Second argument jest nie a dictionary')

        jeżeli d1 != d2:
            standardMsg = '%s != %s' % _common_shorten_repr(d1, d2)
            diff = ('\n' + '\n'.join(difflib.ndiff(
                           pprint.pformat(d1).splitlines(),
                           pprint.pformat(d2).splitlines())))
            standardMsg = self._truncateMessage(standardMsg, diff)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertDictContainsSubset(self, subset, dictionary, msg=Nic):
        """Checks whether dictionary jest a superset of subset."""
        warnings.warn('assertDictContainsSubset jest deprecated',
                      DeprecationWarning)
        missing = []
        mismatched = []
        dla key, value w subset.items():
            jeżeli key nie w dictionary:
                missing.append(key)
            albo_inaczej value != dictionary[key]:
                mismatched.append('%s, expected: %s, actual: %s' %
                                  (safe_repr(key), safe_repr(value),
                                   safe_repr(dictionary[key])))

        jeżeli nie (missing albo mismatched):
            zwróć

        standardMsg = ''
        jeżeli missing:
            standardMsg = 'Missing: %s' % ','.join(safe_repr(m) dla m w
                                                    missing)
        jeżeli mismatched:
            jeżeli standardMsg:
                standardMsg += '; '
            standardMsg += 'Mismatched values: %s' % ','.join(mismatched)

        self.fail(self._formatMessage(msg, standardMsg))


    def assertCountEqual(self, first, second, msg=Nic):
        """An unordered sequence comparison asserting that the same elements,
        regardless of order.  If the same element occurs more than once,
        it verifies that the elements occur the same number of times.

            self.assertEqual(Counter(list(first)),
                             Counter(list(second)))

         Example:
            - [0, 1, 1] oraz [1, 0, 1] compare equal.
            - [0, 0, 1] oraz [0, 1] compare unequal.

        """
        first_seq, second_seq = list(first), list(second)
        spróbuj:
            first = collections.Counter(first_seq)
            second = collections.Counter(second_seq)
        wyjąwszy TypeError:
            # Handle case przy unhashable elements
            differences = _count_diff_all_purpose(first_seq, second_seq)
        inaczej:
            jeżeli first == second:
                zwróć
            differences = _count_diff_hashable(first_seq, second_seq)

        jeżeli differences:
            standardMsg = 'Element counts were nie equal:\n'
            lines = ['First has %d, Second has %d:  %r' % diff dla diff w differences]
            diffMsg = '\n'.join(lines)
            standardMsg = self._truncateMessage(standardMsg, diffMsg)
            msg = self._formatMessage(msg, standardMsg)
            self.fail(msg)

    def assertMultiLineEqual(self, first, second, msg=Nic):
        """Assert that two multi-line strings are equal."""
        self.assertIsInstance(first, str, 'First argument jest nie a string')
        self.assertIsInstance(second, str, 'Second argument jest nie a string')

        jeżeli first != second:
            # don't use difflib jeżeli the strings are too long
            jeżeli (len(first) > self._diffThreshold albo
                len(second) > self._diffThreshold):
                self._baseAssertEqual(first, second, msg)
            firstlines = first.splitlines(keepends=Prawda)
            secondlines = second.splitlines(keepends=Prawda)
            jeżeli len(firstlines) == 1 oraz first.strip('\r\n') == first:
                firstlines = [first + '\n']
                secondlines = [second + '\n']
            standardMsg = '%s != %s' % _common_shorten_repr(first, second)
            diff = '\n' + ''.join(difflib.ndiff(firstlines, secondlines))
            standardMsg = self._truncateMessage(standardMsg, diff)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertLess(self, a, b, msg=Nic):
        """Just like self.assertPrawda(a < b), but przy a nicer default message."""
        jeżeli nie a < b:
            standardMsg = '%s nie less than %s' % (safe_repr(a), safe_repr(b))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertLessEqual(self, a, b, msg=Nic):
        """Just like self.assertPrawda(a <= b), but przy a nicer default message."""
        jeżeli nie a <= b:
            standardMsg = '%s nie less than albo equal to %s' % (safe_repr(a), safe_repr(b))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertGreater(self, a, b, msg=Nic):
        """Just like self.assertPrawda(a > b), but przy a nicer default message."""
        jeżeli nie a > b:
            standardMsg = '%s nie greater than %s' % (safe_repr(a), safe_repr(b))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertGreaterEqual(self, a, b, msg=Nic):
        """Just like self.assertPrawda(a >= b), but przy a nicer default message."""
        jeżeli nie a >= b:
            standardMsg = '%s nie greater than albo equal to %s' % (safe_repr(a), safe_repr(b))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertIsNic(self, obj, msg=Nic):
        """Same jako self.assertPrawda(obj jest Nic), przy a nicer default message."""
        jeżeli obj jest nie Nic:
            standardMsg = '%s jest nie Nic' % (safe_repr(obj),)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertIsNotNic(self, obj, msg=Nic):
        """Included dla symmetry przy assertIsNic."""
        jeżeli obj jest Nic:
            standardMsg = 'unexpectedly Nic'
            self.fail(self._formatMessage(msg, standardMsg))

    def assertIsInstance(self, obj, cls, msg=Nic):
        """Same jako self.assertPrawda(isinstance(obj, cls)), przy a nicer
        default message."""
        jeżeli nie isinstance(obj, cls):
            standardMsg = '%s jest nie an instance of %r' % (safe_repr(obj), cls)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertNotIsInstance(self, obj, cls, msg=Nic):
        """Included dla symmetry przy assertIsInstance."""
        jeżeli isinstance(obj, cls):
            standardMsg = '%s jest an instance of %r' % (safe_repr(obj), cls)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertRaisesRegex(self, expected_exception, expected_regex,
                          *args, **kwargs):
        """Asserts that the message w a podnieśd exception matches a regex.

        Args:
            expected_exception: Exception klasa expected to be podnieśd.
            expected_regex: Regex (re pattern object albo string) expected
                    to be found w error message.
            args: Function to be called oraz extra positional args.
            kwargs: Extra kwargs.
            msg: Optional message used w case of failure. Can only be used
                    when assertRaisesRegex jest used jako a context manager.
        """
        context = _AssertRaisesContext(expected_exception, self, expected_regex)
        zwróć context.handle('assertRaisesRegex', args, kwargs)

    def assertWarnsRegex(self, expected_warning, expected_regex,
                         *args, **kwargs):
        """Asserts that the message w a triggered warning matches a regexp.
        Basic functioning jest similar to assertWarns() przy the addition
        that only warnings whose messages also match the regular expression
        are considered successful matches.

        Args:
            expected_warning: Warning klasa expected to be triggered.
            expected_regex: Regex (re pattern object albo string) expected
                    to be found w error message.
            args: Function to be called oraz extra positional args.
            kwargs: Extra kwargs.
            msg: Optional message used w case of failure. Can only be used
                    when assertWarnsRegex jest used jako a context manager.
        """
        context = _AssertWarnsContext(expected_warning, self, expected_regex)
        zwróć context.handle('assertWarnsRegex', args, kwargs)

    def assertRegex(self, text, expected_regex, msg=Nic):
        """Fail the test unless the text matches the regular expression."""
        jeżeli isinstance(expected_regex, (str, bytes)):
            assert expected_regex, "expected_regex must nie be empty."
            expected_regex = re.compile(expected_regex)
        jeżeli nie expected_regex.search(text):
            msg = msg albo "Regex didn't match"
            msg = '%s: %r nie found w %r' % (msg, expected_regex.pattern, text)
            podnieś self.failureException(msg)

    def assertNotRegex(self, text, unexpected_regex, msg=Nic):
        """Fail the test jeżeli the text matches the regular expression."""
        jeżeli isinstance(unexpected_regex, (str, bytes)):
            unexpected_regex = re.compile(unexpected_regex)
        match = unexpected_regex.search(text)
        jeżeli match:
            msg = msg albo "Regex matched"
            msg = '%s: %r matches %r w %r' % (msg,
                                               text[match.start():match.end()],
                                               unexpected_regex.pattern,
                                               text)
            podnieś self.failureException(msg)


    def _deprecate(original_func):
        def deprecated_func(*args, **kwargs):
            warnings.warn(
                'Please use {0} instead.'.format(original_func.__name__),
                DeprecationWarning, 2)
            zwróć original_func(*args, **kwargs)
        zwróć deprecated_func

    # see #9424
    failUnlessEqual = assertEquals = _deprecate(assertEqual)
    failIfEqual = assertNotEquals = _deprecate(assertNotEqual)
    failUnlessAlmostEqual = assertAlmostEquals = _deprecate(assertAlmostEqual)
    failIfAlmostEqual = assertNotAlmostEquals = _deprecate(assertNotAlmostEqual)
    failUnless = assert_ = _deprecate(assertPrawda)
    failUnlessRaises = _deprecate(assertRaises)
    failIf = _deprecate(assertNieprawda)
    assertRaisesRegexp = _deprecate(assertRaisesRegex)
    assertRegexpMatches = _deprecate(assertRegex)



klasa FunctionTestCase(TestCase):
    """A test case that wraps a test function.

    This jest useful dla slipping pre-existing test functions into the
    unittest framework. Optionally, set-up oraz tidy-up functions can be
    supplied. As przy TestCase, the tidy-up ('tearDown') function will
    always be called jeżeli the set-up ('setUp') function ran successfully.
    """

    def __init__(self, testFunc, setUp=Nic, tearDown=Nic, description=Nic):
        super(FunctionTestCase, self).__init__()
        self._setUpFunc = setUp
        self._tearDownFunc = tearDown
        self._testFunc = testFunc
        self._description = description

    def setUp(self):
        jeżeli self._setUpFunc jest nie Nic:
            self._setUpFunc()

    def tearDown(self):
        jeżeli self._tearDownFunc jest nie Nic:
            self._tearDownFunc()

    def runTest(self):
        self._testFunc()

    def id(self):
        zwróć self._testFunc.__name__

    def __eq__(self, other):
        jeżeli nie isinstance(other, self.__class__):
            zwróć NotImplemented

        zwróć self._setUpFunc == other._setUpFunc oraz \
               self._tearDownFunc == other._tearDownFunc oraz \
               self._testFunc == other._testFunc oraz \
               self._description == other._description

    def __hash__(self):
        zwróć hash((type(self), self._setUpFunc, self._tearDownFunc,
                     self._testFunc, self._description))

    def __str__(self):
        zwróć "%s (%s)" % (strclass(self.__class__),
                            self._testFunc.__name__)

    def __repr__(self):
        zwróć "<%s tec=%s>" % (strclass(self.__class__),
                                     self._testFunc)

    def shortDescription(self):
        jeżeli self._description jest nie Nic:
            zwróć self._description
        doc = self._testFunc.__doc__
        zwróć doc oraz doc.split("\n")[0].strip() albo Nic


klasa _SubTest(TestCase):

    def __init__(self, test_case, message, params):
        super().__init__()
        self._message = message
        self.test_case = test_case
        self.params = params
        self.failureException = test_case.failureException

    def runTest(self):
        podnieś NotImplementedError("subtests cannot be run directly")

    def _subDescription(self):
        parts = []
        jeżeli self._message:
            parts.append("[{}]".format(self._message))
        jeżeli self.params:
            params_desc = ', '.join(
                "{}={!r}".format(k, v)
                dla (k, v) w sorted(self.params.items()))
            parts.append("({})".format(params_desc))
        zwróć " ".join(parts) albo '(<subtest>)'

    def id(self):
        zwróć "{} {}".format(self.test_case.id(), self._subDescription())

    def shortDescription(self):
        """Returns a one-line description of the subtest, albo Nic jeżeli no
        description has been provided.
        """
        zwróć self.test_case.shortDescription()

    def __str__(self):
        zwróć "{} {}".format(self.test_case, self._subDescription())
