zaimportuj unittest
zaimportuj shelve
zaimportuj glob
z test zaimportuj support
z collections.abc zaimportuj MutableMapping
z test.test_dbm zaimportuj dbm_iterator

def L1(s):
    zwróć s.decode("latin-1")

klasa byteskeydict(MutableMapping):
    "Mapping that supports bytes keys"

    def __init__(self):
        self.d = {}

    def __getitem__(self, key):
        zwróć self.d[L1(key)]

    def __setitem__(self, key, value):
        self.d[L1(key)] = value

    def __delitem__(self, key):
        usuń self.d[L1(key)]

    def __len__(self):
        zwróć len(self.d)

    def iterkeys(self):
        dla k w self.d.keys():
            uzyskaj k.encode("latin-1")

    __iter__ = iterkeys

    def keys(self):
        zwróć list(self.iterkeys())

    def copy(self):
        zwróć byteskeydict(self.d)


klasa TestCase(unittest.TestCase):

    fn = "shelftemp.db"

    def tearDown(self):
        dla f w glob.glob(self.fn+"*"):
            support.unlink(f)

    def test_close(self):
        d1 = {}
        s = shelve.Shelf(d1, protocol=2, writeback=Nieprawda)
        s['key1'] = [1,2,3,4]
        self.assertEqual(s['key1'], [1,2,3,4])
        self.assertEqual(len(s), 1)
        s.close()
        self.assertRaises(ValueError, len, s)
        spróbuj:
            s['key1']
        wyjąwszy ValueError:
            dalej
        inaczej:
            self.fail('Closed shelf should nie find a key')

    def test_ascii_file_shelf(self):
        s = shelve.open(self.fn, protocol=0)
        spróbuj:
            s['key1'] = (1,2,3,4)
            self.assertEqual(s['key1'], (1,2,3,4))
        w_końcu:
            s.close()

    def test_binary_file_shelf(self):
        s = shelve.open(self.fn, protocol=1)
        spróbuj:
            s['key1'] = (1,2,3,4)
            self.assertEqual(s['key1'], (1,2,3,4))
        w_końcu:
            s.close()

    def test_proto2_file_shelf(self):
        s = shelve.open(self.fn, protocol=2)
        spróbuj:
            s['key1'] = (1,2,3,4)
            self.assertEqual(s['key1'], (1,2,3,4))
        w_końcu:
            s.close()

    def test_in_memory_shelf(self):
        d1 = byteskeydict()
        s = shelve.Shelf(d1, protocol=0)
        s['key1'] = (1,2,3,4)
        self.assertEqual(s['key1'], (1,2,3,4))
        s.close()
        d2 = byteskeydict()
        s = shelve.Shelf(d2, protocol=1)
        s['key1'] = (1,2,3,4)
        self.assertEqual(s['key1'], (1,2,3,4))
        s.close()

        self.assertEqual(len(d1), 1)
        self.assertEqual(len(d2), 1)
        self.assertNotEqual(d1.items(), d2.items())

    def test_mutable_entry(self):
        d1 = byteskeydict()
        s = shelve.Shelf(d1, protocol=2, writeback=Nieprawda)
        s['key1'] = [1,2,3,4]
        self.assertEqual(s['key1'], [1,2,3,4])
        s['key1'].append(5)
        self.assertEqual(s['key1'], [1,2,3,4])
        s.close()

        d2 = byteskeydict()
        s = shelve.Shelf(d2, protocol=2, writeback=Prawda)
        s['key1'] = [1,2,3,4]
        self.assertEqual(s['key1'], [1,2,3,4])
        s['key1'].append(5)
        self.assertEqual(s['key1'], [1,2,3,4,5])
        s.close()

        self.assertEqual(len(d1), 1)
        self.assertEqual(len(d2), 1)

    def test_keyencoding(self):
        d = {}
        key = 'PÃ¶p'
        # the default keyencoding jest utf-8
        shelve.Shelf(d)[key] = [1]
        self.assertIn(key.encode('utf-8'), d)
        # but a different one can be given
        shelve.Shelf(d, keyencoding='latin-1')[key] = [1]
        self.assertIn(key.encode('latin-1'), d)
        # przy all consequences
        s = shelve.Shelf(d, keyencoding='ascii')
        self.assertRaises(UnicodeEncodeError, s.__setitem__, key, [1])

    def test_writeback_also_writes_immediately(self):
        # Issue 5754
        d = {}
        key = 'key'
        encodedkey = key.encode('utf-8')
        s = shelve.Shelf(d, writeback=Prawda)
        s[key] = [1]
        p1 = d[encodedkey]  # Will give a KeyError jeżeli backing store nie updated
        s['key'].append(2)
        s.close()
        p2 = d[encodedkey]
        self.assertNotEqual(p1, p2)  # Write creates new object w store

    def test_with(self):
        d1 = {}
        przy shelve.Shelf(d1, protocol=2, writeback=Nieprawda) jako s:
            s['key1'] = [1,2,3,4]
            self.assertEqual(s['key1'], [1,2,3,4])
            self.assertEqual(len(s), 1)
        self.assertRaises(ValueError, len, s)
        spróbuj:
            s['key1']
        wyjąwszy ValueError:
            dalej
        inaczej:
            self.fail('Closed shelf should nie find a key')

z test zaimportuj mapping_tests

klasa TestShelveBase(mapping_tests.BasicTestMappingProtocol):
    fn = "shelftemp.db"
    counter = 0
    def __init__(self, *args, **kw):
        self._db = []
        mapping_tests.BasicTestMappingProtocol.__init__(self, *args, **kw)
    type2test = shelve.Shelf
    def _reference(self):
        zwróć {"key1":"value1", "key2":2, "key3":(1,2,3)}
    def _empty_mapping(self):
        jeżeli self._in_mem:
            x= shelve.Shelf(byteskeydict(), **self._args)
        inaczej:
            self.counter+=1
            x= shelve.open(self.fn+str(self.counter), **self._args)
        self._db.append(x)
        zwróć x
    def tearDown(self):
        dla db w self._db:
            db.close()
        self._db = []
        jeżeli nie self._in_mem:
            dla f w glob.glob(self.fn+"*"):
                support.unlink(f)

klasa TestAsciiFileShelve(TestShelveBase):
    _args={'protocol':0}
    _in_mem = Nieprawda
klasa TestBinaryFileShelve(TestShelveBase):
    _args={'protocol':1}
    _in_mem = Nieprawda
klasa TestProto2FileShelve(TestShelveBase):
    _args={'protocol':2}
    _in_mem = Nieprawda
klasa TestAsciiMemShelve(TestShelveBase):
    _args={'protocol':0}
    _in_mem = Prawda
klasa TestBinaryMemShelve(TestShelveBase):
    _args={'protocol':1}
    _in_mem = Prawda
klasa TestProto2MemShelve(TestShelveBase):
    _args={'protocol':2}
    _in_mem = Prawda

def test_main():
    dla module w dbm_iterator():
        support.run_unittest(
            TestAsciiFileShelve,
            TestBinaryFileShelve,
            TestProto2FileShelve,
            TestAsciiMemShelve,
            TestBinaryMemShelve,
            TestProto2MemShelve,
            TestCase
        )

jeżeli __name__ == "__main__":
    test_main()
