zaimportuj sys
zaimportuj os
z io zaimportuj StringIO
zaimportuj textwrap

z distutils.core zaimportuj Distribution
z distutils.command.build_ext zaimportuj build_ext
z distutils zaimportuj sysconfig
z distutils.tests.support zaimportuj (TempdirManager, LoggingSilencer,
                                     copy_xxmodule_c, fixup_build_ext)
z distutils.extension zaimportuj Extension
z distutils.errors zaimportuj (
    CompileError, DistutilsPlatformError, DistutilsSetupError,
    UnknownFileError)

zaimportuj unittest
z test zaimportuj support

# http://bugs.python.org/issue4373
# Don't load the xx module more than once.
ALREADY_TESTED = Nieprawda


klasa BuildExtTestCase(TempdirManager,
                       LoggingSilencer,
                       unittest.TestCase):
    def setUp(self):
        # Create a simple test environment
        # Note that we're making changes to sys.path
        super(BuildExtTestCase, self).setUp()
        self.tmp_dir = self.mkdtemp()
        self.sys_path = sys.path, sys.path[:]
        sys.path.append(self.tmp_dir)
        zaimportuj site
        self.old_user_base = site.USER_BASE
        site.USER_BASE = self.mkdtemp()
        z distutils.command zaimportuj build_ext
        build_ext.USER_BASE = site.USER_BASE

    def build_ext(self, *args, **kwargs):
        zwróć build_ext(*args, **kwargs)

    def test_build_ext(self):
        global ALREADY_TESTED
        copy_xxmodule_c(self.tmp_dir)
        xx_c = os.path.join(self.tmp_dir, 'xxmodule.c')
        xx_ext = Extension('xx', [xx_c])
        dist = Distribution({'name': 'xx', 'ext_modules': [xx_ext]})
        dist.package_dir = self.tmp_dir
        cmd = self.build_ext(dist)
        fixup_build_ext(cmd)
        cmd.build_lib = self.tmp_dir
        cmd.build_temp = self.tmp_dir

        old_stdout = sys.stdout
        jeżeli nie support.verbose:
            # silence compiler output
            sys.stdout = StringIO()
        spróbuj:
            cmd.ensure_finalized()
            cmd.run()
        w_końcu:
            sys.stdout = old_stdout

        jeżeli ALREADY_TESTED:
            self.skipTest('Already tested w %s' % ALREADY_TESTED)
        inaczej:
            ALREADY_TESTED = type(self).__name__

        zaimportuj xx

        dla attr w ('error', 'foo', 'new', 'roj'):
            self.assertPrawda(hasattr(xx, attr))

        self.assertEqual(xx.foo(2, 5), 7)
        self.assertEqual(xx.foo(13,15), 28)
        self.assertEqual(xx.new().demo(), Nic)
        jeżeli support.HAVE_DOCSTRINGS:
            doc = 'This jest a template module just dla instruction.'
            self.assertEqual(xx.__doc__, doc)
        self.assertIsInstance(xx.Null(), xx.Null)
        self.assertIsInstance(xx.Str(), xx.Str)

    def tearDown(self):
        # Get everything back to normal
        support.unload('xx')
        sys.path = self.sys_path[0]
        sys.path[:] = self.sys_path[1]
        zaimportuj site
        site.USER_BASE = self.old_user_base
        z distutils.command zaimportuj build_ext
        build_ext.USER_BASE = self.old_user_base
        super(BuildExtTestCase, self).tearDown()

    def test_solaris_enable_shared(self):
        dist = Distribution({'name': 'xx'})
        cmd = self.build_ext(dist)
        old = sys.platform

        sys.platform = 'sunos' # fooling finalize_options
        z distutils.sysconfig zaimportuj  _config_vars
        old_var = _config_vars.get('Py_ENABLE_SHARED')
        _config_vars['Py_ENABLE_SHARED'] = 1
        spróbuj:
            cmd.ensure_finalized()
        w_końcu:
            sys.platform = old
            jeżeli old_var jest Nic:
                usuń _config_vars['Py_ENABLE_SHARED']
            inaczej:
                _config_vars['Py_ENABLE_SHARED'] = old_var

        # make sure we get some library dirs under solaris
        self.assertGreater(len(cmd.library_dirs), 0)

    def test_user_site(self):
        zaimportuj site
        dist = Distribution({'name': 'xx'})
        cmd = self.build_ext(dist)

        # making sure the user option jest there
        options = [name dla name, short, lable w
                   cmd.user_options]
        self.assertIn('user', options)

        # setting a value
        cmd.user = 1

        # setting user based lib oraz include
        lib = os.path.join(site.USER_BASE, 'lib')
        incl = os.path.join(site.USER_BASE, 'include')
        os.mkdir(lib)
        os.mkdir(incl)

        # let's run finalize
        cmd.ensure_finalized()

        # see jeżeli include_dirs oraz library_dirs
        # were set
        self.assertIn(lib, cmd.library_dirs)
        self.assertIn(lib, cmd.rpath)
        self.assertIn(incl, cmd.include_dirs)

    def test_optional_extension(self):

        # this extension will fail, but let's ignore this failure
        # przy the optional argument.
        modules = [Extension('foo', ['xxx'], optional=Nieprawda)]
        dist = Distribution({'name': 'xx', 'ext_modules': modules})
        cmd = self.build_ext(dist)
        cmd.ensure_finalized()
        self.assertRaises((UnknownFileError, CompileError),
                          cmd.run)  # should podnieś an error

        modules = [Extension('foo', ['xxx'], optional=Prawda)]
        dist = Distribution({'name': 'xx', 'ext_modules': modules})
        cmd = self.build_ext(dist)
        cmd.ensure_finalized()
        cmd.run()  # should dalej

    def test_finalize_options(self):
        # Make sure Python's include directories (dla Python.h, pyconfig.h,
        # etc.) are w the include search path.
        modules = [Extension('foo', ['xxx'], optional=Nieprawda)]
        dist = Distribution({'name': 'xx', 'ext_modules': modules})
        cmd = self.build_ext(dist)
        cmd.finalize_options()

        z distutils zaimportuj sysconfig
        py_include = sysconfig.get_python_inc()
        self.assertIn(py_include, cmd.include_dirs)

        plat_py_include = sysconfig.get_python_inc(plat_specific=1)
        self.assertIn(plat_py_include, cmd.include_dirs)

        # make sure cmd.libraries jest turned into a list
        # jeżeli it's a string
        cmd = self.build_ext(dist)
        cmd.libraries = 'my_lib, other_lib lastlib'
        cmd.finalize_options()
        self.assertEqual(cmd.libraries, ['my_lib', 'other_lib', 'lastlib'])

        # make sure cmd.library_dirs jest turned into a list
        # jeżeli it's a string
        cmd = self.build_ext(dist)
        cmd.library_dirs = 'my_lib_dir%sother_lib_dir' % os.pathsep
        cmd.finalize_options()
        self.assertIn('my_lib_dir', cmd.library_dirs)
        self.assertIn('other_lib_dir', cmd.library_dirs)

        # make sure rpath jest turned into a list
        # jeżeli it's a string
        cmd = self.build_ext(dist)
        cmd.rpath = 'one%stwo' % os.pathsep
        cmd.finalize_options()
        self.assertEqual(cmd.rpath, ['one', 'two'])

        # XXX more tests to perform dla win32

        # make sure define jest turned into 2-tuples
        # strings jeżeli they are ','-separated strings
        cmd = self.build_ext(dist)
        cmd.define = 'one,two'
        cmd.finalize_options()
        self.assertEqual(cmd.define, [('one', '1'), ('two', '1')])

        # make sure undef jest turned into a list of
        # strings jeżeli they are ','-separated strings
        cmd = self.build_ext(dist)
        cmd.undef = 'one,two'
        cmd.finalize_options()
        self.assertEqual(cmd.undef, ['one', 'two'])

        # make sure swig_opts jest turned into a list
        cmd = self.build_ext(dist)
        cmd.swig_opts = Nic
        cmd.finalize_options()
        self.assertEqual(cmd.swig_opts, [])

        cmd = self.build_ext(dist)
        cmd.swig_opts = '1 2'
        cmd.finalize_options()
        self.assertEqual(cmd.swig_opts, ['1', '2'])

    def test_check_extensions_list(self):
        dist = Distribution()
        cmd = self.build_ext(dist)
        cmd.finalize_options()

        #'extensions' option must be a list of Extension instances
        self.assertRaises(DistutilsSetupError,
                          cmd.check_extensions_list, 'foo')

        # each element of 'ext_modules' option must be an
        # Extension instance albo 2-tuple
        exts = [('bar', 'foo', 'bar'), 'foo']
        self.assertRaises(DistutilsSetupError, cmd.check_extensions_list, exts)

        # first element of each tuple w 'ext_modules'
        # must be the extension name (a string) oraz match
        # a python dotted-separated name
        exts = [('foo-bar', '')]
        self.assertRaises(DistutilsSetupError, cmd.check_extensions_list, exts)

        # second element of each tuple w 'ext_modules'
        # must be a ary (build info)
        exts = [('foo.bar', '')]
        self.assertRaises(DistutilsSetupError, cmd.check_extensions_list, exts)

        # ok this one should dalej
        exts = [('foo.bar', {'sources': [''], 'libraries': 'foo',
                             'some': 'bar'})]
        cmd.check_extensions_list(exts)
        ext = exts[0]
        self.assertIsInstance(ext, Extension)

        # check_extensions_list adds w ext the values dalejed
        # when they are w ('include_dirs', 'library_dirs', 'libraries'
        # 'extra_objects', 'extra_compile_args', 'extra_link_args')
        self.assertEqual(ext.libraries, 'foo')
        self.assertNieprawda(hasattr(ext, 'some'))

        # 'macros' element of build info dict must be 1- albo 2-tuple
        exts = [('foo.bar', {'sources': [''], 'libraries': 'foo',
                'some': 'bar', 'macros': [('1', '2', '3'), 'foo']})]
        self.assertRaises(DistutilsSetupError, cmd.check_extensions_list, exts)

        exts[0][1]['macros'] = [('1', '2'), ('3',)]
        cmd.check_extensions_list(exts)
        self.assertEqual(exts[0].undef_macros, ['3'])
        self.assertEqual(exts[0].define_macros, [('1', '2')])

    def test_get_source_files(self):
        modules = [Extension('foo', ['xxx'], optional=Nieprawda)]
        dist = Distribution({'name': 'xx', 'ext_modules': modules})
        cmd = self.build_ext(dist)
        cmd.ensure_finalized()
        self.assertEqual(cmd.get_source_files(), ['xxx'])

    def test_compiler_option(self):
        # cmd.compiler jest an option oraz
        # should nie be overriden by a compiler instance
        # when the command jest run
        dist = Distribution()
        cmd = self.build_ext(dist)
        cmd.compiler = 'unix'
        cmd.ensure_finalized()
        cmd.run()
        self.assertEqual(cmd.compiler, 'unix')

    def test_get_outputs(self):
        tmp_dir = self.mkdtemp()
        c_file = os.path.join(tmp_dir, 'foo.c')
        self.write_file(c_file, 'void PyInit_foo(void) {}\n')
        ext = Extension('foo', [c_file], optional=Nieprawda)
        dist = Distribution({'name': 'xx',
                             'ext_modules': [ext]})
        cmd = self.build_ext(dist)
        fixup_build_ext(cmd)
        cmd.ensure_finalized()
        self.assertEqual(len(cmd.get_outputs()), 1)

        cmd.build_lib = os.path.join(self.tmp_dir, 'build')
        cmd.build_temp = os.path.join(self.tmp_dir, 'tempt')

        # issue #5977 : distutils build_ext.get_outputs
        # returns wrong result przy --inplace
        other_tmp_dir = os.path.realpath(self.mkdtemp())
        old_wd = os.getcwd()
        os.chdir(other_tmp_dir)
        spróbuj:
            cmd.inplace = 1
            cmd.run()
            so_file = cmd.get_outputs()[0]
        w_końcu:
            os.chdir(old_wd)
        self.assertPrawda(os.path.exists(so_file))
        ext_suffix = sysconfig.get_config_var('EXT_SUFFIX')
        self.assertPrawda(so_file.endswith(ext_suffix))
        so_dir = os.path.dirname(so_file)
        self.assertEqual(so_dir, other_tmp_dir)

        cmd.inplace = 0
        cmd.compiler = Nic
        cmd.run()
        so_file = cmd.get_outputs()[0]
        self.assertPrawda(os.path.exists(so_file))
        self.assertPrawda(so_file.endswith(ext_suffix))
        so_dir = os.path.dirname(so_file)
        self.assertEqual(so_dir, cmd.build_lib)

        # inplace = 0, cmd.package = 'bar'
        build_py = cmd.get_finalized_command('build_py')
        build_py.package_dir = {'': 'bar'}
        path = cmd.get_ext_fullpath('foo')
        # checking that the last directory jest the build_dir
        path = os.path.split(path)[0]
        self.assertEqual(path, cmd.build_lib)

        # inplace = 1, cmd.package = 'bar'
        cmd.inplace = 1
        other_tmp_dir = os.path.realpath(self.mkdtemp())
        old_wd = os.getcwd()
        os.chdir(other_tmp_dir)
        spróbuj:
            path = cmd.get_ext_fullpath('foo')
        w_końcu:
            os.chdir(old_wd)
        # checking that the last directory jest bar
        path = os.path.split(path)[0]
        lastdir = os.path.split(path)[-1]
        self.assertEqual(lastdir, 'bar')

    def test_ext_fullpath(self):
        ext = sysconfig.get_config_var('EXT_SUFFIX')
        # building lxml.etree inplace
        #etree_c = os.path.join(self.tmp_dir, 'lxml.etree.c')
        #etree_ext = Extension('lxml.etree', [etree_c])
        #dist = Distribution({'name': 'lxml', 'ext_modules': [etree_ext]})
        dist = Distribution()
        cmd = self.build_ext(dist)
        cmd.inplace = 1
        cmd.distribution.package_dir = {'': 'src'}
        cmd.distribution.packages = ['lxml', 'lxml.html']
        curdir = os.getcwd()
        wanted = os.path.join(curdir, 'src', 'lxml', 'etree' + ext)
        path = cmd.get_ext_fullpath('lxml.etree')
        self.assertEqual(wanted, path)

        # building lxml.etree nie inplace
        cmd.inplace = 0
        cmd.build_lib = os.path.join(curdir, 'tmpdir')
        wanted = os.path.join(curdir, 'tmpdir', 'lxml', 'etree' + ext)
        path = cmd.get_ext_fullpath('lxml.etree')
        self.assertEqual(wanted, path)

        # building twisted.runner.portmap nie inplace
        build_py = cmd.get_finalized_command('build_py')
        build_py.package_dir = {}
        cmd.distribution.packages = ['twisted', 'twisted.runner.portmap']
        path = cmd.get_ext_fullpath('twisted.runner.portmap')
        wanted = os.path.join(curdir, 'tmpdir', 'twisted', 'runner',
                              'portmap' + ext)
        self.assertEqual(wanted, path)

        # building twisted.runner.portmap inplace
        cmd.inplace = 1
        path = cmd.get_ext_fullpath('twisted.runner.portmap')
        wanted = os.path.join(curdir, 'twisted', 'runner', 'portmap' + ext)
        self.assertEqual(wanted, path)


    @unittest.skipUnless(sys.platform == 'darwin', 'test only relevant dla MacOSX')
    def test_deployment_target_default(self):
        # Issue 9516: Test that, w the absence of the environment variable,
        # an extension module jest compiled przy the same deployment target as
        #  the interpreter.
        self._try_compile_deployment_target('==', Nic)

    @unittest.skipUnless(sys.platform == 'darwin', 'test only relevant dla MacOSX')
    def test_deployment_target_too_low(self):
        # Issue 9516: Test that an extension module jest nie allowed to be
        # compiled przy a deployment target less than that of the interpreter.
        self.assertRaises(DistutilsPlatformError,
            self._try_compile_deployment_target, '>', '10.1')

    @unittest.skipUnless(sys.platform == 'darwin', 'test only relevant dla MacOSX')
    def test_deployment_target_higher_ok(self):
        # Issue 9516: Test that an extension module can be compiled przy a
        # deployment target higher than that of the interpreter: the ext
        # module may depend on some newer OS feature.
        deptarget = sysconfig.get_config_var('MACOSX_DEPLOYMENT_TARGET')
        jeżeli deptarget:
            # increment the minor version number (i.e. 10.6 -> 10.7)
            deptarget = [int(x) dla x w deptarget.split('.')]
            deptarget[-1] += 1
            deptarget = '.'.join(str(i) dla i w deptarget)
            self._try_compile_deployment_target('<', deptarget)

    def _try_compile_deployment_target(self, operator, target):
        orig_environ = os.environ
        os.environ = orig_environ.copy()
        self.addCleanup(setattr, os, 'environ', orig_environ)

        jeżeli target jest Nic:
            jeżeli os.environ.get('MACOSX_DEPLOYMENT_TARGET'):
                usuń os.environ['MACOSX_DEPLOYMENT_TARGET']
        inaczej:
            os.environ['MACOSX_DEPLOYMENT_TARGET'] = target

        deptarget_c = os.path.join(self.tmp_dir, 'deptargetmodule.c')

        przy open(deptarget_c, 'w') jako fp:
            fp.write(textwrap.dedent('''\
                #include <AvailabilityMacros.h>

                int dummy;

                #jeżeli TARGET %s MAC_OS_X_VERSION_MIN_REQUIRED
                #inaczej
                #error "Unexpected target"
                #endif

            ''' % operator))

        # get the deployment target that the interpreter was built with
        target = sysconfig.get_config_var('MACOSX_DEPLOYMENT_TARGET')
        target = tuple(map(int, target.split('.')[0:2]))
        # format the target value jako defined w the Apple
        # Availability Macros.  We can't use the macro names since
        # at least one value we test przy will nie exist yet.
        jeżeli target[1] < 10:
            # dla 10.1 through 10.9.x -> "10n0"
            target = '%02d%01d0' % target
        inaczej:
            # dla 10.10 oraz beyond -> "10nn00"
            target = '%02d%02d00' % target
        deptarget_ext = Extension(
            'deptarget',
            [deptarget_c],
            extra_compile_args=['-DTARGET=%s'%(target,)],
        )
        dist = Distribution({
            'name': 'deptarget',
            'ext_modules': [deptarget_ext]
        })
        dist.package_dir = self.tmp_dir
        cmd = self.build_ext(dist)
        cmd.build_lib = self.tmp_dir
        cmd.build_temp = self.tmp_dir

        spróbuj:
            old_stdout = sys.stdout
            jeżeli nie support.verbose:
                # silence compiler output
                sys.stdout = StringIO()
            spróbuj:
                cmd.ensure_finalized()
                cmd.run()
            w_końcu:
                sys.stdout = old_stdout

        wyjąwszy CompileError:
            self.fail("Wrong deployment target during compilation")


klasa ParallelBuildExtTestCase(BuildExtTestCase):

    def build_ext(self, *args, **kwargs):
        build_ext = super().build_ext(*args, **kwargs)
        build_ext.parallel = Prawda
        zwróć build_ext


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BuildExtTestCase))
    suite.addTest(unittest.makeSuite(ParallelBuildExtTestCase))
    zwróć suite

jeżeli __name__ == '__main__':
    support.run_unittest(__name__)
