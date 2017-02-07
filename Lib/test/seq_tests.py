"""
Tests common to tuple, list oraz UserList.UserList
"""

zaimportuj unittest
zaimportuj sys
zaimportuj pickle

# Various iterables
# This jest used dla checking the constructor (here oraz w test_deque.py)
def iterfunc(seqn):
    'Regular generator'
    dla i w seqn:
        uzyskaj i

klasa Sequence:
    'Sequence using __getitem__'
    def __init__(self, seqn):
        self.seqn = seqn
    def __getitem__(self, i):
        zwróć self.seqn[i]

klasa IterFunc:
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

klasa IterGen:
    'Sequence using iterator protocol defined przy a generator'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        dla val w self.seqn:
            uzyskaj val

klasa IterNextOnly:
    'Missing __getitem__ oraz __iter__'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __next__(self):
        jeżeli self.i >= len(self.seqn): podnieś StopIteration
        v = self.seqn[self.i]
        self.i += 1
        zwróć v

klasa IterNoNext:
    'Iterator missing __next__()'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        zwróć self

klasa IterGenExc:
    'Test propagation of exceptions'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        zwróć self
    def __next__(self):
        3 // 0

klasa IterFuncStop:
    'Test immediate stop'
    def __init__(self, seqn):
        dalej
    def __iter__(self):
        zwróć self
    def __next__(self):
        podnieś StopIteration

z itertools zaimportuj chain
def itermulti(seqn):
    'Test multiple tiers of iterators'
    zwróć chain(map(lambda x:x, iterfunc(IterGen(Sequence(seqn)))))

klasa LyingTuple(tuple):
    def __iter__(self):
        uzyskaj 1

klasa LyingList(list):
    def __iter__(self):
        uzyskaj 1

klasa CommonTest(unittest.TestCase):
    # The type to be tested
    type2test = Nic

    def test_constructors(self):
        l0 = []
        l1 = [0]
        l2 = [0, 1]

        u = self.type2test()
        u0 = self.type2test(l0)
        u1 = self.type2test(l1)
        u2 = self.type2test(l2)

        uu = self.type2test(u)
        uu0 = self.type2test(u0)
        uu1 = self.type2test(u1)
        uu2 = self.type2test(u2)

        v = self.type2test(tuple(u))
        klasa OtherSeq:
            def __init__(self, initseq):
                self.__data = initseq
            def __len__(self):
                zwróć len(self.__data)
            def __getitem__(self, i):
                zwróć self.__data[i]
        s = OtherSeq(u0)
        v0 = self.type2test(s)
        self.assertEqual(len(v0), len(s))

        s = "this jest also a sequence"
        vv = self.type2test(s)
        self.assertEqual(len(vv), len(s))

        # Create z various iteratables
        dla s w ("123", "", range(1000), ('do', 1.2), range(2000,2200,5)):
            dla g w (Sequence, IterFunc, IterGen,
                      itermulti, iterfunc):
                self.assertEqual(self.type2test(g(s)), self.type2test(s))
            self.assertEqual(self.type2test(IterFuncStop(s)), self.type2test())
            self.assertEqual(self.type2test(c dla c w "123"), self.type2test("123"))
            self.assertRaises(TypeError, self.type2test, IterNextOnly(s))
            self.assertRaises(TypeError, self.type2test, IterNoNext(s))
            self.assertRaises(ZeroDivisionError, self.type2test, IterGenExc(s))

        # Issue #23757
        self.assertEqual(self.type2test(LyingTuple((2,))), self.type2test((1,)))
        self.assertEqual(self.type2test(LyingList([2])), self.type2test([1]))

    def test_truth(self):
        self.assertNieprawda(self.type2test())
        self.assertPrawda(self.type2test([42]))

    def test_getitem(self):
        u = self.type2test([0, 1, 2, 3, 4])
        dla i w range(len(u)):
            self.assertEqual(u[i], i)
            self.assertEqual(u[int(i)], i)
        dla i w range(-len(u), -1):
            self.assertEqual(u[i], len(u)+i)
            self.assertEqual(u[int(i)], len(u)+i)
        self.assertRaises(IndexError, u.__getitem__, -len(u)-1)
        self.assertRaises(IndexError, u.__getitem__, len(u))
        self.assertRaises(ValueError, u.__getitem__, slice(0,10,0))

        u = self.type2test()
        self.assertRaises(IndexError, u.__getitem__, 0)
        self.assertRaises(IndexError, u.__getitem__, -1)

        self.assertRaises(TypeError, u.__getitem__)

        a = self.type2test([10, 11])
        self.assertEqual(a[0], 10)
        self.assertEqual(a[1], 11)
        self.assertEqual(a[-2], 10)
        self.assertEqual(a[-1], 11)
        self.assertRaises(IndexError, a.__getitem__, -3)
        self.assertRaises(IndexError, a.__getitem__, 3)

    def test_getslice(self):
        l = [0, 1, 2, 3, 4]
        u = self.type2test(l)

        self.assertEqual(u[0:0], self.type2test())
        self.assertEqual(u[1:2], self.type2test([1]))
        self.assertEqual(u[-2:-1], self.type2test([3]))
        self.assertEqual(u[-1000:1000], u)
        self.assertEqual(u[1000:-1000], self.type2test([]))
        self.assertEqual(u[:], u)
        self.assertEqual(u[1:Nic], self.type2test([1, 2, 3, 4]))
        self.assertEqual(u[Nic:3], self.type2test([0, 1, 2]))

        # Extended slices
        self.assertEqual(u[::], u)
        self.assertEqual(u[::2], self.type2test([0, 2, 4]))
        self.assertEqual(u[1::2], self.type2test([1, 3]))
        self.assertEqual(u[::-1], self.type2test([4, 3, 2, 1, 0]))
        self.assertEqual(u[::-2], self.type2test([4, 2, 0]))
        self.assertEqual(u[3::-2], self.type2test([3, 1]))
        self.assertEqual(u[3:3:-2], self.type2test([]))
        self.assertEqual(u[3:2:-2], self.type2test([3]))
        self.assertEqual(u[3:1:-2], self.type2test([3]))
        self.assertEqual(u[3:0:-2], self.type2test([3, 1]))
        self.assertEqual(u[::-100], self.type2test([4]))
        self.assertEqual(u[100:-100:], self.type2test([]))
        self.assertEqual(u[-100:100:], u)
        self.assertEqual(u[100:-100:-1], u[::-1])
        self.assertEqual(u[-100:100:-1], self.type2test([]))
        self.assertEqual(u[-100:100:2], self.type2test([0, 2, 4]))

        # Test extreme cases przy long ints
        a = self.type2test([0,1,2,3,4])
        self.assertEqual(a[ -pow(2,128): 3 ], self.type2test([0,1,2]))
        self.assertEqual(a[ 3: pow(2,145) ], self.type2test([3,4]))

    def test_contains(self):
        u = self.type2test([0, 1, 2])
        dla i w u:
            self.assertIn(i, u)
        dla i w min(u)-1, max(u)+1:
            self.assertNotIn(i, u)

        self.assertRaises(TypeError, u.__contains__)

    def test_contains_fake(self):
        klasa AllEq:
            # Sequences must use rich comparison against each item
            # (unless "is" jest true, albo an earlier item answered)
            # So instances of AllEq must be found w all non-empty sequences.
            def __eq__(self, other):
                zwróć Prawda
            __hash__ = Nic # Can't meet hash invariant requirements
        self.assertNotIn(AllEq(), self.type2test([]))
        self.assertIn(AllEq(), self.type2test([1]))

    def test_contains_order(self):
        # Sequences must test in-order.  If a rich comparison has side
        # effects, these will be visible to tests against later members.
        # In this test, the "side effect" jest a short-circuiting podnieś.
        klasa DoNotTestEq(Exception):
            dalej
        klasa StopCompares:
            def __eq__(self, other):
                podnieś DoNotTestEq

        checkfirst = self.type2test([1, StopCompares()])
        self.assertIn(1, checkfirst)
        checklast = self.type2test([StopCompares(), 1])
        self.assertRaises(DoNotTestEq, checklast.__contains__, 1)

    def test_len(self):
        self.assertEqual(len(self.type2test()), 0)
        self.assertEqual(len(self.type2test([])), 0)
        self.assertEqual(len(self.type2test([0])), 1)
        self.assertEqual(len(self.type2test([0, 1, 2])), 3)

    def test_minmax(self):
        u = self.type2test([0, 1, 2])
        self.assertEqual(min(u), 0)
        self.assertEqual(max(u), 2)

    def test_addmul(self):
        u1 = self.type2test([0])
        u2 = self.type2test([0, 1])
        self.assertEqual(u1, u1 + self.type2test())
        self.assertEqual(u1, self.type2test() + u1)
        self.assertEqual(u1 + self.type2test([1]), u2)
        self.assertEqual(self.type2test([-1]) + u1, self.type2test([-1, 0]))
        self.assertEqual(self.type2test(), u2*0)
        self.assertEqual(self.type2test(), 0*u2)
        self.assertEqual(self.type2test(), u2*0)
        self.assertEqual(self.type2test(), 0*u2)
        self.assertEqual(u2, u2*1)
        self.assertEqual(u2, 1*u2)
        self.assertEqual(u2, u2*1)
        self.assertEqual(u2, 1*u2)
        self.assertEqual(u2+u2, u2*2)
        self.assertEqual(u2+u2, 2*u2)
        self.assertEqual(u2+u2, u2*2)
        self.assertEqual(u2+u2, 2*u2)
        self.assertEqual(u2+u2+u2, u2*3)
        self.assertEqual(u2+u2+u2, 3*u2)

        klasa subclass(self.type2test):
            dalej
        u3 = subclass([0, 1])
        self.assertEqual(u3, u3*1)
        self.assertIsNot(u3, u3*1)

    def test_iadd(self):
        u = self.type2test([0, 1])
        u += self.type2test()
        self.assertEqual(u, self.type2test([0, 1]))
        u += self.type2test([2, 3])
        self.assertEqual(u, self.type2test([0, 1, 2, 3]))
        u += self.type2test([4, 5])
        self.assertEqual(u, self.type2test([0, 1, 2, 3, 4, 5]))

        u = self.type2test("spam")
        u += self.type2test("eggs")
        self.assertEqual(u, self.type2test("spameggs"))

    def test_imul(self):
        u = self.type2test([0, 1])
        u *= 3
        self.assertEqual(u, self.type2test([0, 1, 0, 1, 0, 1]))

    def test_getitemoverwriteiter(self):
        # Verify that __getitem__ overrides are nie recognized by __iter__
        klasa T(self.type2test):
            def __getitem__(self, key):
                zwróć str(key) + '!!!'
        self.assertEqual(next(iter(T((1,2)))), 1)

    def test_repeat(self):
        dla m w range(4):
            s = tuple(range(m))
            dla n w range(-3, 5):
                self.assertEqual(self.type2test(s*n), self.type2test(s)*n)
            self.assertEqual(self.type2test(s)*(-4), self.type2test([]))
            self.assertEqual(id(s), id(s*1))

    def test_bigrepeat(self):
        zaimportuj sys
        jeżeli sys.maxsize <= 2147483647:
            x = self.type2test([0])
            x *= 2**16
            self.assertRaises(MemoryError, x.__mul__, 2**16)
            jeżeli hasattr(x, '__imul__'):
                self.assertRaises(MemoryError, x.__imul__, 2**16)

    def test_subscript(self):
        a = self.type2test([10, 11])
        self.assertEqual(a.__getitem__(0), 10)
        self.assertEqual(a.__getitem__(1), 11)
        self.assertEqual(a.__getitem__(-2), 10)
        self.assertEqual(a.__getitem__(-1), 11)
        self.assertRaises(IndexError, a.__getitem__, -3)
        self.assertRaises(IndexError, a.__getitem__, 3)
        self.assertEqual(a.__getitem__(slice(0,1)), self.type2test([10]))
        self.assertEqual(a.__getitem__(slice(1,2)), self.type2test([11]))
        self.assertEqual(a.__getitem__(slice(0,2)), self.type2test([10, 11]))
        self.assertEqual(a.__getitem__(slice(0,3)), self.type2test([10, 11]))
        self.assertEqual(a.__getitem__(slice(3,5)), self.type2test([]))
        self.assertRaises(ValueError, a.__getitem__, slice(0, 10, 0))
        self.assertRaises(TypeError, a.__getitem__, 'x')

    def test_count(self):
        a = self.type2test([0, 1, 2])*3
        self.assertEqual(a.count(0), 3)
        self.assertEqual(a.count(1), 3)
        self.assertEqual(a.count(3), 0)

        self.assertRaises(TypeError, a.count)

        klasa BadExc(Exception):
            dalej

        klasa BadCmp:
            def __eq__(self, other):
                jeżeli other == 2:
                    podnieś BadExc()
                zwróć Nieprawda

        self.assertRaises(BadExc, a.count, BadCmp())

    def test_index(self):
        u = self.type2test([0, 1])
        self.assertEqual(u.index(0), 0)
        self.assertEqual(u.index(1), 1)
        self.assertRaises(ValueError, u.index, 2)

        u = self.type2test([-2, -1, 0, 0, 1, 2])
        self.assertEqual(u.count(0), 2)
        self.assertEqual(u.index(0), 2)
        self.assertEqual(u.index(0, 2), 2)
        self.assertEqual(u.index(-2, -10), 0)
        self.assertEqual(u.index(0, 3), 3)
        self.assertEqual(u.index(0, 3, 4), 3)
        self.assertRaises(ValueError, u.index, 2, 0, -10)

        self.assertRaises(TypeError, u.index)

        klasa BadExc(Exception):
            dalej

        klasa BadCmp:
            def __eq__(self, other):
                jeżeli other == 2:
                    podnieś BadExc()
                zwróć Nieprawda

        a = self.type2test([0, 1, 2, 3])
        self.assertRaises(BadExc, a.index, BadCmp())

        a = self.type2test([-2, -1, 0, 0, 1, 2])
        self.assertEqual(a.index(0), 2)
        self.assertEqual(a.index(0, 2), 2)
        self.assertEqual(a.index(0, -4), 2)
        self.assertEqual(a.index(-2, -10), 0)
        self.assertEqual(a.index(0, 3), 3)
        self.assertEqual(a.index(0, -3), 3)
        self.assertEqual(a.index(0, 3, 4), 3)
        self.assertEqual(a.index(0, -3, -2), 3)
        self.assertEqual(a.index(0, -4*sys.maxsize, 4*sys.maxsize), 2)
        self.assertRaises(ValueError, a.index, 0, 4*sys.maxsize,-4*sys.maxsize)
        self.assertRaises(ValueError, a.index, 2, 0, -10)

    def test_pickle(self):
        lst = self.type2test([4, 5, 6, 7])
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            lst2 = pickle.loads(pickle.dumps(lst, proto))
            self.assertEqual(lst2, lst)
            self.assertNotEqual(id(lst2), id(lst))
