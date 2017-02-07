zaimportuj unittest
zaimportuj operator
zaimportuj sys
zaimportuj pickle

z test zaimportuj support

klasa G:
    'Sequence using __getitem__'
    def __init__(self, seqn):
        self.seqn = seqn
    def __getitem__(self, i):
        zwróć self.seqn[i]

klasa I:
    'Sequence using iterator protocol'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        zwróć self
    def __next__(self):
        jeżeli self.i >= len(self.seqn): podnieś StopIteration
        v = self.seqn[self.i]
        self.i += 1
        zwróć v

klasa Ig:
    'Sequence using iterator protocol defined przy a generator'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        dla val w self.seqn:
            uzyskaj val

klasa X:
    'Missing __getitem__ oraz __iter__'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __next__(self):
        jeżeli self.i >= len(self.seqn): podnieś StopIteration
        v = self.seqn[self.i]
        self.i += 1
        zwróć v

klasa E:
    'Test propagation of exceptions'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        zwróć self
    def __next__(self):
        3 // 0

klasa N:
    'Iterator missing __next__()'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        zwróć self

klasa PickleTest:
    # Helper to check picklability
    def check_pickle(self, itorg, seq):
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            d = pickle.dumps(itorg, proto)
            it = pickle.loads(d)
            self.assertEqual(type(itorg), type(it))
            self.assertEqual(list(it), seq)

            it = pickle.loads(d)
            spróbuj:
                next(it)
            wyjąwszy StopIteration:
                self.assertNieprawda(seq[1:])
                kontynuuj
            d = pickle.dumps(it, proto)
            it = pickle.loads(d)
            self.assertEqual(list(it), seq[1:])

klasa EnumerateTestCase(unittest.TestCase, PickleTest):

    enum = enumerate
    seq, res = 'abc', [(0,'a'), (1,'b'), (2,'c')]

    def test_basicfunction(self):
        self.assertEqual(type(self.enum(self.seq)), self.enum)
        e = self.enum(self.seq)
        self.assertEqual(iter(e), e)
        self.assertEqual(list(self.enum(self.seq)), self.res)
        self.enum.__doc__

    def test_pickle(self):
        self.check_pickle(self.enum(self.seq), self.res)

    def test_getitemseqn(self):
        self.assertEqual(list(self.enum(G(self.seq))), self.res)
        e = self.enum(G(''))
        self.assertRaises(StopIteration, next, e)

    def test_iteratorseqn(self):
        self.assertEqual(list(self.enum(I(self.seq))), self.res)
        e = self.enum(I(''))
        self.assertRaises(StopIteration, next, e)

    def test_iteratorgenerator(self):
        self.assertEqual(list(self.enum(Ig(self.seq))), self.res)
        e = self.enum(Ig(''))
        self.assertRaises(StopIteration, next, e)

    def test_noniterable(self):
        self.assertRaises(TypeError, self.enum, X(self.seq))

    def test_illformediterable(self):
        self.assertRaises(TypeError, self.enum, N(self.seq))

    def test_exception_propagation(self):
        self.assertRaises(ZeroDivisionError, list, self.enum(E(self.seq)))

    def test_argumentcheck(self):
        self.assertRaises(TypeError, self.enum) # no arguments
        self.assertRaises(TypeError, self.enum, 1) # wrong type (nie iterable)
        self.assertRaises(TypeError, self.enum, 'abc', 'a') # wrong type
        self.assertRaises(TypeError, self.enum, 'abc', 2, 3) # too many arguments

    @support.cpython_only
    def test_tuple_reuse(self):
        # Tests an implementation detail where tuple jest reused
        # whenever nothing inaczej holds a reference to it
        self.assertEqual(len(set(map(id, list(enumerate(self.seq))))), len(self.seq))
        self.assertEqual(len(set(map(id, enumerate(self.seq)))), min(1,len(self.seq)))

klasa MyEnum(enumerate):
    dalej

klasa SubclassTestCase(EnumerateTestCase):

    enum = MyEnum

klasa TestEmpty(EnumerateTestCase):

    seq, res = '', []

klasa TestBig(EnumerateTestCase):

    seq = range(10,20000,2)
    res = list(zip(range(20000), seq))

klasa TestReversed(unittest.TestCase, PickleTest):

    def test_simple(self):
        klasa A:
            def __getitem__(self, i):
                jeżeli i < 5:
                    zwróć str(i)
                podnieś StopIteration
            def __len__(self):
                zwróć 5
        dla data w 'abc', range(5), tuple(enumerate('abc')), A(), range(1,17,5):
            self.assertEqual(list(data)[::-1], list(reversed(data)))
        self.assertRaises(TypeError, reversed, {})
        # don't allow keyword arguments
        self.assertRaises(TypeError, reversed, [], a=1)

    def test_range_optimization(self):
        x = range(1)
        self.assertEqual(type(reversed(x)), type(iter(x)))

    def test_len(self):
        dla s w ('hello', tuple('hello'), list('hello'), range(5)):
            self.assertEqual(operator.length_hint(reversed(s)), len(s))
            r = reversed(s)
            list(r)
            self.assertEqual(operator.length_hint(r), 0)
        klasa SeqWithWeirdLen:
            called = Nieprawda
            def __len__(self):
                jeżeli nie self.called:
                    self.called = Prawda
                    zwróć 10
                podnieś ZeroDivisionError
            def __getitem__(self, index):
                zwróć index
        r = reversed(SeqWithWeirdLen())
        self.assertRaises(ZeroDivisionError, operator.length_hint, r)


    def test_gc(self):
        klasa Seq:
            def __len__(self):
                zwróć 10
            def __getitem__(self, index):
                zwróć index
        s = Seq()
        r = reversed(s)
        s.r = r

    def test_args(self):
        self.assertRaises(TypeError, reversed)
        self.assertRaises(TypeError, reversed, [], 'extra')

    @unittest.skipUnless(hasattr(sys, 'getrefcount'), 'test needs sys.getrefcount()')
    def test_bug1229429(self):
        # this bug was never w reversed, it was w
        # PyObject_CallMethod, oraz reversed_new calls that sometimes.
        def f():
            dalej
        r = f.__reversed__ = object()
        rc = sys.getrefcount(r)
        dla i w range(10):
            spróbuj:
                reversed(f)
            wyjąwszy TypeError:
                dalej
            inaczej:
                self.fail("non-callable __reversed__ didn't podnieś!")
        self.assertEqual(rc, sys.getrefcount(r))

    def test_objmethods(self):
        # Objects must have __len__() oraz __getitem__() implemented.
        klasa NoLen(object):
            def __getitem__(self): zwróć 1
        nl = NoLen()
        self.assertRaises(TypeError, reversed, nl)

        klasa NoGetItem(object):
            def __len__(self): zwróć 2
        ngi = NoGetItem()
        self.assertRaises(TypeError, reversed, ngi)

    def test_pickle(self):
        dla data w 'abc', range(5), tuple(enumerate('abc')), range(1,17,5):
            self.check_pickle(reversed(data), list(data)[::-1])


klasa EnumerateStartTestCase(EnumerateTestCase):

    def test_basicfunction(self):
        e = self.enum(self.seq)
        self.assertEqual(iter(e), e)
        self.assertEqual(list(self.enum(self.seq)), self.res)


klasa TestStart(EnumerateStartTestCase):

    enum = lambda self, i: enumerate(i, start=11)
    seq, res = 'abc', [(11, 'a'), (12, 'b'), (13, 'c')]


klasa TestLongStart(EnumerateStartTestCase):

    enum = lambda self, i: enumerate(i, start=sys.maxsize+1)
    seq, res = 'abc', [(sys.maxsize+1,'a'), (sys.maxsize+2,'b'),
                       (sys.maxsize+3,'c')]


jeżeli __name__ == "__main__":
    unittest.main()
