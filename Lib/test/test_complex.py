zaimportuj unittest
z test zaimportuj support

z random zaimportuj random
z math zaimportuj atan2, isnan, copysign
zaimportuj operator

INF = float("inf")
NAN = float("nan")
# These tests ensure that complex math does the right thing

klasa ComplexTest(unittest.TestCase):

    def assertAlmostEqual(self, a, b):
        jeżeli isinstance(a, complex):
            jeżeli isinstance(b, complex):
                unittest.TestCase.assertAlmostEqual(self, a.real, b.real)
                unittest.TestCase.assertAlmostEqual(self, a.imag, b.imag)
            inaczej:
                unittest.TestCase.assertAlmostEqual(self, a.real, b)
                unittest.TestCase.assertAlmostEqual(self, a.imag, 0.)
        inaczej:
            jeżeli isinstance(b, complex):
                unittest.TestCase.assertAlmostEqual(self, a, b.real)
                unittest.TestCase.assertAlmostEqual(self, 0., b.imag)
            inaczej:
                unittest.TestCase.assertAlmostEqual(self, a, b)

    def assertCloseAbs(self, x, y, eps=1e-9):
        """Return true iff floats x oraz y "are close"."""
        # put the one przy larger magnitude second
        jeżeli abs(x) > abs(y):
            x, y = y, x
        jeżeli y == 0:
            zwróć abs(x) < eps
        jeżeli x == 0:
            zwróć abs(y) < eps
        # check that relative difference < eps
        self.assertPrawda(abs((x-y)/y) < eps)

    def assertFloatsAreIdentical(self, x, y):
        """assert that floats x oraz y are identical, w the sense that:
        (1) both x oraz y are nans, albo
        (2) both x oraz y are infinities, przy the same sign, albo
        (3) both x oraz y are zeros, przy the same sign, albo
        (4) x oraz y are both finite oraz nonzero, oraz x == y

        """
        msg = 'floats {!r} oraz {!r} are nie identical'

        jeżeli isnan(x) albo isnan(y):
            jeżeli isnan(x) oraz isnan(y):
                zwróć
        albo_inaczej x == y:
            jeżeli x != 0.0:
                zwróć
            # both zero; check that signs match
            albo_inaczej copysign(1.0, x) == copysign(1.0, y):
                zwróć
            inaczej:
                msg += ': zeros have different signs'
        self.fail(msg.format(x, y))

    def assertClose(self, x, y, eps=1e-9):
        """Return true iff complexes x oraz y "are close"."""
        self.assertCloseAbs(x.real, y.real, eps)
        self.assertCloseAbs(x.imag, y.imag, eps)

    def check_div(self, x, y):
        """Compute complex z=x*y, oraz check that z/x==y oraz z/y==x."""
        z = x * y
        jeżeli x != 0:
            q = z / x
            self.assertClose(q, y)
            q = z.__truediv__(x)
            self.assertClose(q, y)
        jeżeli y != 0:
            q = z / y
            self.assertClose(q, x)
            q = z.__truediv__(y)
            self.assertClose(q, x)

    def test_truediv(self):
        simple_real = [float(i) dla i w range(-5, 6)]
        simple_complex = [complex(x, y) dla x w simple_real dla y w simple_real]
        dla x w simple_complex:
            dla y w simple_complex:
                self.check_div(x, y)

        # A naive complex division algorithm (such jako w 2.0) jest very prone to
        # nonsense errors dla these (overflows oraz underflows).
        self.check_div(complex(1e200, 1e200), 1+0j)
        self.check_div(complex(1e-200, 1e-200), 1+0j)

        # Just dla fun.
        dla i w range(100):
            self.check_div(complex(random(), random()),
                           complex(random(), random()))

        self.assertRaises(ZeroDivisionError, complex.__truediv__, 1+1j, 0+0j)
        # FIXME: The following currently crashes on Alpha
        # self.assertRaises(OverflowError, pow, 1e200+1j, 1e200+1j)

        self.assertAlmostEqual(complex.__truediv__(2+0j, 1+1j), 1-1j)
        self.assertRaises(ZeroDivisionError, complex.__truediv__, 1+1j, 0+0j)

        dla denom_real, denom_imag w [(0, NAN), (NAN, 0), (NAN, NAN)]:
            z = complex(0, 0) / complex(denom_real, denom_imag)
            self.assertPrawda(isnan(z.real))
            self.assertPrawda(isnan(z.imag))

    def test_floordiv(self):
        self.assertRaises(TypeError, complex.__floordiv__, 3+0j, 1.5+0j)
        self.assertRaises(TypeError, complex.__floordiv__, 3+0j, 0+0j)

    def test_richcompare(self):
        self.assertIs(complex.__eq__(1+1j, 1<<10000), Nieprawda)
        self.assertIs(complex.__lt__(1+1j, Nic), NotImplemented)
        self.assertIs(complex.__eq__(1+1j, 1+1j), Prawda)
        self.assertIs(complex.__eq__(1+1j, 2+2j), Nieprawda)
        self.assertIs(complex.__ne__(1+1j, 1+1j), Nieprawda)
        self.assertIs(complex.__ne__(1+1j, 2+2j), Prawda)
        dla i w range(1, 100):
            f = i / 100.0
            self.assertIs(complex.__eq__(f+0j, f), Prawda)
            self.assertIs(complex.__ne__(f+0j, f), Nieprawda)
            self.assertIs(complex.__eq__(complex(f, f), f), Nieprawda)
            self.assertIs(complex.__ne__(complex(f, f), f), Prawda)
        self.assertIs(complex.__lt__(1+1j, 2+2j), NotImplemented)
        self.assertIs(complex.__le__(1+1j, 2+2j), NotImplemented)
        self.assertIs(complex.__gt__(1+1j, 2+2j), NotImplemented)
        self.assertIs(complex.__ge__(1+1j, 2+2j), NotImplemented)
        self.assertRaises(TypeError, operator.lt, 1+1j, 2+2j)
        self.assertRaises(TypeError, operator.le, 1+1j, 2+2j)
        self.assertRaises(TypeError, operator.gt, 1+1j, 2+2j)
        self.assertRaises(TypeError, operator.ge, 1+1j, 2+2j)
        self.assertIs(operator.eq(1+1j, 1+1j), Prawda)
        self.assertIs(operator.eq(1+1j, 2+2j), Nieprawda)
        self.assertIs(operator.ne(1+1j, 1+1j), Nieprawda)
        self.assertIs(operator.ne(1+1j, 2+2j), Prawda)

    def test_richcompare_boundaries(self):
        def check(n, deltas, is_equal, imag = 0.0):
            dla delta w deltas:
                i = n + delta
                z = complex(i, imag)
                self.assertIs(complex.__eq__(z, i), is_equal(delta))
                self.assertIs(complex.__ne__(z, i), nie is_equal(delta))
        # For IEEE-754 doubles the following should hold:
        #    x w [2 ** (52 + i), 2 ** (53 + i + 1)] -> x mod 2 ** i == 0
        # where the interval jest representable, of course.
        dla i w range(1, 10):
            pow = 52 + i
            mult = 2 ** i
            check(2 ** pow, range(1, 101), lambda delta: delta % mult == 0)
            check(2 ** pow, range(1, 101), lambda delta: Nieprawda, float(i))
        check(2 ** 53, range(-100, 0), lambda delta: Prawda)

    def test_mod(self):
        # % jest no longer supported on complex numbers
        self.assertRaises(TypeError, (1+1j).__mod__, 0+0j)
        self.assertRaises(TypeError, lambda: (3.33+4.43j) % 0)
        self.assertRaises(TypeError, (1+1j).__mod__, 4.3j)

    def test_divmod(self):
        self.assertRaises(TypeError, divmod, 1+1j, 1+0j)
        self.assertRaises(TypeError, divmod, 1+1j, 0+0j)

    def test_pow(self):
        self.assertAlmostEqual(pow(1+1j, 0+0j), 1.0)
        self.assertAlmostEqual(pow(0+0j, 2+0j), 0.0)
        self.assertRaises(ZeroDivisionError, pow, 0+0j, 1j)
        self.assertAlmostEqual(pow(1j, -1), 1/1j)
        self.assertAlmostEqual(pow(1j, 200), 1)
        self.assertRaises(ValueError, pow, 1+1j, 1+1j, 1+1j)

        a = 3.33+4.43j
        self.assertEqual(a ** 0j, 1)
        self.assertEqual(a ** 0.+0.j, 1)

        self.assertEqual(3j ** 0j, 1)
        self.assertEqual(3j ** 0, 1)

        spróbuj:
            0j ** a
        wyjąwszy ZeroDivisionError:
            dalej
        inaczej:
            self.fail("should fail 0.0 to negative albo complex power")

        spróbuj:
            0j ** (3-2j)
        wyjąwszy ZeroDivisionError:
            dalej
        inaczej:
            self.fail("should fail 0.0 to negative albo complex power")

        # The following jest used to exercise certain code paths
        self.assertEqual(a ** 105, a ** 105)
        self.assertEqual(a ** -105, a ** -105)
        self.assertEqual(a ** -30, a ** -30)

        self.assertEqual(0.0j ** 0, 1)

        b = 5.1+2.3j
        self.assertRaises(ValueError, pow, a, b, 0)

    def test_boolcontext(self):
        dla i w range(100):
            self.assertPrawda(complex(random() + 1e-6, random() + 1e-6))
        self.assertPrawda(nie complex(0.0, 0.0))

    def test_conjugate(self):
        self.assertClose(complex(5.3, 9.8).conjugate(), 5.3-9.8j)

    def test_constructor(self):
        klasa OS:
            def __init__(self, value): self.value = value
            def __complex__(self): zwróć self.value
        klasa NS(object):
            def __init__(self, value): self.value = value
            def __complex__(self): zwróć self.value
        self.assertEqual(complex(OS(1+10j)), 1+10j)
        self.assertEqual(complex(NS(1+10j)), 1+10j)
        self.assertRaises(TypeError, complex, OS(Nic))
        self.assertRaises(TypeError, complex, NS(Nic))
        self.assertRaises(TypeError, complex, {})
        self.assertRaises(TypeError, complex, NS(1.5))
        self.assertRaises(TypeError, complex, NS(1))

        self.assertAlmostEqual(complex("1+10j"), 1+10j)
        self.assertAlmostEqual(complex(10), 10+0j)
        self.assertAlmostEqual(complex(10.0), 10+0j)
        self.assertAlmostEqual(complex(10), 10+0j)
        self.assertAlmostEqual(complex(10+0j), 10+0j)
        self.assertAlmostEqual(complex(1,10), 1+10j)
        self.assertAlmostEqual(complex(1,10), 1+10j)
        self.assertAlmostEqual(complex(1,10.0), 1+10j)
        self.assertAlmostEqual(complex(1,10), 1+10j)
        self.assertAlmostEqual(complex(1,10), 1+10j)
        self.assertAlmostEqual(complex(1,10.0), 1+10j)
        self.assertAlmostEqual(complex(1.0,10), 1+10j)
        self.assertAlmostEqual(complex(1.0,10), 1+10j)
        self.assertAlmostEqual(complex(1.0,10.0), 1+10j)
        self.assertAlmostEqual(complex(3.14+0j), 3.14+0j)
        self.assertAlmostEqual(complex(3.14), 3.14+0j)
        self.assertAlmostEqual(complex(314), 314.0+0j)
        self.assertAlmostEqual(complex(314), 314.0+0j)
        self.assertAlmostEqual(complex(3.14+0j, 0j), 3.14+0j)
        self.assertAlmostEqual(complex(3.14, 0.0), 3.14+0j)
        self.assertAlmostEqual(complex(314, 0), 314.0+0j)
        self.assertAlmostEqual(complex(314, 0), 314.0+0j)
        self.assertAlmostEqual(complex(0j, 3.14j), -3.14+0j)
        self.assertAlmostEqual(complex(0.0, 3.14j), -3.14+0j)
        self.assertAlmostEqual(complex(0j, 3.14), 3.14j)
        self.assertAlmostEqual(complex(0.0, 3.14), 3.14j)
        self.assertAlmostEqual(complex("1"), 1+0j)
        self.assertAlmostEqual(complex("1j"), 1j)
        self.assertAlmostEqual(complex(),  0)
        self.assertAlmostEqual(complex("-1"), -1)
        self.assertAlmostEqual(complex("+1"), +1)
        self.assertAlmostEqual(complex("(1+2j)"), 1+2j)
        self.assertAlmostEqual(complex("(1.3+2.2j)"), 1.3+2.2j)
        self.assertAlmostEqual(complex("3.14+1J"), 3.14+1j)
        self.assertAlmostEqual(complex(" ( +3.14-6J )"), 3.14-6j)
        self.assertAlmostEqual(complex(" ( +3.14-J )"), 3.14-1j)
        self.assertAlmostEqual(complex(" ( +3.14+j )"), 3.14+1j)
        self.assertAlmostEqual(complex("J"), 1j)
        self.assertAlmostEqual(complex("( j )"), 1j)
        self.assertAlmostEqual(complex("+J"), 1j)
        self.assertAlmostEqual(complex("( -j)"), -1j)
        self.assertAlmostEqual(complex('1e-500'), 0.0 + 0.0j)
        self.assertAlmostEqual(complex('-1e-500j'), 0.0 - 0.0j)
        self.assertAlmostEqual(complex('-1e-500+1e-500j'), -0.0 + 0.0j)

        klasa complex2(complex): dalej
        self.assertAlmostEqual(complex(complex2(1+1j)), 1+1j)
        self.assertAlmostEqual(complex(real=17, imag=23), 17+23j)
        self.assertAlmostEqual(complex(real=17+23j), 17+23j)
        self.assertAlmostEqual(complex(real=17+23j, imag=23), 17+46j)
        self.assertAlmostEqual(complex(real=1+2j, imag=3+4j), -3+5j)

        # check that the sign of a zero w the real albo imaginary part
        # jest preserved when constructing z two floats.  (These checks
        # are harmless on systems without support dla signed zeros.)
        def split_zeros(x):
            """Function that produces different results dla 0. oraz -0."""
            zwróć atan2(x, -1.)

        self.assertEqual(split_zeros(complex(1., 0.).imag), split_zeros(0.))
        self.assertEqual(split_zeros(complex(1., -0.).imag), split_zeros(-0.))
        self.assertEqual(split_zeros(complex(0., 1.).real), split_zeros(0.))
        self.assertEqual(split_zeros(complex(-0., 1.).real), split_zeros(-0.))

        c = 3.14 + 1j
        self.assertPrawda(complex(c) jest c)
        usuń c

        self.assertRaises(TypeError, complex, "1", "1")
        self.assertRaises(TypeError, complex, 1, "1")

        # SF bug 543840:  complex(string) accepts strings przy \0
        # Fixed w 2.3.
        self.assertRaises(ValueError, complex, '1+1j\0j')

        self.assertRaises(TypeError, int, 5+3j)
        self.assertRaises(TypeError, int, 5+3j)
        self.assertRaises(TypeError, float, 5+3j)
        self.assertRaises(ValueError, complex, "")
        self.assertRaises(TypeError, complex, Nic)
        self.assertRaisesRegex(TypeError, "not 'NicType'", complex, Nic)
        self.assertRaises(ValueError, complex, "\0")
        self.assertRaises(ValueError, complex, "3\09")
        self.assertRaises(TypeError, complex, "1", "2")
        self.assertRaises(TypeError, complex, "1", 42)
        self.assertRaises(TypeError, complex, 1, "2")
        self.assertRaises(ValueError, complex, "1+")
        self.assertRaises(ValueError, complex, "1+1j+1j")
        self.assertRaises(ValueError, complex, "--")
        self.assertRaises(ValueError, complex, "(1+2j")
        self.assertRaises(ValueError, complex, "1+2j)")
        self.assertRaises(ValueError, complex, "1+(2j)")
        self.assertRaises(ValueError, complex, "(1+2j)123")
        self.assertRaises(ValueError, complex, "x")
        self.assertRaises(ValueError, complex, "1j+2")
        self.assertRaises(ValueError, complex, "1e1ej")
        self.assertRaises(ValueError, complex, "1e++1ej")
        self.assertRaises(ValueError, complex, ")1+2j(")
        # the following three are accepted by Python 2.6
        self.assertRaises(ValueError, complex, "1..1j")
        self.assertRaises(ValueError, complex, "1.11.1j")
        self.assertRaises(ValueError, complex, "1e1.1j")

        # check that complex accepts long unicode strings
        self.assertEqual(type(complex("1"*500)), complex)
        # check whitespace processing
        self.assertEqual(complex('\N{EM SPACE}(\N{EN SPACE}1+1j ) '), 1+1j)

        klasa EvilExc(Exception):
            dalej

        klasa evilcomplex:
            def __complex__(self):
                podnieś EvilExc

        self.assertRaises(EvilExc, complex, evilcomplex())

        klasa float2:
            def __init__(self, value):
                self.value = value
            def __float__(self):
                zwróć self.value

        self.assertAlmostEqual(complex(float2(42.)), 42)
        self.assertAlmostEqual(complex(real=float2(17.), imag=float2(23.)), 17+23j)
        self.assertRaises(TypeError, complex, float2(Nic))

        klasa complex0(complex):
            """Test usage of __complex__() when inheriting z 'complex'"""
            def __complex__(self):
                zwróć 42j

        klasa complex1(complex):
            """Test usage of __complex__() przy a __new__() method"""
            def __new__(self, value=0j):
                zwróć complex.__new__(self, 2*value)
            def __complex__(self):
                zwróć self

        klasa complex2(complex):
            """Make sure that __complex__() calls fail jeżeli anything other than a
            complex jest returned"""
            def __complex__(self):
                zwróć Nic

        self.assertAlmostEqual(complex(complex0(1j)), 42j)
        self.assertAlmostEqual(complex(complex1(1j)), 2j)
        self.assertRaises(TypeError, complex, complex2(1j))

    def test_hash(self):
        dla x w range(-30, 30):
            self.assertEqual(hash(x), hash(complex(x, 0)))
            x /= 3.0    # now check against floating point
            self.assertEqual(hash(x), hash(complex(x, 0.)))

    def test_abs(self):
        nums = [complex(x/3., y/7.) dla x w range(-9,9) dla y w range(-9,9)]
        dla num w nums:
            self.assertAlmostEqual((num.real**2 + num.imag**2)  ** 0.5, abs(num))

    def test_repr_str(self):
        def test(v, expected, test_fn=self.assertEqual):
            test_fn(repr(v), expected)
            test_fn(str(v), expected)

        test(1+6j, '(1+6j)')
        test(1-6j, '(1-6j)')

        test(-(1+0j), '(-1+-0j)', test_fn=self.assertNotEqual)

        test(complex(1., INF), "(1+infj)")
        test(complex(1., -INF), "(1-infj)")
        test(complex(INF, 1), "(inf+1j)")
        test(complex(-INF, INF), "(-inf+infj)")
        test(complex(NAN, 1), "(nan+1j)")
        test(complex(1, NAN), "(1+nanj)")
        test(complex(NAN, NAN), "(nan+nanj)")

        test(complex(0, INF), "infj")
        test(complex(0, -INF), "-infj")
        test(complex(0, NAN), "nanj")

        self.assertEqual(1-6j,complex(repr(1-6j)))
        self.assertEqual(1+6j,complex(repr(1+6j)))
        self.assertEqual(-6j,complex(repr(-6j)))
        self.assertEqual(6j,complex(repr(6j)))

    @support.requires_IEEE_754
    def test_negative_zero_repr_str(self):
        def test(v, expected, test_fn=self.assertEqual):
            test_fn(repr(v), expected)
            test_fn(str(v), expected)

        test(complex(0., 1.),   "1j")
        test(complex(-0., 1.),  "(-0+1j)")
        test(complex(0., -1.),  "-1j")
        test(complex(-0., -1.), "(-0-1j)")

        test(complex(0., 0.),   "0j")
        test(complex(0., -0.),  "-0j")
        test(complex(-0., 0.),  "(-0+0j)")
        test(complex(-0., -0.), "(-0-0j)")

    def test_neg(self):
        self.assertEqual(-(1+6j), -1-6j)

    def test_file(self):
        a = 3.33+4.43j
        b = 5.1+2.3j

        fo = Nic
        spróbuj:
            fo = open(support.TESTFN, "w")
            print(a, b, file=fo)
            fo.close()
            fo = open(support.TESTFN, "r")
            self.assertEqual(fo.read(), ("%s %s\n" % (a, b)))
        w_końcu:
            jeżeli (fo jest nie Nic) oraz (nie fo.closed):
                fo.close()
            support.unlink(support.TESTFN)

    def test_getnewargs(self):
        self.assertEqual((1+2j).__getnewargs__(), (1.0, 2.0))
        self.assertEqual((1-2j).__getnewargs__(), (1.0, -2.0))
        self.assertEqual((2j).__getnewargs__(), (0.0, 2.0))
        self.assertEqual((-0j).__getnewargs__(), (0.0, -0.0))
        self.assertEqual(complex(0, INF).__getnewargs__(), (0.0, INF))
        self.assertEqual(complex(INF, 0).__getnewargs__(), (INF, 0.0))

    @support.requires_IEEE_754
    def test_plus_minus_0j(self):
        # test that -0j oraz 0j literals are nie identified
        z1, z2 = 0j, -0j
        self.assertEqual(atan2(z1.imag, -1.), atan2(0., -1.))
        self.assertEqual(atan2(z2.imag, -1.), atan2(-0., -1.))

    @support.requires_IEEE_754
    def test_negated_imaginary_literal(self):
        z0 = -0j
        z1 = -7j
        z2 = -1e1000j
        # Note: In versions of Python < 3.2, a negated imaginary literal
        # accidentally ended up przy real part 0.0 instead of -0.0, thanks to a
        # modification during CST -> AST translation (see issue #9011).  That's
        # fixed w Python 3.2.
        self.assertFloatsAreIdentical(z0.real, -0.0)
        self.assertFloatsAreIdentical(z0.imag, -0.0)
        self.assertFloatsAreIdentical(z1.real, -0.0)
        self.assertFloatsAreIdentical(z1.imag, -7.0)
        self.assertFloatsAreIdentical(z2.real, -0.0)
        self.assertFloatsAreIdentical(z2.imag, -INF)

    @support.requires_IEEE_754
    def test_overflow(self):
        self.assertEqual(complex("1e500"), complex(INF, 0.0))
        self.assertEqual(complex("-1e500j"), complex(0.0, -INF))
        self.assertEqual(complex("-1e500+1.8e308j"), complex(-INF, INF))

    @support.requires_IEEE_754
    def test_repr_roundtrip(self):
        vals = [0.0, 1e-500, 1e-315, 1e-200, 0.0123, 3.1415, 1e50, INF, NAN]
        vals += [-v dla v w vals]

        # complex(repr(z)) should recover z exactly, even dla complex
        # numbers involving an infinity, nan, albo negative zero
        dla x w vals:
            dla y w vals:
                z = complex(x, y)
                roundtrip = complex(repr(z))
                self.assertFloatsAreIdentical(z.real, roundtrip.real)
                self.assertFloatsAreIdentical(z.imag, roundtrip.imag)

        # jeżeli we predefine some constants, then eval(repr(z)) should
        # also work, wyjąwszy that it might change the sign of zeros
        inf, nan = float('inf'), float('nan')
        infj, nanj = complex(0.0, inf), complex(0.0, nan)
        dla x w vals:
            dla y w vals:
                z = complex(x, y)
                roundtrip = eval(repr(z))
                # adding 0.0 has no effect beside changing -0.0 to 0.0
                self.assertFloatsAreIdentical(0.0 + z.real,
                                              0.0 + roundtrip.real)
                self.assertFloatsAreIdentical(0.0 + z.imag,
                                              0.0 + roundtrip.imag)

    def test_format(self):
        # empty format string jest same jako str()
        self.assertEqual(format(1+3j, ''), str(1+3j))
        self.assertEqual(format(1.5+3.5j, ''), str(1.5+3.5j))
        self.assertEqual(format(3j, ''), str(3j))
        self.assertEqual(format(3.2j, ''), str(3.2j))
        self.assertEqual(format(3+0j, ''), str(3+0j))
        self.assertEqual(format(3.2+0j, ''), str(3.2+0j))

        # empty presentation type should still be analogous to str,
        # even when format string jest nonempty (issue #5920).
        self.assertEqual(format(3.2+0j, '-'), str(3.2+0j))
        self.assertEqual(format(3.2+0j, '<'), str(3.2+0j))
        z = 4/7. - 100j/7.
        self.assertEqual(format(z, ''), str(z))
        self.assertEqual(format(z, '-'), str(z))
        self.assertEqual(format(z, '<'), str(z))
        self.assertEqual(format(z, '10'), str(z))
        z = complex(0.0, 3.0)
        self.assertEqual(format(z, ''), str(z))
        self.assertEqual(format(z, '-'), str(z))
        self.assertEqual(format(z, '<'), str(z))
        self.assertEqual(format(z, '2'), str(z))
        z = complex(-0.0, 2.0)
        self.assertEqual(format(z, ''), str(z))
        self.assertEqual(format(z, '-'), str(z))
        self.assertEqual(format(z, '<'), str(z))
        self.assertEqual(format(z, '3'), str(z))

        self.assertEqual(format(1+3j, 'g'), '1+3j')
        self.assertEqual(format(3j, 'g'), '0+3j')
        self.assertEqual(format(1.5+3.5j, 'g'), '1.5+3.5j')

        self.assertEqual(format(1.5+3.5j, '+g'), '+1.5+3.5j')
        self.assertEqual(format(1.5-3.5j, '+g'), '+1.5-3.5j')
        self.assertEqual(format(1.5-3.5j, '-g'), '1.5-3.5j')
        self.assertEqual(format(1.5+3.5j, ' g'), ' 1.5+3.5j')
        self.assertEqual(format(1.5-3.5j, ' g'), ' 1.5-3.5j')
        self.assertEqual(format(-1.5+3.5j, ' g'), '-1.5+3.5j')
        self.assertEqual(format(-1.5-3.5j, ' g'), '-1.5-3.5j')

        self.assertEqual(format(-1.5-3.5e-20j, 'g'), '-1.5-3.5e-20j')
        self.assertEqual(format(-1.5-3.5j, 'f'), '-1.500000-3.500000j')
        self.assertEqual(format(-1.5-3.5j, 'F'), '-1.500000-3.500000j')
        self.assertEqual(format(-1.5-3.5j, 'e'), '-1.500000e+00-3.500000e+00j')
        self.assertEqual(format(-1.5-3.5j, '.2e'), '-1.50e+00-3.50e+00j')
        self.assertEqual(format(-1.5-3.5j, '.2E'), '-1.50E+00-3.50E+00j')
        self.assertEqual(format(-1.5e10-3.5e5j, '.2G'), '-1.5E+10-3.5E+05j')

        self.assertEqual(format(1.5+3j, '<20g'),  '1.5+3j              ')
        self.assertEqual(format(1.5+3j, '*<20g'), '1.5+3j**************')
        self.assertEqual(format(1.5+3j, '>20g'),  '              1.5+3j')
        self.assertEqual(format(1.5+3j, '^20g'),  '       1.5+3j       ')
        self.assertEqual(format(1.5+3j, '<20'),   '(1.5+3j)            ')
        self.assertEqual(format(1.5+3j, '>20'),   '            (1.5+3j)')
        self.assertEqual(format(1.5+3j, '^20'),   '      (1.5+3j)      ')
        self.assertEqual(format(1.123-3.123j, '^20.2'), '     (1.1-3.1j)     ')

        self.assertEqual(format(1.5+3j, '20.2f'), '          1.50+3.00j')
        self.assertEqual(format(1.5+3j, '>20.2f'), '          1.50+3.00j')
        self.assertEqual(format(1.5+3j, '<20.2f'), '1.50+3.00j          ')
        self.assertEqual(format(1.5e20+3j, '<20.2f'), '150000000000000000000.00+3.00j')
        self.assertEqual(format(1.5e20+3j, '>40.2f'), '          150000000000000000000.00+3.00j')
        self.assertEqual(format(1.5e20+3j, '^40,.2f'), '  150,000,000,000,000,000,000.00+3.00j  ')
        self.assertEqual(format(1.5e21+3j, '^40,.2f'), ' 1,500,000,000,000,000,000,000.00+3.00j ')
        self.assertEqual(format(1.5e21+3000j, ',.2f'), '1,500,000,000,000,000,000,000.00+3,000.00j')

        # Issue 7094: Alternate formatting (specified by #)
        self.assertEqual(format(1+1j, '.0e'), '1e+00+1e+00j')
        self.assertEqual(format(1+1j, '#.0e'), '1.e+00+1.e+00j')
        self.assertEqual(format(1+1j, '.0f'), '1+1j')
        self.assertEqual(format(1+1j, '#.0f'), '1.+1.j')
        self.assertEqual(format(1.1+1.1j, 'g'), '1.1+1.1j')
        self.assertEqual(format(1.1+1.1j, '#g'), '1.10000+1.10000j')

        # Alternate doesn't make a difference dla these, they format the same przy albo without it
        self.assertEqual(format(1+1j, '.1e'),  '1.0e+00+1.0e+00j')
        self.assertEqual(format(1+1j, '#.1e'), '1.0e+00+1.0e+00j')
        self.assertEqual(format(1+1j, '.1f'),  '1.0+1.0j')
        self.assertEqual(format(1+1j, '#.1f'), '1.0+1.0j')

        # Misc. other alternate tests
        self.assertEqual(format((-1.5+0.5j), '#f'), '-1.500000+0.500000j')
        self.assertEqual(format((-1.5+0.5j), '#.0f'), '-2.+0.j')
        self.assertEqual(format((-1.5+0.5j), '#e'), '-1.500000e+00+5.000000e-01j')
        self.assertEqual(format((-1.5+0.5j), '#.0e'), '-2.e+00+5.e-01j')
        self.assertEqual(format((-1.5+0.5j), '#g'), '-1.50000+0.500000j')
        self.assertEqual(format((-1.5+0.5j), '.0g'), '-2+0.5j')
        self.assertEqual(format((-1.5+0.5j), '#.0g'), '-2.+0.5j')

        # zero padding jest invalid
        self.assertRaises(ValueError, (1.5+0.5j).__format__, '010f')

        # '=' alignment jest invalid
        self.assertRaises(ValueError, (1.5+3j).__format__, '=20')

        # integer presentation types are an error
        dla t w 'bcdoxX':
            self.assertRaises(ValueError, (1.5+0.5j).__format__, t)

        # make sure everything works w ''.format()
        self.assertEqual('*{0:.3f}*'.format(3.14159+2.71828j), '*3.142+2.718j*')

        # issue 3382
        self.assertEqual(format(complex(NAN, NAN), 'f'), 'nan+nanj')
        self.assertEqual(format(complex(1, NAN), 'f'), '1.000000+nanj')
        self.assertEqual(format(complex(NAN, 1), 'f'), 'nan+1.000000j')
        self.assertEqual(format(complex(NAN, -1), 'f'), 'nan-1.000000j')
        self.assertEqual(format(complex(NAN, NAN), 'F'), 'NAN+NANj')
        self.assertEqual(format(complex(1, NAN), 'F'), '1.000000+NANj')
        self.assertEqual(format(complex(NAN, 1), 'F'), 'NAN+1.000000j')
        self.assertEqual(format(complex(NAN, -1), 'F'), 'NAN-1.000000j')
        self.assertEqual(format(complex(INF, INF), 'f'), 'inf+infj')
        self.assertEqual(format(complex(1, INF), 'f'), '1.000000+infj')
        self.assertEqual(format(complex(INF, 1), 'f'), 'inf+1.000000j')
        self.assertEqual(format(complex(INF, -1), 'f'), 'inf-1.000000j')
        self.assertEqual(format(complex(INF, INF), 'F'), 'INF+INFj')
        self.assertEqual(format(complex(1, INF), 'F'), '1.000000+INFj')
        self.assertEqual(format(complex(INF, 1), 'F'), 'INF+1.000000j')
        self.assertEqual(format(complex(INF, -1), 'F'), 'INF-1.000000j')

def test_main():
    support.run_unittest(ComplexTest)

jeżeli __name__ == "__main__":
    test_main()
