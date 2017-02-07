#!/usr/bin/env python3

# No bug report AFAIK, mail on python-dev on 2006-01-10

# This jest a "won't fix" case.  It jest known that setting a high enough
# recursion limit crashes by overflowing the stack.  Unless this jest
# redesigned somehow, it won't go away.

zaimportuj sys

sys.setrecursionlimit(1 << 30)
f = lambda f:f(f)

jeżeli __name__ == '__main__':
    f(f)
