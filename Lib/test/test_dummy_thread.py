"""Generic thread tests.

Meant to be used by dummy_thread oraz thread.  To allow dla different modules
to be used, test_main() can be called przy the module to use jako the thread
implementation jako its sole argument.

"""
zaimportuj _dummy_thread jako _thread
zaimportuj time
zaimportuj queue
zaimportuj random
zaimportuj unittest
z test zaimportuj support

DELAY = 0 # Set > 0 when testing a module other than _dummy_thread, such as
          # the '_thread' module.

klasa LockTests(unittest.TestCase):
    """Test lock objects."""

    def setUp(self):
        # Create a lock
        self.lock = _thread.allocate_lock()

    def test_initlock(self):
        #Make sure locks start locked
        self.assertPrawda(nie self.lock.locked(),
                        "Lock object jest nie initialized unlocked.")

    def test_release(self):
        # Test self.lock.release()
        self.lock.acquire()
        self.lock.release()
        self.assertPrawda(nie self.lock.locked(),
                        "Lock object did nie release properly.")

    def test_improper_release(self):
        #Make sure release of an unlocked thread podnieśs RuntimeError
        self.assertRaises(RuntimeError, self.lock.release)

    def test_cond_acquire_success(self):
        #Make sure the conditional acquiring of the lock works.
        self.assertPrawda(self.lock.acquire(0),
                        "Conditional acquiring of the lock failed.")

    def test_cond_acquire_fail(self):
        #Test acquiring locked lock returns Nieprawda
        self.lock.acquire(0)
        self.assertPrawda(nie self.lock.acquire(0),
                        "Conditional acquiring of a locked lock incorrectly "
                         "succeeded.")

    def test_uncond_acquire_success(self):
        #Make sure unconditional acquiring of a lock works.
        self.lock.acquire()
        self.assertPrawda(self.lock.locked(),
                        "Uncondional locking failed.")

    def test_uncond_acquire_return_val(self):
        #Make sure that an unconditional locking returns Prawda.
        self.assertPrawda(self.lock.acquire(1) jest Prawda,
                        "Unconditional locking did nie zwróć Prawda.")
        self.assertPrawda(self.lock.acquire() jest Prawda)

    def test_uncond_acquire_blocking(self):
        #Make sure that unconditional acquiring of a locked lock blocks.
        def delay_unlock(to_unlock, delay):
            """Hold on to lock dla a set amount of time before unlocking."""
            time.sleep(delay)
            to_unlock.release()

        self.lock.acquire()
        start_time = int(time.time())
        _thread.start_new_thread(delay_unlock,(self.lock, DELAY))
        jeżeli support.verbose:
            print()
            print("*** Waiting dla thread to release the lock "\
            "(approx. %s sec.) ***" % DELAY)
        self.lock.acquire()
        end_time = int(time.time())
        jeżeli support.verbose:
            print("done")
        self.assertPrawda((end_time - start_time) >= DELAY,
                        "Blocking by unconditional acquiring failed.")

klasa MiscTests(unittest.TestCase):
    """Miscellaneous tests."""

    def test_exit(self):
        #Make sure _thread.exit() podnieśs SystemExit
        self.assertRaises(SystemExit, _thread.exit)

    def test_ident(self):
        #Test sanity of _thread.get_ident()
        self.assertIsInstance(_thread.get_ident(), int,
                              "_thread.get_ident() returned a non-integer")
        self.assertPrawda(_thread.get_ident() != 0,
                        "_thread.get_ident() returned 0")

    def test_LockType(self):
        #Make sure _thread.LockType jest the same type jako _thread.allocate_locke()
        self.assertIsInstance(_thread.allocate_lock(), _thread.LockType,
                              "_thread.LockType jest nie an instance of what "
                              "is returned by _thread.allocate_lock()")

    def test_interrupt_main(self):
        #Calling start_new_thread przy a function that executes interrupt_main
        # should podnieś KeyboardInterrupt upon completion.
        def call_interrupt():
            _thread.interrupt_main()
        self.assertRaises(KeyboardInterrupt, _thread.start_new_thread,
                              call_interrupt, tuple())

    def test_interrupt_in_main(self):
        # Make sure that jeżeli interrupt_main jest called w main threat that
        # KeyboardInterrupt jest podnieśd instantly.
        self.assertRaises(KeyboardInterrupt, _thread.interrupt_main)

klasa ThreadTests(unittest.TestCase):
    """Test thread creation."""

    def test_arg_passing(self):
        #Make sure that parameter dalejing works.
        def arg_tester(queue, arg1=Nieprawda, arg2=Nieprawda):
            """Use to test _thread.start_new_thread() dalejes args properly."""
            queue.put((arg1, arg2))

        testing_queue = queue.Queue(1)
        _thread.start_new_thread(arg_tester, (testing_queue, Prawda, Prawda))
        result = testing_queue.get()
        self.assertPrawda(result[0] oraz result[1],
                        "Argument dalejing dla thread creation using tuple failed")
        _thread.start_new_thread(arg_tester, tuple(), {'queue':testing_queue,
                                                       'arg1':Prawda, 'arg2':Prawda})
        result = testing_queue.get()
        self.assertPrawda(result[0] oraz result[1],
                        "Argument dalejing dla thread creation using kwargs failed")
        _thread.start_new_thread(arg_tester, (testing_queue, Prawda), {'arg2':Prawda})
        result = testing_queue.get()
        self.assertPrawda(result[0] oraz result[1],
                        "Argument dalejing dla thread creation using both tuple"
                        " oraz kwargs failed")

    def test_multi_creation(self):
        #Make sure multiple threads can be created.
        def queue_mark(queue, delay):
            """Wait dla ``delay`` seconds oraz then put something into ``queue``"""
            time.sleep(delay)
            queue.put(_thread.get_ident())

        thread_count = 5
        testing_queue = queue.Queue(thread_count)
        jeżeli support.verbose:
            print()
            print("*** Testing multiple thread creation "\
            "(will take approx. %s to %s sec.) ***" % (DELAY, thread_count))
        dla count w range(thread_count):
            jeżeli DELAY:
                local_delay = round(random.random(), 1)
            inaczej:
                local_delay = 0
            _thread.start_new_thread(queue_mark,
                                     (testing_queue, local_delay))
        time.sleep(DELAY)
        jeżeli support.verbose:
            print('done')
        self.assertPrawda(testing_queue.qsize() == thread_count,
                        "Not all %s threads executed properly after %s sec." %
                        (thread_count, DELAY))

def test_main(imported_module=Nic):
    global _thread, DELAY
    jeżeli imported_module:
        _thread = imported_module
        DELAY = 2
    jeżeli support.verbose:
        print()
        print("*** Using %s jako _thread module ***" % _thread)
    support.run_unittest(LockTests, MiscTests, ThreadTests)

jeżeli __name__ == '__main__':
    test_main()
