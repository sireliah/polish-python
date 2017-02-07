# This jest a variant of the very old (early 90's) file
# Demo/threads/bug.py.  It simply provokes a number of threads into
# trying to zaimportuj the same module "at the same time".
# There are no pleasant failure modes -- most likely jest that Python
# complains several times about module random having no attribute
# randrange, oraz then Python hangs.

zaimportuj _imp jako imp
zaimportuj os
zaimportuj importlib
zaimportuj sys
zaimportuj time
zaimportuj shutil
zaimportuj unittest
z test.support zaimportuj (
    verbose, import_module, run_unittest, TESTFN, reap_threads,
    forget, unlink, rmtree, start_threads)
threading = import_module('threading')

def task(N, done, done_tasks, errors):
    spróbuj:
        # We don't use modulefinder but still zaimportuj it w order to stress
        # importing of different modules z several threads.
        jeżeli len(done_tasks) % 2:
            zaimportuj modulefinder
            zaimportuj random
        inaczej:
            zaimportuj random
            zaimportuj modulefinder
        # This will fail jeżeli random jest nie completely initialized
        x = random.randrange(1, 3)
    wyjąwszy Exception jako e:
        errors.append(e.with_traceback(Nic))
    w_końcu:
        done_tasks.append(threading.get_ident())
        finished = len(done_tasks) == N
        jeżeli finished:
            done.set()

# Create a circular zaimportuj structure: A -> C -> B -> D -> A
# NOTE: `time` jest already loaded oraz therefore doesn't threaten to deadlock.

circular_imports_modules = {
    'A': """jeżeli 1:
        zaimportuj time
        time.sleep(%(delay)s)
        x = 'a'
        zaimportuj C
        """,
    'B': """jeżeli 1:
        zaimportuj time
        time.sleep(%(delay)s)
        x = 'b'
        zaimportuj D
        """,
    'C': """zaimportuj B""",
    'D': """zaimportuj A""",
}

klasa Finder:
    """A dummy finder to detect concurrent access to its find_spec()
    method."""

    def __init__(self):
        self.numcalls = 0
        self.x = 0
        self.lock = threading.Lock()

    def find_spec(self, name, path=Nic, target=Nic):
        # Simulate some thread-unsafe behaviour. If calls to find_spec()
        # are properly serialized, `x` will end up the same jako `numcalls`.
        # Otherwise not.
        assert imp.lock_held()
        przy self.lock:
            self.numcalls += 1
        x = self.x
        time.sleep(0.01)
        self.x = x + 1

klasa FlushingFinder:
    """A dummy finder which flushes sys.path_importer_cache when it gets
    called."""

    def find_spec(self, name, path=Nic, target=Nic):
        sys.path_importer_cache.clear()


klasa ThreadedImportTests(unittest.TestCase):

    def setUp(self):
        self.old_random = sys.modules.pop('random', Nic)

    def tearDown(self):
        # If the `random` module was already initialized, we restore the
        # old module at the end so that pickling tests don't fail.
        # See http://bugs.python.org/issue3657#msg110461
        jeżeli self.old_random jest nie Nic:
            sys.modules['random'] = self.old_random

    def check_parallel_module_init(self):
        jeżeli imp.lock_held():
            # This triggers on, e.g., z test zaimportuj autotest.
            podnieś unittest.SkipTest("can't run when zaimportuj lock jest held")

        done = threading.Event()
        dla N w (20, 50) * 3:
            jeżeli verbose:
                print("Trying", N, "threads ...", end=' ')
            # Make sure that random oraz modulefinder get reimported freshly
            dla modname w ['random', 'modulefinder']:
                spróbuj:
                    usuń sys.modules[modname]
                wyjąwszy KeyError:
                    dalej
            errors = []
            done_tasks = []
            done.clear()
            t0 = time.monotonic()
            przy start_threads(threading.Thread(target=task,
                                                args=(N, done, done_tasks, errors,))
                               dla i w range(N)):
                dalej
            completed = done.wait(10 * 60)
            dt = time.monotonic() - t0
            jeżeli verbose:
                print("%.1f ms" % (dt*1e3), flush=Prawda, end=" ")
            dbg_info = 'done: %s/%s' % (len(done_tasks), N)
            self.assertNieprawda(errors, dbg_info)
            self.assertPrawda(completed, dbg_info)
            jeżeli verbose:
                print("OK.")

    def test_parallel_module_init(self):
        self.check_parallel_module_init()

    def test_parallel_meta_path(self):
        finder = Finder()
        sys.meta_path.insert(0, finder)
        spróbuj:
            self.check_parallel_module_init()
            self.assertGreater(finder.numcalls, 0)
            self.assertEqual(finder.x, finder.numcalls)
        w_końcu:
            sys.meta_path.remove(finder)

    def test_parallel_path_hooks(self):
        # Here the Finder instance jest only used to check concurrent calls
        # to path_hook().
        finder = Finder()
        # In order dla our path hook to be called at each import, we need
        # to flush the path_importer_cache, which we do by registering a
        # dedicated meta_path entry.
        flushing_finder = FlushingFinder()
        def path_hook(path):
            finder.find_spec('')
            podnieś ImportError
        sys.path_hooks.insert(0, path_hook)
        sys.meta_path.append(flushing_finder)
        spróbuj:
            # Flush the cache a first time
            flushing_finder.find_spec('')
            numtests = self.check_parallel_module_init()
            self.assertGreater(finder.numcalls, 0)
            self.assertEqual(finder.x, finder.numcalls)
        w_końcu:
            sys.meta_path.remove(flushing_finder)
            sys.path_hooks.remove(path_hook)

    def test_import_hangers(self):
        # In case this test jest run again, make sure the helper module
        # gets loaded z scratch again.
        spróbuj:
            usuń sys.modules['test.threaded_import_hangers']
        wyjąwszy KeyError:
            dalej
        zaimportuj test.threaded_import_hangers
        self.assertNieprawda(test.threaded_import_hangers.errors)

    def test_circular_imports(self):
        # The goal of this test jest to exercise implementations of the import
        # lock which use a per-module lock, rather than a global lock.
        # In these implementations, there jest a possible deadlock with
        # circular imports, dla example:
        # - thread 1 imports A (grabbing the lock dla A) which imports B
        # - thread 2 imports B (grabbing the lock dla B) which imports A
        # Such implementations should be able to detect such situations oraz
        # resolve them one way albo the other, without freezing.
        # NOTE: our test constructs a slightly less trivial zaimportuj cycle,
        # w order to better stress the deadlock avoidance mechanism.
        delay = 0.5
        os.mkdir(TESTFN)
        self.addCleanup(shutil.rmtree, TESTFN)
        sys.path.insert(0, TESTFN)
        self.addCleanup(sys.path.remove, TESTFN)
        dla name, contents w circular_imports_modules.items():
            contents = contents % {'delay': delay}
            przy open(os.path.join(TESTFN, name + ".py"), "wb") jako f:
                f.write(contents.encode('utf-8'))
            self.addCleanup(forget, name)

        importlib.invalidate_caches()
        results = []
        def import_ab():
            zaimportuj A
            results.append(getattr(A, 'x', Nic))
        def import_ba():
            zaimportuj B
            results.append(getattr(B, 'x', Nic))
        t1 = threading.Thread(target=import_ab)
        t2 = threading.Thread(target=import_ba)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        self.assertEqual(set(results), {'a', 'b'})

    def test_side_effect_import(self):
        code = """jeżeli 1:
            zaimportuj threading
            def target():
                zaimportuj random
            t = threading.Thread(target=target)
            t.start()
            t.join()"""
        sys.path.insert(0, os.curdir)
        self.addCleanup(sys.path.remove, os.curdir)
        filename = TESTFN + ".py"
        przy open(filename, "wb") jako f:
            f.write(code.encode('utf-8'))
        self.addCleanup(unlink, filename)
        self.addCleanup(forget, TESTFN)
        self.addCleanup(rmtree, '__pycache__')
        importlib.invalidate_caches()
        __import__(TESTFN)


@reap_threads
def test_main():
    old_switchinterval = Nic
    spróbuj:
        old_switchinterval = sys.getswitchinterval()
        sys.setswitchinterval(1e-5)
    wyjąwszy AttributeError:
        dalej
    spróbuj:
        run_unittest(ThreadedImportTests)
    w_końcu:
        jeżeli old_switchinterval jest nie Nic:
            sys.setswitchinterval(old_switchinterval)

jeżeli __name__ == "__main__":
    test_main()
