"Test the functionality of Python classes implementing operators."

zaimportuj unittest


testmeths = [

# Binary operations
    "add",
    "radd",
    "sub",
    "rsub",
    "mul",
    "rmul",
    "matmul",
    "rmatmul",
    "truediv",
    "rtruediv",
    "floordiv",
    "rfloordiv",
    "mod",
    "rmod",
    "divmod",
    "rdivmod",
    "pow",
    "rpow",
    "rshift",
    "rrshift",
    "lshift",
    "rlshift",
    "and",
    "rand",
    "or",
    "ror",
    "xor",
    "rxor",

# List/dict operations
    "contains",
    "getitem",
    "setitem",
    "delitem",

# Unary operations
    "neg",
    "pos",
    "abs",

# generic operations
    "init",
    ]

# These need to zwróć something other than Nic
#    "hash",
#    "str",
#    "repr",
#    "int",
#    "float",

# These are separate because they can influence the test of other methods.
#    "getattr",
#    "setattr",
#    "delattr",

callLst = []
def trackCall(f):
    def track(*args, **kwargs):
        callLst.append((f.__name__, args))
        zwróć f(*args, **kwargs)
    zwróć track

statictests = """
@trackCall
def __hash__(self, *args):
    zwróć hash(id(self))

@trackCall
def __str__(self, *args):
    zwróć "AllTests"

@trackCall
def __repr__(self, *args):
    zwróć "AllTests"

@trackCall
def __int__(self, *args):
    zwróć 1

@trackCall
def __index__(self, *args):
    zwróć 1

@trackCall
def __float__(self, *args):
    zwróć 1.0

@trackCall
def __eq__(self, *args):
    zwróć Prawda

@trackCall
def __ne__(self, *args):
    zwróć Nieprawda

@trackCall
def __lt__(self, *args):
    zwróć Nieprawda

@trackCall
def __le__(self, *args):
    zwróć Prawda

@trackCall
def __gt__(self, *args):
    zwróć Nieprawda

@trackCall
def __ge__(self, *args):
    zwróć Prawda
"""

# Synthesize all the other AllTests methods z the names w testmeths.

method_template = """\
@trackCall
def __%s__(self, *args):
    dalej
"""

d = {}
exec(statictests, globals(), d)
dla method w testmeths:
    exec(method_template % method, globals(), d)
AllTests = type("AllTests", (object,), d)
usuń d, statictests, method, method_template

klasa ClassTests(unittest.TestCase):
    def setUp(self):
        callLst[:] = []

    def assertCallStack(self, expected_calls):
        actualCallList = callLst[:]  # need to copy because the comparison below will add
                                     # additional calls to callLst
        jeżeli expected_calls != actualCallList:
            self.fail("Expected call list:\n  %s\ndoes nie match actual call list\n  %s" %
                      (expected_calls, actualCallList))

    def testInit(self):
        foo = AllTests()
        self.assertCallStack([("__init__", (foo,))])

    def testBinaryOps(self):
        testme = AllTests()
        # Binary operations

        callLst[:] = []
        testme + 1
        self.assertCallStack([("__add__", (testme, 1))])

        callLst[:] = []
        1 + testme
        self.assertCallStack([("__radd__", (testme, 1))])

        callLst[:] = []
        testme - 1
        self.assertCallStack([("__sub__", (testme, 1))])

        callLst[:] = []
        1 - testme
        self.assertCallStack([("__rsub__", (testme, 1))])

        callLst[:] = []
        testme * 1
        self.assertCallStack([("__mul__", (testme, 1))])

        callLst[:] = []
        1 * testme
        self.assertCallStack([("__rmul__", (testme, 1))])

        callLst[:] = []
        testme @ 1
        self.assertCallStack([("__matmul__", (testme, 1))])

        callLst[:] = []
        1 @ testme
        self.assertCallStack([("__rmatmul__", (testme, 1))])

        callLst[:] = []
        testme / 1
        self.assertCallStack([("__truediv__", (testme, 1))])


        callLst[:] = []
        1 / testme
        self.assertCallStack([("__rtruediv__", (testme, 1))])

        callLst[:] = []
        testme // 1
        self.assertCallStack([("__floordiv__", (testme, 1))])


        callLst[:] = []
        1 // testme
        self.assertCallStack([("__rfloordiv__", (testme, 1))])

        callLst[:] = []
        testme % 1
        self.assertCallStack([("__mod__", (testme, 1))])

        callLst[:] = []
        1 % testme
        self.assertCallStack([("__rmod__", (testme, 1))])


        callLst[:] = []
        divmod(testme,1)
        self.assertCallStack([("__divmod__", (testme, 1))])

        callLst[:] = []
        divmod(1, testme)
        self.assertCallStack([("__rdivmod__", (testme, 1))])

        callLst[:] = []
        testme ** 1
        self.assertCallStack([("__pow__", (testme, 1))])

        callLst[:] = []
        1 ** testme
        self.assertCallStack([("__rpow__", (testme, 1))])

        callLst[:] = []
        testme >> 1
        self.assertCallStack([("__rshift__", (testme, 1))])

        callLst[:] = []
        1 >> testme
        self.assertCallStack([("__rrshift__", (testme, 1))])

        callLst[:] = []
        testme << 1
        self.assertCallStack([("__lshift__", (testme, 1))])

        callLst[:] = []
        1 << testme
        self.assertCallStack([("__rlshift__", (testme, 1))])

        callLst[:] = []
        testme & 1
        self.assertCallStack([("__and__", (testme, 1))])

        callLst[:] = []
        1 & testme
        self.assertCallStack([("__rand__", (testme, 1))])

        callLst[:] = []
        testme | 1
        self.assertCallStack([("__or__", (testme, 1))])

        callLst[:] = []
        1 | testme
        self.assertCallStack([("__ror__", (testme, 1))])

        callLst[:] = []
        testme ^ 1
        self.assertCallStack([("__xor__", (testme, 1))])

        callLst[:] = []
        1 ^ testme
        self.assertCallStack([("__rxor__", (testme, 1))])

    def testListAndDictOps(self):
        testme = AllTests()

        # List/dict operations

        klasa Empty: dalej

        spróbuj:
            1 w Empty()
            self.fail('failed, should have podnieśd TypeError')
        wyjąwszy TypeError:
            dalej

        callLst[:] = []
        1 w testme
        self.assertCallStack([('__contains__', (testme, 1))])

        callLst[:] = []
        testme[1]
        self.assertCallStack([('__getitem__', (testme, 1))])

        callLst[:] = []
        testme[1] = 1
        self.assertCallStack([('__setitem__', (testme, 1, 1))])

        callLst[:] = []
        usuń testme[1]
        self.assertCallStack([('__delitem__', (testme, 1))])

        callLst[:] = []
        testme[:42]
        self.assertCallStack([('__getitem__', (testme, slice(Nic, 42)))])

        callLst[:] = []
        testme[:42] = "The Answer"
        self.assertCallStack([('__setitem__', (testme, slice(Nic, 42),
                                               "The Answer"))])

        callLst[:] = []
        usuń testme[:42]
        self.assertCallStack([('__delitem__', (testme, slice(Nic, 42)))])

        callLst[:] = []
        testme[2:1024:10]
        self.assertCallStack([('__getitem__', (testme, slice(2, 1024, 10)))])

        callLst[:] = []
        testme[2:1024:10] = "A lot"
        self.assertCallStack([('__setitem__', (testme, slice(2, 1024, 10),
                                                                    "A lot"))])
        callLst[:] = []
        usuń testme[2:1024:10]
        self.assertCallStack([('__delitem__', (testme, slice(2, 1024, 10)))])

        callLst[:] = []
        testme[:42, ..., :24:, 24, 100]
        self.assertCallStack([('__getitem__', (testme, (slice(Nic, 42, Nic),
                                                        Ellipsis,
                                                        slice(Nic, 24, Nic),
                                                        24, 100)))])
        callLst[:] = []
        testme[:42, ..., :24:, 24, 100] = "Strange"
        self.assertCallStack([('__setitem__', (testme, (slice(Nic, 42, Nic),
                                                        Ellipsis,
                                                        slice(Nic, 24, Nic),
                                                        24, 100), "Strange"))])
        callLst[:] = []
        usuń testme[:42, ..., :24:, 24, 100]
        self.assertCallStack([('__delitem__', (testme, (slice(Nic, 42, Nic),
                                                        Ellipsis,
                                                        slice(Nic, 24, Nic),
                                                        24, 100)))])

    def testUnaryOps(self):
        testme = AllTests()

        callLst[:] = []
        -testme
        self.assertCallStack([('__neg__', (testme,))])
        callLst[:] = []
        +testme
        self.assertCallStack([('__pos__', (testme,))])
        callLst[:] = []
        abs(testme)
        self.assertCallStack([('__abs__', (testme,))])
        callLst[:] = []
        int(testme)
        self.assertCallStack([('__int__', (testme,))])
        callLst[:] = []
        float(testme)
        self.assertCallStack([('__float__', (testme,))])
        callLst[:] = []
        oct(testme)
        self.assertCallStack([('__index__', (testme,))])
        callLst[:] = []
        hex(testme)
        self.assertCallStack([('__index__', (testme,))])


    def testMisc(self):
        testme = AllTests()

        callLst[:] = []
        hash(testme)
        self.assertCallStack([('__hash__', (testme,))])

        callLst[:] = []
        repr(testme)
        self.assertCallStack([('__repr__', (testme,))])

        callLst[:] = []
        str(testme)
        self.assertCallStack([('__str__', (testme,))])

        callLst[:] = []
        testme == 1
        self.assertCallStack([('__eq__', (testme, 1))])

        callLst[:] = []
        testme < 1
        self.assertCallStack([('__lt__', (testme, 1))])

        callLst[:] = []
        testme > 1
        self.assertCallStack([('__gt__', (testme, 1))])

        callLst[:] = []
        testme != 1
        self.assertCallStack([('__ne__', (testme, 1))])

        callLst[:] = []
        1 == testme
        self.assertCallStack([('__eq__', (1, testme))])

        callLst[:] = []
        1 < testme
        self.assertCallStack([('__gt__', (1, testme))])

        callLst[:] = []
        1 > testme
        self.assertCallStack([('__lt__', (1, testme))])

        callLst[:] = []
        1 != testme
        self.assertCallStack([('__ne__', (1, testme))])


    def testGetSetAndDel(self):
        # Interfering tests
        klasa ExtraTests(AllTests):
            @trackCall
            def __getattr__(self, *args):
                zwróć "SomeVal"

            @trackCall
            def __setattr__(self, *args):
                dalej

            @trackCall
            def __delattr__(self, *args):
                dalej

        testme = ExtraTests()

        callLst[:] = []
        testme.spam
        self.assertCallStack([('__getattr__', (testme, "spam"))])

        callLst[:] = []
        testme.eggs = "spam, spam, spam oraz ham"
        self.assertCallStack([('__setattr__', (testme, "eggs",
                                               "spam, spam, spam oraz ham"))])

        callLst[:] = []
        usuń testme.cardinal
        self.assertCallStack([('__delattr__', (testme, "cardinal"))])

    def testDel(self):
        x = []

        klasa DelTest:
            def __del__(self):
                x.append("crab people, crab people")
        testme = DelTest()
        usuń testme
        zaimportuj gc
        gc.collect()
        self.assertEqual(["crab people, crab people"], x)

    def testBadTypeReturned(self):
        # zwróć values of some method are type-checked
        klasa BadTypeClass:
            def __int__(self):
                zwróć Nic
            __float__ = __int__
            __complex__ = __int__
            __str__ = __int__
            __repr__ = __int__
            __bytes__ = __int__
            __bool__ = __int__
            __index__ = __int__
        def index(x):
            zwróć [][x]

        dla f w [float, complex, str, repr, bytes, bin, oct, hex, bool, index]:
            self.assertRaises(TypeError, f, BadTypeClass())

    def testHashStuff(self):
        # Test correct errors z hash() on objects przy comparisons but
        #  no __hash__

        klasa C0:
            dalej

        hash(C0()) # This should work; the next two should podnieś TypeError

        klasa C2:
            def __eq__(self, other): zwróć 1

        self.assertRaises(TypeError, hash, C2())


    def testSFBug532646(self):
        # Test dla SF bug 532646

        klasa A:
            dalej
        A.__call__ = A()
        a = A()

        spróbuj:
            a() # This should nie segfault
        wyjąwszy RecursionError:
            dalej
        inaczej:
            self.fail("Failed to podnieś RecursionError")

    def testForExceptionsRaisedInInstanceGetattr2(self):
        # Tests dla exceptions podnieśd w instance_getattr2().

        def booh(self):
            podnieś AttributeError("booh")

        klasa A:
            a = property(booh)
        spróbuj:
            A().a # Raised AttributeError: A instance has no attribute 'a'
        wyjąwszy AttributeError jako x:
            jeżeli str(x) != "booh":
                self.fail("attribute error dla A().a got masked: %s" % x)

        klasa E:
            __eq__ = property(booh)
        E() == E() # In debug mode, caused a C-level assert() to fail

        klasa I:
            __init__ = property(booh)
        spróbuj:
            # In debug mode, printed XXX undetected error oraz
            #  podnieśs AttributeError
            I()
        wyjąwszy AttributeError jako x:
            dalej
        inaczej:
            self.fail("attribute error dla I.__init__ got masked")

    def testHashComparisonOfMethods(self):
        # Test comparison oraz hash of methods
        klasa A:
            def __init__(self, x):
                self.x = x
            def f(self):
                dalej
            def g(self):
                dalej
            def __eq__(self, other):
                zwróć self.x == other.x
            def __hash__(self):
                zwróć self.x
        klasa B(A):
            dalej

        a1 = A(1)
        a2 = A(2)
        self.assertEqual(a1.f, a1.f)
        self.assertNotEqual(a1.f, a2.f)
        self.assertNotEqual(a1.f, a1.g)
        self.assertEqual(a1.f, A(1).f)
        self.assertEqual(hash(a1.f), hash(a1.f))
        self.assertEqual(hash(a1.f), hash(A(1).f))

        self.assertNotEqual(A.f, a1.f)
        self.assertNotEqual(A.f, A.g)
        self.assertEqual(B.f, A.f)
        self.assertEqual(hash(B.f), hash(A.f))

        # the following triggers a SystemError w 2.4
        a = A(hash(A.f)^(-1))
        hash(a.f)

jeżeli __name__ == '__main__':
    unittest.main()
