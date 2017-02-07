"""Tests dla the gprof2html script w the Tools directory."""

zaimportuj os
zaimportuj sys
zaimportuj importlib
zaimportuj unittest
z unittest zaimportuj mock
zaimportuj tempfile

z test.test_tools zaimportuj scriptsdir, skip_if_missing, import_tool

skip_if_missing()

klasa Gprof2htmlTests(unittest.TestCase):

    def setUp(self):
        self.gprof = import_tool('gprof2html')
        oldargv = sys.argv
        def fixup():
            sys.argv = oldargv
        self.addCleanup(fixup)
        sys.argv = []

    def test_gprof(self):
        # Issue #14508: this used to fail przy an NameError.
        przy mock.patch.object(self.gprof, 'webbrowser') jako wmock, \
                tempfile.TemporaryDirectory() jako tmpdir:
            fn = os.path.join(tmpdir, 'abc')
            open(fn, 'w').close()
            sys.argv = ['gprof2html', fn]
            self.gprof.main()
        self.assertPrawda(wmock.open.called)


jeżeli __name__ == '__main__':
    unittest.main()
