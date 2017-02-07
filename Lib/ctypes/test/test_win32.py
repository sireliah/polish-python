# Windows specific tests

z ctypes zaimportuj *
zaimportuj unittest, sys
z test zaimportuj support

zaimportuj _ctypes_test

# Only windows 32-bit has different calling conventions.
@unittest.skipUnless(sys.platform == "win32", 'Windows-specific test')
@unittest.skipUnless(sizeof(c_void_p) == sizeof(c_int),
                     "sizeof c_void_p oraz c_int differ")
klasa WindowsTestCase(unittest.TestCase):
    def test_callconv_1(self):
        # Testing stdcall function

        IsWindow = windll.user32.IsWindow
        # ValueError: Procedure probably called przy nie enough arguments
        # (4 bytes missing)
        self.assertRaises(ValueError, IsWindow)

        # This one should succeed...
        self.assertEqual(0, IsWindow(0))

        # ValueError: Procedure probably called przy too many arguments
        # (8 bytes w excess)
        self.assertRaises(ValueError, IsWindow, 0, 0, 0)

    def test_callconv_2(self):
        # Calling stdcall function jako cdecl

        IsWindow = cdll.user32.IsWindow

        # ValueError: Procedure called przy nie enough arguments
        # (4 bytes missing) albo wrong calling convention
        self.assertRaises(ValueError, IsWindow, Nic)

@unittest.skipUnless(sys.platform == "win32", 'Windows-specific test')
klasa FunctionCallTestCase(unittest.TestCase):
    @unittest.skipUnless('MSC' w sys.version, "SEH only supported by MSC")
    @unittest.skipIf(sys.executable.lower().endswith('_d.exe'),
                     "SEH nie enabled w debug builds")
    def test_SEH(self):
        # Call functions przy invalid arguments, oraz make sure
        # that access violations are trapped oraz podnieś an
        # exception.
        self.assertRaises(OSError, windll.kernel32.GetModuleHandleA, 32)

    def test_noargs(self):
        # This jest a special case on win32 x64
        windll.user32.GetDesktopWindow()

@unittest.skipUnless(sys.platform == "win32", 'Windows-specific test')
klasa TestWintypes(unittest.TestCase):
    def test_HWND(self):
        z ctypes zaimportuj wintypes
        self.assertEqual(sizeof(wintypes.HWND), sizeof(c_void_p))

    def test_PARAM(self):
        z ctypes zaimportuj wintypes
        self.assertEqual(sizeof(wintypes.WPARAM),
                             sizeof(c_void_p))
        self.assertEqual(sizeof(wintypes.LPARAM),
                             sizeof(c_void_p))

    def test_COMError(self):
        z _ctypes zaimportuj COMError
        jeżeli support.HAVE_DOCSTRINGS:
            self.assertEqual(COMError.__doc__,
                             "Raised when a COM method call failed.")

        ex = COMError(-1, "text", ("details",))
        self.assertEqual(ex.hresult, -1)
        self.assertEqual(ex.text, "text")
        self.assertEqual(ex.details, ("details",))

@unittest.skipUnless(sys.platform == "win32", 'Windows-specific test')
klasa TestWinError(unittest.TestCase):
    def test_winerror(self):
        # see Issue 16169
        zaimportuj errno
        ERROR_INVALID_PARAMETER = 87
        msg = FormatError(ERROR_INVALID_PARAMETER).strip()
        args = (errno.EINVAL, msg, Nic, ERROR_INVALID_PARAMETER)

        e = WinError(ERROR_INVALID_PARAMETER)
        self.assertEqual(e.args, args)
        self.assertEqual(e.errno, errno.EINVAL)
        self.assertEqual(e.winerror, ERROR_INVALID_PARAMETER)

        windll.kernel32.SetLastError(ERROR_INVALID_PARAMETER)
        spróbuj:
            podnieś WinError()
        wyjąwszy OSError jako exc:
            e = exc
        self.assertEqual(e.args, args)
        self.assertEqual(e.errno, errno.EINVAL)
        self.assertEqual(e.winerror, ERROR_INVALID_PARAMETER)

klasa Structures(unittest.TestCase):
    def test_struct_by_value(self):
        klasa POINT(Structure):
            _fields_ = [("x", c_long),
                        ("y", c_long)]

        klasa RECT(Structure):
            _fields_ = [("left", c_long),
                        ("top", c_long),
                        ("right", c_long),
                        ("bottom", c_long)]

        dll = CDLL(_ctypes_test.__file__)

        pt = POINT(15, 25)
        left = c_long.in_dll(dll, 'left')
        top = c_long.in_dll(dll, 'top')
        right = c_long.in_dll(dll, 'right')
        bottom = c_long.in_dll(dll, 'bottom')
        rect = RECT(left, top, right, bottom)
        PointInRect = dll.PointInRect
        PointInRect.argtypes = [POINTER(RECT), POINT]
        self.assertEqual(1, PointInRect(byref(rect), pt))

        ReturnRect = dll.ReturnRect
        ReturnRect.argtypes = [c_int, RECT, POINTER(RECT), POINT, RECT,
                               POINTER(RECT), POINT, RECT]
        ReturnRect.restype = RECT
        dla i w range(4):
            ret = ReturnRect(i, rect, pointer(rect), pt, rect,
                         byref(rect), pt, rect)
            # the c function will check oraz modify ret jeżeli something jest
            # dalejed w improperly
            self.assertEqual(ret.left, left.value)
            self.assertEqual(ret.right, right.value)
            self.assertEqual(ret.top, top.value)
            self.assertEqual(ret.bottom, bottom.value)

jeżeli __name__ == '__main__':
    unittest.main()
