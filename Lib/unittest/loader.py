"""Loading unittests."""

zaimportuj os
zaimportuj re
zaimportuj sys
zaimportuj traceback
zaimportuj types
zaimportuj functools
zaimportuj warnings

z fnmatch zaimportuj fnmatch

z . zaimportuj case, suite, util

__unittest = Prawda

# what about .pyc (etc)
# we would need to avoid loading the same tests multiple times
# z '.py', *and* '.pyc'
VALID_MODULE_NAME = re.compile(r'[_a-z]\w*\.py$', re.IGNORECASE)


klasa _FailedTest(case.TestCase):
    _testMethodName = Nic

    def __init__(self, method_name, exception):
        self._exception = exception
        super(_FailedTest, self).__init__(method_name)

    def __getattr__(self, name):
        jeżeli name != self._testMethodName:
            zwróć super(_FailedTest, self).__getattr__(name)
        def testFailure():
            podnieś self._exception
        zwróć testFailure


def _make_failed_import_test(name, suiteClass):
    message = 'Failed to zaimportuj test module: %s\n%s' % (
        name, traceback.format_exc())
    zwróć _make_failed_test(name, ImportError(message), suiteClass, message)

def _make_failed_load_tests(name, exception, suiteClass):
    message = 'Failed to call load_tests:\n%s' % (traceback.format_exc(),)
    zwróć _make_failed_test(
        name, exception, suiteClass, message)

def _make_failed_test(methodname, exception, suiteClass, message):
    test = _FailedTest(methodname, exception)
    zwróć suiteClass((test,)), message

def _make_skipped_test(methodname, exception, suiteClass):
    @case.skip(str(exception))
    def testSkipped(self):
        dalej
    attrs = {methodname: testSkipped}
    TestClass = type("ModuleSkipped", (case.TestCase,), attrs)
    zwróć suiteClass((TestClass(methodname),))

def _jython_aware_splitext(path):
    jeżeli path.lower().endswith('$py.class'):
        zwróć path[:-9]
    zwróć os.path.splitext(path)[0]


klasa TestLoader(object):
    """
    This klasa jest responsible dla loading tests according to various criteria
    oraz returning them wrapped w a TestSuite
    """
    testMethodPrefix = 'test'
    sortTestMethodsUsing = staticmethod(util.three_way_cmp)
    suiteClass = suite.TestSuite
    _top_level_dir = Nic

    def __init__(self):
        super(TestLoader, self).__init__()
        self.errors = []
        # Tracks packages which we have called into via load_tests, to
        # avoid infinite re-entrancy.
        self._loading_packages = set()

    def loadTestsFromTestCase(self, testCaseClass):
        """Return a suite of all tests cases contained w testCaseClass"""
        jeżeli issubclass(testCaseClass, suite.TestSuite):
            podnieś TypeError("Test cases should nie be derived z "
                            "TestSuite. Maybe you meant to derive z "
                            "TestCase?")
        testCaseNames = self.getTestCaseNames(testCaseClass)
        jeżeli nie testCaseNames oraz hasattr(testCaseClass, 'runTest'):
            testCaseNames = ['runTest']
        loaded_suite = self.suiteClass(map(testCaseClass, testCaseNames))
        zwróć loaded_suite

    # XXX After Python 3.5, remove backward compatibility hacks for
    # use_load_tests deprecation via *args oraz **kws.  See issue 16662.
    def loadTestsFromModule(self, module, *args, pattern=Nic, **kws):
        """Return a suite of all tests cases contained w the given module"""
        # This method used to take an undocumented oraz unofficial
        # use_load_tests argument.  For backward compatibility, we still
        # accept the argument (which can also be the first position) but we
        # ignore it oraz issue a deprecation warning jeżeli it's present.
        jeżeli len(args) > 0 albo 'use_load_tests' w kws:
            warnings.warn('use_load_tests jest deprecated oraz ignored',
                          DeprecationWarning)
            kws.pop('use_load_tests', Nic)
        jeżeli len(args) > 1:
            # Complain about the number of arguments, but don't forget the
            # required `module` argument.
            complaint = len(args) + 1
            podnieś TypeError('loadTestsFromModule() takes 1 positional argument but {} were given'.format(complaint))
        jeżeli len(kws) != 0:
            # Since the keyword arguments are unsorted (see PEP 468), just
            # pick the alphabetically sorted first argument to complain about,
            # jeżeli multiple were given.  At least the error message will be
            # predictable.
            complaint = sorted(kws)[0]
            podnieś TypeError("loadTestsFromModule() got an unexpected keyword argument '{}'".format(complaint))
        tests = []
        dla name w dir(module):
            obj = getattr(module, name)
            jeżeli isinstance(obj, type) oraz issubclass(obj, case.TestCase):
                tests.append(self.loadTestsFromTestCase(obj))

        load_tests = getattr(module, 'load_tests', Nic)
        tests = self.suiteClass(tests)
        jeżeli load_tests jest nie Nic:
            spróbuj:
                zwróć load_tests(self, tests, pattern)
            wyjąwszy Exception jako e:
                error_case, error_message = _make_failed_load_tests(
                    module.__name__, e, self.suiteClass)
                self.errors.append(error_message)
                zwróć error_case
        zwróć tests

    def loadTestsFromName(self, name, module=Nic):
        """Return a suite of all tests cases given a string specifier.

        The name may resolve either to a module, a test case class, a
        test method within a test case class, albo a callable object which
        returns a TestCase albo TestSuite instance.

        The method optionally resolves the names relative to a given module.
        """
        parts = name.split('.')
        error_case, error_message = Nic, Nic
        jeżeli module jest Nic:
            parts_copy = parts[:]
            dopóki parts_copy:
                spróbuj:
                    module_name = '.'.join(parts_copy)
                    module = __import__(module_name)
                    przerwij
                wyjąwszy ImportError:
                    next_attribute = parts_copy.pop()
                    # Last error so we can give it to the user jeżeli needed.
                    error_case, error_message = _make_failed_import_test(
                        next_attribute, self.suiteClass)
                    jeżeli nie parts_copy:
                        # Even the top level zaimportuj failed: report that error.
                        self.errors.append(error_message)
                        zwróć error_case
            parts = parts[1:]
        obj = module
        dla part w parts:
            spróbuj:
                parent, obj = obj, getattr(obj, part)
            wyjąwszy AttributeError jako e:
                # We can't traverse some part of the name.
                jeżeli (getattr(obj, '__path__', Nic) jest nie Nic
                    oraz error_case jest nie Nic):
                    # This jest a package (no __path__ per importlib docs), oraz we
                    # encountered an error importing something. We cannot tell
                    # the difference between package.WrongNameTestClass oraz
                    # package.wrong_module_name so we just report the
                    # ImportError - it jest more informative.
                    self.errors.append(error_message)
                    zwróć error_case
                inaczej:
                    # Otherwise, we signal that an AttributeError has occurred.
                    error_case, error_message = _make_failed_test(
                        part, e, self.suiteClass,
                        'Failed to access attribute:\n%s' % (
                            traceback.format_exc(),))
                    self.errors.append(error_message)
                    zwróć error_case

        jeżeli isinstance(obj, types.ModuleType):
            zwróć self.loadTestsFromModule(obj)
        albo_inaczej isinstance(obj, type) oraz issubclass(obj, case.TestCase):
            zwróć self.loadTestsFromTestCase(obj)
        albo_inaczej (isinstance(obj, types.FunctionType) oraz
              isinstance(parent, type) oraz
              issubclass(parent, case.TestCase)):
            name = parts[-1]
            inst = parent(name)
            # static methods follow a different path
            jeżeli nie isinstance(getattr(inst, name), types.FunctionType):
                zwróć self.suiteClass([inst])
        albo_inaczej isinstance(obj, suite.TestSuite):
            zwróć obj
        jeżeli callable(obj):
            test = obj()
            jeżeli isinstance(test, suite.TestSuite):
                zwróć test
            albo_inaczej isinstance(test, case.TestCase):
                zwróć self.suiteClass([test])
            inaczej:
                podnieś TypeError("calling %s returned %s, nie a test" %
                                (obj, test))
        inaczej:
            podnieś TypeError("don't know how to make test from: %s" % obj)

    def loadTestsFromNames(self, names, module=Nic):
        """Return a suite of all tests cases found using the given sequence
        of string specifiers. See 'loadTestsFromName()'.
        """
        suites = [self.loadTestsFromName(name, module) dla name w names]
        zwróć self.suiteClass(suites)

    def getTestCaseNames(self, testCaseClass):
        """Return a sorted sequence of method names found within testCaseClass
        """
        def isTestMethod(attrname, testCaseClass=testCaseClass,
                         prefix=self.testMethodPrefix):
            zwróć attrname.startswith(prefix) oraz \
                callable(getattr(testCaseClass, attrname))
        testFnNames = list(filter(isTestMethod, dir(testCaseClass)))
        jeżeli self.sortTestMethodsUsing:
            testFnNames.sort(key=functools.cmp_to_key(self.sortTestMethodsUsing))
        zwróć testFnNames

    def discover(self, start_dir, pattern='test*.py', top_level_dir=Nic):
        """Find oraz zwróć all test modules z the specified start
        directory, recursing into subdirectories to find them oraz zwróć all
        tests found within them. Only test files that match the pattern will
        be loaded. (Using shell style pattern matching.)

        All test modules must be importable z the top level of the project.
        If the start directory jest nie the top level directory then the top
        level directory must be specified separately.

        If a test package name (directory przy '__init__.py') matches the
        pattern then the package will be checked dla a 'load_tests' function. If
        this exists then it will be called przy (loader, tests, pattern) unless
        the package has already had load_tests called z the same discovery
        invocation, w which case the package module object jest nie scanned for
        tests - this ensures that when a package uses discover to further
        discover child tests that infinite recursion does nie happen.

        If load_tests exists then discovery does *not* recurse into the package,
        load_tests jest responsible dla loading all tests w the package.

        The pattern jest deliberately nie stored jako a loader attribute so that
        packages can continue discovery themselves. top_level_dir jest stored so
        load_tests does nie need to dalej this argument w to loader.discover().

        Paths are sorted before being imported to ensure reproducible execution
        order even on filesystems przy non-alphabetical ordering like ext3/4.
        """
        set_implicit_top = Nieprawda
        jeżeli top_level_dir jest Nic oraz self._top_level_dir jest nie Nic:
            # make top_level_dir optional jeżeli called z load_tests w a package
            top_level_dir = self._top_level_dir
        albo_inaczej top_level_dir jest Nic:
            set_implicit_top = Prawda
            top_level_dir = start_dir

        top_level_dir = os.path.abspath(top_level_dir)

        jeżeli nie top_level_dir w sys.path:
            # all test modules must be importable z the top level directory
            # should we *unconditionally* put the start directory w first
            # w sys.path to minimise likelihood of conflicts between installed
            # modules oraz development versions?
            sys.path.insert(0, top_level_dir)
        self._top_level_dir = top_level_dir

        is_not_importable = Nieprawda
        is_namespace = Nieprawda
        tests = []
        jeżeli os.path.isdir(os.path.abspath(start_dir)):
            start_dir = os.path.abspath(start_dir)
            jeżeli start_dir != top_level_dir:
                is_not_importable = nie os.path.isfile(os.path.join(start_dir, '__init__.py'))
        inaczej:
            # support dla discovery z dotted module names
            spróbuj:
                __import__(start_dir)
            wyjąwszy ImportError:
                is_not_importable = Prawda
            inaczej:
                the_module = sys.modules[start_dir]
                top_part = start_dir.split('.')[0]
                spróbuj:
                    start_dir = os.path.abspath(
                       os.path.dirname((the_module.__file__)))
                wyjąwszy AttributeError:
                    # look dla namespace packages
                    spróbuj:
                        spec = the_module.__spec__
                    wyjąwszy AttributeError:
                        spec = Nic

                    jeżeli spec oraz spec.loader jest Nic:
                        jeżeli spec.submodule_search_locations jest nie Nic:
                            is_namespace = Prawda

                            dla path w the_module.__path__:
                                jeżeli (nie set_implicit_top oraz
                                    nie path.startswith(top_level_dir)):
                                    kontynuuj
                                self._top_level_dir = \
                                    (path.split(the_module.__name__
                                         .replace(".", os.path.sep))[0])
                                tests.extend(self._find_tests(path,
                                                              pattern,
                                                              namespace=Prawda))
                    albo_inaczej the_module.__name__ w sys.builtin_module_names:
                        # builtin module
                        podnieś TypeError('Can nie use builtin modules '
                                        'as dotted module names') z Nic
                    inaczej:
                        podnieś TypeError(
                            'don\'t know how to discover z {!r}'
                            .format(the_module)) z Nic

                jeżeli set_implicit_top:
                    jeżeli nie is_namespace:
                        self._top_level_dir = \
                           self._get_directory_containing_module(top_part)
                        sys.path.remove(top_level_dir)
                    inaczej:
                        sys.path.remove(top_level_dir)

        jeżeli is_not_importable:
            podnieś ImportError('Start directory jest nie importable: %r' % start_dir)

        jeżeli nie is_namespace:
            tests = list(self._find_tests(start_dir, pattern))
        zwróć self.suiteClass(tests)

    def _get_directory_containing_module(self, module_name):
        module = sys.modules[module_name]
        full_path = os.path.abspath(module.__file__)

        jeżeli os.path.basename(full_path).lower().startswith('__init__.py'):
            zwróć os.path.dirname(os.path.dirname(full_path))
        inaczej:
            # here we have been given a module rather than a package - so
            # all we can do jest search the *same* directory the module jest w
            # should an exception be podnieśd instead
            zwróć os.path.dirname(full_path)

    def _get_name_from_path(self, path):
        jeżeli path == self._top_level_dir:
            zwróć '.'
        path = _jython_aware_splitext(os.path.normpath(path))

        _relpath = os.path.relpath(path, self._top_level_dir)
        assert nie os.path.isabs(_relpath), "Path must be within the project"
        assert nie _relpath.startswith('..'), "Path must be within the project"

        name = _relpath.replace(os.path.sep, '.')
        zwróć name

    def _get_module_from_name(self, name):
        __import__(name)
        zwróć sys.modules[name]

    def _match_path(self, path, full_path, pattern):
        # override this method to use alternative matching strategy
        zwróć fnmatch(path, pattern)

    def _find_tests(self, start_dir, pattern, namespace=Nieprawda):
        """Used by discovery. Yields test suites it loads."""
        # Handle the __init__ w this package
        name = self._get_name_from_path(start_dir)
        # name jest '.' when start_dir == top_level_dir (and top_level_dir jest by
        # definition nie a package).
        jeżeli name != '.' oraz name nie w self._loading_packages:
            # name jest w self._loading_packages dopóki we have called into
            # loadTestsFromModule przy name.
            tests, should_recurse = self._find_test_path(
                start_dir, pattern, namespace)
            jeżeli tests jest nie Nic:
                uzyskaj tests
            jeżeli nie should_recurse:
                # Either an error occured, albo load_tests was used by the
                # package.
                zwróć
        # Handle the contents.
        paths = sorted(os.listdir(start_dir))
        dla path w paths:
            full_path = os.path.join(start_dir, path)
            tests, should_recurse = self._find_test_path(
                full_path, pattern, namespace)
            jeżeli tests jest nie Nic:
                uzyskaj tests
            jeżeli should_recurse:
                # we found a package that didn't use load_tests.
                name = self._get_name_from_path(full_path)
                self._loading_packages.add(name)
                spróbuj:
                    uzyskaj z self._find_tests(full_path, pattern, namespace)
                w_końcu:
                    self._loading_packages.discard(name)

    def _find_test_path(self, full_path, pattern, namespace=Nieprawda):
        """Used by discovery.

        Loads tests z a single file, albo a directories' __init__.py when
        dalejed the directory.

        Returns a tuple (Nic_or_tests_from_file, should_recurse).
        """
        basename = os.path.basename(full_path)
        jeżeli os.path.isfile(full_path):
            jeżeli nie VALID_MODULE_NAME.match(basename):
                # valid Python identifiers only
                zwróć Nic, Nieprawda
            jeżeli nie self._match_path(basename, full_path, pattern):
                zwróć Nic, Nieprawda
            # jeżeli the test file matches, load it
            name = self._get_name_from_path(full_path)
            spróbuj:
                module = self._get_module_from_name(name)
            wyjąwszy case.SkipTest jako e:
                zwróć _make_skipped_test(name, e, self.suiteClass), Nieprawda
            wyjąwszy:
                error_case, error_message = \
                    _make_failed_import_test(name, self.suiteClass)
                self.errors.append(error_message)
                zwróć error_case, Nieprawda
            inaczej:
                mod_file = os.path.abspath(
                    getattr(module, '__file__', full_path))
                realpath = _jython_aware_splitext(
                    os.path.realpath(mod_file))
                fullpath_noext = _jython_aware_splitext(
                    os.path.realpath(full_path))
                jeżeli realpath.lower() != fullpath_noext.lower():
                    module_dir = os.path.dirname(realpath)
                    mod_name = _jython_aware_splitext(
                        os.path.basename(full_path))
                    expected_dir = os.path.dirname(full_path)
                    msg = ("%r module incorrectly imported z %r. Expected "
                           "%r. Is this module globally installed?")
                    podnieś ImportError(
                        msg % (mod_name, module_dir, expected_dir))
                zwróć self.loadTestsFromModule(module, pattern=pattern), Nieprawda
        albo_inaczej os.path.isdir(full_path):
            jeżeli (nie namespace oraz
                nie os.path.isfile(os.path.join(full_path, '__init__.py'))):
                zwróć Nic, Nieprawda

            load_tests = Nic
            tests = Nic
            name = self._get_name_from_path(full_path)
            spróbuj:
                package = self._get_module_from_name(name)
            wyjąwszy case.SkipTest jako e:
                zwróć _make_skipped_test(name, e, self.suiteClass), Nieprawda
            wyjąwszy:
                error_case, error_message = \
                    _make_failed_import_test(name, self.suiteClass)
                self.errors.append(error_message)
                zwróć error_case, Nieprawda
            inaczej:
                load_tests = getattr(package, 'load_tests', Nic)
                # Mark this package jako being w load_tests (possibly ;))
                self._loading_packages.add(name)
                spróbuj:
                    tests = self.loadTestsFromModule(package, pattern=pattern)
                    jeżeli load_tests jest nie Nic:
                        # loadTestsFromModule(package) has loaded tests dla us.
                        zwróć tests, Nieprawda
                    zwróć tests, Prawda
                w_końcu:
                    self._loading_packages.discard(name)


defaultTestLoader = TestLoader()


def _makeLoader(prefix, sortUsing, suiteClass=Nic):
    loader = TestLoader()
    loader.sortTestMethodsUsing = sortUsing
    loader.testMethodPrefix = prefix
    jeżeli suiteClass:
        loader.suiteClass = suiteClass
    zwróć loader

def getTestCaseNames(testCaseClass, prefix, sortUsing=util.three_way_cmp):
    zwróć _makeLoader(prefix, sortUsing).getTestCaseNames(testCaseClass)

def makeSuite(testCaseClass, prefix='test', sortUsing=util.three_way_cmp,
              suiteClass=suite.TestSuite):
    zwróć _makeLoader(prefix, sortUsing, suiteClass).loadTestsFromTestCase(
        testCaseClass)

def findTestCases(module, prefix='test', sortUsing=util.three_way_cmp,
                  suiteClass=suite.TestSuite):
    zwróć _makeLoader(prefix, sortUsing, suiteClass).loadTestsFromModule(\
        module)
