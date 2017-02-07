#-*- coding: iso-8859-1 -*-
# pysqlite2/test/types.py: tests dla type conversion oraz detection
#
# Copyright (C) 2005 Gerhard H�ring <gh@ghaering.de>
#
# This file jest part of pysqlite.
#
# This software jest provided 'as-is', without any express albo implied
# warranty.  In no event will the authors be held liable dla any damages
# arising z the use of this software.
#
# Permission jest granted to anyone to use this software dla any purpose,
# including commercial applications, oraz to alter it oraz redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must nie be misrepresented; you must nie
#    claim that you wrote the original software. If you use this software
#    w a product, an acknowledgment w the product documentation would be
#    appreciated but jest nie required.
# 2. Altered source versions must be plainly marked jako such, oraz must nie be
#    misrepresented jako being the original software.
# 3. This notice may nie be removed albo altered z any source distribution.

zaimportuj datetime
zaimportuj unittest
zaimportuj sqlite3 jako sqlite
spróbuj:
    zaimportuj zlib
wyjąwszy ImportError:
    zlib = Nic


klasa SqliteTypeTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite.connect(":memory:")
        self.cur = self.con.cursor()
        self.cur.execute("create table test(i integer, s varchar, f number, b blob)")

    def tearDown(self):
        self.cur.close()
        self.con.close()

    def CheckString(self):
        self.cur.execute("insert into test(s) values (?)", ("�sterreich",))
        self.cur.execute("select s z test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], "�sterreich")

    def CheckSmallInt(self):
        self.cur.execute("insert into test(i) values (?)", (42,))
        self.cur.execute("select i z test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], 42)

    def CheckLargeInt(self):
        num = 2**40
        self.cur.execute("insert into test(i) values (?)", (num,))
        self.cur.execute("select i z test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], num)

    def CheckFloat(self):
        val = 3.14
        self.cur.execute("insert into test(f) values (?)", (val,))
        self.cur.execute("select f z test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], val)

    def CheckBlob(self):
        sample = b"Guglhupf"
        val = memoryview(sample)
        self.cur.execute("insert into test(b) values (?)", (val,))
        self.cur.execute("select b z test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], sample)

    def CheckUnicodeExecute(self):
        self.cur.execute("select '�sterreich'")
        row = self.cur.fetchone()
        self.assertEqual(row[0], "�sterreich")

klasa DeclTypesTests(unittest.TestCase):
    klasa Foo:
        def __init__(self, _val):
            jeżeli isinstance(_val, bytes):
                # sqlite3 always calls __init__ przy a bytes created z a
                # UTF-8 string when __conform__ was used to store the object.
                _val = _val.decode('utf-8')
            self.val = _val

        def __eq__(self, other):
            jeżeli nie isinstance(other, DeclTypesTests.Foo):
                zwróć NotImplemented
            zwróć self.val == other.val

        def __conform__(self, protocol):
            jeżeli protocol jest sqlite.PrepareProtocol:
                zwróć self.val
            inaczej:
                zwróć Nic

        def __str__(self):
            zwróć "<%s>" % self.val

    def setUp(self):
        self.con = sqlite.connect(":memory:", detect_types=sqlite.PARSE_DECLTYPES)
        self.cur = self.con.cursor()
        self.cur.execute("create table test(i int, s str, f float, b bool, u unicode, foo foo, bin blob, n1 number, n2 number(5))")

        # override float, make them always zwróć the same number
        sqlite.converters["FLOAT"] = lambda x: 47.2

        # oraz implement two custom ones
        sqlite.converters["BOOL"] = lambda x: bool(int(x))
        sqlite.converters["FOO"] = DeclTypesTests.Foo
        sqlite.converters["WRONG"] = lambda x: "WRONG"
        sqlite.converters["NUMBER"] = float

    def tearDown(self):
        usuń sqlite.converters["FLOAT"]
        usuń sqlite.converters["BOOL"]
        usuń sqlite.converters["FOO"]
        usuń sqlite.converters["NUMBER"]
        self.cur.close()
        self.con.close()

    def CheckString(self):
        # default
        self.cur.execute("insert into test(s) values (?)", ("foo",))
        self.cur.execute('select s jako "s [WRONG]" z test')
        row = self.cur.fetchone()
        self.assertEqual(row[0], "foo")

    def CheckSmallInt(self):
        # default
        self.cur.execute("insert into test(i) values (?)", (42,))
        self.cur.execute("select i z test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], 42)

    def CheckLargeInt(self):
        # default
        num = 2**40
        self.cur.execute("insert into test(i) values (?)", (num,))
        self.cur.execute("select i z test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], num)

    def CheckFloat(self):
        # custom
        val = 3.14
        self.cur.execute("insert into test(f) values (?)", (val,))
        self.cur.execute("select f z test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], 47.2)

    def CheckBool(self):
        # custom
        self.cur.execute("insert into test(b) values (?)", (Nieprawda,))
        self.cur.execute("select b z test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], Nieprawda)

        self.cur.execute("delete z test")
        self.cur.execute("insert into test(b) values (?)", (Prawda,))
        self.cur.execute("select b z test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], Prawda)

    def CheckUnicode(self):
        # default
        val = "\xd6sterreich"
        self.cur.execute("insert into test(u) values (?)", (val,))
        self.cur.execute("select u z test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], val)

    def CheckFoo(self):
        val = DeclTypesTests.Foo("bla")
        self.cur.execute("insert into test(foo) values (?)", (val,))
        self.cur.execute("select foo z test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], val)

    def CheckUnsupportedSeq(self):
        klasa Bar: dalej
        val = Bar()
        spróbuj:
            self.cur.execute("insert into test(f) values (?)", (val,))
            self.fail("should have podnieśd an InterfaceError")
        wyjąwszy sqlite.InterfaceError:
            dalej
        wyjąwszy:
            self.fail("should have podnieśd an InterfaceError")

    def CheckUnsupportedDict(self):
        klasa Bar: dalej
        val = Bar()
        spróbuj:
            self.cur.execute("insert into test(f) values (:val)", {"val": val})
            self.fail("should have podnieśd an InterfaceError")
        wyjąwszy sqlite.InterfaceError:
            dalej
        wyjąwszy:
            self.fail("should have podnieśd an InterfaceError")

    def CheckBlob(self):
        # default
        sample = b"Guglhupf"
        val = memoryview(sample)
        self.cur.execute("insert into test(bin) values (?)", (val,))
        self.cur.execute("select bin z test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], sample)

    def CheckNumber1(self):
        self.cur.execute("insert into test(n1) values (5)")
        value = self.cur.execute("select n1 z test").fetchone()[0]
        # jeżeli the converter jest nie used, it's an int instead of a float
        self.assertEqual(type(value), float)

    def CheckNumber2(self):
        """Checks whether converter names are cut off at '(' characters"""
        self.cur.execute("insert into test(n2) values (5)")
        value = self.cur.execute("select n2 z test").fetchone()[0]
        # jeżeli the converter jest nie used, it's an int instead of a float
        self.assertEqual(type(value), float)

klasa ColNamesTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite.connect(":memory:", detect_types=sqlite.PARSE_COLNAMES)
        self.cur = self.con.cursor()
        self.cur.execute("create table test(x foo)")

        sqlite.converters["FOO"] = lambda x: "[%s]" % x.decode("ascii")
        sqlite.converters["BAR"] = lambda x: "<%s>" % x.decode("ascii")
        sqlite.converters["EXC"] = lambda x: 5/0
        sqlite.converters["B1B1"] = lambda x: "MARKER"

    def tearDown(self):
        usuń sqlite.converters["FOO"]
        usuń sqlite.converters["BAR"]
        usuń sqlite.converters["EXC"]
        usuń sqlite.converters["B1B1"]
        self.cur.close()
        self.con.close()

    def CheckDeclTypeNotUsed(self):
        """
        Assures that the declared type jest nie used when PARSE_DECLTYPES
        jest nie set.
        """
        self.cur.execute("insert into test(x) values (?)", ("xxx",))
        self.cur.execute("select x z test")
        val = self.cur.fetchone()[0]
        self.assertEqual(val, "xxx")

    def CheckNic(self):
        self.cur.execute("insert into test(x) values (?)", (Nic,))
        self.cur.execute("select x z test")
        val = self.cur.fetchone()[0]
        self.assertEqual(val, Nic)

    def CheckColName(self):
        self.cur.execute("insert into test(x) values (?)", ("xxx",))
        self.cur.execute('select x jako "x [bar]" z test')
        val = self.cur.fetchone()[0]
        self.assertEqual(val, "<xxx>")

        # Check jeżeli the stripping of colnames works. Everything after the first
        # whitespace should be stripped.
        self.assertEqual(self.cur.description[0][0], "x")

    def CheckCaseInConverterName(self):
        self.cur.execute("select 'other' jako \"x [b1b1]\"")
        val = self.cur.fetchone()[0]
        self.assertEqual(val, "MARKER")

    def CheckCursorDescriptionNoRow(self):
        """
        cursor.description should at least provide the column name(s), even if
        no row returned.
        """
        self.cur.execute("select * z test where 0 = 1")
        self.assertEqual(self.cur.description[0][0], "x")

klasa ObjectAdaptationTests(unittest.TestCase):
    def cast(obj):
        zwróć float(obj)
    cast = staticmethod(cast)

    def setUp(self):
        self.con = sqlite.connect(":memory:")
        spróbuj:
            usuń sqlite.adapters[int]
        wyjąwszy:
            dalej
        sqlite.register_adapter(int, ObjectAdaptationTests.cast)
        self.cur = self.con.cursor()

    def tearDown(self):
        usuń sqlite.adapters[(int, sqlite.PrepareProtocol)]
        self.cur.close()
        self.con.close()

    def CheckCasterIsUsed(self):
        self.cur.execute("select ?", (4,))
        val = self.cur.fetchone()[0]
        self.assertEqual(type(val), float)

@unittest.skipUnless(zlib, "requires zlib")
klasa BinaryConverterTests(unittest.TestCase):
    def convert(s):
        zwróć zlib.decompress(s)
    convert = staticmethod(convert)

    def setUp(self):
        self.con = sqlite.connect(":memory:", detect_types=sqlite.PARSE_COLNAMES)
        sqlite.register_converter("bin", BinaryConverterTests.convert)

    def tearDown(self):
        self.con.close()

    def CheckBinaryInputForConverter(self):
        testdata = b"abcdefg" * 10
        result = self.con.execute('select ? jako "x [bin]"', (memoryview(zlib.compress(testdata)),)).fetchone()[0]
        self.assertEqual(testdata, result)

klasa DateTimeTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite.connect(":memory:", detect_types=sqlite.PARSE_DECLTYPES)
        self.cur = self.con.cursor()
        self.cur.execute("create table test(d date, ts timestamp)")

    def tearDown(self):
        self.cur.close()
        self.con.close()

    def CheckSqliteDate(self):
        d = sqlite.Date(2004, 2, 14)
        self.cur.execute("insert into test(d) values (?)", (d,))
        self.cur.execute("select d z test")
        d2 = self.cur.fetchone()[0]
        self.assertEqual(d, d2)

    def CheckSqliteTimestamp(self):
        ts = sqlite.Timestamp(2004, 2, 14, 7, 15, 0)
        self.cur.execute("insert into test(ts) values (?)", (ts,))
        self.cur.execute("select ts z test")
        ts2 = self.cur.fetchone()[0]
        self.assertEqual(ts, ts2)

    def CheckSqlTimestamp(self):
        # The date functions are only available w SQLite version 3.1 albo later
        jeżeli sqlite.sqlite_version_info < (3, 1):
            zwróć

        # SQLite's current_timestamp uses UTC time, dopóki datetime.datetime.now() uses local time.
        now = datetime.datetime.now()
        self.cur.execute("insert into test(ts) values (current_timestamp)")
        self.cur.execute("select ts z test")
        ts = self.cur.fetchone()[0]
        self.assertEqual(type(ts), datetime.datetime)
        self.assertEqual(ts.year, now.year)

    def CheckDateTimeSubSeconds(self):
        ts = sqlite.Timestamp(2004, 2, 14, 7, 15, 0, 500000)
        self.cur.execute("insert into test(ts) values (?)", (ts,))
        self.cur.execute("select ts z test")
        ts2 = self.cur.fetchone()[0]
        self.assertEqual(ts, ts2)

    def CheckDateTimeSubSecondsFloatingPoint(self):
        ts = sqlite.Timestamp(2004, 2, 14, 7, 15, 0, 510241)
        self.cur.execute("insert into test(ts) values (?)", (ts,))
        self.cur.execute("select ts z test")
        ts2 = self.cur.fetchone()[0]
        self.assertEqual(ts, ts2)

def suite():
    sqlite_type_suite = unittest.makeSuite(SqliteTypeTests, "Check")
    decltypes_type_suite = unittest.makeSuite(DeclTypesTests, "Check")
    colnames_type_suite = unittest.makeSuite(ColNamesTests, "Check")
    adaptation_suite = unittest.makeSuite(ObjectAdaptationTests, "Check")
    bin_suite = unittest.makeSuite(BinaryConverterTests, "Check")
    date_suite = unittest.makeSuite(DateTimeTests, "Check")
    zwróć unittest.TestSuite((sqlite_type_suite, decltypes_type_suite, colnames_type_suite, adaptation_suite, bin_suite, date_suite))

def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())

jeżeli __name__ == "__main__":
    test()
