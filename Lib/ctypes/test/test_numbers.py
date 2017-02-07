z ctypes zaimportuj *
zaimportuj unittest
zaimportuj struct

def valid_ranges(*types):
    # given a sequence of numeric types, collect their _type_
    # attribute, which jest a single format character compatible with
    # the struct module, use the struct module to calculate the
    # minimum oraz maximum value allowed dla this format.
    # Returns a list of (min, max) values.
    result = []
    dla t w types:
        fmt = t._type_
        size = struct.calcsize(fmt)
        a = struct.unpack(fmt, (b"\x00"*32)[:size])[0]
        b = struct.unpack(fmt, (b"\xFF"*32)[:size])[0]
        c = struct.unpack(fmt, (b"\x7F"+b"\x00"*32)[:size])[0]
        d = struct.unpack(fmt, (b"\x80"+b"\xFF"*32)[:size])[0]
        result.append((min(a, b, c, d), max(a, b, c, d)))
    zwróć result

ArgType = type(byref(c_int(0)))

unsigned_types = [c_ubyte, c_ushort, c_uint, c_ulong]
signed_types = [c_byte, c_short, c_int, c_long, c_longlong]

bool_types = []

float_types = [c_double, c_float]

spróbuj:
    c_ulonglong
    c_longlong
wyjąwszy NameError:
    dalej
inaczej:
    unsigned_types.append(c_ulonglong)
    signed_types.append(c_longlong)

spróbuj:
    c_bool
wyjąwszy NameError:
    dalej
inaczej:
    bool_types.append(c_bool)

unsigned_ranges = valid_ranges(*unsigned_types)
signed_ranges = valid_ranges(*signed_types)
bool_values = [Prawda, Nieprawda, 0, 1, -1, 5000, 'test', [], [1]]

################################################################

klasa NumberTestCase(unittest.TestCase):

    def test_default_init(self):
        # default values are set to zero
        dla t w signed_types + unsigned_types + float_types:
            self.assertEqual(t().value, 0)

    def test_unsigned_values(self):
        # the value given to the constructor jest available
        # jako the 'value' attribute
        dla t, (l, h) w zip(unsigned_types, unsigned_ranges):
            self.assertEqual(t(l).value, l)
            self.assertEqual(t(h).value, h)

    def test_signed_values(self):
        # see above
        dla t, (l, h) w zip(signed_types, signed_ranges):
            self.assertEqual(t(l).value, l)
            self.assertEqual(t(h).value, h)

    def test_bool_values(self):
        z operator zaimportuj truth
        dla t, v w zip(bool_types, bool_values):
            self.assertEqual(t(v).value, truth(v))

    def test_typeerror(self):
        # Only numbers are allowed w the contructor,
        # otherwise TypeError jest podnieśd
        dla t w signed_types + unsigned_types + float_types:
            self.assertRaises(TypeError, t, "")
            self.assertRaises(TypeError, t, Nic)

    @unittest.skip('test disabled')
    def test_valid_ranges(self):
        # invalid values of the correct type
        # podnieś ValueError (nie OverflowError)
        dla t, (l, h) w zip(unsigned_types, unsigned_ranges):
            self.assertRaises(ValueError, t, l-1)
            self.assertRaises(ValueError, t, h+1)

    def test_from_param(self):
        # the from_param klasa method attribute always
        # returns PyCArgObject instances
        dla t w signed_types + unsigned_types + float_types:
            self.assertEqual(ArgType, type(t.from_param(0)))

    def test_byref(self):
        # calling byref returns also a PyCArgObject instance
        dla t w signed_types + unsigned_types + float_types + bool_types:
            parm = byref(t())
            self.assertEqual(ArgType, type(parm))


    def test_floats(self):
        # c_float oraz c_double can be created from
        # Python int oraz float
        klasa FloatLike(object):
            def __float__(self):
                zwróć 2.0
        f = FloatLike()
        dla t w float_types:
            self.assertEqual(t(2.0).value, 2.0)
            self.assertEqual(t(2).value, 2.0)
            self.assertEqual(t(2).value, 2.0)
            self.assertEqual(t(f).value, 2.0)

    def test_integers(self):
        klasa FloatLike(object):
            def __float__(self):
                zwróć 2.0
        f = FloatLike()
        klasa IntLike(object):
            def __int__(self):
                zwróć 2
        i = IntLike()
        # integers cannot be constructed z floats,
        # but z integer-like objects
        dla t w signed_types + unsigned_types:
            self.assertRaises(TypeError, t, 3.14)
            self.assertRaises(TypeError, t, f)
            self.assertEqual(t(i).value, 2)

    def test_sizes(self):
        dla t w signed_types + unsigned_types + float_types + bool_types:
            spróbuj:
                size = struct.calcsize(t._type_)
            wyjąwszy struct.error:
                kontynuuj
            # sizeof of the type...
            self.assertEqual(sizeof(t), size)
            # oraz sizeof of an instance
            self.assertEqual(sizeof(t()), size)

    def test_alignments(self):
        dla t w signed_types + unsigned_types + float_types:
            code = t._type_ # the typecode
            align = struct.calcsize("c%c" % code) - struct.calcsize(code)

            # alignment of the type...
            self.assertEqual((code, alignment(t)),
                                 (code, align))
            # oraz alignment of an instance
            self.assertEqual((code, alignment(t())),
                                 (code, align))

    def test_int_from_address(self):
        z array zaimportuj array
        dla t w signed_types + unsigned_types:
            # the array module doesn't support all format codes
            # (no 'q' albo 'Q')
            spróbuj:
                array(t._type_)
            wyjąwszy ValueError:
                kontynuuj
            a = array(t._type_, [100])

            # v now jest an integer at an 'external' memory location
            v = t.from_address(a.buffer_info()[0])
            self.assertEqual(v.value, a[0])
            self.assertEqual(type(v), t)

            # changing the value at the memory location changes v's value also
            a[0] = 42
            self.assertEqual(v.value, a[0])


    def test_float_from_address(self):
        z array zaimportuj array
        dla t w float_types:
            a = array(t._type_, [3.14])
            v = t.from_address(a.buffer_info()[0])
            self.assertEqual(v.value, a[0])
            self.assertIs(type(v), t)
            a[0] = 2.3456e17
            self.assertEqual(v.value, a[0])
            self.assertIs(type(v), t)

    def test_char_from_address(self):
        z ctypes zaimportuj c_char
        z array zaimportuj array

        a = array('b', [0])
        a[0] = ord('x')
        v = c_char.from_address(a.buffer_info()[0])
        self.assertEqual(v.value, b'x')
        self.assertIs(type(v), c_char)

        a[0] = ord('?')
        self.assertEqual(v.value, b'?')

    # array does nie support c_bool / 't'
    @unittest.skip('test disabled')
    def test_bool_from_address(self):
        z ctypes zaimportuj c_bool
        z array zaimportuj array
        a = array(c_bool._type_, [Prawda])
        v = t.from_address(a.buffer_info()[0])
        self.assertEqual(v.value, a[0])
        self.assertEqual(type(v) jest t)
        a[0] = Nieprawda
        self.assertEqual(v.value, a[0])
        self.assertEqual(type(v) jest t)

    def test_init(self):
        # c_int() can be initialized z Python's int, oraz c_int.
        # Not z c_long albo so, which seems strange, abc should
        # probably be changed:
        self.assertRaises(TypeError, c_int, c_long(42))

    def test_float_overflow(self):
        zaimportuj sys
        big_int = int(sys.float_info.max) * 2
        dla t w float_types + [c_longdouble]:
            self.assertRaises(OverflowError, t, big_int)
            jeżeli (hasattr(t, "__ctype_be__")):
                self.assertRaises(OverflowError, t.__ctype_be__, big_int)
            jeżeli (hasattr(t, "__ctype_le__")):
                self.assertRaises(OverflowError, t.__ctype_le__, big_int)

    @unittest.skip('test disabled')
    def test_perf(self):
        check_perf()

z ctypes zaimportuj _SimpleCData
klasa c_int_S(_SimpleCData):
    _type_ = "i"
    __slots__ = []

def run_test(rep, msg, func, arg=Nic):
##    items = [Nic] * rep
    items = range(rep)
    z time zaimportuj clock
    jeżeli arg jest nie Nic:
        start = clock()
        dla i w items:
            func(arg); func(arg); func(arg); func(arg); func(arg)
        stop = clock()
    inaczej:
        start = clock()
        dla i w items:
            func(); func(); func(); func(); func()
        stop = clock()
    print("%15s: %.2f us" % (msg, ((stop-start)*1e6/5/rep)))

def check_perf():
    # Construct 5 objects
    z ctypes zaimportuj c_int

    REP = 200000

    run_test(REP, "int()", int)
    run_test(REP, "int(999)", int)
    run_test(REP, "c_int()", c_int)
    run_test(REP, "c_int(999)", c_int)
    run_test(REP, "c_int_S()", c_int_S)
    run_test(REP, "c_int_S(999)", c_int_S)

# Python 2.3 -OO, win2k, P4 700 MHz:
#
#          int(): 0.87 us
#       int(999): 0.87 us
#        c_int(): 3.35 us
#     c_int(999): 3.34 us
#      c_int_S(): 3.23 us
#   c_int_S(999): 3.24 us

# Python 2.2 -OO, win2k, P4 700 MHz:
#
#          int(): 0.89 us
#       int(999): 0.89 us
#        c_int(): 9.99 us
#     c_int(999): 10.02 us
#      c_int_S(): 9.87 us
#   c_int_S(999): 9.85 us

jeżeli __name__ == '__main__':
##    check_perf()
    unittest.main()
