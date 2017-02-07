zaimportuj unittest
z test zaimportuj support
# Skip this test jeżeli the _testcapi module isn't available.
support.import_module('_testcapi')
z _testcapi zaimportuj getargs_keywords, getargs_keyword_only
spróbuj:
    z _testcapi zaimportuj getargs_L, getargs_K
wyjąwszy ImportError:
    getargs_L = Nic # PY_LONG_LONG nie available

# > How about the following counterproposal. This also changes some of
# > the other format codes to be a little more regular.
# >
# > Code C type Range check
# >
# > b unsigned char 0..UCHAR_MAX
# > h signed short SHRT_MIN..SHRT_MAX
# > B unsigned char none **
# > H unsigned short none **
# > k * unsigned long none
# > I * unsigned int 0..UINT_MAX
#
#
# > i int INT_MIN..INT_MAX
# > l long LONG_MIN..LONG_MAX
#
# > K * unsigned long long none
# > L long long LLONG_MIN..LLONG_MAX
#
# > Notes:
# >
# > * New format codes.
# >
# > ** Changed z previous "range-and-a-half" to "none"; the
# > range-and-a-half checking wasn't particularly useful.
#
# Plus a C API albo two, e.g. PyLong_AsUnsignedLongMask() ->
# unsigned long oraz PyLong_AsUnsignedLongLongMask() -> unsigned
# long long (jeżeli that exists).

LARGE = 0x7FFFFFFF
VERY_LARGE = 0xFF0000121212121212121242

z _testcapi zaimportuj UCHAR_MAX, USHRT_MAX, UINT_MAX, ULONG_MAX, INT_MAX, \
     INT_MIN, LONG_MIN, LONG_MAX, PY_SSIZE_T_MIN, PY_SSIZE_T_MAX, \
     SHRT_MIN, SHRT_MAX

# fake, they are nie defined w Python's header files
LLONG_MAX = 2**63-1
LLONG_MIN = -2**63
ULLONG_MAX = 2**64-1

klasa Int:
    def __int__(self):
        zwróć 99

klasa IntSubclass(int):
    def __int__(self):
        zwróć 99

klasa BadInt:
    def __int__(self):
        zwróć 1.0

klasa BadInt2:
    def __int__(self):
        zwróć Prawda

klasa BadInt3(int):
    def __int__(self):
        zwróć Prawda


klasa Unsigned_TestCase(unittest.TestCase):
    def test_b(self):
        z _testcapi zaimportuj getargs_b
        # b returns 'unsigned char', oraz does range checking (0 ... UCHAR_MAX)
        self.assertRaises(TypeError, getargs_b, 3.14)
        self.assertEqual(99, getargs_b(Int()))
        self.assertEqual(0, getargs_b(IntSubclass()))
        self.assertRaises(TypeError, getargs_b, BadInt())
        przy self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_b(BadInt2()))
        self.assertEqual(0, getargs_b(BadInt3()))

        self.assertRaises(OverflowError, getargs_b, -1)
        self.assertEqual(0, getargs_b(0))
        self.assertEqual(UCHAR_MAX, getargs_b(UCHAR_MAX))
        self.assertRaises(OverflowError, getargs_b, UCHAR_MAX + 1)

        self.assertEqual(42, getargs_b(42))
        self.assertRaises(OverflowError, getargs_b, VERY_LARGE)

    def test_B(self):
        z _testcapi zaimportuj getargs_B
        # B returns 'unsigned char', no range checking
        self.assertRaises(TypeError, getargs_B, 3.14)
        self.assertEqual(99, getargs_B(Int()))
        self.assertEqual(0, getargs_B(IntSubclass()))
        self.assertRaises(TypeError, getargs_B, BadInt())
        przy self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_B(BadInt2()))
        self.assertEqual(0, getargs_B(BadInt3()))

        self.assertEqual(UCHAR_MAX, getargs_B(-1))
        self.assertEqual(0, getargs_B(0))
        self.assertEqual(UCHAR_MAX, getargs_B(UCHAR_MAX))
        self.assertEqual(0, getargs_B(UCHAR_MAX+1))

        self.assertEqual(42, getargs_B(42))
        self.assertEqual(UCHAR_MAX & VERY_LARGE, getargs_B(VERY_LARGE))

    def test_H(self):
        z _testcapi zaimportuj getargs_H
        # H returns 'unsigned short', no range checking
        self.assertRaises(TypeError, getargs_H, 3.14)
        self.assertEqual(99, getargs_H(Int()))
        self.assertEqual(0, getargs_H(IntSubclass()))
        self.assertRaises(TypeError, getargs_H, BadInt())
        przy self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_H(BadInt2()))
        self.assertEqual(0, getargs_H(BadInt3()))

        self.assertEqual(USHRT_MAX, getargs_H(-1))
        self.assertEqual(0, getargs_H(0))
        self.assertEqual(USHRT_MAX, getargs_H(USHRT_MAX))
        self.assertEqual(0, getargs_H(USHRT_MAX+1))

        self.assertEqual(42, getargs_H(42))

        self.assertEqual(VERY_LARGE & USHRT_MAX, getargs_H(VERY_LARGE))

    def test_I(self):
        z _testcapi zaimportuj getargs_I
        # I returns 'unsigned int', no range checking
        self.assertRaises(TypeError, getargs_I, 3.14)
        self.assertEqual(99, getargs_I(Int()))
        self.assertEqual(0, getargs_I(IntSubclass()))
        self.assertRaises(TypeError, getargs_I, BadInt())
        przy self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_I(BadInt2()))
        self.assertEqual(0, getargs_I(BadInt3()))

        self.assertEqual(UINT_MAX, getargs_I(-1))
        self.assertEqual(0, getargs_I(0))
        self.assertEqual(UINT_MAX, getargs_I(UINT_MAX))
        self.assertEqual(0, getargs_I(UINT_MAX+1))

        self.assertEqual(42, getargs_I(42))

        self.assertEqual(VERY_LARGE & UINT_MAX, getargs_I(VERY_LARGE))

    def test_k(self):
        z _testcapi zaimportuj getargs_k
        # k returns 'unsigned long', no range checking
        # it does nie accept float, albo instances przy __int__
        self.assertRaises(TypeError, getargs_k, 3.14)
        self.assertRaises(TypeError, getargs_k, Int())
        self.assertEqual(0, getargs_k(IntSubclass()))
        self.assertRaises(TypeError, getargs_k, BadInt())
        self.assertRaises(TypeError, getargs_k, BadInt2())
        self.assertEqual(0, getargs_k(BadInt3()))

        self.assertEqual(ULONG_MAX, getargs_k(-1))
        self.assertEqual(0, getargs_k(0))
        self.assertEqual(ULONG_MAX, getargs_k(ULONG_MAX))
        self.assertEqual(0, getargs_k(ULONG_MAX+1))

        self.assertEqual(42, getargs_k(42))

        self.assertEqual(VERY_LARGE & ULONG_MAX, getargs_k(VERY_LARGE))

klasa Signed_TestCase(unittest.TestCase):
    def test_h(self):
        z _testcapi zaimportuj getargs_h
        # h returns 'short', oraz does range checking (SHRT_MIN ... SHRT_MAX)
        self.assertRaises(TypeError, getargs_h, 3.14)
        self.assertEqual(99, getargs_h(Int()))
        self.assertEqual(0, getargs_h(IntSubclass()))
        self.assertRaises(TypeError, getargs_h, BadInt())
        przy self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_h(BadInt2()))
        self.assertEqual(0, getargs_h(BadInt3()))

        self.assertRaises(OverflowError, getargs_h, SHRT_MIN-1)
        self.assertEqual(SHRT_MIN, getargs_h(SHRT_MIN))
        self.assertEqual(SHRT_MAX, getargs_h(SHRT_MAX))
        self.assertRaises(OverflowError, getargs_h, SHRT_MAX+1)

        self.assertEqual(42, getargs_h(42))
        self.assertRaises(OverflowError, getargs_h, VERY_LARGE)

    def test_i(self):
        z _testcapi zaimportuj getargs_i
        # i returns 'int', oraz does range checking (INT_MIN ... INT_MAX)
        self.assertRaises(TypeError, getargs_i, 3.14)
        self.assertEqual(99, getargs_i(Int()))
        self.assertEqual(0, getargs_i(IntSubclass()))
        self.assertRaises(TypeError, getargs_i, BadInt())
        przy self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_i(BadInt2()))
        self.assertEqual(0, getargs_i(BadInt3()))

        self.assertRaises(OverflowError, getargs_i, INT_MIN-1)
        self.assertEqual(INT_MIN, getargs_i(INT_MIN))
        self.assertEqual(INT_MAX, getargs_i(INT_MAX))
        self.assertRaises(OverflowError, getargs_i, INT_MAX+1)

        self.assertEqual(42, getargs_i(42))
        self.assertRaises(OverflowError, getargs_i, VERY_LARGE)

    def test_l(self):
        z _testcapi zaimportuj getargs_l
        # l returns 'long', oraz does range checking (LONG_MIN ... LONG_MAX)
        self.assertRaises(TypeError, getargs_l, 3.14)
        self.assertEqual(99, getargs_l(Int()))
        self.assertEqual(0, getargs_l(IntSubclass()))
        self.assertRaises(TypeError, getargs_l, BadInt())
        przy self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_l(BadInt2()))
        self.assertEqual(0, getargs_l(BadInt3()))

        self.assertRaises(OverflowError, getargs_l, LONG_MIN-1)
        self.assertEqual(LONG_MIN, getargs_l(LONG_MIN))
        self.assertEqual(LONG_MAX, getargs_l(LONG_MAX))
        self.assertRaises(OverflowError, getargs_l, LONG_MAX+1)

        self.assertEqual(42, getargs_l(42))
        self.assertRaises(OverflowError, getargs_l, VERY_LARGE)

    def test_n(self):
        z _testcapi zaimportuj getargs_n
        # n returns 'Py_ssize_t', oraz does range checking
        # (PY_SSIZE_T_MIN ... PY_SSIZE_T_MAX)
        self.assertRaises(TypeError, getargs_n, 3.14)
        self.assertRaises(TypeError, getargs_n, Int())
        self.assertEqual(0, getargs_n(IntSubclass()))
        self.assertRaises(TypeError, getargs_n, BadInt())
        self.assertRaises(TypeError, getargs_n, BadInt2())
        self.assertEqual(0, getargs_n(BadInt3()))

        self.assertRaises(OverflowError, getargs_n, PY_SSIZE_T_MIN-1)
        self.assertEqual(PY_SSIZE_T_MIN, getargs_n(PY_SSIZE_T_MIN))
        self.assertEqual(PY_SSIZE_T_MAX, getargs_n(PY_SSIZE_T_MAX))
        self.assertRaises(OverflowError, getargs_n, PY_SSIZE_T_MAX+1)

        self.assertEqual(42, getargs_n(42))
        self.assertRaises(OverflowError, getargs_n, VERY_LARGE)


@unittest.skipIf(getargs_L jest Nic, 'PY_LONG_LONG jest nie available')
klasa LongLong_TestCase(unittest.TestCase):
    def test_L(self):
        z _testcapi zaimportuj getargs_L
        # L returns 'long long', oraz does range checking (LLONG_MIN
        # ... LLONG_MAX)
        self.assertRaises(TypeError, getargs_L, 3.14)
        self.assertRaises(TypeError, getargs_L, "Hello")
        self.assertEqual(99, getargs_L(Int()))
        self.assertEqual(0, getargs_L(IntSubclass()))
        self.assertRaises(TypeError, getargs_L, BadInt())
        przy self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_L(BadInt2()))
        self.assertEqual(0, getargs_L(BadInt3()))

        self.assertRaises(OverflowError, getargs_L, LLONG_MIN-1)
        self.assertEqual(LLONG_MIN, getargs_L(LLONG_MIN))
        self.assertEqual(LLONG_MAX, getargs_L(LLONG_MAX))
        self.assertRaises(OverflowError, getargs_L, LLONG_MAX+1)

        self.assertEqual(42, getargs_L(42))
        self.assertRaises(OverflowError, getargs_L, VERY_LARGE)

    def test_K(self):
        z _testcapi zaimportuj getargs_K
        # K zwróć 'unsigned long long', no range checking
        self.assertRaises(TypeError, getargs_K, 3.14)
        self.assertRaises(TypeError, getargs_K, Int())
        self.assertEqual(0, getargs_K(IntSubclass()))
        self.assertRaises(TypeError, getargs_K, BadInt())
        self.assertRaises(TypeError, getargs_K, BadInt2())
        self.assertEqual(0, getargs_K(BadInt3()))

        self.assertEqual(ULLONG_MAX, getargs_K(ULLONG_MAX))
        self.assertEqual(0, getargs_K(0))
        self.assertEqual(0, getargs_K(ULLONG_MAX+1))

        self.assertEqual(42, getargs_K(42))

        self.assertEqual(VERY_LARGE & ULLONG_MAX, getargs_K(VERY_LARGE))

klasa Paradox:
    "This statement jest false."
    def __bool__(self):
        podnieś NotImplementedError

klasa Boolean_TestCase(unittest.TestCase):
    def test_p(self):
        z _testcapi zaimportuj getargs_p
        self.assertEqual(0, getargs_p(Nieprawda))
        self.assertEqual(0, getargs_p(Nic))
        self.assertEqual(0, getargs_p(0))
        self.assertEqual(0, getargs_p(0.0))
        self.assertEqual(0, getargs_p(0j))
        self.assertEqual(0, getargs_p(''))
        self.assertEqual(0, getargs_p(()))
        self.assertEqual(0, getargs_p([]))
        self.assertEqual(0, getargs_p({}))

        self.assertEqual(1, getargs_p(Prawda))
        self.assertEqual(1, getargs_p(1))
        self.assertEqual(1, getargs_p(1.0))
        self.assertEqual(1, getargs_p(1j))
        self.assertEqual(1, getargs_p('x'))
        self.assertEqual(1, getargs_p((1,)))
        self.assertEqual(1, getargs_p([1]))
        self.assertEqual(1, getargs_p({1:2}))
        self.assertEqual(1, getargs_p(unittest.TestCase))

        self.assertRaises(NotImplementedError, getargs_p, Paradox())


klasa Tuple_TestCase(unittest.TestCase):
    def test_tuple(self):
        z _testcapi zaimportuj getargs_tuple

        ret = getargs_tuple(1, (2, 3))
        self.assertEqual(ret, (1,2,3))

        # make sure invalid tuple arguments are handled correctly
        klasa seq:
            def __len__(self):
                zwróć 2
            def __getitem__(self, n):
                podnieś ValueError
        self.assertRaises(TypeError, getargs_tuple, 1, seq())

klasa Keywords_TestCase(unittest.TestCase):
    def test_positional_args(self):
        # using all positional args
        self.assertEqual(
            getargs_keywords((1,2), 3, (4,(5,6)), (7,8,9), 10),
            (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
            )

    def test_mixed_args(self):
        # positional oraz keyword args
        self.assertEqual(
            getargs_keywords((1,2), 3, (4,(5,6)), arg4=(7,8,9), arg5=10),
            (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
            )

    def test_keyword_args(self):
        # all keywords
        self.assertEqual(
            getargs_keywords(arg1=(1,2), arg2=3, arg3=(4,(5,6)), arg4=(7,8,9), arg5=10),
            (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
            )

    def test_optional_args(self):
        # missing optional keyword args, skipping tuples
        self.assertEqual(
            getargs_keywords(arg1=(1,2), arg2=3, arg5=10),
            (1, 2, 3, -1, -1, -1, -1, -1, -1, 10)
            )

    def test_required_args(self):
        # required arg missing
        spróbuj:
            getargs_keywords(arg1=(1,2))
        wyjąwszy TypeError jako err:
            self.assertEqual(str(err), "Required argument 'arg2' (pos 2) nie found")
        inaczej:
            self.fail('TypeError should have been podnieśd')

    def test_too_many_args(self):
        spróbuj:
            getargs_keywords((1,2),3,(4,(5,6)),(7,8,9),10,111)
        wyjąwszy TypeError jako err:
            self.assertEqual(str(err), "function takes at most 5 arguments (6 given)")
        inaczej:
            self.fail('TypeError should have been podnieśd')

    def test_invalid_keyword(self):
        # extraneous keyword arg
        spróbuj:
            getargs_keywords((1,2),3,arg5=10,arg666=666)
        wyjąwszy TypeError jako err:
            self.assertEqual(str(err), "'arg666' jest an invalid keyword argument dla this function")
        inaczej:
            self.fail('TypeError should have been podnieśd')

    def test_surrogate_keyword(self):
        spróbuj:
            getargs_keywords((1,2), 3, (4,(5,6)), (7,8,9), **{'\uDC80': 10})
        wyjąwszy TypeError jako err:
            self.assertEqual(str(err), "'\udc80' jest an invalid keyword argument dla this function")
        inaczej:
            self.fail('TypeError should have been podnieśd')

klasa KeywordOnly_TestCase(unittest.TestCase):
    def test_positional_args(self):
        # using all possible positional args
        self.assertEqual(
            getargs_keyword_only(1, 2),
            (1, 2, -1)
            )

    def test_mixed_args(self):
        # positional oraz keyword args
        self.assertEqual(
            getargs_keyword_only(1, 2, keyword_only=3),
            (1, 2, 3)
            )

    def test_keyword_args(self):
        # all keywords
        self.assertEqual(
            getargs_keyword_only(required=1, optional=2, keyword_only=3),
            (1, 2, 3)
            )

    def test_optional_args(self):
        # missing optional keyword args, skipping tuples
        self.assertEqual(
            getargs_keyword_only(required=1, optional=2),
            (1, 2, -1)
            )
        self.assertEqual(
            getargs_keyword_only(required=1, keyword_only=3),
            (1, -1, 3)
            )

    def test_required_args(self):
        self.assertEqual(
            getargs_keyword_only(1),
            (1, -1, -1)
            )
        self.assertEqual(
            getargs_keyword_only(required=1),
            (1, -1, -1)
            )
        # required arg missing
        przy self.assertRaisesRegex(TypeError,
            "Required argument 'required' \(pos 1\) nie found"):
            getargs_keyword_only(optional=2)

        przy self.assertRaisesRegex(TypeError,
            "Required argument 'required' \(pos 1\) nie found"):
            getargs_keyword_only(keyword_only=3)

    def test_too_many_args(self):
        przy self.assertRaisesRegex(TypeError,
            "Function takes at most 2 positional arguments \(3 given\)"):
            getargs_keyword_only(1, 2, 3)

        przy self.assertRaisesRegex(TypeError,
            "function takes at most 3 arguments \(4 given\)"):
            getargs_keyword_only(1, 2, 3, keyword_only=5)

    def test_invalid_keyword(self):
        # extraneous keyword arg
        przy self.assertRaisesRegex(TypeError,
            "'monster' jest an invalid keyword argument dla this function"):
            getargs_keyword_only(1, 2, monster=666)

    def test_surrogate_keyword(self):
        przy self.assertRaisesRegex(TypeError,
            "'\udc80' jest an invalid keyword argument dla this function"):
            getargs_keyword_only(1, 2, **{'\uDC80': 10})

klasa Bytes_TestCase(unittest.TestCase):
    def test_c(self):
        z _testcapi zaimportuj getargs_c
        self.assertRaises(TypeError, getargs_c, b'abc')  # len > 1
        self.assertEqual(getargs_c(b'a'), b'a')
        self.assertEqual(getargs_c(bytearray(b'a')), b'a')
        self.assertRaises(TypeError, getargs_c, memoryview(b'a'))
        self.assertRaises(TypeError, getargs_c, 's')
        self.assertRaises(TypeError, getargs_c, Nic)

    def test_s(self):
        z _testcapi zaimportuj getargs_s
        self.assertEqual(getargs_s('abc\xe9'), b'abc\xc3\xa9')
        self.assertRaises(ValueError, getargs_s, 'nul:\0')
        self.assertRaises(TypeError, getargs_s, b'bytes')
        self.assertRaises(TypeError, getargs_s, bytearray(b'bytearray'))
        self.assertRaises(TypeError, getargs_s, memoryview(b'memoryview'))
        self.assertRaises(TypeError, getargs_s, Nic)

    def test_s_star(self):
        z _testcapi zaimportuj getargs_s_star
        self.assertEqual(getargs_s_star('abc\xe9'), b'abc\xc3\xa9')
        self.assertEqual(getargs_s_star('nul:\0'), b'nul:\0')
        self.assertEqual(getargs_s_star(b'bytes'), b'bytes')
        self.assertEqual(getargs_s_star(bytearray(b'bytearray')), b'bytearray')
        self.assertEqual(getargs_s_star(memoryview(b'memoryview')), b'memoryview')
        self.assertRaises(TypeError, getargs_s_star, Nic)

    def test_s_hash(self):
        z _testcapi zaimportuj getargs_s_hash
        self.assertEqual(getargs_s_hash('abc\xe9'), b'abc\xc3\xa9')
        self.assertEqual(getargs_s_hash('nul:\0'), b'nul:\0')
        self.assertEqual(getargs_s_hash(b'bytes'), b'bytes')
        self.assertRaises(TypeError, getargs_s_hash, bytearray(b'bytearray'))
        self.assertRaises(TypeError, getargs_s_hash, memoryview(b'memoryview'))
        self.assertRaises(TypeError, getargs_s_hash, Nic)

    def test_z(self):
        z _testcapi zaimportuj getargs_z
        self.assertEqual(getargs_z('abc\xe9'), b'abc\xc3\xa9')
        self.assertRaises(ValueError, getargs_z, 'nul:\0')
        self.assertRaises(TypeError, getargs_z, b'bytes')
        self.assertRaises(TypeError, getargs_z, bytearray(b'bytearray'))
        self.assertRaises(TypeError, getargs_z, memoryview(b'memoryview'))
        self.assertIsNic(getargs_z(Nic))

    def test_z_star(self):
        z _testcapi zaimportuj getargs_z_star
        self.assertEqual(getargs_z_star('abc\xe9'), b'abc\xc3\xa9')
        self.assertEqual(getargs_z_star('nul:\0'), b'nul:\0')
        self.assertEqual(getargs_z_star(b'bytes'), b'bytes')
        self.assertEqual(getargs_z_star(bytearray(b'bytearray')), b'bytearray')
        self.assertEqual(getargs_z_star(memoryview(b'memoryview')), b'memoryview')
        self.assertIsNic(getargs_z_star(Nic))

    def test_z_hash(self):
        z _testcapi zaimportuj getargs_z_hash
        self.assertEqual(getargs_z_hash('abc\xe9'), b'abc\xc3\xa9')
        self.assertEqual(getargs_z_hash('nul:\0'), b'nul:\0')
        self.assertEqual(getargs_z_hash(b'bytes'), b'bytes')
        self.assertRaises(TypeError, getargs_z_hash, bytearray(b'bytearray'))
        self.assertRaises(TypeError, getargs_z_hash, memoryview(b'memoryview'))
        self.assertIsNic(getargs_z_hash(Nic))

    def test_y(self):
        z _testcapi zaimportuj getargs_y
        self.assertRaises(TypeError, getargs_y, 'abc\xe9')
        self.assertEqual(getargs_y(b'bytes'), b'bytes')
        self.assertRaises(ValueError, getargs_y, b'nul:\0')
        self.assertRaises(TypeError, getargs_y, bytearray(b'bytearray'))
        self.assertRaises(TypeError, getargs_y, memoryview(b'memoryview'))
        self.assertRaises(TypeError, getargs_y, Nic)

    def test_y_star(self):
        z _testcapi zaimportuj getargs_y_star
        self.assertRaises(TypeError, getargs_y_star, 'abc\xe9')
        self.assertEqual(getargs_y_star(b'bytes'), b'bytes')
        self.assertEqual(getargs_y_star(b'nul:\0'), b'nul:\0')
        self.assertEqual(getargs_y_star(bytearray(b'bytearray')), b'bytearray')
        self.assertEqual(getargs_y_star(memoryview(b'memoryview')), b'memoryview')
        self.assertRaises(TypeError, getargs_y_star, Nic)

    def test_y_hash(self):
        z _testcapi zaimportuj getargs_y_hash
        self.assertRaises(TypeError, getargs_y_hash, 'abc\xe9')
        self.assertEqual(getargs_y_hash(b'bytes'), b'bytes')
        self.assertEqual(getargs_y_hash(b'nul:\0'), b'nul:\0')
        self.assertRaises(TypeError, getargs_y_hash, bytearray(b'bytearray'))
        self.assertRaises(TypeError, getargs_y_hash, memoryview(b'memoryview'))
        self.assertRaises(TypeError, getargs_y_hash, Nic)

    def test_w_star(self):
        # getargs_w_star() modifies first oraz last byte
        z _testcapi zaimportuj getargs_w_star
        self.assertRaises(TypeError, getargs_w_star, 'abc\xe9')
        self.assertRaises(TypeError, getargs_w_star, b'bytes')
        self.assertRaises(TypeError, getargs_w_star, b'nul:\0')
        self.assertRaises(TypeError, getargs_w_star, memoryview(b'bytes'))
        self.assertEqual(getargs_w_star(bytearray(b'bytearray')), b'[ytearra]')
        self.assertEqual(getargs_w_star(memoryview(bytearray(b'memoryview'))),
                         b'[emoryvie]')
        self.assertRaises(TypeError, getargs_w_star, Nic)


klasa Unicode_TestCase(unittest.TestCase):
    def test_u(self):
        z _testcapi zaimportuj getargs_u
        self.assertEqual(getargs_u('abc\xe9'), 'abc\xe9')
        self.assertRaises(ValueError, getargs_u, 'nul:\0')
        self.assertRaises(TypeError, getargs_u, b'bytes')
        self.assertRaises(TypeError, getargs_u, bytearray(b'bytearray'))
        self.assertRaises(TypeError, getargs_u, memoryview(b'memoryview'))
        self.assertRaises(TypeError, getargs_u, Nic)

    def test_u_hash(self):
        z _testcapi zaimportuj getargs_u_hash
        self.assertEqual(getargs_u_hash('abc\xe9'), 'abc\xe9')
        self.assertEqual(getargs_u_hash('nul:\0'), 'nul:\0')
        self.assertRaises(TypeError, getargs_u_hash, b'bytes')
        self.assertRaises(TypeError, getargs_u_hash, bytearray(b'bytearray'))
        self.assertRaises(TypeError, getargs_u_hash, memoryview(b'memoryview'))
        self.assertRaises(TypeError, getargs_u_hash, Nic)

    def test_Z(self):
        z _testcapi zaimportuj getargs_Z
        self.assertEqual(getargs_Z('abc\xe9'), 'abc\xe9')
        self.assertRaises(ValueError, getargs_Z, 'nul:\0')
        self.assertRaises(TypeError, getargs_Z, b'bytes')
        self.assertRaises(TypeError, getargs_Z, bytearray(b'bytearray'))
        self.assertRaises(TypeError, getargs_Z, memoryview(b'memoryview'))
        self.assertIsNic(getargs_Z(Nic))

    def test_Z_hash(self):
        z _testcapi zaimportuj getargs_Z_hash
        self.assertEqual(getargs_Z_hash('abc\xe9'), 'abc\xe9')
        self.assertEqual(getargs_Z_hash('nul:\0'), 'nul:\0')
        self.assertRaises(TypeError, getargs_Z_hash, b'bytes')
        self.assertRaises(TypeError, getargs_Z_hash, bytearray(b'bytearray'))
        self.assertRaises(TypeError, getargs_Z_hash, memoryview(b'memoryview'))
        self.assertIsNic(getargs_Z_hash(Nic))


jeżeli __name__ == "__main__":
    unittest.main()
