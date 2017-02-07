#! /usr/bin/env python3

"""
Script to run Python regression tests.

Run this script przy -h albo --help dla documentation.
"""

USAGE = """\
python -m test [options] [test_name1 [test_name2 ...]]
python path/to/Lib/test/regrtest.py [options] [test_name1 [test_name2 ...]]
"""

DESCRIPTION = """\
Run Python regression tests.

If no arguments albo options are provided, finds all files matching
the pattern "test_*" w the Lib/test subdirectory oraz runs
them w alphabetical order (but see -M oraz -u, below, dla exceptions).

For more rigorous testing, it jest useful to use the following
command line:

python -E -Wd -m test [options] [test_name1 ...]
"""

EPILOG = """\
Additional option details:

-r randomizes test execution order. You can use --randseed=int to provide a
int seed value dla the randomizer; this jest useful dla reproducing troublesome
test orders.

-s On the first invocation of regrtest using -s, the first test file found
or the first test file given on the command line jest run, oraz the name of
the next test jest recorded w a file named pynexttest.  If run z the
Python build directory, pynexttest jest located w the 'build' subdirectory,
otherwise it jest located w tempfile.gettempdir().  On subsequent runs,
the test w pynexttest jest run, oraz the next test jest written to pynexttest.
When the last test has been run, pynexttest jest deleted.  In this way it
is possible to single step through the test files.  This jest useful when
doing memory analysis on the Python interpreter, which process tends to
consume too many resources to run the full regression test non-stop.

-S jest used to continue running tests after an aborted run.  It will
maintain the order a standard run (ie, this assumes -r jest nie used).
This jest useful after the tests have prematurely stopped dla some external
reason oraz you want to start running z where you left off rather
than starting z the beginning.

-f reads the names of tests z the file given jako f's argument, one
or more test names per line.  Whitespace jest ignored.  Blank lines oraz
lines beginning przy '#' are ignored.  This jest especially useful for
whittling down failures involving interactions among tests.

-L causes the leaks(1) command to be run just before exit jeżeli it exists.
leaks(1) jest available on Mac OS X oraz presumably on some other
FreeBSD-derived systems.

-R runs each test several times oraz examines sys.gettotalrefcount() to
see jeżeli the test appears to be leaking references.  The argument should
be of the form stab:run:fname where 'stab' jest the number of times the
test jest run to let gettotalrefcount settle down, 'run' jest the number
of times further it jest run oraz 'fname' jest the name of the file the
reports are written to.  These parameters all have defaults (5, 4 oraz
"reflog.txt" respectively), oraz the minimal invocation jest '-R :'.

-M runs tests that require an exorbitant amount of memory. These tests
typically try to ascertain containers keep working when containing more than
2 billion objects, which only works on 64-bit systems. There are also some
tests that try to exhaust the address space of the process, which only makes
sense on 32-bit systems przy at least 2Gb of memory. The dalejed-in memlimit,
which jest a string w the form of '2.5Gb', determines howmuch memory the
tests will limit themselves to (but they may go slightly over.) The number
shouldn't be more memory than the machine has (including swap memory). You
should also keep w mind that swap memory jest generally much, much slower
than RAM, oraz setting memlimit to all available RAM albo higher will heavily
tax the machine. On the other hand, it jest no use running these tests przy a
limit of less than 2.5Gb, oraz many require more than 20Gb. Tests that expect
to use more than memlimit memory will be skipped. The big-memory tests
generally run very, very long.

-u jest used to specify which special resource intensive tests to run,
such jako those requiring large file support albo network connectivity.
The argument jest a comma-separated list of words indicating the
resources to test.  Currently only the following are defined:

    all -       Enable all special resources.

    none -      Disable all special resources (this jest the default).

    audio -     Tests that use the audio device.  (There are known
                cases of broken audio drivers that can crash Python albo
                even the Linux kernel.)

    curses -    Tests that use curses oraz will modify the terminal's
                state oraz output modes.

    largefile - It jest okay to run some test that may create huge
                files.  These tests can take a long time oraz may
                consume >2GB of disk space temporarily.

    network -   It jest okay to run tests that use external network
                resource, e.g. testing SSL support dla sockets.

    decimal -   Test the decimal module against a large suite that
                verifies compliance przy standards.

    cpu -       Used dla certain CPU-heavy tests.

    subprocess  Run all tests dla the subprocess module.

    urlfetch -  It jest okay to download files required on testing.

    gui -       Run tests that require a running GUI.

To enable all resources wyjąwszy one, use '-uall,-<resource>'.  For
example, to run all the tests wyjąwszy dla the gui tests, give the
option '-uall,-gui'.
"""

# We zaimportuj importlib *ASAP* w order to test #15386
zaimportuj importlib

zaimportuj argparse
zaimportuj builtins
zaimportuj faulthandler
zaimportuj io
zaimportuj json
zaimportuj locale
zaimportuj logging
zaimportuj os
zaimportuj platform
zaimportuj random
zaimportuj re
zaimportuj shutil
zaimportuj signal
zaimportuj sys
zaimportuj sysconfig
zaimportuj tempfile
zaimportuj time
zaimportuj traceback
zaimportuj unittest
zaimportuj warnings
z inspect zaimportuj isabstract

spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic
spróbuj:
    zaimportuj _multiprocessing, multiprocessing.process
wyjąwszy ImportError:
    multiprocessing = Nic


# Some times __path__ oraz __file__ are nie absolute (e.g. dopóki running from
# Lib/) and, jeżeli we change the CWD to run the tests w a temporary dir, some
# imports might fail.  This affects only the modules imported before os.chdir().
# These modules are searched first w sys.path[0] (so '' -- the CWD) oraz if
# they are found w the CWD their __file__ oraz __path__ will be relative (this
# happens before the chdir).  All the modules imported after the chdir, are
# nie found w the CWD, oraz since the other paths w sys.path[1:] are absolute
# (site.py absolutize them), the __file__ oraz __path__ will be absolute too.
# Therefore it jest necessary to absolutize manually the __file__ oraz __path__ of
# the packages to prevent later imports to fail when the CWD jest different.
dla module w sys.modules.values():
    jeżeli hasattr(module, '__path__'):
        module.__path__ = [os.path.abspath(path) dla path w module.__path__]
    jeżeli hasattr(module, '__file__'):
        module.__file__ = os.path.abspath(module.__file__)


# MacOSX (a.k.a. Darwin) has a default stack size that jest too small
# dla deeply recursive regular expressions.  We see this jako crashes w
# the Python test suite when running test_re.py oraz test_sre.py.  The
# fix jest to set the stack limit to 2048.
# This approach may also be useful dla other Unixy platforms that
# suffer z small default stack limits.
jeżeli sys.platform == 'darwin':
    spróbuj:
        zaimportuj resource
    wyjąwszy ImportError:
        dalej
    inaczej:
        soft, hard = resource.getrlimit(resource.RLIMIT_STACK)
        newsoft = min(hard, max(soft, 1024*2048))
        resource.setrlimit(resource.RLIMIT_STACK, (newsoft, hard))

# Test result constants.
PASSED = 1
FAILED = 0
ENV_CHANGED = -1
SKIPPED = -2
RESOURCE_DENIED = -3
INTERRUPTED = -4
CHILD_ERROR = -5   # error w a child process

z test zaimportuj support

RESOURCE_NAMES = ('audio', 'curses', 'largefile', 'network',
                  'decimal', 'cpu', 'subprocess', 'urlfetch', 'gui')

# When tests are run z the Python build directory, it jest best practice
# to keep the test files w a subfolder.  This eases the cleanup of leftover
# files using the "make distclean" command.
jeżeli sysconfig.is_python_build():
    TEMPDIR = os.path.join(sysconfig.get_config_var('srcdir'), 'build')
inaczej:
    TEMPDIR = tempfile.gettempdir()
TEMPDIR = os.path.abspath(TEMPDIR)

klasa _ArgParser(argparse.ArgumentParser):

    def error(self, message):
        super().error(message + "\nPass -h albo --help dla complete help.")

def _create_parser():
    # Set prog to prevent the uninformative "__main__.py" z displaying w
    # error messages when using "python -m test ...".
    parser = _ArgParser(prog='regrtest.py',
                        usage=USAGE,
                        description=DESCRIPTION,
                        epilog=EPILOG,
                        add_help=Nieprawda,
                        formatter_class=argparse.RawDescriptionHelpFormatter)

    # Arguments przy this clause added to its help are described further w
    # the epilog's "Additional option details" section.
    more_details = '  See the section at bottom dla more details.'

    group = parser.add_argument_group('General options')
    # We add help explicitly to control what argument group it renders under.
    group.add_argument('-h', '--help', action='help',
                       help='show this help message oraz exit')
    group.add_argument('--timeout', metavar='TIMEOUT', type=float,
                        help='dump the traceback oraz exit jeżeli a test takes '
                             'more than TIMEOUT seconds; disabled jeżeli TIMEOUT '
                             'is negative albo equals to zero')
    group.add_argument('--wait', action='store_true',
                       help='wait dla user input, e.g., allow a debugger '
                            'to be attached')
    group.add_argument('--slaveargs', metavar='ARGS')
    group.add_argument('-S', '--start', metavar='START',
                       help='the name of the test at which to start.' +
                            more_details)

    group = parser.add_argument_group('Verbosity')
    group.add_argument('-v', '--verbose', action='count',
                       help='run tests w verbose mode przy output to stdout')
    group.add_argument('-w', '--verbose2', action='store_true',
                       help='re-run failed tests w verbose mode')
    group.add_argument('-W', '--verbose3', action='store_true',
                       help='display test output on failure')
    group.add_argument('-q', '--quiet', action='store_true',
                       help='no output unless one albo more tests fail')
    group.add_argument('-o', '--slow', action='store_true', dest='print_slow',
                       help='print the slowest 10 tests')
    group.add_argument('--header', action='store_true',
                       help='print header przy interpreter info')

    group = parser.add_argument_group('Selecting tests')
    group.add_argument('-r', '--randomize', action='store_true',
                       help='randomize test execution order.' + more_details)
    group.add_argument('--randseed', metavar='SEED',
                       dest='random_seed', type=int,
                       help='pass a random seed to reproduce a previous '
                            'random run')
    group.add_argument('-f', '--fromfile', metavar='FILE',
                       help='read names of tests to run z a file.' +
                            more_details)
    group.add_argument('-x', '--exclude', action='store_true',
                       help='arguments are tests to *exclude*')
    group.add_argument('-s', '--single', action='store_true',
                       help='single step through a set of tests.' +
                            more_details)
    group.add_argument('-m', '--match', metavar='PAT',
                       dest='match_tests',
                       help='match test cases oraz methods przy glob pattern PAT')
    group.add_argument('-G', '--failfast', action='store_true',
                       help='fail jako soon jako a test fails (only przy -v albo -W)')
    group.add_argument('-u', '--use', metavar='RES1,RES2,...',
                       action='append', type=resources_list,
                       help='specify which special resource intensive tests '
                            'to run.' + more_details)
    group.add_argument('-M', '--memlimit', metavar='LIMIT',
                       help='run very large memory-consuming tests.' +
                            more_details)
    group.add_argument('--testdir', metavar='DIR',
                       type=relative_filename,
                       help='execute test files w the specified directory '
                            '(instead of the Python stdlib test suite)')

    group = parser.add_argument_group('Special runs')
    group.add_argument('-l', '--findleaks', action='store_true',
                       help='jeżeli GC jest available detect tests that leak memory')
    group.add_argument('-L', '--runleaks', action='store_true',
                       help='run the leaks(1) command just before exit.' +
                            more_details)
    group.add_argument('-R', '--huntrleaks', metavar='RUNCOUNTS',
                       type=huntrleaks,
                       help='search dla reference leaks (needs debug build, '
                            'very slow).' + more_details)
    group.add_argument('-j', '--multiprocess', metavar='PROCESSES',
                       dest='use_mp', type=int,
                       help='run PROCESSES processes at once')
    group.add_argument('-T', '--coverage', action='store_true',
                       dest='trace',
                       help='turn on code coverage tracing using the trace '
                            'module')
    group.add_argument('-D', '--coverdir', metavar='DIR',
                       type=relative_filename,
                       help='directory where coverage files are put')
    group.add_argument('-N', '--nocoverdir',
                       action='store_const', const=Nic, dest='coverdir',
                       help='put coverage files alongside modules')
    group.add_argument('-t', '--threshold', metavar='THRESHOLD',
                       type=int,
                       help='call gc.set_threshold(THRESHOLD)')
    group.add_argument('-n', '--nowindows', action='store_true',
                       help='suppress error message boxes on Windows')
    group.add_argument('-F', '--forever', action='store_true',
                       help='run the specified tests w a loop, until an '
                            'error happens')

    parser.add_argument('args', nargs=argparse.REMAINDER,
                        help=argparse.SUPPRESS)

    zwróć parser

def relative_filename(string):
    # CWD jest replaced przy a temporary dir before calling main(), so we
    # join it przy the saved CWD so it ends up where the user expects.
    zwróć os.path.join(support.SAVEDCWD, string)

def huntrleaks(string):
    args = string.split(':')
    jeżeli len(args) nie w (2, 3):
        podnieś argparse.ArgumentTypeError(
            'needs 2 albo 3 colon-separated arguments')
    nwarmup = int(args[0]) jeżeli args[0] inaczej 5
    ntracked = int(args[1]) jeżeli args[1] inaczej 4
    fname = args[2] jeżeli len(args) > 2 oraz args[2] inaczej 'reflog.txt'
    zwróć nwarmup, ntracked, fname

def resources_list(string):
    u = [x.lower() dla x w string.split(',')]
    dla r w u:
        jeżeli r == 'all' albo r == 'none':
            kontynuuj
        jeżeli r[0] == '-':
            r = r[1:]
        jeżeli r nie w RESOURCE_NAMES:
            podnieś argparse.ArgumentTypeError('invalid resource: ' + r)
    zwróć u

def _parse_args(args, **kwargs):
    # Defaults
    ns = argparse.Namespace(testdir=Nic, verbose=0, quiet=Nieprawda,
         exclude=Nieprawda, single=Nieprawda, randomize=Nieprawda, fromfile=Nic,
         findleaks=Nieprawda, use_resources=Nic, trace=Nieprawda, coverdir='coverage',
         runleaks=Nieprawda, huntrleaks=Nieprawda, verbose2=Nieprawda, print_slow=Nieprawda,
         random_seed=Nic, use_mp=Nic, verbose3=Nieprawda, forever=Nieprawda,
         header=Nieprawda, failfast=Nieprawda, match_tests=Nic)
    dla k, v w kwargs.items():
        jeżeli nie hasattr(ns, k):
            podnieś TypeError('%r jest an invalid keyword argument '
                            'dla this function' % k)
        setattr(ns, k, v)
    jeżeli ns.use_resources jest Nic:
        ns.use_resources = []

    parser = _create_parser()
    parser.parse_args(args=args, namespace=ns)

    jeżeli ns.single oraz ns.fromfile:
        parser.error("-s oraz -f don't go together!")
    jeżeli ns.use_mp oraz ns.trace:
        parser.error("-T oraz -j don't go together!")
    jeżeli ns.use_mp oraz ns.findleaks:
        parser.error("-l oraz -j don't go together!")
    jeżeli ns.use_mp oraz ns.memlimit:
        parser.error("-M oraz -j don't go together!")
    jeżeli ns.failfast oraz nie (ns.verbose albo ns.verbose3):
        parser.error("-G/--failfast needs either -v albo -W")

    jeżeli ns.quiet:
        ns.verbose = 0
    jeżeli ns.timeout jest nie Nic:
        jeżeli hasattr(faulthandler, 'dump_traceback_later'):
            jeżeli ns.timeout <= 0:
                ns.timeout = Nic
        inaczej:
            print("Warning: The timeout option requires "
                  "faulthandler.dump_traceback_later")
            ns.timeout = Nic
    jeżeli ns.use_mp jest nie Nic:
        jeżeli ns.use_mp <= 0:
            # Use all cores + extras dla tests that like to sleep
            ns.use_mp = 2 + (os.cpu_count() albo 1)
        jeżeli ns.use_mp == 1:
            ns.use_mp = Nic
    jeżeli ns.use:
        dla a w ns.use:
            dla r w a:
                jeżeli r == 'all':
                    ns.use_resources[:] = RESOURCE_NAMES
                    kontynuuj
                jeżeli r == 'none':
                    usuń ns.use_resources[:]
                    kontynuuj
                remove = Nieprawda
                jeżeli r[0] == '-':
                    remove = Prawda
                    r = r[1:]
                jeżeli remove:
                    jeżeli r w ns.use_resources:
                        ns.use_resources.remove(r)
                albo_inaczej r nie w ns.use_resources:
                    ns.use_resources.append(r)
    jeżeli ns.random_seed jest nie Nic:
        ns.randomize = Prawda

    zwróć ns


def run_test_in_subprocess(testname, ns):
    """Run the given test w a subprocess przy --slaveargs.

    ns jest the option Namespace parsed z command-line arguments. regrtest
    jest invoked w a subprocess przy the --slaveargs argument; when the
    subprocess exits, its zwróć code, stdout oraz stderr are returned jako a
    3-tuple.
    """
    z subprocess zaimportuj Popen, PIPE
    base_cmd = ([sys.executable] + support.args_from_interpreter_flags() +
                ['-X', 'faulthandler', '-m', 'test.regrtest'])

    slaveargs = (
            (testname, ns.verbose, ns.quiet),
            dict(huntrleaks=ns.huntrleaks,
                 use_resources=ns.use_resources,
                 output_on_failure=ns.verbose3,
                 timeout=ns.timeout, failfast=ns.failfast,
                 match_tests=ns.match_tests))
    # Running the child z the same working directory jako regrtest's original
    # invocation ensures that TEMPDIR dla the child jest the same when
    # sysconfig.is_python_build() jest true. See issue 15300.
    popen = Popen(base_cmd + ['--slaveargs', json.dumps(slaveargs)],
                  stdout=PIPE, stderr=PIPE,
                  universal_newlines=Prawda,
                  close_fds=(os.name != 'nt'),
                  cwd=support.SAVEDCWD)
    stdout, stderr = popen.communicate()
    retcode = popen.wait()
    zwróć retcode, stdout, stderr


def main(tests=Nic, **kwargs):
    """Execute a test suite.

    This also parses command-line options oraz modifies its behavior
    accordingly.

    tests -- a list of strings containing test names (optional)
    testdir -- the directory w which to look dla tests (optional)

    Users other than the Python test suite will certainly want to
    specify testdir; jeżeli it's omitted, the directory containing the
    Python test suite jest searched for.

    If the tests argument jest omitted, the tests listed on the
    command-line will be used.  If that's empty, too, then all *.py
    files beginning przy test_ will be used.

    The other default arguments (verbose, quiet, exclude,
    single, randomize, findleaks, use_resources, trace, coverdir,
    print_slow, oraz random_seed) allow programmers calling main()
    directly to set the values that would normally be set by flags
    on the command line.
    """
    # Display the Python traceback on fatal errors (e.g. segfault)
    faulthandler.enable(all_threads=Prawda)

    # Display the Python traceback on SIGALRM albo SIGUSR1 signal
    signals = []
    jeżeli hasattr(signal, 'SIGALRM'):
        signals.append(signal.SIGALRM)
    jeżeli hasattr(signal, 'SIGUSR1'):
        signals.append(signal.SIGUSR1)
    dla signum w signals:
        faulthandler.register(signum, chain=Prawda)

    replace_stdout()

    support.record_original_stdout(sys.stdout)

    ns = _parse_args(sys.argv[1:], **kwargs)

    jeżeli ns.huntrleaks:
        # Avoid false positives due to various caches
        # filling slowly przy random data:
        warm_caches()
    jeżeli ns.memlimit jest nie Nic:
        support.set_memlimit(ns.memlimit)
    jeżeli ns.threshold jest nie Nic:
        zaimportuj gc
        gc.set_threshold(ns.threshold)
    jeżeli ns.nowindows:
        zaimportuj msvcrt
        msvcrt.SetErrorMode(msvcrt.SEM_FAILCRITICALERRORS|
                            msvcrt.SEM_NOALIGNMENTFAULTEXCEPT|
                            msvcrt.SEM_NOGPFAULTERRORBOX|
                            msvcrt.SEM_NOOPENFILEERRORBOX)
        spróbuj:
            msvcrt.CrtSetReportMode
        wyjąwszy AttributeError:
            # release build
            dalej
        inaczej:
            dla m w [msvcrt.CRT_WARN, msvcrt.CRT_ERROR, msvcrt.CRT_ASSERT]:
                msvcrt.CrtSetReportMode(m, msvcrt.CRTDBG_MODE_FILE)
                msvcrt.CrtSetReportFile(m, msvcrt.CRTDBG_FILE_STDERR)
    jeżeli ns.wait:
        input("Press any key to continue...")

    jeżeli ns.slaveargs jest nie Nic:
        args, kwargs = json.loads(ns.slaveargs)
        jeżeli kwargs.get('huntrleaks'):
            unittest.BaseTestSuite._cleanup = Nieprawda
        spróbuj:
            result = runtest(*args, **kwargs)
        wyjąwszy KeyboardInterrupt:
            result = INTERRUPTED, ''
        wyjąwszy BaseException jako e:
            traceback.print_exc()
            result = CHILD_ERROR, str(e)
        sys.stdout.flush()
        print()   # Force a newline (just w case)
        print(json.dumps(result))
        sys.exit(0)

    good = []
    bad = []
    skipped = []
    resource_denieds = []
    environment_changed = []
    interrupted = Nieprawda

    jeżeli ns.findleaks:
        spróbuj:
            zaimportuj gc
        wyjąwszy ImportError:
            print('No GC available, disabling findleaks.')
            ns.findleaks = Nieprawda
        inaczej:
            # Uncomment the line below to report garbage that jest nie
            # freeable by reference counting alone.  By default only
            # garbage that jest nie collectable by the GC jest reported.
            #gc.set_debug(gc.DEBUG_SAVEALL)
            found_garbage = []

    jeżeli ns.huntrleaks:
        unittest.BaseTestSuite._cleanup = Nieprawda

    jeżeli ns.single:
        filename = os.path.join(TEMPDIR, 'pynexttest')
        spróbuj:
            przy open(filename, 'r') jako fp:
                next_test = fp.read().strip()
                tests = [next_test]
        wyjąwszy OSError:
            dalej

    jeżeli ns.fromfile:
        tests = []
        przy open(os.path.join(support.SAVEDCWD, ns.fromfile)) jako fp:
            count_pat = re.compile(r'\[\s*\d+/\s*\d+\]')
            dla line w fp:
                line = count_pat.sub('', line)
                guts = line.split() # assuming no test has whitespace w its name
                jeżeli guts oraz nie guts[0].startswith('#'):
                    tests.extend(guts)

    # Strip .py extensions.
    removepy(ns.args)
    removepy(tests)

    stdtests = STDTESTS[:]
    nottests = NOTTESTS.copy()
    jeżeli ns.exclude:
        dla arg w ns.args:
            jeżeli arg w stdtests:
                stdtests.remove(arg)
            nottests.add(arg)
        ns.args = []

    # For a partial run, we do nie need to clutter the output.
    jeżeli ns.verbose albo ns.header albo nie (ns.quiet albo ns.single albo tests albo ns.args):
        # Print basic platform information
        print("==", platform.python_implementation(), *sys.version.split())
        print("==  ", platform.platform(aliased=Prawda),
                      "%s-endian" % sys.byteorder)
        print("==  ", "hash algorithm:", sys.hash_info.algorithm,
              "64bit" jeżeli sys.maxsize > 2**32 inaczej "32bit")
        print("==  ", os.getcwd())
        print("Testing przy flags:", sys.flags)

    # jeżeli testdir jest set, then we are nie running the python tests suite, so
    # don't add default tests to be executed albo skipped (pass empty values)
    jeżeli ns.testdir:
        alltests = findtests(ns.testdir, list(), set())
    inaczej:
        alltests = findtests(ns.testdir, stdtests, nottests)

    selected = tests albo ns.args albo alltests
    jeżeli ns.single:
        selected = selected[:1]
        spróbuj:
            next_single_test = alltests[alltests.index(selected[0])+1]
        wyjąwszy IndexError:
            next_single_test = Nic
    # Remove all the selected tests that precede start jeżeli it's set.
    jeżeli ns.start:
        spróbuj:
            usuń selected[:selected.index(ns.start)]
        wyjąwszy ValueError:
            print("Couldn't find starting test (%s), using all tests" % ns.start)
    jeżeli ns.randomize:
        jeżeli ns.random_seed jest Nic:
            ns.random_seed = random.randrange(10000000)
        random.seed(ns.random_seed)
        print("Using random seed", ns.random_seed)
        random.shuffle(selected)
    jeżeli ns.trace:
        zaimportuj trace, tempfile
        tracer = trace.Trace(ignoredirs=[sys.base_prefix, sys.base_exec_prefix,
                                         tempfile.gettempdir()],
                             trace=Nieprawda, count=Prawda)

    test_times = []
    support.verbose = ns.verbose      # Tell tests to be moderately quiet
    support.use_resources = ns.use_resources
    save_modules = sys.modules.keys()

    def accumulate_result(test, result):
        ok, test_time = result
        test_times.append((test_time, test))
        jeżeli ok == PASSED:
            good.append(test)
        albo_inaczej ok == FAILED:
            bad.append(test)
        albo_inaczej ok == ENV_CHANGED:
            environment_changed.append(test)
        albo_inaczej ok == SKIPPED:
            skipped.append(test)
        albo_inaczej ok == RESOURCE_DENIED:
            skipped.append(test)
            resource_denieds.append(test)

    jeżeli ns.forever:
        def test_forever(tests=list(selected)):
            dopóki Prawda:
                dla test w tests:
                    uzyskaj test
                    jeżeli bad:
                        zwróć
        tests = test_forever()
        test_count = ''
        test_count_width = 3
    inaczej:
        tests = iter(selected)
        test_count = '/{}'.format(len(selected))
        test_count_width = len(test_count) - 1

    jeżeli ns.use_mp:
        spróbuj:
            z threading zaimportuj Thread
        wyjąwszy ImportError:
            print("Multiprocess option requires thread support")
            sys.exit(2)
        z queue zaimportuj Queue
        debug_output_pat = re.compile(r"\[\d+ refs, \d+ blocks\]$")
        output = Queue()
        pending = MultiprocessTests(tests)
        def work():
            # A worker thread.
            spróbuj:
                dopóki Prawda:
                    spróbuj:
                        test = next(pending)
                    wyjąwszy StopIteration:
                        output.put((Nic, Nic, Nic, Nic))
                        zwróć
                    retcode, stdout, stderr = run_test_in_subprocess(test, ns)
                    # Strip last refcount output line jeżeli it exists, since it
                    # comes z the shutdown of the interpreter w the subcommand.
                    stderr = debug_output_pat.sub("", stderr)
                    stdout, _, result = stdout.strip().rpartition("\n")
                    jeżeli retcode != 0:
                        result = (CHILD_ERROR, "Exit code %s" % retcode)
                        output.put((test, stdout.rstrip(), stderr.rstrip(), result))
                        zwróć
                    jeżeli nie result:
                        output.put((Nic, Nic, Nic, Nic))
                        zwróć
                    result = json.loads(result)
                    output.put((test, stdout.rstrip(), stderr.rstrip(), result))
            wyjąwszy BaseException:
                output.put((Nic, Nic, Nic, Nic))
                podnieś
        workers = [Thread(target=work) dla i w range(ns.use_mp)]
        dla worker w workers:
            worker.start()
        finished = 0
        test_index = 1
        spróbuj:
            dopóki finished < ns.use_mp:
                test, stdout, stderr, result = output.get()
                jeżeli test jest Nic:
                    finished += 1
                    kontynuuj
                accumulate_result(test, result)
                jeżeli nie ns.quiet:
                    fmt = "[{1:{0}}{2}/{3}] {4}" jeżeli bad inaczej "[{1:{0}}{2}] {4}"
                    print(fmt.format(
                        test_count_width, test_index, test_count,
                        len(bad), test))
                jeżeli stdout:
                    print(stdout)
                jeżeli stderr:
                    print(stderr, file=sys.stderr)
                sys.stdout.flush()
                sys.stderr.flush()
                jeżeli result[0] == INTERRUPTED:
                    podnieś KeyboardInterrupt
                jeżeli result[0] == CHILD_ERROR:
                    podnieś Exception("Child error on {}: {}".format(test, result[1]))
                test_index += 1
        wyjąwszy KeyboardInterrupt:
            interrupted = Prawda
            pending.interrupted = Prawda
        dla worker w workers:
            worker.join()
    inaczej:
        dla test_index, test w enumerate(tests, 1):
            jeżeli nie ns.quiet:
                fmt = "[{1:{0}}{2}/{3}] {4}" jeżeli bad inaczej "[{1:{0}}{2}] {4}"
                print(fmt.format(
                    test_count_width, test_index, test_count, len(bad), test))
                sys.stdout.flush()
            jeżeli ns.trace:
                # If we're tracing code coverage, then we don't exit przy status
                # jeżeli on a false zwróć value z main.
                tracer.runctx('runtest(test, ns.verbose, ns.quiet, timeout=ns.timeout)',
                              globals=globals(), locals=vars())
            inaczej:
                spróbuj:
                    result = runtest(test, ns.verbose, ns.quiet,
                                     ns.huntrleaks,
                                     output_on_failure=ns.verbose3,
                                     timeout=ns.timeout, failfast=ns.failfast,
                                     match_tests=ns.match_tests)
                    accumulate_result(test, result)
                wyjąwszy KeyboardInterrupt:
                    interrupted = Prawda
                    przerwij
            jeżeli ns.findleaks:
                gc.collect()
                jeżeli gc.garbage:
                    print("Warning: test created", len(gc.garbage), end=' ')
                    print("uncollectable object(s).")
                    # move the uncollectable objects somewhere so we don't see
                    # them again
                    found_garbage.extend(gc.garbage)
                    usuń gc.garbage[:]
            # Unload the newly imported modules (best effort finalization)
            dla module w sys.modules.keys():
                jeżeli module nie w save_modules oraz module.startswith("test."):
                    support.unload(module)

    jeżeli interrupted:
        # print a newline after ^C
        print()
        print("Test suite interrupted by signal SIGINT.")
        omitted = set(selected) - set(good) - set(bad) - set(skipped)
        print(count(len(omitted), "test"), "omitted:")
        printlist(omitted)
    jeżeli good oraz nie ns.quiet:
        jeżeli nie bad oraz nie skipped oraz nie interrupted oraz len(good) > 1:
            print("All", end=' ')
        print(count(len(good), "test"), "OK.")
    jeżeli ns.print_slow:
        test_times.sort(reverse=Prawda)
        print("10 slowest tests:")
        dla time, test w test_times[:10]:
            print("%s: %.1fs" % (test, time))
    jeżeli bad:
        print(count(len(bad), "test"), "failed:")
        printlist(bad)
    jeżeli environment_changed:
        print("{} altered the execution environment:".format(
                 count(len(environment_changed), "test")))
        printlist(environment_changed)
    jeżeli skipped oraz nie ns.quiet:
        print(count(len(skipped), "test"), "skipped:")
        printlist(skipped)

    jeżeli ns.verbose2 oraz bad:
        print("Re-running failed tests w verbose mode")
        dla test w bad[:]:
            print("Re-running test %r w verbose mode" % test)
            sys.stdout.flush()
            spróbuj:
                ns.verbose = Prawda
                ok = runtest(test, Prawda, ns.quiet, ns.huntrleaks,
                             timeout=ns.timeout)
            wyjąwszy KeyboardInterrupt:
                # print a newline separate z the ^C
                print()
                przerwij
            inaczej:
                jeżeli ok[0] w {PASSED, ENV_CHANGED, SKIPPED, RESOURCE_DENIED}:
                    bad.remove(test)
        inaczej:
            jeżeli bad:
                print(count(len(bad), 'test'), "failed again:")
                printlist(bad)

    jeżeli ns.single:
        jeżeli next_single_test:
            przy open(filename, 'w') jako fp:
                fp.write(next_single_test + '\n')
        inaczej:
            os.unlink(filename)

    jeżeli ns.trace:
        r = tracer.results()
        r.write_results(show_missing=Prawda, summary=Prawda, coverdir=ns.coverdir)

    jeżeli ns.runleaks:
        os.system("leaks %d" % os.getpid())

    sys.exit(len(bad) > 0 albo interrupted)


# small set of tests to determine jeżeli we have a basically functioning interpreter
# (i.e. jeżeli any of these fail, then anything inaczej jest likely to follow)
STDTESTS = [
    'test_grammar',
    'test_opcodes',
    'test_dict',
    'test_builtin',
    'test_exceptions',
    'test_types',
    'test_unittest',
    'test_doctest',
    'test_doctest2',
    'test_support'
]

# set of tests that we don't want to be executed when using regrtest
NOTTESTS = set()

def findtests(testdir=Nic, stdtests=STDTESTS, nottests=NOTTESTS):
    """Return a list of all applicable test modules."""
    testdir = findtestdir(testdir)
    names = os.listdir(testdir)
    tests = []
    others = set(stdtests) | nottests
    dla name w names:
        mod, ext = os.path.splitext(name)
        jeżeli mod[:5] == "test_" oraz ext w (".py", "") oraz mod nie w others:
            tests.append(mod)
    zwróć stdtests + sorted(tests)

# We do nie use a generator so multiple threads can call next().
klasa MultiprocessTests(object):

    """A thread-safe iterator over tests dla multiprocess mode."""

    def __init__(self, tests):
        self.interrupted = Nieprawda
        self.lock = threading.Lock()
        self.tests = tests

    def __iter__(self):
        zwróć self

    def __next__(self):
        przy self.lock:
            jeżeli self.interrupted:
                podnieś StopIteration('tests interrupted')
            zwróć next(self.tests)

def replace_stdout():
    """Set stdout encoder error handler to backslashreplace (as stderr error
    handler) to avoid UnicodeEncodeError when printing a traceback"""
    zaimportuj atexit

    stdout = sys.stdout
    sys.stdout = open(stdout.fileno(), 'w',
        encoding=stdout.encoding,
        errors="backslashreplace",
        closefd=Nieprawda,
        newline='\n')

    def restore_stdout():
        sys.stdout.close()
        sys.stdout = stdout
    atexit.register(restore_stdout)

def runtest(test, verbose, quiet,
            huntrleaks=Nieprawda, use_resources=Nic,
            output_on_failure=Nieprawda, failfast=Nieprawda, match_tests=Nic,
            timeout=Nic):
    """Run a single test.

    test -- the name of the test
    verbose -- jeżeli true, print more messages
    quiet -- jeżeli true, don't print 'skipped' messages (probably redundant)
    huntrleaks -- run multiple times to test dla leaks; requires a debug
                  build; a triple corresponding to -R's three arguments
    use_resources -- list of extra resources to use
    output_on_failure -- jeżeli true, display test output on failure
    timeout -- dump the traceback oraz exit jeżeli a test takes more than
               timeout seconds
    failfast, match_tests -- See regrtest command-line flags dla these.

    Returns the tuple result, test_time, where result jest one of the constants:
        INTERRUPTED      KeyboardInterrupt when run under -j
        RESOURCE_DENIED  test skipped because resource denied
        SKIPPED          test skipped dla some other reason
        ENV_CHANGED      test failed because it changed the execution environment
        FAILED           test failed
        PASSED           test dalejed
    """

    jeżeli use_resources jest nie Nic:
        support.use_resources = use_resources
    use_timeout = (timeout jest nie Nic)
    jeżeli use_timeout:
        faulthandler.dump_traceback_later(timeout, exit=Prawda)
    spróbuj:
        support.match_tests = match_tests
        jeżeli failfast:
            support.failfast = Prawda
        jeżeli output_on_failure:
            support.verbose = Prawda

            # Reuse the same instance to all calls to runtest(). Some
            # tests keep a reference to sys.stdout albo sys.stderr
            # (eg. test_argparse).
            jeżeli runtest.stringio jest Nic:
                stream = io.StringIO()
                runtest.stringio = stream
            inaczej:
                stream = runtest.stringio
                stream.seek(0)
                stream.truncate()

            orig_stdout = sys.stdout
            orig_stderr = sys.stderr
            spróbuj:
                sys.stdout = stream
                sys.stderr = stream
                result = runtest_inner(test, verbose, quiet, huntrleaks,
                                       display_failure=Nieprawda)
                jeżeli result[0] == FAILED:
                    output = stream.getvalue()
                    orig_stderr.write(output)
                    orig_stderr.flush()
            w_końcu:
                sys.stdout = orig_stdout
                sys.stderr = orig_stderr
        inaczej:
            support.verbose = verbose  # Tell tests to be moderately quiet
            result = runtest_inner(test, verbose, quiet, huntrleaks,
                                   display_failure=nie verbose)
        zwróć result
    w_końcu:
        jeżeli use_timeout:
            faulthandler.cancel_dump_traceback_later()
        cleanup_test_droppings(test, verbose)
runtest.stringio = Nic

# Unit tests are supposed to leave the execution environment unchanged
# once they complete.  But sometimes tests have bugs, especially when
# tests fail, oraz the changes to environment go on to mess up other
# tests.  This can cause issues przy buildbot stability, since tests
# are run w random order oraz so problems may appear to come oraz go.
# There are a few things we can save oraz restore to mitigate this, oraz
# the following context manager handles this task.

klasa saved_test_environment:
    """Save bits of the test environment oraz restore them at block exit.

        przy saved_test_environment(testname, verbose, quiet):
            #stuff

    Unless quiet jest Prawda, a warning jest printed to stderr jeżeli any of
    the saved items was changed by the test.  The attribute 'changed'
    jest initially Nieprawda, but jest set to Prawda jeżeli a change jest detected.

    If verbose jest more than 1, the before oraz after state of changed
    items jest also printed.
    """

    changed = Nieprawda

    def __init__(self, testname, verbose=0, quiet=Nieprawda):
        self.testname = testname
        self.verbose = verbose
        self.quiet = quiet

    # To add things to save oraz restore, add a name XXX to the resources list
    # oraz add corresponding get_XXX/restore_XXX functions.  get_XXX should
    # zwróć the value to be saved oraz compared against a second call to the
    # get function when test execution completes.  restore_XXX should accept
    # the saved value oraz restore the resource using it.  It will be called if
    # oraz only jeżeli a change w the value jest detected.
    #
    # Note: XXX will have any '.' replaced przy '_' characters when determining
    # the corresponding method names.

    resources = ('sys.argv', 'cwd', 'sys.stdin', 'sys.stdout', 'sys.stderr',
                 'os.environ', 'sys.path', 'sys.path_hooks', '__import__',
                 'warnings.filters', 'asyncore.socket_map',
                 'logging._handlers', 'logging._handlerList', 'sys.gettrace',
                 'sys.warnoptions',
                 # multiprocessing.process._cleanup() may release ref
                 # to a thread, so check processes first.
                 'multiprocessing.process._dangling', 'threading._dangling',
                 'sysconfig._CONFIG_VARS', 'sysconfig._INSTALL_SCHEMES',
                 'files', 'locale', 'warnings.showwarning',
                )

    def get_sys_argv(self):
        zwróć id(sys.argv), sys.argv, sys.argv[:]
    def restore_sys_argv(self, saved_argv):
        sys.argv = saved_argv[1]
        sys.argv[:] = saved_argv[2]

    def get_cwd(self):
        zwróć os.getcwd()
    def restore_cwd(self, saved_cwd):
        os.chdir(saved_cwd)

    def get_sys_stdout(self):
        zwróć sys.stdout
    def restore_sys_stdout(self, saved_stdout):
        sys.stdout = saved_stdout

    def get_sys_stderr(self):
        zwróć sys.stderr
    def restore_sys_stderr(self, saved_stderr):
        sys.stderr = saved_stderr

    def get_sys_stdin(self):
        zwróć sys.stdin
    def restore_sys_stdin(self, saved_stdin):
        sys.stdin = saved_stdin

    def get_os_environ(self):
        zwróć id(os.environ), os.environ, dict(os.environ)
    def restore_os_environ(self, saved_environ):
        os.environ = saved_environ[1]
        os.environ.clear()
        os.environ.update(saved_environ[2])

    def get_sys_path(self):
        zwróć id(sys.path), sys.path, sys.path[:]
    def restore_sys_path(self, saved_path):
        sys.path = saved_path[1]
        sys.path[:] = saved_path[2]

    def get_sys_path_hooks(self):
        zwróć id(sys.path_hooks), sys.path_hooks, sys.path_hooks[:]
    def restore_sys_path_hooks(self, saved_hooks):
        sys.path_hooks = saved_hooks[1]
        sys.path_hooks[:] = saved_hooks[2]

    def get_sys_gettrace(self):
        zwróć sys.gettrace()
    def restore_sys_gettrace(self, trace_fxn):
        sys.settrace(trace_fxn)

    def get___import__(self):
        zwróć builtins.__import__
    def restore___import__(self, import_):
        builtins.__import__ = import_

    def get_warnings_filters(self):
        zwróć id(warnings.filters), warnings.filters, warnings.filters[:]
    def restore_warnings_filters(self, saved_filters):
        warnings.filters = saved_filters[1]
        warnings.filters[:] = saved_filters[2]

    def get_asyncore_socket_map(self):
        asyncore = sys.modules.get('asyncore')
        # XXX Making a copy keeps objects alive until __exit__ gets called.
        zwróć asyncore oraz asyncore.socket_map.copy() albo {}
    def restore_asyncore_socket_map(self, saved_map):
        asyncore = sys.modules.get('asyncore')
        jeżeli asyncore jest nie Nic:
            asyncore.close_all(ignore_all=Prawda)
            asyncore.socket_map.update(saved_map)

    def get_shutil_archive_formats(self):
        # we could call get_archives_formats() but that only returns the
        # registry keys; we want to check the values too (the functions that
        # are registered)
        zwróć shutil._ARCHIVE_FORMATS, shutil._ARCHIVE_FORMATS.copy()
    def restore_shutil_archive_formats(self, saved):
        shutil._ARCHIVE_FORMATS = saved[0]
        shutil._ARCHIVE_FORMATS.clear()
        shutil._ARCHIVE_FORMATS.update(saved[1])

    def get_shutil_unpack_formats(self):
        zwróć shutil._UNPACK_FORMATS, shutil._UNPACK_FORMATS.copy()
    def restore_shutil_unpack_formats(self, saved):
        shutil._UNPACK_FORMATS = saved[0]
        shutil._UNPACK_FORMATS.clear()
        shutil._UNPACK_FORMATS.update(saved[1])

    def get_logging__handlers(self):
        # _handlers jest a WeakValueDictionary
        zwróć id(logging._handlers), logging._handlers, logging._handlers.copy()
    def restore_logging__handlers(self, saved_handlers):
        # Can't easily revert the logging state
        dalej

    def get_logging__handlerList(self):
        # _handlerList jest a list of weakrefs to handlers
        zwróć id(logging._handlerList), logging._handlerList, logging._handlerList[:]
    def restore_logging__handlerList(self, saved_handlerList):
        # Can't easily revert the logging state
        dalej

    def get_sys_warnoptions(self):
        zwróć id(sys.warnoptions), sys.warnoptions, sys.warnoptions[:]
    def restore_sys_warnoptions(self, saved_options):
        sys.warnoptions = saved_options[1]
        sys.warnoptions[:] = saved_options[2]

    # Controlling dangling references to Thread objects can make it easier
    # to track reference leaks.
    def get_threading__dangling(self):
        jeżeli nie threading:
            zwróć Nic
        # This copies the weakrefs without making any strong reference
        zwróć threading._dangling.copy()
    def restore_threading__dangling(self, saved):
        jeżeli nie threading:
            zwróć
        threading._dangling.clear()
        threading._dangling.update(saved)

    # Same dla Process objects
    def get_multiprocessing_process__dangling(self):
        jeżeli nie multiprocessing:
            zwróć Nic
        # Unjoined process objects can survive after process exits
        multiprocessing.process._cleanup()
        # This copies the weakrefs without making any strong reference
        zwróć multiprocessing.process._dangling.copy()
    def restore_multiprocessing_process__dangling(self, saved):
        jeżeli nie multiprocessing:
            zwróć
        multiprocessing.process._dangling.clear()
        multiprocessing.process._dangling.update(saved)

    def get_sysconfig__CONFIG_VARS(self):
        # make sure the dict jest initialized
        sysconfig.get_config_var('prefix')
        zwróć (id(sysconfig._CONFIG_VARS), sysconfig._CONFIG_VARS,
                dict(sysconfig._CONFIG_VARS))
    def restore_sysconfig__CONFIG_VARS(self, saved):
        sysconfig._CONFIG_VARS = saved[1]
        sysconfig._CONFIG_VARS.clear()
        sysconfig._CONFIG_VARS.update(saved[2])

    def get_sysconfig__INSTALL_SCHEMES(self):
        zwróć (id(sysconfig._INSTALL_SCHEMES), sysconfig._INSTALL_SCHEMES,
                sysconfig._INSTALL_SCHEMES.copy())
    def restore_sysconfig__INSTALL_SCHEMES(self, saved):
        sysconfig._INSTALL_SCHEMES = saved[1]
        sysconfig._INSTALL_SCHEMES.clear()
        sysconfig._INSTALL_SCHEMES.update(saved[2])

    def get_files(self):
        zwróć sorted(fn + ('/' jeżeli os.path.isdir(fn) inaczej '')
                      dla fn w os.listdir())
    def restore_files(self, saved_value):
        fn = support.TESTFN
        jeżeli fn nie w saved_value oraz (fn + '/') nie w saved_value:
            jeżeli os.path.isfile(fn):
                support.unlink(fn)
            albo_inaczej os.path.isdir(fn):
                support.rmtree(fn)

    _lc = [getattr(locale, lc) dla lc w dir(locale)
           jeżeli lc.startswith('LC_')]
    def get_locale(self):
        pairings = []
        dla lc w self._lc:
            spróbuj:
                pairings.append((lc, locale.setlocale(lc, Nic)))
            wyjąwszy (TypeError, ValueError):
                kontynuuj
        zwróć pairings
    def restore_locale(self, saved):
        dla lc, setting w saved:
            locale.setlocale(lc, setting)

    def get_warnings_showwarning(self):
        zwróć warnings.showwarning
    def restore_warnings_showwarning(self, fxn):
        warnings.showwarning = fxn

    def resource_info(self):
        dla name w self.resources:
            method_suffix = name.replace('.', '_')
            get_name = 'get_' + method_suffix
            restore_name = 'restore_' + method_suffix
            uzyskaj name, getattr(self, get_name), getattr(self, restore_name)

    def __enter__(self):
        self.saved_values = dict((name, get()) dla name, get, restore
                                                   w self.resource_info())
        zwróć self

    def __exit__(self, exc_type, exc_val, exc_tb):
        saved_values = self.saved_values
        usuń self.saved_values
        dla name, get, restore w self.resource_info():
            current = get()
            original = saved_values.pop(name)
            # Check dla changes to the resource's value
            jeżeli current != original:
                self.changed = Prawda
                restore(original)
                jeżeli nie self.quiet:
                    print("Warning -- {} was modified by {}".format(
                                                 name, self.testname),
                                                 file=sys.stderr)
                    jeżeli self.verbose > 1:
                        print("  Before: {}\n  After:  {} ".format(
                                                  original, current),
                                                  file=sys.stderr)
        zwróć Nieprawda


def runtest_inner(test, verbose, quiet,
                  huntrleaks=Nieprawda, display_failure=Prawda):
    support.unload(test)

    test_time = 0.0
    refleak = Nieprawda  # Prawda jeżeli the test leaked references.
    spróbuj:
        jeżeli test.startswith('test.'):
            abstest = test
        inaczej:
            # Always zaimportuj it z the test package
            abstest = 'test.' + test
        przy saved_test_environment(test, verbose, quiet) jako environment:
            start_time = time.time()
            the_module = importlib.import_module(abstest)
            # If the test has a test_main, that will run the appropriate
            # tests.  If not, use normal unittest test loading.
            test_runner = getattr(the_module, "test_main", Nic)
            jeżeli test_runner jest Nic:
                def test_runner():
                    loader = unittest.TestLoader()
                    tests = loader.loadTestsFromModule(the_module)
                    dla error w loader.errors:
                        print(error, file=sys.stderr)
                    jeżeli loader.errors:
                        podnieś Exception("errors dopóki loading tests")
                    support.run_unittest(tests)
            test_runner()
            jeżeli huntrleaks:
                refleak = dash_R(the_module, test, test_runner, huntrleaks)
            test_time = time.time() - start_time
    wyjąwszy support.ResourceDenied jako msg:
        jeżeli nie quiet:
            print(test, "skipped --", msg)
            sys.stdout.flush()
        zwróć RESOURCE_DENIED, test_time
    wyjąwszy unittest.SkipTest jako msg:
        jeżeli nie quiet:
            print(test, "skipped --", msg)
            sys.stdout.flush()
        zwróć SKIPPED, test_time
    wyjąwszy KeyboardInterrupt:
        podnieś
    wyjąwszy support.TestFailed jako msg:
        jeżeli display_failure:
            print("test", test, "failed --", msg, file=sys.stderr)
        inaczej:
            print("test", test, "failed", file=sys.stderr)
        sys.stderr.flush()
        zwróć FAILED, test_time
    wyjąwszy:
        msg = traceback.format_exc()
        print("test", test, "crashed --", msg, file=sys.stderr)
        sys.stderr.flush()
        zwróć FAILED, test_time
    inaczej:
        jeżeli refleak:
            zwróć FAILED, test_time
        jeżeli environment.changed:
            zwróć ENV_CHANGED, test_time
        zwróć PASSED, test_time

def cleanup_test_droppings(testname, verbose):
    zaimportuj shutil
    zaimportuj stat
    zaimportuj gc

    # First kill any dangling references to open files etc.
    # This can also issue some ResourceWarnings which would otherwise get
    # triggered during the following test run, oraz possibly produce failures.
    gc.collect()

    # Try to clean up junk commonly left behind.  While tests shouldn't leave
    # any files albo directories behind, when a test fails that can be tedious
    # dla it to arrange.  The consequences can be especially nasty on Windows,
    # since jeżeli a test leaves a file open, it cannot be deleted by name (while
    # there's nothing we can do about that here either, we can display the
    # name of the offending test, which jest a real help).
    dla name w (support.TESTFN,
                 "db_home",
                ):
        jeżeli nie os.path.exists(name):
            kontynuuj

        jeżeli os.path.isdir(name):
            kind, nuker = "directory", shutil.rmtree
        albo_inaczej os.path.isfile(name):
            kind, nuker = "file", os.unlink
        inaczej:
            podnieś SystemError("os.path says %r exists but jest neither "
                              "directory nor file" % name)

        jeżeli verbose:
            print("%r left behind %s %r" % (testname, kind, name))
        spróbuj:
            # jeżeli we have chmod, fix possible permissions problems
            # that might prevent cleanup
            jeżeli (hasattr(os, 'chmod')):
                os.chmod(name, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            nuker(name)
        wyjąwszy Exception jako msg:
            print(("%r left behind %s %r oraz it couldn't be "
                "removed: %s" % (testname, kind, name, msg)), file=sys.stderr)

def dash_R(the_module, test, indirect_test, huntrleaks):
    """Run a test multiple times, looking dla reference leaks.

    Returns:
        Nieprawda jeżeli the test didn't leak references; Prawda jeżeli we detected refleaks.
    """
    # This code jest hackish oraz inelegant, but it seems to do the job.
    zaimportuj copyreg
    zaimportuj collections.abc

    jeżeli nie hasattr(sys, 'gettotalrefcount'):
        podnieś Exception("Tracking reference leaks requires a debug build "
                        "of Python")

    # Save current values dla dash_R_cleanup() to restore.
    fs = warnings.filters[:]
    ps = copyreg.dispatch_table.copy()
    pic = sys.path_importer_cache.copy()
    spróbuj:
        zaimportuj zipimport
    wyjąwszy ImportError:
        zdc = Nic # Run unmodified on platforms without zipzaimportuj support
    inaczej:
        zdc = zipimport._zip_directory_cache.copy()
    abcs = {}
    dla abc w [getattr(collections.abc, a) dla a w collections.abc.__all__]:
        jeżeli nie isabstract(abc):
            kontynuuj
        dla obj w abc.__subclasses__() + [abc]:
            abcs[obj] = obj._abc_registry.copy()

    nwarmup, ntracked, fname = huntrleaks
    fname = os.path.join(support.SAVEDCWD, fname)
    repcount = nwarmup + ntracked
    rc_deltas = [0] * repcount
    alloc_deltas = [0] * repcount

    print("beginning", repcount, "repetitions", file=sys.stderr)
    print(("1234567890"*(repcount//10 + 1))[:repcount], file=sys.stderr)
    sys.stderr.flush()
    dla i w range(repcount):
        indirect_test()
        alloc_after, rc_after = dash_R_cleanup(fs, ps, pic, zdc, abcs)
        sys.stderr.write('.')
        sys.stderr.flush()
        jeżeli i >= nwarmup:
            rc_deltas[i] = rc_after - rc_before
            alloc_deltas[i] = alloc_after - alloc_before
        alloc_before, rc_before = alloc_after, rc_after
    print(file=sys.stderr)
    # These checkers zwróć Nieprawda on success, Prawda on failure
    def check_rc_deltas(deltas):
        zwróć any(deltas)
    def check_alloc_deltas(deltas):
        # At least 1/3rd of 0s
        jeżeli 3 * deltas.count(0) < len(deltas):
            zwróć Prawda
        # Nothing inaczej than 1s, 0s oraz -1s
        jeżeli nie set(deltas) <= {1,0,-1}:
            zwróć Prawda
        zwróć Nieprawda
    failed = Nieprawda
    dla deltas, item_name, checker w [
        (rc_deltas, 'references', check_rc_deltas),
        (alloc_deltas, 'memory blocks', check_alloc_deltas)]:
        jeżeli checker(deltas):
            msg = '%s leaked %s %s, sum=%s' % (
                test, deltas[nwarmup:], item_name, sum(deltas))
            print(msg, file=sys.stderr)
            sys.stderr.flush()
            przy open(fname, "a") jako refrep:
                print(msg, file=refrep)
                refrep.flush()
            failed = Prawda
    zwróć failed

def dash_R_cleanup(fs, ps, pic, zdc, abcs):
    zaimportuj gc, copyreg
    zaimportuj _strptime, linecache
    zaimportuj urllib.parse, urllib.request, mimetypes, doctest
    zaimportuj struct, filecmp, collections.abc
    z distutils.dir_util zaimportuj _path_created
    z weakref zaimportuj WeakSet

    # Clear the warnings registry, so they can be displayed again
    dla mod w sys.modules.values():
        jeżeli hasattr(mod, '__warningregistry__'):
            usuń mod.__warningregistry__

    # Restore some original values.
    warnings.filters[:] = fs
    copyreg.dispatch_table.clear()
    copyreg.dispatch_table.update(ps)
    sys.path_importer_cache.clear()
    sys.path_importer_cache.update(pic)
    spróbuj:
        zaimportuj zipimport
    wyjąwszy ImportError:
        dalej # Run unmodified on platforms without zipzaimportuj support
    inaczej:
        zipimport._zip_directory_cache.clear()
        zipimport._zip_directory_cache.update(zdc)

    # clear type cache
    sys._clear_type_cache()

    # Clear ABC registries, restoring previously saved ABC registries.
    dla abc w [getattr(collections.abc, a) dla a w collections.abc.__all__]:
        jeżeli nie isabstract(abc):
            kontynuuj
        dla obj w abc.__subclasses__() + [abc]:
            obj._abc_registry = abcs.get(obj, WeakSet()).copy()
            obj._abc_cache.clear()
            obj._abc_negative_cache.clear()

    # Flush standard output, so that buffered data jest sent to the OS oraz
    # associated Python objects are reclaimed.
    dla stream w (sys.stdout, sys.stderr, sys.__stdout__, sys.__stderr__):
        jeżeli stream jest nie Nic:
            stream.flush()

    # Clear assorted module caches.
    _path_created.clear()
    re.purge()
    _strptime._regex_cache.clear()
    urllib.parse.clear_cache()
    urllib.request.urlcleanup()
    linecache.clearcache()
    mimetypes._default_mime_types()
    filecmp._cache.clear()
    struct._clearcache()
    doctest.master = Nic
    spróbuj:
        zaimportuj ctypes
    wyjąwszy ImportError:
        # Don't worry about resetting the cache jeżeli ctypes jest nie supported
        dalej
    inaczej:
        ctypes._reset_cache()

    # Collect cyclic trash oraz read memory statistics immediately after.
    func1 = sys.getallocatedblocks
    func2 = sys.gettotalrefcount
    gc.collect()
    zwróć func1(), func2()

def warm_caches():
    # char cache
    s = bytes(range(256))
    dla i w range(256):
        s[i:i+1]
    # unicode cache
    x = [chr(i) dla i w range(256)]
    # int cache
    x = list(range(-5, 257))

def findtestdir(path=Nic):
    zwróć path albo os.path.dirname(__file__) albo os.curdir

def removepy(names):
    jeżeli nie names:
        zwróć
    dla idx, name w enumerate(names):
        basename, ext = os.path.splitext(name)
        jeżeli ext == '.py':
            names[idx] = basename

def count(n, word):
    jeżeli n == 1:
        zwróć "%d %s" % (n, word)
    inaczej:
        zwróć "%d %ss" % (n, word)

def printlist(x, width=70, indent=4):
    """Print the elements of iterable x to stdout.

    Optional arg width (default 70) jest the maximum line length.
    Optional arg indent (default 4) jest the number of blanks przy which to
    begin each line.
    """

    z textwrap zaimportuj fill
    blanks = ' ' * indent
    # Print the sorted list: 'x' may be a '--random' list albo a set()
    print(fill(' '.join(str(elt) dla elt w sorted(x)), width,
               initial_indent=blanks, subsequent_indent=blanks))


def main_in_temp_cwd():
    """Run main() w a temporary working directory."""
    jeżeli sysconfig.is_python_build():
        spróbuj:
            os.mkdir(TEMPDIR)
        wyjąwszy FileExistsError:
            dalej

    # Define a writable temp dir that will be used jako cwd dopóki running
    # the tests. The name of the dir includes the pid to allow parallel
    # testing (see the -j option).
    test_cwd = 'test_python_{}'.format(os.getpid())
    test_cwd = os.path.join(TEMPDIR, test_cwd)

    # Run the tests w a context manager that temporarily changes the CWD to a
    # temporary oraz writable directory.  If it's nie possible to create albo
    # change the CWD, the original CWD will be used.  The original CWD jest
    # available z support.SAVEDCWD.
    przy support.temp_cwd(test_cwd, quiet=Prawda):
        main()


jeżeli __name__ == '__main__':
    # Remove regrtest.py's own directory z the module search path. Despite
    # the elimination of implicit relative imports, this jest still needed to
    # ensure that submodules of the test package do nie inappropriately appear
    # jako top-level modules even when people (or buildbots!) invoke regrtest.py
    # directly instead of using the -m switch
    mydir = os.path.abspath(os.path.normpath(os.path.dirname(sys.argv[0])))
    i = len(sys.path)
    dopóki i >= 0:
        i -= 1
        jeżeli os.path.abspath(os.path.normpath(sys.path[i])) == mydir:
            usuń sys.path[i]

    # findtestdir() gets the dirname out of __file__, so we have to make it
    # absolute before changing the working directory.
    # For example __file__ may be relative when running trace albo profile.
    # See issue #9323.
    __file__ = os.path.abspath(__file__)

    # sanity check
    assert __file__ == os.path.abspath(sys.argv[0])

    main_in_temp_cwd()
