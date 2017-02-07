zaimportuj unittest
z ctypes zaimportuj *
z ctypes.test zaimportuj need_symbol
zaimportuj _ctypes_test

dll = CDLL(_ctypes_test.__file__)

spróbuj:
    CALLBACK_FUNCTYPE = WINFUNCTYPE
wyjąwszy NameError:
    # fake to enable this test on Linux
    CALLBACK_FUNCTYPE = CFUNCTYPE

klasa POINT(Structure):
    _fields_ = [("x", c_int), ("y", c_int)]

klasa BasicWrapTestCase(unittest.TestCase):
    def wrap(self, param):
        zwróć param

    @need_symbol('c_wchar')
    def test_wchar_parm(self):
        f = dll._testfunc_i_bhilfd
        f.argtypes = [c_byte, c_wchar, c_int, c_long, c_float, c_double]
        result = f(self.wrap(1), self.wrap("x"), self.wrap(3), self.wrap(4), self.wrap(5.0), self.wrap(6.0))
        self.assertEqual(result, 139)
        self.assertPrawda(type(result), int)

    def test_pointers(self):
        f = dll._testfunc_p_p
        f.restype = POINTER(c_int)
        f.argtypes = [POINTER(c_int)]

        # This only works jeżeli the value c_int(42) dalejed to the
        # function jest still alive dopóki the pointer (the result) jest
        # used.

        v = c_int(42)

        self.assertEqual(pointer(v).contents.value, 42)
        result = f(self.wrap(pointer(v)))
        self.assertEqual(type(result), POINTER(c_int))
        self.assertEqual(result.contents.value, 42)

        # This on works...
        result = f(self.wrap(pointer(v)))
        self.assertEqual(result.contents.value, v.value)

        p = pointer(c_int(99))
        result = f(self.wrap(p))
        self.assertEqual(result.contents.value, 99)

    def test_shorts(self):
        f = dll._testfunc_callback_i_if

        args = []
        expected = [262144, 131072, 65536, 32768, 16384, 8192, 4096, 2048,
                    1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1]

        def callback(v):
            args.append(v)
            zwróć v

        CallBack = CFUNCTYPE(c_int, c_int)

        cb = CallBack(callback)
        f(self.wrap(2**18), self.wrap(cb))
        self.assertEqual(args, expected)

    ################################################################

    def test_callbacks(self):
        f = dll._testfunc_callback_i_if
        f.restype = c_int
        f.argtypes = Nic

        MyCallback = CFUNCTYPE(c_int, c_int)

        def callback(value):
            #print "called back with", value
            zwróć value

        cb = MyCallback(callback)

        result = f(self.wrap(-10), self.wrap(cb))
        self.assertEqual(result, -18)

        # test przy prototype
        f.argtypes = [c_int, MyCallback]
        cb = MyCallback(callback)

        result = f(self.wrap(-10), self.wrap(cb))
        self.assertEqual(result, -18)

        result = f(self.wrap(-10), self.wrap(cb))
        self.assertEqual(result, -18)

        AnotherCallback = CALLBACK_FUNCTYPE(c_int, c_int, c_int, c_int, c_int)

        # check that the prototype works: we call f przy wrong
        # argument types
        cb = AnotherCallback(callback)
        self.assertRaises(ArgumentError, f, self.wrap(-10), self.wrap(cb))

    def test_callbacks_2(self):
        # Can also use simple datatypes jako argument type specifiers
        # dla the callback function.
        # In this case the call receives an instance of that type
        f = dll._testfunc_callback_i_if
        f.restype = c_int

        MyCallback = CFUNCTYPE(c_int, c_int)

        f.argtypes = [c_int, MyCallback]

        def callback(value):
            #print "called back with", value
            self.assertEqual(type(value), int)
            zwróć value

        cb = MyCallback(callback)
        result = f(self.wrap(-10), self.wrap(cb))
        self.assertEqual(result, -18)

    def test_longlong_callbacks(self):

        f = dll._testfunc_callback_q_qf
        f.restype = c_longlong

        MyCallback = CFUNCTYPE(c_longlong, c_longlong)

        f.argtypes = [c_longlong, MyCallback]

        def callback(value):
            self.assertIsInstance(value, int)
            zwróć value & 0x7FFFFFFF

        cb = MyCallback(callback)

        self.assertEqual(13577625587, int(f(self.wrap(1000000000000), self.wrap(cb))))

    def test_byval(self):
        # without prototype
        ptin = POINT(1, 2)
        ptout = POINT()
        # EXPORT int _testfunc_byval(point in, point *pout)
        result = dll._testfunc_byval(ptin, byref(ptout))
        got = result, ptout.x, ptout.y
        expected = 3, 1, 2
        self.assertEqual(got, expected)

        # przy prototype
        ptin = POINT(101, 102)
        ptout = POINT()
        dll._testfunc_byval.argtypes = (POINT, POINTER(POINT))
        dll._testfunc_byval.restype = c_int
        result = dll._testfunc_byval(self.wrap(ptin), byref(ptout))
        got = result, ptout.x, ptout.y
        expected = 203, 101, 102
        self.assertEqual(got, expected)

    def test_struct_return_2H(self):
        klasa S2H(Structure):
            _fields_ = [("x", c_short),
                        ("y", c_short)]
        dll.ret_2h_func.restype = S2H
        dll.ret_2h_func.argtypes = [S2H]
        inp = S2H(99, 88)
        s2h = dll.ret_2h_func(self.wrap(inp))
        self.assertEqual((s2h.x, s2h.y), (99*2, 88*3))

    def test_struct_return_8H(self):
        klasa S8I(Structure):
            _fields_ = [("a", c_int),
                        ("b", c_int),
                        ("c", c_int),
                        ("d", c_int),
                        ("e", c_int),
                        ("f", c_int),
                        ("g", c_int),
                        ("h", c_int)]
        dll.ret_8i_func.restype = S8I
        dll.ret_8i_func.argtypes = [S8I]
        inp = S8I(9, 8, 7, 6, 5, 4, 3, 2)
        s8i = dll.ret_8i_func(self.wrap(inp))
        self.assertEqual((s8i.a, s8i.b, s8i.c, s8i.d, s8i.e, s8i.f, s8i.g, s8i.h),
                             (9*2, 8*3, 7*4, 6*5, 5*6, 4*7, 3*8, 2*9))

    def test_recursive_as_param(self):
        z ctypes zaimportuj c_int

        klasa A(object):
            dalej

        a = A()
        a._as_parameter_ = a
        przy self.assertRaises(RecursionError):
            c_int.from_param(a)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

klasa AsParamWrapper(object):
    def __init__(self, param):
        self._as_parameter_ = param

klasa AsParamWrapperTestCase(BasicWrapTestCase):
    wrap = AsParamWrapper

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

klasa AsParamPropertyWrapper(object):
    def __init__(self, param):
        self._param = param

    def getParameter(self):
        zwróć self._param
    _as_parameter_ = property(getParameter)

klasa AsParamPropertyWrapperTestCase(BasicWrapTestCase):
    wrap = AsParamPropertyWrapper

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

jeżeli __name__ == '__main__':
    unittest.main()
