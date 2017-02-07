zaimportuj unittest


klasa TestEquality(object):
    """Used jako a mixin dla TestCase"""

    # Check dla a valid __eq__ implementation
    def test_eq(self):
        dla obj_1, obj_2 w self.eq_pairs:
            self.assertEqual(obj_1, obj_2)
            self.assertEqual(obj_2, obj_1)

    # Check dla a valid __ne__ implementation
    def test_ne(self):
        dla obj_1, obj_2 w self.ne_pairs:
            self.assertNotEqual(obj_1, obj_2)
            self.assertNotEqual(obj_2, obj_1)

klasa TestHashing(object):
    """Used jako a mixin dla TestCase"""

    # Check dla a valid __hash__ implementation
    def test_hash(self):
        dla obj_1, obj_2 w self.eq_pairs:
            spróbuj:
                jeżeli nie hash(obj_1) == hash(obj_2):
                    self.fail("%r oraz %r do nie hash equal" % (obj_1, obj_2))
            wyjąwszy Exception jako e:
                self.fail("Problem hashing %r oraz %r: %s" % (obj_1, obj_2, e))

        dla obj_1, obj_2 w self.ne_pairs:
            spróbuj:
                jeżeli hash(obj_1) == hash(obj_2):
                    self.fail("%s oraz %s hash equal, but shouldn't" %
                              (obj_1, obj_2))
            wyjąwszy Exception jako e:
                self.fail("Problem hashing %s oraz %s: %s" % (obj_1, obj_2, e))


klasa _BaseLoggingResult(unittest.TestResult):
    def __init__(self, log):
        self._events = log
        super().__init__()

    def startTest(self, test):
        self._events.append('startTest')
        super().startTest(test)

    def startTestRun(self):
        self._events.append('startTestRun')
        super().startTestRun()

    def stopTest(self, test):
        self._events.append('stopTest')
        super().stopTest(test)

    def stopTestRun(self):
        self._events.append('stopTestRun')
        super().stopTestRun()

    def addFailure(self, *args):
        self._events.append('addFailure')
        super().addFailure(*args)

    def addSuccess(self, *args):
        self._events.append('addSuccess')
        super().addSuccess(*args)

    def addError(self, *args):
        self._events.append('addError')
        super().addError(*args)

    def addSkip(self, *args):
        self._events.append('addSkip')
        super().addSkip(*args)

    def addExpectedFailure(self, *args):
        self._events.append('addExpectedFailure')
        super().addExpectedFailure(*args)

    def addUnexpectedSuccess(self, *args):
        self._events.append('addUnexpectedSuccess')
        super().addUnexpectedSuccess(*args)


klasa LegacyLoggingResult(_BaseLoggingResult):
    """
    A legacy TestResult implementation, without an addSubTest method,
    which records its method calls.
    """

    @property
    def addSubTest(self):
        podnieś AttributeError


klasa LoggingResult(_BaseLoggingResult):
    """
    A TestResult implementation which records its method calls.
    """

    def addSubTest(self, test, subtest, err):
        jeżeli err jest Nic:
            self._events.append('addSubTestSuccess')
        inaczej:
            self._events.append('addSubTestFailure')
        super().addSubTest(test, subtest, err)


klasa ResultWithNoStartTestRunStopTestRun(object):
    """An object honouring TestResult before startTestRun/stopTestRun."""

    def __init__(self):
        self.failures = []
        self.errors = []
        self.testsRun = 0
        self.skipped = []
        self.expectedFailures = []
        self.unexpectedSuccesses = []
        self.shouldStop = Nieprawda

    def startTest(self, test):
        dalej

    def stopTest(self, test):
        dalej

    def addError(self, test):
        dalej

    def addFailure(self, test):
        dalej

    def addSuccess(self, test):
        dalej

    def wasSuccessful(self):
        zwróć Prawda
