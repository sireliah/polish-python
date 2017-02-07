doctests = """

Test simple loop przy conditional

    >>> sum(i*i dla i w range(100) jeżeli i&1 == 1)
    166650

Test simple nesting

    >>> list((i,j) dla i w range(3) dla j w range(4) )
    [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3)]

Test nesting przy the inner expression dependent on the outer

    >>> list((i,j) dla i w range(4) dla j w range(i) )
    [(1, 0), (2, 0), (2, 1), (3, 0), (3, 1), (3, 2)]

Make sure the induction variable jest nie exposed

    >>> i = 20
    >>> sum(i*i dla i w range(100))
    328350
    >>> i
    20

Test first class

    >>> g = (i*i dla i w range(4))
    >>> type(g)
    <class 'generator'>
    >>> list(g)
    [0, 1, 4, 9]

Test direct calls to next()

    >>> g = (i*i dla i w range(3))
    >>> next(g)
    0
    >>> next(g)
    1
    >>> next(g)
    4
    >>> next(g)
    Traceback (most recent call last):
      File "<pyshell#21>", line 1, w -toplevel-
        next(g)
    StopIteration

Does it stay stopped?

    >>> next(g)
    Traceback (most recent call last):
      File "<pyshell#21>", line 1, w -toplevel-
        next(g)
    StopIteration
    >>> list(g)
    []

Test running gen when defining function jest out of scope

    >>> def f(n):
    ...     zwróć (i*i dla i w range(n))
    >>> list(f(10))
    [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

    >>> def f(n):
    ...     zwróć ((i,j) dla i w range(3) dla j w range(n))
    >>> list(f(4))
    [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3)]
    >>> def f(n):
    ...     zwróć ((i,j) dla i w range(3) dla j w range(4) jeżeli j w range(n))
    >>> list(f(4))
    [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3)]
    >>> list(f(2))
    [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]

Verify that parenthesis are required w a statement

    >>> def f(n):
    ...     zwróć i*i dla i w range(n)
    Traceback (most recent call last):
       ...
    SyntaxError: invalid syntax

Verify that parenthesis are required when used jako a keyword argument value

    >>> dict(a = i dla i w range(10))
    Traceback (most recent call last):
       ...
    SyntaxError: invalid syntax

Verify that parenthesis are required when used jako a keyword argument value

    >>> dict(a = (i dla i w range(10))) #doctest: +ELLIPSIS
    {'a': <generator object <genexpr> at ...>}

Verify early binding dla the outermost for-expression

    >>> x=10
    >>> g = (i*i dla i w range(x))
    >>> x = 5
    >>> list(g)
    [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

Verify that the outermost for-expression makes an immediate check
dla iterability

    >>> (i dla i w 6)
    Traceback (most recent call last):
      File "<pyshell#4>", line 1, w -toplevel-
        (i dla i w 6)
    TypeError: 'int' object jest nie iterable

Verify late binding dla the outermost if-expression

    >>> include = (2,4,6,8)
    >>> g = (i*i dla i w range(10) jeżeli i w include)
    >>> include = (1,3,5,7,9)
    >>> list(g)
    [1, 9, 25, 49, 81]

Verify late binding dla the innermost for-expression

    >>> g = ((i,j) dla i w range(3) dla j w range(x))
    >>> x = 4
    >>> list(g)
    [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3)]

Verify re-use of tuples (a side benefit of using genexps over listcomps)

    >>> tupleids = list(map(id, ((i,i) dla i w range(10))))
    >>> int(max(tupleids) - min(tupleids))
    0

Verify that syntax error's are podnieśd dla genexps used jako lvalues

    >>> (y dla y w (1,2)) = 10
    Traceback (most recent call last):
       ...
    SyntaxError: can't assign to generator expression

    >>> (y dla y w (1,2)) += 10
    Traceback (most recent call last):
       ...
    SyntaxError: can't assign to generator expression


########### Tests borrowed z albo inspired by test_generators.py ############

Make a generator that acts like range()

    >>> yrange = lambda n:  (i dla i w range(n))
    >>> list(yrange(10))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

Generators always zwróć to the most recent caller:

    >>> def creator():
    ...     r = yrange(5)
    ...     print("creator", next(r))
    ...     zwróć r
    >>> def caller():
    ...     r = creator()
    ...     dla i w r:
    ...             print("caller", i)
    >>> caller()
    creator 0
    caller 1
    caller 2
    caller 3
    caller 4

Generators can call other generators:

    >>> def zrange(n):
    ...     dla i w yrange(n):
    ...         uzyskaj i
    >>> list(zrange(5))
    [0, 1, 2, 3, 4]


Verify that a gen exp cannot be resumed dopóki it jest actively running:

    >>> g = (next(me) dla i w range(10))
    >>> me = g
    >>> next(me)
    Traceback (most recent call last):
      File "<pyshell#30>", line 1, w -toplevel-
        next(me)
      File "<pyshell#28>", line 1, w <generator expression>
        g = (next(me) dla i w range(10))
    ValueError: generator already executing

Verify exception propagation

    >>> g = (10 // i dla i w (5, 0, 2))
    >>> next(g)
    2
    >>> next(g)
    Traceback (most recent call last):
      File "<pyshell#37>", line 1, w -toplevel-
        next(g)
      File "<pyshell#35>", line 1, w <generator expression>
        g = (10 // i dla i w (5, 0, 2))
    ZeroDivisionError: integer division albo modulo by zero
    >>> next(g)
    Traceback (most recent call last):
      File "<pyshell#38>", line 1, w -toplevel-
        next(g)
    StopIteration

Make sure that Nic jest a valid zwróć value

    >>> list(Nic dla i w range(10))
    [Nic, Nic, Nic, Nic, Nic, Nic, Nic, Nic, Nic, Nic]

Check that generator attributes are present

    >>> g = (i*i dla i w range(3))
    >>> expected = set(['gi_frame', 'gi_running'])
    >>> set(attr dla attr w dir(g) jeżeli nie attr.startswith('__')) >= expected
    Prawda

    >>> z test.support zaimportuj HAVE_DOCSTRINGS
    >>> print(g.__next__.__doc__ jeżeli HAVE_DOCSTRINGS inaczej 'Implement next(self).')
    Implement next(self).
    >>> zaimportuj types
    >>> isinstance(g, types.GeneratorType)
    Prawda

Check the __iter__ slot jest defined to zwróć self

    >>> iter(g) jest g
    Prawda

Verify that the running flag jest set properly

    >>> g = (me.gi_running dla i w (0,1))
    >>> me = g
    >>> me.gi_running
    0
    >>> next(me)
    1
    >>> me.gi_running
    0

Verify that genexps are weakly referencable

    >>> zaimportuj weakref
    >>> g = (i*i dla i w range(4))
    >>> wr = weakref.ref(g)
    >>> wr() jest g
    Prawda
    >>> p = weakref.proxy(g)
    >>> list(p)
    [0, 1, 4, 9]


"""

zaimportuj sys

# Trace function can throw off the tuple reuse test.
jeżeli hasattr(sys, 'gettrace') oraz sys.gettrace():
    __test__ = {}
inaczej:
    __test__ = {'doctests' : doctests}

def test_main(verbose=Nic):
    z test zaimportuj support
    z test zaimportuj test_genexps
    support.run_doctest(test_genexps, verbose)

    # verify reference counting
    jeżeli verbose oraz hasattr(sys, "gettotalrefcount"):
        zaimportuj gc
        counts = [Nic] * 5
        dla i w range(len(counts)):
            support.run_doctest(test_genexps, verbose)
            gc.collect()
            counts[i] = sys.gettotalrefcount()
        print(counts)

jeżeli __name__ == "__main__":
    test_main(verbose=Prawda)
