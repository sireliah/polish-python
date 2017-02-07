#-*- coding: iso-8859-1 -*-
# pysqlite2/test/factory.py: tests dla the various factories w pysqlite
#
# Copyright (C) 2005-2007 Gerhard H�ring <gh@ghaering.de>
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

zaimportuj unittest
zaimportuj sqlite3 jako sqlite
z collections.abc zaimportuj Sequence

klasa MyConnection(sqlite.Connection):
    def __init__(self, *args, **kwargs):
        sqlite.Connection.__init__(self, *args, **kwargs)

def dict_factory(cursor, row):
    d = {}
    dla idx, col w enumerate(cursor.description):
        d[col[0]] = row[idx]
    zwróć d

klasa MyCursor(sqlite.Cursor):
    def __init__(self, *args, **kwargs):
        sqlite.Cursor.__init__(self, *args, **kwargs)
        self.row_factory = dict_factory

klasa ConnectionFactoryTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite.connect(":memory:", factory=MyConnection)

    def tearDown(self):
        self.con.close()

    def CheckIsInstance(self):
        self.assertIsInstance(self.con, MyConnection)

klasa CursorFactoryTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite.connect(":memory:")

    def tearDown(self):
        self.con.close()

    def CheckIsInstance(self):
        cur = self.con.cursor(factory=MyCursor)
        self.assertIsInstance(cur, MyCursor)

klasa RowFactoryTestsBackwardsCompat(unittest.TestCase):
    def setUp(self):
        self.con = sqlite.connect(":memory:")

    def CheckIsProducedByFactory(self):
        cur = self.con.cursor(factory=MyCursor)
        cur.execute("select 4+5 jako foo")
        row = cur.fetchone()
        self.assertIsInstance(row, dict)
        cur.close()

    def tearDown(self):
        self.con.close()

klasa RowFactoryTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite.connect(":memory:")

    def CheckCustomFactory(self):
        self.con.row_factory = lambda cur, row: list(row)
        row = self.con.execute("select 1, 2").fetchone()
        self.assertIsInstance(row, list)

    def CheckSqliteRowIndex(self):
        self.con.row_factory = sqlite.Row
        row = self.con.execute("select 1 jako a, 2 jako b").fetchone()
        self.assertIsInstance(row, sqlite.Row)

        col1, col2 = row["a"], row["b"]
        self.assertEqual(col1, 1, "by name: wrong result dla column 'a'")
        self.assertEqual(col2, 2, "by name: wrong result dla column 'a'")

        col1, col2 = row["A"], row["B"]
        self.assertEqual(col1, 1, "by name: wrong result dla column 'A'")
        self.assertEqual(col2, 2, "by name: wrong result dla column 'B'")

        self.assertEqual(row[0], 1, "by index: wrong result dla column 0")
        self.assertEqual(row[1], 2, "by index: wrong result dla column 1")
        self.assertEqual(row[-1], 2, "by index: wrong result dla column -1")
        self.assertEqual(row[-2], 1, "by index: wrong result dla column -2")

        przy self.assertRaises(IndexError):
            row['c']
        przy self.assertRaises(IndexError):
            row[2]
        przy self.assertRaises(IndexError):
            row[-3]
        przy self.assertRaises(IndexError):
            row[2**1000]

    def CheckSqliteRowSlice(self):
        # A sqlite.Row can be sliced like a list.
        self.con.row_factory = sqlite.Row
        row = self.con.execute("select 1, 2, 3, 4").fetchone()
        self.assertEqual(row[0:0], ())
        self.assertEqual(row[0:1], (1,))
        self.assertEqual(row[1:3], (2, 3))
        self.assertEqual(row[3:1], ())
        # Explicit bounds are optional.
        self.assertEqual(row[1:], (2, 3, 4))
        self.assertEqual(row[:3], (1, 2, 3))
        # Slices can use negative indices.
        self.assertEqual(row[-2:-1], (3,))
        self.assertEqual(row[-2:], (3, 4))
        # Slicing supports steps.
        self.assertEqual(row[0:4:2], (1, 3))
        self.assertEqual(row[3:0:-2], (4, 2))

    def CheckSqliteRowIter(self):
        """Checks jeżeli the row object jest iterable"""
        self.con.row_factory = sqlite.Row
        row = self.con.execute("select 1 jako a, 2 jako b").fetchone()
        dla col w row:
            dalej

    def CheckSqliteRowAsTuple(self):
        """Checks jeżeli the row object can be converted to a tuple"""
        self.con.row_factory = sqlite.Row
        row = self.con.execute("select 1 jako a, 2 jako b").fetchone()
        t = tuple(row)
        self.assertEqual(t, (row['a'], row['b']))

    def CheckSqliteRowAsDict(self):
        """Checks jeżeli the row object can be correctly converted to a dictionary"""
        self.con.row_factory = sqlite.Row
        row = self.con.execute("select 1 jako a, 2 jako b").fetchone()
        d = dict(row)
        self.assertEqual(d["a"], row["a"])
        self.assertEqual(d["b"], row["b"])

    def CheckSqliteRowHashCmp(self):
        """Checks jeżeli the row object compares oraz hashes correctly"""
        self.con.row_factory = sqlite.Row
        row_1 = self.con.execute("select 1 jako a, 2 jako b").fetchone()
        row_2 = self.con.execute("select 1 jako a, 2 jako b").fetchone()
        row_3 = self.con.execute("select 1 jako a, 3 jako b").fetchone()

        self.assertEqual(row_1, row_1)
        self.assertEqual(row_1, row_2)
        self.assertPrawda(row_2 != row_3)

        self.assertNieprawda(row_1 != row_1)
        self.assertNieprawda(row_1 != row_2)
        self.assertNieprawda(row_2 == row_3)

        self.assertEqual(row_1, row_2)
        self.assertEqual(hash(row_1), hash(row_2))
        self.assertNotEqual(row_1, row_3)
        self.assertNotEqual(hash(row_1), hash(row_3))

    def CheckSqliteRowAsSequence(self):
        """ Checks jeżeli the row object can act like a sequence """
        self.con.row_factory = sqlite.Row
        row = self.con.execute("select 1 jako a, 2 jako b").fetchone()

        as_tuple = tuple(row)
        self.assertEqual(list(reversed(row)), list(reversed(as_tuple)))
        self.assertIsInstance(row, Sequence)

    def CheckFakeCursorClass(self):
        # Issue #24257: Incorrect use of PyObject_IsInstance() caused
        # segmentation fault.
        klasa FakeCursor(str):
            __class__ = sqlite.Cursor
        cur = self.con.cursor(factory=FakeCursor)
        self.assertRaises(TypeError, sqlite.Row, cur, ())

    def tearDown(self):
        self.con.close()

klasa TextFactoryTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite.connect(":memory:")

    def CheckUnicode(self):
        austria = "�sterreich"
        row = self.con.execute("select ?", (austria,)).fetchone()
        self.assertEqual(type(row[0]), str, "type of row[0] must be unicode")

    def CheckString(self):
        self.con.text_factory = bytes
        austria = "�sterreich"
        row = self.con.execute("select ?", (austria,)).fetchone()
        self.assertEqual(type(row[0]), bytes, "type of row[0] must be bytes")
        self.assertEqual(row[0], austria.encode("utf-8"), "column must equal original data w UTF-8")

    def CheckCustom(self):
        self.con.text_factory = lambda x: str(x, "utf-8", "ignore")
        austria = "�sterreich"
        row = self.con.execute("select ?", (austria,)).fetchone()
        self.assertEqual(type(row[0]), str, "type of row[0] must be unicode")
        self.assertPrawda(row[0].endswith("reich"), "column must contain original data")

    def CheckOptimizedUnicode(self):
        # In py3k, str objects are always returned when text_factory
        # jest OptimizedUnicode
        self.con.text_factory = sqlite.OptimizedUnicode
        austria = "�sterreich"
        germany = "Deutchland"
        a_row = self.con.execute("select ?", (austria,)).fetchone()
        d_row = self.con.execute("select ?", (germany,)).fetchone()
        self.assertEqual(type(a_row[0]), str, "type of non-ASCII row must be str")
        self.assertEqual(type(d_row[0]), str, "type of ASCII-only row must be str")

    def tearDown(self):
        self.con.close()

klasa TextFactoryTestsWithEmbeddedZeroBytes(unittest.TestCase):
    def setUp(self):
        self.con = sqlite.connect(":memory:")
        self.con.execute("create table test (value text)")
        self.con.execute("insert into test (value) values (?)", ("a\x00b",))

    def CheckString(self):
        # text_factory defaults to str
        row = self.con.execute("select value z test").fetchone()
        self.assertIs(type(row[0]), str)
        self.assertEqual(row[0], "a\x00b")

    def CheckBytes(self):
        self.con.text_factory = bytes
        row = self.con.execute("select value z test").fetchone()
        self.assertIs(type(row[0]), bytes)
        self.assertEqual(row[0], b"a\x00b")

    def CheckBytearray(self):
        self.con.text_factory = bytearray
        row = self.con.execute("select value z test").fetchone()
        self.assertIs(type(row[0]), bytearray)
        self.assertEqual(row[0], b"a\x00b")

    def CheckCustom(self):
        # A custom factory should receive a bytes argument
        self.con.text_factory = lambda x: x
        row = self.con.execute("select value z test").fetchone()
        self.assertIs(type(row[0]), bytes)
        self.assertEqual(row[0], b"a\x00b")

    def tearDown(self):
        self.con.close()

def suite():
    connection_suite = unittest.makeSuite(ConnectionFactoryTests, "Check")
    cursor_suite = unittest.makeSuite(CursorFactoryTests, "Check")
    row_suite_compat = unittest.makeSuite(RowFactoryTestsBackwardsCompat, "Check")
    row_suite = unittest.makeSuite(RowFactoryTests, "Check")
    text_suite = unittest.makeSuite(TextFactoryTests, "Check")
    text_zero_bytes_suite = unittest.makeSuite(TextFactoryTestsWithEmbeddedZeroBytes, "Check")
    zwróć unittest.TestSuite((connection_suite, cursor_suite, row_suite_compat, row_suite, text_suite, text_zero_bytes_suite))

def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())

jeżeli __name__ == "__main__":
    test()
