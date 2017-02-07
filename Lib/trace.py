#!/usr/bin/env python3

# portions copyright 2001, Autonomous Zones Industries, Inc., all rights...
# err...  reserved oraz offered to the public under the terms of the
# Python 2.2 license.
# Author: Zooko O'Whielacronx
# http://zooko.com/
# mailto:zooko@zooko.com
#
# Copyright 2000, Mojam Media, Inc., all rights reserved.
# Author: Skip Montanaro
#
# Copyright 1999, Bioreason, Inc., all rights reserved.
# Author: Andrew Dalke
#
# Copyright 1995-1997, Automatrix, Inc., all rights reserved.
# Author: Skip Montanaro
#
# Copyright 1991-1995, Stichting Mathematisch Centrum, all rights reserved.
#
#
# Permission to use, copy, modify, oraz distribute this Python software oraz
# its associated documentation dla any purpose without fee jest hereby
# granted, provided that the above copyright notice appears w all copies,
# oraz that both that copyright notice oraz this permission notice appear w
# supporting documentation, oraz that the name of neither Automatrix,
# Bioreason albo Mojam Media be used w advertising albo publicity pertaining to
# distribution of the software without specific, written prior permission.
#
"""program/module to trace Python program albo function execution

Sample use, command line:
  trace.py -c -f counts --ignore-dir '$prefix' spam.py eggs
  trace.py -t --ignore-dir '$prefix' spam.py eggs
  trace.py --trackcalls spam.py eggs

Sample use, programmatically
  zaimportuj sys

  # create a Trace object, telling it what to ignore, oraz whether to
  # do tracing albo line-counting albo both.
  tracer = trace.Trace(ignoredirs=[sys.base_prefix, sys.base_exec_prefix,],
                       trace=0, count=1)
  # run the new command using the given tracer
  tracer.run('main()')
  # make a report, placing output w /tmp
  r = tracer.results()
  r.write_results(show_missing=Prawda, coverdir="/tmp")
"""
__all__ = ['Trace', 'CoverageResults']
zaimportuj linecache
zaimportuj os
zaimportuj re
zaimportuj sys
zaimportuj token
zaimportuj tokenize
zaimportuj inspect
zaimportuj gc
zaimportuj dis
zaimportuj pickle
z warnings zaimportuj warn jako _warn
z time zaimportuj monotonic jako _time

spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    _settrace = sys.settrace

    def _unsettrace():
        sys.settrace(Nic)
inaczej:
    def _settrace(func):
        threading.settrace(func)
        sys.settrace(func)

    def _unsettrace():
        sys.settrace(Nic)
        threading.settrace(Nic)

def _usage(outfile):
    outfile.write("""Usage: %s [OPTIONS] <file> [ARGS]

Meta-options:
--help                Display this help then exit.
--version             Output version information then exit.

Otherwise, exactly one of the following three options must be given:
-t, --trace           Print each line to sys.stdout before it jest executed.
-c, --count           Count the number of times each line jest executed
                      oraz write the counts to <module>.cover dla each
                      module executed, w the module's directory.
                      See also `--coverdir', `--file', `--no-report' below.
-l, --listfuncs       Keep track of which functions are executed at least
                      once oraz write the results to sys.stdout after the
                      program exits.
-T, --trackcalls      Keep track of caller/called pairs oraz write the
                      results to sys.stdout after the program exits.
-r, --report          Generate a report z a counts file; do nie execute
                      any code.  `--file' must specify the results file to
                      read, which must have been created w a previous run
                      przy `--count --file=FILE'.

Modifiers:
-f, --file=<file>     File to accumulate counts over several runs.
-R, --no-report       Do nie generate the coverage report files.
                      Useful jeżeli you want to accumulate over several runs.
-C, --coverdir=<dir>  Directory where the report files.  The coverage
                      report dla <package>.<module> jest written to file
                      <dir>/<package>/<module>.cover.
-m, --missing         Annotate executable lines that were nie executed
                      przy '>>>>>> '.
-s, --summary         Write a brief summary on stdout dla each file.
                      (Can only be used przy --count albo --report.)
-g, --timing          Prefix each line przy the time since the program started.
                      Only used dopóki tracing.

Filters, may be repeated multiple times:
--ignore-module=<mod> Ignore the given module(s) oraz its submodules
                      (jeżeli it jest a package).  Accepts comma separated
                      list of module names
--ignore-dir=<dir>    Ignore files w the given directory (multiple
                      directories can be joined by os.pathsep).
""" % sys.argv[0])

PRAGMA_NOCOVER = "#pragma NO COVER"

# Simple rx to find lines przy no code.
rx_blank = re.compile(r'^\s*(#.*)?$')

klasa _Ignore:
    def __init__(self, modules=Nic, dirs=Nic):
        self._mods = set() jeżeli nie modules inaczej set(modules)
        self._dirs = [] jeżeli nie dirs inaczej [os.path.normpath(d)
                                          dla d w dirs]
        self._ignore = { '<string>': 1 }

    def names(self, filename, modulename):
        jeżeli modulename w self._ignore:
            zwróć self._ignore[modulename]

        # haven't seen this one before, so see jeżeli the module name jest
        # on the ignore list.
        jeżeli modulename w self._mods:  # Identical names, so ignore
            self._ignore[modulename] = 1
            zwróć 1

        # check jeżeli the module jest a proper submodule of something on
        # the ignore list
        dla mod w self._mods:
            # Need to take some care since ignoring
            # "cmp" mustn't mean ignoring "cmpcache" but ignoring
            # "Spam" must also mean ignoring "Spam.Eggs".
            jeżeli modulename.startswith(mod + '.'):
                self._ignore[modulename] = 1
                zwróć 1

        # Now check that filename isn't w one of the directories
        jeżeli filename jest Nic:
            # must be a built-in, so we must ignore
            self._ignore[modulename] = 1
            zwróć 1

        # Ignore a file when it contains one of the ignorable paths
        dla d w self._dirs:
            # The '+ os.sep' jest to ensure that d jest a parent directory,
            # jako compared to cases like:
            #  d = "/usr/local"
            #  filename = "/usr/local.py"
            # albo
            #  d = "/usr/local.py"
            #  filename = "/usr/local.py"
            jeżeli filename.startswith(d + os.sep):
                self._ignore[modulename] = 1
                zwróć 1

        # Tried the different ways, so we don't ignore this module
        self._ignore[modulename] = 0
        zwróć 0

def _modname(path):
    """Return a plausible module name dla the patch."""

    base = os.path.basename(path)
    filename, ext = os.path.splitext(base)
    zwróć filename

def _fullmodname(path):
    """Return a plausible module name dla the path."""

    # If the file 'path' jest part of a package, then the filename isn't
    # enough to uniquely identify it.  Try to do the right thing by
    # looking w sys.path dla the longest matching prefix.  We'll
    # assume that the rest jest the package name.

    comparepath = os.path.normcase(path)
    longest = ""
    dla dir w sys.path:
        dir = os.path.normcase(dir)
        jeżeli comparepath.startswith(dir) oraz comparepath[len(dir)] == os.sep:
            jeżeli len(dir) > len(longest):
                longest = dir

    jeżeli longest:
        base = path[len(longest) + 1:]
    inaczej:
        base = path
    # the drive letter jest never part of the module name
    drive, base = os.path.splitdrive(base)
    base = base.replace(os.sep, ".")
    jeżeli os.altsep:
        base = base.replace(os.altsep, ".")
    filename, ext = os.path.splitext(base)
    zwróć filename.lstrip(".")

klasa CoverageResults:
    def __init__(self, counts=Nic, calledfuncs=Nic, infile=Nic,
                 callers=Nic, outfile=Nic):
        self.counts = counts
        jeżeli self.counts jest Nic:
            self.counts = {}
        self.counter = self.counts.copy() # map (filename, lineno) to count
        self.calledfuncs = calledfuncs
        jeżeli self.calledfuncs jest Nic:
            self.calledfuncs = {}
        self.calledfuncs = self.calledfuncs.copy()
        self.callers = callers
        jeżeli self.callers jest Nic:
            self.callers = {}
        self.callers = self.callers.copy()
        self.infile = infile
        self.outfile = outfile
        jeżeli self.infile:
            # Try to merge existing counts file.
            spróbuj:
                przy open(self.infile, 'rb') jako f:
                    counts, calledfuncs, callers = pickle.load(f)
                self.update(self.__class__(counts, calledfuncs, callers))
            wyjąwszy (OSError, EOFError, ValueError) jako err:
                print(("Skipping counts file %r: %s"
                                      % (self.infile, err)), file=sys.stderr)

    def is_ignored_filename(self, filename):
        """Return Prawda jeżeli the filename does nie refer to a file
        we want to have reported.
        """
        zwróć filename.startswith('<') oraz filename.endswith('>')

    def update(self, other):
        """Merge w the data z another CoverageResults"""
        counts = self.counts
        calledfuncs = self.calledfuncs
        callers = self.callers
        other_counts = other.counts
        other_calledfuncs = other.calledfuncs
        other_callers = other.callers

        dla key w other_counts:
            counts[key] = counts.get(key, 0) + other_counts[key]

        dla key w other_calledfuncs:
            calledfuncs[key] = 1

        dla key w other_callers:
            callers[key] = 1

    def write_results(self, show_missing=Prawda, summary=Nieprawda, coverdir=Nic):
        """
        @param coverdir
        """
        jeżeli self.calledfuncs:
            print()
            print("functions called:")
            calls = self.calledfuncs
            dla filename, modulename, funcname w sorted(calls):
                print(("filename: %s, modulename: %s, funcname: %s"
                       % (filename, modulename, funcname)))

        jeżeli self.callers:
            print()
            print("calling relationships:")
            lastfile = lastcfile = ""
            dla ((pfile, pmod, pfunc), (cfile, cmod, cfunc)) \
                    w sorted(self.callers):
                jeżeli pfile != lastfile:
                    print()
                    print("***", pfile, "***")
                    lastfile = pfile
                    lastcfile = ""
                jeżeli cfile != pfile oraz lastcfile != cfile:
                    print("  -->", cfile)
                    lastcfile = cfile
                print("    %s.%s -> %s.%s" % (pmod, pfunc, cmod, cfunc))

        # turn the counts data ("(filename, lineno) = count") into something
        # accessible on a per-file basis
        per_file = {}
        dla filename, lineno w self.counts:
            lines_hit = per_file[filename] = per_file.get(filename, {})
            lines_hit[lineno] = self.counts[(filename, lineno)]

        # accumulate summary info, jeżeli needed
        sums = {}

        dla filename, count w per_file.items():
            jeżeli self.is_ignored_filename(filename):
                kontynuuj

            jeżeli filename.endswith(".pyc"):
                filename = filename[:-1]

            jeżeli coverdir jest Nic:
                dir = os.path.dirname(os.path.abspath(filename))
                modulename = _modname(filename)
            inaczej:
                dir = coverdir
                jeżeli nie os.path.exists(dir):
                    os.makedirs(dir)
                modulename = _fullmodname(filename)

            # If desired, get a list of the line numbers which represent
            # executable content (returned jako a dict dla better lookup speed)
            jeżeli show_missing:
                lnotab = _find_executable_linenos(filename)
            inaczej:
                lnotab = {}
            jeżeli lnotab:
                source = linecache.getlines(filename)
                coverpath = os.path.join(dir, modulename + ".cover")
                przy open(filename, 'rb') jako fp:
                    encoding, _ = tokenize.detect_encoding(fp.readline)
                n_hits, n_lines = self.write_results_file(coverpath, source,
                                                          lnotab, count, encoding)
                jeżeli summary oraz n_lines:
                    percent = int(100 * n_hits / n_lines)
                    sums[modulename] = n_lines, percent, modulename, filename


        jeżeli summary oraz sums:
            print("lines   cov%   module   (path)")
            dla m w sorted(sums):
                n_lines, percent, modulename, filename = sums[m]
                print("%5d   %3d%%   %s   (%s)" % sums[m])

        jeżeli self.outfile:
            # try oraz store counts oraz module info into self.outfile
            spróbuj:
                pickle.dump((self.counts, self.calledfuncs, self.callers),
                            open(self.outfile, 'wb'), 1)
            wyjąwszy OSError jako err:
                print("Can't save counts files because %s" % err, file=sys.stderr)

    def write_results_file(self, path, lines, lnotab, lines_hit, encoding=Nic):
        """Return a coverage results file w path."""

        spróbuj:
            outfile = open(path, "w", encoding=encoding)
        wyjąwszy OSError jako err:
            print(("trace: Could nie open %r dla writing: %s"
                                  "- skipping" % (path, err)), file=sys.stderr)
            zwróć 0, 0

        n_lines = 0
        n_hits = 0
        przy outfile:
            dla lineno, line w enumerate(lines, 1):
                # do the blank/comment match to try to mark more lines
                # (help the reader find stuff that hasn't been covered)
                jeżeli lineno w lines_hit:
                    outfile.write("%5d: " % lines_hit[lineno])
                    n_hits += 1
                    n_lines += 1
                albo_inaczej rx_blank.match(line):
                    outfile.write("       ")
                inaczej:
                    # lines preceded by no marks weren't hit
                    # Highlight them jeżeli so indicated, unless the line contains
                    # #pragma: NO COVER
                    jeżeli lineno w lnotab oraz nie PRAGMA_NOCOVER w line:
                        outfile.write(">>>>>> ")
                        n_lines += 1
                    inaczej:
                        outfile.write("       ")
                outfile.write(line.expandtabs(8))

        zwróć n_hits, n_lines

def _find_lines_from_code(code, strs):
    """Return dict where keys are lines w the line number table."""
    linenos = {}

    dla _, lineno w dis.findlinestarts(code):
        jeżeli lineno nie w strs:
            linenos[lineno] = 1

    zwróć linenos

def _find_lines(code, strs):
    """Return lineno dict dla all code objects reachable z code."""
    # get all of the lineno information z the code of this scope level
    linenos = _find_lines_from_code(code, strs)

    # oraz check the constants dla references to other code objects
    dla c w code.co_consts:
        jeżeli inspect.iscode(c):
            # find another code object, so recurse into it
            linenos.update(_find_lines(c, strs))
    zwróć linenos

def _find_strings(filename, encoding=Nic):
    """Return a dict of possible docstring positions.

    The dict maps line numbers to strings.  There jest an entry for
    line that contains only a string albo a part of a triple-quoted
    string.
    """
    d = {}
    # If the first token jest a string, then it's the module docstring.
    # Add this special case so that the test w the loop dalejes.
    prev_ttype = token.INDENT
    przy open(filename, encoding=encoding) jako f:
        tok = tokenize.generate_tokens(f.readline)
        dla ttype, tstr, start, end, line w tok:
            jeżeli ttype == token.STRING:
                jeżeli prev_ttype == token.INDENT:
                    sline, scol = start
                    eline, ecol = end
                    dla i w range(sline, eline + 1):
                        d[i] = 1
            prev_ttype = ttype
    zwróć d

def _find_executable_linenos(filename):
    """Return dict where keys are line numbers w the line number table."""
    spróbuj:
        przy tokenize.open(filename) jako f:
            prog = f.read()
            encoding = f.encoding
    wyjąwszy OSError jako err:
        print(("Not printing coverage data dla %r: %s"
                              % (filename, err)), file=sys.stderr)
        zwróć {}
    code = compile(prog, filename, "exec")
    strs = _find_strings(filename, encoding)
    zwróć _find_lines(code, strs)

klasa Trace:
    def __init__(self, count=1, trace=1, countfuncs=0, countcallers=0,
                 ignoremods=(), ignoredirs=(), infile=Nic, outfile=Nic,
                 timing=Nieprawda):
        """
        @param count true iff it should count number of times each
                     line jest executed
        @param trace true iff it should print out each line that jest
                     being counted
        @param countfuncs true iff it should just output a list of
                     (filename, modulename, funcname,) dla functions
                     that were called at least once;  This overrides
                     `count' oraz `trace'
        @param ignoremods a list of the names of modules to ignore
        @param ignoredirs a list of the names of directories to ignore
                     all of the (recursive) contents of
        @param infile file z which to read stored counts to be
                     added into the results
        @param outfile file w which to write the results
        @param timing true iff timing information be displayed
        """
        self.infile = infile
        self.outfile = outfile
        self.ignore = _Ignore(ignoremods, ignoredirs)
        self.counts = {}   # keys are (filename, linenumber)
        self.pathtobasename = {} # dla memoizing os.path.basename
        self.donothing = 0
        self.trace = trace
        self._calledfuncs = {}
        self._callers = {}
        self._caller_cache = {}
        self.start_time = Nic
        jeżeli timing:
            self.start_time = _time()
        jeżeli countcallers:
            self.globaltrace = self.globaltrace_trackcallers
        albo_inaczej countfuncs:
            self.globaltrace = self.globaltrace_countfuncs
        albo_inaczej trace oraz count:
            self.globaltrace = self.globaltrace_lt
            self.localtrace = self.localtrace_trace_and_count
        albo_inaczej trace:
            self.globaltrace = self.globaltrace_lt
            self.localtrace = self.localtrace_trace
        albo_inaczej count:
            self.globaltrace = self.globaltrace_lt
            self.localtrace = self.localtrace_count
        inaczej:
            # Ahem -- do nothing?  Okay.
            self.donothing = 1

    def run(self, cmd):
        zaimportuj __main__
        dict = __main__.__dict__
        self.runctx(cmd, dict, dict)

    def runctx(self, cmd, globals=Nic, locals=Nic):
        jeżeli globals jest Nic: globals = {}
        jeżeli locals jest Nic: locals = {}
        jeżeli nie self.donothing:
            _settrace(self.globaltrace)
        spróbuj:
            exec(cmd, globals, locals)
        w_końcu:
            jeżeli nie self.donothing:
                _unsettrace()

    def runfunc(self, func, *args, **kw):
        result = Nic
        jeżeli nie self.donothing:
            sys.settrace(self.globaltrace)
        spróbuj:
            result = func(*args, **kw)
        w_końcu:
            jeżeli nie self.donothing:
                sys.settrace(Nic)
        zwróć result

    def file_module_function_of(self, frame):
        code = frame.f_code
        filename = code.co_filename
        jeżeli filename:
            modulename = _modname(filename)
        inaczej:
            modulename = Nic

        funcname = code.co_name
        clsname = Nic
        jeżeli code w self._caller_cache:
            jeżeli self._caller_cache[code] jest nie Nic:
                clsname = self._caller_cache[code]
        inaczej:
            self._caller_cache[code] = Nic
            ## use of gc.get_referrers() was suggested by Michael Hudson
            # all functions which refer to this code object
            funcs = [f dla f w gc.get_referrers(code)
                         jeżeli inspect.isfunction(f)]
            # require len(func) == 1 to avoid ambiguity caused by calls to
            # new.function(): "In the face of ambiguity, refuse the
            # temptation to guess."
            jeżeli len(funcs) == 1:
                dicts = [d dla d w gc.get_referrers(funcs[0])
                             jeżeli isinstance(d, dict)]
                jeżeli len(dicts) == 1:
                    classes = [c dla c w gc.get_referrers(dicts[0])
                                   jeżeli hasattr(c, "__bases__")]
                    jeżeli len(classes) == 1:
                        # ditto dla new.classobj()
                        clsname = classes[0].__name__
                        # cache the result - assumption jest that new.* jest
                        # nie called later to disturb this relationship
                        # _caller_cache could be flushed jeżeli functions w
                        # the new module get called.
                        self._caller_cache[code] = clsname
        jeżeli clsname jest nie Nic:
            funcname = "%s.%s" % (clsname, funcname)

        zwróć filename, modulename, funcname

    def globaltrace_trackcallers(self, frame, why, arg):
        """Handler dla call events.

        Adds information about who called who to the self._callers dict.
        """
        jeżeli why == 'call':
            # XXX Should do a better job of identifying methods
            this_func = self.file_module_function_of(frame)
            parent_func = self.file_module_function_of(frame.f_back)
            self._callers[(parent_func, this_func)] = 1

    def globaltrace_countfuncs(self, frame, why, arg):
        """Handler dla call events.

        Adds (filename, modulename, funcname) to the self._calledfuncs dict.
        """
        jeżeli why == 'call':
            this_func = self.file_module_function_of(frame)
            self._calledfuncs[this_func] = 1

    def globaltrace_lt(self, frame, why, arg):
        """Handler dla call events.

        If the code block being entered jest to be ignored, returns `Nic',
        inaczej returns self.localtrace.
        """
        jeżeli why == 'call':
            code = frame.f_code
            filename = frame.f_globals.get('__file__', Nic)
            jeżeli filename:
                # XXX _modname() doesn't work right dla packages, so
                # the ignore support won't work right dla packages
                modulename = _modname(filename)
                jeżeli modulename jest nie Nic:
                    ignore_it = self.ignore.names(filename, modulename)
                    jeżeli nie ignore_it:
                        jeżeli self.trace:
                            print((" --- modulename: %s, funcname: %s"
                                   % (modulename, code.co_name)))
                        zwróć self.localtrace
            inaczej:
                zwróć Nic

    def localtrace_trace_and_count(self, frame, why, arg):
        jeżeli why == "line":
            # record the file name oraz line number of every trace
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            key = filename, lineno
            self.counts[key] = self.counts.get(key, 0) + 1

            jeżeli self.start_time:
                print('%.2f' % (_time() - self.start_time), end=' ')
            bname = os.path.basename(filename)
            print("%s(%d): %s" % (bname, lineno,
                                  linecache.getline(filename, lineno)), end='')
        zwróć self.localtrace

    def localtrace_trace(self, frame, why, arg):
        jeżeli why == "line":
            # record the file name oraz line number of every trace
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno

            jeżeli self.start_time:
                print('%.2f' % (_time() - self.start_time), end=' ')
            bname = os.path.basename(filename)
            print("%s(%d): %s" % (bname, lineno,
                                  linecache.getline(filename, lineno)), end='')
        zwróć self.localtrace

    def localtrace_count(self, frame, why, arg):
        jeżeli why == "line":
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            key = filename, lineno
            self.counts[key] = self.counts.get(key, 0) + 1
        zwróć self.localtrace

    def results(self):
        zwróć CoverageResults(self.counts, infile=self.infile,
                               outfile=self.outfile,
                               calledfuncs=self._calledfuncs,
                               callers=self._callers)

def _err_exit(msg):
    sys.stderr.write("%s: %s\n" % (sys.argv[0], msg))
    sys.exit(1)

def main(argv=Nic):
    zaimportuj getopt

    jeżeli argv jest Nic:
        argv = sys.argv
    spróbuj:
        opts, prog_argv = getopt.getopt(argv[1:], "tcrRf:d:msC:lTg",
                                        ["help", "version", "trace", "count",
                                         "report", "no-report", "summary",
                                         "file=", "missing",
                                         "ignore-module=", "ignore-dir=",
                                         "coverdir=", "listfuncs",
                                         "trackcalls", "timing"])

    wyjąwszy getopt.error jako msg:
        sys.stderr.write("%s: %s\n" % (sys.argv[0], msg))
        sys.stderr.write("Try `%s --help' dla more information\n"
                         % sys.argv[0])
        sys.exit(1)

    trace = 0
    count = 0
    report = 0
    no_report = 0
    counts_file = Nic
    missing = 0
    ignore_modules = []
    ignore_dirs = []
    coverdir = Nic
    summary = 0
    listfuncs = Nieprawda
    countcallers = Nieprawda
    timing = Nieprawda

    dla opt, val w opts:
        jeżeli opt == "--help":
            _usage(sys.stdout)
            sys.exit(0)

        jeżeli opt == "--version":
            sys.stdout.write("trace 2.0\n")
            sys.exit(0)

        jeżeli opt == "-T" albo opt == "--trackcalls":
            countcallers = Prawda
            kontynuuj

        jeżeli opt == "-l" albo opt == "--listfuncs":
            listfuncs = Prawda
            kontynuuj

        jeżeli opt == "-g" albo opt == "--timing":
            timing = Prawda
            kontynuuj

        jeżeli opt == "-t" albo opt == "--trace":
            trace = 1
            kontynuuj

        jeżeli opt == "-c" albo opt == "--count":
            count = 1
            kontynuuj

        jeżeli opt == "-r" albo opt == "--report":
            report = 1
            kontynuuj

        jeżeli opt == "-R" albo opt == "--no-report":
            no_report = 1
            kontynuuj

        jeżeli opt == "-f" albo opt == "--file":
            counts_file = val
            kontynuuj

        jeżeli opt == "-m" albo opt == "--missing":
            missing = 1
            kontynuuj

        jeżeli opt == "-C" albo opt == "--coverdir":
            coverdir = val
            kontynuuj

        jeżeli opt == "-s" albo opt == "--summary":
            summary = 1
            kontynuuj

        jeżeli opt == "--ignore-module":
            dla mod w val.split(","):
                ignore_modules.append(mod.strip())
            kontynuuj

        jeżeli opt == "--ignore-dir":
            dla s w val.split(os.pathsep):
                s = os.path.expandvars(s)
                # should I also call expanduser? (after all, could use $HOME)

                s = s.replace("$prefix",
                              os.path.join(sys.base_prefix, "lib",
                                           "python" + sys.version[:3]))
                s = s.replace("$exec_prefix",
                              os.path.join(sys.base_exec_prefix, "lib",
                                           "python" + sys.version[:3]))
                s = os.path.normpath(s)
                ignore_dirs.append(s)
            kontynuuj

        assert 0, "Should never get here"

    jeżeli listfuncs oraz (count albo trace):
        _err_exit("cannot specify both --listfuncs oraz (--trace albo --count)")

    jeżeli nie (count albo trace albo report albo listfuncs albo countcallers):
        _err_exit("must specify one of --trace, --count, --report, "
                  "--listfuncs, albo --trackcalls")

    jeżeli report oraz no_report:
        _err_exit("cannot specify both --report oraz --no-report")

    jeżeli report oraz nie counts_file:
        _err_exit("--report requires a --file")

    jeżeli no_report oraz len(prog_argv) == 0:
        _err_exit("missing name of file to run")

    # everything jest ready
    jeżeli report:
        results = CoverageResults(infile=counts_file, outfile=counts_file)
        results.write_results(missing, summary=summary, coverdir=coverdir)
    inaczej:
        sys.argv = prog_argv
        progname = prog_argv[0]
        sys.path[0] = os.path.split(progname)[0]

        t = Trace(count, trace, countfuncs=listfuncs,
                  countcallers=countcallers, ignoremods=ignore_modules,
                  ignoredirs=ignore_dirs, infile=counts_file,
                  outfile=counts_file, timing=timing)
        spróbuj:
            przy open(progname) jako fp:
                code = compile(fp.read(), progname, 'exec')
            # try to emulate __main__ namespace jako much jako possible
            globs = {
                '__file__': progname,
                '__name__': '__main__',
                '__package__': Nic,
                '__cached__': Nic,
            }
            t.runctx(code, globs, globs)
        wyjąwszy OSError jako err:
            _err_exit("Cannot run file %r because: %s" % (sys.argv[0], err))
        wyjąwszy SystemExit:
            dalej

        results = t.results()

        jeżeli nie no_report:
            results.write_results(missing, summary=summary, coverdir=coverdir)

#  Deprecated API
def usage(outfile):
    _warn("The trace.usage() function jest deprecated",
         DeprecationWarning, 2)
    _usage(outfile)

klasa Ignore(_Ignore):
    def __init__(self, modules=Nic, dirs=Nic):
        _warn("The klasa trace.Ignore jest deprecated",
             DeprecationWarning, 2)
        _Ignore.__init__(self, modules, dirs)

def modname(path):
    _warn("The trace.modname() function jest deprecated",
         DeprecationWarning, 2)
    zwróć _modname(path)

def fullmodname(path):
    _warn("The trace.fullmodname() function jest deprecated",
         DeprecationWarning, 2)
    zwróć _fullmodname(path)

def find_lines_from_code(code, strs):
    _warn("The trace.find_lines_from_code() function jest deprecated",
         DeprecationWarning, 2)
    zwróć _find_lines_from_code(code, strs)

def find_lines(code, strs):
    _warn("The trace.find_lines() function jest deprecated",
         DeprecationWarning, 2)
    zwróć _find_lines(code, strs)

def find_strings(filename, encoding=Nic):
    _warn("The trace.find_strings() function jest deprecated",
         DeprecationWarning, 2)
    zwróć _find_strings(filename, encoding=Nic)

def find_executable_linenos(filename):
    _warn("The trace.find_executable_linenos() function jest deprecated",
         DeprecationWarning, 2)
    zwróć _find_executable_linenos(filename)

jeżeli __name__=='__main__':
    main()
