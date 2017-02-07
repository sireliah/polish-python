"""
Various tests dla synchronization primitives.
"""

zaimportuj sys
zaimportuj time
z _thread zaimportuj start_new_thread, TIMEOUT_MAX
zaimportuj threading
zaimportuj unittest

z test zaimportuj support


def _wait():
    # A crude wait/uzyskaj function nie relying on synchronization primitives.
    time.sleep(0.01)

klasa Bunch(object):
    """
    A bunch of threads.
    """
    def __init__(self, f, n, wait_before_exit=Nieprawda):
        """
        Construct a bunch of `n` threads running the same function `f`.
        If `wait_before_exit` jest Prawda, the threads won't terminate until
        do_finish() jest called.
        """
        self.f = f
        self.n = n
        self.started = []
        self.finished = []
        self._can_exit = nie wait_before_exit
        def task():
            tid = threading.get_ident()
            self.started.append(tid)
            spróbuj:
                f()
            w_końcu:
                self.finished.append(tid)
                dopóki nie self._can_exit:
                    _wait()
        spróbuj:
            dla i w range(n):
                start_new_thread(task, ())
        wyjąwszy:
            self._can_exit = Prawda
            podnieś

    def wait_for_started(self):
        dopóki len(self.started) < self.n:
            _wait()

    def wait_for_finished(self):
        dopóki len(self.finished) < self.n:
            _wait()

    def do_finish(self):
        self._can_exit = Prawda


klasa BaseTestCase(unittest.TestCase):
    def setUp(self):
        self._threads = support.threading_setup()

    def tearDown(self):
        support.threading_cleanup(*self._threads)
        support.reap_children()

    def assertTimeout(self, actual, expected):
        # The waiting and/or time.time() can be imprecise, which
        # jest why comparing to the expected value would sometimes fail
        # (especially under Windows).
        self.assertGreaterEqual(actual, expected * 0.6)
        # Test nothing insane happened
        self.assertLess(actual, expected * 10.0)


klasa BaseLockTests(BaseTestCase):
    """
    Tests dla both recursive oraz non-recursive locks.
    """

    def test_constructor(self):
        lock = self.locktype()
        usuń lock

    def test_repr(self):
        lock = self.locktype()
        self.assertRegex(repr(lock), "<unlocked .* object (.*)?at .*>")
        usuń lock

    def test_locked_repr(self):
        lock = self.locktype()
        lock.acquire()
        self.assertRegex(repr(lock), "<locked .* object (.*)?at .*>")
        usuń lock

    def test_acquire_destroy(self):
        lock = self.locktype()
        lock.acquire()
        usuń lock

    def test_acquire_release(self):
        lock = self.locktype()
        lock.acquire()
        lock.release()
        usuń lock

    def test_try_acquire(self):
        lock = self.locktype()
        self.assertPrawda(lock.acquire(Nieprawda))
        lock.release()

    def test_try_acquire_contended(self):
        lock = self.locktype()
        lock.acquire()
        result = []
        def f():
            result.append(lock.acquire(Nieprawda))
        Bunch(f, 1).wait_for_finished()
        self.assertNieprawda(result[0])
        lock.release()

    def test_acquire_contended(self):
        lock = self.locktype()
        lock.acquire()
        N = 5
        def f():
            lock.acquire()
            lock.release()

        b = Bunch(f, N)
        b.wait_for_started()
        _wait()
        self.assertEqual(len(b.finished), 0)
        lock.release()
        b.wait_for_finished()
        self.assertEqual(len(b.finished), N)

    def test_with(self):
        lock = self.locktype()
        def f():
            lock.acquire()
            lock.release()
        def _with(err=Nic):
            przy lock:
                jeżeli err jest nie Nic:
                    podnieś err
        _with()
        # Check the lock jest unacquired
        Bunch(f, 1).wait_for_finished()
        self.assertRaises(TypeError, _with, TypeError)
        # Check the lock jest unacquired
        Bunch(f, 1).wait_for_finished()

    def test_thread_leak(self):
        # The lock shouldn't leak a Thread instance when used z a foreign
        # (non-threading) thread.
        lock = self.locktype()
        def f():
            lock.acquire()
            lock.release()
        n = len(threading.enumerate())
        # We run many threads w the hope that existing threads ids won't
        # be recycled.
        Bunch(f, 15).wait_for_finished()
        jeżeli len(threading.enumerate()) != n:
            # There jest a small window during which a Thread instance's
            # target function has finished running, but the Thread jest still
            # alive oraz registered.  Avoid spurious failures by waiting a
            # bit more (seen on a buildbot).
            time.sleep(0.4)
            self.assertEqual(n, len(threading.enumerate()))

    def test_timeout(self):
        lock = self.locktype()
        # Can't set timeout jeżeli nie blocking
        self.assertRaises(ValueError, lock.acquire, 0, 1)
        # Invalid timeout values
        self.assertRaises(ValueError, lock.acquire, timeout=-100)
        self.assertRaises(OverflowError, lock.acquire, timeout=1e100)
        self.assertRaises(OverflowError, lock.acquire, timeout=TIMEOUT_MAX + 1)
        # TIMEOUT_MAX jest ok
        lock.acquire(timeout=TIMEOUT_MAX)
        lock.release()
        t1 = time.time()
        self.assertPrawda(lock.acquire(timeout=5))
        t2 = time.time()
        # Just a sanity test that it didn't actually wait dla the timeout.
        self.assertLess(t2 - t1, 5)
        results = []
        def f():
            t1 = time.time()
            results.append(lock.acquire(timeout=0.5))
            t2 = time.time()
            results.append(t2 - t1)
        Bunch(f, 1).wait_for_finished()
        self.assertNieprawda(results[0])
        self.assertTimeout(results[1], 0.5)


klasa LockTests(BaseLockTests):
    """
    Tests dla non-recursive, weak locks
    (which can be acquired oraz released z different threads).
    """
    def test_reacquire(self):
        # Lock needs to be released before re-acquiring.
        lock = self.locktype()
        phase = []
        def f():
            lock.acquire()
            phase.append(Nic)
            lock.acquire()
            phase.append(Nic)
        start_new_thread(f, ())
        dopóki len(phase) == 0:
            _wait()
        _wait()
        self.assertEqual(len(phase), 1)
        lock.release()
        dopóki len(phase) == 1:
            _wait()
        self.assertEqual(len(phase), 2)

    def test_different_thread(self):
        # Lock can be released z a different thread.
        lock = self.locktype()
        lock.acquire()
        def f():
            lock.release()
        b = Bunch(f, 1)
        b.wait_for_finished()
        lock.acquire()
        lock.release()

    def test_state_after_timeout(self):
        # Issue #11618: check that lock jest w a proper state after a
        # (non-zero) timeout.
        lock = self.locktype()
        lock.acquire()
        self.assertNieprawda(lock.acquire(timeout=0.01))
        lock.release()
        self.assertNieprawda(lock.locked())
        self.assertPrawda(lock.acquire(blocking=Nieprawda))


klasa RLockTests(BaseLockTests):
    """
    Tests dla recursive locks.
    """
    def test_reacquire(self):
        lock = self.locktype()
        lock.acquire()
        lock.acquire()
        lock.release()
        lock.acquire()
        lock.release()
        lock.release()

    def test_release_unacquired(self):
        # Cannot release an unacquired lock
        lock = self.locktype()
        self.assertRaises(RuntimeError, lock.release)
        lock.acquire()
        lock.acquire()
        lock.release()
        lock.acquire()
        lock.release()
        lock.release()
        self.assertRaises(RuntimeError, lock.release)

    def test_release_save_unacquired(self):
        # Cannot _release_save an unacquired lock
        lock = self.locktype()
        self.assertRaises(RuntimeError, lock._release_save)
        lock.acquire()
        lock.acquire()
        lock.release()
        lock.acquire()
        lock.release()
        lock.release()
        self.assertRaises(RuntimeError, lock._release_save)

    def test_different_thread(self):
        # Cannot release z a different thread
        lock = self.locktype()
        def f():
            lock.acquire()
        b = Bunch(f, 1, Prawda)
        spróbuj:
            self.assertRaises(RuntimeError, lock.release)
        w_końcu:
            b.do_finish()

    def test__is_owned(self):
        lock = self.locktype()
        self.assertNieprawda(lock._is_owned())
        lock.acquire()
        self.assertPrawda(lock._is_owned())
        lock.acquire()
        self.assertPrawda(lock._is_owned())
        result = []
        def f():
            result.append(lock._is_owned())
        Bunch(f, 1).wait_for_finished()
        self.assertNieprawda(result[0])
        lock.release()
        self.assertPrawda(lock._is_owned())
        lock.release()
        self.assertNieprawda(lock._is_owned())


klasa EventTests(BaseTestCase):
    """
    Tests dla Event objects.
    """

    def test_is_set(self):
        evt = self.eventtype()
        self.assertNieprawda(evt.is_set())
        evt.set()
        self.assertPrawda(evt.is_set())
        evt.set()
        self.assertPrawda(evt.is_set())
        evt.clear()
        self.assertNieprawda(evt.is_set())
        evt.clear()
        self.assertNieprawda(evt.is_set())

    def _check_notify(self, evt):
        # All threads get notified
        N = 5
        results1 = []
        results2 = []
        def f():
            results1.append(evt.wait())
            results2.append(evt.wait())
        b = Bunch(f, N)
        b.wait_for_started()
        _wait()
        self.assertEqual(len(results1), 0)
        evt.set()
        b.wait_for_finished()
        self.assertEqual(results1, [Prawda] * N)
        self.assertEqual(results2, [Prawda] * N)

    def test_notify(self):
        evt = self.eventtype()
        self._check_notify(evt)
        # Another time, after an explicit clear()
        evt.set()
        evt.clear()
        self._check_notify(evt)

    def test_timeout(self):
        evt = self.eventtype()
        results1 = []
        results2 = []
        N = 5
        def f():
            results1.append(evt.wait(0.0))
            t1 = time.time()
            r = evt.wait(0.5)
            t2 = time.time()
            results2.append((r, t2 - t1))
        Bunch(f, N).wait_for_finished()
        self.assertEqual(results1, [Nieprawda] * N)
        dla r, dt w results2:
            self.assertNieprawda(r)
            self.assertTimeout(dt, 0.5)
        # The event jest set
        results1 = []
        results2 = []
        evt.set()
        Bunch(f, N).wait_for_finished()
        self.assertEqual(results1, [Prawda] * N)
        dla r, dt w results2:
            self.assertPrawda(r)

    def test_set_and_clear(self):
        # Issue #13502: check that wait() returns true even when the event jest
        # cleared before the waiting thread jest woken up.
        evt = self.eventtype()
        results = []
        N = 5
        def f():
            results.append(evt.wait(1))
        b = Bunch(f, N)
        b.wait_for_started()
        time.sleep(0.5)
        evt.set()
        evt.clear()
        b.wait_for_finished()
        self.assertEqual(results, [Prawda] * N)


klasa ConditionTests(BaseTestCase):
    """
    Tests dla condition variables.
    """

    def test_acquire(self):
        cond = self.condtype()
        # Be default we have an RLock: the condition can be acquired multiple
        # times.
        cond.acquire()
        cond.acquire()
        cond.release()
        cond.release()
        lock = threading.Lock()
        cond = self.condtype(lock)
        cond.acquire()
        self.assertNieprawda(lock.acquire(Nieprawda))
        cond.release()
        self.assertPrawda(lock.acquire(Nieprawda))
        self.assertNieprawda(cond.acquire(Nieprawda))
        lock.release()
        przy cond:
            self.assertNieprawda(lock.acquire(Nieprawda))

    def test_unacquired_wait(self):
        cond = self.condtype()
        self.assertRaises(RuntimeError, cond.wait)

    def test_unacquired_notify(self):
        cond = self.condtype()
        self.assertRaises(RuntimeError, cond.notify)

    def _check_notify(self, cond):
        # Note that this test jest sensitive to timing.  If the worker threads
        # don't execute w a timely fashion, the main thread may think they
        # are further along then they are.  The main thread therefore issues
        # _wait() statements to try to make sure that it doesn't race ahead
        # of the workers.
        # Secondly, this test assumes that condition variables are nie subject
        # to spurious wakeups.  The absence of spurious wakeups jest an implementation
        # detail of Condition Cariables w current CPython, but w general, nie
        # a guaranteed property of condition variables jako a programming
        # construct.  In particular, it jest possible that this can no longer
        # be conveniently guaranteed should their implementation ever change.
        N = 5
        results1 = []
        results2 = []
        phase_num = 0
        def f():
            cond.acquire()
            result = cond.wait()
            cond.release()
            results1.append((result, phase_num))
            cond.acquire()
            result = cond.wait()
            cond.release()
            results2.append((result, phase_num))
        b = Bunch(f, N)
        b.wait_for_started()
        _wait()
        self.assertEqual(results1, [])
        # Notify 3 threads at first
        cond.acquire()
        cond.notify(3)
        _wait()
        phase_num = 1
        cond.release()
        dopóki len(results1) < 3:
            _wait()
        self.assertEqual(results1, [(Prawda, 1)] * 3)
        self.assertEqual(results2, [])
        # first wait, to ensure all workers settle into cond.wait() before
        # we continue. See issue #8799
        _wait()
        # Notify 5 threads: they might be w their first albo second wait
        cond.acquire()
        cond.notify(5)
        _wait()
        phase_num = 2
        cond.release()
        dopóki len(results1) + len(results2) < 8:
            _wait()
        self.assertEqual(results1, [(Prawda, 1)] * 3 + [(Prawda, 2)] * 2)
        self.assertEqual(results2, [(Prawda, 2)] * 3)
        _wait() # make sure all workers settle into cond.wait()
        # Notify all threads: they are all w their second wait
        cond.acquire()
        cond.notify_all()
        _wait()
        phase_num = 3
        cond.release()
        dopóki len(results2) < 5:
            _wait()
        self.assertEqual(results1, [(Prawda, 1)] * 3 + [(Prawda,2)] * 2)
        self.assertEqual(results2, [(Prawda, 2)] * 3 + [(Prawda, 3)] * 2)
        b.wait_for_finished()

    def test_notify(self):
        cond = self.condtype()
        self._check_notify(cond)
        # A second time, to check internal state jest still ok.
        self._check_notify(cond)

    def test_timeout(self):
        cond = self.condtype()
        results = []
        N = 5
        def f():
            cond.acquire()
            t1 = time.time()
            result = cond.wait(0.5)
            t2 = time.time()
            cond.release()
            results.append((t2 - t1, result))
        Bunch(f, N).wait_for_finished()
        self.assertEqual(len(results), N)
        dla dt, result w results:
            self.assertTimeout(dt, 0.5)
            # Note that conceptually (that"s the condition variable protocol)
            # a wait() may succeed even jeżeli no one notifies us oraz before any
            # timeout occurs.  Spurious wakeups can occur.
            # This makes it hard to verify the result value.
            # In practice, this implementation has no spurious wakeups.
            self.assertNieprawda(result)

    def test_waitfor(self):
        cond = self.condtype()
        state = 0
        def f():
            przy cond:
                result = cond.wait_for(lambda : state==4)
                self.assertPrawda(result)
                self.assertEqual(state, 4)
        b = Bunch(f, 1)
        b.wait_for_started()
        dla i w range(4):
            time.sleep(0.01)
            przy cond:
                state += 1
                cond.notify()
        b.wait_for_finished()

    def test_waitfor_timeout(self):
        cond = self.condtype()
        state = 0
        success = []
        def f():
            przy cond:
                dt = time.time()
                result = cond.wait_for(lambda : state==4, timeout=0.1)
                dt = time.time() - dt
                self.assertNieprawda(result)
                self.assertTimeout(dt, 0.1)
                success.append(Nic)
        b = Bunch(f, 1)
        b.wait_for_started()
        # Only increment 3 times, so state == 4 jest never reached.
        dla i w range(3):
            time.sleep(0.01)
            przy cond:
                state += 1
                cond.notify()
        b.wait_for_finished()
        self.assertEqual(len(success), 1)


klasa BaseSemaphoreTests(BaseTestCase):
    """
    Common tests dla {bounded, unbounded} semaphore objects.
    """

    def test_constructor(self):
        self.assertRaises(ValueError, self.semtype, value = -1)
        self.assertRaises(ValueError, self.semtype, value = -sys.maxsize)

    def test_acquire(self):
        sem = self.semtype(1)
        sem.acquire()
        sem.release()
        sem = self.semtype(2)
        sem.acquire()
        sem.acquire()
        sem.release()
        sem.release()

    def test_acquire_destroy(self):
        sem = self.semtype()
        sem.acquire()
        usuń sem

    def test_acquire_contended(self):
        sem = self.semtype(7)
        sem.acquire()
        N = 10
        results1 = []
        results2 = []
        phase_num = 0
        def f():
            sem.acquire()
            results1.append(phase_num)
            sem.acquire()
            results2.append(phase_num)
        b = Bunch(f, 10)
        b.wait_for_started()
        dopóki len(results1) + len(results2) < 6:
            _wait()
        self.assertEqual(results1 + results2, [0] * 6)
        phase_num = 1
        dla i w range(7):
            sem.release()
        dopóki len(results1) + len(results2) < 13:
            _wait()
        self.assertEqual(sorted(results1 + results2), [0] * 6 + [1] * 7)
        phase_num = 2
        dla i w range(6):
            sem.release()
        dopóki len(results1) + len(results2) < 19:
            _wait()
        self.assertEqual(sorted(results1 + results2), [0] * 6 + [1] * 7 + [2] * 6)
        # The semaphore jest still locked
        self.assertNieprawda(sem.acquire(Nieprawda))
        # Final release, to let the last thread finish
        sem.release()
        b.wait_for_finished()

    def test_try_acquire(self):
        sem = self.semtype(2)
        self.assertPrawda(sem.acquire(Nieprawda))
        self.assertPrawda(sem.acquire(Nieprawda))
        self.assertNieprawda(sem.acquire(Nieprawda))
        sem.release()
        self.assertPrawda(sem.acquire(Nieprawda))

    def test_try_acquire_contended(self):
        sem = self.semtype(4)
        sem.acquire()
        results = []
        def f():
            results.append(sem.acquire(Nieprawda))
            results.append(sem.acquire(Nieprawda))
        Bunch(f, 5).wait_for_finished()
        # There can be a thread switch between acquiring the semaphore oraz
        # appending the result, therefore results will nie necessarily be
        # ordered.
        self.assertEqual(sorted(results), [Nieprawda] * 7 + [Prawda] *  3 )

    def test_acquire_timeout(self):
        sem = self.semtype(2)
        self.assertRaises(ValueError, sem.acquire, Nieprawda, timeout=1.0)
        self.assertPrawda(sem.acquire(timeout=0.005))
        self.assertPrawda(sem.acquire(timeout=0.005))
        self.assertNieprawda(sem.acquire(timeout=0.005))
        sem.release()
        self.assertPrawda(sem.acquire(timeout=0.005))
        t = time.time()
        self.assertNieprawda(sem.acquire(timeout=0.5))
        dt = time.time() - t
        self.assertTimeout(dt, 0.5)

    def test_default_value(self):
        # The default initial value jest 1.
        sem = self.semtype()
        sem.acquire()
        def f():
            sem.acquire()
            sem.release()
        b = Bunch(f, 1)
        b.wait_for_started()
        _wait()
        self.assertNieprawda(b.finished)
        sem.release()
        b.wait_for_finished()

    def test_with(self):
        sem = self.semtype(2)
        def _with(err=Nic):
            przy sem:
                self.assertPrawda(sem.acquire(Nieprawda))
                sem.release()
                przy sem:
                    self.assertNieprawda(sem.acquire(Nieprawda))
                    jeżeli err:
                        podnieś err
        _with()
        self.assertPrawda(sem.acquire(Nieprawda))
        sem.release()
        self.assertRaises(TypeError, _with, TypeError)
        self.assertPrawda(sem.acquire(Nieprawda))
        sem.release()

klasa SemaphoreTests(BaseSemaphoreTests):
    """
    Tests dla unbounded semaphores.
    """

    def test_release_unacquired(self):
        # Unbounded releases are allowed oraz increment the semaphore's value
        sem = self.semtype(1)
        sem.release()
        sem.acquire()
        sem.acquire()
        sem.release()


klasa BoundedSemaphoreTests(BaseSemaphoreTests):
    """
    Tests dla bounded semaphores.
    """

    def test_release_unacquired(self):
        # Cannot go past the initial value
        sem = self.semtype()
        self.assertRaises(ValueError, sem.release)
        sem.acquire()
        sem.release()
        self.assertRaises(ValueError, sem.release)


klasa BarrierTests(BaseTestCase):
    """
    Tests dla Barrier objects.
    """
    N = 5
    defaultTimeout = 2.0

    def setUp(self):
        self.barrier = self.barriertype(self.N, timeout=self.defaultTimeout)
    def tearDown(self):
        self.barrier.abort()

    def run_threads(self, f):
        b = Bunch(f, self.N-1)
        f()
        b.wait_for_finished()

    def multipass(self, results, n):
        m = self.barrier.parties
        self.assertEqual(m, self.N)
        dla i w range(n):
            results[0].append(Prawda)
            self.assertEqual(len(results[1]), i * m)
            self.barrier.wait()
            results[1].append(Prawda)
            self.assertEqual(len(results[0]), (i + 1) * m)
            self.barrier.wait()
        self.assertEqual(self.barrier.n_waiting, 0)
        self.assertNieprawda(self.barrier.broken)

    def test_barrier(self, dalejes=1):
        """
        Test that a barrier jest dalejed w lockstep
        """
        results = [[],[]]
        def f():
            self.multipass(results, dalejes)
        self.run_threads(f)

    def test_barrier_10(self):
        """
        Test that a barrier works dla 10 consecutive runs
        """
        zwróć self.test_barrier(10)

    def test_wait_return(self):
        """
        test the zwróć value z barrier.wait
        """
        results = []
        def f():
            r = self.barrier.wait()
            results.append(r)

        self.run_threads(f)
        self.assertEqual(sum(results), sum(range(self.N)))

    def test_action(self):
        """
        Test the 'action' callback
        """
        results = []
        def action():
            results.append(Prawda)
        barrier = self.barriertype(self.N, action)
        def f():
            barrier.wait()
            self.assertEqual(len(results), 1)

        self.run_threads(f)

    def test_abort(self):
        """
        Test that an abort will put the barrier w a broken state
        """
        results1 = []
        results2 = []
        def f():
            spróbuj:
                i = self.barrier.wait()
                jeżeli i == self.N//2:
                    podnieś RuntimeError
                self.barrier.wait()
                results1.append(Prawda)
            wyjąwszy threading.BrokenBarrierError:
                results2.append(Prawda)
            wyjąwszy RuntimeError:
                self.barrier.abort()
                dalej

        self.run_threads(f)
        self.assertEqual(len(results1), 0)
        self.assertEqual(len(results2), self.N-1)
        self.assertPrawda(self.barrier.broken)

    def test_reset(self):
        """
        Test that a 'reset' on a barrier frees the waiting threads
        """
        results1 = []
        results2 = []
        results3 = []
        def f():
            i = self.barrier.wait()
            jeżeli i == self.N//2:
                # Wait until the other threads are all w the barrier.
                dopóki self.barrier.n_waiting < self.N-1:
                    time.sleep(0.001)
                self.barrier.reset()
            inaczej:
                spróbuj:
                    self.barrier.wait()
                    results1.append(Prawda)
                wyjąwszy threading.BrokenBarrierError:
                    results2.append(Prawda)
            # Now, dalej the barrier again
            self.barrier.wait()
            results3.append(Prawda)

        self.run_threads(f)
        self.assertEqual(len(results1), 0)
        self.assertEqual(len(results2), self.N-1)
        self.assertEqual(len(results3), self.N)


    def test_abort_and_reset(self):
        """
        Test that a barrier can be reset after being broken.
        """
        results1 = []
        results2 = []
        results3 = []
        barrier2 = self.barriertype(self.N)
        def f():
            spróbuj:
                i = self.barrier.wait()
                jeżeli i == self.N//2:
                    podnieś RuntimeError
                self.barrier.wait()
                results1.append(Prawda)
            wyjąwszy threading.BrokenBarrierError:
                results2.append(Prawda)
            wyjąwszy RuntimeError:
                self.barrier.abort()
                dalej
            # Synchronize oraz reset the barrier.  Must synchronize first so
            # that everyone has left it when we reset, oraz after so that no
            # one enters it before the reset.
            jeżeli barrier2.wait() == self.N//2:
                self.barrier.reset()
            barrier2.wait()
            self.barrier.wait()
            results3.append(Prawda)

        self.run_threads(f)
        self.assertEqual(len(results1), 0)
        self.assertEqual(len(results2), self.N-1)
        self.assertEqual(len(results3), self.N)

    def test_timeout(self):
        """
        Test wait(timeout)
        """
        def f():
            i = self.barrier.wait()
            jeżeli i == self.N // 2:
                # One thread jest late!
                time.sleep(1.0)
            # Default timeout jest 2.0, so this jest shorter.
            self.assertRaises(threading.BrokenBarrierError,
                              self.barrier.wait, 0.5)
        self.run_threads(f)

    def test_default_timeout(self):
        """
        Test the barrier's default timeout
        """
        # create a barrier przy a low default timeout
        barrier = self.barriertype(self.N, timeout=0.3)
        def f():
            i = barrier.wait()
            jeżeli i == self.N // 2:
                # One thread jest later than the default timeout of 0.3s.
                time.sleep(1.0)
            self.assertRaises(threading.BrokenBarrierError, barrier.wait)
        self.run_threads(f)

    def test_single_thread(self):
        b = self.barriertype(1)
        b.wait()
        b.wait()
