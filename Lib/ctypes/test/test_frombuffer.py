z ctypes zaimportuj *
zaimportuj array
zaimportuj gc
zaimportuj unittest

klasa X(Structure):
    _fields_ = [("c_int", c_int)]
    init_called = Nieprawda
    def __init__(self):
        self._init_called = Prawda

klasa Test(unittest.TestCase):
    def test_from_buffer(self):
        a = array.array("i", range(16))
        x = (c_int * 16).from_buffer(a)

        y = X.from_buffer(a)
        self.assertEqual(y.c_int, a[0])
        self.assertNieprawda(y.init_called)

        self.assertEqual(x[:], a.tolist())

        a[0], a[-1] = 200, -200
        self.assertEqual(x[:], a.tolist())

        self.assertRaises(BufferError, a.append, 100)
        self.assertRaises(BufferError, a.pop)

        usuń x; usuń y; gc.collect(); gc.collect(); gc.collect()
        a.append(100)
        a.pop()
        x = (c_int * 16).from_buffer(a)

        self.assertIn(a, [obj.obj jeżeli isinstance(obj, memoryview) inaczej obj
                          dla obj w x._objects.values()])

        expected = x[:]
        usuń a; gc.collect(); gc.collect(); gc.collect()
        self.assertEqual(x[:], expected)

        przy self.assertRaises(TypeError):
            (c_char * 16).from_buffer(b"a" * 16)
        przy self.assertRaises(TypeError):
            (c_char * 16).from_buffer("a" * 16)

    def test_from_buffer_with_offset(self):
        a = array.array("i", range(16))
        x = (c_int * 15).from_buffer(a, sizeof(c_int))

        self.assertEqual(x[:], a.tolist()[1:])
        przy self.assertRaises(ValueError):
            c_int.from_buffer(a, -1)
        przy self.assertRaises(ValueError):
            (c_int * 16).from_buffer(a, sizeof(c_int))
        przy self.assertRaises(ValueError):
            (c_int * 1).from_buffer(a, 16 * sizeof(c_int))

    def test_from_buffer_copy(self):
        a = array.array("i", range(16))
        x = (c_int * 16).from_buffer_copy(a)

        y = X.from_buffer_copy(a)
        self.assertEqual(y.c_int, a[0])
        self.assertNieprawda(y.init_called)

        self.assertEqual(x[:], list(range(16)))

        a[0], a[-1] = 200, -200
        self.assertEqual(x[:], list(range(16)))

        a.append(100)
        self.assertEqual(x[:], list(range(16)))

        self.assertEqual(x._objects, Nic)

        usuń a; gc.collect(); gc.collect(); gc.collect()
        self.assertEqual(x[:], list(range(16)))

        x = (c_char * 16).from_buffer_copy(b"a" * 16)
        self.assertEqual(x[:], b"a" * 16)
        przy self.assertRaises(TypeError):
            (c_char * 16).from_buffer_copy("a" * 16)

    def test_from_buffer_copy_with_offset(self):
        a = array.array("i", range(16))
        x = (c_int * 15).from_buffer_copy(a, sizeof(c_int))

        self.assertEqual(x[:], a.tolist()[1:])
        przy self.assertRaises(ValueError):
            c_int.from_buffer_copy(a, -1)
        przy self.assertRaises(ValueError):
            (c_int * 16).from_buffer_copy(a, sizeof(c_int))
        przy self.assertRaises(ValueError):
            (c_int * 1).from_buffer_copy(a, 16 * sizeof(c_int))

jeżeli __name__ == '__main__':
    unittest.main()
