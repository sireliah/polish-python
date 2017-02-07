"""Unit tests dla collections.py."""

zaimportuj unittest, doctest, operator
z test.support zaimportuj TESTFN, forget, unlink, import_fresh_module
zaimportuj contextlib
zaimportuj inspect
z test zaimportuj support
z collections zaimportuj namedtuple, Counter, OrderedDict, _count_elements
z test zaimportuj mapping_tests
zaimportuj pickle, copy
z random zaimportuj randrange, shuffle
zaimportuj keyword
zaimportuj re
zaimportuj sys
zaimportuj types
z collections zaimportuj UserDict, UserString, UserList
z collections zaimportuj ChainMap
z collections zaimportuj deque
z collections.abc zaimportuj Awaitable, Coroutine, AsyncIterator, AsyncIterable
z collections.abc zaimportuj Hashable, Iterable, Iterator, Generator
z collections.abc zaimportuj Sized, Container, Callable
z collections.abc zaimportuj Set, MutableSet
z collections.abc zaimportuj Mapping, MutableMapping, KeysView, ItemsView
z collections.abc zaimportuj Sequence, MutableSequence
z collections.abc zaimportuj ByteString


klasa TestUserObjects(unittest.TestCase):
    def _superset_test(self, a, b):
        self.assertGreaterEqual(
            set(dir(a)),
            set(dir(b)),
            '{a} should have all the methods of {b}'.format(
                a=a.__name__,
                b=b.__name__,
            ),
        )
    def test_str_protocol(self):
        self._superset_test(UserString, str)

    def test_list_protocol(self):
        self._superset_test(UserList, list)

    def test_dict_protocol(self):
        self._superset_test(UserDict, dict)


################################################################################
### ChainMap (helper klasa dla configparser oraz the string module)
################################################################################

klasa TestChainMap(unittest.TestCase):

    def test_basics(self):
        c = ChainMap()
        c['a'] = 1
        c['b'] = 2
        d = c.new_child()
        d['b'] = 20
        d['c'] = 30
        self.assertEqual(d.maps, [{'b':20, 'c':30}, {'a':1, 'b':2}])  # check internal state
        self.assertEqual(d.items(), dict(a=1, b=20, c=30).items())    # check items/iter/getitem
        self.assertEqual(len(d), 3)                                   # check len
        dla key w 'abc':                                             # check contains
            self.assertIn(key, d)
        dla k, v w dict(a=1, b=20, c=30, z=100).items():             # check get
            self.assertEqual(d.get(k, 100), v)

        usuń d['b']                                                    # unmask a value
        self.assertEqual(d.maps, [{'c':30}, {'a':1, 'b':2}])          # check internal state
        self.assertEqual(d.items(), dict(a=1, b=2, c=30).items())     # check items/iter/getitem
        self.assertEqual(len(d), 3)                                   # check len
        dla key w 'abc':                                             # check contains
            self.assertIn(key, d)
        dla k, v w dict(a=1, b=2, c=30, z=100).items():              # check get
            self.assertEqual(d.get(k, 100), v)
        self.assertIn(repr(d), [                                      # check repr
            type(d).__name__ + "({'c': 30}, {'a': 1, 'b': 2})",
            type(d).__name__ + "({'c': 30}, {'b': 2, 'a': 1})"
        ])

        dla e w d.copy(), copy.copy(d):                               # check shallow copies
            self.assertEqual(d, e)
            self.assertEqual(d.maps, e.maps)
            self.assertIsNot(d, e)
            self.assertIsNot(d.maps[0], e.maps[0])
            dla m1, m2 w zip(d.maps[1:], e.maps[1:]):
                self.assertIs(m1, m2)

        # check deep copies
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            e = pickle.loads(pickle.dumps(d, proto))
            self.assertEqual(d, e)
            self.assertEqual(d.maps, e.maps)
            self.assertIsNot(d, e)
            dla m1, m2 w zip(d.maps, e.maps):
                self.assertIsNot(m1, m2, e)
        dla e w [copy.deepcopy(d),
                  eval(repr(d))
                ]:
            self.assertEqual(d, e)
            self.assertEqual(d.maps, e.maps)
            self.assertIsNot(d, e)
            dla m1, m2 w zip(d.maps, e.maps):
                self.assertIsNot(m1, m2, e)

        f = d.new_child()
        f['b'] = 5
        self.assertEqual(f.maps, [{'b': 5}, {'c':30}, {'a':1, 'b':2}])
        self.assertEqual(f.parents.maps, [{'c':30}, {'a':1, 'b':2}])   # check parents
        self.assertEqual(f['b'], 5)                                    # find first w chain
        self.assertEqual(f.parents['b'], 2)                            # look beyond maps[0]

    def test_contructor(self):
        self.assertEqual(ChainMap().maps, [{}])                        # no-args --> one new dict
        self.assertEqual(ChainMap({1:2}).maps, [{1:2}])                # 1 arg --> list

    def test_bool(self):
        self.assertNieprawda(ChainMap())
        self.assertNieprawda(ChainMap({}, {}))
        self.assertPrawda(ChainMap({1:2}, {}))
        self.assertPrawda(ChainMap({}, {1:2}))

    def test_missing(self):
        klasa DefaultChainMap(ChainMap):
            def __missing__(self, key):
                zwróć 999
        d = DefaultChainMap(dict(a=1, b=2), dict(b=20, c=30))
        dla k, v w dict(a=1, b=2, c=30, d=999).items():
            self.assertEqual(d[k], v)                                  # check __getitem__ w/missing
        dla k, v w dict(a=1, b=2, c=30, d=77).items():
            self.assertEqual(d.get(k, 77), v)                          # check get() w/ missing
        dla k, v w dict(a=Prawda, b=Prawda, c=Prawda, d=Nieprawda).items():
            self.assertEqual(k w d, v)                                # check __contains__ w/missing
        self.assertEqual(d.pop('a', 1001), 1, d)
        self.assertEqual(d.pop('a', 1002), 1002)                       # check pop() w/missing
        self.assertEqual(d.popitem(), ('b', 2))                        # check popitem() w/missing
        przy self.assertRaises(KeyError):
            d.popitem()

    def test_dict_coercion(self):
        d = ChainMap(dict(a=1, b=2), dict(b=20, c=30))
        self.assertEqual(dict(d), dict(a=1, b=2, c=30))
        self.assertEqual(dict(d.items()), dict(a=1, b=2, c=30))

    def test_new_child(self):
        'Tests dla changes dla issue #16613.'
        c = ChainMap()
        c['a'] = 1
        c['b'] = 2
        m = {'b':20, 'c': 30}
        d = c.new_child(m)
        self.assertEqual(d.maps, [{'b':20, 'c':30}, {'a':1, 'b':2}])  # check internal state
        self.assertIs(m, d.maps[0])

        # Use a different map than a dict
        klasa lowerdict(dict):
            def __getitem__(self, key):
                jeżeli isinstance(key, str):
                    key = key.lower()
                zwróć dict.__getitem__(self, key)
            def __contains__(self, key):
                jeżeli isinstance(key, str):
                    key = key.lower()
                zwróć dict.__contains__(self, key)

        c = ChainMap()
        c['a'] = 1
        c['b'] = 2
        m = lowerdict(b=20, c=30)
        d = c.new_child(m)
        self.assertIs(m, d.maps[0])
        dla key w 'abc':                                             # check contains
            self.assertIn(key, d)
        dla k, v w dict(a=1, B=20, C=30, z=100).items():             # check get
            self.assertEqual(d.get(k, 100), v)


################################################################################
### Named Tuples
################################################################################

TestNT = namedtuple('TestNT', 'x y z')    # type used dla pickle tests

klasa TestNamedTuple(unittest.TestCase):

    def test_factory(self):
        Point = namedtuple('Point', 'x y')
        self.assertEqual(Point.__name__, 'Point')
        self.assertEqual(Point.__slots__, ())
        self.assertEqual(Point.__module__, __name__)
        self.assertEqual(Point.__getitem__, tuple.__getitem__)
        self.assertEqual(Point._fields, ('x', 'y'))
        self.assertIn('class Point(tuple)', Point._source)

        self.assertRaises(ValueError, namedtuple, 'abc%', 'efg ghi')       # type has non-alpha char
        self.assertRaises(ValueError, namedtuple, 'class', 'efg ghi')      # type has keyword
        self.assertRaises(ValueError, namedtuple, '9abc', 'efg ghi')       # type starts przy digit

        self.assertRaises(ValueError, namedtuple, 'abc', 'efg g%hi')       # field przy non-alpha char
        self.assertRaises(ValueError, namedtuple, 'abc', 'abc class')      # field has keyword
        self.assertRaises(ValueError, namedtuple, 'abc', '8efg 9ghi')      # field starts przy digit
        self.assertRaises(ValueError, namedtuple, 'abc', '_efg ghi')       # field przy leading underscore
        self.assertRaises(ValueError, namedtuple, 'abc', 'efg efg ghi')    # duplicate field

        namedtuple('Point0', 'x1 y2')   # Verify that numbers are allowed w names
        namedtuple('_', 'a b c')        # Test leading underscores w a typename

        nt = namedtuple('nt', 'the quick brown fox')                       # check unicode input
        self.assertNotIn("u'", repr(nt._fields))
        nt = namedtuple('nt', ('the', 'quick'))                           # check unicode input
        self.assertNotIn("u'", repr(nt._fields))

        self.assertRaises(TypeError, Point._make, [11])                     # catch too few args
        self.assertRaises(TypeError, Point._make, [11, 22, 33])             # catch too many args

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted przy -O2 oraz above")
    def test_factory_doc_attr(self):
        Point = namedtuple('Point', 'x y')
        self.assertEqual(Point.__doc__, 'Point(x, y)')

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted przy -O2 oraz above")
    def test_doc_writable(self):
        Point = namedtuple('Point', 'x y')
        self.assertEqual(Point.x.__doc__, 'Alias dla field number 0')
        Point.x.__doc__ = 'docstring dla Point.x'
        self.assertEqual(Point.x.__doc__, 'docstring dla Point.x')

    def test_name_fixer(self):
        dla spec, renamed w [
            [('efg', 'g%hi'),  ('efg', '_1')],                              # field przy non-alpha char
            [('abc', 'class'), ('abc', '_1')],                              # field has keyword
            [('8efg', '9ghi'), ('_0', '_1')],                               # field starts przy digit
            [('abc', '_efg'), ('abc', '_1')],                               # field przy leading underscore
            [('abc', 'efg', 'efg', 'ghi'), ('abc', 'efg', '_2', 'ghi')],    # duplicate field
            [('abc', '', 'x'), ('abc', '_1', 'x')],                         # fieldname jest a space
        ]:
            self.assertEqual(namedtuple('NT', spec, rename=Prawda)._fields, renamed)

    def test_instance(self):
        Point = namedtuple('Point', 'x y')
        p = Point(11, 22)
        self.assertEqual(p, Point(x=11, y=22))
        self.assertEqual(p, Point(11, y=22))
        self.assertEqual(p, Point(y=22, x=11))
        self.assertEqual(p, Point(*(11, 22)))
        self.assertEqual(p, Point(**dict(x=11, y=22)))
        self.assertRaises(TypeError, Point, 1)                              # too few args
        self.assertRaises(TypeError, Point, 1, 2, 3)                        # too many args
        self.assertRaises(TypeError, eval, 'Point(XXX=1, y=2)', locals())   # wrong keyword argument
        self.assertRaises(TypeError, eval, 'Point(x=1)', locals())          # missing keyword argument
        self.assertEqual(repr(p), 'Point(x=11, y=22)')
        self.assertNotIn('__weakref__', dir(p))
        self.assertEqual(p, Point._make([11, 22]))                          # test _make classmethod
        self.assertEqual(p._fields, ('x', 'y'))                             # test _fields attribute
        self.assertEqual(p._replace(x=1), (1, 22))                          # test _replace method
        self.assertEqual(p._asdict(), dict(x=11, y=22))                     # test _asdict method
        self.assertEqual(vars(p), p._asdict())                              # verify that vars() works

        spróbuj:
            p._replace(x=1, error=2)
        wyjąwszy ValueError:
            dalej
        inaczej:
            self._fail('Did nie detect an incorrect fieldname')

        # verify that field string can have commas
        Point = namedtuple('Point', 'x, y')
        p = Point(x=11, y=22)
        self.assertEqual(repr(p), 'Point(x=11, y=22)')

        # verify that fieldspec can be a non-string sequence
        Point = namedtuple('Point', ('x', 'y'))
        p = Point(x=11, y=22)
        self.assertEqual(repr(p), 'Point(x=11, y=22)')

    def test_tupleness(self):
        Point = namedtuple('Point', 'x y')
        p = Point(11, 22)

        self.assertIsInstance(p, tuple)
        self.assertEqual(p, (11, 22))                                       # matches a real tuple
        self.assertEqual(tuple(p), (11, 22))                                # coercable to a real tuple
        self.assertEqual(list(p), [11, 22])                                 # coercable to a list
        self.assertEqual(max(p), 22)                                        # iterable
        self.assertEqual(max(*p), 22)                                       # star-able
        x, y = p
        self.assertEqual(p, (x, y))                                         # unpacks like a tuple
        self.assertEqual((p[0], p[1]), (11, 22))                            # indexable like a tuple
        self.assertRaises(IndexError, p.__getitem__, 3)

        self.assertEqual(p.x, x)
        self.assertEqual(p.y, y)
        self.assertRaises(AttributeError, eval, 'p.z', locals())

    def test_odd_sizes(self):
        Zero = namedtuple('Zero', '')
        self.assertEqual(Zero(), ())
        self.assertEqual(Zero._make([]), ())
        self.assertEqual(repr(Zero()), 'Zero()')
        self.assertEqual(Zero()._asdict(), {})
        self.assertEqual(Zero()._fields, ())

        Dot = namedtuple('Dot', 'd')
        self.assertEqual(Dot(1), (1,))
        self.assertEqual(Dot._make([1]), (1,))
        self.assertEqual(Dot(1).d, 1)
        self.assertEqual(repr(Dot(1)), 'Dot(d=1)')
        self.assertEqual(Dot(1)._asdict(), {'d':1})
        self.assertEqual(Dot(1)._replace(d=999), (999,))
        self.assertEqual(Dot(1)._fields, ('d',))

        # n = 5000
        n = 254 # SyntaxError: more than 255 arguments:
        zaimportuj string, random
        names = list(set(''.join([random.choice(string.ascii_letters)
                                  dla j w range(10)]) dla i w range(n)))
        n = len(names)
        Big = namedtuple('Big', names)
        b = Big(*range(n))
        self.assertEqual(b, tuple(range(n)))
        self.assertEqual(Big._make(range(n)), tuple(range(n)))
        dla pos, name w enumerate(names):
            self.assertEqual(getattr(b, name), pos)
        repr(b)                                 # make sure repr() doesn't blow-up
        d = b._asdict()
        d_expected = dict(zip(names, range(n)))
        self.assertEqual(d, d_expected)
        b2 = b._replace(**dict([(names[1], 999),(names[-5], 42)]))
        b2_expected = list(range(n))
        b2_expected[1] = 999
        b2_expected[-5] = 42
        self.assertEqual(b2, tuple(b2_expected))
        self.assertEqual(b._fields, tuple(names))

    def test_pickle(self):
        p = TestNT(x=10, y=20, z=30)
        dla module w (pickle,):
            loads = getattr(module, 'loads')
            dumps = getattr(module, 'dumps')
            dla protocol w range(-1, module.HIGHEST_PROTOCOL + 1):
                q = loads(dumps(p, protocol))
                self.assertEqual(p, q)
                self.assertEqual(p._fields, q._fields)
                self.assertNotIn(b'OrderedDict', dumps(p, protocol))

    def test_copy(self):
        p = TestNT(x=10, y=20, z=30)
        dla copier w copy.copy, copy.deepcopy:
            q = copier(p)
            self.assertEqual(p, q)
            self.assertEqual(p._fields, q._fields)

    def test_name_conflicts(self):
        # Some names like "self", "cls", "tuple", "itemgetter", oraz "property"
        # failed when used jako field names.  Test to make sure these now work.
        T = namedtuple('T', 'itemgetter property self cls tuple')
        t = T(1, 2, 3, 4, 5)
        self.assertEqual(t, (1,2,3,4,5))
        newt = t._replace(itemgetter=10, property=20, self=30, cls=40, tuple=50)
        self.assertEqual(newt, (10,20,30,40,50))

        # Broader test of all interesting names w a template
        przy support.captured_stdout() jako template:
            T = namedtuple('T', 'x', verbose=Prawda)
        words = set(re.findall('[A-Za-z]+', template.getvalue()))
        words -= set(keyword.kwlist)
        T = namedtuple('T', words)
        # test __new__
        values = tuple(range(len(words)))
        t = T(*values)
        self.assertEqual(t, values)
        t = T(**dict(zip(T._fields, values)))
        self.assertEqual(t, values)
        # test _make
        t = T._make(values)
        self.assertEqual(t, values)
        # exercise __repr__
        repr(t)
        # test _asdict
        self.assertEqual(t._asdict(), dict(zip(T._fields, values)))
        # test _replace
        t = T._make(values)
        newvalues = tuple(v*10 dla v w values)
        newt = t._replace(**dict(zip(T._fields, newvalues)))
        self.assertEqual(newt, newvalues)
        # test _fields
        self.assertEqual(T._fields, tuple(words))
        # test __getnewargs__
        self.assertEqual(t.__getnewargs__(), values)

    def test_repr(self):
        przy support.captured_stdout() jako template:
            A = namedtuple('A', 'x', verbose=Prawda)
        self.assertEqual(repr(A(1)), 'A(x=1)')
        # repr should show the name of the subclass
        klasa B(A):
            dalej
        self.assertEqual(repr(B(1)), 'B(x=1)')

    def test_source(self):
        # verify that _source can be run through exec()
        tmp = namedtuple('NTColor', 'red green blue')
        globals().pop('NTColor', Nic)          # remove artifacts z other tests
        exec(tmp._source, globals())
        self.assertIn('NTColor', globals())
        c = NTColor(10, 20, 30)
        self.assertEqual((c.red, c.green, c.blue), (10, 20, 30))
        self.assertEqual(NTColor._fields, ('red', 'green', 'blue'))
        globals().pop('NTColor', Nic)          # clean-up after this test


################################################################################
### Abstract Base Classes
################################################################################

klasa ABCTestCase(unittest.TestCase):

    def validate_abstract_methods(self, abc, *names):
        methodstubs = dict.fromkeys(names, lambda s, *args: 0)

        # everything should work will all required methods are present
        C = type('C', (abc,), methodstubs)
        C()

        # instantiation should fail jeżeli a required method jest missing
        dla name w names:
            stubs = methodstubs.copy()
            usuń stubs[name]
            C = type('C', (abc,), stubs)
            self.assertRaises(TypeError, C, name)

    def validate_isinstance(self, abc, name):
        stub = lambda s, *args: 0

        C = type('C', (object,), {'__hash__': Nic})
        setattr(C, name, stub)
        self.assertIsInstance(C(), abc)
        self.assertPrawda(issubclass(C, abc))

        C = type('C', (object,), {'__hash__': Nic})
        self.assertNotIsInstance(C(), abc)
        self.assertNieprawda(issubclass(C, abc))

    def validate_comparison(self, instance):
        ops = ['lt', 'gt', 'le', 'ge', 'ne', 'or', 'and', 'xor', 'sub']
        operators = {}
        dla op w ops:
            name = '__' + op + '__'
            operators[name] = getattr(operator, name)

        klasa Other:
            def __init__(self):
                self.right_side = Nieprawda
            def __eq__(self, other):
                self.right_side = Prawda
                zwróć Prawda
            __lt__ = __eq__
            __gt__ = __eq__
            __le__ = __eq__
            __ge__ = __eq__
            __ne__ = __eq__
            __ror__ = __eq__
            __rand__ = __eq__
            __rxor__ = __eq__
            __rsub__ = __eq__

        dla name, op w operators.items():
            jeżeli nie hasattr(instance, name):
                kontynuuj
            other = Other()
            op(instance, other)
            self.assertPrawda(other.right_side,'Right side nie called dla %s.%s'
                            % (type(instance), name))

klasa TestOneTrickPonyABCs(ABCTestCase):

    def test_Awaitable(self):
        def gen():
            uzyskaj

        @types.coroutine
        def coro():
            uzyskaj

        async def new_coro():
            dalej

        klasa Bar:
            def __await__(self):
                uzyskaj

        klasa MinimalCoro(Coroutine):
            def send(self, value):
                zwróć value
            def throw(self, typ, val=Nic, tb=Nic):
                super().throw(typ, val, tb)
            def __await__(self):
                uzyskaj

        non_samples = [Nic, int(), gen(), object()]
        dla x w non_samples:
            self.assertNotIsInstance(x, Awaitable)
            self.assertNieprawda(issubclass(type(x), Awaitable), repr(type(x)))

        samples = [Bar(), MinimalCoro()]
        dla x w samples:
            self.assertIsInstance(x, Awaitable)
            self.assertPrawda(issubclass(type(x), Awaitable))

        c = coro()
        # Iterable coroutines (generators przy CO_ITERABLE_COROUTINE
        # flag don't have '__await__' method, hence can't be instances
        # of Awaitable. Use inspect.isawaitable to detect them.
        self.assertNotIsInstance(c, Awaitable)

        c = new_coro()
        self.assertIsInstance(c, Awaitable)
        c.close() # awoid RuntimeWarning that coro() was nie awaited

        klasa CoroLike: dalej
        Coroutine.register(CoroLike)
        self.assertPrawda(isinstance(CoroLike(), Awaitable))
        self.assertPrawda(issubclass(CoroLike, Awaitable))
        CoroLike = Nic
        support.gc_collect() # Kill CoroLike to clean-up ABCMeta cache

    def test_Coroutine(self):
        def gen():
            uzyskaj

        @types.coroutine
        def coro():
            uzyskaj

        async def new_coro():
            dalej

        klasa Bar:
            def __await__(self):
                uzyskaj

        klasa MinimalCoro(Coroutine):
            def send(self, value):
                zwróć value
            def throw(self, typ, val=Nic, tb=Nic):
                super().throw(typ, val, tb)
            def __await__(self):
                uzyskaj

        non_samples = [Nic, int(), gen(), object(), Bar()]
        dla x w non_samples:
            self.assertNotIsInstance(x, Coroutine)
            self.assertNieprawda(issubclass(type(x), Coroutine), repr(type(x)))

        samples = [MinimalCoro()]
        dla x w samples:
            self.assertIsInstance(x, Awaitable)
            self.assertPrawda(issubclass(type(x), Awaitable))

        c = coro()
        # Iterable coroutines (generators przy CO_ITERABLE_COROUTINE
        # flag don't have '__await__' method, hence can't be instances
        # of Coroutine. Use inspect.isawaitable to detect them.
        self.assertNotIsInstance(c, Coroutine)

        c = new_coro()
        self.assertIsInstance(c, Coroutine)
        c.close() # awoid RuntimeWarning that coro() was nie awaited

        klasa CoroLike:
            def send(self, value):
                dalej
            def throw(self, typ, val=Nic, tb=Nic):
                dalej
            def close(self):
                dalej
            def __await__(self):
                dalej
        self.assertPrawda(isinstance(CoroLike(), Coroutine))
        self.assertPrawda(issubclass(CoroLike, Coroutine))

        klasa CoroLike:
            def send(self, value):
                dalej
            def close(self):
                dalej
            def __await__(self):
                dalej
        self.assertNieprawda(isinstance(CoroLike(), Coroutine))
        self.assertNieprawda(issubclass(CoroLike, Coroutine))

    def test_Hashable(self):
        # Check some non-hashables
        non_samples = [bytearray(), list(), set(), dict()]
        dla x w non_samples:
            self.assertNotIsInstance(x, Hashable)
            self.assertNieprawda(issubclass(type(x), Hashable), repr(type(x)))
        # Check some hashables
        samples = [Nic,
                   int(), float(), complex(),
                   str(),
                   tuple(), frozenset(),
                   int, list, object, type, bytes()
                   ]
        dla x w samples:
            self.assertIsInstance(x, Hashable)
            self.assertPrawda(issubclass(type(x), Hashable), repr(type(x)))
        self.assertRaises(TypeError, Hashable)
        # Check direct subclassing
        klasa H(Hashable):
            def __hash__(self):
                zwróć super().__hash__()
        self.assertEqual(hash(H()), 0)
        self.assertNieprawda(issubclass(int, H))
        self.validate_abstract_methods(Hashable, '__hash__')
        self.validate_isinstance(Hashable, '__hash__')

    def test_AsyncIterable(self):
        klasa AI:
            async def __aiter__(self):
                zwróć self
        self.assertPrawda(isinstance(AI(), AsyncIterable))
        self.assertPrawda(issubclass(AI, AsyncIterable))
        # Check some non-iterables
        non_samples = [Nic, object, []]
        dla x w non_samples:
            self.assertNotIsInstance(x, AsyncIterable)
            self.assertNieprawda(issubclass(type(x), AsyncIterable), repr(type(x)))
        self.validate_abstract_methods(AsyncIterable, '__aiter__')
        self.validate_isinstance(AsyncIterable, '__aiter__')

    def test_AsyncIterator(self):
        klasa AI:
            async def __aiter__(self):
                zwróć self
            async def __anext__(self):
                podnieś StopAsyncIteration
        self.assertPrawda(isinstance(AI(), AsyncIterator))
        self.assertPrawda(issubclass(AI, AsyncIterator))
        non_samples = [Nic, object, []]
        # Check some non-iterables
        dla x w non_samples:
            self.assertNotIsInstance(x, AsyncIterator)
            self.assertNieprawda(issubclass(type(x), AsyncIterator), repr(type(x)))
        # Similarly to regular iterators (see issue 10565)
        klasa AnextOnly:
            async def __anext__(self):
                podnieś StopAsyncIteration
        self.assertNotIsInstance(AnextOnly(), AsyncIterator)
        self.validate_abstract_methods(AsyncIterator, '__anext__', '__aiter__')

    def test_Iterable(self):
        # Check some non-iterables
        non_samples = [Nic, 42, 3.14, 1j]
        dla x w non_samples:
            self.assertNotIsInstance(x, Iterable)
            self.assertNieprawda(issubclass(type(x), Iterable), repr(type(x)))
        # Check some iterables
        samples = [bytes(), str(),
                   tuple(), list(), set(), frozenset(), dict(),
                   dict().keys(), dict().items(), dict().values(),
                   (lambda: (uzyskaj))(),
                   (x dla x w []),
                   ]
        dla x w samples:
            self.assertIsInstance(x, Iterable)
            self.assertPrawda(issubclass(type(x), Iterable), repr(type(x)))
        # Check direct subclassing
        klasa I(Iterable):
            def __iter__(self):
                zwróć super().__iter__()
        self.assertEqual(list(I()), [])
        self.assertNieprawda(issubclass(str, I))
        self.validate_abstract_methods(Iterable, '__iter__')
        self.validate_isinstance(Iterable, '__iter__')

    def test_Iterator(self):
        non_samples = [Nic, 42, 3.14, 1j, b"", "", (), [], {}, set()]
        dla x w non_samples:
            self.assertNotIsInstance(x, Iterator)
            self.assertNieprawda(issubclass(type(x), Iterator), repr(type(x)))
        samples = [iter(bytes()), iter(str()),
                   iter(tuple()), iter(list()), iter(dict()),
                   iter(set()), iter(frozenset()),
                   iter(dict().keys()), iter(dict().items()),
                   iter(dict().values()),
                   (lambda: (uzyskaj))(),
                   (x dla x w []),
                   ]
        dla x w samples:
            self.assertIsInstance(x, Iterator)
            self.assertPrawda(issubclass(type(x), Iterator), repr(type(x)))
        self.validate_abstract_methods(Iterator, '__next__', '__iter__')

        # Issue 10565
        klasa NextOnly:
            def __next__(self):
                uzyskaj 1
                zwróć
        self.assertNotIsInstance(NextOnly(), Iterator)

    def test_Generator(self):
        klasa NonGen1:
            def __iter__(self): zwróć self
            def __next__(self): zwróć Nic
            def close(self): dalej
            def throw(self, typ, val=Nic, tb=Nic): dalej

        klasa NonGen2:
            def __iter__(self): zwróć self
            def __next__(self): zwróć Nic
            def close(self): dalej
            def send(self, value): zwróć value

        klasa NonGen3:
            def close(self): dalej
            def send(self, value): zwróć value
            def throw(self, typ, val=Nic, tb=Nic): dalej

        non_samples = [
            Nic, 42, 3.14, 1j, b"", "", (), [], {}, set(),
            iter(()), iter([]), NonGen1(), NonGen2(), NonGen3()]
        dla x w non_samples:
            self.assertNotIsInstance(x, Generator)
            self.assertNieprawda(issubclass(type(x), Generator), repr(type(x)))

        klasa Gen:
            def __iter__(self): zwróć self
            def __next__(self): zwróć Nic
            def close(self): dalej
            def send(self, value): zwróć value
            def throw(self, typ, val=Nic, tb=Nic): dalej

        klasa MinimalGen(Generator):
            def send(self, value):
                zwróć value
            def throw(self, typ, val=Nic, tb=Nic):
                super().throw(typ, val, tb)

        def gen():
            uzyskaj 1

        samples = [gen(), (lambda: (uzyskaj))(), Gen(), MinimalGen()]
        dla x w samples:
            self.assertIsInstance(x, Iterator)
            self.assertIsInstance(x, Generator)
            self.assertPrawda(issubclass(type(x), Generator), repr(type(x)))
        self.validate_abstract_methods(Generator, 'send', 'throw')

        # mixin tests
        mgen = MinimalGen()
        self.assertIs(mgen, iter(mgen))
        self.assertIs(mgen.send(Nic), next(mgen))
        self.assertEqual(2, mgen.send(2))
        self.assertIsNic(mgen.close())
        self.assertRaises(ValueError, mgen.throw, ValueError)
        self.assertRaisesRegex(ValueError, "^huhu$",
                               mgen.throw, ValueError, ValueError("huhu"))
        self.assertRaises(StopIteration, mgen.throw, StopIteration())

        klasa FailOnClose(Generator):
            def send(self, value): zwróć value
            def throw(self, *args): podnieś ValueError

        self.assertRaises(ValueError, FailOnClose().close)

        klasa IgnoreGeneratorExit(Generator):
            def send(self, value): zwróć value
            def throw(self, *args): dalej

        self.assertRaises(RuntimeError, IgnoreGeneratorExit().close)

    def test_Sized(self):
        non_samples = [Nic, 42, 3.14, 1j,
                       (lambda: (uzyskaj))(),
                       (x dla x w []),
                       ]
        dla x w non_samples:
            self.assertNotIsInstance(x, Sized)
            self.assertNieprawda(issubclass(type(x), Sized), repr(type(x)))
        samples = [bytes(), str(),
                   tuple(), list(), set(), frozenset(), dict(),
                   dict().keys(), dict().items(), dict().values(),
                   ]
        dla x w samples:
            self.assertIsInstance(x, Sized)
            self.assertPrawda(issubclass(type(x), Sized), repr(type(x)))
        self.validate_abstract_methods(Sized, '__len__')
        self.validate_isinstance(Sized, '__len__')

    def test_Container(self):
        non_samples = [Nic, 42, 3.14, 1j,
                       (lambda: (uzyskaj))(),
                       (x dla x w []),
                       ]
        dla x w non_samples:
            self.assertNotIsInstance(x, Container)
            self.assertNieprawda(issubclass(type(x), Container), repr(type(x)))
        samples = [bytes(), str(),
                   tuple(), list(), set(), frozenset(), dict(),
                   dict().keys(), dict().items(),
                   ]
        dla x w samples:
            self.assertIsInstance(x, Container)
            self.assertPrawda(issubclass(type(x), Container), repr(type(x)))
        self.validate_abstract_methods(Container, '__contains__')
        self.validate_isinstance(Container, '__contains__')

    def test_Callable(self):
        non_samples = [Nic, 42, 3.14, 1j,
                       "", b"", (), [], {}, set(),
                       (lambda: (uzyskaj))(),
                       (x dla x w []),
                       ]
        dla x w non_samples:
            self.assertNotIsInstance(x, Callable)
            self.assertNieprawda(issubclass(type(x), Callable), repr(type(x)))
        samples = [lambda: Nic,
                   type, int, object,
                   len,
                   list.append, [].append,
                   ]
        dla x w samples:
            self.assertIsInstance(x, Callable)
            self.assertPrawda(issubclass(type(x), Callable), repr(type(x)))
        self.validate_abstract_methods(Callable, '__call__')
        self.validate_isinstance(Callable, '__call__')

    def test_direct_subclassing(self):
        dla B w Hashable, Iterable, Iterator, Sized, Container, Callable:
            klasa C(B):
                dalej
            self.assertPrawda(issubclass(C, B))
            self.assertNieprawda(issubclass(int, C))

    def test_registration(self):
        dla B w Hashable, Iterable, Iterator, Sized, Container, Callable:
            klasa C:
                __hash__ = Nic  # Make sure it isn't hashable by default
            self.assertNieprawda(issubclass(C, B), B.__name__)
            B.register(C)
            self.assertPrawda(issubclass(C, B))

klasa WithSet(MutableSet):

    def __init__(self, it=()):
        self.data = set(it)

    def __len__(self):
        zwróć len(self.data)

    def __iter__(self):
        zwróć iter(self.data)

    def __contains__(self, item):
        zwróć item w self.data

    def add(self, item):
        self.data.add(item)

    def discard(self, item):
        self.data.discard(item)

klasa TestCollectionABCs(ABCTestCase):

    # XXX For now, we only test some virtual inheritance properties.
    # We should also test the proper behavior of the collection ABCs
    # jako real base classes albo mix-in classes.

    def test_Set(self):
        dla sample w [set, frozenset]:
            self.assertIsInstance(sample(), Set)
            self.assertPrawda(issubclass(sample, Set))
        self.validate_abstract_methods(Set, '__contains__', '__iter__', '__len__')
        klasa MySet(Set):
            def __contains__(self, x):
                zwróć Nieprawda
            def __len__(self):
                zwróć 0
            def __iter__(self):
                zwróć iter([])
        self.validate_comparison(MySet())

    def test_hash_Set(self):
        klasa OneTwoThreeSet(Set):
            def __init__(self):
                self.contents = [1, 2, 3]
            def __contains__(self, x):
                zwróć x w self.contents
            def __len__(self):
                zwróć len(self.contents)
            def __iter__(self):
                zwróć iter(self.contents)
            def __hash__(self):
                zwróć self._hash()
        a, b = OneTwoThreeSet(), OneTwoThreeSet()
        self.assertPrawda(hash(a) == hash(b))

    def test_isdisjoint_Set(self):
        klasa MySet(Set):
            def __init__(self, itr):
                self.contents = itr
            def __contains__(self, x):
                zwróć x w self.contents
            def __iter__(self):
                zwróć iter(self.contents)
            def __len__(self):
                zwróć len([x dla x w self.contents])
        s1 = MySet((1, 2, 3))
        s2 = MySet((4, 5, 6))
        s3 = MySet((1, 5, 6))
        self.assertPrawda(s1.isdisjoint(s2))
        self.assertNieprawda(s1.isdisjoint(s3))

    def test_equality_Set(self):
        klasa MySet(Set):
            def __init__(self, itr):
                self.contents = itr
            def __contains__(self, x):
                zwróć x w self.contents
            def __iter__(self):
                zwróć iter(self.contents)
            def __len__(self):
                zwróć len([x dla x w self.contents])
        s1 = MySet((1,))
        s2 = MySet((1, 2))
        s3 = MySet((3, 4))
        s4 = MySet((3, 4))
        self.assertPrawda(s2 > s1)
        self.assertPrawda(s1 < s2)
        self.assertNieprawda(s2 <= s1)
        self.assertNieprawda(s2 <= s3)
        self.assertNieprawda(s1 >= s2)
        self.assertEqual(s3, s4)
        self.assertNotEqual(s2, s3)

    def test_arithmetic_Set(self):
        klasa MySet(Set):
            def __init__(self, itr):
                self.contents = itr
            def __contains__(self, x):
                zwróć x w self.contents
            def __iter__(self):
                zwróć iter(self.contents)
            def __len__(self):
                zwróć len([x dla x w self.contents])
        s1 = MySet((1, 2, 3))
        s2 = MySet((3, 4, 5))
        s3 = s1 & s2
        self.assertEqual(s3, MySet((3,)))

    def test_MutableSet(self):
        self.assertIsInstance(set(), MutableSet)
        self.assertPrawda(issubclass(set, MutableSet))
        self.assertNotIsInstance(frozenset(), MutableSet)
        self.assertNieprawda(issubclass(frozenset, MutableSet))
        self.validate_abstract_methods(MutableSet, '__contains__', '__iter__', '__len__',
            'add', 'discard')

    def test_issue_5647(self):
        # MutableSet.__iand__ mutated the set during iteration
        s = WithSet('abcd')
        s &= WithSet('cdef')            # This used to fail
        self.assertEqual(set(s), set('cd'))

    def test_issue_4920(self):
        # MutableSet.pop() method did nie work
        klasa MySet(MutableSet):
            __slots__=['__s']
            def __init__(self,items=Nic):
                jeżeli items jest Nic:
                    items=[]
                self.__s=set(items)
            def __contains__(self,v):
                zwróć v w self.__s
            def __iter__(self):
                zwróć iter(self.__s)
            def __len__(self):
                zwróć len(self.__s)
            def add(self,v):
                result=v nie w self.__s
                self.__s.add(v)
                zwróć result
            def discard(self,v):
                result=v w self.__s
                self.__s.discard(v)
                zwróć result
            def __repr__(self):
                zwróć "MySet(%s)" % repr(list(self))
        s = MySet([5,43,2,1])
        self.assertEqual(s.pop(), 1)

    def test_issue8750(self):
        empty = WithSet()
        full = WithSet(range(10))
        s = WithSet(full)
        s -= s
        self.assertEqual(s, empty)
        s = WithSet(full)
        s ^= s
        self.assertEqual(s, empty)
        s = WithSet(full)
        s &= s
        self.assertEqual(s, full)
        s |= s
        self.assertEqual(s, full)

    def test_issue16373(self):
        # Recursion error comparing comparable oraz noncomparable
        # Set instances
        klasa MyComparableSet(Set):
            def __contains__(self, x):
                zwróć Nieprawda
            def __len__(self):
                zwróć 0
            def __iter__(self):
                zwróć iter([])
        klasa MyNonComparableSet(Set):
            def __contains__(self, x):
                zwróć Nieprawda
            def __len__(self):
                zwróć 0
            def __iter__(self):
                zwróć iter([])
            def __le__(self, x):
                zwróć NotImplemented
            def __lt__(self, x):
                zwróć NotImplemented

        cs = MyComparableSet()
        ncs = MyNonComparableSet()
        self.assertNieprawda(ncs < cs)
        self.assertPrawda(ncs <= cs)
        self.assertNieprawda(ncs > cs)
        self.assertPrawda(ncs >= cs)

    def assertSameSet(self, s1, s2):
        # coerce both to a real set then check equality
        self.assertSetEqual(set(s1), set(s2))

    def test_Set_interoperability_with_real_sets(self):
        # Issue: 8743
        klasa ListSet(Set):
            def __init__(self, elements=()):
                self.data = []
                dla elem w elements:
                    jeżeli elem nie w self.data:
                        self.data.append(elem)
            def __contains__(self, elem):
                zwróć elem w self.data
            def __iter__(self):
                zwróć iter(self.data)
            def __len__(self):
                zwróć len(self.data)
            def __repr__(self):
                zwróć 'Set({!r})'.format(self.data)

        r1 = set('abc')
        r2 = set('bcd')
        r3 = set('abcde')
        f1 = ListSet('abc')
        f2 = ListSet('bcd')
        f3 = ListSet('abcde')
        l1 = list('abccba')
        l2 = list('bcddcb')
        l3 = list('abcdeedcba')

        target = r1 & r2
        self.assertSameSet(f1 & f2, target)
        self.assertSameSet(f1 & r2, target)
        self.assertSameSet(r2 & f1, target)
        self.assertSameSet(f1 & l2, target)

        target = r1 | r2
        self.assertSameSet(f1 | f2, target)
        self.assertSameSet(f1 | r2, target)
        self.assertSameSet(r2 | f1, target)
        self.assertSameSet(f1 | l2, target)

        fwd_target = r1 - r2
        rev_target = r2 - r1
        self.assertSameSet(f1 - f2, fwd_target)
        self.assertSameSet(f2 - f1, rev_target)
        self.assertSameSet(f1 - r2, fwd_target)
        self.assertSameSet(f2 - r1, rev_target)
        self.assertSameSet(r1 - f2, fwd_target)
        self.assertSameSet(r2 - f1, rev_target)
        self.assertSameSet(f1 - l2, fwd_target)
        self.assertSameSet(f2 - l1, rev_target)

        target = r1 ^ r2
        self.assertSameSet(f1 ^ f2, target)
        self.assertSameSet(f1 ^ r2, target)
        self.assertSameSet(r2 ^ f1, target)
        self.assertSameSet(f1 ^ l2, target)

        # Don't change the following to use assertLess albo other
        # "more specific" unittest assertions.  The current
        # assertPrawda/assertNieprawda style makes the pattern of test
        # case combinations clear oraz allows us to know dla sure
        # the exact operator being invoked.

        # proper subset
        self.assertPrawda(f1 < f3)
        self.assertNieprawda(f1 < f1)
        self.assertNieprawda(f1 < f2)
        self.assertPrawda(r1 < f3)
        self.assertNieprawda(r1 < f1)
        self.assertNieprawda(r1 < f2)
        self.assertPrawda(r1 < r3)
        self.assertNieprawda(r1 < r1)
        self.assertNieprawda(r1 < r2)
        przy self.assertRaises(TypeError):
            f1 < l3
        przy self.assertRaises(TypeError):
            f1 < l1
        przy self.assertRaises(TypeError):
            f1 < l2

        # any subset
        self.assertPrawda(f1 <= f3)
        self.assertPrawda(f1 <= f1)
        self.assertNieprawda(f1 <= f2)
        self.assertPrawda(r1 <= f3)
        self.assertPrawda(r1 <= f1)
        self.assertNieprawda(r1 <= f2)
        self.assertPrawda(r1 <= r3)
        self.assertPrawda(r1 <= r1)
        self.assertNieprawda(r1 <= r2)
        przy self.assertRaises(TypeError):
            f1 <= l3
        przy self.assertRaises(TypeError):
            f1 <= l1
        przy self.assertRaises(TypeError):
            f1 <= l2

        # proper superset
        self.assertPrawda(f3 > f1)
        self.assertNieprawda(f1 > f1)
        self.assertNieprawda(f2 > f1)
        self.assertPrawda(r3 > r1)
        self.assertNieprawda(f1 > r1)
        self.assertNieprawda(f2 > r1)
        self.assertPrawda(r3 > r1)
        self.assertNieprawda(r1 > r1)
        self.assertNieprawda(r2 > r1)
        przy self.assertRaises(TypeError):
            f1 > l3
        przy self.assertRaises(TypeError):
            f1 > l1
        przy self.assertRaises(TypeError):
            f1 > l2

        # any superset
        self.assertPrawda(f3 >= f1)
        self.assertPrawda(f1 >= f1)
        self.assertNieprawda(f2 >= f1)
        self.assertPrawda(r3 >= r1)
        self.assertPrawda(f1 >= r1)
        self.assertNieprawda(f2 >= r1)
        self.assertPrawda(r3 >= r1)
        self.assertPrawda(r1 >= r1)
        self.assertNieprawda(r2 >= r1)
        przy self.assertRaises(TypeError):
            f1 >= l3
        przy self.assertRaises(TypeError):
            f1 >=l1
        przy self.assertRaises(TypeError):
            f1 >= l2

        # equality
        self.assertPrawda(f1 == f1)
        self.assertPrawda(r1 == f1)
        self.assertPrawda(f1 == r1)
        self.assertNieprawda(f1 == f3)
        self.assertNieprawda(r1 == f3)
        self.assertNieprawda(f1 == r3)
        self.assertNieprawda(f1 == l3)
        self.assertNieprawda(f1 == l1)
        self.assertNieprawda(f1 == l2)

        # inequality
        self.assertNieprawda(f1 != f1)
        self.assertNieprawda(r1 != f1)
        self.assertNieprawda(f1 != r1)
        self.assertPrawda(f1 != f3)
        self.assertPrawda(r1 != f3)
        self.assertPrawda(f1 != r3)
        self.assertPrawda(f1 != l3)
        self.assertPrawda(f1 != l1)
        self.assertPrawda(f1 != l2)

    def test_Mapping(self):
        dla sample w [dict]:
            self.assertIsInstance(sample(), Mapping)
            self.assertPrawda(issubclass(sample, Mapping))
        self.validate_abstract_methods(Mapping, '__contains__', '__iter__', '__len__',
            '__getitem__')
        klasa MyMapping(Mapping):
            def __len__(self):
                zwróć 0
            def __getitem__(self, i):
                podnieś IndexError
            def __iter__(self):
                zwróć iter(())
        self.validate_comparison(MyMapping())

    def test_MutableMapping(self):
        dla sample w [dict]:
            self.assertIsInstance(sample(), MutableMapping)
            self.assertPrawda(issubclass(sample, MutableMapping))
        self.validate_abstract_methods(MutableMapping, '__contains__', '__iter__', '__len__',
            '__getitem__', '__setitem__', '__delitem__')

    def test_MutableMapping_subclass(self):
        # Test issue 9214
        mymap = UserDict()
        mymap['red'] = 5
        self.assertIsInstance(mymap.keys(), Set)
        self.assertIsInstance(mymap.keys(), KeysView)
        self.assertIsInstance(mymap.items(), Set)
        self.assertIsInstance(mymap.items(), ItemsView)

        mymap = UserDict()
        mymap['red'] = 5
        z = mymap.keys() | {'orange'}
        self.assertIsInstance(z, set)
        list(z)
        mymap['blue'] = 7               # Shouldn't affect 'z'
        self.assertEqual(sorted(z), ['orange', 'red'])

        mymap = UserDict()
        mymap['red'] = 5
        z = mymap.items() | {('orange', 3)}
        self.assertIsInstance(z, set)
        list(z)
        mymap['blue'] = 7               # Shouldn't affect 'z'
        self.assertEqual(sorted(z), [('orange', 3), ('red', 5)])

    def test_Sequence(self):
        dla sample w [tuple, list, bytes, str]:
            self.assertIsInstance(sample(), Sequence)
            self.assertPrawda(issubclass(sample, Sequence))
        self.assertIsInstance(range(10), Sequence)
        self.assertPrawda(issubclass(range, Sequence))
        self.assertIsInstance(memoryview(b""), Sequence)
        self.assertPrawda(issubclass(memoryview, Sequence))
        self.assertPrawda(issubclass(str, Sequence))
        self.validate_abstract_methods(Sequence, '__contains__', '__iter__', '__len__',
            '__getitem__')

    def test_Sequence_mixins(self):
        klasa SequenceSubclass(Sequence):
            def __init__(self, seq=()):
                self.seq = seq

            def __getitem__(self, index):
                zwróć self.seq[index]

            def __len__(self):
                zwróć len(self.seq)

        # Compare Sequence.index() behavior to (list|str).index() behavior
        def assert_index_same(seq1, seq2, index_args):
            spróbuj:
                expected = seq1.index(*index_args)
            wyjąwszy ValueError:
                przy self.assertRaises(ValueError):
                    seq2.index(*index_args)
            inaczej:
                actual = seq2.index(*index_args)
                self.assertEqual(
                    actual, expected, '%r.index%s' % (seq1, index_args))

        dla ty w list, str:
            nativeseq = ty('abracadabra')
            indexes = [-10000, -9999] + list(range(-3, len(nativeseq) + 3))
            seqseq = SequenceSubclass(nativeseq)
            dla letter w set(nativeseq) | {'z'}:
                assert_index_same(nativeseq, seqseq, (letter,))
                dla start w range(-3, len(nativeseq) + 3):
                    assert_index_same(nativeseq, seqseq, (letter, start))
                    dla stop w range(-3, len(nativeseq) + 3):
                        assert_index_same(
                            nativeseq, seqseq, (letter, start, stop))

    def test_ByteString(self):
        dla sample w [bytes, bytearray]:
            self.assertIsInstance(sample(), ByteString)
            self.assertPrawda(issubclass(sample, ByteString))
        dla sample w [str, list, tuple]:
            self.assertNotIsInstance(sample(), ByteString)
            self.assertNieprawda(issubclass(sample, ByteString))
        self.assertNotIsInstance(memoryview(b""), ByteString)
        self.assertNieprawda(issubclass(memoryview, ByteString))

    def test_MutableSequence(self):
        dla sample w [tuple, str, bytes]:
            self.assertNotIsInstance(sample(), MutableSequence)
            self.assertNieprawda(issubclass(sample, MutableSequence))
        dla sample w [list, bytearray, deque]:
            self.assertIsInstance(sample(), MutableSequence)
            self.assertPrawda(issubclass(sample, MutableSequence))
        self.assertNieprawda(issubclass(str, MutableSequence))
        self.validate_abstract_methods(MutableSequence, '__contains__', '__iter__',
            '__len__', '__getitem__', '__setitem__', '__delitem__', 'insert')

    def test_MutableSequence_mixins(self):
        # Test the mixins of MutableSequence by creating a miminal concrete
        # klasa inherited z it.
        klasa MutableSequenceSubclass(MutableSequence):
            def __init__(self):
                self.lst = []

            def __setitem__(self, index, value):
                self.lst[index] = value

            def __getitem__(self, index):
                zwróć self.lst[index]

            def __len__(self):
                zwróć len(self.lst)

            def __delitem__(self, index):
                usuń self.lst[index]

            def insert(self, index, value):
                self.lst.insert(index, value)

        mss = MutableSequenceSubclass()
        mss.append(0)
        mss.extend((1, 2, 3, 4))
        self.assertEqual(len(mss), 5)
        self.assertEqual(mss[3], 3)
        mss.reverse()
        self.assertEqual(mss[3], 1)
        mss.pop()
        self.assertEqual(len(mss), 4)
        mss.remove(3)
        self.assertEqual(len(mss), 3)
        mss += (10, 20, 30)
        self.assertEqual(len(mss), 6)
        self.assertEqual(mss[-1], 30)
        mss.clear()
        self.assertEqual(len(mss), 0)

################################################################################
### Counter
################################################################################

klasa CounterSubclassWithSetItem(Counter):
    # Test a counter subclass that overrides __setitem__
    def __init__(self, *args, **kwds):
        self.called = Nieprawda
        Counter.__init__(self, *args, **kwds)
    def __setitem__(self, key, value):
        self.called = Prawda
        Counter.__setitem__(self, key, value)

klasa CounterSubclassWithGet(Counter):
    # Test a counter subclass that overrides get()
    def __init__(self, *args, **kwds):
        self.called = Nieprawda
        Counter.__init__(self, *args, **kwds)
    def get(self, key, default):
        self.called = Prawda
        zwróć Counter.get(self, key, default)

klasa TestCounter(unittest.TestCase):

    def test_basics(self):
        c = Counter('abcaba')
        self.assertEqual(c, Counter({'a':3 , 'b': 2, 'c': 1}))
        self.assertEqual(c, Counter(a=3, b=2, c=1))
        self.assertIsInstance(c, dict)
        self.assertIsInstance(c, Mapping)
        self.assertPrawda(issubclass(Counter, dict))
        self.assertPrawda(issubclass(Counter, Mapping))
        self.assertEqual(len(c), 3)
        self.assertEqual(sum(c.values()), 6)
        self.assertEqual(sorted(c.values()), [1, 2, 3])
        self.assertEqual(sorted(c.keys()), ['a', 'b', 'c'])
        self.assertEqual(sorted(c), ['a', 'b', 'c'])
        self.assertEqual(sorted(c.items()),
                         [('a', 3), ('b', 2), ('c', 1)])
        self.assertEqual(c['b'], 2)
        self.assertEqual(c['z'], 0)
        self.assertEqual(c.__contains__('c'), Prawda)
        self.assertEqual(c.__contains__('z'), Nieprawda)
        self.assertEqual(c.get('b', 10), 2)
        self.assertEqual(c.get('z', 10), 10)
        self.assertEqual(c, dict(a=3, b=2, c=1))
        self.assertEqual(repr(c), "Counter({'a': 3, 'b': 2, 'c': 1})")
        self.assertEqual(c.most_common(), [('a', 3), ('b', 2), ('c', 1)])
        dla i w range(5):
            self.assertEqual(c.most_common(i),
                             [('a', 3), ('b', 2), ('c', 1)][:i])
        self.assertEqual(''.join(sorted(c.elements())), 'aaabbc')
        c['a'] += 1         # increment an existing value
        c['b'] -= 2         # sub existing value to zero
        usuń c['c']          # remove an entry
        usuń c['c']          # make sure that usuń doesn't podnieś KeyError
        c['d'] -= 2         # sub z a missing value
        c['e'] = -5         # directly assign a missing value
        c['f'] += 4         # add to a missing value
        self.assertEqual(c, dict(a=4, b=0, d=-2, e=-5, f=4))
        self.assertEqual(''.join(sorted(c.elements())), 'aaaaffff')
        self.assertEqual(c.pop('f'), 4)
        self.assertNotIn('f', c)
        dla i w range(3):
            elem, cnt = c.popitem()
            self.assertNotIn(elem, c)
        c.clear()
        self.assertEqual(c, {})
        self.assertEqual(repr(c), 'Counter()')
        self.assertRaises(NotImplementedError, Counter.fromkeys, 'abc')
        self.assertRaises(TypeError, hash, c)
        c.update(dict(a=5, b=3))
        c.update(c=1)
        c.update(Counter('a' * 50 + 'b' * 30))
        c.update()          # test case przy no args
        c.__init__('a' * 500 + 'b' * 300)
        c.__init__('cdc')
        c.__init__()
        self.assertEqual(c, dict(a=555, b=333, c=3, d=1))
        self.assertEqual(c.setdefault('d', 5), 1)
        self.assertEqual(c['d'], 1)
        self.assertEqual(c.setdefault('e', 5), 5)
        self.assertEqual(c['e'], 5)

    def test_init(self):
        self.assertEqual(list(Counter(self=42).items()), [('self', 42)])
        self.assertEqual(list(Counter(iterable=42).items()), [('iterable', 42)])
        self.assertEqual(list(Counter(iterable=Nic).items()), [('iterable', Nic)])
        self.assertRaises(TypeError, Counter, 42)
        self.assertRaises(TypeError, Counter, (), ())
        self.assertRaises(TypeError, Counter.__init__)

    def test_update(self):
        c = Counter()
        c.update(self=42)
        self.assertEqual(list(c.items()), [('self', 42)])
        c = Counter()
        c.update(iterable=42)
        self.assertEqual(list(c.items()), [('iterable', 42)])
        c = Counter()
        c.update(iterable=Nic)
        self.assertEqual(list(c.items()), [('iterable', Nic)])
        self.assertRaises(TypeError, Counter().update, 42)
        self.assertRaises(TypeError, Counter().update, {}, {})
        self.assertRaises(TypeError, Counter.update)

    def test_copying(self):
        # Check that counters are copyable, deepcopyable, picklable, oraz
        #have a repr/eval round-trip
        words = Counter('which witch had which witches wrist watch'.split())
        def check(dup):
            msg = "\ncopy: %s\nwords: %s" % (dup, words)
            self.assertIsNot(dup, words, msg)
            self.assertEqual(dup, words)
        check(words.copy())
        check(copy.copy(words))
        check(copy.deepcopy(words))
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            przy self.subTest(proto=proto):
                check(pickle.loads(pickle.dumps(words, proto)))
        check(eval(repr(words)))
        update_test = Counter()
        update_test.update(words)
        check(update_test)
        check(Counter(words))

    def test_copy_subclass(self):
        klasa MyCounter(Counter):
            dalej
        c = MyCounter('slartibartfast')
        d = c.copy()
        self.assertEqual(d, c)
        self.assertEqual(len(d), len(c))
        self.assertEqual(type(d), type(c))

    def test_conversions(self):
        # Convert to: set, list, dict
        s = 'she sells sea shells by the sea shore'
        self.assertEqual(sorted(Counter(s).elements()), sorted(s))
        self.assertEqual(sorted(Counter(s)), sorted(set(s)))
        self.assertEqual(dict(Counter(s)), dict(Counter(s).items()))
        self.assertEqual(set(Counter(s)), set(s))

    def test_invariant_for_the_in_operator(self):
        c = Counter(a=10, b=-2, c=0)
        dla elem w c:
            self.assertPrawda(elem w c)
            self.assertIn(elem, c)

    def test_multiset_operations(self):
        # Verify that adding a zero counter will strip zeros oraz negatives
        c = Counter(a=10, b=-2, c=0) + Counter()
        self.assertEqual(dict(c), dict(a=10))

        elements = 'abcd'
        dla i w range(1000):
            # test random pairs of multisets
            p = Counter(dict((elem, randrange(-2,4)) dla elem w elements))
            p.update(e=1, f=-1, g=0)
            q = Counter(dict((elem, randrange(-2,4)) dla elem w elements))
            q.update(h=1, i=-1, j=0)
            dla counterop, numberop w [
                (Counter.__add__, lambda x, y: max(0, x+y)),
                (Counter.__sub__, lambda x, y: max(0, x-y)),
                (Counter.__or__, lambda x, y: max(0,x,y)),
                (Counter.__and__, lambda x, y: max(0, min(x,y))),
            ]:
                result = counterop(p, q)
                dla x w elements:
                    self.assertEqual(numberop(p[x], q[x]), result[x],
                                     (counterop, x, p, q))
                # verify that results exclude non-positive counts
                self.assertPrawda(x>0 dla x w result.values())

        elements = 'abcdef'
        dla i w range(100):
            # verify that random multisets przy no repeats are exactly like sets
            p = Counter(dict((elem, randrange(0, 2)) dla elem w elements))
            q = Counter(dict((elem, randrange(0, 2)) dla elem w elements))
            dla counterop, setop w [
                (Counter.__sub__, set.__sub__),
                (Counter.__or__, set.__or__),
                (Counter.__and__, set.__and__),
            ]:
                counter_result = counterop(p, q)
                set_result = setop(set(p.elements()), set(q.elements()))
                self.assertEqual(counter_result, dict.fromkeys(set_result, 1))

    def test_inplace_operations(self):
        elements = 'abcd'
        dla i w range(1000):
            # test random pairs of multisets
            p = Counter(dict((elem, randrange(-2,4)) dla elem w elements))
            p.update(e=1, f=-1, g=0)
            q = Counter(dict((elem, randrange(-2,4)) dla elem w elements))
            q.update(h=1, i=-1, j=0)
            dla inplace_op, regular_op w [
                (Counter.__iadd__, Counter.__add__),
                (Counter.__isub__, Counter.__sub__),
                (Counter.__ior__, Counter.__or__),
                (Counter.__iand__, Counter.__and__),
            ]:
                c = p.copy()
                c_id = id(c)
                regular_result = regular_op(c, q)
                inplace_result = inplace_op(c, q)
                self.assertEqual(inplace_result, regular_result)
                self.assertEqual(id(inplace_result), c_id)

    def test_subtract(self):
        c = Counter(a=-5, b=0, c=5, d=10, e=15,g=40)
        c.subtract(a=1, b=2, c=-3, d=10, e=20, f=30, h=-50)
        self.assertEqual(c, Counter(a=-6, b=-2, c=8, d=0, e=-5, f=-30, g=40, h=50))
        c = Counter(a=-5, b=0, c=5, d=10, e=15,g=40)
        c.subtract(Counter(a=1, b=2, c=-3, d=10, e=20, f=30, h=-50))
        self.assertEqual(c, Counter(a=-6, b=-2, c=8, d=0, e=-5, f=-30, g=40, h=50))
        c = Counter('aaabbcd')
        c.subtract('aaaabbcce')
        self.assertEqual(c, Counter(a=-1, b=0, c=-1, d=1, e=-1))

        c = Counter()
        c.subtract(self=42)
        self.assertEqual(list(c.items()), [('self', -42)])
        c = Counter()
        c.subtract(iterable=42)
        self.assertEqual(list(c.items()), [('iterable', -42)])
        self.assertRaises(TypeError, Counter().subtract, 42)
        self.assertRaises(TypeError, Counter().subtract, {}, {})
        self.assertRaises(TypeError, Counter.subtract)

    def test_unary(self):
        c = Counter(a=-5, b=0, c=5, d=10, e=15,g=40)
        self.assertEqual(dict(+c), dict(c=5, d=10, e=15, g=40))
        self.assertEqual(dict(-c), dict(a=5))

    def test_repr_nonsortable(self):
        c = Counter(a=2, b=Nic)
        r = repr(c)
        self.assertIn("'a': 2", r)
        self.assertIn("'b': Nic", r)

    def test_helper_function(self):
        # two paths, one dla real dicts oraz one dla other mappings
        elems = list('abracadabra')

        d = dict()
        _count_elements(d, elems)
        self.assertEqual(d, {'a': 5, 'r': 2, 'b': 2, 'c': 1, 'd': 1})

        m = OrderedDict()
        _count_elements(m, elems)
        self.assertEqual(m,
             OrderedDict([('a', 5), ('b', 2), ('r', 2), ('c', 1), ('d', 1)]))

        # test fidelity to the pure python version
        c = CounterSubclassWithSetItem('abracadabra')
        self.assertPrawda(c.called)
        self.assertEqual(dict(c), {'a': 5, 'b': 2, 'c': 1, 'd': 1, 'r':2 })
        c = CounterSubclassWithGet('abracadabra')
        self.assertPrawda(c.called)
        self.assertEqual(dict(c), {'a': 5, 'b': 2, 'c': 1, 'd': 1, 'r':2 })


################################################################################
### OrderedDict
################################################################################

py_coll = import_fresh_module('collections', blocked=['_collections'])
c_coll = import_fresh_module('collections', fresh=['_collections'])


@contextlib.contextmanager
def replaced_module(name, replacement):
    original_module = sys.modules[name]
    sys.modules[name] = replacement
    spróbuj:
        uzyskaj
    w_końcu:
        sys.modules[name] = original_module


klasa OrderedDictTests:

    def test_init(self):
        OrderedDict = self.module.OrderedDict
        przy self.assertRaises(TypeError):
            OrderedDict([('a', 1), ('b', 2)], Nic)                                 # too many args
        pairs = [('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5)]
        self.assertEqual(sorted(OrderedDict(dict(pairs)).items()), pairs)           # dict input
        self.assertEqual(sorted(OrderedDict(**dict(pairs)).items()), pairs)         # kwds input
        self.assertEqual(list(OrderedDict(pairs).items()), pairs)                   # pairs input
        self.assertEqual(list(OrderedDict([('a', 1), ('b', 2), ('c', 9), ('d', 4)],
                                          c=3, e=5).items()), pairs)                # mixed input

        # make sure no positional args conflict przy possible kwdargs
        self.assertEqual(list(OrderedDict(self=42).items()), [('self', 42)])
        self.assertEqual(list(OrderedDict(other=42).items()), [('other', 42)])
        self.assertRaises(TypeError, OrderedDict, 42)
        self.assertRaises(TypeError, OrderedDict, (), ())
        self.assertRaises(TypeError, OrderedDict.__init__)

        # Make sure that direct calls to __init__ do nie clear previous contents
        d = OrderedDict([('a', 1), ('b', 2), ('c', 3), ('d', 44), ('e', 55)])
        d.__init__([('e', 5), ('f', 6)], g=7, d=4)
        self.assertEqual(list(d.items()),
            [('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5), ('f', 6), ('g', 7)])

    def test_update(self):
        OrderedDict = self.module.OrderedDict
        przy self.assertRaises(TypeError):
            OrderedDict().update([('a', 1), ('b', 2)], Nic)                        # too many args
        pairs = [('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5)]
        od = OrderedDict()
        od.update(dict(pairs))
        self.assertEqual(sorted(od.items()), pairs)                                 # dict input
        od = OrderedDict()
        od.update(**dict(pairs))
        self.assertEqual(sorted(od.items()), pairs)                                 # kwds input
        od = OrderedDict()
        od.update(pairs)
        self.assertEqual(list(od.items()), pairs)                                   # pairs input
        od = OrderedDict()
        od.update([('a', 1), ('b', 2), ('c', 9), ('d', 4)], c=3, e=5)
        self.assertEqual(list(od.items()), pairs)                                   # mixed input

        # Issue 9137: Named argument called 'other' albo 'self'
        # shouldn't be treated specially.
        od = OrderedDict()
        od.update(self=23)
        self.assertEqual(list(od.items()), [('self', 23)])
        od = OrderedDict()
        od.update(other={})
        self.assertEqual(list(od.items()), [('other', {})])
        od = OrderedDict()
        od.update(red=5, blue=6, other=7, self=8)
        self.assertEqual(sorted(list(od.items())),
                         [('blue', 6), ('other', 7), ('red', 5), ('self', 8)])

        # Make sure that direct calls to update do nie clear previous contents
        # add that updates items are nie moved to the end
        d = OrderedDict([('a', 1), ('b', 2), ('c', 3), ('d', 44), ('e', 55)])
        d.update([('e', 5), ('f', 6)], g=7, d=4)
        self.assertEqual(list(d.items()),
            [('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5), ('f', 6), ('g', 7)])

        self.assertRaises(TypeError, OrderedDict().update, 42)
        self.assertRaises(TypeError, OrderedDict().update, (), ())
        self.assertRaises(TypeError, OrderedDict.update)

        self.assertRaises(TypeError, OrderedDict().update, 42)
        self.assertRaises(TypeError, OrderedDict().update, (), ())
        self.assertRaises(TypeError, OrderedDict.update)

    def test_fromkeys(self):
        OrderedDict = self.module.OrderedDict
        od = OrderedDict.fromkeys('abc')
        self.assertEqual(list(od.items()), [(c, Nic) dla c w 'abc'])
        od = OrderedDict.fromkeys('abc', value=Nic)
        self.assertEqual(list(od.items()), [(c, Nic) dla c w 'abc'])
        od = OrderedDict.fromkeys('abc', value=0)
        self.assertEqual(list(od.items()), [(c, 0) dla c w 'abc'])

    def test_abc(self):
        OrderedDict = self.module.OrderedDict
        self.assertIsInstance(OrderedDict(), MutableMapping)
        self.assertPrawda(issubclass(OrderedDict, MutableMapping))

    def test_clear(self):
        OrderedDict = self.module.OrderedDict
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        self.assertEqual(len(od), len(pairs))
        od.clear()
        self.assertEqual(len(od), 0)

    def test_delitem(self):
        OrderedDict = self.module.OrderedDict
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        od = OrderedDict(pairs)
        usuń od['a']
        self.assertNotIn('a', od)
        przy self.assertRaises(KeyError):
            usuń od['a']
        self.assertEqual(list(od.items()), pairs[:2] + pairs[3:])

    def test_setitem(self):
        OrderedDict = self.module.OrderedDict
        od = OrderedDict([('d', 1), ('b', 2), ('c', 3), ('a', 4), ('e', 5)])
        od['c'] = 10           # existing element
        od['f'] = 20           # new element
        self.assertEqual(list(od.items()),
                         [('d', 1), ('b', 2), ('c', 10), ('a', 4), ('e', 5), ('f', 20)])

    def test_iterators(self):
        OrderedDict = self.module.OrderedDict
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        self.assertEqual(list(od), [t[0] dla t w pairs])
        self.assertEqual(list(od.keys()), [t[0] dla t w pairs])
        self.assertEqual(list(od.values()), [t[1] dla t w pairs])
        self.assertEqual(list(od.items()), pairs)
        self.assertEqual(list(reversed(od)),
                         [t[0] dla t w reversed(pairs)])
        self.assertEqual(list(reversed(od.keys())),
                         [t[0] dla t w reversed(pairs)])
        self.assertEqual(list(reversed(od.values())),
                         [t[1] dla t w reversed(pairs)])
        self.assertEqual(list(reversed(od.items())), list(reversed(pairs)))

    def test_detect_deletion_during_iteration(self):
        OrderedDict = self.module.OrderedDict
        od = OrderedDict.fromkeys('abc')
        it = iter(od)
        key = next(it)
        usuń od[key]
        przy self.assertRaises(Exception):
            # Note, the exact exception podnieśd jest nie guaranteed
            # The only guarantee that the next() will nie succeed
            next(it)

    def test_sorted_iterators(self):
        OrderedDict = self.module.OrderedDict
        przy self.assertRaises(TypeError):
            OrderedDict([('a', 1), ('b', 2)], Nic)
        pairs = [('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5)]
        od = OrderedDict(pairs)
        self.assertEqual(sorted(od), [t[0] dla t w pairs])
        self.assertEqual(sorted(od.keys()), [t[0] dla t w pairs])
        self.assertEqual(sorted(od.values()), [t[1] dla t w pairs])
        self.assertEqual(sorted(od.items()), pairs)
        self.assertEqual(sorted(reversed(od)),
                         sorted([t[0] dla t w reversed(pairs)]))

    def test_iterators_empty(self):
        OrderedDict = self.module.OrderedDict
        od = OrderedDict()
        empty = []
        self.assertEqual(list(od), empty)
        self.assertEqual(list(od.keys()), empty)
        self.assertEqual(list(od.values()), empty)
        self.assertEqual(list(od.items()), empty)
        self.assertEqual(list(reversed(od)), empty)
        self.assertEqual(list(reversed(od.keys())), empty)
        self.assertEqual(list(reversed(od.values())), empty)
        self.assertEqual(list(reversed(od.items())), empty)

    def test_popitem(self):
        OrderedDict = self.module.OrderedDict
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        dopóki pairs:
            self.assertEqual(od.popitem(), pairs.pop())
        przy self.assertRaises(KeyError):
            od.popitem()
        self.assertEqual(len(od), 0)

    def test_popitem_last(self):
        OrderedDict = self.module.OrderedDict
        pairs = [(i, i) dla i w range(30)]

        obj = OrderedDict(pairs)
        dla i w range(8):
            obj.popitem(Prawda)
        obj.popitem(Prawda)
        obj.popitem(last=Prawda)
        self.assertEqual(len(obj), 20)

    def test_pop(self):
        OrderedDict = self.module.OrderedDict
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        shuffle(pairs)
        dopóki pairs:
            k, v = pairs.pop()
            self.assertEqual(od.pop(k), v)
        przy self.assertRaises(KeyError):
            od.pop('xyz')
        self.assertEqual(len(od), 0)
        self.assertEqual(od.pop(k, 12345), 12345)

        # make sure pop still works when __missing__ jest defined
        klasa Missing(OrderedDict):
            def __missing__(self, key):
                zwróć 0
        m = Missing(a=1)
        self.assertEqual(m.pop('b', 5), 5)
        self.assertEqual(m.pop('a', 6), 1)
        self.assertEqual(m.pop('a', 6), 6)
        self.assertEqual(m.pop('a', default=6), 6)
        przy self.assertRaises(KeyError):
            m.pop('a')

    def test_equality(self):
        OrderedDict = self.module.OrderedDict
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od1 = OrderedDict(pairs)
        od2 = OrderedDict(pairs)
        self.assertEqual(od1, od2)          # same order implies equality
        pairs = pairs[2:] + pairs[:2]
        od2 = OrderedDict(pairs)
        self.assertNotEqual(od1, od2)       # different order implies inequality
        # comparison to regular dict jest nie order sensitive
        self.assertEqual(od1, dict(od2))
        self.assertEqual(dict(od2), od1)
        # different length implied inequality
        self.assertNotEqual(od1, OrderedDict(pairs[:-1]))

    def test_copying(self):
        OrderedDict = self.module.OrderedDict
        # Check that ordered dicts are copyable, deepcopyable, picklable,
        # oraz have a repr/eval round-trip
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        od = OrderedDict(pairs)
        def check(dup):
            msg = "\ncopy: %s\nod: %s" % (dup, od)
            self.assertIsNot(dup, od, msg)
            self.assertEqual(dup, od)
            self.assertEqual(list(dup.items()), list(od.items()))
            self.assertEqual(len(dup), len(od))
            self.assertEqual(type(dup), type(od))
        check(od.copy())
        check(copy.copy(od))
        check(copy.deepcopy(od))
        # pickle directly pulls the module, so we have to fake it
        przy replaced_module('collections', self.module):
            dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
                przy self.subTest(proto=proto):
                    check(pickle.loads(pickle.dumps(od, proto)))
        check(eval(repr(od)))
        update_test = OrderedDict()
        update_test.update(od)
        check(update_test)
        check(OrderedDict(od))

    def test_yaml_linkage(self):
        OrderedDict = self.module.OrderedDict
        # Verify that __reduce__ jest setup w a way that supports PyYAML's dump() feature.
        # In yaml, lists are native but tuples are not.
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        od = OrderedDict(pairs)
        # yaml.dump(od) -->
        # '!!python/object/apply:__main__.OrderedDict\n- - [a, 1]\n  - [b, 2]\n'
        self.assertPrawda(all(type(pair)==list dla pair w od.__reduce__()[1]))

    def test_reduce_not_too_fat(self):
        OrderedDict = self.module.OrderedDict
        # do nie save instance dictionary jeżeli nie needed
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        od = OrderedDict(pairs)
        self.assertIsNic(od.__reduce__()[2])
        od.x = 10
        self.assertIsNotNic(od.__reduce__()[2])

    def test_pickle_recursive(self):
        OrderedDict = self.module.OrderedDict
        od = OrderedDict()
        od[1] = od

        # pickle directly pulls the module, so we have to fake it
        przy replaced_module('collections', self.module):
            dla proto w range(-1, pickle.HIGHEST_PROTOCOL + 1):
                dup = pickle.loads(pickle.dumps(od, proto))
                self.assertIsNot(dup, od)
                self.assertEqual(list(dup.keys()), [1])
                self.assertIs(dup[1], dup)

    def test_repr(self):
        OrderedDict = self.module.OrderedDict
        od = OrderedDict([('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)])
        self.assertEqual(repr(od),
            "OrderedDict([('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)])")
        self.assertEqual(eval(repr(od)), od)
        self.assertEqual(repr(OrderedDict()), "OrderedDict()")

    def test_repr_recursive(self):
        OrderedDict = self.module.OrderedDict
        # See issue #9826
        od = OrderedDict.fromkeys('abc')
        od['x'] = od
        self.assertEqual(repr(od),
            "OrderedDict([('a', Nic), ('b', Nic), ('c', Nic), ('x', ...)])")

    def test_setdefault(self):
        OrderedDict = self.module.OrderedDict
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        pair_order = list(od.items())
        self.assertEqual(od.setdefault('a', 10), 3)
        # make sure order didn't change
        self.assertEqual(list(od.items()), pair_order)
        self.assertEqual(od.setdefault('x', 10), 10)
        # make sure 'x' jest added to the end
        self.assertEqual(list(od.items())[-1], ('x', 10))
        self.assertEqual(od.setdefault('g', default=9), 9)

        # make sure setdefault still works when __missing__ jest defined
        klasa Missing(OrderedDict):
            def __missing__(self, key):
                zwróć 0
        self.assertEqual(Missing().setdefault(5, 9), 9)

    def test_reinsert(self):
        OrderedDict = self.module.OrderedDict
        # Given insert a, insert b, delete a, re-insert a,
        # verify that a jest now later than b.
        od = OrderedDict()
        od['a'] = 1
        od['b'] = 2
        usuń od['a']
        self.assertEqual(list(od.items()), [('b', 2)])
        od['a'] = 1
        self.assertEqual(list(od.items()), [('b', 2), ('a', 1)])

    def test_move_to_end(self):
        OrderedDict = self.module.OrderedDict
        od = OrderedDict.fromkeys('abcde')
        self.assertEqual(list(od), list('abcde'))
        od.move_to_end('c')
        self.assertEqual(list(od), list('abdec'))
        od.move_to_end('c', 0)
        self.assertEqual(list(od), list('cabde'))
        od.move_to_end('c', 0)
        self.assertEqual(list(od), list('cabde'))
        od.move_to_end('e')
        self.assertEqual(list(od), list('cabde'))
        od.move_to_end('b', last=Nieprawda)
        self.assertEqual(list(od), list('bcade'))
        przy self.assertRaises(KeyError):
            od.move_to_end('x')
        przy self.assertRaises(KeyError):
            od.move_to_end('x', 0)

    def test_sizeof(self):
        OrderedDict = self.module.OrderedDict
        # Wimpy test: Just verify the reported size jest larger than a regular dict
        d = dict(a=1)
        od = OrderedDict(**d)
        self.assertGreater(sys.getsizeof(od), sys.getsizeof(d))

    def test_override_update(self):
        OrderedDict = self.module.OrderedDict
        # Verify that subclasses can override update() without przerwijing __init__()
        klasa MyOD(OrderedDict):
            def update(self, *args, **kwds):
                podnieś Exception()
        items = [('a', 1), ('c', 3), ('b', 2)]
        self.assertEqual(list(MyOD(items).items()), items)


klasa PurePythonOrderedDictTests(OrderedDictTests, unittest.TestCase):

    module = py_coll


@unittest.skipUnless(c_coll, 'requires the C version of the collections module')
klasa CPythonOrderedDictTests(OrderedDictTests, unittest.TestCase):

    module = c_coll

    def test_delitem_hash_collision(self):
        OrderedDict = self.module.OrderedDict

        klasa Key:
            def __init__(self, hash):
                self._hash = hash
                self.value = str(id(self))
            def __hash__(self):
                zwróć self._hash
            def __eq__(self, other):
                spróbuj:
                    zwróć self.value == other.value
                wyjąwszy AttributeError:
                    zwróć Nieprawda
            def __repr__(self):
                zwróć self.value

        def blocking_hash(hash):
            # See the collision-handling w lookdict (in Objects/dictobject.c).
            MINSIZE = 8
            i = (hash & MINSIZE-1)
            zwróć (i << 2) + i + hash + 1

        COLLIDING = 1

        key = Key(COLLIDING)
        colliding = Key(COLLIDING)
        blocking = Key(blocking_hash(COLLIDING))

        od = OrderedDict()
        od[key] = ...
        od[blocking] = ...
        od[colliding] = ...
        od['after'] = ...

        usuń od[blocking]
        usuń od[colliding]
        self.assertEqual(list(od.items()), [(key, ...), ('after', ...)])

    def test_key_change_during_iteration(self):
        OrderedDict = self.module.OrderedDict

        od = OrderedDict.fromkeys('abcde')
        self.assertEqual(list(od), list('abcde'))
        przy self.assertRaises(RuntimeError):
            dla i, k w enumerate(od):
                od.move_to_end(k)
                self.assertLess(i, 5)
        przy self.assertRaises(RuntimeError):
            dla k w od:
                od['f'] = Nic
        przy self.assertRaises(RuntimeError):
            dla k w od:
                usuń od['c']
        self.assertEqual(list(od), list('bdeaf'))

    def test_issue24347(self):
        OrderedDict = self.module.OrderedDict

        klasa Key:
            def __hash__(self):
                zwróć randrange(100000)

        od = OrderedDict()
        dla i w range(100):
            key = Key()
            od[key] = i

        # These should nie crash.
        przy self.assertRaises(KeyError):
            repr(od)
        przy self.assertRaises(KeyError):
            od.copy()

    def test_issue24348(self):
        OrderedDict = self.module.OrderedDict

        klasa Key:
            def __hash__(self):
                zwróć 1

        od = OrderedDict()
        od[Key()] = 0
        # This should nie crash.
        od.popitem()

    def test_issue24667(self):
        """
        dict resizes after a certain number of insertion operations,
        whether albo nie there were deletions that freed up slots w the
        hash table.  During fast node lookup, OrderedDict must correctly
        respond to all resizes, even jeżeli the current "size" jest the same
        jako the old one.  We verify that here by forcing a dict resize
        on a sparse odict oraz then perform an operation that should
        trigger an odict resize (e.g. popitem).  One key aspect here jest
        that we will keep the size of the odict the same at each popitem
        call.  This verifies that we handled the dict resize properly.
        """
        OrderedDict = self.module.OrderedDict

        od = OrderedDict()
        dla c0 w '0123456789ABCDEF':
            dla c1 w '0123456789ABCDEF':
                jeżeli len(od) == 4:
                    # This should nie podnieś a KeyError.
                    od.popitem(last=Nieprawda)
                key = c0 + c1
                od[key] = key


klasa PurePythonGeneralMappingTests(mapping_tests.BasicTestMappingProtocol):

    @classmethod
    def setUpClass(cls):
        cls.type2test = py_coll.OrderedDict

    def test_popitem(self):
        d = self._empty_mapping()
        self.assertRaises(KeyError, d.popitem)


@unittest.skipUnless(c_coll, 'requires the C version of the collections module')
klasa CPythonGeneralMappingTests(mapping_tests.BasicTestMappingProtocol):

    @classmethod
    def setUpClass(cls):
        cls.type2test = c_coll.OrderedDict

    def test_popitem(self):
        d = self._empty_mapping()
        self.assertRaises(KeyError, d.popitem)


klasa PurePythonSubclassMappingTests(mapping_tests.BasicTestMappingProtocol):

    @classmethod
    def setUpClass(cls):
        klasa MyOrderedDict(py_coll.OrderedDict):
            dalej
        cls.type2test = MyOrderedDict

    def test_popitem(self):
        d = self._empty_mapping()
        self.assertRaises(KeyError, d.popitem)


@unittest.skipUnless(c_coll, 'requires the C version of the collections module')
klasa CPythonSubclassMappingTests(mapping_tests.BasicTestMappingProtocol):

    @classmethod
    def setUpClass(cls):
        klasa MyOrderedDict(c_coll.OrderedDict):
            dalej
        cls.type2test = MyOrderedDict

    def test_popitem(self):
        d = self._empty_mapping()
        self.assertRaises(KeyError, d.popitem)


################################################################################
### Run tests
################################################################################

zaimportuj doctest, collections

def test_main(verbose=Nic):
    NamedTupleDocs = doctest.DocTestSuite(module=collections)
    test_classes = [TestNamedTuple, NamedTupleDocs, TestOneTrickPonyABCs,
                    TestCollectionABCs, TestCounter, TestChainMap,
                    PurePythonOrderedDictTests, CPythonOrderedDictTests,
                    PurePythonGeneralMappingTests, CPythonGeneralMappingTests,
                    PurePythonSubclassMappingTests, CPythonSubclassMappingTests,
                    TestUserObjects,
                    ]
    support.run_unittest(*test_classes)
    support.run_doctest(collections, verbose)


jeżeli __name__ == "__main__":
    test_main(verbose=Prawda)
