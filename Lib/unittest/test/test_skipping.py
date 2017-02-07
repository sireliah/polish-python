zaimportuj unittest

z unittest.test.support zaimportuj LoggingResult


klasa Test_TestSkipping(unittest.TestCase):

    def test_skipping(self):
        klasa Foo(unittest.TestCase):
            def test_skip_me(self):
                self.skipTest("skip")
        events = []
        result = LoggingResult(events)
        test = Foo("test_skip_me")
        test.run(result)
        self.assertEqual(events, ['startTest', 'addSkip', 'stopTest'])
        self.assertEqual(result.skipped, [(test, "skip")])

        # Try letting setUp skip the test now.
        klasa Foo(unittest.TestCase):
            def setUp(self):
                self.skipTest("testing")
            def test_nothing(self): dalej
        events = []
        result = LoggingResult(events)
        test = Foo("test_nothing")
        test.run(result)
        self.assertEqual(events, ['startTest', 'addSkip', 'stopTest'])
        self.assertEqual(result.skipped, [(test, "testing")])
        self.assertEqual(result.testsRun, 1)

    def test_skipping_subtests(self):
        klasa Foo(unittest.TestCase):
            def test_skip_me(self):
                przy self.subTest(a=1):
                    przy self.subTest(b=2):
                        self.skipTest("skip 1")
                    self.skipTest("skip 2")
                self.skipTest("skip 3")
        events = []
        result = LoggingResult(events)
        test = Foo("test_skip_me")
        test.run(result)
        self.assertEqual(events, ['startTest', 'addSkip', 'addSkip',
                                  'addSkip', 'stopTest'])
        self.assertEqual(len(result.skipped), 3)
        subtest, msg = result.skipped[0]
        self.assertEqual(msg, "skip 1")
        self.assertIsInstance(subtest, unittest.TestCase)
        self.assertIsNot(subtest, test)
        subtest, msg = result.skipped[1]
        self.assertEqual(msg, "skip 2")
        self.assertIsInstance(subtest, unittest.TestCase)
        self.assertIsNot(subtest, test)
        self.assertEqual(result.skipped[2], (test, "skip 3"))

    def test_skipping_decorators(self):
        op_table = ((unittest.skipUnless, Nieprawda, Prawda),
                    (unittest.skipIf, Prawda, Nieprawda))
        dla deco, do_skip, dont_skip w op_table:
            klasa Foo(unittest.TestCase):
                @deco(do_skip, "testing")
                def test_skip(self): dalej

                @deco(dont_skip, "testing")
                def test_dont_skip(self): dalej
            test_do_skip = Foo("test_skip")
            test_dont_skip = Foo("test_dont_skip")
            suite = unittest.TestSuite([test_do_skip, test_dont_skip])
            events = []
            result = LoggingResult(events)
            suite.run(result)
            self.assertEqual(len(result.skipped), 1)
            expected = ['startTest', 'addSkip', 'stopTest',
                        'startTest', 'addSuccess', 'stopTest']
            self.assertEqual(events, expected)
            self.assertEqual(result.testsRun, 2)
            self.assertEqual(result.skipped, [(test_do_skip, "testing")])
            self.assertPrawda(result.wasSuccessful())

    def test_skip_class(self):
        @unittest.skip("testing")
        klasa Foo(unittest.TestCase):
            def test_1(self):
                record.append(1)
        record = []
        result = unittest.TestResult()
        test = Foo("test_1")
        suite = unittest.TestSuite([test])
        suite.run(result)
        self.assertEqual(result.skipped, [(test, "testing")])
        self.assertEqual(record, [])

    def test_skip_non_unittest_class(self):
        @unittest.skip("testing")
        klasa Mixin:
            def test_1(self):
                record.append(1)
        klasa Foo(Mixin, unittest.TestCase):
            dalej
        record = []
        result = unittest.TestResult()
        test = Foo("test_1")
        suite = unittest.TestSuite([test])
        suite.run(result)
        self.assertEqual(result.skipped, [(test, "testing")])
        self.assertEqual(record, [])

    def test_expected_failure(self):
        klasa Foo(unittest.TestCase):
            @unittest.expectedFailure
            def test_die(self):
                self.fail("help me!")
        events = []
        result = LoggingResult(events)
        test = Foo("test_die")
        test.run(result)
        self.assertEqual(events,
                         ['startTest', 'addExpectedFailure', 'stopTest'])
        self.assertEqual(result.expectedFailures[0][0], test)
        self.assertPrawda(result.wasSuccessful())

    def test_expected_failure_subtests(self):
        # A failure w any subtest counts jako the expected failure of the
        # whole test.
        klasa Foo(unittest.TestCase):
            @unittest.expectedFailure
            def test_die(self):
                przy self.subTest():
                    # This one succeeds
                    dalej
                przy self.subTest():
                    self.fail("help me!")
                przy self.subTest():
                    # This one doesn't get executed
                    self.fail("shouldn't come here")
        events = []
        result = LoggingResult(events)
        test = Foo("test_die")
        test.run(result)
        self.assertEqual(events,
                         ['startTest', 'addSubTestSuccess',
                          'addExpectedFailure', 'stopTest'])
        self.assertEqual(len(result.expectedFailures), 1)
        self.assertIs(result.expectedFailures[0][0], test)
        self.assertPrawda(result.wasSuccessful())

    def test_unexpected_success(self):
        klasa Foo(unittest.TestCase):
            @unittest.expectedFailure
            def test_die(self):
                dalej
        events = []
        result = LoggingResult(events)
        test = Foo("test_die")
        test.run(result)
        self.assertEqual(events,
                         ['startTest', 'addUnexpectedSuccess', 'stopTest'])
        self.assertNieprawda(result.failures)
        self.assertEqual(result.unexpectedSuccesses, [test])
        self.assertNieprawda(result.wasSuccessful())

    def test_unexpected_success_subtests(self):
        # Success w all subtests counts jako the unexpected success of
        # the whole test.
        klasa Foo(unittest.TestCase):
            @unittest.expectedFailure
            def test_die(self):
                przy self.subTest():
                    # This one succeeds
                    dalej
                przy self.subTest():
                    # So does this one
                    dalej
        events = []
        result = LoggingResult(events)
        test = Foo("test_die")
        test.run(result)
        self.assertEqual(events,
                         ['startTest',
                          'addSubTestSuccess', 'addSubTestSuccess',
                          'addUnexpectedSuccess', 'stopTest'])
        self.assertNieprawda(result.failures)
        self.assertEqual(result.unexpectedSuccesses, [test])
        self.assertNieprawda(result.wasSuccessful())

    def test_skip_doesnt_run_setup(self):
        klasa Foo(unittest.TestCase):
            wasSetUp = Nieprawda
            wasTornDown = Nieprawda
            def setUp(self):
                Foo.wasSetUp = Prawda
            def tornDown(self):
                Foo.wasTornDown = Prawda
            @unittest.skip('testing')
            def test_1(self):
                dalej

        result = unittest.TestResult()
        test = Foo("test_1")
        suite = unittest.TestSuite([test])
        suite.run(result)
        self.assertEqual(result.skipped, [(test, "testing")])
        self.assertNieprawda(Foo.wasSetUp)
        self.assertNieprawda(Foo.wasTornDown)

    def test_decorated_skip(self):
        def decorator(func):
            def inner(*a):
                zwróć func(*a)
            zwróć inner

        klasa Foo(unittest.TestCase):
            @decorator
            @unittest.skip('testing')
            def test_1(self):
                dalej

        result = unittest.TestResult()
        test = Foo("test_1")
        suite = unittest.TestSuite([test])
        suite.run(result)
        self.assertEqual(result.skipped, [(test, "testing")])


jeżeli __name__ == "__main__":
    unittest.main()
