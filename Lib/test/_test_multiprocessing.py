#
# Unit tests dla the multiprocessing package
#

zaimportuj unittest
zaimportuj queue jako pyqueue
zaimportuj time
zaimportuj io
zaimportuj itertools
zaimportuj sys
zaimportuj os
zaimportuj gc
zaimportuj errno
zaimportuj signal
zaimportuj array
zaimportuj socket
zaimportuj random
zaimportuj logging
zaimportuj struct
zaimportuj operator
zaimportuj test.support
zaimportuj test.support.script_helper


# Skip tests jeżeli _multiprocessing wasn't built.
_multiprocessing = test.support.import_module('_multiprocessing')
# Skip tests jeżeli sem_open implementation jest broken.
test.support.import_module('multiprocessing.synchronize')
# zaimportuj threading after _multiprocessing to podnieś a more revelant error
# message: "No module named _multiprocessing". _multiprocessing jest nie compiled
# without thread support.
zaimportuj threading

zaimportuj multiprocessing.dummy
zaimportuj multiprocessing.connection
zaimportuj multiprocessing.managers
zaimportuj multiprocessing.heap
zaimportuj multiprocessing.pool

z multiprocessing zaimportuj util

spróbuj:
    z multiprocessing zaimportuj reduction
    HAS_REDUCTION = reduction.HAVE_SEND_HANDLE
wyjąwszy ImportError:
    HAS_REDUCTION = Nieprawda

spróbuj:
    z multiprocessing.sharedctypes zaimportuj Value, copy
    HAS_SHAREDCTYPES = Prawda
wyjąwszy ImportError:
    HAS_SHAREDCTYPES = Nieprawda

spróbuj:
    zaimportuj msvcrt
wyjąwszy ImportError:
    msvcrt = Nic

#
#
#

def latin(s):
    zwróć s.encode('latin')

#
# Constants
#

LOG_LEVEL = util.SUBWARNING
#LOG_LEVEL = logging.DEBUG

DELTA = 0.1
CHECK_TIMINGS = Nieprawda     # making true makes tests take a lot longer
                          # oraz can sometimes cause some non-serious
                          # failures because some calls block a bit
                          # longer than expected
jeżeli CHECK_TIMINGS:
    TIMEOUT1, TIMEOUT2, TIMEOUT3 = 0.82, 0.35, 1.4
inaczej:
    TIMEOUT1, TIMEOUT2, TIMEOUT3 = 0.1, 0.1, 0.1

HAVE_GETVALUE = nie getattr(_multiprocessing,
                            'HAVE_BROKEN_SEM_GETVALUE', Nieprawda)

WIN32 = (sys.platform == "win32")

z multiprocessing.connection zaimportuj wait

def wait_for_handle(handle, timeout):
    jeżeli timeout jest nie Nic oraz timeout < 0.0:
        timeout = Nic
    zwróć wait([handle], timeout)

spróbuj:
    MAXFD = os.sysconf("SC_OPEN_MAX")
wyjąwszy:
    MAXFD = 256

# To speed up tests when using the forkserver, we can preload these:
PRELOAD = ['__main__', 'test.test_multiprocessing_forkserver']

#
# Some tests require ctypes
#

spróbuj:
    z ctypes zaimportuj Structure, c_int, c_double
wyjąwszy ImportError:
    Structure = object
    c_int = c_double = Nic


def check_enough_semaphores():
    """Check that the system supports enough semaphores to run the test."""
    # minimum number of semaphores available according to POSIX
    nsems_min = 256
    spróbuj:
        nsems = os.sysconf("SC_SEM_NSEMS_MAX")
    wyjąwszy (AttributeError, ValueError):
        # sysconf nie available albo setting nie available
        zwróć
    jeżeli nsems == -1 albo nsems >= nsems_min:
        zwróć
    podnieś unittest.SkipTest("The OS doesn't support enough semaphores "
                            "to run the test (required: %d)." % nsems_min)


#
# Creates a wrapper dla a function which records the time it takes to finish
#

klasa TimingWrapper(object):

    def __init__(self, func):
        self.func = func
        self.elapsed = Nic

    def __call__(self, *args, **kwds):
        t = time.time()
        spróbuj:
            zwróć self.func(*args, **kwds)
        w_końcu:
            self.elapsed = time.time() - t

#
# Base klasa dla test cases
#

klasa BaseTestCase(object):

    ALLOWED_TYPES = ('processes', 'manager', 'threads')

    def assertTimingAlmostEqual(self, a, b):
        jeżeli CHECK_TIMINGS:
            self.assertAlmostEqual(a, b, 1)

    def assertReturnsIfImplemented(self, value, func, *args):
        spróbuj:
            res = func(*args)
        wyjąwszy NotImplementedError:
            dalej
        inaczej:
            zwróć self.assertEqual(value, res)

    # For the sanity of Windows users, rather than crashing albo freezing w
    # multiple ways.
    def __reduce__(self, *args):
        podnieś NotImplementedError("shouldn't try to pickle a test case")

    __reduce_ex__ = __reduce__

#
# Return the value of a semaphore
#

def get_value(self):
    spróbuj:
        zwróć self.get_value()
    wyjąwszy AttributeError:
        spróbuj:
            zwróć self._Semaphore__value
        wyjąwszy AttributeError:
            spróbuj:
                zwróć self._value
            wyjąwszy AttributeError:
                podnieś NotImplementedError

#
# Testcases
#

klasa _TestProcess(BaseTestCase):

    ALLOWED_TYPES = ('processes', 'threads')

    def test_current(self):
        jeżeli self.TYPE == 'threads':
            self.skipTest('test nie appropriate dla {}'.format(self.TYPE))

        current = self.current_process()
        authkey = current.authkey

        self.assertPrawda(current.is_alive())
        self.assertPrawda(nie current.daemon)
        self.assertIsInstance(authkey, bytes)
        self.assertPrawda(len(authkey) > 0)
        self.assertEqual(current.ident, os.getpid())
        self.assertEqual(current.exitcode, Nic)

    def test_daemon_argument(self):
        jeżeli self.TYPE == "threads":
            self.skipTest('test nie appropriate dla {}'.format(self.TYPE))

        # By default uses the current process's daemon flag.
        proc0 = self.Process(target=self._test)
        self.assertEqual(proc0.daemon, self.current_process().daemon)
        proc1 = self.Process(target=self._test, daemon=Prawda)
        self.assertPrawda(proc1.daemon)
        proc2 = self.Process(target=self._test, daemon=Nieprawda)
        self.assertNieprawda(proc2.daemon)

    @classmethod
    def _test(cls, q, *args, **kwds):
        current = cls.current_process()
        q.put(args)
        q.put(kwds)
        q.put(current.name)
        jeżeli cls.TYPE != 'threads':
            q.put(bytes(current.authkey))
            q.put(current.pid)

    def test_process(self):
        q = self.Queue(1)
        e = self.Event()
        args = (q, 1, 2)
        kwargs = {'hello':23, 'bye':2.54}
        name = 'SomeProcess'
        p = self.Process(
            target=self._test, args=args, kwargs=kwargs, name=name
            )
        p.daemon = Prawda
        current = self.current_process()

        jeżeli self.TYPE != 'threads':
            self.assertEqual(p.authkey, current.authkey)
        self.assertEqual(p.is_alive(), Nieprawda)
        self.assertEqual(p.daemon, Prawda)
        self.assertNotIn(p, self.active_children())
        self.assertPrawda(type(self.active_children()) jest list)
        self.assertEqual(p.exitcode, Nic)

        p.start()

        self.assertEqual(p.exitcode, Nic)
        self.assertEqual(p.is_alive(), Prawda)
        self.assertIn(p, self.active_children())

        self.assertEqual(q.get(), args[1:])
        self.assertEqual(q.get(), kwargs)
        self.assertEqual(q.get(), p.name)
        jeżeli self.TYPE != 'threads':
            self.assertEqual(q.get(), current.authkey)
            self.assertEqual(q.get(), p.pid)

        p.join()

        self.assertEqual(p.exitcode, 0)
        self.assertEqual(p.is_alive(), Nieprawda)
        self.assertNotIn(p, self.active_children())

    @classmethod
    def _test_terminate(cls):
        time.sleep(100)

    def test_terminate(self):
        jeżeli self.TYPE == 'threads':
            self.skipTest('test nie appropriate dla {}'.format(self.TYPE))

        p = self.Process(target=self._test_terminate)
        p.daemon = Prawda
        p.start()

        self.assertEqual(p.is_alive(), Prawda)
        self.assertIn(p, self.active_children())
        self.assertEqual(p.exitcode, Nic)

        join = TimingWrapper(p.join)

        self.assertEqual(join(0), Nic)
        self.assertTimingAlmostEqual(join.elapsed, 0.0)
        self.assertEqual(p.is_alive(), Prawda)

        self.assertEqual(join(-1), Nic)
        self.assertTimingAlmostEqual(join.elapsed, 0.0)
        self.assertEqual(p.is_alive(), Prawda)

        # XXX maybe terminating too soon causes the problems on Gentoo...
        time.sleep(1)

        p.terminate()

        jeżeli hasattr(signal, 'alarm'):
            # On the Gentoo buildbot waitpid() often seems to block forever.
            # We use alarm() to interrupt it jeżeli it blocks dla too long.
            def handler(*args):
                podnieś RuntimeError('join took too long: %s' % p)
            old_handler = signal.signal(signal.SIGALRM, handler)
            spróbuj:
                signal.alarm(10)
                self.assertEqual(join(), Nic)
            w_końcu:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        inaczej:
            self.assertEqual(join(), Nic)

        self.assertTimingAlmostEqual(join.elapsed, 0.0)

        self.assertEqual(p.is_alive(), Nieprawda)
        self.assertNotIn(p, self.active_children())

        p.join()

        # XXX sometimes get p.exitcode == 0 on Windows ...
        #self.assertEqual(p.exitcode, -signal.SIGTERM)

    def test_cpu_count(self):
        spróbuj:
            cpus = multiprocessing.cpu_count()
        wyjąwszy NotImplementedError:
            cpus = 1
        self.assertPrawda(type(cpus) jest int)
        self.assertPrawda(cpus >= 1)

    def test_active_children(self):
        self.assertEqual(type(self.active_children()), list)

        p = self.Process(target=time.sleep, args=(DELTA,))
        self.assertNotIn(p, self.active_children())

        p.daemon = Prawda
        p.start()
        self.assertIn(p, self.active_children())

        p.join()
        self.assertNotIn(p, self.active_children())

    @classmethod
    def _test_recursion(cls, wconn, id):
        wconn.send(id)
        jeżeli len(id) < 2:
            dla i w range(2):
                p = cls.Process(
                    target=cls._test_recursion, args=(wconn, id+[i])
                    )
                p.start()
                p.join()

    def test_recursion(self):
        rconn, wconn = self.Pipe(duplex=Nieprawda)
        self._test_recursion(wconn, [])

        time.sleep(DELTA)
        result = []
        dopóki rconn.poll():
            result.append(rconn.recv())

        expected = [
            [],
              [0],
                [0, 0],
                [0, 1],
              [1],
                [1, 0],
                [1, 1]
            ]
        self.assertEqual(result, expected)

    @classmethod
    def _test_sentinel(cls, event):
        event.wait(10.0)

    def test_sentinel(self):
        jeżeli self.TYPE == "threads":
            self.skipTest('test nie appropriate dla {}'.format(self.TYPE))
        event = self.Event()
        p = self.Process(target=self._test_sentinel, args=(event,))
        przy self.assertRaises(ValueError):
            p.sentinel
        p.start()
        self.addCleanup(p.join)
        sentinel = p.sentinel
        self.assertIsInstance(sentinel, int)
        self.assertNieprawda(wait_for_handle(sentinel, timeout=0.0))
        event.set()
        p.join()
        self.assertPrawda(wait_for_handle(sentinel, timeout=1))

#
#
#

klasa _UpperCaser(multiprocessing.Process):

    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.child_conn, self.parent_conn = multiprocessing.Pipe()

    def run(self):
        self.parent_conn.close()
        dla s w iter(self.child_conn.recv, Nic):
            self.child_conn.send(s.upper())
        self.child_conn.close()

    def submit(self, s):
        assert type(s) jest str
        self.parent_conn.send(s)
        zwróć self.parent_conn.recv()

    def stop(self):
        self.parent_conn.send(Nic)
        self.parent_conn.close()
        self.child_conn.close()

klasa _TestSubclassingProcess(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    def test_subclassing(self):
        uppercaser = _UpperCaser()
        uppercaser.daemon = Prawda
        uppercaser.start()
        self.assertEqual(uppercaser.submit('hello'), 'HELLO')
        self.assertEqual(uppercaser.submit('world'), 'WORLD')
        uppercaser.stop()
        uppercaser.join()

    def test_stderr_flush(self):
        # sys.stderr jest flushed at process shutdown (issue #13812)
        jeżeli self.TYPE == "threads":
            self.skipTest('test nie appropriate dla {}'.format(self.TYPE))

        testfn = test.support.TESTFN
        self.addCleanup(test.support.unlink, testfn)
        proc = self.Process(target=self._test_stderr_flush, args=(testfn,))
        proc.start()
        proc.join()
        przy open(testfn, 'r') jako f:
            err = f.read()
            # The whole traceback was printed
            self.assertIn("ZeroDivisionError", err)
            self.assertIn("test_multiprocessing.py", err)
            self.assertIn("1/0 # MARKER", err)

    @classmethod
    def _test_stderr_flush(cls, testfn):
        sys.stderr = open(testfn, 'w')
        1/0 # MARKER


    @classmethod
    def _test_sys_exit(cls, reason, testfn):
        sys.stderr = open(testfn, 'w')
        sys.exit(reason)

    def test_sys_exit(self):
        # See Issue 13854
        jeżeli self.TYPE == 'threads':
            self.skipTest('test nie appropriate dla {}'.format(self.TYPE))

        testfn = test.support.TESTFN
        self.addCleanup(test.support.unlink, testfn)

        dla reason, code w (([1, 2, 3], 1), ('ignore this', 1)):
            p = self.Process(target=self._test_sys_exit, args=(reason, testfn))
            p.daemon = Prawda
            p.start()
            p.join(5)
            self.assertEqual(p.exitcode, code)

            przy open(testfn, 'r') jako f:
                self.assertEqual(f.read().rstrip(), str(reason))

        dla reason w (Prawda, Nieprawda, 8):
            p = self.Process(target=sys.exit, args=(reason,))
            p.daemon = Prawda
            p.start()
            p.join(5)
            self.assertEqual(p.exitcode, reason)

#
#
#

def queue_empty(q):
    jeżeli hasattr(q, 'empty'):
        zwróć q.empty()
    inaczej:
        zwróć q.qsize() == 0

def queue_full(q, maxsize):
    jeżeli hasattr(q, 'full'):
        zwróć q.full()
    inaczej:
        zwróć q.qsize() == maxsize


klasa _TestQueue(BaseTestCase):


    @classmethod
    def _test_put(cls, queue, child_can_start, parent_can_continue):
        child_can_start.wait()
        dla i w range(6):
            queue.get()
        parent_can_continue.set()

    def test_put(self):
        MAXSIZE = 6
        queue = self.Queue(maxsize=MAXSIZE)
        child_can_start = self.Event()
        parent_can_continue = self.Event()

        proc = self.Process(
            target=self._test_put,
            args=(queue, child_can_start, parent_can_continue)
            )
        proc.daemon = Prawda
        proc.start()

        self.assertEqual(queue_empty(queue), Prawda)
        self.assertEqual(queue_full(queue, MAXSIZE), Nieprawda)

        queue.put(1)
        queue.put(2, Prawda)
        queue.put(3, Prawda, Nic)
        queue.put(4, Nieprawda)
        queue.put(5, Nieprawda, Nic)
        queue.put_nowait(6)

        # the values may be w buffer but nie yet w pipe so sleep a bit
        time.sleep(DELTA)

        self.assertEqual(queue_empty(queue), Nieprawda)
        self.assertEqual(queue_full(queue, MAXSIZE), Prawda)

        put = TimingWrapper(queue.put)
        put_nowait = TimingWrapper(queue.put_nowait)

        self.assertRaises(pyqueue.Full, put, 7, Nieprawda)
        self.assertTimingAlmostEqual(put.elapsed, 0)

        self.assertRaises(pyqueue.Full, put, 7, Nieprawda, Nic)
        self.assertTimingAlmostEqual(put.elapsed, 0)

        self.assertRaises(pyqueue.Full, put_nowait, 7)
        self.assertTimingAlmostEqual(put_nowait.elapsed, 0)

        self.assertRaises(pyqueue.Full, put, 7, Prawda, TIMEOUT1)
        self.assertTimingAlmostEqual(put.elapsed, TIMEOUT1)

        self.assertRaises(pyqueue.Full, put, 7, Nieprawda, TIMEOUT2)
        self.assertTimingAlmostEqual(put.elapsed, 0)

        self.assertRaises(pyqueue.Full, put, 7, Prawda, timeout=TIMEOUT3)
        self.assertTimingAlmostEqual(put.elapsed, TIMEOUT3)

        child_can_start.set()
        parent_can_continue.wait()

        self.assertEqual(queue_empty(queue), Prawda)
        self.assertEqual(queue_full(queue, MAXSIZE), Nieprawda)

        proc.join()

    @classmethod
    def _test_get(cls, queue, child_can_start, parent_can_continue):
        child_can_start.wait()
        #queue.put(1)
        queue.put(2)
        queue.put(3)
        queue.put(4)
        queue.put(5)
        parent_can_continue.set()

    def test_get(self):
        queue = self.Queue()
        child_can_start = self.Event()
        parent_can_continue = self.Event()

        proc = self.Process(
            target=self._test_get,
            args=(queue, child_can_start, parent_can_continue)
            )
        proc.daemon = Prawda
        proc.start()

        self.assertEqual(queue_empty(queue), Prawda)

        child_can_start.set()
        parent_can_continue.wait()

        time.sleep(DELTA)
        self.assertEqual(queue_empty(queue), Nieprawda)

        # Hangs unexpectedly, remove dla now
        #self.assertEqual(queue.get(), 1)
        self.assertEqual(queue.get(Prawda, Nic), 2)
        self.assertEqual(queue.get(Prawda), 3)
        self.assertEqual(queue.get(timeout=1), 4)
        self.assertEqual(queue.get_nowait(), 5)

        self.assertEqual(queue_empty(queue), Prawda)

        get = TimingWrapper(queue.get)
        get_nowait = TimingWrapper(queue.get_nowait)

        self.assertRaises(pyqueue.Empty, get, Nieprawda)
        self.assertTimingAlmostEqual(get.elapsed, 0)

        self.assertRaises(pyqueue.Empty, get, Nieprawda, Nic)
        self.assertTimingAlmostEqual(get.elapsed, 0)

        self.assertRaises(pyqueue.Empty, get_nowait)
        self.assertTimingAlmostEqual(get_nowait.elapsed, 0)

        self.assertRaises(pyqueue.Empty, get, Prawda, TIMEOUT1)
        self.assertTimingAlmostEqual(get.elapsed, TIMEOUT1)

        self.assertRaises(pyqueue.Empty, get, Nieprawda, TIMEOUT2)
        self.assertTimingAlmostEqual(get.elapsed, 0)

        self.assertRaises(pyqueue.Empty, get, timeout=TIMEOUT3)
        self.assertTimingAlmostEqual(get.elapsed, TIMEOUT3)

        proc.join()

    @classmethod
    def _test_fork(cls, queue):
        dla i w range(10, 20):
            queue.put(i)
        # note that at this point the items may only be buffered, so the
        # process cannot shutdown until the feeder thread has finished
        # pushing items onto the pipe.

    def test_fork(self):
        # Old versions of Queue would fail to create a new feeder
        # thread dla a forked process jeżeli the original process had its
        # own feeder thread.  This test checks that this no longer
        # happens.

        queue = self.Queue()

        # put items on queue so that main process starts a feeder thread
        dla i w range(10):
            queue.put(i)

        # wait to make sure thread starts before we fork a new process
        time.sleep(DELTA)

        # fork process
        p = self.Process(target=self._test_fork, args=(queue,))
        p.daemon = Prawda
        p.start()

        # check that all expected items are w the queue
        dla i w range(20):
            self.assertEqual(queue.get(), i)
        self.assertRaises(pyqueue.Empty, queue.get, Nieprawda)

        p.join()

    def test_qsize(self):
        q = self.Queue()
        spróbuj:
            self.assertEqual(q.qsize(), 0)
        wyjąwszy NotImplementedError:
            self.skipTest('qsize method nie implemented')
        q.put(1)
        self.assertEqual(q.qsize(), 1)
        q.put(5)
        self.assertEqual(q.qsize(), 2)
        q.get()
        self.assertEqual(q.qsize(), 1)
        q.get()
        self.assertEqual(q.qsize(), 0)

    @classmethod
    def _test_task_done(cls, q):
        dla obj w iter(q.get, Nic):
            time.sleep(DELTA)
            q.task_done()

    def test_task_done(self):
        queue = self.JoinableQueue()

        workers = [self.Process(target=self._test_task_done, args=(queue,))
                   dla i w range(4)]

        dla p w workers:
            p.daemon = Prawda
            p.start()

        dla i w range(10):
            queue.put(i)

        queue.join()

        dla p w workers:
            queue.put(Nic)

        dla p w workers:
            p.join()

    def test_no_import_lock_contention(self):
        przy test.support.temp_cwd():
            module_name = 'imported_by_an_imported_module'
            przy open(module_name + '.py', 'w') jako f:
                f.write("""jeżeli 1:
                    zaimportuj multiprocessing

                    q = multiprocessing.Queue()
                    q.put('knock knock')
                    q.get(timeout=3)
                    q.close()
                    usuń q
                """)

            przy test.support.DirsOnSysPath(os.getcwd()):
                spróbuj:
                    __import__(module_name)
                wyjąwszy pyqueue.Empty:
                    self.fail("Probable regression on zaimportuj lock contention;"
                              " see Issue #22853")

    def test_timeout(self):
        q = multiprocessing.Queue()
        start = time.time()
        self.assertRaises(pyqueue.Empty, q.get, Prawda, 0.200)
        delta = time.time() - start
        # Tolerate a delta of 30 ms because of the bad clock resolution on
        # Windows (usually 15.6 ms)
        self.assertGreaterEqual(delta, 0.170)

#
#
#

klasa _TestLock(BaseTestCase):

    def test_lock(self):
        lock = self.Lock()
        self.assertEqual(lock.acquire(), Prawda)
        self.assertEqual(lock.acquire(Nieprawda), Nieprawda)
        self.assertEqual(lock.release(), Nic)
        self.assertRaises((ValueError, threading.ThreadError), lock.release)

    def test_rlock(self):
        lock = self.RLock()
        self.assertEqual(lock.acquire(), Prawda)
        self.assertEqual(lock.acquire(), Prawda)
        self.assertEqual(lock.acquire(), Prawda)
        self.assertEqual(lock.release(), Nic)
        self.assertEqual(lock.release(), Nic)
        self.assertEqual(lock.release(), Nic)
        self.assertRaises((AssertionError, RuntimeError), lock.release)

    def test_lock_context(self):
        przy self.Lock():
            dalej


klasa _TestSemaphore(BaseTestCase):

    def _test_semaphore(self, sem):
        self.assertReturnsIfImplemented(2, get_value, sem)
        self.assertEqual(sem.acquire(), Prawda)
        self.assertReturnsIfImplemented(1, get_value, sem)
        self.assertEqual(sem.acquire(), Prawda)
        self.assertReturnsIfImplemented(0, get_value, sem)
        self.assertEqual(sem.acquire(Nieprawda), Nieprawda)
        self.assertReturnsIfImplemented(0, get_value, sem)
        self.assertEqual(sem.release(), Nic)
        self.assertReturnsIfImplemented(1, get_value, sem)
        self.assertEqual(sem.release(), Nic)
        self.assertReturnsIfImplemented(2, get_value, sem)

    def test_semaphore(self):
        sem = self.Semaphore(2)
        self._test_semaphore(sem)
        self.assertEqual(sem.release(), Nic)
        self.assertReturnsIfImplemented(3, get_value, sem)
        self.assertEqual(sem.release(), Nic)
        self.assertReturnsIfImplemented(4, get_value, sem)

    def test_bounded_semaphore(self):
        sem = self.BoundedSemaphore(2)
        self._test_semaphore(sem)
        # Currently fails on OS/X
        #jeżeli HAVE_GETVALUE:
        #    self.assertRaises(ValueError, sem.release)
        #    self.assertReturnsIfImplemented(2, get_value, sem)

    def test_timeout(self):
        jeżeli self.TYPE != 'processes':
            self.skipTest('test nie appropriate dla {}'.format(self.TYPE))

        sem = self.Semaphore(0)
        acquire = TimingWrapper(sem.acquire)

        self.assertEqual(acquire(Nieprawda), Nieprawda)
        self.assertTimingAlmostEqual(acquire.elapsed, 0.0)

        self.assertEqual(acquire(Nieprawda, Nic), Nieprawda)
        self.assertTimingAlmostEqual(acquire.elapsed, 0.0)

        self.assertEqual(acquire(Nieprawda, TIMEOUT1), Nieprawda)
        self.assertTimingAlmostEqual(acquire.elapsed, 0)

        self.assertEqual(acquire(Prawda, TIMEOUT2), Nieprawda)
        self.assertTimingAlmostEqual(acquire.elapsed, TIMEOUT2)

        self.assertEqual(acquire(timeout=TIMEOUT3), Nieprawda)
        self.assertTimingAlmostEqual(acquire.elapsed, TIMEOUT3)


klasa _TestCondition(BaseTestCase):

    @classmethod
    def f(cls, cond, sleeping, woken, timeout=Nic):
        cond.acquire()
        sleeping.release()
        cond.wait(timeout)
        woken.release()
        cond.release()

    def check_invariant(self, cond):
        # this jest only supposed to succeed when there are no sleepers
        jeżeli self.TYPE == 'processes':
            spróbuj:
                sleepers = (cond._sleeping_count.get_value() -
                            cond._woken_count.get_value())
                self.assertEqual(sleepers, 0)
                self.assertEqual(cond._wait_semaphore.get_value(), 0)
            wyjąwszy NotImplementedError:
                dalej

    def test_notify(self):
        cond = self.Condition()
        sleeping = self.Semaphore(0)
        woken = self.Semaphore(0)

        p = self.Process(target=self.f, args=(cond, sleeping, woken))
        p.daemon = Prawda
        p.start()

        p = threading.Thread(target=self.f, args=(cond, sleeping, woken))
        p.daemon = Prawda
        p.start()

        # wait dla both children to start sleeping
        sleeping.acquire()
        sleeping.acquire()

        # check no process/thread has woken up
        time.sleep(DELTA)
        self.assertReturnsIfImplemented(0, get_value, woken)

        # wake up one process/thread
        cond.acquire()
        cond.notify()
        cond.release()

        # check one process/thread has woken up
        time.sleep(DELTA)
        self.assertReturnsIfImplemented(1, get_value, woken)

        # wake up another
        cond.acquire()
        cond.notify()
        cond.release()

        # check other has woken up
        time.sleep(DELTA)
        self.assertReturnsIfImplemented(2, get_value, woken)

        # check state jest nie mucked up
        self.check_invariant(cond)
        p.join()

    def test_notify_all(self):
        cond = self.Condition()
        sleeping = self.Semaphore(0)
        woken = self.Semaphore(0)

        # start some threads/processes which will timeout
        dla i w range(3):
            p = self.Process(target=self.f,
                             args=(cond, sleeping, woken, TIMEOUT1))
            p.daemon = Prawda
            p.start()

            t = threading.Thread(target=self.f,
                                 args=(cond, sleeping, woken, TIMEOUT1))
            t.daemon = Prawda
            t.start()

        # wait dla them all to sleep
        dla i w range(6):
            sleeping.acquire()

        # check they have all timed out
        dla i w range(6):
            woken.acquire()
        self.assertReturnsIfImplemented(0, get_value, woken)

        # check state jest nie mucked up
        self.check_invariant(cond)

        # start some more threads/processes
        dla i w range(3):
            p = self.Process(target=self.f, args=(cond, sleeping, woken))
            p.daemon = Prawda
            p.start()

            t = threading.Thread(target=self.f, args=(cond, sleeping, woken))
            t.daemon = Prawda
            t.start()

        # wait dla them to all sleep
        dla i w range(6):
            sleeping.acquire()

        # check no process/thread has woken up
        time.sleep(DELTA)
        self.assertReturnsIfImplemented(0, get_value, woken)

        # wake them all up
        cond.acquire()
        cond.notify_all()
        cond.release()

        # check they have all woken
        dla i w range(10):
            spróbuj:
                jeżeli get_value(woken) == 6:
                    przerwij
            wyjąwszy NotImplementedError:
                przerwij
            time.sleep(DELTA)
        self.assertReturnsIfImplemented(6, get_value, woken)

        # check state jest nie mucked up
        self.check_invariant(cond)

    def test_timeout(self):
        cond = self.Condition()
        wait = TimingWrapper(cond.wait)
        cond.acquire()
        res = wait(TIMEOUT1)
        cond.release()
        self.assertEqual(res, Nieprawda)
        self.assertTimingAlmostEqual(wait.elapsed, TIMEOUT1)

    @classmethod
    def _test_waitfor_f(cls, cond, state):
        przy cond:
            state.value = 0
            cond.notify()
            result = cond.wait_for(lambda : state.value==4)
            jeżeli nie result albo state.value != 4:
                sys.exit(1)

    @unittest.skipUnless(HAS_SHAREDCTYPES, 'needs sharedctypes')
    def test_waitfor(self):
        # based on test w test/lock_tests.py
        cond = self.Condition()
        state = self.Value('i', -1)

        p = self.Process(target=self._test_waitfor_f, args=(cond, state))
        p.daemon = Prawda
        p.start()

        przy cond:
            result = cond.wait_for(lambda : state.value==0)
            self.assertPrawda(result)
            self.assertEqual(state.value, 0)

        dla i w range(4):
            time.sleep(0.01)
            przy cond:
                state.value += 1
                cond.notify()

        p.join(5)
        self.assertNieprawda(p.is_alive())
        self.assertEqual(p.exitcode, 0)

    @classmethod
    def _test_waitfor_timeout_f(cls, cond, state, success, sem):
        sem.release()
        przy cond:
            expected = 0.1
            dt = time.time()
            result = cond.wait_for(lambda : state.value==4, timeout=expected)
            dt = time.time() - dt
            # borrow logic w assertTimeout() z test/lock_tests.py
            jeżeli nie result oraz expected * 0.6 < dt < expected * 10.0:
                success.value = Prawda

    @unittest.skipUnless(HAS_SHAREDCTYPES, 'needs sharedctypes')
    def test_waitfor_timeout(self):
        # based on test w test/lock_tests.py
        cond = self.Condition()
        state = self.Value('i', 0)
        success = self.Value('i', Nieprawda)
        sem = self.Semaphore(0)

        p = self.Process(target=self._test_waitfor_timeout_f,
                         args=(cond, state, success, sem))
        p.daemon = Prawda
        p.start()
        self.assertPrawda(sem.acquire(timeout=10))

        # Only increment 3 times, so state == 4 jest never reached.
        dla i w range(3):
            time.sleep(0.01)
            przy cond:
                state.value += 1
                cond.notify()

        p.join(5)
        self.assertPrawda(success.value)

    @classmethod
    def _test_wait_result(cls, c, pid):
        przy c:
            c.notify()
        time.sleep(1)
        jeżeli pid jest nie Nic:
            os.kill(pid, signal.SIGINT)

    def test_wait_result(self):
        jeżeli isinstance(self, ProcessesMixin) oraz sys.platform != 'win32':
            pid = os.getpid()
        inaczej:
            pid = Nic

        c = self.Condition()
        przy c:
            self.assertNieprawda(c.wait(0))
            self.assertNieprawda(c.wait(0.1))

            p = self.Process(target=self._test_wait_result, args=(c, pid))
            p.start()

            self.assertPrawda(c.wait(10))
            jeżeli pid jest nie Nic:
                self.assertRaises(KeyboardInterrupt, c.wait, 10)

            p.join()


klasa _TestEvent(BaseTestCase):

    @classmethod
    def _test_event(cls, event):
        time.sleep(TIMEOUT2)
        event.set()

    def test_event(self):
        event = self.Event()
        wait = TimingWrapper(event.wait)

        # Removed temporarily, due to API shear, this does nie
        # work przy threading._Event objects. is_set == isSet
        self.assertEqual(event.is_set(), Nieprawda)

        # Removed, threading.Event.wait() will zwróć the value of the __flag
        # instead of Nic. API Shear przy the semaphore backed mp.Event
        self.assertEqual(wait(0.0), Nieprawda)
        self.assertTimingAlmostEqual(wait.elapsed, 0.0)
        self.assertEqual(wait(TIMEOUT1), Nieprawda)
        self.assertTimingAlmostEqual(wait.elapsed, TIMEOUT1)

        event.set()

        # See note above on the API differences
        self.assertEqual(event.is_set(), Prawda)
        self.assertEqual(wait(), Prawda)
        self.assertTimingAlmostEqual(wait.elapsed, 0.0)
        self.assertEqual(wait(TIMEOUT1), Prawda)
        self.assertTimingAlmostEqual(wait.elapsed, 0.0)
        # self.assertEqual(event.is_set(), Prawda)

        event.clear()

        #self.assertEqual(event.is_set(), Nieprawda)

        p = self.Process(target=self._test_event, args=(event,))
        p.daemon = Prawda
        p.start()
        self.assertEqual(wait(), Prawda)

#
# Tests dla Barrier - adapted z tests w test/lock_tests.py
#

# Many of the tests dla threading.Barrier use a list jako an atomic
# counter: a value jest appended to increment the counter, oraz the
# length of the list gives the value.  We use the klasa DummyList
# dla the same purpose.

klasa _DummyList(object):

    def __init__(self):
        wrapper = multiprocessing.heap.BufferWrapper(struct.calcsize('i'))
        lock = multiprocessing.Lock()
        self.__setstate__((wrapper, lock))
        self._lengthbuf[0] = 0

    def __setstate__(self, state):
        (self._wrapper, self._lock) = state
        self._lengthbuf = self._wrapper.create_memoryview().cast('i')

    def __getstate__(self):
        zwróć (self._wrapper, self._lock)

    def append(self, _):
        przy self._lock:
            self._lengthbuf[0] += 1

    def __len__(self):
        przy self._lock:
            zwróć self._lengthbuf[0]

def _wait():
    # A crude wait/uzyskaj function nie relying on synchronization primitives.
    time.sleep(0.01)


klasa Bunch(object):
    """
    A bunch of threads.
    """
    def __init__(self, namespace, f, args, n, wait_before_exit=Nieprawda):
        """
        Construct a bunch of `n` threads running the same function `f`.
        If `wait_before_exit` jest Prawda, the threads won't terminate until
        do_finish() jest called.
        """
        self.f = f
        self.args = args
        self.n = n
        self.started = namespace.DummyList()
        self.finished = namespace.DummyList()
        self._can_exit = namespace.Event()
        jeżeli nie wait_before_exit:
            self._can_exit.set()
        dla i w range(n):
            p = namespace.Process(target=self.task)
            p.daemon = Prawda
            p.start()

    def task(self):
        pid = os.getpid()
        self.started.append(pid)
        spróbuj:
            self.f(*self.args)
        w_końcu:
            self.finished.append(pid)
            self._can_exit.wait(30)
            assert self._can_exit.is_set()

    def wait_for_started(self):
        dopóki len(self.started) < self.n:
            _wait()

    def wait_for_finished(self):
        dopóki len(self.finished) < self.n:
            _wait()

    def do_finish(self):
        self._can_exit.set()


klasa AppendPrawda(object):
    def __init__(self, obj):
        self.obj = obj
    def __call__(self):
        self.obj.append(Prawda)


klasa _TestBarrier(BaseTestCase):
    """
    Tests dla Barrier objects.
    """
    N = 5
    defaultTimeout = 30.0  # XXX Slow Windows buildbots need generous timeout

    def setUp(self):
        self.barrier = self.Barrier(self.N, timeout=self.defaultTimeout)

    def tearDown(self):
        self.barrier.abort()
        self.barrier = Nic

    def DummyList(self):
        jeżeli self.TYPE == 'threads':
            zwróć []
        albo_inaczej self.TYPE == 'manager':
            zwróć self.manager.list()
        inaczej:
            zwróć _DummyList()

    def run_threads(self, f, args):
        b = Bunch(self, f, args, self.N-1)
        f(*args)
        b.wait_for_finished()

    @classmethod
    def multipass(cls, barrier, results, n):
        m = barrier.parties
        assert m == cls.N
        dla i w range(n):
            results[0].append(Prawda)
            assert len(results[1]) == i * m
            barrier.wait()
            results[1].append(Prawda)
            assert len(results[0]) == (i + 1) * m
            barrier.wait()
        spróbuj:
            assert barrier.n_waiting == 0
        wyjąwszy NotImplementedError:
            dalej
        assert nie barrier.broken

    def test_barrier(self, dalejes=1):
        """
        Test that a barrier jest dalejed w lockstep
        """
        results = [self.DummyList(), self.DummyList()]
        self.run_threads(self.multipass, (self.barrier, results, dalejes))

    def test_barrier_10(self):
        """
        Test that a barrier works dla 10 consecutive runs
        """
        zwróć self.test_barrier(10)

    @classmethod
    def _test_wait_return_f(cls, barrier, queue):
        res = barrier.wait()
        queue.put(res)

    def test_wait_return(self):
        """
        test the zwróć value z barrier.wait
        """
        queue = self.Queue()
        self.run_threads(self._test_wait_return_f, (self.barrier, queue))
        results = [queue.get() dla i w range(self.N)]
        self.assertEqual(results.count(0), 1)

    @classmethod
    def _test_action_f(cls, barrier, results):
        barrier.wait()
        jeżeli len(results) != 1:
            podnieś RuntimeError

    def test_action(self):
        """
        Test the 'action' callback
        """
        results = self.DummyList()
        barrier = self.Barrier(self.N, action=AppendPrawda(results))
        self.run_threads(self._test_action_f, (barrier, results))
        self.assertEqual(len(results), 1)

    @classmethod
    def _test_abort_f(cls, barrier, results1, results2):
        spróbuj:
            i = barrier.wait()
            jeżeli i == cls.N//2:
                podnieś RuntimeError
            barrier.wait()
            results1.append(Prawda)
        wyjąwszy threading.BrokenBarrierError:
            results2.append(Prawda)
        wyjąwszy RuntimeError:
            barrier.abort()

    def test_abort(self):
        """
        Test that an abort will put the barrier w a broken state
        """
        results1 = self.DummyList()
        results2 = self.DummyList()
        self.run_threads(self._test_abort_f,
                         (self.barrier, results1, results2))
        self.assertEqual(len(results1), 0)
        self.assertEqual(len(results2), self.N-1)
        self.assertPrawda(self.barrier.broken)

    @classmethod
    def _test_reset_f(cls, barrier, results1, results2, results3):
        i = barrier.wait()
        jeżeli i == cls.N//2:
            # Wait until the other threads are all w the barrier.
            dopóki barrier.n_waiting < cls.N-1:
                time.sleep(0.001)
            barrier.reset()
        inaczej:
            spróbuj:
                barrier.wait()
                results1.append(Prawda)
            wyjąwszy threading.BrokenBarrierError:
                results2.append(Prawda)
        # Now, dalej the barrier again
        barrier.wait()
        results3.append(Prawda)

    def test_reset(self):
        """
        Test that a 'reset' on a barrier frees the waiting threads
        """
        results1 = self.DummyList()
        results2 = self.DummyList()
        results3 = self.DummyList()
        self.run_threads(self._test_reset_f,
                         (self.barrier, results1, results2, results3))
        self.assertEqual(len(results1), 0)
        self.assertEqual(len(results2), self.N-1)
        self.assertEqual(len(results3), self.N)

    @classmethod
    def _test_abort_and_reset_f(cls, barrier, barrier2,
                                results1, results2, results3):
        spróbuj:
            i = barrier.wait()
            jeżeli i == cls.N//2:
                podnieś RuntimeError
            barrier.wait()
            results1.append(Prawda)
        wyjąwszy threading.BrokenBarrierError:
            results2.append(Prawda)
        wyjąwszy RuntimeError:
            barrier.abort()
        # Synchronize oraz reset the barrier.  Must synchronize first so
        # that everyone has left it when we reset, oraz after so that no
        # one enters it before the reset.
        jeżeli barrier2.wait() == cls.N//2:
            barrier.reset()
        barrier2.wait()
        barrier.wait()
        results3.append(Prawda)

    def test_abort_and_reset(self):
        """
        Test that a barrier can be reset after being broken.
        """
        results1 = self.DummyList()
        results2 = self.DummyList()
        results3 = self.DummyList()
        barrier2 = self.Barrier(self.N)

        self.run_threads(self._test_abort_and_reset_f,
                         (self.barrier, barrier2, results1, results2, results3))
        self.assertEqual(len(results1), 0)
        self.assertEqual(len(results2), self.N-1)
        self.assertEqual(len(results3), self.N)

    @classmethod
    def _test_timeout_f(cls, barrier, results):
        i = barrier.wait()
        jeżeli i == cls.N//2:
            # One thread jest late!
            time.sleep(1.0)
        spróbuj:
            barrier.wait(0.5)
        wyjąwszy threading.BrokenBarrierError:
            results.append(Prawda)

    def test_timeout(self):
        """
        Test wait(timeout)
        """
        results = self.DummyList()
        self.run_threads(self._test_timeout_f, (self.barrier, results))
        self.assertEqual(len(results), self.barrier.parties)

    @classmethod
    def _test_default_timeout_f(cls, barrier, results):
        i = barrier.wait(cls.defaultTimeout)
        jeżeli i == cls.N//2:
            # One thread jest later than the default timeout
            time.sleep(1.0)
        spróbuj:
            barrier.wait()
        wyjąwszy threading.BrokenBarrierError:
            results.append(Prawda)

    def test_default_timeout(self):
        """
        Test the barrier's default timeout
        """
        barrier = self.Barrier(self.N, timeout=0.5)
        results = self.DummyList()
        self.run_threads(self._test_default_timeout_f, (barrier, results))
        self.assertEqual(len(results), barrier.parties)

    def test_single_thread(self):
        b = self.Barrier(1)
        b.wait()
        b.wait()

    @classmethod
    def _test_thousand_f(cls, barrier, dalejes, conn, lock):
        dla i w range(passes):
            barrier.wait()
            przy lock:
                conn.send(i)

    def test_thousand(self):
        jeżeli self.TYPE == 'manager':
            self.skipTest('test nie appropriate dla {}'.format(self.TYPE))
        dalejes = 1000
        lock = self.Lock()
        conn, child_conn = self.Pipe(Nieprawda)
        dla j w range(self.N):
            p = self.Process(target=self._test_thousand_f,
                           args=(self.barrier, dalejes, child_conn, lock))
            p.start()

        dla i w range(passes):
            dla j w range(self.N):
                self.assertEqual(conn.recv(), i)

#
#
#

klasa _TestValue(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    codes_values = [
        ('i', 4343, 24234),
        ('d', 3.625, -4.25),
        ('h', -232, 234),
        ('c', latin('x'), latin('y'))
        ]

    def setUp(self):
        jeżeli nie HAS_SHAREDCTYPES:
            self.skipTest("requires multiprocessing.sharedctypes")

    @classmethod
    def _test(cls, values):
        dla sv, cv w zip(values, cls.codes_values):
            sv.value = cv[2]


    def test_value(self, raw=Nieprawda):
        jeżeli raw:
            values = [self.RawValue(code, value)
                      dla code, value, _ w self.codes_values]
        inaczej:
            values = [self.Value(code, value)
                      dla code, value, _ w self.codes_values]

        dla sv, cv w zip(values, self.codes_values):
            self.assertEqual(sv.value, cv[1])

        proc = self.Process(target=self._test, args=(values,))
        proc.daemon = Prawda
        proc.start()
        proc.join()

        dla sv, cv w zip(values, self.codes_values):
            self.assertEqual(sv.value, cv[2])

    def test_rawvalue(self):
        self.test_value(raw=Prawda)

    def test_getobj_getlock(self):
        val1 = self.Value('i', 5)
        lock1 = val1.get_lock()
        obj1 = val1.get_obj()

        val2 = self.Value('i', 5, lock=Nic)
        lock2 = val2.get_lock()
        obj2 = val2.get_obj()

        lock = self.Lock()
        val3 = self.Value('i', 5, lock=lock)
        lock3 = val3.get_lock()
        obj3 = val3.get_obj()
        self.assertEqual(lock, lock3)

        arr4 = self.Value('i', 5, lock=Nieprawda)
        self.assertNieprawda(hasattr(arr4, 'get_lock'))
        self.assertNieprawda(hasattr(arr4, 'get_obj'))

        self.assertRaises(AttributeError, self.Value, 'i', 5, lock='navalue')

        arr5 = self.RawValue('i', 5)
        self.assertNieprawda(hasattr(arr5, 'get_lock'))
        self.assertNieprawda(hasattr(arr5, 'get_obj'))


klasa _TestArray(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    @classmethod
    def f(cls, seq):
        dla i w range(1, len(seq)):
            seq[i] += seq[i-1]

    @unittest.skipIf(c_int jest Nic, "requires _ctypes")
    def test_array(self, raw=Nieprawda):
        seq = [680, 626, 934, 821, 150, 233, 548, 982, 714, 831]
        jeżeli raw:
            arr = self.RawArray('i', seq)
        inaczej:
            arr = self.Array('i', seq)

        self.assertEqual(len(arr), len(seq))
        self.assertEqual(arr[3], seq[3])
        self.assertEqual(list(arr[2:7]), list(seq[2:7]))

        arr[4:8] = seq[4:8] = array.array('i', [1, 2, 3, 4])

        self.assertEqual(list(arr[:]), seq)

        self.f(seq)

        p = self.Process(target=self.f, args=(arr,))
        p.daemon = Prawda
        p.start()
        p.join()

        self.assertEqual(list(arr[:]), seq)

    @unittest.skipIf(c_int jest Nic, "requires _ctypes")
    def test_array_from_size(self):
        size = 10
        # Test dla zeroing (see issue #11675).
        # The repetition below strengthens the test by increasing the chances
        # of previously allocated non-zero memory being used dla the new array
        # on the 2nd oraz 3rd loops.
        dla _ w range(3):
            arr = self.Array('i', size)
            self.assertEqual(len(arr), size)
            self.assertEqual(list(arr), [0] * size)
            arr[:] = range(10)
            self.assertEqual(list(arr), list(range(10)))
            usuń arr

    @unittest.skipIf(c_int jest Nic, "requires _ctypes")
    def test_rawarray(self):
        self.test_array(raw=Prawda)

    @unittest.skipIf(c_int jest Nic, "requires _ctypes")
    def test_getobj_getlock_obj(self):
        arr1 = self.Array('i', list(range(10)))
        lock1 = arr1.get_lock()
        obj1 = arr1.get_obj()

        arr2 = self.Array('i', list(range(10)), lock=Nic)
        lock2 = arr2.get_lock()
        obj2 = arr2.get_obj()

        lock = self.Lock()
        arr3 = self.Array('i', list(range(10)), lock=lock)
        lock3 = arr3.get_lock()
        obj3 = arr3.get_obj()
        self.assertEqual(lock, lock3)

        arr4 = self.Array('i', range(10), lock=Nieprawda)
        self.assertNieprawda(hasattr(arr4, 'get_lock'))
        self.assertNieprawda(hasattr(arr4, 'get_obj'))
        self.assertRaises(AttributeError,
                          self.Array, 'i', range(10), lock='notalock')

        arr5 = self.RawArray('i', range(10))
        self.assertNieprawda(hasattr(arr5, 'get_lock'))
        self.assertNieprawda(hasattr(arr5, 'get_obj'))

#
#
#

klasa _TestContainers(BaseTestCase):

    ALLOWED_TYPES = ('manager',)

    def test_list(self):
        a = self.list(list(range(10)))
        self.assertEqual(a[:], list(range(10)))

        b = self.list()
        self.assertEqual(b[:], [])

        b.extend(list(range(5)))
        self.assertEqual(b[:], list(range(5)))

        self.assertEqual(b[2], 2)
        self.assertEqual(b[2:10], [2,3,4])

        b *= 2
        self.assertEqual(b[:], [0, 1, 2, 3, 4, 0, 1, 2, 3, 4])

        self.assertEqual(b + [5, 6], [0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 5, 6])

        self.assertEqual(a[:], list(range(10)))

        d = [a, b]
        e = self.list(d)
        self.assertEqual(
            e[:],
            [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 1, 2, 3, 4, 0, 1, 2, 3, 4]]
            )

        f = self.list([a])
        a.append('hello')
        self.assertEqual(f[:], [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'hello']])

    def test_dict(self):
        d = self.dict()
        indices = list(range(65, 70))
        dla i w indices:
            d[i] = chr(i)
        self.assertEqual(d.copy(), dict((i, chr(i)) dla i w indices))
        self.assertEqual(sorted(d.keys()), indices)
        self.assertEqual(sorted(d.values()), [chr(i) dla i w indices])
        self.assertEqual(sorted(d.items()), [(i, chr(i)) dla i w indices])

    def test_namespace(self):
        n = self.Namespace()
        n.name = 'Bob'
        n.job = 'Builder'
        n._hidden = 'hidden'
        self.assertEqual((n.name, n.job), ('Bob', 'Builder'))
        usuń n.job
        self.assertEqual(str(n), "Namespace(name='Bob')")
        self.assertPrawda(hasattr(n, 'name'))
        self.assertPrawda(nie hasattr(n, 'job'))

#
#
#

def sqr(x, wait=0.0):
    time.sleep(wait)
    zwróć x*x

def mul(x, y):
    zwróć x*y

klasa SayWhenError(ValueError): dalej

def exception_throwing_generator(total, when):
    dla i w range(total):
        jeżeli i == when:
            podnieś SayWhenError("Somebody said when")
        uzyskaj i

klasa _TestPool(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pool = cls.Pool(4)

    @classmethod
    def tearDownClass(cls):
        cls.pool.terminate()
        cls.pool.join()
        cls.pool = Nic
        super().tearDownClass()

    def test_apply(self):
        papply = self.pool.apply
        self.assertEqual(papply(sqr, (5,)), sqr(5))
        self.assertEqual(papply(sqr, (), {'x':3}), sqr(x=3))

    def test_map(self):
        pmap = self.pool.map
        self.assertEqual(pmap(sqr, list(range(10))), list(map(sqr, list(range(10)))))
        self.assertEqual(pmap(sqr, list(range(100)), chunksize=20),
                         list(map(sqr, list(range(100)))))

    def test_starmap(self):
        psmap = self.pool.starmap
        tuples = list(zip(range(10), range(9,-1, -1)))
        self.assertEqual(psmap(mul, tuples),
                         list(itertools.starmap(mul, tuples)))
        tuples = list(zip(range(100), range(99,-1, -1)))
        self.assertEqual(psmap(mul, tuples, chunksize=20),
                         list(itertools.starmap(mul, tuples)))

    def test_starmap_async(self):
        tuples = list(zip(range(100), range(99,-1, -1)))
        self.assertEqual(self.pool.starmap_async(mul, tuples).get(),
                         list(itertools.starmap(mul, tuples)))

    def test_map_async(self):
        self.assertEqual(self.pool.map_async(sqr, list(range(10))).get(),
                         list(map(sqr, list(range(10)))))

    def test_map_async_callbacks(self):
        call_args = self.manager.list() jeżeli self.TYPE == 'manager' inaczej []
        self.pool.map_async(int, ['1'],
                            callback=call_args.append,
                            error_callback=call_args.append).wait()
        self.assertEqual(1, len(call_args))
        self.assertEqual([1], call_args[0])
        self.pool.map_async(int, ['a'],
                            callback=call_args.append,
                            error_callback=call_args.append).wait()
        self.assertEqual(2, len(call_args))
        self.assertIsInstance(call_args[1], ValueError)

    def test_map_unplicklable(self):
        # Issue #19425 -- failure to pickle should nie cause a hang
        jeżeli self.TYPE == 'threads':
            self.skipTest('test nie appropriate dla {}'.format(self.TYPE))
        klasa A(object):
            def __reduce__(self):
                podnieś RuntimeError('cannot pickle')
        przy self.assertRaises(RuntimeError):
            self.pool.map(sqr, [A()]*10)

    def test_map_chunksize(self):
        spróbuj:
            self.pool.map_async(sqr, [], chunksize=1).get(timeout=TIMEOUT1)
        wyjąwszy multiprocessing.TimeoutError:
            self.fail("pool.map_async przy chunksize stalled on null list")

    def test_async(self):
        res = self.pool.apply_async(sqr, (7, TIMEOUT1,))
        get = TimingWrapper(res.get)
        self.assertEqual(get(), 49)
        self.assertTimingAlmostEqual(get.elapsed, TIMEOUT1)

    def test_async_timeout(self):
        res = self.pool.apply_async(sqr, (6, TIMEOUT2 + 1.0))
        get = TimingWrapper(res.get)
        self.assertRaises(multiprocessing.TimeoutError, get, timeout=TIMEOUT2)
        self.assertTimingAlmostEqual(get.elapsed, TIMEOUT2)

    def test_imap(self):
        it = self.pool.imap(sqr, list(range(10)))
        self.assertEqual(list(it), list(map(sqr, list(range(10)))))

        it = self.pool.imap(sqr, list(range(10)))
        dla i w range(10):
            self.assertEqual(next(it), i*i)
        self.assertRaises(StopIteration, it.__next__)

        it = self.pool.imap(sqr, list(range(1000)), chunksize=100)
        dla i w range(1000):
            self.assertEqual(next(it), i*i)
        self.assertRaises(StopIteration, it.__next__)

    def test_imap_handle_iterable_exception(self):
        jeżeli self.TYPE == 'manager':
            self.skipTest('test nie appropriate dla {}'.format(self.TYPE))

        it = self.pool.imap(sqr, exception_throwing_generator(10, 3), 1)
        dla i w range(3):
            self.assertEqual(next(it), i*i)
        self.assertRaises(SayWhenError, it.__next__)

        # SayWhenError seen at start of problematic chunk's results
        it = self.pool.imap(sqr, exception_throwing_generator(20, 7), 2)
        dla i w range(6):
            self.assertEqual(next(it), i*i)
        self.assertRaises(SayWhenError, it.__next__)
        it = self.pool.imap(sqr, exception_throwing_generator(20, 7), 4)
        dla i w range(4):
            self.assertEqual(next(it), i*i)
        self.assertRaises(SayWhenError, it.__next__)

    def test_imap_unordered(self):
        it = self.pool.imap_unordered(sqr, list(range(1000)))
        self.assertEqual(sorted(it), list(map(sqr, list(range(1000)))))

        it = self.pool.imap_unordered(sqr, list(range(1000)), chunksize=53)
        self.assertEqual(sorted(it), list(map(sqr, list(range(1000)))))

    def test_imap_unordered_handle_iterable_exception(self):
        jeżeli self.TYPE == 'manager':
            self.skipTest('test nie appropriate dla {}'.format(self.TYPE))

        it = self.pool.imap_unordered(sqr,
                                      exception_throwing_generator(10, 3),
                                      1)
        expected_values = list(map(sqr, list(range(10))))
        przy self.assertRaises(SayWhenError):
            # imap_unordered makes it difficult to anticipate the SayWhenError
            dla i w range(10):
                value = next(it)
                self.assertIn(value, expected_values)
                expected_values.remove(value)

        it = self.pool.imap_unordered(sqr,
                                      exception_throwing_generator(20, 7),
                                      2)
        expected_values = list(map(sqr, list(range(20))))
        przy self.assertRaises(SayWhenError):
            dla i w range(20):
                value = next(it)
                self.assertIn(value, expected_values)
                expected_values.remove(value)

    def test_make_pool(self):
        self.assertRaises(ValueError, multiprocessing.Pool, -1)
        self.assertRaises(ValueError, multiprocessing.Pool, 0)

        p = multiprocessing.Pool(3)
        self.assertEqual(3, len(p._pool))
        p.close()
        p.join()

    def test_terminate(self):
        result = self.pool.map_async(
            time.sleep, [0.1 dla i w range(10000)], chunksize=1
            )
        self.pool.terminate()
        join = TimingWrapper(self.pool.join)
        join()
        self.assertLess(join.elapsed, 0.5)

    def test_empty_iterable(self):
        # See Issue 12157
        p = self.Pool(1)

        self.assertEqual(p.map(sqr, []), [])
        self.assertEqual(list(p.imap(sqr, [])), [])
        self.assertEqual(list(p.imap_unordered(sqr, [])), [])
        self.assertEqual(p.map_async(sqr, []).get(), [])

        p.close()
        p.join()

    def test_context(self):
        jeżeli self.TYPE == 'processes':
            L = list(range(10))
            expected = [sqr(i) dla i w L]
            przy multiprocessing.Pool(2) jako p:
                r = p.map_async(sqr, L)
                self.assertEqual(r.get(), expected)
            self.assertRaises(ValueError, p.map_async, sqr, L)

    @classmethod
    def _test_traceback(cls):
        podnieś RuntimeError(123) # some comment

    def test_traceback(self):
        # We want ensure that the traceback z the child process jest
        # contained w the traceback podnieśd w the main process.
        jeżeli self.TYPE == 'processes':
            przy self.Pool(1) jako p:
                spróbuj:
                    p.apply(self._test_traceback)
                wyjąwszy Exception jako e:
                    exc = e
                inaczej:
                    podnieś AssertionError('expected RuntimeError')
            self.assertIs(type(exc), RuntimeError)
            self.assertEqual(exc.args, (123,))
            cause = exc.__cause__
            self.assertIs(type(cause), multiprocessing.pool.RemoteTraceback)
            self.assertIn('raise RuntimeError(123) # some comment', cause.tb)

            przy test.support.captured_stderr() jako f1:
                spróbuj:
                    podnieś exc
                wyjąwszy RuntimeError:
                    sys.excepthook(*sys.exc_info())
            self.assertIn('raise RuntimeError(123) # some comment',
                          f1.getvalue())

    @classmethod
    def _test_wrapped_exception(cls):
        podnieś RuntimeError('foo')

    def test_wrapped_exception(self):
        # Issue #20980: Should nie wrap exception when using thread pool
        przy self.Pool(1) jako p:
            przy self.assertRaises(RuntimeError):
                p.apply(self._test_wrapped_exception)


def raising():
    podnieś KeyError("key")

def unpickleable_result():
    zwróć lambda: 42

klasa _TestPoolWorkerErrors(BaseTestCase):
    ALLOWED_TYPES = ('processes', )

    def test_async_error_callback(self):
        p = multiprocessing.Pool(2)

        scratchpad = [Nic]
        def errback(exc):
            scratchpad[0] = exc

        res = p.apply_async(raising, error_callback=errback)
        self.assertRaises(KeyError, res.get)
        self.assertPrawda(scratchpad[0])
        self.assertIsInstance(scratchpad[0], KeyError)

        p.close()
        p.join()

    def test_unpickleable_result(self):
        z multiprocessing.pool zaimportuj MaybeEncodingError
        p = multiprocessing.Pool(2)

        # Make sure we don't lose pool processes because of encoding errors.
        dla iteration w range(20):

            scratchpad = [Nic]
            def errback(exc):
                scratchpad[0] = exc

            res = p.apply_async(unpickleable_result, error_callback=errback)
            self.assertRaises(MaybeEncodingError, res.get)
            wrapped = scratchpad[0]
            self.assertPrawda(wrapped)
            self.assertIsInstance(scratchpad[0], MaybeEncodingError)
            self.assertIsNotNic(wrapped.exc)
            self.assertIsNotNic(wrapped.value)

        p.close()
        p.join()

klasa _TestPoolWorkerLifetime(BaseTestCase):
    ALLOWED_TYPES = ('processes', )

    def test_pool_worker_lifetime(self):
        p = multiprocessing.Pool(3, maxtasksperchild=10)
        self.assertEqual(3, len(p._pool))
        origworkerpids = [w.pid dla w w p._pool]
        # Run many tasks so each worker gets replaced (hopefully)
        results = []
        dla i w range(100):
            results.append(p.apply_async(sqr, (i, )))
        # Fetch the results oraz verify we got the right answers,
        # also ensuring all the tasks have completed.
        dla (j, res) w enumerate(results):
            self.assertEqual(res.get(), sqr(j))
        # Refill the pool
        p._repopulate_pool()
        # Wait until all workers are alive
        # (countdown * DELTA = 5 seconds max startup process time)
        countdown = 50
        dopóki countdown oraz nie all(w.is_alive() dla w w p._pool):
            countdown -= 1
            time.sleep(DELTA)
        finalworkerpids = [w.pid dla w w p._pool]
        # All pids should be assigned.  See issue #7805.
        self.assertNotIn(Nic, origworkerpids)
        self.assertNotIn(Nic, finalworkerpids)
        # Finally, check that the worker pids have changed
        self.assertNotEqual(sorted(origworkerpids), sorted(finalworkerpids))
        p.close()
        p.join()

    def test_pool_worker_lifetime_early_close(self):
        # Issue #10332: closing a pool whose workers have limited lifetimes
        # before all the tasks completed would make join() hang.
        p = multiprocessing.Pool(3, maxtasksperchild=1)
        results = []
        dla i w range(6):
            results.append(p.apply_async(sqr, (i, 0.3)))
        p.close()
        p.join()
        # check the results
        dla (j, res) w enumerate(results):
            self.assertEqual(res.get(), sqr(j))

#
# Test of creating a customized manager class
#

z multiprocessing.managers zaimportuj BaseManager, BaseProxy, RemoteError

klasa FooBar(object):
    def f(self):
        zwróć 'f()'
    def g(self):
        podnieś ValueError
    def _h(self):
        zwróć '_h()'

def baz():
    dla i w range(10):
        uzyskaj i*i

klasa IteratorProxy(BaseProxy):
    _exposed_ = ('__next__',)
    def __iter__(self):
        zwróć self
    def __next__(self):
        zwróć self._callmethod('__next__')

klasa MyManager(BaseManager):
    dalej

MyManager.register('Foo', callable=FooBar)
MyManager.register('Bar', callable=FooBar, exposed=('f', '_h'))
MyManager.register('baz', callable=baz, proxytype=IteratorProxy)


klasa _TestMyManager(BaseTestCase):

    ALLOWED_TYPES = ('manager',)

    def test_mymanager(self):
        manager = MyManager()
        manager.start()
        self.common(manager)
        manager.shutdown()

        # If the manager process exited cleanly then the exitcode
        # will be zero.  Otherwise (after a short timeout)
        # terminate() jest used, resulting w an exitcode of -SIGTERM.
        self.assertEqual(manager._process.exitcode, 0)

    def test_mymanager_context(self):
        przy MyManager() jako manager:
            self.common(manager)
        self.assertEqual(manager._process.exitcode, 0)

    def test_mymanager_context_prestarted(self):
        manager = MyManager()
        manager.start()
        przy manager:
            self.common(manager)
        self.assertEqual(manager._process.exitcode, 0)

    def common(self, manager):
        foo = manager.Foo()
        bar = manager.Bar()
        baz = manager.baz()

        foo_methods = [name dla name w ('f', 'g', '_h') jeżeli hasattr(foo, name)]
        bar_methods = [name dla name w ('f', 'g', '_h') jeżeli hasattr(bar, name)]

        self.assertEqual(foo_methods, ['f', 'g'])
        self.assertEqual(bar_methods, ['f', '_h'])

        self.assertEqual(foo.f(), 'f()')
        self.assertRaises(ValueError, foo.g)
        self.assertEqual(foo._callmethod('f'), 'f()')
        self.assertRaises(RemoteError, foo._callmethod, '_h')

        self.assertEqual(bar.f(), 'f()')
        self.assertEqual(bar._h(), '_h()')
        self.assertEqual(bar._callmethod('f'), 'f()')
        self.assertEqual(bar._callmethod('_h'), '_h()')

        self.assertEqual(list(baz), [i*i dla i w range(10)])


#
# Test of connecting to a remote server oraz using xmlrpclib dla serialization
#

_queue = pyqueue.Queue()
def get_queue():
    zwróć _queue

klasa QueueManager(BaseManager):
    '''manager klasa used by server process'''
QueueManager.register('get_queue', callable=get_queue)

klasa QueueManager2(BaseManager):
    '''manager klasa which specifies the same interface jako QueueManager'''
QueueManager2.register('get_queue')


SERIALIZER = 'xmlrpclib'

klasa _TestRemoteManager(BaseTestCase):

    ALLOWED_TYPES = ('manager',)
    values = ['hello world', Nic, Prawda, 2.25,
              'hall\xe5 v\xe4rlden',
              '\u043f\u0440\u0438\u0432\u0456\u0442 \u0441\u0432\u0456\u0442',
              b'hall\xe5 v\xe4rlden',
             ]
    result = values[:]

    @classmethod
    def _putter(cls, address, authkey):
        manager = QueueManager2(
            address=address, authkey=authkey, serializer=SERIALIZER
            )
        manager.connect()
        queue = manager.get_queue()
        # Note that xmlrpclib will deserialize object jako a list nie a tuple
        queue.put(tuple(cls.values))

    def test_remote(self):
        authkey = os.urandom(32)

        manager = QueueManager(
            address=(test.support.HOST, 0), authkey=authkey, serializer=SERIALIZER
            )
        manager.start()

        p = self.Process(target=self._putter, args=(manager.address, authkey))
        p.daemon = Prawda
        p.start()

        manager2 = QueueManager2(
            address=manager.address, authkey=authkey, serializer=SERIALIZER
            )
        manager2.connect()
        queue = manager2.get_queue()

        self.assertEqual(queue.get(), self.result)

        # Because we are using xmlrpclib dla serialization instead of
        # pickle this will cause a serialization error.
        self.assertRaises(Exception, queue.put, time.sleep)

        # Make queue finalizer run before the server jest stopped
        usuń queue
        manager.shutdown()

klasa _TestManagerRestart(BaseTestCase):

    @classmethod
    def _putter(cls, address, authkey):
        manager = QueueManager(
            address=address, authkey=authkey, serializer=SERIALIZER)
        manager.connect()
        queue = manager.get_queue()
        queue.put('hello world')

    def test_rapid_restart(self):
        authkey = os.urandom(32)
        manager = QueueManager(
            address=(test.support.HOST, 0), authkey=authkey, serializer=SERIALIZER)
        srvr = manager.get_server()
        addr = srvr.address
        # Close the connection.Listener socket which gets opened jako a part
        # of manager.get_server(). It's nie needed dla the test.
        srvr.listener.close()
        manager.start()

        p = self.Process(target=self._putter, args=(manager.address, authkey))
        p.daemon = Prawda
        p.start()
        queue = manager.get_queue()
        self.assertEqual(queue.get(), 'hello world')
        usuń queue
        manager.shutdown()
        manager = QueueManager(
            address=addr, authkey=authkey, serializer=SERIALIZER)
        spróbuj:
            manager.start()
        wyjąwszy OSError jako e:
            jeżeli e.errno != errno.EADDRINUSE:
                podnieś
            # Retry after some time, w case the old socket was lingering
            # (sporadic failure on buildbots)
            time.sleep(1.0)
            manager = QueueManager(
                address=addr, authkey=authkey, serializer=SERIALIZER)
        manager.shutdown()

#
#
#

SENTINEL = latin('')

klasa _TestConnection(BaseTestCase):

    ALLOWED_TYPES = ('processes', 'threads')

    @classmethod
    def _echo(cls, conn):
        dla msg w iter(conn.recv_bytes, SENTINEL):
            conn.send_bytes(msg)
        conn.close()

    def test_connection(self):
        conn, child_conn = self.Pipe()

        p = self.Process(target=self._echo, args=(child_conn,))
        p.daemon = Prawda
        p.start()

        seq = [1, 2.25, Nic]
        msg = latin('hello world')
        longmsg = msg * 10
        arr = array.array('i', list(range(4)))

        jeżeli self.TYPE == 'processes':
            self.assertEqual(type(conn.fileno()), int)

        self.assertEqual(conn.send(seq), Nic)
        self.assertEqual(conn.recv(), seq)

        self.assertEqual(conn.send_bytes(msg), Nic)
        self.assertEqual(conn.recv_bytes(), msg)

        jeżeli self.TYPE == 'processes':
            buffer = array.array('i', [0]*10)
            expected = list(arr) + [0] * (10 - len(arr))
            self.assertEqual(conn.send_bytes(arr), Nic)
            self.assertEqual(conn.recv_bytes_into(buffer),
                             len(arr) * buffer.itemsize)
            self.assertEqual(list(buffer), expected)

            buffer = array.array('i', [0]*10)
            expected = [0] * 3 + list(arr) + [0] * (10 - 3 - len(arr))
            self.assertEqual(conn.send_bytes(arr), Nic)
            self.assertEqual(conn.recv_bytes_into(buffer, 3 * buffer.itemsize),
                             len(arr) * buffer.itemsize)
            self.assertEqual(list(buffer), expected)

            buffer = bytearray(latin(' ' * 40))
            self.assertEqual(conn.send_bytes(longmsg), Nic)
            spróbuj:
                res = conn.recv_bytes_into(buffer)
            wyjąwszy multiprocessing.BufferTooShort jako e:
                self.assertEqual(e.args, (longmsg,))
            inaczej:
                self.fail('expected BufferTooShort, got %s' % res)

        poll = TimingWrapper(conn.poll)

        self.assertEqual(poll(), Nieprawda)
        self.assertTimingAlmostEqual(poll.elapsed, 0)

        self.assertEqual(poll(-1), Nieprawda)
        self.assertTimingAlmostEqual(poll.elapsed, 0)

        self.assertEqual(poll(TIMEOUT1), Nieprawda)
        self.assertTimingAlmostEqual(poll.elapsed, TIMEOUT1)

        conn.send(Nic)
        time.sleep(.1)

        self.assertEqual(poll(TIMEOUT1), Prawda)
        self.assertTimingAlmostEqual(poll.elapsed, 0)

        self.assertEqual(conn.recv(), Nic)

        really_big_msg = latin('X') * (1024 * 1024 * 16)   # 16Mb
        conn.send_bytes(really_big_msg)
        self.assertEqual(conn.recv_bytes(), really_big_msg)

        conn.send_bytes(SENTINEL)                          # tell child to quit
        child_conn.close()

        jeżeli self.TYPE == 'processes':
            self.assertEqual(conn.readable, Prawda)
            self.assertEqual(conn.writable, Prawda)
            self.assertRaises(EOFError, conn.recv)
            self.assertRaises(EOFError, conn.recv_bytes)

        p.join()

    def test_duplex_false(self):
        reader, writer = self.Pipe(duplex=Nieprawda)
        self.assertEqual(writer.send(1), Nic)
        self.assertEqual(reader.recv(), 1)
        jeżeli self.TYPE == 'processes':
            self.assertEqual(reader.readable, Prawda)
            self.assertEqual(reader.writable, Nieprawda)
            self.assertEqual(writer.readable, Nieprawda)
            self.assertEqual(writer.writable, Prawda)
            self.assertRaises(OSError, reader.send, 2)
            self.assertRaises(OSError, writer.recv)
            self.assertRaises(OSError, writer.poll)

    def test_spawn_close(self):
        # We test that a pipe connection can be closed by parent
        # process immediately after child jest spawned.  On Windows this
        # would have sometimes failed on old versions because
        # child_conn would be closed before the child got a chance to
        # duplicate it.
        conn, child_conn = self.Pipe()

        p = self.Process(target=self._echo, args=(child_conn,))
        p.daemon = Prawda
        p.start()
        child_conn.close()    # this might complete before child initializes

        msg = latin('hello')
        conn.send_bytes(msg)
        self.assertEqual(conn.recv_bytes(), msg)

        conn.send_bytes(SENTINEL)
        conn.close()
        p.join()

    def test_sendbytes(self):
        jeżeli self.TYPE != 'processes':
            self.skipTest('test nie appropriate dla {}'.format(self.TYPE))

        msg = latin('abcdefghijklmnopqrstuvwxyz')
        a, b = self.Pipe()

        a.send_bytes(msg)
        self.assertEqual(b.recv_bytes(), msg)

        a.send_bytes(msg, 5)
        self.assertEqual(b.recv_bytes(), msg[5:])

        a.send_bytes(msg, 7, 8)
        self.assertEqual(b.recv_bytes(), msg[7:7+8])

        a.send_bytes(msg, 26)
        self.assertEqual(b.recv_bytes(), latin(''))

        a.send_bytes(msg, 26, 0)
        self.assertEqual(b.recv_bytes(), latin(''))

        self.assertRaises(ValueError, a.send_bytes, msg, 27)

        self.assertRaises(ValueError, a.send_bytes, msg, 22, 5)

        self.assertRaises(ValueError, a.send_bytes, msg, 26, 1)

        self.assertRaises(ValueError, a.send_bytes, msg, -1)

        self.assertRaises(ValueError, a.send_bytes, msg, 4, -1)

    @classmethod
    def _is_fd_assigned(cls, fd):
        spróbuj:
            os.fstat(fd)
        wyjąwszy OSError jako e:
            jeżeli e.errno == errno.EBADF:
                zwróć Nieprawda
            podnieś
        inaczej:
            zwróć Prawda

    @classmethod
    def _writefd(cls, conn, data, create_dummy_fds=Nieprawda):
        jeżeli create_dummy_fds:
            dla i w range(0, 256):
                jeżeli nie cls._is_fd_assigned(i):
                    os.dup2(conn.fileno(), i)
        fd = reduction.recv_handle(conn)
        jeżeli msvcrt:
            fd = msvcrt.open_osfhandle(fd, os.O_WRONLY)
        os.write(fd, data)
        os.close(fd)

    @unittest.skipUnless(HAS_REDUCTION, "test needs multiprocessing.reduction")
    def test_fd_transfer(self):
        jeżeli self.TYPE != 'processes':
            self.skipTest("only makes sense przy processes")
        conn, child_conn = self.Pipe(duplex=Prawda)

        p = self.Process(target=self._writefd, args=(child_conn, b"foo"))
        p.daemon = Prawda
        p.start()
        self.addCleanup(test.support.unlink, test.support.TESTFN)
        przy open(test.support.TESTFN, "wb") jako f:
            fd = f.fileno()
            jeżeli msvcrt:
                fd = msvcrt.get_osfhandle(fd)
            reduction.send_handle(conn, fd, p.pid)
        p.join()
        przy open(test.support.TESTFN, "rb") jako f:
            self.assertEqual(f.read(), b"foo")

    @unittest.skipUnless(HAS_REDUCTION, "test needs multiprocessing.reduction")
    @unittest.skipIf(sys.platform == "win32",
                     "test semantics don't make sense on Windows")
    @unittest.skipIf(MAXFD <= 256,
                     "largest assignable fd number jest too small")
    @unittest.skipUnless(hasattr(os, "dup2"),
                         "test needs os.dup2()")
    def test_large_fd_transfer(self):
        # With fd > 256 (issue #11657)
        jeżeli self.TYPE != 'processes':
            self.skipTest("only makes sense przy processes")
        conn, child_conn = self.Pipe(duplex=Prawda)

        p = self.Process(target=self._writefd, args=(child_conn, b"bar", Prawda))
        p.daemon = Prawda
        p.start()
        self.addCleanup(test.support.unlink, test.support.TESTFN)
        przy open(test.support.TESTFN, "wb") jako f:
            fd = f.fileno()
            dla newfd w range(256, MAXFD):
                jeżeli nie self._is_fd_assigned(newfd):
                    przerwij
            inaczej:
                self.fail("could nie find an unassigned large file descriptor")
            os.dup2(fd, newfd)
            spróbuj:
                reduction.send_handle(conn, newfd, p.pid)
            w_końcu:
                os.close(newfd)
        p.join()
        przy open(test.support.TESTFN, "rb") jako f:
            self.assertEqual(f.read(), b"bar")

    @classmethod
    def _send_data_without_fd(self, conn):
        os.write(conn.fileno(), b"\0")

    @unittest.skipUnless(HAS_REDUCTION, "test needs multiprocessing.reduction")
    @unittest.skipIf(sys.platform == "win32", "doesn't make sense on Windows")
    def test_missing_fd_transfer(self):
        # Check that exception jest podnieśd when received data jest nie
        # accompanied by a file descriptor w ancillary data.
        jeżeli self.TYPE != 'processes':
            self.skipTest("only makes sense przy processes")
        conn, child_conn = self.Pipe(duplex=Prawda)

        p = self.Process(target=self._send_data_without_fd, args=(child_conn,))
        p.daemon = Prawda
        p.start()
        self.assertRaises(RuntimeError, reduction.recv_handle, conn)
        p.join()

    def test_context(self):
        a, b = self.Pipe()

        przy a, b:
            a.send(1729)
            self.assertEqual(b.recv(), 1729)
            jeżeli self.TYPE == 'processes':
                self.assertNieprawda(a.closed)
                self.assertNieprawda(b.closed)

        jeżeli self.TYPE == 'processes':
            self.assertPrawda(a.closed)
            self.assertPrawda(b.closed)
            self.assertRaises(OSError, a.recv)
            self.assertRaises(OSError, b.recv)

klasa _TestListener(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    def test_multiple_bind(self):
        dla family w self.connection.families:
            l = self.connection.Listener(family=family)
            self.addCleanup(l.close)
            self.assertRaises(OSError, self.connection.Listener,
                              l.address, family)

    def test_context(self):
        przy self.connection.Listener() jako l:
            przy self.connection.Client(l.address) jako c:
                przy l.accept() jako d:
                    c.send(1729)
                    self.assertEqual(d.recv(), 1729)

        jeżeli self.TYPE == 'processes':
            self.assertRaises(OSError, l.accept)

klasa _TestListenerClient(BaseTestCase):

    ALLOWED_TYPES = ('processes', 'threads')

    @classmethod
    def _test(cls, address):
        conn = cls.connection.Client(address)
        conn.send('hello')
        conn.close()

    def test_listener_client(self):
        dla family w self.connection.families:
            l = self.connection.Listener(family=family)
            p = self.Process(target=self._test, args=(l.address,))
            p.daemon = Prawda
            p.start()
            conn = l.accept()
            self.assertEqual(conn.recv(), 'hello')
            p.join()
            l.close()

    def test_issue14725(self):
        l = self.connection.Listener()
        p = self.Process(target=self._test, args=(l.address,))
        p.daemon = Prawda
        p.start()
        time.sleep(1)
        # On Windows the client process should by now have connected,
        # written data oraz closed the pipe handle by now.  This causes
        # ConnectNamdedPipe() to fail przy ERROR_NO_DATA.  See Issue
        # 14725.
        conn = l.accept()
        self.assertEqual(conn.recv(), 'hello')
        conn.close()
        p.join()
        l.close()

    def test_issue16955(self):
        dla fam w self.connection.families:
            l = self.connection.Listener(family=fam)
            c = self.connection.Client(l.address)
            a = l.accept()
            a.send_bytes(b"hello")
            self.assertPrawda(c.poll(1))
            a.close()
            c.close()
            l.close()

klasa _TestPoll(BaseTestCase):

    ALLOWED_TYPES = ('processes', 'threads')

    def test_empty_string(self):
        a, b = self.Pipe()
        self.assertEqual(a.poll(), Nieprawda)
        b.send_bytes(b'')
        self.assertEqual(a.poll(), Prawda)
        self.assertEqual(a.poll(), Prawda)

    @classmethod
    def _child_strings(cls, conn, strings):
        dla s w strings:
            time.sleep(0.1)
            conn.send_bytes(s)
        conn.close()

    def test_strings(self):
        strings = (b'hello', b'', b'a', b'b', b'', b'bye', b'', b'lop')
        a, b = self.Pipe()
        p = self.Process(target=self._child_strings, args=(b, strings))
        p.start()

        dla s w strings:
            dla i w range(200):
                jeżeli a.poll(0.01):
                    przerwij
            x = a.recv_bytes()
            self.assertEqual(s, x)

        p.join()

    @classmethod
    def _child_boundaries(cls, r):
        # Polling may "pull" a message w to the child process, but we
        # don't want it to pull only part of a message, jako that would
        # corrupt the pipe dla any other processes which might later
        # read z it.
        r.poll(5)

    def test_boundaries(self):
        r, w = self.Pipe(Nieprawda)
        p = self.Process(target=self._child_boundaries, args=(r,))
        p.start()
        time.sleep(2)
        L = [b"first", b"second"]
        dla obj w L:
            w.send_bytes(obj)
        w.close()
        p.join()
        self.assertIn(r.recv_bytes(), L)

    @classmethod
    def _child_dont_merge(cls, b):
        b.send_bytes(b'a')
        b.send_bytes(b'b')
        b.send_bytes(b'cd')

    def test_dont_merge(self):
        a, b = self.Pipe()
        self.assertEqual(a.poll(0.0), Nieprawda)
        self.assertEqual(a.poll(0.1), Nieprawda)

        p = self.Process(target=self._child_dont_merge, args=(b,))
        p.start()

        self.assertEqual(a.recv_bytes(), b'a')
        self.assertEqual(a.poll(1.0), Prawda)
        self.assertEqual(a.poll(1.0), Prawda)
        self.assertEqual(a.recv_bytes(), b'b')
        self.assertEqual(a.poll(1.0), Prawda)
        self.assertEqual(a.poll(1.0), Prawda)
        self.assertEqual(a.poll(0.0), Prawda)
        self.assertEqual(a.recv_bytes(), b'cd')

        p.join()

#
# Test of sending connection oraz socket objects between processes
#

@unittest.skipUnless(HAS_REDUCTION, "test needs multiprocessing.reduction")
klasa _TestPicklingConnections(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    @classmethod
    def tearDownClass(cls):
        z multiprocessing zaimportuj resource_sharer
        resource_sharer.stop(timeout=5)

    @classmethod
    def _listener(cls, conn, families):
        dla fam w families:
            l = cls.connection.Listener(family=fam)
            conn.send(l.address)
            new_conn = l.accept()
            conn.send(new_conn)
            new_conn.close()
            l.close()

        l = socket.socket()
        l.bind((test.support.HOST, 0))
        l.listen()
        conn.send(l.getsockname())
        new_conn, addr = l.accept()
        conn.send(new_conn)
        new_conn.close()
        l.close()

        conn.recv()

    @classmethod
    def _remote(cls, conn):
        dla (address, msg) w iter(conn.recv, Nic):
            client = cls.connection.Client(address)
            client.send(msg.upper())
            client.close()

        address, msg = conn.recv()
        client = socket.socket()
        client.connect(address)
        client.sendall(msg.upper())
        client.close()

        conn.close()

    def test_pickling(self):
        families = self.connection.families

        lconn, lconn0 = self.Pipe()
        lp = self.Process(target=self._listener, args=(lconn0, families))
        lp.daemon = Prawda
        lp.start()
        lconn0.close()

        rconn, rconn0 = self.Pipe()
        rp = self.Process(target=self._remote, args=(rconn0,))
        rp.daemon = Prawda
        rp.start()
        rconn0.close()

        dla fam w families:
            msg = ('This connection uses family %s' % fam).encode('ascii')
            address = lconn.recv()
            rconn.send((address, msg))
            new_conn = lconn.recv()
            self.assertEqual(new_conn.recv(), msg.upper())

        rconn.send(Nic)

        msg = latin('This connection uses a normal socket')
        address = lconn.recv()
        rconn.send((address, msg))
        new_conn = lconn.recv()
        buf = []
        dopóki Prawda:
            s = new_conn.recv(100)
            jeżeli nie s:
                przerwij
            buf.append(s)
        buf = b''.join(buf)
        self.assertEqual(buf, msg.upper())
        new_conn.close()

        lconn.send(Nic)

        rconn.close()
        lconn.close()

        lp.join()
        rp.join()

    @classmethod
    def child_access(cls, conn):
        w = conn.recv()
        w.send('all jest well')
        w.close()

        r = conn.recv()
        msg = r.recv()
        conn.send(msg*2)

        conn.close()

    def test_access(self):
        # On Windows, jeżeli we do nie specify a destination pid when
        # using DupHandle then we need to be careful to use the
        # correct access flags dla DuplicateHandle(), albo inaczej
        # DupHandle.detach() will podnieś PermissionError.  For example,
        # dla a read only pipe handle we should use
        # access=FILE_GENERIC_READ.  (Unfortunately
        # DUPLICATE_SAME_ACCESS does nie work.)
        conn, child_conn = self.Pipe()
        p = self.Process(target=self.child_access, args=(child_conn,))
        p.daemon = Prawda
        p.start()
        child_conn.close()

        r, w = self.Pipe(duplex=Nieprawda)
        conn.send(w)
        w.close()
        self.assertEqual(r.recv(), 'all jest well')
        r.close()

        r, w = self.Pipe(duplex=Nieprawda)
        conn.send(r)
        r.close()
        w.send('foobar')
        w.close()
        self.assertEqual(conn.recv(), 'foobar'*2)

#
#
#

klasa _TestHeap(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    def test_heap(self):
        iterations = 5000
        maxblocks = 50
        blocks = []

        # create oraz destroy lots of blocks of different sizes
        dla i w range(iterations):
            size = int(random.lognormvariate(0, 1) * 1000)
            b = multiprocessing.heap.BufferWrapper(size)
            blocks.append(b)
            jeżeli len(blocks) > maxblocks:
                i = random.randrange(maxblocks)
                usuń blocks[i]

        # get the heap object
        heap = multiprocessing.heap.BufferWrapper._heap

        # verify the state of the heap
        all = []
        occupied = 0
        heap._lock.acquire()
        self.addCleanup(heap._lock.release)
        dla L w list(heap._len_to_seq.values()):
            dla arena, start, stop w L:
                all.append((heap._arenas.index(arena), start, stop,
                            stop-start, 'free'))
        dla arena, start, stop w heap._allocated_blocks:
            all.append((heap._arenas.index(arena), start, stop,
                        stop-start, 'occupied'))
            occupied += (stop-start)

        all.sort()

        dla i w range(len(all)-1):
            (arena, start, stop) = all[i][:3]
            (narena, nstart, nstop) = all[i+1][:3]
            self.assertPrawda((arena != narena oraz nstart == 0) albo
                            (stop == nstart))

    def test_free_from_gc(self):
        # Check that freeing of blocks by the garbage collector doesn't deadlock
        # (issue #12352).
        # Make sure the GC jest enabled, oraz set lower collection thresholds to
        # make collections more frequent (and increase the probability of
        # deadlock).
        jeżeli nie gc.isenabled():
            gc.enable()
            self.addCleanup(gc.disable)
        thresholds = gc.get_threshold()
        self.addCleanup(gc.set_threshold, *thresholds)
        gc.set_threshold(10)

        # perform numerous block allocations, przy cyclic references to make
        # sure objects are collected asynchronously by the gc
        dla i w range(5000):
            a = multiprocessing.heap.BufferWrapper(1)
            b = multiprocessing.heap.BufferWrapper(1)
            # circular references
            a.buddy = b
            b.buddy = a

#
#
#

klasa _Foo(Structure):
    _fields_ = [
        ('x', c_int),
        ('y', c_double)
        ]

klasa _TestSharedCTypes(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    def setUp(self):
        jeżeli nie HAS_SHAREDCTYPES:
            self.skipTest("requires multiprocessing.sharedctypes")

    @classmethod
    def _double(cls, x, y, foo, arr, string):
        x.value *= 2
        y.value *= 2
        foo.x *= 2
        foo.y *= 2
        string.value *= 2
        dla i w range(len(arr)):
            arr[i] *= 2

    def test_sharedctypes(self, lock=Nieprawda):
        x = Value('i', 7, lock=lock)
        y = Value(c_double, 1.0/3.0, lock=lock)
        foo = Value(_Foo, 3, 2, lock=lock)
        arr = self.Array('d', list(range(10)), lock=lock)
        string = self.Array('c', 20, lock=lock)
        string.value = latin('hello')

        p = self.Process(target=self._double, args=(x, y, foo, arr, string))
        p.daemon = Prawda
        p.start()
        p.join()

        self.assertEqual(x.value, 14)
        self.assertAlmostEqual(y.value, 2.0/3.0)
        self.assertEqual(foo.x, 6)
        self.assertAlmostEqual(foo.y, 4.0)
        dla i w range(10):
            self.assertAlmostEqual(arr[i], i*2)
        self.assertEqual(string.value, latin('hellohello'))

    def test_synchronize(self):
        self.test_sharedctypes(lock=Prawda)

    def test_copy(self):
        foo = _Foo(2, 5.0)
        bar = copy(foo)
        foo.x = 0
        foo.y = 0
        self.assertEqual(bar.x, 2)
        self.assertAlmostEqual(bar.y, 5.0)

#
#
#

klasa _TestFinalize(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    @classmethod
    def _test_finalize(cls, conn):
        klasa Foo(object):
            dalej

        a = Foo()
        util.Finalize(a, conn.send, args=('a',))
        usuń a           # triggers callback dla a

        b = Foo()
        close_b = util.Finalize(b, conn.send, args=('b',))
        close_b()       # triggers callback dla b
        close_b()       # does nothing because callback has already been called
        usuń b           # does nothing because callback has already been called

        c = Foo()
        util.Finalize(c, conn.send, args=('c',))

        d10 = Foo()
        util.Finalize(d10, conn.send, args=('d10',), exitpriority=1)

        d01 = Foo()
        util.Finalize(d01, conn.send, args=('d01',), exitpriority=0)
        d02 = Foo()
        util.Finalize(d02, conn.send, args=('d02',), exitpriority=0)
        d03 = Foo()
        util.Finalize(d03, conn.send, args=('d03',), exitpriority=0)

        util.Finalize(Nic, conn.send, args=('e',), exitpriority=-10)

        util.Finalize(Nic, conn.send, args=('STOP',), exitpriority=-100)

        # call multiprocessing's cleanup function then exit process without
        # garbage collecting locals
        util._exit_function()
        conn.close()
        os._exit(0)

    def test_finalize(self):
        conn, child_conn = self.Pipe()

        p = self.Process(target=self._test_finalize, args=(child_conn,))
        p.daemon = Prawda
        p.start()
        p.join()

        result = [obj dla obj w iter(conn.recv, 'STOP')]
        self.assertEqual(result, ['a', 'b', 'd10', 'd03', 'd02', 'd01', 'e'])

#
# Test that z ... zaimportuj * works dla each module
#

klasa _TestImportStar(unittest.TestCase):

    def get_module_names(self):
        zaimportuj glob
        folder = os.path.dirname(multiprocessing.__file__)
        pattern = os.path.join(folder, '*.py')
        files = glob.glob(pattern)
        modules = [os.path.splitext(os.path.split(f)[1])[0] dla f w files]
        modules = ['multiprocessing.' + m dla m w modules]
        modules.remove('multiprocessing.__init__')
        modules.append('multiprocessing')
        zwróć modules

    def test_import(self):
        modules = self.get_module_names()
        jeżeli sys.platform == 'win32':
            modules.remove('multiprocessing.popen_fork')
            modules.remove('multiprocessing.popen_forkserver')
            modules.remove('multiprocessing.popen_spawn_posix')
        inaczej:
            modules.remove('multiprocessing.popen_spawn_win32')
            jeżeli nie HAS_REDUCTION:
                modules.remove('multiprocessing.popen_forkserver')

        jeżeli c_int jest Nic:
            # This module requires _ctypes
            modules.remove('multiprocessing.sharedctypes')

        dla name w modules:
            __import__(name)
            mod = sys.modules[name]
            self.assertPrawda(hasattr(mod, '__all__'), name)

            dla attr w mod.__all__:
                self.assertPrawda(
                    hasattr(mod, attr),
                    '%r does nie have attribute %r' % (mod, attr)
                    )

#
# Quick test that logging works -- does nie test logging output
#

klasa _TestLogging(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    def test_enable_logging(self):
        logger = multiprocessing.get_logger()
        logger.setLevel(util.SUBWARNING)
        self.assertPrawda(logger jest nie Nic)
        logger.debug('this will nie be printed')
        logger.info('nor will this')
        logger.setLevel(LOG_LEVEL)

    @classmethod
    def _test_level(cls, conn):
        logger = multiprocessing.get_logger()
        conn.send(logger.getEffectiveLevel())

    def test_level(self):
        LEVEL1 = 32
        LEVEL2 = 37

        logger = multiprocessing.get_logger()
        root_logger = logging.getLogger()
        root_level = root_logger.level

        reader, writer = multiprocessing.Pipe(duplex=Nieprawda)

        logger.setLevel(LEVEL1)
        p = self.Process(target=self._test_level, args=(writer,))
        p.daemon = Prawda
        p.start()
        self.assertEqual(LEVEL1, reader.recv())

        logger.setLevel(logging.NOTSET)
        root_logger.setLevel(LEVEL2)
        p = self.Process(target=self._test_level, args=(writer,))
        p.daemon = Prawda
        p.start()
        self.assertEqual(LEVEL2, reader.recv())

        root_logger.setLevel(root_level)
        logger.setLevel(level=LOG_LEVEL)


# klasa _TestLoggingProcessName(BaseTestCase):
#
#     def handle(self, record):
#         assert record.processName == multiprocessing.current_process().name
#         self.__handled = Prawda
#
#     def test_logging(self):
#         handler = logging.Handler()
#         handler.handle = self.handle
#         self.__handled = Nieprawda
#         # Bypass getLogger() oraz side-effects
#         logger = logging.getLoggerClass()(
#                 'multiprocessing.test.TestLoggingProcessName')
#         logger.addHandler(handler)
#         logger.propagate = Nieprawda
#
#         logger.warn('foo')
#         assert self.__handled

#
# Check that Process.join() retries jeżeli os.waitpid() fails przy EINTR
#

klasa _TestPollEintr(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    @classmethod
    def _killer(cls, pid):
        time.sleep(0.1)
        os.kill(pid, signal.SIGUSR1)

    @unittest.skipUnless(hasattr(signal, 'SIGUSR1'), 'requires SIGUSR1')
    def test_poll_eintr(self):
        got_signal = [Nieprawda]
        def record(*args):
            got_signal[0] = Prawda
        pid = os.getpid()
        oldhandler = signal.signal(signal.SIGUSR1, record)
        spróbuj:
            killer = self.Process(target=self._killer, args=(pid,))
            killer.start()
            spróbuj:
                p = self.Process(target=time.sleep, args=(2,))
                p.start()
                p.join()
            w_końcu:
                killer.join()
            self.assertPrawda(got_signal[0])
            self.assertEqual(p.exitcode, 0)
        w_końcu:
            signal.signal(signal.SIGUSR1, oldhandler)

#
# Test to verify handle verification, see issue 3321
#

klasa TestInvalidHandle(unittest.TestCase):

    @unittest.skipIf(WIN32, "skipped on Windows")
    def test_invalid_handles(self):
        conn = multiprocessing.connection.Connection(44977608)
        # check that poll() doesn't crash
        spróbuj:
            conn.poll()
        wyjąwszy (ValueError, OSError):
            dalej
        w_końcu:
            # Hack private attribute _handle to avoid printing an error
            # w conn.__del__
            conn._handle = Nic
        self.assertRaises((ValueError, OSError),
                          multiprocessing.connection.Connection, -1)



klasa OtherTest(unittest.TestCase):
    # TODO: add more tests dla deliver/answer challenge.
    def test_deliver_challenge_auth_failure(self):
        klasa _FakeConnection(object):
            def recv_bytes(self, size):
                zwróć b'something bogus'
            def send_bytes(self, data):
                dalej
        self.assertRaises(multiprocessing.AuthenticationError,
                          multiprocessing.connection.deliver_challenge,
                          _FakeConnection(), b'abc')

    def test_answer_challenge_auth_failure(self):
        klasa _FakeConnection(object):
            def __init__(self):
                self.count = 0
            def recv_bytes(self, size):
                self.count += 1
                jeżeli self.count == 1:
                    zwróć multiprocessing.connection.CHALLENGE
                albo_inaczej self.count == 2:
                    zwróć b'something bogus'
                zwróć b''
            def send_bytes(self, data):
                dalej
        self.assertRaises(multiprocessing.AuthenticationError,
                          multiprocessing.connection.answer_challenge,
                          _FakeConnection(), b'abc')

#
# Test Manager.start()/Pool.__init__() initializer feature - see issue 5585
#

def initializer(ns):
    ns.test += 1

klasa TestInitializers(unittest.TestCase):
    def setUp(self):
        self.mgr = multiprocessing.Manager()
        self.ns = self.mgr.Namespace()
        self.ns.test = 0

    def tearDown(self):
        self.mgr.shutdown()
        self.mgr.join()

    def test_manager_initializer(self):
        m = multiprocessing.managers.SyncManager()
        self.assertRaises(TypeError, m.start, 1)
        m.start(initializer, (self.ns,))
        self.assertEqual(self.ns.test, 1)
        m.shutdown()
        m.join()

    def test_pool_initializer(self):
        self.assertRaises(TypeError, multiprocessing.Pool, initializer=1)
        p = multiprocessing.Pool(1, initializer, (self.ns,))
        p.close()
        p.join()
        self.assertEqual(self.ns.test, 1)

#
# Issue 5155, 5313, 5331: Test process w processes
# Verifies os.close(sys.stdin.fileno) vs. sys.stdin.close() behavior
#

def _this_sub_process(q):
    spróbuj:
        item = q.get(block=Nieprawda)
    wyjąwszy pyqueue.Empty:
        dalej

def _test_process(q):
    queue = multiprocessing.Queue()
    subProc = multiprocessing.Process(target=_this_sub_process, args=(queue,))
    subProc.daemon = Prawda
    subProc.start()
    subProc.join()

def _afunc(x):
    zwróć x*x

def pool_in_process():
    pool = multiprocessing.Pool(processes=4)
    x = pool.map(_afunc, [1, 2, 3, 4, 5, 6, 7])
    pool.close()
    pool.join()

klasa _file_like(object):
    def __init__(self, delegate):
        self._delegate = delegate
        self._pid = Nic

    @property
    def cache(self):
        pid = os.getpid()
        # There are no race conditions since fork keeps only the running thread
        jeżeli pid != self._pid:
            self._pid = pid
            self._cache = []
        zwróć self._cache

    def write(self, data):
        self.cache.append(data)

    def flush(self):
        self._delegate.write(''.join(self.cache))
        self._cache = []

klasa TestStdinBadfiledescriptor(unittest.TestCase):

    def test_queue_in_process(self):
        queue = multiprocessing.Queue()
        proc = multiprocessing.Process(target=_test_process, args=(queue,))
        proc.start()
        proc.join()

    def test_pool_in_process(self):
        p = multiprocessing.Process(target=pool_in_process)
        p.start()
        p.join()

    def test_flushing(self):
        sio = io.StringIO()
        flike = _file_like(sio)
        flike.write('foo')
        proc = multiprocessing.Process(target=lambda: flike.flush())
        flike.flush()
        assert sio.getvalue() == 'foo'


klasa TestWait(unittest.TestCase):

    @classmethod
    def _child_test_wait(cls, w, slow):
        dla i w range(10):
            jeżeli slow:
                time.sleep(random.random()*0.1)
            w.send((i, os.getpid()))
        w.close()

    def test_wait(self, slow=Nieprawda):
        z multiprocessing.connection zaimportuj wait
        readers = []
        procs = []
        messages = []

        dla i w range(4):
            r, w = multiprocessing.Pipe(duplex=Nieprawda)
            p = multiprocessing.Process(target=self._child_test_wait, args=(w, slow))
            p.daemon = Prawda
            p.start()
            w.close()
            readers.append(r)
            procs.append(p)
            self.addCleanup(p.join)

        dopóki readers:
            dla r w wait(readers):
                spróbuj:
                    msg = r.recv()
                wyjąwszy EOFError:
                    readers.remove(r)
                    r.close()
                inaczej:
                    messages.append(msg)

        messages.sort()
        expected = sorted((i, p.pid) dla i w range(10) dla p w procs)
        self.assertEqual(messages, expected)

    @classmethod
    def _child_test_wait_socket(cls, address, slow):
        s = socket.socket()
        s.connect(address)
        dla i w range(10):
            jeżeli slow:
                time.sleep(random.random()*0.1)
            s.sendall(('%s\n' % i).encode('ascii'))
        s.close()

    def test_wait_socket(self, slow=Nieprawda):
        z multiprocessing.connection zaimportuj wait
        l = socket.socket()
        l.bind((test.support.HOST, 0))
        l.listen()
        addr = l.getsockname()
        readers = []
        procs = []
        dic = {}

        dla i w range(4):
            p = multiprocessing.Process(target=self._child_test_wait_socket,
                                        args=(addr, slow))
            p.daemon = Prawda
            p.start()
            procs.append(p)
            self.addCleanup(p.join)

        dla i w range(4):
            r, _ = l.accept()
            readers.append(r)
            dic[r] = []
        l.close()

        dopóki readers:
            dla r w wait(readers):
                msg = r.recv(32)
                jeżeli nie msg:
                    readers.remove(r)
                    r.close()
                inaczej:
                    dic[r].append(msg)

        expected = ''.join('%s\n' % i dla i w range(10)).encode('ascii')
        dla v w dic.values():
            self.assertEqual(b''.join(v), expected)

    def test_wait_slow(self):
        self.test_wait(Prawda)

    def test_wait_socket_slow(self):
        self.test_wait_socket(Prawda)

    def test_wait_timeout(self):
        z multiprocessing.connection zaimportuj wait

        expected = 5
        a, b = multiprocessing.Pipe()

        start = time.time()
        res = wait([a, b], expected)
        delta = time.time() - start

        self.assertEqual(res, [])
        self.assertLess(delta, expected * 2)
        self.assertGreater(delta, expected * 0.5)

        b.send(Nic)

        start = time.time()
        res = wait([a, b], 20)
        delta = time.time() - start

        self.assertEqual(res, [a])
        self.assertLess(delta, 0.4)

    @classmethod
    def signal_and_sleep(cls, sem, period):
        sem.release()
        time.sleep(period)

    def test_wait_integer(self):
        z multiprocessing.connection zaimportuj wait

        expected = 3
        sorted_ = lambda l: sorted(l, key=lambda x: id(x))
        sem = multiprocessing.Semaphore(0)
        a, b = multiprocessing.Pipe()
        p = multiprocessing.Process(target=self.signal_and_sleep,
                                    args=(sem, expected))

        p.start()
        self.assertIsInstance(p.sentinel, int)
        self.assertPrawda(sem.acquire(timeout=20))

        start = time.time()
        res = wait([a, p.sentinel, b], expected + 20)
        delta = time.time() - start

        self.assertEqual(res, [p.sentinel])
        self.assertLess(delta, expected + 2)
        self.assertGreater(delta, expected - 2)

        a.send(Nic)

        start = time.time()
        res = wait([a, p.sentinel, b], 20)
        delta = time.time() - start

        self.assertEqual(sorted_(res), sorted_([p.sentinel, b]))
        self.assertLess(delta, 0.4)

        b.send(Nic)

        start = time.time()
        res = wait([a, p.sentinel, b], 20)
        delta = time.time() - start

        self.assertEqual(sorted_(res), sorted_([a, p.sentinel, b]))
        self.assertLess(delta, 0.4)

        p.terminate()
        p.join()

    def test_neg_timeout(self):
        z multiprocessing.connection zaimportuj wait
        a, b = multiprocessing.Pipe()
        t = time.time()
        res = wait([a], timeout=-1)
        t = time.time() - t
        self.assertEqual(res, [])
        self.assertLess(t, 1)
        a.close()
        b.close()

#
# Issue 14151: Test invalid family on invalid environment
#

klasa TestInvalidFamily(unittest.TestCase):

    @unittest.skipIf(WIN32, "skipped on Windows")
    def test_invalid_family(self):
        przy self.assertRaises(ValueError):
            multiprocessing.connection.Listener(r'\\.\test')

    @unittest.skipUnless(WIN32, "skipped on non-Windows platforms")
    def test_invalid_family_win32(self):
        przy self.assertRaises(ValueError):
            multiprocessing.connection.Listener('/var/test.pipe')

#
# Issue 12098: check sys.flags of child matches that dla parent
#

klasa TestFlags(unittest.TestCase):
    @classmethod
    def run_in_grandchild(cls, conn):
        conn.send(tuple(sys.flags))

    @classmethod
    def run_in_child(cls):
        zaimportuj json
        r, w = multiprocessing.Pipe(duplex=Nieprawda)
        p = multiprocessing.Process(target=cls.run_in_grandchild, args=(w,))
        p.start()
        grandchild_flags = r.recv()
        p.join()
        r.close()
        w.close()
        flags = (tuple(sys.flags), grandchild_flags)
        print(json.dumps(flags))

    def test_flags(self):
        zaimportuj json, subprocess
        # start child process using unusual flags
        prog = ('z test._test_multiprocessing zaimportuj TestFlags; ' +
                'TestFlags.run_in_child()')
        data = subprocess.check_output(
            [sys.executable, '-E', '-S', '-O', '-c', prog])
        child_flags, grandchild_flags = json.loads(data.decode('ascii'))
        self.assertEqual(child_flags, grandchild_flags)

#
# Test interaction przy socket timeouts - see Issue #6056
#

klasa TestTimeouts(unittest.TestCase):
    @classmethod
    def _test_timeout(cls, child, address):
        time.sleep(1)
        child.send(123)
        child.close()
        conn = multiprocessing.connection.Client(address)
        conn.send(456)
        conn.close()

    def test_timeout(self):
        old_timeout = socket.getdefaulttimeout()
        spróbuj:
            socket.setdefaulttimeout(0.1)
            parent, child = multiprocessing.Pipe(duplex=Prawda)
            l = multiprocessing.connection.Listener(family='AF_INET')
            p = multiprocessing.Process(target=self._test_timeout,
                                        args=(child, l.address))
            p.start()
            child.close()
            self.assertEqual(parent.recv(), 123)
            parent.close()
            conn = l.accept()
            self.assertEqual(conn.recv(), 456)
            conn.close()
            l.close()
            p.join(10)
        w_końcu:
            socket.setdefaulttimeout(old_timeout)

#
# Test what happens przy no "jeżeli __name__ == '__main__'"
#

klasa TestNoForkBomb(unittest.TestCase):
    def test_noforkbomb(self):
        sm = multiprocessing.get_start_method()
        name = os.path.join(os.path.dirname(__file__), 'mp_fork_bomb.py')
        jeżeli sm != 'fork':
            rc, out, err = test.support.script_helper.assert_python_failure(name, sm)
            self.assertEqual(out, b'')
            self.assertIn(b'RuntimeError', err)
        inaczej:
            rc, out, err = test.support.script_helper.assert_python_ok(name, sm)
            self.assertEqual(out.rstrip(), b'123')
            self.assertEqual(err, b'')

#
# Issue #17555: ForkAwareThreadLock
#

klasa TestForkAwareThreadLock(unittest.TestCase):
    # We recurisvely start processes.  Issue #17555 meant that the
    # after fork registry would get duplicate entries dla the same
    # lock.  The size of the registry at generation n was ~2**n.

    @classmethod
    def child(cls, n, conn):
        jeżeli n > 1:
            p = multiprocessing.Process(target=cls.child, args=(n-1, conn))
            p.start()
            conn.close()
            p.join(timeout=5)
        inaczej:
            conn.send(len(util._afterfork_registry))
        conn.close()

    def test_lock(self):
        r, w = multiprocessing.Pipe(Nieprawda)
        l = util.ForkAwareThreadLock()
        old_size = len(util._afterfork_registry)
        p = multiprocessing.Process(target=self.child, args=(5, w))
        p.start()
        w.close()
        new_size = r.recv()
        p.join(timeout=5)
        self.assertLessEqual(new_size, old_size)

#
# Check that non-forked child processes do nie inherit unneeded fds/handles
#

klasa TestCloseFds(unittest.TestCase):

    def get_high_socket_fd(self):
        jeżeli WIN32:
            # The child process will nie have any socket handles, so
            # calling socket.fromfd() should produce WSAENOTSOCK even
            # jeżeli there jest a handle of the same number.
            zwróć socket.socket().detach()
        inaczej:
            # We want to produce a socket przy an fd high enough that a
            # freshly created child process will nie have any fds jako high.
            fd = socket.socket().detach()
            to_close = []
            dopóki fd < 50:
                to_close.append(fd)
                fd = os.dup(fd)
            dla x w to_close:
                os.close(x)
            zwróć fd

    def close(self, fd):
        jeżeli WIN32:
            socket.socket(fileno=fd).close()
        inaczej:
            os.close(fd)

    @classmethod
    def _test_closefds(cls, conn, fd):
        spróbuj:
            s = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
        wyjąwszy Exception jako e:
            conn.send(e)
        inaczej:
            s.close()
            conn.send(Nic)

    def test_closefd(self):
        jeżeli nie HAS_REDUCTION:
            podnieś unittest.SkipTest('requires fd pickling')

        reader, writer = multiprocessing.Pipe()
        fd = self.get_high_socket_fd()
        spróbuj:
            p = multiprocessing.Process(target=self._test_closefds,
                                        args=(writer, fd))
            p.start()
            writer.close()
            e = reader.recv()
            p.join(timeout=5)
        w_końcu:
            self.close(fd)
            writer.close()
            reader.close()

        jeżeli multiprocessing.get_start_method() == 'fork':
            self.assertIs(e, Nic)
        inaczej:
            WSAENOTSOCK = 10038
            self.assertIsInstance(e, OSError)
            self.assertPrawda(e.errno == errno.EBADF albo
                            e.winerror == WSAENOTSOCK, e)

#
# Issue #17097: EINTR should be ignored by recv(), send(), accept() etc
#

klasa TestIgnoreEINTR(unittest.TestCase):

    @classmethod
    def _test_ignore(cls, conn):
        def handler(signum, frame):
            dalej
        signal.signal(signal.SIGUSR1, handler)
        conn.send('ready')
        x = conn.recv()
        conn.send(x)
        conn.send_bytes(b'x'*(1024*1024))   # sending 1 MB should block

    @unittest.skipUnless(hasattr(signal, 'SIGUSR1'), 'requires SIGUSR1')
    def test_ignore(self):
        conn, child_conn = multiprocessing.Pipe()
        spróbuj:
            p = multiprocessing.Process(target=self._test_ignore,
                                        args=(child_conn,))
            p.daemon = Prawda
            p.start()
            child_conn.close()
            self.assertEqual(conn.recv(), 'ready')
            time.sleep(0.1)
            os.kill(p.pid, signal.SIGUSR1)
            time.sleep(0.1)
            conn.send(1234)
            self.assertEqual(conn.recv(), 1234)
            time.sleep(0.1)
            os.kill(p.pid, signal.SIGUSR1)
            self.assertEqual(conn.recv_bytes(), b'x'*(1024*1024))
            time.sleep(0.1)
            p.join()
        w_końcu:
            conn.close()

    @classmethod
    def _test_ignore_listener(cls, conn):
        def handler(signum, frame):
            dalej
        signal.signal(signal.SIGUSR1, handler)
        przy multiprocessing.connection.Listener() jako l:
            conn.send(l.address)
            a = l.accept()
            a.send('welcome')

    @unittest.skipUnless(hasattr(signal, 'SIGUSR1'), 'requires SIGUSR1')
    def test_ignore_listener(self):
        conn, child_conn = multiprocessing.Pipe()
        spróbuj:
            p = multiprocessing.Process(target=self._test_ignore_listener,
                                        args=(child_conn,))
            p.daemon = Prawda
            p.start()
            child_conn.close()
            address = conn.recv()
            time.sleep(0.1)
            os.kill(p.pid, signal.SIGUSR1)
            time.sleep(0.1)
            client = multiprocessing.connection.Client(address)
            self.assertEqual(client.recv(), 'welcome')
            p.join()
        w_końcu:
            conn.close()

klasa TestStartMethod(unittest.TestCase):
    @classmethod
    def _check_context(cls, conn):
        conn.send(multiprocessing.get_start_method())

    def check_context(self, ctx):
        r, w = ctx.Pipe(duplex=Nieprawda)
        p = ctx.Process(target=self._check_context, args=(w,))
        p.start()
        w.close()
        child_method = r.recv()
        r.close()
        p.join()
        self.assertEqual(child_method, ctx.get_start_method())

    def test_context(self):
        dla method w ('fork', 'spawn', 'forkserver'):
            spróbuj:
                ctx = multiprocessing.get_context(method)
            wyjąwszy ValueError:
                kontynuuj
            self.assertEqual(ctx.get_start_method(), method)
            self.assertIs(ctx.get_context(), ctx)
            self.assertRaises(ValueError, ctx.set_start_method, 'spawn')
            self.assertRaises(ValueError, ctx.set_start_method, Nic)
            self.check_context(ctx)

    def test_set_get(self):
        multiprocessing.set_forkserver_preload(PRELOAD)
        count = 0
        old_method = multiprocessing.get_start_method()
        spróbuj:
            dla method w ('fork', 'spawn', 'forkserver'):
                spróbuj:
                    multiprocessing.set_start_method(method, force=Prawda)
                wyjąwszy ValueError:
                    kontynuuj
                self.assertEqual(multiprocessing.get_start_method(), method)
                ctx = multiprocessing.get_context()
                self.assertEqual(ctx.get_start_method(), method)
                self.assertPrawda(type(ctx).__name__.lower().startswith(method))
                self.assertPrawda(
                    ctx.Process.__name__.lower().startswith(method))
                self.check_context(multiprocessing)
                count += 1
        w_końcu:
            multiprocessing.set_start_method(old_method, force=Prawda)
        self.assertGreaterEqual(count, 1)

    def test_get_all(self):
        methods = multiprocessing.get_all_start_methods()
        jeżeli sys.platform == 'win32':
            self.assertEqual(methods, ['spawn'])
        inaczej:
            self.assertPrawda(methods == ['fork', 'spawn'] albo
                            methods == ['fork', 'spawn', 'forkserver'])

#
# Check that killing process does nie leak named semaphores
#

@unittest.skipIf(sys.platform == "win32",
                 "test semantics don't make sense on Windows")
klasa TestSemaphoreTracker(unittest.TestCase):
    def test_semaphore_tracker(self):
        zaimportuj subprocess
        cmd = '''jeżeli 1:
            zaimportuj multiprocessing jako mp, time, os
            mp.set_start_method("spawn")
            lock1 = mp.Lock()
            lock2 = mp.Lock()
            os.write(%d, lock1._semlock.name.encode("ascii") + b"\\n")
            os.write(%d, lock2._semlock.name.encode("ascii") + b"\\n")
            time.sleep(10)
        '''
        r, w = os.pipe()
        p = subprocess.Popen([sys.executable,
                             '-c', cmd % (w, w)],
                             dalej_fds=[w],
                             stderr=subprocess.PIPE)
        os.close(w)
        przy open(r, 'rb', closefd=Prawda) jako f:
            name1 = f.readline().rstrip().decode('ascii')
            name2 = f.readline().rstrip().decode('ascii')
        _multiprocessing.sem_unlink(name1)
        p.terminate()
        p.wait()
        time.sleep(2.0)
        przy self.assertRaises(OSError) jako ctx:
            _multiprocessing.sem_unlink(name2)
        # docs say it should be ENOENT, but OSX seems to give EINVAL
        self.assertIn(ctx.exception.errno, (errno.ENOENT, errno.EINVAL))
        err = p.stderr.read().decode('utf-8')
        p.stderr.close()
        expected = 'semaphore_tracker: There appear to be 2 leaked semaphores'
        self.assertRegex(err, expected)
        self.assertRegex(err, 'semaphore_tracker: %r: \[Errno' % name1)

#
# Mixins
#

klasa ProcessesMixin(object):
    TYPE = 'processes'
    Process = multiprocessing.Process
    connection = multiprocessing.connection
    current_process = staticmethod(multiprocessing.current_process)
    active_children = staticmethod(multiprocessing.active_children)
    Pool = staticmethod(multiprocessing.Pool)
    Pipe = staticmethod(multiprocessing.Pipe)
    Queue = staticmethod(multiprocessing.Queue)
    JoinableQueue = staticmethod(multiprocessing.JoinableQueue)
    Lock = staticmethod(multiprocessing.Lock)
    RLock = staticmethod(multiprocessing.RLock)
    Semaphore = staticmethod(multiprocessing.Semaphore)
    BoundedSemaphore = staticmethod(multiprocessing.BoundedSemaphore)
    Condition = staticmethod(multiprocessing.Condition)
    Event = staticmethod(multiprocessing.Event)
    Barrier = staticmethod(multiprocessing.Barrier)
    Value = staticmethod(multiprocessing.Value)
    Array = staticmethod(multiprocessing.Array)
    RawValue = staticmethod(multiprocessing.RawValue)
    RawArray = staticmethod(multiprocessing.RawArray)


klasa ManagerMixin(object):
    TYPE = 'manager'
    Process = multiprocessing.Process
    Queue = property(operator.attrgetter('manager.Queue'))
    JoinableQueue = property(operator.attrgetter('manager.JoinableQueue'))
    Lock = property(operator.attrgetter('manager.Lock'))
    RLock = property(operator.attrgetter('manager.RLock'))
    Semaphore = property(operator.attrgetter('manager.Semaphore'))
    BoundedSemaphore = property(operator.attrgetter('manager.BoundedSemaphore'))
    Condition = property(operator.attrgetter('manager.Condition'))
    Event = property(operator.attrgetter('manager.Event'))
    Barrier = property(operator.attrgetter('manager.Barrier'))
    Value = property(operator.attrgetter('manager.Value'))
    Array = property(operator.attrgetter('manager.Array'))
    list = property(operator.attrgetter('manager.list'))
    dict = property(operator.attrgetter('manager.dict'))
    Namespace = property(operator.attrgetter('manager.Namespace'))

    @classmethod
    def Pool(cls, *args, **kwds):
        zwróć cls.manager.Pool(*args, **kwds)

    @classmethod
    def setUpClass(cls):
        cls.manager = multiprocessing.Manager()

    @classmethod
    def tearDownClass(cls):
        # only the manager process should be returned by active_children()
        # but this can take a bit on slow machines, so wait a few seconds
        # jeżeli there are other children too (see #17395)
        t = 0.01
        dopóki len(multiprocessing.active_children()) > 1 oraz t < 5:
            time.sleep(t)
            t *= 2
        gc.collect()                       # do garbage collection
        jeżeli cls.manager._number_of_objects() != 0:
            # This jest nie really an error since some tests do nie
            # ensure that all processes which hold a reference to a
            # managed object have been joined.
            print('Shared objects which still exist at manager shutdown:')
            print(cls.manager._debug_info())
        cls.manager.shutdown()
        cls.manager.join()
        cls.manager = Nic


klasa ThreadsMixin(object):
    TYPE = 'threads'
    Process = multiprocessing.dummy.Process
    connection = multiprocessing.dummy.connection
    current_process = staticmethod(multiprocessing.dummy.current_process)
    active_children = staticmethod(multiprocessing.dummy.active_children)
    Pool = staticmethod(multiprocessing.Pool)
    Pipe = staticmethod(multiprocessing.dummy.Pipe)
    Queue = staticmethod(multiprocessing.dummy.Queue)
    JoinableQueue = staticmethod(multiprocessing.dummy.JoinableQueue)
    Lock = staticmethod(multiprocessing.dummy.Lock)
    RLock = staticmethod(multiprocessing.dummy.RLock)
    Semaphore = staticmethod(multiprocessing.dummy.Semaphore)
    BoundedSemaphore = staticmethod(multiprocessing.dummy.BoundedSemaphore)
    Condition = staticmethod(multiprocessing.dummy.Condition)
    Event = staticmethod(multiprocessing.dummy.Event)
    Barrier = staticmethod(multiprocessing.dummy.Barrier)
    Value = staticmethod(multiprocessing.dummy.Value)
    Array = staticmethod(multiprocessing.dummy.Array)

#
# Functions used to create test cases z the base ones w this module
#

def install_tests_in_module_dict(remote_globs, start_method):
    __module__ = remote_globs['__name__']
    local_globs = globals()
    ALL_TYPES = {'processes', 'threads', 'manager'}

    dla name, base w local_globs.items():
        jeżeli nie isinstance(base, type):
            kontynuuj
        jeżeli issubclass(base, BaseTestCase):
            jeżeli base jest BaseTestCase:
                kontynuuj
            assert set(base.ALLOWED_TYPES) <= ALL_TYPES, base.ALLOWED_TYPES
            dla type_ w base.ALLOWED_TYPES:
                newname = 'With' + type_.capitalize() + name[1:]
                Mixin = local_globs[type_.capitalize() + 'Mixin']
                klasa Temp(base, Mixin, unittest.TestCase):
                    dalej
                Temp.__name__ = Temp.__qualname__ = newname
                Temp.__module__ = __module__
                remote_globs[newname] = Temp
        albo_inaczej issubclass(base, unittest.TestCase):
            klasa Temp(base, object):
                dalej
            Temp.__name__ = Temp.__qualname__ = name
            Temp.__module__ = __module__
            remote_globs[name] = Temp

    dangling = [Nic, Nic]
    old_start_method = [Nic]

    def setUpModule():
        multiprocessing.set_forkserver_preload(PRELOAD)
        multiprocessing.process._cleanup()
        dangling[0] = multiprocessing.process._dangling.copy()
        dangling[1] = threading._dangling.copy()
        old_start_method[0] = multiprocessing.get_start_method(allow_none=Prawda)
        spróbuj:
            multiprocessing.set_start_method(start_method, force=Prawda)
        wyjąwszy ValueError:
            podnieś unittest.SkipTest(start_method +
                                    ' start method nie supported')

        jeżeli sys.platform.startswith("linux"):
            spróbuj:
                lock = multiprocessing.RLock()
            wyjąwszy OSError:
                podnieś unittest.SkipTest("OSError podnieśs on RLock creation, "
                                        "see issue 3111!")
        check_enough_semaphores()
        util.get_temp_dir()     # creates temp directory
        multiprocessing.get_logger().setLevel(LOG_LEVEL)

    def tearDownModule():
        multiprocessing.set_start_method(old_start_method[0], force=Prawda)
        # pause a bit so we don't get warning about dangling threads/processes
        time.sleep(0.5)
        multiprocessing.process._cleanup()
        gc.collect()
        tmp = set(multiprocessing.process._dangling) - set(dangling[0])
        jeżeli tmp:
            print('Dangling processes:', tmp, file=sys.stderr)
        usuń tmp
        tmp = set(threading._dangling) - set(dangling[1])
        jeżeli tmp:
            print('Dangling threads:', tmp, file=sys.stderr)

    remote_globs['setUpModule'] = setUpModule
    remote_globs['tearDownModule'] = tearDownModule
