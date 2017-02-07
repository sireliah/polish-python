# Ridiculously simple test of the os.startfile function dla Windows.
#
# empty.vbs jest an empty file (wyjąwszy dla a comment), which does
# nothing when run przy cscript albo wscript.
#
# A possible improvement would be to have empty.vbs do something that
# we can detect here, to make sure that nie only the os.startfile()
# call succeeded, but also the script actually has run.

zaimportuj unittest
z test zaimportuj support
zaimportuj os
zaimportuj sys
z os zaimportuj path

startfile = support.get_attribute(os, 'startfile')


klasa TestCase(unittest.TestCase):
    def test_nonexisting(self):
        self.assertRaises(OSError, startfile, "nonexisting.vbs")

    def test_empty(self):
        # We need to make sure the child process starts w a directory
        # we're nie about to delete. If we're running under -j, that
        # means the test harness provided directory isn't a safe option.
        # See http://bugs.python.org/issue15526 dla more details
        przy support.change_cwd(path.dirname(sys.executable)):
            empty = path.join(path.dirname(__file__), "empty.vbs")
            startfile(empty)
            startfile(empty, "open")

jeżeli __name__ == "__main__":
    unittest.main()
