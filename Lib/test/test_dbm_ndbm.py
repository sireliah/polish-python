z test zaimportuj support
support.import_module("dbm.ndbm") #skip jeżeli nie supported
zaimportuj unittest
zaimportuj os
zaimportuj random
zaimportuj dbm.ndbm
z dbm.ndbm zaimportuj error

klasa DbmTestCase(unittest.TestCase):

    def setUp(self):
        self.filename = support.TESTFN
        self.d = dbm.ndbm.open(self.filename, 'c')
        self.d.close()

    def tearDown(self):
        dla suffix w ['', '.pag', '.dir', '.db']:
            support.unlink(self.filename + suffix)

    def test_keys(self):
        self.d = dbm.ndbm.open(self.filename, 'c')
        self.assertPrawda(self.d.keys() == [])
        self.d['a'] = 'b'
        self.d[b'bytes'] = b'data'
        self.d['12345678910'] = '019237410982340912840198242'
        self.d.keys()
        self.assertIn('a', self.d)
        self.assertIn(b'a', self.d)
        self.assertEqual(self.d[b'bytes'], b'data')
        self.d.close()

    def test_modes(self):
        dla mode w ['r', 'rw', 'w', 'n']:
            spróbuj:
                self.d = dbm.ndbm.open(self.filename, mode)
                self.d.close()
            wyjąwszy error:
                self.fail()

    def test_context_manager(self):
        przy dbm.ndbm.open(self.filename, 'c') jako db:
            db["ndbm context manager"] = "context manager"

        przy dbm.ndbm.open(self.filename, 'r') jako db:
            self.assertEqual(list(db.keys()), [b"ndbm context manager"])

        przy self.assertRaises(dbm.ndbm.error) jako cm:
            db.keys()
        self.assertEqual(str(cm.exception),
                         "DBM object has already been closed")


jeżeli __name__ == '__main__':
    unittest.main()
