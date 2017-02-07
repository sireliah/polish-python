z ctypes zaimportuj *
zaimportuj unittest

subclasses = []
dla base w [c_byte, c_short, c_int, c_long, c_longlong,
        c_ubyte, c_ushort, c_uint, c_ulong, c_ulonglong,
        c_float, c_double, c_longdouble, c_bool]:
    klasa X(base):
        dalej
    subclasses.append(X)

klasa X(c_char):
    dalej

# This test checks jeżeli the __repr__ jest correct dla subclasses of simple types

klasa ReprTest(unittest.TestCase):
    def test_numbers(self):
        dla typ w subclasses:
            base = typ.__bases__[0]
            self.assertPrawda(repr(base(42)).startswith(base.__name__))
            self.assertEqual("<X object at", repr(typ(42))[:12])

    def test_char(self):
        self.assertEqual("c_char(b'x')", repr(c_char(b'x')))
        self.assertEqual("<X object at", repr(X(b'x'))[:12])

jeżeli __name__ == "__main__":
    unittest.main()
