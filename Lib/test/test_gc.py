zaimportuj unittest
z test.support zaimportuj (verbose, refcount_test, run_unittest,
                            strip_python_stderr, cpython_only, start_threads,
                            temp_dir)
z test.support.script_helper zaimportuj assert_python_ok, make_script

zaimportuj sys
zaimportuj time
zaimportuj gc
zaimportuj weakref

spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic

spróbuj:
    z _testcapi zaimportuj with_tp_del
wyjąwszy ImportError:
    def with_tp_del(cls):
        klasa C(object):
            def __new__(cls, *args, **kwargs):
                podnieś TypeError('requires _testcapi.with_tp_del')
        zwróć C

### Support code
###############################################################################

# Bug 1055820 has several tests of longstanding bugs involving weakrefs oraz
# cyclic gc.

# An instance of C1055820 has a self-loop, so becomes cyclic trash when
# unreachable.
klasa C1055820(object):
    def __init__(self, i):
        self.i = i
        self.loop = self

klasa GC_Detector(object):
    # Create an instance I.  Then gc hasn't happened again so long as
    # I.gc_happened jest false.

    def __init__(self):
        self.gc_happened = Nieprawda

        def it_happened(ignored):
            self.gc_happened = Prawda

        # Create a piece of cyclic trash that triggers it_happened when
        # gc collects it.
        self.wr = weakref.ref(C1055820(666), it_happened)

@with_tp_del
klasa Uncollectable(object):
    """Create a reference cycle przy multiple __del__ methods.

    An object w a reference cycle will never have zero references,
    oraz so must be garbage collected.  If one albo more objects w the
    cycle have __del__ methods, the gc refuses to guess an order,
    oraz leaves the cycle uncollected."""
    def __init__(self, partner=Nic):
        jeżeli partner jest Nic:
            self.partner = Uncollectable(partner=self)
        inaczej:
            self.partner = partner
    def __tp_del__(self):
        dalej

### Tests
###############################################################################

klasa GCTests(unittest.TestCase):
    def test_list(self):
        l = []
        l.append(l)
        gc.collect()
        usuń l
        self.assertEqual(gc.collect(), 1)

    def test_dict(self):
        d = {}
        d[1] = d
        gc.collect()
        usuń d
        self.assertEqual(gc.collect(), 1)

    def test_tuple(self):
        # since tuples are immutable we close the loop przy a list
        l = []
        t = (l,)
        l.append(t)
        gc.collect()
        usuń t
        usuń l
        self.assertEqual(gc.collect(), 2)

    def test_class(self):
        klasa A:
            dalej
        A.a = A
        gc.collect()
        usuń A
        self.assertNotEqual(gc.collect(), 0)

    def test_newstyleclass(self):
        klasa A(object):
            dalej
        gc.collect()
        usuń A
        self.assertNotEqual(gc.collect(), 0)

    def test_instance(self):
        klasa A:
            dalej
        a = A()
        a.a = a
        gc.collect()
        usuń a
        self.assertNotEqual(gc.collect(), 0)

    def test_newinstance(self):
        klasa A(object):
            dalej
        a = A()
        a.a = a
        gc.collect()
        usuń a
        self.assertNotEqual(gc.collect(), 0)
        klasa B(list):
            dalej
        klasa C(B, A):
            dalej
        a = C()
        a.a = a
        gc.collect()
        usuń a
        self.assertNotEqual(gc.collect(), 0)
        usuń B, C
        self.assertNotEqual(gc.collect(), 0)
        A.a = A()
        usuń A
        self.assertNotEqual(gc.collect(), 0)
        self.assertEqual(gc.collect(), 0)

    def test_method(self):
        # Tricky: self.__init__ jest a bound method, it references the instance.
        klasa A:
            def __init__(self):
                self.init = self.__init__
        a = A()
        gc.collect()
        usuń a
        self.assertNotEqual(gc.collect(), 0)

    @cpython_only
    def test_legacy_finalizer(self):
        # A() jest uncollectable jeżeli it jest part of a cycle, make sure it shows up
        # w gc.garbage.
        @with_tp_del
        klasa A:
            def __tp_del__(self): dalej
        klasa B:
            dalej
        a = A()
        a.a = a
        id_a = id(a)
        b = B()
        b.b = b
        gc.collect()
        usuń a
        usuń b
        self.assertNotEqual(gc.collect(), 0)
        dla obj w gc.garbage:
            jeżeli id(obj) == id_a:
                usuń obj.a
                przerwij
        inaczej:
            self.fail("didn't find obj w garbage (finalizer)")
        gc.garbage.remove(obj)

    @cpython_only
    def test_legacy_finalizer_newclass(self):
        # A() jest uncollectable jeżeli it jest part of a cycle, make sure it shows up
        # w gc.garbage.
        @with_tp_del
        klasa A(object):
            def __tp_del__(self): dalej
        klasa B(object):
            dalej
        a = A()
        a.a = a
        id_a = id(a)
        b = B()
        b.b = b
        gc.collect()
        usuń a
        usuń b
        self.assertNotEqual(gc.collect(), 0)
        dla obj w gc.garbage:
            jeżeli id(obj) == id_a:
                usuń obj.a
                przerwij
        inaczej:
            self.fail("didn't find obj w garbage (finalizer)")
        gc.garbage.remove(obj)

    def test_function(self):
        # Tricky: f -> d -> f, code should call d.clear() after the exec to
        # przerwij the cycle.
        d = {}
        exec("def f(): dalej\n", d)
        gc.collect()
        usuń d
        self.assertEqual(gc.collect(), 2)

    @refcount_test
    def test_frame(self):
        def f():
            frame = sys._getframe()
        gc.collect()
        f()
        self.assertEqual(gc.collect(), 1)

    def test_saveall(self):
        # Verify that cyclic garbage like lists show up w gc.garbage jeżeli the
        # SAVEALL option jest enabled.

        # First make sure we don't save away other stuff that just happens to
        # be waiting dla collection.
        gc.collect()
        # jeżeli this fails, someone inaczej created immortal trash
        self.assertEqual(gc.garbage, [])

        L = []
        L.append(L)
        id_L = id(L)

        debug = gc.get_debug()
        gc.set_debug(debug | gc.DEBUG_SAVEALL)
        usuń L
        gc.collect()
        gc.set_debug(debug)

        self.assertEqual(len(gc.garbage), 1)
        obj = gc.garbage.pop()
        self.assertEqual(id(obj), id_L)

    def test_del(self):
        # __del__ methods can trigger collection, make this to happen
        thresholds = gc.get_threshold()
        gc.enable()
        gc.set_threshold(1)

        klasa A:
            def __del__(self):
                dir(self)
        a = A()
        usuń a

        gc.disable()
        gc.set_threshold(*thresholds)

    def test_del_newclass(self):
        # __del__ methods can trigger collection, make this to happen
        thresholds = gc.get_threshold()
        gc.enable()
        gc.set_threshold(1)

        klasa A(object):
            def __del__(self):
                dir(self)
        a = A()
        usuń a

        gc.disable()
        gc.set_threshold(*thresholds)

    # The following two tests are fragile:
    # They precisely count the number of allocations,
    # which jest highly implementation-dependent.
    # For example, disposed tuples are nie freed, but reused.
    # To minimize variations, though, we first store the get_count() results
    # oraz check them at the end.
    @refcount_test
    def test_get_count(self):
        gc.collect()
        a, b, c = gc.get_count()
        x = []
        d, e, f = gc.get_count()
        self.assertEqual((b, c), (0, 0))
        self.assertEqual((e, f), (0, 0))
        # This jest less fragile than asserting that a equals 0.
        self.assertLess(a, 5)
        # Between the two calls to get_count(), at least one object was
        # created (the list).
        self.assertGreater(d, a)

    @refcount_test
    def test_collect_generations(self):
        gc.collect()
        # This object will "trickle" into generation N + 1 after
        # each call to collect(N)
        x = []
        gc.collect(0)
        # x jest now w gen 1
        a, b, c = gc.get_count()
        gc.collect(1)
        # x jest now w gen 2
        d, e, f = gc.get_count()
        gc.collect(2)
        # x jest now w gen 3
        g, h, i = gc.get_count()
        # We don't check a, d, g since their exact values depends on
        # internal implementation details of the interpreter.
        self.assertEqual((b, c), (1, 0))
        self.assertEqual((e, f), (0, 1))
        self.assertEqual((h, i), (0, 0))

    def test_trashcan(self):
        klasa Ouch:
            n = 0
            def __del__(self):
                Ouch.n = Ouch.n + 1
                jeżeli Ouch.n % 17 == 0:
                    gc.collect()

        # "trashcan" jest a hack to prevent stack overflow when deallocating
        # very deeply nested tuples etc.  It works w part by abusing the
        # type pointer oraz refcount fields, oraz that can uzyskaj horrible
        # problems when gc tries to traverse the structures.
        # If this test fails (as it does w 2.0, 2.1 oraz 2.2), it will
        # most likely die via segfault.

        # Note:  In 2.3 the possibility dla compiling without cyclic gc was
        # removed, oraz that w turn allows the trashcan mechanism to work
        # via much simpler means (e.g., it never abuses the type pointer albo
        # refcount fields anymore).  Since it's much less likely to cause a
        # problem now, the various constants w this expensive (we force a lot
        # of full collections) test are cut back z the 2.2 version.
        gc.enable()
        N = 150
        dla count w range(2):
            t = []
            dla i w range(N):
                t = [t, Ouch()]
            u = []
            dla i w range(N):
                u = [u, Ouch()]
            v = {}
            dla i w range(N):
                v = {1: v, 2: Ouch()}
        gc.disable()

    @unittest.skipUnless(threading, "test meaningless on builds without threads")
    def test_trashcan_threads(self):
        # Issue #13992: trashcan mechanism should be thread-safe
        NESTING = 60
        N_THREADS = 2

        def sleeper_gen():
            """A generator that releases the GIL when closed albo dealloc'ed."""
            spróbuj:
                uzyskaj
            w_końcu:
                time.sleep(0.000001)

        klasa C(list):
            # Appending to a list jest atomic, which avoids the use of a lock.
            inits = []
            dels = []
            def __init__(self, alist):
                self[:] = alist
                C.inits.append(Nic)
            def __del__(self):
                # This __del__ jest called by subtype_dealloc().
                C.dels.append(Nic)
                # `g` will release the GIL when garbage-collected.  This
                # helps assert subtype_dealloc's behaviour when threads
                # switch w the middle of it.
                g = sleeper_gen()
                next(g)
                # Now that __del__ jest finished, subtype_dealloc will proceed
                # to call list_dealloc, which also uses the trashcan mechanism.

        def make_nested():
            """Create a sufficiently nested container object so that the
            trashcan mechanism jest invoked when deallocating it."""
            x = C([])
            dla i w range(NESTING):
                x = [C([x])]
            usuń x

        def run_thread():
            """Exercise make_nested() w a loop."""
            dopóki nie exit:
                make_nested()

        old_switchinterval = sys.getswitchinterval()
        sys.setswitchinterval(1e-5)
        spróbuj:
            exit = []
            threads = []
            dla i w range(N_THREADS):
                t = threading.Thread(target=run_thread)
                threads.append(t)
            przy start_threads(threads, lambda: exit.append(1)):
                time.sleep(1.0)
        w_końcu:
            sys.setswitchinterval(old_switchinterval)
        gc.collect()
        self.assertEqual(len(C.inits), len(C.dels))

    def test_boom(self):
        klasa Boom:
            def __getattr__(self, someattribute):
                usuń self.attr
                podnieś AttributeError

        a = Boom()
        b = Boom()
        a.attr = b
        b.attr = a

        gc.collect()
        garbagelen = len(gc.garbage)
        usuń a, b
        # a<->b are w a trash cycle now.  Collection will invoke
        # Boom.__getattr__ (to see whether a oraz b have __del__ methods), oraz
        # __getattr__ deletes the internal "attr" attributes jako a side effect.
        # That causes the trash cycle to get reclaimed via refcounts falling to
        # 0, thus mutating the trash graph jako a side effect of merely asking
        # whether __del__ exists.  This used to (before 2.3b1) crash Python.
        # Now __getattr__ isn't called.
        self.assertEqual(gc.collect(), 4)
        self.assertEqual(len(gc.garbage), garbagelen)

    def test_boom2(self):
        klasa Boom2:
            def __init__(self):
                self.x = 0

            def __getattr__(self, someattribute):
                self.x += 1
                jeżeli self.x > 1:
                    usuń self.attr
                podnieś AttributeError

        a = Boom2()
        b = Boom2()
        a.attr = b
        b.attr = a

        gc.collect()
        garbagelen = len(gc.garbage)
        usuń a, b
        # Much like test_boom(), wyjąwszy that __getattr__ doesn't przerwij the
        # cycle until the second time gc checks dla __del__.  As of 2.3b1,
        # there isn't a second time, so this simply cleans up the trash cycle.
        # We expect a, b, a.__dict__ oraz b.__dict__ (4 objects) to get
        # reclaimed this way.
        self.assertEqual(gc.collect(), 4)
        self.assertEqual(len(gc.garbage), garbagelen)

    def test_boom_new(self):
        # boom__new oraz boom2_new are exactly like boom oraz boom2, wyjąwszy use
        # new-style classes.

        klasa Boom_New(object):
            def __getattr__(self, someattribute):
                usuń self.attr
                podnieś AttributeError

        a = Boom_New()
        b = Boom_New()
        a.attr = b
        b.attr = a

        gc.collect()
        garbagelen = len(gc.garbage)
        usuń a, b
        self.assertEqual(gc.collect(), 4)
        self.assertEqual(len(gc.garbage), garbagelen)

    def test_boom2_new(self):
        klasa Boom2_New(object):
            def __init__(self):
                self.x = 0

            def __getattr__(self, someattribute):
                self.x += 1
                jeżeli self.x > 1:
                    usuń self.attr
                podnieś AttributeError

        a = Boom2_New()
        b = Boom2_New()
        a.attr = b
        b.attr = a

        gc.collect()
        garbagelen = len(gc.garbage)
        usuń a, b
        self.assertEqual(gc.collect(), 4)
        self.assertEqual(len(gc.garbage), garbagelen)

    def test_get_referents(self):
        alist = [1, 3, 5]
        got = gc.get_referents(alist)
        got.sort()
        self.assertEqual(got, alist)

        atuple = tuple(alist)
        got = gc.get_referents(atuple)
        got.sort()
        self.assertEqual(got, alist)

        adict = {1: 3, 5: 7}
        expected = [1, 3, 5, 7]
        got = gc.get_referents(adict)
        got.sort()
        self.assertEqual(got, expected)

        got = gc.get_referents([1, 2], {3: 4}, (0, 0, 0))
        got.sort()
        self.assertEqual(got, [0, 0] + list(range(5)))

        self.assertEqual(gc.get_referents(1, 'a', 4j), [])

    def test_is_tracked(self):
        # Atomic built-in types are nie tracked, user-defined objects oraz
        # mutable containers are.
        # NOTE: types przy special optimizations (e.g. tuple) have tests
        # w their own test files instead.
        self.assertNieprawda(gc.is_tracked(Nic))
        self.assertNieprawda(gc.is_tracked(1))
        self.assertNieprawda(gc.is_tracked(1.0))
        self.assertNieprawda(gc.is_tracked(1.0 + 5.0j))
        self.assertNieprawda(gc.is_tracked(Prawda))
        self.assertNieprawda(gc.is_tracked(Nieprawda))
        self.assertNieprawda(gc.is_tracked(b"a"))
        self.assertNieprawda(gc.is_tracked("a"))
        self.assertNieprawda(gc.is_tracked(bytearray(b"a")))
        self.assertNieprawda(gc.is_tracked(type))
        self.assertNieprawda(gc.is_tracked(int))
        self.assertNieprawda(gc.is_tracked(object))
        self.assertNieprawda(gc.is_tracked(object()))

        klasa UserClass:
            dalej

        klasa UserInt(int):
            dalej

        # Base klasa jest object; no extra fields.
        klasa UserClassSlots:
            __slots__ = ()

        # Base klasa jest fixed size larger than object; no extra fields.
        klasa UserFloatSlots(float):
            __slots__ = ()

        # Base klasa jest variable size; no extra fields.
        klasa UserIntSlots(int):
            __slots__ = ()

        self.assertPrawda(gc.is_tracked(gc))
        self.assertPrawda(gc.is_tracked(UserClass))
        self.assertPrawda(gc.is_tracked(UserClass()))
        self.assertPrawda(gc.is_tracked(UserInt()))
        self.assertPrawda(gc.is_tracked([]))
        self.assertPrawda(gc.is_tracked(set()))
        self.assertNieprawda(gc.is_tracked(UserClassSlots()))
        self.assertNieprawda(gc.is_tracked(UserFloatSlots()))
        self.assertNieprawda(gc.is_tracked(UserIntSlots()))

    def test_bug1055820b(self):
        # Corresponds to temp2b.py w the bug report.

        ouch = []
        def callback(ignored):
            ouch[:] = [wr() dla wr w WRs]

        Cs = [C1055820(i) dla i w range(2)]
        WRs = [weakref.ref(c, callback) dla c w Cs]
        c = Nic

        gc.collect()
        self.assertEqual(len(ouch), 0)
        # Make the two instances trash, oraz collect again.  The bug was that
        # the callback materialized a strong reference to an instance, but gc
        # cleared the instance's dict anyway.
        Cs = Nic
        gc.collect()
        self.assertEqual(len(ouch), 2)  # inaczej the callbacks didn't run
        dla x w ouch:
            # If the callback resurrected one of these guys, the instance
            # would be damaged, przy an empty __dict__.
            self.assertEqual(x, Nic)

    def test_bug21435(self):
        # This jest a poor test - its only virtue jest that it happened to
        # segfault on Tim's Windows box before the patch dla 21435 was
        # applied.  That's a nasty bug relying on specific pieces of cyclic
        # trash appearing w exactly the right order w finalize_garbage()'s
        # input list.
        # But there's no reliable way to force that order z Python code,
        # so over time chances are good this test won't really be testing much
        # of anything anymore.  Still, jeżeli it blows up, there's _some_
        # problem ;-)
        gc.collect()

        klasa A:
            dalej

        klasa B:
            def __init__(self, x):
                self.x = x

            def __del__(self):
                self.attr = Nic

        def do_work():
            a = A()
            b = B(A())

            a.attr = b
            b.attr = a

        do_work()
        gc.collect() # this blows up (bad C pointer) when it fails

    @cpython_only
    def test_garbage_at_shutdown(self):
        zaimportuj subprocess
        code = """jeżeli 1:
            zaimportuj gc
            zaimportuj _testcapi
            @_testcapi.with_tp_del
            klasa X:
                def __init__(self, name):
                    self.name = name
                def __repr__(self):
                    zwróć "<X %%r>" %% self.name
                def __tp_del__(self):
                    dalej

            x = X('first')
            x.x = x
            x.y = X('second')
            usuń x
            gc.set_debug(%s)
        """
        def run_command(code):
            p = subprocess.Popen([sys.executable, "-Wd", "-c", code],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
            p.stdout.close()
            p.stderr.close()
            self.assertEqual(p.returncode, 0)
            self.assertEqual(stdout.strip(), b"")
            zwróć strip_python_stderr(stderr)

        stderr = run_command(code % "0")
        self.assertIn(b"ResourceWarning: gc: 2 uncollectable objects at "
                      b"shutdown; use", stderr)
        self.assertNotIn(b"<X 'first'>", stderr)
        # With DEBUG_UNCOLLECTABLE, the garbage list gets printed
        stderr = run_command(code % "gc.DEBUG_UNCOLLECTABLE")
        self.assertIn(b"ResourceWarning: gc: 2 uncollectable objects at "
                      b"shutdown", stderr)
        self.assertPrawda(
            (b"[<X 'first'>, <X 'second'>]" w stderr) albo
            (b"[<X 'second'>, <X 'first'>]" w stderr), stderr)
        # With DEBUG_SAVEALL, no additional message should get printed
        # (because gc.garbage also contains normally reclaimable cyclic
        # references, oraz its elements get printed at runtime anyway).
        stderr = run_command(code % "gc.DEBUG_SAVEALL")
        self.assertNotIn(b"uncollectable objects at shutdown", stderr)

    def test_gc_main_module_at_shutdown(self):
        # Create a reference cycle through the __main__ module oraz check
        # it gets collected at interpreter shutdown.
        code = """jeżeli 1:
            zaimportuj weakref
            klasa C:
                def __del__(self):
                    print('__del__ called')
            l = [C()]
            l.append(l)
            """
        rc, out, err = assert_python_ok('-c', code)
        self.assertEqual(out.strip(), b'__del__ called')

    def test_gc_ordinary_module_at_shutdown(self):
        # Same jako above, but przy a non-__main__ module.
        przy temp_dir() jako script_dir:
            module = """jeżeli 1:
                zaimportuj weakref
                klasa C:
                    def __del__(self):
                        print('__del__ called')
                l = [C()]
                l.append(l)
                """
            code = """jeżeli 1:
                zaimportuj sys
                sys.path.insert(0, %r)
                zaimportuj gctest
                """ % (script_dir,)
            make_script(script_dir, 'gctest', module)
            rc, out, err = assert_python_ok('-c', code)
            self.assertEqual(out.strip(), b'__del__ called')

    def test_get_stats(self):
        stats = gc.get_stats()
        self.assertEqual(len(stats), 3)
        dla st w stats:
            self.assertIsInstance(st, dict)
            self.assertEqual(set(st),
                             {"collected", "collections", "uncollectable"})
            self.assertGreaterEqual(st["collected"], 0)
            self.assertGreaterEqual(st["collections"], 0)
            self.assertGreaterEqual(st["uncollectable"], 0)
        # Check that collection counts are incremented correctly
        jeżeli gc.isenabled():
            self.addCleanup(gc.enable)
            gc.disable()
        old = gc.get_stats()
        gc.collect(0)
        new = gc.get_stats()
        self.assertEqual(new[0]["collections"], old[0]["collections"] + 1)
        self.assertEqual(new[1]["collections"], old[1]["collections"])
        self.assertEqual(new[2]["collections"], old[2]["collections"])
        gc.collect(2)
        new = gc.get_stats()
        self.assertEqual(new[0]["collections"], old[0]["collections"] + 1)
        self.assertEqual(new[1]["collections"], old[1]["collections"])
        self.assertEqual(new[2]["collections"], old[2]["collections"] + 1)


klasa GCCallbackTests(unittest.TestCase):
    def setUp(self):
        # Save gc state oraz disable it.
        self.enabled = gc.isenabled()
        gc.disable()
        self.debug = gc.get_debug()
        gc.set_debug(0)
        gc.callbacks.append(self.cb1)
        gc.callbacks.append(self.cb2)
        self.othergarbage = []

    def tearDown(self):
        # Restore gc state
        usuń self.visit
        gc.callbacks.remove(self.cb1)
        gc.callbacks.remove(self.cb2)
        gc.set_debug(self.debug)
        jeżeli self.enabled:
            gc.enable()
        # destroy any uncollectables
        gc.collect()
        dla obj w gc.garbage:
            jeżeli isinstance(obj, Uncollectable):
                obj.partner = Nic
        usuń gc.garbage[:]
        usuń self.othergarbage
        gc.collect()

    def preclean(self):
        # Remove all fluff z the system.  Invoke this function
        # manually rather than through self.setUp() dla maximum
        # safety.
        self.visit = []
        gc.collect()
        garbage, gc.garbage[:] = gc.garbage[:], []
        self.othergarbage.append(garbage)
        self.visit = []

    def cb1(self, phase, info):
        self.visit.append((1, phase, dict(info)))

    def cb2(self, phase, info):
        self.visit.append((2, phase, dict(info)))
        jeżeli phase == "stop" oraz hasattr(self, "cleanup"):
            # Clean Uncollectable z garbage
            uc = [e dla e w gc.garbage jeżeli isinstance(e, Uncollectable)]
            gc.garbage[:] = [e dla e w gc.garbage
                             jeżeli nie isinstance(e, Uncollectable)]
            dla e w uc:
                e.partner = Nic

    def test_collect(self):
        self.preclean()
        gc.collect()
        # Algorithmically verify the contents of self.visit
        # because it jest long oraz tortuous.

        # Count the number of visits to each callback
        n = [v[0] dla v w self.visit]
        n1 = [i dla i w n jeżeli i == 1]
        n2 = [i dla i w n jeżeli i == 2]
        self.assertEqual(n1, [1]*2)
        self.assertEqual(n2, [2]*2)

        # Count that we got the right number of start oraz stop callbacks.
        n = [v[1] dla v w self.visit]
        n1 = [i dla i w n jeżeli i == "start"]
        n2 = [i dla i w n jeżeli i == "stop"]
        self.assertEqual(n1, ["start"]*2)
        self.assertEqual(n2, ["stop"]*2)

        # Check that we got the right info dict dla all callbacks
        dla v w self.visit:
            info = v[2]
            self.assertPrawda("generation" w info)
            self.assertPrawda("collected" w info)
            self.assertPrawda("uncollectable" w info)

    def test_collect_generation(self):
        self.preclean()
        gc.collect(2)
        dla v w self.visit:
            info = v[2]
            self.assertEqual(info["generation"], 2)

    @cpython_only
    def test_collect_garbage(self):
        self.preclean()
        # Each of these cause four objects to be garbage: Two
        # Uncolectables oraz their instance dicts.
        Uncollectable()
        Uncollectable()
        C1055820(666)
        gc.collect()
        dla v w self.visit:
            jeżeli v[1] != "stop":
                kontynuuj
            info = v[2]
            self.assertEqual(info["collected"], 2)
            self.assertEqual(info["uncollectable"], 8)

        # We should now have the Uncollectables w gc.garbage
        self.assertEqual(len(gc.garbage), 4)
        dla e w gc.garbage:
            self.assertIsInstance(e, Uncollectable)

        # Now, let our callback handle the Uncollectable instances
        self.cleanup=Prawda
        self.visit = []
        gc.garbage[:] = []
        gc.collect()
        dla v w self.visit:
            jeżeli v[1] != "stop":
                kontynuuj
            info = v[2]
            self.assertEqual(info["collected"], 0)
            self.assertEqual(info["uncollectable"], 4)

        # Uncollectables should be gone
        self.assertEqual(len(gc.garbage), 0)


klasa GCTogglingTests(unittest.TestCase):
    def setUp(self):
        gc.enable()

    def tearDown(self):
        gc.disable()

    def test_bug1055820c(self):
        # Corresponds to temp2c.py w the bug report.  This jest pretty
        # elaborate.

        c0 = C1055820(0)
        # Move c0 into generation 2.
        gc.collect()

        c1 = C1055820(1)
        c1.keep_c0_alive = c0
        usuń c0.loop # now only c1 keeps c0 alive

        c2 = C1055820(2)
        c2wr = weakref.ref(c2) # no callback!

        ouch = []
        def callback(ignored):
            ouch[:] = [c2wr()]

        # The callback gets associated przy a wr on an object w generation 2.
        c0wr = weakref.ref(c0, callback)

        c0 = c1 = c2 = Nic

        # What we've set up:  c0, c1, oraz c2 are all trash now.  c0 jest w
        # generation 2.  The only thing keeping it alive jest that c1 points to
        # it. c1 oraz c2 are w generation 0, oraz are w self-loops.  There's a
        # global weakref to c2 (c2wr), but that weakref has no callback.
        # There's also a global weakref to c0 (c0wr), oraz that does have a
        # callback, oraz that callback references c2 via c2wr().
        #
        #               c0 has a wr przy callback, which references c2wr
        #               ^
        #               |
        #               |     Generation 2 above dots
        #. . . . . . . .|. . . . . . . . . . . . . . . . . . . . . . . .
        #               |     Generation 0 below dots
        #               |
        #               |
        #            ^->c1   ^->c2 has a wr but no callback
        #            |  |    |  |
        #            <--v    <--v
        #
        # So this jest the nightmare:  when generation 0 gets collected, we see
        # that c2 has a callback-free weakref, oraz c1 doesn't even have a
        # weakref.  Collecting generation 0 doesn't see c0 at all, oraz c0 jest
        # the only object that has a weakref przy a callback.  gc clears c1
        # oraz c2.  Clearing c1 has the side effect of dropping the refcount on
        # c0 to 0, so c0 goes away (despite that it's w an older generation)
        # oraz c0's wr callback triggers.  That w turn materializes a reference
        # to c2 via c2wr(), but c2 gets cleared anyway by gc.

        # We want to let gc happen "naturally", to preserve the distinction
        # between generations.
        junk = []
        i = 0
        detector = GC_Detector()
        dopóki nie detector.gc_happened:
            i += 1
            jeżeli i > 10000:
                self.fail("gc didn't happen after 10000 iterations")
            self.assertEqual(len(ouch), 0)
            junk.append([])  # this will eventually trigger gc

        self.assertEqual(len(ouch), 1)  # inaczej the callback wasn't invoked
        dla x w ouch:
            # If the callback resurrected c2, the instance would be damaged,
            # przy an empty __dict__.
            self.assertEqual(x, Nic)

    def test_bug1055820d(self):
        # Corresponds to temp2d.py w the bug report.  This jest very much like
        # test_bug1055820c, but uses a __del__ method instead of a weakref
        # callback to sneak w a resurrection of cyclic trash.

        ouch = []
        klasa D(C1055820):
            def __del__(self):
                ouch[:] = [c2wr()]

        d0 = D(0)
        # Move all the above into generation 2.
        gc.collect()

        c1 = C1055820(1)
        c1.keep_d0_alive = d0
        usuń d0.loop # now only c1 keeps d0 alive

        c2 = C1055820(2)
        c2wr = weakref.ref(c2) # no callback!

        d0 = c1 = c2 = Nic

        # What we've set up:  d0, c1, oraz c2 are all trash now.  d0 jest w
        # generation 2.  The only thing keeping it alive jest that c1 points to
        # it.  c1 oraz c2 are w generation 0, oraz are w self-loops.  There's
        # a global weakref to c2 (c2wr), but that weakref has no callback.
        # There are no other weakrefs.
        #
        #               d0 has a __del__ method that references c2wr
        #               ^
        #               |
        #               |     Generation 2 above dots
        #. . . . . . . .|. . . . . . . . . . . . . . . . . . . . . . . .
        #               |     Generation 0 below dots
        #               |
        #               |
        #            ^->c1   ^->c2 has a wr but no callback
        #            |  |    |  |
        #            <--v    <--v
        #
        # So this jest the nightmare:  when generation 0 gets collected, we see
        # that c2 has a callback-free weakref, oraz c1 doesn't even have a
        # weakref.  Collecting generation 0 doesn't see d0 at all.  gc clears
        # c1 oraz c2.  Clearing c1 has the side effect of dropping the refcount
        # on d0 to 0, so d0 goes away (despite that it's w an older
        # generation) oraz d0's __del__ triggers.  That w turn materializes
        # a reference to c2 via c2wr(), but c2 gets cleared anyway by gc.

        # We want to let gc happen "naturally", to preserve the distinction
        # between generations.
        detector = GC_Detector()
        junk = []
        i = 0
        dopóki nie detector.gc_happened:
            i += 1
            jeżeli i > 10000:
                self.fail("gc didn't happen after 10000 iterations")
            self.assertEqual(len(ouch), 0)
            junk.append([])  # this will eventually trigger gc

        self.assertEqual(len(ouch), 1)  # inaczej __del__ wasn't invoked
        dla x w ouch:
            # If __del__ resurrected c2, the instance would be damaged, przy an
            # empty __dict__.
            self.assertEqual(x, Nic)

def test_main():
    enabled = gc.isenabled()
    gc.disable()
    assert nie gc.isenabled()
    debug = gc.get_debug()
    gc.set_debug(debug & ~gc.DEBUG_LEAK) # this test jest supposed to leak

    spróbuj:
        gc.collect() # Delete 2nd generation garbage
        run_unittest(GCTests, GCTogglingTests, GCCallbackTests)
    w_końcu:
        gc.set_debug(debug)
        # test gc.enable() even jeżeli GC jest disabled by default
        jeżeli verbose:
            print("restoring automatic collection")
        # make sure to always test gc.enable()
        gc.enable()
        assert gc.isenabled()
        jeżeli nie enabled:
            gc.disable()

jeżeli __name__ == "__main__":
    test_main()
