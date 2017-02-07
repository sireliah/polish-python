"""Tests dla distutils.log"""

zaimportuj sys
zaimportuj unittest
z tempfile zaimportuj NamedTemporaryFile
z test.support zaimportuj run_unittest

z distutils zaimportuj log

klasa TestLog(unittest.TestCase):
    def test_non_ascii(self):
        # Issue #8663: test that non-ASCII text jest escaped with
        # backslashreplace error handler (stream use ASCII encoding oraz strict
        # error handler)
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        spróbuj:
            log.set_threshold(log.DEBUG)
            przy NamedTemporaryFile(mode="w+", encoding='ascii') jako stdout, \
                 NamedTemporaryFile(mode="w+", encoding='ascii') jako stderr:
                sys.stdout = stdout
                sys.stderr = stderr
                log.debug("debug:\xe9")
                log.fatal("fatal:\xe9")
                stdout.seek(0)
                self.assertEqual(stdout.read().rstrip(), "debug:\\xe9")
                stderr.seek(0)
                self.assertEqual(stderr.read().rstrip(), "fatal:\\xe9")
        w_końcu:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

def test_suite():
    zwróć unittest.makeSuite(TestLog)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
