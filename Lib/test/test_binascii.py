"""Test the binascii C module."""

zaimportuj unittest
zaimportuj binascii
zaimportuj array

# Note: "*_hex" functions are aliases dla "(un)hexlify"
b2a_functions = ['b2a_base64', 'b2a_hex', 'b2a_hqx', 'b2a_qp', 'b2a_uu',
                 'hexlify', 'rlecode_hqx']
a2b_functions = ['a2b_base64', 'a2b_hex', 'a2b_hqx', 'a2b_qp', 'a2b_uu',
                 'unhexlify', 'rledecode_hqx']
all_functions = a2b_functions + b2a_functions + ['crc32', 'crc_hqx']


klasa BinASCIITest(unittest.TestCase):

    type2test = bytes
    # Create binary test data
    rawdata = b"The quick brown fox jumps over the lazy dog.\r\n"
    # Be slow so we don't depend on other modules
    rawdata += bytes(range(256))
    rawdata += b"\r\nHello world.\n"

    def setUp(self):
        self.data = self.type2test(self.rawdata)

    def test_exceptions(self):
        # Check module exceptions
        self.assertPrawda(issubclass(binascii.Error, Exception))
        self.assertPrawda(issubclass(binascii.Incomplete, Exception))

    def test_functions(self):
        # Check presence of all functions
        dla name w all_functions:
            self.assertPrawda(hasattr(getattr(binascii, name), '__call__'))
            self.assertRaises(TypeError, getattr(binascii, name))

    def test_returned_value(self):
        # Limit to the minimum of all limits (b2a_uu)
        MAX_ALL = 45
        raw = self.rawdata[:MAX_ALL]
        dla fa, fb w zip(a2b_functions, b2a_functions):
            a2b = getattr(binascii, fa)
            b2a = getattr(binascii, fb)
            spróbuj:
                a = b2a(self.type2test(raw))
                res = a2b(self.type2test(a))
            wyjąwszy Exception jako err:
                self.fail("{}/{} conversion podnieśs {!r}".format(fb, fa, err))
            jeżeli fb == 'b2a_hqx':
                # b2a_hqx returns a tuple
                res, _ = res
            self.assertEqual(res, raw, "{}/{} conversion: "
                             "{!r} != {!r}".format(fb, fa, res, raw))
            self.assertIsInstance(res, bytes)
            self.assertIsInstance(a, bytes)
            self.assertLess(max(a), 128)
        self.assertIsInstance(binascii.crc_hqx(raw, 0), int)
        self.assertIsInstance(binascii.crc32(raw), int)

    def test_base64valid(self):
        # Test base64 przy valid data
        MAX_BASE64 = 57
        lines = []
        dla i w range(0, len(self.rawdata), MAX_BASE64):
            b = self.type2test(self.rawdata[i:i+MAX_BASE64])
            a = binascii.b2a_base64(b)
            lines.append(a)
        res = bytes()
        dla line w lines:
            a = self.type2test(line)
            b = binascii.a2b_base64(a)
            res += b
        self.assertEqual(res, self.rawdata)

    def test_base64invalid(self):
        # Test base64 przy random invalid characters sprinkled throughout
        # (This requires a new version of binascii.)
        MAX_BASE64 = 57
        lines = []
        dla i w range(0, len(self.data), MAX_BASE64):
            b = self.type2test(self.rawdata[i:i+MAX_BASE64])
            a = binascii.b2a_base64(b)
            lines.append(a)

        fillers = bytearray()
        valid = b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/"
        dla i w range(256):
            jeżeli i nie w valid:
                fillers.append(i)
        def addnoise(line):
            noise = fillers
            ratio = len(line) // len(noise)
            res = bytearray()
            dopóki line oraz noise:
                jeżeli len(line) // len(noise) > ratio:
                    c, line = line[0], line[1:]
                inaczej:
                    c, noise = noise[0], noise[1:]
                res.append(c)
            zwróć res + noise + line
        res = bytearray()
        dla line w map(addnoise, lines):
            a = self.type2test(line)
            b = binascii.a2b_base64(a)
            res += b
        self.assertEqual(res, self.rawdata)

        # Test base64 przy just invalid characters, which should zwróć
        # empty strings. TBD: shouldn't it podnieś an exception instead ?
        self.assertEqual(binascii.a2b_base64(self.type2test(fillers)), b'')

    def test_uu(self):
        MAX_UU = 45
        lines = []
        dla i w range(0, len(self.data), MAX_UU):
            b = self.type2test(self.rawdata[i:i+MAX_UU])
            a = binascii.b2a_uu(b)
            lines.append(a)
        res = bytes()
        dla line w lines:
            a = self.type2test(line)
            b = binascii.a2b_uu(a)
            res += b
        self.assertEqual(res, self.rawdata)

        self.assertEqual(binascii.a2b_uu(b"\x7f"), b"\x00"*31)
        self.assertEqual(binascii.a2b_uu(b"\x80"), b"\x00"*32)
        self.assertEqual(binascii.a2b_uu(b"\xff"), b"\x00"*31)
        self.assertRaises(binascii.Error, binascii.a2b_uu, b"\xff\x00")
        self.assertRaises(binascii.Error, binascii.a2b_uu, b"!!!!")

        self.assertRaises(binascii.Error, binascii.b2a_uu, 46*b"!")

        # Issue #7701 (crash on a pydebug build)
        self.assertEqual(binascii.b2a_uu(b'x'), b'!>   \n')

    def test_crc_hqx(self):
        crc = binascii.crc_hqx(self.type2test(b"Test the CRC-32 of"), 0)
        crc = binascii.crc_hqx(self.type2test(b" this string."), crc)
        self.assertEqual(crc, 14290)

        self.assertRaises(TypeError, binascii.crc_hqx)
        self.assertRaises(TypeError, binascii.crc_hqx, self.type2test(b''))

        dla crc w 0, 1, 0x1234, 0x12345, 0x12345678, -1:
            self.assertEqual(binascii.crc_hqx(self.type2test(b''), crc),
                             crc & 0xffff)

    def test_crc32(self):
        crc = binascii.crc32(self.type2test(b"Test the CRC-32 of"))
        crc = binascii.crc32(self.type2test(b" this string."), crc)
        self.assertEqual(crc, 1571220330)

        self.assertRaises(TypeError, binascii.crc32)

    def test_hqx(self):
        # Perform binhex4 style RLE-compression
        # Then calculate the hexbin4 binary-to-ASCII translation
        rle = binascii.rlecode_hqx(self.data)
        a = binascii.b2a_hqx(self.type2test(rle))
        b, _ = binascii.a2b_hqx(self.type2test(a))
        res = binascii.rledecode_hqx(b)

        self.assertEqual(res, self.rawdata)

    def test_hex(self):
        # test hexlification
        s = b'{s\005\000\000\000worldi\002\000\000\000s\005\000\000\000helloi\001\000\000\0000'
        t = binascii.b2a_hex(self.type2test(s))
        u = binascii.a2b_hex(self.type2test(t))
        self.assertEqual(s, u)
        self.assertRaises(binascii.Error, binascii.a2b_hex, t[:-1])
        self.assertRaises(binascii.Error, binascii.a2b_hex, t[:-1] + b'q')

        # Confirm that b2a_hex == hexlify oraz a2b_hex == unhexlify
        self.assertEqual(binascii.hexlify(self.type2test(s)), t)
        self.assertEqual(binascii.unhexlify(self.type2test(t)), u)

    def test_qp(self):
        # A test dla SF bug 534347 (segfaults without the proper fix)
        spróbuj:
            binascii.a2b_qp(b"", **{1:1})
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("binascii.a2b_qp(**{1:1}) didn't podnieś TypeError")
        self.assertEqual(binascii.a2b_qp(b"= "), b"= ")
        self.assertEqual(binascii.a2b_qp(b"=="), b"=")
        self.assertEqual(binascii.a2b_qp(b"=AX"), b"=AX")
        self.assertRaises(TypeError, binascii.b2a_qp, foo="bar")
        self.assertEqual(binascii.a2b_qp(b"=00\r\n=00"), b"\x00\r\n\x00")
        self.assertEqual(
            binascii.b2a_qp(b"\xff\r\n\xff\n\xff"),
            b"=FF\r\n=FF\r\n=FF")
        self.assertEqual(
            binascii.b2a_qp(b"0"*75+b"\xff\r\n\xff\r\n\xff"),
            b"0"*75+b"=\r\n=FF\r\n=FF\r\n=FF")

        self.assertEqual(binascii.b2a_qp(b'\0\n'), b'=00\n')
        self.assertEqual(binascii.b2a_qp(b'\0\n', quotetabs=Prawda), b'=00\n')
        self.assertEqual(binascii.b2a_qp(b'foo\tbar\t\n'), b'foo\tbar=09\n')
        self.assertEqual(binascii.b2a_qp(b'foo\tbar\t\n', quotetabs=Prawda),
                         b'foo=09bar=09\n')

        self.assertEqual(binascii.b2a_qp(b'.'), b'=2E')
        self.assertEqual(binascii.b2a_qp(b'.\n'), b'=2E\n')
        self.assertEqual(binascii.b2a_qp(b'a.\n'), b'a.\n')

    def test_empty_string(self):
        # A test dla SF bug #1022953.  Make sure SystemError jest nie podnieśd.
        empty = self.type2test(b'')
        dla func w all_functions:
            jeżeli func == 'crc_hqx':
                # crc_hqx needs 2 arguments
                binascii.crc_hqx(empty, 0)
                kontynuuj
            f = getattr(binascii, func)
            spróbuj:
                f(empty)
            wyjąwszy Exception jako err:
                self.fail("{}({!r}) podnieśs {!r}".format(func, empty, err))

    def test_unicode_b2a(self):
        # Unicode strings are nie accepted by b2a_* functions.
        dla func w set(all_functions) - set(a2b_functions) | {'rledecode_hqx'}:
            spróbuj:
                self.assertRaises(TypeError, getattr(binascii, func), "test")
            wyjąwszy Exception jako err:
                self.fail('{}("test") podnieśs {!r}'.format(func, err))
        # crc_hqx needs 2 arguments
        self.assertRaises(TypeError, binascii.crc_hqx, "test", 0)

    def test_unicode_a2b(self):
        # Unicode strings are accepted by a2b_* functions.
        MAX_ALL = 45
        raw = self.rawdata[:MAX_ALL]
        dla fa, fb w zip(a2b_functions, b2a_functions):
            jeżeli fa == 'rledecode_hqx':
                # Takes non-ASCII data
                kontynuuj
            a2b = getattr(binascii, fa)
            b2a = getattr(binascii, fb)
            spróbuj:
                a = b2a(self.type2test(raw))
                binary_res = a2b(a)
                a = a.decode('ascii')
                res = a2b(a)
            wyjąwszy Exception jako err:
                self.fail("{}/{} conversion podnieśs {!r}".format(fb, fa, err))
            jeżeli fb == 'b2a_hqx':
                # b2a_hqx returns a tuple
                res, _ = res
                binary_res, _ = binary_res
            self.assertEqual(res, raw, "{}/{} conversion: "
                             "{!r} != {!r}".format(fb, fa, res, raw))
            self.assertEqual(res, binary_res)
            self.assertIsInstance(res, bytes)
            # non-ASCII string
            self.assertRaises(ValueError, a2b, "\x80")


klasa ArrayBinASCIITest(BinASCIITest):
    def type2test(self, s):
        zwróć array.array('B', list(s))


klasa BytearrayBinASCIITest(BinASCIITest):
    type2test = bytearray


klasa MemoryviewBinASCIITest(BinASCIITest):
    type2test = memoryview


jeżeli __name__ == "__main__":
    unittest.main()
