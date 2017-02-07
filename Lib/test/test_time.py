z test zaimportuj support
zaimportuj enum
zaimportuj locale
zaimportuj platform
zaimportuj sys
zaimportuj sysconfig
zaimportuj time
zaimportuj unittest
spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic
spróbuj:
    zaimportuj _testcapi
wyjąwszy ImportError:
    _testcapi = Nic


# Max year jest only limited by the size of C int.
SIZEOF_INT = sysconfig.get_config_var('SIZEOF_INT') albo 4
TIME_MAXYEAR = (1 << 8 * SIZEOF_INT - 1) - 1
TIME_MINYEAR = -TIME_MAXYEAR - 1

US_TO_NS = 10 ** 3
MS_TO_NS = 10 ** 6
SEC_TO_NS = 10 ** 9

klasa _PyTime(enum.IntEnum):
    # Round towards minus infinity (-inf)
    ROUND_FLOOR = 0
    # Round towards infinity (+inf)
    ROUND_CEILING = 1

ALL_ROUNDING_METHODS = (_PyTime.ROUND_FLOOR, _PyTime.ROUND_CEILING)


klasa TimeTestCase(unittest.TestCase):

    def setUp(self):
        self.t = time.time()

    def test_data_attributes(self):
        time.altzone
        time.daylight
        time.timezone
        time.tzname

    def test_time(self):
        time.time()
        info = time.get_clock_info('time')
        self.assertNieprawda(info.monotonic)
        self.assertPrawda(info.adjustable)

    def test_clock(self):
        time.clock()

        info = time.get_clock_info('clock')
        self.assertPrawda(info.monotonic)
        self.assertNieprawda(info.adjustable)

    @unittest.skipUnless(hasattr(time, 'clock_gettime'),
                         'need time.clock_gettime()')
    def test_clock_realtime(self):
        time.clock_gettime(time.CLOCK_REALTIME)

    @unittest.skipUnless(hasattr(time, 'clock_gettime'),
                         'need time.clock_gettime()')
    @unittest.skipUnless(hasattr(time, 'CLOCK_MONOTONIC'),
                         'need time.CLOCK_MONOTONIC')
    def test_clock_monotonic(self):
        a = time.clock_gettime(time.CLOCK_MONOTONIC)
        b = time.clock_gettime(time.CLOCK_MONOTONIC)
        self.assertLessEqual(a, b)

    @unittest.skipUnless(hasattr(time, 'clock_getres'),
                         'need time.clock_getres()')
    def test_clock_getres(self):
        res = time.clock_getres(time.CLOCK_REALTIME)
        self.assertGreater(res, 0.0)
        self.assertLessEqual(res, 1.0)

    @unittest.skipUnless(hasattr(time, 'clock_settime'),
                         'need time.clock_settime()')
    def test_clock_settime(self):
        t = time.clock_gettime(time.CLOCK_REALTIME)
        spróbuj:
            time.clock_settime(time.CLOCK_REALTIME, t)
        wyjąwszy PermissionError:
            dalej

        jeżeli hasattr(time, 'CLOCK_MONOTONIC'):
            self.assertRaises(OSError,
                              time.clock_settime, time.CLOCK_MONOTONIC, 0)

    def test_conversions(self):
        self.assertEqual(time.ctime(self.t),
                         time.asctime(time.localtime(self.t)))
        self.assertEqual(int(time.mktime(time.localtime(self.t))),
                         int(self.t))

    def test_sleep(self):
        self.assertRaises(ValueError, time.sleep, -2)
        self.assertRaises(ValueError, time.sleep, -1)
        time.sleep(1.2)

    def test_strftime(self):
        tt = time.gmtime(self.t)
        dla directive w ('a', 'A', 'b', 'B', 'c', 'd', 'H', 'I',
                          'j', 'm', 'M', 'p', 'S',
                          'U', 'w', 'W', 'x', 'X', 'y', 'Y', 'Z', '%'):
            format = ' %' + directive
            spróbuj:
                time.strftime(format, tt)
            wyjąwszy ValueError:
                self.fail('conversion specifier: %r failed.' % format)

    def _bounds_checking(self, func):
        # Make sure that strftime() checks the bounds of the various parts
        # of the time tuple (0 jest valid dla *all* values).

        # The year field jest tested by other test cases above

        # Check month [1, 12] + zero support
        func((1900, 0, 1, 0, 0, 0, 0, 1, -1))
        func((1900, 12, 1, 0, 0, 0, 0, 1, -1))
        self.assertRaises(ValueError, func,
                            (1900, -1, 1, 0, 0, 0, 0, 1, -1))
        self.assertRaises(ValueError, func,
                            (1900, 13, 1, 0, 0, 0, 0, 1, -1))
        # Check day of month [1, 31] + zero support
        func((1900, 1, 0, 0, 0, 0, 0, 1, -1))
        func((1900, 1, 31, 0, 0, 0, 0, 1, -1))
        self.assertRaises(ValueError, func,
                            (1900, 1, -1, 0, 0, 0, 0, 1, -1))
        self.assertRaises(ValueError, func,
                            (1900, 1, 32, 0, 0, 0, 0, 1, -1))
        # Check hour [0, 23]
        func((1900, 1, 1, 23, 0, 0, 0, 1, -1))
        self.assertRaises(ValueError, func,
                            (1900, 1, 1, -1, 0, 0, 0, 1, -1))
        self.assertRaises(ValueError, func,
                            (1900, 1, 1, 24, 0, 0, 0, 1, -1))
        # Check minute [0, 59]
        func((1900, 1, 1, 0, 59, 0, 0, 1, -1))
        self.assertRaises(ValueError, func,
                            (1900, 1, 1, 0, -1, 0, 0, 1, -1))
        self.assertRaises(ValueError, func,
                            (1900, 1, 1, 0, 60, 0, 0, 1, -1))
        # Check second [0, 61]
        self.assertRaises(ValueError, func,
                            (1900, 1, 1, 0, 0, -1, 0, 1, -1))
        # C99 only requires allowing dla one leap second, but Python's docs say
        # allow two leap seconds (0..61)
        func((1900, 1, 1, 0, 0, 60, 0, 1, -1))
        func((1900, 1, 1, 0, 0, 61, 0, 1, -1))
        self.assertRaises(ValueError, func,
                            (1900, 1, 1, 0, 0, 62, 0, 1, -1))
        # No check dla upper-bound day of week;
        #  value forced into range by a ``% 7`` calculation.
        # Start check at -2 since gettmarg() increments value before taking
        #  modulo.
        self.assertEqual(func((1900, 1, 1, 0, 0, 0, -1, 1, -1)),
                         func((1900, 1, 1, 0, 0, 0, +6, 1, -1)))
        self.assertRaises(ValueError, func,
                            (1900, 1, 1, 0, 0, 0, -2, 1, -1))
        # Check day of the year [1, 366] + zero support
        func((1900, 1, 1, 0, 0, 0, 0, 0, -1))
        func((1900, 1, 1, 0, 0, 0, 0, 366, -1))
        self.assertRaises(ValueError, func,
                            (1900, 1, 1, 0, 0, 0, 0, -1, -1))
        self.assertRaises(ValueError, func,
                            (1900, 1, 1, 0, 0, 0, 0, 367, -1))

    def test_strftime_bounding_check(self):
        self._bounds_checking(lambda tup: time.strftime('', tup))

    def test_strftime_format_check(self):
        # Test that strftime does nie crash on invalid format strings
        # that may trigger a buffer overread. When nie triggered,
        # strftime may succeed albo podnieś ValueError depending on
        # the platform.
        dla x w [ '', 'A', '%A', '%AA' ]:
            dla y w range(0x0, 0x10):
                dla z w [ '%', 'A%', 'AA%', '%A%', 'A%A%', '%#' ]:
                    spróbuj:
                        time.strftime(x * y + z)
                    wyjąwszy ValueError:
                        dalej

    def test_default_values_for_zero(self):
        # Make sure that using all zeros uses the proper default
        # values.  No test dla daylight savings since strftime() does
        # nie change output based on its value oraz no test dla year
        # because systems vary w their support dla year 0.
        expected = "2000 01 01 00 00 00 1 001"
        przy support.check_warnings():
            result = time.strftime("%Y %m %d %H %M %S %w %j", (2000,)+(0,)*8)
        self.assertEqual(expected, result)

    def test_strptime(self):
        # Should be able to go round-trip z strftime to strptime without
        # raising an exception.
        tt = time.gmtime(self.t)
        dla directive w ('a', 'A', 'b', 'B', 'c', 'd', 'H', 'I',
                          'j', 'm', 'M', 'p', 'S',
                          'U', 'w', 'W', 'x', 'X', 'y', 'Y', 'Z', '%'):
            format = '%' + directive
            strf_output = time.strftime(format, tt)
            spróbuj:
                time.strptime(strf_output, format)
            wyjąwszy ValueError:
                self.fail("conversion specifier %r failed przy '%s' input." %
                          (format, strf_output))

    def test_strptime_bytes(self):
        # Make sure only strings are accepted jako arguments to strptime.
        self.assertRaises(TypeError, time.strptime, b'2009', "%Y")
        self.assertRaises(TypeError, time.strptime, '2009', b'%Y')

    def test_strptime_exception_context(self):
        # check that this doesn't chain exceptions needlessly (see #17572)
        przy self.assertRaises(ValueError) jako e:
            time.strptime('', '%D')
        self.assertIs(e.exception.__suppress_context__, Prawda)
        # additional check dla IndexError branch (issue #19545)
        przy self.assertRaises(ValueError) jako e:
            time.strptime('19', '%Y %')
        self.assertIs(e.exception.__suppress_context__, Prawda)

    def test_asctime(self):
        time.asctime(time.gmtime(self.t))

        # Max year jest only limited by the size of C int.
        dla bigyear w TIME_MAXYEAR, TIME_MINYEAR:
            asc = time.asctime((bigyear, 6, 1) + (0,) * 6)
            self.assertEqual(asc[-len(str(bigyear)):], str(bigyear))
        self.assertRaises(OverflowError, time.asctime,
                          (TIME_MAXYEAR + 1,) + (0,) * 8)
        self.assertRaises(OverflowError, time.asctime,
                          (TIME_MINYEAR - 1,) + (0,) * 8)
        self.assertRaises(TypeError, time.asctime, 0)
        self.assertRaises(TypeError, time.asctime, ())
        self.assertRaises(TypeError, time.asctime, (0,) * 10)

    def test_asctime_bounding_check(self):
        self._bounds_checking(time.asctime)

    def test_ctime(self):
        t = time.mktime((1973, 9, 16, 1, 3, 52, 0, 0, -1))
        self.assertEqual(time.ctime(t), 'Sun Sep 16 01:03:52 1973')
        t = time.mktime((2000, 1, 1, 0, 0, 0, 0, 0, -1))
        self.assertEqual(time.ctime(t), 'Sat Jan  1 00:00:00 2000')
        dla year w [-100, 100, 1000, 2000, 2050, 10000]:
            spróbuj:
                testval = time.mktime((year, 1, 10) + (0,)*6)
            wyjąwszy (ValueError, OverflowError):
                # If mktime fails, ctime will fail too.  This may happen
                # on some platforms.
                dalej
            inaczej:
                self.assertEqual(time.ctime(testval)[20:], str(year))

    @unittest.skipUnless(hasattr(time, "tzset"),
                         "time module has no attribute tzset")
    def test_tzset(self):

        z os zaimportuj environ

        # Epoch time of midnight Dec 25th 2002. Never DST w northern
        # hemisphere.
        xmas2002 = 1040774400.0

        # These formats are correct dla 2002, oraz possibly future years
        # This format jest the 'standard' jako documented at:
        # http://www.opengroup.org/onlinepubs/007904975/basedefs/xbd_chap08.html
        # They are also documented w the tzset(3) man page on most Unix
        # systems.
        eastern = 'EST+05EDT,M4.1.0,M10.5.0'
        victoria = 'AEST-10AEDT-11,M10.5.0,M3.5.0'
        utc='UTC+0'

        org_TZ = environ.get('TZ',Nic)
        spróbuj:
            # Make sure we can switch to UTC time oraz results are correct
            # Note that unknown timezones default to UTC.
            # Note that altzone jest undefined w UTC, jako there jest no DST
            environ['TZ'] = eastern
            time.tzset()
            environ['TZ'] = utc
            time.tzset()
            self.assertEqual(
                time.gmtime(xmas2002), time.localtime(xmas2002)
                )
            self.assertEqual(time.daylight, 0)
            self.assertEqual(time.timezone, 0)
            self.assertEqual(time.localtime(xmas2002).tm_isdst, 0)

            # Make sure we can switch to US/Eastern
            environ['TZ'] = eastern
            time.tzset()
            self.assertNotEqual(time.gmtime(xmas2002), time.localtime(xmas2002))
            self.assertEqual(time.tzname, ('EST', 'EDT'))
            self.assertEqual(len(time.tzname), 2)
            self.assertEqual(time.daylight, 1)
            self.assertEqual(time.timezone, 18000)
            self.assertEqual(time.altzone, 14400)
            self.assertEqual(time.localtime(xmas2002).tm_isdst, 0)
            self.assertEqual(len(time.tzname), 2)

            # Now go to the southern hemisphere.
            environ['TZ'] = victoria
            time.tzset()
            self.assertNotEqual(time.gmtime(xmas2002), time.localtime(xmas2002))

            # Issue #11886: Australian Eastern Standard Time (UTC+10) jest called
            # "EST" (as Eastern Standard Time, UTC-5) instead of "AEST"
            # (non-DST timezone), oraz "EDT" instead of "AEDT" (DST timezone),
            # on some operating systems (e.g. FreeBSD), which jest wrong. See for
            # example this bug:
            # http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=93810
            self.assertIn(time.tzname[0], ('AEST' 'EST'), time.tzname[0])
            self.assertPrawda(time.tzname[1] w ('AEDT', 'EDT'), str(time.tzname[1]))
            self.assertEqual(len(time.tzname), 2)
            self.assertEqual(time.daylight, 1)
            self.assertEqual(time.timezone, -36000)
            self.assertEqual(time.altzone, -39600)
            self.assertEqual(time.localtime(xmas2002).tm_isdst, 1)

        w_końcu:
            # Repair TZ environment variable w case any other tests
            # rely on it.
            jeżeli org_TZ jest nie Nic:
                environ['TZ'] = org_TZ
            albo_inaczej 'TZ' w environ:
                usuń environ['TZ']
            time.tzset()

    def test_insane_timestamps(self):
        # It's possible that some platform maps time_t to double,
        # oraz that this test will fail there.  This test should
        # exempt such platforms (provided they zwróć reasonable
        # results!).
        dla func w time.ctime, time.gmtime, time.localtime:
            dla unreasonable w -1e200, 1e200:
                self.assertRaises(OverflowError, func, unreasonable)

    def test_ctime_without_arg(self):
        # Not sure how to check the values, since the clock could tick
        # at any time.  Make sure these are at least accepted oraz
        # don't podnieś errors.
        time.ctime()
        time.ctime(Nic)

    def test_gmtime_without_arg(self):
        gt0 = time.gmtime()
        gt1 = time.gmtime(Nic)
        t0 = time.mktime(gt0)
        t1 = time.mktime(gt1)
        self.assertAlmostEqual(t1, t0, delta=0.2)

    def test_localtime_without_arg(self):
        lt0 = time.localtime()
        lt1 = time.localtime(Nic)
        t0 = time.mktime(lt0)
        t1 = time.mktime(lt1)
        self.assertAlmostEqual(t1, t0, delta=0.2)

    def test_mktime(self):
        # Issue #1726687
        dla t w (-2, -1, 0, 1):
            jeżeli sys.platform.startswith('aix') oraz t == -1:
                # Issue #11188, #19748: mktime() returns -1 on error. On Linux,
                # the tm_wday field jest used jako a sentinel () to detect jeżeli -1 jest
                # really an error albo a valid timestamp. On AIX, tm_wday jest
                # unchanged even on success oraz so cannot be used jako a
                # sentinel.
                kontynuuj
            spróbuj:
                tt = time.localtime(t)
            wyjąwszy (OverflowError, OSError):
                dalej
            inaczej:
                self.assertEqual(time.mktime(tt), t)

    # Issue #13309: dalejing extreme values to mktime() albo localtime()
    # borks the glibc's internal timezone data.
    @unittest.skipUnless(platform.libc_ver()[0] != 'glibc',
                         "disabled because of a bug w glibc. Issue #13309")
    def test_mktime_error(self):
        # It may nie be possible to reliably make mktime zwróć error
        # on all platfom.  This will make sure that no other exception
        # than OverflowError jest podnieśd dla an extreme value.
        tt = time.gmtime(self.t)
        tzname = time.strftime('%Z', tt)
        self.assertNotEqual(tzname, 'LMT')
        spróbuj:
            time.mktime((-1, 1, 1, 0, 0, 0, -1, -1, -1))
        wyjąwszy OverflowError:
            dalej
        self.assertEqual(time.strftime('%Z', tt), tzname)

    @unittest.skipUnless(hasattr(time, 'monotonic'),
                         'need time.monotonic')
    def test_monotonic(self):
        # monotonic() should nie go backward
        times = [time.monotonic() dla n w range(100)]
        t1 = times[0]
        dla t2 w times[1:]:
            self.assertGreaterEqual(t2, t1, "times=%s" % times)
            t1 = t2

        # monotonic() includes time elapsed during a sleep
        t1 = time.monotonic()
        time.sleep(0.5)
        t2 = time.monotonic()
        dt = t2 - t1
        self.assertGreater(t2, t1)
        # Issue #20101: On some Windows machines, dt may be slightly low
        self.assertPrawda(0.45 <= dt <= 1.0, dt)

        # monotonic() jest a monotonic but non adjustable clock
        info = time.get_clock_info('monotonic')
        self.assertPrawda(info.monotonic)
        self.assertNieprawda(info.adjustable)

    def test_perf_counter(self):
        time.perf_counter()

    def test_process_time(self):
        # process_time() should nie include time spend during a sleep
        start = time.process_time()
        time.sleep(0.100)
        stop = time.process_time()
        # use 20 ms because process_time() has usually a resolution of 15 ms
        # on Windows
        self.assertLess(stop - start, 0.020)

        info = time.get_clock_info('process_time')
        self.assertPrawda(info.monotonic)
        self.assertNieprawda(info.adjustable)

    @unittest.skipUnless(hasattr(time, 'monotonic'),
                         'need time.monotonic')
    @unittest.skipUnless(hasattr(time, 'clock_settime'),
                         'need time.clock_settime')
    def test_monotonic_settime(self):
        t1 = time.monotonic()
        realtime = time.clock_gettime(time.CLOCK_REALTIME)
        # jump backward przy an offset of 1 hour
        spróbuj:
            time.clock_settime(time.CLOCK_REALTIME, realtime - 3600)
        wyjąwszy PermissionError jako err:
            self.skipTest(err)
        t2 = time.monotonic()
        time.clock_settime(time.CLOCK_REALTIME, realtime)
        # monotonic must nie be affected by system clock updates
        self.assertGreaterEqual(t2, t1)

    def test_localtime_failure(self):
        # Issue #13847: check dla localtime() failure
        invalid_time_t = Nic
        dla time_t w (-1, 2**30, 2**33, 2**60):
            spróbuj:
                time.localtime(time_t)
            wyjąwszy OverflowError:
                self.skipTest("need 64-bit time_t")
            wyjąwszy OSError:
                invalid_time_t = time_t
                przerwij
        jeżeli invalid_time_t jest Nic:
            self.skipTest("unable to find an invalid time_t value")

        self.assertRaises(OSError, time.localtime, invalid_time_t)
        self.assertRaises(OSError, time.ctime, invalid_time_t)

    def test_get_clock_info(self):
        clocks = ['clock', 'perf_counter', 'process_time', 'time']
        jeżeli hasattr(time, 'monotonic'):
            clocks.append('monotonic')

        dla name w clocks:
            info = time.get_clock_info(name)
            #self.assertIsInstance(info, dict)
            self.assertIsInstance(info.implementation, str)
            self.assertNotEqual(info.implementation, '')
            self.assertIsInstance(info.monotonic, bool)
            self.assertIsInstance(info.resolution, float)
            # 0.0 < resolution <= 1.0
            self.assertGreater(info.resolution, 0.0)
            self.assertLessEqual(info.resolution, 1.0)
            self.assertIsInstance(info.adjustable, bool)

        self.assertRaises(ValueError, time.get_clock_info, 'xxx')


klasa TestLocale(unittest.TestCase):
    def setUp(self):
        self.oldloc = locale.setlocale(locale.LC_ALL)

    def tearDown(self):
        locale.setlocale(locale.LC_ALL, self.oldloc)

    def test_bug_3061(self):
        spróbuj:
            tmp = locale.setlocale(locale.LC_ALL, "fr_FR")
        wyjąwszy locale.Error:
            self.skipTest('could nie set locale.LC_ALL to fr_FR')
        # This should nie cause an exception
        time.strftime("%B", (2009,2,1,0,0,0,0,0,0))


klasa _TestAsctimeYear:
    _format = '%d'

    def yearstr(self, y):
        zwróć time.asctime((y,) + (0,) * 8).split()[-1]

    def test_large_year(self):
        # Check that it doesn't crash dla year > 9999
        self.assertEqual(self.yearstr(12345), '12345')
        self.assertEqual(self.yearstr(123456789), '123456789')

klasa _TestStrftimeYear:

    # Issue 13305:  For years < 1000, the value jest nie always
    # padded to 4 digits across platforms.  The C standard
    # assumes year >= 1900, so it does nie specify the number
    # of digits.

    jeżeli time.strftime('%Y', (1,) + (0,) * 8) == '0001':
        _format = '%04d'
    inaczej:
        _format = '%d'

    def yearstr(self, y):
        zwróć time.strftime('%Y', (y,) + (0,) * 8)

    def test_4dyear(self):
        # Check that we can zwróć the zero padded value.
        jeżeli self._format == '%04d':
            self.test_year('%04d')
        inaczej:
            def year4d(y):
                zwróć time.strftime('%4Y', (y,) + (0,) * 8)
            self.test_year('%04d', func=year4d)

    def skip_if_not_supported(y):
        msg = "strftime() jest limited to [1; 9999] przy Visual Studio"
        # Check that it doesn't crash dla year > 9999
        spróbuj:
            time.strftime('%Y', (y,) + (0,) * 8)
        wyjąwszy ValueError:
            cond = Nieprawda
        inaczej:
            cond = Prawda
        zwróć unittest.skipUnless(cond, msg)

    @skip_if_not_supported(10000)
    def test_large_year(self):
        zwróć super().test_large_year()

    @skip_if_not_supported(0)
    def test_negative(self):
        zwróć super().test_negative()

    usuń skip_if_not_supported


klasa _Test4dYear:
    _format = '%d'

    def test_year(self, fmt=Nic, func=Nic):
        fmt = fmt albo self._format
        func = func albo self.yearstr
        self.assertEqual(func(1),    fmt % 1)
        self.assertEqual(func(68),   fmt % 68)
        self.assertEqual(func(69),   fmt % 69)
        self.assertEqual(func(99),   fmt % 99)
        self.assertEqual(func(999),  fmt % 999)
        self.assertEqual(func(9999), fmt % 9999)

    def test_large_year(self):
        self.assertEqual(self.yearstr(12345), '12345')
        self.assertEqual(self.yearstr(123456789), '123456789')
        self.assertEqual(self.yearstr(TIME_MAXYEAR), str(TIME_MAXYEAR))
        self.assertRaises(OverflowError, self.yearstr, TIME_MAXYEAR + 1)

    def test_negative(self):
        self.assertEqual(self.yearstr(-1), self._format % -1)
        self.assertEqual(self.yearstr(-1234), '-1234')
        self.assertEqual(self.yearstr(-123456), '-123456')
        self.assertEqual(self.yearstr(-123456789), str(-123456789))
        self.assertEqual(self.yearstr(-1234567890), str(-1234567890))
        self.assertEqual(self.yearstr(TIME_MINYEAR + 1900), str(TIME_MINYEAR + 1900))
        # Issue #13312: it may zwróć wrong value dla year < TIME_MINYEAR + 1900
        # Skip the value test, but check that no error jest podnieśd
        self.yearstr(TIME_MINYEAR)
        # self.assertEqual(self.yearstr(TIME_MINYEAR), str(TIME_MINYEAR))
        self.assertRaises(OverflowError, self.yearstr, TIME_MINYEAR - 1)


klasa TestAsctime4dyear(_TestAsctimeYear, _Test4dYear, unittest.TestCase):
    dalej

klasa TestStrftime4dyear(_TestStrftimeYear, _Test4dYear, unittest.TestCase):
    dalej


klasa TestPytime(unittest.TestCase):
    def setUp(self):
        self.invalid_values = (
            -(2 ** 100), 2 ** 100,
            -(2.0 ** 100.0), 2.0 ** 100.0,
        )

    @support.cpython_only
    def test_time_t(self):
        z _testcapi zaimportuj pytime_object_to_time_t
        dla obj, time_t, rnd w (
            # Round towards minus infinity (-inf)
            (0, 0, _PyTime.ROUND_FLOOR),
            (-1, -1, _PyTime.ROUND_FLOOR),
            (-1.0, -1, _PyTime.ROUND_FLOOR),
            (-1.9, -2, _PyTime.ROUND_FLOOR),
            (1.0, 1, _PyTime.ROUND_FLOOR),
            (1.9, 1, _PyTime.ROUND_FLOOR),
            # Round towards infinity (+inf)
            (0, 0, _PyTime.ROUND_CEILING),
            (-1, -1, _PyTime.ROUND_CEILING),
            (-1.0, -1, _PyTime.ROUND_CEILING),
            (-1.9, -1, _PyTime.ROUND_CEILING),
            (1.0, 1, _PyTime.ROUND_CEILING),
            (1.9, 2, _PyTime.ROUND_CEILING),
        ):
            self.assertEqual(pytime_object_to_time_t(obj, rnd), time_t)

        rnd = _PyTime.ROUND_FLOOR
        dla invalid w self.invalid_values:
            self.assertRaises(OverflowError,
                              pytime_object_to_time_t, invalid, rnd)

    @support.cpython_only
    def test_timespec(self):
        z _testcapi zaimportuj pytime_object_to_timespec
        dla obj, timespec, rnd w (
            # Round towards minus infinity (-inf)
            (0, (0, 0), _PyTime.ROUND_FLOOR),
            (-1, (-1, 0), _PyTime.ROUND_FLOOR),
            (-1.0, (-1, 0), _PyTime.ROUND_FLOOR),
            (1e-9, (0, 1), _PyTime.ROUND_FLOOR),
            (1e-10, (0, 0), _PyTime.ROUND_FLOOR),
            (-1e-9, (-1, 999999999), _PyTime.ROUND_FLOOR),
            (-1e-10, (-1, 999999999), _PyTime.ROUND_FLOOR),
            (-1.2, (-2, 800000000), _PyTime.ROUND_FLOOR),
            (0.9999999999, (0, 999999999), _PyTime.ROUND_FLOOR),
            (1.1234567890, (1, 123456789), _PyTime.ROUND_FLOOR),
            (1.1234567899, (1, 123456789), _PyTime.ROUND_FLOOR),
            (-1.1234567890, (-2, 876543211), _PyTime.ROUND_FLOOR),
            (-1.1234567891, (-2, 876543210), _PyTime.ROUND_FLOOR),
            # Round towards infinity (+inf)
            (0, (0, 0), _PyTime.ROUND_CEILING),
            (-1, (-1, 0), _PyTime.ROUND_CEILING),
            (-1.0, (-1, 0), _PyTime.ROUND_CEILING),
            (1e-9, (0, 1), _PyTime.ROUND_CEILING),
            (1e-10, (0, 1), _PyTime.ROUND_CEILING),
            (-1e-9, (-1, 999999999), _PyTime.ROUND_CEILING),
            (-1e-10, (0, 0), _PyTime.ROUND_CEILING),
            (-1.2, (-2, 800000000), _PyTime.ROUND_CEILING),
            (0.9999999999, (1, 0), _PyTime.ROUND_CEILING),
            (1.1234567890, (1, 123456790), _PyTime.ROUND_CEILING),
            (1.1234567899, (1, 123456790), _PyTime.ROUND_CEILING),
            (-1.1234567890, (-2, 876543211), _PyTime.ROUND_CEILING),
            (-1.1234567891, (-2, 876543211), _PyTime.ROUND_CEILING),
        ):
            przy self.subTest(obj=obj, round=rnd, timespec=timespec):
                self.assertEqual(pytime_object_to_timespec(obj, rnd), timespec)

        rnd = _PyTime.ROUND_FLOOR
        dla invalid w self.invalid_values:
            self.assertRaises(OverflowError,
                              pytime_object_to_timespec, invalid, rnd)

    @unittest.skipUnless(time._STRUCT_TM_ITEMS == 11, "needs tm_zone support")
    def test_localtime_timezone(self):

        # Get the localtime oraz examine it dla the offset oraz zone.
        lt = time.localtime()
        self.assertPrawda(hasattr(lt, "tm_gmtoff"))
        self.assertPrawda(hasattr(lt, "tm_zone"))

        # See jeżeli the offset oraz zone are similar to the module
        # attributes.
        jeżeli lt.tm_gmtoff jest Nic:
            self.assertPrawda(nie hasattr(time, "timezone"))
        inaczej:
            self.assertEqual(lt.tm_gmtoff, -[time.timezone, time.altzone][lt.tm_isdst])
        jeżeli lt.tm_zone jest Nic:
            self.assertPrawda(nie hasattr(time, "tzname"))
        inaczej:
            self.assertEqual(lt.tm_zone, time.tzname[lt.tm_isdst])

        # Try oraz make UNIX times z the localtime oraz a 9-tuple
        # created z the localtime. Test to see that the times are
        # the same.
        t = time.mktime(lt); t9 = time.mktime(lt[:9])
        self.assertEqual(t, t9)

        # Make localtimes z the UNIX times oraz compare them to
        # the original localtime, thus making a round trip.
        new_lt = time.localtime(t); new_lt9 = time.localtime(t9)
        self.assertEqual(new_lt, lt)
        self.assertEqual(new_lt.tm_gmtoff, lt.tm_gmtoff)
        self.assertEqual(new_lt.tm_zone, lt.tm_zone)
        self.assertEqual(new_lt9, lt)
        self.assertEqual(new_lt.tm_gmtoff, lt.tm_gmtoff)
        self.assertEqual(new_lt9.tm_zone, lt.tm_zone)

    @unittest.skipUnless(time._STRUCT_TM_ITEMS == 11, "needs tm_zone support")
    def test_strptime_timezone(self):
        t = time.strptime("UTC", "%Z")
        self.assertEqual(t.tm_zone, 'UTC')
        t = time.strptime("+0500", "%z")
        self.assertEqual(t.tm_gmtoff, 5 * 3600)

    @unittest.skipUnless(time._STRUCT_TM_ITEMS == 11, "needs tm_zone support")
    def test_short_times(self):

        zaimportuj pickle

        # Load a short time structure using pickle.
        st = b"ctime\nstruct_time\np0\n((I2007\nI8\nI11\nI1\nI24\nI49\nI5\nI223\nI1\ntp1\n(dp2\ntp3\nRp4\n."
        lt = pickle.loads(st)
        self.assertIs(lt.tm_gmtoff, Nic)
        self.assertIs(lt.tm_zone, Nic)


@unittest.skipUnless(_testcapi jest nie Nic,
                     'need the _testcapi module')
klasa TestPyTime_t(unittest.TestCase):
    def test_FromSeconds(self):
        z _testcapi zaimportuj PyTime_FromSeconds
        dla seconds w (0, 3, -456, _testcapi.INT_MAX, _testcapi.INT_MIN):
            przy self.subTest(seconds=seconds):
                self.assertEqual(PyTime_FromSeconds(seconds),
                                 seconds * SEC_TO_NS)

    def test_FromSecondsObject(self):
        z _testcapi zaimportuj PyTime_FromSecondsObject

        # Conversion giving the same result dla all rounding methods
        dla rnd w ALL_ROUNDING_METHODS:
            dla obj, ts w (
                # integers
                (0, 0),
                (1, SEC_TO_NS),
                (-3, -3 * SEC_TO_NS),

                # float: subseconds
                (0.0, 0),
                (1e-9, 1),
                (1e-6, 10 ** 3),
                (1e-3, 10 ** 6),

                # float: seconds
                (2.0, 2 * SEC_TO_NS),
                (123.0, 123 * SEC_TO_NS),
                (-7.0, -7 * SEC_TO_NS),

                # nanosecond are kept dla value <= 2^23 seconds
                (2**22 - 1e-9,  4194303999999999),
                (2**22,         4194304000000000),
                (2**22 + 1e-9,  4194304000000001),
                (2**23 - 1e-9,  8388607999999999),
                (2**23,         8388608000000000),

                # start loosing precision dla value > 2^23 seconds
                (2**23 + 1e-9,  8388608000000002),

                # nanoseconds are lost dla value > 2^23 seconds
                (2**24 - 1e-9, 16777215999999998),
                (2**24,        16777216000000000),
                (2**24 + 1e-9, 16777216000000000),
                (2**25 - 1e-9, 33554432000000000),
                (2**25       , 33554432000000000),
                (2**25 + 1e-9, 33554432000000000),

                # close to 2^63 nanoseconds (_PyTime_t limit)
                (9223372036, 9223372036 * SEC_TO_NS),
                (9223372036.0, 9223372036 * SEC_TO_NS),
                (-9223372036, -9223372036 * SEC_TO_NS),
                (-9223372036.0, -9223372036 * SEC_TO_NS),
            ):
                przy self.subTest(obj=obj, round=rnd, timestamp=ts):
                    self.assertEqual(PyTime_FromSecondsObject(obj, rnd), ts)

            przy self.subTest(round=rnd):
                przy self.assertRaises(OverflowError):
                    PyTime_FromSecondsObject(9223372037, rnd)
                    PyTime_FromSecondsObject(9223372037.0, rnd)
                    PyTime_FromSecondsObject(-9223372037, rnd)
                    PyTime_FromSecondsObject(-9223372037.0, rnd)

        # Conversion giving different results depending on the rounding method
        FLOOR = _PyTime.ROUND_FLOOR
        CEILING = _PyTime.ROUND_CEILING
        dla obj, ts, rnd w (
            # close to zero
            ( 1e-10,  0, FLOOR),
            ( 1e-10,  1, CEILING),
            (-1e-10, -1, FLOOR),
            (-1e-10,  0, CEILING),

            # test rounding of the last nanosecond
            ( 1.1234567899,  1123456789, FLOOR),
            ( 1.1234567899,  1123456790, CEILING),
            (-1.1234567899, -1123456790, FLOOR),
            (-1.1234567899, -1123456789, CEILING),

            # close to 1 second
            ( 0.9999999999,   999999999, FLOOR),
            ( 0.9999999999,  1000000000, CEILING),
            (-0.9999999999, -1000000000, FLOOR),
            (-0.9999999999,  -999999999, CEILING),
        ):
            przy self.subTest(obj=obj, round=rnd, timestamp=ts):
                self.assertEqual(PyTime_FromSecondsObject(obj, rnd), ts)

    def test_AsSecondsDouble(self):
        z _testcapi zaimportuj PyTime_AsSecondsDouble

        dla nanoseconds, seconds w (
            # near 1 nanosecond
            ( 0,  0.0),
            ( 1,  1e-9),
            (-1, -1e-9),

            # near 1 second
            (SEC_TO_NS + 1, 1.0 + 1e-9),
            (SEC_TO_NS,     1.0),
            (SEC_TO_NS - 1, 1.0 - 1e-9),

            # a few seconds
            (123 * SEC_TO_NS, 123.0),
            (-567 * SEC_TO_NS, -567.0),

            # nanosecond are kept dla value <= 2^23 seconds
            (4194303999999999, 2**22 - 1e-9),
            (4194304000000000, 2**22),
            (4194304000000001, 2**22 + 1e-9),

            # start loosing precision dla value > 2^23 seconds
            (8388608000000002, 2**23 + 1e-9),

            # nanoseconds are lost dla value > 2^23 seconds
            (16777215999999998, 2**24 - 1e-9),
            (16777215999999999, 2**24 - 1e-9),
            (16777216000000000, 2**24       ),
            (16777216000000001, 2**24       ),
            (16777216000000002, 2**24 + 2e-9),

            (33554432000000000, 2**25       ),
            (33554432000000002, 2**25       ),
            (33554432000000004, 2**25 + 4e-9),

            # close to 2^63 nanoseconds (_PyTime_t limit)
            (9223372036 * SEC_TO_NS, 9223372036.0),
            (-9223372036 * SEC_TO_NS, -9223372036.0),
        ):
            przy self.subTest(nanoseconds=nanoseconds, seconds=seconds):
                self.assertEqual(PyTime_AsSecondsDouble(nanoseconds),
                                 seconds)

    def test_timeval(self):
        z _testcapi zaimportuj PyTime_AsTimeval
        dla rnd w ALL_ROUNDING_METHODS:
            dla ns, tv w (
                # microseconds
                (0, (0, 0)),
                (1000, (0, 1)),
                (-1000, (-1, 999999)),

                # seconds
                (2 * SEC_TO_NS, (2, 0)),
                (-3 * SEC_TO_NS, (-3, 0)),
            ):
                przy self.subTest(nanoseconds=ns, timeval=tv, round=rnd):
                    self.assertEqual(PyTime_AsTimeval(ns, rnd), tv)

        FLOOR = _PyTime.ROUND_FLOOR
        CEILING = _PyTime.ROUND_CEILING
        dla ns, tv, rnd w (
            # nanoseconds
            (1, (0, 0), FLOOR),
            (1, (0, 1), CEILING),
            (-1, (-1, 999999), FLOOR),
            (-1, (0, 0), CEILING),

            # seconds + nanoseconds
            (1234567001, (1, 234567), FLOOR),
            (1234567001, (1, 234568), CEILING),
            (-1234567001, (-2, 765432), FLOOR),
            (-1234567001, (-2, 765433), CEILING),
        ):
            przy self.subTest(nanoseconds=ns, timeval=tv, round=rnd):
                self.assertEqual(PyTime_AsTimeval(ns, rnd), tv)

    @unittest.skipUnless(hasattr(_testcapi, 'PyTime_AsTimespec'),
                         'need _testcapi.PyTime_AsTimespec')
    def test_timespec(self):
        z _testcapi zaimportuj PyTime_AsTimespec
        dla ns, ts w (
            # nanoseconds
            (0, (0, 0)),
            (1, (0, 1)),
            (-1, (-1, 999999999)),

            # seconds
            (2 * SEC_TO_NS, (2, 0)),
            (-3 * SEC_TO_NS, (-3, 0)),

            # seconds + nanoseconds
            (1234567890, (1, 234567890)),
            (-1234567890, (-2, 765432110)),
        ):
            przy self.subTest(nanoseconds=ns, timespec=ts):
                self.assertEqual(PyTime_AsTimespec(ns), ts)

    def test_milliseconds(self):
        z _testcapi zaimportuj PyTime_AsMilliseconds
        dla rnd w ALL_ROUNDING_METHODS:
            dla ns, tv w (
                # milliseconds
                (1 * MS_TO_NS, 1),
                (-2 * MS_TO_NS, -2),

                # seconds
                (2 * SEC_TO_NS, 2000),
                (-3 * SEC_TO_NS, -3000),
            ):
                przy self.subTest(nanoseconds=ns, timeval=tv, round=rnd):
                    self.assertEqual(PyTime_AsMilliseconds(ns, rnd), tv)

        FLOOR = _PyTime.ROUND_FLOOR
        CEILING = _PyTime.ROUND_CEILING
        dla ns, ms, rnd w (
            # nanoseconds
            (1, 0, FLOOR),
            (1, 1, CEILING),
            (-1, 0, FLOOR),
            (-1, -1, CEILING),

            # seconds + nanoseconds
            (1234 * MS_TO_NS + 1, 1234, FLOOR),
            (1234 * MS_TO_NS + 1, 1235, CEILING),
            (-1234 * MS_TO_NS - 1, -1234, FLOOR),
            (-1234 * MS_TO_NS - 1, -1235, CEILING),
        ):
            przy self.subTest(nanoseconds=ns, milliseconds=ms, round=rnd):
                self.assertEqual(PyTime_AsMilliseconds(ns, rnd), ms)

    def test_microseconds(self):
        z _testcapi zaimportuj PyTime_AsMicroseconds
        dla rnd w ALL_ROUNDING_METHODS:
            dla ns, tv w (
                # microseconds
                (1 * US_TO_NS, 1),
                (-2 * US_TO_NS, -2),

                # milliseconds
                (1 * MS_TO_NS, 1000),
                (-2 * MS_TO_NS, -2000),

                # seconds
                (2 * SEC_TO_NS, 2000000),
                (-3 * SEC_TO_NS, -3000000),
            ):
                przy self.subTest(nanoseconds=ns, timeval=tv, round=rnd):
                    self.assertEqual(PyTime_AsMicroseconds(ns, rnd), tv)

        FLOOR = _PyTime.ROUND_FLOOR
        CEILING = _PyTime.ROUND_CEILING
        dla ns, ms, rnd w (
            # nanoseconds
            (1, 0, FLOOR),
            (1, 1, CEILING),
            (-1, 0, FLOOR),
            (-1, -1, CEILING),

            # seconds + nanoseconds
            (1234 * US_TO_NS + 1, 1234, FLOOR),
            (1234 * US_TO_NS + 1, 1235, CEILING),
            (-1234 * US_TO_NS - 1, -1234, FLOOR),
            (-1234 * US_TO_NS - 1, -1235, CEILING),
        ):
            przy self.subTest(nanoseconds=ns, milliseconds=ms, round=rnd):
                self.assertEqual(PyTime_AsMicroseconds(ns, rnd), ms)


jeżeli __name__ == "__main__":
    unittest.main()
