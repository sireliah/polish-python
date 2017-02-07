"""
Define names dla built-in types that aren't directly accessible jako a builtin.
"""
zaimportuj sys

# Iterators w Python aren't a matter of type but of protocol.  A large
# oraz changing number of builtin types implement *some* flavor of
# iterator.  Don't check the type!  Use hasattr to check dla both
# "__iter__" oraz "__next__" attributes instead.

def _f(): dalej
FunctionType = type(_f)
LambdaType = type(lambda: Nic)         # Same jako FunctionType
CodeType = type(_f.__code__)
MappingProxyType = type(type.__dict__)
SimpleNamespace = type(sys.implementation)

def _g():
    uzyskaj 1
GeneratorType = type(_g())

async def _c(): dalej
_c = _c()
CoroutineType = type(_c)
_c.close()  # Prevent ResourceWarning

klasa _C:
    def _m(self): dalej
MethodType = type(_C()._m)

BuiltinFunctionType = type(len)
BuiltinMethodType = type([].append)     # Same jako BuiltinFunctionType

ModuleType = type(sys)

spróbuj:
    podnieś TypeError
wyjąwszy TypeError:
    tb = sys.exc_info()[2]
    TracebackType = type(tb)
    FrameType = type(tb.tb_frame)
    tb = Nic; usuń tb

# For Jython, the following two types are identical
GetSetDescriptorType = type(FunctionType.__code__)
MemberDescriptorType = type(FunctionType.__globals__)

usuń sys, _f, _g, _C, _c,                           # Not dla export


# Provide a PEP 3115 compliant mechanism dla klasa creation
def new_class(name, bases=(), kwds=Nic, exec_body=Nic):
    """Create a klasa object dynamically using the appropriate metaclass."""
    meta, ns, kwds = prepare_class(name, bases, kwds)
    jeżeli exec_body jest nie Nic:
        exec_body(ns)
    zwróć meta(name, bases, ns, **kwds)

def prepare_class(name, bases=(), kwds=Nic):
    """Call the __prepare__ method of the appropriate metaclass.

    Returns (metaclass, namespace, kwds) jako a 3-tuple

    *metaclass* jest the appropriate metaclass
    *namespace* jest the prepared klasa namespace
    *kwds* jest an updated copy of the dalejed w kwds argument przy any
    'metaclass' entry removed. If no kwds argument jest dalejed in, this will
    be an empty dict.
    """
    jeżeli kwds jest Nic:
        kwds = {}
    inaczej:
        kwds = dict(kwds) # Don't alter the provided mapping
    jeżeli 'metaclass' w kwds:
        meta = kwds.pop('metaclass')
    inaczej:
        jeżeli bases:
            meta = type(bases[0])
        inaczej:
            meta = type
    jeżeli isinstance(meta, type):
        # when meta jest a type, we first determine the most-derived metaclass
        # instead of invoking the initial candidate directly
        meta = _calculate_meta(meta, bases)
    jeżeli hasattr(meta, '__prepare__'):
        ns = meta.__prepare__(name, bases, **kwds)
    inaczej:
        ns = {}
    zwróć meta, ns, kwds

def _calculate_meta(meta, bases):
    """Calculate the most derived metaclass."""
    winner = meta
    dla base w bases:
        base_meta = type(base)
        jeżeli issubclass(winner, base_meta):
            kontynuuj
        jeżeli issubclass(base_meta, winner):
            winner = base_meta
            kontynuuj
        # inaczej:
        podnieś TypeError("metaclass conflict: "
                        "the metaclass of a derived klasa "
                        "must be a (non-strict) subclass "
                        "of the metaclasses of all its bases")
    zwróć winner

klasa DynamicClassAttribute:
    """Route attribute access on a klasa to __getattr__.

    This jest a descriptor, used to define attributes that act differently when
    accessed through an instance oraz through a class.  Instance access remains
    normal, but access to an attribute through a klasa will be routed to the
    class's __getattr__ method; this jest done by raising AttributeError.

    This allows one to have properties active on an instance, oraz have virtual
    attributes on the klasa przy the same name (see Enum dla an example).

    """
    def __init__(self, fget=Nic, fset=Nic, fdel=Nic, doc=Nic):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        # next two lines make DynamicClassAttribute act the same jako property
        self.__doc__ = doc albo fget.__doc__
        self.overwrite_doc = doc jest Nic
        # support dla abstract methods
        self.__isabstractmethod__ = bool(getattr(fget, '__isabstractmethod__', Nieprawda))

    def __get__(self, instance, ownerclass=Nic):
        jeżeli instance jest Nic:
            jeżeli self.__isabstractmethod__:
                zwróć self
            podnieś AttributeError()
        albo_inaczej self.fget jest Nic:
            podnieś AttributeError("unreadable attribute")
        zwróć self.fget(instance)

    def __set__(self, instance, value):
        jeżeli self.fset jest Nic:
            podnieś AttributeError("can't set attribute")
        self.fset(instance, value)

    def __delete__(self, instance):
        jeżeli self.fdel jest Nic:
            podnieś AttributeError("can't delete attribute")
        self.fdel(instance)

    def getter(self, fget):
        fdoc = fget.__doc__ jeżeli self.overwrite_doc inaczej Nic
        result = type(self)(fget, self.fset, self.fdel, fdoc albo self.__doc__)
        result.overwrite_doc = self.overwrite_doc
        zwróć result

    def setter(self, fset):
        result = type(self)(self.fget, fset, self.fdel, self.__doc__)
        result.overwrite_doc = self.overwrite_doc
        zwróć result

    def deleter(self, fdel):
        result = type(self)(self.fget, self.fset, fdel, self.__doc__)
        result.overwrite_doc = self.overwrite_doc
        zwróć result


zaimportuj functools jako _functools
zaimportuj collections.abc jako _collections_abc

klasa _GeneratorWrapper:
    # TODO: Implement this w C.
    def __init__(self, gen):
        self.__wrapped = gen
        self.__isgen = gen.__class__ jest GeneratorType
        self.__name__ = getattr(gen, '__name__', Nic)
        self.__qualname__ = getattr(gen, '__qualname__', Nic)
    def send(self, val):
        zwróć self.__wrapped.send(val)
    def throw(self, tp, *rest):
        zwróć self.__wrapped.throw(tp, *rest)
    def close(self):
        zwróć self.__wrapped.close()
    @property
    def gi_code(self):
        zwróć self.__wrapped.gi_code
    @property
    def gi_frame(self):
        zwróć self.__wrapped.gi_frame
    @property
    def gi_running(self):
        zwróć self.__wrapped.gi_running
    @property
    def gi_uzyskajfrom(self):
        zwróć self.__wrapped.gi_uzyskajfrom
    cr_code = gi_code
    cr_frame = gi_frame
    cr_running = gi_running
    cr_await = gi_uzyskajfrom
    def __next__(self):
        zwróć next(self.__wrapped)
    def __iter__(self):
        jeżeli self.__isgen:
            zwróć self.__wrapped
        zwróć self
    __await__ = __iter__

def coroutine(func):
    """Convert regular generator function to a coroutine."""

    jeżeli nie callable(func):
        podnieś TypeError('types.coroutine() expects a callable')

    jeżeli (func.__class__ jest FunctionType oraz
        getattr(func, '__code__', Nic).__class__ jest CodeType):

        co_flags = func.__code__.co_flags

        # Check jeżeli 'func' jest a coroutine function.
        # (0x180 == CO_COROUTINE | CO_ITERABLE_COROUTINE)
        jeżeli co_flags & 0x180:
            zwróć func

        # Check jeżeli 'func' jest a generator function.
        # (0x20 == CO_GENERATOR)
        jeżeli co_flags & 0x20:
            # TODO: Implement this w C.
            co = func.__code__
            func.__code__ = CodeType(
                co.co_argcount, co.co_kwonlyargcount, co.co_nlocals,
                co.co_stacksize,
                co.co_flags | 0x100,  # 0x100 == CO_ITERABLE_COROUTINE
                co.co_code,
                co.co_consts, co.co_names, co.co_varnames, co.co_filename,
                co.co_name, co.co_firstlineno, co.co_lnotab, co.co_freevars,
                co.co_cellvars)
            zwróć func

    # The following code jest primarily to support functions that
    # zwróć generator-like objects (dla instance generators
    # compiled przy Cython).

    @_functools.wraps(func)
    def wrapped(*args, **kwargs):
        coro = func(*args, **kwargs)
        jeżeli (coro.__class__ jest CoroutineType albo
            coro.__class__ jest GeneratorType oraz coro.gi_code.co_flags & 0x100):
            # 'coro' jest a native coroutine object albo an iterable coroutine
            zwróć coro
        jeżeli (isinstance(coro, _collections_abc.Generator) oraz
            nie isinstance(coro, _collections_abc.Coroutine)):
            # 'coro' jest either a pure Python generator iterator, albo it
            # implements collections.abc.Generator (and does nie implement
            # collections.abc.Coroutine).
            zwróć _GeneratorWrapper(coro)
        # 'coro' jest either an instance of collections.abc.Coroutine albo
        # some other object -- dalej it through.
        zwróć coro

    zwróć wrapped


__all__ = [n dla n w globals() jeżeli n[:1] != '_']
