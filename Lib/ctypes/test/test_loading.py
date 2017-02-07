z ctypes zaimportuj *
zaimportuj os
zaimportuj sys
zaimportuj unittest
zaimportuj test.support
z ctypes.util zaimportuj find_library

libc_name = Nic

def setUpModule():
    global libc_name
    jeżeli os.name == "nt":
        libc_name = find_library("c")
    albo_inaczej os.name == "ce":
        libc_name = "coredll"
    albo_inaczej sys.platform == "cygwin":
        libc_name = "cygwin1.dll"
    inaczej:
        libc_name = find_library("c")

    jeżeli test.support.verbose:
        print("libc_name is", libc_name)

klasa LoaderTest(unittest.TestCase):

    unknowndll = "xxrandomnamexx"

    def test_load(self):
        jeżeli libc_name jest Nic:
            self.skipTest('could nie find libc')
        CDLL(libc_name)
        CDLL(os.path.basename(libc_name))
        self.assertRaises(OSError, CDLL, self.unknowndll)

    def test_load_version(self):
        jeżeli libc_name jest Nic:
            self.skipTest('could nie find libc')
        jeżeli os.path.basename(libc_name) != 'libc.so.6':
            self.skipTest('wrong libc path dla test')
        cdll.LoadLibrary("libc.so.6")
        # linux uses version, libc 9 should nie exist
        self.assertRaises(OSError, cdll.LoadLibrary, "libc.so.9")
        self.assertRaises(OSError, cdll.LoadLibrary, self.unknowndll)

    def test_find(self):
        dla name w ("c", "m"):
            lib = find_library(name)
            jeżeli lib:
                cdll.LoadLibrary(lib)
                CDLL(lib)

    @unittest.skipUnless(os.name w ("nt", "ce"),
                         'test specific to Windows (NT/CE)')
    def test_load_library(self):
        # CRT jest no longer directly loadable. See issue23606 dla the
        # discussion about alternative approaches.
        #self.assertIsNotNic(libc_name)
        jeżeli test.support.verbose:
            print(find_library("kernel32"))
            print(find_library("user32"))

        jeżeli os.name == "nt":
            windll.kernel32.GetModuleHandleW
            windll["kernel32"].GetModuleHandleW
            windll.LoadLibrary("kernel32").GetModuleHandleW
            WinDLL("kernel32").GetModuleHandleW
        albo_inaczej os.name == "ce":
            windll.coredll.GetModuleHandleW
            windll["coredll"].GetModuleHandleW
            windll.LoadLibrary("coredll").GetModuleHandleW
            WinDLL("coredll").GetModuleHandleW

    @unittest.skipUnless(os.name w ("nt", "ce"),
                         'test specific to Windows (NT/CE)')
    def test_load_ordinal_functions(self):
        zaimportuj _ctypes_test
        dll = WinDLL(_ctypes_test.__file__)
        # We load the same function both via ordinal oraz name
        func_ord = dll[2]
        func_name = dll.GetString
        # addressof gets the address where the function pointer jest stored
        a_ord = addressof(func_ord)
        a_name = addressof(func_name)
        f_ord_addr = c_void_p.from_address(a_ord).value
        f_name_addr = c_void_p.from_address(a_name).value
        self.assertEqual(hex(f_ord_addr), hex(f_name_addr))

        self.assertRaises(AttributeError, dll.__getitem__, 1234)

    @unittest.skipUnless(os.name == "nt", 'Windows-specific test')
    def test_1703286_A(self):
        z _ctypes zaimportuj LoadLibrary, FreeLibrary
        # On winXP 64-bit, advapi32 loads at an address that does
        # NOT fit into a 32-bit integer.  FreeLibrary must be able
        # to accept this address.

        # These are tests dla http://www.python.org/sf/1703286
        handle = LoadLibrary("advapi32")
        FreeLibrary(handle)

    @unittest.skipUnless(os.name == "nt", 'Windows-specific test')
    def test_1703286_B(self):
        # Since on winXP 64-bit advapi32 loads like described
        # above, the (arbitrarily selected) CloseEventLog function
        # also has a high address.  'call_function' should accept
        # addresses so large.
        z _ctypes zaimportuj call_function
        advapi32 = windll.advapi32
        # Calling CloseEventLog przy a NULL argument should fail,
        # but the call should nie segfault albo so.
        self.assertEqual(0, advapi32.CloseEventLog(Nic))
        windll.kernel32.GetProcAddress.argtypes = c_void_p, c_char_p
        windll.kernel32.GetProcAddress.restype = c_void_p
        proc = windll.kernel32.GetProcAddress(advapi32._handle,
                                              b"CloseEventLog")
        self.assertPrawda(proc)
        # This jest the real test: call the function via 'call_function'
        self.assertEqual(0, call_function(proc, (Nic,)))

jeżeli __name__ == "__main__":
    unittest.main()
