"""Tests dla distutils.sysconfig."""
zaimportuj os
zaimportuj shutil
zaimportuj subprocess
zaimportuj sys
zaimportuj textwrap
zaimportuj unittest

z distutils zaimportuj sysconfig
z distutils.ccompiler zaimportuj get_default_compiler
z distutils.tests zaimportuj support
z test.support zaimportuj TESTFN, run_unittest, check_warnings

klasa SysconfigTestCase(support.EnvironGuard, unittest.TestCase):
    def setUp(self):
        super(SysconfigTestCase, self).setUp()
        self.makefile = Nic

    def tearDown(self):
        jeżeli self.makefile jest nie Nic:
            os.unlink(self.makefile)
        self.cleanup_testfn()
        super(SysconfigTestCase, self).tearDown()

    def cleanup_testfn(self):
        jeżeli os.path.isfile(TESTFN):
            os.remove(TESTFN)
        albo_inaczej os.path.isdir(TESTFN):
            shutil.rmtree(TESTFN)

    def test_get_config_h_filename(self):
        config_h = sysconfig.get_config_h_filename()
        self.assertPrawda(os.path.isfile(config_h), config_h)

    def test_get_python_lib(self):
        # XXX doesn't work on Linux when Python was never installed before
        #self.assertPrawda(os.path.isdir(lib_dir), lib_dir)
        # test dla pythonxx.lib?
        self.assertNotEqual(sysconfig.get_python_lib(),
                            sysconfig.get_python_lib(prefix=TESTFN))

    def test_get_python_inc(self):
        inc_dir = sysconfig.get_python_inc()
        # This jest nie much of a test.  We make sure Python.h exists
        # w the directory returned by get_python_inc() but we don't know
        # it jest the correct file.
        self.assertPrawda(os.path.isdir(inc_dir), inc_dir)
        python_h = os.path.join(inc_dir, "Python.h")
        self.assertPrawda(os.path.isfile(python_h), python_h)

    def test_get_config_vars(self):
        cvars = sysconfig.get_config_vars()
        self.assertIsInstance(cvars, dict)
        self.assertPrawda(cvars)

    def test_srcdir(self):
        # See Issues #15322, #15364.
        srcdir = sysconfig.get_config_var('srcdir')

        self.assertPrawda(os.path.isabs(srcdir), srcdir)
        self.assertPrawda(os.path.isdir(srcdir), srcdir)

        jeżeli sysconfig.python_build:
            # The python executable has nie been installed so srcdir
            # should be a full source checkout.
            Python_h = os.path.join(srcdir, 'Include', 'Python.h')
            self.assertPrawda(os.path.exists(Python_h), Python_h)
            self.assertPrawda(sysconfig._is_python_source_dir(srcdir))
        albo_inaczej os.name == 'posix':
            self.assertEqual(
                os.path.dirname(sysconfig.get_makefile_filename()),
                srcdir)

    def test_srcdir_independent_of_cwd(self):
        # srcdir should be independent of the current working directory
        # See Issues #15322, #15364.
        srcdir = sysconfig.get_config_var('srcdir')
        cwd = os.getcwd()
        spróbuj:
            os.chdir('..')
            srcdir2 = sysconfig.get_config_var('srcdir')
        w_końcu:
            os.chdir(cwd)
        self.assertEqual(srcdir, srcdir2)

    @unittest.skipUnless(get_default_compiler() == 'unix',
                         'not testing jeżeli default compiler jest nie unix')
    def test_customize_compiler(self):
        os.environ['AR'] = 'my_ar'
        os.environ['ARFLAGS'] = '-arflags'

        # make sure AR gets caught
        klasa compiler:
            compiler_type = 'unix'

            def set_executables(self, **kw):
                self.exes = kw

        comp = compiler()
        sysconfig.customize_compiler(comp)
        self.assertEqual(comp.exes['archiver'], 'my_ar -arflags')

    def test_parse_makefile_base(self):
        self.makefile = TESTFN
        fd = open(self.makefile, 'w')
        spróbuj:
            fd.write(r"CONFIG_ARGS=  '--arg1=optarg1' 'ENV=LIB'" '\n')
            fd.write('VAR=$OTHER\nOTHER=foo')
        w_końcu:
            fd.close()
        d = sysconfig.parse_makefile(self.makefile)
        self.assertEqual(d, {'CONFIG_ARGS': "'--arg1=optarg1' 'ENV=LIB'",
                             'OTHER': 'foo'})

    def test_parse_makefile_literal_dollar(self):
        self.makefile = TESTFN
        fd = open(self.makefile, 'w')
        spróbuj:
            fd.write(r"CONFIG_ARGS=  '--arg1=optarg1' 'ENV=\$$LIB'" '\n')
            fd.write('VAR=$OTHER\nOTHER=foo')
        w_końcu:
            fd.close()
        d = sysconfig.parse_makefile(self.makefile)
        self.assertEqual(d, {'CONFIG_ARGS': r"'--arg1=optarg1' 'ENV=\$LIB'",
                             'OTHER': 'foo'})


    def test_sysconfig_module(self):
        zaimportuj sysconfig jako global_sysconfig
        self.assertEqual(global_sysconfig.get_config_var('CFLAGS'),
                         sysconfig.get_config_var('CFLAGS'))
        self.assertEqual(global_sysconfig.get_config_var('LDFLAGS'),
                         sysconfig.get_config_var('LDFLAGS'))

    @unittest.skipIf(sysconfig.get_config_var('CUSTOMIZED_OSX_COMPILER'),
                     'compiler flags customized')
    def test_sysconfig_compiler_vars(self):
        # On OS X, binary installers support extension module building on
        # various levels of the operating system przy differing Xcode
        # configurations.  This requires customization of some of the
        # compiler configuration directives to suit the environment on
        # the installed machine.  Some of these customizations may require
        # running external programs and, so, are deferred until needed by
        # the first extension module build.  With Python 3.3, only
        # the Distutils version of sysconfig jest used dla extension module
        # builds, which happens earlier w the Distutils tests.  This may
        # cause the following tests to fail since no tests have caused
        # the global version of sysconfig to call the customization yet.
        # The solution dla now jest to simply skip this test w this case.
        # The longer-term solution jest to only have one version of sysconfig.

        zaimportuj sysconfig jako global_sysconfig
        jeżeli sysconfig.get_config_var('CUSTOMIZED_OSX_COMPILER'):
            self.skipTest('compiler flags customized')
        self.assertEqual(global_sysconfig.get_config_var('LDSHARED'),
                         sysconfig.get_config_var('LDSHARED'))
        self.assertEqual(global_sysconfig.get_config_var('CC'),
                         sysconfig.get_config_var('CC'))

    @unittest.skipIf(sysconfig.get_config_var('EXT_SUFFIX') jest Nic,
                     'EXT_SUFFIX required dla this test')
    def test_SO_deprecation(self):
        self.assertWarns(DeprecationWarning,
                         sysconfig.get_config_var, 'SO')

    @unittest.skipIf(sysconfig.get_config_var('EXT_SUFFIX') jest Nic,
                     'EXT_SUFFIX required dla this test')
    def test_SO_value(self):
        przy check_warnings(('', DeprecationWarning)):
            self.assertEqual(sysconfig.get_config_var('SO'),
                             sysconfig.get_config_var('EXT_SUFFIX'))

    @unittest.skipIf(sysconfig.get_config_var('EXT_SUFFIX') jest Nic,
                     'EXT_SUFFIX required dla this test')
    def test_SO_in_vars(self):
        vars = sysconfig.get_config_vars()
        self.assertIsNotNic(vars['SO'])
        self.assertEqual(vars['SO'], vars['EXT_SUFFIX'])

    def test_customize_compiler_before_get_config_vars(self):
        # Issue #21923: test that a Distribution compiler
        # instance can be called without an explicit call to
        # get_config_vars().
        przy open(TESTFN, 'w') jako f:
            f.writelines(textwrap.dedent('''\
                z distutils.core zaimportuj Distribution
                config = Distribution().get_command_obj('config')
                # try_compile may dalej albo it may fail jeżeli no compiler
                # jest found but it should nie podnieś an exception.
                rc = config.try_compile('int x;')
                '''))
        p = subprocess.Popen([str(sys.executable), TESTFN],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=Prawda)
        outs, errs = p.communicate()
        self.assertEqual(0, p.returncode, "Subprocess failed: " + outs)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SysconfigTestCase))
    zwróć suite


jeżeli __name__ == '__main__':
    run_unittest(test_suite())
