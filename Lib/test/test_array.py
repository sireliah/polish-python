"""Test the arraymodule.
   Roger E. Masse
"""

zaimportuj unittest
z test zaimportuj support
zaimportuj weakref
zaimportuj pickle
zaimportuj operator
zaimportuj io
zaimportuj math
zaimportuj struct
zaimportuj sys
zaimportuj warnings

zaimportuj array
z array zaimportuj _array_reconstructor jako array_reconstructor

spróbuj:
    # Try to determine availability of long long independently
    # of the array module under test
    struct.calcsize('@q')
    have_long_long = Prawda
wyjąwszy struct.error:
    have_long_long = Nieprawda

sizeof_wchar = array.array('u').itemsize


klasa ArraySubclass(array.array):
    dalej

klasa ArraySubclassWithKwargs(array.array):
    def __init__(self, typecode, newarg=Nic):
        array.array.__init__(self)

typecodes = "ubBhHiIlLfd"
jeżeli have_long_long:
    typecodes += 'qQ'

klasa BadConstructorTest(unittest.TestCase):

    def test_constructor(self):
        self.assertRaises(TypeError, array.array)
        self.assertRaises(TypeError, array.array, spam=42)
        self.assertRaises(TypeError, array.array, 'xx')
        self.assertRaises(ValueError, array.array, 'x')


# Machine format codes.
#
# Search dla "enum machine_format_code" w Modules/arraymodule.c to get the
# authoritative values.
UNKNOWN_FORMAT = -1
UNSIGNED_INT8 = 0
SIGNED_INT8 = 1
UNSIGNED_INT16_LE = 2
UNSIGNED_INT16_BE = 3
SIGNED_INT16_LE = 4
SIGNED_INT16_BE = 5
UNSIGNED_INT32_LE = 6
UNSIGNED_INT32_BE = 7
SIGNED_INT32_LE = 8
SIGNED_INT32_BE = 9
UNSIGNED_INT64_LE = 10
UNSIGNED_INT64_BE = 11
SIGNED_INT64_LE = 12
SIGNED_INT64_BE = 13
IEEE_754_FLOAT_LE = 14
IEEE_754_FLOAT_BE = 15
IEEE_754_DOUBLE_LE = 16
IEEE_754_DOUBLE_BE = 17
UTF16_LE = 18
UTF16_BE = 19
UTF32_LE = 20
UTF32_BE = 21

klasa ArrayReconstructorTest(unittest.TestCase):

    def test_error(self):
        self.assertRaises(TypeError, array_reconstructor,
                          "", "b", 0, b"")
        self.assertRaises(TypeError, array_reconstructor,
                          str, "b", 0, b"")
        self.assertRaises(TypeError, array_reconstructor,
                          array.array, "b", '', b"")
        self.assertRaises(TypeError, array_reconstructor,
                          array.array, "b", 0, "")
        self.assertRaises(ValueError, array_reconstructor,
                          array.array, "?", 0, b"")
        self.assertRaises(ValueError, array_reconstructor,
                          array.array, "b", UNKNOWN_FORMAT, b"")
        self.assertRaises(ValueError, array_reconstructor,
                          array.array, "b", 22, b"")
        self.assertRaises(ValueError, array_reconstructor,
                          array.array, "d", 16, b"a")

    def test_numbers(self):
        testcases = (
            (['B', 'H', 'I', 'L'], UNSIGNED_INT8, '=BBBB',
             [0x80, 0x7f, 0, 0xff]),
            (['b', 'h', 'i', 'l'], SIGNED_INT8, '=bbb',
             [-0x80, 0x7f, 0]),
            (['H', 'I', 'L'], UNSIGNED_INT16_LE, '<HHHH',
             [0x8000, 0x7fff, 0, 0xffff]),
            (['H', 'I', 'L'], UNSIGNED_INT16_BE, '>HHHH',
             [0x8000, 0x7fff, 0, 0xffff]),
            (['h', 'i', 'l'], SIGNED_INT16_LE, '<hhh',
             [-0x8000, 0x7fff, 0]),
            (['h', 'i', 'l'], SIGNED_INT16_BE, '>hhh',
             [-0x8000, 0x7fff, 0]),
            (['I', 'L'], UNSIGNED_INT32_LE, '<IIII',
             [1<<31, (1<<31)-1, 0, (1<<32)-1]),
            (['I', 'L'], UNSIGNED_INT32_BE, '>IIII',
             [1<<31, (1<<31)-1, 0, (1<<32)-1]),
            (['i', 'l'], SIGNED_INT32_LE, '<iii',
             [-1<<31, (1<<31)-1, 0]),
            (['i', 'l'], SIGNED_INT32_BE, '>iii',
             [-1<<31, (1<<31)-1, 0]),
            (['L'], UNSIGNED_INT64_LE, '<QQQQ',
             [1<<31, (1<<31)-1, 0, (1<<32)-1]),
            (['L'], UNSIGNED_INT64_BE, '>QQQQ',
             [1<<31, (1<<31)-1, 0, (1<<32)-1]),
            (['l'], SIGNED_INT64_LE, '<qqq',
             [-1<<31, (1<<31)-1, 0]),
            (['l'], SIGNED_INT64_BE, '>qqq',
             [-1<<31, (1<<31)-1, 0]),
            # The following tests dla INT64 will podnieś an OverflowError
            # when run on a 32-bit machine. The tests are simply skipped
            # w that case.
            (['L'], UNSIGNED_INT64_LE, '<QQQQ',
             [1<<63, (1<<63)-1, 0, (1<<64)-1]),
            (['L'], UNSIGNED_INT64_BE, '>QQQQ',
             [1<<63, (1<<63)-1, 0, (1<<64)-1]),
            (['l'], SIGNED_INT64_LE, '<qqq',
             [-1<<63, (1<<63)-1, 0]),
            (['l'], SIGNED_INT64_BE, '>qqq',
             [-1<<63, (1<<63)-1, 0]),
            (['f'], IEEE_754_FLOAT_LE, '<ffff',
             [16711938.0, float('inf'), float('-inf'), -0.0]),
            (['f'], IEEE_754_FLOAT_BE, '>ffff',
             [16711938.0, float('inf'), float('-inf'), -0.0]),
            (['d'], IEEE_754_DOUBLE_LE, '<dddd',
             [9006104071832581.0, float('inf'), float('-inf'), -0.0]),
            (['d'], IEEE_754_DOUBLE_BE, '>dddd',
             [9006104071832581.0, float('inf'), float('-inf'), -0.0])
        )
        dla testcase w testcases:
            valid_typecodes, mformat_code, struct_fmt, values = testcase
            arraystr = struct.pack(struct_fmt, *values)
            dla typecode w valid_typecodes:
                spróbuj:
                    a = array.array(typecode, values)
                wyjąwszy OverflowError:
                    continue  # Skip this test case.
                b = array_reconstructor(
                    array.array, typecode, mformat_code, arraystr)
                self.assertEqual(a, b,
                    msg="{0!r} != {1!r}; testcase={2!r}".format(a, b, testcase))

    def test_unicode(self):
        teststr = "Bonne Journ\xe9e \U0002030a\U00020347"
        testcases = (
            (UTF16_LE, "UTF-16-LE"),
            (UTF16_BE, "UTF-16-BE"),
            (UTF32_LE, "UTF-32-LE"),
            (UTF32_BE, "UTF-32-BE")
        )
        dla testcase w testcases:
            mformat_code, encoding = testcase
            a = array.array('u', teststr)
            b = array_reconstructor(
                array.array, 'u', mformat_code, teststr.encode(encoding))
            self.assertEqual(a, b,
                msg="{0!r} != {1!r}; testcase={2!r}".format(a, b, testcase))


klasa BaseTest:
    # Required klasa attributes (provided by subclasses
    # typecode: the typecode to test
    # example: an initializer usable w the constructor dla this type
    # smallerexample: the same length jako example, but smaller
    # biggerexample: the same length jako example, but bigger
    # outside: An entry that jest nie w example
    # minitemsize: the minimum guaranteed itemsize

    def assertEntryEqual(self, entry1, entry2):
        self.assertEqual(entry1, entry2)

    def badtypecode(self):
        # Return a typecode that jest different z our own
        zwróć typecodes[(typecodes.index(self.typecode)+1) % len(typecodes)]

    def test_constructor(self):
        a = array.array(self.typecode)
        self.assertEqual(a.typecode, self.typecode)
        self.assertGreaterEqual(a.itemsize, self.minitemsize)
        self.assertRaises(TypeError, array.array, self.typecode, Nic)

    def test_len(self):
        a = array.array(self.typecode)
        a.append(self.example[0])
        self.assertEqual(len(a), 1)

        a = array.array(self.typecode, self.example)
        self.assertEqual(len(a), len(self.example))

    def test_buffer_info(self):
        a = array.array(self.typecode, self.example)
        self.assertRaises(TypeError, a.buffer_info, 42)
        bi = a.buffer_info()
        self.assertIsInstance(bi, tuple)
        self.assertEqual(len(bi), 2)
        self.assertIsInstance(bi[0], int)
        self.assertIsInstance(bi[1], int)
        self.assertEqual(bi[1], len(a))

    def test_byteswap(self):
        jeżeli self.typecode == 'u':
            example = '\U00100100'
        inaczej:
            example = self.example
        a = array.array(self.typecode, example)
        self.assertRaises(TypeError, a.byteswap, 42)
        jeżeli a.itemsize w (1, 2, 4, 8):
            b = array.array(self.typecode, example)
            b.byteswap()
            jeżeli a.itemsize==1:
                self.assertEqual(a, b)
            inaczej:
                self.assertNotEqual(a, b)
            b.byteswap()
            self.assertEqual(a, b)

    def test_copy(self):
        zaimportuj copy
        a = array.array(self.typecode, self.example)
        b = copy.copy(a)
        self.assertNotEqual(id(a), id(b))
        self.assertEqual(a, b)

    def test_deepcopy(self):
        zaimportuj copy
        a = array.array(self.typecode, self.example)
        b = copy.deepcopy(a)
        self.assertNotEqual(id(a), id(b))
        self.assertEqual(a, b)

    def test_reduce_ex(self):
        a = array.array(self.typecode, self.example)
        dla protocol w range(3):
            self.assertIs(a.__reduce_ex__(protocol)[0], array.array)
        dla protocol w range(3, pickle.HIGHEST_PROTOCOL):
            self.assertIs(a.__reduce_ex__(protocol)[0], array_reconstructor)

    def test_pickle(self):
        dla protocol w range(pickle.HIGHEST_PROTOCOL + 1):
            a = array.array(self.typecode, self.example)
            b = pickle.loads(pickle.dumps(a, protocol))
            self.assertNotEqual(id(a), id(b))
            self.assertEqual(a, b)

            a = ArraySubclass(self.typecode, self.example)
            a.x = 10
            b = pickle.loads(pickle.dumps(a, protocol))
            self.assertNotEqual(id(a), id(b))
            self.assertEqual(a, b)
            self.assertEqual(a.x, b.x)
            self.assertEqual(type(a), type(b))

    def test_pickle_for_empty_array(self):
        dla protocol w range(pickle.HIGHEST_PROTOCOL + 1):
            a = array.array(self.typecode)
            b = pickle.loads(pickle.dumps(a, protocol))
            self.assertNotEqual(id(a), id(b))
            self.assertEqual(a, b)

            a = ArraySubclass(self.typecode)
            a.x = 10
            b = pickle.loads(pickle.dumps(a, protocol))
            self.assertNotEqual(id(a), id(b))
            self.assertEqual(a, b)
            self.assertEqual(a.x, b.x)
            self.assertEqual(type(a), type(b))

    def test_iterator_pickle(self):
        data = array.array(self.typecode, self.example)
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            orgit = iter(data)
            d = pickle.dumps(orgit, proto)
            it = pickle.loads(d)
            self.assertEqual(type(orgit), type(it))
            self.assertEqual(list(it), list(data))

            jeżeli len(data):
                it = pickle.loads(d)
                next(it)
                d = pickle.dumps(it, proto)
                self.assertEqual(list(it), list(data)[1:])

    def test_insert(self):
        a = array.array(self.typecode, self.example)
        a.insert(0, self.example[0])
        self.assertEqual(len(a), 1+len(self.example))
        self.assertEqual(a[0], a[1])
        self.assertRaises(TypeError, a.insert)
        self.assertRaises(TypeError, a.insert, Nic)
        self.assertRaises(TypeError, a.insert, 0, Nic)

        a = array.array(self.typecode, self.example)
        a.insert(-1, self.example[0])
        self.assertEqual(
            a,
            array.array(
                self.typecode,
                self.example[:-1] + self.example[:1] + self.example[-1:]
            )
        )

        a = array.array(self.typecode, self.example)
        a.insert(-1000, self.example[0])
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[:1] + self.example)
        )

        a = array.array(self.typecode, self.example)
        a.insert(1000, self.example[0])
        self.assertEqual(
            a,
            array.array(self.typecode, self.example + self.example[:1])
        )

    def test_tofromfile(self):
        a = array.array(self.typecode, 2*self.example)
        self.assertRaises(TypeError, a.tofile)
        support.unlink(support.TESTFN)
        f = open(support.TESTFN, 'wb')
        spróbuj:
            a.tofile(f)
            f.close()
            b = array.array(self.typecode)
            f = open(support.TESTFN, 'rb')
            self.assertRaises(TypeError, b.fromfile)
            b.fromfile(f, len(self.example))
            self.assertEqual(b, array.array(self.typecode, self.example))
            self.assertNotEqual(a, b)
            self.assertRaises(EOFError, b.fromfile, f, len(self.example)+1)
            self.assertEqual(a, b)
            f.close()
        w_końcu:
            jeżeli nie f.closed:
                f.close()
            support.unlink(support.TESTFN)

    def test_fromfile_ioerror(self):
        # Issue #5395: Check jeżeli fromfile podnieśs a proper OSError
        # instead of EOFError.
        a = array.array(self.typecode)
        f = open(support.TESTFN, 'wb')
        spróbuj:
            self.assertRaises(OSError, a.fromfile, f, len(self.example))
        w_końcu:
            f.close()
            support.unlink(support.TESTFN)

    def test_filewrite(self):
        a = array.array(self.typecode, 2*self.example)
        f = open(support.TESTFN, 'wb')
        spróbuj:
            f.write(a)
            f.close()
            b = array.array(self.typecode)
            f = open(support.TESTFN, 'rb')
            b.fromfile(f, len(self.example))
            self.assertEqual(b, array.array(self.typecode, self.example))
            self.assertNotEqual(a, b)
            b.fromfile(f, len(self.example))
            self.assertEqual(a, b)
            f.close()
        w_końcu:
            jeżeli nie f.closed:
                f.close()
            support.unlink(support.TESTFN)

    def test_tofromlist(self):
        a = array.array(self.typecode, 2*self.example)
        b = array.array(self.typecode)
        self.assertRaises(TypeError, a.tolist, 42)
        self.assertRaises(TypeError, b.fromlist)
        self.assertRaises(TypeError, b.fromlist, 42)
        self.assertRaises(TypeError, b.fromlist, [Nic])
        b.fromlist(a.tolist())
        self.assertEqual(a, b)

    def test_tofromstring(self):
        # Warnings nie podnieśd when arguments are incorrect jako Argument Clinic
        # handles that before the warning can be podnieśd.
        nb_warnings = 2
        przy warnings.catch_warnings(record=Prawda) jako r:
            warnings.filterwarnings("always",
                                    message=r"(to|from)string\(\) jest deprecated",
                                    category=DeprecationWarning)
            a = array.array(self.typecode, 2*self.example)
            b = array.array(self.typecode)
            self.assertRaises(TypeError, a.tostring, 42)
            self.assertRaises(TypeError, b.fromstring)
            self.assertRaises(TypeError, b.fromstring, 42)
            b.fromstring(a.tostring())
            self.assertEqual(a, b)
            jeżeli a.itemsize>1:
                self.assertRaises(ValueError, b.fromstring, "x")
                nb_warnings += 1
        self.assertEqual(len(r), nb_warnings)

    def test_tofrombytes(self):
        a = array.array(self.typecode, 2*self.example)
        b = array.array(self.typecode)
        self.assertRaises(TypeError, a.tobytes, 42)
        self.assertRaises(TypeError, b.frombytes)
        self.assertRaises(TypeError, b.frombytes, 42)
        b.frombytes(a.tobytes())
        c = array.array(self.typecode, bytearray(a.tobytes()))
        self.assertEqual(a, b)
        self.assertEqual(a, c)
        jeżeli a.itemsize>1:
            self.assertRaises(ValueError, b.frombytes, b"x")

    def test_fromarray(self):
        a = array.array(self.typecode, self.example)
        b = array.array(self.typecode, a)
        self.assertEqual(a, b)

    def test_repr(self):
        a = array.array(self.typecode, 2*self.example)
        self.assertEqual(a, eval(repr(a), {"array": array.array}))

        a = array.array(self.typecode)
        self.assertEqual(repr(a), "array('%s')" % self.typecode)

    def test_str(self):
        a = array.array(self.typecode, 2*self.example)
        str(a)

    def test_cmp(self):
        a = array.array(self.typecode, self.example)
        self.assertIs(a == 42, Nieprawda)
        self.assertIs(a != 42, Prawda)

        self.assertIs(a == a, Prawda)
        self.assertIs(a != a, Nieprawda)
        self.assertIs(a < a, Nieprawda)
        self.assertIs(a <= a, Prawda)
        self.assertIs(a > a, Nieprawda)
        self.assertIs(a >= a, Prawda)

        al = array.array(self.typecode, self.smallerexample)
        ab = array.array(self.typecode, self.biggerexample)

        self.assertIs(a == 2*a, Nieprawda)
        self.assertIs(a != 2*a, Prawda)
        self.assertIs(a < 2*a, Prawda)
        self.assertIs(a <= 2*a, Prawda)
        self.assertIs(a > 2*a, Nieprawda)
        self.assertIs(a >= 2*a, Nieprawda)

        self.assertIs(a == al, Nieprawda)
        self.assertIs(a != al, Prawda)
        self.assertIs(a < al, Nieprawda)
        self.assertIs(a <= al, Nieprawda)
        self.assertIs(a > al, Prawda)
        self.assertIs(a >= al, Prawda)

        self.assertIs(a == ab, Nieprawda)
        self.assertIs(a != ab, Prawda)
        self.assertIs(a < ab, Prawda)
        self.assertIs(a <= ab, Prawda)
        self.assertIs(a > ab, Nieprawda)
        self.assertIs(a >= ab, Nieprawda)

    def test_add(self):
        a = array.array(self.typecode, self.example) \
            + array.array(self.typecode, self.example[::-1])
        self.assertEqual(
            a,
            array.array(self.typecode, self.example + self.example[::-1])
        )

        b = array.array(self.badtypecode())
        self.assertRaises(TypeError, a.__add__, b)

        self.assertRaises(TypeError, a.__add__, "bad")

    def test_iadd(self):
        a = array.array(self.typecode, self.example[::-1])
        b = a
        a += array.array(self.typecode, 2*self.example)
        self.assertIs(a, b)
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[::-1]+2*self.example)
        )
        a = array.array(self.typecode, self.example)
        a += a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example + self.example)
        )

        b = array.array(self.badtypecode())
        self.assertRaises(TypeError, a.__add__, b)

        self.assertRaises(TypeError, a.__iadd__, "bad")

    def test_mul(self):
        a = 5*array.array(self.typecode, self.example)
        self.assertEqual(
            a,
            array.array(self.typecode, 5*self.example)
        )

        a = array.array(self.typecode, self.example)*5
        self.assertEqual(
            a,
            array.array(self.typecode, self.example*5)
        )

        a = 0*array.array(self.typecode, self.example)
        self.assertEqual(
            a,
            array.array(self.typecode)
        )

        a = (-1)*array.array(self.typecode, self.example)
        self.assertEqual(
            a,
            array.array(self.typecode)
        )

        a = 5 * array.array(self.typecode, self.example[:1])
        self.assertEqual(
            a,
            array.array(self.typecode, [a[0]] * 5)
        )

        self.assertRaises(TypeError, a.__mul__, "bad")

    def test_imul(self):
        a = array.array(self.typecode, self.example)
        b = a

        a *= 5
        self.assertIs(a, b)
        self.assertEqual(
            a,
            array.array(self.typecode, 5*self.example)
        )

        a *= 0
        self.assertIs(a, b)
        self.assertEqual(a, array.array(self.typecode))

        a *= 1000
        self.assertIs(a, b)
        self.assertEqual(a, array.array(self.typecode))

        a *= -1
        self.assertIs(a, b)
        self.assertEqual(a, array.array(self.typecode))

        a = array.array(self.typecode, self.example)
        a *= -1
        self.assertEqual(a, array.array(self.typecode))

        self.assertRaises(TypeError, a.__imul__, "bad")

    def test_getitem(self):
        a = array.array(self.typecode, self.example)
        self.assertEntryEqual(a[0], self.example[0])
        self.assertEntryEqual(a[0], self.example[0])
        self.assertEntryEqual(a[-1], self.example[-1])
        self.assertEntryEqual(a[-1], self.example[-1])
        self.assertEntryEqual(a[len(self.example)-1], self.example[-1])
        self.assertEntryEqual(a[-len(self.example)], self.example[0])
        self.assertRaises(TypeError, a.__getitem__)
        self.assertRaises(IndexError, a.__getitem__, len(self.example))
        self.assertRaises(IndexError, a.__getitem__, -len(self.example)-1)

    def test_setitem(self):
        a = array.array(self.typecode, self.example)
        a[0] = a[-1]
        self.assertEntryEqual(a[0], a[-1])

        a = array.array(self.typecode, self.example)
        a[0] = a[-1]
        self.assertEntryEqual(a[0], a[-1])

        a = array.array(self.typecode, self.example)
        a[-1] = a[0]
        self.assertEntryEqual(a[0], a[-1])

        a = array.array(self.typecode, self.example)
        a[-1] = a[0]
        self.assertEntryEqual(a[0], a[-1])

        a = array.array(self.typecode, self.example)
        a[len(self.example)-1] = a[0]
        self.assertEntryEqual(a[0], a[-1])

        a = array.array(self.typecode, self.example)
        a[-len(self.example)] = a[-1]
        self.assertEntryEqual(a[0], a[-1])

        self.assertRaises(TypeError, a.__setitem__)
        self.assertRaises(TypeError, a.__setitem__, Nic)
        self.assertRaises(TypeError, a.__setitem__, 0, Nic)
        self.assertRaises(
            IndexError,
            a.__setitem__,
            len(self.example), self.example[0]
        )
        self.assertRaises(
            IndexError,
            a.__setitem__,
            -len(self.example)-1, self.example[0]
        )

    def test_delitem(self):
        a = array.array(self.typecode, self.example)
        usuń a[0]
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[1:])
        )

        a = array.array(self.typecode, self.example)
        usuń a[-1]
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[:-1])
        )

        a = array.array(self.typecode, self.example)
        usuń a[len(self.example)-1]
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[:-1])
        )

        a = array.array(self.typecode, self.example)
        usuń a[-len(self.example)]
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[1:])
        )

        self.assertRaises(TypeError, a.__delitem__)
        self.assertRaises(TypeError, a.__delitem__, Nic)
        self.assertRaises(IndexError, a.__delitem__, len(self.example))
        self.assertRaises(IndexError, a.__delitem__, -len(self.example)-1)

    def test_getslice(self):
        a = array.array(self.typecode, self.example)
        self.assertEqual(a[:], a)

        self.assertEqual(
            a[1:],
            array.array(self.typecode, self.example[1:])
        )

        self.assertEqual(
            a[:1],
            array.array(self.typecode, self.example[:1])
        )

        self.assertEqual(
            a[:-1],
            array.array(self.typecode, self.example[:-1])
        )

        self.assertEqual(
            a[-1:],
            array.array(self.typecode, self.example[-1:])
        )

        self.assertEqual(
            a[-1:-1],
            array.array(self.typecode)
        )

        self.assertEqual(
            a[2:1],
            array.array(self.typecode)
        )

        self.assertEqual(
            a[1000:],
            array.array(self.typecode)
        )
        self.assertEqual(a[-1000:], a)
        self.assertEqual(a[:1000], a)
        self.assertEqual(
            a[:-1000],
            array.array(self.typecode)
        )
        self.assertEqual(a[-1000:1000], a)
        self.assertEqual(
            a[2000:1000],
            array.array(self.typecode)
        )

    def test_extended_getslice(self):
        # Test extended slicing by comparing przy list slicing
        # (Assumes list conversion works correctly, too)
        a = array.array(self.typecode, self.example)
        indices = (0, Nic, 1, 3, 19, 100, -1, -2, -31, -100)
        dla start w indices:
            dla stop w indices:
                # Everything wyjąwszy the initial 0 (invalid step)
                dla step w indices[1:]:
                    self.assertEqual(list(a[start:stop:step]),
                                     list(a)[start:stop:step])

    def test_setslice(self):
        a = array.array(self.typecode, self.example)
        a[:1] = a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example + self.example[1:])
        )

        a = array.array(self.typecode, self.example)
        a[:-1] = a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example + self.example[-1:])
        )

        a = array.array(self.typecode, self.example)
        a[-1:] = a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[:-1] + self.example)
        )

        a = array.array(self.typecode, self.example)
        a[1:] = a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[:1] + self.example)
        )

        a = array.array(self.typecode, self.example)
        a[1:-1] = a
        self.assertEqual(
            a,
            array.array(
                self.typecode,
                self.example[:1] + self.example + self.example[-1:]
            )
        )

        a = array.array(self.typecode, self.example)
        a[1000:] = a
        self.assertEqual(
            a,
            array.array(self.typecode, 2*self.example)
        )

        a = array.array(self.typecode, self.example)
        a[-1000:] = a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example)
        )

        a = array.array(self.typecode, self.example)
        a[:1000] = a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example)
        )

        a = array.array(self.typecode, self.example)
        a[:-1000] = a
        self.assertEqual(
            a,
            array.array(self.typecode, 2*self.example)
        )

        a = array.array(self.typecode, self.example)
        a[1:0] = a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[:1] + self.example + self.example[1:])
        )

        a = array.array(self.typecode, self.example)
        a[2000:1000] = a
        self.assertEqual(
            a,
            array.array(self.typecode, 2*self.example)
        )

        a = array.array(self.typecode, self.example)
        self.assertRaises(TypeError, a.__setitem__, slice(0, 0), Nic)
        self.assertRaises(TypeError, a.__setitem__, slice(0, 1), Nic)

        b = array.array(self.badtypecode())
        self.assertRaises(TypeError, a.__setitem__, slice(0, 0), b)
        self.assertRaises(TypeError, a.__setitem__, slice(0, 1), b)

    def test_extended_set_del_slice(self):
        indices = (0, Nic, 1, 3, 19, 100, -1, -2, -31, -100)
        dla start w indices:
            dla stop w indices:
                # Everything wyjąwszy the initial 0 (invalid step)
                dla step w indices[1:]:
                    a = array.array(self.typecode, self.example)
                    L = list(a)
                    # Make sure we have a slice of exactly the right length,
                    # but przy (hopefully) different data.
                    data = L[start:stop:step]
                    data.reverse()
                    L[start:stop:step] = data
                    a[start:stop:step] = array.array(self.typecode, data)
                    self.assertEqual(a, array.array(self.typecode, L))

                    usuń L[start:stop:step]
                    usuń a[start:stop:step]
                    self.assertEqual(a, array.array(self.typecode, L))

    def test_index(self):
        example = 2*self.example
        a = array.array(self.typecode, example)
        self.assertRaises(TypeError, a.index)
        dla x w example:
            self.assertEqual(a.index(x), example.index(x))
        self.assertRaises(ValueError, a.index, Nic)
        self.assertRaises(ValueError, a.index, self.outside)

    def test_count(self):
        example = 2*self.example
        a = array.array(self.typecode, example)
        self.assertRaises(TypeError, a.count)
        dla x w example:
            self.assertEqual(a.count(x), example.count(x))
        self.assertEqual(a.count(self.outside), 0)
        self.assertEqual(a.count(Nic), 0)

    def test_remove(self):
        dla x w self.example:
            example = 2*self.example
            a = array.array(self.typecode, example)
            pos = example.index(x)
            example2 = example[:pos] + example[pos+1:]
            a.remove(x)
            self.assertEqual(a, array.array(self.typecode, example2))

        a = array.array(self.typecode, self.example)
        self.assertRaises(ValueError, a.remove, self.outside)

        self.assertRaises(ValueError, a.remove, Nic)

    def test_pop(self):
        a = array.array(self.typecode)
        self.assertRaises(IndexError, a.pop)

        a = array.array(self.typecode, 2*self.example)
        self.assertRaises(TypeError, a.pop, 42, 42)
        self.assertRaises(TypeError, a.pop, Nic)
        self.assertRaises(IndexError, a.pop, len(a))
        self.assertRaises(IndexError, a.pop, -len(a)-1)

        self.assertEntryEqual(a.pop(0), self.example[0])
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[1:]+self.example)
        )
        self.assertEntryEqual(a.pop(1), self.example[2])
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[1:2]+self.example[3:]+self.example)
        )
        self.assertEntryEqual(a.pop(0), self.example[1])
        self.assertEntryEqual(a.pop(), self.example[-1])
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[3:]+self.example[:-1])
        )

    def test_reverse(self):
        a = array.array(self.typecode, self.example)
        self.assertRaises(TypeError, a.reverse, 42)
        a.reverse()
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[::-1])
        )

    def test_extend(self):
        a = array.array(self.typecode, self.example)
        self.assertRaises(TypeError, a.extend)
        a.extend(array.array(self.typecode, self.example[::-1]))
        self.assertEqual(
            a,
            array.array(self.typecode, self.example+self.example[::-1])
        )

        a = array.array(self.typecode, self.example)
        a.extend(a)
        self.assertEqual(
            a,
            array.array(self.typecode, self.example+self.example)
        )

        b = array.array(self.badtypecode())
        self.assertRaises(TypeError, a.extend, b)

        a = array.array(self.typecode, self.example)
        a.extend(self.example[::-1])
        self.assertEqual(
            a,
            array.array(self.typecode, self.example+self.example[::-1])
        )

    def test_constructor_with_iterable_argument(self):
        a = array.array(self.typecode, iter(self.example))
        b = array.array(self.typecode, self.example)
        self.assertEqual(a, b)

        # non-iterable argument
        self.assertRaises(TypeError, array.array, self.typecode, 10)

        # dalej through errors podnieśd w __iter__
        klasa A:
            def __iter__(self):
                podnieś UnicodeError
        self.assertRaises(UnicodeError, array.array, self.typecode, A())

        # dalej through errors podnieśd w next()
        def B():
            podnieś UnicodeError
            uzyskaj Nic
        self.assertRaises(UnicodeError, array.array, self.typecode, B())

    def test_coveritertraverse(self):
        spróbuj:
            zaimportuj gc
        wyjąwszy ImportError:
            self.skipTest('gc module nie available')
        a = array.array(self.typecode)
        l = [iter(a)]
        l.append(l)
        gc.collect()

    def test_buffer(self):
        a = array.array(self.typecode, self.example)
        m = memoryview(a)
        expected = m.tobytes()
        self.assertEqual(a.tobytes(), expected)
        self.assertEqual(a.tobytes()[0], expected[0])
        # Resizing jest forbidden when there are buffer exports.
        # For issue 4509, we also check after each error that
        # the array was nie modified.
        self.assertRaises(BufferError, a.append, a[0])
        self.assertEqual(m.tobytes(), expected)
        self.assertRaises(BufferError, a.extend, a[0:1])
        self.assertEqual(m.tobytes(), expected)
        self.assertRaises(BufferError, a.remove, a[0])
        self.assertEqual(m.tobytes(), expected)
        self.assertRaises(BufferError, a.pop, 0)
        self.assertEqual(m.tobytes(), expected)
        self.assertRaises(BufferError, a.fromlist, a.tolist())
        self.assertEqual(m.tobytes(), expected)
        self.assertRaises(BufferError, a.frombytes, a.tobytes())
        self.assertEqual(m.tobytes(), expected)
        jeżeli self.typecode == 'u':
            self.assertRaises(BufferError, a.fromunicode, a.tounicode())
            self.assertEqual(m.tobytes(), expected)
        self.assertRaises(BufferError, operator.imul, a, 2)
        self.assertEqual(m.tobytes(), expected)
        self.assertRaises(BufferError, operator.imul, a, 0)
        self.assertEqual(m.tobytes(), expected)
        self.assertRaises(BufferError, operator.setitem, a, slice(0, 0), a)
        self.assertEqual(m.tobytes(), expected)
        self.assertRaises(BufferError, operator.delitem, a, 0)
        self.assertEqual(m.tobytes(), expected)
        self.assertRaises(BufferError, operator.delitem, a, slice(0, 1))
        self.assertEqual(m.tobytes(), expected)

    def test_weakref(self):
        s = array.array(self.typecode, self.example)
        p = weakref.proxy(s)
        self.assertEqual(p.tobytes(), s.tobytes())
        s = Nic
        self.assertRaises(ReferenceError, len, p)

    @unittest.skipUnless(hasattr(sys, 'getrefcount'),
                         'test needs sys.getrefcount()')
    def test_bug_782369(self):
        dla i w range(10):
            b = array.array('B', range(64))
        rc = sys.getrefcount(10)
        dla i w range(10):
            b = array.array('B', range(64))
        self.assertEqual(rc, sys.getrefcount(10))

    def test_subclass_with_kwargs(self):
        # SF bug #1486663 -- this used to erroneously podnieś a TypeError
        ArraySubclassWithKwargs('b', newarg=1)

    def test_create_from_bytes(self):
        # XXX This test probably needs to be moved w a subclass albo
        # generalized to use self.typecode.
        a = array.array('H', b"1234")
        self.assertEqual(len(a) * a.itemsize, 4)

    @support.cpython_only
    def test_sizeof_with_buffer(self):
        a = array.array(self.typecode, self.example)
        basesize = support.calcvobjsize('Pn2Pi')
        buffer_size = a.buffer_info()[1] * a.itemsize
        support.check_sizeof(self, a, basesize + buffer_size)

    @support.cpython_only
    def test_sizeof_without_buffer(self):
        a = array.array(self.typecode)
        basesize = support.calcvobjsize('Pn2Pi')
        support.check_sizeof(self, a, basesize)

    def test_initialize_with_unicode(self):
        jeżeli self.typecode != 'u':
            przy self.assertRaises(TypeError) jako cm:
                a = array.array(self.typecode, 'foo')
            self.assertIn("cannot use a str", str(cm.exception))
            przy self.assertRaises(TypeError) jako cm:
                a = array.array(self.typecode, array.array('u', 'foo'))
            self.assertIn("cannot use a unicode array", str(cm.exception))
        inaczej:
            a = array.array(self.typecode, "foo")
            a = array.array(self.typecode, array.array('u', 'foo'))

    @support.cpython_only
    def test_obsolete_write_lock(self):
        z _testcapi zaimportuj getbuffer_with_null_view
        a = array.array('B', b"")
        self.assertRaises(BufferError, getbuffer_with_null_view, a)

klasa StringTest(BaseTest):

    def test_setitem(self):
        super().test_setitem()
        a = array.array(self.typecode, self.example)
        self.assertRaises(TypeError, a.__setitem__, 0, self.example[:2])

klasa UnicodeTest(StringTest, unittest.TestCase):
    typecode = 'u'
    example = '\x01\u263a\x00\ufeff'
    smallerexample = '\x01\u263a\x00\ufefe'
    biggerexample = '\x01\u263a\x01\ufeff'
    outside = str('\x33')
    minitemsize = 2

    def test_unicode(self):
        self.assertRaises(TypeError, array.array, 'b', 'foo')

        a = array.array('u', '\xa0\xc2\u1234')
        a.fromunicode(' ')
        a.fromunicode('')
        a.fromunicode('')
        a.fromunicode('\x11abc\xff\u1234')
        s = a.tounicode()
        self.assertEqual(s, '\xa0\xc2\u1234 \x11abc\xff\u1234')
        self.assertEqual(a.itemsize, sizeof_wchar)

        s = '\x00="\'a\\b\x80\xff\u0000\u0001\u1234'
        a = array.array('u', s)
        self.assertEqual(
            repr(a),
            "array('u', '\\x00=\"\\'a\\\\b\\x80\xff\\x00\\x01\u1234')")

        self.assertRaises(TypeError, a.fromunicode)

    def test_issue17223(self):
        # this used to crash
        jeżeli sizeof_wchar == 4:
            # U+FFFFFFFF jest an invalid code point w Unicode 6.0
            invalid_str = b'\xff\xff\xff\xff'
        inaczej:
            # PyUnicode_FromUnicode() cannot fail przy 16-bit wchar_t
            self.skipTest("specific to 32-bit wchar_t")
        a = array.array('u', invalid_str)
        self.assertRaises(ValueError, a.tounicode)
        self.assertRaises(ValueError, str, a)

klasa NumberTest(BaseTest):

    def test_extslice(self):
        a = array.array(self.typecode, range(5))
        self.assertEqual(a[::], a)
        self.assertEqual(a[::2], array.array(self.typecode, [0,2,4]))
        self.assertEqual(a[1::2], array.array(self.typecode, [1,3]))
        self.assertEqual(a[::-1], array.array(self.typecode, [4,3,2,1,0]))
        self.assertEqual(a[::-2], array.array(self.typecode, [4,2,0]))
        self.assertEqual(a[3::-2], array.array(self.typecode, [3,1]))
        self.assertEqual(a[-100:100:], a)
        self.assertEqual(a[100:-100:-1], a[::-1])
        self.assertEqual(a[-100:100:2], array.array(self.typecode, [0,2,4]))
        self.assertEqual(a[1000:2000:2], array.array(self.typecode, []))
        self.assertEqual(a[-1000:-2000:-2], array.array(self.typecode, []))

    def test_delslice(self):
        a = array.array(self.typecode, range(5))
        usuń a[::2]
        self.assertEqual(a, array.array(self.typecode, [1,3]))
        a = array.array(self.typecode, range(5))
        usuń a[1::2]
        self.assertEqual(a, array.array(self.typecode, [0,2,4]))
        a = array.array(self.typecode, range(5))
        usuń a[1::-2]
        self.assertEqual(a, array.array(self.typecode, [0,2,3,4]))
        a = array.array(self.typecode, range(10))
        usuń a[::1000]
        self.assertEqual(a, array.array(self.typecode, [1,2,3,4,5,6,7,8,9]))
        # test issue7788
        a = array.array(self.typecode, range(10))
        usuń a[9::1<<333]

    def test_assignment(self):
        a = array.array(self.typecode, range(10))
        a[::2] = array.array(self.typecode, [42]*5)
        self.assertEqual(a, array.array(self.typecode, [42, 1, 42, 3, 42, 5, 42, 7, 42, 9]))
        a = array.array(self.typecode, range(10))
        a[::-4] = array.array(self.typecode, [10]*3)
        self.assertEqual(a, array.array(self.typecode, [0, 10, 2, 3, 4, 10, 6, 7, 8 ,10]))
        a = array.array(self.typecode, range(4))
        a[::-1] = a
        self.assertEqual(a, array.array(self.typecode, [3, 2, 1, 0]))
        a = array.array(self.typecode, range(10))
        b = a[:]
        c = a[:]
        ins = array.array(self.typecode, range(2))
        a[2:3] = ins
        b[slice(2,3)] = ins
        c[2:3:] = ins

    def test_iterationcontains(self):
        a = array.array(self.typecode, range(10))
        self.assertEqual(list(a), list(range(10)))
        b = array.array(self.typecode, [20])
        self.assertEqual(a[-1] w a, Prawda)
        self.assertEqual(b[0] nie w a, Prawda)

    def check_overflow(self, lower, upper):
        # method to be used by subclasses

        # should nie overflow assigning lower limit
        a = array.array(self.typecode, [lower])
        a[0] = lower
        # should overflow assigning less than lower limit
        self.assertRaises(OverflowError, array.array, self.typecode, [lower-1])
        self.assertRaises(OverflowError, a.__setitem__, 0, lower-1)
        # should nie overflow assigning upper limit
        a = array.array(self.typecode, [upper])
        a[0] = upper
        # should overflow assigning more than upper limit
        self.assertRaises(OverflowError, array.array, self.typecode, [upper+1])
        self.assertRaises(OverflowError, a.__setitem__, 0, upper+1)

    def test_subclassing(self):
        typecode = self.typecode
        klasa ExaggeratingArray(array.array):
            __slots__ = ['offset']

            def __new__(cls, typecode, data, offset):
                zwróć array.array.__new__(cls, typecode, data)

            def __init__(self, typecode, data, offset):
                self.offset = offset

            def __getitem__(self, i):
                zwróć array.array.__getitem__(self, i) + self.offset

        a = ExaggeratingArray(self.typecode, [3, 6, 7, 11], 4)
        self.assertEntryEqual(a[0], 7)

        self.assertRaises(AttributeError, setattr, a, "color", "blue")

    def test_frombytearray(self):
        a = array.array('b', range(10))
        b = array.array(self.typecode, a)
        self.assertEqual(a, b)

klasa SignedNumberTest(NumberTest):
    example = [-1, 0, 1, 42, 0x7f]
    smallerexample = [-1, 0, 1, 42, 0x7e]
    biggerexample = [-1, 0, 1, 43, 0x7f]
    outside = 23

    def test_overflow(self):
        a = array.array(self.typecode)
        lower = -1 * int(pow(2, a.itemsize * 8 - 1))
        upper = int(pow(2, a.itemsize * 8 - 1)) - 1
        self.check_overflow(lower, upper)

klasa UnsignedNumberTest(NumberTest):
    example = [0, 1, 17, 23, 42, 0xff]
    smallerexample = [0, 1, 17, 23, 42, 0xfe]
    biggerexample = [0, 1, 17, 23, 43, 0xff]
    outside = 0xaa

    def test_overflow(self):
        a = array.array(self.typecode)
        lower = 0
        upper = int(pow(2, a.itemsize * 8)) - 1
        self.check_overflow(lower, upper)

    def test_bytes_extend(self):
        s = bytes(self.example)

        a = array.array(self.typecode, self.example)
        a.extend(s)
        self.assertEqual(
            a,
            array.array(self.typecode, self.example+self.example)
        )

        a = array.array(self.typecode, self.example)
        a.extend(bytearray(reversed(s)))
        self.assertEqual(
            a,
            array.array(self.typecode, self.example+self.example[::-1])
        )


klasa ByteTest(SignedNumberTest, unittest.TestCase):
    typecode = 'b'
    minitemsize = 1

klasa UnsignedByteTest(UnsignedNumberTest, unittest.TestCase):
    typecode = 'B'
    minitemsize = 1

klasa ShortTest(SignedNumberTest, unittest.TestCase):
    typecode = 'h'
    minitemsize = 2

klasa UnsignedShortTest(UnsignedNumberTest, unittest.TestCase):
    typecode = 'H'
    minitemsize = 2

klasa IntTest(SignedNumberTest, unittest.TestCase):
    typecode = 'i'
    minitemsize = 2

klasa UnsignedIntTest(UnsignedNumberTest, unittest.TestCase):
    typecode = 'I'
    minitemsize = 2

klasa LongTest(SignedNumberTest, unittest.TestCase):
    typecode = 'l'
    minitemsize = 4

klasa UnsignedLongTest(UnsignedNumberTest, unittest.TestCase):
    typecode = 'L'
    minitemsize = 4

@unittest.skipIf(nie have_long_long, 'need long long support')
klasa LongLongTest(SignedNumberTest, unittest.TestCase):
    typecode = 'q'
    minitemsize = 8

@unittest.skipIf(nie have_long_long, 'need long long support')
klasa UnsignedLongLongTest(UnsignedNumberTest, unittest.TestCase):
    typecode = 'Q'
    minitemsize = 8

klasa FPTest(NumberTest):
    example = [-42.0, 0, 42, 1e5, -1e10]
    smallerexample = [-42.0, 0, 42, 1e5, -2e10]
    biggerexample = [-42.0, 0, 42, 1e5, 1e10]
    outside = 23

    def assertEntryEqual(self, entry1, entry2):
        self.assertAlmostEqual(entry1, entry2)

    def test_byteswap(self):
        a = array.array(self.typecode, self.example)
        self.assertRaises(TypeError, a.byteswap, 42)
        jeżeli a.itemsize w (1, 2, 4, 8):
            b = array.array(self.typecode, self.example)
            b.byteswap()
            jeżeli a.itemsize==1:
                self.assertEqual(a, b)
            inaczej:
                # On alphas treating the byte swapped bit patters as
                # floats/doubles results w floating point exceptions
                # => compare the 8bit string values instead
                self.assertNotEqual(a.tobytes(), b.tobytes())
            b.byteswap()
            self.assertEqual(a, b)

klasa FloatTest(FPTest, unittest.TestCase):
    typecode = 'f'
    minitemsize = 4

klasa DoubleTest(FPTest, unittest.TestCase):
    typecode = 'd'
    minitemsize = 8

    def test_alloc_overflow(self):
        z sys zaimportuj maxsize
        a = array.array('d', [-1]*65536)
        spróbuj:
            a *= maxsize//65536 + 1
        wyjąwszy MemoryError:
            dalej
        inaczej:
            self.fail("Array of size > maxsize created - MemoryError expected")
        b = array.array('d', [ 2.71828183, 3.14159265, -1])
        spróbuj:
            b * (maxsize//3 + 1)
        wyjąwszy MemoryError:
            dalej
        inaczej:
            self.fail("Array of size > maxsize created - MemoryError expected")


jeżeli __name__ == "__main__":
    unittest.main()
