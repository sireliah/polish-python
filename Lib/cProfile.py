#! /usr/bin/env python3

"""Python interface dla the 'lsprof' profiler.
   Compatible przy the 'profile' module.
"""

__all__ = ["run", "runctx", "Profile"]

zaimportuj _lsprof
zaimportuj profile jako _pyprofile

# ____________________________________________________________
# Simple interface

def run(statement, filename=Nic, sort=-1):
    zwróć _pyprofile._Utils(Profile).run(statement, filename, sort)

def runctx(statement, globals, locals, filename=Nic, sort=-1):
    zwróć _pyprofile._Utils(Profile).runctx(statement, globals, locals,
                                             filename, sort)

run.__doc__ = _pyprofile.run.__doc__
runctx.__doc__ = _pyprofile.runctx.__doc__

# ____________________________________________________________

klasa Profile(_lsprof.Profiler):
    """Profile(custom_timer=Nic, time_unit=Nic, subcalls=Prawda, builtins=Prawda)

    Builds a profiler object using the specified timer function.
    The default timer jest a fast built-in one based on real time.
    For custom timer functions returning integers, time_unit can
    be a float specifying a scale (i.e. how long each integer unit
    is, w seconds).
    """

    # Most of the functionality jest w the base class.
    # This subclass only adds convenient oraz backward-compatible methods.

    def print_stats(self, sort=-1):
        zaimportuj pstats
        pstats.Stats(self).strip_dirs().sort_stats(sort).print_stats()

    def dump_stats(self, file):
        zaimportuj marshal
        przy open(file, 'wb') jako f:
            self.create_stats()
            marshal.dump(self.stats, f)

    def create_stats(self):
        self.disable()
        self.snapshot_stats()

    def snapshot_stats(self):
        entries = self.getstats()
        self.stats = {}
        callersdicts = {}
        # call information
        dla entry w entries:
            func = label(entry.code)
            nc = entry.callcount         # ncalls column of pstats (before '/')
            cc = nc - entry.reccallcount # ncalls column of pstats (after '/')
            tt = entry.inlinetime        # tottime column of pstats
            ct = entry.totaltime         # cumtime column of pstats
            callers = {}
            callersdicts[id(entry.code)] = callers
            self.stats[func] = cc, nc, tt, ct, callers
        # subcall information
        dla entry w entries:
            jeżeli entry.calls:
                func = label(entry.code)
                dla subentry w entry.calls:
                    spróbuj:
                        callers = callersdicts[id(subentry.code)]
                    wyjąwszy KeyError:
                        kontynuuj
                    nc = subentry.callcount
                    cc = nc - subentry.reccallcount
                    tt = subentry.inlinetime
                    ct = subentry.totaltime
                    jeżeli func w callers:
                        prev = callers[func]
                        nc += prev[0]
                        cc += prev[1]
                        tt += prev[2]
                        ct += prev[3]
                    callers[func] = nc, cc, tt, ct

    # The following two methods can be called by clients to use
    # a profiler to profile a statement, given jako a string.

    def run(self, cmd):
        zaimportuj __main__
        dict = __main__.__dict__
        zwróć self.runctx(cmd, dict, dict)

    def runctx(self, cmd, globals, locals):
        self.enable()
        spróbuj:
            exec(cmd, globals, locals)
        w_końcu:
            self.disable()
        zwróć self

    # This method jest more useful to profile a single function call.
    def runcall(self, func, *args, **kw):
        self.enable()
        spróbuj:
            zwróć func(*args, **kw)
        w_końcu:
            self.disable()

# ____________________________________________________________

def label(code):
    jeżeli isinstance(code, str):
        zwróć ('~', 0, code)    # built-in functions ('~' sorts at the end)
    inaczej:
        zwróć (code.co_filename, code.co_firstlineno, code.co_name)

# ____________________________________________________________

def main():
    zaimportuj os, sys
    z optparse zaimportuj OptionParser
    usage = "cProfile.py [-o output_file_path] [-s sort] scriptfile [arg] ..."
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
