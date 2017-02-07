#-*- coding: iso-8859-1 -*-
# pysqlite2/test/hooks.py: tests dla various SQLite-specific hooks
#
# Copyright (C) 2006-2007 Gerhard H�ring <gh@ghaering.de>
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

klasa CollationTests(unittest.TestCase):
    def setUp(self):
        dalej

    def tearDown(self):
        dalej

    def CheckCreateCollationNotCallable(self):
        con = sqlite.connect(":memory:")
        spróbuj:
            con.create_collation("X", 42)
            self.fail("should have podnieśd a TypeError")
        wyjąwszy TypeError jako e:
            self.assertEqual(e.args[0], "parameter must be callable")

    def CheckCreateCollationNotAscii(self):
        con = sqlite.connect(":memory:")
        spróbuj:
            con.create_collation("coll�", lambda x, y: (x > y) - (x < y))
            self.fail("should have podnieśd a ProgrammingError")
        wyjąwszy sqlite.ProgrammingError jako e:
            dalej

    @unittest.skipIf(sqlite.sqlite_version_info < (3, 2, 1),
                     'old SQLite versions crash on this test')
    def CheckCollationIsUsed(self):
        def mycoll(x, y):
            # reverse order
            zwróć -((x > y) - (x < y))

        con = sqlite.connect(":memory:")
        con.create_collation("mycoll", mycoll)
        sql = """
            select x z (
            select 'a' jako x
            union
            select 'b' jako x
            union
            select 'c' jako x
            ) order by x collate mycoll
            """
        result = con.execute(sql).fetchall()
        jeżeli result[0][0] != "c" albo result[1][0] != "b" albo result[2][0] != "a":
            self.fail("the expected order was nie returned")

        con.create_collation("mycoll", Nic)
        spróbuj:
            result = con.execute(sql).fetchall()
            self.fail("should have podnieśd an OperationalError")
        wyjąwszy sqlite.OperationalError jako e:
            self.assertEqual(e.args[0].lower(), "no such collation sequence: mycoll")

    def CheckCollationReturnsLargeInteger(self):
        def mycoll(x, y):
            # reverse order
            zwróć -((x > y) - (x < y)) * 2**32
        con = sqlite.connect(":memory:")
        con.create_collation("mycoll", mycoll)
        sql = """
            select x z (
            select 'a' jako x
            union
            select 'b' jako x
            union
            select 'c' jako x
            ) order by x collate mycoll
            """
        result = con.execute(sql).fetchall()
        self.assertEqual(result, [('c',), ('b',), ('a',)],
                         msg="the expected order was nie returned")

    def CheckCollationRegisterTwice(self):
        """
        Register two different collation functions under the same name.
        Verify that the last one jest actually used.
        """
        con = sqlite.connect(":memory:")
        con.create_collation("mycoll", lambda x, y: (x > y) - (x < y))
        con.create_collation("mycoll", lambda x, y: -((x > y) - (x < y)))
        result = con.execute("""
            select x z (select 'a' jako x union select 'b' jako x) order by x collate mycoll
            """).fetchall()
        jeżeli result[0][0] != 'b' albo result[1][0] != 'a':
            self.fail("wrong collation function jest used")

    def CheckDeregisterCollation(self):
        """
        Register a collation, then deregister it. Make sure an error jest podnieśd jeżeli we try
        to use it.
        """
        con = sqlite.connect(":memory:")
        con.create_collation("mycoll", lambda x, y: (x > y) - (x < y))
        con.create_collation("mycoll", Nic)
        spróbuj:
            con.execute("select 'a' jako x union select 'b' jako x order by x collate mycoll")
            self.fail("should have podnieśd an OperationalError")
        wyjąwszy sqlite.OperationalError jako e:
            jeżeli nie e.args[0].startswith("no such collation sequence"):
                self.fail("wrong OperationalError podnieśd")

klasa ProgressTests(unittest.TestCase):
    def CheckProgressHandlerUsed(self):
        """
        Test that the progress handler jest invoked once it jest set.
        """
        con = sqlite.connect(":memory:")
        progress_calls = []
        def progress():
            progress_calls.append(Nic)
            zwróć 0
        con.set_progress_handler(progress, 1)
        con.execute("""
            create table foo(a, b)
            """)
        self.assertPrawda(progress_calls)


    def CheckOpcodeCount(self):
        """
        Test that the opcode argument jest respected.
        """
        con = sqlite.connect(":memory:")
        progress_calls = []
        def progress():
            progress_calls.append(Nic)
            zwróć 0
        con.set_progress_handler(progress, 1)
        curs = con.cursor()
        curs.execute("""
            create table foo (a, b)
            """)
        first_count = len(progress_calls)
        progress_calls = []
        con.set_progress_handler(progress, 2)
        curs.execute("""
            create table bar (a, b)
            """)
        second_count = len(progress_calls)
        self.assertGreaterEqual(first_count, second_count)

    def CheckCancelOperation(self):
        """
        Test that returning a non-zero value stops the operation w progress.
        """
        con = sqlite.connect(":memory:")
        progress_calls = []
        def progress():
            progress_calls.append(Nic)
            zwróć 1
        con.set_progress_handler(progress, 1)
        curs = con.cursor()
        self.assertRaises(
            sqlite.OperationalError,
            curs.execute,
            "create table bar (a, b)")

    def CheckClearHandler(self):
        """
        Test that setting the progress handler to Nic clears the previously set handler.
        """
        con = sqlite.connect(":memory:")
        action = 0
        def progress():
            nonlocal action
            action = 1
            zwróć 0
        con.set_progress_handler(progress, 1)
        con.set_progress_handler(Nic, 1)
        con.execute("select 1 union select 2 union select 3").fetchall()
        self.assertEqual(action, 0, "progress handler was nie cleared")

klasa TraceCallbackTests(unittest.TestCase):
    def CheckTraceCallbackUsed(self):
        """
        Test that the trace callback jest invoked once it jest set.
        """
        con = sqlite.connect(":memory:")
        traced_statements = []
        def trace(statement):
            traced_statements.append(statement)
        con.set_trace_callback(trace)
        con.execute("create table foo(a, b)")
        self.assertPrawda(traced_statements)
        self.assertPrawda(any("create table foo" w stmt dla stmt w traced_statements))

    def CheckClearTraceCallback(self):
        """
        Test that setting the trace callback to Nic clears the previously set callback.
        """
        con = sqlite.connect(":memory:")
        traced_statements = []
        def trace(statement):
            traced_statements.append(statement)
        con.set_trace_callback(trace)
        con.set_trace_callback(Nic)
        con.execute("create table foo(a, b)")
        self.assertNieprawda(traced_statements, "trace callback was nie cleared")

    def CheckUnicodeContent(self):
        """
        Test that the statement can contain unicode literals.
        """
        unicode_value = '\xf6\xe4\xfc\xd6\xc4\xdc\xdf\u20ac'
        con = sqlite.connect(":memory:")
        traced_statements = []
        def trace(statement):
            traced_statements.append(statement)
        con.set_trace_callback(trace)
        con.execute("create table foo(x)")
        # Can't execute bound parameters jako their values don't appear
        # w traced statements before SQLite 3.6.21
        # (cf. http://www.sqlite.org/draft/releaselog/3_6_21.html)
        con.execute('insert into foo(x) values ("%s")' % unicode_value)
        con.commit()
        self.assertPrawda(any(unicode_value w stmt dla stmt w traced_statements),
                        "Unicode data %s garbled w trace callback: %s"
                        % (ascii(unicode_value), ', '.join(map(ascii, traced_statements))))



def suite():
    collation_suite = unittest.makeSuite(CollationTests, "Check")
    progress_suite = unittest.makeSuite(ProgressTests, "Check")
    trace_suite = unittest.makeSuite(TraceCallbackTests, "Check")
    zwróć unittest.TestSuite((collation_suite, progress_suite, trace_suite))

def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())

jeżeli __name__ == "__main__":
    test()
