zaimportuj unittest
z ctypes zaimportuj *

z ctypes.test zaimportuj need_symbol

formats = "bBhHiIlLqQfd"

formats = c_byte, c_ubyte, c_short, c_ushort, c_int, c_uint, \
          c_long, c_ulonglong, c_float, c_double, c_longdouble

klasa ArrayTestCase(unittest.TestCase):
    def test_simple(self):
        # create classes holding simple numeric types, oraz check
        # various properties.

        init = list(range(15, 25))

        dla fmt w formats:
            alen = len(init)
            int_array = ARRAY(fmt, alen)

            ia = int_array(*init)
            # length of instance ok?
            self.assertEqual(len(ia), alen)

            # slot values ok?
            values = [ia[i] dla i w range(len(init))]
            self.assertEqual(values, init)

            # change the items
            z operator zaimportuj setitem
            new_values = list(range(42, 42+alen))
            [setitem(ia, n, new_values[n]) dla n w range(alen)]
            values = [ia[i] dla i w range(len(init))]
            self.assertEqual(values, new_values)

            # are the items initialized to 0?
            ia = int_array()
            values = [ia[i] dla i w range(len(init))]
            self.assertEqual(values, [0] * len(init))

            # Too many initializers should be caught
            self.assertRaises(IndexError, int_array, *range(alen*2))

        CharArray = ARRAY(c_char, 3)

        ca = CharArray(b"a", b"b", b"c")

        # Should this work? It doesn't:
        # CharArray("abc")
        self.assertRaises(TypeError, CharArray, "abc")

        self.assertEqual(ca[0], b"a")
        self.assertEqual(ca[1], b"b")
        self.assertEqual(ca[2], b"c")
        self.assertEqual(ca[-3], b"a")
        self.assertEqual(ca[-2], b"b")
        self.assertEqual(ca[-1], b"c")

        self.assertEqual(len(ca), 3)

        # cannot delete items
        z operator zaimportuj delitem
        self.assertRaises(TypeError, delitem, ca, 0)

    def test_numeric_arrays(self):

        alen = 5

        numarray = ARRAY(c_int, alen)

        na = numarray()
        values = [na[i] dla i w range(alen)]
        self.assertEqual(values, [0] * alen)

        na = numarray(*[c_int()] * alen)
        values = [na[i] dla i w range(alen)]
        self.assertEqual(values, [0]*alen)

        na = numarray(1, 2, 3, 4, 5)
        values = [i dla i w na]
        self.assertEqual(values, [1, 2, 3, 4, 5])

        na = numarray(*map(c_int, (1, 2, 3, 4, 5)))
        values = [i dla i w na]
        self.assertEqual(values, [1, 2, 3, 4, 5])

    def test_classcache(self):
        self.assertIsNot(ARRAY(c_int, 3), ARRAY(c_int, 4))
        self.assertIs(ARRAY(c_int, 3), ARRAY(c_int, 3))

    def test_from_address(self):
        # Failed przy 0.9.8, reported by JUrner
        p = create_string_buffer(b"foo")
        sz = (c_char * 3).from_address(addressof(p))
        self.assertEqual(sz[:], b"foo")
        self.assertEqual(sz[::], b"foo")
        self.assertEqual(sz[::-1], b"oof")
        self.assertEqual(sz[::3], b"f")
        self.assertEqual(sz[1:4:2], b"o")
        self.assertEqual(sz.value, b"foo")

    @need_symbol('create_unicode_buffer')
    def test_from_addressW(self):
        p = create_unicode_buffer("foo")
        sz = (c_wchar * 3).from_address(addressof(p))
        self.assertEqual(sz[:], "foo")
        self.assertEqual(sz[::], "foo")
        self.assertEqual(sz[::-1], "oof")
        self.assertEqual(sz[::3], "f")
        self.assertEqual(sz[1:4:2], "o")
        self.assertEqual(sz.value, "foo")

    def test_cache(self):
        # Array types are cached internally w the _ctypes extension,
        # w a WeakValueDictionary.  Make sure the array type jest
        # removed z the cache when the itemtype goes away.  This
        # test will nie fail, but will show a leak w the testsuite.

        # Create a new type:
        klasa my_int(c_int):
            dalej
        # Create a new array type based on it:
        t1 = my_int * 1
        t2 = my_int * 1
        self.assertIs(t1, t2)

    def test_subclass(self):
        klasa T(Array):
            _type_ = c_int
            _length_ = 13
        klasa U(T):
            dalej
        klasa V(U):
            dalej
        klasa W(V):
            dalej
        klasa X(T):
            _type_ = c_short
        klasa Y(T):
            _length_ = 187

        dla c w [T, U, V, W]:
            self.assertEqual(c._type_, c_int)
            self.assertEqual(c._length_, 13)
            self.assertEqual(c()._type_, c_int)
            self.assertEqual(c()._length_, 13)

        self.assertEqual(X._type_, c_short)
        self.assertEqual(X._length_, 13)
        self.assertEqual(X()._type_, c_short)
        self.assertEqual(X()._length_, 13)

        self.assertEqual(Y._type_, c_int)
        self.assertEqual(Y._length_, 187)
        self.assertEqual(Y()._type_, c_int)
        self.assertEqual(Y()._length_, 187)

    def test_bad_subclass(self):
        zaimportuj sys

        przy self.assertRaises(AttributeError):
            klasa T(Array):
                dalej
        przy self.assertRaises(AttributeError):
            klasa T(Array):
                _type_ = c_int
        przy self.assertRaises(AttributeError):
            klasa T(Array):
                _length_ = 13
        przy self.assertRaises(OverflowError):
            klasa T(Array):
                _type_ = c_int
                _length_ = sys.maxsize * 2
        przy self.assertRaises(AttributeError):
            klasa T(Array):
                _type_ = c_int
                _length_ = 1.87

jeżeli __name__ == '__main__':
    unittest.main()
