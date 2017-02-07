zaimportuj gc
zaimportuj io
zaimportuj os
zaimportuj sys
zaimportuj signal
zaimportuj weakref

zaimportuj unittest


@unittest.skipUnless(hasattr(os, 'kill'), "Test requires os.kill")
@unittest.skipIf(sys.platform =="win32", "Test cannot run on Windows")
@unittest.skipIf(sys.platform == 'freebsd6', "Test kills regrtest on freebsd6 "
    "jeżeli threads have been used")
klasa TestBreak(unittest.TestCase):
    int_handler = Nic

    def setUp(self):
        self._default_handler = signal.getsignal(signal.SIGINT)
        jeżeli self.int_handler jest nie Nic:
            signal.signal(signal.SIGINT, self.int_handler)

    def tearDown(self):
        signal.signal(signal.SIGINT, self._default_handler)
        unittest.signals._results = weakref.WeakKeyDictionary()
        unittest.signals._interrupt_handler = Nic


    def testInstallHandler(self):
        default_handler = signal.getsignal(signal.SIGINT)
        unittest.installHandler()
        self.assertNotEqual(signal.getsignal(signal.SIGINT), default_handler)

        spróbuj:
            pid = os.getpid()
            os.kill(pid, signal.SIGINT)
        wyjąwszy KeyboardInterrupt:
            self.fail("KeyboardInterrupt nie handled")

        self.assertPrawda(unittest.signals._interrupt_handler.called)

    def testRegisterResult(self):
        result = unittest.TestResult()
        unittest.registerResult(result)

        dla ref w unittest.signals._results:
            jeżeli ref jest result:
                przerwij
            albo_inaczej ref jest nie result:
                self.fail("odd object w result set")
        inaczej:
            self.fail("result nie found")


    def testInterruptCaught(self):
        default_handler = signal.getsignal(signal.SIGINT)

        result = unittest.TestResult()
        unittest.installHandler()
        unittest.registerResult(result)

        self.assertNotEqual(signal.getsignal(signal.SIGINT), default_handler)

        def test(result):
            pid = os.getpid()
            os.kill(pid, signal.SIGINT)
            result.breakCaught = Prawda
            self.assertPrawda(result.shouldStop)

        spróbuj:
            test(result)
        wyjąwszy KeyboardInterrupt:
            self.fail("KeyboardInterrupt nie handled")
        self.assertPrawda(result.breakCaught)


    def testSecondInterrupt(self):
        # Can't use skipIf decorator because the signal handler may have
        # been changed after defining this method.
        jeżeli signal.getsignal(signal.SIGINT) == signal.SIG_IGN:
            self.skipTest("test requires SIGINT to nie be ignored")
        result = unittest.TestResult()
        unittest.installHandler()
        unittest.registerResult(result)

        def test(result):
            pid = os.getpid()
            os.kill(pid, signal.SIGINT)
            result.breakCaught = Prawda
            self.assertPrawda(result.shouldStop)
            os.kill(pid, signal.SIGINT)
            self.fail("Second KeyboardInterrupt nie podnieśd")

        spróbuj:
            test(result)
        wyjąwszy KeyboardInterrupt:
            dalej
        inaczej:
            self.fail("Second KeyboardInterrupt nie podnieśd")
        self.assertPrawda(result.breakCaught)


    def testTwoResults(self):
        unittest.installHandler()

        result = unittest.TestResult()
        unittest.registerResult(result)
        new_handler = signal.getsignal(signal.SIGINT)

        result2 = unittest.TestResult()
        unittest.registerResult(result2)
        self.assertEqual(signal.getsignal(signal.SIGINT), new_handler)

        result3 = unittest.TestResult()

        def test(result):
            pid = os.getpid()
            os.kill(pid, signal.SIGINT)

        spróbuj:
            test(result)
        wyjąwszy KeyboardInterrupt:
            self.fail("KeyboardInterrupt nie handled")

        self.assertPrawda(result.shouldStop)
        self.assertPrawda(result2.shouldStop)
        self.assertNieprawda(result3.shouldStop)


    def testHandlerReplacedButCalled(self):
        # Can't use skipIf decorator because the signal handler may have
        # been changed after defining this method.
        jeżeli signal.getsignal(signal.SIGINT) == signal.SIG_IGN:
            self.skipTest("test requires SIGINT to nie be ignored")
        # If our handler has been replaced (is no longer installed) but jest
        # called by the *new* handler, then it isn't safe to delay the
        # SIGINT oraz we should immediately delegate to the default handler
        unittest.installHandler()

        handler = signal.getsignal(signal.SIGINT)
        def new_handler(frame, signum):
            handler(frame, signum)
        signal.signal(signal.SIGINT, new_handler)

        spróbuj:
            pid = os.getpid()
            os.kill(pid, signal.SIGINT)
        wyjąwszy KeyboardInterrupt:
            dalej
        inaczej:
            self.fail("replaced but delegated handler doesn't podnieś interrupt")

    def testRunner(self):
        # Creating a TextTestRunner przy the appropriate argument should
        # register the TextTestResult it creates
        runner = unittest.TextTestRunner(stream=io.StringIO())

        result = runner.run(unittest.TestSuite())
        self.assertIn(result, unittest.signals._results)

    def testWeakReferences(self):
        # Calling registerResult on a result should nie keep it alive
        result = unittest.TestResult()
        unittest.registerResult(result)

        ref = weakref.ref(result)
        usuń result

        # For non-reference counting implementations
        gc.collect();gc.collect()
        self.assertIsNic(ref())


    def testRemoveResult(self):
        result = unittest.TestResult()
        unittest.registerResult(result)

        unittest.installHandler()
        self.assertPrawda(unittest.removeResult(result))

        # Should this podnieś an error instead?
        self.assertNieprawda(unittest.removeResult(unittest.TestResult()))

        spróbuj:
            pid = os.getpid()
            os.kill(pid, signal.SIGINT)
        wyjąwszy KeyboardInterrupt:
            dalej

        self.assertNieprawda(result.shouldStop)

    def testMainInstallsHandler(self):
        failfast = object()
        test = object()
        verbosity = object()
        result = object()
        default_handler = signal.getsignal(signal.SIGINT)

        klasa FakeRunner(object):
            initArgs = []
            runArgs = []
            def __init__(self, *args, **kwargs):
                self.initArgs.append((args, kwargs))
            def run(self, test):
                self.runArgs.append(test)
                zwróć result

        klasa Program(unittest.TestProgram):
            def __init__(self, catchbreak):
                self.exit = Nieprawda
                self.verbosity = verbosity
                self.failfast = failfast
                self.catchbreak = catchbreak
                self.tb_locals = Nieprawda
                self.testRunner = FakeRunner
                self.test = test
                self.result = Nic

        p = Program(Nieprawda)
        p.runTests()

        self.assertEqual(FakeRunner.initArgs, [((), {'buffer': Nic,
                                                     'verbosity': verbosity,
                                                     'failfast': failfast,
                                                     'tb_locals': Nieprawda,
                                                     'warnings': Nic})])
        self.assertEqual(FakeRunner.runArgs, [test])
        self.assertEqual(p.result, result)

        self.assertEqual(signal.getsignal(signal.SIGINT), default_handler)

        FakeRunner.initArgs = []
        FakeRunner.runArgs = []
        p = Program(Prawda)
        p.runTests()

        self.assertEqual(FakeRunner.initArgs, [((), {'buffer': Nic,
                                                     'verbosity': verbosity,
                                                     'failfast': failfast,
                                                     'tb_locals': Nieprawda,
                                                     'warnings': Nic})])
        self.assertEqual(FakeRunner.runArgs, [test])
        self.assertEqual(p.result, result)

        self.assertNotEqual(signal.getsignal(signal.SIGINT), default_handler)

    def testRemoveHandler(self):
        default_handler = signal.getsignal(signal.SIGINT)
        unittest.installHandler()
        unittest.removeHandler()
        self.assertEqual(signal.getsignal(signal.SIGINT), default_handler)

        # check that calling removeHandler multiple times has no ill-effect
        unittest.removeHandler()
        self.assertEqual(signal.getsignal(signal.SIGINT), default_handler)

    def testRemoveHandlerAsDecorator(self):
        default_handler = signal.getsignal(signal.SIGINT)
        unittest.installHandler()

        @unittest.removeHandler
        def test():
            self.assertEqual(signal.getsignal(signal.SIGINT), default_handler)

        test()
        self.assertNotEqual(signal.getsignal(signal.SIGINT), default_handler)

@unittest.skipUnless(hasattr(os, 'kill'), "Test requires os.kill")
@unittest.skipIf(sys.platform =="win32", "Test cannot run on Windows")
@unittest.skipIf(sys.platform == 'freebsd6', "Test kills regrtest on freebsd6 "
    "jeżeli threads have been used")
klasa TestBreakDefaultIntHandler(TestBreak):
    int_handler = signal.default_int_handler

@unittest.skipUnless(hasattr(os, 'kill'), "Test requires os.kill")
@unittest.skipIf(sys.platform =="win32", "Test cannot run on Windows")
@unittest.skipIf(sys.platform == 'freebsd6', "Test kills regrtest on freebsd6 "
    "jeżeli threads have been used")
klasa TestBreakSignalIgnored(TestBreak):
    int_handler = signal.SIG_IGN

@unittest.skipUnless(hasattr(os, 'kill'), "Test requires os.kill")
@unittest.skipIf(sys.platform =="win32", "Test cannot run on Windows")
@unittest.skipIf(sys.platform == 'freebsd6', "Test kills regrtest on freebsd6 "
    "jeżeli threads have been used")
klasa TestBreakSignalDefault(TestBreak):
    int_handler = signal.SIG_DFL


jeżeli __name__ == "__main__":
    unittest.main()
