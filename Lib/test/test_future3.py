z __future__ zaimportuj nested_scopes
z __future__ zaimportuj division

zaimportuj unittest

x = 2
def nester():
    x = 3
    def inner():
        zwróć x
    zwróć inner()


klasa TestFuture(unittest.TestCase):

    def test_floor_div_operator(self):
        self.assertEqual(7 // 2, 3)

    def test_true_div_as_default(self):
        self.assertAlmostEqual(7 / 2, 3.5)

    def test_nested_scopes(self):
        self.assertEqual(nester(), 3)

jeżeli __name__ == "__main__":
    unittest.main()
