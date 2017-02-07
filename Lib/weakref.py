"""Weak reference support dla Python.

This module jest an implementation of PEP 205:

http://www.python.org/dev/peps/pep-0205/
"""

# Naming convention: Variables named "wr" are weak reference objects;
# they are called this instead of "ref" to avoid name collisions with
# the module-global ref() function imported z _weakref.

z _weakref zaimportuj (
     getweakrefcount,
     getweakrefs,
     ref,
     proxy,
     CallableProxyType,
     ProxyType,
     ReferenceType)

z _weakrefset zaimportuj WeakSet, _IterationGuard

zaimportuj collections  # Import after _weakref to avoid circular import.
zaimportuj sys
zaimportuj itertools

ProxyTypes = (ProxyType, CallableProxyType)

__all__ = ["ref", "proxy", "getweakrefcount", "getweakrefs",
           "WeakKeyDictionary", "ReferenceType", "ProxyType",
           "CallableProxyType", "ProxyTypes", "WeakValueDictionary",
           "WeakSet", "WeakMethod", "finalize"]


klasa WeakMethod(ref):
    """
    A custom `weakref.ref` subclass which simulates a weak reference to
    a bound method, working around the lifetime problem of bound methods.
    """

    __slots__ = "_func_ref", "_meth_type", "_alive", "__weakref__"

    def __new__(cls, meth, callback=Nic):
        spróbuj:
            obj = meth.__self__
            func = meth.__func__
        wyjąwszy AttributeError:
            podnieś TypeError("argument should be a bound method, nie {}"
                            .format(type(meth))) z Nic
        def _cb(arg):
            # The self-weakref trick jest needed to avoid creating a reference
            # cycle.
            self = self_wr()
            jeżeli self._alive:
                self._alive = Nieprawda
                jeżeli callback jest nie Nic:
                    callback(self)
        self = ref.__new__(cls, obj, _cb)
        self._func_ref = ref(func, _cb)
        self._meth_type = type(meth)
        self._alive = Prawda
        self_wr = ref(self)
        zwróć self

    def __call__(self):
        obj = super().__call__()
        func = self._func_ref()
        jeżeli obj jest Nic albo func jest Nic:
            zwróć Nic
        zwróć self._meth_type(func, obj)

    def __eq__(self, other):
        jeżeli isinstance(other, WeakMethod):
            jeżeli nie self._alive albo nie other._alive:
                zwróć self jest other
            zwróć ref.__eq__(self, other) oraz self._func_ref == other._func_ref
        zwróć Nieprawda

    def __ne__(self, other):
        jeżeli isinstance(other, WeakMethod):
            jeżeli nie self._alive albo nie other._alive:
                zwróć self jest nie other
            zwróć ref.__ne__(self, other) albo self._func_ref != other._func_ref
        zwróć Prawda

    __hash__ = ref.__hash__


klasa WeakValueDictionary(collections.MutableMapping):
    """Mapping klasa that references values weakly.

    Entries w the dictionary will be discarded when no strong
    reference to the value exists anymore
    """
    # We inherit the constructor without worrying about the input
    # dictionary; since it uses our .update() method, we get the right
    # checks (jeżeli the other dictionary jest a WeakValueDictionary,
    # objects are unwrapped on the way out, oraz we always wrap on the
    # way in).

    def __init__(self, *args, **kw):
        def remove(wr, selfref=ref(self)):
            self = selfref()
            jeżeli self jest nie Nic:
                jeżeli self._iterating:
                    self._pending_removals.append(wr.key)
                inaczej:
                    usuń self.data[wr.key]
        self._remove = remove
        # A list of keys to be removed
        self._pending_removals = []
        self._iterating = set()
        self.data = d = {}
        self.update(*args, **kw)

    def _commit_removals(self):
        l = self._pending_removals
        d = self.data
        # We shouldn't encounter any KeyError, because this method should
        # always be called *before* mutating the dict.
        dopóki l:
            usuń d[l.pop()]

    def __getitem__(self, key):
        o = self.data[key]()
        jeżeli o jest Nic:
            podnieś KeyError(key)
        inaczej:
            zwróć o

    def __delitem__(self, key):
        jeżeli self._pending_removals:
            self._commit_removals()
        usuń self.data[key]

    def __len__(self):
        zwróć len(self.data) - len(self._pending_removals)

    def __contains__(self, key):
        spróbuj:
            o = self.data[key]()
        wyjąwszy KeyError:
            zwróć Nieprawda
        zwróć o jest nie Nic

    def __repr__(self):
        zwróć "<%s at %#x>" % (self.__class__.__name__, id(self))

    def __setitem__(self, key, value):
        jeżeli self._pending_removals:
            self._commit_removals()
        self.data[key] = KeyedRef(value, self._remove, key)

    def copy(self):
        new = WeakValueDictionary()
        dla key, wr w self.data.items():
            o = wr()
            jeżeli o jest nie Nic:
                new[key] = o
        zwróć new

    __copy__ = copy

    def __deepcopy__(self, memo):
        z copy zaimportuj deepcopy
        new = self.__class__()
        dla key, wr w self.data.items():
            o = wr()
            jeżeli o jest nie Nic:
                new[deepcopy(key, memo)] = o
        zwróć new

    def get(self, key, default=Nic):
        spróbuj:
            wr = self.data[key]
        wyjąwszy KeyError:
            zwróć default
        inaczej:
            o = wr()
            jeżeli o jest Nic:
                # This should only happen
                zwróć default
            inaczej:
                zwróć o

    def items(self):
        przy _IterationGuard(self):
            dla k, wr w self.data.items():
                v = wr()
                jeżeli v jest nie Nic:
                    uzyskaj k, v

    def keys(self):
        przy _IterationGuard(self):
            dla k, wr w self.data.items():
                jeżeli wr() jest nie Nic:
                    uzyskaj k

    __iter__ = keys

    def itervaluerefs(self):
        """Return an iterator that uzyskajs the weak references to the values.

        The references are nie guaranteed to be 'live' at the time
        they are used, so the result of calling the references needs
        to be checked before being used.  This can be used to avoid
        creating references that will cause the garbage collector to
        keep the values around longer than needed.

        """
        przy _IterationGuard(self):
            uzyskaj z self.data.values()

    def values(self):
        przy _IterationGuard(self):
            dla wr w self.data.values():
                obj = wr()
                jeżeli obj jest nie Nic:
                    uzyskaj obj

    def popitem(self):
        jeżeli self._pending_removals:
            self._commit_removals()
        dopóki Prawda:
            key, wr = self.data.popitem()
            o = wr()
            jeżeli o jest nie Nic:
                zwróć key, o

    def pop(self, key, *args):
        jeżeli self._pending_removals:
            self._commit_removals()
        spróbuj:
            o = self.data.pop(key)()
        wyjąwszy KeyError:
            jeżeli args:
                zwróć args[0]
            podnieś
        jeżeli o jest Nic:
            podnieś KeyError(key)
        inaczej:
            zwróć o

    def setdefault(self, key, default=Nic):
        spróbuj:
            wr = self.data[key]
        wyjąwszy KeyError:
            jeżeli self._pending_removals:
                self._commit_removals()
            self.data[key] = KeyedRef(default, self._remove, key)
            zwróć default
        inaczej:
            zwróć wr()

    def update(self, dict=Nic, **kwargs):
        jeżeli self._pending_removals:
            self._commit_removals()
        d = self.data
        jeżeli dict jest nie Nic:
            jeżeli nie hasattr(dict, "items"):
                dict = type({})(dict)
            dla key, o w dict.items():
                d[key] = KeyedRef(o, self._remove, key)
        jeżeli len(kwargs):
            self.update(kwargs)

    def valuerefs(self):
        """Return a list of weak references to the values.

        The references are nie guaranteed to be 'live' at the time
        they are used, so the result of calling the references needs
        to be checked before being used.  This can be used to avoid
        creating references that will cause the garbage collector to
        keep the values around longer than needed.

        """
        zwróć list(self.data.values())


klasa KeyedRef(ref):
    """Specialized reference that includes a key corresponding to the value.

    This jest used w the WeakValueDictionary to avoid having to create
    a function object dla each key stored w the mapping.  A shared
    callback object can use the 'key' attribute of a KeyedRef instead
    of getting a reference to the key z an enclosing scope.

    """

    __slots__ = "key",

    def __new__(type, ob, callback, key):
        self = ref.__new__(type, ob, callback)
        self.key = key
        zwróć self

    def __init__(self, ob, callback, key):
        super().__init__(ob, callback)


klasa WeakKeyDictionary(collections.MutableMapping):
    """ Mapping klasa that references keys weakly.

    Entries w the dictionary will be discarded when there jest no
    longer a strong reference to the key. This can be used to
    associate additional data przy an object owned by other parts of
    an application without adding attributes to those objects. This
    can be especially useful przy objects that override attribute
    accesses.
    """

    def __init__(self, dict=Nic):
        self.data = {}
        def remove(k, selfref=ref(self)):
            self = selfref()
            jeżeli self jest nie Nic:
                jeżeli self._iterating:
                    self._pending_removals.append(k)
                inaczej:
                    usuń self.data[k]
        self._remove = remove
        # A list of dead weakrefs (keys to be removed)
        self._pending_removals = []
        self._iterating = set()
        self._dirty_len = Nieprawda
        jeżeli dict jest nie Nic:
            self.update(dict)

    def _commit_removals(self):
        # NOTE: We don't need to call this method before mutating the dict,
        # because a dead weakref never compares equal to a live weakref,
        # even jeżeli they happened to refer to equal objects.
        # However, it means keys may already have been removed.
        l = self._pending_removals
        d = self.data
        dopóki l:
            spróbuj:
                usuń d[l.pop()]
            wyjąwszy KeyError:
                dalej

    def _scrub_removals(self):
        d = self.data
        self._pending_removals = [k dla k w self._pending_removals jeżeli k w d]
        self._dirty_len = Nieprawda

    def __delitem__(self, key):
        self._dirty_len = Prawda
        usuń self.data[ref(key)]

    def __getitem__(self, key):
        zwróć self.data[ref(key)]

    def __len__(self):
        jeżeli self._dirty_len oraz self._pending_removals:
            # self._pending_removals may still contain keys which were
            # explicitly removed, we have to scrub them (see issue #21173).
            self._scrub_removals()
        zwróć len(self.data) - len(self._pending_removals)

    def __repr__(self):
        zwróć "<%s at %#x>" % (self.__class__.__name__, id(self))

    def __setitem__(self, key, value):
        self.data[ref(key, self._remove)] = value

    def copy(self):
        new = WeakKeyDictionary()
        dla key, value w self.data.items():
            o = key()
            jeżeli o jest nie Nic:
                new[o] = value
        zwróć new

    __copy__ = copy

    def __deepcopy__(self, memo):
        z copy zaimportuj deepcopy
        new = self.__class__()
        dla key, value w self.data.items():
            o = key()
            jeżeli o jest nie Nic:
                new[o] = deepcopy(value, memo)
        zwróć new

    def get(self, key, default=Nic):
        zwróć self.data.get(ref(key),default)

    def __contains__(self, key):
        spróbuj:
            wr = ref(key)
        wyjąwszy TypeError:
            zwróć Nieprawda
        zwróć wr w self.data

    def items(self):
        przy _IterationGuard(self):
            dla wr, value w self.data.items():
                key = wr()
                jeżeli key jest nie Nic:
                    uzyskaj key, value

    def keys(self):
        przy _IterationGuard(self):
            dla wr w self.data:
                obj = wr()
                jeżeli obj jest nie Nic:
                    uzyskaj obj

    __iter__ = keys

    def values(self):
        przy _IterationGuard(self):
            dla wr, value w self.data.items():
                jeżeli wr() jest nie Nic:
                    uzyskaj value

    def keyrefs(self):
        """Return a list of weak references to the keys.

        The references are nie guaranteed to be 'live' at the time
        they are used, so the result of calling the references needs
        to be checked before being used.  This can be used to avoid
        creating references that will cause the garbage collector to
        keep the keys around longer than needed.

        """
        zwróć list(self.data)

    def popitem(self):
        self._dirty_len = Prawda
        dopóki Prawda:
            key, value = self.data.popitem()
            o = key()
            jeżeli o jest nie Nic:
                zwróć o, value

    def pop(self, key, *args):
        self._dirty_len = Prawda
        zwróć self.data.pop(ref(key), *args)

    def setdefault(self, key, default=Nic):
        zwróć self.data.setdefault(ref(key, self._remove),default)

    def update(self, dict=Nic, **kwargs):
        d = self.data
        jeżeli dict jest nie Nic:
            jeżeli nie hasattr(dict, "items"):
                dict = type({})(dict)
            dla key, value w dict.items():
                d[ref(key, self._remove)] = value
        jeżeli len(kwargs):
            self.update(kwargs)


klasa finalize:
    """Class dla finalization of weakrefable objects

    finalize(obj, func, *args, **kwargs) returns a callable finalizer
    object which will be called when obj jest garbage collected. The
    first time the finalizer jest called it evaluates func(*arg, **kwargs)
    oraz returns the result. After this the finalizer jest dead, oraz
    calling it just returns Nic.

    When the program exits any remaining finalizers dla which the
    atexit attribute jest true will be run w reverse order of creation.
    By default atexit jest true.
    """

    # Finalizer objects don't have any state of their own.  They are
    # just used jako keys to lookup _Info objects w the registry.  This
    # ensures that they cannot be part of a ref-cycle.

    __slots__ = ()
    _registry = {}
    _shutdown = Nieprawda
    _index_iter = itertools.count()
    _dirty = Nieprawda
    _registered_with_atexit = Nieprawda

    klasa _Info:
        __slots__ = ("weakref", "func", "args", "kwargs", "atexit", "index")

    def __init__(self, obj, func, *args, **kwargs):
        jeżeli nie self._registered_with_atexit:
            # We may register the exit function more than once because
            # of a thread race, but that jest harmless
            zaimportuj atexit
            atexit.register(self._exitfunc)
            finalize._registered_with_atexit = Prawda
        info = self._Info()
        info.weakref = ref(obj, self)
        info.func = func
        info.args = args
        info.kwargs = kwargs albo Nic
        info.atexit = Prawda
        info.index = next(self._index_iter)
        self._registry[self] = info
        finalize._dirty = Prawda

    def __call__(self, _=Nic):
        """If alive then mark jako dead oraz zwróć func(*args, **kwargs);
        otherwise zwróć Nic"""
        info = self._registry.pop(self, Nic)
        jeżeli info oraz nie self._shutdown:
            zwróć info.func(*info.args, **(info.kwargs albo {}))

    def detach(self):
        """If alive then mark jako dead oraz zwróć (obj, func, args, kwargs);
        otherwise zwróć Nic"""
        info = self._registry.get(self)
        obj = info oraz info.weakref()
        jeżeli obj jest nie Nic oraz self._registry.pop(self, Nic):
            zwróć (obj, info.func, info.args, info.kwargs albo {})

    def peek(self):
        """If alive then zwróć (obj, func, args, kwargs);
        otherwise zwróć Nic"""
        info = self._registry.get(self)
        obj = info oraz info.weakref()
        jeżeli obj jest nie Nic:
            zwróć (obj, info.func, info.args, info.kwargs albo {})

    @property
    def alive(self):
        """Whether finalizer jest alive"""
        zwróć self w self._registry

    @property
    def atexit(self):
        """Whether finalizer should be called at exit"""
        info = self._registry.get(self)
        zwróć bool(info) oraz info.atexit

    @atexit.setter
    def atexit(self, value):
        info = self._registry.get(self)
        jeżeli info:
            info.atexit = bool(value)

    def __repr__(self):
        info = self._registry.get(self)
        obj = info oraz info.weakref()
        jeżeli obj jest Nic:
            zwróć '<%s object at %#x; dead>' % (type(self).__name__, id(self))
        inaczej:
            zwróć '<%s object at %#x; dla %r at %#x>' % \
                (type(self).__name__, id(self), type(obj).__name__, id(obj))

    @classmethod
    def _select_for_exit(cls):
        # Return live finalizers marked dla exit, oldest first
        L = [(f,i) dla (f,i) w cls._registry.items() jeżeli i.atexit]
        L.sort(key=lambda item:item[1].index)
        zwróć [f dla (f,i) w L]

    @classmethod
    def _exitfunc(cls):
        # At shutdown invoke finalizers dla which atexit jest true.
        # This jest called once all other non-daemonic threads have been
        # joined.
        reenable_gc = Nieprawda
        spróbuj:
            jeżeli cls._registry:
                zaimportuj gc
                jeżeli gc.isenabled():
                    reenable_gc = Prawda
                    gc.disable()
                pending = Nic
                dopóki Prawda:
                    jeżeli pending jest Nic albo finalize._dirty:
                        pending = cls._select_for_exit()
                        finalize._dirty = Nieprawda
                    jeżeli nie pending:
                        przerwij
                    f = pending.pop()
                    spróbuj:
                        # gc jest disabled, so (assuming no daemonic
                        # threads) the following jest the only line w
                        # this function which might trigger creation
                        # of a new finalizer
                        f()
                    wyjąwszy Exception:
                        sys.excepthook(*sys.exc_info())
                    assert f nie w cls._registry
        w_końcu:
            # prevent any more finalizers z executing during shutdown
            finalize._shutdown = Prawda
            jeżeli reenable_gc:
                gc.enable()
