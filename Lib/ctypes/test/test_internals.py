# This tests the internal _objects attribute
zaimportuj unittest
z ctypes zaimportuj *
z sys zaimportuj getrefcount jako grc

# XXX This test must be reviewed dla correctness!!!

# ctypes' types are container types.
#
# They have an internal memory block, which only consists of some bytes,
# but it has to keep references to other objects jako well. This jest nie
# really needed dla trivial C types like int albo char, but it jest important
# dla aggregate types like strings albo pointers w particular.
#
# What about pointers?

klasa ObjectsTestCase(unittest.TestCase):
    def assertSame(self, a, b):
        self.assertEqual(id(a), id(b))

    def test_ints(self):
        i = 42000123
        refcnt = grc(i)
        ci = c_int(i)
        self.assertEqual(refcnt, grc(i))
        self.assertEqual(ci._objects, Nic)

    def test_c_char_p(self):
        s = b"Hello, World"
        refcnt = grc(s)
        cs = c_char_p(s)
        self.assertEqual(refcnt + 1, grc(s))
        self.assertSame(cs._objects, s)

    def test_simple_struct(self):
        klasa X(Structure):
            _fields_ = [("a", c_int), ("b", c_int)]

        a = 421234
        b = 421235
        x = X()
        self.assertEqual(x._objects, Nic)
        x.a = a
        x.b = b
        self.assertEqual(x._objects, Nic)

    def test_embedded_structs(self):
        klasa X(Structure):
            _fields_ = [("a", c_int), ("b", c_int)]

        klasa Y(Structure):
            _fields_ = [("x", X), ("y", X)]

        y = Y()
        self.assertEqual(y._objects, Nic)

        x1, x2 = X(), X()
        y.x, y.y = x1, x2
        self.assertEqual(y._objects, {"0": {}, "1": {}})
        x1.a, x2.b = 42, 93
        self.assertEqual(y._objects, {"0": {}, "1": {}})

    def test_xxx(self):
        klasa X(Structure):
            _fields_ = [("a", c_char_p), ("b", c_char_p)]

        klasa Y(Structure):
            _fields_ = [("x", X), ("y", X)]

        s1 = b"Hello, World"
        s2 = b"Hallo, Welt"

        x = X()
        x.a = s1
        x.b = s2
        self.assertEqual(x._objects, {"0": s1, "1": s2})

        y = Y()
        y.x = x
        self.assertEqual(y._objects, {"0": {"0": s1, "1": s2}})
##        x = y.x
##        usuń y
##        print x._b_base_._objects

    def test_ptr_struct(self):
        klasa X(Structure):
            _fields_ = [("data", POINTER(c_int))]

        A = c_int*4
        a = A(11, 22, 33, 44)
        self.assertEqual(a._objects, Nic)

        x = X()
        x.data = a
##XXX        print x._objects
##XXX        print x.data[0]
##XXX        print x.data._objects

jeżeli __name__ == '__main__':
    unittest.main()
