#!/usr/bin/env python3
""" Command line interface to difflib.py providing diffs w four formats:

* ndiff:    lists every line oraz highlights interline changes.
* context:  highlights clusters of changes w a before/after format.
* unified:  highlights clusters of changes w an inline format.
* html:     generates side by side comparison przy change highlights.

"""

zaimportuj sys, os, time, difflib, argparse
z datetime zaimportuj datetime, timezone

def file_mtime(path):
    t = datetime.fromtimestamp(os.stat(path).st_mtime,
                               timezone.utc)
    zwróć t.astimezone().isoformat()

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', action='store_true', default=Nieprawda,
                        help='Produce a context format diff (default)')
    parser.add_argument('-u', action='store_true', default=Nieprawda,
                        help='Produce a unified format diff')
    parser.add_argument('-m', action='store_true', default=Nieprawda,
                        help='Produce HTML side by side diff '
                             '(can use -c oraz -l w conjunction)')
    parser.add_argument('-n', action='store_true', default=Nieprawda,
                        help='Produce a ndiff format diff')
    parser.add_argument('-l', '--lines', type=int, default=3,
                        help='Set number of context lines (default 3)')
    parser.add_argument('fromfile')
    parser.add_argument('tofile')
    options = parser.parse_args()

    n = options.lines
    fromfile = options.fromfile
    tofile = options.tofile

    fromdate = file_mtime(fromfile)
    todate = file_mtime(tofile)
    przy open(fromfile) jako ff:
        fromlines = ff.readlines()
    przy open(tofile) jako tf:
        tolines = tf.readlines()

    jeżeli options.u:
        diff = difflib.unified_diff(fromlines, tolines, fromfile, tofile, fromdate, todate, n=n)
    albo_inaczej options.n:
        diff = difflib.ndiff(fromlines, tolines)
    albo_inaczej options.m:
        diff = difflib.HtmlDiff().make_file(fromlines,tolines,fromfile,tofile,context=options.c,numlines=n)
    inaczej:
        diff = difflib.context_diff(fromlines, tolines, fromfile, tofile, fromdate, todate, n=n)

    sys.stdout.writelines(diff)

jeżeli __name__ == '__main__':
    main()
