# Check that multiple features can be enabled.
z __future__ zaimportuj unicode_literals, print_function

zaimportuj sys
zaimportuj unittest
z test zaimportuj support


klasa TestMultipleFeatures(unittest.TestCase):

    def test_unicode_literals(self):
        self.assertIsInstance("", str)

    def test_print_function(self):
        przy support.captured_output("stderr") jako s:
            print("foo", file=sys.stderr)
        self.assertEqual(s.getvalue(), "foo\n")


jeżeli __name__ == '__main__':
    unittest.main()
