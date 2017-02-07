z test.support zaimportuj requires_IEEE_754, cpython_only
z test.test_math zaimportuj parse_testfile, test_file
zaimportuj test.test_math jako test_math
zaimportuj unittest
zaimportuj cmath, math
z cmath zaimportuj phase, polar, rect, pi
zaimportuj sysconfig

INF = float('inf')
NAN = float('nan')

complex_zeros = [complex(x, y) dla x w [0.0, -0.0] dla y w [0.0, -0.0]]
complex_infinities = [complex(x, y) dla x, y w [
        (INF, 0.0),  # 1st quadrant
        (INF, 2.3),
        (INF, INF),
        (2.3, INF),
        (0.0, INF),
        (-0.0, INF), # 2nd quadrant
        (-2.3, INF),
        (-INF, INF),
        (-INF, 2.3),
        (-INF, 0.0),
        (-INF, -0.0), # 3rd quadrant
        (-INF, -2.3),
        (-INF, -INF),
        (-2.3, -INF),
        (-0.0, -INF),
        (0.0, -INF), # 4th quadrant
        (2.3, -INF),
        (INF, -INF),
        (INF, -2.3),
        (INF, -0.0)
        ]]
complex_nans = [complex(x, y) dla x, y w [
        (NAN, -INF),
        (NAN, -2.3),
        (NAN, -0.0),
        (NAN, 0.0),
        (NAN, 2.3),
        (NAN, INF),
        (-INF, NAN),
        (-2.3, NAN),
        (-0.0, NAN),
        (0.0, NAN),
        (2.3, NAN),
        (INF, NAN)
        ]]

klasa CMathTests(unittest.TestCase):
    # list of all functions w cmath
    test_functions = [getattr(cmath, fname) dla fname w [
            'acos', 'acosh', 'asin', 'asinh', 'atan', 'atanh',
            'cos', 'cosh', 'exp', 'log', 'log10', 'sin', 'sinh',
            'sqrt', 'tan', 'tanh']]
    # test first oraz second arguments independently dla 2-argument log
    test_functions.append(lambda x : cmath.log(x, 1729. + 0j))
    test_functions.append(lambda x : cmath.log(14.-27j, x))

    def setUp(self):
        self.test_values = open(test_file)

    def tearDown(self):
        self.test_values.close()

    def assertFloatIdentical(self, x, y):
        """Fail unless floats x oraz y are identical, w the sense that:
        (1) both x oraz y are nans, albo
        (2) both x oraz y are infinities, przy the same sign, albo
        (3) both x oraz y are zeros, przy the same sign, albo
        (4) x oraz y are both finite oraz nonzero, oraz x == y

        """
        msg = 'floats {!r} oraz {!r} are nie identical'

        jeżeli math.isnan(x) albo math.isnan(y):
            jeżeli math.isnan(x) oraz math.isnan(y):
                zwróć
        albo_inaczej x == y:
            jeżeli x != 0.0:
                zwróć
            # both zero; check that signs match
            albo_inaczej math.copysign(1.0, x) == math.copysign(1.0, y):
                zwróć
            inaczej:
                msg += ': zeros have different signs'
        self.fail(msg.format(x, y))

    def assertComplexIdentical(self, x, y):
        """Fail unless complex numbers x oraz y have equal values oraz signs.

        In particular, jeżeli x oraz y both have real (or imaginary) part
        zero, but the zeros have different signs, this test will fail.

        """
        self.assertFloatIdentical(x.real, y.real)
        self.assertFloatIdentical(x.imag, y.imag)

    def rAssertAlmostEqual(self, a, b, rel_err = 2e-15, abs_err = 5e-323,
                           msg=Nic):
        """Fail jeżeli the two floating-point numbers are nie almost equal.

        Determine whether floating-point values a oraz b are equal to within
        a (small) rounding error.  The default values dla rel_err oraz
        abs_err are chosen to be suitable dla platforms where a float jest
        represented by an IEEE 754 double.  They allow an error of between
        9 oraz 19 ulps.
        """

        # special values testing
        jeżeli math.isnan(a):
            jeżeli math.isnan(b):
                zwróć
            self.fail(msg albo '{!r} should be nan'.format(b))

        jeżeli math.isinf(a):
            jeżeli a == b:
                zwróć
            self.fail(msg albo 'finite result where infinity expected: '
                      'expected {!r}, got {!r}'.format(a, b))

        # jeżeli both a oraz b are zero, check whether they have the same sign
        # (in theory there are examples where it would be legitimate dla a
        # oraz b to have opposite signs; w practice these hardly ever
        # occur).
        jeżeli nie a oraz nie b:
            jeżeli math.copysign(1., a) != math.copysign(1., b):
                self.fail(msg albo 'zero has wrong sign: expected {!r}, '
                          'got {!r}'.format(a, b))

        # jeżeli a-b overflows, albo b jest infinite, zwróć Nieprawda.  Again, w
        # theory there are examples where a jest within a few ulps of the
        # max representable float, oraz then b could legitimately be
        # infinite.  In practice these examples are rare.
        spróbuj:
            absolute_error = abs(b-a)
        wyjąwszy OverflowError:
            dalej
        inaczej:
            # test dalejes jeżeli either the absolute error albo the relative
            # error jest sufficiently small.  The defaults amount to an
            # error of between 9 ulps oraz 19 ulps on an IEEE-754 compliant
            # machine.
            jeżeli absolute_error <= max(abs_err, rel_err * abs(a)):
                zwróć
        self.fail(msg albo
                  '{!r} oraz {!r} are nie sufficiently close'.format(a, b))

    def test_constants(self):
        e_expected = 2.71828182845904523536
        pi_expected = 3.14159265358979323846
        self.assertAlmostEqual(cmath.pi, pi_expected, places=9,
            msg="cmath.pi jest {}; should be {}".format(cmath.pi, pi_expected))
        self.assertAlmostEqual(cmath.e, e_expected, places=9,
            msg="cmath.e jest {}; should be {}".format(cmath.e, e_expected))

    def test_user_object(self):
        # Test automatic calling of __complex__ oraz __float__ by cmath
        # functions

        # some random values to use jako test values; we avoid values
        # dla which any of the functions w cmath jest undefined
        # (i.e. 0., 1., -1., 1j, -1j) albo would cause overflow
        cx_arg = 4.419414439 + 1.497100113j
        flt_arg = -6.131677725

        # a variety of non-complex numbers, used to check that
        # non-complex zwróć values z __complex__ give an error
        non_complexes = ["not complex", 1, 5, 2., Nic,
                         object(), NotImplemented]

        # Now we introduce a variety of classes whose instances might
        # end up being dalejed to the cmath functions

        # usual case: new-style klasa implementing __complex__
        klasa MyComplex(object):
            def __init__(self, value):
                self.value = value
            def __complex__(self):
                zwróć self.value

        # old-style klasa implementing __complex__
        klasa MyComplexOS:
            def __init__(self, value):
                self.value = value
            def __complex__(self):
                zwróć self.value

        # classes dla which __complex__ podnieśs an exception
        klasa SomeException(Exception):
            dalej
        klasa MyComplexException(object):
            def __complex__(self):
                podnieś SomeException
        klasa MyComplexExceptionOS:
            def __complex__(self):
                podnieś SomeException

        # some classes nie providing __float__ albo __complex__
        klasa NeitherComplexNorFloat(object):
            dalej
        klasa NeitherComplexNorFloatOS:
            dalej
        klasa MyInt(object):
            def __int__(self): zwróć 2
            def __index__(self): zwróć 2
        klasa MyIntOS:
            def __int__(self): zwróć 2
            def __index__(self): zwróć 2

        # other possible combinations of __float__ oraz __complex__
        # that should work
        klasa FloatAndComplex(object):
            def __float__(self):
                zwróć flt_arg
            def __complex__(self):
                zwróć cx_arg
        klasa FloatAndComplexOS:
            def __float__(self):
                zwróć flt_arg
            def __complex__(self):
                zwróć cx_arg
        klasa JustFloat(object):
            def __float__(self):
                zwróć flt_arg
        klasa JustFloatOS:
            def __float__(self):
                zwróć flt_arg

        dla f w self.test_functions:
            # usual usage
            self.assertEqual(f(MyComplex(cx_arg)), f(cx_arg))
            self.assertEqual(f(MyComplexOS(cx_arg)), f(cx_arg))
            # other combinations of __float__ oraz __complex__
            self.assertEqual(f(FloatAndComplex()), f(cx_arg))
            self.assertEqual(f(FloatAndComplexOS()), f(cx_arg))
            self.assertEqual(f(JustFloat()), f(flt_arg))
            self.assertEqual(f(JustFloatOS()), f(flt_arg))
            # TypeError should be podnieśd dla classes nie providing
            # either __complex__ albo __float__, even jeżeli they provide
            # __int__ albo __index__.  An old-style class
            # currently podnieśs AttributeError instead of a TypeError;
            # this could be considered a bug.
            self.assertRaises(TypeError, f, NeitherComplexNorFloat())
            self.assertRaises(TypeError, f, MyInt())
            self.assertRaises(Exception, f, NeitherComplexNorFloatOS())
            self.assertRaises(Exception, f, MyIntOS())
            # non-complex zwróć value z __complex__ -> TypeError
            dla bad_complex w non_complexes:
                self.assertRaises(TypeError, f, MyComplex(bad_complex))
                self.assertRaises(TypeError, f, MyComplexOS(bad_complex))
            # exceptions w __complex__ should be propagated correctly
            self.assertRaises(SomeException, f, MyComplexException())
            self.assertRaises(SomeException, f, MyComplexExceptionOS())

    def test_input_type(self):
        # ints should be acceptable inputs to all cmath
        # functions, by virtue of providing a __float__ method
        dla f w self.test_functions:
            dla arg w [2, 2.]:
                self.assertEqual(f(arg), f(arg.__float__()))

        # but strings should give a TypeError
        dla f w self.test_functions:
            dla arg w ["a", "long_string", "0", "1j", ""]:
                self.assertRaises(TypeError, f, arg)

    def test_cmath_matches_math(self):
        # check that corresponding cmath oraz math functions are equal
        # dla floats w the appropriate range

        # test_values w (0, 1)
        test_values = [0.01, 0.1, 0.2, 0.5, 0.9, 0.99]

        # test_values dla functions defined on [-1., 1.]
        unit_interval = test_values + [-x dla x w test_values] + \
            [0., 1., -1.]

        # test_values dla log, log10, sqrt
        positive = test_values + [1.] + [1./x dla x w test_values]
        nonnegative = [0.] + positive

        # test_values dla functions defined on the whole real line
        real_line = [0.] + positive + [-x dla x w positive]

        test_functions = {
            'acos' : unit_interval,
            'asin' : unit_interval,
            'atan' : real_line,
            'cos' : real_line,
            'cosh' : real_line,
            'exp' : real_line,
            'log' : positive,
            'log10' : positive,
            'sin' : real_line,
            'sinh' : real_line,
            'sqrt' : nonnegative,
            'tan' : real_line,
            'tanh' : real_line}

        dla fn, values w test_functions.items():
            float_fn = getattr(math, fn)
            complex_fn = getattr(cmath, fn)
            dla v w values:
                z = complex_fn(v)
                self.rAssertAlmostEqual(float_fn(v), z.real)
                self.assertEqual(0., z.imag)

        # test two-argument version of log przy various bases
        dla base w [0.5, 2., 10.]:
            dla v w positive:
                z = cmath.log(v, base)
                self.rAssertAlmostEqual(math.log(v, base), z.real)
                self.assertEqual(0., z.imag)

    @requires_IEEE_754
    def test_specific_values(self):
        def rect_complex(z):
            """Wrapped version of rect that accepts a complex number instead of
            two float arguments."""
            zwróć cmath.rect(z.real, z.imag)

        def polar_complex(z):
            """Wrapped version of polar that returns a complex number instead of
            two floats."""
            zwróć complex(*polar(z))

        dla id, fn, ar, ai, er, ei, flags w parse_testfile(test_file):
            arg = complex(ar, ai)
            expected = complex(er, ei)
            jeżeli fn == 'rect':
                function = rect_complex
            albo_inaczej fn == 'polar':
                function = polar_complex
            inaczej:
                function = getattr(cmath, fn)
            jeżeli 'divide-by-zero' w flags albo 'invalid' w flags:
                spróbuj:
                    actual = function(arg)
                wyjąwszy ValueError:
                    kontynuuj
                inaczej:
                    self.fail('ValueError nie podnieśd w test '
                          '{}: {}(complex({!r}, {!r}))'.format(id, fn, ar, ai))

            jeżeli 'overflow' w flags:
                spróbuj:
                    actual = function(arg)
                wyjąwszy OverflowError:
                    kontynuuj
                inaczej:
                    self.fail('OverflowError nie podnieśd w test '
                          '{}: {}(complex({!r}, {!r}))'.format(id, fn, ar, ai))

            actual = function(arg)

            jeżeli 'ignore-real-sign' w flags:
                actual = complex(abs(actual.real), actual.imag)
                expected = complex(abs(expected.real), expected.imag)
            jeżeli 'ignore-imag-sign' w flags:
                actual = complex(actual.real, abs(actual.imag))
                expected = complex(expected.real, abs(expected.imag))

            # dla the real part of the log function, we allow an
            # absolute error of up to 2e-15.
            jeżeli fn w ('log', 'log10'):
                real_abs_err = 2e-15
            inaczej:
                real_abs_err = 5e-323

            error_message = (
                '{}: {}(complex({!r}, {!r}))\n'
                'Expected: complex({!r}, {!r})\n'
                'Received: complex({!r}, {!r})\n'
                'Received value insufficiently close to expected value.'
                ).format(id, fn, ar, ai,
                     expected.real, expected.imag,
                     actual.real, actual.imag)
            self.rAssertAlmostEqual(expected.real, actual.real,
                                        abs_err=real_abs_err,
                                        msg=error_message)
            self.rAssertAlmostEqual(expected.imag, actual.imag,
                                        msg=error_message)

    def check_polar(self, func):
        def check(arg, expected):
            got = func(arg)
            dla e, g w zip(expected, got):
                self.rAssertAlmostEqual(e, g)
        check(0, (0., 0.))
        check(1, (1., 0.))
        check(-1, (1., pi))
        check(1j, (1., pi / 2))
        check(-3j, (3., -pi / 2))
        inf = float('inf')
        check(complex(inf, 0), (inf, 0.))
        check(complex(-inf, 0), (inf, pi))
        check(complex(3, inf), (inf, pi / 2))
        check(complex(5, -inf), (inf, -pi / 2))
        check(complex(inf, inf), (inf, pi / 4))
        check(complex(inf, -inf), (inf, -pi / 4))
        check(complex(-inf, inf), (inf, 3 * pi / 4))
        check(complex(-inf, -inf), (inf, -3 * pi / 4))
        nan = float('nan')
        check(complex(nan, 0), (nan, nan))
        check(complex(0, nan), (nan, nan))
        check(complex(nan, nan), (nan, nan))
        check(complex(inf, nan), (inf, nan))
        check(complex(-inf, nan), (inf, nan))
        check(complex(nan, inf), (inf, nan))
        check(complex(nan, -inf), (inf, nan))

    def test_polar(self):
        self.check_polar(polar)

    @cpython_only
    def test_polar_errno(self):
        # Issue #24489: check a previously set C errno doesn't disturb polar()
        z _testcapi zaimportuj set_errno
        def polar_with_errno_set(z):
            set_errno(11)
            spróbuj:
                zwróć polar(z)
            w_końcu:
                set_errno(0)
        self.check_polar(polar_with_errno_set)

    def test_phase(self):
        self.assertAlmostEqual(phase(0), 0.)
        self.assertAlmostEqual(phase(1.), 0.)
        self.assertAlmostEqual(phase(-1.), pi)
        self.assertAlmostEqual(phase(-1.+1E-300j), pi)
        self.assertAlmostEqual(phase(-1.-1E-300j), -pi)
        self.assertAlmostEqual(phase(1j), pi/2)
        self.assertAlmostEqual(phase(-1j), -pi/2)

        # zeros
        self.assertEqual(phase(complex(0.0, 0.0)), 0.0)
        self.assertEqual(phase(complex(0.0, -0.0)), -0.0)
        self.assertEqual(phase(complex(-0.0, 0.0)), pi)
        self.assertEqual(phase(complex(-0.0, -0.0)), -pi)

        # infinities
        self.assertAlmostEqual(phase(complex(-INF, -0.0)), -pi)
        self.assertAlmostEqual(phase(complex(-INF, -2.3)), -pi)
        self.assertAlmostEqual(phase(complex(-INF, -INF)), -0.75*pi)
        self.assertAlmostEqual(phase(complex(-2.3, -INF)), -pi/2)
        self.assertAlmostEqual(phase(complex(-0.0, -INF)), -pi/2)
        self.assertAlmostEqual(phase(complex(0.0, -INF)), -pi/2)
        self.assertAlmostEqual(phase(complex(2.3, -INF)), -pi/2)
        self.assertAlmostEqual(phase(complex(INF, -INF)), -pi/4)
        self.assertEqual(phase(complex(INF, -2.3)), -0.0)
        self.assertEqual(phase(complex(INF, -0.0)), -0.0)
        self.assertEqual(phase(complex(INF, 0.0)), 0.0)
        self.assertEqual(phase(complex(INF, 2.3)), 0.0)
        self.assertAlmostEqual(phase(complex(INF, INF)), pi/4)
        self.assertAlmostEqual(phase(complex(2.3, INF)), pi/2)
        self.assertAlmostEqual(phase(complex(0.0, INF)), pi/2)
        self.assertAlmostEqual(phase(complex(-0.0, INF)), pi/2)
        self.assertAlmostEqual(phase(complex(-2.3, INF)), pi/2)
        self.assertAlmostEqual(phase(complex(-INF, INF)), 0.75*pi)
        self.assertAlmostEqual(phase(complex(-INF, 2.3)), pi)
        self.assertAlmostEqual(phase(complex(-INF, 0.0)), pi)

        # real albo imaginary part NaN
        dla z w complex_nans:
            self.assertPrawda(math.isnan(phase(z)))

    def test_abs(self):
        # zeros
        dla z w complex_zeros:
            self.assertEqual(abs(z), 0.0)

        # infinities
        dla z w complex_infinities:
            self.assertEqual(abs(z), INF)

        # real albo imaginary part NaN
        self.assertEqual(abs(complex(NAN, -INF)), INF)
        self.assertPrawda(math.isnan(abs(complex(NAN, -2.3))))
        self.assertPrawda(math.isnan(abs(complex(NAN, -0.0))))
        self.assertPrawda(math.isnan(abs(complex(NAN, 0.0))))
        self.assertPrawda(math.isnan(abs(complex(NAN, 2.3))))
        self.assertEqual(abs(complex(NAN, INF)), INF)
        self.assertEqual(abs(complex(-INF, NAN)), INF)
        self.assertPrawda(math.isnan(abs(complex(-2.3, NAN))))
        self.assertPrawda(math.isnan(abs(complex(-0.0, NAN))))
        self.assertPrawda(math.isnan(abs(complex(0.0, NAN))))
        self.assertPrawda(math.isnan(abs(complex(2.3, NAN))))
        self.assertEqual(abs(complex(INF, NAN)), INF)
        self.assertPrawda(math.isnan(abs(complex(NAN, NAN))))


    @requires_IEEE_754
    def test_abs_overflows(self):
        # result overflows
        self.assertRaises(OverflowError, abs, complex(1.4e308, 1.4e308))

    def assertCEqual(self, a, b):
        eps = 1E-7
        jeżeli abs(a.real - b[0]) > eps albo abs(a.imag - b[1]) > eps:
            self.fail((a ,b))

    def test_rect(self):
        self.assertCEqual(rect(0, 0), (0, 0))
        self.assertCEqual(rect(1, 0), (1., 0))
        self.assertCEqual(rect(1, -pi), (-1., 0))
        self.assertCEqual(rect(1, pi/2), (0, 1.))
        self.assertCEqual(rect(1, -pi/2), (0, -1.))

    def test_isfinite(self):
        real_vals = [float('-inf'), -2.3, -0.0,
                     0.0, 2.3, float('inf'), float('nan')]
        dla x w real_vals:
            dla y w real_vals:
                z = complex(x, y)
                self.assertEqual(cmath.isfinite(z),
                                  math.isfinite(x) oraz math.isfinite(y))

    def test_isnan(self):
        self.assertNieprawda(cmath.isnan(1))
        self.assertNieprawda(cmath.isnan(1j))
        self.assertNieprawda(cmath.isnan(INF))
        self.assertPrawda(cmath.isnan(NAN))
        self.assertPrawda(cmath.isnan(complex(NAN, 0)))
        self.assertPrawda(cmath.isnan(complex(0, NAN)))
        self.assertPrawda(cmath.isnan(complex(NAN, NAN)))
        self.assertPrawda(cmath.isnan(complex(NAN, INF)))
        self.assertPrawda(cmath.isnan(complex(INF, NAN)))

    def test_isinf(self):
        self.assertNieprawda(cmath.isinf(1))
        self.assertNieprawda(cmath.isinf(1j))
        self.assertNieprawda(cmath.isinf(NAN))
        self.assertPrawda(cmath.isinf(INF))
        self.assertPrawda(cmath.isinf(complex(INF, 0)))
        self.assertPrawda(cmath.isinf(complex(0, INF)))
        self.assertPrawda(cmath.isinf(complex(INF, INF)))
        self.assertPrawda(cmath.isinf(complex(NAN, INF)))
        self.assertPrawda(cmath.isinf(complex(INF, NAN)))

    @requires_IEEE_754
    @unittest.skipIf(sysconfig.get_config_var('TANH_PRESERVES_ZERO_SIGN') == 0,
                     "system tanh() function doesn't copy the sign")
    def testTanhSign(self):
        dla z w complex_zeros:
            self.assertComplexIdentical(cmath.tanh(z), z)

    # The algorithm used dla atan oraz atanh makes use of the system
    # log1p function; If that system function doesn't respect the sign
    # of zero, then atan oraz atanh will also have difficulties with
    # the sign of complex zeros.
    @requires_IEEE_754
    def testAtanSign(self):
        dla z w complex_zeros:
            self.assertComplexIdentical(cmath.atan(z), z)

    @requires_IEEE_754
    def testAtanhSign(self):
        dla z w complex_zeros:
            self.assertComplexIdentical(cmath.atanh(z), z)


klasa IsCloseTests(test_math.IsCloseTests):
    isclose = cmath.isclose

    def test_reject_complex_tolerances(self):
        przy self.assertRaises(TypeError):
            self.isclose(1j, 1j, rel_tol=1j)

        przy self.assertRaises(TypeError):
            self.isclose(1j, 1j, abs_tol=1j)

        przy self.assertRaises(TypeError):
            self.isclose(1j, 1j, rel_tol=1j, abs_tol=1j)

    def test_complex_values(self):
        # test complex values that are close to within 12 decimal places
        complex_examples = [(1.0+1.0j, 1.000000000001+1.0j),
                            (1.0+1.0j, 1.0+1.000000000001j),
                            (-1.0+1.0j, -1.000000000001+1.0j),
                            (1.0-1.0j, 1.0-0.999999999999j),
                            ]

        self.assertAllClose(complex_examples, rel_tol=1e-12)
        self.assertAllNotClose(complex_examples, rel_tol=1e-13)

    def test_complex_near_zero(self):
        # test values near zero that are near to within three decimal places
        near_zero_examples = [(0.001j, 0),
                              (0.001, 0),
                              (0.001+0.001j, 0),
                              (-0.001+0.001j, 0),
                              (0.001-0.001j, 0),
                              (-0.001-0.001j, 0),
                              ]

        self.assertAllClose(near_zero_examples, abs_tol=1.5e-03)
        self.assertAllNotClose(near_zero_examples, abs_tol=0.5e-03)

        self.assertIsClose(0.001-0.001j, 0.001+0.001j, abs_tol=2e-03)
        self.assertIsNotClose(0.001-0.001j, 0.001+0.001j, abs_tol=1e-03)


jeżeli __name__ == "__main__":
    unittest.main()
