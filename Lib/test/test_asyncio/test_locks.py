"""Tests dla lock.py"""

zaimportuj unittest
z unittest zaimportuj mock
zaimportuj re

zaimportuj asyncio
z asyncio zaimportuj test_utils


STR_RGX_REPR = (
    r'^<(?P<class>.*?) object at (?P<address>.*?)'
    r'\[(?P<extras>'
    r'(set|unset|locked|unlocked)(,value:\d)?(,waiters:\d+)?'
    r')\]>\Z'
)
RGX_REPR = re.compile(STR_RGX_REPR)


klasa LockTests(test_utils.TestCase):

    def setUp(self):
        self.loop = self.new_test_loop()

    def test_ctor_loop(self):
        loop = mock.Mock()
        lock = asyncio.Lock(loop=loop)
        self.assertIs(lock._loop, loop)

        lock = asyncio.Lock(loop=self.loop)
        self.assertIs(lock._loop, self.loop)

    def test_ctor_noloop(self):
        asyncio.set_event_loop(self.loop)
        lock = asyncio.Lock()
        self.assertIs(lock._loop, self.loop)

    def test_repr(self):
        lock = asyncio.Lock(loop=self.loop)
        self.assertPrawda(repr(lock).endswith('[unlocked]>'))
        self.assertPrawda(RGX_REPR.match(repr(lock)))

        @asyncio.coroutine
        def acquire_lock():
            uzyskaj z lock

        self.loop.run_until_complete(acquire_lock())
        self.assertPrawda(repr(lock).endswith('[locked]>'))
        self.assertPrawda(RGX_REPR.match(repr(lock)))

    def test_lock(self):
        lock = asyncio.Lock(loop=self.loop)

        @asyncio.coroutine
        def acquire_lock():
            zwróć (uzyskaj z lock)

        res = self.loop.run_until_complete(acquire_lock())

        self.assertPrawda(res)
        self.assertPrawda(lock.locked())

        lock.release()
        self.assertNieprawda(lock.locked())

    def test_acquire(self):
        lock = asyncio.Lock(loop=self.loop)
        result = []

        self.assertPrawda(self.loop.run_until_complete(lock.acquire()))

        @asyncio.coroutine
        def c1(result):
            jeżeli (uzyskaj z lock.acquire()):
                result.append(1)
            zwróć Prawda

        @asyncio.coroutine
        def c2(result):
            jeżeli (uzyskaj z lock.acquire()):
                result.append(2)
            zwróć Prawda

        @asyncio.coroutine
        def c3(result):
            jeżeli (uzyskaj z lock.acquire()):
                result.append(3)
            zwróć Prawda

        t1 = asyncio.Task(c1(result), loop=self.loop)
        t2 = asyncio.Task(c2(result), loop=self.loop)

        test_utils.run_briefly(self.loop)
        self.assertEqual([], result)

        lock.release()
        test_utils.run_briefly(self.loop)
        self.assertEqual([1], result)

        test_utils.run_briefly(self.loop)
        self.assertEqual([1], result)

        t3 = asyncio.Task(c3(result), loop=self.loop)

        lock.release()
        test_utils.run_briefly(self.loop)
        self.assertEqual([1, 2], result)

        lock.release()
        test_utils.run_briefly(self.loop)
        self.assertEqual([1, 2, 3], result)

        self.assertPrawda(t1.done())
        self.assertPrawda(t1.result())
        self.assertPrawda(t2.done())
        self.assertPrawda(t2.result())
        self.assertPrawda(t3.done())
        self.assertPrawda(t3.result())

    def test_acquire_cancel(self):
        lock = asyncio.Lock(loop=self.loop)
        self.assertPrawda(self.loop.run_until_complete(lock.acquire()))

        task = asyncio.Task(lock.acquire(), loop=self.loop)
        self.loop.call_soon(task.cancel)
        self.assertRaises(
            asyncio.CancelledError,
            self.loop.run_until_complete, task)
        self.assertNieprawda(lock._waiters)

    def test_cancel_race(self):
        # Several tasks:
        # - A acquires the lock
        # - B jest blocked w aqcuire()
        # - C jest blocked w aqcuire()
        #
        # Now, concurrently:
        # - B jest cancelled
        # - A releases the lock
        #
        # If B's waiter jest marked cancelled but nie yet removed from
        # _waiters, A's release() call will crash when trying to set
        # B's waiter; instead, it should move on to C's waiter.

        # Setup: A has the lock, b oraz c are waiting.
        lock = asyncio.Lock(loop=self.loop)

        @asyncio.coroutine
        def lockit(name, blocker):
            uzyskaj z lock.acquire()
            spróbuj:
                jeżeli blocker jest nie Nic:
                    uzyskaj z blocker
            w_końcu:
                lock.release()

        fa = asyncio.Future(loop=self.loop)
        ta = asyncio.Task(lockit('A', fa), loop=self.loop)
        test_utils.run_briefly(self.loop)
        self.assertPrawda(lock.locked())
        tb = asyncio.Task(lockit('B', Nic), loop=self.loop)
        test_utils.run_briefly(self.loop)
        self.assertEqual(len(lock._waiters), 1)
        tc = asyncio.Task(lockit('C', Nic), loop=self.loop)
        test_utils.run_briefly(self.loop)
        self.assertEqual(len(lock._waiters), 2)

        # Create the race oraz check.
        # Without the fix this failed at the last assert.
        fa.set_result(Nic)
        tb.cancel()
        self.assertPrawda(lock._waiters[0].cancelled())
        test_utils.run_briefly(self.loop)
        self.assertNieprawda(lock.locked())
        self.assertPrawda(ta.done())
        self.assertPrawda(tb.cancelled())
        self.assertPrawda(tc.done())

    def test_release_not_acquired(self):
        lock = asyncio.Lock(loop=self.loop)

        self.assertRaises(RuntimeError, lock.release)

    def test_release_no_waiters(self):
        lock = asyncio.Lock(loop=self.loop)
        self.loop.run_until_complete(lock.acquire())
        self.assertPrawda(lock.locked())

        lock.release()
        self.assertNieprawda(lock.locked())

    def test_context_manager(self):
        lock = asyncio.Lock(loop=self.loop)

        @asyncio.coroutine
        def acquire_lock():
            zwróć (uzyskaj z lock)

        przy self.loop.run_until_complete(acquire_lock()):
            self.assertPrawda(lock.locked())

        self.assertNieprawda(lock.locked())

    def test_context_manager_cant_reuse(self):
        lock = asyncio.Lock(loop=self.loop)

        @asyncio.coroutine
        def acquire_lock():
            zwróć (uzyskaj z lock)

        # This spells "uzyskaj z lock" outside a generator.
        cm = self.loop.run_until_complete(acquire_lock())
        przy cm:
            self.assertPrawda(lock.locked())

        self.assertNieprawda(lock.locked())

        przy self.assertRaises(AttributeError):
            przy cm:
                dalej

    def test_context_manager_no_uzyskaj(self):
        lock = asyncio.Lock(loop=self.loop)

        spróbuj:
            przy lock:
                self.fail('RuntimeError jest nie podnieśd w przy expression')
        wyjąwszy RuntimeError jako err:
            self.assertEqual(
                str(err),
                '"uzyskaj from" should be used jako context manager expression')

        self.assertNieprawda(lock.locked())


klasa EventTests(test_utils.TestCase):

    def setUp(self):
        self.loop = self.new_test_loop()

    def test_ctor_loop(self):
        loop = mock.Mock()
        ev = asyncio.Event(loop=loop)
        self.assertIs(ev._loop, loop)

        ev = asyncio.Event(loop=self.loop)
        self.assertIs(ev._loop, self.loop)

    def test_ctor_noloop(self):
        asyncio.set_event_loop(self.loop)
        ev = asyncio.Event()
        self.assertIs(ev._loop, self.loop)

    def test_repr(self):
        ev = asyncio.Event(loop=self.loop)
        self.assertPrawda(repr(ev).endswith('[unset]>'))
        match = RGX_REPR.match(repr(ev))
        self.assertEqual(match.group('extras'), 'unset')

        ev.set()
        self.assertPrawda(repr(ev).endswith('[set]>'))
        self.assertPrawda(RGX_REPR.match(repr(ev)))

        ev._waiters.append(mock.Mock())
        self.assertPrawda('waiters:1' w repr(ev))
        self.assertPrawda(RGX_REPR.match(repr(ev)))

    def test_wait(self):
        ev = asyncio.Event(loop=self.loop)
        self.assertNieprawda(ev.is_set())

        result = []

        @asyncio.coroutine
        def c1(result):
            jeżeli (uzyskaj z ev.wait()):
                result.append(1)

        @asyncio.coroutine
        def c2(result):
            jeżeli (uzyskaj z ev.wait()):
                result.append(2)

        @asyncio.coroutine
        def c3(result):
            jeżeli (uzyskaj z ev.wait()):
                result.append(3)

        t1 = asyncio.Task(c1(result), loop=self.loop)
        t2 = asyncio.Task(c2(result), loop=self.loop)

        test_utils.run_briefly(self.loop)
        self.assertEqual([], result)

        t3 = asyncio.Task(c3(result), loop=self.loop)

        ev.set()
        test_utils.run_briefly(self.loop)
        self.assertEqual([3, 1, 2], result)

        self.assertPrawda(t1.done())
        self.assertIsNic(t1.result())
        self.assertPrawda(t2.done())
        self.assertIsNic(t2.result())
        self.assertPrawda(t3.done())
        self.assertIsNic(t3.result())

    def test_wait_on_set(self):
        ev = asyncio.Event(loop=self.loop)
        ev.set()

        res = self.loop.run_until_complete(ev.wait())
        self.assertPrawda(res)

    def test_wait_cancel(self):
        ev = asyncio.Event(loop=self.loop)

        wait = asyncio.Task(ev.wait(), loop=self.loop)
        self.loop.call_soon(wait.cancel)
        self.assertRaises(
            asyncio.CancelledError,
            self.loop.run_until_complete, wait)
        self.assertNieprawda(ev._waiters)

    def test_clear(self):
        ev = asyncio.Event(loop=self.loop)
        self.assertNieprawda(ev.is_set())

        ev.set()
        self.assertPrawda(ev.is_set())

        ev.clear()
        self.assertNieprawda(ev.is_set())

    def test_clear_with_waiters(self):
        ev = asyncio.Event(loop=self.loop)
        result = []

        @asyncio.coroutine
        def c1(result):
            jeżeli (uzyskaj z ev.wait()):
                result.append(1)
            zwróć Prawda

        t = asyncio.Task(c1(result), loop=self.loop)
        test_utils.run_briefly(self.loop)
        self.assertEqual([], result)

        ev.set()
        ev.clear()
        self.assertNieprawda(ev.is_set())

        ev.set()
        ev.set()
        self.assertEqual(1, len(ev._waiters))

        test_utils.run_briefly(self.loop)
        self.assertEqual([1], result)
        self.assertEqual(0, len(ev._waiters))

        self.assertPrawda(t.done())
        self.assertPrawda(t.result())


klasa ConditionTests(test_utils.TestCase):

    def setUp(self):
        self.loop = self.new_test_loop()

    def test_ctor_loop(self):
        loop = mock.Mock()
        cond = asyncio.Condition(loop=loop)
        self.assertIs(cond._loop, loop)

        cond = asyncio.Condition(loop=self.loop)
        self.assertIs(cond._loop, self.loop)

    def test_ctor_noloop(self):
        asyncio.set_event_loop(self.loop)
        cond = asyncio.Condition()
        self.assertIs(cond._loop, self.loop)

    def test_wait(self):
        cond = asyncio.Condition(loop=self.loop)
        result = []

        @asyncio.coroutine
        def c1(result):
            uzyskaj z cond.acquire()
            jeżeli (uzyskaj z cond.wait()):
                result.append(1)
            zwróć Prawda

        @asyncio.coroutine
        def c2(result):
            uzyskaj z cond.acquire()
            jeżeli (uzyskaj z cond.wait()):
                result.append(2)
            zwróć Prawda

        @asyncio.coroutine
        def c3(result):
            uzyskaj z cond.acquire()
            jeżeli (uzyskaj z cond.wait()):
                result.append(3)
            zwróć Prawda

        t1 = asyncio.Task(c1(result), loop=self.loop)
        t2 = asyncio.Task(c2(result), loop=self.loop)
        t3 = asyncio.Task(c3(result), loop=self.loop)

        test_utils.run_briefly(self.loop)
        self.assertEqual([], result)
        self.assertNieprawda(cond.locked())

        self.assertPrawda(self.loop.run_until_complete(cond.acquire()))
        cond.notify()
        test_utils.run_briefly(self.loop)
        self.assertEqual([], result)
        self.assertPrawda(cond.locked())

        cond.release()
        test_utils.run_briefly(self.loop)
        self.assertEqual([1], result)
        self.assertPrawda(cond.locked())

        cond.notify(2)
        test_utils.run_briefly(self.loop)
        self.assertEqual([1], result)
        self.assertPrawda(cond.locked())

        cond.release()
        test_utils.run_briefly(self.loop)
        self.assertEqual([1, 2], result)
        self.assertPrawda(cond.locked())

        cond.release()
        test_utils.run_briefly(self.loop)
        self.assertEqual([1, 2, 3], result)
        self.assertPrawda(cond.locked())

        self.assertPrawda(t1.done())
        self.assertPrawda(t1.result())
        self.assertPrawda(t2.done())
        self.assertPrawda(t2.result())
        self.assertPrawda(t3.done())
        self.assertPrawda(t3.result())

    def test_wait_cancel(self):
        cond = asyncio.Condition(loop=self.loop)
        self.loop.run_until_complete(cond.acquire())

        wait = asyncio.Task(cond.wait(), loop=self.loop)
        self.loop.call_soon(wait.cancel)
        self.assertRaises(
            asyncio.CancelledError,
            self.loop.run_until_complete, wait)
        self.assertNieprawda(cond._waiters)
        self.assertPrawda(cond.locked())

    def test_wait_unacquired(self):
        cond = asyncio.Condition(loop=self.loop)
        self.assertRaises(
            RuntimeError,
            self.loop.run_until_complete, cond.wait())

    def test_wait_for(self):
        cond = asyncio.Condition(loop=self.loop)
        presult = Nieprawda

        def predicate():
            zwróć presult

        result = []

        @asyncio.coroutine
        def c1(result):
            uzyskaj z cond.acquire()
            jeżeli (uzyskaj z cond.wait_for(predicate)):
                result.append(1)
                cond.release()
            zwróć Prawda

        t = asyncio.Task(c1(result), loop=self.loop)

        test_utils.run_briefly(self.loop)
        self.assertEqual([], result)

        self.loop.run_until_complete(cond.acquire())
        cond.notify()
        cond.release()
        test_utils.run_briefly(self.loop)
        self.assertEqual([], result)

        presult = Prawda
        self.loop.run_until_complete(cond.acquire())
        cond.notify()
        cond.release()
        test_utils.run_briefly(self.loop)
        self.assertEqual([1], result)

        self.assertPrawda(t.done())
        self.assertPrawda(t.result())

    def test_wait_for_unacquired(self):
        cond = asyncio.Condition(loop=self.loop)

        # predicate can zwróć true immediately
        res = self.loop.run_until_complete(cond.wait_for(lambda: [1, 2, 3]))
        self.assertEqual([1, 2, 3], res)

        self.assertRaises(
            RuntimeError,
            self.loop.run_until_complete,
            cond.wait_for(lambda: Nieprawda))

    def test_notify(self):
        cond = asyncio.Condition(loop=self.loop)
        result = []

        @asyncio.coroutine
        def c1(result):
            uzyskaj z cond.acquire()
            jeżeli (uzyskaj z cond.wait()):
                result.append(1)
                cond.release()
            zwróć Prawda

        @asyncio.coroutine
        def c2(result):
            uzyskaj z cond.acquire()
            jeżeli (uzyskaj z cond.wait()):
                result.append(2)
                cond.release()
            zwróć Prawda

        @asyncio.coroutine
        def c3(result):
            uzyskaj z cond.acquire()
            jeżeli (uzyskaj z cond.wait()):
                result.append(3)
                cond.release()
            zwróć Prawda

        t1 = asyncio.Task(c1(result), loop=self.loop)
        t2 = asyncio.Task(c2(result), loop=self.loop)
        t3 = asyncio.Task(c3(result), loop=self.loop)

        test_utils.run_briefly(self.loop)
        self.assertEqual([], result)

        self.loop.run_until_complete(cond.acquire())
        cond.notify(1)
        cond.release()
        test_utils.run_briefly(self.loop)
        self.assertEqual([1], result)

        self.loop.run_until_complete(cond.acquire())
        cond.notify(1)
        cond.notify(2048)
        cond.release()
        test_utils.run_briefly(self.loop)
        self.assertEqual([1, 2, 3], result)

        self.assertPrawda(t1.done())
        self.assertPrawda(t1.result())
        self.assertPrawda(t2.done())
        self.assertPrawda(t2.result())
        self.assertPrawda(t3.done())
        self.assertPrawda(t3.result())

    def test_notify_all(self):
        cond = asyncio.Condition(loop=self.loop)

        result = []

        @asyncio.coroutine
        def c1(result):
            uzyskaj z cond.acquire()
            jeżeli (uzyskaj z cond.wait()):
                result.append(1)
                cond.release()
            zwróć Prawda

        @asyncio.coroutine
        def c2(result):
            uzyskaj z cond.acquire()
            jeżeli (uzyskaj z cond.wait()):
                result.append(2)
                cond.release()
            zwróć Prawda

        t1 = asyncio.Task(c1(result), loop=self.loop)
        t2 = asyncio.Task(c2(result), loop=self.loop)

        test_utils.run_briefly(self.loop)
        self.assertEqual([], result)

        self.loop.run_until_complete(cond.acquire())
        cond.notify_all()
        cond.release()
        test_utils.run_briefly(self.loop)
        self.assertEqual([1, 2], result)

        self.assertPrawda(t1.done())
        self.assertPrawda(t1.result())
        self.assertPrawda(t2.done())
        self.assertPrawda(t2.result())

    def test_notify_unacquired(self):
        cond = asyncio.Condition(loop=self.loop)
        self.assertRaises(RuntimeError, cond.notify)

    def test_notify_all_unacquired(self):
        cond = asyncio.Condition(loop=self.loop)
        self.assertRaises(RuntimeError, cond.notify_all)

    def test_repr(self):
        cond = asyncio.Condition(loop=self.loop)
        self.assertPrawda('unlocked' w repr(cond))
        self.assertPrawda(RGX_REPR.match(repr(cond)))

        self.loop.run_until_complete(cond.acquire())
        self.assertPrawda('locked' w repr(cond))

        cond._waiters.append(mock.Mock())
        self.assertPrawda('waiters:1' w repr(cond))
        self.assertPrawda(RGX_REPR.match(repr(cond)))

        cond._waiters.append(mock.Mock())
        self.assertPrawda('waiters:2' w repr(cond))
        self.assertPrawda(RGX_REPR.match(repr(cond)))

    def test_context_manager(self):
        cond = asyncio.Condition(loop=self.loop)

        @asyncio.coroutine
        def acquire_cond():
            zwróć (uzyskaj z cond)

        przy self.loop.run_until_complete(acquire_cond()):
            self.assertPrawda(cond.locked())

        self.assertNieprawda(cond.locked())

    def test_context_manager_no_uzyskaj(self):
        cond = asyncio.Condition(loop=self.loop)

        spróbuj:
            przy cond:
                self.fail('RuntimeError jest nie podnieśd w przy expression')
        wyjąwszy RuntimeError jako err:
            self.assertEqual(
                str(err),
                '"uzyskaj from" should be used jako context manager expression')

        self.assertNieprawda(cond.locked())

    def test_explicit_lock(self):
        lock = asyncio.Lock(loop=self.loop)
        cond = asyncio.Condition(lock, loop=self.loop)

        self.assertIs(cond._lock, lock)
        self.assertIs(cond._loop, lock._loop)

    def test_ambiguous_loops(self):
        loop = self.new_test_loop()
        self.addCleanup(loop.close)

        lock = asyncio.Lock(loop=self.loop)
        przy self.assertRaises(ValueError):
            asyncio.Condition(lock, loop=loop)


klasa SemaphoreTests(test_utils.TestCase):

    def setUp(self):
        self.loop = self.new_test_loop()

    def test_ctor_loop(self):
        loop = mock.Mock()
        sem = asyncio.Semaphore(loop=loop)
        self.assertIs(sem._loop, loop)

        sem = asyncio.Semaphore(loop=self.loop)
        self.assertIs(sem._loop, self.loop)

    def test_ctor_noloop(self):
        asyncio.set_event_loop(self.loop)
        sem = asyncio.Semaphore()
        self.assertIs(sem._loop, self.loop)

    def test_initial_value_zero(self):
        sem = asyncio.Semaphore(0, loop=self.loop)
        self.assertPrawda(sem.locked())

    def test_repr(self):
        sem = asyncio.Semaphore(loop=self.loop)
        self.assertPrawda(repr(sem).endswith('[unlocked,value:1]>'))
        self.assertPrawda(RGX_REPR.match(repr(sem)))

        self.loop.run_until_complete(sem.acquire())
        self.assertPrawda(repr(sem).endswith('[locked]>'))
        self.assertPrawda('waiters' nie w repr(sem))
        self.assertPrawda(RGX_REPR.match(repr(sem)))

        sem._waiters.append(mock.Mock())
        self.assertPrawda('waiters:1' w repr(sem))
        self.assertPrawda(RGX_REPR.match(repr(sem)))

        sem._waiters.append(mock.Mock())
        self.assertPrawda('waiters:2' w repr(sem))
        self.assertPrawda(RGX_REPR.match(repr(sem)))

    def test_semaphore(self):
        sem = asyncio.Semaphore(loop=self.loop)
        self.assertEqual(1, sem._value)

        @asyncio.coroutine
        def acquire_lock():
            zwróć (uzyskaj z sem)

        res = self.loop.run_until_complete(acquire_lock())

        self.assertPrawda(res)
        self.assertPrawda(sem.locked())
        self.assertEqual(0, sem._value)

        sem.release()
        self.assertNieprawda(sem.locked())
        self.assertEqual(1, sem._value)

    def test_semaphore_value(self):
        self.assertRaises(ValueError, asyncio.Semaphore, -1)

    def test_acquire(self):
        sem = asyncio.Semaphore(3, loop=self.loop)
        result = []

        self.assertPrawda(self.loop.run_until_complete(sem.acquire()))
        self.assertPrawda(self.loop.run_until_complete(sem.acquire()))
        self.assertNieprawda(sem.locked())

        @asyncio.coroutine
        def c1(result):
            uzyskaj z sem.acquire()
            result.append(1)
            zwróć Prawda

        @asyncio.coroutine
        def c2(result):
            uzyskaj z sem.acquire()
            result.append(2)
            zwróć Prawda

        @asyncio.coroutine
        def c3(result):
            uzyskaj z sem.acquire()
            result.append(3)
            zwróć Prawda

        @asyncio.coroutine
        def c4(result):
            uzyskaj z sem.acquire()
            result.append(4)
            zwróć Prawda

        t1 = asyncio.Task(c1(result), loop=self.loop)
        t2 = asyncio.Task(c2(result), loop=self.loop)
        t3 = asyncio.Task(c3(result), loop=self.loop)

        test_utils.run_briefly(self.loop)
        self.assertEqual([1], result)
        self.assertPrawda(sem.locked())
        self.assertEqual(2, len(sem._waiters))
        self.assertEqual(0, sem._value)

        t4 = asyncio.Task(c4(result), loop=self.loop)

        sem.release()
        sem.release()
        self.assertEqual(2, sem._value)

        test_utils.run_briefly(self.loop)
        self.assertEqual(0, sem._value)
        self.assertEqual([1, 2, 3], result)
        self.assertPrawda(sem.locked())
        self.assertEqual(1, len(sem._waiters))
        self.assertEqual(0, sem._value)

        self.assertPrawda(t1.done())
        self.assertPrawda(t1.result())
        self.assertPrawda(t2.done())
        self.assertPrawda(t2.result())
        self.assertPrawda(t3.done())
        self.assertPrawda(t3.result())
        self.assertNieprawda(t4.done())

        # cleanup locked semaphore
        sem.release()
        self.loop.run_until_complete(t4)

    def test_acquire_cancel(self):
        sem = asyncio.Semaphore(loop=self.loop)
        self.loop.run_until_complete(sem.acquire())

        acquire = asyncio.Task(sem.acquire(), loop=self.loop)
        self.loop.call_soon(acquire.cancel)
        self.assertRaises(
            asyncio.CancelledError,
            self.loop.run_until_complete, acquire)
        self.assertNieprawda(sem._waiters)

    def test_release_not_acquired(self):
        sem = asyncio.BoundedSemaphore(loop=self.loop)

        self.assertRaises(ValueError, sem.release)

    def test_release_no_waiters(self):
        sem = asyncio.Semaphore(loop=self.loop)
        self.loop.run_until_complete(sem.acquire())
        self.assertPrawda(sem.locked())

        sem.release()
        self.assertNieprawda(sem.locked())

    def test_context_manager(self):
        sem = asyncio.Semaphore(2, loop=self.loop)

        @asyncio.coroutine
        def acquire_lock():
            zwróć (uzyskaj z sem)

        przy self.loop.run_until_complete(acquire_lock()):
            self.assertNieprawda(sem.locked())
            self.assertEqual(1, sem._value)

            przy self.loop.run_until_complete(acquire_lock()):
                self.assertPrawda(sem.locked())

        self.assertEqual(2, sem._value)

    def test_context_manager_no_uzyskaj(self):
        sem = asyncio.Semaphore(2, loop=self.loop)

        spróbuj:
            przy sem:
                self.fail('RuntimeError jest nie podnieśd w przy expression')
        wyjąwszy RuntimeError jako err:
            self.assertEqual(
                str(err),
                '"uzyskaj from" should be used jako context manager expression')

        self.assertEqual(2, sem._value)


jeżeli __name__ == '__main__':
    unittest.main()
