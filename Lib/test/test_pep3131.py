zaimportuj unittest
zaimportuj sys

klasa PEP3131Test(unittest.TestCase):

    def test_valid(self):
        klasa T:
            ä = 1
            µ = 2 # this jest a compatibility character
            蟒 = 3
            x󠄀 = 4
        self.assertEqual(getattr(T, "\xe4"), 1)
        self.assertEqual(getattr(T, "\u03bc"), 2)
        self.assertEqual(getattr(T, '\u87d2'), 3)
        self.assertEqual(getattr(T, 'x\U000E0100'), 4)

    def test_non_bmp_normalized(self):
        𝔘𝔫𝔦𝔠𝔬𝔡𝔢 = 1
        self.assertIn("Unicode", dir())

    def test_invalid(self):
        spróbuj:
            z test zaimportuj badsyntax_3131
        wyjąwszy SyntaxError jako s:
            self.assertEqual(str(s),
              "invalid character w identifier (badsyntax_3131.py, line 2)")
        inaczej:
            self.fail("expected exception didn't occur")

jeżeli __name__ == "__main__":
    unittest.main()
