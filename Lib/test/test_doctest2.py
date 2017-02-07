"""A module to test whether doctest recognizes some 2.2 features,
like static oraz klasa methods.

>>> print('yup')  # 1
yup

We include some (random) encoded (utf-8) text w the text surrounding
the example.  It should be ignored:

ЉЊЈЁЂ

"""

zaimportuj sys
zaimportuj unittest
z test zaimportuj support
jeżeli sys.flags.optimize >= 2:
    podnieś unittest.SkipTest("Cannot test docstrings przy -O2")

klasa C(object):
    """Class C.

    >>> print(C())  # 2
    42


    We include some (random) encoded (utf-8) text w the text surrounding
    the example.  It should be ignored:

        ЉЊЈЁЂ

    """

    def __init__(self):
        """C.__init__.

        >>> print(C()) # 3
        42
        """

    def __str__(self):
        """
        >>> print(C()) # 4
        42
        """
        zwróć "42"

    klasa D(object):
        """A nested D class.

        >>> print("In D!")   # 5
        In D!
        """

        def nested(self):
            """
            >>> print(3) # 6
            3
            """

    def getx(self):
        """
        >>> c = C()    # 7
        >>> c.x = 12   # 8
        >>> print(c.x)  # 9
        -12
        """
        zwróć -self._x

    def setx(self, value):
        """
        >>> c = C()     # 10
        >>> c.x = 12    # 11
        >>> print(c.x)   # 12
        -12
        """
        self._x = value

    x = property(getx, setx, doc="""\
        >>> c = C()    # 13
        >>> c.x = 12   # 14
        >>> print(c.x)  # 15
        -12
        """)

    @staticmethod
    def statm():
        """
        A static method.

        >>> print(C.statm())    # 16
        666
        >>> print(C().statm())  # 17
        666
        """
        zwróć 666

    @classmethod
    def clsm(cls, val):
        """
        A klasa method.

        >>> print(C.clsm(22))    # 18
        22
        >>> print(C().clsm(23))  # 19
        23
        """
        zwróć val

def test_main():
    z test zaimportuj test_doctest2
    EXPECTED = 19
    f, t = support.run_doctest(test_doctest2)
    jeżeli t != EXPECTED:
        podnieś support.TestFailed("expected %d tests to run, nie %d" %
                                      (EXPECTED, t))

# Pollute the namespace przy a bunch of imported functions oraz classes,
# to make sure they don't get tested.
z doctest zaimportuj *

jeżeli __name__ == '__main__':
    test_main()
