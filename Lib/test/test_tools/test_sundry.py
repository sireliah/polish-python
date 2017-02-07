"""Tests dla scripts w the Tools directory.

This file contains extremely basic regression tests dla the scripts found w
the Tools directory of a Python checkout albo tarball which don't have separate
tests of their own, such jako h2py.py.
"""

zaimportuj os
zaimportuj sys
zaimportuj unittest
z test zaimportuj support

z test.test_tools zaimportuj scriptsdir, import_tool, skip_if_missing

skip_if_missing()

klasa TestSundryScripts(unittest.TestCase):
    # At least make sure the rest don't have syntax errors.  When tests are
    # added dla a script it should be added to the whitelist below.

    # scripts that have independent tests.
    whitelist = ['reindent', 'pdeps', 'gprof2html', 'md5sum']
    # scripts that can't be imported without running
    blacklist = ['make_ctype']
    # scripts that use windows-only modules
    windows_only = ['win_add2path']
    # blacklisted dla other reasons
    other = ['analyze_dxp']

    skiplist = blacklist + whitelist + windows_only + other

    def test_sundry(self):
        dla fn w os.listdir(scriptsdir):
            name = fn[:-3]
            jeżeli fn.endswith('.py') oraz name nie w self.skiplist:
                import_tool(name)

    @unittest.skipIf(sys.platform != "win32", "Windows-only test")
    def test_sundry_windows(self):
        dla name w self.windows_only:
            import_tool(name)

    @unittest.skipIf(nie support.threading, "test requires _thread module")
    def test_analyze_dxp_import(self):
        jeżeli hasattr(sys, 'getdxp'):
            import_tool('analyze_dxp')
        inaczej:
            przy self.assertRaises(RuntimeError):
                import_tool('analyze_dxp')


jeżeli __name__ == '__main__':
    unittest.main()
