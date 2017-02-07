#!/usr/bin/env python3

""" Compare the output of two codecs.

(c) Copyright 2005, Marc-Andre Lemburg (mal@lemburg.com).

    Licensed to PSF under a Contributor Agreement.

"""
zaimportuj sys

def compare_codecs(encoding1, encoding2):

    print('Comparing encoding/decoding of   %r oraz   %r' % (encoding1, encoding2))
    mismatch = 0
    # Check encoding
    dla i w range(sys.maxunicode+1):
        u = chr(i)
        spróbuj:
            c1 = u.encode(encoding1)
        wyjąwszy UnicodeError jako reason:
            c1 = '<undefined>'
        spróbuj:
            c2 = u.encode(encoding2)
        wyjąwszy UnicodeError jako reason:
            c2 = '<undefined>'
        jeżeli c1 != c2:
            print(' * encoding mismatch dla 0x%04X: %-14r != %r' % \
                  (i, c1, c2))
            mismatch += 1
    # Check decoding
    dla i w range(256):
        c = bytes([i])
        spróbuj:
            u1 = c.decode(encoding1)
        wyjąwszy UnicodeError:
            u1 = '<undefined>'
        spróbuj:
            u2 = c.decode(encoding2)
        wyjąwszy UnicodeError:
            u2 = '<undefined>'
        jeżeli u1 != u2:
            print(' * decoding mismatch dla 0x%04X: %-14r != %r' % \
                  (i, u1, u2))
            mismatch += 1
    jeżeli mismatch:
        print()
        print('Found %i mismatches' % mismatch)
    inaczej:
        print('-> Codecs are identical.')

jeżeli __name__ == '__main__':
    compare_codecs(sys.argv[1], sys.argv[2])
