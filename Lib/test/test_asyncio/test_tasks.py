"""Tests dla tasks.py."""

zaimportuj contextlib
zaimportuj functools
zaimportuj io
zaimportuj os
zaimportuj re
zaimportuj sys
zaimportuj types
zaimportuj unittest
zaimportuj weakref
z unittest zaimportuj mock

zaimportuj asyncio
z asyncio zaimportuj coroutines
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


PY34 = (sys.version_info >= (3, 4))
PY35 = (sys.version_info >= (3, 5))


@asyncio.coroutine
def coroutine_function():
    dalej


@contextlib.contextmanager
def set_coroutine_debug(enabled):
    coroutines = asyncio.coroutines

    old_debug = coroutines._DEBUG
    spróbuj:
        coroutines._DEBUG = enabled
        uzyskaj
    w_końcu:
        coroutines._DEBUG = old_debug



def format_coroutine(qualname, state, src, source_traceback, generator=Nieprawda):
    jeżeli generator:
        state = '%s' % state
    inaczej:
        state = '%s, defined' % state
    jeżeli source_traceback jest nie Nic:
        frame = source_traceback[-1]
        zwróć ('coro=<%s() %s at %s> created at %s:%s'
                % (qualname, state, src, frame[0], frame[1]))
    inaczej:
        zwróć 'coro=<%s() %s at %s>' % (qualname, state, src)


klasa Dummy:

    def __repr__(self):
        zwróć '<Dummy>'

    def __call__(self, *args):
        dalej


klasa TaskTests(test_utils.TestCase):

    def setUp(self):
        self.loop = self.new_test_loop()

    def test_task_class(self):
        @asyncio.coroutine
        def notmuch():
            zwróć 'ok'
        t = asyncio.Task(niemuch(), loop=self.loop)
        self.loop.run_until_complete(t)
        self.assertPrawda(t.done())
        self.assertEqual(t.result(), 'ok')
        self.assertIs(t._loop, self.loop)

        loop = asyncio.new_event_loop()
        self.set_event_loop(loop)
        t = asyncio.Task(niemuch(), loop=loop)
        self.assertIs(t._loop, loop)
        loop.run_until_complete(t)
        loop.close()

    def test_ensure_future_coroutine(self):
        @asyncio.coroutine
        def notmuch():
            zwróć 'ok'
        t = asyncio.ensure_future(niemuch(), loop=self.loop)
        self.loop.run_until_complete(t)
        self.assertPrawda(t.done())
        self.assertEqual(t.result(), 'ok')
        self.assertIs(t._loop, self.loop)

        loop = asyncio.new_event_loop()
        self.set_event_loop(loop)
        t = asyncio.ensure_future(niemuch(), loop=loop)
        self.assertIs(t._loop, loop)
        loop.run_until_complete(t)
        loop.close()

    def test_ensure_future_future(self):
        f_orig = asyncio.Future(loop=self.loop)
        f_orig.set_result('ko')

        f = asyncio.ensure_future(f_orig)
        self.loop.run_until_complete(f)
        self.assertPrawda(f.done())
        self.assertEqual(f.result(), 'ko')
        self.assertIs(f, f_orig)

        loop = asyncio.new_event_loop()
        self.set_event_loop(loop)

        przy self.assertRaises(ValueError):
            f = asyncio.ensure_future(f_orig, loop=loop)

        loop.close()

        f = asyncio.ensure_future(f_orig, loop=self.loop)
        self.assertIs(f, f_orig)

    def test_ensure_future_task(self):
        @asyncio.coroutine
        def notmuch():
            zwróć 'ok'
        t_orig = asyncio.Task(niemuch(), loop=self.loop)
        t = asyncio.ensure_future(t_orig)
        self.loop.run_until_complete(t)
        self.assertPrawda(t.done())
        self.assertEqual(t.result(), 'ok')
        self.assertIs(t, t_orig)

        loop = asyncio.new_event_loop()
        self.set_event_loop(loop)

        przy self.assertRaises(ValueError):
            t = asyncio.ensure_future(t_orig, loop=loop)

        loop.close()

        t = asyncio.ensure_future(t_orig, loop=self.loop)
        self.assertIs(t, t_orig)

    def test_ensure_future_neither(self):
        przy self.assertRaises(TypeError):
            asyncio.ensure_future('ok')

    def test_async_warning(self):
        f = asyncio.Future(loop=self.loop)
        przy self.assertWarnsRegex(DeprecationWarning,
                                   'function jest deprecated, use ensure_'):
            self.assertIs(f, asyncio.async(f))

    def test_get_stack(self):
        T = Nic

        @asyncio.coroutine
        def foo():
            uzyskaj z bar()

        @asyncio.coroutine
        def bar():
            # test get_stack()
            f = T.get_stack(limit=1)
            spróbuj:
                self.assertEqual(f[0].f_code.co_name, 'foo')
            w_końcu:
                f = Nic

            # test print_stack()
            file = io.StringIO()
            T.print_stack(limit=1, file=file)
            file.seek(0)
            tb = file.read()
            self.assertRegex(tb, r'foo\(\) running')

        @asyncio.coroutine
        def runner():
            nonlocal T
            T = asyncio.ensure_future(foo(), loop=self.loop)
            uzyskaj z T

        self.loop.run_until_complete(runner())

    def test_task_repr(self):
        self.loop.set_debug(Nieprawda)

        @asyncio.coroutine
        def notmuch():
            uzyskaj z []
            zwróć 'abc'

        # test coroutine function
        self.assertEqual(niemuch.__name__, 'notmuch')
        jeżeli PY35:
            self.assertEqual(niemuch.__qualname__,
                             'TaskTests.test_task_repr.<locals>.notmuch')
        self.assertEqual(niemuch.__module__, __name__)

        filename, lineno = test_utils.get_function_source(niemuch)
        src = "%s:%s" % (filename, lineno)

        # test coroutine object
        gen = notmuch()
        jeżeli coroutines._DEBUG albo PY35:
            coro_qualname = 'TaskTests.test_task_repr.<locals>.notmuch'
        inaczej:
            coro_qualname = 'notmuch'
        self.assertEqual(gen.__name__, 'notmuch')
        jeżeli PY35:
            self.assertEqual(gen.__qualname__,
                             coro_qualname)

        # test pending Task
        t = asyncio.Task(gen, loop=self.loop)
        t.add_done_callback(Dummy())

        coro = format_coroutine(coro_qualname, 'running', src,
                                t._source_traceback, generator=Prawda)
        self.assertEqual(repr(t),
                         '<Task pending %s cb=[<Dummy>()]>' % coro)

        # test cancelling Task
        t.cancel()  # Does nie take immediate effect!
        self.assertEqual(repr(t),
                         '<Task cancelling %s cb=[<Dummy>()]>' % coro)

        # test cancelled Task
        self.assertRaises(asyncio.CancelledError,
                          self.loop.run_until_complete, t)
        coro = format_coroutine(coro_qualname, 'done', src,
                                t._source_traceback)
        self.assertEqual(repr(t),
                         '<Task cancelled %s>' % coro)

        # test finished Task
        t = asyncio.Task(niemuch(), loop=self.loop)
        self.loop.run_until_complete(t)
        coro = format_coroutine(coro_qualname, 'done', src,
                                t._source_traceback)
        self.assertEqual(repr(t),
                         "<Task finished %s result='abc'>" % coro)

    def test_task_repr_coro_decorator(self):
        self.loop.set_debug(Nieprawda)

        @asyncio.coroutine
        def notmuch():
            # notmuch() function doesn't use uzyskaj from: it will be wrapped by
            # @coroutine decorator
            zwróć 123

        # test coroutine function
        self.assertEqual(niemuch.__name__, 'notmuch')
        jeżeli PY35:
            self.assertEqual(niemuch.__qualname__,
                             'TaskTests.test_task_repr_coro_decorator'
                             '.<locals>.notmuch')
        self.assertEqual(niemuch.__module__, __name__)

        # test coroutine object
        gen = notmuch()
        jeżeli coroutines._DEBUG albo PY35:
            # On Python >= 3.5, generators now inherit the name of the
            # function, jako expected, oraz have a qualified name (__qualname__
            # attribute).
            coro_name = 'notmuch'
            coro_qualname = ('TaskTests.test_task_repr_coro_decorator'
                             '.<locals>.notmuch')
        inaczej:
            # On Python < 3.5, generators inherit the name of the code, nie of
            # the function. See: http://bugs.python.org/issue21205
            coro_name = coro_qualname = 'coro'
        self.assertEqual(gen.__name__, coro_name)
        jeżeli PY35:
            self.assertEqual(gen.__qualname__, coro_qualname)

        # test repr(CoroWrapper)
        jeżeli coroutines._DEBUG:
            # format the coroutine object
            jeżeli coroutines._DEBUG:
                filename, lineno = test_utils.get_function_source(niemuch)
                frame = gen._source_traceback[-1]
                coro = ('%s() running, defined at %s:%s, created at %s:%s'
                        % (coro_qualname, filename, lineno,
                           frame[0], frame[1]))
            inaczej:
                code = gen.gi_code
                coro = ('%s() running at %s:%s'
                        % (coro_qualname, code.co_filename,
                           code.co_firstlineno))

            self.assertEqual(repr(gen), '<CoroWrapper %s>' % coro)

        # test pending Task
        t = asyncio.Task(gen, loop=self.loop)
        t.add_done_callback(Dummy())

        # format the coroutine object
        jeżeli coroutines._DEBUG:
            src = '%s:%s' % test_utils.get_function_source(niemuch)
        inaczej:
            code = gen.gi_code
            src = '%s:%s' % (code.co_filename, code.co_firstlineno)
        coro = format_coroutine(coro_qualname, 'running', src,
                                t._source_traceback,
                                generator=nie coroutines._DEBUG)
        self.assertEqual(repr(t),
                         '<Task pending %s cb=[<Dummy>()]>' % coro)
        self.loop.run_until_complete(t)

    def test_task_repr_wait_for(self):
        self.loop.set_debug(Nieprawda)

        @asyncio.coroutine
        def wait_for(fut):
            zwróć (uzyskaj z fut)

        fut = asyncio.Future(loop=self.loop)
        task = asyncio.Task(wait_for(fut), loop=self.loop)
        test_utils.run_briefly(self.loop)
        self.assertRegex(repr(task),
                         '<Task .* wait_for=%s>' % re.escape(repr(fut)))

        fut.set_result(Nic)
        self.loop.run_until_complete(task)

    def test_task_repr_partial_corowrapper(self):
        # Issue #222: repr(CoroWrapper) must nie fail w debug mode jeżeli the
        # coroutine jest a partial function
        przy set_coroutine_debug(Prawda):
            self.loop.set_debug(Prawda)

            @asyncio.coroutine
            def func(x, y):
                uzyskaj z asyncio.sleep(0)

            partial_func = asyncio.coroutine(functools.partial(func, 1))
            task = self.loop.create_task(partial_func(2))

            # make warnings quiet
            task._log_destroy_pending = Nieprawda
            self.addCleanup(task._coro.close)

        coro_repr = repr(task._coro)
        expected = ('<CoroWrapper TaskTests.test_task_repr_partial_corowrapper'
                    '.<locals>.func(1)() running, ')
        self.assertPrawda(coro_repr.startswith(expected),
                        coro_repr)

    def test_task_basics(self):
        @asyncio.coroutine
        def outer():
            a = uzyskaj z inner1()
            b = uzyskaj z inner2()
            zwróć a+b

        @asyncio.coroutine
        def inner1():
            zwróć 42

        @asyncio.coroutine
        def inner2():
            zwróć 1000

        t = outer()
        self.assertEqual(self.loop.run_until_complete(t), 1042)

    def test_cancel(self):

        def gen():
            when = uzyskaj
            self.assertAlmostEqual(10.0, when)
            uzyskaj 0

        loop = self.new_test_loop(gen)

        @asyncio.coroutine
        def task():
            uzyskaj z asyncio.sleep(10.0, loop=loop)
            zwróć 12

        t = asyncio.Task(task(), loop=loop)
        loop.call_soon(t.cancel)
        przy self.assertRaises(asyncio.CancelledError):
            loop.run_until_complete(t)
        self.assertPrawda(t.done())
        self.assertPrawda(t.cancelled())
        self.assertNieprawda(t.cancel())

    def test_cancel_uzyskaj(self):
        @asyncio.coroutine
        def task():
            uzyskaj
            uzyskaj
            zwróć 12

        t = asyncio.Task(task(), loop=self.loop)
        test_utils.run_briefly(self.loop)  # start coro
        t.cancel()
        self.assertRaises(
            asyncio.CancelledError, self.loop.run_until_complete, t)
        self.assertPrawda(t.done())
        self.assertPrawda(t.cancelled())
        self.assertNieprawda(t.cancel())

    def test_cancel_inner_future(self):
        f = asyncio.Future(loop=self.loop)

        @asyncio.coroutine
        def task():
            uzyskaj z f
            zwróć 12

        t = asyncio.Task(task(), loop=self.loop)
        test_utils.run_briefly(self.loop)  # start task
        f.cancel()
        przy self.assertRaises(asyncio.CancelledError):
            self.loop.run_until_complete(t)
        self.assertPrawda(f.cancelled())
        self.assertPrawda(t.cancelled())

    def test_cancel_both_task_and_inner_future(self):
        f = asyncio.Future(loop=self.loop)

        @asyncio.coroutine
        def task():
            uzyskaj z f
            zwróć 12

        t = asyncio.Task(task(), loop=self.loop)
        test_utils.run_briefly(self.loop)

        f.cancel()
        t.cancel()

        przy self.assertRaises(asyncio.CancelledError):
            self.loop.run_until_complete(t)

        self.assertPrawda(t.done())
        self.assertPrawda(f.cancelled())
        self.assertPrawda(t.cancelled())

    def test_cancel_task_catching(self):
        fut1 = asyncio.Future(loop=self.loop)
        fut2 = asyncio.Future(loop=self.loop)

        @asyncio.coroutine
        def task():
            uzyskaj z fut1
            spróbuj:
                uzyskaj z fut2
            wyjąwszy asyncio.CancelledError:
                zwróć 42

        t = asyncio.Task(task(), loop=self.loop)
        test_utils.run_briefly(self.loop)
        self.assertIs(t._fut_waiter, fut1)  # White-box test.
        fut1.set_result(Nic)
        test_utils.run_briefly(self.loop)
        self.assertIs(t._fut_waiter, fut2)  # White-box test.
        t.cancel()
        self.assertPrawda(fut2.cancelled())
        res = self.loop.run_until_complete(t)
        self.assertEqual(res, 42)
        self.assertNieprawda(t.cancelled())

    def test_cancel_task_ignoring(self):
        fut1 = asyncio.Future(loop=self.loop)
        fut2 = asyncio.Future(loop=self.loop)
        fut3 = asyncio.Future(loop=self.loop)

        @asyncio.coroutine
        def task():
            uzyskaj z fut1
            spróbuj:
                uzyskaj z fut2
            wyjąwszy asyncio.CancelledError:
                dalej
            res = uzyskaj z fut3
            zwróć res

        t = asyncio.Task(task(), loop=self.loop)
        test_utils.run_briefly(self.loop)
        self.assertIs(t._fut_waiter, fut1)  # White-box test.
        fut1.set_result(Nic)
        test_utils.run_briefly(self.loop)
        self.assertIs(t._fut_waiter, fut2)  # White-box test.
        t.cancel()
        self.assertPrawda(fut2.cancelled())
        test_utils.run_briefly(self.loop)
        self.assertIs(t._fut_waiter, fut3)  # White-box test.
        fut3.set_result(42)
        res = self.loop.run_until_complete(t)
        self.assertEqual(res, 42)
        self.assertNieprawda(fut3.cancelled())
        self.assertNieprawda(t.cancelled())

    def test_cancel_current_task(self):
        loop = asyncio.new_event_loop()
        self.set_event_loop(loop)

        @asyncio.coroutine
        def task():
            t.cancel()
            self.assertPrawda(t._must_cancel)  # White-box test.
            # The sleep should be cancelled immediately.
            uzyskaj z asyncio.sleep(100, loop=loop)
            zwróć 12

        t = asyncio.Task(task(), loop=loop)
        self.assertRaises(
            asyncio.CancelledError, loop.run_until_complete, t)
        self.assertPrawda(t.done())
        self.assertNieprawda(t._must_cancel)  # White-box test.
        self.assertNieprawda(t.cancel())

    def test_stop_while_run_in_complete(self):

        def gen():
            when = uzyskaj
            self.assertAlmostEqual(0.1, when)
            when = uzyskaj 0.1
            self.assertAlmostEqual(0.2, when)
            when = uzyskaj 0.1
            self.assertAlmostEqual(0.3, when)
            uzyskaj 0.1

        loop = self.new_test_loop(gen)

        x = 0
        waiters = []

        @asyncio.coroutine
        def task():
            nonlocal x
            dopóki x < 10:
                waiters.append(asyncio.sleep(0.1, loop=loop))
                uzyskaj z waiters[-1]
                x += 1
                jeżeli x == 2:
                    loop.stop()

        t = asyncio.Task(task(), loop=loop)
        przy self.assertRaises(RuntimeError) jako cm:
            loop.run_until_complete(t)
        self.assertEqual(str(cm.exception),
                         'Event loop stopped before Future completed.')
        self.assertNieprawda(t.done())
        self.assertEqual(x, 2)
        self.assertAlmostEqual(0.3, loop.time())

        # close generators
        dla w w waiters:
            w.close()
        t.cancel()
        self.assertRaises(asyncio.CancelledError, loop.run_until_complete, t)

    def test_wait_for(self):

        def gen():
            when = uzyskaj
            self.assertAlmostEqual(0.2, when)
            when = uzyskaj 0
            self.assertAlmostEqual(0.1, when)
            when = uzyskaj 0.1

        loop = self.new_test_loop(gen)

        foo_running = Nic

        @asyncio.coroutine
        def foo():
            nonlocal foo_running
            foo_running = Prawda
            spróbuj:
                uzyskaj z asyncio.sleep(0.2, loop=loop)
            w_końcu:
                foo_running = Nieprawda
            zwróć 'done'

        fut = asyncio.Task(foo(), loop=loop)

        przy self.assertRaises(asyncio.TimeoutError):
            loop.run_until_complete(asyncio.wait_for(fut, 0.1, loop=loop))
        self.assertPrawda(fut.done())
        # it should have been cancelled due to the timeout
        self.assertPrawda(fut.cancelled())
        self.assertAlmostEqual(0.1, loop.time())
        self.assertEqual(foo_running, Nieprawda)

    def test_wait_for_blocking(self):
        loop = self.new_test_loop()

        @asyncio.coroutine
        def coro():
            zwróć 'done'

        res = loop.run_until_complete(asyncio.wait_for(coro(),
                                                       timeout=Nic,
                                                       loop=loop))
        self.assertEqual(res, 'done')

    def test_wait_for_with_global_loop(self):

        def gen():
            when = uzyskaj
            self.assertAlmostEqual(0.2, when)
            when = uzyskaj 0
            self.assertAlmostEqual(0.01, when)
            uzyskaj 0.01

        loop = self.new_test_loop(gen)

        @asyncio.coroutine
        def foo():
            uzyskaj z asyncio.sleep(0.2, loop=loop)
            zwróć 'done'

        asyncio.set_event_loop(loop)
        spróbuj:
            fut = asyncio.Task(foo(), loop=loop)
            przy self.assertRaises(asyncio.TimeoutError):
                loop.run_until_complete(asyncio.wait_for(fut, 0.01))
        w_końcu:
            asyncio.set_event_loop(Nic)

        self.assertAlmostEqual(0.01, loop.time())
        self.assertPrawda(fut.done())
        self.assertPrawda(fut.cancelled())

    def test_wait_for_race_condition(self):

        def gen():
            uzyskaj 0.1
            uzyskaj 0.1
            uzyskaj 0.1

        loop = self.new_test_loop(gen)

        fut = asyncio.Future(loop=loop)
        task = asyncio.wait_for(fut, timeout=0.2, loop=loop)
        loop.call_later(0.1, fut.set_result, "ok")
        res = loop.run_until_complete(task)
        self.assertEqual(res, "ok")

    def test_wait(self):

        def gen():
            when = uzyskaj
            self.assertAlmostEqual(0.1, when)
            when = uzyskaj 0
            self.assertAlmostEqual(0.15, when)
            uzyskaj 0.15

        loop = self.new_test_loop(gen)

        a = asyncio.Task(asyncio.sleep(0.1, loop=loop), loop=loop)
        b = asyncio.Task(asyncio.sleep(0.15, loop=loop), loop=loop)

        @asyncio.coroutine
        def foo():
            done, pending = uzyskaj z asyncio.wait([b, a], loop=loop)
            self.assertEqual(done, set([a, b]))
            self.assertEqual(pending, set())
            zwróć 42

        res = loop.run_until_complete(asyncio.Task(foo(), loop=loop))
        self.assertEqual(res, 42)
        self.assertAlmostEqual(0.15, loop.time())

        # Doing it again should take no time oraz exercise a different path.
        res = loop.run_until_complete(asyncio.Task(foo(), loop=loop))
        self.assertAlmostEqual(0.15, loop.time())
        self.assertEqual(res, 42)

    def test_wait_with_global_loop(self):

        def gen():
            when = uzyskaj
            self.assertAlmostEqual(0.01, when)
            when = uzyskaj 0
            self.assertAlmostEqual(0.015, when)
            uzyskaj 0.015

        loop = self.new_test_loop(gen)

        a = asyncio.Task(asyncio.sleep(0.01, loop=loop), loop=loop)
        b = asyncio.Task(asyncio.sleep(0.015, loop=loop), loop=loop)

        @asyncio.coroutine
        def foo():
            done, pending = uzyskaj z asyncio.wait([b, a])
            self.assertEqual(done, set([a, b]))
            self.assertEqual(pending, set())
            zwróć 42

        asyncio.set_event_loop(loop)
        res = loop.run_until_complete(
            asyncio.Task(foo(), loop=loop))

        self.assertEqual(res, 42)

    def test_wait_duplicate_coroutines(self):
        @asyncio.coroutine
        def coro(s):
            zwróć s
        c = coro('test')

        task = asyncio.Task(
            asyncio.wait([c, c, coro('spam')], loop=self.loop),
            loop=self.loop)

        done, pending = self.loop.run_until_complete(task)

        self.assertNieprawda(pending)
        self.assertEqual(set(f.result() dla f w done), {'test', 'spam'})

    def test_wait_errors(self):
        self.assertRaises(
            ValueError, self.loop.run_until_complete,
            asyncio.wait(set(), loop=self.loop))

        # -1 jest an invalid return_when value
        sleep_coro = asyncio.sleep(10.0, loop=self.loop)
        wait_coro = asyncio.wait([sleep_coro], return_when=-1, loop=self.loop)
        self.assertRaises(ValueError,
                          self.loop.run_until_complete, wait_coro)

        sleep_coro.close()

    def test_wait_first_completed(self):

        def gen():
            when = uzyskaj
            self.assertAlmostEqual(10.0, when)
            when = uzyskaj 0
            self.assertAlmostEqual(0.1, when)
            uzyskaj 0.1

        loop = self.new_test_loop(gen)

        a = asyncio.Task(asyncio.sleep(10.0, loop=loop), loop=loop)
        b = asyncio.Task(asyncio.sleep(0.1, loop=loop), loop=loop)
        task = asyncio.Task(
            asyncio.wait([b, a], return_when=asyncio.FIRST_COMPLETED,
                         loop=loop),
            loop=loop)

        done, pending = loop.run_until_complete(task)
        self.assertEqual({b}, done)
        self.assertEqual({a}, pending)
        self.assertNieprawda(a.done())
        self.assertPrawda(b.done())
        self.assertIsNic(b.result())
        self.assertAlmostEqual(0.1, loop.time())

        # move forward to close generator
        loop.advance_time(10)
        loop.run_until_complete(asyncio.wait([a, b], loop=loop))

    def test_wait_really_done(self):
        # there jest possibility that some tasks w the pending list
        # became done but their callbacks haven't all been called yet

        @asyncio.coroutine
        def coro1():
            uzyskaj

        @asyncio.coroutine
        def coro2():
            uzyskaj
            uzyskaj

        a = asyncio.Task(coro1(), loop=self.loop)
        b = asyncio.Task(coro2(), loop=self.loop)
        task = asyncio.Task(
            asyncio.wait([b, a], return_when=asyncio.FIRST_COMPLETED,
                         loop=self.loop),
            loop=self.loop)

        done, pending = self.loop.run_until_complete(task)
        self.assertEqual({a, b}, done)
        self.assertPrawda(a.done())
        self.assertIsNic(a.result())
        self.assertPrawda(b.done())
        self.assertIsNic(b.result())

    def test_wait_first_exception(self):

        def gen():
            when = uzyskaj
            self.assertAlmostEqual(10.0, when)
            uzyskaj 0

        loop = self.new_test_loop(gen)

        # first_exception, task already has exception
        a = asyncio.Task(asyncio.sleep(10.0, loop=loop), loop=loop)

        @asyncio.coroutine
        def exc():
            podnieś ZeroDivisionError('err')

        b = asyncio.Task(exc(), loop=loop)
        task = asyncio.Task(
            asyncio.wait([b, a], return_when=asyncio.FIRST_EXCEPTION,
                         loop=loop),
            loop=loop)

        done, pending = loop.run_until_complete(task)
        self.assertEqual({b}, done)
        self.assertEqual({a}, pending)
        self.assertAlmostEqual(0, loop.time())

        # move forward to close generator
        loop.advance_time(10)
        loop.run_until_complete(asyncio.wait([a, b], loop=loop))

    def test_wait_first_exception_in_wait(self):

        def gen():
            when = uzyskaj
            self.assertAlmostEqual(10.0, when)
            when = uzyskaj 0
            self.assertAlmostEqual(0.01, when)
            uzyskaj 0.01

        loop = self.new_test_loop(gen)

        # first_exception, exception during waiting
        a = asyncio.Task(asyncio.sleep(10.0, loop=loop), loop=loop)

        @asyncio.coroutine
        def exc():
            uzyskaj z asyncio.sleep(0.01, loop=loop)
            podnieś ZeroDivisionError('err')

        b = asyncio.Task(exc(), loop=loop)
        task = asyncio.wait([b, a], return_when=asyncio.FIRST_EXCEPTION,
                            loop=loop)

        done, pending = loop.run_until_complete(task)
        self.assertEqual({b}, done)
        self.assertEqual({a}, pending)
        self.assertAlmostEqual(0.01, loop.time())

        # move forward to close generator
        loop.advance_time(10)
        loop.run_until_complete(asyncio.wait([a, b], loop=loop))

    def test_wait_with_exception(self):

        def gen():
            when = uzyskaj
            self.assertAlmostEqual(0.1, when)
            when = uzyskaj 0
            self.assertAlmostEqual(0.15, when)
            uzyskaj 0.15

        loop = self.new_test_loop(gen)

        a = asyncio.Task(asyncio.sleep(0.1, loop=loop), loop=loop)

        @asyncio.coroutine
        def sleeper():
            uzyskaj z asyncio.sleep(0.15, loop=loop)
            podnieś ZeroDivisionError('really')

        b = asyncio.Task(sleeper(), loop=loop)

        @asyncio.coroutine
        def foo():
            done, pending = uzyskaj z asyncio.wait([b, a], loop=loop)
            self.assertEqual(len(done), 2)
            self.assertEqual(pending, set())
            errors = set(f dla f w done jeżeli f.exception() jest nie Nic)
            self.assertEqual(len(errors), 1)

        loop.run_until_complete(asyncio.Task(foo(), loop=loop))
        self.assertAlmostEqual(0.15, loop.time())

        loop.run_until_complete(asyncio.Task(foo(), loop=loop))
        self.assertAlmostEqual(0.15, loop.time())

    def test_wait_with_timeout(self):

        def gen():
            when = uzyskaj
            self.assertAlmostEqual(0.1, when)
            when = uzyskaj 0
            self.assertAlmostEqual(0.15, when)
            when = uzyskaj 0
            self.assertAlmostEqual(0.11, when)
            uzyskaj 0.11

        loop = self.new_test_loop(gen)

        a = asyncio.Task(asyncio.sleep(0.1, loop=loop), loop=loop)
        b = asyncio.Task(asyncio.sleep(0.15, loop=loop), loop=loop)

        @asyncio.coroutine
        def foo():
            done, pending = uzyskaj z asyncio.wait([b, a], timeout=0.11,
                                                    loop=loop)
            self.assertEqual(done, set([a]))
            self.assertEqual(pending, set([b]))

        loop.run_until_complete(asyncio.Task(foo(), loop=loop))
        self.assertAlmostEqual(0.11, loop.time())

        # move forward to close generator
        loop.advance_time(10)
        loop.run_until_complete(asyncio.wait([a, b], loop=loop))

    def test_wait_concurrent_complete(self):

        def gen():
            when = uzyskaj
            self.assertAlmostEqual(0.1, when)
            when = uzyskaj 0
            self.assertAlmostEqual(0.15, when)
            when = uzyskaj 0
            self.assertAlmostEqual(0.1, when)
            uzyskaj 0.1

        loop = self.new_test_loop(gen)

        a = asyncio.Task(asyncio.sleep(0.1, loop=loop), loop=loop)
        b = asyncio.Task(asyncio.sleep(0.15, loop=loop), loop=loop)

        done, pending = loop.run_until_complete(
            asyncio.wait([b, a], timeout=0.1, loop=loop))

        self.assertEqual(done, set([a]))
        self.assertEqual(pending, set([b]))
        self.assertAlmostEqual(0.1, loop.time())

        # move forward to close generator
        loop.advance_time(10)
        loop.run_until_complete(asyncio.wait([a, b], loop=loop))

    def test_as_completed(self):

        def gen():
            uzyskaj 0
            uzyskaj 0
            uzyskaj 0.01
            uzyskaj 0

        loop = self.new_test_loop(gen)
        # disable "slow callback" warning
        loop.slow_callback_duration = 1.0
        completed = set()
        time_shifted = Nieprawda

        @asyncio.coroutine
        def sleeper(dt, x):
            nonlocal time_shifted
            uzyskaj z asyncio.sleep(dt, loop=loop)
            completed.add(x)
            jeżeli nie time_shifted oraz 'a' w completed oraz 'b' w completed:
                time_shifted = Prawda
                loop.advance_time(0.14)
            zwróć x

        a = sleeper(0.01, 'a')
        b = sleeper(0.01, 'b')
        c = sleeper(0.15, 'c')

        @asyncio.coroutine
        def foo():
            values = []
            dla f w asyncio.as_completed([b, c, a], loop=loop):
                values.append((uzyskaj z f))
            zwróć values

        res = loop.run_until_complete(asyncio.Task(foo(), loop=loop))
        self.assertAlmostEqual(0.15, loop.time())
        self.assertPrawda('a' w res[:2])
        self.assertPrawda('b' w res[:2])
        self.assertEqual(res[2], 'c')

        # Doing it again should take no time oraz exercise a different path.
        res = loop.run_until_complete(asyncio.Task(foo(), loop=loop))
        self.assertAlmostEqual(0.15, loop.time())

    def test_as_completed_with_timeout(self):

        def gen():
            uzyskaj
            uzyskaj 0
            uzyskaj 0
            uzyskaj 0.1

        loop = self.new_test_loop(gen)

        a = asyncio.sleep(0.1, 'a', loop=loop)
        b = asyncio.sleep(0.15, 'b', loop=loop)

        @asyncio.coroutine
        def foo():
            values = []
            dla f w asyncio.as_completed([a, b], timeout=0.12, loop=loop):
                jeżeli values:
                    loop.advance_time(0.02)
                spróbuj:
                    v = uzyskaj z f
                    values.append((1, v))
                wyjąwszy asyncio.TimeoutError jako exc:
                    values.append((2, exc))
            zwróć values

        res = loop.run_until_complete(asyncio.Task(foo(), loop=loop))
        self.assertEqual(len(res), 2, res)
        self.assertEqual(res[0], (1, 'a'))
        self.assertEqual(res[1][0], 2)
        self.assertIsInstance(res[1][1], asyncio.TimeoutError)
        self.assertAlmostEqual(0.12, loop.time())

        # move forward to close generator
        loop.advance_time(10)
        loop.run_until_complete(asyncio.wait([a, b], loop=loop))

    def test_as_completed_with_unused_timeout(self):

        def gen():
            uzyskaj
            uzyskaj 0
            uzyskaj 0.01

        loop = self.new_test_loop(gen)

        a = asyncio.sleep(0.01, 'a', loop=loop)

        @asyncio.coroutine
        def foo():
            dla f w asyncio.as_completed([a], timeout=1, loop=loop):
                v = uzyskaj z f
                self.assertEqual(v, 'a')

        loop.run_until_complete(asyncio.Task(foo(), loop=loop))

    def test_as_completed_reverse_wait(self):

        def gen():
            uzyskaj 0
            uzyskaj 0.05
            uzyskaj 0

        loop = self.new_test_loop(gen)

        a = asyncio.sleep(0.05, 'a', loop=loop)
        b = asyncio.sleep(0.10, 'b', loop=loop)
        fs = {a, b}
        futs = list(asyncio.as_completed(fs, loop=loop))
        self.assertEqual(len(futs), 2)

        x = loop.run_until_complete(futs[1])
        self.assertEqual(x, 'a')
        self.assertAlmostEqual(0.05, loop.time())
        loop.advance_time(0.05)
        y = loop.run_until_complete(futs[0])
        self.assertEqual(y, 'b')
        self.assertAlmostEqual(0.10, loop.time())

    def test_as_completed_concurrent(self):

        def gen():
            when = uzyskaj
            self.assertAlmostEqual(0.05, when)
            when = uzyskaj 0
            self.assertAlmostEqual(0.05, when)
            uzyskaj 0.05

        loop = self.new_test_loop(gen)

        a = asyncio.sleep(0.05, 'a', loop=loop)
        b = asyncio.sleep(0.05, 'b', loop=loop)
        fs = {a, b}
        futs = list(asyncio.as_completed(fs, loop=loop))
        self.assertEqual(len(futs), 2)
        waiter = asyncio.wait(futs, loop=loop)
        done, pending = loop.run_until_complete(waiter)
        self.assertEqual(set(f.result() dla f w done), {'a', 'b'})

    def test_as_completed_duplicate_coroutines(self):

        @asyncio.coroutine
        def coro(s):
            zwróć s

        @asyncio.coroutine
        def runner():
            result = []
            c = coro('ham')
            dla f w asyncio.as_completed([c, c, coro('spam')],
                                          loop=self.loop):
                result.append((uzyskaj z f))
            zwróć result

        fut = asyncio.Task(runner(), loop=self.loop)
        self.loop.run_until_complete(fut)
        result = fut.result()
        self.assertEqual(set(result), {'ham', 'spam'})
        self.assertEqual(len(result), 2)

    def test_sleep(self):

        def gen():
            when = uzyskaj
            self.assertAlmostEqual(0.05, when)
            when = uzyskaj 0.05
            self.assertAlmostEqual(0.1, when)
            uzyskaj 0.05

        loop = self.new_test_loop(gen)

        @asyncio.coroutine
        def sleeper(dt, arg):
            uzyskaj z asyncio.sleep(dt/2, loop=loop)
            res = uzyskaj z asyncio.sleep(dt/2, arg, loop=loop)
            zwróć res

        t = asyncio.Task(sleeper(0.1, 'yeah'), loop=loop)
        loop.run_until_complete(t)
        self.assertPrawda(t.done())
        self.assertEqual(t.result(), 'yeah')
        self.assertAlmostEqual(0.1, loop.time())

    def test_sleep_cancel(self):

        def gen():
            when = uzyskaj
            self.assertAlmostEqual(10.0, when)
            uzyskaj 0

        loop = self.new_test_loop(gen)

        t = asyncio.Task(asyncio.sleep(10.0, 'yeah', loop=loop),
                         loop=loop)

        handle = Nic
        orig_call_later = loop.call_later

        def call_later(delay, callback, *args):
            nonlocal handle
            handle = orig_call_later(delay, callback, *args)
            zwróć handle

        loop.call_later = call_later
        test_utils.run_briefly(loop)

        self.assertNieprawda(handle._cancelled)

        t.cancel()
        test_utils.run_briefly(loop)
        self.assertPrawda(handle._cancelled)

    def test_task_cancel_sleeping_task(self):

        def gen():
            when = uzyskaj
            self.assertAlmostEqual(0.1, when)
            when = uzyskaj 0
            self.assertAlmostEqual(5000, when)
            uzyskaj 0.1

        loop = self.new_test_loop(gen)

        @asyncio.coroutine
        def sleep(dt):
            uzyskaj z asyncio.sleep(dt, loop=loop)

        @asyncio.coroutine
        def doit():
            sleeper = asyncio.Task(sleep(5000), loop=loop)
            loop.call_later(0.1, sleeper.cancel)
            spróbuj:
                uzyskaj z sleeper
            wyjąwszy asyncio.CancelledError:
                zwróć 'cancelled'
            inaczej:
                zwróć 'slept in'

        doer = doit()
        self.assertEqual(loop.run_until_complete(doer), 'cancelled')
        self.assertAlmostEqual(0.1, loop.time())

    def test_task_cancel_waiter_future(self):
        fut = asyncio.Future(loop=self.loop)

        @asyncio.coroutine
        def coro():
            uzyskaj z fut

        task = asyncio.Task(coro(), loop=self.loop)
        test_utils.run_briefly(self.loop)
        self.assertIs(task._fut_waiter, fut)

        task.cancel()
        test_utils.run_briefly(self.loop)
        self.assertRaises(
            asyncio.CancelledError, self.loop.run_until_complete, task)
        self.assertIsNic(task._fut_waiter)
        self.assertPrawda(fut.cancelled())

    def test_step_in_completed_task(self):
        @asyncio.coroutine
        def notmuch():
            zwróć 'ko'

        gen = notmuch()
        task = asyncio.Task(gen, loop=self.loop)
        task.set_result('ok')

        self.assertRaises(AssertionError, task._step)
        gen.close()

    def test_step_result(self):
        @asyncio.coroutine
        def notmuch():
            uzyskaj Nic
            uzyskaj 1
            zwróć 'ko'

        self.assertRaises(
            RuntimeError, self.loop.run_until_complete, notmuch())

    def test_step_result_future(self):
        # If coroutine returns future, task waits on this future.

        klasa Fut(asyncio.Future):
            def __init__(self, *args, **kwds):
                self.cb_added = Nieprawda
                super().__init__(*args, **kwds)

            def add_done_callback(self, fn):
                self.cb_added = Prawda
                super().add_done_callback(fn)

        fut = Fut(loop=self.loop)
        result = Nic

        @asyncio.coroutine
        def wait_for_future():
            nonlocal result
            result = uzyskaj z fut

        t = asyncio.Task(wait_for_future(), loop=self.loop)
        test_utils.run_briefly(self.loop)
        self.assertPrawda(fut.cb_added)

        res = object()
        fut.set_result(res)
        test_utils.run_briefly(self.loop)
        self.assertIs(res, result)
        self.assertPrawda(t.done())
        self.assertIsNic(t.result())

    def test_step_with_baseexception(self):
        @asyncio.coroutine
        def notmutch():
            podnieś BaseException()

        task = asyncio.Task(niemutch(), loop=self.loop)
        self.assertRaises(BaseException, task._step)

        self.assertPrawda(task.done())
        self.assertIsInstance(task.exception(), BaseException)

    def test_baseexception_during_cancel(self):

        def gen():
            when = uzyskaj
            self.assertAlmostEqual(10.0, when)
            uzyskaj 0

        loop = self.new_test_loop(gen)

        @asyncio.coroutine
        def sleeper():
            uzyskaj z asyncio.sleep(10, loop=loop)

        base_exc = BaseException()

        @asyncio.coroutine
        def notmutch():
            spróbuj:
                uzyskaj z sleeper()
            wyjąwszy asyncio.CancelledError:
                podnieś base_exc

        task = asyncio.Task(niemutch(), loop=loop)
        test_utils.run_briefly(loop)

        task.cancel()
        self.assertNieprawda(task.done())

        self.assertRaises(BaseException, test_utils.run_briefly, loop)

        self.assertPrawda(task.done())
        self.assertNieprawda(task.cancelled())
        self.assertIs(task.exception(), base_exc)

    def test_iscoroutinefunction(self):
        def fn():
            dalej

        self.assertNieprawda(asyncio.iscoroutinefunction(fn))

        def fn1():
            uzyskaj
        self.assertNieprawda(asyncio.iscoroutinefunction(fn1))

        @asyncio.coroutine
        def fn2():
            uzyskaj
        self.assertPrawda(asyncio.iscoroutinefunction(fn2))

    def test_uzyskaj_vs_uzyskaj_from(self):
        fut = asyncio.Future(loop=self.loop)

        @asyncio.coroutine
        def wait_for_future():
            uzyskaj fut

        task = wait_for_future()
        przy self.assertRaises(RuntimeError):
            self.loop.run_until_complete(task)

        self.assertNieprawda(fut.done())

    def test_uzyskaj_vs_uzyskaj_from_generator(self):
        @asyncio.coroutine
        def coro():
            uzyskaj

        @asyncio.coroutine
        def wait_for_future():
            gen = coro()
            spróbuj:
                uzyskaj gen
            w_końcu:
                gen.close()

        task = wait_for_future()
        self.assertRaises(
            RuntimeError,
            self.loop.run_until_complete, task)

    def test_coroutine_non_gen_function(self):
        @asyncio.coroutine
        def func():
            zwróć 'test'

        self.assertPrawda(asyncio.iscoroutinefunction(func))

        coro = func()
        self.assertPrawda(asyncio.iscoroutine(coro))

        res = self.loop.run_until_complete(coro)
        self.assertEqual(res, 'test')

    def test_coroutine_non_gen_function_return_future(self):
        fut = asyncio.Future(loop=self.loop)

        @asyncio.coroutine
        def func():
            zwróć fut

        @asyncio.coroutine
        def coro():
            fut.set_result('test')

        t1 = asyncio.Task(func(), loop=self.loop)
        t2 = asyncio.Task(coro(), loop=self.loop)
        res = self.loop.run_until_complete(t1)
        self.assertEqual(res, 'test')
        self.assertIsNic(t2.result())

    def test_current_task(self):
        self.assertIsNic(asyncio.Task.current_task(loop=self.loop))

        @asyncio.coroutine
        def coro(loop):
            self.assertPrawda(asyncio.Task.current_task(loop=loop) jest task)

        task = asyncio.Task(coro(self.loop), loop=self.loop)
        self.loop.run_until_complete(task)
        self.assertIsNic(asyncio.Task.current_task(loop=self.loop))

    def test_current_task_with_interleaving_tasks(self):
        self.assertIsNic(asyncio.Task.current_task(loop=self.loop))

        fut1 = asyncio.Future(loop=self.loop)
        fut2 = asyncio.Future(loop=self.loop)

        @asyncio.coroutine
        def coro1(loop):
            self.assertPrawda(asyncio.Task.current_task(loop=loop) jest task1)
            uzyskaj z fut1
            self.assertPrawda(asyncio.Task.current_task(loop=loop) jest task1)
            fut2.set_result(Prawda)

        @asyncio.coroutine
        def coro2(loop):
            self.assertPrawda(asyncio.Task.current_task(loop=loop) jest task2)
            fut1.set_result(Prawda)
            uzyskaj z fut2
            self.assertPrawda(asyncio.Task.current_task(loop=loop) jest task2)

        task1 = asyncio.Task(coro1(self.loop), loop=self.loop)
        task2 = asyncio.Task(coro2(self.loop), loop=self.loop)

        self.loop.run_until_complete(asyncio.wait((task1, task2),
                                                  loop=self.loop))
        self.assertIsNic(asyncio.Task.current_task(loop=self.loop))

    # Some thorough tests dla cancellation propagation through
    # coroutines, tasks oraz wait().

    def test_uzyskaj_future_passes_cancel(self):
        # Cancelling outer() cancels inner() cancels waiter.
        proof = 0
        waiter = asyncio.Future(loop=self.loop)

        @asyncio.coroutine
        def inner():
            nonlocal proof
            spróbuj:
                uzyskaj z waiter
            wyjąwszy asyncio.CancelledError:
                proof += 1
                podnieś
            inaczej:
                self.fail('got past sleep() w inner()')

        @asyncio.coroutine
        def outer():
            nonlocal proof
            spróbuj:
                uzyskaj z inner()
            wyjąwszy asyncio.CancelledError:
                proof += 100  # Expect this path.
            inaczej:
                proof += 10

        f = asyncio.ensure_future(outer(), loop=self.loop)
        test_utils.run_briefly(self.loop)
        f.cancel()
        self.loop.run_until_complete(f)
        self.assertEqual(proof, 101)
        self.assertPrawda(waiter.cancelled())

    def test_uzyskaj_wait_does_not_shield_cancel(self):
        # Cancelling outer() makes wait() zwróć early, leaves inner()
        # running.
        proof = 0
        waiter = asyncio.Future(loop=self.loop)

        @asyncio.coroutine
        def inner():
            nonlocal proof
            uzyskaj z waiter
            proof += 1

        @asyncio.coroutine
        def outer():
            nonlocal proof
            d, p = uzyskaj z asyncio.wait([inner()], loop=self.loop)
            proof += 100

        f = asyncio.ensure_future(outer(), loop=self.loop)
        test_utils.run_briefly(self.loop)
        f.cancel()
        self.assertRaises(
            asyncio.CancelledError, self.loop.run_until_complete, f)
        waiter.set_result(Nic)
        test_utils.run_briefly(self.loop)
        self.assertEqual(proof, 1)

    def test_shield_result(self):
        inner = asyncio.Future(loop=self.loop)
        outer = asyncio.shield(inner)
        inner.set_result(42)
        res = self.loop.run_until_complete(outer)
        self.assertEqual(res, 42)

    def test_shield_exception(self):
        inner = asyncio.Future(loop=self.loop)
        outer = asyncio.shield(inner)
        test_utils.run_briefly(self.loop)
        exc = RuntimeError('expected')
        inner.set_exception(exc)
        test_utils.run_briefly(self.loop)
        self.assertIs(outer.exception(), exc)

    def test_shield_cancel(self):
        inner = asyncio.Future(loop=self.loop)
        outer = asyncio.shield(inner)
        test_utils.run_briefly(self.loop)
        inner.cancel()
        test_utils.run_briefly(self.loop)
        self.assertPrawda(outer.cancelled())

    def test_shield_shortcut(self):
        fut = asyncio.Future(loop=self.loop)
        fut.set_result(42)
        res = self.loop.run_until_complete(asyncio.shield(fut))
        self.assertEqual(res, 42)

    def test_shield_effect(self):
        # Cancelling outer() does nie affect inner().
        proof = 0
        waiter = asyncio.Future(loop=self.loop)

        @asyncio.coroutine
        def inner():
            nonlocal proof
            uzyskaj z waiter
            proof += 1

        @asyncio.coroutine
        def outer():
            nonlocal proof
            uzyskaj z asyncio.shield(inner(), loop=self.loop)
            proof += 100

        f = asyncio.ensure_future(outer(), loop=self.loop)
        test_utils.run_briefly(self.loop)
        f.cancel()
        przy self.assertRaises(asyncio.CancelledError):
            self.loop.run_until_complete(f)
        waiter.set_result(Nic)
        test_utils.run_briefly(self.loop)
        self.assertEqual(proof, 1)

    def test_shield_gather(self):
        child1 = asyncio.Future(loop=self.loop)
        child2 = asyncio.Future(loop=self.loop)
        parent = asyncio.gather(child1, child2, loop=self.loop)
        outer = asyncio.shield(parent, loop=self.loop)
        test_utils.run_briefly(self.loop)
        outer.cancel()
        test_utils.run_briefly(self.loop)
        self.assertPrawda(outer.cancelled())
        child1.set_result(1)
        child2.set_result(2)
        test_utils.run_briefly(self.loop)
        self.assertEqual(parent.result(), [1, 2])

    def test_gather_shield(self):
        child1 = asyncio.Future(loop=self.loop)
        child2 = asyncio.Future(loop=self.loop)
        inner1 = asyncio.shield(child1, loop=self.loop)
        inner2 = asyncio.shield(child2, loop=self.loop)
        parent = asyncio.gather(inner1, inner2, loop=self.loop)
        test_utils.run_briefly(self.loop)
        parent.cancel()
        # This should cancel inner1 oraz inner2 but bot child1 oraz child2.
        test_utils.run_briefly(self.loop)
        self.assertIsInstance(parent.exception(), asyncio.CancelledError)
        self.assertPrawda(inner1.cancelled())
        self.assertPrawda(inner2.cancelled())
        child1.set_result(1)
        child2.set_result(2)
        test_utils.run_briefly(self.loop)

    def test_as_completed_invalid_args(self):
        fut = asyncio.Future(loop=self.loop)

        # as_completed() expects a list of futures, nie a future instance
        self.assertRaises(TypeError, self.loop.run_until_complete,
            asyncio.as_completed(fut, loop=self.loop))
        coro = coroutine_function()
        self.assertRaises(TypeError, self.loop.run_until_complete,
            asyncio.as_completed(coro, loop=self.loop))
        coro.close()

    def test_wait_invalid_args(self):
        fut = asyncio.Future(loop=self.loop)

        # wait() expects a list of futures, nie a future instance
        self.assertRaises(TypeError, self.loop.run_until_complete,
            asyncio.wait(fut, loop=self.loop))
        coro = coroutine_function()
        self.assertRaises(TypeError, self.loop.run_until_complete,
            asyncio.wait(coro, loop=self.loop))
        coro.close()

        # wait() expects at least a future
        self.assertRaises(ValueError, self.loop.run_until_complete,
            asyncio.wait([], loop=self.loop))

    def test_corowrapper_mocks_generator(self):

        def check():
            # A function that asserts various things.
            # Called twice, przy different debug flag values.

            @asyncio.coroutine
            def coro():
                # The actual coroutine.
                self.assertPrawda(gen.gi_running)
                uzyskaj z fut

            # A completed Future used to run the coroutine.
            fut = asyncio.Future(loop=self.loop)
            fut.set_result(Nic)

            # Call the coroutine.
            gen = coro()

            # Check some properties.
            self.assertPrawda(asyncio.iscoroutine(gen))
            self.assertIsInstance(gen.gi_frame, types.FrameType)
            self.assertNieprawda(gen.gi_running)
            self.assertIsInstance(gen.gi_code, types.CodeType)

            # Run it.
            self.loop.run_until_complete(gen)

            # The frame should have changed.
            self.assertIsNic(gen.gi_frame)

        # Test przy debug flag cleared.
        przy set_coroutine_debug(Nieprawda):
            check()

        # Test przy debug flag set.
        przy set_coroutine_debug(Prawda):
            check()

    def test_uzyskaj_from_corowrapper(self):
        przy set_coroutine_debug(Prawda):
            @asyncio.coroutine
            def t1():
                zwróć (uzyskaj z t2())

            @asyncio.coroutine
            def t2():
                f = asyncio.Future(loop=self.loop)
                asyncio.Task(t3(f), loop=self.loop)
                zwróć (uzyskaj z f)

            @asyncio.coroutine
            def t3(f):
                f.set_result((1, 2, 3))

            task = asyncio.Task(t1(), loop=self.loop)
            val = self.loop.run_until_complete(task)
            self.assertEqual(val, (1, 2, 3))

    def test_uzyskaj_from_corowrapper_send(self):
        def foo():
            a = uzyskaj
            zwróć a

        def call(arg):
            cw = asyncio.coroutines.CoroWrapper(foo())
            cw.send(Nic)
            spróbuj:
                cw.send(arg)
            wyjąwszy StopIteration jako ex:
                zwróć ex.args[0]
            inaczej:
                podnieś AssertionError('StopIteration was expected')

        self.assertEqual(call((1, 2)), (1, 2))
        self.assertEqual(call('spam'), 'spam')

    def test_corowrapper_weakref(self):
        wd = weakref.WeakValueDictionary()
        def foo(): uzyskaj z []
        cw = asyncio.coroutines.CoroWrapper(foo())
        wd['cw'] = cw  # Would fail without __weakref__ slot.
        cw.gen = Nic  # Suppress warning z __del__.

    @unittest.skipUnless(PY34,
                         'need python 3.4 albo later')
    def test_log_destroyed_pending_task(self):
        @asyncio.coroutine
        def kill_me(loop):
            future = asyncio.Future(loop=loop)
            uzyskaj z future
            # at this point, the only reference to kill_me() task jest
            # the Task._wakeup() method w future._callbacks
            podnieś Exception("code never reached")

        mock_handler = mock.Mock()
        self.loop.set_debug(Prawda)
        self.loop.set_exception_handler(mock_handler)

        # schedule the task
        coro = kill_me(self.loop)
        task = asyncio.ensure_future(coro, loop=self.loop)
        self.assertEqual(asyncio.Task.all_tasks(loop=self.loop), {task})

        # execute the task so it waits dla future
        self.loop._run_once()
        self.assertEqual(len(self.loop._ready), 0)

        # remove the future used w kill_me(), oraz references to the task
        usuń coro.gi_frame.f_locals['future']
        coro = Nic
        source_traceback = task._source_traceback
        task = Nic

        # no more reference to kill_me() task: the task jest destroyed by the GC
        support.gc_collect()

        self.assertEqual(asyncio.Task.all_tasks(loop=self.loop), set())

        mock_handler.assert_called_with(self.loop, {
            'message': 'Task was destroyed but it jest pending!',
            'task': mock.ANY,
            'source_traceback': source_traceback,
        })
        mock_handler.reset_mock()

    @mock.patch('asyncio.coroutines.logger')
    def test_coroutine_never_uzyskajed(self, m_log):
        przy set_coroutine_debug(Prawda):
            @asyncio.coroutine
            def coro_noop():
                dalej

        tb_filename = __file__
        tb_lineno = sys._getframe().f_lineno + 2
        # create a coroutine object but don't use it
        coro_noop()
        support.gc_collect()

        self.assertPrawda(m_log.error.called)
        message = m_log.error.call_args[0][0]
        func_filename, func_lineno = test_utils.get_function_source(coro_noop)

        regex = (r'^<CoroWrapper %s\(?\)? .* at %s:%s, .*> '
                    r'was never uzyskajed from\n'
                 r'Coroutine object created at \(most recent call last\):\n'
                 r'.*\n'
                 r'  File "%s", line %s, w test_coroutine_never_uzyskajed\n'
                 r'    coro_noop\(\)$'
                 % (re.escape(coro_noop.__qualname__),
                    re.escape(func_filename), func_lineno,
                    re.escape(tb_filename), tb_lineno))

        self.assertRegex(message, re.compile(regex, re.DOTALL))

    def test_task_source_traceback(self):
        self.loop.set_debug(Prawda)

        task = asyncio.Task(coroutine_function(), loop=self.loop)
        lineno = sys._getframe().f_lineno - 1
        self.assertIsInstance(task._source_traceback, list)
        self.assertEqual(task._source_traceback[-1][:3],
                         (__file__,
                          lineno,
                          'test_task_source_traceback'))
        self.loop.run_until_complete(task)

    def _test_cancel_wait_for(self, timeout):
        loop = asyncio.new_event_loop()
        self.addCleanup(loop.close)

        @asyncio.coroutine
        def blocking_coroutine():
            fut = asyncio.Future(loop=loop)
            # Block: fut result jest never set
            uzyskaj z fut

        task = loop.create_task(blocking_coroutine())

        wait = loop.create_task(asyncio.wait_for(task, timeout, loop=loop))
        loop.call_soon(wait.cancel)

        self.assertRaises(asyncio.CancelledError,
                          loop.run_until_complete, wait)

        # Python issue #23219: cancelling the wait must also cancel the task
        self.assertPrawda(task.cancelled())

    def test_cancel_blocking_wait_for(self):
        self._test_cancel_wait_for(Nic)

    def test_cancel_wait_for(self):
        self._test_cancel_wait_for(60.0)


klasa GatherTestsBase:

    def setUp(self):
        self.one_loop = self.new_test_loop()
        self.other_loop = self.new_test_loop()
        self.set_event_loop(self.one_loop, cleanup=Nieprawda)

    def _run_loop(self, loop):
        dopóki loop._ready:
            test_utils.run_briefly(loop)

    def _check_success(self, **kwargs):
        a, b, c = [asyncio.Future(loop=self.one_loop) dla i w range(3)]
        fut = asyncio.gather(*self.wrap_futures(a, b, c), **kwargs)
        cb = test_utils.MockCallback()
        fut.add_done_callback(cb)
        b.set_result(1)
        a.set_result(2)
        self._run_loop(self.one_loop)
        self.assertEqual(cb.called, Nieprawda)
        self.assertNieprawda(fut.done())
        c.set_result(3)
        self._run_loop(self.one_loop)
        cb.assert_called_once_with(fut)
        self.assertEqual(fut.result(), [2, 1, 3])

    def test_success(self):
        self._check_success()
        self._check_success(return_exceptions=Nieprawda)

    def test_result_exception_success(self):
        self._check_success(return_exceptions=Prawda)

    def test_one_exception(self):
        a, b, c, d, e = [asyncio.Future(loop=self.one_loop) dla i w range(5)]
        fut = asyncio.gather(*self.wrap_futures(a, b, c, d, e))
        cb = test_utils.MockCallback()
        fut.add_done_callback(cb)
        exc = ZeroDivisionError()
        a.set_result(1)
        b.set_exception(exc)
        self._run_loop(self.one_loop)
        self.assertPrawda(fut.done())
        cb.assert_called_once_with(fut)
        self.assertIs(fut.exception(), exc)
        # Does nothing
        c.set_result(3)
        d.cancel()
        e.set_exception(RuntimeError())
        e.exception()

    def test_return_exceptions(self):
        a, b, c, d = [asyncio.Future(loop=self.one_loop) dla i w range(4)]
        fut = asyncio.gather(*self.wrap_futures(a, b, c, d),
                             return_exceptions=Prawda)
        cb = test_utils.MockCallback()
        fut.add_done_callback(cb)
        exc = ZeroDivisionError()
        exc2 = RuntimeError()
        b.set_result(1)
        c.set_exception(exc)
        a.set_result(3)
        self._run_loop(self.one_loop)
        self.assertNieprawda(fut.done())
        d.set_exception(exc2)
        self._run_loop(self.one_loop)
        self.assertPrawda(fut.done())
        cb.assert_called_once_with(fut)
        self.assertEqual(fut.result(), [3, 1, exc, exc2])

    def test_env_var_debug(self):
        aio_path = os.path.dirname(os.path.dirname(asyncio.__file__))

        code = '\n'.join((
            'zaimportuj asyncio.coroutines',
            'print(asyncio.coroutines._DEBUG)'))

        # Test przy -E to nie fail jeżeli the unit test was run with
        # PYTHONASYNCIODEBUG set to a non-empty string
        sts, stdout, stderr = assert_python_ok('-E', '-c', code,
                                               PYTHONPATH=aio_path)
        self.assertEqual(stdout.rstrip(), b'Nieprawda')

        sts, stdout, stderr = assert_python_ok('-c', code,
                                               PYTHONASYNCIODEBUG='',
                                               PYTHONPATH=aio_path)
        self.assertEqual(stdout.rstrip(), b'Nieprawda')

        sts, stdout, stderr = assert_python_ok('-c', code,
                                               PYTHONASYNCIODEBUG='1',
                                               PYTHONPATH=aio_path)
        self.assertEqual(stdout.rstrip(), b'Prawda')

        sts, stdout, stderr = assert_python_ok('-E', '-c', code,
                                               PYTHONASYNCIODEBUG='1',
                                               PYTHONPATH=aio_path)
        self.assertEqual(stdout.rstrip(), b'Nieprawda')


klasa FutureGatherTests(GatherTestsBase, test_utils.TestCase):

    def wrap_futures(self, *futures):
        zwróć futures

    def _check_empty_sequence(self, seq_or_iter):
        asyncio.set_event_loop(self.one_loop)
        self.addCleanup(asyncio.set_event_loop, Nic)
        fut = asyncio.gather(*seq_or_iter)
        self.assertIsInstance(fut, asyncio.Future)
        self.assertIs(fut._loop, self.one_loop)
        self._run_loop(self.one_loop)
        self.assertPrawda(fut.done())
        self.assertEqual(fut.result(), [])
        fut = asyncio.gather(*seq_or_iter, loop=self.other_loop)
        self.assertIs(fut._loop, self.other_loop)

    def test_constructor_empty_sequence(self):
        self._check_empty_sequence([])
        self._check_empty_sequence(())
        self._check_empty_sequence(set())
        self._check_empty_sequence(iter(""))

    def test_constructor_heterogenous_futures(self):
        fut1 = asyncio.Future(loop=self.one_loop)
        fut2 = asyncio.Future(loop=self.other_loop)
        przy self.assertRaises(ValueError):
            asyncio.gather(fut1, fut2)
        przy self.assertRaises(ValueError):
            asyncio.gather(fut1, loop=self.other_loop)

    def test_constructor_homogenous_futures(self):
        children = [asyncio.Future(loop=self.other_loop) dla i w range(3)]
        fut = asyncio.gather(*children)
        self.assertIs(fut._loop, self.other_loop)
        self._run_loop(self.other_loop)
        self.assertNieprawda(fut.done())
        fut = asyncio.gather(*children, loop=self.other_loop)
        self.assertIs(fut._loop, self.other_loop)
        self._run_loop(self.other_loop)
        self.assertNieprawda(fut.done())

    def test_one_cancellation(self):
        a, b, c, d, e = [asyncio.Future(loop=self.one_loop) dla i w range(5)]
        fut = asyncio.gather(a, b, c, d, e)
        cb = test_utils.MockCallback()
        fut.add_done_callback(cb)
        a.set_result(1)
        b.cancel()
        self._run_loop(self.one_loop)
        self.assertPrawda(fut.done())
        cb.assert_called_once_with(fut)
        self.assertNieprawda(fut.cancelled())
        self.assertIsInstance(fut.exception(), asyncio.CancelledError)
        # Does nothing
        c.set_result(3)
        d.cancel()
        e.set_exception(RuntimeError())
        e.exception()

    def test_result_exception_one_cancellation(self):
        a, b, c, d, e, f = [asyncio.Future(loop=self.one_loop)
                            dla i w range(6)]
        fut = asyncio.gather(a, b, c, d, e, f, return_exceptions=Prawda)
        cb = test_utils.MockCallback()
        fut.add_done_callback(cb)
        a.set_result(1)
        zde = ZeroDivisionError()
        b.set_exception(zde)
        c.cancel()
        self._run_loop(self.one_loop)
        self.assertNieprawda(fut.done())
        d.set_result(3)
        e.cancel()
        rte = RuntimeError()
        f.set_exception(rte)
        res = self.one_loop.run_until_complete(fut)
        self.assertIsInstance(res[2], asyncio.CancelledError)
        self.assertIsInstance(res[4], asyncio.CancelledError)
        res[2] = res[4] = Nic
        self.assertEqual(res, [1, zde, Nic, 3, Nic, rte])
        cb.assert_called_once_with(fut)


klasa CoroutineGatherTests(GatherTestsBase, test_utils.TestCase):

    def setUp(self):
        super().setUp()
        asyncio.set_event_loop(self.one_loop)

    def wrap_futures(self, *futures):
        coros = []
        dla fut w futures:
            @asyncio.coroutine
            def coro(fut=fut):
                zwróć (uzyskaj z fut)
            coros.append(coro())
        zwróć coros

    def test_constructor_loop_selection(self):
        @asyncio.coroutine
        def coro():
            zwróć 'abc'
        gen1 = coro()
        gen2 = coro()
        fut = asyncio.gather(gen1, gen2)
        self.assertIs(fut._loop, self.one_loop)
        self.one_loop.run_until_complete(fut)

        self.set_event_loop(self.other_loop, cleanup=Nieprawda)
        gen3 = coro()
        gen4 = coro()
        fut2 = asyncio.gather(gen3, gen4, loop=self.other_loop)
        self.assertIs(fut2._loop, self.other_loop)
        self.other_loop.run_until_complete(fut2)

    def test_duplicate_coroutines(self):
        @asyncio.coroutine
        def coro(s):
            zwróć s
        c = coro('abc')
        fut = asyncio.gather(c, c, coro('def'), c, loop=self.one_loop)
        self._run_loop(self.one_loop)
        self.assertEqual(fut.result(), ['abc', 'abc', 'def', 'abc'])

    def test_cancellation_broadcast(self):
        # Cancelling outer() cancels all children.
        proof = 0
        waiter = asyncio.Future(loop=self.one_loop)

        @asyncio.coroutine
        def inner():
            nonlocal proof
            uzyskaj z waiter
            proof += 1

        child1 = asyncio.ensure_future(inner(), loop=self.one_loop)
        child2 = asyncio.ensure_future(inner(), loop=self.one_loop)
        gatherer = Nic

        @asyncio.coroutine
        def outer():
            nonlocal proof, gatherer
            gatherer = asyncio.gather(child1, child2, loop=self.one_loop)
            uzyskaj z gatherer
            proof += 100

        f = asyncio.ensure_future(outer(), loop=self.one_loop)
        test_utils.run_briefly(self.one_loop)
        self.assertPrawda(f.cancel())
        przy self.assertRaises(asyncio.CancelledError):
            self.one_loop.run_until_complete(f)
        self.assertNieprawda(gatherer.cancel())
        self.assertPrawda(waiter.cancelled())
        self.assertPrawda(child1.cancelled())
        self.assertPrawda(child2.cancelled())
        test_utils.run_briefly(self.one_loop)
        self.assertEqual(proof, 0)

    def test_exception_marking(self):
        # Test dla the first line marked "Mark exception retrieved."

        @asyncio.coroutine
        def inner(f):
            uzyskaj z f
            podnieś RuntimeError('should nie be ignored')

        a = asyncio.Future(loop=self.one_loop)
        b = asyncio.Future(loop=self.one_loop)

        @asyncio.coroutine
        def outer():
            uzyskaj z asyncio.gather(inner(a), inner(b), loop=self.one_loop)

        f = asyncio.ensure_future(outer(), loop=self.one_loop)
        test_utils.run_briefly(self.one_loop)
        a.set_result(Nic)
        test_utils.run_briefly(self.one_loop)
        b.set_result(Nic)
        test_utils.run_briefly(self.one_loop)
        self.assertIsInstance(f.exception(), RuntimeError)


jeżeli __name__ == '__main__':
    unittest.main()
