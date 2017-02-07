# tempfile.py unit tests.
zaimportuj tempfile
zaimportuj errno
zaimportuj io
zaimportuj os
zaimportuj signal
zaimportuj sys
zaimportuj re
zaimportuj warnings
zaimportuj contextlib
zaimportuj weakref
z unittest zaimportuj mock

zaimportuj unittest
z test zaimportuj support
z test.support zaimportuj script_helper


jeżeli hasattr(os, 'stat'):
    zaimportuj stat
    has_stat = 1
inaczej:
    has_stat = 0

has_textmode = (tempfile._text_openflags != tempfile._bin_openflags)
has_spawnl = hasattr(os, 'spawnl')

# TEST_FILES may need to be tweaked dla systems depending on the maximum
# number of files that can be opened at one time (see ulimit -n)
jeżeli sys.platform.startswith('openbsd'):
    TEST_FILES = 48
inaczej:
    TEST_FILES = 100

# This jest organized jako one test dla each chunk of code w tempfile.py,
# w order of their appearance w the file.  Testing which requires
# threads jest nie done here.

klasa TestLowLevelInternals(unittest.TestCase):
    def test_infer_return_type_singles(self):
        self.assertIs(str, tempfile._infer_return_type(''))
        self.assertIs(bytes, tempfile._infer_return_type(b''))
        self.assertIs(str, tempfile._infer_return_type(Nic))

    def test_infer_return_type_multiples(self):
        self.assertIs(str, tempfile._infer_return_type('', ''))
        self.assertIs(bytes, tempfile._infer_return_type(b'', b''))
        przy self.assertRaises(TypeError):
            tempfile._infer_return_type('', b'')
        przy self.assertRaises(TypeError):
            tempfile._infer_return_type(b'', '')

    def test_infer_return_type_multiples_and_none(self):
        self.assertIs(str, tempfile._infer_return_type(Nic, ''))
        self.assertIs(str, tempfile._infer_return_type('', Nic))
        self.assertIs(str, tempfile._infer_return_type(Nic, Nic))
        self.assertIs(bytes, tempfile._infer_return_type(b'', Nic))
        self.assertIs(bytes, tempfile._infer_return_type(Nic, b''))
        przy self.assertRaises(TypeError):
            tempfile._infer_return_type('', Nic, b'')
        przy self.assertRaises(TypeError):
            tempfile._infer_return_type(b'', Nic, '')


# Common functionality.

klasa BaseTestCase(unittest.TestCase):

    str_check = re.compile(r"^[a-z0-9_-]{8}$")
    b_check = re.compile(br"^[a-z0-9_-]{8}$")

    def setUp(self):
        self._warnings_manager = support.check_warnings()
        self._warnings_manager.__enter__()
        warnings.filterwarnings("ignore", category=RuntimeWarning,
                                message="mktemp", module=__name__)

    def tearDown(self):
        self._warnings_manager.__exit__(Nic, Nic, Nic)


    def nameCheck(self, name, dir, pre, suf):
        (ndir, nbase) = os.path.split(name)
        npre  = nbase[:len(pre)]
        nsuf  = nbase[len(nbase)-len(suf):]

        jeżeli dir jest nie Nic:
            self.assertIs(type(name), str jeżeli type(dir) jest str inaczej bytes,
                          "unexpected zwróć type")
        jeżeli pre jest nie Nic:
            self.assertIs(type(name), str jeżeli type(pre) jest str inaczej bytes,
                          "unexpected zwróć type")
        jeżeli suf jest nie Nic:
            self.assertIs(type(name), str jeżeli type(suf) jest str inaczej bytes,
                          "unexpected zwróć type")
        jeżeli (dir, pre, suf) == (Nic, Nic, Nic):
            self.assertIs(type(name), str, "default zwróć type must be str")

        # check dla equality of the absolute paths!
        self.assertEqual(os.path.abspath(ndir), os.path.abspath(dir),
                         "file %r nie w directory %r" % (name, dir))
        self.assertEqual(npre, pre,
                         "file %r does nie begin przy %r" % (nbase, pre))
        self.assertEqual(nsuf, suf,
                         "file %r does nie end przy %r" % (nbase, suf))

        nbase = nbase[len(pre):len(nbase)-len(suf)]
        check = self.str_check jeżeli isinstance(nbase, str) inaczej self.b_check
        self.assertPrawda(check.match(nbase),
                        "random characters %r do nie match %r"
                        % (nbase, check.pattern))


klasa TestExports(BaseTestCase):
    def test_exports(self):
        # There are no surprising symbols w the tempfile module
        dict = tempfile.__dict__

        expected = {
            "NamedTemporaryFile" : 1,
            "TemporaryFile" : 1,
            "mkstemp" : 1,
            "mkdtemp" : 1,
            "mktemp" : 1,
            "TMP_MAX" : 1,
            "gettempprefix" : 1,
            "gettempprefixb" : 1,
            "gettempdir" : 1,
            "gettempdirb" : 1,
            "tempdir" : 1,
            "template" : 1,
            "SpooledTemporaryFile" : 1,
            "TemporaryDirectory" : 1,
        }

        unexp = []
        dla key w dict:
            jeżeli key[0] != '_' oraz key nie w expected:
                unexp.append(key)
        self.assertPrawda(len(unexp) == 0,
                        "unexpected keys: %s" % unexp)


klasa TestRandomNameSequence(BaseTestCase):
    """Test the internal iterator object _RandomNameSequence."""

    def setUp(self):
        self.r = tempfile._RandomNameSequence()
        super().setUp()

    def test_get_six_char_str(self):
        # _RandomNameSequence returns a six-character string
        s = next(self.r)
        self.nameCheck(s, '', '', '')

    def test_many(self):
        # _RandomNameSequence returns no duplicate strings (stochastic)

        dict = {}
        r = self.r
        dla i w range(TEST_FILES):
            s = next(r)
            self.nameCheck(s, '', '', '')
            self.assertNotIn(s, dict)
            dict[s] = 1

    def supports_iter(self):
        # _RandomNameSequence supports the iterator protocol

        i = 0
        r = self.r
        dla s w r:
            i += 1
            jeżeli i == 20:
                przerwij

    @unittest.skipUnless(hasattr(os, 'fork'),
        "os.fork jest required dla this test")
    def test_process_awareness(self):
        # ensure that the random source differs between
        # child oraz parent.
        read_fd, write_fd = os.pipe()
        pid = Nic
        spróbuj:
            pid = os.fork()
            jeżeli nie pid:
                os.close(read_fd)
                os.write(write_fd, next(self.r).encode("ascii"))
                os.close(write_fd)
                # bypass the normal exit handlers- leave those to
                # the parent.
                os._exit(0)
            parent_value = next(self.r)
            child_value = os.read(read_fd, len(parent_value)).decode("ascii")
        w_końcu:
            jeżeli pid:
                # best effort to ensure the process can't bleed out
                # via any bugs above
                spróbuj:
                    os.kill(pid, signal.SIGKILL)
                wyjąwszy OSError:
                    dalej
            os.close(read_fd)
            os.close(write_fd)
        self.assertNotEqual(child_value, parent_value)



klasa TestCandidateTempdirList(BaseTestCase):
    """Test the internal function _candidate_tempdir_list."""

    def test_nonempty_list(self):
        # _candidate_tempdir_list returns a nonempty list of strings

        cand = tempfile._candidate_tempdir_list()

        self.assertNieprawda(len(cand) == 0)
        dla c w cand:
            self.assertIsInstance(c, str)

    def test_wanted_dirs(self):
        # _candidate_tempdir_list contains the expected directories

        # Make sure the interesting environment variables are all set.
        przy support.EnvironmentVarGuard() jako env:
            dla envname w 'TMPDIR', 'TEMP', 'TMP':
                dirname = os.getenv(envname)
                jeżeli nie dirname:
                    env[envname] = os.path.abspath(envname)

            cand = tempfile._candidate_tempdir_list()

            dla envname w 'TMPDIR', 'TEMP', 'TMP':
                dirname = os.getenv(envname)
                jeżeli nie dirname: podnieś ValueError
                self.assertIn(dirname, cand)

            spróbuj:
                dirname = os.getcwd()
            wyjąwszy (AttributeError, OSError):
                dirname = os.curdir

            self.assertIn(dirname, cand)

            # Not practical to try to verify the presence of OS-specific
            # paths w this list.


# We test _get_default_tempdir some more by testing gettempdir.

klasa TestGetDefaultTempdir(BaseTestCase):
    """Test _get_default_tempdir()."""

    def test_no_files_left_behind(self):
        # use a private empty directory
        przy tempfile.TemporaryDirectory() jako our_temp_directory:
            # force _get_default_tempdir() to consider our empty directory
            def our_candidate_list():
                zwróć [our_temp_directory]

            przy support.swap_attr(tempfile, "_candidate_tempdir_list",
                                   our_candidate_list):
                # verify our directory jest empty after _get_default_tempdir()
                tempfile._get_default_tempdir()
                self.assertEqual(os.listdir(our_temp_directory), [])

                def podnieś_OSError(*args, **kwargs):
                    podnieś OSError()

                przy support.swap_attr(io, "open", podnieś_OSError):
                    # test again przy failing io.open()
                    przy self.assertRaises(FileNotFoundError):
                        tempfile._get_default_tempdir()
                    self.assertEqual(os.listdir(our_temp_directory), [])

                open = io.open
                def bad_writer(*args, **kwargs):
                    fp = open(*args, **kwargs)
                    fp.write = podnieś_OSError
                    zwróć fp

                przy support.swap_attr(io, "open", bad_writer):
                    # test again przy failing write()
                    przy self.assertRaises(FileNotFoundError):
                        tempfile._get_default_tempdir()
                    self.assertEqual(os.listdir(our_temp_directory), [])


klasa TestGetCandidateNames(BaseTestCase):
    """Test the internal function _get_candidate_names."""

    def test_retval(self):
        # _get_candidate_names returns a _RandomNameSequence object
        obj = tempfile._get_candidate_names()
        self.assertIsInstance(obj, tempfile._RandomNameSequence)

    def test_same_thing(self):
        # _get_candidate_names always returns the same object
        a = tempfile._get_candidate_names()
        b = tempfile._get_candidate_names()

        self.assertPrawda(a jest b)


@contextlib.contextmanager
def _inside_empty_temp_dir():
    dir = tempfile.mkdtemp()
    spróbuj:
        przy support.swap_attr(tempfile, 'tempdir', dir):
            uzyskaj
    w_końcu:
        support.rmtree(dir)


def _mock_candidate_names(*names):
    zwróć support.swap_attr(tempfile,
                             '_get_candidate_names',
                             lambda: iter(names))


klasa TestBadTempdir:

    def test_read_only_directory(self):
        przy _inside_empty_temp_dir():
            oldmode = mode = os.stat(tempfile.tempdir).st_mode
            mode &= ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
            os.chmod(tempfile.tempdir, mode)
            spróbuj:
                jeżeli os.access(tempfile.tempdir, os.W_OK):
                    self.skipTest("can't set the directory read-only")
                przy self.assertRaises(PermissionError):
                    self.make_temp()
                self.assertEqual(os.listdir(tempfile.tempdir), [])
            w_końcu:
                os.chmod(tempfile.tempdir, oldmode)

    def test_nonexisting_directory(self):
        przy _inside_empty_temp_dir():
            tempdir = os.path.join(tempfile.tempdir, 'nonexistent')
            przy support.swap_attr(tempfile, 'tempdir', tempdir):
                przy self.assertRaises(FileNotFoundError):
                    self.make_temp()

    def test_non_directory(self):
        przy _inside_empty_temp_dir():
            tempdir = os.path.join(tempfile.tempdir, 'file')
            open(tempdir, 'wb').close()
            przy support.swap_attr(tempfile, 'tempdir', tempdir):
                przy self.assertRaises((NotADirectoryError, FileNotFoundError)):
                    self.make_temp()


klasa TestMkstempInner(TestBadTempdir, BaseTestCase):
    """Test the internal function _mkstemp_inner."""

    klasa mkstemped:
        _bflags = tempfile._bin_openflags
        _tflags = tempfile._text_openflags
        _close = os.close
        _unlink = os.unlink

        def __init__(self, dir, pre, suf, bin):
            jeżeli bin: flags = self._bflags
            inaczej:   flags = self._tflags

            output_type = tempfile._infer_return_type(dir, pre, suf)
            (self.fd, self.name) = tempfile._mkstemp_inner(dir, pre, suf, flags, output_type)

        def write(self, str):
            os.write(self.fd, str)

        def __del__(self):
            self._close(self.fd)
            self._unlink(self.name)

    def do_create(self, dir=Nic, pre=Nic, suf=Nic, bin=1):
        output_type = tempfile._infer_return_type(dir, pre, suf)
        jeżeli dir jest Nic:
            jeżeli output_type jest str:
                dir = tempfile.gettempdir()
            inaczej:
                dir = tempfile.gettempdirb()
        jeżeli pre jest Nic:
            pre = output_type()
        jeżeli suf jest Nic:
            suf = output_type()
        file = self.mkstemped(dir, pre, suf, bin)

        self.nameCheck(file.name, dir, pre, suf)
        zwróć file

    def test_basic(self):
        # _mkstemp_inner can create files
        self.do_create().write(b"blat")
        self.do_create(pre="a").write(b"blat")
        self.do_create(suf="b").write(b"blat")
        self.do_create(pre="a", suf="b").write(b"blat")
        self.do_create(pre="aa", suf=".txt").write(b"blat")

    def test_basic_with_bytes_names(self):
        # _mkstemp_inner can create files when given name parts all
        # specified jako bytes.
        dir_b = tempfile.gettempdirb()
        self.do_create(dir=dir_b, suf=b"").write(b"blat")
        self.do_create(dir=dir_b, pre=b"a").write(b"blat")
        self.do_create(dir=dir_b, suf=b"b").write(b"blat")
        self.do_create(dir=dir_b, pre=b"a", suf=b"b").write(b"blat")
        self.do_create(dir=dir_b, pre=b"aa", suf=b".txt").write(b"blat")
        # Can't mix str & binary types w the args.
        przy self.assertRaises(TypeError):
            self.do_create(dir="", suf=b"").write(b"blat")
        przy self.assertRaises(TypeError):
            self.do_create(dir=dir_b, pre="").write(b"blat")
        przy self.assertRaises(TypeError):
            self.do_create(dir=dir_b, pre=b"", suf="").write(b"blat")

    def test_basic_many(self):
        # _mkstemp_inner can create many files (stochastic)
        extant = list(range(TEST_FILES))
        dla i w extant:
            extant[i] = self.do_create(pre="aa")

    def test_choose_directory(self):
        # _mkstemp_inner can create files w a user-selected directory
        dir = tempfile.mkdtemp()
        spróbuj:
            self.do_create(dir=dir).write(b"blat")
        w_końcu:
            os.rmdir(dir)

    @unittest.skipUnless(has_stat, 'os.stat nie available')
    def test_file_mode(self):
        # _mkstemp_inner creates files przy the proper mode

        file = self.do_create()
        mode = stat.S_IMODE(os.stat(file.name).st_mode)
        expected = 0o600
        jeżeli sys.platform == 'win32':
            # There's no distinction among 'user', 'group' oraz 'world';
            # replicate the 'user' bits.
            user = expected >> 6
            expected = user * (1 + 8 + 64)
        self.assertEqual(mode, expected)

    @unittest.skipUnless(has_spawnl, 'os.spawnl nie available')
    def test_noinherit(self):
        # _mkstemp_inner file handles are nie inherited by child processes

        jeżeli support.verbose:
            v="v"
        inaczej:
            v="q"

        file = self.do_create()
        self.assertEqual(os.get_inheritable(file.fd), Nieprawda)
        fd = "%d" % file.fd

        spróbuj:
            me = __file__
        wyjąwszy NameError:
            me = sys.argv[0]

        # We have to exec something, so that FD_CLOEXEC will take
        # effect.  The core of this test jest therefore w
        # tf_inherit_check.py, which see.
        tester = os.path.join(os.path.dirname(os.path.abspath(me)),
                              "tf_inherit_check.py")

        # On Windows a spawn* /path/ przy embedded spaces shouldn't be quoted,
        # but an arg przy embedded spaces should be decorated przy double
        # quotes on each end
        jeżeli sys.platform == 'win32':
            decorated = '"%s"' % sys.executable
            tester = '"%s"' % tester
        inaczej:
            decorated = sys.executable

        retval = os.spawnl(os.P_WAIT, sys.executable, decorated, tester, v, fd)
        self.assertNieprawda(retval < 0,
                    "child process caught fatal signal %d" % -retval)
        self.assertNieprawda(retval > 0, "child process reports failure %d"%retval)

    @unittest.skipUnless(has_textmode, "text mode nie available")
    def test_textmode(self):
        # _mkstemp_inner can create files w text mode

        # A text file jest truncated at the first Ctrl+Z byte
        f = self.do_create(bin=0)
        f.write(b"blat\x1a")
        f.write(b"extra\n")
        os.lseek(f.fd, 0, os.SEEK_SET)
        self.assertEqual(os.read(f.fd, 20), b"blat")

    def make_temp(self):
        zwróć tempfile._mkstemp_inner(tempfile.gettempdir(),
                                       tempfile.gettempprefix(),
                                       '',
                                       tempfile._bin_openflags,
                                       str)

    def test_collision_with_existing_file(self):
        # _mkstemp_inner tries another name when a file with
        # the chosen name already exists
        przy _inside_empty_temp_dir(), \
             _mock_candidate_names('aaa', 'aaa', 'bbb'):
            (fd1, name1) = self.make_temp()
            os.close(fd1)
            self.assertPrawda(name1.endswith('aaa'))

            (fd2, name2) = self.make_temp()
            os.close(fd2)
            self.assertPrawda(name2.endswith('bbb'))

    def test_collision_with_existing_directory(self):
        # _mkstemp_inner tries another name when a directory with
        # the chosen name already exists
        przy _inside_empty_temp_dir(), \
             _mock_candidate_names('aaa', 'aaa', 'bbb'):
            dir = tempfile.mkdtemp()
            self.assertPrawda(dir.endswith('aaa'))

            (fd, name) = self.make_temp()
            os.close(fd)
            self.assertPrawda(name.endswith('bbb'))


klasa TestGetTempPrefix(BaseTestCase):
    """Test gettempprefix()."""

    def test_sane_template(self):
        # gettempprefix returns a nonempty prefix string
        p = tempfile.gettempprefix()

        self.assertIsInstance(p, str)
        self.assertGreater(len(p), 0)

        pb = tempfile.gettempprefixb()

        self.assertIsInstance(pb, bytes)
        self.assertGreater(len(pb), 0)

    def test_usable_template(self):
        # gettempprefix returns a usable prefix string

        # Create a temp directory, avoiding use of the prefix.
        # Then attempt to create a file whose name jest
        # prefix + 'xxxxxx.xxx' w that directory.
        p = tempfile.gettempprefix() + "xxxxxx.xxx"
        d = tempfile.mkdtemp(prefix="")
        spróbuj:
            p = os.path.join(d, p)
            fd = os.open(p, os.O_RDWR | os.O_CREAT)
            os.close(fd)
            os.unlink(p)
        w_końcu:
            os.rmdir(d)


klasa TestGetTempDir(BaseTestCase):
    """Test gettempdir()."""

    def test_directory_exists(self):
        # gettempdir returns a directory which exists

        dla d w (tempfile.gettempdir(), tempfile.gettempdirb()):
            self.assertPrawda(os.path.isabs(d) albo d == os.curdir,
                            "%r jest nie an absolute path" % d)
            self.assertPrawda(os.path.isdir(d),
                            "%r jest nie a directory" % d)

    def test_directory_writable(self):
        # gettempdir returns a directory writable by the user

        # sneaky: just instantiate a NamedTemporaryFile, which
        # defaults to writing into the directory returned by
        # gettempdir.
        file = tempfile.NamedTemporaryFile()
        file.write(b"blat")
        file.close()

    def test_same_thing(self):
        # gettempdir always returns the same object
        a = tempfile.gettempdir()
        b = tempfile.gettempdir()
        c = tempfile.gettempdirb()

        self.assertPrawda(a jest b)
        self.assertNotEqual(type(a), type(c))
        self.assertEqual(a, os.fsdecode(c))

    def test_case_sensitive(self):
        # gettempdir should nie flatten its case
        # even on a case-insensitive file system
        case_sensitive_tempdir = tempfile.mkdtemp("-Temp")
        _tempdir, tempfile.tempdir = tempfile.tempdir, Nic
        spróbuj:
            przy support.EnvironmentVarGuard() jako env:
                # Fake the first env var which jest checked jako a candidate
                env["TMPDIR"] = case_sensitive_tempdir
                self.assertEqual(tempfile.gettempdir(), case_sensitive_tempdir)
        w_końcu:
            tempfile.tempdir = _tempdir
            support.rmdir(case_sensitive_tempdir)


klasa TestMkstemp(BaseTestCase):
    """Test mkstemp()."""

    def do_create(self, dir=Nic, pre=Nic, suf=Nic):
        output_type = tempfile._infer_return_type(dir, pre, suf)
        jeżeli dir jest Nic:
            jeżeli output_type jest str:
                dir = tempfile.gettempdir()
            inaczej:
                dir = tempfile.gettempdirb()
        jeżeli pre jest Nic:
            pre = output_type()
        jeżeli suf jest Nic:
            suf = output_type()
        (fd, name) = tempfile.mkstemp(dir=dir, prefix=pre, suffix=suf)
        (ndir, nbase) = os.path.split(name)
        adir = os.path.abspath(dir)
        self.assertEqual(adir, ndir,
            "Directory '%s' incorrectly returned jako '%s'" % (adir, ndir))

        spróbuj:
            self.nameCheck(name, dir, pre, suf)
        w_końcu:
            os.close(fd)
            os.unlink(name)

    def test_basic(self):
        # mkstemp can create files
        self.do_create()
        self.do_create(pre="a")
        self.do_create(suf="b")
        self.do_create(pre="a", suf="b")
        self.do_create(pre="aa", suf=".txt")
        self.do_create(dir=".")

    def test_basic_with_bytes_names(self):
        # mkstemp can create files when given name parts all
        # specified jako bytes.
        d = tempfile.gettempdirb()
        self.do_create(dir=d, suf=b"")
        self.do_create(dir=d, pre=b"a")
        self.do_create(dir=d, suf=b"b")
        self.do_create(dir=d, pre=b"a", suf=b"b")
        self.do_create(dir=d, pre=b"aa", suf=b".txt")
        self.do_create(dir=b".")
        przy self.assertRaises(TypeError):
            self.do_create(dir=".", pre=b"aa", suf=b".txt")
        przy self.assertRaises(TypeError):
            self.do_create(dir=b".", pre="aa", suf=b".txt")
        przy self.assertRaises(TypeError):
            self.do_create(dir=b".", pre=b"aa", suf=".txt")


    def test_choose_directory(self):
        # mkstemp can create directories w a user-selected directory
        dir = tempfile.mkdtemp()
        spróbuj:
            self.do_create(dir=dir)
        w_końcu:
            os.rmdir(dir)


klasa TestMkdtemp(TestBadTempdir, BaseTestCase):
    """Test mkdtemp()."""

    def make_temp(self):
        zwróć tempfile.mkdtemp()

    def do_create(self, dir=Nic, pre=Nic, suf=Nic):
        output_type = tempfile._infer_return_type(dir, pre, suf)
        jeżeli dir jest Nic:
            jeżeli output_type jest str:
                dir = tempfile.gettempdir()
            inaczej:
                dir = tempfile.gettempdirb()
        jeżeli pre jest Nic:
            pre = output_type()
        jeżeli suf jest Nic:
            suf = output_type()
        name = tempfile.mkdtemp(dir=dir, prefix=pre, suffix=suf)

        spróbuj:
            self.nameCheck(name, dir, pre, suf)
            zwróć name
        wyjąwszy:
            os.rmdir(name)
            podnieś

    def test_basic(self):
        # mkdtemp can create directories
        os.rmdir(self.do_create())
        os.rmdir(self.do_create(pre="a"))
        os.rmdir(self.do_create(suf="b"))
        os.rmdir(self.do_create(pre="a", suf="b"))
        os.rmdir(self.do_create(pre="aa", suf=".txt"))

    def test_basic_with_bytes_names(self):
        # mkdtemp can create directories when given all binary parts
        d = tempfile.gettempdirb()
        os.rmdir(self.do_create(dir=d))
        os.rmdir(self.do_create(dir=d, pre=b"a"))
        os.rmdir(self.do_create(dir=d, suf=b"b"))
        os.rmdir(self.do_create(dir=d, pre=b"a", suf=b"b"))
        os.rmdir(self.do_create(dir=d, pre=b"aa", suf=b".txt"))
        przy self.assertRaises(TypeError):
            os.rmdir(self.do_create(dir=d, pre="aa", suf=b".txt"))
        przy self.assertRaises(TypeError):
            os.rmdir(self.do_create(dir=d, pre=b"aa", suf=".txt"))
        przy self.assertRaises(TypeError):
            os.rmdir(self.do_create(dir="", pre=b"aa", suf=b".txt"))

    def test_basic_many(self):
        # mkdtemp can create many directories (stochastic)
        extant = list(range(TEST_FILES))
        spróbuj:
            dla i w extant:
                extant[i] = self.do_create(pre="aa")
        w_końcu:
            dla i w extant:
                if(isinstance(i, str)):
                    os.rmdir(i)

    def test_choose_directory(self):
        # mkdtemp can create directories w a user-selected directory
        dir = tempfile.mkdtemp()
        spróbuj:
            os.rmdir(self.do_create(dir=dir))
        w_końcu:
            os.rmdir(dir)

    @unittest.skipUnless(has_stat, 'os.stat nie available')
    def test_mode(self):
        # mkdtemp creates directories przy the proper mode

        dir = self.do_create()
        spróbuj:
            mode = stat.S_IMODE(os.stat(dir).st_mode)
            mode &= 0o777 # Mask off sticky bits inherited z /tmp
            expected = 0o700
            jeżeli sys.platform == 'win32':
                # There's no distinction among 'user', 'group' oraz 'world';
                # replicate the 'user' bits.
                user = expected >> 6
                expected = user * (1 + 8 + 64)
            self.assertEqual(mode, expected)
        w_końcu:
            os.rmdir(dir)

    def test_collision_with_existing_file(self):
        # mkdtemp tries another name when a file with
        # the chosen name already exists
        przy _inside_empty_temp_dir(), \
             _mock_candidate_names('aaa', 'aaa', 'bbb'):
            file = tempfile.NamedTemporaryFile(delete=Nieprawda)
            file.close()
            self.assertPrawda(file.name.endswith('aaa'))
            dir = tempfile.mkdtemp()
            self.assertPrawda(dir.endswith('bbb'))

    def test_collision_with_existing_directory(self):
        # mkdtemp tries another name when a directory with
        # the chosen name already exists
        przy _inside_empty_temp_dir(), \
             _mock_candidate_names('aaa', 'aaa', 'bbb'):
            dir1 = tempfile.mkdtemp()
            self.assertPrawda(dir1.endswith('aaa'))
            dir2 = tempfile.mkdtemp()
            self.assertPrawda(dir2.endswith('bbb'))


klasa TestMktemp(BaseTestCase):
    """Test mktemp()."""

    # For safety, all use of mktemp must occur w a private directory.
    # We must also suppress the RuntimeWarning it generates.
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        super().setUp()

    def tearDown(self):
        jeżeli self.dir:
            os.rmdir(self.dir)
            self.dir = Nic
        super().tearDown()

    klasa mktemped:
        _unlink = os.unlink
        _bflags = tempfile._bin_openflags

        def __init__(self, dir, pre, suf):
            self.name = tempfile.mktemp(dir=dir, prefix=pre, suffix=suf)
            # Create the file.  This will podnieś an exception jeżeli it's
            # mysteriously appeared w the meanwhile.
            os.close(os.open(self.name, self._bflags, 0o600))

        def __del__(self):
            self._unlink(self.name)

    def do_create(self, pre="", suf=""):
        file = self.mktemped(self.dir, pre, suf)

        self.nameCheck(file.name, self.dir, pre, suf)
        zwróć file

    def test_basic(self):
        # mktemp can choose usable file names
        self.do_create()
        self.do_create(pre="a")
        self.do_create(suf="b")
        self.do_create(pre="a", suf="b")
        self.do_create(pre="aa", suf=".txt")

    def test_many(self):
        # mktemp can choose many usable file names (stochastic)
        extant = list(range(TEST_FILES))
        dla i w extant:
            extant[i] = self.do_create(pre="aa")

##     def test_warning(self):
##         # mktemp issues a warning when used
##         warnings.filterwarnings("error",
##                                 category=RuntimeWarning,
##                                 message="mktemp")
##         self.assertRaises(RuntimeWarning,
##                           tempfile.mktemp, dir=self.dir)


# We test _TemporaryFileWrapper by testing NamedTemporaryFile.


klasa TestNamedTemporaryFile(BaseTestCase):
    """Test NamedTemporaryFile()."""

    def do_create(self, dir=Nic, pre="", suf="", delete=Prawda):
        jeżeli dir jest Nic:
            dir = tempfile.gettempdir()
        file = tempfile.NamedTemporaryFile(dir=dir, prefix=pre, suffix=suf,
                                           delete=delete)

        self.nameCheck(file.name, dir, pre, suf)
        zwróć file


    def test_basic(self):
        # NamedTemporaryFile can create files
        self.do_create()
        self.do_create(pre="a")
        self.do_create(suf="b")
        self.do_create(pre="a", suf="b")
        self.do_create(pre="aa", suf=".txt")

    def test_method_lookup(self):
        # Issue #18879: Looking up a temporary file method should keep it
        # alive long enough.
        f = self.do_create()
        wr = weakref.ref(f)
        write = f.write
        write2 = f.write
        usuń f
        write(b'foo')
        usuń write
        write2(b'bar')
        usuń write2
        jeżeli support.check_impl_detail(cpython=Prawda):
            # No reference cycle was created.
            self.assertIsNic(wr())

    def test_iter(self):
        # Issue #23700: getting iterator z a temporary file should keep
        # it alive jako long jako it's being iterated over
        lines = [b'spam\n', b'eggs\n', b'beans\n']
        def make_file():
            f = tempfile.NamedTemporaryFile(mode='w+b')
            f.write(b''.join(lines))
            f.seek(0)
            zwróć f
        dla i, l w enumerate(make_file()):
            self.assertEqual(l, lines[i])
        self.assertEqual(i, len(lines) - 1)

    def test_creates_named(self):
        # NamedTemporaryFile creates files przy names
        f = tempfile.NamedTemporaryFile()
        self.assertPrawda(os.path.exists(f.name),
                        "NamedTemporaryFile %s does nie exist" % f.name)

    def test_del_on_close(self):
        # A NamedTemporaryFile jest deleted when closed
        dir = tempfile.mkdtemp()
        spróbuj:
            f = tempfile.NamedTemporaryFile(dir=dir)
            f.write(b'blat')
            f.close()
            self.assertNieprawda(os.path.exists(f.name),
                        "NamedTemporaryFile %s exists after close" % f.name)
        w_końcu:
            os.rmdir(dir)

    def test_dis_del_on_close(self):
        # Tests that delete-on-close can be disabled
        dir = tempfile.mkdtemp()
        tmp = Nic
        spróbuj:
            f = tempfile.NamedTemporaryFile(dir=dir, delete=Nieprawda)
            tmp = f.name
            f.write(b'blat')
            f.close()
            self.assertPrawda(os.path.exists(f.name),
                        "NamedTemporaryFile %s missing after close" % f.name)
        w_końcu:
            jeżeli tmp jest nie Nic:
                os.unlink(tmp)
            os.rmdir(dir)

    def test_multiple_close(self):
        # A NamedTemporaryFile can be closed many times without error
        f = tempfile.NamedTemporaryFile()
        f.write(b'abc\n')
        f.close()
        f.close()
        f.close()

    def test_context_manager(self):
        # A NamedTemporaryFile can be used jako a context manager
        przy tempfile.NamedTemporaryFile() jako f:
            self.assertPrawda(os.path.exists(f.name))
        self.assertNieprawda(os.path.exists(f.name))
        def use_closed():
            przy f:
                dalej
        self.assertRaises(ValueError, use_closed)

    def test_no_leak_fd(self):
        # Issue #21058: don't leak file descriptor when io.open() fails
        closed = []
        os_close = os.close
        def close(fd):
            closed.append(fd)
            os_close(fd)

        przy mock.patch('os.close', side_effect=close):
            przy mock.patch('io.open', side_effect=ValueError):
                self.assertRaises(ValueError, tempfile.NamedTemporaryFile)
                self.assertEqual(len(closed), 1)

    # How to test the mode oraz bufsize parameters?


klasa TestSpooledTemporaryFile(BaseTestCase):
    """Test SpooledTemporaryFile()."""

    def do_create(self, max_size=0, dir=Nic, pre="", suf=""):
        jeżeli dir jest Nic:
            dir = tempfile.gettempdir()
        file = tempfile.SpooledTemporaryFile(max_size=max_size, dir=dir, prefix=pre, suffix=suf)

        zwróć file


    def test_basic(self):
        # SpooledTemporaryFile can create files
        f = self.do_create()
        self.assertNieprawda(f._rolled)
        f = self.do_create(max_size=100, pre="a", suf=".txt")
        self.assertNieprawda(f._rolled)

    def test_del_on_close(self):
        # A SpooledTemporaryFile jest deleted when closed
        dir = tempfile.mkdtemp()
        spróbuj:
            f = tempfile.SpooledTemporaryFile(max_size=10, dir=dir)
            self.assertNieprawda(f._rolled)
            f.write(b'blat ' * 5)
            self.assertPrawda(f._rolled)
            filename = f.name
            f.close()
            self.assertNieprawda(isinstance(filename, str) oraz os.path.exists(filename),
                        "SpooledTemporaryFile %s exists after close" % filename)
        w_końcu:
            os.rmdir(dir)

    def test_rewrite_small(self):
        # A SpooledTemporaryFile can be written to multiple within the max_size
        f = self.do_create(max_size=30)
        self.assertNieprawda(f._rolled)
        dla i w range(5):
            f.seek(0, 0)
            f.write(b'x' * 20)
        self.assertNieprawda(f._rolled)

    def test_write_sequential(self):
        # A SpooledTemporaryFile should hold exactly max_size bytes, oraz roll
        # over afterward
        f = self.do_create(max_size=30)
        self.assertNieprawda(f._rolled)
        f.write(b'x' * 20)
        self.assertNieprawda(f._rolled)
        f.write(b'x' * 10)
        self.assertNieprawda(f._rolled)
        f.write(b'x')
        self.assertPrawda(f._rolled)

    def test_writelines(self):
        # Verify writelines przy a SpooledTemporaryFile
        f = self.do_create()
        f.writelines((b'x', b'y', b'z'))
        f.seek(0)
        buf = f.read()
        self.assertEqual(buf, b'xyz')

    def test_writelines_sequential(self):
        # A SpooledTemporaryFile should hold exactly max_size bytes, oraz roll
        # over afterward
        f = self.do_create(max_size=35)
        f.writelines((b'x' * 20, b'x' * 10, b'x' * 5))
        self.assertNieprawda(f._rolled)
        f.write(b'x')
        self.assertPrawda(f._rolled)

    def test_sparse(self):
        # A SpooledTemporaryFile that jest written late w the file will extend
        # when that occurs
        f = self.do_create(max_size=30)
        self.assertNieprawda(f._rolled)
        f.seek(100, 0)
        self.assertNieprawda(f._rolled)
        f.write(b'x')
        self.assertPrawda(f._rolled)

    def test_fileno(self):
        # A SpooledTemporaryFile should roll over to a real file on fileno()
        f = self.do_create(max_size=30)
        self.assertNieprawda(f._rolled)
        self.assertPrawda(f.fileno() > 0)
        self.assertPrawda(f._rolled)

    def test_multiple_close_before_rollover(self):
        # A SpooledTemporaryFile can be closed many times without error
        f = tempfile.SpooledTemporaryFile()
        f.write(b'abc\n')
        self.assertNieprawda(f._rolled)
        f.close()
        f.close()
        f.close()

    def test_multiple_close_after_rollover(self):
        # A SpooledTemporaryFile can be closed many times without error
        f = tempfile.SpooledTemporaryFile(max_size=1)
        f.write(b'abc\n')
        self.assertPrawda(f._rolled)
        f.close()
        f.close()
        f.close()

    def test_bound_methods(self):
        # It should be OK to steal a bound method z a SpooledTemporaryFile
        # oraz use it independently; when the file rolls over, those bound
        # methods should continue to function
        f = self.do_create(max_size=30)
        read = f.read
        write = f.write
        seek = f.seek

        write(b"a" * 35)
        write(b"b" * 35)
        seek(0, 0)
        self.assertEqual(read(70), b'a'*35 + b'b'*35)

    def test_properties(self):
        f = tempfile.SpooledTemporaryFile(max_size=10)
        f.write(b'x' * 10)
        self.assertNieprawda(f._rolled)
        self.assertEqual(f.mode, 'w+b')
        self.assertIsNic(f.name)
        przy self.assertRaises(AttributeError):
            f.newlines
        przy self.assertRaises(AttributeError):
            f.encoding

        f.write(b'x')
        self.assertPrawda(f._rolled)
        self.assertEqual(f.mode, 'rb+')
        self.assertIsNotNic(f.name)
        przy self.assertRaises(AttributeError):
            f.newlines
        przy self.assertRaises(AttributeError):
            f.encoding

    def test_text_mode(self):
        # Creating a SpooledTemporaryFile przy a text mode should produce
        # a file object reading oraz writing (Unicode) text strings.
        f = tempfile.SpooledTemporaryFile(mode='w+', max_size=10)
        f.write("abc\n")
        f.seek(0)
        self.assertEqual(f.read(), "abc\n")
        f.write("def\n")
        f.seek(0)
        self.assertEqual(f.read(), "abc\ndef\n")
        self.assertNieprawda(f._rolled)
        self.assertEqual(f.mode, 'w+')
        self.assertIsNic(f.name)
        self.assertIsNic(f.newlines)
        self.assertIsNic(f.encoding)

        f.write("xyzzy\n")
        f.seek(0)
        self.assertEqual(f.read(), "abc\ndef\nxyzzy\n")
        # Check that Ctrl+Z doesn't truncate the file
        f.write("foo\x1abar\n")
        f.seek(0)
        self.assertEqual(f.read(), "abc\ndef\nxyzzy\nfoo\x1abar\n")
        self.assertPrawda(f._rolled)
        self.assertEqual(f.mode, 'w+')
        self.assertIsNotNic(f.name)
        self.assertEqual(f.newlines, os.linesep)
        self.assertIsNotNic(f.encoding)

    def test_text_newline_and_encoding(self):
        f = tempfile.SpooledTemporaryFile(mode='w+', max_size=10,
                                          newline='', encoding='utf-8')
        f.write("\u039B\r\n")
        f.seek(0)
        self.assertEqual(f.read(), "\u039B\r\n")
        self.assertNieprawda(f._rolled)
        self.assertEqual(f.mode, 'w+')
        self.assertIsNic(f.name)
        self.assertIsNic(f.newlines)
        self.assertIsNic(f.encoding)

        f.write("\u039B" * 20 + "\r\n")
        f.seek(0)
        self.assertEqual(f.read(), "\u039B\r\n" + ("\u039B" * 20) + "\r\n")
        self.assertPrawda(f._rolled)
        self.assertEqual(f.mode, 'w+')
        self.assertIsNotNic(f.name)
        self.assertIsNotNic(f.newlines)
        self.assertEqual(f.encoding, 'utf-8')

    def test_context_manager_before_rollover(self):
        # A SpooledTemporaryFile can be used jako a context manager
        przy tempfile.SpooledTemporaryFile(max_size=1) jako f:
            self.assertNieprawda(f._rolled)
            self.assertNieprawda(f.closed)
        self.assertPrawda(f.closed)
        def use_closed():
            przy f:
                dalej
        self.assertRaises(ValueError, use_closed)

    def test_context_manager_during_rollover(self):
        # A SpooledTemporaryFile can be used jako a context manager
        przy tempfile.SpooledTemporaryFile(max_size=1) jako f:
            self.assertNieprawda(f._rolled)
            f.write(b'abc\n')
            f.flush()
            self.assertPrawda(f._rolled)
            self.assertNieprawda(f.closed)
        self.assertPrawda(f.closed)
        def use_closed():
            przy f:
                dalej
        self.assertRaises(ValueError, use_closed)

    def test_context_manager_after_rollover(self):
        # A SpooledTemporaryFile can be used jako a context manager
        f = tempfile.SpooledTemporaryFile(max_size=1)
        f.write(b'abc\n')
        f.flush()
        self.assertPrawda(f._rolled)
        przy f:
            self.assertNieprawda(f.closed)
        self.assertPrawda(f.closed)
        def use_closed():
            przy f:
                dalej
        self.assertRaises(ValueError, use_closed)

    def test_truncate_with_size_parameter(self):
        # A SpooledTemporaryFile can be truncated to zero size
        f = tempfile.SpooledTemporaryFile(max_size=10)
        f.write(b'abcdefg\n')
        f.seek(0)
        f.truncate()
        self.assertNieprawda(f._rolled)
        self.assertEqual(f._file.getvalue(), b'')
        # A SpooledTemporaryFile can be truncated to a specific size
        f = tempfile.SpooledTemporaryFile(max_size=10)
        f.write(b'abcdefg\n')
        f.truncate(4)
        self.assertNieprawda(f._rolled)
        self.assertEqual(f._file.getvalue(), b'abcd')
        # A SpooledTemporaryFile rolls over jeżeli truncated to large size
        f = tempfile.SpooledTemporaryFile(max_size=10)
        f.write(b'abcdefg\n')
        f.truncate(20)
        self.assertPrawda(f._rolled)
        jeżeli has_stat:
            self.assertEqual(os.fstat(f.fileno()).st_size, 20)


jeżeli tempfile.NamedTemporaryFile jest nie tempfile.TemporaryFile:

    klasa TestTemporaryFile(BaseTestCase):
        """Test TemporaryFile()."""

        def test_basic(self):
            # TemporaryFile can create files
            # No point w testing the name params - the file has no name.
            tempfile.TemporaryFile()

        def test_has_no_name(self):
            # TemporaryFile creates files przy no names (on this system)
            dir = tempfile.mkdtemp()
            f = tempfile.TemporaryFile(dir=dir)
            f.write(b'blat')

            # Sneaky: because this file has no name, it should nie prevent
            # us z removing the directory it was created in.
            spróbuj:
                os.rmdir(dir)
            wyjąwszy:
                # cleanup
                f.close()
                os.rmdir(dir)
                podnieś

        def test_multiple_close(self):
            # A TemporaryFile can be closed many times without error
            f = tempfile.TemporaryFile()
            f.write(b'abc\n')
            f.close()
            f.close()
            f.close()

        # How to test the mode oraz bufsize parameters?
        def test_mode_and_encoding(self):

            def roundtrip(input, *args, **kwargs):
                przy tempfile.TemporaryFile(*args, **kwargs) jako fileobj:
                    fileobj.write(input)
                    fileobj.seek(0)
                    self.assertEqual(input, fileobj.read())

            roundtrip(b"1234", "w+b")
            roundtrip("abdc\n", "w+")
            roundtrip("\u039B", "w+", encoding="utf-16")
            roundtrip("foo\r\n", "w+", newline="")

        def test_no_leak_fd(self):
            # Issue #21058: don't leak file descriptor when io.open() fails
            closed = []
            os_close = os.close
            def close(fd):
                closed.append(fd)
                os_close(fd)

            przy mock.patch('os.close', side_effect=close):
                przy mock.patch('io.open', side_effect=ValueError):
                    self.assertRaises(ValueError, tempfile.TemporaryFile)
                    self.assertEqual(len(closed), 1)



# Helper dla test_del_on_shutdown
klasa NulledModules:
    def __init__(self, *modules):
        self.refs = [mod.__dict__ dla mod w modules]
        self.contents = [ref.copy() dla ref w self.refs]

    def __enter__(self):
        dla d w self.refs:
            dla key w d:
                d[key] = Nic

    def __exit__(self, *exc_info):
        dla d, c w zip(self.refs, self.contents):
            d.clear()
            d.update(c)

klasa TestTemporaryDirectory(BaseTestCase):
    """Test TemporaryDirectory()."""

    def do_create(self, dir=Nic, pre="", suf="", recurse=1):
        jeżeli dir jest Nic:
            dir = tempfile.gettempdir()
        tmp = tempfile.TemporaryDirectory(dir=dir, prefix=pre, suffix=suf)
        self.nameCheck(tmp.name, dir, pre, suf)
        # Create a subdirectory oraz some files
        jeżeli recurse:
            d1 = self.do_create(tmp.name, pre, suf, recurse-1)
            d1.name = Nic
        przy open(os.path.join(tmp.name, "test.txt"), "wb") jako f:
            f.write(b"Hello world!")
        zwróć tmp

    def test_mkdtemp_failure(self):
        # Check no additional exception jeżeli mkdtemp fails
        # Previously would podnieś AttributeError instead
        # (nieed jako part of Issue #10188)
        przy tempfile.TemporaryDirectory() jako nonexistent:
            dalej
        przy self.assertRaises(FileNotFoundError) jako cm:
            tempfile.TemporaryDirectory(dir=nonexistent)
        self.assertEqual(cm.exception.errno, errno.ENOENT)

    def test_explicit_cleanup(self):
        # A TemporaryDirectory jest deleted when cleaned up
        dir = tempfile.mkdtemp()
        spróbuj:
            d = self.do_create(dir=dir)
            self.assertPrawda(os.path.exists(d.name),
                            "TemporaryDirectory %s does nie exist" % d.name)
            d.cleanup()
            self.assertNieprawda(os.path.exists(d.name),
                        "TemporaryDirectory %s exists after cleanup" % d.name)
        w_końcu:
            os.rmdir(dir)

    @support.skip_unless_symlink
    def test_cleanup_with_symlink_to_a_directory(self):
        # cleanup() should nie follow symlinks to directories (issue #12464)
        d1 = self.do_create()
        d2 = self.do_create(recurse=0)

        # Symlink d1/foo -> d2
        os.symlink(d2.name, os.path.join(d1.name, "foo"))

        # This call to cleanup() should nie follow the "foo" symlink
        d1.cleanup()

        self.assertNieprawda(os.path.exists(d1.name),
                         "TemporaryDirectory %s exists after cleanup" % d1.name)
        self.assertPrawda(os.path.exists(d2.name),
                        "Directory pointed to by a symlink was deleted")
        self.assertEqual(os.listdir(d2.name), ['test.txt'],
                         "Contents of the directory pointed to by a symlink "
                         "were deleted")
        d2.cleanup()

    @support.cpython_only
    def test_del_on_collection(self):
        # A TemporaryDirectory jest deleted when garbage collected
        dir = tempfile.mkdtemp()
        spróbuj:
            d = self.do_create(dir=dir)
            name = d.name
            usuń d # Rely on refcounting to invoke __del__
            self.assertNieprawda(os.path.exists(name),
                        "TemporaryDirectory %s exists after __del__" % name)
        w_końcu:
            os.rmdir(dir)

    def test_del_on_shutdown(self):
        # A TemporaryDirectory may be cleaned up during shutdown
        przy self.do_create() jako dir:
            dla mod w ('builtins', 'os', 'shutil', 'sys', 'tempfile', 'warnings'):
                code = """jeżeli Prawda:
                    zaimportuj builtins
                    zaimportuj os
                    zaimportuj shutil
                    zaimportuj sys
                    zaimportuj tempfile
                    zaimportuj warnings

                    tmp = tempfile.TemporaryDirectory(dir={dir!r})
                    sys.stdout.buffer.write(tmp.name.encode())

                    tmp2 = os.path.join(tmp.name, 'test_dir')
                    os.mkdir(tmp2)
                    przy open(os.path.join(tmp2, "test.txt"), "w") jako f:
                        f.write("Hello world!")

                    {mod}.tmp = tmp

                    warnings.filterwarnings("always", category=ResourceWarning)
                    """.format(dir=dir, mod=mod)
                rc, out, err = script_helper.assert_python_ok("-c", code)
                tmp_name = out.decode().strip()
                self.assertNieprawda(os.path.exists(tmp_name),
                            "TemporaryDirectory %s exists after cleanup" % tmp_name)
                err = err.decode('utf-8', 'backslashreplace')
                self.assertNotIn("Exception ", err)
                self.assertIn("ResourceWarning: Implicitly cleaning up", err)

    def test_exit_on_shutdown(self):
        # Issue #22427
        przy self.do_create() jako dir:
            code = """jeżeli Prawda:
                zaimportuj sys
                zaimportuj tempfile
                zaimportuj warnings

                def generator():
                    przy tempfile.TemporaryDirectory(dir={dir!r}) jako tmp:
                        uzyskaj tmp
                g = generator()
                sys.stdout.buffer.write(next(g).encode())

                warnings.filterwarnings("always", category=ResourceWarning)
                """.format(dir=dir)
            rc, out, err = script_helper.assert_python_ok("-c", code)
            tmp_name = out.decode().strip()
            self.assertNieprawda(os.path.exists(tmp_name),
                        "TemporaryDirectory %s exists after cleanup" % tmp_name)
            err = err.decode('utf-8', 'backslashreplace')
            self.assertNotIn("Exception ", err)
            self.assertIn("ResourceWarning: Implicitly cleaning up", err)

    def test_warnings_on_cleanup(self):
        # ResourceWarning will be triggered by __del__
        przy self.do_create() jako dir:
            d = self.do_create(dir=dir, recurse=3)
            name = d.name

            # Check dla the resource warning
            przy support.check_warnings(('Implicitly', ResourceWarning), quiet=Nieprawda):
                warnings.filterwarnings("always", category=ResourceWarning)
                usuń d
                support.gc_collect()
            self.assertNieprawda(os.path.exists(name),
                        "TemporaryDirectory %s exists after __del__" % name)

    def test_multiple_close(self):
        # Can be cleaned-up many times without error
        d = self.do_create()
        d.cleanup()
        d.cleanup()
        d.cleanup()

    def test_context_manager(self):
        # Can be used jako a context manager
        d = self.do_create()
        przy d jako name:
            self.assertPrawda(os.path.exists(name))
            self.assertEqual(name, d.name)
        self.assertNieprawda(os.path.exists(name))


jeżeli __name__ == "__main__":
    unittest.main()
