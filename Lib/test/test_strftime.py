"""
Unittest dla time.strftime
"""

zaimportuj calendar
zaimportuj sys
zaimportuj re
z test zaimportuj support
zaimportuj time
zaimportuj unittest


# helper functions
def fixasctime(s):
    jeżeli s[8] == ' ':
        s = s[:8] + '0' + s[9:]
    zwróć s

def escapestr(text, ampm):
    """
    Escape text to deal przy possible locale values that have regex
    syntax dopóki allowing regex syntax used dla comparison.
    """
    new_text = re.escape(text)
    new_text = new_text.replace(re.escape(ampm), ampm)
    new_text = new_text.replace('\%', '%')
    new_text = new_text.replace('\:', ':')
    new_text = new_text.replace('\?', '?')
    zwróć new_text


klasa StrftimeTest(unittest.TestCase):

    def _update_variables(self, now):
        # we must update the local variables on every cycle
        self.gmt = time.gmtime(now)
        now = time.localtime(now)

        jeżeli now[3] < 12: self.ampm='(AM|am)'
        inaczej: self.ampm='(PM|pm)'

        self.jan1 = time.localtime(time.mktime((now[0], 1, 1, 0, 0, 0, 0, 1, 0)))

        spróbuj:
            jeżeli now[8]: self.tz = time.tzname[1]
            inaczej: self.tz = time.tzname[0]
        wyjąwszy AttributeError:
            self.tz = ''

        jeżeli now[3] > 12: self.clock12 = now[3] - 12
        albo_inaczej now[3] > 0: self.clock12 = now[3]
        inaczej: self.clock12 = 12

        self.now = now

    def setUp(self):
        spróbuj:
            zaimportuj java
            java.util.Locale.setDefault(java.util.Locale.US)
        wyjąwszy ImportError:
            zaimportuj locale
            locale.setlocale(locale.LC_TIME, 'C')

    def test_strftime(self):
        now = time.time()
        self._update_variables(now)
        self.strftest1(now)
        self.strftest2(now)

        jeżeli support.verbose:
            print("Strftime test, platform: %s, Python version: %s" % \
                  (sys.platform, sys.version.split()[0]))

        dla j w range(-5, 5):
            dla i w range(25):
                arg = now + (i+j*100)*23*3603
                self._update_variables(arg)
                self.strftest1(arg)
                self.strftest2(arg)

    def strftest1(self, now):
        jeżeli support.verbose:
            print("strftime test for", time.ctime(now))
        now = self.now
        # Make sure any characters that could be taken jako regex syntax jest
        # escaped w escapestr()
        expectations = (
            ('%a', calendar.day_abbr[now[6]], 'abbreviated weekday name'),
            ('%A', calendar.day_name[now[6]], 'full weekday name'),
            ('%b', calendar.month_abbr[now[1]], 'abbreviated month name'),
            ('%B', calendar.month_name[now[1]], 'full month name'),
            # %c see below
            ('%d', '%02d' % now[2], 'day of month jako number (00-31)'),
            ('%H', '%02d' % now[3], 'hour (00-23)'),
            ('%I', '%02d' % self.clock12, 'hour (01-12)'),
            ('%j', '%03d' % now[7], 'julian day (001-366)'),
            ('%m', '%02d' % now[1], 'month jako number (01-12)'),
            ('%M', '%02d' % now[4], 'minute, (00-59)'),
            ('%p', self.ampm, 'AM albo PM jako appropriate'),
            ('%S', '%02d' % now[5], 'seconds of current time (00-60)'),
            ('%U', '%02d' % ((now[7] + self.jan1[6])//7),
             'week number of the year (Sun 1st)'),
            ('%w', '0?%d' % ((1+now[6]) % 7), 'weekday jako a number (Sun 1st)'),
            ('%W', '%02d' % ((now[7] + (self.jan1[6] - 1)%7)//7),
            'week number of the year (Mon 1st)'),
            # %x see below
            ('%X', '%02d:%02d:%02d' % (now[3], now[4], now[5]), '%H:%M:%S'),
            ('%y', '%02d' % (now[0]%100), 'year without century'),
            ('%Y', '%d' % now[0], 'year przy century'),
            # %Z see below
            ('%%', '%', 'single percent sign'),
        )

        dla e w expectations:
            # musn't podnieś a value error
            spróbuj:
                result = time.strftime(e[0], now)
            wyjąwszy ValueError jako error:
                self.fail("strftime '%s' format gave error: %s" % (e[0], error))
            jeżeli re.match(escapestr(e[1], self.ampm), result):
                kontynuuj
            jeżeli nie result albo result[0] == '%':
                self.fail("strftime does nie support standard '%s' format (%s)"
                          % (e[0], e[2]))
            inaczej:
                self.fail("Conflict dla %s (%s): expected %s, but got %s"
                          % (e[0], e[2], e[1], result))

    def strftest2(self, now):
        nowsecs = str(int(now))[:-1]
        now = self.now

        nonstandard_expectations = (
        # These are standard but don't have predictable output
            ('%c', fixasctime(time.asctime(now)), 'near-asctime() format'),
            ('%x', '%02d/%02d/%02d' % (now[1], now[2], (now[0]%100)),
            '%m/%d/%y %H:%M:%S'),
            ('%Z', '%s' % self.tz, 'time zone name'),

            # These are some platform specific extensions
            ('%D', '%02d/%02d/%02d' % (now[1], now[2], (now[0]%100)), 'mm/dd/yy'),
            ('%e', '%2d' % now[2], 'day of month jako number, blank padded ( 0-31)'),
            ('%h', calendar.month_abbr[now[1]], 'abbreviated month name'),
            ('%k', '%2d' % now[3], 'hour, blank padded ( 0-23)'),
            ('%n', '\n', 'newline character'),
            ('%r', '%02d:%02d:%02d %s' % (self.clock12, now[4], now[5], self.ampm),
            '%I:%M:%S %p'),
            ('%R', '%02d:%02d' % (now[3], now[4]), '%H:%M'),
            ('%s', nowsecs, 'seconds since the Epoch w UCT'),
            ('%t', '\t', 'tab character'),
            ('%T', '%02d:%02d:%02d' % (now[3], now[4], now[5]), '%H:%M:%S'),
            ('%3y', '%03d' % (now[0]%100),
            'year without century rendered using fieldwidth'),
        )


        dla e w nonstandard_expectations:
            spróbuj:
                result = time.strftime(e[0], now)
            wyjąwszy ValueError jako result:
                msg = "Error dla nonstandard '%s' format (%s): %s" % \
                      (e[0], e[2], str(result))
                jeżeli support.verbose:
                    print(msg)
                kontynuuj
            jeżeli re.match(escapestr(e[1], self.ampm), result):
                jeżeli support.verbose:
                    print("Supports nonstandard '%s' format (%s)" % (e[0], e[2]))
            albo_inaczej nie result albo result[0] == '%':
                jeżeli support.verbose:
                    print("Does nie appear to support '%s' format (%s)" % \
                           (e[0], e[2]))
            inaczej:
                jeżeli support.verbose:
                    print("Conflict dla nonstandard '%s' format (%s):" % \
                           (e[0], e[2]))
                    print("  Expected %s, but got %s" % (e[1], result))


klasa Y1900Tests(unittest.TestCase):
    """A limitation of the MS C runtime library jest that it crashes if
    a date before 1900 jest dalejed przy a format string containing "%y"
    """

    def test_y_before_1900(self):
        # Issue #13674, #19634
        t = (1899, 1, 1, 0, 0, 0, 0, 0, 0)
        jeżeli (sys.platform == "win32"
        albo sys.platform.startswith(("aix", "sunos", "solaris"))):
            przy self.assertRaises(ValueError):
                time.strftime("%y", t)
        inaczej:
            self.assertEqual(time.strftime("%y", t), "99")

    def test_y_1900(self):
        self.assertEqual(
            time.strftime("%y", (1900, 1, 1, 0, 0, 0, 0, 0, 0)), "00")

    def test_y_after_1900(self):
        self.assertEqual(
            time.strftime("%y", (2013, 1, 1, 0, 0, 0, 0, 0, 0)), "13")

jeżeli __name__ == '__main__':
    unittest.main()
