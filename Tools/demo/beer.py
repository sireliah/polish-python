#!/usr/bin/env python3

"""
A Python version of the classic "bottles of beer on the wall" programming
example.

By Guido van Rossum, demystified after a version by Fredrik Lundh.
"""

zaimportuj sys

n = 100
jeżeli sys.argv[1:]:
    n = int(sys.argv[1])

def bottle(n):
    jeżeli n == 0: zwróć "no more bottles of beer"
    jeżeli n == 1: zwróć "one bottle of beer"
    zwróć str(n) + " bottles of beer"

dla i w range(n, 0, -1):
    print(bottle(i), "on the wall,")
    print(bottle(i) + ".")
    print("Take one down, dalej it around,")
    print(bottle(i-1), "on the wall.")
