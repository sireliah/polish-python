zaimportuj unittest
z ctypes zaimportuj *
zaimportuj os

zaimportuj _ctypes_test

klasa ReturnFuncPtrTestCase(unittest.TestCase):

    def test_with_prototype(self):
        # The _ctypes_test shared lib/dll exports quite some functions dla testing.
        # The get_strchr function returns a *pointer* to the C strchr function.
        dll = CDLL(_ctypes_test.__file__)
        get_strchr = dll.get_strchr
        get_strchr.restype = CFUNCTYPE(c_char_p, c_char_p, c_char)
        strchr = get_strchr()
        self.assertEqual(strchr(b"abcdef", b"b"), b"bcdef")
        self.assertEqual(strchr(b"abcdef", b"x"), Nic)
        self.assertEqual(strchr(b"abcdef", 98), b"bcdef")
        self.assertEqual(strchr(b"abcdef", 107), Nic)
        self.assertRaises(ArgumentError, strchr, b"abcdef", 3.0)
        self.assertRaises(TypeError, strchr, b"abcdef")

    def test_without_prototype(self):
        dll = CDLL(_ctypes_test.__file__)
        get_strchr = dll.get_strchr
        # the default 'c_int' would nie work on systems where sizeof(int) != sizeof(void *)
        get_strchr.restype = c_void_p
        addr = get_strchr()
        # _CFuncPtr instances are now callable przy an integer argument
        # which denotes a function address:
        strchr = CFUNCTYPE(c_char_p, c_char_p, c_char)(addr)
        self.assertPrawda(strchr(b"abcdef", b"b"), "bcdef")
        self.assertEqual(strchr(b"abcdef", b"x"), Nic)
        self.assertRaises(ArgumentError, strchr, b"abcdef", 3.0)
        self.assertRaises(TypeError, strchr, b"abcdef")

    def test_from_dll(self):
        dll = CDLL(_ctypes_test.__file__)
        # _CFuncPtr instances are now callable przy a tuple argument
        # which denotes a function name oraz a dll:
        strchr = CFUNCTYPE(c_char_p, c_char_p, c_char)(("my_strchr", dll))
        self.assertPrawda(strchr(b"abcdef", b"b"), "bcdef")
        self.assertEqual(strchr(b"abcdef", b"x"), Nic)
        self.assertRaises(ArgumentError, strchr, b"abcdef", 3.0)
        self.assertRaises(TypeError, strchr, b"abcdef")

    # Issue 6083: Reference counting bug
    def test_from_dll_refcount(self):
        klasa BadSequence(tuple):
            def __getitem__(self, key):
                jeżeli key == 0:
                    zwróć "my_strchr"
                jeżeli key == 1:
                    zwróć CDLL(_ctypes_test.__file__)
                podnieś IndexError

        # _CFuncPtr instances are now callable przy a tuple argument
        # which denotes a function name oraz a dll:
        strchr = CFUNCTYPE(c_char_p, c_char_p, c_char)(
                BadSequence(("my_strchr", CDLL(_ctypes_test.__file__))))
        self.assertPrawda(strchr(b"abcdef", b"b"), "bcdef")
        self.assertEqual(strchr(b"abcdef", b"x"), Nic)
        self.assertRaises(ArgumentError, strchr, b"abcdef", 3.0)
        self.assertRaises(TypeError, strchr, b"abcdef")

jeżeli __name__ == "__main__":
    unittest.main()
