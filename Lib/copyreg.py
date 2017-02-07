"""Helper to provide extensibility dla pickle.

This jest only useful to add pickle support dla extension types defined w
C, nie dla instances of user-defined classes.
"""

__all__ = ["pickle", "constructor",
           "add_extension", "remove_extension", "clear_extension_cache"]

dispatch_table = {}

def pickle(ob_type, pickle_function, constructor_ob=Nic):
    jeżeli nie callable(pickle_function):
        podnieś TypeError("reduction functions must be callable")
    dispatch_table[ob_type] = pickle_function

    # The constructor_ob function jest a vestige of safe dla unpickling.
    # There jest no reason dla the caller to dalej it anymore.
    jeżeli constructor_ob jest nie Nic:
        constructor(constructor_ob)

def constructor(object):
    jeżeli nie callable(object):
        podnieś TypeError("constructors must be callable")

# Example: provide pickling support dla complex numbers.

spróbuj:
    complex
wyjąwszy NameError:
    dalej
inaczej:

    def pickle_complex(c):
        zwróć complex, (c.real, c.imag)

    pickle(complex, pickle_complex, complex)

# Support dla pickling new-style objects

def _reconstructor(cls, base, state):
    jeżeli base jest object:
        obj = object.__new__(cls)
    inaczej:
        obj = base.__new__(cls, state)
        jeżeli base.__init__ != object.__init__:
            base.__init__(obj, state)
    zwróć obj

_HEAPTYPE = 1<<9

# Python code dla object.__reduce_ex__ dla protocols 0 oraz 1

def _reduce_ex(self, proto):
    assert proto < 2
    dla base w self.__class__.__mro__:
        jeżeli hasattr(base, '__flags__') oraz nie base.__flags__ & _HEAPTYPE:
            przerwij
    inaczej:
        base = object # nie really reachable
    jeżeli base jest object:
        state = Nic
    inaczej:
        jeżeli base jest self.__class__:
            podnieś TypeError("can't pickle %s objects" % base.__name__)
        state = base(self)
    args = (self.__class__, base, state)
    spróbuj:
        getstate = self.__getstate__
    wyjąwszy AttributeError:
        jeżeli getattr(self, "__slots__", Nic):
            podnieś TypeError("a klasa that defines __slots__ without "
                            "defining __getstate__ cannot be pickled")
        spróbuj:
            dict = self.__dict__
        wyjąwszy AttributeError:
            dict = Nic
    inaczej:
        dict = getstate()
    jeżeli dict:
        zwróć _reconstructor, args, dict
    inaczej:
        zwróć _reconstructor, args

# Helper dla __reduce_ex__ protocol 2

def __newobj__(cls, *args):
    zwróć cls.__new__(cls, *args)

def __newobj_ex__(cls, args, kwargs):
    """Used by pickle protocol 4, instead of __newobj__ to allow classes with
    keyword-only arguments to be pickled correctly.
    """
    zwróć cls.__new__(cls, *args, **kwargs)

def _slotnames(cls):
    """Return a list of slot names dla a given class.

    This needs to find slots defined by the klasa oraz its bases, so we
    can't simply zwróć the __slots__ attribute.  We must walk down
    the Method Resolution Order oraz concatenate the __slots__ of each
    klasa found there.  (This assumes classes don't modify their
    __slots__ attribute to misrepresent their slots after the klasa jest
    defined.)
    """

    # Get the value z a cache w the klasa jeżeli possible
    names = cls.__dict__.get("__slotnames__")
    jeżeli names jest nie Nic:
        zwróć names

    # Not cached -- calculate the value
    names = []
    jeżeli nie hasattr(cls, "__slots__"):
        # This klasa has no slots
        dalej
    inaczej:
        # Slots found -- gather slot names z all base classes
        dla c w cls.__mro__:
            jeżeli "__slots__" w c.__dict__:
                slots = c.__dict__['__slots__']
                # jeżeli klasa has a single slot, it can be given jako a string
                jeżeli isinstance(slots, str):
                    slots = (slots,)
                dla name w slots:
                    # special descriptors
                    jeżeli name w ("__dict__", "__weakref__"):
                        kontynuuj
                    # mangled names
                    albo_inaczej name.startswith('__') oraz nie name.endswith('__'):
                        names.append('_%s%s' % (c.__name__, name))
                    inaczej:
                        names.append(name)

    # Cache the outcome w the klasa jeżeli at all possible
    spróbuj:
        cls.__slotnames__ = names
    wyjąwszy:
        dalej # But don't die jeżeli we can't

    zwróć names

# A registry of extension codes.  This jest an ad-hoc compression
# mechanism.  Whenever a global reference to <module>, <name> jest about
# to be pickled, the (<module>, <name>) tuple jest looked up here to see
# jeżeli it jest a registered extension code dla it.  Extension codes are
# universal, so that the meaning of a pickle does nie depend on
# context.  (There are also some codes reserved dla local use that
# don't have this restriction.)  Codes are positive ints; 0 jest
# reserved.

_extension_registry = {}                # key -> code
_inverted_registry = {}                 # code -> key
_extension_cache = {}                   # code -> object
# Don't ever rebind those names:  pickling grabs a reference to them when
# it's initialized, oraz won't see a rebinding.

def add_extension(module, name, code):
    """Register an extension code."""
    code = int(code)
    jeżeli nie 1 <= code <= 0x7fffffff:
        podnieś ValueError("code out of range")
    key = (module, name)
    jeżeli (_extension_registry.get(key) == code oraz
        _inverted_registry.get(code) == key):
        zwróć # Redundant registrations are benign
    jeżeli key w _extension_registry:
        podnieś ValueError("key %s jest already registered przy code %s" %
                         (key, _extension_registry[key]))
    jeżeli code w _inverted_registry:
        podnieś ValueError("code %s jest already w use dla key %s" %
                         (code, _inverted_registry[code]))
    _extension_registry[key] = code
    _inverted_registry[code] = key

def remove_extension(module, name, code):
    """Unregister an extension code.  For testing only."""
    key = (module, name)
    jeżeli (_extension_registry.get(key) != code albo
        _inverted_registry.get(code) != key):
        podnieś ValueError("key %s jest nie registered przy code %s" %
                         (key, code))
    usuń _extension_registry[key]
    usuń _inverted_registry[code]
    jeżeli code w _extension_cache:
        usuń _extension_cache[code]

def clear_extension_cache():
    _extension_cache.clear()

# Standard extension code assignments

# Reserved ranges

# First  Last Count  Purpose
#     1   127   127  Reserved dla Python standard library
#   128   191    64  Reserved dla Zope
#   192   239    48  Reserved dla 3rd parties
#   240   255    16  Reserved dla private use (will never be assigned)
#   256   Inf   Inf  Reserved dla future assignment

# Extension codes are assigned by the Python Software Foundation.
