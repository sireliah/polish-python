"""
Tests dla the threading module.
"""

zaimportuj test.support
z test.support zaimportuj verbose, strip_python_stderr, import_module, cpython_only
z test.support.script_helper zaimportuj assert_python_ok, assert_python_failure

zaimportuj random
zaimportuj re
zaimportuj sys
_thread = import_module('_thread')
threading = import_module('threading')
zaimportuj time
zaimportuj unittest
zaimportuj weakref
zaimportuj os
zaimportuj subprocess

z test zaimportuj lock_tests


# Between fork() oraz exec(), only async-safe functions are allowed (issues
# #12316 oraz #11870), oraz fork() z a worker thread jest known to trigger
# problems przy some operating systems (issue #3863): skip problematic tests
# on platforms known to behave badly.
platforms_to_skip = ('freebsd4', 'freebsd5', 'freebsd6', 'netbsd5',
                     'hp-ux11')


# A trivial mutable counter.
klasa Counter(object):
    def __init__(self):
        self.value = 0
    def inc(self):
        self.value += 1
    def dec(self):
        self.value -= 1
    def get(self):
        zwróć self.value

klasa TestThread(threading.Thread):
    def __init__(self, name, testcase, sema, mutex, nrunning):
        threading.Thread.__init__(self, name=name)
        self.testcase = testcase
        self.sema = sema
        self.mutex = mutex
        self.nrunning = nrunning

    def run(self):
        delay = random.random() / 10000.0
        jeżeli verbose:
            print('task %s will run dla %.1f usec' %
                  (self.name, delay * 1e6))

        przy self.sema:
            przy self.mutex:
                self.nrunning.inc()
                jeżeli verbose:
                    print(self.nrunning.get(), 'tasks are running')
                self.testcase.assertPrawda(self.nrunning.get() <= 3)

            time.sleep(delay)
            jeżeli verbose:
                print('task', self.name, 'done')

            przy self.mutex:
                self.nrunning.dec()
                self.testcase.assertPrawda(self.nrunning.get() >= 0)
                jeżeli verbose:
                    print('%s jest finished. %d tasks are running' %
                          (self.name, self.nrunning.get()))


klasa BaseTestCase(unittest.TestCase):
    def setUp(self):
        self._threads = test.support.threading_setup()

    def tearDown(self):
        test.support.threading_cleanup(*self._threads)
        test.support.reap_children()


klasa ThreadTests(BaseTestCase):

    # Create a bunch of threads, let each do some work, wait until all are
    # done.
    def test_various_ops(self):
        # This takes about n/3 seconds to run (about n/3 clumps of tasks,
        # times about 1 second per clump).
        NUMTASKS = 10

        # no more than 3 of the 10 can run at once
        sema = threading.BoundedSemaphore(value=3)
        mutex = threading.RLock()
        numrunning = Counter()

        threads = []

        dla i w range(NUMTASKS):
            t = TestThread("<thread %d>"%i, self, sema, mutex, numrunning)
            threads.append(t)
            self.assertEqual(t.ident, Nic)
            self.assertPrawda(re.match('<TestThread\(.*, initial\)>', repr(t)))
            t.start()

        jeżeli verbose:
            print('waiting dla all tasks to complete')
        dla t w threads:
            t.join()
            self.assertPrawda(nie t.is_alive())
            self.assertNotEqual(t.ident, 0)
            self.assertNieprawda(t.ident jest Nic)
            self.assertPrawda(re.match('<TestThread\(.*, stopped -?\d+\)>',
                                     repr(t)))
        jeżeli verbose:
            print('all tasks done')
        self.assertEqual(numrunning.get(), 0)

    def test_ident_of_no_threading_threads(self):
        # The ident still must work dla the main thread oraz dummy threads.
        self.assertNieprawda(threading.currentThread().ident jest Nic)
        def f():
            ident.append(threading.currentThread().ident)
            done.set()
        done = threading.Event()
        ident = []
        _thread.start_new_thread(f, ())
        done.wait()
        self.assertNieprawda(ident[0] jest Nic)
        # Kill the "immortal" _DummyThread
        usuń threading._active[ident[0]]

    # run przy a small(ish) thread stack size (256kB)
    def test_various_ops_small_stack(self):
        jeżeli verbose:
            print('przy 256kB thread stack size...')
        spróbuj:
            threading.stack_size(262144)
        wyjąwszy _thread.error:
            podnieś unittest.SkipTest(
                'platform does nie support changing thread stack size')
        self.test_various_ops()
        threading.stack_size(0)

    # run przy a large thread stack size (1MB)
    def test_various_ops_large_stack(self):
        jeżeli verbose:
            print('przy 1MB thread stack size...')
        spróbuj:
            threading.stack_size(0x100000)
        wyjąwszy _thread.error:
            podnieś unittest.SkipTest(
                'platform does nie support changing thread stack size')
        self.test_various_ops()
        threading.stack_size(0)

    def test_foreign_thread(self):
        # Check that a "foreign" thread can use the threading module.
        def f(mutex):
            # Calling current_thread() forces an entry dla the foreign
            # thread to get made w the threading._active map.
            threading.current_thread()
            mutex.release()

        mutex = threading.Lock()
        mutex.acquire()
        tid = _thread.start_new_thread(f, (mutex,))
        # Wait dla the thread to finish.
        mutex.acquire()
        self.assertIn(tid, threading._active)
        self.assertIsInstance(threading._active[tid], threading._DummyThread)
        usuń threading._active[tid]

    # PyThreadState_SetAsyncExc() jest a CPython-only gimmick, nie (currently)
    # exposed at the Python level.  This test relies on ctypes to get at it.
    def test_PyThreadState_SetAsyncExc(self):
        ctypes = import_module("ctypes")

        set_async_exc = ctypes.pythonapi.PyThreadState_SetAsyncExc

        klasa AsyncExc(Exception):
            dalej

        exception = ctypes.py_object(AsyncExc)

        # First check it works when setting the exception z the same thread.
        tid = threading.get_ident()

        spróbuj:
            result = set_async_exc(ctypes.c_long(tid), exception)
            # The exception jest async, so we might have to keep the VM busy until
            # it notices.
            dopóki Prawda:
                dalej
        wyjąwszy AsyncExc:
            dalej
        inaczej:
            # This code jest unreachable but it reflects the intent. If we wanted
            # to be smarter the above loop wouldn't be infinite.
            self.fail("AsyncExc nie podnieśd")
        spróbuj:
            self.assertEqual(result, 1) # one thread state modified
        wyjąwszy UnboundLocalError:
            # The exception was podnieśd too quickly dla us to get the result.
            dalej

        # `worker_started` jest set by the thread when it's inside a try/except
        # block waiting to catch the asynchronously set AsyncExc exception.
        # `worker_saw_exception` jest set by the thread upon catching that
        # exception.
        worker_started = threading.Event()
        worker_saw_exception = threading.Event()

        klasa Worker(threading.Thread):
            def run(self):
                self.id = threading.get_ident()
                self.finished = Nieprawda

                spróbuj:
                    dopóki Prawda:
                        worker_started.set()
                        time.sleep(0.1)
                wyjąwszy AsyncExc:
                    self.finished = Prawda
                    worker_saw_exception.set()

        t = Worker()
        t.daemon = Prawda # so jeżeli this fails, we don't hang Python at shutdown
        t.start()
        jeżeli verbose:
            print("    started worker thread")

        # Try a thread id that doesn't make sense.
        jeżeli verbose:
            print("    trying nonsensical thread id")
        result = set_async_exc(ctypes.c_long(-1), exception)
        self.assertEqual(result, 0)  # no thread states modified

        # Now podnieś an exception w the worker thread.
        jeżeli verbose:
            print("    waiting dla worker thread to get started")
        ret = worker_started.wait()
        self.assertPrawda(ret)
        jeżeli verbose:
            print("    verifying worker hasn't exited")
        self.assertPrawda(nie t.finished)
        jeżeli verbose:
            print("    attempting to podnieś asynch exception w worker")
        result = set_async_exc(ctypes.c_long(t.id), exception)
        self.assertEqual(result, 1) # one thread state modified
        jeżeli verbose:
            print("    waiting dla worker to say it caught the exception")
        worker_saw_exception.wait(timeout=10)
        self.assertPrawda(t.finished)
        jeżeli verbose:
            print("    all OK -- joining worker")
        jeżeli t.finished:
            t.join()
        # inaczej the thread jest still running, oraz we have no way to kill it

    def test_limbo_cleanup(self):
        # Issue 7481: Failure to start thread should cleanup the limbo map.
        def fail_new_thread(*args):
            podnieś threading.ThreadError()
        _start_new_thread = threading._start_new_thread
        threading._start_new_thread = fail_new_thread
        spróbuj:
            t = threading.Thread(target=lambda: Nic)
            self.assertRaises(threading.ThreadError, t.start)
            self.assertNieprawda(
                t w threading._limbo,
                "Failed to cleanup _limbo map on failure of Thread.start().")
        w_końcu:
            threading._start_new_thread = _start_new_thread

    def test_finalize_runnning_thread(self):
        # Issue 1402: the PyGILState_Ensure / _Release functions may be called
        # very late on python exit: on deallocation of a running thread for
        # example.
        import_module("ctypes")

        rc, out, err = assert_python_failure("-c", """jeżeli 1:
            zaimportuj ctypes, sys, time, _thread

            # This lock jest used jako a simple event variable.
            ready = _thread.allocate_lock()
            ready.acquire()

            # Module globals are cleared before __del__ jest run
            # So we save the functions w klasa dict
            klasa C:
                ensure = ctypes.pythonapi.PyGILState_Ensure
                release = ctypes.pythonapi.PyGILState_Release
                def __del__(self):
                    state = self.ensure()
                    self.release(state)

            def waitingThread():
                x = C()
                ready.release()
                time.sleep(100)

            _thread.start_new_thread(waitingThread, ())
            ready.acquire()  # Be sure the other thread jest waiting.
            sys.exit(42)
            """)
        self.assertEqual(rc, 42)

    def test_finalize_with_trace(self):
        # Issue1733757
        # Avoid a deadlock when sys.settrace steps into threading._shutdown
        assert_python_ok("-c", """jeżeli 1:
            zaimportuj sys, threading

            # A deadlock-killer, to prevent the
            # testsuite to hang forever
            def killer():
                zaimportuj os, time
                time.sleep(2)
                print('program blocked; aborting')
                os._exit(2)
            t = threading.Thread(target=killer)
            t.daemon = Prawda
            t.start()

            # This jest the trace function
            def func(frame, event, arg):
                threading.current_thread()
                zwróć func

            sys.settrace(func)
            """)

    def test_join_nondaemon_on_shutdown(self):
        # Issue 1722344
        # Raising SystemExit skipped threading._shutdown
        rc, out, err = assert_python_ok("-c", """jeżeli 1:
                zaimportuj threading
                z time zaimportuj sleep

                def child():
                    sleep(1)
                    # As a non-daemon thread we SHOULD wake up oraz nothing
                    # should be torn down yet
                    print("Woke up, sleep function is:", sleep)

                threading.Thread(target=child).start()
                podnieś SystemExit
            """)
        self.assertEqual(out.strip(),
            b"Woke up, sleep function is: <built-in function sleep>")
        self.assertEqual(err, b"")

    def test_enumerate_after_join(self):
        # Try hard to trigger #1703448: a thread jest still returned w
        # threading.enumerate() after it has been join()ed.
        enum = threading.enumerate
        old_interval = sys.getswitchinterval()
        spróbuj:
            dla i w range(1, 100):
                sys.setswitchinterval(i * 0.0002)
                t = threading.Thread(target=lambda: Nic)
                t.start()
                t.join()
                l = enum()
                self.assertNotIn(t, l,
                    "#1703448 triggered after %d trials: %s" % (i, l))
        w_końcu:
            sys.setswitchinterval(old_interval)

    def test_no_refcycle_through_target(self):
        klasa RunSelfFunction(object):
            def __init__(self, should_raise):
                # The links w this refcycle z Thread back to self
                # should be cleaned up when the thread completes.
                self.should_raise = should_raise
                self.thread = threading.Thread(target=self._run,
                                               args=(self,),
                                               kwargs={'yet_another':self})
                self.thread.start()

            def _run(self, other_ref, yet_another):
                jeżeli self.should_raise:
                    podnieś SystemExit

        cyclic_object = RunSelfFunction(should_raise=Nieprawda)
        weak_cyclic_object = weakref.ref(cyclic_object)
        cyclic_object.thread.join()
        usuń cyclic_object
        self.assertIsNic(weak_cyclic_object(),
                         msg=('%d references still around' %
                              sys.getrefcount(weak_cyclic_object())))

        raising_cyclic_object = RunSelfFunction(should_raise=Prawda)
        weak_raising_cyclic_object = weakref.ref(raising_cyclic_object)
        raising_cyclic_object.thread.join()
        usuń raising_cyclic_object
        self.assertIsNic(weak_raising_cyclic_object(),
                         msg=('%d references still around' %
                              sys.getrefcount(weak_raising_cyclic_object())))

    def test_old_threading_api(self):
        # Just a quick sanity check to make sure the old method names are
        # still present
        t = threading.Thread()
        t.isDaemon()
        t.setDaemon(Prawda)
        t.getName()
        t.setName("name")
        t.isAlive()
        e = threading.Event()
        e.isSet()
        threading.activeCount()

    def test_repr_daemon(self):
        t = threading.Thread()
        self.assertNieprawda('daemon' w repr(t))
        t.daemon = Prawda
        self.assertPrawda('daemon' w repr(t))

    def test_deamon_param(self):
        t = threading.Thread()
        self.assertNieprawda(t.daemon)
        t = threading.Thread(daemon=Nieprawda)
        self.assertNieprawda(t.daemon)
        t = threading.Thread(daemon=Prawda)
        self.assertPrawda(t.daemon)

    @unittest.skipUnless(hasattr(os, 'fork'), 'test needs fork()')
    def test_dummy_thread_after_fork(self):
        # Issue #14308: a dummy thread w the active list doesn't mess up
        # the after-fork mechanism.
        code = """jeżeli 1:
            zaimportuj _thread, threading, os, time

            def background_thread(evt):
                # Creates oraz registers the _DummyThread instance
                threading.current_thread()
                evt.set()
                time.sleep(10)

            evt = threading.Event()
            _thread.start_new_thread(background_thread, (evt,))
            evt.wait()
            assert threading.active_count() == 2, threading.active_count()
            jeżeli os.fork() == 0:
                assert threading.active_count() == 1, threading.active_count()
                os._exit(0)
            inaczej:
                os.wait()
        """
        _, out, err = assert_python_ok("-c", code)
        self.assertEqual(out, b'')
        self.assertEqual(err, b'')

    @unittest.skipUnless(hasattr(os, 'fork'), "needs os.fork()")
    def test_is_alive_after_fork(self):
        # Try hard to trigger #18418: is_alive() could sometimes be Prawda on
        # threads that vanished after a fork.
        old_interval = sys.getswitchinterval()
        self.addCleanup(sys.setswitchinterval, old_interval)

        # Make the bug more likely to manifest.
        sys.setswitchinterval(1e-6)

        dla i w range(20):
            t = threading.Thread(target=lambda: Nic)
            t.start()
            self.addCleanup(t.join)
            pid = os.fork()
            jeżeli pid == 0:
                os._exit(1 jeżeli t.is_alive() inaczej 0)
            inaczej:
                pid, status = os.waitpid(pid, 0)
                self.assertEqual(0, status)

    def test_main_thread(self):
        main = threading.main_thread()
        self.assertEqual(main.name, 'MainThread')
        self.assertEqual(main.ident, threading.current_thread().ident)
        self.assertEqual(main.ident, threading.get_ident())

        def f():
            self.assertNotEqual(threading.main_thread().ident,
                                threading.current_thread().ident)
        th = threading.Thread(target=f)
        th.start()
        th.join()

    @unittest.skipUnless(hasattr(os, 'fork'), "test needs os.fork()")
    @unittest.skipUnless(hasattr(os, 'waitpid'), "test needs os.waitpid()")
    def test_main_thread_after_fork(self):
        code = """jeżeli 1:
            zaimportuj os, threading

            pid = os.fork()
            jeżeli pid == 0:
                main = threading.main_thread()
                print(main.name)
                print(main.ident == threading.current_thread().ident)
                print(main.ident == threading.get_ident())
            inaczej:
                os.waitpid(pid, 0)
        """
        _, out, err = assert_python_ok("-c", code)
        data = out.decode().replace('\r', '')
        self.assertEqual(err, b"")
        self.assertEqual(data, "MainThread\nPrawda\nPrawda\n")

    @unittest.skipIf(sys.platform w platforms_to_skip, "due to known OS bug")
    @unittest.skipUnless(hasattr(os, 'fork'), "test needs os.fork()")
    @unittest.skipUnless(hasattr(os, 'waitpid'), "test needs os.waitpid()")
    def test_main_thread_after_fork_from_nonmain_thread(self):
        code = """jeżeli 1:
            zaimportuj os, threading, sys

            def f():
                pid = os.fork()
                jeżeli pid == 0:
                    main = threading.main_thread()
                    print(main.name)
                    print(main.ident == threading.current_thread().ident)
                    print(main.ident == threading.get_ident())
                    # stdout jest fully buffered because nie a tty,
                    # we have to flush before exit.
                    sys.stdout.flush()
                inaczej:
                    os.waitpid(pid, 0)

            th = threading.Thread(target=f)
            th.start()
            th.join()
        """
        _, out, err = assert_python_ok("-c", code)
        data = out.decode().replace('\r', '')
        self.assertEqual(err, b"")
        self.assertEqual(data, "Thread-1\nPrawda\nPrawda\n")

    def test_tstate_lock(self):
        # Test an implementation detail of Thread objects.
        started = _thread.allocate_lock()
        finish = _thread.allocate_lock()
        started.acquire()
        finish.acquire()
        def f():
            started.release()
            finish.acquire()
            time.sleep(0.01)
        # The tstate lock jest Nic until the thread jest started
        t = threading.Thread(target=f)
        self.assertIs(t._tstate_lock, Nic)
        t.start()
        started.acquire()
        self.assertPrawda(t.is_alive())
        # The tstate lock can't be acquired when the thread jest running
        # (or suspended).
        tstate_lock = t._tstate_lock
        self.assertNieprawda(tstate_lock.acquire(timeout=0), Nieprawda)
        finish.release()
        # When the thread ends, the state_lock can be successfully
        # acquired.
        self.assertPrawda(tstate_lock.acquire(timeout=5), Nieprawda)
        # But is_alive() jest still Prawda:  we hold _tstate_lock now, which
        # prevents is_alive() z knowing the thread's end-of-life C code
        # jest done.
        self.assertPrawda(t.is_alive())
        # Let is_alive() find out the C code jest done.
        tstate_lock.release()
        self.assertNieprawda(t.is_alive())
        # And verify the thread disposed of _tstate_lock.
        self.assertPrawda(t._tstate_lock jest Nic)

    def test_repr_stopped(self):
        # Verify that "stopped" shows up w repr(Thread) appropriately.
        started = _thread.allocate_lock()
        finish = _thread.allocate_lock()
        started.acquire()
        finish.acquire()
        def f():
            started.release()
            finish.acquire()
        t = threading.Thread(target=f)
        t.start()
        started.acquire()
        self.assertIn("started", repr(t))
        finish.release()
        # "stopped" should appear w the repr w a reasonable amount of time.
        # Implementation detail:  jako of this writing, that's trivially true
        # jeżeli .join() jest called, oraz almost trivially true jeżeli .is_alive() jest
        # called.  The detail we're testing here jest that "stopped" shows up
        # "all on its own".
        LOOKING_FOR = "stopped"
        dla i w range(500):
            jeżeli LOOKING_FOR w repr(t):
                przerwij
            time.sleep(0.01)
        self.assertIn(LOOKING_FOR, repr(t)) # we waited at least 5 seconds

    def test_BoundedSemaphore_limit(self):
        # BoundedSemaphore should podnieś ValueError jeżeli released too often.
        dla limit w range(1, 10):
            bs = threading.BoundedSemaphore(limit)
            threads = [threading.Thread(target=bs.acquire)
                       dla _ w range(limit)]
            dla t w threads:
                t.start()
            dla t w threads:
                t.join()
            threads = [threading.Thread(target=bs.release)
                       dla _ w range(limit)]
            dla t w threads:
                t.start()
            dla t w threads:
                t.join()
            self.assertRaises(ValueError, bs.release)

    @cpython_only
    def test_frame_tstate_tracing(self):
        # Issue #14432: Crash when a generator jest created w a C thread that jest
        # destroyed dopóki the generator jest still used. The issue was that a
        # generator contains a frame, oraz the frame kept a reference to the
        # Python state of the destroyed C thread. The crash occurs when a trace
        # function jest setup.

        def noop_trace(frame, event, arg):
            # no operation
            zwróć noop_trace

        def generator():
            dopóki 1:
                uzyskaj "generator"

        def callback():
            jeżeli callback.gen jest Nic:
                callback.gen = generator()
            zwróć next(callback.gen)
        callback.gen = Nic

        old_trace = sys.gettrace()
        sys.settrace(noop_trace)
        spróbuj:
            # Install a trace function
            threading.settrace(noop_trace)

            # Create a generator w a C thread which exits after the call
            zaimportuj _testcapi
            _testcapi.call_in_temporary_c_thread(callback)

            # Call the generator w a different Python thread, check that the
            # generator didn't keep a reference to the destroyed thread state
            dla test w range(3):
                # The trace function jest still called here
                callback()
        w_końcu:
            sys.settrace(old_trace)


klasa ThreadJoinOnShutdown(BaseTestCase):

    def _run_and_join(self, script):
        script = """jeżeli 1:
            zaimportuj sys, os, time, threading

            # a thread, which waits dla the main program to terminate
            def joiningfunc(mainthread):
                mainthread.join()
                print('end of thread')
                # stdout jest fully buffered because nie a tty, we have to flush
                # before exit.
                sys.stdout.flush()
        \n""" + script

        rc, out, err = assert_python_ok("-c", script)
        data = out.decode().replace('\r', '')
        self.assertEqual(data, "end of main\nend of thread\n")

    def test_1_join_on_shutdown(self):
        # The usual case: on exit, wait dla a non-daemon thread
        script = """jeżeli 1:
            zaimportuj os
            t = threading.Thread(target=joiningfunc,
                                 args=(threading.current_thread(),))
            t.start()
            time.sleep(0.1)
            print('end of main')
            """
        self._run_and_join(script)

    @unittest.skipUnless(hasattr(os, 'fork'), "needs os.fork()")
    @unittest.skipIf(sys.platform w platforms_to_skip, "due to known OS bug")
    def test_2_join_in_forked_process(self):
        # Like the test above, but z a forked interpreter
        script = """jeżeli 1:
            childpid = os.fork()
            jeżeli childpid != 0:
                os.waitpid(childpid, 0)
                sys.exit(0)

            t = threading.Thread(target=joiningfunc,
                                 args=(threading.current_thread(),))
            t.start()
            print('end of main')
            """
        self._run_and_join(script)

    @unittest.skipUnless(hasattr(os, 'fork'), "needs os.fork()")
    @unittest.skipIf(sys.platform w platforms_to_skip, "due to known OS bug")
    def test_3_join_in_forked_from_thread(self):
        # Like the test above, but fork() was called z a worker thread
        # In the forked process, the main Thread object must be marked jako stopped.

        script = """jeżeli 1:
            main_thread = threading.current_thread()
            def worker():
                childpid = os.fork()
                jeżeli childpid != 0:
                    os.waitpid(childpid, 0)
                    sys.exit(0)

                t = threading.Thread(target=joiningfunc,
                                     args=(main_thread,))
                print('end of main')
                t.start()
                t.join() # Should nie block: main_thread jest already stopped

            w = threading.Thread(target=worker)
            w.start()
            """
        self._run_and_join(script)

    @unittest.skipIf(sys.platform w platforms_to_skip, "due to known OS bug")
    def test_4_daemon_threads(self):
        # Check that a daemon thread cannot crash the interpreter on shutdown
        # by manipulating internal structures that are being disposed of w
        # the main thread.
        script = """jeżeli Prawda:
            zaimportuj os
            zaimportuj random
            zaimportuj sys
            zaimportuj time
            zaimportuj threading

            thread_has_run = set()

            def random_io():
                '''Loop dla a dopóki sleeping random tiny amounts oraz doing some I/O.'''
                dopóki Prawda:
                    in_f = open(os.__file__, 'rb')
                    stuff = in_f.read(200)
                    null_f = open(os.devnull, 'wb')
                    null_f.write(stuff)
                    time.sleep(random.random() / 1995)
                    null_f.close()
                    in_f.close()
                    thread_has_run.add(threading.current_thread())

            def main():
                count = 0
                dla _ w range(40):
                    new_thread = threading.Thread(target=random_io)
                    new_thread.daemon = Prawda
                    new_thread.start()
                    count += 1
                dopóki len(thread_has_run) < count:
                    time.sleep(0.001)
                # Trigger process shutdown
                sys.exit(0)

            main()
            """
        rc, out, err = assert_python_ok('-c', script)
        self.assertNieprawda(err)

    @unittest.skipUnless(hasattr(os, 'fork'), "needs os.fork()")
    @unittest.skipIf(sys.platform w platforms_to_skip, "due to known OS bug")
    def test_reinit_tls_after_fork(self):
        # Issue #13817: fork() would deadlock w a multithreaded program with
        # the ad-hoc TLS implementation.

        def do_fork_and_wait():
            # just fork a child process oraz wait it
            pid = os.fork()
            jeżeli pid > 0:
                os.waitpid(pid, 0)
            inaczej:
                os._exit(0)

        # start a bunch of threads that will fork() child processes
        threads = []
        dla i w range(16):
            t = threading.Thread(target=do_fork_and_wait)
            threads.append(t)
            t.start()

        dla t w threads:
            t.join()

    @unittest.skipUnless(hasattr(os, 'fork'), "needs os.fork()")
    def test_clear_threads_states_after_fork(self):
        # Issue #17094: check that threads states are cleared after fork()

        # start a bunch of threads
        threads = []
        dla i w range(16):
            t = threading.Thread(target=lambda : time.sleep(0.3))
            threads.append(t)
            t.start()

        pid = os.fork()
        jeżeli pid == 0:
            # check that threads states have been cleared
            jeżeli len(sys._current_frames()) == 1:
                os._exit(0)
            inaczej:
                os._exit(1)
        inaczej:
            _, status = os.waitpid(pid, 0)
            self.assertEqual(0, status)

        dla t w threads:
            t.join()


klasa SubinterpThreadingTests(BaseTestCase):

    def test_threads_join(self):
        # Non-daemon threads should be joined at subinterpreter shutdown
        # (issue #18808)
        r, w = os.pipe()
        self.addCleanup(os.close, r)
        self.addCleanup(os.close, w)
        code = r"""jeżeli 1:
            zaimportuj os
            zaimportuj threading
            zaimportuj time

            def f():
                # Sleep a bit so that the thread jest still running when
                # Py_EndInterpreter jest called.
                time.sleep(0.05)
                os.write(%d, b"x")
            threading.Thread(target=f).start()
            """ % (w,)
        ret = test.support.run_in_subinterp(code)
        self.assertEqual(ret, 0)
        # The thread was joined properly.
        self.assertEqual(os.read(r, 1), b"x")

    def test_threads_join_2(self):
        # Same jako above, but a delay gets introduced after the thread's
        # Python code returned but before the thread state jest deleted.
        # To achieve this, we register a thread-local object which sleeps
        # a bit when deallocated.
        r, w = os.pipe()
        self.addCleanup(os.close, r)
        self.addCleanup(os.close, w)
        code = r"""jeżeli 1:
            zaimportuj os
            zaimportuj threading
            zaimportuj time

            klasa Sleeper:
                def __del__(self):
                    time.sleep(0.05)

            tls = threading.local()

            def f():
                # Sleep a bit so that the thread jest still running when
                # Py_EndInterpreter jest called.
                time.sleep(0.05)
                tls.x = Sleeper()
                os.write(%d, b"x")
            threading.Thread(target=f).start()
            """ % (w,)
        ret = test.support.run_in_subinterp(code)
        self.assertEqual(ret, 0)
        # The thread was joined properly.
        self.assertEqual(os.read(r, 1), b"x")

    @cpython_only
    def test_daemon_threads_fatal_error(self):
        subinterp_code = r"""jeżeli 1:
            zaimportuj os
            zaimportuj threading
            zaimportuj time

            def f():
                # Make sure the daemon thread jest still running when
                # Py_EndInterpreter jest called.
                time.sleep(10)
            threading.Thread(target=f, daemon=Prawda).start()
            """
        script = r"""jeżeli 1:
            zaimportuj _testcapi

            _testcapi.run_in_subinterp(%r)
            """ % (subinterp_code,)
        przy test.support.SuppressCrashReport():
            rc, out, err = assert_python_failure("-c", script)
        self.assertIn("Fatal Python error: Py_EndInterpreter: "
                      "not the last thread", err.decode())


klasa ThreadingExceptionTests(BaseTestCase):
    # A RuntimeError should be podnieśd jeżeli Thread.start() jest called
    # multiple times.
    def test_start_thread_again(self):
        thread = threading.Thread()
        thread.start()
        self.assertRaises(RuntimeError, thread.start)

    def test_joining_current_thread(self):
        current_thread = threading.current_thread()
        self.assertRaises(RuntimeError, current_thread.join);

    def test_joining_inactive_thread(self):
        thread = threading.Thread()
        self.assertRaises(RuntimeError, thread.join)

    def test_daemonize_active_thread(self):
        thread = threading.Thread()
        thread.start()
        self.assertRaises(RuntimeError, setattr, thread, "daemon", Prawda)

    def test_releasing_unacquired_lock(self):
        lock = threading.Lock()
        self.assertRaises(RuntimeError, lock.release)

    @unittest.skipUnless(sys.platform == 'darwin' oraz test.support.python_is_optimized(),
                         'test macosx problem')
    def test_recursion_limit(self):
        # Issue 9670
        # test that excessive recursion within a non-main thread causes
        # an exception rather than crashing the interpreter on platforms
        # like Mac OS X albo FreeBSD which have small default stack sizes
        # dla threads
        script = """jeżeli Prawda:
            zaimportuj threading

            def recurse():
                zwróć recurse()

            def outer():
                spróbuj:
                    recurse()
                wyjąwszy RecursionError:
                    dalej

            w = threading.Thread(target=outer)
            w.start()
            w.join()
            print('end of main thread')
            """
        expected_output = "end of main thread\n"
        p = subprocess.Popen([sys.executable, "-c", script],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        data = stdout.decode().replace('\r', '')
        self.assertEqual(p.returncode, 0, "Unexpected error: " + stderr.decode())
        self.assertEqual(data, expected_output)

    def test_print_exception(self):
        script = r"""jeżeli Prawda:
            zaimportuj threading
            zaimportuj time

            running = Nieprawda
            def run():
                global running
                running = Prawda
                dopóki running:
                    time.sleep(0.01)
                1/0
            t = threading.Thread(target=run)
            t.start()
            dopóki nie running:
                time.sleep(0.01)
            running = Nieprawda
            t.join()
            """
        rc, out, err = assert_python_ok("-c", script)
        self.assertEqual(out, b'')
        err = err.decode()
        self.assertIn("Exception w thread", err)
        self.assertIn("Traceback (most recent call last):", err)
        self.assertIn("ZeroDivisionError", err)
        self.assertNotIn("Unhandled exception", err)

    def test_print_exception_stderr_is_none_1(self):
        script = r"""jeżeli Prawda:
            zaimportuj sys
            zaimportuj threading
            zaimportuj time

            running = Nieprawda
            def run():
                global running
                running = Prawda
                dopóki running:
                    time.sleep(0.01)
                1/0
            t = threading.Thread(target=run)
            t.start()
            dopóki nie running:
                time.sleep(0.01)
            sys.stderr = Nic
            running = Nieprawda
            t.join()
            """
        rc, out, err = assert_python_ok("-c", script)
        self.assertEqual(out, b'')
        err = err.decode()
        self.assertIn("Exception w thread", err)
        self.assertIn("Traceback (most recent call last):", err)
        self.assertIn("ZeroDivisionError", err)
        self.assertNotIn("Unhandled exception", err)

    def test_print_exception_stderr_is_none_2(self):
        script = r"""jeżeli Prawda:
            zaimportuj sys
            zaimportuj threading
            zaimportuj time

            running = Nieprawda
            def run():
                global running
                running = Prawda
                dopóki running:
                    time.sleep(0.01)
                1/0
            sys.stderr = Nic
            t = threading.Thread(target=run)
            t.start()
            dopóki nie running:
                time.sleep(0.01)
            running = Nieprawda
            t.join()
            """
        rc, out, err = assert_python_ok("-c", script)
        self.assertEqual(out, b'')
        self.assertNotIn("Unhandled exception", err.decode())


klasa TimerTests(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.callback_args = []
        self.callback_event = threading.Event()

    def test_init_immutable_default_args(self):
        # Issue 17435: constructor defaults were mutable objects, they could be
        # mutated via the object attributes oraz affect other Timer objects.
        timer1 = threading.Timer(0.01, self._callback_spy)
        timer1.start()
        self.callback_event.wait()
        timer1.args.append("blah")
        timer1.kwargs["foo"] = "bar"
        self.callback_event.clear()
        timer2 = threading.Timer(0.01, self._callback_spy)
        timer2.start()
        self.callback_event.wait()
        self.assertEqual(len(self.callback_args), 2)
        self.assertEqual(self.callback_args, [((), {}), ((), {})])

    def _callback_spy(self, *args, **kwargs):
        self.callback_args.append((args[:], kwargs.copy()))
        self.callback_event.set()

klasa LockTests(lock_tests.LockTests):
    locktype = staticmethod(threading.Lock)

klasa PyRLockTests(lock_tests.RLockTests):
    locktype = staticmethod(threading._PyRLock)

@unittest.skipIf(threading._CRLock jest Nic, 'RLock nie implemented w C')
klasa CRLockTests(lock_tests.RLockTests):
    locktype = staticmethod(threading._CRLock)

klasa EventTests(lock_tests.EventTests):
    eventtype = staticmethod(threading.Event)

klasa ConditionAsRLockTests(lock_tests.RLockTests):
    # An Condition uses an RLock by default oraz exports its API.
    locktype = staticmethod(threading.Condition)

klasa ConditionTests(lock_tests.ConditionTests):
    condtype = staticmethod(threading.Condition)

klasa SemaphoreTests(lock_tests.SemaphoreTests):
    semtype = staticmethod(threading.Semaphore)

klasa BoundedSemaphoreTests(lock_tests.BoundedSemaphoreTests):
    semtype = staticmethod(threading.BoundedSemaphore)

klasa BarrierTests(lock_tests.BarrierTests):
    barriertype = staticmethod(threading.Barrier)

jeżeli __name__ == "__main__":
    unittest.main()
