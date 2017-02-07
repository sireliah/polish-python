""" Test Iterator Length Transparency

Some functions albo methods which accept general iterable arguments have
optional, more efficient code paths jeżeli they know how many items to expect.
For instance, map(func, iterable), will pre-allocate the exact amount of
space required whenever the iterable can report its length.

The desired invariant is:  len(it)==len(list(it)).

A complication jest that an iterable oraz iterator can be the same object. To
maintain the invariant, an iterator needs to dynamically update its length.
For instance, an iterable such jako range(10) always reports its length jako ten,
but it=iter(range(10)) starts at ten, oraz then goes to nine after next(it).
Having this capability means that map() can ignore the distinction between
map(func, iterable) oraz map(func, iter(iterable)).

When the iterable jest immutable, the implementation can straight-forwardly
report the original length minus the cumulative number of calls to next().
This jest the case dla tuples, range objects, oraz itertools.repeat().

Some containers become temporarily immutable during iteration.  This includes
dicts, sets, oraz collections.deque.  Their implementation jest equally simple
though they need to permanently set their length to zero whenever there jest
an attempt to iterate after a length mutation.

The situation slightly more involved whenever an object allows length mutation
during iteration.  Lists oraz sequence iterators are dynamically updatable.
So, jeżeli a list jest extended during iteration, the iterator will continue through
the new items.  If it shrinks to a point before the most recent iteration,
then no further items are available oraz the length jest reported at zero.

Reversed objects can also be wrapped around mutable objects; however, any
appends after the current position are ignored.  Any other approach leads
to confusion oraz possibly returning the same item more than once.

The iterators nie listed above, such jako enumerate oraz the other itertools,
are nie length transparent because they have no way to distinguish between
iterables that report static length oraz iterators whose length changes with
each call (i.e. the difference between enumerate('abc') oraz
enumerate(iter('abc')).

"""

zaimportuj unittest
z test zaimportuj support
z itertools zaimportuj repeat
z collections zaimportuj deque
z operator zaimportuj length_hint

n = 10


klasa TestInvariantWithoutMutations:

    def test_invariant(self):
        it = self.it
        dla i w reversed(range(1, n+1)):
            self.assertEqual(length_hint(it), i)
            next(it)
        self.assertEqual(length_hint(it), 0)
        self.assertRaises(StopIteration, next, it)
        self.assertEqual(length_hint(it), 0)

klasa TestTemporarilyImmutable(TestInvariantWithoutMutations):

    def test_immutable_during_iteration(self):
        # objects such jako deques, sets, oraz dictionaries enforce
        # length immutability  during iteration

        it = self.it
        self.assertEqual(length_hint(it), n)
        next(it)
        self.assertEqual(length_hint(it), n-1)
        self.mutate()
        self.assertRaises(RuntimeError, next, it)
        self.assertEqual(length_hint(it), 0)

## ------- Concrete Type Tests -------

klasa TestRepeat(TestInvariantWithoutMutations, unittest.TestCase):

    def setUp(self):
        self.it = repeat(Nic, n)

klasa TestXrange(TestInvariantWithoutMutations, unittest.TestCase):

    def setUp(self):
        self.it = iter(range(n))

klasa TestXrangeCustomReversed(TestInvariantWithoutMutations, unittest.TestCase):

    def setUp(self):
        self.it = reversed(range(n))

klasa TestTuple(TestInvariantWithoutMutations, unittest.TestCase):

    def setUp(self):
        self.it = iter(tuple(range(n)))

## ------- Types that should nie be mutated during iteration -------

klasa TestDeque(TestTemporarilyImmutable, unittest.TestCase):

    def setUp(self):
        d = deque(range(n))
        self.it = iter(d)
        self.mutate = d.pop

klasa TestDequeReversed(TestTemporarilyImmutable, unittest.TestCase):

    def setUp(self):
        d = deque(range(n))
        self.it = reversed(d)
        self.mutate = d.pop

klasa TestDictKeys(TestTemporarilyImmutable, unittest.TestCase):

    def setUp(self):
        d = dict.fromkeys(range(n))
        self.it = iter(d)
        self.mutate = d.popitem

klasa TestDictItems(TestTemporarilyImmutable, unittest.TestCase):

    def setUp(self):
        d = dict.fromkeys(range(n))
        self.it = iter(d.items())
        self.mutate = d.popitem

klasa TestDictValues(TestTemporarilyImmutable, unittest.TestCase):

    def setUp(self):
        d = dict.fromkeys(range(n))
        self.it = iter(d.values())
        self.mutate = d.popitem

klasa TestSet(TestTemporarilyImmutable, unittest.TestCase):

    def setUp(self):
        d = set(range(n))
        self.it = iter(d)
        self.mutate = d.pop

## ------- Types that can mutate during iteration -------

klasa TestList(TestInvariantWithoutMutations, unittest.TestCase):

    def setUp(self):
        self.it = iter(range(n))

    def test_mutation(self):
        d = list(range(n))
        it = iter(d)
        next(it)
        next(it)
        self.assertEqual(length_hint(it), n - 2)
        d.append(n)
        self.assertEqual(length_hint(it), n - 1)  # grow przy append
        d[1:] = []
        self.assertEqual(length_hint(it), 0)
        self.assertEqual(list(it), [])
        d.extend(range(20))
        self.assertEqual(length_hint(it), 0)


klasa TestListReversed(TestInvariantWithoutMutations, unittest.TestCase):

    def setUp(self):
        self.it = reversed(range(n))

    def test_mutation(self):
        d = list(range(n))
        it = reversed(d)
        next(it)
        next(it)
        self.assertEqual(length_hint(it), n - 2)
        d.append(n)
        self.assertEqual(length_hint(it), n - 2)  # ignore append
        d[1:] = []
        self.assertEqual(length_hint(it), 0)
        self.assertEqual(list(it), [])  # confirm invariant
        d.extend(range(20))
        self.assertEqual(length_hint(it), 0)

## -- Check to make sure exceptions are nie suppressed by __length_hint__()


klasa BadLen(object):
    def __iter__(self):
        zwróć iter(range(10))

    def __len__(self):
        podnieś RuntimeError('hello')


klasa BadLengthHint(object):
    def __iter__(self):
        zwróć iter(range(10))

    def __length_hint__(self):
        podnieś RuntimeError('hello')


klasa NicLengthHint(object):
    def __iter__(self):
        zwróć iter(range(10))

    def __length_hint__(self):
        zwróć NotImplemented


klasa TestLengthHintExceptions(unittest.TestCase):

    def test_issue1242657(self):
        self.assertRaises(RuntimeError, list, BadLen())
        self.assertRaises(RuntimeError, list, BadLengthHint())
        self.assertRaises(RuntimeError, [].extend, BadLen())
        self.assertRaises(RuntimeError, [].extend, BadLengthHint())
        b = bytearray(range(10))
        self.assertRaises(RuntimeError, b.extend, BadLen())
        self.assertRaises(RuntimeError, b.extend, BadLengthHint())

    def test_invalid_hint(self):
        # Make sure an invalid result doesn't muck-up the works
        self.assertEqual(list(NicLengthHint()), list(range(10)))


jeżeli __name__ == "__main__":
    unittest.main()
