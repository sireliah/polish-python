#! /usr/bin/env python3

# Released to the public domain, by Tim Peters, 03 October 2000.

"""reindent [-d][-r][-v] [ path ... ]

-d (--dryrun)   Dry run.   Analyze, but don't make any changes to, files.
-r (--recurse)  Recurse.   Search dla all .py files w subdirectories too.
-n (--nobackup) No backup. Does nie make a ".bak" file before reindenting.
-v (--verbose)  Verbose.   Print informative msgs; inaczej no output.
   (--newline)  Newline.   Specify the newline character to use (CRLF, LF).
                           Default jest the same jako the original file.
-h (--help)     Help.      Print this usage information oraz exit.

Change Python (.py) files to use 4-space indents oraz no hard tab characters.
Also trim excess spaces oraz tabs z ends of lines, oraz remove empty lines
at the end of files.  Also ensure the last line ends przy a newline.

If no paths are given on the command line, reindent operates jako a filter,
reading a single source file z standard input oraz writing the transformed
source to standard output.  In this case, the -d, -r oraz -v flags are
ignored.

You can dalej one albo more file and/or directory paths.  When a directory
path, all .py files within the directory will be examined, and, jeżeli the -r
option jest given, likewise recursively dla subdirectories.

If output jest nie to standard output, reindent overwrites files w place,
renaming the originals przy a .bak extension.  If it finds nothing to
change, the file jest left alone.  If reindent does change a file, the changed
file jest a fixed-point dla future runs (i.e., running reindent on the
resulting .py file won't change it again).

The hard part of reindenting jest figuring out what to do przy comment
lines.  So long jako the input files get a clean bill of health from
tabnanny.py, reindent should do a good job.

The backup file jest a copy of the one that jest being reindented. The ".bak"
file jest generated przy shutil.copy(), but some corner cases regarding
user/group oraz permissions could leave the backup file more readable than
you'd prefer. You can always use the --nobackup option to prevent this.
"""

__version__ = "1"

zaimportuj tokenize
zaimportuj os
zaimportuj shutil
zaimportuj sys

verbose = Nieprawda
recurse = Nieprawda
dryrun = Nieprawda
makebackup = Prawda
# A specified newline to be used w the output (set by --newline option)
spec_newline = Nic


def usage(msg=Nic):
    jeżeli msg jest Nic:
        msg = __doc__
    print(msg, file=sys.stderr)


def errprint(*args):
    sys.stderr.write(" ".join(str(arg) dla arg w args))
    sys.stderr.write("\n")

def main():
    zaimportuj getopt
    global verbose, recurse, dryrun, makebackup, spec_newline
    spróbuj:
        opts, args = getopt.getopt(sys.argv[1:], "drnvh",
            ["dryrun", "recurse", "nobackup", "verbose", "newline=", "help"])
    wyjąwszy getopt.error jako msg:
        usage(msg)
        zwróć
    dla o, a w opts:
        jeżeli o w ('-d', '--dryrun'):
            dryrun = Prawda
        albo_inaczej o w ('-r', '--recurse'):
            recurse = Prawda
        albo_inaczej o w ('-n', '--nobackup'):
            makebackup = Nieprawda
        albo_inaczej o w ('-v', '--verbose'):
            verbose = Prawda
        albo_inaczej o w ('--newline',):
            jeżeli nie a.upper() w ('CRLF', 'LF'):
                usage()
                zwróć
            spec_newline = dict(CRLF='\r\n', LF='\n')[a.upper()]
        albo_inaczej o w ('-h', '--help'):
            usage()
            zwróć
    jeżeli nie args:
        r = Reindenter(sys.stdin)
        r.run()
        r.write(sys.stdout)
        zwróć
    dla arg w args:
        check(arg)


def check(file):
    jeżeli os.path.isdir(file) oraz nie os.path.islink(file):
        jeżeli verbose:
            print("listing directory", file)
        names = os.listdir(file)
        dla name w names:
            fullname = os.path.join(file, name)
            jeżeli ((recurse oraz os.path.isdir(fullname) oraz
                 nie os.path.islink(fullname) oraz
                 nie os.path.split(fullname)[1].startswith("."))
                albo name.lower().endswith(".py")):
                check(fullname)
        zwróć

    jeżeli verbose:
        print("checking", file, "...", end=' ')
    przy open(file, 'rb') jako f:
        encoding, _ = tokenize.detect_encoding(f.readline)
    spróbuj:
        przy open(file, encoding=encoding) jako f:
            r = Reindenter(f)
    wyjąwszy IOError jako msg:
        errprint("%s: I/O Error: %s" % (file, str(msg)))
        zwróć

    newline = spec_newline jeżeli spec_newline inaczej r.newlines
    jeżeli isinstance(newline, tuple):
        errprint("%s: mixed newlines detected; cannot continue without --newline" % file)
        zwróć

    jeżeli r.run():
        jeżeli verbose:
            print("changed.")
            jeżeli dryrun:
                print("But this jest a dry run, so leaving it alone.")
        jeżeli nie dryrun:
            bak = file + ".bak"
            jeżeli makebackup:
                shutil.copyfile(file, bak)
                jeżeli verbose:
                    print("backed up", file, "to", bak)
            przy open(file, "w", encoding=encoding, newline=newline) jako f:
                r.write(f)
            jeżeli verbose:
                print("wrote new", file)
        zwróć Prawda
    inaczej:
        jeżeli verbose:
            print("unchanged.")
        zwróć Nieprawda


def _rstrip(line, JUNK='\n \t'):
    """Return line stripped of trailing spaces, tabs, newlines.

    Note that line.rstrip() instead also strips sundry control characters,
    but at least one known Emacs user expects to keep junk like that, nie
    mentioning Barry by name albo anything <wink>.
    """

    i = len(line)
    dopóki i > 0 oraz line[i - 1] w JUNK:
        i -= 1
    zwróć line[:i]


klasa Reindenter:

    def __init__(self, f):
        self.find_stmt = 1  # next token begins a fresh stmt?
        self.level = 0      # current indent level

        # Raw file lines.
        self.raw = f.readlines()

        # File lines, rstripped & tab-expanded.  Dummy at start jest so
        # that we can use tokenize's 1-based line numbering easily.
        # Note that a line jest all-blank iff it's "\n".
        self.lines = [_rstrip(line).expandtabs() + "\n"
                      dla line w self.raw]
        self.lines.insert(0, Nic)
        self.index = 1  # index into self.lines of next line

        # List of (lineno, indentlevel) pairs, one dla each stmt oraz
        # comment line.  indentlevel jest -1 dla comment lines, jako a
        # signal that tokenize doesn't know what to do about them;
        # indeed, they're our headache!
        self.stats = []

        # Save the newlines found w the file so they can be used to
        #  create output without mutating the newlines.
        self.newlines = f.newlines

    def run(self):
        tokens = tokenize.generate_tokens(self.getline)
        dla _token w tokens:
            self.tokeneater(*_token)
        # Remove trailing empty lines.
        lines = self.lines
        dopóki lines oraz lines[-1] == "\n":
            lines.pop()
        # Sentinel.
        stats = self.stats
        stats.append((len(lines), 0))
        # Map count of leading spaces to # we want.
        have2want = {}
        # Program after transformation.
        after = self.after = []
        # Copy over initial empty lines -- there's nothing to do until
        # we see a line przy *something* on it.
        i = stats[0][0]
        after.extend(lines[1:i])
        dla i w range(len(stats) - 1):
            thisstmt, thislevel = stats[i]
            nextstmt = stats[i + 1][0]
            have = getlspace(lines[thisstmt])
            want = thislevel * 4
            jeżeli want < 0:
                # A comment line.
                jeżeli have:
                    # An indented comment line.  If we saw the same
                    # indentation before, reuse what it most recently
                    # mapped to.
                    want = have2want.get(have, -1)
                    jeżeli want < 0:
                        # Then it probably belongs to the next real stmt.
                        dla j w range(i + 1, len(stats) - 1):
                            jline, jlevel = stats[j]
                            jeżeli jlevel >= 0:
                                jeżeli have == getlspace(lines[jline]):
                                    want = jlevel * 4
                                przerwij
                    jeżeli want < 0:           # Maybe it's a hanging
                                           # comment like this one,
                        # w which case we should shift it like its base
                        # line got shifted.
                        dla j w range(i - 1, -1, -1):
                            jline, jlevel = stats[j]
                            jeżeli jlevel >= 0:
                                want = have + (getlspace(after[jline - 1]) -
                                               getlspace(lines[jline]))
                                przerwij
                    jeżeli want < 0:
                        # Still no luck -- leave it alone.
                        want = have
                inaczej:
                    want = 0
            assert want >= 0
            have2want[have] = want
            diff = want - have
            jeżeli diff == 0 albo have == 0:
                after.extend(lines[thisstmt:nextstmt])
            inaczej:
                dla line w lines[thisstmt:nextstmt]:
                    jeżeli diff > 0:
                        jeżeli line == "\n":
                            after.append(line)
                        inaczej:
                            after.append(" " * diff + line)
                    inaczej:
                        remove = min(getlspace(line), -diff)
                        after.append(line[remove:])
        zwróć self.raw != self.after

    def write(self, f):
        f.writelines(self.after)

    # Line-getter dla tokenize.
    def getline(self):
        jeżeli self.index >= len(self.lines):
            line = ""
        inaczej:
            line = self.lines[self.index]
            self.index += 1
        zwróć line

    # Line-eater dla tokenize.
    def tokeneater(self, type, token, slinecol, end, line,
                   INDENT=tokenize.INDENT,
                   DEDENT=tokenize.DEDENT,
                   NEWLINE=tokenize.NEWLINE,
                   COMMENT=tokenize.COMMENT,
                   NL=tokenize.NL):

        jeżeli type == NEWLINE:
            # A program statement, albo ENDMARKER, will eventually follow,
            # after some (possibly empty) run of tokens of the form
            #     (NL | COMMENT)* (INDENT | DEDENT+)?
            self.find_stmt = 1

        albo_inaczej type == INDENT:
            self.find_stmt = 1
            self.level += 1

        albo_inaczej type == DEDENT:
            self.find_stmt = 1
            self.level -= 1

        albo_inaczej type == COMMENT:
            jeżeli self.find_stmt:
                self.stats.append((slinecol[0], -1))
                # but we're still looking dla a new stmt, so leave
                # find_stmt alone

        albo_inaczej type == NL:
            dalej

        albo_inaczej self.find_stmt:
            # This jest the first "real token" following a NEWLINE, so it
            # must be the first token of the next program statement, albo an
            # ENDMARKER.
            self.find_stmt = 0
            jeżeli line:   # nie endmarker
                self.stats.append((slinecol[0], self.level))


# Count number of leading blanks.
def getlspace(line):
    i, n = 0, len(line)
    dopóki i < n oraz line[i] == " ":
        i += 1
    zwróć i


jeżeli __name__ == '__main__':
    main()
