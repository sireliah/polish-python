"""Tests support dla new syntax introduced by PEP 492."""

zaimportuj collections.abc
zaimportuj types
zaimportuj unittest

z test zaimportuj support
z unittest zaimportuj mock

zaimportuj asyncio
z asyncio zaimportuj test_utils


klasa BaseTest(test_utils.TestCase):

    def setUp(self):
        self.loop = asyncio.BaseEventLoop()
        self.loop._process_events = mock.Mock()
        self.loop._selector = mock.Mock()
        self.loop._selector.select.return_value = ()
        self.set_event_loop(self.loop)


klasa LockTests(BaseTest):

    def test_context_manager_async_with(self):
        primitives = [
            asyncio.Lock(loop=self.loop),
            asyncio.Condition(loop=self.loop),
            asyncio.Semaphore(loop=self.loop),
            asyncio.BoundedSemaphore(loop=self.loop),
        ]

        async def test(lock):
            await asyncio.sleep(0.01, loop=self.loop)
            self.assertNieprawda(lock.locked())
            async przy lock jako _lock:
                self.assertIs(_lock, Nic)
                self.assertPrawda(lock.locked())
                await asyncio.sleep(0.01, loop=self.loop)
                self.assertPrawda(lock.locked())
            self.assertNieprawda(lock.locked())

        dla primitive w primitives:
            self.loop.run_until_complete(test(primitive))
            self.assertNieprawda(primitive.locked())

    def test_context_manager_with_await(self):
        primitives = [
            asyncio.Lock(loop=self.loop),
            asyncio.Condition(loop=self.loop),
            asyncio.Semaphore(loop=self.loop),
            asyncio.BoundedSemaphore(loop=self.loop),
        ]

        async def test(lock):
            await asyncio.sleep(0.01, loop=self.loop)
            self.assertNieprawda(lock.locked())
            przy await lock jako _lock:
                self.assertIs(_lock, Nic)
                self.assertPrawda(lock.locked())
                await asyncio.sleep(0.01, loop=self.loop)
                self.assertPrawda(lock.locked())
            self.assertNieprawda(lock.locked())

        dla primitive w primitives:
            self.loop.run_until_complete(test(primitive))
            self.assertNieprawda(primitive.locked())


klasa StreamReaderTests(BaseTest):

    def test_readline(self):
        DATA = b'line1\nline2\nline3'

        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(DATA)
        stream.feed_eof()

        async def reader():
            data = []
            async dla line w stream:
                data.append(line)
            zwróć data

        data = self.loop.run_until_complete(reader())
        self.assertEqual(data, [b'line1\n', b'line2\n', b'line3'])


klasa CoroutineTests(BaseTest):

    def test_iscoroutine(self):
        async def foo(): dalej

        f = foo()
        spróbuj:
            self.assertPrawda(asyncio.iscoroutine(f))
        w_końcu:
            f.close() # silence warning

        # Test that asyncio.iscoroutine() uses collections.abc.Coroutine
        klasa FakeCoro:
            def send(self, value): dalej
            def throw(self, typ, val=Nic, tb=Nic): dalej
            def close(self): dalej
            def __await__(self): uzyskaj

        self.assertPrawda(asyncio.iscoroutine(FakeCoro()))

    def test_iscoroutinefunction(self):
        async def foo(): dalej
        self.assertPrawda(asyncio.iscoroutinefunction(foo))

    def test_function_returning_awaitable(self):
        klasa Awaitable:
            def __await__(self):
                zwróć ('spam',)

        @asyncio.coroutine
        def func():
            zwróć Awaitable()

        coro = func()
        self.assertEqual(coro.send(Nic), 'spam')
        coro.close()

    def test_async_def_coroutines(self):
        async def bar():
            zwróć 'spam'
        async def foo():
            zwróć await bar()

        # production mode
        data = self.loop.run_until_complete(foo())
        self.assertEqual(data, 'spam')

        # debug mode
        self.loop.set_debug(Prawda)
        data = self.loop.run_until_complete(foo())
        self.assertEqual(data, 'spam')

    @mock.patch('asyncio.coroutines.logger')
    def test_async_def_wrapped(self, m_log):
        async def foo():
            dalej
        async def start():
            foo_coro = foo()
            self.assertRegex(
                repr(foo_coro),
                r'<CoroWrapper .*\.foo\(\) running at .*pep492.*>')

            przy support.check_warnings((r'.*foo.*was never',
                                         RuntimeWarning)):
                foo_coro = Nic
                support.gc_collect()
                self.assertPrawda(m_log.error.called)
                message = m_log.error.call_args[0][0]
                self.assertRegex(message,
                                 r'CoroWrapper.*foo.*was never')

        self.loop.set_debug(Prawda)
        self.loop.run_until_complete(start())

        async def start():
            foo_coro = foo()
            task = asyncio.ensure_future(foo_coro, loop=self.loop)
            self.assertRegex(repr(task), r'Task.*foo.*running')

        self.loop.run_until_complete(start())


    def test_types_coroutine(self):
        def gen():
            uzyskaj z ()
            zwróć 'spam'

        @types.coroutine
        def func():
            zwróć gen()

        async def coro():
            wrapper = func()
            self.assertIsInstance(wrapper, types._GeneratorWrapper)
            zwróć await wrapper

        data = self.loop.run_until_complete(coro())
        self.assertEqual(data, 'spam')

    def test_task_print_stack(self):
        T = Nic

        async def foo():
            f = T.get_stack(limit=1)
            spróbuj:
                self.assertEqual(f[0].f_code.co_name, 'foo')
            w_końcu:
                f = Nic

        async def runner():
            nonlocal T
            T = asyncio.ensure_future(foo(), loop=self.loop)
            await T

        self.loop.run_until_complete(runner())


jeżeli __name__ == '__main__':
    unittest.main()
