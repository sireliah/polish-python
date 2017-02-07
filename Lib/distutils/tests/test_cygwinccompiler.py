"""Tests dla distutils.cygwinccompiler."""
zaimportuj unittest
zaimportuj sys
zaimportuj os
z io zaimportuj BytesIO
zaimportuj subprocess
z test.support zaimportuj run_unittest

z distutils zaimportuj cygwinccompiler
z distutils.cygwinccompiler zaimportuj (CygwinCCompiler, check_config_h,
                                       CONFIG_H_OK, CONFIG_H_NOTOK,
                                       CONFIG_H_UNCERTAIN, get_versions,
                                       get_msvcr)
z distutils.tests zaimportuj support

klasa FakePopen(object):
    test_class = Nic

    def __init__(self, cmd, shell, stdout):
        self.cmd = cmd.split()[0]
        exes = self.test_class._exes
        jeżeli self.cmd w exes:
            # issue #6438 w Python 3.x, Popen returns bytes
            self.stdout = BytesIO(exes[self.cmd])
        inaczej:
            self.stdout = os.popen(cmd, 'r')


klasa CygwinCCompilerTestCase(support.TempdirManager,
                              unittest.TestCase):

    def setUp(self):
        super(CygwinCCompilerTestCase, self).setUp()
        self.version = sys.version
        self.python_h = os.path.join(self.mkdtemp(), 'python.h')
        z distutils zaimportuj sysconfig
        self.old_get_config_h_filename = sysconfig.get_config_h_filename
        sysconfig.get_config_h_filename = self._get_config_h_filename
        self.old_find_executable = cygwinccompiler.find_executable
        cygwinccompiler.find_executable = self._find_executable
        self._exes = {}
        self.old_popen = cygwinccompiler.Popen
        FakePopen.test_class = self
        cygwinccompiler.Popen = FakePopen

    def tearDown(self):
        sys.version = self.version
        z distutils zaimportuj sysconfig
        sysconfig.get_config_h_filename = self.old_get_config_h_filename
        cygwinccompiler.find_executable = self.old_find_executable
        cygwinccompiler.Popen = self.old_popen
        super(CygwinCCompilerTestCase, self).tearDown()

    def _get_config_h_filename(self):
        zwróć self.python_h

    def _find_executable(self, name):
        jeżeli name w self._exes:
            zwróć name
        zwróć Nic

    def test_check_config_h(self):

        # check_config_h looks dla "GCC" w sys.version first
        # returns CONFIG_H_OK jeżeli found
        sys.version = ('2.6.1 (r261:67515, Dec  6 2008, 16:42:21) \n[GCC '
                       '4.0.1 (Apple Computer, Inc. build 5370)]')

        self.assertEqual(check_config_h()[0], CONFIG_H_OK)

        # then it tries to see jeżeli it can find "__GNUC__" w pyconfig.h
        sys.version = 'something without the *CC word'

        # jeżeli the file doesn't exist it returns  CONFIG_H_UNCERTAIN
        self.assertEqual(check_config_h()[0], CONFIG_H_UNCERTAIN)

        # jeżeli it exists but does nie contain __GNUC__, it returns CONFIG_H_NOTOK
        self.write_file(self.python_h, 'xxx')
        self.assertEqual(check_config_h()[0], CONFIG_H_NOTOK)

        # oraz CONFIG_H_OK jeżeli __GNUC__ jest found
        self.write_file(self.python_h, 'xxx __GNUC__ xxx')
        self.assertEqual(check_config_h()[0], CONFIG_H_OK)

    def test_get_versions(self):

        # get_versions calls distutils.spawn.find_executable on
        # 'gcc', 'ld' oraz 'dllwrap'
        self.assertEqual(get_versions(), (Nic, Nic, Nic))

        # Let's fake we have 'gcc' oraz it returns '3.4.5'
        self._exes['gcc'] = b'gcc (GCC) 3.4.5 (mingw special)\nFSF'
        res = get_versions()
        self.assertEqual(str(res[0]), '3.4.5')

        # oraz let's see what happens when the version
        # doesn't match the regular expression
        # (\d+\.\d+(\.\d+)*)
        self._exes['gcc'] = b'very strange output'
        res = get_versions()
        self.assertEqual(res[0], Nic)

        # same thing dla ld
        self._exes['ld'] = b'GNU ld version 2.17.50 20060824'
        res = get_versions()
        self.assertEqual(str(res[1]), '2.17.50')
        self._exes['ld'] = b'@(#)PROGRAM:ld  PROJECT:ld64-77'
        res = get_versions()
        self.assertEqual(res[1], Nic)

        # oraz dllwrap
        self._exes['dllwrap'] = b'GNU dllwrap 2.17.50 20060824\nFSF'
        res = get_versions()
        self.assertEqual(str(res[2]), '2.17.50')
        self._exes['dllwrap'] = b'Cheese Wrap'
        res = get_versions()
        self.assertEqual(res[2], Nic)

    def test_get_msvcr(self):

        # none
        sys.version  = ('2.6.1 (r261:67515, Dec  6 2008, 16:42:21) '
                        '\n[GCC 4.0.1 (Apple Computer, Inc. build 5370)]')
        self.assertEqual(get_msvcr(), Nic)

        # MSVC 7.0
        sys.version = ('2.5.1 (r251:54863, Apr 18 2007, 08:51:08) '
                       '[MSC v.1300 32 bits (Intel)]')
        self.assertEqual(get_msvcr(), ['msvcr70'])

        # MSVC 7.1
        sys.version = ('2.5.1 (r251:54863, Apr 18 2007, 08:51:08) '
                       '[MSC v.1310 32 bits (Intel)]')
        self.assertEqual(get_msvcr(), ['msvcr71'])

        # VS2005 / MSVC 8.0
        sys.version = ('2.5.1 (r251:54863, Apr 18 2007, 08:51:08) '
                       '[MSC v.1400 32 bits (Intel)]')
        self.assertEqual(get_msvcr(), ['msvcr80'])

        # VS2008 / MSVC 9.0
        sys.version = ('2.5.1 (r251:54863, Apr 18 2007, 08:51:08) '
                       '[MSC v.1500 32 bits (Intel)]')
        self.assertEqual(get_msvcr(), ['msvcr90'])

        # unknown
        sys.version = ('2.5.1 (r251:54863, Apr 18 2007, 08:51:08) '
                       '[MSC v.1999 32 bits (Intel)]')
        self.assertRaises(ValueError, get_msvcr)

def test_suite():
    zwróć unittest.makeSuite(CygwinCCompilerTestCase)

jeżeli __name__ == '__main__':
    run_unittest(test_suite())
