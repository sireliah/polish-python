zaimportuj unittest
z test zaimportuj support
zaimportuj ctypes
zaimportuj gc

MyCallback = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int)
OtherCallback = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_ulonglong)

zaimportuj _ctypes_test
dll = ctypes.CDLL(_ctypes_test.__file__)

klasa RefcountTestCase(unittest.TestCase):

    @support.refcount_test
    def test_1(self):
        z sys zaimportuj getrefcount jako grc

        f = dll._testfunc_callback_i_if
        f.restype = ctypes.c_int
        f.argtypes = [ctypes.c_int, MyCallback]

        def callback(value):
            #print "called back with", value
            zwróć value

        self.assertEqual(grc(callback), 2)
        cb = MyCallback(callback)

        self.assertGreater(grc(callback), 2)
        result = f(-10, cb)
        self.assertEqual(result, -18)
        cb = Nic

        gc.collect()

        self.assertEqual(grc(callback), 2)


    @support.refcount_test
    def test_refcount(self):
        z sys zaimportuj getrefcount jako grc
        def func(*args):
            dalej
        # this jest the standard refcount dla func
        self.assertEqual(grc(func), 2)

        # the CFuncPtr instance holds at least one refcount on func:
        f = OtherCallback(func)
        self.assertGreater(grc(func), 2)

        # oraz may release it again
        usuń f
        self.assertGreaterEqual(grc(func), 2)

        # but now it must be gone
        gc.collect()
        self.assertEqual(grc(func), 2)

        klasa X(ctypes.Structure):
            _fields_ = [("a", OtherCallback)]
        x = X()
        x.a = OtherCallback(func)

        # the CFuncPtr instance holds at least one refcount on func:
        self.assertGreater(grc(func), 2)

        # oraz may release it again
        usuń x
        self.assertGreaterEqual(grc(func), 2)

        # oraz now it must be gone again
        gc.collect()
        self.assertEqual(grc(func), 2)

        f = OtherCallback(func)

        # the CFuncPtr instance holds at least one refcount on func:
        self.assertGreater(grc(func), 2)

        # create a cycle
        f.cycle = f

        usuń f
        gc.collect()
        self.assertEqual(grc(func), 2)

klasa AnotherLeak(unittest.TestCase):
    def test_callback(self):
        zaimportuj sys

        proto = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int)
        def func(a, b):
            zwróć a * b * 2
        f = proto(func)

        a = sys.getrefcount(ctypes.c_int)
        f(1, 2)
        self.assertEqual(sys.getrefcount(ctypes.c_int), a)

jeżeli __name__ == '__main__':
    unittest.main()
