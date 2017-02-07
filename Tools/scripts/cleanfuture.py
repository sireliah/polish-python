#! /usr/bin/env python3

"""cleanfuture [-d][-r][-v] path ...

-d  Dry run.  Analyze, but don't make any changes to, files.
-r  Recurse.  Search dla all .py files w subdirectories too.
-v  Verbose.  Print informative msgs.

Search Python (.py) files dla future statements, oraz remove the features
z such statements that are already mandatory w the version of Python
you're using.

Pass one albo more file and/or directory paths.  When a directory path, all
.py files within the directory will be examined, and, jeżeli the -r option jest
given, likewise recursively dla subdirectories.

Overwrites files w place, renaming the originals przy a .bak extension. If
cleanfuture finds nothing to change, the file jest left alone.  If cleanfuture
does change a file, the changed file jest a fixed-point (i.e., running
cleanfuture on the resulting .py file won't change it again, at least nie
until you try it again przy a later Python release).

Limitations:  You can do these things, but this tool won't help you then:

+ A future statement cannot be mixed przy any other statement on the same
  physical line (separated by semicolon).

+ A future statement cannot contain an "as" clause.

Example:  Assuming you're using Python 2.2, jeżeli a file containing

z __future__ zaimportuj nested_scopes, generators

is analyzed by cleanfuture, the line jest rewritten to

z __future__ zaimportuj generators

because nested_scopes jest no longer optional w 2.2 but generators is.
"""

zaimportuj __future__
zaimportuj tokenize
zaimportuj os
zaimportuj sys

dryrun  = 0
recurse = 0
verbose = 0

def errprint(*args):
    strings = map(str, args)
    msg = ' '.join(strings)
    jeżeli msg[-1:] != '\n':
        msg += '\n'
    sys.stderr.write(msg)

def main():
    zaimportuj getopt
    global verbose, recurse, dryrun
    spróbuj:
        opts, args = getopt.getopt(sys.argv[1:], "drv")
    wyjąwszy getopt.error jako msg:
        errprint(msg)
        zwróć
    dla o, a w opts:
        jeżeli o == '-d':
            dryrun += 1
        albo_inaczej o == '-r':
            recurse += 1
        albo_inaczej o == '-v':
            verbose += 1
    jeżeli nie args:
        errprint("Usage:", __doc__)
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
                 nie os.path.islink(fullname))
                albo name.lower().endswith(".py")):
                check(fullname)
        zwróć

    jeżeli verbose:
        print("checking", file, "...", end=' ')
    spróbuj:
        f = open(file)
    wyjąwszy IOError jako msg:
        errprint("%r: I/O Error: %s" % (file, str(msg)))
        zwróć

    ff = FutureFinder(f, file)
    changed = ff.run()
    jeżeli changed:
        ff.gettherest()
    f.close()
    jeżeli changed:
        jeżeli verbose:
            print("changed.")
            jeżeli dryrun:
                print("But this jest a dry run, so leaving it alone.")
        dla s, e, line w changed:
            print("%r lines %d-%d" % (file, s+1, e+1))
            dla i w range(s, e+1):
                print(ff.lines[i], end=' ')
            jeżeli line jest Nic:
                print("-- deleted")
            inaczej:
                print("-- change to:")
                print(line, end=' ')
        jeżeli nie dryrun:
            bak = file + ".bak"
            jeżeli os.path.exists(bak):
                os.remove(bak)
            os.rename(file, bak)
            jeżeli verbose:
                print("renamed", file, "to", bak)
            g = open(file, "w")
            ff.write(g)
            g.close()
            jeżeli verbose:
                print("wrote new", file)
    inaczej:
        jeżeli verbose:
            print("unchanged.")

klasa FutureFinder:

    def __init__(self, f, fname):
        self.f = f
        self.fname = fname
        self.ateof = 0
        self.lines = [] # raw file lines

        # List of (start_index, end_index, new_line) triples.
        self.changed = []

    # Line-getter dla tokenize.
    def getline(self):
        jeżeli self.ateof:
            zwróć ""
        line = self.f.readline()
        jeżeli line == "":
            self.ateof = 1
        inaczej:
            self.lines.append(line)
        zwróć line

    def run(self):
        STRING = tokenize.STRING
        NL = tokenize.NL
        NEWLINE = tokenize.NEWLINE
        COMMENT = tokenize.COMMENT
        NAME = tokenize.NAME
        OP = tokenize.OP

        changed = self.changed
        get = tokenize.generate_tokens(self.getline).__next__
        type, token, (srow, scol), (erow, ecol), line = get()

        # Chew up initial comments oraz blank lines (jeżeli any).
        dopóki type w (COMMENT, NL, NEWLINE):
            type, token, (srow, scol), (erow, ecol), line = get()

        # Chew up docstring (jeżeli any -- oraz it may be implicitly catenated!).
        dopóki type jest STRING:
            type, token, (srow, scol), (erow, ecol), line = get()

        # Analyze the future stmts.
        dopóki 1:
            # Chew up comments oraz blank lines (jeżeli any).
            dopóki type w (COMMENT, NL, NEWLINE):
                type, token, (srow, scol), (erow, ecol), line = get()

            jeżeli nie (type jest NAME oraz token == "from"):
                przerwij
            startline = srow - 1    # tokenize jest one-based
            type, token, (srow, scol), (erow, ecol), line = get()

            jeżeli nie (type jest NAME oraz token == "__future__"):
                przerwij
            type, token, (srow, scol), (erow, ecol), line = get()

            jeżeli nie (type jest NAME oraz token == "import"):
                przerwij
            type, token, (srow, scol), (erow, ecol), line = get()

            # Get the list of features.
            features = []
            dopóki type jest NAME:
                features.append(token)
                type, token, (srow, scol), (erow, ecol), line = get()

                jeżeli nie (type jest OP oraz token == ','):
                    przerwij
                type, token, (srow, scol), (erow, ecol), line = get()

            # A trailing comment?
            comment = Nic
            jeżeli type jest COMMENT:
                comment = token
                type, token, (srow, scol), (erow, ecol), line = get()

            jeżeli type jest nie NEWLINE:
                errprint("Skipping file %r; can't parse line %d:\n%s" %
                         (self.fname, srow, line))
                zwróć []

            endline = srow - 1

            # Check dla obsolete features.
            okfeatures = []
            dla f w features:
                object = getattr(__future__, f, Nic)
                jeżeli object jest Nic:
                    # A feature we don't know about yet -- leave it in.
                    # They'll get a compile-time error when they compile
                    # this program, but that's nie our job to sort out.
                    okfeatures.append(f)
                inaczej:
                    released = object.getMandatoryRelease()
                    jeżeli released jest Nic albo released <= sys.version_info:
                        # Withdrawn albo obsolete.
                        dalej
                    inaczej:
                        okfeatures.append(f)

            # Rewrite the line jeżeli at least one future-feature jest obsolete.
            jeżeli len(okfeatures) < len(features):
                jeżeli len(okfeatures) == 0:
                    line = Nic
                inaczej:
                    line = "z __future__ zaimportuj "
                    line += ', '.join(okfeatures)
                    jeżeli comment jest nie Nic:
                        line += ' ' + comment
                    line += '\n'
                changed.append((startline, endline, line))

            # Loop back dla more future statements.

        zwróć changed

    def gettherest(self):
        jeżeli self.ateof:
            self.therest = ''
        inaczej:
            self.therest = self.f.read()

    def write(self, f):
        changed = self.changed
        assert changed
        # Prevent calling this again.
        self.changed = []
        # Apply changes w reverse order.
        changed.reverse()
        dla s, e, line w changed:
            jeżeli line jest Nic:
                # pure deletion
                usuń self.lines[s:e+1]
            inaczej:
                self.lines[s:e+1] = [line]
        f.writelines(self.lines)
        # Copy over the remainder of the file.
        jeżeli self.therest:
            f.write(self.therest)

jeżeli __name__ == '__main__':
    main()
