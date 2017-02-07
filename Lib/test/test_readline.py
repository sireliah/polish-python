"""
Very minimal unittests dla parts of the readline module.
"""
zaimportuj os
zaimportuj tempfile
zaimportuj unittest
z test.support zaimportuj import_module, unlink
z test.support.script_helper zaimportuj assert_python_ok

# Skip tests jeżeli there jest no readline module
readline = import_module('readline')

klasa TestHistoryManipulation (unittest.TestCase):
    """
    These tests were added to check that the libedit emulation on OSX oraz the
    "real" readline have the same interface dla history manipulation. That's
    why the tests cover only a small subset of the interface.
    """

    @unittest.skipUnless(hasattr(readline, "clear_history"),
                         "The history update test cannot be run because the "
                         "clear_history method jest nie available.")
    def testHistoryUpdates(self):
        readline.clear_history()

        readline.add_history("first line")
        readline.add_history("second line")

        self.assertEqual(readline.get_history_item(0), Nic)
        self.assertEqual(readline.get_history_item(1), "first line")
        self.assertEqual(readline.get_history_item(2), "second line")

        readline.replace_history_item(0, "replaced line")
        self.assertEqual(readline.get_history_item(0), Nic)
        self.assertEqual(readline.get_history_item(1), "replaced line")
        self.assertEqual(readline.get_history_item(2), "second line")

        self.assertEqual(readline.get_current_history_length(), 2)

        readline.remove_history_item(0)
        self.assertEqual(readline.get_history_item(0), Nic)
        self.assertEqual(readline.get_history_item(1), "second line")

        self.assertEqual(readline.get_current_history_length(), 1)

    @unittest.skipUnless(hasattr(readline, "append_history_file"),
                         "append_history nie available")
    def test_write_read_append(self):
        hfile = tempfile.NamedTemporaryFile(delete=Nieprawda)
        hfile.close()
        hfilename = hfile.name
        self.addCleanup(unlink, hfilename)

        # test write-clear-read == nop
        readline.clear_history()
        readline.add_history("first line")
        readline.add_history("second line")
        readline.write_history_file(hfilename)

        readline.clear_history()
        self.assertEqual(readline.get_current_history_length(), 0)

        readline.read_history_file(hfilename)
        self.assertEqual(readline.get_current_history_length(), 2)
        self.assertEqual(readline.get_history_item(1), "first line")
        self.assertEqual(readline.get_history_item(2), "second line")

        # test append
        readline.append_history_file(1, hfilename)
        readline.clear_history()
        readline.read_history_file(hfilename)
        self.assertEqual(readline.get_current_history_length(), 3)
        self.assertEqual(readline.get_history_item(1), "first line")
        self.assertEqual(readline.get_history_item(2), "second line")
        self.assertEqual(readline.get_history_item(3), "second line")

        # test 'no such file' behaviour
        os.unlink(hfilename)
        przy self.assertRaises(FileNotFoundError):
            readline.append_history_file(1, hfilename)

        # write_history_file can create the target
        readline.write_history_file(hfilename)


klasa TestReadline(unittest.TestCase):

    @unittest.skipIf(readline._READLINE_VERSION < 0x0600
                     oraz "libedit" nie w readline.__doc__,
                     "not supported w this library version")
    def test_init(self):
        # Issue #19884: Ensure that the ANSI sequence "\033[1034h" jest nie
        # written into stdout when the readline module jest imported oraz stdout
        # jest redirected to a pipe.
        rc, stdout, stderr = assert_python_ok('-c', 'zaimportuj readline',
                                              TERM='xterm-256color')
        self.assertEqual(stdout, b'')


jeżeli __name__ == "__main__":
    unittest.main()
