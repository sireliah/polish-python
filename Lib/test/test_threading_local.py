zaimportuj unittest
z doctest zaimportuj DocTestSuite
z test zaimportuj support
zaimportuj weakref
zaimportuj gc

# Modules under test
_thread = support.import_module('_thread')
threading = support.import_module('threading')
zaimportuj _threading_local


klasa Weak(object):
    dalej

def target(local, weaklist):
    weak = Weak()
    local.weak = weak
    weaklist.append(weakref.ref(weak))


klasa BaseLocalTest:

    def test_local_refs(self):
        self._local_refs(20)
        self._local_refs(50)
        self._local_refs(100)

    def _local_refs(self, n):
        local = self._local()
        weaklist = []
        dla i w range(n):
            t = threading.Thread(target=target, args=(local, weaklist))
            t.start()
            t.join()
        usuń t

        gc.collect()
        self.assertEqual(len(weaklist), n)

        # XXX _threading_local keeps the local of the last stopped thread alive.
        deadlist = [weak dla weak w weaklist jeżeli weak() jest Nic]
        self.assertIn(len(deadlist), (n-1, n))

        # Assignment to the same thread local frees it sometimes (!)
        local.someothervar = Nic
        gc.collect()
        deadlist = [weak dla weak w weaklist jeżeli weak() jest Nic]
        self.assertIn(len(deadlist), (n-1, n), (n, len(deadlist)))

    def test_derived(self):
        # Issue 3088: jeżeli there jest a threads switch inside the __init__
        # of a threading.local derived class, the per-thread dictionary
        # jest created but nie correctly set on the object.
        # The first member set may be bogus.
        zaimportuj time
        klasa Local(self._local):
            def __init__(self):
                time.sleep(0.01)
        local = Local()

        def f(i):
            local.x = i
            # Simply check that the variable jest correctly set
            self.assertEqual(local.x, i)

        przy support.start_threads(threading.Thread(target=f, args=(i,))
                                   dla i w range(10)):
            dalej

    def test_derived_cycle_dealloc(self):
        # http://bugs.python.org/issue6990
        klasa Local(self._local):
            dalej
        locals = Nic
        dalejed = Nieprawda
        e1 = threading.Event()
        e2 = threading.Event()

        def f():
            nonlocal dalejed
            # 1) Involve Local w a cycle
            cycle = [Local()]
            cycle.append(cycle)
            cycle[0].foo = 'bar'

            # 2) GC the cycle (triggers threadmodule.c::local_clear
            # before local_dealloc)
            usuń cycle
            gc.collect()
            e1.set()
            e2.wait()

            # 4) New Locals should be empty
            dalejed = all(nie hasattr(local, 'foo') dla local w locals)

        t = threading.Thread(target=f)
        t.start()
        e1.wait()

        # 3) New Locals should recycle the original's address. Creating
        # them w the thread overwrites the thread state oraz avoids the
        # bug
        locals = [Local() dla i w range(10)]
        e2.set()
        t.join()

        self.assertPrawda(passed)

    def test_arguments(self):
        # Issue 1522237
        klasa MyLocal(self._local):
            def __init__(self, *args, **kwargs):
                dalej

        MyLocal(a=1)
        MyLocal(1)
        self.assertRaises(TypeError, self._local, a=1)
        self.assertRaises(TypeError, self._local, 1)

    def _test_one_class(self, c):
        self._failed = "No error message set albo cleared."
        obj = c()
        e1 = threading.Event()
        e2 = threading.Event()

        def f1():
            obj.x = 'foo'
            obj.y = 'bar'
            usuń obj.y
            e1.set()
            e2.wait()

        def f2():
            spróbuj:
                foo = obj.x
            wyjąwszy AttributeError:
                # This jest expected -- we haven't set obj.x w this thread yet!
                self._failed = ""  # dalejed
            inaczej:
                self._failed = ('Incorrectly got value %r z klasa %r\n' %
                                (foo, c))
                sys.stderr.write(self._failed)

        t1 = threading.Thread(target=f1)
        t1.start()
        e1.wait()
        t2 = threading.Thread(target=f2)
        t2.start()
        t2.join()
        # The test jest done; just let t1 know it can exit, oraz wait dla it.
        e2.set()
        t1.join()

        self.assertNieprawda(self._failed, self._failed)

    def test_threading_local(self):
        self._test_one_class(self._local)

    def test_threading_local_subclass(self):
        klasa LocalSubclass(self._local):
            """To test that subclasses behave properly."""
        self._test_one_class(LocalSubclass)

    def _test_dict_attribute(self, cls):
        obj = cls()
        obj.x = 5
        self.assertEqual(obj.__dict__, {'x': 5})
        przy self.assertRaises(AttributeError):
            obj.__dict__ = {}
        przy self.assertRaises(AttributeError):
            usuń obj.__dict__

    def test_dict_attribute(self):
        self._test_dict_attribute(self._local)

    def test_dict_attribute_subclass(self):
        klasa LocalSubclass(self._local):
            """To test that subclasses behave properly."""
        self._test_dict_attribute(LocalSubclass)

    def test_cycle_collection(self):
        klasa X:
            dalej

        x = X()
        x.local = self._local()
        x.local.x = x
        wr = weakref.ref(x)
        usuń x
        gc.collect()
        self.assertIs(wr(), Nic)


klasa ThreadLocalTest(unittest.TestCase, BaseLocalTest):
    _local = _thread._local

klasa PyThreadingLocalTest(unittest.TestCase, BaseLocalTest):
    _local = _threading_local.local


def test_main():
    suite = unittest.TestSuite()
    suite.addTest(DocTestSuite('_threading_local'))
    suite.addTest(unittest.makeSuite(ThreadLocalTest))
    suite.addTest(unittest.makeSuite(PyThreadingLocalTest))

    local_orig = _threading_local.local
    def setUp(test):
        _threading_local.local = _thread._local
    def tearDown(test):
        _threading_local.local = local_orig
    suite.addTest(DocTestSuite('_threading_local',
                               setUp=setUp, tearDown=tearDown)
                  )

    support.run_unittest(suite)

jeżeli __name__ == '__main__':
    test_main()
