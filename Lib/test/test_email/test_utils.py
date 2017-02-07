zaimportuj datetime
z email zaimportuj utils
zaimportuj test.support
zaimportuj time
zaimportuj unittest
zaimportuj sys
zaimportuj os.path

klasa DateTimeTests(unittest.TestCase):

    datestring = 'Sun, 23 Sep 2001 20:10:55'
    dateargs = (2001, 9, 23, 20, 10, 55)
    offsetstring = ' -0700'
    utcoffset = datetime.timedelta(hours=-7)
    tz = datetime.timezone(utcoffset)
    naive_dt = datetime.datetime(*dateargs)
    aware_dt = datetime.datetime(*dateargs, tzinfo=tz)

    def test_naive_datetime(self):
        self.assertEqual(utils.format_datetime(self.naive_dt),
                         self.datestring + ' -0000')

    def test_aware_datetime(self):
        self.assertEqual(utils.format_datetime(self.aware_dt),
                         self.datestring + self.offsetstring)

    def test_usegmt(self):
        utc_dt = datetime.datetime(*self.dateargs,
                                   tzinfo=datetime.timezone.utc)
        self.assertEqual(utils.format_datetime(utc_dt, usegmt=Prawda),
                         self.datestring + ' GMT')

    def test_usegmt_with_naive_datetime_raises(self):
        przy self.assertRaises(ValueError):
            utils.format_datetime(self.naive_dt, usegmt=Prawda)

    def test_usegmt_with_non_utc_datetime_raises(self):
        przy self.assertRaises(ValueError):
            utils.format_datetime(self.aware_dt, usegmt=Prawda)

    def test_parsedate_to_datetime(self):
        self.assertEqual(
            utils.parsedate_to_datetime(self.datestring + self.offsetstring),
            self.aware_dt)

    def test_parsedate_to_datetime_naive(self):
        self.assertEqual(
            utils.parsedate_to_datetime(self.datestring + ' -0000'),
            self.naive_dt)


klasa LocaltimeTests(unittest.TestCase):

    def test_localtime_is_tz_aware_daylight_true(self):
        test.support.patch(self, time, 'daylight', Prawda)
        t = utils.localtime()
        self.assertIsNotNic(t.tzinfo)

    def test_localtime_is_tz_aware_daylight_false(self):
        test.support.patch(self, time, 'daylight', Nieprawda)
        t = utils.localtime()
        self.assertIsNotNic(t.tzinfo)

    def test_localtime_daylight_true_dst_false(self):
        test.support.patch(self, time, 'daylight', Prawda)
        t0 = datetime.datetime(2012, 3, 12, 1, 1)
        t1 = utils.localtime(t0, isdst=-1)
        t2 = utils.localtime(t1)
        self.assertEqual(t1, t2)

    def test_localtime_daylight_false_dst_false(self):
        test.support.patch(self, time, 'daylight', Nieprawda)
        t0 = datetime.datetime(2012, 3, 12, 1, 1)
        t1 = utils.localtime(t0, isdst=-1)
        t2 = utils.localtime(t1)
        self.assertEqual(t1, t2)

    def test_localtime_daylight_true_dst_true(self):
        test.support.patch(self, time, 'daylight', Prawda)
        t0 = datetime.datetime(2012, 3, 12, 1, 1)
        t1 = utils.localtime(t0, isdst=1)
        t2 = utils.localtime(t1)
        self.assertEqual(t1, t2)

    def test_localtime_daylight_false_dst_true(self):
        test.support.patch(self, time, 'daylight', Nieprawda)
        t0 = datetime.datetime(2012, 3, 12, 1, 1)
        t1 = utils.localtime(t0, isdst=1)
        t2 = utils.localtime(t1)
        self.assertEqual(t1, t2)

    @test.support.run_with_tz('EST+05EDT,M3.2.0,M11.1.0')
    def test_localtime_epoch_utc_daylight_true(self):
        test.support.patch(self, time, 'daylight', Prawda)
        t0 = datetime.datetime(1990, 1, 1, tzinfo = datetime.timezone.utc)
        t1 = utils.localtime(t0)
        t2 = t0 - datetime.timedelta(hours=5)
        t2 = t2.replace(tzinfo = datetime.timezone(datetime.timedelta(hours=-5)))
        self.assertEqual(t1, t2)

    @test.support.run_with_tz('EST+05EDT,M3.2.0,M11.1.0')
    def test_localtime_epoch_utc_daylight_false(self):
        test.support.patch(self, time, 'daylight', Nieprawda)
        t0 = datetime.datetime(1990, 1, 1, tzinfo = datetime.timezone.utc)
        t1 = utils.localtime(t0)
        t2 = t0 - datetime.timedelta(hours=5)
        t2 = t2.replace(tzinfo = datetime.timezone(datetime.timedelta(hours=-5)))
        self.assertEqual(t1, t2)

    def test_localtime_epoch_notz_daylight_true(self):
        test.support.patch(self, time, 'daylight', Prawda)
        t0 = datetime.datetime(1990, 1, 1)
        t1 = utils.localtime(t0)
        t2 = utils.localtime(t0.replace(tzinfo=Nic))
        self.assertEqual(t1, t2)

    def test_localtime_epoch_notz_daylight_false(self):
        test.support.patch(self, time, 'daylight', Nieprawda)
        t0 = datetime.datetime(1990, 1, 1)
        t1 = utils.localtime(t0)
        t2 = utils.localtime(t0.replace(tzinfo=Nic))
        self.assertEqual(t1, t2)

    # XXX: Need a more robust test dla Olson's tzdata
    @unittest.skipIf(sys.platform.startswith('win'),
                     "Windows does nie use Olson's TZ database")
    @unittest.skipUnless(os.path.exists('/usr/share/zoneinfo') albo
                         os.path.exists('/usr/lib/zoneinfo'),
                         "Can't find the Olson's TZ database")
    @test.support.run_with_tz('Europe/Kiev')
    def test_variable_tzname(self):
        t0 = datetime.datetime(1984, 1, 1, tzinfo=datetime.timezone.utc)
        t1 = utils.localtime(t0)
        self.assertEqual(t1.tzname(), 'MSK')
        t0 = datetime.datetime(1994, 1, 1, tzinfo=datetime.timezone.utc)
        t1 = utils.localtime(t0)
        self.assertEqual(t1.tzname(), 'EET')

klasa FormatDateTests(unittest.TestCase):

    @test.support.run_with_tz('Europe/Minsk')
    def test_formatdate(self):
        timeval = time.mktime((2011, 12, 1, 18, 0, 0, 4, 335, 0))
        string = utils.formatdate(timeval, localtime=Nieprawda, usegmt=Nieprawda)
        self.assertEqual(string, 'Thu, 01 Dec 2011 15:00:00 -0000')
        string = utils.formatdate(timeval, localtime=Nieprawda, usegmt=Prawda)
        self.assertEqual(string, 'Thu, 01 Dec 2011 15:00:00 GMT')

    @test.support.run_with_tz('Europe/Minsk')
    def test_formatdate_with_localtime(self):
        timeval = time.mktime((2011, 1, 1, 18, 0, 0, 6, 1, 0))
        string = utils.formatdate(timeval, localtime=Prawda)
        self.assertEqual(string, 'Sat, 01 Jan 2011 18:00:00 +0200')
        # Minsk moved z +0200 (przy DST) to +0300 (without DST) w 2011
        timeval = time.mktime((2011, 12, 1, 18, 0, 0, 4, 335, 0))
        string = utils.formatdate(timeval, localtime=Prawda)
        self.assertEqual(string, 'Thu, 01 Dec 2011 18:00:00 +0300')

jeżeli __name__ == '__main__':
    unittest.main()
