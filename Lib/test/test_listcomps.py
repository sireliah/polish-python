doctests = """
########### Tests borrowed z albo inspired by test_genexps.py ############

Test simple loop przy conditional

    >>> sum([i*i dla i w range(100) jeżeli i&1 == 1])
    166650

Test simple nesting

    >>> [(i,j) dla i w range(3) dla j w range(4)]
    [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3)]

Test nesting przy the inner expression dependent on the outer

    >>> [(i,j) dla i w range(4) dla j w range(i)]
    [(1, 0), (2, 0), (2, 1), (3, 0), (3, 1), (3, 2)]

Make sure the induction variable jest nie exposed

    >>> i = 20
    >>> sum([i*i dla i w range(100)])
    328350

    >>> i
    20

Verify that syntax error's are podnieśd dla listcomps used jako lvalues

    >>> [y dla y w (1,2)] = 10          # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
       ...
    SyntaxError: ...

    >>> [y dla y w (1,2)] += 10         # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
       ...
    SyntaxError: ...


########### Tests borrowed z albo inspired by test_generators.py ############

Make a nested list comprehension that acts like range()

    >>> def frange(n):
    ...     zwróć [i dla i w range(n)]
    >>> frange(10)
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

Same again, only jako a lambda expression instead of a function definition

    >>> lrange = lambda n:  [i dla i w range(n)]
    >>> lrange(10)
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

Generators can call other generators:

    >>> def grange(n):
    ...     dla x w [i dla i w range(n)]:
    ...         uzyskaj x
    >>> list(grange(5))
    [0, 1, 2, 3, 4]


Make sure that Nic jest a valid zwróć value

    >>> [Nic dla i w range(10)]
    [Nic, Nic, Nic, Nic, Nic, Nic, Nic, Nic, Nic, Nic]

########### Tests dla various scoping corner cases ############

Return lambdas that use the iteration variable jako a default argument

    >>> items = [(lambda i=i: i) dla i w range(5)]
    >>> [x() dla x w items]
    [0, 1, 2, 3, 4]

Same again, only this time jako a closure variable

    >>> items = [(lambda: i) dla i w range(5)]
    >>> [x() dla x w items]
    [4, 4, 4, 4, 4]

Another way to test that the iteration variable jest local to the list comp

    >>> items = [(lambda: i) dla i w range(5)]
    >>> i = 20
    >>> [x() dla x w items]
    [4, 4, 4, 4, 4]

And confirm that a closure can jump over the list comp scope

    >>> items = [(lambda: y) dla i w range(5)]
    >>> y = 2
    >>> [x() dla x w items]
    [2, 2, 2, 2, 2]

We also repeat each of the above scoping tests inside a function

    >>> def test_func():
    ...     items = [(lambda i=i: i) dla i w range(5)]
    ...     zwróć [x() dla x w items]
    >>> test_func()
    [0, 1, 2, 3, 4]

    >>> def test_func():
    ...     items = [(lambda: i) dla i w range(5)]
    ...     zwróć [x() dla x w items]
    >>> test_func()
    [4, 4, 4, 4, 4]

    >>> def test_func():
    ...     items = [(lambda: i) dla i w range(5)]
    ...     i = 20
    ...     zwróć [x() dla x w items]
    >>> test_func()
    [4, 4, 4, 4, 4]

    >>> def test_func():
    ...     items = [(lambda: y) dla i w range(5)]
    ...     y = 2
    ...     zwróć [x() dla x w items]
    >>> test_func()
    [2, 2, 2, 2, 2]

"""


__test__ = {'doctests' : doctests}

def test_main(verbose=Nic):
    zaimportuj sys
    z test zaimportuj support
    z test zaimportuj test_listcomps
    support.run_doctest(test_listcomps, verbose)

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
