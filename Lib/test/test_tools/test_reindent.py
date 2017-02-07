"""Tests dla scripts w the Tools directory.

This file contains regression tests dla some of the scripts found w the
Tools directory of a Python checkout albo tarball, such jako reindent.py.
"""

zaimportuj os
zaimportuj unittest
z test.support.script_helper zaimportuj assert_python_ok

z test.test_tools zaimportuj scriptsdir, skip_if_missing

skip_if_missing()

klasa ReindentTests(unittest.TestCase):
    script = os.path.join(scriptsdir, 'reindent.py')

    def test_noargs(self):
        assert_python_ok(self.script)

    def test_help(self):
        rc, out, err = assert_python_ok(self.script, '-h')
        self.assertEqual(out, b'')
        self.assertGreater(err, b'')


jeżeli __name__ == '__main__':
    unittest.main()
