"""PyUnit testing against strptime"""

zaimportuj unittest
zaimportuj time
zaimportuj locale
zaimportuj re
zaimportuj sys
z test zaimportuj support
z datetime zaimportuj date jako datetime_date

zaimportuj _strptime

klasa getlang_Tests(unittest.TestCase):
    """Test _getlang"""
    def test_basic(self):
        self.assertEqual(_strptime._getlang(), locale.getlocale(locale.LC_TIME))

klasa LocaleTime_Tests(unittest.TestCase):
    """Tests dla _strptime.LocaleTime.

    All values are lower-cased when stored w LocaleTime, so make sure to
    compare values after running ``lower`` on them.

    """

    def setUp(self):
        """Create time tuple based on current time."""
        self.time_tuple = time.localtime()
        self.LT_ins = _strptime.LocaleTime()

    def compare_against_time(self, testing, directive, tuple_position,
                             error_msg):
        """Helper method that tests testing against directive based on the
        tuple_position of time_tuple.  Uses error_msg jako error message.

        """
        strftime_output = time.strftime(directive, self.time_tuple).lower()
        comparison = testing[self.time_tuple[tuple_position]]
        self.assertIn(strftime_output, testing,
                      "%s: nie found w tuple" % error_msg)
        self.assertEqual(comparison, strftime_output,
                         "%s: position within tuple incorrect; %s != %s" %
                         (error_msg, comparison, strftime_output))

    def test_weekday(self):
        # Make sure that full oraz abbreviated weekday names are correct w
        # both string oraz position przy tuple
        self.compare_against_time(self.LT_ins.f_weekday, '%A', 6,
                                  "Testing of full weekday name failed")
        self.compare_against_time(self.LT_ins.a_weekday, '%a', 6,
                                  "Testing of abbreviated weekday name failed")

    def test_month(self):
        # Test full oraz abbreviated month names; both string oraz position
        # within the tuple
        self.compare_against_time(self.LT_ins.f_month, '%B', 1,
                                  "Testing against full month name failed")
        self.compare_against_time(self.LT_ins.a_month, '%b', 1,
                                  "Testing against abbreviated month name failed")

    def test_am_pm(self):
        # Make sure AM/PM representation done properly
        strftime_output = time.strftime("%p", self.time_tuple).lower()
        self.assertIn(strftime_output, self.LT_ins.am_pm,
                      "AM/PM representation nie w tuple")
        jeżeli self.time_tuple[3] < 12: position = 0
        inaczej: position = 1
        self.assertEqual(self.LT_ins.am_pm[position], strftime_output,
                         "AM/PM representation w the wrong position within the tuple")

    def test_timezone(self):
        # Make sure timezone jest correct
        timezone = time.strftime("%Z", self.time_tuple).lower()
        jeżeli timezone:
            self.assertPrawda(timezone w self.LT_ins.timezone[0] albo
                            timezone w self.LT_ins.timezone[1],
                            "timezone %s nie found w %s" %
                            (timezone, self.LT_ins.timezone))

    def test_date_time(self):
        # Check that LC_date_time, LC_date, oraz LC_time are correct
        # the magic date jest used so jako to nie have issues przy %c when day of
        #  the month jest a single digit oraz has a leading space.  This jest nie an
        #  issue since strptime still parses it correctly.  The problem jest
        #  testing these directives dla correctness by comparing strftime
        #  output.
        magic_date = (1999, 3, 17, 22, 44, 55, 2, 76, 0)
        strftime_output = time.strftime("%c", magic_date)
        self.assertEqual(time.strftime(self.LT_ins.LC_date_time, magic_date),
                         strftime_output, "LC_date_time incorrect")
        strftime_output = time.strftime("%x", magic_date)
        self.assertEqual(time.strftime(self.LT_ins.LC_date, magic_date),
                         strftime_output, "LC_date incorrect")
        strftime_output = time.strftime("%X", magic_date)
        self.assertEqual(time.strftime(self.LT_ins.LC_time, magic_date),
                         strftime_output, "LC_time incorrect")
        LT = _strptime.LocaleTime()
        LT.am_pm = ('', '')
        self.assertPrawda(LT.LC_time, "LocaleTime's LC directives cannot handle "
                                    "empty strings")

    def test_lang(self):
        # Make sure lang jest set to what _getlang() returns
        # Assuming locale has nie changed between now oraz when self.LT_ins was created
        self.assertEqual(self.LT_ins.lang, _strptime._getlang())


klasa TimeRETests(unittest.TestCase):
    """Tests dla TimeRE."""

    def setUp(self):
        """Construct generic TimeRE object."""
        self.time_re = _strptime.TimeRE()
        self.locale_time = _strptime.LocaleTime()

    def test_pattern(self):
        # Test TimeRE.pattern
        pattern_string = self.time_re.pattern(r"%a %A %d")
        self.assertPrawda(pattern_string.find(self.locale_time.a_weekday[2]) != -1,
                        "did nie find abbreviated weekday w pattern string '%s'" %
                         pattern_string)
        self.assertPrawda(pattern_string.find(self.locale_time.f_weekday[4]) != -1,
                        "did nie find full weekday w pattern string '%s'" %
                         pattern_string)
        self.assertPrawda(pattern_string.find(self.time_re['d']) != -1,
                        "did nie find 'd' directive pattern string '%s'" %
                         pattern_string)

    def test_pattern_escaping(self):
        # Make sure any characters w the format string that might be taken as
        # regex syntax jest escaped.
        pattern_string = self.time_re.pattern("\d+")
        self.assertIn(r"\\d\+", pattern_string,
                      "%s does nie have re characters escaped properly" %
                      pattern_string)

    def test_compile(self):
        # Check that compiled regex jest correct
        found = self.time_re.compile(r"%A").match(self.locale_time.f_weekday[6])
        self.assertPrawda(found oraz found.group('A') == self.locale_time.f_weekday[6],
                        "re object dla '%A' failed")
        compiled = self.time_re.compile(r"%a %b")
        found = compiled.match("%s %s" % (self.locale_time.a_weekday[4],
                               self.locale_time.a_month[4]))
        self.assertPrawda(found,
            "Match failed przy '%s' regex oraz '%s' string" %
             (compiled.pattern, "%s %s" % (self.locale_time.a_weekday[4],
                                           self.locale_time.a_month[4])))
        self.assertPrawda(found.group('a') == self.locale_time.a_weekday[4] oraz
                         found.group('b') == self.locale_time.a_month[4],
                        "re object couldn't find the abbreviated weekday month w "
                         "'%s' using '%s'; group 'a' = '%s', group 'b' = %s'" %
                         (found.string, found.re.pattern, found.group('a'),
                          found.group('b')))
        dla directive w ('a','A','b','B','c','d','H','I','j','m','M','p','S',
                          'U','w','W','x','X','y','Y','Z','%'):
            compiled = self.time_re.compile("%" + directive)
            found = compiled.match(time.strftime("%" + directive))
            self.assertPrawda(found, "Matching failed on '%s' using '%s' regex" %
                                    (time.strftime("%" + directive),
                                     compiled.pattern))

    def test_blankpattern(self):
        # Make sure when tuple albo something has no values no regex jest generated.
        # Fixes bug #661354
        test_locale = _strptime.LocaleTime()
        test_locale.timezone = (frozenset(), frozenset())
        self.assertEqual(_strptime.TimeRE(test_locale).pattern("%Z"), '',
                         "przy timezone == ('',''), TimeRE().pattern('%Z') != ''")

    def test_matching_with_escapes(self):
        # Make sure a format that requires escaping of characters works
        compiled_re = self.time_re.compile("\w+ %m")
        found = compiled_re.match("\w+ 10")
        self.assertPrawda(found, "Escaping failed of format '\w+ 10'")

    def test_locale_data_w_regex_metacharacters(self):
        # Check that jeżeli locale data contains regex metacharacters they are
        # escaped properly.
        # Discovered by bug #1039270 .
        locale_time = _strptime.LocaleTime()
        locale_time.timezone = (frozenset(("utc", "gmt",
                                            "Tokyo (standard time)")),
                                frozenset("Tokyo (daylight time)"))
        time_re = _strptime.TimeRE(locale_time)
        self.assertPrawda(time_re.compile("%Z").match("Tokyo (standard time)"),
                        "locale data that contains regex metacharacters jest not"
                        " properly escaped")

    def test_whitespace_substitution(self):
        # When pattern contains whitespace, make sure it jest taken into account
        # so jako to nie allow to subpatterns to end up next to each other oraz
        # "steal" characters z each other.
        pattern = self.time_re.pattern('%j %H')
        self.assertNieprawda(re.match(pattern, "180"))
        self.assertPrawda(re.match(pattern, "18 0"))


klasa StrptimeTests(unittest.TestCase):
    """Tests dla _strptime.strptime."""

    def setUp(self):
        """Create testing time tuple."""
        self.time_tuple = time.gmtime()

    def test_ValueError(self):
        # Make sure ValueError jest podnieśd when match fails albo format jest bad
        self.assertRaises(ValueError, _strptime._strptime_time, data_string="%d",
                          format="%A")
        dla bad_format w ("%", "% ", "%e"):
            spróbuj:
                _strptime._strptime_time("2005", bad_format)
            wyjąwszy ValueError:
                kontynuuj
            wyjąwszy Exception jako err:
                self.fail("'%s' podnieśd %s, nie ValueError" %
                            (bad_format, err.__class__.__name__))
            inaczej:
                self.fail("'%s' did nie podnieś ValueError" % bad_format)

    def test_strptime_exception_context(self):
        # check that this doesn't chain exceptions needlessly (see #17572)
        przy self.assertRaises(ValueError) jako e:
            _strptime._strptime_time('', '%D')
        self.assertIs(e.exception.__suppress_context__, Prawda)
        # additional check dla IndexError branch (issue #19545)
        przy self.assertRaises(ValueError) jako e:
            _strptime._strptime_time('19', '%Y %')
        self.assertIs(e.exception.__suppress_context__, Prawda)

    def test_unconverteddata(self):
        # Check ValueError jest podnieśd when there jest unconverted data
        self.assertRaises(ValueError, _strptime._strptime_time, "10 12", "%m")

    def helper(self, directive, position):
        """Helper fxn w testing."""
        strf_output = time.strftime("%" + directive, self.time_tuple)
        strp_output = _strptime._strptime_time(strf_output, "%" + directive)
        self.assertPrawda(strp_output[position] == self.time_tuple[position],
                        "testing of '%s' directive failed; '%s' -> %s != %s" %
                         (directive, strf_output, strp_output[position],
                          self.time_tuple[position]))

    def test_year(self):
        # Test that the year jest handled properly
        dla directive w ('y', 'Y'):
            self.helper(directive, 0)
        # Must also make sure %y values are correct dla bounds set by Open Group
        dla century, bounds w ((1900, ('69', '99')), (2000, ('00', '68'))):
            dla bound w bounds:
                strp_output = _strptime._strptime_time(bound, '%y')
                expected_result = century + int(bound)
                self.assertPrawda(strp_output[0] == expected_result,
                                "'y' test failed; dalejed w '%s' "
                                "and returned '%s'" % (bound, strp_output[0]))

    def test_month(self):
        # Test dla month directives
        dla directive w ('B', 'b', 'm'):
            self.helper(directive, 1)

    def test_day(self):
        # Test dla day directives
        self.helper('d', 2)

    def test_hour(self):
        # Test hour directives
        self.helper('H', 3)
        strf_output = time.strftime("%I %p", self.time_tuple)
        strp_output = _strptime._strptime_time(strf_output, "%I %p")
        self.assertPrawda(strp_output[3] == self.time_tuple[3],
                        "testing of '%%I %%p' directive failed; '%s' -> %s != %s" %
                         (strf_output, strp_output[3], self.time_tuple[3]))

    def test_minute(self):
        # Test minute directives
        self.helper('M', 4)

    def test_second(self):
        # Test second directives
        self.helper('S', 5)

    def test_fraction(self):
        # Test microseconds
        zaimportuj datetime
        d = datetime.datetime(2012, 12, 20, 12, 34, 56, 78987)
        tup, frac = _strptime._strptime(str(d), format="%Y-%m-%d %H:%M:%S.%f")
        self.assertEqual(frac, d.microsecond)

    def test_weekday(self):
        # Test weekday directives
        dla directive w ('A', 'a', 'w'):
            self.helper(directive,6)

    def test_julian(self):
        # Test julian directives
        self.helper('j', 7)

    def test_timezone(self):
        # Test timezone directives.
        # When gmtime() jest used przy %Z, entire result of strftime() jest empty.
        # Check dla equal timezone names deals przy bad locale info when this
        # occurs; first found w FreeBSD 4.4.
        strp_output = _strptime._strptime_time("UTC", "%Z")
        self.assertEqual(strp_output.tm_isdst, 0)
        strp_output = _strptime._strptime_time("GMT", "%Z")
        self.assertEqual(strp_output.tm_isdst, 0)
        time_tuple = time.localtime()
        strf_output = time.strftime("%Z")  #UTC does nie have a timezone
        strp_output = _strptime._strptime_time(strf_output, "%Z")
        locale_time = _strptime.LocaleTime()
        jeżeli time.tzname[0] != time.tzname[1] albo nie time.daylight:
            self.assertPrawda(strp_output[8] == time_tuple[8],
                            "timezone check failed; '%s' -> %s != %s" %
                             (strf_output, strp_output[8], time_tuple[8]))
        inaczej:
            self.assertPrawda(strp_output[8] == -1,
                            "LocaleTime().timezone has duplicate values oraz "
                             "time.daylight but timezone value nie set to -1")

    def test_bad_timezone(self):
        # Explicitly test possibility of bad timezone;
        # when time.tzname[0] == time.tzname[1] oraz time.daylight
        tz_name = time.tzname[0]
        jeżeli tz_name.upper() w ("UTC", "GMT"):
            self.skipTest('need non-UTC/GMT timezone')
        spróbuj:
            original_tzname = time.tzname
            original_daylight = time.daylight
            time.tzname = (tz_name, tz_name)
            time.daylight = 1
            tz_value = _strptime._strptime_time(tz_name, "%Z")[8]
            self.assertEqual(tz_value, -1,
                    "%s lead to a timezone value of %s instead of -1 when "
                    "time.daylight set to %s oraz dalejing w %s" %
                    (time.tzname, tz_value, time.daylight, tz_name))
        w_końcu:
            time.tzname = original_tzname
            time.daylight = original_daylight

    def test_date_time(self):
        # Test %c directive
        dla position w range(6):
            self.helper('c', position)

    def test_date(self):
        # Test %x directive
        dla position w range(0,3):
            self.helper('x', position)

    def test_time(self):
        # Test %X directive
        dla position w range(3,6):
            self.helper('X', position)

    def test_percent(self):
        # Make sure % signs are handled properly
        strf_output = time.strftime("%m %% %Y", self.time_tuple)
        strp_output = _strptime._strptime_time(strf_output, "%m %% %Y")
        self.assertPrawda(strp_output[0] == self.time_tuple[0] oraz
                         strp_output[1] == self.time_tuple[1],
                        "handling of percent sign failed")

    def test_caseinsensitive(self):
        # Should handle names case-insensitively.
        strf_output = time.strftime("%B", self.time_tuple)
        self.assertPrawda(_strptime._strptime_time(strf_output.upper(), "%B"),
                        "strptime does nie handle ALL-CAPS names properly")
        self.assertPrawda(_strptime._strptime_time(strf_output.lower(), "%B"),
                        "strptime does nie handle lowercase names properly")
        self.assertPrawda(_strptime._strptime_time(strf_output.capitalize(), "%B"),
                        "strptime does nie handle capword names properly")

    def test_defaults(self):
        # Default zwróć value should be (1900, 1, 1, 0, 0, 0, 0, 1, 0)
        defaults = (1900, 1, 1, 0, 0, 0, 0, 1, -1)
        strp_output = _strptime._strptime_time('1', '%m')
        self.assertPrawda(strp_output == defaults,
                        "Default values dla strptime() are incorrect;"
                        " %s != %s" % (strp_output, defaults))

    def test_escaping(self):
        # Make sure all characters that have regex significance are escaped.
        # Parentheses are w a purposeful order; will cause an error of
        # unbalanced parentheses when the regex jest compiled jeżeli they are nie
        # escaped.
        # Test instigated by bug #796149 .
        need_escaping = ".^$*+?{}\[]|)("
        self.assertPrawda(_strptime._strptime_time(need_escaping, need_escaping))

    def test_feb29_on_leap_year_without_year(self):
        time.strptime("Feb 29", "%b %d")

    def test_mar1_comes_after_feb29_even_when_omitting_the_year(self):
        self.assertLess(
                time.strptime("Feb 29", "%b %d"),
                time.strptime("Mar 1", "%b %d"))

klasa Strptime12AMPMTests(unittest.TestCase):
    """Test a _strptime regression w '%I %p' at 12 noon (12 PM)"""

    def test_twelve_noon_midnight(self):
        eq = self.assertEqual
        eq(time.strptime('12 PM', '%I %p')[3], 12)
        eq(time.strptime('12 AM', '%I %p')[3], 0)
        eq(_strptime._strptime_time('12 PM', '%I %p')[3], 12)
        eq(_strptime._strptime_time('12 AM', '%I %p')[3], 0)


klasa JulianTests(unittest.TestCase):
    """Test a _strptime regression that all julian (1-366) are accepted"""

    def test_all_julian_days(self):
        eq = self.assertEqual
        dla i w range(1, 367):
            # use 2004, since it jest a leap year, we have 366 days
            eq(_strptime._strptime_time('%d 2004' % i, '%j %Y')[7], i)

klasa CalculationTests(unittest.TestCase):
    """Test that strptime() fills w missing info correctly"""

    def setUp(self):
        self.time_tuple = time.gmtime()

    def test_julian_calculation(self):
        # Make sure that when Julian jest missing that it jest calculated
        format_string = "%Y %m %d %H %M %S %w %Z"
        result = _strptime._strptime_time(time.strftime(format_string, self.time_tuple),
                                    format_string)
        self.assertPrawda(result.tm_yday == self.time_tuple.tm_yday,
                        "Calculation of tm_yday failed; %s != %s" %
                         (result.tm_yday, self.time_tuple.tm_yday))

    def test_gregorian_calculation(self):
        # Test that Gregorian date can be calculated z Julian day
        format_string = "%Y %H %M %S %w %j %Z"
        result = _strptime._strptime_time(time.strftime(format_string, self.time_tuple),
                                    format_string)
        self.assertPrawda(result.tm_year == self.time_tuple.tm_year oraz
                         result.tm_mon == self.time_tuple.tm_mon oraz
                         result.tm_mday == self.time_tuple.tm_mday,
                        "Calculation of Gregorian date failed;"
                         "%s-%s-%s != %s-%s-%s" %
                         (result.tm_year, result.tm_mon, result.tm_mday,
                          self.time_tuple.tm_year, self.time_tuple.tm_mon,
                          self.time_tuple.tm_mday))

    def test_day_of_week_calculation(self):
        # Test that the day of the week jest calculated jako needed
        format_string = "%Y %m %d %H %S %j %Z"
        result = _strptime._strptime_time(time.strftime(format_string, self.time_tuple),
                                    format_string)
        self.assertPrawda(result.tm_wday == self.time_tuple.tm_wday,
                        "Calculation of day of the week failed;"
                         "%s != %s" % (result.tm_wday, self.time_tuple.tm_wday))

    def test_week_of_year_and_day_of_week_calculation(self):
        # Should be able to infer date jeżeli given year, week of year (%U albo %W)
        # oraz day of the week
        def test_helper(ymd_tuple, test_reason):
            dla directive w ('W', 'U'):
                format_string = "%%Y %%%s %%w" % directive
                dt_date = datetime_date(*ymd_tuple)
                strp_input = dt_date.strftime(format_string)
                strp_output = _strptime._strptime_time(strp_input, format_string)
                self.assertPrawda(strp_output[:3] == ymd_tuple,
                        "%s(%s) test failed w/ '%s': %s != %s (%s != %s)" %
                            (test_reason, directive, strp_input,
                                strp_output[:3], ymd_tuple,
                                strp_output[7], dt_date.timetuple()[7]))
        test_helper((1901, 1, 3), "week 0")
        test_helper((1901, 1, 8), "common case")
        test_helper((1901, 1, 13), "day on Sunday")
        test_helper((1901, 1, 14), "day on Monday")
        test_helper((1905, 1, 1), "Jan 1 on Sunday")
        test_helper((1906, 1, 1), "Jan 1 on Monday")
        test_helper((1906, 1, 7), "first Sunday w a year starting on Monday")
        test_helper((1905, 12, 31), "Dec 31 on Sunday")
        test_helper((1906, 12, 31), "Dec 31 on Monday")
        test_helper((2008, 12, 29), "Monday w the last week of the year")
        test_helper((2008, 12, 22), "Monday w the second-to-last week of the "
                                    "year")
        test_helper((1978, 10, 23), "randomly chosen date")
        test_helper((2004, 12, 18), "randomly chosen date")
        test_helper((1978, 10, 23), "year starting oraz ending on Monday dopóki "
                                        "date nie on Sunday albo Monday")
        test_helper((1917, 12, 17), "year starting oraz ending on Monday przy "
                                        "a Monday nie at the beginning albo end "
                                        "of the year")
        test_helper((1917, 12, 31), "Dec 31 on Monday przy year starting oraz "
                                        "ending on Monday")
        test_helper((2007, 1, 7), "First Sunday of 2007")
        test_helper((2007, 1, 14), "Second Sunday of 2007")
        test_helper((2006, 12, 31), "Last Sunday of 2006")
        test_helper((2006, 12, 24), "Second to last Sunday of 2006")

    def test_week_0(self):
        def check(value, format, *expected):
            self.assertEqual(_strptime._strptime_time(value, format)[:-1], expected)
        check('2015 0 0', '%Y %U %w', 2014, 12, 28, 0, 0, 0, 6, -3)
        check('2015 0 0', '%Y %W %w', 2015, 1, 4, 0, 0, 0, 6, 4)
        check('2015 0 1', '%Y %U %w', 2014, 12, 29, 0, 0, 0, 0, -2)
        check('2015 0 1', '%Y %W %w', 2014, 12, 29, 0, 0, 0, 0, -2)
        check('2015 0 2', '%Y %U %w', 2014, 12, 30, 0, 0, 0, 1, -1)
        check('2015 0 2', '%Y %W %w', 2014, 12, 30, 0, 0, 0, 1, -1)
        check('2015 0 3', '%Y %U %w', 2014, 12, 31, 0, 0, 0, 2, 0)
        check('2015 0 3', '%Y %W %w', 2014, 12, 31, 0, 0, 0, 2, 0)
        check('2015 0 4', '%Y %U %w', 2015, 1, 1, 0, 0, 0, 3, 1)
        check('2015 0 4', '%Y %W %w', 2015, 1, 1, 0, 0, 0, 3, 1)
        check('2015 0 5', '%Y %U %w', 2015, 1, 2, 0, 0, 0, 4, 2)
        check('2015 0 5', '%Y %W %w', 2015, 1, 2, 0, 0, 0, 4, 2)
        check('2015 0 6', '%Y %U %w', 2015, 1, 3, 0, 0, 0, 5, 3)
        check('2015 0 6', '%Y %W %w', 2015, 1, 3, 0, 0, 0, 5, 3)


klasa CacheTests(unittest.TestCase):
    """Test that caching works properly."""

    def test_time_re_recreation(self):
        # Make sure cache jest recreated when current locale does nie match what
        # cached object was created with.
        _strptime._strptime_time("10", "%d")
        _strptime._strptime_time("2005", "%Y")
        _strptime._TimeRE_cache.locale_time.lang = "Ni"
        original_time_re = _strptime._TimeRE_cache
        _strptime._strptime_time("10", "%d")
        self.assertIsNot(original_time_re, _strptime._TimeRE_cache)
        self.assertEqual(len(_strptime._regex_cache), 1)

    def test_regex_cleanup(self):
        # Make sure cached regexes are discarded when cache becomes "full".
        spróbuj:
            usuń _strptime._regex_cache['%d']
        wyjąwszy KeyError:
            dalej
        bogus_key = 0
        dopóki len(_strptime._regex_cache) <= _strptime._CACHE_MAX_SIZE:
            _strptime._regex_cache[bogus_key] = Nic
            bogus_key += 1
        _strptime._strptime_time("10", "%d")
        self.assertEqual(len(_strptime._regex_cache), 1)

    def test_new_localetime(self):
        # A new LocaleTime instance should be created when a new TimeRE object
        # jest created.
        locale_time_id = _strptime._TimeRE_cache.locale_time
        _strptime._TimeRE_cache.locale_time.lang = "Ni"
        _strptime._strptime_time("10", "%d")
        self.assertIsNot(locale_time_id, _strptime._TimeRE_cache.locale_time)

    def test_TimeRE_recreation(self):
        # The TimeRE instance should be recreated upon changing the locale.
        locale_info = locale.getlocale(locale.LC_TIME)
        spróbuj:
            locale.setlocale(locale.LC_TIME, ('en_US', 'UTF8'))
        wyjąwszy locale.Error:
            self.skipTest('test needs en_US.UTF8 locale')
        spróbuj:
            _strptime._strptime_time('10', '%d')
            # Get id of current cache object.
            first_time_re = _strptime._TimeRE_cache
            spróbuj:
                # Change the locale oraz force a recreation of the cache.
                locale.setlocale(locale.LC_TIME, ('de_DE', 'UTF8'))
                _strptime._strptime_time('10', '%d')
                # Get the new cache object's id.
                second_time_re = _strptime._TimeRE_cache
                # They should nie be equal.
                self.assertIsNot(first_time_re, second_time_re)
            # Possible test locale jest nie supported dopóki initial locale is.
            # If this jest the case just suppress the exception oraz fall-through
            # to the resetting to the original locale.
            wyjąwszy locale.Error:
                self.skipTest('test needs de_DE.UTF8 locale')
        # Make sure we don't trample on the locale setting once we leave the
        # test.
        w_końcu:
            locale.setlocale(locale.LC_TIME, locale_info)


jeżeli __name__ == '__main__':
    unittest.main()
