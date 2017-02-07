zaimportuj contextlib
zaimportuj io
zaimportuj os
zaimportuj sys
zaimportuj importlib.util
zaimportuj time
zaimportuj struct
zaimportuj zipfile
zaimportuj unittest


z tempfile zaimportuj TemporaryFile
z random zaimportuj randint, random, getrandbits

z test.support zaimportuj (TESTFN, findfile, unlink, rmtree,
                          requires_zlib, requires_bz2, requires_lzma,
                          captured_stdout, check_warnings)

TESTFN2 = TESTFN + "2"
TESTFNDIR = TESTFN + "d"
FIXEDTEST_SIZE = 1000
DATAFILES_DIR = 'zipfile_datafiles'

SMALL_TEST_DATA = [('_ziptest1', '1q2w3e4r5t'),
                   ('ziptest2dir/_ziptest2', 'qawsedrftg'),
                   ('ziptest2dir/ziptest3dir/_ziptest3', 'azsxdcfvgb'),
                   ('ziptest2dir/ziptest3dir/ziptest4dir/_ziptest3', '6y7u8i9o0p')]

def getrandbytes(size):
    zwróć getrandbits(8 * size).to_bytes(size, 'little')

def get_files(test):
    uzyskaj TESTFN2
    przy TemporaryFile() jako f:
        uzyskaj f
        test.assertNieprawda(f.closed)
    przy io.BytesIO() jako f:
        uzyskaj f
        test.assertNieprawda(f.closed)

def openU(zipfp, fn):
    przy check_warnings(('', DeprecationWarning)):
        zwróć zipfp.open(fn, 'rU')

klasa AbstractTestsWithSourceFile:
    @classmethod
    def setUpClass(cls):
        cls.line_gen = [bytes("Zipfile test line %d. random float: %f\n" %
                              (i, random()), "ascii")
                        dla i w range(FIXEDTEST_SIZE)]
        cls.data = b''.join(cls.line_gen)

    def setUp(self):
        # Make a source file przy some lines
        przy open(TESTFN, "wb") jako fp:
            fp.write(self.data)

    def make_test_archive(self, f, compression):
        # Create the ZIP archive
        przy zipfile.ZipFile(f, "w", compression) jako zipfp:
            zipfp.write(TESTFN, "another.name")
            zipfp.write(TESTFN, TESTFN)
            zipfp.writestr("strfile", self.data)

    def zip_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        przy zipfile.ZipFile(f, "r", compression) jako zipfp:
            self.assertEqual(zipfp.read(TESTFN), self.data)
            self.assertEqual(zipfp.read("another.name"), self.data)
            self.assertEqual(zipfp.read("strfile"), self.data)

            # Print the ZIP directory
            fp = io.StringIO()
            zipfp.printdir(file=fp)
            directory = fp.getvalue()
            lines = directory.splitlines()
            self.assertEqual(len(lines), 4) # Number of files + header

            self.assertIn('File Name', lines[0])
            self.assertIn('Modified', lines[0])
            self.assertIn('Size', lines[0])

            fn, date, time_, size = lines[1].split()
            self.assertEqual(fn, 'another.name')
            self.assertPrawda(time.strptime(date, '%Y-%m-%d'))
            self.assertPrawda(time.strptime(time_, '%H:%M:%S'))
            self.assertEqual(size, str(len(self.data)))

            # Check the namelist
            names = zipfp.namelist()
            self.assertEqual(len(names), 3)
            self.assertIn(TESTFN, names)
            self.assertIn("another.name", names)
            self.assertIn("strfile", names)

            # Check infolist
            infos = zipfp.infolist()
            names = [i.filename dla i w infos]
            self.assertEqual(len(names), 3)
            self.assertIn(TESTFN, names)
            self.assertIn("another.name", names)
            self.assertIn("strfile", names)
            dla i w infos:
                self.assertEqual(i.file_size, len(self.data))

            # check getinfo
            dla nm w (TESTFN, "another.name", "strfile"):
                info = zipfp.getinfo(nm)
                self.assertEqual(info.filename, nm)
                self.assertEqual(info.file_size, len(self.data))

            # Check that testzip doesn't podnieś an exception
            zipfp.testzip()

    def test_basic(self):
        dla f w get_files(self):
            self.zip_test(f, self.compression)

    def zip_open_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        przy zipfile.ZipFile(f, "r", compression) jako zipfp:
            zipdata1 = []
            przy zipfp.open(TESTFN) jako zipopen1:
                dopóki Prawda:
                    read_data = zipopen1.read(256)
                    jeżeli nie read_data:
                        przerwij
                    zipdata1.append(read_data)

            zipdata2 = []
            przy zipfp.open("another.name") jako zipopen2:
                dopóki Prawda:
                    read_data = zipopen2.read(256)
                    jeżeli nie read_data:
                        przerwij
                    zipdata2.append(read_data)

            self.assertEqual(b''.join(zipdata1), self.data)
            self.assertEqual(b''.join(zipdata2), self.data)

    def test_open(self):
        dla f w get_files(self):
            self.zip_open_test(f, self.compression)

    def zip_random_open_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        przy zipfile.ZipFile(f, "r", compression) jako zipfp:
            zipdata1 = []
            przy zipfp.open(TESTFN) jako zipopen1:
                dopóki Prawda:
                    read_data = zipopen1.read(randint(1, 1024))
                    jeżeli nie read_data:
                        przerwij
                    zipdata1.append(read_data)

            self.assertEqual(b''.join(zipdata1), self.data)

    def test_random_open(self):
        dla f w get_files(self):
            self.zip_random_open_test(f, self.compression)

    def zip_read1_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        przy zipfile.ZipFile(f, "r") jako zipfp, \
             zipfp.open(TESTFN) jako zipopen:
            zipdata = []
            dopóki Prawda:
                read_data = zipopen.read1(-1)
                jeżeli nie read_data:
                    przerwij
                zipdata.append(read_data)

        self.assertEqual(b''.join(zipdata), self.data)

    def test_read1(self):
        dla f w get_files(self):
            self.zip_read1_test(f, self.compression)

    def zip_read1_10_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        przy zipfile.ZipFile(f, "r") jako zipfp, \
             zipfp.open(TESTFN) jako zipopen:
            zipdata = []
            dopóki Prawda:
                read_data = zipopen.read1(10)
                self.assertLessEqual(len(read_data), 10)
                jeżeli nie read_data:
                    przerwij
                zipdata.append(read_data)

        self.assertEqual(b''.join(zipdata), self.data)

    def test_read1_10(self):
        dla f w get_files(self):
            self.zip_read1_10_test(f, self.compression)

    def zip_readline_read_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        przy zipfile.ZipFile(f, "r") jako zipfp, \
             zipfp.open(TESTFN) jako zipopen:
            data = b''
            dopóki Prawda:
                read = zipopen.readline()
                jeżeli nie read:
                    przerwij
                data += read

                read = zipopen.read(100)
                jeżeli nie read:
                    przerwij
                data += read

        self.assertEqual(data, self.data)

    def test_readline_read(self):
        # Issue #7610: calls to readline() interleaved przy calls to read().
        dla f w get_files(self):
            self.zip_readline_read_test(f, self.compression)

    def zip_readline_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        przy zipfile.ZipFile(f, "r") jako zipfp:
            przy zipfp.open(TESTFN) jako zipopen:
                dla line w self.line_gen:
                    linedata = zipopen.readline()
                    self.assertEqual(linedata, line)

    def test_readline(self):
        dla f w get_files(self):
            self.zip_readline_test(f, self.compression)

    def zip_readlines_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        przy zipfile.ZipFile(f, "r") jako zipfp:
            przy zipfp.open(TESTFN) jako zipopen:
                ziplines = zipopen.readlines()
            dla line, zipline w zip(self.line_gen, ziplines):
                self.assertEqual(zipline, line)

    def test_readlines(self):
        dla f w get_files(self):
            self.zip_readlines_test(f, self.compression)

    def zip_iterlines_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        przy zipfile.ZipFile(f, "r") jako zipfp:
            przy zipfp.open(TESTFN) jako zipopen:
                dla line, zipline w zip(self.line_gen, zipopen):
                    self.assertEqual(zipline, line)

    def test_iterlines(self):
        dla f w get_files(self):
            self.zip_iterlines_test(f, self.compression)

    def test_low_compression(self):
        """Check dla cases where compressed data jest larger than original."""
        # Create the ZIP archive
        przy zipfile.ZipFile(TESTFN2, "w", self.compression) jako zipfp:
            zipfp.writestr("strfile", '12')

        # Get an open object dla strfile
        przy zipfile.ZipFile(TESTFN2, "r", self.compression) jako zipfp:
            przy zipfp.open("strfile") jako openobj:
                self.assertEqual(openobj.read(1), b'1')
                self.assertEqual(openobj.read(1), b'2')

    def test_writestr_compression(self):
        zipfp = zipfile.ZipFile(TESTFN2, "w")
        zipfp.writestr("b.txt", "hello world", compress_type=self.compression)
        info = zipfp.getinfo('b.txt')
        self.assertEqual(info.compress_type, self.compression)

    def test_read_return_size(self):
        # Issue #9837: ZipExtFile.read() shouldn't zwróć more bytes
        # than requested.
        dla test_size w (1, 4095, 4096, 4097, 16384):
            file_size = test_size + 1
            junk = getrandbytes(file_size)
            przy zipfile.ZipFile(io.BytesIO(), "w", self.compression) jako zipf:
                zipf.writestr('foo', junk)
                przy zipf.open('foo', 'r') jako fp:
                    buf = fp.read(test_size)
                    self.assertEqual(len(buf), test_size)

    def test_truncated_zipfile(self):
        fp = io.BytesIO()
        przy zipfile.ZipFile(fp, mode='w') jako zipf:
            zipf.writestr('strfile', self.data, compress_type=self.compression)
            end_offset = fp.tell()
        zipfiledata = fp.getvalue()

        fp = io.BytesIO(zipfiledata)
        przy zipfile.ZipFile(fp) jako zipf:
            przy zipf.open('strfile') jako zipopen:
                fp.truncate(end_offset - 20)
                przy self.assertRaises(EOFError):
                    zipopen.read()

        fp = io.BytesIO(zipfiledata)
        przy zipfile.ZipFile(fp) jako zipf:
            przy zipf.open('strfile') jako zipopen:
                fp.truncate(end_offset - 20)
                przy self.assertRaises(EOFError):
                    dopóki zipopen.read(100):
                        dalej

        fp = io.BytesIO(zipfiledata)
        przy zipfile.ZipFile(fp) jako zipf:
            przy zipf.open('strfile') jako zipopen:
                fp.truncate(end_offset - 20)
                przy self.assertRaises(EOFError):
                    dopóki zipopen.read1(100):
                        dalej

    def test_repr(self):
        fname = 'file.name'
        dla f w get_files(self):
            przy zipfile.ZipFile(f, 'w', self.compression) jako zipfp:
                zipfp.write(TESTFN, fname)
                r = repr(zipfp)
                self.assertIn("mode='w'", r)

            przy zipfile.ZipFile(f, 'r') jako zipfp:
                r = repr(zipfp)
                jeżeli isinstance(f, str):
                    self.assertIn('filename=%r' % f, r)
                inaczej:
                    self.assertIn('file=%r' % f, r)
                self.assertIn("mode='r'", r)
                r = repr(zipfp.getinfo(fname))
                self.assertIn('filename=%r' % fname, r)
                self.assertIn('filemode=', r)
                self.assertIn('file_size=', r)
                jeżeli self.compression != zipfile.ZIP_STORED:
                    self.assertIn('compress_type=', r)
                    self.assertIn('compress_size=', r)
                przy zipfp.open(fname) jako zipopen:
                    r = repr(zipopen)
                    self.assertIn('name=%r' % fname, r)
                    self.assertIn("mode='r'", r)
                    jeżeli self.compression != zipfile.ZIP_STORED:
                        self.assertIn('compress_type=', r)
                self.assertIn('[closed]', repr(zipopen))
            self.assertIn('[closed]', repr(zipfp))

    def tearDown(self):
        unlink(TESTFN)
        unlink(TESTFN2)


klasa StoredTestsWithSourceFile(AbstractTestsWithSourceFile,
                                unittest.TestCase):
    compression = zipfile.ZIP_STORED
    test_low_compression = Nic

    def zip_test_writestr_permissions(self, f, compression):
        # Make sure that writestr creates files przy mode 0600,
        # when it jest dalejed a name rather than a ZipInfo instance.

        self.make_test_archive(f, compression)
        przy zipfile.ZipFile(f, "r") jako zipfp:
            zinfo = zipfp.getinfo('strfile')
            self.assertEqual(zinfo.external_attr, 0o600 << 16)

    def test_writestr_permissions(self):
        dla f w get_files(self):
            self.zip_test_writestr_permissions(f, zipfile.ZIP_STORED)

    def test_absolute_arcnames(self):
        przy zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED) jako zipfp:
            zipfp.write(TESTFN, "/absolute")

        przy zipfile.ZipFile(TESTFN2, "r", zipfile.ZIP_STORED) jako zipfp:
            self.assertEqual(zipfp.namelist(), ["absolute"])

    def test_append_to_zip_file(self):
        """Test appending to an existing zipfile."""
        przy zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED) jako zipfp:
            zipfp.write(TESTFN, TESTFN)

        przy zipfile.ZipFile(TESTFN2, "a", zipfile.ZIP_STORED) jako zipfp:
            zipfp.writestr("strfile", self.data)
            self.assertEqual(zipfp.namelist(), [TESTFN, "strfile"])

    def test_append_to_non_zip_file(self):
        """Test appending to an existing file that jest nie a zipfile."""
        # NOTE: this test fails jeżeli len(d) < 22 because of the first
        # line "fpin.seek(-22, 2)" w _EndRecData
        data = b'I am nie a ZipFile!'*10
        przy open(TESTFN2, 'wb') jako f:
            f.write(data)

        przy zipfile.ZipFile(TESTFN2, "a", zipfile.ZIP_STORED) jako zipfp:
            zipfp.write(TESTFN, TESTFN)

        przy open(TESTFN2, 'rb') jako f:
            f.seek(len(data))
            przy zipfile.ZipFile(f, "r") jako zipfp:
                self.assertEqual(zipfp.namelist(), [TESTFN])

    def test_ignores_newline_at_end(self):
        przy zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED) jako zipfp:
            zipfp.write(TESTFN, TESTFN)
        przy open(TESTFN2, 'a') jako f:
            f.write("\r\n\00\00\00")
        przy zipfile.ZipFile(TESTFN2, "r") jako zipfp:
            self.assertIsInstance(zipfp, zipfile.ZipFile)

    def test_ignores_stuff_appended_past_comments(self):
        przy zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED) jako zipfp:
            zipfp.comment = b"this jest a comment"
            zipfp.write(TESTFN, TESTFN)
        przy open(TESTFN2, 'a') jako f:
            f.write("abcdef\r\n")
        przy zipfile.ZipFile(TESTFN2, "r") jako zipfp:
            self.assertIsInstance(zipfp, zipfile.ZipFile)
            self.assertEqual(zipfp.comment, b"this jest a comment")

    def test_write_default_name(self):
        """Check that calling ZipFile.write without arcname specified
        produces the expected result."""
        przy zipfile.ZipFile(TESTFN2, "w") jako zipfp:
            zipfp.write(TESTFN)
            przy open(TESTFN, "rb") jako f:
                self.assertEqual(zipfp.read(TESTFN), f.read())

    def test_write_to_readonly(self):
        """Check that trying to call write() on a readonly ZipFile object
        podnieśs a RuntimeError."""
        przy zipfile.ZipFile(TESTFN2, mode="w") jako zipfp:
            zipfp.writestr("somefile.txt", "bogus")

        przy zipfile.ZipFile(TESTFN2, mode="r") jako zipfp:
            self.assertRaises(RuntimeError, zipfp.write, TESTFN)

    def test_add_file_before_1980(self):
        # Set atime oraz mtime to 1970-01-01
        os.utime(TESTFN, (0, 0))
        przy zipfile.ZipFile(TESTFN2, "w") jako zipfp:
            self.assertRaises(ValueError, zipfp.write, TESTFN)


@requires_zlib
klasa DeflateTestsWithSourceFile(AbstractTestsWithSourceFile,
                                 unittest.TestCase):
    compression = zipfile.ZIP_DEFLATED

    def test_per_file_compression(self):
        """Check that files within a Zip archive can have different
        compression options."""
        przy zipfile.ZipFile(TESTFN2, "w") jako zipfp:
            zipfp.write(TESTFN, 'storeme', zipfile.ZIP_STORED)
            zipfp.write(TESTFN, 'deflateme', zipfile.ZIP_DEFLATED)
            sinfo = zipfp.getinfo('storeme')
            dinfo = zipfp.getinfo('deflateme')
            self.assertEqual(sinfo.compress_type, zipfile.ZIP_STORED)
            self.assertEqual(dinfo.compress_type, zipfile.ZIP_DEFLATED)

@requires_bz2
klasa Bzip2TestsWithSourceFile(AbstractTestsWithSourceFile,
                               unittest.TestCase):
    compression = zipfile.ZIP_BZIP2

@requires_lzma
klasa LzmaTestsWithSourceFile(AbstractTestsWithSourceFile,
                              unittest.TestCase):
    compression = zipfile.ZIP_LZMA


klasa AbstractTestZip64InSmallFiles:
    # These tests test the ZIP64 functionality without using large files,
    # see test_zipfile64 dla proper tests.

    @classmethod
    def setUpClass(cls):
        line_gen = (bytes("Test of zipfile line %d." % i, "ascii")
                    dla i w range(0, FIXEDTEST_SIZE))
        cls.data = b'\n'.join(line_gen)

    def setUp(self):
        self._limit = zipfile.ZIP64_LIMIT
        self._filecount_limit = zipfile.ZIP_FILECOUNT_LIMIT
        zipfile.ZIP64_LIMIT = 1000
        zipfile.ZIP_FILECOUNT_LIMIT = 9

        # Make a source file przy some lines
        przy open(TESTFN, "wb") jako fp:
            fp.write(self.data)

    def zip_test(self, f, compression):
        # Create the ZIP archive
        przy zipfile.ZipFile(f, "w", compression, allowZip64=Prawda) jako zipfp:
            zipfp.write(TESTFN, "another.name")
            zipfp.write(TESTFN, TESTFN)
            zipfp.writestr("strfile", self.data)

        # Read the ZIP archive
        przy zipfile.ZipFile(f, "r", compression) jako zipfp:
            self.assertEqual(zipfp.read(TESTFN), self.data)
            self.assertEqual(zipfp.read("another.name"), self.data)
            self.assertEqual(zipfp.read("strfile"), self.data)

            # Print the ZIP directory
            fp = io.StringIO()
            zipfp.printdir(fp)

            directory = fp.getvalue()
            lines = directory.splitlines()
            self.assertEqual(len(lines), 4) # Number of files + header

            self.assertIn('File Name', lines[0])
            self.assertIn('Modified', lines[0])
            self.assertIn('Size', lines[0])

            fn, date, time_, size = lines[1].split()
            self.assertEqual(fn, 'another.name')
            self.assertPrawda(time.strptime(date, '%Y-%m-%d'))
            self.assertPrawda(time.strptime(time_, '%H:%M:%S'))
            self.assertEqual(size, str(len(self.data)))

            # Check the namelist
            names = zipfp.namelist()
            self.assertEqual(len(names), 3)
            self.assertIn(TESTFN, names)
            self.assertIn("another.name", names)
            self.assertIn("strfile", names)

            # Check infolist
            infos = zipfp.infolist()
            names = [i.filename dla i w infos]
            self.assertEqual(len(names), 3)
            self.assertIn(TESTFN, names)
            self.assertIn("another.name", names)
            self.assertIn("strfile", names)
            dla i w infos:
                self.assertEqual(i.file_size, len(self.data))

            # check getinfo
            dla nm w (TESTFN, "another.name", "strfile"):
                info = zipfp.getinfo(nm)
                self.assertEqual(info.filename, nm)
                self.assertEqual(info.file_size, len(self.data))

            # Check that testzip doesn't podnieś an exception
            zipfp.testzip()

    def test_basic(self):
        dla f w get_files(self):
            self.zip_test(f, self.compression)

    def test_too_many_files(self):
        # This test checks that more than 64k files can be added to an archive,
        # oraz that the resulting archive can be read properly by ZipFile
        zipf = zipfile.ZipFile(TESTFN, "w", self.compression,
                               allowZip64=Prawda)
        zipf.debug = 100
        numfiles = 15
        dla i w range(numfiles):
            zipf.writestr("foo%08d" % i, "%d" % (i**3 % 57))
        self.assertEqual(len(zipf.namelist()), numfiles)
        zipf.close()

        zipf2 = zipfile.ZipFile(TESTFN, "r", self.compression)
        self.assertEqual(len(zipf2.namelist()), numfiles)
        dla i w range(numfiles):
            content = zipf2.read("foo%08d" % i).decode('ascii')
            self.assertEqual(content, "%d" % (i**3 % 57))
        zipf2.close()

    def test_too_many_files_append(self):
        zipf = zipfile.ZipFile(TESTFN, "w", self.compression,
                               allowZip64=Nieprawda)
        zipf.debug = 100
        numfiles = 9
        dla i w range(numfiles):
            zipf.writestr("foo%08d" % i, "%d" % (i**3 % 57))
        self.assertEqual(len(zipf.namelist()), numfiles)
        przy self.assertRaises(zipfile.LargeZipFile):
            zipf.writestr("foo%08d" % numfiles, b'')
        self.assertEqual(len(zipf.namelist()), numfiles)
        zipf.close()

        zipf = zipfile.ZipFile(TESTFN, "a", self.compression,
                               allowZip64=Nieprawda)
        zipf.debug = 100
        self.assertEqual(len(zipf.namelist()), numfiles)
        przy self.assertRaises(zipfile.LargeZipFile):
            zipf.writestr("foo%08d" % numfiles, b'')
        self.assertEqual(len(zipf.namelist()), numfiles)
        zipf.close()

        zipf = zipfile.ZipFile(TESTFN, "a", self.compression,
                               allowZip64=Prawda)
        zipf.debug = 100
        self.assertEqual(len(zipf.namelist()), numfiles)
        numfiles2 = 15
        dla i w range(numfiles, numfiles2):
            zipf.writestr("foo%08d" % i, "%d" % (i**3 % 57))
        self.assertEqual(len(zipf.namelist()), numfiles2)
        zipf.close()

        zipf2 = zipfile.ZipFile(TESTFN, "r", self.compression)
        self.assertEqual(len(zipf2.namelist()), numfiles2)
        dla i w range(numfiles2):
            content = zipf2.read("foo%08d" % i).decode('ascii')
            self.assertEqual(content, "%d" % (i**3 % 57))
        zipf2.close()

    def tearDown(self):
        zipfile.ZIP64_LIMIT = self._limit
        zipfile.ZIP_FILECOUNT_LIMIT = self._filecount_limit
        unlink(TESTFN)
        unlink(TESTFN2)


klasa StoredTestZip64InSmallFiles(AbstractTestZip64InSmallFiles,
                                  unittest.TestCase):
    compression = zipfile.ZIP_STORED

    def large_file_exception_test(self, f, compression):
        przy zipfile.ZipFile(f, "w", compression, allowZip64=Nieprawda) jako zipfp:
            self.assertRaises(zipfile.LargeZipFile,
                              zipfp.write, TESTFN, "another.name")

    def large_file_exception_test2(self, f, compression):
        przy zipfile.ZipFile(f, "w", compression, allowZip64=Nieprawda) jako zipfp:
            self.assertRaises(zipfile.LargeZipFile,
                              zipfp.writestr, "another.name", self.data)

    def test_large_file_exception(self):
        dla f w get_files(self):
            self.large_file_exception_test(f, zipfile.ZIP_STORED)
            self.large_file_exception_test2(f, zipfile.ZIP_STORED)

    def test_absolute_arcnames(self):
        przy zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED,
                             allowZip64=Prawda) jako zipfp:
            zipfp.write(TESTFN, "/absolute")

        przy zipfile.ZipFile(TESTFN2, "r", zipfile.ZIP_STORED) jako zipfp:
            self.assertEqual(zipfp.namelist(), ["absolute"])

@requires_zlib
klasa DeflateTestZip64InSmallFiles(AbstractTestZip64InSmallFiles,
                                   unittest.TestCase):
    compression = zipfile.ZIP_DEFLATED

@requires_bz2
klasa Bzip2TestZip64InSmallFiles(AbstractTestZip64InSmallFiles,
                                 unittest.TestCase):
    compression = zipfile.ZIP_BZIP2

@requires_lzma
klasa LzmaTestZip64InSmallFiles(AbstractTestZip64InSmallFiles,
                                unittest.TestCase):
    compression = zipfile.ZIP_LZMA


klasa PyZipFileTests(unittest.TestCase):
    def assertCompiledIn(self, name, namelist):
        jeżeli name + 'o' nie w namelist:
            self.assertIn(name + 'c', namelist)

    def requiresWriteAccess(self, path):
        # effective_ids unavailable on windows
        jeżeli nie os.access(path, os.W_OK,
                         effective_ids=os.access w os.supports_effective_ids):
            self.skipTest('requires write access to the installed location')

    def test_write_pyfile(self):
        self.requiresWriteAccess(os.path.dirname(__file__))
        przy TemporaryFile() jako t, zipfile.PyZipFile(t, "w") jako zipfp:
            fn = __file__
            jeżeli fn.endswith('.pyc'):
                path_split = fn.split(os.sep)
                jeżeli os.altsep jest nie Nic:
                    path_split.extend(fn.split(os.altsep))
                jeżeli '__pycache__' w path_split:
                    fn = importlib.util.source_from_cache(fn)
                inaczej:
                    fn = fn[:-1]

            zipfp.writepy(fn)

            bn = os.path.basename(fn)
            self.assertNotIn(bn, zipfp.namelist())
            self.assertCompiledIn(bn, zipfp.namelist())

        przy TemporaryFile() jako t, zipfile.PyZipFile(t, "w") jako zipfp:
            fn = __file__
            jeżeli fn.endswith('.pyc'):
                fn = fn[:-1]

            zipfp.writepy(fn, "testpackage")

            bn = "%s/%s" % ("testpackage", os.path.basename(fn))
            self.assertNotIn(bn, zipfp.namelist())
            self.assertCompiledIn(bn, zipfp.namelist())

    def test_write_python_package(self):
        zaimportuj email
        packagedir = os.path.dirname(email.__file__)
        self.requiresWriteAccess(packagedir)

        przy TemporaryFile() jako t, zipfile.PyZipFile(t, "w") jako zipfp:
            zipfp.writepy(packagedir)

            # Check dla a couple of modules at different levels of the
            # hierarchy
            names = zipfp.namelist()
            self.assertCompiledIn('email/__init__.py', names)
            self.assertCompiledIn('email/mime/text.py', names)

    def test_write_filtered_python_package(self):
        zaimportuj test
        packagedir = os.path.dirname(test.__file__)
        self.requiresWriteAccess(packagedir)

        przy TemporaryFile() jako t, zipfile.PyZipFile(t, "w") jako zipfp:

            # first make sure that the test folder gives error messages
            # (on the badsyntax_... files)
            przy captured_stdout() jako reportSIO:
                zipfp.writepy(packagedir)
            reportStr = reportSIO.getvalue()
            self.assertPrawda('SyntaxError' w reportStr)

            # then check that the filter works on the whole package
            przy captured_stdout() jako reportSIO:
                zipfp.writepy(packagedir, filterfunc=lambda whatever: Nieprawda)
            reportStr = reportSIO.getvalue()
            self.assertPrawda('SyntaxError' nie w reportStr)

            # then check that the filter works on individual files
            def filter(path):
                zwróć nie os.path.basename(path).startswith("bad")
            przy captured_stdout() jako reportSIO, self.assertWarns(UserWarning):
                zipfp.writepy(packagedir, filterfunc=filter)
            reportStr = reportSIO.getvalue()
            jeżeli reportStr:
                print(reportStr)
            self.assertPrawda('SyntaxError' nie w reportStr)

    def test_write_with_optimization(self):
        zaimportuj email
        packagedir = os.path.dirname(email.__file__)
        self.requiresWriteAccess(packagedir)
        optlevel = 1 jeżeli __debug__ inaczej 0
        ext = '.pyc'

        przy TemporaryFile() jako t, \
             zipfile.PyZipFile(t, "w", optimize=optlevel) jako zipfp:
            zipfp.writepy(packagedir)

            names = zipfp.namelist()
            self.assertIn('email/__init__' + ext, names)
            self.assertIn('email/mime/text' + ext, names)

    def test_write_python_directory(self):
        os.mkdir(TESTFN2)
        spróbuj:
            przy open(os.path.join(TESTFN2, "mod1.py"), "w") jako fp:
                fp.write("print(42)\n")

            przy open(os.path.join(TESTFN2, "mod2.py"), "w") jako fp:
                fp.write("print(42 * 42)\n")

            przy open(os.path.join(TESTFN2, "mod2.txt"), "w") jako fp:
                fp.write("bla bla bla\n")

            przy TemporaryFile() jako t, zipfile.PyZipFile(t, "w") jako zipfp:
                zipfp.writepy(TESTFN2)

                names = zipfp.namelist()
                self.assertCompiledIn('mod1.py', names)
                self.assertCompiledIn('mod2.py', names)
                self.assertNotIn('mod2.txt', names)

        w_końcu:
            rmtree(TESTFN2)

    def test_write_python_directory_filtered(self):
        os.mkdir(TESTFN2)
        spróbuj:
            przy open(os.path.join(TESTFN2, "mod1.py"), "w") jako fp:
                fp.write("print(42)\n")

            przy open(os.path.join(TESTFN2, "mod2.py"), "w") jako fp:
                fp.write("print(42 * 42)\n")

            przy TemporaryFile() jako t, zipfile.PyZipFile(t, "w") jako zipfp:
                zipfp.writepy(TESTFN2, filterfunc=lambda fn:
                                                  nie fn.endswith('mod2.py'))

                names = zipfp.namelist()
                self.assertCompiledIn('mod1.py', names)
                self.assertNotIn('mod2.py', names)

        w_końcu:
            rmtree(TESTFN2)

    def test_write_non_pyfile(self):
        przy TemporaryFile() jako t, zipfile.PyZipFile(t, "w") jako zipfp:
            przy open(TESTFN, 'w') jako f:
                f.write('most definitely nie a python file')
            self.assertRaises(RuntimeError, zipfp.writepy, TESTFN)
            unlink(TESTFN)

    def test_write_pyfile_bad_syntax(self):
        os.mkdir(TESTFN2)
        spróbuj:
            przy open(os.path.join(TESTFN2, "mod1.py"), "w") jako fp:
                fp.write("Bad syntax w python file\n")

            przy TemporaryFile() jako t, zipfile.PyZipFile(t, "w") jako zipfp:
                # syntax errors are printed to stdout
                przy captured_stdout() jako s:
                    zipfp.writepy(os.path.join(TESTFN2, "mod1.py"))

                self.assertIn("SyntaxError", s.getvalue())

                # jako it will nie have compiled the python file, it will
                # include the .py file nie .pyc
                names = zipfp.namelist()
                self.assertIn('mod1.py', names)
                self.assertNotIn('mod1.pyc', names)

        w_końcu:
            rmtree(TESTFN2)


klasa ExtractTests(unittest.TestCase):
    def test_extract(self):
        przy zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED) jako zipfp:
            dla fpath, fdata w SMALL_TEST_DATA:
                zipfp.writestr(fpath, fdata)

        przy zipfile.ZipFile(TESTFN2, "r") jako zipfp:
            dla fpath, fdata w SMALL_TEST_DATA:
                writtenfile = zipfp.extract(fpath)

                # make sure it was written to the right place
                correctfile = os.path.join(os.getcwd(), fpath)
                correctfile = os.path.normpath(correctfile)

                self.assertEqual(writtenfile, correctfile)

                # make sure correct data jest w correct file
                przy open(writtenfile, "rb") jako f:
                    self.assertEqual(fdata.encode(), f.read())

                unlink(writtenfile)

        # remove the test file subdirectories
        rmtree(os.path.join(os.getcwd(), 'ziptest2dir'))

    def test_extract_all(self):
        przy zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED) jako zipfp:
            dla fpath, fdata w SMALL_TEST_DATA:
                zipfp.writestr(fpath, fdata)

        przy zipfile.ZipFile(TESTFN2, "r") jako zipfp:
            zipfp.extractall()
            dla fpath, fdata w SMALL_TEST_DATA:
                outfile = os.path.join(os.getcwd(), fpath)

                przy open(outfile, "rb") jako f:
                    self.assertEqual(fdata.encode(), f.read())

                unlink(outfile)

        # remove the test file subdirectories
        rmtree(os.path.join(os.getcwd(), 'ziptest2dir'))

    def check_file(self, filename, content):
        self.assertPrawda(os.path.isfile(filename))
        przy open(filename, 'rb') jako f:
            self.assertEqual(f.read(), content)

    def test_sanitize_windows_name(self):
        san = zipfile.ZipFile._sanitize_windows_name
        # Passing pathsep w allows this test to work regardless of platform.
        self.assertEqual(san(r',,?,C:,foo,bar/z', ','), r'_,C_,foo,bar/z')
        self.assertEqual(san(r'a\b,c<d>e|f"g?h*i', ','), r'a\b,c_d_e_f_g_h_i')
        self.assertEqual(san('../../foo../../ba..r', '/'), r'foo/ba..r')

    def test_extract_hackers_arcnames_common_cases(self):
        common_hacknames = [
            ('../foo/bar', 'foo/bar'),
            ('foo/../bar', 'foo/bar'),
            ('foo/../../bar', 'foo/bar'),
            ('foo/bar/..', 'foo/bar'),
            ('./../foo/bar', 'foo/bar'),
            ('/foo/bar', 'foo/bar'),
            ('/foo/../bar', 'foo/bar'),
            ('/foo/../../bar', 'foo/bar'),
        ]
        self._test_extract_hackers_arcnames(common_hacknames)

    @unittest.skipIf(os.path.sep != '\\', 'Requires \\ jako path separator.')
    def test_extract_hackers_arcnames_windows_only(self):
        """Test combination of path fixing oraz windows name sanitization."""
        windows_hacknames = [
            (r'..\foo\bar', 'foo/bar'),
            (r'..\/foo\/bar', 'foo/bar'),
            (r'foo/\..\/bar', 'foo/bar'),
            (r'foo\/../\bar', 'foo/bar'),
            (r'C:foo/bar', 'foo/bar'),
            (r'C:/foo/bar', 'foo/bar'),
            (r'C://foo/bar', 'foo/bar'),
            (r'C:\foo\bar', 'foo/bar'),
            (r'//conky/mountpoint/foo/bar', 'foo/bar'),
            (r'\\conky\mountpoint\foo\bar', 'foo/bar'),
            (r'///conky/mountpoint/foo/bar', 'conky/mountpoint/foo/bar'),
            (r'\\\conky\mountpoint\foo\bar', 'conky/mountpoint/foo/bar'),
            (r'//conky//mountpoint/foo/bar', 'conky/mountpoint/foo/bar'),
            (r'\\conky\\mountpoint\foo\bar', 'conky/mountpoint/foo/bar'),
            (r'//?/C:/foo/bar', 'foo/bar'),
            (r'\\?\C:\foo\bar', 'foo/bar'),
            (r'C:/../C:/foo/bar', 'C_/foo/bar'),
            (r'a:b\c<d>e|f"g?h*i', 'b/c_d_e_f_g_h_i'),
            ('../../foo../../ba..r', 'foo/ba..r'),
        ]
        self._test_extract_hackers_arcnames(windows_hacknames)

    @unittest.skipIf(os.path.sep != '/', r'Requires / jako path separator.')
    def test_extract_hackers_arcnames_posix_only(self):
        posix_hacknames = [
            ('//foo/bar', 'foo/bar'),
            ('../../foo../../ba..r', 'foo../ba..r'),
            (r'foo/..\bar', r'foo/..\bar'),
        ]
        self._test_extract_hackers_arcnames(posix_hacknames)

    def _test_extract_hackers_arcnames(self, hacknames):
        dla arcname, fixedname w hacknames:
            content = b'foobar' + arcname.encode()
            przy zipfile.ZipFile(TESTFN2, 'w', zipfile.ZIP_STORED) jako zipfp:
                zinfo = zipfile.ZipInfo()
                # preserve backslashes
                zinfo.filename = arcname
                zinfo.external_attr = 0o600 << 16
                zipfp.writestr(zinfo, content)

            arcname = arcname.replace(os.sep, "/")
            targetpath = os.path.join('target', 'subdir', 'subsub')
            correctfile = os.path.join(targetpath, *fixedname.split('/'))

            przy zipfile.ZipFile(TESTFN2, 'r') jako zipfp:
                writtenfile = zipfp.extract(arcname, targetpath)
                self.assertEqual(writtenfile, correctfile,
                                 msg='extract %r: %r != %r' %
                                 (arcname, writtenfile, correctfile))
            self.check_file(correctfile, content)
            rmtree('target')

            przy zipfile.ZipFile(TESTFN2, 'r') jako zipfp:
                zipfp.extractall(targetpath)
            self.check_file(correctfile, content)
            rmtree('target')

            correctfile = os.path.join(os.getcwd(), *fixedname.split('/'))

            przy zipfile.ZipFile(TESTFN2, 'r') jako zipfp:
                writtenfile = zipfp.extract(arcname)
                self.assertEqual(writtenfile, correctfile,
                                 msg="extract %r" % arcname)
            self.check_file(correctfile, content)
            rmtree(fixedname.split('/')[0])

            przy zipfile.ZipFile(TESTFN2, 'r') jako zipfp:
                zipfp.extractall()
            self.check_file(correctfile, content)
            rmtree(fixedname.split('/')[0])

            unlink(TESTFN2)


klasa OtherTests(unittest.TestCase):
    def test_open_via_zip_info(self):
        # Create the ZIP archive
        przy zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED) jako zipfp:
            zipfp.writestr("name", "foo")
            przy self.assertWarns(UserWarning):
                zipfp.writestr("name", "bar")
            self.assertEqual(zipfp.namelist(), ["name"] * 2)

        przy zipfile.ZipFile(TESTFN2, "r") jako zipfp:
            infos = zipfp.infolist()
            data = b""
            dla info w infos:
                przy zipfp.open(info) jako zipopen:
                    data += zipopen.read()
            self.assertIn(data, {b"foobar", b"barfoo"})
            data = b""
            dla info w infos:
                data += zipfp.read(info)
            self.assertIn(data, {b"foobar", b"barfoo"})

    def test_universal_deprecation(self):
        f = io.BytesIO()
        przy zipfile.ZipFile(f, "w") jako zipfp:
            zipfp.writestr('spam.txt', b'ababagalamaga')

        przy zipfile.ZipFile(f, "r") jako zipfp:
            dla mode w 'U', 'rU':
                przy self.assertWarns(DeprecationWarning):
                    zipopen = zipfp.open('spam.txt', mode)
                zipopen.close()

    def test_universal_readaheads(self):
        f = io.BytesIO()

        data = b'a\r\n' * 16 * 1024
        przy zipfile.ZipFile(f, 'w', zipfile.ZIP_STORED) jako zipfp:
            zipfp.writestr(TESTFN, data)

        data2 = b''
        przy zipfile.ZipFile(f, 'r') jako zipfp, \
             openU(zipfp, TESTFN) jako zipopen:
            dla line w zipopen:
                data2 += line

        self.assertEqual(data, data2.replace(b'\n', b'\r\n'))

    def test_writestr_extended_local_header_issue1202(self):
        przy zipfile.ZipFile(TESTFN2, 'w') jako orig_zip:
            dla data w 'abcdefghijklmnop':
                zinfo = zipfile.ZipInfo(data)
                zinfo.flag_bits |= 0x08  # Include an extended local header.
                orig_zip.writestr(zinfo, data)

    def test_close(self):
        """Check that the zipfile jest closed after the 'with' block."""
        przy zipfile.ZipFile(TESTFN2, "w") jako zipfp:
            dla fpath, fdata w SMALL_TEST_DATA:
                zipfp.writestr(fpath, fdata)
                self.assertIsNotNic(zipfp.fp, 'zipfp jest nie open')
        self.assertIsNic(zipfp.fp, 'zipfp jest nie closed')

        przy zipfile.ZipFile(TESTFN2, "r") jako zipfp:
            self.assertIsNotNic(zipfp.fp, 'zipfp jest nie open')
        self.assertIsNic(zipfp.fp, 'zipfp jest nie closed')

    def test_close_on_exception(self):
        """Check that the zipfile jest closed jeżeli an exception jest podnieśd w the
        'with' block."""
        przy zipfile.ZipFile(TESTFN2, "w") jako zipfp:
            dla fpath, fdata w SMALL_TEST_DATA:
                zipfp.writestr(fpath, fdata)

        spróbuj:
            przy zipfile.ZipFile(TESTFN2, "r") jako zipfp2:
                podnieś zipfile.BadZipFile()
        wyjąwszy zipfile.BadZipFile:
            self.assertIsNic(zipfp2.fp, 'zipfp jest nie closed')

    def test_unsupported_version(self):
        # File has an extract_version of 120
        data = (b'PK\x03\x04x\x00\x00\x00\x00\x00!p\xa1@\x00\x00\x00\x00\x00\x00'
                b'\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00xPK\x01\x02x\x03x\x00\x00\x00\x00'
                b'\x00!p\xa1@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00'
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x01\x00\x00\x00\x00xPK\x05\x06'
                b'\x00\x00\x00\x00\x01\x00\x01\x00/\x00\x00\x00\x1f\x00\x00\x00\x00\x00')

        self.assertRaises(NotImplementedError, zipfile.ZipFile,
                          io.BytesIO(data), 'r')

    @requires_zlib
    def test_read_unicode_filenames(self):
        # bug #10801
        fname = findfile('zip_cp437_header.zip')
        przy zipfile.ZipFile(fname) jako zipfp:
            dla name w zipfp.namelist():
                zipfp.open(name).close()

    def test_write_unicode_filenames(self):
        przy zipfile.ZipFile(TESTFN, "w") jako zf:
            zf.writestr("foo.txt", "Test dla unicode filename")
            zf.writestr("\xf6.txt", "Test dla unicode filename")
            self.assertIsInstance(zf.infolist()[0].filename, str)

        przy zipfile.ZipFile(TESTFN, "r") jako zf:
            self.assertEqual(zf.filelist[0].filename, "foo.txt")
            self.assertEqual(zf.filelist[1].filename, "\xf6.txt")

    def test_exclusive_create_zip_file(self):
        """Test exclusive creating a new zipfile."""
        unlink(TESTFN2)
        filename = 'testfile.txt'
        content = b'hello, world. this jest some content.'
        przy zipfile.ZipFile(TESTFN2, "x", zipfile.ZIP_STORED) jako zipfp:
            zipfp.writestr(filename, content)
        przy self.assertRaises(FileExistsError):
            zipfile.ZipFile(TESTFN2, "x", zipfile.ZIP_STORED)
        przy zipfile.ZipFile(TESTFN2, "r") jako zipfp:
            self.assertEqual(zipfp.namelist(), [filename])
            self.assertEqual(zipfp.read(filename), content)

    def test_create_non_existent_file_for_append(self):
        jeżeli os.path.exists(TESTFN):
            os.unlink(TESTFN)

        filename = 'testfile.txt'
        content = b'hello, world. this jest some content.'

        spróbuj:
            przy zipfile.ZipFile(TESTFN, 'a') jako zf:
                zf.writestr(filename, content)
        wyjąwszy OSError:
            self.fail('Could nie append data to a non-existent zip file.')

        self.assertPrawda(os.path.exists(TESTFN))

        przy zipfile.ZipFile(TESTFN, 'r') jako zf:
            self.assertEqual(zf.read(filename), content)

    def test_close_erroneous_file(self):
        # This test checks that the ZipFile constructor closes the file object
        # it opens jeżeli there's an error w the file.  If it doesn't, the
        # traceback holds a reference to the ZipFile object and, indirectly,
        # the file object.
        # On Windows, this causes the os.unlink() call to fail because the
        # underlying file jest still open.  This jest SF bug #412214.
        #
        przy open(TESTFN, "w") jako fp:
            fp.write("this jest nie a legal zip file\n")
        spróbuj:
            zf = zipfile.ZipFile(TESTFN)
        wyjąwszy zipfile.BadZipFile:
            dalej

    def test_is_zip_erroneous_file(self):
        """Check that is_zipfile() correctly identifies non-zip files."""
        # - dalejing a filename
        przy open(TESTFN, "w") jako fp:
            fp.write("this jest nie a legal zip file\n")
        self.assertNieprawda(zipfile.is_zipfile(TESTFN))
        # - dalejing a file object
        przy open(TESTFN, "rb") jako fp:
            self.assertNieprawda(zipfile.is_zipfile(fp))
        # - dalejing a file-like object
        fp = io.BytesIO()
        fp.write(b"this jest nie a legal zip file\n")
        self.assertNieprawda(zipfile.is_zipfile(fp))
        fp.seek(0, 0)
        self.assertNieprawda(zipfile.is_zipfile(fp))

    def test_damaged_zipfile(self):
        """Check that zipfiles przy missing bytes at the end podnieś BadZipFile."""
        # - Create a valid zip file
        fp = io.BytesIO()
        przy zipfile.ZipFile(fp, mode="w") jako zipf:
            zipf.writestr("foo.txt", b"O, dla a Muse of Fire!")
        zipfiledata = fp.getvalue()

        # - Now create copies of it missing the last N bytes oraz make sure
        #   a BadZipFile exception jest podnieśd when we try to open it
        dla N w range(len(zipfiledata)):
            fp = io.BytesIO(zipfiledata[:N])
            self.assertRaises(zipfile.BadZipFile, zipfile.ZipFile, fp)

    def test_is_zip_valid_file(self):
        """Check that is_zipfile() correctly identifies zip files."""
        # - dalejing a filename
        przy zipfile.ZipFile(TESTFN, mode="w") jako zipf:
            zipf.writestr("foo.txt", b"O, dla a Muse of Fire!")

        self.assertPrawda(zipfile.is_zipfile(TESTFN))
        # - dalejing a file object
        przy open(TESTFN, "rb") jako fp:
            self.assertPrawda(zipfile.is_zipfile(fp))
            fp.seek(0, 0)
            zip_contents = fp.read()
        # - dalejing a file-like object
        fp = io.BytesIO()
        fp.write(zip_contents)
        self.assertPrawda(zipfile.is_zipfile(fp))
        fp.seek(0, 0)
        self.assertPrawda(zipfile.is_zipfile(fp))

    def test_non_existent_file_raises_OSError(self):
        # make sure we don't podnieś an AttributeError when a partially-constructed
        # ZipFile instance jest finalized; this tests dla regression on SF tracker
        # bug #403871.

        # The bug we're testing dla caused an AttributeError to be podnieśd
        # when a ZipFile instance was created dla a file that did nie
        # exist; the .fp member was nie initialized but was needed by the
        # __del__() method.  Since the AttributeError jest w the __del__(),
        # it jest ignored, but the user should be sufficiently annoyed by
        # the message on the output that regression will be noticed
        # quickly.
        self.assertRaises(OSError, zipfile.ZipFile, TESTFN)

    def test_empty_file_raises_BadZipFile(self):
        f = open(TESTFN, 'w')
        f.close()
        self.assertRaises(zipfile.BadZipFile, zipfile.ZipFile, TESTFN)

        przy open(TESTFN, 'w') jako fp:
            fp.write("short file")
        self.assertRaises(zipfile.BadZipFile, zipfile.ZipFile, TESTFN)

    def test_closed_zip_raises_RuntimeError(self):
        """Verify that testzip() doesn't swallow inappropriate exceptions."""
        data = io.BytesIO()
        przy zipfile.ZipFile(data, mode="w") jako zipf:
            zipf.writestr("foo.txt", "O, dla a Muse of Fire!")

        # This jest correct; calling .read on a closed ZipFile should podnieś
        # a RuntimeError, oraz so should calling .testzip.  An earlier
        # version of .testzip would swallow this exception (and any other)
        # oraz report that the first file w the archive was corrupt.
        self.assertRaises(RuntimeError, zipf.read, "foo.txt")
        self.assertRaises(RuntimeError, zipf.open, "foo.txt")
        self.assertRaises(RuntimeError, zipf.testzip)
        self.assertRaises(RuntimeError, zipf.writestr, "bogus.txt", "bogus")
        przy open(TESTFN, 'w') jako f:
            f.write('zipfile test data')
        self.assertRaises(RuntimeError, zipf.write, TESTFN)

    def test_bad_constructor_mode(self):
        """Check that bad modes dalejed to ZipFile constructor are caught."""
        self.assertRaises(RuntimeError, zipfile.ZipFile, TESTFN, "q")

    def test_bad_open_mode(self):
        """Check that bad modes dalejed to ZipFile.open are caught."""
        przy zipfile.ZipFile(TESTFN, mode="w") jako zipf:
            zipf.writestr("foo.txt", "O, dla a Muse of Fire!")

        przy zipfile.ZipFile(TESTFN, mode="r") jako zipf:
        # read the data to make sure the file jest there
            zipf.read("foo.txt")
            self.assertRaises(RuntimeError, zipf.open, "foo.txt", "q")

    def test_read0(self):
        """Check that calling read(0) on a ZipExtFile object returns an empty
        string oraz doesn't advance file pointer."""
        przy zipfile.ZipFile(TESTFN, mode="w") jako zipf:
            zipf.writestr("foo.txt", "O, dla a Muse of Fire!")
            # read the data to make sure the file jest there
            przy zipf.open("foo.txt") jako f:
                dla i w range(FIXEDTEST_SIZE):
                    self.assertEqual(f.read(0), b'')

                self.assertEqual(f.read(), b"O, dla a Muse of Fire!")

    def test_open_non_existent_item(self):
        """Check that attempting to call open() dla an item that doesn't
        exist w the archive podnieśs a RuntimeError."""
        przy zipfile.ZipFile(TESTFN, mode="w") jako zipf:
            self.assertRaises(KeyError, zipf.open, "foo.txt", "r")

    def test_bad_compression_mode(self):
        """Check that bad compression methods dalejed to ZipFile.open are
        caught."""
        self.assertRaises(RuntimeError, zipfile.ZipFile, TESTFN, "w", -1)

    def test_unsupported_compression(self):
        # data jest declared jako shrunk, but actually deflated
        data = (b'PK\x03\x04.\x00\x00\x00\x01\x00\xe4C\xa1@\x00\x00\x00'
                b'\x00\x02\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00x\x03\x00PK\x01'
                b'\x02.\x03.\x00\x00\x00\x01\x00\xe4C\xa1@\x00\x00\x00\x00\x02\x00\x00'
                b'\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                b'\x80\x01\x00\x00\x00\x00xPK\x05\x06\x00\x00\x00\x00\x01\x00\x01\x00'
                b'/\x00\x00\x00!\x00\x00\x00\x00\x00')
        przy zipfile.ZipFile(io.BytesIO(data), 'r') jako zipf:
            self.assertRaises(NotImplementedError, zipf.open, 'x')

    def test_null_byte_in_filename(self):
        """Check that a filename containing a null byte jest properly
        terminated."""
        przy zipfile.ZipFile(TESTFN, mode="w") jako zipf:
            zipf.writestr("foo.txt\x00qqq", b"O, dla a Muse of Fire!")
            self.assertEqual(zipf.namelist(), ['foo.txt'])

    def test_struct_sizes(self):
        """Check that ZIP internal structure sizes are calculated correctly."""
        self.assertEqual(zipfile.sizeEndCentDir, 22)
        self.assertEqual(zipfile.sizeCentralDir, 46)
        self.assertEqual(zipfile.sizeEndCentDir64, 56)
        self.assertEqual(zipfile.sizeEndCentDir64Locator, 20)

    def test_comments(self):
        """Check that comments on the archive are handled properly."""

        # check default comment jest empty
        przy zipfile.ZipFile(TESTFN, mode="w") jako zipf:
            self.assertEqual(zipf.comment, b'')
            zipf.writestr("foo.txt", "O, dla a Muse of Fire!")

        przy zipfile.ZipFile(TESTFN, mode="r") jako zipfr:
            self.assertEqual(zipfr.comment, b'')

        # check a simple short comment
        comment = b'Bravely taking to his feet, he beat a very brave retreat.'
        przy zipfile.ZipFile(TESTFN, mode="w") jako zipf:
            zipf.comment = comment
            zipf.writestr("foo.txt", "O, dla a Muse of Fire!")
        przy zipfile.ZipFile(TESTFN, mode="r") jako zipfr:
            self.assertEqual(zipf.comment, comment)

        # check a comment of max length
        comment2 = ''.join(['%d' % (i**3 % 10) dla i w range((1 << 16)-1)])
        comment2 = comment2.encode("ascii")
        przy zipfile.ZipFile(TESTFN, mode="w") jako zipf:
            zipf.comment = comment2
            zipf.writestr("foo.txt", "O, dla a Muse of Fire!")

        przy zipfile.ZipFile(TESTFN, mode="r") jako zipfr:
            self.assertEqual(zipfr.comment, comment2)

        # check a comment that jest too long jest truncated
        przy zipfile.ZipFile(TESTFN, mode="w") jako zipf:
            przy self.assertWarns(UserWarning):
                zipf.comment = comment2 + b'oops'
            zipf.writestr("foo.txt", "O, dla a Muse of Fire!")
        przy zipfile.ZipFile(TESTFN, mode="r") jako zipfr:
            self.assertEqual(zipfr.comment, comment2)

        # check that comments are correctly modified w append mode
        przy zipfile.ZipFile(TESTFN,mode="w") jako zipf:
            zipf.comment = b"original comment"
            zipf.writestr("foo.txt", "O, dla a Muse of Fire!")
        przy zipfile.ZipFile(TESTFN,mode="a") jako zipf:
            zipf.comment = b"an updated comment"
        przy zipfile.ZipFile(TESTFN,mode="r") jako zipf:
            self.assertEqual(zipf.comment, b"an updated comment")

        # check that comments are correctly shortened w append mode
        przy zipfile.ZipFile(TESTFN,mode="w") jako zipf:
            zipf.comment = b"original comment that's longer"
            zipf.writestr("foo.txt", "O, dla a Muse of Fire!")
        przy zipfile.ZipFile(TESTFN,mode="a") jako zipf:
            zipf.comment = b"shorter comment"
        przy zipfile.ZipFile(TESTFN,mode="r") jako zipf:
            self.assertEqual(zipf.comment, b"shorter comment")

    def test_unicode_comment(self):
        przy zipfile.ZipFile(TESTFN, "w", zipfile.ZIP_STORED) jako zipf:
            zipf.writestr("foo.txt", "O, dla a Muse of Fire!")
            przy self.assertRaises(TypeError):
                zipf.comment = "this jest an error"

    def test_change_comment_in_empty_archive(self):
        przy zipfile.ZipFile(TESTFN, "a", zipfile.ZIP_STORED) jako zipf:
            self.assertNieprawda(zipf.filelist)
            zipf.comment = b"this jest a comment"
        przy zipfile.ZipFile(TESTFN, "r") jako zipf:
            self.assertEqual(zipf.comment, b"this jest a comment")

    def test_change_comment_in_nonempty_archive(self):
        przy zipfile.ZipFile(TESTFN, "w", zipfile.ZIP_STORED) jako zipf:
            zipf.writestr("foo.txt", "O, dla a Muse of Fire!")
        przy zipfile.ZipFile(TESTFN, "a", zipfile.ZIP_STORED) jako zipf:
            self.assertPrawda(zipf.filelist)
            zipf.comment = b"this jest a comment"
        przy zipfile.ZipFile(TESTFN, "r") jako zipf:
            self.assertEqual(zipf.comment, b"this jest a comment")

    def test_empty_zipfile(self):
        # Check that creating a file w 'w' albo 'a' mode oraz closing without
        # adding any files to the archives creates a valid empty ZIP file
        zipf = zipfile.ZipFile(TESTFN, mode="w")
        zipf.close()
        spróbuj:
            zipf = zipfile.ZipFile(TESTFN, mode="r")
        wyjąwszy zipfile.BadZipFile:
            self.fail("Unable to create empty ZIP file w 'w' mode")

        zipf = zipfile.ZipFile(TESTFN, mode="a")
        zipf.close()
        spróbuj:
            zipf = zipfile.ZipFile(TESTFN, mode="r")
        wyjąwszy:
            self.fail("Unable to create empty ZIP file w 'a' mode")

    def test_open_empty_file(self):
        # Issue 1710703: Check that opening a file przy less than 22 bytes
        # podnieśs a BadZipFile exception (rather than the previously unhelpful
        # OSError)
        f = open(TESTFN, 'w')
        f.close()
        self.assertRaises(zipfile.BadZipFile, zipfile.ZipFile, TESTFN, 'r')

    def test_create_zipinfo_before_1980(self):
        self.assertRaises(ValueError,
                          zipfile.ZipInfo, 'seventies', (1979, 1, 1, 0, 0, 0))

    def test_zipfile_with_short_extra_field(self):
        """If an extra field w the header jest less than 4 bytes, skip it."""
        zipdata = (
            b'PK\x03\x04\x14\x00\x00\x00\x00\x00\x93\x9b\xad@\x8b\x9e'
            b'\xd9\xd3\x01\x00\x00\x00\x01\x00\x00\x00\x03\x00\x03\x00ab'
            b'c\x00\x00\x00APK\x01\x02\x14\x03\x14\x00\x00\x00\x00'
            b'\x00\x93\x9b\xad@\x8b\x9e\xd9\xd3\x01\x00\x00\x00\x01\x00\x00'
            b'\x00\x03\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa4\x81\x00'
            b'\x00\x00\x00abc\x00\x00PK\x05\x06\x00\x00\x00\x00'
            b'\x01\x00\x01\x003\x00\x00\x00%\x00\x00\x00\x00\x00'
        )
        przy zipfile.ZipFile(io.BytesIO(zipdata), 'r') jako zipf:
            # testzip returns the name of the first corrupt file, albo Nic
            self.assertIsNic(zipf.testzip())

    def tearDown(self):
        unlink(TESTFN)
        unlink(TESTFN2)


klasa AbstractBadCrcTests:
    def test_testzip_with_bad_crc(self):
        """Tests that files przy bad CRCs zwróć their name z testzip."""
        zipdata = self.zip_with_bad_crc

        przy zipfile.ZipFile(io.BytesIO(zipdata), mode="r") jako zipf:
            # testzip returns the name of the first corrupt file, albo Nic
            self.assertEqual('afile', zipf.testzip())

    def test_read_with_bad_crc(self):
        """Tests that files przy bad CRCs podnieś a BadZipFile exception when read."""
        zipdata = self.zip_with_bad_crc

        # Using ZipFile.read()
        przy zipfile.ZipFile(io.BytesIO(zipdata), mode="r") jako zipf:
            self.assertRaises(zipfile.BadZipFile, zipf.read, 'afile')

        # Using ZipExtFile.read()
        przy zipfile.ZipFile(io.BytesIO(zipdata), mode="r") jako zipf:
            przy zipf.open('afile', 'r') jako corrupt_file:
                self.assertRaises(zipfile.BadZipFile, corrupt_file.read)

        # Same przy small reads (in order to exercise the buffering logic)
        przy zipfile.ZipFile(io.BytesIO(zipdata), mode="r") jako zipf:
            przy zipf.open('afile', 'r') jako corrupt_file:
                corrupt_file.MIN_READ_SIZE = 2
                przy self.assertRaises(zipfile.BadZipFile):
                    dopóki corrupt_file.read(2):
                        dalej


klasa StoredBadCrcTests(AbstractBadCrcTests, unittest.TestCase):
    compression = zipfile.ZIP_STORED
    zip_with_bad_crc = (
        b'PK\003\004\024\0\0\0\0\0 \213\212;:r'
        b'\253\377\f\0\0\0\f\0\0\0\005\0\0\000af'
        b'ilehello,AworldP'
        b'K\001\002\024\003\024\0\0\0\0\0 \213\212;:'
        b'r\253\377\f\0\0\0\f\0\0\0\005\0\0\0\0'
        b'\0\0\0\0\0\0\0\200\001\0\0\0\000afi'
        b'lePK\005\006\0\0\0\0\001\0\001\0003\000'
        b'\0\0/\0\0\0\0\0')

@requires_zlib
klasa DeflateBadCrcTests(AbstractBadCrcTests, unittest.TestCase):
    compression = zipfile.ZIP_DEFLATED
    zip_with_bad_crc = (
        b'PK\x03\x04\x14\x00\x00\x00\x08\x00n}\x0c=FA'
        b'KE\x10\x00\x00\x00n\x00\x00\x00\x05\x00\x00\x00af'
        b'ile\xcbH\xcd\xc9\xc9W(\xcf/\xcaI\xc9\xa0'
        b'=\x13\x00PK\x01\x02\x14\x03\x14\x00\x00\x00\x08\x00n'
        b'}\x0c=FAKE\x10\x00\x00\x00n\x00\x00\x00\x05'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x01\x00\x00\x00'
        b'\x00afilePK\x05\x06\x00\x00\x00\x00\x01\x00'
        b'\x01\x003\x00\x00\x003\x00\x00\x00\x00\x00')

@requires_bz2
klasa Bzip2BadCrcTests(AbstractBadCrcTests, unittest.TestCase):
    compression = zipfile.ZIP_BZIP2
    zip_with_bad_crc = (
        b'PK\x03\x04\x14\x03\x00\x00\x0c\x00nu\x0c=FA'
        b'KE8\x00\x00\x00n\x00\x00\x00\x05\x00\x00\x00af'
        b'ileBZh91AY&SY\xd4\xa8\xca'
        b'\x7f\x00\x00\x0f\x11\x80@\x00\x06D\x90\x80 \x00 \xa5'
        b'P\xd9!\x03\x03\x13\x13\x13\x89\xa9\xa9\xc2u5:\x9f'
        b'\x8b\xb9"\x9c(HjTe?\x80PK\x01\x02\x14'
        b'\x03\x14\x03\x00\x00\x0c\x00nu\x0c=FAKE8'
        b'\x00\x00\x00n\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00 \x80\x80\x81\x00\x00\x00\x00afilePK'
        b'\x05\x06\x00\x00\x00\x00\x01\x00\x01\x003\x00\x00\x00[\x00'
        b'\x00\x00\x00\x00')

@requires_lzma
klasa LzmaBadCrcTests(AbstractBadCrcTests, unittest.TestCase):
    compression = zipfile.ZIP_LZMA
    zip_with_bad_crc = (
        b'PK\x03\x04\x14\x03\x00\x00\x0e\x00nu\x0c=FA'
        b'KE\x1b\x00\x00\x00n\x00\x00\x00\x05\x00\x00\x00af'
        b'ile\t\x04\x05\x00]\x00\x00\x00\x04\x004\x19I'
        b'\xee\x8d\xe9\x17\x89:3`\tq!.8\x00PK'
        b'\x01\x02\x14\x03\x14\x03\x00\x00\x0e\x00nu\x0c=FA'
        b'KE\x1b\x00\x00\x00n\x00\x00\x00\x05\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00 \x80\x80\x81\x00\x00\x00\x00afil'
        b'ePK\x05\x06\x00\x00\x00\x00\x01\x00\x01\x003\x00\x00'
        b'\x00>\x00\x00\x00\x00\x00')


klasa DecryptionTests(unittest.TestCase):
    """Check that ZIP decryption works. Since the library does nie
    support encryption at the moment, we use a pre-generated encrypted
    ZIP file."""

    data = (
        b'PK\x03\x04\x14\x00\x01\x00\x00\x00n\x92i.#y\xef?&\x00\x00\x00\x1a\x00'
        b'\x00\x00\x08\x00\x00\x00test.txt\xfa\x10\xa0gly|\xfa-\xc5\xc0=\xf9y'
        b'\x18\xe0\xa8r\xb3Z}Lg\xbc\xae\xf9|\x9b\x19\xe4\x8b\xba\xbb)\x8c\xb0\xdbl'
        b'PK\x01\x02\x14\x00\x14\x00\x01\x00\x00\x00n\x92i.#y\xef?&\x00\x00\x00'
        b'\x1a\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x01\x00 \x00\xb6\x81'
        b'\x00\x00\x00\x00test.txtPK\x05\x06\x00\x00\x00\x00\x01\x00\x01\x006\x00'
        b'\x00\x00L\x00\x00\x00\x00\x00' )
    data2 = (
        b'PK\x03\x04\x14\x00\t\x00\x08\x00\xcf}38xu\xaa\xb2\x14\x00\x00\x00\x00\x02'
        b'\x00\x00\x04\x00\x15\x00zeroUT\t\x00\x03\xd6\x8b\x92G\xda\x8b\x92GUx\x04'
        b'\x00\xe8\x03\xe8\x03\xc7<M\xb5a\xceX\xa3Y&\x8b{oE\xd7\x9d\x8c\x98\x02\xc0'
        b'PK\x07\x08xu\xaa\xb2\x14\x00\x00\x00\x00\x02\x00\x00PK\x01\x02\x17\x03'
        b'\x14\x00\t\x00\x08\x00\xcf}38xu\xaa\xb2\x14\x00\x00\x00\x00\x02\x00\x00'
        b'\x04\x00\r\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa4\x81\x00\x00\x00\x00ze'
        b'roUT\x05\x00\x03\xd6\x8b\x92GUx\x00\x00PK\x05\x06\x00\x00\x00\x00\x01'
        b'\x00\x01\x00?\x00\x00\x00[\x00\x00\x00\x00\x00' )

    plain = b'zipfile.py encryption test'
    plain2 = b'\x00'*512

    def setUp(self):
        przy open(TESTFN, "wb") jako fp:
            fp.write(self.data)
        self.zip = zipfile.ZipFile(TESTFN, "r")
        przy open(TESTFN2, "wb") jako fp:
            fp.write(self.data2)
        self.zip2 = zipfile.ZipFile(TESTFN2, "r")

    def tearDown(self):
        self.zip.close()
        os.unlink(TESTFN)
        self.zip2.close()
        os.unlink(TESTFN2)

    def test_no_password(self):
        # Reading the encrypted file without dalejword
        # must generate a RunTime exception
        self.assertRaises(RuntimeError, self.zip.read, "test.txt")
        self.assertRaises(RuntimeError, self.zip2.read, "zero")

    def test_bad_password(self):
        self.zip.setpassword(b"perl")
        self.assertRaises(RuntimeError, self.zip.read, "test.txt")
        self.zip2.setpassword(b"perl")
        self.assertRaises(RuntimeError, self.zip2.read, "zero")

    @requires_zlib
    def test_good_password(self):
        self.zip.setpassword(b"python")
        self.assertEqual(self.zip.read("test.txt"), self.plain)
        self.zip2.setpassword(b"12345")
        self.assertEqual(self.zip2.read("zero"), self.plain2)

    def test_unicode_password(self):
        self.assertRaises(TypeError, self.zip.setpassword, "unicode")
        self.assertRaises(TypeError, self.zip.read, "test.txt", "python")
        self.assertRaises(TypeError, self.zip.open, "test.txt", pwd="python")
        self.assertRaises(TypeError, self.zip.extract, "test.txt", pwd="python")

klasa AbstractTestsWithRandomBinaryFiles:
    @classmethod
    def setUpClass(cls):
        datacount = randint(16, 64)*1024 + randint(1, 1024)
        cls.data = b''.join(struct.pack('<f', random()*randint(-1000, 1000))
                            dla i w range(datacount))

    def setUp(self):
        # Make a source file przy some lines
        przy open(TESTFN, "wb") jako fp:
            fp.write(self.data)

    def tearDown(self):
        unlink(TESTFN)
        unlink(TESTFN2)

    def make_test_archive(self, f, compression):
        # Create the ZIP archive
        przy zipfile.ZipFile(f, "w", compression) jako zipfp:
            zipfp.write(TESTFN, "another.name")
            zipfp.write(TESTFN, TESTFN)

    def zip_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        przy zipfile.ZipFile(f, "r", compression) jako zipfp:
            testdata = zipfp.read(TESTFN)
            self.assertEqual(len(testdata), len(self.data))
            self.assertEqual(testdata, self.data)
            self.assertEqual(zipfp.read("another.name"), self.data)

    def test_read(self):
        dla f w get_files(self):
            self.zip_test(f, self.compression)

    def zip_open_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        przy zipfile.ZipFile(f, "r", compression) jako zipfp:
            zipdata1 = []
            przy zipfp.open(TESTFN) jako zipopen1:
                dopóki Prawda:
                    read_data = zipopen1.read(256)
                    jeżeli nie read_data:
                        przerwij
                    zipdata1.append(read_data)

            zipdata2 = []
            przy zipfp.open("another.name") jako zipopen2:
                dopóki Prawda:
                    read_data = zipopen2.read(256)
                    jeżeli nie read_data:
                        przerwij
                    zipdata2.append(read_data)

            testdata1 = b''.join(zipdata1)
            self.assertEqual(len(testdata1), len(self.data))
            self.assertEqual(testdata1, self.data)

            testdata2 = b''.join(zipdata2)
            self.assertEqual(len(testdata2), len(self.data))
            self.assertEqual(testdata2, self.data)

    def test_open(self):
        dla f w get_files(self):
            self.zip_open_test(f, self.compression)

    def zip_random_open_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        przy zipfile.ZipFile(f, "r", compression) jako zipfp:
            zipdata1 = []
            przy zipfp.open(TESTFN) jako zipopen1:
                dopóki Prawda:
                    read_data = zipopen1.read(randint(1, 1024))
                    jeżeli nie read_data:
                        przerwij
                    zipdata1.append(read_data)

            testdata = b''.join(zipdata1)
            self.assertEqual(len(testdata), len(self.data))
            self.assertEqual(testdata, self.data)

    def test_random_open(self):
        dla f w get_files(self):
            self.zip_random_open_test(f, self.compression)


klasa StoredTestsWithRandomBinaryFiles(AbstractTestsWithRandomBinaryFiles,
                                       unittest.TestCase):
    compression = zipfile.ZIP_STORED

@requires_zlib
klasa DeflateTestsWithRandomBinaryFiles(AbstractTestsWithRandomBinaryFiles,
                                        unittest.TestCase):
    compression = zipfile.ZIP_DEFLATED

@requires_bz2
klasa Bzip2TestsWithRandomBinaryFiles(AbstractTestsWithRandomBinaryFiles,
                                      unittest.TestCase):
    compression = zipfile.ZIP_BZIP2

@requires_lzma
klasa LzmaTestsWithRandomBinaryFiles(AbstractTestsWithRandomBinaryFiles,
                                     unittest.TestCase):
    compression = zipfile.ZIP_LZMA


# Privide the tell() method but nie seek()
klasa Tellable:
    def __init__(self, fp):
        self.fp = fp
        self.offset = 0

    def write(self, data):
        n = self.fp.write(data)
        self.offset += n
        zwróć n

    def tell(self):
        zwróć self.offset

    def flush(self):
        self.fp.flush()

klasa Unseekable:
    def __init__(self, fp):
        self.fp = fp

    def write(self, data):
        zwróć self.fp.write(data)

    def flush(self):
        self.fp.flush()

klasa UnseekableTests(unittest.TestCase):
    def test_writestr(self):
        dla wrapper w (lambda f: f), Tellable, Unseekable:
            przy self.subTest(wrapper=wrapper):
                f = io.BytesIO()
                f.write(b'abc')
                bf = io.BufferedWriter(f)
                przy zipfile.ZipFile(wrapper(bf), 'w', zipfile.ZIP_STORED) jako zipfp:
                    zipfp.writestr('ones', b'111')
                    zipfp.writestr('twos', b'222')
                self.assertEqual(f.getvalue()[:5], b'abcPK')
                przy zipfile.ZipFile(f, mode='r') jako zipf:
                    przy zipf.open('ones') jako zopen:
                        self.assertEqual(zopen.read(), b'111')
                    przy zipf.open('twos') jako zopen:
                        self.assertEqual(zopen.read(), b'222')

    def test_write(self):
        dla wrapper w (lambda f: f), Tellable, Unseekable:
            przy self.subTest(wrapper=wrapper):
                f = io.BytesIO()
                f.write(b'abc')
                bf = io.BufferedWriter(f)
                przy zipfile.ZipFile(wrapper(bf), 'w', zipfile.ZIP_STORED) jako zipfp:
                    self.addCleanup(unlink, TESTFN)
                    przy open(TESTFN, 'wb') jako f2:
                        f2.write(b'111')
                    zipfp.write(TESTFN, 'ones')
                    przy open(TESTFN, 'wb') jako f2:
                        f2.write(b'222')
                    zipfp.write(TESTFN, 'twos')
                self.assertEqual(f.getvalue()[:5], b'abcPK')
                przy zipfile.ZipFile(f, mode='r') jako zipf:
                    przy zipf.open('ones') jako zopen:
                        self.assertEqual(zopen.read(), b'111')
                    przy zipf.open('twos') jako zopen:
                        self.assertEqual(zopen.read(), b'222')


@requires_zlib
klasa TestsWithMultipleOpens(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data1 = b'111' + getrandbytes(10000)
        cls.data2 = b'222' + getrandbytes(10000)

    def make_test_archive(self, f):
        # Create the ZIP archive
        przy zipfile.ZipFile(f, "w", zipfile.ZIP_DEFLATED) jako zipfp:
            zipfp.writestr('ones', self.data1)
            zipfp.writestr('twos', self.data2)

    def test_same_file(self):
        # Verify that (when the ZipFile jest w control of creating file objects)
        # multiple open() calls can be made without interfering przy each other.
        dla f w get_files(self):
            self.make_test_archive(f)
            przy zipfile.ZipFile(f, mode="r") jako zipf:
                przy zipf.open('ones') jako zopen1, zipf.open('ones') jako zopen2:
                    data1 = zopen1.read(500)
                    data2 = zopen2.read(500)
                    data1 += zopen1.read()
                    data2 += zopen2.read()
                self.assertEqual(data1, data2)
                self.assertEqual(data1, self.data1)

    def test_different_file(self):
        # Verify that (when the ZipFile jest w control of creating file objects)
        # multiple open() calls can be made without interfering przy each other.
        dla f w get_files(self):
            self.make_test_archive(f)
            przy zipfile.ZipFile(f, mode="r") jako zipf:
                przy zipf.open('ones') jako zopen1, zipf.open('twos') jako zopen2:
                    data1 = zopen1.read(500)
                    data2 = zopen2.read(500)
                    data1 += zopen1.read()
                    data2 += zopen2.read()
                self.assertEqual(data1, self.data1)
                self.assertEqual(data2, self.data2)

    def test_interleaved(self):
        # Verify that (when the ZipFile jest w control of creating file objects)
        # multiple open() calls can be made without interfering przy each other.
        dla f w get_files(self):
            self.make_test_archive(f)
            przy zipfile.ZipFile(f, mode="r") jako zipf:
                przy zipf.open('ones') jako zopen1, zipf.open('twos') jako zopen2:
                    data1 = zopen1.read(500)
                    data2 = zopen2.read(500)
                    data1 += zopen1.read()
                    data2 += zopen2.read()
                self.assertEqual(data1, self.data1)
                self.assertEqual(data2, self.data2)

    def test_read_after_close(self):
        dla f w get_files(self):
            self.make_test_archive(f)
            przy contextlib.ExitStack() jako stack:
                przy zipfile.ZipFile(f, 'r') jako zipf:
                    zopen1 = stack.enter_context(zipf.open('ones'))
                    zopen2 = stack.enter_context(zipf.open('twos'))
                data1 = zopen1.read(500)
                data2 = zopen2.read(500)
                data1 += zopen1.read()
                data2 += zopen2.read()
            self.assertEqual(data1, self.data1)
            self.assertEqual(data2, self.data2)

    def test_read_after_write(self):
        dla f w get_files(self):
            przy zipfile.ZipFile(f, 'w', zipfile.ZIP_DEFLATED) jako zipf:
                zipf.writestr('ones', self.data1)
                zipf.writestr('twos', self.data2)
                przy zipf.open('ones') jako zopen1:
                    data1 = zopen1.read(500)
            self.assertEqual(data1, self.data1[:500])
            przy zipfile.ZipFile(f, 'r') jako zipf:
                data1 = zipf.read('ones')
                data2 = zipf.read('twos')
            self.assertEqual(data1, self.data1)
            self.assertEqual(data2, self.data2)

    def test_write_after_read(self):
        dla f w get_files(self):
            przy zipfile.ZipFile(f, "w", zipfile.ZIP_DEFLATED) jako zipf:
                zipf.writestr('ones', self.data1)
                przy zipf.open('ones') jako zopen1:
                    zopen1.read(500)
                    zipf.writestr('twos', self.data2)
            przy zipfile.ZipFile(f, 'r') jako zipf:
                data1 = zipf.read('ones')
                data2 = zipf.read('twos')
            self.assertEqual(data1, self.data1)
            self.assertEqual(data2, self.data2)

    def test_many_opens(self):
        # Verify that read() oraz open() promptly close the file descriptor,
        # oraz don't rely on the garbage collector to free resources.
        self.make_test_archive(TESTFN2)
        przy zipfile.ZipFile(TESTFN2, mode="r") jako zipf:
            dla x w range(100):
                zipf.read('ones')
                przy zipf.open('ones') jako zopen1:
                    dalej
        przy open(os.devnull) jako f:
            self.assertLess(f.fileno(), 100)

    def tearDown(self):
        unlink(TESTFN2)


klasa TestWithDirectory(unittest.TestCase):
    def setUp(self):
        os.mkdir(TESTFN2)

    def test_extract_dir(self):
        przy zipfile.ZipFile(findfile("zipdir.zip")) jako zipf:
            zipf.extractall(TESTFN2)
        self.assertPrawda(os.path.isdir(os.path.join(TESTFN2, "a")))
        self.assertPrawda(os.path.isdir(os.path.join(TESTFN2, "a", "b")))
        self.assertPrawda(os.path.exists(os.path.join(TESTFN2, "a", "b", "c")))

    def test_bug_6050(self):
        # Extraction should succeed jeżeli directories already exist
        os.mkdir(os.path.join(TESTFN2, "a"))
        self.test_extract_dir()

    def test_write_dir(self):
        dirpath = os.path.join(TESTFN2, "x")
        os.mkdir(dirpath)
        mode = os.stat(dirpath).st_mode & 0xFFFF
        przy zipfile.ZipFile(TESTFN, "w") jako zipf:
            zipf.write(dirpath)
            zinfo = zipf.filelist[0]
            self.assertPrawda(zinfo.filename.endswith("/x/"))
            self.assertEqual(zinfo.external_attr, (mode << 16) | 0x10)
            zipf.write(dirpath, "y")
            zinfo = zipf.filelist[1]
            self.assertPrawda(zinfo.filename, "y/")
            self.assertEqual(zinfo.external_attr, (mode << 16) | 0x10)
        przy zipfile.ZipFile(TESTFN, "r") jako zipf:
            zinfo = zipf.filelist[0]
            self.assertPrawda(zinfo.filename.endswith("/x/"))
            self.assertEqual(zinfo.external_attr, (mode << 16) | 0x10)
            zinfo = zipf.filelist[1]
            self.assertPrawda(zinfo.filename, "y/")
            self.assertEqual(zinfo.external_attr, (mode << 16) | 0x10)
            target = os.path.join(TESTFN2, "target")
            os.mkdir(target)
            zipf.extractall(target)
            self.assertPrawda(os.path.isdir(os.path.join(target, "y")))
            self.assertEqual(len(os.listdir(target)), 2)

    def test_writestr_dir(self):
        os.mkdir(os.path.join(TESTFN2, "x"))
        przy zipfile.ZipFile(TESTFN, "w") jako zipf:
            zipf.writestr("x/", b'')
            zinfo = zipf.filelist[0]
            self.assertEqual(zinfo.filename, "x/")
            self.assertEqual(zinfo.external_attr, (0o40775 << 16) | 0x10)
        przy zipfile.ZipFile(TESTFN, "r") jako zipf:
            zinfo = zipf.filelist[0]
            self.assertPrawda(zinfo.filename.endswith("x/"))
            self.assertEqual(zinfo.external_attr, (0o40775 << 16) | 0x10)
            target = os.path.join(TESTFN2, "target")
            os.mkdir(target)
            zipf.extractall(target)
            self.assertPrawda(os.path.isdir(os.path.join(target, "x")))
            self.assertEqual(os.listdir(target), ["x"])

    def tearDown(self):
        rmtree(TESTFN2)
        jeżeli os.path.exists(TESTFN):
            unlink(TESTFN)


klasa AbstractUniversalNewlineTests:
    @classmethod
    def setUpClass(cls):
        cls.line_gen = [bytes("Test of zipfile line %d." % i, "ascii")
                        dla i w range(FIXEDTEST_SIZE)]
        cls.seps = (b'\r', b'\r\n', b'\n')
        cls.arcdata = {}
        dla n, s w enumerate(cls.seps):
            cls.arcdata[s] = s.join(cls.line_gen) + s

    def setUp(self):
        self.arcfiles = {}
        dla n, s w enumerate(self.seps):
            self.arcfiles[s] = '%s-%d' % (TESTFN, n)
            przy open(self.arcfiles[s], "wb") jako f:
                f.write(self.arcdata[s])

    def make_test_archive(self, f, compression):
        # Create the ZIP archive
        przy zipfile.ZipFile(f, "w", compression) jako zipfp:
            dla fn w self.arcfiles.values():
                zipfp.write(fn, fn)

    def read_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        przy zipfile.ZipFile(f, "r") jako zipfp:
            dla sep, fn w self.arcfiles.items():
                przy openU(zipfp, fn) jako fp:
                    zipdata = fp.read()
                self.assertEqual(self.arcdata[sep], zipdata)

    def test_read(self):
        dla f w get_files(self):
            self.read_test(f, self.compression)

    def readline_read_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        przy zipfile.ZipFile(f, "r") jako zipfp:
            dla sep, fn w self.arcfiles.items():
                przy openU(zipfp, fn) jako zipopen:
                    data = b''
                    dopóki Prawda:
                        read = zipopen.readline()
                        jeżeli nie read:
                            przerwij
                        data += read

                        read = zipopen.read(5)
                        jeżeli nie read:
                            przerwij
                        data += read

            self.assertEqual(data, self.arcdata[b'\n'])

    def test_readline_read(self):
        dla f w get_files(self):
            self.readline_read_test(f, self.compression)

    def readline_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        przy zipfile.ZipFile(f, "r") jako zipfp:
            dla sep, fn w self.arcfiles.items():
                przy openU(zipfp, fn) jako zipopen:
                    dla line w self.line_gen:
                        linedata = zipopen.readline()
                        self.assertEqual(linedata, line + b'\n')

    def test_readline(self):
        dla f w get_files(self):
            self.readline_test(f, self.compression)

    def readlines_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        przy zipfile.ZipFile(f, "r") jako zipfp:
            dla sep, fn w self.arcfiles.items():
                przy openU(zipfp, fn) jako fp:
                    ziplines = fp.readlines()
                dla line, zipline w zip(self.line_gen, ziplines):
                    self.assertEqual(zipline, line + b'\n')

    def test_readlines(self):
        dla f w get_files(self):
            self.readlines_test(f, self.compression)

    def iterlines_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        przy zipfile.ZipFile(f, "r") jako zipfp:
            dla sep, fn w self.arcfiles.items():
                przy openU(zipfp, fn) jako fp:
                    dla line, zipline w zip(self.line_gen, fp):
                        self.assertEqual(zipline, line + b'\n')

    def test_iterlines(self):
        dla f w get_files(self):
            self.iterlines_test(f, self.compression)

    def tearDown(self):
        dla sep, fn w self.arcfiles.items():
            unlink(fn)
        unlink(TESTFN)
        unlink(TESTFN2)


klasa StoredUniversalNewlineTests(AbstractUniversalNewlineTests,
                                  unittest.TestCase):
    compression = zipfile.ZIP_STORED

@requires_zlib
klasa DeflateUniversalNewlineTests(AbstractUniversalNewlineTests,
                                   unittest.TestCase):
    compression = zipfile.ZIP_DEFLATED

@requires_bz2
klasa Bzip2UniversalNewlineTests(AbstractUniversalNewlineTests,
                                 unittest.TestCase):
    compression = zipfile.ZIP_BZIP2

@requires_lzma
klasa LzmaUniversalNewlineTests(AbstractUniversalNewlineTests,
                                unittest.TestCase):
    compression = zipfile.ZIP_LZMA

jeżeli __name__ == "__main__":
    unittest.main()
