"""Tests dla distutils.unixccompiler."""
zaimportuj os
zaimportuj sys
zaimportuj unittest
z test.support zaimportuj EnvironmentVarGuard, run_unittest

z distutils zaimportuj sysconfig
z distutils.unixccompiler zaimportuj UnixCCompiler

klasa UnixCCompilerTestCase(unittest.TestCase):

    def setUp(self):
        self._backup_platform = sys.platform
        self._backup_get_config_var = sysconfig.get_config_var
        klasa CompilerWrapper(UnixCCompiler):
            def rpath_foo(self):
                zwróć self.runtime_library_dir_option('/foo')
        self.cc = CompilerWrapper()

    def tearDown(self):
        sys.platform = self._backup_platform
        sysconfig.get_config_var = self._backup_get_config_var

    @unittest.skipIf(sys.platform == 'win32', "can't test on Windows")
    def test_runtime_libdir_option(self):
        # Issue#5900
        #
        # Ensure RUNPATH jest added to extension modules przy RPATH if
        # GNU ld jest used

        # darwin
        sys.platform = 'darwin'
        self.assertEqual(self.cc.rpath_foo(), '-L/foo')

        # hp-ux
        sys.platform = 'hp-ux'
        old_gcv = sysconfig.get_config_var
        def gcv(v):
            zwróć 'xxx'
        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), ['+s', '-L/foo'])

        def gcv(v):
            zwróć 'gcc'
        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), ['-Wl,+s', '-L/foo'])

        def gcv(v):
            zwróć 'g++'
        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), ['-Wl,+s', '-L/foo'])

        sysconfig.get_config_var = old_gcv

        # irix646
        sys.platform = 'irix646'
        self.assertEqual(self.cc.rpath_foo(), ['-rpath', '/foo'])

        # osf1V5
        sys.platform = 'osf1V5'
        self.assertEqual(self.cc.rpath_foo(), ['-rpath', '/foo'])

        # GCC GNULD
        sys.platform = 'bar'
        def gcv(v):
            jeżeli v == 'CC':
                zwróć 'gcc'
            albo_inaczej v == 'GNULD':
                zwróć 'yes'
        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), '-Wl,--enable-new-dtags,-R/foo')

        # GCC non-GNULD
        sys.platform = 'bar'
        def gcv(v):
            jeżeli v == 'CC':
                zwróć 'gcc'
            albo_inaczej v == 'GNULD':
                zwróć 'no'
        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), '-Wl,-R/foo')

        # GCC GNULD przy fully qualified configuration prefix
        # see #7617
        sys.platform = 'bar'
        def gcv(v):
            jeżeli v == 'CC':
                zwróć 'x86_64-pc-linux-gnu-gcc-4.4.2'
            albo_inaczej v == 'GNULD':
                zwróć 'yes'
        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), '-Wl,--enable-new-dtags,-R/foo')

        # non-GCC GNULD
        sys.platform = 'bar'
        def gcv(v):
            jeżeli v == 'CC':
                zwróć 'cc'
            albo_inaczej v == 'GNULD':
                zwróć 'yes'
        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), '-R/foo')

        # non-GCC non-GNULD
        sys.platform = 'bar'
        def gcv(v):
            jeżeli v == 'CC':
                zwróć 'cc'
            albo_inaczej v == 'GNULD':
                zwróć 'no'
        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), '-R/foo')

    @unittest.skipUnless(sys.platform == 'darwin', 'test only relevant dla OS X')
    def test_osx_cc_overrides_ldshared(self):
        # Issue #18080:
        # ensure that setting CC env variable also changes default linker
        def gcv(v):
            jeżeli v == 'LDSHARED':
                zwróć 'gcc-4.2 -bundle -undefined dynamic_lookup '
            zwróć 'gcc-4.2'
        sysconfig.get_config_var = gcv
        przy EnvironmentVarGuard() jako env:
            env['CC'] = 'my_cc'
            usuń env['LDSHARED']
            sysconfig.customize_compiler(self.cc)
        self.assertEqual(self.cc.linker_so[0], 'my_cc')

    @unittest.skipUnless(sys.platform == 'darwin', 'test only relevant dla OS X')
    def test_osx_explict_ldshared(self):
        # Issue #18080:
        # ensure that setting CC env variable does nie change
        #   explicit LDSHARED setting dla linker
        def gcv(v):
            jeżeli v == 'LDSHARED':
                zwróć 'gcc-4.2 -bundle -undefined dynamic_lookup '
            zwróć 'gcc-4.2'
        sysconfig.get_config_var = gcv
        przy EnvironmentVarGuard() jako env:
            env['CC'] = 'my_cc'
            env['LDSHARED'] = 'my_ld -bundle -dynamic'
            sysconfig.customize_compiler(self.cc)
        self.assertEqual(self.cc.linker_so[0], 'my_ld')


def test_suite():
    zwróć unittest.makeSuite(UnixCCompilerTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
