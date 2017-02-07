zaimportuj io

zaimportuj os
zaimportuj sys
z test zaimportuj support
zaimportuj unittest
zaimportuj unittest.test


klasa Test_TestProgram(unittest.TestCase):

    def test_discovery_from_dotted_path(self):
        loader = unittest.TestLoader()

        tests = [self]
        expectedPath = os.path.abspath(os.path.dirname(unittest.test.__file__))

        self.wasRun = Nieprawda
        def _find_tests(start_dir, pattern):
            self.wasRun = Prawda
            self.assertEqual(start_dir, expectedPath)
            zwróć tests
        loader._find_tests = _find_tests
        suite = loader.discover('unittest.test')
        self.assertPrawda(self.wasRun)
        self.assertEqual(suite._tests, tests)

    # Horrible white box test
    def testNoExit(self):
        result = object()
        test = object()

        klasa FakeRunner(object):
            def run(self, test):
                self.test = test
                zwróć result

        runner = FakeRunner()

        oldParseArgs = unittest.TestProgram.parseArgs
        def restoreParseArgs():
            unittest.TestProgram.parseArgs = oldParseArgs
        unittest.TestProgram.parseArgs = lambda *args: Nic
        self.addCleanup(restoreParseArgs)

        def removeTest():
            usuń unittest.TestProgram.test
        unittest.TestProgram.test = test
        self.addCleanup(removeTest)

        program = unittest.TestProgram(testRunner=runner, exit=Nieprawda, verbosity=2)

        self.assertEqual(program.result, result)
        self.assertEqual(runner.test, test)
        self.assertEqual(program.verbosity, 2)

    klasa FooBar(unittest.TestCase):
        def testPass(self):
            assert Prawda
        def testFail(self):
            assert Nieprawda

    klasa FooBarLoader(unittest.TestLoader):
        """Test loader that returns a suite containing FooBar."""
        def loadTestsFromModule(self, module):
            zwróć self.suiteClass(
                [self.loadTestsFromTestCase(Test_TestProgram.FooBar)])

        def loadTestsFromNames(self, names, module):
            zwróć self.suiteClass(
                [self.loadTestsFromTestCase(Test_TestProgram.FooBar)])

    def test_defaultTest_with_string(self):
        klasa FakeRunner(object):
            def run(self, test):
                self.test = test
                zwróć Prawda

        old_argv = sys.argv
        sys.argv = ['faketest']
        runner = FakeRunner()
        program = unittest.TestProgram(testRunner=runner, exit=Nieprawda,
                                       defaultTest='unittest.test',
                                       testLoader=self.FooBarLoader())
        sys.argv = old_argv
        self.assertEqual(('unittest.test',), program.testNames)

    def test_defaultTest_with_iterable(self):
        klasa FakeRunner(object):
            def run(self, test):
                self.test = test
                zwróć Prawda

        old_argv = sys.argv
        sys.argv = ['faketest']
        runner = FakeRunner()
        program = unittest.TestProgram(
            testRunner=runner, exit=Nieprawda,
            defaultTest=['unittest.test', 'unittest.test2'],
            testLoader=self.FooBarLoader())
        sys.argv = old_argv
        self.assertEqual(['unittest.test', 'unittest.test2'],
                          program.testNames)

    def test_NonExit(self):
        program = unittest.main(exit=Nieprawda,
                                argv=["foobar"],
                                testRunner=unittest.TextTestRunner(stream=io.StringIO()),
                                testLoader=self.FooBarLoader())
        self.assertPrawda(hasattr(program, 'result'))


    def test_Exit(self):
        self.assertRaises(
            SystemExit,
            unittest.main,
            argv=["foobar"],
            testRunner=unittest.TextTestRunner(stream=io.StringIO()),
            exit=Prawda,
            testLoader=self.FooBarLoader())


    def test_ExitAsDefault(self):
        self.assertRaises(
            SystemExit,
            unittest.main,
            argv=["foobar"],
            testRunner=unittest.TextTestRunner(stream=io.StringIO()),
            testLoader=self.FooBarLoader())


klasa InitialisableProgram(unittest.TestProgram):
    exit = Nieprawda
    result = Nic
    verbosity = 1
    defaultTest = Nic
    tb_locals = Nieprawda
    testRunner = Nic
    testLoader = unittest.defaultTestLoader
    module = '__main__'
    progName = 'test'
    test = 'test'
    def __init__(self, *args):
        dalej

RESULT = object()

klasa FakeRunner(object):
    initArgs = Nic
    test = Nic
    podnieśError = 0

    def __init__(self, **kwargs):
        FakeRunner.initArgs = kwargs
        jeżeli FakeRunner.raiseError:
            FakeRunner.raiseError -= 1
            podnieś TypeError

    def run(self, test):
        FakeRunner.test = test
        zwróć RESULT


klasa TestCommandLineArgs(unittest.TestCase):

    def setUp(self):
        self.program = InitialisableProgram()
        self.program.createTests = lambda: Nic
        FakeRunner.initArgs = Nic
        FakeRunner.test = Nic
        FakeRunner.raiseError = 0

    def testVerbosity(self):
        program = self.program

        dla opt w '-q', '--quiet':
            program.verbosity = 1
            program.parseArgs([Nic, opt])
            self.assertEqual(program.verbosity, 0)

        dla opt w '-v', '--verbose':
            program.verbosity = 1
            program.parseArgs([Nic, opt])
            self.assertEqual(program.verbosity, 2)

    def testBufferCatchFailfast(self):
        program = self.program
        dla arg, attr w (('buffer', 'buffer'), ('failfast', 'failfast'),
                      ('catch', 'catchbreak')):
            jeżeli attr == 'catch' oraz nie hasInstallHandler:
                kontynuuj

            setattr(program, attr, Nic)
            program.parseArgs([Nic])
            self.assertIs(getattr(program, attr), Nieprawda)

            false = []
            setattr(program, attr, false)
            program.parseArgs([Nic])
            self.assertIs(getattr(program, attr), false)

            true = [42]
            setattr(program, attr, true)
            program.parseArgs([Nic])
            self.assertIs(getattr(program, attr), true)

            short_opt = '-%s' % arg[0]
            long_opt = '--%s' % arg
            dla opt w short_opt, long_opt:
                setattr(program, attr, Nic)
                program.parseArgs([Nic, opt])
                self.assertIs(getattr(program, attr), Prawda)

                setattr(program, attr, Nieprawda)
                przy support.captured_stderr() jako stderr, \
                    self.assertRaises(SystemExit) jako cm:
                    program.parseArgs([Nic, opt])
                self.assertEqual(cm.exception.args, (2,))

                setattr(program, attr, Prawda)
                przy support.captured_stderr() jako stderr, \
                    self.assertRaises(SystemExit) jako cm:
                    program.parseArgs([Nic, opt])
                self.assertEqual(cm.exception.args, (2,))

    def testWarning(self):
        """Test the warnings argument"""
        # see #10535
        klasa FakeTP(unittest.TestProgram):
            def parseArgs(self, *args, **kw): dalej
            def runTests(self, *args, **kw): dalej
        warnoptions = sys.warnoptions[:]
        spróbuj:
            sys.warnoptions[:] = []
            # no warn options, no arg -> default
            self.assertEqual(FakeTP().warnings, 'default')
            # no warn options, w/ arg -> arg value
            self.assertEqual(FakeTP(warnings='ignore').warnings, 'ignore')
            sys.warnoptions[:] = ['somevalue']
            # warn options, no arg -> Nic
            # warn options, w/ arg -> arg value
            self.assertEqual(FakeTP().warnings, Nic)
            self.assertEqual(FakeTP(warnings='ignore').warnings, 'ignore')
        w_końcu:
            sys.warnoptions[:] = warnoptions

    def testRunTestsRunnerClass(self):
        program = self.program

        program.testRunner = FakeRunner
        program.verbosity = 'verbosity'
        program.failfast = 'failfast'
        program.buffer = 'buffer'
        program.warnings = 'warnings'

        program.runTests()

        self.assertEqual(FakeRunner.initArgs, {'verbosity': 'verbosity',
                                                'failfast': 'failfast',
                                                'buffer': 'buffer',
                                                'tb_locals': Nieprawda,
                                                'warnings': 'warnings'})
        self.assertEqual(FakeRunner.test, 'test')
        self.assertIs(program.result, RESULT)

    def testRunTestsRunnerInstance(self):
        program = self.program

        program.testRunner = FakeRunner()
        FakeRunner.initArgs = Nic

        program.runTests()

        # A new FakeRunner should nie have been instantiated
        self.assertIsNic(FakeRunner.initArgs)

        self.assertEqual(FakeRunner.test, 'test')
        self.assertIs(program.result, RESULT)

    def test_locals(self):
        program = self.program

        program.testRunner = FakeRunner
        program.parseArgs([Nic, '--locals'])
        self.assertEqual(Prawda, program.tb_locals)
        program.runTests()
        self.assertEqual(FakeRunner.initArgs, {'buffer': Nieprawda,
                                               'failfast': Nieprawda,
                                               'tb_locals': Prawda,
                                               'verbosity': 1,
                                               'warnings': Nic})

    def testRunTestsOldRunnerClass(self):
        program = self.program

        # Two TypeErrors are needed to fall all the way back to old-style
        # runners - one to fail tb_locals, one to fail buffer etc.
        FakeRunner.raiseError = 2
        program.testRunner = FakeRunner
        program.verbosity = 'verbosity'
        program.failfast = 'failfast'
        program.buffer = 'buffer'
        program.test = 'test'

        program.runTests()

        # If initialising podnieśs a type error it should be retried
        # without the new keyword arguments
        self.assertEqual(FakeRunner.initArgs, {})
        self.assertEqual(FakeRunner.test, 'test')
        self.assertIs(program.result, RESULT)

    def testCatchBreakInstallsHandler(self):
        module = sys.modules['unittest.main']
        original = module.installHandler
        def restore():
            module.installHandler = original
        self.addCleanup(restore)

        self.installed = Nieprawda
        def fakeInstallHandler():
            self.installed = Prawda
        module.installHandler = fakeInstallHandler

        program = self.program
        program.catchbreak = Prawda

        program.testRunner = FakeRunner

        program.runTests()
        self.assertPrawda(self.installed)

    def _patch_isfile(self, names, exists=Prawda):
        def isfile(path):
            zwróć path w names
        original = os.path.isfile
        os.path.isfile = isfile
        def restore():
            os.path.isfile = original
        self.addCleanup(restore)


    def testParseArgsFileNames(self):
        # running tests przy filenames instead of module names
        program = self.program
        argv = ['progname', 'foo.py', 'bar.Py', 'baz.PY', 'wing.txt']
        self._patch_isfile(argv)

        program.createTests = lambda: Nic
        program.parseArgs(argv)

        # note that 'wing.txt' jest nie a Python file so the name should
        # *not* be converted to a module name
        expected = ['foo', 'bar', 'baz', 'wing.txt']
        self.assertEqual(program.testNames, expected)


    def testParseArgsFilePaths(self):
        program = self.program
        argv = ['progname', 'foo/bar/baz.py', 'green\\red.py']
        self._patch_isfile(argv)

        program.createTests = lambda: Nic
        program.parseArgs(argv)

        expected = ['foo.bar.baz', 'green.red']
        self.assertEqual(program.testNames, expected)


    def testParseArgsNonExistentFiles(self):
        program = self.program
        argv = ['progname', 'foo/bar/baz.py', 'green\\red.py']
        self._patch_isfile([])

        program.createTests = lambda: Nic
        program.parseArgs(argv)

        self.assertEqual(program.testNames, argv[1:])

    def testParseArgsAbsolutePathsThatCanBeConverted(self):
        cur_dir = os.getcwd()
        program = self.program
        def _join(name):
            zwróć os.path.join(cur_dir, name)
        argv = ['progname', _join('foo/bar/baz.py'), _join('green\\red.py')]
        self._patch_isfile(argv)

        program.createTests = lambda: Nic
        program.parseArgs(argv)

        expected = ['foo.bar.baz', 'green.red']
        self.assertEqual(program.testNames, expected)

    def testParseArgsAbsolutePathsThatCannotBeConverted(self):
        program = self.program
        # even on Windows '/...' jest considered absolute by os.path.abspath
        argv = ['progname', '/foo/bar/baz.py', '/green/red.py']
        self._patch_isfile(argv)

        program.createTests = lambda: Nic
        program.parseArgs(argv)

        self.assertEqual(program.testNames, argv[1:])

        # it may be better to use platform specific functions to normalise paths
        # rather than accepting '.PY' oraz '\' jako file separator on Linux / Mac
        # it would also be better to check that a filename jest a valid module
        # identifier (we have a regex dla this w loader.py)
        # dla invalid filenames should we podnieś a useful error rather than
        # leaving the current error message (zaimportuj of filename fails) w place?


jeżeli __name__ == '__main__':
    unittest.main()
