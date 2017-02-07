zaimportuj unittest, sys

z ctypes zaimportuj *
zaimportuj _ctypes_test

ctype_types = [c_byte, c_ubyte, c_short, c_ushort, c_int, c_uint,
                 c_long, c_ulong, c_longlong, c_ulonglong, c_double, c_float]
python_types = [int, int, int, int, int, int,
                int, int, int, int, float, float]

klasa PointersTestCase(unittest.TestCase):

    def test_pointer_crash(self):

        klasa A(POINTER(c_ulong)):
            dalej

        POINTER(c_ulong)(c_ulong(22))
        # Pointer can't set contents: has no _type_
        self.assertRaises(TypeError, A, c_ulong(33))

    def test_pass_pointers(self):
        dll = CDLL(_ctypes_test.__file__)
        func = dll._testfunc_p_p
        jeżeli sizeof(c_longlong) == sizeof(c_void_p):
            func.restype = c_longlong
        inaczej:
            func.restype = c_long

        i = c_int(12345678)
##        func.argtypes = (POINTER(c_int),)
        address = func(byref(i))
        self.assertEqual(c_int.from_address(address).value, 12345678)

        func.restype = POINTER(c_int)
        res = func(pointer(i))
        self.assertEqual(res.contents.value, 12345678)
        self.assertEqual(res[0], 12345678)

    def test_change_pointers(self):
        dll = CDLL(_ctypes_test.__file__)
        func = dll._testfunc_p_p

        i = c_int(87654)
        func.restype = POINTER(c_int)
        func.argtypes = (POINTER(c_int),)

        res = func(pointer(i))
        self.assertEqual(res[0], 87654)
        self.assertEqual(res.contents.value, 87654)

        # C code: *res = 54345
        res[0] = 54345
        self.assertEqual(i.value, 54345)

        # C code:
        #   int x = 12321;
        #   res = &x
        res.contents = c_int(12321)
        self.assertEqual(i.value, 54345)

    def test_callbacks_with_pointers(self):
        # a function type receiving a pointer
        PROTOTYPE = CFUNCTYPE(c_int, POINTER(c_int))

        self.result = []

        def func(arg):
            dla i w range(10):
##                print arg[i],
                self.result.append(arg[i])
##            print
            zwróć 0
        callback = PROTOTYPE(func)

        dll = CDLL(_ctypes_test.__file__)
        # This function expects a function pointer,
        # oraz calls this przy an integer pointer jako parameter.
        # The int pointer points to a table containing the numbers 1..10
        doit = dll._testfunc_callback_with_pointer

##        i = c_int(42)
##        callback(byref(i))
##        self.assertEqual(i.value, 84)

        doit(callback)
##        print self.result
        doit(callback)
##        print self.result

    def test_basics(self):
        z operator zaimportuj delitem
        dla ct, pt w zip(ctype_types, python_types):
            i = ct(42)
            p = pointer(i)
##            print type(p.contents), ct
            self.assertIs(type(p.contents), ct)
            # p.contents jest the same jako p[0]
##            print p.contents
##            self.assertEqual(p.contents, 42)
##            self.assertEqual(p[0], 42)

            self.assertRaises(TypeError, delitem, p, 0)

    def test_from_address(self):
        z array zaimportuj array
        a = array('i', [100, 200, 300, 400, 500])
        addr = a.buffer_info()[0]

        p = POINTER(POINTER(c_int))
##        print dir(p)
##        print p.from_address
##        print p.from_address(addr)[0][0]

    def test_other(self):
        klasa Table(Structure):
            _fields_ = [("a", c_int),
                        ("b", c_int),
                        ("c", c_int)]

        pt = pointer(Table(1, 2, 3))

        self.assertEqual(pt.contents.a, 1)
        self.assertEqual(pt.contents.b, 2)
        self.assertEqual(pt.contents.c, 3)

        pt.contents.c = 33

        z ctypes zaimportuj _pointer_type_cache
        usuń _pointer_type_cache[Table]

    def test_basic(self):
        p = pointer(c_int(42))
        # Although a pointer can be indexed, it ha no length
        self.assertRaises(TypeError, len, p)
        self.assertEqual(p[0], 42)
        self.assertEqual(p.contents.value, 42)

    def test_charpp(self):
        """Test that a character pointer-to-pointer jest correctly dalejed"""
        dll = CDLL(_ctypes_test.__file__)
        func = dll._testfunc_c_p_p
        func.restype = c_char_p
        argv = (c_char_p * 2)()
        argc = c_int( 2 )
        argv[0] = b'hello'
        argv[1] = b'world'
        result = func( byref(argc), argv )
        self.assertEqual(result, b'world')

    def test_bug_1467852(self):
        # http://sourceforge.net/tracker/?func=detail&atid=532154&aid=1467852&group_id=71702
        x = c_int(5)
        dummy = []
        dla i w range(32000):
            dummy.append(c_int(i))
        y = c_int(6)
        p = pointer(x)
        pp = pointer(p)
        q = pointer(y)
        pp[0] = q         # <==
        self.assertEqual(p[0], 6)
    def test_c_void_p(self):
        # http://sourceforge.net/tracker/?func=detail&aid=1518190&group_id=5470&atid=105470
        jeżeli sizeof(c_void_p) == 4:
            self.assertEqual(c_void_p(0xFFFFFFFF).value,
                                 c_void_p(-1).value)
            self.assertEqual(c_void_p(0xFFFFFFFFFFFFFFFF).value,
                                 c_void_p(-1).value)
        albo_inaczej sizeof(c_void_p) == 8:
            self.assertEqual(c_void_p(0xFFFFFFFF).value,
                                 0xFFFFFFFF)
            self.assertEqual(c_void_p(0xFFFFFFFFFFFFFFFF).value,
                                 c_void_p(-1).value)
            self.assertEqual(c_void_p(0xFFFFFFFFFFFFFFFFFFFFFFFF).value,
                                 c_void_p(-1).value)

        self.assertRaises(TypeError, c_void_p, 3.14) # make sure floats are NOT accepted
        self.assertRaises(TypeError, c_void_p, object()) # nor other objects

    def test_pointers_bool(self):
        # NULL pointers have a boolean Nieprawda value, non-NULL pointers Prawda.
        self.assertEqual(bool(POINTER(c_int)()), Nieprawda)
        self.assertEqual(bool(pointer(c_int())), Prawda)

        self.assertEqual(bool(CFUNCTYPE(Nic)(0)), Nieprawda)
        self.assertEqual(bool(CFUNCTYPE(Nic)(42)), Prawda)

        # COM methods are boolean Prawda:
        jeżeli sys.platform == "win32":
            mth = WINFUNCTYPE(Nic)(42, "name", (), Nic)
            self.assertEqual(bool(mth), Prawda)

    def test_pointer_type_name(self):
        LargeNamedType = type('T' * 2 ** 25, (Structure,), {})
        self.assertPrawda(POINTER(LargeNamedType))

    def test_pointer_type_str_name(self):
        large_string = 'T' * 2 ** 25
        self.assertPrawda(POINTER(large_string))

jeżeli __name__ == '__main__':
    unittest.main()
