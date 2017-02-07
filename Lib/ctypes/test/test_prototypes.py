z ctypes zaimportuj *
z ctypes.test zaimportuj need_symbol
zaimportuj unittest

# IMPORTANT INFO:
#
# Consider this call:
#    func.restype = c_char_p
#    func(c_char_p("123"))
# It returns
#    "123"
#
# WHY IS THIS SO?
#
# argument tuple (c_char_p("123"), ) jest destroyed after the function
# func jest called, but NOT before the result jest actually built.
#
# If the arglist would be destroyed BEFORE the result has been built,
# the c_char_p("123") object would already have a zero refcount,
# oraz the pointer dalejed to (and returned by) the function would
# probably point to deallocated space.
#
# In this case, there would have to be an additional reference to the argument...

zaimportuj _ctypes_test
testdll = CDLL(_ctypes_test.__file__)

# Return machine address `a` jako a (possibly long) non-negative integer.
# Starting przy Python 2.5, id(anything) jest always non-negative, oraz
# the ctypes addressof() inherits that via PyLong_FromVoidPtr().
def positive_address(a):
    jeżeli a >= 0:
        zwróć a
    # View the bits w `a` jako unsigned instead.
    zaimportuj struct
    num_bits = struct.calcsize("P") * 8 # num bits w native machine address
    a += 1 << num_bits
    assert a >= 0
    zwróć a

def c_wbuffer(init):
    n = len(init) + 1
    zwróć (c_wchar * n)(*init)

klasa CharPointersTestCase(unittest.TestCase):

    def setUp(self):
        func = testdll._testfunc_p_p
        func.restype = c_long
        func.argtypes = Nic

    def test_paramflags(self):
        # function returns c_void_p result,
        # oraz has a required parameter named 'input'
        prototype = CFUNCTYPE(c_void_p, c_void_p)
        func = prototype(("_testfunc_p_p", testdll),
                         ((1, "input"),))

        spróbuj:
            func()
        wyjąwszy TypeError jako details:
            self.assertEqual(str(details), "required argument 'input' missing")
        inaczej:
            self.fail("TypeError nie podnieśd")

        self.assertEqual(func(Nic), Nic)
        self.assertEqual(func(input=Nic), Nic)


    def test_int_pointer_arg(self):
        func = testdll._testfunc_p_p
        jeżeli sizeof(c_longlong) == sizeof(c_void_p):
            func.restype = c_longlong
        inaczej:
            func.restype = c_long
        self.assertEqual(0, func(0))

        ci = c_int(0)

        func.argtypes = POINTER(c_int),
        self.assertEqual(positive_address(addressof(ci)),
                             positive_address(func(byref(ci))))

        func.argtypes = c_char_p,
        self.assertRaises(ArgumentError, func, byref(ci))

        func.argtypes = POINTER(c_short),
        self.assertRaises(ArgumentError, func, byref(ci))

        func.argtypes = POINTER(c_double),
        self.assertRaises(ArgumentError, func, byref(ci))

    def test_POINTER_c_char_arg(self):
        func = testdll._testfunc_p_p
        func.restype = c_char_p
        func.argtypes = POINTER(c_char),

        self.assertEqual(Nic, func(Nic))
        self.assertEqual(b"123", func(b"123"))
        self.assertEqual(Nic, func(c_char_p(Nic)))
        self.assertEqual(b"123", func(c_char_p(b"123")))

        self.assertEqual(b"123", func(c_buffer(b"123")))
        ca = c_char(b"a")
        self.assertEqual(ord(b"a"), func(pointer(ca))[0])
        self.assertEqual(ord(b"a"), func(byref(ca))[0])

    def test_c_char_p_arg(self):
        func = testdll._testfunc_p_p
        func.restype = c_char_p
        func.argtypes = c_char_p,

        self.assertEqual(Nic, func(Nic))
        self.assertEqual(b"123", func(b"123"))
        self.assertEqual(Nic, func(c_char_p(Nic)))
        self.assertEqual(b"123", func(c_char_p(b"123")))

        self.assertEqual(b"123", func(c_buffer(b"123")))
        ca = c_char(b"a")
        self.assertEqual(ord(b"a"), func(pointer(ca))[0])
        self.assertEqual(ord(b"a"), func(byref(ca))[0])

    def test_c_void_p_arg(self):
        func = testdll._testfunc_p_p
        func.restype = c_char_p
        func.argtypes = c_void_p,

        self.assertEqual(Nic, func(Nic))
        self.assertEqual(b"123", func(b"123"))
        self.assertEqual(b"123", func(c_char_p(b"123")))
        self.assertEqual(Nic, func(c_char_p(Nic)))

        self.assertEqual(b"123", func(c_buffer(b"123")))
        ca = c_char(b"a")
        self.assertEqual(ord(b"a"), func(pointer(ca))[0])
        self.assertEqual(ord(b"a"), func(byref(ca))[0])

        func(byref(c_int()))
        func(pointer(c_int()))
        func((c_int * 3)())

    @need_symbol('c_wchar_p')
    def test_c_void_p_arg_with_c_wchar_p(self):
        func = testdll._testfunc_p_p
        func.restype = c_wchar_p
        func.argtypes = c_void_p,

        self.assertEqual(Nic, func(c_wchar_p(Nic)))
        self.assertEqual("123", func(c_wchar_p("123")))

    def test_instance(self):
        func = testdll._testfunc_p_p
        func.restype = c_void_p

        klasa X:
            _as_parameter_ = Nic

        func.argtypes = c_void_p,
        self.assertEqual(Nic, func(X()))

        func.argtypes = Nic
        self.assertEqual(Nic, func(X()))

@need_symbol('c_wchar')
klasa WCharPointersTestCase(unittest.TestCase):

    def setUp(self):
        func = testdll._testfunc_p_p
        func.restype = c_int
        func.argtypes = Nic


    def test_POINTER_c_wchar_arg(self):
        func = testdll._testfunc_p_p
        func.restype = c_wchar_p
        func.argtypes = POINTER(c_wchar),

        self.assertEqual(Nic, func(Nic))
        self.assertEqual("123", func("123"))
        self.assertEqual(Nic, func(c_wchar_p(Nic)))
        self.assertEqual("123", func(c_wchar_p("123")))

        self.assertEqual("123", func(c_wbuffer("123")))
        ca = c_wchar("a")
        self.assertEqual("a", func(pointer(ca))[0])
        self.assertEqual("a", func(byref(ca))[0])

    def test_c_wchar_p_arg(self):
        func = testdll._testfunc_p_p
        func.restype = c_wchar_p
        func.argtypes = c_wchar_p,

        c_wchar_p.from_param("123")

        self.assertEqual(Nic, func(Nic))
        self.assertEqual("123", func("123"))
        self.assertEqual(Nic, func(c_wchar_p(Nic)))
        self.assertEqual("123", func(c_wchar_p("123")))

        # XXX Currently, these podnieś TypeErrors, although they shouldn't:
        self.assertEqual("123", func(c_wbuffer("123")))
        ca = c_wchar("a")
        self.assertEqual("a", func(pointer(ca))[0])
        self.assertEqual("a", func(byref(ca))[0])

klasa ArrayTest(unittest.TestCase):
    def test(self):
        func = testdll._testfunc_ai8
        func.restype = POINTER(c_int)
        func.argtypes = c_int * 8,

        func((c_int * 8)(1, 2, 3, 4, 5, 6, 7, 8))

        # This did crash before:

        def func(): dalej
        CFUNCTYPE(Nic, c_int * 3)(func)

################################################################

jeżeli __name__ == '__main__':
    unittest.main()
