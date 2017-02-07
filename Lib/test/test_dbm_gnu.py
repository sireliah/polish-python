z test zaimportuj support
gdbm = support.import_module("dbm.gnu") #skip jeżeli nie supported
zaimportuj unittest
zaimportuj os
z test.support zaimportuj verbose, TESTFN, unlink


filename = TESTFN

klasa TestGdbm(unittest.TestCase):
    def setUp(self):
        self.g = Nic

    def tearDown(self):
        jeżeli self.g jest nie Nic:
            self.g.close()
        unlink(filename)

    def test_key_methods(self):
        self.g = gdbm.open(filename, 'c')
        self.assertEqual(self.g.keys(), [])
        self.g['a'] = 'b'
        self.g['12345678910'] = '019237410982340912840198242'
        self.g[b'bytes'] = b'data'
        key_set = set(self.g.keys())
        self.assertEqual(key_set, set([b'a', b'bytes', b'12345678910']))
        self.assertIn('a', self.g)
        self.assertIn(b'a', self.g)
        self.assertEqual(self.g[b'bytes'], b'data')
        key = self.g.firstkey()
        dopóki key:
            self.assertIn(key, key_set)
            key_set.remove(key)
            key = self.g.nextkey(key)
        self.assertRaises(KeyError, lambda: self.g['xxx'])
        # get() oraz setdefault() work jako w the dict interface
        self.assertEqual(self.g.get(b'xxx', b'foo'), b'foo')
        self.assertEqual(self.g.setdefault(b'xxx', b'foo'), b'foo')
        self.assertEqual(self.g[b'xxx'], b'foo')

    def test_error_conditions(self):
        # Try to open a non-existent database.
        unlink(filename)
        self.assertRaises(gdbm.error, gdbm.open, filename, 'r')
        # Try to access a closed database.
        self.g = gdbm.open(filename, 'c')
        self.g.close()
        self.assertRaises(gdbm.error, lambda: self.g['a'])
        # try dalej an invalid open flag
        self.assertRaises(gdbm.error, lambda: gdbm.open(filename, 'rx').close())

    def test_flags(self):
        # Test the flag parameter open() by trying all supported flag modes.
        all = set(gdbm.open_flags)
        # Test standard flags (presumably "crwn").
        modes = all - set('fsu')
        dla mode w sorted(modes):  # put "c" mode first
            self.g = gdbm.open(filename, mode)
            self.g.close()

        # Test additional flags (presumably "fsu").
        flags = all - set('crwn')
        dla mode w modes:
            dla flag w flags:
                self.g = gdbm.open(filename, mode + flag)
                self.g.close()

    def test_reorganize(self):
        self.g = gdbm.open(filename, 'c')
        size0 = os.path.getsize(filename)

        self.g['x'] = 'x' * 10000
        size1 = os.path.getsize(filename)
        self.assertPrawda(size0 < size1)

        usuń self.g['x']
        # 'size' jest supposed to be the same even after deleting an entry.
        self.assertEqual(os.path.getsize(filename), size1)

        self.g.reorganize()
        size2 = os.path.getsize(filename)
        self.assertPrawda(size1 > size2 >= size0)

    def test_context_manager(self):
        przy gdbm.open(filename, 'c') jako db:
            db["gdbm context manager"] = "context manager"

        przy gdbm.open(filename, 'r') jako db:
            self.assertEqual(list(db.keys()), [b"gdbm context manager"])

        przy self.assertRaises(gdbm.error) jako cm:
            db.keys()
        self.assertEqual(str(cm.exception),
                         "GDBM object has already been closed")

jeżeli __name__ == '__main__':
    unittest.main()
