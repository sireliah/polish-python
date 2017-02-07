zaimportuj os
zaimportuj unittest
zaimportuj random
z test zaimportuj support
thread = support.import_module('_thread')
zaimportuj time
zaimportuj sys
zaimportuj weakref

z test zaimportuj lock_tests

NUMTASKS = 10
NUMTRIPS = 3

_print_mutex = thread.allocate_lock()

def verbose_print(arg):
    """Helper function dla printing out debugging output."""
    jeżeli support.verbose:
        przy _print_mutex:
            print(arg)

klasa BasicThreadTest(unittest.TestCase):

    def setUp(self):
        self.done_mutex = thread.allocate_lock()
        self.done_mutex.acquire()
        self.running_mutex = thread.allocate_lock()
        self.random_mutex = thread.allocate_lock()
        self.created = 0
        self.running = 0
        self.next_ident = 0


klasa ThreadRunningTests(BasicThreadTest):

    def newtask(self):
        przy self.running_mutex:
            self.next_ident += 1
            verbose_print("creating task %s" % self.next_ident)
            thread.start_new_thread(self.task, (self.next_ident,))
            self.created += 1
            self.running += 1

    def task(self, ident):
        przy self.random_mutex:
            delay = random.random() / 10000.0
        verbose_print("task %s will run dla %sus" % (ident, round(delay*1e6)))
        time.sleep(delay)
        verbose_print("task %s done" % ident)
        przy self.running_mutex:
            self.running -= 1
            jeżeli self.created == NUMTASKS oraz self.running == 0:
                self.done_mutex.release()

    def test_starting_threads(self):
        # Basic test dla thread creation.
        dla i w range(NUMTASKS):
            self.newtask()
        verbose_print("waiting dla tasks to complete...")
        self.done_mutex.acquire()
        verbose_print("all tasks done")

    def test_stack_size(self):
        # Various stack size tests.
        self.assertEqual(thread.stack_size(), 0, "initial stack size jest nie 0")

        thread.stack_size(0)
        self.assertEqual(thread.stack_size(), 0, "stack_size nie reset to default")

    @unittest.skipIf(os.name nie w ("nt", "posix"), 'test meant dla nt oraz posix')
    def test_nt_and_posix_stack_size(self):
        spróbuj:
            thread.stack_size(4096)
        wyjąwszy ValueError:
            verbose_print("caught expected ValueError setting "
                            "stack_size(4096)")
        wyjąwszy thread.error:
            self.skipTest("platform does nie support changing thread stack "
                          "size")

        fail_msg = "stack_size(%d) failed - should succeed"
        dla tss w (262144, 0x100000, 0):
            thread.stack_size(tss)
            self.assertEqual(thread.stack_size(), tss, fail_msg % tss)
            verbose_print("successfully set stack_size(%d)" % tss)

        dla tss w (262144, 0x100000):
            verbose_print("trying stack_size = (%d)" % tss)
            self.next_ident = 0
            self.created = 0
            dla i w range(NUMTASKS):
                self.newtask()

            verbose_print("waiting dla all tasks to complete")
            self.done_mutex.acquire()
            verbose_print("all tasks done")

        thread.stack_size(0)

    def test__count(self):
        # Test the _count() function.
        orig = thread._count()
        mut = thread.allocate_lock()
        mut.acquire()
        started = []
        def task():
            started.append(Nic)
            mut.acquire()
            mut.release()
        thread.start_new_thread(task, ())
        dopóki nie started:
            time.sleep(0.01)
        self.assertEqual(thread._count(), orig + 1)
        # Allow the task to finish.
        mut.release()
        # The only reliable way to be sure that the thread ended z the
        # interpreter's point of view jest to wait dla the function object to be
        # destroyed.
        done = []
        wr = weakref.ref(task, lambda _: done.append(Nic))
        usuń task
        dopóki nie done:
            time.sleep(0.01)
        self.assertEqual(thread._count(), orig)

    def test_save_exception_state_on_error(self):
        # See issue #14474
        def task():
            started.release()
            podnieś SyntaxError
        def mywrite(self, *args):
            spróbuj:
                podnieś ValueError
            wyjąwszy ValueError:
                dalej
            real_write(self, *args)
        c = thread._count()
        started = thread.allocate_lock()
        przy support.captured_output("stderr") jako stderr:
            real_write = stderr.write
            stderr.write = mywrite
            started.acquire()
            thread.start_new_thread(task, ())
            started.acquire()
            dopóki thread._count() > c:
                time.sleep(0.01)
        self.assertIn("Traceback", stderr.getvalue())


klasa Barrier:
    def __init__(self, num_threads):
        self.num_threads = num_threads
        self.waiting = 0
        self.checkin_mutex  = thread.allocate_lock()
        self.checkout_mutex = thread.allocate_lock()
        self.checkout_mutex.acquire()

    def enter(self):
        self.checkin_mutex.acquire()
        self.waiting = self.waiting + 1
        jeżeli self.waiting == self.num_threads:
            self.waiting = self.num_threads - 1
            self.checkout_mutex.release()
            zwróć
        self.checkin_mutex.release()

        self.checkout_mutex.acquire()
        self.waiting = self.waiting - 1
        jeżeli self.waiting == 0:
            self.checkin_mutex.release()
            zwróć
        self.checkout_mutex.release()


klasa BarrierTest(BasicThreadTest):

    def test_barrier(self):
        self.bar = Barrier(NUMTASKS)
        self.running = NUMTASKS
        dla i w range(NUMTASKS):
            thread.start_new_thread(self.task2, (i,))
        verbose_print("waiting dla tasks to end")
        self.done_mutex.acquire()
        verbose_print("tasks done")

    def task2(self, ident):
        dla i w range(NUMTRIPS):
            jeżeli ident == 0:
                # give it a good chance to enter the next
                # barrier before the others are all out
                # of the current one
                delay = 0
            inaczej:
                przy self.random_mutex:
                    delay = random.random() / 10000.0
            verbose_print("task %s will run dla %sus" %
                          (ident, round(delay * 1e6)))
            time.sleep(delay)
            verbose_print("task %s entering %s" % (ident, i))
            self.bar.enter()
            verbose_print("task %s leaving barrier" % ident)
        przy self.running_mutex:
            self.running -= 1
            # Must release mutex before releasing done, inaczej the main thread can
            # exit oraz set mutex to Nic jako part of global teardown; then
            # mutex.release() podnieśs AttributeError.
            finished = self.running == 0
        jeżeli finished:
            self.done_mutex.release()

klasa LockTests(lock_tests.LockTests):
    locktype = thread.allocate_lock


klasa TestForkInThread(unittest.TestCase):
    def setUp(self):
        self.read_fd, self.write_fd = os.pipe()

    @unittest.skipIf(sys.platform.startswith('win'),
                     "This test jest only appropriate dla POSIX-like systems.")
    @support.reap_threads
    def test_forkinthread(self):
        def thread1():
            spróbuj:
                pid = os.fork() # fork w a thread
            wyjąwszy RuntimeError:
                os._exit(1) # exit the child

            jeżeli pid == 0: # child
                spróbuj:
                    os.close(self.read_fd)
                    os.write(self.write_fd, b"OK")
                w_końcu:
                    os._exit(0)
            inaczej: # parent
                os.close(self.write_fd)

        thread.start_new_thread(thread1, ())
        self.assertEqual(os.read(self.read_fd, 2), b"OK",
                         "Unable to fork() w thread")

    def tearDown(self):
        spróbuj:
            os.close(self.read_fd)
        wyjąwszy OSError:
            dalej

        spróbuj:
            os.close(self.write_fd)
        wyjąwszy OSError:
            dalej


jeżeli __name__ == "__main__":
    unittest.main()
