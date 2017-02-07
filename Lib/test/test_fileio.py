# Adapted z test_file.py by Daniel Stutzbach

zaimportuj sys
zaimportuj os
zaimportuj io
zaimportuj errno
zaimportuj unittest
z array zaimportuj array
z weakref zaimportuj proxy
z functools zaimportuj wraps

z test.support zaimportuj TESTFN, check_warnings, run_unittest, make_bad_fd, cpython_only
z collections zaimportuj UserList

zaimportuj _io  # C implementation of io
zaimportuj _pyio # Python implementation of io


klasa AutoFileTests:
    # file tests dla which a test file jest automatically set up

    def setUp(self):
        self.f = self.FileIO(TESTFN, 'w')

    def tearDown(self):
        jeżeli self.f:
            self.f.close()
        os.remove(TESTFN)

    def testWeakRefs(self):
        # verify weak references
        p = proxy(self.f)
        p.write(bytes(range(10)))
        self.assertEqual(self.f.tell(), p.tell())
        self.f.close()
        self.f = Nic
        self.assertRaises(ReferenceError, getattr, p, 'tell')

    def testSeekTell(self):
        self.f.write(bytes(range(20)))
        self.assertEqual(self.f.tell(), 20)
        self.f.seek(0)
        self.assertEqual(self.f.tell(), 0)
        self.f.seek(10)
        self.assertEqual(self.f.tell(), 10)
        self.f.seek(5, 1)
        self.assertEqual(self.f.tell(), 15)
        self.f.seek(-5, 1)
        self.assertEqual(self.f.tell(), 10)
        self.f.seek(-5, 2)
        self.assertEqual(self.f.tell(), 15)

    def testAttributes(self):
        # verify expected attributes exist
        f = self.f

        self.assertEqual(f.mode, "wb")
        self.assertEqual(f.closed, Nieprawda)

        # verify the attributes are readonly
        dla attr w 'mode', 'closed':
            self.assertRaises((AttributeError, TypeError),
                              setattr, f, attr, 'oops')

    def testBlksize(self):
        # test private _blksize attribute
        blksize = io.DEFAULT_BUFFER_SIZE
        # try to get preferred blksize z stat.st_blksize, jeżeli available
        jeżeli hasattr(os, 'fstat'):
            fst = os.fstat(self.f.fileno())
            blksize = getattr(fst, 'st_blksize', blksize)
        self.assertEqual(self.f._blksize, blksize)

    # verify readinto
    def testReadintoByteArray(self):
        self.f.write(bytes([1, 2, 0, 255]))
        self.f.close()

        ba = bytearray(b'abcdefgh')
        przy self.FileIO(TESTFN, 'r') jako f:
            n = f.readinto(ba)
        self.assertEqual(ba, b'\x01\x02\x00\xffefgh')
        self.assertEqual(n, 4)

    def _testReadintoMemoryview(self):
        self.f.write(bytes([1, 2, 0, 255]))
        self.f.close()

        m = memoryview(bytearray(b'abcdefgh'))
        przy self.FileIO(TESTFN, 'r') jako f:
            n = f.readinto(m)
        self.assertEqual(m, b'\x01\x02\x00\xffefgh')
        self.assertEqual(n, 4)

        m = memoryview(bytearray(b'abcdefgh')).cast('H', shape=[2, 2])
        przy self.FileIO(TESTFN, 'r') jako f:
            n = f.readinto(m)
        self.assertEqual(bytes(m), b'\x01\x02\x00\xffefgh')
        self.assertEqual(n, 4)

    def _testReadintoArray(self):
        self.f.write(bytes([1, 2, 0, 255]))
        self.f.close()

        a = array('B', b'abcdefgh')
        przy self.FileIO(TESTFN, 'r') jako f:
            n = f.readinto(a)
        self.assertEqual(a, array('B', [1, 2, 0, 255, 101, 102, 103, 104]))
        self.assertEqual(n, 4)

        a = array('b', b'abcdefgh')
        przy self.FileIO(TESTFN, 'r') jako f:
            n = f.readinto(a)
        self.assertEqual(a, array('b', [1, 2, 0, -1, 101, 102, 103, 104]))
        self.assertEqual(n, 4)

        a = array('I', b'abcdefgh')
        przy self.FileIO(TESTFN, 'r') jako f:
            n = f.readinto(a)
        self.assertEqual(a, array('I', b'\x01\x02\x00\xffefgh'))
        self.assertEqual(n, 4)

    def testWritelinesList(self):
        l = [b'123', b'456']
        self.f.writelines(l)
        self.f.close()
        self.f = self.FileIO(TESTFN, 'rb')
        buf = self.f.read()
        self.assertEqual(buf, b'123456')

    def testWritelinesUserList(self):
        l = UserList([b'123', b'456'])
        self.f.writelines(l)
        self.f.close()
        self.f = self.FileIO(TESTFN, 'rb')
        buf = self.f.read()
        self.assertEqual(buf, b'123456')

    def testWritelinesError(self):
        self.assertRaises(TypeError, self.f.writelines, [1, 2, 3])
        self.assertRaises(TypeError, self.f.writelines, Nic)
        self.assertRaises(TypeError, self.f.writelines, "abc")

    def test_none_args(self):
        self.f.write(b"hi\nbye\nabc")
        self.f.close()
        self.f = self.FileIO(TESTFN, 'r')
        self.assertEqual(self.f.read(Nic), b"hi\nbye\nabc")
        self.f.seek(0)
        self.assertEqual(self.f.readline(Nic), b"hi\n")
        self.assertEqual(self.f.readlines(Nic), [b"bye\n", b"abc"])

    def test_reject(self):
        self.assertRaises(TypeError, self.f.write, "Hello!")

    def testRepr(self):
        self.assertEqual(repr(self.f),
                         "<%s.FileIO name=%r mode=%r closefd=Prawda>" %
                         (self.modulename, self.f.name, self.f.mode))
        usuń self.f.name
        self.assertEqual(repr(self.f),
                         "<%s.FileIO fd=%r mode=%r closefd=Prawda>" %
                         (self.modulename, self.f.fileno(), self.f.mode))
        self.f.close()
        self.assertEqual(repr(self.f),
                         "<%s.FileIO [closed]>" % (self.modulename,))

    def testReprNoCloseFD(self):
        fd = os.open(TESTFN, os.O_RDONLY)
        spróbuj:
            przy self.FileIO(fd, 'r', closefd=Nieprawda) jako f:
                self.assertEqual(repr(f),
                                 "<%s.FileIO name=%r mode=%r closefd=Nieprawda>" %
                                 (self.modulename, f.name, f.mode))
        w_końcu:
            os.close(fd)

    def testErrors(self):
        f = self.f
        self.assertNieprawda(f.isatty())
        self.assertNieprawda(f.closed)
        #self.assertEqual(f.name, TESTFN)
        self.assertRaises(ValueError, f.read, 10) # Open dla reading
        f.close()
        self.assertPrawda(f.closed)
        f = self.FileIO(TESTFN, 'r')
        self.assertRaises(TypeError, f.readinto, "")
        self.assertNieprawda(f.closed)
        f.close()
        self.assertPrawda(f.closed)

    def testMethods(self):
        methods = ['fileno', 'isatty', 'seekable', 'readable', 'writable',
                   'read', 'readall', 'readline', 'readlines',
                   'tell', 'truncate', 'flush']

        self.f.close()
        self.assertPrawda(self.f.closed)

        dla methodname w methods:
            method = getattr(self.f, methodname)
            # should podnieś on closed file
            self.assertRaises(ValueError, method)

        self.assertRaises(TypeError, self.f.readinto)
        self.assertRaises(ValueError, self.f.readinto, bytearray(1))
        self.assertRaises(TypeError, self.f.seek)
        self.assertRaises(ValueError, self.f.seek, 0)
        self.assertRaises(TypeError, self.f.write)
        self.assertRaises(ValueError, self.f.write, b'')
        self.assertRaises(TypeError, self.f.writelines)
        self.assertRaises(ValueError, self.f.writelines, b'')

    def testOpendir(self):
        # Issue 3703: opening a directory should fill the errno
        # Windows always returns "[Errno 13]: Permission denied
        # Unix uses fstat oraz returns "[Errno 21]: Is a directory"
        spróbuj:
            self.FileIO('.', 'r')
        wyjąwszy OSError jako e:
            self.assertNotEqual(e.errno, 0)
            self.assertEqual(e.filename, ".")
        inaczej:
            self.fail("Should have podnieśd OSError")

    @unittest.skipIf(os.name == 'nt', "test only works on a POSIX-like system")
    def testOpenDirFD(self):
        fd = os.open('.', os.O_RDONLY)
        przy self.assertRaises(OSError) jako cm:
            self.FileIO(fd, 'r')
        os.close(fd)
        self.assertEqual(cm.exception.errno, errno.EISDIR)

    #A set of functions testing that we get expected behaviour jeżeli someone has
    #manually closed the internal file descriptor.  First, a decorator:
    def ClosedFD(func):
        @wraps(func)
        def wrapper(self):
            #forcibly close the fd before invoking the problem function
            f = self.f
            os.close(f.fileno())
            spróbuj:
                func(self, f)
            w_końcu:
                spróbuj:
                    self.f.close()
                wyjąwszy OSError:
                    dalej
        zwróć wrapper

    def ClosedFDRaises(func):
        @wraps(func)
        def wrapper(self):
            #forcibly close the fd before invoking the problem function
            f = self.f
            os.close(f.fileno())
            spróbuj:
                func(self, f)
            wyjąwszy OSError jako e:
                self.assertEqual(e.errno, errno.EBADF)
            inaczej:
                self.fail("Should have podnieśd OSError")
            w_końcu:
                spróbuj:
                    self.f.close()
                wyjąwszy OSError:
                    dalej
        zwróć wrapper

    @ClosedFDRaises
    def testErrnoOnClose(self, f):
        f.close()

    @ClosedFDRaises
    def testErrnoOnClosedWrite(self, f):
        f.write(b'a')

    @ClosedFDRaises
    def testErrnoOnClosedSeek(self, f):
        f.seek(0)

    @ClosedFDRaises
    def testErrnoOnClosedTell(self, f):
        f.tell()

    @ClosedFDRaises
    def testErrnoOnClosedTruncate(self, f):
        f.truncate(0)

    @ClosedFD
    def testErrnoOnClosedSeekable(self, f):
        f.seekable()

    @ClosedFD
    def testErrnoOnClosedReadable(self, f):
        f.readable()

    @ClosedFD
    def testErrnoOnClosedWritable(self, f):
        f.writable()

    @ClosedFD
    def testErrnoOnClosedFileno(self, f):
        f.fileno()

    @ClosedFD
    def testErrnoOnClosedIsatty(self, f):
        self.assertEqual(f.isatty(), Nieprawda)

    def ReopenForRead(self):
        spróbuj:
            self.f.close()
        wyjąwszy OSError:
            dalej
        self.f = self.FileIO(TESTFN, 'r')
        os.close(self.f.fileno())
        zwróć self.f

    @ClosedFDRaises
    def testErrnoOnClosedRead(self, f):
        f = self.ReopenForRead()
        f.read(1)

    @ClosedFDRaises
    def testErrnoOnClosedReadall(self, f):
        f = self.ReopenForRead()
        f.readall()

    @ClosedFDRaises
    def testErrnoOnClosedReadinto(self, f):
        f = self.ReopenForRead()
        a = array('b', b'x'*10)
        f.readinto(a)

klasa CAutoFileTests(AutoFileTests, unittest.TestCase):
    FileIO = _io.FileIO
    modulename = '_io'

klasa PyAutoFileTests(AutoFileTests, unittest.TestCase):
    FileIO = _pyio.FileIO
    modulename = '_pyio'


klasa OtherFileTests:

    def testAbles(self):
        spróbuj:
            f = self.FileIO(TESTFN, "w")
            self.assertEqual(f.readable(), Nieprawda)
            self.assertEqual(f.writable(), Prawda)
            self.assertEqual(f.seekable(), Prawda)
            f.close()

            f = self.FileIO(TESTFN, "r")
            self.assertEqual(f.readable(), Prawda)
            self.assertEqual(f.writable(), Nieprawda)
            self.assertEqual(f.seekable(), Prawda)
            f.close()

            f = self.FileIO(TESTFN, "a+")
            self.assertEqual(f.readable(), Prawda)
            self.assertEqual(f.writable(), Prawda)
            self.assertEqual(f.seekable(), Prawda)
            self.assertEqual(f.isatty(), Nieprawda)
            f.close()

            jeżeli sys.platform != "win32":
                spróbuj:
                    f = self.FileIO("/dev/tty", "a")
                wyjąwszy OSError:
                    # When run w a cron job there just aren't any
                    # ttys, so skip the test.  This also handles other
                    # OS'es that don't support /dev/tty.
                    dalej
                inaczej:
                    self.assertEqual(f.readable(), Nieprawda)
                    self.assertEqual(f.writable(), Prawda)
                    jeżeli sys.platform != "darwin" oraz \
                       'bsd' nie w sys.platform oraz \
                       nie sys.platform.startswith('sunos'):
                        # Somehow /dev/tty appears seekable on some BSDs
                        self.assertEqual(f.seekable(), Nieprawda)
                    self.assertEqual(f.isatty(), Prawda)
                    f.close()
        w_końcu:
            os.unlink(TESTFN)

    def testInvalidModeStrings(self):
        # check invalid mode strings
        dla mode w ("", "aU", "wU+", "rw", "rt"):
            spróbuj:
                f = self.FileIO(TESTFN, mode)
            wyjąwszy ValueError:
                dalej
            inaczej:
                f.close()
                self.fail('%r jest an invalid file mode' % mode)

    def testModeStrings(self):
        # test that the mode attribute jest correct dla various mode strings
        # given jako init args
        spróbuj:
            dla modes w [('w', 'wb'), ('wb', 'wb'), ('wb+', 'rb+'),
                          ('w+b', 'rb+'), ('a', 'ab'), ('ab', 'ab'),
                          ('ab+', 'ab+'), ('a+b', 'ab+'), ('r', 'rb'),
                          ('rb', 'rb'), ('rb+', 'rb+'), ('r+b', 'rb+')]:
                # read modes are last so that TESTFN will exist first
                przy self.FileIO(TESTFN, modes[0]) jako f:
                    self.assertEqual(f.mode, modes[1])
        w_końcu:
            jeżeli os.path.exists(TESTFN):
                os.unlink(TESTFN)

    def testUnicodeOpen(self):
        # verify repr works dla unicode too
        f = self.FileIO(str(TESTFN), "w")
        f.close()
        os.unlink(TESTFN)

    def testBytesOpen(self):
        # Opening a bytes filename
        spróbuj:
            fn = TESTFN.encode("ascii")
        wyjąwszy UnicodeEncodeError:
            self.skipTest('could nie encode %r to ascii' % TESTFN)
        f = self.FileIO(fn, "w")
        spróbuj:
            f.write(b"abc")
            f.close()
            przy open(TESTFN, "rb") jako f:
                self.assertEqual(f.read(), b"abc")
        w_końcu:
            os.unlink(TESTFN)

    def testConstructorHandlesNULChars(self):
        fn_with_NUL = 'foo\0bar'
        self.assertRaises(ValueError, self.FileIO, fn_with_NUL, 'w')
        self.assertRaises(ValueError, self.FileIO, bytes(fn_with_NUL, 'ascii'), 'w')

    def testInvalidFd(self):
        self.assertRaises(ValueError, self.FileIO, -10)
        self.assertRaises(OSError, self.FileIO, make_bad_fd())
        jeżeli sys.platform == 'win32':
            zaimportuj msvcrt
            self.assertRaises(OSError, msvcrt.get_osfhandle, make_bad_fd())

    def testBadModeArgument(self):
        # verify that we get a sensible error message dla bad mode argument
        bad_mode = "qwerty"
        spróbuj:
            f = self.FileIO(TESTFN, bad_mode)
        wyjąwszy ValueError jako msg:
            jeżeli msg.args[0] != 0:
                s = str(msg)
                jeżeli TESTFN w s albo bad_mode nie w s:
                    self.fail("bad error message dla invalid mode: %s" % s)
            # jeżeli msg.args[0] == 0, we're probably on Windows where there may be
            # no obvious way to discover why open() failed.
        inaczej:
            f.close()
            self.fail("no error dla invalid mode: %s" % bad_mode)

    def testTruncate(self):
        f = self.FileIO(TESTFN, 'w')
        f.write(bytes(bytearray(range(10))))
        self.assertEqual(f.tell(), 10)
        f.truncate(5)
        self.assertEqual(f.tell(), 10)
        self.assertEqual(f.seek(0, io.SEEK_END), 5)
        f.truncate(15)
        self.assertEqual(f.tell(), 5)
        self.assertEqual(f.seek(0, io.SEEK_END), 15)
        f.close()

    def testTruncateOnWindows(self):
        def bug801631():
            # SF bug <http://www.python.org/sf/801631>
            # "file.truncate fault on windows"
            f = self.FileIO(TESTFN, 'w')
            f.write(bytes(range(11)))
            f.close()

            f = self.FileIO(TESTFN,'r+')
            data = f.read(5)
            jeżeli data != bytes(range(5)):
                self.fail("Read on file opened dla update failed %r" % data)
            jeżeli f.tell() != 5:
                self.fail("File pos after read wrong %d" % f.tell())

            f.truncate()
            jeżeli f.tell() != 5:
                self.fail("File pos after ftruncate wrong %d" % f.tell())

            f.close()
            size = os.path.getsize(TESTFN)
            jeżeli size != 5:
                self.fail("File size after ftruncate wrong %d" % size)

        spróbuj:
            bug801631()
        w_końcu:
            os.unlink(TESTFN)

    def testAppend(self):
        spróbuj:
            f = open(TESTFN, 'wb')
            f.write(b'spam')
            f.close()
            f = open(TESTFN, 'ab')
            f.write(b'eggs')
            f.close()
            f = open(TESTFN, 'rb')
            d = f.read()
            f.close()
            self.assertEqual(d, b'spameggs')
        w_końcu:
            spróbuj:
                os.unlink(TESTFN)
            wyjąwszy:
                dalej

    def testInvalidInit(self):
        self.assertRaises(TypeError, self.FileIO, "1", 0, 0)

    def testWarnings(self):
        przy check_warnings(quiet=Prawda) jako w:
            self.assertEqual(w.warnings, [])
            self.assertRaises(TypeError, self.FileIO, [])
            self.assertEqual(w.warnings, [])
            self.assertRaises(ValueError, self.FileIO, "/some/invalid/name", "rt")
            self.assertEqual(w.warnings, [])

    def testUnclosedFDOnException(self):
        klasa MyException(Exception): dalej
        klasa MyFileIO(self.FileIO):
            def __setattr__(self, name, value):
                jeżeli name == "name":
                    podnieś MyException("blocked setting name")
                zwróć super(MyFileIO, self).__setattr__(name, value)
        fd = os.open(__file__, os.O_RDONLY)
        self.assertRaises(MyException, MyFileIO, fd)
        os.close(fd)  # should nie podnieś OSError(EBADF)

klasa COtherFileTests(OtherFileTests, unittest.TestCase):
    FileIO = _io.FileIO
    modulename = '_io'

    @cpython_only
    def testInvalidFd_overflow(self):
        # Issue 15989
        zaimportuj _testcapi
        self.assertRaises(TypeError, self.FileIO, _testcapi.INT_MAX + 1)
        self.assertRaises(TypeError, self.FileIO, _testcapi.INT_MIN - 1)

klasa PyOtherFileTests(OtherFileTests, unittest.TestCase):
    FileIO = _pyio.FileIO
    modulename = '_pyio'


def test_main():
    # Historically, these tests have been sloppy about removing TESTFN.
    # So get rid of it no matter what.
    spróbuj:
        run_unittest(CAutoFileTests, PyAutoFileTests,
                     COtherFileTests, PyOtherFileTests)
    w_końcu:
        jeżeli os.path.exists(TESTFN):
            os.unlink(TESTFN)

jeżeli __name__ == '__main__':
    test_main()
