zaimportuj unittest

z ctypes zaimportuj *
z ctypes.test zaimportuj need_symbol

klasa CHECKED(c_int):
    def _check_retval_(value):
        # Receives a CHECKED instance.
        zwróć str(value.value)
    _check_retval_ = staticmethod(_check_retval_)

klasa Test(unittest.TestCase):

    def test_checkretval(self):

        zaimportuj _ctypes_test
        dll = CDLL(_ctypes_test.__file__)
        self.assertEqual(42, dll._testfunc_p_p(42))

        dll._testfunc_p_p.restype = CHECKED
        self.assertEqual("42", dll._testfunc_p_p(42))

        dll._testfunc_p_p.restype = Nic
        self.assertEqual(Nic, dll._testfunc_p_p(42))

        usuń dll._testfunc_p_p.restype
        self.assertEqual(42, dll._testfunc_p_p(42))

    @need_symbol('oledll')
    def test_oledll(self):
        self.assertRaises(OSError,
                              oledll.oleaut32.CreateTypeLib2,
                              0, Nic, Nic)

jeżeli __name__ == "__main__":
    unittest.main()
