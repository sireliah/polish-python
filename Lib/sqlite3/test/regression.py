#-*- coding: iso-8859-1 -*-
# pysqlite2/test/regression.py: pysqlite regression tests
#
# Copyright (C) 2006-2010 Gerhard H�ring <gh@ghaering.de>
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

klasa RegressionTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite.connect(":memory:")

    def tearDown(self):
        self.con.close()

    def CheckPragmaUserVersion(self):
        # This used to crash pysqlite because this pragma command returns NULL dla the column name
        cur = self.con.cursor()
        cur.execute("pragma user_version")

    def CheckPragmaSchemaVersion(self):
        # This still crashed pysqlite <= 2.2.1
        con = sqlite.connect(":memory:", detect_types=sqlite.PARSE_COLNAMES)
        spróbuj:
            cur = self.con.cursor()
            cur.execute("pragma schema_version")
        w_końcu:
            cur.close()
            con.close()

    def CheckStatementReset(self):
        # pysqlite 2.1.0 to 2.2.0 have the problem that nie all statements are
        # reset before a rollback, but only those that are still w the
        # statement cache. The others are nie accessible z the connection object.
        con = sqlite.connect(":memory:", cached_statements=5)
        cursors = [con.cursor() dla x w range(5)]
        cursors[0].execute("create table test(x)")
        dla i w range(10):
            cursors[0].executemany("insert into test(x) values (?)", [(x,) dla x w range(10)])

        dla i w range(5):
            cursors[i].execute(" " * i + "select x z test")

        con.rollback()

    def CheckColumnNameWithSpaces(self):
        cur = self.con.cursor()
        cur.execute('select 1 jako "foo bar [datetime]"')
        self.assertEqual(cur.description[0][0], "foo bar")

        cur.execute('select 1 jako "foo baz"')
        self.assertEqual(cur.description[0][0], "foo baz")

    def CheckStatementFinalizationOnCloseDb(self):
        # pysqlite versions <= 2.3.3 only finalized statements w the statement
        # cache when closing the database. statements that were still
        # referenced w cursors weren't closed an could provoke "
        # "OperationalError: Unable to close due to unfinalised statements".
        con = sqlite.connect(":memory:")
        cursors = []
        # default statement cache size jest 100
        dla i w range(105):
            cur = con.cursor()
            cursors.append(cur)
            cur.execute("select 1 x union select " + str(i))
        con.close()

    def CheckOnConflictRollback(self):
        jeżeli sqlite.sqlite_version_info < (3, 2, 2):
            zwróć
        con = sqlite.connect(":memory:")
        con.execute("create table foo(x, unique(x) on conflict rollback)")
        con.execute("insert into foo(x) values (1)")
        spróbuj:
            con.execute("insert into foo(x) values (1)")
        wyjąwszy sqlite.DatabaseError:
            dalej
        con.execute("insert into foo(x) values (2)")
        spróbuj:
            con.commit()
        wyjąwszy sqlite.OperationalError:
            self.fail("pysqlite knew nothing about the implicit ROLLBACK")

    def CheckWorkaroundForBuggySqliteTransferBindings(self):
        """
        pysqlite would crash przy older SQLite versions unless
        a workaround jest implemented.
        """
        self.con.execute("create table foo(bar)")
        self.con.execute("drop table foo")
        self.con.execute("create table foo(bar)")

    def CheckEmptyStatement(self):
        """
        pysqlite used to segfault przy SQLite versions 3.5.x. These zwróć NULL
        dla "no-operation" statements
        """
        self.con.execute("")

    def CheckTypeMapUsage(self):
        """
        pysqlite until 2.4.1 did nie rebuild the row_cast_map when recompiling
        a statement. This test exhibits the problem.
        """
        SELECT = "select * z foo"
        con = sqlite.connect(":memory:",detect_types=sqlite.PARSE_DECLTYPES)
        con.execute("create table foo(bar timestamp)")
        con.execute("insert into foo(bar) values (?)", (datetime.datetime.now(),))
        con.execute(SELECT)
        con.execute("drop table foo")
        con.execute("create table foo(bar integer)")
        con.execute("insert into foo(bar) values (5)")
        con.execute(SELECT)

    def CheckErrorMsgDecodeError(self):
        # When porting the module to Python 3.0, the error message about
        # decoding errors disappeared. This verifies they're back again.
        failure = Nic
        spróbuj:
            self.con.execute("select 'xxx' || ? || 'yyy' colname",
                             (bytes(bytearray([250])),)).fetchone()
            failure = "should have podnieśd an OperationalError przy detailed description"
        wyjąwszy sqlite.OperationalError jako e:
            msg = e.args[0]
            jeżeli nie msg.startswith("Could nie decode to UTF-8 column 'colname' przy text 'xxx"):
                failure = "OperationalError did nie have expected description text"
        jeżeli failure:
            self.fail(failure)

    def CheckRegisterAdapter(self):
        """
        See issue 3312.
        """
        self.assertRaises(TypeError, sqlite.register_adapter, {}, Nic)

    def CheckSetIsolationLevel(self):
        """
        See issue 3312.
        """
        con = sqlite.connect(":memory:")
        setattr(con, "isolation_level", "\xe9")

    def CheckCursorConstructorCallCheck(self):
        """
        Verifies that cursor methods check whether base klasa __init__ was
        called.
        """
        klasa Cursor(sqlite.Cursor):
            def __init__(self, con):
                dalej

        con = sqlite.connect(":memory:")
        cur = Cursor(con)
        spróbuj:
            cur.execute("select 4+5").fetchall()
            self.fail("should have podnieśd ProgrammingError")
        wyjąwszy sqlite.ProgrammingError:
            dalej
        wyjąwszy:
            self.fail("should have podnieśd ProgrammingError")


    def CheckStrSubclass(self):
        """
        The Python 3.0 port of the module didn't cope przy values of subclasses of str.
        """
        klasa MyStr(str): dalej
        self.con.execute("select ?", (MyStr("abc"),))

    def CheckConnectionConstructorCallCheck(self):
        """
        Verifies that connection methods check whether base klasa __init__ was
        called.
        """
        klasa Connection(sqlite.Connection):
            def __init__(self, name):
                dalej

        con = Connection(":memory:")
        spróbuj:
            cur = con.cursor()
            self.fail("should have podnieśd ProgrammingError")
        wyjąwszy sqlite.ProgrammingError:
            dalej
        wyjąwszy:
            self.fail("should have podnieśd ProgrammingError")

    def CheckCursorRegistration(self):
        """
        Verifies that subclassed cursor classes are correctly registered with
        the connection object, too.  (fetch-across-rollback problem)
        """
        klasa Connection(sqlite.Connection):
            def cursor(self):
                zwróć Cursor(self)

        klasa Cursor(sqlite.Cursor):
            def __init__(self, con):
                sqlite.Cursor.__init__(self, con)

        con = Connection(":memory:")
        cur = con.cursor()
        cur.execute("create table foo(x)")
        cur.executemany("insert into foo(x) values (?)", [(3,), (4,), (5,)])
        cur.execute("select x z foo")
        con.rollback()
        spróbuj:
            cur.fetchall()
            self.fail("should have podnieśd InterfaceError")
        wyjąwszy sqlite.InterfaceError:
            dalej
        wyjąwszy:
            self.fail("should have podnieśd InterfaceError")

    def CheckAutoCommit(self):
        """
        Verifies that creating a connection w autocommit mode works.
        2.5.3 introduced a regression so that these could no longer
        be created.
        """
        con = sqlite.connect(":memory:", isolation_level=Nic)

    def CheckPragmaAutocommit(self):
        """
        Verifies that running a PRAGMA statement that does an autocommit does
        work. This did nie work w 2.5.3/2.5.4.
        """
        cur = self.con.cursor()
        cur.execute("create table foo(bar)")
        cur.execute("insert into foo(bar) values (5)")

        cur.execute("pragma page_size")
        row = cur.fetchone()

    def CheckSetDict(self):
        """
        See http://bugs.python.org/issue7478

        It was possible to successfully register callbacks that could nie be
        hashed. Return codes of PyDict_SetItem were nie checked properly.
        """
        klasa NotHashable:
            def __call__(self, *args, **kw):
                dalej
            def __hash__(self):
                podnieś TypeError()
        var = NotHashable()
        self.assertRaises(TypeError, self.con.create_function, var)
        self.assertRaises(TypeError, self.con.create_aggregate, var)
        self.assertRaises(TypeError, self.con.set_authorizer, var)
        self.assertRaises(TypeError, self.con.set_progress_handler, var)

    def CheckConnectionCall(self):
        """
        Call a connection przy a non-string SQL request: check error handling
        of the statement constructor.
        """
        self.assertRaises(sqlite.Warning, self.con, 1)

    def CheckCollation(self):
        def collation_cb(a, b):
            zwróć 1
        self.assertRaises(sqlite.ProgrammingError, self.con.create_collation,
            # Lone surrogate cannot be encoded to the default encoding (utf8)
            "\uDC80", collation_cb)

    def CheckRecursiveCursorUse(self):
        """
        http://bugs.python.org/issue10811

        Recursively using a cursor, such jako when reusing it z a generator led to segfaults.
        Now we catch recursive cursor usage oraz podnieś a ProgrammingError.
        """
        con = sqlite.connect(":memory:")

        cur = con.cursor()
        cur.execute("create table a (bar)")
        cur.execute("create table b (baz)")

        def foo():
            cur.execute("insert into a (bar) values (?)", (1,))
            uzyskaj 1

        przy self.assertRaises(sqlite.ProgrammingError):
            cur.executemany("insert into b (baz) values (?)",
                            ((i,) dla i w foo()))

    def CheckConvertTimestampMicrosecondPadding(self):
        """
        http://bugs.python.org/issue14720

        The microsecond parsing of convert_timestamp() should pad przy zeros,
        since the microsecond string "456" actually represents "456000".
        """

        con = sqlite.connect(":memory:", detect_types=sqlite.PARSE_DECLTYPES)
        cur = con.cursor()
        cur.execute("CREATE TABLE t (x TIMESTAMP)")

        # Microseconds should be 456000
        cur.execute("INSERT INTO t (x) VALUES ('2012-04-04 15:06:00.456')")

        # Microseconds should be truncated to 123456
        cur.execute("INSERT INTO t (x) VALUES ('2012-04-04 15:06:00.123456789')")

        cur.execute("SELECT * FROM t")
        values = [x[0] dla x w cur.fetchall()]

        self.assertEqual(values, [
            datetime.datetime(2012, 4, 4, 15, 6, 0, 456000),
            datetime.datetime(2012, 4, 4, 15, 6, 0, 123456),
        ])

    def CheckInvalidIsolationLevelType(self):
        # isolation level jest a string, nie an integer
        self.assertRaises(TypeError,
                          sqlite.connect, ":memory:", isolation_level=123)


    def CheckNullCharacter(self):
        # Issue #21147
        con = sqlite.connect(":memory:")
        self.assertRaises(ValueError, con, "\0select 1")
        self.assertRaises(ValueError, con, "select 1\0")
        cur = con.cursor()
        self.assertRaises(ValueError, cur.execute, " \0select 2")
        self.assertRaises(ValueError, cur.execute, "select 2\0")


def suite():
    regression_suite = unittest.makeSuite(RegressionTests, "Check")
    zwróć unittest.TestSuite((regression_suite,))

def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())

jeżeli __name__ == "__main__":
    test()
