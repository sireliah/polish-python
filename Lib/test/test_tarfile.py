zaimportuj sys
zaimportuj os
zaimportuj io
z hashlib zaimportuj md5
z contextlib zaimportuj contextmanager

zaimportuj unittest
zaimportuj unittest.mock
zaimportuj tarfile

z test zaimportuj support
z test.support zaimportuj script_helper

# Check dla our compression modules.
spróbuj:
    zaimportuj gzip
wyjąwszy ImportError:
    gzip = Nic
spróbuj:
    zaimportuj bz2
wyjąwszy ImportError:
    bz2 = Nic
spróbuj:
    zaimportuj lzma
wyjąwszy ImportError:
    lzma = Nic

def md5sum(data):
    zwróć md5(data).hexdigest()

TEMPDIR = os.path.abspath(support.TESTFN) + "-tardir"
tarextdir = TEMPDIR + '-extract-test'
tarname = support.findfile("testtar.tar")
gzipname = os.path.join(TEMPDIR, "testtar.tar.gz")
bz2name = os.path.join(TEMPDIR, "testtar.tar.bz2")
xzname = os.path.join(TEMPDIR, "testtar.tar.xz")
tmpname = os.path.join(TEMPDIR, "tmp.tar")
dotlessname = os.path.join(TEMPDIR, "testtar")

md5_regtype = "65f477c818ad9e15f7feab0c6d37742f"
md5_sparse = "a54fbc4ca4f4399a90e1b27164012fc6"


klasa TarTest:
    tarname = tarname
    suffix = ''
    open = io.FileIO
    taropen = tarfile.TarFile.taropen

    @property
    def mode(self):
        zwróć self.prefix + self.suffix

@support.requires_gzip
klasa GzipTest:
    tarname = gzipname
    suffix = 'gz'
    open = gzip.GzipFile jeżeli gzip inaczej Nic
    taropen = tarfile.TarFile.gzopen

@support.requires_bz2
klasa Bz2Test:
    tarname = bz2name
    suffix = 'bz2'
    open = bz2.BZ2File jeżeli bz2 inaczej Nic
    taropen = tarfile.TarFile.bz2open

@support.requires_lzma
klasa LzmaTest:
    tarname = xzname
    suffix = 'xz'
    open = lzma.LZMAFile jeżeli lzma inaczej Nic
    taropen = tarfile.TarFile.xzopen


klasa ReadTest(TarTest):

    prefix = "r:"

    def setUp(self):
        self.tar = tarfile.open(self.tarname, mode=self.mode,
                                encoding="iso8859-1")

    def tearDown(self):
        self.tar.close()


klasa UstarReadTest(ReadTest, unittest.TestCase):

    def test_fileobj_regular_file(self):
        tarinfo = self.tar.getmember("ustar/regtype")
        przy self.tar.extractfile(tarinfo) jako fobj:
            data = fobj.read()
            self.assertEqual(len(data), tarinfo.size,
                    "regular file extraction failed")
            self.assertEqual(md5sum(data), md5_regtype,
                    "regular file extraction failed")

    def test_fileobj_readlines(self):
        self.tar.extract("ustar/regtype", TEMPDIR)
        tarinfo = self.tar.getmember("ustar/regtype")
        przy open(os.path.join(TEMPDIR, "ustar/regtype"), "r") jako fobj1:
            lines1 = fobj1.readlines()

        przy self.tar.extractfile(tarinfo) jako fobj:
            fobj2 = io.TextIOWrapper(fobj)
            lines2 = fobj2.readlines()
            self.assertEqual(lines1, lines2,
                    "fileobj.readlines() failed")
            self.assertEqual(len(lines2), 114,
                    "fileobj.readlines() failed")
            self.assertEqual(lines2[83],
                    "I will gladly admit that Python jest nie the fastest "
                    "running scripting language.\n",
                    "fileobj.readlines() failed")

    def test_fileobj_iter(self):
        self.tar.extract("ustar/regtype", TEMPDIR)
        tarinfo = self.tar.getmember("ustar/regtype")
        przy open(os.path.join(TEMPDIR, "ustar/regtype"), "r") jako fobj1:
            lines1 = fobj1.readlines()
        przy self.tar.extractfile(tarinfo) jako fobj2:
            lines2 = list(io.TextIOWrapper(fobj2))
            self.assertEqual(lines1, lines2,
                    "fileobj.__iter__() failed")

    def test_fileobj_seek(self):
        self.tar.extract("ustar/regtype", TEMPDIR)
        przy open(os.path.join(TEMPDIR, "ustar/regtype"), "rb") jako fobj:
            data = fobj.read()

        tarinfo = self.tar.getmember("ustar/regtype")
        fobj = self.tar.extractfile(tarinfo)

        text = fobj.read()
        fobj.seek(0)
        self.assertEqual(0, fobj.tell(),
                     "seek() to file's start failed")
        fobj.seek(2048, 0)
        self.assertEqual(2048, fobj.tell(),
                     "seek() to absolute position failed")
        fobj.seek(-1024, 1)
        self.assertEqual(1024, fobj.tell(),
                     "seek() to negative relative position failed")
        fobj.seek(1024, 1)
        self.assertEqual(2048, fobj.tell(),
                     "seek() to positive relative position failed")
        s = fobj.read(10)
        self.assertEqual(s, data[2048:2058],
                     "read() after seek failed")
        fobj.seek(0, 2)
        self.assertEqual(tarinfo.size, fobj.tell(),
                     "seek() to file's end failed")
        self.assertEqual(fobj.read(), b"",
                     "read() at file's end did nie zwróć empty string")
        fobj.seek(-tarinfo.size, 2)
        self.assertEqual(0, fobj.tell(),
                     "relative seek() to file's end failed")
        fobj.seek(512)
        s1 = fobj.readlines()
        fobj.seek(512)
        s2 = fobj.readlines()
        self.assertEqual(s1, s2,
                     "readlines() after seek failed")
        fobj.seek(0)
        self.assertEqual(len(fobj.readline()), fobj.tell(),
                     "tell() after readline() failed")
        fobj.seek(512)
        self.assertEqual(len(fobj.readline()) + 512, fobj.tell(),
                     "tell() after seek() oraz readline() failed")
        fobj.seek(0)
        line = fobj.readline()
        self.assertEqual(fobj.read(), data[len(line):],
                     "read() after readline() failed")
        fobj.close()

    def test_fileobj_text(self):
        przy self.tar.extractfile("ustar/regtype") jako fobj:
            fobj = io.TextIOWrapper(fobj)
            data = fobj.read().encode("iso8859-1")
            self.assertEqual(md5sum(data), md5_regtype)
            spróbuj:
                fobj.seek(100)
            wyjąwszy AttributeError:
                # Issue #13815: seek() complained about a missing
                # flush() method.
                self.fail("seeking failed w text mode")

    # Test jeżeli symbolic oraz hard links are resolved by extractfile().  The
    # test link members each point to a regular member whose data jest
    # supposed to be exported.
    def _test_fileobj_link(self, lnktype, regtype):
        przy self.tar.extractfile(lnktype) jako a, \
             self.tar.extractfile(regtype) jako b:
            self.assertEqual(a.name, b.name)

    def test_fileobj_link1(self):
        self._test_fileobj_link("ustar/lnktype", "ustar/regtype")

    def test_fileobj_link2(self):
        self._test_fileobj_link("./ustar/linktest2/lnktype",
                                "ustar/linktest1/regtype")

    def test_fileobj_symlink1(self):
        self._test_fileobj_link("ustar/symtype", "ustar/regtype")

    def test_fileobj_symlink2(self):
        self._test_fileobj_link("./ustar/linktest2/symtype",
                                "ustar/linktest1/regtype")

    def test_issue14160(self):
        self._test_fileobj_link("symtype2", "ustar/regtype")

klasa GzipUstarReadTest(GzipTest, UstarReadTest):
    dalej

klasa Bz2UstarReadTest(Bz2Test, UstarReadTest):
    dalej

klasa LzmaUstarReadTest(LzmaTest, UstarReadTest):
    dalej


klasa ListTest(ReadTest, unittest.TestCase):

    # Override setUp to use default encoding (UTF-8)
    def setUp(self):
        self.tar = tarfile.open(self.tarname, mode=self.mode)

    def test_list(self):
        tio = io.TextIOWrapper(io.BytesIO(), 'ascii', newline='\n')
        przy support.swap_attr(sys, 'stdout', tio):
            self.tar.list(verbose=Nieprawda)
        out = tio.detach().getvalue()
        self.assertIn(b'ustar/conttype', out)
        self.assertIn(b'ustar/regtype', out)
        self.assertIn(b'ustar/lnktype', out)
        self.assertIn(b'ustar' + (b'/12345' * 40) + b'67/longname', out)
        self.assertIn(b'./ustar/linktest2/symtype', out)
        self.assertIn(b'./ustar/linktest2/lnktype', out)
        # Make sure it puts trailing slash dla directory
        self.assertIn(b'ustar/dirtype/', out)
        self.assertIn(b'ustar/dirtype-with-size/', out)
        # Make sure it jest able to print unencodable characters
        def conv(b):
            s = b.decode(self.tar.encoding, 'surrogateescape')
            zwróć s.encode('ascii', 'backslashreplace')
        self.assertIn(conv(b'ustar/umlauts-\xc4\xd6\xdc\xe4\xf6\xfc\xdf'), out)
        self.assertIn(conv(b'misc/regtype-hpux-signed-chksum-'
                           b'\xc4\xd6\xdc\xe4\xf6\xfc\xdf'), out)
        self.assertIn(conv(b'misc/regtype-old-v7-signed-chksum-'
                           b'\xc4\xd6\xdc\xe4\xf6\xfc\xdf'), out)
        self.assertIn(conv(b'pax/bad-pax-\xe4\xf6\xfc'), out)
        self.assertIn(conv(b'pax/hdrcharset-\xe4\xf6\xfc'), out)
        # Make sure it prints files separated by one newline without any
        # 'ls -l'-like accessories jeżeli verbose flag jest nie being used
        # ...
        # ustar/conttype
        # ustar/regtype
        # ...
        self.assertRegex(out, br'ustar/conttype ?\r?\n'
                              br'ustar/regtype ?\r?\n')
        # Make sure it does nie print the source of link without verbose flag
        self.assertNotIn(b'link to', out)
        self.assertNotIn(b'->', out)

    def test_list_verbose(self):
        tio = io.TextIOWrapper(io.BytesIO(), 'ascii', newline='\n')
        przy support.swap_attr(sys, 'stdout', tio):
            self.tar.list(verbose=Prawda)
        out = tio.detach().getvalue()
        # Make sure it prints files separated by one newline przy 'ls -l'-like
        # accessories jeżeli verbose flag jest being used
        # ...
        # ?rw-r--r-- tarfile/tarfile     7011 2003-01-06 07:19:43 ustar/conttype
        # ?rw-r--r-- tarfile/tarfile     7011 2003-01-06 07:19:43 ustar/regtype
        # ...
        self.assertRegex(out, (br'\?rw-r--r-- tarfile/tarfile\s+7011 '
                               br'\d{4}-\d\d-\d\d\s+\d\d:\d\d:\d\d '
                               br'ustar/\w+type ?\r?\n') * 2)
        # Make sure it prints the source of link przy verbose flag
        self.assertIn(b'ustar/symtype -> regtype', out)
        self.assertIn(b'./ustar/linktest2/symtype -> ../linktest1/regtype', out)
        self.assertIn(b'./ustar/linktest2/lnktype link to '
                      b'./ustar/linktest1/regtype', out)
        self.assertIn(b'gnu' + (b'/123' * 125) + b'/longlink link to gnu' +
                      (b'/123' * 125) + b'/longname', out)
        self.assertIn(b'pax' + (b'/123' * 125) + b'/longlink link to pax' +
                      (b'/123' * 125) + b'/longname', out)

    def test_list_members(self):
        tio = io.TextIOWrapper(io.BytesIO(), 'ascii', newline='\n')
        def members(tar):
            dla tarinfo w tar.getmembers():
                jeżeli 'reg' w tarinfo.name:
                    uzyskaj tarinfo
        przy support.swap_attr(sys, 'stdout', tio):
            self.tar.list(verbose=Nieprawda, members=members(self.tar))
        out = tio.detach().getvalue()
        self.assertIn(b'ustar/regtype', out)
        self.assertNotIn(b'ustar/conttype', out)


klasa GzipListTest(GzipTest, ListTest):
    dalej


klasa Bz2ListTest(Bz2Test, ListTest):
    dalej


klasa LzmaListTest(LzmaTest, ListTest):
    dalej


klasa CommonReadTest(ReadTest):

    def test_empty_tarfile(self):
        # Test dla issue6123: Allow opening empty archives.
        # This test checks jeżeli tarfile.open() jest able to open an empty tar
        # archive successfully. Note that an empty tar archive jest nie the
        # same jako an empty file!
        przy tarfile.open(tmpname, self.mode.replace("r", "w")):
            dalej
        spróbuj:
            tar = tarfile.open(tmpname, self.mode)
            tar.getnames()
        wyjąwszy tarfile.ReadError:
            self.fail("tarfile.open() failed on empty archive")
        inaczej:
            self.assertListEqual(tar.getmembers(), [])
        w_końcu:
            tar.close()

    def test_non_existent_tarfile(self):
        # Test dla issue11513: prevent non-existent gzipped tarfiles raising
        # multiple exceptions.
        przy self.assertRaisesRegex(FileNotFoundError, "xxx"):
            tarfile.open("xxx", self.mode)

    def test_null_tarfile(self):
        # Test dla issue6123: Allow opening empty archives.
        # This test guarantees that tarfile.open() does nie treat an empty
        # file jako an empty tar archive.
        przy open(tmpname, "wb"):
            dalej
        self.assertRaises(tarfile.ReadError, tarfile.open, tmpname, self.mode)
        self.assertRaises(tarfile.ReadError, tarfile.open, tmpname)

    def test_ignore_zeros(self):
        # Test TarFile's ignore_zeros option.
        dla char w (b'\0', b'a'):
            # Test jeżeli EOFHeaderError ('\0') oraz InvalidHeaderError ('a')
            # are ignored correctly.
            przy self.open(tmpname, "w") jako fobj:
                fobj.write(char * 1024)
                fobj.write(tarfile.TarInfo("foo").tobuf())

            tar = tarfile.open(tmpname, mode="r", ignore_zeros=Prawda)
            spróbuj:
                self.assertListEqual(tar.getnames(), ["foo"],
                    "ignore_zeros=Prawda should have skipped the %r-blocks" %
                    char)
            w_końcu:
                tar.close()

    def test_premature_end_of_archive(self):
        dla size w (512, 600, 1024, 1200):
            przy tarfile.open(tmpname, "w:") jako tar:
                t = tarfile.TarInfo("foo")
                t.size = 1024
                tar.addfile(t, io.BytesIO(b"a" * 1024))

            przy open(tmpname, "r+b") jako fobj:
                fobj.truncate(size)

            przy tarfile.open(tmpname) jako tar:
                przy self.assertRaisesRegex(tarfile.ReadError, "unexpected end of data"):
                    dla t w tar:
                        dalej

            przy tarfile.open(tmpname) jako tar:
                t = tar.next()

                przy self.assertRaisesRegex(tarfile.ReadError, "unexpected end of data"):
                    tar.extract(t, TEMPDIR)

                przy self.assertRaisesRegex(tarfile.ReadError, "unexpected end of data"):
                    tar.extractfile(t).read()

klasa MiscReadTestBase(CommonReadTest):
    def requires_name_attribute(self):
        dalej

    def test_no_name_argument(self):
        self.requires_name_attribute()
        przy open(self.tarname, "rb") jako fobj:
            self.assertIsInstance(fobj.name, str)
            przy tarfile.open(fileobj=fobj, mode=self.mode) jako tar:
                self.assertIsInstance(tar.name, str)
                self.assertEqual(tar.name, os.path.abspath(fobj.name))

    def test_no_name_attribute(self):
        przy open(self.tarname, "rb") jako fobj:
            data = fobj.read()
        fobj = io.BytesIO(data)
        self.assertRaises(AttributeError, getattr, fobj, "name")
        tar = tarfile.open(fileobj=fobj, mode=self.mode)
        self.assertIsNic(tar.name)

    def test_empty_name_attribute(self):
        przy open(self.tarname, "rb") jako fobj:
            data = fobj.read()
        fobj = io.BytesIO(data)
        fobj.name = ""
        przy tarfile.open(fileobj=fobj, mode=self.mode) jako tar:
            self.assertIsNic(tar.name)

    def test_int_name_attribute(self):
        # Issue 21044: tarfile.open() should handle fileobj przy an integer
        # 'name' attribute.
        fd = os.open(self.tarname, os.O_RDONLY)
        przy open(fd, 'rb') jako fobj:
            self.assertIsInstance(fobj.name, int)
            przy tarfile.open(fileobj=fobj, mode=self.mode) jako tar:
                self.assertIsNic(tar.name)

    def test_bytes_name_attribute(self):
        self.requires_name_attribute()
        tarname = os.fsencode(self.tarname)
        przy open(tarname, 'rb') jako fobj:
            self.assertIsInstance(fobj.name, bytes)
            przy tarfile.open(fileobj=fobj, mode=self.mode) jako tar:
                self.assertIsInstance(tar.name, bytes)
                self.assertEqual(tar.name, os.path.abspath(fobj.name))

    def test_illegal_mode_arg(self):
        przy open(tmpname, 'wb'):
            dalej
        przy self.assertRaisesRegex(ValueError, 'mode must be '):
            tar = self.taropen(tmpname, 'q')
        przy self.assertRaisesRegex(ValueError, 'mode must be '):
            tar = self.taropen(tmpname, 'rw')
        przy self.assertRaisesRegex(ValueError, 'mode must be '):
            tar = self.taropen(tmpname, '')

    def test_fileobj_with_offset(self):
        # Skip the first member oraz store values z the second member
        # of the testtar.
        tar = tarfile.open(self.tarname, mode=self.mode)
        spróbuj:
            tar.next()
            t = tar.next()
            name = t.name
            offset = t.offset
            przy tar.extractfile(t) jako f:
                data = f.read()
        w_końcu:
            tar.close()

        # Open the testtar oraz seek to the offset of the second member.
        przy self.open(self.tarname) jako fobj:
            fobj.seek(offset)

            # Test jeżeli the tarfile starts przy the second member.
            tar = tar.open(self.tarname, mode="r:", fileobj=fobj)
            t = tar.next()
            self.assertEqual(t.name, name)
            # Read to the end of fileobj oraz test jeżeli seeking back to the
            # beginning works.
            tar.getmembers()
            self.assertEqual(tar.extractfile(t).read(), data,
                    "seek back did nie work")
            tar.close()

    def test_fail_comp(self):
        # For Gzip oraz Bz2 Tests: fail przy a ReadError on an uncompressed file.
        self.assertRaises(tarfile.ReadError, tarfile.open, tarname, self.mode)
        przy open(tarname, "rb") jako fobj:
            self.assertRaises(tarfile.ReadError, tarfile.open,
                              fileobj=fobj, mode=self.mode)

    def test_v7_dirtype(self):
        # Test old style dirtype member (bug #1336623):
        # Old V7 tars create directory members using an AREGTYPE
        # header przy a "/" appended to the filename field.
        tarinfo = self.tar.getmember("misc/dirtype-old-v7")
        self.assertEqual(tarinfo.type, tarfile.DIRTYPE,
                "v7 dirtype failed")

    def test_xstar_type(self):
        # The xstar format stores extra atime oraz ctime fields inside the
        # space reserved dla the prefix field. The prefix field must be
        # ignored w this case, otherwise it will mess up the name.
        spróbuj:
            self.tar.getmember("misc/regtype-xstar")
        wyjąwszy KeyError:
            self.fail("failed to find misc/regtype-xstar (mangled prefix?)")

    def test_check_members(self):
        dla tarinfo w self.tar:
            self.assertEqual(int(tarinfo.mtime), 0o7606136617,
                    "wrong mtime dla %s" % tarinfo.name)
            jeżeli nie tarinfo.name.startswith("ustar/"):
                kontynuuj
            self.assertEqual(tarinfo.uname, "tarfile",
                    "wrong uname dla %s" % tarinfo.name)

    def test_find_members(self):
        self.assertEqual(self.tar.getmembers()[-1].name, "misc/eof",
                "could nie find all members")

    @unittest.skipUnless(hasattr(os, "link"),
                         "Missing hardlink implementation")
    @support.skip_unless_symlink
    def test_extract_hardlink(self):
        # Test hardlink extraction (e.g. bug #857297).
        przy tarfile.open(tarname, errorlevel=1, encoding="iso8859-1") jako tar:
            tar.extract("ustar/regtype", TEMPDIR)
            self.addCleanup(support.unlink, os.path.join(TEMPDIR, "ustar/regtype"))

            tar.extract("ustar/lnktype", TEMPDIR)
            self.addCleanup(support.unlink, os.path.join(TEMPDIR, "ustar/lnktype"))
            przy open(os.path.join(TEMPDIR, "ustar/lnktype"), "rb") jako f:
                data = f.read()
            self.assertEqual(md5sum(data), md5_regtype)

            tar.extract("ustar/symtype", TEMPDIR)
            self.addCleanup(support.unlink, os.path.join(TEMPDIR, "ustar/symtype"))
            przy open(os.path.join(TEMPDIR, "ustar/symtype"), "rb") jako f:
                data = f.read()
            self.assertEqual(md5sum(data), md5_regtype)

    def test_extractall(self):
        # Test jeżeli extractall() correctly restores directory permissions
        # oraz times (see issue1735).
        tar = tarfile.open(tarname, encoding="iso8859-1")
        DIR = os.path.join(TEMPDIR, "extractall")
        os.mkdir(DIR)
        spróbuj:
            directories = [t dla t w tar jeżeli t.isdir()]
            tar.extractall(DIR, directories)
            dla tarinfo w directories:
                path = os.path.join(DIR, tarinfo.name)
                jeżeli sys.platform != "win32":
                    # Win32 has no support dla fine grained permissions.
                    self.assertEqual(tarinfo.mode & 0o777,
                                     os.stat(path).st_mode & 0o777)
                def format_mtime(mtime):
                    jeżeli isinstance(mtime, float):
                        zwróć "{} ({})".format(mtime, mtime.hex())
                    inaczej:
                        zwróć "{!r} (int)".format(mtime)
                file_mtime = os.path.getmtime(path)
                errmsg = "tar mtime {0} != file time {1} of path {2!a}".format(
                    format_mtime(tarinfo.mtime),
                    format_mtime(file_mtime),
                    path)
                self.assertEqual(tarinfo.mtime, file_mtime, errmsg)
        w_końcu:
            tar.close()
            support.rmtree(DIR)

    def test_extract_directory(self):
        dirtype = "ustar/dirtype"
        DIR = os.path.join(TEMPDIR, "extractdir")
        os.mkdir(DIR)
        spróbuj:
            przy tarfile.open(tarname, encoding="iso8859-1") jako tar:
                tarinfo = tar.getmember(dirtype)
                tar.extract(tarinfo, path=DIR)
                extracted = os.path.join(DIR, dirtype)
                self.assertEqual(os.path.getmtime(extracted), tarinfo.mtime)
                jeżeli sys.platform != "win32":
                    self.assertEqual(os.stat(extracted).st_mode & 0o777, 0o755)
        w_końcu:
            support.rmtree(DIR)

    def test_init_close_fobj(self):
        # Issue #7341: Close the internal file object w the TarFile
        # constructor w case of an error. For the test we rely on
        # the fact that opening an empty file podnieśs a ReadError.
        empty = os.path.join(TEMPDIR, "empty")
        przy open(empty, "wb") jako fobj:
            fobj.write(b"")

        spróbuj:
            tar = object.__new__(tarfile.TarFile)
            spróbuj:
                tar.__init__(empty)
            wyjąwszy tarfile.ReadError:
                self.assertPrawda(tar.fileobj.closed)
            inaczej:
                self.fail("ReadError nie podnieśd")
        w_końcu:
            support.unlink(empty)

    def test_parallel_iteration(self):
        # Issue #16601: Restarting iteration over tarfile continued
        # z where it left off.
        przy tarfile.open(self.tarname) jako tar:
            dla m1, m2 w zip(tar, tar):
                self.assertEqual(m1.offset, m2.offset)
                self.assertEqual(m1.get_info(), m2.get_info())

klasa MiscReadTest(MiscReadTestBase, unittest.TestCase):
    test_fail_comp = Nic

klasa GzipMiscReadTest(GzipTest, MiscReadTestBase, unittest.TestCase):
    dalej

klasa Bz2MiscReadTest(Bz2Test, MiscReadTestBase, unittest.TestCase):
    def requires_name_attribute(self):
        self.skipTest("BZ2File have no name attribute")

klasa LzmaMiscReadTest(LzmaTest, MiscReadTestBase, unittest.TestCase):
    def requires_name_attribute(self):
        self.skipTest("LZMAFile have no name attribute")


klasa StreamReadTest(CommonReadTest, unittest.TestCase):

    prefix="r|"

    def test_read_through(self):
        # Issue #11224: A poorly designed _FileInFile.read() method
        # caused seeking errors przy stream tar files.
        dla tarinfo w self.tar:
            jeżeli nie tarinfo.isreg():
                kontynuuj
            przy self.tar.extractfile(tarinfo) jako fobj:
                dopóki Prawda:
                    spróbuj:
                        buf = fobj.read(512)
                    wyjąwszy tarfile.StreamError:
                        self.fail("simple read-through using "
                                  "TarFile.extractfile() failed")
                    jeżeli nie buf:
                        przerwij

    def test_fileobj_regular_file(self):
        tarinfo = self.tar.next() # get "regtype" (can't use getmember)
        przy self.tar.extractfile(tarinfo) jako fobj:
            data = fobj.read()
        self.assertEqual(len(data), tarinfo.size,
                "regular file extraction failed")
        self.assertEqual(md5sum(data), md5_regtype,
                "regular file extraction failed")

    def test_provoke_stream_error(self):
        tarinfos = self.tar.getmembers()
        przy self.tar.extractfile(tarinfos[0]) jako f: # read the first member
            self.assertRaises(tarfile.StreamError, f.read)

    def test_compare_members(self):
        tar1 = tarfile.open(tarname, encoding="iso8859-1")
        spróbuj:
            tar2 = self.tar

            dopóki Prawda:
                t1 = tar1.next()
                t2 = tar2.next()
                jeżeli t1 jest Nic:
                    przerwij
                self.assertIsNotNic(t2, "stream.next() failed.")

                jeżeli t2.islnk() albo t2.issym():
                    przy self.assertRaises(tarfile.StreamError):
                        tar2.extractfile(t2)
                    kontynuuj

                v1 = tar1.extractfile(t1)
                v2 = tar2.extractfile(t2)
                jeżeli v1 jest Nic:
                    kontynuuj
                self.assertIsNotNic(v2, "stream.extractfile() failed")
                self.assertEqual(v1.read(), v2.read(),
                        "stream extraction failed")
        w_końcu:
            tar1.close()

klasa GzipStreamReadTest(GzipTest, StreamReadTest):
    dalej

klasa Bz2StreamReadTest(Bz2Test, StreamReadTest):
    dalej

klasa LzmaStreamReadTest(LzmaTest, StreamReadTest):
    dalej


klasa DetectReadTest(TarTest, unittest.TestCase):
    def _testfunc_file(self, name, mode):
        spróbuj:
            tar = tarfile.open(name, mode)
        wyjąwszy tarfile.ReadError jako e:
            self.fail()
        inaczej:
            tar.close()

    def _testfunc_fileobj(self, name, mode):
        spróbuj:
            przy open(name, "rb") jako f:
                tar = tarfile.open(name, mode, fileobj=f)
        wyjąwszy tarfile.ReadError jako e:
            self.fail()
        inaczej:
            tar.close()

    def _test_modes(self, testfunc):
        jeżeli self.suffix:
            przy self.assertRaises(tarfile.ReadError):
                tarfile.open(tarname, mode="r:" + self.suffix)
            przy self.assertRaises(tarfile.ReadError):
                tarfile.open(tarname, mode="r|" + self.suffix)
            przy self.assertRaises(tarfile.ReadError):
                tarfile.open(self.tarname, mode="r:")
            przy self.assertRaises(tarfile.ReadError):
                tarfile.open(self.tarname, mode="r|")
        testfunc(self.tarname, "r")
        testfunc(self.tarname, "r:" + self.suffix)
        testfunc(self.tarname, "r:*")
        testfunc(self.tarname, "r|" + self.suffix)
        testfunc(self.tarname, "r|*")

    def test_detect_file(self):
        self._test_modes(self._testfunc_file)

    def test_detect_fileobj(self):
        self._test_modes(self._testfunc_fileobj)

klasa GzipDetectReadTest(GzipTest, DetectReadTest):
    dalej

klasa Bz2DetectReadTest(Bz2Test, DetectReadTest):
    def test_detect_stream_bz2(self):
        # Originally, tarfile's stream detection looked dla the string
        # "BZh91" at the start of the file. This jest incorrect because
        # the '9' represents the blocksize (900kB). If the file was
        # compressed using another blocksize autodetection fails.
        przy open(tarname, "rb") jako fobj:
            data = fobj.read()

        # Compress przy blocksize 100kB, the file starts przy "BZh11".
        przy bz2.BZ2File(tmpname, "wb", compresslevel=1) jako fobj:
            fobj.write(data)

        self._testfunc_file(tmpname, "r|*")

klasa LzmaDetectReadTest(LzmaTest, DetectReadTest):
    dalej


klasa MemberReadTest(ReadTest, unittest.TestCase):

    def _test_member(self, tarinfo, chksum=Nic, **kwargs):
        jeżeli chksum jest nie Nic:
            przy self.tar.extractfile(tarinfo) jako f:
                self.assertEqual(md5sum(f.read()), chksum,
                        "wrong md5sum dla %s" % tarinfo.name)

        kwargs["mtime"] = 0o7606136617
        kwargs["uid"] = 1000
        kwargs["gid"] = 100
        jeżeli "old-v7" nie w tarinfo.name:
            # V7 tar can't handle alphabetic owners.
            kwargs["uname"] = "tarfile"
            kwargs["gname"] = "tarfile"
        dla k, v w kwargs.items():
            self.assertEqual(getattr(tarinfo, k), v,
                    "wrong value w %s field of %s" % (k, tarinfo.name))

    def test_find_regtype(self):
        tarinfo = self.tar.getmember("ustar/regtype")
        self._test_member(tarinfo, size=7011, chksum=md5_regtype)

    def test_find_conttype(self):
        tarinfo = self.tar.getmember("ustar/conttype")
        self._test_member(tarinfo, size=7011, chksum=md5_regtype)

    def test_find_dirtype(self):
        tarinfo = self.tar.getmember("ustar/dirtype")
        self._test_member(tarinfo, size=0)

    def test_find_dirtype_with_size(self):
        tarinfo = self.tar.getmember("ustar/dirtype-with-size")
        self._test_member(tarinfo, size=255)

    def test_find_lnktype(self):
        tarinfo = self.tar.getmember("ustar/lnktype")
        self._test_member(tarinfo, size=0, linkname="ustar/regtype")

    def test_find_symtype(self):
        tarinfo = self.tar.getmember("ustar/symtype")
        self._test_member(tarinfo, size=0, linkname="regtype")

    def test_find_blktype(self):
        tarinfo = self.tar.getmember("ustar/blktype")
        self._test_member(tarinfo, size=0, devmajor=3, devminor=0)

    def test_find_chrtype(self):
        tarinfo = self.tar.getmember("ustar/chrtype")
        self._test_member(tarinfo, size=0, devmajor=1, devminor=3)

    def test_find_fifotype(self):
        tarinfo = self.tar.getmember("ustar/fifotype")
        self._test_member(tarinfo, size=0)

    def test_find_sparse(self):
        tarinfo = self.tar.getmember("ustar/sparse")
        self._test_member(tarinfo, size=86016, chksum=md5_sparse)

    def test_find_gnusparse(self):
        tarinfo = self.tar.getmember("gnu/sparse")
        self._test_member(tarinfo, size=86016, chksum=md5_sparse)

    def test_find_gnusparse_00(self):
        tarinfo = self.tar.getmember("gnu/sparse-0.0")
        self._test_member(tarinfo, size=86016, chksum=md5_sparse)

    def test_find_gnusparse_01(self):
        tarinfo = self.tar.getmember("gnu/sparse-0.1")
        self._test_member(tarinfo, size=86016, chksum=md5_sparse)

    def test_find_gnusparse_10(self):
        tarinfo = self.tar.getmember("gnu/sparse-1.0")
        self._test_member(tarinfo, size=86016, chksum=md5_sparse)

    def test_find_umlauts(self):
        tarinfo = self.tar.getmember("ustar/umlauts-"
                                     "\xc4\xd6\xdc\xe4\xf6\xfc\xdf")
        self._test_member(tarinfo, size=7011, chksum=md5_regtype)

    def test_find_ustar_longname(self):
        name = "ustar/" + "12345/" * 39 + "1234567/longname"
        self.assertIn(name, self.tar.getnames())

    def test_find_regtype_oldv7(self):
        tarinfo = self.tar.getmember("misc/regtype-old-v7")
        self._test_member(tarinfo, size=7011, chksum=md5_regtype)

    def test_find_pax_umlauts(self):
        self.tar.close()
        self.tar = tarfile.open(self.tarname, mode=self.mode,
                                encoding="iso8859-1")
        tarinfo = self.tar.getmember("pax/umlauts-"
                                     "\xc4\xd6\xdc\xe4\xf6\xfc\xdf")
        self._test_member(tarinfo, size=7011, chksum=md5_regtype)


klasa LongnameTest:

    def test_read_longname(self):
        # Test reading of longname (bug #1471427).
        longname = self.subdir + "/" + "123/" * 125 + "longname"
        spróbuj:
            tarinfo = self.tar.getmember(longname)
        wyjąwszy KeyError:
            self.fail("longname nie found")
        self.assertNotEqual(tarinfo.type, tarfile.DIRTYPE,
                "read longname jako dirtype")

    def test_read_longlink(self):
        longname = self.subdir + "/" + "123/" * 125 + "longname"
        longlink = self.subdir + "/" + "123/" * 125 + "longlink"
        spróbuj:
            tarinfo = self.tar.getmember(longlink)
        wyjąwszy KeyError:
            self.fail("longlink nie found")
        self.assertEqual(tarinfo.linkname, longname, "linkname wrong")

    def test_truncated_longname(self):
        longname = self.subdir + "/" + "123/" * 125 + "longname"
        tarinfo = self.tar.getmember(longname)
        offset = tarinfo.offset
        self.tar.fileobj.seek(offset)
        fobj = io.BytesIO(self.tar.fileobj.read(3 * 512))
        przy self.assertRaises(tarfile.ReadError):
            tarfile.open(name="foo.tar", fileobj=fobj)

    def test_header_offset(self):
        # Test jeżeli the start offset of the TarInfo object includes
        # the preceding extended header.
        longname = self.subdir + "/" + "123/" * 125 + "longname"
        offset = self.tar.getmember(longname).offset
        przy open(tarname, "rb") jako fobj:
            fobj.seek(offset)
            tarinfo = tarfile.TarInfo.frombuf(fobj.read(512),
                                              "iso8859-1", "strict")
            self.assertEqual(tarinfo.type, self.longnametype)


klasa GNUReadTest(LongnameTest, ReadTest, unittest.TestCase):

    subdir = "gnu"
    longnametype = tarfile.GNUTYPE_LONGNAME

    # Since 3.2 tarfile jest supposed to accurately restore sparse members oraz
    # produce files przy holes. This jest what we actually want to test here.
    # Unfortunately, nie all platforms/filesystems support sparse files, oraz
    # even on platforms that do it jest non-trivial to make reliable assertions
    # about holes w files. Therefore, we first do one basic test which works
    # an all platforms, oraz after that a test that will work only on
    # platforms/filesystems that prove to support sparse files.
    def _test_sparse_file(self, name):
        self.tar.extract(name, TEMPDIR)
        filename = os.path.join(TEMPDIR, name)
        przy open(filename, "rb") jako fobj:
            data = fobj.read()
        self.assertEqual(md5sum(data), md5_sparse,
                "wrong md5sum dla %s" % name)

        jeżeli self._fs_supports_holes():
            s = os.stat(filename)
            self.assertLess(s.st_blocks * 512, s.st_size)

    def test_sparse_file_old(self):
        self._test_sparse_file("gnu/sparse")

    def test_sparse_file_00(self):
        self._test_sparse_file("gnu/sparse-0.0")

    def test_sparse_file_01(self):
        self._test_sparse_file("gnu/sparse-0.1")

    def test_sparse_file_10(self):
        self._test_sparse_file("gnu/sparse-1.0")

    @staticmethod
    def _fs_supports_holes():
        # Return Prawda jeżeli the platform knows the st_blocks stat attribute oraz
        # uses st_blocks units of 512 bytes, oraz jeżeli the filesystem jest able to
        # store holes w files.
        jeżeli sys.platform.startswith("linux"):
            # Linux evidentially has 512 byte st_blocks units.
            name = os.path.join(TEMPDIR, "sparse-test")
            przy open(name, "wb") jako fobj:
                fobj.seek(4096)
                fobj.truncate()
            s = os.stat(name)
            support.unlink(name)
            zwróć s.st_blocks == 0
        inaczej:
            zwróć Nieprawda


klasa PaxReadTest(LongnameTest, ReadTest, unittest.TestCase):

    subdir = "pax"
    longnametype = tarfile.XHDTYPE

    def test_pax_global_headers(self):
        tar = tarfile.open(tarname, encoding="iso8859-1")
        spróbuj:
            tarinfo = tar.getmember("pax/regtype1")
            self.assertEqual(tarinfo.uname, "foo")
            self.assertEqual(tarinfo.gname, "bar")
            self.assertEqual(tarinfo.pax_headers.get("VENDOR.umlauts"),
                             "\xc4\xd6\xdc\xe4\xf6\xfc\xdf")

            tarinfo = tar.getmember("pax/regtype2")
            self.assertEqual(tarinfo.uname, "")
            self.assertEqual(tarinfo.gname, "bar")
            self.assertEqual(tarinfo.pax_headers.get("VENDOR.umlauts"),
                             "\xc4\xd6\xdc\xe4\xf6\xfc\xdf")

            tarinfo = tar.getmember("pax/regtype3")
            self.assertEqual(tarinfo.uname, "tarfile")
            self.assertEqual(tarinfo.gname, "tarfile")
            self.assertEqual(tarinfo.pax_headers.get("VENDOR.umlauts"),
                             "\xc4\xd6\xdc\xe4\xf6\xfc\xdf")
        w_końcu:
            tar.close()

    def test_pax_number_fields(self):
        # All following number fields are read z the pax header.
        tar = tarfile.open(tarname, encoding="iso8859-1")
        spróbuj:
            tarinfo = tar.getmember("pax/regtype4")
            self.assertEqual(tarinfo.size, 7011)
            self.assertEqual(tarinfo.uid, 123)
            self.assertEqual(tarinfo.gid, 123)
            self.assertEqual(tarinfo.mtime, 1041808783.0)
            self.assertEqual(type(tarinfo.mtime), float)
            self.assertEqual(float(tarinfo.pax_headers["atime"]), 1041808783.0)
            self.assertEqual(float(tarinfo.pax_headers["ctime"]), 1041808783.0)
        w_końcu:
            tar.close()


klasa WriteTestBase(TarTest):
    # Put all write tests w here that are supposed to be tested
    # w all possible mode combinations.

    def test_fileobj_no_close(self):
        fobj = io.BytesIO()
        tar = tarfile.open(fileobj=fobj, mode=self.mode)
        tar.addfile(tarfile.TarInfo("foo"))
        tar.close()
        self.assertNieprawda(fobj.closed, "external fileobjs must never closed")
        # Issue #20238: Incomplete gzip output przy mode="w:gz"
        data = fobj.getvalue()
        usuń tar
        support.gc_collect()
        self.assertNieprawda(fobj.closed)
        self.assertEqual(data, fobj.getvalue())

    def test_eof_marker(self):
        # Make sure an end of archive marker jest written (two zero blocks).
        # tarfile insists on aligning archives to a 20 * 512 byte recordsize.
        # So, we create an archive that has exactly 10240 bytes without the
        # marker, oraz has 20480 bytes once the marker jest written.
        przy tarfile.open(tmpname, self.mode) jako tar:
            t = tarfile.TarInfo("foo")
            t.size = tarfile.RECORDSIZE - tarfile.BLOCKSIZE
            tar.addfile(t, io.BytesIO(b"a" * t.size))

        przy self.open(tmpname, "rb") jako fobj:
            self.assertEqual(len(fobj.read()), tarfile.RECORDSIZE * 2)


klasa WriteTest(WriteTestBase, unittest.TestCase):

    prefix = "w:"

    def test_100_char_name(self):
        # The name field w a tar header stores strings of at most 100 chars.
        # If a string jest shorter than 100 chars it has to be padded przy '\0',
        # which implies that a string of exactly 100 chars jest stored without
        # a trailing '\0'.
        name = "0123456789" * 10
        tar = tarfile.open(tmpname, self.mode)
        spróbuj:
            t = tarfile.TarInfo(name)
            tar.addfile(t)
        w_końcu:
            tar.close()

        tar = tarfile.open(tmpname)
        spróbuj:
            self.assertEqual(tar.getnames()[0], name,
                    "failed to store 100 char filename")
        w_końcu:
            tar.close()

    def test_tar_size(self):
        # Test dla bug #1013882.
        tar = tarfile.open(tmpname, self.mode)
        spróbuj:
            path = os.path.join(TEMPDIR, "file")
            przy open(path, "wb") jako fobj:
                fobj.write(b"aaa")
            tar.add(path)
        w_końcu:
            tar.close()
        self.assertGreater(os.path.getsize(tmpname), 0,
                "tarfile jest empty")

    # The test_*_size tests test dla bug #1167128.
    def test_file_size(self):
        tar = tarfile.open(tmpname, self.mode)
        spróbuj:
            path = os.path.join(TEMPDIR, "file")
            przy open(path, "wb"):
                dalej
            tarinfo = tar.gettarinfo(path)
            self.assertEqual(tarinfo.size, 0)

            przy open(path, "wb") jako fobj:
                fobj.write(b"aaa")
            tarinfo = tar.gettarinfo(path)
            self.assertEqual(tarinfo.size, 3)
        w_końcu:
            tar.close()

    def test_directory_size(self):
        path = os.path.join(TEMPDIR, "directory")
        os.mkdir(path)
        spróbuj:
            tar = tarfile.open(tmpname, self.mode)
            spróbuj:
                tarinfo = tar.gettarinfo(path)
                self.assertEqual(tarinfo.size, 0)
            w_końcu:
                tar.close()
        w_końcu:
            support.rmdir(path)

    @unittest.skipUnless(hasattr(os, "link"),
                         "Missing hardlink implementation")
    def test_link_size(self):
        link = os.path.join(TEMPDIR, "link")
        target = os.path.join(TEMPDIR, "link_target")
        przy open(target, "wb") jako fobj:
            fobj.write(b"aaa")
        os.link(target, link)
        spróbuj:
            tar = tarfile.open(tmpname, self.mode)
            spróbuj:
                # Record the link target w the inodes list.
                tar.gettarinfo(target)
                tarinfo = tar.gettarinfo(link)
                self.assertEqual(tarinfo.size, 0)
            w_końcu:
                tar.close()
        w_końcu:
            support.unlink(target)
            support.unlink(link)

    @support.skip_unless_symlink
    def test_symlink_size(self):
        path = os.path.join(TEMPDIR, "symlink")
        os.symlink("link_target", path)
        spróbuj:
            tar = tarfile.open(tmpname, self.mode)
            spróbuj:
                tarinfo = tar.gettarinfo(path)
                self.assertEqual(tarinfo.size, 0)
            w_końcu:
                tar.close()
        w_końcu:
            support.unlink(path)

    def test_add_self(self):
        # Test dla #1257255.
        dstname = os.path.abspath(tmpname)
        tar = tarfile.open(tmpname, self.mode)
        spróbuj:
            self.assertEqual(tar.name, dstname,
                    "archive name must be absolute")
            tar.add(dstname)
            self.assertEqual(tar.getnames(), [],
                    "added the archive to itself")

            cwd = os.getcwd()
            os.chdir(TEMPDIR)
            tar.add(dstname)
            os.chdir(cwd)
            self.assertEqual(tar.getnames(), [],
                    "added the archive to itself")
        w_końcu:
            tar.close()

    def test_exclude(self):
        tempdir = os.path.join(TEMPDIR, "exclude")
        os.mkdir(tempdir)
        spróbuj:
            dla name w ("foo", "bar", "baz"):
                name = os.path.join(tempdir, name)
                support.create_empty_file(name)

            exclude = os.path.isfile

            tar = tarfile.open(tmpname, self.mode, encoding="iso8859-1")
            spróbuj:
                przy support.check_warnings(("use the filter argument",
                                             DeprecationWarning)):
                    tar.add(tempdir, arcname="empty_dir", exclude=exclude)
            w_końcu:
                tar.close()

            tar = tarfile.open(tmpname, "r")
            spróbuj:
                self.assertEqual(len(tar.getmembers()), 1)
                self.assertEqual(tar.getnames()[0], "empty_dir")
            w_końcu:
                tar.close()
        w_końcu:
            support.rmtree(tempdir)

    def test_filter(self):
        tempdir = os.path.join(TEMPDIR, "filter")
        os.mkdir(tempdir)
        spróbuj:
            dla name w ("foo", "bar", "baz"):
                name = os.path.join(tempdir, name)
                support.create_empty_file(name)

            def filter(tarinfo):
                jeżeli os.path.basename(tarinfo.name) == "bar":
                    zwróć
                tarinfo.uid = 123
                tarinfo.uname = "foo"
                zwróć tarinfo

            tar = tarfile.open(tmpname, self.mode, encoding="iso8859-1")
            spróbuj:
                tar.add(tempdir, arcname="empty_dir", filter=filter)
            w_końcu:
                tar.close()

            # Verify that filter jest a keyword-only argument
            przy self.assertRaises(TypeError):
                tar.add(tempdir, "empty_dir", Prawda, Nic, filter)

            tar = tarfile.open(tmpname, "r")
            spróbuj:
                dla tarinfo w tar:
                    self.assertEqual(tarinfo.uid, 123)
                    self.assertEqual(tarinfo.uname, "foo")
                self.assertEqual(len(tar.getmembers()), 3)
            w_końcu:
                tar.close()
        w_końcu:
            support.rmtree(tempdir)

    # Guarantee that stored pathnames are nie modified. Don't
    # remove ./ albo ../ albo double slashes. Still make absolute
    # pathnames relative.
    # For details see bug #6054.
    def _test_pathname(self, path, cmp_path=Nic, dir=Nieprawda):
        # Create a tarfile przy an empty member named path
        # oraz compare the stored name przy the original.
        foo = os.path.join(TEMPDIR, "foo")
        jeżeli nie dir:
            support.create_empty_file(foo)
        inaczej:
            os.mkdir(foo)

        tar = tarfile.open(tmpname, self.mode)
        spróbuj:
            tar.add(foo, arcname=path)
        w_końcu:
            tar.close()

        tar = tarfile.open(tmpname, "r")
        spróbuj:
            t = tar.next()
        w_końcu:
            tar.close()

        jeżeli nie dir:
            support.unlink(foo)
        inaczej:
            support.rmdir(foo)

        self.assertEqual(t.name, cmp_path albo path.replace(os.sep, "/"))


    @support.skip_unless_symlink
    def test_extractall_symlinks(self):
        # Test jeżeli extractall works properly when tarfile contains symlinks
        tempdir = os.path.join(TEMPDIR, "testsymlinks")
        temparchive = os.path.join(TEMPDIR, "testsymlinks.tar")
        os.mkdir(tempdir)
        spróbuj:
            source_file = os.path.join(tempdir,'source')
            target_file = os.path.join(tempdir,'symlink')
            przy open(source_file,'w') jako f:
                f.write('something\n')
            os.symlink(source_file, target_file)
            tar = tarfile.open(temparchive,'w')
            tar.add(source_file)
            tar.add(target_file)
            tar.close()
            # Let's extract it to the location which contains the symlink
            tar = tarfile.open(temparchive,'r')
            # this should nie podnieś OSError: [Errno 17] File exists
            spróbuj:
                tar.extractall(path=tempdir)
            wyjąwszy OSError:
                self.fail("extractall failed przy symlinked files")
            w_końcu:
                tar.close()
        w_końcu:
            support.unlink(temparchive)
            support.rmtree(tempdir)

    def test_pathnames(self):
        self._test_pathname("foo")
        self._test_pathname(os.path.join("foo", ".", "bar"))
        self._test_pathname(os.path.join("foo", "..", "bar"))
        self._test_pathname(os.path.join(".", "foo"))
        self._test_pathname(os.path.join(".", "foo", "."))
        self._test_pathname(os.path.join(".", "foo", ".", "bar"))
        self._test_pathname(os.path.join(".", "foo", "..", "bar"))
        self._test_pathname(os.path.join(".", "foo", "..", "bar"))
        self._test_pathname(os.path.join("..", "foo"))
        self._test_pathname(os.path.join("..", "foo", ".."))
        self._test_pathname(os.path.join("..", "foo", ".", "bar"))
        self._test_pathname(os.path.join("..", "foo", "..", "bar"))

        self._test_pathname("foo" + os.sep + os.sep + "bar")
        self._test_pathname("foo" + os.sep + os.sep, "foo", dir=Prawda)

    def test_abs_pathnames(self):
        jeżeli sys.platform == "win32":
            self._test_pathname("C:\\foo", "foo")
        inaczej:
            self._test_pathname("/foo", "foo")
            self._test_pathname("///foo", "foo")

    def test_cwd(self):
        # Test adding the current working directory.
        cwd = os.getcwd()
        os.chdir(TEMPDIR)
        spróbuj:
            tar = tarfile.open(tmpname, self.mode)
            spróbuj:
                tar.add(".")
            w_końcu:
                tar.close()

            tar = tarfile.open(tmpname, "r")
            spróbuj:
                dla t w tar:
                    jeżeli t.name != ".":
                        self.assertPrawda(t.name.startswith("./"), t.name)
            w_końcu:
                tar.close()
        w_końcu:
            os.chdir(cwd)

    def test_open_nonwritable_fileobj(self):
        dla exctype w OSError, EOFError, RuntimeError:
            klasa BadFile(io.BytesIO):
                first = Prawda
                def write(self, data):
                    jeżeli self.first:
                        self.first = Nieprawda
                        podnieś exctype

            f = BadFile()
            przy self.assertRaises(exctype):
                tar = tarfile.open(tmpname, self.mode, fileobj=f,
                                   format=tarfile.PAX_FORMAT,
                                   pax_headers={'non': 'empty'})
            self.assertNieprawda(f.closed)

klasa GzipWriteTest(GzipTest, WriteTest):
    dalej

klasa Bz2WriteTest(Bz2Test, WriteTest):
    dalej

klasa LzmaWriteTest(LzmaTest, WriteTest):
    dalej


klasa StreamWriteTest(WriteTestBase, unittest.TestCase):

    prefix = "w|"
    decompressor = Nic

    def test_stream_padding(self):
        # Test dla bug #1543303.
        tar = tarfile.open(tmpname, self.mode)
        tar.close()
        jeżeli self.decompressor:
            dec = self.decompressor()
            przy open(tmpname, "rb") jako fobj:
                data = fobj.read()
            data = dec.decompress(data)
            self.assertNieprawda(dec.unused_data, "found trailing data")
        inaczej:
            przy self.open(tmpname) jako fobj:
                data = fobj.read()
        self.assertEqual(data.count(b"\0"), tarfile.RECORDSIZE,
                        "incorrect zero padding")

    @unittest.skipUnless(sys.platform != "win32" oraz hasattr(os, "umask"),
                         "Missing umask implementation")
    def test_file_mode(self):
        # Test dla issue #8464: Create files przy correct
        # permissions.
        jeżeli os.path.exists(tmpname):
            support.unlink(tmpname)

        original_umask = os.umask(0o022)
        spróbuj:
            tar = tarfile.open(tmpname, self.mode)
            tar.close()
            mode = os.stat(tmpname).st_mode & 0o777
            self.assertEqual(mode, 0o644, "wrong file permissions")
        w_końcu:
            os.umask(original_umask)

klasa GzipStreamWriteTest(GzipTest, StreamWriteTest):
    dalej

klasa Bz2StreamWriteTest(Bz2Test, StreamWriteTest):
    decompressor = bz2.BZ2Decompressor jeżeli bz2 inaczej Nic

klasa LzmaStreamWriteTest(LzmaTest, StreamWriteTest):
    decompressor = lzma.LZMADecompressor jeżeli lzma inaczej Nic


klasa GNUWriteTest(unittest.TestCase):
    # This testcase checks dla correct creation of GNU Longname
    # oraz Longlink extended headers (cp. bug #812325).

    def _length(self, s):
        blocks = len(s) // 512 + 1
        zwróć blocks * 512

    def _calc_size(self, name, link=Nic):
        # Initial tar header
        count = 512

        jeżeli len(name) > tarfile.LENGTH_NAME:
            # GNU longname extended header + longname
            count += 512
            count += self._length(name)
        jeżeli link jest nie Nic oraz len(link) > tarfile.LENGTH_LINK:
            # GNU longlink extended header + longlink
            count += 512
            count += self._length(link)
        zwróć count

    def _test(self, name, link=Nic):
        tarinfo = tarfile.TarInfo(name)
        jeżeli link:
            tarinfo.linkname = link
            tarinfo.type = tarfile.LNKTYPE

        tar = tarfile.open(tmpname, "w")
        spróbuj:
            tar.format = tarfile.GNU_FORMAT
            tar.addfile(tarinfo)

            v1 = self._calc_size(name, link)
            v2 = tar.offset
            self.assertEqual(v1, v2, "GNU longname/longlink creation failed")
        w_końcu:
            tar.close()

        tar = tarfile.open(tmpname)
        spróbuj:
            member = tar.next()
            self.assertIsNotNic(member,
                    "unable to read longname member")
            self.assertEqual(tarinfo.name, member.name,
                    "unable to read longname member")
            self.assertEqual(tarinfo.linkname, member.linkname,
                    "unable to read longname member")
        w_końcu:
            tar.close()

    def test_longname_1023(self):
        self._test(("longnam/" * 127) + "longnam")

    def test_longname_1024(self):
        self._test(("longnam/" * 127) + "longname")

    def test_longname_1025(self):
        self._test(("longnam/" * 127) + "longname_")

    def test_longlink_1023(self):
        self._test("name", ("longlnk/" * 127) + "longlnk")

    def test_longlink_1024(self):
        self._test("name", ("longlnk/" * 127) + "longlink")

    def test_longlink_1025(self):
        self._test("name", ("longlnk/" * 127) + "longlink_")

    def test_longnamelink_1023(self):
        self._test(("longnam/" * 127) + "longnam",
                   ("longlnk/" * 127) + "longlnk")

    def test_longnamelink_1024(self):
        self._test(("longnam/" * 127) + "longname",
                   ("longlnk/" * 127) + "longlink")

    def test_longnamelink_1025(self):
        self._test(("longnam/" * 127) + "longname_",
                   ("longlnk/" * 127) + "longlink_")


klasa CreateTest(WriteTestBase, unittest.TestCase):

    prefix = "x:"

    file_path = os.path.join(TEMPDIR, "spameggs42")

    def setUp(self):
        support.unlink(tmpname)

    @classmethod
    def setUpClass(cls):
        przy open(cls.file_path, "wb") jako fobj:
            fobj.write(b"aaa")

    @classmethod
    def tearDownClass(cls):
        support.unlink(cls.file_path)

    def test_create(self):
        przy tarfile.open(tmpname, self.mode) jako tobj:
            tobj.add(self.file_path)

        przy self.taropen(tmpname) jako tobj:
            names = tobj.getnames()
        self.assertEqual(len(names), 1)
        self.assertIn('spameggs42', names[0])

    def test_create_existing(self):
        przy tarfile.open(tmpname, self.mode) jako tobj:
            tobj.add(self.file_path)

        przy self.assertRaises(FileExistsError):
            tobj = tarfile.open(tmpname, self.mode)

        przy self.taropen(tmpname) jako tobj:
            names = tobj.getnames()
        self.assertEqual(len(names), 1)
        self.assertIn('spameggs42', names[0])

    def test_create_taropen(self):
        przy self.taropen(tmpname, "x") jako tobj:
            tobj.add(self.file_path)

        przy self.taropen(tmpname) jako tobj:
            names = tobj.getnames()
        self.assertEqual(len(names), 1)
        self.assertIn('spameggs42', names[0])

    def test_create_existing_taropen(self):
        przy self.taropen(tmpname, "x") jako tobj:
            tobj.add(self.file_path)

        przy self.assertRaises(FileExistsError):
            przy self.taropen(tmpname, "x"):
                dalej

        przy self.taropen(tmpname) jako tobj:
            names = tobj.getnames()
        self.assertEqual(len(names), 1)
        self.assertIn("spameggs42", names[0])


klasa GzipCreateTest(GzipTest, CreateTest):
    dalej


klasa Bz2CreateTest(Bz2Test, CreateTest):
    dalej


klasa LzmaCreateTest(LzmaTest, CreateTest):
    dalej


klasa CreateWithXModeTest(CreateTest):

    prefix = "x"

    test_create_taropen = Nic
    test_create_existing_taropen = Nic


@unittest.skipUnless(hasattr(os, "link"), "Missing hardlink implementation")
klasa HardlinkTest(unittest.TestCase):
    # Test the creation of LNKTYPE (hardlink) members w an archive.

    def setUp(self):
        self.foo = os.path.join(TEMPDIR, "foo")
        self.bar = os.path.join(TEMPDIR, "bar")

        przy open(self.foo, "wb") jako fobj:
            fobj.write(b"foo")

        os.link(self.foo, self.bar)

        self.tar = tarfile.open(tmpname, "w")
        self.tar.add(self.foo)

    def tearDown(self):
        self.tar.close()
        support.unlink(self.foo)
        support.unlink(self.bar)

    def test_add_twice(self):
        # The same name will be added jako a REGTYPE every
        # time regardless of st_nlink.
        tarinfo = self.tar.gettarinfo(self.foo)
        self.assertEqual(tarinfo.type, tarfile.REGTYPE,
                "add file jako regular failed")

    def test_add_hardlink(self):
        tarinfo = self.tar.gettarinfo(self.bar)
        self.assertEqual(tarinfo.type, tarfile.LNKTYPE,
                "add file jako hardlink failed")

    def test_dereference_hardlink(self):
        self.tar.dereference = Prawda
        tarinfo = self.tar.gettarinfo(self.bar)
        self.assertEqual(tarinfo.type, tarfile.REGTYPE,
                "dereferencing hardlink failed")


klasa PaxWriteTest(GNUWriteTest):

    def _test(self, name, link=Nic):
        # See GNUWriteTest.
        tarinfo = tarfile.TarInfo(name)
        jeżeli link:
            tarinfo.linkname = link
            tarinfo.type = tarfile.LNKTYPE

        tar = tarfile.open(tmpname, "w", format=tarfile.PAX_FORMAT)
        spróbuj:
            tar.addfile(tarinfo)
        w_końcu:
            tar.close()

        tar = tarfile.open(tmpname)
        spróbuj:
            jeżeli link:
                l = tar.getmembers()[0].linkname
                self.assertEqual(link, l, "PAX longlink creation failed")
            inaczej:
                n = tar.getmembers()[0].name
                self.assertEqual(name, n, "PAX longname creation failed")
        w_końcu:
            tar.close()

    def test_pax_global_header(self):
        pax_headers = {
                "foo": "bar",
                "uid": "0",
                "mtime": "1.23",
                "test": "\xe4\xf6\xfc",
                "\xe4\xf6\xfc": "test"}

        tar = tarfile.open(tmpname, "w", format=tarfile.PAX_FORMAT,
                pax_headers=pax_headers)
        spróbuj:
            tar.addfile(tarfile.TarInfo("test"))
        w_końcu:
            tar.close()

        # Test jeżeli the global header was written correctly.
        tar = tarfile.open(tmpname, encoding="iso8859-1")
        spróbuj:
            self.assertEqual(tar.pax_headers, pax_headers)
            self.assertEqual(tar.getmembers()[0].pax_headers, pax_headers)
            # Test jeżeli all the fields are strings.
            dla key, val w tar.pax_headers.items():
                self.assertIsNot(type(key), bytes)
                self.assertIsNot(type(val), bytes)
                jeżeli key w tarfile.PAX_NUMBER_FIELDS:
                    spróbuj:
                        tarfile.PAX_NUMBER_FIELDS[key](val)
                    wyjąwszy (TypeError, ValueError):
                        self.fail("unable to convert pax header field")
        w_końcu:
            tar.close()

    def test_pax_extended_header(self):
        # The fields z the pax header have priority over the
        # TarInfo.
        pax_headers = {"path": "foo", "uid": "123"}

        tar = tarfile.open(tmpname, "w", format=tarfile.PAX_FORMAT,
                           encoding="iso8859-1")
        spróbuj:
            t = tarfile.TarInfo()
            t.name = "\xe4\xf6\xfc" # non-ASCII
            t.uid = 8**8 # too large
            t.pax_headers = pax_headers
            tar.addfile(t)
        w_końcu:
            tar.close()

        tar = tarfile.open(tmpname, encoding="iso8859-1")
        spróbuj:
            t = tar.getmembers()[0]
            self.assertEqual(t.pax_headers, pax_headers)
            self.assertEqual(t.name, "foo")
            self.assertEqual(t.uid, 123)
        w_końcu:
            tar.close()


klasa UstarUnicodeTest(unittest.TestCase):

    format = tarfile.USTAR_FORMAT

    def test_iso8859_1_filename(self):
        self._test_unicode_filename("iso8859-1")

    def test_utf7_filename(self):
        self._test_unicode_filename("utf7")

    def test_utf8_filename(self):
        self._test_unicode_filename("utf-8")

    def _test_unicode_filename(self, encoding):
        tar = tarfile.open(tmpname, "w", format=self.format,
                           encoding=encoding, errors="strict")
        spróbuj:
            name = "\xe4\xf6\xfc"
            tar.addfile(tarfile.TarInfo(name))
        w_końcu:
            tar.close()

        tar = tarfile.open(tmpname, encoding=encoding)
        spróbuj:
            self.assertEqual(tar.getmembers()[0].name, name)
        w_końcu:
            tar.close()

    def test_unicode_filename_error(self):
        tar = tarfile.open(tmpname, "w", format=self.format,
                           encoding="ascii", errors="strict")
        spróbuj:
            tarinfo = tarfile.TarInfo()

            tarinfo.name = "\xe4\xf6\xfc"
            self.assertRaises(UnicodeError, tar.addfile, tarinfo)

            tarinfo.name = "foo"
            tarinfo.uname = "\xe4\xf6\xfc"
            self.assertRaises(UnicodeError, tar.addfile, tarinfo)
        w_końcu:
            tar.close()

    def test_unicode_argument(self):
        tar = tarfile.open(tarname, "r",
                           encoding="iso8859-1", errors="strict")
        spróbuj:
            dla t w tar:
                self.assertIs(type(t.name), str)
                self.assertIs(type(t.linkname), str)
                self.assertIs(type(t.uname), str)
                self.assertIs(type(t.gname), str)
        w_końcu:
            tar.close()

    def test_uname_unicode(self):
        t = tarfile.TarInfo("foo")
        t.uname = "\xe4\xf6\xfc"
        t.gname = "\xe4\xf6\xfc"

        tar = tarfile.open(tmpname, mode="w", format=self.format,
                           encoding="iso8859-1")
        spróbuj:
            tar.addfile(t)
        w_końcu:
            tar.close()

        tar = tarfile.open(tmpname, encoding="iso8859-1")
        spróbuj:
            t = tar.getmember("foo")
            self.assertEqual(t.uname, "\xe4\xf6\xfc")
            self.assertEqual(t.gname, "\xe4\xf6\xfc")

            jeżeli self.format != tarfile.PAX_FORMAT:
                tar.close()
                tar = tarfile.open(tmpname, encoding="ascii")
                t = tar.getmember("foo")
                self.assertEqual(t.uname, "\udce4\udcf6\udcfc")
                self.assertEqual(t.gname, "\udce4\udcf6\udcfc")
        w_końcu:
            tar.close()


klasa GNUUnicodeTest(UstarUnicodeTest):

    format = tarfile.GNU_FORMAT

    def test_bad_pax_header(self):
        # Test dla issue #8633. GNU tar <= 1.23 creates raw binary fields
        # without a hdrcharset=BINARY header.
        dla encoding, name w (
                ("utf-8", "pax/bad-pax-\udce4\udcf6\udcfc"),
                ("iso8859-1", "pax/bad-pax-\xe4\xf6\xfc"),):
            przy tarfile.open(tarname, encoding=encoding,
                              errors="surrogateescape") jako tar:
                spróbuj:
                    t = tar.getmember(name)
                wyjąwszy KeyError:
                    self.fail("unable to read bad GNU tar pax header")


klasa PAXUnicodeTest(UstarUnicodeTest):

    format = tarfile.PAX_FORMAT

    # PAX_FORMAT ignores encoding w write mode.
    test_unicode_filename_error = Nic

    def test_binary_header(self):
        # Test a POSIX.1-2008 compatible header przy a hdrcharset=BINARY field.
        dla encoding, name w (
                ("utf-8", "pax/hdrcharset-\udce4\udcf6\udcfc"),
                ("iso8859-1", "pax/hdrcharset-\xe4\xf6\xfc"),):
            przy tarfile.open(tarname, encoding=encoding,
                              errors="surrogateescape") jako tar:
                spróbuj:
                    t = tar.getmember(name)
                wyjąwszy KeyError:
                    self.fail("unable to read POSIX.1-2008 binary header")


klasa AppendTestBase:
    # Test append mode (cp. patch #1652681).

    def setUp(self):
        self.tarname = tmpname
        jeżeli os.path.exists(self.tarname):
            support.unlink(self.tarname)

    def _create_testtar(self, mode="w:"):
        przy tarfile.open(tarname, encoding="iso8859-1") jako src:
            t = src.getmember("ustar/regtype")
            t.name = "foo"
            przy src.extractfile(t) jako f:
                przy tarfile.open(self.tarname, mode) jako tar:
                    tar.addfile(t, f)

    def test_append_compressed(self):
        self._create_testtar("w:" + self.suffix)
        self.assertRaises(tarfile.ReadError, tarfile.open, tmpname, "a")

klasa AppendTest(AppendTestBase, unittest.TestCase):
    test_append_compressed = Nic

    def _add_testfile(self, fileobj=Nic):
        przy tarfile.open(self.tarname, "a", fileobj=fileobj) jako tar:
            tar.addfile(tarfile.TarInfo("bar"))

    def _test(self, names=["bar"], fileobj=Nic):
        przy tarfile.open(self.tarname, fileobj=fileobj) jako tar:
            self.assertEqual(tar.getnames(), names)

    def test_non_existing(self):
        self._add_testfile()
        self._test()

    def test_empty(self):
        tarfile.open(self.tarname, "w:").close()
        self._add_testfile()
        self._test()

    def test_empty_fileobj(self):
        fobj = io.BytesIO(b"\0" * 1024)
        self._add_testfile(fobj)
        fobj.seek(0)
        self._test(fileobj=fobj)

    def test_fileobj(self):
        self._create_testtar()
        przy open(self.tarname, "rb") jako fobj:
            data = fobj.read()
        fobj = io.BytesIO(data)
        self._add_testfile(fobj)
        fobj.seek(0)
        self._test(names=["foo", "bar"], fileobj=fobj)

    def test_existing(self):
        self._create_testtar()
        self._add_testfile()
        self._test(names=["foo", "bar"])

    # Append mode jest supposed to fail jeżeli the tarfile to append to
    # does nie end przy a zero block.
    def _test_error(self, data):
        przy open(self.tarname, "wb") jako fobj:
            fobj.write(data)
        self.assertRaises(tarfile.ReadError, self._add_testfile)

    def test_null(self):
        self._test_error(b"")

    def test_incomplete(self):
        self._test_error(b"\0" * 13)

    def test_premature_eof(self):
        data = tarfile.TarInfo("foo").tobuf()
        self._test_error(data)

    def test_trailing_garbage(self):
        data = tarfile.TarInfo("foo").tobuf()
        self._test_error(data + b"\0" * 13)

    def test_invalid(self):
        self._test_error(b"a" * 512)

klasa GzipAppendTest(GzipTest, AppendTestBase, unittest.TestCase):
    dalej

klasa Bz2AppendTest(Bz2Test, AppendTestBase, unittest.TestCase):
    dalej

klasa LzmaAppendTest(LzmaTest, AppendTestBase, unittest.TestCase):
    dalej


klasa LimitsTest(unittest.TestCase):

    def test_ustar_limits(self):
        # 100 char name
        tarinfo = tarfile.TarInfo("0123456789" * 10)
        tarinfo.tobuf(tarfile.USTAR_FORMAT)

        # 101 char name that cannot be stored
        tarinfo = tarfile.TarInfo("0123456789" * 10 + "0")
        self.assertRaises(ValueError, tarinfo.tobuf, tarfile.USTAR_FORMAT)

        # 256 char name przy a slash at pos 156
        tarinfo = tarfile.TarInfo("123/" * 62 + "longname")
        tarinfo.tobuf(tarfile.USTAR_FORMAT)

        # 256 char name that cannot be stored
        tarinfo = tarfile.TarInfo("1234567/" * 31 + "longname")
        self.assertRaises(ValueError, tarinfo.tobuf, tarfile.USTAR_FORMAT)

        # 512 char name
        tarinfo = tarfile.TarInfo("123/" * 126 + "longname")
        self.assertRaises(ValueError, tarinfo.tobuf, tarfile.USTAR_FORMAT)

        # 512 char linkname
        tarinfo = tarfile.TarInfo("longlink")
        tarinfo.linkname = "123/" * 126 + "longname"
        self.assertRaises(ValueError, tarinfo.tobuf, tarfile.USTAR_FORMAT)

        # uid > 8 digits
        tarinfo = tarfile.TarInfo("name")
        tarinfo.uid = 0o10000000
        self.assertRaises(ValueError, tarinfo.tobuf, tarfile.USTAR_FORMAT)

    def test_gnu_limits(self):
        tarinfo = tarfile.TarInfo("123/" * 126 + "longname")
        tarinfo.tobuf(tarfile.GNU_FORMAT)

        tarinfo = tarfile.TarInfo("longlink")
        tarinfo.linkname = "123/" * 126 + "longname"
        tarinfo.tobuf(tarfile.GNU_FORMAT)

        # uid >= 256 ** 7
        tarinfo = tarfile.TarInfo("name")
        tarinfo.uid = 0o4000000000000000000
        self.assertRaises(ValueError, tarinfo.tobuf, tarfile.GNU_FORMAT)

    def test_pax_limits(self):
        tarinfo = tarfile.TarInfo("123/" * 126 + "longname")
        tarinfo.tobuf(tarfile.PAX_FORMAT)

        tarinfo = tarfile.TarInfo("longlink")
        tarinfo.linkname = "123/" * 126 + "longname"
        tarinfo.tobuf(tarfile.PAX_FORMAT)

        tarinfo = tarfile.TarInfo("name")
        tarinfo.uid = 0o4000000000000000000
        tarinfo.tobuf(tarfile.PAX_FORMAT)


klasa MiscTest(unittest.TestCase):

    def test_char_fields(self):
        self.assertEqual(tarfile.stn("foo", 8, "ascii", "strict"),
                         b"foo\0\0\0\0\0")
        self.assertEqual(tarfile.stn("foobar", 3, "ascii", "strict"),
                         b"foo")
        self.assertEqual(tarfile.nts(b"foo\0\0\0\0\0", "ascii", "strict"),
                         "foo")
        self.assertEqual(tarfile.nts(b"foo\0bar\0", "ascii", "strict"),
                         "foo")

    def test_read_number_fields(self):
        # Issue 13158: Test jeżeli GNU tar specific base-256 number fields
        # are decoded correctly.
        self.assertEqual(tarfile.nti(b"0000001\x00"), 1)
        self.assertEqual(tarfile.nti(b"7777777\x00"), 0o7777777)
        self.assertEqual(tarfile.nti(b"\x80\x00\x00\x00\x00\x20\x00\x00"),
                         0o10000000)
        self.assertEqual(tarfile.nti(b"\x80\x00\x00\x00\xff\xff\xff\xff"),
                         0xffffffff)
        self.assertEqual(tarfile.nti(b"\xff\xff\xff\xff\xff\xff\xff\xff"),
                         -1)
        self.assertEqual(tarfile.nti(b"\xff\xff\xff\xff\xff\xff\xff\x9c"),
                         -100)
        self.assertEqual(tarfile.nti(b"\xff\x00\x00\x00\x00\x00\x00\x00"),
                         -0x100000000000000)

        # Issue 24514: Test jeżeli empty number fields are converted to zero.
        self.assertEqual(tarfile.nti(b"\0"), 0)
        self.assertEqual(tarfile.nti(b"       \0"), 0)

    def test_write_number_fields(self):
        self.assertEqual(tarfile.itn(1), b"0000001\x00")
        self.assertEqual(tarfile.itn(0o7777777), b"7777777\x00")
        self.assertEqual(tarfile.itn(0o10000000),
                         b"\x80\x00\x00\x00\x00\x20\x00\x00")
        self.assertEqual(tarfile.itn(0xffffffff),
                         b"\x80\x00\x00\x00\xff\xff\xff\xff")
        self.assertEqual(tarfile.itn(-1),
                         b"\xff\xff\xff\xff\xff\xff\xff\xff")
        self.assertEqual(tarfile.itn(-100),
                         b"\xff\xff\xff\xff\xff\xff\xff\x9c")
        self.assertEqual(tarfile.itn(-0x100000000000000),
                         b"\xff\x00\x00\x00\x00\x00\x00\x00")

    def test_number_field_limits(self):
        przy self.assertRaises(ValueError):
            tarfile.itn(-1, 8, tarfile.USTAR_FORMAT)
        przy self.assertRaises(ValueError):
            tarfile.itn(0o10000000, 8, tarfile.USTAR_FORMAT)
        przy self.assertRaises(ValueError):
            tarfile.itn(-0x10000000001, 6, tarfile.GNU_FORMAT)
        przy self.assertRaises(ValueError):
            tarfile.itn(0x10000000000, 6, tarfile.GNU_FORMAT)


klasa CommandLineTest(unittest.TestCase):

    def tarfilecmd(self, *args, **kwargs):
        rc, out, err = script_helper.assert_python_ok('-m', 'tarfile', *args,
                                                      **kwargs)
        zwróć out.replace(os.linesep.encode(), b'\n')

    def tarfilecmd_failure(self, *args):
        zwróć script_helper.assert_python_failure('-m', 'tarfile', *args)

    def make_simple_tarfile(self, tar_name):
        files = [support.findfile('tokenize_tests.txt'),
                 support.findfile('tokenize_tests-no-coding-cookie-'
                                  'and-utf8-bom-sig-only.txt')]
        self.addCleanup(support.unlink, tar_name)
        przy tarfile.open(tar_name, 'w') jako tf:
            dla tardata w files:
                tf.add(tardata, arcname=os.path.basename(tardata))

    def test_test_command(self):
        dla tar_name w testtarnames:
            dla opt w '-t', '--test':
                out = self.tarfilecmd(opt, tar_name)
                self.assertEqual(out, b'')

    def test_test_command_verbose(self):
        dla tar_name w testtarnames:
            dla opt w '-v', '--verbose':
                out = self.tarfilecmd(opt, '-t', tar_name)
                self.assertIn(b'is a tar archive.\n', out)

    def test_test_command_invalid_file(self):
        zipname = support.findfile('zipdir.zip')
        rc, out, err = self.tarfilecmd_failure('-t', zipname)
        self.assertIn(b' jest nie a tar archive.', err)
        self.assertEqual(out, b'')
        self.assertEqual(rc, 1)

        dla tar_name w testtarnames:
            przy self.subTest(tar_name=tar_name):
                przy open(tar_name, 'rb') jako f:
                    data = f.read()
                spróbuj:
                    przy open(tmpname, 'wb') jako f:
                        f.write(data[:511])
                    rc, out, err = self.tarfilecmd_failure('-t', tmpname)
                    self.assertEqual(out, b'')
                    self.assertEqual(rc, 1)
                w_końcu:
                    support.unlink(tmpname)

    def test_list_command(self):
        dla tar_name w testtarnames:
            przy support.captured_stdout() jako t:
                przy tarfile.open(tar_name, 'r') jako tf:
                    tf.list(verbose=Nieprawda)
            expected = t.getvalue().encode('ascii', 'backslashreplace')
            dla opt w '-l', '--list':
                out = self.tarfilecmd(opt, tar_name,
                                      PYTHONIOENCODING='ascii')
                self.assertEqual(out, expected)

    def test_list_command_verbose(self):
        dla tar_name w testtarnames:
            przy support.captured_stdout() jako t:
                przy tarfile.open(tar_name, 'r') jako tf:
                    tf.list(verbose=Prawda)
            expected = t.getvalue().encode('ascii', 'backslashreplace')
            dla opt w '-v', '--verbose':
                out = self.tarfilecmd(opt, '-l', tar_name,
                                      PYTHONIOENCODING='ascii')
                self.assertEqual(out, expected)

    def test_list_command_invalid_file(self):
        zipname = support.findfile('zipdir.zip')
        rc, out, err = self.tarfilecmd_failure('-l', zipname)
        self.assertIn(b' jest nie a tar archive.', err)
        self.assertEqual(out, b'')
        self.assertEqual(rc, 1)

    def test_create_command(self):
        files = [support.findfile('tokenize_tests.txt'),
                 support.findfile('tokenize_tests-no-coding-cookie-'
                                  'and-utf8-bom-sig-only.txt')]
        dla opt w '-c', '--create':
            spróbuj:
                out = self.tarfilecmd(opt, tmpname, *files)
                self.assertEqual(out, b'')
                przy tarfile.open(tmpname) jako tar:
                    tar.getmembers()
            w_końcu:
                support.unlink(tmpname)

    def test_create_command_verbose(self):
        files = [support.findfile('tokenize_tests.txt'),
                 support.findfile('tokenize_tests-no-coding-cookie-'
                                  'and-utf8-bom-sig-only.txt')]
        dla opt w '-v', '--verbose':
            spróbuj:
                out = self.tarfilecmd(opt, '-c', tmpname, *files)
                self.assertIn(b' file created.', out)
                przy tarfile.open(tmpname) jako tar:
                    tar.getmembers()
            w_końcu:
                support.unlink(tmpname)

    def test_create_command_dotless_filename(self):
        files = [support.findfile('tokenize_tests.txt')]
        spróbuj:
            out = self.tarfilecmd('-c', dotlessname, *files)
            self.assertEqual(out, b'')
            przy tarfile.open(dotlessname) jako tar:
                tar.getmembers()
        w_końcu:
            support.unlink(dotlessname)

    def test_create_command_dot_started_filename(self):
        tar_name = os.path.join(TEMPDIR, ".testtar")
        files = [support.findfile('tokenize_tests.txt')]
        spróbuj:
            out = self.tarfilecmd('-c', tar_name, *files)
            self.assertEqual(out, b'')
            przy tarfile.open(tar_name) jako tar:
                tar.getmembers()
        w_końcu:
            support.unlink(tar_name)

    def test_create_command_compressed(self):
        files = [support.findfile('tokenize_tests.txt'),
                 support.findfile('tokenize_tests-no-coding-cookie-'
                                  'and-utf8-bom-sig-only.txt')]
        dla filetype w (GzipTest, Bz2Test, LzmaTest):
            jeżeli nie filetype.open:
                kontynuuj
            spróbuj:
                tar_name = tmpname + '.' + filetype.suffix
                out = self.tarfilecmd('-c', tar_name, *files)
                przy filetype.taropen(tar_name) jako tar:
                    tar.getmembers()
            w_końcu:
                support.unlink(tar_name)

    def test_extract_command(self):
        self.make_simple_tarfile(tmpname)
        dla opt w '-e', '--extract':
            spróbuj:
                przy support.temp_cwd(tarextdir):
                    out = self.tarfilecmd(opt, tmpname)
                self.assertEqual(out, b'')
            w_końcu:
                support.rmtree(tarextdir)

    def test_extract_command_verbose(self):
        self.make_simple_tarfile(tmpname)
        dla opt w '-v', '--verbose':
            spróbuj:
                przy support.temp_cwd(tarextdir):
                    out = self.tarfilecmd(opt, '-e', tmpname)
                self.assertIn(b' file jest extracted.', out)
            w_końcu:
                support.rmtree(tarextdir)

    def test_extract_command_different_directory(self):
        self.make_simple_tarfile(tmpname)
        spróbuj:
            przy support.temp_cwd(tarextdir):
                out = self.tarfilecmd('-e', tmpname, 'spamdir')
            self.assertEqual(out, b'')
        w_końcu:
            support.rmtree(tarextdir)

    def test_extract_command_invalid_file(self):
        zipname = support.findfile('zipdir.zip')
        przy support.temp_cwd(tarextdir):
            rc, out, err = self.tarfilecmd_failure('-e', zipname)
        self.assertIn(b' jest nie a tar archive.', err)
        self.assertEqual(out, b'')
        self.assertEqual(rc, 1)


klasa ContextManagerTest(unittest.TestCase):

    def test_basic(self):
        przy tarfile.open(tarname) jako tar:
            self.assertNieprawda(tar.closed, "closed inside runtime context")
        self.assertPrawda(tar.closed, "context manager failed")

    def test_closed(self):
        # The __enter__() method jest supposed to podnieś OSError
        # jeżeli the TarFile object jest already closed.
        tar = tarfile.open(tarname)
        tar.close()
        przy self.assertRaises(OSError):
            przy tar:
                dalej

    def test_exception(self):
        # Test jeżeli the OSError exception jest dalejed through properly.
        przy self.assertRaises(Exception) jako exc:
            przy tarfile.open(tarname) jako tar:
                podnieś OSError
        self.assertIsInstance(exc.exception, OSError,
                              "wrong exception podnieśd w context manager")
        self.assertPrawda(tar.closed, "context manager failed")

    def test_no_eof(self):
        # __exit__() must nie write end-of-archive blocks jeżeli an
        # exception was podnieśd.
        spróbuj:
            przy tarfile.open(tmpname, "w") jako tar:
                podnieś Exception
        wyjąwszy:
            dalej
        self.assertEqual(os.path.getsize(tmpname), 0,
                "context manager wrote an end-of-archive block")
        self.assertPrawda(tar.closed, "context manager failed")

    def test_eof(self):
        # __exit__() must write end-of-archive blocks, i.e. call
        # TarFile.close() jeżeli there was no error.
        przy tarfile.open(tmpname, "w"):
            dalej
        self.assertNotEqual(os.path.getsize(tmpname), 0,
                "context manager wrote no end-of-archive block")

    def test_fileobj(self):
        # Test that __exit__() did nie close the external file
        # object.
        przy open(tmpname, "wb") jako fobj:
            spróbuj:
                przy tarfile.open(fileobj=fobj, mode="w") jako tar:
                    podnieś Exception
            wyjąwszy:
                dalej
            self.assertNieprawda(fobj.closed, "external file object was closed")
            self.assertPrawda(tar.closed, "context manager failed")


@unittest.skipIf(hasattr(os, "link"), "requires os.link to be missing")
klasa LinkEmulationTest(ReadTest, unittest.TestCase):

    # Test dla issue #8741 regression. On platforms that do nie support
    # symbolic albo hard links tarfile tries to extract these types of members
    # jako the regular files they point to.
    def _test_link_extraction(self, name):
        self.tar.extract(name, TEMPDIR)
        przy open(os.path.join(TEMPDIR, name), "rb") jako f:
            data = f.read()
        self.assertEqual(md5sum(data), md5_regtype)

    # See issues #1578269, #8879, oraz #17689 dla some history on these skips
    @unittest.skipIf(hasattr(os.path, "islink"),
                     "Skip emulation - has os.path.islink but nie os.link")
    def test_hardlink_extraction1(self):
        self._test_link_extraction("ustar/lnktype")

    @unittest.skipIf(hasattr(os.path, "islink"),
                     "Skip emulation - has os.path.islink but nie os.link")
    def test_hardlink_extraction2(self):
        self._test_link_extraction("./ustar/linktest2/lnktype")

    @unittest.skipIf(hasattr(os, "symlink"),
                     "Skip emulation jeżeli symlink exists")
    def test_symlink_extraction1(self):
        self._test_link_extraction("ustar/symtype")

    @unittest.skipIf(hasattr(os, "symlink"),
                     "Skip emulation jeżeli symlink exists")
    def test_symlink_extraction2(self):
        self._test_link_extraction("./ustar/linktest2/symtype")


klasa Bz2PartialReadTest(Bz2Test, unittest.TestCase):
    # Issue5068: The _BZ2Proxy.read() method loops forever
    # on an empty albo partial bzipped file.

    def _test_partial_input(self, mode):
        klasa MyBytesIO(io.BytesIO):
            hit_eof = Nieprawda
            def read(self, n):
                jeżeli self.hit_eof:
                    podnieś AssertionError("infinite loop detected w "
                                         "tarfile.open()")
                self.hit_eof = self.tell() == len(self.getvalue())
                zwróć super(MyBytesIO, self).read(n)
            def seek(self, *args):
                self.hit_eof = Nieprawda
                zwróć super(MyBytesIO, self).seek(*args)

        data = bz2.compress(tarfile.TarInfo("foo").tobuf())
        dla x w range(len(data) + 1):
            spróbuj:
                tarfile.open(fileobj=MyBytesIO(data[:x]), mode=mode)
            wyjąwszy tarfile.ReadError:
                dalej # we have no interest w ReadErrors

    def test_partial_input(self):
        self._test_partial_input("r")

    def test_partial_input_bz2(self):
        self._test_partial_input("r:bz2")


def root_is_uid_gid_0():
    spróbuj:
        zaimportuj pwd, grp
    wyjąwszy ImportError:
        zwróć Nieprawda
    jeżeli pwd.getpwuid(0)[0] != 'root':
        zwróć Nieprawda
    jeżeli grp.getgrgid(0)[0] != 'root':
        zwróć Nieprawda
    zwróć Prawda


@unittest.skipUnless(hasattr(os, 'chown'), "missing os.chown")
@unittest.skipUnless(hasattr(os, 'geteuid'), "missing os.geteuid")
klasa NumericOwnerTest(unittest.TestCase):
    # mock the following:
    #  os.chown: so we can test what's being called
    #  os.chmod: so the modes are nie actually changed. jeżeli they are, we can't
    #             delete the files/directories
    #  os.geteuid: so we can lie oraz say we're root (uid = 0)

    @staticmethod
    def _make_test_archive(filename_1, dirname_1, filename_2):
        # the file contents to write
        fobj = io.BytesIO(b"content")

        # create a tar file przy a file, a directory, oraz a file within that
        #  directory. Assign various .uid/.gid values to them
        items = [(filename_1, 99, 98, tarfile.REGTYPE, fobj),
                 (dirname_1,  77, 76, tarfile.DIRTYPE, Nic),
                 (filename_2, 88, 87, tarfile.REGTYPE, fobj),
                 ]
        przy tarfile.open(tmpname, 'w') jako tarfl:
            dla name, uid, gid, typ, contents w items:
                t = tarfile.TarInfo(name)
                t.uid = uid
                t.gid = gid
                t.uname = 'root'
                t.gname = 'root'
                t.type = typ
                tarfl.addfile(t, contents)

        # zwróć the full pathname to the tar file
        zwróć tmpname

    @staticmethod
    @contextmanager
    def _setup_test(mock_geteuid):
        mock_geteuid.return_value = 0  # lie oraz say we're root
        fname = 'numeric-owner-testfile'
        dirname = 'dir'

        # the names we want stored w the tarfile
        filename_1 = fname
        dirname_1 = dirname
        filename_2 = os.path.join(dirname, fname)

        # create the tarfile przy the contents we're after
        tar_filename = NumericOwnerTest._make_test_archive(filename_1,
                                                           dirname_1,
                                                           filename_2)

        # open the tarfile dla reading. uzyskaj it oraz the names of the items
        #  we stored into the file
        przy tarfile.open(tar_filename) jako tarfl:
            uzyskaj tarfl, filename_1, dirname_1, filename_2

    @unittest.mock.patch('os.chown')
    @unittest.mock.patch('os.chmod')
    @unittest.mock.patch('os.geteuid')
    def test_extract_with_numeric_owner(self, mock_geteuid, mock_chmod,
                                        mock_chown):
        przy self._setup_test(mock_geteuid) jako (tarfl, filename_1, _,
                                                filename_2):
            tarfl.extract(filename_1, TEMPDIR, numeric_owner=Prawda)
            tarfl.extract(filename_2 , TEMPDIR, numeric_owner=Prawda)

        # convert to filesystem paths
        f_filename_1 = os.path.join(TEMPDIR, filename_1)
        f_filename_2 = os.path.join(TEMPDIR, filename_2)

        mock_chown.assert_has_calls([unittest.mock.call(f_filename_1, 99, 98),
                                     unittest.mock.call(f_filename_2, 88, 87),
                                     ],
                                    any_order=Prawda)

    @unittest.mock.patch('os.chown')
    @unittest.mock.patch('os.chmod')
    @unittest.mock.patch('os.geteuid')
    def test_extractall_with_numeric_owner(self, mock_geteuid, mock_chmod,
                                           mock_chown):
        przy self._setup_test(mock_geteuid) jako (tarfl, filename_1, dirname_1,
                                                filename_2):
            tarfl.extractall(TEMPDIR, numeric_owner=Prawda)

        # convert to filesystem paths
        f_filename_1 = os.path.join(TEMPDIR, filename_1)
        f_dirname_1  = os.path.join(TEMPDIR, dirname_1)
        f_filename_2 = os.path.join(TEMPDIR, filename_2)

        mock_chown.assert_has_calls([unittest.mock.call(f_filename_1, 99, 98),
                                     unittest.mock.call(f_dirname_1, 77, 76),
                                     unittest.mock.call(f_filename_2, 88, 87),
                                     ],
                                    any_order=Prawda)

    # this test requires that uid=0 oraz gid=0 really be named 'root'. that's
    #  because the uname oraz gname w the test file are 'root', oraz extract()
    #  will look them up using pwd oraz grp to find their uid oraz gid, which we
    #  test here to be 0.
    @unittest.skipUnless(root_is_uid_gid_0(),
                         'uid=0,gid=0 must be named "root"')
    @unittest.mock.patch('os.chown')
    @unittest.mock.patch('os.chmod')
    @unittest.mock.patch('os.geteuid')
    def test_extract_without_numeric_owner(self, mock_geteuid, mock_chmod,
                                           mock_chown):
        przy self._setup_test(mock_geteuid) jako (tarfl, filename_1, _, _):
            tarfl.extract(filename_1, TEMPDIR, numeric_owner=Nieprawda)

        # convert to filesystem paths
        f_filename_1 = os.path.join(TEMPDIR, filename_1)

        mock_chown.assert_called_with(f_filename_1, 0, 0)

    @unittest.mock.patch('os.geteuid')
    def test_keyword_only(self, mock_geteuid):
        przy self._setup_test(mock_geteuid) jako (tarfl, filename_1, _, _):
            self.assertRaises(TypeError,
                              tarfl.extract, filename_1, TEMPDIR, Nieprawda, Prawda)


def setUpModule():
    support.unlink(TEMPDIR)
    os.makedirs(TEMPDIR)

    global testtarnames
    testtarnames = [tarname]
    przy open(tarname, "rb") jako fobj:
        data = fobj.read()

    # Create compressed tarfiles.
    dla c w GzipTest, Bz2Test, LzmaTest:
        jeżeli c.open:
            support.unlink(c.tarname)
            testtarnames.append(c.tarname)
            przy c.open(c.tarname, "wb") jako tar:
                tar.write(data)

def tearDownModule():
    jeżeli os.path.exists(TEMPDIR):
        support.rmtree(TEMPDIR)

jeżeli __name__ == "__main__":
    unittest.main()
