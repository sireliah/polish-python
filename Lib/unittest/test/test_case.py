zaimportuj contextlib
zaimportuj difflib
zaimportuj pprint
zaimportuj pickle
zaimportuj re
zaimportuj sys
zaimportuj logging
zaimportuj warnings
zaimportuj weakref
zaimportuj inspect

z copy zaimportuj deepcopy
z test zaimportuj support

zaimportuj unittest

z unittest.test.support zaimportuj (
    TestEquality, TestHashing, LoggingResult, LegacyLoggingResult,
    ResultWithNoStartTestRunStopTestRun
)
z test.support zaimportuj captured_stderr


log_foo = logging.getLogger('foo')
log_foobar = logging.getLogger('foo.bar')
log_quux = logging.getLogger('quux')


klasa Test(object):
    "Keep these TestCase classes out of the main namespace"

    klasa Foo(unittest.TestCase):
        def runTest(self): dalej
        def test1(self): dalej

    klasa Bar(Foo):
        def test2(self): dalej

    klasa LoggingTestCase(unittest.TestCase):
        """A test case which logs its calls."""

        def __init__(self, events):
            super(Test.LoggingTestCase, self).__init__('test')
            self.events = events

        def setUp(self):
            self.events.append('setUp')

        def test(self):
            self.events.append('test')

        def tearDown(self):
            self.events.append('tearDown')


klasa Test_TestCase(unittest.TestCase, TestEquality, TestHashing):

    ### Set up attributes used by inherited tests
    ################################################################

    # Used by TestHashing.test_hash oraz TestEquality.test_eq
    eq_pairs = [(Test.Foo('test1'), Test.Foo('test1'))]

    # Used by TestEquality.test_ne
    ne_pairs = [(Test.Foo('test1'), Test.Foo('runTest')),
                (Test.Foo('test1'), Test.Bar('test1')),
                (Test.Foo('test1'), Test.Bar('test2'))]

    ################################################################
    ### /Set up attributes used by inherited tests


    # "class TestCase([methodName])"
    # ...
    # "Each instance of TestCase will run a single test method: the
    # method named methodName."
    # ...
    # "methodName defaults to "runTest"."
    #
    # Make sure it really jest optional, oraz that it defaults to the proper
    # thing.
    def test_init__no_test_name(self):
        klasa Test(unittest.TestCase):
            def runTest(self): podnieś MyException()
            def test(self): dalej

        self.assertEqual(Test().id()[-13:], '.Test.runTest')

        # test that TestCase can be instantiated przy no args
        # primarily dla use at the interactive interpreter
        test = unittest.TestCase()
        test.assertEqual(3, 3)
        przy test.assertRaises(test.failureException):
            test.assertEqual(3, 2)

        przy self.assertRaises(AttributeError):
            test.run()

    # "class TestCase([methodName])"
    # ...
    # "Each instance of TestCase will run a single test method: the
    # method named methodName."
    def test_init__test_name__valid(self):
        klasa Test(unittest.TestCase):
            def runTest(self): podnieś MyException()
            def test(self): dalej

        self.assertEqual(Test('test').id()[-10:], '.Test.test')

    # "class TestCase([methodName])"
    # ...
    # "Each instance of TestCase will run a single test method: the
    # method named methodName."
    def test_init__test_name__invalid(self):
        klasa Test(unittest.TestCase):
            def runTest(self): podnieś MyException()
            def test(self): dalej

        spróbuj:
            Test('testfoo')
        wyjąwszy ValueError:
            dalej
        inaczej:
            self.fail("Failed to podnieś ValueError")

    # "Return the number of tests represented by the this test object. For
    # TestCase instances, this will always be 1"
    def test_countTestCases(self):
        klasa Foo(unittest.TestCase):
            def test(self): dalej

        self.assertEqual(Foo('test').countTestCases(), 1)

    # "Return the default type of test result object to be used to run this
    # test. For TestCase instances, this will always be
    # unittest.TestResult;  subclasses of TestCase should
    # override this jako necessary."
    def test_defaultTestResult(self):
        klasa Foo(unittest.TestCase):
            def runTest(self):
                dalej

        result = Foo().defaultTestResult()
        self.assertEqual(type(result), unittest.TestResult)

    # "When a setUp() method jest defined, the test runner will run that method
    # prior to each test. Likewise, jeżeli a tearDown() method jest defined, the
    # test runner will invoke that method after each test. In the example,
    # setUp() was used to create a fresh sequence dla each test."
    #
    # Make sure the proper call order jest maintained, even jeżeli setUp() podnieśs
    # an exception.
    def test_run_call_order__error_in_setUp(self):
        events = []
        result = LoggingResult(events)

        klasa Foo(Test.LoggingTestCase):
            def setUp(self):
                super(Foo, self).setUp()
                podnieś RuntimeError('raised by Foo.setUp')

        Foo(events).run(result)
        expected = ['startTest', 'setUp', 'addError', 'stopTest']
        self.assertEqual(events, expected)

    # "With a temporary result stopTestRun jest called when setUp errors.
    def test_run_call_order__error_in_setUp_default_result(self):
        events = []

        klasa Foo(Test.LoggingTestCase):
            def defaultTestResult(self):
                zwróć LoggingResult(self.events)

            def setUp(self):
                super(Foo, self).setUp()
                podnieś RuntimeError('raised by Foo.setUp')

        Foo(events).run()
        expected = ['startTestRun', 'startTest', 'setUp', 'addError',
                    'stopTest', 'stopTestRun']
        self.assertEqual(events, expected)

    # "When a setUp() method jest defined, the test runner will run that method
    # prior to each test. Likewise, jeżeli a tearDown() method jest defined, the
    # test runner will invoke that method after each test. In the example,
    # setUp() was used to create a fresh sequence dla each test."
    #
    # Make sure the proper call order jest maintained, even jeżeli the test podnieśs
    # an error (as opposed to a failure).
    def test_run_call_order__error_in_test(self):
        events = []
        result = LoggingResult(events)

        klasa Foo(Test.LoggingTestCase):
            def test(self):
                super(Foo, self).test()
                podnieś RuntimeError('raised by Foo.test')

        expected = ['startTest', 'setUp', 'test', 'tearDown',
                    'addError', 'stopTest']
        Foo(events).run(result)
        self.assertEqual(events, expected)

    # "With a default result, an error w the test still results w stopTestRun
    # being called."
    def test_run_call_order__error_in_test_default_result(self):
        events = []

        klasa Foo(Test.LoggingTestCase):
            def defaultTestResult(self):
                zwróć LoggingResult(self.events)

            def test(self):
                super(Foo, self).test()
                podnieś RuntimeError('raised by Foo.test')

        expected = ['startTestRun', 'startTest', 'setUp', 'test',
                    'tearDown', 'addError', 'stopTest', 'stopTestRun']
        Foo(events).run()
        self.assertEqual(events, expected)

    # "When a setUp() method jest defined, the test runner will run that method
    # prior to each test. Likewise, jeżeli a tearDown() method jest defined, the
    # test runner will invoke that method after each test. In the example,
    # setUp() was used to create a fresh sequence dla each test."
    #
    # Make sure the proper call order jest maintained, even jeżeli the test signals
    # a failure (as opposed to an error).
    def test_run_call_order__failure_in_test(self):
        events = []
        result = LoggingResult(events)

        klasa Foo(Test.LoggingTestCase):
            def test(self):
                super(Foo, self).test()
                self.fail('raised by Foo.test')

        expected = ['startTest', 'setUp', 'test', 'tearDown',
                    'addFailure', 'stopTest']
        Foo(events).run(result)
        self.assertEqual(events, expected)

    # "When a test fails przy a default result stopTestRun jest still called."
    def test_run_call_order__failure_in_test_default_result(self):

        klasa Foo(Test.LoggingTestCase):
            def defaultTestResult(self):
                zwróć LoggingResult(self.events)
            def test(self):
                super(Foo, self).test()
                self.fail('raised by Foo.test')

        expected = ['startTestRun', 'startTest', 'setUp', 'test',
                    'tearDown', 'addFailure', 'stopTest', 'stopTestRun']
        events = []
        Foo(events).run()
        self.assertEqual(events, expected)

    # "When a setUp() method jest defined, the test runner will run that method
    # prior to each test. Likewise, jeżeli a tearDown() method jest defined, the
    # test runner will invoke that method after each test. In the example,
    # setUp() was used to create a fresh sequence dla each test."
    #
    # Make sure the proper call order jest maintained, even jeżeli tearDown() podnieśs
    # an exception.
    def test_run_call_order__error_in_tearDown(self):
        events = []
        result = LoggingResult(events)

        klasa Foo(Test.LoggingTestCase):
            def tearDown(self):
                super(Foo, self).tearDown()
                podnieś RuntimeError('raised by Foo.tearDown')

        Foo(events).run(result)
        expected = ['startTest', 'setUp', 'test', 'tearDown', 'addError',
                    'stopTest']
        self.assertEqual(events, expected)

    # "When tearDown errors przy a default result stopTestRun jest still called."
    def test_run_call_order__error_in_tearDown_default_result(self):

        klasa Foo(Test.LoggingTestCase):
            def defaultTestResult(self):
                zwróć LoggingResult(self.events)
            def tearDown(self):
                super(Foo, self).tearDown()
                podnieś RuntimeError('raised by Foo.tearDown')

        events = []
        Foo(events).run()
        expected = ['startTestRun', 'startTest', 'setUp', 'test', 'tearDown',
                    'addError', 'stopTest', 'stopTestRun']
        self.assertEqual(events, expected)

    # "TestCase.run() still works when the defaultTestResult jest a TestResult
    # that does nie support startTestRun oraz stopTestRun.
    def test_run_call_order_default_result(self):

        klasa Foo(unittest.TestCase):
            def defaultTestResult(self):
                zwróć ResultWithNoStartTestRunStopTestRun()
            def test(self):
                dalej

        Foo('test').run()

    def _check_call_order__subtests(self, result, events, expected_events):
        klasa Foo(Test.LoggingTestCase):
            def test(self):
                super(Foo, self).test()
                dla i w [1, 2, 3]:
                    przy self.subTest(i=i):
                        jeżeli i == 1:
                            self.fail('failure')
                        dla j w [2, 3]:
                            przy self.subTest(j=j):
                                jeżeli i * j == 6:
                                    podnieś RuntimeError('raised by Foo.test')
                1 / 0

        # Order jest the following:
        # i=1 => subtest failure
        # i=2, j=2 => subtest success
        # i=2, j=3 => subtest error
        # i=3, j=2 => subtest error
        # i=3, j=3 => subtest success
        # toplevel => error
        Foo(events).run(result)
        self.assertEqual(events, expected_events)

    def test_run_call_order__subtests(self):
        events = []
        result = LoggingResult(events)
        expected = ['startTest', 'setUp', 'test', 'tearDown',
                    'addSubTestFailure', 'addSubTestSuccess',
                    'addSubTestFailure', 'addSubTestFailure',
                    'addSubTestSuccess', 'addError', 'stopTest']
        self._check_call_order__subtests(result, events, expected)

    def test_run_call_order__subtests_legacy(self):
        # With a legacy result object (without a addSubTest method),
        # text execution stops after the first subtest failure.
        events = []
        result = LegacyLoggingResult(events)
        expected = ['startTest', 'setUp', 'test', 'tearDown',
                    'addFailure', 'stopTest']
        self._check_call_order__subtests(result, events, expected)

    def _check_call_order__subtests_success(self, result, events, expected_events):
        klasa Foo(Test.LoggingTestCase):
            def test(self):
                super(Foo, self).test()
                dla i w [1, 2]:
                    przy self.subTest(i=i):
                        dla j w [2, 3]:
                            przy self.subTest(j=j):
                                dalej

        Foo(events).run(result)
        self.assertEqual(events, expected_events)

    def test_run_call_order__subtests_success(self):
        events = []
        result = LoggingResult(events)
        # The 6 subtest successes are individually recorded, w addition
        # to the whole test success.
        expected = (['startTest', 'setUp', 'test', 'tearDown']
                    + 6 * ['addSubTestSuccess']
                    + ['addSuccess', 'stopTest'])
        self._check_call_order__subtests_success(result, events, expected)

    def test_run_call_order__subtests_success_legacy(self):
        # With a legacy result, only the whole test success jest recorded.
        events = []
        result = LegacyLoggingResult(events)
        expected = ['startTest', 'setUp', 'test', 'tearDown',
                    'addSuccess', 'stopTest']
        self._check_call_order__subtests_success(result, events, expected)

    def test_run_call_order__subtests_failfast(self):
        events = []
        result = LoggingResult(events)
        result.failfast = Prawda

        klasa Foo(Test.LoggingTestCase):
            def test(self):
                super(Foo, self).test()
                przy self.subTest(i=1):
                    self.fail('failure')
                przy self.subTest(i=2):
                    self.fail('failure')
                self.fail('failure')

        expected = ['startTest', 'setUp', 'test', 'tearDown',
                    'addSubTestFailure', 'stopTest']
        Foo(events).run(result)
        self.assertEqual(events, expected)

    def test_subtests_failfast(self):
        # Ensure proper test flow przy subtests oraz failfast (issue #22894)
        events = []

        klasa Foo(unittest.TestCase):
            def test_a(self):
                przy self.subTest():
                    events.append('a1')
                events.append('a2')

            def test_b(self):
                przy self.subTest():
                    events.append('b1')
                przy self.subTest():
                    self.fail('failure')
                events.append('b2')

            def test_c(self):
                events.append('c')

        result = unittest.TestResult()
        result.failfast = Prawda
        suite = unittest.makeSuite(Foo)
        suite.run(result)

        expected = ['a1', 'a2', 'b1']
        self.assertEqual(events, expected)

    # "This klasa attribute gives the exception podnieśd by the test() method.
    # If a test framework needs to use a specialized exception, possibly to
    # carry additional information, it must subclass this exception w
    # order to ``play fair'' przy the framework.  The initial value of this
    # attribute jest AssertionError"
    def test_failureException__default(self):
        klasa Foo(unittest.TestCase):
            def test(self):
                dalej

        self.assertIs(Foo('test').failureException, AssertionError)

    # "This klasa attribute gives the exception podnieśd by the test() method.
    # If a test framework needs to use a specialized exception, possibly to
    # carry additional information, it must subclass this exception w
    # order to ``play fair'' przy the framework."
    #
    # Make sure TestCase.run() respects the designated failureException
    def test_failureException__subclassing__explicit_raise(self):
        events = []
        result = LoggingResult(events)

        klasa Foo(unittest.TestCase):
            def test(self):
                podnieś RuntimeError()

            failureException = RuntimeError

        self.assertIs(Foo('test').failureException, RuntimeError)


        Foo('test').run(result)
        expected = ['startTest', 'addFailure', 'stopTest']
        self.assertEqual(events, expected)

    # "This klasa attribute gives the exception podnieśd by the test() method.
    # If a test framework needs to use a specialized exception, possibly to
    # carry additional information, it must subclass this exception w
    # order to ``play fair'' przy the framework."
    #
    # Make sure TestCase.run() respects the designated failureException
    def test_failureException__subclassing__implicit_raise(self):
        events = []
        result = LoggingResult(events)

        klasa Foo(unittest.TestCase):
            def test(self):
                self.fail("foo")

            failureException = RuntimeError

        self.assertIs(Foo('test').failureException, RuntimeError)


        Foo('test').run(result)
        expected = ['startTest', 'addFailure', 'stopTest']
        self.assertEqual(events, expected)

    # "The default implementation does nothing."
    def test_setUp(self):
        klasa Foo(unittest.TestCase):
            def runTest(self):
                dalej

        # ... oraz nothing should happen
        Foo().setUp()

    # "The default implementation does nothing."
    def test_tearDown(self):
        klasa Foo(unittest.TestCase):
            def runTest(self):
                dalej

        # ... oraz nothing should happen
        Foo().tearDown()

    # "Return a string identifying the specific test case."
    #
    # Because of the vague nature of the docs, I'm nie going to lock this
    # test down too much. Really all that can be asserted jest that the id()
    # will be a string (either 8-byte albo unicode -- again, because the docs
    # just say "string")
    def test_id(self):
        klasa Foo(unittest.TestCase):
            def runTest(self):
                dalej

        self.assertIsInstance(Foo().id(), str)


    # "If result jest omitted albo Nic, a temporary result object jest created,
    # used, oraz jest made available to the caller. As TestCase owns the
    # temporary result startTestRun oraz stopTestRun are called.

    def test_run__uses_defaultTestResult(self):
        events = []
        defaultResult = LoggingResult(events)

        klasa Foo(unittest.TestCase):
            def test(self):
                events.append('test')

            def defaultTestResult(self):
                zwróć defaultResult

        # Make run() find a result object on its own
        result = Foo('test').run()

        self.assertIs(result, defaultResult)
        expected = ['startTestRun', 'startTest', 'test', 'addSuccess',
            'stopTest', 'stopTestRun']
        self.assertEqual(events, expected)


    # "The result object jest returned to run's caller"
    def test_run__returns_given_result(self):

        klasa Foo(unittest.TestCase):
            def test(self):
                dalej

        result = unittest.TestResult()

        retval = Foo('test').run(result)
        self.assertIs(retval, result)


    # "The same effect [as method run] may be had by simply calling the
    # TestCase instance."
    def test_call__invoking_an_instance_delegates_to_run(self):
        resultIn = unittest.TestResult()
        resultOut = unittest.TestResult()

        klasa Foo(unittest.TestCase):
            def test(self):
                dalej

            def run(self, result):
                self.assertIs(result, resultIn)
                zwróć resultOut

        retval = Foo('test')(resultIn)

        self.assertIs(retval, resultOut)


    def testShortDescriptionWithoutDocstring(self):
        self.assertIsNic(self.shortDescription())

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted przy -O2 oraz above")
    def testShortDescriptionWithOneLineDocstring(self):
        """Tests shortDescription() dla a method przy a docstring."""
        self.assertEqual(
                self.shortDescription(),
                'Tests shortDescription() dla a method przy a docstring.')

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted przy -O2 oraz above")
    def testShortDescriptionWithMultiLineDocstring(self):
        """Tests shortDescription() dla a method przy a longer docstring.

        This method ensures that only the first line of a docstring jest
        returned used w the short description, no matter how long the
        whole thing is.
        """
        self.assertEqual(
                self.shortDescription(),
                 'Tests shortDescription() dla a method przy a longer '
                 'docstring.')

    def testAddTypeEqualityFunc(self):
        klasa SadSnake(object):
            """Dummy klasa dla test_addTypeEqualityFunc."""
        s1, s2 = SadSnake(), SadSnake()
        self.assertNieprawda(s1 == s2)
        def AllSnakesCreatedEqual(a, b, msg=Nic):
            zwróć type(a) == type(b) == SadSnake
        self.addTypeEqualityFunc(SadSnake, AllSnakesCreatedEqual)
        self.assertEqual(s1, s2)
        # No this doesn't clean up oraz remove the SadSnake equality func
        # z this TestCase instance but since its a local nothing inaczej
        # will ever notice that.

    def testAssertIs(self):
        thing = object()
        self.assertIs(thing, thing)
        self.assertRaises(self.failureException, self.assertIs, thing, object())

    def testAssertIsNot(self):
        thing = object()
        self.assertIsNot(thing, object())
        self.assertRaises(self.failureException, self.assertIsNot, thing, thing)

    def testAssertIsInstance(self):
        thing = []
        self.assertIsInstance(thing, list)
        self.assertRaises(self.failureException, self.assertIsInstance,
                          thing, dict)

    def testAssertNotIsInstance(self):
        thing = []
        self.assertNotIsInstance(thing, dict)
        self.assertRaises(self.failureException, self.assertNotIsInstance,
                          thing, list)

    def testAssertIn(self):
        animals = {'monkey': 'banana', 'cow': 'grass', 'seal': 'fish'}

        self.assertIn('a', 'abc')
        self.assertIn(2, [1, 2, 3])
        self.assertIn('monkey', animals)

        self.assertNotIn('d', 'abc')
        self.assertNotIn(0, [1, 2, 3])
        self.assertNotIn('otter', animals)

        self.assertRaises(self.failureException, self.assertIn, 'x', 'abc')
        self.assertRaises(self.failureException, self.assertIn, 4, [1, 2, 3])
        self.assertRaises(self.failureException, self.assertIn, 'elephant',
                          animals)

        self.assertRaises(self.failureException, self.assertNotIn, 'c', 'abc')
        self.assertRaises(self.failureException, self.assertNotIn, 1, [1, 2, 3])
        self.assertRaises(self.failureException, self.assertNotIn, 'cow',
                          animals)

    def testAssertDictContainsSubset(self):
        przy warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)

            self.assertDictContainsSubset({}, {})
            self.assertDictContainsSubset({}, {'a': 1})
            self.assertDictContainsSubset({'a': 1}, {'a': 1})
            self.assertDictContainsSubset({'a': 1}, {'a': 1, 'b': 2})
            self.assertDictContainsSubset({'a': 1, 'b': 2}, {'a': 1, 'b': 2})

            przy self.assertRaises(self.failureException):
                self.assertDictContainsSubset({1: "one"}, {})

            przy self.assertRaises(self.failureException):
                self.assertDictContainsSubset({'a': 2}, {'a': 1})

            przy self.assertRaises(self.failureException):
                self.assertDictContainsSubset({'c': 1}, {'a': 1})

            przy self.assertRaises(self.failureException):
                self.assertDictContainsSubset({'a': 1, 'c': 1}, {'a': 1})

            przy self.assertRaises(self.failureException):
                self.assertDictContainsSubset({'a': 1, 'c': 1}, {'a': 1})

            one = ''.join(chr(i) dla i w range(255))
            # this used to cause a UnicodeDecodeError constructing the failure msg
            przy self.assertRaises(self.failureException):
                self.assertDictContainsSubset({'foo': one}, {'foo': '\uFFFD'})

    def testAssertEqual(self):
        equal_pairs = [
                ((), ()),
                ({}, {}),
                ([], []),
                (set(), set()),
                (frozenset(), frozenset())]
        dla a, b w equal_pairs:
            # This mess of try excepts jest to test the assertEqual behavior
            # itself.
            spróbuj:
                self.assertEqual(a, b)
            wyjąwszy self.failureException:
                self.fail('assertEqual(%r, %r) failed' % (a, b))
            spróbuj:
                self.assertEqual(a, b, msg='foo')
            wyjąwszy self.failureException:
                self.fail('assertEqual(%r, %r) przy msg= failed' % (a, b))
            spróbuj:
                self.assertEqual(a, b, 'foo')
            wyjąwszy self.failureException:
                self.fail('assertEqual(%r, %r) przy third parameter failed' %
                          (a, b))

        unequal_pairs = [
               ((), []),
               ({}, set()),
               (set([4,1]), frozenset([4,2])),
               (frozenset([4,5]), set([2,3])),
               (set([3,4]), set([5,4]))]
        dla a, b w unequal_pairs:
            self.assertRaises(self.failureException, self.assertEqual, a, b)
            self.assertRaises(self.failureException, self.assertEqual, a, b,
                              'foo')
            self.assertRaises(self.failureException, self.assertEqual, a, b,
                              msg='foo')

    def testEquality(self):
        self.assertListEqual([], [])
        self.assertTupleEqual((), ())
        self.assertSequenceEqual([], ())

        a = [0, 'a', []]
        b = []
        self.assertRaises(unittest.TestCase.failureException,
                          self.assertListEqual, a, b)
        self.assertRaises(unittest.TestCase.failureException,
                          self.assertListEqual, tuple(a), tuple(b))
        self.assertRaises(unittest.TestCase.failureException,
                          self.assertSequenceEqual, a, tuple(b))

        b.extend(a)
        self.assertListEqual(a, b)
        self.assertTupleEqual(tuple(a), tuple(b))
        self.assertSequenceEqual(a, tuple(b))
        self.assertSequenceEqual(tuple(a), b)

        self.assertRaises(self.failureException, self.assertListEqual,
                          a, tuple(b))
        self.assertRaises(self.failureException, self.assertTupleEqual,
                          tuple(a), b)
        self.assertRaises(self.failureException, self.assertListEqual, Nic, b)
        self.assertRaises(self.failureException, self.assertTupleEqual, Nic,
                          tuple(b))
        self.assertRaises(self.failureException, self.assertSequenceEqual,
                          Nic, tuple(b))
        self.assertRaises(self.failureException, self.assertListEqual, 1, 1)
        self.assertRaises(self.failureException, self.assertTupleEqual, 1, 1)
        self.assertRaises(self.failureException, self.assertSequenceEqual,
                          1, 1)

        self.assertDictEqual({}, {})

        c = { 'x': 1 }
        d = {}
        self.assertRaises(unittest.TestCase.failureException,
                          self.assertDictEqual, c, d)

        d.update(c)
        self.assertDictEqual(c, d)

        d['x'] = 0
        self.assertRaises(unittest.TestCase.failureException,
                          self.assertDictEqual, c, d, 'These are unequal')

        self.assertRaises(self.failureException, self.assertDictEqual, Nic, d)
        self.assertRaises(self.failureException, self.assertDictEqual, [], d)
        self.assertRaises(self.failureException, self.assertDictEqual, 1, 1)

    def testAssertSequenceEqualMaxDiff(self):
        self.assertEqual(self.maxDiff, 80*8)
        seq1 = 'a' + 'x' * 80**2
        seq2 = 'b' + 'x' * 80**2
        diff = '\n'.join(difflib.ndiff(pprint.pformat(seq1).splitlines(),
                                       pprint.pformat(seq2).splitlines()))
        # the +1 jest the leading \n added by assertSequenceEqual
        omitted = unittest.case.DIFF_OMITTED % (len(diff) + 1,)

        self.maxDiff = len(diff)//2
        spróbuj:

            self.assertSequenceEqual(seq1, seq2)
        wyjąwszy self.failureException jako e:
            msg = e.args[0]
        inaczej:
            self.fail('assertSequenceEqual did nie fail.')
        self.assertLess(len(msg), len(diff))
        self.assertIn(omitted, msg)

        self.maxDiff = len(diff) * 2
        spróbuj:
            self.assertSequenceEqual(seq1, seq2)
        wyjąwszy self.failureException jako e:
            msg = e.args[0]
        inaczej:
            self.fail('assertSequenceEqual did nie fail.')
        self.assertGreater(len(msg), len(diff))
        self.assertNotIn(omitted, msg)

        self.maxDiff = Nic
        spróbuj:
            self.assertSequenceEqual(seq1, seq2)
        wyjąwszy self.failureException jako e:
            msg = e.args[0]
        inaczej:
            self.fail('assertSequenceEqual did nie fail.')
        self.assertGreater(len(msg), len(diff))
        self.assertNotIn(omitted, msg)

    def testTruncateMessage(self):
        self.maxDiff = 1
        message = self._truncateMessage('foo', 'bar')
        omitted = unittest.case.DIFF_OMITTED % len('bar')
        self.assertEqual(message, 'foo' + omitted)

        self.maxDiff = Nic
        message = self._truncateMessage('foo', 'bar')
        self.assertEqual(message, 'foobar')

        self.maxDiff = 4
        message = self._truncateMessage('foo', 'bar')
        self.assertEqual(message, 'foobar')

    def testAssertDictEqualTruncates(self):
        test = unittest.TestCase('assertEqual')
        def truncate(msg, diff):
            zwróć 'foo'
        test._truncateMessage = truncate
        spróbuj:
            test.assertDictEqual({}, {1: 0})
        wyjąwszy self.failureException jako e:
            self.assertEqual(str(e), 'foo')
        inaczej:
            self.fail('assertDictEqual did nie fail')

    def testAssertMultiLineEqualTruncates(self):
        test = unittest.TestCase('assertEqual')
        def truncate(msg, diff):
            zwróć 'foo'
        test._truncateMessage = truncate
        spróbuj:
            test.assertMultiLineEqual('foo', 'bar')
        wyjąwszy self.failureException jako e:
            self.assertEqual(str(e), 'foo')
        inaczej:
            self.fail('assertMultiLineEqual did nie fail')

    def testAssertEqual_diffThreshold(self):
        # check threshold value
        self.assertEqual(self._diffThreshold, 2**16)
        # disable madDiff to get diff markers
        self.maxDiff = Nic

        # set a lower threshold value oraz add a cleanup to restore it
        old_threshold = self._diffThreshold
        self._diffThreshold = 2**5
        self.addCleanup(lambda: setattr(self, '_diffThreshold', old_threshold))

        # under the threshold: diff marker (^) w error message
        s = 'x' * (2**4)
        przy self.assertRaises(self.failureException) jako cm:
            self.assertEqual(s + 'a', s + 'b')
        self.assertIn('^', str(cm.exception))
        self.assertEqual(s + 'a', s + 'a')

        # over the threshold: diff nie used oraz marker (^) nie w error message
        s = 'x' * (2**6)
        # jeżeli the path that uses difflib jest taken, _truncateMessage will be
        # called -- replace it przy explodingTruncation to verify that this
        # doesn't happen
        def explodingTruncation(message, diff):
            podnieś SystemError('this should nie be podnieśd')
        old_truncate = self._truncateMessage
        self._truncateMessage = explodingTruncation
        self.addCleanup(lambda: setattr(self, '_truncateMessage', old_truncate))

        s1, s2 = s + 'a', s + 'b'
        przy self.assertRaises(self.failureException) jako cm:
            self.assertEqual(s1, s2)
        self.assertNotIn('^', str(cm.exception))
        self.assertEqual(str(cm.exception), '%r != %r' % (s1, s2))
        self.assertEqual(s + 'a', s + 'a')

    def testAssertEqual_shorten(self):
        # set a lower threshold value oraz add a cleanup to restore it
        old_threshold = self._diffThreshold
        self._diffThreshold = 0
        self.addCleanup(lambda: setattr(self, '_diffThreshold', old_threshold))

        s = 'x' * 100
        s1, s2 = s + 'a', s + 'b'
        przy self.assertRaises(self.failureException) jako cm:
            self.assertEqual(s1, s2)
        c = 'xxxx[35 chars]' + 'x' * 61
        self.assertEqual(str(cm.exception), "'%sa' != '%sb'" % (c, c))
        self.assertEqual(s + 'a', s + 'a')

        p = 'y' * 50
        s1, s2 = s + 'a' + p, s + 'b' + p
        przy self.assertRaises(self.failureException) jako cm:
            self.assertEqual(s1, s2)
        c = 'xxxx[85 chars]xxxxxxxxxxx'
        self.assertEqual(str(cm.exception), "'%sa%s' != '%sb%s'" % (c, p, c, p))

        p = 'y' * 100
        s1, s2 = s + 'a' + p, s + 'b' + p
        przy self.assertRaises(self.failureException) jako cm:
            self.assertEqual(s1, s2)
        c = 'xxxx[91 chars]xxxxx'
        d = 'y' * 40 + '[56 chars]yyyy'
        self.assertEqual(str(cm.exception), "'%sa%s' != '%sb%s'" % (c, d, c, d))

    def testAssertCountEqual(self):
        a = object()
        self.assertCountEqual([1, 2, 3], [3, 2, 1])
        self.assertCountEqual(['foo', 'bar', 'baz'], ['bar', 'baz', 'foo'])
        self.assertCountEqual([a, a, 2, 2, 3], (a, 2, 3, a, 2))
        self.assertCountEqual([1, "2", "a", "a"], ["a", "2", Prawda, "a"])
        self.assertRaises(self.failureException, self.assertCountEqual,
                          [1, 2] + [3] * 100, [1] * 100 + [2, 3])
        self.assertRaises(self.failureException, self.assertCountEqual,
                          [1, "2", "a", "a"], ["a", "2", Prawda, 1])
        self.assertRaises(self.failureException, self.assertCountEqual,
                          [10], [10, 11])
        self.assertRaises(self.failureException, self.assertCountEqual,
                          [10, 11], [10])
        self.assertRaises(self.failureException, self.assertCountEqual,
                          [10, 11, 10], [10, 11])

        # Test that sequences of unhashable objects can be tested dla sameness:
        self.assertCountEqual([[1, 2], [3, 4], 0], [Nieprawda, [3, 4], [1, 2]])
        # Test that iterator of unhashable objects can be tested dla sameness:
        self.assertCountEqual(iter([1, 2, [], 3, 4]),
                              iter([1, 2, [], 3, 4]))

        # hashable types, but nie orderable
        self.assertRaises(self.failureException, self.assertCountEqual,
                          [], [divmod, 'x', 1, 5j, 2j, frozenset()])
        # comparing dicts
        self.assertCountEqual([{'a': 1}, {'b': 2}], [{'b': 2}, {'a': 1}])
        # comparing heterogenous non-hashable sequences
        self.assertCountEqual([1, 'x', divmod, []], [divmod, [], 'x', 1])
        self.assertRaises(self.failureException, self.assertCountEqual,
                          [], [divmod, [], 'x', 1, 5j, 2j, set()])
        self.assertRaises(self.failureException, self.assertCountEqual,
                          [[1]], [[2]])

        # Same elements, but nie same sequence length
        self.assertRaises(self.failureException, self.assertCountEqual,
                          [1, 1, 2], [2, 1])
        self.assertRaises(self.failureException, self.assertCountEqual,
                          [1, 1, "2", "a", "a"], ["2", "2", Prawda, "a"])
        self.assertRaises(self.failureException, self.assertCountEqual,
                          [1, {'b': 2}, Nic, Prawda], [{'b': 2}, Prawda, Nic])

        # Same elements which don't reliably compare, w
        # different order, see issue 10242
        a = [{2,4}, {1,2}]
        b = a[::-1]
        self.assertCountEqual(a, b)

        # test utility functions supporting assertCountEqual()

        diffs = set(unittest.util._count_diff_all_purpose('aaabccd', 'abbbcce'))
        expected = {(3,1,'a'), (1,3,'b'), (1,0,'d'), (0,1,'e')}
        self.assertEqual(diffs, expected)

        diffs = unittest.util._count_diff_all_purpose([[]], [])
        self.assertEqual(diffs, [(1, 0, [])])

        diffs = set(unittest.util._count_diff_hashable('aaabccd', 'abbbcce'))
        expected = {(3,1,'a'), (1,3,'b'), (1,0,'d'), (0,1,'e')}
        self.assertEqual(diffs, expected)

    def testAssertSetEqual(self):
        set1 = set()
        set2 = set()
        self.assertSetEqual(set1, set2)

        self.assertRaises(self.failureException, self.assertSetEqual, Nic, set2)
        self.assertRaises(self.failureException, self.assertSetEqual, [], set2)
        self.assertRaises(self.failureException, self.assertSetEqual, set1, Nic)
        self.assertRaises(self.failureException, self.assertSetEqual, set1, [])

        set1 = set(['a'])
        set2 = set()
        self.assertRaises(self.failureException, self.assertSetEqual, set1, set2)

        set1 = set(['a'])
        set2 = set(['a'])
        self.assertSetEqual(set1, set2)

        set1 = set(['a'])
        set2 = set(['a', 'b'])
        self.assertRaises(self.failureException, self.assertSetEqual, set1, set2)

        set1 = set(['a'])
        set2 = frozenset(['a', 'b'])
        self.assertRaises(self.failureException, self.assertSetEqual, set1, set2)

        set1 = set(['a', 'b'])
        set2 = frozenset(['a', 'b'])
        self.assertSetEqual(set1, set2)

        set1 = set()
        set2 = "foo"
        self.assertRaises(self.failureException, self.assertSetEqual, set1, set2)
        self.assertRaises(self.failureException, self.assertSetEqual, set2, set1)

        # make sure any string formatting jest tuple-safe
        set1 = set([(0, 1), (2, 3)])
        set2 = set([(4, 5)])
        self.assertRaises(self.failureException, self.assertSetEqual, set1, set2)

    def testInequality(self):
        # Try ints
        self.assertGreater(2, 1)
        self.assertGreaterEqual(2, 1)
        self.assertGreaterEqual(1, 1)
        self.assertLess(1, 2)
        self.assertLessEqual(1, 2)
        self.assertLessEqual(1, 1)
        self.assertRaises(self.failureException, self.assertGreater, 1, 2)
        self.assertRaises(self.failureException, self.assertGreater, 1, 1)
        self.assertRaises(self.failureException, self.assertGreaterEqual, 1, 2)
        self.assertRaises(self.failureException, self.assertLess, 2, 1)
        self.assertRaises(self.failureException, self.assertLess, 1, 1)
        self.assertRaises(self.failureException, self.assertLessEqual, 2, 1)

        # Try Floats
        self.assertGreater(1.1, 1.0)
        self.assertGreaterEqual(1.1, 1.0)
        self.assertGreaterEqual(1.0, 1.0)
        self.assertLess(1.0, 1.1)
        self.assertLessEqual(1.0, 1.1)
        self.assertLessEqual(1.0, 1.0)
        self.assertRaises(self.failureException, self.assertGreater, 1.0, 1.1)
        self.assertRaises(self.failureException, self.assertGreater, 1.0, 1.0)
        self.assertRaises(self.failureException, self.assertGreaterEqual, 1.0, 1.1)
        self.assertRaises(self.failureException, self.assertLess, 1.1, 1.0)
        self.assertRaises(self.failureException, self.assertLess, 1.0, 1.0)
        self.assertRaises(self.failureException, self.assertLessEqual, 1.1, 1.0)

        # Try Strings
        self.assertGreater('bug', 'ant')
        self.assertGreaterEqual('bug', 'ant')
        self.assertGreaterEqual('ant', 'ant')
        self.assertLess('ant', 'bug')
        self.assertLessEqual('ant', 'bug')
        self.assertLessEqual('ant', 'ant')
        self.assertRaises(self.failureException, self.assertGreater, 'ant', 'bug')
        self.assertRaises(self.failureException, self.assertGreater, 'ant', 'ant')
        self.assertRaises(self.failureException, self.assertGreaterEqual, 'ant', 'bug')
        self.assertRaises(self.failureException, self.assertLess, 'bug', 'ant')
        self.assertRaises(self.failureException, self.assertLess, 'ant', 'ant')
        self.assertRaises(self.failureException, self.assertLessEqual, 'bug', 'ant')

        # Try bytes
        self.assertGreater(b'bug', b'ant')
        self.assertGreaterEqual(b'bug', b'ant')
        self.assertGreaterEqual(b'ant', b'ant')
        self.assertLess(b'ant', b'bug')
        self.assertLessEqual(b'ant', b'bug')
        self.assertLessEqual(b'ant', b'ant')
        self.assertRaises(self.failureException, self.assertGreater, b'ant', b'bug')
        self.assertRaises(self.failureException, self.assertGreater, b'ant', b'ant')
        self.assertRaises(self.failureException, self.assertGreaterEqual, b'ant',
                          b'bug')
        self.assertRaises(self.failureException, self.assertLess, b'bug', b'ant')
        self.assertRaises(self.failureException, self.assertLess, b'ant', b'ant')
        self.assertRaises(self.failureException, self.assertLessEqual, b'bug', b'ant')

    def testAssertMultiLineEqual(self):
        sample_text = """\
http://www.python.org/doc/2.3/lib/module-unittest.html
test case
    A test case jest the smallest unit of testing. [...]
"""
        revised_sample_text = """\
http://www.python.org/doc/2.4.1/lib/module-unittest.html
test case
    A test case jest the smallest unit of testing. [...] You may provide your
    own implementation that does nie subclass z TestCase, of course.
"""
        sample_text_error = """\
- http://www.python.org/doc/2.3/lib/module-unittest.html
?                             ^
+ http://www.python.org/doc/2.4.1/lib/module-unittest.html
?                             ^^^
  test case
-     A test case jest the smallest unit of testing. [...]
+     A test case jest the smallest unit of testing. [...] You may provide your
?                                                       +++++++++++++++++++++
+     own implementation that does nie subclass z TestCase, of course.
"""
        self.maxDiff = Nic
        spróbuj:
            self.assertMultiLineEqual(sample_text, revised_sample_text)
        wyjąwszy self.failureException jako e:
            # need to remove the first line of the error message
            error = str(e).split('\n', 1)[1]
            self.assertEqual(sample_text_error, error)

    def testAssertEqualSingleLine(self):
        sample_text = "laden swallows fly slowly"
        revised_sample_text = "unladen swallows fly quickly"
        sample_text_error = """\
- laden swallows fly slowly
?                    ^^^^
+ unladen swallows fly quickly
? ++                   ^^^^^
"""
        spróbuj:
            self.assertEqual(sample_text, revised_sample_text)
        wyjąwszy self.failureException jako e:
            # need to remove the first line of the error message
            error = str(e).split('\n', 1)[1]
            self.assertEqual(sample_text_error, error)

    def testAssertIsNic(self):
        self.assertIsNic(Nic)
        self.assertRaises(self.failureException, self.assertIsNic, Nieprawda)
        self.assertIsNotNic('DjZoPloGears on Rails')
        self.assertRaises(self.failureException, self.assertIsNotNic, Nic)

    def testAssertRegex(self):
        self.assertRegex('asdfabasdf', r'ab+')
        self.assertRaises(self.failureException, self.assertRegex,
                          'saaas', r'aaaa')

    def testAssertRaisesCallable(self):
        klasa ExceptionMock(Exception):
            dalej
        def Stub():
            podnieś ExceptionMock('We expect')
        self.assertRaises(ExceptionMock, Stub)
        # A tuple of exception classes jest accepted
        self.assertRaises((ValueError, ExceptionMock), Stub)
        # *args oraz **kwargs also work
        self.assertRaises(ValueError, int, '19', base=8)
        # Failure when no exception jest podnieśd
        przy self.assertRaises(self.failureException):
            self.assertRaises(ExceptionMock, lambda: 0)
        # Failure when the function jest Nic
        przy self.assertWarns(DeprecationWarning):
            self.assertRaises(ExceptionMock, Nic)
        # Failure when another exception jest podnieśd
        przy self.assertRaises(ExceptionMock):
            self.assertRaises(ValueError, Stub)

    def testAssertRaisesContext(self):
        klasa ExceptionMock(Exception):
            dalej
        def Stub():
            podnieś ExceptionMock('We expect')
        przy self.assertRaises(ExceptionMock):
            Stub()
        # A tuple of exception classes jest accepted
        przy self.assertRaises((ValueError, ExceptionMock)) jako cm:
            Stub()
        # The context manager exposes caught exception
        self.assertIsInstance(cm.exception, ExceptionMock)
        self.assertEqual(cm.exception.args[0], 'We expect')
        # *args oraz **kwargs also work
        przy self.assertRaises(ValueError):
            int('19', base=8)
        # Failure when no exception jest podnieśd
        przy self.assertRaises(self.failureException):
            przy self.assertRaises(ExceptionMock):
                dalej
        # Custom message
        przy self.assertRaisesRegex(self.failureException, 'foobar'):
            przy self.assertRaises(ExceptionMock, msg='foobar'):
                dalej
        # Invalid keyword argument
        przy self.assertWarnsRegex(DeprecationWarning, 'foobar'), \
             self.assertRaises(AssertionError):
            przy self.assertRaises(ExceptionMock, foobar=42):
                dalej
        # Failure when another exception jest podnieśd
        przy self.assertRaises(ExceptionMock):
            self.assertRaises(ValueError, Stub)

    def testAssertRaisesNoExceptionType(self):
        przy self.assertRaises(TypeError):
            self.assertRaises()
        przy self.assertRaises(TypeError):
            self.assertRaises(1)
        przy self.assertRaises(TypeError):
            self.assertRaises(object)
        przy self.assertRaises(TypeError):
            self.assertRaises((ValueError, 1))
        przy self.assertRaises(TypeError):
            self.assertRaises((ValueError, object))

    def testAssertRaisesRegex(self):
        klasa ExceptionMock(Exception):
            dalej

        def Stub():
            podnieś ExceptionMock('We expect')

        self.assertRaisesRegex(ExceptionMock, re.compile('expect$'), Stub)
        self.assertRaisesRegex(ExceptionMock, 'expect$', Stub)
        przy self.assertWarns(DeprecationWarning):
            self.assertRaisesRegex(ExceptionMock, 'expect$', Nic)

    def testAssertNotRaisesRegex(self):
        self.assertRaisesRegex(
                self.failureException, '^Exception nie podnieśd by <lambda>$',
                self.assertRaisesRegex, Exception, re.compile('x'),
                lambda: Nic)
        self.assertRaisesRegex(
                self.failureException, '^Exception nie podnieśd by <lambda>$',
                self.assertRaisesRegex, Exception, 'x',
                lambda: Nic)
        # Custom message
        przy self.assertRaisesRegex(self.failureException, 'foobar'):
            przy self.assertRaisesRegex(Exception, 'expect', msg='foobar'):
                dalej
        # Invalid keyword argument
        przy self.assertWarnsRegex(DeprecationWarning, 'foobar'), \
             self.assertRaises(AssertionError):
            przy self.assertRaisesRegex(Exception, 'expect', foobar=42):
                dalej

    def testAssertRaisesRegexInvalidRegex(self):
        # Issue 20145.
        klasa MyExc(Exception):
            dalej
        self.assertRaises(TypeError, self.assertRaisesRegex, MyExc, lambda: Prawda)

    def testAssertWarnsRegexInvalidRegex(self):
        # Issue 20145.
        klasa MyWarn(Warning):
            dalej
        self.assertRaises(TypeError, self.assertWarnsRegex, MyWarn, lambda: Prawda)

    def testAssertRaisesRegexMismatch(self):
        def Stub():
            podnieś Exception('Unexpected')

        self.assertRaisesRegex(
                self.failureException,
                r'"\^Expected\$" does nie match "Unexpected"',
                self.assertRaisesRegex, Exception, '^Expected$',
                Stub)
        self.assertRaisesRegex(
                self.failureException,
                r'"\^Expected\$" does nie match "Unexpected"',
                self.assertRaisesRegex, Exception,
                re.compile('^Expected$'), Stub)

    def testAssertRaisesExcValue(self):
        klasa ExceptionMock(Exception):
            dalej

        def Stub(foo):
            podnieś ExceptionMock(foo)
        v = "particular value"

        ctx = self.assertRaises(ExceptionMock)
        przy ctx:
            Stub(v)
        e = ctx.exception
        self.assertIsInstance(e, ExceptionMock)
        self.assertEqual(e.args[0], v)

    def testAssertRaisesRegexNoExceptionType(self):
        przy self.assertRaises(TypeError):
            self.assertRaisesRegex()
        przy self.assertRaises(TypeError):
            self.assertRaisesRegex(ValueError)
        przy self.assertRaises(TypeError):
            self.assertRaisesRegex(1, 'expect')
        przy self.assertRaises(TypeError):
            self.assertRaisesRegex(object, 'expect')
        przy self.assertRaises(TypeError):
            self.assertRaisesRegex((ValueError, 1), 'expect')
        przy self.assertRaises(TypeError):
            self.assertRaisesRegex((ValueError, object), 'expect')

    def testAssertWarnsCallable(self):
        def _runtime_warn():
            warnings.warn("foo", RuntimeWarning)
        # Success when the right warning jest triggered, even several times
        self.assertWarns(RuntimeWarning, _runtime_warn)
        self.assertWarns(RuntimeWarning, _runtime_warn)
        # A tuple of warning classes jest accepted
        self.assertWarns((DeprecationWarning, RuntimeWarning), _runtime_warn)
        # *args oraz **kwargs also work
        self.assertWarns(RuntimeWarning,
                         warnings.warn, "foo", category=RuntimeWarning)
        # Failure when no warning jest triggered
        przy self.assertRaises(self.failureException):
            self.assertWarns(RuntimeWarning, lambda: 0)
        # Failure when the function jest Nic
        przy self.assertWarns(DeprecationWarning):
            self.assertWarns(RuntimeWarning, Nic)
        # Failure when another warning jest triggered
        przy warnings.catch_warnings():
            # Force default filter (in case tests are run przy -We)
            warnings.simplefilter("default", RuntimeWarning)
            przy self.assertRaises(self.failureException):
                self.assertWarns(DeprecationWarning, _runtime_warn)
        # Filters dla other warnings are nie modified
        przy warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)
            przy self.assertRaises(RuntimeWarning):
                self.assertWarns(DeprecationWarning, _runtime_warn)

    def testAssertWarnsContext(self):
        # Believe it albo not, it jest preferable to duplicate all tests above,
        # to make sure the __warningregistry__ $@ jest circumvented correctly.
        def _runtime_warn():
            warnings.warn("foo", RuntimeWarning)
        _runtime_warn_lineno = inspect.getsourcelines(_runtime_warn)[1]
        przy self.assertWarns(RuntimeWarning) jako cm:
            _runtime_warn()
        # A tuple of warning classes jest accepted
        przy self.assertWarns((DeprecationWarning, RuntimeWarning)) jako cm:
            _runtime_warn()
        # The context manager exposes various useful attributes
        self.assertIsInstance(cm.warning, RuntimeWarning)
        self.assertEqual(cm.warning.args[0], "foo")
        self.assertIn("test_case.py", cm.filename)
        self.assertEqual(cm.lineno, _runtime_warn_lineno + 1)
        # Same przy several warnings
        przy self.assertWarns(RuntimeWarning):
            _runtime_warn()
            _runtime_warn()
        przy self.assertWarns(RuntimeWarning):
            warnings.warn("foo", category=RuntimeWarning)
        # Failure when no warning jest triggered
        przy self.assertRaises(self.failureException):
            przy self.assertWarns(RuntimeWarning):
                dalej
        # Custom message
        przy self.assertRaisesRegex(self.failureException, 'foobar'):
            przy self.assertWarns(RuntimeWarning, msg='foobar'):
                dalej
        # Invalid keyword argument
        przy self.assertWarnsRegex(DeprecationWarning, 'foobar'), \
             self.assertRaises(AssertionError):
            przy self.assertWarns(RuntimeWarning, foobar=42):
                dalej
        # Failure when another warning jest triggered
        przy warnings.catch_warnings():
            # Force default filter (in case tests are run przy -We)
            warnings.simplefilter("default", RuntimeWarning)
            przy self.assertRaises(self.failureException):
                przy self.assertWarns(DeprecationWarning):
                    _runtime_warn()
        # Filters dla other warnings are nie modified
        przy warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)
            przy self.assertRaises(RuntimeWarning):
                przy self.assertWarns(DeprecationWarning):
                    _runtime_warn()

    def testAssertWarnsNoExceptionType(self):
        przy self.assertRaises(TypeError):
            self.assertWarns()
        przy self.assertRaises(TypeError):
            self.assertWarns(1)
        przy self.assertRaises(TypeError):
            self.assertWarns(object)
        przy self.assertRaises(TypeError):
            self.assertWarns((UserWarning, 1))
        przy self.assertRaises(TypeError):
            self.assertWarns((UserWarning, object))
        przy self.assertRaises(TypeError):
            self.assertWarns((UserWarning, Exception))

    def testAssertWarnsRegexCallable(self):
        def _runtime_warn(msg):
            warnings.warn(msg, RuntimeWarning)
        self.assertWarnsRegex(RuntimeWarning, "o+",
                              _runtime_warn, "foox")
        # Failure when no warning jest triggered
        przy self.assertRaises(self.failureException):
            self.assertWarnsRegex(RuntimeWarning, "o+",
                                  lambda: 0)
        # Failure when the function jest Nic
        przy self.assertWarns(DeprecationWarning):
            self.assertWarnsRegex(RuntimeWarning, "o+", Nic)
        # Failure when another warning jest triggered
        przy warnings.catch_warnings():
            # Force default filter (in case tests are run przy -We)
            warnings.simplefilter("default", RuntimeWarning)
            przy self.assertRaises(self.failureException):
                self.assertWarnsRegex(DeprecationWarning, "o+",
                                      _runtime_warn, "foox")
        # Failure when message doesn't match
        przy self.assertRaises(self.failureException):
            self.assertWarnsRegex(RuntimeWarning, "o+",
                                  _runtime_warn, "barz")
        # A little trickier: we ask RuntimeWarnings to be podnieśd, oraz then
        # check dla some of them.  It jest implementation-defined whether
        # non-matching RuntimeWarnings are simply re-raised, albo produce a
        # failureException.
        przy warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)
            przy self.assertRaises((RuntimeWarning, self.failureException)):
                self.assertWarnsRegex(RuntimeWarning, "o+",
                                      _runtime_warn, "barz")

    def testAssertWarnsRegexContext(self):
        # Same jako above, but przy assertWarnsRegex jako a context manager
        def _runtime_warn(msg):
            warnings.warn(msg, RuntimeWarning)
        _runtime_warn_lineno = inspect.getsourcelines(_runtime_warn)[1]
        przy self.assertWarnsRegex(RuntimeWarning, "o+") jako cm:
            _runtime_warn("foox")
        self.assertIsInstance(cm.warning, RuntimeWarning)
        self.assertEqual(cm.warning.args[0], "foox")
        self.assertIn("test_case.py", cm.filename)
        self.assertEqual(cm.lineno, _runtime_warn_lineno + 1)
        # Failure when no warning jest triggered
        przy self.assertRaises(self.failureException):
            przy self.assertWarnsRegex(RuntimeWarning, "o+"):
                dalej
        # Custom message
        przy self.assertRaisesRegex(self.failureException, 'foobar'):
            przy self.assertWarnsRegex(RuntimeWarning, 'o+', msg='foobar'):
                dalej
        # Invalid keyword argument
        przy self.assertWarnsRegex(DeprecationWarning, 'foobar'), \
             self.assertRaises(AssertionError):
            przy self.assertWarnsRegex(RuntimeWarning, 'o+', foobar=42):
                dalej
        # Failure when another warning jest triggered
        przy warnings.catch_warnings():
            # Force default filter (in case tests are run przy -We)
            warnings.simplefilter("default", RuntimeWarning)
            przy self.assertRaises(self.failureException):
                przy self.assertWarnsRegex(DeprecationWarning, "o+"):
                    _runtime_warn("foox")
        # Failure when message doesn't match
        przy self.assertRaises(self.failureException):
            przy self.assertWarnsRegex(RuntimeWarning, "o+"):
                _runtime_warn("barz")
        # A little trickier: we ask RuntimeWarnings to be podnieśd, oraz then
        # check dla some of them.  It jest implementation-defined whether
        # non-matching RuntimeWarnings are simply re-raised, albo produce a
        # failureException.
        przy warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)
            przy self.assertRaises((RuntimeWarning, self.failureException)):
                przy self.assertWarnsRegex(RuntimeWarning, "o+"):
                    _runtime_warn("barz")

    def testAssertWarnsRegexNoExceptionType(self):
        przy self.assertRaises(TypeError):
            self.assertWarnsRegex()
        przy self.assertRaises(TypeError):
            self.assertWarnsRegex(UserWarning)
        przy self.assertRaises(TypeError):
            self.assertWarnsRegex(1, 'expect')
        przy self.assertRaises(TypeError):
            self.assertWarnsRegex(object, 'expect')
        przy self.assertRaises(TypeError):
            self.assertWarnsRegex((UserWarning, 1), 'expect')
        przy self.assertRaises(TypeError):
            self.assertWarnsRegex((UserWarning, object), 'expect')
        przy self.assertRaises(TypeError):
            self.assertWarnsRegex((UserWarning, Exception), 'expect')

    @contextlib.contextmanager
    def assertNoStderr(self):
        przy captured_stderr() jako buf:
            uzyskaj
        self.assertEqual(buf.getvalue(), "")

    def assertLogRecords(self, records, matches):
        self.assertEqual(len(records), len(matches))
        dla rec, match w zip(records, matches):
            self.assertIsInstance(rec, logging.LogRecord)
            dla k, v w match.items():
                self.assertEqual(getattr(rec, k), v)

    def testAssertLogsDefaults(self):
        # defaults: root logger, level INFO
        przy self.assertNoStderr():
            przy self.assertLogs() jako cm:
                log_foo.info("1")
                log_foobar.debug("2")
            self.assertEqual(cm.output, ["INFO:foo:1"])
            self.assertLogRecords(cm.records, [{'name': 'foo'}])

    def testAssertLogsTwoMatchingMessages(self):
        # Same, but przy two matching log messages
        przy self.assertNoStderr():
            przy self.assertLogs() jako cm:
                log_foo.info("1")
                log_foobar.debug("2")
                log_quux.warning("3")
            self.assertEqual(cm.output, ["INFO:foo:1", "WARNING:quux:3"])
            self.assertLogRecords(cm.records,
                                   [{'name': 'foo'}, {'name': 'quux'}])

    def checkAssertLogsPerLevel(self, level):
        # Check level filtering
        przy self.assertNoStderr():
            przy self.assertLogs(level=level) jako cm:
                log_foo.warning("1")
                log_foobar.error("2")
                log_quux.critical("3")
            self.assertEqual(cm.output, ["ERROR:foo.bar:2", "CRITICAL:quux:3"])
            self.assertLogRecords(cm.records,
                                   [{'name': 'foo.bar'}, {'name': 'quux'}])

    def testAssertLogsPerLevel(self):
        self.checkAssertLogsPerLevel(logging.ERROR)
        self.checkAssertLogsPerLevel('ERROR')

    def checkAssertLogsPerLogger(self, logger):
        # Check per-logger filtering
        przy self.assertNoStderr():
            przy self.assertLogs(level='DEBUG') jako outer_cm:
                przy self.assertLogs(logger, level='DEBUG') jako cm:
                    log_foo.info("1")
                    log_foobar.debug("2")
                    log_quux.warning("3")
                self.assertEqual(cm.output, ["INFO:foo:1", "DEBUG:foo.bar:2"])
                self.assertLogRecords(cm.records,
                                       [{'name': 'foo'}, {'name': 'foo.bar'}])
            # The outer catchall caught the quux log
            self.assertEqual(outer_cm.output, ["WARNING:quux:3"])

    def testAssertLogsPerLogger(self):
        self.checkAssertLogsPerLogger(logging.getLogger('foo'))
        self.checkAssertLogsPerLogger('foo')

    def testAssertLogsFailureNoLogs(self):
        # Failure due to no logs
        przy self.assertNoStderr():
            przy self.assertRaises(self.failureException):
                przy self.assertLogs():
                    dalej

    def testAssertLogsFailureLevelTooHigh(self):
        # Failure due to level too high
        przy self.assertNoStderr():
            przy self.assertRaises(self.failureException):
                przy self.assertLogs(level='WARNING'):
                    log_foo.info("1")

    def testAssertLogsFailureMismatchingLogger(self):
        # Failure due to mismatching logger (and the logged message jest
        # dalejed through)
        przy self.assertLogs('quux', level='ERROR'):
            przy self.assertRaises(self.failureException):
                przy self.assertLogs('foo'):
                    log_quux.error("1")

    def testDeprecatedMethodNames(self):
        """
        Test that the deprecated methods podnieś a DeprecationWarning. See #9424.
        """
        old = (
            (self.failIfEqual, (3, 5)),
            (self.assertNotEquals, (3, 5)),
            (self.failUnlessEqual, (3, 3)),
            (self.assertEquals, (3, 3)),
            (self.failUnlessAlmostEqual, (2.0, 2.0)),
            (self.assertAlmostEquals, (2.0, 2.0)),
            (self.failIfAlmostEqual, (3.0, 5.0)),
            (self.assertNotAlmostEquals, (3.0, 5.0)),
            (self.failUnless, (Prawda,)),
            (self.assert_, (Prawda,)),
            (self.failUnlessRaises, (TypeError, lambda _: 3.14 + 'spam')),
            (self.failIf, (Nieprawda,)),
            (self.assertDictContainsSubset, (dict(a=1, b=2), dict(a=1, b=2, c=3))),
            (self.assertRaisesRegexp, (KeyError, 'foo', lambda: {}['foo'])),
            (self.assertRegexpMatches, ('bar', 'bar')),
        )
        dla meth, args w old:
            przy self.assertWarns(DeprecationWarning):
                meth(*args)

    # disable this test dla now. When the version where the fail* methods will
    # be removed jest decided, re-enable it oraz update the version
    def _testDeprecatedFailMethods(self):
        """Test that the deprecated fail* methods get removed w 3.x"""
        jeżeli sys.version_info[:2] < (3, 3):
            zwróć
        deprecated_names = [
            'failIfEqual', 'failUnlessEqual', 'failUnlessAlmostEqual',
            'failIfAlmostEqual', 'failUnless', 'failUnlessRaises', 'failIf',
            'assertDictContainsSubset',
        ]
        dla deprecated_name w deprecated_names:
            przy self.assertRaises(AttributeError):
                getattr(self, deprecated_name)  # remove these w 3.x

    def testDeepcopy(self):
        # Issue: 5660
        klasa TestableTest(unittest.TestCase):
            def testNothing(self):
                dalej

        test = TestableTest('testNothing')

        # This shouldn't blow up
        deepcopy(test)

    def testPickle(self):
        # Issue 10326

        # Can't use TestCase classes defined w Test klasa as
        # pickle does nie work przy inner classes
        test = unittest.TestCase('run')
        dla protocol w range(pickle.HIGHEST_PROTOCOL + 1):

            # blew up prior to fix
            pickled_test = pickle.dumps(test, protocol=protocol)
            unpickled_test = pickle.loads(pickled_test)
            self.assertEqual(test, unpickled_test)

            # exercise the TestCase instance w a way that will invoke
            # the type equality lookup mechanism
            unpickled_test.assertEqual(set(), set())

    def testKeyboardInterrupt(self):
        def _raise(self=Nic):
            podnieś KeyboardInterrupt
        def nothing(self):
            dalej

        klasa Test1(unittest.TestCase):
            test_something = _raise

        klasa Test2(unittest.TestCase):
            setUp = _raise
            test_something = nothing

        klasa Test3(unittest.TestCase):
            test_something = nothing
            tearDown = _raise

        klasa Test4(unittest.TestCase):
            def test_something(self):
                self.addCleanup(_raise)

        dla klass w (Test1, Test2, Test3, Test4):
            przy self.assertRaises(KeyboardInterrupt):
                klass('test_something').run()

    def testSkippingEverywhere(self):
        def _skip(self=Nic):
            podnieś unittest.SkipTest('some reason')
        def nothing(self):
            dalej

        klasa Test1(unittest.TestCase):
            test_something = _skip

        klasa Test2(unittest.TestCase):
            setUp = _skip
            test_something = nothing

        klasa Test3(unittest.TestCase):
            test_something = nothing
            tearDown = _skip

        klasa Test4(unittest.TestCase):
            def test_something(self):
                self.addCleanup(_skip)

        dla klass w (Test1, Test2, Test3, Test4):
            result = unittest.TestResult()
            klass('test_something').run(result)
            self.assertEqual(len(result.skipped), 1)
            self.assertEqual(result.testsRun, 1)

    def testSystemExit(self):
        def _raise(self=Nic):
            podnieś SystemExit
        def nothing(self):
            dalej

        klasa Test1(unittest.TestCase):
            test_something = _raise

        klasa Test2(unittest.TestCase):
            setUp = _raise
            test_something = nothing

        klasa Test3(unittest.TestCase):
            test_something = nothing
            tearDown = _raise

        klasa Test4(unittest.TestCase):
            def test_something(self):
                self.addCleanup(_raise)

        dla klass w (Test1, Test2, Test3, Test4):
            result = unittest.TestResult()
            klass('test_something').run(result)
            self.assertEqual(len(result.errors), 1)
            self.assertEqual(result.testsRun, 1)

    @support.cpython_only
    def testNoCycles(self):
        case = unittest.TestCase()
        wr = weakref.ref(case)
        przy support.disable_gc():
            usuń case
            self.assertNieprawda(wr())

    def test_no_exception_leak(self):
        # Issue #19880: TestCase.run() should nie keep a reference
        # to the exception
        klasa MyException(Exception):
            ninstance = 0

            def __init__(self):
                MyException.ninstance += 1
                Exception.__init__(self)

            def __del__(self):
                MyException.ninstance -= 1

        klasa TestCase(unittest.TestCase):
            def test1(self):
                podnieś MyException()

            @unittest.expectedFailure
            def test2(self):
                podnieś MyException()

        dla method_name w ('test1', 'test2'):
            testcase = TestCase(method_name)
            testcase.run()
            self.assertEqual(MyException.ninstance, 0)


jeżeli __name__ == "__main__":
    unittest.main()
