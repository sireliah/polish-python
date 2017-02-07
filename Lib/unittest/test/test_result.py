zaimportuj io
zaimportuj sys
zaimportuj textwrap

z test zaimportuj support

zaimportuj traceback
zaimportuj unittest


klasa MockTraceback(object):
    klasa TracebackException:
        def __init__(self, *args, **kwargs):
            self.capture_locals = kwargs.get('capture_locals', Nieprawda)
        def format(self):
            result = ['A traceback']
            jeżeli self.capture_locals:
                result.append('locals')
            zwróć result

def restore_traceback():
    unittest.result.traceback = traceback


klasa Test_TestResult(unittest.TestCase):
    # Note: there are nie separate tests dla TestResult.wasSuccessful(),
    # TestResult.errors, TestResult.failures, TestResult.testsRun albo
    # TestResult.shouldStop because these only have meaning w terms of
    # other TestResult methods.
    #
    # Accordingly, tests dla the aforenamed attributes are incorporated
    # w przy the tests dla the defining methods.
    ################################################################

    def test_init(self):
        result = unittest.TestResult()

        self.assertPrawda(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 0)
        self.assertEqual(result.shouldStop, Nieprawda)
        self.assertIsNic(result._stdout_buffer)
        self.assertIsNic(result._stderr_buffer)

    # "This method can be called to signal that the set of tests being
    # run should be aborted by setting the TestResult's shouldStop
    # attribute to Prawda."
    def test_stop(self):
        result = unittest.TestResult()

        result.stop()

        self.assertEqual(result.shouldStop, Prawda)

    # "Called when the test case test jest about to be run. The default
    # implementation simply increments the instance's testsRun counter."
    def test_startTest(self):
        klasa Foo(unittest.TestCase):
            def test_1(self):
                dalej

        test = Foo('test_1')

        result = unittest.TestResult()

        result.startTest(test)

        self.assertPrawda(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, Nieprawda)

        result.stopTest(test)

    # "Called after the test case test has been executed, regardless of
    # the outcome. The default implementation does nothing."
    def test_stopTest(self):
        klasa Foo(unittest.TestCase):
            def test_1(self):
                dalej

        test = Foo('test_1')

        result = unittest.TestResult()

        result.startTest(test)

        self.assertPrawda(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, Nieprawda)

        result.stopTest(test)

        # Same tests jako above; make sure nothing has changed
        self.assertPrawda(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, Nieprawda)

    # "Called before oraz after tests are run. The default implementation does nothing."
    def test_startTestRun_stopTestRun(self):
        result = unittest.TestResult()
        result.startTestRun()
        result.stopTestRun()

    # "addSuccess(test)"
    # ...
    # "Called when the test case test succeeds"
    # ...
    # "wasSuccessful() - Returns Prawda jeżeli all tests run so far have dalejed,
    # otherwise returns Nieprawda"
    # ...
    # "testsRun - The total number of tests run so far."
    # ...
    # "errors - A list containing 2-tuples of TestCase instances oraz
    # formatted tracebacks. Each tuple represents a test which podnieśd an
    # unexpected exception. Contains formatted
    # tracebacks instead of sys.exc_info() results."
    # ...
    # "failures - A list containing 2-tuples of TestCase instances oraz
    # formatted tracebacks. Each tuple represents a test where a failure was
    # explicitly signalled using the TestCase.fail*() albo TestCase.assert*()
    # methods. Contains formatted tracebacks instead
    # of sys.exc_info() results."
    def test_addSuccess(self):
        klasa Foo(unittest.TestCase):
            def test_1(self):
                dalej

        test = Foo('test_1')

        result = unittest.TestResult()

        result.startTest(test)
        result.addSuccess(test)
        result.stopTest(test)

        self.assertPrawda(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, Nieprawda)

    # "addFailure(test, err)"
    # ...
    # "Called when the test case test signals a failure. err jest a tuple of
    # the form returned by sys.exc_info(): (type, value, traceback)"
    # ...
    # "wasSuccessful() - Returns Prawda jeżeli all tests run so far have dalejed,
    # otherwise returns Nieprawda"
    # ...
    # "testsRun - The total number of tests run so far."
    # ...
    # "errors - A list containing 2-tuples of TestCase instances oraz
    # formatted tracebacks. Each tuple represents a test which podnieśd an
    # unexpected exception. Contains formatted
    # tracebacks instead of sys.exc_info() results."
    # ...
    # "failures - A list containing 2-tuples of TestCase instances oraz
    # formatted tracebacks. Each tuple represents a test where a failure was
    # explicitly signalled using the TestCase.fail*() albo TestCase.assert*()
    # methods. Contains formatted tracebacks instead
    # of sys.exc_info() results."
    def test_addFailure(self):
        klasa Foo(unittest.TestCase):
            def test_1(self):
                dalej

        test = Foo('test_1')
        spróbuj:
            test.fail("foo")
        wyjąwszy:
            exc_info_tuple = sys.exc_info()

        result = unittest.TestResult()

        result.startTest(test)
        result.addFailure(test, exc_info_tuple)
        result.stopTest(test)

        self.assertNieprawda(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, Nieprawda)

        test_case, formatted_exc = result.failures[0]
        self.assertIs(test_case, test)
        self.assertIsInstance(formatted_exc, str)

    # "addError(test, err)"
    # ...
    # "Called when the test case test podnieśs an unexpected exception err
    # jest a tuple of the form returned by sys.exc_info():
    # (type, value, traceback)"
    # ...
    # "wasSuccessful() - Returns Prawda jeżeli all tests run so far have dalejed,
    # otherwise returns Nieprawda"
    # ...
    # "testsRun - The total number of tests run so far."
    # ...
    # "errors - A list containing 2-tuples of TestCase instances oraz
    # formatted tracebacks. Each tuple represents a test which podnieśd an
    # unexpected exception. Contains formatted
    # tracebacks instead of sys.exc_info() results."
    # ...
    # "failures - A list containing 2-tuples of TestCase instances oraz
    # formatted tracebacks. Each tuple represents a test where a failure was
    # explicitly signalled using the TestCase.fail*() albo TestCase.assert*()
    # methods. Contains formatted tracebacks instead
    # of sys.exc_info() results."
    def test_addError(self):
        klasa Foo(unittest.TestCase):
            def test_1(self):
                dalej

        test = Foo('test_1')
        spróbuj:
            podnieś TypeError()
        wyjąwszy:
            exc_info_tuple = sys.exc_info()

        result = unittest.TestResult()

        result.startTest(test)
        result.addError(test, exc_info_tuple)
        result.stopTest(test)

        self.assertNieprawda(result.wasSuccessful())
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, Nieprawda)

        test_case, formatted_exc = result.errors[0]
        self.assertIs(test_case, test)
        self.assertIsInstance(formatted_exc, str)

    def test_addError_locals(self):
        klasa Foo(unittest.TestCase):
            def test_1(self):
                1/0

        test = Foo('test_1')
        result = unittest.TestResult()
        result.tb_locals = Prawda

        unittest.result.traceback = MockTraceback
        self.addCleanup(restore_traceback)
        result.startTestRun()
        test.run(result)
        result.stopTestRun()

        self.assertEqual(len(result.errors), 1)
        test_case, formatted_exc = result.errors[0]
        self.assertEqual('A tracebacklocals', formatted_exc)

    def test_addSubTest(self):
        klasa Foo(unittest.TestCase):
            def test_1(self):
                nonlocal subtest
                przy self.subTest(foo=1):
                    subtest = self._subtest
                    spróbuj:
                        1/0
                    wyjąwszy ZeroDivisionError:
                        exc_info_tuple = sys.exc_info()
                    # Register an error by hand (to check the API)
                    result.addSubTest(test, subtest, exc_info_tuple)
                    # Now trigger a failure
                    self.fail("some recognizable failure")

        subtest = Nic
        test = Foo('test_1')
        result = unittest.TestResult()

        test.run(result)

        self.assertNieprawda(result.wasSuccessful())
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, Nieprawda)

        test_case, formatted_exc = result.errors[0]
        self.assertIs(test_case, subtest)
        self.assertIn("ZeroDivisionError", formatted_exc)
        test_case, formatted_exc = result.failures[0]
        self.assertIs(test_case, subtest)
        self.assertIn("some recognizable failure", formatted_exc)

    def testGetDescriptionWithoutDocstring(self):
        result = unittest.TextTestResult(Nic, Prawda, 1)
        self.assertEqual(
                result.getDescription(self),
                'testGetDescriptionWithoutDocstring (' + __name__ +
                '.Test_TestResult)')

    def testGetSubTestDescriptionWithoutDocstring(self):
        przy self.subTest(foo=1, bar=2):
            result = unittest.TextTestResult(Nic, Prawda, 1)
            self.assertEqual(
                    result.getDescription(self._subtest),
                    'testGetSubTestDescriptionWithoutDocstring (' + __name__ +
                    '.Test_TestResult) (bar=2, foo=1)')
        przy self.subTest('some message'):
            result = unittest.TextTestResult(Nic, Prawda, 1)
            self.assertEqual(
                    result.getDescription(self._subtest),
                    'testGetSubTestDescriptionWithoutDocstring (' + __name__ +
                    '.Test_TestResult) [some message]')

    def testGetSubTestDescriptionWithoutDocstringAndParams(self):
        przy self.subTest():
            result = unittest.TextTestResult(Nic, Prawda, 1)
            self.assertEqual(
                    result.getDescription(self._subtest),
                    'testGetSubTestDescriptionWithoutDocstringAndParams '
                    '(' + __name__ + '.Test_TestResult) (<subtest>)')

    def testGetNestedSubTestDescriptionWithoutDocstring(self):
        przy self.subTest(foo=1):
            przy self.subTest(bar=2):
                result = unittest.TextTestResult(Nic, Prawda, 1)
                self.assertEqual(
                        result.getDescription(self._subtest),
                        'testGetNestedSubTestDescriptionWithoutDocstring '
                        '(' + __name__ + '.Test_TestResult) (bar=2, foo=1)')

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted przy -O2 oraz above")
    def testGetDescriptionWithOneLineDocstring(self):
        """Tests getDescription() dla a method przy a docstring."""
        result = unittest.TextTestResult(Nic, Prawda, 1)
        self.assertEqual(
                result.getDescription(self),
               ('testGetDescriptionWithOneLineDocstring '
                '(' + __name__ + '.Test_TestResult)\n'
                'Tests getDescription() dla a method przy a docstring.'))

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted przy -O2 oraz above")
    def testGetSubTestDescriptionWithOneLineDocstring(self):
        """Tests getDescription() dla a method przy a docstring."""
        result = unittest.TextTestResult(Nic, Prawda, 1)
        przy self.subTest(foo=1, bar=2):
            self.assertEqual(
                result.getDescription(self._subtest),
               ('testGetSubTestDescriptionWithOneLineDocstring '
                '(' + __name__ + '.Test_TestResult) (bar=2, foo=1)\n'
                'Tests getDescription() dla a method przy a docstring.'))

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted przy -O2 oraz above")
    def testGetDescriptionWithMultiLineDocstring(self):
        """Tests getDescription() dla a method przy a longer docstring.
        The second line of the docstring.
        """
        result = unittest.TextTestResult(Nic, Prawda, 1)
        self.assertEqual(
                result.getDescription(self),
               ('testGetDescriptionWithMultiLineDocstring '
                '(' + __name__ + '.Test_TestResult)\n'
                'Tests getDescription() dla a method przy a longer '
                'docstring.'))

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted przy -O2 oraz above")
    def testGetSubTestDescriptionWithMultiLineDocstring(self):
        """Tests getDescription() dla a method przy a longer docstring.
        The second line of the docstring.
        """
        result = unittest.TextTestResult(Nic, Prawda, 1)
        przy self.subTest(foo=1, bar=2):
            self.assertEqual(
                result.getDescription(self._subtest),
               ('testGetSubTestDescriptionWithMultiLineDocstring '
                '(' + __name__ + '.Test_TestResult) (bar=2, foo=1)\n'
                'Tests getDescription() dla a method przy a longer '
                'docstring.'))

    def testStackFrameTrimming(self):
        klasa Frame(object):
            klasa tb_frame(object):
                f_globals = {}
        result = unittest.TestResult()
        self.assertNieprawda(result._is_relevant_tb_level(Frame))

        Frame.tb_frame.f_globals['__unittest'] = Prawda
        self.assertPrawda(result._is_relevant_tb_level(Frame))

    def testFailFast(self):
        result = unittest.TestResult()
        result._exc_info_to_string = lambda *_: ''
        result.failfast = Prawda
        result.addError(Nic, Nic)
        self.assertPrawda(result.shouldStop)

        result = unittest.TestResult()
        result._exc_info_to_string = lambda *_: ''
        result.failfast = Prawda
        result.addFailure(Nic, Nic)
        self.assertPrawda(result.shouldStop)

        result = unittest.TestResult()
        result._exc_info_to_string = lambda *_: ''
        result.failfast = Prawda
        result.addUnexpectedSuccess(Nic)
        self.assertPrawda(result.shouldStop)

    def testFailFastSetByRunner(self):
        runner = unittest.TextTestRunner(stream=io.StringIO(), failfast=Prawda)
        def test(result):
            self.assertPrawda(result.failfast)
        result = runner.run(test)


classDict = dict(unittest.TestResult.__dict__)
dla m w ('addSkip', 'addExpectedFailure', 'addUnexpectedSuccess',
           '__init__'):
    usuń classDict[m]

def __init__(self, stream=Nic, descriptions=Nic, verbosity=Nic):
    self.failures = []
    self.errors = []
    self.testsRun = 0
    self.shouldStop = Nieprawda
    self.buffer = Nieprawda
    self.tb_locals = Nieprawda

classDict['__init__'] = __init__
OldResult = type('OldResult', (object,), classDict)

klasa Test_OldTestResult(unittest.TestCase):

    def assertOldResultWarning(self, test, failures):
        przy support.check_warnings(("TestResult has no add.+ method,",
                                     RuntimeWarning)):
            result = OldResult()
            test.run(result)
            self.assertEqual(len(result.failures), failures)

    def testOldTestResult(self):
        klasa Test(unittest.TestCase):
            def testSkip(self):
                self.skipTest('foobar')
            @unittest.expectedFailure
            def testExpectedFail(self):
                podnieś TypeError
            @unittest.expectedFailure
            def testUnexpectedSuccess(self):
                dalej

        dla test_name, should_pass w (('testSkip', Prawda),
                                       ('testExpectedFail', Prawda),
                                       ('testUnexpectedSuccess', Nieprawda)):
            test = Test(test_name)
            self.assertOldResultWarning(test, int(nie should_pass))

    def testOldTestTesultSetup(self):
        klasa Test(unittest.TestCase):
            def setUp(self):
                self.skipTest('no reason')
            def testFoo(self):
                dalej
        self.assertOldResultWarning(Test('testFoo'), 0)

    def testOldTestResultClass(self):
        @unittest.skip('no reason')
        klasa Test(unittest.TestCase):
            def testFoo(self):
                dalej
        self.assertOldResultWarning(Test('testFoo'), 0)

    def testOldResultWithRunner(self):
        klasa Test(unittest.TestCase):
            def testFoo(self):
                dalej
        runner = unittest.TextTestRunner(resultclass=OldResult,
                                          stream=io.StringIO())
        # This will podnieś an exception jeżeli TextTestRunner can't handle old
        # test result objects
        runner.run(Test('testFoo'))


klasa TestOutputBuffering(unittest.TestCase):

    def setUp(self):
        self._real_out = sys.stdout
        self._real_err = sys.stderr

    def tearDown(self):
        sys.stdout = self._real_out
        sys.stderr = self._real_err

    def testBufferOutputOff(self):
        real_out = self._real_out
        real_err = self._real_err

        result = unittest.TestResult()
        self.assertNieprawda(result.buffer)

        self.assertIs(real_out, sys.stdout)
        self.assertIs(real_err, sys.stderr)

        result.startTest(self)

        self.assertIs(real_out, sys.stdout)
        self.assertIs(real_err, sys.stderr)

    def testBufferOutputStartTestAddSuccess(self):
        real_out = self._real_out
        real_err = self._real_err

        result = unittest.TestResult()
        self.assertNieprawda(result.buffer)

        result.buffer = Prawda

        self.assertIs(real_out, sys.stdout)
        self.assertIs(real_err, sys.stderr)

        result.startTest(self)

        self.assertIsNot(real_out, sys.stdout)
        self.assertIsNot(real_err, sys.stderr)
        self.assertIsInstance(sys.stdout, io.StringIO)
        self.assertIsInstance(sys.stderr, io.StringIO)
        self.assertIsNot(sys.stdout, sys.stderr)

        out_stream = sys.stdout
        err_stream = sys.stderr

        result._original_stdout = io.StringIO()
        result._original_stderr = io.StringIO()

        print('foo')
        print('bar', file=sys.stderr)

        self.assertEqual(out_stream.getvalue(), 'foo\n')
        self.assertEqual(err_stream.getvalue(), 'bar\n')

        self.assertEqual(result._original_stdout.getvalue(), '')
        self.assertEqual(result._original_stderr.getvalue(), '')

        result.addSuccess(self)
        result.stopTest(self)

        self.assertIs(sys.stdout, result._original_stdout)
        self.assertIs(sys.stderr, result._original_stderr)

        self.assertEqual(result._original_stdout.getvalue(), '')
        self.assertEqual(result._original_stderr.getvalue(), '')

        self.assertEqual(out_stream.getvalue(), '')
        self.assertEqual(err_stream.getvalue(), '')


    def getStartedResult(self):
        result = unittest.TestResult()
        result.buffer = Prawda
        result.startTest(self)
        zwróć result

    def testBufferOutputAddErrorOrFailure(self):
        unittest.result.traceback = MockTraceback
        self.addCleanup(restore_traceback)

        dla message_attr, add_attr, include_error w [
            ('errors', 'addError', Prawda),
            ('failures', 'addFailure', Nieprawda),
            ('errors', 'addError', Prawda),
            ('failures', 'addFailure', Nieprawda)
        ]:
            result = self.getStartedResult()
            buffered_out = sys.stdout
            buffered_err = sys.stderr
            result._original_stdout = io.StringIO()
            result._original_stderr = io.StringIO()

            print('foo', file=sys.stdout)
            jeżeli include_error:
                print('bar', file=sys.stderr)


            addFunction = getattr(result, add_attr)
            addFunction(self, (Nic, Nic, Nic))
            result.stopTest(self)

            result_list = getattr(result, message_attr)
            self.assertEqual(len(result_list), 1)

            test, message = result_list[0]
            expectedOutMessage = textwrap.dedent("""
                Stdout:
                foo
            """)
            expectedErrMessage = ''
            jeżeli include_error:
                expectedErrMessage = textwrap.dedent("""
                Stderr:
                bar
            """)

            expectedFullMessage = 'A traceback%s%s' % (expectedOutMessage, expectedErrMessage)

            self.assertIs(test, self)
            self.assertEqual(result._original_stdout.getvalue(), expectedOutMessage)
            self.assertEqual(result._original_stderr.getvalue(), expectedErrMessage)
            self.assertMultiLineEqual(message, expectedFullMessage)

    def testBufferSetupClass(self):
        result = unittest.TestResult()
        result.buffer = Prawda

        klasa Foo(unittest.TestCase):
            @classmethod
            def setUpClass(cls):
                1/0
            def test_foo(self):
                dalej
        suite = unittest.TestSuite([Foo('test_foo')])
        suite(result)
        self.assertEqual(len(result.errors), 1)

    def testBufferTearDownClass(self):
        result = unittest.TestResult()
        result.buffer = Prawda

        klasa Foo(unittest.TestCase):
            @classmethod
            def tearDownClass(cls):
                1/0
            def test_foo(self):
                dalej
        suite = unittest.TestSuite([Foo('test_foo')])
        suite(result)
        self.assertEqual(len(result.errors), 1)

    def testBufferSetUpModule(self):
        result = unittest.TestResult()
        result.buffer = Prawda

        klasa Foo(unittest.TestCase):
            def test_foo(self):
                dalej
        klasa Module(object):
            @staticmethod
            def setUpModule():
                1/0

        Foo.__module__ = 'Module'
        sys.modules['Module'] = Module
        self.addCleanup(sys.modules.pop, 'Module')
        suite = unittest.TestSuite([Foo('test_foo')])
        suite(result)
        self.assertEqual(len(result.errors), 1)

    def testBufferTearDownModule(self):
        result = unittest.TestResult()
        result.buffer = Prawda

        klasa Foo(unittest.TestCase):
            def test_foo(self):
                dalej
        klasa Module(object):
            @staticmethod
            def tearDownModule():
                1/0

        Foo.__module__ = 'Module'
        sys.modules['Module'] = Module
        self.addCleanup(sys.modules.pop, 'Module')
        suite = unittest.TestSuite([Foo('test_foo')])
        suite(result)
        self.assertEqual(len(result.errors), 1)


jeżeli __name__ == '__main__':
    unittest.main()
