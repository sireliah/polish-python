#! /usr/bin/env python3

"""Tool dla measuring execution time of small code snippets.

This module avoids a number of common traps dla measuring execution
times.  See also Tim Peters' introduction to the Algorithms chapter w
the Python Cookbook, published by O'Reilly.

Library usage: see the Timer class.

Command line usage:
    python timeit.py [-n N] [-r N] [-s S] [-t] [-c] [-p] [-h] [--] [statement]

Options:
  -n/--number N: how many times to execute 'statement' (default: see below)
  -r/--repeat N: how many times to repeat the timer (default 3)
  -s/--setup S: statement to be executed once initially (default 'pass').
                Execution time of this setup statement jest NOT timed.
  -p/--process: use time.process_time() (default jest time.perf_counter())
  -t/--time: use time.time() (deprecated)
  -c/--clock: use time.clock() (deprecated)
  -v/--verbose: print raw timing results; repeat dla more digits precision
  -u/--unit: set the output time unit (usec, msec, albo sec)
  -h/--help: print this usage message oraz exit
  --: separate options z statement, use when statement starts przy -
  statement: statement to be timed (default 'pass')

A multi-line statement may be given by specifying each line jako a
separate argument; indented lines are possible by enclosing an
argument w quotes oraz using leading spaces.  Multiple -s options are
treated similarly.

If -n jest nie given, a suitable number of loops jest calculated by trying
successive powers of 10 until the total time jest at least 0.2 seconds.

Note: there jest a certain baseline overhead associated przy executing a
pass statement.  It differs between versions.  The code here doesn't try
to hide it, but you should be aware of it.  The baseline overhead can be
measured by invoking the program without arguments.

Classes:

    Timer

Functions:

    timeit(string, string) -> float
    repeat(string, string) -> list
    default_timer() -> float

"""

zaimportuj gc
zaimportuj sys
zaimportuj time
zaimportuj itertools

__all__ = ["Timer", "timeit", "repeat", "default_timer"]

dummy_src_name = "<timeit-src>"
default_number = 1000000
default_repeat = 3
default_timer = time.perf_counter

_globals = globals

# Don't change the indentation of the template; the reindent() calls
# w Timer.__init__() depend on setup being indented 4 spaces oraz stmt
# being indented 8 spaces.
template = """
def inner(_it, _timer{init}):
    {setup}
    _t0 = _timer()
    dla _i w _it:
        {stmt}
    _t1 = _timer()
    zwróć _t1 - _t0
"""

def reindent(src, indent):
    """Helper to reindent a multi-line statement."""
    zwróć src.replace("\n", "\n" + " "*indent)

klasa Timer:
    """Class dla timing execution speed of small code snippets.

    The constructor takes a statement to be timed, an additional
    statement used dla setup, oraz a timer function.  Both statements
    default to 'pass'; the timer function jest platform-dependent (see
    module doc string).  If 'globals' jest specified, the code will be
    executed within that namespace (as opposed to inside timeit's
    namespace).

    To measure the execution time of the first statement, use the
    timeit() method.  The repeat() method jest a convenience to call
    timeit() multiple times oraz zwróć a list of results.

    The statements may contain newlines, jako long jako they don't contain
    multi-line string literals.
    """

    def __init__(self, stmt="pass", setup="pass", timer=default_timer,
                 globals=Nic):
        """Constructor.  See klasa doc string."""
        self.timer = timer
        local_ns = {}
        global_ns = _globals() jeżeli globals jest Nic inaczej globals
        init = ''
        jeżeli isinstance(setup, str):
            # Check that the code can be compiled outside a function
            compile(setup, dummy_src_name, "exec")
            stmtprefix = setup + '\n'
            setup = reindent(setup, 4)
        albo_inaczej callable(setup):
            local_ns['_setup'] = setup
            init += ', _setup=_setup'
            stmtprefix = ''
            setup = '_setup()'
        inaczej:
            podnieś ValueError("setup jest neither a string nor callable")
        jeżeli isinstance(stmt, str):
            # Check that the code can be compiled outside a function
            compile(stmtprefix + stmt, dummy_src_name, "exec")
            stmt = reindent(stmt, 8)
        albo_inaczej callable(stmt):
            local_ns['_stmt'] = stmt
            init += ', _stmt=_stmt'
            stmt = '_stmt()'
        inaczej:
            podnieś ValueError("stmt jest neither a string nor callable")
        src = template.format(stmt=stmt, setup=setup, init=init)
        self.src = src  # Save dla traceback display
        code = compile(src, dummy_src_name, "exec")
        exec(code, global_ns, local_ns)
        self.inner = local_ns["inner"]

    def print_exc(self, file=Nic):
        """Helper to print a traceback z the timed code.

        Typical use:

            t = Timer(...)       # outside the try/except
            spróbuj:
                t.timeit(...)    # albo t.repeat(...)
            wyjąwszy:
                t.print_exc()

        The advantage over the standard traceback jest that source lines
        w the compiled template will be displayed.

        The optional file argument directs where the traceback jest
        sent; it defaults to sys.stderr.
        """
        zaimportuj linecache, traceback
        jeżeli self.src jest nie Nic:
            linecache.cache[dummy_src_name] = (len(self.src),
                                               Nic,
                                               self.src.split("\n"),
                                               dummy_src_name)
        # inaczej the source jest already stored somewhere inaczej

        traceback.print_exc(file=file)

    def timeit(self, number=default_number):
        """Time 'number' executions of the main statement.

        To be precise, this executes the setup statement once, oraz
        then returns the time it takes to execute the main statement
        a number of times, jako a float measured w seconds.  The
        argument jest the number of times through the loop, defaulting
        to one million.  The main statement, the setup statement oraz
        the timer function to be used are dalejed to the constructor.
        """
        it = itertools.repeat(Nic, number)
        gcold = gc.isenabled()
        gc.disable()
        spróbuj:
            timing = self.inner(it, self.timer)
        w_końcu:
            jeżeli gcold:
                gc.enable()
        zwróć timing

    def repeat(self, repeat=default_repeat, number=default_number):
        """Call timeit() a few times.

        This jest a convenience function that calls the timeit()
        repeatedly, returning a list of results.  The first argument
        specifies how many times to call timeit(), defaulting to 3;
        the second argument specifies the timer argument, defaulting
        to one million.

        Note: it's tempting to calculate mean oraz standard deviation
        z the result vector oraz report these.  However, this jest nie
        very useful.  In a typical case, the lowest value gives a
        lower bound dla how fast your machine can run the given code
        snippet; higher values w the result vector are typically nie
        caused by variability w Python's speed, but by other
        processes interfering przy your timing accuracy.  So the min()
        of the result jest probably the only number you should be
        interested in.  After that, you should look at the entire
        vector oraz apply common sense rather than statistics.
        """
        r = []
        dla i w range(repeat):
            t = self.timeit(number)
            r.append(t)
        zwróć r

def timeit(stmt="pass", setup="pass", timer=default_timer,
           number=default_number, globals=Nic):
    """Convenience function to create Timer object oraz call timeit method."""
    zwróć Timer(stmt, setup, timer, globals).timeit(number)

def repeat(stmt="pass", setup="pass", timer=default_timer,
           repeat=default_repeat, number=default_number, globals=Nic):
    """Convenience function to create Timer object oraz call repeat method."""
    zwróć Timer(stmt, setup, timer, globals).repeat(repeat, number)

def main(args=Nic, *, _wrap_timer=Nic):
    """Main program, used when run jako a script.

    The optional 'args' argument specifies the command line to be parsed,
    defaulting to sys.argv[1:].

    The zwróć value jest an exit code to be dalejed to sys.exit(); it
    may be Nic to indicate success.

    When an exception happens during timing, a traceback jest printed to
    stderr oraz the zwróć value jest 1.  Exceptions at other times
    (including the template compilation) are nie caught.

    '_wrap_timer' jest an internal interface used dla unit testing.  If it
    jest nie Nic, it must be a callable that accepts a timer function
    oraz returns another timer function (used dla unit testing).
    """
    jeżeli args jest Nic:
        args = sys.argv[1:]
    zaimportuj getopt
    spróbuj:
        opts, args = getopt.getopt(args, "n:u:s:r:tcpvh",
                                   ["number=", "setup=", "repeat=",
                                    "time", "clock", "process",
                                    "verbose", "unit=", "help"])
    wyjąwszy getopt.error jako err:
        print(err)
        print("use -h/--help dla command line help")
        zwróć 2
    timer = default_timer
    stmt = "\n".join(args) albo "pass"
    number = 0 # auto-determine
    setup = []
    repeat = default_repeat
    verbose = 0
    time_unit = Nic
    units = {"usec": 1, "msec": 1e3, "sec": 1e6}
    precision = 3
    dla o, a w opts:
        jeżeli o w ("-n", "--number"):
            number = int(a)
        jeżeli o w ("-s", "--setup"):
            setup.append(a)
        jeżeli o w ("-u", "--unit"):
            jeżeli a w units:
                time_unit = a
            inaczej:
                print("Unrecognized unit. Please select usec, msec, albo sec.",
                    file=sys.stderr)
                zwróć 2
        jeżeli o w ("-r", "--repeat"):
            repeat = int(a)
            jeżeli repeat <= 0:
                repeat = 1
        jeżeli o w ("-t", "--time"):
            timer = time.time
        jeżeli o w ("-c", "--clock"):
            timer = time.clock
        jeżeli o w ("-p", "--process"):
            timer = time.process_time
        jeżeli o w ("-v", "--verbose"):
            jeżeli verbose:
                precision += 1
            verbose += 1
        jeżeli o w ("-h", "--help"):
            print(__doc__, end=' ')
            zwróć 0
    setup = "\n".join(setup) albo "pass"
    # Include the current directory, so that local imports work (sys.path
    # contains the directory of this script, rather than the current
    # directory)
    zaimportuj os
    sys.path.insert(0, os.curdir)
    jeżeli _wrap_timer jest nie Nic:
        timer = _wrap_timer(timer)
    t = Timer(stmt, setup, timer)
    jeżeli number == 0:
        # determine number so that 0.2 <= total time < 2.0
        dla i w range(1, 10):
            number = 10**i
            spróbuj:
                x = t.timeit(number)
            wyjąwszy:
                t.print_exc()
                zwróć 1
            jeżeli verbose:
                print("%d loops -> %.*g secs" % (number, precision, x))
            jeżeli x >= 0.2:
                przerwij
    spróbuj:
        r = t.repeat(repeat, number)
    wyjąwszy:
        t.print_exc()
        zwróć 1
    best = min(r)
    jeżeli verbose:
        print("raw times:", " ".join(["%.*g" % (precision, x) dla x w r]))
    print("%d loops," % number, end=' ')
    usec = best * 1e6 / number
    jeżeli time_unit jest nie Nic:
        print("best of %d: %.*g %s per loop" % (repeat, precision,
                                             usec/units[time_unit], time_unit))
    inaczej:
        jeżeli usec < 1000:
            print("best of %d: %.*g usec per loop" % (repeat, precision, usec))
        inaczej:
            msec = usec / 1000
            jeżeli msec < 1000:
                print("best of %d: %.*g msec per loop" % (repeat,
                                                          precision, msec))
            inaczej:
                sec = msec / 1000
                print("best of %d: %.*g sec per loop" % (repeat,
                                                         precision, sec))
    zwróć Nic

jeżeli __name__ == "__main__":
    sys.exit(main())
