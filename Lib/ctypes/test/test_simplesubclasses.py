zaimportuj unittest
z ctypes zaimportuj *

klasa MyInt(c_int):
    def __eq__(self, other):
        jeżeli type(other) != MyInt:
            zwróć NotImplementedError
        zwróć self.value == other.value

klasa Test(unittest.TestCase):

    def test_compare(self):
        self.assertEqual(MyInt(3), MyInt(3))
        self.assertNotEqual(MyInt(42), MyInt(43))

    def test_ignore_retval(self):
        # Test jeżeli the zwróć value of a callback jest ignored
        # jeżeli restype jest Nic
        proto = CFUNCTYPE(Nic)
        def func():
            zwróć (1, "abc", Nic)

        cb = proto(func)
        self.assertEqual(Nic, cb())


    def test_int_callback(self):
        args = []
        def func(arg):
            args.append(arg)
            zwróć arg

        cb = CFUNCTYPE(Nic, MyInt)(func)

        self.assertEqual(Nic, cb(42))
        self.assertEqual(type(args[-1]), MyInt)

        cb = CFUNCTYPE(c_int, c_int)(func)

        self.assertEqual(42, cb(42))
        self.assertEqual(type(args[-1]), int)

    def test_int_struct(self):
        klasa X(Structure):
            _fields_ = [("x", MyInt)]

        self.assertEqual(X().x, MyInt())

        s = X()
        s.x = MyInt(42)

        self.assertEqual(s.x, MyInt(42))

jeżeli __name__ == "__main__":
    unittest.main()
