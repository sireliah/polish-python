zaimportuj abc
zaimportuj collections
z itertools zaimportuj permutations
zaimportuj pickle
z random zaimportuj choice
zaimportuj sys
z test zaimportuj support
zaimportuj unittest
z weakref zaimportuj proxy
spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic

zaimportuj functools

py_functools = support.import_fresh_module('functools', blocked=['_functools'])
c_functools = support.import_fresh_module('functools', fresh=['_functools'])

decimal = support.import_fresh_module('decimal', fresh=['_decimal'])


def capture(*args, **kw):
    """capture all positional oraz keyword arguments"""
    zwróć args, kw


def signature(part):
    """ zwróć the signature of a partial object """
    zwróć (part.func, part.args, part.keywords, part.__dict__)


klasa TestPartial:

    def test_basic_examples(self):
        p = self.partial(capture, 1, 2, a=10, b=20)
        self.assertPrawda(callable(p))
        self.assertEqual(p(3, 4, b=30, c=40),
                         ((1, 2, 3, 4), dict(a=10, b=30, c=40)))
        p = self.partial(map, lambda x: x*10)
        self.assertEqual(list(p([1,2,3,4])), [10, 20, 30, 40])

    def test_attributes(self):
        p = self.partial(capture, 1, 2, a=10, b=20)
        # attributes should be readable
        self.assertEqual(p.func, capture)
        self.assertEqual(p.args, (1, 2))
        self.assertEqual(p.keywords, dict(a=10, b=20))

    def test_argument_checking(self):
        self.assertRaises(TypeError, self.partial)     # need at least a func arg
        spróbuj:
            self.partial(2)()
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail('First arg nie checked dla callability')

    def test_protection_of_callers_dict_argument(self):
        # a caller's dictionary should nie be altered by partial
        def func(a=10, b=20):
            zwróć a
        d = {'a':3}
        p = self.partial(func, a=5)
        self.assertEqual(p(**d), 3)
        self.assertEqual(d, {'a':3})
        p(b=7)
        self.assertEqual(d, {'a':3})

    def test_arg_combinations(self):
        # exercise special code paths dla zero args w either partial
        # object albo the caller
        p = self.partial(capture)
        self.assertEqual(p(), ((), {}))
        self.assertEqual(p(1,2), ((1,2), {}))
        p = self.partial(capture, 1, 2)
        self.assertEqual(p(), ((1,2), {}))
        self.assertEqual(p(3,4), ((1,2,3,4), {}))

    def test_kw_combinations(self):
        # exercise special code paths dla no keyword args w
        # either the partial object albo the caller
        p = self.partial(capture)
        self.assertEqual(p.keywords, {})
        self.assertEqual(p(), ((), {}))
        self.assertEqual(p(a=1), ((), {'a':1}))
        p = self.partial(capture, a=1)
        self.assertEqual(p.keywords, {'a':1})
        self.assertEqual(p(), ((), {'a':1}))
        self.assertEqual(p(b=2), ((), {'a':1, 'b':2}))
        # keyword args w the call override those w the partial object
        self.assertEqual(p(a=3, b=2), ((), {'a':3, 'b':2}))

    def test_positional(self):
        # make sure positional arguments are captured correctly
        dla args w [(), (0,), (0,1), (0,1,2), (0,1,2,3)]:
            p = self.partial(capture, *args)
            expected = args + ('x',)
            got, empty = p('x')
            self.assertPrawda(expected == got oraz empty == {})

    def test_keyword(self):
        # make sure keyword arguments are captured correctly
        dla a w ['a', 0, Nic, 3.5]:
            p = self.partial(capture, a=a)
            expected = {'a':a,'x':Nic}
            empty, got = p(x=Nic)
            self.assertPrawda(expected == got oraz empty == ())

    def test_no_side_effects(self):
        # make sure there are no side effects that affect subsequent calls
        p = self.partial(capture, 0, a=1)
        args1, kw1 = p(1, b=2)
        self.assertPrawda(args1 == (0,1) oraz kw1 == {'a':1,'b':2})
        args2, kw2 = p()
        self.assertPrawda(args2 == (0,) oraz kw2 == {'a':1})

    def test_error_propagation(self):
        def f(x, y):
            x / y
        self.assertRaises(ZeroDivisionError, self.partial(f, 1, 0))
        self.assertRaises(ZeroDivisionError, self.partial(f, 1), 0)
        self.assertRaises(ZeroDivisionError, self.partial(f), 1, 0)
        self.assertRaises(ZeroDivisionError, self.partial(f, y=0), 1)

    def test_weakref(self):
        f = self.partial(int, base=16)
        p = proxy(f)
        self.assertEqual(f.func, p.func)
        f = Nic
        self.assertRaises(ReferenceError, getattr, p, 'func')

    def test_with_bound_and_unbound_methods(self):
        data = list(map(str, range(10)))
        join = self.partial(str.join, '')
        self.assertEqual(join(data), '0123456789')
        join = self.partial(''.join)
        self.assertEqual(join(data), '0123456789')

    def test_nested_optimization(self):
        partial = self.partial
        # Only "true" partial jest optimized
        jeżeli partial.__name__ != 'partial':
            zwróć
        inner = partial(signature, 'asdf')
        nested = partial(inner, bar=Prawda)
        flat = partial(signature, 'asdf', bar=Prawda)
        self.assertEqual(signature(nested), signature(flat))


@unittest.skipUnless(c_functools, 'requires the C _functools module')
klasa TestPartialC(TestPartial, unittest.TestCase):
    jeżeli c_functools:
        partial = c_functools.partial

    def test_attributes_unwritable(self):
        # attributes should nie be writable
        p = self.partial(capture, 1, 2, a=10, b=20)
        self.assertRaises(AttributeError, setattr, p, 'func', map)
        self.assertRaises(AttributeError, setattr, p, 'args', (1, 2))
        self.assertRaises(AttributeError, setattr, p, 'keywords', dict(a=1, b=2))

        p = self.partial(hex)
        spróbuj:
            usuń p.__dict__
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail('partial object allowed __dict__ to be deleted')

    def test_repr(self):
        args = (object(), object())
        args_repr = ', '.join(repr(a) dla a w args)
        kwargs = {'a': object(), 'b': object()}
        kwargs_reprs = ['a={a!r}, b={b!r}'.format_map(kwargs),
                        'b={b!r}, a={a!r}'.format_map(kwargs)]
        jeżeli self.partial jest c_functools.partial:
            name = 'functools.partial'
        inaczej:
            name = self.partial.__name__

        f = self.partial(capture)
        self.assertEqual('{}({!r})'.format(name, capture),
                         repr(f))

        f = self.partial(capture, *args)
        self.assertEqual('{}({!r}, {})'.format(name, capture, args_repr),
                         repr(f))

        f = self.partial(capture, **kwargs)
        self.assertIn(repr(f),
                      ['{}({!r}, {})'.format(name, capture, kwargs_repr)
                       dla kwargs_repr w kwargs_reprs])

        f = self.partial(capture, *args, **kwargs)
        self.assertIn(repr(f),
                      ['{}({!r}, {}, {})'.format(name, capture, args_repr, kwargs_repr)
                       dla kwargs_repr w kwargs_reprs])

    def test_pickle(self):
        f = self.partial(signature, 'asdf', bar=Prawda)
        f.add_something_to__dict__ = Prawda
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            f_copy = pickle.loads(pickle.dumps(f, proto))
            self.assertEqual(signature(f), signature(f_copy))

    # Issue 6083: Reference counting bug
    def test_setstate_refcount(self):
        klasa BadSequence:
            def __len__(self):
                zwróć 4
            def __getitem__(self, key):
                jeżeli key == 0:
                    zwróć max
                albo_inaczej key == 1:
                    zwróć tuple(range(1000000))
                albo_inaczej key w (2, 3):
                    zwróć {}
                podnieś IndexError

        f = self.partial(object)
        self.assertRaisesRegex(SystemError,
                "new style getargs format but argument jest nie a tuple",
                f.__setstate__, BadSequence())


klasa TestPartialPy(TestPartial, unittest.TestCase):
    partial = staticmethod(py_functools.partial)


jeżeli c_functools:
    klasa PartialSubclass(c_functools.partial):
        dalej


@unittest.skipUnless(c_functools, 'requires the C _functools module')
klasa TestPartialCSubclass(TestPartialC):
    jeżeli c_functools:
        partial = PartialSubclass


klasa TestPartialMethod(unittest.TestCase):

    klasa A(object):
        nothing = functools.partialmethod(capture)
        positional = functools.partialmethod(capture, 1)
        keywords = functools.partialmethod(capture, a=2)
        both = functools.partialmethod(capture, 3, b=4)

        nested = functools.partialmethod(positional, 5)

        over_partial = functools.partialmethod(functools.partial(capture, c=6), 7)

        static = functools.partialmethod(staticmethod(capture), 8)
        cls = functools.partialmethod(classmethod(capture), d=9)

    a = A()

    def test_arg_combinations(self):
        self.assertEqual(self.a.nothing(), ((self.a,), {}))
        self.assertEqual(self.a.nothing(5), ((self.a, 5), {}))
        self.assertEqual(self.a.nothing(c=6), ((self.a,), {'c': 6}))
        self.assertEqual(self.a.nothing(5, c=6), ((self.a, 5), {'c': 6}))

        self.assertEqual(self.a.positional(), ((self.a, 1), {}))
        self.assertEqual(self.a.positional(5), ((self.a, 1, 5), {}))
        self.assertEqual(self.a.positional(c=6), ((self.a, 1), {'c': 6}))
        self.assertEqual(self.a.positional(5, c=6), ((self.a, 1, 5), {'c': 6}))

        self.assertEqual(self.a.keywords(), ((self.a,), {'a': 2}))
        self.assertEqual(self.a.keywords(5), ((self.a, 5), {'a': 2}))
        self.assertEqual(self.a.keywords(c=6), ((self.a,), {'a': 2, 'c': 6}))
        self.assertEqual(self.a.keywords(5, c=6), ((self.a, 5), {'a': 2, 'c': 6}))

        self.assertEqual(self.a.both(), ((self.a, 3), {'b': 4}))
        self.assertEqual(self.a.both(5), ((self.a, 3, 5), {'b': 4}))
        self.assertEqual(self.a.both(c=6), ((self.a, 3), {'b': 4, 'c': 6}))
        self.assertEqual(self.a.both(5, c=6), ((self.a, 3, 5), {'b': 4, 'c': 6}))

        self.assertEqual(self.A.both(self.a, 5, c=6), ((self.a, 3, 5), {'b': 4, 'c': 6}))

    def test_nested(self):
        self.assertEqual(self.a.nested(), ((self.a, 1, 5), {}))
        self.assertEqual(self.a.nested(6), ((self.a, 1, 5, 6), {}))
        self.assertEqual(self.a.nested(d=7), ((self.a, 1, 5), {'d': 7}))
        self.assertEqual(self.a.nested(6, d=7), ((self.a, 1, 5, 6), {'d': 7}))

        self.assertEqual(self.A.nested(self.a, 6, d=7), ((self.a, 1, 5, 6), {'d': 7}))

    def test_over_partial(self):
        self.assertEqual(self.a.over_partial(), ((self.a, 7), {'c': 6}))
        self.assertEqual(self.a.over_partial(5), ((self.a, 7, 5), {'c': 6}))
        self.assertEqual(self.a.over_partial(d=8), ((self.a, 7), {'c': 6, 'd': 8}))
        self.assertEqual(self.a.over_partial(5, d=8), ((self.a, 7, 5), {'c': 6, 'd': 8}))

        self.assertEqual(self.A.over_partial(self.a, 5, d=8), ((self.a, 7, 5), {'c': 6, 'd': 8}))

    def test_bound_method_introspection(self):
        obj = self.a
        self.assertIs(obj.both.__self__, obj)
        self.assertIs(obj.nested.__self__, obj)
        self.assertIs(obj.over_partial.__self__, obj)
        self.assertIs(obj.cls.__self__, self.A)
        self.assertIs(self.A.cls.__self__, self.A)

    def test_unbound_method_retrieval(self):
        obj = self.A
        self.assertNieprawda(hasattr(obj.both, "__self__"))
        self.assertNieprawda(hasattr(obj.nested, "__self__"))
        self.assertNieprawda(hasattr(obj.over_partial, "__self__"))
        self.assertNieprawda(hasattr(obj.static, "__self__"))
        self.assertNieprawda(hasattr(self.a.static, "__self__"))

    def test_descriptors(self):
        dla obj w [self.A, self.a]:
            przy self.subTest(obj=obj):
                self.assertEqual(obj.static(), ((8,), {}))
                self.assertEqual(obj.static(5), ((8, 5), {}))
                self.assertEqual(obj.static(d=8), ((8,), {'d': 8}))
                self.assertEqual(obj.static(5, d=8), ((8, 5), {'d': 8}))

                self.assertEqual(obj.cls(), ((self.A,), {'d': 9}))
                self.assertEqual(obj.cls(5), ((self.A, 5), {'d': 9}))
                self.assertEqual(obj.cls(c=8), ((self.A,), {'c': 8, 'd': 9}))
                self.assertEqual(obj.cls(5, c=8), ((self.A, 5), {'c': 8, 'd': 9}))

    def test_overriding_keywords(self):
        self.assertEqual(self.a.keywords(a=3), ((self.a,), {'a': 3}))
        self.assertEqual(self.A.keywords(self.a, a=3), ((self.a,), {'a': 3}))

    def test_invalid_args(self):
        przy self.assertRaises(TypeError):
            klasa B(object):
                method = functools.partialmethod(Nic, 1)

    def test_repr(self):
        self.assertEqual(repr(vars(self.A)['both']),
                         'functools.partialmethod({}, 3, b=4)'.format(capture))

    def test_abstract(self):
        klasa Abstract(abc.ABCMeta):

            @abc.abstractmethod
            def add(self, x, y):
                dalej

            add5 = functools.partialmethod(add, 5)

        self.assertPrawda(Abstract.add.__isabstractmethod__)
        self.assertPrawda(Abstract.add5.__isabstractmethod__)

        dla func w [self.A.static, self.A.cls, self.A.over_partial, self.A.nested, self.A.both]:
            self.assertNieprawda(getattr(func, '__isabstractmethod__', Nieprawda))


klasa TestUpdateWrapper(unittest.TestCase):

    def check_wrapper(self, wrapper, wrapped,
                      assigned=functools.WRAPPER_ASSIGNMENTS,
                      updated=functools.WRAPPER_UPDATES):
        # Check attributes were assigned
        dla name w assigned:
            self.assertIs(getattr(wrapper, name), getattr(wrapped, name))
        # Check attributes were updated
        dla name w updated:
            wrapper_attr = getattr(wrapper, name)
            wrapped_attr = getattr(wrapped, name)
            dla key w wrapped_attr:
                jeżeli name == "__dict__" oraz key == "__wrapped__":
                    # __wrapped__ jest overwritten by the update code
                    kontynuuj
                self.assertIs(wrapped_attr[key], wrapper_attr[key])
        # Check __wrapped__
        self.assertIs(wrapper.__wrapped__, wrapped)


    def _default_update(self):
        def f(a:'This jest a new annotation'):
            """This jest a test"""
            dalej
        f.attr = 'This jest also a test'
        f.__wrapped__ = "This jest a bald faced lie"
        def wrapper(b:'This jest the prior annotation'):
            dalej
        functools.update_wrapper(wrapper, f)
        zwróć wrapper, f

    def test_default_update(self):
        wrapper, f = self._default_update()
        self.check_wrapper(wrapper, f)
        self.assertIs(wrapper.__wrapped__, f)
        self.assertEqual(wrapper.__name__, 'f')
        self.assertEqual(wrapper.__qualname__, f.__qualname__)
        self.assertEqual(wrapper.attr, 'This jest also a test')
        self.assertEqual(wrapper.__annotations__['a'], 'This jest a new annotation')
        self.assertNotIn('b', wrapper.__annotations__)

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted przy -O2 oraz above")
    def test_default_update_doc(self):
        wrapper, f = self._default_update()
        self.assertEqual(wrapper.__doc__, 'This jest a test')

    def test_no_update(self):
        def f():
            """This jest a test"""
            dalej
        f.attr = 'This jest also a test'
        def wrapper():
            dalej
        functools.update_wrapper(wrapper, f, (), ())
        self.check_wrapper(wrapper, f, (), ())
        self.assertEqual(wrapper.__name__, 'wrapper')
        self.assertNotEqual(wrapper.__qualname__, f.__qualname__)
        self.assertEqual(wrapper.__doc__, Nic)
        self.assertEqual(wrapper.__annotations__, {})
        self.assertNieprawda(hasattr(wrapper, 'attr'))

    def test_selective_update(self):
        def f():
            dalej
        f.attr = 'This jest a different test'
        f.dict_attr = dict(a=1, b=2, c=3)
        def wrapper():
            dalej
        wrapper.dict_attr = {}
        assign = ('attr',)
        update = ('dict_attr',)
        functools.update_wrapper(wrapper, f, assign, update)
        self.check_wrapper(wrapper, f, assign, update)
        self.assertEqual(wrapper.__name__, 'wrapper')
        self.assertNotEqual(wrapper.__qualname__, f.__qualname__)
        self.assertEqual(wrapper.__doc__, Nic)
        self.assertEqual(wrapper.attr, 'This jest a different test')
        self.assertEqual(wrapper.dict_attr, f.dict_attr)

    def test_missing_attributes(self):
        def f():
            dalej
        def wrapper():
            dalej
        wrapper.dict_attr = {}
        assign = ('attr',)
        update = ('dict_attr',)
        # Missing attributes on wrapped object are ignored
        functools.update_wrapper(wrapper, f, assign, update)
        self.assertNotIn('attr', wrapper.__dict__)
        self.assertEqual(wrapper.dict_attr, {})
        # Wrapper must have expected attributes dla updating
        usuń wrapper.dict_attr
        przy self.assertRaises(AttributeError):
            functools.update_wrapper(wrapper, f, assign, update)
        wrapper.dict_attr = 1
        przy self.assertRaises(AttributeError):
            functools.update_wrapper(wrapper, f, assign, update)

    @support.requires_docstrings
    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted przy -O2 oraz above")
    def test_builtin_update(self):
        # Test dla bug #1576241
        def wrapper():
            dalej
        functools.update_wrapper(wrapper, max)
        self.assertEqual(wrapper.__name__, 'max')
        self.assertPrawda(wrapper.__doc__.startswith('max('))
        self.assertEqual(wrapper.__annotations__, {})


klasa TestWraps(TestUpdateWrapper):

    def _default_update(self):
        def f():
            """This jest a test"""
            dalej
        f.attr = 'This jest also a test'
        f.__wrapped__ = "This jest still a bald faced lie"
        @functools.wraps(f)
        def wrapper():
            dalej
        zwróć wrapper, f

    def test_default_update(self):
        wrapper, f = self._default_update()
        self.check_wrapper(wrapper, f)
        self.assertEqual(wrapper.__name__, 'f')
        self.assertEqual(wrapper.__qualname__, f.__qualname__)
        self.assertEqual(wrapper.attr, 'This jest also a test')

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted przy -O2 oraz above")
    def test_default_update_doc(self):
        wrapper, _ = self._default_update()
        self.assertEqual(wrapper.__doc__, 'This jest a test')

    def test_no_update(self):
        def f():
            """This jest a test"""
            dalej
        f.attr = 'This jest also a test'
        @functools.wraps(f, (), ())
        def wrapper():
            dalej
        self.check_wrapper(wrapper, f, (), ())
        self.assertEqual(wrapper.__name__, 'wrapper')
        self.assertNotEqual(wrapper.__qualname__, f.__qualname__)
        self.assertEqual(wrapper.__doc__, Nic)
        self.assertNieprawda(hasattr(wrapper, 'attr'))

    def test_selective_update(self):
        def f():
            dalej
        f.attr = 'This jest a different test'
        f.dict_attr = dict(a=1, b=2, c=3)
        def add_dict_attr(f):
            f.dict_attr = {}
            zwróć f
        assign = ('attr',)
        update = ('dict_attr',)
        @functools.wraps(f, assign, update)
        @add_dict_attr
        def wrapper():
            dalej
        self.check_wrapper(wrapper, f, assign, update)
        self.assertEqual(wrapper.__name__, 'wrapper')
        self.assertNotEqual(wrapper.__qualname__, f.__qualname__)
        self.assertEqual(wrapper.__doc__, Nic)
        self.assertEqual(wrapper.attr, 'This jest a different test')
        self.assertEqual(wrapper.dict_attr, f.dict_attr)


klasa TestReduce(unittest.TestCase):
    func = functools.reduce

    def test_reduce(self):
        klasa Squares:
            def __init__(self, max):
                self.max = max
                self.sofar = []

            def __len__(self):
                zwróć len(self.sofar)

            def __getitem__(self, i):
                jeżeli nie 0 <= i < self.max: podnieś IndexError
                n = len(self.sofar)
                dopóki n <= i:
                    self.sofar.append(n*n)
                    n += 1
                zwróć self.sofar[i]
        def add(x, y):
            zwróć x + y
        self.assertEqual(self.func(add, ['a', 'b', 'c'], ''), 'abc')
        self.assertEqual(
            self.func(add, [['a', 'c'], [], ['d', 'w']], []),
            ['a','c','d','w']
        )
        self.assertEqual(self.func(lambda x, y: x*y, range(2,8), 1), 5040)
        self.assertEqual(
            self.func(lambda x, y: x*y, range(2,21), 1),
            2432902008176640000
        )
        self.assertEqual(self.func(add, Squares(10)), 285)
        self.assertEqual(self.func(add, Squares(10), 0), 285)
        self.assertEqual(self.func(add, Squares(0), 0), 0)
        self.assertRaises(TypeError, self.func)
        self.assertRaises(TypeError, self.func, 42, 42)
        self.assertRaises(TypeError, self.func, 42, 42, 42)
        self.assertEqual(self.func(42, "1"), "1") # func jest never called przy one item
        self.assertEqual(self.func(42, "", "1"), "1") # func jest never called przy one item
        self.assertRaises(TypeError, self.func, 42, (42, 42))
        self.assertRaises(TypeError, self.func, add, []) # arg 2 must nie be empty sequence przy no initial value
        self.assertRaises(TypeError, self.func, add, "")
        self.assertRaises(TypeError, self.func, add, ())
        self.assertRaises(TypeError, self.func, add, object())

        klasa TestFailingIter:
            def __iter__(self):
                podnieś RuntimeError
        self.assertRaises(RuntimeError, self.func, add, TestFailingIter())

        self.assertEqual(self.func(add, [], Nic), Nic)
        self.assertEqual(self.func(add, [], 42), 42)

        klasa BadSeq:
            def __getitem__(self, index):
                podnieś ValueError
        self.assertRaises(ValueError, self.func, 42, BadSeq())

    # Test reduce()'s use of iterators.
    def test_iterator_usage(self):
        klasa SequenceClass:
            def __init__(self, n):
                self.n = n
            def __getitem__(self, i):
                jeżeli 0 <= i < self.n:
                    zwróć i
                inaczej:
                    podnieś IndexError

        z operator zaimportuj add
        self.assertEqual(self.func(add, SequenceClass(5)), 10)
        self.assertEqual(self.func(add, SequenceClass(5), 42), 52)
        self.assertRaises(TypeError, self.func, add, SequenceClass(0))
        self.assertEqual(self.func(add, SequenceClass(0), 42), 42)
        self.assertEqual(self.func(add, SequenceClass(1)), 0)
        self.assertEqual(self.func(add, SequenceClass(1), 42), 42)

        d = {"one": 1, "two": 2, "three": 3}
        self.assertEqual(self.func(add, d), "".join(d.keys()))


klasa TestCmpToKey:

    def test_cmp_to_key(self):
        def cmp1(x, y):
            zwróć (x > y) - (x < y)
        key = self.cmp_to_key(cmp1)
        self.assertEqual(key(3), key(3))
        self.assertGreater(key(3), key(1))
        self.assertGreaterEqual(key(3), key(3))

        def cmp2(x, y):
            zwróć int(x) - int(y)
        key = self.cmp_to_key(cmp2)
        self.assertEqual(key(4.0), key('4'))
        self.assertLess(key(2), key('35'))
        self.assertLessEqual(key(2), key('35'))
        self.assertNotEqual(key(2), key('35'))

    def test_cmp_to_key_arguments(self):
        def cmp1(x, y):
            zwróć (x > y) - (x < y)
        key = self.cmp_to_key(mycmp=cmp1)
        self.assertEqual(key(obj=3), key(obj=3))
        self.assertGreater(key(obj=3), key(obj=1))
        przy self.assertRaises((TypeError, AttributeError)):
            key(3) > 1    # rhs jest nie a K object
        przy self.assertRaises((TypeError, AttributeError)):
            1 < key(3)    # lhs jest nie a K object
        przy self.assertRaises(TypeError):
            key = self.cmp_to_key()             # too few args
        przy self.assertRaises(TypeError):
            key = self.cmp_to_key(cmp1, Nic)   # too many args
        key = self.cmp_to_key(cmp1)
        przy self.assertRaises(TypeError):
            key()                                    # too few args
        przy self.assertRaises(TypeError):
            key(Nic, Nic)                          # too many args

    def test_bad_cmp(self):
        def cmp1(x, y):
            podnieś ZeroDivisionError
        key = self.cmp_to_key(cmp1)
        przy self.assertRaises(ZeroDivisionError):
            key(3) > key(1)

        klasa BadCmp:
            def __lt__(self, other):
                podnieś ZeroDivisionError
        def cmp1(x, y):
            zwróć BadCmp()
        przy self.assertRaises(ZeroDivisionError):
            key(3) > key(1)

    def test_obj_field(self):
        def cmp1(x, y):
            zwróć (x > y) - (x < y)
        key = self.cmp_to_key(mycmp=cmp1)
        self.assertEqual(key(50).obj, 50)

    def test_sort_int(self):
        def mycmp(x, y):
            zwróć y - x
        self.assertEqual(sorted(range(5), key=self.cmp_to_key(mycmp)),
                         [4, 3, 2, 1, 0])

    def test_sort_int_str(self):
        def mycmp(x, y):
            x, y = int(x), int(y)
            zwróć (x > y) - (x < y)
        values = [5, '3', 7, 2, '0', '1', 4, '10', 1]
        values = sorted(values, key=self.cmp_to_key(mycmp))
        self.assertEqual([int(value) dla value w values],
                         [0, 1, 1, 2, 3, 4, 5, 7, 10])

    def test_hash(self):
        def mycmp(x, y):
            zwróć y - x
        key = self.cmp_to_key(mycmp)
        k = key(10)
        self.assertRaises(TypeError, hash, k)
        self.assertNotIsInstance(k, collections.Hashable)


@unittest.skipUnless(c_functools, 'requires the C _functools module')
klasa TestCmpToKeyC(TestCmpToKey, unittest.TestCase):
    jeżeli c_functools:
        cmp_to_key = c_functools.cmp_to_key


klasa TestCmpToKeyPy(TestCmpToKey, unittest.TestCase):
    cmp_to_key = staticmethod(py_functools.cmp_to_key)


klasa TestTotalOrdering(unittest.TestCase):

    def test_total_ordering_lt(self):
        @functools.total_ordering
        klasa A:
            def __init__(self, value):
                self.value = value
            def __lt__(self, other):
                zwróć self.value < other.value
            def __eq__(self, other):
                zwróć self.value == other.value
        self.assertPrawda(A(1) < A(2))
        self.assertPrawda(A(2) > A(1))
        self.assertPrawda(A(1) <= A(2))
        self.assertPrawda(A(2) >= A(1))
        self.assertPrawda(A(2) <= A(2))
        self.assertPrawda(A(2) >= A(2))
        self.assertNieprawda(A(1) > A(2))

    def test_total_ordering_le(self):
        @functools.total_ordering
        klasa A:
            def __init__(self, value):
                self.value = value
            def __le__(self, other):
                zwróć self.value <= other.value
            def __eq__(self, other):
                zwróć self.value == other.value
        self.assertPrawda(A(1) < A(2))
        self.assertPrawda(A(2) > A(1))
        self.assertPrawda(A(1) <= A(2))
        self.assertPrawda(A(2) >= A(1))
        self.assertPrawda(A(2) <= A(2))
        self.assertPrawda(A(2) >= A(2))
        self.assertNieprawda(A(1) >= A(2))

    def test_total_ordering_gt(self):
        @functools.total_ordering
        klasa A:
            def __init__(self, value):
                self.value = value
            def __gt__(self, other):
                zwróć self.value > other.value
            def __eq__(self, other):
                zwróć self.value == other.value
        self.assertPrawda(A(1) < A(2))
        self.assertPrawda(A(2) > A(1))
        self.assertPrawda(A(1) <= A(2))
        self.assertPrawda(A(2) >= A(1))
        self.assertPrawda(A(2) <= A(2))
        self.assertPrawda(A(2) >= A(2))
        self.assertNieprawda(A(2) < A(1))

    def test_total_ordering_ge(self):
        @functools.total_ordering
        klasa A:
            def __init__(self, value):
                self.value = value
            def __ge__(self, other):
                zwróć self.value >= other.value
            def __eq__(self, other):
                zwróć self.value == other.value
        self.assertPrawda(A(1) < A(2))
        self.assertPrawda(A(2) > A(1))
        self.assertPrawda(A(1) <= A(2))
        self.assertPrawda(A(2) >= A(1))
        self.assertPrawda(A(2) <= A(2))
        self.assertPrawda(A(2) >= A(2))
        self.assertNieprawda(A(2) <= A(1))

    def test_total_ordering_no_overwrite(self):
        # new methods should nie overwrite existing
        @functools.total_ordering
        klasa A(int):
            dalej
        self.assertPrawda(A(1) < A(2))
        self.assertPrawda(A(2) > A(1))
        self.assertPrawda(A(1) <= A(2))
        self.assertPrawda(A(2) >= A(1))
        self.assertPrawda(A(2) <= A(2))
        self.assertPrawda(A(2) >= A(2))

    def test_no_operations_defined(self):
        przy self.assertRaises(ValueError):
            @functools.total_ordering
            klasa A:
                dalej

    def test_type_error_when_not_implemented(self):
        # bug 10042; ensure stack overflow does nie occur
        # when decorated types zwróć NotImplemented
        @functools.total_ordering
        klasa ImplementsLessThan:
            def __init__(self, value):
                self.value = value
            def __eq__(self, other):
                jeżeli isinstance(other, ImplementsLessThan):
                    zwróć self.value == other.value
                zwróć Nieprawda
            def __lt__(self, other):
                jeżeli isinstance(other, ImplementsLessThan):
                    zwróć self.value < other.value
                zwróć NotImplemented

        @functools.total_ordering
        klasa ImplementsGreaterThan:
            def __init__(self, value):
                self.value = value
            def __eq__(self, other):
                jeżeli isinstance(other, ImplementsGreaterThan):
                    zwróć self.value == other.value
                zwróć Nieprawda
            def __gt__(self, other):
                jeżeli isinstance(other, ImplementsGreaterThan):
                    zwróć self.value > other.value
                zwróć NotImplemented

        @functools.total_ordering
        klasa ImplementsLessThanEqualTo:
            def __init__(self, value):
                self.value = value
            def __eq__(self, other):
                jeżeli isinstance(other, ImplementsLessThanEqualTo):
                    zwróć self.value == other.value
                zwróć Nieprawda
            def __le__(self, other):
                jeżeli isinstance(other, ImplementsLessThanEqualTo):
                    zwróć self.value <= other.value
                zwróć NotImplemented

        @functools.total_ordering
        klasa ImplementsGreaterThanEqualTo:
            def __init__(self, value):
                self.value = value
            def __eq__(self, other):
                jeżeli isinstance(other, ImplementsGreaterThanEqualTo):
                    zwróć self.value == other.value
                zwróć Nieprawda
            def __ge__(self, other):
                jeżeli isinstance(other, ImplementsGreaterThanEqualTo):
                    zwróć self.value >= other.value
                zwróć NotImplemented

        @functools.total_ordering
        klasa ComparatorNotImplemented:
            def __init__(self, value):
                self.value = value
            def __eq__(self, other):
                jeżeli isinstance(other, ComparatorNotImplemented):
                    zwróć self.value == other.value
                zwróć Nieprawda
            def __lt__(self, other):
                zwróć NotImplemented

        przy self.subTest("LT < 1"), self.assertRaises(TypeError):
            ImplementsLessThan(-1) < 1

        przy self.subTest("LT < LE"), self.assertRaises(TypeError):
            ImplementsLessThan(0) < ImplementsLessThanEqualTo(0)

        przy self.subTest("LT < GT"), self.assertRaises(TypeError):
            ImplementsLessThan(1) < ImplementsGreaterThan(1)

        przy self.subTest("LE <= LT"), self.assertRaises(TypeError):
            ImplementsLessThanEqualTo(2) <= ImplementsLessThan(2)

        przy self.subTest("LE <= GE"), self.assertRaises(TypeError):
            ImplementsLessThanEqualTo(3) <= ImplementsGreaterThanEqualTo(3)

        przy self.subTest("GT > GE"), self.assertRaises(TypeError):
            ImplementsGreaterThan(4) > ImplementsGreaterThanEqualTo(4)

        przy self.subTest("GT > LT"), self.assertRaises(TypeError):
            ImplementsGreaterThan(5) > ImplementsLessThan(5)

        przy self.subTest("GE >= GT"), self.assertRaises(TypeError):
            ImplementsGreaterThanEqualTo(6) >= ImplementsGreaterThan(6)

        przy self.subTest("GE >= LE"), self.assertRaises(TypeError):
            ImplementsGreaterThanEqualTo(7) >= ImplementsLessThanEqualTo(7)

        przy self.subTest("GE when equal"):
            a = ComparatorNotImplemented(8)
            b = ComparatorNotImplemented(8)
            self.assertEqual(a, b)
            przy self.assertRaises(TypeError):
                a >= b

        przy self.subTest("LE when equal"):
            a = ComparatorNotImplemented(9)
            b = ComparatorNotImplemented(9)
            self.assertEqual(a, b)
            przy self.assertRaises(TypeError):
                a <= b

    def test_pickle(self):
        dla proto w range(4, pickle.HIGHEST_PROTOCOL + 1):
            dla name w '__lt__', '__gt__', '__le__', '__ge__':
                przy self.subTest(method=name, proto=proto):
                    method = getattr(Orderable_LT, name)
                    method_copy = pickle.loads(pickle.dumps(method, proto))
                    self.assertIs(method_copy, method)

@functools.total_ordering
klasa Orderable_LT:
    def __init__(self, value):
        self.value = value
    def __lt__(self, other):
        zwróć self.value < other.value
    def __eq__(self, other):
        zwróć self.value == other.value


klasa TestLRU:

    def test_lru(self):
        def orig(x, y):
            zwróć 3 * x + y
        f = self.module.lru_cache(maxsize=20)(orig)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(maxsize, 20)
        self.assertEqual(currsize, 0)
        self.assertEqual(hits, 0)
        self.assertEqual(misses, 0)

        domain = range(5)
        dla i w range(1000):
            x, y = choice(domain), choice(domain)
            actual = f(x, y)
            expected = orig(x, y)
            self.assertEqual(actual, expected)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertPrawda(hits > misses)
        self.assertEqual(hits + misses, 1000)
        self.assertEqual(currsize, 20)

        f.cache_clear()   # test clearing
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(hits, 0)
        self.assertEqual(misses, 0)
        self.assertEqual(currsize, 0)
        f(x, y)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(hits, 0)
        self.assertEqual(misses, 1)
        self.assertEqual(currsize, 1)

        # Test bypassing the cache
        self.assertIs(f.__wrapped__, orig)
        f.__wrapped__(x, y)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(hits, 0)
        self.assertEqual(misses, 1)
        self.assertEqual(currsize, 1)

        # test size zero (which means "never-cache")
        @self.module.lru_cache(0)
        def f():
            nonlocal f_cnt
            f_cnt += 1
            zwróć 20
        self.assertEqual(f.cache_info().maxsize, 0)
        f_cnt = 0
        dla i w range(5):
            self.assertEqual(f(), 20)
        self.assertEqual(f_cnt, 5)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(hits, 0)
        self.assertEqual(misses, 5)
        self.assertEqual(currsize, 0)

        # test size one
        @self.module.lru_cache(1)
        def f():
            nonlocal f_cnt
            f_cnt += 1
            zwróć 20
        self.assertEqual(f.cache_info().maxsize, 1)
        f_cnt = 0
        dla i w range(5):
            self.assertEqual(f(), 20)
        self.assertEqual(f_cnt, 1)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(hits, 4)
        self.assertEqual(misses, 1)
        self.assertEqual(currsize, 1)

        # test size two
        @self.module.lru_cache(2)
        def f(x):
            nonlocal f_cnt
            f_cnt += 1
            zwróć x*10
        self.assertEqual(f.cache_info().maxsize, 2)
        f_cnt = 0
        dla x w 7, 9, 7, 9, 7, 9, 8, 8, 8, 9, 9, 9, 8, 8, 8, 7:
            #    *  *              *                          *
            self.assertEqual(f(x), x*10)
        self.assertEqual(f_cnt, 4)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(hits, 12)
        self.assertEqual(misses, 4)
        self.assertEqual(currsize, 2)

    def test_lru_with_maxsize_none(self):
        @self.module.lru_cache(maxsize=Nic)
        def fib(n):
            jeżeli n < 2:
                zwróć n
            zwróć fib(n-1) + fib(n-2)
        self.assertEqual([fib(n) dla n w range(16)],
            [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610])
        self.assertEqual(fib.cache_info(),
            self.module._CacheInfo(hits=28, misses=16, maxsize=Nic, currsize=16))
        fib.cache_clear()
        self.assertEqual(fib.cache_info(),
            self.module._CacheInfo(hits=0, misses=0, maxsize=Nic, currsize=0))

    def test_lru_with_maxsize_negative(self):
        @self.module.lru_cache(maxsize=-10)
        def eq(n):
            zwróć n
        dla i w (0, 1):
            self.assertEqual([eq(n) dla n w range(150)], list(range(150)))
        self.assertEqual(eq.cache_info(),
            self.module._CacheInfo(hits=0, misses=300, maxsize=-10, currsize=1))

    def test_lru_with_exceptions(self):
        # Verify that user_function exceptions get dalejed through without
        # creating a hard-to-read chained exception.
        # http://bugs.python.org/issue13177
        dla maxsize w (Nic, 128):
            @self.module.lru_cache(maxsize)
            def func(i):
                zwróć 'abc'[i]
            self.assertEqual(func(0), 'a')
            przy self.assertRaises(IndexError) jako cm:
                func(15)
            self.assertIsNic(cm.exception.__context__)
            # Verify that the previous exception did nie result w a cached entry
            przy self.assertRaises(IndexError):
                func(15)

    def test_lru_with_types(self):
        dla maxsize w (Nic, 128):
            @self.module.lru_cache(maxsize=maxsize, typed=Prawda)
            def square(x):
                zwróć x * x
            self.assertEqual(square(3), 9)
            self.assertEqual(type(square(3)), type(9))
            self.assertEqual(square(3.0), 9.0)
            self.assertEqual(type(square(3.0)), type(9.0))
            self.assertEqual(square(x=3), 9)
            self.assertEqual(type(square(x=3)), type(9))
            self.assertEqual(square(x=3.0), 9.0)
            self.assertEqual(type(square(x=3.0)), type(9.0))
            self.assertEqual(square.cache_info().hits, 4)
            self.assertEqual(square.cache_info().misses, 4)

    def test_lru_with_keyword_args(self):
        @self.module.lru_cache()
        def fib(n):
            jeżeli n < 2:
                zwróć n
            zwróć fib(n=n-1) + fib(n=n-2)
        self.assertEqual(
            [fib(n=number) dla number w range(16)],
            [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]
        )
        self.assertEqual(fib.cache_info(),
            self.module._CacheInfo(hits=28, misses=16, maxsize=128, currsize=16))
        fib.cache_clear()
        self.assertEqual(fib.cache_info(),
            self.module._CacheInfo(hits=0, misses=0, maxsize=128, currsize=0))

    def test_lru_with_keyword_args_maxsize_none(self):
        @self.module.lru_cache(maxsize=Nic)
        def fib(n):
            jeżeli n < 2:
                zwróć n
            zwróć fib(n=n-1) + fib(n=n-2)
        self.assertEqual([fib(n=number) dla number w range(16)],
            [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610])
        self.assertEqual(fib.cache_info(),
            self.module._CacheInfo(hits=28, misses=16, maxsize=Nic, currsize=16))
        fib.cache_clear()
        self.assertEqual(fib.cache_info(),
            self.module._CacheInfo(hits=0, misses=0, maxsize=Nic, currsize=0))

    def test_lru_cache_decoration(self):
        def f(zomg: 'zomg_annotation'):
            """f doc string"""
            zwróć 42
        g = self.module.lru_cache()(f)
        dla attr w self.module.WRAPPER_ASSIGNMENTS:
            self.assertEqual(getattr(g, attr), getattr(f, attr))

    @unittest.skipUnless(threading, 'This test requires threading.')
    def test_lru_cache_threaded(self):
        n, m = 5, 11
        def orig(x, y):
            zwróć 3 * x + y
        f = self.module.lru_cache(maxsize=n*m)(orig)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(currsize, 0)

        start = threading.Event()
        def full(k):
            start.wait(10)
            dla _ w range(m):
                self.assertEqual(f(k, 0), orig(k, 0))

        def clear():
            start.wait(10)
            dla _ w range(2*m):
                f.cache_clear()

        orig_si = sys.getswitchinterval()
        sys.setswitchinterval(1e-6)
        spróbuj:
            # create n threads w order to fill cache
            threads = [threading.Thread(target=full, args=[k])
                       dla k w range(n)]
            przy support.start_threads(threads):
                start.set()

            hits, misses, maxsize, currsize = f.cache_info()
            jeżeli self.module jest py_functools:
                # XXX: Why can be nie equal?
                self.assertLessEqual(misses, n)
                self.assertLessEqual(hits, m*n - misses)
            inaczej:
                self.assertEqual(misses, n)
                self.assertEqual(hits, m*n - misses)
            self.assertEqual(currsize, n)

            # create n threads w order to fill cache oraz 1 to clear it
            threads = [threading.Thread(target=clear)]
            threads += [threading.Thread(target=full, args=[k])
                        dla k w range(n)]
            start.clear()
            przy support.start_threads(threads):
                start.set()
        w_końcu:
            sys.setswitchinterval(orig_si)

    @unittest.skipUnless(threading, 'This test requires threading.')
    def test_lru_cache_threaded2(self):
        # Simultaneous call przy the same arguments
        n, m = 5, 7
        start = threading.Barrier(n+1)
        pause = threading.Barrier(n+1)
        stop = threading.Barrier(n+1)
        @self.module.lru_cache(maxsize=m*n)
        def f(x):
            pause.wait(10)
            zwróć 3 * x
        self.assertEqual(f.cache_info(), (0, 0, m*n, 0))
        def test():
            dla i w range(m):
                start.wait(10)
                self.assertEqual(f(i), 3 * i)
                stop.wait(10)
        threads = [threading.Thread(target=test) dla k w range(n)]
        przy support.start_threads(threads):
            dla i w range(m):
                start.wait(10)
                stop.reset()
                pause.wait(10)
                start.reset()
                stop.wait(10)
                pause.reset()
                self.assertEqual(f.cache_info(), (0, (i+1)*n, m*n, i+1))

    def test_need_for_rlock(self):
        # This will deadlock on an LRU cache that uses a regular lock

        @self.module.lru_cache(maxsize=10)
        def test_func(x):
            'Used to demonstrate a reentrant lru_cache call within a single thread'
            zwróć x

        klasa DoubleEq:
            'Demonstrate a reentrant lru_cache call within a single thread'
            def __init__(self, x):
                self.x = x
            def __hash__(self):
                zwróć self.x
            def __eq__(self, other):
                jeżeli self.x == 2:
                    test_func(DoubleEq(1))
                zwróć self.x == other.x

        test_func(DoubleEq(1))                      # Load the cache
        test_func(DoubleEq(2))                      # Load the cache
        self.assertEqual(test_func(DoubleEq(2)),    # Trigger a re-entrant __eq__ call
                         DoubleEq(2))               # Verify the correct zwróć value

    def test_early_detection_of_bad_call(self):
        # Issue #22184
        przy self.assertRaises(TypeError):
            @functools.lru_cache
            def f():
                dalej

    def test_lru_method(self):
        klasa X(int):
            f_cnt = 0
            @self.module.lru_cache(2)
            def f(self, x):
                self.f_cnt += 1
                zwróć x*10+self
        a = X(5)
        b = X(5)
        c = X(7)
        self.assertEqual(X.f.cache_info(), (0, 0, 2, 0))

        dla x w 1, 2, 2, 3, 1, 1, 1, 2, 3, 3:
            self.assertEqual(a.f(x), x*10 + 5)
        self.assertEqual((a.f_cnt, b.f_cnt, c.f_cnt), (6, 0, 0))
        self.assertEqual(X.f.cache_info(), (4, 6, 2, 2))

        dla x w 1, 2, 1, 1, 1, 1, 3, 2, 2, 2:
            self.assertEqual(b.f(x), x*10 + 5)
        self.assertEqual((a.f_cnt, b.f_cnt, c.f_cnt), (6, 4, 0))
        self.assertEqual(X.f.cache_info(), (10, 10, 2, 2))

        dla x w 2, 1, 1, 1, 1, 2, 1, 3, 2, 1:
            self.assertEqual(c.f(x), x*10 + 7)
        self.assertEqual((a.f_cnt, b.f_cnt, c.f_cnt), (6, 4, 5))
        self.assertEqual(X.f.cache_info(), (15, 15, 2, 2))

        self.assertEqual(a.f.cache_info(), X.f.cache_info())
        self.assertEqual(b.f.cache_info(), X.f.cache_info())
        self.assertEqual(c.f.cache_info(), X.f.cache_info())

klasa TestLRUC(TestLRU, unittest.TestCase):
    module = c_functools

klasa TestLRUPy(TestLRU, unittest.TestCase):
    module = py_functools


klasa TestSingleDispatch(unittest.TestCase):
    def test_simple_overloads(self):
        @functools.singledispatch
        def g(obj):
            zwróć "base"
        def g_int(i):
            zwróć "integer"
        g.register(int, g_int)
        self.assertEqual(g("str"), "base")
        self.assertEqual(g(1), "integer")
        self.assertEqual(g([1,2,3]), "base")

    def test_mro(self):
        @functools.singledispatch
        def g(obj):
            zwróć "base"
        klasa A:
            dalej
        klasa C(A):
            dalej
        klasa B(A):
            dalej
        klasa D(C, B):
            dalej
        def g_A(a):
            zwróć "A"
        def g_B(b):
            zwróć "B"
        g.register(A, g_A)
        g.register(B, g_B)
        self.assertEqual(g(A()), "A")
        self.assertEqual(g(B()), "B")
        self.assertEqual(g(C()), "A")
        self.assertEqual(g(D()), "B")

    def test_register_decorator(self):
        @functools.singledispatch
        def g(obj):
            zwróć "base"
        @g.register(int)
        def g_int(i):
            zwróć "int %s" % (i,)
        self.assertEqual(g(""), "base")
        self.assertEqual(g(12), "int 12")
        self.assertIs(g.dispatch(int), g_int)
        self.assertIs(g.dispatch(object), g.dispatch(str))
        # Note: w the assert above this jest nie g.
        # @singledispatch returns the wrapper.

    def test_wrapping_attributes(self):
        @functools.singledispatch
        def g(obj):
            "Simple test"
            zwróć "Test"
        self.assertEqual(g.__name__, "g")
        jeżeli sys.flags.optimize < 2:
            self.assertEqual(g.__doc__, "Simple test")

    @unittest.skipUnless(decimal, 'requires _decimal')
    @support.cpython_only
    def test_c_classes(self):
        @functools.singledispatch
        def g(obj):
            zwróć "base"
        @g.register(decimal.DecimalException)
        def _(obj):
            zwróć obj.args
        subn = decimal.Subnormal("Exponent < Emin")
        rnd = decimal.Rounded("Number got rounded")
        self.assertEqual(g(subn), ("Exponent < Emin",))
        self.assertEqual(g(rnd), ("Number got rounded",))
        @g.register(decimal.Subnormal)
        def _(obj):
            zwróć "Too small to care."
        self.assertEqual(g(subn), "Too small to care.")
        self.assertEqual(g(rnd), ("Number got rounded",))

    def test_compose_mro(self):
        # Nic of the examples w this test depend on haystack ordering.
        c = collections
        mro = functools._compose_mro
        bases = [c.Sequence, c.MutableMapping, c.Mapping, c.Set]
        dla haystack w permutations(bases):
            m = mro(dict, haystack)
            self.assertEqual(m, [dict, c.MutableMapping, c.Mapping, c.Sized,
                                 c.Iterable, c.Container, object])
        bases = [c.Container, c.Mapping, c.MutableMapping, c.OrderedDict]
        dla haystack w permutations(bases):
            m = mro(c.ChainMap, haystack)
            self.assertEqual(m, [c.ChainMap, c.MutableMapping, c.Mapping,
                                 c.Sized, c.Iterable, c.Container, object])

        # If there's a generic function przy implementations registered for
        # both Sized oraz Container, dalejing a defaultdict to it results w an
        # ambiguous dispatch which will cause a RuntimeError (see
        # test_mro_conflicts).
        bases = [c.Container, c.Sized, str]
        dla haystack w permutations(bases):
            m = mro(c.defaultdict, [c.Sized, c.Container, str])
            self.assertEqual(m, [c.defaultdict, dict, c.Sized, c.Container,
                                 object])

        # MutableSequence below jest registered directly on D. In other words, it
        # preceeds MutableMapping which means single dispatch will always
        # choose MutableSequence here.
        klasa D(c.defaultdict):
            dalej
        c.MutableSequence.register(D)
        bases = [c.MutableSequence, c.MutableMapping]
        dla haystack w permutations(bases):
            m = mro(D, bases)
            self.assertEqual(m, [D, c.MutableSequence, c.Sequence,
                                 c.defaultdict, dict, c.MutableMapping,
                                 c.Mapping, c.Sized, c.Iterable, c.Container,
                                 object])

        # Container oraz Callable are registered on different base classes oraz
        # a generic function supporting both should always pick the Callable
        # implementation jeżeli a C instance jest dalejed.
        klasa C(c.defaultdict):
            def __call__(self):
                dalej
        bases = [c.Sized, c.Callable, c.Container, c.Mapping]
        dla haystack w permutations(bases):
            m = mro(C, haystack)
            self.assertEqual(m, [C, c.Callable, c.defaultdict, dict, c.Mapping,
                                 c.Sized, c.Iterable, c.Container, object])

    def test_register_abc(self):
        c = collections
        d = {"a": "b"}
        l = [1, 2, 3]
        s = {object(), Nic}
        f = frozenset(s)
        t = (1, 2, 3)
        @functools.singledispatch
        def g(obj):
            zwróć "base"
        self.assertEqual(g(d), "base")
        self.assertEqual(g(l), "base")
        self.assertEqual(g(s), "base")
        self.assertEqual(g(f), "base")
        self.assertEqual(g(t), "base")
        g.register(c.Sized, lambda obj: "sized")
        self.assertEqual(g(d), "sized")
        self.assertEqual(g(l), "sized")
        self.assertEqual(g(s), "sized")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")
        g.register(c.MutableMapping, lambda obj: "mutablemapping")
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(g(l), "sized")
        self.assertEqual(g(s), "sized")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")
        g.register(c.ChainMap, lambda obj: "chainmap")
        self.assertEqual(g(d), "mutablemapping")  # irrelevant ABCs registered
        self.assertEqual(g(l), "sized")
        self.assertEqual(g(s), "sized")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")
        g.register(c.MutableSequence, lambda obj: "mutablesequence")
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "sized")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")
        g.register(c.MutableSet, lambda obj: "mutableset")
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")
        g.register(c.Mapping, lambda obj: "mapping")
        self.assertEqual(g(d), "mutablemapping")  # nie specific enough
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")
        g.register(c.Sequence, lambda obj: "sequence")
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sequence")
        g.register(c.Set, lambda obj: "set")
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "set")
        self.assertEqual(g(t), "sequence")
        g.register(dict, lambda obj: "dict")
        self.assertEqual(g(d), "dict")
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "set")
        self.assertEqual(g(t), "sequence")
        g.register(list, lambda obj: "list")
        self.assertEqual(g(d), "dict")
        self.assertEqual(g(l), "list")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "set")
        self.assertEqual(g(t), "sequence")
        g.register(set, lambda obj: "concrete-set")
        self.assertEqual(g(d), "dict")
        self.assertEqual(g(l), "list")
        self.assertEqual(g(s), "concrete-set")
        self.assertEqual(g(f), "set")
        self.assertEqual(g(t), "sequence")
        g.register(frozenset, lambda obj: "frozen-set")
        self.assertEqual(g(d), "dict")
        self.assertEqual(g(l), "list")
        self.assertEqual(g(s), "concrete-set")
        self.assertEqual(g(f), "frozen-set")
        self.assertEqual(g(t), "sequence")
        g.register(tuple, lambda obj: "tuple")
        self.assertEqual(g(d), "dict")
        self.assertEqual(g(l), "list")
        self.assertEqual(g(s), "concrete-set")
        self.assertEqual(g(f), "frozen-set")
        self.assertEqual(g(t), "tuple")

    def test_c3_abc(self):
        c = collections
        mro = functools._c3_mro
        klasa A(object):
            dalej
        klasa B(A):
            def __len__(self):
                zwróć 0   # implies Sized
        @c.Container.register
        klasa C(object):
            dalej
        klasa D(object):
            dalej   # unrelated
        klasa X(D, C, B):
            def __call__(self):
                dalej   # implies Callable
        expected = [X, c.Callable, D, C, c.Container, B, c.Sized, A, object]
        dla abcs w permutations([c.Sized, c.Callable, c.Container]):
            self.assertEqual(mro(X, abcs=abcs), expected)
        # unrelated ABCs don't appear w the resulting MRO
        many_abcs = [c.Mapping, c.Sized, c.Callable, c.Container, c.Iterable]
        self.assertEqual(mro(X, abcs=many_abcs), expected)

    def test_mro_conflicts(self):
        c = collections
        @functools.singledispatch
        def g(arg):
            zwróć "base"
        klasa O(c.Sized):
            def __len__(self):
                zwróć 0
        o = O()
        self.assertEqual(g(o), "base")
        g.register(c.Iterable, lambda arg: "iterable")
        g.register(c.Container, lambda arg: "container")
        g.register(c.Sized, lambda arg: "sized")
        g.register(c.Set, lambda arg: "set")
        self.assertEqual(g(o), "sized")
        c.Iterable.register(O)
        self.assertEqual(g(o), "sized")   # because it's explicitly w __mro__
        c.Container.register(O)
        self.assertEqual(g(o), "sized")   # see above: Sized jest w __mro__
        c.Set.register(O)
        self.assertEqual(g(o), "set")     # because c.Set jest a subclass of
                                          # c.Sized oraz c.Container
        klasa P:
            dalej
        p = P()
        self.assertEqual(g(p), "base")
        c.Iterable.register(P)
        self.assertEqual(g(p), "iterable")
        c.Container.register(P)
        przy self.assertRaises(RuntimeError) jako re_one:
            g(p)
        self.assertIn(
            str(re_one.exception),
            (("Ambiguous dispatch: <class 'collections.abc.Container'> "
              "or <class 'collections.abc.Iterable'>"),
             ("Ambiguous dispatch: <class 'collections.abc.Iterable'> "
              "or <class 'collections.abc.Container'>")),
        )
        klasa Q(c.Sized):
            def __len__(self):
                zwróć 0
        q = Q()
        self.assertEqual(g(q), "sized")
        c.Iterable.register(Q)
        self.assertEqual(g(q), "sized")   # because it's explicitly w __mro__
        c.Set.register(Q)
        self.assertEqual(g(q), "set")     # because c.Set jest a subclass of
                                          # c.Sized oraz c.Iterable
        @functools.singledispatch
        def h(arg):
            zwróć "base"
        @h.register(c.Sized)
        def _(arg):
            zwróć "sized"
        @h.register(c.Container)
        def _(arg):
            zwróć "container"
        # Even though Sized oraz Container are explicit bases of MutableMapping,
        # this ABC jest implicitly registered on defaultdict which makes all of
        # MutableMapping's bases implicit jako well z defaultdict's
        # perspective.
        przy self.assertRaises(RuntimeError) jako re_two:
            h(c.defaultdict(lambda: 0))
        self.assertIn(
            str(re_two.exception),
            (("Ambiguous dispatch: <class 'collections.abc.Container'> "
              "or <class 'collections.abc.Sized'>"),
             ("Ambiguous dispatch: <class 'collections.abc.Sized'> "
              "or <class 'collections.abc.Container'>")),
        )
        klasa R(c.defaultdict):
            dalej
        c.MutableSequence.register(R)
        @functools.singledispatch
        def i(arg):
            zwróć "base"
        @i.register(c.MutableMapping)
        def _(arg):
            zwróć "mapping"
        @i.register(c.MutableSequence)
        def _(arg):
            zwróć "sequence"
        r = R()
        self.assertEqual(i(r), "sequence")
        klasa S:
            dalej
        klasa T(S, c.Sized):
            def __len__(self):
                zwróć 0
        t = T()
        self.assertEqual(h(t), "sized")
        c.Container.register(T)
        self.assertEqual(h(t), "sized")   # because it's explicitly w the MRO
        klasa U:
            def __len__(self):
                zwróć 0
        u = U()
        self.assertEqual(h(u), "sized")   # implicit Sized subclass inferred
                                          # z the existence of __len__()
        c.Container.register(U)
        # There jest no preference dla registered versus inferred ABCs.
        przy self.assertRaises(RuntimeError) jako re_three:
            h(u)
        self.assertIn(
            str(re_three.exception),
            (("Ambiguous dispatch: <class 'collections.abc.Container'> "
              "or <class 'collections.abc.Sized'>"),
             ("Ambiguous dispatch: <class 'collections.abc.Sized'> "
              "or <class 'collections.abc.Container'>")),
        )
        klasa V(c.Sized, S):
            def __len__(self):
                zwróć 0
        @functools.singledispatch
        def j(arg):
            zwróć "base"
        @j.register(S)
        def _(arg):
            zwróć "s"
        @j.register(c.Container)
        def _(arg):
            zwróć "container"
        v = V()
        self.assertEqual(j(v), "s")
        c.Container.register(V)
        self.assertEqual(j(v), "container")   # because it ends up right after
                                              # Sized w the MRO

    def test_cache_invalidation(self):
        z collections zaimportuj UserDict
        klasa TracingDict(UserDict):
            def __init__(self, *args, **kwargs):
                super(TracingDict, self).__init__(*args, **kwargs)
                self.set_ops = []
                self.get_ops = []
            def __getitem__(self, key):
                result = self.data[key]
                self.get_ops.append(key)
                zwróć result
            def __setitem__(self, key, value):
                self.set_ops.append(key)
                self.data[key] = value
            def clear(self):
                self.data.clear()
        _orig_wkd = functools.WeakKeyDictionary
        td = TracingDict()
        functools.WeakKeyDictionary = lambda: td
        c = collections
        @functools.singledispatch
        def g(arg):
            zwróć "base"
        d = {}
        l = []
        self.assertEqual(len(td), 0)
        self.assertEqual(g(d), "base")
        self.assertEqual(len(td), 1)
        self.assertEqual(td.get_ops, [])
        self.assertEqual(td.set_ops, [dict])
        self.assertEqual(td.data[dict], g.registry[object])
        self.assertEqual(g(l), "base")
        self.assertEqual(len(td), 2)
        self.assertEqual(td.get_ops, [])
        self.assertEqual(td.set_ops, [dict, list])
        self.assertEqual(td.data[dict], g.registry[object])
        self.assertEqual(td.data[list], g.registry[object])
        self.assertEqual(td.data[dict], td.data[list])
        self.assertEqual(g(l), "base")
        self.assertEqual(g(d), "base")
        self.assertEqual(td.get_ops, [list, dict])
        self.assertEqual(td.set_ops, [dict, list])
        g.register(list, lambda arg: "list")
        self.assertEqual(td.get_ops, [list, dict])
        self.assertEqual(len(td), 0)
        self.assertEqual(g(d), "base")
        self.assertEqual(len(td), 1)
        self.assertEqual(td.get_ops, [list, dict])
        self.assertEqual(td.set_ops, [dict, list, dict])
        self.assertEqual(td.data[dict],
                         functools._find_impl(dict, g.registry))
        self.assertEqual(g(l), "list")
        self.assertEqual(len(td), 2)
        self.assertEqual(td.get_ops, [list, dict])
        self.assertEqual(td.set_ops, [dict, list, dict, list])
        self.assertEqual(td.data[list],
                         functools._find_impl(list, g.registry))
        klasa X:
            dalej
        c.MutableMapping.register(X)   # Will nie invalidate the cache,
                                       # nie using ABCs yet.
        self.assertEqual(g(d), "base")
        self.assertEqual(g(l), "list")
        self.assertEqual(td.get_ops, [list, dict, dict, list])
        self.assertEqual(td.set_ops, [dict, list, dict, list])
        g.register(c.Sized, lambda arg: "sized")
        self.assertEqual(len(td), 0)
        self.assertEqual(g(d), "sized")
        self.assertEqual(len(td), 1)
        self.assertEqual(td.get_ops, [list, dict, dict, list])
        self.assertEqual(td.set_ops, [dict, list, dict, list, dict])
        self.assertEqual(g(l), "list")
        self.assertEqual(len(td), 2)
        self.assertEqual(td.get_ops, [list, dict, dict, list])
        self.assertEqual(td.set_ops, [dict, list, dict, list, dict, list])
        self.assertEqual(g(l), "list")
        self.assertEqual(g(d), "sized")
        self.assertEqual(td.get_ops, [list, dict, dict, list, list, dict])
        self.assertEqual(td.set_ops, [dict, list, dict, list, dict, list])
        g.dispatch(list)
        g.dispatch(dict)
        self.assertEqual(td.get_ops, [list, dict, dict, list, list, dict,
                                      list, dict])
        self.assertEqual(td.set_ops, [dict, list, dict, list, dict, list])
        c.MutableSet.register(X)       # Will invalidate the cache.
        self.assertEqual(len(td), 2)   # Stale cache.
        self.assertEqual(g(l), "list")
        self.assertEqual(len(td), 1)
        g.register(c.MutableMapping, lambda arg: "mutablemapping")
        self.assertEqual(len(td), 0)
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(len(td), 1)
        self.assertEqual(g(l), "list")
        self.assertEqual(len(td), 2)
        g.register(dict, lambda arg: "dict")
        self.assertEqual(g(d), "dict")
        self.assertEqual(g(l), "list")
        g._clear_cache()
        self.assertEqual(len(td), 0)
        functools.WeakKeyDictionary = _orig_wkd


jeżeli __name__ == '__main__':
    unittest.main()
