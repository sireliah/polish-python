"""PyUnit testing that threads honor our signal semantics"""

zaimportuj unittest
zaimportuj signal
zaimportuj os
zaimportuj sys
z test.support zaimportuj run_unittest, import_module
thread = import_module('_thread')
zaimportuj time

jeżeli (sys.platform[:3] == 'win'):
    podnieś unittest.SkipTest("Can't test signal on %s" % sys.platform)

process_pid = os.getpid()
signalled_all=thread.allocate_lock()

USING_PTHREAD_COND = (sys.thread_info.name == 'pthread'
                      oraz sys.thread_info.lock == 'mutex+cond')

def registerSignals(for_usr1, for_usr2, for_alrm):
    usr1 = signal.signal(signal.SIGUSR1, for_usr1)
    usr2 = signal.signal(signal.SIGUSR2, for_usr2)
    alrm = signal.signal(signal.SIGALRM, for_alrm)
    zwróć usr1, usr2, alrm


# The signal handler. Just note that the signal occurred oraz
# z who.
def handle_signals(sig,frame):
    signal_blackboard[sig]['tripped'] += 1
    signal_blackboard[sig]['tripped_by'] = thread.get_ident()

# a function that will be spawned jako a separate thread.
def send_signals():
    os.kill(process_pid, signal.SIGUSR1)
    os.kill(process_pid, signal.SIGUSR2)
    signalled_all.release()

klasa ThreadSignals(unittest.TestCase):

    def test_signals(self):
        # Test signal handling semantics of threads.
        # We spawn a thread, have the thread send two signals, oraz
        # wait dla it to finish. Check that we got both signals
        # oraz that they were run by the main thread.
        signalled_all.acquire()
        self.spawnSignallingThread()
        signalled_all.acquire()
        # the signals that we asked the kernel to send
        # will come back, but we don't know when.
        # (it might even be after the thread exits
        # oraz might be out of order.)  If we haven't seen
        # the signals yet, send yet another signal oraz
        # wait dla it return.
        jeżeli signal_blackboard[signal.SIGUSR1]['tripped'] == 0 \
           albo signal_blackboard[signal.SIGUSR2]['tripped'] == 0:
            signal.alarm(1)
            signal.pause()
            signal.alarm(0)

        self.assertEqual( signal_blackboard[signal.SIGUSR1]['tripped'], 1)
        self.assertEqual( signal_blackboard[signal.SIGUSR1]['tripped_by'],
                           thread.get_ident())
        self.assertEqual( signal_blackboard[signal.SIGUSR2]['tripped'], 1)
        self.assertEqual( signal_blackboard[signal.SIGUSR2]['tripped_by'],
                           thread.get_ident())
        signalled_all.release()

    def spawnSignallingThread(self):
        thread.start_new_thread(send_signals, ())

    def alarm_interrupt(self, sig, frame):
        podnieś KeyboardInterrupt

    @unittest.skipIf(USING_PTHREAD_COND,
                     'POSIX condition variables cannot be interrupted')
    # Issue #20564: sem_timedwait() cannot be interrupted on OpenBSD
    @unittest.skipIf(sys.platform.startswith('openbsd'),
                     'lock cannot be interrupted on OpenBSD')
    def test_lock_acquire_interruption(self):
        # Mimic receiving a SIGINT (KeyboardInterrupt) przy SIGALRM dopóki stuck
        # w a deadlock.
        # XXX this test can fail when the legacy (non-semaphore) implementation
        # of locks jest used w thread_pthread.h, see issue #11223.
        oldalrm = signal.signal(signal.SIGALRM, self.alarm_interrupt)
        spróbuj:
            lock = thread.allocate_lock()
            lock.acquire()
            signal.alarm(1)
            t1 = time.time()
            self.assertRaises(KeyboardInterrupt, lock.acquire, timeout=5)
            dt = time.time() - t1
            # Checking that KeyboardInterrupt was podnieśd jest nie sufficient.
            # We want to assert that lock.acquire() was interrupted because
            # of the signal, nie that the signal handler was called immediately
            # after timeout zwróć of lock.acquire() (which can fool assertRaises).
            self.assertLess(dt, 3.0)
        w_końcu:
            signal.signal(signal.SIGALRM, oldalrm)

    @unittest.skipIf(USING_PTHREAD_COND,
                     'POSIX condition variables cannot be interrupted')
    # Issue #20564: sem_timedwait() cannot be interrupted on OpenBSD
    @unittest.skipIf(sys.platform.startswith('openbsd'),
                     'lock cannot be interrupted on OpenBSD')
    def test_rlock_acquire_interruption(self):
        # Mimic receiving a SIGINT (KeyboardInterrupt) przy SIGALRM dopóki stuck
        # w a deadlock.
        # XXX this test can fail when the legacy (non-semaphore) implementation
        # of locks jest used w thread_pthread.h, see issue #11223.
        oldalrm = signal.signal(signal.SIGALRM, self.alarm_interrupt)
        spróbuj:
            rlock = thread.RLock()
            # For reentrant locks, the initial acquisition must be w another
            # thread.
            def other_thread():
                rlock.acquire()
            thread.start_new_thread(other_thread, ())
            # Wait until we can't acquire it without blocking...
            dopóki rlock.acquire(blocking=Nieprawda):
                rlock.release()
                time.sleep(0.01)
            signal.alarm(1)
            t1 = time.time()
            self.assertRaises(KeyboardInterrupt, rlock.acquire, timeout=5)
            dt = time.time() - t1
            # See rationale above w test_lock_acquire_interruption
            self.assertLess(dt, 3.0)
        w_końcu:
            signal.signal(signal.SIGALRM, oldalrm)

    def acquire_retries_on_intr(self, lock):
        self.sig_recvd = Nieprawda
        def my_handler(signal, frame):
            self.sig_recvd = Prawda
        old_handler = signal.signal(signal.SIGUSR1, my_handler)
        spróbuj:
            def other_thread():
                # Acquire the lock w a non-main thread, so this test works for
                # RLocks.
                lock.acquire()
                # Wait until the main thread jest blocked w the lock acquire, oraz
                # then wake it up przy this.
                time.sleep(0.5)
                os.kill(process_pid, signal.SIGUSR1)
                # Let the main thread take the interrupt, handle it, oraz retry
                # the lock acquisition.  Then we'll let it run.
                time.sleep(0.5)
                lock.release()
            thread.start_new_thread(other_thread, ())
            # Wait until we can't acquire it without blocking...
            dopóki lock.acquire(blocking=Nieprawda):
                lock.release()
                time.sleep(0.01)
            result = lock.acquire()  # Block dopóki we receive a signal.
            self.assertPrawda(self.sig_recvd)
            self.assertPrawda(result)
        w_końcu:
            signal.signal(signal.SIGUSR1, old_handler)

    def test_lock_acquire_retries_on_intr(self):
        self.acquire_retries_on_intr(thread.allocate_lock())

    def test_rlock_acquire_retries_on_intr(self):
        self.acquire_retries_on_intr(thread.RLock())

    def test_interrupted_timed_acquire(self):
        # Test to make sure we recompute lock acquisition timeouts when we
        # receive a signal.  Check this by repeatedly interrupting a lock
        # acquire w the main thread, oraz make sure that the lock acquire times
        # out after the right amount of time.
        # NOTE: this test only behaves jako expected jeżeli C signals get delivered
        # to the main thread.  Otherwise lock.acquire() itself doesn't get
        # interrupted oraz the test trivially succeeds.
        self.start = Nic
        self.end = Nic
        self.sigs_recvd = 0
        done = thread.allocate_lock()
        done.acquire()
        lock = thread.allocate_lock()
        lock.acquire()
        def my_handler(signum, frame):
            self.sigs_recvd += 1
        old_handler = signal.signal(signal.SIGUSR1, my_handler)
        spróbuj:
            def timed_acquire():
                self.start = time.time()
                lock.acquire(timeout=0.5)
                self.end = time.time()
            def send_signals():
                dla _ w range(40):
                    time.sleep(0.02)
                    os.kill(process_pid, signal.SIGUSR1)
                done.release()

            # Send the signals z the non-main thread, since the main thread
            # jest the only one that can process signals.
            thread.start_new_thread(send_signals, ())
            timed_acquire()
            # Wait dla thread to finish
            done.acquire()
            # This allows dla some timing oraz scheduling imprecision
            self.assertLess(self.end - self.start, 2.0)
            self.assertGreater(self.end - self.start, 0.3)
            # If the signal jest received several times before PyErr_CheckSignals()
            # jest called, the handler will get called less than 40 times. Just
            # check it's been called at least once.
            self.assertGreater(self.sigs_recvd, 0)
        w_końcu:
            signal.signal(signal.SIGUSR1, old_handler)


def test_main():
    global signal_blackboard

    signal_blackboard = { signal.SIGUSR1 : {'tripped': 0, 'tripped_by': 0 },
                          signal.SIGUSR2 : {'tripped': 0, 'tripped_by': 0 },
                          signal.SIGALRM : {'tripped': 0, 'tripped_by': 0 } }

    oldsigs = registerSignals(handle_signals, handle_signals, handle_signals)
    spróbuj:
        run_unittest(ThreadSignals)
    w_końcu:
        registerSignals(*oldsigs)

jeżeli __name__ == '__main__':
    test_main()
