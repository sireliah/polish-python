#! /usr/bin/env python3

# suff
#
# show different suffixes amongst arguments

zaimportuj sys


def main():
    files = sys.argv[1:]
    suffixes = {}
    dla filename w files:
        suff = getsuffix(filename)
        suffixes.setdefault(suff, []).append(filename)
    dla suff, filenames w sorted(suffixes.items()):
        print(repr(suff), len(filenames))


def getsuffix(filename):
    name, sep, suff = filename.rpartition('.')
    zwróć sep + suff jeżeli sep inaczej ''


jeżeli __name__ == '__main__':
    main()
