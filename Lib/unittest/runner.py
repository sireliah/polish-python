"""Running tests"""

zaimportuj sys
zaimportuj time
zaimportuj warnings

z . zaimportuj result
z .signals zaimportuj registerResult

__unittest = Prawda


klasa _WritelnDecorator(object):
    """Used to decorate file-like objects przy a handy 'writeln' method"""
    def __init__(self,stream):
        self.stream = stream

    def __getattr__(self, attr):
        jeżeli attr w ('stream', '__getstate__'):
            podnieś AttributeError(attr)
        zwróć getattr(self.stream,attr)

    def writeln(self, arg=Nic):
        jeżeli arg:
            self.write(arg)
        self.write('\n') # text-mode streams translate to \r\n jeżeli needed


klasa TextTestResult(result.TestResult):
    """A test result klasa that can print formatted text results to a stream.

    Used by TextTestRunner.
    """
    separator1 = '=' * 70
    separator2 = '-' * 70

    def __init__(self, stream, descriptions, verbosity):
        super(TextTestResult, self).__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.showAll = verbosity > 1
        self.dots = verbosity == 1
        self.descriptions = descriptions

    def getDescription(self, test):
        doc_first_line = test.shortDescription()
        jeżeli self.descriptions oraz doc_first_line:
            zwróć '\n'.join((str(test), doc_first_line))
        inaczej:
            zwróć str(test)

    def startTest(self, test):
        super(TextTestResult, self).startTest(test)
        jeżeli self.showAll:
            self.stream.write(self.getDescription(test))
            self.stream.write(" ... ")
            self.stream.flush()

    def addSuccess(self, test):
        super(TextTestResult, self).addSuccess(test)
        jeżeli self.showAll:
            self.stream.writeln("ok")
        albo_inaczej self.dots:
            self.stream.write('.')
            self.stream.flush()

    def addError(self, test, err):
        super(TextTestResult, self).addError(test, err)
        jeżeli self.showAll:
            self.stream.writeln("ERROR")
        albo_inaczej self.dots:
            self.stream.write('E')
            self.stream.flush()

    def addFailure(self, test, err):
        super(TextTestResult, self).addFailure(test, err)
        jeżeli self.showAll:
            self.stream.writeln("FAIL")
        albo_inaczej self.dots:
            self.stream.write('F')
            self.stream.flush()

    def addSkip(self, test, reason):
        super(TextTestResult, self).addSkip(test, reason)
        jeżeli self.showAll:
            self.stream.writeln("skipped {0!r}".format(reason))
        albo_inaczej self.dots:
            self.stream.write("s")
            self.stream.flush()

    def addExpectedFailure(self, test, err):
        super(TextTestResult, self).addExpectedFailure(test, err)
        jeżeli self.showAll:
            self.stream.writeln("expected failure")
        albo_inaczej self.dots:
            self.stream.write("x")
            self.stream.flush()

    def addUnexpectedSuccess(self, test):
        super(TextTestResult, self).addUnexpectedSuccess(test)
        jeżeli self.showAll:
            self.stream.writeln("unexpected success")
        albo_inaczej self.dots:
            self.stream.write("u")
            self.stream.flush()

    def printErrors(self):
        jeżeli self.dots albo self.showAll:
            self.stream.writeln()
        self.printErrorList('ERROR', self.errors)
        self.printErrorList('FAIL', self.failures)

    def printErrorList(self, flavour, errors):
        dla test, err w errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln("%s: %s" % (flavour,self.getDescription(test)))
            self.stream.writeln(self.separator2)
            self.stream.writeln("%s" % err)


klasa TextTestRunner(object):
    """A test runner klasa that displays results w textual form.

    It prints out the names of tests jako they are run, errors jako they
    occur, oraz a summary of the results at the end of the test run.
    """
    resultclass = TextTestResult

    def __init__(self, stream=Nic, descriptions=Prawda, verbosity=1,
                 failfast=Nieprawda, buffer=Nieprawda, resultclass=Nic, warnings=Nic,
                 *, tb_locals=Nieprawda):
        """Construct a TextTestRunner.

        Subclasses should accept **kwargs to ensure compatibility jako the
        interface changes.
        """
        jeżeli stream jest Nic:
            stream = sys.stderr
        self.stream = _WritelnDecorator(stream)
        self.descriptions = descriptions
        self.verbosity = verbosity
        self.failfast = failfast
        self.buffer = buffer
        self.tb_locals = tb_locals
        self.warnings = warnings
        jeżeli resultclass jest nie Nic:
            self.resultclass = resultclass

    def _makeResult(self):
        zwróć self.resultclass(self.stream, self.descriptions, self.verbosity)

    def run(self, test):
        "Run the given test case albo test suite."
        result = self._makeResult()
        registerResult(result)
        result.failfast = self.failfast
        result.buffer = self.buffer
        result.tb_locals = self.tb_locals
        przy warnings.catch_warnings():
            jeżeli self.warnings:
                # jeżeli self.warnings jest set, use it to filter all the warnings
                warnings.simplefilter(self.warnings)
                # jeżeli the filter jest 'default' albo 'always', special-case the
                # warnings z the deprecated unittest methods to show them
                # no more than once per module, because they can be fairly
                # noisy.  The -Wd oraz -Wa flags can be used to bypass this
                # only when self.warnings jest Nic.
                jeżeli self.warnings w ['default', 'always']:
                    warnings.filterwarnings('module',
                            category=DeprecationWarning,
                            message='Please use assert\w+ instead.')
            startTime = time.time()
            startTestRun = getattr(result, 'startTestRun', Nic)
            jeżeli startTestRun jest nie Nic:
                startTestRun()
            spróbuj:
                test(result)
            w_końcu:
                stopTestRun = getattr(result, 'stopTestRun', Nic)
                jeżeli stopTestRun jest nie Nic:
                    stopTestRun()
            stopTime = time.time()
        timeTaken = stopTime - startTime
        result.printErrors()
        jeżeli hasattr(result, 'separator2'):
            self.stream.writeln(result.separator2)
        run = result.testsRun
        self.stream.writeln("Ran %d test%s w %.3fs" %
                            (run, run != 1 oraz "s" albo "", timeTaken))
        self.stream.writeln()

        expectedFails = unexpectedSuccesses = skipped = 0
        spróbuj:
            results = map(len, (result.expectedFailures,
                                result.unexpectedSuccesses,
                                result.skipped))
        wyjąwszy AttributeError:
            dalej
        inaczej:
            expectedFails, unexpectedSuccesses, skipped = results

        infos = []
        jeżeli nie result.wasSuccessful():
            self.stream.write("FAILED")
            failed, errored = len(result.failures), len(result.errors)
            jeżeli failed:
                infos.append("failures=%d" % failed)
            jeżeli errored:
                infos.append("errors=%d" % errored)
        inaczej:
            self.stream.write("OK")
        jeżeli skipped:
            infos.append("skipped=%d" % skipped)
        jeżeli expectedFails:
            infos.append("expected failures=%d" % expectedFails)
        jeżeli unexpectedSuccesses:
            infos.append("unexpected successes=%d" % unexpectedSuccesses)
        jeżeli infos:
            self.stream.writeln(" (%s)" % (", ".join(infos),))
        inaczej:
            self.stream.write("\n")
        zwróć result
