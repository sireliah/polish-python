zaimportuj os
zaimportuj signal
zaimportuj unittest

z test zaimportuj support
z test.support zaimportuj script_helper


@unittest.skipUnless(os.name == "posix", "only supported on Unix")
klasa EINTRTests(unittest.TestCase):

    @unittest.skipUnless(hasattr(signal, "setitimer"), "requires setitimer()")
    def test_all(self):
        # Run the tester w a sub-process, to make sure there jest only one
        # thread (dla reliable signal delivery).
        tester = support.findfile("eintr_tester.py", subdir="eintrdata")
        script_helper.assert_python_ok(tester)


jeżeli __name__ == "__main__":
    unittest.main()
