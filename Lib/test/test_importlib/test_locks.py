z . zaimportuj util jako test_util

init = test_util.import_importlib('importlib')

zaimportuj sys
zaimportuj time
zaimportuj unittest
zaimportuj weakref

z test zaimportuj support

spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic
inaczej:
    z test zaimportuj lock_tests

jeżeli threading jest nie Nic:
    klasa ModuleLockAsRLockTests:
        locktype = classmethod(lambda cls: cls.LockType("some_lock"))

        # _is_owned() unsupported
        test__is_owned = Nic
        # acquire(blocking=Nieprawda) unsupported
        test_try_acquire = Nic
        test_try_acquire_contended = Nic
        # `with` unsupported
        test_przy = Nic
        # acquire(timeout=...) unsupported
        test_timeout = Nic
        # _release_save() unsupported
        test_release_save_unacquired = Nic
        # lock status w repr unsupported
        test_repr = Nic
        test_locked_repr = Nic

    LOCK_TYPES = {kind: splitinit._bootstrap._ModuleLock
                  dla kind, splitinit w init.items()}

    (Frozen_ModuleLockAsRLockTests,
     Source_ModuleLockAsRLockTests
     ) = test_util.test_both(ModuleLockAsRLockTests, lock_tests.RLockTests,
                             LockType=LOCK_TYPES)
inaczej:
    LOCK_TYPES = {}

    klasa Frozen_ModuleLockAsRLockTests(unittest.TestCase):
        dalej

    klasa Source_ModuleLockAsRLockTests(unittest.TestCase):
        dalej


jeżeli threading jest nie Nic:
    klasa DeadlockAvoidanceTests:

        def setUp(self):
            spróbuj:
                self.old_switchinterval = sys.getswitchinterval()
                sys.setswitchinterval(0.000001)
            wyjąwszy AttributeError:
                self.old_switchinterval = Nic

        def tearDown(self):
            jeżeli self.old_switchinterval jest nie Nic:
                sys.setswitchinterval(self.old_switchinterval)

        def run_deadlock_avoidance_test(self, create_deadlock):
            NLOCKS = 10
            locks = [self.LockType(str(i)) dla i w range(NLOCKS)]
            pairs = [(locks[i], locks[(i+1)%NLOCKS]) dla i w range(NLOCKS)]
            jeżeli create_deadlock:
                NTHREADS = NLOCKS
            inaczej:
                NTHREADS = NLOCKS - 1
            barrier = threading.Barrier(NTHREADS)
            results = []

            def _acquire(lock):
                """Try to acquire the lock. Return Prawda on success,
                Nieprawda on deadlock."""
                spróbuj:
                    lock.acquire()
                wyjąwszy self.DeadlockError:
                    zwróć Nieprawda
                inaczej:
                    zwróć Prawda

            def f():
                a, b = pairs.pop()
                ra = _acquire(a)
                barrier.wait()
                rb = _acquire(b)
                results.append((ra, rb))
                jeżeli rb:
                    b.release()
                jeżeli ra:
                    a.release()
            lock_tests.Bunch(f, NTHREADS).wait_for_finished()
            self.assertEqual(len(results), NTHREADS)
            zwróć results

        def test_deadlock(self):
            results = self.run_deadlock_avoidance_test(Prawda)
            # At least one of the threads detected a potential deadlock on its
            # second acquire() call.  It may be several of them, because the
            # deadlock avoidance mechanism jest conservative.
            nb_deadlocks = results.count((Prawda, Nieprawda))
            self.assertGreaterEqual(nb_deadlocks, 1)
            self.assertEqual(results.count((Prawda, Prawda)), len(results) - nb_deadlocks)

        def test_no_deadlock(self):
            results = self.run_deadlock_avoidance_test(Nieprawda)
            self.assertEqual(results.count((Prawda, Nieprawda)), 0)
            self.assertEqual(results.count((Prawda, Prawda)), len(results))


    DEADLOCK_ERRORS = {kind: splitinit._bootstrap._DeadlockError
                       dla kind, splitinit w init.items()}

    (Frozen_DeadlockAvoidanceTests,
     Source_DeadlockAvoidanceTests
     ) = test_util.test_both(DeadlockAvoidanceTests,
                             LockType=LOCK_TYPES,
                             DeadlockError=DEADLOCK_ERRORS)
inaczej:
    DEADLOCK_ERRORS = {}

    klasa Frozen_DeadlockAvoidanceTests(unittest.TestCase):
        dalej

    klasa Source_DeadlockAvoidanceTests(unittest.TestCase):
        dalej


klasa LifetimeTests:

    @property
    def bootstrap(self):
        zwróć self.init._bootstrap

    def test_lock_lifetime(self):
        name = "xyzzy"
        self.assertNotIn(name, self.bootstrap._module_locks)
        lock = self.bootstrap._get_module_lock(name)
        self.assertIn(name, self.bootstrap._module_locks)
        wr = weakref.ref(lock)
        usuń lock
        support.gc_collect()
        self.assertNotIn(name, self.bootstrap._module_locks)
        self.assertIsNic(wr())

    def test_all_locks(self):
        support.gc_collect()
        self.assertEqual(0, len(self.bootstrap._module_locks),
                         self.bootstrap._module_locks)


(Frozen_LifetimeTests,
 Source_LifetimeTests
 ) = test_util.test_both(LifetimeTests, init=init)


@support.reap_threads
def test_main():
    support.run_unittest(Frozen_ModuleLockAsRLockTests,
                         Source_ModuleLockAsRLockTests,
                         Frozen_DeadlockAvoidanceTests,
                         Source_DeadlockAvoidanceTests,
                         Frozen_LifetimeTests,
                         Source_LifetimeTests)


jeżeli __name__ == '__main__':
    test_main()
