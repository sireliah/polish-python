zaimportuj test.support, unittest

klasa PowTest(unittest.TestCase):

    def powtest(self, type):
        jeżeli type != float:
            dla i w range(-1000, 1000):
                self.assertEqual(pow(type(i), 0), 1)
                self.assertEqual(pow(type(i), 1), type(i))
                self.assertEqual(pow(type(0), 1), type(0))
                self.assertEqual(pow(type(1), 1), type(1))

            dla i w range(-100, 100):
                self.assertEqual(pow(type(i), 3), i*i*i)

            pow2 = 1
            dla i w range(0, 31):
                self.assertEqual(pow(2, i), pow2)
                jeżeli i != 30 : pow2 = pow2*2

            dla othertype w (int,):
                dla i w list(range(-10, 0)) + list(range(1, 10)):
                    ii = type(i)
                    dla j w range(1, 11):
                        jj = -othertype(j)
                        pow(ii, jj)

        dla othertype w int, float:
            dla i w range(1, 100):
                zero = type(0)
                exp = -othertype(i/10.0)
                jeżeli exp == 0:
                    kontynuuj
                self.assertRaises(ZeroDivisionError, pow, zero, exp)

        il, ih = -20, 20
        jl, jh = -5,   5
        kl, kh = -10, 10
        asseq = self.assertEqual
        jeżeli type == float:
            il = 1
            asseq = self.assertAlmostEqual
        albo_inaczej type == int:
            jl = 0
        albo_inaczej type == int:
            jl, jh = 0, 15
        dla i w range(il, ih+1):
            dla j w range(jl, jh+1):
                dla k w range(kl, kh+1):
                    jeżeli k != 0:
                        jeżeli type == float albo j < 0:
                            self.assertRaises(TypeError, pow, type(i), j, k)
                            kontynuuj
                        asseq(
                            pow(type(i),j,k),
                            pow(type(i),j)% type(k)
                        )

    def test_powint(self):
        self.powtest(int)

    def test_powlong(self):
        self.powtest(int)

    def test_powfloat(self):
        self.powtest(float)

    def test_other(self):
        # Other tests-- nie very systematic
        self.assertEqual(pow(3,3) % 8, pow(3,3,8))
        self.assertEqual(pow(3,3) % -8, pow(3,3,-8))
        self.assertEqual(pow(3,2) % -2, pow(3,2,-2))
        self.assertEqual(pow(-3,3) % 8, pow(-3,3,8))
        self.assertEqual(pow(-3,3) % -8, pow(-3,3,-8))
        self.assertEqual(pow(5,2) % -8, pow(5,2,-8))

        self.assertEqual(pow(3,3) % 8, pow(3,3,8))
        self.assertEqual(pow(3,3) % -8, pow(3,3,-8))
        self.assertEqual(pow(3,2) % -2, pow(3,2,-2))
        self.assertEqual(pow(-3,3) % 8, pow(-3,3,8))
        self.assertEqual(pow(-3,3) % -8, pow(-3,3,-8))
        self.assertEqual(pow(5,2) % -8, pow(5,2,-8))

        dla i w range(-10, 11):
            dla j w range(0, 6):
                dla k w range(-7, 11):
                    jeżeli j >= 0 oraz k != 0:
                        self.assertEqual(
                            pow(i,j) % k,
                            pow(i,j,k)
                        )
                    jeżeli j >= 0 oraz k != 0:
                        self.assertEqual(
                            pow(int(i),j) % k,
                            pow(int(i),j,k)
                        )

    def test_bug643260(self):
        klasa TestRpow:
            def __rpow__(self, other):
                zwróć Nic
        Nic ** TestRpow() # Won't fail when __rpow__ invoked.  SF bug #643260.

    def test_bug705231(self):
        # -1.0 podnieśd to an integer should never blow up.  It did jeżeli the
        # platform pow() was buggy, oraz Python didn't worm around it.
        eq = self.assertEqual
        a = -1.0
        # The next two tests can still fail jeżeli the platform floor()
        # function doesn't treat all large inputs jako integers
        # test_math should also fail jeżeli that jest happening
        eq(pow(a, 1.23e167), 1.0)
        eq(pow(a, -1.23e167), 1.0)
        dla b w range(-10, 11):
            eq(pow(a, float(b)), b & 1 oraz -1.0 albo 1.0)
        dla n w range(0, 100):
            fiveto = float(5 ** n)
            # For small n, fiveto will be odd.  Eventually we run out of
            # mantissa bits, though, oraz thereafer fiveto will be even.
            expected = fiveto % 2.0 oraz -1.0 albo 1.0
            eq(pow(a, fiveto), expected)
            eq(pow(a, -fiveto), expected)
        eq(expected, 1.0)   # inaczej we didn't push fiveto to evenness

jeżeli __name__ == "__main__":
    unittest.main()
