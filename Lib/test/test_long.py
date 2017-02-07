zaimportuj unittest
z test zaimportuj support

zaimportuj sys

zaimportuj random
zaimportuj math
zaimportuj array

# Used dla lazy formatting of failure messages
klasa Frm(object):
    def __init__(self, format, *args):
        self.format = format
        self.args = args

    def __str__(self):
        zwróć self.format % self.args

# SHIFT should match the value w longintrepr.h dla best testing.
SHIFT = sys.int_info.bits_per_digit
BASE = 2 ** SHIFT
MASK = BASE - 1
KARATSUBA_CUTOFF = 70   # z longobject.c

# Max number of base BASE digits to use w test cases.  Doubling
# this will more than double the runtime.
MAXDIGITS = 15

# build some special values
special = [0, 1, 2, BASE, BASE >> 1, 0x5555555555555555, 0xaaaaaaaaaaaaaaaa]
#  some solid strings of one bits
p2 = 4  # 0 oraz 1 already added
dla i w range(2*SHIFT):
    special.append(p2 - 1)
    p2 = p2 << 1
usuń p2
# add complements & negations
special += [~x dla x w special] + [-x dla x w special]

DBL_MAX = sys.float_info.max
DBL_MAX_EXP = sys.float_info.max_exp
DBL_MIN_EXP = sys.float_info.min_exp
DBL_MANT_DIG = sys.float_info.mant_dig
DBL_MIN_OVERFLOW = 2**DBL_MAX_EXP - 2**(DBL_MAX_EXP - DBL_MANT_DIG - 1)


# Pure Python version of correctly-rounded integer-to-float conversion.
def int_to_float(n):
    """
    Correctly-rounded integer-to-float conversion.

    """
    # Constants, depending only on the floating-point format w use.
    # We use an extra 2 bits of precision dla rounding purposes.
    PRECISION = sys.float_info.mant_dig + 2
    SHIFT_MAX = sys.float_info.max_exp - PRECISION
    Q_MAX = 1 << PRECISION
    ROUND_HALF_TO_EVEN_CORRECTION = [0, -1, -2, 1, 0, -1, 2, 1]

    # Reduce to the case where n jest positive.
    jeżeli n == 0:
        zwróć 0.0
    albo_inaczej n < 0:
        zwróć -int_to_float(-n)

    # Convert n to a 'floating-point' number q * 2**shift, where q jest an
    # integer przy 'PRECISION' significant bits.  When shifting n to create q,
    # the least significant bit of q jest treated jako 'sticky'.  That is, the
    # least significant bit of q jest set jeżeli either the corresponding bit of n
    # was already set, albo any one of the bits of n lost w the shift was set.
    shift = n.bit_length() - PRECISION
    q = n << -shift jeżeli shift < 0 inaczej (n >> shift) | bool(n & ~(-1 << shift))

    # Round half to even (actually rounds to the nearest multiple of 4,
    # rounding ties to a multiple of 8).
    q += ROUND_HALF_TO_EVEN_CORRECTION[q & 7]

    # Detect overflow.
    jeżeli shift + (q == Q_MAX) > SHIFT_MAX:
        podnieś OverflowError("integer too large to convert to float")

    # Checks: q jest exactly representable, oraz q**2**shift doesn't overflow.
    assert q % 4 == 0 oraz q // 4 <= 2**(sys.float_info.mant_dig)
    assert q * 2**shift <= sys.float_info.max

    # Some circularity here, since float(q) jest doing an int-to-float
    # conversion.  But here q jest of bounded size, oraz jest exactly representable
    # jako a float.  In a low-level C-like language, this operation would be a
    # simple cast (e.g., z unsigned long long to double).
    zwróć math.ldexp(float(q), shift)


# pure Python version of correctly-rounded true division
def truediv(a, b):
    """Correctly-rounded true division dla integers."""
    negative = a^b < 0
    a, b = abs(a), abs(b)

    # exceptions:  division by zero, overflow
    jeżeli nie b:
        podnieś ZeroDivisionError("division by zero")
    jeżeli a >= DBL_MIN_OVERFLOW * b:
        podnieś OverflowError("int/int too large to represent jako a float")

   # find integer d satisfying 2**(d - 1) <= a/b < 2**d
    d = a.bit_length() - b.bit_length()
    jeżeli d >= 0 oraz a >= 2**d * b albo d < 0 oraz a * 2**-d >= b:
        d += 1

    # compute 2**-exp * a / b dla suitable exp
    exp = max(d, DBL_MIN_EXP) - DBL_MANT_DIG
    a, b = a << max(-exp, 0), b << max(exp, 0)
    q, r = divmod(a, b)

    # round-half-to-even: fractional part jest r/b, which jest > 0.5 iff
    # 2*r > b, oraz == 0.5 iff 2*r == b.
    jeżeli 2*r > b albo 2*r == b oraz q % 2 == 1:
        q += 1

    result = math.ldexp(q, exp)
    zwróć -result jeżeli negative inaczej result


klasa LongTest(unittest.TestCase):

    # Get quasi-random long consisting of ndigits digits (in base BASE).
    # quasi == the most-significant digit will nie be 0, oraz the number
    # jest constructed to contain long strings of 0 oraz 1 bits.  These are
    # more likely than random bits to provoke digit-boundary errors.
    # The sign of the number jest also random.

    def getran(self, ndigits):
        self.assertGreater(ndigits, 0)
        nbits_hi = ndigits * SHIFT
        nbits_lo = nbits_hi - SHIFT + 1
        answer = 0
        nbits = 0
        r = int(random.random() * (SHIFT * 2)) | 1  # force 1 bits to start
        dopóki nbits < nbits_lo:
            bits = (r >> 1) + 1
            bits = min(bits, nbits_hi - nbits)
            self.assertPrawda(1 <= bits <= SHIFT)
            nbits = nbits + bits
            answer = answer << bits
            jeżeli r & 1:
                answer = answer | ((1 << bits) - 1)
            r = int(random.random() * (SHIFT * 2))
        self.assertPrawda(nbits_lo <= nbits <= nbits_hi)
        jeżeli random.random() < 0.5:
            answer = -answer
        zwróć answer

    # Get random long consisting of ndigits random digits (relative to base
    # BASE).  The sign bit jest also random.

    def getran2(ndigits):
        answer = 0
        dla i w range(ndigits):
            answer = (answer << SHIFT) | random.randint(0, MASK)
        jeżeli random.random() < 0.5:
            answer = -answer
        zwróć answer

    def check_division(self, x, y):
        eq = self.assertEqual
        q, r = divmod(x, y)
        q2, r2 = x//y, x%y
        pab, pba = x*y, y*x
        eq(pab, pba, Frm("multiplication does nie commute dla %r oraz %r", x, y))
        eq(q, q2, Frm("divmod returns different quotient than / dla %r oraz %r", x, y))
        eq(r, r2, Frm("divmod returns different mod than %% dla %r oraz %r", x, y))
        eq(x, q*y + r, Frm("x != q*y + r after divmod on x=%r, y=%r", x, y))
        jeżeli y > 0:
            self.assertPrawda(0 <= r < y, Frm("bad mod z divmod on %r oraz %r", x, y))
        inaczej:
            self.assertPrawda(y < r <= 0, Frm("bad mod z divmod on %r oraz %r", x, y))

    def test_division(self):
        digits = list(range(1, MAXDIGITS+1)) + list(range(KARATSUBA_CUTOFF,
                                                      KARATSUBA_CUTOFF + 14))
        digits.append(KARATSUBA_CUTOFF * 3)
        dla lenx w digits:
            x = self.getran(lenx)
            dla leny w digits:
                y = self.getran(leny) albo 1
                self.check_division(x, y)

        # specific numbers chosen to exercise corner cases of the
        # current long division implementation

        # 30-bit cases involving a quotient digit estimate of BASE+1
        self.check_division(1231948412290879395966702881,
                            1147341367131428698)
        self.check_division(815427756481275430342312021515587883,
                       707270836069027745)
        self.check_division(627976073697012820849443363563599041,
                       643588798496057020)
        self.check_division(1115141373653752303710932756325578065,
                       1038556335171453937726882627)
        # 30-bit cases that require the post-subtraction correction step
        self.check_division(922498905405436751940989320930368494,
                       949985870686786135626943396)
        self.check_division(768235853328091167204009652174031844,
                       1091555541180371554426545266)

        # 15-bit cases involving a quotient digit estimate of BASE+1
        self.check_division(20172188947443, 615611397)
        self.check_division(1020908530270155025, 950795710)
        self.check_division(128589565723112408, 736393718)
        self.check_division(609919780285761575, 18613274546784)
        # 15-bit cases that require the post-subtraction correction step
        self.check_division(710031681576388032, 26769404391308)
        self.check_division(1933622614268221, 30212853348836)



    def test_karatsuba(self):
        digits = list(range(1, 5)) + list(range(KARATSUBA_CUTOFF,
                                                KARATSUBA_CUTOFF + 10))
        digits.extend([KARATSUBA_CUTOFF * 10, KARATSUBA_CUTOFF * 100])

        bits = [digit * SHIFT dla digit w digits]

        # Test products of long strings of 1 bits -- (2**x-1)*(2**y-1) ==
        # 2**(x+y) - 2**x - 2**y + 1, so the proper result jest easy to check.
        dla abits w bits:
            a = (1 << abits) - 1
            dla bbits w bits:
                jeżeli bbits < abits:
                    kontynuuj
                b = (1 << bbits) - 1
                x = a * b
                y = ((1 << (abits + bbits)) -
                     (1 << abits) -
                     (1 << bbits) +
                     1)
                self.assertEqual(x, y,
                    Frm("bad result dla a*b: a=%r, b=%r, x=%r, y=%r", a, b, x, y))

    def check_bitop_identities_1(self, x):
        eq = self.assertEqual
        eq(x & 0, 0, Frm("x & 0 != 0 dla x=%r", x))
        eq(x | 0, x, Frm("x | 0 != x dla x=%r", x))
        eq(x ^ 0, x, Frm("x ^ 0 != x dla x=%r", x))
        eq(x & -1, x, Frm("x & -1 != x dla x=%r", x))
        eq(x | -1, -1, Frm("x | -1 != -1 dla x=%r", x))
        eq(x ^ -1, ~x, Frm("x ^ -1 != ~x dla x=%r", x))
        eq(x, ~~x, Frm("x != ~~x dla x=%r", x))
        eq(x & x, x, Frm("x & x != x dla x=%r", x))
        eq(x | x, x, Frm("x | x != x dla x=%r", x))
        eq(x ^ x, 0, Frm("x ^ x != 0 dla x=%r", x))
        eq(x & ~x, 0, Frm("x & ~x != 0 dla x=%r", x))
        eq(x | ~x, -1, Frm("x | ~x != -1 dla x=%r", x))
        eq(x ^ ~x, -1, Frm("x ^ ~x != -1 dla x=%r", x))
        eq(-x, 1 + ~x, Frm("not -x == 1 + ~x dla x=%r", x))
        eq(-x, ~(x-1), Frm("not -x == ~(x-1) forx =%r", x))
        dla n w range(2*SHIFT):
            p2 = 2 ** n
            eq(x << n >> n, x,
                Frm("x << n >> n != x dla x=%r, n=%r", (x, n)))
            eq(x // p2, x >> n,
                Frm("x // p2 != x >> n dla x=%r n=%r p2=%r", (x, n, p2)))
            eq(x * p2, x << n,
                Frm("x * p2 != x << n dla x=%r n=%r p2=%r", (x, n, p2)))
            eq(x & -p2, x >> n << n,
                Frm("not x & -p2 == x >> n << n dla x=%r n=%r p2=%r", (x, n, p2)))
            eq(x & -p2, x & ~(p2 - 1),
                Frm("not x & -p2 == x & ~(p2 - 1) dla x=%r n=%r p2=%r", (x, n, p2)))

    def check_bitop_identities_2(self, x, y):
        eq = self.assertEqual
        eq(x & y, y & x, Frm("x & y != y & x dla x=%r, y=%r", (x, y)))
        eq(x | y, y | x, Frm("x | y != y | x dla x=%r, y=%r", (x, y)))
        eq(x ^ y, y ^ x, Frm("x ^ y != y ^ x dla x=%r, y=%r", (x, y)))
        eq(x ^ y ^ x, y, Frm("x ^ y ^ x != y dla x=%r, y=%r", (x, y)))
        eq(x & y, ~(~x | ~y), Frm("x & y != ~(~x | ~y) dla x=%r, y=%r", (x, y)))
        eq(x | y, ~(~x & ~y), Frm("x | y != ~(~x & ~y) dla x=%r, y=%r", (x, y)))
        eq(x ^ y, (x | y) & ~(x & y),
             Frm("x ^ y != (x | y) & ~(x & y) dla x=%r, y=%r", (x, y)))
        eq(x ^ y, (x & ~y) | (~x & y),
             Frm("x ^ y == (x & ~y) | (~x & y) dla x=%r, y=%r", (x, y)))
        eq(x ^ y, (x | y) & (~x | ~y),
             Frm("x ^ y == (x | y) & (~x | ~y) dla x=%r, y=%r", (x, y)))

    def check_bitop_identities_3(self, x, y, z):
        eq = self.assertEqual
        eq((x & y) & z, x & (y & z),
             Frm("(x & y) & z != x & (y & z) dla x=%r, y=%r, z=%r", (x, y, z)))
        eq((x | y) | z, x | (y | z),
             Frm("(x | y) | z != x | (y | z) dla x=%r, y=%r, z=%r", (x, y, z)))
        eq((x ^ y) ^ z, x ^ (y ^ z),
             Frm("(x ^ y) ^ z != x ^ (y ^ z) dla x=%r, y=%r, z=%r", (x, y, z)))
        eq(x & (y | z), (x & y) | (x & z),
             Frm("x & (y | z) != (x & y) | (x & z) dla x=%r, y=%r, z=%r", (x, y, z)))
        eq(x | (y & z), (x | y) & (x | z),
             Frm("x | (y & z) != (x | y) & (x | z) dla x=%r, y=%r, z=%r", (x, y, z)))

    def test_bitop_identities(self):
        dla x w special:
            self.check_bitop_identities_1(x)
        digits = range(1, MAXDIGITS+1)
        dla lenx w digits:
            x = self.getran(lenx)
            self.check_bitop_identities_1(x)
            dla leny w digits:
                y = self.getran(leny)
                self.check_bitop_identities_2(x, y)
                self.check_bitop_identities_3(x, y, self.getran((lenx + leny)//2))

    def slow_format(self, x, base):
        digits = []
        sign = 0
        jeżeli x < 0:
            sign, x = 1, -x
        dopóki x:
            x, r = divmod(x, base)
            digits.append(int(r))
        digits.reverse()
        digits = digits albo [0]
        zwróć '-'[:sign] + \
               {2: '0b', 8: '0o', 10: '', 16: '0x'}[base] + \
               "".join("0123456789abcdef"[i] dla i w digits)

    def check_format_1(self, x):
        dla base, mapper w (2, bin), (8, oct), (10, str), (10, repr), (16, hex):
            got = mapper(x)
            expected = self.slow_format(x, base)
            msg = Frm("%s returned %r but expected %r dla %r",
                mapper.__name__, got, expected, x)
            self.assertEqual(got, expected, msg)
            self.assertEqual(int(got, 0), x, Frm('int("%s", 0) != %r', got, x))

    def test_format(self):
        dla x w special:
            self.check_format_1(x)
        dla i w range(10):
            dla lenx w range(1, MAXDIGITS+1):
                x = self.getran(lenx)
                self.check_format_1(x)

    def test_long(self):
        # Check conversions z string
        LL = [
                ('1' + '0'*20, 10**20),
                ('1' + '0'*100, 10**100)
        ]
        dla s, v w LL:
            dla sign w "", "+", "-":
                dla prefix w "", " ", "\t", "  \t\t  ":
                    ss = prefix + sign + s
                    vv = v
                    jeżeli sign == "-" oraz v jest nie ValueError:
                        vv = -v
                    spróbuj:
                        self.assertEqual(int(ss), vv)
                    wyjąwszy ValueError:
                        dalej

        # trailing L should no longer be accepted...
        self.assertRaises(ValueError, int, '123L')
        self.assertRaises(ValueError, int, '123l')
        self.assertRaises(ValueError, int, '0L')
        self.assertRaises(ValueError, int, '-37L')
        self.assertRaises(ValueError, int, '0x32L', 16)
        self.assertRaises(ValueError, int, '1L', 21)
        # ... but it's just a normal digit jeżeli base >= 22
        self.assertEqual(int('1L', 22), 43)

        # tests przy base 0
        self.assertEqual(int('000', 0), 0)
        self.assertEqual(int('0o123', 0), 83)
        self.assertEqual(int('0x123', 0), 291)
        self.assertEqual(int('0b100', 0), 4)
        self.assertEqual(int(' 0O123   ', 0), 83)
        self.assertEqual(int(' 0X123  ', 0), 291)
        self.assertEqual(int(' 0B100 ', 0), 4)
        self.assertEqual(int('0', 0), 0)
        self.assertEqual(int('+0', 0), 0)
        self.assertEqual(int('-0', 0), 0)
        self.assertEqual(int('00', 0), 0)
        self.assertRaises(ValueError, int, '08', 0)
        self.assertRaises(ValueError, int, '-012395', 0)

        # invalid bases
        invalid_bases = [-909,
                          2**31-1, 2**31, -2**31, -2**31-1,
                          2**63-1, 2**63, -2**63, -2**63-1,
                          2**100, -2**100,
                          ]
        dla base w invalid_bases:
            self.assertRaises(ValueError, int, '42', base)


    def test_conversion(self):

        klasa JustLong:
            # test that __long__ no longer used w 3.x
            def __long__(self):
                zwróć 42
        self.assertRaises(TypeError, int, JustLong())

        klasa LongTrunc:
            # __long__ should be ignored w 3.x
            def __long__(self):
                zwróć 42
            def __trunc__(self):
                zwróć 1729
        self.assertEqual(int(LongTrunc()), 1729)

    def check_float_conversion(self, n):
        # Check that int -> float conversion behaviour matches
        # that of the pure Python version above.
        spróbuj:
            actual = float(n)
        wyjąwszy OverflowError:
            actual = 'overflow'

        spróbuj:
            expected = int_to_float(n)
        wyjąwszy OverflowError:
            expected = 'overflow'

        msg = ("Error w conversion of integer {} to float.  "
               "Got {}, expected {}.".format(n, actual, expected))
        self.assertEqual(actual, expected, msg)

    @support.requires_IEEE_754
    def test_float_conversion(self):

        exact_values = [0, 1, 2,
                         2**53-3,
                         2**53-2,
                         2**53-1,
                         2**53,
                         2**53+2,
                         2**54-4,
                         2**54-2,
                         2**54,
                         2**54+4]
        dla x w exact_values:
            self.assertEqual(float(x), x)
            self.assertEqual(float(-x), -x)

        # test round-half-even
        dla x, y w [(1, 0), (2, 2), (3, 4), (4, 4), (5, 4), (6, 6), (7, 8)]:
            dla p w range(15):
                self.assertEqual(int(float(2**p*(2**53+x))), 2**p*(2**53+y))

        dla x, y w [(0, 0), (1, 0), (2, 0), (3, 4), (4, 4), (5, 4), (6, 8),
                     (7, 8), (8, 8), (9, 8), (10, 8), (11, 12), (12, 12),
                     (13, 12), (14, 16), (15, 16)]:
            dla p w range(15):
                self.assertEqual(int(float(2**p*(2**54+x))), 2**p*(2**54+y))

        # behaviour near extremes of floating-point range
        int_dbl_max = int(DBL_MAX)
        top_power = 2**DBL_MAX_EXP
        halfway = (int_dbl_max + top_power)//2
        self.assertEqual(float(int_dbl_max), DBL_MAX)
        self.assertEqual(float(int_dbl_max+1), DBL_MAX)
        self.assertEqual(float(halfway-1), DBL_MAX)
        self.assertRaises(OverflowError, float, halfway)
        self.assertEqual(float(1-halfway), -DBL_MAX)
        self.assertRaises(OverflowError, float, -halfway)
        self.assertRaises(OverflowError, float, top_power-1)
        self.assertRaises(OverflowError, float, top_power)
        self.assertRaises(OverflowError, float, top_power+1)
        self.assertRaises(OverflowError, float, 2*top_power-1)
        self.assertRaises(OverflowError, float, 2*top_power)
        self.assertRaises(OverflowError, float, top_power*top_power)

        dla p w range(100):
            x = 2**p * (2**53 + 1) + 1
            y = 2**p * (2**53 + 2)
            self.assertEqual(int(float(x)), y)

            x = 2**p * (2**53 + 1)
            y = 2**p * 2**53
            self.assertEqual(int(float(x)), y)

        # Compare builtin float conversion przy pure Python int_to_float
        # function above.
        test_values = [
            int_dbl_max-1, int_dbl_max, int_dbl_max+1,
            halfway-1, halfway, halfway + 1,
            top_power-1, top_power, top_power+1,
            2*top_power-1, 2*top_power, top_power*top_power,
        ]
        test_values.extend(exact_values)
        dla p w range(-4, 8):
            dla x w range(-128, 128):
                test_values.append(2**(p+53) + x)
        dla value w test_values:
            self.check_float_conversion(value)
            self.check_float_conversion(-value)

    def test_float_overflow(self):
        dla x w -2.0, -1.0, 0.0, 1.0, 2.0:
            self.assertEqual(float(int(x)), x)

        shuge = '12345' * 120
        huge = 1 << 30000
        mhuge = -huge
        namespace = {'huge': huge, 'mhuge': mhuge, 'shuge': shuge, 'math': math}
        dla test w ["float(huge)", "float(mhuge)",
                     "complex(huge)", "complex(mhuge)",
                     "complex(huge, 1)", "complex(mhuge, 1)",
                     "complex(1, huge)", "complex(1, mhuge)",
                     "1. + huge", "huge + 1.", "1. + mhuge", "mhuge + 1.",
                     "1. - huge", "huge - 1.", "1. - mhuge", "mhuge - 1.",
                     "1. * huge", "huge * 1.", "1. * mhuge", "mhuge * 1.",
                     "1. // huge", "huge // 1.", "1. // mhuge", "mhuge // 1.",
                     "1. / huge", "huge / 1.", "1. / mhuge", "mhuge / 1.",
                     "1. ** huge", "huge ** 1.", "1. ** mhuge", "mhuge ** 1.",
                     "math.sin(huge)", "math.sin(mhuge)",
                     "math.sqrt(huge)", "math.sqrt(mhuge)", # should do better
                     # math.floor() of an int returns an int now
                     ##"math.floor(huge)", "math.floor(mhuge)",
                     ]:

            self.assertRaises(OverflowError, eval, test, namespace)

        # XXX Perhaps float(shuge) can podnieś OverflowError on some box?
        # The comparison should not.
        self.assertNotEqual(float(shuge), int(shuge),
            "float(shuge) should nie equal int(shuge)")

    def test_logs(self):
        LOG10E = math.log10(math.e)

        dla exp w list(range(10)) + [100, 1000, 10000]:
            value = 10 ** exp
            log10 = math.log10(value)
            self.assertAlmostEqual(log10, exp)

            # log10(value) == exp, so log(value) == log10(value)/log10(e) ==
            # exp/LOG10E
            expected = exp / LOG10E
            log = math.log(value)
            self.assertAlmostEqual(log, expected)

        dla bad w -(1 << 10000), -2, 0:
            self.assertRaises(ValueError, math.log, bad)
            self.assertRaises(ValueError, math.log10, bad)

    def test_mixed_compares(self):
        eq = self.assertEqual

        # We're mostly concerned przy that mixing floats oraz ints does the
        # right stuff, even when ints are too large to fit w a float.
        # The safest way to check the results jest to use an entirely different
        # method, which we do here via a skeletal rational klasa (which
        # represents all Python ints oraz floats exactly).
        klasa Rat:
            def __init__(self, value):
                jeżeli isinstance(value, int):
                    self.n = value
                    self.d = 1
                albo_inaczej isinstance(value, float):
                    # Convert to exact rational equivalent.
                    f, e = math.frexp(abs(value))
                    assert f == 0 albo 0.5 <= f < 1.0
                    # |value| = f * 2**e exactly

                    # Suck up CHUNK bits at a time; 28 jest enough so that we suck
                    # up all bits w 2 iterations dla all known binary double-
                    # precision formats, oraz small enough to fit w an int.
                    CHUNK = 28
                    top = 0
                    # invariant: |value| = (top + f) * 2**e exactly
                    dopóki f:
                        f = math.ldexp(f, CHUNK)
                        digit = int(f)
                        assert digit >> CHUNK == 0
                        top = (top << CHUNK) | digit
                        f -= digit
                        assert 0.0 <= f < 1.0
                        e -= CHUNK

                    # Now |value| = top * 2**e exactly.
                    jeżeli e >= 0:
                        n = top << e
                        d = 1
                    inaczej:
                        n = top
                        d = 1 << -e
                    jeżeli value < 0:
                        n = -n
                    self.n = n
                    self.d = d
                    assert float(n) / float(d) == value
                inaczej:
                    podnieś TypeError("can't deal przy %r" % value)

            def _cmp__(self, other):
                jeżeli nie isinstance(other, Rat):
                    other = Rat(other)
                x, y = self.n * other.d, self.d * other.n
                zwróć (x > y) - (x < y)
            def __eq__(self, other):
                zwróć self._cmp__(other) == 0
            def __ge__(self, other):
                zwróć self._cmp__(other) >= 0
            def __gt__(self, other):
                zwróć self._cmp__(other) > 0
            def __le__(self, other):
                zwróć self._cmp__(other) <= 0
            def __lt__(self, other):
                zwróć self._cmp__(other) < 0

        cases = [0, 0.001, 0.99, 1.0, 1.5, 1e20, 1e200]
        # 2**48 jest an important boundary w the internals.  2**53 jest an
        # important boundary dla IEEE double precision.
        dla t w 2.0**48, 2.0**50, 2.0**53:
            cases.extend([t - 1.0, t - 0.3, t, t + 0.3, t + 1.0,
                          int(t-1), int(t), int(t+1)])
        cases.extend([0, 1, 2, sys.maxsize, float(sys.maxsize)])
        # 1 << 20000 should exceed all double formats.  int(1e200) jest to
        # check that we get equality przy 1e200 above.
        t = int(1e200)
        cases.extend([0, 1, 2, 1 << 20000, t-1, t, t+1])
        cases.extend([-x dla x w cases])
        dla x w cases:
            Rx = Rat(x)
            dla y w cases:
                Ry = Rat(y)
                Rcmp = (Rx > Ry) - (Rx < Ry)
                xycmp = (x > y) - (x < y)
                eq(Rcmp, xycmp, Frm("%r %r %d %d", x, y, Rcmp, xycmp))
                eq(x == y, Rcmp == 0, Frm("%r == %r %d", x, y, Rcmp))
                eq(x != y, Rcmp != 0, Frm("%r != %r %d", x, y, Rcmp))
                eq(x < y, Rcmp < 0, Frm("%r < %r %d", x, y, Rcmp))
                eq(x <= y, Rcmp <= 0, Frm("%r <= %r %d", x, y, Rcmp))
                eq(x > y, Rcmp > 0, Frm("%r > %r %d", x, y, Rcmp))
                eq(x >= y, Rcmp >= 0, Frm("%r >= %r %d", x, y, Rcmp))

    def test__format__(self):
        self.assertEqual(format(123456789, 'd'), '123456789')
        self.assertEqual(format(123456789, 'd'), '123456789')

        # sign oraz aligning are interdependent
        self.assertEqual(format(1, "-"), '1')
        self.assertEqual(format(-1, "-"), '-1')
        self.assertEqual(format(1, "-3"), '  1')
        self.assertEqual(format(-1, "-3"), ' -1')
        self.assertEqual(format(1, "+3"), ' +1')
        self.assertEqual(format(-1, "+3"), ' -1')
        self.assertEqual(format(1, " 3"), '  1')
        self.assertEqual(format(-1, " 3"), ' -1')
        self.assertEqual(format(1, " "), ' 1')
        self.assertEqual(format(-1, " "), '-1')

        # hex
        self.assertEqual(format(3, "x"), "3")
        self.assertEqual(format(3, "X"), "3")
        self.assertEqual(format(1234, "x"), "4d2")
        self.assertEqual(format(-1234, "x"), "-4d2")
        self.assertEqual(format(1234, "8x"), "     4d2")
        self.assertEqual(format(-1234, "8x"), "    -4d2")
        self.assertEqual(format(1234, "x"), "4d2")
        self.assertEqual(format(-1234, "x"), "-4d2")
        self.assertEqual(format(-3, "x"), "-3")
        self.assertEqual(format(-3, "X"), "-3")
        self.assertEqual(format(int('be', 16), "x"), "be")
        self.assertEqual(format(int('be', 16), "X"), "BE")
        self.assertEqual(format(-int('be', 16), "x"), "-be")
        self.assertEqual(format(-int('be', 16), "X"), "-BE")

        # octal
        self.assertEqual(format(3, "b"), "11")
        self.assertEqual(format(-3, "b"), "-11")
        self.assertEqual(format(1234, "b"), "10011010010")
        self.assertEqual(format(-1234, "b"), "-10011010010")
        self.assertEqual(format(1234, "-b"), "10011010010")
        self.assertEqual(format(-1234, "-b"), "-10011010010")
        self.assertEqual(format(1234, " b"), " 10011010010")
        self.assertEqual(format(-1234, " b"), "-10011010010")
        self.assertEqual(format(1234, "+b"), "+10011010010")
        self.assertEqual(format(-1234, "+b"), "-10011010010")

        # make sure these are errors
        self.assertRaises(ValueError, format, 3, "1.3")  # precision disallowed
        self.assertRaises(ValueError, format, 3, "+c")   # sign nie allowed
                                                         # przy 'c'

        # ensure that only int oraz float type specifiers work
        dla format_spec w ([chr(x) dla x w range(ord('a'), ord('z')+1)] +
                            [chr(x) dla x w range(ord('A'), ord('Z')+1)]):
            jeżeli nie format_spec w 'bcdoxXeEfFgGn%':
                self.assertRaises(ValueError, format, 0, format_spec)
                self.assertRaises(ValueError, format, 1, format_spec)
                self.assertRaises(ValueError, format, -1, format_spec)
                self.assertRaises(ValueError, format, 2**100, format_spec)
                self.assertRaises(ValueError, format, -(2**100), format_spec)

        # ensure that float type specifiers work; format converts
        #  the int to a float
        dla format_spec w 'eEfFgG%':
            dla value w [0, 1, -1, 100, -100, 1234567890, -1234567890]:
                self.assertEqual(format(value, format_spec),
                                 format(float(value), format_spec))

    def test_nan_inf(self):
        self.assertRaises(OverflowError, int, float('inf'))
        self.assertRaises(OverflowError, int, float('-inf'))
        self.assertRaises(ValueError, int, float('nan'))

    def test_true_division(self):
        huge = 1 << 40000
        mhuge = -huge
        self.assertEqual(huge / huge, 1.0)
        self.assertEqual(mhuge / mhuge, 1.0)
        self.assertEqual(huge / mhuge, -1.0)
        self.assertEqual(mhuge / huge, -1.0)
        self.assertEqual(1 / huge, 0.0)
        self.assertEqual(1 / huge, 0.0)
        self.assertEqual(1 / mhuge, 0.0)
        self.assertEqual(1 / mhuge, 0.0)
        self.assertEqual((666 * huge + (huge >> 1)) / huge, 666.5)
        self.assertEqual((666 * mhuge + (mhuge >> 1)) / mhuge, 666.5)
        self.assertEqual((666 * huge + (huge >> 1)) / mhuge, -666.5)
        self.assertEqual((666 * mhuge + (mhuge >> 1)) / huge, -666.5)
        self.assertEqual(huge / (huge << 1), 0.5)
        self.assertEqual((1000000 * huge) / huge, 1000000)

        namespace = {'huge': huge, 'mhuge': mhuge}

        dla overflow w ["float(huge)", "float(mhuge)",
                         "huge / 1", "huge / 2", "huge / -1", "huge / -2",
                         "mhuge / 100", "mhuge / 200"]:
            self.assertRaises(OverflowError, eval, overflow, namespace)

        dla underflow w ["1 / huge", "2 / huge", "-1 / huge", "-2 / huge",
                         "100 / mhuge", "200 / mhuge"]:
            result = eval(underflow, namespace)
            self.assertEqual(result, 0.0,
                             "expected underflow to 0 z %r" % underflow)

        dla zero w ["huge / 0", "mhuge / 0"]:
            self.assertRaises(ZeroDivisionError, eval, zero, namespace)

    def check_truediv(self, a, b, skip_small=Prawda):
        """Verify that the result of a/b jest correctly rounded, by
        comparing it przy a pure Python implementation of correctly
        rounded division.  b should be nonzero."""

        # skip check dla small a oraz b: w this case, the current
        # implementation converts the arguments to float directly oraz
        # then applies a float division.  This can give doubly-rounded
        # results on x87-using machines (particularly 32-bit Linux).
        jeżeli skip_small oraz max(abs(a), abs(b)) < 2**DBL_MANT_DIG:
            zwróć

        spróbuj:
            # use repr so that we can distinguish between -0.0 oraz 0.0
            expected = repr(truediv(a, b))
        wyjąwszy OverflowError:
            expected = 'overflow'
        wyjąwszy ZeroDivisionError:
            expected = 'zerodivision'

        spróbuj:
            got = repr(a / b)
        wyjąwszy OverflowError:
            got = 'overflow'
        wyjąwszy ZeroDivisionError:
            got = 'zerodivision'

        self.assertEqual(expected, got, "Incorrectly rounded division {}/{}: "
                         "expected {}, got {}".format(a, b, expected, got))

    @support.requires_IEEE_754
    def test_correctly_rounded_true_division(self):
        # more stringent tests than those above, checking that the
        # result of true division of ints jest always correctly rounded.
        # This test should probably be considered CPython-specific.

        # Exercise all the code paths nie involving Gb-sized ints.
        # ... divisions involving zero
        self.check_truediv(123, 0)
        self.check_truediv(-456, 0)
        self.check_truediv(0, 3)
        self.check_truediv(0, -3)
        self.check_truediv(0, 0)
        # ... overflow albo underflow by large margin
        self.check_truediv(671 * 12345 * 2**DBL_MAX_EXP, 12345)
        self.check_truediv(12345, 345678 * 2**(DBL_MANT_DIG - DBL_MIN_EXP))
        # ... a much larger albo smaller than b
        self.check_truediv(12345*2**100, 98765)
        self.check_truediv(12345*2**30, 98765*7**81)
        # ... a / b near a boundary: one of 1, 2**DBL_MANT_DIG, 2**DBL_MIN_EXP,
        #                 2**DBL_MAX_EXP, 2**(DBL_MIN_EXP-DBL_MANT_DIG)
        bases = (0, DBL_MANT_DIG, DBL_MIN_EXP,
                 DBL_MAX_EXP, DBL_MIN_EXP - DBL_MANT_DIG)
        dla base w bases:
            dla exp w range(base - 15, base + 15):
                self.check_truediv(75312*2**max(exp, 0), 69187*2**max(-exp, 0))
                self.check_truediv(69187*2**max(exp, 0), 75312*2**max(-exp, 0))

        # overflow corner case
        dla m w [1, 2, 7, 17, 12345, 7**100,
                  -1, -2, -5, -23, -67891, -41**50]:
            dla n w range(-10, 10):
                self.check_truediv(m*DBL_MIN_OVERFLOW + n, m)
                self.check_truediv(m*DBL_MIN_OVERFLOW + n, -m)

        # check detection of inexactness w shifting stage
        dla n w range(250):
            # (2**DBL_MANT_DIG+1)/(2**DBL_MANT_DIG) lies halfway
            # between two representable floats, oraz would usually be
            # rounded down under round-half-to-even.  The tiniest of
            # additions to the numerator should cause it to be rounded
            # up instead.
            self.check_truediv((2**DBL_MANT_DIG + 1)*12345*2**200 + 2**n,
                           2**DBL_MANT_DIG*12345)

        # 1/2731 jest one of the smallest division cases that's subject
        # to double rounding on IEEE 754 machines working internally with
        # 64-bit precision.  On such machines, the next check would fail,
        # were it nie explicitly skipped w check_truediv.
        self.check_truediv(1, 2731)

        # a particularly bad case dla the old algorithm:  gives an
        # error of close to 3.5 ulps.
        self.check_truediv(295147931372582273023, 295147932265116303360)
        dla i w range(1000):
            self.check_truediv(10**(i+1), 10**i)
            self.check_truediv(10**i, 10**(i+1))

        # test round-half-to-even behaviour, normal result
        dla m w [1, 2, 4, 7, 8, 16, 17, 32, 12345, 7**100,
                  -1, -2, -5, -23, -67891, -41**50]:
            dla n w range(-10, 10):
                self.check_truediv(2**DBL_MANT_DIG*m + n, m)

        # test round-half-to-even, subnormal result
        dla n w range(-20, 20):
            self.check_truediv(n, 2**1076)

        # largeish random divisions: a/b where |a| <= |b| <=
        # 2*|a|; |ans| jest between 0.5 oraz 1.0, so error should
        # always be bounded by 2**-54 przy equality possible only
        # jeżeli the least significant bit of q=ans*2**53 jest zero.
        dla M w [10**10, 10**100, 10**1000]:
            dla i w range(1000):
                a = random.randrange(1, M)
                b = random.randrange(a, 2*a+1)
                self.check_truediv(a, b)
                self.check_truediv(-a, b)
                self.check_truediv(a, -b)
                self.check_truediv(-a, -b)

        # oraz some (genuinely) random tests
        dla _ w range(10000):
            a_bits = random.randrange(1000)
            b_bits = random.randrange(1, 1000)
            x = random.randrange(2**a_bits)
            y = random.randrange(1, 2**b_bits)
            self.check_truediv(x, y)
            self.check_truediv(x, -y)
            self.check_truediv(-x, y)
            self.check_truediv(-x, -y)

    def test_small_ints(self):
        dla i w range(-5, 257):
            self.assertIs(i, i + 0)
            self.assertIs(i, i * 1)
            self.assertIs(i, i - 0)
            self.assertIs(i, i // 1)
            self.assertIs(i, i & -1)
            self.assertIs(i, i | 0)
            self.assertIs(i, i ^ 0)
            self.assertIs(i, ~~i)
            self.assertIs(i, i**1)
            self.assertIs(i, int(str(i)))
            self.assertIs(i, i<<2>>2, str(i))
        # corner cases
        i = 1 << 70
        self.assertIs(i - i, 0)
        self.assertIs(0 * i, 0)

    def test_bit_length(self):
        tiny = 1e-10
        dla x w range(-65000, 65000):
            k = x.bit_length()
            # Check equivalence przy Python version
            self.assertEqual(k, len(bin(x).lstrip('-0b')))
            # Behaviour jako specified w the docs
            jeżeli x != 0:
                self.assertPrawda(2**(k-1) <= abs(x) < 2**k)
            inaczej:
                self.assertEqual(k, 0)
            # Alternative definition: x.bit_length() == 1 + floor(log_2(x))
            jeżeli x != 0:
                # When x jest an exact power of 2, numeric errors can
                # cause floor(log(x)/log(2)) to be one too small; for
                # small x this can be fixed by adding a small quantity
                # to the quotient before taking the floor.
                self.assertEqual(k, 1 + math.floor(
                        math.log(abs(x))/math.log(2) + tiny))

        self.assertEqual((0).bit_length(), 0)
        self.assertEqual((1).bit_length(), 1)
        self.assertEqual((-1).bit_length(), 1)
        self.assertEqual((2).bit_length(), 2)
        self.assertEqual((-2).bit_length(), 2)
        dla i w [2, 3, 15, 16, 17, 31, 32, 33, 63, 64, 234]:
            a = 2**i
            self.assertEqual((a-1).bit_length(), i)
            self.assertEqual((1-a).bit_length(), i)
            self.assertEqual((a).bit_length(), i+1)
            self.assertEqual((-a).bit_length(), i+1)
            self.assertEqual((a+1).bit_length(), i+1)
            self.assertEqual((-a-1).bit_length(), i+1)

    def test_round(self):
        # check round-half-even algorithm. For round to nearest ten;
        # rounding map jest invariant under adding multiples of 20
        test_dict = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0,
                     6:10, 7:10, 8:10, 9:10, 10:10, 11:10, 12:10, 13:10, 14:10,
                     15:20, 16:20, 17:20, 18:20, 19:20}
        dla offset w range(-520, 520, 20):
            dla k, v w test_dict.items():
                got = round(k+offset, -1)
                expected = v+offset
                self.assertEqual(got, expected)
                self.assertIs(type(got), int)

        # larger second argument
        self.assertEqual(round(-150, -2), -200)
        self.assertEqual(round(-149, -2), -100)
        self.assertEqual(round(-51, -2), -100)
        self.assertEqual(round(-50, -2), 0)
        self.assertEqual(round(-49, -2), 0)
        self.assertEqual(round(-1, -2), 0)
        self.assertEqual(round(0, -2), 0)
        self.assertEqual(round(1, -2), 0)
        self.assertEqual(round(49, -2), 0)
        self.assertEqual(round(50, -2), 0)
        self.assertEqual(round(51, -2), 100)
        self.assertEqual(round(149, -2), 100)
        self.assertEqual(round(150, -2), 200)
        self.assertEqual(round(250, -2), 200)
        self.assertEqual(round(251, -2), 300)
        self.assertEqual(round(172500, -3), 172000)
        self.assertEqual(round(173500, -3), 174000)
        self.assertEqual(round(31415926535, -1), 31415926540)
        self.assertEqual(round(31415926535, -2), 31415926500)
        self.assertEqual(round(31415926535, -3), 31415927000)
        self.assertEqual(round(31415926535, -4), 31415930000)
        self.assertEqual(round(31415926535, -5), 31415900000)
        self.assertEqual(round(31415926535, -6), 31416000000)
        self.assertEqual(round(31415926535, -7), 31420000000)
        self.assertEqual(round(31415926535, -8), 31400000000)
        self.assertEqual(round(31415926535, -9), 31000000000)
        self.assertEqual(round(31415926535, -10), 30000000000)
        self.assertEqual(round(31415926535, -11), 0)
        self.assertEqual(round(31415926535, -12), 0)
        self.assertEqual(round(31415926535, -999), 0)

        # should get correct results even dla huge inputs
        dla k w range(10, 100):
            got = round(10**k + 324678, -3)
            expect = 10**k + 325000
            self.assertEqual(got, expect)
            self.assertIs(type(got), int)

        # nonnegative second argument: round(x, n) should just zwróć x
        dla n w range(5):
            dla i w range(100):
                x = random.randrange(-10000, 10000)
                got = round(x, n)
                self.assertEqual(got, x)
                self.assertIs(type(got), int)
        dla huge_n w 2**31-1, 2**31, 2**63-1, 2**63, 2**100, 10**100:
            self.assertEqual(round(8979323, huge_n), 8979323)

        # omitted second argument
        dla i w range(100):
            x = random.randrange(-10000, 10000)
            got = round(x)
            self.assertEqual(got, x)
            self.assertIs(type(got), int)

        # bad second argument
        bad_exponents = ('brian', 2.0, 0j, Nic)
        dla e w bad_exponents:
            self.assertRaises(TypeError, round, 3, e)

    def test_to_bytes(self):
        def check(tests, byteorder, signed=Nieprawda):
            dla test, expected w tests.items():
                spróbuj:
                    self.assertEqual(
                        test.to_bytes(len(expected), byteorder, signed=signed),
                        expected)
                wyjąwszy Exception jako err:
                    podnieś AssertionError(
                        "failed to convert {0} przy byteorder={1} oraz signed={2}"
                        .format(test, byteorder, signed)) z err

        # Convert integers to signed big-endian byte arrays.
        tests1 = {
            0: b'\x00',
            1: b'\x01',
            -1: b'\xff',
            -127: b'\x81',
            -128: b'\x80',
            -129: b'\xff\x7f',
            127: b'\x7f',
            129: b'\x00\x81',
            -255: b'\xff\x01',
            -256: b'\xff\x00',
            255: b'\x00\xff',
            256: b'\x01\x00',
            32767: b'\x7f\xff',
            -32768: b'\xff\x80\x00',
            65535: b'\x00\xff\xff',
            -65536: b'\xff\x00\x00',
            -8388608: b'\x80\x00\x00'
        }
        check(tests1, 'big', signed=Prawda)

        # Convert integers to signed little-endian byte arrays.
        tests2 = {
            0: b'\x00',
            1: b'\x01',
            -1: b'\xff',
            -127: b'\x81',
            -128: b'\x80',
            -129: b'\x7f\xff',
            127: b'\x7f',
            129: b'\x81\x00',
            -255: b'\x01\xff',
            -256: b'\x00\xff',
            255: b'\xff\x00',
            256: b'\x00\x01',
            32767: b'\xff\x7f',
            -32768: b'\x00\x80',
            65535: b'\xff\xff\x00',
            -65536: b'\x00\x00\xff',
            -8388608: b'\x00\x00\x80'
        }
        check(tests2, 'little', signed=Prawda)

        # Convert integers to unsigned big-endian byte arrays.
        tests3 = {
            0: b'\x00',
            1: b'\x01',
            127: b'\x7f',
            128: b'\x80',
            255: b'\xff',
            256: b'\x01\x00',
            32767: b'\x7f\xff',
            32768: b'\x80\x00',
            65535: b'\xff\xff',
            65536: b'\x01\x00\x00'
        }
        check(tests3, 'big', signed=Nieprawda)

        # Convert integers to unsigned little-endian byte arrays.
        tests4 = {
            0: b'\x00',
            1: b'\x01',
            127: b'\x7f',
            128: b'\x80',
            255: b'\xff',
            256: b'\x00\x01',
            32767: b'\xff\x7f',
            32768: b'\x00\x80',
            65535: b'\xff\xff',
            65536: b'\x00\x00\x01'
        }
        check(tests4, 'little', signed=Nieprawda)

        self.assertRaises(OverflowError, (256).to_bytes, 1, 'big', signed=Nieprawda)
        self.assertRaises(OverflowError, (256).to_bytes, 1, 'big', signed=Prawda)
        self.assertRaises(OverflowError, (256).to_bytes, 1, 'little', signed=Nieprawda)
        self.assertRaises(OverflowError, (256).to_bytes, 1, 'little', signed=Prawda)
        self.assertRaises(OverflowError, (-1).to_bytes, 2, 'big', signed=Nieprawda)
        self.assertRaises(OverflowError, (-1).to_bytes, 2, 'little', signed=Nieprawda)
        self.assertEqual((0).to_bytes(0, 'big'), b'')
        self.assertEqual((1).to_bytes(5, 'big'), b'\x00\x00\x00\x00\x01')
        self.assertEqual((0).to_bytes(5, 'big'), b'\x00\x00\x00\x00\x00')
        self.assertEqual((-1).to_bytes(5, 'big', signed=Prawda),
                         b'\xff\xff\xff\xff\xff')
        self.assertRaises(OverflowError, (1).to_bytes, 0, 'big')

    def test_from_bytes(self):
        def check(tests, byteorder, signed=Nieprawda):
            dla test, expected w tests.items():
                spróbuj:
                    self.assertEqual(
                        int.from_bytes(test, byteorder, signed=signed),
                        expected)
                wyjąwszy Exception jako err:
                    podnieś AssertionError(
                        "failed to convert {0} przy byteorder={1!r} oraz signed={2}"
                        .format(test, byteorder, signed)) z err

        # Convert signed big-endian byte arrays to integers.
        tests1 = {
            b'': 0,
            b'\x00': 0,
            b'\x00\x00': 0,
            b'\x01': 1,
            b'\x00\x01': 1,
            b'\xff': -1,
            b'\xff\xff': -1,
            b'\x81': -127,
            b'\x80': -128,
            b'\xff\x7f': -129,
            b'\x7f': 127,
            b'\x00\x81': 129,
            b'\xff\x01': -255,
            b'\xff\x00': -256,
            b'\x00\xff': 255,
            b'\x01\x00': 256,
            b'\x7f\xff': 32767,
            b'\x80\x00': -32768,
            b'\x00\xff\xff': 65535,
            b'\xff\x00\x00': -65536,
            b'\x80\x00\x00': -8388608
        }
        check(tests1, 'big', signed=Prawda)

        # Convert signed little-endian byte arrays to integers.
        tests2 = {
            b'': 0,
            b'\x00': 0,
            b'\x00\x00': 0,
            b'\x01': 1,
            b'\x00\x01': 256,
            b'\xff': -1,
            b'\xff\xff': -1,
            b'\x81': -127,
            b'\x80': -128,
            b'\x7f\xff': -129,
            b'\x7f': 127,
            b'\x81\x00': 129,
            b'\x01\xff': -255,
            b'\x00\xff': -256,
            b'\xff\x00': 255,
            b'\x00\x01': 256,
            b'\xff\x7f': 32767,
            b'\x00\x80': -32768,
            b'\xff\xff\x00': 65535,
            b'\x00\x00\xff': -65536,
            b'\x00\x00\x80': -8388608
        }
        check(tests2, 'little', signed=Prawda)

        # Convert unsigned big-endian byte arrays to integers.
        tests3 = {
            b'': 0,
            b'\x00': 0,
            b'\x01': 1,
            b'\x7f': 127,
            b'\x80': 128,
            b'\xff': 255,
            b'\x01\x00': 256,
            b'\x7f\xff': 32767,
            b'\x80\x00': 32768,
            b'\xff\xff': 65535,
            b'\x01\x00\x00': 65536,
        }
        check(tests3, 'big', signed=Nieprawda)

        # Convert integers to unsigned little-endian byte arrays.
        tests4 = {
            b'': 0,
            b'\x00': 0,
            b'\x01': 1,
            b'\x7f': 127,
            b'\x80': 128,
            b'\xff': 255,
            b'\x00\x01': 256,
            b'\xff\x7f': 32767,
            b'\x00\x80': 32768,
            b'\xff\xff': 65535,
            b'\x00\x00\x01': 65536,
        }
        check(tests4, 'little', signed=Nieprawda)

        klasa myint(int):
            dalej

        self.assertIs(type(myint.from_bytes(b'\x00', 'big')), myint)
        self.assertEqual(myint.from_bytes(b'\x01', 'big'), 1)
        self.assertIs(
            type(myint.from_bytes(b'\x00', 'big', signed=Nieprawda)), myint)
        self.assertEqual(myint.from_bytes(b'\x01', 'big', signed=Nieprawda), 1)
        self.assertIs(type(myint.from_bytes(b'\x00', 'little')), myint)
        self.assertEqual(myint.from_bytes(b'\x01', 'little'), 1)
        self.assertIs(type(myint.from_bytes(
            b'\x00', 'little', signed=Nieprawda)), myint)
        self.assertEqual(myint.from_bytes(b'\x01', 'little', signed=Nieprawda), 1)
        self.assertEqual(
            int.from_bytes([255, 0, 0], 'big', signed=Prawda), -65536)
        self.assertEqual(
            int.from_bytes((255, 0, 0), 'big', signed=Prawda), -65536)
        self.assertEqual(int.from_bytes(
            bytearray(b'\xff\x00\x00'), 'big', signed=Prawda), -65536)
        self.assertEqual(int.from_bytes(
            bytearray(b'\xff\x00\x00'), 'big', signed=Prawda), -65536)
        self.assertEqual(int.from_bytes(
            array.array('B', b'\xff\x00\x00'), 'big', signed=Prawda), -65536)
        self.assertEqual(int.from_bytes(
            memoryview(b'\xff\x00\x00'), 'big', signed=Prawda), -65536)
        self.assertRaises(ValueError, int.from_bytes, [256], 'big')
        self.assertRaises(ValueError, int.from_bytes, [0], 'big\x00')
        self.assertRaises(ValueError, int.from_bytes, [0], 'little\x00')
        self.assertRaises(TypeError, int.from_bytes, "", 'big')
        self.assertRaises(TypeError, int.from_bytes, "\x00", 'big')
        self.assertRaises(TypeError, int.from_bytes, 0, 'big')
        self.assertRaises(TypeError, int.from_bytes, 0, 'big', Prawda)
        self.assertRaises(TypeError, myint.from_bytes, "", 'big')
        self.assertRaises(TypeError, myint.from_bytes, "\x00", 'big')
        self.assertRaises(TypeError, myint.from_bytes, 0, 'big')
        self.assertRaises(TypeError, int.from_bytes, 0, 'big', Prawda)

    def test_access_to_nonexistent_digit_0(self):
        # http://bugs.python.org/issue14630: A bug w _PyLong_Copy meant that
        # ob_digit[0] was being incorrectly accessed dla instances of a
        # subclass of int, przy value 0.
        klasa Integer(int):
            def __new__(cls, value=0):
                self = int.__new__(cls, value)
                self.foo = 'foo'
                zwróć self

        integers = [Integer(0) dla i w range(1000)]
        dla n w map(int, integers):
            self.assertEqual(n, 0)

    def test_shift_bool(self):
        # Issue #21422: ensure that bool << int oraz bool >> int zwróć int
        dla value w (Prawda, Nieprawda):
            dla shift w (0, 2):
                self.assertEqual(type(value << shift), int)
                self.assertEqual(type(value >> shift), int)


jeżeli __name__ == "__main__":
    unittest.main()
