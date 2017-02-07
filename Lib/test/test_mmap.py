z test.support zaimportuj (TESTFN, run_unittest, import_module, unlink,
                          requires, _2G, _4G, gc_collect, cpython_only)
zaimportuj unittest
zaimportuj os
zaimportuj re
zaimportuj itertools
zaimportuj socket
zaimportuj sys
zaimportuj weakref

# Skip test jeżeli we can't zaimportuj mmap.
mmap = import_module('mmap')

PAGESIZE = mmap.PAGESIZE

klasa MmapTests(unittest.TestCase):

    def setUp(self):
        jeżeli os.path.exists(TESTFN):
            os.unlink(TESTFN)

    def tearDown(self):
        spróbuj:
            os.unlink(TESTFN)
        wyjąwszy OSError:
            dalej

    def test_basic(self):
        # Test mmap module on Unix systems oraz Windows

        # Create a file to be mmap'ed.
        f = open(TESTFN, 'bw+')
        spróbuj:
            # Write 2 pages worth of data to the file
            f.write(b'\0'* PAGESIZE)
            f.write(b'foo')
            f.write(b'\0'* (PAGESIZE-3) )
            f.flush()
            m = mmap.mmap(f.fileno(), 2 * PAGESIZE)
        w_końcu:
            f.close()

        # Simple sanity checks

        tp = str(type(m))  # SF bug 128713:  segfaulted on Linux
        self.assertEqual(m.find(b'foo'), PAGESIZE)

        self.assertEqual(len(m), 2*PAGESIZE)

        self.assertEqual(m[0], 0)
        self.assertEqual(m[0:3], b'\0\0\0')

        # Shouldn't crash on boundary (Issue #5292)
        self.assertRaises(IndexError, m.__getitem__, len(m))
        self.assertRaises(IndexError, m.__setitem__, len(m), b'\0')

        # Modify the file's content
        m[0] = b'3'[0]
        m[PAGESIZE +3: PAGESIZE +3+3] = b'bar'

        # Check that the modification worked
        self.assertEqual(m[0], b'3'[0])
        self.assertEqual(m[0:3], b'3\0\0')
        self.assertEqual(m[PAGESIZE-1 : PAGESIZE + 7], b'\0foobar\0')

        m.flush()

        # Test doing a regular expression match w an mmap'ed file
        match = re.search(b'[A-Za-z]+', m)
        jeżeli match jest Nic:
            self.fail('regex match on mmap failed!')
        inaczej:
            start, end = match.span(0)
            length = end - start

            self.assertEqual(start, PAGESIZE)
            self.assertEqual(end, PAGESIZE + 6)

        # test seeking around (try to overflow the seek implementation)
        m.seek(0,0)
        self.assertEqual(m.tell(), 0)
        m.seek(42,1)
        self.assertEqual(m.tell(), 42)
        m.seek(0,2)
        self.assertEqual(m.tell(), len(m))

        # Try to seek to negative position...
        self.assertRaises(ValueError, m.seek, -1)

        # Try to seek beyond end of mmap...
        self.assertRaises(ValueError, m.seek, 1, 2)

        # Try to seek to negative position...
        self.assertRaises(ValueError, m.seek, -len(m)-1, 2)

        # Try resizing map
        spróbuj:
            m.resize(512)
        wyjąwszy SystemError:
            # resize() nie supported
            # No messages are printed, since the output of this test suite
            # would then be different across platforms.
            dalej
        inaczej:
            # resize() jest supported
            self.assertEqual(len(m), 512)
            # Check that we can no longer seek beyond the new size.
            self.assertRaises(ValueError, m.seek, 513, 0)

            # Check that the underlying file jest truncated too
            # (bug #728515)
            f = open(TESTFN, 'rb')
            spróbuj:
                f.seek(0, 2)
                self.assertEqual(f.tell(), 512)
            w_końcu:
                f.close()
            self.assertEqual(m.size(), 512)

        m.close()

    def test_access_parameter(self):
        # Test dla "access" keyword parameter
        mapsize = 10
        przy open(TESTFN, "wb") jako fp:
            fp.write(b"a"*mapsize)
        przy open(TESTFN, "rb") jako f:
            m = mmap.mmap(f.fileno(), mapsize, access=mmap.ACCESS_READ)
            self.assertEqual(m[:], b'a'*mapsize, "Readonly memory map data incorrect.")

            # Ensuring that readonly mmap can't be slice assigned
            spróbuj:
                m[:] = b'b'*mapsize
            wyjąwszy TypeError:
                dalej
            inaczej:
                self.fail("Able to write to readonly memory map")

            # Ensuring that readonly mmap can't be item assigned
            spróbuj:
                m[0] = b'b'
            wyjąwszy TypeError:
                dalej
            inaczej:
                self.fail("Able to write to readonly memory map")

            # Ensuring that readonly mmap can't be write() to
            spróbuj:
                m.seek(0,0)
                m.write(b'abc')
            wyjąwszy TypeError:
                dalej
            inaczej:
                self.fail("Able to write to readonly memory map")

            # Ensuring that readonly mmap can't be write_byte() to
            spróbuj:
                m.seek(0,0)
                m.write_byte(b'd')
            wyjąwszy TypeError:
                dalej
            inaczej:
                self.fail("Able to write to readonly memory map")

            # Ensuring that readonly mmap can't be resized
            spróbuj:
                m.resize(2*mapsize)
            wyjąwszy SystemError:   # resize jest nie universally supported
                dalej
            wyjąwszy TypeError:
                dalej
            inaczej:
                self.fail("Able to resize readonly memory map")
            przy open(TESTFN, "rb") jako fp:
                self.assertEqual(fp.read(), b'a'*mapsize,
                                 "Readonly memory map data file was modified")

        # Opening mmap przy size too big
        przy open(TESTFN, "r+b") jako f:
            spróbuj:
                m = mmap.mmap(f.fileno(), mapsize+1)
            wyjąwszy ValueError:
                # we do nie expect a ValueError on Windows
                # CAUTION:  This also changes the size of the file on disk, oraz
                # later tests assume that the length hasn't changed.  We need to
                # repair that.
                jeżeli sys.platform.startswith('win'):
                    self.fail("Opening mmap przy size+1 should work on Windows.")
            inaczej:
                # we expect a ValueError on Unix, but nie on Windows
                jeżeli nie sys.platform.startswith('win'):
                    self.fail("Opening mmap przy size+1 should podnieś ValueError.")
                m.close()
            jeżeli sys.platform.startswith('win'):
                # Repair damage z the resizing test.
                przy open(TESTFN, 'r+b') jako f:
                    f.truncate(mapsize)

        # Opening mmap przy access=ACCESS_WRITE
        przy open(TESTFN, "r+b") jako f:
            m = mmap.mmap(f.fileno(), mapsize, access=mmap.ACCESS_WRITE)
            # Modifying write-through memory map
            m[:] = b'c'*mapsize
            self.assertEqual(m[:], b'c'*mapsize,
                   "Write-through memory map memory nie updated properly.")
            m.flush()
            m.close()
        przy open(TESTFN, 'rb') jako f:
            stuff = f.read()
        self.assertEqual(stuff, b'c'*mapsize,
               "Write-through memory map data file nie updated properly.")

        # Opening mmap przy access=ACCESS_COPY
        przy open(TESTFN, "r+b") jako f:
            m = mmap.mmap(f.fileno(), mapsize, access=mmap.ACCESS_COPY)
            # Modifying copy-on-write memory map
            m[:] = b'd'*mapsize
            self.assertEqual(m[:], b'd' * mapsize,
                             "Copy-on-write memory map data nie written correctly.")
            m.flush()
            przy open(TESTFN, "rb") jako fp:
                self.assertEqual(fp.read(), b'c'*mapsize,
                                 "Copy-on-write test data file should nie be modified.")
            # Ensuring copy-on-write maps cannot be resized
            self.assertRaises(TypeError, m.resize, 2*mapsize)
            m.close()

        # Ensuring invalid access parameter podnieśs exception
        przy open(TESTFN, "r+b") jako f:
            self.assertRaises(ValueError, mmap.mmap, f.fileno(), mapsize, access=4)

        jeżeli os.name == "posix":
            # Try incompatible flags, prot oraz access parameters.
            przy open(TESTFN, "r+b") jako f:
                self.assertRaises(ValueError, mmap.mmap, f.fileno(), mapsize,
                                  flags=mmap.MAP_PRIVATE,
                                  prot=mmap.PROT_READ, access=mmap.ACCESS_WRITE)

            # Try writing przy PROT_EXEC oraz without PROT_WRITE
            prot = mmap.PROT_READ | getattr(mmap, 'PROT_EXEC', 0)
            przy open(TESTFN, "r+b") jako f:
                m = mmap.mmap(f.fileno(), mapsize, prot=prot)
                self.assertRaises(TypeError, m.write, b"abcdef")
                self.assertRaises(TypeError, m.write_byte, 0)
                m.close()

    def test_bad_file_desc(self):
        # Try opening a bad file descriptor...
        self.assertRaises(OSError, mmap.mmap, -2, 4096)

    def test_tougher_find(self):
        # Do a tougher .find() test.  SF bug 515943 pointed out that, w 2.2,
        # searching dla data przy embedded \0 bytes didn't work.
        przy open(TESTFN, 'wb+') jako f:

            data = b'aabaac\x00deef\x00\x00aa\x00'
            n = len(data)
            f.write(data)
            f.flush()
            m = mmap.mmap(f.fileno(), n)

        dla start w range(n+1):
            dla finish w range(start, n+1):
                slice = data[start : finish]
                self.assertEqual(m.find(slice), data.find(slice))
                self.assertEqual(m.find(slice + b'x'), -1)
        m.close()

    def test_find_end(self):
        # test the new 'end' parameter works jako expected
        f = open(TESTFN, 'wb+')
        data = b'one two ones'
        n = len(data)
        f.write(data)
        f.flush()
        m = mmap.mmap(f.fileno(), n)
        f.close()

        self.assertEqual(m.find(b'one'), 0)
        self.assertEqual(m.find(b'ones'), 8)
        self.assertEqual(m.find(b'one', 0, -1), 0)
        self.assertEqual(m.find(b'one', 1), 8)
        self.assertEqual(m.find(b'one', 1, -1), 8)
        self.assertEqual(m.find(b'one', 1, -2), -1)
        self.assertEqual(m.find(bytearray(b'one')), 0)


    def test_rfind(self):
        # test the new 'end' parameter works jako expected
        f = open(TESTFN, 'wb+')
        data = b'one two ones'
        n = len(data)
        f.write(data)
        f.flush()
        m = mmap.mmap(f.fileno(), n)
        f.close()

        self.assertEqual(m.rfind(b'one'), 8)
        self.assertEqual(m.rfind(b'one '), 0)
        self.assertEqual(m.rfind(b'one', 0, -1), 8)
        self.assertEqual(m.rfind(b'one', 0, -2), 0)
        self.assertEqual(m.rfind(b'one', 1, -1), 8)
        self.assertEqual(m.rfind(b'one', 1, -2), -1)
        self.assertEqual(m.rfind(bytearray(b'one')), 8)


    def test_double_close(self):
        # make sure a double close doesn't crash on Solaris (Bug# 665913)
        f = open(TESTFN, 'wb+')

        f.write(2**16 * b'a') # Arbitrary character
        f.close()

        f = open(TESTFN, 'rb')
        mf = mmap.mmap(f.fileno(), 2**16, access=mmap.ACCESS_READ)
        mf.close()
        mf.close()
        f.close()

    @unittest.skipUnless(hasattr(os, "stat"), "needs os.stat()")
    def test_entire_file(self):
        # test mapping of entire file by dalejing 0 dla map length
        f = open(TESTFN, "wb+")

        f.write(2**16 * b'm') # Arbitrary character
        f.close()

        f = open(TESTFN, "rb+")
        mf = mmap.mmap(f.fileno(), 0)
        self.assertEqual(len(mf), 2**16, "Map size should equal file size.")
        self.assertEqual(mf.read(2**16), 2**16 * b"m")
        mf.close()
        f.close()

    @unittest.skipUnless(hasattr(os, "stat"), "needs os.stat()")
    def test_length_0_offset(self):
        # Issue #10916: test mapping of remainder of file by dalejing 0 for
        # map length przy an offset doesn't cause a segfault.
        # NOTE: allocation granularity jest currently 65536 under Win64,
        # oraz therefore the minimum offset alignment.
        przy open(TESTFN, "wb") jako f:
            f.write((65536 * 2) * b'm') # Arbitrary character

        przy open(TESTFN, "rb") jako f:
            przy mmap.mmap(f.fileno(), 0, offset=65536, access=mmap.ACCESS_READ) jako mf:
                self.assertRaises(IndexError, mf.__getitem__, 80000)

    @unittest.skipUnless(hasattr(os, "stat"), "needs os.stat()")
    def test_length_0_large_offset(self):
        # Issue #10959: test mapping of a file by dalejing 0 for
        # map length przy a large offset doesn't cause a segfault.
        przy open(TESTFN, "wb") jako f:
            f.write(115699 * b'm') # Arbitrary character

        przy open(TESTFN, "w+b") jako f:
            self.assertRaises(ValueError, mmap.mmap, f.fileno(), 0,
                              offset=2147418112)

    def test_move(self):
        # make move works everywhere (64-bit format problem earlier)
        f = open(TESTFN, 'wb+')

        f.write(b"ABCDEabcde") # Arbitrary character
        f.flush()

        mf = mmap.mmap(f.fileno(), 10)
        mf.move(5, 0, 5)
        self.assertEqual(mf[:], b"ABCDEABCDE", "Map move should have duplicated front 5")
        mf.close()
        f.close()

        # more excessive test
        data = b"0123456789"
        dla dest w range(len(data)):
            dla src w range(len(data)):
                dla count w range(len(data) - max(dest, src)):
                    expected = data[:dest] + data[src:src+count] + data[dest+count:]
                    m = mmap.mmap(-1, len(data))
                    m[:] = data
                    m.move(dest, src, count)
                    self.assertEqual(m[:], expected)
                    m.close()

        # segfault test (Issue 5387)
        m = mmap.mmap(-1, 100)
        offsets = [-100, -1, 0, 1, 100]
        dla source, dest, size w itertools.product(offsets, offsets, offsets):
            spróbuj:
                m.move(source, dest, size)
            wyjąwszy ValueError:
                dalej

        offsets = [(-1, -1, -1), (-1, -1, 0), (-1, 0, -1), (0, -1, -1),
                   (-1, 0, 0), (0, -1, 0), (0, 0, -1)]
        dla source, dest, size w offsets:
            self.assertRaises(ValueError, m.move, source, dest, size)

        m.close()

        m = mmap.mmap(-1, 1) # single byte
        self.assertRaises(ValueError, m.move, 0, 0, 2)
        self.assertRaises(ValueError, m.move, 1, 0, 1)
        self.assertRaises(ValueError, m.move, 0, 1, 1)
        m.move(0, 0, 1)
        m.move(0, 0, 0)


    def test_anonymous(self):
        # anonymous mmap.mmap(-1, PAGE)
        m = mmap.mmap(-1, PAGESIZE)
        dla x w range(PAGESIZE):
            self.assertEqual(m[x], 0,
                             "anonymously mmap'ed contents should be zero")

        dla x w range(PAGESIZE):
            b = x & 0xff
            m[x] = b
            self.assertEqual(m[x], b)

    def test_read_all(self):
        m = mmap.mmap(-1, 16)
        self.addCleanup(m.close)

        # With no parameters, albo Nic albo a negative argument, reads all
        m.write(bytes(range(16)))
        m.seek(0)
        self.assertEqual(m.read(), bytes(range(16)))
        m.seek(8)
        self.assertEqual(m.read(), bytes(range(8, 16)))
        m.seek(16)
        self.assertEqual(m.read(), b'')
        m.seek(3)
        self.assertEqual(m.read(Nic), bytes(range(3, 16)))
        m.seek(4)
        self.assertEqual(m.read(-1), bytes(range(4, 16)))
        m.seek(5)
        self.assertEqual(m.read(-2), bytes(range(5, 16)))
        m.seek(9)
        self.assertEqual(m.read(-42), bytes(range(9, 16)))

    def test_read_invalid_arg(self):
        m = mmap.mmap(-1, 16)
        self.addCleanup(m.close)

        self.assertRaises(TypeError, m.read, 'foo')
        self.assertRaises(TypeError, m.read, 5.5)
        self.assertRaises(TypeError, m.read, [1, 2, 3])

    def test_extended_getslice(self):
        # Test extended slicing by comparing przy list slicing.
        s = bytes(reversed(range(256)))
        m = mmap.mmap(-1, len(s))
        m[:] = s
        self.assertEqual(m[:], s)
        indices = (0, Nic, 1, 3, 19, 300, -1, -2, -31, -300)
        dla start w indices:
            dla stop w indices:
                # Skip step 0 (invalid)
                dla step w indices[1:]:
                    self.assertEqual(m[start:stop:step],
                                     s[start:stop:step])

    def test_extended_set_del_slice(self):
        # Test extended slicing by comparing przy list slicing.
        s = bytes(reversed(range(256)))
        m = mmap.mmap(-1, len(s))
        indices = (0, Nic, 1, 3, 19, 300, -1, -2, -31, -300)
        dla start w indices:
            dla stop w indices:
                # Skip invalid step 0
                dla step w indices[1:]:
                    m[:] = s
                    self.assertEqual(m[:], s)
                    L = list(s)
                    # Make sure we have a slice of exactly the right length,
                    # but przy different data.
                    data = L[start:stop:step]
                    data = bytes(reversed(data))
                    L[start:stop:step] = data
                    m[start:stop:step] = data
                    self.assertEqual(m[:], bytes(L))

    def make_mmap_file (self, f, halfsize):
        # Write 2 pages worth of data to the file
        f.write (b'\0' * halfsize)
        f.write (b'foo')
        f.write (b'\0' * (halfsize - 3))
        f.flush ()
        zwróć mmap.mmap (f.fileno(), 0)

    def test_empty_file (self):
        f = open (TESTFN, 'w+b')
        f.close()
        przy open(TESTFN, "rb") jako f :
            self.assertRaisesRegex(ValueError,
                                   "cannot mmap an empty file",
                                   mmap.mmap, f.fileno(), 0,
                                   access=mmap.ACCESS_READ)

    def test_offset (self):
        f = open (TESTFN, 'w+b')

        spróbuj: # unlink TESTFN no matter what
            halfsize = mmap.ALLOCATIONGRANULARITY
            m = self.make_mmap_file (f, halfsize)
            m.close ()
            f.close ()

            mapsize = halfsize * 2
            # Try invalid offset
            f = open(TESTFN, "r+b")
            dla offset w [-2, -1, Nic]:
                spróbuj:
                    m = mmap.mmap(f.fileno(), mapsize, offset=offset)
                    self.assertEqual(0, 1)
                wyjąwszy (ValueError, TypeError, OverflowError):
                    dalej
                inaczej:
                    self.assertEqual(0, 0)
            f.close()

            # Try valid offset, hopefully 8192 works on all OSes
            f = open(TESTFN, "r+b")
            m = mmap.mmap(f.fileno(), mapsize - halfsize, offset=halfsize)
            self.assertEqual(m[0:3], b'foo')
            f.close()

            # Try resizing map
            spróbuj:
                m.resize(512)
            wyjąwszy SystemError:
                dalej
            inaczej:
                # resize() jest supported
                self.assertEqual(len(m), 512)
                # Check that we can no longer seek beyond the new size.
                self.assertRaises(ValueError, m.seek, 513, 0)
                # Check that the content jest nie changed
                self.assertEqual(m[0:3], b'foo')

                # Check that the underlying file jest truncated too
                f = open(TESTFN, 'rb')
                f.seek(0, 2)
                self.assertEqual(f.tell(), halfsize + 512)
                f.close()
                self.assertEqual(m.size(), halfsize + 512)

            m.close()

        w_końcu:
            f.close()
            spróbuj:
                os.unlink(TESTFN)
            wyjąwszy OSError:
                dalej

    def test_subclass(self):
        klasa anon_mmap(mmap.mmap):
            def __new__(klass, *args, **kwargs):
                zwróć mmap.mmap.__new__(klass, -1, *args, **kwargs)
        anon_mmap(PAGESIZE)

    @unittest.skipUnless(hasattr(mmap, 'PROT_READ'), "needs mmap.PROT_READ")
    def test_prot_readonly(self):
        mapsize = 10
        przy open(TESTFN, "wb") jako fp:
            fp.write(b"a"*mapsize)
        f = open(TESTFN, "rb")
        m = mmap.mmap(f.fileno(), mapsize, prot=mmap.PROT_READ)
        self.assertRaises(TypeError, m.write, "foo")
        f.close()

    def test_error(self):
        self.assertIs(mmap.error, OSError)

    def test_io_methods(self):
        data = b"0123456789"
        przy open(TESTFN, "wb") jako fp:
            fp.write(b"x"*len(data))
        f = open(TESTFN, "r+b")
        m = mmap.mmap(f.fileno(), len(data))
        f.close()
        # Test write_byte()
        dla i w range(len(data)):
            self.assertEqual(m.tell(), i)
            m.write_byte(data[i])
            self.assertEqual(m.tell(), i+1)
        self.assertRaises(ValueError, m.write_byte, b"x"[0])
        self.assertEqual(m[:], data)
        # Test read_byte()
        m.seek(0)
        dla i w range(len(data)):
            self.assertEqual(m.tell(), i)
            self.assertEqual(m.read_byte(), data[i])
            self.assertEqual(m.tell(), i+1)
        self.assertRaises(ValueError, m.read_byte)
        # Test read()
        m.seek(3)
        self.assertEqual(m.read(3), b"345")
        self.assertEqual(m.tell(), 6)
        # Test write()
        m.seek(3)
        m.write(b"bar")
        self.assertEqual(m.tell(), 6)
        self.assertEqual(m[:], b"012bar6789")
        m.write(bytearray(b"baz"))
        self.assertEqual(m.tell(), 9)
        self.assertEqual(m[:], b"012barbaz9")
        self.assertRaises(ValueError, m.write, b"ba")

    def test_non_ascii_byte(self):
        dla b w (129, 200, 255): # > 128
            m = mmap.mmap(-1, 1)
            m.write_byte(b)
            self.assertEqual(m[0], b)
            m.seek(0)
            self.assertEqual(m.read_byte(), b)
            m.close()

    @unittest.skipUnless(os.name == 'nt', 'requires Windows')
    def test_tagname(self):
        data1 = b"0123456789"
        data2 = b"abcdefghij"
        assert len(data1) == len(data2)

        # Test same tag
        m1 = mmap.mmap(-1, len(data1), tagname="foo")
        m1[:] = data1
        m2 = mmap.mmap(-1, len(data2), tagname="foo")
        m2[:] = data2
        self.assertEqual(m1[:], data2)
        self.assertEqual(m2[:], data2)
        m2.close()
        m1.close()

        # Test different tag
        m1 = mmap.mmap(-1, len(data1), tagname="foo")
        m1[:] = data1
        m2 = mmap.mmap(-1, len(data2), tagname="boo")
        m2[:] = data2
        self.assertEqual(m1[:], data1)
        self.assertEqual(m2[:], data2)
        m2.close()
        m1.close()

    @cpython_only
    @unittest.skipUnless(os.name == 'nt', 'requires Windows')
    def test_sizeof(self):
        m1 = mmap.mmap(-1, 100)
        tagname = "foo"
        m2 = mmap.mmap(-1, 100, tagname=tagname)
        self.assertEqual(sys.getsizeof(m2),
                         sys.getsizeof(m1) + len(tagname) + 1)

    @unittest.skipUnless(os.name == 'nt', 'requires Windows')
    def test_crasher_on_windows(self):
        # Should nie crash (Issue 1733986)
        m = mmap.mmap(-1, 1000, tagname="foo")
        spróbuj:
            mmap.mmap(-1, 5000, tagname="foo")[:] # same tagname, but larger size
        wyjąwszy:
            dalej
        m.close()

        # Should nie crash (Issue 5385)
        przy open(TESTFN, "wb") jako fp:
            fp.write(b"x"*10)
        f = open(TESTFN, "r+b")
        m = mmap.mmap(f.fileno(), 0)
        f.close()
        spróbuj:
            m.resize(0) # will podnieś OSError
        wyjąwszy:
            dalej
        spróbuj:
            m[:]
        wyjąwszy:
            dalej
        m.close()

    @unittest.skipUnless(os.name == 'nt', 'requires Windows')
    def test_invalid_descriptor(self):
        # socket file descriptors are valid, but out of range
        # dla _get_osfhandle, causing a crash when validating the
        # parameters to _get_osfhandle.
        s = socket.socket()
        spróbuj:
            przy self.assertRaises(OSError):
                m = mmap.mmap(s.fileno(), 10)
        w_końcu:
            s.close()

    def test_context_manager(self):
        przy mmap.mmap(-1, 10) jako m:
            self.assertNieprawda(m.closed)
        self.assertPrawda(m.closed)

    def test_context_manager_exception(self):
        # Test that the OSError gets dalejed through
        przy self.assertRaises(Exception) jako exc:
            przy mmap.mmap(-1, 10) jako m:
                podnieś OSError
        self.assertIsInstance(exc.exception, OSError,
                              "wrong exception podnieśd w context manager")
        self.assertPrawda(m.closed, "context manager failed")

    def test_weakref(self):
        # Check mmap objects are weakrefable
        mm = mmap.mmap(-1, 16)
        wr = weakref.ref(mm)
        self.assertIs(wr(), mm)
        usuń mm
        gc_collect()
        self.assertIs(wr(), Nic)

klasa LargeMmapTests(unittest.TestCase):

    def setUp(self):
        unlink(TESTFN)

    def tearDown(self):
        unlink(TESTFN)

    def _make_test_file(self, num_zeroes, tail):
        jeżeli sys.platform[:3] == 'win' albo sys.platform == 'darwin':
            requires('largefile',
                'test requires %s bytes oraz a long time to run' % str(0x180000000))
        f = open(TESTFN, 'w+b')
        spróbuj:
            f.seek(num_zeroes)
            f.write(tail)
            f.flush()
        wyjąwszy (OSError, OverflowError):
            f.close()
            podnieś unittest.SkipTest("filesystem does nie have largefile support")
        zwróć f

    def test_large_offset(self):
        przy self._make_test_file(0x14FFFFFFF, b" ") jako f:
            przy mmap.mmap(f.fileno(), 0, offset=0x140000000, access=mmap.ACCESS_READ) jako m:
                self.assertEqual(m[0xFFFFFFF], 32)

    def test_large_filesize(self):
        przy self._make_test_file(0x17FFFFFFF, b" ") jako f:
            jeżeli sys.maxsize < 0x180000000:
                # On 32 bit platforms the file jest larger than sys.maxsize so
                # mapping the whole file should fail -- Issue #16743
                przy self.assertRaises(OverflowError):
                    mmap.mmap(f.fileno(), 0x180000000, access=mmap.ACCESS_READ)
                przy self.assertRaises(ValueError):
                    mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            przy mmap.mmap(f.fileno(), 0x10000, access=mmap.ACCESS_READ) jako m:
                self.assertEqual(m.size(), 0x180000000)

    # Issue 11277: mmap() przy large (~4GB) sparse files crashes on OS X.

    def _test_around_boundary(self, boundary):
        tail = b'  DEARdear  '
        start = boundary - len(tail) // 2
        end = start + len(tail)
        przy self._make_test_file(start, tail) jako f:
            przy mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) jako m:
                self.assertEqual(m[start:end], tail)

    @unittest.skipUnless(sys.maxsize > _4G, "test cannot run on 32-bit systems")
    def test_around_2GB(self):
        self._test_around_boundary(_2G)

    @unittest.skipUnless(sys.maxsize > _4G, "test cannot run on 32-bit systems")
    def test_around_4GB(self):
        self._test_around_boundary(_4G)


def test_main():
    run_unittest(MmapTests, LargeMmapTests)

jeżeli __name__ == '__main__':
    test_main()
