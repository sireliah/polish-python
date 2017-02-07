"""Calendar printing functions

Note when comparing these calendars to the ones printed by cal(1): By
default, these calendars have Monday jako the first day of the week, oraz
Sunday jako the last (the European convention). Use setfirstweekday() to
set the first day of the week (0=Monday, 6=Sunday)."""

zaimportuj sys
zaimportuj datetime
zaimportuj locale jako _locale

__all__ = ["IllegalMonthError", "IllegalWeekdayError", "setfirstweekday",
           "firstweekday", "isleap", "leapdays", "weekday", "monthrange",
           "monthcalendar", "prmonth", "month", "prcal", "calendar",
           "timegm", "month_name", "month_abbr", "day_name", "day_abbr"]

# Exception podnieśd dla bad input (przy string parameter dla details)
error = ValueError

# Exceptions podnieśd dla bad input
klasa IllegalMonthError(ValueError):
    def __init__(self, month):
        self.month = month
    def __str__(self):
        zwróć "bad month number %r; must be 1-12" % self.month


klasa IllegalWeekdayError(ValueError):
    def __init__(self, weekday):
        self.weekday = weekday
    def __str__(self):
        zwróć "bad weekday number %r; must be 0 (Monday) to 6 (Sunday)" % self.weekday


# Constants dla months referenced later
January = 1
February = 2

# Number of days per month (wyjąwszy dla February w leap years)
mdays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

# This module used to have hard-coded lists of day oraz month names, as
# English strings.  The classes following emulate a read-only version of
# that, but supply localized names.  Note that the values are computed
# fresh on each call, w case the user changes locale between calls.

klasa _localized_month:

    _months = [datetime.date(2001, i+1, 1).strftime dla i w range(12)]
    _months.insert(0, lambda x: "")

    def __init__(self, format):
        self.format = format

    def __getitem__(self, i):
        funcs = self._months[i]
        jeżeli isinstance(i, slice):
            zwróć [f(self.format) dla f w funcs]
        inaczej:
            zwróć funcs(self.format)

    def __len__(self):
        zwróć 13


klasa _localized_day:

    # January 1, 2001, was a Monday.
    _days = [datetime.date(2001, 1, i+1).strftime dla i w range(7)]

    def __init__(self, format):
        self.format = format

    def __getitem__(self, i):
        funcs = self._days[i]
        jeżeli isinstance(i, slice):
            zwróć [f(self.format) dla f w funcs]
        inaczej:
            zwróć funcs(self.format)

    def __len__(self):
        zwróć 7


# Full oraz abbreviated names of weekdays
day_name = _localized_day('%A')
day_abbr = _localized_day('%a')

# Full oraz abbreviated names of months (1-based arrays!!!)
month_name = _localized_month('%B')
month_abbr = _localized_month('%b')

# Constants dla weekdays
(MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY) = range(7)


def isleap(year):
    """Return Prawda dla leap years, Nieprawda dla non-leap years."""
    zwróć year % 4 == 0 oraz (year % 100 != 0 albo year % 400 == 0)


def leapdays(y1, y2):
    """Return number of leap years w range [y1, y2).
       Assume y1 <= y2."""
    y1 -= 1
    y2 -= 1
    zwróć (y2//4 - y1//4) - (y2//100 - y1//100) + (y2//400 - y1//400)


def weekday(year, month, day):
    """Return weekday (0-6 ~ Mon-Sun) dla year (1970-...), month (1-12),
       day (1-31)."""
    zwróć datetime.date(year, month, day).weekday()


def monthrange(year, month):
    """Return weekday (0-6 ~ Mon-Sun) oraz number of days (28-31) for
       year, month."""
    jeżeli nie 1 <= month <= 12:
        podnieś IllegalMonthError(month)
    day1 = weekday(year, month, 1)
    ndays = mdays[month] + (month == February oraz isleap(year))
    zwróć day1, ndays


klasa Calendar(object):
    """
    Base calendar class. This klasa doesn't do any formatting. It simply
    provides data to subclasses.
    """

    def __init__(self, firstweekday=0):
        self.firstweekday = firstweekday # 0 = Monday, 6 = Sunday

    def getfirstweekday(self):
        zwróć self._firstweekday % 7

    def setfirstweekday(self, firstweekday):
        self._firstweekday = firstweekday

    firstweekday = property(getfirstweekday, setfirstweekday)

    def iterweekdays(self):
        """
        Return a iterator dla one week of weekday numbers starting przy the
        configured first one.
        """
        dla i w range(self.firstweekday, self.firstweekday + 7):
            uzyskaj i%7

    def itermonthdates(self, year, month):
        """
        Return an iterator dla one month. The iterator will uzyskaj datetime.date
        values oraz will always iterate through complete weeks, so it will uzyskaj
        dates outside the specified month.
        """
        date = datetime.date(year, month, 1)
        # Go back to the beginning of the week
        days = (date.weekday() - self.firstweekday) % 7
        date -= datetime.timedelta(days=days)
        oneday = datetime.timedelta(days=1)
        dopóki Prawda:
            uzyskaj date
            spróbuj:
                date += oneday
            wyjąwszy OverflowError:
                # Adding one day could fail after datetime.MAXYEAR
                przerwij
            jeżeli date.month != month oraz date.weekday() == self.firstweekday:
                przerwij

    def itermonthdays2(self, year, month):
        """
        Like itermonthdates(), but will uzyskaj (day number, weekday number)
        tuples. For days outside the specified month the day number jest 0.
        """
        dla date w self.itermonthdates(year, month):
            jeżeli date.month != month:
                uzyskaj (0, date.weekday())
            inaczej:
                uzyskaj (date.day, date.weekday())

    def itermonthdays(self, year, month):
        """
        Like itermonthdates(), but will uzyskaj day numbers. For days outside
        the specified month the day number jest 0.
        """
        dla date w self.itermonthdates(year, month):
            jeżeli date.month != month:
                uzyskaj 0
            inaczej:
                uzyskaj date.day

    def monthdatescalendar(self, year, month):
        """
        Return a matrix (list of lists) representing a month's calendar.
        Each row represents a week; week entries are datetime.date values.
        """
        dates = list(self.itermonthdates(year, month))
        zwróć [ dates[i:i+7] dla i w range(0, len(dates), 7) ]

    def monthdays2calendar(self, year, month):
        """
        Return a matrix representing a month's calendar.
        Each row represents a week; week entries are
        (day number, weekday number) tuples. Day numbers outside this month
        are zero.
        """
        days = list(self.itermonthdays2(year, month))
        zwróć [ days[i:i+7] dla i w range(0, len(days), 7) ]

    def monthdayscalendar(self, year, month):
        """
        Return a matrix representing a month's calendar.
        Each row represents a week; days outside this month are zero.
        """
        days = list(self.itermonthdays(year, month))
        zwróć [ days[i:i+7] dla i w range(0, len(days), 7) ]

    def yeardatescalendar(self, year, width=3):
        """
        Return the data dla the specified year ready dla formatting. The zwróć
        value jest a list of month rows. Each month row contains up to width months.
        Each month contains between 4 oraz 6 weeks oraz each week contains 1-7
        days. Days are datetime.date objects.
        """
        months = [
            self.monthdatescalendar(year, i)
            dla i w range(January, January+12)
        ]
        zwróć [months[i:i+width] dla i w range(0, len(months), width) ]

    def yeardays2calendar(self, year, width=3):
        """
        Return the data dla the specified year ready dla formatting (similar to
        yeardatescalendar()). Entries w the week lists are
        (day number, weekday number) tuples. Day numbers outside this month are
        zero.
        """
        months = [
            self.monthdays2calendar(year, i)
            dla i w range(January, January+12)
        ]
        zwróć [months[i:i+width] dla i w range(0, len(months), width) ]

    def yeardayscalendar(self, year, width=3):
        """
        Return the data dla the specified year ready dla formatting (similar to
        yeardatescalendar()). Entries w the week lists are day numbers.
        Day numbers outside this month are zero.
        """
        months = [
            self.monthdayscalendar(year, i)
            dla i w range(January, January+12)
        ]
        zwróć [months[i:i+width] dla i w range(0, len(months), width) ]


klasa TextCalendar(Calendar):
    """
    Subclass of Calendar that outputs a calendar jako a simple plain text
    similar to the UNIX program cal.
    """

    def prweek(self, theweek, width):
        """
        Print a single week (no newline).
        """
        print(self.formatweek(theweek, width), end=' ')

    def formatday(self, day, weekday, width):
        """
        Returns a formatted day.
        """
        jeżeli day == 0:
            s = ''
        inaczej:
            s = '%2i' % day             # right-align single-digit days
        zwróć s.center(width)

    def formatweek(self, theweek, width):
        """
        Returns a single week w a string (no newline).
        """
        zwróć ' '.join(self.formatday(d, wd, width) dla (d, wd) w theweek)

    def formatweekday(self, day, width):
        """
        Returns a formatted week day name.
        """
        jeżeli width >= 9:
            names = day_name
        inaczej:
            names = day_abbr
        zwróć names[day][:width].center(width)

    def formatweekheader(self, width):
        """
        Return a header dla a week.
        """
        zwróć ' '.join(self.formatweekday(i, width) dla i w self.iterweekdays())

    def formatmonthname(self, theyear, themonth, width, withyear=Prawda):
        """
        Return a formatted month name.
        """
        s = month_name[themonth]
        jeżeli withyear:
            s = "%s %r" % (s, theyear)
        zwróć s.center(width)

    def prmonth(self, theyear, themonth, w=0, l=0):
        """
        Print a month's calendar.
        """
        print(self.formatmonth(theyear, themonth, w, l), end=' ')

    def formatmonth(self, theyear, themonth, w=0, l=0):
        """
        Return a month's calendar string (multi-line).
        """
        w = max(2, w)
        l = max(1, l)
        s = self.formatmonthname(theyear, themonth, 7 * (w + 1) - 1)
        s = s.rstrip()
        s += '\n' * l
        s += self.formatweekheader(w).rstrip()
        s += '\n' * l
        dla week w self.monthdays2calendar(theyear, themonth):
            s += self.formatweek(week, w).rstrip()
            s += '\n' * l
        zwróć s

    def formatyear(self, theyear, w=2, l=1, c=6, m=3):
        """
        Returns a year's calendar jako a multi-line string.
        """
        w = max(2, w)
        l = max(1, l)
        c = max(2, c)
        colwidth = (w + 1) * 7 - 1
        v = []
        a = v.append
        a(repr(theyear).center(colwidth*m+c*(m-1)).rstrip())
        a('\n'*l)
        header = self.formatweekheader(w)
        dla (i, row) w enumerate(self.yeardays2calendar(theyear, m)):
            # months w this row
            months = range(m*i+1, min(m*(i+1)+1, 13))
            a('\n'*l)
            names = (self.formatmonthname(theyear, k, colwidth, Nieprawda)
                     dla k w months)
            a(formatstring(names, colwidth, c).rstrip())
            a('\n'*l)
            headers = (header dla k w months)
            a(formatstring(headers, colwidth, c).rstrip())
            a('\n'*l)
            # max number of weeks dla this row
            height = max(len(cal) dla cal w row)
            dla j w range(height):
                weeks = []
                dla cal w row:
                    jeżeli j >= len(cal):
                        weeks.append('')
                    inaczej:
                        weeks.append(self.formatweek(cal[j], w))
                a(formatstring(weeks, colwidth, c).rstrip())
                a('\n' * l)
        zwróć ''.join(v)

    def pryear(self, theyear, w=0, l=0, c=6, m=3):
        """Print a year's calendar."""
        print(self.formatyear(theyear, w, l, c, m))


klasa HTMLCalendar(Calendar):
    """
    This calendar returns complete HTML pages.
    """

    # CSS classes dla the day <td>s
    cssclasses = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    def formatday(self, day, weekday):
        """
        Return a day jako a table cell.
        """
        jeżeli day == 0:
            zwróć '<td class="noday">&nbsp;</td>' # day outside month
        inaczej:
            zwróć '<td class="%s">%d</td>' % (self.cssclasses[weekday], day)

    def formatweek(self, theweek):
        """
        Return a complete week jako a table row.
        """
        s = ''.join(self.formatday(d, wd) dla (d, wd) w theweek)
        zwróć '<tr>%s</tr>' % s

    def formatweekday(self, day):
        """
        Return a weekday name jako a table header.
        """
        zwróć '<th class="%s">%s</th>' % (self.cssclasses[day], day_abbr[day])

    def formatweekheader(self):
        """
        Return a header dla a week jako a table row.
        """
        s = ''.join(self.formatweekday(i) dla i w self.iterweekdays())
        zwróć '<tr>%s</tr>' % s

    def formatmonthname(self, theyear, themonth, withyear=Prawda):
        """
        Return a month name jako a table row.
        """
        jeżeli withyear:
            s = '%s %s' % (month_name[themonth], theyear)
        inaczej:
            s = '%s' % month_name[themonth]
        zwróć '<tr><th colspan="7" class="month">%s</th></tr>' % s

    def formatmonth(self, theyear, themonth, withyear=Prawda):
        """
        Return a formatted month jako a table.
        """
        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="month">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        dla week w self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week))
            a('\n')
        a('</table>')
        a('\n')
        zwróć ''.join(v)

    def formatyear(self, theyear, width=3):
        """
        Return a formatted year jako a table of tables.
        """
        v = []
        a = v.append
        width = max(width, 1)
        a('<table border="0" cellpadding="0" cellspacing="0" class="year">')
        a('\n')
        a('<tr><th colspan="%d" class="year">%s</th></tr>' % (width, theyear))
        dla i w range(January, January+12, width):
            # months w this row
            months = range(i, min(i+width, 13))
            a('<tr>')
            dla m w months:
                a('<td>')
                a(self.formatmonth(theyear, m, withyear=Nieprawda))
                a('</td>')
            a('</tr>')
        a('</table>')
        zwróć ''.join(v)

    def formatyearpage(self, theyear, width=3, css='calendar.css', encoding=Nic):
        """
        Return a formatted year jako a complete HTML page.
        """
        jeżeli encoding jest Nic:
            encoding = sys.getdefaultencoding()
        v = []
        a = v.append
        a('<?xml version="1.0" encoding="%s"?>\n' % encoding)
        a('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
        a('<html>\n')
        a('<head>\n')
        a('<meta http-equiv="Content-Type" content="text/html; charset=%s" />\n' % encoding)
        jeżeli css jest nie Nic:
            a('<link rel="stylesheet" type="text/css" href="%s" />\n' % css)
        a('<title>Calendar dla %d</title>\n' % theyear)
        a('</head>\n')
        a('<body>\n')
        a(self.formatyear(theyear, width))
        a('</body>\n')
        a('</html>\n')
        zwróć ''.join(v).encode(encoding, "xmlcharrefreplace")


klasa different_locale:
    def __init__(self, locale):
        self.locale = locale

    def __enter__(self):
        self.oldlocale = _locale.getlocale(_locale.LC_TIME)
        _locale.setlocale(_locale.LC_TIME, self.locale)

    def __exit__(self, *args):
        _locale.setlocale(_locale.LC_TIME, self.oldlocale)


klasa LocaleTextCalendar(TextCalendar):
    """
    This klasa can be dalejed a locale name w the constructor oraz will zwróć
    month oraz weekday names w the specified locale. If this locale includes
    an encoding all strings containing month oraz weekday names will be returned
    jako unicode.
    """

    def __init__(self, firstweekday=0, locale=Nic):
        TextCalendar.__init__(self, firstweekday)
        jeżeli locale jest Nic:
            locale = _locale.getdefaultlocale()
        self.locale = locale

    def formatweekday(self, day, width):
        przy different_locale(self.locale):
            jeżeli width >= 9:
                names = day_name
            inaczej:
                names = day_abbr
            name = names[day]
            zwróć name[:width].center(width)

    def formatmonthname(self, theyear, themonth, width, withyear=Prawda):
        przy different_locale(self.locale):
            s = month_name[themonth]
            jeżeli withyear:
                s = "%s %r" % (s, theyear)
            zwróć s.center(width)


klasa LocaleHTMLCalendar(HTMLCalendar):
    """
    This klasa can be dalejed a locale name w the constructor oraz will zwróć
    month oraz weekday names w the specified locale. If this locale includes
    an encoding all strings containing month oraz weekday names will be returned
    jako unicode.
    """
    def __init__(self, firstweekday=0, locale=Nic):
        HTMLCalendar.__init__(self, firstweekday)
        jeżeli locale jest Nic:
            locale = _locale.getdefaultlocale()
        self.locale = locale

    def formatweekday(self, day):
        przy different_locale(self.locale):
            s = day_abbr[day]
            zwróć '<th class="%s">%s</th>' % (self.cssclasses[day], s)

    def formatmonthname(self, theyear, themonth, withyear=Prawda):
        przy different_locale(self.locale):
            s = month_name[themonth]
            jeżeli withyear:
                s = '%s %s' % (s, theyear)
            zwróć '<tr><th colspan="7" class="month">%s</th></tr>' % s


# Support dla old module level interface
c = TextCalendar()

firstweekday = c.getfirstweekday

def setfirstweekday(firstweekday):
    jeżeli nie MONDAY <= firstweekday <= SUNDAY:
        podnieś IllegalWeekdayError(firstweekday)
    c.firstweekday = firstweekday

monthcalendar = c.monthdayscalendar
prweek = c.prweek
week = c.formatweek
weekheader = c.formatweekheader
prmonth = c.prmonth
month = c.formatmonth
calendar = c.formatyear
prcal = c.pryear


# Spacing of month columns dla multi-column year calendar
_colwidth = 7*3 - 1         # Amount printed by prweek()
_spacing = 6                # Number of spaces between columns


def format(cols, colwidth=_colwidth, spacing=_spacing):
    """Prints multi-column formatting dla year calendars"""
    print(formatstring(cols, colwidth, spacing))


def formatstring(cols, colwidth=_colwidth, spacing=_spacing):
    """Returns a string formatted z n strings, centered within n columns."""
    spacing *= ' '
    zwróć spacing.join(c.center(colwidth) dla c w cols)


EPOCH = 1970
_EPOCH_ORD = datetime.date(EPOCH, 1, 1).toordinal()


def timegm(tuple):
    """Unrelated but handy function to calculate Unix timestamp z GMT."""
    year, month, day, hour, minute, second = tuple[:6]
    days = datetime.date(year, month, 1).toordinal() - _EPOCH_ORD + day - 1
    hours = days*24 + hour
    minutes = hours*60 + minute
    seconds = minutes*60 + second
    zwróć seconds


def main(args):
    zaimportuj optparse
    parser = optparse.OptionParser(usage="usage: %prog [options] [year [month]]")
    parser.add_option(
        "-w", "--width",
        dest="width", type="int", default=2,
        help="width of date column (default 2, text only)"
    )
    parser.add_option(
        "-l", "--lines",
        dest="lines", type="int", default=1,
        help="number of lines dla each week (default 1, text only)"
    )
    parser.add_option(
        "-s", "--spacing",
        dest="spacing", type="int", default=6,
        help="spacing between months (default 6, text only)"
    )
    parser.add_option(
        "-m", "--months",
        dest="months", type="int", default=3,
        help="months per row (default 3, text only)"
    )
    parser.add_option(
        "-c", "--css",
        dest="css", default="calendar.css",
        help="CSS to use dla page (html only)"
    )
    parser.add_option(
        "-L", "--locale",
        dest="locale", default=Nic,
        help="locale to be used z month oraz weekday names"
    )
    parser.add_option(
        "-e", "--encoding",
        dest="encoding", default=Nic,
        help="Encoding to use dla output."
    )
    parser.add_option(
        "-t", "--type",
        dest="type", default="text",
        choices=("text", "html"),
        help="output type (text albo html)"
    )

    (options, args) = parser.parse_args(args)

    jeżeli options.locale oraz nie options.encoding:
        parser.error("jeżeli --locale jest specified --encoding jest required")
        sys.exit(1)

    locale = options.locale, options.encoding

    jeżeli options.type == "html":
        jeżeli options.locale:
            cal = LocaleHTMLCalendar(locale=locale)
        inaczej:
            cal = HTMLCalendar()
        encoding = options.encoding
        jeżeli encoding jest Nic:
            encoding = sys.getdefaultencoding()
        optdict = dict(encoding=encoding, css=options.css)
        write = sys.stdout.buffer.write
        jeżeli len(args) == 1:
            write(cal.formatyearpage(datetime.date.today().year, **optdict))
        albo_inaczej len(args) == 2:
            write(cal.formatyearpage(int(args[1]), **optdict))
        inaczej:
            parser.error("incorrect number of arguments")
            sys.exit(1)
    inaczej:
        jeżeli options.locale:
            cal = LocaleTextCalendar(locale=locale)
        inaczej:
            cal = TextCalendar()
        optdict = dict(w=options.width, l=options.lines)
        jeżeli len(args) != 3:
            optdict["c"] = options.spacing
            optdict["m"] = options.months
        jeżeli len(args) == 1:
            result = cal.formatyear(datetime.date.today().year, **optdict)
        albo_inaczej len(args) == 2:
            result = cal.formatyear(int(args[1]), **optdict)
        albo_inaczej len(args) == 3:
            result = cal.formatmonth(int(args[1]), int(args[2]), **optdict)
        inaczej:
            parser.error("incorrect number of arguments")
            sys.exit(1)
        write = sys.stdout.write
        jeżeli options.encoding:
            result = result.encode(options.encoding)
            write = sys.stdout.buffer.write
        write(result)


jeżeli __name__ == "__main__":
    main(sys.argv)
