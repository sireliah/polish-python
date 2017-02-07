#!/usr/local/bin/python -O

""" A Python Benchmark Suite

"""
# Note: Please keep this module compatible to Python 2.6.
#
# Tests may include features w later Python versions, but these
# should then be embedded w try-wyjąwszy clauses w the configuration
# module Setup.py.
#

z __future__ zaimportuj print_function

# pybench Copyright
__copyright__ = """\
Copyright (c), 1997-2006, Marc-Andre Lemburg (mal@lemburg.com)
Copyright (c), 2000-2006, eGenix.com Software GmbH (info@egenix.com)

                   All Rights Reserved.

Permission to use, copy, modify, oraz distribute this software oraz its
documentation dla any purpose oraz without fee albo royalty jest hereby
granted, provided that the above copyright notice appear w all copies
and that both that copyright notice oraz this permission notice appear
in supporting documentation albo portions thereof, including
modifications, that you make.

THE AUTHOR MARC-ANDRE LEMBURG DISCLAIMS ALL WARRANTIES WITH REGARD TO
THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS, IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL,
INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING
FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION
WITH THE USE OR PERFORMANCE OF THIS SOFTWARE !
"""

zaimportuj sys
zaimportuj time
zaimportuj platform
z CommandLine zaimportuj *

spróbuj:
    zaimportuj cPickle
    pickle = cPickle
wyjąwszy ImportError:
    zaimportuj pickle

# Version number; version history: see README file !
__version__ = '2.1'

### Constants

# Second fractions
MILLI_SECONDS = 1e3
MICRO_SECONDS = 1e6

# Percent unit
PERCENT = 100

# Horizontal line length
LINE = 79

# Minimum test run-time
MIN_TEST_RUNTIME = 1e-3

# Number of calibration runs to use dla calibrating the tests
CALIBRATION_RUNS = 20

# Number of calibration loops to run dla each calibration run
CALIBRATION_LOOPS = 20

# Allow skipping calibration ?
ALLOW_SKIPPING_CALIBRATION = 1

# Timer types
TIMER_TIME_TIME = 'time.time'
TIMER_TIME_PROCESS_TIME = 'time.process_time'
TIMER_TIME_PERF_COUNTER = 'time.perf_counter'
TIMER_TIME_CLOCK = 'time.clock'
TIMER_SYSTIMES_PROCESSTIME = 'systimes.processtime'

# Choose platform default timer
jeżeli hasattr(time, 'perf_counter'):
    TIMER_PLATFORM_DEFAULT = TIMER_TIME_PERF_COUNTER
albo_inaczej sys.platform[:3] == 'win':
    # On WinXP this has 2.5ms resolution
    TIMER_PLATFORM_DEFAULT = TIMER_TIME_CLOCK
inaczej:
    # On Linux this has 1ms resolution
    TIMER_PLATFORM_DEFAULT = TIMER_TIME_TIME

# Print debug information ?
_debug = 0

### Helpers

def get_timer(timertype):

    jeżeli timertype == TIMER_TIME_TIME:
        zwróć time.time
    albo_inaczej timertype == TIMER_TIME_PROCESS_TIME:
        zwróć time.process_time
    albo_inaczej timertype == TIMER_TIME_PERF_COUNTER:
        zwróć time.perf_counter
    albo_inaczej timertype == TIMER_TIME_CLOCK:
        zwróć time.clock
    albo_inaczej timertype == TIMER_SYSTIMES_PROCESSTIME:
        zaimportuj systimes
        zwróć systimes.processtime
    inaczej:
        podnieś TypeError('unknown timer type: %s' % timertype)

def get_machine_details():

    jeżeli _debug:
        print('Getting machine details...')
    buildno, builddate = platform.python_build()
    python = platform.python_version()
    # XXX this jest now always UCS4, maybe replace it przy 'PEP393' w 3.3+?
    jeżeli sys.maxunicode == 65535:
        # UCS2 build (standard)
        unitype = 'UCS2'
    inaczej:
        # UCS4 build (most recent Linux distros)
        unitype = 'UCS4'
    bits, linkage = platform.architecture()
    zwróć {
        'platform': platform.platform(),
        'processor': platform.processor(),
        'executable': sys.executable,
        'implementation': getattr(platform, 'python_implementation',
                                  lambda:'n/a')(),
        'python': platform.python_version(),
        'compiler': platform.python_compiler(),
        'buildno': buildno,
        'builddate': builddate,
        'unicode': unitype,
        'bits': bits,
        }

def print_machine_details(d, indent=''):

    l = ['Machine Details:',
         '   Platform ID:    %s' % d.get('platform', 'n/a'),
         '   Processor:      %s' % d.get('processor', 'n/a'),
         '',
         'Python:',
         '   Implementation: %s' % d.get('implementation', 'n/a'),
         '   Executable:     %s' % d.get('executable', 'n/a'),
         '   Version:        %s' % d.get('python', 'n/a'),
         '   Compiler:       %s' % d.get('compiler', 'n/a'),
         '   Bits:           %s' % d.get('bits', 'n/a'),
         '   Build:          %s (#%s)' % (d.get('builddate', 'n/a'),
                                          d.get('buildno', 'n/a')),
         '   Unicode:        %s' % d.get('unicode', 'n/a'),
         ]
    joiner = '\n' + indent
    print(indent + joiner.join(l) + '\n')

### Test baseclass

klasa Test:

    """ All test must have this klasa jako baseclass. It provides
        the necessary interface to the benchmark machinery.

        The tests must set .rounds to a value high enough to let the
        test run between 20-50 seconds. This jest needed because
        clock()-timing only gives rather inaccurate values (on Linux,
        dla example, it jest accurate to a few hundreths of a
        second). If you don't want to wait that long, use a warp
        factor larger than 1.

        It jest also important to set the .operations variable to a
        value representing the number of "virtual operations" done per
        call of .run().

        If you change a test w some way, don't forget to increase
        its version number.

    """

    ### Instance variables that each test should override

    # Version number of the test jako float (x.yy); this jest important
    # dla comparisons of benchmark runs - tests przy unequal version
    # number will nie get compared.
    version = 2.1

    # The number of abstract operations done w each round of the
    # test. An operation jest the basic unit of what you want to
    # measure. The benchmark will output the amount of run-time per
    # operation. Note that w order to podnieś the measured timings
    # significantly above noise level, it jest often required to repeat
    # sets of operations more than once per test round. The measured
    # overhead per test round should be less than 1 second.
    operations = 1

    # Number of rounds to execute per test run. This should be
    # adjusted to a figure that results w a test run-time of between
    # 1-2 seconds.
    rounds = 100000

    ### Internal variables

    # Mark this klasa jako implementing a test
    is_a_test = 1

    # Last timing: (real, run, overhead)
    last_timing = (0.0, 0.0, 0.0)

    # Warp factor to use dla this test
    warp = 1

    # Number of calibration runs to use
    calibration_runs = CALIBRATION_RUNS

    # List of calibration timings
    overhead_times = Nic

    # List of test run timings
    times = []

    # Timer used dla the benchmark
    timer = TIMER_PLATFORM_DEFAULT

    def __init__(self, warp=Nic, calibration_runs=Nic, timer=Nic):

        # Set parameters
        jeżeli warp jest nie Nic:
            self.rounds = int(self.rounds / warp)
            jeżeli self.rounds == 0:
                podnieś ValueError('warp factor set too high')
            self.warp = warp
        jeżeli calibration_runs jest nie Nic:
            jeżeli (nie ALLOW_SKIPPING_CALIBRATION oraz
                calibration_runs < 1):
                podnieś ValueError('at least one calibration run jest required')
            self.calibration_runs = calibration_runs
        jeżeli timer jest nie Nic:
            self.timer = timer

        # Init variables
        self.times = []
        self.overhead_times = []

        # We want these to be w the instance dict, so that pickle
        # saves them
        self.version = self.version
        self.operations = self.operations
        self.rounds = self.rounds

    def get_timer(self):

        """ Return the timer function to use dla the test.

        """
        zwróć get_timer(self.timer)

    def compatible(self, other):

        """ Return 1/0 depending on whether the test jest compatible
            przy the other Test instance albo not.

        """
        jeżeli self.version != other.version:
            zwróć 0
        jeżeli self.rounds != other.rounds:
            zwróć 0
        zwróć 1

    def calibrate_test(self):

        jeżeli self.calibration_runs == 0:
            self.overhead_times = [0.0]
            zwróć

        calibrate = self.calibrate
        timer = self.get_timer()
        calibration_loops = range(CALIBRATION_LOOPS)

        # Time the calibration loop overhead
        prep_times = []
        dla i w range(self.calibration_runs):
            t = timer()
            dla i w calibration_loops:
                dalej
            t = timer() - t
            prep_times.append(t / CALIBRATION_LOOPS)
        min_prep_time = min(prep_times)
        jeżeli _debug:
            print()
            print('Calib. prep time     = %.6fms' % (
                min_prep_time * MILLI_SECONDS))

        # Time the calibration runs (doing CALIBRATION_LOOPS loops of
        # .calibrate() method calls each)
        dla i w range(self.calibration_runs):
            t = timer()
            dla i w calibration_loops:
                calibrate()
            t = timer() - t
            self.overhead_times.append(t / CALIBRATION_LOOPS
                                       - min_prep_time)

        # Check the measured times
        min_overhead = min(self.overhead_times)
        max_overhead = max(self.overhead_times)
        jeżeli _debug:
            print('Calib. overhead time = %.6fms' % (
                min_overhead * MILLI_SECONDS))
        jeżeli min_overhead < 0.0:
            podnieś ValueError('calibration setup did nie work')
        jeżeli max_overhead - min_overhead > 0.1:
            podnieś ValueError(
                'overhead calibration timing range too inaccurate: '
                '%r - %r' % (min_overhead, max_overhead))

    def run(self):

        """ Run the test w two phases: first calibrate, then
            do the actual test. Be careful to keep the calibration
            timing low w/r to the test timing.

        """
        test = self.test
        timer = self.get_timer()

        # Get calibration
        min_overhead = min(self.overhead_times)

        # Test run
        t = timer()
        test()
        t = timer() - t
        jeżeli t < MIN_TEST_RUNTIME:
            podnieś ValueError('warp factor too high: '
                             'test times are < 10ms')
        eff_time = t - min_overhead
        jeżeli eff_time < 0:
            podnieś ValueError('wrong calibration')
        self.last_timing = (eff_time, t, min_overhead)
        self.times.append(eff_time)

    def calibrate(self):

        """ Calibrate the test.

            This method should execute everything that jest needed to
            setup oraz run the test - wyjąwszy dla the actual operations
            that you intend to measure. pybench uses this method to
            measure the test implementation overhead.

        """
        zwróć

    def test(self):

        """ Run the test.

            The test needs to run self.rounds executing
            self.operations number of operations each.

        """
        zwróć

    def stat(self):

        """ Return test run statistics jako tuple:

            (minimum run time,
             average run time,
             total run time,
             average time per operation,
             minimum overhead time)

        """
        runs = len(self.times)
        jeżeli runs == 0:
            zwróć 0.0, 0.0, 0.0, 0.0
        min_time = min(self.times)
        total_time = sum(self.times)
        avg_time = total_time / float(runs)
        operation_avg = total_time / float(runs
                                           * self.rounds
                                           * self.operations)
        jeżeli self.overhead_times:
            min_overhead = min(self.overhead_times)
        inaczej:
            min_overhead = self.last_timing[2]
        zwróć min_time, avg_time, total_time, operation_avg, min_overhead

### Load Setup

# This has to be done after the definition of the Test class, since
# the Setup module will zaimportuj subclasses using this class.

zaimportuj Setup

### Benchmark base class

klasa Benchmark:

    # Name of the benchmark
    name = ''

    # Number of benchmark rounds to run
    rounds = 1

    # Warp factor use to run the tests
    warp = 1                    # Warp factor

    # Average benchmark round time
    roundtime = 0

    # Benchmark version number jako float x.yy
    version = 2.1

    # Produce verbose output ?
    verbose = 0

    # Dictionary przy the machine details
    machine_details = Nic

    # Timer used dla the benchmark
    timer = TIMER_PLATFORM_DEFAULT

    def __init__(self, name, verbose=Nic, timer=Nic, warp=Nic,
                 calibration_runs=Nic):

        jeżeli name:
            self.name = name
        inaczej:
            self.name = '%04i-%02i-%02i %02i:%02i:%02i' % \
                        (time.localtime(time.time())[:6])
        jeżeli verbose jest nie Nic:
            self.verbose = verbose
        jeżeli timer jest nie Nic:
            self.timer = timer
        jeżeli warp jest nie Nic:
            self.warp = warp
        jeżeli calibration_runs jest nie Nic:
            self.calibration_runs = calibration_runs

        # Init vars
        self.tests = {}
        jeżeli _debug:
            print('Getting machine details...')
        self.machine_details = get_machine_details()

        # Make .version an instance attribute to have it saved w the
        # Benchmark pickle
        self.version = self.version

    def get_timer(self):

        """ Return the timer function to use dla the test.

        """
        zwróć get_timer(self.timer)

    def compatible(self, other):

        """ Return 1/0 depending on whether the benchmark jest
            compatible przy the other Benchmark instance albo not.

        """
        jeżeli self.version != other.version:
            zwróć 0
        jeżeli (self.machine_details == other.machine_details oraz
            self.timer != other.timer):
            zwróć 0
        jeżeli (self.calibration_runs == 0 oraz
            other.calibration_runs != 0):
            zwróć 0
        jeżeli (self.calibration_runs != 0 oraz
            other.calibration_runs == 0):
            zwróć 0
        zwróć 1

    def load_tests(self, setupmod, limitnames=Nic):

        # Add tests
        jeżeli self.verbose:
            print('Searching dla tests ...')
            print('--------------------------------------')
        dla testclass w setupmod.__dict__.values():
            jeżeli nie hasattr(testclass, 'is_a_test'):
                kontynuuj
            name = testclass.__name__
            jeżeli  name == 'Test':
                kontynuuj
            jeżeli (limitnames jest nie Nic oraz
                limitnames.search(name) jest Nic):
                kontynuuj
            self.tests[name] = testclass(
                warp=self.warp,
                calibration_runs=self.calibration_runs,
                timer=self.timer)
        l = sorted(self.tests)
        jeżeli self.verbose:
            dla name w l:
                print('  %s' % name)
            print('--------------------------------------')
            print('  %i tests found' % len(l))
            print()

    def calibrate(self):

        print('Calibrating tests. Please wait...', end=' ')
        sys.stdout.flush()
        jeżeli self.verbose:
            print()
            print()
            print('Test                              min      max')
            print('-' * LINE)
        tests = sorted(self.tests.items())
        dla i w range(len(tests)):
            name, test = tests[i]
            test.calibrate_test()
            jeżeli self.verbose:
                print('%30s:  %6.3fms  %6.3fms' % \
                      (name,
                       min(test.overhead_times) * MILLI_SECONDS,
                       max(test.overhead_times) * MILLI_SECONDS))
        jeżeli self.verbose:
            print()
            print('Done przy the calibration.')
        inaczej:
            print('done.')
        print()

    def run(self):

        tests = sorted(self.tests.items())
        timer = self.get_timer()
        print('Running %i round(s) of the suite at warp factor %i:' % \
              (self.rounds, self.warp))
        print()
        self.roundtimes = []
        dla i w range(self.rounds):
            jeżeli self.verbose:
                print(' Round %-25i  effective   absolute  overhead' % (i+1))
            total_eff_time = 0.0
            dla j w range(len(tests)):
                name, test = tests[j]
                jeżeli self.verbose:
                    print('%30s:' % name, end=' ')
                test.run()
                (eff_time, abs_time, min_overhead) = test.last_timing
                total_eff_time = total_eff_time + eff_time
                jeżeli self.verbose:
                    print('    %5.0fms    %5.0fms %7.3fms' % \
                          (eff_time * MILLI_SECONDS,
                           abs_time * MILLI_SECONDS,
                           min_overhead * MILLI_SECONDS))
            self.roundtimes.append(total_eff_time)
            jeżeli self.verbose:
                print('                   '
                       '               ------------------------------')
                print('                   '
                       '     Totals:    %6.0fms' %
                       (total_eff_time * MILLI_SECONDS))
                print()
            inaczej:
                print('* Round %i done w %.3f seconds.' % (i+1,
                                                            total_eff_time))
        print()

    def stat(self):

        """ Return benchmark run statistics jako tuple:

            (minimum round time,
             average round time,
             maximum round time)

            XXX Currently nie used, since the benchmark does test
                statistics across all rounds.

        """
        runs = len(self.roundtimes)
        jeżeli runs == 0:
            zwróć 0.0, 0.0
        min_time = min(self.roundtimes)
        total_time = sum(self.roundtimes)
        avg_time = total_time / float(runs)
        max_time = max(self.roundtimes)
        zwróć (min_time, avg_time, max_time)

    def print_header(self, title='Benchmark'):

        print('-' * LINE)
        print('%s: %s' % (title, self.name))
        print('-' * LINE)
        print()
        print('    Rounds: %s' % self.rounds)
        print('    Warp:   %s' % self.warp)
        print('    Timer:  %s' % self.timer)
        print()
        jeżeli self.machine_details:
            print_machine_details(self.machine_details, indent='    ')
            print()

    def print_benchmark(self, hidenoise=0, limitnames=Nic):

        print('Test                          '
               '   minimum  average  operation  overhead')
        print('-' * LINE)
        tests = sorted(self.tests.items())
        total_min_time = 0.0
        total_avg_time = 0.0
        dla name, test w tests:
            jeżeli (limitnames jest nie Nic oraz
                limitnames.search(name) jest Nic):
                kontynuuj
            (min_time,
             avg_time,
             total_time,
             op_avg,
             min_overhead) = test.stat()
            total_min_time = total_min_time + min_time
            total_avg_time = total_avg_time + avg_time
            print('%30s:  %5.0fms  %5.0fms  %6.2fus  %7.3fms' % \
                  (name,
                   min_time * MILLI_SECONDS,
                   avg_time * MILLI_SECONDS,
                   op_avg * MICRO_SECONDS,
                   min_overhead *MILLI_SECONDS))
        print('-' * LINE)
        print('Totals:                        '
               ' %6.0fms %6.0fms' %
               (total_min_time * MILLI_SECONDS,
                total_avg_time * MILLI_SECONDS,
                ))
        print()

    def print_comparison(self, compare_to, hidenoise=0, limitnames=Nic):

        # Check benchmark versions
        jeżeli compare_to.version != self.version:
            print('* Benchmark versions differ: '
                   'cannot compare this benchmark to "%s" !' %
                   compare_to.name)
            print()
            self.print_benchmark(hidenoise=hidenoise,
                                 limitnames=limitnames)
            zwróć

        # Print header
        compare_to.print_header('Comparing with')
        print('Test                          '
               '   minimum run-time        average  run-time')
        print('                              '
               '   this    other   diff    this    other   diff')
        print('-' * LINE)

        # Print test comparisons
        tests = sorted(self.tests.items())
        total_min_time = other_total_min_time = 0.0
        total_avg_time = other_total_avg_time = 0.0
        benchmarks_compatible = self.compatible(compare_to)
        tests_compatible = 1
        dla name, test w tests:
            jeżeli (limitnames jest nie Nic oraz
                limitnames.search(name) jest Nic):
                kontynuuj
            (min_time,
             avg_time,
             total_time,
             op_avg,
             min_overhead) = test.stat()
            total_min_time = total_min_time + min_time
            total_avg_time = total_avg_time + avg_time
            spróbuj:
                other = compare_to.tests[name]
            wyjąwszy KeyError:
                other = Nic
            jeżeli other jest Nic:
                # Other benchmark doesn't include the given test
                min_diff, avg_diff = 'n/a', 'n/a'
                other_min_time = 0.0
                other_avg_time = 0.0
                tests_compatible = 0
            inaczej:
                (other_min_time,
                 other_avg_time,
                 other_total_time,
                 other_op_avg,
                 other_min_overhead) = other.stat()
                other_total_min_time = other_total_min_time + other_min_time
                other_total_avg_time = other_total_avg_time + other_avg_time
                jeżeli (benchmarks_compatible oraz
                    test.compatible(other)):
                    # Both benchmark oraz tests are comparable
                    min_diff = ((min_time * self.warp) /
                                (other_min_time * other.warp) - 1.0)
                    avg_diff = ((avg_time * self.warp) /
                                (other_avg_time * other.warp) - 1.0)
                    jeżeli hidenoise oraz abs(min_diff) < 10.0:
                        min_diff = ''
                    inaczej:
                        min_diff = '%+5.1f%%' % (min_diff * PERCENT)
                    jeżeli hidenoise oraz abs(avg_diff) < 10.0:
                        avg_diff = ''
                    inaczej:
                        avg_diff = '%+5.1f%%' % (avg_diff * PERCENT)
                inaczej:
                    # Benchmark albo tests are nie comparable
                    min_diff, avg_diff = 'n/a', 'n/a'
                    tests_compatible = 0
            print('%30s: %5.0fms %5.0fms %7s %5.0fms %5.0fms %7s' % \
                  (name,
                   min_time * MILLI_SECONDS,
                   other_min_time * MILLI_SECONDS * compare_to.warp / self.warp,
                   min_diff,
                   avg_time * MILLI_SECONDS,
                   other_avg_time * MILLI_SECONDS * compare_to.warp / self.warp,
                   avg_diff))
        print('-' * LINE)

        # Summarise test results
        jeżeli nie benchmarks_compatible albo nie tests_compatible:
            min_diff, avg_diff = 'n/a', 'n/a'
        inaczej:
            jeżeli other_total_min_time != 0.0:
                min_diff = '%+5.1f%%' % (
                    ((total_min_time * self.warp) /
                     (other_total_min_time * compare_to.warp) - 1.0) * PERCENT)
            inaczej:
                min_diff = 'n/a'
            jeżeli other_total_avg_time != 0.0:
                avg_diff = '%+5.1f%%' % (
                    ((total_avg_time * self.warp) /
                     (other_total_avg_time * compare_to.warp) - 1.0) * PERCENT)
            inaczej:
                avg_diff = 'n/a'
        print('Totals:                       '
               '  %5.0fms %5.0fms %7s %5.0fms %5.0fms %7s' %
               (total_min_time * MILLI_SECONDS,
                (other_total_min_time * compare_to.warp/self.warp
                 * MILLI_SECONDS),
                min_diff,
                total_avg_time * MILLI_SECONDS,
                (other_total_avg_time * compare_to.warp/self.warp
                 * MILLI_SECONDS),
                avg_diff
               ))
        print()
        print('(this=%s, other=%s)' % (self.name,
                                       compare_to.name))
        print()

klasa PyBenchCmdline(Application):

    header = ("PYBENCH - a benchmark test suite dla Python "
              "interpreters/compilers.")

    version = __version__

    debug = _debug

    options = [ArgumentOption('-n',
                              'number of rounds',
                              Setup.Number_of_rounds),
               ArgumentOption('-f',
                              'save benchmark to file arg',
                              ''),
               ArgumentOption('-c',
                              'compare benchmark przy the one w file arg',
                              ''),
               ArgumentOption('-s',
                              'show benchmark w file arg, then exit',
                              ''),
               ArgumentOption('-w',
                              'set warp factor to arg',
                              Setup.Warp_factor),
               ArgumentOption('-t',
                              'run only tests przy names matching arg',
                              ''),
               ArgumentOption('-C',
                              'set the number of calibration runs to arg',
                              CALIBRATION_RUNS),
               SwitchOption('-d',
                            'hide noise w comparisons',
                            0),
               SwitchOption('-v',
                            'verbose output (nie recommended)',
                            0),
               SwitchOption('--with-gc',
                            'enable garbage collection',
                            0),
               SwitchOption('--with-syscheck',
                            'use default sys check interval',
                            0),
               ArgumentOption('--timer',
                            'use given timer',
                            TIMER_PLATFORM_DEFAULT),
               ]

    about = """\
The normal operation jest to run the suite oraz display the
results. Use -f to save them dla later reuse albo comparisons.

Available timers:

   time.time
   time.clock
   systimes.processtime

Examples:

python2.1 pybench.py -f p21.pybench
python2.5 pybench.py -f p25.pybench
python pybench.py -s p25.pybench -c p21.pybench
"""
    copyright = __copyright__

    def main(self):

        rounds = self.values['-n']
        reportfile = self.values['-f']
        show_bench = self.values['-s']
        compare_to = self.values['-c']
        hidenoise = self.values['-d']
        warp = int(self.values['-w'])
        withgc = self.values['--with-gc']
        limitnames = self.values['-t']
        jeżeli limitnames:
            jeżeli _debug:
                print('* limiting test names to one przy substring "%s"' % \
                      limitnames)
            limitnames = re.compile(limitnames, re.I)
        inaczej:
            limitnames = Nic
        verbose = self.verbose
        withsyscheck = self.values['--with-syscheck']
        calibration_runs = self.values['-C']
        timer = self.values['--timer']

        print('-' * LINE)
        print('PYBENCH %s' % __version__)
        print('-' * LINE)
        print('* using %s %s' % (
            getattr(platform, 'python_implementation', lambda:'Python')(),
            ' '.join(sys.version.split())))

        # Switch off garbage collection
        jeżeli nie withgc:
            spróbuj:
                zaimportuj gc
            wyjąwszy ImportError:
                print('* Python version doesn\'t support garbage collection')
            inaczej:
                spróbuj:
                    gc.disable()
                wyjąwszy NotImplementedError:
                    print('* Python version doesn\'t support gc.disable')
                inaczej:
                    print('* disabled garbage collection')

        # "Disable" sys check interval
        jeżeli nie withsyscheck:
            # Too bad the check interval uses an int instead of a long...
            value = 2147483647
            spróbuj:
                sys.setcheckinterval(value)
            wyjąwszy (AttributeError, NotImplementedError):
                print('* Python version doesn\'t support sys.setcheckinterval')
            inaczej:
                print('* system check interval set to maximum: %s' % value)

        jeżeli timer == TIMER_SYSTIMES_PROCESSTIME:
            zaimportuj systimes
            print('* using timer: systimes.processtime (%s)' % \
                  systimes.SYSTIMES_IMPLEMENTATION)
        inaczej:
            # Check that the clock function does exist
            spróbuj:
                get_timer(timer)
            wyjąwszy TypeError:
                print("* Error: Unknown timer: %s" % timer)
                zwróć

            print('* using timer: %s' % timer)
            jeżeli hasattr(time, 'get_clock_info'):
                info = time.get_clock_info(timer[5:])
                print('* timer: resolution=%s, implementation=%s'
                      % (info.resolution, info.implementation))

        print()

        jeżeli compare_to:
            spróbuj:
                f = open(compare_to,'rb')
                bench = pickle.load(f)
                bench.name = compare_to
                f.close()
                compare_to = bench
            wyjąwszy IOError jako reason:
                print('* Error opening/reading file %s: %s' % (
                    repr(compare_to),
                    reason))
                compare_to = Nic

        jeżeli show_bench:
            spróbuj:
                f = open(show_bench,'rb')
                bench = pickle.load(f)
                bench.name = show_bench
                f.close()
                bench.print_header()
                jeżeli compare_to:
                    bench.print_comparison(compare_to,
                                           hidenoise=hidenoise,
                                           limitnames=limitnames)
                inaczej:
                    bench.print_benchmark(hidenoise=hidenoise,
                                          limitnames=limitnames)
            wyjąwszy IOError jako reason:
                print('* Error opening/reading file %s: %s' % (
                    repr(show_bench),
                    reason))
                print()
            zwróć

        jeżeli reportfile:
            print('Creating benchmark: %s (rounds=%i, warp=%i)' % \
                  (reportfile, rounds, warp))
            print()

        # Create benchmark object
        bench = Benchmark(reportfile,
                          verbose=verbose,
                          timer=timer,
                          warp=warp,
                          calibration_runs=calibration_runs)
        bench.rounds = rounds
        bench.load_tests(Setup, limitnames=limitnames)
        spróbuj:
            bench.calibrate()
            bench.run()
        wyjąwszy KeyboardInterrupt:
            print()
            print('*** KeyboardInterrupt -- Aborting')
            print()
            zwróć
        bench.print_header()
        jeżeli compare_to:
            bench.print_comparison(compare_to,
                                   hidenoise=hidenoise,
                                   limitnames=limitnames)
        inaczej:
            bench.print_benchmark(hidenoise=hidenoise,
                                  limitnames=limitnames)

        # Ring bell
        sys.stderr.write('\007')

        jeżeli reportfile:
            spróbuj:
                f = open(reportfile,'wb')
                bench.name = reportfile
                pickle.dump(bench,f)
                f.close()
            wyjąwszy IOError jako reason:
                print('* Error opening/writing reportfile %s: %s' % (
                    reportfile,
                    reason))
                print()

jeżeli __name__ == '__main__':
    PyBenchCmdline()
