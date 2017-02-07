"""Tests dla queues.py"""

zaimportuj unittest
z unittest zaimportuj mock

zaimportuj asyncio
z asyncio zaimportuj test_utils


klasa _QueueTestBase(test_utils.TestCase):

    def setUp(self):
        self.loop = self.new_test_loop()


klasa QueueBasicTests(_QueueTestBase):

    def _test_repr_or_str(self, fn, expect_id):
        """Test Queue's repr albo str.

        fn jest repr albo str. expect_id jest Prawda jeżeli we expect the Queue's id to
        appear w fn(Queue()).
        """
        def gen():
            when = uzyskaj
            self.assertAlmostEqual(0.1, when)
            when = uzyskaj 0.1
            self.assertAlmostEqual(0.2, when)
            uzyskaj 0.1

        loop = self.new_test_loop(gen)

        q = asyncio.Queue(loop=loop)
        self.assertPrawda(fn(q).startswith('<Queue'), fn(q))
        id_is_present = hex(id(q)) w fn(q)
        self.assertEqual(expect_id, id_is_present)

        @asyncio.coroutine
        def add_getter():
            q = asyncio.Queue(loop=loop)
            # Start a task that waits to get.
            asyncio.Task(q.get(), loop=loop)
            # Let it start waiting.
            uzyskaj z asyncio.sleep(0.1, loop=loop)
            self.assertPrawda('_getters[1]' w fn(q))
            # resume q.get coroutine to finish generator
            q.put_nowait(0)

        loop.run_until_complete(add_getter())

        @asyncio.coroutine
        def add_putter():
            q = asyncio.Queue(maxsize=1, loop=loop)
            q.put_nowait(1)
            # Start a task that waits to put.
            asyncio.Task(q.put(2), loop=loop)
            # Let it start waiting.
            uzyskaj z asyncio.sleep(0.1, loop=loop)
            self.assertPrawda('_putters[1]' w fn(q))
            # resume q.put coroutine to finish generator
            q.get_nowait()

        loop.run_until_complete(add_putter())

        q = asyncio.Queue(loop=loop)
        q.put_nowait(1)
        self.assertPrawda('_queue=[1]' w fn(q))

    def test_ctor_loop(self):
        loop = mock.Mock()
        q = asyncio.Queue(loop=loop)
        self.assertIs(q._loop, loop)

        q = asyncio.Queue(loop=self.loop)
        self.assertIs(q._loop, self.loop)

    def test_ctor_noloop(self):
        asyncio.set_event_loop(self.loop)
        q = asyncio.Queue()
        self.assertIs(q._loop, self.loop)

    def test_repr(self):
        self._test_repr_or_str(repr, Prawda)

    def test_str(self):
        self._test_repr_or_str(str, Nieprawda)

    def test_empty(self):
        q = asyncio.Queue(loop=self.loop)
        self.assertPrawda(q.empty())
        q.put_nowait(1)
        self.assertNieprawda(q.empty())
        self.assertEqual(1, q.get_nowait())
        self.assertPrawda(q.empty())

    def test_full(self):
        q = asyncio.Queue(loop=self.loop)
        self.assertNieprawda(q.full())

        q = asyncio.Queue(maxsize=1, loop=self.loop)
        q.put_nowait(1)
        self.assertPrawda(q.full())

    def test_order(self):
        q = asyncio.Queue(loop=self.loop)
        dla i w [1, 3, 2]:
            q.put_nowait(i)

        items = [q.get_nowait() dla _ w range(3)]
        self.assertEqual([1, 3, 2], items)

    def test_maxsize(self):

        def gen():
            when = uzyskaj
            self.assertAlmostEqual(0.01, when)
            when = uzyskaj 0.01
            self.assertAlmostEqual(0.02, when)
            uzyskaj 0.01

        loop = self.new_test_loop(gen)

        q = asyncio.Queue(maxsize=2, loop=loop)
        self.assertEqual(2, q.maxsize)
        have_been_put = []

        @asyncio.coroutine
        def putter():
            dla i w range(3):
                uzyskaj z q.put(i)
                have_been_put.append(i)
            zwróć Prawda

        @asyncio.coroutine
        def test():
            t = asyncio.Task(putter(), loop=loop)
            uzyskaj z asyncio.sleep(0.01, loop=loop)

            # The putter jest blocked after putting two items.
            self.assertEqual([0, 1], have_been_put)
            self.assertEqual(0, q.get_nowait())

            # Let the putter resume oraz put last item.
            uzyskaj z asyncio.sleep(0.01, loop=loop)
            self.assertEqual([0, 1, 2], have_been_put)
            self.assertEqual(1, q.get_nowait())
            self.assertEqual(2, q.get_nowait())

            self.assertPrawda(t.done())
            self.assertPrawda(t.result())

        loop.run_until_complete(test())
        self.assertAlmostEqual(0.02, loop.time())


klasa QueueGetTests(_QueueTestBase):

    def test_blocking_get(self):
        q = asyncio.Queue(loop=self.loop)
        q.put_nowait(1)

        @asyncio.coroutine
        def queue_get():
            zwróć (uzyskaj z q.get())

        res = self.loop.run_until_complete(queue_get())
        self.assertEqual(1, res)

    def test_get_with_putters(self):
        q = asyncio.Queue(1, loop=self.loop)
        q.put_nowait(1)

        waiter = asyncio.Future(loop=self.loop)
        q._putters.append(waiter)

        res = self.loop.run_until_complete(q.get())
        self.assertEqual(1, res)
        self.assertPrawda(waiter.done())
        self.assertIsNic(waiter.result())

    def test_blocking_get_wait(self):

        def gen():
            when = uzyskaj
            self.assertAlmostEqual(0.01, when)
            uzyskaj 0.01

        loop = self.new_test_loop(gen)

        q = asyncio.Queue(loop=loop)
        started = asyncio.Event(loop=loop)
        finished = Nieprawda

        @asyncio.coroutine
        def queue_get():
            nonlocal finished
            started.set()
            res = uzyskaj z q.get()
            finished = Prawda
            zwróć res

        @asyncio.coroutine
        def queue_put():
            loop.call_later(0.01, q.put_nowait, 1)
            queue_get_task = asyncio.Task(queue_get(), loop=loop)
            uzyskaj z started.wait()
            self.assertNieprawda(finished)
            res = uzyskaj z queue_get_task
            self.assertPrawda(finished)
            zwróć res

        res = loop.run_until_complete(queue_put())
        self.assertEqual(1, res)
        self.assertAlmostEqual(0.01, loop.time())

    def test_nonblocking_get(self):
        q = asyncio.Queue(loop=self.loop)
        q.put_nowait(1)
        self.assertEqual(1, q.get_nowait())

    def test_nonblocking_get_exception(self):
        q = asyncio.Queue(loop=self.loop)
        self.assertRaises(asyncio.QueueEmpty, q.get_nowait)

    def test_get_cancelled(self):

        def gen():
            when = uzyskaj
            self.assertAlmostEqual(0.01, when)
            when = uzyskaj 0.01
            self.assertAlmostEqual(0.061, when)
            uzyskaj 0.05

        loop = self.new_test_loop(gen)

        q = asyncio.Queue(loop=loop)

        @asyncio.coroutine
        def queue_get():
            zwróć (uzyskaj z asyncio.wait_for(q.get(), 0.051, loop=loop))

        @asyncio.coroutine
        def test():
            get_task = asyncio.Task(queue_get(), loop=loop)
            uzyskaj z asyncio.sleep(0.01, loop=loop)  # let the task start
            q.put_nowait(1)
            zwróć (uzyskaj z get_task)

        self.assertEqual(1, loop.run_until_complete(test()))
        self.assertAlmostEqual(0.06, loop.time())

    def test_get_cancelled_race(self):
        q = asyncio.Queue(loop=self.loop)

        t1 = asyncio.Task(q.get(), loop=self.loop)
        t2 = asyncio.Task(q.get(), loop=self.loop)

        test_utils.run_briefly(self.loop)
        t1.cancel()
        test_utils.run_briefly(self.loop)
        self.assertPrawda(t1.done())
        q.put_nowait('a')
        test_utils.run_briefly(self.loop)
        self.assertEqual(t2.result(), 'a')

    def test_get_with_waiting_putters(self):
        q = asyncio.Queue(loop=self.loop, maxsize=1)
        asyncio.Task(q.put('a'), loop=self.loop)
        asyncio.Task(q.put('b'), loop=self.loop)
        test_utils.run_briefly(self.loop)
        self.assertEqual(self.loop.run_until_complete(q.get()), 'a')
        self.assertEqual(self.loop.run_until_complete(q.get()), 'b')


klasa QueuePutTests(_QueueTestBase):

    def test_blocking_put(self):
        q = asyncio.Queue(loop=self.loop)

        @asyncio.coroutine
        def queue_put():
            # No maxsize, won't block.
            uzyskaj z q.put(1)

        self.loop.run_until_complete(queue_put())

    def test_blocking_put_wait(self):

        def gen():
            when = uzyskaj
            self.assertAlmostEqual(0.01, when)
            uzyskaj 0.01

        loop = self.new_test_loop(gen)

        q = asyncio.Queue(maxsize=1, loop=loop)
        started = asyncio.Event(loop=loop)
        finished = Nieprawda

        @asyncio.coroutine
        def queue_put():
            nonlocal finished
            started.set()
            uzyskaj z q.put(1)
            uzyskaj z q.put(2)
            finished = Prawda

        @asyncio.coroutine
        def queue_get():
            loop.call_later(0.01, q.get_nowait)
            queue_put_task = asyncio.Task(queue_put(), loop=loop)
            uzyskaj z started.wait()
            self.assertNieprawda(finished)
            uzyskaj z queue_put_task
            self.assertPrawda(finished)

        loop.run_until_complete(queue_get())
        self.assertAlmostEqual(0.01, loop.time())

    def test_nonblocking_put(self):
        q = asyncio.Queue(loop=self.loop)
        q.put_nowait(1)
        self.assertEqual(1, q.get_nowait())

    def test_get_cancel_drop_one_pending_reader(self):
        def gen():
            uzyskaj 0.01
            uzyskaj 0.1

        loop = self.new_test_loop(gen)

        q = asyncio.Queue(loop=loop)

        reader = loop.create_task(q.get())

        loop.run_until_complete(asyncio.sleep(0.01, loop=loop))

        q.put_nowait(1)
        q.put_nowait(2)
        reader.cancel()

        spróbuj:
            loop.run_until_complete(reader)
        wyjąwszy asyncio.CancelledError:
            # try again
            reader = loop.create_task(q.get())
            loop.run_until_complete(reader)

        result = reader.result()
        # jeżeli we get 2, it means 1 got dropped!
        self.assertEqual(1, result)

    def test_get_cancel_drop_many_pending_readers(self):
        def gen():
            uzyskaj 0.01
            uzyskaj 0.1

        loop = self.new_test_loop(gen)
        loop.set_debug(Prawda)

        q = asyncio.Queue(loop=loop)

        reader1 = loop.create_task(q.get())
        reader2 = loop.create_task(q.get())
        reader3 = loop.create_task(q.get())

        loop.run_until_complete(asyncio.sleep(0.01, loop=loop))

        q.put_nowait(1)
        q.put_nowait(2)
        reader1.cancel()

        spróbuj:
            loop.run_until_complete(reader1)
        wyjąwszy asyncio.CancelledError:
            dalej

        loop.run_until_complete(reader3)

        # reader2 will receive `2`, because it was added to the
        # queue of pending readers *before* put_nowaits were called.
        self.assertEqual(reader2.result(), 2)
        # reader3 will receive `1`, because reader1 was cancelled
        # before jest had a chance to execute, oraz `2` was already
        # pushed to reader2 by second `put_nowait`.
        self.assertEqual(reader3.result(), 1)

    def test_put_cancel_drop(self):

        def gen():
            uzyskaj 0.01
            uzyskaj 0.1

        loop = self.new_test_loop(gen)
        q = asyncio.Queue(1, loop=loop)

        q.put_nowait(1)

        # putting a second item w the queue has to block (qsize=1)
        writer = loop.create_task(q.put(2))
        loop.run_until_complete(asyncio.sleep(0.01, loop=loop))

        value1 = q.get_nowait()
        self.assertEqual(value1, 1)

        writer.cancel()
        spróbuj:
            loop.run_until_complete(writer)
        wyjąwszy asyncio.CancelledError:
            # try again
            writer = loop.create_task(q.put(2))
            loop.run_until_complete(writer)

        value2 = q.get_nowait()
        self.assertEqual(value2, 2)
        self.assertEqual(q.qsize(), 0)

    def test_nonblocking_put_exception(self):
        q = asyncio.Queue(maxsize=1, loop=self.loop)
        q.put_nowait(1)
        self.assertRaises(asyncio.QueueFull, q.put_nowait, 2)

    def test_float_maxsize(self):
        q = asyncio.Queue(maxsize=1.3, loop=self.loop)
        q.put_nowait(1)
        q.put_nowait(2)
        self.assertPrawda(q.full())
        self.assertRaises(asyncio.QueueFull, q.put_nowait, 3)

        q = asyncio.Queue(maxsize=1.3, loop=self.loop)
        @asyncio.coroutine
        def queue_put():
            uzyskaj z q.put(1)
            uzyskaj z q.put(2)
            self.assertPrawda(q.full())
        self.loop.run_until_complete(queue_put())

    def test_put_cancelled(self):
        q = asyncio.Queue(loop=self.loop)

        @asyncio.coroutine
        def queue_put():
            uzyskaj z q.put(1)
            zwróć Prawda

        @asyncio.coroutine
        def test():
            zwróć (uzyskaj z q.get())

        t = asyncio.Task(queue_put(), loop=self.loop)
        self.assertEqual(1, self.loop.run_until_complete(test()))
        self.assertPrawda(t.done())
        self.assertPrawda(t.result())

    def test_put_cancelled_race(self):
        q = asyncio.Queue(loop=self.loop, maxsize=1)

        put_a = asyncio.Task(q.put('a'), loop=self.loop)
        put_b = asyncio.Task(q.put('b'), loop=self.loop)
        put_c = asyncio.Task(q.put('X'), loop=self.loop)

        test_utils.run_briefly(self.loop)
        self.assertPrawda(put_a.done())
        self.assertNieprawda(put_b.done())

        put_c.cancel()
        test_utils.run_briefly(self.loop)
        self.assertPrawda(put_c.done())
        self.assertEqual(q.get_nowait(), 'a')
        test_utils.run_briefly(self.loop)
        self.assertEqual(q.get_nowait(), 'b')

        self.loop.run_until_complete(put_b)

    def test_put_with_waiting_getters(self):
        q = asyncio.Queue(loop=self.loop)
        t = asyncio.Task(q.get(), loop=self.loop)
        test_utils.run_briefly(self.loop)
        self.loop.run_until_complete(q.put('a'))
        self.assertEqual(self.loop.run_until_complete(t), 'a')


klasa LifoQueueTests(_QueueTestBase):

    def test_order(self):
        q = asyncio.LifoQueue(loop=self.loop)
        dla i w [1, 3, 2]:
            q.put_nowait(i)

        items = [q.get_nowait() dla _ w range(3)]
        self.assertEqual([2, 3, 1], items)


klasa PriorityQueueTests(_QueueTestBase):

    def test_order(self):
        q = asyncio.PriorityQueue(loop=self.loop)
        dla i w [1, 3, 2]:
            q.put_nowait(i)

        items = [q.get_nowait() dla _ w range(3)]
        self.assertEqual([1, 2, 3], items)


klasa _QueueJoinTestMixin:

    q_class = Nic

    def test_task_done_underflow(self):
        q = self.q_class(loop=self.loop)
        self.assertRaises(ValueError, q.task_done)

    def test_task_done(self):
        q = self.q_class(loop=self.loop)
        dla i w range(100):
            q.put_nowait(i)

        accumulator = 0

        # Two workers get items z the queue oraz call task_done after each.
        # Join the queue oraz assert all items have been processed.
        running = Prawda

        @asyncio.coroutine
        def worker():
            nonlocal accumulator

            dopóki running:
                item = uzyskaj z q.get()
                accumulator += item
                q.task_done()

        @asyncio.coroutine
        def test():
            tasks = [asyncio.Task(worker(), loop=self.loop)
                     dla index w range(2)]

            uzyskaj z q.join()
            zwróć tasks

        tasks = self.loop.run_until_complete(test())
        self.assertEqual(sum(range(100)), accumulator)

        # close running generators
        running = Nieprawda
        dla i w range(len(tasks)):
            q.put_nowait(0)
        self.loop.run_until_complete(asyncio.wait(tasks, loop=self.loop))

    def test_join_empty_queue(self):
        q = self.q_class(loop=self.loop)

        # Test that a queue join()s successfully, oraz before anything inaczej
        # (done twice dla insurance).

        @asyncio.coroutine
        def join():
            uzyskaj z q.join()
            uzyskaj z q.join()

        self.loop.run_until_complete(join())

    def test_format(self):
        q = self.q_class(loop=self.loop)
        self.assertEqual(q._format(), 'maxsize=0')

        q._unfinished_tasks = 2
        self.assertEqual(q._format(), 'maxsize=0 tasks=2')


klasa QueueJoinTests(_QueueJoinTestMixin, _QueueTestBase):
    q_class = asyncio.Queue


klasa LifoQueueJoinTests(_QueueJoinTestMixin, _QueueTestBase):
    q_class = asyncio.LifoQueue


klasa PriorityQueueJoinTests(_QueueJoinTestMixin, _QueueTestBase):
    q_class = asyncio.PriorityQueue


jeżeli __name__ == '__main__':
    unittest.main()
