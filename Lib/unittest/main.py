"""Unittest main program"""

zaimportuj sys
zaimportuj argparse
zaimportuj os

z . zaimportuj loader, runner
z .signals zaimportuj installHandler

__unittest = Prawda

MAIN_EXAMPLES = """\
Examples:
  %(prog)s test_module               - run tests z test_module
  %(prog)s module.TestClass          - run tests z module.TestClass
  %(prog)s module.Class.test_method  - run specified test method
"""

MODULE_EXAMPLES = """\
Examples:
  %(prog)s                           - run default set of tests
  %(prog)s MyTestSuite               - run suite 'MyTestSuite'
  %(prog)s MyTestCase.testSomething  - run MyTestCase.testSomething
  %(prog)s MyTestCase                - run all 'test*' test methods
                                       w MyTestCase
"""

def _convert_name(name):
    # on Linux / Mac OS X 'foo.PY' jest nie importable, but on
    # Windows it is. Simpler to do a case insensitive match
    # a better check would be to check that the name jest a
    # valid Python module name.
    jeżeli os.path.isfile(name) oraz name.lower().endswith('.py'):
        jeżeli os.path.isabs(name):
            rel_path = os.path.relpath(name, os.getcwd())
            jeżeli os.path.isabs(rel_path) albo rel_path.startswith(os.pardir):
                zwróć name
            name = rel_path
        # on Windows both '\' oraz '/' are used jako path
        # separators. Better to replace both than rely on os.path.sep
        zwróć name[:-3].replace('\\', '.').replace('/', '.')
    zwróć name

def _convert_names(names):
    zwróć [_convert_name(name) dla name w names]


klasa TestProgram(object):
    """A command-line program that runs a set of tests; this jest primarily
       dla making test modules conveniently executable.
    """
    # defaults dla testing
    module=Nic
    verbosity = 1
    failfast = catchbreak = buffer = progName = warnings = Nic
    _discovery_parser = Nic

    def __init__(self, module='__main__', defaultTest=Nic, argv=Nic,
                    testRunner=Nic, testLoader=loader.defaultTestLoader,
                    exit=Prawda, verbosity=1, failfast=Nic, catchbreak=Nic,
                    buffer=Nic, warnings=Nic, *, tb_locals=Nieprawda):
        jeżeli isinstance(module, str):
            self.module = __import__(module)
            dla part w module.split('.')[1:]:
                self.module = getattr(self.module, part)
        inaczej:
            self.module = module
        jeżeli argv jest Nic:
            argv = sys.argv

        self.exit = exit
        self.failfast = failfast
        self.catchbreak = catchbreak
        self.verbosity = verbosity
        self.buffer = buffer
        self.tb_locals = tb_locals
        jeżeli warnings jest Nic oraz nie sys.warnoptions:
            # even jeżeli DeprecationWarnings are ignored by default
            # print them anyway unless other warnings settings are
            # specified by the warnings arg albo the -W python flag
            self.warnings = 'default'
        inaczej:
            # here self.warnings jest set either to the value dalejed
            # to the warnings args albo to Nic.
            # If the user didn't dalej a value self.warnings will
            # be Nic. This means that the behavior jest unchanged
            # oraz depends on the values dalejed to -W.
            self.warnings = warnings
        self.defaultTest = defaultTest
        self.testRunner = testRunner
        self.testLoader = testLoader
        self.progName = os.path.basename(argv[0])
        self.parseArgs(argv)
        self.runTests()

    def usageExit(self, msg=Nic):
        jeżeli msg:
            print(msg)
        jeżeli self._discovery_parser jest Nic:
            self._initArgParsers()
        self._print_help()
        sys.exit(2)

    def _print_help(self, *args, **kwargs):
        jeżeli self.module jest Nic:
            print(self._main_parser.format_help())
            print(MAIN_EXAMPLES % {'prog': self.progName})
            self._discovery_parser.print_help()
        inaczej:
            print(self._main_parser.format_help())
            print(MODULE_EXAMPLES % {'prog': self.progName})

    def parseArgs(self, argv):
        self._initArgParsers()
        jeżeli self.module jest Nic:
            jeżeli len(argv) > 1 oraz argv[1].lower() == 'discover':
                self._do_discovery(argv[2:])
                zwróć
            self._main_parser.parse_args(argv[1:], self)
            jeżeli nie self.tests:
                # this allows "python -m unittest -v" to still work for
                # test discovery.
                self._do_discovery([])
                zwróć
        inaczej:
            self._main_parser.parse_args(argv[1:], self)

        jeżeli self.tests:
            self.testNames = _convert_names(self.tests)
            jeżeli __name__ == '__main__':
                # to support python -m unittest ...
                self.module = Nic
        albo_inaczej self.defaultTest jest Nic:
            # createTests will load tests z self.module
            self.testNames = Nic
        albo_inaczej isinstance(self.defaultTest, str):
            self.testNames = (self.defaultTest,)
        inaczej:
            self.testNames = list(self.defaultTest)
        self.createTests()

    def createTests(self):
        jeżeli self.testNames jest Nic:
            self.test = self.testLoader.loadTestsFromModule(self.module)
        inaczej:
            self.test = self.testLoader.loadTestsFromNames(self.testNames,
                                                           self.module)

    def _initArgParsers(self):
        parent_parser = self._getParentArgParser()
        self._main_parser = self._getMainArgParser(parent_parser)
        self._discovery_parser = self._getDiscoveryArgParser(parent_parser)

    def _getParentArgParser(self):
        parser = argparse.ArgumentParser(add_help=Nieprawda)

        parser.add_argument('-v', '--verbose', dest='verbosity',
                            action='store_const', const=2,
                            help='Verbose output')
        parser.add_argument('-q', '--quiet', dest='verbosity',
                            action='store_const', const=0,
                            help='Quiet output')
        parser.add_argument('--locals', dest='tb_locals',
                            action='store_true',
                            help='Show local variables w tracebacks')
        jeżeli self.failfast jest Nic:
            parser.add_argument('-f', '--failfast', dest='failfast',
                                action='store_true',
                                help='Stop on first fail albo error')
            self.failfast = Nieprawda
        jeżeli self.catchbreak jest Nic:
            parser.add_argument('-c', '--catch', dest='catchbreak',
                                action='store_true',
                                help='Catch ctrl-C oraz display results so far')
            self.catchbreak = Nieprawda
        jeżeli self.buffer jest Nic:
            parser.add_argument('-b', '--buffer', dest='buffer',
                                action='store_true',
                                help='Buffer stdout oraz stderr during tests')
            self.buffer = Nieprawda

        zwróć parser

    def _getMainArgParser(self, parent):
        parser = argparse.ArgumentParser(parents=[parent])
        parser.prog = self.progName
        parser.print_help = self._print_help

        parser.add_argument('tests', nargs='*',
                            help='a list of any number of test modules, '
                            'classes oraz test methods.')

        zwróć parser

    def _getDiscoveryArgParser(self, parent):
        parser = argparse.ArgumentParser(parents=[parent])
        parser.prog = '%s discover' % self.progName
        parser.epilog = ('For test discovery all test modules must be '
                         'importable z the top level directory of the '
                         'project.')

        parser.add_argument('-s', '--start-directory', dest='start',
                            help="Directory to start discovery ('.' default)")
        parser.add_argument('-p', '--pattern', dest='pattern',
                            help="Pattern to match tests ('test*.py' default)")
        parser.add_argument('-t', '--top-level-directory', dest='top',
                            help='Top level directory of project (defaults to '
                                 'start directory)')
        dla arg w ('start', 'pattern', 'top'):
            parser.add_argument(arg, nargs='?',
                                default=argparse.SUPPRESS,
                                help=argparse.SUPPRESS)

        zwróć parser

    def _do_discovery(self, argv, Loader=Nic):
        self.start = '.'
        self.pattern = 'test*.py'
        self.top = Nic
        jeżeli argv jest nie Nic:
            # handle command line args dla test discovery
            jeżeli self._discovery_parser jest Nic:
                # dla testing
                self._initArgParsers()
            self._discovery_parser.parse_args(argv, self)

        loader = self.testLoader jeżeli Loader jest Nic inaczej Loader()
        self.test = loader.discover(self.start, self.pattern, self.top)

    def runTests(self):
        jeżeli self.catchbreak:
            installHandler()
        jeżeli self.testRunner jest Nic:
            self.testRunner = runner.TextTestRunner
        jeżeli isinstance(self.testRunner, type):
            spróbuj:
                spróbuj:
                    testRunner = self.testRunner(verbosity=self.verbosity,
                                                 failfast=self.failfast,
                                                 buffer=self.buffer,
                                                 warnings=self.warnings,
                                                 tb_locals=self.tb_locals)
                wyjąwszy TypeError:
                    # didn't accept the tb_locals argument
                    testRunner = self.testRunner(verbosity=self.verbosity,
                                                 failfast=self.failfast,
                                                 buffer=self.buffer,
                                                 warnings=self.warnings)
            wyjąwszy TypeError:
                # didn't accept the verbosity, buffer albo failfast arguments
                testRunner = self.testRunner()
        inaczej:
            # it jest assumed to be a TestRunner instance
            testRunner = self.testRunner
        self.result = testRunner.run(self.test)
        jeżeli self.exit:
            sys.exit(nie self.result.wasSuccessful())

main = TestProgram
