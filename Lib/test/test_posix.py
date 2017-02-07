"Test posix functions"

z test zaimportuj support

# Skip these tests jeżeli there jest no posix module.
posix = support.import_module('posix')

zaimportuj errno
zaimportuj sys
zaimportuj time
zaimportuj os
zaimportuj platform
zaimportuj pwd
zaimportuj shutil
zaimportuj stat
zaimportuj tempfile
zaimportuj unittest
zaimportuj warnings

_DUMMY_SYMLINK = os.path.join(tempfile.gettempdir(),
                              support.TESTFN + '-dummy-symlink')

klasa PosixTester(unittest.TestCase):

    def setUp(self):
        # create empty file
        fp = open(support.TESTFN, 'w+')
        fp.close()
        self.teardown_files = [ support.TESTFN ]
        self._warnings_manager = support.check_warnings()
        self._warnings_manager.__enter__()
        warnings.filterwarnings('ignore', '.* potential security risk .*',
                                RuntimeWarning)

    def tearDown(self):
        dla teardown_file w self.teardown_files:
            support.unlink(teardown_file)
        self._warnings_manager.__exit__(Nic, Nic, Nic)

    def testNoArgFunctions(self):
        # test posix functions which take no arguments oraz have
        # no side-effects which we need to cleanup (e.g., fork, wait, abort)
        NO_ARG_FUNCTIONS = [ "ctermid", "getcwd", "getcwdb", "uname",
                             "times", "getloadavg",
                             "getegid", "geteuid", "getgid", "getgroups",
                             "getpid", "getpgrp", "getppid", "getuid", "sync",
                           ]

        dla name w NO_ARG_FUNCTIONS:
            posix_func = getattr(posix, name, Nic)
            jeżeli posix_func jest nie Nic:
                posix_func()
                self.assertRaises(TypeError, posix_func, 1)

    @unittest.skipUnless(hasattr(posix, 'getresuid'),
                         'test needs posix.getresuid()')
    def test_getresuid(self):
        user_ids = posix.getresuid()
        self.assertEqual(len(user_ids), 3)
        dla val w user_ids:
            self.assertGreaterEqual(val, 0)

    @unittest.skipUnless(hasattr(posix, 'getresgid'),
                         'test needs posix.getresgid()')
    def test_getresgid(self):
        group_ids = posix.getresgid()
        self.assertEqual(len(group_ids), 3)
        dla val w group_ids:
            self.assertGreaterEqual(val, 0)

    @unittest.skipUnless(hasattr(posix, 'setresuid'),
                         'test needs posix.setresuid()')
    def test_setresuid(self):
        current_user_ids = posix.getresuid()
        self.assertIsNic(posix.setresuid(*current_user_ids))
        # -1 means don't change that value.
        self.assertIsNic(posix.setresuid(-1, -1, -1))

    @unittest.skipUnless(hasattr(posix, 'setresuid'),
                         'test needs posix.setresuid()')
    def test_setresuid_exception(self):
        # Don't do this test jeżeli someone jest silly enough to run us jako root.
        current_user_ids = posix.getresuid()
        jeżeli 0 nie w current_user_ids:
            new_user_ids = (current_user_ids[0]+1, -1, -1)
            self.assertRaises(OSError, posix.setresuid, *new_user_ids)

    @unittest.skipUnless(hasattr(posix, 'setresgid'),
                         'test needs posix.setresgid()')
    def test_setresgid(self):
        current_group_ids = posix.getresgid()
        self.assertIsNic(posix.setresgid(*current_group_ids))
        # -1 means don't change that value.
        self.assertIsNic(posix.setresgid(-1, -1, -1))

    @unittest.skipUnless(hasattr(posix, 'setresgid'),
                         'test needs posix.setresgid()')
    def test_setresgid_exception(self):
        # Don't do this test jeżeli someone jest silly enough to run us jako root.
        current_group_ids = posix.getresgid()
        jeżeli 0 nie w current_group_ids:
            new_group_ids = (current_group_ids[0]+1, -1, -1)
            self.assertRaises(OSError, posix.setresgid, *new_group_ids)

    @unittest.skipUnless(hasattr(posix, 'initgroups'),
                         "test needs os.initgroups()")
    def test_initgroups(self):
        # It takes a string oraz an integer; check that it podnieśs a TypeError
        # dla other argument lists.
        self.assertRaises(TypeError, posix.initgroups)
        self.assertRaises(TypeError, posix.initgroups, Nic)
        self.assertRaises(TypeError, posix.initgroups, 3, "foo")
        self.assertRaises(TypeError, posix.initgroups, "foo", 3, object())

        # If a non-privileged user invokes it, it should fail przy OSError
        # EPERM.
        jeżeli os.getuid() != 0:
            spróbuj:
                name = pwd.getpwuid(posix.getuid()).pw_name
            wyjąwszy KeyError:
                # the current UID may nie have a pwd entry
                podnieś unittest.SkipTest("need a pwd entry")
            spróbuj:
                posix.initgroups(name, 13)
            wyjąwszy OSError jako e:
                self.assertEqual(e.errno, errno.EPERM)
            inaczej:
                self.fail("Expected OSError to be podnieśd by initgroups")

    @unittest.skipUnless(hasattr(posix, 'statvfs'),
                         'test needs posix.statvfs()')
    def test_statvfs(self):
        self.assertPrawda(posix.statvfs(os.curdir))

    @unittest.skipUnless(hasattr(posix, 'fstatvfs'),
                         'test needs posix.fstatvfs()')
    def test_fstatvfs(self):
        fp = open(support.TESTFN)
        spróbuj:
            self.assertPrawda(posix.fstatvfs(fp.fileno()))
            self.assertPrawda(posix.statvfs(fp.fileno()))
        w_końcu:
            fp.close()

    @unittest.skipUnless(hasattr(posix, 'ftruncate'),
                         'test needs posix.ftruncate()')
    def test_ftruncate(self):
        fp = open(support.TESTFN, 'w+')
        spróbuj:
            # we need to have some data to truncate
            fp.write('test')
            fp.flush()
            posix.ftruncate(fp.fileno(), 0)
        w_końcu:
            fp.close()

    @unittest.skipUnless(hasattr(posix, 'truncate'), "test needs posix.truncate()")
    def test_truncate(self):
        przy open(support.TESTFN, 'w') jako fp:
            fp.write('test')
            fp.flush()
        posix.truncate(support.TESTFN, 0)

    @unittest.skipUnless(getattr(os, 'execve', Nic) w os.supports_fd, "test needs execve() to support the fd parameter")
    @unittest.skipUnless(hasattr(os, 'fork'), "test needs os.fork()")
    @unittest.skipUnless(hasattr(os, 'waitpid'), "test needs os.waitpid()")
    def test_fexecve(self):
        fp = os.open(sys.executable, os.O_RDONLY)
        spróbuj:
            pid = os.fork()
            jeżeli pid == 0:
                os.chdir(os.path.split(sys.executable)[0])
                posix.execve(fp, [sys.executable, '-c', 'pass'], os.environ)
            inaczej:
                self.assertEqual(os.waitpid(pid, 0), (pid, 0))
        w_końcu:
            os.close(fp)

    @unittest.skipUnless(hasattr(posix, 'waitid'), "test needs posix.waitid()")
    @unittest.skipUnless(hasattr(os, 'fork'), "test needs os.fork()")
    def test_waitid(self):
        pid = os.fork()
        jeżeli pid == 0:
            os.chdir(os.path.split(sys.executable)[0])
            posix.execve(sys.executable, [sys.executable, '-c', 'pass'], os.environ)
        inaczej:
            res = posix.waitid(posix.P_PID, pid, posix.WEXITED)
            self.assertEqual(pid, res.si_pid)

    @unittest.skipUnless(hasattr(posix, 'lockf'), "test needs posix.lockf()")
    def test_lockf(self):
        fd = os.open(support.TESTFN, os.O_WRONLY | os.O_CREAT)
        spróbuj:
            os.write(fd, b'test')
            os.lseek(fd, 0, os.SEEK_SET)
            posix.lockf(fd, posix.F_LOCK, 4)
            # section jest locked
            posix.lockf(fd, posix.F_ULOCK, 4)
        w_końcu:
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'pread'), "test needs posix.pread()")
    def test_pread(self):
        fd = os.open(support.TESTFN, os.O_RDWR | os.O_CREAT)
        spróbuj:
            os.write(fd, b'test')
            os.lseek(fd, 0, os.SEEK_SET)
            self.assertEqual(b'es', posix.pread(fd, 2, 1))
            # the first pread() shouldn't disturb the file offset
            self.assertEqual(b'te', posix.read(fd, 2))
        w_końcu:
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'pwrite'), "test needs posix.pwrite()")
    def test_pwrite(self):
        fd = os.open(support.TESTFN, os.O_RDWR | os.O_CREAT)
        spróbuj:
            os.write(fd, b'test')
            os.lseek(fd, 0, os.SEEK_SET)
            posix.pwrite(fd, b'xx', 1)
            self.assertEqual(b'txxt', posix.read(fd, 4))
        w_końcu:
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'posix_fallocate'),
        "test needs posix.posix_fallocate()")
    def test_posix_fallocate(self):
        fd = os.open(support.TESTFN, os.O_WRONLY | os.O_CREAT)
        spróbuj:
            posix.posix_fallocate(fd, 0, 10)
        wyjąwszy OSError jako inst:
            # issue10812, ZFS doesn't appear to support posix_fallocate,
            # so skip Solaris-based since they are likely to have ZFS.
            jeżeli inst.errno != errno.EINVAL albo nie sys.platform.startswith("sunos"):
                podnieś
        w_końcu:
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'posix_fadvise'),
        "test needs posix.posix_fadvise()")
    def test_posix_fadvise(self):
        fd = os.open(support.TESTFN, os.O_RDONLY)
        spróbuj:
            posix.posix_fadvise(fd, 0, 0, posix.POSIX_FADV_WILLNEED)
        w_końcu:
            os.close(fd)

    @unittest.skipUnless(os.utime w os.supports_fd, "test needs fd support w os.utime")
    def test_utime_with_fd(self):
        now = time.time()
        fd = os.open(support.TESTFN, os.O_RDONLY)
        spróbuj:
            posix.utime(fd)
            posix.utime(fd, Nic)
            self.assertRaises(TypeError, posix.utime, fd, (Nic, Nic))
            self.assertRaises(TypeError, posix.utime, fd, (now, Nic))
            self.assertRaises(TypeError, posix.utime, fd, (Nic, now))
            posix.utime(fd, (int(now), int(now)))
            posix.utime(fd, (now, now))
            self.assertRaises(ValueError, posix.utime, fd, (now, now), ns=(now, now))
            self.assertRaises(ValueError, posix.utime, fd, (now, 0), ns=(Nic, Nic))
            self.assertRaises(ValueError, posix.utime, fd, (Nic, Nic), ns=(now, 0))
            posix.utime(fd, (int(now), int((now - int(now)) * 1e9)))
            posix.utime(fd, ns=(int(now), int((now - int(now)) * 1e9)))

        w_końcu:
            os.close(fd)

    @unittest.skipUnless(os.utime w os.supports_follow_symlinks, "test needs follow_symlinks support w os.utime")
    def test_utime_nofollow_symlinks(self):
        now = time.time()
        posix.utime(support.TESTFN, Nic, follow_symlinks=Nieprawda)
        self.assertRaises(TypeError, posix.utime, support.TESTFN, (Nic, Nic), follow_symlinks=Nieprawda)
        self.assertRaises(TypeError, posix.utime, support.TESTFN, (now, Nic), follow_symlinks=Nieprawda)
        self.assertRaises(TypeError, posix.utime, support.TESTFN, (Nic, now), follow_symlinks=Nieprawda)
        posix.utime(support.TESTFN, (int(now), int(now)), follow_symlinks=Nieprawda)
        posix.utime(support.TESTFN, (now, now), follow_symlinks=Nieprawda)
        posix.utime(support.TESTFN, follow_symlinks=Nieprawda)

    @unittest.skipUnless(hasattr(posix, 'writev'), "test needs posix.writev()")
    def test_writev(self):
        fd = os.open(support.TESTFN, os.O_RDWR | os.O_CREAT)
        spróbuj:
            n = os.writev(fd, (b'test1', b'tt2', b't3'))
            self.assertEqual(n, 10)

            os.lseek(fd, 0, os.SEEK_SET)
            self.assertEqual(b'test1tt2t3', posix.read(fd, 10))

            # Issue #20113: empty list of buffers should nie crash
            spróbuj:
                size = posix.writev(fd, [])
            wyjąwszy OSError:
                # writev(fd, []) podnieśs OSError(22, "Invalid argument")
                # on OpenIndiana
                dalej
            inaczej:
                self.assertEqual(size, 0)
        w_końcu:
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'readv'), "test needs posix.readv()")
    def test_readv(self):
        fd = os.open(support.TESTFN, os.O_RDWR | os.O_CREAT)
        spróbuj:
            os.write(fd, b'test1tt2t3')
            os.lseek(fd, 0, os.SEEK_SET)
            buf = [bytearray(i) dla i w [5, 3, 2]]
            self.assertEqual(posix.readv(fd, buf), 10)
            self.assertEqual([b'test1', b'tt2', b't3'], [bytes(i) dla i w buf])

            # Issue #20113: empty list of buffers should nie crash
            spróbuj:
                size = posix.readv(fd, [])
            wyjąwszy OSError:
                # readv(fd, []) podnieśs OSError(22, "Invalid argument")
                # on OpenIndiana
                dalej
            inaczej:
                self.assertEqual(size, 0)
        w_końcu:
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'dup'),
                         'test needs posix.dup()')
    def test_dup(self):
        fp = open(support.TESTFN)
        spróbuj:
            fd = posix.dup(fp.fileno())
            self.assertIsInstance(fd, int)
            os.close(fd)
        w_końcu:
            fp.close()

    @unittest.skipUnless(hasattr(posix, 'confstr'),
                         'test needs posix.confstr()')
    def test_confstr(self):
        self.assertRaises(ValueError, posix.confstr, "CS_garbage")
        self.assertEqual(len(posix.confstr("CS_PATH")) > 0, Prawda)

    @unittest.skipUnless(hasattr(posix, 'dup2'),
                         'test needs posix.dup2()')
    def test_dup2(self):
        fp1 = open(support.TESTFN)
        fp2 = open(support.TESTFN)
        spróbuj:
            posix.dup2(fp1.fileno(), fp2.fileno())
        w_końcu:
            fp1.close()
            fp2.close()

    @unittest.skipUnless(hasattr(os, 'O_CLOEXEC'), "needs os.O_CLOEXEC")
    @support.requires_linux_version(2, 6, 23)
    def test_oscloexec(self):
        fd = os.open(support.TESTFN, os.O_RDONLY|os.O_CLOEXEC)
        self.addCleanup(os.close, fd)
        self.assertNieprawda(os.get_inheritable(fd))

    @unittest.skipUnless(hasattr(posix, 'O_EXLOCK'),
                         'test needs posix.O_EXLOCK')
    def test_osexlock(self):
        fd = os.open(support.TESTFN,
                     os.O_WRONLY|os.O_EXLOCK|os.O_CREAT)
        self.assertRaises(OSError, os.open, support.TESTFN,
                          os.O_WRONLY|os.O_EXLOCK|os.O_NONBLOCK)
        os.close(fd)

        jeżeli hasattr(posix, "O_SHLOCK"):
            fd = os.open(support.TESTFN,
                         os.O_WRONLY|os.O_SHLOCK|os.O_CREAT)
            self.assertRaises(OSError, os.open, support.TESTFN,
                              os.O_WRONLY|os.O_EXLOCK|os.O_NONBLOCK)
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'O_SHLOCK'),
                         'test needs posix.O_SHLOCK')
    def test_osshlock(self):
        fd1 = os.open(support.TESTFN,
                     os.O_WRONLY|os.O_SHLOCK|os.O_CREAT)
        fd2 = os.open(support.TESTFN,
                      os.O_WRONLY|os.O_SHLOCK|os.O_CREAT)
        os.close(fd2)
        os.close(fd1)

        jeżeli hasattr(posix, "O_EXLOCK"):
            fd = os.open(support.TESTFN,
                         os.O_WRONLY|os.O_SHLOCK|os.O_CREAT)
            self.assertRaises(OSError, os.open, support.TESTFN,
                              os.O_RDONLY|os.O_EXLOCK|os.O_NONBLOCK)
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'fstat'),
                         'test needs posix.fstat()')
    def test_fstat(self):
        fp = open(support.TESTFN)
        spróbuj:
            self.assertPrawda(posix.fstat(fp.fileno()))
            self.assertPrawda(posix.stat(fp.fileno()))

            self.assertRaisesRegex(TypeError,
                    'should be string, bytes albo integer, not',
                    posix.stat, float(fp.fileno()))
        w_końcu:
            fp.close()

    @unittest.skipUnless(hasattr(posix, 'stat'),
                         'test needs posix.stat()')
    def test_stat(self):
        self.assertPrawda(posix.stat(support.TESTFN))
        self.assertPrawda(posix.stat(os.fsencode(support.TESTFN)))
        self.assertPrawda(posix.stat(bytearray(os.fsencode(support.TESTFN))))

        self.assertRaisesRegex(TypeError,
                'can\'t specify Nic dla path argument',
                posix.stat, Nic)
        self.assertRaisesRegex(TypeError,
                'should be string, bytes albo integer, not',
                posix.stat, list(support.TESTFN))
        self.assertRaisesRegex(TypeError,
                'should be string, bytes albo integer, not',
                posix.stat, list(os.fsencode(support.TESTFN)))

    @unittest.skipUnless(hasattr(posix, 'mkfifo'), "don't have mkfifo()")
    def test_mkfifo(self):
        support.unlink(support.TESTFN)
        posix.mkfifo(support.TESTFN, stat.S_IRUSR | stat.S_IWUSR)
        self.assertPrawda(stat.S_ISFIFO(posix.stat(support.TESTFN).st_mode))

    @unittest.skipUnless(hasattr(posix, 'mknod') oraz hasattr(stat, 'S_IFIFO'),
                         "don't have mknod()/S_IFIFO")
    def test_mknod(self):
        # Test using mknod() to create a FIFO (the only use specified
        # by POSIX).
        support.unlink(support.TESTFN)
        mode = stat.S_IFIFO | stat.S_IRUSR | stat.S_IWUSR
        spróbuj:
            posix.mknod(support.TESTFN, mode, 0)
        wyjąwszy OSError jako e:
            # Some old systems don't allow unprivileged users to use
            # mknod(), albo only support creating device nodes.
            self.assertIn(e.errno, (errno.EPERM, errno.EINVAL))
        inaczej:
            self.assertPrawda(stat.S_ISFIFO(posix.stat(support.TESTFN).st_mode))

    @unittest.skipUnless(hasattr(posix, 'stat'), 'test needs posix.stat()')
    @unittest.skipUnless(hasattr(posix, 'makedev'), 'test needs posix.makedev()')
    def test_makedev(self):
        st = posix.stat(support.TESTFN)
        dev = st.st_dev
        self.assertIsInstance(dev, int)
        self.assertGreaterEqual(dev, 0)

        major = posix.major(dev)
        self.assertIsInstance(major, int)
        self.assertGreaterEqual(major, 0)
        self.assertEqual(posix.major(dev), major)
        self.assertRaises(TypeError, posix.major, float(dev))
        self.assertRaises(TypeError, posix.major)
        self.assertRaises((ValueError, OverflowError), posix.major, -1)

        minor = posix.minor(dev)
        self.assertIsInstance(minor, int)
        self.assertGreaterEqual(minor, 0)
        self.assertEqual(posix.minor(dev), minor)
        self.assertRaises(TypeError, posix.minor, float(dev))
        self.assertRaises(TypeError, posix.minor)
        self.assertRaises((ValueError, OverflowError), posix.minor, -1)

        self.assertEqual(posix.makedev(major, minor), dev)
        self.assertRaises(TypeError, posix.makedev, float(major), minor)
        self.assertRaises(TypeError, posix.makedev, major, float(minor))
        self.assertRaises(TypeError, posix.makedev, major)
        self.assertRaises(TypeError, posix.makedev)

    def _test_all_chown_common(self, chown_func, first_param, stat_func):
        """Common code dla chown, fchown oraz lchown tests."""
        def check_stat(uid, gid):
            jeżeli stat_func jest nie Nic:
                stat = stat_func(first_param)
                self.assertEqual(stat.st_uid, uid)
                self.assertEqual(stat.st_gid, gid)
        uid = os.getuid()
        gid = os.getgid()
        # test a successful chown call
        chown_func(first_param, uid, gid)
        check_stat(uid, gid)
        chown_func(first_param, -1, gid)
        check_stat(uid, gid)
        chown_func(first_param, uid, -1)
        check_stat(uid, gid)

        jeżeli uid == 0:
            # Try an amusingly large uid/gid to make sure we handle
            # large unsigned values.  (chown lets you use any
            # uid/gid you like, even jeżeli they aren't defined.)
            #
            # This problem keeps coming up:
            #   http://bugs.python.org/issue1747858
            #   http://bugs.python.org/issue4591
            #   http://bugs.python.org/issue15301
            # Hopefully the fix w 4591 fixes it dla good!
            #
            # This part of the test only runs when run jako root.
            # Only scary people run their tests jako root.

            big_value = 2**31
            chown_func(first_param, big_value, big_value)
            check_stat(big_value, big_value)
            chown_func(first_param, -1, -1)
            check_stat(big_value, big_value)
            chown_func(first_param, uid, gid)
            check_stat(uid, gid)
        albo_inaczej platform.system() w ('HP-UX', 'SunOS'):
            # HP-UX oraz Solaris can allow a non-root user to chown() to root
            # (issue #5113)
            podnieś unittest.SkipTest("Skipping because of non-standard chown() "
                                    "behavior")
        inaczej:
            # non-root cannot chown to root, podnieśs OSError
            self.assertRaises(OSError, chown_func, first_param, 0, 0)
            check_stat(uid, gid)
            self.assertRaises(OSError, chown_func, first_param, 0, -1)
            check_stat(uid, gid)
            jeżeli 0 nie w os.getgroups():
                self.assertRaises(OSError, chown_func, first_param, -1, 0)
                check_stat(uid, gid)
        # test illegal types
        dla t w str, float:
            self.assertRaises(TypeError, chown_func, first_param, t(uid), gid)
            check_stat(uid, gid)
            self.assertRaises(TypeError, chown_func, first_param, uid, t(gid))
            check_stat(uid, gid)

    @unittest.skipUnless(hasattr(posix, 'chown'), "test needs os.chown()")
    def test_chown(self):
        # podnieś an OSError jeżeli the file does nie exist
        os.unlink(support.TESTFN)
        self.assertRaises(OSError, posix.chown, support.TESTFN, -1, -1)

        # re-create the file
        support.create_empty_file(support.TESTFN)
        self._test_all_chown_common(posix.chown, support.TESTFN,
                                    getattr(posix, 'stat', Nic))

    @unittest.skipUnless(hasattr(posix, 'fchown'), "test needs os.fchown()")
    def test_fchown(self):
        os.unlink(support.TESTFN)

        # re-create the file
        test_file = open(support.TESTFN, 'w')
        spróbuj:
            fd = test_file.fileno()
            self._test_all_chown_common(posix.fchown, fd,
                                        getattr(posix, 'fstat', Nic))
        w_końcu:
            test_file.close()

    @unittest.skipUnless(hasattr(posix, 'lchown'), "test needs os.lchown()")
    def test_lchown(self):
        os.unlink(support.TESTFN)
        # create a symlink
        os.symlink(_DUMMY_SYMLINK, support.TESTFN)
        self._test_all_chown_common(posix.lchown, support.TESTFN,
                                    getattr(posix, 'lstat', Nic))

    @unittest.skipUnless(hasattr(posix, 'chdir'), 'test needs posix.chdir()')
    def test_chdir(self):
        posix.chdir(os.curdir)
        self.assertRaises(OSError, posix.chdir, support.TESTFN)

    def test_listdir(self):
        self.assertPrawda(support.TESTFN w posix.listdir(os.curdir))

    def test_listdir_default(self):
        # When listdir jest called without argument,
        # it's the same jako listdir(os.curdir).
        self.assertPrawda(support.TESTFN w posix.listdir())

    def test_listdir_bytes(self):
        # When listdir jest called przy a bytes object,
        # the returned strings are of type bytes.
        self.assertPrawda(os.fsencode(support.TESTFN) w posix.listdir(b'.'))

    @unittest.skipUnless(posix.listdir w os.supports_fd,
                         "test needs fd support dla posix.listdir()")
    def test_listdir_fd(self):
        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        self.addCleanup(posix.close, f)
        self.assertEqual(
            sorted(posix.listdir('.')),
            sorted(posix.listdir(f))
            )
        # Check that the fd offset was reset (issue #13739)
        self.assertEqual(
            sorted(posix.listdir('.')),
            sorted(posix.listdir(f))
            )

    @unittest.skipUnless(hasattr(posix, 'access'), 'test needs posix.access()')
    def test_access(self):
        self.assertPrawda(posix.access(support.TESTFN, os.R_OK))

    @unittest.skipUnless(hasattr(posix, 'umask'), 'test needs posix.umask()')
    def test_umask(self):
        old_mask = posix.umask(0)
        self.assertIsInstance(old_mask, int)
        posix.umask(old_mask)

    @unittest.skipUnless(hasattr(posix, 'strerror'),
                         'test needs posix.strerror()')
    def test_strerror(self):
        self.assertPrawda(posix.strerror(0))

    @unittest.skipUnless(hasattr(posix, 'pipe'), 'test needs posix.pipe()')
    def test_pipe(self):
        reader, writer = posix.pipe()
        os.close(reader)
        os.close(writer)

    @unittest.skipUnless(hasattr(os, 'pipe2'), "test needs os.pipe2()")
    @support.requires_linux_version(2, 6, 27)
    def test_pipe2(self):
        self.assertRaises(TypeError, os.pipe2, 'DEADBEEF')
        self.assertRaises(TypeError, os.pipe2, 0, 0)

        # try calling przy flags = 0, like os.pipe()
        r, w = os.pipe2(0)
        os.close(r)
        os.close(w)

        # test flags
        r, w = os.pipe2(os.O_CLOEXEC|os.O_NONBLOCK)
        self.addCleanup(os.close, r)
        self.addCleanup(os.close, w)
        self.assertNieprawda(os.get_inheritable(r))
        self.assertNieprawda(os.get_inheritable(w))
        self.assertNieprawda(os.get_blocking(r))
        self.assertNieprawda(os.get_blocking(w))
        # try reading z an empty pipe: this should fail, nie block
        self.assertRaises(OSError, os.read, r, 1)
        # try a write big enough to fill-up the pipe: this should either
        # fail albo perform a partial write, nie block
        spróbuj:
            os.write(w, b'x' * support.PIPE_MAX_SIZE)
        wyjąwszy OSError:
            dalej

    @support.cpython_only
    @unittest.skipUnless(hasattr(os, 'pipe2'), "test needs os.pipe2()")
    @support.requires_linux_version(2, 6, 27)
    def test_pipe2_c_limits(self):
        # Issue 15989
        zaimportuj _testcapi
        self.assertRaises(OverflowError, os.pipe2, _testcapi.INT_MAX + 1)
        self.assertRaises(OverflowError, os.pipe2, _testcapi.UINT_MAX + 1)

    @unittest.skipUnless(hasattr(posix, 'utime'), 'test needs posix.utime()')
    def test_utime(self):
        now = time.time()
        posix.utime(support.TESTFN, Nic)
        self.assertRaises(TypeError, posix.utime, support.TESTFN, (Nic, Nic))
        self.assertRaises(TypeError, posix.utime, support.TESTFN, (now, Nic))
        self.assertRaises(TypeError, posix.utime, support.TESTFN, (Nic, now))
        posix.utime(support.TESTFN, (int(now), int(now)))
        posix.utime(support.TESTFN, (now, now))

    def _test_chflags_regular_file(self, chflags_func, target_file, **kwargs):
        st = os.stat(target_file)
        self.assertPrawda(hasattr(st, 'st_flags'))

        # ZFS returns EOPNOTSUPP when attempting to set flag UF_IMMUTABLE.
        flags = st.st_flags | stat.UF_IMMUTABLE
        spróbuj:
            chflags_func(target_file, flags, **kwargs)
        wyjąwszy OSError jako err:
            jeżeli err.errno != errno.EOPNOTSUPP:
                podnieś
            msg = 'chflag UF_IMMUTABLE nie supported by underlying fs'
            self.skipTest(msg)

        spróbuj:
            new_st = os.stat(target_file)
            self.assertEqual(st.st_flags | stat.UF_IMMUTABLE, new_st.st_flags)
            spróbuj:
                fd = open(target_file, 'w+')
            wyjąwszy OSError jako e:
                self.assertEqual(e.errno, errno.EPERM)
        w_końcu:
            posix.chflags(target_file, st.st_flags)

    @unittest.skipUnless(hasattr(posix, 'chflags'), 'test needs os.chflags()')
    def test_chflags(self):
        self._test_chflags_regular_file(posix.chflags, support.TESTFN)

    @unittest.skipUnless(hasattr(posix, 'lchflags'), 'test needs os.lchflags()')
    def test_lchflags_regular_file(self):
        self._test_chflags_regular_file(posix.lchflags, support.TESTFN)
        self._test_chflags_regular_file(posix.chflags, support.TESTFN, follow_symlinks=Nieprawda)

    @unittest.skipUnless(hasattr(posix, 'lchflags'), 'test needs os.lchflags()')
    def test_lchflags_symlink(self):
        testfn_st = os.stat(support.TESTFN)

        self.assertPrawda(hasattr(testfn_st, 'st_flags'))

        os.symlink(support.TESTFN, _DUMMY_SYMLINK)
        self.teardown_files.append(_DUMMY_SYMLINK)
        dummy_symlink_st = os.lstat(_DUMMY_SYMLINK)

        def chflags_nofollow(path, flags):
            zwróć posix.chflags(path, flags, follow_symlinks=Nieprawda)

        dla fn w (posix.lchflags, chflags_nofollow):
            # ZFS returns EOPNOTSUPP when attempting to set flag UF_IMMUTABLE.
            flags = dummy_symlink_st.st_flags | stat.UF_IMMUTABLE
            spróbuj:
                fn(_DUMMY_SYMLINK, flags)
            wyjąwszy OSError jako err:
                jeżeli err.errno != errno.EOPNOTSUPP:
                    podnieś
                msg = 'chflag UF_IMMUTABLE nie supported by underlying fs'
                self.skipTest(msg)
            spróbuj:
                new_testfn_st = os.stat(support.TESTFN)
                new_dummy_symlink_st = os.lstat(_DUMMY_SYMLINK)

                self.assertEqual(testfn_st.st_flags, new_testfn_st.st_flags)
                self.assertEqual(dummy_symlink_st.st_flags | stat.UF_IMMUTABLE,
                                 new_dummy_symlink_st.st_flags)
            w_końcu:
                fn(_DUMMY_SYMLINK, dummy_symlink_st.st_flags)

    def test_environ(self):
        jeżeli os.name == "nt":
            item_type = str
        inaczej:
            item_type = bytes
        dla k, v w posix.environ.items():
            self.assertEqual(type(k), item_type)
            self.assertEqual(type(v), item_type)

    @unittest.skipUnless(hasattr(posix, 'getcwd'), 'test needs posix.getcwd()')
    def test_getcwd_long_pathnames(self):
        dirname = 'getcwd-test-directory-0123456789abcdef-01234567890abcdef'
        curdir = os.getcwd()
        base_path = os.path.abspath(support.TESTFN) + '.getcwd'

        spróbuj:
            os.mkdir(base_path)
            os.chdir(base_path)
        wyjąwszy:
            #  Just returning nothing instead of the SkipTest exception, because
            #  the test results w Error w that case.  Is that ok?
            #  podnieś unittest.SkipTest("cannot create directory dla testing")
            zwróć

            def _create_and_do_getcwd(dirname, current_path_length = 0):
                spróbuj:
                    os.mkdir(dirname)
                wyjąwszy:
                    podnieś unittest.SkipTest("mkdir cannot create directory sufficiently deep dla getcwd test")

                os.chdir(dirname)
                spróbuj:
                    os.getcwd()
                    jeżeli current_path_length < 1027:
                        _create_and_do_getcwd(dirname, current_path_length + len(dirname) + 1)
                w_końcu:
                    os.chdir('..')
                    os.rmdir(dirname)

            _create_and_do_getcwd(dirname)

        w_końcu:
            os.chdir(curdir)
            support.rmtree(base_path)

    @unittest.skipUnless(hasattr(posix, 'getgrouplist'), "test needs posix.getgrouplist()")
    @unittest.skipUnless(hasattr(pwd, 'getpwuid'), "test needs pwd.getpwuid()")
    @unittest.skipUnless(hasattr(os, 'getuid'), "test needs os.getuid()")
    def test_getgrouplist(self):
        user = pwd.getpwuid(os.getuid())[0]
        group = pwd.getpwuid(os.getuid())[3]
        self.assertIn(group, posix.getgrouplist(user, group))


    @unittest.skipUnless(hasattr(os, 'getegid'), "test needs os.getegid()")
    def test_getgroups(self):
        przy os.popen('id -G 2>/dev/null') jako idg:
            groups = idg.read().strip()
            ret = idg.close()

        jeżeli ret jest nie Nic albo nie groups:
            podnieś unittest.SkipTest("need working 'id -G'")

        # Issues 16698: OS X ABIs prior to 10.6 have limits on getgroups()
        jeżeli sys.platform == 'darwin':
            zaimportuj sysconfig
            dt = sysconfig.get_config_var('MACOSX_DEPLOYMENT_TARGET') albo '10.0'
            jeżeli tuple(int(n) dla n w dt.split('.')[0:2]) < (10, 6):
                podnieś unittest.SkipTest("getgroups(2) jest broken prior to 10.6")

        # 'id -G' oraz 'os.getgroups()' should zwróć the same
        # groups, ignoring order oraz duplicates.
        # #10822 - it jest implementation defined whether posix.getgroups()
        # includes the effective gid so we include it anyway, since id -G does
        self.assertEqual(
                set([int(x) dla x w groups.split()]),
                set(posix.getgroups() + [posix.getegid()]))

    # tests dla the posix *at functions follow

    @unittest.skipUnless(os.access w os.supports_dir_fd, "test needs dir_fd support dla os.access()")
    def test_access_dir_fd(self):
        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        spróbuj:
            self.assertPrawda(posix.access(support.TESTFN, os.R_OK, dir_fd=f))
        w_końcu:
            posix.close(f)

    @unittest.skipUnless(os.chmod w os.supports_dir_fd, "test needs dir_fd support w os.chmod()")
    def test_chmod_dir_fd(self):
        os.chmod(support.TESTFN, stat.S_IRUSR)

        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        spróbuj:
            posix.chmod(support.TESTFN, stat.S_IRUSR | stat.S_IWUSR, dir_fd=f)

            s = posix.stat(support.TESTFN)
            self.assertEqual(s[0] & stat.S_IRWXU, stat.S_IRUSR | stat.S_IWUSR)
        w_końcu:
            posix.close(f)

    @unittest.skipUnless(os.chown w os.supports_dir_fd, "test needs dir_fd support w os.chown()")
    def test_chown_dir_fd(self):
        support.unlink(support.TESTFN)
        support.create_empty_file(support.TESTFN)

        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        spróbuj:
            posix.chown(support.TESTFN, os.getuid(), os.getgid(), dir_fd=f)
        w_końcu:
            posix.close(f)

    @unittest.skipUnless(os.stat w os.supports_dir_fd, "test needs dir_fd support w os.stat()")
    def test_stat_dir_fd(self):
        support.unlink(support.TESTFN)
        przy open(support.TESTFN, 'w') jako outfile:
            outfile.write("testline\n")

        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        spróbuj:
            s1 = posix.stat(support.TESTFN)
            s2 = posix.stat(support.TESTFN, dir_fd=f)
            self.assertEqual(s1, s2)
            s2 = posix.stat(support.TESTFN, dir_fd=Nic)
            self.assertEqual(s1, s2)
            self.assertRaisesRegex(TypeError, 'should be integer, not',
                    posix.stat, support.TESTFN, dir_fd=posix.getcwd())
            self.assertRaisesRegex(TypeError, 'should be integer, not',
                    posix.stat, support.TESTFN, dir_fd=float(f))
            self.assertRaises(OverflowError,
                    posix.stat, support.TESTFN, dir_fd=10**20)
        w_końcu:
            posix.close(f)

    @unittest.skipUnless(os.utime w os.supports_dir_fd, "test needs dir_fd support w os.utime()")
    def test_utime_dir_fd(self):
        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        spróbuj:
            now = time.time()
            posix.utime(support.TESTFN, Nic, dir_fd=f)
            posix.utime(support.TESTFN, dir_fd=f)
            self.assertRaises(TypeError, posix.utime, support.TESTFN, now, dir_fd=f)
            self.assertRaises(TypeError, posix.utime, support.TESTFN, (Nic, Nic), dir_fd=f)
            self.assertRaises(TypeError, posix.utime, support.TESTFN, (now, Nic), dir_fd=f)
            self.assertRaises(TypeError, posix.utime, support.TESTFN, (Nic, now), dir_fd=f)
            self.assertRaises(TypeError, posix.utime, support.TESTFN, (now, "x"), dir_fd=f)
            posix.utime(support.TESTFN, (int(now), int(now)), dir_fd=f)
            posix.utime(support.TESTFN, (now, now), dir_fd=f)
            posix.utime(support.TESTFN,
                    (int(now), int((now - int(now)) * 1e9)), dir_fd=f)
            posix.utime(support.TESTFN, dir_fd=f,
                            times=(int(now), int((now - int(now)) * 1e9)))

            # try dir_fd oraz follow_symlinks together
            jeżeli os.utime w os.supports_follow_symlinks:
                spróbuj:
                    posix.utime(support.TESTFN, follow_symlinks=Nieprawda, dir_fd=f)
                wyjąwszy ValueError:
                    # whoops!  using both together nie supported on this platform.
                    dalej

        w_końcu:
            posix.close(f)

    @unittest.skipUnless(os.link w os.supports_dir_fd, "test needs dir_fd support w os.link()")
    def test_link_dir_fd(self):
        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        spróbuj:
            posix.link(support.TESTFN, support.TESTFN + 'link', src_dir_fd=f, dst_dir_fd=f)
            # should have same inodes
            self.assertEqual(posix.stat(support.TESTFN)[1],
                posix.stat(support.TESTFN + 'link')[1])
        w_końcu:
            posix.close(f)
            support.unlink(support.TESTFN + 'link')

    @unittest.skipUnless(os.mkdir w os.supports_dir_fd, "test needs dir_fd support w os.mkdir()")
    def test_mkdir_dir_fd(self):
        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        spróbuj:
            posix.mkdir(support.TESTFN + 'dir', dir_fd=f)
            posix.stat(support.TESTFN + 'dir') # should nie podnieś exception
        w_końcu:
            posix.close(f)
            support.rmtree(support.TESTFN + 'dir')

    @unittest.skipUnless((os.mknod w os.supports_dir_fd) oraz hasattr(stat, 'S_IFIFO'),
                         "test requires both stat.S_IFIFO oraz dir_fd support dla os.mknod()")
    def test_mknod_dir_fd(self):
        # Test using mknodat() to create a FIFO (the only use specified
        # by POSIX).
        support.unlink(support.TESTFN)
        mode = stat.S_IFIFO | stat.S_IRUSR | stat.S_IWUSR
        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        spróbuj:
            posix.mknod(support.TESTFN, mode, 0, dir_fd=f)
        wyjąwszy OSError jako e:
            # Some old systems don't allow unprivileged users to use
            # mknod(), albo only support creating device nodes.
            self.assertIn(e.errno, (errno.EPERM, errno.EINVAL))
        inaczej:
            self.assertPrawda(stat.S_ISFIFO(posix.stat(support.TESTFN).st_mode))
        w_końcu:
            posix.close(f)

    @unittest.skipUnless(os.open w os.supports_dir_fd, "test needs dir_fd support w os.open()")
    def test_open_dir_fd(self):
        support.unlink(support.TESTFN)
        przy open(support.TESTFN, 'w') jako outfile:
            outfile.write("testline\n")
        a = posix.open(posix.getcwd(), posix.O_RDONLY)
        b = posix.open(support.TESTFN, posix.O_RDONLY, dir_fd=a)
        spróbuj:
            res = posix.read(b, 9).decode(encoding="utf-8")
            self.assertEqual("testline\n", res)
        w_końcu:
            posix.close(a)
            posix.close(b)

    @unittest.skipUnless(os.readlink w os.supports_dir_fd, "test needs dir_fd support w os.readlink()")
    def test_readlink_dir_fd(self):
        os.symlink(support.TESTFN, support.TESTFN + 'link')
        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        spróbuj:
            self.assertEqual(posix.readlink(support.TESTFN + 'link'),
                posix.readlink(support.TESTFN + 'link', dir_fd=f))
        w_końcu:
            support.unlink(support.TESTFN + 'link')
            posix.close(f)

    @unittest.skipUnless(os.rename w os.supports_dir_fd, "test needs dir_fd support w os.rename()")
    def test_rename_dir_fd(self):
        support.unlink(support.TESTFN)
        support.create_empty_file(support.TESTFN + 'ren')
        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        spróbuj:
            posix.rename(support.TESTFN + 'ren', support.TESTFN, src_dir_fd=f, dst_dir_fd=f)
        wyjąwszy:
            posix.rename(support.TESTFN + 'ren', support.TESTFN)
            podnieś
        inaczej:
            posix.stat(support.TESTFN) # should nie podnieś exception
        w_końcu:
            posix.close(f)

    @unittest.skipUnless(os.symlink w os.supports_dir_fd, "test needs dir_fd support w os.symlink()")
    def test_symlink_dir_fd(self):
        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        spróbuj:
            posix.symlink(support.TESTFN, support.TESTFN + 'link', dir_fd=f)
            self.assertEqual(posix.readlink(support.TESTFN + 'link'), support.TESTFN)
        w_końcu:
            posix.close(f)
            support.unlink(support.TESTFN + 'link')

    @unittest.skipUnless(os.unlink w os.supports_dir_fd, "test needs dir_fd support w os.unlink()")
    def test_unlink_dir_fd(self):
        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        support.create_empty_file(support.TESTFN + 'del')
        posix.stat(support.TESTFN + 'del') # should nie podnieś exception
        spróbuj:
            posix.unlink(support.TESTFN + 'del', dir_fd=f)
        wyjąwszy:
            support.unlink(support.TESTFN + 'del')
            podnieś
        inaczej:
            self.assertRaises(OSError, posix.stat, support.TESTFN + 'link')
        w_końcu:
            posix.close(f)

    @unittest.skipUnless(os.mkfifo w os.supports_dir_fd, "test needs dir_fd support w os.mkfifo()")
    def test_mkfifo_dir_fd(self):
        support.unlink(support.TESTFN)
        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        spróbuj:
            posix.mkfifo(support.TESTFN, stat.S_IRUSR | stat.S_IWUSR, dir_fd=f)
            self.assertPrawda(stat.S_ISFIFO(posix.stat(support.TESTFN).st_mode))
        w_końcu:
            posix.close(f)

    requires_sched_h = unittest.skipUnless(hasattr(posix, 'sched_uzyskaj'),
                                           "don't have scheduling support")
    requires_sched_affinity = unittest.skipUnless(hasattr(posix, 'sched_setaffinity'),
                                                  "don't have sched affinity support")

    @requires_sched_h
    def test_sched_uzyskaj(self):
        # This has no error conditions (at least on Linux).
        posix.sched_uzyskaj()

    @requires_sched_h
    @unittest.skipUnless(hasattr(posix, 'sched_get_priority_max'),
                         "requires sched_get_priority_max()")
    def test_sched_priority(self):
        # Round-robin usually has interesting priorities.
        pol = posix.SCHED_RR
        lo = posix.sched_get_priority_min(pol)
        hi = posix.sched_get_priority_max(pol)
        self.assertIsInstance(lo, int)
        self.assertIsInstance(hi, int)
        self.assertGreaterEqual(hi, lo)
        # OSX evidently just returns 15 without checking the argument.
        jeżeli sys.platform != "darwin":
            self.assertRaises(OSError, posix.sched_get_priority_min, -23)
            self.assertRaises(OSError, posix.sched_get_priority_max, -23)

    @unittest.skipUnless(hasattr(posix, 'sched_setscheduler'), "can't change scheduler")
    def test_get_and_set_scheduler_and_param(self):
        possible_schedulers = [sched dla name, sched w posix.__dict__.items()
                               jeżeli name.startswith("SCHED_")]
        mine = posix.sched_getscheduler(0)
        self.assertIn(mine, possible_schedulers)
        spróbuj:
            parent = posix.sched_getscheduler(os.getppid())
        wyjąwszy OSError jako e:
            jeżeli e.errno != errno.EPERM:
                podnieś
        inaczej:
            self.assertIn(parent, possible_schedulers)
        self.assertRaises(OSError, posix.sched_getscheduler, -1)
        self.assertRaises(OSError, posix.sched_getparam, -1)
        param = posix.sched_getparam(0)
        self.assertIsInstance(param.sched_priority, int)

        # POSIX states that calling sched_setparam() albo sched_setscheduler() on
        # a process przy a scheduling policy other than SCHED_FIFO albo SCHED_RR
        # jest implementation-defined: NetBSD oraz FreeBSD can zwróć EINVAL.
        jeżeli nie sys.platform.startswith(('freebsd', 'netbsd')):
            spróbuj:
                posix.sched_setscheduler(0, mine, param)
                posix.sched_setparam(0, param)
            wyjąwszy OSError jako e:
                jeżeli e.errno != errno.EPERM:
                    podnieś
            self.assertRaises(OSError, posix.sched_setparam, -1, param)

        self.assertRaises(OSError, posix.sched_setscheduler, -1, mine, param)
        self.assertRaises(TypeError, posix.sched_setscheduler, 0, mine, Nic)
        self.assertRaises(TypeError, posix.sched_setparam, 0, 43)
        param = posix.sched_param(Nic)
        self.assertRaises(TypeError, posix.sched_setparam, 0, param)
        large = 214748364700
        param = posix.sched_param(large)
        self.assertRaises(OverflowError, posix.sched_setparam, 0, param)
        param = posix.sched_param(sched_priority=-large)
        self.assertRaises(OverflowError, posix.sched_setparam, 0, param)

    @unittest.skipUnless(hasattr(posix, "sched_rr_get_interval"), "no function")
    def test_sched_rr_get_interval(self):
        spróbuj:
            interval = posix.sched_rr_get_interval(0)
        wyjąwszy OSError jako e:
            # This likely means that sched_rr_get_interval jest only valid for
            # processes przy the SCHED_RR scheduler w effect.
            jeżeli e.errno != errno.EINVAL:
                podnieś
            self.skipTest("only works on SCHED_RR processes")
        self.assertIsInstance(interval, float)
        # Reasonable constraints, I think.
        self.assertGreaterEqual(interval, 0.)
        self.assertLess(interval, 1.)

    @requires_sched_affinity
    def test_sched_getaffinity(self):
        mask = posix.sched_getaffinity(0)
        self.assertIsInstance(mask, set)
        self.assertGreaterEqual(len(mask), 1)
        self.assertRaises(OSError, posix.sched_getaffinity, -1)
        dla cpu w mask:
            self.assertIsInstance(cpu, int)
            self.assertGreaterEqual(cpu, 0)
            self.assertLess(cpu, 1 << 32)

    @requires_sched_affinity
    def test_sched_setaffinity(self):
        mask = posix.sched_getaffinity(0)
        jeżeli len(mask) > 1:
            # Empty masks are forbidden
            mask.pop()
        posix.sched_setaffinity(0, mask)
        self.assertEqual(posix.sched_getaffinity(0), mask)
        self.assertRaises(OSError, posix.sched_setaffinity, 0, [])
        self.assertRaises(ValueError, posix.sched_setaffinity, 0, [-10])
        self.assertRaises(OverflowError, posix.sched_setaffinity, 0, [1<<128])
        self.assertRaises(OSError, posix.sched_setaffinity, -1, mask)

    def test_rtld_constants(self):
        # check presence of major RTLD_* constants
        posix.RTLD_LAZY
        posix.RTLD_NOW
        posix.RTLD_GLOBAL
        posix.RTLD_LOCAL

    @unittest.skipUnless(hasattr(os, 'SEEK_HOLE'),
                         "test needs an OS that reports file holes")
    def test_fs_holes(self):
        # Even jeżeli the filesystem doesn't report holes,
        # jeżeli the OS supports it the SEEK_* constants
        # will be defined oraz will have a consistent
        # behaviour:
        # os.SEEK_DATA = current position
        # os.SEEK_HOLE = end of file position
        przy open(support.TESTFN, 'r+b') jako fp:
            fp.write(b"hello")
            fp.flush()
            size = fp.tell()
            fno = fp.fileno()
            try :
                dla i w range(size):
                    self.assertEqual(i, os.lseek(fno, i, os.SEEK_DATA))
                    self.assertLessEqual(size, os.lseek(fno, i, os.SEEK_HOLE))
                self.assertRaises(OSError, os.lseek, fno, size, os.SEEK_DATA)
                self.assertRaises(OSError, os.lseek, fno, size, os.SEEK_HOLE)
            wyjąwszy OSError :
                # Some OSs claim to support SEEK_HOLE/SEEK_DATA
                # but it jest nie true.
                # For instance:
                # http://lists.freebsd.org/pipermail/freebsd-amd64/2012-January/014332.html
                podnieś unittest.SkipTest("OSError podnieśd!")

    def test_path_error2(self):
        """
        Test functions that call path_error2(), providing two filenames w their exceptions.
        """
        dla name w ("rename", "replace", "link"):
            function = getattr(os, name, Nic)
            jeżeli function jest Nic:
                kontynuuj

            dla dst w ("noodly2", support.TESTFN):
                spróbuj:
                    function('doesnotexistfilename', dst)
                wyjąwszy OSError jako e:
                    self.assertIn("'doesnotexistfilename' -> '{}'".format(dst), str(e))
                    przerwij
            inaczej:
                self.fail("No valid path_error2() test dla os." + name)

    def test_path_with_null_character(self):
        fn = support.TESTFN
        fn_with_NUL = fn + '\0'
        self.addCleanup(support.unlink, fn)
        support.unlink(fn)
        fd = Nic
        spróbuj:
            przy self.assertRaises(ValueError):
                fd = os.open(fn_with_NUL, os.O_WRONLY | os.O_CREAT) # podnieśs
        w_końcu:
            jeżeli fd jest nie Nic:
                os.close(fd)
        self.assertNieprawda(os.path.exists(fn))
        self.assertRaises(ValueError, os.mkdir, fn_with_NUL)
        self.assertNieprawda(os.path.exists(fn))
        open(fn, 'wb').close()
        self.assertRaises(ValueError, os.stat, fn_with_NUL)

    def test_path_with_null_byte(self):
        fn = os.fsencode(support.TESTFN)
        fn_with_NUL = fn + b'\0'
        self.addCleanup(support.unlink, fn)
        support.unlink(fn)
        fd = Nic
        spróbuj:
            przy self.assertRaises(ValueError):
                fd = os.open(fn_with_NUL, os.O_WRONLY | os.O_CREAT) # podnieśs
        w_końcu:
            jeżeli fd jest nie Nic:
                os.close(fd)
        self.assertNieprawda(os.path.exists(fn))
        self.assertRaises(ValueError, os.mkdir, fn_with_NUL)
        self.assertNieprawda(os.path.exists(fn))
        open(fn, 'wb').close()
        self.assertRaises(ValueError, os.stat, fn_with_NUL)

klasa PosixGroupsTester(unittest.TestCase):

    def setUp(self):
        jeżeli posix.getuid() != 0:
            podnieś unittest.SkipTest("not enough privileges")
        jeżeli nie hasattr(posix, 'getgroups'):
            podnieś unittest.SkipTest("need posix.getgroups")
        jeżeli sys.platform == 'darwin':
            podnieś unittest.SkipTest("getgroups(2) jest broken on OSX")
        self.saved_groups = posix.getgroups()

    def tearDown(self):
        jeżeli hasattr(posix, 'setgroups'):
            posix.setgroups(self.saved_groups)
        albo_inaczej hasattr(posix, 'initgroups'):
            name = pwd.getpwuid(posix.getuid()).pw_name
            posix.initgroups(name, self.saved_groups[0])

    @unittest.skipUnless(hasattr(posix, 'initgroups'),
                         "test needs posix.initgroups()")
    def test_initgroups(self):
        # find missing group

        g = max(self.saved_groups albo [0]) + 1
        name = pwd.getpwuid(posix.getuid()).pw_name
        posix.initgroups(name, g)
        self.assertIn(g, posix.getgroups())

    @unittest.skipUnless(hasattr(posix, 'setgroups'),
                         "test needs posix.setgroups()")
    def test_setgroups(self):
        dla groups w [[0], list(range(16))]:
            posix.setgroups(groups)
            self.assertListEqual(groups, posix.getgroups())

def test_main():
    spróbuj:
        support.run_unittest(PosixTester, PosixGroupsTester)
    w_końcu:
        support.reap_children()

jeżeli __name__ == '__main__':
    test_main()
