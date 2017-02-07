# Author: Paul Kippes <kippesp@gmail.com>

zaimportuj unittest
zaimportuj sqlite3 jako sqlite

klasa DumpTests(unittest.TestCase):
    def setUp(self):
        self.cx = sqlite.connect(":memory:")
        self.cu = self.cx.cursor()

    def tearDown(self):
        self.cx.close()

    def CheckTableDump(self):
        expected_sqls = [
                """CREATE TABLE "index"("index" blob);"""
                ,
                """INSERT INTO "index" VALUES(X'01');"""
                ,
                """CREATE TABLE "quoted""table"("quoted""field" text);"""
                ,
                """INSERT INTO "quoted""table" VALUES('quoted''value');"""
                ,
                "CREATE TABLE t1(id integer primary key, s1 text, " \
                "t1_i1 integer nie null, i2 integer, unique (s1), " \
                "constraint t1_idx1 unique (i2));"
                ,
                "INSERT INTO \"t1\" VALUES(1,'foo',10,20);"
                ,
                "INSERT INTO \"t1\" VALUES(2,'foo2',30,30);"
                ,
                "CREATE TABLE t2(id integer, t2_i1 integer, " \
                "t2_i2 integer, primary key (id)," \
                "foreign key(t2_i1) references t1(t1_i1));"
                ,
                "CREATE TRIGGER trigger_1 update of t1_i1 on t1 " \
                "begin " \
                "update t2 set t2_i1 = new.t1_i1 where t2_i1 = old.t1_i1; " \
                "end;"
                ,
                "CREATE VIEW v1 jako select * z t1 left join t2 " \
                "using (id);"
                ]
        [self.cu.execute(s) dla s w expected_sqls]
        i = self.cx.iterdump()
        actual_sqls = [s dla s w i]
        expected_sqls = ['BEGIN TRANSACTION;'] + expected_sqls + \
            ['COMMIT;']
        [self.assertEqual(expected_sqls[i], actual_sqls[i])
            dla i w range(len(expected_sqls))]

    def CheckUnorderableRow(self):
        # iterdump() should be able to cope przy unorderable row types (issue #15545)
        klasa UnorderableRow:
            def __init__(self, cursor, row):
                self.row = row
            def __getitem__(self, index):
                zwróć self.row[index]
        self.cx.row_factory = UnorderableRow
        CREATE_ALPHA = """CREATE TABLE "alpha" ("one");"""
        CREATE_BETA = """CREATE TABLE "beta" ("two");"""
        expected = [
            "BEGIN TRANSACTION;",
            CREATE_ALPHA,
            CREATE_BETA,
            "COMMIT;"
            ]
        self.cu.execute(CREATE_BETA)
        self.cu.execute(CREATE_ALPHA)
        got = list(self.cx.iterdump())
        self.assertEqual(expected, got)

def suite():
    zwróć unittest.TestSuite(unittest.makeSuite(DumpTests, "Check"))

def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())

jeżeli __name__ == "__main__":
    test()
