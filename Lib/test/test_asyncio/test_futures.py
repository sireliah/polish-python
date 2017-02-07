"""Tests dla futures.py."""

zaimportuj concurrent.futures
zaimportuj re
zaimportuj sys
zaimportuj threading
zaimportuj unittest
z unittest zaimportuj mock

zaimportuj asyncio
z asyncio zaimportuj test_utils
spróbuj:
    z test zaimportuj support
wyjąwszy ImportError:
    z asyncio zaimportuj test_support jako support


def _fakefunc(f):
    zwróć f

def first_cb():
    dalej

def last_cb():
    dalej


klasa FutureTests(test_utils.TestCase):

    def setUp(self):
        self.loop = self.new_test_loop()
        self.addCleanup(self.loop.close)

    def test_initial_state(self):
        f = asyncio.Future(loop=self.loop)
        self.assertNieprawda(f.cancelled())
        self.assertNieprawda(f.done())
        f.cancel()
        self.assertPrawda(f.cancelled())

    def test_init_constructor_default_loop(self):
        asyncio.set_event_loop(self.loop)
        f = asyncio.Future()
        self.assertIs(f._loop, self.loop)

    def test_constructor_positional(self):
        # Make sure Future doesn't accept a positional argument
        self.assertRaises(TypeError, asyncio.Future, 42)

    def test_cancel(self):
        f = asyncio.Future(loop=self.loop)
        self.assertPrawda(f.cancel())
        self.assertPrawda(f.cancelled())
        self.assertPrawda(f.done())
        self.assertRaises(asyncio.CancelledError, f.result)
        self.assertRaises(asyncio.CancelledError, f.exception)
        self.assertRaises(asyncio.InvalidStateError, f.set_result, Nic)
        self.assertRaises(asyncio.InvalidStateError, f.set_exception, Nic)
        self.assertNieprawda(f.cancel())

    def test_result(self):
        f = asyncio.Future(loop=self.loop)
        self.assertRaises(asyncio.InvalidStateError, f.result)

        f.set_result(42)
        self.assertNieprawda(f.cancelled())
        self.assertPrawda(f.done())
        self.assertEqual(f.result(), 42)
        self.assertEqual(f.exception(), Nic)
        self.assertRaises(asyncio.InvalidStateError, f.set_result, Nic)
        self.assertRaises(asyncio.InvalidStateError, f.set_exception, Nic)
        self.assertNieprawda(f.cancel())

    def test_exception(self):
        exc = RuntimeError()
        f = asyncio.Future(loop=self.loop)
        self.assertRaises(asyncio.InvalidStateError, f.exception)

        f.set_exception(exc)
        self.assertNieprawda(f.cancelled())
        self.assertPrawda(f.done())
        self.assertRaises(RuntimeError, f.result)
        self.assertEqual(f.exception(), exc)
        self.assertRaises(asyncio.InvalidStateError, f.set_result, Nic)
        self.assertRaises(asyncio.InvalidStateError, f.set_exception, Nic)
        self.assertNieprawda(f.cancel())

    def test_exception_class(self):
        f = asyncio.Future(loop=self.loop)
        f.set_exception(RuntimeError)
        self.assertIsInstance(f.exception(), RuntimeError)

    def test_uzyskaj_from_twice(self):
        f = asyncio.Future(loop=self.loop)

        def fixture():
            uzyskaj 'A'
            x = uzyskaj z f
            uzyskaj 'B', x
            y = uzyskaj z f
            uzyskaj 'C', y

        g = fixture()
        self.assertEqual(next(g), 'A')  # uzyskaj 'A'.
        self.assertEqual(next(g), f)  # First uzyskaj z f.
        f.set_result(42)
        self.assertEqual(next(g), ('B', 42))  # uzyskaj 'B', x.
        # The second "uzyskaj z f" does nie uzyskaj f.
        self.assertEqual(next(g), ('C', 42))  # uzyskaj 'C', y.

    def test_future_repr(self):
        self.loop.set_debug(Prawda)
        f_pending_debug = asyncio.Future(loop=self.loop)
        frame = f_pending_debug._source_traceback[-1]
        self.assertEqual(repr(f_pending_debug),
                         '<Future pending created at %s:%s>'
                         % (frame[0], frame[1]))
        f_pending_debug.cancel()

        self.loop.set_debug(Nieprawda)
        f_pending = asyncio.Future(loop=self.loop)
        self.assertEqual(repr(f_pending), '<Future pending>')
        f_pending.cancel()

        f_cancelled = asyncio.Future(loop=self.loop)
        f_cancelled.cancel()
        self.assertEqual(repr(f_cancelled), '<Future cancelled>')

        f_result = asyncio.Future(loop=self.loop)
        f_result.set_result(4)
        self.assertEqual(repr(f_result), '<Future finished result=4>')
        self.assertEqual(f_result.result(), 4)

        exc = RuntimeError()
        f_exception = asyncio.Future(loop=self.loop)
        f_exception.set_exception(exc)
        self.assertEqual(repr(f_exception),
                         '<Future finished exception=RuntimeError()>')
        self.assertIs(f_exception.exception(), exc)

        def func_repr(func):
            filename, lineno = test_utils.get_function_source(func)
            text = '%s() at %s:%s' % (func.__qualname__, filename, lineno)
            zwróć re.escape(text)

        f_one_callbacks = asyncio.Future(loop=self.loop)
        f_one_callbacks.add_done_callback(_fakefunc)
        fake_repr = func_repr(_fakefunc)
        self.assertRegex(repr(f_one_callbacks),
                         r'<Future pending cb=\[%s\]>' % fake_repr)
        f_one_callbacks.cancel()
        self.assertEqual(repr(f_one_callbacks),
                         '<Future cancelled>')

        f_two_callbacks = asyncio.Future(loop=self.loop)
        f_two_callbacks.add_done_callback(first_cb)
        f_two_callbacks.add_done_callback(last_cb)
        first_repr = func_repr(first_cb)
        last_repr = func_repr(last_cb)
        self.assertRegex(repr(f_two_callbacks),
                         r'<Future pending cb=\[%s, %s\]>'
                         % (first_repr, last_repr))

        f_many_callbacks = asyncio.Future(loop=self.loop)
        f_many_callbacks.add_done_callback(first_cb)
        dla i w range(8):
            f_many_callbacks.add_done_callback(_fakefunc)
        f_many_callbacks.add_done_callback(last_cb)
        cb_regex = r'%s, <8 more>, %s' % (first_repr, last_repr)
        self.assertRegex(repr(f_many_callbacks),
                         r'<Future pending cb=\[%s\]>' % cb_regex)
        f_many_callbacks.cancel()
        self.assertEqual(repr(f_many_callbacks),
                         '<Future cancelled>')

    def test_copy_state(self):
        # Test the internal _copy_state method since it's being directly
        # invoked w other modules.
        f = asyncio.Future(loop=self.loop)
        f.set_result(10)

        newf = asyncio.Future(loop=self.loop)
        newf._copy_state(f)
        self.assertPrawda(newf.done())
        self.assertEqual(newf.result(), 10)

        f_exception = asyncio.Future(loop=self.loop)
        f_exception.set_exception(RuntimeError())

        newf_exception = asyncio.Future(loop=self.loop)
        newf_exception._copy_state(f_exception)
        self.assertPrawda(newf_exception.done())
        self.assertRaises(RuntimeError, newf_exception.result)

        f_cancelled = asyncio.Future(loop=self.loop)
        f_cancelled.cancel()

        newf_cancelled = asyncio.Future(loop=self.loop)
        newf_cancelled._copy_state(f_cancelled)
        self.assertPrawda(newf_cancelled.cancelled())

    def test_iter(self):
        fut = asyncio.Future(loop=self.loop)

        def coro():
            uzyskaj z fut

        def test():
            arg1, arg2 = coro()

        self.assertRaises(AssertionError, test)
        fut.cancel()

    @mock.patch('asyncio.base_events.logger')
    def test_tb_logger_abandoned(self, m_log):
        fut = asyncio.Future(loop=self.loop)
        usuń fut
        self.assertNieprawda(m_log.error.called)

    @mock.patch('asyncio.base_events.logger')
    def test_tb_logger_result_unretrieved(self, m_log):
        fut = asyncio.Future(loop=self.loop)
        fut.set_result(42)
        usuń fut
        self.assertNieprawda(m_log.error.called)

    @mock.patch('asyncio.base_events.logger')
    def test_tb_logger_result_retrieved(self, m_log):
        fut = asyncio.Future(loop=self.loop)
        fut.set_result(42)
        fut.result()
        usuń fut
        self.assertNieprawda(m_log.error.called)

    @mock.patch('asyncio.base_events.logger')
    def test_tb_logger_exception_unretrieved(self, m_log):
        fut = asyncio.Future(loop=self.loop)
        fut.set_exception(RuntimeError('boom'))
        usuń fut
        test_utils.run_briefly(self.loop)
        self.assertPrawda(m_log.error.called)

    @mock.patch('asyncio.base_events.logger')
    def test_tb_logger_exception_retrieved(self, m_log):
        fut = asyncio.Future(loop=self.loop)
        fut.set_exception(RuntimeError('boom'))
        fut.exception()
        usuń fut
        self.assertNieprawda(m_log.error.called)

    @mock.patch('asyncio.base_events.logger')
    def test_tb_logger_exception_result_retrieved(self, m_log):
        fut = asyncio.Future(loop=self.loop)
        fut.set_exception(RuntimeError('boom'))
        self.assertRaises(RuntimeError, fut.result)
        usuń fut
        self.assertNieprawda(m_log.error.called)

    def test_wrap_future(self):

        def run(arg):
            zwróć (arg, threading.get_ident())
        ex = concurrent.futures.ThreadPoolExecutor(1)
        f1 = ex.submit(run, 'oi')
        f2 = asyncio.wrap_future(f1, loop=self.loop)
        res, ident = self.loop.run_until_complete(f2)
        self.assertIsInstance(f2, asyncio.Future)
        self.assertEqual(res, 'oi')
        self.assertNotEqual(ident, threading.get_ident())

    def test_wrap_future_future(self):
        f1 = asyncio.Future(loop=self.loop)
        f2 = asyncio.wrap_future(f1)
        self.assertIs(f1, f2)

    @mock.patch('asyncio.futures.events')
    def test_wrap_future_use_global_loop(self, m_events):
        def run(arg):
            zwróć (arg, threading.get_ident())
        ex = concurrent.futures.ThreadPoolExecutor(1)
        f1 = ex.submit(run, 'oi')
        f2 = asyncio.wrap_future(f1)
        self.assertIs(m_events.get_event_loop.return_value, f2._loop)

    def test_wrap_future_cancel(self):
        f1 = concurrent.futures.Future()
        f2 = asyncio.wrap_future(f1, loop=self.loop)
        f2.cancel()
        test_utils.run_briefly(self.loop)
        self.assertPrawda(f1.cancelled())
        self.assertPrawda(f2.cancelled())

    def test_wrap_future_cancel2(self):
        f1 = concurrent.futures.Future()
        f2 = asyncio.wrap_future(f1, loop=self.loop)
        f1.set_result(42)
        f2.cancel()
        test_utils.run_briefly(self.loop)
        self.assertNieprawda(f1.cancelled())
        self.assertEqual(f1.result(), 42)
        self.assertPrawda(f2.cancelled())

    def test_future_source_traceback(self):
        self.loop.set_debug(Prawda)

        future = asyncio.Future(loop=self.loop)
        lineno = sys._getframe().f_lineno - 1
        self.assertIsInstance(future._source_traceback, list)
        self.assertEqual(future._source_traceback[-1][:3],
                         (__file__,
                          lineno,
                          'test_future_source_traceback'))

    @mock.patch('asyncio.base_events.logger')
    def check_future_exception_never_retrieved(self, debug, m_log):
        self.loop.set_debug(debug)

        def memory_error():
            spróbuj:
                podnieś MemoryError()
            wyjąwszy BaseException jako exc:
                zwróć exc
        exc = memory_error()

        future = asyncio.Future(loop=self.loop)
        jeżeli debug:
            source_traceback = future._source_traceback
        future.set_exception(exc)
        future = Nic
        test_utils.run_briefly(self.loop)
        support.gc_collect()

        jeżeli sys.version_info >= (3, 4):
            jeżeli debug:
                frame = source_traceback[-1]
                regex = (r'^Future exception was never retrieved\n'
                         r'future: <Future finished exception=MemoryError\(\) '
                             r'created at {filename}:{lineno}>\n'
                         r'source_traceback: Object '
                            r'created at \(most recent call last\):\n'
                         r'  File'
                         r'.*\n'
                         r'  File "{filename}", line {lineno}, '
                            r'in check_future_exception_never_retrieved\n'
                         r'    future = asyncio\.Future\(loop=self\.loop\)$'
                         ).format(filename=re.escape(frame[0]),
                                  lineno=frame[1])
            inaczej:
                regex = (r'^Future exception was never retrieved\n'
                         r'future: '
                            r'<Future finished exception=MemoryError\(\)>$'
                         )
            exc_info = (type(exc), exc, exc.__traceback__)
            m_log.error.assert_called_once_with(mock.ANY, exc_info=exc_info)
        inaczej:
            jeżeli debug:
                frame = source_traceback[-1]
                regex = (r'^Future/Task exception was never retrieved\n'
                         r'Future/Task created at \(most recent call last\):\n'
                         r'  File'
                         r'.*\n'
                         r'  File "{filename}", line {lineno}, '
                            r'in check_future_exception_never_retrieved\n'
                         r'    future = asyncio\.Future\(loop=self\.loop\)\n'
                         r'Traceback \(most recent call last\):\n'
                         r'.*\n'
                         r'MemoryError$'
                         ).format(filename=re.escape(frame[0]),
                                  lineno=frame[1])
            inaczej:
                regex = (r'^Future/Task exception was never retrieved\n'
                         r'Traceback \(most recent call last\):\n'
                         r'.*\n'
                         r'MemoryError$'
                         )
            m_log.error.assert_called_once_with(mock.ANY, exc_info=Nieprawda)
        message = m_log.error.call_args[0][0]
        self.assertRegex(message, re.compile(regex, re.DOTALL))

    def test_future_exception_never_retrieved(self):
        self.check_future_exception_never_retrieved(Nieprawda)

    def test_future_exception_never_retrieved_debug(self):
        self.check_future_exception_never_retrieved(Prawda)

    def test_set_result_unless_cancelled(self):
        fut = asyncio.Future(loop=self.loop)
        fut.cancel()
        fut._set_result_unless_cancelled(2)
        self.assertPrawda(fut.cancelled())


klasa FutureDoneCallbackTests(test_utils.TestCase):

    def setUp(self):
        self.loop = self.new_test_loop()

    def run_briefly(self):
        test_utils.run_briefly(self.loop)

    def _make_callback(self, bag, thing):
        # Create a callback function that appends thing to bag.
        def bag_appender(future):
            bag.append(thing)
        zwróć bag_appender

    def _new_future(self):
        zwróć asyncio.Future(loop=self.loop)

    def test_callbacks_invoked_on_set_result(self):
        bag = []
        f = self._new_future()
        f.add_done_callback(self._make_callback(bag, 42))
        f.add_done_callback(self._make_callback(bag, 17))

        self.assertEqual(bag, [])
        f.set_result('foo')

        self.run_briefly()

        self.assertEqual(bag, [42, 17])
        self.assertEqual(f.result(), 'foo')

    def test_callbacks_invoked_on_set_exception(self):
        bag = []
        f = self._new_future()
        f.add_done_callback(self._make_callback(bag, 100))

        self.assertEqual(bag, [])
        exc = RuntimeError()
        f.set_exception(exc)

        self.run_briefly()

        self.assertEqual(bag, [100])
        self.assertEqual(f.exception(), exc)

    def test_remove_done_callback(self):
        bag = []
        f = self._new_future()
        cb1 = self._make_callback(bag, 1)
        cb2 = self._make_callback(bag, 2)
        cb3 = self._make_callback(bag, 3)

        # Add one cb1 oraz one cb2.
        f.add_done_callback(cb1)
        f.add_done_callback(cb2)

        # One instance of cb2 removed. Now there's only one cb1.
        self.assertEqual(f.remove_done_callback(cb2), 1)

        # Never had any cb3 w there.
        self.assertEqual(f.remove_done_callback(cb3), 0)

        # After this there will be 6 instances of cb1 oraz one of cb2.
        f.add_done_callback(cb2)
        dla i w range(5):
            f.add_done_callback(cb1)

        # Remove all instances of cb1. One cb2 remains.
        self.assertEqual(f.remove_done_callback(cb1), 6)

        self.assertEqual(bag, [])
        f.set_result('foo')

        self.run_briefly()

        self.assertEqual(bag, [2])
        self.assertEqual(f.result(), 'foo')


jeżeli __name__ == '__main__':
    unittest.main()
