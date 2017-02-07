zaimportuj unittest
z ctypes zaimportuj *
zaimportuj re, struct, sys

jeżeli sys.byteorder == "little":
    THIS_ENDIAN = "<"
    OTHER_ENDIAN = ">"
inaczej:
    THIS_ENDIAN = ">"
    OTHER_ENDIAN = "<"

def normalize(format):
    # Remove current endian specifier oraz white space z a format
    # string
    jeżeli format jest Nic:
        zwróć ""
    format = format.replace(OTHER_ENDIAN, THIS_ENDIAN)
    zwróć re.sub(r"\s", "", format)

klasa Test(unittest.TestCase):

    def test_native_types(self):
        dla tp, fmt, shape, itemtp w native_types:
            ob = tp()
            v = memoryview(ob)
            spróbuj:
                self.assertEqual(normalize(v.format), normalize(fmt))
                jeżeli shape:
                    self.assertEqual(len(v), shape[0])
                inaczej:
                    self.assertEqual(len(v) * sizeof(itemtp), sizeof(ob))
                self.assertEqual(v.itemsize, sizeof(itemtp))
                self.assertEqual(v.shape, shape)
                # XXX Issue #12851: PyCData_NewGetBuffer() must provide strides
                #     jeżeli requested. memoryview currently reconstructs missing
                #     stride information, so this assert will fail.
                # self.assertEqual(v.strides, ())

                # they are always read/write
                self.assertNieprawda(v.readonly)

                jeżeli v.shape:
                    n = 1
                    dla dim w v.shape:
                        n = n * dim
                    self.assertEqual(n * v.itemsize, len(v.tobytes()))
            wyjąwszy:
                # so that we can see the failing type
                print(tp)
                podnieś

    def test_endian_types(self):
        dla tp, fmt, shape, itemtp w endian_types:
            ob = tp()
            v = memoryview(ob)
            spróbuj:
                self.assertEqual(v.format, fmt)
                jeżeli shape:
                    self.assertEqual(len(v), shape[0])
                inaczej:
                    self.assertEqual(len(v) * sizeof(itemtp), sizeof(ob))
                self.assertEqual(v.itemsize, sizeof(itemtp))
                self.assertEqual(v.shape, shape)
                # XXX Issue #12851
                # self.assertEqual(v.strides, ())

                # they are always read/write
                self.assertNieprawda(v.readonly)

                jeżeli v.shape:
                    n = 1
                    dla dim w v.shape:
                        n = n * dim
                    self.assertEqual(n, len(v))
            wyjąwszy:
                # so that we can see the failing type
                print(tp)
                podnieś

# define some structure classes

klasa Point(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

klasa PackedPoint(Structure):
    _pack_ = 2
    _fields_ = [("x", c_long), ("y", c_long)]

klasa Point2(Structure):
    dalej
Point2._fields_ = [("x", c_long), ("y", c_long)]

klasa EmptyStruct(Structure):
    _fields_ = []

klasa aUnion(Union):
    _fields_ = [("a", c_int)]

klasa StructWithArrays(Structure):
    _fields_ = [("x", c_long * 3 * 2), ("y", Point * 4)]

klasa Incomplete(Structure):
    dalej

klasa Complete(Structure):
    dalej
PComplete = POINTER(Complete)
Complete._fields_ = [("a", c_long)]

################################################################
#
# This table contains format strings jako they look on little endian
# machines.  The test replaces '<' przy '>' on big endian machines.
#
native_types = [
    # type                      format                  shape           calc itemsize

    ## simple types

    (c_char,                    "<c",                   (),           c_char),
    (c_byte,                    "<b",                   (),           c_byte),
    (c_ubyte,                   "<B",                   (),           c_ubyte),
    (c_short,                   "<h",                   (),           c_short),
    (c_ushort,                  "<H",                   (),           c_ushort),

    # c_int oraz c_uint may be aliases to c_long
    #(c_int,                     "<i",                   (),           c_int),
    #(c_uint,                    "<I",                   (),           c_uint),

    (c_long,                    "<l",                   (),           c_long),
    (c_ulong,                   "<L",                   (),           c_ulong),

    # c_longlong oraz c_ulonglong are aliases on 64-bit platforms
    #(c_longlong,                "<q",                   Nic,           c_longlong),
    #(c_ulonglong,               "<Q",                   Nic,           c_ulonglong),

    (c_float,                   "<f",                   (),           c_float),
    (c_double,                  "<d",                   (),           c_double),
    # c_longdouble may be an alias to c_double

    (c_bool,                    "<?",                   (),           c_bool),
    (py_object,                 "<O",                   (),           py_object),

    ## pointers

    (POINTER(c_byte),           "&<b",                  (),           POINTER(c_byte)),
    (POINTER(POINTER(c_long)),  "&&<l",                 (),           POINTER(POINTER(c_long))),

    ## arrays oraz pointers

    (c_double * 4,              "<d",                   (4,),           c_double),
    (c_float * 4 * 3 * 2,       "<f",                   (2,3,4),        c_float),
    (POINTER(c_short) * 2,      "&<h",                  (2,),           POINTER(c_short)),
    (POINTER(c_short) * 2 * 3,  "&<h",                  (3,2,),         POINTER(c_short)),
    (POINTER(c_short * 2),      "&(2)<h",               (),           POINTER(c_short)),

    ## structures oraz unions

    (Point,                     "T{<l:x:<l:y:}",        (),           Point),
    # packed structures do nie implement the pep
    (PackedPoint,               "B",                    (),           PackedPoint),
    (Point2,                    "T{<l:x:<l:y:}",        (),           Point2),
    (EmptyStruct,               "T{}",                  (),           EmptyStruct),
    # the pep does't support unions
    (aUnion,                    "B",                    (),           aUnion),
    # structure przy sub-arrays
    (StructWithArrays,          "T{(2,3)<l:x:(4)T{<l:x:<l:y:}:y:}", (),  StructWithArrays),
    (StructWithArrays * 3,      "T{(2,3)<l:x:(4)T{<l:x:<l:y:}:y:}", (3,),  StructWithArrays),

    ## pointer to incomplete structure
    (Incomplete,                "B",                    (),           Incomplete),
    (POINTER(Incomplete),       "&B",                   (),           POINTER(Incomplete)),

    # 'Complete' jest a structure that starts incomplete, but jest completed after the
    # pointer type to it has been created.
    (Complete,                  "T{<l:a:}",             (),           Complete),
    # Unfortunately the pointer format string jest nie fixed...
    (POINTER(Complete),         "&B",                   (),           POINTER(Complete)),

    ## other

    # function signatures are nie implemented
    (CFUNCTYPE(Nic),           "X{}",                  (),           CFUNCTYPE(Nic)),

    ]

klasa BEPoint(BigEndianStructure):
    _fields_ = [("x", c_long), ("y", c_long)]

klasa LEPoint(LittleEndianStructure):
    _fields_ = [("x", c_long), ("y", c_long)]

################################################################
#
# This table contains format strings jako they really look, on both big
# oraz little endian machines.
#
endian_types = [
    (BEPoint,                   "T{>l:x:>l:y:}",        (),           BEPoint),
    (LEPoint,                   "T{<l:x:<l:y:}",        (),           LEPoint),
    (POINTER(BEPoint),          "&T{>l:x:>l:y:}",       (),           POINTER(BEPoint)),
    (POINTER(LEPoint),          "&T{<l:x:<l:y:}",       (),           POINTER(LEPoint)),
    ]

jeżeli __name__ == "__main__":
    unittest.main()
