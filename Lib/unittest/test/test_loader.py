zaimportuj sys
zaimportuj types
zaimportuj warnings

zaimportuj unittest

# Decorator used w the deprecation tests to reset the warning registry for
# test isolation oraz reproducibility.
def warningregistry(func):
    def wrapper(*args, **kws):
        missing = object()
        saved = getattr(warnings, '__warningregistry__', missing).copy()
        spróbuj:
            zwróć func(*args, **kws)
        w_końcu:
            jeżeli saved jest missing:
                spróbuj:
                    usuń warnings.__warningregistry__
                wyjąwszy AttributeError:
                    dalej
            inaczej:
                warnings.__warningregistry__ = saved


klasa Test_TestLoader(unittest.TestCase):

    ### Basic object tests
    ################################################################

    def test___init__(self):
        loader = unittest.TestLoader()
        self.assertEqual([], loader.errors)

    ### Tests dla TestLoader.loadTestsFromTestCase
    ################################################################

    # "Return a suite of all tests cases contained w the TestCase-derived
    # klasa testCaseClass"
    def test_loadTestsFromTestCase(self):
        klasa Foo(unittest.TestCase):
            def test_1(self): dalej
            def test_2(self): dalej
            def foo_bar(self): dalej

        tests = unittest.TestSuite([Foo('test_1'), Foo('test_2')])

        loader = unittest.TestLoader()
        self.assertEqual(loader.loadTestsFromTestCase(Foo), tests)

    # "Return a suite of all tests cases contained w the TestCase-derived
    # klasa testCaseClass"
    #
    # Make sure it does the right thing even jeżeli no tests were found
    def test_loadTestsFromTestCase__no_matches(self):
        klasa Foo(unittest.TestCase):
            def foo_bar(self): dalej

        empty_suite = unittest.TestSuite()

        loader = unittest.TestLoader()
        self.assertEqual(loader.loadTestsFromTestCase(Foo), empty_suite)

    # "Return a suite of all tests cases contained w the TestCase-derived
    # klasa testCaseClass"
    #
    # What happens jeżeli loadTestsFromTestCase() jest given an object
    # that isn't a subclass of TestCase? Specifically, what happens
    # jeżeli testCaseClass jest a subclass of TestSuite?
    #
    # This jest checked dla specifically w the code, so we better add a
    # test dla it.
    def test_loadTestsFromTestCase__TestSuite_subclass(self):
        klasa NotATestCase(unittest.TestSuite):
            dalej

        loader = unittest.TestLoader()
        spróbuj:
            loader.loadTestsFromTestCase(NotATestCase)
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail('Should podnieś TypeError')

    # "Return a suite of all tests cases contained w the TestCase-derived
    # klasa testCaseClass"
    #
    # Make sure loadTestsFromTestCase() picks up the default test method
    # name (as specified by TestCase), even though the method name does
    # nie match the default TestLoader.testMethodPrefix string
    def test_loadTestsFromTestCase__default_method_name(self):
        klasa Foo(unittest.TestCase):
            def runTest(self):
                dalej

        loader = unittest.TestLoader()
        # This has to be false dla the test to succeed
        self.assertNieprawda('runTest'.startswith(loader.testMethodPrefix))

        suite = loader.loadTestsFromTestCase(Foo)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [Foo('runTest')])

    ################################################################
    ### /Tests dla TestLoader.loadTestsFromTestCase

    ### Tests dla TestLoader.loadTestsFromModule
    ################################################################

    # "This method searches `module` dla classes derived z TestCase"
    def test_loadTestsFromModule__TestCase_subclass(self):
        m = types.ModuleType('m')
        klasa MyTestCase(unittest.TestCase):
            def test(self):
                dalej
        m.testcase_1 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(m)
        self.assertIsInstance(suite, loader.suiteClass)

        expected = [loader.suiteClass([MyTestCase('test')])]
        self.assertEqual(list(suite), expected)

    # "This method searches `module` dla classes derived z TestCase"
    #
    # What happens jeżeli no tests are found (no TestCase instances)?
    def test_loadTestsFromModule__no_TestCase_instances(self):
        m = types.ModuleType('m')

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(m)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [])

    # "This method searches `module` dla classes derived z TestCase"
    #
    # What happens jeżeli no tests are found (TestCases instances, but no tests)?
    def test_loadTestsFromModule__no_TestCase_tests(self):
        m = types.ModuleType('m')
        klasa MyTestCase(unittest.TestCase):
            dalej
        m.testcase_1 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(m)
        self.assertIsInstance(suite, loader.suiteClass)

        self.assertEqual(list(suite), [loader.suiteClass()])

    # "This method searches `module` dla classes derived z TestCase"s
    #
    # What happens jeżeli loadTestsFromModule() jest given something other
    # than a module?
    #
    # XXX Currently, it succeeds anyway. This flexibility
    # should either be documented albo loadTestsFromModule() should
    # podnieś a TypeError
    #
    # XXX Certain people are using this behaviour. We'll add a test dla it
    def test_loadTestsFromModule__not_a_module(self):
        klasa MyTestCase(unittest.TestCase):
            def test(self):
                dalej

        klasa NotAModule(object):
            test_2 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(NotAModule)

        reference = [unittest.TestSuite([MyTestCase('test')])]
        self.assertEqual(list(suite), reference)


    # Check that loadTestsFromModule honors (or not) a module
    # przy a load_tests function.
    @warningregistry
    def test_loadTestsFromModule__load_tests(self):
        m = types.ModuleType('m')
        klasa MyTestCase(unittest.TestCase):
            def test(self):
                dalej
        m.testcase_1 = MyTestCase

        load_tests_args = []
        def load_tests(loader, tests, pattern):
            self.assertIsInstance(tests, unittest.TestSuite)
            load_tests_args.extend((loader, tests, pattern))
            zwróć tests
        m.load_tests = load_tests

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(m)
        self.assertIsInstance(suite, unittest.TestSuite)
        self.assertEqual(load_tests_args, [loader, suite, Nic])
        # With Python 3.5, the undocumented oraz unofficial use_load_tests jest
        # ignored (and deprecated).
        load_tests_args = []
        przy warnings.catch_warnings(record=Nieprawda):
            warnings.simplefilter('never')
            suite = loader.loadTestsFromModule(m, use_load_tests=Nieprawda)
            self.assertEqual(load_tests_args, [loader, suite, Nic])

    @warningregistry
    def test_loadTestsFromModule__use_load_tests_deprecated_positional(self):
        m = types.ModuleType('m')
        klasa MyTestCase(unittest.TestCase):
            def test(self):
                dalej
        m.testcase_1 = MyTestCase

        load_tests_args = []
        def load_tests(loader, tests, pattern):
            self.assertIsInstance(tests, unittest.TestSuite)
            load_tests_args.extend((loader, tests, pattern))
            zwróć tests
        m.load_tests = load_tests
        # The method still works.
        loader = unittest.TestLoader()
        # use_load_tests=Prawda jako a positional argument.
        przy warnings.catch_warnings(record=Prawda) jako w:
            warnings.simplefilter('always')
            suite = loader.loadTestsFromModule(m, Nieprawda)
            self.assertIsInstance(suite, unittest.TestSuite)
            # load_tests was still called because use_load_tests jest deprecated
            # oraz ignored.
            self.assertEqual(load_tests_args, [loader, suite, Nic])
        # We got a warning.
        self.assertIs(w[-1].category, DeprecationWarning)
        self.assertEqual(str(w[-1].message),
                             'use_load_tests jest deprecated oraz ignored')

    @warningregistry
    def test_loadTestsFromModule__use_load_tests_deprecated_keyword(self):
        m = types.ModuleType('m')
        klasa MyTestCase(unittest.TestCase):
            def test(self):
                dalej
        m.testcase_1 = MyTestCase

        load_tests_args = []
        def load_tests(loader, tests, pattern):
            self.assertIsInstance(tests, unittest.TestSuite)
            load_tests_args.extend((loader, tests, pattern))
            zwróć tests
        m.load_tests = load_tests
        # The method still works.
        loader = unittest.TestLoader()
        przy warnings.catch_warnings(record=Prawda) jako w:
            warnings.simplefilter('always')
            suite = loader.loadTestsFromModule(m, use_load_tests=Nieprawda)
            self.assertIsInstance(suite, unittest.TestSuite)
            # load_tests was still called because use_load_tests jest deprecated
            # oraz ignored.
            self.assertEqual(load_tests_args, [loader, suite, Nic])
            # We got a warning.
            self.assertIs(w[-1].category, DeprecationWarning)
            self.assertEqual(str(w[-1].message),
                                 'use_load_tests jest deprecated oraz ignored')

    @warningregistry
    def test_loadTestsFromModule__too_many_positional_args(self):
        m = types.ModuleType('m')
        klasa MyTestCase(unittest.TestCase):
            def test(self):
                dalej
        m.testcase_1 = MyTestCase

        load_tests_args = []
        def load_tests(loader, tests, pattern):
            self.assertIsInstance(tests, unittest.TestSuite)
            load_tests_args.extend((loader, tests, pattern))
            zwróć tests
        m.load_tests = load_tests
        loader = unittest.TestLoader()
        przy self.assertRaises(TypeError) jako cm, \
             warnings.catch_warning(record=Prawda) jako w:
            loader.loadTestsFromModule(m, Nieprawda, 'testme.*')
            # We still got the deprecation warning.
            self.assertIs(w[-1].category, DeprecationWarning)
            self.assertEqual(str(w[-1].message),
                                 'use_load_tests jest deprecated oraz ignored')
            # We also got a TypeError dla too many positional arguments.
            self.assertEqual(type(cm.exception), TypeError)
            self.assertEqual(
                str(cm.exception),
                'loadTestsFromModule() takes 1 positional argument but 3 were given')

    @warningregistry
    def test_loadTestsFromModule__use_load_tests_other_bad_keyword(self):
        m = types.ModuleType('m')
        klasa MyTestCase(unittest.TestCase):
            def test(self):
                dalej
        m.testcase_1 = MyTestCase

        load_tests_args = []
        def load_tests(loader, tests, pattern):
            self.assertIsInstance(tests, unittest.TestSuite)
            load_tests_args.extend((loader, tests, pattern))
            zwróć tests
        m.load_tests = load_tests
        loader = unittest.TestLoader()
        przy warnings.catch_warnings():
            warnings.simplefilter('never')
            przy self.assertRaises(TypeError) jako cm:
                loader.loadTestsFromModule(
                    m, use_load_tests=Nieprawda, very_bad=Prawda, worse=Nieprawda)
        self.assertEqual(type(cm.exception), TypeError)
        # The error message names the first bad argument alphabetically,
        # however use_load_tests (which sorts first) jest ignored.
        self.assertEqual(
            str(cm.exception),
            "loadTestsFromModule() got an unexpected keyword argument 'very_bad'")

    def test_loadTestsFromModule__pattern(self):
        m = types.ModuleType('m')
        klasa MyTestCase(unittest.TestCase):
            def test(self):
                dalej
        m.testcase_1 = MyTestCase

        load_tests_args = []
        def load_tests(loader, tests, pattern):
            self.assertIsInstance(tests, unittest.TestSuite)
            load_tests_args.extend((loader, tests, pattern))
            zwróć tests
        m.load_tests = load_tests

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(m, pattern='testme.*')
        self.assertIsInstance(suite, unittest.TestSuite)
        self.assertEqual(load_tests_args, [loader, suite, 'testme.*'])

    def test_loadTestsFromModule__faulty_load_tests(self):
        m = types.ModuleType('m')

        def load_tests(loader, tests, pattern):
            podnieś TypeError('some failure')
        m.load_tests = load_tests

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(m)
        self.assertIsInstance(suite, unittest.TestSuite)
        self.assertEqual(suite.countTestCases(), 1)
        # Errors loading the suite are also captured dla introspection.
        self.assertNotEqual([], loader.errors)
        self.assertEqual(1, len(loader.errors))
        error = loader.errors[0]
        self.assertPrawda(
            'Failed to call load_tests:' w error,
            'missing error string w %r' % error)
        test = list(suite)[0]

        self.assertRaisesRegex(TypeError, "some failure", test.m)

    ################################################################
    ### /Tests dla TestLoader.loadTestsFromModule()

    ### Tests dla TestLoader.loadTestsFromName()
    ################################################################

    # "The specifier name jest a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, albo a callable object which returns a
    # TestCase albo TestSuite instance."
    #
    # Is ValueError podnieśd w response to an empty name?
    def test_loadTestsFromName__empty_name(self):
        loader = unittest.TestLoader()

        spróbuj:
            loader.loadTestsFromName('')
        wyjąwszy ValueError jako e:
            self.assertEqual(str(e), "Empty module name")
        inaczej:
            self.fail("TestLoader.loadTestsFromName failed to podnieś ValueError")

    # "The specifier name jest a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, albo a callable object which returns a
    # TestCase albo TestSuite instance."
    #
    # What happens when the name contains invalid characters?
    def test_loadTestsFromName__malformed_name(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromName('abc () //')
        error, test = self.check_deferred_error(loader, suite)
        expected = "Failed to zaimportuj test module: abc () //"
        expected_regex = "Failed to zaimportuj test module: abc \(\) //"
        self.assertIn(
            expected, error,
            'missing error string w %r' % error)
        self.assertRaisesRegex(
            ImportError, expected_regex, getattr(test, 'abc () //'))

    # "The specifier name jest a ``dotted name'' that may resolve ... to a
    # module"
    #
    # What happens when a module by that name can't be found?
    def test_loadTestsFromName__unknown_module_name(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromName('sdasfasfasdf')
        expected = "No module named 'sdasfasfasdf'"
        error, test = self.check_deferred_error(loader, suite)
        self.assertIn(
            expected, error,
            'missing error string w %r' % error)
        self.assertRaisesRegex(ImportError, expected, test.sdasfasfasdf)

    # "The specifier name jest a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, albo a callable object which returns a
    # TestCase albo TestSuite instance."
    #
    # What happens when the module jest found, but the attribute isn't?
    def test_loadTestsFromName__unknown_attr_name_on_module(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromName('unittest.loader.sdasfasfasdf')
        expected = "module 'unittest.loader' has no attribute 'sdasfasfasdf'"
        error, test = self.check_deferred_error(loader, suite)
        self.assertIn(
            expected, error,
            'missing error string w %r' % error)
        self.assertRaisesRegex(AttributeError, expected, test.sdasfasfasdf)

    # "The specifier name jest a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, albo a callable object which returns a
    # TestCase albo TestSuite instance."
    #
    # What happens when the module jest found, but the attribute isn't?
    def test_loadTestsFromName__unknown_attr_name_on_package(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromName('unittest.sdasfasfasdf')
        expected = "No module named 'unittest.sdasfasfasdf'"
        error, test = self.check_deferred_error(loader, suite)
        self.assertIn(
            expected, error,
            'missing error string w %r' % error)
        self.assertRaisesRegex(ImportError, expected, test.sdasfasfasdf)

    # "The specifier name jest a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, albo a callable object which returns a
    # TestCase albo TestSuite instance."
    #
    # What happens when we provide the module, but the attribute can't be
    # found?
    def test_loadTestsFromName__relative_unknown_name(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromName('sdasfasfasdf', unittest)
        expected = "module 'unittest' has no attribute 'sdasfasfasdf'"
        error, test = self.check_deferred_error(loader, suite)
        self.assertIn(
            expected, error,
            'missing error string w %r' % error)
        self.assertRaisesRegex(AttributeError, expected, test.sdasfasfasdf)

    # "The specifier name jest a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, albo a callable object which returns a
    # TestCase albo TestSuite instance."
    # ...
    # "The method optionally resolves name relative to the given module"
    #
    # Does loadTestsFromName podnieś ValueError when dalejed an empty
    # name relative to a provided module?
    #
    # XXX Should probably podnieś a ValueError instead of an AttributeError
    def test_loadTestsFromName__relative_empty_name(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromName('', unittest)
        error, test = self.check_deferred_error(loader, suite)
        expected = "has no attribute ''"
        self.assertIn(
            expected, error,
            'missing error string w %r' % error)
        self.assertRaisesRegex(AttributeError, expected, getattr(test, ''))

    # "The specifier name jest a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, albo a callable object which returns a
    # TestCase albo TestSuite instance."
    # ...
    # "The method optionally resolves name relative to the given module"
    #
    # What happens when an impossible name jest given, relative to the provided
    # `module`?
    def test_loadTestsFromName__relative_malformed_name(self):
        loader = unittest.TestLoader()

        # XXX Should this podnieś AttributeError albo ValueError?
        suite = loader.loadTestsFromName('abc () //', unittest)
        error, test = self.check_deferred_error(loader, suite)
        expected = "module 'unittest' has no attribute 'abc () //'"
        expected_regex = "module 'unittest' has no attribute 'abc \(\) //'"
        self.assertIn(
            expected, error,
            'missing error string w %r' % error)
        self.assertRaisesRegex(
            AttributeError, expected_regex, getattr(test, 'abc () //'))

    # "The method optionally resolves name relative to the given module"
    #
    # Does loadTestsFromName podnieś TypeError when the `module` argument
    # isn't a module object?
    #
    # XXX Accepts the not-a-module object, ignoring the object's type
    # This should podnieś an exception albo the method name should be changed
    #
    # XXX Some people are relying on this, so keep it dla now
    def test_loadTestsFromName__relative_not_a_module(self):
        klasa MyTestCase(unittest.TestCase):
            def test(self):
                dalej

        klasa NotAModule(object):
            test_2 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName('test_2', NotAModule)

        reference = [MyTestCase('test')]
        self.assertEqual(list(suite), reference)

    # "The specifier name jest a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, albo a callable object which returns a
    # TestCase albo TestSuite instance."
    #
    # Does it podnieś an exception jeżeli the name resolves to an invalid
    # object?
    def test_loadTestsFromName__relative_bad_object(self):
        m = types.ModuleType('m')
        m.testcase_1 = object()

        loader = unittest.TestLoader()
        spróbuj:
            loader.loadTestsFromName('testcase_1', m)
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("Should have podnieśd TypeError")

    # "The specifier name jest a ``dotted name'' that may
    # resolve either to ... a test case class"
    def test_loadTestsFromName__relative_TestCase_subclass(self):
        m = types.ModuleType('m')
        klasa MyTestCase(unittest.TestCase):
            def test(self):
                dalej
        m.testcase_1 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName('testcase_1', m)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [MyTestCase('test')])

    # "The specifier name jest a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, albo a callable object which returns a
    # TestCase albo TestSuite instance."
    def test_loadTestsFromName__relative_TestSuite(self):
        m = types.ModuleType('m')
        klasa MyTestCase(unittest.TestCase):
            def test(self):
                dalej
        m.testsuite = unittest.TestSuite([MyTestCase('test')])

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName('testsuite', m)
        self.assertIsInstance(suite, loader.suiteClass)

        self.assertEqual(list(suite), [MyTestCase('test')])

    # "The specifier name jest a ``dotted name'' that may resolve ... to
    # ... a test method within a test case class"
    def test_loadTestsFromName__relative_testmethod(self):
        m = types.ModuleType('m')
        klasa MyTestCase(unittest.TestCase):
            def test(self):
                dalej
        m.testcase_1 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName('testcase_1.test', m)
        self.assertIsInstance(suite, loader.suiteClass)

        self.assertEqual(list(suite), [MyTestCase('test')])

    # "The specifier name jest a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, albo a callable object which returns a
    # TestCase albo TestSuite instance."
    #
    # Does loadTestsFromName() podnieś the proper exception when trying to
    # resolve "a test method within a test case class" that doesn't exist
    # dla the given name (relative to a provided module)?
    def test_loadTestsFromName__relative_invalid_testmethod(self):
        m = types.ModuleType('m')
        klasa MyTestCase(unittest.TestCase):
            def test(self):
                dalej
        m.testcase_1 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName('testcase_1.testfoo', m)
        expected = "type object 'MyTestCase' has no attribute 'testfoo'"
        error, test = self.check_deferred_error(loader, suite)
        self.assertIn(
            expected, error,
            'missing error string w %r' % error)
        self.assertRaisesRegex(AttributeError, expected, test.testfoo)

    # "The specifier name jest a ``dotted name'' that may resolve ... to
    # ... a callable object which returns a ... TestSuite instance"
    def test_loadTestsFromName__callable__TestSuite(self):
        m = types.ModuleType('m')
        testcase_1 = unittest.FunctionTestCase(lambda: Nic)
        testcase_2 = unittest.FunctionTestCase(lambda: Nic)
        def return_TestSuite():
            zwróć unittest.TestSuite([testcase_1, testcase_2])
        m.return_TestSuite = return_TestSuite

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName('return_TestSuite', m)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [testcase_1, testcase_2])

    # "The specifier name jest a ``dotted name'' that may resolve ... to
    # ... a callable object which returns a TestCase ... instance"
    def test_loadTestsFromName__callable__TestCase_instance(self):
        m = types.ModuleType('m')
        testcase_1 = unittest.FunctionTestCase(lambda: Nic)
        def return_TestCase():
            zwróć testcase_1
        m.return_TestCase = return_TestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName('return_TestCase', m)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [testcase_1])

    # "The specifier name jest a ``dotted name'' that may resolve ... to
    # ... a callable object which returns a TestCase ... instance"
    #*****************************************************************
    #Override the suiteClass attribute to ensure that the suiteClass
    #attribute jest used
    def test_loadTestsFromName__callable__TestCase_instance_ProperSuiteClass(self):
        klasa SubTestSuite(unittest.TestSuite):
            dalej
        m = types.ModuleType('m')
        testcase_1 = unittest.FunctionTestCase(lambda: Nic)
        def return_TestCase():
            zwróć testcase_1
        m.return_TestCase = return_TestCase

        loader = unittest.TestLoader()
        loader.suiteClass = SubTestSuite
        suite = loader.loadTestsFromName('return_TestCase', m)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [testcase_1])

    # "The specifier name jest a ``dotted name'' that may resolve ... to
    # ... a test method within a test case class"
    #*****************************************************************
    #Override the suiteClass attribute to ensure that the suiteClass
    #attribute jest used
    def test_loadTestsFromName__relative_testmethod_ProperSuiteClass(self):
        klasa SubTestSuite(unittest.TestSuite):
            dalej
        m = types.ModuleType('m')
        klasa MyTestCase(unittest.TestCase):
            def test(self):
                dalej
        m.testcase_1 = MyTestCase

        loader = unittest.TestLoader()
        loader.suiteClass=SubTestSuite
        suite = loader.loadTestsFromName('testcase_1.test', m)
        self.assertIsInstance(suite, loader.suiteClass)

        self.assertEqual(list(suite), [MyTestCase('test')])

    # "The specifier name jest a ``dotted name'' that may resolve ... to
    # ... a callable object which returns a TestCase albo TestSuite instance"
    #
    # What happens jeżeli the callable returns something inaczej?
    def test_loadTestsFromName__callable__wrong_type(self):
        m = types.ModuleType('m')
        def return_wrong():
            zwróć 6
        m.return_wrong = return_wrong

        loader = unittest.TestLoader()
        spróbuj:
            suite = loader.loadTestsFromName('return_wrong', m)
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("TestLoader.loadTestsFromName failed to podnieś TypeError")

    # "The specifier can refer to modules oraz packages which have nie been
    # imported; they will be imported jako a side-effect"
    def test_loadTestsFromName__module_not_loaded(self):
        # We're going to try to load this module jako a side-effect, so it
        # better nie be loaded before we try.
        #
        module_name = 'unittest.test.dummy'
        sys.modules.pop(module_name, Nic)

        loader = unittest.TestLoader()
        spróbuj:
            suite = loader.loadTestsFromName(module_name)

            self.assertIsInstance(suite, loader.suiteClass)
            self.assertEqual(list(suite), [])

            # module should now be loaded, thanks to loadTestsFromName()
            self.assertIn(module_name, sys.modules)
        w_końcu:
            jeżeli module_name w sys.modules:
                usuń sys.modules[module_name]

    ################################################################
    ### Tests dla TestLoader.loadTestsFromName()

    ### Tests dla TestLoader.loadTestsFromNames()
    ################################################################

    def check_deferred_error(self, loader, suite):
        """Helper function dla checking that errors w loading are reported.

        :param loader: A loader przy some errors.
        :param suite: A suite that should have a late bound error.
        :return: The first error message z the loader oraz the test object
            z the suite.
        """
        self.assertIsInstance(suite, unittest.TestSuite)
        self.assertEqual(suite.countTestCases(), 1)
        # Errors loading the suite are also captured dla introspection.
        self.assertNotEqual([], loader.errors)
        self.assertEqual(1, len(loader.errors))
        error = loader.errors[0]
        test = list(suite)[0]
        zwróć error, test

    # "Similar to loadTestsFromName(), but takes a sequence of names rather
    # than a single name."
    #
    # What happens jeżeli that sequence of names jest empty?
    def test_loadTestsFromNames__empty_name_list(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromNames([])
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [])

    # "Similar to loadTestsFromName(), but takes a sequence of names rather
    # than a single name."
    # ...
    # "The method optionally resolves name relative to the given module"
    #
    # What happens jeżeli that sequence of names jest empty?
    #
    # XXX Should this podnieś a ValueError albo just zwróć an empty TestSuite?
    def test_loadTestsFromNames__relative_empty_name_list(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromNames([], unittest)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [])

    # "The specifier name jest a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, albo a callable object which returns a
    # TestCase albo TestSuite instance."
    #
    # Is ValueError podnieśd w response to an empty name?
    def test_loadTestsFromNames__empty_name(self):
        loader = unittest.TestLoader()

        spróbuj:
            loader.loadTestsFromNames([''])
        wyjąwszy ValueError jako e:
            self.assertEqual(str(e), "Empty module name")
        inaczej:
            self.fail("TestLoader.loadTestsFromNames failed to podnieś ValueError")

    # "The specifier name jest a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, albo a callable object which returns a
    # TestCase albo TestSuite instance."
    #
    # What happens when presented przy an impossible module name?
    def test_loadTestsFromNames__malformed_name(self):
        loader = unittest.TestLoader()

        # XXX Should this podnieś ValueError albo ImportError?
        suite = loader.loadTestsFromNames(['abc () //'])
        error, test = self.check_deferred_error(loader, list(suite)[0])
        expected = "Failed to zaimportuj test module: abc () //"
        expected_regex = "Failed to zaimportuj test module: abc \(\) //"
        self.assertIn(
            expected,  error,
            'missing error string w %r' % error)
        self.assertRaisesRegex(
            ImportError, expected_regex, getattr(test, 'abc () //'))

    # "The specifier name jest a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, albo a callable object which returns a
    # TestCase albo TestSuite instance."
    #
    # What happens when no module can be found dla the given name?
    def test_loadTestsFromNames__unknown_module_name(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromNames(['sdasfasfasdf'])
        error, test = self.check_deferred_error(loader, list(suite)[0])
        expected = "Failed to zaimportuj test module: sdasfasfasdf"
        self.assertIn(
            expected, error,
            'missing error string w %r' % error)
        self.assertRaisesRegex(ImportError, expected, test.sdasfasfasdf)

    # "The specifier name jest a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, albo a callable object which returns a
    # TestCase albo TestSuite instance."
    #
    # What happens when the module can be found, but nie the attribute?
    def test_loadTestsFromNames__unknown_attr_name(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromNames(
            ['unittest.loader.sdasfasfasdf', 'unittest.test.dummy'])
        error, test = self.check_deferred_error(loader, list(suite)[0])
        expected = "module 'unittest.loader' has no attribute 'sdasfasfasdf'"
        self.assertIn(
            expected, error,
            'missing error string w %r' % error)
        self.assertRaisesRegex(AttributeError, expected, test.sdasfasfasdf)

    # "The specifier name jest a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, albo a callable object which returns a
    # TestCase albo TestSuite instance."
    # ...
    # "The method optionally resolves name relative to the given module"
    #
    # What happens when given an unknown attribute on a specified `module`
    # argument?
    def test_loadTestsFromNames__unknown_name_relative_1(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromNames(['sdasfasfasdf'], unittest)
        error, test = self.check_deferred_error(loader, list(suite)[0])
        expected = "module 'unittest' has no attribute 'sdasfasfasdf'"
        self.assertIn(
            expected, error,
            'missing error string w %r' % error)
        self.assertRaisesRegex(AttributeError, expected, test.sdasfasfasdf)

    # "The specifier name jest a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, albo a callable object which returns a
    # TestCase albo TestSuite instance."
    # ...
    # "The method optionally resolves name relative to the given module"
    #
    # Do unknown attributes (relative to a provided module) still podnieś an
    # exception even w the presence of valid attribute names?
    def test_loadTestsFromNames__unknown_name_relative_2(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromNames(['TestCase', 'sdasfasfasdf'], unittest)
        error, test = self.check_deferred_error(loader, list(suite)[1])
        expected = "module 'unittest' has no attribute 'sdasfasfasdf'"
        self.assertIn(
            expected, error,
            'missing error string w %r' % error)
        self.assertRaisesRegex(AttributeError, expected, test.sdasfasfasdf)

    # "The specifier name jest a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, albo a callable object which returns a
    # TestCase albo TestSuite instance."
    # ...
    # "The method optionally resolves name relative to the given module"
    #
    # What happens when faced przy the empty string?
    #
    # XXX This currently podnieśs AttributeError, though ValueError jest probably
    # more appropriate
    def test_loadTestsFromNames__relative_empty_name(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromNames([''], unittest)
        error, test = self.check_deferred_error(loader, list(suite)[0])
        expected = "has no attribute ''"
        self.assertIn(
            expected, error,
            'missing error string w %r' % error)
        self.assertRaisesRegex(AttributeError, expected, getattr(test, ''))

    # "The specifier name jest a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, albo a callable object which returns a
    # TestCase albo TestSuite instance."
    # ...
    # "The method optionally resolves name relative to the given module"
    #
    # What happens when presented przy an impossible attribute name?
    def test_loadTestsFromNames__relative_malformed_name(self):
        loader = unittest.TestLoader()

        # XXX Should this podnieś AttributeError albo ValueError?
        suite = loader.loadTestsFromNames(['abc () //'], unittest)
        error, test = self.check_deferred_error(loader, list(suite)[0])
        expected = "module 'unittest' has no attribute 'abc () //'"
        expected_regex = "module 'unittest' has no attribute 'abc \(\) //'"
        self.assertIn(
            expected, error,
            'missing error string w %r' % error)
        self.assertRaisesRegex(
            AttributeError, expected_regex, getattr(test, 'abc () //'))

    # "The method optionally resolves name relative to the given module"
    #
    # Does loadTestsFromNames() make sure the provided `module` jest w fact
    # a module?
    #
    # XXX This validation jest currently nie done. This flexibility should
    # either be documented albo a TypeError should be podnieśd.
    def test_loadTestsFromNames__relative_not_a_module(self):
        klasa MyTestCase(unittest.TestCase):
            def test(self):
                dalej

        klasa NotAModule(object):
            test_2 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromNames(['test_2'], NotAModule)

        reference = [unittest.TestSuite([MyTestCase('test')])]
        self.assertEqual(list(suite), reference)

    # "The specifier name jest a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, albo a callable object which returns a
    # TestCase albo TestSuite instance."
    #
    # Does it podnieś an exception jeżeli the name resolves to an invalid
    # object?
    def test_loadTestsFromNames__relative_bad_object(self):
        m = types.ModuleType('m')
        m.testcase_1 = object()

        loader = unittest.TestLoader()
        spróbuj:
            loader.loadTestsFromNames(['testcase_1'], m)
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("Should have podnieśd TypeError")

    # "The specifier name jest a ``dotted name'' that may resolve ... to
    # ... a test case class"
    def test_loadTestsFromNames__relative_TestCase_subclass(self):
        m = types.ModuleType('m')
        klasa MyTestCase(unittest.TestCase):
            def test(self):
                dalej
        m.testcase_1 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromNames(['testcase_1'], m)
        self.assertIsInstance(suite, loader.suiteClass)

        expected = loader.suiteClass([MyTestCase('test')])
        self.assertEqual(list(suite), [expected])

    # "The specifier name jest a ``dotted name'' that may resolve ... to
    # ... a TestSuite instance"
    def test_loadTestsFromNames__relative_TestSuite(self):
        m = types.ModuleType('m')
        klasa MyTestCase(unittest.TestCase):
            def test(self):
                dalej
        m.testsuite = unittest.TestSuite([MyTestCase('test')])

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromNames(['testsuite'], m)
        self.assertIsInstance(suite, loader.suiteClass)

        self.assertEqual(list(suite), [m.testsuite])

    # "The specifier name jest a ``dotted name'' that may resolve ... to ... a
    # test method within a test case class"
    def test_loadTestsFromNames__relative_testmethod(self):
        m = types.ModuleType('m')
        klasa MyTestCase(unittest.TestCase):
            def test(self):
                dalej
        m.testcase_1 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromNames(['testcase_1.test'], m)
        self.assertIsInstance(suite, loader.suiteClass)

        ref_suite = unittest.TestSuite([MyTestCase('test')])
        self.assertEqual(list(suite), [ref_suite])

    # #14971: Make sure the dotted name resolution works even jeżeli the actual
    # function doesn't have the same name jako jest used to find it.
    def test_loadTestsFromName__function_with_different_name_than_method(self):
        # lambdas have the name '<lambda>'.
        m = types.ModuleType('m')
        klasa MyTestCase(unittest.TestCase):
            test = lambda: 1
        m.testcase_1 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromNames(['testcase_1.test'], m)
        self.assertIsInstance(suite, loader.suiteClass)

        ref_suite = unittest.TestSuite([MyTestCase('test')])
        self.assertEqual(list(suite), [ref_suite])

    # "The specifier name jest a ``dotted name'' that may resolve ... to ... a
    # test method within a test case class"
    #
    # Does the method gracefully handle names that initially look like they
    # resolve to "a test method within a test case class" but don't?
    def test_loadTestsFromNames__relative_invalid_testmethod(self):
        m = types.ModuleType('m')
        klasa MyTestCase(unittest.TestCase):
            def test(self):
                dalej
        m.testcase_1 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromNames(['testcase_1.testfoo'], m)
        error, test = self.check_deferred_error(loader, list(suite)[0])
        expected = "type object 'MyTestCase' has no attribute 'testfoo'"
        self.assertIn(
            expected, error,
            'missing error string w %r' % error)
        self.assertRaisesRegex(AttributeError, expected, test.testfoo)

    # "The specifier name jest a ``dotted name'' that may resolve ... to
    # ... a callable object which returns a ... TestSuite instance"
    def test_loadTestsFromNames__callable__TestSuite(self):
        m = types.ModuleType('m')
        testcase_1 = unittest.FunctionTestCase(lambda: Nic)
        testcase_2 = unittest.FunctionTestCase(lambda: Nic)
        def return_TestSuite():
            zwróć unittest.TestSuite([testcase_1, testcase_2])
        m.return_TestSuite = return_TestSuite

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromNames(['return_TestSuite'], m)
        self.assertIsInstance(suite, loader.suiteClass)

        expected = unittest.TestSuite([testcase_1, testcase_2])
        self.assertEqual(list(suite), [expected])

    # "The specifier name jest a ``dotted name'' that may resolve ... to
    # ... a callable object which returns a TestCase ... instance"
    def test_loadTestsFromNames__callable__TestCase_instance(self):
        m = types.ModuleType('m')
        testcase_1 = unittest.FunctionTestCase(lambda: Nic)
        def return_TestCase():
            zwróć testcase_1
        m.return_TestCase = return_TestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromNames(['return_TestCase'], m)
        self.assertIsInstance(suite, loader.suiteClass)

        ref_suite = unittest.TestSuite([testcase_1])
        self.assertEqual(list(suite), [ref_suite])

    # "The specifier name jest a ``dotted name'' that may resolve ... to
    # ... a callable object which returns a TestCase albo TestSuite instance"
    #
    # Are staticmethods handled correctly?
    def test_loadTestsFromNames__callable__call_staticmethod(self):
        m = types.ModuleType('m')
        klasa Test1(unittest.TestCase):
            def test(self):
                dalej

        testcase_1 = Test1('test')
        klasa Foo(unittest.TestCase):
            @staticmethod
            def foo():
                zwróć testcase_1
        m.Foo = Foo

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromNames(['Foo.foo'], m)
        self.assertIsInstance(suite, loader.suiteClass)

        ref_suite = unittest.TestSuite([testcase_1])
        self.assertEqual(list(suite), [ref_suite])

    # "The specifier name jest a ``dotted name'' that may resolve ... to
    # ... a callable object which returns a TestCase albo TestSuite instance"
    #
    # What happens when the callable returns something inaczej?
    def test_loadTestsFromNames__callable__wrong_type(self):
        m = types.ModuleType('m')
        def return_wrong():
            zwróć 6
        m.return_wrong = return_wrong

        loader = unittest.TestLoader()
        spróbuj:
            suite = loader.loadTestsFromNames(['return_wrong'], m)
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("TestLoader.loadTestsFromNames failed to podnieś TypeError")

    # "The specifier can refer to modules oraz packages which have nie been
    # imported; they will be imported jako a side-effect"
    def test_loadTestsFromNames__module_not_loaded(self):
        # We're going to try to load this module jako a side-effect, so it
        # better nie be loaded before we try.
        #
        module_name = 'unittest.test.dummy'
        sys.modules.pop(module_name, Nic)

        loader = unittest.TestLoader()
        spróbuj:
            suite = loader.loadTestsFromNames([module_name])

            self.assertIsInstance(suite, loader.suiteClass)
            self.assertEqual(list(suite), [unittest.TestSuite()])

            # module should now be loaded, thanks to loadTestsFromName()
            self.assertIn(module_name, sys.modules)
        w_końcu:
            jeżeli module_name w sys.modules:
                usuń sys.modules[module_name]

    ################################################################
    ### /Tests dla TestLoader.loadTestsFromNames()

    ### Tests dla TestLoader.getTestCaseNames()
    ################################################################

    # "Return a sorted sequence of method names found within testCaseClass"
    #
    # Test.foobar jest defined to make sure getTestCaseNames() respects
    # loader.testMethodPrefix
    def test_getTestCaseNames(self):
        klasa Test(unittest.TestCase):
            def test_1(self): dalej
            def test_2(self): dalej
            def foobar(self): dalej

        loader = unittest.TestLoader()

        self.assertEqual(loader.getTestCaseNames(Test), ['test_1', 'test_2'])

    # "Return a sorted sequence of method names found within testCaseClass"
    #
    # Does getTestCaseNames() behave appropriately jeżeli no tests are found?
    def test_getTestCaseNames__no_tests(self):
        klasa Test(unittest.TestCase):
            def foobar(self): dalej

        loader = unittest.TestLoader()

        self.assertEqual(loader.getTestCaseNames(Test), [])

    # "Return a sorted sequence of method names found within testCaseClass"
    #
    # Are not-TestCases handled gracefully?
    #
    # XXX This should podnieś a TypeError, nie zwróć a list
    #
    # XXX It's too late w the 2.5 release cycle to fix this, but it should
    # probably be revisited dla 2.6
    def test_getTestCaseNames__not_a_TestCase(self):
        klasa BadCase(int):
            def test_foo(self):
                dalej

        loader = unittest.TestLoader()
        names = loader.getTestCaseNames(BadCase)

        self.assertEqual(names, ['test_foo'])

    # "Return a sorted sequence of method names found within testCaseClass"
    #
    # Make sure inherited names are handled.
    #
    # TestP.foobar jest defined to make sure getTestCaseNames() respects
    # loader.testMethodPrefix
    def test_getTestCaseNames__inheritance(self):
        klasa TestP(unittest.TestCase):
            def test_1(self): dalej
            def test_2(self): dalej
            def foobar(self): dalej

        klasa TestC(TestP):
            def test_1(self): dalej
            def test_3(self): dalej

        loader = unittest.TestLoader()

        names = ['test_1', 'test_2', 'test_3']
        self.assertEqual(loader.getTestCaseNames(TestC), names)

    ################################################################
    ### /Tests dla TestLoader.getTestCaseNames()

    ### Tests dla TestLoader.testMethodPrefix
    ################################################################

    # "String giving the prefix of method names which will be interpreted as
    # test methods"
    #
    # Implicit w the documentation jest that testMethodPrefix jest respected by
    # all loadTestsFrom* methods.
    def test_testMethodPrefix__loadTestsFromTestCase(self):
        klasa Foo(unittest.TestCase):
            def test_1(self): dalej
            def test_2(self): dalej
            def foo_bar(self): dalej

        tests_1 = unittest.TestSuite([Foo('foo_bar')])
        tests_2 = unittest.TestSuite([Foo('test_1'), Foo('test_2')])

        loader = unittest.TestLoader()
        loader.testMethodPrefix = 'foo'
        self.assertEqual(loader.loadTestsFromTestCase(Foo), tests_1)

        loader.testMethodPrefix = 'test'
        self.assertEqual(loader.loadTestsFromTestCase(Foo), tests_2)

    # "String giving the prefix of method names which will be interpreted as
    # test methods"
    #
    # Implicit w the documentation jest that testMethodPrefix jest respected by
    # all loadTestsFrom* methods.
    def test_testMethodPrefix__loadTestsFromModule(self):
        m = types.ModuleType('m')
        klasa Foo(unittest.TestCase):
            def test_1(self): dalej
            def test_2(self): dalej
            def foo_bar(self): dalej
        m.Foo = Foo

        tests_1 = [unittest.TestSuite([Foo('foo_bar')])]
        tests_2 = [unittest.TestSuite([Foo('test_1'), Foo('test_2')])]

        loader = unittest.TestLoader()
        loader.testMethodPrefix = 'foo'
        self.assertEqual(list(loader.loadTestsFromModule(m)), tests_1)

        loader.testMethodPrefix = 'test'
        self.assertEqual(list(loader.loadTestsFromModule(m)), tests_2)

    # "String giving the prefix of method names which will be interpreted as
    # test methods"
    #
    # Implicit w the documentation jest that testMethodPrefix jest respected by
    # all loadTestsFrom* methods.
    def test_testMethodPrefix__loadTestsFromName(self):
        m = types.ModuleType('m')
        klasa Foo(unittest.TestCase):
            def test_1(self): dalej
            def test_2(self): dalej
            def foo_bar(self): dalej
        m.Foo = Foo

        tests_1 = unittest.TestSuite([Foo('foo_bar')])
        tests_2 = unittest.TestSuite([Foo('test_1'), Foo('test_2')])

        loader = unittest.TestLoader()
        loader.testMethodPrefix = 'foo'
        self.assertEqual(loader.loadTestsFromName('Foo', m), tests_1)

        loader.testMethodPrefix = 'test'
        self.assertEqual(loader.loadTestsFromName('Foo', m), tests_2)

    # "String giving the prefix of method names which will be interpreted as
    # test methods"
    #
    # Implicit w the documentation jest that testMethodPrefix jest respected by
    # all loadTestsFrom* methods.
    def test_testMethodPrefix__loadTestsFromNames(self):
        m = types.ModuleType('m')
        klasa Foo(unittest.TestCase):
            def test_1(self): dalej
            def test_2(self): dalej
            def foo_bar(self): dalej
        m.Foo = Foo

        tests_1 = unittest.TestSuite([unittest.TestSuite([Foo('foo_bar')])])
        tests_2 = unittest.TestSuite([Foo('test_1'), Foo('test_2')])
        tests_2 = unittest.TestSuite([tests_2])

        loader = unittest.TestLoader()
        loader.testMethodPrefix = 'foo'
        self.assertEqual(loader.loadTestsFromNames(['Foo'], m), tests_1)

        loader.testMethodPrefix = 'test'
        self.assertEqual(loader.loadTestsFromNames(['Foo'], m), tests_2)

    # "The default value jest 'test'"
    def test_testMethodPrefix__default_value(self):
        loader = unittest.TestLoader()
        self.assertEqual(loader.testMethodPrefix, 'test')

    ################################################################
    ### /Tests dla TestLoader.testMethodPrefix

    ### Tests dla TestLoader.sortTestMethodsUsing
    ################################################################

    # "Function to be used to compare method names when sorting them w
    # getTestCaseNames() oraz all the loadTestsFromX() methods"
    def test_sortTestMethodsUsing__loadTestsFromTestCase(self):
        def reversed_cmp(x, y):
            zwróć -((x > y) - (x < y))

        klasa Foo(unittest.TestCase):
            def test_1(self): dalej
            def test_2(self): dalej

        loader = unittest.TestLoader()
        loader.sortTestMethodsUsing = reversed_cmp

        tests = loader.suiteClass([Foo('test_2'), Foo('test_1')])
        self.assertEqual(loader.loadTestsFromTestCase(Foo), tests)

    # "Function to be used to compare method names when sorting them w
    # getTestCaseNames() oraz all the loadTestsFromX() methods"
    def test_sortTestMethodsUsing__loadTestsFromModule(self):
        def reversed_cmp(x, y):
            zwróć -((x > y) - (x < y))

        m = types.ModuleType('m')
        klasa Foo(unittest.TestCase):
            def test_1(self): dalej
            def test_2(self): dalej
        m.Foo = Foo

        loader = unittest.TestLoader()
        loader.sortTestMethodsUsing = reversed_cmp

        tests = [loader.suiteClass([Foo('test_2'), Foo('test_1')])]
        self.assertEqual(list(loader.loadTestsFromModule(m)), tests)

    # "Function to be used to compare method names when sorting them w
    # getTestCaseNames() oraz all the loadTestsFromX() methods"
    def test_sortTestMethodsUsing__loadTestsFromName(self):
        def reversed_cmp(x, y):
            zwróć -((x > y) - (x < y))

        m = types.ModuleType('m')
        klasa Foo(unittest.TestCase):
            def test_1(self): dalej
            def test_2(self): dalej
        m.Foo = Foo

        loader = unittest.TestLoader()
        loader.sortTestMethodsUsing = reversed_cmp

        tests = loader.suiteClass([Foo('test_2'), Foo('test_1')])
        self.assertEqual(loader.loadTestsFromName('Foo', m), tests)

    # "Function to be used to compare method names when sorting them w
    # getTestCaseNames() oraz all the loadTestsFromX() methods"
    def test_sortTestMethodsUsing__loadTestsFromNames(self):
        def reversed_cmp(x, y):
            zwróć -((x > y) - (x < y))

        m = types.ModuleType('m')
        klasa Foo(unittest.TestCase):
            def test_1(self): dalej
            def test_2(self): dalej
        m.Foo = Foo

        loader = unittest.TestLoader()
        loader.sortTestMethodsUsing = reversed_cmp

        tests = [loader.suiteClass([Foo('test_2'), Foo('test_1')])]
        self.assertEqual(list(loader.loadTestsFromNames(['Foo'], m)), tests)

    # "Function to be used to compare method names when sorting them w
    # getTestCaseNames()"
    #
    # Does it actually affect getTestCaseNames()?
    def test_sortTestMethodsUsing__getTestCaseNames(self):
        def reversed_cmp(x, y):
            zwróć -((x > y) - (x < y))

        klasa Foo(unittest.TestCase):
            def test_1(self): dalej
            def test_2(self): dalej

        loader = unittest.TestLoader()
        loader.sortTestMethodsUsing = reversed_cmp

        test_names = ['test_2', 'test_1']
        self.assertEqual(loader.getTestCaseNames(Foo), test_names)

    # "The default value jest the built-in cmp() function"
    # Since cmp jest now defunct, we simply verify that the results
    # occur w the same order jako they would przy the default sort.
    def test_sortTestMethodsUsing__default_value(self):
        loader = unittest.TestLoader()

        klasa Foo(unittest.TestCase):
            def test_2(self): dalej
            def test_3(self): dalej
            def test_1(self): dalej

        test_names = ['test_2', 'test_3', 'test_1']
        self.assertEqual(loader.getTestCaseNames(Foo), sorted(test_names))


    # "it can be set to Nic to disable the sort."
    #
    # XXX How jest this different z reassigning cmp? Are the tests returned
    # w a random order albo something? This behaviour should die
    def test_sortTestMethodsUsing__Nic(self):
        klasa Foo(unittest.TestCase):
            def test_1(self): dalej
            def test_2(self): dalej

        loader = unittest.TestLoader()
        loader.sortTestMethodsUsing = Nic

        test_names = ['test_2', 'test_1']
        self.assertEqual(set(loader.getTestCaseNames(Foo)), set(test_names))

    ################################################################
    ### /Tests dla TestLoader.sortTestMethodsUsing

    ### Tests dla TestLoader.suiteClass
    ################################################################

    # "Callable object that constructs a test suite z a list of tests."
    def test_suiteClass__loadTestsFromTestCase(self):
        klasa Foo(unittest.TestCase):
            def test_1(self): dalej
            def test_2(self): dalej
            def foo_bar(self): dalej

        tests = [Foo('test_1'), Foo('test_2')]

        loader = unittest.TestLoader()
        loader.suiteClass = list
        self.assertEqual(loader.loadTestsFromTestCase(Foo), tests)

    # It jest implicit w the documentation dla TestLoader.suiteClass that
    # all TestLoader.loadTestsFrom* methods respect it. Let's make sure
    def test_suiteClass__loadTestsFromModule(self):
        m = types.ModuleType('m')
        klasa Foo(unittest.TestCase):
            def test_1(self): dalej
            def test_2(self): dalej
            def foo_bar(self): dalej
        m.Foo = Foo

        tests = [[Foo('test_1'), Foo('test_2')]]

        loader = unittest.TestLoader()
        loader.suiteClass = list
        self.assertEqual(loader.loadTestsFromModule(m), tests)

    # It jest implicit w the documentation dla TestLoader.suiteClass that
    # all TestLoader.loadTestsFrom* methods respect it. Let's make sure
    def test_suiteClass__loadTestsFromName(self):
        m = types.ModuleType('m')
        klasa Foo(unittest.TestCase):
            def test_1(self): dalej
            def test_2(self): dalej
            def foo_bar(self): dalej
        m.Foo = Foo

        tests = [Foo('test_1'), Foo('test_2')]

        loader = unittest.TestLoader()
        loader.suiteClass = list
        self.assertEqual(loader.loadTestsFromName('Foo', m), tests)

    # It jest implicit w the documentation dla TestLoader.suiteClass that
    # all TestLoader.loadTestsFrom* methods respect it. Let's make sure
    def test_suiteClass__loadTestsFromNames(self):
        m = types.ModuleType('m')
        klasa Foo(unittest.TestCase):
            def test_1(self): dalej
            def test_2(self): dalej
            def foo_bar(self): dalej
        m.Foo = Foo

        tests = [[Foo('test_1'), Foo('test_2')]]

        loader = unittest.TestLoader()
        loader.suiteClass = list
        self.assertEqual(loader.loadTestsFromNames(['Foo'], m), tests)

    # "The default value jest the TestSuite class"
    def test_suiteClass__default_value(self):
        loader = unittest.TestLoader()
        self.assertIs(loader.suiteClass, unittest.TestSuite)


jeżeli __name__ == "__main__":
    unittest.main()
