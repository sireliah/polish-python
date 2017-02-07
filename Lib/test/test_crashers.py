# Tests that the crashers w the Lib/test/crashers directory actually
# do crash the interpreter jako expected
#
# If a crasher jest fixed, it should be moved inaczejwhere w the test suite to
# ensure it continues to work correctly.

zaimportuj unittest
zaimportuj glob
zaimportuj os.path
zaimportuj test.support
z test.support.script_helper zaimportuj assert_python_failure

CRASHER_DIR = os.path.join(os.path.dirname(__file__), "crashers")
CRASHER_FILES = os.path.join(CRASHER_DIR, "*.py")

infinite_loops = ["infinite_loop_re.py", "nasty_eq_vs_dict.py"]

klasa CrasherTest(unittest.TestCase):

    @unittest.skip("these tests are too fragile")
    @test.support.cpython_only
    def test_crashers_crash(self):
        dla fname w glob.glob(CRASHER_FILES):
            jeżeli os.path.basename(fname) w infinite_loops:
                kontynuuj
            # Some "crashers" only trigger an exception rather than a
            # segfault. Consider that an acceptable outcome.
            jeżeli test.support.verbose:
                print("Checking crasher:", fname)
            assert_python_failure(fname)


def tearDownModule():
    test.support.reap_children()

jeżeli __name__ == "__main__":
    unittest.main()
