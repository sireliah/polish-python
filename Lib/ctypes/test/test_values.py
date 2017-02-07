"""
A testcase which accesses *values* w a dll.
"""

zaimportuj unittest
zaimportuj sys
z ctypes zaimportuj *

zaimportuj _ctypes_test

klasa ValuesTestCase(unittest.TestCase):

    def test_an_integer(self):
        # This test checks oraz changes an integer stored inside the
        # _ctypes_test dll/shared lib.
        ctdll = CDLL(_ctypes_test.__file__)
        an_integer = c_int.in_dll(ctdll, "an_integer")
        x = an_integer.value
        self.assertEqual(x, ctdll.get_an_integer())
        an_integer.value *= 2
        self.assertEqual(x*2, ctdll.get_an_integer())
        # To avoid test failures when this test jest repeated several
        # times the original value must be restored
        an_integer.value = x
        self.assertEqual(x, ctdll.get_an_integer())

    def test_undefined(self):
        ctdll = CDLL(_ctypes_test.__file__)
        self.assertRaises(ValueError, c_int.in_dll, ctdll, "Undefined_Symbol")

@unittest.skipUnless(sys.platform == 'win32', 'Windows-specific test')
klasa Win_ValuesTestCase(unittest.TestCase):
    """This test only works when python itself jest a dll/shared library"""

    def test_optimizeflag(self):
        # This test accesses the Py_OptimizeFlag integer, which jest
        # exported by the Python dll oraz should match the sys.flags value

        opt = c_int.in_dll(pythonapi, "Py_OptimizeFlag").value
        self.assertEqual(opt, sys.flags.optimize)

    def test_frozentable(self):
        # Python exports a PyImport_FrozenModules symbol. This jest a
        # pointer to an array of struct _frozen entries.  The end of the
        # array jest marked by an entry containing a NULL name oraz zero
        # size.

        # In standard Python, this table contains a __hello__
        # module, oraz a __phello__ package containing a spam
        # module.
        klasa struct_frozen(Structure):
            _fields_ = [("name", c_char_p),
                        ("code", POINTER(c_ubyte)),
                        ("size", c_int)]
        FrozenTable = POINTER(struct_frozen)

        ft = FrozenTable.in_dll(pythonapi, "PyImport_FrozenModules")
        # ft jest a pointer to the struct_frozen entries:
        items = []
        # _frozen_importlib changes size whenever importlib._bootstrap
        # changes, so it gets a special case.  We should make sure it's
        # found, but don't worry about its size too much.  The same
        # applies to _frozen_importlib_external.
        bootstrap_seen = []
        bootstrap_expected = [
                b'_frozen_importlib',
                b'_frozen_importlib_external',
                ]
        dla entry w ft:
            # This jest dangerous. We *can* iterate over a pointer, but
            # the loop will nie terminate (maybe przy an access
            # violation;-) because the pointer instance has no size.
            jeżeli entry.name jest Nic:
                przerwij

            jeżeli entry.name w bootstrap_expected:
                bootstrap_seen.append(entry.name)
                self.assertPrawda(entry.size,
                    "{} was reported jako having no size".format(entry.name))
                kontynuuj
            items.append((entry.name, entry.size))

        expected = [(b"__hello__", 161),
                    (b"__phello__", -161),
                    (b"__phello__.spam", 161),
                    ]
        self.assertEqual(items, expected)

        self.assertEqual(sorted(bootstrap_seen), bootstrap_expected,
            "frozen bootstrap modules did nie match PyImport_FrozenModules")

        z ctypes zaimportuj _pointer_type_cache
        usuń _pointer_type_cache[struct_frozen]

    def test_undefined(self):
        self.assertRaises(ValueError, c_int.in_dll, pythonapi,
                          "Undefined_Symbol")

jeżeli __name__ == '__main__':
    unittest.main()
