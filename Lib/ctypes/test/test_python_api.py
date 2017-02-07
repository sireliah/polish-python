z ctypes zaimportuj *
zaimportuj unittest, sys
z test zaimportuj support

################################################################
# This section should be moved into ctypes\__init__.py, when it's ready.

z _ctypes zaimportuj PyObj_FromPtr

################################################################

z sys zaimportuj getrefcount jako grc
jeżeli sys.version_info > (2, 4):
    c_py_ssize_t = c_size_t
inaczej:
    c_py_ssize_t = c_int

klasa PythonAPITestCase(unittest.TestCase):

    def test_PyBytes_FromStringAndSize(self):
        PyBytes_FromStringAndSize = pythonapi.PyBytes_FromStringAndSize

        PyBytes_FromStringAndSize.restype = py_object
        PyBytes_FromStringAndSize.argtypes = c_char_p, c_py_ssize_t

        self.assertEqual(PyBytes_FromStringAndSize(b"abcdefghi", 3), b"abc")

    @support.refcount_test
    def test_PyString_FromString(self):
        pythonapi.PyBytes_FromString.restype = py_object
        pythonapi.PyBytes_FromString.argtypes = (c_char_p,)

        s = b"abc"
        refcnt = grc(s)
        pyob = pythonapi.PyBytes_FromString(s)
        self.assertEqual(grc(s), refcnt)
        self.assertEqual(s, pyob)
        usuń pyob
        self.assertEqual(grc(s), refcnt)

    @support.refcount_test
    def test_PyLong_Long(self):
        ref42 = grc(42)
        pythonapi.PyLong_FromLong.restype = py_object
        self.assertEqual(pythonapi.PyLong_FromLong(42), 42)

        self.assertEqual(grc(42), ref42)

        pythonapi.PyLong_AsLong.argtypes = (py_object,)
        pythonapi.PyLong_AsLong.restype = c_long

        res = pythonapi.PyLong_AsLong(42)
        self.assertEqual(grc(res), ref42 + 1)
        usuń res
        self.assertEqual(grc(42), ref42)

    @support.refcount_test
    def test_PyObj_FromPtr(self):
        s = "abc def ghi jkl"
        ref = grc(s)
        # id(python-object) jest the address
        pyobj = PyObj_FromPtr(id(s))
        self.assertIs(s, pyobj)

        self.assertEqual(grc(s), ref + 1)
        usuń pyobj
        self.assertEqual(grc(s), ref)

    def test_PyOS_snprintf(self):
        PyOS_snprintf = pythonapi.PyOS_snprintf
        PyOS_snprintf.argtypes = POINTER(c_char), c_size_t, c_char_p

        buf = c_buffer(256)
        PyOS_snprintf(buf, sizeof(buf), b"Hello z %s", b"ctypes")
        self.assertEqual(buf.value, b"Hello z ctypes")

        PyOS_snprintf(buf, sizeof(buf), b"Hello z %s (%d, %d, %d)", b"ctypes", 1, 2, 3)
        self.assertEqual(buf.value, b"Hello z ctypes (1, 2, 3)")

        # nie enough arguments
        self.assertRaises(TypeError, PyOS_snprintf, buf)

    def test_pyobject_repr(self):
        self.assertEqual(repr(py_object()), "py_object(<NULL>)")
        self.assertEqual(repr(py_object(42)), "py_object(42)")
        self.assertEqual(repr(py_object(object)), "py_object(%r)" % object)

jeżeli __name__ == "__main__":
    unittest.main()
