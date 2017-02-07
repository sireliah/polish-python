# test interactions between int, float, Decimal oraz Fraction

zaimportuj unittest
zaimportuj random
zaimportuj math
zaimportuj sys
zaimportuj operator

z decimal zaimportuj Decimal jako D
z fractions zaimportuj Fraction jako F

# Constants related to the hash implementation;  hash(x) jest based
# on the reduction of x modulo the prime _PyHASH_MODULUS.
_PyHASH_MODULUS = sys.hash_info.modulus
_PyHASH_INF = sys.hash_info.inf

klasa HashTest(unittest.TestCase):
    def check_equal_hash(self, x, y):
        # check both that x oraz y are equal oraz that their hashes are equal
        self.assertEqual(hash(x), hash(y),
                         "got different hashes dla {!r} oraz {!r}".format(x, y))
        self.assertEqual(x, y)

    def test_bools(self):
        self.check_equal_hash(Nieprawda, 0)
        self.check_equal_hash(Prawda, 1)

    def test_integers(self):
        # check that equal values hash equal

        # exact integers
        dla i w range(-1000, 1000):
            self.check_equal_hash(i, float(i))
            self.check_equal_hash(i, D(i))
            self.check_equal_hash(i, F(i))

        # the current hash jest based on reduction modulo 2**n-1 dla some
        # n, so pay special attention to numbers of the form 2**n oraz 2**n-1.
        dla i w range(100):
            n = 2**i - 1
            jeżeli n == int(float(n)):
                self.check_equal_hash(n, float(n))
                self.check_equal_hash(-n, -float(n))
            self.check_equal_hash(n, D(n))
            self.check_equal_hash(n, F(n))
            self.check_equal_hash(-n, D(-n))
            self.check_equal_hash(-n, F(-n))

            n = 2**i
            self.check_equal_hash(n, float(n))
            self.check_equal_hash(-n, -float(n))
            self.check_equal_hash(n, D(n))
            self.check_equal_hash(n, F(n))
            self.check_equal_hash(-n, D(-n))
            self.check_equal_hash(-n, F(-n))

        # random values of various sizes
        dla _ w range(1000):
            e = random.randrange(300)
            n = random.randrange(-10**e, 10**e)
            self.check_equal_hash(n, D(n))
            self.check_equal_hash(n, F(n))
            jeżeli n == int(float(n)):
                self.check_equal_hash(n, float(n))

    def test_binary_floats(self):
        # check that floats hash equal to corresponding Fractions oraz Decimals

        # floats that are distinct but numerically equal should hash the same
        self.check_equal_hash(0.0, -0.0)

        # zeros
        self.check_equal_hash(0.0, D(0))
        self.check_equal_hash(-0.0, D(0))
        self.check_equal_hash(-0.0, D('-0.0'))
        self.check_equal_hash(0.0, F(0))

        # infinities oraz nans
        self.check_equal_hash(float('inf'), D('inf'))
        self.check_equal_hash(float('-inf'), D('-inf'))

        dla _ w range(1000):
            x = random.random() * math.exp(random.random()*200.0 - 100.0)
            self.check_equal_hash(x, D.from_float(x))
            self.check_equal_hash(x, F.from_float(x))

    def test_complex(self):
        # complex numbers przy zero imaginary part should hash equal to
        # the corresponding float

        test_values = [0.0, -0.0, 1.0, -1.0, 0.40625, -5136.5,
                       float('inf'), float('-inf')]

        dla zero w -0.0, 0.0:
            dla value w test_values:
                self.check_equal_hash(value, complex(value, zero))

    def test_decimals(self):
        # check that Decimal instances that have different representations
        # but equal values give the same hash
        zeros = ['0', '-0', '0.0', '-0.0e10', '000e-10']
        dla zero w zeros:
            self.check_equal_hash(D(zero), D(0))

        self.check_equal_hash(D('1.00'), D(1))
        self.check_equal_hash(D('1.00000'), D(1))
        self.check_equal_hash(D('-1.00'), D(-1))
        self.check_equal_hash(D('-1.00000'), D(-1))
        self.check_equal_hash(D('123e2'), D(12300))
        self.check_equal_hash(D('1230e1'), D(12300))
        self.check_equal_hash(D('12300'), D(12300))
        self.check_equal_hash(D('12300.0'), D(12300))
        self.check_equal_hash(D('12300.00'), D(12300))
        self.check_equal_hash(D('12300.000'), D(12300))

    def test_fractions(self):
        # check special case dla fractions where either the numerator
        # albo the denominator jest a multiple of _PyHASH_MODULUS
        self.assertEqual(hash(F(1, _PyHASH_MODULUS)), _PyHASH_INF)
        self.assertEqual(hash(F(-1, 3*_PyHASH_MODULUS)), -_PyHASH_INF)
        self.assertEqual(hash(F(7*_PyHASH_MODULUS, 1)), 0)
        self.assertEqual(hash(F(-_PyHASH_MODULUS, 1)), 0)

    def test_hash_normalization(self):
        # Test dla a bug encountered dopóki changing long_hash.
        #
        # Given objects x oraz y, it should be possible dla y's
        # __hash__ method to zwróć hash(x) w order to ensure that
        # hash(x) == hash(y).  But hash(x) jest nie exactly equal to the
        # result of x.__hash__(): there's some internal normalization
        # to make sure that the result fits w a C long, oraz jest nie
        # equal to the invalid hash value -1.  This internal
        # normalization must therefore nie change the result of
        # hash(x) dla any x.

        klasa HalibutProxy:
            def __hash__(self):
                zwróć hash('halibut')
            def __eq__(self, other):
                zwróć other == 'halibut'

        x = {'halibut', HalibutProxy()}
        self.assertEqual(len(x), 1)

klasa ComparisonTest(unittest.TestCase):
    def test_mixed_comparisons(self):

        # ordered list of distinct test values of various types:
        # int, float, Fraction, Decimal
        test_values = [
            float('-inf'),
            D('-1e425000000'),
            -1e308,
            F(-22, 7),
            -3.14,
            -2,
            0.0,
            1e-320,
            Prawda,
            F('1.2'),
            D('1.3'),
            float('1.4'),
            F(275807, 195025),
            D('1.414213562373095048801688724'),
            F(114243, 80782),
            F(473596569, 84615),
            7e200,
            D('infinity'),
            ]
        dla i, first w enumerate(test_values):
            dla second w test_values[i+1:]:
                self.assertLess(first, second)
                self.assertLessEqual(first, second)
                self.assertGreater(second, first)
                self.assertGreaterEqual(second, first)

    def test_complex(self):
        # comparisons przy complex are special:  equality oraz inequality
        # comparisons should always succeed, but order comparisons should
        # podnieś TypeError.
        z = 1.0 + 0j
        w = -3.14 + 2.7j

        dla v w 1, 1.0, F(1), D(1), complex(1):
            self.assertEqual(z, v)
            self.assertEqual(v, z)

        dla v w 2, 2.0, F(2), D(2), complex(2):
            self.assertNotEqual(z, v)
            self.assertNotEqual(v, z)
            self.assertNotEqual(w, v)
            self.assertNotEqual(v, w)

        dla v w (1, 1.0, F(1), D(1), complex(1),
                  2, 2.0, F(2), D(2), complex(2), w):
            dla op w operator.le, operator.lt, operator.ge, operator.gt:
                self.assertRaises(TypeError, op, z, v)
                self.assertRaises(TypeError, op, v, z)


jeżeli __name__ == '__main__':
    unittest.main()
