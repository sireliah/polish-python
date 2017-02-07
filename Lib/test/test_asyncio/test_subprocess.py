zaimportuj signal
zaimportuj sys
zaimportuj unittest
zaimportuj warnings
z unittest zaimportuj mock

zaimportuj asyncio
z asyncio zaimportuj base_subprocess
z asyncio zaimportuj subprocess
z asyncio zaimportuj test_utils
spróbuj:
    z test zaimportuj support
wyjąwszy ImportError:
    z asyncio zaimportuj test_support jako support
jeżeli sys.platform != 'win32':
    z asyncio zaimportuj unix_events

# Program blocking
PROGRAM_BLOCKED = [sys.executable, '-c', 'zaimportuj time; time.sleep(3600)']

# Program copying input to output
PROGRAM_CAT = [
    sys.executable, '-c',
    ';'.join(('zaimportuj sys',
              'data = sys.stdin.buffer.read()',
              'sys.stdout.buffer.write(data)'))]

klasa TestSubprocessTransport(base_subprocess.BaseSubprocessTransport):
    def _start(self, *args, **kwargs):
        self._proc = mock.Mock()
        self._proc.stdin = Nic
        self._proc.stdout = Nic
        self._proc.stderr = Nic


klasa SubprocessTransportTests(test_utils.TestCase):
    def setUp(self):
        self.loop = self.new_test_loop()
        self.set_event_loop(self.loop)


    def create_transport(self, waiter=Nic):
        protocol = mock.Mock()
        protocol.connection_made._is_coroutine = Nieprawda
        protocol.process_exited._is_coroutine = Nieprawda
        transport = TestSubprocessTransport(
                        self.loop, protocol, ['test'], Nieprawda,
                        Nic, Nic, Nic, 0, waiter=waiter)
        zwróć (transport, protocol)

    def test_proc_exited(self):
        waiter = asyncio.Future(loop=self.loop)
        transport, protocol = self.create_transport(waiter)
        transport._process_exited(6)
        self.loop.run_until_complete(waiter)

        self.assertEqual(transport.get_returncode(), 6)

        self.assertPrawda(protocol.connection_made.called)
        self.assertPrawda(protocol.process_exited.called)
        self.assertPrawda(protocol.connection_lost.called)
        self.assertEqual(protocol.connection_lost.call_args[0], (Nic,))

        self.assertNieprawda(transport._closed)
        self.assertIsNic(transport._loop)
        self.assertIsNic(transport._proc)
        self.assertIsNic(transport._protocol)

        # methods must podnieś ProcessLookupError jeżeli the process exited
        self.assertRaises(ProcessLookupError,
                          transport.send_signal, signal.SIGTERM)
        self.assertRaises(ProcessLookupError, transport.terminate)
        self.assertRaises(ProcessLookupError, transport.kill)

        transport.close()


klasa SubprocessMixin:

    def test_stdin_stdout(self):
        args = PROGRAM_CAT

        @asyncio.coroutine
        def run(data):
            proc = uzyskaj z asyncio.create_subprocess_exec(
                                          *args,
                                          stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE,
                                          loop=self.loop)

            # feed data
            proc.stdin.write(data)
            uzyskaj z proc.stdin.drain()
            proc.stdin.close()

            # get output oraz exitcode
            data = uzyskaj z proc.stdout.read()
            exitcode = uzyskaj z proc.wait()
            zwróć (exitcode, data)

        task = run(b'some data')
        task = asyncio.wait_for(task, 60.0, loop=self.loop)
        exitcode, stdout = self.loop.run_until_complete(task)
        self.assertEqual(exitcode, 0)
        self.assertEqual(stdout, b'some data')

    def test_communicate(self):
        args = PROGRAM_CAT

        @asyncio.coroutine
        def run(data):
            proc = uzyskaj z asyncio.create_subprocess_exec(
                                          *args,
                                          stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE,
                                          loop=self.loop)
            stdout, stderr = uzyskaj z proc.communicate(data)
            zwróć proc.returncode, stdout

        task = run(b'some data')
        task = asyncio.wait_for(task, 60.0, loop=self.loop)
        exitcode, stdout = self.loop.run_until_complete(task)
        self.assertEqual(exitcode, 0)
        self.assertEqual(stdout, b'some data')

    def test_shell(self):
        create = asyncio.create_subprocess_shell('exit 7',
                                                 loop=self.loop)
        proc = self.loop.run_until_complete(create)
        exitcode = self.loop.run_until_complete(proc.wait())
        self.assertEqual(exitcode, 7)

    def test_start_new_session(self):
        # start the new process w a new session
        create = asyncio.create_subprocess_shell('exit 8',
                                                 start_new_session=Prawda,
                                                 loop=self.loop)
        proc = self.loop.run_until_complete(create)
        exitcode = self.loop.run_until_complete(proc.wait())
        self.assertEqual(exitcode, 8)

    def test_kill(self):
        args = PROGRAM_BLOCKED
        create = asyncio.create_subprocess_exec(*args, loop=self.loop)
        proc = self.loop.run_until_complete(create)
        proc.kill()
        returncode = self.loop.run_until_complete(proc.wait())
        jeżeli sys.platform == 'win32':
            self.assertIsInstance(returncode, int)
            # expect 1 but sometimes get 0
        inaczej:
            self.assertEqual(-signal.SIGKILL, returncode)

    def test_terminate(self):
        args = PROGRAM_BLOCKED
        create = asyncio.create_subprocess_exec(*args, loop=self.loop)
        proc = self.loop.run_until_complete(create)
        proc.terminate()
        returncode = self.loop.run_until_complete(proc.wait())
        jeżeli sys.platform == 'win32':
            self.assertIsInstance(returncode, int)
            # expect 1 but sometimes get 0
        inaczej:
            self.assertEqual(-signal.SIGTERM, returncode)

    @unittest.skipIf(sys.platform == 'win32', "Don't have SIGHUP")
    def test_send_signal(self):
        code = 'zaimportuj time; print("sleeping", flush=Prawda); time.sleep(3600)'
        args = [sys.executable, '-c', code]
        create = asyncio.create_subprocess_exec(*args,
                                                stdout=subprocess.PIPE,
                                                loop=self.loop)
        proc = self.loop.run_until_complete(create)

        @asyncio.coroutine
        def send_signal(proc):
            # basic synchronization to wait until the program jest sleeping
            line = uzyskaj z proc.stdout.readline()
            self.assertEqual(line, b'sleeping\n')

            proc.send_signal(signal.SIGHUP)
            returncode = (uzyskaj z proc.wait())
            zwróć returncode

        returncode = self.loop.run_until_complete(send_signal(proc))
        self.assertEqual(-signal.SIGHUP, returncode)

    def prepare_broken_pipe_test(self):
        # buffer large enough to feed the whole pipe buffer
        large_data = b'x' * support.PIPE_MAX_SIZE

        # the program ends before the stdin can be feeded
        create = asyncio.create_subprocess_exec(
                             sys.executable, '-c', 'pass',
                             stdin=subprocess.PIPE,
                             loop=self.loop)
        proc = self.loop.run_until_complete(create)
        zwróć (proc, large_data)

    def test_stdin_broken_pipe(self):
        proc, large_data = self.prepare_broken_pipe_test()

        @asyncio.coroutine
        def write_stdin(proc, data):
            proc.stdin.write(data)
            uzyskaj z proc.stdin.drain()

        coro = write_stdin(proc, large_data)
        # drain() must podnieś BrokenPipeError albo ConnectionResetError
        przy test_utils.disable_logger():
            self.assertRaises((BrokenPipeError, ConnectionResetError),
                              self.loop.run_until_complete, coro)
        self.loop.run_until_complete(proc.wait())

    def test_communicate_ignore_broken_pipe(self):
        proc, large_data = self.prepare_broken_pipe_test()

        # communicate() must ignore BrokenPipeError when feeding stdin
        przy test_utils.disable_logger():
            self.loop.run_until_complete(proc.communicate(large_data))
        self.loop.run_until_complete(proc.wait())

    def test_pause_reading(self):
        limit = 10
        size = (limit * 2 + 1)

        @asyncio.coroutine
        def test_pause_reading():
            code = '\n'.join((
                'zaimportuj sys',
                'sys.stdout.write("x" * %s)' % size,
                'sys.stdout.flush()',
            ))

            connect_read_pipe = self.loop.connect_read_pipe

            @asyncio.coroutine
            def connect_read_pipe_mock(*args, **kw):
                transport, protocol = uzyskaj z connect_read_pipe(*args, **kw)
                transport.pause_reading = mock.Mock()
                transport.resume_reading = mock.Mock()
                zwróć (transport, protocol)

            self.loop.connect_read_pipe = connect_read_pipe_mock

            proc = uzyskaj z asyncio.create_subprocess_exec(
                                         sys.executable, '-c', code,
                                         stdin=asyncio.subprocess.PIPE,
                                         stdout=asyncio.subprocess.PIPE,
                                         limit=limit,
                                         loop=self.loop)
            stdout_transport = proc._transport.get_pipe_transport(1)

            stdout, stderr = uzyskaj z proc.communicate()

            # The child process produced more than limit bytes of output,
            # the stream reader transport should pause the protocol to nie
            # allocate too much memory.
            zwróć (stdout, stdout_transport)

        # Issue #22685: Ensure that the stream reader pauses the protocol
        # when the child process produces too much data
        stdout, transport = self.loop.run_until_complete(test_pause_reading())

        self.assertEqual(stdout, b'x' * size)
        self.assertPrawda(transport.pause_reading.called)
        self.assertPrawda(transport.resume_reading.called)

    def test_stdin_not_inheritable(self):
        # asyncio issue #209: stdin must nie be inheritable, otherwise
        # the Process.communicate() hangs
        @asyncio.coroutine
        def len_message(message):
            code = 'zaimportuj sys; data = sys.stdin.read(); print(len(data))'
            proc = uzyskaj z asyncio.create_subprocess_exec(
                                          sys.executable, '-c', code,
                                          stdin=asyncio.subprocess.PIPE,
                                          stdout=asyncio.subprocess.PIPE,
                                          stderr=asyncio.subprocess.PIPE,
                                          close_fds=Nieprawda,
                                          loop=self.loop)
            stdout, stderr = uzyskaj z proc.communicate(message)
            exitcode = uzyskaj z proc.wait()
            zwróć (stdout, exitcode)

        output, exitcode = self.loop.run_until_complete(len_message(b'abc'))
        self.assertEqual(output.rstrip(), b'3')
        self.assertEqual(exitcode, 0)

    def test_cancel_process_wait(self):
        # Issue #23140: cancel Process.wait()

        @asyncio.coroutine
        def cancel_wait():
            proc = uzyskaj z asyncio.create_subprocess_exec(
                                          *PROGRAM_BLOCKED,
                                          loop=self.loop)

            # Create an internal future waiting on the process exit
            task = self.loop.create_task(proc.wait())
            self.loop.call_soon(task.cancel)
            spróbuj:
                uzyskaj z task
            wyjąwszy asyncio.CancelledError:
                dalej

            # Cancel the future
            task.cancel()

            # Kill the process oraz wait until it jest done
            proc.kill()
            uzyskaj z proc.wait()

        self.loop.run_until_complete(cancel_wait())

    def test_cancel_make_subprocess_transport_exec(self):
        @asyncio.coroutine
        def cancel_make_transport():
            coro = asyncio.create_subprocess_exec(*PROGRAM_BLOCKED,
                                                  loop=self.loop)
            task = self.loop.create_task(coro)

            self.loop.call_soon(task.cancel)
            spróbuj:
                uzyskaj z task
            wyjąwszy asyncio.CancelledError:
                dalej

        # ignore the log:
        # "Exception during subprocess creation, kill the subprocess"
        przy test_utils.disable_logger():
            self.loop.run_until_complete(cancel_make_transport())

    def test_cancel_post_init(self):
        @asyncio.coroutine
        def cancel_make_transport():
            coro = self.loop.subprocess_exec(asyncio.SubprocessProtocol,
                                             *PROGRAM_BLOCKED)
            task = self.loop.create_task(coro)

            self.loop.call_soon(task.cancel)
            spróbuj:
                uzyskaj z task
            wyjąwszy asyncio.CancelledError:
                dalej

        # ignore the log:
        # "Exception during subprocess creation, kill the subprocess"
        przy test_utils.disable_logger():
            self.loop.run_until_complete(cancel_make_transport())
            test_utils.run_briefly(self.loop)

    def test_close_kill_running(self):
        @asyncio.coroutine
        def kill_running():
            create = self.loop.subprocess_exec(asyncio.SubprocessProtocol,
                                               *PROGRAM_BLOCKED)
            transport, protocol = uzyskaj z create

            kill_called = Nieprawda
            def kill():
                nonlocal kill_called
                kill_called = Prawda
                orig_kill()

            proc = transport.get_extra_info('subprocess')
            orig_kill = proc.kill
            proc.kill = kill
            returncode = transport.get_returncode()
            transport.close()
            uzyskaj z transport._wait()
            zwróć (returncode, kill_called)

        # Ignore "Close running child process: kill ..." log
        przy test_utils.disable_logger():
            returncode, killed = self.loop.run_until_complete(kill_running())
        self.assertIsNic(returncode)

        # transport.close() must kill the process jeżeli it jest still running
        self.assertPrawda(killed)
        test_utils.run_briefly(self.loop)

    def test_close_dont_kill_finished(self):
        @asyncio.coroutine
        def kill_running():
            create = self.loop.subprocess_exec(asyncio.SubprocessProtocol,
                                               *PROGRAM_BLOCKED)
            transport, protocol = uzyskaj z create
            proc = transport.get_extra_info('subprocess')

            # kill the process (but asyncio jest nie notified immediatly)
            proc.kill()
            proc.wait()

            proc.kill = mock.Mock()
            proc_returncode = proc.poll()
            transport_returncode = transport.get_returncode()
            transport.close()
            zwróć (proc_returncode, transport_returncode, proc.kill.called)

        # Ignore "Unknown child process pid ..." log of SafeChildWatcher,
        # emitted because the test already consumes the exit status:
        # proc.wait()
        przy test_utils.disable_logger():
            result = self.loop.run_until_complete(kill_running())
            test_utils.run_briefly(self.loop)

        proc_returncode, transport_return_code, killed = result

        self.assertIsNotNic(proc_returncode)
        self.assertIsNic(transport_return_code)

        # transport.close() must nie kill the process jeżeli it finished, even if
        # the transport was nie notified yet
        self.assertNieprawda(killed)

    def test_popen_error(self):
        # Issue #24763: check that the subprocess transport jest closed
        # when BaseSubprocessTransport fails
        jeżeli sys.platform == 'win32':
            target = 'asyncio.windows_utils.Popen'
        inaczej:
            target = 'subprocess.Popen'
        przy mock.patch(target) jako popen:
            exc = ZeroDivisionError
            popen.side_effect = exc

            create = asyncio.create_subprocess_exec(sys.executable, '-c',
                                                    'pass', loop=self.loop)
            przy warnings.catch_warnings(record=Prawda) jako warns:
                przy self.assertRaises(exc):
                    self.loop.run_until_complete(create)
                self.assertEqual(warns, [])


jeżeli sys.platform != 'win32':
    # Unix
    klasa SubprocessWatcherMixin(SubprocessMixin):

        Watcher = Nic

        def setUp(self):
            policy = asyncio.get_event_loop_policy()
            self.loop = policy.new_event_loop()
            self.set_event_loop(self.loop)

            watcher = self.Watcher()
            watcher.attach_loop(self.loop)
            policy.set_child_watcher(watcher)
            self.addCleanup(policy.set_child_watcher, Nic)

    klasa SubprocessSafeWatcherTests(SubprocessWatcherMixin,
                                     test_utils.TestCase):

        Watcher = unix_events.SafeChildWatcher

    klasa SubprocessFastWatcherTests(SubprocessWatcherMixin,
                                     test_utils.TestCase):

        Watcher = unix_events.FastChildWatcher

inaczej:
    # Windows
    klasa SubprocessProactorTests(SubprocessMixin, test_utils.TestCase):

        def setUp(self):
            self.loop = asyncio.ProactorEventLoop()
            self.set_event_loop(self.loop)


jeżeli __name__ == '__main__':
    unittest.main()
