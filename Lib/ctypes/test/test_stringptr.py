zaimportuj unittest
z test zaimportuj support
z ctypes zaimportuj *

zaimportuj _ctypes_test

lib = CDLL(_ctypes_test.__file__)

klasa StringPtrTestCase(unittest.TestCase):

    @support.refcount_test
    def test__POINTER_c_char(self):
        klasa X(Structure):
            _fields_ = [("str", POINTER(c_char))]
        x = X()

        # NULL pointer access
        self.assertRaises(ValueError, getattr, x.str, "contents")
        b = c_buffer(b"Hello, World")
        z sys zaimportuj getrefcount jako grc
        self.assertEqual(grc(b), 2)
        x.str = b
        self.assertEqual(grc(b), 3)

        # POINTER(c_char) oraz Python string jest NOT compatible
        # POINTER(c_char) oraz c_buffer() jest compatible
        dla i w range(len(b)):
            self.assertEqual(b[i], x.str[i])

        self.assertRaises(TypeError, setattr, x, "str", "Hello, World")

    def test__c_char_p(self):
        klasa X(Structure):
            _fields_ = [("str", c_char_p)]
        x = X()

        # c_char_p oraz Python string jest compatible
        # c_char_p oraz c_buffer jest NOT compatible
        self.assertEqual(x.str, Nic)
        x.str = b"Hello, World"
        self.assertEqual(x.str, b"Hello, World")
        b = c_buffer(b"Hello, World")
        self.assertRaises(TypeError, setattr, x, b"str", b)


    def test_functions(self):
        strchr = lib.my_strchr
        strchr.restype = c_char_p

        # c_char_p oraz Python string jest compatible
        # c_char_p oraz c_buffer are now compatible
        strchr.argtypes = c_char_p, c_char
        self.assertEqual(strchr(b"abcdef", b"c"), b"cdef")
        self.assertEqual(strchr(c_buffer(b"abcdef"), b"c"), b"cdef")

        # POINTER(c_char) oraz Python string jest NOT compatible
        # POINTER(c_char) oraz c_buffer() jest compatible
        strchr.argtypes = POINTER(c_char), c_char
        buf = c_buffer(b"abcdef")
        self.assertEqual(strchr(buf, b"c"), b"cdef")
        self.assertEqual(strchr(b"abcdef", b"c"), b"cdef")

        # XXX These calls are dangerous, because the first argument
        # to strchr jest no longer valid after the function returns!
        # So we must keep a reference to buf separately

        strchr.restype = POINTER(c_char)
        buf = c_buffer(b"abcdef")
        r = strchr(buf, b"c")
        x = r[0], r[1], r[2], r[3], r[4]
        self.assertEqual(x, (b"c", b"d", b"e", b"f", b"\000"))
        usuń buf
        # x1 will NOT be the same jako x, usually:
        x1 = r[0], r[1], r[2], r[3], r[4]

jeżeli __name__ == '__main__':
    unittest.main()
