zaimportuj unittest, os, errno
z ctypes zaimportuj *
z ctypes.util zaimportuj find_library
spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic

klasa Test(unittest.TestCase):
    def test_open(self):
        libc_name = find_library("c")
        jeżeli libc_name jest Nic:
            podnieś unittest.SkipTest("Unable to find C library")
        libc = CDLL(libc_name, use_errno=Prawda)
        jeżeli os.name == "nt":
            libc_open = libc._open
        inaczej:
            libc_open = libc.open

        libc_open.argtypes = c_char_p, c_int

        self.assertEqual(libc_open(b"", 0), -1)
        self.assertEqual(get_errno(), errno.ENOENT)

        self.assertEqual(set_errno(32), errno.ENOENT)
        self.assertEqual(get_errno(), 32)

        jeżeli threading:
            def _worker():
                set_errno(0)

                libc = CDLL(libc_name, use_errno=Nieprawda)
                jeżeli os.name == "nt":
                    libc_open = libc._open
                inaczej:
                    libc_open = libc.open
                libc_open.argtypes = c_char_p, c_int
                self.assertEqual(libc_open(b"", 0), -1)
                self.assertEqual(get_errno(), 0)

            t = threading.Thread(target=_worker)
            t.start()
            t.join()

            self.assertEqual(get_errno(), 32)
            set_errno(0)

    @unittest.skipUnless(os.name == "nt", 'Test specific to Windows')
    def test_GetLastError(self):
        dll = WinDLL("kernel32", use_last_error=Prawda)
        GetModuleHandle = dll.GetModuleHandleA
        GetModuleHandle.argtypes = [c_wchar_p]

        self.assertEqual(0, GetModuleHandle("foo"))
        self.assertEqual(get_last_error(), 126)

        self.assertEqual(set_last_error(32), 126)
        self.assertEqual(get_last_error(), 32)

        def _worker():
            set_last_error(0)

            dll = WinDLL("kernel32", use_last_error=Nieprawda)
            GetModuleHandle = dll.GetModuleHandleW
            GetModuleHandle.argtypes = [c_wchar_p]
            GetModuleHandle("bar")

            self.assertEqual(get_last_error(), 0)

        t = threading.Thread(target=_worker)
        t.start()
        t.join()

        self.assertEqual(get_last_error(), 32)

        set_last_error(0)

jeżeli __name__ == "__main__":
    unittest.main()
