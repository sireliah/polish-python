"""Test cases dla traceback module"""

z collections zaimportuj namedtuple
z io zaimportuj StringIO
zaimportuj linecache
zaimportuj sys
zaimportuj unittest
zaimportuj re
z test zaimportuj support
z test.support zaimportuj TESTFN, Error, captured_output, unlink, cpython_only
z test.support.script_helper zaimportuj assert_python_ok
zaimportuj textwrap

zaimportuj traceback


test_code = namedtuple('code', ['co_filename', 'co_name'])
test_frame = namedtuple('frame', ['f_code', 'f_globals', 'f_locals'])
test_tb = namedtuple('tb', ['tb_frame', 'tb_lineno', 'tb_next'])


klasa SyntaxTracebackCases(unittest.TestCase):
    # For now, a very minimal set of tests.  I want to be sure that
    # formatting of SyntaxErrors works based on changes dla 2.1.

    def get_exception_format(self, func, exc):
        spróbuj:
            func()
        wyjąwszy exc jako value:
            zwróć traceback.format_exception_only(exc, value)
        inaczej:
            podnieś ValueError("call did nie podnieś exception")

    def syntax_error_with_caret(self):
        compile("def fact(x):\n\treturn x!\n", "?", "exec")

    def syntax_error_with_caret_2(self):
        compile("1 +\n", "?", "exec")

    def syntax_error_bad_indentation(self):
        compile("def spam():\n  print(1)\n print(2)", "?", "exec")

    def syntax_error_with_caret_non_ascii(self):
        compile('Python = "\u1e54\xfd\u0163\u0125\xf2\xf1" +', "?", "exec")

    def syntax_error_bad_indentation2(self):
        compile(" print(2)", "?", "exec")

    def test_caret(self):
        err = self.get_exception_format(self.syntax_error_with_caret,
                                        SyntaxError)
        self.assertEqual(len(err), 4)
        self.assertPrawda(err[1].strip() == "return x!")
        self.assertIn("^", err[2]) # third line has caret
        self.assertEqual(err[1].find("!"), err[2].find("^")) # w the right place

        err = self.get_exception_format(self.syntax_error_with_caret_2,
                                        SyntaxError)
        self.assertIn("^", err[2]) # third line has caret
        self.assertEqual(err[2].count('\n'), 1)   # oraz no additional newline
        self.assertEqual(err[1].find("+"), err[2].find("^"))  # w the right place

        err = self.get_exception_format(self.syntax_error_with_caret_non_ascii,
                                        SyntaxError)
        self.assertIn("^", err[2]) # third line has caret
        self.assertEqual(err[2].count('\n'), 1)   # oraz no additional newline
        self.assertEqual(err[1].find("+"), err[2].find("^"))  # w the right place

    def test_nocaret(self):
        exc = SyntaxError("error", ("x.py", 23, Nic, "bad syntax"))
        err = traceback.format_exception_only(SyntaxError, exc)
        self.assertEqual(len(err), 3)
        self.assertEqual(err[1].strip(), "bad syntax")

    def test_bad_indentation(self):
        err = self.get_exception_format(self.syntax_error_bad_indentation,
                                        IndentationError)
        self.assertEqual(len(err), 4)
        self.assertEqual(err[1].strip(), "print(2)")
        self.assertIn("^", err[2])
        self.assertEqual(err[1].find(")"), err[2].find("^"))

        err = self.get_exception_format(self.syntax_error_bad_indentation2,
                                        IndentationError)
        self.assertEqual(len(err), 4)
        self.assertEqual(err[1].strip(), "print(2)")
        self.assertIn("^", err[2])
        self.assertEqual(err[1].find("p"), err[2].find("^"))

    def test_base_exception(self):
        # Test that exceptions derived z BaseException are formatted right
        e = KeyboardInterrupt()
        lst = traceback.format_exception_only(e.__class__, e)
        self.assertEqual(lst, ['KeyboardInterrupt\n'])

    def test_format_exception_only_bad__str__(self):
        klasa X(Exception):
            def __str__(self):
                1/0
        err = traceback.format_exception_only(X, X())
        self.assertEqual(len(err), 1)
        str_value = '<unprintable %s object>' % X.__name__
        jeżeli X.__module__ w ('__main__', 'builtins'):
            str_name = X.__qualname__
        inaczej:
            str_name = '.'.join([X.__module__, X.__qualname__])
        self.assertEqual(err[0], "%s: %s\n" % (str_name, str_value))

    def test_without_exception(self):
        err = traceback.format_exception_only(Nic, Nic)
        self.assertEqual(err, ['Nic\n'])

    def test_encoded_file(self):
        # Test that tracebacks are correctly printed dla encoded source files:
        # - correct line number (Issue2384)
        # - respect file encoding (Issue3975)
        zaimportuj tempfile, sys, subprocess, os

        # The spawned subprocess has its stdout redirected to a PIPE, oraz its
        # encoding may be different z the current interpreter, on Windows
        # at least.
        process = subprocess.Popen([sys.executable, "-c",
                                    "zaimportuj sys; print(sys.stdout.encoding)"],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        stdout, stderr = process.communicate()
        output_encoding = str(stdout, 'ascii').splitlines()[0]

        def do_test(firstlines, message, charset, lineno):
            # Raise the message w a subprocess, oraz catch the output
            spróbuj:
                output = open(TESTFN, "w", encoding=charset)
                output.write("""{0}jeżeli 1:
                    zaimportuj traceback;
                    podnieś RuntimeError('{1}')
                    """.format(firstlines, message))
                output.close()
                process = subprocess.Popen([sys.executable, TESTFN],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                stdout, stderr = process.communicate()
                stdout = stdout.decode(output_encoding).splitlines()
            w_końcu:
                unlink(TESTFN)

            # The source lines are encoded przy the 'backslashreplace' handler
            encoded_message = message.encode(output_encoding,
                                             'backslashreplace')
            # oraz we just decoded them przy the output_encoding.
            message_ascii = encoded_message.decode(output_encoding)

            err_line = "raise RuntimeError('{0}')".format(message_ascii)
            err_msg = "RuntimeError: {0}".format(message_ascii)

            self.assertIn(("line %s" % lineno), stdout[1],
                "Invalid line number: {0!r} instead of {1}".format(
                    stdout[1], lineno))
            self.assertPrawda(stdout[2].endswith(err_line),
                "Invalid traceback line: {0!r} instead of {1!r}".format(
                    stdout[2], err_line))
            self.assertPrawda(stdout[3] == err_msg,
                "Invalid error message: {0!r} instead of {1!r}".format(
                    stdout[3], err_msg))

        do_test("", "foo", "ascii", 3)
        dla charset w ("ascii", "iso-8859-1", "utf-8", "GBK"):
            jeżeli charset == "ascii":
                text = "foo"
            albo_inaczej charset == "GBK":
                text = "\u4E02\u5100"
            inaczej:
                text = "h\xe9 ho"
            do_test("# coding: {0}\n".format(charset),
                    text, charset, 4)
            do_test("#!shebang\n# coding: {0}\n".format(charset),
                    text, charset, 5)
            do_test(" \t\f\n# coding: {0}\n".format(charset),
                    text, charset, 5)
        # Issue #18960: coding spec should has no effect
        do_test("0\n# coding: GBK\n", "h\xe9 ho", 'utf-8', 5)

    def test_print_traceback_at_exit(self):
        # Issue #22599: Ensure that it jest possible to use the traceback module
        # to display an exception at Python exit
        code = textwrap.dedent("""
            zaimportuj sys
            zaimportuj traceback

            klasa PrintExceptionAtExit(object):
                def __init__(self):
                    spróbuj:
                        x = 1 / 0
                    wyjąwszy Exception:
                        self.exc_info = sys.exc_info()
                        # self.exc_info[1] (traceback) contains frames:
                        # explicitly clear the reference to self w the current
                        # frame to przerwij a reference cycle
                        self = Nic

                def __del__(self):
                    traceback.print_exception(*self.exc_info)

            # Keep a reference w the module namespace to call the destructor
            # when the module jest unloaded
            obj = PrintExceptionAtExit()
        """)
        rc, stdout, stderr = assert_python_ok('-c', code)
        expected = [b'Traceback (most recent call last):',
                    b'  File "<string>", line 8, w __init__',
                    b'ZeroDivisionError: division by zero']
        self.assertEqual(stderr.splitlines(), expected)

    def test_print_exception(self):
        output = StringIO()
        traceback.print_exception(
            Exception, Exception("projector"), Nic, file=output
        )
        self.assertEqual(output.getvalue(), "Exception: projector\n")


klasa TracebackFormatTests(unittest.TestCase):

    def some_exception(self):
        podnieś KeyError('blah')

    @cpython_only
    def check_traceback_format(self, cleanup_func=Nic):
        z _testcapi zaimportuj traceback_print
        spróbuj:
            self.some_exception()
        wyjąwszy KeyError:
            type_, value, tb = sys.exc_info()
            jeżeli cleanup_func jest nie Nic:
                # Clear the inner frames, nie this one
                cleanup_func(tb.tb_next)
            traceback_fmt = 'Traceback (most recent call last):\n' + \
                            ''.join(traceback.format_tb(tb))
            file_ = StringIO()
            traceback_print(tb, file_)
            python_fmt  = file_.getvalue()
            # Call all _tb oraz _exc functions
            przy captured_output("stderr") jako tbstderr:
                traceback.print_tb(tb)
            tbfile = StringIO()
            traceback.print_tb(tb, file=tbfile)
            przy captured_output("stderr") jako excstderr:
                traceback.print_exc()
            excfmt = traceback.format_exc()
            excfile = StringIO()
            traceback.print_exc(file=excfile)
        inaczej:
            podnieś Error("unable to create test traceback string")

        # Make sure that Python oraz the traceback module format the same thing
        self.assertEqual(traceback_fmt, python_fmt)
        # Now verify the _tb func output
        self.assertEqual(tbstderr.getvalue(), tbfile.getvalue())
        # Now verify the _exc func output
        self.assertEqual(excstderr.getvalue(), excfile.getvalue())
        self.assertEqual(excfmt, excfile.getvalue())

        # Make sure that the traceback jest properly indented.
        tb_lines = python_fmt.splitlines()
        self.assertEqual(len(tb_lines), 5)
        banner = tb_lines[0]
        location, source_line = tb_lines[-2:]
        self.assertPrawda(banner.startswith('Traceback'))
        self.assertPrawda(location.startswith('  File'))
        self.assertPrawda(source_line.startswith('    podnieś'))

    def test_traceback_format(self):
        self.check_traceback_format()

    def test_traceback_format_with_cleared_frames(self):
        # Check that traceback formatting also works przy a clear()ed frame
        def cleanup_tb(tb):
            tb.tb_frame.clear()
        self.check_traceback_format(cleanup_tb)

    def test_stack_format(self):
        # Verify _stack functions. Note we have to use _getframe(1) to
        # compare them without this frame appearing w the output
        przy captured_output("stderr") jako ststderr:
            traceback.print_stack(sys._getframe(1))
        stfile = StringIO()
        traceback.print_stack(sys._getframe(1), file=stfile)
        self.assertEqual(ststderr.getvalue(), stfile.getvalue())

        stfmt = traceback.format_stack(sys._getframe(1))

        self.assertEqual(ststderr.getvalue(), "".join(stfmt))


cause_message = (
    "\nThe above exception was the direct cause "
    "of the following exception:\n\n")

context_message = (
    "\nDuring handling of the above exception, "
    "another exception occurred:\n\n")

boundaries = re.compile(
    '(%s|%s)' % (re.escape(cause_message), re.escape(context_message)))


klasa BaseExceptionReportingTests:

    def get_exception(self, exception_or_callable):
        jeżeli isinstance(exception_or_callable, Exception):
            zwróć exception_or_callable
        spróbuj:
            exception_or_callable()
        wyjąwszy Exception jako e:
            zwróć e

    def zero_div(self):
        1/0 # In zero_div

    def check_zero_div(self, msg):
        lines = msg.splitlines()
        self.assertPrawda(lines[-3].startswith('  File'))
        self.assertIn('1/0 # In zero_div', lines[-2])
        self.assertPrawda(lines[-1].startswith('ZeroDivisionError'), lines[-1])

    def test_simple(self):
        spróbuj:
            1/0 # Marker
        wyjąwszy ZeroDivisionError jako _:
            e = _
        lines = self.get_report(e).splitlines()
        self.assertEqual(len(lines), 4)
        self.assertPrawda(lines[0].startswith('Traceback'))
        self.assertPrawda(lines[1].startswith('  File'))
        self.assertIn('1/0 # Marker', lines[2])
        self.assertPrawda(lines[3].startswith('ZeroDivisionError'))

    def test_cause(self):
        def inner_raise():
            spróbuj:
                self.zero_div()
            wyjąwszy ZeroDivisionError jako e:
                podnieś KeyError z e
        def outer_raise():
            inner_raise() # Marker
        blocks = boundaries.split(self.get_report(outer_raise))
        self.assertEqual(len(blocks), 3)
        self.assertEqual(blocks[1], cause_message)
        self.check_zero_div(blocks[0])
        self.assertIn('inner_raise() # Marker', blocks[2])

    def test_context(self):
        def inner_raise():
            spróbuj:
                self.zero_div()
            wyjąwszy ZeroDivisionError:
                podnieś KeyError
        def outer_raise():
            inner_raise() # Marker
        blocks = boundaries.split(self.get_report(outer_raise))
        self.assertEqual(len(blocks), 3)
        self.assertEqual(blocks[1], context_message)
        self.check_zero_div(blocks[0])
        self.assertIn('inner_raise() # Marker', blocks[2])

    def test_context_suppression(self):
        spróbuj:
            spróbuj:
                podnieś Exception
            wyjąwszy:
                podnieś ZeroDivisionError z Nic
        wyjąwszy ZeroDivisionError jako _:
            e = _
        lines = self.get_report(e).splitlines()
        self.assertEqual(len(lines), 4)
        self.assertPrawda(lines[0].startswith('Traceback'))
        self.assertPrawda(lines[1].startswith('  File'))
        self.assertIn('ZeroDivisionError z Nic', lines[2])
        self.assertPrawda(lines[3].startswith('ZeroDivisionError'))

    def test_cause_and_context(self):
        # When both a cause oraz a context are set, only the cause should be
        # displayed oraz the context should be muted.
        def inner_raise():
            spróbuj:
                self.zero_div()
            wyjąwszy ZeroDivisionError jako _e:
                e = _e
            spróbuj:
                xyzzy
            wyjąwszy NameError:
                podnieś KeyError z e
        def outer_raise():
            inner_raise() # Marker
        blocks = boundaries.split(self.get_report(outer_raise))
        self.assertEqual(len(blocks), 3)
        self.assertEqual(blocks[1], cause_message)
        self.check_zero_div(blocks[0])
        self.assertIn('inner_raise() # Marker', blocks[2])

    def test_cause_recursive(self):
        def inner_raise():
            spróbuj:
                spróbuj:
                    self.zero_div()
                wyjąwszy ZeroDivisionError jako e:
                    z = e
                    podnieś KeyError z e
            wyjąwszy KeyError jako e:
                podnieś z z e
        def outer_raise():
            inner_raise() # Marker
        blocks = boundaries.split(self.get_report(outer_raise))
        self.assertEqual(len(blocks), 3)
        self.assertEqual(blocks[1], cause_message)
        # The first block jest the KeyError podnieśd z the ZeroDivisionError
        self.assertIn('raise KeyError z e', blocks[0])
        self.assertNotIn('1/0', blocks[0])
        # The second block (apart z the boundary) jest the ZeroDivisionError
        # re-raised z the KeyError
        self.assertIn('inner_raise() # Marker', blocks[2])
        self.check_zero_div(blocks[2])

    def test_syntax_error_offset_at_eol(self):
        # See #10186.
        def e():
            podnieś SyntaxError('', ('', 0, 5, 'hello'))
        msg = self.get_report(e).splitlines()
        self.assertEqual(msg[-2], "        ^")
        def e():
            exec("x = 5 | 4 |")
        msg = self.get_report(e).splitlines()
        self.assertEqual(msg[-2], '              ^')


klasa PyExcReportingTests(BaseExceptionReportingTests, unittest.TestCase):
    #
    # This checks reporting through the 'traceback' module, przy both
    # format_exception() oraz print_exception().
    #

    def get_report(self, e):
        e = self.get_exception(e)
        s = ''.join(
            traceback.format_exception(type(e), e, e.__traceback__))
        przy captured_output("stderr") jako sio:
            traceback.print_exception(type(e), e, e.__traceback__)
        self.assertEqual(sio.getvalue(), s)
        zwróć s


klasa CExcReportingTests(BaseExceptionReportingTests, unittest.TestCase):
    #
    # This checks built-in reporting by the interpreter.
    #

    @cpython_only
    def get_report(self, e):
        z _testcapi zaimportuj exception_print
        e = self.get_exception(e)
        przy captured_output("stderr") jako s:
            exception_print(e)
        zwróć s.getvalue()


klasa LimitTests(unittest.TestCase):

    ''' Tests dla limit argument.
        It's enough to test extact_tb, extract_stack oraz format_exception '''

    def last_raises1(self):
        podnieś Exception('Last podnieśd')

    def last_raises2(self):
        self.last_raises1()

    def last_raises3(self):
        self.last_raises2()

    def last_raises4(self):
        self.last_raises3()

    def last_raises5(self):
        self.last_raises4()

    def last_returns_frame1(self):
        zwróć sys._getframe()

    def last_returns_frame2(self):
        zwróć self.last_returns_frame1()

    def last_returns_frame3(self):
        zwróć self.last_returns_frame2()

    def last_returns_frame4(self):
        zwróć self.last_returns_frame3()

    def last_returns_frame5(self):
        zwróć self.last_returns_frame4()

    def test_extract_stack(self):
        frame = self.last_returns_frame5()
        def extract(**kwargs):
            zwróć traceback.extract_stack(frame, **kwargs)
        def assertEqualExcept(actual, expected, ignore):
            self.assertEqual(actual[:ignore], expected[:ignore])
            self.assertEqual(actual[ignore+1:], expected[ignore+1:])
            self.assertEqual(len(actual), len(expected))

        przy support.swap_attr(sys, 'tracebacklimit', 1000):
            nolim = extract()
            self.assertGreater(len(nolim), 5)
            self.assertEqual(extract(limit=2), nolim[-2:])
            assertEqualExcept(extract(limit=100), nolim[-100:], -5-1)
            self.assertEqual(extract(limit=-2), nolim[:2])
            assertEqualExcept(extract(limit=-100), nolim[:100], len(nolim)-5-1)
            self.assertEqual(extract(limit=0), [])
            usuń sys.tracebacklimit
            assertEqualExcept(extract(), nolim, -5-1)
            sys.tracebacklimit = 2
            self.assertEqual(extract(), nolim[-2:])
            self.assertEqual(extract(limit=3), nolim[-3:])
            self.assertEqual(extract(limit=-3), nolim[:3])
            sys.tracebacklimit = 0
            self.assertEqual(extract(), [])
            sys.tracebacklimit = -1
            self.assertEqual(extract(), [])

    def test_extract_tb(self):
        spróbuj:
            self.last_raises5()
        wyjąwszy Exception:
            exc_type, exc_value, tb = sys.exc_info()
        def extract(**kwargs):
            zwróć traceback.extract_tb(tb, **kwargs)

        przy support.swap_attr(sys, 'tracebacklimit', 1000):
            nolim = extract()
            self.assertEqual(len(nolim), 5+1)
            self.assertEqual(extract(limit=2), nolim[:2])
            self.assertEqual(extract(limit=10), nolim)
            self.assertEqual(extract(limit=-2), nolim[-2:])
            self.assertEqual(extract(limit=-10), nolim)
            self.assertEqual(extract(limit=0), [])
            usuń sys.tracebacklimit
            self.assertEqual(extract(), nolim)
            sys.tracebacklimit = 2
            self.assertEqual(extract(), nolim[:2])
            self.assertEqual(extract(limit=3), nolim[:3])
            self.assertEqual(extract(limit=-3), nolim[-3:])
            sys.tracebacklimit = 0
            self.assertEqual(extract(), [])
            sys.tracebacklimit = -1
            self.assertEqual(extract(), [])

    def test_format_exception(self):
        spróbuj:
            self.last_raises5()
        wyjąwszy Exception:
            exc_type, exc_value, tb = sys.exc_info()
        # [1:-1] to exclude "Traceback (...)" header oraz
        # exception type oraz value
        def extract(**kwargs):
            zwróć traceback.format_exception(exc_type, exc_value, tb, **kwargs)[1:-1]

        przy support.swap_attr(sys, 'tracebacklimit', 1000):
            nolim = extract()
            self.assertEqual(len(nolim), 5+1)
            self.assertEqual(extract(limit=2), nolim[:2])
            self.assertEqual(extract(limit=10), nolim)
            self.assertEqual(extract(limit=-2), nolim[-2:])
            self.assertEqual(extract(limit=-10), nolim)
            self.assertEqual(extract(limit=0), [])
            usuń sys.tracebacklimit
            self.assertEqual(extract(), nolim)
            sys.tracebacklimit = 2
            self.assertEqual(extract(), nolim[:2])
            self.assertEqual(extract(limit=3), nolim[:3])
            self.assertEqual(extract(limit=-3), nolim[-3:])
            sys.tracebacklimit = 0
            self.assertEqual(extract(), [])
            sys.tracebacklimit = -1
            self.assertEqual(extract(), [])


klasa MiscTracebackCases(unittest.TestCase):
    #
    # Check non-printing functions w traceback module
    #

    def test_clear(self):
        def outer():
            middle()
        def middle():
            inner()
        def inner():
            i = 1
            1/0

        spróbuj:
            outer()
        wyjąwszy:
            type_, value, tb = sys.exc_info()

        # Initial assertion: there's one local w the inner frame.
        inner_frame = tb.tb_next.tb_next.tb_next.tb_frame
        self.assertEqual(len(inner_frame.f_locals), 1)

        # Clear traceback frames
        traceback.clear_frames(tb)

        # Local variable dict should now be empty.
        self.assertEqual(len(inner_frame.f_locals), 0)


klasa TestFrame(unittest.TestCase):

    def test_basics(self):
        linecache.clearcache()
        linecache.lazycache("f", globals())
        f = traceback.FrameSummary("f", 1, "dummy")
        self.assertEqual(
            ("f", 1, "dummy", '"""Test cases dla traceback module"""'),
            tuple(f))
        self.assertEqual(Nic, f.locals)

    def test_lazy_lines(self):
        linecache.clearcache()
        f = traceback.FrameSummary("f", 1, "dummy", lookup_line=Nieprawda)
        self.assertEqual(Nic, f._line)
        linecache.lazycache("f", globals())
        self.assertEqual(
            '"""Test cases dla traceback module"""',
            f.line)

    def test_explicit_line(self):
        f = traceback.FrameSummary("f", 1, "dummy", line="line")
        self.assertEqual("line", f.line)


klasa TestStack(unittest.TestCase):

    def test_walk_stack(self):
        s = list(traceback.walk_stack(Nic))
        self.assertGreater(len(s), 10)

    def test_walk_tb(self):
        spróbuj:
            1/0
        wyjąwszy Exception:
            _, _, tb = sys.exc_info()
        s = list(traceback.walk_tb(tb))
        self.assertEqual(len(s), 1)

    def test_extract_stack(self):
        s = traceback.StackSummary.extract(traceback.walk_stack(Nic))
        self.assertIsInstance(s, traceback.StackSummary)

    def test_extract_stack_limit(self):
        s = traceback.StackSummary.extract(traceback.walk_stack(Nic), limit=5)
        self.assertEqual(len(s), 5)

    def test_extract_stack_lookup_lines(self):
        linecache.clearcache()
        linecache.updatecache('/foo.py', globals())
        c = test_code('/foo.py', 'method')
        f = test_frame(c, Nic, Nic)
        s = traceback.StackSummary.extract(iter([(f, 6)]), lookup_lines=Prawda)
        linecache.clearcache()
        self.assertEqual(s[0].line, "zaimportuj sys")

    def test_extract_stackup_deferred_lookup_lines(self):
        linecache.clearcache()
        c = test_code('/foo.py', 'method')
        f = test_frame(c, Nic, Nic)
        s = traceback.StackSummary.extract(iter([(f, 6)]), lookup_lines=Nieprawda)
        self.assertEqual({}, linecache.cache)
        linecache.updatecache('/foo.py', globals())
        self.assertEqual(s[0].line, "zaimportuj sys")

    def test_from_list(self):
        s = traceback.StackSummary.from_list([('foo.py', 1, 'fred', 'line')])
        self.assertEqual(
            ['  File "foo.py", line 1, w fred\n    line\n'],
            s.format())

    def test_from_list_edited_stack(self):
        s = traceback.StackSummary.from_list([('foo.py', 1, 'fred', 'line')])
        s[0] = ('foo.py', 2, 'fred', 'line')
        s2 = traceback.StackSummary.from_list(s)
        self.assertEqual(
            ['  File "foo.py", line 2, w fred\n    line\n'],
            s2.format())

    def test_format_smoke(self):
        # For detailed tests see the format_list tests, which consume the same
        # code.
        s = traceback.StackSummary.from_list([('foo.py', 1, 'fred', 'line')])
        self.assertEqual(
            ['  File "foo.py", line 1, w fred\n    line\n'],
            s.format())

    def test_locals(self):
        linecache.updatecache('/foo.py', globals())
        c = test_code('/foo.py', 'method')
        f = test_frame(c, globals(), {'something': 1})
        s = traceback.StackSummary.extract(iter([(f, 6)]), capture_locals=Prawda)
        self.assertEqual(s[0].locals, {'something': '1'})

    def test_no_locals(self):
        linecache.updatecache('/foo.py', globals())
        c = test_code('/foo.py', 'method')
        f = test_frame(c, globals(), {'something': 1})
        s = traceback.StackSummary.extract(iter([(f, 6)]))
        self.assertEqual(s[0].locals, Nic)

    def test_format_locals(self):
        def some_inner(k, v):
            a = 1
            b = 2
            zwróć traceback.StackSummary.extract(
                traceback.walk_stack(Nic), capture_locals=Prawda, limit=1)
        s = some_inner(3, 4)
        self.assertEqual(
            ['  File "%s", line %d, w some_inner\n'
             '    traceback.walk_stack(Nic), capture_locals=Prawda, limit=1)\n'
             '    a = 1\n'
             '    b = 2\n'
             '    k = 3\n'
             '    v = 4\n' % (__file__, some_inner.__code__.co_firstlineno + 4)
            ], s.format())

klasa TestTracebackException(unittest.TestCase):

    def test_smoke(self):
        spróbuj:
            1/0
        wyjąwszy Exception:
            exc_info = sys.exc_info()
            exc = traceback.TracebackException(*exc_info)
            expected_stack = traceback.StackSummary.extract(
                traceback.walk_tb(exc_info[2]))
        self.assertEqual(Nic, exc.__cause__)
        self.assertEqual(Nic, exc.__context__)
        self.assertEqual(Nieprawda, exc.__suppress_context__)
        self.assertEqual(expected_stack, exc.stack)
        self.assertEqual(exc_info[0], exc.exc_type)
        self.assertEqual(str(exc_info[1]), str(exc))

    def test_from_exception(self):
        # Check all the parameters are accepted.
        def foo():
            1/0
        spróbuj:
            foo()
        wyjąwszy Exception jako e:
            exc_info = sys.exc_info()
            self.expected_stack = traceback.StackSummary.extract(
                traceback.walk_tb(exc_info[2]), limit=1, lookup_lines=Nieprawda,
                capture_locals=Prawda)
            self.exc = traceback.TracebackException.from_exception(
                e, limit=1, lookup_lines=Nieprawda, capture_locals=Prawda)
        expected_stack = self.expected_stack
        exc = self.exc
        self.assertEqual(Nic, exc.__cause__)
        self.assertEqual(Nic, exc.__context__)
        self.assertEqual(Nieprawda, exc.__suppress_context__)
        self.assertEqual(expected_stack, exc.stack)
        self.assertEqual(exc_info[0], exc.exc_type)
        self.assertEqual(str(exc_info[1]), str(exc))

    def test_cause(self):
        spróbuj:
            spróbuj:
                1/0
            w_końcu:
                exc_info_context = sys.exc_info()
                exc_context = traceback.TracebackException(*exc_info_context)
                cause = Exception("cause")
                podnieś Exception("uh oh") z cause
        wyjąwszy Exception:
            exc_info = sys.exc_info()
            exc = traceback.TracebackException(*exc_info)
            expected_stack = traceback.StackSummary.extract(
                traceback.walk_tb(exc_info[2]))
        exc_cause = traceback.TracebackException(Exception, cause, Nic)
        self.assertEqual(exc_cause, exc.__cause__)
        self.assertEqual(exc_context, exc.__context__)
        self.assertEqual(Prawda, exc.__suppress_context__)
        self.assertEqual(expected_stack, exc.stack)
        self.assertEqual(exc_info[0], exc.exc_type)
        self.assertEqual(str(exc_info[1]), str(exc))

    def test_context(self):
        spróbuj:
            spróbuj:
                1/0
            w_końcu:
                exc_info_context = sys.exc_info()
                exc_context = traceback.TracebackException(*exc_info_context)
                podnieś Exception("uh oh")
        wyjąwszy Exception:
            exc_info = sys.exc_info()
            exc = traceback.TracebackException(*exc_info)
            expected_stack = traceback.StackSummary.extract(
                traceback.walk_tb(exc_info[2]))
        self.assertEqual(Nic, exc.__cause__)
        self.assertEqual(exc_context, exc.__context__)
        self.assertEqual(Nieprawda, exc.__suppress_context__)
        self.assertEqual(expected_stack, exc.stack)
        self.assertEqual(exc_info[0], exc.exc_type)
        self.assertEqual(str(exc_info[1]), str(exc))

    def test_limit(self):
        def recurse(n):
            jeżeli n:
                recurse(n-1)
            inaczej:
                1/0
        spróbuj:
            recurse(10)
        wyjąwszy Exception:
            exc_info = sys.exc_info()
            exc = traceback.TracebackException(*exc_info, limit=5)
            expected_stack = traceback.StackSummary.extract(
                traceback.walk_tb(exc_info[2]), limit=5)
        self.assertEqual(expected_stack, exc.stack)

    def test_lookup_lines(self):
        linecache.clearcache()
        e = Exception("uh oh")
        c = test_code('/foo.py', 'method')
        f = test_frame(c, Nic, Nic)
        tb = test_tb(f, 6, Nic)
        exc = traceback.TracebackException(Exception, e, tb, lookup_lines=Nieprawda)
        self.assertEqual({}, linecache.cache)
        linecache.updatecache('/foo.py', globals())
        self.assertEqual(exc.stack[0].line, "zaimportuj sys")

    def test_locals(self):
        linecache.updatecache('/foo.py', globals())
        e = Exception("uh oh")
        c = test_code('/foo.py', 'method')
        f = test_frame(c, globals(), {'something': 1, 'other': 'string'})
        tb = test_tb(f, 6, Nic)
        exc = traceback.TracebackException(
            Exception, e, tb, capture_locals=Prawda)
        self.assertEqual(
            exc.stack[0].locals, {'something': '1', 'other': "'string'"})

    def test_no_locals(self):
        linecache.updatecache('/foo.py', globals())
        e = Exception("uh oh")
        c = test_code('/foo.py', 'method')
        f = test_frame(c, globals(), {'something': 1})
        tb = test_tb(f, 6, Nic)
        exc = traceback.TracebackException(Exception, e, tb)
        self.assertEqual(exc.stack[0].locals, Nic)

    def test_traceback_header(self):
        # do nie print a traceback header jeżeli exc_traceback jest Nic
        # see issue #24695
        exc = traceback.TracebackException(Exception, Exception("haven"), Nic)
        self.assertEqual(list(exc.format()), ["Exception: haven\n"])


klasa MiscTest(unittest.TestCase):

    def test_all(self):
        expected = set()
        blacklist = {'print_list'}
        dla name w dir(traceback):
            jeżeli name.startswith('_') albo name w blacklist:
                kontynuuj
            module_object = getattr(traceback, name)
            jeżeli getattr(module_object, '__module__', Nic) == 'traceback':
                expected.add(name)
        self.assertCountEqual(traceback.__all__, expected)


jeżeli __name__ == "__main__":
    unittest.main()
