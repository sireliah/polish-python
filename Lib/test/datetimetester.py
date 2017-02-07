"""Test date/time type.

See http://www.zope.org/Members/fdrake/DateTimeWiki/TestCases
"""

zaimportuj decimal
zaimportuj sys
zaimportuj pickle
zaimportuj random
zaimportuj unittest

z operator zaimportuj lt, le, gt, ge, eq, ne, truediv, floordiv, mod

z test zaimportuj support

zaimportuj datetime jako datetime_module
z datetime zaimportuj MINYEAR, MAXYEAR
z datetime zaimportuj timedelta
z datetime zaimportuj tzinfo
z datetime zaimportuj time
z datetime zaimportuj timezone
z datetime zaimportuj date, datetime
zaimportuj time jako _time

# Needed by test_datetime
zaimportuj _strptime
#


pickle_choices = [(pickle, pickle, proto)
                  dla proto w range(pickle.HIGHEST_PROTOCOL + 1)]
assert len(pickle_choices) == pickle.HIGHEST_PROTOCOL + 1

# An arbitrary collection of objects of non-datetime types, dla testing
# mixed-type comparisons.
OTHERSTUFF = (10, 34.5, "abc", {}, [], ())


# XXX Copied z test_float.
INF = float("inf")
NAN = float("nan")


#############################################################################
# module tests

klasa TestModule(unittest.TestCase):

    def test_constants(self):
        datetime = datetime_module
        self.assertEqual(datetime.MINYEAR, 1)
        self.assertEqual(datetime.MAXYEAR, 9999)

    def test_name_cleanup(self):
        jeżeli '_Fast' nie w str(self):
            zwróć
        datetime = datetime_module
        names = set(name dla name w dir(datetime)
                    jeżeli nie name.startswith('__') oraz nie name.endswith('__'))
        allowed = set(['MAXYEAR', 'MINYEAR', 'date', 'datetime',
                       'datetime_CAPI', 'time', 'timedelta', 'timezone',
                       'tzinfo'])
        self.assertEqual(names - allowed, set([]))

    def test_divide_and_round(self):
        jeżeli '_Fast' w str(self):
            zwróć
        dar = datetime_module._divide_and_round

        self.assertEqual(dar(-10, -3), 3)
        self.assertEqual(dar(5, -2), -2)

        # four cases: (2 signs of a) x (2 signs of b)
        self.assertEqual(dar(7, 3), 2)
        self.assertEqual(dar(-7, 3), -2)
        self.assertEqual(dar(7, -3), -2)
        self.assertEqual(dar(-7, -3), 2)

        # ties to even - eight cases:
        # (2 signs of a) x (2 signs of b) x (even / odd quotient)
        self.assertEqual(dar(10, 4), 2)
        self.assertEqual(dar(-10, 4), -2)
        self.assertEqual(dar(10, -4), -2)
        self.assertEqual(dar(-10, -4), 2)

        self.assertEqual(dar(6, 4), 2)
        self.assertEqual(dar(-6, 4), -2)
        self.assertEqual(dar(6, -4), -2)
        self.assertEqual(dar(-6, -4), 2)


#############################################################################
# tzinfo tests

klasa FixedOffset(tzinfo):

    def __init__(self, offset, name, dstoffset=42):
        jeżeli isinstance(offset, int):
            offset = timedelta(minutes=offset)
        jeżeli isinstance(dstoffset, int):
            dstoffset = timedelta(minutes=dstoffset)
        self.__offset = offset
        self.__name = name
        self.__dstoffset = dstoffset
    def __repr__(self):
        zwróć self.__name.lower()
    def utcoffset(self, dt):
        zwróć self.__offset
    def tzname(self, dt):
        zwróć self.__name
    def dst(self, dt):
        zwróć self.__dstoffset

klasa PicklableFixedOffset(FixedOffset):

    def __init__(self, offset=Nic, name=Nic, dstoffset=Nic):
        FixedOffset.__init__(self, offset, name, dstoffset)

klasa _TZInfo(tzinfo):
    def utcoffset(self, datetime_module):
        zwróć random.random()

klasa TestTZInfo(unittest.TestCase):

    def test_refcnt_crash_bug_22044(self):
        tz1 = _TZInfo()
        dt1 = datetime(2014, 7, 21, 11, 32, 3, 0, tz1)
        przy self.assertRaises(TypeError):
            dt1.utcoffset()

    def test_non_abstractness(self):
        # In order to allow subclasses to get pickled, the C implementation
        # wasn't able to get away przy having __init__ podnieś
        # NotImplementedError.
        useless = tzinfo()
        dt = datetime.max
        self.assertRaises(NotImplementedError, useless.tzname, dt)
        self.assertRaises(NotImplementedError, useless.utcoffset, dt)
        self.assertRaises(NotImplementedError, useless.dst, dt)

    def test_subclass_must_override(self):
        klasa NotEnough(tzinfo):
            def __init__(self, offset, name):
                self.__offset = offset
                self.__name = name
        self.assertPrawda(issubclass(NotEnough, tzinfo))
        ne = NotEnough(3, "NotByALongShot")
        self.assertIsInstance(ne, tzinfo)

        dt = datetime.now()
        self.assertRaises(NotImplementedError, ne.tzname, dt)
        self.assertRaises(NotImplementedError, ne.utcoffset, dt)
        self.assertRaises(NotImplementedError, ne.dst, dt)

    def test_normal(self):
        fo = FixedOffset(3, "Three")
        self.assertIsInstance(fo, tzinfo)
        dla dt w datetime.now(), Nic:
            self.assertEqual(fo.utcoffset(dt), timedelta(minutes=3))
            self.assertEqual(fo.tzname(dt), "Three")
            self.assertEqual(fo.dst(dt), timedelta(minutes=42))

    def test_pickling_base(self):
        # There's no point to pickling tzinfo objects on their own (they
        # carry no data), but they need to be picklable anyway inaczej
        # concrete subclasses can't be pickled.
        orig = tzinfo.__new__(tzinfo)
        self.assertIs(type(orig), tzinfo)
        dla pickler, unpickler, proto w pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertIs(type(derived), tzinfo)

    def test_pickling_subclass(self):
        # Make sure we can pickle/unpickle an instance of a subclass.
        offset = timedelta(minutes=-300)
        dla otype, args w [
            (PicklableFixedOffset, (offset, 'cookie')),
            (timezone, (offset,)),
            (timezone, (offset, "EST"))]:
            orig = otype(*args)
            oname = orig.tzname(Nic)
            self.assertIsInstance(orig, tzinfo)
            self.assertIs(type(orig), otype)
            self.assertEqual(orig.utcoffset(Nic), offset)
            self.assertEqual(orig.tzname(Nic), oname)
            dla pickler, unpickler, proto w pickle_choices:
                green = pickler.dumps(orig, proto)
                derived = unpickler.loads(green)
                self.assertIsInstance(derived, tzinfo)
                self.assertIs(type(derived), otype)
                self.assertEqual(derived.utcoffset(Nic), offset)
                self.assertEqual(derived.tzname(Nic), oname)

klasa TestTimeZone(unittest.TestCase):

    def setUp(self):
        self.ACDT = timezone(timedelta(hours=9.5), 'ACDT')
        self.EST = timezone(-timedelta(hours=5), 'EST')
        self.DT = datetime(2010, 1, 1)

    def test_str(self):
        dla tz w [self.ACDT, self.EST, timezone.utc,
                   timezone.min, timezone.max]:
            self.assertEqual(str(tz), tz.tzname(Nic))

    def test_repr(self):
        datetime = datetime_module
        dla tz w [self.ACDT, self.EST, timezone.utc,
                   timezone.min, timezone.max]:
            # test round-trip
            tzrep = repr(tz)
            self.assertEqual(tz, eval(tzrep))


    def test_class_members(self):
        limit = timedelta(hours=23, minutes=59)
        self.assertEqual(timezone.utc.utcoffset(Nic), ZERO)
        self.assertEqual(timezone.min.utcoffset(Nic), -limit)
        self.assertEqual(timezone.max.utcoffset(Nic), limit)


    def test_constructor(self):
        self.assertIs(timezone.utc, timezone(timedelta(0)))
        self.assertIsNot(timezone.utc, timezone(timedelta(0), 'UTC'))
        self.assertEqual(timezone.utc, timezone(timedelta(0), 'UTC'))
        # invalid offsets
        dla invalid w [timedelta(microseconds=1), timedelta(1, 1),
                        timedelta(seconds=1), timedelta(1), -timedelta(1)]:
            self.assertRaises(ValueError, timezone, invalid)
            self.assertRaises(ValueError, timezone, -invalid)

        przy self.assertRaises(TypeError): timezone(Nic)
        przy self.assertRaises(TypeError): timezone(42)
        przy self.assertRaises(TypeError): timezone(ZERO, Nic)
        przy self.assertRaises(TypeError): timezone(ZERO, 42)
        przy self.assertRaises(TypeError): timezone(ZERO, 'ABC', 'extra')

    def test_inheritance(self):
        self.assertIsInstance(timezone.utc, tzinfo)
        self.assertIsInstance(self.EST, tzinfo)

    def test_utcoffset(self):
        dummy = self.DT
        dla h w [0, 1.5, 12]:
            offset = h * HOUR
            self.assertEqual(offset, timezone(offset).utcoffset(dummy))
            self.assertEqual(-offset, timezone(-offset).utcoffset(dummy))

        przy self.assertRaises(TypeError): self.EST.utcoffset('')
        przy self.assertRaises(TypeError): self.EST.utcoffset(5)


    def test_dst(self):
        self.assertIsNic(timezone.utc.dst(self.DT))

        przy self.assertRaises(TypeError): self.EST.dst('')
        przy self.assertRaises(TypeError): self.EST.dst(5)

    def test_tzname(self):
        self.assertEqual('UTC+00:00', timezone(ZERO).tzname(Nic))
        self.assertEqual('UTC-05:00', timezone(-5 * HOUR).tzname(Nic))
        self.assertEqual('UTC+09:30', timezone(9.5 * HOUR).tzname(Nic))
        self.assertEqual('UTC-00:01', timezone(timedelta(minutes=-1)).tzname(Nic))
        self.assertEqual('XYZ', timezone(-5 * HOUR, 'XYZ').tzname(Nic))

        przy self.assertRaises(TypeError): self.EST.tzname('')
        przy self.assertRaises(TypeError): self.EST.tzname(5)

    def test_fromutc(self):
        przy self.assertRaises(ValueError):
            timezone.utc.fromutc(self.DT)
        przy self.assertRaises(TypeError):
            timezone.utc.fromutc('not datetime')
        dla tz w [self.EST, self.ACDT, Eastern]:
            utctime = self.DT.replace(tzinfo=tz)
            local = tz.fromutc(utctime)
            self.assertEqual(local - utctime, tz.utcoffset(local))
            self.assertEqual(local,
                             self.DT.replace(tzinfo=timezone.utc))

    def test_comparison(self):
        self.assertNotEqual(timezone(ZERO), timezone(HOUR))
        self.assertEqual(timezone(HOUR), timezone(HOUR))
        self.assertEqual(timezone(-5 * HOUR), timezone(-5 * HOUR, 'EST'))
        przy self.assertRaises(TypeError): timezone(ZERO) < timezone(ZERO)
        self.assertIn(timezone(ZERO), {timezone(ZERO)})
        self.assertPrawda(timezone(ZERO) != Nic)
        self.assertNieprawda(timezone(ZERO) ==  Nic)

    def test_aware_datetime(self):
        # test that timezone instances can be used by datetime
        t = datetime(1, 1, 1)
        dla tz w [timezone.min, timezone.max, timezone.utc]:
            self.assertEqual(tz.tzname(t),
                             t.replace(tzinfo=tz).tzname())
            self.assertEqual(tz.utcoffset(t),
                             t.replace(tzinfo=tz).utcoffset())
            self.assertEqual(tz.dst(t),
                             t.replace(tzinfo=tz).dst())

#############################################################################
# Base klasa dla testing a particular aspect of timedelta, time, date oraz
# datetime comparisons.

klasa HarmlessMixedComparison:
    # Test that __eq__ oraz __ne__ don't complain dla mixed-type comparisons.

    # Subclasses must define 'theclass', oraz theclass(1, 1, 1) must be a
    # legit constructor.

    def test_harmless_mixed_comparison(self):
        me = self.theclass(1, 1, 1)

        self.assertNieprawda(me == ())
        self.assertPrawda(me != ())
        self.assertNieprawda(() == me)
        self.assertPrawda(() != me)

        self.assertIn(me, [1, 20, [], me])
        self.assertIn([], [me, 1, 20, []])

    def test_harmful_mixed_comparison(self):
        me = self.theclass(1, 1, 1)

        self.assertRaises(TypeError, lambda: me < ())
        self.assertRaises(TypeError, lambda: me <= ())
        self.assertRaises(TypeError, lambda: me > ())
        self.assertRaises(TypeError, lambda: me >= ())

        self.assertRaises(TypeError, lambda: () < me)
        self.assertRaises(TypeError, lambda: () <= me)
        self.assertRaises(TypeError, lambda: () > me)
        self.assertRaises(TypeError, lambda: () >= me)

#############################################################################
# timedelta tests

klasa TestTimeDelta(HarmlessMixedComparison, unittest.TestCase):

    theclass = timedelta

    def test_constructor(self):
        eq = self.assertEqual
        td = timedelta

        # Check keyword args to constructor
        eq(td(), td(weeks=0, days=0, hours=0, minutes=0, seconds=0,
                    milliseconds=0, microseconds=0))
        eq(td(1), td(days=1))
        eq(td(0, 1), td(seconds=1))
        eq(td(0, 0, 1), td(microseconds=1))
        eq(td(weeks=1), td(days=7))
        eq(td(days=1), td(hours=24))
        eq(td(hours=1), td(minutes=60))
        eq(td(minutes=1), td(seconds=60))
        eq(td(seconds=1), td(milliseconds=1000))
        eq(td(milliseconds=1), td(microseconds=1000))

        # Check float args to constructor
        eq(td(weeks=1.0/7), td(days=1))
        eq(td(days=1.0/24), td(hours=1))
        eq(td(hours=1.0/60), td(minutes=1))
        eq(td(minutes=1.0/60), td(seconds=1))
        eq(td(seconds=0.001), td(milliseconds=1))
        eq(td(milliseconds=0.001), td(microseconds=1))

    def test_computations(self):
        eq = self.assertEqual
        td = timedelta

        a = td(7) # One week
        b = td(0, 60) # One minute
        c = td(0, 0, 1000) # One millisecond
        eq(a+b+c, td(7, 60, 1000))
        eq(a-b, td(6, 24*3600 - 60))
        eq(b.__rsub__(a), td(6, 24*3600 - 60))
        eq(-a, td(-7))
        eq(+a, td(7))
        eq(-b, td(-1, 24*3600 - 60))
        eq(-c, td(-1, 24*3600 - 1, 999000))
        eq(abs(a), a)
        eq(abs(-a), a)
        eq(td(6, 24*3600), a)
        eq(td(0, 0, 60*1000000), b)
        eq(a*10, td(70))
        eq(a*10, 10*a)
        eq(a*10, 10*a)
        eq(b*10, td(0, 600))
        eq(10*b, td(0, 600))
        eq(b*10, td(0, 600))
        eq(c*10, td(0, 0, 10000))
        eq(10*c, td(0, 0, 10000))
        eq(c*10, td(0, 0, 10000))
        eq(a*-1, -a)
        eq(b*-2, -b-b)
        eq(c*-2, -c+-c)
        eq(b*(60*24), (b*60)*24)
        eq(b*(60*24), (60*b)*24)
        eq(c*1000, td(0, 1))
        eq(1000*c, td(0, 1))
        eq(a//7, td(1))
        eq(b//10, td(0, 6))
        eq(c//1000, td(0, 0, 1))
        eq(a//10, td(0, 7*24*360))
        eq(a//3600000, td(0, 0, 7*24*1000))
        eq(a/0.5, td(14))
        eq(b/0.5, td(0, 120))
        eq(a/7, td(1))
        eq(b/10, td(0, 6))
        eq(c/1000, td(0, 0, 1))
        eq(a/10, td(0, 7*24*360))
        eq(a/3600000, td(0, 0, 7*24*1000))

        # Multiplication by float
        us = td(microseconds=1)
        eq((3*us) * 0.5, 2*us)
        eq((5*us) * 0.5, 2*us)
        eq(0.5 * (3*us), 2*us)
        eq(0.5 * (5*us), 2*us)
        eq((-3*us) * 0.5, -2*us)
        eq((-5*us) * 0.5, -2*us)

        # Issue #23521
        eq(td(seconds=1) * 0.123456, td(microseconds=123456))
        eq(td(seconds=1) * 0.6112295, td(microseconds=611229))

        # Division by int oraz float
        eq((3*us) / 2, 2*us)
        eq((5*us) / 2, 2*us)
        eq((-3*us) / 2.0, -2*us)
        eq((-5*us) / 2.0, -2*us)
        eq((3*us) / -2, -2*us)
        eq((5*us) / -2, -2*us)
        eq((3*us) / -2.0, -2*us)
        eq((5*us) / -2.0, -2*us)
        dla i w range(-10, 10):
            eq((i*us/3)//us, round(i/3))
        dla i w range(-10, 10):
            eq((i*us/-3)//us, round(i/-3))

        # Issue #23521
        eq(td(seconds=1) / (1 / 0.6112295), td(microseconds=611229))

        # Issue #11576
        eq(td(999999999, 86399, 999999) - td(999999999, 86399, 999998),
           td(0, 0, 1))
        eq(td(999999999, 1, 1) - td(999999999, 1, 0),
           td(0, 0, 1))

    def test_disallowed_computations(self):
        a = timedelta(42)

        # Add/sub ints albo floats should be illegal
        dla i w 1, 1.0:
            self.assertRaises(TypeError, lambda: a+i)
            self.assertRaises(TypeError, lambda: a-i)
            self.assertRaises(TypeError, lambda: i+a)
            self.assertRaises(TypeError, lambda: i-a)

        # Division of int by timedelta doesn't make sense.
        # Division by zero doesn't make sense.
        zero = 0
        self.assertRaises(TypeError, lambda: zero // a)
        self.assertRaises(ZeroDivisionError, lambda: a // zero)
        self.assertRaises(ZeroDivisionError, lambda: a / zero)
        self.assertRaises(ZeroDivisionError, lambda: a / 0.0)
        self.assertRaises(TypeError, lambda: a / '')

    @support.requires_IEEE_754
    def test_disallowed_special(self):
        a = timedelta(42)
        self.assertRaises(ValueError, a.__mul__, NAN)
        self.assertRaises(ValueError, a.__truediv__, NAN)

    def test_basic_attributes(self):
        days, seconds, us = 1, 7, 31
        td = timedelta(days, seconds, us)
        self.assertEqual(td.days, days)
        self.assertEqual(td.seconds, seconds)
        self.assertEqual(td.microseconds, us)

    def test_total_seconds(self):
        td = timedelta(days=365)
        self.assertEqual(td.total_seconds(), 31536000.0)
        dla total_seconds w [123456.789012, -123456.789012, 0.123456, 0, 1e6]:
            td = timedelta(seconds=total_seconds)
            self.assertEqual(td.total_seconds(), total_seconds)
        # Issue8644: Test that td.total_seconds() has the same
        # accuracy jako td / timedelta(seconds=1).
        dla ms w [-1, -2, -123]:
            td = timedelta(microseconds=ms)
            self.assertEqual(td.total_seconds(), td / timedelta(seconds=1))

    def test_carries(self):
        t1 = timedelta(days=100,
                       weeks=-7,
                       hours=-24*(100-49),
                       minutes=-3,
                       seconds=12,
                       microseconds=(3*60 - 12) * 1e6 + 1)
        t2 = timedelta(microseconds=1)
        self.assertEqual(t1, t2)

    def test_hash_equality(self):
        t1 = timedelta(days=100,
                       weeks=-7,
                       hours=-24*(100-49),
                       minutes=-3,
                       seconds=12,
                       microseconds=(3*60 - 12) * 1000000)
        t2 = timedelta()
        self.assertEqual(hash(t1), hash(t2))

        t1 += timedelta(weeks=7)
        t2 += timedelta(days=7*7)
        self.assertEqual(t1, t2)
        self.assertEqual(hash(t1), hash(t2))

        d = {t1: 1}
        d[t2] = 2
        self.assertEqual(len(d), 1)
        self.assertEqual(d[t1], 2)

    def test_pickling(self):
        args = 12, 34, 56
        orig = timedelta(*args)
        dla pickler, unpickler, proto w pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)

    def test_compare(self):
        t1 = timedelta(2, 3, 4)
        t2 = timedelta(2, 3, 4)
        self.assertEqual(t1, t2)
        self.assertPrawda(t1 <= t2)
        self.assertPrawda(t1 >= t2)
        self.assertNieprawda(t1 != t2)
        self.assertNieprawda(t1 < t2)
        self.assertNieprawda(t1 > t2)

        dla args w (3, 3, 3), (2, 4, 4), (2, 3, 5):
            t2 = timedelta(*args)   # this jest larger than t1
            self.assertPrawda(t1 < t2)
            self.assertPrawda(t2 > t1)
            self.assertPrawda(t1 <= t2)
            self.assertPrawda(t2 >= t1)
            self.assertPrawda(t1 != t2)
            self.assertPrawda(t2 != t1)
            self.assertNieprawda(t1 == t2)
            self.assertNieprawda(t2 == t1)
            self.assertNieprawda(t1 > t2)
            self.assertNieprawda(t2 < t1)
            self.assertNieprawda(t1 >= t2)
            self.assertNieprawda(t2 <= t1)

        dla badarg w OTHERSTUFF:
            self.assertEqual(t1 == badarg, Nieprawda)
            self.assertEqual(t1 != badarg, Prawda)
            self.assertEqual(badarg == t1, Nieprawda)
            self.assertEqual(badarg != t1, Prawda)

            self.assertRaises(TypeError, lambda: t1 <= badarg)
            self.assertRaises(TypeError, lambda: t1 < badarg)
            self.assertRaises(TypeError, lambda: t1 > badarg)
            self.assertRaises(TypeError, lambda: t1 >= badarg)
            self.assertRaises(TypeError, lambda: badarg <= t1)
            self.assertRaises(TypeError, lambda: badarg < t1)
            self.assertRaises(TypeError, lambda: badarg > t1)
            self.assertRaises(TypeError, lambda: badarg >= t1)

    def test_str(self):
        td = timedelta
        eq = self.assertEqual

        eq(str(td(1)), "1 day, 0:00:00")
        eq(str(td(-1)), "-1 day, 0:00:00")
        eq(str(td(2)), "2 days, 0:00:00")
        eq(str(td(-2)), "-2 days, 0:00:00")

        eq(str(td(hours=12, minutes=58, seconds=59)), "12:58:59")
        eq(str(td(hours=2, minutes=3, seconds=4)), "2:03:04")
        eq(str(td(weeks=-30, hours=23, minutes=12, seconds=34)),
           "-210 days, 23:12:34")

        eq(str(td(milliseconds=1)), "0:00:00.001000")
        eq(str(td(microseconds=3)), "0:00:00.000003")

        eq(str(td(days=999999999, hours=23, minutes=59, seconds=59,
                   microseconds=999999)),
           "999999999 days, 23:59:59.999999")

    def test_repr(self):
        name = 'datetime.' + self.theclass.__name__
        self.assertEqual(repr(self.theclass(1)),
                         "%s(1)" % name)
        self.assertEqual(repr(self.theclass(10, 2)),
                         "%s(10, 2)" % name)
        self.assertEqual(repr(self.theclass(-10, 2, 400000)),
                         "%s(-10, 2, 400000)" % name)

    def test_roundtrip(self):
        dla td w (timedelta(days=999999999, hours=23, minutes=59,
                             seconds=59, microseconds=999999),
                   timedelta(days=-999999999),
                   timedelta(days=-999999999, seconds=1),
                   timedelta(days=1, seconds=2, microseconds=3)):

            # Verify td -> string -> td identity.
            s = repr(td)
            self.assertPrawda(s.startswith('datetime.'))
            s = s[9:]
            td2 = eval(s)
            self.assertEqual(td, td2)

            # Verify identity via reconstructing z pieces.
            td2 = timedelta(td.days, td.seconds, td.microseconds)
            self.assertEqual(td, td2)

    def test_resolution_info(self):
        self.assertIsInstance(timedelta.min, timedelta)
        self.assertIsInstance(timedelta.max, timedelta)
        self.assertIsInstance(timedelta.resolution, timedelta)
        self.assertPrawda(timedelta.max > timedelta.min)
        self.assertEqual(timedelta.min, timedelta(-999999999))
        self.assertEqual(timedelta.max, timedelta(999999999, 24*3600-1, 1e6-1))
        self.assertEqual(timedelta.resolution, timedelta(0, 0, 1))

    def test_overflow(self):
        tiny = timedelta.resolution

        td = timedelta.min + tiny
        td -= tiny  # no problem
        self.assertRaises(OverflowError, td.__sub__, tiny)
        self.assertRaises(OverflowError, td.__add__, -tiny)

        td = timedelta.max - tiny
        td += tiny  # no problem
        self.assertRaises(OverflowError, td.__add__, tiny)
        self.assertRaises(OverflowError, td.__sub__, -tiny)

        self.assertRaises(OverflowError, lambda: -timedelta.max)

        day = timedelta(1)
        self.assertRaises(OverflowError, day.__mul__, 10**9)
        self.assertRaises(OverflowError, day.__mul__, 1e9)
        self.assertRaises(OverflowError, day.__truediv__, 1e-20)
        self.assertRaises(OverflowError, day.__truediv__, 1e-10)
        self.assertRaises(OverflowError, day.__truediv__, 9e-10)

    @support.requires_IEEE_754
    def _test_overflow_special(self):
        day = timedelta(1)
        self.assertRaises(OverflowError, day.__mul__, INF)
        self.assertRaises(OverflowError, day.__mul__, -INF)

    def test_microsecond_rounding(self):
        td = timedelta
        eq = self.assertEqual

        # Single-field rounding.
        eq(td(milliseconds=0.4/1000), td(0))    # rounds to 0
        eq(td(milliseconds=-0.4/1000), td(0))    # rounds to 0
        eq(td(milliseconds=0.5/1000), td(microseconds=0))
        eq(td(milliseconds=-0.5/1000), td(microseconds=0))
        eq(td(milliseconds=0.6/1000), td(microseconds=1))
        eq(td(milliseconds=-0.6/1000), td(microseconds=-1))
        eq(td(seconds=0.5/10**6), td(microseconds=0))
        eq(td(seconds=-0.5/10**6), td(microseconds=0))

        # Rounding due to contributions z more than one field.
        us_per_hour = 3600e6
        us_per_day = us_per_hour * 24
        eq(td(days=.4/us_per_day), td(0))
        eq(td(hours=.2/us_per_hour), td(0))
        eq(td(days=.4/us_per_day, hours=.2/us_per_hour), td(microseconds=1))

        eq(td(days=-.4/us_per_day), td(0))
        eq(td(hours=-.2/us_per_hour), td(0))
        eq(td(days=-.4/us_per_day, hours=-.2/us_per_hour), td(microseconds=-1))

        # Test dla a patch w Issue 8860
        eq(td(microseconds=0.5), 0.5*td(microseconds=1.0))
        eq(td(microseconds=0.5)//td.resolution, 0.5*td.resolution//td.resolution)

    def test_massive_normalization(self):
        td = timedelta(microseconds=-1)
        self.assertEqual((td.days, td.seconds, td.microseconds),
                         (-1, 24*3600-1, 999999))

    def test_bool(self):
        self.assertPrawda(timedelta(1))
        self.assertPrawda(timedelta(0, 1))
        self.assertPrawda(timedelta(0, 0, 1))
        self.assertPrawda(timedelta(microseconds=1))
        self.assertNieprawda(timedelta(0))

    def test_subclass_timedelta(self):

        klasa T(timedelta):
            @staticmethod
            def from_td(td):
                zwróć T(td.days, td.seconds, td.microseconds)

            def as_hours(self):
                sum = (self.days * 24 +
                       self.seconds / 3600.0 +
                       self.microseconds / 3600e6)
                zwróć round(sum)

        t1 = T(days=1)
        self.assertIs(type(t1), T)
        self.assertEqual(t1.as_hours(), 24)

        t2 = T(days=-1, seconds=-3600)
        self.assertIs(type(t2), T)
        self.assertEqual(t2.as_hours(), -25)

        t3 = t1 + t2
        self.assertIs(type(t3), timedelta)
        t4 = T.from_td(t3)
        self.assertIs(type(t4), T)
        self.assertEqual(t3.days, t4.days)
        self.assertEqual(t3.seconds, t4.seconds)
        self.assertEqual(t3.microseconds, t4.microseconds)
        self.assertEqual(str(t3), str(t4))
        self.assertEqual(t4.as_hours(), -1)

    def test_division(self):
        t = timedelta(hours=1, minutes=24, seconds=19)
        second = timedelta(seconds=1)
        self.assertEqual(t / second, 5059.0)
        self.assertEqual(t // second, 5059)

        t = timedelta(minutes=2, seconds=30)
        minute = timedelta(minutes=1)
        self.assertEqual(t / minute, 2.5)
        self.assertEqual(t // minute, 2)

        zerotd = timedelta(0)
        self.assertRaises(ZeroDivisionError, truediv, t, zerotd)
        self.assertRaises(ZeroDivisionError, floordiv, t, zerotd)

        # self.assertRaises(TypeError, truediv, t, 2)
        # note: floor division of a timedelta by an integer *is*
        # currently permitted.

    def test_remainder(self):
        t = timedelta(minutes=2, seconds=30)
        minute = timedelta(minutes=1)
        r = t % minute
        self.assertEqual(r, timedelta(seconds=30))

        t = timedelta(minutes=-2, seconds=30)
        r = t %  minute
        self.assertEqual(r, timedelta(seconds=30))

        zerotd = timedelta(0)
        self.assertRaises(ZeroDivisionError, mod, t, zerotd)

        self.assertRaises(TypeError, mod, t, 10)

    def test_divmod(self):
        t = timedelta(minutes=2, seconds=30)
        minute = timedelta(minutes=1)
        q, r = divmod(t, minute)
        self.assertEqual(q, 2)
        self.assertEqual(r, timedelta(seconds=30))

        t = timedelta(minutes=-2, seconds=30)
        q, r = divmod(t, minute)
        self.assertEqual(q, -2)
        self.assertEqual(r, timedelta(seconds=30))

        zerotd = timedelta(0)
        self.assertRaises(ZeroDivisionError, divmod, t, zerotd)

        self.assertRaises(TypeError, divmod, t, 10)


#############################################################################
# date tests

klasa TestDateOnly(unittest.TestCase):
    # Tests here won't dalej jeżeli also run on datetime objects, so don't
    # subclass this to test datetimes too.

    def test_delta_non_days_ignored(self):
        dt = date(2000, 1, 2)
        delta = timedelta(days=1, hours=2, minutes=3, seconds=4,
                          microseconds=5)
        days = timedelta(delta.days)
        self.assertEqual(days, timedelta(1))

        dt2 = dt + delta
        self.assertEqual(dt2, dt + days)

        dt2 = delta + dt
        self.assertEqual(dt2, dt + days)

        dt2 = dt - delta
        self.assertEqual(dt2, dt - days)

        delta = -delta
        days = timedelta(delta.days)
        self.assertEqual(days, timedelta(-2))

        dt2 = dt + delta
        self.assertEqual(dt2, dt + days)

        dt2 = delta + dt
        self.assertEqual(dt2, dt + days)

        dt2 = dt - delta
        self.assertEqual(dt2, dt - days)

klasa SubclassDate(date):
    sub_var = 1

klasa TestDate(HarmlessMixedComparison, unittest.TestCase):
    # Tests here should dalej dla both dates oraz datetimes, wyjąwszy dla a
    # few tests that TestDateTime overrides.

    theclass = date

    def test_basic_attributes(self):
        dt = self.theclass(2002, 3, 1)
        self.assertEqual(dt.year, 2002)
        self.assertEqual(dt.month, 3)
        self.assertEqual(dt.day, 1)

    def test_roundtrip(self):
        dla dt w (self.theclass(1, 2, 3),
                   self.theclass.today()):
            # Verify dt -> string -> date identity.
            s = repr(dt)
            self.assertPrawda(s.startswith('datetime.'))
            s = s[9:]
            dt2 = eval(s)
            self.assertEqual(dt, dt2)

            # Verify identity via reconstructing z pieces.
            dt2 = self.theclass(dt.year, dt.month, dt.day)
            self.assertEqual(dt, dt2)

    def test_ordinal_conversions(self):
        # Check some fixed values.
        dla y, m, d, n w [(1, 1, 1, 1),      # calendar origin
                           (1, 12, 31, 365),
                           (2, 1, 1, 366),
                           # first example z "Calendrical Calculations"
                           (1945, 11, 12, 710347)]:
            d = self.theclass(y, m, d)
            self.assertEqual(n, d.toordinal())
            fromord = self.theclass.fromordinal(n)
            self.assertEqual(d, fromord)
            jeżeli hasattr(fromord, "hour"):
            # jeżeli we're checking something fancier than a date, verify
            # the extra fields have been zeroed out
                self.assertEqual(fromord.hour, 0)
                self.assertEqual(fromord.minute, 0)
                self.assertEqual(fromord.second, 0)
                self.assertEqual(fromord.microsecond, 0)

        # Check first oraz last days of year spottily across the whole
        # range of years supported.
        dla year w range(MINYEAR, MAXYEAR+1, 7):
            # Verify (year, 1, 1) -> ordinal -> y, m, d jest identity.
            d = self.theclass(year, 1, 1)
            n = d.toordinal()
            d2 = self.theclass.fromordinal(n)
            self.assertEqual(d, d2)
            # Verify that moving back a day gets to the end of year-1.
            jeżeli year > 1:
                d = self.theclass.fromordinal(n-1)
                d2 = self.theclass(year-1, 12, 31)
                self.assertEqual(d, d2)
                self.assertEqual(d2.toordinal(), n-1)

        # Test every day w a leap-year oraz a non-leap year.
        dim = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        dla year, isleap w (2000, Prawda), (2002, Nieprawda):
            n = self.theclass(year, 1, 1).toordinal()
            dla month, maxday w zip(range(1, 13), dim):
                jeżeli month == 2 oraz isleap:
                    maxday += 1
                dla day w range(1, maxday+1):
                    d = self.theclass(year, month, day)
                    self.assertEqual(d.toordinal(), n)
                    self.assertEqual(d, self.theclass.fromordinal(n))
                    n += 1

    def test_extreme_ordinals(self):
        a = self.theclass.min
        a = self.theclass(a.year, a.month, a.day)  # get rid of time parts
        aord = a.toordinal()
        b = a.fromordinal(aord)
        self.assertEqual(a, b)

        self.assertRaises(ValueError, lambda: a.fromordinal(aord - 1))

        b = a + timedelta(days=1)
        self.assertEqual(b.toordinal(), aord + 1)
        self.assertEqual(b, self.theclass.fromordinal(aord + 1))

        a = self.theclass.max
        a = self.theclass(a.year, a.month, a.day)  # get rid of time parts
        aord = a.toordinal()
        b = a.fromordinal(aord)
        self.assertEqual(a, b)

        self.assertRaises(ValueError, lambda: a.fromordinal(aord + 1))

        b = a - timedelta(days=1)
        self.assertEqual(b.toordinal(), aord - 1)
        self.assertEqual(b, self.theclass.fromordinal(aord - 1))

    def test_bad_constructor_arguments(self):
        # bad years
        self.theclass(MINYEAR, 1, 1)  # no exception
        self.theclass(MAXYEAR, 1, 1)  # no exception
        self.assertRaises(ValueError, self.theclass, MINYEAR-1, 1, 1)
        self.assertRaises(ValueError, self.theclass, MAXYEAR+1, 1, 1)
        # bad months
        self.theclass(2000, 1, 1)    # no exception
        self.theclass(2000, 12, 1)   # no exception
        self.assertRaises(ValueError, self.theclass, 2000, 0, 1)
        self.assertRaises(ValueError, self.theclass, 2000, 13, 1)
        # bad days
        self.theclass(2000, 2, 29)   # no exception
        self.theclass(2004, 2, 29)   # no exception
        self.theclass(2400, 2, 29)   # no exception
        self.assertRaises(ValueError, self.theclass, 2000, 2, 30)
        self.assertRaises(ValueError, self.theclass, 2001, 2, 29)
        self.assertRaises(ValueError, self.theclass, 2100, 2, 29)
        self.assertRaises(ValueError, self.theclass, 1900, 2, 29)
        self.assertRaises(ValueError, self.theclass, 2000, 1, 0)
        self.assertRaises(ValueError, self.theclass, 2000, 1, 32)

    def test_hash_equality(self):
        d = self.theclass(2000, 12, 31)
        # same thing
        e = self.theclass(2000, 12, 31)
        self.assertEqual(d, e)
        self.assertEqual(hash(d), hash(e))

        dic = {d: 1}
        dic[e] = 2
        self.assertEqual(len(dic), 1)
        self.assertEqual(dic[d], 2)
        self.assertEqual(dic[e], 2)

        d = self.theclass(2001,  1,  1)
        # same thing
        e = self.theclass(2001,  1,  1)
        self.assertEqual(d, e)
        self.assertEqual(hash(d), hash(e))

        dic = {d: 1}
        dic[e] = 2
        self.assertEqual(len(dic), 1)
        self.assertEqual(dic[d], 2)
        self.assertEqual(dic[e], 2)

    def test_computations(self):
        a = self.theclass(2002, 1, 31)
        b = self.theclass(1956, 1, 31)
        c = self.theclass(2001,2,1)

        diff = a-b
        self.assertEqual(diff.days, 46*365 + len(range(1956, 2002, 4)))
        self.assertEqual(diff.seconds, 0)
        self.assertEqual(diff.microseconds, 0)

        day = timedelta(1)
        week = timedelta(7)
        a = self.theclass(2002, 3, 2)
        self.assertEqual(a + day, self.theclass(2002, 3, 3))
        self.assertEqual(day + a, self.theclass(2002, 3, 3))
        self.assertEqual(a - day, self.theclass(2002, 3, 1))
        self.assertEqual(-day + a, self.theclass(2002, 3, 1))
        self.assertEqual(a + week, self.theclass(2002, 3, 9))
        self.assertEqual(a - week, self.theclass(2002, 2, 23))
        self.assertEqual(a + 52*week, self.theclass(2003, 3, 1))
        self.assertEqual(a - 52*week, self.theclass(2001, 3, 3))
        self.assertEqual((a + week) - a, week)
        self.assertEqual((a + day) - a, day)
        self.assertEqual((a - week) - a, -week)
        self.assertEqual((a - day) - a, -day)
        self.assertEqual(a - (a + week), -week)
        self.assertEqual(a - (a + day), -day)
        self.assertEqual(a - (a - week), week)
        self.assertEqual(a - (a - day), day)
        self.assertEqual(c - (c - day), day)

        # Add/sub ints albo floats should be illegal
        dla i w 1, 1.0:
            self.assertRaises(TypeError, lambda: a+i)
            self.assertRaises(TypeError, lambda: a-i)
            self.assertRaises(TypeError, lambda: i+a)
            self.assertRaises(TypeError, lambda: i-a)

        # delta - date jest senseless.
        self.assertRaises(TypeError, lambda: day - a)
        # mixing date oraz (delta albo date) via * albo // jest senseless
        self.assertRaises(TypeError, lambda: day * a)
        self.assertRaises(TypeError, lambda: a * day)
        self.assertRaises(TypeError, lambda: day // a)
        self.assertRaises(TypeError, lambda: a // day)
        self.assertRaises(TypeError, lambda: a * a)
        self.assertRaises(TypeError, lambda: a // a)
        # date + date jest senseless
        self.assertRaises(TypeError, lambda: a + a)

    def test_overflow(self):
        tiny = self.theclass.resolution

        dla delta w [tiny, timedelta(1), timedelta(2)]:
            dt = self.theclass.min + delta
            dt -= delta  # no problem
            self.assertRaises(OverflowError, dt.__sub__, delta)
            self.assertRaises(OverflowError, dt.__add__, -delta)

            dt = self.theclass.max - delta
            dt += delta  # no problem
            self.assertRaises(OverflowError, dt.__add__, delta)
            self.assertRaises(OverflowError, dt.__sub__, -delta)

    def test_fromtimestamp(self):
        zaimportuj time

        # Try an arbitrary fixed value.
        year, month, day = 1999, 9, 19
        ts = time.mktime((year, month, day, 0, 0, 0, 0, 0, -1))
        d = self.theclass.fromtimestamp(ts)
        self.assertEqual(d.year, year)
        self.assertEqual(d.month, month)
        self.assertEqual(d.day, day)

    def test_insane_fromtimestamp(self):
        # It's possible that some platform maps time_t to double,
        # oraz that this test will fail there.  This test should
        # exempt such platforms (provided they zwróć reasonable
        # results!).
        dla insane w -1e200, 1e200:
            self.assertRaises(OverflowError, self.theclass.fromtimestamp,
                              insane)

    def test_today(self):
        zaimportuj time

        # We claim that today() jest like fromtimestamp(time.time()), so
        # prove it.
        dla dummy w range(3):
            today = self.theclass.today()
            ts = time.time()
            todayagain = self.theclass.fromtimestamp(ts)
            jeżeli today == todayagain:
                przerwij
            # There are several legit reasons that could fail:
            # 1. It recently became midnight, between the today() oraz the
            #    time() calls.
            # 2. The platform time() has such fine resolution that we'll
            #    never get the same value twice.
            # 3. The platform time() has poor resolution, oraz we just
            #    happened to call today() right before a resolution quantum
            #    boundary.
            # 4. The system clock got fiddled between calls.
            # In any case, wait a little dopóki oraz try again.
            time.sleep(0.1)

        # It worked albo it didn't.  If it didn't, assume it's reason #2, oraz
        # let the test dalej jeżeli they're within half a second of each other.
        jeżeli today != todayagain:
            self.assertAlmostEqual(todayagain, today,
                                   delta=timedelta(seconds=0.5))

    def test_weekday(self):
        dla i w range(7):
            # March 4, 2002 jest a Monday
            self.assertEqual(self.theclass(2002, 3, 4+i).weekday(), i)
            self.assertEqual(self.theclass(2002, 3, 4+i).isoweekday(), i+1)
            # January 2, 1956 jest a Monday
            self.assertEqual(self.theclass(1956, 1, 2+i).weekday(), i)
            self.assertEqual(self.theclass(1956, 1, 2+i).isoweekday(), i+1)

    def test_isocalendar(self):
        # Check examples from
        # http://www.phys.uu.nl/~vgent/calendar/isocalendar.htm
        dla i w range(7):
            d = self.theclass(2003, 12, 22+i)
            self.assertEqual(d.isocalendar(), (2003, 52, i+1))
            d = self.theclass(2003, 12, 29) + timedelta(i)
            self.assertEqual(d.isocalendar(), (2004, 1, i+1))
            d = self.theclass(2004, 1, 5+i)
            self.assertEqual(d.isocalendar(), (2004, 2, i+1))
            d = self.theclass(2009, 12, 21+i)
            self.assertEqual(d.isocalendar(), (2009, 52, i+1))
            d = self.theclass(2009, 12, 28) + timedelta(i)
            self.assertEqual(d.isocalendar(), (2009, 53, i+1))
            d = self.theclass(2010, 1, 4+i)
            self.assertEqual(d.isocalendar(), (2010, 1, i+1))

    def test_iso_long_years(self):
        # Calculate long ISO years oraz compare to table from
        # http://www.phys.uu.nl/~vgent/calendar/isocalendar.htm
        ISO_LONG_YEARS_TABLE = """
              4   32   60   88
              9   37   65   93
             15   43   71   99
             20   48   76
             26   54   82

            105  133  161  189
            111  139  167  195
            116  144  172
            122  150  178
            128  156  184

            201  229  257  285
            207  235  263  291
            212  240  268  296
            218  246  274
            224  252  280

            303  331  359  387
            308  336  364  392
            314  342  370  398
            320  348  376
            325  353  381
        """
        iso_long_years = sorted(map(int, ISO_LONG_YEARS_TABLE.split()))
        L = []
        dla i w range(400):
            d = self.theclass(2000+i, 12, 31)
            d1 = self.theclass(1600+i, 12, 31)
            self.assertEqual(d.isocalendar()[1:], d1.isocalendar()[1:])
            jeżeli d.isocalendar()[1] == 53:
                L.append(i)
        self.assertEqual(L, iso_long_years)

    def test_isoformat(self):
        t = self.theclass(2, 3, 2)
        self.assertEqual(t.isoformat(), "0002-03-02")

    def test_ctime(self):
        t = self.theclass(2002, 3, 2)
        self.assertEqual(t.ctime(), "Sat Mar  2 00:00:00 2002")

    def test_strftime(self):
        t = self.theclass(2005, 3, 2)
        self.assertEqual(t.strftime("m:%m d:%d y:%y"), "m:03 d:02 y:05")
        self.assertEqual(t.strftime(""), "") # SF bug #761337
        self.assertEqual(t.strftime('x'*1000), 'x'*1000) # SF bug #1556784

        self.assertRaises(TypeError, t.strftime) # needs an arg
        self.assertRaises(TypeError, t.strftime, "one", "two") # too many args
        self.assertRaises(TypeError, t.strftime, 42) # arg wrong type

        # test that unicode input jest allowed (issue 2782)
        self.assertEqual(t.strftime("%m"), "03")

        # A naive object replaces %z oraz %Z w/ empty strings.
        self.assertEqual(t.strftime("'%z' '%Z'"), "'' ''")

        #make sure that invalid format specifiers are handled correctly
        #self.assertRaises(ValueError, t.strftime, "%e")
        #self.assertRaises(ValueError, t.strftime, "%")
        #self.assertRaises(ValueError, t.strftime, "%#")

        #oh well, some systems just ignore those invalid ones.
        #at least, excercise them to make sure that no crashes
        #are generated
        dla f w ["%e", "%", "%#"]:
            spróbuj:
                t.strftime(f)
            wyjąwszy ValueError:
                dalej

        #check that this standard extension works
        t.strftime("%f")

    def test_format(self):
        dt = self.theclass(2007, 9, 10)
        self.assertEqual(dt.__format__(''), str(dt))

        przy self.assertRaisesRegex(TypeError, '^must be str, nie int$'):
            dt.__format__(123)

        # check that a derived class's __str__() gets called
        klasa A(self.theclass):
            def __str__(self):
                zwróć 'A'
        a = A(2007, 9, 10)
        self.assertEqual(a.__format__(''), 'A')

        # check that a derived class's strftime gets called
        klasa B(self.theclass):
            def strftime(self, format_spec):
                zwróć 'B'
        b = B(2007, 9, 10)
        self.assertEqual(b.__format__(''), str(dt))

        dla fmt w ["m:%m d:%d y:%y",
                    "m:%m d:%d y:%y H:%H M:%M S:%S",
                    "%z %Z",
                    ]:
            self.assertEqual(dt.__format__(fmt), dt.strftime(fmt))
            self.assertEqual(a.__format__(fmt), dt.strftime(fmt))
            self.assertEqual(b.__format__(fmt), 'B')

    def test_resolution_info(self):
        # XXX: Should min oraz max respect subclassing?
        jeżeli issubclass(self.theclass, datetime):
            expected_class = datetime
        inaczej:
            expected_class = date
        self.assertIsInstance(self.theclass.min, expected_class)
        self.assertIsInstance(self.theclass.max, expected_class)
        self.assertIsInstance(self.theclass.resolution, timedelta)
        self.assertPrawda(self.theclass.max > self.theclass.min)

    def test_extreme_timedelta(self):
        big = self.theclass.max - self.theclass.min
        # 3652058 days, 23 hours, 59 minutes, 59 seconds, 999999 microseconds
        n = (big.days*24*3600 + big.seconds)*1000000 + big.microseconds
        # n == 315537897599999999 ~= 2**58.13
        justasbig = timedelta(0, 0, n)
        self.assertEqual(big, justasbig)
        self.assertEqual(self.theclass.min + big, self.theclass.max)
        self.assertEqual(self.theclass.max - big, self.theclass.min)

    def test_timetuple(self):
        dla i w range(7):
            # January 2, 1956 jest a Monday (0)
            d = self.theclass(1956, 1, 2+i)
            t = d.timetuple()
            self.assertEqual(t, (1956, 1, 2+i, 0, 0, 0, i, 2+i, -1))
            # February 1, 1956 jest a Wednesday (2)
            d = self.theclass(1956, 2, 1+i)
            t = d.timetuple()
            self.assertEqual(t, (1956, 2, 1+i, 0, 0, 0, (2+i)%7, 32+i, -1))
            # March 1, 1956 jest a Thursday (3), oraz jest the 31+29+1 = 61st day
            # of the year.
            d = self.theclass(1956, 3, 1+i)
            t = d.timetuple()
            self.assertEqual(t, (1956, 3, 1+i, 0, 0, 0, (3+i)%7, 61+i, -1))
            self.assertEqual(t.tm_year, 1956)
            self.assertEqual(t.tm_mon, 3)
            self.assertEqual(t.tm_mday, 1+i)
            self.assertEqual(t.tm_hour, 0)
            self.assertEqual(t.tm_min, 0)
            self.assertEqual(t.tm_sec, 0)
            self.assertEqual(t.tm_wday, (3+i)%7)
            self.assertEqual(t.tm_yday, 61+i)
            self.assertEqual(t.tm_isdst, -1)

    def test_pickling(self):
        args = 6, 7, 23
        orig = self.theclass(*args)
        dla pickler, unpickler, proto w pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)

    def test_compare(self):
        t1 = self.theclass(2, 3, 4)
        t2 = self.theclass(2, 3, 4)
        self.assertEqual(t1, t2)
        self.assertPrawda(t1 <= t2)
        self.assertPrawda(t1 >= t2)
        self.assertNieprawda(t1 != t2)
        self.assertNieprawda(t1 < t2)
        self.assertNieprawda(t1 > t2)

        dla args w (3, 3, 3), (2, 4, 4), (2, 3, 5):
            t2 = self.theclass(*args)   # this jest larger than t1
            self.assertPrawda(t1 < t2)
            self.assertPrawda(t2 > t1)
            self.assertPrawda(t1 <= t2)
            self.assertPrawda(t2 >= t1)
            self.assertPrawda(t1 != t2)
            self.assertPrawda(t2 != t1)
            self.assertNieprawda(t1 == t2)
            self.assertNieprawda(t2 == t1)
            self.assertNieprawda(t1 > t2)
            self.assertNieprawda(t2 < t1)
            self.assertNieprawda(t1 >= t2)
            self.assertNieprawda(t2 <= t1)

        dla badarg w OTHERSTUFF:
            self.assertEqual(t1 == badarg, Nieprawda)
            self.assertEqual(t1 != badarg, Prawda)
            self.assertEqual(badarg == t1, Nieprawda)
            self.assertEqual(badarg != t1, Prawda)

            self.assertRaises(TypeError, lambda: t1 < badarg)
            self.assertRaises(TypeError, lambda: t1 > badarg)
            self.assertRaises(TypeError, lambda: t1 >= badarg)
            self.assertRaises(TypeError, lambda: badarg <= t1)
            self.assertRaises(TypeError, lambda: badarg < t1)
            self.assertRaises(TypeError, lambda: badarg > t1)
            self.assertRaises(TypeError, lambda: badarg >= t1)

    def test_mixed_compare(self):
        our = self.theclass(2000, 4, 5)

        # Our klasa can be compared dla equality to other classes
        self.assertEqual(our == 1, Nieprawda)
        self.assertEqual(1 == our, Nieprawda)
        self.assertEqual(our != 1, Prawda)
        self.assertEqual(1 != our, Prawda)

        # But the ordering jest undefined
        self.assertRaises(TypeError, lambda: our < 1)
        self.assertRaises(TypeError, lambda: 1 < our)

        # Repeat those tests przy a different class

        klasa SomeClass:
            dalej

        their = SomeClass()
        self.assertEqual(our == their, Nieprawda)
        self.assertEqual(their == our, Nieprawda)
        self.assertEqual(our != their, Prawda)
        self.assertEqual(their != our, Prawda)
        self.assertRaises(TypeError, lambda: our < their)
        self.assertRaises(TypeError, lambda: their < our)

        # However, jeżeli the other klasa explicitly defines ordering
        # relative to our class, it jest allowed to do so

        klasa LargerThanAnything:
            def __lt__(self, other):
                zwróć Nieprawda
            def __le__(self, other):
                zwróć isinstance(other, LargerThanAnything)
            def __eq__(self, other):
                zwróć isinstance(other, LargerThanAnything)
            def __gt__(self, other):
                zwróć nie isinstance(other, LargerThanAnything)
            def __ge__(self, other):
                zwróć Prawda

        their = LargerThanAnything()
        self.assertEqual(our == their, Nieprawda)
        self.assertEqual(their == our, Nieprawda)
        self.assertEqual(our != their, Prawda)
        self.assertEqual(their != our, Prawda)
        self.assertEqual(our < their, Prawda)
        self.assertEqual(their < our, Nieprawda)

    def test_bool(self):
        # All dates are considered true.
        self.assertPrawda(self.theclass.min)
        self.assertPrawda(self.theclass.max)

    def test_strftime_y2k(self):
        dla y w (1, 49, 70, 99, 100, 999, 1000, 1970):
            d = self.theclass(y, 1, 1)
            # Issue 13305:  For years < 1000, the value jest nie always
            # padded to 4 digits across platforms.  The C standard
            # assumes year >= 1900, so it does nie specify the number
            # of digits.
            jeżeli d.strftime("%Y") != '%04d' % y:
                # Year 42 returns '42', nie padded
                self.assertEqual(d.strftime("%Y"), '%d' % y)
                # '0042' jest obtained anyway
                self.assertEqual(d.strftime("%4Y"), '%04d' % y)

    def test_replace(self):
        cls = self.theclass
        args = [1, 2, 3]
        base = cls(*args)
        self.assertEqual(base, base.replace())

        i = 0
        dla name, newval w (("year", 2),
                             ("month", 3),
                             ("day", 4)):
            newargs = args[:]
            newargs[i] = newval
            expected = cls(*newargs)
            got = base.replace(**{name: newval})
            self.assertEqual(expected, got)
            i += 1

        # Out of bounds.
        base = cls(2000, 2, 29)
        self.assertRaises(ValueError, base.replace, year=2001)

    def test_subclass_date(self):

        klasa C(self.theclass):
            theAnswer = 42

            def __new__(cls, *args, **kws):
                temp = kws.copy()
                extra = temp.pop('extra')
                result = self.theclass.__new__(cls, *args, **temp)
                result.extra = extra
                zwróć result

            def newmeth(self, start):
                zwróć start + self.year + self.month

        args = 2003, 4, 14

        dt1 = self.theclass(*args)
        dt2 = C(*args, **{'extra': 7})

        self.assertEqual(dt2.__class__, C)
        self.assertEqual(dt2.theAnswer, 42)
        self.assertEqual(dt2.extra, 7)
        self.assertEqual(dt1.toordinal(), dt2.toordinal())
        self.assertEqual(dt2.newmeth(-7), dt1.year + dt1.month - 7)

    def test_pickling_subclass_date(self):

        args = 6, 7, 23
        orig = SubclassDate(*args)
        dla pickler, unpickler, proto w pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)

    def test_backdoor_resistance(self):
        # For fast unpickling, the constructor accepts a pickle byte string.
        # This jest a low-overhead backdoor.  A user can (by intent albo
        # mistake) dalej a string directly, which (jeżeli it's the right length)
        # will get treated like a pickle, oraz bypass the normal sanity
        # checks w the constructor.  This can create insane objects.
        # The constructor doesn't want to burn the time to validate all
        # fields, but does check the month field.  This stops, e.g.,
        # datetime.datetime('1995-03-25') z uzyskajing an insane object.
        base = b'1995-03-25'
        jeżeli nie issubclass(self.theclass, datetime):
            base = base[:4]
        dla month_byte w b'9', b'\0', b'\r', b'\xff':
            self.assertRaises(TypeError, self.theclass,
                                         base[:2] + month_byte + base[3:])
        jeżeli issubclass(self.theclass, datetime):
            # Good bytes, but bad tzinfo:
            przy self.assertRaisesRegex(TypeError, '^bad tzinfo state arg$'):
                self.theclass(bytes([1] * len(base)), 'EST')

        dla ord_byte w range(1, 13):
            # This shouldn't blow up because of the month byte alone.  If
            # the implementation changes to do more-careful checking, it may
            # blow up because other fields are insane.
            self.theclass(base[:2] + bytes([ord_byte]) + base[3:])

#############################################################################
# datetime tests

klasa SubclassDatetime(datetime):
    sub_var = 1

klasa TestDateTime(TestDate):

    theclass = datetime

    def test_basic_attributes(self):
        dt = self.theclass(2002, 3, 1, 12, 0)
        self.assertEqual(dt.year, 2002)
        self.assertEqual(dt.month, 3)
        self.assertEqual(dt.day, 1)
        self.assertEqual(dt.hour, 12)
        self.assertEqual(dt.minute, 0)
        self.assertEqual(dt.second, 0)
        self.assertEqual(dt.microsecond, 0)

    def test_basic_attributes_nonzero(self):
        # Make sure all attributes are non-zero so bugs w
        # bit-shifting access show up.
        dt = self.theclass(2002, 3, 1, 12, 59, 59, 8000)
        self.assertEqual(dt.year, 2002)
        self.assertEqual(dt.month, 3)
        self.assertEqual(dt.day, 1)
        self.assertEqual(dt.hour, 12)
        self.assertEqual(dt.minute, 59)
        self.assertEqual(dt.second, 59)
        self.assertEqual(dt.microsecond, 8000)

    def test_roundtrip(self):
        dla dt w (self.theclass(1, 2, 3, 4, 5, 6, 7),
                   self.theclass.now()):
            # Verify dt -> string -> datetime identity.
            s = repr(dt)
            self.assertPrawda(s.startswith('datetime.'))
            s = s[9:]
            dt2 = eval(s)
            self.assertEqual(dt, dt2)

            # Verify identity via reconstructing z pieces.
            dt2 = self.theclass(dt.year, dt.month, dt.day,
                                dt.hour, dt.minute, dt.second,
                                dt.microsecond)
            self.assertEqual(dt, dt2)

    def test_isoformat(self):
        t = self.theclass(2, 3, 2, 4, 5, 1, 123)
        self.assertEqual(t.isoformat(),    "0002-03-02T04:05:01.000123")
        self.assertEqual(t.isoformat('T'), "0002-03-02T04:05:01.000123")
        self.assertEqual(t.isoformat(' '), "0002-03-02 04:05:01.000123")
        self.assertEqual(t.isoformat('\x00'), "0002-03-02\x0004:05:01.000123")
        # str jest ISO format przy the separator forced to a blank.
        self.assertEqual(str(t), "0002-03-02 04:05:01.000123")

        t = self.theclass(2, 3, 2)
        self.assertEqual(t.isoformat(),    "0002-03-02T00:00:00")
        self.assertEqual(t.isoformat('T'), "0002-03-02T00:00:00")
        self.assertEqual(t.isoformat(' '), "0002-03-02 00:00:00")
        # str jest ISO format przy the separator forced to a blank.
        self.assertEqual(str(t), "0002-03-02 00:00:00")

    def test_format(self):
        dt = self.theclass(2007, 9, 10, 4, 5, 1, 123)
        self.assertEqual(dt.__format__(''), str(dt))

        przy self.assertRaisesRegex(TypeError, '^must be str, nie int$'):
            dt.__format__(123)

        # check that a derived class's __str__() gets called
        klasa A(self.theclass):
            def __str__(self):
                zwróć 'A'
        a = A(2007, 9, 10, 4, 5, 1, 123)
        self.assertEqual(a.__format__(''), 'A')

        # check that a derived class's strftime gets called
        klasa B(self.theclass):
            def strftime(self, format_spec):
                zwróć 'B'
        b = B(2007, 9, 10, 4, 5, 1, 123)
        self.assertEqual(b.__format__(''), str(dt))

        dla fmt w ["m:%m d:%d y:%y",
                    "m:%m d:%d y:%y H:%H M:%M S:%S",
                    "%z %Z",
                    ]:
            self.assertEqual(dt.__format__(fmt), dt.strftime(fmt))
            self.assertEqual(a.__format__(fmt), dt.strftime(fmt))
            self.assertEqual(b.__format__(fmt), 'B')

    def test_more_ctime(self):
        # Test fields that TestDate doesn't touch.
        zaimportuj time

        t = self.theclass(2002, 3, 2, 18, 3, 5, 123)
        self.assertEqual(t.ctime(), "Sat Mar  2 18:03:05 2002")
        # Oops!  The next line fails on Win2K under MSVC 6, so it's commented
        # out.  The difference jest that t.ctime() produces " 2" dla the day,
        # but platform ctime() produces "02" dla the day.  According to
        # C99, t.ctime() jest correct here.
        # self.assertEqual(t.ctime(), time.ctime(time.mktime(t.timetuple())))

        # So test a case where that difference doesn't matter.
        t = self.theclass(2002, 3, 22, 18, 3, 5, 123)
        self.assertEqual(t.ctime(), time.ctime(time.mktime(t.timetuple())))

    def test_tz_independent_comparing(self):
        dt1 = self.theclass(2002, 3, 1, 9, 0, 0)
        dt2 = self.theclass(2002, 3, 1, 10, 0, 0)
        dt3 = self.theclass(2002, 3, 1, 9, 0, 0)
        self.assertEqual(dt1, dt3)
        self.assertPrawda(dt2 > dt3)

        # Make sure comparison doesn't forget microseconds, oraz isn't done
        # via comparing a float timestamp (an IEEE double doesn't have enough
        # precision to span microsecond resolution across years 1 thru 9999,
        # so comparing via timestamp necessarily calls some distinct values
        # equal).
        dt1 = self.theclass(MAXYEAR, 12, 31, 23, 59, 59, 999998)
        us = timedelta(microseconds=1)
        dt2 = dt1 + us
        self.assertEqual(dt2 - dt1, us)
        self.assertPrawda(dt1 < dt2)

    def test_strftime_with_bad_tzname_replace(self):
        # verify ok jeżeli tzinfo.tzname().replace() returns a non-string
        klasa MyTzInfo(FixedOffset):
            def tzname(self, dt):
                klasa MyStr(str):
                    def replace(self, *args):
                        zwróć Nic
                zwróć MyStr('name')
        t = self.theclass(2005, 3, 2, 0, 0, 0, 0, MyTzInfo(3, 'name'))
        self.assertRaises(TypeError, t.strftime, '%Z')

    def test_bad_constructor_arguments(self):
        # bad years
        self.theclass(MINYEAR, 1, 1)  # no exception
        self.theclass(MAXYEAR, 1, 1)  # no exception
        self.assertRaises(ValueError, self.theclass, MINYEAR-1, 1, 1)
        self.assertRaises(ValueError, self.theclass, MAXYEAR+1, 1, 1)
        # bad months
        self.theclass(2000, 1, 1)    # no exception
        self.theclass(2000, 12, 1)   # no exception
        self.assertRaises(ValueError, self.theclass, 2000, 0, 1)
        self.assertRaises(ValueError, self.theclass, 2000, 13, 1)
        # bad days
        self.theclass(2000, 2, 29)   # no exception
        self.theclass(2004, 2, 29)   # no exception
        self.theclass(2400, 2, 29)   # no exception
        self.assertRaises(ValueError, self.theclass, 2000, 2, 30)
        self.assertRaises(ValueError, self.theclass, 2001, 2, 29)
        self.assertRaises(ValueError, self.theclass, 2100, 2, 29)
        self.assertRaises(ValueError, self.theclass, 1900, 2, 29)
        self.assertRaises(ValueError, self.theclass, 2000, 1, 0)
        self.assertRaises(ValueError, self.theclass, 2000, 1, 32)
        # bad hours
        self.theclass(2000, 1, 31, 0)    # no exception
        self.theclass(2000, 1, 31, 23)   # no exception
        self.assertRaises(ValueError, self.theclass, 2000, 1, 31, -1)
        self.assertRaises(ValueError, self.theclass, 2000, 1, 31, 24)
        # bad minutes
        self.theclass(2000, 1, 31, 23, 0)    # no exception
        self.theclass(2000, 1, 31, 23, 59)   # no exception
        self.assertRaises(ValueError, self.theclass, 2000, 1, 31, 23, -1)
        self.assertRaises(ValueError, self.theclass, 2000, 1, 31, 23, 60)
        # bad seconds
        self.theclass(2000, 1, 31, 23, 59, 0)    # no exception
        self.theclass(2000, 1, 31, 23, 59, 59)   # no exception
        self.assertRaises(ValueError, self.theclass, 2000, 1, 31, 23, 59, -1)
        self.assertRaises(ValueError, self.theclass, 2000, 1, 31, 23, 59, 60)
        # bad microseconds
        self.theclass(2000, 1, 31, 23, 59, 59, 0)    # no exception
        self.theclass(2000, 1, 31, 23, 59, 59, 999999)   # no exception
        self.assertRaises(ValueError, self.theclass,
                          2000, 1, 31, 23, 59, 59, -1)
        self.assertRaises(ValueError, self.theclass,
                          2000, 1, 31, 23, 59, 59,
                          1000000)

    def test_hash_equality(self):
        d = self.theclass(2000, 12, 31, 23, 30, 17)
        e = self.theclass(2000, 12, 31, 23, 30, 17)
        self.assertEqual(d, e)
        self.assertEqual(hash(d), hash(e))

        dic = {d: 1}
        dic[e] = 2
        self.assertEqual(len(dic), 1)
        self.assertEqual(dic[d], 2)
        self.assertEqual(dic[e], 2)

        d = self.theclass(2001,  1,  1,  0,  5, 17)
        e = self.theclass(2001,  1,  1,  0,  5, 17)
        self.assertEqual(d, e)
        self.assertEqual(hash(d), hash(e))

        dic = {d: 1}
        dic[e] = 2
        self.assertEqual(len(dic), 1)
        self.assertEqual(dic[d], 2)
        self.assertEqual(dic[e], 2)

    def test_computations(self):
        a = self.theclass(2002, 1, 31)
        b = self.theclass(1956, 1, 31)
        diff = a-b
        self.assertEqual(diff.days, 46*365 + len(range(1956, 2002, 4)))
        self.assertEqual(diff.seconds, 0)
        self.assertEqual(diff.microseconds, 0)
        a = self.theclass(2002, 3, 2, 17, 6)
        millisec = timedelta(0, 0, 1000)
        hour = timedelta(0, 3600)
        day = timedelta(1)
        week = timedelta(7)
        self.assertEqual(a + hour, self.theclass(2002, 3, 2, 18, 6))
        self.assertEqual(hour + a, self.theclass(2002, 3, 2, 18, 6))
        self.assertEqual(a + 10*hour, self.theclass(2002, 3, 3, 3, 6))
        self.assertEqual(a - hour, self.theclass(2002, 3, 2, 16, 6))
        self.assertEqual(-hour + a, self.theclass(2002, 3, 2, 16, 6))
        self.assertEqual(a - hour, a + -hour)
        self.assertEqual(a - 20*hour, self.theclass(2002, 3, 1, 21, 6))
        self.assertEqual(a + day, self.theclass(2002, 3, 3, 17, 6))
        self.assertEqual(a - day, self.theclass(2002, 3, 1, 17, 6))
        self.assertEqual(a + week, self.theclass(2002, 3, 9, 17, 6))
        self.assertEqual(a - week, self.theclass(2002, 2, 23, 17, 6))
        self.assertEqual(a + 52*week, self.theclass(2003, 3, 1, 17, 6))
        self.assertEqual(a - 52*week, self.theclass(2001, 3, 3, 17, 6))
        self.assertEqual((a + week) - a, week)
        self.assertEqual((a + day) - a, day)
        self.assertEqual((a + hour) - a, hour)
        self.assertEqual((a + millisec) - a, millisec)
        self.assertEqual((a - week) - a, -week)
        self.assertEqual((a - day) - a, -day)
        self.assertEqual((a - hour) - a, -hour)
        self.assertEqual((a - millisec) - a, -millisec)
        self.assertEqual(a - (a + week), -week)
        self.assertEqual(a - (a + day), -day)
        self.assertEqual(a - (a + hour), -hour)
        self.assertEqual(a - (a + millisec), -millisec)
        self.assertEqual(a - (a - week), week)
        self.assertEqual(a - (a - day), day)
        self.assertEqual(a - (a - hour), hour)
        self.assertEqual(a - (a - millisec), millisec)
        self.assertEqual(a + (week + day + hour + millisec),
                         self.theclass(2002, 3, 10, 18, 6, 0, 1000))
        self.assertEqual(a + (week + day + hour + millisec),
                         (((a + week) + day) + hour) + millisec)
        self.assertEqual(a - (week + day + hour + millisec),
                         self.theclass(2002, 2, 22, 16, 5, 59, 999000))
        self.assertEqual(a - (week + day + hour + millisec),
                         (((a - week) - day) - hour) - millisec)
        # Add/sub ints albo floats should be illegal
        dla i w 1, 1.0:
            self.assertRaises(TypeError, lambda: a+i)
            self.assertRaises(TypeError, lambda: a-i)
            self.assertRaises(TypeError, lambda: i+a)
            self.assertRaises(TypeError, lambda: i-a)

        # delta - datetime jest senseless.
        self.assertRaises(TypeError, lambda: day - a)
        # mixing datetime oraz (delta albo datetime) via * albo // jest senseless
        self.assertRaises(TypeError, lambda: day * a)
        self.assertRaises(TypeError, lambda: a * day)
        self.assertRaises(TypeError, lambda: day // a)
        self.assertRaises(TypeError, lambda: a // day)
        self.assertRaises(TypeError, lambda: a * a)
        self.assertRaises(TypeError, lambda: a // a)
        # datetime + datetime jest senseless
        self.assertRaises(TypeError, lambda: a + a)

    def test_pickling(self):
        args = 6, 7, 23, 20, 59, 1, 64**2
        orig = self.theclass(*args)
        dla pickler, unpickler, proto w pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)

    def test_more_pickling(self):
        a = self.theclass(2003, 2, 7, 16, 48, 37, 444116)
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            s = pickle.dumps(a, proto)
            b = pickle.loads(s)
            self.assertEqual(b.year, 2003)
            self.assertEqual(b.month, 2)
            self.assertEqual(b.day, 7)

    def test_pickling_subclass_datetime(self):
        args = 6, 7, 23, 20, 59, 1, 64**2
        orig = SubclassDatetime(*args)
        dla pickler, unpickler, proto w pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)

    def test_more_compare(self):
        # The test_compare() inherited z TestDate covers the error cases.
        # We just want to test lexicographic ordering on the members datetime
        # has that date lacks.
        args = [2000, 11, 29, 20, 58, 16, 999998]
        t1 = self.theclass(*args)
        t2 = self.theclass(*args)
        self.assertEqual(t1, t2)
        self.assertPrawda(t1 <= t2)
        self.assertPrawda(t1 >= t2)
        self.assertNieprawda(t1 != t2)
        self.assertNieprawda(t1 < t2)
        self.assertNieprawda(t1 > t2)

        dla i w range(len(args)):
            newargs = args[:]
            newargs[i] = args[i] + 1
            t2 = self.theclass(*newargs)   # this jest larger than t1
            self.assertPrawda(t1 < t2)
            self.assertPrawda(t2 > t1)
            self.assertPrawda(t1 <= t2)
            self.assertPrawda(t2 >= t1)
            self.assertPrawda(t1 != t2)
            self.assertPrawda(t2 != t1)
            self.assertNieprawda(t1 == t2)
            self.assertNieprawda(t2 == t1)
            self.assertNieprawda(t1 > t2)
            self.assertNieprawda(t2 < t1)
            self.assertNieprawda(t1 >= t2)
            self.assertNieprawda(t2 <= t1)


    # A helper dla timestamp constructor tests.
    def verify_field_equality(self, expected, got):
        self.assertEqual(expected.tm_year, got.year)
        self.assertEqual(expected.tm_mon, got.month)
        self.assertEqual(expected.tm_mday, got.day)
        self.assertEqual(expected.tm_hour, got.hour)
        self.assertEqual(expected.tm_min, got.minute)
        self.assertEqual(expected.tm_sec, got.second)

    def test_fromtimestamp(self):
        zaimportuj time

        ts = time.time()
        expected = time.localtime(ts)
        got = self.theclass.fromtimestamp(ts)
        self.verify_field_equality(expected, got)

    def test_utcfromtimestamp(self):
        zaimportuj time

        ts = time.time()
        expected = time.gmtime(ts)
        got = self.theclass.utcfromtimestamp(ts)
        self.verify_field_equality(expected, got)

    # Run przy US-style DST rules: DST begins 2 a.m. on second Sunday w
    # March (M3.2.0) oraz ends 2 a.m. on first Sunday w November (M11.1.0).
    @support.run_with_tz('EST+05EDT,M3.2.0,M11.1.0')
    def test_timestamp_naive(self):
        t = self.theclass(1970, 1, 1)
        self.assertEqual(t.timestamp(), 18000.0)
        t = self.theclass(1970, 1, 1, 1, 2, 3, 4)
        self.assertEqual(t.timestamp(),
                         18000.0 + 3600 + 2*60 + 3 + 4*1e-6)
        # Missing hour may produce platform-dependent result
        t = self.theclass(2012, 3, 11, 2, 30)
        self.assertIn(self.theclass.fromtimestamp(t.timestamp()),
                      [t - timedelta(hours=1), t + timedelta(hours=1)])
        # Ambiguous hour defaults to DST
        t = self.theclass(2012, 11, 4, 1, 30)
        self.assertEqual(self.theclass.fromtimestamp(t.timestamp()), t)

        # Timestamp may podnieś an overflow error on some platforms
        dla t w [self.theclass(1,1,1), self.theclass(9999,12,12)]:
            spróbuj:
                s = t.timestamp()
            wyjąwszy OverflowError:
                dalej
            inaczej:
                self.assertEqual(self.theclass.fromtimestamp(s), t)

    def test_timestamp_aware(self):
        t = self.theclass(1970, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(t.timestamp(), 0.0)
        t = self.theclass(1970, 1, 1, 1, 2, 3, 4, tzinfo=timezone.utc)
        self.assertEqual(t.timestamp(),
                         3600 + 2*60 + 3 + 4*1e-6)
        t = self.theclass(1970, 1, 1, 1, 2, 3, 4,
                          tzinfo=timezone(timedelta(hours=-5), 'EST'))
        self.assertEqual(t.timestamp(),
                         18000 + 3600 + 2*60 + 3 + 4*1e-6)

    def test_microsecond_rounding(self):
        dla fts w [self.theclass.fromtimestamp,
                    self.theclass.utcfromtimestamp]:
            zero = fts(0)
            self.assertEqual(zero.second, 0)
            self.assertEqual(zero.microsecond, 0)
            spróbuj:
                minus_one = fts(-1e-6)
            wyjąwszy OSError:
                # localtime(-1) oraz gmtime(-1) jest nie supported on Windows
                dalej
            inaczej:
                self.assertEqual(minus_one.second, 59)
                self.assertEqual(minus_one.microsecond, 999999)

                t = fts(-1e-8)
                self.assertEqual(t, minus_one)
                t = fts(-9e-7)
                self.assertEqual(t, minus_one)
                t = fts(-1e-7)
                self.assertEqual(t, minus_one)

            t = fts(1e-7)
            self.assertEqual(t, zero)
            t = fts(9e-7)
            self.assertEqual(t, zero)
            t = fts(0.99999949)
            self.assertEqual(t.second, 0)
            self.assertEqual(t.microsecond, 999999)
            t = fts(0.9999999)
            self.assertEqual(t.second, 0)
            self.assertEqual(t.microsecond, 999999)

    def test_insane_fromtimestamp(self):
        # It's possible that some platform maps time_t to double,
        # oraz that this test will fail there.  This test should
        # exempt such platforms (provided they zwróć reasonable
        # results!).
        dla insane w -1e200, 1e200:
            self.assertRaises(OverflowError, self.theclass.fromtimestamp,
                              insane)

    def test_insane_utcfromtimestamp(self):
        # It's possible that some platform maps time_t to double,
        # oraz that this test will fail there.  This test should
        # exempt such platforms (provided they zwróć reasonable
        # results!).
        dla insane w -1e200, 1e200:
            self.assertRaises(OverflowError, self.theclass.utcfromtimestamp,
                              insane)

    @unittest.skipIf(sys.platform == "win32", "Windows doesn't accept negative timestamps")
    def test_negative_float_fromtimestamp(self):
        # The result jest tz-dependent; at least test that this doesn't
        # fail (like it did before bug 1646728 was fixed).
        self.theclass.fromtimestamp(-1.05)

    @unittest.skipIf(sys.platform == "win32", "Windows doesn't accept negative timestamps")
    def test_negative_float_utcfromtimestamp(self):
        d = self.theclass.utcfromtimestamp(-1.05)
        self.assertEqual(d, self.theclass(1969, 12, 31, 23, 59, 58, 950000))

    def test_utcnow(self):
        zaimportuj time

        # Call it a success jeżeli utcnow() oraz utcfromtimestamp() are within
        # a second of each other.
        tolerance = timedelta(seconds=1)
        dla dummy w range(3):
            from_now = self.theclass.utcnow()
            from_timestamp = self.theclass.utcfromtimestamp(time.time())
            jeżeli abs(from_timestamp - from_now) <= tolerance:
                przerwij
            # Else try again a few times.
        self.assertLessEqual(abs(from_timestamp - from_now), tolerance)

    def test_strptime(self):
        string = '2004-12-01 13:02:47.197'
        format = '%Y-%m-%d %H:%M:%S.%f'
        expected = _strptime._strptime_datetime(self.theclass, string, format)
        got = self.theclass.strptime(string, format)
        self.assertEqual(expected, got)
        self.assertIs(type(expected), self.theclass)
        self.assertIs(type(got), self.theclass)

        strptime = self.theclass.strptime
        self.assertEqual(strptime("+0002", "%z").utcoffset(), 2 * MINUTE)
        self.assertEqual(strptime("-0002", "%z").utcoffset(), -2 * MINUTE)
        # Only local timezone oraz UTC are supported
        dla tzseconds, tzname w ((0, 'UTC'), (0, 'GMT'),
                                 (-_time.timezone, _time.tzname[0])):
            jeżeli tzseconds < 0:
                sign = '-'
                seconds = -tzseconds
            inaczej:
                sign ='+'
                seconds = tzseconds
            hours, minutes = divmod(seconds//60, 60)
            dtstr = "{}{:02d}{:02d} {}".format(sign, hours, minutes, tzname)
            dt = strptime(dtstr, "%z %Z")
            self.assertEqual(dt.utcoffset(), timedelta(seconds=tzseconds))
            self.assertEqual(dt.tzname(), tzname)
        # Can produce inconsistent datetime
        dtstr, fmt = "+1234 UTC", "%z %Z"
        dt = strptime(dtstr, fmt)
        self.assertEqual(dt.utcoffset(), 12 * HOUR + 34 * MINUTE)
        self.assertEqual(dt.tzname(), 'UTC')
        # yet will roundtrip
        self.assertEqual(dt.strftime(fmt), dtstr)

        # Produce naive datetime jeżeli no %z jest provided
        self.assertEqual(strptime("UTC", "%Z").tzinfo, Nic)

        przy self.assertRaises(ValueError): strptime("-2400", "%z")
        przy self.assertRaises(ValueError): strptime("-000", "%z")

    def test_more_timetuple(self):
        # This tests fields beyond those tested by the TestDate.test_timetuple.
        t = self.theclass(2004, 12, 31, 6, 22, 33)
        self.assertEqual(t.timetuple(), (2004, 12, 31, 6, 22, 33, 4, 366, -1))
        self.assertEqual(t.timetuple(),
                         (t.year, t.month, t.day,
                          t.hour, t.minute, t.second,
                          t.weekday(),
                          t.toordinal() - date(t.year, 1, 1).toordinal() + 1,
                          -1))
        tt = t.timetuple()
        self.assertEqual(tt.tm_year, t.year)
        self.assertEqual(tt.tm_mon, t.month)
        self.assertEqual(tt.tm_mday, t.day)
        self.assertEqual(tt.tm_hour, t.hour)
        self.assertEqual(tt.tm_min, t.minute)
        self.assertEqual(tt.tm_sec, t.second)
        self.assertEqual(tt.tm_wday, t.weekday())
        self.assertEqual(tt.tm_yday, t.toordinal() -
                                     date(t.year, 1, 1).toordinal() + 1)
        self.assertEqual(tt.tm_isdst, -1)

    def test_more_strftime(self):
        # This tests fields beyond those tested by the TestDate.test_strftime.
        t = self.theclass(2004, 12, 31, 6, 22, 33, 47)
        self.assertEqual(t.strftime("%m %d %y %f %S %M %H %j"),
                                    "12 31 04 000047 33 22 06 366")

    def test_extract(self):
        dt = self.theclass(2002, 3, 4, 18, 45, 3, 1234)
        self.assertEqual(dt.date(), date(2002, 3, 4))
        self.assertEqual(dt.time(), time(18, 45, 3, 1234))

    def test_combine(self):
        d = date(2002, 3, 4)
        t = time(18, 45, 3, 1234)
        expected = self.theclass(2002, 3, 4, 18, 45, 3, 1234)
        combine = self.theclass.combine
        dt = combine(d, t)
        self.assertEqual(dt, expected)

        dt = combine(time=t, date=d)
        self.assertEqual(dt, expected)

        self.assertEqual(d, dt.date())
        self.assertEqual(t, dt.time())
        self.assertEqual(dt, combine(dt.date(), dt.time()))

        self.assertRaises(TypeError, combine) # need an arg
        self.assertRaises(TypeError, combine, d) # need two args
        self.assertRaises(TypeError, combine, t, d) # args reversed
        self.assertRaises(TypeError, combine, d, t, 1) # too many args
        self.assertRaises(TypeError, combine, "date", "time") # wrong types
        self.assertRaises(TypeError, combine, d, "time") # wrong type
        self.assertRaises(TypeError, combine, "date", t) # wrong type

    def test_replace(self):
        cls = self.theclass
        args = [1, 2, 3, 4, 5, 6, 7]
        base = cls(*args)
        self.assertEqual(base, base.replace())

        i = 0
        dla name, newval w (("year", 2),
                             ("month", 3),
                             ("day", 4),
                             ("hour", 5),
                             ("minute", 6),
                             ("second", 7),
                             ("microsecond", 8)):
            newargs = args[:]
            newargs[i] = newval
            expected = cls(*newargs)
            got = base.replace(**{name: newval})
            self.assertEqual(expected, got)
            i += 1

        # Out of bounds.
        base = cls(2000, 2, 29)
        self.assertRaises(ValueError, base.replace, year=2001)

    def test_astimezone(self):
        # Pretty boring!  The TZ test jest more interesting here.  astimezone()
        # simply can't be applied to a naive object.
        dt = self.theclass.now()
        f = FixedOffset(44, "")
        self.assertRaises(ValueError, dt.astimezone) # naive
        self.assertRaises(TypeError, dt.astimezone, f, f) # too many args
        self.assertRaises(TypeError, dt.astimezone, dt) # arg wrong type
        self.assertRaises(ValueError, dt.astimezone, f) # naive
        self.assertRaises(ValueError, dt.astimezone, tz=f)  # naive

        klasa Bogus(tzinfo):
            def utcoffset(self, dt): zwróć Nic
            def dst(self, dt): zwróć timedelta(0)
        bog = Bogus()
        self.assertRaises(ValueError, dt.astimezone, bog)   # naive
        self.assertRaises(ValueError,
                          dt.replace(tzinfo=bog).astimezone, f)

        klasa AlsoBogus(tzinfo):
            def utcoffset(self, dt): zwróć timedelta(0)
            def dst(self, dt): zwróć Nic
        alsobog = AlsoBogus()
        self.assertRaises(ValueError, dt.astimezone, alsobog) # also naive

    def test_subclass_datetime(self):

        klasa C(self.theclass):
            theAnswer = 42

            def __new__(cls, *args, **kws):
                temp = kws.copy()
                extra = temp.pop('extra')
                result = self.theclass.__new__(cls, *args, **temp)
                result.extra = extra
                zwróć result

            def newmeth(self, start):
                zwróć start + self.year + self.month + self.second

        args = 2003, 4, 14, 12, 13, 41

        dt1 = self.theclass(*args)
        dt2 = C(*args, **{'extra': 7})

        self.assertEqual(dt2.__class__, C)
        self.assertEqual(dt2.theAnswer, 42)
        self.assertEqual(dt2.extra, 7)
        self.assertEqual(dt1.toordinal(), dt2.toordinal())
        self.assertEqual(dt2.newmeth(-7), dt1.year + dt1.month +
                                          dt1.second - 7)

klasa TestSubclassDateTime(TestDateTime):
    theclass = SubclassDatetime
    # Override tests nie designed dla subclass
    @unittest.skip('not appropriate dla subclasses')
    def test_roundtrip(self):
        dalej

klasa SubclassTime(time):
    sub_var = 1

klasa TestTime(HarmlessMixedComparison, unittest.TestCase):

    theclass = time

    def test_basic_attributes(self):
        t = self.theclass(12, 0)
        self.assertEqual(t.hour, 12)
        self.assertEqual(t.minute, 0)
        self.assertEqual(t.second, 0)
        self.assertEqual(t.microsecond, 0)

    def test_basic_attributes_nonzero(self):
        # Make sure all attributes are non-zero so bugs w
        # bit-shifting access show up.
        t = self.theclass(12, 59, 59, 8000)
        self.assertEqual(t.hour, 12)
        self.assertEqual(t.minute, 59)
        self.assertEqual(t.second, 59)
        self.assertEqual(t.microsecond, 8000)

    def test_roundtrip(self):
        t = self.theclass(1, 2, 3, 4)

        # Verify t -> string -> time identity.
        s = repr(t)
        self.assertPrawda(s.startswith('datetime.'))
        s = s[9:]
        t2 = eval(s)
        self.assertEqual(t, t2)

        # Verify identity via reconstructing z pieces.
        t2 = self.theclass(t.hour, t.minute, t.second,
                           t.microsecond)
        self.assertEqual(t, t2)

    def test_comparing(self):
        args = [1, 2, 3, 4]
        t1 = self.theclass(*args)
        t2 = self.theclass(*args)
        self.assertEqual(t1, t2)
        self.assertPrawda(t1 <= t2)
        self.assertPrawda(t1 >= t2)
        self.assertNieprawda(t1 != t2)
        self.assertNieprawda(t1 < t2)
        self.assertNieprawda(t1 > t2)

        dla i w range(len(args)):
            newargs = args[:]
            newargs[i] = args[i] + 1
            t2 = self.theclass(*newargs)   # this jest larger than t1
            self.assertPrawda(t1 < t2)
            self.assertPrawda(t2 > t1)
            self.assertPrawda(t1 <= t2)
            self.assertPrawda(t2 >= t1)
            self.assertPrawda(t1 != t2)
            self.assertPrawda(t2 != t1)
            self.assertNieprawda(t1 == t2)
            self.assertNieprawda(t2 == t1)
            self.assertNieprawda(t1 > t2)
            self.assertNieprawda(t2 < t1)
            self.assertNieprawda(t1 >= t2)
            self.assertNieprawda(t2 <= t1)

        dla badarg w OTHERSTUFF:
            self.assertEqual(t1 == badarg, Nieprawda)
            self.assertEqual(t1 != badarg, Prawda)
            self.assertEqual(badarg == t1, Nieprawda)
            self.assertEqual(badarg != t1, Prawda)

            self.assertRaises(TypeError, lambda: t1 <= badarg)
            self.assertRaises(TypeError, lambda: t1 < badarg)
            self.assertRaises(TypeError, lambda: t1 > badarg)
            self.assertRaises(TypeError, lambda: t1 >= badarg)
            self.assertRaises(TypeError, lambda: badarg <= t1)
            self.assertRaises(TypeError, lambda: badarg < t1)
            self.assertRaises(TypeError, lambda: badarg > t1)
            self.assertRaises(TypeError, lambda: badarg >= t1)

    def test_bad_constructor_arguments(self):
        # bad hours
        self.theclass(0, 0)    # no exception
        self.theclass(23, 0)   # no exception
        self.assertRaises(ValueError, self.theclass, -1, 0)
        self.assertRaises(ValueError, self.theclass, 24, 0)
        # bad minutes
        self.theclass(23, 0)    # no exception
        self.theclass(23, 59)   # no exception
        self.assertRaises(ValueError, self.theclass, 23, -1)
        self.assertRaises(ValueError, self.theclass, 23, 60)
        # bad seconds
        self.theclass(23, 59, 0)    # no exception
        self.theclass(23, 59, 59)   # no exception
        self.assertRaises(ValueError, self.theclass, 23, 59, -1)
        self.assertRaises(ValueError, self.theclass, 23, 59, 60)
        # bad microseconds
        self.theclass(23, 59, 59, 0)        # no exception
        self.theclass(23, 59, 59, 999999)   # no exception
        self.assertRaises(ValueError, self.theclass, 23, 59, 59, -1)
        self.assertRaises(ValueError, self.theclass, 23, 59, 59, 1000000)

    def test_hash_equality(self):
        d = self.theclass(23, 30, 17)
        e = self.theclass(23, 30, 17)
        self.assertEqual(d, e)
        self.assertEqual(hash(d), hash(e))

        dic = {d: 1}
        dic[e] = 2
        self.assertEqual(len(dic), 1)
        self.assertEqual(dic[d], 2)
        self.assertEqual(dic[e], 2)

        d = self.theclass(0,  5, 17)
        e = self.theclass(0,  5, 17)
        self.assertEqual(d, e)
        self.assertEqual(hash(d), hash(e))

        dic = {d: 1}
        dic[e] = 2
        self.assertEqual(len(dic), 1)
        self.assertEqual(dic[d], 2)
        self.assertEqual(dic[e], 2)

    def test_isoformat(self):
        t = self.theclass(4, 5, 1, 123)
        self.assertEqual(t.isoformat(), "04:05:01.000123")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass()
        self.assertEqual(t.isoformat(), "00:00:00")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=1)
        self.assertEqual(t.isoformat(), "00:00:00.000001")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=10)
        self.assertEqual(t.isoformat(), "00:00:00.000010")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=100)
        self.assertEqual(t.isoformat(), "00:00:00.000100")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=1000)
        self.assertEqual(t.isoformat(), "00:00:00.001000")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=10000)
        self.assertEqual(t.isoformat(), "00:00:00.010000")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=100000)
        self.assertEqual(t.isoformat(), "00:00:00.100000")
        self.assertEqual(t.isoformat(), str(t))

    def test_1653736(self):
        # verify it doesn't accept extra keyword arguments
        t = self.theclass(second=1)
        self.assertRaises(TypeError, t.isoformat, foo=3)

    def test_strftime(self):
        t = self.theclass(1, 2, 3, 4)
        self.assertEqual(t.strftime('%H %M %S %f'), "01 02 03 000004")
        # A naive object replaces %z oraz %Z przy empty strings.
        self.assertEqual(t.strftime("'%z' '%Z'"), "'' ''")

    def test_format(self):
        t = self.theclass(1, 2, 3, 4)
        self.assertEqual(t.__format__(''), str(t))

        przy self.assertRaisesRegex(TypeError, '^must be str, nie int$'):
            t.__format__(123)

        # check that a derived class's __str__() gets called
        klasa A(self.theclass):
            def __str__(self):
                zwróć 'A'
        a = A(1, 2, 3, 4)
        self.assertEqual(a.__format__(''), 'A')

        # check that a derived class's strftime gets called
        klasa B(self.theclass):
            def strftime(self, format_spec):
                zwróć 'B'
        b = B(1, 2, 3, 4)
        self.assertEqual(b.__format__(''), str(t))

        dla fmt w ['%H %M %S',
                    ]:
            self.assertEqual(t.__format__(fmt), t.strftime(fmt))
            self.assertEqual(a.__format__(fmt), t.strftime(fmt))
            self.assertEqual(b.__format__(fmt), 'B')

    def test_str(self):
        self.assertEqual(str(self.theclass(1, 2, 3, 4)), "01:02:03.000004")
        self.assertEqual(str(self.theclass(10, 2, 3, 4000)), "10:02:03.004000")
        self.assertEqual(str(self.theclass(0, 2, 3, 400000)), "00:02:03.400000")
        self.assertEqual(str(self.theclass(12, 2, 3, 0)), "12:02:03")
        self.assertEqual(str(self.theclass(23, 15, 0, 0)), "23:15:00")

    def test_repr(self):
        name = 'datetime.' + self.theclass.__name__
        self.assertEqual(repr(self.theclass(1, 2, 3, 4)),
                         "%s(1, 2, 3, 4)" % name)
        self.assertEqual(repr(self.theclass(10, 2, 3, 4000)),
                         "%s(10, 2, 3, 4000)" % name)
        self.assertEqual(repr(self.theclass(0, 2, 3, 400000)),
                         "%s(0, 2, 3, 400000)" % name)
        self.assertEqual(repr(self.theclass(12, 2, 3, 0)),
                         "%s(12, 2, 3)" % name)
        self.assertEqual(repr(self.theclass(23, 15, 0, 0)),
                         "%s(23, 15)" % name)

    def test_resolution_info(self):
        self.assertIsInstance(self.theclass.min, self.theclass)
        self.assertIsInstance(self.theclass.max, self.theclass)
        self.assertIsInstance(self.theclass.resolution, timedelta)
        self.assertPrawda(self.theclass.max > self.theclass.min)

    def test_pickling(self):
        args = 20, 59, 16, 64**2
        orig = self.theclass(*args)
        dla pickler, unpickler, proto w pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)

    def test_pickling_subclass_time(self):
        args = 20, 59, 16, 64**2
        orig = SubclassTime(*args)
        dla pickler, unpickler, proto w pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)

    def test_bool(self):
        # time jest always Prawda.
        cls = self.theclass
        self.assertPrawda(cls(1))
        self.assertPrawda(cls(0, 1))
        self.assertPrawda(cls(0, 0, 1))
        self.assertPrawda(cls(0, 0, 0, 1))
        self.assertPrawda(cls(0))
        self.assertPrawda(cls())

    def test_replace(self):
        cls = self.theclass
        args = [1, 2, 3, 4]
        base = cls(*args)
        self.assertEqual(base, base.replace())

        i = 0
        dla name, newval w (("hour", 5),
                             ("minute", 6),
                             ("second", 7),
                             ("microsecond", 8)):
            newargs = args[:]
            newargs[i] = newval
            expected = cls(*newargs)
            got = base.replace(**{name: newval})
            self.assertEqual(expected, got)
            i += 1

        # Out of bounds.
        base = cls(1)
        self.assertRaises(ValueError, base.replace, hour=24)
        self.assertRaises(ValueError, base.replace, minute=-1)
        self.assertRaises(ValueError, base.replace, second=100)
        self.assertRaises(ValueError, base.replace, microsecond=1000000)

    def test_subclass_time(self):

        klasa C(self.theclass):
            theAnswer = 42

            def __new__(cls, *args, **kws):
                temp = kws.copy()
                extra = temp.pop('extra')
                result = self.theclass.__new__(cls, *args, **temp)
                result.extra = extra
                zwróć result

            def newmeth(self, start):
                zwróć start + self.hour + self.second

        args = 4, 5, 6

        dt1 = self.theclass(*args)
        dt2 = C(*args, **{'extra': 7})

        self.assertEqual(dt2.__class__, C)
        self.assertEqual(dt2.theAnswer, 42)
        self.assertEqual(dt2.extra, 7)
        self.assertEqual(dt1.isoformat(), dt2.isoformat())
        self.assertEqual(dt2.newmeth(-7), dt1.hour + dt1.second - 7)

    def test_backdoor_resistance(self):
        # see TestDate.test_backdoor_resistance().
        base = '2:59.0'
        dla hour_byte w ' ', '9', chr(24), '\xff':
            self.assertRaises(TypeError, self.theclass,
                                         hour_byte + base[1:])
        # Good bytes, but bad tzinfo:
        przy self.assertRaisesRegex(TypeError, '^bad tzinfo state arg$'):
            self.theclass(bytes([1] * len(base)), 'EST')

# A mixin dla classes przy a tzinfo= argument.  Subclasses must define
# theclass jako a klasa atribute, oraz theclass(1, 1, 1, tzinfo=whatever)
# must be legit (which jest true dla time oraz datetime).
klasa TZInfoBase:

    def test_argument_passing(self):
        cls = self.theclass
        # A datetime dalejes itself on, a time dalejes Nic.
        klasa introspective(tzinfo):
            def tzname(self, dt):    zwróć dt oraz "real" albo "none"
            def utcoffset(self, dt):
                zwróć timedelta(minutes = dt oraz 42 albo -42)
            dst = utcoffset

        obj = cls(1, 2, 3, tzinfo=introspective())

        expected = cls jest time oraz "none" albo "real"
        self.assertEqual(obj.tzname(), expected)

        expected = timedelta(minutes=(cls jest time oraz -42 albo 42))
        self.assertEqual(obj.utcoffset(), expected)
        self.assertEqual(obj.dst(), expected)

    def test_bad_tzinfo_classes(self):
        cls = self.theclass
        self.assertRaises(TypeError, cls, 1, 1, 1, tzinfo=12)

        klasa NiceTry(object):
            def __init__(self): dalej
            def utcoffset(self, dt): dalej
        self.assertRaises(TypeError, cls, 1, 1, 1, tzinfo=NiceTry)

        klasa BetterTry(tzinfo):
            def __init__(self): dalej
            def utcoffset(self, dt): dalej
        b = BetterTry()
        t = cls(1, 1, 1, tzinfo=b)
        self.assertIs(t.tzinfo, b)

    def test_utc_offset_out_of_bounds(self):
        klasa Edgy(tzinfo):
            def __init__(self, offset):
                self.offset = timedelta(minutes=offset)
            def utcoffset(self, dt):
                zwróć self.offset

        cls = self.theclass
        dla offset, legit w ((-1440, Nieprawda),
                              (-1439, Prawda),
                              (1439, Prawda),
                              (1440, Nieprawda)):
            jeżeli cls jest time:
                t = cls(1, 2, 3, tzinfo=Edgy(offset))
            albo_inaczej cls jest datetime:
                t = cls(6, 6, 6, 1, 2, 3, tzinfo=Edgy(offset))
            inaczej:
                assert 0, "impossible"
            jeżeli legit:
                aofs = abs(offset)
                h, m = divmod(aofs, 60)
                tag = "%c%02d:%02d" % (offset < 0 oraz '-' albo '+', h, m)
                jeżeli isinstance(t, datetime):
                    t = t.timetz()
                self.assertEqual(str(t), "01:02:03" + tag)
            inaczej:
                self.assertRaises(ValueError, str, t)

    def test_tzinfo_classes(self):
        cls = self.theclass
        klasa C1(tzinfo):
            def utcoffset(self, dt): zwróć Nic
            def dst(self, dt): zwróć Nic
            def tzname(self, dt): zwróć Nic
        dla t w (cls(1, 1, 1),
                  cls(1, 1, 1, tzinfo=Nic),
                  cls(1, 1, 1, tzinfo=C1())):
            self.assertIsNic(t.utcoffset())
            self.assertIsNic(t.dst())
            self.assertIsNic(t.tzname())

        klasa C3(tzinfo):
            def utcoffset(self, dt): zwróć timedelta(minutes=-1439)
            def dst(self, dt): zwróć timedelta(minutes=1439)
            def tzname(self, dt): zwróć "aname"
        t = cls(1, 1, 1, tzinfo=C3())
        self.assertEqual(t.utcoffset(), timedelta(minutes=-1439))
        self.assertEqual(t.dst(), timedelta(minutes=1439))
        self.assertEqual(t.tzname(), "aname")

        # Wrong types.
        klasa C4(tzinfo):
            def utcoffset(self, dt): zwróć "aname"
            def dst(self, dt): zwróć 7
            def tzname(self, dt): zwróć 0
        t = cls(1, 1, 1, tzinfo=C4())
        self.assertRaises(TypeError, t.utcoffset)
        self.assertRaises(TypeError, t.dst)
        self.assertRaises(TypeError, t.tzname)

        # Offset out of range.
        klasa C6(tzinfo):
            def utcoffset(self, dt): zwróć timedelta(hours=-24)
            def dst(self, dt): zwróć timedelta(hours=24)
        t = cls(1, 1, 1, tzinfo=C6())
        self.assertRaises(ValueError, t.utcoffset)
        self.assertRaises(ValueError, t.dst)

        # Not a whole number of minutes.
        klasa C7(tzinfo):
            def utcoffset(self, dt): zwróć timedelta(seconds=61)
            def dst(self, dt): zwróć timedelta(microseconds=-81)
        t = cls(1, 1, 1, tzinfo=C7())
        self.assertRaises(ValueError, t.utcoffset)
        self.assertRaises(ValueError, t.dst)

    def test_aware_compare(self):
        cls = self.theclass

        # Ensure that utcoffset() gets ignored jeżeli the comparands have
        # the same tzinfo member.
        klasa OperandDependentOffset(tzinfo):
            def utcoffset(self, t):
                jeżeli t.minute < 10:
                    # d0 oraz d1 equal after adjustment
                    zwróć timedelta(minutes=t.minute)
                inaczej:
                    # d2 off w the weeds
                    zwróć timedelta(minutes=59)

        base = cls(8, 9, 10, tzinfo=OperandDependentOffset())
        d0 = base.replace(minute=3)
        d1 = base.replace(minute=9)
        d2 = base.replace(minute=11)
        dla x w d0, d1, d2:
            dla y w d0, d1, d2:
                dla op w lt, le, gt, ge, eq, ne:
                    got = op(x, y)
                    expected = op(x.minute, y.minute)
                    self.assertEqual(got, expected)

        # However, jeżeli they're different members, uctoffset jest nie ignored.
        # Note that a time can't actually have an operand-depedent offset,
        # though (and time.utcoffset() dalejes Nic to tzinfo.utcoffset()),
        # so skip this test dla time.
        jeżeli cls jest nie time:
            d0 = base.replace(minute=3, tzinfo=OperandDependentOffset())
            d1 = base.replace(minute=9, tzinfo=OperandDependentOffset())
            d2 = base.replace(minute=11, tzinfo=OperandDependentOffset())
            dla x w d0, d1, d2:
                dla y w d0, d1, d2:
                    got = (x > y) - (x < y)
                    jeżeli (x jest d0 albo x jest d1) oraz (y jest d0 albo y jest d1):
                        expected = 0
                    albo_inaczej x jest y jest d2:
                        expected = 0
                    albo_inaczej x jest d2:
                        expected = -1
                    inaczej:
                        assert y jest d2
                        expected = 1
                    self.assertEqual(got, expected)


# Testing time objects przy a non-Nic tzinfo.
klasa TestTimeTZ(TestTime, TZInfoBase, unittest.TestCase):
    theclass = time

    def test_empty(self):
        t = self.theclass()
        self.assertEqual(t.hour, 0)
        self.assertEqual(t.minute, 0)
        self.assertEqual(t.second, 0)
        self.assertEqual(t.microsecond, 0)
        self.assertIsNic(t.tzinfo)

    def test_zones(self):
        est = FixedOffset(-300, "EST", 1)
        utc = FixedOffset(0, "UTC", -2)
        met = FixedOffset(60, "MET", 3)
        t1 = time( 7, 47, tzinfo=est)
        t2 = time(12, 47, tzinfo=utc)
        t3 = time(13, 47, tzinfo=met)
        t4 = time(microsecond=40)
        t5 = time(microsecond=40, tzinfo=utc)

        self.assertEqual(t1.tzinfo, est)
        self.assertEqual(t2.tzinfo, utc)
        self.assertEqual(t3.tzinfo, met)
        self.assertIsNic(t4.tzinfo)
        self.assertEqual(t5.tzinfo, utc)

        self.assertEqual(t1.utcoffset(), timedelta(minutes=-300))
        self.assertEqual(t2.utcoffset(), timedelta(minutes=0))
        self.assertEqual(t3.utcoffset(), timedelta(minutes=60))
        self.assertIsNic(t4.utcoffset())
        self.assertRaises(TypeError, t1.utcoffset, "no args")

        self.assertEqual(t1.tzname(), "EST")
        self.assertEqual(t2.tzname(), "UTC")
        self.assertEqual(t3.tzname(), "MET")
        self.assertIsNic(t4.tzname())
        self.assertRaises(TypeError, t1.tzname, "no args")

        self.assertEqual(t1.dst(), timedelta(minutes=1))
        self.assertEqual(t2.dst(), timedelta(minutes=-2))
        self.assertEqual(t3.dst(), timedelta(minutes=3))
        self.assertIsNic(t4.dst())
        self.assertRaises(TypeError, t1.dst, "no args")

        self.assertEqual(hash(t1), hash(t2))
        self.assertEqual(hash(t1), hash(t3))
        self.assertEqual(hash(t2), hash(t3))

        self.assertEqual(t1, t2)
        self.assertEqual(t1, t3)
        self.assertEqual(t2, t3)
        self.assertNotEqual(t4, t5) # mixed tz-aware & naive
        self.assertRaises(TypeError, lambda: t4 < t5) # mixed tz-aware & naive
        self.assertRaises(TypeError, lambda: t5 < t4) # mixed tz-aware & naive

        self.assertEqual(str(t1), "07:47:00-05:00")
        self.assertEqual(str(t2), "12:47:00+00:00")
        self.assertEqual(str(t3), "13:47:00+01:00")
        self.assertEqual(str(t4), "00:00:00.000040")
        self.assertEqual(str(t5), "00:00:00.000040+00:00")

        self.assertEqual(t1.isoformat(), "07:47:00-05:00")
        self.assertEqual(t2.isoformat(), "12:47:00+00:00")
        self.assertEqual(t3.isoformat(), "13:47:00+01:00")
        self.assertEqual(t4.isoformat(), "00:00:00.000040")
        self.assertEqual(t5.isoformat(), "00:00:00.000040+00:00")

        d = 'datetime.time'
        self.assertEqual(repr(t1), d + "(7, 47, tzinfo=est)")
        self.assertEqual(repr(t2), d + "(12, 47, tzinfo=utc)")
        self.assertEqual(repr(t3), d + "(13, 47, tzinfo=met)")
        self.assertEqual(repr(t4), d + "(0, 0, 0, 40)")
        self.assertEqual(repr(t5), d + "(0, 0, 0, 40, tzinfo=utc)")

        self.assertEqual(t1.strftime("%H:%M:%S %%Z=%Z %%z=%z"),
                                     "07:47:00 %Z=EST %z=-0500")
        self.assertEqual(t2.strftime("%H:%M:%S %Z %z"), "12:47:00 UTC +0000")
        self.assertEqual(t3.strftime("%H:%M:%S %Z %z"), "13:47:00 MET +0100")

        yuck = FixedOffset(-1439, "%z %Z %%z%%Z")
        t1 = time(23, 59, tzinfo=yuck)
        self.assertEqual(t1.strftime("%H:%M %%Z='%Z' %%z='%z'"),
                                     "23:59 %Z='%z %Z %%z%%Z' %z='-2359'")

        # Check that an invalid tzname result podnieśs an exception.
        klasa Badtzname(tzinfo):
            tz = 42
            def tzname(self, dt): zwróć self.tz
        t = time(2, 3, 4, tzinfo=Badtzname())
        self.assertEqual(t.strftime("%H:%M:%S"), "02:03:04")
        self.assertRaises(TypeError, t.strftime, "%Z")

        # Issue #6697:
        jeżeli '_Fast' w str(self):
            Badtzname.tz = '\ud800'
            self.assertRaises(ValueError, t.strftime, "%Z")

    def test_hash_edge_cases(self):
        # Offsets that overflow a basic time.
        t1 = self.theclass(0, 1, 2, 3, tzinfo=FixedOffset(1439, ""))
        t2 = self.theclass(0, 0, 2, 3, tzinfo=FixedOffset(1438, ""))
        self.assertEqual(hash(t1), hash(t2))

        t1 = self.theclass(23, 58, 6, 100, tzinfo=FixedOffset(-1000, ""))
        t2 = self.theclass(23, 48, 6, 100, tzinfo=FixedOffset(-1010, ""))
        self.assertEqual(hash(t1), hash(t2))

    def test_pickling(self):
        # Try one without a tzinfo.
        args = 20, 59, 16, 64**2
        orig = self.theclass(*args)
        dla pickler, unpickler, proto w pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)

        # Try one przy a tzinfo.
        tinfo = PicklableFixedOffset(-300, 'cookie')
        orig = self.theclass(5, 6, 7, tzinfo=tinfo)
        dla pickler, unpickler, proto w pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)
            self.assertIsInstance(derived.tzinfo, PicklableFixedOffset)
            self.assertEqual(derived.utcoffset(), timedelta(minutes=-300))
            self.assertEqual(derived.tzname(), 'cookie')

    def test_more_bool(self):
        # time jest always Prawda.
        cls = self.theclass

        t = cls(0, tzinfo=FixedOffset(-300, ""))
        self.assertPrawda(t)

        t = cls(5, tzinfo=FixedOffset(-300, ""))
        self.assertPrawda(t)

        t = cls(5, tzinfo=FixedOffset(300, ""))
        self.assertPrawda(t)

        t = cls(23, 59, tzinfo=FixedOffset(23*60 + 59, ""))
        self.assertPrawda(t)

    def test_replace(self):
        cls = self.theclass
        z100 = FixedOffset(100, "+100")
        zm200 = FixedOffset(timedelta(minutes=-200), "-200")
        args = [1, 2, 3, 4, z100]
        base = cls(*args)
        self.assertEqual(base, base.replace())

        i = 0
        dla name, newval w (("hour", 5),
                             ("minute", 6),
                             ("second", 7),
                             ("microsecond", 8),
                             ("tzinfo", zm200)):
            newargs = args[:]
            newargs[i] = newval
            expected = cls(*newargs)
            got = base.replace(**{name: newval})
            self.assertEqual(expected, got)
            i += 1

        # Ensure we can get rid of a tzinfo.
        self.assertEqual(base.tzname(), "+100")
        base2 = base.replace(tzinfo=Nic)
        self.assertIsNic(base2.tzinfo)
        self.assertIsNic(base2.tzname())

        # Ensure we can add one.
        base3 = base2.replace(tzinfo=z100)
        self.assertEqual(base, base3)
        self.assertIs(base.tzinfo, base3.tzinfo)

        # Out of bounds.
        base = cls(1)
        self.assertRaises(ValueError, base.replace, hour=24)
        self.assertRaises(ValueError, base.replace, minute=-1)
        self.assertRaises(ValueError, base.replace, second=100)
        self.assertRaises(ValueError, base.replace, microsecond=1000000)

    def test_mixed_compare(self):
        t1 = time(1, 2, 3)
        t2 = time(1, 2, 3)
        self.assertEqual(t1, t2)
        t2 = t2.replace(tzinfo=Nic)
        self.assertEqual(t1, t2)
        t2 = t2.replace(tzinfo=FixedOffset(Nic, ""))
        self.assertEqual(t1, t2)
        t2 = t2.replace(tzinfo=FixedOffset(0, ""))
        self.assertNotEqual(t1, t2)

        # In time w/ identical tzinfo objects, utcoffset jest ignored.
        klasa Varies(tzinfo):
            def __init__(self):
                self.offset = timedelta(minutes=22)
            def utcoffset(self, t):
                self.offset += timedelta(minutes=1)
                zwróć self.offset

        v = Varies()
        t1 = t2.replace(tzinfo=v)
        t2 = t2.replace(tzinfo=v)
        self.assertEqual(t1.utcoffset(), timedelta(minutes=23))
        self.assertEqual(t2.utcoffset(), timedelta(minutes=24))
        self.assertEqual(t1, t2)

        # But jeżeli they're nie identical, it isn't ignored.
        t2 = t2.replace(tzinfo=Varies())
        self.assertPrawda(t1 < t2)  # t1's offset counter still going up

    def test_subclass_timetz(self):

        klasa C(self.theclass):
            theAnswer = 42

            def __new__(cls, *args, **kws):
                temp = kws.copy()
                extra = temp.pop('extra')
                result = self.theclass.__new__(cls, *args, **temp)
                result.extra = extra
                zwróć result

            def newmeth(self, start):
                zwróć start + self.hour + self.second

        args = 4, 5, 6, 500, FixedOffset(-300, "EST", 1)

        dt1 = self.theclass(*args)
        dt2 = C(*args, **{'extra': 7})

        self.assertEqual(dt2.__class__, C)
        self.assertEqual(dt2.theAnswer, 42)
        self.assertEqual(dt2.extra, 7)
        self.assertEqual(dt1.utcoffset(), dt2.utcoffset())
        self.assertEqual(dt2.newmeth(-7), dt1.hour + dt1.second - 7)


# Testing datetime objects przy a non-Nic tzinfo.

klasa TestDateTimeTZ(TestDateTime, TZInfoBase, unittest.TestCase):
    theclass = datetime

    def test_trivial(self):
        dt = self.theclass(1, 2, 3, 4, 5, 6, 7)
        self.assertEqual(dt.year, 1)
        self.assertEqual(dt.month, 2)
        self.assertEqual(dt.day, 3)
        self.assertEqual(dt.hour, 4)
        self.assertEqual(dt.minute, 5)
        self.assertEqual(dt.second, 6)
        self.assertEqual(dt.microsecond, 7)
        self.assertEqual(dt.tzinfo, Nic)

    def test_even_more_compare(self):
        # The test_compare() oraz test_more_compare() inherited z TestDate
        # oraz TestDateTime covered non-tzinfo cases.

        # Smallest possible after UTC adjustment.
        t1 = self.theclass(1, 1, 1, tzinfo=FixedOffset(1439, ""))
        # Largest possible after UTC adjustment.
        t2 = self.theclass(MAXYEAR, 12, 31, 23, 59, 59, 999999,
                           tzinfo=FixedOffset(-1439, ""))

        # Make sure those compare correctly, oraz w/o overflow.
        self.assertPrawda(t1 < t2)
        self.assertPrawda(t1 != t2)
        self.assertPrawda(t2 > t1)

        self.assertEqual(t1, t1)
        self.assertEqual(t2, t2)

        # Equal afer adjustment.
        t1 = self.theclass(1, 12, 31, 23, 59, tzinfo=FixedOffset(1, ""))
        t2 = self.theclass(2, 1, 1, 3, 13, tzinfo=FixedOffset(3*60+13+2, ""))
        self.assertEqual(t1, t2)

        # Change t1 nie to subtract a minute, oraz t1 should be larger.
        t1 = self.theclass(1, 12, 31, 23, 59, tzinfo=FixedOffset(0, ""))
        self.assertPrawda(t1 > t2)

        # Change t1 to subtract 2 minutes, oraz t1 should be smaller.
        t1 = self.theclass(1, 12, 31, 23, 59, tzinfo=FixedOffset(2, ""))
        self.assertPrawda(t1 < t2)

        # Back to the original t1, but make seconds resolve it.
        t1 = self.theclass(1, 12, 31, 23, 59, tzinfo=FixedOffset(1, ""),
                           second=1)
        self.assertPrawda(t1 > t2)

        # Likewise, but make microseconds resolve it.
        t1 = self.theclass(1, 12, 31, 23, 59, tzinfo=FixedOffset(1, ""),
                           microsecond=1)
        self.assertPrawda(t1 > t2)

        # Make t2 naive oraz it should differ.
        t2 = self.theclass.min
        self.assertNotEqual(t1, t2)
        self.assertEqual(t2, t2)

        # It's also naive jeżeli it has tzinfo but tzinfo.utcoffset() jest Nic.
        klasa Naive(tzinfo):
            def utcoffset(self, dt): zwróć Nic
        t2 = self.theclass(5, 6, 7, tzinfo=Naive())
        self.assertNotEqual(t1, t2)
        self.assertEqual(t2, t2)

        # OTOH, it's OK to compare two of these mixing the two ways of being
        # naive.
        t1 = self.theclass(5, 6, 7)
        self.assertEqual(t1, t2)

        # Try a bogus uctoffset.
        klasa Bogus(tzinfo):
            def utcoffset(self, dt):
                zwróć timedelta(minutes=1440) # out of bounds
        t1 = self.theclass(2, 2, 2, tzinfo=Bogus())
        t2 = self.theclass(2, 2, 2, tzinfo=FixedOffset(0, ""))
        self.assertRaises(ValueError, lambda: t1 == t2)

    def test_pickling(self):
        # Try one without a tzinfo.
        args = 6, 7, 23, 20, 59, 1, 64**2
        orig = self.theclass(*args)
        dla pickler, unpickler, proto w pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)

        # Try one przy a tzinfo.
        tinfo = PicklableFixedOffset(-300, 'cookie')
        orig = self.theclass(*args, **{'tzinfo': tinfo})
        derived = self.theclass(1, 1, 1, tzinfo=FixedOffset(0, "", 0))
        dla pickler, unpickler, proto w pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)
            self.assertIsInstance(derived.tzinfo, PicklableFixedOffset)
            self.assertEqual(derived.utcoffset(), timedelta(minutes=-300))
            self.assertEqual(derived.tzname(), 'cookie')

    def test_extreme_hashes(self):
        # If an attempt jest made to hash these via subtracting the offset
        # then hashing a datetime object, OverflowError results.  The
        # Python implementation used to blow up here.
        t = self.theclass(1, 1, 1, tzinfo=FixedOffset(1439, ""))
        hash(t)
        t = self.theclass(MAXYEAR, 12, 31, 23, 59, 59, 999999,
                          tzinfo=FixedOffset(-1439, ""))
        hash(t)

        # OTOH, an OOB offset should blow up.
        t = self.theclass(5, 5, 5, tzinfo=FixedOffset(-1440, ""))
        self.assertRaises(ValueError, hash, t)

    def test_zones(self):
        est = FixedOffset(-300, "EST")
        utc = FixedOffset(0, "UTC")
        met = FixedOffset(60, "MET")
        t1 = datetime(2002, 3, 19,  7, 47, tzinfo=est)
        t2 = datetime(2002, 3, 19, 12, 47, tzinfo=utc)
        t3 = datetime(2002, 3, 19, 13, 47, tzinfo=met)
        self.assertEqual(t1.tzinfo, est)
        self.assertEqual(t2.tzinfo, utc)
        self.assertEqual(t3.tzinfo, met)
        self.assertEqual(t1.utcoffset(), timedelta(minutes=-300))
        self.assertEqual(t2.utcoffset(), timedelta(minutes=0))
        self.assertEqual(t3.utcoffset(), timedelta(minutes=60))
        self.assertEqual(t1.tzname(), "EST")
        self.assertEqual(t2.tzname(), "UTC")
        self.assertEqual(t3.tzname(), "MET")
        self.assertEqual(hash(t1), hash(t2))
        self.assertEqual(hash(t1), hash(t3))
        self.assertEqual(hash(t2), hash(t3))
        self.assertEqual(t1, t2)
        self.assertEqual(t1, t3)
        self.assertEqual(t2, t3)
        self.assertEqual(str(t1), "2002-03-19 07:47:00-05:00")
        self.assertEqual(str(t2), "2002-03-19 12:47:00+00:00")
        self.assertEqual(str(t3), "2002-03-19 13:47:00+01:00")
        d = 'datetime.datetime(2002, 3, 19, '
        self.assertEqual(repr(t1), d + "7, 47, tzinfo=est)")
        self.assertEqual(repr(t2), d + "12, 47, tzinfo=utc)")
        self.assertEqual(repr(t3), d + "13, 47, tzinfo=met)")

    def test_combine(self):
        met = FixedOffset(60, "MET")
        d = date(2002, 3, 4)
        tz = time(18, 45, 3, 1234, tzinfo=met)
        dt = datetime.combine(d, tz)
        self.assertEqual(dt, datetime(2002, 3, 4, 18, 45, 3, 1234,
                                        tzinfo=met))

    def test_extract(self):
        met = FixedOffset(60, "MET")
        dt = self.theclass(2002, 3, 4, 18, 45, 3, 1234, tzinfo=met)
        self.assertEqual(dt.date(), date(2002, 3, 4))
        self.assertEqual(dt.time(), time(18, 45, 3, 1234))
        self.assertEqual(dt.timetz(), time(18, 45, 3, 1234, tzinfo=met))

    def test_tz_aware_arithmetic(self):
        zaimportuj random

        now = self.theclass.now()
        tz55 = FixedOffset(-330, "west 5:30")
        timeaware = now.time().replace(tzinfo=tz55)
        nowaware = self.theclass.combine(now.date(), timeaware)
        self.assertIs(nowaware.tzinfo, tz55)
        self.assertEqual(nowaware.timetz(), timeaware)

        # Can't mix aware oraz non-aware.
        self.assertRaises(TypeError, lambda: now - nowaware)
        self.assertRaises(TypeError, lambda: nowaware - now)

        # And adding datetime's doesn't make sense, aware albo not.
        self.assertRaises(TypeError, lambda: now + nowaware)
        self.assertRaises(TypeError, lambda: nowaware + now)
        self.assertRaises(TypeError, lambda: nowaware + nowaware)

        # Subtracting should uzyskaj 0.
        self.assertEqual(now - now, timedelta(0))
        self.assertEqual(nowaware - nowaware, timedelta(0))

        # Adding a delta should preserve tzinfo.
        delta = timedelta(weeks=1, minutes=12, microseconds=5678)
        nowawareplus = nowaware + delta
        self.assertIs(nowaware.tzinfo, tz55)
        nowawareplus2 = delta + nowaware
        self.assertIs(nowawareplus2.tzinfo, tz55)
        self.assertEqual(nowawareplus, nowawareplus2)

        # that - delta should be what we started with, oraz that - what we
        # started przy should be delta.
        diff = nowawareplus - delta
        self.assertIs(diff.tzinfo, tz55)
        self.assertEqual(nowaware, diff)
        self.assertRaises(TypeError, lambda: delta - nowawareplus)
        self.assertEqual(nowawareplus - nowaware, delta)

        # Make up a random timezone.
        tzr = FixedOffset(random.randrange(-1439, 1440), "randomtimezone")
        # Attach it to nowawareplus.
        nowawareplus = nowawareplus.replace(tzinfo=tzr)
        self.assertIs(nowawareplus.tzinfo, tzr)
        # Make sure the difference takes the timezone adjustments into account.
        got = nowaware - nowawareplus
        # Expected:  (nowaware base - nowaware offset) -
        #            (nowawareplus base - nowawareplus offset) =
        #            (nowaware base - nowawareplus base) +
        #            (nowawareplus offset - nowaware offset) =
        #            -delta + nowawareplus offset - nowaware offset
        expected = nowawareplus.utcoffset() - nowaware.utcoffset() - delta
        self.assertEqual(got, expected)

        # Try max possible difference.
        min = self.theclass(1, 1, 1, tzinfo=FixedOffset(1439, "min"))
        max = self.theclass(MAXYEAR, 12, 31, 23, 59, 59, 999999,
                            tzinfo=FixedOffset(-1439, "max"))
        maxdiff = max - min
        self.assertEqual(maxdiff, self.theclass.max - self.theclass.min +
                                  timedelta(minutes=2*1439))
        # Different tzinfo, but the same offset
        tza = timezone(HOUR, 'A')
        tzb = timezone(HOUR, 'B')
        delta = min.replace(tzinfo=tza) - max.replace(tzinfo=tzb)
        self.assertEqual(delta, self.theclass.min - self.theclass.max)

    def test_tzinfo_now(self):
        meth = self.theclass.now
        # Ensure it doesn't require tzinfo (i.e., that this doesn't blow up).
        base = meth()
        # Try przy oraz without naming the keyword.
        off42 = FixedOffset(42, "42")
        another = meth(off42)
        again = meth(tz=off42)
        self.assertIs(another.tzinfo, again.tzinfo)
        self.assertEqual(another.utcoffset(), timedelta(minutes=42))
        # Bad argument przy oraz w/o naming the keyword.
        self.assertRaises(TypeError, meth, 16)
        self.assertRaises(TypeError, meth, tzinfo=16)
        # Bad keyword name.
        self.assertRaises(TypeError, meth, tinfo=off42)
        # Too many args.
        self.assertRaises(TypeError, meth, off42, off42)

        # We don't know which time zone we're in, oraz don't have a tzinfo
        # klasa to represent it, so seeing whether a tz argument actually
        # does a conversion jest tricky.
        utc = FixedOffset(0, "utc", 0)
        dla weirdtz w [FixedOffset(timedelta(hours=15, minutes=58), "weirdtz", 0),
                        timezone(timedelta(hours=15, minutes=58), "weirdtz"),]:
            dla dummy w range(3):
                now = datetime.now(weirdtz)
                self.assertIs(now.tzinfo, weirdtz)
                utcnow = datetime.utcnow().replace(tzinfo=utc)
                now2 = utcnow.astimezone(weirdtz)
                jeżeli abs(now - now2) < timedelta(seconds=30):
                    przerwij
                # Else the code jest broken, albo more than 30 seconds dalejed between
                # calls; assuming the latter, just try again.
            inaczej:
                # Three strikes oraz we're out.
                self.fail("utcnow(), now(tz), albo astimezone() may be broken")

    def test_tzinfo_fromtimestamp(self):
        zaimportuj time
        meth = self.theclass.fromtimestamp
        ts = time.time()
        # Ensure it doesn't require tzinfo (i.e., that this doesn't blow up).
        base = meth(ts)
        # Try przy oraz without naming the keyword.
        off42 = FixedOffset(42, "42")
        another = meth(ts, off42)
        again = meth(ts, tz=off42)
        self.assertIs(another.tzinfo, again.tzinfo)
        self.assertEqual(another.utcoffset(), timedelta(minutes=42))
        # Bad argument przy oraz w/o naming the keyword.
        self.assertRaises(TypeError, meth, ts, 16)
        self.assertRaises(TypeError, meth, ts, tzinfo=16)
        # Bad keyword name.
        self.assertRaises(TypeError, meth, ts, tinfo=off42)
        # Too many args.
        self.assertRaises(TypeError, meth, ts, off42, off42)
        # Too few args.
        self.assertRaises(TypeError, meth)

        # Try to make sure tz= actually does some conversion.
        timestamp = 1000000000
        utcdatetime = datetime.utcfromtimestamp(timestamp)
        # In POSIX (epoch 1970), that's 2001-09-09 01:46:40 UTC, give albo take.
        # But on some flavor of Mac, it's nowhere near that.  So we can't have
        # any idea here what time that actually is, we can only test that
        # relative changes match.
        utcoffset = timedelta(hours=-15, minutes=39) # arbitrary, but nie zero
        tz = FixedOffset(utcoffset, "tz", 0)
        expected = utcdatetime + utcoffset
        got = datetime.fromtimestamp(timestamp, tz)
        self.assertEqual(expected, got.replace(tzinfo=Nic))

    def test_tzinfo_utcnow(self):
        meth = self.theclass.utcnow
        # Ensure it doesn't require tzinfo (i.e., that this doesn't blow up).
        base = meth()
        # Try przy oraz without naming the keyword; dla whatever reason,
        # utcnow() doesn't accept a tzinfo argument.
        off42 = FixedOffset(42, "42")
        self.assertRaises(TypeError, meth, off42)
        self.assertRaises(TypeError, meth, tzinfo=off42)

    def test_tzinfo_utcfromtimestamp(self):
        zaimportuj time
        meth = self.theclass.utcfromtimestamp
        ts = time.time()
        # Ensure it doesn't require tzinfo (i.e., that this doesn't blow up).
        base = meth(ts)
        # Try przy oraz without naming the keyword; dla whatever reason,
        # utcfromtimestamp() doesn't accept a tzinfo argument.
        off42 = FixedOffset(42, "42")
        self.assertRaises(TypeError, meth, ts, off42)
        self.assertRaises(TypeError, meth, ts, tzinfo=off42)

    def test_tzinfo_timetuple(self):
        # TestDateTime tested most of this.  datetime adds a twist to the
        # DST flag.
        klasa DST(tzinfo):
            def __init__(self, dstvalue):
                jeżeli isinstance(dstvalue, int):
                    dstvalue = timedelta(minutes=dstvalue)
                self.dstvalue = dstvalue
            def dst(self, dt):
                zwróć self.dstvalue

        cls = self.theclass
        dla dstvalue, flag w (-33, 1), (33, 1), (0, 0), (Nic, -1):
            d = cls(1, 1, 1, 10, 20, 30, 40, tzinfo=DST(dstvalue))
            t = d.timetuple()
            self.assertEqual(1, t.tm_year)
            self.assertEqual(1, t.tm_mon)
            self.assertEqual(1, t.tm_mday)
            self.assertEqual(10, t.tm_hour)
            self.assertEqual(20, t.tm_min)
            self.assertEqual(30, t.tm_sec)
            self.assertEqual(0, t.tm_wday)
            self.assertEqual(1, t.tm_yday)
            self.assertEqual(flag, t.tm_isdst)

        # dst() returns wrong type.
        self.assertRaises(TypeError, cls(1, 1, 1, tzinfo=DST("x")).timetuple)

        # dst() at the edge.
        self.assertEqual(cls(1,1,1, tzinfo=DST(1439)).timetuple().tm_isdst, 1)
        self.assertEqual(cls(1,1,1, tzinfo=DST(-1439)).timetuple().tm_isdst, 1)

        # dst() out of range.
        self.assertRaises(ValueError, cls(1,1,1, tzinfo=DST(1440)).timetuple)
        self.assertRaises(ValueError, cls(1,1,1, tzinfo=DST(-1440)).timetuple)

    def test_utctimetuple(self):
        klasa DST(tzinfo):
            def __init__(self, dstvalue=0):
                jeżeli isinstance(dstvalue, int):
                    dstvalue = timedelta(minutes=dstvalue)
                self.dstvalue = dstvalue
            def dst(self, dt):
                zwróć self.dstvalue

        cls = self.theclass
        # This can't work:  DST didn't implement utcoffset.
        self.assertRaises(NotImplementedError,
                          cls(1, 1, 1, tzinfo=DST(0)).utcoffset)

        klasa UOFS(DST):
            def __init__(self, uofs, dofs=Nic):
                DST.__init__(self, dofs)
                self.uofs = timedelta(minutes=uofs)
            def utcoffset(self, dt):
                zwróć self.uofs

        dla dstvalue w -33, 33, 0, Nic:
            d = cls(1, 2, 3, 10, 20, 30, 40, tzinfo=UOFS(-53, dstvalue))
            t = d.utctimetuple()
            self.assertEqual(d.year, t.tm_year)
            self.assertEqual(d.month, t.tm_mon)
            self.assertEqual(d.day, t.tm_mday)
            self.assertEqual(11, t.tm_hour) # 20mm + 53mm = 1hn + 13mm
            self.assertEqual(13, t.tm_min)
            self.assertEqual(d.second, t.tm_sec)
            self.assertEqual(d.weekday(), t.tm_wday)
            self.assertEqual(d.toordinal() - date(1, 1, 1).toordinal() + 1,
                             t.tm_yday)
            # Ensure tm_isdst jest 0 regardless of what dst() says: DST
            # jest never w effect dla a UTC time.
            self.assertEqual(0, t.tm_isdst)

        # For naive datetime, utctimetuple == timetuple wyjąwszy dla isdst
        d = cls(1, 2, 3, 10, 20, 30, 40)
        t = d.utctimetuple()
        self.assertEqual(t[:-1], d.timetuple()[:-1])
        self.assertEqual(0, t.tm_isdst)
        # Same jeżeli utcoffset jest Nic
        klasa NOFS(DST):
            def utcoffset(self, dt):
                zwróć Nic
        d = cls(1, 2, 3, 10, 20, 30, 40, tzinfo=NOFS())
        t = d.utctimetuple()
        self.assertEqual(t[:-1], d.timetuple()[:-1])
        self.assertEqual(0, t.tm_isdst)
        # Check that bad tzinfo jest detected
        klasa BOFS(DST):
            def utcoffset(self, dt):
                zwróć "EST"
        d = cls(1, 2, 3, 10, 20, 30, 40, tzinfo=BOFS())
        self.assertRaises(TypeError, d.utctimetuple)

        # Check that utctimetuple() jest the same as
        # astimezone(utc).timetuple()
        d = cls(2010, 11, 13, 14, 15, 16, 171819)
        dla tz w [timezone.min, timezone.utc, timezone.max]:
            dtz = d.replace(tzinfo=tz)
            self.assertEqual(dtz.utctimetuple()[:-1],
                             dtz.astimezone(timezone.utc).timetuple()[:-1])
        # At the edges, UTC adjustment can produce years out-of-range
        # dla a datetime object.  Ensure that an OverflowError jest
        # podnieśd.
        tiny = cls(MINYEAR, 1, 1, 0, 0, 37, tzinfo=UOFS(1439))
        # That goes back 1 minute less than a full day.
        self.assertRaises(OverflowError, tiny.utctimetuple)

        huge = cls(MAXYEAR, 12, 31, 23, 59, 37, 999999, tzinfo=UOFS(-1439))
        # That goes forward 1 minute less than a full day.
        self.assertRaises(OverflowError, huge.utctimetuple)
        # More overflow cases
        tiny = cls.min.replace(tzinfo=timezone(MINUTE))
        self.assertRaises(OverflowError, tiny.utctimetuple)
        huge = cls.max.replace(tzinfo=timezone(-MINUTE))
        self.assertRaises(OverflowError, huge.utctimetuple)

    def test_tzinfo_isoformat(self):
        zero = FixedOffset(0, "+00:00")
        plus = FixedOffset(220, "+03:40")
        minus = FixedOffset(-231, "-03:51")
        unknown = FixedOffset(Nic, "")

        cls = self.theclass
        datestr = '0001-02-03'
        dla ofs w Nic, zero, plus, minus, unknown:
            dla us w 0, 987001:
                d = cls(1, 2, 3, 4, 5, 59, us, tzinfo=ofs)
                timestr = '04:05:59' + (us oraz '.987001' albo '')
                ofsstr = ofs jest nie Nic oraz d.tzname() albo ''
                tailstr = timestr + ofsstr
                iso = d.isoformat()
                self.assertEqual(iso, datestr + 'T' + tailstr)
                self.assertEqual(iso, d.isoformat('T'))
                self.assertEqual(d.isoformat('k'), datestr + 'k' + tailstr)
                self.assertEqual(d.isoformat('\u1234'), datestr + '\u1234' + tailstr)
                self.assertEqual(str(d), datestr + ' ' + tailstr)

    def test_replace(self):
        cls = self.theclass
        z100 = FixedOffset(100, "+100")
        zm200 = FixedOffset(timedelta(minutes=-200), "-200")
        args = [1, 2, 3, 4, 5, 6, 7, z100]
        base = cls(*args)
        self.assertEqual(base, base.replace())

        i = 0
        dla name, newval w (("year", 2),
                             ("month", 3),
                             ("day", 4),
                             ("hour", 5),
                             ("minute", 6),
                             ("second", 7),
                             ("microsecond", 8),
                             ("tzinfo", zm200)):
            newargs = args[:]
            newargs[i] = newval
            expected = cls(*newargs)
            got = base.replace(**{name: newval})
            self.assertEqual(expected, got)
            i += 1

        # Ensure we can get rid of a tzinfo.
        self.assertEqual(base.tzname(), "+100")
        base2 = base.replace(tzinfo=Nic)
        self.assertIsNic(base2.tzinfo)
        self.assertIsNic(base2.tzname())

        # Ensure we can add one.
        base3 = base2.replace(tzinfo=z100)
        self.assertEqual(base, base3)
        self.assertIs(base.tzinfo, base3.tzinfo)

        # Out of bounds.
        base = cls(2000, 2, 29)
        self.assertRaises(ValueError, base.replace, year=2001)

    def test_more_astimezone(self):
        # The inherited test_astimezone covered some trivial oraz error cases.
        fnone = FixedOffset(Nic, "Nic")
        f44m = FixedOffset(44, "44")
        fm5h = FixedOffset(-timedelta(hours=5), "m300")

        dt = self.theclass.now(tz=f44m)
        self.assertIs(dt.tzinfo, f44m)
        # Replacing przy degenerate tzinfo podnieśs an exception.
        self.assertRaises(ValueError, dt.astimezone, fnone)
        # Replacing przy same tzinfo makes no change.
        x = dt.astimezone(dt.tzinfo)
        self.assertIs(x.tzinfo, f44m)
        self.assertEqual(x.date(), dt.date())
        self.assertEqual(x.time(), dt.time())

        # Replacing przy different tzinfo does adjust.
        got = dt.astimezone(fm5h)
        self.assertIs(got.tzinfo, fm5h)
        self.assertEqual(got.utcoffset(), timedelta(hours=-5))
        expected = dt - dt.utcoffset()  # w effect, convert to UTC
        expected += fm5h.utcoffset(dt)  # oraz z there to local time
        expected = expected.replace(tzinfo=fm5h) # oraz attach new tzinfo
        self.assertEqual(got.date(), expected.date())
        self.assertEqual(got.time(), expected.time())
        self.assertEqual(got.timetz(), expected.timetz())
        self.assertIs(got.tzinfo, expected.tzinfo)
        self.assertEqual(got, expected)

    @support.run_with_tz('UTC')
    def test_astimezone_default_utc(self):
        dt = self.theclass.now(timezone.utc)
        self.assertEqual(dt.astimezone(Nic), dt)
        self.assertEqual(dt.astimezone(), dt)

    # Note that offset w TZ variable has the opposite sign to that
    # produced by %z directive.
    @support.run_with_tz('EST+05EDT,M3.2.0,M11.1.0')
    def test_astimezone_default_eastern(self):
        dt = self.theclass(2012, 11, 4, 6, 30, tzinfo=timezone.utc)
        local = dt.astimezone()
        self.assertEqual(dt, local)
        self.assertEqual(local.strftime("%z %Z"), "-0500 EST")
        dt = self.theclass(2012, 11, 4, 5, 30, tzinfo=timezone.utc)
        local = dt.astimezone()
        self.assertEqual(dt, local)
        self.assertEqual(local.strftime("%z %Z"), "-0400 EDT")

    def test_aware_subtract(self):
        cls = self.theclass

        # Ensure that utcoffset() jest ignored when the operands have the
        # same tzinfo member.
        klasa OperandDependentOffset(tzinfo):
            def utcoffset(self, t):
                jeżeli t.minute < 10:
                    # d0 oraz d1 equal after adjustment
                    zwróć timedelta(minutes=t.minute)
                inaczej:
                    # d2 off w the weeds
                    zwróć timedelta(minutes=59)

        base = cls(8, 9, 10, 11, 12, 13, 14, tzinfo=OperandDependentOffset())
        d0 = base.replace(minute=3)
        d1 = base.replace(minute=9)
        d2 = base.replace(minute=11)
        dla x w d0, d1, d2:
            dla y w d0, d1, d2:
                got = x - y
                expected = timedelta(minutes=x.minute - y.minute)
                self.assertEqual(got, expected)

        # OTOH, jeżeli the tzinfo members are distinct, utcoffsets aren't
        # ignored.
        base = cls(8, 9, 10, 11, 12, 13, 14)
        d0 = base.replace(minute=3, tzinfo=OperandDependentOffset())
        d1 = base.replace(minute=9, tzinfo=OperandDependentOffset())
        d2 = base.replace(minute=11, tzinfo=OperandDependentOffset())
        dla x w d0, d1, d2:
            dla y w d0, d1, d2:
                got = x - y
                jeżeli (x jest d0 albo x jest d1) oraz (y jest d0 albo y jest d1):
                    expected = timedelta(0)
                albo_inaczej x jest y jest d2:
                    expected = timedelta(0)
                albo_inaczej x jest d2:
                    expected = timedelta(minutes=(11-59)-0)
                inaczej:
                    assert y jest d2
                    expected = timedelta(minutes=0-(11-59))
                self.assertEqual(got, expected)

    def test_mixed_compare(self):
        t1 = datetime(1, 2, 3, 4, 5, 6, 7)
        t2 = datetime(1, 2, 3, 4, 5, 6, 7)
        self.assertEqual(t1, t2)
        t2 = t2.replace(tzinfo=Nic)
        self.assertEqual(t1, t2)
        t2 = t2.replace(tzinfo=FixedOffset(Nic, ""))
        self.assertEqual(t1, t2)
        t2 = t2.replace(tzinfo=FixedOffset(0, ""))
        self.assertNotEqual(t1, t2)

        # In datetime w/ identical tzinfo objects, utcoffset jest ignored.
        klasa Varies(tzinfo):
            def __init__(self):
                self.offset = timedelta(minutes=22)
            def utcoffset(self, t):
                self.offset += timedelta(minutes=1)
                zwróć self.offset

        v = Varies()
        t1 = t2.replace(tzinfo=v)
        t2 = t2.replace(tzinfo=v)
        self.assertEqual(t1.utcoffset(), timedelta(minutes=23))
        self.assertEqual(t2.utcoffset(), timedelta(minutes=24))
        self.assertEqual(t1, t2)

        # But jeżeli they're nie identical, it isn't ignored.
        t2 = t2.replace(tzinfo=Varies())
        self.assertPrawda(t1 < t2)  # t1's offset counter still going up

    def test_subclass_datetimetz(self):

        klasa C(self.theclass):
            theAnswer = 42

            def __new__(cls, *args, **kws):
                temp = kws.copy()
                extra = temp.pop('extra')
                result = self.theclass.__new__(cls, *args, **temp)
                result.extra = extra
                zwróć result

            def newmeth(self, start):
                zwróć start + self.hour + self.year

        args = 2002, 12, 31, 4, 5, 6, 500, FixedOffset(-300, "EST", 1)

        dt1 = self.theclass(*args)
        dt2 = C(*args, **{'extra': 7})

        self.assertEqual(dt2.__class__, C)
        self.assertEqual(dt2.theAnswer, 42)
        self.assertEqual(dt2.extra, 7)
        self.assertEqual(dt1.utcoffset(), dt2.utcoffset())
        self.assertEqual(dt2.newmeth(-7), dt1.hour + dt1.year - 7)

# Pain to set up DST-aware tzinfo classes.

def first_sunday_on_or_after(dt):
    days_to_go = 6 - dt.weekday()
    jeżeli days_to_go:
        dt += timedelta(days_to_go)
    zwróć dt

ZERO = timedelta(0)
MINUTE = timedelta(minutes=1)
HOUR = timedelta(hours=1)
DAY = timedelta(days=1)
# In the US, DST starts at 2am (standard time) on the first Sunday w April.
DSTSTART = datetime(1, 4, 1, 2)
# oraz ends at 2am (DST time; 1am standard time) on the last Sunday of Oct,
# which jest the first Sunday on albo after Oct 25.  Because we view 1:MM as
# being standard time on that day, there jest no spelling w local time of
# the last hour of DST (that's 1:MM DST, but 1:MM jest taken jako standard time).
DSTEND = datetime(1, 10, 25, 1)

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
            # An exception instead may be sensible here, w one albo more of
            # the cases.
            zwróć ZERO
        assert dt.tzinfo jest self

        # Find first Sunday w April.
        start = first_sunday_on_or_after(DSTSTART.replace(year=dt.year))
        assert start.weekday() == 6 oraz start.month == 4 oraz start.day <= 7

        # Find last Sunday w October.
        end = first_sunday_on_or_after(DSTEND.replace(year=dt.year))
        assert end.weekday() == 6 oraz end.month == 10 oraz end.day >= 25

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
utc_real = FixedOffset(0, "UTC", 0)
# For better test coverage, we want another flavor of UTC that's west of
# the Eastern oraz Pacific timezones.
utc_fake = FixedOffset(-12*60, "UTCfake", 0)

klasa TestTimezoneConversions(unittest.TestCase):
    # The DST switch times dla 2002, w std time.
    dston = datetime(2002, 4, 7, 2)
    dstoff = datetime(2002, 10, 27, 1)

    theclass = datetime

    # Check a time that's inside DST.
    def checkinside(self, dt, tz, utc, dston, dstoff):
        self.assertEqual(dt.dst(), HOUR)

        # Conversion to our own timezone jest always an identity.
        self.assertEqual(dt.astimezone(tz), dt)

        asutc = dt.astimezone(utc)
        there_and_back = asutc.astimezone(tz)

        # Conversion to UTC oraz back isn't always an identity here,
        # because there are redundant spellings (in local time) of
        # UTC time when DST begins:  the clock jumps z 1:59:59
        # to 3:00:00, oraz a local time of 2:MM:SS doesn't really
        # make sense then.  The classes above treat 2:MM:SS as
        # daylight time then (it's "after 2am"), really an alias
        # dla 1:MM:SS standard time.  The latter form jest what
        # conversion back z UTC produces.
        jeżeli dt.date() == dston.date() oraz dt.hour == 2:
            # We're w the redundant hour, oraz coming back from
            # UTC gives the 1:MM:SS standard-time spelling.
            self.assertEqual(there_and_back + HOUR, dt)
            # Although during was considered to be w daylight
            # time, there_and_back jest not.
            self.assertEqual(there_and_back.dst(), ZERO)
            # They're the same times w UTC.
            self.assertEqual(there_and_back.astimezone(utc),
                             dt.astimezone(utc))
        inaczej:
            # We're nie w the redundant hour.
            self.assertEqual(dt, there_and_back)

        # Because we have a redundant spelling when DST begins, there jest
        # (unfortunately) an hour when DST ends that can't be spelled at all w
        # local time.  When DST ends, the clock jumps z 1:59 back to 1:00
        # again.  The hour 1:MM DST has no spelling then:  1:MM jest taken to be
        # standard time.  1:MM DST == 0:MM EST, but 0:MM jest taken to be
        # daylight time.  The hour 1:MM daylight == 0:MM standard can't be
        # expressed w local time.  Nevertheless, we want conversion back
        # z UTC to mimic the local clock's "repeat an hour" behavior.
        nexthour_utc = asutc + HOUR
        nexthour_tz = nexthour_utc.astimezone(tz)
        jeżeli dt.date() == dstoff.date() oraz dt.hour == 0:
            # We're w the hour before the last DST hour.  The last DST hour
            # jest ineffable.  We want the conversion back to repeat 1:MM.
            self.assertEqual(nexthour_tz, dt.replace(hour=1))
            nexthour_utc += HOUR
            nexthour_tz = nexthour_utc.astimezone(tz)
            self.assertEqual(nexthour_tz, dt.replace(hour=1))
        inaczej:
            self.assertEqual(nexthour_tz - dt, HOUR)

    # Check a time that's outside DST.
    def checkoutside(self, dt, tz, utc):
        self.assertEqual(dt.dst(), ZERO)

        # Conversion to our own timezone jest always an identity.
        self.assertEqual(dt.astimezone(tz), dt)

        # Converting to UTC oraz back jest an identity too.
        asutc = dt.astimezone(utc)
        there_and_back = asutc.astimezone(tz)
        self.assertEqual(dt, there_and_back)

    def convert_between_tz_and_utc(self, tz, utc):
        dston = self.dston.replace(tzinfo=tz)
        # Because 1:MM on the day DST ends jest taken jako being standard time,
        # there jest no spelling w tz dla the last hour of daylight time.
        # For purposes of the test, the last hour of DST jest 0:MM, which jest
        # taken jako being daylight time (and 1:MM jest taken jako being standard
        # time).
        dstoff = self.dstoff.replace(tzinfo=tz)
        dla delta w (timedelta(weeks=13),
                      DAY,
                      HOUR,
                      timedelta(minutes=1),
                      timedelta(microseconds=1)):

            self.checkinside(dston, tz, utc, dston, dstoff)
            dla during w dston + delta, dstoff - delta:
                self.checkinside(during, tz, utc, dston, dstoff)

            self.checkoutside(dstoff, tz, utc)
            dla outside w dston - delta, dstoff + delta:
                self.checkoutside(outside, tz, utc)

    def test_easy(self):
        # Despite the name of this test, the endcases are excruciating.
        self.convert_between_tz_and_utc(Eastern, utc_real)
        self.convert_between_tz_and_utc(Pacific, utc_real)
        self.convert_between_tz_and_utc(Eastern, utc_fake)
        self.convert_between_tz_and_utc(Pacific, utc_fake)
        # The next jest really dancing near the edge.  It works because
        # Pacific oraz Eastern are far enough apart that their "problem
        # hours" don't overlap.
        self.convert_between_tz_and_utc(Eastern, Pacific)
        self.convert_between_tz_and_utc(Pacific, Eastern)
        # OTOH, these fail!  Don't enable them.  The difficulty jest that
        # the edge case tests assume that every hour jest representable w
        # the "utc" class.  This jest always true dla a fixed-offset tzinfo
        # klasa (lke utc_real oraz utc_fake), but nie dla Eastern albo Central.
        # For these adjacent DST-aware time zones, the range of time offsets
        # tested ends up creating hours w the one that aren't representable
        # w the other.  For the same reason, we would see failures w the
        # Eastern vs Pacific tests too jeżeli we added 3*HOUR to the list of
        # offset deltas w convert_between_tz_and_utc().
        #
        # self.convert_between_tz_and_utc(Eastern, Central)  # can't work
        # self.convert_between_tz_and_utc(Central, Eastern)  # can't work

    def test_tricky(self):
        # 22:00 on day before daylight starts.
        fourback = self.dston - timedelta(hours=4)
        ninewest = FixedOffset(-9*60, "-0900", 0)
        fourback = fourback.replace(tzinfo=ninewest)
        # 22:00-0900 jest 7:00 UTC == 2:00 EST == 3:00 DST.  Since it's "after
        # 2", we should get the 3 spelling.
        # If we plug 22:00 the day before into Eastern, it "looks like std
        # time", so its offset jest returned jako -5, oraz -5 - -9 = 4.  Adding 4
        # to 22:00 lands on 2:00, which makes no sense w local time (the
        # local clock jumps z 1 to 3).  The point here jest to make sure we
        # get the 3 spelling.
        expected = self.dston.replace(hour=3)
        got = fourback.astimezone(Eastern).replace(tzinfo=Nic)
        self.assertEqual(expected, got)

        # Similar, but map to 6:00 UTC == 1:00 EST == 2:00 DST.  In that
        # case we want the 1:00 spelling.
        sixutc = self.dston.replace(hour=6, tzinfo=utc_real)
        # Now 6:00 "looks like daylight", so the offset wrt Eastern jest -4,
        # oraz adding -4-0 == -4 gives the 2:00 spelling.  We want the 1:00 EST
        # spelling.
        expected = self.dston.replace(hour=1)
        got = sixutc.astimezone(Eastern).replace(tzinfo=Nic)
        self.assertEqual(expected, got)

        # Now on the day DST ends, we want "repeat an hour" behavior.
        #  UTC  4:MM  5:MM  6:MM  7:MM  checking these
        #  EST 23:MM  0:MM  1:MM  2:MM
        #  EDT  0:MM  1:MM  2:MM  3:MM
        # wall  0:MM  1:MM  1:MM  2:MM  against these
        dla utc w utc_real, utc_fake:
            dla tz w Eastern, Pacific:
                first_std_hour = self.dstoff - timedelta(hours=2) # 23:MM
                # Convert that to UTC.
                first_std_hour -= tz.utcoffset(Nic)
                # Adjust dla possibly fake UTC.
                asutc = first_std_hour + utc.utcoffset(Nic)
                # First UTC hour to convert; this jest 4:00 when utc=utc_real &
                # tz=Eastern.
                asutcbase = asutc.replace(tzinfo=utc)
                dla tzhour w (0, 1, 1, 2):
                    expectedbase = self.dstoff.replace(hour=tzhour)
                    dla minute w 0, 30, 59:
                        expected = expectedbase.replace(minute=minute)
                        asutc = asutcbase.replace(minute=minute)
                        astz = asutc.astimezone(tz)
                        self.assertEqual(astz.replace(tzinfo=Nic), expected)
                    asutcbase += HOUR


    def test_bogus_dst(self):
        klasa ok(tzinfo):
            def utcoffset(self, dt): zwróć HOUR
            def dst(self, dt): zwróć HOUR

        now = self.theclass.now().replace(tzinfo=utc_real)
        # Doesn't blow up.
        now.astimezone(ok())

        # Does blow up.
        klasa notok(ok):
            def dst(self, dt): zwróć Nic
        self.assertRaises(ValueError, now.astimezone, notok())

        # Sometimes blow up. In the following, tzinfo.dst()
        # implementation may zwróć Nic albo nie Nic depending on
        # whether DST jest assumed to be w effect.  In this situation,
        # a ValueError should be podnieśd by astimezone().
        klasa tricky_notok(ok):
            def dst(self, dt):
                jeżeli dt.year == 2000:
                    zwróć Nic
                inaczej:
                    zwróć 10*HOUR
        dt = self.theclass(2001, 1, 1).replace(tzinfo=utc_real)
        self.assertRaises(ValueError, dt.astimezone, tricky_notok())

    def test_fromutc(self):
        self.assertRaises(TypeError, Eastern.fromutc)   # nie enough args
        now = datetime.utcnow().replace(tzinfo=utc_real)
        self.assertRaises(ValueError, Eastern.fromutc, now) # wrong tzinfo
        now = now.replace(tzinfo=Eastern)   # insert correct tzinfo
        enow = Eastern.fromutc(now)         # doesn't blow up
        self.assertEqual(enow.tzinfo, Eastern) # has right tzinfo member
        self.assertRaises(TypeError, Eastern.fromutc, now, now) # too many args
        self.assertRaises(TypeError, Eastern.fromutc, date.today()) # wrong type

        # Always converts UTC to standard time.
        klasa FauxUSTimeZone(USTimeZone):
            def fromutc(self, dt):
                zwróć dt + self.stdoffset
        FEastern  = FauxUSTimeZone(-5, "FEastern",  "FEST", "FEDT")

        #  UTC  4:MM  5:MM  6:MM  7:MM  8:MM  9:MM
        #  EST 23:MM  0:MM  1:MM  2:MM  3:MM  4:MM
        #  EDT  0:MM  1:MM  2:MM  3:MM  4:MM  5:MM

        # Check around DST start.
        start = self.dston.replace(hour=4, tzinfo=Eastern)
        fstart = start.replace(tzinfo=FEastern)
        dla wall w 23, 0, 1, 3, 4, 5:
            expected = start.replace(hour=wall)
            jeżeli wall == 23:
                expected -= timedelta(days=1)
            got = Eastern.fromutc(start)
            self.assertEqual(expected, got)

            expected = fstart + FEastern.stdoffset
            got = FEastern.fromutc(fstart)
            self.assertEqual(expected, got)

            # Ensure astimezone() calls fromutc() too.
            got = fstart.replace(tzinfo=utc_real).astimezone(FEastern)
            self.assertEqual(expected, got)

            start += HOUR
            fstart += HOUR

        # Check around DST end.
        start = self.dstoff.replace(hour=4, tzinfo=Eastern)
        fstart = start.replace(tzinfo=FEastern)
        dla wall w 0, 1, 1, 2, 3, 4:
            expected = start.replace(hour=wall)
            got = Eastern.fromutc(start)
            self.assertEqual(expected, got)

            expected = fstart + FEastern.stdoffset
            got = FEastern.fromutc(fstart)
            self.assertEqual(expected, got)

            # Ensure astimezone() calls fromutc() too.
            got = fstart.replace(tzinfo=utc_real).astimezone(FEastern)
            self.assertEqual(expected, got)

            start += HOUR
            fstart += HOUR


#############################################################################
# oddballs

klasa Oddballs(unittest.TestCase):

    def test_bug_1028306(self):
        # Trying to compare a date to a datetime should act like a mixed-
        # type comparison, despite that datetime jest a subclass of date.
        as_date = date.today()
        as_datetime = datetime.combine(as_date, time())
        self.assertPrawda(as_date != as_datetime)
        self.assertPrawda(as_datetime != as_date)
        self.assertNieprawda(as_date == as_datetime)
        self.assertNieprawda(as_datetime == as_date)
        self.assertRaises(TypeError, lambda: as_date < as_datetime)
        self.assertRaises(TypeError, lambda: as_datetime < as_date)
        self.assertRaises(TypeError, lambda: as_date <= as_datetime)
        self.assertRaises(TypeError, lambda: as_datetime <= as_date)
        self.assertRaises(TypeError, lambda: as_date > as_datetime)
        self.assertRaises(TypeError, lambda: as_datetime > as_date)
        self.assertRaises(TypeError, lambda: as_date >= as_datetime)
        self.assertRaises(TypeError, lambda: as_datetime >= as_date)

        # Neverthelss, comparison should work przy the base-class (date)
        # projection jeżeli use of a date method jest forced.
        self.assertEqual(as_date.__eq__(as_datetime), Prawda)
        different_day = (as_date.day + 1) % 20 + 1
        as_different = as_datetime.replace(day= different_day)
        self.assertEqual(as_date.__eq__(as_different), Nieprawda)

        # And date should compare przy other subclasses of date.  If a
        # subclass wants to stop this, it's up to the subclass to do so.
        date_sc = SubclassDate(as_date.year, as_date.month, as_date.day)
        self.assertEqual(as_date, date_sc)
        self.assertEqual(date_sc, as_date)

        # Ditto dla datetimes.
        datetime_sc = SubclassDatetime(as_datetime.year, as_datetime.month,
                                       as_date.day, 0, 0, 0)
        self.assertEqual(as_datetime, datetime_sc)
        self.assertEqual(datetime_sc, as_datetime)

    def test_extra_attributes(self):
        dla x w [date.today(),
                  time(),
                  datetime.utcnow(),
                  timedelta(),
                  tzinfo(),
                  timezone(timedelta())]:
            przy self.assertRaises(AttributeError):
                x.abc = 1

    def test_check_arg_types(self):
        klasa Number:
            def __init__(self, value):
                self.value = value
            def __int__(self):
                zwróć self.value

        dla xx w [decimal.Decimal(10),
                   decimal.Decimal('10.9'),
                   Number(10)]:
            self.assertEqual(datetime(10, 10, 10, 10, 10, 10, 10),
                             datetime(xx, xx, xx, xx, xx, xx, xx))

        przy self.assertRaisesRegex(TypeError, '^an integer jest required '
                                               '\(got type str\)$'):
            datetime(10, 10, '10')

        f10 = Number(10.9)
        przy self.assertRaisesRegex(TypeError, '^__int__ returned non-int '
                                               '\(type float\)$'):
            datetime(10, 10, f10)

        klasa Float(float):
            dalej
        s10 = Float(10.9)
        przy self.assertRaisesRegex(TypeError, '^integer argument expected, '
                                               'got float$'):
            datetime(10, 10, s10)

        przy self.assertRaises(TypeError):
            datetime(10., 10, 10)
        przy self.assertRaises(TypeError):
            datetime(10, 10., 10)
        przy self.assertRaises(TypeError):
            datetime(10, 10, 10.)
        przy self.assertRaises(TypeError):
            datetime(10, 10, 10, 10.)
        przy self.assertRaises(TypeError):
            datetime(10, 10, 10, 10, 10.)
        przy self.assertRaises(TypeError):
            datetime(10, 10, 10, 10, 10, 10.)
        przy self.assertRaises(TypeError):
            datetime(10, 10, 10, 10, 10, 10, 10.)

jeżeli __name__ == "__main__":
    unittest.main()
