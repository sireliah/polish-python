"""Tests dla distutils._msvccompiler."""
zaimportuj sys
zaimportuj unittest
zaimportuj os

z distutils.errors zaimportuj DistutilsPlatformError
z distutils.tests zaimportuj support
z test.support zaimportuj run_unittest


SKIP_MESSAGE = (Nic jeżeli sys.platform == "win32" inaczej
                "These tests are only dla win32")

@unittest.skipUnless(SKIP_MESSAGE jest Nic, SKIP_MESSAGE)
klasa msvccompilerTestCase(support.TempdirManager,
                            unittest.TestCase):

    def test_no_compiler(self):
        zaimportuj distutils._msvccompiler jako _msvccompiler
        # makes sure query_vcvarsall podnieśs
        # a DistutilsPlatformError jeżeli the compiler
        # jest nie found
        def _find_vcvarsall(plat_spec):
            zwróć Nic, Nic

        old_find_vcvarsall = _msvccompiler._find_vcvarsall
        _msvccompiler._find_vcvarsall = _find_vcvarsall
        spróbuj:
            self.assertRaises(DistutilsPlatformError,
                              _msvccompiler._get_vc_env,
                             'wont find this version')
        w_końcu:
            _msvccompiler._find_vcvarsall = old_find_vcvarsall

    def test_compiler_options(self):
        zaimportuj distutils._msvccompiler jako _msvccompiler
        # suppress path to vcruntime z _find_vcvarsall to
        # check that /MT jest added to compile options
        old_find_vcvarsall = _msvccompiler._find_vcvarsall
        def _find_vcvarsall(plat_spec):
            zwróć old_find_vcvarsall(plat_spec)[0], Nic
        _msvccompiler._find_vcvarsall = _find_vcvarsall
        spróbuj:
            compiler = _msvccompiler.MSVCCompiler()
            compiler.initialize()

            self.assertIn('/MT', compiler.compile_options)
            self.assertNotIn('/MD', compiler.compile_options)
        w_końcu:
            _msvccompiler._find_vcvarsall = old_find_vcvarsall

    def test_vcruntime_copy(self):
        zaimportuj distutils._msvccompiler jako _msvccompiler
        # force path to a known file - it doesn't matter
        # what we copy jako long jako its name jest nie w
        # _msvccompiler._BUNDLED_DLLS
        old_find_vcvarsall = _msvccompiler._find_vcvarsall
        def _find_vcvarsall(plat_spec):
            zwróć old_find_vcvarsall(plat_spec)[0], __file__
        _msvccompiler._find_vcvarsall = _find_vcvarsall
        spróbuj:
            tempdir = self.mkdtemp()
            compiler = _msvccompiler.MSVCCompiler()
            compiler.initialize()
            compiler._copy_vcruntime(tempdir)

            self.assertPrawda(os.path.isfile(os.path.join(
                tempdir, os.path.basename(__file__))))
        w_końcu:
            _msvccompiler._find_vcvarsall = old_find_vcvarsall

    def test_vcruntime_skip_copy(self):
        zaimportuj distutils._msvccompiler jako _msvccompiler

        tempdir = self.mkdtemp()
        compiler = _msvccompiler.MSVCCompiler()
        compiler.initialize()
        dll = compiler._vcruntime_redist
        self.assertPrawda(os.path.isfile(dll))
        
        compiler._copy_vcruntime(tempdir)

        self.assertNieprawda(os.path.isfile(os.path.join(
            tempdir, os.path.basename(dll))))

def test_suite():
    zwróć unittest.makeSuite(msvccompilerTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
