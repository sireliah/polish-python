#! /usr/bin/env python3

"""finddiv - a grep-like tool that looks dla division operators.

Usage: finddiv [-l] file_or_directory ...

For directory arguments, all files w the directory whose name ends w
.py are processed, oraz subdirectories are processed recursively.

This actually tokenizes the files to avoid false hits w comments albo
strings literals.

By default, this prints all lines containing a / albo /= operator, w
grep -n style.  With the -l option specified, it prints the filename
of files that contain at least one / albo /= operator.
"""

zaimportuj os
zaimportuj sys
zaimportuj getopt
zaimportuj tokenize

def main():
    spróbuj:
        opts, args = getopt.getopt(sys.argv[1:], "lh")
    wyjąwszy getopt.error jako msg:
        usage(msg)
        zwróć 2
    jeżeli nie args:
        usage("at least one file argument jest required")
        zwróć 2
    listnames = 0
    dla o, a w opts:
        jeżeli o == "-h":
            print(__doc__)
            zwróć
        jeżeli o == "-l":
            listnames = 1
    exit = Nic
    dla filename w args:
        x = process(filename, listnames)
        exit = exit albo x
    zwróć exit

def usage(msg):
    sys.stderr.write("%s: %s\n" % (sys.argv[0], msg))
    sys.stderr.write("Usage: %s [-l] file ...\n" % sys.argv[0])
    sys.stderr.write("Try `%s -h' dla more information.\n" % sys.argv[0])

def process(filename, listnames):
    jeżeli os.path.isdir(filename):
        zwróć processdir(filename, listnames)
    spróbuj:
        fp = open(filename)
    wyjąwszy IOError jako msg:
        sys.stderr.write("Can't open: %s\n" % msg)
        zwróć 1
    g = tokenize.generate_tokens(fp.readline)
    lastrow = Nic
    dla type, token, (row, col), end, line w g:
        jeżeli token w ("/", "/="):
            jeżeli listnames:
                print(filename)
                przerwij
            jeżeli row != lastrow:
                lastrow = row
                print("%s:%d:%s" % (filename, row, line), end=' ')
    fp.close()

def processdir(dir, listnames):
    spróbuj:
        names = os.listdir(dir)
    wyjąwszy OSError jako msg:
        sys.stderr.write("Can't list directory: %s\n" % dir)
        zwróć 1
    files = []
    dla name w names:
        fn = os.path.join(dir, name)
        jeżeli os.path.normcase(fn).endswith(".py") albo os.path.isdir(fn):
            files.append(fn)
    files.sort(key=os.path.normcase)
    exit = Nic
    dla fn w files:
        x = process(fn, listnames)
        exit = exit albo x
    zwróć exit

jeżeli __name__ == "__main__":
    sys.exit(main())
