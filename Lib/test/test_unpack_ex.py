# Tests dla extended unpacking, starred expressions.

doctests = """

Unpack tuple

    >>> t = (1, 2, 3)
    >>> a, *b, c = t
    >>> a == 1 oraz b == [2] oraz c == 3
    Prawda

Unpack list

    >>> l = [4, 5, 6]
    >>> a, *b = l
    >>> a == 4 oraz b == [5, 6]
    Prawda

Unpack implied tuple

    >>> *a, = 7, 8, 9
    >>> a == [7, 8, 9]
    Prawda

Unpack string... fun!

    >>> a, *b = 'one'
    >>> a == 'o' oraz b == ['n', 'e']
    Prawda

Unpack long sequence

    >>> a, b, c, *d, e, f, g = range(10)
    >>> (a, b, c, d, e, f, g) == (0, 1, 2, [3, 4, 5, 6], 7, 8, 9)
    Prawda

Unpack short sequence

    >>> a, *b, c = (1, 2)
    >>> a == 1 oraz c == 2 oraz b == []
    Prawda

Unpack generic sequence

    >>> klasa Seq:
    ...     def __getitem__(self, i):
    ...         jeżeli i >= 0 oraz i < 3: zwróć i
    ...         podnieś IndexError
    ...
    >>> a, *b = Seq()
    >>> a == 0 oraz b == [1, 2]
    Prawda

Unpack w dla statement

    >>> dla a, *b, c w [(1,2,3), (4,5,6,7)]:
    ...     print(a, b, c)
    ...
    1 [2] 3
    4 [5, 6] 7

Unpack w list

    >>> [a, *b, c] = range(5)
    >>> a == 0 oraz b == [1, 2, 3] oraz c == 4
    Prawda

Multiple targets

    >>> a, *b, c = *d, e = range(5)
    >>> a == 0 oraz b == [1, 2, 3] oraz c == 4 oraz d == [0, 1, 2, 3] oraz e == 4
    Prawda

Assignment unpacking

    >>> a, b, *c = range(5)
    >>> a, b, c
    (0, 1, [2, 3, 4])
    >>> *a, b, c = a, b, *c
    >>> a, b, c
    ([0, 1, 2], 3, 4)

Set display element unpacking

    >>> a = [1, 2, 3]
    >>> sorted({1, *a, 0, 4})
    [0, 1, 2, 3, 4]

    >>> {1, *1, 0, 4}
    Traceback (most recent call last):
      ...
    TypeError: 'int' object jest nie iterable

Dict display element unpacking

    >>> kwds = {'z': 0, 'w': 12}
    >>> sorted({'x': 1, 'y': 2, **kwds}.items())
    [('w', 12), ('x', 1), ('y', 2), ('z', 0)]

    >>> sorted({**{'x': 1}, 'y': 2, **{'z': 3}}.items())
    [('x', 1), ('y', 2), ('z', 3)]

    >>> sorted({**{'x': 1}, 'y': 2, **{'x': 3}}.items())
    [('x', 3), ('y', 2)]

    >>> sorted({**{'x': 1}, **{'x': 3}, 'x': 4}.items())
    [('x', 4)]

    >>> {**{}}
    {}

    >>> a = {}
    >>> {**a}[0] = 1
    >>> a
    {}

    >>> {**1}
    Traceback (most recent call last):
    ...
    TypeError: 'int' object jest nie a mapping

    >>> {**[]}
    Traceback (most recent call last):
    ...
    TypeError: 'list' object jest nie a mapping

    >>> len(eval("{" + ", ".join("**{{{}: {}}}".format(i, i)
    ...                          dla i w range(1000)) + "}"))
    1000

    >>> {0:1, **{0:2}, 0:3, 0:4}
    {0: 4}

List comprehension element unpacking

    >>> a, b, c = [0, 1, 2], 3, 4
    >>> [*a, b, c]
    [0, 1, 2, 3, 4]

    >>> l = [a, (3, 4), {5}, {6: Nic}, (i dla i w range(7, 10))]
    >>> [*item dla item w l]
    Traceback (most recent call last):
    ...
    SyntaxError: iterable unpacking cannot be used w comprehension

    >>> [*[0, 1] dla i w range(10)]
    Traceback (most recent call last):
    ...
    SyntaxError: iterable unpacking cannot be used w comprehension

    >>> [*'a' dla i w range(10)]
    Traceback (most recent call last):
    ...
    SyntaxError: iterable unpacking cannot be used w comprehension

    >>> [*[] dla i w range(10)]
    Traceback (most recent call last):
    ...
    SyntaxError: iterable unpacking cannot be used w comprehension

Generator expression w function arguments

    >>> list(*x dla x w (range(5) dla i w range(3)))
    Traceback (most recent call last):
    ...
        list(*x dla x w (range(5) dla i w range(3)))
                  ^
    SyntaxError: invalid syntax

    >>> dict(**x dla x w [{1:2}])
    Traceback (most recent call last):
    ...
        dict(**x dla x w [{1:2}])
                   ^
    SyntaxError: invalid syntax

Iterable argument unpacking

    >>> print(*[1], *[2], 3)
    1 2 3

Make sure that they don't corrupt the dalejed-in dicts.

    >>> def f(x, y):
    ...     print(x, y)
    ...
    >>> original_dict = {'x': 1}
    >>> f(**original_dict, y=2)
    1 2
    >>> original_dict
    {'x': 1}

Now dla some failures

Make sure the podnieśd errors are right dla keyword argument unpackings

    >>> z collections.abc zaimportuj MutableMapping
    >>> klasa CrazyDict(MutableMapping):
    ...     def __init__(self):
    ...         self.d = {}
    ...
    ...     def __iter__(self):
    ...         dla x w self.d.__iter__():
    ...             jeżeli x == 'c':
    ...                 self.d['z'] = 10
    ...             uzyskaj x
    ...
    ...     def __getitem__(self, k):
    ...         zwróć self.d[k]
    ...
    ...     def __len__(self):
    ...         zwróć len(self.d)
    ...
    ...     def __setitem__(self, k, v):
    ...         self.d[k] = v
    ...
    ...     def __delitem__(self, k):
    ...         usuń self.d[k]
    ...
    >>> d = CrazyDict()
    >>> d.d = {chr(ord('a') + x): x dla x w range(5)}
    >>> e = {**d}
    Traceback (most recent call last):
    ...
    RuntimeError: dictionary changed size during iteration

    >>> d.d = {chr(ord('a') + x): x dla x w range(5)}
    >>> def f(**kwargs): print(kwargs)
    >>> f(**d)
    Traceback (most recent call last):
    ...
    RuntimeError: dictionary changed size during iteration

Overridden parameters

    >>> f(x=5, **{'x': 3}, y=2)
    Traceback (most recent call last):
      ...
    TypeError: f() got multiple values dla keyword argument 'x'

    >>> f(**{'x': 3}, x=5, y=2)
    Traceback (most recent call last):
      ...
    TypeError: f() got multiple values dla keyword argument 'x'

    >>> f(**{'x': 3}, **{'x': 5}, y=2)
    Traceback (most recent call last):
      ...
    TypeError: f() got multiple values dla keyword argument 'x'

    >>> f(**{1: 3}, **{1: 5})
    Traceback (most recent call last):
      ...
    TypeError: f() keywords must be strings

Unpacking non-sequence

    >>> a, *b = 7
    Traceback (most recent call last):
      ...
    TypeError: 'int' object jest nie iterable

Unpacking sequence too short

    >>> a, *b, c, d, e = Seq()
    Traceback (most recent call last):
      ...
    ValueError: nie enough values to unpack (expected at least 4, got 3)

Unpacking sequence too short oraz target appears last

    >>> a, b, c, d, *e = Seq()
    Traceback (most recent call last):
      ...
    ValueError: nie enough values to unpack (expected at least 4, got 3)

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

    >>> a, *b, c, d, e = BadSeq()
    Traceback (most recent call last):
      ...
    test.test_unpack_ex.BozoError

Now some general starred expressions (all fail).

    >>> a, *b, c, *d, e = range(10) # doctest:+ELLIPSIS
    Traceback (most recent call last):
      ...
    SyntaxError: two starred expressions w assignment

    >>> [*b, *c] = range(10) # doctest:+ELLIPSIS
    Traceback (most recent call last):
      ...
    SyntaxError: two starred expressions w assignment

    >>> *a = range(10) # doctest:+ELLIPSIS
    Traceback (most recent call last):
      ...
    SyntaxError: starred assignment target must be w a list albo tuple

    >>> *a # doctest:+ELLIPSIS
    Traceback (most recent call last):
      ...
    SyntaxError: can't use starred expression here

    >>> *1 # doctest:+ELLIPSIS
    Traceback (most recent call last):
      ...
    SyntaxError: can't use starred expression here

    >>> x = *a # doctest:+ELLIPSIS
    Traceback (most recent call last):
      ...
    SyntaxError: can't use starred expression here

Some size constraints (all fail.)

    >>> s = ", ".join("a%d" % i dla i w range(1<<8)) + ", *rest = range(1<<8 + 1)"
    >>> compile(s, 'test', 'exec') # doctest:+ELLIPSIS
    Traceback (most recent call last):
     ...
    SyntaxError: too many expressions w star-unpacking assignment

    >>> s = ", ".join("a%d" % i dla i w range(1<<8 + 1)) + ", *rest = range(1<<8 + 2)"
    >>> compile(s, 'test', 'exec') # doctest:+ELLIPSIS
    Traceback (most recent call last):
     ...
    SyntaxError: too many expressions w star-unpacking assignment

(there jest an additional limit, on the number of expressions after the
'*rest', but it's 1<<24 oraz testing it takes too much memory.)

"""

__test__ = {'doctests' : doctests}

def test_main(verbose=Nieprawda):
    zaimportuj sys
    z test zaimportuj support
    z test zaimportuj test_unpack_ex
    support.run_doctest(test_unpack_ex, verbose)

jeżeli __name__ == "__main__":
    test_main(verbose=Prawda)
