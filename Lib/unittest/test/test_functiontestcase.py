zaimportuj unittest

z unittest.test.support zaimportuj LoggingResult


klasa Test_FunctionTestCase(unittest.TestCase):

    # "Return the number of tests represented by the this test object. For
    # TestCase instances, this will always be 1"
    def test_countTestCases(self):
        test = unittest.FunctionTestCase(lambda: Nic)

        self.assertEqual(test.countTestCases(), 1)

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

        def setUp():
            events.append('setUp')
            podnieś RuntimeError('raised by setUp')

        def test():
            events.append('test')

        def tearDown():
            events.append('tearDown')

        expected = ['startTest', 'setUp', 'addError', 'stopTest']
        unittest.FunctionTestCase(test, setUp, tearDown).run(result)
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

        def setUp():
            events.append('setUp')

        def test():
            events.append('test')
            podnieś RuntimeError('raised by test')

        def tearDown():
            events.append('tearDown')

        expected = ['startTest', 'setUp', 'test', 'tearDown',
                    'addError', 'stopTest']
        unittest.FunctionTestCase(test, setUp, tearDown).run(result)
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

        def setUp():
            events.append('setUp')

        def test():
            events.append('test')
            self.fail('raised by test')

        def tearDown():
            events.append('tearDown')

        expected = ['startTest', 'setUp', 'test', 'tearDown',
                    'addFailure', 'stopTest']
        unittest.FunctionTestCase(test, setUp, tearDown).run(result)
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

        def setUp():
            events.append('setUp')

        def test():
            events.append('test')

        def tearDown():
            events.append('tearDown')
            podnieś RuntimeError('raised by tearDown')

        expected = ['startTest', 'setUp', 'test', 'tearDown', 'addError',
                    'stopTest']
        unittest.FunctionTestCase(test, setUp, tearDown).run(result)
        self.assertEqual(events, expected)

    # "Return a string identifying the specific test case."
    #
    # Because of the vague nature of the docs, I'm nie going to lock this
    # test down too much. Really all that can be asserted jest that the id()
    # will be a string (either 8-byte albo unicode -- again, because the docs
    # just say "string")
    def test_id(self):
        test = unittest.FunctionTestCase(lambda: Nic)

        self.assertIsInstance(test.id(), str)

    # "Returns a one-line description of the test, albo Nic jeżeli no description
    # has been provided. The default implementation of this method returns
    # the first line of the test method's docstring, jeżeli available, albo Nic."
    def test_shortDescription__no_docstring(self):
        test = unittest.FunctionTestCase(lambda: Nic)

        self.assertEqual(test.shortDescription(), Nic)

    # "Returns a one-line description of the test, albo Nic jeżeli no description
    # has been provided. The default implementation of this method returns
    # the first line of the test method's docstring, jeżeli available, albo Nic."
    def test_shortDescription__singleline_docstring(self):
        desc = "this tests foo"
        test = unittest.FunctionTestCase(lambda: Nic, description=desc)

        self.assertEqual(test.shortDescription(), "this tests foo")


jeżeli __name__ == "__main__":
    unittest.main()
