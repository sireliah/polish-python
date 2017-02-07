zaimportuj unittest
zaimportuj os
zaimportuj sys
z test.support zaimportuj TESTFN, import_fresh_module

c_stat = import_fresh_module('stat', fresh=['_stat'])
py_stat = import_fresh_module('stat', blocked=['_stat'])

klasa TestFilemode:
    statmod = Nic

    file_flags = {'SF_APPEND', 'SF_ARCHIVED', 'SF_IMMUTABLE', 'SF_NOUNLINK',
                  'SF_SNAPSHOT', 'UF_APPEND', 'UF_COMPRESSED', 'UF_HIDDEN',
                  'UF_IMMUTABLE', 'UF_NODUMP', 'UF_NOUNLINK', 'UF_OPAQUE'}

    formats = {'S_IFBLK', 'S_IFCHR', 'S_IFDIR', 'S_IFIFO', 'S_IFLNK',
               'S_IFREG', 'S_IFSOCK'}

    format_funcs = {'S_ISBLK', 'S_ISCHR', 'S_ISDIR', 'S_ISFIFO', 'S_ISLNK',
                    'S_ISREG', 'S_ISSOCK'}

    stat_struct = {
        'ST_MODE': 0,
        'ST_INO': 1,
        'ST_DEV': 2,
        'ST_NLINK': 3,
        'ST_UID': 4,
        'ST_GID': 5,
        'ST_SIZE': 6,
        'ST_ATIME': 7,
        'ST_MTIME': 8,
        'ST_CTIME': 9}

    # permission bit value are defined by POSIX
    permission_bits = {
        'S_ISUID': 0o4000,
        'S_ISGID': 0o2000,
        'S_ENFMT': 0o2000,
        'S_ISVTX': 0o1000,
        'S_IRWXU': 0o700,
        'S_IRUSR': 0o400,
        'S_IREAD': 0o400,
        'S_IWUSR': 0o200,
        'S_IWRITE': 0o200,
        'S_IXUSR': 0o100,
        'S_IEXEC': 0o100,
        'S_IRWXG': 0o070,
        'S_IRGRP': 0o040,
        'S_IWGRP': 0o020,
        'S_IXGRP': 0o010,
        'S_IRWXO': 0o007,
        'S_IROTH': 0o004,
        'S_IWOTH': 0o002,
        'S_IXOTH': 0o001}

    # defined by the Windows API documentation
    file_attributes = {
        'FILE_ATTRIBUTE_ARCHIVE': 32,
        'FILE_ATTRIBUTE_COMPRESSED': 2048,
        'FILE_ATTRIBUTE_DEVICE': 64,
        'FILE_ATTRIBUTE_DIRECTORY': 16,
        'FILE_ATTRIBUTE_ENCRYPTED': 16384,
        'FILE_ATTRIBUTE_HIDDEN': 2,
        'FILE_ATTRIBUTE_INTEGRITY_STREAM': 32768,
        'FILE_ATTRIBUTE_NORMAL': 128,
        'FILE_ATTRIBUTE_NOT_CONTENT_INDEXED': 8192,
        'FILE_ATTRIBUTE_NO_SCRUB_DATA': 131072,
        'FILE_ATTRIBUTE_OFFLINE': 4096,
        'FILE_ATTRIBUTE_READONLY': 1,
        'FILE_ATTRIBUTE_REPARSE_POINT': 1024,
        'FILE_ATTRIBUTE_SPARSE_FILE': 512,
        'FILE_ATTRIBUTE_SYSTEM': 4,
        'FILE_ATTRIBUTE_TEMPORARY': 256,
        'FILE_ATTRIBUTE_VIRTUAL': 65536}

    def setUp(self):
        spróbuj:
            os.remove(TESTFN)
        wyjąwszy OSError:
            spróbuj:
                os.rmdir(TESTFN)
            wyjąwszy OSError:
                dalej
    tearDown = setUp

    def get_mode(self, fname=TESTFN, lstat=Prawda):
        jeżeli lstat:
            st_mode = os.lstat(fname).st_mode
        inaczej:
            st_mode = os.stat(fname).st_mode
        modestr = self.statmod.filemode(st_mode)
        zwróć st_mode, modestr

    def assertS_IS(self, name, mode):
        # test format, lstrip jest dla S_IFIFO
        fmt = getattr(self.statmod, "S_IF" + name.lstrip("F"))
        self.assertEqual(self.statmod.S_IFMT(mode), fmt)
        # test that just one function returns true
        testname = "S_IS" + name
        dla funcname w self.format_funcs:
            func = getattr(self.statmod, funcname, Nic)
            jeżeli func jest Nic:
                jeżeli funcname == testname:
                    podnieś ValueError(funcname)
                kontynuuj
            jeżeli funcname == testname:
                self.assertPrawda(func(mode))
            inaczej:
                self.assertNieprawda(func(mode))

    def test_mode(self):
        przy open(TESTFN, 'w'):
            dalej
        jeżeli os.name == 'posix':
            os.chmod(TESTFN, 0o700)
            st_mode, modestr = self.get_mode()
            self.assertEqual(modestr, '-rwx------')
            self.assertS_IS("REG", st_mode)
            self.assertEqual(self.statmod.S_IMODE(st_mode),
                             self.statmod.S_IRWXU)

            os.chmod(TESTFN, 0o070)
            st_mode, modestr = self.get_mode()
            self.assertEqual(modestr, '----rwx---')
            self.assertS_IS("REG", st_mode)
            self.assertEqual(self.statmod.S_IMODE(st_mode),
                             self.statmod.S_IRWXG)

            os.chmod(TESTFN, 0o007)
            st_mode, modestr = self.get_mode()
            self.assertEqual(modestr, '-------rwx')
            self.assertS_IS("REG", st_mode)
            self.assertEqual(self.statmod.S_IMODE(st_mode),
                             self.statmod.S_IRWXO)

            os.chmod(TESTFN, 0o444)
            st_mode, modestr = self.get_mode()
            self.assertS_IS("REG", st_mode)
            self.assertEqual(modestr, '-r--r--r--')
            self.assertEqual(self.statmod.S_IMODE(st_mode), 0o444)
        inaczej:
            os.chmod(TESTFN, 0o700)
            st_mode, modestr = self.get_mode()
            self.assertEqual(modestr[:3], '-rw')
            self.assertS_IS("REG", st_mode)
            self.assertEqual(self.statmod.S_IFMT(st_mode),
                             self.statmod.S_IFREG)

    def test_directory(self):
        os.mkdir(TESTFN)
        os.chmod(TESTFN, 0o700)
        st_mode, modestr = self.get_mode()
        self.assertS_IS("DIR", st_mode)
        jeżeli os.name == 'posix':
            self.assertEqual(modestr, 'drwx------')
        inaczej:
            self.assertEqual(modestr[0], 'd')

    @unittest.skipUnless(hasattr(os, 'symlink'), 'os.symlink nie available')
    def test_link(self):
        spróbuj:
            os.symlink(os.getcwd(), TESTFN)
        wyjąwszy (OSError, NotImplementedError) jako err:
            podnieś unittest.SkipTest(str(err))
        inaczej:
            st_mode, modestr = self.get_mode()
            self.assertEqual(modestr[0], 'l')
            self.assertS_IS("LNK", st_mode)

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'os.mkfifo nie available')
    def test_fifo(self):
        os.mkfifo(TESTFN, 0o700)
        st_mode, modestr = self.get_mode()
        self.assertEqual(modestr, 'prwx------')
        self.assertS_IS("FIFO", st_mode)

    @unittest.skipUnless(os.name == 'posix', 'requires Posix')
    def test_devices(self):
        jeżeli os.path.exists(os.devnull):
            st_mode, modestr = self.get_mode(os.devnull, lstat=Nieprawda)
            self.assertEqual(modestr[0], 'c')
            self.assertS_IS("CHR", st_mode)
        # Linux block devices, BSD has no block devices anymore
        dla blockdev w ("/dev/sda", "/dev/hda"):
            jeżeli os.path.exists(blockdev):
                st_mode, modestr = self.get_mode(blockdev, lstat=Nieprawda)
                self.assertEqual(modestr[0], 'b')
                self.assertS_IS("BLK", st_mode)
                przerwij

    def test_module_attributes(self):
        dla key, value w self.stat_struct.items():
            modvalue = getattr(self.statmod, key)
            self.assertEqual(value, modvalue, key)
        dla key, value w self.permission_bits.items():
            modvalue = getattr(self.statmod, key)
            self.assertEqual(value, modvalue, key)
        dla key w self.file_flags:
            modvalue = getattr(self.statmod, key)
            self.assertIsInstance(modvalue, int)
        dla key w self.formats:
            modvalue = getattr(self.statmod, key)
            self.assertIsInstance(modvalue, int)
        dla key w self.format_funcs:
            func = getattr(self.statmod, key)
            self.assertPrawda(callable(func))
            self.assertEqual(func(0), 0)

    @unittest.skipUnless(sys.platform == "win32",
                         "FILE_ATTRIBUTE_* constants are Win32 specific")
    def test_file_attribute_constants(self):
        dla key, value w sorted(self.file_attributes.items()):
            self.assertPrawda(hasattr(self.statmod, key), key)
            modvalue = getattr(self.statmod, key)
            self.assertEqual(value, modvalue, key)


klasa TestFilemodeCStat(TestFilemode, unittest.TestCase):
    statmod = c_stat

    formats = TestFilemode.formats | {'S_IFDOOR', 'S_IFPORT', 'S_IFWHT'}
    format_funcs = TestFilemode.format_funcs | {'S_ISDOOR', 'S_ISPORT',
                                                'S_ISWHT'}


klasa TestFilemodePyStat(TestFilemode, unittest.TestCase):
    statmod = py_stat


jeżeli __name__ == '__main__':
    unittest.main()
