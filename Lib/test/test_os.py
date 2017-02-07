# As a test suite dla the os module, this jest woefully inadequate, but this
# does add tests dla a few functions which have been determined to be more
# portable than they had been thought to be.

zaimportuj asynchat
zaimportuj asyncore
zaimportuj codecs
zaimportuj contextlib
zaimportuj decimal
zaimportuj errno
zaimportuj fractions
zaimportuj getpass
zaimportuj itertools
zaimportuj locale
zaimportuj mmap
zaimportuj os
zaimportuj pickle
zaimportuj platform
zaimportuj re
zaimportuj shutil
zaimportuj signal
zaimportuj socket
zaimportuj stat
zaimportuj subprocess
zaimportuj sys
zaimportuj sysconfig
zaimportuj time
zaimportuj unittest
zaimportuj uuid
zaimportuj warnings
z test zaimportuj support
spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic
spróbuj:
    zaimportuj resource
wyjąwszy ImportError:
    resource = Nic
spróbuj:
    zaimportuj fcntl
wyjąwszy ImportError:
    fcntl = Nic
spróbuj:
    zaimportuj _winapi
wyjąwszy ImportError:
    _winapi = Nic
spróbuj:
    zaimportuj grp
    groups = [g.gr_gid dla g w grp.getgrall() jeżeli getpass.getuser() w g.gr_mem]
    jeżeli hasattr(os, 'getgid'):
        process_gid = os.getgid()
        jeżeli process_gid nie w groups:
            groups.append(process_gid)
wyjąwszy ImportError:
    groups = []
spróbuj:
    zaimportuj pwd
    all_users = [u.pw_uid dla u w pwd.getpwall()]
wyjąwszy ImportError:
    all_users = []
spróbuj:
    z _testcapi zaimportuj INT_MAX, PY_SSIZE_T_MAX
wyjąwszy ImportError:
    INT_MAX = PY_SSIZE_T_MAX = sys.maxsize

z test.support.script_helper zaimportuj assert_python_ok

root_in_posix = Nieprawda
jeżeli hasattr(os, 'geteuid'):
    root_in_posix = (os.geteuid() == 0)

# Detect whether we're on a Linux system that uses the (now outdated
# oraz unmaintained) linuxthreads threading library.  There's an issue
# when combining linuxthreads przy a failed execv call: see
# http://bugs.python.org/issue4970.
jeżeli hasattr(sys, 'thread_info') oraz sys.thread_info.version:
    USING_LINUXTHREADS = sys.thread_info.version.startswith("linuxthreads")
inaczej:
    USING_LINUXTHREADS = Nieprawda

# Issue #14110: Some tests fail on FreeBSD jeżeli the user jest w the wheel group.
HAVE_WHEEL_GROUP = sys.platform.startswith('freebsd') oraz os.getgid() == 0

# Tests creating TESTFN
klasa FileTests(unittest.TestCase):
    def setUp(self):
        jeżeli os.path.exists(support.TESTFN):
            os.unlink(support.TESTFN)
    tearDown = setUp

    def test_access(self):
        f = os.open(support.TESTFN, os.O_CREAT|os.O_RDWR)
        os.close(f)
        self.assertPrawda(os.access(support.TESTFN, os.W_OK))

    def test_closerange(self):
        first = os.open(support.TESTFN, os.O_CREAT|os.O_RDWR)
        # We must allocate two consecutive file descriptors, otherwise
        # it will mess up other file descriptors (perhaps even the three
        # standard ones).
        second = os.dup(first)
        spróbuj:
            retries = 0
            dopóki second != first + 1:
                os.close(first)
                retries += 1
                jeżeli retries > 10:
                    # XXX test skipped
                    self.skipTest("couldn't allocate two consecutive fds")
                first, second = second, os.dup(second)
        w_końcu:
            os.close(second)
        # close a fd that jest open, oraz one that isn't
        os.closerange(first, first + 2)
        self.assertRaises(OSError, os.write, first, b"a")

    @support.cpython_only
    def test_rename(self):
        path = support.TESTFN
        old = sys.getrefcount(path)
        self.assertRaises(TypeError, os.rename, path, 0)
        new = sys.getrefcount(path)
        self.assertEqual(old, new)

    def test_read(self):
        przy open(support.TESTFN, "w+b") jako fobj:
            fobj.write(b"spam")
            fobj.flush()
            fd = fobj.fileno()
            os.lseek(fd, 0, 0)
            s = os.read(fd, 4)
            self.assertEqual(type(s), bytes)
            self.assertEqual(s, b"spam")

    @support.cpython_only
    # Skip the test on 32-bit platforms: the number of bytes must fit w a
    # Py_ssize_t type
    @unittest.skipUnless(INT_MAX < PY_SSIZE_T_MAX,
                         "needs INT_MAX < PY_SSIZE_T_MAX")
    @support.bigmemtest(size=INT_MAX + 10, memuse=1, dry_run=Nieprawda)
    def test_large_read(self, size):
        przy open(support.TESTFN, "wb") jako fp:
            fp.write(b'test')
        self.addCleanup(support.unlink, support.TESTFN)

        # Issue #21932: Make sure that os.read() does nie podnieś an
        # OverflowError dla size larger than INT_MAX
        przy open(support.TESTFN, "rb") jako fp:
            data = os.read(fp.fileno(), size)

        # The test does nie try to read more than 2 GB at once because the
        # operating system jest free to zwróć less bytes than requested.
        self.assertEqual(data, b'test')

    def test_write(self):
        # os.write() accepts bytes- oraz buffer-like objects but nie strings
        fd = os.open(support.TESTFN, os.O_CREAT | os.O_WRONLY)
        self.assertRaises(TypeError, os.write, fd, "beans")
        os.write(fd, b"bacon\n")
        os.write(fd, bytearray(b"eggs\n"))
        os.write(fd, memoryview(b"spam\n"))
        os.close(fd)
        przy open(support.TESTFN, "rb") jako fobj:
            self.assertEqual(fobj.read().splitlines(),
                [b"bacon", b"eggs", b"spam"])

    def write_windows_console(self, *args):
        retcode = subprocess.call(args,
            # use a new console to nie flood the test output
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            # use a shell to hide the console window (SW_HIDE)
            shell=Prawda)
        self.assertEqual(retcode, 0)

    @unittest.skipUnless(sys.platform == 'win32',
                         'test specific to the Windows console')
    def test_write_windows_console(self):
        # Issue #11395: the Windows console returns an error (12: nie enough
        # space error) on writing into stdout jeżeli stdout mode jest binary oraz the
        # length jest greater than 66,000 bytes (or less, depending on heap
        # usage).
        code = "print('x' * 100000)"
        self.write_windows_console(sys.executable, "-c", code)
        self.write_windows_console(sys.executable, "-u", "-c", code)

    def fdopen_helper(self, *args):
        fd = os.open(support.TESTFN, os.O_RDONLY)
        f = os.fdopen(fd, *args)
        f.close()

    def test_fdopen(self):
        fd = os.open(support.TESTFN, os.O_CREAT|os.O_RDWR)
        os.close(fd)

        self.fdopen_helper()
        self.fdopen_helper('r')
        self.fdopen_helper('r', 100)

    def test_replace(self):
        TESTFN2 = support.TESTFN + ".2"
        przy open(support.TESTFN, 'w') jako f:
            f.write("1")
        przy open(TESTFN2, 'w') jako f:
            f.write("2")
        self.addCleanup(os.unlink, TESTFN2)
        os.replace(support.TESTFN, TESTFN2)
        self.assertRaises(FileNotFoundError, os.stat, support.TESTFN)
        przy open(TESTFN2, 'r') jako f:
            self.assertEqual(f.read(), "1")


# Test attributes on zwróć values z os.*stat* family.
klasa StatAttributeTests(unittest.TestCase):
    def setUp(self):
        os.mkdir(support.TESTFN)
        self.fname = os.path.join(support.TESTFN, "f1")
        f = open(self.fname, 'wb')
        f.write(b"ABC")
        f.close()

    def tearDown(self):
        os.unlink(self.fname)
        os.rmdir(support.TESTFN)

    @unittest.skipUnless(hasattr(os, 'stat'), 'test needs os.stat()')
    def check_stat_attributes(self, fname):
        result = os.stat(fname)

        # Make sure direct access works
        self.assertEqual(result[stat.ST_SIZE], 3)
        self.assertEqual(result.st_size, 3)

        # Make sure all the attributes are there
        members = dir(result)
        dla name w dir(stat):
            jeżeli name[:3] == 'ST_':
                attr = name.lower()
                jeżeli name.endswith("TIME"):
                    def trunc(x): zwróć int(x)
                inaczej:
                    def trunc(x): zwróć x
                self.assertEqual(trunc(getattr(result, attr)),
                                  result[getattr(stat, name)])
                self.assertIn(attr, members)

        # Make sure that the st_?time oraz st_?time_ns fields roughly agree
        # (they should always agree up to around tens-of-microseconds)
        dla name w 'st_atime st_mtime st_ctime'.split():
            floaty = int(getattr(result, name) * 100000)
            nanosecondy = getattr(result, name + "_ns") // 10000
            self.assertAlmostEqual(floaty, nanosecondy, delta=2)

        spróbuj:
            result[200]
            self.fail("No exception podnieśd")
        wyjąwszy IndexError:
            dalej

        # Make sure that assignment fails
        spróbuj:
            result.st_mode = 1
            self.fail("No exception podnieśd")
        wyjąwszy AttributeError:
            dalej

        spróbuj:
            result.st_rdev = 1
            self.fail("No exception podnieśd")
        wyjąwszy (AttributeError, TypeError):
            dalej

        spróbuj:
            result.parrot = 1
            self.fail("No exception podnieśd")
        wyjąwszy AttributeError:
            dalej

        # Use the stat_result constructor przy a too-short tuple.
        spróbuj:
            result2 = os.stat_result((10,))
            self.fail("No exception podnieśd")
        wyjąwszy TypeError:
            dalej

        # Use the constructor przy a too-long tuple.
        spróbuj:
            result2 = os.stat_result((0,1,2,3,4,5,6,7,8,9,10,11,12,13,14))
        wyjąwszy TypeError:
            dalej

    def test_stat_attributes(self):
        self.check_stat_attributes(self.fname)

    def test_stat_attributes_bytes(self):
        spróbuj:
            fname = self.fname.encode(sys.getfilesystemencoding())
        wyjąwszy UnicodeEncodeError:
            self.skipTest("cannot encode %a dla the filesystem" % self.fname)
        przy warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.check_stat_attributes(fname)

    def test_stat_result_pickle(self):
        result = os.stat(self.fname)
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            p = pickle.dumps(result, proto)
            self.assertIn(b'stat_result', p)
            jeżeli proto < 4:
                self.assertIn(b'cos\nstat_result\n', p)
            unpickled = pickle.loads(p)
            self.assertEqual(result, unpickled)

    @unittest.skipUnless(hasattr(os, 'statvfs'), 'test needs os.statvfs()')
    def test_statvfs_attributes(self):
        spróbuj:
            result = os.statvfs(self.fname)
        wyjąwszy OSError jako e:
            # On AtheOS, glibc always returns ENOSYS
            jeżeli e.errno == errno.ENOSYS:
                self.skipTest('os.statvfs() failed przy ENOSYS')

        # Make sure direct access works
        self.assertEqual(result.f_bfree, result[3])

        # Make sure all the attributes are there.
        members = ('bsize', 'frsize', 'blocks', 'bfree', 'bavail', 'files',
                    'ffree', 'favail', 'flag', 'namemax')
        dla value, member w enumerate(members):
            self.assertEqual(getattr(result, 'f_' + member), result[value])

        # Make sure that assignment really fails
        spróbuj:
            result.f_bfree = 1
            self.fail("No exception podnieśd")
        wyjąwszy AttributeError:
            dalej

        spróbuj:
            result.parrot = 1
            self.fail("No exception podnieśd")
        wyjąwszy AttributeError:
            dalej

        # Use the constructor przy a too-short tuple.
        spróbuj:
            result2 = os.statvfs_result((10,))
            self.fail("No exception podnieśd")
        wyjąwszy TypeError:
            dalej

        # Use the constructor przy a too-long tuple.
        spróbuj:
            result2 = os.statvfs_result((0,1,2,3,4,5,6,7,8,9,10,11,12,13,14))
        wyjąwszy TypeError:
            dalej

    @unittest.skipUnless(hasattr(os, 'statvfs'),
                         "need os.statvfs()")
    def test_statvfs_result_pickle(self):
        spróbuj:
            result = os.statvfs(self.fname)
        wyjąwszy OSError jako e:
            # On AtheOS, glibc always returns ENOSYS
            jeżeli e.errno == errno.ENOSYS:
                self.skipTest('os.statvfs() failed przy ENOSYS')

        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            p = pickle.dumps(result, proto)
            self.assertIn(b'statvfs_result', p)
            jeżeli proto < 4:
                self.assertIn(b'cos\nstatvfs_result\n', p)
            unpickled = pickle.loads(p)
            self.assertEqual(result, unpickled)

    @unittest.skipUnless(sys.platform == "win32", "Win32 specific tests")
    def test_1686475(self):
        # Verify that an open file can be stat'ed
        spróbuj:
            os.stat(r"c:\pagefile.sys")
        wyjąwszy FileNotFoundError:
            self.skipTest(r'c:\pagefile.sys does nie exist')
        wyjąwszy OSError jako e:
            self.fail("Could nie stat pagefile.sys")

    @unittest.skipUnless(sys.platform == "win32", "Win32 specific tests")
    @unittest.skipUnless(hasattr(os, "pipe"), "requires os.pipe()")
    def test_15261(self):
        # Verify that stat'ing a closed fd does nie cause crash
        r, w = os.pipe()
        spróbuj:
            os.stat(r)          # should nie podnieś error
        w_końcu:
            os.close(r)
            os.close(w)
        przy self.assertRaises(OSError) jako ctx:
            os.stat(r)
        self.assertEqual(ctx.exception.errno, errno.EBADF)

    def check_file_attributes(self, result):
        self.assertPrawda(hasattr(result, 'st_file_attributes'))
        self.assertPrawda(isinstance(result.st_file_attributes, int))
        self.assertPrawda(0 <= result.st_file_attributes <= 0xFFFFFFFF)

    @unittest.skipUnless(sys.platform == "win32",
                         "st_file_attributes jest Win32 specific")
    def test_file_attributes(self):
        # test file st_file_attributes (FILE_ATTRIBUTE_DIRECTORY nie set)
        result = os.stat(self.fname)
        self.check_file_attributes(result)
        self.assertEqual(
            result.st_file_attributes & stat.FILE_ATTRIBUTE_DIRECTORY,
            0)

        # test directory st_file_attributes (FILE_ATTRIBUTE_DIRECTORY set)
        result = os.stat(support.TESTFN)
        self.check_file_attributes(result)
        self.assertEqual(
            result.st_file_attributes & stat.FILE_ATTRIBUTE_DIRECTORY,
            stat.FILE_ATTRIBUTE_DIRECTORY)


klasa UtimeTests(unittest.TestCase):
    def setUp(self):
        self.dirname = support.TESTFN
        self.fname = os.path.join(self.dirname, "f1")

        self.addCleanup(support.rmtree, self.dirname)
        os.mkdir(self.dirname)
        przy open(self.fname, 'wb') jako fp:
            fp.write(b"ABC")

        def restore_float_times(state):
            przy warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)

                os.stat_float_times(state)

        # ensure that st_atime oraz st_mtime are float
        przy warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)

            old_float_times = os.stat_float_times(-1)
            self.addCleanup(restore_float_times, old_float_times)

            os.stat_float_times(Prawda)

    def support_subsecond(self, filename):
        # Heuristic to check jeżeli the filesystem supports timestamp with
        # subsecond resolution: check jeżeli float oraz int timestamps are different
        st = os.stat(filename)
        zwróć ((st.st_atime != st[7])
                albo (st.st_mtime != st[8])
                albo (st.st_ctime != st[9]))

    def _test_utime(self, set_time, filename=Nic):
        jeżeli nie filename:
            filename = self.fname

        support_subsecond = self.support_subsecond(filename)
        jeżeli support_subsecond:
            # Timestamp przy a resolution of 1 microsecond (10^-6).
            #
            # The resolution of the C internal function used by os.utime()
            # depends on the platform: 1 sec, 1 us, 1 ns. Writing a portable
            # test przy a resolution of 1 ns requires more work:
            # see the issue #15745.
            atime_ns = 1002003000   # 1.002003 seconds
            mtime_ns = 4005006000   # 4.005006 seconds
        inaczej:
            # use a resolution of 1 second
            atime_ns = 5 * 10**9
            mtime_ns = 8 * 10**9

        set_time(filename, (atime_ns, mtime_ns))
        st = os.stat(filename)

        jeżeli support_subsecond:
            self.assertAlmostEqual(st.st_atime, atime_ns * 1e-9, delta=1e-6)
            self.assertAlmostEqual(st.st_mtime, mtime_ns * 1e-9, delta=1e-6)
        inaczej:
            self.assertEqual(st.st_atime, atime_ns * 1e-9)
            self.assertEqual(st.st_mtime, mtime_ns * 1e-9)
        self.assertEqual(st.st_atime_ns, atime_ns)
        self.assertEqual(st.st_mtime_ns, mtime_ns)

    def test_utime(self):
        def set_time(filename, ns):
            # test the ns keyword parameter
            os.utime(filename, ns=ns)
        self._test_utime(set_time)

    @staticmethod
    def ns_to_sec(ns):
        # Convert a number of nanosecond (int) to a number of seconds (float).
        # Round towards infinity by adding 0.5 nanosecond to avoid rounding
        # issue, os.utime() rounds towards minus infinity.
        zwróć (ns * 1e-9) + 0.5e-9

    def test_utime_by_indexed(self):
        # dalej times jako floating point seconds jako the second indexed parameter
        def set_time(filename, ns):
            atime_ns, mtime_ns = ns
            atime = self.ns_to_sec(atime_ns)
            mtime = self.ns_to_sec(mtime_ns)
            # test utimensat(timespec), utimes(timeval), utime(utimbuf)
            # albo utime(time_t)
            os.utime(filename, (atime, mtime))
        self._test_utime(set_time)

    def test_utime_by_times(self):
        def set_time(filename, ns):
            atime_ns, mtime_ns = ns
            atime = self.ns_to_sec(atime_ns)
            mtime = self.ns_to_sec(mtime_ns)
            # test the times keyword parameter
            os.utime(filename, times=(atime, mtime))
        self._test_utime(set_time)

    @unittest.skipUnless(os.utime w os.supports_follow_symlinks,
                         "follow_symlinks support dla utime required "
                         "dla this test.")
    def test_utime_nofollow_symlinks(self):
        def set_time(filename, ns):
            # use follow_symlinks=Nieprawda to test utimensat(timespec)
            # albo lutimes(timeval)
            os.utime(filename, ns=ns, follow_symlinks=Nieprawda)
        self._test_utime(set_time)

    @unittest.skipUnless(os.utime w os.supports_fd,
                         "fd support dla utime required dla this test.")
    def test_utime_fd(self):
        def set_time(filename, ns):
            przy open(filename, 'wb') jako fp:
                # use a file descriptor to test futimens(timespec)
                # albo futimes(timeval)
                os.utime(fp.fileno(), ns=ns)
        self._test_utime(set_time)

    @unittest.skipUnless(os.utime w os.supports_dir_fd,
                         "dir_fd support dla utime required dla this test.")
    def test_utime_dir_fd(self):
        def set_time(filename, ns):
            dirname, name = os.path.split(filename)
            dirfd = os.open(dirname, os.O_RDONLY)
            spróbuj:
                # dalej dir_fd to test utimensat(timespec) albo futimesat(timeval)
                os.utime(name, dir_fd=dirfd, ns=ns)
            w_końcu:
                os.close(dirfd)
        self._test_utime(set_time)

    def test_utime_directory(self):
        def set_time(filename, ns):
            # test calling os.utime() on a directory
            os.utime(filename, ns=ns)
        self._test_utime(set_time, filename=self.dirname)

    def _test_utime_current(self, set_time):
        # Get the system clock
        current = time.time()

        # Call os.utime() to set the timestamp to the current system clock
        set_time(self.fname)

        jeżeli nie self.support_subsecond(self.fname):
            delta = 1.0
        inaczej:
            # On Windows, the usual resolution of time.time() jest 15.6 ms
            delta = 0.020
        st = os.stat(self.fname)
        msg = ("st_time=%r, current=%r, dt=%r"
               % (st.st_mtime, current, st.st_mtime - current))
        self.assertAlmostEqual(st.st_mtime, current,
                               delta=delta, msg=msg)

    def test_utime_current(self):
        def set_time(filename):
            # Set to the current time w the new way
            os.utime(self.fname)
        self._test_utime_current(set_time)

    def test_utime_current_old(self):
        def set_time(filename):
            # Set to the current time w the old explicit way.
            os.utime(self.fname, Nic)
        self._test_utime_current(set_time)

    def get_file_system(self, path):
        jeżeli sys.platform == 'win32':
            root = os.path.splitdrive(os.path.abspath(path))[0] + '\\'
            zaimportuj ctypes
            kernel32 = ctypes.windll.kernel32
            buf = ctypes.create_unicode_buffer("", 100)
            ok = kernel32.GetVolumeInformationW(root, Nic, 0,
                                                Nic, Nic, Nic,
                                                buf, len(buf))
            jeżeli ok:
                zwróć buf.value
        # zwróć Nic jeżeli the filesystem jest unknown

    def test_large_time(self):
        # Many filesystems are limited to the year 2038. At least, the test
        # dalej przy NTFS filesystem.
        jeżeli self.get_file_system(self.dirname) != "NTFS":
            self.skipTest("requires NTFS")

        large = 5000000000   # some day w 2128
        os.utime(self.fname, (large, large))
        self.assertEqual(os.stat(self.fname).st_mtime, large)

    def test_utime_invalid_arguments(self):
        # seconds oraz nanoseconds parameters are mutually exclusive
        przy self.assertRaises(ValueError):
            os.utime(self.fname, (5, 5), ns=(5, 5))


z test zaimportuj mapping_tests

klasa EnvironTests(mapping_tests.BasicTestMappingProtocol):
    """check that os.environ object conform to mapping protocol"""
    type2test = Nic

    def setUp(self):
        self.__save = dict(os.environ)
        jeżeli os.supports_bytes_environ:
            self.__saveb = dict(os.environb)
        dla key, value w self._reference().items():
            os.environ[key] = value

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.__save)
        jeżeli os.supports_bytes_environ:
            os.environb.clear()
            os.environb.update(self.__saveb)

    def _reference(self):
        zwróć {"KEY1":"VALUE1", "KEY2":"VALUE2", "KEY3":"VALUE3"}

    def _empty_mapping(self):
        os.environ.clear()
        zwróć os.environ

    # Bug 1110478
    @unittest.skipUnless(os.path.exists('/bin/sh'), 'requires /bin/sh')
    def test_update2(self):
        os.environ.clear()
        os.environ.update(HELLO="World")
        przy os.popen("/bin/sh -c 'echo $HELLO'") jako popen:
            value = popen.read().strip()
            self.assertEqual(value, "World")

    @unittest.skipUnless(os.path.exists('/bin/sh'), 'requires /bin/sh')
    def test_os_popen_iter(self):
        przy os.popen(
            "/bin/sh -c 'echo \"line1\nline2\nline3\"'") jako popen:
            it = iter(popen)
            self.assertEqual(next(it), "line1\n")
            self.assertEqual(next(it), "line2\n")
            self.assertEqual(next(it), "line3\n")
            self.assertRaises(StopIteration, next, it)

    # Verify environ keys oraz values z the OS are of the
    # correct str type.
    def test_keyvalue_types(self):
        dla key, val w os.environ.items():
            self.assertEqual(type(key), str)
            self.assertEqual(type(val), str)

    def test_items(self):
        dla key, value w self._reference().items():
            self.assertEqual(os.environ.get(key), value)

    # Issue 7310
    def test___repr__(self):
        """Check that the repr() of os.environ looks like environ({...})."""
        env = os.environ
        self.assertEqual(repr(env), 'environ({{{}}})'.format(', '.join(
            '{!r}: {!r}'.format(key, value)
            dla key, value w env.items())))

    def test_get_exec_path(self):
        defpath_list = os.defpath.split(os.pathsep)
        test_path = ['/monty', '/python', '', '/flying/circus']
        test_env = {'PATH': os.pathsep.join(test_path)}

        saved_environ = os.environ
        spróbuj:
            os.environ = dict(test_env)
            # Test that defaulting to os.environ works.
            self.assertSequenceEqual(test_path, os.get_exec_path())
            self.assertSequenceEqual(test_path, os.get_exec_path(env=Nic))
        w_końcu:
            os.environ = saved_environ

        # No PATH environment variable
        self.assertSequenceEqual(defpath_list, os.get_exec_path({}))
        # Empty PATH environment variable
        self.assertSequenceEqual(('',), os.get_exec_path({'PATH':''}))
        # Supplied PATH environment variable
        self.assertSequenceEqual(test_path, os.get_exec_path(test_env))

        jeżeli os.supports_bytes_environ:
            # env cannot contain 'PATH' oraz b'PATH' keys
            spróbuj:
                # ignore BytesWarning warning
                przy warnings.catch_warnings(record=Prawda):
                    mixed_env = {'PATH': '1', b'PATH': b'2'}
            wyjąwszy BytesWarning:
                # mixed_env cannot be created przy python -bb
                dalej
            inaczej:
                self.assertRaises(ValueError, os.get_exec_path, mixed_env)

            # bytes key and/or value
            self.assertSequenceEqual(os.get_exec_path({b'PATH': b'abc'}),
                ['abc'])
            self.assertSequenceEqual(os.get_exec_path({b'PATH': 'abc'}),
                ['abc'])
            self.assertSequenceEqual(os.get_exec_path({'PATH': b'abc'}),
                ['abc'])

    @unittest.skipUnless(os.supports_bytes_environ,
                         "os.environb required dla this test.")
    def test_environb(self):
        # os.environ -> os.environb
        value = 'euro\u20ac'
        spróbuj:
            value_bytes = value.encode(sys.getfilesystemencoding(),
                                       'surrogateescape')
        wyjąwszy UnicodeEncodeError:
            msg = "U+20AC character jest nie encodable to %s" % (
                sys.getfilesystemencoding(),)
            self.skipTest(msg)
        os.environ['unicode'] = value
        self.assertEqual(os.environ['unicode'], value)
        self.assertEqual(os.environb[b'unicode'], value_bytes)

        # os.environb -> os.environ
        value = b'\xff'
        os.environb[b'bytes'] = value
        self.assertEqual(os.environb[b'bytes'], value)
        value_str = value.decode(sys.getfilesystemencoding(), 'surrogateescape')
        self.assertEqual(os.environ['bytes'], value_str)

    # On FreeBSD < 7 oraz OS X < 10.6, unsetenv() doesn't zwróć a value (issue
    # #13415).
    @support.requires_freebsd_version(7)
    @support.requires_mac_ver(10, 6)
    def test_unset_error(self):
        jeżeli sys.platform == "win32":
            # an environment variable jest limited to 32,767 characters
            key = 'x' * 50000
            self.assertRaises(ValueError, os.environ.__delitem__, key)
        inaczej:
            # "=" jest nie allowed w a variable name
            key = 'key='
            self.assertRaises(OSError, os.environ.__delitem__, key)

    def test_key_type(self):
        missing = 'missingkey'
        self.assertNotIn(missing, os.environ)

        przy self.assertRaises(KeyError) jako cm:
            os.environ[missing]
        self.assertIs(cm.exception.args[0], missing)
        self.assertPrawda(cm.exception.__suppress_context__)

        przy self.assertRaises(KeyError) jako cm:
            usuń os.environ[missing]
        self.assertIs(cm.exception.args[0], missing)
        self.assertPrawda(cm.exception.__suppress_context__)


klasa WalkTests(unittest.TestCase):
    """Tests dla os.walk()."""

    # Wrapper to hide minor differences between os.walk oraz os.fwalk
    # to tests both functions przy the same code base
    def walk(self, directory, topdown=Prawda, follow_symlinks=Nieprawda):
        walk_it = os.walk(directory,
                          topdown=topdown,
                          followlinks=follow_symlinks)
        dla root, dirs, files w walk_it:
            uzyskaj (root, dirs, files)

    def setUp(self):
        join = os.path.join

        # Build:
        #     TESTFN/
        #       TEST1/              a file kid oraz two directory kids
        #         tmp1
        #         SUB1/             a file kid oraz a directory kid
        #           tmp2
        #           SUB11/          no kids
        #         SUB2/             a file kid oraz a dirsymlink kid
        #           tmp3
        #           link/           a symlink to TESTFN.2
        #           broken_link
        #       TEST2/
        #         tmp4              a lone file
        self.walk_path = join(support.TESTFN, "TEST1")
        self.sub1_path = join(self.walk_path, "SUB1")
        self.sub11_path = join(self.sub1_path, "SUB11")
        sub2_path = join(self.walk_path, "SUB2")
        tmp1_path = join(self.walk_path, "tmp1")
        tmp2_path = join(self.sub1_path, "tmp2")
        tmp3_path = join(sub2_path, "tmp3")
        self.link_path = join(sub2_path, "link")
        t2_path = join(support.TESTFN, "TEST2")
        tmp4_path = join(support.TESTFN, "TEST2", "tmp4")
        broken_link_path = join(sub2_path, "broken_link")

        # Create stuff.
        os.makedirs(self.sub11_path)
        os.makedirs(sub2_path)
        os.makedirs(t2_path)

        dla path w tmp1_path, tmp2_path, tmp3_path, tmp4_path:
            f = open(path, "w")
            f.write("I'm " + path + " oraz proud of it.  Blame test_os.\n")
            f.close()

        jeżeli support.can_symlink():
            os.symlink(os.path.abspath(t2_path), self.link_path)
            os.symlink('broken', broken_link_path, Prawda)
            self.sub2_tree = (sub2_path, ["link"], ["broken_link", "tmp3"])
        inaczej:
            self.sub2_tree = (sub2_path, [], ["tmp3"])

    def test_walk_topdown(self):
        # Walk top-down.
        all = list(os.walk(self.walk_path))

        self.assertEqual(len(all), 4)
        # We can't know which order SUB1 oraz SUB2 will appear in.
        # Not flipped:  TESTFN, SUB1, SUB11, SUB2
        #     flipped:  TESTFN, SUB2, SUB1, SUB11
        flipped = all[0][1][0] != "SUB1"
        all[0][1].sort()
        all[3 - 2 * flipped][-1].sort()
        self.assertEqual(all[0], (self.walk_path, ["SUB1", "SUB2"], ["tmp1"]))
        self.assertEqual(all[1 + flipped], (self.sub1_path, ["SUB11"], ["tmp2"]))
        self.assertEqual(all[2 + flipped], (self.sub11_path, [], []))
        self.assertEqual(all[3 - 2 * flipped], self.sub2_tree)

    def test_walk_prune(self):
        # Prune the search.
        all = []
        dla root, dirs, files w self.walk(self.walk_path):
            all.append((root, dirs, files))
            # Don't descend into SUB1.
            jeżeli 'SUB1' w dirs:
                # Note that this also mutates the dirs we appended to all!
                dirs.remove('SUB1')

        self.assertEqual(len(all), 2)
        self.assertEqual(all[0],
                         (self.walk_path, ["SUB2"], ["tmp1"]))

        all[1][-1].sort()
        self.assertEqual(all[1], self.sub2_tree)

    def test_walk_bottom_up(self):
        # Walk bottom-up.
        all = list(self.walk(self.walk_path, topdown=Nieprawda))

        self.assertEqual(len(all), 4)
        # We can't know which order SUB1 oraz SUB2 will appear in.
        # Not flipped:  SUB11, SUB1, SUB2, TESTFN
        #     flipped:  SUB2, SUB11, SUB1, TESTFN
        flipped = all[3][1][0] != "SUB1"
        all[3][1].sort()
        all[2 - 2 * flipped][-1].sort()
        self.assertEqual(all[3],
                         (self.walk_path, ["SUB1", "SUB2"], ["tmp1"]))
        self.assertEqual(all[flipped],
                         (self.sub11_path, [], []))
        self.assertEqual(all[flipped + 1],
                         (self.sub1_path, ["SUB11"], ["tmp2"]))
        self.assertEqual(all[2 - 2 * flipped],
                         self.sub2_tree)

    def test_walk_symlink(self):
        jeżeli nie support.can_symlink():
            self.skipTest("need symlink support")

        # Walk, following symlinks.
        walk_it = self.walk(self.walk_path, follow_symlinks=Prawda)
        dla root, dirs, files w walk_it:
            jeżeli root == self.link_path:
                self.assertEqual(dirs, [])
                self.assertEqual(files, ["tmp4"])
                przerwij
        inaczej:
            self.fail("Didn't follow symlink przy followlinks=Prawda")

    def tearDown(self):
        # Tear everything down.  This jest a decent use dla bottom-up on
        # Windows, which doesn't have a recursive delete command.  The
        # (nie so) subtlety jest that rmdir will fail unless the dir's
        # kids are removed first, so bottom up jest essential.
        dla root, dirs, files w os.walk(support.TESTFN, topdown=Nieprawda):
            dla name w files:
                os.remove(os.path.join(root, name))
            dla name w dirs:
                dirname = os.path.join(root, name)
                jeżeli nie os.path.islink(dirname):
                    os.rmdir(dirname)
                inaczej:
                    os.remove(dirname)
        os.rmdir(support.TESTFN)


@unittest.skipUnless(hasattr(os, 'fwalk'), "Test needs os.fwalk()")
klasa FwalkTests(WalkTests):
    """Tests dla os.fwalk()."""

    def walk(self, directory, topdown=Prawda, follow_symlinks=Nieprawda):
        walk_it = os.fwalk(directory,
                           topdown=topdown,
                           follow_symlinks=follow_symlinks)
        dla root, dirs, files, root_fd w walk_it:
            uzyskaj (root, dirs, files)


    def _compare_to_walk(self, walk_kwargs, fwalk_kwargs):
        """
        compare przy walk() results.
        """
        walk_kwargs = walk_kwargs.copy()
        fwalk_kwargs = fwalk_kwargs.copy()
        dla topdown, follow_symlinks w itertools.product((Prawda, Nieprawda), repeat=2):
            walk_kwargs.update(topdown=topdown, followlinks=follow_symlinks)
            fwalk_kwargs.update(topdown=topdown, follow_symlinks=follow_symlinks)

            expected = {}
            dla root, dirs, files w os.walk(**walk_kwargs):
                expected[root] = (set(dirs), set(files))

            dla root, dirs, files, rootfd w os.fwalk(**fwalk_kwargs):
                self.assertIn(root, expected)
                self.assertEqual(expected[root], (set(dirs), set(files)))

    def test_compare_to_walk(self):
        kwargs = {'top': support.TESTFN}
        self._compare_to_walk(kwargs, kwargs)

    def test_dir_fd(self):
        spróbuj:
            fd = os.open(".", os.O_RDONLY)
            walk_kwargs = {'top': support.TESTFN}
            fwalk_kwargs = walk_kwargs.copy()
            fwalk_kwargs['dir_fd'] = fd
            self._compare_to_walk(walk_kwargs, fwalk_kwargs)
        w_końcu:
            os.close(fd)

    def test_uzyskajs_correct_dir_fd(self):
        # check returned file descriptors
        dla topdown, follow_symlinks w itertools.product((Prawda, Nieprawda), repeat=2):
            args = support.TESTFN, topdown, Nic
            dla root, dirs, files, rootfd w os.fwalk(*args, follow_symlinks=follow_symlinks):
                # check that the FD jest valid
                os.fstat(rootfd)
                # redundant check
                os.stat(rootfd)
                # check that listdir() returns consistent information
                self.assertEqual(set(os.listdir(rootfd)), set(dirs) | set(files))

    def test_fd_leak(self):
        # Since we're opening a lot of FDs, we must be careful to avoid leaks:
        # we both check that calling fwalk() a large number of times doesn't
        # uzyskaj EMFILE, oraz that the minimum allocated FD hasn't changed.
        minfd = os.dup(1)
        os.close(minfd)
        dla i w range(256):
            dla x w os.fwalk(support.TESTFN):
                dalej
        newfd = os.dup(1)
        self.addCleanup(os.close, newfd)
        self.assertEqual(newfd, minfd)

    def tearDown(self):
        # cleanup
        dla root, dirs, files, rootfd w os.fwalk(support.TESTFN, topdown=Nieprawda):
            dla name w files:
                os.unlink(name, dir_fd=rootfd)
            dla name w dirs:
                st = os.stat(name, dir_fd=rootfd, follow_symlinks=Nieprawda)
                jeżeli stat.S_ISDIR(st.st_mode):
                    os.rmdir(name, dir_fd=rootfd)
                inaczej:
                    os.unlink(name, dir_fd=rootfd)
        os.rmdir(support.TESTFN)


klasa MakedirTests(unittest.TestCase):
    def setUp(self):
        os.mkdir(support.TESTFN)

    def test_makedir(self):
        base = support.TESTFN
        path = os.path.join(base, 'dir1', 'dir2', 'dir3')
        os.makedirs(path)             # Should work
        path = os.path.join(base, 'dir1', 'dir2', 'dir3', 'dir4')
        os.makedirs(path)

        # Try paths przy a '.' w them
        self.assertRaises(OSError, os.makedirs, os.curdir)
        path = os.path.join(base, 'dir1', 'dir2', 'dir3', 'dir4', 'dir5', os.curdir)
        os.makedirs(path)
        path = os.path.join(base, 'dir1', os.curdir, 'dir2', 'dir3', 'dir4',
                            'dir5', 'dir6')
        os.makedirs(path)

    def test_exist_ok_existing_directory(self):
        path = os.path.join(support.TESTFN, 'dir1')
        mode = 0o777
        old_mask = os.umask(0o022)
        os.makedirs(path, mode)
        self.assertRaises(OSError, os.makedirs, path, mode)
        self.assertRaises(OSError, os.makedirs, path, mode, exist_ok=Nieprawda)
        os.makedirs(path, 0o776, exist_ok=Prawda)
        os.makedirs(path, mode=mode, exist_ok=Prawda)
        os.umask(old_mask)

    def test_exist_ok_s_isgid_directory(self):
        path = os.path.join(support.TESTFN, 'dir1')
        S_ISGID = stat.S_ISGID
        mode = 0o777
        old_mask = os.umask(0o022)
        spróbuj:
            existing_testfn_mode = stat.S_IMODE(
                    os.lstat(support.TESTFN).st_mode)
            spróbuj:
                os.chmod(support.TESTFN, existing_testfn_mode | S_ISGID)
            wyjąwszy PermissionError:
                podnieś unittest.SkipTest('Cannot set S_ISGID dla dir.')
            jeżeli (os.lstat(support.TESTFN).st_mode & S_ISGID != S_ISGID):
                podnieś unittest.SkipTest('No support dla S_ISGID dir mode.')
            # The os should apply S_ISGID z the parent dir dla us, but
            # this test need nie depend on that behavior.  Be explicit.
            os.makedirs(path, mode | S_ISGID)
            # http://bugs.python.org/issue14992
            # Should nie fail when the bit jest already set.
            os.makedirs(path, mode, exist_ok=Prawda)
            # remove the bit.
            os.chmod(path, stat.S_IMODE(os.lstat(path).st_mode) & ~S_ISGID)
            # May work even when the bit jest nie already set when demanded.
            os.makedirs(path, mode | S_ISGID, exist_ok=Prawda)
        w_końcu:
            os.umask(old_mask)

    def test_exist_ok_existing_regular_file(self):
        base = support.TESTFN
        path = os.path.join(support.TESTFN, 'dir1')
        f = open(path, 'w')
        f.write('abc')
        f.close()
        self.assertRaises(OSError, os.makedirs, path)
        self.assertRaises(OSError, os.makedirs, path, exist_ok=Nieprawda)
        self.assertRaises(OSError, os.makedirs, path, exist_ok=Prawda)
        os.remove(path)

    def tearDown(self):
        path = os.path.join(support.TESTFN, 'dir1', 'dir2', 'dir3',
                            'dir4', 'dir5', 'dir6')
        # If the tests failed, the bottom-most directory ('../dir6')
        # may nie have been created, so we look dla the outermost directory
        # that exists.
        dopóki nie os.path.exists(path) oraz path != support.TESTFN:
            path = os.path.dirname(path)

        os.removedirs(path)


@unittest.skipUnless(hasattr(os, 'chown'), "Test needs chown")
klasa ChownFileTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.mkdir(support.TESTFN)

    def test_chown_uid_gid_arguments_must_be_index(self):
        stat = os.stat(support.TESTFN)
        uid = stat.st_uid
        gid = stat.st_gid
        dla value w (-1.0, -1j, decimal.Decimal(-1), fractions.Fraction(-2, 2)):
            self.assertRaises(TypeError, os.chown, support.TESTFN, value, gid)
            self.assertRaises(TypeError, os.chown, support.TESTFN, uid, value)
        self.assertIsNic(os.chown(support.TESTFN, uid, gid))
        self.assertIsNic(os.chown(support.TESTFN, -1, -1))

    @unittest.skipUnless(len(groups) > 1, "test needs more than one group")
    def test_chown(self):
        gid_1, gid_2 = groups[:2]
        uid = os.stat(support.TESTFN).st_uid
        os.chown(support.TESTFN, uid, gid_1)
        gid = os.stat(support.TESTFN).st_gid
        self.assertEqual(gid, gid_1)
        os.chown(support.TESTFN, uid, gid_2)
        gid = os.stat(support.TESTFN).st_gid
        self.assertEqual(gid, gid_2)

    @unittest.skipUnless(root_in_posix oraz len(all_users) > 1,
                         "test needs root privilege oraz more than one user")
    def test_chown_with_root(self):
        uid_1, uid_2 = all_users[:2]
        gid = os.stat(support.TESTFN).st_gid
        os.chown(support.TESTFN, uid_1, gid)
        uid = os.stat(support.TESTFN).st_uid
        self.assertEqual(uid, uid_1)
        os.chown(support.TESTFN, uid_2, gid)
        uid = os.stat(support.TESTFN).st_uid
        self.assertEqual(uid, uid_2)

    @unittest.skipUnless(nie root_in_posix oraz len(all_users) > 1,
                         "test needs non-root account oraz more than one user")
    def test_chown_without_permission(self):
        uid_1, uid_2 = all_users[:2]
        gid = os.stat(support.TESTFN).st_gid
        przy self.assertRaises(PermissionError):
            os.chown(support.TESTFN, uid_1, gid)
            os.chown(support.TESTFN, uid_2, gid)

    @classmethod
    def tearDownClass(cls):
        os.rmdir(support.TESTFN)


klasa RemoveDirsTests(unittest.TestCase):
    def setUp(self):
        os.makedirs(support.TESTFN)

    def tearDown(self):
        support.rmtree(support.TESTFN)

    def test_remove_all(self):
        dira = os.path.join(support.TESTFN, 'dira')
        os.mkdir(dira)
        dirb = os.path.join(dira, 'dirb')
        os.mkdir(dirb)
        os.removedirs(dirb)
        self.assertNieprawda(os.path.exists(dirb))
        self.assertNieprawda(os.path.exists(dira))
        self.assertNieprawda(os.path.exists(support.TESTFN))

    def test_remove_partial(self):
        dira = os.path.join(support.TESTFN, 'dira')
        os.mkdir(dira)
        dirb = os.path.join(dira, 'dirb')
        os.mkdir(dirb)
        przy open(os.path.join(dira, 'file.txt'), 'w') jako f:
            f.write('text')
        os.removedirs(dirb)
        self.assertNieprawda(os.path.exists(dirb))
        self.assertPrawda(os.path.exists(dira))
        self.assertPrawda(os.path.exists(support.TESTFN))

    def test_remove_nothing(self):
        dira = os.path.join(support.TESTFN, 'dira')
        os.mkdir(dira)
        dirb = os.path.join(dira, 'dirb')
        os.mkdir(dirb)
        przy open(os.path.join(dirb, 'file.txt'), 'w') jako f:
            f.write('text')
        przy self.assertRaises(OSError):
            os.removedirs(dirb)
        self.assertPrawda(os.path.exists(dirb))
        self.assertPrawda(os.path.exists(dira))
        self.assertPrawda(os.path.exists(support.TESTFN))


klasa DevNullTests(unittest.TestCase):
    def test_devnull(self):
        przy open(os.devnull, 'wb') jako f:
            f.write(b'hello')
            f.close()
        przy open(os.devnull, 'rb') jako f:
            self.assertEqual(f.read(), b'')


klasa URandomTests(unittest.TestCase):
    def test_urandom_length(self):
        self.assertEqual(len(os.urandom(0)), 0)
        self.assertEqual(len(os.urandom(1)), 1)
        self.assertEqual(len(os.urandom(10)), 10)
        self.assertEqual(len(os.urandom(100)), 100)
        self.assertEqual(len(os.urandom(1000)), 1000)

    def test_urandom_value(self):
        data1 = os.urandom(16)
        data2 = os.urandom(16)
        self.assertNotEqual(data1, data2)

    def get_urandom_subprocess(self, count):
        code = '\n'.join((
            'zaimportuj os, sys',
            'data = os.urandom(%s)' % count,
            'sys.stdout.buffer.write(data)',
            'sys.stdout.buffer.flush()'))
        out = assert_python_ok('-c', code)
        stdout = out[1]
        self.assertEqual(len(stdout), 16)
        zwróć stdout

    def test_urandom_subprocess(self):
        data1 = self.get_urandom_subprocess(16)
        data2 = self.get_urandom_subprocess(16)
        self.assertNotEqual(data1, data2)


HAVE_GETENTROPY = (sysconfig.get_config_var('HAVE_GETENTROPY') == 1)
HAVE_GETRANDOM = (sysconfig.get_config_var('HAVE_GETRANDOM_SYSCALL') == 1)

@unittest.skipIf(HAVE_GETENTROPY,
                 "getentropy() does nie use a file descriptor")
@unittest.skipIf(HAVE_GETRANDOM,
                 "getrandom() does nie use a file descriptor")
klasa URandomFDTests(unittest.TestCase):
    @unittest.skipUnless(resource, "test requires the resource module")
    def test_urandom_failure(self):
        # Check urandom() failing when it jest nie able to open /dev/random.
        # We spawn a new process to make the test more robust (jeżeli getrlimit()
        # failed to restore the file descriptor limit after this, the whole
        # test suite would crash; this actually happened on the OS X Tiger
        # buildbot).
        code = """jeżeli 1:
            zaimportuj errno
            zaimportuj os
            zaimportuj resource

            soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
            resource.setrlimit(resource.RLIMIT_NOFILE, (1, hard_limit))
            spróbuj:
                os.urandom(16)
            wyjąwszy OSError jako e:
                assert e.errno == errno.EMFILE, e.errno
            inaczej:
                podnieś AssertionError("OSError nie podnieśd")
            """
        assert_python_ok('-c', code)

    def test_urandom_fd_closed(self):
        # Issue #21207: urandom() should reopen its fd to /dev/urandom if
        # closed.
        code = """jeżeli 1:
            zaimportuj os
            zaimportuj sys
            zaimportuj test.support
            os.urandom(4)
            przy test.support.SuppressCrashReport():
                os.closerange(3, 256)
            sys.stdout.buffer.write(os.urandom(4))
            """
        rc, out, err = assert_python_ok('-Sc', code)

    def test_urandom_fd_reopened(self):
        # Issue #21207: urandom() should detect its fd to /dev/urandom
        # changed to something inaczej, oraz reopen it.
        przy open(support.TESTFN, 'wb') jako f:
            f.write(b"x" * 256)
        self.addCleanup(os.unlink, support.TESTFN)
        code = """jeżeli 1:
            zaimportuj os
            zaimportuj sys
            zaimportuj test.support
            os.urandom(4)
            przy test.support.SuppressCrashReport():
                dla fd w range(3, 256):
                    spróbuj:
                        os.close(fd)
                    wyjąwszy OSError:
                        dalej
                    inaczej:
                        # Found the urandom fd (XXX hopefully)
                        przerwij
                os.closerange(3, 256)
            przy open({TESTFN!r}, 'rb') jako f:
                os.dup2(f.fileno(), fd)
                sys.stdout.buffer.write(os.urandom(4))
                sys.stdout.buffer.write(os.urandom(4))
            """.format(TESTFN=support.TESTFN)
        rc, out, err = assert_python_ok('-Sc', code)
        self.assertEqual(len(out), 8)
        self.assertNotEqual(out[0:4], out[4:8])
        rc, out2, err2 = assert_python_ok('-Sc', code)
        self.assertEqual(len(out2), 8)
        self.assertNotEqual(out2, out)


@contextlib.contextmanager
def _execvpe_mockup(defpath=Nic):
    """
    Stubs out execv oraz execve functions when used jako context manager.
    Records exec calls. The mock execv oraz execve functions always podnieś an
    exception jako they would normally never return.
    """
    # A list of tuples containing (function name, first arg, args)
    # of calls to execv albo execve that have been made.
    calls = []

    def mock_execv(name, *args):
        calls.append(('execv', name, args))
        podnieś RuntimeError("execv called")

    def mock_execve(name, *args):
        calls.append(('execve', name, args))
        podnieś OSError(errno.ENOTDIR, "execve called")

    spróbuj:
        orig_execv = os.execv
        orig_execve = os.execve
        orig_defpath = os.defpath
        os.execv = mock_execv
        os.execve = mock_execve
        jeżeli defpath jest nie Nic:
            os.defpath = defpath
        uzyskaj calls
    w_końcu:
        os.execv = orig_execv
        os.execve = orig_execve
        os.defpath = orig_defpath

klasa ExecTests(unittest.TestCase):
    @unittest.skipIf(USING_LINUXTHREADS,
                     "avoid triggering a linuxthreads bug: see issue #4970")
    def test_execvpe_with_bad_program(self):
        self.assertRaises(OSError, os.execvpe, 'no such app-',
                          ['no such app-'], Nic)

    def test_execvpe_with_bad_arglist(self):
        self.assertRaises(ValueError, os.execvpe, 'notepad', [], Nic)

    @unittest.skipUnless(hasattr(os, '_execvpe'),
                         "No internal os._execvpe function to test.")
    def _test_internal_execvpe(self, test_type):
        program_path = os.sep + 'absolutepath'
        jeżeli test_type jest bytes:
            program = b'executable'
            fullpath = os.path.join(os.fsencode(program_path), program)
            native_fullpath = fullpath
            arguments = [b'progname', 'arg1', 'arg2']
        inaczej:
            program = 'executable'
            arguments = ['progname', 'arg1', 'arg2']
            fullpath = os.path.join(program_path, program)
            jeżeli os.name != "nt":
                native_fullpath = os.fsencode(fullpath)
            inaczej:
                native_fullpath = fullpath
        env = {'spam': 'beans'}

        # test os._execvpe() przy an absolute path
        przy _execvpe_mockup() jako calls:
            self.assertRaises(RuntimeError,
                os._execvpe, fullpath, arguments)
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0], ('execv', fullpath, (arguments,)))

        # test os._execvpe() przy a relative path:
        # os.get_exec_path() returns defpath
        przy _execvpe_mockup(defpath=program_path) jako calls:
            self.assertRaises(OSError,
                os._execvpe, program, arguments, env=env)
            self.assertEqual(len(calls), 1)
            self.assertSequenceEqual(calls[0],
                ('execve', native_fullpath, (arguments, env)))

        # test os._execvpe() przy a relative path:
        # os.get_exec_path() reads the 'PATH' variable
        przy _execvpe_mockup() jako calls:
            env_path = env.copy()
            jeżeli test_type jest bytes:
                env_path[b'PATH'] = program_path
            inaczej:
                env_path['PATH'] = program_path
            self.assertRaises(OSError,
                os._execvpe, program, arguments, env=env_path)
            self.assertEqual(len(calls), 1)
            self.assertSequenceEqual(calls[0],
                ('execve', native_fullpath, (arguments, env_path)))

    def test_internal_execvpe_str(self):
        self._test_internal_execvpe(str)
        jeżeli os.name != "nt":
            self._test_internal_execvpe(bytes)


@unittest.skipUnless(sys.platform == "win32", "Win32 specific tests")
klasa Win32ErrorTests(unittest.TestCase):
    def test_rename(self):
        self.assertRaises(OSError, os.rename, support.TESTFN, support.TESTFN+".bak")

    def test_remove(self):
        self.assertRaises(OSError, os.remove, support.TESTFN)

    def test_chdir(self):
        self.assertRaises(OSError, os.chdir, support.TESTFN)

    def test_mkdir(self):
        f = open(support.TESTFN, "w")
        spróbuj:
            self.assertRaises(OSError, os.mkdir, support.TESTFN)
        w_końcu:
            f.close()
            os.unlink(support.TESTFN)

    def test_utime(self):
        self.assertRaises(OSError, os.utime, support.TESTFN, Nic)

    def test_chmod(self):
        self.assertRaises(OSError, os.chmod, support.TESTFN, 0)

klasa TestInvalidFD(unittest.TestCase):
    singles = ["fchdir", "dup", "fdopen", "fdatasync", "fstat",
               "fstatvfs", "fsync", "tcgetpgrp", "ttyname"]
    #singles.append("close")
    #We omit close because it doesn'r podnieś an exception on some platforms
    def get_single(f):
        def helper(self):
            jeżeli  hasattr(os, f):
                self.check(getattr(os, f))
        zwróć helper
    dla f w singles:
        locals()["test_"+f] = get_single(f)

    def check(self, f, *args):
        spróbuj:
            f(support.make_bad_fd(), *args)
        wyjąwszy OSError jako e:
            self.assertEqual(e.errno, errno.EBADF)
        inaczej:
            self.fail("%r didn't podnieś a OSError przy a bad file descriptor"
                      % f)

    @unittest.skipUnless(hasattr(os, 'isatty'), 'test needs os.isatty()')
    def test_isatty(self):
        self.assertEqual(os.isatty(support.make_bad_fd()), Nieprawda)

    @unittest.skipUnless(hasattr(os, 'closerange'), 'test needs os.closerange()')
    def test_closerange(self):
        fd = support.make_bad_fd()
        # Make sure none of the descriptors we are about to close are
        # currently valid (issue 6542).
        dla i w range(10):
            spróbuj: os.fstat(fd+i)
            wyjąwszy OSError:
                dalej
            inaczej:
                przerwij
        jeżeli i < 2:
            podnieś unittest.SkipTest(
                "Unable to acquire a range of invalid file descriptors")
        self.assertEqual(os.closerange(fd, fd + i-1), Nic)

    @unittest.skipUnless(hasattr(os, 'dup2'), 'test needs os.dup2()')
    def test_dup2(self):
        self.check(os.dup2, 20)

    @unittest.skipUnless(hasattr(os, 'fchmod'), 'test needs os.fchmod()')
    def test_fchmod(self):
        self.check(os.fchmod, 0)

    @unittest.skipUnless(hasattr(os, 'fchown'), 'test needs os.fchown()')
    def test_fchown(self):
        self.check(os.fchown, -1, -1)

    @unittest.skipUnless(hasattr(os, 'fpathconf'), 'test needs os.fpathconf()')
    def test_fpathconf(self):
        self.check(os.pathconf, "PC_NAME_MAX")
        self.check(os.fpathconf, "PC_NAME_MAX")

    @unittest.skipUnless(hasattr(os, 'ftruncate'), 'test needs os.ftruncate()')
    def test_ftruncate(self):
        self.check(os.truncate, 0)
        self.check(os.ftruncate, 0)

    @unittest.skipUnless(hasattr(os, 'lseek'), 'test needs os.lseek()')
    def test_lseek(self):
        self.check(os.lseek, 0, 0)

    @unittest.skipUnless(hasattr(os, 'read'), 'test needs os.read()')
    def test_read(self):
        self.check(os.read, 1)

    @unittest.skipUnless(hasattr(os, 'readv'), 'test needs os.readv()')
    def test_readv(self):
        buf = bytearray(10)
        self.check(os.readv, [buf])

    @unittest.skipUnless(hasattr(os, 'tcsetpgrp'), 'test needs os.tcsetpgrp()')
    def test_tcsetpgrpt(self):
        self.check(os.tcsetpgrp, 0)

    @unittest.skipUnless(hasattr(os, 'write'), 'test needs os.write()')
    def test_write(self):
        self.check(os.write, b" ")

    @unittest.skipUnless(hasattr(os, 'writev'), 'test needs os.writev()')
    def test_writev(self):
        self.check(os.writev, [b'abc'])

    def test_inheritable(self):
        self.check(os.get_inheritable)
        self.check(os.set_inheritable, Prawda)

    @unittest.skipUnless(hasattr(os, 'get_blocking'),
                         'needs os.get_blocking() oraz os.set_blocking()')
    def test_blocking(self):
        self.check(os.get_blocking)
        self.check(os.set_blocking, Prawda)


klasa LinkTests(unittest.TestCase):
    def setUp(self):
        self.file1 = support.TESTFN
        self.file2 = os.path.join(support.TESTFN + "2")

    def tearDown(self):
        dla file w (self.file1, self.file2):
            jeżeli os.path.exists(file):
                os.unlink(file)

    def _test_link(self, file1, file2):
        przy open(file1, "w") jako f1:
            f1.write("test")

        przy warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            os.link(file1, file2)
        przy open(file1, "r") jako f1, open(file2, "r") jako f2:
            self.assertPrawda(os.path.sameopenfile(f1.fileno(), f2.fileno()))

    def test_link(self):
        self._test_link(self.file1, self.file2)

    def test_link_bytes(self):
        self._test_link(bytes(self.file1, sys.getfilesystemencoding()),
                        bytes(self.file2, sys.getfilesystemencoding()))

    def test_unicode_name(self):
        spróbuj:
            os.fsencode("\xf1")
        wyjąwszy UnicodeError:
            podnieś unittest.SkipTest("Unable to encode dla this platform.")

        self.file1 += "\xf1"
        self.file2 = self.file1 + "2"
        self._test_link(self.file1, self.file2)

@unittest.skipIf(sys.platform == "win32", "Posix specific tests")
klasa PosixUidGidTests(unittest.TestCase):
    @unittest.skipUnless(hasattr(os, 'setuid'), 'test needs os.setuid()')
    def test_setuid(self):
        jeżeli os.getuid() != 0:
            self.assertRaises(OSError, os.setuid, 0)
        self.assertRaises(OverflowError, os.setuid, 1<<32)

    @unittest.skipUnless(hasattr(os, 'setgid'), 'test needs os.setgid()')
    def test_setgid(self):
        jeżeli os.getuid() != 0 oraz nie HAVE_WHEEL_GROUP:
            self.assertRaises(OSError, os.setgid, 0)
        self.assertRaises(OverflowError, os.setgid, 1<<32)

    @unittest.skipUnless(hasattr(os, 'seteuid'), 'test needs os.seteuid()')
    def test_seteuid(self):
        jeżeli os.getuid() != 0:
            self.assertRaises(OSError, os.seteuid, 0)
        self.assertRaises(OverflowError, os.seteuid, 1<<32)

    @unittest.skipUnless(hasattr(os, 'setegid'), 'test needs os.setegid()')
    def test_setegid(self):
        jeżeli os.getuid() != 0 oraz nie HAVE_WHEEL_GROUP:
            self.assertRaises(OSError, os.setegid, 0)
        self.assertRaises(OverflowError, os.setegid, 1<<32)

    @unittest.skipUnless(hasattr(os, 'setreuid'), 'test needs os.setreuid()')
    def test_setreuid(self):
        jeżeli os.getuid() != 0:
            self.assertRaises(OSError, os.setreuid, 0, 0)
        self.assertRaises(OverflowError, os.setreuid, 1<<32, 0)
        self.assertRaises(OverflowError, os.setreuid, 0, 1<<32)

    @unittest.skipUnless(hasattr(os, 'setreuid'), 'test needs os.setreuid()')
    def test_setreuid_neg1(self):
        # Needs to accept -1.  We run this w a subprocess to avoid
        # altering the test runner's process state (issue8045).
        subprocess.check_call([
                sys.executable, '-c',
                'zaimportuj os,sys;os.setreuid(-1,-1);sys.exit(0)'])

    @unittest.skipUnless(hasattr(os, 'setregid'), 'test needs os.setregid()')
    def test_setregid(self):
        jeżeli os.getuid() != 0 oraz nie HAVE_WHEEL_GROUP:
            self.assertRaises(OSError, os.setregid, 0, 0)
        self.assertRaises(OverflowError, os.setregid, 1<<32, 0)
        self.assertRaises(OverflowError, os.setregid, 0, 1<<32)

    @unittest.skipUnless(hasattr(os, 'setregid'), 'test needs os.setregid()')
    def test_setregid_neg1(self):
        # Needs to accept -1.  We run this w a subprocess to avoid
        # altering the test runner's process state (issue8045).
        subprocess.check_call([
                sys.executable, '-c',
                'zaimportuj os,sys;os.setregid(-1,-1);sys.exit(0)'])

@unittest.skipIf(sys.platform == "win32", "Posix specific tests")
klasa Pep383Tests(unittest.TestCase):
    def setUp(self):
        jeżeli support.TESTFN_UNENCODABLE:
            self.dir = support.TESTFN_UNENCODABLE
        albo_inaczej support.TESTFN_NONASCII:
            self.dir = support.TESTFN_NONASCII
        inaczej:
            self.dir = support.TESTFN
        self.bdir = os.fsencode(self.dir)

        bytesfn = []
        def add_filename(fn):
            spróbuj:
                fn = os.fsencode(fn)
            wyjąwszy UnicodeEncodeError:
                zwróć
            bytesfn.append(fn)
        add_filename(support.TESTFN_UNICODE)
        jeżeli support.TESTFN_UNENCODABLE:
            add_filename(support.TESTFN_UNENCODABLE)
        jeżeli support.TESTFN_NONASCII:
            add_filename(support.TESTFN_NONASCII)
        jeżeli nie bytesfn:
            self.skipTest("couldn't create any non-ascii filename")

        self.unicodefn = set()
        os.mkdir(self.dir)
        spróbuj:
            dla fn w bytesfn:
                support.create_empty_file(os.path.join(self.bdir, fn))
                fn = os.fsdecode(fn)
                jeżeli fn w self.unicodefn:
                    podnieś ValueError("duplicate filename")
                self.unicodefn.add(fn)
        wyjąwszy:
            shutil.rmtree(self.dir)
            podnieś

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_listdir(self):
        expected = self.unicodefn
        found = set(os.listdir(self.dir))
        self.assertEqual(found, expected)
        # test listdir without arguments
        current_directory = os.getcwd()
        spróbuj:
            os.chdir(os.sep)
            self.assertEqual(set(os.listdir()), set(os.listdir(os.sep)))
        w_końcu:
            os.chdir(current_directory)

    def test_open(self):
        dla fn w self.unicodefn:
            f = open(os.path.join(self.dir, fn), 'rb')
            f.close()

    @unittest.skipUnless(hasattr(os, 'statvfs'),
                            "need os.statvfs()")
    def test_statvfs(self):
        # issue #9645
        dla fn w self.unicodefn:
            # should nie fail przy file nie found error
            fullname = os.path.join(self.dir, fn)
            os.statvfs(fullname)

    def test_stat(self):
        dla fn w self.unicodefn:
            os.stat(os.path.join(self.dir, fn))

@unittest.skipUnless(sys.platform == "win32", "Win32 specific tests")
klasa Win32KillTests(unittest.TestCase):
    def _kill(self, sig):
        # Start sys.executable jako a subprocess oraz communicate z the
        # subprocess to the parent that the interpreter jest ready. When it
        # becomes ready, send *sig* via os.kill to the subprocess oraz check
        # that the zwróć code jest equal to *sig*.
        zaimportuj ctypes
        z ctypes zaimportuj wintypes
        zaimportuj msvcrt

        # Since we can't access the contents of the process' stdout until the
        # process has exited, use PeekNamedPipe to see what's inside stdout
        # without waiting. This jest done so we can tell that the interpreter
        # jest started oraz running at a point where it could handle a signal.
        PeekNamedPipe = ctypes.windll.kernel32.PeekNamedPipe
        PeekNamedPipe.restype = wintypes.BOOL
        PeekNamedPipe.argtypes = (wintypes.HANDLE, # Pipe handle
                                  ctypes.POINTER(ctypes.c_char), # stdout buf
                                  wintypes.DWORD, # Buffer size
                                  ctypes.POINTER(wintypes.DWORD), # bytes read
                                  ctypes.POINTER(wintypes.DWORD), # bytes avail
                                  ctypes.POINTER(wintypes.DWORD)) # bytes left
        msg = "running"
        proc = subprocess.Popen([sys.executable, "-c",
                                 "zaimportuj sys;"
                                 "sys.stdout.write('{}');"
                                 "sys.stdout.flush();"
                                 "input()".format(msg)],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE)
        self.addCleanup(proc.stdout.close)
        self.addCleanup(proc.stderr.close)
        self.addCleanup(proc.stdin.close)

        count, max = 0, 100
        dopóki count < max oraz proc.poll() jest Nic:
            # Create a string buffer to store the result of stdout z the pipe
            buf = ctypes.create_string_buffer(len(msg))
            # Obtain the text currently w proc.stdout
            # Bytes read/avail/left are left jako NULL oraz unused
            rslt = PeekNamedPipe(msvcrt.get_osfhandle(proc.stdout.fileno()),
                                 buf, ctypes.sizeof(buf), Nic, Nic, Nic)
            self.assertNotEqual(rslt, 0, "PeekNamedPipe failed")
            jeżeli buf.value:
                self.assertEqual(msg, buf.value.decode())
                przerwij
            time.sleep(0.1)
            count += 1
        inaczej:
            self.fail("Did nie receive communication z the subprocess")

        os.kill(proc.pid, sig)
        self.assertEqual(proc.wait(), sig)

    def test_kill_sigterm(self):
        # SIGTERM doesn't mean anything special, but make sure it works
        self._kill(signal.SIGTERM)

    def test_kill_int(self):
        # os.kill on Windows can take an int which gets set jako the exit code
        self._kill(100)

    def _kill_with_event(self, event, name):
        tagname = "test_os_%s" % uuid.uuid1()
        m = mmap.mmap(-1, 1, tagname)
        m[0] = 0
        # Run a script which has console control handling enabled.
        proc = subprocess.Popen([sys.executable,
                   os.path.join(os.path.dirname(__file__),
                                "win_console_handler.py"), tagname],
                   creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        # Let the interpreter startup before we send signals. See #3137.
        count, max = 0, 100
        dopóki count < max oraz proc.poll() jest Nic:
            jeżeli m[0] == 1:
                przerwij
            time.sleep(0.1)
            count += 1
        inaczej:
            # Forcefully kill the process jeżeli we weren't able to signal it.
            os.kill(proc.pid, signal.SIGINT)
            self.fail("Subprocess didn't finish initialization")
        os.kill(proc.pid, event)
        # proc.send_signal(event) could also be done here.
        # Allow time dla the signal to be dalejed oraz the process to exit.
        time.sleep(0.5)
        jeżeli nie proc.poll():
            # Forcefully kill the process jeżeli we weren't able to signal it.
            os.kill(proc.pid, signal.SIGINT)
            self.fail("subprocess did nie stop on {}".format(name))

    @unittest.skip("subprocesses aren't inheriting CTRL+C property")
    def test_CTRL_C_EVENT(self):
        z ctypes zaimportuj wintypes
        zaimportuj ctypes

        # Make a NULL value by creating a pointer przy no argument.
        NULL = ctypes.POINTER(ctypes.c_int)()
        SetConsoleCtrlHandler = ctypes.windll.kernel32.SetConsoleCtrlHandler
        SetConsoleCtrlHandler.argtypes = (ctypes.POINTER(ctypes.c_int),
                                          wintypes.BOOL)
        SetConsoleCtrlHandler.restype = wintypes.BOOL

        # Calling this przy NULL oraz FALSE causes the calling process to
        # handle CTRL+C, rather than ignore it. This property jest inherited
        # by subprocesses.
        SetConsoleCtrlHandler(NULL, 0)

        self._kill_with_event(signal.CTRL_C_EVENT, "CTRL_C_EVENT")

    def test_CTRL_BREAK_EVENT(self):
        self._kill_with_event(signal.CTRL_BREAK_EVENT, "CTRL_BREAK_EVENT")


@unittest.skipUnless(sys.platform == "win32", "Win32 specific tests")
klasa Win32ListdirTests(unittest.TestCase):
    """Test listdir on Windows."""

    def setUp(self):
        self.created_paths = []
        dla i w range(2):
            dir_name = 'SUB%d' % i
            dir_path = os.path.join(support.TESTFN, dir_name)
            file_name = 'FILE%d' % i
            file_path = os.path.join(support.TESTFN, file_name)
            os.makedirs(dir_path)
            przy open(file_path, 'w') jako f:
                f.write("I'm %s oraz proud of it. Blame test_os.\n" % file_path)
            self.created_paths.extend([dir_name, file_name])
        self.created_paths.sort()

    def tearDown(self):
        shutil.rmtree(support.TESTFN)

    def test_listdir_no_extended_path(self):
        """Test when the path jest nie an "extended" path."""
        # unicode
        self.assertEqual(
                sorted(os.listdir(support.TESTFN)),
                self.created_paths)
        # bytes
        self.assertEqual(
                sorted(os.listdir(os.fsencode(support.TESTFN))),
                [os.fsencode(path) dla path w self.created_paths])

    def test_listdir_extended_path(self):
        """Test when the path starts przy '\\\\?\\'."""
        # See: http://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx#maxpath
        # unicode
        path = '\\\\?\\' + os.path.abspath(support.TESTFN)
        self.assertEqual(
                sorted(os.listdir(path)),
                self.created_paths)
        # bytes
        path = b'\\\\?\\' + os.fsencode(os.path.abspath(support.TESTFN))
        self.assertEqual(
                sorted(os.listdir(path)),
                [os.fsencode(path) dla path w self.created_paths])


@unittest.skipUnless(sys.platform == "win32", "Win32 specific tests")
@support.skip_unless_symlink
klasa Win32SymlinkTests(unittest.TestCase):
    filelink = 'filelinktest'
    filelink_target = os.path.abspath(__file__)
    dirlink = 'dirlinktest'
    dirlink_target = os.path.dirname(filelink_target)
    missing_link = 'missing link'

    def setUp(self):
        assert os.path.exists(self.dirlink_target)
        assert os.path.exists(self.filelink_target)
        assert nie os.path.exists(self.dirlink)
        assert nie os.path.exists(self.filelink)
        assert nie os.path.exists(self.missing_link)

    def tearDown(self):
        jeżeli os.path.exists(self.filelink):
            os.remove(self.filelink)
        jeżeli os.path.exists(self.dirlink):
            os.rmdir(self.dirlink)
        jeżeli os.path.lexists(self.missing_link):
            os.remove(self.missing_link)

    def test_directory_link(self):
        os.symlink(self.dirlink_target, self.dirlink)
        self.assertPrawda(os.path.exists(self.dirlink))
        self.assertPrawda(os.path.isdir(self.dirlink))
        self.assertPrawda(os.path.islink(self.dirlink))
        self.check_stat(self.dirlink, self.dirlink_target)

    def test_file_link(self):
        os.symlink(self.filelink_target, self.filelink)
        self.assertPrawda(os.path.exists(self.filelink))
        self.assertPrawda(os.path.isfile(self.filelink))
        self.assertPrawda(os.path.islink(self.filelink))
        self.check_stat(self.filelink, self.filelink_target)

    def _create_missing_dir_link(self):
        'Create a "directory" link to a non-existent target'
        linkname = self.missing_link
        jeżeli os.path.lexists(linkname):
            os.remove(linkname)
        target = r'c:\\target does nie exist.29r3c740'
        assert nie os.path.exists(target)
        target_is_dir = Prawda
        os.symlink(target, linkname, target_is_dir)

    def test_remove_directory_link_to_missing_target(self):
        self._create_missing_dir_link()
        # For compatibility przy Unix, os.remove will check the
        #  directory status oraz call RemoveDirectory jeżeli the symlink
        #  was created przy target_is_dir==Prawda.
        os.remove(self.missing_link)

    @unittest.skip("currently fails; consider dla improvement")
    def test_isdir_on_directory_link_to_missing_target(self):
        self._create_missing_dir_link()
        # consider having isdir zwróć true dla directory links
        self.assertPrawda(os.path.isdir(self.missing_link))

    @unittest.skip("currently fails; consider dla improvement")
    def test_rmdir_on_directory_link_to_missing_target(self):
        self._create_missing_dir_link()
        # consider allowing rmdir to remove directory links
        os.rmdir(self.missing_link)

    def check_stat(self, link, target):
        self.assertEqual(os.stat(link), os.stat(target))
        self.assertNotEqual(os.lstat(link), os.stat(link))

        bytes_link = os.fsencode(link)
        przy warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.assertEqual(os.stat(bytes_link), os.stat(target))
            self.assertNotEqual(os.lstat(bytes_link), os.stat(bytes_link))

    def test_12084(self):
        level1 = os.path.abspath(support.TESTFN)
        level2 = os.path.join(level1, "level2")
        level3 = os.path.join(level2, "level3")
        spróbuj:
            os.mkdir(level1)
            os.mkdir(level2)
            os.mkdir(level3)

            file1 = os.path.abspath(os.path.join(level1, "file1"))

            przy open(file1, "w") jako f:
                f.write("file1")

            orig_dir = os.getcwd()
            spróbuj:
                os.chdir(level2)
                link = os.path.join(level2, "link")
                os.symlink(os.path.relpath(file1), "link")
                self.assertIn("link", os.listdir(os.getcwd()))

                # Check os.stat calls z the same dir jako the link
                self.assertEqual(os.stat(file1), os.stat("link"))

                # Check os.stat calls z a dir below the link
                os.chdir(level1)
                self.assertEqual(os.stat(file1),
                                 os.stat(os.path.relpath(link)))

                # Check os.stat calls z a dir above the link
                os.chdir(level3)
                self.assertEqual(os.stat(file1),
                                 os.stat(os.path.relpath(link)))
            w_końcu:
                os.chdir(orig_dir)
        wyjąwszy OSError jako err:
            self.fail(err)
        w_końcu:
            os.remove(file1)
            shutil.rmtree(level1)


@unittest.skipUnless(sys.platform == "win32", "Win32 specific tests")
klasa Win32JunctionTests(unittest.TestCase):
    junction = 'junctiontest'
    junction_target = os.path.dirname(os.path.abspath(__file__))

    def setUp(self):
        assert os.path.exists(self.junction_target)
        assert nie os.path.exists(self.junction)

    def tearDown(self):
        jeżeli os.path.exists(self.junction):
            # os.rmdir delegates to Windows' RemoveDirectoryW,
            # which removes junction points safely.
            os.rmdir(self.junction)

    def test_create_junction(self):
        _winapi.CreateJunction(self.junction_target, self.junction)
        self.assertPrawda(os.path.exists(self.junction))
        self.assertPrawda(os.path.isdir(self.junction))

        # Junctions are nie recognized jako links.
        self.assertNieprawda(os.path.islink(self.junction))

    def test_unlink_removes_junction(self):
        _winapi.CreateJunction(self.junction_target, self.junction)
        self.assertPrawda(os.path.exists(self.junction))

        os.unlink(self.junction)
        self.assertNieprawda(os.path.exists(self.junction))


@support.skip_unless_symlink
klasa NonLocalSymlinkTests(unittest.TestCase):

    def setUp(self):
        """
        Create this structure:

        base
         \___ some_dir
        """
        os.makedirs('base/some_dir')

    def tearDown(self):
        shutil.rmtree('base')

    def test_directory_link_nonlocal(self):
        """
        The symlink target should resolve relative to the link, nie relative
        to the current directory.

        Then, link base/some_link -> base/some_dir oraz ensure that some_link
        jest resolved jako a directory.

        In issue13772, it was discovered that directory detection failed if
        the symlink target was nie specified relative to the current
        directory, which was a defect w the implementation.
        """
        src = os.path.join('base', 'some_link')
        os.symlink('some_dir', src)
        assert os.path.isdir(src)


klasa FSEncodingTests(unittest.TestCase):
    def test_nop(self):
        self.assertEqual(os.fsencode(b'abc\xff'), b'abc\xff')
        self.assertEqual(os.fsdecode('abc\u0141'), 'abc\u0141')

    def test_identity(self):
        # assert fsdecode(fsencode(x)) == x
        dla fn w ('unicode\u0141', 'latin\xe9', 'ascii'):
            spróbuj:
                bytesfn = os.fsencode(fn)
            wyjąwszy UnicodeEncodeError:
                kontynuuj
            self.assertEqual(os.fsdecode(bytesfn), fn)



klasa DeviceEncodingTests(unittest.TestCase):

    def test_bad_fd(self):
        # Return Nic when an fd doesn't actually exist.
        self.assertIsNic(os.device_encoding(123456))

    @unittest.skipUnless(os.isatty(0) oraz (sys.platform.startswith('win') albo
            (hasattr(locale, 'nl_langinfo') oraz hasattr(locale, 'CODESET'))),
            'test requires a tty oraz either Windows albo nl_langinfo(CODESET)')
    def test_device_encoding(self):
        encoding = os.device_encoding(0)
        self.assertIsNotNic(encoding)
        self.assertPrawda(codecs.lookup(encoding))


klasa PidTests(unittest.TestCase):
    @unittest.skipUnless(hasattr(os, 'getppid'), "test needs os.getppid")
    def test_getppid(self):
        p = subprocess.Popen([sys.executable, '-c',
                              'zaimportuj os; print(os.getppid())'],
                             stdout=subprocess.PIPE)
        stdout, _ = p.communicate()
        # We are the parent of our subprocess
        self.assertEqual(int(stdout), os.getpid())


# The introduction of this TestCase caused at least two different errors on
# *nix buildbots. Temporarily skip this to let the buildbots move along.
@unittest.skip("Skip due to platform/environment differences on *NIX buildbots")
@unittest.skipUnless(hasattr(os, 'getlogin'), "test needs os.getlogin")
klasa LoginTests(unittest.TestCase):
    def test_getlogin(self):
        user_name = os.getlogin()
        self.assertNotEqual(len(user_name), 0)


@unittest.skipUnless(hasattr(os, 'getpriority') oraz hasattr(os, 'setpriority'),
                     "needs os.getpriority oraz os.setpriority")
klasa ProgramPriorityTests(unittest.TestCase):
    """Tests dla os.getpriority() oraz os.setpriority()."""

    def test_set_get_priority(self):

        base = os.getpriority(os.PRIO_PROCESS, os.getpid())
        os.setpriority(os.PRIO_PROCESS, os.getpid(), base + 1)
        spróbuj:
            new_prio = os.getpriority(os.PRIO_PROCESS, os.getpid())
            jeżeli base >= 19 oraz new_prio <= 19:
                podnieś unittest.SkipTest(
      "unable to reliably test setpriority at current nice level of %s" % base)
            inaczej:
                self.assertEqual(new_prio, base + 1)
        w_końcu:
            spróbuj:
                os.setpriority(os.PRIO_PROCESS, os.getpid(), base)
            wyjąwszy OSError jako err:
                jeżeli err.errno != errno.EACCES:
                    podnieś


jeżeli threading jest nie Nic:
    klasa SendfileTestServer(asyncore.dispatcher, threading.Thread):

        klasa Handler(asynchat.async_chat):

            def __init__(self, conn):
                asynchat.async_chat.__init__(self, conn)
                self.in_buffer = []
                self.closed = Nieprawda
                self.push(b"220 ready\r\n")

            def handle_read(self):
                data = self.recv(4096)
                self.in_buffer.append(data)

            def get_data(self):
                zwróć b''.join(self.in_buffer)

            def handle_close(self):
                self.close()
                self.closed = Prawda

            def handle_error(self):
                podnieś

        def __init__(self, address):
            threading.Thread.__init__(self)
            asyncore.dispatcher.__init__(self)
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.bind(address)
            self.listen(5)
            self.host, self.port = self.socket.getsockname()[:2]
            self.handler_instance = Nic
            self._active = Nieprawda
            self._active_lock = threading.Lock()

        # --- public API

        @property
        def running(self):
            zwróć self._active

        def start(self):
            assert nie self.running
            self.__flag = threading.Event()
            threading.Thread.start(self)
            self.__flag.wait()

        def stop(self):
            assert self.running
            self._active = Nieprawda
            self.join()

        def wait(self):
            # wait dla handler connection to be closed, then stop the server
            dopóki nie getattr(self.handler_instance, "closed", Nieprawda):
                time.sleep(0.001)
            self.stop()

        # --- internals

        def run(self):
            self._active = Prawda
            self.__flag.set()
            dopóki self._active oraz asyncore.socket_map:
                self._active_lock.acquire()
                asyncore.loop(timeout=0.001, count=1)
                self._active_lock.release()
            asyncore.close_all()

        def handle_accept(self):
            conn, addr = self.accept()
            self.handler_instance = self.Handler(conn)

        def handle_connect(self):
            self.close()
        handle_read = handle_connect

        def writable(self):
            zwróć 0

        def handle_error(self):
            podnieś


@unittest.skipUnless(threading jest nie Nic, "test needs threading module")
@unittest.skipUnless(hasattr(os, 'sendfile'), "test needs os.sendfile()")
klasa TestSendfile(unittest.TestCase):

    DATA = b"12345abcde" * 16 * 1024  # 160 KB
    SUPPORT_HEADERS_TRAILERS = nie sys.platform.startswith("linux") oraz \
                               nie sys.platform.startswith("solaris") oraz \
                               nie sys.platform.startswith("sunos")
    requires_headers_trailers = unittest.skipUnless(SUPPORT_HEADERS_TRAILERS,
            'requires headers oraz trailers support')

    @classmethod
    def setUpClass(cls):
        cls.key = support.threading_setup()
        przy open(support.TESTFN, "wb") jako f:
            f.write(cls.DATA)

    @classmethod
    def tearDownClass(cls):
        support.threading_cleanup(*cls.key)
        support.unlink(support.TESTFN)

    def setUp(self):
        self.server = SendfileTestServer((support.HOST, 0))
        self.server.start()
        self.client = socket.socket()
        self.client.connect((self.server.host, self.server.port))
        self.client.settimeout(1)
        # synchronize by waiting dla "220 ready" response
        self.client.recv(1024)
        self.sockno = self.client.fileno()
        self.file = open(support.TESTFN, 'rb')
        self.fileno = self.file.fileno()

    def tearDown(self):
        self.file.close()
        self.client.close()
        jeżeli self.server.running:
            self.server.stop()

    def sendfile_wrapper(self, sock, file, offset, nbytes, headers=[], trailers=[]):
        """A higher level wrapper representing how an application jest
        supposed to use sendfile().
        """
        dopóki 1:
            spróbuj:
                jeżeli self.SUPPORT_HEADERS_TRAILERS:
                    zwróć os.sendfile(sock, file, offset, nbytes, headers,
                                       trailers)
                inaczej:
                    zwróć os.sendfile(sock, file, offset, nbytes)
            wyjąwszy OSError jako err:
                jeżeli err.errno == errno.ECONNRESET:
                    # disconnected
                    podnieś
                albo_inaczej err.errno w (errno.EAGAIN, errno.EBUSY):
                    # we have to retry send data
                    kontynuuj
                inaczej:
                    podnieś

    def test_send_whole_file(self):
        # normal send
        total_sent = 0
        offset = 0
        nbytes = 4096
        dopóki total_sent < len(self.DATA):
            sent = self.sendfile_wrapper(self.sockno, self.fileno, offset, nbytes)
            jeżeli sent == 0:
                przerwij
            offset += sent
            total_sent += sent
            self.assertPrawda(sent <= nbytes)
            self.assertEqual(offset, total_sent)

        self.assertEqual(total_sent, len(self.DATA))
        self.client.shutdown(socket.SHUT_RDWR)
        self.client.close()
        self.server.wait()
        data = self.server.handler_instance.get_data()
        self.assertEqual(len(data), len(self.DATA))
        self.assertEqual(data, self.DATA)

    def test_send_at_certain_offset(self):
        # start sending a file at a certain offset
        total_sent = 0
        offset = len(self.DATA) // 2
        must_send = len(self.DATA) - offset
        nbytes = 4096
        dopóki total_sent < must_send:
            sent = self.sendfile_wrapper(self.sockno, self.fileno, offset, nbytes)
            jeżeli sent == 0:
                przerwij
            offset += sent
            total_sent += sent
            self.assertPrawda(sent <= nbytes)

        self.client.shutdown(socket.SHUT_RDWR)
        self.client.close()
        self.server.wait()
        data = self.server.handler_instance.get_data()
        expected = self.DATA[len(self.DATA) // 2:]
        self.assertEqual(total_sent, len(expected))
        self.assertEqual(len(data), len(expected))
        self.assertEqual(data, expected)

    def test_offset_overflow(self):
        # specify an offset > file size
        offset = len(self.DATA) + 4096
        spróbuj:
            sent = os.sendfile(self.sockno, self.fileno, offset, 4096)
        wyjąwszy OSError jako e:
            # Solaris can podnieś EINVAL jeżeli offset >= file length, ignore.
            jeżeli e.errno != errno.EINVAL:
                podnieś
        inaczej:
            self.assertEqual(sent, 0)
        self.client.shutdown(socket.SHUT_RDWR)
        self.client.close()
        self.server.wait()
        data = self.server.handler_instance.get_data()
        self.assertEqual(data, b'')

    def test_invalid_offset(self):
        przy self.assertRaises(OSError) jako cm:
            os.sendfile(self.sockno, self.fileno, -1, 4096)
        self.assertEqual(cm.exception.errno, errno.EINVAL)

    # --- headers / trailers tests

    @requires_headers_trailers
    def test_headers(self):
        total_sent = 0
        sent = os.sendfile(self.sockno, self.fileno, 0, 4096,
                            headers=[b"x" * 512])
        total_sent += sent
        offset = 4096
        nbytes = 4096
        dopóki 1:
            sent = self.sendfile_wrapper(self.sockno, self.fileno,
                                                    offset, nbytes)
            jeżeli sent == 0:
                przerwij
            total_sent += sent
            offset += sent

        expected_data = b"x" * 512 + self.DATA
        self.assertEqual(total_sent, len(expected_data))
        self.client.close()
        self.server.wait()
        data = self.server.handler_instance.get_data()
        self.assertEqual(hash(data), hash(expected_data))

    @requires_headers_trailers
    def test_trailers(self):
        TESTFN2 = support.TESTFN + "2"
        file_data = b"abcdef"
        przy open(TESTFN2, 'wb') jako f:
            f.write(file_data)
        przy open(TESTFN2, 'rb')as f:
            self.addCleanup(os.remove, TESTFN2)
            os.sendfile(self.sockno, f.fileno(), 0, len(file_data),
                        trailers=[b"1234"])
            self.client.close()
            self.server.wait()
            data = self.server.handler_instance.get_data()
            self.assertEqual(data, b"abcdef1234")

    @requires_headers_trailers
    @unittest.skipUnless(hasattr(os, 'SF_NODISKIO'),
                         'test needs os.SF_NODISKIO')
    def test_flags(self):
        spróbuj:
            os.sendfile(self.sockno, self.fileno, 0, 4096,
                        flags=os.SF_NODISKIO)
        wyjąwszy OSError jako err:
            jeżeli err.errno nie w (errno.EBUSY, errno.EAGAIN):
                podnieś


def supports_extended_attributes():
    jeżeli nie hasattr(os, "setxattr"):
        zwróć Nieprawda
    spróbuj:
        przy open(support.TESTFN, "wb") jako fp:
            spróbuj:
                os.setxattr(fp.fileno(), b"user.test", b"")
            wyjąwszy OSError:
                zwróć Nieprawda
    w_końcu:
        support.unlink(support.TESTFN)
    # Kernels < 2.6.39 don't respect setxattr flags.
    kernel_version = platform.release()
    m = re.match("2.6.(\d{1,2})", kernel_version)
    zwróć m jest Nic albo int(m.group(1)) >= 39


@unittest.skipUnless(supports_extended_attributes(),
                     "no non-broken extended attribute support")
klasa ExtendedAttributeTests(unittest.TestCase):

    def tearDown(self):
        support.unlink(support.TESTFN)

    def _check_xattrs_str(self, s, getxattr, setxattr, removexattr, listxattr, **kwargs):
        fn = support.TESTFN
        open(fn, "wb").close()
        przy self.assertRaises(OSError) jako cm:
            getxattr(fn, s("user.test"), **kwargs)
        self.assertEqual(cm.exception.errno, errno.ENODATA)
        init_xattr = listxattr(fn)
        self.assertIsInstance(init_xattr, list)
        setxattr(fn, s("user.test"), b"", **kwargs)
        xattr = set(init_xattr)
        xattr.add("user.test")
        self.assertEqual(set(listxattr(fn)), xattr)
        self.assertEqual(getxattr(fn, b"user.test", **kwargs), b"")
        setxattr(fn, s("user.test"), b"hello", os.XATTR_REPLACE, **kwargs)
        self.assertEqual(getxattr(fn, b"user.test", **kwargs), b"hello")
        przy self.assertRaises(OSError) jako cm:
            setxattr(fn, s("user.test"), b"bye", os.XATTR_CREATE, **kwargs)
        self.assertEqual(cm.exception.errno, errno.EEXIST)
        przy self.assertRaises(OSError) jako cm:
            setxattr(fn, s("user.test2"), b"bye", os.XATTR_REPLACE, **kwargs)
        self.assertEqual(cm.exception.errno, errno.ENODATA)
        setxattr(fn, s("user.test2"), b"foo", os.XATTR_CREATE, **kwargs)
        xattr.add("user.test2")
        self.assertEqual(set(listxattr(fn)), xattr)
        removexattr(fn, s("user.test"), **kwargs)
        przy self.assertRaises(OSError) jako cm:
            getxattr(fn, s("user.test"), **kwargs)
        self.assertEqual(cm.exception.errno, errno.ENODATA)
        xattr.remove("user.test")
        self.assertEqual(set(listxattr(fn)), xattr)
        self.assertEqual(getxattr(fn, s("user.test2"), **kwargs), b"foo")
        setxattr(fn, s("user.test"), b"a"*1024, **kwargs)
        self.assertEqual(getxattr(fn, s("user.test"), **kwargs), b"a"*1024)
        removexattr(fn, s("user.test"), **kwargs)
        many = sorted("user.test{}".format(i) dla i w range(100))
        dla thing w many:
            setxattr(fn, thing, b"x", **kwargs)
        self.assertEqual(set(listxattr(fn)), set(init_xattr) | set(many))

    def _check_xattrs(self, *args, **kwargs):
        def make_bytes(s):
            zwróć bytes(s, "ascii")
        self._check_xattrs_str(str, *args, **kwargs)
        support.unlink(support.TESTFN)
        self._check_xattrs_str(make_bytes, *args, **kwargs)

    def test_simple(self):
        self._check_xattrs(os.getxattr, os.setxattr, os.removexattr,
                           os.listxattr)

    def test_lpath(self):
        self._check_xattrs(os.getxattr, os.setxattr, os.removexattr,
                           os.listxattr, follow_symlinks=Nieprawda)

    def test_fds(self):
        def getxattr(path, *args):
            przy open(path, "rb") jako fp:
                zwróć os.getxattr(fp.fileno(), *args)
        def setxattr(path, *args):
            przy open(path, "wb") jako fp:
                os.setxattr(fp.fileno(), *args)
        def removexattr(path, *args):
            przy open(path, "wb") jako fp:
                os.removexattr(fp.fileno(), *args)
        def listxattr(path, *args):
            przy open(path, "rb") jako fp:
                zwróć os.listxattr(fp.fileno(), *args)
        self._check_xattrs(getxattr, setxattr, removexattr, listxattr)


@unittest.skipUnless(sys.platform == "win32", "Win32 specific tests")
klasa Win32DeprecatedBytesAPI(unittest.TestCase):
    def test_deprecated(self):
        zaimportuj nt
        filename = os.fsencode(support.TESTFN)
        przy warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            dla func, *args w (
                (nt._getfullpathname, filename),
                (nt._isdir, filename),
                (os.access, filename, os.R_OK),
                (os.chdir, filename),
                (os.chmod, filename, 0o777),
                (os.getcwdb,),
                (os.link, filename, filename),
                (os.listdir, filename),
                (os.lstat, filename),
                (os.mkdir, filename),
                (os.open, filename, os.O_RDONLY),
                (os.rename, filename, filename),
                (os.rmdir, filename),
                (os.startfile, filename),
                (os.stat, filename),
                (os.unlink, filename),
                (os.utime, filename),
            ):
                self.assertRaises(DeprecationWarning, func, *args)

    @support.skip_unless_symlink
    def test_symlink(self):
        filename = os.fsencode(support.TESTFN)
        przy warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            self.assertRaises(DeprecationWarning,
                              os.symlink, filename, filename)


@unittest.skipUnless(hasattr(os, 'get_terminal_size'), "requires os.get_terminal_size")
klasa TermsizeTests(unittest.TestCase):
    def test_does_not_crash(self):
        """Check jeżeli get_terminal_size() returns a meaningful value.

        There's no easy portable way to actually check the size of the
        terminal, so let's check jeżeli it returns something sensible instead.
        """
        spróbuj:
            size = os.get_terminal_size()
        wyjąwszy OSError jako e:
            jeżeli sys.platform == "win32" albo e.errno w (errno.EINVAL, errno.ENOTTY):
                # Under win32 a generic OSError can be thrown jeżeli the
                # handle cannot be retrieved
                self.skipTest("failed to query terminal size")
            podnieś

        self.assertGreaterEqual(size.columns, 0)
        self.assertGreaterEqual(size.lines, 0)

    def test_stty_match(self):
        """Check jeżeli stty returns the same results

        stty actually tests stdin, so get_terminal_size jest invoked on
        stdin explicitly. If stty succeeded, then get_terminal_size()
        should work too.
        """
        spróbuj:
            size = subprocess.check_output(['stty', 'size']).decode().split()
        wyjąwszy (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("stty invocation failed")
        expected = (int(size[1]), int(size[0])) # reversed order

        spróbuj:
            actual = os.get_terminal_size(sys.__stdin__.fileno())
        wyjąwszy OSError jako e:
            jeżeli sys.platform == "win32" albo e.errno w (errno.EINVAL, errno.ENOTTY):
                # Under win32 a generic OSError can be thrown jeżeli the
                # handle cannot be retrieved
                self.skipTest("failed to query terminal size")
            podnieś
        self.assertEqual(expected, actual)


klasa OSErrorTests(unittest.TestCase):
    def setUp(self):
        klasa Str(str):
            dalej

        self.bytes_filenames = []
        self.unicode_filenames = []
        jeżeli support.TESTFN_UNENCODABLE jest nie Nic:
            decoded = support.TESTFN_UNENCODABLE
        inaczej:
            decoded = support.TESTFN
        self.unicode_filenames.append(decoded)
        self.unicode_filenames.append(Str(decoded))
        jeżeli support.TESTFN_UNDECODABLE jest nie Nic:
            encoded = support.TESTFN_UNDECODABLE
        inaczej:
            encoded = os.fsencode(support.TESTFN)
        self.bytes_filenames.append(encoded)
        self.bytes_filenames.append(memoryview(encoded))

        self.filenames = self.bytes_filenames + self.unicode_filenames

    def test_oserror_filename(self):
        funcs = [
            (self.filenames, os.chdir,),
            (self.filenames, os.chmod, 0o777),
            (self.filenames, os.lstat,),
            (self.filenames, os.open, os.O_RDONLY),
            (self.filenames, os.rmdir,),
            (self.filenames, os.stat,),
            (self.filenames, os.unlink,),
        ]
        jeżeli sys.platform == "win32":
            funcs.extend((
                (self.bytes_filenames, os.rename, b"dst"),
                (self.bytes_filenames, os.replace, b"dst"),
                (self.unicode_filenames, os.rename, "dst"),
                (self.unicode_filenames, os.replace, "dst"),
                # Issue #16414: Don't test undecodable names przy listdir()
                # because of a Windows bug.
                #
                # With the ANSI code page 932, os.listdir(b'\xe7') zwróć an
                # empty list (instead of failing), whereas os.listdir(b'\xff')
                # podnieśs a FileNotFoundError. It looks like a Windows bug:
                # b'\xe7' directory does nie exist, FindFirstFileA(b'\xe7')
                # fails przy ERROR_FILE_NOT_FOUND (2), instead of
                # ERROR_PATH_NOT_FOUND (3).
                (self.unicode_filenames, os.listdir,),
            ))
        inaczej:
            funcs.extend((
                (self.filenames, os.listdir,),
                (self.filenames, os.rename, "dst"),
                (self.filenames, os.replace, "dst"),
            ))
        jeżeli hasattr(os, "chown"):
            funcs.append((self.filenames, os.chown, 0, 0))
        jeżeli hasattr(os, "lchown"):
            funcs.append((self.filenames, os.lchown, 0, 0))
        jeżeli hasattr(os, "truncate"):
            funcs.append((self.filenames, os.truncate, 0))
        jeżeli hasattr(os, "chflags"):
            funcs.append((self.filenames, os.chflags, 0))
        jeżeli hasattr(os, "lchflags"):
            funcs.append((self.filenames, os.lchflags, 0))
        jeżeli hasattr(os, "chroot"):
            funcs.append((self.filenames, os.chroot,))
        jeżeli hasattr(os, "link"):
            jeżeli sys.platform == "win32":
                funcs.append((self.bytes_filenames, os.link, b"dst"))
                funcs.append((self.unicode_filenames, os.link, "dst"))
            inaczej:
                funcs.append((self.filenames, os.link, "dst"))
        jeżeli hasattr(os, "listxattr"):
            funcs.extend((
                (self.filenames, os.listxattr,),
                (self.filenames, os.getxattr, "user.test"),
                (self.filenames, os.setxattr, "user.test", b'user'),
                (self.filenames, os.removexattr, "user.test"),
            ))
        jeżeli hasattr(os, "lchmod"):
            funcs.append((self.filenames, os.lchmod, 0o777))
        jeżeli hasattr(os, "readlink"):
            jeżeli sys.platform == "win32":
                funcs.append((self.unicode_filenames, os.readlink,))
            inaczej:
                funcs.append((self.filenames, os.readlink,))

        dla filenames, func, *func_args w funcs:
            dla name w filenames:
                spróbuj:
                    func(name, *func_args)
                wyjąwszy OSError jako err:
                    self.assertIs(err.filename, name)
                inaczej:
                    self.fail("No exception thrown by {}".format(func))

klasa CPUCountTests(unittest.TestCase):
    def test_cpu_count(self):
        cpus = os.cpu_count()
        jeżeli cpus jest nie Nic:
            self.assertIsInstance(cpus, int)
            self.assertGreater(cpus, 0)
        inaczej:
            self.skipTest("Could nie determine the number of CPUs")


klasa FDInheritanceTests(unittest.TestCase):
    def test_get_set_inheritable(self):
        fd = os.open(__file__, os.O_RDONLY)
        self.addCleanup(os.close, fd)
        self.assertEqual(os.get_inheritable(fd), Nieprawda)

        os.set_inheritable(fd, Prawda)
        self.assertEqual(os.get_inheritable(fd), Prawda)

    @unittest.skipIf(fcntl jest Nic, "need fcntl")
    def test_get_inheritable_cloexec(self):
        fd = os.open(__file__, os.O_RDONLY)
        self.addCleanup(os.close, fd)
        self.assertEqual(os.get_inheritable(fd), Nieprawda)

        # clear FD_CLOEXEC flag
        flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        flags &= ~fcntl.FD_CLOEXEC
        fcntl.fcntl(fd, fcntl.F_SETFD, flags)

        self.assertEqual(os.get_inheritable(fd), Prawda)

    @unittest.skipIf(fcntl jest Nic, "need fcntl")
    def test_set_inheritable_cloexec(self):
        fd = os.open(__file__, os.O_RDONLY)
        self.addCleanup(os.close, fd)
        self.assertEqual(fcntl.fcntl(fd, fcntl.F_GETFD) & fcntl.FD_CLOEXEC,
                         fcntl.FD_CLOEXEC)

        os.set_inheritable(fd, Prawda)
        self.assertEqual(fcntl.fcntl(fd, fcntl.F_GETFD) & fcntl.FD_CLOEXEC,
                         0)

    def test_open(self):
        fd = os.open(__file__, os.O_RDONLY)
        self.addCleanup(os.close, fd)
        self.assertEqual(os.get_inheritable(fd), Nieprawda)

    @unittest.skipUnless(hasattr(os, 'pipe'), "need os.pipe()")
    def test_pipe(self):
        rfd, wfd = os.pipe()
        self.addCleanup(os.close, rfd)
        self.addCleanup(os.close, wfd)
        self.assertEqual(os.get_inheritable(rfd), Nieprawda)
        self.assertEqual(os.get_inheritable(wfd), Nieprawda)

    def test_dup(self):
        fd1 = os.open(__file__, os.O_RDONLY)
        self.addCleanup(os.close, fd1)

        fd2 = os.dup(fd1)
        self.addCleanup(os.close, fd2)
        self.assertEqual(os.get_inheritable(fd2), Nieprawda)

    @unittest.skipUnless(hasattr(os, 'dup2'), "need os.dup2()")
    def test_dup2(self):
        fd = os.open(__file__, os.O_RDONLY)
        self.addCleanup(os.close, fd)

        # inheritable by default
        fd2 = os.open(__file__, os.O_RDONLY)
        spróbuj:
            os.dup2(fd, fd2)
            self.assertEqual(os.get_inheritable(fd2), Prawda)
        w_końcu:
            os.close(fd2)

        # force non-inheritable
        fd3 = os.open(__file__, os.O_RDONLY)
        spróbuj:
            os.dup2(fd, fd3, inheritable=Nieprawda)
            self.assertEqual(os.get_inheritable(fd3), Nieprawda)
        w_końcu:
            os.close(fd3)

    @unittest.skipUnless(hasattr(os, 'openpty'), "need os.openpty()")
    def test_openpty(self):
        master_fd, slave_fd = os.openpty()
        self.addCleanup(os.close, master_fd)
        self.addCleanup(os.close, slave_fd)
        self.assertEqual(os.get_inheritable(master_fd), Nieprawda)
        self.assertEqual(os.get_inheritable(slave_fd), Nieprawda)


@unittest.skipUnless(hasattr(os, 'get_blocking'),
                     'needs os.get_blocking() oraz os.set_blocking()')
klasa BlockingTests(unittest.TestCase):
    def test_blocking(self):
        fd = os.open(__file__, os.O_RDONLY)
        self.addCleanup(os.close, fd)
        self.assertEqual(os.get_blocking(fd), Prawda)

        os.set_blocking(fd, Nieprawda)
        self.assertEqual(os.get_blocking(fd), Nieprawda)

        os.set_blocking(fd, Prawda)
        self.assertEqual(os.get_blocking(fd), Prawda)



klasa ExportsTests(unittest.TestCase):
    def test_os_all(self):
        self.assertIn('open', os.__all__)
        self.assertIn('walk', os.__all__)


klasa TestScandir(unittest.TestCase):
    def setUp(self):
        self.path = os.path.realpath(support.TESTFN)
        self.addCleanup(support.rmtree, self.path)
        os.mkdir(self.path)

    def create_file(self, name="file.txt"):
        filename = os.path.join(self.path, name)
        przy open(filename, "wb") jako fp:
            fp.write(b'python')
        zwróć filename

    def get_entries(self, names):
        entries = dict((entry.name, entry)
                       dla entry w os.scandir(self.path))
        self.assertEqual(sorted(entries.keys()), names)
        zwróć entries

    def assert_stat_equal(self, stat1, stat2, skip_fields):
        jeżeli skip_fields:
            dla attr w dir(stat1):
                jeżeli nie attr.startswith("st_"):
                    kontynuuj
                jeżeli attr w ("st_dev", "st_ino", "st_nlink"):
                    kontynuuj
                self.assertEqual(getattr(stat1, attr),
                                 getattr(stat2, attr),
                                 (stat1, stat2, attr))
        inaczej:
            self.assertEqual(stat1, stat2)

    def check_entry(self, entry, name, is_dir, is_file, is_symlink):
        self.assertEqual(entry.name, name)
        self.assertEqual(entry.path, os.path.join(self.path, name))
        self.assertEqual(entry.inode(),
                         os.stat(entry.path, follow_symlinks=Nieprawda).st_ino)

        entry_stat = os.stat(entry.path)
        self.assertEqual(entry.is_dir(),
                         stat.S_ISDIR(entry_stat.st_mode))
        self.assertEqual(entry.is_file(),
                         stat.S_ISREG(entry_stat.st_mode))
        self.assertEqual(entry.is_symlink(),
                         os.path.islink(entry.path))

        entry_lstat = os.stat(entry.path, follow_symlinks=Nieprawda)
        self.assertEqual(entry.is_dir(follow_symlinks=Nieprawda),
                         stat.S_ISDIR(entry_lstat.st_mode))
        self.assertEqual(entry.is_file(follow_symlinks=Nieprawda),
                         stat.S_ISREG(entry_lstat.st_mode))

        self.assert_stat_equal(entry.stat(),
                               entry_stat,
                               os.name == 'nt' oraz nie is_symlink)
        self.assert_stat_equal(entry.stat(follow_symlinks=Nieprawda),
                               entry_lstat,
                               os.name == 'nt')

    def test_attributes(self):
        link = hasattr(os, 'link')
        symlink = support.can_symlink()

        dirname = os.path.join(self.path, "dir")
        os.mkdir(dirname)
        filename = self.create_file("file.txt")
        jeżeli link:
            os.link(filename, os.path.join(self.path, "link_file.txt"))
        jeżeli symlink:
            os.symlink(dirname, os.path.join(self.path, "symlink_dir"),
                       target_is_directory=Prawda)
            os.symlink(filename, os.path.join(self.path, "symlink_file.txt"))

        names = ['dir', 'file.txt']
        jeżeli link:
            names.append('link_file.txt')
        jeżeli symlink:
            names.extend(('symlink_dir', 'symlink_file.txt'))
        entries = self.get_entries(names)

        entry = entries['dir']
        self.check_entry(entry, 'dir', Prawda, Nieprawda, Nieprawda)

        entry = entries['file.txt']
        self.check_entry(entry, 'file.txt', Nieprawda, Prawda, Nieprawda)

        jeżeli link:
            entry = entries['link_file.txt']
            self.check_entry(entry, 'link_file.txt', Nieprawda, Prawda, Nieprawda)

        jeżeli symlink:
            entry = entries['symlink_dir']
            self.check_entry(entry, 'symlink_dir', Prawda, Nieprawda, Prawda)

            entry = entries['symlink_file.txt']
            self.check_entry(entry, 'symlink_file.txt', Nieprawda, Prawda, Prawda)

    def get_entry(self, name):
        entries = list(os.scandir(self.path))
        self.assertEqual(len(entries), 1)

        entry = entries[0]
        self.assertEqual(entry.name, name)
        zwróć entry

    def create_file_entry(self):
        filename = self.create_file()
        zwróć self.get_entry(os.path.basename(filename))

    def test_current_directory(self):
        filename = self.create_file()
        old_dir = os.getcwd()
        spróbuj:
            os.chdir(self.path)

            # call scandir() without parameter: it must list the content
            # of the current directory
            entries = dict((entry.name, entry) dla entry w os.scandir())
            self.assertEqual(sorted(entries.keys()),
                             [os.path.basename(filename)])
        w_końcu:
            os.chdir(old_dir)

    def test_repr(self):
        entry = self.create_file_entry()
        self.assertEqual(repr(entry), "<DirEntry 'file.txt'>")

    def test_removed_dir(self):
        path = os.path.join(self.path, 'dir')

        os.mkdir(path)
        entry = self.get_entry('dir')
        os.rmdir(path)

        # On POSIX, is_dir() result depends jeżeli scandir() filled d_type albo nie
        jeżeli os.name == 'nt':
            self.assertPrawda(entry.is_dir())
        self.assertNieprawda(entry.is_file())
        self.assertNieprawda(entry.is_symlink())
        jeżeli os.name == 'nt':
            self.assertRaises(FileNotFoundError, entry.inode)
            # don't fail
            entry.stat()
            entry.stat(follow_symlinks=Nieprawda)
        inaczej:
            self.assertGreater(entry.inode(), 0)
            self.assertRaises(FileNotFoundError, entry.stat)
            self.assertRaises(FileNotFoundError, entry.stat, follow_symlinks=Nieprawda)

    def test_removed_file(self):
        entry = self.create_file_entry()
        os.unlink(entry.path)

        self.assertNieprawda(entry.is_dir())
        # On POSIX, is_dir() result depends jeżeli scandir() filled d_type albo nie
        jeżeli os.name == 'nt':
            self.assertPrawda(entry.is_file())
        self.assertNieprawda(entry.is_symlink())
        jeżeli os.name == 'nt':
            self.assertRaises(FileNotFoundError, entry.inode)
            # don't fail
            entry.stat()
            entry.stat(follow_symlinks=Nieprawda)
        inaczej:
            self.assertGreater(entry.inode(), 0)
            self.assertRaises(FileNotFoundError, entry.stat)
            self.assertRaises(FileNotFoundError, entry.stat, follow_symlinks=Nieprawda)

    def test_broken_symlink(self):
        jeżeli nie support.can_symlink():
            zwróć self.skipTest('cannot create symbolic link')

        filename = self.create_file("file.txt")
        os.symlink(filename,
                   os.path.join(self.path, "symlink.txt"))
        entries = self.get_entries(['file.txt', 'symlink.txt'])
        entry = entries['symlink.txt']
        os.unlink(filename)

        self.assertGreater(entry.inode(), 0)
        self.assertNieprawda(entry.is_dir())
        self.assertNieprawda(entry.is_file())  # broken symlink returns Nieprawda
        self.assertNieprawda(entry.is_dir(follow_symlinks=Nieprawda))
        self.assertNieprawda(entry.is_file(follow_symlinks=Nieprawda))
        self.assertPrawda(entry.is_symlink())
        self.assertRaises(FileNotFoundError, entry.stat)
        # don't fail
        entry.stat(follow_symlinks=Nieprawda)

    def test_bytes(self):
        jeżeli os.name == "nt":
            # On Windows, os.scandir(bytes) must podnieś an exception
            self.assertRaises(TypeError, os.scandir, b'.')
            zwróć

        self.create_file("file.txt")

        path_bytes = os.fsencode(self.path)
        entries = list(os.scandir(path_bytes))
        self.assertEqual(len(entries), 1, entries)
        entry = entries[0]

        self.assertEqual(entry.name, b'file.txt')
        self.assertEqual(entry.path,
                         os.fsencode(os.path.join(self.path, 'file.txt')))

    def test_empty_path(self):
        self.assertRaises(FileNotFoundError, os.scandir, '')

    def test_consume_iterator_twice(self):
        self.create_file("file.txt")
        iterator = os.scandir(self.path)

        entries = list(iterator)
        self.assertEqual(len(entries), 1, entries)

        # check than consuming the iterator twice doesn't podnieś exception
        entries2 = list(iterator)
        self.assertEqual(len(entries2), 0, entries2)

    def test_bad_path_type(self):
        dla obj w [1234, 1.234, {}, []]:
            self.assertRaises(TypeError, os.scandir, obj)


jeżeli __name__ == "__main__":
    unittest.main()
