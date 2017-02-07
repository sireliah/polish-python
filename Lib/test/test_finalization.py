"""
Tests dla object finalization semantics, jako outlined w PEP 442.
"""

zaimportuj contextlib
zaimportuj gc
zaimportuj unittest
zaimportuj weakref

spróbuj:
    z _testcapi zaimportuj with_tp_del
wyjąwszy ImportError:
    def with_tp_del(cls):
        klasa C(object):
            def __new__(cls, *args, **kwargs):
                podnieś TypeError('requires _testcapi.with_tp_del')
        zwróć C

z test zaimportuj support


klasa NonGCSimpleBase:
    """
    The base klasa dla all the objects under test, equipped przy various
    testing features.
    """

    survivors = []
    del_calls = []
    tp_del_calls = []
    errors = []

    _cleaning = Nieprawda

    __slots__ = ()

    @classmethod
    def _cleanup(cls):
        cls.survivors.clear()
        cls.errors.clear()
        gc.garbage.clear()
        gc.collect()
        cls.del_calls.clear()
        cls.tp_del_calls.clear()

    @classmethod
    @contextlib.contextmanager
    def test(cls):
        """
        A context manager to use around all finalization tests.
        """
        przy support.disable_gc():
            cls.del_calls.clear()
            cls.tp_del_calls.clear()
            NonGCSimpleBase._cleaning = Nieprawda
            spróbuj:
                uzyskaj
                jeżeli cls.errors:
                    podnieś cls.errors[0]
            w_końcu:
                NonGCSimpleBase._cleaning = Prawda
                cls._cleanup()

    def check_sanity(self):
        """
        Check the object jest sane (non-broken).
        """

    def __del__(self):
        """
        PEP 442 finalizer.  Record that this was called, check the
        object jest w a sane state, oraz invoke a side effect.
        """
        spróbuj:
            jeżeli nie self._cleaning:
                self.del_calls.append(id(self))
                self.check_sanity()
                self.side_effect()
        wyjąwszy Exception jako e:
            self.errors.append(e)

    def side_effect(self):
        """
        A side effect called on destruction.
        """


klasa SimpleBase(NonGCSimpleBase):

    def __init__(self):
        self.id_ = id(self)

    def check_sanity(self):
        assert self.id_ == id(self)


klasa NonGC(NonGCSimpleBase):
    __slots__ = ()

klasa NonGCResurrector(NonGCSimpleBase):
    __slots__ = ()

    def side_effect(self):
        """
        Resurrect self by storing self w a class-wide list.
        """
        self.survivors.append(self)

klasa Simple(SimpleBase):
    dalej

klasa SimpleResurrector(NonGCResurrector, SimpleBase):
    dalej


klasa TestBase:

    def setUp(self):
        self.old_garbage = gc.garbage[:]
        gc.garbage[:] = []

    def tearDown(self):
        # Nic of the tests here should put anything w gc.garbage
        spróbuj:
            self.assertEqual(gc.garbage, [])
        w_końcu:
            usuń self.old_garbage
            gc.collect()

    def assert_del_calls(self, ids):
        self.assertEqual(sorted(SimpleBase.del_calls), sorted(ids))

    def assert_tp_del_calls(self, ids):
        self.assertEqual(sorted(SimpleBase.tp_del_calls), sorted(ids))

    def assert_survivors(self, ids):
        self.assertEqual(sorted(id(x) dla x w SimpleBase.survivors), sorted(ids))

    def assert_garbage(self, ids):
        self.assertEqual(sorted(id(x) dla x w gc.garbage), sorted(ids))

    def clear_survivors(self):
        SimpleBase.survivors.clear()


klasa SimpleFinalizationTest(TestBase, unittest.TestCase):
    """
    Test finalization without refcycles.
    """

    def test_simple(self):
        przy SimpleBase.test():
            s = Simple()
            ids = [id(s)]
            wr = weakref.ref(s)
            usuń s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
            self.assertIs(wr(), Nic)
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])

    def test_simple_resurrect(self):
        przy SimpleBase.test():
            s = SimpleResurrector()
            ids = [id(s)]
            wr = weakref.ref(s)
            usuń s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors(ids)
            self.assertIsNot(wr(), Nic)
            self.clear_survivors()
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
        self.assertIs(wr(), Nic)

    def test_non_gc(self):
        przy SimpleBase.test():
            s = NonGC()
            self.assertNieprawda(gc.is_tracked(s))
            ids = [id(s)]
            usuń s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])

    def test_non_gc_resurrect(self):
        przy SimpleBase.test():
            s = NonGCResurrector()
            self.assertNieprawda(gc.is_tracked(s))
            ids = [id(s)]
            usuń s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors(ids)
            self.clear_survivors()
            gc.collect()
            self.assert_del_calls(ids * 2)
            self.assert_survivors(ids)


klasa SelfCycleBase:

    def __init__(self):
        super().__init__()
        self.ref = self

    def check_sanity(self):
        super().check_sanity()
        assert self.ref jest self

klasa SimpleSelfCycle(SelfCycleBase, Simple):
    dalej

klasa SelfCycleResurrector(SelfCycleBase, SimpleResurrector):
    dalej

klasa SuicidalSelfCycle(SelfCycleBase, Simple):

    def side_effect(self):
        """
        Explicitly przerwij the reference cycle.
        """
        self.ref = Nic


klasa SelfCycleFinalizationTest(TestBase, unittest.TestCase):
    """
    Test finalization of an object having a single cyclic reference to
    itself.
    """

    def test_simple(self):
        przy SimpleBase.test():
            s = SimpleSelfCycle()
            ids = [id(s)]
            wr = weakref.ref(s)
            usuń s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
            self.assertIs(wr(), Nic)
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])

    def test_simple_resurrect(self):
        # Test that __del__ can resurrect the object being finalized.
        przy SimpleBase.test():
            s = SelfCycleResurrector()
            ids = [id(s)]
            wr = weakref.ref(s)
            usuń s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors(ids)
            # XXX jest this desirable?
            self.assertIs(wr(), Nic)
            # When trying to destroy the object a second time, __del__
            # isn't called anymore (and the object isn't resurrected).
            self.clear_survivors()
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
            self.assertIs(wr(), Nic)

    def test_simple_suicide(self):
        # Test the GC jest able to deal przy an object that kills its last
        # reference during __del__.
        przy SimpleBase.test():
            s = SuicidalSelfCycle()
            ids = [id(s)]
            wr = weakref.ref(s)
            usuń s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
            self.assertIs(wr(), Nic)
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
            self.assertIs(wr(), Nic)


klasa ChainedBase:

    def chain(self, left):
        self.suicided = Nieprawda
        self.left = left
        left.right = self

    def check_sanity(self):
        super().check_sanity()
        jeżeli self.suicided:
            assert self.left jest Nic
            assert self.right jest Nic
        inaczej:
            left = self.left
            jeżeli left.suicided:
                assert left.right jest Nic
            inaczej:
                assert left.right jest self
            right = self.right
            jeżeli right.suicided:
                assert right.left jest Nic
            inaczej:
                assert right.left jest self

klasa SimpleChained(ChainedBase, Simple):
    dalej

klasa ChainedResurrector(ChainedBase, SimpleResurrector):
    dalej

klasa SuicidalChained(ChainedBase, Simple):

    def side_effect(self):
        """
        Explicitly przerwij the reference cycle.
        """
        self.suicided = Prawda
        self.left = Nic
        self.right = Nic


klasa CycleChainFinalizationTest(TestBase, unittest.TestCase):
    """
    Test finalization of a cyclic chain.  These tests are similar w
    spirit to the self-cycle tests above, but the collectable object
    graph isn't trivial anymore.
    """

    def build_chain(self, classes):
        nodes = [cls() dla cls w classes]
        dla i w range(len(nodes)):
            nodes[i].chain(nodes[i-1])
        zwróć nodes

    def check_non_resurrecting_chain(self, classes):
        N = len(classes)
        przy SimpleBase.test():
            nodes = self.build_chain(classes)
            ids = [id(s) dla s w nodes]
            wrs = [weakref.ref(s) dla s w nodes]
            usuń nodes
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
            self.assertEqual([wr() dla wr w wrs], [Nic] * N)
            gc.collect()
            self.assert_del_calls(ids)

    def check_resurrecting_chain(self, classes):
        N = len(classes)
        przy SimpleBase.test():
            nodes = self.build_chain(classes)
            N = len(nodes)
            ids = [id(s) dla s w nodes]
            survivor_ids = [id(s) dla s w nodes jeżeli isinstance(s, SimpleResurrector)]
            wrs = [weakref.ref(s) dla s w nodes]
            usuń nodes
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors(survivor_ids)
            # XXX desirable?
            self.assertEqual([wr() dla wr w wrs], [Nic] * N)
            self.clear_survivors()
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])

    def test_homogenous(self):
        self.check_non_resurrecting_chain([SimpleChained] * 3)

    def test_homogenous_resurrect(self):
        self.check_resurrecting_chain([ChainedResurrector] * 3)

    def test_homogenous_suicidal(self):
        self.check_non_resurrecting_chain([SuicidalChained] * 3)

    def test_heterogenous_suicidal_one(self):
        self.check_non_resurrecting_chain([SuicidalChained, SimpleChained] * 2)

    def test_heterogenous_suicidal_two(self):
        self.check_non_resurrecting_chain(
            [SuicidalChained] * 2 + [SimpleChained] * 2)

    def test_heterogenous_resurrect_one(self):
        self.check_resurrecting_chain([ChainedResurrector, SimpleChained] * 2)

    def test_heterogenous_resurrect_two(self):
        self.check_resurrecting_chain(
            [ChainedResurrector, SimpleChained, SuicidalChained] * 2)

    def test_heterogenous_resurrect_three(self):
        self.check_resurrecting_chain(
            [ChainedResurrector] * 2 + [SimpleChained] * 2 + [SuicidalChained] * 2)


# NOTE: the tp_usuń slot isn't automatically inherited, so we have to call
# with_tp_del() dla each instantiated class.

klasa LegacyBase(SimpleBase):

    def __del__(self):
        spróbuj:
            # Do nie invoke side_effect here, since we are now exercising
            # the tp_usuń slot.
            jeżeli nie self._cleaning:
                self.del_calls.append(id(self))
                self.check_sanity()
        wyjąwszy Exception jako e:
            self.errors.append(e)

    def __tp_del__(self):
        """
        Legacy (pre-PEP 442) finalizer, mapped to a tp_usuń slot.
        """
        spróbuj:
            jeżeli nie self._cleaning:
                self.tp_del_calls.append(id(self))
                self.check_sanity()
                self.side_effect()
        wyjąwszy Exception jako e:
            self.errors.append(e)

@with_tp_del
klasa Legacy(LegacyBase):
    dalej

@with_tp_del
klasa LegacyResurrector(LegacyBase):

    def side_effect(self):
        """
        Resurrect self by storing self w a class-wide list.
        """
        self.survivors.append(self)

@with_tp_del
klasa LegacySelfCycle(SelfCycleBase, LegacyBase):
    dalej


@support.cpython_only
klasa LegacyFinalizationTest(TestBase, unittest.TestCase):
    """
    Test finalization of objects przy a tp_del.
    """

    def tearDown(self):
        # These tests need to clean up a bit more, since they create
        # uncollectable objects.
        gc.garbage.clear()
        gc.collect()
        super().tearDown()

    def test_legacy(self):
        przy SimpleBase.test():
            s = Legacy()
            ids = [id(s)]
            wr = weakref.ref(s)
            usuń s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_tp_del_calls(ids)
            self.assert_survivors([])
            self.assertIs(wr(), Nic)
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_tp_del_calls(ids)

    def test_legacy_resurrect(self):
        przy SimpleBase.test():
            s = LegacyResurrector()
            ids = [id(s)]
            wr = weakref.ref(s)
            usuń s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_tp_del_calls(ids)
            self.assert_survivors(ids)
            # weakrefs are cleared before tp_usuń jest called.
            self.assertIs(wr(), Nic)
            self.clear_survivors()
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_tp_del_calls(ids * 2)
            self.assert_survivors(ids)
        self.assertIs(wr(), Nic)

    def test_legacy_self_cycle(self):
        # Self-cycles przy legacy finalizers end up w gc.garbage.
        przy SimpleBase.test():
            s = LegacySelfCycle()
            ids = [id(s)]
            wr = weakref.ref(s)
            usuń s
            gc.collect()
            self.assert_del_calls([])
            self.assert_tp_del_calls([])
            self.assert_survivors([])
            self.assert_garbage(ids)
            self.assertIsNot(wr(), Nic)
            # Break the cycle to allow collection
            gc.garbage[0].ref = Nic
        self.assert_garbage([])
        self.assertIs(wr(), Nic)


jeżeli __name__ == "__main__":
    unittest.main()
