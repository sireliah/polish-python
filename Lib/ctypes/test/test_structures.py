zaimportuj unittest
z ctypes zaimportuj *
z ctypes.test zaimportuj need_symbol
z struct zaimportuj calcsize
zaimportuj _testcapi

klasa SubclassesTest(unittest.TestCase):
    def test_subclass(self):
        klasa X(Structure):
            _fields_ = [("a", c_int)]

        klasa Y(X):
            _fields_ = [("b", c_int)]

        klasa Z(X):
            dalej

        self.assertEqual(sizeof(X), sizeof(c_int))
        self.assertEqual(sizeof(Y), sizeof(c_int)*2)
        self.assertEqual(sizeof(Z), sizeof(c_int))
        self.assertEqual(X._fields_, [("a", c_int)])
        self.assertEqual(Y._fields_, [("b", c_int)])
        self.assertEqual(Z._fields_, [("a", c_int)])

    def test_subclass_delayed(self):
        klasa X(Structure):
            dalej
        self.assertEqual(sizeof(X), 0)
        X._fields_ = [("a", c_int)]

        klasa Y(X):
            dalej
        self.assertEqual(sizeof(Y), sizeof(X))
        Y._fields_ = [("b", c_int)]

        klasa Z(X):
            dalej

        self.assertEqual(sizeof(X), sizeof(c_int))
        self.assertEqual(sizeof(Y), sizeof(c_int)*2)
        self.assertEqual(sizeof(Z), sizeof(c_int))
        self.assertEqual(X._fields_, [("a", c_int)])
        self.assertEqual(Y._fields_, [("b", c_int)])
        self.assertEqual(Z._fields_, [("a", c_int)])

klasa StructureTestCase(unittest.TestCase):
    formats = {"c": c_char,
               "b": c_byte,
               "B": c_ubyte,
               "h": c_short,
               "H": c_ushort,
               "i": c_int,
               "I": c_uint,
               "l": c_long,
               "L": c_ulong,
               "q": c_longlong,
               "Q": c_ulonglong,
               "f": c_float,
               "d": c_double,
               }

    def test_simple_structs(self):
        dla code, tp w self.formats.items():
            klasa X(Structure):
                _fields_ = [("x", c_char),
                            ("y", tp)]
            self.assertEqual((sizeof(X), code),
                                 (calcsize("c%c0%c" % (code, code)), code))

    def test_unions(self):
        dla code, tp w self.formats.items():
            klasa X(Union):
                _fields_ = [("x", c_char),
                            ("y", tp)]
            self.assertEqual((sizeof(X), code),
                                 (calcsize("%c" % (code)), code))

    def test_struct_alignment(self):
        klasa X(Structure):
            _fields_ = [("x", c_char * 3)]
        self.assertEqual(alignment(X), calcsize("s"))
        self.assertEqual(sizeof(X), calcsize("3s"))

        klasa Y(Structure):
            _fields_ = [("x", c_char * 3),
                        ("y", c_int)]
        self.assertEqual(alignment(Y), alignment(c_int))
        self.assertEqual(sizeof(Y), calcsize("3si"))

        klasa SI(Structure):
            _fields_ = [("a", X),
                        ("b", Y)]
        self.assertEqual(alignment(SI), max(alignment(Y), alignment(X)))
        self.assertEqual(sizeof(SI), calcsize("3s0i 3si 0i"))

        klasa IS(Structure):
            _fields_ = [("b", Y),
                        ("a", X)]

        self.assertEqual(alignment(SI), max(alignment(X), alignment(Y)))
        self.assertEqual(sizeof(IS), calcsize("3si 3s 0i"))

        klasa XX(Structure):
            _fields_ = [("a", X),
                        ("b", X)]
        self.assertEqual(alignment(XX), alignment(X))
        self.assertEqual(sizeof(XX), calcsize("3s 3s 0s"))

    def test_emtpy(self):
        # I had problems przy these
        #
        # Although these are pathological cases: Empty Structures!
        klasa X(Structure):
            _fields_ = []

        klasa Y(Union):
            _fields_ = []

        # Is this really the correct alignment, albo should it be 0?
        self.assertPrawda(alignment(X) == alignment(Y) == 1)
        self.assertPrawda(sizeof(X) == sizeof(Y) == 0)

        klasa XX(Structure):
            _fields_ = [("a", X),
                        ("b", X)]

        self.assertEqual(alignment(XX), 1)
        self.assertEqual(sizeof(XX), 0)

    def test_fields(self):
        # test the offset oraz size attributes of Structure/Unoin fields.
        klasa X(Structure):
            _fields_ = [("x", c_int),
                        ("y", c_char)]

        self.assertEqual(X.x.offset, 0)
        self.assertEqual(X.x.size, sizeof(c_int))

        self.assertEqual(X.y.offset, sizeof(c_int))
        self.assertEqual(X.y.size, sizeof(c_char))

        # readonly
        self.assertRaises((TypeError, AttributeError), setattr, X.x, "offset", 92)
        self.assertRaises((TypeError, AttributeError), setattr, X.x, "size", 92)

        klasa X(Union):
            _fields_ = [("x", c_int),
                        ("y", c_char)]

        self.assertEqual(X.x.offset, 0)
        self.assertEqual(X.x.size, sizeof(c_int))

        self.assertEqual(X.y.offset, 0)
        self.assertEqual(X.y.size, sizeof(c_char))

        # readonly
        self.assertRaises((TypeError, AttributeError), setattr, X.x, "offset", 92)
        self.assertRaises((TypeError, AttributeError), setattr, X.x, "size", 92)

        # XXX Should we check nested data types also?
        # offset jest always relative to the class...

    def test_packed(self):
        klasa X(Structure):
            _fields_ = [("a", c_byte),
                        ("b", c_longlong)]
            _pack_ = 1

        self.assertEqual(sizeof(X), 9)
        self.assertEqual(X.b.offset, 1)

        klasa X(Structure):
            _fields_ = [("a", c_byte),
                        ("b", c_longlong)]
            _pack_ = 2
        self.assertEqual(sizeof(X), 10)
        self.assertEqual(X.b.offset, 2)

        zaimportuj struct
        longlong_size = struct.calcsize("q")
        longlong_align = struct.calcsize("bq") - longlong_size

        klasa X(Structure):
            _fields_ = [("a", c_byte),
                        ("b", c_longlong)]
            _pack_ = 4
        self.assertEqual(sizeof(X), min(4, longlong_align) + longlong_size)
        self.assertEqual(X.b.offset, min(4, longlong_align))

        klasa X(Structure):
            _fields_ = [("a", c_byte),
                        ("b", c_longlong)]
            _pack_ = 8

        self.assertEqual(sizeof(X), min(8, longlong_align) + longlong_size)
        self.assertEqual(X.b.offset, min(8, longlong_align))


        d = {"_fields_": [("a", "b"),
                          ("b", "q")],
             "_pack_": -1}
        self.assertRaises(ValueError, type(Structure), "X", (Structure,), d)

        # Issue 15989
        d = {"_fields_": [("a", c_byte)],
             "_pack_": _testcapi.INT_MAX + 1}
        self.assertRaises(ValueError, type(Structure), "X", (Structure,), d)
        d = {"_fields_": [("a", c_byte)],
             "_pack_": _testcapi.UINT_MAX + 2}
        self.assertRaises(ValueError, type(Structure), "X", (Structure,), d)

    def test_initializers(self):
        klasa Person(Structure):
            _fields_ = [("name", c_char*6),
                        ("age", c_int)]

        self.assertRaises(TypeError, Person, 42)
        self.assertRaises(ValueError, Person, b"asldkjaslkdjaslkdj")
        self.assertRaises(TypeError, Person, "Name", "HI")

        # short enough
        self.assertEqual(Person(b"12345", 5).name, b"12345")
        # exact fit
        self.assertEqual(Person(b"123456", 5).name, b"123456")
        # too long
        self.assertRaises(ValueError, Person, b"1234567", 5)

    def test_conflicting_initializers(self):
        klasa POINT(Structure):
            _fields_ = [("x", c_int), ("y", c_int)]
        # conflicting positional oraz keyword args
        self.assertRaises(TypeError, POINT, 2, 3, x=4)
        self.assertRaises(TypeError, POINT, 2, 3, y=4)

        # too many initializers
        self.assertRaises(TypeError, POINT, 2, 3, 4)

    def test_keyword_initializers(self):
        klasa POINT(Structure):
            _fields_ = [("x", c_int), ("y", c_int)]
        pt = POINT(1, 2)
        self.assertEqual((pt.x, pt.y), (1, 2))

        pt = POINT(y=2, x=1)
        self.assertEqual((pt.x, pt.y), (1, 2))

    def test_invalid_field_types(self):
        klasa POINT(Structure):
            dalej
        self.assertRaises(TypeError, setattr, POINT, "_fields_", [("x", 1), ("y", 2)])

    def test_invalid_name(self):
        # field name must be string
        def declare_with_name(name):
            klasa S(Structure):
                _fields_ = [(name, c_int)]

        self.assertRaises(TypeError, declare_with_name, b"x")

    def test_intarray_fields(self):
        klasa SomeInts(Structure):
            _fields_ = [("a", c_int * 4)]

        # can use tuple to initialize array (but nie list!)
        self.assertEqual(SomeInts((1, 2)).a[:], [1, 2, 0, 0])
        self.assertEqual(SomeInts((1, 2)).a[::], [1, 2, 0, 0])
        self.assertEqual(SomeInts((1, 2)).a[::-1], [0, 0, 2, 1])
        self.assertEqual(SomeInts((1, 2)).a[::2], [1, 0])
        self.assertEqual(SomeInts((1, 2)).a[1:5:6], [2])
        self.assertEqual(SomeInts((1, 2)).a[6:4:-1], [])
        self.assertEqual(SomeInts((1, 2, 3, 4)).a[:], [1, 2, 3, 4])
        self.assertEqual(SomeInts((1, 2, 3, 4)).a[::], [1, 2, 3, 4])
        # too long
        # XXX Should podnieś ValueError?, nie RuntimeError
        self.assertRaises(RuntimeError, SomeInts, (1, 2, 3, 4, 5))

    def test_nested_initializers(self):
        # test initializing nested structures
        klasa Phone(Structure):
            _fields_ = [("areacode", c_char*6),
                        ("number", c_char*12)]

        klasa Person(Structure):
            _fields_ = [("name", c_char * 12),
                        ("phone", Phone),
                        ("age", c_int)]

        p = Person(b"Someone", (b"1234", b"5678"), 5)

        self.assertEqual(p.name, b"Someone")
        self.assertEqual(p.phone.areacode, b"1234")
        self.assertEqual(p.phone.number, b"5678")
        self.assertEqual(p.age, 5)

    @need_symbol('c_wchar')
    def test_structures_with_wchar(self):
        klasa PersonW(Structure):
            _fields_ = [("name", c_wchar * 12),
                        ("age", c_int)]

        p = PersonW("Someone \xe9")
        self.assertEqual(p.name, "Someone \xe9")

        self.assertEqual(PersonW("1234567890").name, "1234567890")
        self.assertEqual(PersonW("12345678901").name, "12345678901")
        # exact fit
        self.assertEqual(PersonW("123456789012").name, "123456789012")
        #too long
        self.assertRaises(ValueError, PersonW, "1234567890123")

    def test_init_errors(self):
        klasa Phone(Structure):
            _fields_ = [("areacode", c_char*6),
                        ("number", c_char*12)]

        klasa Person(Structure):
            _fields_ = [("name", c_char * 12),
                        ("phone", Phone),
                        ("age", c_int)]

        cls, msg = self.get_except(Person, b"Someone", (1, 2))
        self.assertEqual(cls, RuntimeError)
        self.assertEqual(msg,
                             "(Phone) <class 'TypeError'>: "
                             "expected bytes, int found")

        cls, msg = self.get_except(Person, b"Someone", (b"a", b"b", b"c"))
        self.assertEqual(cls, RuntimeError)
        jeżeli issubclass(Exception, object):
            self.assertEqual(msg,
                                 "(Phone) <class 'TypeError'>: too many initializers")
        inaczej:
            self.assertEqual(msg, "(Phone) TypeError: too many initializers")

    def test_huge_field_name(self):
        # issue12881: segfault przy large structure field names
        def create_class(length):
            klasa S(Structure):
                _fields_ = [('x' * length, c_int)]

        dla length w [10 ** i dla i w range(0, 8)]:
            spróbuj:
                create_class(length)
            wyjąwszy MemoryError:
                # MemoryErrors are OK, we just don't want to segfault
                dalej

    def get_except(self, func, *args):
        spróbuj:
            func(*args)
        wyjąwszy Exception jako detail:
            zwróć detail.__class__, str(detail)

    @unittest.skip('test disabled')
    def test_subclass_creation(self):
        meta = type(Structure)
        # same jako 'class X(Structure): dalej'
        # fails, since we need either a _fields_ albo a _abstract_ attribute
        cls, msg = self.get_except(meta, "X", (Structure,), {})
        self.assertEqual((cls, msg),
                (AttributeError, "class must define a '_fields_' attribute"))

    def test_abstract_class(self):
        klasa X(Structure):
            _abstract_ = "something"
        # try 'X()'
        cls, msg = self.get_except(eval, "X()", locals())
        self.assertEqual((cls, msg), (TypeError, "abstract class"))

    def test_methods(self):
##        klasa X(Structure):
##            _fields_ = []

        self.assertIn("in_dll", dir(type(Structure)))
        self.assertIn("from_address", dir(type(Structure)))
        self.assertIn("in_dll", dir(type(Structure)))

    def test_positional_args(self):
        # see also http://bugs.python.org/issue5042
        klasa W(Structure):
            _fields_ = [("a", c_int), ("b", c_int)]
        klasa X(W):
            _fields_ = [("c", c_int)]
        klasa Y(X):
            dalej
        klasa Z(Y):
            _fields_ = [("d", c_int), ("e", c_int), ("f", c_int)]

        z = Z(1, 2, 3, 4, 5, 6)
        self.assertEqual((z.a, z.b, z.c, z.d, z.e, z.f),
                         (1, 2, 3, 4, 5, 6))
        z = Z(1)
        self.assertEqual((z.a, z.b, z.c, z.d, z.e, z.f),
                         (1, 0, 0, 0, 0, 0))
        self.assertRaises(TypeError, lambda: Z(1, 2, 3, 4, 5, 6, 7))

klasa PointerMemberTestCase(unittest.TestCase):

    def test(self):
        # a Structure przy a POINTER field
        klasa S(Structure):
            _fields_ = [("array", POINTER(c_int))]

        s = S()
        # We can assign arrays of the correct type
        s.array = (c_int * 3)(1, 2, 3)
        items = [s.array[i] dla i w range(3)]
        self.assertEqual(items, [1, 2, 3])

        # The following are bugs, but are included here because the unittests
        # also describe the current behaviour.
        #
        # This fails przy SystemError: bad arg to internal function
        # albo przy IndexError (przy a patch I have)

        s.array[0] = 42

        items = [s.array[i] dla i w range(3)]
        self.assertEqual(items, [42, 2, 3])

        s.array[0] = 1

##        s.array[1] = 42

        items = [s.array[i] dla i w range(3)]
        self.assertEqual(items, [1, 2, 3])

    def test_none_to_pointer_fields(self):
        klasa S(Structure):
            _fields_ = [("x", c_int),
                        ("p", POINTER(c_int))]

        s = S()
        s.x = 12345678
        s.p = Nic
        self.assertEqual(s.x, 12345678)

klasa TestRecursiveStructure(unittest.TestCase):
    def test_contains_itself(self):
        klasa Recursive(Structure):
            dalej

        spróbuj:
            Recursive._fields_ = [("next", Recursive)]
        wyjąwszy AttributeError jako details:
            self.assertIn("Structure albo union cannot contain itself",
                          str(details))
        inaczej:
            self.fail("Structure albo union cannot contain itself")


    def test_vice_versa(self):
        klasa First(Structure):
            dalej
        klasa Second(Structure):
            dalej

        First._fields_ = [("second", Second)]

        spróbuj:
            Second._fields_ = [("first", First)]
        wyjąwszy AttributeError jako details:
            self.assertIn("_fields_ jest final", str(details))
        inaczej:
            self.fail("AttributeError nie podnieśd")

jeżeli __name__ == '__main__':
    unittest.main()
