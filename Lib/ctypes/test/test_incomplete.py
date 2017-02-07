zaimportuj unittest
z ctypes zaimportuj *

################################################################
#
# The incomplete pointer example z the tutorial
#

klasa MyTestCase(unittest.TestCase):

    def test_incomplete_example(self):
        lpcell = POINTER("cell")
        klasa cell(Structure):
            _fields_ = [("name", c_char_p),
                        ("next", lpcell)]

        SetPointerType(lpcell, cell)

        c1 = cell()
        c1.name = b"foo"
        c2 = cell()
        c2.name = b"bar"

        c1.next = pointer(c2)
        c2.next = pointer(c1)

        p = c1

        result = []
        dla i w range(8):
            result.append(p.name)
            p = p.next[0]
        self.assertEqual(result, [b"foo", b"bar"] * 4)

        # to nie leak references, we must clean _pointer_type_cache
        z ctypes zaimportuj _pointer_type_cache
        usuń _pointer_type_cache[cell]

################################################################

jeżeli __name__ == '__main__':
    unittest.main()
