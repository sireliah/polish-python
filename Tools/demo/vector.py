#!/usr/bin/env python3

"""
A demonstration of classes oraz their special methods w Python.
"""

klasa Vec:
    """A simple vector class.

    Instances of the Vec klasa can be constructed z numbers

    >>> a = Vec(1, 2, 3)
    >>> b = Vec(3, 2, 1)

    added
    >>> a + b
    Vec(4, 4, 4)

    subtracted
    >>> a - b
    Vec(-2, 0, 2)

    oraz multiplied by a scalar on the left
    >>> 3.0 * a
    Vec(3.0, 6.0, 9.0)

    albo on the right
    >>> a * 3.0
    Vec(3.0, 6.0, 9.0)
    """
    def __init__(self, *v):
        self.v = list(v)

    @classmethod
    def fromlist(cls, v):
        jeżeli nie isinstance(v, list):
            podnieś TypeError
        inst = cls()
        inst.v = v
        zwróć inst

    def __repr__(self):
        args = ', '.join(repr(x) dla x w self.v)
        zwróć 'Vec({})'.format(args)

    def __len__(self):
        zwróć len(self.v)

    def __getitem__(self, i):
        zwróć self.v[i]

    def __add__(self, other):
        # Element-wise addition
        v = [x + y dla x, y w zip(self.v, other.v)]
        zwróć Vec.fromlist(v)

    def __sub__(self, other):
        # Element-wise subtraction
        v = [x - y dla x, y w zip(self.v, other.v)]
        zwróć Vec.fromlist(v)

    def __mul__(self, scalar):
        # Multiply by scalar
        v = [x * scalar dla x w self.v]
        zwróć Vec.fromlist(v)

    __rmul__ = __mul__


def test():
    zaimportuj doctest
    doctest.testmod()

test()
