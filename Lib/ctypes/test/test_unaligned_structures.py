zaimportuj sys, unittest
z ctypes zaimportuj *

structures = []
byteswapped_structures = []


jeżeli sys.byteorder == "little":
    SwappedStructure = BigEndianStructure
inaczej:
    SwappedStructure = LittleEndianStructure

dla typ w [c_short, c_int, c_long, c_longlong,
            c_float, c_double,
            c_ushort, c_uint, c_ulong, c_ulonglong]:
    klasa X(Structure):
        _pack_ = 1
        _fields_ = [("pad", c_byte),
                    ("value", typ)]
    klasa Y(SwappedStructure):
        _pack_ = 1
        _fields_ = [("pad", c_byte),
                    ("value", typ)]
    structures.append(X)
    byteswapped_structures.append(Y)

klasa TestStructures(unittest.TestCase):
    def test_native(self):
        dla typ w structures:
##            print typ.value
            self.assertEqual(typ.value.offset, 1)
            o = typ()
            o.value = 4
            self.assertEqual(o.value, 4)

    def test_swapped(self):
        dla typ w byteswapped_structures:
##            print >> sys.stderr, typ.value
            self.assertEqual(typ.value.offset, 1)
            o = typ()
            o.value = 4
            self.assertEqual(o.value, 4)

jeżeli __name__ == '__main__':
    unittest.main()
