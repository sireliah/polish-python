z collections zaimportuj abc
zaimportuj array
zaimportuj operator
zaimportuj unittest
zaimportuj struct
zaimportuj sys

z test zaimportuj support

ISBIGENDIAN = sys.byteorder == "big"

integer_codes = 'b', 'B', 'h', 'H', 'i', 'I', 'l', 'L', 'q', 'Q', 'n', 'N'
byteorders = '', '@', '=', '<', '>', '!'

def iter_integer_formats(byteorders=byteorders):
    dla code w integer_codes:
        dla byteorder w byteorders:
            jeżeli (byteorder w ('', '@') oraz code w ('q', 'Q') oraz
                nie HAVE_LONG_LONG):
                kontynuuj
            jeżeli (byteorder nie w ('', '@') oraz code w ('n', 'N')):
                kontynuuj
            uzyskaj code, byteorder

# Native 'q' packing isn't available on systems that don't have the C
# long long type.
spróbuj:
    struct.pack('q', 5)
wyjąwszy struct.error:
    HAVE_LONG_LONG = Nieprawda
inaczej:
    HAVE_LONG_LONG = Prawda

def string_reverse(s):
    zwróć s[::-1]

def bigendian_to_native(value):
    jeżeli ISBIGENDIAN:
        zwróć value
    inaczej:
        zwróć string_reverse(value)

klasa StructTest(unittest.TestCase):
    def test_isbigendian(self):
        self.assertEqual((struct.pack('=i', 1)[0] == 0), ISBIGENDIAN)

    def test_consistence(self):
        self.assertRaises(struct.error, struct.calcsize, 'Z')

        sz = struct.calcsize('i')
        self.assertEqual(sz * 3, struct.calcsize('iii'))

        fmt = 'cbxxxxxxhhhhiillffd?'
        fmt3 = '3c3b18x12h6i6l6f3d3?'
        sz = struct.calcsize(fmt)
        sz3 = struct.calcsize(fmt3)
        self.assertEqual(sz * 3, sz3)

        self.assertRaises(struct.error, struct.pack, 'iii', 3)
        self.assertRaises(struct.error, struct.pack, 'i', 3, 3, 3)
        self.assertRaises((TypeError, struct.error), struct.pack, 'i', 'foo')
        self.assertRaises((TypeError, struct.error), struct.pack, 'P', 'foo')
        self.assertRaises(struct.error, struct.unpack, 'd', b'flap')
        s = struct.pack('ii', 1, 2)
        self.assertRaises(struct.error, struct.unpack, 'iii', s)
        self.assertRaises(struct.error, struct.unpack, 'i', s)

    def test_transitiveness(self):
        c = b'a'
        b = 1
        h = 255
        i = 65535
        l = 65536
        f = 3.1415
        d = 3.1415
        t = Prawda

        dla prefix w ('', '@', '<', '>', '=', '!'):
            dla format w ('xcbhilfd?', 'xcBHILfd?'):
                format = prefix + format
                s = struct.pack(format, c, b, h, i, l, f, d, t)
                cp, bp, hp, ip, lp, fp, dp, tp = struct.unpack(format, s)
                self.assertEqual(cp, c)
                self.assertEqual(bp, b)
                self.assertEqual(hp, h)
                self.assertEqual(ip, i)
                self.assertEqual(lp, l)
                self.assertEqual(int(100 * fp), int(100 * f))
                self.assertEqual(int(100 * dp), int(100 * d))
                self.assertEqual(tp, t)

    def test_new_features(self):
        # Test some of the new features w detail
        # (format, argument, big-endian result, little-endian result, asymmetric)
        tests = [
            ('c', b'a', b'a', b'a', 0),
            ('xc', b'a', b'\0a', b'\0a', 0),
            ('cx', b'a', b'a\0', b'a\0', 0),
            ('s', b'a', b'a', b'a', 0),
            ('0s', b'helloworld', b'', b'', 1),
            ('1s', b'helloworld', b'h', b'h', 1),
            ('9s', b'helloworld', b'helloworl', b'helloworl', 1),
            ('10s', b'helloworld', b'helloworld', b'helloworld', 0),
            ('11s', b'helloworld', b'helloworld\0', b'helloworld\0', 1),
            ('20s', b'helloworld', b'helloworld'+10*b'\0', b'helloworld'+10*b'\0', 1),
            ('b', 7, b'\7', b'\7', 0),
            ('b', -7, b'\371', b'\371', 0),
            ('B', 7, b'\7', b'\7', 0),
            ('B', 249, b'\371', b'\371', 0),
            ('h', 700, b'\002\274', b'\274\002', 0),
            ('h', -700, b'\375D', b'D\375', 0),
            ('H', 700, b'\002\274', b'\274\002', 0),
            ('H', 0x10000-700, b'\375D', b'D\375', 0),
            ('i', 70000000, b'\004,\035\200', b'\200\035,\004', 0),
            ('i', -70000000, b'\373\323\342\200', b'\200\342\323\373', 0),
            ('I', 70000000, b'\004,\035\200', b'\200\035,\004', 0),
            ('I', 0x100000000-70000000, b'\373\323\342\200', b'\200\342\323\373', 0),
            ('l', 70000000, b'\004,\035\200', b'\200\035,\004', 0),
            ('l', -70000000, b'\373\323\342\200', b'\200\342\323\373', 0),
            ('L', 70000000, b'\004,\035\200', b'\200\035,\004', 0),
            ('L', 0x100000000-70000000, b'\373\323\342\200', b'\200\342\323\373', 0),
            ('f', 2.0, b'@\000\000\000', b'\000\000\000@', 0),
            ('d', 2.0, b'@\000\000\000\000\000\000\000',
                       b'\000\000\000\000\000\000\000@', 0),
            ('f', -2.0, b'\300\000\000\000', b'\000\000\000\300', 0),
            ('d', -2.0, b'\300\000\000\000\000\000\000\000',
                        b'\000\000\000\000\000\000\000\300', 0),
            ('?', 0, b'\0', b'\0', 0),
            ('?', 3, b'\1', b'\1', 1),
            ('?', Prawda, b'\1', b'\1', 0),
            ('?', [], b'\0', b'\0', 1),
            ('?', (1,), b'\1', b'\1', 1),
        ]

        dla fmt, arg, big, lil, asy w tests:
            dla (xfmt, exp) w [('>'+fmt, big), ('!'+fmt, big), ('<'+fmt, lil),
                                ('='+fmt, ISBIGENDIAN oraz big albo lil)]:
                res = struct.pack(xfmt, arg)
                self.assertEqual(res, exp)
                self.assertEqual(struct.calcsize(xfmt), len(res))
                rev = struct.unpack(xfmt, res)[0]
                jeżeli rev != arg:
                    self.assertPrawda(asy)

    def test_calcsize(self):
        expected_size = {
            'b': 1, 'B': 1,
            'h': 2, 'H': 2,
            'i': 4, 'I': 4,
            'l': 4, 'L': 4,
            'q': 8, 'Q': 8,
            }

        # standard integer sizes
        dla code, byteorder w iter_integer_formats(('=', '<', '>', '!')):
            format = byteorder+code
            size = struct.calcsize(format)
            self.assertEqual(size, expected_size[code])

        # native integer sizes
        native_pairs = 'bB', 'hH', 'iI', 'lL', 'nN'
        jeżeli HAVE_LONG_LONG:
            native_pairs += 'qQ',
        dla format_pair w native_pairs:
            dla byteorder w '', '@':
                signed_size = struct.calcsize(byteorder + format_pair[0])
                unsigned_size = struct.calcsize(byteorder + format_pair[1])
                self.assertEqual(signed_size, unsigned_size)

        # bounds dla native integer sizes
        self.assertEqual(struct.calcsize('b'), 1)
        self.assertLessEqual(2, struct.calcsize('h'))
        self.assertLessEqual(4, struct.calcsize('l'))
        self.assertLessEqual(struct.calcsize('h'), struct.calcsize('i'))
        self.assertLessEqual(struct.calcsize('i'), struct.calcsize('l'))
        jeżeli HAVE_LONG_LONG:
            self.assertLessEqual(8, struct.calcsize('q'))
            self.assertLessEqual(struct.calcsize('l'), struct.calcsize('q'))
        self.assertGreaterEqual(struct.calcsize('n'), struct.calcsize('i'))
        self.assertGreaterEqual(struct.calcsize('n'), struct.calcsize('P'))

    def test_integers(self):
        # Integer tests (bBhHiIlLqQnN).
        zaimportuj binascii

        klasa IntTester(unittest.TestCase):
            def __init__(self, format):
                super(IntTester, self).__init__(methodName='test_one')
                self.format = format
                self.code = format[-1]
                self.byteorder = format[:-1]
                jeżeli nie self.byteorder w byteorders:
                    podnieś ValueError("unrecognized packing byteorder: %s" %
                                     self.byteorder)
                self.bytesize = struct.calcsize(format)
                self.bitsize = self.bytesize * 8
                jeżeli self.code w tuple('bhilqn'):
                    self.signed = Prawda
                    self.min_value = -(2**(self.bitsize-1))
                    self.max_value = 2**(self.bitsize-1) - 1
                albo_inaczej self.code w tuple('BHILQN'):
                    self.signed = Nieprawda
                    self.min_value = 0
                    self.max_value = 2**self.bitsize - 1
                inaczej:
                    podnieś ValueError("unrecognized format code: %s" %
                                     self.code)

            def test_one(self, x, pack=struct.pack,
                                  unpack=struct.unpack,
                                  unhexlify=binascii.unhexlify):

                format = self.format
                jeżeli self.min_value <= x <= self.max_value:
                    expected = x
                    jeżeli self.signed oraz x < 0:
                        expected += 1 << self.bitsize
                    self.assertGreaterEqual(expected, 0)
                    expected = '%x' % expected
                    jeżeli len(expected) & 1:
                        expected = "0" + expected
                    expected = expected.encode('ascii')
                    expected = unhexlify(expected)
                    expected = (b"\x00" * (self.bytesize - len(expected)) +
                                expected)
                    jeżeli (self.byteorder == '<' albo
                        self.byteorder w ('', '@', '=') oraz nie ISBIGENDIAN):
                        expected = string_reverse(expected)
                    self.assertEqual(len(expected), self.bytesize)

                    # Pack work?
                    got = pack(format, x)
                    self.assertEqual(got, expected)

                    # Unpack work?
                    retrieved = unpack(format, got)[0]
                    self.assertEqual(x, retrieved)

                    # Adding any byte should cause a "too big" error.
                    self.assertRaises((struct.error, TypeError), unpack, format,
                                                                 b'\x01' + got)
                inaczej:
                    # x jest out of range -- verify pack realizes that.
                    self.assertRaises((OverflowError, ValueError, struct.error),
                                      pack, format, x)

            def run(self):
                z random zaimportuj randrange

                # Create all interesting powers of 2.
                values = []
                dla exp w range(self.bitsize + 3):
                    values.append(1 << exp)

                # Add some random values.
                dla i w range(self.bitsize):
                    val = 0
                    dla j w range(self.bytesize):
                        val = (val << 8) | randrange(256)
                    values.append(val)

                # Values absorbed z other tests
                values.extend([300, 700000, sys.maxsize*4])

                # Try all those, oraz their negations, oraz +-1 from
                # them.  Note that this tests all power-of-2
                # boundaries w range, oraz a few out of range, plus
                # +-(2**n +- 1).
                dla base w values:
                    dla val w -base, base:
                        dla incr w -1, 0, 1:
                            x = val + incr
                            self.test_one(x)

                # Some error cases.
                klasa NotAnInt:
                    def __int__(self):
                        zwróć 42

                # Objects przy an '__index__' method should be allowed
                # to pack jako integers.  That jest assuming the implemented
                # '__index__' method returns an 'int'.
                klasa Indexable(object):
                    def __init__(self, value):
                        self._value = value

                    def __index__(self):
                        zwróć self._value

                # If the '__index__' method podnieśs a type error, then
                # '__int__' should be used przy a deprecation warning.
                klasa BadIndex(object):
                    def __index__(self):
                        podnieś TypeError

                    def __int__(self):
                        zwróć 42

                self.assertRaises((TypeError, struct.error),
                                  struct.pack, self.format,
                                  "a string")
                self.assertRaises((TypeError, struct.error),
                                  struct.pack, self.format,
                                  randrange)
                self.assertRaises((TypeError, struct.error),
                                  struct.pack, self.format,
                                  3+42j)
                self.assertRaises((TypeError, struct.error),
                                  struct.pack, self.format,
                                  NotAnInt())
                self.assertRaises((TypeError, struct.error),
                                  struct.pack, self.format,
                                  BadIndex())

                # Check dla legitimate values z '__index__'.
                dla obj w (Indexable(0), Indexable(10), Indexable(17),
                            Indexable(42), Indexable(100), Indexable(127)):
                    spróbuj:
                        struct.pack(format, obj)
                    wyjąwszy:
                        self.fail("integer code pack failed on object "
                                  "przy '__index__' method")

                # Check dla bogus values z '__index__'.
                dla obj w (Indexable(b'a'), Indexable('b'), Indexable(Nic),
                            Indexable({'a': 1}), Indexable([1, 2, 3])):
                    self.assertRaises((TypeError, struct.error),
                                      struct.pack, self.format,
                                      obj)

        dla code, byteorder w iter_integer_formats():
            format = byteorder+code
            t = IntTester(format)
            t.run()

    def test_nN_code(self):
        # n oraz N don't exist w standard sizes
        def assertStructError(func, *args, **kwargs):
            przy self.assertRaises(struct.error) jako cm:
                func(*args, **kwargs)
            self.assertIn("bad char w struct format", str(cm.exception))
        dla code w 'nN':
            dla byteorder w ('=', '<', '>', '!'):
                format = byteorder+code
                assertStructError(struct.calcsize, format)
                assertStructError(struct.pack, format, 0)
                assertStructError(struct.unpack, format, b"")

    def test_p_code(self):
        # Test p ("Pascal string") code.
        dla code, input, expected, expectedback w [
                ('p',  b'abc', b'\x00',            b''),
                ('1p', b'abc', b'\x00',            b''),
                ('2p', b'abc', b'\x01a',           b'a'),
                ('3p', b'abc', b'\x02ab',          b'ab'),
                ('4p', b'abc', b'\x03abc',         b'abc'),
                ('5p', b'abc', b'\x03abc\x00',     b'abc'),
                ('6p', b'abc', b'\x03abc\x00\x00', b'abc'),
                ('1000p', b'x'*1000, b'\xff' + b'x'*999, b'x'*255)]:
            got = struct.pack(code, input)
            self.assertEqual(got, expected)
            (got,) = struct.unpack(code, got)
            self.assertEqual(got, expectedback)

    def test_705836(self):
        # SF bug 705836.  "<f" oraz ">f" had a severe rounding bug, where a carry
        # z the low-order discarded bits could propagate into the exponent
        # field, causing the result to be wrong by a factor of 2.
        zaimportuj math

        dla base w range(1, 33):
            # smaller <- largest representable float less than base.
            delta = 0.5
            dopóki base - delta / 2.0 != base:
                delta /= 2.0
            smaller = base - delta
            # Packing this rounds away a solid string of trailing 1 bits.
            packed = struct.pack("<f", smaller)
            unpacked = struct.unpack("<f", packed)[0]
            # This failed at base = 2, 4, oraz 32, przy unpacked = 1, 2, oraz
            # 16, respectively.
            self.assertEqual(base, unpacked)
            bigpacked = struct.pack(">f", smaller)
            self.assertEqual(bigpacked, string_reverse(packed))
            unpacked = struct.unpack(">f", bigpacked)[0]
            self.assertEqual(base, unpacked)

        # Largest finite IEEE single.
        big = (1 << 24) - 1
        big = math.ldexp(big, 127 - 23)
        packed = struct.pack(">f", big)
        unpacked = struct.unpack(">f", packed)[0]
        self.assertEqual(big, unpacked)

        # The same, but tack on a 1 bit so it rounds up to infinity.
        big = (1 << 25) - 1
        big = math.ldexp(big, 127 - 24)
        self.assertRaises(OverflowError, struct.pack, ">f", big)

    def test_1530559(self):
        dla code, byteorder w iter_integer_formats():
            format = byteorder + code
            self.assertRaises(struct.error, struct.pack, format, 1.0)
            self.assertRaises(struct.error, struct.pack, format, 1.5)
        self.assertRaises(struct.error, struct.pack, 'P', 1.0)
        self.assertRaises(struct.error, struct.pack, 'P', 1.5)

    def test_unpack_from(self):
        test_string = b'abcd01234'
        fmt = '4s'
        s = struct.Struct(fmt)
        dla cls w (bytes, bytearray):
            data = cls(test_string)
            self.assertEqual(s.unpack_from(data), (b'abcd',))
            self.assertEqual(s.unpack_from(data, 2), (b'cd01',))
            self.assertEqual(s.unpack_from(data, 4), (b'0123',))
            dla i w range(6):
                self.assertEqual(s.unpack_from(data, i), (data[i:i+4],))
            dla i w range(6, len(test_string) + 1):
                self.assertRaises(struct.error, s.unpack_from, data, i)
        dla cls w (bytes, bytearray):
            data = cls(test_string)
            self.assertEqual(struct.unpack_from(fmt, data), (b'abcd',))
            self.assertEqual(struct.unpack_from(fmt, data, 2), (b'cd01',))
            self.assertEqual(struct.unpack_from(fmt, data, 4), (b'0123',))
            dla i w range(6):
                self.assertEqual(struct.unpack_from(fmt, data, i), (data[i:i+4],))
            dla i w range(6, len(test_string) + 1):
                self.assertRaises(struct.error, struct.unpack_from, fmt, data, i)

    def test_pack_into(self):
        test_string = b'Reykjavik rocks, eow!'
        writable_buf = array.array('b', b' '*100)
        fmt = '21s'
        s = struct.Struct(fmt)

        # Test without offset
        s.pack_into(writable_buf, 0, test_string)
        from_buf = writable_buf.tobytes()[:len(test_string)]
        self.assertEqual(from_buf, test_string)

        # Test przy offset.
        s.pack_into(writable_buf, 10, test_string)
        from_buf = writable_buf.tobytes()[:len(test_string)+10]
        self.assertEqual(from_buf, test_string[:10] + test_string)

        # Go beyond boundaries.
        small_buf = array.array('b', b' '*10)
        self.assertRaises((ValueError, struct.error), s.pack_into, small_buf, 0,
                          test_string)
        self.assertRaises((ValueError, struct.error), s.pack_into, small_buf, 2,
                          test_string)

        # Test bogus offset (issue 3694)
        sb = small_buf
        self.assertRaises((TypeError, struct.error), struct.pack_into, b'', sb,
                          Nic)

    def test_pack_into_fn(self):
        test_string = b'Reykjavik rocks, eow!'
        writable_buf = array.array('b', b' '*100)
        fmt = '21s'
        pack_into = lambda *args: struct.pack_into(fmt, *args)

        # Test without offset.
        pack_into(writable_buf, 0, test_string)
        from_buf = writable_buf.tobytes()[:len(test_string)]
        self.assertEqual(from_buf, test_string)

        # Test przy offset.
        pack_into(writable_buf, 10, test_string)
        from_buf = writable_buf.tobytes()[:len(test_string)+10]
        self.assertEqual(from_buf, test_string[:10] + test_string)

        # Go beyond boundaries.
        small_buf = array.array('b', b' '*10)
        self.assertRaises((ValueError, struct.error), pack_into, small_buf, 0,
                          test_string)
        self.assertRaises((ValueError, struct.error), pack_into, small_buf, 2,
                          test_string)

    def test_unpack_with_buffer(self):
        # SF bug 1563759: struct.unpack doesn't support buffer protocol objects
        data1 = array.array('B', b'\x12\x34\x56\x78')
        data2 = memoryview(b'\x12\x34\x56\x78') # XXX b'......XXXX......', 6, 4
        dla data w [data1, data2]:
            value, = struct.unpack('>I', data)
            self.assertEqual(value, 0x12345678)

    def test_bool(self):
        klasa ExplodingBool(object):
            def __bool__(self):
                podnieś OSError
        dla prefix w tuple("<>!=")+('',):
            false = (), [], [], '', 0
            true = [1], 'test', 5, -1, 0xffffffff+1, 0xffffffff/2

            falseFormat = prefix + '?' * len(false)
            packedNieprawda = struct.pack(falseFormat, *false)
            unpackedNieprawda = struct.unpack(falseFormat, packedNieprawda)

            trueFormat = prefix + '?' * len(true)
            packedPrawda = struct.pack(trueFormat, *true)
            unpackedPrawda = struct.unpack(trueFormat, packedPrawda)

            self.assertEqual(len(true), len(unpackedPrawda))
            self.assertEqual(len(false), len(unpackedNieprawda))

            dla t w unpackedNieprawda:
                self.assertNieprawda(t)
            dla t w unpackedPrawda:
                self.assertPrawda(t)

            packed = struct.pack(prefix+'?', 1)

            self.assertEqual(len(packed), struct.calcsize(prefix+'?'))

            jeżeli len(packed) != 1:
                self.assertNieprawda(prefix, msg='encoded bool jest nie one byte: %r'
                                             %packed)

            spróbuj:
                struct.pack(prefix + '?', ExplodingBool())
            wyjąwszy OSError:
                dalej
            inaczej:
                self.fail("Expected OSError: struct.pack(%r, "
                          "ExplodingBool())" % (prefix + '?'))

        dla c w [b'\x01', b'\x7f', b'\xff', b'\x0f', b'\xf0']:
            self.assertPrawda(struct.unpack('>?', c)[0])

    def test_count_overflow(self):
        hugecount = '{}b'.format(sys.maxsize+1)
        self.assertRaises(struct.error, struct.calcsize, hugecount)

        hugecount2 = '{}b{}H'.format(sys.maxsize//2, sys.maxsize//2)
        self.assertRaises(struct.error, struct.calcsize, hugecount2)

    def test_trailing_counter(self):
        store = array.array('b', b' '*100)

        # format lists containing only count spec should result w an error
        self.assertRaises(struct.error, struct.pack, '12345')
        self.assertRaises(struct.error, struct.unpack, '12345', '')
        self.assertRaises(struct.error, struct.pack_into, '12345', store, 0)
        self.assertRaises(struct.error, struct.unpack_from, '12345', store, 0)

        # Format lists przy trailing count spec should result w an error
        self.assertRaises(struct.error, struct.pack, 'c12345', 'x')
        self.assertRaises(struct.error, struct.unpack, 'c12345', 'x')
        self.assertRaises(struct.error, struct.pack_into, 'c12345', store, 0,
                           'x')
        self.assertRaises(struct.error, struct.unpack_from, 'c12345', store,
                           0)

        # Mixed format tests
        self.assertRaises(struct.error, struct.pack, '14s42', 'spam oraz eggs')
        self.assertRaises(struct.error, struct.unpack, '14s42',
                          'spam oraz eggs')
        self.assertRaises(struct.error, struct.pack_into, '14s42', store, 0,
                          'spam oraz eggs')
        self.assertRaises(struct.error, struct.unpack_from, '14s42', store, 0)

    def test_Struct_reinitialization(self):
        # Issue 9422: there was a memory leak when reinitializing a
        # Struct instance.  This test can be used to detect the leak
        # when running przy regrtest -L.
        s = struct.Struct('i')
        s.__init__('ii')

    def check_sizeof(self, format_str, number_of_codes):
        # The size of 'PyStructObject'
        totalsize = support.calcobjsize('2n3P')
        # The size taken up by the 'formatcode' dynamic array
        totalsize += struct.calcsize('P3n0P') * (number_of_codes + 1)
        support.check_sizeof(self, struct.Struct(format_str), totalsize)

    @support.cpython_only
    def test__sizeof__(self):
        dla code w integer_codes:
            self.check_sizeof(code, 1)
        self.check_sizeof('BHILfdspP', 9)
        self.check_sizeof('B' * 1234, 1234)
        self.check_sizeof('fd', 2)
        self.check_sizeof('xxxxxxxxxxxxxx', 0)
        self.check_sizeof('100H', 1)
        self.check_sizeof('187s', 1)
        self.check_sizeof('20p', 1)
        self.check_sizeof('0s', 1)
        self.check_sizeof('0c', 0)


klasa UnpackIteratorTest(unittest.TestCase):
    """
    Tests dla iterative unpacking (struct.Struct.iter_unpack).
    """

    def test_construct(self):
        def _check_iterator(it):
            self.assertIsInstance(it, abc.Iterator)
            self.assertIsInstance(it, abc.Iterable)
        s = struct.Struct('>ibcp')
        it = s.iter_unpack(b"")
        _check_iterator(it)
        it = s.iter_unpack(b"1234567")
        _check_iterator(it)
        # Wrong bytes length
        przy self.assertRaises(struct.error):
            s.iter_unpack(b"123456")
        przy self.assertRaises(struct.error):
            s.iter_unpack(b"12345678")
        # Zero-length struct
        s = struct.Struct('>')
        przy self.assertRaises(struct.error):
            s.iter_unpack(b"")
        przy self.assertRaises(struct.error):
            s.iter_unpack(b"12")

    def test_iterate(self):
        s = struct.Struct('>IB')
        b = bytes(range(1, 16))
        it = s.iter_unpack(b)
        self.assertEqual(next(it), (0x01020304, 5))
        self.assertEqual(next(it), (0x06070809, 10))
        self.assertEqual(next(it), (0x0b0c0d0e, 15))
        self.assertRaises(StopIteration, next, it)
        self.assertRaises(StopIteration, next, it)

    def test_arbitrary_buffer(self):
        s = struct.Struct('>IB')
        b = bytes(range(1, 11))
        it = s.iter_unpack(memoryview(b))
        self.assertEqual(next(it), (0x01020304, 5))
        self.assertEqual(next(it), (0x06070809, 10))
        self.assertRaises(StopIteration, next, it)
        self.assertRaises(StopIteration, next, it)

    def test_length_hint(self):
        lh = operator.length_hint
        s = struct.Struct('>IB')
        b = bytes(range(1, 16))
        it = s.iter_unpack(b)
        self.assertEqual(lh(it), 3)
        next(it)
        self.assertEqual(lh(it), 2)
        next(it)
        self.assertEqual(lh(it), 1)
        next(it)
        self.assertEqual(lh(it), 0)
        self.assertRaises(StopIteration, next, it)
        self.assertEqual(lh(it), 0)

    def test_module_func(self):
        # Sanity check dla the global struct.iter_unpack()
        it = struct.iter_unpack('>IB', bytes(range(1, 11)))
        self.assertEqual(next(it), (0x01020304, 5))
        self.assertEqual(next(it), (0x06070809, 10))
        self.assertRaises(StopIteration, next, it)
        self.assertRaises(StopIteration, next, it)


jeżeli __name__ == '__main__':
    unittest.main()
