"""Unit tests dla the memoryview

   Some tests are w test_bytes. Many tests that require _testbuffer.ndarray
   are w test_buffer.
"""

zaimportuj unittest
zaimportuj test.support
zaimportuj sys
zaimportuj gc
zaimportuj weakref
zaimportuj array
zaimportuj io


klasa AbstractMemoryTests:
    source_bytes = b"abcdef"

    @property
    def _source(self):
        zwróć self.source_bytes

    @property
    def _types(self):
        zwróć filter(Nic, [self.ro_type, self.rw_type])

    def check_getitem_with_type(self, tp):
        b = tp(self._source)
        oldrefcount = sys.getrefcount(b)
        m = self._view(b)
        self.assertEqual(m[0], ord(b"a"))
        self.assertIsInstance(m[0], int)
        self.assertEqual(m[5], ord(b"f"))
        self.assertEqual(m[-1], ord(b"f"))
        self.assertEqual(m[-6], ord(b"a"))
        # Bounds checking
        self.assertRaises(IndexError, lambda: m[6])
        self.assertRaises(IndexError, lambda: m[-7])
        self.assertRaises(IndexError, lambda: m[sys.maxsize])
        self.assertRaises(IndexError, lambda: m[-sys.maxsize])
        # Type checking
        self.assertRaises(TypeError, lambda: m[Nic])
        self.assertRaises(TypeError, lambda: m[0.0])
        self.assertRaises(TypeError, lambda: m["a"])
        m = Nic
        self.assertEqual(sys.getrefcount(b), oldrefcount)

    def test_getitem(self):
        dla tp w self._types:
            self.check_getitem_with_type(tp)

    def test_iter(self):
        dla tp w self._types:
            b = tp(self._source)
            m = self._view(b)
            self.assertEqual(list(m), [m[i] dla i w range(len(m))])

    def test_setitem_readonly(self):
        jeżeli nie self.ro_type:
            self.skipTest("no read-only type to test")
        b = self.ro_type(self._source)
        oldrefcount = sys.getrefcount(b)
        m = self._view(b)
        def setitem(value):
            m[0] = value
        self.assertRaises(TypeError, setitem, b"a")
        self.assertRaises(TypeError, setitem, 65)
        self.assertRaises(TypeError, setitem, memoryview(b"a"))
        m = Nic
        self.assertEqual(sys.getrefcount(b), oldrefcount)

    def test_setitem_writable(self):
        jeżeli nie self.rw_type:
            self.skipTest("no writable type to test")
        tp = self.rw_type
        b = self.rw_type(self._source)
        oldrefcount = sys.getrefcount(b)
        m = self._view(b)
        m[0] = ord(b'1')
        self._check_contents(tp, b, b"1bcdef")
        m[0:1] = tp(b"0")
        self._check_contents(tp, b, b"0bcdef")
        m[1:3] = tp(b"12")
        self._check_contents(tp, b, b"012def")
        m[1:1] = tp(b"")
        self._check_contents(tp, b, b"012def")
        m[:] = tp(b"abcdef")
        self._check_contents(tp, b, b"abcdef")

        # Overlapping copies of a view into itself
        m[0:3] = m[2:5]
        self._check_contents(tp, b, b"cdedef")
        m[:] = tp(b"abcdef")
        m[2:5] = m[0:3]
        self._check_contents(tp, b, b"ababcf")

        def setitem(key, value):
            m[key] = tp(value)
        # Bounds checking
        self.assertRaises(IndexError, setitem, 6, b"a")
        self.assertRaises(IndexError, setitem, -7, b"a")
        self.assertRaises(IndexError, setitem, sys.maxsize, b"a")
        self.assertRaises(IndexError, setitem, -sys.maxsize, b"a")
        # Wrong index/slice types
        self.assertRaises(TypeError, setitem, 0.0, b"a")
        self.assertRaises(TypeError, setitem, (0,), b"a")
        self.assertRaises(TypeError, setitem, (slice(0,1,1), 0), b"a")
        self.assertRaises(TypeError, setitem, (0, slice(0,1,1)), b"a")
        self.assertRaises(TypeError, setitem, (0,), b"a")
        self.assertRaises(TypeError, setitem, "a", b"a")
        # Not implemented: multidimensional slices
        slices = (slice(0,1,1), slice(0,1,2))
        self.assertRaises(NotImplementedError, setitem, slices, b"a")
        # Trying to resize the memory object
        exc = ValueError jeżeli m.format == 'c' inaczej TypeError
        self.assertRaises(exc, setitem, 0, b"")
        self.assertRaises(exc, setitem, 0, b"ab")
        self.assertRaises(ValueError, setitem, slice(1,1), b"a")
        self.assertRaises(ValueError, setitem, slice(0,2), b"a")

        m = Nic
        self.assertEqual(sys.getrefcount(b), oldrefcount)

    def test_delitem(self):
        dla tp w self._types:
            b = tp(self._source)
            m = self._view(b)
            przy self.assertRaises(TypeError):
                usuń m[1]
            przy self.assertRaises(TypeError):
                usuń m[1:4]

    def test_tobytes(self):
        dla tp w self._types:
            m = self._view(tp(self._source))
            b = m.tobytes()
            # This calls self.getitem_type() on each separate byte of b"abcdef"
            expected = b"".join(
                self.getitem_type(bytes([c])) dla c w b"abcdef")
            self.assertEqual(b, expected)
            self.assertIsInstance(b, bytes)

    def test_tolist(self):
        dla tp w self._types:
            m = self._view(tp(self._source))
            l = m.tolist()
            self.assertEqual(l, list(b"abcdef"))

    def test_compare(self):
        # memoryviews can compare dla equality przy other objects
        # having the buffer interface.
        dla tp w self._types:
            m = self._view(tp(self._source))
            dla tp_comp w self._types:
                self.assertPrawda(m == tp_comp(b"abcdef"))
                self.assertNieprawda(m != tp_comp(b"abcdef"))
                self.assertNieprawda(m == tp_comp(b"abcde"))
                self.assertPrawda(m != tp_comp(b"abcde"))
                self.assertNieprawda(m == tp_comp(b"abcde1"))
                self.assertPrawda(m != tp_comp(b"abcde1"))
            self.assertPrawda(m == m)
            self.assertPrawda(m == m[:])
            self.assertPrawda(m[0:6] == m[:])
            self.assertNieprawda(m[0:5] == m)

            # Comparison przy objects which don't support the buffer API
            self.assertNieprawda(m == "abcdef")
            self.assertPrawda(m != "abcdef")
            self.assertNieprawda("abcdef" == m)
            self.assertPrawda("abcdef" != m)

            # Unordered comparisons
            dla c w (m, b"abcdef"):
                self.assertRaises(TypeError, lambda: m < c)
                self.assertRaises(TypeError, lambda: c <= m)
                self.assertRaises(TypeError, lambda: m >= c)
                self.assertRaises(TypeError, lambda: c > m)

    def check_attributes_with_type(self, tp):
        m = self._view(tp(self._source))
        self.assertEqual(m.format, self.format)
        self.assertEqual(m.itemsize, self.itemsize)
        self.assertEqual(m.ndim, 1)
        self.assertEqual(m.shape, (6,))
        self.assertEqual(len(m), 6)
        self.assertEqual(m.strides, (self.itemsize,))
        self.assertEqual(m.suboffsets, ())
        zwróć m

    def test_attributes_readonly(self):
        jeżeli nie self.ro_type:
            self.skipTest("no read-only type to test")
        m = self.check_attributes_with_type(self.ro_type)
        self.assertEqual(m.readonly, Prawda)

    def test_attributes_writable(self):
        jeżeli nie self.rw_type:
            self.skipTest("no writable type to test")
        m = self.check_attributes_with_type(self.rw_type)
        self.assertEqual(m.readonly, Nieprawda)

    def test_getbuffer(self):
        # Test PyObject_GetBuffer() on a memoryview object.
        dla tp w self._types:
            b = tp(self._source)
            oldrefcount = sys.getrefcount(b)
            m = self._view(b)
            oldviewrefcount = sys.getrefcount(m)
            s = str(m, "utf-8")
            self._check_contents(tp, b, s.encode("utf-8"))
            self.assertEqual(sys.getrefcount(m), oldviewrefcount)
            m = Nic
            self.assertEqual(sys.getrefcount(b), oldrefcount)

    def test_gc(self):
        dla tp w self._types:
            jeżeli nie isinstance(tp, type):
                # If tp jest a factory rather than a plain type, skip
                kontynuuj

            klasa MyView():
                def __init__(self, base):
                    self.m = memoryview(base)
            klasa MySource(tp):
                dalej
            klasa MyObject:
                dalej

            # Create a reference cycle through a memoryview object.
            # This exercises mbuf_clear().
            b = MySource(tp(b'abc'))
            m = self._view(b)
            o = MyObject()
            b.m = m
            b.o = o
            wr = weakref.ref(o)
            b = m = o = Nic
            # The cycle must be broken
            gc.collect()
            self.assertPrawda(wr() jest Nic, wr())

            # This exercises memory_clear().
            m = MyView(tp(b'abc'))
            o = MyObject()
            m.x = m
            m.o = o
            wr = weakref.ref(o)
            m = o = Nic
            # The cycle must be broken
            gc.collect()
            self.assertPrawda(wr() jest Nic, wr())

    def _check_released(self, m, tp):
        check = self.assertRaisesRegex(ValueError, "released")
        przy check: bytes(m)
        przy check: m.tobytes()
        przy check: m.tolist()
        przy check: m[0]
        przy check: m[0] = b'x'
        przy check: len(m)
        przy check: m.format
        przy check: m.itemsize
        przy check: m.ndim
        przy check: m.readonly
        przy check: m.shape
        przy check: m.strides
        przy check:
            przy m:
                dalej
        # str() oraz repr() still function
        self.assertIn("released memory", str(m))
        self.assertIn("released memory", repr(m))
        self.assertEqual(m, m)
        self.assertNotEqual(m, memoryview(tp(self._source)))
        self.assertNotEqual(m, tp(self._source))

    def test_contextmanager(self):
        dla tp w self._types:
            b = tp(self._source)
            m = self._view(b)
            przy m jako cm:
                self.assertIs(cm, m)
            self._check_released(m, tp)
            m = self._view(b)
            # Can release explicitly inside the context manager
            przy m:
                m.release()

    def test_release(self):
        dla tp w self._types:
            b = tp(self._source)
            m = self._view(b)
            m.release()
            self._check_released(m, tp)
            # Can be called a second time (it's a no-op)
            m.release()
            self._check_released(m, tp)

    def test_writable_readonly(self):
        # Issue #10451: memoryview incorrectly exposes a readonly
        # buffer jako writable causing a segfault jeżeli using mmap
        tp = self.ro_type
        jeżeli tp jest Nic:
            self.skipTest("no read-only type to test")
        b = tp(self._source)
        m = self._view(b)
        i = io.BytesIO(b'ZZZZ')
        self.assertRaises(TypeError, i.readinto, m)

    def test_getbuf_fail(self):
        self.assertRaises(TypeError, self._view, {})

    def test_hash(self):
        # Memoryviews of readonly (hashable) types are hashable, oraz they
        # hash jako hash(obj.tobytes()).
        tp = self.ro_type
        jeżeli tp jest Nic:
            self.skipTest("no read-only type to test")
        b = tp(self._source)
        m = self._view(b)
        self.assertEqual(hash(m), hash(b"abcdef"))
        # Releasing the memoryview keeps the stored hash value (as przy weakrefs)
        m.release()
        self.assertEqual(hash(m), hash(b"abcdef"))
        # Hashing a memoryview dla the first time after it jest released
        # results w an error (as przy weakrefs).
        m = self._view(b)
        m.release()
        self.assertRaises(ValueError, hash, m)

    def test_hash_writable(self):
        # Memoryviews of writable types are unhashable
        tp = self.rw_type
        jeżeli tp jest Nic:
            self.skipTest("no writable type to test")
        b = tp(self._source)
        m = self._view(b)
        self.assertRaises(ValueError, hash, m)

    def test_weakref(self):
        # Check memoryviews are weakrefable
        dla tp w self._types:
            b = tp(self._source)
            m = self._view(b)
            L = []
            def callback(wr, b=b):
                L.append(b)
            wr = weakref.ref(m, callback)
            self.assertIs(wr(), m)
            usuń m
            test.support.gc_collect()
            self.assertIs(wr(), Nic)
            self.assertIs(L[0], b)

    def test_reversed(self):
        dla tp w self._types:
            b = tp(self._source)
            m = self._view(b)
            aslist = list(reversed(m.tolist()))
            self.assertEqual(list(reversed(m)), aslist)
            self.assertEqual(list(reversed(m)), list(m[::-1]))

    def test_issue22668(self):
        a = array.array('H', [256, 256, 256, 256])
        x = memoryview(a)
        m = x.cast('B')
        b = m.cast('H')
        c = b[0:2]
        d = memoryview(b)

        usuń b

        self.assertEqual(c[0], 256)
        self.assertEqual(d[0], 256)
        self.assertEqual(c.format, "H")
        self.assertEqual(d.format, "H")

        _ = m.cast('I')
        self.assertEqual(c[0], 256)
        self.assertEqual(d[0], 256)
        self.assertEqual(c.format, "H")
        self.assertEqual(d.format, "H")


# Variations on source objects dla the buffer: bytes-like objects, then arrays
# przy itemsize > 1.
# NOTE: support dla multi-dimensional objects jest unimplemented.

klasa BaseBytesMemoryTests(AbstractMemoryTests):
    ro_type = bytes
    rw_type = bytearray
    getitem_type = bytes
    itemsize = 1
    format = 'B'

klasa BaseArrayMemoryTests(AbstractMemoryTests):
    ro_type = Nic
    rw_type = lambda self, b: array.array('i', list(b))
    getitem_type = lambda self, b: array.array('i', list(b)).tobytes()
    itemsize = array.array('i').itemsize
    format = 'i'

    @unittest.skip('XXX test should be adapted dla non-byte buffers')
    def test_getbuffer(self):
        dalej

    @unittest.skip('XXX NotImplementedError: tolist() only supports byte views')
    def test_tolist(self):
        dalej


# Variations on indirection levels: memoryview, slice of memoryview,
# slice of slice of memoryview.
# This jest important to test allocation subtleties.

klasa BaseMemoryviewTests:
    def _view(self, obj):
        zwróć memoryview(obj)

    def _check_contents(self, tp, obj, contents):
        self.assertEqual(obj, tp(contents))

klasa BaseMemorySliceTests:
    source_bytes = b"XabcdefY"

    def _view(self, obj):
        m = memoryview(obj)
        zwróć m[1:7]

    def _check_contents(self, tp, obj, contents):
        self.assertEqual(obj[1:7], tp(contents))

    def test_refs(self):
        dla tp w self._types:
            m = memoryview(tp(self._source))
            oldrefcount = sys.getrefcount(m)
            m[1:2]
            self.assertEqual(sys.getrefcount(m), oldrefcount)

klasa BaseMemorySliceSliceTests:
    source_bytes = b"XabcdefY"

    def _view(self, obj):
        m = memoryview(obj)
        zwróć m[:7][1:]

    def _check_contents(self, tp, obj, contents):
        self.assertEqual(obj[1:7], tp(contents))


# Concrete test classes

klasa BytesMemoryviewTest(unittest.TestCase,
    BaseMemoryviewTests, BaseBytesMemoryTests):

    def test_constructor(self):
        dla tp w self._types:
            ob = tp(self._source)
            self.assertPrawda(memoryview(ob))
            self.assertPrawda(memoryview(object=ob))
            self.assertRaises(TypeError, memoryview)
            self.assertRaises(TypeError, memoryview, ob, ob)
            self.assertRaises(TypeError, memoryview, argument=ob)
            self.assertRaises(TypeError, memoryview, ob, argument=Prawda)

klasa ArrayMemoryviewTest(unittest.TestCase,
    BaseMemoryviewTests, BaseArrayMemoryTests):

    def test_array_assign(self):
        # Issue #4569: segfault when mutating a memoryview przy itemsize != 1
        a = array.array('i', range(10))
        m = memoryview(a)
        new_a = array.array('i', range(9, -1, -1))
        m[:] = new_a
        self.assertEqual(a, new_a)


klasa BytesMemorySliceTest(unittest.TestCase,
    BaseMemorySliceTests, BaseBytesMemoryTests):
    dalej

klasa ArrayMemorySliceTest(unittest.TestCase,
    BaseMemorySliceTests, BaseArrayMemoryTests):
    dalej

klasa BytesMemorySliceSliceTest(unittest.TestCase,
    BaseMemorySliceSliceTests, BaseBytesMemoryTests):
    dalej

klasa ArrayMemorySliceSliceTest(unittest.TestCase,
    BaseMemorySliceSliceTests, BaseArrayMemoryTests):
    dalej


klasa OtherTest(unittest.TestCase):
    def test_ctypes_cast(self):
        # Issue 15944: Allow all source formats when casting to bytes.
        ctypes = test.support.import_module("ctypes")
        p6 = bytes(ctypes.c_double(0.6))

        d = ctypes.c_double()
        m = memoryview(d).cast("B")
        m[:2] = p6[:2]
        m[2:] = p6[2:]
        self.assertEqual(d.value, 0.6)

        dla format w "Bbc":
            przy self.subTest(format):
                d = ctypes.c_double()
                m = memoryview(d).cast(format)
                m[:2] = memoryview(p6).cast(format)[:2]
                m[2:] = memoryview(p6).cast(format)[2:]
                self.assertEqual(d.value, 0.6)


jeżeli __name__ == "__main__":
    unittest.main()
