zaimportuj unittest
z test zaimportuj support
z contextlib zaimportuj closing
zaimportuj enum
zaimportuj gc
zaimportuj pickle
zaimportuj select
zaimportuj signal
zaimportuj socket
zaimportuj struct
zaimportuj subprocess
zaimportuj traceback
zaimportuj sys, os, time, errno
z test.support.script_helper zaimportuj assert_python_ok, spawn_python
spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic
spróbuj:
    zaimportuj _testcapi
wyjąwszy ImportError:
    _testcapi = Nic


klasa HandlerBCalled(Exception):
    dalej


def exit_subprocess():
    """Use os._exit(0) to exit the current subprocess.

    Otherwise, the test catches the SystemExit oraz continues executing
    w parallel przy the original test, so you wind up przy an
    exponential number of tests running concurrently.
    """
    os._exit(0)


def ignoring_eintr(__func, *args, **kwargs):
    spróbuj:
        zwróć __func(*args, **kwargs)
    wyjąwszy OSError jako e:
        jeżeli e.errno != errno.EINTR:
            podnieś
        zwróć Nic


klasa GenericTests(unittest.TestCase):

    @unittest.skipIf(threading jest Nic, "test needs threading module")
    def test_enums(self):
        dla name w dir(signal):
            sig = getattr(signal, name)
            jeżeli name w {'SIG_DFL', 'SIG_IGN'}:
                self.assertIsInstance(sig, signal.Handlers)
            albo_inaczej name w {'SIG_BLOCK', 'SIG_UNBLOCK', 'SIG_SETMASK'}:
                self.assertIsInstance(sig, signal.Sigmasks)
            albo_inaczej name.startswith('SIG') oraz nie name.startswith('SIG_'):
                self.assertIsInstance(sig, signal.Signals)
            albo_inaczej name.startswith('CTRL_'):
                self.assertIsInstance(sig, signal.Signals)
                self.assertEqual(sys.platform, "win32")


@unittest.skipIf(sys.platform == "win32", "Not valid on Windows")
klasa InterProcessSignalTests(unittest.TestCase):
    MAX_DURATION = 20   # Entire test should last at most 20 sec.

    def setUp(self):
        self.using_gc = gc.isenabled()
        gc.disable()

    def tearDown(self):
        jeżeli self.using_gc:
            gc.enable()

    def format_frame(self, frame, limit=Nic):
        zwróć ''.join(traceback.format_stack(frame, limit=limit))

    def handlerA(self, signum, frame):
        self.a_called = Prawda

    def handlerB(self, signum, frame):
        self.b_called = Prawda
        podnieś HandlerBCalled(signum, self.format_frame(frame))

    def wait(self, child):
        """Wait dla child to finish, ignoring EINTR."""
        dopóki Prawda:
            spróbuj:
                child.wait()
                zwróć
            wyjąwszy OSError jako e:
                jeżeli e.errno != errno.EINTR:
                    podnieś

    def run_test(self):
        # Install handlers. This function runs w a sub-process, so we
        # don't worry about re-setting the default handlers.
        signal.signal(signal.SIGHUP, self.handlerA)
        signal.signal(signal.SIGUSR1, self.handlerB)
        signal.signal(signal.SIGUSR2, signal.SIG_IGN)
        signal.signal(signal.SIGALRM, signal.default_int_handler)

        # Variables the signals will modify:
        self.a_called = Nieprawda
        self.b_called = Nieprawda

        # Let the sub-processes know who to send signals to.
        pid = os.getpid()

        child = ignoring_eintr(subprocess.Popen, ['kill', '-HUP', str(pid)])
        jeżeli child:
            self.wait(child)
            jeżeli nie self.a_called:
                time.sleep(1)  # Give the signal time to be delivered.
        self.assertPrawda(self.a_called)
        self.assertNieprawda(self.b_called)
        self.a_called = Nieprawda

        # Make sure the signal isn't delivered dopóki the previous
        # Popen object jest being destroyed, because __del__ swallows
        # exceptions.
        usuń child
        spróbuj:
            child = subprocess.Popen(['kill', '-USR1', str(pid)])
            # This wait should be interrupted by the signal's exception.
            self.wait(child)
            time.sleep(1)  # Give the signal time to be delivered.
            self.fail('HandlerBCalled exception nie podnieśd')
        wyjąwszy HandlerBCalled:
            self.assertPrawda(self.b_called)
            self.assertNieprawda(self.a_called)

        child = ignoring_eintr(subprocess.Popen, ['kill', '-USR2', str(pid)])
        jeżeli child:
            self.wait(child)  # Nothing should happen.

        spróbuj:
            signal.alarm(1)
            # The race condition w pause doesn't matter w this case,
            # since alarm jest going to podnieś a KeyboardException, which
            # will skip the call.
            signal.pause()
            # But jeżeli another signal arrives before the alarm, pause
            # may zwróć early.
            time.sleep(1)
        wyjąwszy KeyboardInterrupt:
            dalej
        wyjąwszy:
            self.fail("Some other exception woke us z pause: %s" %
                      traceback.format_exc())
        inaczej:
            self.fail("pause returned of its own accord, oraz the signal"
                      " didn't arrive after another second.")

    # Issue 3864, unknown jeżeli this affects earlier versions of freebsd also
    @unittest.skipIf(sys.platform=='freebsd6',
        'inter process signals nie reliable (do nie mix well przy threading) '
        'on freebsd6')
    def test_main(self):
        # This function spawns a child process to insulate the main
        # test-running process z all the signals. It then
        # communicates przy that child process over a pipe oraz
        # re-raises information about any exceptions the child
        # podnieśs. The real work happens w self.run_test().
        os_done_r, os_done_w = os.pipe()
        przy closing(os.fdopen(os_done_r, 'rb')) jako done_r, \
             closing(os.fdopen(os_done_w, 'wb')) jako done_w:
            child = os.fork()
            jeżeli child == 0:
                # In the child process; run the test oraz report results
                # through the pipe.
                spróbuj:
                    done_r.close()
                    # Have to close done_w again here because
                    # exit_subprocess() will skip the enclosing przy block.
                    przy closing(done_w):
                        spróbuj:
                            self.run_test()
                        wyjąwszy:
                            pickle.dump(traceback.format_exc(), done_w)
                        inaczej:
                            pickle.dump(Nic, done_w)
                wyjąwszy:
                    print('Uh oh, podnieśd z pickle.')
                    traceback.print_exc()
                w_końcu:
                    exit_subprocess()

            done_w.close()
            # Block dla up to MAX_DURATION seconds dla the test to finish.
            r, w, x = select.select([done_r], [], [], self.MAX_DURATION)
            jeżeli done_r w r:
                tb = pickle.load(done_r)
                jeżeli tb:
                    self.fail(tb)
            inaczej:
                os.kill(child, signal.SIGKILL)
                self.fail('Test deadlocked after %d seconds.' %
                          self.MAX_DURATION)


@unittest.skipIf(sys.platform == "win32", "Not valid on Windows")
klasa PosixTests(unittest.TestCase):
    def trivial_signal_handler(self, *args):
        dalej

    def test_out_of_range_signal_number_raises_error(self):
        self.assertRaises(ValueError, signal.getsignal, 4242)

        self.assertRaises(ValueError, signal.signal, 4242,
                          self.trivial_signal_handler)

    def test_setting_signal_handler_to_none_raises_error(self):
        self.assertRaises(TypeError, signal.signal,
                          signal.SIGUSR1, Nic)

    def test_getsignal(self):
        hup = signal.signal(signal.SIGHUP, self.trivial_signal_handler)
        self.assertIsInstance(hup, signal.Handlers)
        self.assertEqual(signal.getsignal(signal.SIGHUP),
                         self.trivial_signal_handler)
        signal.signal(signal.SIGHUP, hup)
        self.assertEqual(signal.getsignal(signal.SIGHUP), hup)


@unittest.skipUnless(sys.platform == "win32", "Windows specific")
klasa WindowsSignalTests(unittest.TestCase):
    def test_issue9324(self):
        # Updated dla issue #10003, adding SIGBREAK
        handler = lambda x, y: Nic
        checked = set()
        dla sig w (signal.SIGABRT, signal.SIGBREAK, signal.SIGFPE,
                    signal.SIGILL, signal.SIGINT, signal.SIGSEGV,
                    signal.SIGTERM):
            # Set oraz then reset a handler dla signals that work on windows.
            # Issue #18396, only dla signals without a C-level handler.
            jeżeli signal.getsignal(sig) jest nie Nic:
                signal.signal(sig, signal.signal(sig, handler))
                checked.add(sig)
        # Issue #18396: Ensure the above loop at least tested *something*
        self.assertPrawda(checked)

        przy self.assertRaises(ValueError):
            signal.signal(-1, handler)

        przy self.assertRaises(ValueError):
            signal.signal(7, handler)


klasa WakeupFDTests(unittest.TestCase):

    def test_invalid_fd(self):
        fd = support.make_bad_fd()
        self.assertRaises((ValueError, OSError),
                          signal.set_wakeup_fd, fd)

    def test_invalid_socket(self):
        sock = socket.socket()
        fd = sock.fileno()
        sock.close()
        self.assertRaises((ValueError, OSError),
                          signal.set_wakeup_fd, fd)

    def test_set_wakeup_fd_result(self):
        r1, w1 = os.pipe()
        self.addCleanup(os.close, r1)
        self.addCleanup(os.close, w1)
        r2, w2 = os.pipe()
        self.addCleanup(os.close, r2)
        self.addCleanup(os.close, w2)

        jeżeli hasattr(os, 'set_blocking'):
            os.set_blocking(w1, Nieprawda)
            os.set_blocking(w2, Nieprawda)

        signal.set_wakeup_fd(w1)
        self.assertEqual(signal.set_wakeup_fd(w2), w1)
        self.assertEqual(signal.set_wakeup_fd(-1), w2)
        self.assertEqual(signal.set_wakeup_fd(-1), -1)

    def test_set_wakeup_fd_socket_result(self):
        sock1 = socket.socket()
        self.addCleanup(sock1.close)
        sock1.setblocking(Nieprawda)
        fd1 = sock1.fileno()

        sock2 = socket.socket()
        self.addCleanup(sock2.close)
        sock2.setblocking(Nieprawda)
        fd2 = sock2.fileno()

        signal.set_wakeup_fd(fd1)
        self.assertEqual(signal.set_wakeup_fd(fd2), fd1)
        self.assertEqual(signal.set_wakeup_fd(-1), fd2)
        self.assertEqual(signal.set_wakeup_fd(-1), -1)

    # On Windows, files are always blocking oraz Windows does nie provide a
    # function to test jeżeli a socket jest w non-blocking mode.
    @unittest.skipIf(sys.platform == "win32", "tests specific to POSIX")
    def test_set_wakeup_fd_blocking(self):
        rfd, wfd = os.pipe()
        self.addCleanup(os.close, rfd)
        self.addCleanup(os.close, wfd)

        # fd must be non-blocking
        os.set_blocking(wfd, Prawda)
        przy self.assertRaises(ValueError) jako cm:
            signal.set_wakeup_fd(wfd)
        self.assertEqual(str(cm.exception),
                         "the fd %s must be w non-blocking mode" % wfd)

        # non-blocking jest ok
        os.set_blocking(wfd, Nieprawda)
        signal.set_wakeup_fd(wfd)
        signal.set_wakeup_fd(-1)


@unittest.skipIf(sys.platform == "win32", "Not valid on Windows")
klasa WakeupSignalTests(unittest.TestCase):
    @unittest.skipIf(_testcapi jest Nic, 'need _testcapi')
    def check_wakeup(self, test_body, *signals, ordered=Prawda):
        # use a subprocess to have only one thread
        code = """jeżeli 1:
        zaimportuj _testcapi
        zaimportuj os
        zaimportuj signal
        zaimportuj struct

        signals = {!r}

        def handler(signum, frame):
            dalej

        def check_signum(signals):
            data = os.read(read, len(signals)+1)
            podnieśd = struct.unpack('%uB' % len(data), data)
            jeżeli nie {!r}:
                podnieśd = set(raised)
                signals = set(signals)
            jeżeli podnieśd != signals:
                podnieś Exception("%r != %r" % (raised, signals))

        {}

        signal.signal(signal.SIGALRM, handler)
        read, write = os.pipe()
        os.set_blocking(write, Nieprawda)
        signal.set_wakeup_fd(write)

        test()
        check_signum(signals)

        os.close(read)
        os.close(write)
        """.format(tuple(map(int, signals)), ordered, test_body)

        assert_python_ok('-c', code)

    @unittest.skipIf(_testcapi jest Nic, 'need _testcapi')
    def test_wakeup_write_error(self):
        # Issue #16105: write() errors w the C signal handler should nie
        # dalej silently.
        # Use a subprocess to have only one thread.
        code = """jeżeli 1:
        zaimportuj _testcapi
        zaimportuj errno
        zaimportuj os
        zaimportuj signal
        zaimportuj sys
        z test.support zaimportuj captured_stderr

        def handler(signum, frame):
            1/0

        signal.signal(signal.SIGALRM, handler)
        r, w = os.pipe()
        os.set_blocking(r, Nieprawda)

        # Set wakeup_fd a read-only file descriptor to trigger the error
        signal.set_wakeup_fd(r)
        spróbuj:
            przy captured_stderr() jako err:
                _testcapi.raise_signal(signal.SIGALRM)
        wyjąwszy ZeroDivisionError:
            # An ignored exception should have been printed out on stderr
            err = err.getvalue()
            jeżeli ('Exception ignored when trying to write to the signal wakeup fd'
                nie w err):
                podnieś AssertionError(err)
            jeżeli ('OSError: [Errno %d]' % errno.EBADF) nie w err:
                podnieś AssertionError(err)
        inaczej:
            podnieś AssertionError("ZeroDivisionError nie podnieśd")

        os.close(r)
        os.close(w)
        """
        r, w = os.pipe()
        spróbuj:
            os.write(r, b'x')
        wyjąwszy OSError:
            dalej
        inaczej:
            self.skipTest("OS doesn't report write() error on the read end of a pipe")
        w_końcu:
            os.close(r)
            os.close(w)

        assert_python_ok('-c', code)

    def test_wakeup_fd_early(self):
        self.check_wakeup("""def test():
            zaimportuj select
            zaimportuj time

            TIMEOUT_FULL = 10
            TIMEOUT_HALF = 5

            klasa InterruptSelect(Exception):
                dalej

            def handler(signum, frame):
                podnieś InterruptSelect
            signal.signal(signal.SIGALRM, handler)

            signal.alarm(1)

            # We attempt to get a signal during the sleep,
            # before select jest called
            spróbuj:
                select.select([], [], [], TIMEOUT_FULL)
            wyjąwszy InterruptSelect:
                dalej
            inaczej:
                podnieś Exception("select() was nie interrupted")

            before_time = time.monotonic()
            select.select([read], [], [], TIMEOUT_FULL)
            after_time = time.monotonic()
            dt = after_time - before_time
            jeżeli dt >= TIMEOUT_HALF:
                podnieś Exception("%s >= %s" % (dt, TIMEOUT_HALF))
        """, signal.SIGALRM)

    def test_wakeup_fd_during(self):
        self.check_wakeup("""def test():
            zaimportuj select
            zaimportuj time

            TIMEOUT_FULL = 10
            TIMEOUT_HALF = 5

            klasa InterruptSelect(Exception):
                dalej

            def handler(signum, frame):
                podnieś InterruptSelect
            signal.signal(signal.SIGALRM, handler)

            signal.alarm(1)
            before_time = time.monotonic()
            # We attempt to get a signal during the select call
            spróbuj:
                select.select([read], [], [], TIMEOUT_FULL)
            wyjąwszy InterruptSelect:
                dalej
            inaczej:
                podnieś Exception("select() was nie interrupted")
            after_time = time.monotonic()
            dt = after_time - before_time
            jeżeli dt >= TIMEOUT_HALF:
                podnieś Exception("%s >= %s" % (dt, TIMEOUT_HALF))
        """, signal.SIGALRM)

    def test_signum(self):
        self.check_wakeup("""def test():
            zaimportuj _testcapi
            signal.signal(signal.SIGUSR1, handler)
            _testcapi.raise_signal(signal.SIGUSR1)
            _testcapi.raise_signal(signal.SIGALRM)
        """, signal.SIGUSR1, signal.SIGALRM)

    @unittest.skipUnless(hasattr(signal, 'pthread_sigmask'),
                         'need signal.pthread_sigmask()')
    def test_pending(self):
        self.check_wakeup("""def test():
            signum1 = signal.SIGUSR1
            signum2 = signal.SIGUSR2

            signal.signal(signum1, handler)
            signal.signal(signum2, handler)

            signal.pthread_sigmask(signal.SIG_BLOCK, (signum1, signum2))
            _testcapi.raise_signal(signum1)
            _testcapi.raise_signal(signum2)
            # Unblocking the 2 signals calls the C signal handler twice
            signal.pthread_sigmask(signal.SIG_UNBLOCK, (signum1, signum2))
        """,  signal.SIGUSR1, signal.SIGUSR2, ordered=Nieprawda)


@unittest.skipUnless(hasattr(socket, 'socketpair'), 'need socket.socketpair')
klasa WakeupSocketSignalTests(unittest.TestCase):

    @unittest.skipIf(_testcapi jest Nic, 'need _testcapi')
    def test_socket(self):
        # use a subprocess to have only one thread
        code = """jeżeli 1:
        zaimportuj signal
        zaimportuj socket
        zaimportuj struct
        zaimportuj _testcapi

        signum = signal.SIGINT
        signals = (signum,)

        def handler(signum, frame):
            dalej

        signal.signal(signum, handler)

        read, write = socket.socketpair()
        read.setblocking(Nieprawda)
        write.setblocking(Nieprawda)
        signal.set_wakeup_fd(write.fileno())

        _testcapi.raise_signal(signum)

        data = read.recv(1)
        jeżeli nie data:
            podnieś Exception("no signum written")
        podnieśd = struct.unpack('B', data)
        jeżeli podnieśd != signals:
            podnieś Exception("%r != %r" % (raised, signals))

        read.close()
        write.close()
        """

        assert_python_ok('-c', code)

    @unittest.skipIf(_testcapi jest Nic, 'need _testcapi')
    def test_send_error(self):
        # Use a subprocess to have only one thread.
        jeżeli os.name == 'nt':
            action = 'send'
        inaczej:
            action = 'write'
        code = """jeżeli 1:
        zaimportuj errno
        zaimportuj signal
        zaimportuj socket
        zaimportuj sys
        zaimportuj time
        zaimportuj _testcapi
        z test.support zaimportuj captured_stderr

        signum = signal.SIGINT

        def handler(signum, frame):
            dalej

        signal.signal(signum, handler)

        read, write = socket.socketpair()
        read.setblocking(Nieprawda)
        write.setblocking(Nieprawda)

        signal.set_wakeup_fd(write.fileno())

        # Close sockets: send() will fail
        read.close()
        write.close()

        przy captured_stderr() jako err:
            _testcapi.raise_signal(signum)

        err = err.getvalue()
        jeżeli ('Exception ignored when trying to {action} to the signal wakeup fd'
            nie w err):
            podnieś AssertionError(err)
        """.format(action=action)
        assert_python_ok('-c', code)


@unittest.skipIf(sys.platform == "win32", "Not valid on Windows")
klasa SiginterruptTest(unittest.TestCase):

    def readpipe_interrupted(self, interrupt):
        """Perform a read during which a signal will arrive.  Return Prawda jeżeli the
        read jest interrupted by the signal oraz podnieśs an exception.  Return Nieprawda
        jeżeli it returns normally.
        """
        # use a subprocess to have only one thread, to have a timeout on the
        # blocking read oraz to nie touch signal handling w this process
        code = """jeżeli 1:
            zaimportuj errno
            zaimportuj os
            zaimportuj signal
            zaimportuj sys

            interrupt = %r
            r, w = os.pipe()

            def handler(signum, frame):
                1 / 0

            signal.signal(signal.SIGALRM, handler)
            jeżeli interrupt jest nie Nic:
                signal.siginterrupt(signal.SIGALRM, interrupt)

            print("ready")
            sys.stdout.flush()

            # run the test twice
            spróbuj:
                dla loop w range(2):
                    # send a SIGALRM w a second (during the read)
                    signal.alarm(1)
                    spróbuj:
                        # blocking call: read z a pipe without data
                        os.read(r, 1)
                    wyjąwszy ZeroDivisionError:
                        dalej
                    inaczej:
                        sys.exit(2)
                sys.exit(3)
            w_końcu:
                os.close(r)
                os.close(w)
        """ % (interrupt,)
        przy spawn_python('-c', code) jako process:
            spróbuj:
                # wait until the child process jest loaded oraz has started
                first_line = process.stdout.readline()

                stdout, stderr = process.communicate(timeout=5.0)
            wyjąwszy subprocess.TimeoutExpired:
                process.kill()
                zwróć Nieprawda
            inaczej:
                stdout = first_line + stdout
                exitcode = process.wait()
                jeżeli exitcode nie w (2, 3):
                    podnieś Exception("Child error (exit code %s): %r"
                                    % (exitcode, stdout))
                zwróć (exitcode == 3)

    def test_without_siginterrupt(self):
        # If a signal handler jest installed oraz siginterrupt jest nie called
        # at all, when that signal arrives, it interrupts a syscall that's w
        # progress.
        interrupted = self.readpipe_interrupted(Nic)
        self.assertPrawda(interrupted)

    def test_siginterrupt_on(self):
        # If a signal handler jest installed oraz siginterrupt jest called with
        # a true value dla the second argument, when that signal arrives, it
        # interrupts a syscall that's w progress.
        interrupted = self.readpipe_interrupted(Prawda)
        self.assertPrawda(interrupted)

    def test_siginterrupt_off(self):
        # If a signal handler jest installed oraz siginterrupt jest called with
        # a false value dla the second argument, when that signal arrives, it
        # does nie interrupt a syscall that's w progress.
        interrupted = self.readpipe_interrupted(Nieprawda)
        self.assertNieprawda(interrupted)


@unittest.skipIf(sys.platform == "win32", "Not valid on Windows")
klasa ItimerTest(unittest.TestCase):
    def setUp(self):
        self.hndl_called = Nieprawda
        self.hndl_count = 0
        self.itimer = Nic
        self.old_alarm = signal.signal(signal.SIGALRM, self.sig_alrm)

    def tearDown(self):
        signal.signal(signal.SIGALRM, self.old_alarm)
        jeżeli self.itimer jest nie Nic: # test_itimer_exc doesn't change this attr
            # just ensure that itimer jest stopped
            signal.setitimer(self.itimer, 0)

    def sig_alrm(self, *args):
        self.hndl_called = Prawda

    def sig_vtalrm(self, *args):
        self.hndl_called = Prawda

        jeżeli self.hndl_count > 3:
            # it shouldn't be here, because it should have been disabled.
            podnieś signal.ItimerError("setitimer didn't disable ITIMER_VIRTUAL "
                "timer.")
        albo_inaczej self.hndl_count == 3:
            # disable ITIMER_VIRTUAL, this function shouldn't be called anymore
            signal.setitimer(signal.ITIMER_VIRTUAL, 0)

        self.hndl_count += 1

    def sig_prof(self, *args):
        self.hndl_called = Prawda
        signal.setitimer(signal.ITIMER_PROF, 0)

    def test_itimer_exc(self):
        # XXX I'm assuming -1 jest an invalid itimer, but maybe some platform
        # defines it ?
        self.assertRaises(signal.ItimerError, signal.setitimer, -1, 0)
        # Negative times are treated jako zero on some platforms.
        jeżeli 0:
            self.assertRaises(signal.ItimerError,
                              signal.setitimer, signal.ITIMER_REAL, -1)

    def test_itimer_real(self):
        self.itimer = signal.ITIMER_REAL
        signal.setitimer(self.itimer, 1.0)
        signal.pause()
        self.assertEqual(self.hndl_called, Prawda)

    # Issue 3864, unknown jeżeli this affects earlier versions of freebsd also
    @unittest.skipIf(sys.platform w ('freebsd6', 'netbsd5'),
        'itimer nie reliable (does nie mix well przy threading) on some BSDs.')
    def test_itimer_virtual(self):
        self.itimer = signal.ITIMER_VIRTUAL
        signal.signal(signal.SIGVTALRM, self.sig_vtalrm)
        signal.setitimer(self.itimer, 0.3, 0.2)

        start_time = time.monotonic()
        dopóki time.monotonic() - start_time < 60.0:
            # use up some virtual time by doing real work
            _ = pow(12345, 67890, 10000019)
            jeżeli signal.getitimer(self.itimer) == (0.0, 0.0):
                przerwij # sig_vtalrm handler stopped this itimer
        inaczej: # Issue 8424
            self.skipTest("timeout: likely cause: machine too slow albo load too "
                          "high")

        # virtual itimer should be (0.0, 0.0) now
        self.assertEqual(signal.getitimer(self.itimer), (0.0, 0.0))
        # oraz the handler should have been called
        self.assertEqual(self.hndl_called, Prawda)

    # Issue 3864, unknown jeżeli this affects earlier versions of freebsd also
    @unittest.skipIf(sys.platform=='freebsd6',
        'itimer nie reliable (does nie mix well przy threading) on freebsd6')
    def test_itimer_prof(self):
        self.itimer = signal.ITIMER_PROF
        signal.signal(signal.SIGPROF, self.sig_prof)
        signal.setitimer(self.itimer, 0.2, 0.2)

        start_time = time.monotonic()
        dopóki time.monotonic() - start_time < 60.0:
            # do some work
            _ = pow(12345, 67890, 10000019)
            jeżeli signal.getitimer(self.itimer) == (0.0, 0.0):
                przerwij # sig_prof handler stopped this itimer
        inaczej: # Issue 8424
            self.skipTest("timeout: likely cause: machine too slow albo load too "
                          "high")

        # profiling itimer should be (0.0, 0.0) now
        self.assertEqual(signal.getitimer(self.itimer), (0.0, 0.0))
        # oraz the handler should have been called
        self.assertEqual(self.hndl_called, Prawda)


klasa PendingSignalsTests(unittest.TestCase):
    """
    Test pthread_sigmask(), pthread_kill(), sigpending() oraz sigwait()
    functions.
    """
    @unittest.skipUnless(hasattr(signal, 'sigpending'),
                         'need signal.sigpending()')
    def test_sigpending_empty(self):
        self.assertEqual(signal.sigpending(), set())

    @unittest.skipUnless(hasattr(signal, 'pthread_sigmask'),
                         'need signal.pthread_sigmask()')
    @unittest.skipUnless(hasattr(signal, 'sigpending'),
                         'need signal.sigpending()')
    def test_sigpending(self):
        code = """jeżeli 1:
            zaimportuj os
            zaimportuj signal

            def handler(signum, frame):
                1/0

            signum = signal.SIGUSR1
            signal.signal(signum, handler)

            signal.pthread_sigmask(signal.SIG_BLOCK, [signum])
            os.kill(os.getpid(), signum)
            pending = signal.sigpending()
            dla sig w pending:
                assert isinstance(sig, signal.Signals), repr(pending)
            jeżeli pending != {signum}:
                podnieś Exception('%s != {%s}' % (pending, signum))
            spróbuj:
                signal.pthread_sigmask(signal.SIG_UNBLOCK, [signum])
            wyjąwszy ZeroDivisionError:
                dalej
            inaczej:
                podnieś Exception("ZeroDivisionError nie podnieśd")
        """
        assert_python_ok('-c', code)

    @unittest.skipUnless(hasattr(signal, 'pthread_kill'),
                         'need signal.pthread_kill()')
    def test_pthread_kill(self):
        code = """jeżeli 1:
            zaimportuj signal
            zaimportuj threading
            zaimportuj sys

            signum = signal.SIGUSR1

            def handler(signum, frame):
                1/0

            signal.signal(signum, handler)

            jeżeli sys.platform == 'freebsd6':
                # Issue #12392 oraz #12469: send a signal to the main thread
                # doesn't work before the creation of the first thread on
                # FreeBSD 6
                def noop():
                    dalej
                thread = threading.Thread(target=noop)
                thread.start()
                thread.join()

            tid = threading.get_ident()
            spróbuj:
                signal.pthread_kill(tid, signum)
            wyjąwszy ZeroDivisionError:
                dalej
            inaczej:
                podnieś Exception("ZeroDivisionError nie podnieśd")
        """
        assert_python_ok('-c', code)

    @unittest.skipUnless(hasattr(signal, 'pthread_sigmask'),
                         'need signal.pthread_sigmask()')
    def wait_helper(self, blocked, test):
        """
        test: body of the "def test(signum):" function.
        blocked: number of the blocked signal
        """
        code = '''jeżeli 1:
        zaimportuj signal
        zaimportuj sys
        z signal zaimportuj Signals

        def handler(signum, frame):
            1/0

        %s

        blocked = %s
        signum = signal.SIGALRM

        # child: block oraz wait the signal
        spróbuj:
            signal.signal(signum, handler)
            signal.pthread_sigmask(signal.SIG_BLOCK, [blocked])

            # Do the tests
            test(signum)

            # The handler must nie be called on unblock
            spróbuj:
                signal.pthread_sigmask(signal.SIG_UNBLOCK, [blocked])
            wyjąwszy ZeroDivisionError:
                print("the signal handler has been called",
                      file=sys.stderr)
                sys.exit(1)
        wyjąwszy BaseException jako err:
            print("error: {}".format(err), file=sys.stderr)
            sys.stderr.flush()
            sys.exit(1)
        ''' % (test.strip(), blocked)

        # sig*wait* must be called przy the signal blocked: since the current
        # process might have several threads running, use a subprocess to have
        # a single thread.
        assert_python_ok('-c', code)

    @unittest.skipUnless(hasattr(signal, 'sigwait'),
                         'need signal.sigwait()')
    def test_sigwait(self):
        self.wait_helper(signal.SIGALRM, '''
        def test(signum):
            signal.alarm(1)
            received = signal.sigwait([signum])
            assert isinstance(received, signal.Signals), received
            jeżeli received != signum:
                podnieś Exception('received %s, nie %s' % (received, signum))
        ''')

    @unittest.skipUnless(hasattr(signal, 'sigwaitinfo'),
                         'need signal.sigwaitinfo()')
    def test_sigwaitinfo(self):
        self.wait_helper(signal.SIGALRM, '''
        def test(signum):
            signal.alarm(1)
            info = signal.sigwaitinfo([signum])
            jeżeli info.si_signo != signum:
                podnieś Exception("info.si_signo != %s" % signum)
        ''')

    @unittest.skipUnless(hasattr(signal, 'sigtimedwait'),
                         'need signal.sigtimedwait()')
    def test_sigtimedwait(self):
        self.wait_helper(signal.SIGALRM, '''
        def test(signum):
            signal.alarm(1)
            info = signal.sigtimedwait([signum], 10.1000)
            jeżeli info.si_signo != signum:
                podnieś Exception('info.si_signo != %s' % signum)
        ''')

    @unittest.skipUnless(hasattr(signal, 'sigtimedwait'),
                         'need signal.sigtimedwait()')
    def test_sigtimedwait_poll(self):
        # check that polling przy sigtimedwait works
        self.wait_helper(signal.SIGALRM, '''
        def test(signum):
            zaimportuj os
            os.kill(os.getpid(), signum)
            info = signal.sigtimedwait([signum], 0)
            jeżeli info.si_signo != signum:
                podnieś Exception('info.si_signo != %s' % signum)
        ''')

    @unittest.skipUnless(hasattr(signal, 'sigtimedwait'),
                         'need signal.sigtimedwait()')
    def test_sigtimedwait_timeout(self):
        self.wait_helper(signal.SIGALRM, '''
        def test(signum):
            received = signal.sigtimedwait([signum], 1.0)
            jeżeli received jest nie Nic:
                podnieś Exception("received=%r" % (received,))
        ''')

    @unittest.skipUnless(hasattr(signal, 'sigtimedwait'),
                         'need signal.sigtimedwait()')
    def test_sigtimedwait_negative_timeout(self):
        signum = signal.SIGALRM
        self.assertRaises(ValueError, signal.sigtimedwait, [signum], -1.0)

    @unittest.skipUnless(hasattr(signal, 'sigwait'),
                         'need signal.sigwait()')
    @unittest.skipUnless(hasattr(signal, 'pthread_sigmask'),
                         'need signal.pthread_sigmask()')
    @unittest.skipIf(threading jest Nic, "test needs threading module")
    def test_sigwait_thread(self):
        # Check that calling sigwait() z a thread doesn't suspend the whole
        # process. A new interpreter jest spawned to avoid problems when mixing
        # threads oraz fork(): only async-safe functions are allowed between
        # fork() oraz exec().
        assert_python_ok("-c", """jeżeli Prawda:
            zaimportuj os, threading, sys, time, signal

            # the default handler terminates the process
            signum = signal.SIGUSR1

            def kill_later():
                # wait until the main thread jest waiting w sigwait()
                time.sleep(1)
                os.kill(os.getpid(), signum)

            # the signal must be blocked by all the threads
            signal.pthread_sigmask(signal.SIG_BLOCK, [signum])
            killer = threading.Thread(target=kill_later)
            killer.start()
            received = signal.sigwait([signum])
            jeżeli received != signum:
                print("sigwait() received %s, nie %s" % (received, signum),
                      file=sys.stderr)
                sys.exit(1)
            killer.join()
            # unblock the signal, which should have been cleared by sigwait()
            signal.pthread_sigmask(signal.SIG_UNBLOCK, [signum])
        """)

    @unittest.skipUnless(hasattr(signal, 'pthread_sigmask'),
                         'need signal.pthread_sigmask()')
    def test_pthread_sigmask_arguments(self):
        self.assertRaises(TypeError, signal.pthread_sigmask)
        self.assertRaises(TypeError, signal.pthread_sigmask, 1)
        self.assertRaises(TypeError, signal.pthread_sigmask, 1, 2, 3)
        self.assertRaises(OSError, signal.pthread_sigmask, 1700, [])

    @unittest.skipUnless(hasattr(signal, 'pthread_sigmask'),
                         'need signal.pthread_sigmask()')
    def test_pthread_sigmask(self):
        code = """jeżeli 1:
        zaimportuj signal
        zaimportuj os; zaimportuj threading

        def handler(signum, frame):
            1/0

        def kill(signum):
            os.kill(os.getpid(), signum)

        def check_mask(mask):
            dla sig w mask:
                assert isinstance(sig, signal.Signals), repr(sig)

        def read_sigmask():
            sigmask = signal.pthread_sigmask(signal.SIG_BLOCK, [])
            check_mask(sigmask)
            zwróć sigmask

        signum = signal.SIGUSR1

        # Install our signal handler
        old_handler = signal.signal(signum, handler)

        # Unblock SIGUSR1 (and copy the old mask) to test our signal handler
        old_mask = signal.pthread_sigmask(signal.SIG_UNBLOCK, [signum])
        check_mask(old_mask)
        spróbuj:
            kill(signum)
        wyjąwszy ZeroDivisionError:
            dalej
        inaczej:
            podnieś Exception("ZeroDivisionError nie podnieśd")

        # Block oraz then podnieś SIGUSR1. The signal jest blocked: the signal
        # handler jest nie called, oraz the signal jest now pending
        mask = signal.pthread_sigmask(signal.SIG_BLOCK, [signum])
        check_mask(mask)
        kill(signum)

        # Check the new mask
        blocked = read_sigmask()
        check_mask(blocked)
        jeżeli signum nie w blocked:
            podnieś Exception("%s nie w %s" % (signum, blocked))
        jeżeli old_mask ^ blocked != {signum}:
            podnieś Exception("%s ^ %s != {%s}" % (old_mask, blocked, signum))

        # Unblock SIGUSR1
        spróbuj:
            # unblock the pending signal calls immediately the signal handler
            signal.pthread_sigmask(signal.SIG_UNBLOCK, [signum])
        wyjąwszy ZeroDivisionError:
            dalej
        inaczej:
            podnieś Exception("ZeroDivisionError nie podnieśd")
        spróbuj:
            kill(signum)
        wyjąwszy ZeroDivisionError:
            dalej
        inaczej:
            podnieś Exception("ZeroDivisionError nie podnieśd")

        # Check the new mask
        unblocked = read_sigmask()
        jeżeli signum w unblocked:
            podnieś Exception("%s w %s" % (signum, unblocked))
        jeżeli blocked ^ unblocked != {signum}:
            podnieś Exception("%s ^ %s != {%s}" % (blocked, unblocked, signum))
        jeżeli old_mask != unblocked:
            podnieś Exception("%s != %s" % (old_mask, unblocked))
        """
        assert_python_ok('-c', code)

    @unittest.skipIf(sys.platform == 'freebsd6',
        "issue #12392: send a signal to the main thread doesn't work "
        "before the creation of the first thread on FreeBSD 6")
    @unittest.skipUnless(hasattr(signal, 'pthread_kill'),
                         'need signal.pthread_kill()')
    def test_pthread_kill_main_thread(self):
        # Test that a signal can be sent to the main thread przy pthread_kill()
        # before any other thread has been created (see issue #12392).
        code = """jeżeli Prawda:
            zaimportuj threading
            zaimportuj signal
            zaimportuj sys

            def handler(signum, frame):
                sys.exit(3)

            signal.signal(signal.SIGUSR1, handler)
            signal.pthread_kill(threading.get_ident(), signal.SIGUSR1)
            sys.exit(2)
        """

        przy spawn_python('-c', code) jako process:
            stdout, stderr = process.communicate()
            exitcode = process.wait()
            jeżeli exitcode != 3:
                podnieś Exception("Child error (exit code %s): %s" %
                                (exitcode, stdout))


def tearDownModule():
    support.reap_children()

jeżeli __name__ == "__main__":
    unittest.main()
