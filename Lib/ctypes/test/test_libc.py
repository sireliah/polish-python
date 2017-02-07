zaimportuj unittest

z ctypes zaimportuj *
zaimportuj _ctypes_test

lib = CDLL(_ctypes_test.__file__)

def three_way_cmp(x, y):
    """Return -1 jeżeli x < y, 0 jeżeli x == y oraz 1 jeżeli x > y"""
    zwróć (x > y) - (x < y)

klasa LibTest(unittest.TestCase):
    def test_sqrt(self):
        lib.my_sqrt.argtypes = c_double,
        lib.my_sqrt.restype = c_double
        self.assertEqual(lib.my_sqrt(4.0), 2.0)
        zaimportuj math
        self.assertEqual(lib.my_sqrt(2.0), math.sqrt(2.0))

    def test_qsort(self):
        comparefunc = CFUNCTYPE(c_int, POINTER(c_char), POINTER(c_char))
        lib.my_qsort.argtypes = c_void_p, c_size_t, c_size_t, comparefunc
        lib.my_qsort.restype = Nic

        def sort(a, b):
            zwróć three_way_cmp(a[0], b[0])

        chars = create_string_buffer(b"spam, spam, oraz spam")
        lib.my_qsort(chars, len(chars)-1, sizeof(c_char), comparefunc(sort))
        self.assertEqual(chars.raw, b"   ,,aaaadmmmnpppsss\x00")

jeżeli __name__ == "__main__":
    unittest.main()
