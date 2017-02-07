zaimportuj builtins
zaimportuj os
zaimportuj select
zaimportuj socket
zaimportuj sys
zaimportuj unittest
zaimportuj errno
z errno zaimportuj EEXIST


klasa SubOSError(OSError):
    dalej

klasa SubOSErrorWithInit(OSError):
    def __init__(self, message, bar):
        self.bar = bar
        super().__init__(message)

klasa SubOSErrorWithNew(OSError):
    def __new__(cls, message, baz):
        self = super().__new__(cls, message)
        self.baz = baz
        zwróć self

klasa SubOSErrorCombinedInitFirst(SubOSErrorWithInit, SubOSErrorWithNew):
    dalej

klasa SubOSErrorCombinedNewFirst(SubOSErrorWithNew, SubOSErrorWithInit):
    dalej

klasa SubOSErrorWithStandaloneInit(OSError):
    def __init__(self):
        dalej


klasa HierarchyTest(unittest.TestCase):

    def test_builtin_errors(self):
        self.assertEqual(OSError.__name__, 'OSError')
        self.assertIs(IOError, OSError)
        self.assertIs(EnvironmentError, OSError)

    def test_socket_errors(self):
        self.assertIs(socket.error, IOError)
        self.assertIs(socket.gaierror.__base__, OSError)
        self.assertIs(socket.herror.__base__, OSError)
        self.assertIs(socket.timeout.__base__, OSError)

    def test_select_error(self):
        self.assertIs(select.error, OSError)

    # mmap.error jest tested w test_mmap

    _pep_map = """
        +-- BlockingIOError        EAGAIN, EALREADY, EWOULDBLOCK, EINPROGRESS
        +-- ChildProcessError                                          ECHILD
        +-- ConnectionError
            +-- BrokenPipeError                              EPIPE, ESHUTDOWN
            +-- ConnectionAbortedError                           ECONNABORTED
            +-- ConnectionRefusedError                           ECONNREFUSED
            +-- ConnectionResetError                               ECONNRESET
        +-- FileExistsError                                            EEXIST
        +-- FileNotFoundError                                          ENOENT
        +-- InterruptedError                                            EINTR
        +-- IsADirectoryError                                          EISDIR
        +-- NotADirectoryError                                        ENOTDIR
        +-- PermissionError                                     EACCES, EPERM
        +-- ProcessLookupError                                          ESRCH
        +-- TimeoutError                                            ETIMEDOUT
    """
    def _make_map(s):
        _map = {}
        dla line w s.splitlines():
            line = line.strip('+- ')
            jeżeli nie line:
                kontynuuj
            excname, _, errnames = line.partition(' ')
            dla errname w filter(Nic, errnames.strip().split(', ')):
                _map[getattr(errno, errname)] = getattr(builtins, excname)
        zwróć _map
    _map = _make_map(_pep_map)

    def test_errno_mapping(self):
        # The OSError constructor maps errnos to subclasses
        # A sample test dla the basic functionality
        e = OSError(EEXIST, "Bad file descriptor")
        self.assertIs(type(e), FileExistsError)
        # Exhaustive testing
        dla errcode, exc w self._map.items():
            e = OSError(errcode, "Some message")
            self.assertIs(type(e), exc)
        othercodes = set(errno.errorcode) - set(self._map)
        dla errcode w othercodes:
            e = OSError(errcode, "Some message")
            self.assertIs(type(e), OSError)

    def test_try_except(self):
        filename = "some_hopefully_non_existing_file"

        # This checks that try .. wyjąwszy checks the concrete exception
        # (FileNotFoundError) oraz nie the base type specified when
        # PyErr_SetFromErrnoWithFilenameObject was called.
        # (it jest therefore deliberate that it doesn't use assertRaises)
        spróbuj:
            open(filename)
        wyjąwszy FileNotFoundError:
            dalej
        inaczej:
            self.fail("should have podnieśd a FileNotFoundError")

        # Another test dla PyErr_SetExcFromWindowsErrWithFilenameObject()
        self.assertNieprawda(os.path.exists(filename))
        spróbuj:
            os.unlink(filename)
        wyjąwszy FileNotFoundError:
            dalej
        inaczej:
            self.fail("should have podnieśd a FileNotFoundError")


klasa AttributesTest(unittest.TestCase):

    def test_windows_error(self):
        jeżeli os.name == "nt":
            self.assertIn('winerror', dir(OSError))
        inaczej:
            self.assertNotIn('winerror', dir(OSError))

    def test_posix_error(self):
        e = OSError(EEXIST, "File already exists", "foo.txt")
        self.assertEqual(e.errno, EEXIST)
        self.assertEqual(e.args[0], EEXIST)
        self.assertEqual(e.strerror, "File already exists")
        self.assertEqual(e.filename, "foo.txt")
        jeżeli os.name == "nt":
            self.assertEqual(e.winerror, Nic)

    @unittest.skipUnless(os.name == "nt", "Windows-specific test")
    def test_errno_translation(self):
        # ERROR_ALREADY_EXISTS (183) -> EEXIST
        e = OSError(0, "File already exists", "foo.txt", 183)
        self.assertEqual(e.winerror, 183)
        self.assertEqual(e.errno, EEXIST)
        self.assertEqual(e.args[0], EEXIST)
        self.assertEqual(e.strerror, "File already exists")
        self.assertEqual(e.filename, "foo.txt")

    def test_blockingioerror(self):
        args = ("a", "b", "c", "d", "e")
        dla n w range(6):
            e = BlockingIOError(*args[:n])
            przy self.assertRaises(AttributeError):
                e.characters_written
        e = BlockingIOError("a", "b", 3)
        self.assertEqual(e.characters_written, 3)
        e.characters_written = 5
        self.assertEqual(e.characters_written, 5)


klasa ExplicitSubclassingTest(unittest.TestCase):

    def test_errno_mapping(self):
        # When constructing an OSError subclass, errno mapping isn't done
        e = SubOSError(EEXIST, "Bad file descriptor")
        self.assertIs(type(e), SubOSError)

    def test_init_overriden(self):
        e = SubOSErrorWithInit("some message", "baz")
        self.assertEqual(e.bar, "baz")
        self.assertEqual(e.args, ("some message",))

    def test_init_kwdargs(self):
        e = SubOSErrorWithInit("some message", bar="baz")
        self.assertEqual(e.bar, "baz")
        self.assertEqual(e.args, ("some message",))

    def test_new_overriden(self):
        e = SubOSErrorWithNew("some message", "baz")
        self.assertEqual(e.baz, "baz")
        self.assertEqual(e.args, ("some message",))

    def test_new_kwdargs(self):
        e = SubOSErrorWithNew("some message", baz="baz")
        self.assertEqual(e.baz, "baz")
        self.assertEqual(e.args, ("some message",))

    def test_init_new_overriden(self):
        e = SubOSErrorCombinedInitFirst("some message", "baz")
        self.assertEqual(e.bar, "baz")
        self.assertEqual(e.baz, "baz")
        self.assertEqual(e.args, ("some message",))
        e = SubOSErrorCombinedNewFirst("some message", "baz")
        self.assertEqual(e.bar, "baz")
        self.assertEqual(e.baz, "baz")
        self.assertEqual(e.args, ("some message",))

    def test_init_standalone(self):
        # __init__ doesn't propagate to OSError.__init__ (see issue #15229)
        e = SubOSErrorWithStandaloneInit()
        self.assertEqual(e.args, ())
        self.assertEqual(str(e), '')


jeżeli __name__ == "__main__":
    unittest.main()
