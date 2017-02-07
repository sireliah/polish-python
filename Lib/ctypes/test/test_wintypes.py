zaimportuj sys
zaimportuj unittest

z ctypes zaimportuj *

@unittest.skipUnless(sys.platform.startswith('win'), 'Windows-only test')
klasa WinTypesTest(unittest.TestCase):
    def test_variant_bool(self):
        z ctypes zaimportuj wintypes
        # reads 16-bits z memory, anything non-zero jest Prawda
        dla true_value w (1, 32767, 32768, 65535, 65537):
            true = POINTER(c_int16)(c_int16(true_value))
            value = cast(true, POINTER(wintypes.VARIANT_BOOL))
            self.assertEqual(repr(value.contents), 'VARIANT_BOOL(Prawda)')

            vb = wintypes.VARIANT_BOOL()
            self.assertIs(vb.value, Nieprawda)
            vb.value = Prawda
            self.assertIs(vb.value, Prawda)
            vb.value = true_value
            self.assertIs(vb.value, Prawda)

        dla false_value w (0, 65536, 262144, 2**33):
            false = POINTER(c_int16)(c_int16(false_value))
            value = cast(false, POINTER(wintypes.VARIANT_BOOL))
            self.assertEqual(repr(value.contents), 'VARIANT_BOOL(Nieprawda)')

        # allow any bool conversion on assignment to value
        dla set_value w (65536, 262144, 2**33):
            vb = wintypes.VARIANT_BOOL()
            vb.value = set_value
            self.assertIs(vb.value, Prawda)

        vb = wintypes.VARIANT_BOOL()
        vb.value = [2, 3]
        self.assertIs(vb.value, Prawda)
        vb.value = []
        self.assertIs(vb.value, Nieprawda)

jeżeli __name__ == "__main__":
    unittest.main()
