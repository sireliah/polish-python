#-*- coding: iso-8859-1 -*-
# pysqlite2/test/userfunctions.py: tests dla user-defined functions oraz
#                                  aggregates.
#
# Copyright (C) 2005-2007 Gerhard H鋜ing <gh@ghaering.de>
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

def func_returntext():
    zwr贸膰 "foo"
def func_returnunicode():
    zwr贸膰 "bar"
def func_returnint():
    zwr贸膰 42
def func_returnfloat():
    zwr贸膰 3.14
def func_returnnull():
    zwr贸膰 Nic
def func_returnblob():
    zwr贸膰 b"blob"
def func_returnlonglong():
    zwr贸膰 1<<31
def func_raiseexception():
    5/0

def func_isstring(v):
    zwr贸膰 type(v) jest str
def func_isint(v):
    zwr贸膰 type(v) jest int
def func_isfloat(v):
    zwr贸膰 type(v) jest float
def func_isnone(v):
    zwr贸膰 type(v) jest type(Nic)
def func_isblob(v):
    zwr贸膰 isinstance(v, (bytes, memoryview))
def func_islonglong(v):
    zwr贸膰 isinstance(v, int) oraz v >= 1<<31

klasa AggrNoStep:
    def __init__(self):
        dalej

    def finalize(self):
        zwr贸膰 1

klasa AggrNoFinalize:
    def __init__(self):
        dalej

    def step(self, x):
        dalej

klasa AggrExceptionInInit:
    def __init__(self):
        5/0

    def step(self, x):
        dalej

    def finalize(self):
        dalej

klasa AggrExceptionInStep:
    def __init__(self):
        dalej

    def step(self, x):
        5/0

    def finalize(self):
        zwr贸膰 42

klasa AggrExceptionInFinalize:
    def __init__(self):
        dalej

    def step(self, x):
        dalej

    def finalize(self):
        5/0

klasa AggrCheckType:
    def __init__(self):
        self.val = Nic

    def step(self, whichType, val):
        theType = {"str": str, "int": int, "float": float, "Nic": type(Nic),
                   "blob": bytes}
        self.val = int(theType[whichType] jest type(val))

    def finalize(self):
        zwr贸膰 self.val

klasa AggrSum:
    def __init__(self):
        self.val = 0.0

    def step(self, val):
        self.val += val

    def finalize(self):
        zwr贸膰 self.val

klasa FunctionTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite.connect(":memory:")

        self.con.create_function("returntext", 0, func_returntext)
        self.con.create_function("returnunicode", 0, func_returnunicode)
        self.con.create_function("returnint", 0, func_returnint)
        self.con.create_function("returnfloat", 0, func_returnfloat)
        self.con.create_function("returnnull", 0, func_returnnull)
        self.con.create_function("returnblob", 0, func_returnblob)
        self.con.create_function("returnlonglong", 0, func_returnlonglong)
        self.con.create_function("raiseexception", 0, func_raiseexception)

        self.con.create_function("isstring", 1, func_isstring)
        self.con.create_function("isint", 1, func_isint)
        self.con.create_function("isfloat", 1, func_isfloat)
        self.con.create_function("isnone", 1, func_isnone)
        self.con.create_function("isblob", 1, func_isblob)
        self.con.create_function("islonglong", 1, func_islonglong)

    def tearDown(self):
        self.con.close()

    def CheckFuncErrorOnCreate(self):
        spr贸buj:
            self.con.create_function("bla", -100, lambda x: 2*x)
            self.fail("should have podnie艣d an OperationalError")
        wyj膮wszy sqlite.OperationalError:
            dalej

    def CheckFuncRefCount(self):
        def getfunc():
            def f():
                zwr贸膰 1
            zwr贸膰 f
        f = getfunc()
        globals()["foo"] = f
        # self.con.create_function("reftest", 0, getfunc())
        self.con.create_function("reftest", 0, f)
        cur = self.con.cursor()
        cur.execute("select reftest()")

    def CheckFuncReturnText(self):
        cur = self.con.cursor()
        cur.execute("select returntext()")
        val = cur.fetchone()[0]
        self.assertEqual(type(val), str)
        self.assertEqual(val, "foo")

    def CheckFuncReturnUnicode(self):
        cur = self.con.cursor()
        cur.execute("select returnunicode()")
        val = cur.fetchone()[0]
        self.assertEqual(type(val), str)
        self.assertEqual(val, "bar")

    def CheckFuncReturnInt(self):
        cur = self.con.cursor()
        cur.execute("select returnint()")
        val = cur.fetchone()[0]
        self.assertEqual(type(val), int)
        self.assertEqual(val, 42)

    def CheckFuncReturnFloat(self):
        cur = self.con.cursor()
        cur.execute("select returnfloat()")
        val = cur.fetchone()[0]
        self.assertEqual(type(val), float)
        je偶eli val < 3.139 albo val > 3.141:
            self.fail("wrong value")

    def CheckFuncReturnNull(self):
        cur = self.con.cursor()
        cur.execute("select returnnull()")
        val = cur.fetchone()[0]
        self.assertEqual(type(val), type(Nic))
        self.assertEqual(val, Nic)

    def CheckFuncReturnBlob(self):
        cur = self.con.cursor()
        cur.execute("select returnblob()")
        val = cur.fetchone()[0]
        self.assertEqual(type(val), bytes)
        self.assertEqual(val, b"blob")

    def CheckFuncReturnLongLong(self):
        cur = self.con.cursor()
        cur.execute("select returnlonglong()")
        val = cur.fetchone()[0]
        self.assertEqual(val, 1<<31)

    def CheckFuncException(self):
        cur = self.con.cursor()
        spr贸buj:
            cur.execute("select podnie艣exception()")
            cur.fetchone()
            self.fail("should have podnie艣d OperationalError")
        wyj膮wszy sqlite.OperationalError jako e:
            self.assertEqual(e.args[0], 'user-defined function podnie艣d exception')

    def CheckParamString(self):
        cur = self.con.cursor()
        cur.execute("select isstring(?)", ("foo",))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    def CheckParamInt(self):
        cur = self.con.cursor()
        cur.execute("select isint(?)", (42,))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    def CheckParamFloat(self):
        cur = self.con.cursor()
        cur.execute("select isfloat(?)", (3.14,))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    def CheckParamNic(self):
        cur = self.con.cursor()
        cur.execute("select isnone(?)", (Nic,))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    def CheckParamBlob(self):
        cur = self.con.cursor()
        cur.execute("select isblob(?)", (memoryview(b"blob"),))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    def CheckParamLongLong(self):
        cur = self.con.cursor()
        cur.execute("select islonglong(?)", (1<<42,))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

klasa AggregateTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite.connect(":memory:")
        cur = self.con.cursor()
        cur.execute("""
            create table test(
                t text,
                i integer,
                f float,
                n,
                b blob
                )
            """)
        cur.execute("insert into test(t, i, f, n, b) values (?, ?, ?, ?, ?)",
            ("foo", 5, 3.14, Nic, memoryview(b"blob"),))

        self.con.create_aggregate("nostep", 1, AggrNoStep)
        self.con.create_aggregate("nofinalize", 1, AggrNoFinalize)
        self.con.create_aggregate("excInit", 1, AggrExceptionInInit)
        self.con.create_aggregate("excStep", 1, AggrExceptionInStep)
        self.con.create_aggregate("excFinalize", 1, AggrExceptionInFinalize)
        self.con.create_aggregate("checkType", 2, AggrCheckType)
        self.con.create_aggregate("mysum", 1, AggrSum)

    def tearDown(self):
        #self.cur.close()
        #self.con.close()
        dalej

    def CheckAggrErrorOnCreate(self):
        spr贸buj:
            self.con.create_function("bla", -100, AggrSum)
            self.fail("should have podnie艣d an OperationalError")
        wyj膮wszy sqlite.OperationalError:
            dalej

    def CheckAggrNoStep(self):
        cur = self.con.cursor()
        spr贸buj:
            cur.execute("select nostep(t) z test")
            self.fail("should have podnie艣d an AttributeError")
        wyj膮wszy AttributeError jako e:
            self.assertEqual(e.args[0], "'AggrNoStep' object has no attribute 'step'")

    def CheckAggrNoFinalize(self):
        cur = self.con.cursor()
        spr贸buj:
            cur.execute("select nofinalize(t) z test")
            val = cur.fetchone()[0]
            self.fail("should have podnie艣d an OperationalError")
        wyj膮wszy sqlite.OperationalError jako e:
            self.assertEqual(e.args[0], "user-defined aggregate's 'finalize' method podnie艣d error")

    def CheckAggrExceptionInInit(self):
        cur = self.con.cursor()
        spr贸buj:
            cur.execute("select excInit(t) z test")
            val = cur.fetchone()[0]
            self.fail("should have podnie艣d an OperationalError")
        wyj膮wszy sqlite.OperationalError jako e:
            self.assertEqual(e.args[0], "user-defined aggregate's '__init__' method podnie艣d error")

    def CheckAggrExceptionInStep(self):
        cur = self.con.cursor()
        spr贸buj:
            cur.execute("select excStep(t) z test")
            val = cur.fetchone()[0]
            self.fail("should have podnie艣d an OperationalError")
        wyj膮wszy sqlite.OperationalError jako e:
            self.assertEqual(e.args[0], "user-defined aggregate's 'step' method podnie艣d error")

    def CheckAggrExceptionInFinalize(self):
        cur = self.con.cursor()
        spr贸buj:
            cur.execute("select excFinalize(t) z test")
            val = cur.fetchone()[0]
            self.fail("should have podnie艣d an OperationalError")
        wyj膮wszy sqlite.OperationalError jako e:
            self.assertEqual(e.args[0], "user-defined aggregate's 'finalize' method podnie艣d error")

    def CheckAggrCheckParamStr(self):
        cur = self.con.cursor()
        cur.execute("select checkType('str', ?)", ("foo",))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    def CheckAggrCheckParamInt(self):
        cur = self.con.cursor()
        cur.execute("select checkType('int', ?)", (42,))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    def CheckAggrCheckParamFloat(self):
        cur = self.con.cursor()
        cur.execute("select checkType('float', ?)", (3.14,))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    def CheckAggrCheckParamNic(self):
        cur = self.con.cursor()
        cur.execute("select checkType('Nic', ?)", (Nic,))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    def CheckAggrCheckParamBlob(self):
        cur = self.con.cursor()
        cur.execute("select checkType('blob', ?)", (memoryview(b"blob"),))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    def CheckAggrCheckAggrSum(self):
        cur = self.con.cursor()
        cur.execute("delete z test")
        cur.executemany("insert into test(i) values (?)", [(10,), (20,), (30,)])
        cur.execute("select mysum(i) z test")
        val = cur.fetchone()[0]
        self.assertEqual(val, 60)

klasa AuthorizerTests(unittest.TestCase):
    @staticmethod
    def authorizer_cb(action, arg1, arg2, dbname, source):
        je偶eli action != sqlite.SQLITE_SELECT:
            zwr贸膰 sqlite.SQLITE_DENY
        je偶eli arg2 == 'c2' albo arg1 == 't2':
            zwr贸膰 sqlite.SQLITE_DENY
        zwr贸膰 sqlite.SQLITE_OK

    def setUp(self):
        self.con = sqlite.connect(":memory:")
        self.con.executescript("""
            create table t1 (c1, c2);
            create table t2 (c1, c2);
            insert into t1 (c1, c2) values (1, 2);
            insert into t2 (c1, c2) values (4, 5);
            """)

        # For our security test:
        self.con.execute("select c2 z t2")

        self.con.set_authorizer(self.authorizer_cb)

    def tearDown(self):
        dalej

    def test_table_access(self):
        spr贸buj:
            self.con.execute("select * z t2")
        wyj膮wszy sqlite.DatabaseError jako e:
            je偶eli nie e.args[0].endswith("prohibited"):
                self.fail("wrong exception text: %s" % e.args[0])
            zwr贸膰
        self.fail("should have podnie艣d an exception due to missing privileges")

    def test_column_access(self):
        spr贸buj:
            self.con.execute("select c2 z t1")
        wyj膮wszy sqlite.DatabaseError jako e:
            je偶eli nie e.args[0].endswith("prohibited"):
                self.fail("wrong exception text: %s" % e.args[0])
            zwr贸膰
        self.fail("should have podnie艣d an exception due to missing privileges")

klasa AuthorizerRaiseExceptionTests(AuthorizerTests):
    @staticmethod
    def authorizer_cb(action, arg1, arg2, dbname, source):
        je偶eli action != sqlite.SQLITE_SELECT:
            podnie艣 ValueError
        je偶eli arg2 == 'c2' albo arg1 == 't2':
            podnie艣 ValueError
        zwr贸膰 sqlite.SQLITE_OK

klasa AuthorizerIllegalTypeTests(AuthorizerTests):
    @staticmethod
    def authorizer_cb(action, arg1, arg2, dbname, source):
        je偶eli action != sqlite.SQLITE_SELECT:
            zwr贸膰 0.0
        je偶eli arg2 == 'c2' albo arg1 == 't2':
            zwr贸膰 0.0
        zwr贸膰 sqlite.SQLITE_OK

klasa AuthorizerLargeIntegerTests(AuthorizerTests):
    @staticmethod
    def authorizer_cb(action, arg1, arg2, dbname, source):
        je偶eli action != sqlite.SQLITE_SELECT:
            zwr贸膰 2**32
        je偶eli arg2 == 'c2' albo arg1 == 't2':
            zwr贸膰 2**32
        zwr贸膰 sqlite.SQLITE_OK


def suite():
    function_suite = unittest.makeSuite(FunctionTests, "Check")
    aggregate_suite = unittest.makeSuite(AggregateTests, "Check")
    authorizer_suite = unittest.makeSuite(AuthorizerTests)
    zwr贸膰 unittest.TestSuite((
            function_suite,
            aggregate_suite,
            authorizer_suite,
            unittest.makeSuite(AuthorizerRaiseExceptionTests),
            unittest.makeSuite(AuthorizerIllegalTypeTests),
            unittest.makeSuite(AuthorizerLargeIntegerTests),
        ))

def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())

je偶eli __name__ == "__main__":
    test()
