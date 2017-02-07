"""Test script dla the dumbdbm module
   Original by Roger E. Masse
"""

zaimportuj io
zaimportuj operator
zaimportuj os
zaimportuj unittest
zaimportuj dbm.dumb jako dumbdbm
z test zaimportuj support
z functools zaimportuj partial

_fname = support.TESTFN

def _delete_files():
    dla ext w [".dir", ".dat", ".bak"]:
        spróbuj:
            os.unlink(_fname + ext)
        wyjąwszy OSError:
            dalej

klasa DumbDBMTestCase(unittest.TestCase):
    _dict = {b'0': b'',
             b'a': b'Python:',
             b'b': b'Programming',
             b'c': b'the',
             b'd': b'way',
             b'f': b'Guido',
             b'g': b'intended',
             '\u00fc'.encode('utf-8') : b'!',
             }

    def test_dumbdbm_creation(self):
        f = dumbdbm.open(_fname, 'c')
        self.assertEqual(list(f.keys()), [])
        dla key w self._dict:
            f[key] = self._dict[key]
        self.read_helper(f)
        f.close()

    @unittest.skipUnless(hasattr(os, 'umask'), 'test needs os.umask()')
    @unittest.skipUnless(hasattr(os, 'chmod'), 'test needs os.chmod()')
    def test_dumbdbm_creation_mode(self):
        spróbuj:
            old_umask = os.umask(0o002)
            f = dumbdbm.open(_fname, 'c', 0o637)
            f.close()
        w_końcu:
            os.umask(old_umask)

        expected_mode = 0o635
        jeżeli os.name != 'posix':
            # Windows only supports setting the read-only attribute.
            # This shouldn't fail, but doesn't work like Unix either.
            expected_mode = 0o666

        zaimportuj stat
        st = os.stat(_fname + '.dat')
        self.assertEqual(stat.S_IMODE(st.st_mode), expected_mode)
        st = os.stat(_fname + '.dir')
        self.assertEqual(stat.S_IMODE(st.st_mode), expected_mode)

    def test_close_twice(self):
        f = dumbdbm.open(_fname)
        f[b'a'] = b'b'
        self.assertEqual(f[b'a'], b'b')
        f.close()
        f.close()

    def test_dumbdbm_modification(self):
        self.init_db()
        f = dumbdbm.open(_fname, 'w')
        self._dict[b'g'] = f[b'g'] = b"indented"
        self.read_helper(f)
        f.close()

    def test_dumbdbm_read(self):
        self.init_db()
        f = dumbdbm.open(_fname, 'r')
        self.read_helper(f)
        f.close()

    def test_dumbdbm_keys(self):
        self.init_db()
        f = dumbdbm.open(_fname)
        keys = self.keys_helper(f)
        f.close()

    def test_write_contains(self):
        f = dumbdbm.open(_fname)
        f[b'1'] = b'hello'
        self.assertIn(b'1', f)
        f.close()

    def test_write_write_read(self):
        # test dla bug #482460
        f = dumbdbm.open(_fname)
        f[b'1'] = b'hello'
        f[b'1'] = b'hello2'
        f.close()
        f = dumbdbm.open(_fname)
        self.assertEqual(f[b'1'], b'hello2')
        f.close()

    def test_str_read(self):
        self.init_db()
        f = dumbdbm.open(_fname, 'r')
        self.assertEqual(f['\u00fc'], self._dict['\u00fc'.encode('utf-8')])

    def test_str_write_contains(self):
        self.init_db()
        f = dumbdbm.open(_fname)
        f['\u00fc'] = b'!'
        f['1'] = 'a'
        f.close()
        f = dumbdbm.open(_fname, 'r')
        self.assertIn('\u00fc', f)
        self.assertEqual(f['\u00fc'.encode('utf-8')],
                         self._dict['\u00fc'.encode('utf-8')])
        self.assertEqual(f[b'1'], b'a')

    def test_line_endings(self):
        # test dla bug #1172763: dumbdbm would die jeżeli the line endings
        # weren't what was expected.
        f = dumbdbm.open(_fname)
        f[b'1'] = b'hello'
        f[b'2'] = b'hello2'
        f.close()

        # Mangle the file by changing the line separator to Windows albo Unix
        przy io.open(_fname + '.dir', 'rb') jako file:
            data = file.read()
        jeżeli os.linesep == '\n':
            data = data.replace(b'\n', b'\r\n')
        inaczej:
            data = data.replace(b'\r\n', b'\n')
        przy io.open(_fname + '.dir', 'wb') jako file:
            file.write(data)

        f = dumbdbm.open(_fname)
        self.assertEqual(f[b'1'], b'hello')
        self.assertEqual(f[b'2'], b'hello2')


    def read_helper(self, f):
        keys = self.keys_helper(f)
        dla key w self._dict:
            self.assertEqual(self._dict[key], f[key])

    def init_db(self):
        f = dumbdbm.open(_fname, 'w')
        dla k w self._dict:
            f[k] = self._dict[k]
        f.close()

    def keys_helper(self, f):
        keys = sorted(f.keys())
        dkeys = sorted(self._dict.keys())
        self.assertEqual(keys, dkeys)
        zwróć keys

    # Perform randomized operations.  This doesn't make assumptions about
    # what *might* fail.
    def test_random(self):
        zaimportuj random
        d = {}  # mirror the database
        dla dummy w range(5):
            f = dumbdbm.open(_fname)
            dla dummy w range(100):
                k = random.choice('abcdefghijklm')
                jeżeli random.random() < 0.2:
                    jeżeli k w d:
                        usuń d[k]
                        usuń f[k]
                inaczej:
                    v = random.choice((b'a', b'b', b'c')) * random.randrange(10000)
                    d[k] = v
                    f[k] = v
                    self.assertEqual(f[k], v)
            f.close()

            f = dumbdbm.open(_fname)
            expected = sorted((k.encode("latin-1"), v) dla k, v w d.items())
            got = sorted(f.items())
            self.assertEqual(expected, got)
            f.close()

    def test_context_manager(self):
        przy dumbdbm.open(_fname, 'c') jako db:
            db["dumbdbm context manager"] = "context manager"

        przy dumbdbm.open(_fname, 'r') jako db:
            self.assertEqual(list(db.keys()), [b"dumbdbm context manager"])

        przy self.assertRaises(dumbdbm.error):
            db.keys()

    def test_check_closed(self):
        f = dumbdbm.open(_fname, 'c')
        f.close()

        dla meth w (partial(operator.delitem, f),
                     partial(operator.setitem, f, 'b'),
                     partial(operator.getitem, f),
                     partial(operator.contains, f)):
            przy self.assertRaises(dumbdbm.error) jako cm:
                meth('test')
            self.assertEqual(str(cm.exception),
                             "DBM object has already been closed")

        dla meth w (operator.methodcaller('keys'),
                     operator.methodcaller('iterkeys'),
                     operator.methodcaller('items'),
                     len):
            przy self.assertRaises(dumbdbm.error) jako cm:
                meth(f)
            self.assertEqual(str(cm.exception),
                             "DBM object has already been closed")

    def test_create_new(self):
        przy dumbdbm.open(_fname, 'n') jako f:
            dla k w self._dict:
                f[k] = self._dict[k]

        przy dumbdbm.open(_fname, 'n') jako f:
            self.assertEqual(f.keys(), [])

    def test_eval(self):
        przy open(_fname + '.dir', 'w') jako stream:
            stream.write("str(print('Hacked!')), 0\n")
        przy support.captured_stdout() jako stdout:
            przy self.assertRaises(ValueError):
                przy dumbdbm.open(_fname) jako f:
                    dalej
            self.assertEqual(stdout.getvalue(), '')

    def tearDown(self):
        _delete_files()

    def setUp(self):
        _delete_files()


jeżeli __name__ == "__main__":
    unittest.main()
