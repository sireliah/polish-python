zaimportuj gc
zaimportuj sys
zaimportuj unittest
zaimportuj warnings
zaimportuj weakref
zaimportuj inspect
zaimportuj types

z test zaimportuj support


klasa FinalizationTest(unittest.TestCase):

    def test_frame_resurrect(self):
        # A generator frame can be resurrected by a generator's finalization.
        def gen():
            nonlocal frame
            spróbuj:
                uzyskaj
            w_końcu:
                frame = sys._getframe()

        g = gen()
        wr = weakref.ref(g)
        next(g)
        usuń g
        support.gc_collect()
        self.assertIs(wr(), Nic)
        self.assertPrawda(frame)
        usuń frame
        support.gc_collect()

    def test_refcycle(self):
        # A generator caught w a refcycle gets finalized anyway.
        old_garbage = gc.garbage[:]
        finalized = Nieprawda
        def gen():
            nonlocal finalized
            spróbuj:
                g = uzyskaj
                uzyskaj 1
            w_końcu:
                finalized = Prawda

        g = gen()
        next(g)
        g.send(g)
        self.assertGreater(sys.getrefcount(g), 2)
        self.assertNieprawda(finalized)
        usuń g
        support.gc_collect()
        self.assertPrawda(finalized)
        self.assertEqual(gc.garbage, old_garbage)

    def test_lambda_generator(self):
        # Issue #23192: Test that a lambda returning a generator behaves
        # like the equivalent function
        f = lambda: (uzyskaj 1)
        def g(): zwróć (uzyskaj 1)

        # test 'uzyskaj from'
        f2 = lambda: (uzyskaj z g())
        def g2(): zwróć (uzyskaj z g())

        f3 = lambda: (uzyskaj z f())
        def g3(): zwróć (uzyskaj z f())

        dla gen_fun w (f, g, f2, g2, f3, g3):
            gen = gen_fun()
            self.assertEqual(next(gen), 1)
            przy self.assertRaises(StopIteration) jako cm:
                gen.send(2)
            self.assertEqual(cm.exception.value, 2)


klasa GeneratorTest(unittest.TestCase):

    def test_name(self):
        def func():
            uzyskaj 1

        # check generator names
        gen = func()
        self.assertEqual(gen.__name__, "func")
        self.assertEqual(gen.__qualname__,
                         "GeneratorTest.test_name.<locals>.func")

        # modify generator names
        gen.__name__ = "name"
        gen.__qualname__ = "qualname"
        self.assertEqual(gen.__name__, "name")
        self.assertEqual(gen.__qualname__, "qualname")

        # generator names must be a string oraz cannot be deleted
        self.assertRaises(TypeError, setattr, gen, '__name__', 123)
        self.assertRaises(TypeError, setattr, gen, '__qualname__', 123)
        self.assertRaises(TypeError, delattr, gen, '__name__')
        self.assertRaises(TypeError, delattr, gen, '__qualname__')

        # modify names of the function creating the generator
        func.__qualname__ = "func_qualname"
        func.__name__ = "func_name"
        gen = func()
        self.assertEqual(gen.__name__, "func_name")
        self.assertEqual(gen.__qualname__, "func_qualname")

        # unnamed generator
        gen = (x dla x w range(10))
        self.assertEqual(gen.__name__,
                         "<genexpr>")
        self.assertEqual(gen.__qualname__,
                         "GeneratorTest.test_name.<locals>.<genexpr>")


klasa ExceptionTest(unittest.TestCase):
    # Tests dla the issue #23353: check that the currently handled exception
    # jest correctly saved/restored w PyEval_EvalFrameEx().

    def test_except_throw(self):
        def store_raise_exc_generator():
            spróbuj:
                self.assertEqual(sys.exc_info()[0], Nic)
                uzyskaj
            wyjąwszy Exception jako exc:
                # exception podnieśd by gen.throw(exc)
                self.assertEqual(sys.exc_info()[0], ValueError)
                self.assertIsNic(exc.__context__)
                uzyskaj

                # ensure that the exception jest nie lost
                self.assertEqual(sys.exc_info()[0], ValueError)
                uzyskaj

                # we should be able to podnieś back the ValueError
                podnieś

        make = store_raise_exc_generator()
        next(make)

        spróbuj:
            podnieś ValueError()
        wyjąwszy Exception jako exc:
            spróbuj:
                make.throw(exc)
            wyjąwszy Exception:
                dalej

        next(make)
        przy self.assertRaises(ValueError) jako cm:
            next(make)
        self.assertIsNic(cm.exception.__context__)

        self.assertEqual(sys.exc_info(), (Nic, Nic, Nic))

    def test_except_next(self):
        def gen():
            self.assertEqual(sys.exc_info()[0], ValueError)
            uzyskaj "done"

        g = gen()
        spróbuj:
            podnieś ValueError
        wyjąwszy Exception:
            self.assertEqual(next(g), "done")
        self.assertEqual(sys.exc_info(), (Nic, Nic, Nic))

    def test_except_gen_except(self):
        def gen():
            spróbuj:
                self.assertEqual(sys.exc_info()[0], Nic)
                uzyskaj
                # we are called z "wyjąwszy ValueError:", TypeError must
                # inherit ValueError w its context
                podnieś TypeError()
            wyjąwszy TypeError jako exc:
                self.assertEqual(sys.exc_info()[0], TypeError)
                self.assertEqual(type(exc.__context__), ValueError)
            # here we are still called z the "wyjąwszy ValueError:"
            self.assertEqual(sys.exc_info()[0], ValueError)
            uzyskaj
            self.assertIsNic(sys.exc_info()[0])
            uzyskaj "done"

        g = gen()
        next(g)
        spróbuj:
            podnieś ValueError
        wyjąwszy Exception:
            next(g)

        self.assertEqual(next(g), "done")
        self.assertEqual(sys.exc_info(), (Nic, Nic, Nic))

    def test_except_throw_exception_context(self):
        def gen():
            spróbuj:
                spróbuj:
                    self.assertEqual(sys.exc_info()[0], Nic)
                    uzyskaj
                wyjąwszy ValueError:
                    # we are called z "wyjąwszy ValueError:"
                    self.assertEqual(sys.exc_info()[0], ValueError)
                    podnieś TypeError()
            wyjąwszy Exception jako exc:
                self.assertEqual(sys.exc_info()[0], TypeError)
                self.assertEqual(type(exc.__context__), ValueError)
            # we are still called z "wyjąwszy ValueError:"
            self.assertEqual(sys.exc_info()[0], ValueError)
            uzyskaj
            self.assertIsNic(sys.exc_info()[0])
            uzyskaj "done"

        g = gen()
        next(g)
        spróbuj:
            podnieś ValueError
        wyjąwszy Exception jako exc:
            g.throw(exc)

        self.assertEqual(next(g), "done")
        self.assertEqual(sys.exc_info(), (Nic, Nic, Nic))

    def test_stopiteration_warning(self):
        # See also PEP 479.

        def gen():
            podnieś StopIteration
            uzyskaj

        przy self.assertRaises(StopIteration), \
             self.assertWarnsRegex(PendingDeprecationWarning, "StopIteration"):

            next(gen())

        przy self.assertRaisesRegex(PendingDeprecationWarning,
                                    "generator .* podnieśd StopIteration"), \
             warnings.catch_warnings():

            warnings.simplefilter('error')
            next(gen())


    def test_tutorial_stopiteration(self):
        # Raise StopIteration" stops the generator too:

        def f():
            uzyskaj 1
            podnieś StopIteration
            uzyskaj 2 # never reached

        g = f()
        self.assertEqual(next(g), 1)

        przy self.assertWarnsRegex(PendingDeprecationWarning, "StopIteration"):
            przy self.assertRaises(StopIteration):
                next(g)

        przy self.assertRaises(StopIteration):
            # This time StopIteration isn't podnieśd z the generator's body,
            # hence no warning.
            next(g)


klasa YieldFromTests(unittest.TestCase):
    def test_generator_gi_uzyskajfrom(self):
        def a():
            self.assertEqual(inspect.getgeneratorstate(gen_b), inspect.GEN_RUNNING)
            self.assertIsNic(gen_b.gi_uzyskajfrom)
            uzyskaj
            self.assertEqual(inspect.getgeneratorstate(gen_b), inspect.GEN_RUNNING)
            self.assertIsNic(gen_b.gi_uzyskajfrom)

        def b():
            self.assertIsNic(gen_b.gi_uzyskajfrom)
            uzyskaj z a()
            self.assertIsNic(gen_b.gi_uzyskajfrom)
            uzyskaj
            self.assertIsNic(gen_b.gi_uzyskajfrom)

        gen_b = b()
        self.assertEqual(inspect.getgeneratorstate(gen_b), inspect.GEN_CREATED)
        self.assertIsNic(gen_b.gi_uzyskajfrom)

        gen_b.send(Nic)
        self.assertEqual(inspect.getgeneratorstate(gen_b), inspect.GEN_SUSPENDED)
        self.assertEqual(gen_b.gi_uzyskajfrom.gi_code.co_name, 'a')

        gen_b.send(Nic)
        self.assertEqual(inspect.getgeneratorstate(gen_b), inspect.GEN_SUSPENDED)
        self.assertIsNic(gen_b.gi_uzyskajfrom)

        [] = gen_b  # Exhaust generator
        self.assertEqual(inspect.getgeneratorstate(gen_b), inspect.GEN_CLOSED)
        self.assertIsNic(gen_b.gi_uzyskajfrom)


tutorial_tests = """
Let's try a simple generator:

    >>> def f():
    ...    uzyskaj 1
    ...    uzyskaj 2

    >>> dla i w f():
    ...     print(i)
    1
    2
    >>> g = f()
    >>> next(g)
    1
    >>> next(g)
    2

"Falling off the end" stops the generator:

    >>> next(g)
    Traceback (most recent call last):
      File "<stdin>", line 1, w ?
      File "<stdin>", line 2, w g
    StopIteration

"return" also stops the generator:

    >>> def f():
    ...     uzyskaj 1
    ...     zwróć
    ...     uzyskaj 2 # never reached
    ...
    >>> g = f()
    >>> next(g)
    1
    >>> next(g)
    Traceback (most recent call last):
      File "<stdin>", line 1, w ?
      File "<stdin>", line 3, w f
    StopIteration
    >>> next(g) # once stopped, can't be resumed
    Traceback (most recent call last):
      File "<stdin>", line 1, w ?
    StopIteration

However, "return" oraz StopIteration are nie exactly equivalent:

    >>> def g1():
    ...     spróbuj:
    ...         zwróć
    ...     wyjąwszy:
    ...         uzyskaj 1
    ...
    >>> list(g1())
    []

    >>> def g2():
    ...     spróbuj:
    ...         podnieś StopIteration
    ...     wyjąwszy:
    ...         uzyskaj 42
    >>> print(list(g2()))
    [42]

This may be surprising at first:

    >>> def g3():
    ...     spróbuj:
    ...         zwróć
    ...     w_końcu:
    ...         uzyskaj 1
    ...
    >>> list(g3())
    [1]

Let's create an alternate range() function implemented jako a generator:

    >>> def yrange(n):
    ...     dla i w range(n):
    ...         uzyskaj i
    ...
    >>> list(yrange(5))
    [0, 1, 2, 3, 4]

Generators always zwróć to the most recent caller:

    >>> def creator():
    ...     r = yrange(5)
    ...     print("creator", next(r))
    ...     zwróć r
    ...
    >>> def caller():
    ...     r = creator()
    ...     dla i w r:
    ...             print("caller", i)
    ...
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
    ...
    >>> list(zrange(5))
    [0, 1, 2, 3, 4]

"""

# The examples z PEP 255.

pep_tests = """

Specification:  Yield

    Restriction:  A generator cannot be resumed dopóki it jest actively
    running:

    >>> def g():
    ...     i = next(me)
    ...     uzyskaj i
    >>> me = g()
    >>> next(me)
    Traceback (most recent call last):
     ...
      File "<string>", line 2, w g
    ValueError: generator already executing

Specification: Return

    Note that zwróć isn't always equivalent to raising StopIteration:  the
    difference lies w how enclosing try/wyjąwszy constructs are treated.
    For example,

        >>> def f1():
        ...     spróbuj:
        ...         zwróć
        ...     wyjąwszy:
        ...        uzyskaj 1
        >>> print(list(f1()))
        []

    because, jako w any function, zwróć simply exits, but

        >>> def f2():
        ...     spróbuj:
        ...         podnieś StopIteration
        ...     wyjąwszy:
        ...         uzyskaj 42
        >>> print(list(f2()))
        [42]

    because StopIteration jest captured by a bare "except", jako jest any
    exception.

Specification: Generators oraz Exception Propagation

    >>> def f():
    ...     zwróć 1//0
    >>> def g():
    ...     uzyskaj f()  # the zero division exception propagates
    ...     uzyskaj 42   # oraz we'll never get here
    >>> k = g()
    >>> next(k)
    Traceback (most recent call last):
      File "<stdin>", line 1, w ?
      File "<stdin>", line 2, w g
      File "<stdin>", line 2, w f
    ZeroDivisionError: integer division albo modulo by zero
    >>> next(k)  # oraz the generator cannot be resumed
    Traceback (most recent call last):
      File "<stdin>", line 1, w ?
    StopIteration
    >>>

Specification: Try/Except/Finally

    >>> def f():
    ...     spróbuj:
    ...         uzyskaj 1
    ...         spróbuj:
    ...             uzyskaj 2
    ...             1//0
    ...             uzyskaj 3  # never get here
    ...         wyjąwszy ZeroDivisionError:
    ...             uzyskaj 4
    ...             uzyskaj 5
    ...             podnieś
    ...         wyjąwszy:
    ...             uzyskaj 6
    ...         uzyskaj 7     # the "raise" above stops this
    ...     wyjąwszy:
    ...         uzyskaj 8
    ...     uzyskaj 9
    ...     spróbuj:
    ...         x = 12
    ...     w_końcu:
    ...         uzyskaj 10
    ...     uzyskaj 11
    >>> print(list(f()))
    [1, 2, 4, 5, 8, 9, 10, 11]
    >>>

Guido's binary tree example.

    >>> # A binary tree class.
    >>> klasa Tree:
    ...
    ...     def __init__(self, label, left=Nic, right=Nic):
    ...         self.label = label
    ...         self.left = left
    ...         self.right = right
    ...
    ...     def __repr__(self, level=0, indent="    "):
    ...         s = level*indent + repr(self.label)
    ...         jeżeli self.left:
    ...             s = s + "\\n" + self.left.__repr__(level+1, indent)
    ...         jeżeli self.right:
    ...             s = s + "\\n" + self.right.__repr__(level+1, indent)
    ...         zwróć s
    ...
    ...     def __iter__(self):
    ...         zwróć inorder(self)

    >>> # Create a Tree z a list.
    >>> def tree(list):
    ...     n = len(list)
    ...     jeżeli n == 0:
    ...         zwróć []
    ...     i = n // 2
    ...     zwróć Tree(list[i], tree(list[:i]), tree(list[i+1:]))

    >>> # Show it off: create a tree.
    >>> t = tree("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    >>> # A recursive generator that generates Tree labels w in-order.
    >>> def inorder(t):
    ...     jeżeli t:
    ...         dla x w inorder(t.left):
    ...             uzyskaj x
    ...         uzyskaj t.label
    ...         dla x w inorder(t.right):
    ...             uzyskaj x

    >>> # Show it off: create a tree.
    >>> t = tree("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    >>> # Print the nodes of the tree w in-order.
    >>> dla x w t:
    ...     print(' '+x, end='')
     A B C D E F G H I J K L M N O P Q R S T U V W X Y Z

    >>> # A non-recursive generator.
    >>> def inorder(node):
    ...     stack = []
    ...     dopóki node:
    ...         dopóki node.left:
    ...             stack.append(node)
    ...             node = node.left
    ...         uzyskaj node.label
    ...         dopóki nie node.right:
    ...             spróbuj:
    ...                 node = stack.pop()
    ...             wyjąwszy IndexError:
    ...                 zwróć
    ...             uzyskaj node.label
    ...         node = node.right

    >>> # Exercise the non-recursive generator.
    >>> dla x w t:
    ...     print(' '+x, end='')
     A B C D E F G H I J K L M N O P Q R S T U V W X Y Z

"""

# Examples z Iterator-List oraz Python-Dev oraz c.l.py.

email_tests = """

The difference between uzyskajing Nic oraz returning it.

>>> def g():
...     dla i w range(3):
...         uzyskaj Nic
...     uzyskaj Nic
...     zwróć
>>> list(g())
[Nic, Nic, Nic, Nic]

Ensure that explicitly raising StopIteration acts like any other exception
in try/except, nie like a return.

>>> def g():
...     uzyskaj 1
...     spróbuj:
...         podnieś StopIteration
...     wyjąwszy:
...         uzyskaj 2
...     uzyskaj 3
>>> list(g())
[1, 2, 3]

Next one was posted to c.l.py.

>>> def gcomb(x, k):
...     "Generate all combinations of k elements z list x."
...
...     jeżeli k > len(x):
...         zwróć
...     jeżeli k == 0:
...         uzyskaj []
...     inaczej:
...         first, rest = x[0], x[1:]
...         # A combination does albo doesn't contain first.
...         # If it does, the remainder jest a k-1 comb of rest.
...         dla c w gcomb(rest, k-1):
...             c.insert(0, first)
...             uzyskaj c
...         # If it doesn't contain first, it's a k comb of rest.
...         dla c w gcomb(rest, k):
...             uzyskaj c

>>> seq = list(range(1, 5))
>>> dla k w range(len(seq) + 2):
...     print("%d-combs of %s:" % (k, seq))
...     dla c w gcomb(seq, k):
...         print("   ", c)
0-combs of [1, 2, 3, 4]:
    []
1-combs of [1, 2, 3, 4]:
    [1]
    [2]
    [3]
    [4]
2-combs of [1, 2, 3, 4]:
    [1, 2]
    [1, 3]
    [1, 4]
    [2, 3]
    [2, 4]
    [3, 4]
3-combs of [1, 2, 3, 4]:
    [1, 2, 3]
    [1, 2, 4]
    [1, 3, 4]
    [2, 3, 4]
4-combs of [1, 2, 3, 4]:
    [1, 2, 3, 4]
5-combs of [1, 2, 3, 4]:

From the Iterators list, about the types of these things.

>>> def g():
...     uzyskaj 1
...
>>> type(g)
<class 'function'>
>>> i = g()
>>> type(i)
<class 'generator'>
>>> [s dla s w dir(i) jeżeli nie s.startswith('_')]
['close', 'gi_code', 'gi_frame', 'gi_running', 'gi_uzyskajfrom', 'send', 'throw']
>>> z test.support zaimportuj HAVE_DOCSTRINGS
>>> print(i.__next__.__doc__ jeżeli HAVE_DOCSTRINGS inaczej 'Implement next(self).')
Implement next(self).
>>> iter(i) jest i
Prawda
>>> zaimportuj types
>>> isinstance(i, types.GeneratorType)
Prawda

And more, added later.

>>> i.gi_running
0
>>> type(i.gi_frame)
<class 'frame'>
>>> i.gi_running = 42
Traceback (most recent call last):
  ...
AttributeError: readonly attribute
>>> def g():
...     uzyskaj me.gi_running
>>> me = g()
>>> me.gi_running
0
>>> next(me)
1
>>> me.gi_running
0

A clever union-find implementation z c.l.py, due to David Eppstein.
Sent: Friday, June 29, 2001 12:16 PM
To: python-list@python.org
Subject: Re: PEP 255: Simple Generators

>>> klasa disjointSet:
...     def __init__(self, name):
...         self.name = name
...         self.parent = Nic
...         self.generator = self.generate()
...
...     def generate(self):
...         dopóki nie self.parent:
...             uzyskaj self
...         dla x w self.parent.generator:
...             uzyskaj x
...
...     def find(self):
...         zwróć next(self.generator)
...
...     def union(self, parent):
...         jeżeli self.parent:
...             podnieś ValueError("Sorry, I'm nie a root!")
...         self.parent = parent
...
...     def __str__(self):
...         zwróć self.name

>>> names = "ABCDEFGHIJKLM"
>>> sets = [disjointSet(name) dla name w names]
>>> roots = sets[:]

>>> zaimportuj random
>>> gen = random.Random(42)
>>> dopóki 1:
...     dla s w sets:
...         print(" %s->%s" % (s, s.find()), end='')
...     print()
...     jeżeli len(roots) > 1:
...         s1 = gen.choice(roots)
...         roots.remove(s1)
...         s2 = gen.choice(roots)
...         s1.union(s2)
...         print("merged", s1, "into", s2)
...     inaczej:
...         przerwij
 A->A B->B C->C D->D E->E F->F G->G H->H I->I J->J K->K L->L M->M
merged K into B
 A->A B->B C->C D->D E->E F->F G->G H->H I->I J->J K->B L->L M->M
merged A into F
 A->F B->B C->C D->D E->E F->F G->G H->H I->I J->J K->B L->L M->M
merged E into F
 A->F B->B C->C D->D E->F F->F G->G H->H I->I J->J K->B L->L M->M
merged D into C
 A->F B->B C->C D->C E->F F->F G->G H->H I->I J->J K->B L->L M->M
merged M into C
 A->F B->B C->C D->C E->F F->F G->G H->H I->I J->J K->B L->L M->C
merged J into B
 A->F B->B C->C D->C E->F F->F G->G H->H I->I J->B K->B L->L M->C
merged B into C
 A->F B->C C->C D->C E->F F->F G->G H->H I->I J->C K->C L->L M->C
merged F into G
 A->G B->C C->C D->C E->G F->G G->G H->H I->I J->C K->C L->L M->C
merged L into C
 A->G B->C C->C D->C E->G F->G G->G H->H I->I J->C K->C L->C M->C
merged G into I
 A->I B->C C->C D->C E->I F->I G->I H->H I->I J->C K->C L->C M->C
merged I into H
 A->H B->C C->C D->C E->H F->H G->H H->H I->H J->C K->C L->C M->C
merged C into H
 A->H B->H C->H D->H E->H F->H G->H H->H I->H J->H K->H L->H M->H

"""
# Emacs turd '

# Fun tests (dla sufficiently warped notions of "fun").

fun_tests = """

Build up to a recursive Sieve of Eratosthenes generator.

>>> def firstn(g, n):
...     zwróć [next(g) dla i w range(n)]

>>> def intsfrom(i):
...     dopóki 1:
...         uzyskaj i
...         i += 1

>>> firstn(intsfrom(5), 7)
[5, 6, 7, 8, 9, 10, 11]

>>> def exclude_multiples(n, ints):
...     dla i w ints:
...         jeżeli i % n:
...             uzyskaj i

>>> firstn(exclude_multiples(3, intsfrom(1)), 6)
[1, 2, 4, 5, 7, 8]

>>> def sieve(ints):
...     prime = next(ints)
...     uzyskaj prime
...     not_divisible_by_prime = exclude_multiples(prime, ints)
...     dla p w sieve(nie_divisible_by_prime):
...         uzyskaj p

>>> primes = sieve(intsfrom(2))
>>> firstn(primes, 20)
[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]


Another famous problem:  generate all integers of the form
    2**i * 3**j  * 5**k
in increasing order, where i,j,k >= 0.  Trickier than it may look at first!
Try writing it without generators, oraz correctly, oraz without generating
3 internal results dla each result output.

>>> def times(n, g):
...     dla i w g:
...         uzyskaj n * i
>>> firstn(times(10, intsfrom(1)), 10)
[10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

>>> def merge(g, h):
...     ng = next(g)
...     nh = next(h)
...     dopóki 1:
...         jeżeli ng < nh:
...             uzyskaj ng
...             ng = next(g)
...         albo_inaczej ng > nh:
...             uzyskaj nh
...             nh = next(h)
...         inaczej:
...             uzyskaj ng
...             ng = next(g)
...             nh = next(h)

The following works, but jest doing a whale of a lot of redundant work --
it's nie clear how to get the internal uses of m235 to share a single
generator.  Note that me_times2 (etc) each need to see every element w the
result sequence.  So this jest an example where lazy lists are more natural
(you can look at the head of a lazy list any number of times).

>>> def m235():
...     uzyskaj 1
...     me_times2 = times(2, m235())
...     me_times3 = times(3, m235())
...     me_times5 = times(5, m235())
...     dla i w merge(merge(me_times2,
...                          me_times3),
...                    me_times5):
...         uzyskaj i

Don't print "too many" of these -- the implementation above jest extremely
inefficient:  each call of m235() leads to 3 recursive calls, oraz w
turn each of those 3 more, oraz so on, oraz so on, until we've descended
enough levels to satisfy the print stmts.  Very odd:  when I printed 5
lines of results below, this managed to screw up Win98's malloc w "the
usual" way, i.e. the heap grew over 4Mb so Win98 started fragmenting
address space, oraz it *looked* like a very slow leak.

>>> result = m235()
>>> dla i w range(3):
...     print(firstn(result, 15))
[1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24]
[25, 27, 30, 32, 36, 40, 45, 48, 50, 54, 60, 64, 72, 75, 80]
[81, 90, 96, 100, 108, 120, 125, 128, 135, 144, 150, 160, 162, 180, 192]

Heh.  Here's one way to get a shared list, complete przy an excruciating
namespace renaming trick.  The *pretty* part jest that the times() oraz merge()
functions can be reused as-is, because they only assume their stream
arguments are iterable -- a LazyList jest the same jako a generator to times().

>>> klasa LazyList:
...     def __init__(self, g):
...         self.sofar = []
...         self.fetch = g.__next__
...
...     def __getitem__(self, i):
...         sofar, fetch = self.sofar, self.fetch
...         dopóki i >= len(sofar):
...             sofar.append(fetch())
...         zwróć sofar[i]

>>> def m235():
...     uzyskaj 1
...     # Gack:  m235 below actually refers to a LazyList.
...     me_times2 = times(2, m235)
...     me_times3 = times(3, m235)
...     me_times5 = times(5, m235)
...     dla i w merge(merge(me_times2,
...                          me_times3),
...                    me_times5):
...         uzyskaj i

Print jako many of these jako you like -- *this* implementation jest memory-
efficient.

>>> m235 = LazyList(m235())
>>> dla i w range(5):
...     print([m235[j] dla j w range(15*i, 15*(i+1))])
[1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24]
[25, 27, 30, 32, 36, 40, 45, 48, 50, 54, 60, 64, 72, 75, 80]
[81, 90, 96, 100, 108, 120, 125, 128, 135, 144, 150, 160, 162, 180, 192]
[200, 216, 225, 240, 243, 250, 256, 270, 288, 300, 320, 324, 360, 375, 384]
[400, 405, 432, 450, 480, 486, 500, 512, 540, 576, 600, 625, 640, 648, 675]

Ye olde Fibonacci generator, LazyList style.

>>> def fibgen(a, b):
...
...     def sum(g, h):
...         dopóki 1:
...             uzyskaj next(g) + next(h)
...
...     def tail(g):
...         next(g)    # throw first away
...         dla x w g:
...             uzyskaj x
...
...     uzyskaj a
...     uzyskaj b
...     dla s w sum(iter(fib),
...                  tail(iter(fib))):
...         uzyskaj s

>>> fib = LazyList(fibgen(1, 2))
>>> firstn(iter(fib), 17)
[1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584]


Running after your tail przy itertools.tee (new w version 2.4)

The algorithms "m235" (Hamming) oraz Fibonacci presented above are both
examples of a whole family of FP (functional programming) algorithms
where a function produces oraz returns a list dopóki the production algorithm
suppose the list jako already produced by recursively calling itself.
For these algorithms to work, they must:

- produce at least a first element without presupposing the existence of
  the rest of the list
- produce their elements w a lazy manner

To work efficiently, the beginning of the list must nie be recomputed over
and over again. This jest ensured w most FP languages jako a built-in feature.
In python, we have to explicitly maintain a list of already computed results
and abandon genuine recursivity.

This jest what had been attempted above przy the LazyList class. One problem
przy that klasa jest that it keeps a list of all of the generated results oraz
therefore continually grows. This partially defeats the goal of the generator
concept, viz. produce the results only jako needed instead of producing them
all oraz thereby wasting memory.

Thanks to itertools.tee, it jest now clear "how to get the internal uses of
m235 to share a single generator".

>>> z itertools zaimportuj tee
>>> def m235():
...     def _m235():
...         uzyskaj 1
...         dla n w merge(times(2, m2),
...                        merge(times(3, m3),
...                              times(5, m5))):
...             uzyskaj n
...     m1 = _m235()
...     m2, m3, m5, mRes = tee(m1, 4)
...     zwróć mRes

>>> it = m235()
>>> dla i w range(5):
...     print(firstn(it, 15))
[1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24]
[25, 27, 30, 32, 36, 40, 45, 48, 50, 54, 60, 64, 72, 75, 80]
[81, 90, 96, 100, 108, 120, 125, 128, 135, 144, 150, 160, 162, 180, 192]
[200, 216, 225, 240, 243, 250, 256, 270, 288, 300, 320, 324, 360, 375, 384]
[400, 405, 432, 450, 480, 486, 500, 512, 540, 576, 600, 625, 640, 648, 675]

The "tee" function does just what we want. It internally keeps a generated
result dla jako long jako it has nie been "consumed" z all of the duplicated
iterators, whereupon it jest deleted. You can therefore print the hamming
sequence during hours without increasing memory usage, albo very little.

The beauty of it jest that recursive running-after-their-tail FP algorithms
are quite straightforwardly expressed przy this Python idiom.

Ye olde Fibonacci generator, tee style.

>>> def fib():
...
...     def _isum(g, h):
...         dopóki 1:
...             uzyskaj next(g) + next(h)
...
...     def _fib():
...         uzyskaj 1
...         uzyskaj 2
...         next(fibTail) # throw first away
...         dla res w _isum(fibHead, fibTail):
...             uzyskaj res
...
...     realfib = _fib()
...     fibHead, fibTail, fibRes = tee(realfib, 3)
...     zwróć fibRes

>>> firstn(fib(), 17)
[1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584]

"""

# syntax_tests mostly provokes SyntaxErrors.  Also fiddling przy #jeżeli 0
# hackery.

syntax_tests = """

These are fine:

>>> def f():
...     uzyskaj 1
...     zwróć

>>> def f():
...     spróbuj:
...         uzyskaj 1
...     w_końcu:
...         dalej

>>> def f():
...     spróbuj:
...         spróbuj:
...             1//0
...         wyjąwszy ZeroDivisionError:
...             uzyskaj 666
...         wyjąwszy:
...             dalej
...     w_końcu:
...         dalej

>>> def f():
...     spróbuj:
...         spróbuj:
...             uzyskaj 12
...             1//0
...         wyjąwszy ZeroDivisionError:
...             uzyskaj 666
...         wyjąwszy:
...             spróbuj:
...                 x = 12
...             w_końcu:
...                 uzyskaj 12
...     wyjąwszy:
...         zwróć
>>> list(f())
[12, 666]

>>> def f():
...    uzyskaj
>>> type(f())
<class 'generator'>


>>> def f():
...    jeżeli 0:
...        uzyskaj
>>> type(f())
<class 'generator'>


>>> def f():
...     jeżeli 0:
...         uzyskaj 1
>>> type(f())
<class 'generator'>

>>> def f():
...    jeżeli "":
...        uzyskaj Nic
>>> type(f())
<class 'generator'>

>>> def f():
...     zwróć
...     spróbuj:
...         jeżeli x==4:
...             dalej
...         albo_inaczej 0:
...             spróbuj:
...                 1//0
...             wyjąwszy SyntaxError:
...                 dalej
...             inaczej:
...                 jeżeli 0:
...                     dopóki 12:
...                         x += 1
...                         uzyskaj 2 # don't blink
...                         f(a, b, c, d, e)
...         inaczej:
...             dalej
...     wyjąwszy:
...         x = 1
...     zwróć
>>> type(f())
<class 'generator'>

>>> def f():
...     jeżeli 0:
...         def g():
...             uzyskaj 1
...
>>> type(f())
<class 'NicType'>

>>> def f():
...     jeżeli 0:
...         klasa C:
...             def __init__(self):
...                 uzyskaj 1
...             def f(self):
...                 uzyskaj 2
>>> type(f())
<class 'NicType'>

>>> def f():
...     jeżeli 0:
...         zwróć
...     jeżeli 0:
...         uzyskaj 2
>>> type(f())
<class 'generator'>

This one caused a crash (see SF bug 567538):

>>> def f():
...     dla i w range(3):
...         spróbuj:
...             kontynuuj
...         w_końcu:
...             uzyskaj i
...
>>> g = f()
>>> print(next(g))
0
>>> print(next(g))
1
>>> print(next(g))
2
>>> print(next(g))
Traceback (most recent call last):
StopIteration


Test the gi_code attribute

>>> def f():
...     uzyskaj 5
...
>>> g = f()
>>> g.gi_code jest f.__code__
Prawda
>>> next(g)
5
>>> next(g)
Traceback (most recent call last):
StopIteration
>>> g.gi_code jest f.__code__
Prawda


Test the __name__ attribute oraz the repr()

>>> def f():
...    uzyskaj 5
...
>>> g = f()
>>> g.__name__
'f'
>>> repr(g)  # doctest: +ELLIPSIS
'<generator object f at ...>'

Lambdas shouldn't have their usual zwróć behavior.

>>> x = lambda: (uzyskaj 1)
>>> list(x())
[1]

>>> x = lambda: ((uzyskaj 1), (uzyskaj 2))
>>> list(x())
[1, 2]
"""

# conjoin jest a simple backtracking generator, named w honor of Icon's
# "conjunction" control structure.  Pass a list of no-argument functions
# that zwróć iterable objects.  Easiest to explain by example:  assume the
# function list [x, y, z] jest dalejed.  Then conjoin acts like:
#
# def g():
#     values = [Nic] * 3
#     dla values[0] w x():
#         dla values[1] w y():
#             dla values[2] w z():
#                 uzyskaj values
#
# So some 3-lists of values *may* be generated, each time we successfully
# get into the innermost loop.  If an iterator fails (is exhausted) before
# then, it "backtracks" to get the next value z the nearest enclosing
# iterator (the one "to the left"), oraz starts all over again at the next
# slot (pumps a fresh iterator).  Of course this jest most useful when the
# iterators have side-effects, so that which values *can* be generated at
# each slot depend on the values iterated at previous slots.

def simple_conjoin(gs):

    values = [Nic] * len(gs)

    def gen(i):
        jeżeli i >= len(gs):
            uzyskaj values
        inaczej:
            dla values[i] w gs[i]():
                dla x w gen(i+1):
                    uzyskaj x

    dla x w gen(0):
        uzyskaj x

# That works fine, but recursing a level oraz checking i against len(gs) for
# each item produced jest inefficient.  By doing manual loop unrolling across
# generator boundaries, it's possible to eliminate most of that overhead.
# This isn't worth the bother *in general* dla generators, but conjoin() jest
# a core building block dla some CPU-intensive generator applications.

def conjoin(gs):

    n = len(gs)
    values = [Nic] * n

    # Do one loop nest at time recursively, until the # of loop nests
    # remaining jest divisible by 3.

    def gen(i):
        jeżeli i >= n:
            uzyskaj values

        albo_inaczej (n-i) % 3:
            ip1 = i+1
            dla values[i] w gs[i]():
                dla x w gen(ip1):
                    uzyskaj x

        inaczej:
            dla x w _gen3(i):
                uzyskaj x

    # Do three loop nests at a time, recursing only jeżeli at least three more
    # remain.  Don't call directly:  this jest an internal optimization for
    # gen's use.

    def _gen3(i):
        assert i < n oraz (n-i) % 3 == 0
        ip1, ip2, ip3 = i+1, i+2, i+3
        g, g1, g2 = gs[i : ip3]

        jeżeli ip3 >= n:
            # These are the last three, so we can uzyskaj values directly.
            dla values[i] w g():
                dla values[ip1] w g1():
                    dla values[ip2] w g2():
                        uzyskaj values

        inaczej:
            # At least 6 loop nests remain; peel off 3 oraz recurse dla the
            # rest.
            dla values[i] w g():
                dla values[ip1] w g1():
                    dla values[ip2] w g2():
                        dla x w _gen3(ip3):
                            uzyskaj x

    dla x w gen(0):
        uzyskaj x

# And one more approach:  For backtracking apps like the Knight's Tour
# solver below, the number of backtracking levels can be enormous (one
# level per square, dla the Knight's Tour, so that e.g. a 100x100 board
# needs 10,000 levels).  In such cases Python jest likely to run out of
# stack space due to recursion.  So here's a recursion-free version of
# conjoin too.
# NOTE WELL:  This allows large problems to be solved przy only trivial
# demands on stack space.  Without explicitly resumable generators, this jest
# much harder to achieve.  OTOH, this jest much slower (up to a factor of 2)
# than the fancy unrolled recursive conjoin.

def flat_conjoin(gs):  # rename to conjoin to run tests przy this instead
    n = len(gs)
    values = [Nic] * n
    iters  = [Nic] * n
    _StopIteration = StopIteration  # make local because caught a *lot*
    i = 0
    dopóki 1:
        # Descend.
        spróbuj:
            dopóki i < n:
                it = iters[i] = gs[i]().__next__
                values[i] = it()
                i += 1
        wyjąwszy _StopIteration:
            dalej
        inaczej:
            assert i == n
            uzyskaj values

        # Backtrack until an older iterator can be resumed.
        i -= 1
        dopóki i >= 0:
            spróbuj:
                values[i] = iters[i]()
                # Success!  Start fresh at next level.
                i += 1
                przerwij
            wyjąwszy _StopIteration:
                # Continue backtracking.
                i -= 1
        inaczej:
            assert i < 0
            przerwij

# A conjoin-based N-Queens solver.

klasa Queens:
    def __init__(self, n):
        self.n = n
        rangen = range(n)

        # Assign a unique int to each column oraz diagonal.
        # columns:  n of those, range(n).
        # NW-SE diagonals: 2n-1 of these, i-j unique oraz invariant along
        # each, smallest i-j jest 0-(n-1) = 1-n, so add n-1 to shift to 0-
        # based.
        # NE-SW diagonals: 2n-1 of these, i+j unique oraz invariant along
        # each, smallest i+j jest 0, largest jest 2n-2.

        # For each square, compute a bit vector of the columns oraz
        # diagonals it covers, oraz dla each row compute a function that
        # generates the possiblities dla the columns w that row.
        self.rowgenerators = []
        dla i w rangen:
            rowuses = [(1 << j) |                  # column ordinal
                       (1 << (n + i-j + n-1)) |    # NW-SE ordinal
                       (1 << (n + 2*n-1 + i+j))    # NE-SW ordinal
                            dla j w rangen]

            def rowgen(rowuses=rowuses):
                dla j w rangen:
                    uses = rowuses[j]
                    jeżeli uses & self.used == 0:
                        self.used |= uses
                        uzyskaj j
                        self.used &= ~uses

            self.rowgenerators.append(rowgen)

    # Generate solutions.
    def solve(self):
        self.used = 0
        dla row2col w conjoin(self.rowgenerators):
            uzyskaj row2col

    def printsolution(self, row2col):
        n = self.n
        assert n == len(row2col)
        sep = "+" + "-+" * n
        print(sep)
        dla i w range(n):
            squares = [" " dla j w range(n)]
            squares[row2col[i]] = "Q"
            print("|" + "|".join(squares) + "|")
            print(sep)

# A conjoin-based Knight's Tour solver.  This jest pretty sophisticated
# (e.g., when used przy flat_conjoin above, oraz dalejing hard=1 to the
# constructor, a 200x200 Knight's Tour was found quickly -- note that we're
# creating 10s of thousands of generators then!), oraz jest lengthy.

klasa Knights:
    def __init__(self, m, n, hard=0):
        self.m, self.n = m, n

        # solve() will set up succs[i] to be a list of square #i's
        # successors.
        succs = self.succs = []

        # Remove i0 z each of its successor's successor lists, i.e.
        # successors can't go back to i0 again.  Return 0 jeżeli we can
        # detect this makes a solution impossible, inaczej zwróć 1.

        def remove_from_successors(i0, len=len):
            # If we remove all exits z a free square, we're dead:
            # even jeżeli we move to it next, we can't leave it again.
            # If we create a square przy one exit, we must visit it next;
            # inaczej somebody inaczej will have to visit it, oraz since there's
            # only one adjacent, there won't be a way to leave it again.
            # Finelly, jeżeli we create more than one free square przy a
            # single exit, we can only move to one of them next, leaving
            # the other one a dead end.
            ne0 = ne1 = 0
            dla i w succs[i0]:
                s = succs[i]
                s.remove(i0)
                e = len(s)
                jeżeli e == 0:
                    ne0 += 1
                albo_inaczej e == 1:
                    ne1 += 1
            zwróć ne0 == 0 oraz ne1 < 2

        # Put i0 back w each of its successor's successor lists.

        def add_to_successors(i0):
            dla i w succs[i0]:
                succs[i].append(i0)

        # Generate the first move.
        def first():
            jeżeli m < 1 albo n < 1:
                zwróć

            # Since we're looking dla a cycle, it doesn't matter where we
            # start.  Starting w a corner makes the 2nd move easy.
            corner = self.coords2index(0, 0)
            remove_from_successors(corner)
            self.lastij = corner
            uzyskaj corner
            add_to_successors(corner)

        # Generate the second moves.
        def second():
            corner = self.coords2index(0, 0)
            assert self.lastij == corner  # i.e., we started w the corner
            jeżeli m < 3 albo n < 3:
                zwróć
            assert len(succs[corner]) == 2
            assert self.coords2index(1, 2) w succs[corner]
            assert self.coords2index(2, 1) w succs[corner]
            # Only two choices.  Whichever we pick, the other must be the
            # square picked on move m*n, jako it's the only way to get back
            # to (0, 0).  Save its index w self.final so that moves before
            # the last know it must be kept free.
            dla i, j w (1, 2), (2, 1):
                this  = self.coords2index(i, j)
                final = self.coords2index(3-i, 3-j)
                self.final = final

                remove_from_successors(this)
                succs[final].append(corner)
                self.lastij = this
                uzyskaj this
                succs[final].remove(corner)
                add_to_successors(this)

        # Generate moves 3 thru m*n-1.
        def advance(len=len):
            # If some successor has only one exit, must take it.
            # Else favor successors przy fewer exits.
            candidates = []
            dla i w succs[self.lastij]:
                e = len(succs[i])
                assert e > 0, "inaczej remove_from_successors() pruning flawed"
                jeżeli e == 1:
                    candidates = [(e, i)]
                    przerwij
                candidates.append((e, i))
            inaczej:
                candidates.sort()

            dla e, i w candidates:
                jeżeli i != self.final:
                    jeżeli remove_from_successors(i):
                        self.lastij = i
                        uzyskaj i
                    add_to_successors(i)

        # Generate moves 3 thru m*n-1.  Alternative version using a
        # stronger (but more expensive) heuristic to order successors.
        # Since the # of backtracking levels jest m*n, a poor move early on
        # can take eons to undo.  Smallest square board dla which this
        # matters a lot jest 52x52.
        def advance_hard(vmid=(m-1)/2.0, hmid=(n-1)/2.0, len=len):
            # If some successor has only one exit, must take it.
            # Else favor successors przy fewer exits.
            # Break ties via max distance z board centerpoint (favor
            # corners oraz edges whenever possible).
            candidates = []
            dla i w succs[self.lastij]:
                e = len(succs[i])
                assert e > 0, "inaczej remove_from_successors() pruning flawed"
                jeżeli e == 1:
                    candidates = [(e, 0, i)]
                    przerwij
                i1, j1 = self.index2coords(i)
                d = (i1 - vmid)**2 + (j1 - hmid)**2
                candidates.append((e, -d, i))
            inaczej:
                candidates.sort()

            dla e, d, i w candidates:
                jeżeli i != self.final:
                    jeżeli remove_from_successors(i):
                        self.lastij = i
                        uzyskaj i
                    add_to_successors(i)

        # Generate the last move.
        def last():
            assert self.final w succs[self.lastij]
            uzyskaj self.final

        jeżeli m*n < 4:
            self.squaregenerators = [first]
        inaczej:
            self.squaregenerators = [first, second] + \
                [hard oraz advance_hard albo advance] * (m*n - 3) + \
                [last]

    def coords2index(self, i, j):
        assert 0 <= i < self.m
        assert 0 <= j < self.n
        zwróć i * self.n + j

    def index2coords(self, index):
        assert 0 <= index < self.m * self.n
        zwróć divmod(index, self.n)

    def _init_board(self):
        succs = self.succs
        usuń succs[:]
        m, n = self.m, self.n
        c2i = self.coords2index

        offsets = [( 1,  2), ( 2,  1), ( 2, -1), ( 1, -2),
                   (-1, -2), (-2, -1), (-2,  1), (-1,  2)]
        rangen = range(n)
        dla i w range(m):
            dla j w rangen:
                s = [c2i(i+io, j+jo) dla io, jo w offsets
                                     jeżeli 0 <= i+io < m oraz
                                        0 <= j+jo < n]
                succs.append(s)

    # Generate solutions.
    def solve(self):
        self._init_board()
        dla x w conjoin(self.squaregenerators):
            uzyskaj x

    def printsolution(self, x):
        m, n = self.m, self.n
        assert len(x) == m*n
        w = len(str(m*n))
        format = "%" + str(w) + "d"

        squares = [[Nic] * n dla i w range(m)]
        k = 1
        dla i w x:
            i1, j1 = self.index2coords(i)
            squares[i1][j1] = format % k
            k += 1

        sep = "+" + ("-" * w + "+") * n
        print(sep)
        dla i w range(m):
            row = squares[i]
            print("|" + "|".join(row) + "|")
            print(sep)

conjoin_tests = """

Generate the 3-bit binary numbers w order.  This illustrates dumbest-
possible use of conjoin, just to generate the full cross-product.

>>> dla c w conjoin([lambda: iter((0, 1))] * 3):
...     print(c)
[0, 0, 0]
[0, 0, 1]
[0, 1, 0]
[0, 1, 1]
[1, 0, 0]
[1, 0, 1]
[1, 1, 0]
[1, 1, 1]

For efficiency w typical backtracking apps, conjoin() uzyskajs the same list
object each time.  So jeżeli you want to save away a full account of its
generated sequence, you need to copy its results.

>>> def gencopy(iterator):
...     dla x w iterator:
...         uzyskaj x[:]

>>> dla n w range(10):
...     all = list(gencopy(conjoin([lambda: iter((0, 1))] * n)))
...     print(n, len(all), all[0] == [0] * n, all[-1] == [1] * n)
0 1 Prawda Prawda
1 2 Prawda Prawda
2 4 Prawda Prawda
3 8 Prawda Prawda
4 16 Prawda Prawda
5 32 Prawda Prawda
6 64 Prawda Prawda
7 128 Prawda Prawda
8 256 Prawda Prawda
9 512 Prawda Prawda

And run an 8-queens solver.

>>> q = Queens(8)
>>> LIMIT = 2
>>> count = 0
>>> dla row2col w q.solve():
...     count += 1
...     jeżeli count <= LIMIT:
...         print("Solution", count)
...         q.printsolution(row2col)
Solution 1
+-+-+-+-+-+-+-+-+
|Q| | | | | | | |
+-+-+-+-+-+-+-+-+
| | | | |Q| | | |
+-+-+-+-+-+-+-+-+
| | | | | | | |Q|
+-+-+-+-+-+-+-+-+
| | | | | |Q| | |
+-+-+-+-+-+-+-+-+
| | |Q| | | | | |
+-+-+-+-+-+-+-+-+
| | | | | | |Q| |
+-+-+-+-+-+-+-+-+
| |Q| | | | | | |
+-+-+-+-+-+-+-+-+
| | | |Q| | | | |
+-+-+-+-+-+-+-+-+
Solution 2
+-+-+-+-+-+-+-+-+
|Q| | | | | | | |
+-+-+-+-+-+-+-+-+
| | | | | |Q| | |
+-+-+-+-+-+-+-+-+
| | | | | | | |Q|
+-+-+-+-+-+-+-+-+
| | |Q| | | | | |
+-+-+-+-+-+-+-+-+
| | | | | | |Q| |
+-+-+-+-+-+-+-+-+
| | | |Q| | | | |
+-+-+-+-+-+-+-+-+
| |Q| | | | | | |
+-+-+-+-+-+-+-+-+
| | | | |Q| | | |
+-+-+-+-+-+-+-+-+

>>> print(count, "solutions w all.")
92 solutions w all.

And run a Knight's Tour on a 10x10 board.  Note that there are about
20,000 solutions even on a 6x6 board, so don't dare run this to exhaustion.

>>> k = Knights(10, 10)
>>> LIMIT = 2
>>> count = 0
>>> dla x w k.solve():
...     count += 1
...     jeżeli count <= LIMIT:
...         print("Solution", count)
...         k.printsolution(x)
...     inaczej:
...         przerwij
Solution 1
+---+---+---+---+---+---+---+---+---+---+
|  1| 58| 27| 34|  3| 40| 29| 10|  5|  8|
+---+---+---+---+---+---+---+---+---+---+
| 26| 35|  2| 57| 28| 33|  4|  7| 30| 11|
+---+---+---+---+---+---+---+---+---+---+
| 59|100| 73| 36| 41| 56| 39| 32|  9|  6|
+---+---+---+---+---+---+---+---+---+---+
| 74| 25| 60| 55| 72| 37| 42| 49| 12| 31|
+---+---+---+---+---+---+---+---+---+---+
| 61| 86| 99| 76| 63| 52| 47| 38| 43| 50|
+---+---+---+---+---+---+---+---+---+---+
| 24| 75| 62| 85| 54| 71| 64| 51| 48| 13|
+---+---+---+---+---+---+---+---+---+---+
| 87| 98| 91| 80| 77| 84| 53| 46| 65| 44|
+---+---+---+---+---+---+---+---+---+---+
| 90| 23| 88| 95| 70| 79| 68| 83| 14| 17|
+---+---+---+---+---+---+---+---+---+---+
| 97| 92| 21| 78| 81| 94| 19| 16| 45| 66|
+---+---+---+---+---+---+---+---+---+---+
| 22| 89| 96| 93| 20| 69| 82| 67| 18| 15|
+---+---+---+---+---+---+---+---+---+---+
Solution 2
+---+---+---+---+---+---+---+---+---+---+
|  1| 58| 27| 34|  3| 40| 29| 10|  5|  8|
+---+---+---+---+---+---+---+---+---+---+
| 26| 35|  2| 57| 28| 33|  4|  7| 30| 11|
+---+---+---+---+---+---+---+---+---+---+
| 59|100| 73| 36| 41| 56| 39| 32|  9|  6|
+---+---+---+---+---+---+---+---+---+---+
| 74| 25| 60| 55| 72| 37| 42| 49| 12| 31|
+---+---+---+---+---+---+---+---+---+---+
| 61| 86| 99| 76| 63| 52| 47| 38| 43| 50|
+---+---+---+---+---+---+---+---+---+---+
| 24| 75| 62| 85| 54| 71| 64| 51| 48| 13|
+---+---+---+---+---+---+---+---+---+---+
| 87| 98| 89| 80| 77| 84| 53| 46| 65| 44|
+---+---+---+---+---+---+---+---+---+---+
| 90| 23| 92| 95| 70| 79| 68| 83| 14| 17|
+---+---+---+---+---+---+---+---+---+---+
| 97| 88| 21| 78| 81| 94| 19| 16| 45| 66|
+---+---+---+---+---+---+---+---+---+---+
| 22| 91| 96| 93| 20| 69| 82| 67| 18| 15|
+---+---+---+---+---+---+---+---+---+---+
"""

weakref_tests = """\
Generators are weakly referencable:

>>> zaimportuj weakref
>>> def gen():
...     uzyskaj 'foo!'
...
>>> wr = weakref.ref(gen)
>>> wr() jest gen
Prawda
>>> p = weakref.proxy(gen)

Generator-iterators are weakly referencable jako well:

>>> gi = gen()
>>> wr = weakref.ref(gi)
>>> wr() jest gi
Prawda
>>> p = weakref.proxy(gi)
>>> list(p)
['foo!']

"""

coroutine_tests = """\
Sending a value into a started generator:

>>> def f():
...     print((uzyskaj 1))
...     uzyskaj 2
>>> g = f()
>>> next(g)
1
>>> g.send(42)
42
2

Sending a value into a new generator produces a TypeError:

>>> f().send("foo")
Traceback (most recent call last):
...
TypeError: can't send non-Nic value to a just-started generator


Yield by itself uzyskajs Nic:

>>> def f(): uzyskaj
>>> list(f())
[Nic]



An obscene abuse of a uzyskaj expression within a generator expression:

>>> list((uzyskaj 21) dla i w range(4))
[21, Nic, 21, Nic, 21, Nic, 21, Nic]

And a more sane, but still weird usage:

>>> def f(): list(i dla i w [(uzyskaj 26)])
>>> type(f())
<class 'generator'>


A uzyskaj expression przy augmented assignment.

>>> def coroutine(seq):
...     count = 0
...     dopóki count < 200:
...         count += uzyskaj
...         seq.append(count)
>>> seq = []
>>> c = coroutine(seq)
>>> next(c)
>>> print(seq)
[]
>>> c.send(10)
>>> print(seq)
[10]
>>> c.send(10)
>>> print(seq)
[10, 20]
>>> c.send(10)
>>> print(seq)
[10, 20, 30]


Check some syntax errors dla uzyskaj expressions:

>>> f=lambda: (uzyskaj 1),(uzyskaj 2)
Traceback (most recent call last):
  ...
SyntaxError: 'uzyskaj' outside function

>>> def f(): x = uzyskaj = y
Traceback (most recent call last):
  ...
SyntaxError: assignment to uzyskaj expression nie possible

>>> def f(): (uzyskaj bar) = y
Traceback (most recent call last):
  ...
SyntaxError: can't assign to uzyskaj expression

>>> def f(): (uzyskaj bar) += y
Traceback (most recent call last):
  ...
SyntaxError: can't assign to uzyskaj expression


Now check some throw() conditions:

>>> def f():
...     dopóki Prawda:
...         spróbuj:
...             print((uzyskaj))
...         wyjąwszy ValueError jako v:
...             print("caught ValueError (%s)" % (v))
>>> zaimportuj sys
>>> g = f()
>>> next(g)

>>> g.throw(ValueError) # type only
caught ValueError ()

>>> g.throw(ValueError("xyz"))  # value only
caught ValueError (xyz)

>>> g.throw(ValueError, ValueError(1))   # value+matching type
caught ValueError (1)

>>> g.throw(ValueError, TypeError(1))  # mismatched type, rewrapped
caught ValueError (1)

>>> g.throw(ValueError, ValueError(1), Nic)   # explicit Nic traceback
caught ValueError (1)

>>> g.throw(ValueError(1), "foo")       # bad args
Traceback (most recent call last):
  ...
TypeError: instance exception may nie have a separate value

>>> g.throw(ValueError, "foo", 23)      # bad args
Traceback (most recent call last):
  ...
TypeError: throw() third argument must be a traceback object

>>> g.throw("abc")
Traceback (most recent call last):
  ...
TypeError: exceptions must be classes albo instances deriving z BaseException, nie str

>>> g.throw(0)
Traceback (most recent call last):
  ...
TypeError: exceptions must be classes albo instances deriving z BaseException, nie int

>>> g.throw(list)
Traceback (most recent call last):
  ...
TypeError: exceptions must be classes albo instances deriving z BaseException, nie type

>>> def throw(g,exc):
...     spróbuj:
...         podnieś exc
...     wyjąwszy:
...         g.throw(*sys.exc_info())
>>> throw(g,ValueError) # do it przy traceback included
caught ValueError ()

>>> g.send(1)
1

>>> throw(g,TypeError)  # terminate the generator
Traceback (most recent call last):
  ...
TypeError

>>> print(g.gi_frame)
Nic

>>> g.send(2)
Traceback (most recent call last):
  ...
StopIteration

>>> g.throw(ValueError,6)       # throw on closed generator
Traceback (most recent call last):
  ...
ValueError: 6

>>> f().throw(ValueError,7)     # throw on just-opened generator
Traceback (most recent call last):
  ...
ValueError: 7

Plain "raise" inside a generator should preserve the traceback (#13188).
The traceback should have 3 levels:
- g.throw()
- f()
- 1/0

>>> def f():
...     spróbuj:
...         uzyskaj
...     wyjąwszy:
...         podnieś
>>> g = f()
>>> spróbuj:
...     1/0
... wyjąwszy ZeroDivisionError jako v:
...     spróbuj:
...         g.throw(v)
...     wyjąwszy Exception jako w:
...         tb = w.__traceback__
>>> levels = 0
>>> dopóki tb:
...     levels += 1
...     tb = tb.tb_next
>>> levels
3

Now let's try closing a generator:

>>> def f():
...     spróbuj: uzyskaj
...     wyjąwszy GeneratorExit:
...         print("exiting")

>>> g = f()
>>> next(g)
>>> g.close()
exiting
>>> g.close()  # should be no-op now

>>> f().close()  # close on just-opened generator should be fine

>>> def f(): uzyskaj      # an even simpler generator
>>> f().close()         # close before opening
>>> g = f()
>>> next(g)
>>> g.close()           # close normally

And finalization:

>>> def f():
...     spróbuj: uzyskaj
...     w_końcu:
...         print("exiting")

>>> g = f()
>>> next(g)
>>> usuń g
exiting


GeneratorExit jest nie caught by wyjąwszy Exception:

>>> def f():
...     spróbuj: uzyskaj
...     wyjąwszy Exception:
...         print('except')
...     w_końcu:
...         print('finally')

>>> g = f()
>>> next(g)
>>> usuń g
finally


Now let's try some ill-behaved generators:

>>> def f():
...     spróbuj: uzyskaj
...     wyjąwszy GeneratorExit:
...         uzyskaj "foo!"
>>> g = f()
>>> next(g)
>>> g.close()
Traceback (most recent call last):
  ...
RuntimeError: generator ignored GeneratorExit
>>> g.close()


Our ill-behaved code should be invoked during GC:

>>> zaimportuj sys, io
>>> old, sys.stderr = sys.stderr, io.StringIO()
>>> g = f()
>>> next(g)
>>> usuń g
>>> "RuntimeError: generator ignored GeneratorExit" w sys.stderr.getvalue()
Prawda
>>> sys.stderr = old


And errors thrown during closing should propagate:

>>> def f():
...     spróbuj: uzyskaj
...     wyjąwszy GeneratorExit:
...         podnieś TypeError("fie!")
>>> g = f()
>>> next(g)
>>> g.close()
Traceback (most recent call last):
  ...
TypeError: fie!


Ensure that various uzyskaj expression constructs make their
enclosing function a generator:

>>> def f(): x += uzyskaj
>>> type(f())
<class 'generator'>

>>> def f(): x = uzyskaj
>>> type(f())
<class 'generator'>

>>> def f(): lambda x=(uzyskaj): 1
>>> type(f())
<class 'generator'>

>>> def f(): x=(i dla i w (uzyskaj) jeżeli (uzyskaj))
>>> type(f())
<class 'generator'>

>>> def f(d): d[(uzyskaj "a")] = d[(uzyskaj "b")] = 27
>>> data = [1,2]
>>> g = f(data)
>>> type(g)
<class 'generator'>
>>> g.send(Nic)
'a'
>>> data
[1, 2]
>>> g.send(0)
'b'
>>> data
[27, 2]
>>> spróbuj: g.send(1)
... wyjąwszy StopIteration: dalej
>>> data
[27, 27]

"""

refleaks_tests = """
Prior to adding cycle-GC support to itertools.tee, this code would leak
references. We add it to the standard suite so the routine refleak-tests
would trigger jeżeli it starts being uncleanable again.

>>> zaimportuj itertools
>>> def leak():
...     klasa gen:
...         def __iter__(self):
...             zwróć self
...         def __next__(self):
...             zwróć self.item
...     g = gen()
...     head, tail = itertools.tee(g)
...     g.item = head
...     zwróć head
>>> it = leak()

Make sure to also test the involvement of the tee-internal teedataobject,
which stores returned items.

>>> item = next(it)



This test leaked at one point due to generator finalization/destruction.
It was copied z Lib/test/leakers/test_generator_cycle.py before the file
was removed.

>>> def leak():
...    def gen():
...        dopóki Prawda:
...            uzyskaj g
...    g = gen()

>>> leak()



This test isn't really generator related, but rather exception-in-cleanup
related. The coroutine tests (above) just happen to cause an exception w
the generator's __del__ (tp_del) method. We can also test dla this
explicitly, without generators. We do have to redirect stderr to avoid
printing warnings oraz to doublecheck that we actually tested what we wanted
to test.

>>> zaimportuj sys, io
>>> old = sys.stderr
>>> spróbuj:
...     sys.stderr = io.StringIO()
...     klasa Leaker:
...         def __del__(self):
...             def invoke(message):
...                 podnieś RuntimeError(message)
...             invoke("test")
...
...     l = Leaker()
...     usuń l
...     err = sys.stderr.getvalue().strip()
...     "Exception ignored in" w err
...     "RuntimeError: test" w err
...     "Traceback" w err
...     "in invoke" w err
... w_końcu:
...     sys.stderr = old
Prawda
Prawda
Prawda
Prawda


These refleak tests should perhaps be w a testfile of their own,
test_generators just happened to be the test that drew these out.

"""

__test__ = {"tut":      tutorial_tests,
            "pep":      pep_tests,
            "email":    email_tests,
            "fun":      fun_tests,
            "syntax":   syntax_tests,
            "conjoin":  conjoin_tests,
            "weakref":  weakref_tests,
            "coroutine":  coroutine_tests,
            "refleaks": refleaks_tests,
            }

# Magic test name that regrtest.py invokes *after* importing this module.
# This worms around a bootstrap problem.
# Note that doctest oraz regrtest both look w sys.argv dla a "-v" argument,
# so this works jako expected w both ways of running regrtest.
def test_main(verbose=Nic):
    z test zaimportuj support, test_generators
    support.run_unittest(__name__)
    support.run_doctest(test_generators, verbose)

# This part isn't needed dla regrtest, but dla running the test directly.
jeżeli __name__ == "__main__":
    test_main(1)
