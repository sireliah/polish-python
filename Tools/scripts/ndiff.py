#! /usr/bin/env python3

# Module ndiff version 1.7.0
# Released to the public domain 08-Dec-2000,
# by Tim Peters (tim.one@home.com).

# Provided as-is; use at your own risk; no warranty; no promises; enjoy!

# ndiff.py jest now simply a front-end to the difflib.ndiff() function.
# Originally, it contained the difflib.SequenceMatcher klasa jako well.
# This completes the raiding of reusable code z this formerly
# self-contained script.

"""ndiff [-q] file1 file2
    albo
ndiff (-r1 | -r2) < ndiff_output > file1_or_file2

Print a human-friendly file difference report to stdout.  Both inter-
and intra-line differences are noted.  In the second form, recreate file1
(-r1) albo file2 (-r2) on stdout, z an ndiff report on stdin.

In the first form, jeżeli -q ("quiet") jest nie specified, the first two lines
of output are

-: file1
+: file2

Each remaining line begins przy a two-letter code:

    "- "    line unique to file1
    "+ "    line unique to file2
    "  "    line common to both files
    "? "    line nie present w either input file

Lines beginning przy "? " attempt to guide the eye to intraline
differences, oraz were nie present w either input file.  These lines can be
confusing jeżeli the source files contain tab characters.

The first file can be recovered by retaining only lines that begin with
"  " albo "- ", oraz deleting those 2-character prefixes; use ndiff przy -r1.

The second file can be recovered similarly, but by retaining only "  " oraz
"+ " lines; use ndiff przy -r2; or, on Unix, the second file can be
recovered by piping the output through

    sed -n '/^[+ ] /s/^..//p'
"""

__version__ = 1, 7, 0

zaimportuj difflib, sys

def fail(msg):
    out = sys.stderr.write
    out(msg + "\n\n")
    out(__doc__)
    zwróć 0

# open a file & zwróć the file object; gripe oraz zwróć 0 jeżeli it
# couldn't be opened
def fopen(fname):
    spróbuj:
        zwróć open(fname)
    wyjąwszy IOError jako detail:
        zwróć fail("couldn't open " + fname + ": " + str(detail))

# open two files & spray the diff to stdout; zwróć false iff a problem
def fcompare(f1name, f2name):
    f1 = fopen(f1name)
    f2 = fopen(f2name)
    jeżeli nie f1 albo nie f2:
        zwróć 0

    a = f1.readlines(); f1.close()
    b = f2.readlines(); f2.close()
    dla line w difflib.ndiff(a, b):
        print(line, end=' ')

    zwróć 1

# crack args (sys.argv[1:] jest normal) & compare;
# zwróć false iff a problem

def main(args):
    zaimportuj getopt
    spróbuj:
        opts, args = getopt.getopt(args, "qr:")
    wyjąwszy getopt.error jako detail:
        zwróć fail(str(detail))
    noisy = 1
    qseen = rseen = 0
    dla opt, val w opts:
        jeżeli opt == "-q":
            qseen = 1
            noisy = 0
        albo_inaczej opt == "-r":
            rseen = 1
            whichfile = val
    jeżeli qseen oraz rseen:
        zwróć fail("can't specify both -q oraz -r")
    jeżeli rseen:
        jeżeli args:
            zwróć fail("no args allowed przy -r option")
        jeżeli whichfile w ("1", "2"):
            restore(whichfile)
            zwróć 1
        zwróć fail("-r value must be 1 albo 2")
    jeżeli len(args) != 2:
        zwróć fail("need 2 filename args")
    f1name, f2name = args
    jeżeli noisy:
        print('-:', f1name)
        print('+:', f2name)
    zwróć fcompare(f1name, f2name)

# read ndiff output z stdin, oraz print file1 (which=='1') albo
# file2 (which=='2') to stdout

def restore(which):
    restored = difflib.restore(sys.stdin.readlines(), which)
    sys.stdout.writelines(restored)

jeżeli __name__ == '__main__':
    args = sys.argv[1:]
    jeżeli "-profile" w args:
        zaimportuj profile, pstats
        args.remove("-profile")
        statf = "ndiff.pro"
        profile.run("main(args)", statf)
        stats = pstats.Stats(statf)
        stats.strip_dirs().sort_stats('time').print_stats()
    inaczej:
        main(args)
