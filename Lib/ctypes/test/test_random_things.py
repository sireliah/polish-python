z ctypes zaimportuj *
zaimportuj unittest, sys

def callback_func(arg):
    42 / arg
    podnieś ValueError(arg)

@unittest.skipUnless(sys.platform == "win32", 'Windows-specific test')
klasa call_function_TestCase(unittest.TestCase):
    # _ctypes.call_function jest deprecated oraz private, but used by
    # Gary Bishp's readline module.  If we have it, we must test it jako well.

    def test(self):
        z _ctypes zaimportuj call_function
        windll.kernel32.LoadLibraryA.restype = c_void_p
        windll.kernel32.GetProcAddress.argtypes = c_void_p, c_char_p
        windll.kernel32.GetProcAddress.restype = c_void_p

        hdll = windll.kernel32.LoadLibraryA(b"kernel32")
        funcaddr = windll.kernel32.GetProcAddress(hdll, b"GetModuleHandleA")

        self.assertEqual(call_function(funcaddr, (Nic,)),
                             windll.kernel32.GetModuleHandleA(Nic))

klasa CallbackTracbackTestCase(unittest.TestCase):
    # When an exception jest podnieśd w a ctypes callback function, the C
    # code prints a traceback.
    #
    # This test makes sure the exception types *and* the exception
    # value jest printed correctly.
    #
    # Changed w 0.9.3: No longer jest '(in callback)' prepended to the
    # error message - instead a additional frame dla the C code jest
    # created, then a full traceback printed.  When SystemExit jest
    # podnieśd w a callback function, the interpreter exits.

    def capture_stderr(self, func, *args, **kw):
        # helper - call function 'func', oraz zwróć the captured stderr
        zaimportuj io
        old_stderr = sys.stderr
        logger = sys.stderr = io.StringIO()
        spróbuj:
            func(*args, **kw)
        w_końcu:
            sys.stderr = old_stderr
        zwróć logger.getvalue()

    def test_ValueError(self):
        cb = CFUNCTYPE(c_int, c_int)(callback_func)
        out = self.capture_stderr(cb, 42)
        self.assertEqual(out.splitlines()[-1],
                             "ValueError: 42")

    def test_IntegerDivisionError(self):
        cb = CFUNCTYPE(c_int, c_int)(callback_func)
        out = self.capture_stderr(cb, 0)
        self.assertEqual(out.splitlines()[-1][:19],
                             "ZeroDivisionError: ")

    def test_FloatDivisionError(self):
        cb = CFUNCTYPE(c_int, c_double)(callback_func)
        out = self.capture_stderr(cb, 0.0)
        self.assertEqual(out.splitlines()[-1][:19],
                             "ZeroDivisionError: ")

    def test_TypeErrorDivisionError(self):
        cb = CFUNCTYPE(c_int, c_char_p)(callback_func)
        out = self.capture_stderr(cb, b"spam")
        self.assertEqual(out.splitlines()[-1],
                             "TypeError: "
                             "unsupported operand type(s) dla /: 'int' oraz 'bytes'")

jeżeli __name__ == '__main__':
    unittest.main()
