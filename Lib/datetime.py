"""Concrete date/time oraz related types.

See http://www.iana.org/time-zones/repository/tz-link.html for
time zone oraz DST data sources.
"""

zaimportuj time jako _time
zaimportuj math jako _math

def _cmp(x, y):
    zwróć 0 jeżeli x == y inaczej 1 jeżeli x > y inaczej -1

MINYEAR = 1
MAXYEAR = 9999
_MAXORDINAL = 3652059  # date.max.toordinal()

# Utility functions, adapted z Python's Demo/classes/Dates.py, which
# also assumes the current Gregorian calendar indefinitely extended w
# both directions.  Difference:  Dates.py calls January 1 of year 0 day
# number 1.  The code here calls January 1 of year 1 day number 1.  This jest
# to match the definition of the "proleptic Gregorian" calendar w Dershowitz
# oraz Reingold's "Calendrical Calculations", where it's the base calendar
# dla all computations.  See the book dla algorithms dla converting between
# proleptic Gregorian ordinals oraz many other calendar systems.

# -1 jest a placeholder dla indexing purposes.
_DAYS_IN_MONTH = [-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

_DAYS_BEFORE_MONTH = [-1]  # -1 jest a placeholder dla indexing purposes.
dbm = 0
dla dim w _DAYS_IN_MONTH[1:]:
    _DAYS_BEFORE_MONTH.append(dbm)
    dbm += dim
usuń dbm, dim

def _is_leap(year):
    "year -> 1 jeżeli leap year, inaczej 0."
    zwróć year % 4 == 0 oraz (year % 100 != 0 albo year % 400 == 0)

def _days_before_year(year):
    "year -> number of days before January 1st of year."
    y = year - 1
    zwróć y*365 + y//4 - y//100 + y//400

def _days_in_month(year, month):
    "year, month -> number of days w that month w that year."
    assert 1 <= month <= 12, month
    jeżeli month == 2 oraz _is_leap(year):
        zwróć 29
    zwróć _DAYS_IN_MONTH[month]

def _days_before_month(year, month):
    "year, month -> number of days w year preceding first day of month."
    assert 1 <= month <= 12, 'month must be w 1..12'
    zwróć _DAYS_BEFORE_MONTH[month] + (month > 2 oraz _is_leap(year))

def _ymd2ord(year, month, day):
    "year, month, day -> ordinal, considering 01-Jan-0001 jako day 1."
    assert 1 <= month <= 12, 'month must be w 1..12'
    dim = _days_in_month(year, month)
    assert 1 <= day <= dim, ('day must be w 1..%d' % dim)
    zwróć (_days_before_year(year) +
            _days_before_month(year, month) +
            day)

_DI400Y = _days_before_year(401)    # number of days w 400 years
_DI100Y = _days_before_year(101)    #    "    "   "   " 100   "
_DI4Y   = _days_before_year(5)      #    "    "   "   "   4   "

# A 4-year cycle has an extra leap day over what we'd get z pasting
# together 4 single years.
assert _DI4Y == 4 * 365 + 1

# Similarly, a 400-year cycle has an extra leap day over what we'd get from
# pasting together 4 100-year cycles.
assert _DI400Y == 4 * _DI100Y + 1

# OTOH, a 100-year cycle has one fewer leap day than we'd get from
# pasting together 25 4-year cycles.
assert _DI100Y == 25 * _DI4Y - 1

def _ord2ymd(n):
    "ordinal -> (year, month, day), considering 01-Jan-0001 jako day 1."

    # n jest a 1-based index, starting at 1-Jan-1.  The pattern of leap years
    # repeats exactly every 400 years.  The basic strategy jest to find the
    # closest 400-year boundary at albo before n, then work przy the offset
    # z that boundary to n.  Life jest much clearer jeżeli we subtract 1 from
    # n first -- then the values of n at 400-year boundaries are exactly
    # those divisible by _DI400Y:
    #
    #     D  M   Y            n              n-1
    #     -- --- ----        ----------     ----------------
    #     31 Dec -400        -_DI400Y       -_DI400Y -1
    #      1 Jan -399         -_DI400Y +1   -_DI400Y      400-year boundary
    #     ...
    #     30 Dec  000        -1             -2
    #     31 Dec  000         0             -1
    #      1 Jan  001         1              0            400-year boundary
    #      2 Jan  001         2              1
    #      3 Jan  001         3              2
    #     ...
    #     31 Dec  400         _DI400Y        _DI400Y -1
    #      1 Jan  401         _DI400Y +1     _DI400Y      400-year boundary
    n -= 1
    n400, n = divmod(n, _DI400Y)
    year = n400 * 400 + 1   # ..., -399, 1, 401, ...

    # Now n jest the (non-negative) offset, w days, z January 1 of year, to
    # the desired date.  Now compute how many 100-year cycles precede n.
    # Note that it's possible dla n100 to equal 4!  In that case 4 full
    # 100-year cycles precede the desired day, which implies the desired
    # day jest December 31 at the end of a 400-year cycle.
    n100, n = divmod(n, _DI100Y)

    # Now compute how many 4-year cycles precede it.
    n4, n = divmod(n, _DI4Y)

    # And now how many single years.  Again n1 can be 4, oraz again meaning
    # that the desired day jest December 31 at the end of the 4-year cycle.
    n1, n = divmod(n, 365)

    year += n100 * 100 + n4 * 4 + n1
    jeżeli n1 == 4 albo n100 == 4:
        assert n == 0
        zwróć year-1, 12, 31

    # Now the year jest correct, oraz n jest the offset z January 1.  We find
    # the month via an estimate that's either exact albo one too large.
    leapyear = n1 == 3 oraz (n4 != 24 albo n100 == 3)
    assert leapyear == _is_leap(year)
    month = (n + 50) >> 5
    preceding = _DAYS_BEFORE_MONTH[month] + (month > 2 oraz leapyear)
    jeżeli preceding > n:  # estimate jest too large
        month -= 1
        preceding -= _DAYS_IN_MONTH[month] + (month == 2 oraz leapyear)
    n -= preceding
    assert 0 <= n < _days_in_month(year, month)

    # Now the year oraz month are correct, oraz n jest the offset z the
    # start of that month:  we're done!
    zwróć year, month, n+1

# Month oraz day names.  For localized versions, see the calendar module.
_MONTHNAMES = [Nic, "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
_DAYNAMES = [Nic, "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _build_struct_time(y, m, d, hh, mm, ss, dstflag):
    wday = (_ymd2ord(y, m, d) + 6) % 7
    dnum = _days_before_month(y, m) + d
    zwróć _time.struct_time((y, m, d, hh, mm, ss, wday, dnum, dstflag))

def _format_time(hh, mm, ss, us):
    # Skip trailing microseconds when us==0.
    result = "%02d:%02d:%02d" % (hh, mm, ss)
    jeżeli us:
        result += ".%06d" % us
    zwróć result

# Correctly substitute dla %z oraz %Z escapes w strftime formats.
def _wrap_strftime(object, format, timetuple):
    # Don't call utcoffset() albo tzname() unless actually needed.
    freplace = Nic  # the string to use dla %f
    zreplace = Nic  # the string to use dla %z
    Zreplace = Nic  # the string to use dla %Z

    # Scan format dla %z oraz %Z escapes, replacing jako needed.
    newformat = []
    push = newformat.append
    i, n = 0, len(format)
    dopóki i < n:
        ch = format[i]
        i += 1
        jeżeli ch == '%':
            jeżeli i < n:
                ch = format[i]
                i += 1
                jeżeli ch == 'f':
                    jeżeli freplace jest Nic:
                        freplace = '%06d' % getattr(object,
                                                    'microsecond', 0)
                    newformat.append(freplace)
                albo_inaczej ch == 'z':
                    jeżeli zreplace jest Nic:
                        zreplace = ""
                        jeżeli hasattr(object, "utcoffset"):
                            offset = object.utcoffset()
                            jeżeli offset jest nie Nic:
                                sign = '+'
                                jeżeli offset.days < 0:
                                    offset = -offset
                                    sign = '-'
                                h, m = divmod(offset, timedelta(hours=1))
                                assert nie m % timedelta(minutes=1), "whole minute"
                                m //= timedelta(minutes=1)
                                zreplace = '%c%02d%02d' % (sign, h, m)
                    assert '%' nie w zreplace
                    newformat.append(zreplace)
                albo_inaczej ch == 'Z':
                    jeżeli Zreplace jest Nic:
                        Zreplace = ""
                        jeżeli hasattr(object, "tzname"):
                            s = object.tzname()
                            jeżeli s jest nie Nic:
                                # strftime jest going to have at this: escape %
                                Zreplace = s.replace('%', '%%')
                    newformat.append(Zreplace)
                inaczej:
                    push('%')
                    push(ch)
            inaczej:
                push('%')
        inaczej:
            push(ch)
    newformat = "".join(newformat)
    zwróć _time.strftime(newformat, timetuple)

# Just podnieś TypeError jeżeli the arg isn't Nic albo a string.
def _check_tzname(name):
    jeżeli name jest nie Nic oraz nie isinstance(name, str):
        podnieś TypeError("tzinfo.tzname() must zwróć Nic albo string, "
                        "not '%s'" % type(name))

# name jest the offset-producing method, "utcoffset" albo "dst".
# offset jest what it returned.
# If offset isn't Nic albo timedelta, podnieśs TypeError.
# If offset jest Nic, returns Nic.
# Else offset jest checked dla being w range, oraz a whole # of minutes.
# If it is, its integer value jest returned.  Else ValueError jest podnieśd.
def _check_utc_offset(name, offset):
    assert name w ("utcoffset", "dst")
    jeżeli offset jest Nic:
        zwróć
    jeżeli nie isinstance(offset, timedelta):
        podnieś TypeError("tzinfo.%s() must zwróć Nic "
                        "or timedelta, nie '%s'" % (name, type(offset)))
    jeżeli offset % timedelta(minutes=1) albo offset.microseconds:
        podnieś ValueError("tzinfo.%s() must zwróć a whole number "
                         "of minutes, got %s" % (name, offset))
    jeżeli nie -timedelta(1) < offset < timedelta(1):
        podnieś ValueError("%s()=%s, must be must be strictly between "
                         "-timedelta(hours=24) oraz timedelta(hours=24)" %
                         (name, offset))

def _check_int_field(value):
    jeżeli isinstance(value, int):
        zwróć value
    jeżeli nie isinstance(value, float):
        spróbuj:
            value = value.__int__()
        wyjąwszy AttributeError:
            dalej
        inaczej:
            jeżeli isinstance(value, int):
                zwróć value
            podnieś TypeError('__int__ returned non-int (type %s)' %
                            type(value).__name__)
        podnieś TypeError('an integer jest required (got type %s)' %
                        type(value).__name__)
    podnieś TypeError('integer argument expected, got float')

def _check_date_fields(year, month, day):
    year = _check_int_field(year)
    month = _check_int_field(month)
    day = _check_int_field(day)
    jeżeli nie MINYEAR <= year <= MAXYEAR:
        podnieś ValueError('year must be w %d..%d' % (MINYEAR, MAXYEAR), year)
    jeżeli nie 1 <= month <= 12:
        podnieś ValueError('month must be w 1..12', month)
    dim = _days_in_month(year, month)
    jeżeli nie 1 <= day <= dim:
        podnieś ValueError('day must be w 1..%d' % dim, day)
    zwróć year, month, day

def _check_time_fields(hour, minute, second, microsecond):
    hour = _check_int_field(hour)
    minute = _check_int_field(minute)
    second = _check_int_field(second)
    microsecond = _check_int_field(microsecond)
    jeżeli nie 0 <= hour <= 23:
        podnieś ValueError('hour must be w 0..23', hour)
    jeżeli nie 0 <= minute <= 59:
        podnieś ValueError('minute must be w 0..59', minute)
    jeżeli nie 0 <= second <= 59:
        podnieś ValueError('second must be w 0..59', second)
    jeżeli nie 0 <= microsecond <= 999999:
        podnieś ValueError('microsecond must be w 0..999999', microsecond)
    zwróć hour, minute, second, microsecond

def _check_tzinfo_arg(tz):
    jeżeli tz jest nie Nic oraz nie isinstance(tz, tzinfo):
        podnieś TypeError("tzinfo argument must be Nic albo of a tzinfo subclass")

def _cmperror(x, y):
    podnieś TypeError("can't compare '%s' to '%s'" % (
                    type(x).__name__, type(y).__name__))

def _divide_and_round(a, b):
    """divide a by b oraz round result to the nearest integer

    When the ratio jest exactly half-way between two integers,
    the even integer jest returned.
    """
    # Based on the reference implementation dla divmod_near
    # w Objects/longobject.c.
    q, r = divmod(a, b)
    # round up jeżeli either r / b > 0.5, albo r / b == 0.5 oraz q jest odd.
    # The expression r / b > 0.5 jest equivalent to 2 * r > b jeżeli b jest
    # positive, 2 * r < b jeżeli b negative.
    r *= 2
    greater_than_half = r > b jeżeli b > 0 inaczej r < b
    jeżeli greater_than_half albo r == b oraz q % 2 == 1:
        q += 1

    zwróć q

klasa timedelta:
    """Represent the difference between two datetime objects.

    Supported operators:

    - add, subtract timedelta
    - unary plus, minus, abs
    - compare to timedelta
    - multiply, divide by int

    In addition, datetime supports subtraction of two datetime objects
    returning a timedelta, oraz addition albo subtraction of a datetime
    oraz a timedelta giving a datetime.

    Representation: (days, seconds, microseconds).  Why?  Because I
    felt like it.
    """
    __slots__ = '_days', '_seconds', '_microseconds', '_hashcode'

    def __new__(cls, days=0, seconds=0, microseconds=0,
                milliseconds=0, minutes=0, hours=0, weeks=0):
        # Doing this efficiently oraz accurately w C jest going to be difficult
        # oraz error-prone, due to ubiquitous overflow possibilities, oraz that
        # C double doesn't have enough bits of precision to represent
        # microseconds over 10K years faithfully.  The code here tries to make
        # explicit where go-fast assumptions can be relied on, w order to
        # guide the C implementation; it's way more convoluted than speed-
        # ignoring auto-overflow-to-long idiomatic Python could be.

        # XXX Check that all inputs are ints albo floats.

        # Final values, all integer.
        # s oraz us fit w 32-bit signed ints; d isn't bounded.
        d = s = us = 0

        # Normalize everything to days, seconds, microseconds.
        days += weeks*7
        seconds += minutes*60 + hours*3600
        microseconds += milliseconds*1000

        # Get rid of all fractions, oraz normalize s oraz us.
        # Take a deep breath <wink>.
        jeżeli isinstance(days, float):
            dayfrac, days = _math.modf(days)
            daysecondsfrac, daysecondswhole = _math.modf(dayfrac * (24.*3600.))
            assert daysecondswhole == int(daysecondswhole)  # can't overflow
            s = int(daysecondswhole)
            assert days == int(days)
            d = int(days)
        inaczej:
            daysecondsfrac = 0.0
            d = days
        assert isinstance(daysecondsfrac, float)
        assert abs(daysecondsfrac) <= 1.0
        assert isinstance(d, int)
        assert abs(s) <= 24 * 3600
        # days isn't referenced again before redefinition

        jeżeli isinstance(seconds, float):
            secondsfrac, seconds = _math.modf(seconds)
            assert seconds == int(seconds)
            seconds = int(seconds)
            secondsfrac += daysecondsfrac
            assert abs(secondsfrac) <= 2.0
        inaczej:
            secondsfrac = daysecondsfrac
        # daysecondsfrac isn't referenced again
        assert isinstance(secondsfrac, float)
        assert abs(secondsfrac) <= 2.0

        assert isinstance(seconds, int)
        days, seconds = divmod(seconds, 24*3600)
        d += days
        s += int(seconds)    # can't overflow
        assert isinstance(s, int)
        assert abs(s) <= 2 * 24 * 3600
        # seconds isn't referenced again before redefinition

        usdouble = secondsfrac * 1e6
        assert abs(usdouble) < 2.1e6    # exact value nie critical
        # secondsfrac isn't referenced again

        jeżeli isinstance(microseconds, float):
            microseconds = round(microseconds + usdouble)
            seconds, microseconds = divmod(microseconds, 1000000)
            days, seconds = divmod(seconds, 24*3600)
            d += days
            s += seconds
        inaczej:
            microseconds = int(microseconds)
            seconds, microseconds = divmod(microseconds, 1000000)
            days, seconds = divmod(seconds, 24*3600)
            d += days
            s += seconds
            microseconds = round(microseconds + usdouble)
        assert isinstance(s, int)
        assert isinstance(microseconds, int)
        assert abs(s) <= 3 * 24 * 3600
        assert abs(microseconds) < 3.1e6

        # Just a little bit of carrying possible dla microseconds oraz seconds.
        seconds, us = divmod(microseconds, 1000000)
        s += seconds
        days, s = divmod(s, 24*3600)
        d += days

        assert isinstance(d, int)
        assert isinstance(s, int) oraz 0 <= s < 24*3600
        assert isinstance(us, int) oraz 0 <= us < 1000000

        jeżeli abs(d) > 999999999:
            podnieś OverflowError("timedelta # of days jest too large: %d" % d)

        self = object.__new__(cls)
        self._days = d
        self._seconds = s
        self._microseconds = us
        self._hashcode = -1
        zwróć self

    def __repr__(self):
        jeżeli self._microseconds:
            zwróć "%s.%s(%d, %d, %d)" % (self.__class__.__module__,
                                          self.__class__.__qualname__,
                                          self._days,
                                          self._seconds,
                                          self._microseconds)
        jeżeli self._seconds:
            zwróć "%s.%s(%d, %d)" % (self.__class__.__module__,
                                      self.__class__.__qualname__,
                                      self._days,
                                      self._seconds)
        zwróć "%s.%s(%d)" % (self.__class__.__module__,
                              self.__class__.__qualname__,
                              self._days)

    def __str__(self):
        mm, ss = divmod(self._seconds, 60)
        hh, mm = divmod(mm, 60)
        s = "%d:%02d:%02d" % (hh, mm, ss)
        jeżeli self._days:
            def plural(n):
                zwróć n, abs(n) != 1 oraz "s" albo ""
            s = ("%d day%s, " % plural(self._days)) + s
        jeżeli self._microseconds:
            s = s + ".%06d" % self._microseconds
        zwróć s

    def total_seconds(self):
        """Total seconds w the duration."""
        zwróć ((self.days * 86400 + self.seconds) * 10**6 +
                self.microseconds) / 10**6

    # Read-only field accessors
    @property
    def days(self):
        """days"""
        zwróć self._days

    @property
    def seconds(self):
        """seconds"""
        zwróć self._seconds

    @property
    def microseconds(self):
        """microseconds"""
        zwróć self._microseconds

    def __add__(self, other):
        jeżeli isinstance(other, timedelta):
            # dla CPython compatibility, we cannot use
            # our __class__ here, but need a real timedelta
            zwróć timedelta(self._days + other._days,
                             self._seconds + other._seconds,
                             self._microseconds + other._microseconds)
        zwróć NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        jeżeli isinstance(other, timedelta):
            # dla CPython compatibility, we cannot use
            # our __class__ here, but need a real timedelta
            zwróć timedelta(self._days - other._days,
                             self._seconds - other._seconds,
                             self._microseconds - other._microseconds)
        zwróć NotImplemented

    def __rsub__(self, other):
        jeżeli isinstance(other, timedelta):
            zwróć -self + other
        zwróć NotImplemented

    def __neg__(self):
        # dla CPython compatibility, we cannot use
        # our __class__ here, but need a real timedelta
        zwróć timedelta(-self._days,
                         -self._seconds,
                         -self._microseconds)

    def __pos__(self):
        zwróć self

    def __abs__(self):
        jeżeli self._days < 0:
            zwróć -self
        inaczej:
            zwróć self

    def __mul__(self, other):
        jeżeli isinstance(other, int):
            # dla CPython compatibility, we cannot use
            # our __class__ here, but need a real timedelta
            zwróć timedelta(self._days * other,
                             self._seconds * other,
                             self._microseconds * other)
        jeżeli isinstance(other, float):
            usec = self._to_microseconds()
            a, b = other.as_integer_ratio()
            zwróć timedelta(0, 0, _divide_and_round(usec * a, b))
        zwróć NotImplemented

    __rmul__ = __mul__

    def _to_microseconds(self):
        zwróć ((self._days * (24*3600) + self._seconds) * 1000000 +
                self._microseconds)

    def __floordiv__(self, other):
        jeżeli nie isinstance(other, (int, timedelta)):
            zwróć NotImplemented
        usec = self._to_microseconds()
        jeżeli isinstance(other, timedelta):
            zwróć usec // other._to_microseconds()
        jeżeli isinstance(other, int):
            zwróć timedelta(0, 0, usec // other)

    def __truediv__(self, other):
        jeżeli nie isinstance(other, (int, float, timedelta)):
            zwróć NotImplemented
        usec = self._to_microseconds()
        jeżeli isinstance(other, timedelta):
            zwróć usec / other._to_microseconds()
        jeżeli isinstance(other, int):
            zwróć timedelta(0, 0, _divide_and_round(usec, other))
        jeżeli isinstance(other, float):
            a, b = other.as_integer_ratio()
            zwróć timedelta(0, 0, _divide_and_round(b * usec, a))

    def __mod__(self, other):
        jeżeli isinstance(other, timedelta):
            r = self._to_microseconds() % other._to_microseconds()
            zwróć timedelta(0, 0, r)
        zwróć NotImplemented

    def __divmod__(self, other):
        jeżeli isinstance(other, timedelta):
            q, r = divmod(self._to_microseconds(),
                          other._to_microseconds())
            zwróć q, timedelta(0, 0, r)
        zwróć NotImplemented

    # Comparisons of timedelta objects przy other.

    def __eq__(self, other):
        jeżeli isinstance(other, timedelta):
            zwróć self._cmp(other) == 0
        inaczej:
            zwróć Nieprawda

    def __le__(self, other):
        jeżeli isinstance(other, timedelta):
            zwróć self._cmp(other) <= 0
        inaczej:
            _cmperror(self, other)

    def __lt__(self, other):
        jeżeli isinstance(other, timedelta):
            zwróć self._cmp(other) < 0
        inaczej:
            _cmperror(self, other)

    def __ge__(self, other):
        jeżeli isinstance(other, timedelta):
            zwróć self._cmp(other) >= 0
        inaczej:
            _cmperror(self, other)

    def __gt__(self, other):
        jeżeli isinstance(other, timedelta):
            zwróć self._cmp(other) > 0
        inaczej:
            _cmperror(self, other)

    def _cmp(self, other):
        assert isinstance(other, timedelta)
        zwróć _cmp(self._getstate(), other._getstate())

    def __hash__(self):
        jeżeli self._hashcode == -1:
            self._hashcode = hash(self._getstate())
        zwróć self._hashcode

    def __bool__(self):
        zwróć (self._days != 0 albo
                self._seconds != 0 albo
                self._microseconds != 0)

    # Pickle support.

    def _getstate(self):
        zwróć (self._days, self._seconds, self._microseconds)

    def __reduce__(self):
        zwróć (self.__class__, self._getstate())

timedelta.min = timedelta(-999999999)
timedelta.max = timedelta(days=999999999, hours=23, minutes=59, seconds=59,
                          microseconds=999999)
timedelta.resolution = timedelta(microseconds=1)

klasa date:
    """Concrete date type.

    Constructors:

    __new__()
    fromtimestamp()
    today()
    fromordinal()

    Operators:

    __repr__, __str__
    __eq__, __le__, __lt__, __ge__, __gt__, __hash__
    __add__, __radd__, __sub__ (add/radd only przy timedelta arg)

    Methods:

    timetuple()
    toordinal()
    weekday()
    isoweekday(), isocalendar(), isoformat()
    ctime()
    strftime()

    Properties (readonly):
    year, month, day
    """
    __slots__ = '_year', '_month', '_day', '_hashcode'

    def __new__(cls, year, month=Nic, day=Nic):
        """Constructor.

        Arguments:

        year, month, day (required, base 1)
        """
        jeżeli month jest Nic oraz isinstance(year, bytes) oraz len(year) == 4 oraz \
                1 <= year[2] <= 12:
            # Pickle support
            self = object.__new__(cls)
            self.__setstate(year)
            self._hashcode = -1
            zwróć self
        year, month, day = _check_date_fields(year, month, day)
        self = object.__new__(cls)
        self._year = year
        self._month = month
        self._day = day
        self._hashcode = -1
        zwróć self

    # Additional constructors

    @classmethod
    def fromtimestamp(cls, t):
        "Construct a date z a POSIX timestamp (like time.time())."
        y, m, d, hh, mm, ss, weekday, jday, dst = _time.localtime(t)
        zwróć cls(y, m, d)

    @classmethod
    def today(cls):
        "Construct a date z time.time()."
        t = _time.time()
        zwróć cls.fromtimestamp(t)

    @classmethod
    def fromordinal(cls, n):
        """Contruct a date z a proleptic Gregorian ordinal.

        January 1 of year 1 jest day 1.  Only the year, month oraz day are
        non-zero w the result.
        """
        y, m, d = _ord2ymd(n)
        zwróć cls(y, m, d)

    # Conversions to string

    def __repr__(self):
        """Convert to formal string, dla repr().

        >>> dt = datetime(2010, 1, 1)
        >>> repr(dt)
        'datetime.datetime(2010, 1, 1, 0, 0)'

        >>> dt = datetime(2010, 1, 1, tzinfo=timezone.utc)
        >>> repr(dt)
        'datetime.datetime(2010, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)'
        """
        zwróć "%s.%s(%d, %d, %d)" % (self.__class__.__module__,
                                      self.__class__.__qualname__,
                                      self._year,
                                      self._month,
                                      self._day)
    # XXX These shouldn't depend on time.localtime(), because that
    # clips the usable dates to [1970 .. 2038).  At least ctime() jest
    # easily done without using strftime() -- that's better too because
    # strftime("%c", ...) jest locale specific.


    def ctime(self):
        "Return ctime() style string."
        weekday = self.toordinal() % 7 albo 7
        zwróć "%s %s %2d 00:00:00 %04d" % (
            _DAYNAMES[weekday],
            _MONTHNAMES[self._month],
            self._day, self._year)

    def strftime(self, fmt):
        "Format using strftime()."
        zwróć _wrap_strftime(self, fmt, self.timetuple())

    def __format__(self, fmt):
        jeżeli nie isinstance(fmt, str):
            podnieś TypeError("must be str, nie %s" % type(fmt).__name__)
        jeżeli len(fmt) != 0:
            zwróć self.strftime(fmt)
        zwróć str(self)

    def isoformat(self):
        """Return the date formatted according to ISO.

        This jest 'YYYY-MM-DD'.

        References:
        - http://www.w3.org/TR/NOTE-datetime
        - http://www.cl.cam.ac.uk/~mgk25/iso-time.html
        """
        zwróć "%04d-%02d-%02d" % (self._year, self._month, self._day)

    __str__ = isoformat

    # Read-only field accessors
    @property
    def year(self):
        """year (1-9999)"""
        zwróć self._year

    @property
    def month(self):
        """month (1-12)"""
        zwróć self._month

    @property
    def day(self):
        """day (1-31)"""
        zwróć self._day

    # Standard conversions, __eq__, __le__, __lt__, __ge__, __gt__,
    # __hash__ (and helpers)

    def timetuple(self):
        "Return local time tuple compatible przy time.localtime()."
        zwróć _build_struct_time(self._year, self._month, self._day,
                                  0, 0, 0, -1)

    def toordinal(self):
        """Return proleptic Gregorian ordinal dla the year, month oraz day.

        January 1 of year 1 jest day 1.  Only the year, month oraz day values
        contribute to the result.
        """
        zwróć _ymd2ord(self._year, self._month, self._day)

    def replace(self, year=Nic, month=Nic, day=Nic):
        """Return a new date przy new values dla the specified fields."""
        jeżeli year jest Nic:
            year = self._year
        jeżeli month jest Nic:
            month = self._month
        jeżeli day jest Nic:
            day = self._day
        zwróć date(year, month, day)

    # Comparisons of date objects przy other.

    def __eq__(self, other):
        jeżeli isinstance(other, date):
            zwróć self._cmp(other) == 0
        zwróć NotImplemented

    def __le__(self, other):
        jeżeli isinstance(other, date):
            zwróć self._cmp(other) <= 0
        zwróć NotImplemented

    def __lt__(self, other):
        jeżeli isinstance(other, date):
            zwróć self._cmp(other) < 0
        zwróć NotImplemented

    def __ge__(self, other):
        jeżeli isinstance(other, date):
            zwróć self._cmp(other) >= 0
        zwróć NotImplemented

    def __gt__(self, other):
        jeżeli isinstance(other, date):
            zwróć self._cmp(other) > 0
        zwróć NotImplemented

    def _cmp(self, other):
        assert isinstance(other, date)
        y, m, d = self._year, self._month, self._day
        y2, m2, d2 = other._year, other._month, other._day
        zwróć _cmp((y, m, d), (y2, m2, d2))

    def __hash__(self):
        "Hash."
        jeżeli self._hashcode == -1:
            self._hashcode = hash(self._getstate())
        zwróć self._hashcode

    # Computations

    def __add__(self, other):
        "Add a date to a timedelta."
        jeżeli isinstance(other, timedelta):
            o = self.toordinal() + other.days
            jeżeli 0 < o <= _MAXORDINAL:
                zwróć date.fromordinal(o)
            podnieś OverflowError("result out of range")
        zwróć NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        """Subtract two dates, albo a date oraz a timedelta."""
        jeżeli isinstance(other, timedelta):
            zwróć self + timedelta(-other.days)
        jeżeli isinstance(other, date):
            days1 = self.toordinal()
            days2 = other.toordinal()
            zwróć timedelta(days1 - days2)
        zwróć NotImplemented

    def weekday(self):
        "Return day of the week, where Monday == 0 ... Sunday == 6."
        zwróć (self.toordinal() + 6) % 7

    # Day-of-the-week oraz week-of-the-year, according to ISO

    def isoweekday(self):
        "Return day of the week, where Monday == 1 ... Sunday == 7."
        # 1-Jan-0001 jest a Monday
        zwróć self.toordinal() % 7 albo 7

    def isocalendar(self):
        """Return a 3-tuple containing ISO year, week number, oraz weekday.

        The first ISO week of the year jest the (Mon-Sun) week
        containing the year's first Thursday; everything inaczej derives
        z that.

        The first week jest 1; Monday jest 1 ... Sunday jest 7.

        ISO calendar algorithm taken from
        http://www.phys.uu.nl/~vgent/calendar/isocalendar.htm
        """
        year = self._year
        week1monday = _isoweek1monday(year)
        today = _ymd2ord(self._year, self._month, self._day)
        # Internally, week oraz day have origin 0
        week, day = divmod(today - week1monday, 7)
        jeżeli week < 0:
            year -= 1
            week1monday = _isoweek1monday(year)
            week, day = divmod(today - week1monday, 7)
        albo_inaczej week >= 52:
            jeżeli today >= _isoweek1monday(year+1):
                year += 1
                week = 0
        zwróć year, week+1, day+1

    # Pickle support.

    def _getstate(self):
        yhi, ylo = divmod(self._year, 256)
        zwróć bytes([yhi, ylo, self._month, self._day]),

    def __setstate(self, string):
        yhi, ylo, self._month, self._day = string
        self._year = yhi * 256 + ylo

    def __reduce__(self):
        zwróć (self.__class__, self._getstate())

_date_class = date  # so functions w/ args named "date" can get at the class

date.min = date(1, 1, 1)
date.max = date(9999, 12, 31)
date.resolution = timedelta(days=1)

klasa tzinfo:
    """Abstract base klasa dla time zone info classes.

    Subclasses must override the name(), utcoffset() oraz dst() methods.
    """
    __slots__ = ()

    def tzname(self, dt):
        "datetime -> string name of time zone."
        podnieś NotImplementedError("tzinfo subclass must override tzname()")

    def utcoffset(self, dt):
        "datetime -> minutes east of UTC (negative dla west of UTC)"
        podnieś NotImplementedError("tzinfo subclass must override utcoffset()")

    def dst(self, dt):
        """datetime -> DST offset w minutes east of UTC.

        Return 0 jeżeli DST nie w effect.  utcoffset() must include the DST
        offset.
        """
        podnieś NotImplementedError("tzinfo subclass must override dst()")

    def fromutc(self, dt):
        "datetime w UTC -> datetime w local time."

        jeżeli nie isinstance(dt, datetime):
            podnieś TypeError("fromutc() requires a datetime argument")
        jeżeli dt.tzinfo jest nie self:
            podnieś ValueError("dt.tzinfo jest nie self")

        dtoff = dt.utcoffset()
        jeżeli dtoff jest Nic:
            podnieś ValueError("fromutc() requires a non-Nic utcoffset() "
                             "result")

        # See the long comment block at the end of this file dla an
        # explanation of this algorithm.
        dtdst = dt.dst()
        jeżeli dtdst jest Nic:
            podnieś ValueError("fromutc() requires a non-Nic dst() result")
        delta = dtoff - dtdst
        jeżeli delta:
            dt += delta
            dtdst = dt.dst()
            jeżeli dtdst jest Nic:
                podnieś ValueError("fromutc(): dt.dst gave inconsistent "
                                 "results; cannot convert")
        zwróć dt + dtdst

    # Pickle support.

    def __reduce__(self):
        getinitargs = getattr(self, "__getinitargs__", Nic)
        jeżeli getinitargs:
            args = getinitargs()
        inaczej:
            args = ()
        getstate = getattr(self, "__getstate__", Nic)
        jeżeli getstate:
            state = getstate()
        inaczej:
            state = getattr(self, "__dict__", Nic) albo Nic
        jeżeli state jest Nic:
            zwróć (self.__class__, args)
        inaczej:
            zwróć (self.__class__, args, state)

_tzinfo_class = tzinfo

klasa time:
    """Time przy time zone.

    Constructors:

    __new__()

    Operators:

    __repr__, __str__
    __eq__, __le__, __lt__, __ge__, __gt__, __hash__

    Methods:

    strftime()
    isoformat()
    utcoffset()
    tzname()
    dst()

    Properties (readonly):
    hour, minute, second, microsecond, tzinfo
    """
    __slots__ = '_hour', '_minute', '_second', '_microsecond', '_tzinfo', '_hashcode'

    def __new__(cls, hour=0, minute=0, second=0, microsecond=0, tzinfo=Nic):
        """Constructor.

        Arguments:

        hour, minute (required)
        second, microsecond (default to zero)
        tzinfo (default to Nic)
        """
        jeżeli isinstance(hour, bytes) oraz len(hour) == 6 oraz hour[0] < 24:
            # Pickle support
            self = object.__new__(cls)
            self.__setstate(hour, minute albo Nic)
            self._hashcode = -1
            zwróć self
        hour, minute, second, microsecond = _check_time_fields(
            hour, minute, second, microsecond)
        _check_tzinfo_arg(tzinfo)
        self = object.__new__(cls)
        self._hour = hour
        self._minute = minute
        self._second = second
        self._microsecond = microsecond
        self._tzinfo = tzinfo
        self._hashcode = -1
        zwróć self

    # Read-only field accessors
    @property
    def hour(self):
        """hour (0-23)"""
        zwróć self._hour

    @property
    def minute(self):
        """minute (0-59)"""
        zwróć self._minute

    @property
    def second(self):
        """second (0-59)"""
        zwróć self._second

    @property
    def microsecond(self):
        """microsecond (0-999999)"""
        zwróć self._microsecond

    @property
    def tzinfo(self):
        """timezone info object"""
        zwróć self._tzinfo

    # Standard conversions, __hash__ (and helpers)

    # Comparisons of time objects przy other.

    def __eq__(self, other):
        jeżeli isinstance(other, time):
            zwróć self._cmp(other, allow_mixed=Prawda) == 0
        inaczej:
            zwróć Nieprawda

    def __le__(self, other):
        jeżeli isinstance(other, time):
            zwróć self._cmp(other) <= 0
        inaczej:
            _cmperror(self, other)

    def __lt__(self, other):
        jeżeli isinstance(other, time):
            zwróć self._cmp(other) < 0
        inaczej:
            _cmperror(self, other)

    def __ge__(self, other):
        jeżeli isinstance(other, time):
            zwróć self._cmp(other) >= 0
        inaczej:
            _cmperror(self, other)

    def __gt__(self, other):
        jeżeli isinstance(other, time):
            zwróć self._cmp(other) > 0
        inaczej:
            _cmperror(self, other)

    def _cmp(self, other, allow_mixed=Nieprawda):
        assert isinstance(other, time)
        mytz = self._tzinfo
        ottz = other._tzinfo
        myoff = otoff = Nic

        jeżeli mytz jest ottz:
            base_compare = Prawda
        inaczej:
            myoff = self.utcoffset()
            otoff = other.utcoffset()
            base_compare = myoff == otoff

        jeżeli base_compare:
            zwróć _cmp((self._hour, self._minute, self._second,
                         self._microsecond),
                        (other._hour, other._minute, other._second,
                         other._microsecond))
        jeżeli myoff jest Nic albo otoff jest Nic:
            jeżeli allow_mixed:
                zwróć 2 # arbitrary non-zero value
            inaczej:
                podnieś TypeError("cannot compare naive oraz aware times")
        myhhmm = self._hour * 60 + self._minute - myoff//timedelta(minutes=1)
        othhmm = other._hour * 60 + other._minute - otoff//timedelta(minutes=1)
        zwróć _cmp((myhhmm, self._second, self._microsecond),
                    (othhmm, other._second, other._microsecond))

    def __hash__(self):
        """Hash."""
        jeżeli self._hashcode == -1:
            tzoff = self.utcoffset()
            jeżeli nie tzoff:  # zero albo Nic
                self._hashcode = hash(self._getstate()[0])
            inaczej:
                h, m = divmod(timedelta(hours=self.hour, minutes=self.minute) - tzoff,
                              timedelta(hours=1))
                assert nie m % timedelta(minutes=1), "whole minute"
                m //= timedelta(minutes=1)
                jeżeli 0 <= h < 24:
                    self._hashcode = hash(time(h, m, self.second, self.microsecond))
                inaczej:
                    self._hashcode = hash((h, m, self.second, self.microsecond))
        zwróć self._hashcode

    # Conversion to string

    def _tzstr(self, sep=":"):
        """Return formatted timezone offset (+xx:xx) albo Nic."""
        off = self.utcoffset()
        jeżeli off jest nie Nic:
            jeżeli off.days < 0:
                sign = "-"
                off = -off
            inaczej:
                sign = "+"
            hh, mm = divmod(off, timedelta(hours=1))
            assert nie mm % timedelta(minutes=1), "whole minute"
            mm //= timedelta(minutes=1)
            assert 0 <= hh < 24
            off = "%s%02d%s%02d" % (sign, hh, sep, mm)
        zwróć off

    def __repr__(self):
        """Convert to formal string, dla repr()."""
        jeżeli self._microsecond != 0:
            s = ", %d, %d" % (self._second, self._microsecond)
        albo_inaczej self._second != 0:
            s = ", %d" % self._second
        inaczej:
            s = ""
        s= "%s.%s(%d, %d%s)" % (self.__class__.__module__,
                                self.__class__.__qualname__,
                                self._hour, self._minute, s)
        jeżeli self._tzinfo jest nie Nic:
            assert s[-1:] == ")"
            s = s[:-1] + ", tzinfo=%r" % self._tzinfo + ")"
        zwróć s

    def isoformat(self):
        """Return the time formatted according to ISO.

        This jest 'HH:MM:SS.mmmmmm+zz:zz', albo 'HH:MM:SS+zz:zz' if
        self.microsecond == 0.
        """
        s = _format_time(self._hour, self._minute, self._second,
                         self._microsecond)
        tz = self._tzstr()
        jeżeli tz:
            s += tz
        zwróć s

    __str__ = isoformat

    def strftime(self, fmt):
        """Format using strftime().  The date part of the timestamp dalejed
        to underlying strftime should nie be used.
        """
        # The year must be >= 1000 inaczej Python's strftime implementation
        # can podnieś a bogus exception.
        timetuple = (1900, 1, 1,
                     self._hour, self._minute, self._second,
                     0, 1, -1)
        zwróć _wrap_strftime(self, fmt, timetuple)

    def __format__(self, fmt):
        jeżeli nie isinstance(fmt, str):
            podnieś TypeError("must be str, nie %s" % type(fmt).__name__)
        jeżeli len(fmt) != 0:
            zwróć self.strftime(fmt)
        zwróć str(self)

    # Timezone functions

    def utcoffset(self):
        """Return the timezone offset w minutes east of UTC (negative west of
        UTC)."""
        jeżeli self._tzinfo jest Nic:
            zwróć Nic
        offset = self._tzinfo.utcoffset(Nic)
        _check_utc_offset("utcoffset", offset)
        zwróć offset

    def tzname(self):
        """Return the timezone name.

        Note that the name jest 100% informational -- there's no requirement that
        it mean anything w particular. For example, "GMT", "UTC", "-500",
        "-5:00", "EDT", "US/Eastern", "America/New York" are all valid replies.
        """
        jeżeli self._tzinfo jest Nic:
            zwróć Nic
        name = self._tzinfo.tzname(Nic)
        _check_tzname(name)
        zwróć name

    def dst(self):
        """Return 0 jeżeli DST jest nie w effect, albo the DST offset (in minutes
        eastward) jeżeli DST jest w effect.

        This jest purely informational; the DST offset has already been added to
        the UTC offset returned by utcoffset() jeżeli applicable, so there's no
        need to consult dst() unless you're interested w displaying the DST
        info.
        """
        jeżeli self._tzinfo jest Nic:
            zwróć Nic
        offset = self._tzinfo.dst(Nic)
        _check_utc_offset("dst", offset)
        zwróć offset

    def replace(self, hour=Nic, minute=Nic, second=Nic, microsecond=Nic,
                tzinfo=Prawda):
        """Return a new time przy new values dla the specified fields."""
        jeżeli hour jest Nic:
            hour = self.hour
        jeżeli minute jest Nic:
            minute = self.minute
        jeżeli second jest Nic:
            second = self.second
        jeżeli microsecond jest Nic:
            microsecond = self.microsecond
        jeżeli tzinfo jest Prawda:
            tzinfo = self.tzinfo
        zwróć time(hour, minute, second, microsecond, tzinfo)

    # Pickle support.

    def _getstate(self):
        us2, us3 = divmod(self._microsecond, 256)
        us1, us2 = divmod(us2, 256)
        basestate = bytes([self._hour, self._minute, self._second,
                           us1, us2, us3])
        jeżeli self._tzinfo jest Nic:
            zwróć (basestate,)
        inaczej:
            zwróć (basestate, self._tzinfo)

    def __setstate(self, string, tzinfo):
        jeżeli tzinfo jest nie Nic oraz nie isinstance(tzinfo, _tzinfo_class):
            podnieś TypeError("bad tzinfo state arg")
        self._hour, self._minute, self._second, us1, us2, us3 = string
        self._microsecond = (((us1 << 8) | us2) << 8) | us3
        self._tzinfo = tzinfo

    def __reduce__(self):
        zwróć (time, self._getstate())

_time_class = time  # so functions w/ args named "time" can get at the class

time.min = time(0, 0, 0)
time.max = time(23, 59, 59, 999999)
time.resolution = timedelta(microseconds=1)

klasa datetime(date):
    """datetime(year, month, day[, hour[, minute[, second[, microsecond[,tzinfo]]]]])

    The year, month oraz day arguments are required. tzinfo may be Nic, albo an
    instance of a tzinfo subclass. The remaining arguments may be ints.
    """
    __slots__ = date.__slots__ + time.__slots__

    def __new__(cls, year, month=Nic, day=Nic, hour=0, minute=0, second=0,
                microsecond=0, tzinfo=Nic):
        jeżeli isinstance(year, bytes) oraz len(year) == 10 oraz 1 <= year[2] <= 12:
            # Pickle support
            self = object.__new__(cls)
            self.__setstate(year, month)
            self._hashcode = -1
            zwróć self
        year, month, day = _check_date_fields(year, month, day)
        hour, minute, second, microsecond = _check_time_fields(
            hour, minute, second, microsecond)
        _check_tzinfo_arg(tzinfo)
        self = object.__new__(cls)
        self._year = year
        self._month = month
        self._day = day
        self._hour = hour
        self._minute = minute
        self._second = second
        self._microsecond = microsecond
        self._tzinfo = tzinfo
        self._hashcode = -1
        zwróć self

    # Read-only field accessors
    @property
    def hour(self):
        """hour (0-23)"""
        zwróć self._hour

    @property
    def minute(self):
        """minute (0-59)"""
        zwróć self._minute

    @property
    def second(self):
        """second (0-59)"""
        zwróć self._second

    @property
    def microsecond(self):
        """microsecond (0-999999)"""
        zwróć self._microsecond

    @property
    def tzinfo(self):
        """timezone info object"""
        zwróć self._tzinfo

    @classmethod
    def fromtimestamp(cls, t, tz=Nic):
        """Construct a datetime z a POSIX timestamp (like time.time()).

        A timezone info object may be dalejed w jako well.
        """
        _check_tzinfo_arg(tz)

        converter = _time.localtime jeżeli tz jest Nic inaczej _time.gmtime

        t, frac = divmod(t, 1.0)
        us = int(frac * 1e6)

        # If timestamp jest less than one microsecond smaller than a
        # full second, us can be rounded up to 1000000.  In this case,
        # roll over to seconds, otherwise, ValueError jest podnieśd
        # by the constructor.
        jeżeli us == 1000000:
            t += 1
            us = 0
        y, m, d, hh, mm, ss, weekday, jday, dst = converter(t)
        ss = min(ss, 59)    # clamp out leap seconds jeżeli the platform has them
        result = cls(y, m, d, hh, mm, ss, us, tz)
        jeżeli tz jest nie Nic:
            result = tz.fromutc(result)
        zwróć result

    @classmethod
    def utcfromtimestamp(cls, t):
        """Construct a naive UTC datetime z a POSIX timestamp."""
        t, frac = divmod(t, 1.0)
        us = int(frac * 1e6)

        # If timestamp jest less than one microsecond smaller than a
        # full second, us can be rounded up to 1000000.  In this case,
        # roll over to seconds, otherwise, ValueError jest podnieśd
        # by the constructor.
        jeżeli us == 1000000:
            t += 1
            us = 0
        y, m, d, hh, mm, ss, weekday, jday, dst = _time.gmtime(t)
        ss = min(ss, 59)    # clamp out leap seconds jeżeli the platform has them
        zwróć cls(y, m, d, hh, mm, ss, us)

    @classmethod
    def now(cls, tz=Nic):
        "Construct a datetime z time.time() oraz optional time zone info."
        t = _time.time()
        zwróć cls.fromtimestamp(t, tz)

    @classmethod
    def utcnow(cls):
        "Construct a UTC datetime z time.time()."
        t = _time.time()
        zwróć cls.utcfromtimestamp(t)

    @classmethod
    def combine(cls, date, time):
        "Construct a datetime z a given date oraz a given time."
        jeżeli nie isinstance(date, _date_class):
            podnieś TypeError("date argument must be a date instance")
        jeżeli nie isinstance(time, _time_class):
            podnieś TypeError("time argument must be a time instance")
        zwróć cls(date.year, date.month, date.day,
                   time.hour, time.minute, time.second, time.microsecond,
                   time.tzinfo)

    def timetuple(self):
        "Return local time tuple compatible przy time.localtime()."
        dst = self.dst()
        jeżeli dst jest Nic:
            dst = -1
        albo_inaczej dst:
            dst = 1
        inaczej:
            dst = 0
        zwróć _build_struct_time(self.year, self.month, self.day,
                                  self.hour, self.minute, self.second,
                                  dst)

    def timestamp(self):
        "Return POSIX timestamp jako float"
        jeżeli self._tzinfo jest Nic:
            zwróć _time.mktime((self.year, self.month, self.day,
                                 self.hour, self.minute, self.second,
                                 -1, -1, -1)) + self.microsecond / 1e6
        inaczej:
            zwróć (self - _EPOCH).total_seconds()

    def utctimetuple(self):
        "Return UTC time tuple compatible przy time.gmtime()."
        offset = self.utcoffset()
        jeżeli offset:
            self -= offset
        y, m, d = self.year, self.month, self.day
        hh, mm, ss = self.hour, self.minute, self.second
        zwróć _build_struct_time(y, m, d, hh, mm, ss, 0)

    def date(self):
        "Return the date part."
        zwróć date(self._year, self._month, self._day)

    def time(self):
        "Return the time part, przy tzinfo Nic."
        zwróć time(self.hour, self.minute, self.second, self.microsecond)

    def timetz(self):
        "Return the time part, przy same tzinfo."
        zwróć time(self.hour, self.minute, self.second, self.microsecond,
                    self._tzinfo)

    def replace(self, year=Nic, month=Nic, day=Nic, hour=Nic,
                minute=Nic, second=Nic, microsecond=Nic, tzinfo=Prawda):
        """Return a new datetime przy new values dla the specified fields."""
        jeżeli year jest Nic:
            year = self.year
        jeżeli month jest Nic:
            month = self.month
        jeżeli day jest Nic:
            day = self.day
        jeżeli hour jest Nic:
            hour = self.hour
        jeżeli minute jest Nic:
            minute = self.minute
        jeżeli second jest Nic:
            second = self.second
        jeżeli microsecond jest Nic:
            microsecond = self.microsecond
        jeżeli tzinfo jest Prawda:
            tzinfo = self.tzinfo
        zwróć datetime(year, month, day, hour, minute, second, microsecond,
                        tzinfo)

    def astimezone(self, tz=Nic):
        jeżeli tz jest Nic:
            jeżeli self.tzinfo jest Nic:
                podnieś ValueError("astimezone() requires an aware datetime")
            ts = (self - _EPOCH) // timedelta(seconds=1)
            localtm = _time.localtime(ts)
            local = datetime(*localtm[:6])
            spróbuj:
                # Extract TZ data jeżeli available
                gmtoff = localtm.tm_gmtoff
                zone = localtm.tm_zone
            wyjąwszy AttributeError:
                # Compute UTC offset oraz compare przy the value implied
                # by tm_isdst.  If the values match, use the zone name
                # implied by tm_isdst.
                delta = local - datetime(*_time.gmtime(ts)[:6])
                dst = _time.daylight oraz localtm.tm_isdst > 0
                gmtoff = -(_time.altzone jeżeli dst inaczej _time.timezone)
                jeżeli delta == timedelta(seconds=gmtoff):
                    tz = timezone(delta, _time.tzname[dst])
                inaczej:
                    tz = timezone(delta)
            inaczej:
                tz = timezone(timedelta(seconds=gmtoff), zone)

        albo_inaczej nie isinstance(tz, tzinfo):
            podnieś TypeError("tz argument must be an instance of tzinfo")

        mytz = self.tzinfo
        jeżeli mytz jest Nic:
            podnieś ValueError("astimezone() requires an aware datetime")

        jeżeli tz jest mytz:
            zwróć self

        # Convert self to UTC, oraz attach the new time zone object.
        myoffset = self.utcoffset()
        jeżeli myoffset jest Nic:
            podnieś ValueError("astimezone() requires an aware datetime")
        utc = (self - myoffset).replace(tzinfo=tz)

        # Convert z UTC to tz's local time.
        zwróć tz.fromutc(utc)

    # Ways to produce a string.

    def ctime(self):
        "Return ctime() style string."
        weekday = self.toordinal() % 7 albo 7
        zwróć "%s %s %2d %02d:%02d:%02d %04d" % (
            _DAYNAMES[weekday],
            _MONTHNAMES[self._month],
            self._day,
            self._hour, self._minute, self._second,
            self._year)

    def isoformat(self, sep='T'):
        """Return the time formatted according to ISO.

        This jest 'YYYY-MM-DD HH:MM:SS.mmmmmm', albo 'YYYY-MM-DD HH:MM:SS' if
        self.microsecond == 0.

        If self.tzinfo jest nie Nic, the UTC offset jest also attached, giving
        'YYYY-MM-DD HH:MM:SS.mmmmmm+HH:MM' albo 'YYYY-MM-DD HH:MM:SS+HH:MM'.

        Optional argument sep specifies the separator between date oraz
        time, default 'T'.
        """
        s = ("%04d-%02d-%02d%c" % (self._year, self._month, self._day, sep) +
             _format_time(self._hour, self._minute, self._second,
                          self._microsecond))
        off = self.utcoffset()
        jeżeli off jest nie Nic:
            jeżeli off.days < 0:
                sign = "-"
                off = -off
            inaczej:
                sign = "+"
            hh, mm = divmod(off, timedelta(hours=1))
            assert nie mm % timedelta(minutes=1), "whole minute"
            mm //= timedelta(minutes=1)
            s += "%s%02d:%02d" % (sign, hh, mm)
        zwróć s

    def __repr__(self):
        """Convert to formal string, dla repr()."""
        L = [self._year, self._month, self._day,  # These are never zero
             self._hour, self._minute, self._second, self._microsecond]
        jeżeli L[-1] == 0:
            usuń L[-1]
        jeżeli L[-1] == 0:
            usuń L[-1]
        s = "%s.%s(%s)" % (self.__class__.__module__,
                           self.__class__.__qualname__,
                           ", ".join(map(str, L)))
        jeżeli self._tzinfo jest nie Nic:
            assert s[-1:] == ")"
            s = s[:-1] + ", tzinfo=%r" % self._tzinfo + ")"
        zwróć s

    def __str__(self):
        "Convert to string, dla str()."
        zwróć self.isoformat(sep=' ')

    @classmethod
    def strptime(cls, date_string, format):
        'string, format -> new datetime parsed z a string (like time.strptime()).'
        zaimportuj _strptime
        zwróć _strptime._strptime_datetime(cls, date_string, format)

    def utcoffset(self):
        """Return the timezone offset w minutes east of UTC (negative west of
        UTC)."""
        jeżeli self._tzinfo jest Nic:
            zwróć Nic
        offset = self._tzinfo.utcoffset(self)
        _check_utc_offset("utcoffset", offset)
        zwróć offset

    def tzname(self):
        """Return the timezone name.

        Note that the name jest 100% informational -- there's no requirement that
        it mean anything w particular. For example, "GMT", "UTC", "-500",
        "-5:00", "EDT", "US/Eastern", "America/New York" are all valid replies.
        """
        jeżeli self._tzinfo jest Nic:
            zwróć Nic
        name = self._tzinfo.tzname(self)
        _check_tzname(name)
        zwróć name

    def dst(self):
        """Return 0 jeżeli DST jest nie w effect, albo the DST offset (in minutes
        eastward) jeżeli DST jest w effect.

        This jest purely informational; the DST offset has already been added to
        the UTC offset returned by utcoffset() jeżeli applicable, so there's no
        need to consult dst() unless you're interested w displaying the DST
        info.
        """
        jeżeli self._tzinfo jest Nic:
            zwróć Nic
        offset = self._tzinfo.dst(self)
        _check_utc_offset("dst", offset)
        zwróć offset

    # Comparisons of datetime objects przy other.

    def __eq__(self, other):
        jeżeli isinstance(other, datetime):
            zwróć self._cmp(other, allow_mixed=Prawda) == 0
        albo_inaczej nie isinstance(other, date):
            zwróć NotImplemented
        inaczej:
            zwróć Nieprawda

    def __le__(self, other):
        jeżeli isinstance(other, datetime):
            zwróć self._cmp(other) <= 0
        albo_inaczej nie isinstance(other, date):
            zwróć NotImplemented
        inaczej:
            _cmperror(self, other)

    def __lt__(self, other):
        jeżeli isinstance(other, datetime):
            zwróć self._cmp(other) < 0
        albo_inaczej nie isinstance(other, date):
            zwróć NotImplemented
        inaczej:
            _cmperror(self, other)

    def __ge__(self, other):
        jeżeli isinstance(other, datetime):
            zwróć self._cmp(other) >= 0
        albo_inaczej nie isinstance(other, date):
            zwróć NotImplemented
        inaczej:
            _cmperror(self, other)

    def __gt__(self, other):
        jeżeli isinstance(other, datetime):
            zwróć self._cmp(other) > 0
        albo_inaczej nie isinstance(other, date):
            zwróć NotImplemented
        inaczej:
            _cmperror(self, other)

    def _cmp(self, other, allow_mixed=Nieprawda):
        assert isinstance(other, datetime)
        mytz = self._tzinfo
        ottz = other._tzinfo
        myoff = otoff = Nic

        jeżeli mytz jest ottz:
            base_compare = Prawda
        inaczej:
            myoff = self.utcoffset()
            otoff = other.utcoffset()
            base_compare = myoff == otoff

        jeżeli base_compare:
            zwróć _cmp((self._year, self._month, self._day,
                         self._hour, self._minute, self._second,
                         self._microsecond),
                        (other._year, other._month, other._day,
                         other._hour, other._minute, other._second,
                         other._microsecond))
        jeżeli myoff jest Nic albo otoff jest Nic:
            jeżeli allow_mixed:
                zwróć 2 # arbitrary non-zero value
            inaczej:
                podnieś TypeError("cannot compare naive oraz aware datetimes")
        # XXX What follows could be done more efficiently...
        diff = self - other     # this will take offsets into account
        jeżeli diff.days < 0:
            zwróć -1
        zwróć diff oraz 1 albo 0

    def __add__(self, other):
        "Add a datetime oraz a timedelta."
        jeżeli nie isinstance(other, timedelta):
            zwróć NotImplemented
        delta = timedelta(self.toordinal(),
                          hours=self._hour,
                          minutes=self._minute,
                          seconds=self._second,
                          microseconds=self._microsecond)
        delta += other
        hour, rem = divmod(delta.seconds, 3600)
        minute, second = divmod(rem, 60)
        jeżeli 0 < delta.days <= _MAXORDINAL:
            zwróć datetime.combine(date.fromordinal(delta.days),
                                    time(hour, minute, second,
                                         delta.microseconds,
                                         tzinfo=self._tzinfo))
        podnieś OverflowError("result out of range")

    __radd__ = __add__

    def __sub__(self, other):
        "Subtract two datetimes, albo a datetime oraz a timedelta."
        jeżeli nie isinstance(other, datetime):
            jeżeli isinstance(other, timedelta):
                zwróć self + -other
            zwróć NotImplemented

        days1 = self.toordinal()
        days2 = other.toordinal()
        secs1 = self._second + self._minute * 60 + self._hour * 3600
        secs2 = other._second + other._minute * 60 + other._hour * 3600
        base = timedelta(days1 - days2,
                         secs1 - secs2,
                         self._microsecond - other._microsecond)
        jeżeli self._tzinfo jest other._tzinfo:
            zwróć base
        myoff = self.utcoffset()
        otoff = other.utcoffset()
        jeżeli myoff == otoff:
            zwróć base
        jeżeli myoff jest Nic albo otoff jest Nic:
            podnieś TypeError("cannot mix naive oraz timezone-aware time")
        zwróć base + otoff - myoff

    def __hash__(self):
        jeżeli self._hashcode == -1:
            tzoff = self.utcoffset()
            jeżeli tzoff jest Nic:
                self._hashcode = hash(self._getstate()[0])
            inaczej:
                days = _ymd2ord(self.year, self.month, self.day)
                seconds = self.hour * 3600 + self.minute * 60 + self.second
                self._hashcode = hash(timedelta(days, seconds, self.microsecond) - tzoff)
        zwróć self._hashcode

    # Pickle support.

    def _getstate(self):
        yhi, ylo = divmod(self._year, 256)
        us2, us3 = divmod(self._microsecond, 256)
        us1, us2 = divmod(us2, 256)
        basestate = bytes([yhi, ylo, self._month, self._day,
                           self._hour, self._minute, self._second,
                           us1, us2, us3])
        jeżeli self._tzinfo jest Nic:
            zwróć (basestate,)
        inaczej:
            zwróć (basestate, self._tzinfo)

    def __setstate(self, string, tzinfo):
        jeżeli tzinfo jest nie Nic oraz nie isinstance(tzinfo, _tzinfo_class):
            podnieś TypeError("bad tzinfo state arg")
        (yhi, ylo, self._month, self._day, self._hour,
         self._minute, self._second, us1, us2, us3) = string
        self._year = yhi * 256 + ylo
        self._microsecond = (((us1 << 8) | us2) << 8) | us3
        self._tzinfo = tzinfo

    def __reduce__(self):
        zwróć (self.__class__, self._getstate())


datetime.min = datetime(1, 1, 1)
datetime.max = datetime(9999, 12, 31, 23, 59, 59, 999999)
datetime.resolution = timedelta(microseconds=1)


def _isoweek1monday(year):
    # Helper to calculate the day number of the Monday starting week 1
    # XXX This could be done more efficiently
    THURSDAY = 3
    firstday = _ymd2ord(year, 1, 1)
    firstweekday = (firstday + 6) % 7  # See weekday() above
    week1monday = firstday - firstweekday
    jeżeli firstweekday > THURSDAY:
        week1monday += 7
    zwróć week1monday

klasa timezone(tzinfo):
    __slots__ = '_offset', '_name'

    # Sentinel value to disallow Nic
    _Omitted = object()
    def __new__(cls, offset, name=_Omitted):
        jeżeli nie isinstance(offset, timedelta):
            podnieś TypeError("offset must be a timedelta")
        jeżeli name jest cls._Omitted:
            jeżeli nie offset:
                zwróć cls.utc
            name = Nic
        albo_inaczej nie isinstance(name, str):
            podnieś TypeError("name must be a string")
        jeżeli nie cls._minoffset <= offset <= cls._maxoffset:
            podnieś ValueError("offset must be a timedelta "
                             "strictly between -timedelta(hours=24) oraz "
                             "timedelta(hours=24).")
        jeżeli (offset.microseconds != 0 albo offset.seconds % 60 != 0):
            podnieś ValueError("offset must be a timedelta "
                             "representing a whole number of minutes")
        zwróć cls._create(offset, name)

    @classmethod
    def _create(cls, offset, name=Nic):
        self = tzinfo.__new__(cls)
        self._offset = offset
        self._name = name
        zwróć self

    def __getinitargs__(self):
        """pickle support"""
        jeżeli self._name jest Nic:
            zwróć (self._offset,)
        zwróć (self._offset, self._name)

    def __eq__(self, other):
        jeżeli type(other) != timezone:
            zwróć Nieprawda
        zwróć self._offset == other._offset

    def __hash__(self):
        zwróć hash(self._offset)

    def __repr__(self):
        """Convert to formal string, dla repr().

        >>> tz = timezone.utc
        >>> repr(tz)
        'datetime.timezone.utc'
        >>> tz = timezone(timedelta(hours=-5), 'EST')
        >>> repr(tz)
        "datetime.timezone(datetime.timedelta(-1, 68400), 'EST')"
        """
        jeżeli self jest self.utc:
            zwróć 'datetime.timezone.utc'
        jeżeli self._name jest Nic:
            zwróć "%s.%s(%r)" % (self.__class__.__module__,
                                  self.__class__.__qualname__,
                                  self._offset)
        zwróć "%s.%s(%r, %r)" % (self.__class__.__module__,
                                  self.__class__.__qualname__,
                                  self._offset, self._name)

    def __str__(self):
        zwróć self.tzname(Nic)

    def utcoffset(self, dt):
        jeżeli isinstance(dt, datetime) albo dt jest Nic:
            zwróć self._offset
        podnieś TypeError("utcoffset() argument must be a datetime instance"
                        " albo Nic")

    def tzname(self, dt):
        jeżeli isinstance(dt, datetime) albo dt jest Nic:
            jeżeli self._name jest Nic:
                zwróć self._name_from_offset(self._offset)
            zwróć self._name
        podnieś TypeError("tzname() argument must be a datetime instance"
                        " albo Nic")

    def dst(self, dt):
        jeżeli isinstance(dt, datetime) albo dt jest Nic:
            zwróć Nic
        podnieś TypeError("dst() argument must be a datetime instance"
                        " albo Nic")

    def fromutc(self, dt):
        jeżeli isinstance(dt, datetime):
            jeżeli dt.tzinfo jest nie self:
                podnieś ValueError("fromutc: dt.tzinfo "
                                 "is nie self")
            zwróć dt + self._offset
        podnieś TypeError("fromutc() argument must be a datetime instance"
                        " albo Nic")

    _maxoffset = timedelta(hours=23, minutes=59)
    _minoffset = -_maxoffset

    @staticmethod
    def _name_from_offset(delta):
        jeżeli delta < timedelta(0):
            sign = '-'
            delta = -delta
        inaczej:
            sign = '+'
        hours, rest = divmod(delta, timedelta(hours=1))
        minutes = rest // timedelta(minutes=1)
        zwróć 'UTC{}{:02d}:{:02d}'.format(sign, hours, minutes)

timezone.utc = timezone._create(timedelta(0))
timezone.min = timezone._create(timezone._minoffset)
timezone.max = timezone._create(timezone._maxoffset)
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

# Some time zone algebra.  For a datetime x, let
#     x.n = x stripped of its timezone -- its naive time.
#     x.o = x.utcoffset(), oraz assuming that doesn't podnieś an exception albo
#           zwróć Nic
#     x.d = x.dst(), oraz assuming that doesn't podnieś an exception albo
#           zwróć Nic
#     x.s = x's standard offset, x.o - x.d
#
# Now some derived rules, where k jest a duration (timedelta).
#
# 1. x.o = x.s + x.d
#    This follows z the definition of x.s.
#
# 2. If x oraz y have the same tzinfo member, x.s = y.s.
#    This jest actually a requirement, an assumption we need to make about
#    sane tzinfo classes.
#
# 3. The naive UTC time corresponding to x jest x.n - x.o.
#    This jest again a requirement dla a sane tzinfo class.
#
# 4. (x+k).s = x.s
#    This follows z #2, oraz that datimetimetz+timedelta preserves tzinfo.
#
# 5. (x+k).n = x.n + k
#    Again follows z how arithmetic jest defined.
#
# Now we can explain tz.fromutc(x).  Let's assume it's an interesting case
# (meaning that the various tzinfo methods exist, oraz don't blow up albo zwróć
# Nic when called).
#
# The function wants to zwróć a datetime y przy timezone tz, equivalent to x.
# x jest already w UTC.
#
# By #3, we want
#
#     y.n - y.o = x.n                             [1]
#
# The algorithm starts by attaching tz to x.n, oraz calling that y.  So
# x.n = y.n at the start.  Then it wants to add a duration k to y, so that [1]
# becomes true; w effect, we want to solve [2] dla k:
#
#    (y+k).n - (y+k).o = x.n                      [2]
#
# By #1, this jest the same as
#
#    (y+k).n - ((y+k).s + (y+k).d) = x.n          [3]
#
# By #5, (y+k).n = y.n + k, which equals x.n + k because x.n=y.n at the start.
# Substituting that into [3],
#
#    x.n + k - (y+k).s - (y+k).d = x.n; the x.n terms cancel, leaving
#    k - (y+k).s - (y+k).d = 0; rearranging,
#    k = (y+k).s - (y+k).d; by #4, (y+k).s == y.s, so
#    k = y.s - (y+k).d
#
# On the RHS, (y+k).d can't be computed directly, but y.s can be, oraz we
# approximate k by ignoring the (y+k).d term at first.  Note that k can't be
# very large, since all offset-returning methods zwróć a duration of magnitude
# less than 24 hours.  For that reason, jeżeli y jest firmly w std time, (y+k).d must
# be 0, so ignoring it has no consequence then.
#
# In any case, the new value jest
#
#     z = y + y.s                                 [4]
#
# It's helpful to step back at look at [4] z a higher level:  it's simply
# mapping z UTC to tz's standard time.
#
# At this point, if
#
#     z.n - z.o = x.n                             [5]
#
# we have an equivalent time, oraz are almost done.  The insecurity here jest
# at the start of daylight time.  Picture US Eastern dla concreteness.  The wall
# time jumps z 1:59 to 3:00, oraz wall hours of the form 2:MM don't make good
# sense then.  The docs ask that an Eastern tzinfo klasa consider such a time to
# be EDT (because it's "after 2"), which jest a redundant spelling of 1:MM EST
# on the day DST starts.  We want to zwróć the 1:MM EST spelling because that's
# the only spelling that makes sense on the local wall clock.
#
# In fact, jeżeli [5] holds at this point, we do have the standard-time spelling,
# but that takes a bit of proof.  We first prove a stronger result.  What's the
# difference between the LHS oraz RHS of [5]?  Let
#
#     diff = x.n - (z.n - z.o)                    [6]
#
# Now
#     z.n =                       by [4]
#     (y + y.s).n =               by #5
#     y.n + y.s =                 since y.n = x.n
#     x.n + y.s =                 since z oraz y are have the same tzinfo member,
#                                     y.s = z.s by #2
#     x.n + z.s
#
# Plugging that back into [6] gives
#
#     diff =
#     x.n - ((x.n + z.s) - z.o) =     expanding
#     x.n - x.n - z.s + z.o =         cancelling
#     - z.s + z.o =                   by #2
#     z.d
#
# So diff = z.d.
#
# If [5] jest true now, diff = 0, so z.d = 0 too, oraz we have the standard-time
# spelling we wanted w the endcase described above.  We're done.  Contrarily,
# jeżeli z.d = 0, then we have a UTC equivalent, oraz are also done.
#
# If [5] jest nie true now, diff = z.d != 0, oraz z.d jest the offset we need to
# add to z (in effect, z jest w tz's standard time, oraz we need to shift the
# local clock into tz's daylight time).
#
# Let
#
#     z' = z + z.d = z + diff                     [7]
#
# oraz we can again ask whether
#
#     z'.n - z'.o = x.n                           [8]
#
# If so, we're done.  If not, the tzinfo klasa jest insane, according to the
# assumptions we've made.  This also requires a bit of proof.  As before, let's
# compute the difference between the LHS oraz RHS of [8] (and skipping some of
# the justifications dla the kinds of substitutions we've done several times
# already):
#
#     diff' = x.n - (z'.n - z'.o) =           replacing z'.n via [7]
#             x.n  - (z.n + diff - z'.o) =    replacing diff via [6]
#             x.n - (z.n + x.n - (z.n - z.o) - z'.o) =
#             x.n - z.n - x.n + z.n - z.o + z'.o =    cancel x.n
#             - z.n + z.n - z.o + z'.o =              cancel z.n
#             - z.o + z'.o =                      #1 twice
#             -z.s - z.d + z'.s + z'.d =          z oraz z' have same tzinfo
#             z'.d - z.d
#
# So z' jest UTC-equivalent to x iff z'.d = z.d at this point.  If they are equal,
# we've found the UTC-equivalent so are done.  In fact, we stop przy [7] oraz
# zwróć z', nie bothering to compute z'.d.
#
# How could z.d oraz z'd differ?  z' = z + z.d [7], so merely moving z' by
# a dst() offset, oraz starting *from* a time already w DST (we know z.d != 0),
# would have to change the result dst() returns:  we start w DST, oraz moving
# a little further into it takes us out of DST.
#
# There isn't a sane case where this can happen.  The closest it gets jest at
# the end of DST, where there's an hour w UTC przy no spelling w a hybrid
# tzinfo class.  In US Eastern, that's 5:MM UTC = 0:MM EST = 1:MM EDT.  During
# that hour, on an Eastern clock 1:MM jest taken jako being w standard time (6:MM
# UTC) because the docs insist on that, but 0:MM jest taken jako being w daylight
# time (4:MM UTC).  There jest no local time mapping to 5:MM UTC.  The local
# clock jumps z 1:59 back to 1:00 again, oraz repeats the 1:MM hour w
# standard time.  Since that's what the local clock *does*, we want to map both
# UTC hours 5:MM oraz 6:MM to 1:MM Eastern.  The result jest ambiguous
# w local time, but so it goes -- it's the way the local clock works.
#
# When x = 5:MM UTC jest the input to this algorithm, x.o=0, y.o=-5 oraz y.d=0,
# so z=0:MM.  z.d=60 (minutes) then, so [5] doesn't hold oraz we keep going.
# z' = z + z.d = 1:MM then, oraz z'.d=0, oraz z'.d - z.d = -60 != 0 so [8]
# (correctly) concludes that z' jest nie UTC-equivalent to x.
#
# Because we know z.d said z was w daylight time (inaczej [5] would have held oraz
# we would have stopped then), oraz we know z.d != z'.d (inaczej [8] would have held
# oraz we have stopped then), oraz there are only 2 possible values dst() can
# zwróć w Eastern, it follows that z'.d must be 0 (which it jest w the example,
# but the reasoning doesn't depend on the example -- it depends on there being
# two possible dst() outcomes, one zero oraz the other non-zero).  Therefore
# z' must be w standard time, oraz jest the spelling we want w this case.
#
# Note again that z' jest nie UTC-equivalent jako far jako the hybrid tzinfo klasa jest
# concerned (because it takes z' jako being w standard time rather than the
# daylight time we intend here), but returning it gives the real-life "local
# clock repeats an hour" behavior when mapping the "unspellable" UTC hour into
# tz.
#
# When the input jest 6:MM, z=1:MM oraz z.d=0, oraz we stop at once, again with
# the 1:MM standard time spelling we want.
#
# So how can this przerwij?  One of the assumptions must be violated.  Two
# possibilities:
#
# 1) [2] effectively says that y.s jest invariant across all y belong to a given
#    time zone.  This isn't true if, dla political reasons albo continental drift,
#    a region decides to change its base offset z UTC.
#
# 2) There may be versions of "double daylight" time where the tail end of
#    the analysis gives up a step too early.  I haven't thought about that
#    enough to say.
#
# In any case, it's clear that the default fromutc() jest strong enough to handle
# "almost all" time zones:  so long jako the standard offset jest invariant, it
# doesn't matter jeżeli daylight time transition points change z year to year, albo
# jeżeli daylight time jest skipped w some years; it doesn't matter how large albo
# small dst() may get within its bounds; oraz it doesn't even matter jeżeli some
# perverse time zone returns a negative dst()).  So a przerwijing case must be
# pretty bizarre, oraz a tzinfo subclass can override fromutc() jeżeli it is.

spróbuj:
    z _datetime zaimportuj *
wyjąwszy ImportError:
    dalej
inaczej:
    # Clean up unused names
    usuń (_DAYNAMES, _DAYS_BEFORE_MONTH, _DAYS_IN_MONTH, _DI100Y, _DI400Y,
         _DI4Y, _EPOCH, _MAXORDINAL, _MONTHNAMES, _build_struct_time,
         _check_date_fields, _check_int_field, _check_time_fields,
         _check_tzinfo_arg, _check_tzname, _check_utc_offset, _cmp, _cmperror,
         _date_class, _days_before_month, _days_before_year, _days_in_month,
         _format_time, _is_leap, _isoweek1monday, _math, _ord2ymd,
         _time, _time_class, _tzinfo_class, _wrap_strftime, _ymd2ord)
    # XXX Since zaimportuj * above excludes names that start przy _,
    # docstring does nie get overwritten. In the future, it may be
    # appropriate to maintain a single module level docstring oraz
    # remove the following line.
    z _datetime zaimportuj __doc__
