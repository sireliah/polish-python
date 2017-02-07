"""Unit tests dla the io module."""

# Tests of io are scattered over the test suite:
# * test_bufio - tests file buffering
# * test_memoryio - tests BytesIO oraz StringIO
# * test_fileio - tests FileIO
# * test_file - tests the file interface
# * test_io - tests everything inaczej w the io module
# * test_univnewlines - tests universal newline support
# * test_largefile - tests operations on a file greater than 2**32 bytes
#     (only enabled przy -ulargefile)

################################################################################
# ATTENTION TEST WRITERS!!!
################################################################################
# When writing tests dla io, it's important to test both the C oraz Python
# implementations. This jest usually done by writing a base test that refers to
# the type it jest testing jako a attribute. Then it provides custom subclasses to
# test both implementations. This file has lots of examples.
################################################################################

zaimportuj abc
zaimportuj array
zaimportuj errno
zaimportuj locale
zaimportuj os
zaimportuj pickle
zaimportuj random
zaimportuj signal
zaimportuj sys
zaimportuj time
zaimportuj unittest
zaimportuj warnings
zaimportuj weakref
z collections zaimportuj deque, UserList
z itertools zaimportuj cycle, count
z test zaimportuj support
z test.support.script_helper zaimportuj assert_python_ok, run_python_until_end

zaimportuj codecs
zaimportuj io  # C implementation of io
zaimportuj _pyio jako pyio # Python implementation of io
spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic

def _default_chunk_size():
    """Get the default TextIOWrapper chunk size"""
    przy open(__file__, "r", encoding="latin-1") jako f:
        zwróć f._CHUNK_SIZE


klasa MockRawIOWithoutRead:
    """A RawIO implementation without read(), so jako to exercise the default
    RawIO.read() which calls readinto()."""

    def __init__(self, read_stack=()):
        self._read_stack = list(read_stack)
        self._write_stack = []
        self._reads = 0
        self._extraneous_reads = 0

    def write(self, b):
        self._write_stack.append(bytes(b))
        zwróć len(b)

    def writable(self):
        zwróć Prawda

    def fileno(self):
        zwróć 42

    def readable(self):
        zwróć Prawda

    def seekable(self):
        zwróć Prawda

    def seek(self, pos, whence):
        zwróć 0   # wrong but we gotta zwróć something

    def tell(self):
        zwróć 0   # same comment jako above

    def readinto(self, buf):
        self._reads += 1
        max_len = len(buf)
        spróbuj:
            data = self._read_stack[0]
        wyjąwszy IndexError:
            self._extraneous_reads += 1
            zwróć 0
        jeżeli data jest Nic:
            usuń self._read_stack[0]
            zwróć Nic
        n = len(data)
        jeżeli len(data) <= max_len:
            usuń self._read_stack[0]
            buf[:n] = data
            zwróć n
        inaczej:
            buf[:] = data[:max_len]
            self._read_stack[0] = data[max_len:]
            zwróć max_len

    def truncate(self, pos=Nic):
        zwróć pos

klasa CMockRawIOWithoutRead(MockRawIOWithoutRead, io.RawIOBase):
    dalej

klasa PyMockRawIOWithoutRead(MockRawIOWithoutRead, pyio.RawIOBase):
    dalej


klasa MockRawIO(MockRawIOWithoutRead):

    def read(self, n=Nic):
        self._reads += 1
        spróbuj:
            zwróć self._read_stack.pop(0)
        wyjąwszy:
            self._extraneous_reads += 1
            zwróć b""

klasa CMockRawIO(MockRawIO, io.RawIOBase):
    dalej

klasa PyMockRawIO(MockRawIO, pyio.RawIOBase):
    dalej


klasa MisbehavedRawIO(MockRawIO):
    def write(self, b):
        zwróć super().write(b) * 2

    def read(self, n=Nic):
        zwróć super().read(n) * 2

    def seek(self, pos, whence):
        zwróć -123

    def tell(self):
        zwróć -456

    def readinto(self, buf):
        super().readinto(buf)
        zwróć len(buf) * 5

klasa CMisbehavedRawIO(MisbehavedRawIO, io.RawIOBase):
    dalej

klasa PyMisbehavedRawIO(MisbehavedRawIO, pyio.RawIOBase):
    dalej


klasa CloseFailureIO(MockRawIO):
    closed = 0

    def close(self):
        jeżeli nie self.closed:
            self.closed = 1
            podnieś OSError

klasa CCloseFailureIO(CloseFailureIO, io.RawIOBase):
    dalej

klasa PyCloseFailureIO(CloseFailureIO, pyio.RawIOBase):
    dalej


klasa MockFileIO:

    def __init__(self, data):
        self.read_history = []
        super().__init__(data)

    def read(self, n=Nic):
        res = super().read(n)
        self.read_history.append(Nic jeżeli res jest Nic inaczej len(res))
        zwróć res

    def readinto(self, b):
        res = super().readinto(b)
        self.read_history.append(res)
        zwróć res

klasa CMockFileIO(MockFileIO, io.BytesIO):
    dalej

klasa PyMockFileIO(MockFileIO, pyio.BytesIO):
    dalej


klasa MockUnseekableIO:
    def seekable(self):
        zwróć Nieprawda

    def seek(self, *args):
        podnieś self.UnsupportedOperation("not seekable")

    def tell(self, *args):
        podnieś self.UnsupportedOperation("not seekable")

klasa CMockUnseekableIO(MockUnseekableIO, io.BytesIO):
    UnsupportedOperation = io.UnsupportedOperation

klasa PyMockUnseekableIO(MockUnseekableIO, pyio.BytesIO):
    UnsupportedOperation = pyio.UnsupportedOperation


klasa MockNonBlockWriterIO:

    def __init__(self):
        self._write_stack = []
        self._blocker_char = Nic

    def pop_written(self):
        s = b"".join(self._write_stack)
        self._write_stack[:] = []
        zwróć s

    def block_on(self, char):
        """Block when a given char jest encountered."""
        self._blocker_char = char

    def readable(self):
        zwróć Prawda

    def seekable(self):
        zwróć Prawda

    def writable(self):
        zwróć Prawda

    def write(self, b):
        b = bytes(b)
        n = -1
        jeżeli self._blocker_char:
            spróbuj:
                n = b.index(self._blocker_char)
            wyjąwszy ValueError:
                dalej
            inaczej:
                jeżeli n > 0:
                    # write data up to the first blocker
                    self._write_stack.append(b[:n])
                    zwróć n
                inaczej:
                    # cancel blocker oraz indicate would block
                    self._blocker_char = Nic
                    zwróć Nic
        self._write_stack.append(b)
        zwróć len(b)

klasa CMockNonBlockWriterIO(MockNonBlockWriterIO, io.RawIOBase):
    BlockingIOError = io.BlockingIOError

klasa PyMockNonBlockWriterIO(MockNonBlockWriterIO, pyio.RawIOBase):
    BlockingIOError = pyio.BlockingIOError


klasa IOTest(unittest.TestCase):

    def setUp(self):
        support.unlink(support.TESTFN)

    def tearDown(self):
        support.unlink(support.TESTFN)

    def write_ops(self, f):
        self.assertEqual(f.write(b"blah."), 5)
        f.truncate(0)
        self.assertEqual(f.tell(), 5)
        f.seek(0)

        self.assertEqual(f.write(b"blah."), 5)
        self.assertEqual(f.seek(0), 0)
        self.assertEqual(f.write(b"Hello."), 6)
        self.assertEqual(f.tell(), 6)
        self.assertEqual(f.seek(-1, 1), 5)
        self.assertEqual(f.tell(), 5)
        self.assertEqual(f.write(bytearray(b" world\n\n\n")), 9)
        self.assertEqual(f.seek(0), 0)
        self.assertEqual(f.write(b"h"), 1)
        self.assertEqual(f.seek(-1, 2), 13)
        self.assertEqual(f.tell(), 13)

        self.assertEqual(f.truncate(12), 12)
        self.assertEqual(f.tell(), 13)
        self.assertRaises(TypeError, f.seek, 0.0)

    def read_ops(self, f, buffered=Nieprawda):
        data = f.read(5)
        self.assertEqual(data, b"hello")
        data = bytearray(data)
        self.assertEqual(f.readinto(data), 5)
        self.assertEqual(data, b" worl")
        self.assertEqual(f.readinto(data), 2)
        self.assertEqual(len(data), 5)
        self.assertEqual(data[:2], b"d\n")
        self.assertEqual(f.seek(0), 0)
        self.assertEqual(f.read(20), b"hello world\n")
        self.assertEqual(f.read(1), b"")
        self.assertEqual(f.readinto(bytearray(b"x")), 0)
        self.assertEqual(f.seek(-6, 2), 6)
        self.assertEqual(f.read(5), b"world")
        self.assertEqual(f.read(0), b"")
        self.assertEqual(f.readinto(bytearray()), 0)
        self.assertEqual(f.seek(-6, 1), 5)
        self.assertEqual(f.read(5), b" worl")
        self.assertEqual(f.tell(), 10)
        self.assertRaises(TypeError, f.seek, 0.0)
        jeżeli buffered:
            f.seek(0)
            self.assertEqual(f.read(), b"hello world\n")
            f.seek(6)
            self.assertEqual(f.read(), b"world\n")
            self.assertEqual(f.read(), b"")

    LARGE = 2**31

    def large_file_ops(self, f):
        assert f.readable()
        assert f.writable()
        self.assertEqual(f.seek(self.LARGE), self.LARGE)
        self.assertEqual(f.tell(), self.LARGE)
        self.assertEqual(f.write(b"xxx"), 3)
        self.assertEqual(f.tell(), self.LARGE + 3)
        self.assertEqual(f.seek(-1, 1), self.LARGE + 2)
        self.assertEqual(f.truncate(), self.LARGE + 2)
        self.assertEqual(f.tell(), self.LARGE + 2)
        self.assertEqual(f.seek(0, 2), self.LARGE + 2)
        self.assertEqual(f.truncate(self.LARGE + 1), self.LARGE + 1)
        self.assertEqual(f.tell(), self.LARGE + 2)
        self.assertEqual(f.seek(0, 2), self.LARGE + 1)
        self.assertEqual(f.seek(-1, 2), self.LARGE)
        self.assertEqual(f.read(2), b"x")

    def test_invalid_operations(self):
        # Try writing on a file opened w read mode oraz vice-versa.
        exc = self.UnsupportedOperation
        dla mode w ("w", "wb"):
            przy self.open(support.TESTFN, mode) jako fp:
                self.assertRaises(exc, fp.read)
                self.assertRaises(exc, fp.readline)
        przy self.open(support.TESTFN, "wb", buffering=0) jako fp:
            self.assertRaises(exc, fp.read)
            self.assertRaises(exc, fp.readline)
        przy self.open(support.TESTFN, "rb", buffering=0) jako fp:
            self.assertRaises(exc, fp.write, b"blah")
            self.assertRaises(exc, fp.writelines, [b"blah\n"])
        przy self.open(support.TESTFN, "rb") jako fp:
            self.assertRaises(exc, fp.write, b"blah")
            self.assertRaises(exc, fp.writelines, [b"blah\n"])
        przy self.open(support.TESTFN, "r") jako fp:
            self.assertRaises(exc, fp.write, "blah")
            self.assertRaises(exc, fp.writelines, ["blah\n"])
            # Non-zero seeking z current albo end pos
            self.assertRaises(exc, fp.seek, 1, self.SEEK_CUR)
            self.assertRaises(exc, fp.seek, -1, self.SEEK_END)

    def test_open_handles_NUL_chars(self):
        fn_with_NUL = 'foo\0bar'
        self.assertRaises(ValueError, self.open, fn_with_NUL, 'w')
        self.assertRaises(ValueError, self.open, bytes(fn_with_NUL, 'ascii'), 'w')

    def test_raw_file_io(self):
        przy self.open(support.TESTFN, "wb", buffering=0) jako f:
            self.assertEqual(f.readable(), Nieprawda)
            self.assertEqual(f.writable(), Prawda)
            self.assertEqual(f.seekable(), Prawda)
            self.write_ops(f)
        przy self.open(support.TESTFN, "rb", buffering=0) jako f:
            self.assertEqual(f.readable(), Prawda)
            self.assertEqual(f.writable(), Nieprawda)
            self.assertEqual(f.seekable(), Prawda)
            self.read_ops(f)

    def test_buffered_file_io(self):
        przy self.open(support.TESTFN, "wb") jako f:
            self.assertEqual(f.readable(), Nieprawda)
            self.assertEqual(f.writable(), Prawda)
            self.assertEqual(f.seekable(), Prawda)
            self.write_ops(f)
        przy self.open(support.TESTFN, "rb") jako f:
            self.assertEqual(f.readable(), Prawda)
            self.assertEqual(f.writable(), Nieprawda)
            self.assertEqual(f.seekable(), Prawda)
            self.read_ops(f, Prawda)

    def test_readline(self):
        przy self.open(support.TESTFN, "wb") jako f:
            f.write(b"abc\ndef\nxyzzy\nfoo\x00bar\nanother line")
        przy self.open(support.TESTFN, "rb") jako f:
            self.assertEqual(f.readline(), b"abc\n")
            self.assertEqual(f.readline(10), b"def\n")
            self.assertEqual(f.readline(2), b"xy")
            self.assertEqual(f.readline(4), b"zzy\n")
            self.assertEqual(f.readline(), b"foo\x00bar\n")
            self.assertEqual(f.readline(Nic), b"another line")
            self.assertRaises(TypeError, f.readline, 5.3)
        przy self.open(support.TESTFN, "r") jako f:
            self.assertRaises(TypeError, f.readline, 5.3)

    def test_raw_bytes_io(self):
        f = self.BytesIO()
        self.write_ops(f)
        data = f.getvalue()
        self.assertEqual(data, b"hello world\n")
        f = self.BytesIO(data)
        self.read_ops(f, Prawda)

    def test_large_file_ops(self):
        # On Windows oraz Mac OSX this test comsumes large resources; It takes
        # a long time to build the >2GB file oraz takes >2GB of disk space
        # therefore the resource must be enabled to run this test.
        jeżeli sys.platform[:3] == 'win' albo sys.platform == 'darwin':
            support.requires(
                'largefile',
                'test requires %s bytes oraz a long time to run' % self.LARGE)
        przy self.open(support.TESTFN, "w+b", 0) jako f:
            self.large_file_ops(f)
        przy self.open(support.TESTFN, "w+b") jako f:
            self.large_file_ops(f)

    def test_with_open(self):
        dla bufsize w (0, 1, 100):
            f = Nic
            przy self.open(support.TESTFN, "wb", bufsize) jako f:
                f.write(b"xxx")
            self.assertEqual(f.closed, Prawda)
            f = Nic
            spróbuj:
                przy self.open(support.TESTFN, "wb", bufsize) jako f:
                    1/0
            wyjąwszy ZeroDivisionError:
                self.assertEqual(f.closed, Prawda)
            inaczej:
                self.fail("1/0 didn't podnieś an exception")

    # issue 5008
    def test_append_mode_tell(self):
        przy self.open(support.TESTFN, "wb") jako f:
            f.write(b"xxx")
        przy self.open(support.TESTFN, "ab", buffering=0) jako f:
            self.assertEqual(f.tell(), 3)
        przy self.open(support.TESTFN, "ab") jako f:
            self.assertEqual(f.tell(), 3)
        przy self.open(support.TESTFN, "a") jako f:
            self.assertGreater(f.tell(), 0)

    def test_destructor(self):
        record = []
        klasa MyFileIO(self.FileIO):
            def __del__(self):
                record.append(1)
                spróbuj:
                    f = super().__del__
                wyjąwszy AttributeError:
                    dalej
                inaczej:
                    f()
            def close(self):
                record.append(2)
                super().close()
            def flush(self):
                record.append(3)
                super().flush()
        przy support.check_warnings(('', ResourceWarning)):
            f = MyFileIO(support.TESTFN, "wb")
            f.write(b"xxx")
            usuń f
            support.gc_collect()
            self.assertEqual(record, [1, 2, 3])
            przy self.open(support.TESTFN, "rb") jako f:
                self.assertEqual(f.read(), b"xxx")

    def _check_base_destructor(self, base):
        record = []
        klasa MyIO(base):
            def __init__(self):
                # This exercises the availability of attributes on object
                # destruction.
                # (in the C version, close() jest called by the tp_dealloc
                # function, nie by __del__)
                self.on_usuń = 1
                self.on_close = 2
                self.on_flush = 3
            def __del__(self):
                record.append(self.on_del)
                spróbuj:
                    f = super().__del__
                wyjąwszy AttributeError:
                    dalej
                inaczej:
                    f()
            def close(self):
                record.append(self.on_close)
                super().close()
            def flush(self):
                record.append(self.on_flush)
                super().flush()
        f = MyIO()
        usuń f
        support.gc_collect()
        self.assertEqual(record, [1, 2, 3])

    def test_IOBase_destructor(self):
        self._check_base_destructor(self.IOBase)

    def test_RawIOBase_destructor(self):
        self._check_base_destructor(self.RawIOBase)

    def test_BufferedIOBase_destructor(self):
        self._check_base_destructor(self.BufferedIOBase)

    def test_TextIOBase_destructor(self):
        self._check_base_destructor(self.TextIOBase)

    def test_close_flushes(self):
        przy self.open(support.TESTFN, "wb") jako f:
            f.write(b"xxx")
        przy self.open(support.TESTFN, "rb") jako f:
            self.assertEqual(f.read(), b"xxx")

    def test_array_writes(self):
        a = array.array('i', range(10))
        n = len(a.tobytes())
        przy self.open(support.TESTFN, "wb", 0) jako f:
            self.assertEqual(f.write(a), n)
        przy self.open(support.TESTFN, "wb") jako f:
            self.assertEqual(f.write(a), n)

    def test_closefd(self):
        self.assertRaises(ValueError, self.open, support.TESTFN, 'w',
                          closefd=Nieprawda)

    def test_read_closed(self):
        przy self.open(support.TESTFN, "w") jako f:
            f.write("egg\n")
        przy self.open(support.TESTFN, "r") jako f:
            file = self.open(f.fileno(), "r", closefd=Nieprawda)
            self.assertEqual(file.read(), "egg\n")
            file.seek(0)
            file.close()
            self.assertRaises(ValueError, file.read)

    def test_no_closefd_with_filename(self):
        # can't use closefd w combination przy a file name
        self.assertRaises(ValueError, self.open, support.TESTFN, "r", closefd=Nieprawda)

    def test_closefd_attr(self):
        przy self.open(support.TESTFN, "wb") jako f:
            f.write(b"egg\n")
        przy self.open(support.TESTFN, "r") jako f:
            self.assertEqual(f.buffer.raw.closefd, Prawda)
            file = self.open(f.fileno(), "r", closefd=Nieprawda)
            self.assertEqual(file.buffer.raw.closefd, Nieprawda)

    def test_garbage_collection(self):
        # FileIO objects are collected, oraz collecting them flushes
        # all data to disk.
        przy support.check_warnings(('', ResourceWarning)):
            f = self.FileIO(support.TESTFN, "wb")
            f.write(b"abcxxx")
            f.f = f
            wr = weakref.ref(f)
            usuń f
            support.gc_collect()
        self.assertIsNic(wr(), wr)
        przy self.open(support.TESTFN, "rb") jako f:
            self.assertEqual(f.read(), b"abcxxx")

    def test_unbounded_file(self):
        # Issue #1174606: reading z an unbounded stream such jako /dev/zero.
        zero = "/dev/zero"
        jeżeli nie os.path.exists(zero):
            self.skipTest("{0} does nie exist".format(zero))
        jeżeli sys.maxsize > 0x7FFFFFFF:
            self.skipTest("test can only run w a 32-bit address space")
        jeżeli support.real_max_memuse < support._2G:
            self.skipTest("test requires at least 2GB of memory")
        przy self.open(zero, "rb", buffering=0) jako f:
            self.assertRaises(OverflowError, f.read)
        przy self.open(zero, "rb") jako f:
            self.assertRaises(OverflowError, f.read)
        przy self.open(zero, "r") jako f:
            self.assertRaises(OverflowError, f.read)

    def check_flush_error_on_close(self, *args, **kwargs):
        # Test that the file jest closed despite failed flush
        # oraz that flush() jest called before file closed.
        f = self.open(*args, **kwargs)
        closed = []
        def bad_flush():
            closed[:] = [f.closed]
            podnieś OSError()
        f.flush = bad_flush
        self.assertRaises(OSError, f.close) # exception nie swallowed
        self.assertPrawda(f.closed)
        self.assertPrawda(closed)      # flush() called
        self.assertNieprawda(closed[0])  # flush() called before file closed
        f.flush = lambda: Nic  # przerwij reference loop

    def test_flush_error_on_close(self):
        # raw file
        # Issue #5700: io.FileIO calls flush() after file closed
        self.check_flush_error_on_close(support.TESTFN, 'wb', buffering=0)
        fd = os.open(support.TESTFN, os.O_WRONLY|os.O_CREAT)
        self.check_flush_error_on_close(fd, 'wb', buffering=0)
        fd = os.open(support.TESTFN, os.O_WRONLY|os.O_CREAT)
        self.check_flush_error_on_close(fd, 'wb', buffering=0, closefd=Nieprawda)
        os.close(fd)
        # buffered io
        self.check_flush_error_on_close(support.TESTFN, 'wb')
        fd = os.open(support.TESTFN, os.O_WRONLY|os.O_CREAT)
        self.check_flush_error_on_close(fd, 'wb')
        fd = os.open(support.TESTFN, os.O_WRONLY|os.O_CREAT)
        self.check_flush_error_on_close(fd, 'wb', closefd=Nieprawda)
        os.close(fd)
        # text io
        self.check_flush_error_on_close(support.TESTFN, 'w')
        fd = os.open(support.TESTFN, os.O_WRONLY|os.O_CREAT)
        self.check_flush_error_on_close(fd, 'w')
        fd = os.open(support.TESTFN, os.O_WRONLY|os.O_CREAT)
        self.check_flush_error_on_close(fd, 'w', closefd=Nieprawda)
        os.close(fd)

    def test_multi_close(self):
        f = self.open(support.TESTFN, "wb", buffering=0)
        f.close()
        f.close()
        f.close()
        self.assertRaises(ValueError, f.flush)

    def test_RawIOBase_read(self):
        # Exercise the default RawIOBase.read() implementation (which calls
        # readinto() internally).
        rawio = self.MockRawIOWithoutRead((b"abc", b"d", Nic, b"efg", Nic))
        self.assertEqual(rawio.read(2), b"ab")
        self.assertEqual(rawio.read(2), b"c")
        self.assertEqual(rawio.read(2), b"d")
        self.assertEqual(rawio.read(2), Nic)
        self.assertEqual(rawio.read(2), b"ef")
        self.assertEqual(rawio.read(2), b"g")
        self.assertEqual(rawio.read(2), Nic)
        self.assertEqual(rawio.read(2), b"")

    def test_types_have_dict(self):
        test = (
            self.IOBase(),
            self.RawIOBase(),
            self.TextIOBase(),
            self.StringIO(),
            self.BytesIO()
        )
        dla obj w test:
            self.assertPrawda(hasattr(obj, "__dict__"))

    def test_opener(self):
        przy self.open(support.TESTFN, "w") jako f:
            f.write("egg\n")
        fd = os.open(support.TESTFN, os.O_RDONLY)
        def opener(path, flags):
            zwróć fd
        przy self.open("non-existent", "r", opener=opener) jako f:
            self.assertEqual(f.read(), "egg\n")

    def test_fileio_closefd(self):
        # Issue #4841
        przy self.open(__file__, 'rb') jako f1, \
             self.open(__file__, 'rb') jako f2:
            fileio = self.FileIO(f1.fileno(), closefd=Nieprawda)
            # .__init__() must nie close f1
            fileio.__init__(f2.fileno(), closefd=Nieprawda)
            f1.readline()
            # .close() must nie close f2
            fileio.close()
            f2.readline()

    def test_nonbuffered_textio(self):
        przy warnings.catch_warnings(record=Prawda) jako recorded:
            przy self.assertRaises(ValueError):
                self.open(support.TESTFN, 'w', buffering=0)
            support.gc_collect()
        self.assertEqual(recorded, [])

    def test_invalid_newline(self):
        przy warnings.catch_warnings(record=Prawda) jako recorded:
            przy self.assertRaises(ValueError):
                self.open(support.TESTFN, 'w', newline='invalid')
            support.gc_collect()
        self.assertEqual(recorded, [])


klasa CIOTest(IOTest):

    def test_IOBase_finalize(self):
        # Issue #12149: segmentation fault on _PyIOBase_finalize when both a
        # klasa which inherits IOBase oraz an object of this klasa are caught
        # w a reference cycle oraz close() jest already w the method cache.
        klasa MyIO(self.IOBase):
            def close(self):
                dalej

        # create an instance to populate the method cache
        MyIO()
        obj = MyIO()
        obj.obj = obj
        wr = weakref.ref(obj)
        usuń MyIO
        usuń obj
        support.gc_collect()
        self.assertIsNic(wr(), wr)

klasa PyIOTest(IOTest):
    dalej


@support.cpython_only
klasa APIMismatchTest(unittest.TestCase):

    def test_RawIOBase_io_in_pyio_match(self):
        """Test that pyio RawIOBase klasa has all c RawIOBase methods"""
        mismatch = support.detect_api_mismatch(pyio.RawIOBase, io.RawIOBase,
                                               ignore=('__weakref__',))
        self.assertEqual(mismatch, set(), msg='Python RawIOBase does nie have all C RawIOBase methods')

    def test_RawIOBase_pyio_in_io_match(self):
        """Test that c RawIOBase klasa has all pyio RawIOBase methods"""
        mismatch = support.detect_api_mismatch(io.RawIOBase, pyio.RawIOBase)
        self.assertEqual(mismatch, set(), msg='C RawIOBase does nie have all Python RawIOBase methods')


klasa CommonBufferedTests:
    # Tests common to BufferedReader, BufferedWriter oraz BufferedRandom

    def test_detach(self):
        raw = self.MockRawIO()
        buf = self.tp(raw)
        self.assertIs(buf.detach(), raw)
        self.assertRaises(ValueError, buf.detach)

        repr(buf)  # Should still work

    def test_fileno(self):
        rawio = self.MockRawIO()
        bufio = self.tp(rawio)

        self.assertEqual(42, bufio.fileno())

    @unittest.skip('test having existential crisis')
    def test_no_fileno(self):
        # XXX will we always have fileno() function? If so, kill
        # this test. Else, write it.
        dalej

    def test_invalid_args(self):
        rawio = self.MockRawIO()
        bufio = self.tp(rawio)
        # Invalid whence
        self.assertRaises(ValueError, bufio.seek, 0, -1)
        self.assertRaises(ValueError, bufio.seek, 0, 9)

    def test_override_destructor(self):
        tp = self.tp
        record = []
        klasa MyBufferedIO(tp):
            def __del__(self):
                record.append(1)
                spróbuj:
                    f = super().__del__
                wyjąwszy AttributeError:
                    dalej
                inaczej:
                    f()
            def close(self):
                record.append(2)
                super().close()
            def flush(self):
                record.append(3)
                super().flush()
        rawio = self.MockRawIO()
        bufio = MyBufferedIO(rawio)
        writable = bufio.writable()
        usuń bufio
        support.gc_collect()
        jeżeli writable:
            self.assertEqual(record, [1, 2, 3])
        inaczej:
            self.assertEqual(record, [1, 2])

    def test_context_manager(self):
        # Test usability jako a context manager
        rawio = self.MockRawIO()
        bufio = self.tp(rawio)
        def _with():
            przy bufio:
                dalej
        _with()
        # bufio should now be closed, oraz using it a second time should podnieś
        # a ValueError.
        self.assertRaises(ValueError, _with)

    def test_error_through_destructor(self):
        # Test that the exception state jest nie modified by a destructor,
        # even jeżeli close() fails.
        rawio = self.CloseFailureIO()
        def f():
            self.tp(rawio).xyzzy
        przy support.captured_output("stderr") jako s:
            self.assertRaises(AttributeError, f)
        s = s.getvalue().strip()
        jeżeli s:
            # The destructor *may* have printed an unraisable error, check it
            self.assertEqual(len(s.splitlines()), 1)
            self.assertPrawda(s.startswith("Exception OSError: "), s)
            self.assertPrawda(s.endswith(" ignored"), s)

    def test_repr(self):
        raw = self.MockRawIO()
        b = self.tp(raw)
        clsname = "%s.%s" % (self.tp.__module__, self.tp.__qualname__)
        self.assertEqual(repr(b), "<%s>" % clsname)
        raw.name = "dummy"
        self.assertEqual(repr(b), "<%s name='dummy'>" % clsname)
        raw.name = b"dummy"
        self.assertEqual(repr(b), "<%s name=b'dummy'>" % clsname)

    def test_flush_error_on_close(self):
        # Test that buffered file jest closed despite failed flush
        # oraz that flush() jest called before file closed.
        raw = self.MockRawIO()
        closed = []
        def bad_flush():
            closed[:] = [b.closed, raw.closed]
            podnieś OSError()
        raw.flush = bad_flush
        b = self.tp(raw)
        self.assertRaises(OSError, b.close) # exception nie swallowed
        self.assertPrawda(b.closed)
        self.assertPrawda(raw.closed)
        self.assertPrawda(closed)      # flush() called
        self.assertNieprawda(closed[0])  # flush() called before file closed
        self.assertNieprawda(closed[1])
        raw.flush = lambda: Nic  # przerwij reference loop

    def test_close_error_on_close(self):
        raw = self.MockRawIO()
        def bad_flush():
            podnieś OSError('flush')
        def bad_close():
            podnieś OSError('close')
        raw.close = bad_close
        b = self.tp(raw)
        b.flush = bad_flush
        przy self.assertRaises(OSError) jako err: # exception nie swallowed
            b.close()
        self.assertEqual(err.exception.args, ('close',))
        self.assertIsInstance(err.exception.__context__, OSError)
        self.assertEqual(err.exception.__context__.args, ('flush',))
        self.assertNieprawda(b.closed)

    def test_nonnormalized_close_error_on_close(self):
        # Issue #21677
        raw = self.MockRawIO()
        def bad_flush():
            podnieś non_existing_flush
        def bad_close():
            podnieś non_existing_close
        raw.close = bad_close
        b = self.tp(raw)
        b.flush = bad_flush
        przy self.assertRaises(NameError) jako err: # exception nie swallowed
            b.close()
        self.assertIn('non_existing_close', str(err.exception))
        self.assertIsInstance(err.exception.__context__, NameError)
        self.assertIn('non_existing_flush', str(err.exception.__context__))
        self.assertNieprawda(b.closed)

    def test_multi_close(self):
        raw = self.MockRawIO()
        b = self.tp(raw)
        b.close()
        b.close()
        b.close()
        self.assertRaises(ValueError, b.flush)

    def test_unseekable(self):
        bufio = self.tp(self.MockUnseekableIO(b"A" * 10))
        self.assertRaises(self.UnsupportedOperation, bufio.tell)
        self.assertRaises(self.UnsupportedOperation, bufio.seek, 0)

    def test_readonly_attributes(self):
        raw = self.MockRawIO()
        buf = self.tp(raw)
        x = self.MockRawIO()
        przy self.assertRaises(AttributeError):
            buf.raw = x


klasa SizeofTest:

    @support.cpython_only
    def test_sizeof(self):
        bufsize1 = 4096
        bufsize2 = 8192
        rawio = self.MockRawIO()
        bufio = self.tp(rawio, buffer_size=bufsize1)
        size = sys.getsizeof(bufio) - bufsize1
        rawio = self.MockRawIO()
        bufio = self.tp(rawio, buffer_size=bufsize2)
        self.assertEqual(sys.getsizeof(bufio), size + bufsize2)

    @support.cpython_only
    def test_buffer_freeing(self) :
        bufsize = 4096
        rawio = self.MockRawIO()
        bufio = self.tp(rawio, buffer_size=bufsize)
        size = sys.getsizeof(bufio) - bufsize
        bufio.close()
        self.assertEqual(sys.getsizeof(bufio), size)

klasa BufferedReaderTest(unittest.TestCase, CommonBufferedTests):
    read_mode = "rb"

    def test_constructor(self):
        rawio = self.MockRawIO([b"abc"])
        bufio = self.tp(rawio)
        bufio.__init__(rawio)
        bufio.__init__(rawio, buffer_size=1024)
        bufio.__init__(rawio, buffer_size=16)
        self.assertEqual(b"abc", bufio.read())
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=0)
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=-16)
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=-1)
        rawio = self.MockRawIO([b"abc"])
        bufio.__init__(rawio)
        self.assertEqual(b"abc", bufio.read())

    def test_uninitialized(self):
        bufio = self.tp.__new__(self.tp)
        usuń bufio
        bufio = self.tp.__new__(self.tp)
        self.assertRaisesRegex((ValueError, AttributeError),
                               'uninitialized|has no attribute',
                               bufio.read, 0)
        bufio.__init__(self.MockRawIO())
        self.assertEqual(bufio.read(0), b'')

    def test_read(self):
        dla arg w (Nic, 7):
            rawio = self.MockRawIO((b"abc", b"d", b"efg"))
            bufio = self.tp(rawio)
            self.assertEqual(b"abcdefg", bufio.read(arg))
        # Invalid args
        self.assertRaises(ValueError, bufio.read, -2)

    def test_read1(self):
        rawio = self.MockRawIO((b"abc", b"d", b"efg"))
        bufio = self.tp(rawio)
        self.assertEqual(b"a", bufio.read(1))
        self.assertEqual(b"b", bufio.read1(1))
        self.assertEqual(rawio._reads, 1)
        self.assertEqual(b"c", bufio.read1(100))
        self.assertEqual(rawio._reads, 1)
        self.assertEqual(b"d", bufio.read1(100))
        self.assertEqual(rawio._reads, 2)
        self.assertEqual(b"efg", bufio.read1(100))
        self.assertEqual(rawio._reads, 3)
        self.assertEqual(b"", bufio.read1(100))
        self.assertEqual(rawio._reads, 4)
        # Invalid args
        self.assertRaises(ValueError, bufio.read1, -1)

    def test_readinto(self):
        rawio = self.MockRawIO((b"abc", b"d", b"efg"))
        bufio = self.tp(rawio)
        b = bytearray(2)
        self.assertEqual(bufio.readinto(b), 2)
        self.assertEqual(b, b"ab")
        self.assertEqual(bufio.readinto(b), 2)
        self.assertEqual(b, b"cd")
        self.assertEqual(bufio.readinto(b), 2)
        self.assertEqual(b, b"ef")
        self.assertEqual(bufio.readinto(b), 1)
        self.assertEqual(b, b"gf")
        self.assertEqual(bufio.readinto(b), 0)
        self.assertEqual(b, b"gf")
        rawio = self.MockRawIO((b"abc", Nic))
        bufio = self.tp(rawio)
        self.assertEqual(bufio.readinto(b), 2)
        self.assertEqual(b, b"ab")
        self.assertEqual(bufio.readinto(b), 1)
        self.assertEqual(b, b"cb")

    def test_readinto1(self):
        buffer_size = 10
        rawio = self.MockRawIO((b"abc", b"de", b"fgh", b"jkl"))
        bufio = self.tp(rawio, buffer_size=buffer_size)
        b = bytearray(2)
        self.assertEqual(bufio.peek(3), b'abc')
        self.assertEqual(rawio._reads, 1)
        self.assertEqual(bufio.readinto1(b), 2)
        self.assertEqual(b, b"ab")
        self.assertEqual(rawio._reads, 1)
        self.assertEqual(bufio.readinto1(b), 1)
        self.assertEqual(b[:1], b"c")
        self.assertEqual(rawio._reads, 1)
        self.assertEqual(bufio.readinto1(b), 2)
        self.assertEqual(b, b"de")
        self.assertEqual(rawio._reads, 2)
        b = bytearray(2*buffer_size)
        self.assertEqual(bufio.peek(3), b'fgh')
        self.assertEqual(rawio._reads, 3)
        self.assertEqual(bufio.readinto1(b), 6)
        self.assertEqual(b[:6], b"fghjkl")
        self.assertEqual(rawio._reads, 4)

    def test_readinto_array(self):
        buffer_size = 60
        data = b"a" * 26
        rawio = self.MockRawIO((data,))
        bufio = self.tp(rawio, buffer_size=buffer_size)

        # Create an array przy element size > 1 byte
        b = array.array('i', b'x' * 32)
        assert len(b) != 16

        # Read into it. We should get jako many *bytes* jako we can fit into b
        # (which jest more than the number of elements)
        n = bufio.readinto(b)
        self.assertGreater(n, len(b))

        # Check that old contents of b are preserved
        bm = memoryview(b).cast('B')
        self.assertLess(n, len(bm))
        self.assertEqual(bm[:n], data[:n])
        self.assertEqual(bm[n:], b'x' * (len(bm[n:])))

    def test_readinto1_array(self):
        buffer_size = 60
        data = b"a" * 26
        rawio = self.MockRawIO((data,))
        bufio = self.tp(rawio, buffer_size=buffer_size)

        # Create an array przy element size > 1 byte
        b = array.array('i', b'x' * 32)
        assert len(b) != 16

        # Read into it. We should get jako many *bytes* jako we can fit into b
        # (which jest more than the number of elements)
        n = bufio.readinto1(b)
        self.assertGreater(n, len(b))

        # Check that old contents of b are preserved
        bm = memoryview(b).cast('B')
        self.assertLess(n, len(bm))
        self.assertEqual(bm[:n], data[:n])
        self.assertEqual(bm[n:], b'x' * (len(bm[n:])))

    def test_readlines(self):
        def bufio():
            rawio = self.MockRawIO((b"abc\n", b"d\n", b"ef"))
            zwróć self.tp(rawio)
        self.assertEqual(bufio().readlines(), [b"abc\n", b"d\n", b"ef"])
        self.assertEqual(bufio().readlines(5), [b"abc\n", b"d\n"])
        self.assertEqual(bufio().readlines(Nic), [b"abc\n", b"d\n", b"ef"])

    def test_buffering(self):
        data = b"abcdefghi"
        dlen = len(data)

        tests = [
            [ 100, [ 3, 1, 4, 8 ], [ dlen, 0 ] ],
            [ 100, [ 3, 3, 3],     [ dlen ]    ],
            [   4, [ 1, 2, 4, 2 ], [ 4, 4, 1 ] ],
        ]

        dla bufsize, buf_read_sizes, raw_read_sizes w tests:
            rawio = self.MockFileIO(data)
            bufio = self.tp(rawio, buffer_size=bufsize)
            pos = 0
            dla nbytes w buf_read_sizes:
                self.assertEqual(bufio.read(nbytes), data[pos:pos+nbytes])
                pos += nbytes
            # this jest mildly implementation-dependent
            self.assertEqual(rawio.read_history, raw_read_sizes)

    def test_read_non_blocking(self):
        # Inject some Nic's w there to simulate EWOULDBLOCK
        rawio = self.MockRawIO((b"abc", b"d", Nic, b"efg", Nic, Nic, Nic))
        bufio = self.tp(rawio)
        self.assertEqual(b"abcd", bufio.read(6))
        self.assertEqual(b"e", bufio.read(1))
        self.assertEqual(b"fg", bufio.read())
        self.assertEqual(b"", bufio.peek(1))
        self.assertIsNic(bufio.read())
        self.assertEqual(b"", bufio.read())

        rawio = self.MockRawIO((b"a", Nic, Nic))
        self.assertEqual(b"a", rawio.readall())
        self.assertIsNic(rawio.readall())

    def test_read_past_eof(self):
        rawio = self.MockRawIO((b"abc", b"d", b"efg"))
        bufio = self.tp(rawio)

        self.assertEqual(b"abcdefg", bufio.read(9000))

    def test_read_all(self):
        rawio = self.MockRawIO((b"abc", b"d", b"efg"))
        bufio = self.tp(rawio)

        self.assertEqual(b"abcdefg", bufio.read())

    @unittest.skipUnless(threading, 'Threading required dla this test.')
    @support.requires_resource('cpu')
    def test_threads(self):
        spróbuj:
            # Write out many bytes przy exactly the same number of 0's,
            # 1's... 255's. This will help us check that concurrent reading
            # doesn't duplicate albo forget contents.
            N = 1000
            l = list(range(256)) * N
            random.shuffle(l)
            s = bytes(bytearray(l))
            przy self.open(support.TESTFN, "wb") jako f:
                f.write(s)
            przy self.open(support.TESTFN, self.read_mode, buffering=0) jako raw:
                bufio = self.tp(raw, 8)
                errors = []
                results = []
                def f():
                    spróbuj:
                        # Intra-buffer read then buffer-flushing read
                        dla n w cycle([1, 19]):
                            s = bufio.read(n)
                            jeżeli nie s:
                                przerwij
                            # list.append() jest atomic
                            results.append(s)
                    wyjąwszy Exception jako e:
                        errors.append(e)
                        podnieś
                threads = [threading.Thread(target=f) dla x w range(20)]
                przy support.start_threads(threads):
                    time.sleep(0.02) # uzyskaj
                self.assertNieprawda(errors,
                    "the following exceptions were caught: %r" % errors)
                s = b''.join(results)
                dla i w range(256):
                    c = bytes(bytearray([i]))
                    self.assertEqual(s.count(c), N)
        w_końcu:
            support.unlink(support.TESTFN)

    def test_unseekable(self):
        bufio = self.tp(self.MockUnseekableIO(b"A" * 10))
        self.assertRaises(self.UnsupportedOperation, bufio.tell)
        self.assertRaises(self.UnsupportedOperation, bufio.seek, 0)
        bufio.read(1)
        self.assertRaises(self.UnsupportedOperation, bufio.seek, 0)
        self.assertRaises(self.UnsupportedOperation, bufio.tell)

    def test_misbehaved_io(self):
        rawio = self.MisbehavedRawIO((b"abc", b"d", b"efg"))
        bufio = self.tp(rawio)
        self.assertRaises(OSError, bufio.seek, 0)
        self.assertRaises(OSError, bufio.tell)

    def test_no_extraneous_read(self):
        # Issue #9550; when the raw IO object has satisfied the read request,
        # we should nie issue any additional reads, otherwise it may block
        # (e.g. socket).
        bufsize = 16
        dla n w (2, bufsize - 1, bufsize, bufsize + 1, bufsize * 2):
            rawio = self.MockRawIO([b"x" * n])
            bufio = self.tp(rawio, bufsize)
            self.assertEqual(bufio.read(n), b"x" * n)
            # Simple case: one raw read jest enough to satisfy the request.
            self.assertEqual(rawio._extraneous_reads, 0,
                             "failed dla {}: {} != 0".format(n, rawio._extraneous_reads))
            # A more complex case where two raw reads are needed to satisfy
            # the request.
            rawio = self.MockRawIO([b"x" * (n - 1), b"x"])
            bufio = self.tp(rawio, bufsize)
            self.assertEqual(bufio.read(n), b"x" * n)
            self.assertEqual(rawio._extraneous_reads, 0,
                             "failed dla {}: {} != 0".format(n, rawio._extraneous_reads))

    def test_read_on_closed(self):
        # Issue #23796
        b = io.BufferedReader(io.BytesIO(b"12"))
        b.read(1)
        b.close()
        self.assertRaises(ValueError, b.peek)
        self.assertRaises(ValueError, b.read1, 1)


klasa CBufferedReaderTest(BufferedReaderTest, SizeofTest):
    tp = io.BufferedReader

    def test_constructor(self):
        BufferedReaderTest.test_constructor(self)
        # The allocation can succeed on 32-bit builds, e.g. przy more
        # than 2GB RAM oraz a 64-bit kernel.
        jeżeli sys.maxsize > 0x7FFFFFFF:
            rawio = self.MockRawIO()
            bufio = self.tp(rawio)
            self.assertRaises((OverflowError, MemoryError, ValueError),
                bufio.__init__, rawio, sys.maxsize)

    def test_initialization(self):
        rawio = self.MockRawIO([b"abc"])
        bufio = self.tp(rawio)
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=0)
        self.assertRaises(ValueError, bufio.read)
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=-16)
        self.assertRaises(ValueError, bufio.read)
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=-1)
        self.assertRaises(ValueError, bufio.read)

    def test_misbehaved_io_read(self):
        rawio = self.MisbehavedRawIO((b"abc", b"d", b"efg"))
        bufio = self.tp(rawio)
        # _pyio.BufferedReader seems to implement reading different, so that
        # checking this jest nie so easy.
        self.assertRaises(OSError, bufio.read, 10)

    def test_garbage_collection(self):
        # C BufferedReader objects are collected.
        # The Python version has __del__, so it ends into gc.garbage instead
        przy support.check_warnings(('', ResourceWarning)):
            rawio = self.FileIO(support.TESTFN, "w+b")
            f = self.tp(rawio)
            f.f = f
            wr = weakref.ref(f)
            usuń f
            support.gc_collect()
        self.assertIsNic(wr(), wr)

    def test_args_error(self):
        # Issue #17275
        przy self.assertRaisesRegex(TypeError, "BufferedReader"):
            self.tp(io.BytesIO(), 1024, 1024, 1024)


klasa PyBufferedReaderTest(BufferedReaderTest):
    tp = pyio.BufferedReader


klasa BufferedWriterTest(unittest.TestCase, CommonBufferedTests):
    write_mode = "wb"

    def test_constructor(self):
        rawio = self.MockRawIO()
        bufio = self.tp(rawio)
        bufio.__init__(rawio)
        bufio.__init__(rawio, buffer_size=1024)
        bufio.__init__(rawio, buffer_size=16)
        self.assertEqual(3, bufio.write(b"abc"))
        bufio.flush()
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=0)
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=-16)
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=-1)
        bufio.__init__(rawio)
        self.assertEqual(3, bufio.write(b"ghi"))
        bufio.flush()
        self.assertEqual(b"".join(rawio._write_stack), b"abcghi")

    def test_uninitialized(self):
        bufio = self.tp.__new__(self.tp)
        usuń bufio
        bufio = self.tp.__new__(self.tp)
        self.assertRaisesRegex((ValueError, AttributeError),
                               'uninitialized|has no attribute',
                               bufio.write, b'')
        bufio.__init__(self.MockRawIO())
        self.assertEqual(bufio.write(b''), 0)

    def test_detach_flush(self):
        raw = self.MockRawIO()
        buf = self.tp(raw)
        buf.write(b"howdy!")
        self.assertNieprawda(raw._write_stack)
        buf.detach()
        self.assertEqual(raw._write_stack, [b"howdy!"])

    def test_write(self):
        # Write to the buffered IO but don't overflow the buffer.
        writer = self.MockRawIO()
        bufio = self.tp(writer, 8)
        bufio.write(b"abc")
        self.assertNieprawda(writer._write_stack)

    def test_write_overflow(self):
        writer = self.MockRawIO()
        bufio = self.tp(writer, 8)
        contents = b"abcdefghijklmnop"
        dla n w range(0, len(contents), 3):
            bufio.write(contents[n:n+3])
        flushed = b"".join(writer._write_stack)
        # At least (total - 8) bytes were implicitly flushed, perhaps more
        # depending on the implementation.
        self.assertPrawda(flushed.startswith(contents[:-8]), flushed)

    def check_writes(self, intermediate_func):
        # Lots of writes, test the flushed output jest jako expected.
        contents = bytes(range(256)) * 1000
        n = 0
        writer = self.MockRawIO()
        bufio = self.tp(writer, 13)
        # Generator of write sizes: repeat each N 15 times then proceed to N+1
        def gen_sizes():
            dla size w count(1):
                dla i w range(15):
                    uzyskaj size
        sizes = gen_sizes()
        dopóki n < len(contents):
            size = min(next(sizes), len(contents) - n)
            self.assertEqual(bufio.write(contents[n:n+size]), size)
            intermediate_func(bufio)
            n += size
        bufio.flush()
        self.assertEqual(contents, b"".join(writer._write_stack))

    def test_writes(self):
        self.check_writes(lambda bufio: Nic)

    def test_writes_and_flushes(self):
        self.check_writes(lambda bufio: bufio.flush())

    def test_writes_and_seeks(self):
        def _seekabs(bufio):
            pos = bufio.tell()
            bufio.seek(pos + 1, 0)
            bufio.seek(pos - 1, 0)
            bufio.seek(pos, 0)
        self.check_writes(_seekabs)
        def _seekrel(bufio):
            pos = bufio.seek(0, 1)
            bufio.seek(+1, 1)
            bufio.seek(-1, 1)
            bufio.seek(pos, 0)
        self.check_writes(_seekrel)

    def test_writes_and_truncates(self):
        self.check_writes(lambda bufio: bufio.truncate(bufio.tell()))

    def test_write_non_blocking(self):
        raw = self.MockNonBlockWriterIO()
        bufio = self.tp(raw, 8)

        self.assertEqual(bufio.write(b"abcd"), 4)
        self.assertEqual(bufio.write(b"efghi"), 5)
        # 1 byte will be written, the rest will be buffered
        raw.block_on(b"k")
        self.assertEqual(bufio.write(b"jklmn"), 5)

        # 8 bytes will be written, 8 will be buffered oraz the rest will be lost
        raw.block_on(b"0")
        spróbuj:
            bufio.write(b"opqrwxyz0123456789")
        wyjąwszy self.BlockingIOError jako e:
            written = e.characters_written
        inaczej:
            self.fail("BlockingIOError should have been podnieśd")
        self.assertEqual(written, 16)
        self.assertEqual(raw.pop_written(),
            b"abcdefghijklmnopqrwxyz")

        self.assertEqual(bufio.write(b"ABCDEFGHI"), 9)
        s = raw.pop_written()
        # Previously buffered bytes were flushed
        self.assertPrawda(s.startswith(b"01234567A"), s)

    def test_write_and_rewind(self):
        raw = io.BytesIO()
        bufio = self.tp(raw, 4)
        self.assertEqual(bufio.write(b"abcdef"), 6)
        self.assertEqual(bufio.tell(), 6)
        bufio.seek(0, 0)
        self.assertEqual(bufio.write(b"XY"), 2)
        bufio.seek(6, 0)
        self.assertEqual(raw.getvalue(), b"XYcdef")
        self.assertEqual(bufio.write(b"123456"), 6)
        bufio.flush()
        self.assertEqual(raw.getvalue(), b"XYcdef123456")

    def test_flush(self):
        writer = self.MockRawIO()
        bufio = self.tp(writer, 8)
        bufio.write(b"abc")
        bufio.flush()
        self.assertEqual(b"abc", writer._write_stack[0])

    def test_writelines(self):
        l = [b'ab', b'cd', b'ef']
        writer = self.MockRawIO()
        bufio = self.tp(writer, 8)
        bufio.writelines(l)
        bufio.flush()
        self.assertEqual(b''.join(writer._write_stack), b'abcdef')

    def test_writelines_userlist(self):
        l = UserList([b'ab', b'cd', b'ef'])
        writer = self.MockRawIO()
        bufio = self.tp(writer, 8)
        bufio.writelines(l)
        bufio.flush()
        self.assertEqual(b''.join(writer._write_stack), b'abcdef')

    def test_writelines_error(self):
        writer = self.MockRawIO()
        bufio = self.tp(writer, 8)
        self.assertRaises(TypeError, bufio.writelines, [1, 2, 3])
        self.assertRaises(TypeError, bufio.writelines, Nic)
        self.assertRaises(TypeError, bufio.writelines, 'abc')

    def test_destructor(self):
        writer = self.MockRawIO()
        bufio = self.tp(writer, 8)
        bufio.write(b"abc")
        usuń bufio
        support.gc_collect()
        self.assertEqual(b"abc", writer._write_stack[0])

    def test_truncate(self):
        # Truncate implicitly flushes the buffer.
        przy self.open(support.TESTFN, self.write_mode, buffering=0) jako raw:
            bufio = self.tp(raw, 8)
            bufio.write(b"abcdef")
            self.assertEqual(bufio.truncate(3), 3)
            self.assertEqual(bufio.tell(), 6)
        przy self.open(support.TESTFN, "rb", buffering=0) jako f:
            self.assertEqual(f.read(), b"abc")

    @unittest.skipUnless(threading, 'Threading required dla this test.')
    @support.requires_resource('cpu')
    def test_threads(self):
        spróbuj:
            # Write out many bytes z many threads oraz test they were
            # all flushed.
            N = 1000
            contents = bytes(range(256)) * N
            sizes = cycle([1, 19])
            n = 0
            queue = deque()
            dopóki n < len(contents):
                size = next(sizes)
                queue.append(contents[n:n+size])
                n += size
            usuń contents
            # We use a real file object because it allows us to
            # exercise situations where the GIL jest released before
            # writing the buffer to the raw streams. This jest w addition
            # to concurrency issues due to switching threads w the middle
            # of Python code.
            przy self.open(support.TESTFN, self.write_mode, buffering=0) jako raw:
                bufio = self.tp(raw, 8)
                errors = []
                def f():
                    spróbuj:
                        dopóki Prawda:
                            spróbuj:
                                s = queue.popleft()
                            wyjąwszy IndexError:
                                zwróć
                            bufio.write(s)
                    wyjąwszy Exception jako e:
                        errors.append(e)
                        podnieś
                threads = [threading.Thread(target=f) dla x w range(20)]
                przy support.start_threads(threads):
                    time.sleep(0.02) # uzyskaj
                self.assertNieprawda(errors,
                    "the following exceptions were caught: %r" % errors)
                bufio.close()
            przy self.open(support.TESTFN, "rb") jako f:
                s = f.read()
            dla i w range(256):
                self.assertEqual(s.count(bytes([i])), N)
        w_końcu:
            support.unlink(support.TESTFN)

    def test_misbehaved_io(self):
        rawio = self.MisbehavedRawIO()
        bufio = self.tp(rawio, 5)
        self.assertRaises(OSError, bufio.seek, 0)
        self.assertRaises(OSError, bufio.tell)
        self.assertRaises(OSError, bufio.write, b"abcdef")

    def test_max_buffer_size_removal(self):
        przy self.assertRaises(TypeError):
            self.tp(self.MockRawIO(), 8, 12)

    def test_write_error_on_close(self):
        raw = self.MockRawIO()
        def bad_write(b):
            podnieś OSError()
        raw.write = bad_write
        b = self.tp(raw)
        b.write(b'spam')
        self.assertRaises(OSError, b.close) # exception nie swallowed
        self.assertPrawda(b.closed)


klasa CBufferedWriterTest(BufferedWriterTest, SizeofTest):
    tp = io.BufferedWriter

    def test_constructor(self):
        BufferedWriterTest.test_constructor(self)
        # The allocation can succeed on 32-bit builds, e.g. przy more
        # than 2GB RAM oraz a 64-bit kernel.
        jeżeli sys.maxsize > 0x7FFFFFFF:
            rawio = self.MockRawIO()
            bufio = self.tp(rawio)
            self.assertRaises((OverflowError, MemoryError, ValueError),
                bufio.__init__, rawio, sys.maxsize)

    def test_initialization(self):
        rawio = self.MockRawIO()
        bufio = self.tp(rawio)
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=0)
        self.assertRaises(ValueError, bufio.write, b"def")
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=-16)
        self.assertRaises(ValueError, bufio.write, b"def")
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=-1)
        self.assertRaises(ValueError, bufio.write, b"def")

    def test_garbage_collection(self):
        # C BufferedWriter objects are collected, oraz collecting them flushes
        # all data to disk.
        # The Python version has __del__, so it ends into gc.garbage instead
        przy support.check_warnings(('', ResourceWarning)):
            rawio = self.FileIO(support.TESTFN, "w+b")
            f = self.tp(rawio)
            f.write(b"123xxx")
            f.x = f
            wr = weakref.ref(f)
            usuń f
            support.gc_collect()
        self.assertIsNic(wr(), wr)
        przy self.open(support.TESTFN, "rb") jako f:
            self.assertEqual(f.read(), b"123xxx")

    def test_args_error(self):
        # Issue #17275
        przy self.assertRaisesRegex(TypeError, "BufferedWriter"):
            self.tp(io.BytesIO(), 1024, 1024, 1024)


klasa PyBufferedWriterTest(BufferedWriterTest):
    tp = pyio.BufferedWriter

klasa BufferedRWPairTest(unittest.TestCase):

    def test_constructor(self):
        pair = self.tp(self.MockRawIO(), self.MockRawIO())
        self.assertNieprawda(pair.closed)

    def test_uninitialized(self):
        pair = self.tp.__new__(self.tp)
        usuń pair
        pair = self.tp.__new__(self.tp)
        self.assertRaisesRegex((ValueError, AttributeError),
                               'uninitialized|has no attribute',
                               pair.read, 0)
        self.assertRaisesRegex((ValueError, AttributeError),
                               'uninitialized|has no attribute',
                               pair.write, b'')
        pair.__init__(self.MockRawIO(), self.MockRawIO())
        self.assertEqual(pair.read(0), b'')
        self.assertEqual(pair.write(b''), 0)

    def test_detach(self):
        pair = self.tp(self.MockRawIO(), self.MockRawIO())
        self.assertRaises(self.UnsupportedOperation, pair.detach)

    def test_constructor_max_buffer_size_removal(self):
        przy self.assertRaises(TypeError):
            self.tp(self.MockRawIO(), self.MockRawIO(), 8, 12)

    def test_constructor_with_not_readable(self):
        klasa NotReadable(MockRawIO):
            def readable(self):
                zwróć Nieprawda

        self.assertRaises(OSError, self.tp, NotReadable(), self.MockRawIO())

    def test_constructor_with_not_writeable(self):
        klasa NotWriteable(MockRawIO):
            def writable(self):
                zwróć Nieprawda

        self.assertRaises(OSError, self.tp, self.MockRawIO(), NotWriteable())

    def test_read(self):
        pair = self.tp(self.BytesIO(b"abcdef"), self.MockRawIO())

        self.assertEqual(pair.read(3), b"abc")
        self.assertEqual(pair.read(1), b"d")
        self.assertEqual(pair.read(), b"ef")
        pair = self.tp(self.BytesIO(b"abc"), self.MockRawIO())
        self.assertEqual(pair.read(Nic), b"abc")

    def test_readlines(self):
        pair = lambda: self.tp(self.BytesIO(b"abc\ndef\nh"), self.MockRawIO())
        self.assertEqual(pair().readlines(), [b"abc\n", b"def\n", b"h"])
        self.assertEqual(pair().readlines(), [b"abc\n", b"def\n", b"h"])
        self.assertEqual(pair().readlines(5), [b"abc\n", b"def\n"])

    def test_read1(self):
        # .read1() jest delegated to the underlying reader object, so this test
        # can be shallow.
        pair = self.tp(self.BytesIO(b"abcdef"), self.MockRawIO())

        self.assertEqual(pair.read1(3), b"abc")

    def test_readinto(self):
        pair = self.tp(self.BytesIO(b"abcdef"), self.MockRawIO())

        data = bytearray(5)
        self.assertEqual(pair.readinto(data), 5)
        self.assertEqual(data, b"abcde")

    def test_write(self):
        w = self.MockRawIO()
        pair = self.tp(self.MockRawIO(), w)

        pair.write(b"abc")
        pair.flush()
        pair.write(b"def")
        pair.flush()
        self.assertEqual(w._write_stack, [b"abc", b"def"])

    def test_peek(self):
        pair = self.tp(self.BytesIO(b"abcdef"), self.MockRawIO())

        self.assertPrawda(pair.peek(3).startswith(b"abc"))
        self.assertEqual(pair.read(3), b"abc")

    def test_readable(self):
        pair = self.tp(self.MockRawIO(), self.MockRawIO())
        self.assertPrawda(pair.readable())

    def test_writeable(self):
        pair = self.tp(self.MockRawIO(), self.MockRawIO())
        self.assertPrawda(pair.writable())

    def test_seekable(self):
        # BufferedRWPairs are never seekable, even jeżeli their readers oraz writers
        # are.
        pair = self.tp(self.MockRawIO(), self.MockRawIO())
        self.assertNieprawda(pair.seekable())

    # .flush() jest delegated to the underlying writer object oraz has been
    # tested w the test_write method.

    def test_close_and_closed(self):
        pair = self.tp(self.MockRawIO(), self.MockRawIO())
        self.assertNieprawda(pair.closed)
        pair.close()
        self.assertPrawda(pair.closed)

    def test_reader_close_error_on_close(self):
        def reader_close():
            reader_non_existing
        reader = self.MockRawIO()
        reader.close = reader_close
        writer = self.MockRawIO()
        pair = self.tp(reader, writer)
        przy self.assertRaises(NameError) jako err:
            pair.close()
        self.assertIn('reader_non_existing', str(err.exception))
        self.assertPrawda(pair.closed)
        self.assertNieprawda(reader.closed)
        self.assertPrawda(writer.closed)

    def test_writer_close_error_on_close(self):
        def writer_close():
            writer_non_existing
        reader = self.MockRawIO()
        writer = self.MockRawIO()
        writer.close = writer_close
        pair = self.tp(reader, writer)
        przy self.assertRaises(NameError) jako err:
            pair.close()
        self.assertIn('writer_non_existing', str(err.exception))
        self.assertNieprawda(pair.closed)
        self.assertPrawda(reader.closed)
        self.assertNieprawda(writer.closed)

    def test_reader_writer_close_error_on_close(self):
        def reader_close():
            reader_non_existing
        def writer_close():
            writer_non_existing
        reader = self.MockRawIO()
        reader.close = reader_close
        writer = self.MockRawIO()
        writer.close = writer_close
        pair = self.tp(reader, writer)
        przy self.assertRaises(NameError) jako err:
            pair.close()
        self.assertIn('reader_non_existing', str(err.exception))
        self.assertIsInstance(err.exception.__context__, NameError)
        self.assertIn('writer_non_existing', str(err.exception.__context__))
        self.assertNieprawda(pair.closed)
        self.assertNieprawda(reader.closed)
        self.assertNieprawda(writer.closed)

    def test_isatty(self):
        klasa SelectableIsAtty(MockRawIO):
            def __init__(self, isatty):
                MockRawIO.__init__(self)
                self._isatty = isatty

            def isatty(self):
                zwróć self._isatty

        pair = self.tp(SelectableIsAtty(Nieprawda), SelectableIsAtty(Nieprawda))
        self.assertNieprawda(pair.isatty())

        pair = self.tp(SelectableIsAtty(Prawda), SelectableIsAtty(Nieprawda))
        self.assertPrawda(pair.isatty())

        pair = self.tp(SelectableIsAtty(Nieprawda), SelectableIsAtty(Prawda))
        self.assertPrawda(pair.isatty())

        pair = self.tp(SelectableIsAtty(Prawda), SelectableIsAtty(Prawda))
        self.assertPrawda(pair.isatty())

    def test_weakref_clearing(self):
        brw = self.tp(self.MockRawIO(), self.MockRawIO())
        ref = weakref.ref(brw)
        brw = Nic
        ref = Nic # Shouldn't segfault.

klasa CBufferedRWPairTest(BufferedRWPairTest):
    tp = io.BufferedRWPair

klasa PyBufferedRWPairTest(BufferedRWPairTest):
    tp = pyio.BufferedRWPair


klasa BufferedRandomTest(BufferedReaderTest, BufferedWriterTest):
    read_mode = "rb+"
    write_mode = "wb+"

    def test_constructor(self):
        BufferedReaderTest.test_constructor(self)
        BufferedWriterTest.test_constructor(self)

    def test_uninitialized(self):
        BufferedReaderTest.test_uninitialized(self)
        BufferedWriterTest.test_uninitialized(self)

    def test_read_and_write(self):
        raw = self.MockRawIO((b"asdf", b"ghjk"))
        rw = self.tp(raw, 8)

        self.assertEqual(b"as", rw.read(2))
        rw.write(b"ddd")
        rw.write(b"eee")
        self.assertNieprawda(raw._write_stack) # Buffer writes
        self.assertEqual(b"ghjk", rw.read())
        self.assertEqual(b"dddeee", raw._write_stack[0])

    def test_seek_and_tell(self):
        raw = self.BytesIO(b"asdfghjkl")
        rw = self.tp(raw)

        self.assertEqual(b"as", rw.read(2))
        self.assertEqual(2, rw.tell())
        rw.seek(0, 0)
        self.assertEqual(b"asdf", rw.read(4))

        rw.write(b"123f")
        rw.seek(0, 0)
        self.assertEqual(b"asdf123fl", rw.read())
        self.assertEqual(9, rw.tell())
        rw.seek(-4, 2)
        self.assertEqual(5, rw.tell())
        rw.seek(2, 1)
        self.assertEqual(7, rw.tell())
        self.assertEqual(b"fl", rw.read(11))
        rw.flush()
        self.assertEqual(b"asdf123fl", raw.getvalue())

        self.assertRaises(TypeError, rw.seek, 0.0)

    def check_flush_and_read(self, read_func):
        raw = self.BytesIO(b"abcdefghi")
        bufio = self.tp(raw)

        self.assertEqual(b"ab", read_func(bufio, 2))
        bufio.write(b"12")
        self.assertEqual(b"ef", read_func(bufio, 2))
        self.assertEqual(6, bufio.tell())
        bufio.flush()
        self.assertEqual(6, bufio.tell())
        self.assertEqual(b"ghi", read_func(bufio))
        raw.seek(0, 0)
        raw.write(b"XYZ")
        # flush() resets the read buffer
        bufio.flush()
        bufio.seek(0, 0)
        self.assertEqual(b"XYZ", read_func(bufio, 3))

    def test_flush_and_read(self):
        self.check_flush_and_read(lambda bufio, *args: bufio.read(*args))

    def test_flush_and_readinto(self):
        def _readinto(bufio, n=-1):
            b = bytearray(n jeżeli n >= 0 inaczej 9999)
            n = bufio.readinto(b)
            zwróć bytes(b[:n])
        self.check_flush_and_read(_readinto)

    def test_flush_and_peek(self):
        def _peek(bufio, n=-1):
            # This relies on the fact that the buffer can contain the whole
            # raw stream, otherwise peek() can zwróć less.
            b = bufio.peek(n)
            jeżeli n != -1:
                b = b[:n]
            bufio.seek(len(b), 1)
            zwróć b
        self.check_flush_and_read(_peek)

    def test_flush_and_write(self):
        raw = self.BytesIO(b"abcdefghi")
        bufio = self.tp(raw)

        bufio.write(b"123")
        bufio.flush()
        bufio.write(b"45")
        bufio.flush()
        bufio.seek(0, 0)
        self.assertEqual(b"12345fghi", raw.getvalue())
        self.assertEqual(b"12345fghi", bufio.read())

    def test_threads(self):
        BufferedReaderTest.test_threads(self)
        BufferedWriterTest.test_threads(self)

    def test_writes_and_peek(self):
        def _peek(bufio):
            bufio.peek(1)
        self.check_writes(_peek)
        def _peek(bufio):
            pos = bufio.tell()
            bufio.seek(-1, 1)
            bufio.peek(1)
            bufio.seek(pos, 0)
        self.check_writes(_peek)

    def test_writes_and_reads(self):
        def _read(bufio):
            bufio.seek(-1, 1)
            bufio.read(1)
        self.check_writes(_read)

    def test_writes_and_read1s(self):
        def _read1(bufio):
            bufio.seek(-1, 1)
            bufio.read1(1)
        self.check_writes(_read1)

    def test_writes_and_readintos(self):
        def _read(bufio):
            bufio.seek(-1, 1)
            bufio.readinto(bytearray(1))
        self.check_writes(_read)

    def test_write_after_readahead(self):
        # Issue #6629: writing after the buffer was filled by readahead should
        # first rewind the raw stream.
        dla overwrite_size w [1, 5]:
            raw = self.BytesIO(b"A" * 10)
            bufio = self.tp(raw, 4)
            # Trigger readahead
            self.assertEqual(bufio.read(1), b"A")
            self.assertEqual(bufio.tell(), 1)
            # Overwriting should rewind the raw stream jeżeli it needs so
            bufio.write(b"B" * overwrite_size)
            self.assertEqual(bufio.tell(), overwrite_size + 1)
            # If the write size was smaller than the buffer size, flush() oraz
            # check that rewind happens.
            bufio.flush()
            self.assertEqual(bufio.tell(), overwrite_size + 1)
            s = raw.getvalue()
            self.assertEqual(s,
                b"A" + b"B" * overwrite_size + b"A" * (9 - overwrite_size))

    def test_write_rewind_write(self):
        # Various combinations of reading / writing / seeking backwards / writing again
        def mutate(bufio, pos1, pos2):
            assert pos2 >= pos1
            # Fill the buffer
            bufio.seek(pos1)
            bufio.read(pos2 - pos1)
            bufio.write(b'\x02')
            # This writes earlier than the previous write, but still inside
            # the buffer.
            bufio.seek(pos1)
            bufio.write(b'\x01')

        b = b"\x80\x81\x82\x83\x84"
        dla i w range(0, len(b)):
            dla j w range(i, len(b)):
                raw = self.BytesIO(b)
                bufio = self.tp(raw, 100)
                mutate(bufio, i, j)
                bufio.flush()
                expected = bytearray(b)
                expected[j] = 2
                expected[i] = 1
                self.assertEqual(raw.getvalue(), expected,
                                 "failed result dla i=%d, j=%d" % (i, j))

    def test_truncate_after_read_or_write(self):
        raw = self.BytesIO(b"A" * 10)
        bufio = self.tp(raw, 100)
        self.assertEqual(bufio.read(2), b"AA") # the read buffer gets filled
        self.assertEqual(bufio.truncate(), 2)
        self.assertEqual(bufio.write(b"BB"), 2) # the write buffer increases
        self.assertEqual(bufio.truncate(), 4)

    def test_misbehaved_io(self):
        BufferedReaderTest.test_misbehaved_io(self)
        BufferedWriterTest.test_misbehaved_io(self)

    def test_interleaved_read_write(self):
        # Test dla issue #12213
        przy self.BytesIO(b'abcdefgh') jako raw:
            przy self.tp(raw, 100) jako f:
                f.write(b"1")
                self.assertEqual(f.read(1), b'b')
                f.write(b'2')
                self.assertEqual(f.read1(1), b'd')
                f.write(b'3')
                buf = bytearray(1)
                f.readinto(buf)
                self.assertEqual(buf, b'f')
                f.write(b'4')
                self.assertEqual(f.peek(1), b'h')
                f.flush()
                self.assertEqual(raw.getvalue(), b'1b2d3f4h')

        przy self.BytesIO(b'abc') jako raw:
            przy self.tp(raw, 100) jako f:
                self.assertEqual(f.read(1), b'a')
                f.write(b"2")
                self.assertEqual(f.read(1), b'c')
                f.flush()
                self.assertEqual(raw.getvalue(), b'a2c')

    def test_interleaved_readline_write(self):
        przy self.BytesIO(b'ab\ncdef\ng\n') jako raw:
            przy self.tp(raw) jako f:
                f.write(b'1')
                self.assertEqual(f.readline(), b'b\n')
                f.write(b'2')
                self.assertEqual(f.readline(), b'def\n')
                f.write(b'3')
                self.assertEqual(f.readline(), b'\n')
                f.flush()
                self.assertEqual(raw.getvalue(), b'1b\n2def\n3\n')

    # You can't construct a BufferedRandom over a non-seekable stream.
    test_unseekable = Nic


klasa CBufferedRandomTest(BufferedRandomTest, SizeofTest):
    tp = io.BufferedRandom

    def test_constructor(self):
        BufferedRandomTest.test_constructor(self)
        # The allocation can succeed on 32-bit builds, e.g. przy more
        # than 2GB RAM oraz a 64-bit kernel.
        jeżeli sys.maxsize > 0x7FFFFFFF:
            rawio = self.MockRawIO()
            bufio = self.tp(rawio)
            self.assertRaises((OverflowError, MemoryError, ValueError),
                bufio.__init__, rawio, sys.maxsize)

    def test_garbage_collection(self):
        CBufferedReaderTest.test_garbage_collection(self)
        CBufferedWriterTest.test_garbage_collection(self)

    def test_args_error(self):
        # Issue #17275
        przy self.assertRaisesRegex(TypeError, "BufferedRandom"):
            self.tp(io.BytesIO(), 1024, 1024, 1024)


klasa PyBufferedRandomTest(BufferedRandomTest):
    tp = pyio.BufferedRandom


# To fully exercise seek/tell, the StatefulIncrementalDecoder has these
# properties:
#   - A single output character can correspond to many bytes of input.
#   - The number of input bytes to complete the character can be
#     undetermined until the last input byte jest received.
#   - The number of input bytes can vary depending on previous input.
#   - A single input byte can correspond to many characters of output.
#   - The number of output characters can be undetermined until the
#     last input byte jest received.
#   - The number of output characters can vary depending on previous input.

klasa StatefulIncrementalDecoder(codecs.IncrementalDecoder):
    """
    For testing seek/tell behavior przy a stateful, buffering decoder.

    Input jest a sequence of words.  Words may be fixed-length (length set
    by input) albo variable-length (period-terminated).  In variable-length
    mode, extra periods are ignored.  Possible words are:
      - 'i' followed by a number sets the input length, I (maximum 99).
        When I jest set to 0, words are space-terminated.
      - 'o' followed by a number sets the output length, O (maximum 99).
      - Any other word jest converted into a word followed by a period on
        the output.  The output word consists of the input word truncated
        albo padded out przy hyphens to make its length equal to O.  If O
        jest 0, the word jest output verbatim without truncating albo padding.
    I oraz O are initially set to 1.  When I changes, any buffered input jest
    re-scanned according to the new I.  EOF also terminates the last word.
    """

    def __init__(self, errors='strict'):
        codecs.IncrementalDecoder.__init__(self, errors)
        self.reset()

    def __repr__(self):
        zwróć '<SID %x>' % id(self)

    def reset(self):
        self.i = 1
        self.o = 1
        self.buffer = bytearray()

    def getstate(self):
        i, o = self.i ^ 1, self.o ^ 1 # so that flags = 0 after reset()
        zwróć bytes(self.buffer), i*100 + o

    def setstate(self, state):
        buffer, io = state
        self.buffer = bytearray(buffer)
        i, o = divmod(io, 100)
        self.i, self.o = i ^ 1, o ^ 1

    def decode(self, input, final=Nieprawda):
        output = ''
        dla b w input:
            jeżeli self.i == 0: # variable-length, terminated przy period
                jeżeli b == ord('.'):
                    jeżeli self.buffer:
                        output += self.process_word()
                inaczej:
                    self.buffer.append(b)
            inaczej: # fixed-length, terminate after self.i bytes
                self.buffer.append(b)
                jeżeli len(self.buffer) == self.i:
                    output += self.process_word()
        jeżeli final oraz self.buffer: # EOF terminates the last word
            output += self.process_word()
        zwróć output

    def process_word(self):
        output = ''
        jeżeli self.buffer[0] == ord('i'):
            self.i = min(99, int(self.buffer[1:] albo 0)) # set input length
        albo_inaczej self.buffer[0] == ord('o'):
            self.o = min(99, int(self.buffer[1:] albo 0)) # set output length
        inaczej:
            output = self.buffer.decode('ascii')
            jeżeli len(output) < self.o:
                output += '-'*self.o # pad out przy hyphens
            jeżeli self.o:
                output = output[:self.o] # truncate to output length
            output += '.'
        self.buffer = bytearray()
        zwróć output

    codecEnabled = Nieprawda

    @classmethod
    def lookupTestDecoder(cls, name):
        jeżeli cls.codecEnabled oraz name == 'test_decoder':
            latin1 = codecs.lookup('latin-1')
            zwróć codecs.CodecInfo(
                name='test_decoder', encode=latin1.encode, decode=Nic,
                incrementalencoder=Nic,
                streamreader=Nic, streamwriter=Nic,
                incrementaldecoder=cls)

# Register the previous decoder dla testing.
# Disabled by default, tests will enable it.
codecs.register(StatefulIncrementalDecoder.lookupTestDecoder)


klasa StatefulIncrementalDecoderTest(unittest.TestCase):
    """
    Make sure the StatefulIncrementalDecoder actually works.
    """

    test_cases = [
        # I=1, O=1 (fixed-length input == fixed-length output)
        (b'abcd', Nieprawda, 'a.b.c.d.'),
        # I=0, O=0 (variable-length input, variable-length output)
        (b'oiabcd', Prawda, 'abcd.'),
        # I=0, O=0 (should ignore extra periods)
        (b'oi...abcd...', Prawda, 'abcd.'),
        # I=0, O=6 (variable-length input, fixed-length output)
        (b'i.o6.x.xyz.toolongtofit.', Nieprawda, 'x-----.xyz---.toolon.'),
        # I=2, O=6 (fixed-length input < fixed-length output)
        (b'i.i2.o6xyz', Prawda, 'xy----.z-----.'),
        # I=6, O=3 (fixed-length input > fixed-length output)
        (b'i.o3.i6.abcdefghijklmnop', Prawda, 'abc.ghi.mno.'),
        # I=0, then 3; O=29, then 15 (przy longer output)
        (b'i.o29.a.b.cde.o15.abcdefghijabcdefghij.i3.a.b.c.d.ei00k.l.m', Prawda,
         'a----------------------------.' +
         'b----------------------------.' +
         'cde--------------------------.' +
         'abcdefghijabcde.' +
         'a.b------------.' +
         '.c.------------.' +
         'd.e------------.' +
         'k--------------.' +
         'l--------------.' +
         'm--------------.')
    ]

    def test_decoder(self):
        # Try a few one-shot test cases.
        dla input, eof, output w self.test_cases:
            d = StatefulIncrementalDecoder()
            self.assertEqual(d.decode(input, eof), output)

        # Also test an unfinished decode, followed by forcing EOF.
        d = StatefulIncrementalDecoder()
        self.assertEqual(d.decode(b'oiabcd'), '')
        self.assertEqual(d.decode(b'', 1), 'abcd.')

klasa TextIOWrapperTest(unittest.TestCase):

    def setUp(self):
        self.testdata = b"AAA\r\nBBB\rCCC\r\nDDD\nEEE\r\n"
        self.normalized = b"AAA\nBBB\nCCC\nDDD\nEEE\n".decode("ascii")
        support.unlink(support.TESTFN)

    def tearDown(self):
        support.unlink(support.TESTFN)

    def test_constructor(self):
        r = self.BytesIO(b"\xc3\xa9\n\n")
        b = self.BufferedReader(r, 1000)
        t = self.TextIOWrapper(b)
        t.__init__(b, encoding="latin-1", newline="\r\n")
        self.assertEqual(t.encoding, "latin-1")
        self.assertEqual(t.line_buffering, Nieprawda)
        t.__init__(b, encoding="utf-8", line_buffering=Prawda)
        self.assertEqual(t.encoding, "utf-8")
        self.assertEqual(t.line_buffering, Prawda)
        self.assertEqual("\xe9\n", t.readline())
        self.assertRaises(TypeError, t.__init__, b, newline=42)
        self.assertRaises(ValueError, t.__init__, b, newline='xyzzy')

    def test_uninitialized(self):
        t = self.TextIOWrapper.__new__(self.TextIOWrapper)
        usuń t
        t = self.TextIOWrapper.__new__(self.TextIOWrapper)
        self.assertRaises(Exception, repr, t)
        self.assertRaisesRegex((ValueError, AttributeError),
                               'uninitialized|has no attribute',
                               t.read, 0)
        t.__init__(self.MockRawIO())
        self.assertEqual(t.read(0), '')

    def test_non_text_encoding_codecs_are_rejected(self):
        # Ensure the constructor complains jeżeli dalejed a codec that isn't
        # marked jako a text encoding
        # http://bugs.python.org/issue20404
        r = self.BytesIO()
        b = self.BufferedWriter(r)
        przy self.assertRaisesRegex(LookupError, "is nie a text encoding"):
            self.TextIOWrapper(b, encoding="hex")

    def test_detach(self):
        r = self.BytesIO()
        b = self.BufferedWriter(r)
        t = self.TextIOWrapper(b)
        self.assertIs(t.detach(), b)

        t = self.TextIOWrapper(b, encoding="ascii")
        t.write("howdy")
        self.assertNieprawda(r.getvalue())
        t.detach()
        self.assertEqual(r.getvalue(), b"howdy")
        self.assertRaises(ValueError, t.detach)

        # Operations independent of the detached stream should still work
        repr(t)
        self.assertEqual(t.encoding, "ascii")
        self.assertEqual(t.errors, "strict")
        self.assertNieprawda(t.line_buffering)

    def test_repr(self):
        raw = self.BytesIO("hello".encode("utf-8"))
        b = self.BufferedReader(raw)
        t = self.TextIOWrapper(b, encoding="utf-8")
        modname = self.TextIOWrapper.__module__
        self.assertEqual(repr(t),
                         "<%s.TextIOWrapper encoding='utf-8'>" % modname)
        raw.name = "dummy"
        self.assertEqual(repr(t),
                         "<%s.TextIOWrapper name='dummy' encoding='utf-8'>" % modname)
        t.mode = "r"
        self.assertEqual(repr(t),
                         "<%s.TextIOWrapper name='dummy' mode='r' encoding='utf-8'>" % modname)
        raw.name = b"dummy"
        self.assertEqual(repr(t),
                         "<%s.TextIOWrapper name=b'dummy' mode='r' encoding='utf-8'>" % modname)

        t.buffer.detach()
        repr(t)  # Should nie podnieś an exception

    def test_line_buffering(self):
        r = self.BytesIO()
        b = self.BufferedWriter(r, 1000)
        t = self.TextIOWrapper(b, newline="\n", line_buffering=Prawda)
        t.write("X")
        self.assertEqual(r.getvalue(), b"")  # No flush happened
        t.write("Y\nZ")
        self.assertEqual(r.getvalue(), b"XY\nZ")  # All got flushed
        t.write("A\rB")
        self.assertEqual(r.getvalue(), b"XY\nZA\rB")

    def test_default_encoding(self):
        old_environ = dict(os.environ)
        spróbuj:
            # try to get a user preferred encoding different than the current
            # locale encoding to check that TextIOWrapper() uses the current
            # locale encoding oraz nie the user preferred encoding
            dla key w ('LC_ALL', 'LANG', 'LC_CTYPE'):
                jeżeli key w os.environ:
                    usuń os.environ[key]

            current_locale_encoding = locale.getpreferredencoding(Nieprawda)
            b = self.BytesIO()
            t = self.TextIOWrapper(b)
            self.assertEqual(t.encoding, current_locale_encoding)
        w_końcu:
            os.environ.clear()
            os.environ.update(old_environ)

    @support.cpython_only
    def test_device_encoding(self):
        # Issue 15989
        zaimportuj _testcapi
        b = self.BytesIO()
        b.fileno = lambda: _testcapi.INT_MAX + 1
        self.assertRaises(OverflowError, self.TextIOWrapper, b)
        b.fileno = lambda: _testcapi.UINT_MAX + 1
        self.assertRaises(OverflowError, self.TextIOWrapper, b)

    def test_encoding(self):
        # Check the encoding attribute jest always set, oraz valid
        b = self.BytesIO()
        t = self.TextIOWrapper(b, encoding="utf-8")
        self.assertEqual(t.encoding, "utf-8")
        t = self.TextIOWrapper(b)
        self.assertIsNotNic(t.encoding)
        codecs.lookup(t.encoding)

    def test_encoding_errors_reading(self):
        # (1) default
        b = self.BytesIO(b"abc\n\xff\n")
        t = self.TextIOWrapper(b, encoding="ascii")
        self.assertRaises(UnicodeError, t.read)
        # (2) explicit strict
        b = self.BytesIO(b"abc\n\xff\n")
        t = self.TextIOWrapper(b, encoding="ascii", errors="strict")
        self.assertRaises(UnicodeError, t.read)
        # (3) ignore
        b = self.BytesIO(b"abc\n\xff\n")
        t = self.TextIOWrapper(b, encoding="ascii", errors="ignore")
        self.assertEqual(t.read(), "abc\n\n")
        # (4) replace
        b = self.BytesIO(b"abc\n\xff\n")
        t = self.TextIOWrapper(b, encoding="ascii", errors="replace")
        self.assertEqual(t.read(), "abc\n\ufffd\n")

    def test_encoding_errors_writing(self):
        # (1) default
        b = self.BytesIO()
        t = self.TextIOWrapper(b, encoding="ascii")
        self.assertRaises(UnicodeError, t.write, "\xff")
        # (2) explicit strict
        b = self.BytesIO()
        t = self.TextIOWrapper(b, encoding="ascii", errors="strict")
        self.assertRaises(UnicodeError, t.write, "\xff")
        # (3) ignore
        b = self.BytesIO()
        t = self.TextIOWrapper(b, encoding="ascii", errors="ignore",
                             newline="\n")
        t.write("abc\xffdef\n")
        t.flush()
        self.assertEqual(b.getvalue(), b"abcdef\n")
        # (4) replace
        b = self.BytesIO()
        t = self.TextIOWrapper(b, encoding="ascii", errors="replace",
                             newline="\n")
        t.write("abc\xffdef\n")
        t.flush()
        self.assertEqual(b.getvalue(), b"abc?def\n")

    def test_newlines(self):
        input_lines = [ "unix\n", "windows\r\n", "os9\r", "last\n", "nonl" ]

        tests = [
            [ Nic, [ 'unix\n', 'windows\n', 'os9\n', 'last\n', 'nonl' ] ],
            [ '', input_lines ],
            [ '\n', [ "unix\n", "windows\r\n", "os9\rlast\n", "nonl" ] ],
            [ '\r\n', [ "unix\nwindows\r\n", "os9\rlast\nnonl" ] ],
            [ '\r', [ "unix\nwindows\r", "\nos9\r", "last\nnonl" ] ],
        ]
        encodings = (
            'utf-8', 'latin-1',
            'utf-16', 'utf-16-le', 'utf-16-be',
            'utf-32', 'utf-32-le', 'utf-32-be',
        )

        # Try a range of buffer sizes to test the case where \r jest the last
        # character w TextIOWrapper._pending_line.
        dla encoding w encodings:
            # XXX: str.encode() should zwróć bytes
            data = bytes(''.join(input_lines).encode(encoding))
            dla do_reads w (Nieprawda, Prawda):
                dla bufsize w range(1, 10):
                    dla newline, exp_lines w tests:
                        bufio = self.BufferedReader(self.BytesIO(data), bufsize)
                        textio = self.TextIOWrapper(bufio, newline=newline,
                                                  encoding=encoding)
                        jeżeli do_reads:
                            got_lines = []
                            dopóki Prawda:
                                c2 = textio.read(2)
                                jeżeli c2 == '':
                                    przerwij
                                self.assertEqual(len(c2), 2)
                                got_lines.append(c2 + textio.readline())
                        inaczej:
                            got_lines = list(textio)

                        dla got_line, exp_line w zip(got_lines, exp_lines):
                            self.assertEqual(got_line, exp_line)
                        self.assertEqual(len(got_lines), len(exp_lines))

    def test_newlines_input(self):
        testdata = b"AAA\nBB\x00B\nCCC\rDDD\rEEE\r\nFFF\r\nGGG"
        normalized = testdata.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        dla newline, expected w [
            (Nic, normalized.decode("ascii").splitlines(keepends=Prawda)),
            ("", testdata.decode("ascii").splitlines(keepends=Prawda)),
            ("\n", ["AAA\n", "BB\x00B\n", "CCC\rDDD\rEEE\r\n", "FFF\r\n", "GGG"]),
            ("\r\n", ["AAA\nBB\x00B\nCCC\rDDD\rEEE\r\n", "FFF\r\n", "GGG"]),
            ("\r",  ["AAA\nBB\x00B\nCCC\r", "DDD\r", "EEE\r", "\nFFF\r", "\nGGG"]),
            ]:
            buf = self.BytesIO(testdata)
            txt = self.TextIOWrapper(buf, encoding="ascii", newline=newline)
            self.assertEqual(txt.readlines(), expected)
            txt.seek(0)
            self.assertEqual(txt.read(), "".join(expected))

    def test_newlines_output(self):
        testdict = {
            "": b"AAA\nBBB\nCCC\nX\rY\r\nZ",
            "\n": b"AAA\nBBB\nCCC\nX\rY\r\nZ",
            "\r": b"AAA\rBBB\rCCC\rX\rY\r\rZ",
            "\r\n": b"AAA\r\nBBB\r\nCCC\r\nX\rY\r\r\nZ",
            }
        tests = [(Nic, testdict[os.linesep])] + sorted(testdict.items())
        dla newline, expected w tests:
            buf = self.BytesIO()
            txt = self.TextIOWrapper(buf, encoding="ascii", newline=newline)
            txt.write("AAA\nB")
            txt.write("BB\nCCC\n")
            txt.write("X\rY\r\nZ")
            txt.flush()
            self.assertEqual(buf.closed, Nieprawda)
            self.assertEqual(buf.getvalue(), expected)

    def test_destructor(self):
        l = []
        base = self.BytesIO
        klasa MyBytesIO(base):
            def close(self):
                l.append(self.getvalue())
                base.close(self)
        b = MyBytesIO()
        t = self.TextIOWrapper(b, encoding="ascii")
        t.write("abc")
        usuń t
        support.gc_collect()
        self.assertEqual([b"abc"], l)

    def test_override_destructor(self):
        record = []
        klasa MyTextIO(self.TextIOWrapper):
            def __del__(self):
                record.append(1)
                spróbuj:
                    f = super().__del__
                wyjąwszy AttributeError:
                    dalej
                inaczej:
                    f()
            def close(self):
                record.append(2)
                super().close()
            def flush(self):
                record.append(3)
                super().flush()
        b = self.BytesIO()
        t = MyTextIO(b, encoding="ascii")
        usuń t
        support.gc_collect()
        self.assertEqual(record, [1, 2, 3])

    def test_error_through_destructor(self):
        # Test that the exception state jest nie modified by a destructor,
        # even jeżeli close() fails.
        rawio = self.CloseFailureIO()
        def f():
            self.TextIOWrapper(rawio).xyzzy
        przy support.captured_output("stderr") jako s:
            self.assertRaises(AttributeError, f)
        s = s.getvalue().strip()
        jeżeli s:
            # The destructor *may* have printed an unraisable error, check it
            self.assertEqual(len(s.splitlines()), 1)
            self.assertPrawda(s.startswith("Exception OSError: "), s)
            self.assertPrawda(s.endswith(" ignored"), s)

    # Systematic tests of the text I/O API

    def test_basic_io(self):
        dla chunksize w (1, 2, 3, 4, 5, 15, 16, 17, 31, 32, 33, 63, 64, 65):
            dla enc w "ascii", "latin-1", "utf-8" :# , "utf-16-be", "utf-16-le":
                f = self.open(support.TESTFN, "w+", encoding=enc)
                f._CHUNK_SIZE = chunksize
                self.assertEqual(f.write("abc"), 3)
                f.close()
                f = self.open(support.TESTFN, "r+", encoding=enc)
                f._CHUNK_SIZE = chunksize
                self.assertEqual(f.tell(), 0)
                self.assertEqual(f.read(), "abc")
                cookie = f.tell()
                self.assertEqual(f.seek(0), 0)
                self.assertEqual(f.read(Nic), "abc")
                f.seek(0)
                self.assertEqual(f.read(2), "ab")
                self.assertEqual(f.read(1), "c")
                self.assertEqual(f.read(1), "")
                self.assertEqual(f.read(), "")
                self.assertEqual(f.tell(), cookie)
                self.assertEqual(f.seek(0), 0)
                self.assertEqual(f.seek(0, 2), cookie)
                self.assertEqual(f.write("def"), 3)
                self.assertEqual(f.seek(cookie), cookie)
                self.assertEqual(f.read(), "def")
                jeżeli enc.startswith("utf"):
                    self.multi_line_test(f, enc)
                f.close()

    def multi_line_test(self, f, enc):
        f.seek(0)
        f.truncate()
        sample = "s\xff\u0fff\uffff"
        wlines = []
        dla size w (0, 1, 2, 3, 4, 5, 30, 31, 32, 33, 62, 63, 64, 65, 1000):
            chars = []
            dla i w range(size):
                chars.append(sample[i % len(sample)])
            line = "".join(chars) + "\n"
            wlines.append((f.tell(), line))
            f.write(line)
        f.seek(0)
        rlines = []
        dopóki Prawda:
            pos = f.tell()
            line = f.readline()
            jeżeli nie line:
                przerwij
            rlines.append((pos, line))
        self.assertEqual(rlines, wlines)

    def test_telling(self):
        f = self.open(support.TESTFN, "w+", encoding="utf-8")
        p0 = f.tell()
        f.write("\xff\n")
        p1 = f.tell()
        f.write("\xff\n")
        p2 = f.tell()
        f.seek(0)
        self.assertEqual(f.tell(), p0)
        self.assertEqual(f.readline(), "\xff\n")
        self.assertEqual(f.tell(), p1)
        self.assertEqual(f.readline(), "\xff\n")
        self.assertEqual(f.tell(), p2)
        f.seek(0)
        dla line w f:
            self.assertEqual(line, "\xff\n")
            self.assertRaises(OSError, f.tell)
        self.assertEqual(f.tell(), p2)
        f.close()

    def test_seeking(self):
        chunk_size = _default_chunk_size()
        prefix_size = chunk_size - 2
        u_prefix = "a" * prefix_size
        prefix = bytes(u_prefix.encode("utf-8"))
        self.assertEqual(len(u_prefix), len(prefix))
        u_suffix = "\u8888\n"
        suffix = bytes(u_suffix.encode("utf-8"))
        line = prefix + suffix
        przy self.open(support.TESTFN, "wb") jako f:
            f.write(line*2)
        przy self.open(support.TESTFN, "r", encoding="utf-8") jako f:
            s = f.read(prefix_size)
            self.assertEqual(s, str(prefix, "ascii"))
            self.assertEqual(f.tell(), prefix_size)
            self.assertEqual(f.readline(), u_suffix)

    def test_seeking_too(self):
        # Regression test dla a specific bug
        data = b'\xe0\xbf\xbf\n'
        przy self.open(support.TESTFN, "wb") jako f:
            f.write(data)
        przy self.open(support.TESTFN, "r", encoding="utf-8") jako f:
            f._CHUNK_SIZE  # Just test that it exists
            f._CHUNK_SIZE = 2
            f.readline()
            f.tell()

    def test_seek_and_tell(self):
        #Test seek/tell using the StatefulIncrementalDecoder.
        # Make test faster by doing smaller seeks
        CHUNK_SIZE = 128

        def test_seek_and_tell_with_data(data, min_pos=0):
            """Tell/seek to various points within a data stream oraz ensure
            that the decoded data returned by read() jest consistent."""
            f = self.open(support.TESTFN, 'wb')
            f.write(data)
            f.close()
            f = self.open(support.TESTFN, encoding='test_decoder')
            f._CHUNK_SIZE = CHUNK_SIZE
            decoded = f.read()
            f.close()

            dla i w range(min_pos, len(decoded) + 1): # seek positions
                dla j w [1, 5, len(decoded) - i]: # read lengths
                    f = self.open(support.TESTFN, encoding='test_decoder')
                    self.assertEqual(f.read(i), decoded[:i])
                    cookie = f.tell()
                    self.assertEqual(f.read(j), decoded[i:i + j])
                    f.seek(cookie)
                    self.assertEqual(f.read(), decoded[i:])
                    f.close()

        # Enable the test decoder.
        StatefulIncrementalDecoder.codecEnabled = 1

        # Run the tests.
        spróbuj:
            # Try each test case.
            dla input, _, _ w StatefulIncrementalDecoderTest.test_cases:
                test_seek_and_tell_with_data(input)

            # Position each test case so that it crosses a chunk boundary.
            dla input, _, _ w StatefulIncrementalDecoderTest.test_cases:
                offset = CHUNK_SIZE - len(input)//2
                prefix = b'.'*offset
                # Don't bother seeking into the prefix (takes too long).
                min_pos = offset*2
                test_seek_and_tell_with_data(prefix + input, min_pos)

        # Ensure our test decoder won't interfere przy subsequent tests.
        w_końcu:
            StatefulIncrementalDecoder.codecEnabled = 0

    def test_encoded_writes(self):
        data = "1234567890"
        tests = ("utf-16",
                 "utf-16-le",
                 "utf-16-be",
                 "utf-32",
                 "utf-32-le",
                 "utf-32-be")
        dla encoding w tests:
            buf = self.BytesIO()
            f = self.TextIOWrapper(buf, encoding=encoding)
            # Check jeżeli the BOM jest written only once (see issue1753).
            f.write(data)
            f.write(data)
            f.seek(0)
            self.assertEqual(f.read(), data * 2)
            f.seek(0)
            self.assertEqual(f.read(), data * 2)
            self.assertEqual(buf.getvalue(), (data * 2).encode(encoding))

    def test_unreadable(self):
        klasa UnReadable(self.BytesIO):
            def readable(self):
                zwróć Nieprawda
        txt = self.TextIOWrapper(UnReadable())
        self.assertRaises(OSError, txt.read)

    def test_read_one_by_one(self):
        txt = self.TextIOWrapper(self.BytesIO(b"AA\r\nBB"))
        reads = ""
        dopóki Prawda:
            c = txt.read(1)
            jeżeli nie c:
                przerwij
            reads += c
        self.assertEqual(reads, "AA\nBB")

    def test_readlines(self):
        txt = self.TextIOWrapper(self.BytesIO(b"AA\nBB\nCC"))
        self.assertEqual(txt.readlines(), ["AA\n", "BB\n", "CC"])
        txt.seek(0)
        self.assertEqual(txt.readlines(Nic), ["AA\n", "BB\n", "CC"])
        txt.seek(0)
        self.assertEqual(txt.readlines(5), ["AA\n", "BB\n"])

    # read w amounts equal to TextIOWrapper._CHUNK_SIZE which jest 128.
    def test_read_by_chunk(self):
        # make sure "\r\n" straddles 128 char boundary.
        txt = self.TextIOWrapper(self.BytesIO(b"A" * 127 + b"\r\nB"))
        reads = ""
        dopóki Prawda:
            c = txt.read(128)
            jeżeli nie c:
                przerwij
            reads += c
        self.assertEqual(reads, "A"*127+"\nB")

    def test_writelines(self):
        l = ['ab', 'cd', 'ef']
        buf = self.BytesIO()
        txt = self.TextIOWrapper(buf)
        txt.writelines(l)
        txt.flush()
        self.assertEqual(buf.getvalue(), b'abcdef')

    def test_writelines_userlist(self):
        l = UserList(['ab', 'cd', 'ef'])
        buf = self.BytesIO()
        txt = self.TextIOWrapper(buf)
        txt.writelines(l)
        txt.flush()
        self.assertEqual(buf.getvalue(), b'abcdef')

    def test_writelines_error(self):
        txt = self.TextIOWrapper(self.BytesIO())
        self.assertRaises(TypeError, txt.writelines, [1, 2, 3])
        self.assertRaises(TypeError, txt.writelines, Nic)
        self.assertRaises(TypeError, txt.writelines, b'abc')

    def test_issue1395_1(self):
        txt = self.TextIOWrapper(self.BytesIO(self.testdata), encoding="ascii")

        # read one char at a time
        reads = ""
        dopóki Prawda:
            c = txt.read(1)
            jeżeli nie c:
                przerwij
            reads += c
        self.assertEqual(reads, self.normalized)

    def test_issue1395_2(self):
        txt = self.TextIOWrapper(self.BytesIO(self.testdata), encoding="ascii")
        txt._CHUNK_SIZE = 4

        reads = ""
        dopóki Prawda:
            c = txt.read(4)
            jeżeli nie c:
                przerwij
            reads += c
        self.assertEqual(reads, self.normalized)

    def test_issue1395_3(self):
        txt = self.TextIOWrapper(self.BytesIO(self.testdata), encoding="ascii")
        txt._CHUNK_SIZE = 4

        reads = txt.read(4)
        reads += txt.read(4)
        reads += txt.readline()
        reads += txt.readline()
        reads += txt.readline()
        self.assertEqual(reads, self.normalized)

    def test_issue1395_4(self):
        txt = self.TextIOWrapper(self.BytesIO(self.testdata), encoding="ascii")
        txt._CHUNK_SIZE = 4

        reads = txt.read(4)
        reads += txt.read()
        self.assertEqual(reads, self.normalized)

    def test_issue1395_5(self):
        txt = self.TextIOWrapper(self.BytesIO(self.testdata), encoding="ascii")
        txt._CHUNK_SIZE = 4

        reads = txt.read(4)
        pos = txt.tell()
        txt.seek(0)
        txt.seek(pos)
        self.assertEqual(txt.read(4), "BBB\n")

    def test_issue2282(self):
        buffer = self.BytesIO(self.testdata)
        txt = self.TextIOWrapper(buffer, encoding="ascii")

        self.assertEqual(buffer.seekable(), txt.seekable())

    def test_append_bom(self):
        # The BOM jest nie written again when appending to a non-empty file
        filename = support.TESTFN
        dla charset w ('utf-8-sig', 'utf-16', 'utf-32'):
            przy self.open(filename, 'w', encoding=charset) jako f:
                f.write('aaa')
                pos = f.tell()
            przy self.open(filename, 'rb') jako f:
                self.assertEqual(f.read(), 'aaa'.encode(charset))

            przy self.open(filename, 'a', encoding=charset) jako f:
                f.write('xxx')
            przy self.open(filename, 'rb') jako f:
                self.assertEqual(f.read(), 'aaaxxx'.encode(charset))

    def test_seek_bom(self):
        # Same test, but when seeking manually
        filename = support.TESTFN
        dla charset w ('utf-8-sig', 'utf-16', 'utf-32'):
            przy self.open(filename, 'w', encoding=charset) jako f:
                f.write('aaa')
                pos = f.tell()
            przy self.open(filename, 'r+', encoding=charset) jako f:
                f.seek(pos)
                f.write('zzz')
                f.seek(0)
                f.write('bbb')
            przy self.open(filename, 'rb') jako f:
                self.assertEqual(f.read(), 'bbbzzz'.encode(charset))

    def test_seek_append_bom(self):
        # Same test, but first seek to the start oraz then to the end
        filename = support.TESTFN
        dla charset w ('utf-8-sig', 'utf-16', 'utf-32'):
            przy self.open(filename, 'w', encoding=charset) jako f:
                f.write('aaa')
            przy self.open(filename, 'a', encoding=charset) jako f:
                f.seek(0)
                f.seek(0, self.SEEK_END)
                f.write('xxx')
            przy self.open(filename, 'rb') jako f:
                self.assertEqual(f.read(), 'aaaxxx'.encode(charset))

    def test_errors_property(self):
        przy self.open(support.TESTFN, "w") jako f:
            self.assertEqual(f.errors, "strict")
        przy self.open(support.TESTFN, "w", errors="replace") jako f:
            self.assertEqual(f.errors, "replace")

    @support.no_tracing
    @unittest.skipUnless(threading, 'Threading required dla this test.')
    def test_threads_write(self):
        # Issue6750: concurrent writes could duplicate data
        event = threading.Event()
        przy self.open(support.TESTFN, "w", buffering=1) jako f:
            def run(n):
                text = "Thread%03d\n" % n
                event.wait()
                f.write(text)
            threads = [threading.Thread(target=run, args=(x,))
                       dla x w range(20)]
            przy support.start_threads(threads, event.set):
                time.sleep(0.02)
        przy self.open(support.TESTFN) jako f:
            content = f.read()
            dla n w range(20):
                self.assertEqual(content.count("Thread%03d\n" % n), 1)

    def test_flush_error_on_close(self):
        # Test that text file jest closed despite failed flush
        # oraz that flush() jest called before file closed.
        txt = self.TextIOWrapper(self.BytesIO(self.testdata), encoding="ascii")
        closed = []
        def bad_flush():
            closed[:] = [txt.closed, txt.buffer.closed]
            podnieś OSError()
        txt.flush = bad_flush
        self.assertRaises(OSError, txt.close) # exception nie swallowed
        self.assertPrawda(txt.closed)
        self.assertPrawda(txt.buffer.closed)
        self.assertPrawda(closed)      # flush() called
        self.assertNieprawda(closed[0])  # flush() called before file closed
        self.assertNieprawda(closed[1])
        txt.flush = lambda: Nic  # przerwij reference loop

    def test_close_error_on_close(self):
        buffer = self.BytesIO(self.testdata)
        def bad_flush():
            podnieś OSError('flush')
        def bad_close():
            podnieś OSError('close')
        buffer.close = bad_close
        txt = self.TextIOWrapper(buffer, encoding="ascii")
        txt.flush = bad_flush
        przy self.assertRaises(OSError) jako err: # exception nie swallowed
            txt.close()
        self.assertEqual(err.exception.args, ('close',))
        self.assertIsInstance(err.exception.__context__, OSError)
        self.assertEqual(err.exception.__context__.args, ('flush',))
        self.assertNieprawda(txt.closed)

    def test_nonnormalized_close_error_on_close(self):
        # Issue #21677
        buffer = self.BytesIO(self.testdata)
        def bad_flush():
            podnieś non_existing_flush
        def bad_close():
            podnieś non_existing_close
        buffer.close = bad_close
        txt = self.TextIOWrapper(buffer, encoding="ascii")
        txt.flush = bad_flush
        przy self.assertRaises(NameError) jako err: # exception nie swallowed
            txt.close()
        self.assertIn('non_existing_close', str(err.exception))
        self.assertIsInstance(err.exception.__context__, NameError)
        self.assertIn('non_existing_flush', str(err.exception.__context__))
        self.assertNieprawda(txt.closed)

    def test_multi_close(self):
        txt = self.TextIOWrapper(self.BytesIO(self.testdata), encoding="ascii")
        txt.close()
        txt.close()
        txt.close()
        self.assertRaises(ValueError, txt.flush)

    def test_unseekable(self):
        txt = self.TextIOWrapper(self.MockUnseekableIO(self.testdata))
        self.assertRaises(self.UnsupportedOperation, txt.tell)
        self.assertRaises(self.UnsupportedOperation, txt.seek, 0)

    def test_readonly_attributes(self):
        txt = self.TextIOWrapper(self.BytesIO(self.testdata), encoding="ascii")
        buf = self.BytesIO(self.testdata)
        przy self.assertRaises(AttributeError):
            txt.buffer = buf

    def test_rawio(self):
        # Issue #12591: TextIOWrapper must work przy raw I/O objects, so
        # that subprocess.Popen() can have the required unbuffered
        # semantics przy universal_newlines=Prawda.
        raw = self.MockRawIO([b'abc', b'def', b'ghi\njkl\nopq\n'])
        txt = self.TextIOWrapper(raw, encoding='ascii', newline='\n')
        # Reads
        self.assertEqual(txt.read(4), 'abcd')
        self.assertEqual(txt.readline(), 'efghi\n')
        self.assertEqual(list(txt), ['jkl\n', 'opq\n'])

    def test_rawio_write_through(self):
        # Issue #12591: przy write_through=Prawda, writes don't need a flush
        raw = self.MockRawIO([b'abc', b'def', b'ghi\njkl\nopq\n'])
        txt = self.TextIOWrapper(raw, encoding='ascii', newline='\n',
                                 write_through=Prawda)
        txt.write('1')
        txt.write('23\n4')
        txt.write('5')
        self.assertEqual(b''.join(raw._write_stack), b'123\n45')

    def test_bufio_write_through(self):
        # Issue #21396: write_through=Prawda doesn't force a flush()
        # on the underlying binary buffered object.
        flush_called, write_called = [], []
        klasa BufferedWriter(self.BufferedWriter):
            def flush(self, *args, **kwargs):
                flush_called.append(Prawda)
                zwróć super().flush(*args, **kwargs)
            def write(self, *args, **kwargs):
                write_called.append(Prawda)
                zwróć super().write(*args, **kwargs)

        rawio = self.BytesIO()
        data = b"a"
        bufio = BufferedWriter(rawio, len(data)*2)
        textio = self.TextIOWrapper(bufio, encoding='ascii',
                                    write_through=Prawda)
        # write to the buffered io but don't overflow the buffer
        text = data.decode('ascii')
        textio.write(text)

        # buffer.flush jest nie called przy write_through=Prawda
        self.assertNieprawda(flush_called)
        # buffer.write *is* called przy write_through=Prawda
        self.assertPrawda(write_called)
        self.assertEqual(rawio.getvalue(), b"") # no flush

        write_called = [] # reset
        textio.write(text * 10) # total content jest larger than bufio buffer
        self.assertPrawda(write_called)
        self.assertEqual(rawio.getvalue(), data * 11) # all flushed

    def test_read_nonbytes(self):
        # Issue #17106
        # Crash when underlying read() returns non-bytes
        t = self.TextIOWrapper(self.StringIO('a'))
        self.assertRaises(TypeError, t.read, 1)
        t = self.TextIOWrapper(self.StringIO('a'))
        self.assertRaises(TypeError, t.readline)
        t = self.TextIOWrapper(self.StringIO('a'))
        self.assertRaises(TypeError, t.read)

    def test_illegal_decoder(self):
        # Issue #17106
        # Bypass the early encoding check added w issue 20404
        def _make_illegal_wrapper():
            quopri = codecs.lookup("quopri")
            quopri._is_text_encoding = Prawda
            spróbuj:
                t = self.TextIOWrapper(self.BytesIO(b'aaaaaa'),
                                       newline='\n', encoding="quopri")
            w_końcu:
                quopri._is_text_encoding = Nieprawda
            zwróć t
        # Crash when decoder returns non-string
        t = _make_illegal_wrapper()
        self.assertRaises(TypeError, t.read, 1)
        t = _make_illegal_wrapper()
        self.assertRaises(TypeError, t.readline)
        t = _make_illegal_wrapper()
        self.assertRaises(TypeError, t.read)

    def _check_create_at_shutdown(self, **kwargs):
        # Issue #20037: creating a TextIOWrapper at shutdown
        # shouldn't crash the interpreter.
        iomod = self.io.__name__
        code = """jeżeli 1:
            zaimportuj codecs
            zaimportuj {iomod} jako io

            # Avoid looking up codecs at shutdown
            codecs.lookup('utf-8')

            klasa C:
                def __init__(self):
                    self.buf = io.BytesIO()
                def __del__(self):
                    io.TextIOWrapper(self.buf, **{kwargs})
                    print("ok")
            c = C()
            """.format(iomod=iomod, kwargs=kwargs)
        zwróć assert_python_ok("-c", code)

    def test_create_at_shutdown_without_encoding(self):
        rc, out, err = self._check_create_at_shutdown()
        jeżeli err:
            # Can error out przy a RuntimeError jeżeli the module state
            # isn't found.
            self.assertIn(self.shutdown_error, err.decode())
        inaczej:
            self.assertEqual("ok", out.decode().strip())

    def test_create_at_shutdown_with_encoding(self):
        rc, out, err = self._check_create_at_shutdown(encoding='utf-8',
                                                      errors='strict')
        self.assertNieprawda(err)
        self.assertEqual("ok", out.decode().strip())

    def test_read_byteslike(self):
        r = MemviewBytesIO(b'Just some random string\n')
        t = self.TextIOWrapper(r, 'utf-8')

        # TextIOwrapper will nie read the full string, because
        # we truncate it to a multiple of the native int size
        # so that we can construct a more complex memoryview.
        bytes_val =  _to_memoryview(r.getvalue()).tobytes()

        self.assertEqual(t.read(200), bytes_val.decode('utf-8'))

    def test_issue22849(self):
        klasa F(object):
            def readable(self): zwróć Prawda
            def writable(self): zwróć Prawda
            def seekable(self): zwróć Prawda

        dla i w range(10):
            spróbuj:
                self.TextIOWrapper(F(), encoding='utf-8')
            wyjąwszy Exception:
                dalej

        F.tell = lambda x: 0
        t = self.TextIOWrapper(F(), encoding='utf-8')


klasa MemviewBytesIO(io.BytesIO):
    '''A BytesIO object whose read method returns memoryviews
       rather than bytes'''

    def read1(self, len_):
        zwróć _to_memoryview(super().read1(len_))

    def read(self, len_):
        zwróć _to_memoryview(super().read(len_))

def _to_memoryview(buf):
    '''Convert bytes-object *buf* to a non-trivial memoryview'''

    arr = array.array('i')
    idx = len(buf) - len(buf) % arr.itemsize
    arr.frombytes(buf[:idx])
    zwróć memoryview(arr)


klasa CTextIOWrapperTest(TextIOWrapperTest):
    io = io
    shutdown_error = "RuntimeError: could nie find io module state"

    def test_initialization(self):
        r = self.BytesIO(b"\xc3\xa9\n\n")
        b = self.BufferedReader(r, 1000)
        t = self.TextIOWrapper(b)
        self.assertRaises(ValueError, t.__init__, b, newline='xyzzy')
        self.assertRaises(ValueError, t.read)

        t = self.TextIOWrapper.__new__(self.TextIOWrapper)
        self.assertRaises(Exception, repr, t)

    def test_garbage_collection(self):
        # C TextIOWrapper objects are collected, oraz collecting them flushes
        # all data to disk.
        # The Python version has __del__, so it ends w gc.garbage instead.
        przy support.check_warnings(('', ResourceWarning)):
            rawio = io.FileIO(support.TESTFN, "wb")
            b = self.BufferedWriter(rawio)
            t = self.TextIOWrapper(b, encoding="ascii")
            t.write("456def")
            t.x = t
            wr = weakref.ref(t)
            usuń t
            support.gc_collect()
        self.assertIsNic(wr(), wr)
        przy self.open(support.TESTFN, "rb") jako f:
            self.assertEqual(f.read(), b"456def")

    def test_rwpair_cleared_before_textio(self):
        # Issue 13070: TextIOWrapper's finalization would crash when called
        # after the reference to the underlying BufferedRWPair's writer got
        # cleared by the GC.
        dla i w range(1000):
            b1 = self.BufferedRWPair(self.MockRawIO(), self.MockRawIO())
            t1 = self.TextIOWrapper(b1, encoding="ascii")
            b2 = self.BufferedRWPair(self.MockRawIO(), self.MockRawIO())
            t2 = self.TextIOWrapper(b2, encoding="ascii")
            # circular references
            t1.buddy = t2
            t2.buddy = t1
        support.gc_collect()


klasa PyTextIOWrapperTest(TextIOWrapperTest):
    io = pyio
    #shutdown_error = "LookupError: unknown encoding: ascii"
    shutdown_error = "TypeError: 'NicType' object jest nie iterable"


klasa IncrementalNewlineDecoderTest(unittest.TestCase):

    def check_newline_decoding_utf8(self, decoder):
        # UTF-8 specific tests dla a newline decoder
        def _check_decode(b, s, **kwargs):
            # We exercise getstate() / setstate() jako well jako decode()
            state = decoder.getstate()
            self.assertEqual(decoder.decode(b, **kwargs), s)
            decoder.setstate(state)
            self.assertEqual(decoder.decode(b, **kwargs), s)

        _check_decode(b'\xe8\xa2\x88', "\u8888")

        _check_decode(b'\xe8', "")
        _check_decode(b'\xa2', "")
        _check_decode(b'\x88', "\u8888")

        _check_decode(b'\xe8', "")
        _check_decode(b'\xa2', "")
        _check_decode(b'\x88', "\u8888")

        _check_decode(b'\xe8', "")
        self.assertRaises(UnicodeDecodeError, decoder.decode, b'', final=Prawda)

        decoder.reset()
        _check_decode(b'\n', "\n")
        _check_decode(b'\r', "")
        _check_decode(b'', "\n", final=Prawda)
        _check_decode(b'\r', "\n", final=Prawda)

        _check_decode(b'\r', "")
        _check_decode(b'a', "\na")

        _check_decode(b'\r\r\n', "\n\n")
        _check_decode(b'\r', "")
        _check_decode(b'\r', "\n")
        _check_decode(b'\na', "\na")

        _check_decode(b'\xe8\xa2\x88\r\n', "\u8888\n")
        _check_decode(b'\xe8\xa2\x88', "\u8888")
        _check_decode(b'\n', "\n")
        _check_decode(b'\xe8\xa2\x88\r', "\u8888")
        _check_decode(b'\n', "\n")

    def check_newline_decoding(self, decoder, encoding):
        result = []
        jeżeli encoding jest nie Nic:
            encoder = codecs.getincrementalencoder(encoding)()
            def _decode_bytewise(s):
                # Decode one byte at a time
                dla b w encoder.encode(s):
                    result.append(decoder.decode(bytes([b])))
        inaczej:
            encoder = Nic
            def _decode_bytewise(s):
                # Decode one char at a time
                dla c w s:
                    result.append(decoder.decode(c))
        self.assertEqual(decoder.newlines, Nic)
        _decode_bytewise("abc\n\r")
        self.assertEqual(decoder.newlines, '\n')
        _decode_bytewise("\nabc")
        self.assertEqual(decoder.newlines, ('\n', '\r\n'))
        _decode_bytewise("abc\r")
        self.assertEqual(decoder.newlines, ('\n', '\r\n'))
        _decode_bytewise("abc")
        self.assertEqual(decoder.newlines, ('\r', '\n', '\r\n'))
        _decode_bytewise("abc\r")
        self.assertEqual("".join(result), "abc\n\nabcabc\nabcabc")
        decoder.reset()
        input = "abc"
        jeżeli encoder jest nie Nic:
            encoder.reset()
            input = encoder.encode(input)
        self.assertEqual(decoder.decode(input), "abc")
        self.assertEqual(decoder.newlines, Nic)

    def test_newline_decoder(self):
        encodings = (
            # Nic meaning the IncrementalNewlineDecoder takes unicode input
            # rather than bytes input
            Nic, 'utf-8', 'latin-1',
            'utf-16', 'utf-16-le', 'utf-16-be',
            'utf-32', 'utf-32-le', 'utf-32-be',
        )
        dla enc w encodings:
            decoder = enc oraz codecs.getincrementaldecoder(enc)()
            decoder = self.IncrementalNewlineDecoder(decoder, translate=Prawda)
            self.check_newline_decoding(decoder, enc)
        decoder = codecs.getincrementaldecoder("utf-8")()
        decoder = self.IncrementalNewlineDecoder(decoder, translate=Prawda)
        self.check_newline_decoding_utf8(decoder)

    def test_newline_bytes(self):
        # Issue 5433: Excessive optimization w IncrementalNewlineDecoder
        def _check(dec):
            self.assertEqual(dec.newlines, Nic)
            self.assertEqual(dec.decode("\u0D00"), "\u0D00")
            self.assertEqual(dec.newlines, Nic)
            self.assertEqual(dec.decode("\u0A00"), "\u0A00")
            self.assertEqual(dec.newlines, Nic)
        dec = self.IncrementalNewlineDecoder(Nic, translate=Nieprawda)
        _check(dec)
        dec = self.IncrementalNewlineDecoder(Nic, translate=Prawda)
        _check(dec)

klasa CIncrementalNewlineDecoderTest(IncrementalNewlineDecoderTest):
    dalej

klasa PyIncrementalNewlineDecoderTest(IncrementalNewlineDecoderTest):
    dalej


# XXX Tests dla open()

klasa MiscIOTest(unittest.TestCase):

    def tearDown(self):
        support.unlink(support.TESTFN)

    def test___all__(self):
        dla name w self.io.__all__:
            obj = getattr(self.io, name, Nic)
            self.assertIsNotNic(obj, name)
            jeżeli name == "open":
                kontynuuj
            albo_inaczej "error" w name.lower() albo name == "UnsupportedOperation":
                self.assertPrawda(issubclass(obj, Exception), name)
            albo_inaczej nie name.startswith("SEEK_"):
                self.assertPrawda(issubclass(obj, self.IOBase))

    def test_attributes(self):
        f = self.open(support.TESTFN, "wb", buffering=0)
        self.assertEqual(f.mode, "wb")
        f.close()

        przy support.check_warnings(('', DeprecationWarning)):
            f = self.open(support.TESTFN, "U")
        self.assertEqual(f.name,            support.TESTFN)
        self.assertEqual(f.buffer.name,     support.TESTFN)
        self.assertEqual(f.buffer.raw.name, support.TESTFN)
        self.assertEqual(f.mode,            "U")
        self.assertEqual(f.buffer.mode,     "rb")
        self.assertEqual(f.buffer.raw.mode, "rb")
        f.close()

        f = self.open(support.TESTFN, "w+")
        self.assertEqual(f.mode,            "w+")
        self.assertEqual(f.buffer.mode,     "rb+") # Does it really matter?
        self.assertEqual(f.buffer.raw.mode, "rb+")

        g = self.open(f.fileno(), "wb", closefd=Nieprawda)
        self.assertEqual(g.mode,     "wb")
        self.assertEqual(g.raw.mode, "wb")
        self.assertEqual(g.name,     f.fileno())
        self.assertEqual(g.raw.name, f.fileno())
        f.close()
        g.close()

    def test_io_after_close(self):
        dla kwargs w [
                {"mode": "w"},
                {"mode": "wb"},
                {"mode": "w", "buffering": 1},
                {"mode": "w", "buffering": 2},
                {"mode": "wb", "buffering": 0},
                {"mode": "r"},
                {"mode": "rb"},
                {"mode": "r", "buffering": 1},
                {"mode": "r", "buffering": 2},
                {"mode": "rb", "buffering": 0},
                {"mode": "w+"},
                {"mode": "w+b"},
                {"mode": "w+", "buffering": 1},
                {"mode": "w+", "buffering": 2},
                {"mode": "w+b", "buffering": 0},
            ]:
            f = self.open(support.TESTFN, **kwargs)
            f.close()
            self.assertRaises(ValueError, f.flush)
            self.assertRaises(ValueError, f.fileno)
            self.assertRaises(ValueError, f.isatty)
            self.assertRaises(ValueError, f.__iter__)
            jeżeli hasattr(f, "peek"):
                self.assertRaises(ValueError, f.peek, 1)
            self.assertRaises(ValueError, f.read)
            jeżeli hasattr(f, "read1"):
                self.assertRaises(ValueError, f.read1, 1024)
            jeżeli hasattr(f, "readall"):
                self.assertRaises(ValueError, f.readall)
            jeżeli hasattr(f, "readinto"):
                self.assertRaises(ValueError, f.readinto, bytearray(1024))
            jeżeli hasattr(f, "readinto1"):
                self.assertRaises(ValueError, f.readinto1, bytearray(1024))
            self.assertRaises(ValueError, f.readline)
            self.assertRaises(ValueError, f.readlines)
            self.assertRaises(ValueError, f.seek, 0)
            self.assertRaises(ValueError, f.tell)
            self.assertRaises(ValueError, f.truncate)
            self.assertRaises(ValueError, f.write,
                              b"" jeżeli "b" w kwargs['mode'] inaczej "")
            self.assertRaises(ValueError, f.writelines, [])
            self.assertRaises(ValueError, next, f)

    def test_blockingioerror(self):
        # Various BlockingIOError issues
        klasa C(str):
            dalej
        c = C("")
        b = self.BlockingIOError(1, c)
        c.b = b
        b.c = c
        wr = weakref.ref(c)
        usuń c, b
        support.gc_collect()
        self.assertIsNic(wr(), wr)

    def test_abcs(self):
        # Test the visible base classes are ABCs.
        self.assertIsInstance(self.IOBase, abc.ABCMeta)
        self.assertIsInstance(self.RawIOBase, abc.ABCMeta)
        self.assertIsInstance(self.BufferedIOBase, abc.ABCMeta)
        self.assertIsInstance(self.TextIOBase, abc.ABCMeta)

    def _check_abc_inheritance(self, abcmodule):
        przy self.open(support.TESTFN, "wb", buffering=0) jako f:
            self.assertIsInstance(f, abcmodule.IOBase)
            self.assertIsInstance(f, abcmodule.RawIOBase)
            self.assertNotIsInstance(f, abcmodule.BufferedIOBase)
            self.assertNotIsInstance(f, abcmodule.TextIOBase)
        przy self.open(support.TESTFN, "wb") jako f:
            self.assertIsInstance(f, abcmodule.IOBase)
            self.assertNotIsInstance(f, abcmodule.RawIOBase)
            self.assertIsInstance(f, abcmodule.BufferedIOBase)
            self.assertNotIsInstance(f, abcmodule.TextIOBase)
        przy self.open(support.TESTFN, "w") jako f:
            self.assertIsInstance(f, abcmodule.IOBase)
            self.assertNotIsInstance(f, abcmodule.RawIOBase)
            self.assertNotIsInstance(f, abcmodule.BufferedIOBase)
            self.assertIsInstance(f, abcmodule.TextIOBase)

    def test_abc_inheritance(self):
        # Test implementations inherit z their respective ABCs
        self._check_abc_inheritance(self)

    def test_abc_inheritance_official(self):
        # Test implementations inherit z the official ABCs of the
        # baseline "io" module.
        self._check_abc_inheritance(io)

    def _check_warn_on_dealloc(self, *args, **kwargs):
        f = open(*args, **kwargs)
        r = repr(f)
        przy self.assertWarns(ResourceWarning) jako cm:
            f = Nic
            support.gc_collect()
        self.assertIn(r, str(cm.warning.args[0]))

    def test_warn_on_dealloc(self):
        self._check_warn_on_dealloc(support.TESTFN, "wb", buffering=0)
        self._check_warn_on_dealloc(support.TESTFN, "wb")
        self._check_warn_on_dealloc(support.TESTFN, "w")

    def _check_warn_on_dealloc_fd(self, *args, **kwargs):
        fds = []
        def cleanup_fds():
            dla fd w fds:
                spróbuj:
                    os.close(fd)
                wyjąwszy OSError jako e:
                    jeżeli e.errno != errno.EBADF:
                        podnieś
        self.addCleanup(cleanup_fds)
        r, w = os.pipe()
        fds += r, w
        self._check_warn_on_dealloc(r, *args, **kwargs)
        # When using closefd=Nieprawda, there's no warning
        r, w = os.pipe()
        fds += r, w
        przy warnings.catch_warnings(record=Prawda) jako recorded:
            open(r, *args, closefd=Nieprawda, **kwargs)
            support.gc_collect()
        self.assertEqual(recorded, [])

    def test_warn_on_dealloc_fd(self):
        self._check_warn_on_dealloc_fd("rb", buffering=0)
        self._check_warn_on_dealloc_fd("rb")
        self._check_warn_on_dealloc_fd("r")


    def test_pickling(self):
        # Pickling file objects jest forbidden
        dla kwargs w [
                {"mode": "w"},
                {"mode": "wb"},
                {"mode": "wb", "buffering": 0},
                {"mode": "r"},
                {"mode": "rb"},
                {"mode": "rb", "buffering": 0},
                {"mode": "w+"},
                {"mode": "w+b"},
                {"mode": "w+b", "buffering": 0},
            ]:
            dla protocol w range(pickle.HIGHEST_PROTOCOL + 1):
                przy self.open(support.TESTFN, **kwargs) jako f:
                    self.assertRaises(TypeError, pickle.dumps, f, protocol)

    def test_nonblock_pipe_write_bigbuf(self):
        self._test_nonblock_pipe_write(16*1024)

    def test_nonblock_pipe_write_smallbuf(self):
        self._test_nonblock_pipe_write(1024)

    @unittest.skipUnless(hasattr(os, 'set_blocking'),
                         'os.set_blocking() required dla this test')
    def _test_nonblock_pipe_write(self, bufsize):
        sent = []
        received = []
        r, w = os.pipe()
        os.set_blocking(r, Nieprawda)
        os.set_blocking(w, Nieprawda)

        # To exercise all code paths w the C implementation we need
        # to play przy buffer sizes.  For instance, jeżeli we choose a
        # buffer size less than albo equal to _PIPE_BUF (4096 on Linux)
        # then we will never get a partial write of the buffer.
        rf = self.open(r, mode='rb', closefd=Prawda, buffering=bufsize)
        wf = self.open(w, mode='wb', closefd=Prawda, buffering=bufsize)

        przy rf, wf:
            dla N w 9999, 73, 7574:
                spróbuj:
                    i = 0
                    dopóki Prawda:
                        msg = bytes([i % 26 + 97]) * N
                        sent.append(msg)
                        wf.write(msg)
                        i += 1

                wyjąwszy self.BlockingIOError jako e:
                    self.assertEqual(e.args[0], errno.EAGAIN)
                    self.assertEqual(e.args[2], e.characters_written)
                    sent[-1] = sent[-1][:e.characters_written]
                    received.append(rf.read())
                    msg = b'BLOCKED'
                    wf.write(msg)
                    sent.append(msg)

            dopóki Prawda:
                spróbuj:
                    wf.flush()
                    przerwij
                wyjąwszy self.BlockingIOError jako e:
                    self.assertEqual(e.args[0], errno.EAGAIN)
                    self.assertEqual(e.args[2], e.characters_written)
                    self.assertEqual(e.characters_written, 0)
                    received.append(rf.read())

            received += iter(rf.read, Nic)

        sent, received = b''.join(sent), b''.join(received)
        self.assertEqual(sent, received)
        self.assertPrawda(wf.closed)
        self.assertPrawda(rf.closed)

    def test_create_fail(self):
        # 'x' mode fails jeżeli file jest existing
        przy self.open(support.TESTFN, 'w'):
            dalej
        self.assertRaises(FileExistsError, self.open, support.TESTFN, 'x')

    def test_create_writes(self):
        # 'x' mode opens dla writing
        przy self.open(support.TESTFN, 'xb') jako f:
            f.write(b"spam")
        przy self.open(support.TESTFN, 'rb') jako f:
            self.assertEqual(b"spam", f.read())

    def test_open_allargs(self):
        # there used to be a buffer overflow w the parser dla rawmode
        self.assertRaises(ValueError, self.open, support.TESTFN, 'rwax+')


klasa CMiscIOTest(MiscIOTest):
    io = io

    def test_readinto_buffer_overflow(self):
        # Issue #18025
        klasa BadReader(self.io.BufferedIOBase):
            def read(self, n=-1):
                zwróć b'x' * 10**6
        bufio = BadReader()
        b = bytearray(2)
        self.assertRaises(ValueError, bufio.readinto, b)

    @unittest.skipUnless(threading, 'Threading required dla this test.')
    def check_daemon_threads_shutdown_deadlock(self, stream_name):
        # Issue #23309: deadlocks at shutdown should be avoided when a
        # daemon thread oraz the main thread both write to a file.
        code = """jeżeli 1:
            zaimportuj sys
            zaimportuj time
            zaimportuj threading

            file = sys.{stream_name}

            def run():
                dopóki Prawda:
                    file.write('.')
                    file.flush()

            thread = threading.Thread(target=run)
            thread.daemon = Prawda
            thread.start()

            time.sleep(0.5)
            file.write('!')
            file.flush()
            """.format_map(locals())
        res, _ = run_python_until_end("-c", code)
        err = res.err.decode()
        jeżeli res.rc != 0:
            # Failure: should be a fatal error
            self.assertIn("Fatal Python error: could nie acquire lock "
                          "dla <_io.BufferedWriter name='<{stream_name}>'> "
                          "at interpreter shutdown, possibly due to "
                          "daemon threads".format_map(locals()),
                          err)
        inaczej:
            self.assertNieprawda(err.strip('.!'))

    def test_daemon_threads_shutdown_stdout_deadlock(self):
        self.check_daemon_threads_shutdown_deadlock('stdout')

    def test_daemon_threads_shutdown_stderr_deadlock(self):
        self.check_daemon_threads_shutdown_deadlock('stderr')


klasa PyMiscIOTest(MiscIOTest):
    io = pyio


@unittest.skipIf(os.name == 'nt', 'POSIX signals required dla this test.')
klasa SignalsTest(unittest.TestCase):

    def setUp(self):
        self.oldalrm = signal.signal(signal.SIGALRM, self.alarm_interrupt)

    def tearDown(self):
        signal.signal(signal.SIGALRM, self.oldalrm)

    def alarm_interrupt(self, sig, frame):
        1/0

    @unittest.skipUnless(threading, 'Threading required dla this test.')
    def check_interrupted_write(self, item, bytes, **fdopen_kwargs):
        """Check that a partial write, when it gets interrupted, properly
        invokes the signal handler, oraz bubbles up the exception podnieśd
        w the latter."""
        read_results = []
        def _read():
            jeżeli hasattr(signal, 'pthread_sigmask'):
                signal.pthread_sigmask(signal.SIG_BLOCK, [signal.SIGALRM])
            s = os.read(r, 1)
            read_results.append(s)
        t = threading.Thread(target=_read)
        t.daemon = Prawda
        r, w = os.pipe()
        fdopen_kwargs["closefd"] = Nieprawda
        large_data = item * (support.PIPE_MAX_SIZE // len(item) + 1)
        spróbuj:
            wio = self.io.open(w, **fdopen_kwargs)
            t.start()
            # Fill the pipe enough that the write will be blocking.
            # It will be interrupted by the timer armed above.  Since the
            # other thread has read one byte, the low-level write will
            # zwróć przy a successful (partial) result rather than an EINTR.
            # The buffered IO layer must check dla pending signal
            # handlers, which w this case will invoke alarm_interrupt().
            signal.alarm(1)
            spróbuj:
                self.assertRaises(ZeroDivisionError, wio.write, large_data)
            w_końcu:
                signal.alarm(0)
                t.join()
            # We got one byte, get another one oraz check that it isn't a
            # repeat of the first one.
            read_results.append(os.read(r, 1))
            self.assertEqual(read_results, [bytes[0:1], bytes[1:2]])
        w_końcu:
            os.close(w)
            os.close(r)
            # This jest deliberate. If we didn't close the file descriptor
            # before closing wio, wio would try to flush its internal
            # buffer, oraz block again.
            spróbuj:
                wio.close()
            wyjąwszy OSError jako e:
                jeżeli e.errno != errno.EBADF:
                    podnieś

    def test_interrupted_write_unbuffered(self):
        self.check_interrupted_write(b"xy", b"xy", mode="wb", buffering=0)

    def test_interrupted_write_buffered(self):
        self.check_interrupted_write(b"xy", b"xy", mode="wb")

    # Issue #22331: The test hangs on FreeBSD 7.2
    @support.requires_freebsd_version(8)
    def test_interrupted_write_text(self):
        self.check_interrupted_write("xy", b"xy", mode="w", encoding="ascii")

    @support.no_tracing
    def check_reentrant_write(self, data, **fdopen_kwargs):
        def on_alarm(*args):
            # Will be called reentrantly z the same thread
            wio.write(data)
            1/0
        signal.signal(signal.SIGALRM, on_alarm)
        r, w = os.pipe()
        wio = self.io.open(w, **fdopen_kwargs)
        spróbuj:
            signal.alarm(1)
            # Either the reentrant call to wio.write() fails przy RuntimeError,
            # albo the signal handler podnieśs ZeroDivisionError.
            przy self.assertRaises((ZeroDivisionError, RuntimeError)) jako cm:
                dopóki 1:
                    dla i w range(100):
                        wio.write(data)
                        wio.flush()
                    # Make sure the buffer doesn't fill up oraz block further writes
                    os.read(r, len(data) * 100)
            exc = cm.exception
            jeżeli isinstance(exc, RuntimeError):
                self.assertPrawda(str(exc).startswith("reentrant call"), str(exc))
        w_końcu:
            wio.close()
            os.close(r)

    def test_reentrant_write_buffered(self):
        self.check_reentrant_write(b"xy", mode="wb")

    def test_reentrant_write_text(self):
        self.check_reentrant_write("xy", mode="w", encoding="ascii")

    def check_interrupted_read_retry(self, decode, **fdopen_kwargs):
        """Check that a buffered read, when it gets interrupted (either
        returning a partial result albo EINTR), properly invokes the signal
        handler oraz retries jeżeli the latter returned successfully."""
        r, w = os.pipe()
        fdopen_kwargs["closefd"] = Nieprawda
        def alarm_handler(sig, frame):
            os.write(w, b"bar")
        signal.signal(signal.SIGALRM, alarm_handler)
        spróbuj:
            rio = self.io.open(r, **fdopen_kwargs)
            os.write(w, b"foo")
            signal.alarm(1)
            # Expected behaviour:
            # - first raw read() returns partial b"foo"
            # - second raw read() returns EINTR
            # - third raw read() returns b"bar"
            self.assertEqual(decode(rio.read(6)), "foobar")
        w_końcu:
            rio.close()
            os.close(w)
            os.close(r)

    def test_interrupted_read_retry_buffered(self):
        self.check_interrupted_read_retry(lambda x: x.decode('latin1'),
                                          mode="rb")

    def test_interrupted_read_retry_text(self):
        self.check_interrupted_read_retry(lambda x: x,
                                          mode="r")

    @unittest.skipUnless(threading, 'Threading required dla this test.')
    def check_interrupted_write_retry(self, item, **fdopen_kwargs):
        """Check that a buffered write, when it gets interrupted (either
        returning a partial result albo EINTR), properly invokes the signal
        handler oraz retries jeżeli the latter returned successfully."""
        select = support.import_module("select")

        # A quantity that exceeds the buffer size of an anonymous pipe's
        # write end.
        N = support.PIPE_MAX_SIZE
        r, w = os.pipe()
        fdopen_kwargs["closefd"] = Nieprawda

        # We need a separate thread to read z the pipe oraz allow the
        # write() to finish.  This thread jest started after the SIGALRM jest
        # received (forcing a first EINTR w write()).
        read_results = []
        write_finished = Nieprawda
        error = Nic
        def _read():
            spróbuj:
                dopóki nie write_finished:
                    dopóki r w select.select([r], [], [], 1.0)[0]:
                        s = os.read(r, 1024)
                        read_results.append(s)
            wyjąwszy BaseException jako exc:
                nonlocal error
                error = exc
        t = threading.Thread(target=_read)
        t.daemon = Prawda
        def alarm1(sig, frame):
            signal.signal(signal.SIGALRM, alarm2)
            signal.alarm(1)
        def alarm2(sig, frame):
            t.start()

        large_data = item * N
        signal.signal(signal.SIGALRM, alarm1)
        spróbuj:
            wio = self.io.open(w, **fdopen_kwargs)
            signal.alarm(1)
            # Expected behaviour:
            # - first raw write() jest partial (because of the limited pipe buffer
            #   oraz the first alarm)
            # - second raw write() returns EINTR (because of the second alarm)
            # - subsequent write()s are successful (either partial albo complete)
            written = wio.write(large_data)
            self.assertEqual(N, written)

            wio.flush()
            write_finished = Prawda
            t.join()

            self.assertIsNic(error)
            self.assertEqual(N, sum(len(x) dla x w read_results))
        w_końcu:
            write_finished = Prawda
            os.close(w)
            os.close(r)
            # This jest deliberate. If we didn't close the file descriptor
            # before closing wio, wio would try to flush its internal
            # buffer, oraz could block (in case of failure).
            spróbuj:
                wio.close()
            wyjąwszy OSError jako e:
                jeżeli e.errno != errno.EBADF:
                    podnieś

    def test_interrupted_write_retry_buffered(self):
        self.check_interrupted_write_retry(b"x", mode="wb")

    def test_interrupted_write_retry_text(self):
        self.check_interrupted_write_retry("x", mode="w", encoding="latin1")


klasa CSignalsTest(SignalsTest):
    io = io

klasa PySignalsTest(SignalsTest):
    io = pyio

    # Handling reentrancy issues would slow down _pyio even more, so the
    # tests are disabled.
    test_reentrant_write_buffered = Nic
    test_reentrant_write_text = Nic


def load_tests(*args):
    tests = (CIOTest, PyIOTest, APIMismatchTest,
             CBufferedReaderTest, PyBufferedReaderTest,
             CBufferedWriterTest, PyBufferedWriterTest,
             CBufferedRWPairTest, PyBufferedRWPairTest,
             CBufferedRandomTest, PyBufferedRandomTest,
             StatefulIncrementalDecoderTest,
             CIncrementalNewlineDecoderTest, PyIncrementalNewlineDecoderTest,
             CTextIOWrapperTest, PyTextIOWrapperTest,
             CMiscIOTest, PyMiscIOTest,
             CSignalsTest, PySignalsTest,
             )

    # Put the namespaces of the IO module we are testing oraz some useful mock
    # classes w the __dict__ of each test.
    mocks = (MockRawIO, MisbehavedRawIO, MockFileIO, CloseFailureIO,
             MockNonBlockWriterIO, MockUnseekableIO, MockRawIOWithoutRead)
    all_members = io.__all__ + ["IncrementalNewlineDecoder"]
    c_io_ns = {name : getattr(io, name) dla name w all_members}
    py_io_ns = {name : getattr(pyio, name) dla name w all_members}
    globs = globals()
    c_io_ns.update((x.__name__, globs["C" + x.__name__]) dla x w mocks)
    py_io_ns.update((x.__name__, globs["Py" + x.__name__]) dla x w mocks)
    # Avoid turning open into a bound method.
    py_io_ns["open"] = pyio.OpenWrapper
    dla test w tests:
        jeżeli test.__name__.startswith("C"):
            dla name, obj w c_io_ns.items():
                setattr(test, name, obj)
        albo_inaczej test.__name__.startswith("Py"):
            dla name, obj w py_io_ns.items():
                setattr(test, name, obj)

    suite = unittest.TestSuite([unittest.makeSuite(test) dla test w tests])
    zwróć suite

jeżeli __name__ == "__main__":
    unittest.main()
