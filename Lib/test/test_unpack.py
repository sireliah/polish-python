doctests = """

Unpack tuple

    >>> t = (1, 2, 3)
    >>> a, b, c = t
    >>> a == 1 oraz b == 2 oraz c == 3
    Prawda

Unpack list

    >>> l = [4, 5, 6]
    >>> a, b, c = l
    >>> a == 4 oraz b == 5 oraz c == 6
    Prawda

Unpack implied tuple

    >>> a, b, c = 7, 8, 9
    >>> a == 7 oraz b == 8 oraz c == 9
    Prawda

Unpack string... fun!

    >>> a, b, c = 'one'
    >>> a == 'o' oraz b == 'n' oraz c == 'e'
    Prawda

Unpack generic sequence

    >>> klasa Seq:
    ...     def __getitem__(self, i):
    ...         jeżeli i >= 0 oraz i < 3: zwróć i
    ...         podnieś IndexError
    ...
    >>> a, b, c = Seq()
    >>> a == 0 oraz b == 1 oraz c == 2
    Prawda

Single element unpacking, przy extra syntax

    >>> st = (99,)
    >>> sl = [100]
    >>> a, = st
    >>> a
    99
    >>> b, = sl
    >>> b
    100

Now dla some failures

Unpacking non-sequence

    >>> a, b, c = 7
    Traceback (most recent call last):
      ...
    TypeError: 'int' object jest nie iterable

Unpacking tuple of wrong size

    >>> a, b = t
    Traceback (most recent call last):
      ...
    ValueError: too many values to unpack (expected 2)

Unpacking tuple of wrong size

    >>> a, b = l
    Traceback (most recent call last):
      ...
    ValueError: too many values to unpack (expected 2)

Unpacking sequence too short

    >>> a, b, c, d = Seq()
    Traceback (most recent call last):
      ...
    ValueError: nie enough values to unpack (expected 4, got 3)

Unpacking sequence too long

    >>> a, b = Seq()
    Traceback (most recent call last):
      ...
    ValueError: too many values to unpack (expected 2)

Unpacking a sequence where the test dla too long podnieśs a different kind of
error

    >>> klasa BozoError(Exception):
    ...     dalej
    ...
    >>> klasa BadSeq:
    ...     def __getitem__(self, i):
    ...         jeżeli i >= 0 oraz i < 3:
    ...             zwróć i
    ...         albo_inaczej i == 3:
    ...             podnieś BozoError
    ...         inaczej:
    ...             podnieś IndexError
    ...

Trigger code dopóki nie expecting an IndexError (unpack sequence too long, wrong
error)

    >>> a, b, c, d, e = BadSeq()
    Traceback (most recent call last):
      ...
    test.test_unpack.BozoError

Trigger code dopóki expecting an IndexError (unpack sequence too short, wrong
error)

    >>> a, b, c = BadSeq()
    Traceback (most recent call last):
      ...
    test.test_unpack.BozoError

"""

__test__ = {'doctests' : doctests}

def test_main(verbose=Nieprawda):
    z test zaimportuj support
    z test zaimportuj test_unpack
    support.run_doctest(test_unpack, verbose)

jeżeli __name__ == "__main__":
    test_main(verbose=Prawda)
