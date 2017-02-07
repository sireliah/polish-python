"""Unit tests dla the copy module."""

zaimportuj copy
zaimportuj copyreg
zaimportuj weakref
zaimportuj abc
z operator zaimportuj le, lt, ge, gt, eq, ne

zaimportuj unittest

order_comparisons = le, lt, ge, gt
equality_comparisons = eq, ne
comparisons = order_comparisons + equality_comparisons

klasa TestCopy(unittest.TestCase):

    # Attempt full line coverage of copy.py z top to bottom

    def test_exceptions(self):
        self.assertIs(copy.Error, copy.error)
        self.assertPrawda(issubclass(copy.Error, Exception))

    # The copy() method

    def test_copy_basic(self):
        x = 42
        y = copy.copy(x)
        self.assertEqual(x, y)

    def test_copy_copy(self):
        klasa C(object):
            def __init__(self, foo):
                self.foo = foo
            def __copy__(self):
                zwróć C(self.foo)
        x = C(42)
        y = copy.copy(x)
        self.assertEqual(y.__class__, x.__class__)
        self.assertEqual(y.foo, x.foo)

    def test_copy_registry(self):
        klasa C(object):
            def __new__(cls, foo):
                obj = object.__new__(cls)
                obj.foo = foo
                zwróć obj
        def pickle_C(obj):
            zwróć (C, (obj.foo,))
        x = C(42)
        self.assertRaises(TypeError, copy.copy, x)
        copyreg.pickle(C, pickle_C, C)
        y = copy.copy(x)

    def test_copy_reduce_ex(self):
        klasa C(object):
            def __reduce_ex__(self, proto):
                c.append(1)
                zwróć ""
            def __reduce__(self):
                self.fail("shouldn't call this")
        c = []
        x = C()
        y = copy.copy(x)
        self.assertIs(y, x)
        self.assertEqual(c, [1])

    def test_copy_reduce(self):
        klasa C(object):
            def __reduce__(self):
                c.append(1)
                zwróć ""
        c = []
        x = C()
        y = copy.copy(x)
        self.assertIs(y, x)
        self.assertEqual(c, [1])

    def test_copy_cant(self):
        klasa C(object):
            def __getattribute__(self, name):
                jeżeli name.startswith("__reduce"):
                    podnieś AttributeError(name)
                zwróć object.__getattribute__(self, name)
        x = C()
        self.assertRaises(copy.Error, copy.copy, x)

    # Type-specific _copy_xxx() methods

    def test_copy_atomic(self):
        klasa Classic:
            dalej
        klasa NewStyle(object):
            dalej
        def f():
            dalej
        klasa WithMetaclass(metaclass=abc.ABCMeta):
            dalej
        tests = [Nic, 42, 2**100, 3.14, Prawda, Nieprawda, 1j,
                 "hello", "hello\u1234", f.__code__,
                 b"world", bytes(range(256)),
                 NewStyle, range(10), Classic, max, WithMetaclass]
        dla x w tests:
            self.assertIs(copy.copy(x), x)

    def test_copy_list(self):
        x = [1, 2, 3]
        self.assertEqual(copy.copy(x), x)

    def test_copy_tuple(self):
        x = (1, 2, 3)
        self.assertEqual(copy.copy(x), x)

    def test_copy_dict(self):
        x = {"foo": 1, "bar": 2}
        self.assertEqual(copy.copy(x), x)

    def test_copy_inst_vanilla(self):
        klasa C:
            def __init__(self, foo):
                self.foo = foo
            def __eq__(self, other):
                zwróć self.foo == other.foo
        x = C(42)
        self.assertEqual(copy.copy(x), x)

    def test_copy_inst_copy(self):
        klasa C:
            def __init__(self, foo):
                self.foo = foo
            def __copy__(self):
                zwróć C(self.foo)
            def __eq__(self, other):
                zwróć self.foo == other.foo
        x = C(42)
        self.assertEqual(copy.copy(x), x)

    def test_copy_inst_getinitargs(self):
        klasa C:
            def __init__(self, foo):
                self.foo = foo
            def __getinitargs__(self):
                zwróć (self.foo,)
            def __eq__(self, other):
                zwróć self.foo == other.foo
        x = C(42)
        self.assertEqual(copy.copy(x), x)

    def test_copy_inst_getnewargs(self):
        klasa C(int):
            def __new__(cls, foo):
                self = int.__new__(cls)
                self.foo = foo
                zwróć self
            def __getnewargs__(self):
                zwróć self.foo,
            def __eq__(self, other):
                zwróć self.foo == other.foo
        x = C(42)
        y = copy.copy(x)
        self.assertIsInstance(y, C)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertEqual(y.foo, x.foo)

    def test_copy_inst_getnewargs_ex(self):
        klasa C(int):
            def __new__(cls, *, foo):
                self = int.__new__(cls)
                self.foo = foo
                zwróć self
            def __getnewargs_ex__(self):
                zwróć (), {'foo': self.foo}
            def __eq__(self, other):
                zwróć self.foo == other.foo
        x = C(foo=42)
        y = copy.copy(x)
        self.assertIsInstance(y, C)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertEqual(y.foo, x.foo)

    def test_copy_inst_getstate(self):
        klasa C:
            def __init__(self, foo):
                self.foo = foo
            def __getstate__(self):
                zwróć {"foo": self.foo}
            def __eq__(self, other):
                zwróć self.foo == other.foo
        x = C(42)
        self.assertEqual(copy.copy(x), x)

    def test_copy_inst_setstate(self):
        klasa C:
            def __init__(self, foo):
                self.foo = foo
            def __setstate__(self, state):
                self.foo = state["foo"]
            def __eq__(self, other):
                zwróć self.foo == other.foo
        x = C(42)
        self.assertEqual(copy.copy(x), x)

    def test_copy_inst_getstate_setstate(self):
        klasa C:
            def __init__(self, foo):
                self.foo = foo
            def __getstate__(self):
                zwróć self.foo
            def __setstate__(self, state):
                self.foo = state
            def __eq__(self, other):
                zwróć self.foo == other.foo
        x = C(42)
        self.assertEqual(copy.copy(x), x)

    # The deepcopy() method

    def test_deepcopy_basic(self):
        x = 42
        y = copy.deepcopy(x)
        self.assertEqual(y, x)

    def test_deepcopy_memo(self):
        # Tests of reflexive objects are under type-specific sections below.
        # This tests only repetitions of objects.
        x = []
        x = [x, x]
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertIsNot(y[0], x[0])
        self.assertIs(y[0], y[1])

    def test_deepcopy_issubclass(self):
        # XXX Note: there's no way to test the TypeError coming out of
        # issubclass() -- this can only happen when an extension
        # module defines a "type" that doesn't formally inherit from
        # type.
        klasa Meta(type):
            dalej
        klasa C(metaclass=Meta):
            dalej
        self.assertEqual(copy.deepcopy(C), C)

    def test_deepcopy_deepcopy(self):
        klasa C(object):
            def __init__(self, foo):
                self.foo = foo
            def __deepcopy__(self, memo=Nic):
                zwróć C(self.foo)
        x = C(42)
        y = copy.deepcopy(x)
        self.assertEqual(y.__class__, x.__class__)
        self.assertEqual(y.foo, x.foo)

    def test_deepcopy_registry(self):
        klasa C(object):
            def __new__(cls, foo):
                obj = object.__new__(cls)
                obj.foo = foo
                zwróć obj
        def pickle_C(obj):
            zwróć (C, (obj.foo,))
        x = C(42)
        self.assertRaises(TypeError, copy.deepcopy, x)
        copyreg.pickle(C, pickle_C, C)
        y = copy.deepcopy(x)

    def test_deepcopy_reduce_ex(self):
        klasa C(object):
            def __reduce_ex__(self, proto):
                c.append(1)
                zwróć ""
            def __reduce__(self):
                self.fail("shouldn't call this")
        c = []
        x = C()
        y = copy.deepcopy(x)
        self.assertIs(y, x)
        self.assertEqual(c, [1])

    def test_deepcopy_reduce(self):
        klasa C(object):
            def __reduce__(self):
                c.append(1)
                zwróć ""
        c = []
        x = C()
        y = copy.deepcopy(x)
        self.assertIs(y, x)
        self.assertEqual(c, [1])

    def test_deepcopy_cant(self):
        klasa C(object):
            def __getattribute__(self, name):
                jeżeli name.startswith("__reduce"):
                    podnieś AttributeError(name)
                zwróć object.__getattribute__(self, name)
        x = C()
        self.assertRaises(copy.Error, copy.deepcopy, x)

    # Type-specific _deepcopy_xxx() methods

    def test_deepcopy_atomic(self):
        klasa Classic:
            dalej
        klasa NewStyle(object):
            dalej
        def f():
            dalej
        tests = [Nic, 42, 2**100, 3.14, Prawda, Nieprawda, 1j,
                 "hello", "hello\u1234", f.__code__,
                 NewStyle, range(10), Classic, max]
        dla x w tests:
            self.assertIs(copy.deepcopy(x), x)

    def test_deepcopy_list(self):
        x = [[1, 2], 3]
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(x, y)
        self.assertIsNot(x[0], y[0])

    def test_deepcopy_reflexive_list(self):
        x = []
        x.append(x)
        y = copy.deepcopy(x)
        dla op w comparisons:
            self.assertRaises(RecursionError, op, y, x)
        self.assertIsNot(y, x)
        self.assertIs(y[0], y)
        self.assertEqual(len(y), 1)

    def test_deepcopy_empty_tuple(self):
        x = ()
        y = copy.deepcopy(x)
        self.assertIs(x, y)

    def test_deepcopy_tuple(self):
        x = ([1, 2], 3)
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(x, y)
        self.assertIsNot(x[0], y[0])

    def test_deepcopy_tuple_of_immutables(self):
        x = ((1, 2), 3)
        y = copy.deepcopy(x)
        self.assertIs(x, y)

    def test_deepcopy_reflexive_tuple(self):
        x = ([],)
        x[0].append(x)
        y = copy.deepcopy(x)
        dla op w comparisons:
            self.assertRaises(RecursionError, op, y, x)
        self.assertIsNot(y, x)
        self.assertIsNot(y[0], x[0])
        self.assertIs(y[0][0], y)

    def test_deepcopy_dict(self):
        x = {"foo": [1, 2], "bar": 3}
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(x, y)
        self.assertIsNot(x["foo"], y["foo"])

    def test_deepcopy_reflexive_dict(self):
        x = {}
        x['foo'] = x
        y = copy.deepcopy(x)
        dla op w order_comparisons:
            self.assertRaises(TypeError, op, y, x)
        dla op w equality_comparisons:
            self.assertRaises(RecursionError, op, y, x)
        self.assertIsNot(y, x)
        self.assertIs(y['foo'], y)
        self.assertEqual(len(y), 1)

    def test_deepcopy_keepalive(self):
        memo = {}
        x = []
        y = copy.deepcopy(x, memo)
        self.assertIs(memo[id(memo)][0], x)

    def test_deepcopy_dont_memo_immutable(self):
        memo = {}
        x = [1, 2, 3, 4]
        y = copy.deepcopy(x, memo)
        self.assertEqual(y, x)
        # There's the entry dla the new list, oraz the keep alive.
        self.assertEqual(len(memo), 2)

        memo = {}
        x = [(1, 2)]
        y = copy.deepcopy(x, memo)
        self.assertEqual(y, x)
        # Tuples przy immutable contents are immutable dla deepcopy.
        self.assertEqual(len(memo), 2)

    def test_deepcopy_inst_vanilla(self):
        klasa C:
            def __init__(self, foo):
                self.foo = foo
            def __eq__(self, other):
                zwróć self.foo == other.foo
        x = C([42])
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y.foo, x.foo)

    def test_deepcopy_inst_deepcopy(self):
        klasa C:
            def __init__(self, foo):
                self.foo = foo
            def __deepcopy__(self, memo):
                zwróć C(copy.deepcopy(self.foo, memo))
            def __eq__(self, other):
                zwróć self.foo == other.foo
        x = C([42])
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertIsNot(y.foo, x.foo)

    def test_deepcopy_inst_getinitargs(self):
        klasa C:
            def __init__(self, foo):
                self.foo = foo
            def __getinitargs__(self):
                zwróć (self.foo,)
            def __eq__(self, other):
                zwróć self.foo == other.foo
        x = C([42])
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertIsNot(y.foo, x.foo)

    def test_deepcopy_inst_getnewargs(self):
        klasa C(int):
            def __new__(cls, foo):
                self = int.__new__(cls)
                self.foo = foo
                zwróć self
            def __getnewargs__(self):
                zwróć self.foo,
            def __eq__(self, other):
                zwróć self.foo == other.foo
        x = C([42])
        y = copy.deepcopy(x)
        self.assertIsInstance(y, C)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertEqual(y.foo, x.foo)
        self.assertIsNot(y.foo, x.foo)

    def test_deepcopy_inst_getnewargs_ex(self):
        klasa C(int):
            def __new__(cls, *, foo):
                self = int.__new__(cls)
                self.foo = foo
                zwróć self
            def __getnewargs_ex__(self):
                zwróć (), {'foo': self.foo}
            def __eq__(self, other):
                zwróć self.foo == other.foo
        x = C(foo=[42])
        y = copy.deepcopy(x)
        self.assertIsInstance(y, C)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertEqual(y.foo, x.foo)
        self.assertIsNot(y.foo, x.foo)

    def test_deepcopy_inst_getstate(self):
        klasa C:
            def __init__(self, foo):
                self.foo = foo
            def __getstate__(self):
                zwróć {"foo": self.foo}
            def __eq__(self, other):
                zwróć self.foo == other.foo
        x = C([42])
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertIsNot(y.foo, x.foo)

    def test_deepcopy_inst_setstate(self):
        klasa C:
            def __init__(self, foo):
                self.foo = foo
            def __setstate__(self, state):
                self.foo = state["foo"]
            def __eq__(self, other):
                zwróć self.foo == other.foo
        x = C([42])
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertIsNot(y.foo, x.foo)

    def test_deepcopy_inst_getstate_setstate(self):
        klasa C:
            def __init__(self, foo):
                self.foo = foo
            def __getstate__(self):
                zwróć self.foo
            def __setstate__(self, state):
                self.foo = state
            def __eq__(self, other):
                zwróć self.foo == other.foo
        x = C([42])
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertIsNot(y.foo, x.foo)

    def test_deepcopy_reflexive_inst(self):
        klasa C:
            dalej
        x = C()
        x.foo = x
        y = copy.deepcopy(x)
        self.assertIsNot(y, x)
        self.assertIs(y.foo, y)

    # _reconstruct()

    def test_reconstruct_string(self):
        klasa C(object):
            def __reduce__(self):
                zwróć ""
        x = C()
        y = copy.copy(x)
        self.assertIs(y, x)
        y = copy.deepcopy(x)
        self.assertIs(y, x)

    def test_reconstruct_nostate(self):
        klasa C(object):
            def __reduce__(self):
                zwróć (C, ())
        x = C()
        x.foo = 42
        y = copy.copy(x)
        self.assertIs(y.__class__, x.__class__)
        y = copy.deepcopy(x)
        self.assertIs(y.__class__, x.__class__)

    def test_reconstruct_state(self):
        klasa C(object):
            def __reduce__(self):
                zwróć (C, (), self.__dict__)
            def __eq__(self, other):
                zwróć self.__dict__ == other.__dict__
        x = C()
        x.foo = [42]
        y = copy.copy(x)
        self.assertEqual(y, x)
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y.foo, x.foo)

    def test_reconstruct_state_setstate(self):
        klasa C(object):
            def __reduce__(self):
                zwróć (C, (), self.__dict__)
            def __setstate__(self, state):
                self.__dict__.update(state)
            def __eq__(self, other):
                zwróć self.__dict__ == other.__dict__
        x = C()
        x.foo = [42]
        y = copy.copy(x)
        self.assertEqual(y, x)
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y.foo, x.foo)

    def test_reconstruct_reflexive(self):
        klasa C(object):
            dalej
        x = C()
        x.foo = x
        y = copy.deepcopy(x)
        self.assertIsNot(y, x)
        self.assertIs(y.foo, y)

    # Additions dla Python 2.3 oraz pickle protocol 2

    def test_reduce_4tuple(self):
        klasa C(list):
            def __reduce__(self):
                zwróć (C, (), self.__dict__, iter(self))
            def __eq__(self, other):
                zwróć (list(self) == list(other) oraz
                        self.__dict__ == other.__dict__)
        x = C([[1, 2], 3])
        y = copy.copy(x)
        self.assertEqual(x, y)
        self.assertIsNot(x, y)
        self.assertIs(x[0], y[0])
        y = copy.deepcopy(x)
        self.assertEqual(x, y)
        self.assertIsNot(x, y)
        self.assertIsNot(x[0], y[0])

    def test_reduce_5tuple(self):
        klasa C(dict):
            def __reduce__(self):
                zwróć (C, (), self.__dict__, Nic, self.items())
            def __eq__(self, other):
                zwróć (dict(self) == dict(other) oraz
                        self.__dict__ == other.__dict__)
        x = C([("foo", [1, 2]), ("bar", 3)])
        y = copy.copy(x)
        self.assertEqual(x, y)
        self.assertIsNot(x, y)
        self.assertIs(x["foo"], y["foo"])
        y = copy.deepcopy(x)
        self.assertEqual(x, y)
        self.assertIsNot(x, y)
        self.assertIsNot(x["foo"], y["foo"])

    def test_copy_slots(self):
        klasa C(object):
            __slots__ = ["foo"]
        x = C()
        x.foo = [42]
        y = copy.copy(x)
        self.assertIs(x.foo, y.foo)

    def test_deepcopy_slots(self):
        klasa C(object):
            __slots__ = ["foo"]
        x = C()
        x.foo = [42]
        y = copy.deepcopy(x)
        self.assertEqual(x.foo, y.foo)
        self.assertIsNot(x.foo, y.foo)

    def test_deepcopy_dict_subclass(self):
        klasa C(dict):
            def __init__(self, d=Nic):
                jeżeli nie d:
                    d = {}
                self._keys = list(d.keys())
                super().__init__(d)
            def __setitem__(self, key, item):
                super().__setitem__(key, item)
                jeżeli key nie w self._keys:
                    self._keys.append(key)
        x = C(d={'foo':0})
        y = copy.deepcopy(x)
        self.assertEqual(x, y)
        self.assertEqual(x._keys, y._keys)
        self.assertIsNot(x, y)
        x['bar'] = 1
        self.assertNotEqual(x, y)
        self.assertNotEqual(x._keys, y._keys)

    def test_copy_list_subclass(self):
        klasa C(list):
            dalej
        x = C([[1, 2], 3])
        x.foo = [4, 5]
        y = copy.copy(x)
        self.assertEqual(list(x), list(y))
        self.assertEqual(x.foo, y.foo)
        self.assertIs(x[0], y[0])
        self.assertIs(x.foo, y.foo)

    def test_deepcopy_list_subclass(self):
        klasa C(list):
            dalej
        x = C([[1, 2], 3])
        x.foo = [4, 5]
        y = copy.deepcopy(x)
        self.assertEqual(list(x), list(y))
        self.assertEqual(x.foo, y.foo)
        self.assertIsNot(x[0], y[0])
        self.assertIsNot(x.foo, y.foo)

    def test_copy_tuple_subclass(self):
        klasa C(tuple):
            dalej
        x = C([1, 2, 3])
        self.assertEqual(tuple(x), (1, 2, 3))
        y = copy.copy(x)
        self.assertEqual(tuple(y), (1, 2, 3))

    def test_deepcopy_tuple_subclass(self):
        klasa C(tuple):
            dalej
        x = C([[1, 2], 3])
        self.assertEqual(tuple(x), ([1, 2], 3))
        y = copy.deepcopy(x)
        self.assertEqual(tuple(y), ([1, 2], 3))
        self.assertIsNot(x, y)
        self.assertIsNot(x[0], y[0])

    def test_getstate_exc(self):
        klasa EvilState(object):
            def __getstate__(self):
                podnieś ValueError("ain't got no stickin' state")
        self.assertRaises(ValueError, copy.copy, EvilState())

    def test_copy_function(self):
        self.assertEqual(copy.copy(global_foo), global_foo)
        def foo(x, y): zwróć x+y
        self.assertEqual(copy.copy(foo), foo)
        bar = lambda: Nic
        self.assertEqual(copy.copy(bar), bar)

    def test_deepcopy_function(self):
        self.assertEqual(copy.deepcopy(global_foo), global_foo)
        def foo(x, y): zwróć x+y
        self.assertEqual(copy.deepcopy(foo), foo)
        bar = lambda: Nic
        self.assertEqual(copy.deepcopy(bar), bar)

    def _check_weakref(self, _copy):
        klasa C(object):
            dalej
        obj = C()
        x = weakref.ref(obj)
        y = _copy(x)
        self.assertIs(y, x)
        usuń obj
        y = _copy(x)
        self.assertIs(y, x)

    def test_copy_weakref(self):
        self._check_weakref(copy.copy)

    def test_deepcopy_weakref(self):
        self._check_weakref(copy.deepcopy)

    def _check_copy_weakdict(self, _dicttype):
        klasa C(object):
            dalej
        a, b, c, d = [C() dla i w range(4)]
        u = _dicttype()
        u[a] = b
        u[c] = d
        v = copy.copy(u)
        self.assertIsNot(v, u)
        self.assertEqual(v, u)
        self.assertEqual(v[a], b)
        self.assertEqual(v[c], d)
        self.assertEqual(len(v), 2)
        usuń c, d
        self.assertEqual(len(v), 1)
        x, y = C(), C()
        # The underlying containers are decoupled
        v[x] = y
        self.assertNotIn(x, u)

    def test_copy_weakkeydict(self):
        self._check_copy_weakdict(weakref.WeakKeyDictionary)

    def test_copy_weakvaluedict(self):
        self._check_copy_weakdict(weakref.WeakValueDictionary)

    def test_deepcopy_weakkeydict(self):
        klasa C(object):
            def __init__(self, i):
                self.i = i
        a, b, c, d = [C(i) dla i w range(4)]
        u = weakref.WeakKeyDictionary()
        u[a] = b
        u[c] = d
        # Keys aren't copied, values are
        v = copy.deepcopy(u)
        self.assertNotEqual(v, u)
        self.assertEqual(len(v), 2)
        self.assertIsNot(v[a], b)
        self.assertIsNot(v[c], d)
        self.assertEqual(v[a].i, b.i)
        self.assertEqual(v[c].i, d.i)
        usuń c
        self.assertEqual(len(v), 1)

    def test_deepcopy_weakvaluedict(self):
        klasa C(object):
            def __init__(self, i):
                self.i = i
        a, b, c, d = [C(i) dla i w range(4)]
        u = weakref.WeakValueDictionary()
        u[a] = b
        u[c] = d
        # Keys are copied, values aren't
        v = copy.deepcopy(u)
        self.assertNotEqual(v, u)
        self.assertEqual(len(v), 2)
        (x, y), (z, t) = sorted(v.items(), key=lambda pair: pair[0].i)
        self.assertIsNot(x, a)
        self.assertEqual(x.i, a.i)
        self.assertIs(y, b)
        self.assertIsNot(z, c)
        self.assertEqual(z.i, c.i)
        self.assertIs(t, d)
        usuń x, y, z, t
        usuń d
        self.assertEqual(len(v), 1)

    def test_deepcopy_bound_method(self):
        klasa Foo(object):
            def m(self):
                dalej
        f = Foo()
        f.b = f.m
        g = copy.deepcopy(f)
        self.assertEqual(g.m, g.b)
        self.assertIs(g.b.__self__, g)
        g.b()


def global_foo(x, y): zwróć x+y

jeżeli __name__ == "__main__":
    unittest.main()
