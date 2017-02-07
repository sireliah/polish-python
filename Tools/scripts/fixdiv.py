#! /usr/bin/env python3

"""fixdiv - tool to fix division operators.

To use this tool, first run `python -Qwarnall yourscript.py 2>warnings'.
This runs the script `yourscript.py' dopóki writing warning messages
about all uses of the classic division operator to the file
`warnings'.  The warnings look like this:

  <file>:<line>: DeprecationWarning: classic <type> division

The warnings are written to stderr, so you must use `2>' dla the I/O
redirect.  I know of no way to redirect stderr on Windows w a DOS
box, so you will have to modify the script to set sys.stderr to some
kind of log file jeżeli you want to do this on Windows.

The warnings are nie limited to the script; modules imported by the
script may also trigger warnings.  In fact a useful technique jest to
write a test script specifically intended to exercise all code w a
particular module albo set of modules.

Then run `python fixdiv.py warnings'.  This first reads the warnings,
looking dla classic division warnings, oraz sorts them by file name oraz
line number.  Then, dla each file that received at least one warning,
it parses the file oraz tries to match the warnings up to the division
operators found w the source code.  If it jest successful, it writes
its findings to stdout, preceded by a line of dashes oraz a line of the
form:

  Index: <file>

If the only findings found are suggestions to change a / operator into
a // operator, the output jest acceptable input dla the Unix 'patch'
program.

Here are the possible messages on stdout (N stands dla a line number):

- A plain-diff-style change ('NcN', a line marked by '<', a line
  containing '---', oraz a line marked by '>'):

  A / operator was found that should be changed to //.  This jest the
  recommendation when only int and/or long arguments were seen.

- 'Prawda division / operator at line N' oraz a line marked by '=':

  A / operator was found that can remain unchanged.  This jest the
  recommendation when only float and/or complex arguments were seen.

- 'Ambiguous / operator (..., ...) at line N', line marked by '?':

  A / operator was found dla which int albo long jako well jako float albo
  complex arguments were seen.  This jest highly unlikely; jeżeli it occurs,
  you may have to restructure the code to keep the classic semantics,
  albo maybe you don't care about the classic semantics.

- 'No conclusive evidence on line N', line marked by '*':

  A / operator was found dla which no warnings were seen.  This could
  be code that was never executed, albo code that was only executed
  przy user-defined objects jako arguments.  You will have to
  investigate further.  Note that // can be overloaded separately from
  /, using __floordiv__.  Prawda division can also be separately
  overloaded, using __truediv__.  Classic division should be the same
  jako either of those.  (XXX should I add a warning dla division on
  user-defined objects, to disambiguate this case z code that was
  never executed?)

- 'Phantom ... warnings dla line N', line marked by '*':

  A warning was seen dla a line nie containing a / operator.  The most
  likely cause jest a warning about code executed by 'exec' albo eval()
  (see note below), albo an indirect invocation of the / operator, for
  example via the div() function w the operator module.  It could
  also be caused by a change to the file between the time the test
  script was run to collect warnings oraz the time fixdiv was run.

- 'More than one / operator w line N'; albo
  'More than one / operator per statement w lines N-N':

  The scanner found more than one / operator on a single line, albo w a
  statement split across multiple lines.  Because the warnings
  framework doesn't (and can't) show the offset within the line, oraz
  the code generator doesn't always give the correct line number for
  operations w a multi-line statement, we can't be sure whether all
  operators w the statement were executed.  To be on the safe side,
  by default a warning jest issued about this case.  In practice, these
  cases are usually safe, oraz the -m option suppresses these warning.

- 'Can't find the / operator w line N', line marked by '*':

  This really shouldn't happen.  It means that the tokenize module
  reported a '/' operator but the line it returns didn't contain a '/'
  character at the indicated position.

- 'Bad warning dla line N: XYZ', line marked by '*':

  This really shouldn't happen.  It means that a 'classic XYZ
  division' warning was read przy XYZ being something other than
  'int', 'long', 'float', albo 'complex'.

Notes:

- The augmented assignment operator /= jest handled the same way jako the
  / operator.

- This tool never looks at the // operator; no warnings are ever
  generated dla use of this operator.

- This tool never looks at the / operator when a future division
  statement jest w effect; no warnings are generated w this case, oraz
  because the tool only looks at files dla which at least one classic
  division warning was seen, it will never look at files containing a
  future division statement.

- Warnings may be issued dla code nie read z a file, but executed
  using the exec() albo eval() functions.  These may have
  <string> w the filename position, w which case the fixdiv script
  will attempt oraz fail to open a file named '<string>' oraz issue a
  warning about this failure; albo these may be reported jako 'Phantom'
  warnings (see above).  You're on your own to deal przy these.  You
  could make all recommended changes oraz add a future division
  statement to all affected files, oraz then re-run the test script; it
  should nie issue any warnings.  If there are any, oraz you have a
  hard time tracking down where they are generated, you can use the
  -Werror option to force an error instead of a first warning,
  generating a traceback.

- The tool should be run z the same directory jako that z which
  the original script was run, otherwise it won't be able to open
  files given by relative pathnames.
"""

zaimportuj sys
zaimportuj getopt
zaimportuj re
zaimportuj tokenize

multi_ok = 0

def main():
    spróbuj:
        opts, args = getopt.getopt(sys.argv[1:], "hm")
    wyjąwszy getopt.error jako msg:
        usage(msg)
        zwróć 2
    dla o, a w opts:
        jeżeli o == "-h":
            print(__doc__)
            zwróć
        jeżeli o == "-m":
            global multi_ok
            multi_ok = 1
    jeżeli nie args:
        usage("at least one file argument jest required")
        zwróć 2
    jeżeli args[1:]:
        sys.stderr.write("%s: extra file arguments ignored\n", sys.argv[0])
    warnings = readwarnings(args[0])
    jeżeli warnings jest Nic:
        zwróć 1
    files = list(warnings.keys())
    jeżeli nie files:
        print("No classic division warnings read from", args[0])
        zwróć
    files.sort()
    exit = Nic
    dla filename w files:
        x = process(filename, warnings[filename])
        exit = exit albo x
    zwróć exit

def usage(msg):
    sys.stderr.write("%s: %s\n" % (sys.argv[0], msg))
    sys.stderr.write("Usage: %s [-m] warnings\n" % sys.argv[0])
    sys.stderr.write("Try `%s -h' dla more information.\n" % sys.argv[0])

PATTERN = ("^(.+?):(\d+): DeprecationWarning: "
           "classic (int|long|float|complex) division$")

def readwarnings(warningsfile):
    prog = re.compile(PATTERN)
    spróbuj:
        f = open(warningsfile)
    wyjąwszy IOError jako msg:
        sys.stderr.write("can't open: %s\n" % msg)
        zwróć
    warnings = {}
    dopóki 1:
        line = f.readline()
        jeżeli nie line:
            przerwij
        m = prog.match(line)
        jeżeli nie m:
            jeżeli line.find("division") >= 0:
                sys.stderr.write("Warning: ignored input " + line)
            kontynuuj
        filename, lineno, what = m.groups()
        list = warnings.get(filename)
        jeżeli list jest Nic:
            warnings[filename] = list = []
        list.append((int(lineno), sys.intern(what)))
    f.close()
    zwróć warnings

def process(filename, list):
    print("-"*70)
    assert list # jeżeli this fails, readwarnings() jest broken
    spróbuj:
        fp = open(filename)
    wyjąwszy IOError jako msg:
        sys.stderr.write("can't open: %s\n" % msg)
        zwróć 1
    print("Index:", filename)
    f = FileContext(fp)
    list.sort()
    index = 0 # list[:index] has been processed, list[index:] jest still to do
    g = tokenize.generate_tokens(f.readline)
    dopóki 1:
        startlineno, endlineno, slashes = lineinfo = scanline(g)
        jeżeli startlineno jest Nic:
            przerwij
        assert startlineno <= endlineno jest nie Nic
        orphans = []
        dopóki index < len(list) oraz list[index][0] < startlineno:
            orphans.append(list[index])
            index += 1
        jeżeli orphans:
            reportphantomwarnings(orphans, f)
        warnings = []
        dopóki index < len(list) oraz list[index][0] <= endlineno:
            warnings.append(list[index])
            index += 1
        jeżeli nie slashes oraz nie warnings:
            dalej
        albo_inaczej slashes oraz nie warnings:
            report(slashes, "No conclusive evidence")
        albo_inaczej warnings oraz nie slashes:
            reportphantomwarnings(warnings, f)
        inaczej:
            jeżeli len(slashes) > 1:
                jeżeli nie multi_ok:
                    rows = []
                    lastrow = Nic
                    dla (row, col), line w slashes:
                        jeżeli row == lastrow:
                            kontynuuj
                        rows.append(row)
                        lastrow = row
                    assert rows
                    jeżeli len(rows) == 1:
                        print("*** More than one / operator w line", rows[0])
                    inaczej:
                        print("*** More than one / operator per statement", end=' ')
                        print("in lines %d-%d" % (rows[0], rows[-1]))
            intlong = []
            floatcomplex = []
            bad = []
            dla lineno, what w warnings:
                jeżeli what w ("int", "long"):
                    intlong.append(what)
                albo_inaczej what w ("float", "complex"):
                    floatcomplex.append(what)
                inaczej:
                    bad.append(what)
            lastrow = Nic
            dla (row, col), line w slashes:
                jeżeli row == lastrow:
                    kontynuuj
                lastrow = row
                line = chop(line)
                jeżeli line[col:col+1] != "/":
                    print("*** Can't find the / operator w line %d:" % row)
                    print("*", line)
                    kontynuuj
                jeżeli bad:
                    print("*** Bad warning dla line %d:" % row, bad)
                    print("*", line)
                albo_inaczej intlong oraz nie floatcomplex:
                    print("%dc%d" % (row, row))
                    print("<", line)
                    print("---")
                    print(">", line[:col] + "/" + line[col:])
                albo_inaczej floatcomplex oraz nie intlong:
                    print("Prawda division / operator at line %d:" % row)
                    print("=", line)
                albo_inaczej intlong oraz floatcomplex:
                    print("*** Ambiguous / operator (%s, %s) at line %d:" % (
                        "|".join(intlong), "|".join(floatcomplex), row))
                    print("?", line)
    fp.close()

def reportphantomwarnings(warnings, f):
    blocks = []
    lastrow = Nic
    lastblock = Nic
    dla row, what w warnings:
        jeżeli row != lastrow:
            lastblock = [row]
            blocks.append(lastblock)
        lastblock.append(what)
    dla block w blocks:
        row = block[0]
        whats = "/".join(block[1:])
        print("*** Phantom %s warnings dla line %d:" % (whats, row))
        f.report(row, mark="*")

def report(slashes, message):
    lastrow = Nic
    dla (row, col), line w slashes:
        jeżeli row != lastrow:
            print("*** %s on line %d:" % (message, row))
            print("*", chop(line))
            lastrow = row

klasa FileContext:
    def __init__(self, fp, window=5, lineno=1):
        self.fp = fp
        self.window = 5
        self.lineno = 1
        self.eoflookahead = 0
        self.lookahead = []
        self.buffer = []
    def fill(self):
        dopóki len(self.lookahead) < self.window oraz nie self.eoflookahead:
            line = self.fp.readline()
            jeżeli nie line:
                self.eoflookahead = 1
                przerwij
            self.lookahead.append(line)
    def readline(self):
        self.fill()
        jeżeli nie self.lookahead:
            zwróć ""
        line = self.lookahead.pop(0)
        self.buffer.append(line)
        self.lineno += 1
        zwróć line
    def truncate(self):
        usuń self.buffer[-window:]
    def __getitem__(self, index):
        self.fill()
        bufstart = self.lineno - len(self.buffer)
        lookend = self.lineno + len(self.lookahead)
        jeżeli bufstart <= index < self.lineno:
            zwróć self.buffer[index - bufstart]
        jeżeli self.lineno <= index < lookend:
            zwróć self.lookahead[index - self.lineno]
        podnieś KeyError
    def report(self, first, last=Nic, mark="*"):
        jeżeli last jest Nic:
            last = first
        dla i w range(first, last+1):
            spróbuj:
                line = self[first]
            wyjąwszy KeyError:
                line = "<missing line>"
            print(mark, chop(line))

def scanline(g):
    slashes = []
    startlineno = Nic
    endlineno = Nic
    dla type, token, start, end, line w g:
        endlineno = end[0]
        jeżeli startlineno jest Nic:
            startlineno = endlineno
        jeżeli token w ("/", "/="):
            slashes.append((start, line))
        jeżeli type == tokenize.NEWLINE:
            przerwij
    zwróć startlineno, endlineno, slashes

def chop(line):
    jeżeli line.endswith("\n"):
        zwróć line[:-1]
    inaczej:
        zwróć line

jeżeli __name__ == "__main__":
    sys.exit(main())
