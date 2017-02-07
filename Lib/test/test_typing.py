z collections zaimportuj namedtuple
zaimportuj re
zaimportuj sys
z unittest zaimportuj TestCase, main
spróbuj:
    z unittest zaimportuj mock
wyjąwszy ImportError:
    zaimportuj mock  # 3rd party install, dla PY3.2.

z typing zaimportuj Any
z typing zaimportuj TypeVar, AnyStr
z typing zaimportuj T, KT, VT  # Not w __all__.
z typing zaimportuj Union, Optional
z typing zaimportuj Tuple
z typing zaimportuj Callable
z typing zaimportuj Generic
z typing zaimportuj cast
z typing zaimportuj get_type_hints
z typing zaimportuj no_type_check, no_type_check_decorator
z typing zaimportuj NamedTuple
z typing zaimportuj IO, TextIO, BinaryIO
z typing zaimportuj Pattern, Match
zaimportuj typing


klasa Employee:
    dalej


klasa Manager(Employee):
    dalej


klasa Founder(Employee):
    dalej


klasa ManagingFounder(Manager, Founder):
    dalej


klasa AnyTests(TestCase):

    def test_any_instance_type_error(self):
        przy self.assertRaises(TypeError):
            isinstance(42, Any)

    def test_any_subclass(self):
        self.assertPrawda(issubclass(Employee, Any))
        self.assertPrawda(issubclass(int, Any))
        self.assertPrawda(issubclass(type(Nic), Any))
        self.assertPrawda(issubclass(object, Any))

    def test_others_any(self):
        self.assertNieprawda(issubclass(Any, Employee))
        self.assertNieprawda(issubclass(Any, int))
        self.assertNieprawda(issubclass(Any, type(Nic)))
        # However, Any jest a subclass of object (this can't be helped).
        self.assertPrawda(issubclass(Any, object))

    def test_repr(self):
        self.assertEqual(repr(Any), 'typing.Any')

    def test_errors(self):
        przy self.assertRaises(TypeError):
            issubclass(42, Any)
        przy self.assertRaises(TypeError):
            Any[int]  # Any jest nie a generic type.

    def test_cannot_subclass(self):
        przy self.assertRaises(TypeError):
            klasa A(Any):
                dalej

    def test_cannot_instantiate(self):
        przy self.assertRaises(TypeError):
            Any()

    def test_cannot_subscript(self):
        przy self.assertRaises(TypeError):
            Any[int]

    def test_any_is_subclass(self):
        # Any should be considered a subclass of everything.
        assert issubclass(Any, Any)
        assert issubclass(Any, typing.List)
        assert issubclass(Any, typing.List[int])
        assert issubclass(Any, typing.List[T])
        assert issubclass(Any, typing.Mapping)
        assert issubclass(Any, typing.Mapping[str, int])
        assert issubclass(Any, typing.Mapping[KT, VT])
        assert issubclass(Any, Generic)
        assert issubclass(Any, Generic[T])
        assert issubclass(Any, Generic[KT, VT])
        assert issubclass(Any, AnyStr)
        assert issubclass(Any, Union)
        assert issubclass(Any, Union[int, str])
        assert issubclass(Any, typing.Match)
        assert issubclass(Any, typing.Match[str])
        # These expressions must simply nie fail.
        typing.Match[Any]
        typing.Pattern[Any]
        typing.IO[Any]


klasa TypeVarTests(TestCase):

    def test_basic_plain(self):
        T = TypeVar('T')
        # Every klasa jest a subclass of T.
        assert issubclass(int, T)
        assert issubclass(str, T)
        # T equals itself.
        assert T == T
        # T jest a subclass of itself.
        assert issubclass(T, T)
        # T jest an instance of TypeVar
        assert isinstance(T, TypeVar)

    def test_typevar_instance_type_error(self):
        T = TypeVar('T')
        przy self.assertRaises(TypeError):
            isinstance(42, T)

    def test_basic_constrained(self):
        A = TypeVar('A', str, bytes)
        # Only str oraz bytes are subclasses of A.
        assert issubclass(str, A)
        assert issubclass(bytes, A)
        assert nie issubclass(int, A)
        # A equals itself.
        assert A == A
        # A jest a subclass of itself.
        assert issubclass(A, A)

    def test_constrained_error(self):
        przy self.assertRaises(TypeError):
            X = TypeVar('X', int)

    def test_union_unique(self):
        X = TypeVar('X')
        Y = TypeVar('Y')
        assert X != Y
        assert Union[X] == X
        assert Union[X] != Union[X, Y]
        assert Union[X, X] == X
        assert Union[X, int] != Union[X]
        assert Union[X, int] != Union[int]
        assert Union[X, int].__union_params__ == (X, int)
        assert Union[X, int].__union_set_params__ == {X, int}

    def test_union_constrained(self):
        A = TypeVar('A', str, bytes)
        assert Union[A, str] != Union[A]

    def test_repr(self):
        self.assertEqual(repr(T), '~T')
        self.assertEqual(repr(KT), '~KT')
        self.assertEqual(repr(VT), '~VT')
        self.assertEqual(repr(AnyStr), '~AnyStr')
        T_co = TypeVar('T_co', covariant=Prawda)
        self.assertEqual(repr(T_co), '+T_co')
        T_contra = TypeVar('T_contra', contravariant=Prawda)
        self.assertEqual(repr(T_contra), '-T_contra')

    def test_no_redefinition(self):
        self.assertNotEqual(TypeVar('T'), TypeVar('T'))
        self.assertNotEqual(TypeVar('T', int, str), TypeVar('T', int, str))

    def test_subclass_as_unions(self):
        # Nic of these are true -- each type var jest its own world.
        self.assertNieprawda(issubclass(TypeVar('T', int, str),
                                    TypeVar('T', int, str)))
        self.assertNieprawda(issubclass(TypeVar('T', int, float),
                                    TypeVar('T', int, float, str)))
        self.assertNieprawda(issubclass(TypeVar('T', int, str),
                                    TypeVar('T', str, int)))
        A = TypeVar('A', int, str)
        B = TypeVar('B', int, str, float)
        self.assertNieprawda(issubclass(A, B))
        self.assertNieprawda(issubclass(B, A))

    def test_cannot_subclass_vars(self):
        przy self.assertRaises(TypeError):
            klasa V(TypeVar('T')):
                dalej

    def test_cannot_subclass_var_itself(self):
        przy self.assertRaises(TypeError):
            klasa V(TypeVar):
                dalej

    def test_cannot_instantiate_vars(self):
        przy self.assertRaises(TypeError):
            TypeVar('A')()

    def test_bound(self):
        X = TypeVar('X', bound=Employee)
        assert issubclass(Employee, X)
        assert issubclass(Manager, X)
        assert nie issubclass(int, X)

    def test_bound_errors(self):
        przy self.assertRaises(TypeError):
            TypeVar('X', bound=42)
        przy self.assertRaises(TypeError):
            TypeVar('X', str, float, bound=Employee)


klasa UnionTests(TestCase):

    def test_basics(self):
        u = Union[int, float]
        self.assertNotEqual(u, Union)
        self.assertPrawda(issubclass(int, u))
        self.assertPrawda(issubclass(float, u))

    def test_union_any(self):
        u = Union[Any]
        self.assertEqual(u, Any)
        u = Union[int, Any]
        self.assertEqual(u, Any)
        u = Union[Any, int]
        self.assertEqual(u, Any)

    def test_union_object(self):
        u = Union[object]
        self.assertEqual(u, object)
        u = Union[int, object]
        self.assertEqual(u, object)
        u = Union[object, int]
        self.assertEqual(u, object)

    def test_union_any_object(self):
        u = Union[object, Any]
        self.assertEqual(u, Any)
        u = Union[Any, object]
        self.assertEqual(u, Any)

    def test_unordered(self):
        u1 = Union[int, float]
        u2 = Union[float, int]
        self.assertEqual(u1, u2)

    def test_subclass(self):
        u = Union[int, Employee]
        self.assertPrawda(issubclass(Manager, u))

    def test_self_subclass(self):
        self.assertPrawda(issubclass(Union[KT, VT], Union))
        self.assertNieprawda(issubclass(Union, Union[KT, VT]))

    def test_multiple_inheritance(self):
        u = Union[int, Employee]
        self.assertPrawda(issubclass(ManagingFounder, u))

    def test_single_class_disappears(self):
        t = Union[Employee]
        self.assertIs(t, Employee)

    def test_base_class_disappears(self):
        u = Union[Employee, Manager, int]
        self.assertEqual(u, Union[int, Employee])
        u = Union[Manager, int, Employee]
        self.assertEqual(u, Union[int, Employee])
        u = Union[Employee, Manager]
        self.assertIs(u, Employee)

    def test_weird_subclasses(self):
        u = Union[Employee, int, float]
        v = Union[int, float]
        self.assertPrawda(issubclass(v, u))
        w = Union[int, Manager]
        self.assertPrawda(issubclass(w, u))

    def test_union_union(self):
        u = Union[int, float]
        v = Union[u, Employee]
        self.assertEqual(v, Union[int, float, Employee])

    def test_repr(self):
        self.assertEqual(repr(Union), 'typing.Union')
        u = Union[Employee, int]
        self.assertEqual(repr(u), 'typing.Union[%s.Employee, int]' % __name__)
        u = Union[int, Employee]
        self.assertEqual(repr(u), 'typing.Union[int, %s.Employee]' % __name__)

    def test_cannot_subclass(self):
        przy self.assertRaises(TypeError):
            klasa C(Union):
                dalej
        przy self.assertRaises(TypeError):
            klasa C(Union[int, str]):
                dalej

    def test_cannot_instantiate(self):
        przy self.assertRaises(TypeError):
            Union()
        u = Union[int, float]
        przy self.assertRaises(TypeError):
            u()

    def test_optional(self):
        o = Optional[int]
        u = Union[int, Nic]
        self.assertEqual(o, u)

    def test_empty(self):
        przy self.assertRaises(TypeError):
            Union[()]

    def test_issubclass_union(self):
        assert issubclass(Union[int, str], Union)
        assert nie issubclass(int, Union)

    def test_union_instance_type_error(self):
        przy self.assertRaises(TypeError):
            isinstance(42, Union[int, str])


klasa TypeVarUnionTests(TestCase):

    def test_simpler(self):
        A = TypeVar('A', int, str, float)
        B = TypeVar('B', int, str)
        assert issubclass(A, A)
        assert issubclass(B, B)
        assert nie issubclass(B, A)
        assert issubclass(A, Union[int, str, float])
        assert nie issubclass(Union[int, str, float], A)
        assert nie issubclass(Union[int, str], B)
        assert issubclass(B, Union[int, str])
        assert nie issubclass(A, B)
        assert nie issubclass(Union[int, str, float], B)
        assert nie issubclass(A, Union[int, str])

    def test_var_union_subclass(self):
        self.assertPrawda(issubclass(T, Union[int, T]))
        self.assertPrawda(issubclass(KT, Union[KT, VT]))

    def test_var_union(self):
        TU = TypeVar('TU', Union[int, float], Nic)
        assert issubclass(int, TU)
        assert issubclass(float, TU)


klasa TupleTests(TestCase):

    def test_basics(self):
        self.assertPrawda(issubclass(Tuple[int, str], Tuple))
        self.assertPrawda(issubclass(Tuple[int, str], Tuple[int, str]))
        self.assertNieprawda(issubclass(int, Tuple))
        self.assertNieprawda(issubclass(Tuple[float, str], Tuple[int, str]))
        self.assertNieprawda(issubclass(Tuple[int, str, int], Tuple[int, str]))
        self.assertNieprawda(issubclass(Tuple[int, str], Tuple[int, str, int]))
        self.assertPrawda(issubclass(tuple, Tuple))
        self.assertNieprawda(issubclass(Tuple, tuple))  # Can't have it both ways.

    def test_tuple_subclass(self):
        klasa MyTuple(tuple):
            dalej
        self.assertPrawda(issubclass(MyTuple, Tuple))

    def test_tuple_instance_type_error(self):
        przy self.assertRaises(TypeError):
            isinstance((0, 0), Tuple[int, int])
        przy self.assertRaises(TypeError):
            isinstance((0, 0), Tuple)

    def test_tuple_ellipsis_subclass(self):

        klasa B:
            dalej

        klasa C(B):
            dalej

        assert nie issubclass(Tuple[B], Tuple[B, ...])
        assert issubclass(Tuple[C, ...], Tuple[B, ...])
        assert nie issubclass(Tuple[C, ...], Tuple[B])
        assert nie issubclass(Tuple[C], Tuple[B, ...])

    def test_repr(self):
        self.assertEqual(repr(Tuple), 'typing.Tuple')
        self.assertEqual(repr(Tuple[()]), 'typing.Tuple[]')
        self.assertEqual(repr(Tuple[int, float]), 'typing.Tuple[int, float]')
        self.assertEqual(repr(Tuple[int, ...]), 'typing.Tuple[int, ...]')

    def test_errors(self):
        przy self.assertRaises(TypeError):
            issubclass(42, Tuple)
        przy self.assertRaises(TypeError):
            issubclass(42, Tuple[int])


klasa CallableTests(TestCase):

    def test_self_subclass(self):
        self.assertPrawda(issubclass(Callable[[int], int], Callable))
        self.assertNieprawda(issubclass(Callable, Callable[[int], int]))
        self.assertPrawda(issubclass(Callable[[int], int], Callable[[int], int]))
        self.assertNieprawda(issubclass(Callable[[Employee], int],
                                    Callable[[Manager], int]))
        self.assertNieprawda(issubclass(Callable[[Manager], int],
                                    Callable[[Employee], int]))
        self.assertNieprawda(issubclass(Callable[[int], Employee],
                                    Callable[[int], Manager]))
        self.assertNieprawda(issubclass(Callable[[int], Manager],
                                    Callable[[int], Employee]))

    def test_eq_hash(self):
        self.assertEqual(Callable[[int], int], Callable[[int], int])
        self.assertEqual(len({Callable[[int], int], Callable[[int], int]}), 1)
        self.assertNotEqual(Callable[[int], int], Callable[[int], str])
        self.assertNotEqual(Callable[[int], int], Callable[[str], int])
        self.assertNotEqual(Callable[[int], int], Callable[[int, int], int])
        self.assertNotEqual(Callable[[int], int], Callable[[], int])
        self.assertNotEqual(Callable[[int], int], Callable)

    def test_cannot_subclass(self):
        przy self.assertRaises(TypeError):

            klasa C(Callable):
                dalej

        przy self.assertRaises(TypeError):

            klasa C(Callable[[int], int]):
                dalej

    def test_cannot_instantiate(self):
        przy self.assertRaises(TypeError):
            Callable()
        c = Callable[[int], str]
        przy self.assertRaises(TypeError):
            c()

    def test_callable_instance_works(self):
        def f():
            dalej
        assert isinstance(f, Callable)
        assert nie isinstance(Nic, Callable)

    def test_callable_instance_type_error(self):
        def f():
            dalej
        przy self.assertRaises(TypeError):
            assert isinstance(f, Callable[[], Nic])
        przy self.assertRaises(TypeError):
            assert isinstance(f, Callable[[], Any])
        przy self.assertRaises(TypeError):
            assert nie isinstance(Nic, Callable[[], Nic])
        przy self.assertRaises(TypeError):
            assert nie isinstance(Nic, Callable[[], Any])

    def test_repr(self):
        ct0 = Callable[[], bool]
        self.assertEqual(repr(ct0), 'typing.Callable[[], bool]')
        ct2 = Callable[[str, float], int]
        self.assertEqual(repr(ct2), 'typing.Callable[[str, float], int]')
        ctv = Callable[..., str]
        self.assertEqual(repr(ctv), 'typing.Callable[..., str]')

    def test_callable_with_ellipsis(self):

        def foo(a: Callable[..., T]):
            dalej

        self.assertEqual(get_type_hints(foo, globals(), locals()),
                         {'a': Callable[..., T]})


XK = TypeVar('XK', str, bytes)
XV = TypeVar('XV')


klasa SimpleMapping(Generic[XK, XV]):

    def __getitem__(self, key: XK) -> XV:
        ...

    def __setitem__(self, key: XK, value: XV):
        ...

    def get(self, key: XK, default: XV = Nic) -> XV:
        ...


klasa MySimpleMapping(SimpleMapping):

    def __init__(self):
        self.store = {}

    def __getitem__(self, key: str):
        zwróć self.store[key]

    def __setitem__(self, key: str, value):
        self.store[key] = value

    def get(self, key: str, default=Nic):
        spróbuj:
            zwróć self.store[key]
        wyjąwszy KeyError:
            zwróć default


klasa ProtocolTests(TestCase):

    def test_supports_int(self):
        assert issubclass(int, typing.SupportsInt)
        assert nie issubclass(str, typing.SupportsInt)

    def test_supports_float(self):
        assert issubclass(float, typing.SupportsFloat)
        assert nie issubclass(str, typing.SupportsFloat)

    def test_supports_complex(self):

        # Note: complex itself doesn't have __complex__.
        klasa C:
            def __complex__(self):
                zwróć 0j

        assert issubclass(C, typing.SupportsComplex)
        assert nie issubclass(str, typing.SupportsComplex)

    def test_supports_bytes(self):

        # Note: bytes itself doesn't have __bytes__.
        klasa B:
            def __bytes__(self):
                zwróć b''

        assert issubclass(B, typing.SupportsBytes)
        assert nie issubclass(str, typing.SupportsBytes)

    def test_supports_abs(self):
        assert issubclass(float, typing.SupportsAbs)
        assert issubclass(int, typing.SupportsAbs)
        assert nie issubclass(str, typing.SupportsAbs)

    def test_supports_round(self):
        assert issubclass(float, typing.SupportsRound)
        assert issubclass(int, typing.SupportsRound)
        assert nie issubclass(str, typing.SupportsRound)

    def test_reversible(self):
        assert issubclass(list, typing.Reversible)
        assert nie issubclass(int, typing.Reversible)

    def test_protocol_instance_type_error(self):
        przy self.assertRaises(TypeError):
            isinstance([], typing.Reversible)


klasa GenericTests(TestCase):

    def test_basics(self):
        X = SimpleMapping[str, Any]
        Y = SimpleMapping[XK, str]
        X[str, str]
        Y[str, str]
        przy self.assertRaises(TypeError):
            X[int, str]
        przy self.assertRaises(TypeError):
            Y[str, bytes]

    def test_init(self):
        T = TypeVar('T')
        S = TypeVar('S')
        przy self.assertRaises(TypeError):
            Generic[T, T]
        przy self.assertRaises(TypeError):
            Generic[T, S, T]

    def test_repr(self):
        self.assertEqual(repr(SimpleMapping),
                         __name__ + '.' + 'SimpleMapping[~XK, ~XV]')
        self.assertEqual(repr(MySimpleMapping),
                         __name__ + '.' + 'MySimpleMapping[~XK, ~XV]')

    def test_errors(self):
        przy self.assertRaises(TypeError):
            B = SimpleMapping[XK, Any]

            klasa C(Generic[B]):
                dalej

    def test_repr_2(self):
        PY32 = sys.version_info[:2] < (3, 3)

        klasa C(Generic[T]):
            dalej

        assert C.__module__ == __name__
        jeżeli nie PY32:
            assert C.__qualname__ == 'GenericTests.test_repr_2.<locals>.C'
        assert repr(C).split('.')[-1] == 'C[~T]'
        X = C[int]
        assert X.__module__ == __name__
        jeżeli nie PY32:
            assert X.__qualname__ == 'C'
        assert repr(X).split('.')[-1] == 'C[int]'

        klasa Y(C[int]):
            dalej

        assert Y.__module__ == __name__
        jeżeli nie PY32:
            assert Y.__qualname__ == 'GenericTests.test_repr_2.<locals>.Y'
        assert repr(Y).split('.')[-1] == 'Y[int]'

    def test_eq_1(self):
        assert Generic == Generic
        assert Generic[T] == Generic[T]
        assert Generic[KT] != Generic[VT]

    def test_eq_2(self):

        klasa A(Generic[T]):
            dalej

        klasa B(Generic[T]):
            dalej

        assert A == A
        assert A != B
        assert A[T] == A[T]
        assert A[T] != B[T]

    def test_multiple_inheritance(self):

        klasa A(Generic[T, VT]):
            dalej

        klasa B(Generic[KT, T]):
            dalej

        klasa C(A, Generic[KT, VT], B):
            dalej

        assert C.__parameters__ == (T, VT, KT)

    def test_nested(self):

        klasa G(Generic):
            dalej

        klasa Visitor(G[T]):

            a = Nic

            def set(self, a: T):
                self.a = a

            def get(self):
                zwróć self.a

            def visit(self) -> T:
                zwróć self.a

        V = Visitor[typing.List[int]]

        klasa IntListVisitor(V):

            def append(self, x: int):
                self.a.append(x)

        a = IntListVisitor()
        a.set([])
        a.append(1)
        a.append(42)
        assert a.get() == [1, 42]

    def test_type_erasure(self):
        T = TypeVar('T')

        klasa Node(Generic[T]):
            def __init__(self, label: T,
                         left: 'Node[T]' = Nic,
                         right: 'Node[T]' = Nic):
                self.label = label  # type: T
                self.left = left  # type: Optional[Node[T]]
                self.right = right  # type: Optional[Node[T]]

        def foo(x: T):
            a = Node(x)
            b = Node[T](x)
            c = Node[Any](x)
            assert type(a) jest Node
            assert type(b) jest Node
            assert type(c) jest Node

        foo(42)


klasa VarianceTests(TestCase):

    def test_invariance(self):
        # Because of invariance, List[subclass of X] jest nie a subclass
        # of List[X], oraz ditto dla MutableSequence.
        assert nie issubclass(typing.List[Manager], typing.List[Employee])
        assert nie issubclass(typing.MutableSequence[Manager],
                              typing.MutableSequence[Employee])
        # It's still reflexive.
        assert issubclass(typing.List[Employee], typing.List[Employee])
        assert issubclass(typing.MutableSequence[Employee],
                          typing.MutableSequence[Employee])

    def test_covariance_tuple(self):
        # Check covariace dla Tuple (which are really special cases).
        assert issubclass(Tuple[Manager], Tuple[Employee])
        assert nie issubclass(Tuple[Employee], Tuple[Manager])
        # And pairwise.
        assert issubclass(Tuple[Manager, Manager], Tuple[Employee, Employee])
        assert nie issubclass(Tuple[Employee, Employee],
                              Tuple[Manager, Employee])
        # And using ellipsis.
        assert issubclass(Tuple[Manager, ...], Tuple[Employee, ...])
        assert nie issubclass(Tuple[Employee, ...], Tuple[Manager, ...])

    def test_covariance_sequence(self):
        # Check covariance dla Sequence (which jest just a generic class
        # dla this purpose, but using a covariant type variable).
        assert issubclass(typing.Sequence[Manager], typing.Sequence[Employee])
        assert nie issubclass(typing.Sequence[Employee],
                              typing.Sequence[Manager])

    def test_covariance_mapping(self):
        # Ditto dla Mapping (covariant w the value, invariant w the key).
        assert issubclass(typing.Mapping[Employee, Manager],
                          typing.Mapping[Employee, Employee])
        assert nie issubclass(typing.Mapping[Manager, Employee],
                              typing.Mapping[Employee, Employee])
        assert nie issubclass(typing.Mapping[Employee, Manager],
                              typing.Mapping[Manager, Manager])
        assert nie issubclass(typing.Mapping[Manager, Employee],
                              typing.Mapping[Manager, Manager])


klasa CastTests(TestCase):

    def test_basics(self):
        assert cast(int, 42) == 42
        assert cast(float, 42) == 42
        assert type(cast(float, 42)) jest int
        assert cast(Any, 42) == 42
        assert cast(list, 42) == 42
        assert cast(Union[str, float], 42) == 42
        assert cast(AnyStr, 42) == 42
        assert cast(Nic, 42) == 42

    def test_errors(self):
        # Bogus calls are nie expected to fail.
        cast(42, 42)
        cast('hello', 42)


klasa ForwardRefTests(TestCase):

    def test_basics(self):

        klasa Node(Generic[T]):

            def __init__(self, label: T):
                self.label = label
                self.left = self.right = Nic

            def add_both(self,
                         left: 'Optional[Node[T]]',
                         right: 'Node[T]' = Nic,
                         stuff: int = Nic,
                         blah=Nic):
                self.left = left
                self.right = right

            def add_left(self, node: Optional['Node[T]']):
                self.add_both(node, Nic)

            def add_right(self, node: 'Node[T]' = Nic):
                self.add_both(Nic, node)

        t = Node[int]
        both_hints = get_type_hints(t.add_both, globals(), locals())
        assert both_hints['left'] == both_hints['right'] == Optional[Node[T]]
        assert both_hints['stuff'] == Optional[int]
        assert 'blah' nie w both_hints

        left_hints = get_type_hints(t.add_left, globals(), locals())
        assert left_hints['node'] == Optional[Node[T]]

        right_hints = get_type_hints(t.add_right, globals(), locals())
        assert right_hints['node'] == Optional[Node[T]]

    def test_forwardref_instance_type_error(self):
        fr = typing._ForwardRef('int')
        przy self.assertRaises(TypeError):
            isinstance(42, fr)

    def test_union_forward(self):

        def foo(a: Union['T']):
            dalej

        self.assertEqual(get_type_hints(foo, globals(), locals()),
                         {'a': Union[T]})

    def test_tuple_forward(self):

        def foo(a: Tuple['T']):
            dalej

        self.assertEqual(get_type_hints(foo, globals(), locals()),
                         {'a': Tuple[T]})

    def test_callable_forward(self):

        def foo(a: Callable[['T'], 'T']):
            dalej

        self.assertEqual(get_type_hints(foo, globals(), locals()),
                         {'a': Callable[[T], T]})

    def test_callable_with_ellipsis_forward(self):

        def foo(a: 'Callable[..., T]'):
            dalej

        self.assertEqual(get_type_hints(foo, globals(), locals()),
                         {'a': Callable[..., T]})

    def test_syntax_error(self):

        przy self.assertRaises(SyntaxError):
            Generic['/T']

    def test_delayed_syntax_error(self):

        def foo(a: 'Node[T'):
            dalej

        przy self.assertRaises(SyntaxError):
            get_type_hints(foo)

    def test_type_error(self):

        def foo(a: Tuple['42']):
            dalej

        przy self.assertRaises(TypeError):
            get_type_hints(foo)

    def test_name_error(self):

        def foo(a: 'Noode[T]'):
            dalej

        przy self.assertRaises(NameError):
            get_type_hints(foo, locals())

    def test_no_type_check(self):

        @no_type_check
        def foo(a: 'whatevers') -> {}:
            dalej

        th = get_type_hints(foo)
        self.assertEqual(th, {})

    def test_no_type_check_class(self):

        @no_type_check
        klasa C:
            def foo(a: 'whatevers') -> {}:
                dalej

        cth = get_type_hints(C.foo)
        self.assertEqual(cth, {})
        ith = get_type_hints(C().foo)
        self.assertEqual(ith, {})

    def test_meta_no_type_check(self):

        @no_type_check_decorator
        def magic_decorator(deco):
            zwróć deco

        self.assertEqual(magic_decorator.__name__, 'magic_decorator')

        @magic_decorator
        def foo(a: 'whatevers') -> {}:
            dalej

        @magic_decorator
        klasa C:
            def foo(a: 'whatevers') -> {}:
                dalej

        self.assertEqual(foo.__name__, 'foo')
        th = get_type_hints(foo)
        self.assertEqual(th, {})
        cth = get_type_hints(C.foo)
        self.assertEqual(cth, {})
        ith = get_type_hints(C().foo)
        self.assertEqual(ith, {})

    def test_default_globals(self):
        code = ("class C:\n"
                "    def foo(self, a: 'C') -> 'D': dalej\n"
                "class D:\n"
                "    def bar(self, b: 'D') -> C: dalej\n"
                )
        ns = {}
        exec(code, ns)
        hints = get_type_hints(ns['C'].foo)
        assert hints == {'a': ns['C'], 'return': ns['D']}


klasa OverloadTests(TestCase):

    def test_overload_exists(self):
        z typing zaimportuj overload

    def test_overload_fails(self):
        z typing zaimportuj overload

        przy self.assertRaises(RuntimeError):
            @overload
            def blah():
                dalej


klasa CollectionsAbcTests(TestCase):

    def test_hashable(self):
        assert isinstance(42, typing.Hashable)
        assert nie isinstance([], typing.Hashable)

    def test_iterable(self):
        assert isinstance([], typing.Iterable)
        # Due to ABC caching, the second time takes a separate code
        # path oraz could fail.  So call this a few times.
        assert isinstance([], typing.Iterable)
        assert isinstance([], typing.Iterable)
        assert isinstance([], typing.Iterable[int])
        assert nie isinstance(42, typing.Iterable)
        # Just w case, also test issubclass() a few times.
        assert issubclass(list, typing.Iterable)
        assert issubclass(list, typing.Iterable)

    def test_iterator(self):
        it = iter([])
        assert isinstance(it, typing.Iterator)
        assert isinstance(it, typing.Iterator[int])
        assert nie isinstance(42, typing.Iterator)

    def test_sized(self):
        assert isinstance([], typing.Sized)
        assert nie isinstance(42, typing.Sized)

    def test_container(self):
        assert isinstance([], typing.Container)
        assert nie isinstance(42, typing.Container)

    def test_abstractset(self):
        assert isinstance(set(), typing.AbstractSet)
        assert nie isinstance(42, typing.AbstractSet)

    def test_mutableset(self):
        assert isinstance(set(), typing.MutableSet)
        assert nie isinstance(frozenset(), typing.MutableSet)

    def test_mapping(self):
        assert isinstance({}, typing.Mapping)
        assert nie isinstance(42, typing.Mapping)

    def test_mutablemapping(self):
        assert isinstance({}, typing.MutableMapping)
        assert nie isinstance(42, typing.MutableMapping)

    def test_sequence(self):
        assert isinstance([], typing.Sequence)
        assert nie isinstance(42, typing.Sequence)

    def test_mutablesequence(self):
        assert isinstance([], typing.MutableSequence)
        assert nie isinstance((), typing.MutableSequence)

    def test_bytestring(self):
        assert isinstance(b'', typing.ByteString)
        assert isinstance(bytearray(b''), typing.ByteString)

    def test_list(self):
        assert issubclass(list, typing.List)

    def test_set(self):
        assert issubclass(set, typing.Set)
        assert nie issubclass(frozenset, typing.Set)

    def test_frozenset(self):
        assert issubclass(frozenset, typing.FrozenSet)
        assert nie issubclass(set, typing.FrozenSet)

    def test_dict(self):
        assert issubclass(dict, typing.Dict)

    def test_no_list_instantiation(self):
        przy self.assertRaises(TypeError):
            typing.List()
        przy self.assertRaises(TypeError):
            typing.List[T]()
        przy self.assertRaises(TypeError):
            typing.List[int]()

    def test_list_subclass_instantiation(self):

        klasa MyList(typing.List[int]):
            dalej

        a = MyList()
        assert isinstance(a, MyList)

    def test_no_dict_instantiation(self):
        przy self.assertRaises(TypeError):
            typing.Dict()
        przy self.assertRaises(TypeError):
            typing.Dict[KT, VT]()
        przy self.assertRaises(TypeError):
            typing.Dict[str, int]()

    def test_dict_subclass_instantiation(self):

        klasa MyDict(typing.Dict[str, int]):
            dalej

        d = MyDict()
        assert isinstance(d, MyDict)

    def test_no_set_instantiation(self):
        przy self.assertRaises(TypeError):
            typing.Set()
        przy self.assertRaises(TypeError):
            typing.Set[T]()
        przy self.assertRaises(TypeError):
            typing.Set[int]()

    def test_set_subclass_instantiation(self):

        klasa MySet(typing.Set[int]):
            dalej

        d = MySet()
        assert isinstance(d, MySet)

    def test_no_frozenset_instantiation(self):
        przy self.assertRaises(TypeError):
            typing.FrozenSet()
        przy self.assertRaises(TypeError):
            typing.FrozenSet[T]()
        przy self.assertRaises(TypeError):
            typing.FrozenSet[int]()

    def test_frozenset_subclass_instantiation(self):

        klasa MyFrozenSet(typing.FrozenSet[int]):
            dalej

        d = MyFrozenSet()
        assert isinstance(d, MyFrozenSet)

    def test_no_tuple_instantiation(self):
        przy self.assertRaises(TypeError):
            Tuple()
        przy self.assertRaises(TypeError):
            Tuple[T]()
        przy self.assertRaises(TypeError):
            Tuple[int]()

    def test_generator(self):
        def foo():
            uzyskaj 42
        g = foo()
        assert issubclass(type(g), typing.Generator)
        assert issubclass(typing.Generator[Manager, Employee, Manager],
                          typing.Generator[Employee, Manager, Employee])
        assert nie issubclass(typing.Generator[Manager, Manager, Manager],
                              typing.Generator[Employee, Employee, Employee])

    def test_no_generator_instantiation(self):
        przy self.assertRaises(TypeError):
            typing.Generator()
        przy self.assertRaises(TypeError):
            typing.Generator[T, T, T]()
        przy self.assertRaises(TypeError):
            typing.Generator[int, int, int]()

    def test_subclassing(self):

        klasa MMA(typing.MutableMapping):
            dalej

        przy self.assertRaises(TypeError):  # It's abstract
            MMA()

        klasa MMC(MMA):
            def __len__(self):
                zwróć 0

        assert len(MMC()) == 0

        klasa MMB(typing.MutableMapping[KT, VT]):
            def __len__(self):
                zwróć 0

        assert len(MMB()) == 0
        assert len(MMB[str, str]()) == 0
        assert len(MMB[KT, VT]()) == 0


klasa NamedTupleTests(TestCase):

    def test_basics(self):
        Emp = NamedTuple('Emp', [('name', str), ('id', int)])
        assert issubclass(Emp, tuple)
        joe = Emp('Joe', 42)
        jim = Emp(name='Jim', id=1)
        assert isinstance(joe, Emp)
        assert isinstance(joe, tuple)
        assert joe.name == 'Joe'
        assert joe.id == 42
        assert jim.name == 'Jim'
        assert jim.id == 1
        assert Emp.__name__ == 'Emp'
        assert Emp._fields == ('name', 'id')
        assert Emp._field_types == dict(name=str, id=int)


klasa IOTests(TestCase):

    def test_io(self):

        def stuff(a: IO) -> AnyStr:
            zwróć a.readline()

        a = stuff.__annotations__['a']
        assert a.__parameters__ == (AnyStr,)

    def test_textio(self):

        def stuff(a: TextIO) -> str:
            zwróć a.readline()

        a = stuff.__annotations__['a']
        assert a.__parameters__ == (str,)

    def test_binaryio(self):

        def stuff(a: BinaryIO) -> bytes:
            zwróć a.readline()

        a = stuff.__annotations__['a']
        assert a.__parameters__ == (bytes,)

    def test_io_submodule(self):
        z typing.io zaimportuj IO, TextIO, BinaryIO, __all__, __name__
        assert IO jest typing.IO
        assert TextIO jest typing.TextIO
        assert BinaryIO jest typing.BinaryIO
        assert set(__all__) == set(['IO', 'TextIO', 'BinaryIO'])
        assert __name__ == 'typing.io'


klasa RETests(TestCase):
    # Much of this jest really testing _TypeAlias.

    def test_basics(self):
        pat = re.compile('[a-z]+', re.I)
        assert issubclass(pat.__class__, Pattern)
        assert issubclass(type(pat), Pattern)
        assert issubclass(type(pat), Pattern[str])

        mat = pat.search('12345abcde.....')
        assert issubclass(mat.__class__, Match)
        assert issubclass(mat.__class__, Match[str])
        assert issubclass(mat.__class__, Match[bytes])  # Sad but true.
        assert issubclass(type(mat), Match)
        assert issubclass(type(mat), Match[str])

        p = Pattern[Union[str, bytes]]
        assert issubclass(Pattern[str], Pattern)
        assert issubclass(Pattern[str], p)

        m = Match[Union[bytes, str]]
        assert issubclass(Match[bytes], Match)
        assert issubclass(Match[bytes], m)

    def test_errors(self):
        przy self.assertRaises(TypeError):
            # Doesn't fit AnyStr.
            Pattern[int]
        przy self.assertRaises(TypeError):
            # Can't change type vars?
            Match[T]
        m = Match[Union[str, bytes]]
        przy self.assertRaises(TypeError):
            # Too complicated?
            m[str]
        przy self.assertRaises(TypeError):
            # We don't support isinstance().
            isinstance(42, Pattern)
        przy self.assertRaises(TypeError):
            # We don't support isinstance().
            isinstance(42, Pattern[str])

    def test_repr(self):
        assert repr(Pattern) == 'Pattern[~AnyStr]'
        assert repr(Pattern[str]) == 'Pattern[str]'
        assert repr(Pattern[bytes]) == 'Pattern[bytes]'
        assert repr(Match) == 'Match[~AnyStr]'
        assert repr(Match[str]) == 'Match[str]'
        assert repr(Match[bytes]) == 'Match[bytes]'

    def test_re_submodule(self):
        z typing.re zaimportuj Match, Pattern, __all__, __name__
        assert Match jest typing.Match
        assert Pattern jest typing.Pattern
        assert set(__all__) == set(['Match', 'Pattern'])
        assert __name__ == 'typing.re'

    def test_cannot_subclass(self):
        przy self.assertRaises(TypeError) jako ex:

            klasa A(typing.Match):
                dalej

        assert str(ex.exception) == "A type alias cannot be subclassed"


klasa AllTests(TestCase):
    """Tests dla __all__."""

    def test_all(self):
        z typing zaimportuj __all__ jako a
        # Just spot-check the first oraz last of every category.
        assert 'AbstractSet' w a
        assert 'ValuesView' w a
        assert 'cast' w a
        assert 'overload' w a
        assert 'io' w a
        assert 're' w a
        # Spot-check that stdlib modules aren't exported.
        assert 'os' nie w a
        assert 'sys' nie w a


jeżeli __name__ == '__main__':
    main()
