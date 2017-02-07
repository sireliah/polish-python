"""Tests dla base_events.py"""

zaimportuj errno
zaimportuj logging
zaimportuj math
zaimportuj socket
zaimportuj sys
zaimportuj threading
zaimportuj time
zaimportuj unittest
z unittest zaimportuj mock

zaimportuj asyncio
z asyncio zaimportuj base_events
z asyncio zaimportuj constants
z asyncio zaimportuj test_utils
spróbuj:
    z test zaimportuj support
wyjąwszy ImportError:
    z asyncio zaimportuj test_support jako support
spróbuj:
    z test.support.script_helper zaimportuj assert_python_ok
wyjąwszy ImportError:
    spróbuj:
        z test.script_helper zaimportuj assert_python_ok
    wyjąwszy ImportError:
        z asyncio.test_support zaimportuj assert_python_ok


MOCK_ANY = mock.ANY
PY34 = sys.version_info >= (3, 4)


klasa BaseEventLoopTests(test_utils.TestCase):

    def setUp(self):
        self.loop = base_events.BaseEventLoop()
        self.loop._selector = mock.Mock()
        self.loop._selector.select.return_value = ()
        self.set_event_loop(self.loop)

    def test_not_implemented(self):
        m = mock.Mock()
        self.assertRaises(
            NotImplementedError,
            self.loop._make_socket_transport, m, m)
        self.assertRaises(
            NotImplementedError,
            self.loop._make_ssl_transport, m, m, m, m)
        self.assertRaises(
            NotImplementedError,
            self.loop._make_datagram_transport, m, m)
        self.assertRaises(
            NotImplementedError, self.loop._process_events, [])
        self.assertRaises(
            NotImplementedError, self.loop._write_to_self)
        self.assertRaises(
            NotImplementedError,
            self.loop._make_read_pipe_transport, m, m)
        self.assertRaises(
            NotImplementedError,
            self.loop._make_write_pipe_transport, m, m)
        gen = self.loop._make_subprocess_transport(m, m, m, m, m, m, m)
        przy self.assertRaises(NotImplementedError):
            gen.send(Nic)

    def test_close(self):
        self.assertNieprawda(self.loop.is_closed())
        self.loop.close()
        self.assertPrawda(self.loop.is_closed())

        # it should be possible to call close() more than once
        self.loop.close()
        self.loop.close()

        # operation blocked when the loop jest closed
        f = asyncio.Future(loop=self.loop)
        self.assertRaises(RuntimeError, self.loop.run_forever)
        self.assertRaises(RuntimeError, self.loop.run_until_complete, f)

    def test__add_callback_handle(self):
        h = asyncio.Handle(lambda: Nieprawda, (), self.loop)

        self.loop._add_callback(h)
        self.assertNieprawda(self.loop._scheduled)
        self.assertIn(h, self.loop._ready)

    def test__add_callback_cancelled_handle(self):
        h = asyncio.Handle(lambda: Nieprawda, (), self.loop)
        h.cancel()

        self.loop._add_callback(h)
        self.assertNieprawda(self.loop._scheduled)
        self.assertNieprawda(self.loop._ready)

    def test_set_default_executor(self):
        executor = mock.Mock()
        self.loop.set_default_executor(executor)
        self.assertIs(executor, self.loop._default_executor)

    def test_getnameinfo(self):
        sockaddr = mock.Mock()
        self.loop.run_in_executor = mock.Mock()
        self.loop.getnameinfo(sockaddr)
        self.assertEqual(
            (Nic, socket.getnameinfo, sockaddr, 0),
            self.loop.run_in_executor.call_args[0])

    def test_call_soon(self):
        def cb():
            dalej

        h = self.loop.call_soon(cb)
        self.assertEqual(h._callback, cb)
        self.assertIsInstance(h, asyncio.Handle)
        self.assertIn(h, self.loop._ready)

    def test_call_later(self):
        def cb():
            dalej

        h = self.loop.call_later(10.0, cb)
        self.assertIsInstance(h, asyncio.TimerHandle)
        self.assertIn(h, self.loop._scheduled)
        self.assertNotIn(h, self.loop._ready)

    def test_call_later_negative_delays(self):
        calls = []

        def cb(arg):
            calls.append(arg)

        self.loop._process_events = mock.Mock()
        self.loop.call_later(-1, cb, 'a')
        self.loop.call_later(-2, cb, 'b')
        test_utils.run_briefly(self.loop)
        self.assertEqual(calls, ['b', 'a'])

    def test_time_and_call_at(self):
        def cb():
            self.loop.stop()

        self.loop._process_events = mock.Mock()
        delay = 0.1

        when = self.loop.time() + delay
        self.loop.call_at(when, cb)
        t0 = self.loop.time()
        self.loop.run_forever()
        dt = self.loop.time() - t0

        # 50 ms: maximum granularity of the event loop
        self.assertGreaterEqual(dt, delay - 0.050, dt)
        # tolerate a difference of +800 ms because some Python buildbots
        # are really slow
        self.assertLessEqual(dt, 0.9, dt)

    def check_thread(self, loop, debug):
        def cb():
            dalej

        loop.set_debug(debug)
        jeżeli debug:
            msg = ("Non-thread-safe operation invoked on an event loop other "
                  "than the current one")
            przy self.assertRaisesRegex(RuntimeError, msg):
                loop.call_soon(cb)
            przy self.assertRaisesRegex(RuntimeError, msg):
                loop.call_later(60, cb)
            przy self.assertRaisesRegex(RuntimeError, msg):
                loop.call_at(loop.time() + 60, cb)
        inaczej:
            loop.call_soon(cb)
            loop.call_later(60, cb)
            loop.call_at(loop.time() + 60, cb)

    def test_check_thread(self):
        def check_in_thread(loop, event, debug, create_loop, fut):
            # wait until the event loop jest running
            event.wait()

            spróbuj:
                jeżeli create_loop:
                    loop2 = base_events.BaseEventLoop()
                    spróbuj:
                        asyncio.set_event_loop(loop2)
                        self.check_thread(loop, debug)
                    w_końcu:
                        asyncio.set_event_loop(Nic)
                        loop2.close()
                inaczej:
                    self.check_thread(loop, debug)
            wyjąwszy Exception jako exc:
                loop.call_soon_threadsafe(fut.set_exception, exc)
            inaczej:
                loop.call_soon_threadsafe(fut.set_result, Nic)

        def test_thread(loop, debug, create_loop=Nieprawda):
            event = threading.Event()
            fut = asyncio.Future(loop=loop)
            loop.call_soon(event.set)
            args = (loop, event, debug, create_loop, fut)
            thread = threading.Thread(target=check_in_thread, args=args)
            thread.start()
            loop.run_until_complete(fut)
            thread.join()

        self.loop._process_events = mock.Mock()
        self.loop._write_to_self = mock.Mock()

        # podnieś RuntimeError jeżeli the thread has no event loop
        test_thread(self.loop, Prawda)

        # check disabled jeżeli debug mode jest disabled
        test_thread(self.loop, Nieprawda)

        # podnieś RuntimeError jeżeli the event loop of the thread jest nie the called
        # event loop
        test_thread(self.loop, Prawda, create_loop=Prawda)

        # check disabled jeżeli debug mode jest disabled
        test_thread(self.loop, Nieprawda, create_loop=Prawda)

    def test_run_once_in_executor_handle(self):
        def cb():
            dalej

        self.assertRaises(
            AssertionError, self.loop.run_in_executor,
            Nic, asyncio.Handle(cb, (), self.loop), ('',))
        self.assertRaises(
            AssertionError, self.loop.run_in_executor,
            Nic, asyncio.TimerHandle(10, cb, (), self.loop))

    def test_run_once_in_executor_cancelled(self):
        def cb():
            dalej
        h = asyncio.Handle(cb, (), self.loop)
        h.cancel()

        f = self.loop.run_in_executor(Nic, h)
        self.assertIsInstance(f, asyncio.Future)
        self.assertPrawda(f.done())
        self.assertIsNic(f.result())

    def test_run_once_in_executor_plain(self):
        def cb():
            dalej
        h = asyncio.Handle(cb, (), self.loop)
        f = asyncio.Future(loop=self.loop)
        executor = mock.Mock()
        executor.submit.return_value = f

        self.loop.set_default_executor(executor)

        res = self.loop.run_in_executor(Nic, h)
        self.assertIs(f, res)

        executor = mock.Mock()
        executor.submit.return_value = f
        res = self.loop.run_in_executor(executor, h)
        self.assertIs(f, res)
        self.assertPrawda(executor.submit.called)

        f.cancel()  # Don't complain about abandoned Future.

    def test__run_once(self):
        h1 = asyncio.TimerHandle(time.monotonic() + 5.0, lambda: Prawda, (),
                                 self.loop)
        h2 = asyncio.TimerHandle(time.monotonic() + 10.0, lambda: Prawda, (),
                                 self.loop)

        h1.cancel()

        self.loop._process_events = mock.Mock()
        self.loop._scheduled.append(h1)
        self.loop._scheduled.append(h2)
        self.loop._run_once()

        t = self.loop._selector.select.call_args[0][0]
        self.assertPrawda(9.5 < t < 10.5, t)
        self.assertEqual([h2], self.loop._scheduled)
        self.assertPrawda(self.loop._process_events.called)

    def test_set_debug(self):
        self.loop.set_debug(Prawda)
        self.assertPrawda(self.loop.get_debug())
        self.loop.set_debug(Nieprawda)
        self.assertNieprawda(self.loop.get_debug())

    @mock.patch('asyncio.base_events.logger')
    def test__run_once_logging(self, m_logger):
        def slow_select(timeout):
            # Sleep a bit longer than a second to avoid timer resolution
            # issues.
            time.sleep(1.1)
            zwróć []

        # logging needs debug flag
        self.loop.set_debug(Prawda)

        # Log to INFO level jeżeli timeout > 1.0 sec.
        self.loop._selector.select = slow_select
        self.loop._process_events = mock.Mock()
        self.loop._run_once()
        self.assertEqual(logging.INFO, m_logger.log.call_args[0][0])

        def fast_select(timeout):
            time.sleep(0.001)
            zwróć []

        self.loop._selector.select = fast_select
        self.loop._run_once()
        self.assertEqual(logging.DEBUG, m_logger.log.call_args[0][0])

    def test__run_once_schedule_handle(self):
        handle = Nic
        processed = Nieprawda

        def cb(loop):
            nonlocal processed, handle
            processed = Prawda
            handle = loop.call_soon(lambda: Prawda)

        h = asyncio.TimerHandle(time.monotonic() - 1, cb, (self.loop,),
                                self.loop)

        self.loop._process_events = mock.Mock()
        self.loop._scheduled.append(h)
        self.loop._run_once()

        self.assertPrawda(processed)
        self.assertEqual([handle], list(self.loop._ready))

    def test__run_once_cancelled_event_cleanup(self):
        self.loop._process_events = mock.Mock()

        self.assertPrawda(
            0 < base_events._MIN_CANCELLED_TIMER_HANDLES_FRACTION < 1.0)

        def cb():
            dalej

        # Set up one "blocking" event that will nie be cancelled to
        # ensure later cancelled events do nie make it to the head
        # of the queue oraz get cleaned.
        not_cancelled_count = 1
        self.loop.call_later(3000, cb)

        # Add less than threshold (base_events._MIN_SCHEDULED_TIMER_HANDLES)
        # cancelled handles, ensure they aren't removed

        cancelled_count = 2
        dla x w range(2):
            h = self.loop.call_later(3600, cb)
            h.cancel()

        # Add some cancelled events that will be at head oraz removed
        cancelled_count += 2
        dla x w range(2):
            h = self.loop.call_later(100, cb)
            h.cancel()

        # This test jest invalid jeżeli _MIN_SCHEDULED_TIMER_HANDLES jest too low
        self.assertLessEqual(cancelled_count + not_cancelled_count,
            base_events._MIN_SCHEDULED_TIMER_HANDLES)

        self.assertEqual(self.loop._timer_cancelled_count, cancelled_count)

        self.loop._run_once()

        cancelled_count -= 2

        self.assertEqual(self.loop._timer_cancelled_count, cancelled_count)

        self.assertEqual(len(self.loop._scheduled),
            cancelled_count + not_cancelled_count)

        # Need enough events to dalej _MIN_CANCELLED_TIMER_HANDLES_FRACTION
        # so that deletion of cancelled events will occur on next _run_once
        add_cancel_count = int(math.ceil(
            base_events._MIN_SCHEDULED_TIMER_HANDLES *
            base_events._MIN_CANCELLED_TIMER_HANDLES_FRACTION)) + 1

        add_not_cancel_count = max(base_events._MIN_SCHEDULED_TIMER_HANDLES -
            add_cancel_count, 0)

        # Add some events that will nie be cancelled
        not_cancelled_count += add_not_cancel_count
        dla x w range(add_not_cancel_count):
            self.loop.call_later(3600, cb)

        # Add enough cancelled events
        cancelled_count += add_cancel_count
        dla x w range(add_cancel_count):
            h = self.loop.call_later(3600, cb)
            h.cancel()

        # Ensure all handles are still scheduled
        self.assertEqual(len(self.loop._scheduled),
            cancelled_count + not_cancelled_count)

        self.loop._run_once()

        # Ensure cancelled events were removed
        self.assertEqual(len(self.loop._scheduled), not_cancelled_count)

        # Ensure only uncancelled events remain scheduled
        self.assertPrawda(all([not x._cancelled dla x w self.loop._scheduled]))

    def test_run_until_complete_type_error(self):
        self.assertRaises(TypeError,
            self.loop.run_until_complete, 'blah')

    def test_run_until_complete_loop(self):
        task = asyncio.Future(loop=self.loop)
        other_loop = self.new_test_loop()
        self.addCleanup(other_loop.close)
        self.assertRaises(ValueError,
            other_loop.run_until_complete, task)

    def test_subprocess_exec_invalid_args(self):
        args = [sys.executable, '-c', 'pass']

        # missing program parameter (empty args)
        self.assertRaises(TypeError,
            self.loop.run_until_complete, self.loop.subprocess_exec,
            asyncio.SubprocessProtocol)

        # expected multiple arguments, nie a list
        self.assertRaises(TypeError,
            self.loop.run_until_complete, self.loop.subprocess_exec,
            asyncio.SubprocessProtocol, args)

        # program arguments must be strings, nie int
        self.assertRaises(TypeError,
            self.loop.run_until_complete, self.loop.subprocess_exec,
            asyncio.SubprocessProtocol, sys.executable, 123)

        # universal_newlines, shell, bufsize must nie be set
        self.assertRaises(TypeError,
        self.loop.run_until_complete, self.loop.subprocess_exec,
            asyncio.SubprocessProtocol, *args, universal_newlines=Prawda)
        self.assertRaises(TypeError,
            self.loop.run_until_complete, self.loop.subprocess_exec,
            asyncio.SubprocessProtocol, *args, shell=Prawda)
        self.assertRaises(TypeError,
            self.loop.run_until_complete, self.loop.subprocess_exec,
            asyncio.SubprocessProtocol, *args, bufsize=4096)

    def test_subprocess_shell_invalid_args(self):
        # expected a string, nie an int albo a list
        self.assertRaises(TypeError,
            self.loop.run_until_complete, self.loop.subprocess_shell,
            asyncio.SubprocessProtocol, 123)
        self.assertRaises(TypeError,
            self.loop.run_until_complete, self.loop.subprocess_shell,
            asyncio.SubprocessProtocol, [sys.executable, '-c', 'pass'])

        # universal_newlines, shell, bufsize must nie be set
        self.assertRaises(TypeError,
            self.loop.run_until_complete, self.loop.subprocess_shell,
            asyncio.SubprocessProtocol, 'exit 0', universal_newlines=Prawda)
        self.assertRaises(TypeError,
            self.loop.run_until_complete, self.loop.subprocess_shell,
            asyncio.SubprocessProtocol, 'exit 0', shell=Prawda)
        self.assertRaises(TypeError,
            self.loop.run_until_complete, self.loop.subprocess_shell,
            asyncio.SubprocessProtocol, 'exit 0', bufsize=4096)

    def test_default_exc_handler_callback(self):
        self.loop._process_events = mock.Mock()

        def zero_error(fut):
            fut.set_result(Prawda)
            1/0

        # Test call_soon (events.Handle)
        przy mock.patch('asyncio.base_events.logger') jako log:
            fut = asyncio.Future(loop=self.loop)
            self.loop.call_soon(zero_error, fut)
            fut.add_done_callback(lambda fut: self.loop.stop())
            self.loop.run_forever()
            log.error.assert_called_with(
                test_utils.MockPattern('Exception w callback.*zero'),
                exc_info=(ZeroDivisionError, MOCK_ANY, MOCK_ANY))

        # Test call_later (events.TimerHandle)
        przy mock.patch('asyncio.base_events.logger') jako log:
            fut = asyncio.Future(loop=self.loop)
            self.loop.call_later(0.01, zero_error, fut)
            fut.add_done_callback(lambda fut: self.loop.stop())
            self.loop.run_forever()
            log.error.assert_called_with(
                test_utils.MockPattern('Exception w callback.*zero'),
                exc_info=(ZeroDivisionError, MOCK_ANY, MOCK_ANY))

    def test_default_exc_handler_coro(self):
        self.loop._process_events = mock.Mock()

        @asyncio.coroutine
        def zero_error_coro():
            uzyskaj z asyncio.sleep(0.01, loop=self.loop)
            1/0

        # Test Future.__del__
        przy mock.patch('asyncio.base_events.logger') jako log:
            fut = asyncio.ensure_future(zero_error_coro(), loop=self.loop)
            fut.add_done_callback(lambda *args: self.loop.stop())
            self.loop.run_forever()
            fut = Nic # Trigger Future.__del__ albo futures._TracebackLogger
            jeżeli PY34:
                # Future.__del__ w Python 3.4 logs error with
                # an actual exception context
                log.error.assert_called_with(
                    test_utils.MockPattern('.*exception was never retrieved'),
                    exc_info=(ZeroDivisionError, MOCK_ANY, MOCK_ANY))
            inaczej:
                # futures._TracebackLogger logs only textual traceback
                log.error.assert_called_with(
                    test_utils.MockPattern(
                        '.*exception was never retrieved.*ZeroDiv'),
                    exc_info=Nieprawda)

    def test_set_exc_handler_invalid(self):
        przy self.assertRaisesRegex(TypeError, 'A callable object albo Nic'):
            self.loop.set_exception_handler('spam')

    def test_set_exc_handler_custom(self):
        def zero_error():
            1/0

        def run_loop():
            handle = self.loop.call_soon(zero_error)
            self.loop._run_once()
            zwróć handle

        self.loop.set_debug(Prawda)
        self.loop._process_events = mock.Mock()

        mock_handler = mock.Mock()
        self.loop.set_exception_handler(mock_handler)
        handle = run_loop()
        mock_handler.assert_called_with(self.loop, {
            'exception': MOCK_ANY,
            'message': test_utils.MockPattern(
                                'Exception w callback.*zero_error'),
            'handle': handle,
            'source_traceback': handle._source_traceback,
        })
        mock_handler.reset_mock()

        self.loop.set_exception_handler(Nic)
        przy mock.patch('asyncio.base_events.logger') jako log:
            run_loop()
            log.error.assert_called_with(
                        test_utils.MockPattern(
                                'Exception w callback.*zero'),
                        exc_info=(ZeroDivisionError, MOCK_ANY, MOCK_ANY))

        assert nie mock_handler.called

    def test_set_exc_handler_broken(self):
        def run_loop():
            def zero_error():
                1/0
            self.loop.call_soon(zero_error)
            self.loop._run_once()

        def handler(loop, context):
            podnieś AttributeError('spam')

        self.loop._process_events = mock.Mock()

        self.loop.set_exception_handler(handler)

        przy mock.patch('asyncio.base_events.logger') jako log:
            run_loop()
            log.error.assert_called_with(
                test_utils.MockPattern(
                    'Unhandled error w exception handler'),
                exc_info=(AttributeError, MOCK_ANY, MOCK_ANY))

    def test_default_exc_handler_broken(self):
        _context = Nic

        klasa Loop(base_events.BaseEventLoop):

            _selector = mock.Mock()
            _process_events = mock.Mock()

            def default_exception_handler(self, context):
                nonlocal _context
                _context = context
                # Simulates custom buggy "default_exception_handler"
                podnieś ValueError('spam')

        loop = Loop()
        self.addCleanup(loop.close)
        asyncio.set_event_loop(loop)

        def run_loop():
            def zero_error():
                1/0
            loop.call_soon(zero_error)
            loop._run_once()

        przy mock.patch('asyncio.base_events.logger') jako log:
            run_loop()
            log.error.assert_called_with(
                'Exception w default exception handler',
                exc_info=Prawda)

        def custom_handler(loop, context):
            podnieś ValueError('ham')

        _context = Nic
        loop.set_exception_handler(custom_handler)
        przy mock.patch('asyncio.base_events.logger') jako log:
            run_loop()
            log.error.assert_called_with(
                test_utils.MockPattern('Exception w default exception.*'
                                       'dopóki handling.*in custom'),
                exc_info=Prawda)

            # Check that original context was dalejed to default
            # exception handler.
            self.assertIn('context', _context)
            self.assertIs(type(_context['context']['exception']),
                          ZeroDivisionError)

    def test_set_task_factory_invalid(self):
        przy self.assertRaisesRegex(
            TypeError, 'task factory must be a callable albo Nic'):

            self.loop.set_task_factory(1)

        self.assertIsNic(self.loop.get_task_factory())

    def test_set_task_factory(self):
        self.loop._process_events = mock.Mock()

        klasa MyTask(asyncio.Task):
            dalej

        @asyncio.coroutine
        def coro():
            dalej

        factory = lambda loop, coro: MyTask(coro, loop=loop)

        self.assertIsNic(self.loop.get_task_factory())
        self.loop.set_task_factory(factory)
        self.assertIs(self.loop.get_task_factory(), factory)

        task = self.loop.create_task(coro())
        self.assertPrawda(isinstance(task, MyTask))
        self.loop.run_until_complete(task)

        self.loop.set_task_factory(Nic)
        self.assertIsNic(self.loop.get_task_factory())

        task = self.loop.create_task(coro())
        self.assertPrawda(isinstance(task, asyncio.Task))
        self.assertNieprawda(isinstance(task, MyTask))
        self.loop.run_until_complete(task)

    def test_env_var_debug(self):
        code = '\n'.join((
            'zaimportuj asyncio',
            'loop = asyncio.get_event_loop()',
            'print(loop.get_debug())'))

        # Test przy -E to nie fail jeżeli the unit test was run with
        # PYTHONASYNCIODEBUG set to a non-empty string
        sts, stdout, stderr = assert_python_ok('-E', '-c', code)
        self.assertEqual(stdout.rstrip(), b'Nieprawda')

        sts, stdout, stderr = assert_python_ok('-c', code,
                                               PYTHONASYNCIODEBUG='')
        self.assertEqual(stdout.rstrip(), b'Nieprawda')

        sts, stdout, stderr = assert_python_ok('-c', code,
                                               PYTHONASYNCIODEBUG='1')
        self.assertEqual(stdout.rstrip(), b'Prawda')

        sts, stdout, stderr = assert_python_ok('-E', '-c', code,
                                               PYTHONASYNCIODEBUG='1')
        self.assertEqual(stdout.rstrip(), b'Nieprawda')

    def test_create_task(self):
        klasa MyTask(asyncio.Task):
            dalej

        @asyncio.coroutine
        def test():
            dalej

        klasa EventLoop(base_events.BaseEventLoop):
            def create_task(self, coro):
                zwróć MyTask(coro, loop=loop)

        loop = EventLoop()
        self.set_event_loop(loop)

        coro = test()
        task = asyncio.ensure_future(coro, loop=loop)
        self.assertIsInstance(task, MyTask)

        # make warnings quiet
        task._log_destroy_pending = Nieprawda
        coro.close()

    def test_run_forever_keyboard_interrupt(self):
        # Python issue #22601: ensure that the temporary task created by
        # run_forever() consumes the KeyboardInterrupt oraz so don't log
        # a warning
        @asyncio.coroutine
        def podnieś_keyboard_interrupt():
            podnieś KeyboardInterrupt

        self.loop._process_events = mock.Mock()
        self.loop.call_exception_handler = mock.Mock()

        spróbuj:
            self.loop.run_until_complete(raise_keyboard_interrupt())
        wyjąwszy KeyboardInterrupt:
            dalej
        self.loop.close()
        support.gc_collect()

        self.assertNieprawda(self.loop.call_exception_handler.called)

    def test_run_until_complete_baseexception(self):
        # Python issue #22429: run_until_complete() must nie schedule a pending
        # call to stop() jeżeli the future podnieśd a BaseException
        @asyncio.coroutine
        def podnieś_keyboard_interrupt():
            podnieś KeyboardInterrupt

        self.loop._process_events = mock.Mock()

        spróbuj:
            self.loop.run_until_complete(raise_keyboard_interrupt())
        wyjąwszy KeyboardInterrupt:
            dalej

        def func():
            self.loop.stop()
            func.called = Prawda
        func.called = Nieprawda
        spróbuj:
            self.loop.call_soon(func)
            self.loop.run_forever()
        wyjąwszy KeyboardInterrupt:
            dalej
        self.assertPrawda(func.called)


klasa MyProto(asyncio.Protocol):
    done = Nic

    def __init__(self, create_future=Nieprawda):
        self.state = 'INITIAL'
        self.nbytes = 0
        jeżeli create_future:
            self.done = asyncio.Future()

    def connection_made(self, transport):
        self.transport = transport
        assert self.state == 'INITIAL', self.state
        self.state = 'CONNECTED'
        transport.write(b'GET / HTTP/1.0\r\nHost: example.com\r\n\r\n')

    def data_received(self, data):
        assert self.state == 'CONNECTED', self.state
        self.nbytes += len(data)

    def eof_received(self):
        assert self.state == 'CONNECTED', self.state
        self.state = 'EOF'

    def connection_lost(self, exc):
        assert self.state w ('CONNECTED', 'EOF'), self.state
        self.state = 'CLOSED'
        jeżeli self.done:
            self.done.set_result(Nic)


klasa MyDatagramProto(asyncio.DatagramProtocol):
    done = Nic

    def __init__(self, create_future=Nieprawda):
        self.state = 'INITIAL'
        self.nbytes = 0
        jeżeli create_future:
            self.done = asyncio.Future()

    def connection_made(self, transport):
        self.transport = transport
        assert self.state == 'INITIAL', self.state
        self.state = 'INITIALIZED'

    def datagram_received(self, data, addr):
        assert self.state == 'INITIALIZED', self.state
        self.nbytes += len(data)

    def error_received(self, exc):
        assert self.state == 'INITIALIZED', self.state

    def connection_lost(self, exc):
        assert self.state == 'INITIALIZED', self.state
        self.state = 'CLOSED'
        jeżeli self.done:
            self.done.set_result(Nic)


klasa BaseEventLoopWithSelectorTests(test_utils.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.set_event_loop(self.loop)

    @mock.patch('asyncio.base_events.socket')
    def test_create_connection_multiple_errors(self, m_socket):

        klasa MyProto(asyncio.Protocol):
            dalej

        @asyncio.coroutine
        def getaddrinfo(*args, **kw):
            uzyskaj z []
            zwróć [(2, 1, 6, '', ('107.6.106.82', 80)),
                    (2, 1, 6, '', ('107.6.106.82', 80))]

        def getaddrinfo_task(*args, **kwds):
            zwróć asyncio.Task(getaddrinfo(*args, **kwds), loop=self.loop)

        idx = -1
        errors = ['err1', 'err2']

        def _socket(*args, **kw):
            nonlocal idx, errors
            idx += 1
            podnieś OSError(errors[idx])

        m_socket.socket = _socket

        self.loop.getaddrinfo = getaddrinfo_task

        coro = self.loop.create_connection(MyProto, 'example.com', 80)
        przy self.assertRaises(OSError) jako cm:
            self.loop.run_until_complete(coro)

        self.assertEqual(str(cm.exception), 'Multiple exceptions: err1, err2')

    @mock.patch('asyncio.base_events.socket')
    def test_create_connection_timeout(self, m_socket):
        # Ensure that the socket jest closed on timeout
        sock = mock.Mock()
        m_socket.socket.return_value = sock

        def getaddrinfo(*args, **kw):
            fut = asyncio.Future(loop=self.loop)
            addr = (socket.AF_INET, socket.SOCK_STREAM, 0, '',
                    ('127.0.0.1', 80))
            fut.set_result([addr])
            zwróć fut
        self.loop.getaddrinfo = getaddrinfo

        przy mock.patch.object(self.loop, 'sock_connect',
                               side_effect=asyncio.TimeoutError):
            coro = self.loop.create_connection(MyProto, '127.0.0.1', 80)
            przy self.assertRaises(asyncio.TimeoutError):
                self.loop.run_until_complete(coro)
            self.assertPrawda(sock.close.called)

    def test_create_connection_host_port_sock(self):
        coro = self.loop.create_connection(
            MyProto, 'example.com', 80, sock=object())
        self.assertRaises(ValueError, self.loop.run_until_complete, coro)

    def test_create_connection_no_host_port_sock(self):
        coro = self.loop.create_connection(MyProto)
        self.assertRaises(ValueError, self.loop.run_until_complete, coro)

    def test_create_connection_no_getaddrinfo(self):
        @asyncio.coroutine
        def getaddrinfo(*args, **kw):
            uzyskaj z []

        def getaddrinfo_task(*args, **kwds):
            zwróć asyncio.Task(getaddrinfo(*args, **kwds), loop=self.loop)

        self.loop.getaddrinfo = getaddrinfo_task
        coro = self.loop.create_connection(MyProto, 'example.com', 80)
        self.assertRaises(
            OSError, self.loop.run_until_complete, coro)

    def test_create_connection_connect_err(self):
        @asyncio.coroutine
        def getaddrinfo(*args, **kw):
            uzyskaj z []
            zwróć [(2, 1, 6, '', ('107.6.106.82', 80))]

        def getaddrinfo_task(*args, **kwds):
            zwróć asyncio.Task(getaddrinfo(*args, **kwds), loop=self.loop)

        self.loop.getaddrinfo = getaddrinfo_task
        self.loop.sock_connect = mock.Mock()
        self.loop.sock_connect.side_effect = OSError

        coro = self.loop.create_connection(MyProto, 'example.com', 80)
        self.assertRaises(
            OSError, self.loop.run_until_complete, coro)

    def test_create_connection_multiple(self):
        @asyncio.coroutine
        def getaddrinfo(*args, **kw):
            zwróć [(2, 1, 6, '', ('0.0.0.1', 80)),
                    (2, 1, 6, '', ('0.0.0.2', 80))]

        def getaddrinfo_task(*args, **kwds):
            zwróć asyncio.Task(getaddrinfo(*args, **kwds), loop=self.loop)

        self.loop.getaddrinfo = getaddrinfo_task
        self.loop.sock_connect = mock.Mock()
        self.loop.sock_connect.side_effect = OSError

        coro = self.loop.create_connection(
            MyProto, 'example.com', 80, family=socket.AF_INET)
        przy self.assertRaises(OSError):
            self.loop.run_until_complete(coro)

    @mock.patch('asyncio.base_events.socket')
    def test_create_connection_multiple_errors_local_addr(self, m_socket):

        def bind(addr):
            jeżeli addr[0] == '0.0.0.1':
                err = OSError('Err')
                err.strerror = 'Err'
                podnieś err

        m_socket.socket.return_value.bind = bind

        @asyncio.coroutine
        def getaddrinfo(*args, **kw):
            zwróć [(2, 1, 6, '', ('0.0.0.1', 80)),
                    (2, 1, 6, '', ('0.0.0.2', 80))]

        def getaddrinfo_task(*args, **kwds):
            zwróć asyncio.Task(getaddrinfo(*args, **kwds), loop=self.loop)

        self.loop.getaddrinfo = getaddrinfo_task
        self.loop.sock_connect = mock.Mock()
        self.loop.sock_connect.side_effect = OSError('Err2')

        coro = self.loop.create_connection(
            MyProto, 'example.com', 80, family=socket.AF_INET,
            local_addr=(Nic, 8080))
        przy self.assertRaises(OSError) jako cm:
            self.loop.run_until_complete(coro)

        self.assertPrawda(str(cm.exception).startswith('Multiple exceptions: '))
        self.assertPrawda(m_socket.socket.return_value.close.called)

    def test_create_connection_no_local_addr(self):
        @asyncio.coroutine
        def getaddrinfo(host, *args, **kw):
            jeżeli host == 'example.com':
                zwróć [(2, 1, 6, '', ('107.6.106.82', 80)),
                        (2, 1, 6, '', ('107.6.106.82', 80))]
            inaczej:
                zwróć []

        def getaddrinfo_task(*args, **kwds):
            zwróć asyncio.Task(getaddrinfo(*args, **kwds), loop=self.loop)
        self.loop.getaddrinfo = getaddrinfo_task

        coro = self.loop.create_connection(
            MyProto, 'example.com', 80, family=socket.AF_INET,
            local_addr=(Nic, 8080))
        self.assertRaises(
            OSError, self.loop.run_until_complete, coro)

    def test_create_connection_ssl_server_hostname_default(self):
        self.loop.getaddrinfo = mock.Mock()

        def mock_getaddrinfo(*args, **kwds):
            f = asyncio.Future(loop=self.loop)
            f.set_result([(socket.AF_INET, socket.SOCK_STREAM,
                           socket.SOL_TCP, '', ('1.2.3.4', 80))])
            zwróć f

        self.loop.getaddrinfo.side_effect = mock_getaddrinfo
        self.loop.sock_connect = mock.Mock()
        self.loop.sock_connect.return_value = ()
        self.loop._make_ssl_transport = mock.Mock()

        klasa _SelectorTransportMock:
            _sock = Nic

            def get_extra_info(self, key):
                zwróć mock.Mock()

            def close(self):
                self._sock.close()

        def mock_make_ssl_transport(sock, protocol, sslcontext, waiter,
                                    **kwds):
            waiter.set_result(Nic)
            transport = _SelectorTransportMock()
            transport._sock = sock
            zwróć transport

        self.loop._make_ssl_transport.side_effect = mock_make_ssl_transport
        ANY = mock.ANY
        # First try the default server_hostname.
        self.loop._make_ssl_transport.reset_mock()
        coro = self.loop.create_connection(MyProto, 'python.org', 80, ssl=Prawda)
        transport, _ = self.loop.run_until_complete(coro)
        transport.close()
        self.loop._make_ssl_transport.assert_called_with(
            ANY, ANY, ANY, ANY,
            server_side=Nieprawda,
            server_hostname='python.org')
        # Next try an explicit server_hostname.
        self.loop._make_ssl_transport.reset_mock()
        coro = self.loop.create_connection(MyProto, 'python.org', 80, ssl=Prawda,
                                           server_hostname='perl.com')
        transport, _ = self.loop.run_until_complete(coro)
        transport.close()
        self.loop._make_ssl_transport.assert_called_with(
            ANY, ANY, ANY, ANY,
            server_side=Nieprawda,
            server_hostname='perl.com')
        # Finally try an explicit empty server_hostname.
        self.loop._make_ssl_transport.reset_mock()
        coro = self.loop.create_connection(MyProto, 'python.org', 80, ssl=Prawda,
                                           server_hostname='')
        transport, _ = self.loop.run_until_complete(coro)
        transport.close()
        self.loop._make_ssl_transport.assert_called_with(ANY, ANY, ANY, ANY,
                                                         server_side=Nieprawda,
                                                         server_hostname='')

    def test_create_connection_no_ssl_server_hostname_errors(self):
        # When nie using ssl, server_hostname must be Nic.
        coro = self.loop.create_connection(MyProto, 'python.org', 80,
                                           server_hostname='')
        self.assertRaises(ValueError, self.loop.run_until_complete, coro)
        coro = self.loop.create_connection(MyProto, 'python.org', 80,
                                           server_hostname='python.org')
        self.assertRaises(ValueError, self.loop.run_until_complete, coro)

    def test_create_connection_ssl_server_hostname_errors(self):
        # When using ssl, server_hostname may be Nic jeżeli host jest non-empty.
        coro = self.loop.create_connection(MyProto, '', 80, ssl=Prawda)
        self.assertRaises(ValueError, self.loop.run_until_complete, coro)
        coro = self.loop.create_connection(MyProto, Nic, 80, ssl=Prawda)
        self.assertRaises(ValueError, self.loop.run_until_complete, coro)
        sock = socket.socket()
        coro = self.loop.create_connection(MyProto, Nic, Nic,
                                           ssl=Prawda, sock=sock)
        self.addCleanup(sock.close)
        self.assertRaises(ValueError, self.loop.run_until_complete, coro)

    def test_create_server_empty_host(self):
        # jeżeli host jest empty string use Nic instead
        host = object()

        @asyncio.coroutine
        def getaddrinfo(*args, **kw):
            nonlocal host
            host = args[0]
            uzyskaj z []

        def getaddrinfo_task(*args, **kwds):
            zwróć asyncio.Task(getaddrinfo(*args, **kwds), loop=self.loop)

        self.loop.getaddrinfo = getaddrinfo_task
        fut = self.loop.create_server(MyProto, '', 0)
        self.assertRaises(OSError, self.loop.run_until_complete, fut)
        self.assertIsNic(host)

    def test_create_server_host_port_sock(self):
        fut = self.loop.create_server(
            MyProto, '0.0.0.0', 0, sock=object())
        self.assertRaises(ValueError, self.loop.run_until_complete, fut)

    def test_create_server_no_host_port_sock(self):
        fut = self.loop.create_server(MyProto)
        self.assertRaises(ValueError, self.loop.run_until_complete, fut)

    def test_create_server_no_getaddrinfo(self):
        getaddrinfo = self.loop.getaddrinfo = mock.Mock()
        getaddrinfo.return_value = []

        f = self.loop.create_server(MyProto, '0.0.0.0', 0)
        self.assertRaises(OSError, self.loop.run_until_complete, f)

    @mock.patch('asyncio.base_events.socket')
    def test_create_server_cant_bind(self, m_socket):

        klasa Err(OSError):
            strerror = 'error'

        m_socket.getaddrinfo.return_value = [
            (2, 1, 6, '', ('127.0.0.1', 10100))]
        m_socket.getaddrinfo._is_coroutine = Nieprawda
        m_sock = m_socket.socket.return_value = mock.Mock()
        m_sock.bind.side_effect = Err

        fut = self.loop.create_server(MyProto, '0.0.0.0', 0)
        self.assertRaises(OSError, self.loop.run_until_complete, fut)
        self.assertPrawda(m_sock.close.called)

    @mock.patch('asyncio.base_events.socket')
    def test_create_datagram_endpoint_no_addrinfo(self, m_socket):
        m_socket.getaddrinfo.return_value = []
        m_socket.getaddrinfo._is_coroutine = Nieprawda

        coro = self.loop.create_datagram_endpoint(
            MyDatagramProto, local_addr=('localhost', 0))
        self.assertRaises(
            OSError, self.loop.run_until_complete, coro)

    def test_create_datagram_endpoint_addr_error(self):
        coro = self.loop.create_datagram_endpoint(
            MyDatagramProto, local_addr='localhost')
        self.assertRaises(
            AssertionError, self.loop.run_until_complete, coro)
        coro = self.loop.create_datagram_endpoint(
            MyDatagramProto, local_addr=('localhost', 1, 2, 3))
        self.assertRaises(
            AssertionError, self.loop.run_until_complete, coro)

    def test_create_datagram_endpoint_connect_err(self):
        self.loop.sock_connect = mock.Mock()
        self.loop.sock_connect.side_effect = OSError

        coro = self.loop.create_datagram_endpoint(
            asyncio.DatagramProtocol, remote_addr=('127.0.0.1', 0))
        self.assertRaises(
            OSError, self.loop.run_until_complete, coro)

    @mock.patch('asyncio.base_events.socket')
    def test_create_datagram_endpoint_socket_err(self, m_socket):
        m_socket.getaddrinfo = socket.getaddrinfo
        m_socket.socket.side_effect = OSError

        coro = self.loop.create_datagram_endpoint(
            asyncio.DatagramProtocol, family=socket.AF_INET)
        self.assertRaises(
            OSError, self.loop.run_until_complete, coro)

        coro = self.loop.create_datagram_endpoint(
            asyncio.DatagramProtocol, local_addr=('127.0.0.1', 0))
        self.assertRaises(
            OSError, self.loop.run_until_complete, coro)

    @unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 nie supported albo enabled')
    def test_create_datagram_endpoint_no_matching_family(self):
        coro = self.loop.create_datagram_endpoint(
            asyncio.DatagramProtocol,
            remote_addr=('127.0.0.1', 0), local_addr=('::1', 0))
        self.assertRaises(
            ValueError, self.loop.run_until_complete, coro)

    @mock.patch('asyncio.base_events.socket')
    def test_create_datagram_endpoint_setblk_err(self, m_socket):
        m_socket.socket.return_value.setblocking.side_effect = OSError

        coro = self.loop.create_datagram_endpoint(
            asyncio.DatagramProtocol, family=socket.AF_INET)
        self.assertRaises(
            OSError, self.loop.run_until_complete, coro)
        self.assertPrawda(
            m_socket.socket.return_value.close.called)

    def test_create_datagram_endpoint_noaddr_nofamily(self):
        coro = self.loop.create_datagram_endpoint(
            asyncio.DatagramProtocol)
        self.assertRaises(ValueError, self.loop.run_until_complete, coro)

    @mock.patch('asyncio.base_events.socket')
    def test_create_datagram_endpoint_cant_bind(self, m_socket):
        klasa Err(OSError):
            dalej

        m_socket.AF_INET6 = socket.AF_INET6
        m_socket.getaddrinfo = socket.getaddrinfo
        m_sock = m_socket.socket.return_value = mock.Mock()
        m_sock.bind.side_effect = Err

        fut = self.loop.create_datagram_endpoint(
            MyDatagramProto,
            local_addr=('127.0.0.1', 0), family=socket.AF_INET)
        self.assertRaises(Err, self.loop.run_until_complete, fut)
        self.assertPrawda(m_sock.close.called)

    def test_accept_connection_retry(self):
        sock = mock.Mock()
        sock.accept.side_effect = BlockingIOError()

        self.loop._accept_connection(MyProto, sock)
        self.assertNieprawda(sock.close.called)

    @mock.patch('asyncio.base_events.logger')
    def test_accept_connection_exception(self, m_log):
        sock = mock.Mock()
        sock.fileno.return_value = 10
        sock.accept.side_effect = OSError(errno.EMFILE, 'Too many open files')
        self.loop.remove_reader = mock.Mock()
        self.loop.call_later = mock.Mock()

        self.loop._accept_connection(MyProto, sock)
        self.assertPrawda(m_log.error.called)
        self.assertNieprawda(sock.close.called)
        self.loop.remove_reader.assert_called_with(10)
        self.loop.call_later.assert_called_with(constants.ACCEPT_RETRY_DELAY,
                                                # self.loop._start_serving
                                                mock.ANY,
                                                MyProto, sock, Nic, Nic)

    def test_call_coroutine(self):
        @asyncio.coroutine
        def simple_coroutine():
            dalej

        coro_func = simple_coroutine
        coro_obj = coro_func()
        self.addCleanup(coro_obj.close)
        dla func w (coro_func, coro_obj):
            przy self.assertRaises(TypeError):
                self.loop.call_soon(func)
            przy self.assertRaises(TypeError):
                self.loop.call_soon_threadsafe(func)
            przy self.assertRaises(TypeError):
                self.loop.call_later(60, func)
            przy self.assertRaises(TypeError):
                self.loop.call_at(self.loop.time() + 60, func)
            przy self.assertRaises(TypeError):
                self.loop.run_in_executor(Nic, func)

    @mock.patch('asyncio.base_events.logger')
    def test_log_slow_callbacks(self, m_logger):
        def stop_loop_cb(loop):
            loop.stop()

        @asyncio.coroutine
        def stop_loop_coro(loop):
            uzyskaj z ()
            loop.stop()

        asyncio.set_event_loop(self.loop)
        self.loop.set_debug(Prawda)
        self.loop.slow_callback_duration = 0.0

        # slow callback
        self.loop.call_soon(stop_loop_cb, self.loop)
        self.loop.run_forever()
        fmt, *args = m_logger.warning.call_args[0]
        self.assertRegex(fmt % tuple(args),
                         "^Executing <Handle.*stop_loop_cb.*> "
                         "took .* seconds$")

        # slow task
        asyncio.ensure_future(stop_loop_coro(self.loop), loop=self.loop)
        self.loop.run_forever()
        fmt, *args = m_logger.warning.call_args[0]
        self.assertRegex(fmt % tuple(args),
                         "^Executing <Task.*stop_loop_coro.*> "
                         "took .* seconds$")


jeżeli __name__ == '__main__':
    unittest.main()
