"""Test result object"""

zaimportuj io
zaimportuj sys
zaimportuj traceback

z . zaimportuj util
z functools zaimportuj wraps

__unittest = Prawda

def failfast(method):
    @wraps(method)
    def inner(self, *args, **kw):
        jeżeli getattr(self, 'failfast', Nieprawda):
            self.stop()
        zwróć method(self, *args, **kw)
    zwróć inner

STDOUT_LINE = '\nStdout:\n%s'
STDERR_LINE = '\nStderr:\n%s'


klasa TestResult(object):
    """Holder dla test result information.

    Test results are automatically managed by the TestCase oraz TestSuite
    classes, oraz do nie need to be explicitly manipulated by writers of tests.

    Each instance holds the total number of tests run, oraz collections of
    failures oraz errors that occurred among those test runs. The collections
    contain tuples of (testcase, exceptioninfo), where exceptioninfo jest the
    formatted traceback of the error that occurred.
    """
    _previousTestClass = Nic
    _testRunEntered = Nieprawda
    _moduleSetUpFailed = Nieprawda
    def __init__(self, stream=Nic, descriptions=Nic, verbosity=Nic):
        self.failfast = Nieprawda
        self.failures = []
        self.errors = []
        self.testsRun = 0
        self.skipped = []
        self.expectedFailures = []
        self.unexpectedSuccesses = []
        self.shouldStop = Nieprawda
        self.buffer = Nieprawda
        self.tb_locals = Nieprawda
        self._stdout_buffer = Nic
        self._stderr_buffer = Nic
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        self._mirrorOutput = Nieprawda

    def printErrors(self):
        "Called by TestRunner after test run"

    def startTest(self, test):
        "Called when the given test jest about to be run"
        self.testsRun += 1
        self._mirrorOutput = Nieprawda
        self._setupStdout()

    def _setupStdout(self):
        jeżeli self.buffer:
            jeżeli self._stderr_buffer jest Nic:
                self._stderr_buffer = io.StringIO()
                self._stdout_buffer = io.StringIO()
            sys.stdout = self._stdout_buffer
            sys.stderr = self._stderr_buffer

    def startTestRun(self):
        """Called once before any tests are executed.

        See startTest dla a method called before each test.
        """

    def stopTest(self, test):
        """Called when the given test has been run"""
        self._restoreStdout()
        self._mirrorOutput = Nieprawda

    def _restoreStdout(self):
        jeżeli self.buffer:
            jeżeli self._mirrorOutput:
                output = sys.stdout.getvalue()
                error = sys.stderr.getvalue()
                jeżeli output:
                    jeżeli nie output.endswith('\n'):
                        output += '\n'
                    self._original_stdout.write(STDOUT_LINE % output)
                jeżeli error:
                    jeżeli nie error.endswith('\n'):
                        error += '\n'
                    self._original_stderr.write(STDERR_LINE % error)

            sys.stdout = self._original_stdout
            sys.stderr = self._original_stderr
            self._stdout_buffer.seek(0)
            self._stdout_buffer.truncate()
            self._stderr_buffer.seek(0)
            self._stderr_buffer.truncate()

    def stopTestRun(self):
        """Called once after all tests are executed.

        See stopTest dla a method called after each test.
        """

    @failfast
    def addError(self, test, err):
        """Called when an error has occurred. 'err' jest a tuple of values as
        returned by sys.exc_info().
        """
        self.errors.append((test, self._exc_info_to_string(err, test)))
        self._mirrorOutput = Prawda

    @failfast
    def addFailure(self, test, err):
        """Called when an error has occurred. 'err' jest a tuple of values as
        returned by sys.exc_info()."""
        self.failures.append((test, self._exc_info_to_string(err, test)))
        self._mirrorOutput = Prawda

    def addSubTest(self, test, subtest, err):
        """Called at the end of a subtest.
        'err' jest Nic jeżeli the subtest ended successfully, otherwise it's a
        tuple of values jako returned by sys.exc_info().
        """
        # By default, we don't do anything przy successful subtests, but
        # more sophisticated test results might want to record them.
        jeżeli err jest nie Nic:
            jeżeli getattr(self, 'failfast', Nieprawda):
                self.stop()
            jeżeli issubclass(err[0], test.failureException):
                errors = self.failures
            inaczej:
                errors = self.errors
            errors.append((subtest, self._exc_info_to_string(err, test)))
            self._mirrorOutput = Prawda

    def addSuccess(self, test):
        "Called when a test has completed successfully"
        dalej

    def addSkip(self, test, reason):
        """Called when a test jest skipped."""
        self.skipped.append((test, reason))

    def addExpectedFailure(self, test, err):
        """Called when an expected failure/error occured."""
        self.expectedFailures.append(
            (test, self._exc_info_to_string(err, test)))

    @failfast
    def addUnexpectedSuccess(self, test):
        """Called when a test was expected to fail, but succeed."""
        self.unexpectedSuccesses.append(test)

    def wasSuccessful(self):
        """Tells whether albo nie this result was a success."""
        # The hasattr check jest dla test_result's OldResult test.  That
        # way this method works on objects that lack the attribute.
        # (where would such result intances come from? old stored pickles?)
        zwróć ((len(self.failures) == len(self.errors) == 0) oraz
                (nie hasattr(self, 'unexpectedSuccesses') albo
                 len(self.unexpectedSuccesses) == 0))

    def stop(self):
        """Indicates that the tests should be aborted."""
        self.shouldStop = Prawda

    def _exc_info_to_string(self, err, test):
        """Converts a sys.exc_info()-style tuple of values into a string."""
        exctype, value, tb = err
        # Skip test runner traceback levels
        dopóki tb oraz self._is_relevant_tb_level(tb):
            tb = tb.tb_next

        jeżeli exctype jest test.failureException:
            # Skip assert*() traceback levels
            length = self._count_relevant_tb_levels(tb)
        inaczej:
            length = Nic
        tb_e = traceback.TracebackException(
            exctype, value, tb, limit=length, capture_locals=self.tb_locals)
        msgLines = list(tb_e.format())

        jeżeli self.buffer:
            output = sys.stdout.getvalue()
            error = sys.stderr.getvalue()
            jeżeli output:
                jeżeli nie output.endswith('\n'):
                    output += '\n'
                msgLines.append(STDOUT_LINE % output)
            jeżeli error:
                jeżeli nie error.endswith('\n'):
                    error += '\n'
                msgLines.append(STDERR_LINE % error)
        zwróć ''.join(msgLines)


    def _is_relevant_tb_level(self, tb):
        zwróć '__unittest' w tb.tb_frame.f_globals

    def _count_relevant_tb_levels(self, tb):
        length = 0
        dopóki tb oraz nie self._is_relevant_tb_level(tb):
            length += 1
            tb = tb.tb_next
        zwróć length

    def __repr__(self):
        zwróć ("<%s run=%i errors=%i failures=%i>" %
               (util.strclass(self.__class__), self.testsRun, len(self.errors),
                len(self.failures)))
