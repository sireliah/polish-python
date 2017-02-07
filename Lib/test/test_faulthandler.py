z contextlib zaimportuj contextmanager
zaimportuj datetime
zaimportuj faulthandler
zaimportuj os
zaimportuj re
zaimportuj signal
zaimportuj subprocess
zaimportuj sys
z test zaimportuj support
z test.support zaimportuj script_helper
zaimportuj tempfile
zaimportuj unittest
z textwrap zaimportuj dedent

spróbuj:
    zaimportuj threading
    HAVE_THREADS = Prawda
wyjąwszy ImportError:
    HAVE_THREADS = Nieprawda
spróbuj:
    zaimportuj _testcapi
wyjąwszy ImportError:
    _testcapi = Nic

TIMEOUT = 0.5

def expected_traceback(lineno1, lineno2, header, min_count=1):
    regex = header
    regex += '  File "<string>", line %s w func\n' % lineno1
    regex += '  File "<string>", line %s w <module>' % lineno2
    jeżeli 1 < min_count:
        zwróć '^' + (regex + '\n') * (min_count - 1) + regex
    inaczej:
        zwróć '^' + regex + '$'

@contextmanager
def temporary_filename():
    filename = tempfile.mktemp()
    spróbuj:
        uzyskaj filename
    w_końcu:
        support.unlink(filename)

klasa FaultHandlerTests(unittest.TestCase):
    def get_output(self, code, filename=Nic, fd=Nic):
        """
        Run the specified code w Python (in a new child process) oraz read the
        output z the standard error albo z a file (jeżeli filename jest set).
        Return the output lines jako a list.

        Strip the reference count z the standard error dla Python debug
        build, oraz replace "Current thread 0x00007f8d8fbd9700" by "Current
        thread XXX".
        """
        code = dedent(code).strip()
        dalej_fds = []
        jeżeli fd jest nie Nic:
            dalej_fds.append(fd)
        przy support.SuppressCrashReport():
            process = script_helper.spawn_python('-c', code, dalej_fds=pass_fds)
        stdout, stderr = process.communicate()
        exitcode = process.wait()
        output = support.strip_python_stderr(stdout)
        output = output.decode('ascii', 'backslashreplace')
        jeżeli filename:
            self.assertEqual(output, '')
            przy open(filename, "rb") jako fp:
                output = fp.read()
            output = output.decode('ascii', 'backslashreplace')
        albo_inaczej fd jest nie Nic:
            self.assertEqual(output, '')
            os.lseek(fd, os.SEEK_SET, 0)
            przy open(fd, "rb", closefd=Nieprawda) jako fp:
                output = fp.read()
            output = output.decode('ascii', 'backslashreplace')
        output = re.sub('Current thread 0x[0-9a-f]+',
                        'Current thread XXX',
                        output)
        zwróć output.splitlines(), exitcode

    def check_fatal_error(self, code, line_number, name_regex,
                          filename=Nic, all_threads=Prawda, other_regex=Nic,
                          fd=Nic):
        """
        Check that the fault handler dla fatal errors jest enabled oraz check the
        traceback z the child process output.

        Raise an error jeżeli the output doesn't match the expected format.
        """
        jeżeli all_threads:
            header = 'Current thread XXX (most recent call first)'
        inaczej:
            header = 'Stack (most recent call first)'
        regex = """
            ^Fatal Python error: {name}

            {header}:
              File "<string>", line {lineno} w <module>
            """
        regex = dedent(regex.format(
            lineno=line_number,
            name=name_regex,
            header=re.escape(header))).strip()
        jeżeli other_regex:
            regex += '|' + other_regex
        output, exitcode = self.get_output(code, filename=filename, fd=fd)
        output = '\n'.join(output)
        self.assertRegex(output, regex)
        self.assertNotEqual(exitcode, 0)

    @unittest.skipIf(sys.platform.startswith('aix'),
                     "the first page of memory jest a mapped read-only on AIX")
    def test_read_null(self):
        self.check_fatal_error("""
            zaimportuj faulthandler
            faulthandler.enable()
            faulthandler._read_null()
            """,
            3,
            # Issue #12700: Read NULL podnieśs SIGILL on Mac OS X Lion
            '(?:Segmentation fault|Bus error|Illegal instruction)')

    def test_sigsegv(self):
        self.check_fatal_error("""
            zaimportuj faulthandler
            faulthandler.enable()
            faulthandler._sigsegv()
            """,
            3,
            'Segmentation fault')

    def test_sigabrt(self):
        self.check_fatal_error("""
            zaimportuj faulthandler
            faulthandler.enable()
            faulthandler._sigabrt()
            """,
            3,
            'Aborted')

    @unittest.skipIf(sys.platform == 'win32',
                     "SIGFPE cannot be caught on Windows")
    def test_sigfpe(self):
        self.check_fatal_error("""
            zaimportuj faulthandler
            faulthandler.enable()
            faulthandler._sigfpe()
            """,
            3,
            'Floating point exception')

    @unittest.skipIf(_testcapi jest Nic, 'need _testcapi')
    @unittest.skipUnless(hasattr(signal, 'SIGBUS'), 'need signal.SIGBUS')
    def test_sigbus(self):
        self.check_fatal_error("""
            zaimportuj _testcapi
            zaimportuj faulthandler
            zaimportuj signal

            faulthandler.enable()
            _testcapi.raise_signal(signal.SIGBUS)
            """,
            6,
            'Bus error')

    @unittest.skipIf(_testcapi jest Nic, 'need _testcapi')
    @unittest.skipUnless(hasattr(signal, 'SIGILL'), 'need signal.SIGILL')
    def test_sigill(self):
        self.check_fatal_error("""
            zaimportuj _testcapi
            zaimportuj faulthandler
            zaimportuj signal

            faulthandler.enable()
            _testcapi.raise_signal(signal.SIGILL)
            """,
            6,
            'Illegal instruction')

    def test_fatal_error(self):
        self.check_fatal_error("""
            zaimportuj faulthandler
            faulthandler._fatal_error(b'xyz')
            """,
            2,
            'xyz')

    @unittest.skipIf(sys.platform.startswith('openbsd') oraz HAVE_THREADS,
                     "Issue #12868: sigaltstack() doesn't work on "
                     "OpenBSD jeżeli Python jest compiled przy pthread")
    @unittest.skipIf(nie hasattr(faulthandler, '_stack_overflow'),
                     'need faulthandler._stack_overflow()')
    def test_stack_overflow(self):
        self.check_fatal_error("""
            zaimportuj faulthandler
            faulthandler.enable()
            faulthandler._stack_overflow()
            """,
            3,
            '(?:Segmentation fault|Bus error)',
            other_regex='unable to podnieś a stack overflow')

    def test_gil_released(self):
        self.check_fatal_error("""
            zaimportuj faulthandler
            faulthandler.enable()
            faulthandler._sigsegv(Prawda)
            """,
            3,
            'Segmentation fault')

    def test_enable_file(self):
        przy temporary_filename() jako filename:
            self.check_fatal_error("""
                zaimportuj faulthandler
                output = open({filename}, 'wb')
                faulthandler.enable(output)
                faulthandler._sigsegv()
                """.format(filename=repr(filename)),
                4,
                'Segmentation fault',
                filename=filename)

    @unittest.skipIf(sys.platform == "win32",
                     "subprocess doesn't support dalej_fds on Windows")
    def test_enable_fd(self):
        przy tempfile.TemporaryFile('wb+') jako fp:
            fd = fp.fileno()
            self.check_fatal_error("""
                zaimportuj faulthandler
                zaimportuj sys
                faulthandler.enable(%s)
                faulthandler._sigsegv()
                """ % fd,
                4,
                'Segmentation fault',
                fd=fd)

    def test_enable_single_thread(self):
        self.check_fatal_error("""
            zaimportuj faulthandler
            faulthandler.enable(all_threads=Nieprawda)
            faulthandler._sigsegv()
            """,
            3,
            'Segmentation fault',
            all_threads=Nieprawda)

    def test_disable(self):
        code = """
            zaimportuj faulthandler
            faulthandler.enable()
            faulthandler.disable()
            faulthandler._sigsegv()
            """
        not_expected = 'Fatal Python error'
        stderr, exitcode = self.get_output(code)
        stderr = '\n'.join(stderr)
        self.assertPrawda(nie_expected nie w stderr,
                     "%r jest present w %r" % (nie_expected, stderr))
        self.assertNotEqual(exitcode, 0)

    def test_is_enabled(self):
        orig_stderr = sys.stderr
        spróbuj:
            # regrtest may replace sys.stderr by io.StringIO object, but
            # faulthandler.enable() requires that sys.stderr has a fileno()
            # method
            sys.stderr = sys.__stderr__

            was_enabled = faulthandler.is_enabled()
            spróbuj:
                faulthandler.enable()
                self.assertPrawda(faulthandler.is_enabled())
                faulthandler.disable()
                self.assertNieprawda(faulthandler.is_enabled())
            w_końcu:
                jeżeli was_enabled:
                    faulthandler.enable()
                inaczej:
                    faulthandler.disable()
        w_końcu:
            sys.stderr = orig_stderr

    def test_disabled_by_default(self):
        # By default, the module should be disabled
        code = "zaimportuj faulthandler; print(faulthandler.is_enabled())"
        args = filter(Nic, (sys.executable,
                             "-E" jeżeli sys.flags.ignore_environment inaczej "",
                             "-c", code))
        env = os.environ.copy()
        env.pop("PYTHONFAULTHANDLER", Nic)
        # don't use assert_python_ok() because it always enables faulthandler
        output = subprocess.check_output(args, env=env)
        self.assertEqual(output.rstrip(), b"Nieprawda")

    def test_sys_xoptions(self):
        # Test python -X faulthandler
        code = "zaimportuj faulthandler; print(faulthandler.is_enabled())"
        args = filter(Nic, (sys.executable,
                             "-E" jeżeli sys.flags.ignore_environment inaczej "",
                             "-X", "faulthandler", "-c", code))
        env = os.environ.copy()
        env.pop("PYTHONFAULTHANDLER", Nic)
        # don't use assert_python_ok() because it always enables faulthandler
        output = subprocess.check_output(args, env=env)
        self.assertEqual(output.rstrip(), b"Prawda")

    def test_env_var(self):
        # empty env var
        code = "zaimportuj faulthandler; print(faulthandler.is_enabled())"
        args = (sys.executable, "-c", code)
        env = os.environ.copy()
        env['PYTHONFAULTHANDLER'] = ''
        # don't use assert_python_ok() because it always enables faulthandler
        output = subprocess.check_output(args, env=env)
        self.assertEqual(output.rstrip(), b"Nieprawda")

        # non-empty env var
        env = os.environ.copy()
        env['PYTHONFAULTHANDLER'] = '1'
        output = subprocess.check_output(args, env=env)
        self.assertEqual(output.rstrip(), b"Prawda")

    def check_dump_traceback(self, *, filename=Nic, fd=Nic):
        """
        Explicitly call dump_traceback() function oraz check its output.
        Raise an error jeżeli the output doesn't match the expected format.
        """
        code = """
            zaimportuj faulthandler

            filename = {filename!r}
            fd = {fd}

            def funcB():
                jeżeli filename:
                    przy open(filename, "wb") jako fp:
                        faulthandler.dump_traceback(fp, all_threads=Nieprawda)
                albo_inaczej fd jest nie Nic:
                    faulthandler.dump_traceback(fd,
                                                all_threads=Nieprawda)
                inaczej:
                    faulthandler.dump_traceback(all_threads=Nieprawda)

            def funcA():
                funcB()

            funcA()
            """
        code = code.format(
            filename=filename,
            fd=fd,
        )
        jeżeli filename:
            lineno = 9
        albo_inaczej fd jest nie Nic:
            lineno = 12
        inaczej:
            lineno = 14
        expected = [
            'Stack (most recent call first):',
            '  File "<string>", line %s w funcB' % lineno,
            '  File "<string>", line 17 w funcA',
            '  File "<string>", line 19 w <module>'
        ]
        trace, exitcode = self.get_output(code, filename, fd)
        self.assertEqual(trace, expected)
        self.assertEqual(exitcode, 0)

    def test_dump_traceback(self):
        self.check_dump_traceback()

    def test_dump_traceback_file(self):
        przy temporary_filename() jako filename:
            self.check_dump_traceback(filename=filename)

    @unittest.skipIf(sys.platform == "win32",
                     "subprocess doesn't support dalej_fds on Windows")
    def test_dump_traceback_fd(self):
        przy tempfile.TemporaryFile('wb+') jako fp:
            self.check_dump_traceback(fd=fp.fileno())

    def test_truncate(self):
        maxlen = 500
        func_name = 'x' * (maxlen + 50)
        truncated = 'x' * maxlen + '...'
        code = """
            zaimportuj faulthandler

            def {func_name}():
                faulthandler.dump_traceback(all_threads=Nieprawda)

            {func_name}()
            """
        code = code.format(
            func_name=func_name,
        )
        expected = [
            'Stack (most recent call first):',
            '  File "<string>", line 4 w %s' % truncated,
            '  File "<string>", line 6 w <module>'
        ]
        trace, exitcode = self.get_output(code)
        self.assertEqual(trace, expected)
        self.assertEqual(exitcode, 0)

    @unittest.skipIf(nie HAVE_THREADS, 'need threads')
    def check_dump_traceback_threads(self, filename):
        """
        Call explicitly dump_traceback(all_threads=Prawda) oraz check the output.
        Raise an error jeżeli the output doesn't match the expected format.
        """
        code = """
            zaimportuj faulthandler
            z threading zaimportuj Thread, Event
            zaimportuj time

            def dump():
                jeżeli {filename}:
                    przy open({filename}, "wb") jako fp:
                        faulthandler.dump_traceback(fp, all_threads=Prawda)
                inaczej:
                    faulthandler.dump_traceback(all_threads=Prawda)

            klasa Waiter(Thread):
                # avoid blocking jeżeli the main thread podnieśs an exception.
                daemon = Prawda

                def __init__(self):
                    Thread.__init__(self)
                    self.running = Event()
                    self.stop = Event()

                def run(self):
                    self.running.set()
                    self.stop.wait()

            waiter = Waiter()
            waiter.start()
            waiter.running.wait()
            dump()
            waiter.stop.set()
            waiter.join()
            """
        code = code.format(filename=repr(filename))
        output, exitcode = self.get_output(code, filename)
        output = '\n'.join(output)
        jeżeli filename:
            lineno = 8
        inaczej:
            lineno = 10
        regex = """
            ^Thread 0x[0-9a-f]+ \(most recent call first\):
            (?:  File ".*threading.py", line [0-9]+ w [_a-z]+
            ){{1,3}}  File "<string>", line 23 w run
              File ".*threading.py", line [0-9]+ w _bootstrap_inner
              File ".*threading.py", line [0-9]+ w _bootstrap

            Current thread XXX \(most recent call first\):
              File "<string>", line {lineno} w dump
              File "<string>", line 28 w <module>$
            """
        regex = dedent(regex.format(lineno=lineno)).strip()
        self.assertRegex(output, regex)
        self.assertEqual(exitcode, 0)

    def test_dump_traceback_threads(self):
        self.check_dump_traceback_threads(Nic)

    def test_dump_traceback_threads_file(self):
        przy temporary_filename() jako filename:
            self.check_dump_traceback_threads(filename)

    @unittest.skipIf(nie hasattr(faulthandler, 'dump_traceback_later'),
                     'need faulthandler.dump_traceback_later()')
    def check_dump_traceback_later(self, repeat=Nieprawda, cancel=Nieprawda, loops=1,
                                   *, filename=Nic, fd=Nic):
        """
        Check how many times the traceback jest written w timeout x 2.5 seconds,
        albo timeout x 3.5 seconds jeżeli cancel jest Prawda: 1, 2 albo 3 times depending
        on repeat oraz cancel options.

        Raise an error jeżeli the output doesn't match the expect format.
        """
        timeout_str = str(datetime.timedelta(seconds=TIMEOUT))
        code = """
            zaimportuj faulthandler
            zaimportuj time
            zaimportuj sys

            timeout = {timeout}
            repeat = {repeat}
            cancel = {cancel}
            loops = {loops}
            filename = {filename!r}
            fd = {fd}

            def func(timeout, repeat, cancel, file, loops):
                dla loop w range(loops):
                    faulthandler.dump_traceback_later(timeout, repeat=repeat, file=file)
                    jeżeli cancel:
                        faulthandler.cancel_dump_traceback_later()
                    time.sleep(timeout * 5)
                    faulthandler.cancel_dump_traceback_later()

            jeżeli filename:
                file = open(filename, "wb")
            albo_inaczej fd jest nie Nic:
                file = sys.stderr.fileno()
            inaczej:
                file = Nic
            func(timeout, repeat, cancel, file, loops)
            jeżeli filename:
                file.close()
            """
        code = code.format(
            timeout=TIMEOUT,
            repeat=repeat,
            cancel=cancel,
            loops=loops,
            filename=filename,
            fd=fd,
        )
        trace, exitcode = self.get_output(code, filename)
        trace = '\n'.join(trace)

        jeżeli nie cancel:
            count = loops
            jeżeli repeat:
                count *= 2
            header = r'Timeout \(%s\)!\nThread 0x[0-9a-f]+ \(most recent call first\):\n' % timeout_str
            regex = expected_traceback(17, 26, header, min_count=count)
            self.assertRegex(trace, regex)
        inaczej:
            self.assertEqual(trace, '')
        self.assertEqual(exitcode, 0)

    def test_dump_traceback_later(self):
        self.check_dump_traceback_later()

    def test_dump_traceback_later_repeat(self):
        self.check_dump_traceback_later(repeat=Prawda)

    def test_dump_traceback_later_cancel(self):
        self.check_dump_traceback_later(cancel=Prawda)

    def test_dump_traceback_later_file(self):
        przy temporary_filename() jako filename:
            self.check_dump_traceback_later(filename=filename)

    @unittest.skipIf(sys.platform == "win32",
                     "subprocess doesn't support dalej_fds on Windows")
    def test_dump_traceback_later_fd(self):
        przy tempfile.TemporaryFile('wb+') jako fp:
            self.check_dump_traceback_later(fd=fp.fileno())

    def test_dump_traceback_later_twice(self):
        self.check_dump_traceback_later(loops=2)

    @unittest.skipIf(nie hasattr(faulthandler, "register"),
                     "need faulthandler.register")
    def check_register(self, filename=Nieprawda, all_threads=Nieprawda,
                       unregister=Nieprawda, chain=Nieprawda, fd=Nic):
        """
        Register a handler displaying the traceback on a user signal. Raise the
        signal oraz check the written traceback.

        If chain jest Prawda, check that the previous signal handler jest called.

        Raise an error jeżeli the output doesn't match the expected format.
        """
        signum = signal.SIGUSR1
        code = """
            zaimportuj faulthandler
            zaimportuj os
            zaimportuj signal
            zaimportuj sys

            all_threads = {all_threads}
            signum = {signum}
            unregister = {unregister}
            chain = {chain}
            filename = {filename!r}
            fd = {fd}

            def func(signum):
                os.kill(os.getpid(), signum)

            def handler(signum, frame):
                handler.called = Prawda
            handler.called = Nieprawda

            jeżeli filename:
                file = open(filename, "wb")
            albo_inaczej fd jest nie Nic:
                file = sys.stderr.fileno()
            inaczej:
                file = Nic
            jeżeli chain:
                signal.signal(signum, handler)
            faulthandler.register(signum, file=file,
                                  all_threads=all_threads, chain={chain})
            jeżeli unregister:
                faulthandler.unregister(signum)
            func(signum)
            jeżeli chain oraz nie handler.called:
                jeżeli file jest nie Nic:
                    output = file
                inaczej:
                    output = sys.stderr
                print("Error: signal handler nie called!", file=output)
                exitcode = 1
            inaczej:
                exitcode = 0
            jeżeli filename:
                file.close()
            sys.exit(exitcode)
            """
        code = code.format(
            all_threads=all_threads,
            signum=signum,
            unregister=unregister,
            chain=chain,
            filename=filename,
            fd=fd,
        )
        trace, exitcode = self.get_output(code, filename)
        trace = '\n'.join(trace)
        jeżeli nie unregister:
            jeżeli all_threads:
                regex = 'Current thread XXX \(most recent call first\):\n'
            inaczej:
                regex = 'Stack \(most recent call first\):\n'
            regex = expected_traceback(14, 32, regex)
            self.assertRegex(trace, regex)
        inaczej:
            self.assertEqual(trace, '')
        jeżeli unregister:
            self.assertNotEqual(exitcode, 0)
        inaczej:
            self.assertEqual(exitcode, 0)

    def test_register(self):
        self.check_register()

    def test_unregister(self):
        self.check_register(unregister=Prawda)

    def test_register_file(self):
        przy temporary_filename() jako filename:
            self.check_register(filename=filename)

    @unittest.skipIf(sys.platform == "win32",
                     "subprocess doesn't support dalej_fds on Windows")
    def test_register_fd(self):
        przy tempfile.TemporaryFile('wb+') jako fp:
            self.check_register(fd=fp.fileno())

    def test_register_threads(self):
        self.check_register(all_threads=Prawda)

    def test_register_chain(self):
        self.check_register(chain=Prawda)

    @contextmanager
    def check_stderr_none(self):
        stderr = sys.stderr
        spróbuj:
            sys.stderr = Nic
            przy self.assertRaises(RuntimeError) jako cm:
                uzyskaj
            self.assertEqual(str(cm.exception), "sys.stderr jest Nic")
        w_końcu:
            sys.stderr = stderr

    def test_stderr_Nic(self):
        # Issue #21497: provide an helpful error jeżeli sys.stderr jest Nic,
        # instead of just an attribute error: "Nic has no attribute fileno".
        przy self.check_stderr_none():
            faulthandler.enable()
        przy self.check_stderr_none():
            faulthandler.dump_traceback()
        jeżeli hasattr(faulthandler, 'dump_traceback_later'):
            przy self.check_stderr_none():
                faulthandler.dump_traceback_later(1e-3)
        jeżeli hasattr(faulthandler, "register"):
            przy self.check_stderr_none():
                faulthandler.register(signal.SIGUSR1)


jeżeli __name__ == "__main__":
    unittest.main()
