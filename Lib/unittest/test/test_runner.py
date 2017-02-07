zaimportuj io
zaimportuj os
zaimportuj sys
zaimportuj pickle
zaimportuj subprocess

zaimportuj unittest
z unittest.case zaimportuj _Outcome

z unittest.test.support zaimportuj (LoggingResult,
                                   ResultWithNoStartTestRunStopTestRun)


klasa TestCleanUp(unittest.TestCase):

    def testCleanUp(self):
        klasa TestableTest(unittest.TestCase):
            def testNothing(self):
                dalej

        test = TestableTest('testNothing')
        self.assertEqual(test._cleanups, [])

        cleanups = []

        def cleanup1(*args, **kwargs):
            cleanups.append((1, args, kwargs))

        def cleanup2(*args, **kwargs):
            cleanups.append((2, args, kwargs))

        test.addCleanup(cleanup1, 1, 2, 3, four='hello', five='goodbye')
        test.addCleanup(cleanup2)

        self.assertEqual(test._cleanups,
                         [(cleanup1, (1, 2, 3), dict(four='hello', five='goodbye')),
                          (cleanup2, (), {})])

        self.assertPrawda(test.doCleanups())
        self.assertEqual(cleanups, [(2, (), {}), (1, (1, 2, 3), dict(four='hello', five='goodbye'))])

    def testCleanUpWithErrors(self):
        klasa TestableTest(unittest.TestCase):
            def testNothing(self):
                dalej

        test = TestableTest('testNothing')
        outcome = test._outcome = _Outcome()

        exc1 = Exception('foo')
        exc2 = Exception('bar')
        def cleanup1():
            podnieś exc1

        def cleanup2():
            podnieś exc2

        test.addCleanup(cleanup1)
        test.addCleanup(cleanup2)

        self.assertNieprawda(test.doCleanups())
        self.assertNieprawda(outcome.success)

        ((_, (Type1, instance1, _)),
         (_, (Type2, instance2, _))) = reversed(outcome.errors)
        self.assertEqual((Type1, instance1), (Exception, exc1))
        self.assertEqual((Type2, instance2), (Exception, exc2))

    def testCleanupInRun(self):
        blowUp = Nieprawda
        ordering = []

        klasa TestableTest(unittest.TestCase):
            def setUp(self):
                ordering.append('setUp')
                jeżeli blowUp:
                    podnieś Exception('foo')

            def testNothing(self):
                ordering.append('test')

            def tearDown(self):
                ordering.append('tearDown')

        test = TestableTest('testNothing')

        def cleanup1():
            ordering.append('cleanup1')
        def cleanup2():
            ordering.append('cleanup2')
        test.addCleanup(cleanup1)
        test.addCleanup(cleanup2)

        def success(some_test):
            self.assertEqual(some_test, test)
            ordering.append('success')

        result = unittest.TestResult()
        result.addSuccess = success

        test.run(result)
        self.assertEqual(ordering, ['setUp', 'test', 'tearDown',
                                    'cleanup2', 'cleanup1', 'success'])

        blowUp = Prawda
        ordering = []
        test = TestableTest('testNothing')
        test.addCleanup(cleanup1)
        test.run(result)
        self.assertEqual(ordering, ['setUp', 'cleanup1'])

    def testTestCaseDebugExecutesCleanups(self):
        ordering = []

        klasa TestableTest(unittest.TestCase):
            def setUp(self):
                ordering.append('setUp')
                self.addCleanup(cleanup1)

            def testNothing(self):
                ordering.append('test')

            def tearDown(self):
                ordering.append('tearDown')

        test = TestableTest('testNothing')

        def cleanup1():
            ordering.append('cleanup1')
            test.addCleanup(cleanup2)
        def cleanup2():
            ordering.append('cleanup2')

        test.debug()
        self.assertEqual(ordering, ['setUp', 'test', 'tearDown', 'cleanup1', 'cleanup2'])


klasa Test_TextTestRunner(unittest.TestCase):
    """Tests dla TextTestRunner."""

    def setUp(self):
        # clean the environment z pre-existing PYTHONWARNINGS to make
        # test_warnings results consistent
        self.pythonwarnings = os.environ.get('PYTHONWARNINGS')
        jeżeli self.pythonwarnings:
            usuń os.environ['PYTHONWARNINGS']

    def tearDown(self):
        # bring back pre-existing PYTHONWARNINGS jeżeli present
        jeżeli self.pythonwarnings:
            os.environ['PYTHONWARNINGS'] = self.pythonwarnings

    def test_init(self):
        runner = unittest.TextTestRunner()
        self.assertNieprawda(runner.failfast)
        self.assertNieprawda(runner.buffer)
        self.assertEqual(runner.verbosity, 1)
        self.assertEqual(runner.warnings, Nic)
        self.assertPrawda(runner.descriptions)
        self.assertEqual(runner.resultclass, unittest.TextTestResult)
        self.assertNieprawda(runner.tb_locals)

    def test_multiple_inheritance(self):
        klasa AResult(unittest.TestResult):
            def __init__(self, stream, descriptions, verbosity):
                super(AResult, self).__init__(stream, descriptions, verbosity)

        klasa ATextResult(unittest.TextTestResult, AResult):
            dalej

        # This used to podnieś an exception due to TextTestResult nie dalejing
        # on arguments w its __init__ super call
        ATextResult(Nic, Nic, 1)

    def testBufferAndFailfast(self):
        klasa Test(unittest.TestCase):
            def testFoo(self):
                dalej
        result = unittest.TestResult()
        runner = unittest.TextTestRunner(stream=io.StringIO(), failfast=Prawda,
                                         buffer=Prawda)
        # Use our result object
        runner._makeResult = lambda: result
        runner.run(Test('testFoo'))

        self.assertPrawda(result.failfast)
        self.assertPrawda(result.buffer)

    def test_locals(self):
        runner = unittest.TextTestRunner(stream=io.StringIO(), tb_locals=Prawda)
        result = runner.run(unittest.TestSuite())
        self.assertEqual(Prawda, result.tb_locals)

    def testRunnerRegistersResult(self):
        klasa Test(unittest.TestCase):
            def testFoo(self):
                dalej
        originalRegisterResult = unittest.runner.registerResult
        def cleanup():
            unittest.runner.registerResult = originalRegisterResult
        self.addCleanup(cleanup)

        result = unittest.TestResult()
        runner = unittest.TextTestRunner(stream=io.StringIO())
        # Use our result object
        runner._makeResult = lambda: result

        self.wasRegistered = 0
        def fakeRegisterResult(thisResult):
            self.wasRegistered += 1
            self.assertEqual(thisResult, result)
        unittest.runner.registerResult = fakeRegisterResult

        runner.run(unittest.TestSuite())
        self.assertEqual(self.wasRegistered, 1)

    def test_works_with_result_without_startTestRun_stopTestRun(self):
        klasa OldTextResult(ResultWithNoStartTestRunStopTestRun):
            separator2 = ''
            def printErrors(self):
                dalej

        klasa Runner(unittest.TextTestRunner):
            def __init__(self):
                super(Runner, self).__init__(io.StringIO())

            def _makeResult(self):
                zwróć OldTextResult()

        runner = Runner()
        runner.run(unittest.TestSuite())

    def test_startTestRun_stopTestRun_called(self):
        klasa LoggingTextResult(LoggingResult):
            separator2 = ''
            def printErrors(self):
                dalej

        klasa LoggingRunner(unittest.TextTestRunner):
            def __init__(self, events):
                super(LoggingRunner, self).__init__(io.StringIO())
                self._events = events

            def _makeResult(self):
                zwróć LoggingTextResult(self._events)

        events = []
        runner = LoggingRunner(events)
        runner.run(unittest.TestSuite())
        expected = ['startTestRun', 'stopTestRun']
        self.assertEqual(events, expected)

    def test_pickle_unpickle(self):
        # Issue #7197: a TextTestRunner should be (un)pickleable. This jest
        # required by test_multiprocessing under Windows (in verbose mode).
        stream = io.StringIO("foo")
        runner = unittest.TextTestRunner(stream)
        dla protocol w range(2, pickle.HIGHEST_PROTOCOL + 1):
            s = pickle.dumps(runner, protocol)
            obj = pickle.loads(s)
            # StringIO objects never compare equal, a cheap test instead.
            self.assertEqual(obj.stream.getvalue(), stream.getvalue())

    def test_resultclass(self):
        def MockResultClass(*args):
            zwróć args
        STREAM = object()
        DESCRIPTIONS = object()
        VERBOSITY = object()
        runner = unittest.TextTestRunner(STREAM, DESCRIPTIONS, VERBOSITY,
                                         resultclass=MockResultClass)
        self.assertEqual(runner.resultclass, MockResultClass)

        expectedresult = (runner.stream, DESCRIPTIONS, VERBOSITY)
        self.assertEqual(runner._makeResult(), expectedresult)

    def test_warnings(self):
        """
        Check that warnings argument of TextTestRunner correctly affects the
        behavior of the warnings.
        """
        # see #10535 oraz the _test_warnings file dla more information

        def get_parse_out_err(p):
            zwróć [b.splitlines() dla b w p.communicate()]
        opts = dict(stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    cwd=os.path.dirname(__file__))
        ae_msg = b'Please use assertEqual instead.'
        at_msg = b'Please use assertPrawda instead.'

        # no args -> all the warnings are printed, unittest warnings only once
        p = subprocess.Popen([sys.executable, '_test_warnings.py'], **opts)
        out, err = get_parse_out_err(p)
        self.assertIn(b'OK', err)
        # check that the total number of warnings w the output jest correct
        self.assertEqual(len(out), 12)
        # check that the numbers of the different kind of warnings jest correct
        dla msg w [b'dw', b'iw', b'uw']:
            self.assertEqual(out.count(msg), 3)
        dla msg w [ae_msg, at_msg, b'rw']:
            self.assertEqual(out.count(msg), 1)

        args_list = (
            # dalejing 'ignore' jako warnings arg -> no warnings
            [sys.executable, '_test_warnings.py', 'ignore'],
            # -W doesn't affect the result jeżeli the arg jest dalejed
            [sys.executable, '-Wa', '_test_warnings.py', 'ignore'],
            # -W affects the result jeżeli the arg jest nie dalejed
            [sys.executable, '-Wi', '_test_warnings.py']
        )
        # w all these cases no warnings are printed
        dla args w args_list:
            p = subprocess.Popen(args, **opts)
            out, err = get_parse_out_err(p)
            self.assertIn(b'OK', err)
            self.assertEqual(len(out), 0)


        # dalejing 'always' jako warnings arg -> all the warnings printed,
        #                                     unittest warnings only once
        p = subprocess.Popen([sys.executable, '_test_warnings.py', 'always'],
                             **opts)
        out, err = get_parse_out_err(p)
        self.assertIn(b'OK', err)
        self.assertEqual(len(out), 14)
        dla msg w [b'dw', b'iw', b'uw', b'rw']:
            self.assertEqual(out.count(msg), 3)
        dla msg w [ae_msg, at_msg]:
            self.assertEqual(out.count(msg), 1)

    def testStdErrLookedUpAtInstantiationTime(self):
        # see issue 10786
        old_stderr = sys.stderr
        f = io.StringIO()
        sys.stderr = f
        spróbuj:
            runner = unittest.TextTestRunner()
            self.assertPrawda(runner.stream.stream jest f)
        w_końcu:
            sys.stderr = old_stderr

    def testSpecifiedStreamUsed(self):
        # see issue 10786
        f = io.StringIO()
        runner = unittest.TextTestRunner(f)
        self.assertPrawda(runner.stream.stream jest f)


jeżeli __name__ == "__main__":
    unittest.main()
