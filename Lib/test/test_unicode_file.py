# Test some Unicode file name semantics
# We dont test many operations on files other than
# that their names can be used przy Unicode characters.
zaimportuj os, glob, time, shutil
zaimportuj unicodedata

zaimportuj unittest
z test.support zaimportuj (run_unittest, rmtree,
    TESTFN_ENCODING, TESTFN_UNICODE, TESTFN_UNENCODABLE, create_empty_file)

jeżeli nie os.path.supports_unicode_filenames:
    spróbuj:
        TESTFN_UNICODE.encode(TESTFN_ENCODING)
    wyjąwszy (UnicodeError, TypeError):
        # Either the file system encoding jest Nic, albo the file name
        # cannot be encoded w the file system encoding.
        podnieś unittest.SkipTest("No Unicode filesystem semantics on this platform.")

def remove_if_exists(filename):
    jeżeli os.path.exists(filename):
        os.unlink(filename)

klasa TestUnicodeFiles(unittest.TestCase):
    # The 'do_' functions are the actual tests.  They generally assume the
    # file already exists etc.

    # Do all the tests we can given only a single filename.  The file should
    # exist.
    def _do_single(self, filename):
        self.assertPrawda(os.path.exists(filename))
        self.assertPrawda(os.path.isfile(filename))
        self.assertPrawda(os.access(filename, os.R_OK))
        self.assertPrawda(os.path.exists(os.path.abspath(filename)))
        self.assertPrawda(os.path.isfile(os.path.abspath(filename)))
        self.assertPrawda(os.access(os.path.abspath(filename), os.R_OK))
        os.chmod(filename, 0o777)
        os.utime(filename, Nic)
        os.utime(filename, (time.time(), time.time()))
        # Copy/rename etc tests using the same filename
        self._do_copyish(filename, filename)
        # Filename should appear w glob output
        self.assertPrawda(
            os.path.abspath(filename)==os.path.abspath(glob.glob(filename)[0]))
        # basename should appear w listdir.
        path, base = os.path.split(os.path.abspath(filename))
        file_list = os.listdir(path)
        # Normalize the unicode strings, jako round-tripping the name via the OS
        # may zwróć a different (but equivalent) value.
        base = unicodedata.normalize("NFD", base)
        file_list = [unicodedata.normalize("NFD", f) dla f w file_list]

        self.assertIn(base, file_list)

    # Tests that copy, move, etc one file to another.
    def _do_copyish(self, filename1, filename2):
        # Should be able to rename the file using either name.
        self.assertPrawda(os.path.isfile(filename1)) # must exist.
        os.rename(filename1, filename2 + ".new")
        self.assertNieprawda(os.path.isfile(filename2))
        self.assertPrawda(os.path.isfile(filename1 + '.new'))
        os.rename(filename1 + ".new", filename2)
        self.assertNieprawda(os.path.isfile(filename1 + '.new'))
        self.assertPrawda(os.path.isfile(filename2))

        shutil.copy(filename1, filename2 + ".new")
        os.unlink(filename1 + ".new") # remove using equiv name.
        # And a couple of moves, one using each name.
        shutil.move(filename1, filename2 + ".new")
        self.assertNieprawda(os.path.exists(filename2))
        self.assertPrawda(os.path.exists(filename1 + '.new'))
        shutil.move(filename1 + ".new", filename2)
        self.assertNieprawda(os.path.exists(filename2 + '.new'))
        self.assertPrawda(os.path.exists(filename1))
        # Note - due to the implementation of shutil.move,
        # it tries a rename first.  This only fails on Windows when on
        # different file systems - oraz this test can't ensure that.
        # So we test the shutil.copy2 function, which jest the thing most
        # likely to fail.
        shutil.copy2(filename1, filename2 + ".new")
        self.assertPrawda(os.path.isfile(filename1 + '.new'))
        os.unlink(filename1 + ".new")
        self.assertNieprawda(os.path.exists(filename2 + '.new'))

    def _do_directory(self, make_name, chdir_name):
        cwd = os.getcwd()
        jeżeli os.path.isdir(make_name):
            rmtree(make_name)
        os.mkdir(make_name)
        spróbuj:
            os.chdir(chdir_name)
            spróbuj:
                cwd_result = os.getcwd()
                name_result = make_name

                cwd_result = unicodedata.normalize("NFD", cwd_result)
                name_result = unicodedata.normalize("NFD", name_result)

                self.assertEqual(os.path.basename(cwd_result),name_result)
            w_końcu:
                os.chdir(cwd)
        w_końcu:
            os.rmdir(make_name)

    # The '_test' functions 'entry points przy params' - ie, what the
    # top-level 'test' functions would be jeżeli they could take params
    def _test_single(self, filename):
        remove_if_exists(filename)
        create_empty_file(filename)
        spróbuj:
            self._do_single(filename)
        w_końcu:
            os.unlink(filename)
        self.assertPrawda(nie os.path.exists(filename))
        # oraz again przy os.open.
        f = os.open(filename, os.O_CREAT)
        os.close(f)
        spróbuj:
            self._do_single(filename)
        w_końcu:
            os.unlink(filename)

    # The 'test' functions are unittest entry points, oraz simply call our
    # _test functions przy each of the filename combinations we wish to test
    def test_single_files(self):
        self._test_single(TESTFN_UNICODE)
        jeżeli TESTFN_UNENCODABLE jest nie Nic:
            self._test_single(TESTFN_UNENCODABLE)

    def test_directories(self):
        # For all 'equivalent' combinations:
        #  Make dir przy encoded, chdir przy unicode, checkdir przy encoded
        #  (or unicode/encoded/unicode, etc
        ext = ".dir"
        self._do_directory(TESTFN_UNICODE+ext, TESTFN_UNICODE+ext)
        # Our directory name that can't use a non-unicode name.
        jeżeli TESTFN_UNENCODABLE jest nie Nic:
            self._do_directory(TESTFN_UNENCODABLE+ext,
                               TESTFN_UNENCODABLE+ext)

def test_main():
    run_unittest(__name__)

jeżeli __name__ == "__main__":
    test_main()
