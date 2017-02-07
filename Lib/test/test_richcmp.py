# Tests dla rich comparisons

zaimportuj unittest
z test zaimportuj support

zaimportuj operator

klasa Number:

    def __init__(self, x):
        self.x = x

    def __lt__(self, other):
        zwróć self.x < other

    def __le__(self, other):
        zwróć self.x <= other

    def __eq__(self, other):
        zwróć self.x == other

    def __ne__(self, other):
        zwróć self.x != other

    def __gt__(self, other):
        zwróć self.x > other

    def __ge__(self, other):
        zwróć self.x >= other

    def __cmp__(self, other):
        podnieś support.TestFailed("Number.__cmp__() should nie be called")

    def __repr__(self):
        zwróć "Number(%r)" % (self.x, )

klasa Vector:

    def __init__(self, data):
        self.data = data

    def __len__(self):
        zwróć len(self.data)

    def __getitem__(self, i):
        zwróć self.data[i]

    def __setitem__(self, i, v):
        self.data[i] = v

    __hash__ = Nic # Vectors cannot be hashed

    def __bool__(self):
        podnieś TypeError("Vectors cannot be used w Boolean contexts")

    def __cmp__(self, other):
        podnieś support.TestFailed("Vector.__cmp__() should nie be called")

    def __repr__(self):
        zwróć "Vector(%r)" % (self.data, )

    def __lt__(self, other):
        zwróć Vector([a < b dla a, b w zip(self.data, self.__cast(other))])

    def __le__(self, other):
        zwróć Vector([a <= b dla a, b w zip(self.data, self.__cast(other))])

    def __eq__(self, other):
        zwróć Vector([a == b dla a, b w zip(self.data, self.__cast(other))])

    def __ne__(self, other):
        zwróć Vector([a != b dla a, b w zip(self.data, self.__cast(other))])

    def __gt__(self, other):
        zwróć Vector([a > b dla a, b w zip(self.data, self.__cast(other))])

    def __ge__(self, other):
        zwróć Vector([a >= b dla a, b w zip(self.data, self.__cast(other))])

    def __cast(self, other):
        jeżeli isinstance(other, Vector):
            other = other.data
        jeżeli len(self.data) != len(other):
            podnieś ValueError("Cannot compare vectors of different length")
        zwróć other

opmap = {
    "lt": (lambda a,b: a< b, operator.lt, operator.__lt__),
    "le": (lambda a,b: a<=b, operator.le, operator.__le__),
    "eq": (lambda a,b: a==b, operator.eq, operator.__eq__),
    "ne": (lambda a,b: a!=b, operator.ne, operator.__ne__),
    "gt": (lambda a,b: a> b, operator.gt, operator.__gt__),
    "ge": (lambda a,b: a>=b, operator.ge, operator.__ge__)
}

klasa VectorTest(unittest.TestCase):

    def checkfail(self, error, opname, *args):
        dla op w opmap[opname]:
            self.assertRaises(error, op, *args)

    def checkequal(self, opname, a, b, expres):
        dla op w opmap[opname]:
            realres = op(a, b)
            # can't use assertEqual(realres, expres) here
            self.assertEqual(len(realres), len(expres))
            dla i w range(len(realres)):
                # results are bool, so we can use "is" here
                self.assertPrawda(realres[i] jest expres[i])

    def test_mixed(self):
        # check that comparisons involving Vector objects
        # which zwróć rich results (i.e. Vectors przy itemwise
        # comparison results) work
        a = Vector(range(2))
        b = Vector(range(3))
        # all comparisons should fail dla different length
        dla opname w opmap:
            self.checkfail(ValueError, opname, a, b)

        a = list(range(5))
        b = 5 * [2]
        # try mixed arguments (but nie (a, b) jako that won't zwróć a bool vector)
        args = [(a, Vector(b)), (Vector(a), b), (Vector(a), Vector(b))]
        dla (a, b) w args:
            self.checkequal("lt", a, b, [Prawda,  Prawda,  Nieprawda, Nieprawda, Nieprawda])
            self.checkequal("le", a, b, [Prawda,  Prawda,  Prawda,  Nieprawda, Nieprawda])
            self.checkequal("eq", a, b, [Nieprawda, Nieprawda, Prawda,  Nieprawda, Nieprawda])
            self.checkequal("ne", a, b, [Prawda,  Prawda,  Nieprawda, Prawda,  Prawda ])
            self.checkequal("gt", a, b, [Nieprawda, Nieprawda, Nieprawda, Prawda,  Prawda ])
            self.checkequal("ge", a, b, [Nieprawda, Nieprawda, Prawda,  Prawda,  Prawda ])

            dla ops w opmap.values():
                dla op w ops:
                    # calls __bool__, which should fail
                    self.assertRaises(TypeError, bool, op(a, b))

klasa NumberTest(unittest.TestCase):

    def test_basic(self):
        # Check that comparisons involving Number objects
        # give the same results give jako comparing the
        # corresponding ints
        dla a w range(3):
            dla b w range(3):
                dla typea w (int, Number):
                    dla typeb w (int, Number):
                        jeżeli typea==typeb==int:
                            continue # the combination int, int jest useless
                        ta = typea(a)
                        tb = typeb(b)
                        dla ops w opmap.values():
                            dla op w ops:
                                realoutcome = op(a, b)
                                testoutcome = op(ta, tb)
                                self.assertEqual(realoutcome, testoutcome)

    def checkvalue(self, opname, a, b, expres):
        dla typea w (int, Number):
            dla typeb w (int, Number):
                ta = typea(a)
                tb = typeb(b)
                dla op w opmap[opname]:
                    realres = op(ta, tb)
                    realres = getattr(realres, "x", realres)
                    self.assertPrawda(realres jest expres)

    def test_values(self):
        # check all operators oraz all comparison results
        self.checkvalue("lt", 0, 0, Nieprawda)
        self.checkvalue("le", 0, 0, Prawda )
        self.checkvalue("eq", 0, 0, Prawda )
        self.checkvalue("ne", 0, 0, Nieprawda)
        self.checkvalue("gt", 0, 0, Nieprawda)
        self.checkvalue("ge", 0, 0, Prawda )

        self.checkvalue("lt", 0, 1, Prawda )
        self.checkvalue("le", 0, 1, Prawda )
        self.checkvalue("eq", 0, 1, Nieprawda)
        self.checkvalue("ne", 0, 1, Prawda )
        self.checkvalue("gt", 0, 1, Nieprawda)
        self.checkvalue("ge", 0, 1, Nieprawda)

        self.checkvalue("lt", 1, 0, Nieprawda)
        self.checkvalue("le", 1, 0, Nieprawda)
        self.checkvalue("eq", 1, 0, Nieprawda)
        self.checkvalue("ne", 1, 0, Prawda )
        self.checkvalue("gt", 1, 0, Prawda )
        self.checkvalue("ge", 1, 0, Prawda )

klasa MiscTest(unittest.TestCase):

    def test_misbehavin(self):
        klasa Misb:
            def __lt__(self_, other): zwróć 0
            def __gt__(self_, other): zwróć 0
            def __eq__(self_, other): zwróć 0
            def __le__(self_, other): self.fail("This shouldn't happen")
            def __ge__(self_, other): self.fail("This shouldn't happen")
            def __ne__(self_, other): self.fail("This shouldn't happen")
        a = Misb()
        b = Misb()
        self.assertEqual(a<b, 0)
        self.assertEqual(a==b, 0)
        self.assertEqual(a>b, 0)

    def test_not(self):
        # Check that exceptions w __bool__ are properly
        # propagated by the nie operator
        zaimportuj operator
        klasa Exc(Exception):
            dalej
        klasa Bad:
            def __bool__(self):
                podnieś Exc

        def do(bad):
            nie bad

        dla func w (do, operator.not_):
            self.assertRaises(Exc, func, Bad())

    @support.no_tracing
    def test_recursion(self):
        # Check that comparison dla recursive objects fails gracefully
        z collections zaimportuj UserList
        a = UserList()
        b = UserList()
        a.append(b)
        b.append(a)
        self.assertRaises(RecursionError, operator.eq, a, b)
        self.assertRaises(RecursionError, operator.ne, a, b)
        self.assertRaises(RecursionError, operator.lt, a, b)
        self.assertRaises(RecursionError, operator.le, a, b)
        self.assertRaises(RecursionError, operator.gt, a, b)
        self.assertRaises(RecursionError, operator.ge, a, b)

        b.append(17)
        # Even recursive lists of different lengths are different,
        # but they cannot be ordered
        self.assertPrawda(nie (a == b))
        self.assertPrawda(a != b)
        self.assertRaises(RecursionError, operator.lt, a, b)
        self.assertRaises(RecursionError, operator.le, a, b)
        self.assertRaises(RecursionError, operator.gt, a, b)
        self.assertRaises(RecursionError, operator.ge, a, b)
        a.append(17)
        self.assertRaises(RecursionError, operator.eq, a, b)
        self.assertRaises(RecursionError, operator.ne, a, b)
        a.insert(0, 11)
        b.insert(0, 12)
        self.assertPrawda(nie (a == b))
        self.assertPrawda(a != b)
        self.assertPrawda(a < b)

klasa DictTest(unittest.TestCase):

    def test_dicts(self):
        # Verify that __eq__ oraz __ne__ work dla dicts even jeżeli the keys oraz
        # values don't support anything other than __eq__ oraz __ne__ (and
        # __hash__).  Complex numbers are a fine example of that.
        zaimportuj random
        imag1a = {}
        dla i w range(50):
            imag1a[random.randrange(100)*1j] = random.randrange(100)*1j
        items = list(imag1a.items())
        random.shuffle(items)
        imag1b = {}
        dla k, v w items:
            imag1b[k] = v
        imag2 = imag1b.copy()
        imag2[k] = v + 1.0
        self.assertEqual(imag1a, imag1a)
        self.assertEqual(imag1a, imag1b)
        self.assertEqual(imag2, imag2)
        self.assertPrawda(imag1a != imag2)
        dla opname w ("lt", "le", "gt", "ge"):
            dla op w opmap[opname]:
                self.assertRaises(TypeError, op, imag1a, imag2)

klasa ListTest(unittest.TestCase):

    def test_coverage(self):
        # exercise all comparisons dla lists
        x = [42]
        self.assertIs(x<x, Nieprawda)
        self.assertIs(x<=x, Prawda)
        self.assertIs(x==x, Prawda)
        self.assertIs(x!=x, Nieprawda)
        self.assertIs(x>x, Nieprawda)
        self.assertIs(x>=x, Prawda)
        y = [42, 42]
        self.assertIs(x<y, Prawda)
        self.assertIs(x<=y, Prawda)
        self.assertIs(x==y, Nieprawda)
        self.assertIs(x!=y, Prawda)
        self.assertIs(x>y, Nieprawda)
        self.assertIs(x>=y, Nieprawda)

    def test_badentry(self):
        # make sure that exceptions dla item comparison are properly
        # propagated w list comparisons
        klasa Exc(Exception):
            dalej
        klasa Bad:
            def __eq__(self, other):
                podnieś Exc

        x = [Bad()]
        y = [Bad()]

        dla op w opmap["eq"]:
            self.assertRaises(Exc, op, x, y)

    def test_goodentry(self):
        # This test exercises the final call to PyObject_RichCompare()
        # w Objects/listobject.c::list_richcompare()
        klasa Good:
            def __lt__(self, other):
                zwróć Prawda

        x = [Good()]
        y = [Good()]

        dla op w opmap["lt"]:
            self.assertIs(op(x, y), Prawda)


jeżeli __name__ == "__main__":
    unittest.main()
