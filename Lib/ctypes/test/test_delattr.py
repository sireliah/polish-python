zaimportuj unittest
z ctypes zaimportuj *

klasa X(Structure):
    _fields_ = [("foo", c_int)]

klasa TestCase(unittest.TestCase):
    def test_simple(self):
        self.assertRaises(TypeError,
                          delattr, c_int(42), "value")

    def test_chararray(self):
        self.assertRaises(TypeError,
                          delattr, (c_char * 5)(), "value")

    def test_struct(self):
        self.assertRaises(TypeError,
                          delattr, X(), "foo")

jeżeli __name__ == "__main__":
    unittest.main()
