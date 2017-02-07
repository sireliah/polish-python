#! /usr/bin/env python3
#
# Class dla profiling python code. rev 1.0  6/2/94
#
# Written by James Roskind
# Based on prior profile module by Sjoerd Mullender...
#   which was hacked somewhat by: Guido van Rossum

"""Class dla profiling Python code."""

# Copyright Disney Enterprises, Inc.  All Rights Reserved.
# Licensed to PSF under a Contributor Agreement
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may nie use this file wyjąwszy w compliance przy the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law albo agreed to w writing, software
# distributed under the License jest distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express albo implied.  See the License dla the specific language
# governing permissions oraz limitations under the License.


zaimportuj sys
zaimportuj os
zaimportuj time
zaimportuj marshal
z optparse zaimportuj OptionParser

__all__ = ["run", "runctx", "Profile"]

# Sample timer dla use with
#i_count = 0
#def integer_timer():
#       global i_count
#       i_count = i_count + 1
#       zwróć i_count
#itimes = integer_timer # replace przy C coded timer returning integers

klasa _Utils:
    """Support klasa dla utility functions which are shared by
    profile.py oraz cProfile.py modules.
    Not supposed to be used directly.
    """

    def __init__(self, profiler):
        self.profiler = profiler

    def run(self, statement, filename, sort):
        prof = self.profiler()
        spróbuj:
            prof.run(statement)
        wyjąwszy SystemExit:
            dalej
        w_końcu:
            self._show(prof, filename, sort)

    def runctx(self, statement, globals, locals, filename, sort):
        prof = self.profiler()
        spróbuj:
            prof.runctx(statement, globals, locals)
        wyjąwszy SystemExit:
            dalej
        w_końcu:
            self._show(prof, filename, sort)

    def _show(self, prof, filename, sort):
        jeżeli filename jest nie Nic:
            prof.dump_stats(filename)
        inaczej:
            prof.print_stats(sort)


#**************************************************************************
# The following are the static member functions dla the profiler class
# Note that an instance of Profile() jest *not* needed to call them.
#**************************************************************************

def run(statement, filename=Nic, sort=-1):
    """Run statement under profiler optionally saving results w filename

    This function takes a single argument that can be dalejed to the
    "exec" statement, oraz an optional file name.  In all cases this
    routine attempts to "exec" its first argument oraz gather profiling
    statistics z the execution. If no file name jest present, then this
    function automatically prints a simple profiling report, sorted by the
    standard name string (file/line/function-name) that jest presented w
    each line.
    """
    zwróć _Utils(Profile).run(statement, filename, sort)

def runctx(statement, globals, locals, filename=Nic, sort=-1):
    """Run statement under profiler, supplying your own globals oraz locals,
    optionally saving results w filename.

    statement oraz filename have the same semantics jako profile.run
    """
    zwróć _Utils(Profile).runctx(statement, globals, locals, filename, sort)


klasa Profile:
    """Profiler class.

    self.cur jest always a tuple.  Each such tuple corresponds to a stack
    frame that jest currently active (self.cur[-2]).  The following are the
    definitions of its members.  We use this external "parallel stack" to
    avoid contaminating the program that we are profiling. (old profiler
    used to write into the frames local dictionary!!) Derived classes
    can change the definition of some entries, jako long jako they leave
    [-2:] intact (frame oraz previous tuple).  In case an internal error jest
    detected, the -3 element jest used jako the function name.

    [ 0] = Time that needs to be charged to the parent frame's function.
           It jest used so that a function call will nie have to access the
           timing data dla the parent frame.
    [ 1] = Total time spent w this frame's function, excluding time w
           subfunctions (this latter jest tallied w cur[2]).
    [ 2] = Total time spent w subfunctions, excluding time executing the
           frame's function (this latter jest tallied w cur[1]).
    [-3] = Name of the function that corresponds to this frame.
    [-2] = Actual frame that we correspond to (used to sync exception handling).
    [-1] = Our parent 6-tuple (corresponds to frame.f_back).

    Timing data dla each function jest stored jako a 5-tuple w the dictionary
    self.timings[].  The index jest always the name stored w self.cur[-3].
    The following are the definitions of the members:

    [0] = The number of times this function was called, nie counting direct
          albo indirect recursion,
    [1] = Number of times this function appears on the stack, minus one
    [2] = Total time spent internal to this function
    [3] = Cumulative time that this function was present on the stack.  In
          non-recursive functions, this jest the total execution time z start
          to finish of each invocation of a function, including time spent w
          all subfunctions.
    [4] = A dictionary indicating dla each function name, the number of times
          it was called by us.
    """

    bias = 0  # calibration constant

    def __init__(self, timer=Nic, bias=Nic):
        self.timings = {}
        self.cur = Nic
        self.cmd = ""
        self.c_func_name = ""

        jeżeli bias jest Nic:
            bias = self.bias
        self.bias = bias     # Materialize w local dict dla lookup speed.

        jeżeli nie timer:
            self.timer = self.get_time = time.process_time
            self.dispatcher = self.trace_dispatch_i
        inaczej:
            self.timer = timer
            t = self.timer() # test out timer function
            spróbuj:
                length = len(t)
            wyjąwszy TypeError:
                self.get_time = timer
                self.dispatcher = self.trace_dispatch_i
            inaczej:
                jeżeli length == 2:
                    self.dispatcher = self.trace_dispatch
                inaczej:
                    self.dispatcher = self.trace_dispatch_l
                # This get_time() implementation needs to be defined
                # here to capture the dalejed-in timer w the parameter
                # list (dla performance).  Note that we can't assume
                # the timer() result contains two values w all
                # cases.
                def get_time_timer(timer=timer, sum=sum):
                    zwróć sum(timer())
                self.get_time = get_time_timer
        self.t = self.get_time()
        self.simulate_call('profiler')

    # Heavily optimized dispatch routine dla os.times() timer

    def trace_dispatch(self, frame, event, arg):
        timer = self.timer
        t = timer()
        t = t[0] + t[1] - self.t - self.bias

        jeżeli event == "c_call":
            self.c_func_name = arg.__name__

        jeżeli self.dispatch[event](self, frame,t):
            t = timer()
            self.t = t[0] + t[1]
        inaczej:
            r = timer()
            self.t = r[0] + r[1] - t # put back unrecorded delta

    # Dispatch routine dla best timer program (return = scalar, fastest if
    # an integer but float works too -- oraz time.clock() relies on that).

    def trace_dispatch_i(self, frame, event, arg):
        timer = self.timer
        t = timer() - self.t - self.bias

        jeżeli event == "c_call":
            self.c_func_name = arg.__name__

        jeżeli self.dispatch[event](self, frame, t):
            self.t = timer()
        inaczej:
            self.t = timer() - t  # put back unrecorded delta

    # Dispatch routine dla macintosh (timer returns time w ticks of
    # 1/60th second)

    def trace_dispatch_mac(self, frame, event, arg):
        timer = self.timer
        t = timer()/60.0 - self.t - self.bias

        jeżeli event == "c_call":
            self.c_func_name = arg.__name__

        jeżeli self.dispatch[event](self, frame, t):
            self.t = timer()/60.0
        inaczej:
            self.t = timer()/60.0 - t  # put back unrecorded delta

    # SLOW generic dispatch routine dla timer returning lists of numbers

    def trace_dispatch_l(self, frame, event, arg):
        get_time = self.get_time
        t = get_time() - self.t - self.bias

        jeżeli event == "c_call":
            self.c_func_name = arg.__name__

        jeżeli self.dispatch[event](self, frame, t):
            self.t = get_time()
        inaczej:
            self.t = get_time() - t # put back unrecorded delta

    # In the event handlers, the first 3 elements of self.cur are unpacked
    # into vrbls w/ 3-letter names.  The last two characters are meant to be
    # mnemonic:
    #     _pt  self.cur[0] "parent time"   time to be charged to parent frame
    #     _it  self.cur[1] "internal time" time spent directly w the function
    #     _et  self.cur[2] "external time" time spent w subfunctions

    def trace_dispatch_exception(self, frame, t):
        rpt, rit, ret, rfn, rframe, rcur = self.cur
        jeżeli (rframe jest nie frame) oraz rcur:
            zwróć self.trace_dispatch_return(rframe, t)
        self.cur = rpt, rit+t, ret, rfn, rframe, rcur
        zwróć 1


    def trace_dispatch_call(self, frame, t):
        jeżeli self.cur oraz frame.f_back jest nie self.cur[-2]:
            rpt, rit, ret, rfn, rframe, rcur = self.cur
            jeżeli nie isinstance(rframe, Profile.fake_frame):
                assert rframe.f_back jest frame.f_back, ("Bad call", rfn,
                                                       rframe, rframe.f_back,
                                                       frame, frame.f_back)
                self.trace_dispatch_return(rframe, 0)
                assert (self.cur jest Nic albo \
                        frame.f_back jest self.cur[-2]), ("Bad call",
                                                        self.cur[-3])
        fcode = frame.f_code
        fn = (fcode.co_filename, fcode.co_firstlineno, fcode.co_name)
        self.cur = (t, 0, 0, fn, frame, self.cur)
        timings = self.timings
        jeżeli fn w timings:
            cc, ns, tt, ct, callers = timings[fn]
            timings[fn] = cc, ns + 1, tt, ct, callers
        inaczej:
            timings[fn] = 0, 0, 0, 0, {}
        zwróć 1

    def trace_dispatch_c_call (self, frame, t):
        fn = ("", 0, self.c_func_name)
        self.cur = (t, 0, 0, fn, frame, self.cur)
        timings = self.timings
        jeżeli fn w timings:
            cc, ns, tt, ct, callers = timings[fn]
            timings[fn] = cc, ns+1, tt, ct, callers
        inaczej:
            timings[fn] = 0, 0, 0, 0, {}
        zwróć 1

    def trace_dispatch_return(self, frame, t):
        jeżeli frame jest nie self.cur[-2]:
            assert frame jest self.cur[-2].f_back, ("Bad return", self.cur[-3])
            self.trace_dispatch_return(self.cur[-2], 0)

        # Prefix "r" means part of the Returning albo exiting frame.
        # Prefix "p" means part of the Previous albo Parent albo older frame.

        rpt, rit, ret, rfn, frame, rcur = self.cur
        rit = rit + t
        frame_total = rit + ret

        ppt, pit, pet, pfn, pframe, pcur = rcur
        self.cur = ppt, pit + rpt, pet + frame_total, pfn, pframe, pcur

        timings = self.timings
        cc, ns, tt, ct, callers = timings[rfn]
        jeżeli nie ns:
            # This jest the only occurrence of the function on the stack.
            # Else this jest a (directly albo indirectly) recursive call, oraz
            # its cumulative time will get updated when the topmost call to
            # it returns.
            ct = ct + frame_total
            cc = cc + 1

        jeżeli pfn w callers:
            callers[pfn] = callers[pfn] + 1  # hack: gather more
            # stats such jako the amount of time added to ct courtesy
            # of this specific call, oraz the contribution to cc
            # courtesy of this call.
        inaczej:
            callers[pfn] = 1

        timings[rfn] = cc, ns - 1, tt + rit, ct, callers

        zwróć 1


    dispatch = {
        "call": trace_dispatch_call,
        "exception": trace_dispatch_exception,
        "return": trace_dispatch_return,
        "c_call": trace_dispatch_c_call,
        "c_exception": trace_dispatch_return,  # the C function returned
        "c_return": trace_dispatch_return,
        }


    # The next few functions play przy self.cmd. By carefully preloading
    # our parallel stack, we can force the profiled result to include
    # an arbitrary string jako the name of the calling function.
    # We use self.cmd jako that string, oraz the resulting stats look
    # very nice :-).

    def set_cmd(self, cmd):
        jeżeli self.cur[-1]: zwróć   # already set
        self.cmd = cmd
        self.simulate_call(cmd)

    klasa fake_code:
        def __init__(self, filename, line, name):
            self.co_filename = filename
            self.co_line = line
            self.co_name = name
            self.co_firstlineno = 0

        def __repr__(self):
            zwróć repr((self.co_filename, self.co_line, self.co_name))

    klasa fake_frame:
        def __init__(self, code, prior):
            self.f_code = code
            self.f_back = prior

    def simulate_call(self, name):
        code = self.fake_code('profile', 0, name)
        jeżeli self.cur:
            pframe = self.cur[-2]
        inaczej:
            pframe = Nic
        frame = self.fake_frame(code, pframe)
        self.dispatch['call'](self, frame, 0)

    # collect stats z pending stack, including getting final
    # timings dla self.cmd frame.

    def simulate_cmd_complete(self):
        get_time = self.get_time
        t = get_time() - self.t
        dopóki self.cur[-1]:
            # We *can* cause assertion errors here if
            # dispatch_trace_return checks dla a frame match!
            self.dispatch['return'](self, self.cur[-2], t)
            t = 0
        self.t = get_time() - t


    def print_stats(self, sort=-1):
        zaimportuj pstats
        pstats.Stats(self).strip_dirs().sort_stats(sort). \
                  print_stats()

    def dump_stats(self, file):
        przy open(file, 'wb') jako f:
            self.create_stats()
            marshal.dump(self.stats, f)

    def create_stats(self):
        self.simulate_cmd_complete()
        self.snapshot_stats()

    def snapshot_stats(self):
        self.stats = {}
        dla func, (cc, ns, tt, ct, callers) w self.timings.items():
            callers = callers.copy()
            nc = 0
            dla callcnt w callers.values():
                nc += callcnt
            self.stats[func] = cc, nc, tt, ct, callers


    # The following two methods can be called by clients to use
    # a profiler to profile a statement, given jako a string.

    def run(self, cmd):
        zaimportuj __main__
        dict = __main__.__dict__
        zwróć self.runctx(cmd, dict, dict)

    def runctx(self, cmd, globals, locals):
        self.set_cmd(cmd)
        sys.setprofile(self.dispatcher)
        spróbuj:
            exec(cmd, globals, locals)
        w_końcu:
            sys.setprofile(Nic)
        zwróć self

    # This method jest more useful to profile a single function call.
    def runcall(self, func, *args, **kw):
        self.set_cmd(repr(func))
        sys.setprofile(self.dispatcher)
        spróbuj:
            zwróć func(*args, **kw)
        w_końcu:
            sys.setprofile(Nic)


    #******************************************************************
    # The following calculates the overhead dla using a profiler.  The
    # problem jest that it takes a fair amount of time dla the profiler
    # to stop the stopwatch (z the time it receives an event).
    # Similarly, there jest a delay z the time that the profiler
    # re-starts the stopwatch before the user's code really gets to
    # continue.  The following code tries to measure the difference on
    # a per-event basis.
    #
    # Note that this difference jest only significant jeżeli there are a lot of
    # events, oraz relatively little user code per event.  For example,
    # code przy small functions will typically benefit z having the
    # profiler calibrated dla the current platform.  This *could* be
    # done on the fly during init() time, but it jest nie worth the
    # effort.  Also note that jeżeli too large a value specified, then
    # execution time on some functions will actually appear jako a
    # negative number.  It jest *normal* dla some functions (przy very
    # low call counts) to have such negative stats, even jeżeli the
    # calibration figure jest "correct."
    #
    # One alternative to profile-time calibration adjustments (i.e.,
    # adding w the magic little delta during each event) jest to track
    # more carefully the number of events (and cumulatively, the number
    # of events during sub functions) that are seen.  If this were
    # done, then the arithmetic could be done after the fact (i.e., at
    # display time).  Currently, we track only call/return events.
    # These values can be deduced by examining the callees oraz callers
    # vectors dla each functions.  Hence we *can* almost correct the
    # internal time figure at print time (niee that we currently don't
    # track exception event processing counts).  Unfortunately, there
    # jest currently no similar information dla cumulative sub-function
    # time.  It would nie be hard to "get all this info" at profiler
    # time.  Specifically, we would have to extend the tuples to keep
    # counts of this w each frame, oraz then extend the defs of timing
    # tuples to include the significant two figures. I'm a bit fearful
    # that this additional feature will slow the heavily optimized
    # event/time ratio (i.e., the profiler would run slower, fur a very
    # low "value added" feature.)
    #**************************************************************

    def calibrate(self, m, verbose=0):
        jeżeli self.__class__ jest nie Profile:
            podnieś TypeError("Subclasses must override .calibrate().")

        saved_bias = self.bias
        self.bias = 0
        spróbuj:
            zwróć self._calibrate_inner(m, verbose)
        w_końcu:
            self.bias = saved_bias

    def _calibrate_inner(self, m, verbose):
        get_time = self.get_time

        # Set up a test case to be run przy oraz without profiling.  Include
        # lots of calls, because we're trying to quantify stopwatch overhead.
        # Do nie podnieś any exceptions, though, because we want to know
        # exactly how many profile events are generated (one call event, +
        # one zwróć event, per Python-level call).

        def f1(n):
            dla i w range(n):
                x = 1

        def f(m, f1=f1):
            dla i w range(m):
                f1(100)

        f(m)    # warm up the cache

        # elapsed_noprofile <- time f(m) takes without profiling.
        t0 = get_time()
        f(m)
        t1 = get_time()
        elapsed_noprofile = t1 - t0
        jeżeli verbose:
            print("elapsed time without profiling =", elapsed_noprofile)

        # elapsed_profile <- time f(m) takes przy profiling.  The difference
        # jest profiling overhead, only some of which the profiler subtracts
        # out on its own.
        p = Profile()
        t0 = get_time()
        p.runctx('f(m)', globals(), locals())
        t1 = get_time()
        elapsed_profile = t1 - t0
        jeżeli verbose:
            print("elapsed time przy profiling =", elapsed_profile)

        # reported_time <- "CPU seconds" the profiler charged to f oraz f1.
        total_calls = 0.0
        reported_time = 0.0
        dla (filename, line, funcname), (cc, ns, tt, ct, callers) w \
                p.timings.items():
            jeżeli funcname w ("f", "f1"):
                total_calls += cc
                reported_time += tt

        jeżeli verbose:
            print("'CPU seconds' profiler reported =", reported_time)
            print("total # calls =", total_calls)
        jeżeli total_calls != m + 1:
            podnieś ValueError("internal error: total calls = %d" % total_calls)

        # reported_time - elapsed_noprofile = overhead the profiler wasn't
        # able to measure.  Divide by twice the number of calls (since there
        # are two profiler events per call w this test) to get the hidden
        # overhead per event.
        mean = (reported_time - elapsed_noprofile) / 2.0 / total_calls
        jeżeli verbose:
            print("mean stopwatch overhead per profile event =", mean)
        zwróć mean

#****************************************************************************

def main():
    usage = "profile.py [-o output_file_path] [-s sort] scriptfile [arg] ..."
    parser = OptionParser(usage=usage)
    parser.allow_interspersed_args = Nieprawda
    parser.add_option('-o', '--outfile', dest="outfile",
        help="Save stats to <outfile>", default=Nic)
    parser.add_option('-s', '--sort', dest="sort",
        help="Sort order when printing to stdout, based on pstats.Stats class",
        default=-1)

    jeżeli nie sys.argv[1:]:
        parser.print_usage()
        sys.exit(2)

    (options, args) = parser.parse_args()
    sys.argv[:] = args

    jeżeli len(args) > 0:
        progname = args[0]
        sys.path.insert(0, os.path.dirname(progname))
        przy open(progname, 'rb') jako fp:
            code = compile(fp.read(), progname, 'exec')
        globs = {
            '__file__': progname,
            '__name__': '__main__',
            '__package__': Nic,
            '__cached__': Nic,
        }
        runctx(code, globs, Nic, options.outfile, options.sort)
    inaczej:
        parser.print_usage()
    zwróć parser

# When invoked jako main program, invoke the profiler on a script
jeżeli __name__ == '__main__':
    main()
