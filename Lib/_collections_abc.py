# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Abstract Base Classes (ABCs) dla collections, according to PEP 3119.

Unit tests are w test_collections.
"""

z abc zaimportuj ABCMeta, abstractmethod
zaimportuj sys

__all__ = ["Awaitable", "Coroutine", "AsyncIterable", "AsyncIterator",
           "Hashable", "Iterable", "Iterator", "Generator",
           "Sized", "Container", "Callable",
           "Set", "MutableSet",
           "Mapping", "MutableMapping",
           "MappingView", "KeysView", "ItemsView", "ValuesView",
           "Sequence", "MutableSequence",
           "ByteString",
           ]

# This module has been renamed z collections.abc to _collections_abc to
# speed up interpreter startup. Some of the types such jako MutableMapping are
# required early but collections module imports a lot of other modules.
# See issue #19218
__name__ = "collections.abc"

# Private list of types that we want to register przy the various ABCs
# so that they will dalej tests like:
#       it = iter(somebytearray)
#       assert isinstance(it, Iterable)
# Note:  w other implementations, these types many nie be distinct
# oraz they make have their own implementation specific types that
# are nie included on this list.
bytes_iterator = type(iter(b''))
bytearray_iterator = type(iter(bytearray()))
#callable_iterator = ???
dict_keyiterator = type(iter({}.keys()))
dict_valueiterator = type(iter({}.values()))
dict_itemiterator = type(iter({}.items()))
list_iterator = type(iter([]))
list_reverseiterator = type(iter(reversed([])))
range_iterator = type(iter(range(0)))
set_iterator = type(iter(set()))
str_iterator = type(iter(""))
tuple_iterator = type(iter(()))
zip_iterator = type(iter(zip()))
## views ##
dict_keys = type({}.keys())
dict_values = type({}.values())
dict_items = type({}.items())
## misc ##
mappingproxy = type(type.__dict__)
generator = type((lambda: (uzyskaj))())
## coroutine ##
async def _coro(): dalej
_coro = _coro()
coroutine = type(_coro)
_coro.close()  # Prevent ResourceWarning
usuń _coro


### ONE-TRICK PONIES ###

klasa Hashable(metaclass=ABCMeta):

    __slots__ = ()

    @abstractmethod
    def __hash__(self):
        zwróć 0

    @classmethod
    def __subclasshook__(cls, C):
        jeżeli cls jest Hashable:
            dla B w C.__mro__:
                jeżeli "__hash__" w B.__dict__:
                    jeżeli B.__dict__["__hash__"]:
                        zwróć Prawda
                    przerwij
        zwróć NotImplemented


klasa Awaitable(metaclass=ABCMeta):

    __slots__ = ()

    @abstractmethod
    def __await__(self):
        uzyskaj

    @classmethod
    def __subclasshook__(cls, C):
        jeżeli cls jest Awaitable:
            dla B w C.__mro__:
                jeżeli "__await__" w B.__dict__:
                    jeżeli B.__dict__["__await__"]:
                        zwróć Prawda
                    przerwij
        zwróć NotImplemented


klasa Coroutine(Awaitable):

    __slots__ = ()

    @abstractmethod
    def send(self, value):
        """Send a value into the coroutine.
        Return next uzyskajed value albo podnieś StopIteration.
        """
        podnieś StopIteration

    @abstractmethod
    def throw(self, typ, val=Nic, tb=Nic):
        """Raise an exception w the coroutine.
        Return next uzyskajed value albo podnieś StopIteration.
        """
        jeżeli val jest Nic:
            jeżeli tb jest Nic:
                podnieś typ
            val = typ()
        jeżeli tb jest nie Nic:
            val = val.with_traceback(tb)
        podnieś val

    def close(self):
        """Raise GeneratorExit inside coroutine.
        """
        spróbuj:
            self.throw(GeneratorExit)
        wyjąwszy (GeneratorExit, StopIteration):
            dalej
        inaczej:
            podnieś RuntimeError("coroutine ignored GeneratorExit")

    @classmethod
    def __subclasshook__(cls, C):
        jeżeli cls jest Coroutine:
            mro = C.__mro__
            dla method w ('__await__', 'send', 'throw', 'close'):
                dla base w mro:
                    jeżeli method w base.__dict__:
                        przerwij
                inaczej:
                    zwróć NotImplemented
            zwróć Prawda
        zwróć NotImplemented


Coroutine.register(coroutine)


klasa AsyncIterable(metaclass=ABCMeta):

    __slots__ = ()

    @abstractmethod
    async def __aiter__(self):
        zwróć AsyncIterator()

    @classmethod
    def __subclasshook__(cls, C):
        jeżeli cls jest AsyncIterable:
            jeżeli any("__aiter__" w B.__dict__ dla B w C.__mro__):
                zwróć Prawda
        zwróć NotImplemented


klasa AsyncIterator(AsyncIterable):

    __slots__ = ()

    @abstractmethod
    async def __anext__(self):
        """Return the next item albo podnieś StopAsyncIteration when exhausted."""
        podnieś StopAsyncIteration

    async def __aiter__(self):
        zwróć self

    @classmethod
    def __subclasshook__(cls, C):
        jeżeli cls jest AsyncIterator:
            jeżeli (any("__anext__" w B.__dict__ dla B w C.__mro__) oraz
                any("__aiter__" w B.__dict__ dla B w C.__mro__)):
                zwróć Prawda
        zwróć NotImplemented


klasa Iterable(metaclass=ABCMeta):

    __slots__ = ()

    @abstractmethod
    def __iter__(self):
        dopóki Nieprawda:
            uzyskaj Nic

    @classmethod
    def __subclasshook__(cls, C):
        jeżeli cls jest Iterable:
            jeżeli any("__iter__" w B.__dict__ dla B w C.__mro__):
                zwróć Prawda
        zwróć NotImplemented


klasa Iterator(Iterable):

    __slots__ = ()

    @abstractmethod
    def __next__(self):
        'Return the next item z the iterator. When exhausted, podnieś StopIteration'
        podnieś StopIteration

    def __iter__(self):
        zwróć self

    @classmethod
    def __subclasshook__(cls, C):
        jeżeli cls jest Iterator:
            jeżeli (any("__next__" w B.__dict__ dla B w C.__mro__) oraz
                any("__iter__" w B.__dict__ dla B w C.__mro__)):
                zwróć Prawda
        zwróć NotImplemented

Iterator.register(bytes_iterator)
Iterator.register(bytearray_iterator)
#Iterator.register(callable_iterator)
Iterator.register(dict_keyiterator)
Iterator.register(dict_valueiterator)
Iterator.register(dict_itemiterator)
Iterator.register(list_iterator)
Iterator.register(list_reverseiterator)
Iterator.register(range_iterator)
Iterator.register(set_iterator)
Iterator.register(str_iterator)
Iterator.register(tuple_iterator)
Iterator.register(zip_iterator)


klasa Generator(Iterator):

    __slots__ = ()

    def __next__(self):
        """Return the next item z the generator.
        When exhausted, podnieś StopIteration.
        """
        zwróć self.send(Nic)

    @abstractmethod
    def send(self, value):
        """Send a value into the generator.
        Return next uzyskajed value albo podnieś StopIteration.
        """
        podnieś StopIteration

    @abstractmethod
    def throw(self, typ, val=Nic, tb=Nic):
        """Raise an exception w the generator.
        Return next uzyskajed value albo podnieś StopIteration.
        """
        jeżeli val jest Nic:
            jeżeli tb jest Nic:
                podnieś typ
            val = typ()
        jeżeli tb jest nie Nic:
            val = val.with_traceback(tb)
        podnieś val

    def close(self):
        """Raise GeneratorExit inside generator.
        """
        spróbuj:
            self.throw(GeneratorExit)
        wyjąwszy (GeneratorExit, StopIteration):
            dalej
        inaczej:
            podnieś RuntimeError("generator ignored GeneratorExit")

    @classmethod
    def __subclasshook__(cls, C):
        jeżeli cls jest Generator:
            mro = C.__mro__
            dla method w ('__iter__', '__next__', 'send', 'throw', 'close'):
                dla base w mro:
                    jeżeli method w base.__dict__:
                        przerwij
                inaczej:
                    zwróć NotImplemented
            zwróć Prawda
        zwróć NotImplemented


Generator.register(generator)


klasa Sized(metaclass=ABCMeta):

    __slots__ = ()

    @abstractmethod
    def __len__(self):
        zwróć 0

    @classmethod
    def __subclasshook__(cls, C):
        jeżeli cls jest Sized:
            jeżeli any("__len__" w B.__dict__ dla B w C.__mro__):
                zwróć Prawda
        zwróć NotImplemented


klasa Container(metaclass=ABCMeta):

    __slots__ = ()

    @abstractmethod
    def __contains__(self, x):
        zwróć Nieprawda

    @classmethod
    def __subclasshook__(cls, C):
        jeżeli cls jest Container:
            jeżeli any("__contains__" w B.__dict__ dla B w C.__mro__):
                zwróć Prawda
        zwróć NotImplemented


klasa Callable(metaclass=ABCMeta):

    __slots__ = ()

    @abstractmethod
    def __call__(self, *args, **kwds):
        zwróć Nieprawda

    @classmethod
    def __subclasshook__(cls, C):
        jeżeli cls jest Callable:
            jeżeli any("__call__" w B.__dict__ dla B w C.__mro__):
                zwróć Prawda
        zwróć NotImplemented


### SETS ###


klasa Set(Sized, Iterable, Container):

    """A set jest a finite, iterable container.

    This klasa provides concrete generic implementations of all
    methods wyjąwszy dla __contains__, __iter__ oraz __len__.

    To override the comparisons (presumably dla speed, jako the
    semantics are fixed), redefine __le__ oraz __ge__,
    then the other operations will automatically follow suit.
    """

    __slots__ = ()

    def __le__(self, other):
        jeżeli nie isinstance(other, Set):
            zwróć NotImplemented
        jeżeli len(self) > len(other):
            zwróć Nieprawda
        dla elem w self:
            jeżeli elem nie w other:
                zwróć Nieprawda
        zwróć Prawda

    def __lt__(self, other):
        jeżeli nie isinstance(other, Set):
            zwróć NotImplemented
        zwróć len(self) < len(other) oraz self.__le__(other)

    def __gt__(self, other):
        jeżeli nie isinstance(other, Set):
            zwróć NotImplemented
        zwróć len(self) > len(other) oraz self.__ge__(other)

    def __ge__(self, other):
        jeżeli nie isinstance(other, Set):
            zwróć NotImplemented
        jeżeli len(self) < len(other):
            zwróć Nieprawda
        dla elem w other:
            jeżeli elem nie w self:
                zwróć Nieprawda
        zwróć Prawda

    def __eq__(self, other):
        jeżeli nie isinstance(other, Set):
            zwróć NotImplemented
        zwróć len(self) == len(other) oraz self.__le__(other)

    @classmethod
    def _from_iterable(cls, it):
        '''Construct an instance of the klasa z any iterable input.

        Must override this method jeżeli the klasa constructor signature
        does nie accept an iterable dla an input.
        '''
        zwróć cls(it)

    def __and__(self, other):
        jeżeli nie isinstance(other, Iterable):
            zwróć NotImplemented
        zwróć self._from_iterable(value dla value w other jeżeli value w self)

    __rand__ = __and__

    def isdisjoint(self, other):
        'Return Prawda jeżeli two sets have a null intersection.'
        dla value w other:
            jeżeli value w self:
                zwróć Nieprawda
        zwróć Prawda

    def __or__(self, other):
        jeżeli nie isinstance(other, Iterable):
            zwróć NotImplemented
        chain = (e dla s w (self, other) dla e w s)
        zwróć self._from_iterable(chain)

    __ror__ = __or__

    def __sub__(self, other):
        jeżeli nie isinstance(other, Set):
            jeżeli nie isinstance(other, Iterable):
                zwróć NotImplemented
            other = self._from_iterable(other)
        zwróć self._from_iterable(value dla value w self
                                   jeżeli value nie w other)

    def __rsub__(self, other):
        jeżeli nie isinstance(other, Set):
            jeżeli nie isinstance(other, Iterable):
                zwróć NotImplemented
            other = self._from_iterable(other)
        zwróć self._from_iterable(value dla value w other
                                   jeżeli value nie w self)

    def __xor__(self, other):
        jeżeli nie isinstance(other, Set):
            jeżeli nie isinstance(other, Iterable):
                zwróć NotImplemented
            other = self._from_iterable(other)
        zwróć (self - other) | (other - self)

    __rxor__ = __xor__

    def _hash(self):
        """Compute the hash value of a set.

        Note that we don't define __hash__: nie all sets are hashable.
        But jeżeli you define a hashable set type, its __hash__ should
        call this function.

        This must be compatible __eq__.

        All sets ought to compare equal jeżeli they contain the same
        elements, regardless of how they are implemented, oraz
        regardless of the order of the elements; so there's nie much
        freedom dla __eq__ albo __hash__.  We match the algorithm used
        by the built-in frozenset type.
        """
        MAX = sys.maxsize
        MASK = 2 * MAX + 1
        n = len(self)
        h = 1927868237 * (n + 1)
        h &= MASK
        dla x w self:
            hx = hash(x)
            h ^= (hx ^ (hx << 16) ^ 89869747)  * 3644798167
            h &= MASK
        h = h * 69069 + 907133923
        h &= MASK
        jeżeli h > MAX:
            h -= MASK + 1
        jeżeli h == -1:
            h = 590923713
        zwróć h

Set.register(frozenset)


klasa MutableSet(Set):
    """A mutable set jest a finite, iterable container.

    This klasa provides concrete generic implementations of all
    methods wyjąwszy dla __contains__, __iter__, __len__,
    add(), oraz discard().

    To override the comparisons (presumably dla speed, jako the
    semantics are fixed), all you have to do jest redefine __le__ oraz
    then the other operations will automatically follow suit.
    """

    __slots__ = ()

    @abstractmethod
    def add(self, value):
        """Add an element."""
        podnieś NotImplementedError

    @abstractmethod
    def discard(self, value):
        """Remove an element.  Do nie podnieś an exception jeżeli absent."""
        podnieś NotImplementedError

    def remove(self, value):
        """Remove an element. If nie a member, podnieś a KeyError."""
        jeżeli value nie w self:
            podnieś KeyError(value)
        self.discard(value)

    def pop(self):
        """Return the popped value.  Raise KeyError jeżeli empty."""
        it = iter(self)
        spróbuj:
            value = next(it)
        wyjąwszy StopIteration:
            podnieś KeyError
        self.discard(value)
        zwróć value

    def clear(self):
        """This jest slow (creates N new iterators!) but effective."""
        spróbuj:
            dopóki Prawda:
                self.pop()
        wyjąwszy KeyError:
            dalej

    def __ior__(self, it):
        dla value w it:
            self.add(value)
        zwróć self

    def __iand__(self, it):
        dla value w (self - it):
            self.discard(value)
        zwróć self

    def __ixor__(self, it):
        jeżeli it jest self:
            self.clear()
        inaczej:
            jeżeli nie isinstance(it, Set):
                it = self._from_iterable(it)
            dla value w it:
                jeżeli value w self:
                    self.discard(value)
                inaczej:
                    self.add(value)
        zwróć self

    def __isub__(self, it):
        jeżeli it jest self:
            self.clear()
        inaczej:
            dla value w it:
                self.discard(value)
        zwróć self

MutableSet.register(set)


### MAPPINGS ###


klasa Mapping(Sized, Iterable, Container):

    __slots__ = ()

    """A Mapping jest a generic container dla associating key/value
    pairs.

    This klasa provides concrete generic implementations of all
    methods wyjąwszy dla __getitem__, __iter__, oraz __len__.

    """

    @abstractmethod
    def __getitem__(self, key):
        podnieś KeyError

    def get(self, key, default=Nic):
        'D.get(k[,d]) -> D[k] jeżeli k w D, inaczej d.  d defaults to Nic.'
        spróbuj:
            zwróć self[key]
        wyjąwszy KeyError:
            zwróć default

    def __contains__(self, key):
        spróbuj:
            self[key]
        wyjąwszy KeyError:
            zwróć Nieprawda
        inaczej:
            zwróć Prawda

    def keys(self):
        "D.keys() -> a set-like object providing a view on D's keys"
        zwróć KeysView(self)

    def items(self):
        "D.items() -> a set-like object providing a view on D's items"
        zwróć ItemsView(self)

    def values(self):
        "D.values() -> an object providing a view on D's values"
        zwróć ValuesView(self)

    def __eq__(self, other):
        jeżeli nie isinstance(other, Mapping):
            zwróć NotImplemented
        zwróć dict(self.items()) == dict(other.items())

Mapping.register(mappingproxy)


klasa MappingView(Sized):

    __slots__ = '_mapping',

    def __init__(self, mapping):
        self._mapping = mapping

    def __len__(self):
        zwróć len(self._mapping)

    def __repr__(self):
        zwróć '{0.__class__.__name__}({0._mapping!r})'.format(self)


klasa KeysView(MappingView, Set):

    __slots__ = ()

    @classmethod
    def _from_iterable(self, it):
        zwróć set(it)

    def __contains__(self, key):
        zwróć key w self._mapping

    def __iter__(self):
        uzyskaj z self._mapping

KeysView.register(dict_keys)


klasa ItemsView(MappingView, Set):

    __slots__ = ()

    @classmethod
    def _from_iterable(self, it):
        zwróć set(it)

    def __contains__(self, item):
        key, value = item
        spróbuj:
            v = self._mapping[key]
        wyjąwszy KeyError:
            zwróć Nieprawda
        inaczej:
            zwróć v == value

    def __iter__(self):
        dla key w self._mapping:
            uzyskaj (key, self._mapping[key])

ItemsView.register(dict_items)


klasa ValuesView(MappingView):

    __slots__ = ()

    def __contains__(self, value):
        dla key w self._mapping:
            jeżeli value == self._mapping[key]:
                zwróć Prawda
        zwróć Nieprawda

    def __iter__(self):
        dla key w self._mapping:
            uzyskaj self._mapping[key]

ValuesView.register(dict_values)


klasa MutableMapping(Mapping):

    __slots__ = ()

    """A MutableMapping jest a generic container dla associating
    key/value pairs.

    This klasa provides concrete generic implementations of all
    methods wyjąwszy dla __getitem__, __setitem__, __delitem__,
    __iter__, oraz __len__.

    """

    @abstractmethod
    def __setitem__(self, key, value):
        podnieś KeyError

    @abstractmethod
    def __delitem__(self, key):
        podnieś KeyError

    __marker = object()

    def pop(self, key, default=__marker):
        '''D.pop(k[,d]) -> v, remove specified key oraz zwróć the corresponding value.
          If key jest nie found, d jest returned jeżeli given, otherwise KeyError jest podnieśd.
        '''
        spróbuj:
            value = self[key]
        wyjąwszy KeyError:
            jeżeli default jest self.__marker:
                podnieś
            zwróć default
        inaczej:
            usuń self[key]
            zwróć value

    def popitem(self):
        '''D.popitem() -> (k, v), remove oraz zwróć some (key, value) pair
           jako a 2-tuple; but podnieś KeyError jeżeli D jest empty.
        '''
        spróbuj:
            key = next(iter(self))
        wyjąwszy StopIteration:
            podnieś KeyError
        value = self[key]
        usuń self[key]
        zwróć key, value

    def clear(self):
        'D.clear() -> Nic.  Remove all items z D.'
        spróbuj:
            dopóki Prawda:
                self.popitem()
        wyjąwszy KeyError:
            dalej

    def update(*args, **kwds):
        ''' D.update([E, ]**F) -> Nic.  Update D z mapping/iterable E oraz F.
            If E present oraz has a .keys() method, does:     dla k w E: D[k] = E[k]
            If E present oraz lacks .keys() method, does:     dla (k, v) w E: D[k] = v
            In either case, this jest followed by: dla k, v w F.items(): D[k] = v
        '''
        jeżeli nie args:
            podnieś TypeError("descriptor 'update' of 'MutableMapping' object "
                            "needs an argument")
        self, *args = args
        jeżeli len(args) > 1:
            podnieś TypeError('update expected at most 1 arguments, got %d' %
                            len(args))
        jeżeli args:
            other = args[0]
            jeżeli isinstance(other, Mapping):
                dla key w other:
                    self[key] = other[key]
            albo_inaczej hasattr(other, "keys"):
                dla key w other.keys():
                    self[key] = other[key]
            inaczej:
                dla key, value w other:
                    self[key] = value
        dla key, value w kwds.items():
            self[key] = value

    def setdefault(self, key, default=Nic):
        'D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d jeżeli k nie w D'
        spróbuj:
            zwróć self[key]
        wyjąwszy KeyError:
            self[key] = default
        zwróć default

MutableMapping.register(dict)


### SEQUENCES ###


klasa Sequence(Sized, Iterable, Container):

    """All the operations on a read-only sequence.

    Concrete subclasses must override __new__ albo __init__,
    __getitem__, oraz __len__.
    """

    __slots__ = ()

    @abstractmethod
    def __getitem__(self, index):
        podnieś IndexError

    def __iter__(self):
        i = 0
        spróbuj:
            dopóki Prawda:
                v = self[i]
                uzyskaj v
                i += 1
        wyjąwszy IndexError:
            zwróć

    def __contains__(self, value):
        dla v w self:
            jeżeli v == value:
                zwróć Prawda
        zwróć Nieprawda

    def __reversed__(self):
        dla i w reversed(range(len(self))):
            uzyskaj self[i]

    def index(self, value, start=0, stop=Nic):
        '''S.index(value, [start, [stop]]) -> integer -- zwróć first index of value.
           Raises ValueError jeżeli the value jest nie present.
        '''
        jeżeli start jest nie Nic oraz start < 0:
            start = max(len(self) + start, 0)
        jeżeli stop jest nie Nic oraz stop < 0:
            stop += len(self)

        i = start
        dopóki stop jest Nic albo i < stop:
            spróbuj:
                jeżeli self[i] == value:
                    zwróć i
            wyjąwszy IndexError:
                przerwij
            i += 1
        podnieś ValueError

    def count(self, value):
        'S.count(value) -> integer -- zwróć number of occurrences of value'
        zwróć sum(1 dla v w self jeżeli v == value)

Sequence.register(tuple)
Sequence.register(str)
Sequence.register(range)
Sequence.register(memoryview)


klasa ByteString(Sequence):

    """This unifies bytes oraz bytearray.

    XXX Should add all their methods.
    """

    __slots__ = ()

ByteString.register(bytes)
ByteString.register(bytearray)


klasa MutableSequence(Sequence):

    __slots__ = ()

    """All the operations on a read-write sequence.

    Concrete subclasses must provide __new__ albo __init__,
    __getitem__, __setitem__, __delitem__, __len__, oraz insert().

    """

    @abstractmethod
    def __setitem__(self, index, value):
        podnieś IndexError

    @abstractmethod
    def __delitem__(self, index):
        podnieś IndexError

    @abstractmethod
    def insert(self, index, value):
        'S.insert(index, value) -- insert value before index'
        podnieś IndexError

    def append(self, value):
        'S.append(value) -- append value to the end of the sequence'
        self.insert(len(self), value)

    def clear(self):
        'S.clear() -> Nic -- remove all items z S'
        spróbuj:
            dopóki Prawda:
                self.pop()
        wyjąwszy IndexError:
            dalej

    def reverse(self):
        'S.reverse() -- reverse *IN PLACE*'
        n = len(self)
        dla i w range(n//2):
            self[i], self[n-i-1] = self[n-i-1], self[i]

    def extend(self, values):
        'S.extend(iterable) -- extend sequence by appending elements z the iterable'
        dla v w values:
            self.append(v)

    def pop(self, index=-1):
        '''S.pop([index]) -> item -- remove oraz zwróć item at index (default last).
           Raise IndexError jeżeli list jest empty albo index jest out of range.
        '''
        v = self[index]
        usuń self[index]
        zwróć v

    def remove(self, value):
        '''S.remove(value) -- remove first occurrence of value.
           Raise ValueError jeżeli the value jest nie present.
        '''
        usuń self[self.index(value)]

    def __iadd__(self, values):
        self.extend(values)
        zwróć self

MutableSequence.register(list)
MutableSequence.register(bytearray)  # Multiply inheriting, see ByteString
