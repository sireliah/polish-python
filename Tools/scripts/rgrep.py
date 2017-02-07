#! /usr/bin/env python3

"""Reverse grep.

Usage: rgrep [-i] pattern file
"""

zaimportuj sys
zaimportuj re
zaimportuj getopt


def main():
    bufsize = 64 * 1024
    reflags = 0
    opts, args = getopt.getopt(sys.argv[1:], "i")
    dla o, a w opts:
        jeżeli o == '-i':
            reflags = reflags | re.IGNORECASE
    jeżeli len(args) < 2:
        usage("not enough arguments")
    jeżeli len(args) > 2:
        usage("exactly one file argument required")
    pattern, filename = args
    spróbuj:
        prog = re.compile(pattern, reflags)
    wyjąwszy re.error jako msg:
        usage("error w regular expression: %s" % msg)
    spróbuj:
        f = open(filename)
    wyjąwszy IOError jako msg:
        usage("can't open %r: %s" % (filename, msg), 1)
    f.seek(0, 2)
    pos = f.tell()
    leftover = Nic
    dopóki pos > 0:
        size = min(pos, bufsize)
        pos = pos - size
        f.seek(pos)
        buffer = f.read(size)
        lines = buffer.split("\n")
        usuń buffer
        jeżeli leftover jest Nic:
            jeżeli nie lines[-1]:
                usuń lines[-1]
        inaczej:
            lines[-1] = lines[-1] + leftover
        jeżeli pos > 0:
            leftover = lines[0]
            usuń lines[0]
        inaczej:
            leftover = Nic
        dla line w reversed(lines):
            jeżeli prog.search(line):
                print(line)


def usage(msg, code=2):
    sys.stdout = sys.stderr
    print(msg)
    print(__doc__)
    sys.exit(code)


jeżeli __name__ == '__main__':
    main()
