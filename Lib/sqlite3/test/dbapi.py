#-*- coding: iso-8859-1 -*-
# pysqlite2/test/dbapi.py: tests dla DB-API compliance
#
# Copyright (C) 2004-2010 Gerhard H�ring <gh@ghaering.de>
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
spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic

z test.support zaimportuj TESTFN, unlink


klasa ModuleTests(unittest.TestCase):
    def CheckAPILevel(self):
        self.assertEqual(sqlite.apilevel, "2.0",
                         "apilevel jest %s, should be 2.0" % sqlite.apilevel)

    def CheckThreadSafety(self):
        self.assertEqual(sqlite.threadsafety, 1,
                         "threadsafety jest %d, should be 1" % sqlite.threadsafety)

    def CheckParamStyle(self):
        self.assertEqual(sqlite.paramstyle, "qmark",
                         "paramstyle jest '%s', should be 'qmark'" %
                         sqlite.paramstyle)

    def CheckWarning(self):
        self.assertPrawda(issubclass(sqlite.Warning, Exception),
                     "Warning jest nie a subclass of Exception")

    def CheckError(self):
        self.assertPrawda(issubclass(sqlite.Error, Exception),
                        "Error jest nie a subclass of Exception")

    def CheckInterfaceError(self):
        self.assertPrawda(issubclass(sqlite.InterfaceError, sqlite.Error),
                        "InterfaceError jest nie a subclass of Error")

    def CheckDatabaseError(self):
        self.assertPrawda(issubclass(sqlite.DatabaseError, sqlite.Error),
                        "DatabaseError jest nie a subclass of Error")

    def CheckDataError(self):
        self.assertPrawda(issubclass(sqlite.DataError, sqlite.DatabaseError),
                        "DataError jest nie a subclass of DatabaseError")

    def CheckOperationalError(self):
        self.assertPrawda(issubclass(sqlite.OperationalError, sqlite.DatabaseError),
                        "OperationalError jest nie a subclass of DatabaseError")

    def CheckIntegrityError(self):
        self.assertPrawda(issubclass(sqlite.IntegrityError, sqlite.DatabaseError),
                        "IntegrityError jest nie a subclass of DatabaseError")

    def CheckInternalError(self):
        self.assertPrawda(issubclass(sqlite.InternalError, sqlite.DatabaseError),
                        "InternalError jest nie a subclass of DatabaseError")

    def CheckProgrammingError(self):
        self.assertPrawda(issubclass(sqlite.ProgrammingError, sqlite.DatabaseError),
                        "ProgrammingError jest nie a subclass of DatabaseError")

    def CheckNotSupportedError(self):
        self.assertPrawda(issubclass(sqlite.NotSupportedError,
                                   sqlite.DatabaseError),
                        "NotSupportedError jest nie a subclass of DatabaseError")

klasa ConnectionTests(unittest.TestCase):

    def setUp(self):
        self.cx = sqlite.connect(":memory:")
        cu = self.cx.cursor()
        cu.execute("create table test(id integer primary key, name text)")
        cu.execute("insert into test(name) values (?)", ("foo",))

    def tearDown(self):
        self.cx.close()

    def CheckCommit(self):
        self.cx.commit()

    def CheckCommitAfterNoChanges(self):
        """
        A commit should also work when no changes were made to the database.
        """
        self.cx.commit()
        self.cx.commit()

    def CheckRollback(self):
        self.cx.rollback()

    def CheckRollbackAfterNoChanges(self):
        """
        A rollback should also work when no changes were made to the database.
        """
        self.cx.rollback()
        self.cx.rollback()

    def CheckCursor(self):
        cu = self.cx.cursor()

    def CheckFailedOpen(self):
        YOU_CANNOT_OPEN_THIS = "/foo/bar/bla/23534/mydb.db"
        spróbuj:
            con = sqlite.connect(YOU_CANNOT_OPEN_THIS)
        wyjąwszy sqlite.OperationalError:
            zwróć
        self.fail("should have podnieśd an OperationalError")

    def CheckClose(self):
        self.cx.close()

    def CheckExceptions(self):
        # Optional DB-API extension.
        self.assertEqual(self.cx.Warning, sqlite.Warning)
        self.assertEqual(self.cx.Error, sqlite.Error)
        self.assertEqual(self.cx.InterfaceError, sqlite.InterfaceError)
        self.assertEqual(self.cx.DatabaseError, sqlite.DatabaseError)
        self.assertEqual(self.cx.DataError, sqlite.DataError)
        self.assertEqual(self.cx.OperationalError, sqlite.OperationalError)
        self.assertEqual(self.cx.IntegrityError, sqlite.IntegrityError)
        self.assertEqual(self.cx.InternalError, sqlite.InternalError)
        self.assertEqual(self.cx.ProgrammingError, sqlite.ProgrammingError)
        self.assertEqual(self.cx.NotSupportedError, sqlite.NotSupportedError)

    def CheckInTransaction(self):
        # Can't use db z setUp because we want to test initial state.
        cx = sqlite.connect(":memory:")
        cu = cx.cursor()
        self.assertEqual(cx.in_transaction, Nieprawda)
        cu.execute("create table transactiontest(id integer primary key, name text)")
        self.assertEqual(cx.in_transaction, Nieprawda)
        cu.execute("insert into transactiontest(name) values (?)", ("foo",))
        self.assertEqual(cx.in_transaction, Prawda)
        cu.execute("select name z transactiontest where name=?", ["foo"])
        row = cu.fetchone()
        self.assertEqual(cx.in_transaction, Prawda)
        cx.commit()
        self.assertEqual(cx.in_transaction, Nieprawda)
        cu.execute("select name z transactiontest where name=?", ["foo"])
        row = cu.fetchone()
        self.assertEqual(cx.in_transaction, Nieprawda)

    def CheckInTransactionRO(self):
        przy self.assertRaises(AttributeError):
            self.cx.in_transaction = Prawda

    def CheckOpenUri(self):
        jeżeli sqlite.sqlite_version_info < (3, 7, 7):
            przy self.assertRaises(sqlite.NotSupportedError):
                sqlite.connect(':memory:', uri=Prawda)
            zwróć
        self.addCleanup(unlink, TESTFN)
        przy sqlite.connect(TESTFN) jako cx:
            cx.execute('create table test(id integer)')
        przy sqlite.connect('file:' + TESTFN, uri=Prawda) jako cx:
            cx.execute('insert into test(id) values(0)')
        przy sqlite.connect('file:' + TESTFN + '?mode=ro', uri=Prawda) jako cx:
            przy self.assertRaises(sqlite.OperationalError):
                cx.execute('insert into test(id) values(1)')


klasa CursorTests(unittest.TestCase):
    def setUp(self):
        self.cx = sqlite.connect(":memory:")
        self.cu = self.cx.cursor()
        self.cu.execute("create table test(id integer primary key, name text, income number)")
        self.cu.execute("insert into test(name) values (?)", ("foo",))

    def tearDown(self):
        self.cu.close()
        self.cx.close()

    def CheckExecuteNoArgs(self):
        self.cu.execute("delete z test")

    def CheckExecuteIllegalSql(self):
        spróbuj:
            self.cu.execute("select asdf")
            self.fail("should have podnieśd an OperationalError")
        wyjąwszy sqlite.OperationalError:
            zwróć
        wyjąwszy:
            self.fail("raised wrong exception")

    def CheckExecuteTooMuchSql(self):
        spróbuj:
            self.cu.execute("select 5+4; select 4+5")
            self.fail("should have podnieśd a Warning")
        wyjąwszy sqlite.Warning:
            zwróć
        wyjąwszy:
            self.fail("raised wrong exception")

    def CheckExecuteTooMuchSql2(self):
        self.cu.execute("select 5+4; -- foo bar")

    def CheckExecuteTooMuchSql3(self):
        self.cu.execute("""
            select 5+4;

            /*
            foo
            */
            """)

    def CheckExecuteWrongSqlArg(self):
        spróbuj:
            self.cu.execute(42)
            self.fail("should have podnieśd a ValueError")
        wyjąwszy ValueError:
            zwróć
        wyjąwszy:
            self.fail("raised wrong exception.")

    def CheckExecuteArgInt(self):
        self.cu.execute("insert into test(id) values (?)", (42,))

    def CheckExecuteArgFloat(self):
        self.cu.execute("insert into test(income) values (?)", (2500.32,))

    def CheckExecuteArgString(self):
        self.cu.execute("insert into test(name) values (?)", ("Hugo",))

    def CheckExecuteArgStringWithZeroByte(self):
        self.cu.execute("insert into test(name) values (?)", ("Hu\x00go",))

        self.cu.execute("select name z test where id=?", (self.cu.lastrowid,))
        row = self.cu.fetchone()
        self.assertEqual(row[0], "Hu\x00go")

    def CheckExecuteWrongNoOfArgs1(self):
        # too many parameters
        spróbuj:
            self.cu.execute("insert into test(id) values (?)", (17, "Egon"))
            self.fail("should have podnieśd ProgrammingError")
        wyjąwszy sqlite.ProgrammingError:
            dalej

    def CheckExecuteWrongNoOfArgs2(self):
        # too little parameters
        spróbuj:
            self.cu.execute("insert into test(id) values (?)")
            self.fail("should have podnieśd ProgrammingError")
        wyjąwszy sqlite.ProgrammingError:
            dalej

    def CheckExecuteWrongNoOfArgs3(self):
        # no parameters, parameters are needed
        spróbuj:
            self.cu.execute("insert into test(id) values (?)")
            self.fail("should have podnieśd ProgrammingError")
        wyjąwszy sqlite.ProgrammingError:
            dalej

    def CheckExecuteParamList(self):
        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("select name z test where name=?", ["foo"])
        row = self.cu.fetchone()
        self.assertEqual(row[0], "foo")

    def CheckExecuteParamSequence(self):
        klasa L(object):
            def __len__(self):
                zwróć 1
            def __getitem__(self, x):
                assert x == 0
                zwróć "foo"

        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("select name z test where name=?", L())
        row = self.cu.fetchone()
        self.assertEqual(row[0], "foo")

    def CheckExecuteDictMapping(self):
        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("select name z test where name=:name", {"name": "foo"})
        row = self.cu.fetchone()
        self.assertEqual(row[0], "foo")

    def CheckExecuteDictMapping_Mapping(self):
        klasa D(dict):
            def __missing__(self, key):
                zwróć "foo"

        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("select name z test where name=:name", D())
        row = self.cu.fetchone()
        self.assertEqual(row[0], "foo")

    def CheckExecuteDictMappingTooLittleArgs(self):
        self.cu.execute("insert into test(name) values ('foo')")
        spróbuj:
            self.cu.execute("select name z test where name=:name oraz id=:id", {"name": "foo"})
            self.fail("should have podnieśd ProgrammingError")
        wyjąwszy sqlite.ProgrammingError:
            dalej

    def CheckExecuteDictMappingNoArgs(self):
        self.cu.execute("insert into test(name) values ('foo')")
        spróbuj:
            self.cu.execute("select name z test where name=:name")
            self.fail("should have podnieśd ProgrammingError")
        wyjąwszy sqlite.ProgrammingError:
            dalej

    def CheckExecuteDictMappingUnnamed(self):
        self.cu.execute("insert into test(name) values ('foo')")
        spróbuj:
            self.cu.execute("select name z test where name=?", {"name": "foo"})
            self.fail("should have podnieśd ProgrammingError")
        wyjąwszy sqlite.ProgrammingError:
            dalej

    def CheckClose(self):
        self.cu.close()

    def CheckRowcountExecute(self):
        self.cu.execute("delete z test")
        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("update test set name='bar'")
        self.assertEqual(self.cu.rowcount, 2)

    def CheckRowcountSelect(self):
        """
        pysqlite does nie know the rowcount of SELECT statements, because we
        don't fetch all rows after executing the select statement. The rowcount
        has thus to be -1.
        """
        self.cu.execute("select 5 union select 6")
        self.assertEqual(self.cu.rowcount, -1)

    def CheckRowcountExecutemany(self):
        self.cu.execute("delete z test")
        self.cu.executemany("insert into test(name) values (?)", [(1,), (2,), (3,)])
        self.assertEqual(self.cu.rowcount, 3)

    def CheckTotalChanges(self):
        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("insert into test(name) values ('foo')")
        jeżeli self.cx.total_changes < 2:
            self.fail("total changes reported wrong value")

    # Checks dla executemany:
    # Sequences are required by the DB-API, iterators
    # enhancements w pysqlite.

    def CheckExecuteManySequence(self):
        self.cu.executemany("insert into test(income) values (?)", [(x,) dla x w range(100, 110)])

    def CheckExecuteManyIterator(self):
        klasa MyIter:
            def __init__(self):
                self.value = 5

            def __next__(self):
                jeżeli self.value == 10:
                    podnieś StopIteration
                inaczej:
                    self.value += 1
                    zwróć (self.value,)

        self.cu.executemany("insert into test(income) values (?)", MyIter())

    def CheckExecuteManyGenerator(self):
        def mygen():
            dla i w range(5):
                uzyskaj (i,)

        self.cu.executemany("insert into test(income) values (?)", mygen())

    def CheckExecuteManyWrongSqlArg(self):
        spróbuj:
            self.cu.executemany(42, [(3,)])
            self.fail("should have podnieśd a ValueError")
        wyjąwszy ValueError:
            zwróć
        wyjąwszy:
            self.fail("raised wrong exception.")

    def CheckExecuteManySelect(self):
        spróbuj:
            self.cu.executemany("select ?", [(3,)])
            self.fail("should have podnieśd a ProgrammingError")
        wyjąwszy sqlite.ProgrammingError:
            zwróć
        wyjąwszy:
            self.fail("raised wrong exception.")

    def CheckExecuteManyNotIterable(self):
        spróbuj:
            self.cu.executemany("insert into test(income) values (?)", 42)
            self.fail("should have podnieśd a TypeError")
        wyjąwszy TypeError:
            zwróć
        wyjąwszy Exception jako e:
            print("raised", e.__class__)
            self.fail("raised wrong exception.")

    def CheckFetchIter(self):
        # Optional DB-API extension.
        self.cu.execute("delete z test")
        self.cu.execute("insert into test(id) values (?)", (5,))
        self.cu.execute("insert into test(id) values (?)", (6,))
        self.cu.execute("select id z test order by id")
        lst = []
        dla row w self.cu:
            lst.append(row[0])
        self.assertEqual(lst[0], 5)
        self.assertEqual(lst[1], 6)

    def CheckFetchone(self):
        self.cu.execute("select name z test")
        row = self.cu.fetchone()
        self.assertEqual(row[0], "foo")
        row = self.cu.fetchone()
        self.assertEqual(row, Nic)

    def CheckFetchoneNoStatement(self):
        cur = self.cx.cursor()
        row = cur.fetchone()
        self.assertEqual(row, Nic)

    def CheckArraySize(self):
        # must default ot 1
        self.assertEqual(self.cu.arraysize, 1)

        # now set to 2
        self.cu.arraysize = 2

        # now make the query zwróć 3 rows
        self.cu.execute("delete z test")
        self.cu.execute("insert into test(name) values ('A')")
        self.cu.execute("insert into test(name) values ('B')")
        self.cu.execute("insert into test(name) values ('C')")
        self.cu.execute("select name z test")
        res = self.cu.fetchmany()

        self.assertEqual(len(res), 2)

    def CheckFetchmany(self):
        self.cu.execute("select name z test")
        res = self.cu.fetchmany(100)
        self.assertEqual(len(res), 1)
        res = self.cu.fetchmany(100)
        self.assertEqual(res, [])

    def CheckFetchmanyKwArg(self):
        """Checks jeżeli fetchmany works przy keyword arguments"""
        self.cu.execute("select name z test")
        res = self.cu.fetchmany(size=100)
        self.assertEqual(len(res), 1)

    def CheckFetchall(self):
        self.cu.execute("select name z test")
        res = self.cu.fetchall()
        self.assertEqual(len(res), 1)
        res = self.cu.fetchall()
        self.assertEqual(res, [])

    def CheckSetinputsizes(self):
        self.cu.setinputsizes([3, 4, 5])

    def CheckSetoutputsize(self):
        self.cu.setoutputsize(5, 0)

    def CheckSetoutputsizeNoColumn(self):
        self.cu.setoutputsize(42)

    def CheckCursorConnection(self):
        # Optional DB-API extension.
        self.assertEqual(self.cu.connection, self.cx)

    def CheckWrongCursorCallable(self):
        spróbuj:
            def f(): dalej
            cur = self.cx.cursor(f)
            self.fail("should have podnieśd a TypeError")
        wyjąwszy TypeError:
            zwróć
        self.fail("should have podnieśd a ValueError")

    def CheckCursorWrongClass(self):
        klasa Foo: dalej
        foo = Foo()
        spróbuj:
            cur = sqlite.Cursor(foo)
            self.fail("should have podnieśd a ValueError")
        wyjąwszy TypeError:
            dalej

@unittest.skipUnless(threading, 'This test requires threading.')
klasa ThreadTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite.connect(":memory:")
        self.cur = self.con.cursor()
        self.cur.execute("create table test(id integer primary key, name text, bin binary, ratio number, ts timestamp)")

    def tearDown(self):
        self.cur.close()
        self.con.close()

    def CheckConCursor(self):
        def run(con, errors):
            spróbuj:
                cur = con.cursor()
                errors.append("did nie podnieś ProgrammingError")
                zwróć
            wyjąwszy sqlite.ProgrammingError:
                zwróć
            wyjąwszy:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"con": self.con, "errors": errors})
        t.start()
        t.join()
        jeżeli len(errors) > 0:
            self.fail("\n".join(errors))

    def CheckConCommit(self):
        def run(con, errors):
            spróbuj:
                con.commit()
                errors.append("did nie podnieś ProgrammingError")
                zwróć
            wyjąwszy sqlite.ProgrammingError:
                zwróć
            wyjąwszy:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"con": self.con, "errors": errors})
        t.start()
        t.join()
        jeżeli len(errors) > 0:
            self.fail("\n".join(errors))

    def CheckConRollback(self):
        def run(con, errors):
            spróbuj:
                con.rollback()
                errors.append("did nie podnieś ProgrammingError")
                zwróć
            wyjąwszy sqlite.ProgrammingError:
                zwróć
            wyjąwszy:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"con": self.con, "errors": errors})
        t.start()
        t.join()
        jeżeli len(errors) > 0:
            self.fail("\n".join(errors))

    def CheckConClose(self):
        def run(con, errors):
            spróbuj:
                con.close()
                errors.append("did nie podnieś ProgrammingError")
                zwróć
            wyjąwszy sqlite.ProgrammingError:
                zwróć
            wyjąwszy:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"con": self.con, "errors": errors})
        t.start()
        t.join()
        jeżeli len(errors) > 0:
            self.fail("\n".join(errors))

    def CheckCurImplicitBegin(self):
        def run(cur, errors):
            spróbuj:
                cur.execute("insert into test(name) values ('a')")
                errors.append("did nie podnieś ProgrammingError")
                zwróć
            wyjąwszy sqlite.ProgrammingError:
                zwróć
            wyjąwszy:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"cur": self.cur, "errors": errors})
        t.start()
        t.join()
        jeżeli len(errors) > 0:
            self.fail("\n".join(errors))

    def CheckCurClose(self):
        def run(cur, errors):
            spróbuj:
                cur.close()
                errors.append("did nie podnieś ProgrammingError")
                zwróć
            wyjąwszy sqlite.ProgrammingError:
                zwróć
            wyjąwszy:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"cur": self.cur, "errors": errors})
        t.start()
        t.join()
        jeżeli len(errors) > 0:
            self.fail("\n".join(errors))

    def CheckCurExecute(self):
        def run(cur, errors):
            spróbuj:
                cur.execute("select name z test")
                errors.append("did nie podnieś ProgrammingError")
                zwróć
            wyjąwszy sqlite.ProgrammingError:
                zwróć
            wyjąwszy:
                errors.append("raised wrong exception")

        errors = []
        self.cur.execute("insert into test(name) values ('a')")
        t = threading.Thread(target=run, kwargs={"cur": self.cur, "errors": errors})
        t.start()
        t.join()
        jeżeli len(errors) > 0:
            self.fail("\n".join(errors))

    def CheckCurIterNext(self):
        def run(cur, errors):
            spróbuj:
                row = cur.fetchone()
                errors.append("did nie podnieś ProgrammingError")
                zwróć
            wyjąwszy sqlite.ProgrammingError:
                zwróć
            wyjąwszy:
                errors.append("raised wrong exception")

        errors = []
        self.cur.execute("insert into test(name) values ('a')")
        self.cur.execute("select name z test")
        t = threading.Thread(target=run, kwargs={"cur": self.cur, "errors": errors})
        t.start()
        t.join()
        jeżeli len(errors) > 0:
            self.fail("\n".join(errors))

klasa ConstructorTests(unittest.TestCase):
    def CheckDate(self):
        d = sqlite.Date(2004, 10, 28)

    def CheckTime(self):
        t = sqlite.Time(12, 39, 35)

    def CheckTimestamp(self):
        ts = sqlite.Timestamp(2004, 10, 28, 12, 39, 35)

    def CheckDateFromTicks(self):
        d = sqlite.DateFromTicks(42)

    def CheckTimeFromTicks(self):
        t = sqlite.TimeFromTicks(42)

    def CheckTimestampFromTicks(self):
        ts = sqlite.TimestampFromTicks(42)

    def CheckBinary(self):
        b = sqlite.Binary(b"\0'")

klasa ExtensionTests(unittest.TestCase):
    def CheckScriptStringSql(self):
        con = sqlite.connect(":memory:")
        cur = con.cursor()
        cur.executescript("""
            -- bla bla
            /* a stupid comment */
            create table a(i);
            insert into a(i) values (5);
            """)
        cur.execute("select i z a")
        res = cur.fetchone()[0]
        self.assertEqual(res, 5)

    def CheckScriptSyntaxError(self):
        con = sqlite.connect(":memory:")
        cur = con.cursor()
        podnieśd = Nieprawda
        spróbuj:
            cur.executescript("create table test(x); asdf; create table test2(x)")
        wyjąwszy sqlite.OperationalError:
            podnieśd = Prawda
        self.assertEqual(raised, Prawda, "should have podnieśd an exception")

    def CheckScriptErrorNormal(self):
        con = sqlite.connect(":memory:")
        cur = con.cursor()
        podnieśd = Nieprawda
        spróbuj:
            cur.executescript("create table test(sadfsadfdsa); select foo z hurz;")
        wyjąwszy sqlite.OperationalError:
            podnieśd = Prawda
        self.assertEqual(raised, Prawda, "should have podnieśd an exception")

    def CheckConnectionExecute(self):
        con = sqlite.connect(":memory:")
        result = con.execute("select 5").fetchone()[0]
        self.assertEqual(result, 5, "Basic test of Connection.execute")

    def CheckConnectionExecutemany(self):
        con = sqlite.connect(":memory:")
        con.execute("create table test(foo)")
        con.executemany("insert into test(foo) values (?)", [(3,), (4,)])
        result = con.execute("select foo z test order by foo").fetchall()
        self.assertEqual(result[0][0], 3, "Basic test of Connection.executemany")
        self.assertEqual(result[1][0], 4, "Basic test of Connection.executemany")

    def CheckConnectionExecutescript(self):
        con = sqlite.connect(":memory:")
        con.executescript("create table test(foo); insert into test(foo) values (5);")
        result = con.execute("select foo z test").fetchone()[0]
        self.assertEqual(result, 5, "Basic test of Connection.executescript")

klasa ClosedConTests(unittest.TestCase):
    def setUp(self):
        dalej

    def tearDown(self):
        dalej

    def CheckClosedConCursor(self):
        con = sqlite.connect(":memory:")
        con.close()
        spróbuj:
            cur = con.cursor()
            self.fail("Should have podnieśd a ProgrammingError")
        wyjąwszy sqlite.ProgrammingError:
            dalej
        wyjąwszy:
            self.fail("Should have podnieśd a ProgrammingError")

    def CheckClosedConCommit(self):
        con = sqlite.connect(":memory:")
        con.close()
        spróbuj:
            con.commit()
            self.fail("Should have podnieśd a ProgrammingError")
        wyjąwszy sqlite.ProgrammingError:
            dalej
        wyjąwszy:
            self.fail("Should have podnieśd a ProgrammingError")

    def CheckClosedConRollback(self):
        con = sqlite.connect(":memory:")
        con.close()
        spróbuj:
            con.rollback()
            self.fail("Should have podnieśd a ProgrammingError")
        wyjąwszy sqlite.ProgrammingError:
            dalej
        wyjąwszy:
            self.fail("Should have podnieśd a ProgrammingError")

    def CheckClosedCurExecute(self):
        con = sqlite.connect(":memory:")
        cur = con.cursor()
        con.close()
        spróbuj:
            cur.execute("select 4")
            self.fail("Should have podnieśd a ProgrammingError")
        wyjąwszy sqlite.ProgrammingError:
            dalej
        wyjąwszy:
            self.fail("Should have podnieśd a ProgrammingError")

    def CheckClosedCreateFunction(self):
        con = sqlite.connect(":memory:")
        con.close()
        def f(x): zwróć 17
        spróbuj:
            con.create_function("foo", 1, f)
            self.fail("Should have podnieśd a ProgrammingError")
        wyjąwszy sqlite.ProgrammingError:
            dalej
        wyjąwszy:
            self.fail("Should have podnieśd a ProgrammingError")

    def CheckClosedCreateAggregate(self):
        con = sqlite.connect(":memory:")
        con.close()
        klasa Agg:
            def __init__(self):
                dalej
            def step(self, x):
                dalej
            def finalize(self):
                zwróć 17
        spróbuj:
            con.create_aggregate("foo", 1, Agg)
            self.fail("Should have podnieśd a ProgrammingError")
        wyjąwszy sqlite.ProgrammingError:
            dalej
        wyjąwszy:
            self.fail("Should have podnieśd a ProgrammingError")

    def CheckClosedSetAuthorizer(self):
        con = sqlite.connect(":memory:")
        con.close()
        def authorizer(*args):
            zwróć sqlite.DENY
        spróbuj:
            con.set_authorizer(authorizer)
            self.fail("Should have podnieśd a ProgrammingError")
        wyjąwszy sqlite.ProgrammingError:
            dalej
        wyjąwszy:
            self.fail("Should have podnieśd a ProgrammingError")

    def CheckClosedSetProgressCallback(self):
        con = sqlite.connect(":memory:")
        con.close()
        def progress(): dalej
        spróbuj:
            con.set_progress_handler(progress, 100)
            self.fail("Should have podnieśd a ProgrammingError")
        wyjąwszy sqlite.ProgrammingError:
            dalej
        wyjąwszy:
            self.fail("Should have podnieśd a ProgrammingError")

    def CheckClosedCall(self):
        con = sqlite.connect(":memory:")
        con.close()
        spróbuj:
            con()
            self.fail("Should have podnieśd a ProgrammingError")
        wyjąwszy sqlite.ProgrammingError:
            dalej
        wyjąwszy:
            self.fail("Should have podnieśd a ProgrammingError")

klasa ClosedCurTests(unittest.TestCase):
    def setUp(self):
        dalej

    def tearDown(self):
        dalej

    def CheckClosed(self):
        con = sqlite.connect(":memory:")
        cur = con.cursor()
        cur.close()

        dla method_name w ("execute", "executemany", "executescript", "fetchall", "fetchmany", "fetchone"):
            jeżeli method_name w ("execute", "executescript"):
                params = ("select 4 union select 5",)
            albo_inaczej method_name == "executemany":
                params = ("insert into foo(bar) values (?)", [(3,), (4,)])
            inaczej:
                params = []

            spróbuj:
                method = getattr(cur, method_name)

                method(*params)
                self.fail("Should have podnieśd a ProgrammingError: method " + method_name)
            wyjąwszy sqlite.ProgrammingError:
                dalej
            wyjąwszy:
                self.fail("Should have podnieśd a ProgrammingError: " + method_name)

def suite():
    module_suite = unittest.makeSuite(ModuleTests, "Check")
    connection_suite = unittest.makeSuite(ConnectionTests, "Check")
    cursor_suite = unittest.makeSuite(CursorTests, "Check")
    thread_suite = unittest.makeSuite(ThreadTests, "Check")
    constructor_suite = unittest.makeSuite(ConstructorTests, "Check")
    ext_suite = unittest.makeSuite(ExtensionTests, "Check")
    closed_con_suite = unittest.makeSuite(ClosedConTests, "Check")
    closed_cur_suite = unittest.makeSuite(ClosedCurTests, "Check")
    zwróć unittest.TestSuite((module_suite, connection_suite, cursor_suite, thread_suite, constructor_suite, ext_suite, closed_con_suite, closed_cur_suite))

def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())

jeżeli __name__ == "__main__":
    test()
