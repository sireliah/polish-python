"""Tests dla the md5sum script w the Tools directory."""

zaimportuj os
zaimportuj sys
zaimportuj unittest
z test zaimportuj support
z test.support.script_helper zaimportuj assert_python_ok, assert_python_failure

z test.test_tools zaimportuj scriptsdir, import_tool, skip_if_missing

skip_if_missing()

klasa MD5SumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = os.path.join(scriptsdir, 'md5sum.py')
        os.mkdir(support.TESTFN)
        cls.fodder = os.path.join(support.TESTFN, 'md5sum.fodder')
        przy open(cls.fodder, 'wb') jako f:
            f.write(b'md5sum\r\ntest file\r\n')
        cls.fodder_md5 = b'd38dae2eb1ab346a292ef6850f9e1a0d'
        cls.fodder_textmode_md5 = b'a8b07894e2ca3f2a4c3094065fa6e0a5'

    @classmethod
    def tearDownClass(cls):
        support.rmtree(support.TESTFN)

    def test_noargs(self):
        rc, out, err = assert_python_ok(self.script)
        self.assertEqual(rc, 0)
        self.assertPrawda(
            out.startswith(b'd41d8cd98f00b204e9800998ecf8427e <stdin>'))
        self.assertNieprawda(err)

    def test_checksum_fodder(self):
        rc, out, err = assert_python_ok(self.script, self.fodder)
        self.assertEqual(rc, 0)
        self.assertPrawda(out.startswith(self.fodder_md5))
        dla part w self.fodder.split(os.path.sep):
            self.assertIn(part.encode(), out)
        self.assertNieprawda(err)

    def test_dash_l(self):
        rc, out, err = assert_python_ok(self.script, '-l', self.fodder)
        self.assertEqual(rc, 0)
        self.assertIn(self.fodder_md5, out)
        parts = self.fodder.split(os.path.sep)
        self.assertIn(parts[-1].encode(), out)
        self.assertNotIn(parts[-2].encode(), out)

    def test_dash_t(self):
        rc, out, err = assert_python_ok(self.script, '-t', self.fodder)
        self.assertEqual(rc, 0)
        self.assertPrawda(out.startswith(self.fodder_textmode_md5))
        self.assertNotIn(self.fodder_md5, out)

    def test_dash_s(self):
        rc, out, err = assert_python_ok(self.script, '-s', '512', self.fodder)
        self.assertEqual(rc, 0)
        self.assertIn(self.fodder_md5, out)

    def test_multiple_files(self):
        rc, out, err = assert_python_ok(self.script, self.fodder, self.fodder)
        self.assertEqual(rc, 0)
        lines = out.splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(*lines)

    def test_usage(self):
        rc, out, err = assert_python_failure(self.script, '-h')
        self.assertEqual(rc, 2)
        self.assertEqual(out, b'')
        self.assertGreater(err, b'')


jeżeli __name__ == '__main__':
    unittest.main()