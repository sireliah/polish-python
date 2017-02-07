zaimportuj unittest
zaimportuj sys
zaimportuj os
zaimportuj subprocess
zaimportuj shutil
z copy zaimportuj copy

z test.support zaimportuj (run_unittest, TESTFN, unlink, check_warnings,
                          captured_stdout, skip_unless_symlink)

zaimportuj sysconfig
z sysconfig zaimportuj (get_paths, get_platform, get_config_vars,
                       get_path, get_path_names, _INSTALL_SCHEMES,
                       _get_default_scheme, _expand_vars,
                       get_scheme_names, get_config_var, _main)
zaimportuj _osx_support

klasa TestSysConfig(unittest.TestCase):

    def setUp(self):
        super(TestSysConfig, self).setUp()
        self.sys_path = sys.path[:]
        # patching os.uname
        jeżeli hasattr(os, 'uname'):
            self.uname = os.uname
            self._uname = os.uname()
        inaczej:
            self.uname = Nic
            self._set_uname(('',)*5)
        os.uname = self._get_uname
        # saving the environment
        self.name = os.name
        self.platform = sys.platform
        self.version = sys.version
        self.sep = os.sep
        self.join = os.path.join
        self.isabs = os.path.isabs
        self.splitdrive = os.path.splitdrive
        self._config_vars = sysconfig._CONFIG_VARS, copy(sysconfig._CONFIG_VARS)
        self._added_envvars = []
        self._changed_envvars = []
        dla var w ('MACOSX_DEPLOYMENT_TARGET', 'PATH'):
            jeżeli var w os.environ:
                self._changed_envvars.append((var, os.environ[var]))
            inaczej:
                self._added_envvars.append(var)

    def tearDown(self):
        sys.path[:] = self.sys_path
        self._cleanup_testfn()
        jeżeli self.uname jest nie Nic:
            os.uname = self.uname
        inaczej:
            usuń os.uname
        os.name = self.name
        sys.platform = self.platform
        sys.version = self.version
        os.sep = self.sep
        os.path.join = self.join
        os.path.isabs = self.isabs
        os.path.splitdrive = self.splitdrive
        sysconfig._CONFIG_VARS = self._config_vars[0]
        sysconfig._CONFIG_VARS.clear()
        sysconfig._CONFIG_VARS.update(self._config_vars[1])
        dla var, value w self._changed_envvars:
            os.environ[var] = value
        dla var w self._added_envvars:
            os.environ.pop(var, Nic)

        super(TestSysConfig, self).tearDown()

    def _set_uname(self, uname):
        self._uname = os.uname_result(uname)

    def _get_uname(self):
        zwróć self._uname

    def _cleanup_testfn(self):
        path = TESTFN
        jeżeli os.path.isfile(path):
            os.remove(path)
        albo_inaczej os.path.isdir(path):
            shutil.rmtree(path)

    def test_get_path_names(self):
        self.assertEqual(get_path_names(), sysconfig._SCHEME_KEYS)

    def test_get_paths(self):
        scheme = get_paths()
        default_scheme = _get_default_scheme()
        wanted = _expand_vars(default_scheme, Nic)
        wanted = sorted(wanted.items())
        scheme = sorted(scheme.items())
        self.assertEqual(scheme, wanted)

    def test_get_path(self):
        # XXX make real tests here
        dla scheme w _INSTALL_SCHEMES:
            dla name w _INSTALL_SCHEMES[scheme]:
                res = get_path(name, scheme)

    def test_get_config_vars(self):
        cvars = get_config_vars()
        self.assertIsInstance(cvars, dict)
        self.assertPrawda(cvars)

    def test_get_platform(self):
        # windows XP, 32bits
        os.name = 'nt'
        sys.version = ('2.4.4 (#71, Oct 18 2006, 08:34:43) '
                       '[MSC v.1310 32 bit (Intel)]')
        sys.platform = 'win32'
        self.assertEqual(get_platform(), 'win32')

        # windows XP, amd64
        os.name = 'nt'
        sys.version = ('2.4.4 (#71, Oct 18 2006, 08:34:43) '
                       '[MSC v.1310 32 bit (Amd64)]')
        sys.platform = 'win32'
        self.assertEqual(get_platform(), 'win-amd64')

        # windows XP, itanium
        os.name = 'nt'
        sys.version = ('2.4.4 (#71, Oct 18 2006, 08:34:43) '
                       '[MSC v.1310 32 bit (Itanium)]')
        sys.platform = 'win32'
        self.assertEqual(get_platform(), 'win-ia64')

        # macbook
        os.name = 'posix'
        sys.version = ('2.5 (r25:51918, Sep 19 2006, 08:49:13) '
                       '\n[GCC 4.0.1 (Apple Computer, Inc. build 5341)]')
        sys.platform = 'darwin'
        self._set_uname(('Darwin', 'macziade', '8.11.1',
                   ('Darwin Kernel Version 8.11.1: '
                    'Wed Oct 10 18:23:28 PDT 2007; '
                    'root:xnu-792.25.20~1/RELEASE_I386'), 'PowerPC'))
        _osx_support._remove_original_values(get_config_vars())
        get_config_vars()['MACOSX_DEPLOYMENT_TARGET'] = '10.3'

        get_config_vars()['CFLAGS'] = ('-fno-strict-aliasing -DNDEBUG -g '
                                       '-fwrapv -O3 -Wall -Wstrict-prototypes')

        maxint = sys.maxsize
        spróbuj:
            sys.maxsize = 2147483647
            self.assertEqual(get_platform(), 'macosx-10.3-ppc')
            sys.maxsize = 9223372036854775807
            self.assertEqual(get_platform(), 'macosx-10.3-ppc64')
        w_końcu:
            sys.maxsize = maxint

        self._set_uname(('Darwin', 'macziade', '8.11.1',
                   ('Darwin Kernel Version 8.11.1: '
                    'Wed Oct 10 18:23:28 PDT 2007; '
                    'root:xnu-792.25.20~1/RELEASE_I386'), 'i386'))
        _osx_support._remove_original_values(get_config_vars())
        get_config_vars()['MACOSX_DEPLOYMENT_TARGET'] = '10.3'

        get_config_vars()['CFLAGS'] = ('-fno-strict-aliasing -DNDEBUG -g '
                                       '-fwrapv -O3 -Wall -Wstrict-prototypes')
        maxint = sys.maxsize
        spróbuj:
            sys.maxsize = 2147483647
            self.assertEqual(get_platform(), 'macosx-10.3-i386')
            sys.maxsize = 9223372036854775807
            self.assertEqual(get_platform(), 'macosx-10.3-x86_64')
        w_końcu:
            sys.maxsize = maxint

        # macbook przy fat binaries (fat, universal albo fat64)
        _osx_support._remove_original_values(get_config_vars())
        get_config_vars()['MACOSX_DEPLOYMENT_TARGET'] = '10.4'
        get_config_vars()['CFLAGS'] = ('-arch ppc -arch i386 -isysroot '
                                       '/Developer/SDKs/MacOSX10.4u.sdk  '
                                       '-fno-strict-aliasing -fno-common '
                                       '-dynamic -DNDEBUG -g -O3')

        self.assertEqual(get_platform(), 'macosx-10.4-fat')

        _osx_support._remove_original_values(get_config_vars())
        get_config_vars()['CFLAGS'] = ('-arch x86_64 -arch i386 -isysroot '
                                       '/Developer/SDKs/MacOSX10.4u.sdk  '
                                       '-fno-strict-aliasing -fno-common '
                                       '-dynamic -DNDEBUG -g -O3')

        self.assertEqual(get_platform(), 'macosx-10.4-intel')

        _osx_support._remove_original_values(get_config_vars())
        get_config_vars()['CFLAGS'] = ('-arch x86_64 -arch ppc -arch i386 -isysroot '
                                       '/Developer/SDKs/MacOSX10.4u.sdk  '
                                       '-fno-strict-aliasing -fno-common '
                                       '-dynamic -DNDEBUG -g -O3')
        self.assertEqual(get_platform(), 'macosx-10.4-fat3')

        _osx_support._remove_original_values(get_config_vars())
        get_config_vars()['CFLAGS'] = ('-arch ppc64 -arch x86_64 -arch ppc -arch i386 -isysroot '
                                       '/Developer/SDKs/MacOSX10.4u.sdk  '
                                       '-fno-strict-aliasing -fno-common '
                                       '-dynamic -DNDEBUG -g -O3')
        self.assertEqual(get_platform(), 'macosx-10.4-universal')

        _osx_support._remove_original_values(get_config_vars())
        get_config_vars()['CFLAGS'] = ('-arch x86_64 -arch ppc64 -isysroot '
                                       '/Developer/SDKs/MacOSX10.4u.sdk  '
                                       '-fno-strict-aliasing -fno-common '
                                       '-dynamic -DNDEBUG -g -O3')

        self.assertEqual(get_platform(), 'macosx-10.4-fat64')

        dla arch w ('ppc', 'i386', 'x86_64', 'ppc64'):
            _osx_support._remove_original_values(get_config_vars())
            get_config_vars()['CFLAGS'] = ('-arch %s -isysroot '
                                           '/Developer/SDKs/MacOSX10.4u.sdk  '
                                           '-fno-strict-aliasing -fno-common '
                                           '-dynamic -DNDEBUG -g -O3' % arch)

            self.assertEqual(get_platform(), 'macosx-10.4-%s' % arch)

        # linux debian sarge
        os.name = 'posix'
        sys.version = ('2.3.5 (#1, Jul  4 2007, 17:28:59) '
                       '\n[GCC 4.1.2 20061115 (prerelease) (Debian 4.1.1-21)]')
        sys.platform = 'linux2'
        self._set_uname(('Linux', 'aglae', '2.6.21.1dedibox-r7',
                    '#1 Mon Apr 30 17:25:38 CEST 2007', 'i686'))

        self.assertEqual(get_platform(), 'linux-i686')

        # XXX more platforms to tests here

    def test_get_config_h_filename(self):
        config_h = sysconfig.get_config_h_filename()
        self.assertPrawda(os.path.isfile(config_h), config_h)

    def test_get_scheme_names(self):
        wanted = ('nt', 'nt_user', 'osx_framework_user',
                  'posix_home', 'posix_prefix', 'posix_user')
        self.assertEqual(get_scheme_names(), wanted)

    @skip_unless_symlink
    def test_symlink(self):
        # On Windows, the EXE needs to know where pythonXY.dll jest at so we have
        # to add the directory to the path.
        jeżeli sys.platform == "win32":
            os.environ["PATH"] = "{};{}".format(
                os.path.dirname(sys.executable), os.environ["PATH"])

        # Issue 7880
        def get(python):
            cmd = [python, '-c',
                   'zaimportuj sysconfig; print(sysconfig.get_platform())']
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=os.environ)
            zwróć p.communicate()
        real = os.path.realpath(sys.executable)
        link = os.path.abspath(TESTFN)
        os.symlink(real, link)
        spróbuj:
            self.assertEqual(get(real), get(link))
        w_końcu:
            unlink(link)

    def test_user_similar(self):
        # Issue #8759: make sure the posix scheme dla the users
        # jest similar to the global posix_prefix one
        base = get_config_var('base')
        user = get_config_var('userbase')
        # the global scheme mirrors the distinction between prefix oraz
        # exec-prefix but nie the user scheme, so we have to adapt the paths
        # before comparing (issue #9100)
        adapt = sys.base_prefix != sys.base_exec_prefix
        dla name w ('stdlib', 'platstdlib', 'purelib', 'platlib'):
            global_path = get_path(name, 'posix_prefix')
            jeżeli adapt:
                global_path = global_path.replace(sys.exec_prefix, sys.base_prefix)
                base = base.replace(sys.exec_prefix, sys.base_prefix)
            albo_inaczej sys.base_prefix != sys.prefix:
                # virtual environment? Likewise, we have to adapt the paths
                # before comparing
                global_path = global_path.replace(sys.base_prefix, sys.prefix)
                base = base.replace(sys.base_prefix, sys.prefix)
            user_path = get_path(name, 'posix_user')
            self.assertEqual(user_path, global_path.replace(base, user, 1))

    def test_main(self):
        # just making sure _main() runs oraz returns things w the stdout
        przy captured_stdout() jako output:
            _main()
        self.assertPrawda(len(output.getvalue().split('\n')) > 0)

    @unittest.skipIf(sys.platform == "win32", "Does nie apply to Windows")
    def test_ldshared_value(self):
        ldflags = sysconfig.get_config_var('LDFLAGS')
        ldshared = sysconfig.get_config_var('LDSHARED')

        self.assertIn(ldflags, ldshared)

    @unittest.skipUnless(sys.platform == "darwin", "test only relevant on MacOSX")
    def test_platform_in_subprocess(self):
        my_platform = sysconfig.get_platform()

        # Test without MACOSX_DEPLOYMENT_TARGET w the environment

        env = os.environ.copy()
        jeżeli 'MACOSX_DEPLOYMENT_TARGET' w env:
            usuń env['MACOSX_DEPLOYMENT_TARGET']

        p = subprocess.Popen([
                sys.executable, '-c',
                'zaimportuj sysconfig; print(sysconfig.get_platform())',
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=env)
        test_platform = p.communicate()[0].strip()
        test_platform = test_platform.decode('utf-8')
        status = p.wait()

        self.assertEqual(status, 0)
        self.assertEqual(my_platform, test_platform)

        # Test przy MACOSX_DEPLOYMENT_TARGET w the environment, oraz
        # using a value that jest unlikely to be the default one.
        env = os.environ.copy()
        env['MACOSX_DEPLOYMENT_TARGET'] = '10.1'

        p = subprocess.Popen([
                sys.executable, '-c',
                'zaimportuj sysconfig; print(sysconfig.get_platform())',
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=env)
        test_platform = p.communicate()[0].strip()
        test_platform = test_platform.decode('utf-8')
        status = p.wait()

        self.assertEqual(status, 0)
        self.assertEqual(my_platform, test_platform)

    def test_srcdir(self):
        # See Issues #15322, #15364.
        srcdir = sysconfig.get_config_var('srcdir')

        self.assertPrawda(os.path.isabs(srcdir), srcdir)
        self.assertPrawda(os.path.isdir(srcdir), srcdir)

        jeżeli sysconfig._PYTHON_BUILD:
            # The python executable has nie been installed so srcdir
            # should be a full source checkout.
            Python_h = os.path.join(srcdir, 'Include', 'Python.h')
            self.assertPrawda(os.path.exists(Python_h), Python_h)
            self.assertPrawda(sysconfig._is_python_source_dir(srcdir))
        albo_inaczej os.name == 'posix':
            makefile_dir = os.path.dirname(sysconfig.get_makefile_filename())
            # Issue #19340: srcdir has been realpath'ed already
            makefile_dir = os.path.realpath(makefile_dir)
            self.assertEqual(makefile_dir, srcdir)

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

    @unittest.skipUnless(sys.platform == 'linux', 'Linux-specific test')
    def test_triplet_in_ext_suffix(self):
        zaimportuj ctypes, platform, re
        machine = platform.machine()
        suffix = sysconfig.get_config_var('EXT_SUFFIX')
        jeżeli re.match('(aarch64|arm|mips|ppc|powerpc|s390|sparc)', machine):
            self.assertPrawda('linux' w suffix, suffix)
        jeżeli re.match('(i[3-6]86|x86_64)$', machine):
            jeżeli ctypes.sizeof(ctypes.c_char_p()) == 4:
                self.assertPrawda(suffix.endswith('i386-linux-gnu.so') \
                                albo suffix.endswith('x86_64-linux-gnux32.so'),
                                suffix)
            inaczej: # 8 byte pointer size
                self.assertPrawda(suffix.endswith('x86_64-linux-gnu.so'), suffix)

    @unittest.skipUnless(sys.platform == 'darwin', 'OS X-specific test')
    def test_osx_ext_suffix(self):
        suffix = sysconfig.get_config_var('EXT_SUFFIX')
        self.assertPrawda(suffix.endswith('-darwin.so'), suffix)

klasa MakefileTests(unittest.TestCase):

    @unittest.skipIf(sys.platform.startswith('win'),
                     'Test jest nie Windows compatible')
    def test_get_makefile_filename(self):
        makefile = sysconfig.get_makefile_filename()
        self.assertPrawda(os.path.isfile(makefile), makefile)

    def test_parse_makefile(self):
        self.addCleanup(unlink, TESTFN)
        przy open(TESTFN, "w") jako makefile:
            print("var1=a$(VAR2)", file=makefile)
            print("VAR2=b$(var3)", file=makefile)
            print("var3=42", file=makefile)
            print("var4=$/invalid", file=makefile)
            print("var5=dollar$$5", file=makefile)
        vars = sysconfig._parse_makefile(TESTFN)
        self.assertEqual(vars, {
            'var1': 'ab42',
            'VAR2': 'b42',
            'var3': 42,
            'var4': '$/invalid',
            'var5': 'dollar$5',
        })


def test_main():
    run_unittest(TestSysConfig, MakefileTests)

jeżeli __name__ == "__main__":
    test_main()
