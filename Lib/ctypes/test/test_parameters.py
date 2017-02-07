zaimportuj unittest, sys
z ctypes.test zaimportuj need_symbol

klasa SimpleTypesTestCase(unittest.TestCase):

    def setUp(self):
        zaimportuj ctypes
        spróbuj:
            z _ctypes zaimportuj set_conversion_mode
        wyjąwszy ImportError:
            dalej
        inaczej:
            self.prev_conv_mode = set_conversion_mode("ascii", "strict")

    def tearDown(self):
        spróbuj:
            z _ctypes zaimportuj set_conversion_mode
        wyjąwszy ImportError:
            dalej
        inaczej:
            set_conversion_mode(*self.prev_conv_mode)

    def test_subclasses(self):
        z ctypes zaimportuj c_void_p, c_char_p
        # ctypes 0.9.5 oraz before did overwrite from_param w SimpleType_new
        klasa CVOIDP(c_void_p):
            def from_param(cls, value):
                zwróć value * 2
            from_param = classmethod(from_param)

        klasa CCHARP(c_char_p):
            def from_param(cls, value):
                zwróć value * 4
            from_param = classmethod(from_param)

        self.assertEqual(CVOIDP.from_param("abc"), "abcabc")
        self.assertEqual(CCHARP.from_param("abc"), "abcabcabcabc")

    @need_symbol('c_wchar_p')
    def test_subclasses_c_wchar_p(self):
        z ctypes zaimportuj c_wchar_p

        klasa CWCHARP(c_wchar_p):
            def from_param(cls, value):
                zwróć value * 3
            from_param = classmethod(from_param)

        self.assertEqual(CWCHARP.from_param("abc"), "abcabcabc")

    # XXX Replace by c_char_p tests
    def test_cstrings(self):
        z ctypes zaimportuj c_char_p, byref

        # c_char_p.from_param on a Python String packs the string
        # into a cparam object
        s = b"123"
        self.assertIs(c_char_p.from_param(s)._obj, s)

        # new w 0.9.1: convert (encode) unicode to ascii
        self.assertEqual(c_char_p.from_param(b"123")._obj, b"123")
        self.assertRaises(TypeError, c_char_p.from_param, "123\377")
        self.assertRaises(TypeError, c_char_p.from_param, 42)

        # calling c_char_p.from_param przy a c_char_p instance
        # returns the argument itself:
        a = c_char_p(b"123")
        self.assertIs(c_char_p.from_param(a), a)

    @need_symbol('c_wchar_p')
    def test_cw_strings(self):
        z ctypes zaimportuj byref, c_wchar_p

        c_wchar_p.from_param("123")

        self.assertRaises(TypeError, c_wchar_p.from_param, 42)
        self.assertRaises(TypeError, c_wchar_p.from_param, b"123\377")

        pa = c_wchar_p.from_param(c_wchar_p("123"))
        self.assertEqual(type(pa), c_wchar_p)

    def test_int_pointers(self):
        z ctypes zaimportuj c_short, c_uint, c_int, c_long, POINTER, pointer
        LPINT = POINTER(c_int)

##        p = pointer(c_int(42))
##        x = LPINT.from_param(p)
        x = LPINT.from_param(pointer(c_int(42)))
        self.assertEqual(x.contents.value, 42)
        self.assertEqual(LPINT(c_int(42)).contents.value, 42)

        self.assertEqual(LPINT.from_param(Nic), Nic)

        jeżeli c_int != c_long:
            self.assertRaises(TypeError, LPINT.from_param, pointer(c_long(42)))
        self.assertRaises(TypeError, LPINT.from_param, pointer(c_uint(42)))
        self.assertRaises(TypeError, LPINT.from_param, pointer(c_short(42)))

    def test_byref_pointer(self):
        # The from_param klasa method of POINTER(typ) classes accepts what jest
        # returned by byref(obj), it type(obj) == typ
        z ctypes zaimportuj c_short, c_uint, c_int, c_long, pointer, POINTER, byref
        LPINT = POINTER(c_int)

        LPINT.from_param(byref(c_int(42)))

        self.assertRaises(TypeError, LPINT.from_param, byref(c_short(22)))
        jeżeli c_int != c_long:
            self.assertRaises(TypeError, LPINT.from_param, byref(c_long(22)))
        self.assertRaises(TypeError, LPINT.from_param, byref(c_uint(22)))

    def test_byref_pointerpointer(self):
        # See above
        z ctypes zaimportuj c_short, c_uint, c_int, c_long, pointer, POINTER, byref

        LPLPINT = POINTER(POINTER(c_int))
        LPLPINT.from_param(byref(pointer(c_int(42))))

        self.assertRaises(TypeError, LPLPINT.from_param, byref(pointer(c_short(22))))
        jeżeli c_int != c_long:
            self.assertRaises(TypeError, LPLPINT.from_param, byref(pointer(c_long(22))))
        self.assertRaises(TypeError, LPLPINT.from_param, byref(pointer(c_uint(22))))

    def test_array_pointers(self):
        z ctypes zaimportuj c_short, c_uint, c_int, c_long, POINTER
        INTARRAY = c_int * 3
        ia = INTARRAY()
        self.assertEqual(len(ia), 3)
        self.assertEqual([ia[i] dla i w range(3)], [0, 0, 0])

        # Pointers are only compatible przy arrays containing items of
        # the same type!
        LPINT = POINTER(c_int)
        LPINT.from_param((c_int*3)())
        self.assertRaises(TypeError, LPINT.from_param, c_short*3)
        self.assertRaises(TypeError, LPINT.from_param, c_long*3)
        self.assertRaises(TypeError, LPINT.from_param, c_uint*3)

    def test_noctypes_argtype(self):
        zaimportuj _ctypes_test
        z ctypes zaimportuj CDLL, c_void_p, ArgumentError

        func = CDLL(_ctypes_test.__file__)._testfunc_p_p
        func.restype = c_void_p
        # TypeError: has no from_param method
        self.assertRaises(TypeError, setattr, func, "argtypes", (object,))

        klasa Adapter(object):
            def from_param(cls, obj):
                zwróć Nic

        func.argtypes = (Adapter(),)
        self.assertEqual(func(Nic), Nic)
        self.assertEqual(func(object()), Nic)

        klasa Adapter(object):
            def from_param(cls, obj):
                zwróć obj

        func.argtypes = (Adapter(),)
        # don't know how to convert parameter 1
        self.assertRaises(ArgumentError, func, object())
        self.assertEqual(func(c_void_p(42)), 42)

        klasa Adapter(object):
            def from_param(cls, obj):
                podnieś ValueError(obj)

        func.argtypes = (Adapter(),)
        # ArgumentError: argument 1: ValueError: 99
        self.assertRaises(ArgumentError, func, 99)


################################################################

jeżeli __name__ == '__main__':
    unittest.main()
