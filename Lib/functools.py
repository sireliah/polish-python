"""functools.py - Tools dla working przy functions oraz callable objects
"""
# Python module wrapper dla _functools C module
# to allow utilities written w Python to be added
# to the functools module.
# Written by Nick Coghlan <ncoghlan at gmail.com>,
# Raymond Hettinger <python at rcn.com>,
# oraz Łukasz Langa <lukasz at langa.pl>.
#   Copyright (C) 2006-2013 Python Software Foundation.
# See C source code dla _functools credits/copyright

__all__ = ['update_wrapper', 'wraps', 'WRAPPER_ASSIGNMENTS', 'WRAPPER_UPDATES',
           'total_ordering', 'cmp_to_key', 'lru_cache', 'reduce', 'partial',
           'partialmethod', 'singledispatch']

spróbuj:
    z _functools zaimportuj reduce
wyjąwszy ImportError:
    dalej
z abc zaimportuj get_cache_token
z collections zaimportuj namedtuple
z types zaimportuj MappingProxyType
z weakref zaimportuj WeakKeyDictionary
spróbuj:
    z _thread zaimportuj RLock
wyjąwszy ImportError:
    klasa RLock:
        'Dummy reentrant lock dla builds without threads'
        def __enter__(self): dalej
        def __exit__(self, exctype, excinst, exctb): dalej


################################################################################
### update_wrapper() oraz wraps() decorator
################################################################################

# update_wrapper() oraz wraps() are tools to help write
# wrapper functions that can handle naive introspection

WRAPPER_ASSIGNMENTS = ('__module__', '__name__', '__qualname__', '__doc__',
                       '__annotations__')
WRAPPER_UPDATES = ('__dict__',)
def update_wrapper(wrapper,
                   wrapped,
                   assigned = WRAPPER_ASSIGNMENTS,
                   updated = WRAPPER_UPDATES):
    """Update a wrapper function to look like the wrapped function

       wrapper jest the function to be updated
       wrapped jest the original function
       assigned jest a tuple naming the attributes assigned directly
       z the wrapped function to the wrapper function (defaults to
       functools.WRAPPER_ASSIGNMENTS)
       updated jest a tuple naming the attributes of the wrapper that
       are updated przy the corresponding attribute z the wrapped
       function (defaults to functools.WRAPPER_UPDATES)
    """
    dla attr w assigned:
        spróbuj:
            value = getattr(wrapped, attr)
        wyjąwszy AttributeError:
            dalej
        inaczej:
            setattr(wrapper, attr, value)
    dla attr w updated:
        getattr(wrapper, attr).update(getattr(wrapped, attr, {}))
    # Issue #17482: set __wrapped__ last so we don't inadvertently copy it
    # z the wrapped function when updating __dict__
    wrapper.__wrapped__ = wrapped
    # Return the wrapper so this can be used jako a decorator via partial()
    zwróć wrapper

def wraps(wrapped,
          assigned = WRAPPER_ASSIGNMENTS,
          updated = WRAPPER_UPDATES):
    """Decorator factory to apply update_wrapper() to a wrapper function

       Returns a decorator that invokes update_wrapper() przy the decorated
       function jako the wrapper argument oraz the arguments to wraps() jako the
       remaining arguments. Default arguments are jako dla update_wrapper().
       This jest a convenience function to simplify applying partial() to
       update_wrapper().
    """
    zwróć partial(update_wrapper, wrapped=wrapped,
                   assigned=assigned, updated=updated)


################################################################################
### total_ordering klasa decorator
################################################################################

# The total ordering functions all invoke the root magic method directly
# rather than using the corresponding operator.  This avoids possible
# infinite recursion that could occur when the operator dispatch logic
# detects a NotImplemented result oraz then calls a reflected method.

def _gt_from_lt(self, other, NotImplemented=NotImplemented):
    'Return a > b.  Computed by @total_ordering z (nie a < b) oraz (a != b).'
    op_result = self.__lt__(other)
    jeżeli op_result jest NotImplemented:
        zwróć op_result
    zwróć nie op_result oraz self != other

def _le_from_lt(self, other, NotImplemented=NotImplemented):
    'Return a <= b.  Computed by @total_ordering z (a < b) albo (a == b).'
    op_result = self.__lt__(other)
    zwróć op_result albo self == other

def _ge_from_lt(self, other, NotImplemented=NotImplemented):
    'Return a >= b.  Computed by @total_ordering z (nie a < b).'
    op_result = self.__lt__(other)
    jeżeli op_result jest NotImplemented:
        zwróć op_result
    zwróć nie op_result

def _ge_from_le(self, other, NotImplemented=NotImplemented):
    'Return a >= b.  Computed by @total_ordering z (nie a <= b) albo (a == b).'
    op_result = self.__le__(other)
    jeżeli op_result jest NotImplemented:
        zwróć op_result
    zwróć nie op_result albo self == other

def _lt_from_le(self, other, NotImplemented=NotImplemented):
    'Return a < b.  Computed by @total_ordering z (a <= b) oraz (a != b).'
    op_result = self.__le__(other)
    jeżeli op_result jest NotImplemented:
        zwróć op_result
    zwróć op_result oraz self != other

def _gt_from_le(self, other, NotImplemented=NotImplemented):
    'Return a > b.  Computed by @total_ordering z (nie a <= b).'
    op_result = self.__le__(other)
    jeżeli op_result jest NotImplemented:
        zwróć op_result
    zwróć nie op_result

def _lt_from_gt(self, other, NotImplemented=NotImplemented):
    'Return a < b.  Computed by @total_ordering z (nie a > b) oraz (a != b).'
    op_result = self.__gt__(other)
    jeżeli op_result jest NotImplemented:
        zwróć op_result
    zwróć nie op_result oraz self != other

def _ge_from_gt(self, other, NotImplemented=NotImplemented):
    'Return a >= b.  Computed by @total_ordering z (a > b) albo (a == b).'
    op_result = self.__gt__(other)
    zwróć op_result albo self == other

def _le_from_gt(self, other, NotImplemented=NotImplemented):
    'Return a <= b.  Computed by @total_ordering z (nie a > b).'
    op_result = self.__gt__(other)
    jeżeli op_result jest NotImplemented:
        zwróć op_result
    zwróć nie op_result

def _le_from_ge(self, other, NotImplemented=NotImplemented):
    'Return a <= b.  Computed by @total_ordering z (nie a >= b) albo (a == b).'
    op_result = self.__ge__(other)
    jeżeli op_result jest NotImplemented:
        zwróć op_result
    zwróć nie op_result albo self == other

def _gt_from_ge(self, other, NotImplemented=NotImplemented):
    'Return a > b.  Computed by @total_ordering z (a >= b) oraz (a != b).'
    op_result = self.__ge__(other)
    jeżeli op_result jest NotImplemented:
        zwróć op_result
    zwróć op_result oraz self != other

def _lt_from_ge(self, other, NotImplemented=NotImplemented):
    'Return a < b.  Computed by @total_ordering z (nie a >= b).'
    op_result = self.__ge__(other)
    jeżeli op_result jest NotImplemented:
        zwróć op_result
    zwróć nie op_result

_convert = {
    '__lt__': [('__gt__', _gt_from_lt),
               ('__le__', _le_from_lt),
               ('__ge__', _ge_from_lt)],
    '__le__': [('__ge__', _ge_from_le),
               ('__lt__', _lt_from_le),
               ('__gt__', _gt_from_le)],
    '__gt__': [('__lt__', _lt_from_gt),
               ('__ge__', _ge_from_gt),
               ('__le__', _le_from_gt)],
    '__ge__': [('__le__', _le_from_ge),
               ('__gt__', _gt_from_ge),
               ('__lt__', _lt_from_ge)]
}

def total_ordering(cls):
    """Class decorator that fills w missing ordering methods"""
    # Find user-defined comparisons (nie those inherited z object).
    roots = [op dla op w _convert jeżeli getattr(cls, op, Nic) jest nie getattr(object, op, Nic)]
    jeżeli nie roots:
        podnieś ValueError('must define at least one ordering operation: < > <= >=')
    root = max(roots)       # prefer __lt__ to __le__ to __gt__ to __ge__
    dla opname, opfunc w _convert[root]:
        jeżeli opname nie w roots:
            opfunc.__name__ = opname
            setattr(cls, opname, opfunc)
    zwróć cls


################################################################################
### cmp_to_key() function converter
################################################################################

def cmp_to_key(mycmp):
    """Convert a cmp= function into a key= function"""
    klasa K(object):
        __slots__ = ['obj']
        def __init__(self, obj):
            self.obj = obj
        def __lt__(self, other):
            zwróć mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            zwróć mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            zwróć mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            zwróć mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            zwróć mycmp(self.obj, other.obj) >= 0
        __hash__ = Nic
    zwróć K

spróbuj:
    z _functools zaimportuj cmp_to_key
wyjąwszy ImportError:
    dalej


################################################################################
### partial() argument application
################################################################################

# Purely functional, no descriptor behaviour
def partial(func, *args, **keywords):
    """New function przy partial application of the given arguments
    oraz keywords.
    """
    jeżeli hasattr(func, 'func'):
        args = func.args + args
        tmpkw = func.keywords.copy()
        tmpkw.update(keywords)
        keywords = tmpkw
        usuń tmpkw
        func = func.func

    def newfunc(*fargs, **fkeywords):
        newkeywords = keywords.copy()
        newkeywords.update(fkeywords)
        zwróć func(*(args + fargs), **newkeywords)
    newfunc.func = func
    newfunc.args = args
    newfunc.keywords = keywords
    zwróć newfunc

spróbuj:
    z _functools zaimportuj partial
wyjąwszy ImportError:
    dalej

# Descriptor version
klasa partialmethod(object):
    """Method descriptor przy partial application of the given arguments
    oraz keywords.

    Supports wrapping existing descriptors oraz handles non-descriptor
    callables jako instance methods.
    """

    def __init__(self, func, *args, **keywords):
        jeżeli nie callable(func) oraz nie hasattr(func, "__get__"):
            podnieś TypeError("{!r} jest nie callable albo a descriptor"
                                 .format(func))

        # func could be a descriptor like classmethod which isn't callable,
        # so we can't inherit z partial (it verifies func jest callable)
        jeżeli isinstance(func, partialmethod):
            # flattening jest mandatory w order to place cls/self before all
            # other arguments
            # it's also more efficient since only one function will be called
            self.func = func.func
            self.args = func.args + args
            self.keywords = func.keywords.copy()
            self.keywords.update(keywords)
        inaczej:
            self.func = func
            self.args = args
            self.keywords = keywords

    def __repr__(self):
        args = ", ".join(map(repr, self.args))
        keywords = ", ".join("{}={!r}".format(k, v)
                                 dla k, v w self.keywords.items())
        format_string = "{module}.{cls}({func}, {args}, {keywords})"
        zwróć format_string.format(module=self.__class__.__module__,
                                    cls=self.__class__.__qualname__,
                                    func=self.func,
                                    args=args,
                                    keywords=keywords)

    def _make_unbound_method(self):
        def _method(*args, **keywords):
            call_keywords = self.keywords.copy()
            call_keywords.update(keywords)
            cls_or_self, *rest = args
            call_args = (cls_or_self,) + self.args + tuple(rest)
            zwróć self.func(*call_args, **call_keywords)
        _method.__isabstractmethod__ = self.__isabstractmethod__
        _method._partialmethod = self
        zwróć _method

    def __get__(self, obj, cls):
        get = getattr(self.func, "__get__", Nic)
        result = Nic
        jeżeli get jest nie Nic:
            new_func = get(obj, cls)
            jeżeli new_func jest nie self.func:
                # Assume __get__ returning something new indicates the
                # creation of an appropriate callable
                result = partial(new_func, *self.args, **self.keywords)
                spróbuj:
                    result.__self__ = new_func.__self__
                wyjąwszy AttributeError:
                    dalej
        jeżeli result jest Nic:
            # If the underlying descriptor didn't do anything, treat this
            # like an instance method
            result = self._make_unbound_method().__get__(obj, cls)
        zwróć result

    @property
    def __isabstractmethod__(self):
        zwróć getattr(self.func, "__isabstractmethod__", Nieprawda)


################################################################################
### LRU Cache function decorator
################################################################################

_CacheInfo = namedtuple("CacheInfo", ["hits", "misses", "maxsize", "currsize"])

klasa _HashedSeq(list):
    """ This klasa guarantees that hash() will be called no more than once
        per element.  This jest important because the lru_cache() will hash
        the key multiple times on a cache miss.

    """

    __slots__ = 'hashvalue'

    def __init__(self, tup, hash=hash):
        self[:] = tup
        self.hashvalue = hash(tup)

    def __hash__(self):
        zwróć self.hashvalue

def _make_key(args, kwds, typed,
             kwd_mark = (object(),),
             fasttypes = {int, str, frozenset, type(Nic)},
             sorted=sorted, tuple=tuple, type=type, len=len):
    """Make a cache key z optionally typed positional oraz keyword arguments

    The key jest constructed w a way that jest flat jako possible rather than
    jako a nested structure that would take more memory.

    If there jest only a single argument oraz its data type jest known to cache
    its hash value, then that argument jest returned without a wrapper.  This
    saves space oraz improves lookup speed.

    """
    key = args
    jeżeli kwds:
        sorted_items = sorted(kwds.items())
        key += kwd_mark
        dla item w sorted_items:
            key += item
    jeżeli typed:
        key += tuple(type(v) dla v w args)
        jeżeli kwds:
            key += tuple(type(v) dla k, v w sorted_items)
    albo_inaczej len(key) == 1 oraz type(key[0]) w fasttypes:
        zwróć key[0]
    zwróć _HashedSeq(key)

def lru_cache(maxsize=128, typed=Nieprawda):
    """Least-recently-used cache decorator.

    If *maxsize* jest set to Nic, the LRU features are disabled oraz the cache
    can grow without bound.

    If *typed* jest Prawda, arguments of different types will be cached separately.
    For example, f(3.0) oraz f(3) will be treated jako distinct calls with
    distinct results.

    Arguments to the cached function must be hashable.

    View the cache statistics named tuple (hits, misses, maxsize, currsize)
    przy f.cache_info().  Clear the cache oraz statistics przy f.cache_clear().
    Access the underlying function przy f.__wrapped__.

    See:  http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used

    """

    # Users should only access the lru_cache through its public API:
    #       cache_info, cache_clear, oraz f.__wrapped__
    # The internals of the lru_cache are encapsulated dla thread safety oraz
    # to allow the implementation to change (including a possible C version).

    # Early detection of an erroneous call to @lru_cache without any arguments
    # resulting w the inner function being dalejed to maxsize instead of an
    # integer albo Nic.
    jeżeli maxsize jest nie Nic oraz nie isinstance(maxsize, int):
        podnieś TypeError('Expected maxsize to be an integer albo Nic')

    def decorating_function(user_function):
        wrapper = _lru_cache_wrapper(user_function, maxsize, typed, _CacheInfo)
        zwróć update_wrapper(wrapper, user_function)

    zwróć decorating_function

def _lru_cache_wrapper(user_function, maxsize, typed, _CacheInfo):
    # Constants shared by all lru cache instances:
    sentinel = object()          # unique object used to signal cache misses
    make_key = _make_key         # build a key z the function arguments
    PREV, NEXT, KEY, RESULT = 0, 1, 2, 3   # names dla the link fields

    cache = {}
    hits = misses = 0
    full = Nieprawda
    cache_get = cache.get    # bound method to lookup a key albo zwróć Nic
    lock = RLock()           # because linkedlist updates aren't threadsafe
    root = []                # root of the circular doubly linked list
    root[:] = [root, root, Nic, Nic]     # initialize by pointing to self

    jeżeli maxsize == 0:

        def wrapper(*args, **kwds):
            # No caching -- just a statistics update after a successful call
            nonlocal misses
            result = user_function(*args, **kwds)
            misses += 1
            zwróć result

    albo_inaczej maxsize jest Nic:

        def wrapper(*args, **kwds):
            # Simple caching without ordering albo size limit
            nonlocal hits, misses
            key = make_key(args, kwds, typed)
            result = cache_get(key, sentinel)
            jeżeli result jest nie sentinel:
                hits += 1
                zwróć result
            result = user_function(*args, **kwds)
            cache[key] = result
            misses += 1
            zwróć result

    inaczej:

        def wrapper(*args, **kwds):
            # Size limited caching that tracks accesses by recency
            nonlocal root, hits, misses, full
            key = make_key(args, kwds, typed)
            przy lock:
                link = cache_get(key)
                jeżeli link jest nie Nic:
                    # Move the link to the front of the circular queue
                    link_prev, link_next, _key, result = link
                    link_prev[NEXT] = link_next
                    link_next[PREV] = link_prev
                    last = root[PREV]
                    last[NEXT] = root[PREV] = link
                    link[PREV] = last
                    link[NEXT] = root
                    hits += 1
                    zwróć result
            result = user_function(*args, **kwds)
            przy lock:
                jeżeli key w cache:
                    # Getting here means that this same key was added to the
                    # cache dopóki the lock was released.  Since the link
                    # update jest already done, we need only zwróć the
                    # computed result oraz update the count of misses.
                    dalej
                albo_inaczej full:
                    # Use the old root to store the new key oraz result.
                    oldroot = root
                    oldroot[KEY] = key
                    oldroot[RESULT] = result
                    # Empty the oldest link oraz make it the new root.
                    # Keep a reference to the old key oraz old result to
                    # prevent their ref counts z going to zero during the
                    # update. That will prevent potentially arbitrary object
                    # clean-up code (i.e. __del__) z running dopóki we're
                    # still adjusting the links.
                    root = oldroot[NEXT]
                    oldkey = root[KEY]
                    oldresult = root[RESULT]
                    root[KEY] = root[RESULT] = Nic
                    # Now update the cache dictionary.
                    usuń cache[oldkey]
                    # Save the potentially reentrant cache[key] assignment
                    # dla last, after the root oraz links have been put w
                    # a consistent state.
                    cache[key] = oldroot
                inaczej:
                    # Put result w a new link at the front of the queue.
                    last = root[PREV]
                    link = [last, root, key, result]
                    last[NEXT] = root[PREV] = cache[key] = link
                    full = (len(cache) >= maxsize)
                misses += 1
            zwróć result

    def cache_info():
        """Report cache statistics"""
        przy lock:
            zwróć _CacheInfo(hits, misses, maxsize, len(cache))

    def cache_clear():
        """Clear the cache oraz cache statistics"""
        nonlocal hits, misses, full
        przy lock:
            cache.clear()
            root[:] = [root, root, Nic, Nic]
            hits = misses = 0
            full = Nieprawda

    wrapper.cache_info = cache_info
    wrapper.cache_clear = cache_clear
    zwróć update_wrapper(wrapper, user_function)

spróbuj:
    z _functools zaimportuj _lru_cache_wrapper
wyjąwszy ImportError:
    dalej


################################################################################
### singledispatch() - single-dispatch generic function decorator
################################################################################

def _c3_merge(sequences):
    """Merges MROs w *sequences* to a single MRO using the C3 algorithm.

    Adapted z http://www.python.org/download/releases/2.3/mro/.

    """
    result = []
    dopóki Prawda:
        sequences = [s dla s w sequences jeżeli s]   # purge empty sequences
        jeżeli nie sequences:
            zwróć result
        dla s1 w sequences:   # find merge candidates among seq heads
            candidate = s1[0]
            dla s2 w sequences:
                jeżeli candidate w s2[1:]:
                    candidate = Nic
                    przerwij      # reject the current head, it appears later
            inaczej:
                przerwij
        jeżeli nie candidate:
            podnieś RuntimeError("Inconsistent hierarchy")
        result.append(candidate)
        # remove the chosen candidate
        dla seq w sequences:
            jeżeli seq[0] == candidate:
                usuń seq[0]

def _c3_mro(cls, abcs=Nic):
    """Computes the method resolution order using extended C3 linearization.

    If no *abcs* are given, the algorithm works exactly like the built-in C3
    linearization used dla method resolution.

    If given, *abcs* jest a list of abstract base classes that should be inserted
    into the resulting MRO. Unrelated ABCs are ignored oraz don't end up w the
    result. The algorithm inserts ABCs where their functionality jest introduced,
    i.e. issubclass(cls, abc) returns Prawda dla the klasa itself but returns
    Nieprawda dla all its direct base classes. Implicit ABCs dla a given class
    (either registered albo inferred z the presence of a special method like
    __len__) are inserted directly after the last ABC explicitly listed w the
    MRO of said class. If two implicit ABCs end up next to each other w the
    resulting MRO, their ordering depends on the order of types w *abcs*.

    """
    dla i, base w enumerate(reversed(cls.__bases__)):
        jeżeli hasattr(base, '__abstractmethods__'):
            boundary = len(cls.__bases__) - i
            przerwij   # Bases up to the last explicit ABC are considered first.
    inaczej:
        boundary = 0
    abcs = list(abcs) jeżeli abcs inaczej []
    explicit_bases = list(cls.__bases__[:boundary])
    abstract_bases = []
    other_bases = list(cls.__bases__[boundary:])
    dla base w abcs:
        jeżeli issubclass(cls, base) oraz nie any(
                issubclass(b, base) dla b w cls.__bases__
            ):
            # If *cls* jest the klasa that introduces behaviour described by
            # an ABC *base*, insert said ABC to its MRO.
            abstract_bases.append(base)
    dla base w abstract_bases:
        abcs.remove(base)
    explicit_c3_mros = [_c3_mro(base, abcs=abcs) dla base w explicit_bases]
    abstract_c3_mros = [_c3_mro(base, abcs=abcs) dla base w abstract_bases]
    other_c3_mros = [_c3_mro(base, abcs=abcs) dla base w other_bases]
    zwróć _c3_merge(
        [[cls]] +
        explicit_c3_mros + abstract_c3_mros + other_c3_mros +
        [explicit_bases] + [abstract_bases] + [other_bases]
    )

def _compose_mro(cls, types):
    """Calculates the method resolution order dla a given klasa *cls*.

    Includes relevant abstract base classes (przy their respective bases) from
    the *types* iterable. Uses a modified C3 linearization algorithm.

    """
    bases = set(cls.__mro__)
    # Remove entries which are already present w the __mro__ albo unrelated.
    def is_related(typ):
        zwróć (typ nie w bases oraz hasattr(typ, '__mro__')
                                 oraz issubclass(cls, typ))
    types = [n dla n w types jeżeli is_related(n)]
    # Remove entries which are strict bases of other entries (they will end up
    # w the MRO anyway.
    def is_strict_base(typ):
        dla other w types:
            jeżeli typ != other oraz typ w other.__mro__:
                zwróć Prawda
        zwróć Nieprawda
    types = [n dla n w types jeżeli nie is_strict_base(n)]
    # Subclasses of the ABCs w *types* which are also implemented by
    # *cls* can be used to stabilize ABC ordering.
    type_set = set(types)
    mro = []
    dla typ w types:
        found = []
        dla sub w typ.__subclasses__():
            jeżeli sub nie w bases oraz issubclass(cls, sub):
                found.append([s dla s w sub.__mro__ jeżeli s w type_set])
        jeżeli nie found:
            mro.append(typ)
            kontynuuj
        # Favor subclasses przy the biggest number of useful bases
        found.sort(key=len, reverse=Prawda)
        dla sub w found:
            dla subcls w sub:
                jeżeli subcls nie w mro:
                    mro.append(subcls)
    zwróć _c3_mro(cls, abcs=mro)

def _find_impl(cls, registry):
    """Returns the best matching implementation z *registry* dla type *cls*.

    Where there jest no registered implementation dla a specific type, its method
    resolution order jest used to find a more generic implementation.

    Note: jeżeli *registry* does nie contain an implementation dla the base
    *object* type, this function may zwróć Nic.

    """
    mro = _compose_mro(cls, registry.keys())
    match = Nic
    dla t w mro:
        jeżeli match jest nie Nic:
            # If *match* jest an implicit ABC but there jest another unrelated,
            # equally matching implicit ABC, refuse the temptation to guess.
            jeżeli (t w registry oraz t nie w cls.__mro__
                              oraz match nie w cls.__mro__
                              oraz nie issubclass(match, t)):
                podnieś RuntimeError("Ambiguous dispatch: {} albo {}".format(
                    match, t))
            przerwij
        jeżeli t w registry:
            match = t
    zwróć registry.get(match)

def singledispatch(func):
    """Single-dispatch generic function decorator.

    Transforms a function into a generic function, which can have different
    behaviours depending upon the type of its first argument. The decorated
    function acts jako the default implementation, oraz additional
    implementations can be registered using the register() attribute of the
    generic function.

    """
    registry = {}
    dispatch_cache = WeakKeyDictionary()
    cache_token = Nic

    def dispatch(cls):
        """generic_func.dispatch(cls) -> <function implementation>

        Runs the dispatch algorithm to zwróć the best available implementation
        dla the given *cls* registered on *generic_func*.

        """
        nonlocal cache_token
        jeżeli cache_token jest nie Nic:
            current_token = get_cache_token()
            jeżeli cache_token != current_token:
                dispatch_cache.clear()
                cache_token = current_token
        spróbuj:
            impl = dispatch_cache[cls]
        wyjąwszy KeyError:
            spróbuj:
                impl = registry[cls]
            wyjąwszy KeyError:
                impl = _find_impl(cls, registry)
            dispatch_cache[cls] = impl
        zwróć impl

    def register(cls, func=Nic):
        """generic_func.register(cls, func) -> func

        Registers a new implementation dla the given *cls* on a *generic_func*.

        """
        nonlocal cache_token
        jeżeli func jest Nic:
            zwróć lambda f: register(cls, f)
        registry[cls] = func
        jeżeli cache_token jest Nic oraz hasattr(cls, '__abstractmethods__'):
            cache_token = get_cache_token()
        dispatch_cache.clear()
        zwróć func

    def wrapper(*args, **kw):
        zwróć dispatch(args[0].__class__)(*args, **kw)

    registry[object] = func
    wrapper.register = register
    wrapper.dispatch = dispatch
    wrapper.registry = MappingProxyType(registry)
    wrapper._clear_cache = dispatch_cache.clear
    update_wrapper(wrapper, func)
    zwróć wrapper
