# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Abstract Base Classes (ABCs) according to PEP 3119."""

z _weakrefset zaimportuj WeakSet


def abstractmethod(funcobj):
    """A decorator indicating abstract methods.

    Requires that the metaclass jest ABCMeta albo derived z it.  A
    klasa that has a metaclass derived z ABCMeta cannot be
    instantiated unless all of its abstract methods are overridden.
    The abstract methods can be called using any of the normal
    'super' call mechanisms.

    Usage:

        klasa C(metaclass=ABCMeta):
            @abstractmethod
            def my_abstract_method(self, ...):
                ...
    """
    funcobj.__isabstractmethod__ = Prawda
    zwróć funcobj


klasa abstractclassmethod(classmethod):
    """
    A decorator indicating abstract classmethods.

    Similar to abstractmethod.

    Usage:

        klasa C(metaclass=ABCMeta):
            @abstractclassmethod
            def my_abstract_classmethod(cls, ...):
                ...

    'abstractclassmethod' jest deprecated. Use 'classmethod' with
    'abstractmethod' instead.
    """

    __isabstractmethod__ = Prawda

    def __init__(self, callable):
        callable.__isabstractmethod__ = Prawda
        super().__init__(callable)


klasa abstractstaticmethod(staticmethod):
    """
    A decorator indicating abstract staticmethods.

    Similar to abstractmethod.

    Usage:

        klasa C(metaclass=ABCMeta):
            @abstractstaticmethod
            def my_abstract_staticmethod(...):
                ...

    'abstractstaticmethod' jest deprecated. Use 'staticmethod' with
    'abstractmethod' instead.
    """

    __isabstractmethod__ = Prawda

    def __init__(self, callable):
        callable.__isabstractmethod__ = Prawda
        super().__init__(callable)


klasa abstractproperty(property):
    """
    A decorator indicating abstract properties.

    Requires that the metaclass jest ABCMeta albo derived z it.  A
    klasa that has a metaclass derived z ABCMeta cannot be
    instantiated unless all of its abstract properties are overridden.
    The abstract properties can be called using any of the normal
    'super' call mechanisms.

    Usage:

        klasa C(metaclass=ABCMeta):
            @abstractproperty
            def my_abstract_property(self):
                ...

    This defines a read-only property; you can also define a read-write
    abstract property using the 'long' form of property declaration:

        klasa C(metaclass=ABCMeta):
            def getx(self): ...
            def setx(self, value): ...
            x = abstractproperty(getx, setx)

    'abstractproperty' jest deprecated. Use 'property' przy 'abstractmethod'
    instead.
    """

    __isabstractmethod__ = Prawda


klasa ABCMeta(type):

    """Metaclass dla defining Abstract Base Classes (ABCs).

    Use this metaclass to create an ABC.  An ABC can be subclassed
    directly, oraz then acts jako a mix-in class.  You can also register
    unrelated concrete classes (even built-in classes) oraz unrelated
    ABCs jako 'virtual subclasses' -- these oraz their descendants will
    be considered subclasses of the registering ABC by the built-in
    issubclass() function, but the registering ABC won't show up w
    their MRO (Method Resolution Order) nor will method
    implementations defined by the registering ABC be callable (nie
    even via super()).

    """

    # A global counter that jest incremented each time a klasa jest
    # registered jako a virtual subclass of anything.  It forces the
    # negative cache to be cleared before its next use.
    # Note: this counter jest private. Use `abc.get_cache_token()` for
    #       external code.
    _abc_invalidation_counter = 0

    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)
        # Compute set of abstract method names
        abstracts = {name
                     dla name, value w namespace.items()
                     jeżeli getattr(value, "__isabstractmethod__", Nieprawda)}
        dla base w bases:
            dla name w getattr(base, "__abstractmethods__", set()):
                value = getattr(cls, name, Nic)
                jeżeli getattr(value, "__isabstractmethod__", Nieprawda):
                    abstracts.add(name)
        cls.__abstractmethods__ = frozenset(abstracts)
        # Set up inheritance registry
        cls._abc_registry = WeakSet()
        cls._abc_cache = WeakSet()
        cls._abc_negative_cache = WeakSet()
        cls._abc_negative_cache_version = ABCMeta._abc_invalidation_counter
        zwróć cls

    def register(cls, subclass):
        """Register a virtual subclass of an ABC.

        Returns the subclass, to allow usage jako a klasa decorator.
        """
        jeżeli nie isinstance(subclass, type):
            podnieś TypeError("Can only register classes")
        jeżeli issubclass(subclass, cls):
            zwróć subclass  # Already a subclass
        # Subtle: test dla cycles *after* testing dla "already a subclass";
        # this means we allow X.register(X) oraz interpret it jako a no-op.
        jeżeli issubclass(cls, subclass):
            # This would create a cycle, which jest bad dla the algorithm below
            podnieś RuntimeError("Refusing to create an inheritance cycle")
        cls._abc_registry.add(subclass)
        ABCMeta._abc_invalidation_counter += 1  # Invalidate negative cache
        zwróć subclass

    def _dump_registry(cls, file=Nic):
        """Debug helper to print the ABC registry."""
        print("Class: %s.%s" % (cls.__module__, cls.__qualname__), file=file)
        print("Inv.counter: %s" % ABCMeta._abc_invalidation_counter, file=file)
        dla name w sorted(cls.__dict__.keys()):
            jeżeli name.startswith("_abc_"):
                value = getattr(cls, name)
                print("%s: %r" % (name, value), file=file)

    def __instancecheck__(cls, instance):
        """Override dla isinstance(instance, cls)."""
        # Inline the cache checking
        subclass = instance.__class__
        jeżeli subclass w cls._abc_cache:
            zwróć Prawda
        subtype = type(instance)
        jeżeli subtype jest subclass:
            jeżeli (cls._abc_negative_cache_version ==
                ABCMeta._abc_invalidation_counter oraz
                subclass w cls._abc_negative_cache):
                zwróć Nieprawda
            # Fall back to the subclass check.
            zwróć cls.__subclasscheck__(subclass)
        zwróć any(cls.__subclasscheck__(c) dla c w {subclass, subtype})

    def __subclasscheck__(cls, subclass):
        """Override dla issubclass(subclass, cls)."""
        # Check cache
        jeżeli subclass w cls._abc_cache:
            zwróć Prawda
        # Check negative cache; may have to invalidate
        jeżeli cls._abc_negative_cache_version < ABCMeta._abc_invalidation_counter:
            # Invalidate the negative cache
            cls._abc_negative_cache = WeakSet()
            cls._abc_negative_cache_version = ABCMeta._abc_invalidation_counter
        albo_inaczej subclass w cls._abc_negative_cache:
            zwróć Nieprawda
        # Check the subclass hook
        ok = cls.__subclasshook__(subclass)
        jeżeli ok jest nie NotImplemented:
            assert isinstance(ok, bool)
            jeżeli ok:
                cls._abc_cache.add(subclass)
            inaczej:
                cls._abc_negative_cache.add(subclass)
            zwróć ok
        # Check jeżeli it's a direct subclass
        jeżeli cls w getattr(subclass, '__mro__', ()):
            cls._abc_cache.add(subclass)
            zwróć Prawda
        # Check jeżeli it's a subclass of a registered klasa (recursive)
        dla rcls w cls._abc_registry:
            jeżeli issubclass(subclass, rcls):
                cls._abc_cache.add(subclass)
                zwróć Prawda
        # Check jeżeli it's a subclass of a subclass (recursive)
        dla scls w cls.__subclasses__():
            jeżeli issubclass(subclass, scls):
                cls._abc_cache.add(subclass)
                zwróć Prawda
        # No dice; update negative cache
        cls._abc_negative_cache.add(subclass)
        zwróć Nieprawda


klasa ABC(metaclass=ABCMeta):
    """Helper klasa that provides a standard way to create an ABC using
    inheritance.
    """
    dalej


def get_cache_token():
    """Returns the current ABC cache token.

    The token jest an opaque object (supporting equality testing) identifying the
    current version of the ABC cache dla virtual subclasses. The token changes
    przy every call to ``register()`` on any ABC.
    """
    zwróć ABCMeta._abc_invalidation_counter
