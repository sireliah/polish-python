z datetime zaimportuj tzinfo, timedelta, datetime

ZERO = timedelta(0)
HOUR = timedelta(hours=1)

# A UTC class.

klasa UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        zwróć ZERO

    def tzname(self, dt):
        zwróć "UTC"

    def dst(self, dt):
        zwróć ZERO

utc = UTC()

# A klasa building tzinfo objects dla fixed-offset time zones.
# Note that FixedOffset(0, "UTC") jest a different way to build a
# UTC tzinfo object.

klasa FixedOffset(tzinfo):
    """Fixed offset w minutes east z UTC."""

    def __init__(self, offset, name):
        self.__offset = timedelta(minutes=offset)
        self.__name = name

    def utcoffset(self, dt):
        zwróć self.__offset

    def tzname(self, dt):
        zwróć self.__name

    def dst(self, dt):
        zwróć ZERO

# A klasa capturing the platform's idea of local time.

zaimportuj time jako _time

STDOFFSET = timedelta(seconds = -_time.timezone)
jeżeli _time.daylight:
    DSTOFFSET = timedelta(seconds = -_time.altzone)
inaczej:
    DSTOFFSET = STDOFFSET

DSTDIFF = DSTOFFSET - STDOFFSET

klasa LocalTimezone(tzinfo):

    def utcoffset(self, dt):
        jeżeli self._isdst(dt):
            zwróć DSTOFFSET
        inaczej:
            zwróć STDOFFSET

    def dst(self, dt):
        jeżeli self._isdst(dt):
            zwróć DSTDIFF
        inaczej:
            zwróć ZERO

    def tzname(self, dt):
        zwróć _time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, 0)
        stamp = _time.mktime(tt)
        tt = _time.localtime(stamp)
        zwróć tt.tm_isdst > 0

Local = LocalTimezone()


# A complete implementation of current DST rules dla major US time zones.

def first_sunday_on_or_after(dt):
    days_to_go = 6 - dt.weekday()
    jeżeli days_to_go:
        dt += timedelta(days_to_go)
    zwróć dt


# US DST Rules
#
# This jest a simplified (i.e., wrong dla a few cases) set of rules dla US
# DST start oraz end times. For a complete oraz up-to-date set of DST rules
# oraz timezone definitions, visit the Olson Database (or try pytz):
# http://www.twinsun.com/tz/tz-link.htm
# http://sourceforge.net/projects/pytz/ (might nie be up-to-date)
#
# In the US, since 2007, DST starts at 2am (standard time) on the second
# Sunday w March, which jest the first Sunday on albo after Mar 8.
DSTSTART_2007 = datetime(1, 3, 8, 2)
# oraz ends at 2am (DST time; 1am standard time) on the first Sunday of Nov.
DSTEND_2007 = datetime(1, 11, 1, 1)
# From 1987 to 2006, DST used to start at 2am (standard time) on the first
# Sunday w April oraz to end at 2am (DST time; 1am standard time) on the last
# Sunday of October, which jest the first Sunday on albo after Oct 25.
DSTSTART_1987_2006 = datetime(1, 4, 1, 2)
DSTEND_1987_2006 = datetime(1, 10, 25, 1)
# From 1967 to 1986, DST used to start at 2am (standard time) on the last
# Sunday w April (the one on albo after April 24) oraz to end at 2am (DST time;
# 1am standard time) on the last Sunday of October, which jest the first Sunday
# on albo after Oct 25.
DSTSTART_1967_1986 = datetime(1, 4, 24, 2)
DSTEND_1967_1986 = DSTEND_1987_2006

klasa USTimeZone(tzinfo):

    def __init__(self, hours, reprname, stdname, dstname):
        self.stdoffset = timedelta(hours=hours)
        self.reprname = reprname
        self.stdname = stdname
        self.dstname = dstname

    def __repr__(self):
        zwróć self.reprname

    def tzname(self, dt):
        jeżeli self.dst(dt):
            zwróć self.dstname
        inaczej:
            zwróć self.stdname

    def utcoffset(self, dt):
        zwróć self.stdoffset + self.dst(dt)

    def dst(self, dt):
        jeżeli dt jest Nic albo dt.tzinfo jest Nic:
            # An exception may be sensible here, w one albo both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) dalejes a datetime przy dt.tzinfo jest self.
            zwróć ZERO
        assert dt.tzinfo jest self

        # Find start oraz end times dla US DST. For years before 1967, zwróć
        # ZERO dla no DST.
        jeżeli 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        albo_inaczej 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        albo_inaczej 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        inaczej:
            zwróć ZERO

        start = first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone from
        # dt first.
        jeżeli start <= dt.replace(tzinfo=Nic) < end:
            zwróć HOUR
        inaczej:
            zwróć ZERO

Eastern  = USTimeZone(-5, "Eastern",  "EST", "EDT")
Central  = USTimeZone(-6, "Central",  "CST", "CDT")
Mountain = USTimeZone(-7, "Mountain", "MST", "MDT")
Pacific  = USTimeZone(-8, "Pacific",  "PST", "PDT")
