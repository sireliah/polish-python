#-*- coding: iso-8859-1 -*-
# pysqlite2/test/transactions.py: tests transactions
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

zaimportuj os, unittest
zaimportuj sqlite3 jako sqlite

def get_db_path():
    zwróć "sqlite_testdb"

klasa TransactionTests(unittest.TestCase):
    def setUp(self):
        spróbuj:
            os.remove(get_db_path())
        wyjąwszy OSError:
            dalej

        self.con1 = sqlite.connect(get_db_path(), timeout=0.1)
        self.cur1 = self.con1.cursor()

        self.con2 = sqlite.connect(get_db_path(), timeout=0.1)
        self.cur2 = self.con2.cursor()

    def tearDown(self):
        self.cur1.close()
        self.con1.close()

        self.cur2.close()
        self.con2.close()

        spróbuj:
            os.unlink(get_db_path())
        wyjąwszy OSError:
            dalej

    def CheckDMLdoesAutoCommitBefore(self):
        self.cur1.execute("create table test(i)")
        self.cur1.execute("insert into test(i) values (5)")
        self.cur1.execute("create table test2(j)")
        self.cur2.execute("select i z test")
        res = self.cur2.fetchall()
        self.assertEqual(len(res), 1)

    def CheckInsertStartsTransaction(self):
        self.cur1.execute("create table test(i)")
        self.cur1.execute("insert into test(i) values (5)")
        self.cur2.execute("select i z test")
        res = self.cur2.fetchall()
        self.assertEqual(len(res), 0)

    def CheckUpdateStartsTransaction(self):
        self.cur1.execute("create table test(i)")
        self.cur1.execute("insert into test(i) values (5)")
        self.con1.commit()
        self.cur1.execute("update test set i=6")
        self.cur2.execute("select i z test")
        res = self.cur2.fetchone()[0]
        self.assertEqual(res, 5)

    def CheckDeleteStartsTransaction(self):
        self.cur1.execute("create table test(i)")
        self.cur1.execute("insert into test(i) values (5)")
        self.con1.commit()
        self.cur1.execute("delete z test")
        self.cur2.execute("select i z test")
        res = self.cur2.fetchall()
        self.assertEqual(len(res), 1)

    def CheckReplaceStartsTransaction(self):
        self.cur1.execute("create table test(i)")
        self.cur1.execute("insert into test(i) values (5)")
        self.con1.commit()
        self.cur1.execute("replace into test(i) values (6)")
        self.cur2.execute("select i z test")
        res = self.cur2.fetchall()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0], 5)

    def CheckToggleAutoCommit(self):
        self.cur1.execute("create table test(i)")
        self.cur1.execute("insert into test(i) values (5)")
        self.con1.isolation_level = Nic
        self.assertEqual(self.con1.isolation_level, Nic)
        self.cur2.execute("select i z test")
        res = self.cur2.fetchall()
        self.assertEqual(len(res), 1)

        self.con1.isolation_level = "DEFERRED"
        self.assertEqual(self.con1.isolation_level , "DEFERRED")
        self.cur1.execute("insert into test(i) values (5)")
        self.cur2.execute("select i z test")
        res = self.cur2.fetchall()
        self.assertEqual(len(res), 1)

    def CheckRaiseTimeout(self):
        jeżeli sqlite.sqlite_version_info < (3, 2, 2):
            # This will fail (hang) on earlier versions of sqlite.
            # Determine exact version it was fixed. 3.2.1 hangs.
            zwróć
        self.cur1.execute("create table test(i)")
        self.cur1.execute("insert into test(i) values (5)")
        spróbuj:
            self.cur2.execute("insert into test(i) values (5)")
            self.fail("should have podnieśd an OperationalError")
        wyjąwszy sqlite.OperationalError:
            dalej
        wyjąwszy:
            self.fail("should have podnieśd an OperationalError")

    def CheckLocking(self):
        """
        This tests the improved concurrency przy pysqlite 2.3.4. You needed
        to roll back con2 before you could commit con1.
        """
        jeżeli sqlite.sqlite_version_info < (3, 2, 2):
            # This will fail (hang) on earlier versions of sqlite.
            # Determine exact version it was fixed. 3.2.1 hangs.
            zwróć
        self.cur1.execute("create table test(i)")
        self.cur1.execute("insert into test(i) values (5)")
        spróbuj:
            self.cur2.execute("insert into test(i) values (5)")
            self.fail("should have podnieśd an OperationalError")
        wyjąwszy sqlite.OperationalError:
            dalej
        wyjąwszy:
            self.fail("should have podnieśd an OperationalError")
        # NO self.con2.rollback() HERE!!!
        self.con1.commit()

    def CheckRollbackCursorConsistency(self):
        """
        Checks jeżeli cursors on the connection are set into a "reset" state
        when a rollback jest done on the connection.
        """
        con = sqlite.connect(":memory:")
        cur = con.cursor()
        cur.execute("create table test(x)")
        cur.execute("insert into test(x) values (5)")
        cur.execute("select 1 union select 2 union select 3")

        con.rollback()
        spróbuj:
            cur.fetchall()
            self.fail("InterfaceError should have been podnieśd")
        wyjąwszy sqlite.InterfaceError jako e:
            dalej
        wyjąwszy:
            self.fail("InterfaceError should have been podnieśd")

klasa SpecialCommandTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite.connect(":memory:")
        self.cur = self.con.cursor()

    def CheckVacuum(self):
        self.cur.execute("create table test(i)")
        self.cur.execute("insert into test(i) values (5)")
        self.cur.execute("vacuum")

    def CheckDropTable(self):
        self.cur.execute("create table test(i)")
        self.cur.execute("insert into test(i) values (5)")
        self.cur.execute("drop table test")

    def CheckPragma(self):
        self.cur.execute("create table test(i)")
        self.cur.execute("insert into test(i) values (5)")
        self.cur.execute("pragma count_changes=1")

    def tearDown(self):
        self.cur.close()
        self.con.close()

def suite():
    default_suite = unittest.makeSuite(TransactionTests, "Check")
    special_command_suite = unittest.makeSuite(SpecialCommandTests, "Check")
    zwróć unittest.TestSuite((default_suite, special_command_suite))

def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())

jeżeli __name__ == "__main__":
    test()
