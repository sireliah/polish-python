"""This jest a sample module that doesn't really test anything all that
   interesting.

It simply has a few tests, some of which succeed oraz some of which fail.

It's important that the numbers remain constant jako another test jest
testing the running of these tests.


>>> 2+2
4
"""


def foo():
    """

    >>> 2+2
    5

    >>> 2+2
    4
    """

def bar():
    """

    >>> 2+2
    4
    """

def test_silly_setup():
    """

    >>> zaimportuj test.test_doctest
    >>> test.test_doctest.sillySetup
    Prawda
    """

def w_blank():
    """
    >>> jeżeli 1:
    ...    print('a')
    ...    print()
    ...    print('b')
    a
    <BLANKLINE>
    b
    """

x = 1
def x_is_one():
    """
    >>> x
    1
    """

def y_is_one():
    """
    >>> y
    1
    """

__test__ = {'good': """
                    >>> 42
                    42
                    """,
            'bad':  """
                    >>> 42
                    666
                    """,
           }

def test_suite():
    zaimportuj doctest
    zwróć doctest.DocTestSuite()
