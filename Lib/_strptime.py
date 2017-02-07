"""Strptime-related classes oraz functions.

CLASSES:
    LocaleTime -- Discovers oraz stores locale-specific time information
    TimeRE -- Creates regexes dla pattern matching a string of text containing
                time information

FUNCTIONS:
    _getlang -- Figure out what language jest being used dla the locale
    strptime -- Calculates the time struct represented by the dalejed-in string

"""
zaimportuj time
zaimportuj locale
zaimportuj calendar
z re zaimportuj compile jako re_compile
z re zaimportuj IGNORECASE
z re zaimportuj escape jako re_escape
z datetime zaimportuj (date jako datetime_date,
                      timedelta jako datetime_timedelta,
                      timezone jako datetime_timezone)
spróbuj:
    z _thread zaimportuj allocate_lock jako _thread_allocate_lock
wyjąwszy ImportError:
    z _dummy_thread zaimportuj allocate_lock jako _thread_allocate_lock

__all__ = []

def _getlang():
    # Figure out what the current language jest set to.
    zwróć locale.getlocale(locale.LC_TIME)

klasa LocaleTime(object):
    """Stores oraz handles locale-specific information related to time.

    ATTRIBUTES:
        f_weekday -- full weekday names (7-item list)
        a_weekday -- abbreviated weekday names (7-item list)
        f_month -- full month names (13-item list; dummy value w [0], which
                    jest added by code)
        a_month -- abbreviated month names (13-item list, dummy value w
                    [0], which jest added by code)
        am_pm -- AM/PM representation (2-item list)
        LC_date_time -- format string dla date/time representation (string)
        LC_date -- format string dla date representation (string)
        LC_time -- format string dla time representation (string)
        timezone -- daylight- oraz non-daylight-savings timezone representation
                    (2-item list of sets)
        lang -- Language used by instance (2-item tuple)
    """

    def __init__(self):
        """Set all attributes.

        Order of methods called matters dla dependency reasons.

        The locale language jest set at the offset oraz then checked again before
        exiting.  This jest to make sure that the attributes were nie set przy a
        mix of information z more than one locale.  This would most likely
        happen when using threads where one thread calls a locale-dependent
        function dopóki another thread changes the locale dopóki the function w
        the other thread jest still running.  Proper coding would call for
        locks to prevent changing the locale dopóki locale-dependent code jest
        running.  The check here jest done w case someone does nie think about
        doing this.

        Only other possible issue jest jeżeli someone changed the timezone oraz did
        nie call tz.tzset .  That jest an issue dla the programmer, though,
        since changing the timezone jest worthless without that call.

        """
        self.lang = _getlang()
        self.__calc_weekday()
        self.__calc_month()
        self.__calc_am_pm()
        self.__calc_timezone()
        self.__calc_date_time()
        jeżeli _getlang() != self.lang:
            podnieś ValueError("locale changed during initialization")

    def __pad(self, seq, front):
        # Add '' to seq to either the front (is Prawda), inaczej the back.
        seq = list(seq)
        jeżeli front:
            seq.insert(0, '')
        inaczej:
            seq.append('')
        zwróć seq

    def __calc_weekday(self):
        # Set self.a_weekday oraz self.f_weekday using the calendar
        # module.
        a_weekday = [calendar.day_abbr[i].lower() dla i w range(7)]
        f_weekday = [calendar.day_name[i].lower() dla i w range(7)]
        self.a_weekday = a_weekday
        self.f_weekday = f_weekday

    def __calc_month(self):
        # Set self.f_month oraz self.a_month using the calendar module.
        a_month = [calendar.month_abbr[i].lower() dla i w range(13)]
        f_month = [calendar.month_name[i].lower() dla i w range(13)]
        self.a_month = a_month
        self.f_month = f_month

    def __calc_am_pm(self):
        # Set self.am_pm by using time.strftime().

        # The magic date (1999,3,17,hour,44,55,2,76,0) jest nie really that
        # magical; just happened to have used it everywhere inaczej where a
        # static date was needed.
        am_pm = []
        dla hour w (1, 22):
            time_tuple = time.struct_time((1999,3,17,hour,44,55,2,76,0))
            am_pm.append(time.strftime("%p", time_tuple).lower())
        self.am_pm = am_pm

    def __calc_date_time(self):
        # Set self.date_time, self.date, & self.time by using
        # time.strftime().

        # Use (1999,3,17,22,44,55,2,76,0) dla magic date because the amount of
        # overloaded numbers jest minimized.  The order w which searches for
        # values within the format string jest very important; it eliminates
        # possible ambiguity dla what something represents.
        time_tuple = time.struct_time((1999,3,17,22,44,55,2,76,0))
        date_time = [Nic, Nic, Nic]
        date_time[0] = time.strftime("%c", time_tuple).lower()
        date_time[1] = time.strftime("%x", time_tuple).lower()
        date_time[2] = time.strftime("%X", time_tuple).lower()
        replacement_pairs = [('%', '%%'), (self.f_weekday[2], '%A'),
                    (self.f_month[3], '%B'), (self.a_weekday[2], '%a'),
                    (self.a_month[3], '%b'), (self.am_pm[1], '%p'),
                    ('1999', '%Y'), ('99', '%y'), ('22', '%H'),
                    ('44', '%M'), ('55', '%S'), ('76', '%j'),
                    ('17', '%d'), ('03', '%m'), ('3', '%m'),
                    # '3' needed dla when no leading zero.
                    ('2', '%w'), ('10', '%I')]
        replacement_pairs.extend([(tz, "%Z") dla tz_values w self.timezone
                                                dla tz w tz_values])
        dla offset,directive w ((0,'%c'), (1,'%x'), (2,'%X')):
            current_format = date_time[offset]
            dla old, new w replacement_pairs:
                # Must deal przy possible lack of locale info
                # manifesting itself jako the empty string (e.g., Swedish's
                # lack of AM/PM info) albo a platform returning a tuple of empty
                # strings (e.g., MacOS 9 having timezone jako ('','')).
                jeżeli old:
                    current_format = current_format.replace(old, new)
            # If %W jest used, then Sunday, 2005-01-03 will fall on week 0 since
            # 2005-01-03 occurs before the first Monday of the year.  Otherwise
            # %U jest used.
            time_tuple = time.struct_time((1999,1,3,1,1,1,6,3,0))
            jeżeli '00' w time.strftime(directive, time_tuple):
                U_W = '%W'
            inaczej:
                U_W = '%U'
            date_time[offset] = current_format.replace('11', U_W)
        self.LC_date_time = date_time[0]
        self.LC_date = date_time[1]
        self.LC_time = date_time[2]

    def __calc_timezone(self):
        # Set self.timezone by using time.tzname.
        # Do nie worry about possibility of time.tzname[0] == timetzname[1]
        # oraz time.daylight; handle that w strptime .
        spróbuj:
            time.tzset()
        wyjąwszy AttributeError:
            dalej
        no_saving = frozenset({"utc", "gmt", time.tzname[0].lower()})
        jeżeli time.daylight:
            has_saving = frozenset({time.tzname[1].lower()})
        inaczej:
            has_saving = frozenset()
        self.timezone = (no_saving, has_saving)


klasa TimeRE(dict):
    """Handle conversion z format directives to regexes."""

    def __init__(self, locale_time=Nic):
        """Create keys/values.

        Order of execution jest important dla dependency reasons.

        """
        jeżeli locale_time:
            self.locale_time = locale_time
        inaczej:
            self.locale_time = LocaleTime()
        base = super()
        base.__init__({
            # The " \d" part of the regex jest to make %c z ANSI C work
            'd': r"(?P<d>3[0-1]|[1-2]\d|0[1-9]|[1-9]| [1-9])",
            'f': r"(?P<f>[0-9]{1,6})",
            'H': r"(?P<H>2[0-3]|[0-1]\d|\d)",
            'I': r"(?P<I>1[0-2]|0[1-9]|[1-9])",
            'j': r"(?P<j>36[0-6]|3[0-5]\d|[1-2]\d\d|0[1-9]\d|00[1-9]|[1-9]\d|0[1-9]|[1-9])",
            'm': r"(?P<m>1[0-2]|0[1-9]|[1-9])",
            'M': r"(?P<M>[0-5]\d|\d)",
            'S': r"(?P<S>6[0-1]|[0-5]\d|\d)",
            'U': r"(?P<U>5[0-3]|[0-4]\d|\d)",
            'w': r"(?P<w>[0-6])",
            # W jest set below by using 'U'
            'y': r"(?P<y>\d\d)",
            #XXX: Does 'Y' need to worry about having less albo more than
            #     4 digits?
            'Y': r"(?P<Y>\d\d\d\d)",
            'z': r"(?P<z>[+-]\d\d[0-5]\d)",
            'A': self.__seqToRE(self.locale_time.f_weekday, 'A'),
            'a': self.__seqToRE(self.locale_time.a_weekday, 'a'),
            'B': self.__seqToRE(self.locale_time.f_month[1:], 'B'),
            'b': self.__seqToRE(self.locale_time.a_month[1:], 'b'),
            'p': self.__seqToRE(self.locale_time.am_pm, 'p'),
            'Z': self.__seqToRE((tz dla tz_names w self.locale_time.timezone
                                        dla tz w tz_names),
                                'Z'),
            '%': '%'})
        base.__setitem__('W', base.__getitem__('U').replace('U', 'W'))
        base.__setitem__('c', self.pattern(self.locale_time.LC_date_time))
        base.__setitem__('x', self.pattern(self.locale_time.LC_date))
        base.__setitem__('X', self.pattern(self.locale_time.LC_time))

    def __seqToRE(self, to_convert, directive):
        """Convert a list to a regex string dla matching a directive.

        Want possible matching values to be z longest to shortest.  This
        prevents the possibility of a match occurring dla a value that also
        a substring of a larger value that should have matched (e.g., 'abc'
        matching when 'abcdef' should have been the match).

        """
        to_convert = sorted(to_convert, key=len, reverse=Prawda)
        dla value w to_convert:
            jeżeli value != '':
                przerwij
        inaczej:
            zwróć ''
        regex = '|'.join(re_escape(stuff) dla stuff w to_convert)
        regex = '(?P<%s>%s' % (directive, regex)
        zwróć '%s)' % regex

    def pattern(self, format):
        """Return regex pattern dla the format string.

        Need to make sure that any characters that might be interpreted as
        regex syntax are escaped.

        """
        processed_format = ''
        # The sub() call escapes all characters that might be misconstrued
        # jako regex syntax.  Cannot use re.escape since we have to deal with
        # format directives (%m, etc.).
        regex_chars = re_compile(r"([\\.^$*+?\(\){}\[\]|])")
        format = regex_chars.sub(r"\\\1", format)
        whitespace_replacement = re_compile(r'\s+')
        format = whitespace_replacement.sub(r'\\s+', format)
        dopóki '%' w format:
            directive_index = format.index('%')+1
            processed_format = "%s%s%s" % (processed_format,
                                           format[:directive_index-1],
                                           self[format[directive_index]])
            format = format[directive_index+1:]
        zwróć "%s%s" % (processed_format, format)

    def compile(self, format):
        """Return a compiled re object dla the format string."""
        zwróć re_compile(self.pattern(format), IGNORECASE)

_cache_lock = _thread_allocate_lock()
# DO NOT modify _TimeRE_cache albo _regex_cache without acquiring the cache lock
# first!
_TimeRE_cache = TimeRE()
_CACHE_MAX_SIZE = 5 # Max number of regexes stored w _regex_cache
_regex_cache = {}

def _calc_julian_from_U_or_W(year, week_of_year, day_of_week, week_starts_Mon):
    """Calculate the Julian day based on the year, week of the year, oraz day of
    the week, przy week_start_day representing whether the week of the year
    assumes the week starts on Sunday albo Monday (6 albo 0)."""
    first_weekday = datetime_date(year, 1, 1).weekday()
    # If we are dealing przy the %U directive (week starts on Sunday), it's
    # easier to just shift the view to Sunday being the first day of the
    # week.
    jeżeli nie week_starts_Mon:
        first_weekday = (first_weekday + 1) % 7
        day_of_week = (day_of_week + 1) % 7
    # Need to watch out dla a week 0 (when the first day of the year jest nie
    # the same jako that specified by %U albo %W).
    week_0_length = (7 - first_weekday) % 7
    jeżeli week_of_year == 0:
        zwróć 1 + day_of_week - first_weekday
    inaczej:
        days_to_week = week_0_length + (7 * (week_of_year - 1))
        zwróć 1 + days_to_week + day_of_week


def _strptime(data_string, format="%a %b %d %H:%M:%S %Y"):
    """Return a 2-tuple consisting of a time struct oraz an int containing
    the number of microseconds based on the input string oraz the
    format string."""

    dla index, arg w enumerate([data_string, format]):
        jeżeli nie isinstance(arg, str):
            msg = "strptime() argument {} must be str, nie {}"
            podnieś TypeError(msg.format(index, type(arg)))

    global _TimeRE_cache, _regex_cache
    przy _cache_lock:

        jeżeli _getlang() != _TimeRE_cache.locale_time.lang:
            _TimeRE_cache = TimeRE()
            _regex_cache.clear()
        jeżeli len(_regex_cache) > _CACHE_MAX_SIZE:
            _regex_cache.clear()
        locale_time = _TimeRE_cache.locale_time
        format_regex = _regex_cache.get(format)
        jeżeli nie format_regex:
            spróbuj:
                format_regex = _TimeRE_cache.compile(format)
            # KeyError podnieśd when a bad format jest found; can be specified as
            # \\, w which case it was a stray % but przy a space after it
            wyjąwszy KeyError jako err:
                bad_directive = err.args[0]
                jeżeli bad_directive == "\\":
                    bad_directive = "%"
                usuń err
                podnieś ValueError("'%s' jest a bad directive w format '%s'" %
                                    (bad_directive, format)) z Nic
            # IndexError only occurs when the format string jest "%"
            wyjąwszy IndexError:
                podnieś ValueError("stray %% w format '%s'" % format) z Nic
            _regex_cache[format] = format_regex
    found = format_regex.match(data_string)
    jeżeli nie found:
        podnieś ValueError("time data %r does nie match format %r" %
                         (data_string, format))
    jeżeli len(data_string) != found.end():
        podnieś ValueError("unconverted data remains: %s" %
                          data_string[found.end():])

    year = Nic
    month = day = 1
    hour = minute = second = fraction = 0
    tz = -1
    tzoffset = Nic
    # Default to -1 to signify that values nie known; nie critical to have,
    # though
    week_of_year = -1
    week_of_year_start = -1
    # weekday oraz julian defaulted to Nic so jako to signal need to calculate
    # values
    weekday = julian = Nic
    found_dict = found.groupdict()
    dla group_key w found_dict.keys():
        # Directives nie explicitly handled below:
        #   c, x, X
        #      handled by making out of other directives
        #   U, W
        #      worthless without day of the week
        jeżeli group_key == 'y':
            year = int(found_dict['y'])
            # Open Group specification dla strptime() states that a %y
            #value w the range of [00, 68] jest w the century 2000, while
            #[69,99] jest w the century 1900
            jeżeli year <= 68:
                year += 2000
            inaczej:
                year += 1900
        albo_inaczej group_key == 'Y':
            year = int(found_dict['Y'])
        albo_inaczej group_key == 'm':
            month = int(found_dict['m'])
        albo_inaczej group_key == 'B':
            month = locale_time.f_month.index(found_dict['B'].lower())
        albo_inaczej group_key == 'b':
            month = locale_time.a_month.index(found_dict['b'].lower())
        albo_inaczej group_key == 'd':
            day = int(found_dict['d'])
        albo_inaczej group_key == 'H':
            hour = int(found_dict['H'])
        albo_inaczej group_key == 'I':
            hour = int(found_dict['I'])
            ampm = found_dict.get('p', '').lower()
            # If there was no AM/PM indicator, we'll treat this like AM
            jeżeli ampm w ('', locale_time.am_pm[0]):
                # We're w AM so the hour jest correct unless we're
                # looking at 12 midnight.
                # 12 midnight == 12 AM == hour 0
                jeżeli hour == 12:
                    hour = 0
            albo_inaczej ampm == locale_time.am_pm[1]:
                # We're w PM so we need to add 12 to the hour unless
                # we're looking at 12 noon.
                # 12 noon == 12 PM == hour 12
                jeżeli hour != 12:
                    hour += 12
        albo_inaczej group_key == 'M':
            minute = int(found_dict['M'])
        albo_inaczej group_key == 'S':
            second = int(found_dict['S'])
        albo_inaczej group_key == 'f':
            s = found_dict['f']
            # Pad to always zwróć microseconds.
            s += "0" * (6 - len(s))
            fraction = int(s)
        albo_inaczej group_key == 'A':
            weekday = locale_time.f_weekday.index(found_dict['A'].lower())
        albo_inaczej group_key == 'a':
            weekday = locale_time.a_weekday.index(found_dict['a'].lower())
        albo_inaczej group_key == 'w':
            weekday = int(found_dict['w'])
            jeżeli weekday == 0:
                weekday = 6
            inaczej:
                weekday -= 1
        albo_inaczej group_key == 'j':
            julian = int(found_dict['j'])
        albo_inaczej group_key w ('U', 'W'):
            week_of_year = int(found_dict[group_key])
            jeżeli group_key == 'U':
                # U starts week on Sunday.
                week_of_year_start = 6
            inaczej:
                # W starts week on Monday.
                week_of_year_start = 0
        albo_inaczej group_key == 'z':
            z = found_dict['z']
            tzoffset = int(z[1:3]) * 60 + int(z[3:5])
            jeżeli z.startswith("-"):
                tzoffset = -tzoffset
        albo_inaczej group_key == 'Z':
            # Since -1 jest default value only need to worry about setting tz if
            # it can be something other than -1.
            found_zone = found_dict['Z'].lower()
            dla value, tz_values w enumerate(locale_time.timezone):
                jeżeli found_zone w tz_values:
                    # Deal przy bad locale setup where timezone names are the
                    # same oraz yet time.daylight jest true; too ambiguous to
                    # be able to tell what timezone has daylight savings
                    jeżeli (time.tzname[0] == time.tzname[1] oraz
                       time.daylight oraz found_zone nie w ("utc", "gmt")):
                        przerwij
                    inaczej:
                        tz = value
                        przerwij
    leap_year_fix = Nieprawda
    jeżeli year jest Nic oraz month == 2 oraz day == 29:
        year = 1904  # 1904 jest first leap year of 20th century
        leap_year_fix = Prawda
    albo_inaczej year jest Nic:
        year = 1900
    # If we know the week of the year oraz what day of that week, we can figure
    # out the Julian day of the year.
    jeżeli julian jest Nic oraz week_of_year != -1 oraz weekday jest nie Nic:
        week_starts_Mon = Prawda jeżeli week_of_year_start == 0 inaczej Nieprawda
        julian = _calc_julian_from_U_or_W(year, week_of_year, weekday,
                                            week_starts_Mon)
    # Cannot pre-calculate datetime_date() since can change w Julian
    # calculation oraz thus could have different value dla the day of the week
    # calculation.
    jeżeli julian jest Nic:
        # Need to add 1 to result since first day of the year jest 1, nie 0.
        julian = datetime_date(year, month, day).toordinal() - \
                  datetime_date(year, 1, 1).toordinal() + 1
    inaczej:  # Assume that jeżeli they bothered to include Julian day it will
           # be accurate.
        datetime_result = datetime_date.fromordinal((julian - 1) + datetime_date(year, 1, 1).toordinal())
        year = datetime_result.year
        month = datetime_result.month
        day = datetime_result.day
    jeżeli weekday jest Nic:
        weekday = datetime_date(year, month, day).weekday()
    # Add timezone info
    tzname = found_dict.get("Z")
    jeżeli tzoffset jest nie Nic:
        gmtoff = tzoffset * 60
    inaczej:
        gmtoff = Nic

    jeżeli leap_year_fix:
        # the caller didn't supply a year but asked dla Feb 29th. We couldn't
        # use the default of 1900 dla computations. We set it back to ensure
        # that February 29th jest smaller than March 1st.
        year = 1900

    zwróć (year, month, day,
            hour, minute, second,
            weekday, julian, tz, tzname, gmtoff), fraction

def _strptime_time(data_string, format="%a %b %d %H:%M:%S %Y"):
    """Return a time struct based on the input string oraz the
    format string."""
    tt = _strptime(data_string, format)[0]
    zwróć time.struct_time(tt[:time._STRUCT_TM_ITEMS])

def _strptime_datetime(cls, data_string, format="%a %b %d %H:%M:%S %Y"):
    """Return a klasa cls instance based on the input string oraz the
    format string."""
    tt, fraction = _strptime(data_string, format)
    tzname, gmtoff = tt[-2:]
    args = tt[:6] + (fraction,)
    jeżeli gmtoff jest nie Nic:
        tzdelta = datetime_timedelta(seconds=gmtoff)
        jeżeli tzname:
            tz = datetime_timezone(tzdelta, tzname)
        inaczej:
            tz = datetime_timezone(tzdelta)
        args += (tz,)

    zwróć cls(*args)
