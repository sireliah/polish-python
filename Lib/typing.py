# TODO nits:
# Get rid of asserts that are the caller's fault.
# Docstrings (e.g. ABCs).

zaimportuj abc
z abc zaimportuj abstractmethod, abstractproperty
zaimportuj collections
zaimportuj functools
zaimportuj re jako stdlib_re  # Avoid confusion przy the re we export.
zaimportuj sys
zaimportuj types
spróbuj:
    zaimportuj collections.abc jako collections_abc
wyjąwszy ImportError:
    zaimportuj collections jako collections_abc  # Fallback dla PY3.2.


# Please keep __all__ alphabetized within each category.
__all__ = [
    # Super-special typing primitives.
    'Any',
    'Callable',
    'Generic',
    'Optional',
    'TypeVar',
    'Union',
    'Tuple',

    # ABCs (z collections.abc).
    'AbstractSet',  # collections.abc.Set.
    'ByteString',
    'Container',
    'Hashable',
    'ItemsView',
    'Iterable',
    'Iterator',
    'KeysView',
    'Mapping',
    'MappingView',
    'MutableMapping',
    'MutableSequence',
    'MutableSet',
    'Sequence',
    'Sized',
    'ValuesView',

    # Structural checks, a.k.a. protocols.
    'Reversible',
    'SupportsAbs',
    'SupportsFloat',
    'SupportsInt',
    'SupportsRound',

    # Concrete collection types.
    'Dict',
    'List',
    'Set',
    'NamedTuple',  # Not really a type.
    'Generator',

    # One-off things.
    'AnyStr',
    'cast',
    'get_type_hints',
    'no_type_check',
    'no_type_check_decorator',
    'overload',

    # Submodules.
    'io',
    're',
]


def _qualname(x):
    jeżeli sys.version_info[:2] >= (3, 3):
        zwróć x.__qualname__
    inaczej:
        # Fall back to just name.
        zwróć x.__name__


klasa TypingMeta(type):
    """Metaclass dla every type defined below.

    This overrides __new__() to require an extra keyword parameter
    '_root', which serves jako a guard against naive subclassing of the
    typing classes.  Any legitimate klasa defined using a metaclass
    derived z TypingMeta (including internal subclasses created by
    e.g.  Union[X, Y]) must dalej _root=Prawda.

    This also defines a dummy constructor (all the work jest done w
    __new__) oraz a nicer repr().
    """

    _is_protocol = Nieprawda

    def __new__(cls, name, bases, namespace, *, _root=Nieprawda):
        jeżeli nie _root:
            podnieś TypeError("Cannot subclass %s" %
                            (', '.join(map(_type_repr, bases)) albo '()'))
        zwróć super().__new__(cls, name, bases, namespace)

    def __init__(self, *args, **kwds):
        dalej

    def _eval_type(self, globalns, localns):
        """Override this w subclasses to interpret forward references.

        For example, Union['C'] jest internally stored as
        Union[_ForwardRef('C')], which should evaluate to _Union[C],
        where C jest an object found w globalns albo localns (searching
        localns first, of course).
        """
        zwróć self

    def _has_type_var(self):
        zwróć Nieprawda

    def __repr__(self):
        zwróć '%s.%s' % (self.__module__, _qualname(self))


klasa Final:
    """Mix-in klasa to prevent instantiation."""

    __slots__ = ()

    def __new__(self, *args, **kwds):
        podnieś TypeError("Cannot instantiate %r" % self.__class__)


klasa _ForwardRef(TypingMeta):
    """Wrapper to hold a forward reference."""

    def __new__(cls, arg):
        jeżeli nie isinstance(arg, str):
            podnieś TypeError('ForwardRef must be a string -- got %r' % (arg,))
        spróbuj:
            code = compile(arg, '<string>', 'eval')
        wyjąwszy SyntaxError:
            podnieś SyntaxError('ForwardRef must be an expression -- got %r' %
                              (arg,))
        self = super().__new__(cls, arg, (), {}, _root=Prawda)
        self.__forward_arg__ = arg
        self.__forward_code__ = code
        self.__forward_evaluated__ = Nieprawda
        self.__forward_value__ = Nic
        typing_globals = globals()
        frame = sys._getframe(1)
        dopóki frame jest nie Nic oraz frame.f_globals jest typing_globals:
            frame = frame.f_back
        assert frame jest nie Nic
        self.__forward_frame__ = frame
        zwróć self

    def _eval_type(self, globalns, localns):
        jeżeli nie isinstance(localns, dict):
            podnieś TypeError('ForwardRef localns must be a dict -- got %r' %
                            (localns,))
        jeżeli nie isinstance(globalns, dict):
            podnieś TypeError('ForwardRef globalns must be a dict -- got %r' %
                            (globalns,))
        jeżeli nie self.__forward_evaluated__:
            jeżeli globalns jest Nic oraz localns jest Nic:
                globalns = localns = {}
            albo_inaczej globalns jest Nic:
                globalns = localns
            albo_inaczej localns jest Nic:
                localns = globalns
            self.__forward_value__ = _type_check(
                eval(self.__forward_code__, globalns, localns),
                "Forward references must evaluate to types.")
            self.__forward_evaluated__ = Prawda
        zwróć self.__forward_value__

    def __instancecheck__(self, obj):
        podnieś TypeError("Forward references cannot be used przy isinstance().")

    def __subclasscheck__(self, cls):
        jeżeli nie self.__forward_evaluated__:
            globalns = self.__forward_frame__.f_globals
            localns = self.__forward_frame__.f_locals
            spróbuj:
                self._eval_type(globalns, localns)
            wyjąwszy NameError:
                zwróć Nieprawda  # Too early.
        zwróć issubclass(cls, self.__forward_value__)

    def __repr__(self):
        zwróć '_ForwardRef(%r)' % (self.__forward_arg__,)


klasa _TypeAlias:
    """Internal helper klasa dla defining generic variants of concrete types.

    Note that this jest nie a type; let's call it a pseudo-type.  It can
    be used w instance oraz subclass checks, e.g. isinstance(m, Match)
    albo issubclass(type(m), Match).  However, it cannot be itself the
    target of an issubclass() call; e.g. issubclass(Match, C) (for
    some arbitrary klasa C) podnieśs TypeError rather than returning
    Nieprawda.
    """

    __slots__ = ('name', 'type_var', 'impl_type', 'type_checker')

    def __new__(cls, *args, **kwds):
        """Constructor.

        This only exists to give a better error message w case
        someone tries to subclass a type alias (nie a good idea).
        """
        jeżeli (len(args) == 3 oraz
            isinstance(args[0], str) oraz
            isinstance(args[1], tuple)):
            # Close enough.
            podnieś TypeError("A type alias cannot be subclassed")
        zwróć object.__new__(cls)

    def __init__(self, name, type_var, impl_type, type_checker):
        """Initializer.

        Args:
            name: The name, e.g. 'Pattern'.
            type_var: The type parameter, e.g. AnyStr, albo the
                specific type, e.g. str.
            impl_type: The implementation type.
            type_checker: Function that takes an impl_type instance.
                oraz returns a value that should be a type_var instance.
        """
        assert isinstance(name, str), repr(name)
        assert isinstance(type_var, type), repr(type_var)
        assert isinstance(impl_type, type), repr(impl_type)
        assert nie isinstance(impl_type, TypingMeta), repr(impl_type)
        self.name = name
        self.type_var = type_var
        self.impl_type = impl_type
        self.type_checker = type_checker

    def __repr__(self):
        zwróć "%s[%s]" % (self.name, _type_repr(self.type_var))

    def __getitem__(self, parameter):
        assert isinstance(parameter, type), repr(parameter)
        jeżeli nie isinstance(self.type_var, TypeVar):
            podnieś TypeError("%s cannot be further parameterized." % self)
        jeżeli self.type_var.__constraints__:
            jeżeli nie issubclass(parameter, Union[self.type_var.__constraints__]):
                podnieś TypeError("%s jest nie a valid substitution dla %s." %
                                (parameter, self.type_var))
        zwróć self.__class__(self.name, parameter,
                              self.impl_type, self.type_checker)

    def __instancecheck__(self, obj):
        podnieś TypeError("Type aliases cannot be used przy isinstance().")

    def __subclasscheck__(self, cls):
        jeżeli cls jest Any:
            zwróć Prawda
        jeżeli isinstance(cls, _TypeAlias):
            # Covariance.  For now, we compare by name.
            zwróć (cls.name == self.name oraz
                    issubclass(cls.type_var, self.type_var))
        inaczej:
            # Note that this jest too lenient, because the
            # implementation type doesn't carry information about
            # whether it jest about bytes albo str (dla example).
            zwróć issubclass(cls, self.impl_type)


def _has_type_var(t):
    zwróć t jest nie Nic oraz isinstance(t, TypingMeta) oraz t._has_type_var()


def _eval_type(t, globalns, localns):
    jeżeli isinstance(t, TypingMeta):
        zwróć t._eval_type(globalns, localns)
    inaczej:
        zwróć t


def _type_check(arg, msg):
    """Check that the argument jest a type, oraz zwróć it.

    As a special case, accept Nic oraz zwróć type(Nic) instead.
    Also, _TypeAlias instances (e.g. Match, Pattern) are acceptable.

    The msg argument jest a human-readable error message, e.g.

        "Union[arg, ...]: arg should be a type."

    We append the repr() of the actual value (truncated to 100 chars).
    """
    jeżeli arg jest Nic:
        zwróć type(Nic)
    jeżeli isinstance(arg, str):
        arg = _ForwardRef(arg)
    jeżeli nie isinstance(arg, (type, _TypeAlias)):
        podnieś TypeError(msg + " Got %.100r." % (arg,))
    zwróć arg


def _type_repr(obj):
    """Return the repr() of an object, special-casing types.

    If obj jest a type, we zwróć a shorter version than the default
    type.__repr__, based on the module oraz qualified name, which jest
    typically enough to uniquely identify a type.  For everything
    inaczej, we fall back on repr(obj).
    """
    jeżeli isinstance(obj, type) oraz nie isinstance(obj, TypingMeta):
        jeżeli obj.__module__ == 'builtins':
            zwróć _qualname(obj)
        inaczej:
            zwróć '%s.%s' % (obj.__module__, _qualname(obj))
    inaczej:
        zwróć repr(obj)


klasa AnyMeta(TypingMeta):
    """Metaclass dla Any."""

    def __new__(cls, name, bases, namespace, _root=Nieprawda):
        self = super().__new__(cls, name, bases, namespace, _root=_root)
        zwróć self

    def __instancecheck__(self, obj):
        podnieś TypeError("Any cannot be used przy isinstance().")

    def __subclasscheck__(self, cls):
        jeżeli nie isinstance(cls, type):
            zwróć super().__subclasscheck__(cls)  # To TypeError.
        zwróć Prawda


klasa Any(Final, metaclass=AnyMeta, _root=Prawda):
    """Special type indicating an unconstrained type.

    - Any object jest an instance of Any.
    - Any klasa jest a subclass of Any.
    - As a special case, Any oraz object are subclasses of each other.
    """

    __slots__ = ()


klasa TypeVar(TypingMeta, metaclass=TypingMeta, _root=Prawda):
    """Type variable.

    Usage::

      T = TypeVar('T')  # Can be anything
      A = TypeVar('A', str, bytes)  # Must be str albo bytes

    Type variables exist primarily dla the benefit of static type
    checkers.  They serve jako the parameters dla generic types jako well
    jako dla generic function definitions.  See klasa Generic dla more
    information on generic types.  Generic functions work jako follows:

      def repeat(x: T, n: int) -> Sequence[T]:
          '''Return a list containing n references to x.'''
          zwróć [x]*n

      def longest(x: A, y: A) -> A:
          '''Return the longest of two strings.'''
          zwróć x jeżeli len(x) >= len(y) inaczej y

    The latter example's signature jest essentially the overloading
    of (str, str) -> str oraz (bytes, bytes) -> bytes.  Also note
    that jeżeli the arguments are instances of some subclass of str,
    the zwróć type jest still plain str.

    At runtime, isinstance(x, T) will podnieś TypeError.  However,
    issubclass(C, T) jest true dla any klasa C, oraz issubclass(str, A)
    oraz issubclass(bytes, A) are true, oraz issubclass(int, A) jest
    false.

    Type variables may be marked covariant albo contravariant by dalejing
    covariant=Prawda albo contravariant=Prawda.  See PEP 484 dla more
    details.  By default type variables are invariant.

    Type variables can be introspected. e.g.:

      T.__name__ == 'T'
      T.__constraints__ == ()
      T.__covariant__ == Nieprawda
      T.__contravariant__ = Nieprawda
      A.__constraints__ == (str, bytes)
    """

    def __new__(cls, name, *constraints, bound=Nic,
                covariant=Nieprawda, contravariant=Nieprawda):
        self = super().__new__(cls, name, (Final,), {}, _root=Prawda)
        jeżeli covariant oraz contravariant:
            podnieś ValueError("Bivariant type variables are nie supported.")
        self.__covariant__ = bool(covariant)
        self.__contravariant__ = bool(contravariant)
        jeżeli constraints oraz bound jest nie Nic:
            podnieś TypeError("Constraints cannot be combined przy bound=...")
        jeżeli constraints oraz len(constraints) == 1:
            podnieś TypeError("A single constraint jest nie allowed")
        msg = "TypeVar(name, constraint, ...): constraints must be types."
        self.__constraints__ = tuple(_type_check(t, msg) dla t w constraints)
        jeżeli bound:
            self.__bound__ = _type_check(bound, "Bound must be a type.")
        inaczej:
            self.__bound__ = Nic
        zwróć self

    def _has_type_var(self):
        zwróć Prawda

    def __repr__(self):
        jeżeli self.__covariant__:
            prefix = '+'
        albo_inaczej self.__contravariant__:
            prefix = '-'
        inaczej:
            prefix = '~'
        zwróć prefix + self.__name__

    def __instancecheck__(self, instance):
        podnieś TypeError("Type variables cannot be used przy isinstance().")

    def __subclasscheck__(self, cls):
        # TODO: Make this podnieś TypeError too?
        jeżeli cls jest self:
            zwróć Prawda
        jeżeli cls jest Any:
            zwróć Prawda
        jeżeli self.__bound__ jest nie Nic:
            zwróć issubclass(cls, self.__bound__)
        jeżeli self.__constraints__:
            zwróć any(issubclass(cls, c) dla c w self.__constraints__)
        zwróć Prawda


# Some unconstrained type variables.  These are used by the container types.
T = TypeVar('T')  # Any type.
KT = TypeVar('KT')  # Key type.
VT = TypeVar('VT')  # Value type.
T_co = TypeVar('T_co', covariant=Prawda)  # Any type covariant containers.
V_co = TypeVar('V_co', covariant=Prawda)  # Any type covariant containers.
VT_co = TypeVar('VT_co', covariant=Prawda)  # Value type covariant containers.
T_contra = TypeVar('T_contra', contravariant=Prawda)  # Ditto contravariant.

# A useful type variable przy constraints.  This represents string types.
# TODO: What about bytearray, memoryview?
AnyStr = TypeVar('AnyStr', bytes, str)


klasa UnionMeta(TypingMeta):
    """Metaclass dla Union."""

    def __new__(cls, name, bases, namespace, parameters=Nic, _root=Nieprawda):
        jeżeli parameters jest Nic:
            zwróć super().__new__(cls, name, bases, namespace, _root=_root)
        jeżeli nie isinstance(parameters, tuple):
            podnieś TypeError("Expected parameters=<tuple>")
        # Flatten out Union[Union[...], ...] oraz type-check non-Union args.
        params = []
        msg = "Union[arg, ...]: each arg must be a type."
        dla p w parameters:
            jeżeli isinstance(p, UnionMeta):
                params.extend(p.__union_params__)
            inaczej:
                params.append(_type_check(p, msg))
        # Weed out strict duplicates, preserving the first of each occurrence.
        all_params = set(params)
        jeżeli len(all_params) < len(params):
            new_params = []
            dla t w params:
                jeżeli t w all_params:
                    new_params.append(t)
                    all_params.remove(t)
            params = new_params
            assert nie all_params, all_params
        # Weed out subclasses.
        # E.g. Union[int, Employee, Manager] == Union[int, Employee].
        # If Any albo object jest present it will be the sole survivor.
        # If both Any oraz object are present, Any wins.
        # Never discard type variables, wyjąwszy against Any.
        # (In particular, Union[str, AnyStr] != AnyStr.)
        all_params = set(params)
        dla t1 w params:
            jeżeli t1 jest Any:
                zwróć Any
            jeżeli isinstance(t1, TypeVar):
                kontynuuj
            jeżeli any(issubclass(t1, t2)
                   dla t2 w all_params - {t1} jeżeli nie isinstance(t2, TypeVar)):
                all_params.remove(t1)
        # It's nie a union jeżeli there's only one type left.
        jeżeli len(all_params) == 1:
            zwróć all_params.pop()
        # Create a new klasa przy these params.
        self = super().__new__(cls, name, bases, {}, _root=Prawda)
        self.__union_params__ = tuple(t dla t w params jeżeli t w all_params)
        self.__union_set_params__ = frozenset(self.__union_params__)
        zwróć self

    def _eval_type(self, globalns, localns):
        p = tuple(_eval_type(t, globalns, localns)
                  dla t w self.__union_params__)
        jeżeli p == self.__union_params__:
            zwróć self
        inaczej:
            zwróć self.__class__(self.__name__, self.__bases__, {},
                                  p, _root=Prawda)

    def _has_type_var(self):
        jeżeli self.__union_params__:
            dla t w self.__union_params__:
                jeżeli _has_type_var(t):
                    zwróć Prawda
        zwróć Nieprawda

    def __repr__(self):
        r = super().__repr__()
        jeżeli self.__union_params__:
            r += '[%s]' % (', '.join(_type_repr(t)
                                     dla t w self.__union_params__))
        zwróć r

    def __getitem__(self, parameters):
        jeżeli self.__union_params__ jest nie Nic:
            podnieś TypeError(
                "Cannot subscript an existing Union. Use Union[u, t] instead.")
        jeżeli parameters == ():
            podnieś TypeError("Cannot take a Union of no types.")
        jeżeli nie isinstance(parameters, tuple):
            parameters = (parameters,)
        zwróć self.__class__(self.__name__, self.__bases__,
                              dict(self.__dict__), parameters, _root=Prawda)

    def __eq__(self, other):
        jeżeli nie isinstance(other, UnionMeta):
            zwróć NotImplemented
        zwróć self.__union_set_params__ == other.__union_set_params__

    def __hash__(self):
        zwróć hash(self.__union_set_params__)

    def __instancecheck__(self, obj):
        podnieś TypeError("Unions cannot be used przy isinstance().")

    def __subclasscheck__(self, cls):
        jeżeli cls jest Any:
            zwróć Prawda
        jeżeli self.__union_params__ jest Nic:
            zwróć isinstance(cls, UnionMeta)
        albo_inaczej isinstance(cls, UnionMeta):
            jeżeli cls.__union_params__ jest Nic:
                zwróć Nieprawda
            zwróć all(issubclass(c, self) dla c w (cls.__union_params__))
        albo_inaczej isinstance(cls, TypeVar):
            jeżeli cls w self.__union_params__:
                zwróć Prawda
            jeżeli cls.__constraints__:
                zwróć issubclass(Union[cls.__constraints__], self)
            zwróć Nieprawda
        inaczej:
            zwróć any(issubclass(cls, t) dla t w self.__union_params__)


klasa Union(Final, metaclass=UnionMeta, _root=Prawda):
    """Union type; Union[X, Y] means either X albo Y.

    To define a union, use e.g. Union[int, str].  Details:

    - The arguments must be types oraz there must be at least one.

    - Nic jako an argument jest a special case oraz jest replaced by
      type(Nic).

    - Unions of unions are flattened, e.g.::

        Union[Union[int, str], float] == Union[int, str, float]

    - Unions of a single argument vanish, e.g.::

        Union[int] == int  # The constructor actually returns int

    - Redundant arguments are skipped, e.g.::

        Union[int, str, int] == Union[int, str]

    - When comparing unions, the argument order jest ignored, e.g.::

        Union[int, str] == Union[str, int]

    - When two arguments have a subclass relationship, the least
      derived argument jest kept, e.g.::

        klasa Employee: dalej
        klasa Manager(Employee): dalej
        Union[int, Employee, Manager] == Union[int, Employee]
        Union[Manager, int, Employee] == Union[int, Employee]
        Union[Employee, Manager] == Employee

    - Corollary: jeżeli Any jest present it jest the sole survivor, e.g.::

        Union[int, Any] == Any

    - Similar dla object::

        Union[int, object] == object

    - To cut a tie: Union[object, Any] == Union[Any, object] == Any.

    - You cannot subclass albo instantiate a union.

    - You cannot write Union[X][Y] (what would it mean?).

    - You can use Optional[X] jako a shorthand dla Union[X, Nic].
    """

    # Unsubscripted Union type has params set to Nic.
    __union_params__ = Nic
    __union_set_params__ = Nic


klasa OptionalMeta(TypingMeta):
    """Metaclass dla Optional."""

    def __new__(cls, name, bases, namespace, _root=Nieprawda):
        zwróć super().__new__(cls, name, bases, namespace, _root=_root)

    def __getitem__(self, arg):
        arg = _type_check(arg, "Optional[t] requires a single type.")
        zwróć Union[arg, type(Nic)]


klasa Optional(Final, metaclass=OptionalMeta, _root=Prawda):
    """Optional type.

    Optional[X] jest equivalent to Union[X, type(Nic)].
    """

    __slots__ = ()


klasa TupleMeta(TypingMeta):
    """Metaclass dla Tuple."""

    def __new__(cls, name, bases, namespace, parameters=Nic,
                use_ellipsis=Nieprawda, _root=Nieprawda):
        self = super().__new__(cls, name, bases, namespace, _root=_root)
        self.__tuple_params__ = parameters
        self.__tuple_use_ellipsis__ = use_ellipsis
        zwróć self

    def _has_type_var(self):
        jeżeli self.__tuple_params__:
            dla t w self.__tuple_params__:
                jeżeli _has_type_var(t):
                    zwróć Prawda
        zwróć Nieprawda

    def _eval_type(self, globalns, localns):
        tp = self.__tuple_params__
        jeżeli tp jest Nic:
            zwróć self
        p = tuple(_eval_type(t, globalns, localns) dla t w tp)
        jeżeli p == self.__tuple_params__:
            zwróć self
        inaczej:
            zwróć self.__class__(self.__name__, self.__bases__, {},
                                  p, _root=Prawda)

    def __repr__(self):
        r = super().__repr__()
        jeżeli self.__tuple_params__ jest nie Nic:
            params = [_type_repr(p) dla p w self.__tuple_params__]
            jeżeli self.__tuple_use_ellipsis__:
                params.append('...')
            r += '[%s]' % (
                ', '.join(params))
        zwróć r

    def __getitem__(self, parameters):
        jeżeli self.__tuple_params__ jest nie Nic:
            podnieś TypeError("Cannot re-parameterize %r" % (self,))
        jeżeli nie isinstance(parameters, tuple):
            parameters = (parameters,)
        jeżeli len(parameters) == 2 oraz parameters[1] == Ellipsis:
            parameters = parameters[:1]
            use_ellipsis = Prawda
            msg = "Tuple[t, ...]: t must be a type."
        inaczej:
            use_ellipsis = Nieprawda
            msg = "Tuple[t0, t1, ...]: each t must be a type."
        parameters = tuple(_type_check(p, msg) dla p w parameters)
        zwróć self.__class__(self.__name__, self.__bases__,
                              dict(self.__dict__), parameters,
                              use_ellipsis=use_ellipsis, _root=Prawda)

    def __eq__(self, other):
        jeżeli nie isinstance(other, TupleMeta):
            zwróć NotImplemented
        zwróć self.__tuple_params__ == other.__tuple_params__

    def __hash__(self):
        zwróć hash(self.__tuple_params__)

    def __instancecheck__(self, obj):
        podnieś TypeError("Tuples cannot be used przy isinstance().")

    def __subclasscheck__(self, cls):
        jeżeli cls jest Any:
            zwróć Prawda
        jeżeli nie isinstance(cls, type):
            zwróć super().__subclasscheck__(cls)  # To TypeError.
        jeżeli issubclass(cls, tuple):
            zwróć Prawda  # Special case.
        jeżeli nie isinstance(cls, TupleMeta):
            zwróć super().__subclasscheck__(cls)  # Nieprawda.
        jeżeli self.__tuple_params__ jest Nic:
            zwróć Prawda
        jeżeli cls.__tuple_params__ jest Nic:
            zwróć Nieprawda  # ???
        jeżeli cls.__tuple_use_ellipsis__ != self.__tuple_use_ellipsis__:
            zwróć Nieprawda
        # Covariance.
        zwróć (len(self.__tuple_params__) == len(cls.__tuple_params__) oraz
                all(issubclass(x, p)
                    dla x, p w zip(cls.__tuple_params__,
                                    self.__tuple_params__)))


klasa Tuple(Final, metaclass=TupleMeta, _root=Prawda):
    """Tuple type; Tuple[X, Y] jest the cross-product type of X oraz Y.

    Example: Tuple[T1, T2] jest a tuple of two elements corresponding
    to type variables T1 oraz T2.  Tuple[int, float, str] jest a tuple
    of an int, a float oraz a string.

    To specify a variable-length tuple of homogeneous type, use Sequence[T].
    """

    __slots__ = ()


klasa CallableMeta(TypingMeta):
    """Metaclass dla Callable."""

    def __new__(cls, name, bases, namespace, _root=Nieprawda,
                args=Nic, result=Nic):
        jeżeli args jest Nic oraz result jest Nic:
            dalej  # Must be 'class Callable'.
        inaczej:
            jeżeli args jest nie Ellipsis:
                jeżeli nie isinstance(args, list):
                    podnieś TypeError("Callable[args, result]: "
                                    "args must be a list."
                                    " Got %.100r." % (args,))
                msg = "Callable[[arg, ...], result]: each arg must be a type."
                args = tuple(_type_check(arg, msg) dla arg w args)
            msg = "Callable[args, result]: result must be a type."
            result = _type_check(result, msg)
        self = super().__new__(cls, name, bases, namespace, _root=_root)
        self.__args__ = args
        self.__result__ = result
        zwróć self

    def _has_type_var(self):
        jeżeli self.__args__:
            dla t w self.__args__:
                jeżeli _has_type_var(t):
                    zwróć Prawda
        zwróć _has_type_var(self.__result__)

    def _eval_type(self, globalns, localns):
        jeżeli self.__args__ jest Nic oraz self.__result__ jest Nic:
            zwróć self
        jeżeli self.__args__ jest Ellipsis:
            args = self.__args__
        inaczej:
            args = [_eval_type(t, globalns, localns) dla t w self.__args__]
        result = _eval_type(self.__result__, globalns, localns)
        jeżeli args == self.__args__ oraz result == self.__result__:
            zwróć self
        inaczej:
            zwróć self.__class__(self.__name__, self.__bases__, {},
                                  args=args, result=result, _root=Prawda)

    def __repr__(self):
        r = super().__repr__()
        jeżeli self.__args__ jest nie Nic albo self.__result__ jest nie Nic:
            jeżeli self.__args__ jest Ellipsis:
                args_r = '...'
            inaczej:
                args_r = '[%s]' % ', '.join(_type_repr(t)
                                            dla t w self.__args__)
            r += '[%s, %s]' % (args_r, _type_repr(self.__result__))
        zwróć r

    def __getitem__(self, parameters):
        jeżeli self.__args__ jest nie Nic albo self.__result__ jest nie Nic:
            podnieś TypeError("This Callable type jest already parameterized.")
        jeżeli nie isinstance(parameters, tuple) albo len(parameters) != 2:
            podnieś TypeError(
                "Callable must be used jako Callable[[arg, ...], result].")
        args, result = parameters
        zwróć self.__class__(self.__name__, self.__bases__,
                              dict(self.__dict__), _root=Prawda,
                              args=args, result=result)

    def __eq__(self, other):
        jeżeli nie isinstance(other, CallableMeta):
            zwróć NotImplemented
        zwróć (self.__args__ == other.__args__ oraz
                self.__result__ == other.__result__)

    def __hash__(self):
        zwróć hash(self.__args__) ^ hash(self.__result__)

    def __instancecheck__(self, obj):
        # For unparametrized Callable we allow this, because
        # typing.Callable should be equivalent to
        # collections.abc.Callable.
        jeżeli self.__args__ jest Nic oraz self.__result__ jest Nic:
            zwróć isinstance(obj, collections_abc.Callable)
        inaczej:
            podnieś TypeError("Callable[] cannot be used przy isinstance().")

    def __subclasscheck__(self, cls):
        jeżeli cls jest Any:
            zwróć Prawda
        jeżeli nie isinstance(cls, CallableMeta):
            zwróć super().__subclasscheck__(cls)
        jeżeli self.__args__ jest Nic oraz self.__result__ jest Nic:
            zwróć Prawda
        # We're nie doing covariance albo contravariance -- this jest *invariance*.
        zwróć self == cls


klasa Callable(Final, metaclass=CallableMeta, _root=Prawda):
    """Callable type; Callable[[int], str] jest a function of (int) -> str.

    The subscription syntax must always be used przy exactly two
    values: the argument list oraz the zwróć type.  The argument list
    must be a list of types; the zwróć type must be a single type.

    There jest no syntax to indicate optional albo keyword arguments,
    such function types are rarely used jako callback types.
    """

    __slots__ = ()


def _gorg(a):
    """Return the farthest origin of a generic class."""
    assert isinstance(a, GenericMeta)
    dopóki a.__origin__ jest nie Nic:
        a = a.__origin__
    zwróć a


def _geqv(a, b):
    """Return whether two generic classes are equivalent.

    The intention jest to consider generic klasa X oraz any of its
    parameterized forms (X[T], X[int], etc.)  jako equivalent.

    However, X jest nie equivalent to a subclass of X.

    The relation jest reflexive, symmetric oraz transitive.
    """
    assert isinstance(a, GenericMeta) oraz isinstance(b, GenericMeta)
    # Reduce each to its origin.
    zwróć _gorg(a) jest _gorg(b)


klasa GenericMeta(TypingMeta, abc.ABCMeta):
    """Metaclass dla generic types."""

    # TODO: Constrain more how Generic jest used; only a few
    # standard patterns should be allowed.

    # TODO: Use a more precise rule than matching __name__ to decide
    # whether two classes are the same.  Also, save the formal
    # parameters.  (These things are related!  A solution lies w
    # using origin.)

    __extra__ = Nic

    def __new__(cls, name, bases, namespace,
                parameters=Nic, origin=Nic, extra=Nic):
        jeżeli parameters jest Nic:
            # Extract parameters z direct base classes.  Only
            # direct bases are considered oraz only those that are
            # themselves generic, oraz parameterized przy type
            # variables.  Don't use bases like Any, Union, Tuple,
            # Callable albo type variables.
            params = Nic
            dla base w bases:
                jeżeli isinstance(base, TypingMeta):
                    jeżeli nie isinstance(base, GenericMeta):
                        podnieś TypeError(
                            "You cannot inherit z magic klasa %s" %
                            repr(base))
                    jeżeli base.__parameters__ jest Nic:
                        continue  # The base jest unparameterized.
                    dla bp w base.__parameters__:
                        jeżeli _has_type_var(bp) oraz nie isinstance(bp, TypeVar):
                            podnieś TypeError(
                                "Cannot inherit z a generic klasa "
                                "parameterized przy "
                                "non-type-variable %s" % bp)
                        jeżeli params jest Nic:
                            params = []
                        jeżeli bp nie w params:
                            params.append(bp)
            jeżeli params jest nie Nic:
                parameters = tuple(params)
        self = super().__new__(cls, name, bases, namespace, _root=Prawda)
        self.__parameters__ = parameters
        jeżeli extra jest nie Nic:
            self.__extra__ = extra
        # Else __extra__ jest inherited, eventually z the
        # (meta-)class default above.
        self.__origin__ = origin
        zwróć self

    def _has_type_var(self):
        jeżeli self.__parameters__:
            dla t w self.__parameters__:
                jeżeli _has_type_var(t):
                    zwróć Prawda
        zwróć Nieprawda

    def __repr__(self):
        r = super().__repr__()
        jeżeli self.__parameters__ jest nie Nic:
            r += '[%s]' % (
                ', '.join(_type_repr(p) dla p w self.__parameters__))
        zwróć r

    def __eq__(self, other):
        jeżeli nie isinstance(other, GenericMeta):
            zwróć NotImplemented
        zwróć (_geqv(self, other) oraz
                self.__parameters__ == other.__parameters__)

    def __hash__(self):
        zwróć hash((self.__name__, self.__parameters__))

    def __getitem__(self, params):
        jeżeli nie isinstance(params, tuple):
            params = (params,)
        jeżeli nie params:
            podnieś TypeError("Cannot have empty parameter list")
        msg = "Parameters to generic types must be types."
        params = tuple(_type_check(p, msg) dla p w params)
        jeżeli self.__parameters__ jest Nic:
            dla p w params:
                jeżeli nie isinstance(p, TypeVar):
                    podnieś TypeError("Initial parameters must be "
                                    "type variables; got %s" % p)
            jeżeli len(set(params)) != len(params):
                podnieś TypeError(
                    "All type variables w Generic[...] must be distinct.")
        inaczej:
            jeżeli len(params) != len(self.__parameters__):
                podnieś TypeError("Cannot change parameter count z %d to %d" %
                                (len(self.__parameters__), len(params)))
            dla new, old w zip(params, self.__parameters__):
                jeżeli isinstance(old, TypeVar):
                    jeżeli nie old.__constraints__:
                        # Substituting dla an unconstrained TypeVar jest OK.
                        kontynuuj
                    jeżeli issubclass(new, Union[old.__constraints__]):
                        # Specializing a constrained type variable jest OK.
                        kontynuuj
                jeżeli nie issubclass(new, old):
                    podnieś TypeError(
                        "Cannot substitute %s dla %s w %s" %
                        (_type_repr(new), _type_repr(old), self))

        zwróć self.__class__(self.__name__, self.__bases__,
                              dict(self.__dict__),
                              parameters=params,
                              origin=self,
                              extra=self.__extra__)

    def __instancecheck__(self, instance):
        # Since we extend ABC.__subclasscheck__ oraz
        # ABC.__instancecheck__ inlines the cache checking done by the
        # latter, we must extend __instancecheck__ too. For simplicity
        # we just skip the cache check -- instance checks dla generic
        # classes are supposed to be rare anyways.
        zwróć self.__subclasscheck__(instance.__class__)

    def __subclasscheck__(self, cls):
        jeżeli cls jest Any:
            zwróć Prawda
        jeżeli isinstance(cls, GenericMeta):
            # For a klasa C(Generic[T]) where T jest co-variant,
            # C[X] jest a subclass of C[Y] iff X jest a subclass of Y.
            origin = self.__origin__
            jeżeli origin jest nie Nic oraz origin jest cls.__origin__:
                assert len(self.__parameters__) == len(origin.__parameters__)
                assert len(cls.__parameters__) == len(origin.__parameters__)
                dla p_self, p_cls, p_origin w zip(self.__parameters__,
                                                   cls.__parameters__,
                                                   origin.__parameters__):
                    jeżeli isinstance(p_origin, TypeVar):
                        jeżeli p_origin.__covariant__:
                            # Covariant -- p_cls must be a subclass of p_self.
                            jeżeli nie issubclass(p_cls, p_self):
                                przerwij
                        albo_inaczej p_origin.__contravariant__:
                            # Contravariant.  I think it's the opposite. :-)
                            jeżeli nie issubclass(p_self, p_cls):
                                przerwij
                        inaczej:
                            # Invariant -- p_cls oraz p_self must equal.
                            jeżeli p_self != p_cls:
                                przerwij
                    inaczej:
                        # If the origin's parameter jest nie a typevar,
                        # insist on invariance.
                        jeżeli p_self != p_cls:
                            przerwij
                inaczej:
                    zwróć Prawda
                # If we przerwij out of the loop, the superclass gets a chance.
        jeżeli super().__subclasscheck__(cls):
            zwróć Prawda
        jeżeli self.__extra__ jest Nic albo isinstance(cls, GenericMeta):
            zwróć Nieprawda
        zwróć issubclass(cls, self.__extra__)


klasa Generic(metaclass=GenericMeta):
    """Abstract base klasa dla generic types.

    A generic type jest typically declared by inheriting z an
    instantiation of this klasa przy one albo more type variables.
    For example, a generic mapping type might be defined as::

      klasa Mapping(Generic[KT, VT]):
          def __getitem__(self, key: KT) -> VT:
              ...
          # Etc.

    This klasa can then be used jako follows::

      def lookup_name(mapping: Mapping, key: KT, default: VT) -> VT:
          spróbuj:
              zwróć mapping[key]
          wyjąwszy KeyError:
              zwróć default

    For clarity the type variables may be redefined, e.g.::

      X = TypeVar('X')
      Y = TypeVar('Y')
      def lookup_name(mapping: Mapping[X, Y], key: X, default: Y) -> Y:
          # Same body jako above.
    """

    __slots__ = ()

    def __new__(cls, *args, **kwds):
        next_in_mro = object
        # Look dla the last occurrence of Generic albo Generic[...].
        dla i, c w enumerate(cls.__mro__[:-1]):
            jeżeli isinstance(c, GenericMeta) oraz _gorg(c) jest Generic:
                next_in_mro = cls.__mro__[i+1]
        zwróć next_in_mro.__new__(_gorg(cls))


def cast(typ, val):
    """Cast a value to a type.

    This returns the value unchanged.  To the type checker this
    signals that the zwróć value has the designated type, but at
    runtime we intentionally don't check anything (we want this
    to be jako fast jako possible).
    """
    zwróć val


def _get_defaults(func):
    """Internal helper to extract the default arguments, by name."""
    code = func.__code__
    pos_count = code.co_argcount
    kw_count = code.co_kwonlyargcount
    arg_names = code.co_varnames
    kwarg_names = arg_names[pos_count:pos_count + kw_count]
    arg_names = arg_names[:pos_count]
    defaults = func.__defaults__ albo ()
    kwdefaults = func.__kwdefaults__
    res = dict(kwdefaults) jeżeli kwdefaults inaczej {}
    pos_offset = pos_count - len(defaults)
    dla name, value w zip(arg_names[pos_offset:], defaults):
        assert name nie w res
        res[name] = value
    zwróć res


def get_type_hints(obj, globalns=Nic, localns=Nic):
    """Return type hints dla a function albo method object.

    This jest often the same jako obj.__annotations__, but it handles
    forward references encoded jako string literals, oraz jeżeli necessary
    adds Optional[t] jeżeli a default value equal to Nic jest set.

    BEWARE -- the behavior of globalns oraz localns jest counterintuitive
    (unless you are familiar przy how eval() oraz exec() work).  The
    search order jest locals first, then globals.

    - If no dict arguments are dalejed, an attempt jest made to use the
      globals z obj, oraz these are also used jako the locals.  If the
      object does nie appear to have globals, an exception jest podnieśd.

    - If one dict argument jest dalejed, it jest used dla both globals oraz
      locals.

    - If two dict arguments are dalejed, they specify globals oraz
      locals, respectively.
    """
    jeżeli getattr(obj, '__no_type_check__', Nic):
        zwróć {}
    jeżeli globalns jest Nic:
        globalns = getattr(obj, '__globals__', {})
        jeżeli localns jest Nic:
            localns = globalns
    albo_inaczej localns jest Nic:
        localns = globalns
    defaults = _get_defaults(obj)
    hints = dict(obj.__annotations__)
    dla name, value w hints.items():
        jeżeli isinstance(value, str):
            value = _ForwardRef(value)
        value = _eval_type(value, globalns, localns)
        jeżeli name w defaults oraz defaults[name] jest Nic:
            value = Optional[value]
        hints[name] = value
    zwróć hints


# TODO: Also support this jako a klasa decorator.
def no_type_check(arg):
    """Decorator to indicate that annotations are nie type hints.

    The argument must be a klasa albo function; jeżeli it jest a class, it
    applies recursively to all methods defined w that klasa (but nie
    to methods defined w its superclasses albo subclasses).

    This mutates the function(s) w place.
    """
    jeżeli isinstance(arg, type):
        dla obj w arg.__dict__.values():
            jeżeli isinstance(obj, types.FunctionType):
                obj.__no_type_check__ = Prawda
    inaczej:
        arg.__no_type_check__ = Prawda
    zwróć arg


def no_type_check_decorator(decorator):
    """Decorator to give another decorator the @no_type_check effect.

    This wraps the decorator przy something that wraps the decorated
    function w @no_type_check.
    """

    @functools.wraps(decorator)
    def wrapped_decorator(*args, **kwds):
        func = decorator(*args, **kwds)
        func = no_type_check(func)
        zwróć func

    zwróć wrapped_decorator


def overload(func):
    podnieś RuntimeError("Overloading jest only supported w library stubs")


klasa _ProtocolMeta(GenericMeta):
    """Internal metaclass dla _Protocol.

    This exists so _Protocol classes can be generic without deriving
    z Generic.
    """

    def __instancecheck__(self, obj):
        podnieś TypeError("Protocols cannot be used przy isinstance().")

    def __subclasscheck__(self, cls):
        jeżeli nie self._is_protocol:
            # No structural checks since this isn't a protocol.
            zwróć NotImplemented

        jeżeli self jest _Protocol:
            # Every klasa jest a subclass of the empty protocol.
            zwróć Prawda

        # Find all attributes defined w the protocol.
        attrs = self._get_protocol_attrs()

        dla attr w attrs:
            jeżeli nie any(attr w d.__dict__ dla d w cls.__mro__):
                zwróć Nieprawda
        zwróć Prawda

    def _get_protocol_attrs(self):
        # Get all Protocol base classes.
        protocol_bases = []
        dla c w self.__mro__:
            jeżeli getattr(c, '_is_protocol', Nieprawda) oraz c.__name__ != '_Protocol':
                protocol_bases.append(c)

        # Get attributes included w protocol.
        attrs = set()
        dla base w protocol_bases:
            dla attr w base.__dict__.keys():
                # Include attributes nie defined w any non-protocol bases.
                dla c w self.__mro__:
                    jeżeli (c jest nie base oraz attr w c.__dict__ oraz
                            nie getattr(c, '_is_protocol', Nieprawda)):
                        przerwij
                inaczej:
                    jeżeli (nie attr.startswith('_abc_') oraz
                        attr != '__abstractmethods__' oraz
                        attr != '_is_protocol' oraz
                        attr != '__dict__' oraz
                        attr != '__slots__' oraz
                        attr != '_get_protocol_attrs' oraz
                        attr != '__parameters__' oraz
                        attr != '__origin__' oraz
                        attr != '__module__'):
                        attrs.add(attr)

        zwróć attrs


klasa _Protocol(metaclass=_ProtocolMeta):
    """Internal base klasa dla protocol classes.

    This implements a simple-minded structural isinstance check
    (similar but more general than the one-offs w collections.abc
    such jako Hashable).
    """

    __slots__ = ()

    _is_protocol = Prawda


# Various ABCs mimicking those w collections.abc.
# A few are simply re-exported dla completeness.

Hashable = collections_abc.Hashable  # Not generic.


klasa Iterable(Generic[T_co], extra=collections_abc.Iterable):
    __slots__ = ()


klasa Iterator(Iterable[T_co], extra=collections_abc.Iterator):
    __slots__ = ()


klasa SupportsInt(_Protocol):
    __slots__ = ()

    @abstractmethod
    def __int__(self) -> int:
        dalej


klasa SupportsFloat(_Protocol):
    __slots__ = ()

    @abstractmethod
    def __float__(self) -> float:
        dalej


klasa SupportsComplex(_Protocol):
    __slots__ = ()

    @abstractmethod
    def __complex__(self) -> complex:
        dalej


klasa SupportsBytes(_Protocol):
    __slots__ = ()

    @abstractmethod
    def __bytes__(self) -> bytes:
        dalej


klasa SupportsAbs(_Protocol[T_co]):
    __slots__ = ()

    @abstractmethod
    def __abs__(self) -> T_co:
        dalej


klasa SupportsRound(_Protocol[T_co]):
    __slots__ = ()

    @abstractmethod
    def __round__(self, ndigits: int = 0) -> T_co:
        dalej


klasa Reversible(_Protocol[T_co]):
    __slots__ = ()

    @abstractmethod
    def __reversed__(self) -> 'Iterator[T_co]':
        dalej


Sized = collections_abc.Sized  # Not generic.


klasa Container(Generic[T_co], extra=collections_abc.Container):
    __slots__ = ()


# Callable was defined earlier.


klasa AbstractSet(Sized, Iterable[T_co], Container[T_co],
                  extra=collections_abc.Set):
    dalej


klasa MutableSet(AbstractSet[T], extra=collections_abc.MutableSet):
    dalej


# NOTE: Only the value type jest covariant.
klasa Mapping(Sized, Iterable[KT], Container[KT], Generic[VT_co],
              extra=collections_abc.Mapping):
    dalej


klasa MutableMapping(Mapping[KT, VT], extra=collections_abc.MutableMapping):
    dalej


klasa Sequence(Sized, Iterable[T_co], Container[T_co],
               extra=collections_abc.Sequence):
    dalej


klasa MutableSequence(Sequence[T], extra=collections_abc.MutableSequence):
    dalej


klasa ByteString(Sequence[int], extra=collections_abc.ByteString):
    dalej


ByteString.register(type(memoryview(b'')))


klasa List(list, MutableSequence[T]):

    def __new__(cls, *args, **kwds):
        jeżeli _geqv(cls, List):
            podnieś TypeError("Type List cannot be instantiated; "
                            "use list() instead")
        zwróć list.__new__(cls, *args, **kwds)


klasa Set(set, MutableSet[T]):

    def __new__(cls, *args, **kwds):
        jeżeli _geqv(cls, Set):
            podnieś TypeError("Type Set cannot be instantiated; "
                            "use set() instead")
        zwróć set.__new__(cls, *args, **kwds)


klasa _FrozenSetMeta(GenericMeta):
    """This metaclass ensures set jest nie a subclass of FrozenSet.

    Without this metaclass, set would be considered a subclass of
    FrozenSet, because FrozenSet.__extra__ jest collections.abc.Set, oraz
    set jest a subclass of that.
    """

    def __subclasscheck__(self, cls):
        jeżeli issubclass(cls, Set):
            zwróć Nieprawda
        zwróć super().__subclasscheck__(cls)


klasa FrozenSet(frozenset, AbstractSet[T_co], metaclass=_FrozenSetMeta):
    __slots__ = ()

    def __new__(cls, *args, **kwds):
        jeżeli _geqv(cls, FrozenSet):
            podnieś TypeError("Type FrozenSet cannot be instantiated; "
                            "use frozenset() instead")
        zwróć frozenset.__new__(cls, *args, **kwds)


klasa MappingView(Sized, Iterable[T_co], extra=collections_abc.MappingView):
    dalej


klasa KeysView(MappingView[KT], AbstractSet[KT],
               extra=collections_abc.KeysView):
    dalej


# TODO: Enable Set[Tuple[KT, VT_co]] instead of Generic[KT, VT_co].
klasa ItemsView(MappingView, Generic[KT, VT_co],
                extra=collections_abc.ItemsView):
    dalej


klasa ValuesView(MappingView[VT_co], extra=collections_abc.ValuesView):
    dalej


klasa Dict(dict, MutableMapping[KT, VT]):

    def __new__(cls, *args, **kwds):
        jeżeli _geqv(cls, Dict):
            podnieś TypeError("Type Dict cannot be instantiated; "
                            "use dict() instead")
        zwróć dict.__new__(cls, *args, **kwds)


# Determine what base klasa to use dla Generator.
jeżeli hasattr(collections_abc, 'Generator'):
    # Sufficiently recent versions of 3.5 have a Generator ABC.
    _G_base = collections_abc.Generator
inaczej:
    # Fall back on the exact type.
    _G_base = types.GeneratorType


klasa Generator(Iterator[T_co], Generic[T_co, T_contra, V_co],
                extra=_G_base):
    __slots__ = ()

    def __new__(cls, *args, **kwds):
        jeżeli _geqv(cls, Generator):
            podnieś TypeError("Type Generator cannot be instantiated; "
                            "create a subclass instead")
        zwróć super().__new__(cls, *args, **kwds)


def NamedTuple(typename, fields):
    """Typed version of namedtuple.

    Usage::

        Employee = typing.NamedTuple('Employee', [('name', str), 'id', int)])

    This jest equivalent to::

        Employee = collections.namedtuple('Employee', ['name', 'id'])

    The resulting klasa has one extra attribute: _field_types,
    giving a dict mapping field names to types.  (The field names
    are w the _fields attribute, which jest part of the namedtuple
    API.)
    """
    fields = [(n, t) dla n, t w fields]
    cls = collections.namedtuple(typename, [n dla n, t w fields])
    cls._field_types = dict(fields)
    zwróć cls


klasa IO(Generic[AnyStr]):
    """Generic base klasa dla TextIO oraz BinaryIO.

    This jest an abstract, generic version of the zwróć of open().

    NOTE: This does nie distinguish between the different possible
    classes (text vs. binary, read vs. write vs. read/write,
    append-only, unbuffered).  The TextIO oraz BinaryIO subclasses
    below capture the distinctions between text vs. binary, which jest
    pervasive w the interface; however we currently do nie offer a
    way to track the other distinctions w the type system.
    """

    __slots__ = ()

    @abstractproperty
    def mode(self) -> str:
        dalej

    @abstractproperty
    def name(self) -> str:
        dalej

    @abstractmethod
    def close(self) -> Nic:
        dalej

    @abstractmethod
    def closed(self) -> bool:
        dalej

    @abstractmethod
    def fileno(self) -> int:
        dalej

    @abstractmethod
    def flush(self) -> Nic:
        dalej

    @abstractmethod
    def isatty(self) -> bool:
        dalej

    @abstractmethod
    def read(self, n: int = -1) -> AnyStr:
        dalej

    @abstractmethod
    def readable(self) -> bool:
        dalej

    @abstractmethod
    def readline(self, limit: int = -1) -> AnyStr:
        dalej

    @abstractmethod
    def readlines(self, hint: int = -1) -> List[AnyStr]:
        dalej

    @abstractmethod
    def seek(self, offset: int, whence: int = 0) -> int:
        dalej

    @abstractmethod
    def seekable(self) -> bool:
        dalej

    @abstractmethod
    def tell(self) -> int:
        dalej

    @abstractmethod
    def truncate(self, size: int = Nic) -> int:
        dalej

    @abstractmethod
    def writable(self) -> bool:
        dalej

    @abstractmethod
    def write(self, s: AnyStr) -> int:
        dalej

    @abstractmethod
    def writelines(self, lines: List[AnyStr]) -> Nic:
        dalej

    @abstractmethod
    def __enter__(self) -> 'IO[AnyStr]':
        dalej

    @abstractmethod
    def __exit__(self, type, value, traceback) -> Nic:
        dalej


klasa BinaryIO(IO[bytes]):
    """Typed version of the zwróć of open() w binary mode."""

    __slots__ = ()

    @abstractmethod
    def write(self, s: Union[bytes, bytearray]) -> int:
        dalej

    @abstractmethod
    def __enter__(self) -> 'BinaryIO':
        dalej


klasa TextIO(IO[str]):
    """Typed version of the zwróć of open() w text mode."""

    __slots__ = ()

    @abstractproperty
    def buffer(self) -> BinaryIO:
        dalej

    @abstractproperty
    def encoding(self) -> str:
        dalej

    @abstractproperty
    def errors(self) -> str:
        dalej

    @abstractproperty
    def line_buffering(self) -> bool:
        dalej

    @abstractproperty
    def newlines(self) -> Any:
        dalej

    @abstractmethod
    def __enter__(self) -> 'TextIO':
        dalej


klasa io:
    """Wrapper namespace dla IO generic classes."""

    __all__ = ['IO', 'TextIO', 'BinaryIO']
    IO = IO
    TextIO = TextIO
    BinaryIO = BinaryIO

io.__name__ = __name__ + '.io'
sys.modules[io.__name__] = io


Pattern = _TypeAlias('Pattern', AnyStr, type(stdlib_re.compile('')),
                     lambda p: p.pattern)
Match = _TypeAlias('Match', AnyStr, type(stdlib_re.match('', '')),
                   lambda m: m.re.pattern)


klasa re:
    """Wrapper namespace dla re type aliases."""

    __all__ = ['Pattern', 'Match']
    Pattern = Pattern
    Match = Match

re.__name__ = __name__ + '.re'
sys.modules[re.__name__] = re
