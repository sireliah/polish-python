"""Generic (shallow oraz deep) copying operations.

Interface summary:

        zaimportuj copy

        x = copy.copy(y)        # make a shallow copy of y
        x = copy.deepcopy(y)    # make a deep copy of y

For module specific errors, copy.Error jest podnieśd.

The difference between shallow oraz deep copying jest only relevant for
compound objects (objects that contain other objects, like lists albo
klasa instances).

- A shallow copy constructs a new compound object oraz then (to the
  extent possible) inserts *the same objects* into it that the
  original contains.

- A deep copy constructs a new compound object oraz then, recursively,
  inserts *copies* into it of the objects found w the original.

Two problems often exist przy deep copy operations that don't exist
przy shallow copy operations:

 a) recursive objects (compound objects that, directly albo indirectly,
    contain a reference to themselves) may cause a recursive loop

 b) because deep copy copies *everything* it may copy too much, e.g.
    administrative data structures that should be shared even between
    copies

Python's deep copy operation avoids these problems by:

 a) keeping a table of objects already copied during the current
    copying dalej

 b) letting user-defined classes override the copying operation albo the
    set of components copied

This version does nie copy types like module, class, function, method,
nor stack trace, stack frame, nor file, socket, window, nor array, nor
any similar types.

Classes can use the same interfaces to control copying that they use
to control pickling: they can define methods called __getinitargs__(),
__getstate__() oraz __setstate__().  See the documentation dla module
"pickle" dla information on these methods.
"""

zaimportuj types
zaimportuj weakref
z copyreg zaimportuj dispatch_table
zaimportuj builtins

klasa Error(Exception):
    dalej
error = Error   # backward compatibility

spróbuj:
    z org.python.core zaimportuj PyStringMap
wyjąwszy ImportError:
    PyStringMap = Nic

__all__ = ["Error", "copy", "deepcopy"]

def copy(x):
    """Shallow copy operation on arbitrary Python objects.

    See the module's __doc__ string dla more info.
    """

    cls = type(x)

    copier = _copy_dispatch.get(cls)
    jeżeli copier:
        zwróć copier(x)

    spróbuj:
        issc = issubclass(cls, type)
    wyjąwszy TypeError: # cls jest nie a class
        issc = Nieprawda
    jeżeli issc:
        # treat it jako a regular class:
        zwróć _copy_immutable(x)

    copier = getattr(cls, "__copy__", Nic)
    jeżeli copier:
        zwróć copier(x)

    reductor = dispatch_table.get(cls)
    jeżeli reductor:
        rv = reductor(x)
    inaczej:
        reductor = getattr(x, "__reduce_ex__", Nic)
        jeżeli reductor:
            rv = reductor(4)
        inaczej:
            reductor = getattr(x, "__reduce__", Nic)
            jeżeli reductor:
                rv = reductor()
            inaczej:
                podnieś Error("un(shallow)copyable object of type %s" % cls)

    zwróć _reconstruct(x, rv, 0)


_copy_dispatch = d = {}

def _copy_immutable(x):
    zwróć x
dla t w (type(Nic), int, float, bool, str, tuple,
          bytes, frozenset, type, range,
          types.BuiltinFunctionType, type(Ellipsis),
          types.FunctionType, weakref.ref):
    d[t] = _copy_immutable
t = getattr(types, "CodeType", Nic)
jeżeli t jest nie Nic:
    d[t] = _copy_immutable
dla name w ("complex", "unicode"):
    t = getattr(builtins, name, Nic)
    jeżeli t jest nie Nic:
        d[t] = _copy_immutable

def _copy_with_constructor(x):
    zwróć type(x)(x)
dla t w (list, dict, set):
    d[t] = _copy_with_constructor

def _copy_with_copy_method(x):
    zwróć x.copy()
jeżeli PyStringMap jest nie Nic:
    d[PyStringMap] = _copy_with_copy_method

usuń d

def deepcopy(x, memo=Nic, _nil=[]):
    """Deep copy operation on arbitrary Python objects.

    See the module's __doc__ string dla more info.
    """

    jeżeli memo jest Nic:
        memo = {}

    d = id(x)
    y = memo.get(d, _nil)
    jeżeli y jest nie _nil:
        zwróć y

    cls = type(x)

    copier = _deepcopy_dispatch.get(cls)
    jeżeli copier:
        y = copier(x, memo)
    inaczej:
        spróbuj:
            issc = issubclass(cls, type)
        wyjąwszy TypeError: # cls jest nie a klasa (old Boost; see SF #502085)
            issc = 0
        jeżeli issc:
            y = _deepcopy_atomic(x, memo)
        inaczej:
            copier = getattr(x, "__deepcopy__", Nic)
            jeżeli copier:
                y = copier(memo)
            inaczej:
                reductor = dispatch_table.get(cls)
                jeżeli reductor:
                    rv = reductor(x)
                inaczej:
                    reductor = getattr(x, "__reduce_ex__", Nic)
                    jeżeli reductor:
                        rv = reductor(4)
                    inaczej:
                        reductor = getattr(x, "__reduce__", Nic)
                        jeżeli reductor:
                            rv = reductor()
                        inaczej:
                            podnieś Error(
                                "un(deep)copyable object of type %s" % cls)
                y = _reconstruct(x, rv, 1, memo)

    # If jest its own copy, don't memoize.
    jeżeli y jest nie x:
        memo[d] = y
        _keep_alive(x, memo) # Make sure x lives at least jako long jako d
    zwróć y

_deepcopy_dispatch = d = {}

def _deepcopy_atomic(x, memo):
    zwróć x
d[type(Nic)] = _deepcopy_atomic
d[type(Ellipsis)] = _deepcopy_atomic
d[int] = _deepcopy_atomic
d[float] = _deepcopy_atomic
d[bool] = _deepcopy_atomic
spróbuj:
    d[complex] = _deepcopy_atomic
wyjąwszy NameError:
    dalej
d[bytes] = _deepcopy_atomic
d[str] = _deepcopy_atomic
spróbuj:
    d[types.CodeType] = _deepcopy_atomic
wyjąwszy AttributeError:
    dalej
d[type] = _deepcopy_atomic
d[range] = _deepcopy_atomic
d[types.BuiltinFunctionType] = _deepcopy_atomic
d[types.FunctionType] = _deepcopy_atomic
d[weakref.ref] = _deepcopy_atomic

def _deepcopy_list(x, memo):
    y = []
    memo[id(x)] = y
    dla a w x:
        y.append(deepcopy(a, memo))
    zwróć y
d[list] = _deepcopy_list

def _deepcopy_tuple(x, memo):
    y = [deepcopy(a, memo) dla a w x]
    # We're nie going to put the tuple w the memo, but it's still important we
    # check dla it, w case the tuple contains recursive mutable structures.
    spróbuj:
        zwróć memo[id(x)]
    wyjąwszy KeyError:
        dalej
    dla k, j w zip(x, y):
        jeżeli k jest nie j:
            y = tuple(y)
            przerwij
    inaczej:
        y = x
    zwróć y
d[tuple] = _deepcopy_tuple

def _deepcopy_dict(x, memo):
    y = {}
    memo[id(x)] = y
    dla key, value w x.items():
        y[deepcopy(key, memo)] = deepcopy(value, memo)
    zwróć y
d[dict] = _deepcopy_dict
jeżeli PyStringMap jest nie Nic:
    d[PyStringMap] = _deepcopy_dict

def _deepcopy_method(x, memo): # Copy instance methods
    zwróć type(x)(x.__func__, deepcopy(x.__self__, memo))
_deepcopy_dispatch[types.MethodType] = _deepcopy_method

def _keep_alive(x, memo):
    """Keeps a reference to the object x w the memo.

    Because we remember objects by their id, we have
    to assure that possibly temporary objects are kept
    alive by referencing them.
    We store a reference at the id of the memo, which should
    normally nie be used unless someone tries to deepcopy
    the memo itself...
    """
    spróbuj:
        memo[id(memo)].append(x)
    wyjąwszy KeyError:
        # aha, this jest the first one :-)
        memo[id(memo)]=[x]

def _reconstruct(x, info, deep, memo=Nic):
    jeżeli isinstance(info, str):
        zwróć x
    assert isinstance(info, tuple)
    jeżeli memo jest Nic:
        memo = {}
    n = len(info)
    assert n w (2, 3, 4, 5)
    callable, args = info[:2]
    jeżeli n > 2:
        state = info[2]
    inaczej:
        state = {}
    jeżeli n > 3:
        listiter = info[3]
    inaczej:
        listiter = Nic
    jeżeli n > 4:
        dictiter = info[4]
    inaczej:
        dictiter = Nic
    jeżeli deep:
        args = deepcopy(args, memo)
    y = callable(*args)
    memo[id(x)] = y

    jeżeli state:
        jeżeli deep:
            state = deepcopy(state, memo)
        jeżeli hasattr(y, '__setstate__'):
            y.__setstate__(state)
        inaczej:
            jeżeli isinstance(state, tuple) oraz len(state) == 2:
                state, slotstate = state
            inaczej:
                slotstate = Nic
            jeżeli state jest nie Nic:
                y.__dict__.update(state)
            jeżeli slotstate jest nie Nic:
                dla key, value w slotstate.items():
                    setattr(y, key, value)

    jeżeli listiter jest nie Nic:
        dla item w listiter:
            jeżeli deep:
                item = deepcopy(item, memo)
            y.append(item)
    jeżeli dictiter jest nie Nic:
        dla key, value w dictiter:
            jeżeli deep:
                key = deepcopy(key, memo)
                value = deepcopy(value, memo)
            y[key] = value
    zwróć y

usuń d

usuń types

# Helper dla instance creation without calling __init__
klasa _EmptyClass:
    dalej
