"""Tests dla distutils.util."""
zaimportuj os
zaimportuj sys
zaimportuj unittest
z copy zaimportuj copy
z test.support zaimportuj run_unittest

z distutils.errors zaimportuj DistutilsPlatformError, DistutilsByteCompileError
z distutils.util zaimportuj (get_platform, convert_path, change_root,
                            check_environ, split_quoted, strtobool,
                            rfc822_escape, byte_compile,
                            grok_environment_error)
z distutils zaimportuj util # used to patch _environ_checked
z distutils.sysconfig zaimportuj get_config_vars
z distutils zaimportuj sysconfig
z distutils.tests zaimportuj support
zaimportuj _osx_support

klasa UtilTestCase(support.EnvironGuard, unittest.TestCase):

    def setUp(self):
        super(UtilTestCase, self).setUp()
        # saving the environment
        self.name = os.name
        self.platform = sys.platform
        self.version = sys.version
        self.sep = os.sep
        self.join = os.path.join
        self.isabs = os.path.isabs
        self.splitdrive = os.path.splitdrive
        self._config_vars = copy(sysconfig._config_vars)

        # patching os.uname
        jeżeli hasattr(os, 'uname'):
            self.uname = os.uname
            self._uname = os.uname()
        inaczej:
            self.uname = Nic
            self._uname = Nic

        os.uname = self._get_uname

    def tearDown(self):
        # getting back the environment
        os.name = self.name
        sys.platform = self.platform
        sys.version = self.version
        os.sep = self.sep
        os.path.join = self.join
        os.path.isabs = self.isabs
        os.path.splitdrive = self.splitdrive
        jeżeli self.uname jest nie Nic:
            os.uname = self.uname
        inaczej:
            usuń os.uname
        sysconfig._config_vars = copy(self._config_vars)
        super(UtilTestCase, self).tearDown()

    def _set_uname(self, uname):
        self._uname = uname

    def _get_uname(self):
        zwróć self._uname

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
                    'root:xnu-792.25.20~1/RELEASE_I386'), 'i386'))
        _osx_support._remove_original_values(get_config_vars())
        get_config_vars()['MACOSX_DEPLOYMENT_TARGET'] = '10.3'

        get_config_vars()['CFLAGS'] = ('-fno-strict-aliasing -DNDEBUG -g '
                                       '-fwrapv -O3 -Wall -Wstrict-prototypes')

        cursize = sys.maxsize
        sys.maxsize = (2 ** 31)-1
        spróbuj:
            self.assertEqual(get_platform(), 'macosx-10.3-i386')
        w_końcu:
            sys.maxsize = cursize

        # macbook przy fat binaries (fat, universal albo fat64)
        _osx_support._remove_original_values(get_config_vars())
        get_config_vars()['MACOSX_DEPLOYMENT_TARGET'] = '10.4'
        get_config_vars()['CFLAGS'] = ('-arch ppc -arch i386 -isysroot '
                                       '/Developer/SDKs/MacOSX10.4u.sdk  '
                                       '-fno-strict-aliasing -fno-common '
                                       '-dynamic -DNDEBUG -g -O3')

        self.assertEqual(get_platform(), 'macosx-10.4-fat')

        _osx_support._remove_original_values(get_config_vars())
        os.environ['MACOSX_DEPLOYMENT_TARGET'] = '10.1'
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
                                           '-dynamic -DNDEBUG -g -O3'%(arch,))

            self.assertEqual(get_platform(), 'macosx-10.4-%s'%(arch,))


        # linux debian sarge
        os.name = 'posix'
        sys.version = ('2.3.5 (#1, Jul  4 2007, 17:28:59) '
                       '\n[GCC 4.1.2 20061115 (prerelease) (Debian 4.1.1-21)]')
        sys.platform = 'linux2'
        self._set_uname(('Linux', 'aglae', '2.6.21.1dedibox-r7',
                    '#1 Mon Apr 30 17:25:38 CEST 2007', 'i686'))

        self.assertEqual(get_platform(), 'linux-i686')

        # XXX more platforms to tests here

    def test_convert_path(self):
        # linux/mac
        os.sep = '/'
        def _join(path):
            zwróć '/'.join(path)
        os.path.join = _join

        self.assertEqual(convert_path('/home/to/my/stuff'),
                         '/home/to/my/stuff')

        # win
        os.sep = '\\'
        def _join(*path):
            zwróć '\\'.join(path)
        os.path.join = _join

        self.assertRaises(ValueError, convert_path, '/home/to/my/stuff')
        self.assertRaises(ValueError, convert_path, 'home/to/my/stuff/')

        self.assertEqual(convert_path('home/to/my/stuff'),
                         'home\\to\\my\\stuff')
        self.assertEqual(convert_path('.'),
                         os.curdir)

    def test_change_root(self):
        # linux/mac
        os.name = 'posix'
        def _isabs(path):
            zwróć path[0] == '/'
        os.path.isabs = _isabs
        def _join(*path):
            zwróć '/'.join(path)
        os.path.join = _join

        self.assertEqual(change_root('/root', '/old/its/here'),
                         '/root/old/its/here')
        self.assertEqual(change_root('/root', 'its/here'),
                         '/root/its/here')

        # windows
        os.name = 'nt'
        def _isabs(path):
            zwróć path.startswith('c:\\')
        os.path.isabs = _isabs
        def _splitdrive(path):
            jeżeli path.startswith('c:'):
                zwróć ('', path.replace('c:', ''))
            zwróć ('', path)
        os.path.splitdrive = _splitdrive
        def _join(*path):
            zwróć '\\'.join(path)
        os.path.join = _join

        self.assertEqual(change_root('c:\\root', 'c:\\old\\its\\here'),
                         'c:\\root\\old\\its\\here')
        self.assertEqual(change_root('c:\\root', 'its\\here'),
                         'c:\\root\\its\\here')

        # BugsBunny os (it's a great os)
        os.name = 'BugsBunny'
        self.assertRaises(DistutilsPlatformError,
                          change_root, 'c:\\root', 'its\\here')

        # XXX platforms to be covered: mac

    def test_check_environ(self):
        util._environ_checked = 0
        jeżeli 'HOME' w os.environ:
            usuń os.environ['HOME']

        # posix without HOME
        jeżeli os.name == 'posix':  # this test won't run on windows
            check_environ()
            zaimportuj pwd
            self.assertEqual(os.environ['HOME'], pwd.getpwuid(os.getuid())[5])
        inaczej:
            check_environ()

        self.assertEqual(os.environ['PLAT'], get_platform())
        self.assertEqual(util._environ_checked, 1)

    def test_split_quoted(self):
        self.assertEqual(split_quoted('""one"" "two" \'three\' \\four'),
                         ['one', 'two', 'three', 'four'])

    def test_strtobool(self):
        yes = ('y', 'Y', 'yes', 'Prawda', 't', 'true', 'Prawda', 'On', 'on', '1')
        no = ('n', 'no', 'f', 'false', 'off', '0', 'Off', 'No', 'N')

        dla y w yes:
            self.assertPrawda(strtobool(y))

        dla n w no:
            self.assertNieprawda(strtobool(n))

    def test_rfc822_escape(self):
        header = 'I am a\npoor\nlonesome\nheader\n'
        res = rfc822_escape(header)
        wanted = ('I am a%(8s)spoor%(8s)slonesome%(8s)s'
                  'header%(8s)s') % {'8s': '\n'+8*' '}
        self.assertEqual(res, wanted)

    def test_dont_write_bytecode(self):
        # makes sure byte_compile podnieś a DistutilsError
        # jeżeli sys.dont_write_bytecode jest Prawda
        old_dont_write_bytecode = sys.dont_write_bytecode
        sys.dont_write_bytecode = Prawda
        spróbuj:
            self.assertRaises(DistutilsByteCompileError, byte_compile, [])
        w_końcu:
            sys.dont_write_bytecode = old_dont_write_bytecode

    def test_grok_environment_error(self):
        # test obsolete function to ensure backward compat (#4931)
        exc = IOError("Unable to find batch file")
        msg = grok_environment_error(exc)
        self.assertEqual(msg, "error: Unable to find batch file")


def test_suite():
    zwróć unittest.makeSuite(UtilTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
