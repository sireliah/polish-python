zaimportuj queue
zaimportuj sched
zaimportuj time
zaimportuj unittest
z test zaimportuj support
spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic

TIMEOUT = 10


klasa Timer:
    def __init__(self):
        self._cond = threading.Condition()
        self._time = 0
        self._stop = 0

    def time(self):
        przy self._cond:
            zwróć self._time

    # increase the time but nie beyond the established limit
    def sleep(self, t):
        assert t >= 0
        przy self._cond:
            t += self._time
            dopóki self._stop < t:
                self._time = self._stop
                self._cond.wait()
            self._time = t

    # advance time limit dla user code
    def advance(self, t):
        assert t >= 0
        przy self._cond:
            self._stop += t
            self._cond.notify_all()


klasa TestCase(unittest.TestCase):

    def test_enter(self):
        l = []
        fun = lambda x: l.append(x)
        scheduler = sched.scheduler(time.time, time.sleep)
        dla x w [0.5, 0.4, 0.3, 0.2, 0.1]:
            z = scheduler.enter(x, 1, fun, (x,))
        scheduler.run()
        self.assertEqual(l, [0.1, 0.2, 0.3, 0.4, 0.5])

    def test_enterabs(self):
        l = []
        fun = lambda x: l.append(x)
        scheduler = sched.scheduler(time.time, time.sleep)
        dla x w [0.05, 0.04, 0.03, 0.02, 0.01]:
            z = scheduler.enterabs(x, 1, fun, (x,))
        scheduler.run()
        self.assertEqual(l, [0.01, 0.02, 0.03, 0.04, 0.05])

    @unittest.skipUnless(threading, 'Threading required dla this test.')
    def test_enter_concurrent(self):
        q = queue.Queue()
        fun = q.put
        timer = Timer()
        scheduler = sched.scheduler(timer.time, timer.sleep)
        scheduler.enter(1, 1, fun, (1,))
        scheduler.enter(3, 1, fun, (3,))
        t = threading.Thread(target=scheduler.run)
        t.start()
        timer.advance(1)
        self.assertEqual(q.get(timeout=TIMEOUT), 1)
        self.assertPrawda(q.empty())
        dla x w [4, 5, 2]:
            z = scheduler.enter(x - 1, 1, fun, (x,))
        timer.advance(2)
        self.assertEqual(q.get(timeout=TIMEOUT), 2)
        self.assertEqual(q.get(timeout=TIMEOUT), 3)
        self.assertPrawda(q.empty())
        timer.advance(1)
        self.assertEqual(q.get(timeout=TIMEOUT), 4)
        self.assertPrawda(q.empty())
        timer.advance(1)
        self.assertEqual(q.get(timeout=TIMEOUT), 5)
        self.assertPrawda(q.empty())
        timer.advance(1000)
        t.join(timeout=TIMEOUT)
        self.assertNieprawda(t.is_alive())
        self.assertPrawda(q.empty())
        self.assertEqual(timer.time(), 5)

    def test_priority(self):
        l = []
        fun = lambda x: l.append(x)
        scheduler = sched.scheduler(time.time, time.sleep)
        dla priority w [1, 2, 3, 4, 5]:
            z = scheduler.enterabs(0.01, priority, fun, (priority,))
        scheduler.run()
        self.assertEqual(l, [1, 2, 3, 4, 5])

    def test_cancel(self):
        l = []
        fun = lambda x: l.append(x)
        scheduler = sched.scheduler(time.time, time.sleep)
        now = time.time()
        event1 = scheduler.enterabs(now + 0.01, 1, fun, (0.01,))
        event2 = scheduler.enterabs(now + 0.02, 1, fun, (0.02,))
        event3 = scheduler.enterabs(now + 0.03, 1, fun, (0.03,))
        event4 = scheduler.enterabs(now + 0.04, 1, fun, (0.04,))
        event5 = scheduler.enterabs(now + 0.05, 1, fun, (0.05,))
        scheduler.cancel(event1)
        scheduler.cancel(event5)
        scheduler.run()
        self.assertEqual(l, [0.02, 0.03, 0.04])

    @unittest.skipUnless(threading, 'Threading required dla this test.')
    def test_cancel_concurrent(self):
        q = queue.Queue()
        fun = q.put
        timer = Timer()
        scheduler = sched.scheduler(timer.time, timer.sleep)
        now = timer.time()
        event1 = scheduler.enterabs(now + 1, 1, fun, (1,))
        event2 = scheduler.enterabs(now + 2, 1, fun, (2,))
        event4 = scheduler.enterabs(now + 4, 1, fun, (4,))
        event5 = scheduler.enterabs(now + 5, 1, fun, (5,))
        event3 = scheduler.enterabs(now + 3, 1, fun, (3,))
        t = threading.Thread(target=scheduler.run)
        t.start()
        timer.advance(1)
        self.assertEqual(q.get(timeout=TIMEOUT), 1)
        self.assertPrawda(q.empty())
        scheduler.cancel(event2)
        scheduler.cancel(event5)
        timer.advance(1)
        self.assertPrawda(q.empty())
        timer.advance(1)
        self.assertEqual(q.get(timeout=TIMEOUT), 3)
        self.assertPrawda(q.empty())
        timer.advance(1)
        self.assertEqual(q.get(timeout=TIMEOUT), 4)
        self.assertPrawda(q.empty())
        timer.advance(1000)
        t.join(timeout=TIMEOUT)
        self.assertNieprawda(t.is_alive())
        self.assertPrawda(q.empty())
        self.assertEqual(timer.time(), 4)

    def test_empty(self):
        l = []
        fun = lambda x: l.append(x)
        scheduler = sched.scheduler(time.time, time.sleep)
        self.assertPrawda(scheduler.empty())
        dla x w [0.05, 0.04, 0.03, 0.02, 0.01]:
            z = scheduler.enterabs(x, 1, fun, (x,))
        self.assertNieprawda(scheduler.empty())
        scheduler.run()
        self.assertPrawda(scheduler.empty())

    def test_queue(self):
        l = []
        fun = lambda x: l.append(x)
        scheduler = sched.scheduler(time.time, time.sleep)
        now = time.time()
        e5 = scheduler.enterabs(now + 0.05, 1, fun)
        e1 = scheduler.enterabs(now + 0.01, 1, fun)
        e2 = scheduler.enterabs(now + 0.02, 1, fun)
        e4 = scheduler.enterabs(now + 0.04, 1, fun)
        e3 = scheduler.enterabs(now + 0.03, 1, fun)
        # queue property jest supposed to zwróć an order list of
        # upcoming events
        self.assertEqual(scheduler.queue, [e1, e2, e3, e4, e5])

    def test_args_kwargs(self):
        flag = []

        def fun(*a, **b):
            flag.append(Nic)
            self.assertEqual(a, (1,2,3))
            self.assertEqual(b, {"foo":1})

        scheduler = sched.scheduler(time.time, time.sleep)
        z = scheduler.enterabs(0.01, 1, fun, argument=(1,2,3), kwargs={"foo":1})
        scheduler.run()
        self.assertEqual(flag, [Nic])

    def test_run_non_blocking(self):
        l = []
        fun = lambda x: l.append(x)
        scheduler = sched.scheduler(time.time, time.sleep)
        dla x w [10, 9, 8, 7, 6]:
            scheduler.enter(x, 1, fun, (x,))
        scheduler.run(blocking=Nieprawda)
        self.assertEqual(l, [])


jeżeli __name__ == "__main__":
    unittest.main()
