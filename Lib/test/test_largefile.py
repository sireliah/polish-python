"""Test largefile support on system where this makes sense.
"""

zaimportuj os
zaimportuj stat
zaimportuj sys
zaimportuj unittest
z test.support zaimportuj TESTFN, requires, unlink
zaimportuj io  # C implementation of io
zaimportuj _pyio jako pyio # Python implementation of io

# size of file to create (>2GB; 2GB == 2147483648 bytes)
size = 2500000000

klasa LargeFileTest:
    """Test that each file function works jako expected dla large
    (i.e. > 2GB) files.
    """

    def setUp(self):
        jeżeli os.path.exists(TESTFN):
            mode = 'r+b'
        inaczej:
            mode = 'w+b'

        przy self.open(TESTFN, mode) jako f:
            current_size = os.fstat(f.fileno())[stat.ST_SIZE]
            jeżeli current_size == size+1:
                zwróć

            jeżeli current_size == 0:
                f.write(b'z')

            f.seek(0)
            f.seek(size)
            f.write(b'a')
            f.flush()
            self.assertEqual(os.fstat(f.fileno())[stat.ST_SIZE], size+1)

    @classmethod
    def tearDownClass(cls):
        przy cls.open(TESTFN, 'wb'):
            dalej
        jeżeli nie os.stat(TESTFN)[stat.ST_SIZE] == 0:
            podnieś cls.failureException('File was nie truncated by opening '
                                       'przy mode "wb"')

    def test_osstat(self):
        self.assertEqual(os.stat(TESTFN)[stat.ST_SIZE], size+1)

    def test_seek_read(self):
        przy self.open(TESTFN, 'rb') jako f:
            self.assertEqual(f.tell(), 0)
            self.assertEqual(f.read(1), b'z')
            self.assertEqual(f.tell(), 1)
            f.seek(0)
            self.assertEqual(f.tell(), 0)
            f.seek(0, 0)
            self.assertEqual(f.tell(), 0)
            f.seek(42)
            self.assertEqual(f.tell(), 42)
            f.seek(42, 0)
            self.assertEqual(f.tell(), 42)
            f.seek(42, 1)
            self.assertEqual(f.tell(), 84)
            f.seek(0, 1)
            self.assertEqual(f.tell(), 84)
            f.seek(0, 2)  # seek z the end
            self.assertEqual(f.tell(), size + 1 + 0)
            f.seek(-10, 2)
            self.assertEqual(f.tell(), size + 1 - 10)
            f.seek(-size-1, 2)
            self.assertEqual(f.tell(), 0)
            f.seek(size)
            self.assertEqual(f.tell(), size)
            # the 'a' that was written at the end of file above
            self.assertEqual(f.read(1), b'a')
            f.seek(-size-1, 1)
            self.assertEqual(f.read(1), b'z')
            self.assertEqual(f.tell(), 1)

    def test_lseek(self):
        przy self.open(TESTFN, 'rb') jako f:
            self.assertEqual(os.lseek(f.fileno(), 0, 0), 0)
            self.assertEqual(os.lseek(f.fileno(), 42, 0), 42)
            self.assertEqual(os.lseek(f.fileno(), 42, 1), 84)
            self.assertEqual(os.lseek(f.fileno(), 0, 1), 84)
            self.assertEqual(os.lseek(f.fileno(), 0, 2), size+1+0)
            self.assertEqual(os.lseek(f.fileno(), -10, 2), size+1-10)
            self.assertEqual(os.lseek(f.fileno(), -size-1, 2), 0)
            self.assertEqual(os.lseek(f.fileno(), size, 0), size)
            # the 'a' that was written at the end of file above
            self.assertEqual(f.read(1), b'a')

    def test_truncate(self):
        przy self.open(TESTFN, 'r+b') jako f:
            jeżeli nie hasattr(f, 'truncate'):
                podnieś unittest.SkipTest("open().truncate() nie available "
                                        "on this system")
            f.seek(0, 2)
            # inaczej we've lost track of the true size
            self.assertEqual(f.tell(), size+1)
            # Cut it back via seek + truncate przy no argument.
            newsize = size - 10
            f.seek(newsize)
            f.truncate()
            self.assertEqual(f.tell(), newsize)  # inaczej pointer moved
            f.seek(0, 2)
            self.assertEqual(f.tell(), newsize)  # inaczej wasn't truncated
            # Ensure that truncate(smaller than true size) shrinks
            # the file.
            newsize -= 1
            f.seek(42)
            f.truncate(newsize)
            self.assertEqual(f.tell(), 42)
            f.seek(0, 2)
            self.assertEqual(f.tell(), newsize)
            # XXX truncate(larger than true size) jest ill-defined
            # across platform; cut it waaaaay back
            f.seek(0)
            f.truncate(1)
            self.assertEqual(f.tell(), 0)       # inaczej pointer moved
            f.seek(0)
            self.assertEqual(len(f.read()), 1)  # inaczej wasn't truncated

    def test_seekable(self):
        # Issue #5016; seekable() can zwróć Nieprawda when the current position
        # jest negative when truncated to an int.
        dla pos w (2**31-1, 2**31, 2**31+1):
            przy self.open(TESTFN, 'rb') jako f:
                f.seek(pos)
                self.assertPrawda(f.seekable())

def setUpModule():
    spróbuj:
        zaimportuj signal
        # The default handler dla SIGXFSZ jest to abort the process.
        # By ignoring it, system calls exceeding the file size resource
        # limit will podnieś OSError instead of crashing the interpreter.
        signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
    wyjąwszy (ImportError, AttributeError):
        dalej

    # On Windows oraz Mac OSX this test comsumes large resources; It
    # takes a long time to build the >2GB file oraz takes >2GB of disk
    # space therefore the resource must be enabled to run this test.
    # If not, nothing after this line stanza will be executed.
    jeżeli sys.platform[:3] == 'win' albo sys.platform == 'darwin':
        requires('largefile',
                 'test requires %s bytes oraz a long time to run' % str(size))
    inaczej:
        # Only run jeżeli the current filesystem supports large files.
        # (Skip this test on Windows, since we now always support
        # large files.)
        f = open(TESTFN, 'wb', buffering=0)
        spróbuj:
            # 2**31 == 2147483648
            f.seek(2147483649)
            # Seeking jest nie enough of a test: you must write oraz flush, too!
            f.write(b'x')
            f.flush()
        wyjąwszy (OSError, OverflowError):
            podnieś unittest.SkipTest("filesystem does nie have "
                                    "largefile support")
        w_końcu:
            f.close()
            unlink(TESTFN)


klasa CLargeFileTest(LargeFileTest, unittest.TestCase):
    open = staticmethod(io.open)

klasa PyLargeFileTest(LargeFileTest, unittest.TestCase):
    open = staticmethod(pyio.open)

def tearDownModule():
    unlink(TESTFN)

jeżeli __name__ == '__main__':
    unittest.main()
