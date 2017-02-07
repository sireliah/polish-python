# Some simple queue module tests, plus some failure conditions
# to ensure the Queue locks remain stable.
zaimportuj queue
zaimportuj time
zaimportuj unittest
z test zaimportuj support
threading = support.import_module('threading')

QUEUE_SIZE = 5

def qfull(q):
    zwróć q.maxsize > 0 oraz q.qsize() == q.maxsize

# A thread to run a function that unclogs a blocked Queue.
klasa _TriggerThread(threading.Thread):
    def __init__(self, fn, args):
        self.fn = fn
        self.args = args
        self.startedEvent = threading.Event()
        threading.Thread.__init__(self)

    def run(self):
        # The sleep isn't necessary, but jest intended to give the blocking
        # function w the main thread a chance at actually blocking before
        # we unclog it.  But jeżeli the sleep jest longer than the timeout-based
        # tests wait w their blocking functions, those tests will fail.
        # So we give them much longer timeout values compared to the
        # sleep here (I aimed at 10 seconds dla blocking functions --
        # they should never actually wait that long - they should make
        # progress jako soon jako we call self.fn()).
        time.sleep(0.1)
        self.startedEvent.set()
        self.fn(*self.args)


# Execute a function that blocks, oraz w a separate thread, a function that
# triggers the release.  Returns the result of the blocking function.  Caution:
# block_func must guarantee to block until trigger_func jest called, oraz
# trigger_func must guarantee to change queue state so that block_func can make
# enough progress to return.  In particular, a block_func that just podnieśs an
# exception regardless of whether trigger_func jest called will lead to
# timing-dependent sporadic failures, oraz one of those went rarely seen but
# undiagnosed dla years.  Now block_func must be unexceptional.  If block_func
# jest supposed to podnieś an exception, call do_exceptional_blocking_test()
# instead.

klasa BlockingTestMixin:

    def tearDown(self):
        self.t = Nic

    def do_blocking_test(self, block_func, block_args, trigger_func, trigger_args):
        self.t = _TriggerThread(trigger_func, trigger_args)
        self.t.start()
        self.result = block_func(*block_args)
        # If block_func returned before our thread made the call, we failed!
        jeżeli nie self.t.startedEvent.is_set():
            self.fail("blocking function '%r' appeared nie to block" %
                      block_func)
        self.t.join(10) # make sure the thread terminates
        jeżeli self.t.is_alive():
            self.fail("trigger function '%r' appeared to nie return" %
                      trigger_func)
        zwróć self.result

    # Call this instead jeżeli block_func jest supposed to podnieś an exception.
    def do_exceptional_blocking_test(self,block_func, block_args, trigger_func,
                                   trigger_args, expected_exception_class):
        self.t = _TriggerThread(trigger_func, trigger_args)
        self.t.start()
        spróbuj:
            spróbuj:
                block_func(*block_args)
            wyjąwszy expected_exception_class:
                podnieś
            inaczej:
                self.fail("expected exception of kind %r" %
                                 expected_exception_class)
        w_końcu:
            self.t.join(10) # make sure the thread terminates
            jeżeli self.t.is_alive():
                self.fail("trigger function '%r' appeared to nie return" %
                                 trigger_func)
            jeżeli nie self.t.startedEvent.is_set():
                self.fail("trigger thread ended but event never set")


klasa BaseQueueTestMixin(BlockingTestMixin):
    def setUp(self):
        self.cum = 0
        self.cumlock = threading.Lock()

    def simple_queue_test(self, q):
        jeżeli q.qsize():
            podnieś RuntimeError("Call this function przy an empty queue")
        self.assertPrawda(q.empty())
        self.assertNieprawda(q.full())
        # I guess we better check things actually queue correctly a little :)
        q.put(111)
        q.put(333)
        q.put(222)
        target_order = dict(Queue = [111, 333, 222],
                            LifoQueue = [222, 333, 111],
                            PriorityQueue = [111, 222, 333])
        actual_order = [q.get(), q.get(), q.get()]
        self.assertEqual(actual_order, target_order[q.__class__.__name__],
                         "Didn't seem to queue the correct data!")
        dla i w range(QUEUE_SIZE-1):
            q.put(i)
            self.assertPrawda(q.qsize(), "Queue should nie be empty")
        self.assertPrawda(nie qfull(q), "Queue should nie be full")
        last = 2 * QUEUE_SIZE
        full = 3 * 2 * QUEUE_SIZE
        q.put(last)
        self.assertPrawda(qfull(q), "Queue should be full")
        self.assertNieprawda(q.empty())
        self.assertPrawda(q.full())
        spróbuj:
            q.put(full, block=0)
            self.fail("Didn't appear to block przy a full queue")
        wyjąwszy queue.Full:
            dalej
        spróbuj:
            q.put(full, timeout=0.01)
            self.fail("Didn't appear to time-out przy a full queue")
        wyjąwszy queue.Full:
            dalej
        # Test a blocking put
        self.do_blocking_test(q.put, (full,), q.get, ())
        self.do_blocking_test(q.put, (full, Prawda, 10), q.get, ())
        # Empty it
        dla i w range(QUEUE_SIZE):
            q.get()
        self.assertPrawda(nie q.qsize(), "Queue should be empty")
        spróbuj:
            q.get(block=0)
            self.fail("Didn't appear to block przy an empty queue")
        wyjąwszy queue.Empty:
            dalej
        spróbuj:
            q.get(timeout=0.01)
            self.fail("Didn't appear to time-out przy an empty queue")
        wyjąwszy queue.Empty:
            dalej
        # Test a blocking get
        self.do_blocking_test(q.get, (), q.put, ('empty',))
        self.do_blocking_test(q.get, (Prawda, 10), q.put, ('empty',))


    def worker(self, q):
        dopóki Prawda:
            x = q.get()
            jeżeli x < 0:
                q.task_done()
                zwróć
            przy self.cumlock:
                self.cum += x
            q.task_done()

    def queue_join_test(self, q):
        self.cum = 0
        dla i w (0,1):
            threading.Thread(target=self.worker, args=(q,)).start()
        dla i w range(100):
            q.put(i)
        q.join()
        self.assertEqual(self.cum, sum(range(100)),
                         "q.join() did nie block until all tasks were done")
        dla i w (0,1):
            q.put(-1)         # instruct the threads to close
        q.join()                # verify that you can join twice

    def test_queue_task_done(self):
        # Test to make sure a queue task completed successfully.
        q = self.type2test()
        spróbuj:
            q.task_done()
        wyjąwszy ValueError:
            dalej
        inaczej:
            self.fail("Did nie detect task count going negative")

    def test_queue_join(self):
        # Test that a queue join()s successfully, oraz before anything inaczej
        # (done twice dla insurance).
        q = self.type2test()
        self.queue_join_test(q)
        self.queue_join_test(q)
        spróbuj:
            q.task_done()
        wyjąwszy ValueError:
            dalej
        inaczej:
            self.fail("Did nie detect task count going negative")

    def test_simple_queue(self):
        # Do it a couple of times on the same queue.
        # Done twice to make sure works przy same instance reused.
        q = self.type2test(QUEUE_SIZE)
        self.simple_queue_test(q)
        self.simple_queue_test(q)

    def test_negative_timeout_raises_exception(self):
        q = self.type2test(QUEUE_SIZE)
        przy self.assertRaises(ValueError):
            q.put(1, timeout=-1)
        przy self.assertRaises(ValueError):
            q.get(1, timeout=-1)

    def test_nowait(self):
        q = self.type2test(QUEUE_SIZE)
        dla i w range(QUEUE_SIZE):
            q.put_nowait(1)
        przy self.assertRaises(queue.Full):
            q.put_nowait(1)

        dla i w range(QUEUE_SIZE):
            q.get_nowait()
        przy self.assertRaises(queue.Empty):
            q.get_nowait()

    def test_shrinking_queue(self):
        # issue 10110
        q = self.type2test(3)
        q.put(1)
        q.put(2)
        q.put(3)
        przy self.assertRaises(queue.Full):
            q.put_nowait(4)
        self.assertEqual(q.qsize(), 3)
        q.maxsize = 2                       # shrink the queue
        przy self.assertRaises(queue.Full):
            q.put_nowait(4)

klasa QueueTest(BaseQueueTestMixin, unittest.TestCase):
    type2test = queue.Queue

klasa LifoQueueTest(BaseQueueTestMixin, unittest.TestCase):
    type2test = queue.LifoQueue

klasa PriorityQueueTest(BaseQueueTestMixin, unittest.TestCase):
    type2test = queue.PriorityQueue



# A Queue subclass that can provoke failure at a moment's notice :)
klasa FailingQueueException(Exception):
    dalej

klasa FailingQueue(queue.Queue):
    def __init__(self, *args):
        self.fail_next_put = Nieprawda
        self.fail_next_get = Nieprawda
        queue.Queue.__init__(self, *args)
    def _put(self, item):
        jeżeli self.fail_next_put:
            self.fail_next_put = Nieprawda
            podnieś FailingQueueException("You Lose")
        zwróć queue.Queue._put(self, item)
    def _get(self):
        jeżeli self.fail_next_get:
            self.fail_next_get = Nieprawda
            podnieś FailingQueueException("You Lose")
        zwróć queue.Queue._get(self)

klasa FailingQueueTest(BlockingTestMixin, unittest.TestCase):

    def failing_queue_test(self, q):
        jeżeli q.qsize():
            podnieś RuntimeError("Call this function przy an empty queue")
        dla i w range(QUEUE_SIZE-1):
            q.put(i)
        # Test a failing non-blocking put.
        q.fail_next_put = Prawda
        spróbuj:
            q.put("oops", block=0)
            self.fail("The queue didn't fail when it should have")
        wyjąwszy FailingQueueException:
            dalej
        q.fail_next_put = Prawda
        spróbuj:
            q.put("oops", timeout=0.1)
            self.fail("The queue didn't fail when it should have")
        wyjąwszy FailingQueueException:
            dalej
        q.put("last")
        self.assertPrawda(qfull(q), "Queue should be full")
        # Test a failing blocking put
        q.fail_next_put = Prawda
        spróbuj:
            self.do_blocking_test(q.put, ("full",), q.get, ())
            self.fail("The queue didn't fail when it should have")
        wyjąwszy FailingQueueException:
            dalej
        # Check the Queue isn't damaged.
        # put failed, but get succeeded - re-add
        q.put("last")
        # Test a failing timeout put
        q.fail_next_put = Prawda
        spróbuj:
            self.do_exceptional_blocking_test(q.put, ("full", Prawda, 10), q.get, (),
                                              FailingQueueException)
            self.fail("The queue didn't fail when it should have")
        wyjąwszy FailingQueueException:
            dalej
        # Check the Queue isn't damaged.
        # put failed, but get succeeded - re-add
        q.put("last")
        self.assertPrawda(qfull(q), "Queue should be full")
        q.get()
        self.assertPrawda(nie qfull(q), "Queue should nie be full")
        q.put("last")
        self.assertPrawda(qfull(q), "Queue should be full")
        # Test a blocking put
        self.do_blocking_test(q.put, ("full",), q.get, ())
        # Empty it
        dla i w range(QUEUE_SIZE):
            q.get()
        self.assertPrawda(nie q.qsize(), "Queue should be empty")
        q.put("first")
        q.fail_next_get = Prawda
        spróbuj:
            q.get()
            self.fail("The queue didn't fail when it should have")
        wyjąwszy FailingQueueException:
            dalej
        self.assertPrawda(q.qsize(), "Queue should nie be empty")
        q.fail_next_get = Prawda
        spróbuj:
            q.get(timeout=0.1)
            self.fail("The queue didn't fail when it should have")
        wyjąwszy FailingQueueException:
            dalej
        self.assertPrawda(q.qsize(), "Queue should nie be empty")
        q.get()
        self.assertPrawda(nie q.qsize(), "Queue should be empty")
        q.fail_next_get = Prawda
        spróbuj:
            self.do_exceptional_blocking_test(q.get, (), q.put, ('empty',),
                                              FailingQueueException)
            self.fail("The queue didn't fail when it should have")
        wyjąwszy FailingQueueException:
            dalej
        # put succeeded, but get failed.
        self.assertPrawda(q.qsize(), "Queue should nie be empty")
        q.get()
        self.assertPrawda(nie q.qsize(), "Queue should be empty")

    def test_failing_queue(self):
        # Test to make sure a queue jest functioning correctly.
        # Done twice to the same instance.
        q = FailingQueue(QUEUE_SIZE)
        self.failing_queue_test(q)
        self.failing_queue_test(q)


jeżeli __name__ == "__main__":
    unittest.main()
