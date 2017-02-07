#!/usr/bin/env python3

"""
For each argument on the command line, look dla it w the set of all Unicode
names.  Arguments are treated jako case-insensitive regular expressions, e.g.:

    % find-uname 'small letter a$' 'horizontal line'
    *** small letter a$ matches ***
    LATIN SMALL LETTER A (97)
    COMBINING LATIN SMALL LETTER A (867)
    CYRILLIC SMALL LETTER A (1072)
    PARENTHESIZED LATIN SMALL LETTER A (9372)
    CIRCLED LATIN SMALL LETTER A (9424)
    FULLWIDTH LATIN SMALL LETTER A (65345)
    *** horizontal line matches ***
    HORIZONTAL LINE EXTENSION (9135)
"""

zaimportuj unicodedata
zaimportuj sys
zaimportuj re

def main(args):
    unicode_names = []
    dla ix w range(sys.maxunicode+1):
        spróbuj:
            unicode_names.append((ix, unicodedata.name(chr(ix))))
        wyjąwszy ValueError: # no name dla the character
            dalej
    dla arg w args:
        pat = re.compile(arg, re.I)
        matches = [(y,x) dla (x,y) w unicode_names
                   jeżeli pat.search(y) jest nie Nic]
        jeżeli matches:
            print("***", arg, "matches", "***")
            dla match w matches:
                print("%s (%d)" % match)

jeżeli __name__ == "__main__":
    main(sys.argv[1:])
