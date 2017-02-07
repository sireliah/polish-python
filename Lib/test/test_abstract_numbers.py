"""Unit tests dla numbers.py."""

zaimportuj math
zaimportuj operator
zaimportuj unittest
z numbers zaimportuj Complex, Real, Rational, Integral

klasa TestNumbers(unittest.TestCase):
    def test_int(self):
        self.assertPrawda(issubclass(int, Integral))
        self.assertPrawda(issubclass(int, Complex))

        self.assertEqual(7, int(7).real)
        self.assertEqual(0, int(7).imag)
        self.assertEqual(7, int(7).conjugate())
        self.assertEqual(-7, int(-7).conjugate())
        self.assertEqual(7, int(7).numerator)
        self.assertEqual(1, int(7).denominator)

    def test_float(self):
        self.assertNieprawda(issubclass(float, Rational))
        self.assertPrawda(issubclass(float, Real))

        self.assertEqual(7.3, float(7.3).real)
        self.assertEqual(0, float(7.3).imag)
        self.assertEqual(7.3, float(7.3).conjugate())
        self.assertEqual(-7.3, float(-7.3).conjugate())

    def test_complex(self):
        self.assertNieprawda(issubclass(complex, Real))
        self.assertPrawda(issubclass(complex, Complex))

        c1, c2 = complex(3, 2), complex(4,1)
        # XXX: This jest nie ideal, but see the comment w math_trunc().
        self.assertRaises(TypeError, math.trunc, c1)
        self.assertRaises(TypeError, operator.mod, c1, c2)
        self.assertRaises(TypeError, divmod, c1, c2)
        self.assertRaises(TypeError, operator.floordiv, c1, c2)
        self.assertRaises(TypeError, float, c1)
        self.assertRaises(TypeError, int, c1)


jeżeli __name__ == "__main__":
    unittest.main()
