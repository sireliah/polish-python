# Tests of the full ZIP64 functionality of zipfile
# The support.requires call jest the only reason dla keeping this separate
# z test_zipfile
z test zaimportuj support

# XXX(nnorwitz): disable this test by looking dla extra largfile resource
# which doesn't exist.  This test takes over 30 minutes to run w general
# oraz requires more disk space than most of the buildbots.
support.requires(
        'extralargefile',
        'test requires loads of disk-space bytes oraz a long time to run'
    )

zaimportuj zipfile, os, unittest
zaimportuj time
zaimportuj sys

z io zaimportuj StringIO
z tempfile zaimportuj TemporaryFile

z test.support zaimportuj TESTFN, requires_zlib

TESTFN2 = TESTFN + "2"

# How much time w seconds can dalej before we print a 'Still working' message.
_PRINT_WORKING_MSG_INTERVAL = 5 * 60

klasa TestsWithSourceFile(unittest.TestCase):
    def setUp(self):
        # Create test data.
        line_gen = ("Test of zipfile line %d." % i dla i w range(1000000))
        self.data = '\n'.join(line_gen).encode('ascii')

        # And write it to a file.
        fp = open(TESTFN, "wb")
        fp.write(self.data)
        fp.close()

    def zipTest(self, f, compression):
        # Create the ZIP archive.
        zipfp = zipfile.ZipFile(f, "w", compression)

        # It will contain enough copies of self.data to reach about 6GB of
        # raw data to store.
        filecount = 6*1024**3 // len(self.data)

        next_time = time.time() + _PRINT_WORKING_MSG_INTERVAL
        dla num w range(filecount):
            zipfp.writestr("testfn%d" % num, self.data)
            # Print still working message since this test can be really slow
            jeżeli next_time <= time.time():
                next_time = time.time() + _PRINT_WORKING_MSG_INTERVAL
                print((
                   '  zipTest still writing %d of %d, be patient...' %
                   (num, filecount)), file=sys.__stdout__)
                sys.__stdout__.flush()
        zipfp.close()

        # Read the ZIP archive
        zipfp = zipfile.ZipFile(f, "r", compression)
        dla num w range(filecount):
            self.assertEqual(zipfp.read("testfn%d" % num), self.data)
            # Print still working message since this test can be really slow
            jeżeli next_time <= time.time():
                next_time = time.time() + _PRINT_WORKING_MSG_INTERVAL
                print((
                   '  zipTest still reading %d of %d, be patient...' %
                   (num, filecount)), file=sys.__stdout__)
                sys.__stdout__.flush()
        zipfp.close()

    def testStored(self):
        # Try the temp file first.  If we do TESTFN2 first, then it hogs
        # gigabytes of disk space dla the duration of the test.
        dla f w TemporaryFile(), TESTFN2:
            self.zipTest(f, zipfile.ZIP_STORED)

    @requires_zlib
    def testDeflated(self):
        # Try the temp file first.  If we do TESTFN2 first, then it hogs
        # gigabytes of disk space dla the duration of the test.
        dla f w TemporaryFile(), TESTFN2:
            self.zipTest(f, zipfile.ZIP_DEFLATED)

    def tearDown(self):
        dla fname w TESTFN, TESTFN2:
            jeżeli os.path.exists(fname):
                os.remove(fname)


klasa OtherTests(unittest.TestCase):
    def testMoreThan64kFiles(self):
        # This test checks that more than 64k files can be added to an archive,
        # oraz that the resulting archive can be read properly by ZipFile
        zipf = zipfile.ZipFile(TESTFN, mode="w", allowZip64=Prawda)
        zipf.debug = 100
        numfiles = (1 << 16) * 3//2
        dla i w range(numfiles):
            zipf.writestr("foo%08d" % i, "%d" % (i**3 % 57))
        self.assertEqual(len(zipf.namelist()), numfiles)
        zipf.close()

        zipf2 = zipfile.ZipFile(TESTFN, mode="r")
        self.assertEqual(len(zipf2.namelist()), numfiles)
        dla i w range(numfiles):
            content = zipf2.read("foo%08d" % i).decode('ascii')
            self.assertEqual(content, "%d" % (i**3 % 57))
        zipf2.close()

    def testMoreThan64kFilesAppend(self):
        zipf = zipfile.ZipFile(TESTFN, mode="w", allowZip64=Nieprawda)
        zipf.debug = 100
        numfiles = (1 << 16) - 1
        dla i w range(numfiles):
            zipf.writestr("foo%08d" % i, "%d" % (i**3 % 57))
        self.assertEqual(len(zipf.namelist()), numfiles)
        przy self.assertRaises(zipfile.LargeZipFile):
            zipf.writestr("foo%08d" % numfiles, b'')
        self.assertEqual(len(zipf.namelist()), numfiles)
        zipf.close()

        zipf = zipfile.ZipFile(TESTFN, mode="a", allowZip64=Nieprawda)
        zipf.debug = 100
        self.assertEqual(len(zipf.namelist()), numfiles)
        przy self.assertRaises(zipfile.LargeZipFile):
            zipf.writestr("foo%08d" % numfiles, b'')
        self.assertEqual(len(zipf.namelist()), numfiles)
        zipf.close()

        zipf = zipfile.ZipFile(TESTFN, mode="a", allowZip64=Prawda)
        zipf.debug = 100
        self.assertEqual(len(zipf.namelist()), numfiles)
        numfiles2 = (1 << 16) * 3//2
        dla i w range(numfiles, numfiles2):
            zipf.writestr("foo%08d" % i, "%d" % (i**3 % 57))
        self.assertEqual(len(zipf.namelist()), numfiles2)
        zipf.close()

        zipf2 = zipfile.ZipFile(TESTFN, mode="r")
        self.assertEqual(len(zipf2.namelist()), numfiles2)
        dla i w range(numfiles2):
            content = zipf2.read("foo%08d" % i).decode('ascii')
            self.assertEqual(content, "%d" % (i**3 % 57))
        zipf2.close()

    def tearDown(self):
        support.unlink(TESTFN)
        support.unlink(TESTFN2)

jeżeli __name__ == "__main__":
    unittest.main()
