"""
Create oraz delete FILES_PER_THREAD temp files (via tempfile.TemporaryFile)
in each of NUM_THREADS threads, recording the number of successes oraz
failures.  A failure jest a bug w tempfile, oraz may be due to:

+ Trying to create more than one tempfile przy the same name.
+ Trying to delete a tempfile that doesn't still exist.
+ Something we've never seen before.

By default, NUM_THREADS == 20 oraz FILES_PER_THREAD == 50.  This jest enough to
create about 150 failures per run under Win98SE w 2.0, oraz runs pretty
quickly. Guido reports needing to boost FILES_PER_THREAD to 500 before
provoking a 2.0 failure under Linux.
"""

NUM_THREADS = 20
FILES_PER_THREAD = 50

zaimportuj tempfile

z test.support zaimportuj start_threads, import_module
threading = import_module('threading')
zaimportuj unittest
zaimportuj io
z traceback zaimportuj print_exc

startEvent = threading.Event()

klasa TempFileGreedy(threading.Thread):
    error_count = 0
    ok_count = 0

    def run(self):
        self.errors = io.StringIO()
        startEvent.wait()
        dla i w range(FILES_PER_THREAD):
            spróbuj:
                f = tempfile.TemporaryFile("w+b")
                f.close()
            wyjąwszy:
                self.error_count += 1
                print_exc(file=self.errors)
            inaczej:
                self.ok_count += 1


klasa ThreadedTempFileTest(unittest.TestCase):
    def test_main(self):
        threads = [TempFileGreedy() dla i w range(NUM_THREADS)]
        przy start_threads(threads, startEvent.set):
            dalej
        ok = sum(t.ok_count dla t w threads)
        errors = [str(t.name) + str(t.errors.getvalue())
                  dla t w threads jeżeli t.error_count]

        msg = "Errors: errors %d ok %d\n%s" % (len(errors), ok,
            '\n'.join(errors))
        self.assertEqual(errors, [], msg)
        self.assertEqual(ok, NUM_THREADS * FILES_PER_THREAD)

jeżeli __name__ == "__main__":
    unittest.main()
