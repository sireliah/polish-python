__all__ = ['deque', 'defaultdict', 'namedtuple', 'UserDict', 'UserList',
            'UserString', 'Counter', 'OrderedDict', 'ChainMap']

# For backwards compatibility, continue to make the collections ABCs
# available through the collections module.
z _collections_abc zaimportuj *
zaimportuj _collections_abc
__all__ += _collections_abc.__all__

z operator zaimportuj itemgetter jako _itemgetter, eq jako _eq
z keyword zaimportuj iskeyword jako _iskeyword
zaimportuj sys jako _sys
zaimportuj heapq jako _heapq
z _weakref zaimportuj proxy jako _proxy
z itertools zaimportuj repeat jako _repeat, chain jako _chain, starmap jako _starmap
z reprlib zaimportuj recursive_repr jako _recursive_repr

spróbuj:
    z _collections zaimportuj deque
wyjąwszy ImportError:
    dalej
inaczej:
    MutableSequence.register(deque)

spróbuj:
    z _collections zaimportuj defaultdict
wyjąwszy ImportError:
    dalej


################################################################################
### OrderedDict
################################################################################

klasa _OrderedDictKeysView(KeysView):

    def __reversed__(self):
        uzyskaj z reversed(self._mapping)

klasa _OrderedDictItemsView(ItemsView):

    def __reversed__(self):
        dla key w reversed(self._mapping):
            uzyskaj (key, self._mapping[key])

klasa _OrderedDictValuesView(ValuesView):

    def __reversed__(self):
        dla key w reversed(self._mapping):
            uzyskaj self._mapping[key]

klasa _Link(object):
    __slots__ = 'prev', 'next', 'key', '__weakref__'

klasa OrderedDict(dict):
    'Dictionary that remembers insertion order'
    # An inherited dict maps keys to values.
    # The inherited dict provides __getitem__, __len__, __contains__, oraz get.
    # The remaining methods are order-aware.
    # Big-O running times dla all methods are the same jako regular dictionaries.

    # The internal self.__map dict maps keys to links w a doubly linked list.
    # The circular doubly linked list starts oraz ends przy a sentinel element.
    # The sentinel element never gets deleted (this simplifies the algorithm).
    # The sentinel jest w self.__hardroot przy a weakref proxy w self.__root.
    # The prev links are weakref proxies (to prevent circular references).
    # Individual links are kept alive by the hard reference w self.__map.
    # Those hard references disappear when a key jest deleted z an OrderedDict.

    def __init__(*args, **kwds):
        '''Initialize an ordered dictionary.  The signature jest the same as
        regular dictionaries, but keyword arguments are nie recommended because
        their insertion order jest arbitrary.

        '''
        jeżeli nie args:
            podnieś TypeError("descriptor '__init__' of 'OrderedDict' object "
                            "needs an argument")
        self, *args = args
        jeżeli len(args) > 1:
            podnieś TypeError('expected at most 1 arguments, got %d' % len(args))
        spróbuj:
            self.__root
        wyjąwszy AttributeError:
            self.__hardroot = _Link()
            self.__root = root = _proxy(self.__hardroot)
            root.prev = root.next = root
            self.__map = {}
        self.__update(*args, **kwds)

    def __setitem__(self, key, value,
                    dict_setitem=dict.__setitem__, proxy=_proxy, Link=_Link):
        'od.__setitem__(i, y) <==> od[i]=y'
        # Setting a new item creates a new link at the end of the linked list,
        # oraz the inherited dictionary jest updated przy the new key/value pair.
        jeżeli key nie w self:
            self.__map[key] = link = Link()
            root = self.__root
            last = root.prev
            link.prev, link.next, link.key = last, root, key
            last.next = link
            root.prev = proxy(link)
        dict_setitem(self, key, value)

    def __delitem__(self, key, dict_delitem=dict.__delitem__):
        'od.__delitem__(y) <==> usuń od[y]'
        # Deleting an existing item uses self.__map to find the link which gets
        # removed by updating the links w the predecessor oraz successor nodes.
        dict_delitem(self, key)
        link = self.__map.pop(key)
        link_prev = link.prev
        link_next = link.next
        link_prev.next = link_next
        link_next.prev = link_prev
        link.prev = Nic
        link.next = Nic

    def __iter__(self):
        'od.__iter__() <==> iter(od)'
        # Traverse the linked list w order.
        root = self.__root
        curr = root.next
        dopóki curr jest nie root:
            uzyskaj curr.key
            curr = curr.next

    def __reversed__(self):
        'od.__reversed__() <==> reversed(od)'
        # Traverse the linked list w reverse order.
        root = self.__root
        curr = root.prev
        dopóki curr jest nie root:
            uzyskaj curr.key
            curr = curr.prev

    def clear(self):
        'od.clear() -> Nic.  Remove all items z od.'
        root = self.__root
        root.prev = root.next = root
        self.__map.clear()
        dict.clear(self)

    def popitem(self, last=Prawda):
        '''od.popitem() -> (k, v), zwróć oraz remove a (key, value) pair.
        Pairs are returned w LIFO order jeżeli last jest true albo FIFO order jeżeli false.

        '''
        jeżeli nie self:
            podnieś KeyError('dictionary jest empty')
        root = self.__root
        jeżeli last:
            link = root.prev
            link_prev = link.prev
            link_prev.next = root
            root.prev = link_prev
        inaczej:
            link = root.next
            link_next = link.next
            root.next = link_next
            link_next.prev = root
        key = link.key
        usuń self.__map[key]
        value = dict.pop(self, key)
        zwróć key, value

    def move_to_end(self, key, last=Prawda):
        '''Move an existing element to the end (or beginning jeżeli last==Nieprawda).

        Raises KeyError jeżeli the element does nie exist.
        When last=Prawda, acts like a fast version of self[key]=self.pop(key).

        '''
        link = self.__map[key]
        link_prev = link.prev
        link_next = link.next
        link_prev.next = link_next
        link_next.prev = link_prev
        root = self.__root
        jeżeli last:
            last = root.prev
            link.prev = last
            link.next = root
            last.next = root.prev = link
        inaczej:
            first = root.next
            link.prev = root
            link.next = first
            root.next = first.prev = link

    def __sizeof__(self):
        sizeof = _sys.getsizeof
        n = len(self) + 1                       # number of links including root
        size = sizeof(self.__dict__)            # instance dictionary
        size += sizeof(self.__map) * 2          # internal dict oraz inherited dict
        size += sizeof(self.__hardroot) * n     # link objects
        size += sizeof(self.__root) * n         # proxy objects
        zwróć size

    update = __update = MutableMapping.update

    def keys(self):
        "D.keys() -> a set-like object providing a view on D's keys"
        zwróć _OrderedDictKeysView(self)

    def items(self):
        "D.items() -> a set-like object providing a view on D's items"
        zwróć _OrderedDictItemsView(self)

    def values(self):
        "D.values() -> an object providing a view on D's values"
        zwróć _OrderedDictValuesView(self)

    __ne__ = MutableMapping.__ne__

    __marker = object()

    def pop(self, key, default=__marker):
        '''od.pop(k[,d]) -> v, remove specified key oraz zwróć the corresponding
        value.  If key jest nie found, d jest returned jeżeli given, otherwise KeyError
        jest podnieśd.

        '''
        jeżeli key w self:
            result = self[key]
            usuń self[key]
            zwróć result
        jeżeli default jest self.__marker:
            podnieś KeyError(key)
        zwróć default

    def setdefault(self, key, default=Nic):
        'od.setdefault(k[,d]) -> od.get(k,d), also set od[k]=d jeżeli k nie w od'
        jeżeli key w self:
            zwróć self[key]
        self[key] = default
        zwróć default

    @_recursive_repr()
    def __repr__(self):
        'od.__repr__() <==> repr(od)'
        jeżeli nie self:
            zwróć '%s()' % (self.__class__.__name__,)
        zwróć '%s(%r)' % (self.__class__.__name__, list(self.items()))

    def __reduce__(self):
        'Return state information dla pickling'
        inst_dict = vars(self).copy()
        dla k w vars(OrderedDict()):
            inst_dict.pop(k, Nic)
        zwróć self.__class__, (), inst_dict albo Nic, Nic, iter(self.items())

    def copy(self):
        'od.copy() -> a shallow copy of od'
        zwróć self.__class__(self)

    @classmethod
    def fromkeys(cls, iterable, value=Nic):
        '''OD.fromkeys(S[, v]) -> New ordered dictionary przy keys z S.
        If nie specified, the value defaults to Nic.

        '''
        self = cls()
        dla key w iterable:
            self[key] = value
        zwróć self

    def __eq__(self, other):
        '''od.__eq__(y) <==> od==y.  Comparison to another OD jest order-sensitive
        dopóki comparison to a regular mapping jest order-insensitive.

        '''
        jeżeli isinstance(other, OrderedDict):
            zwróć dict.__eq__(self, other) oraz all(map(_eq, self, other))
        zwróć dict.__eq__(self, other)


spróbuj:
    z _collections zaimportuj OrderedDict
wyjąwszy ImportError:
    # Leave the pure Python version w place.
    dalej


################################################################################
### namedtuple
################################################################################

_class_template = """\
z builtins zaimportuj property jako _property, tuple jako _tuple
z operator zaimportuj itemgetter jako _itemgetter
z collections zaimportuj OrderedDict

klasa {typename}(tuple):
    '{typename}({arg_list})'

    __slots__ = ()

    _fields = {field_names!r}

    def __new__(_cls, {arg_list}):
        'Create new instance of {typename}({arg_list})'
        zwróć _tuple.__new__(_cls, ({arg_list}))

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new {typename} object z a sequence albo iterable'
        result = new(cls, iterable)
        jeżeli len(result) != {num_fields:d}:
            podnieś TypeError('Expected {num_fields:d} arguments, got %d' % len(result))
        zwróć result

    def _replace(_self, **kwds):
        'Return a new {typename} object replacing specified fields przy new values'
        result = _self._make(map(kwds.pop, {field_names!r}, _self))
        jeżeli kwds:
            podnieś ValueError('Got unexpected field names: %r' % list(kwds))
        zwróć result

    def __repr__(self):
        'Return a nicely formatted representation string'
        zwróć self.__class__.__name__ + '({repr_fmt})' % self

    @property
    def __dict__(self):
        'A new OrderedDict mapping field names to their values'
        zwróć OrderedDict(zip(self._fields, self))

    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values.'
        zwróć self.__dict__

    def __getnewargs__(self):
        'Return self jako a plain tuple.  Used by copy oraz pickle.'
        zwróć tuple(self)

    def __getstate__(self):
        'Exclude the OrderedDict z pickling'
        zwróć Nic

{field_defs}
"""

_repr_template = '{name}=%r'

_field_template = '''\
    {name} = _property(_itemgetter({index:d}), doc='Alias dla field number {index:d}')
'''

def namedtuple(typename, field_names, verbose=Nieprawda, rename=Nieprawda):
    """Returns a new subclass of tuple przy named fields.

    >>> Point = namedtuple('Point', ['x', 'y'])
    >>> Point.__doc__                   # docstring dla the new class
    'Point(x, y)'
    >>> p = Point(11, y=22)             # instantiate przy positional args albo keywords
    >>> p[0] + p[1]                     # indexable like a plain tuple
    33
    >>> x, y = p                        # unpack like a regular tuple
    >>> x, y
    (11, 22)
    >>> p.x + p.y                       # fields also accessable by name
    33
    >>> d = p._asdict()                 # convert to a dictionary
    >>> d['x']
    11
    >>> Point(**d)                      # convert z a dictionary
    Point(x=11, y=22)
    >>> p._replace(x=100)               # _replace() jest like str.replace() but targets named fields
    Point(x=100, y=22)

    """

    # Validate the field names.  At the user's option, either generate an error
    # message albo automatically replace the field name przy a valid name.
    jeżeli isinstance(field_names, str):
        field_names = field_names.replace(',', ' ').split()
    field_names = list(map(str, field_names))
    typename = str(typename)
    jeżeli rename:
        seen = set()
        dla index, name w enumerate(field_names):
            jeżeli (nie name.isidentifier()
                albo _iskeyword(name)
                albo name.startswith('_')
                albo name w seen):
                field_names[index] = '_%d' % index
            seen.add(name)
    dla name w [typename] + field_names:
        jeżeli type(name) != str:
            podnieś TypeError('Type names oraz field names must be strings')
        jeżeli nie name.isidentifier():
            podnieś ValueError('Type names oraz field names must be valid '
                             'identifiers: %r' % name)
        jeżeli _iskeyword(name):
            podnieś ValueError('Type names oraz field names cannot be a '
                             'keyword: %r' % name)
    seen = set()
    dla name w field_names:
        jeżeli name.startswith('_') oraz nie rename:
            podnieś ValueError('Field names cannot start przy an underscore: '
                             '%r' % name)
        jeżeli name w seen:
            podnieś ValueError('Encountered duplicate field name: %r' % name)
        seen.add(name)

    # Fill-in the klasa template
    class_definition = _class_template.format(
        typename = typename,
        field_names = tuple(field_names),
        num_fields = len(field_names),
        arg_list = repr(tuple(field_names)).replace("'", "")[1:-1],
        repr_fmt = ', '.join(_repr_template.format(name=name)
                             dla name w field_names),
        field_defs = '\n'.join(_field_template.format(index=index, name=name)
                               dla index, name w enumerate(field_names))
    )

    # Execute the template string w a temporary namespace oraz support
    # tracing utilities by setting a value dla frame.f_globals['__name__']
    namespace = dict(__name__='namedtuple_%s' % typename)
    exec(class_definition, namespace)
    result = namespace[typename]
    result._source = class_definition
    jeżeli verbose:
        print(result._source)

    # For pickling to work, the __module__ variable needs to be set to the frame
    # where the named tuple jest created.  Bypass this step w environments where
    # sys._getframe jest nie defined (Jython dla example) albo sys._getframe jest nie
    # defined dla arguments greater than 0 (IronPython).
    spróbuj:
        result.__module__ = _sys._getframe(1).f_globals.get('__name__', '__main__')
    wyjąwszy (AttributeError, ValueError):
        dalej

    zwróć result


########################################################################
###  Counter
########################################################################

def _count_elements(mapping, iterable):
    'Tally elements z the iterable.'
    mapping_get = mapping.get
    dla elem w iterable:
        mapping[elem] = mapping_get(elem, 0) + 1

spróbuj:                                    # Load C helper function jeżeli available
    z _collections zaimportuj _count_elements
wyjąwszy ImportError:
    dalej

klasa Counter(dict):
    '''Dict subclass dla counting hashable items.  Sometimes called a bag
    albo multiset.  Elements are stored jako dictionary keys oraz their counts
    are stored jako dictionary values.

    >>> c = Counter('abcdeabcdabcaba')  # count elements z a string

    >>> c.most_common(3)                # three most common elements
    [('a', 5), ('b', 4), ('c', 3)]
    >>> sorted(c)                       # list all unique elements
    ['a', 'b', 'c', 'd', 'e']
    >>> ''.join(sorted(c.elements()))   # list elements przy repetitions
    'aaaaabbbbcccdde'
    >>> sum(c.values())                 # total of all counts
    15

    >>> c['a']                          # count of letter 'a'
    5
    >>> dla elem w 'shazam':           # update counts z an iterable
    ...     c[elem] += 1                # by adding 1 to each element's count
    >>> c['a']                          # now there are seven 'a'
    7
    >>> usuń c['b']                      # remove all 'b'
    >>> c['b']                          # now there are zero 'b'
    0

    >>> d = Counter('simsalabim')       # make another counter
    >>> c.update(d)                     # add w the second counter
    >>> c['a']                          # now there are nine 'a'
    9

    >>> c.clear()                       # empty the counter
    >>> c
    Counter()

    Note:  If a count jest set to zero albo reduced to zero, it will remain
    w the counter until the entry jest deleted albo the counter jest cleared:

    >>> c = Counter('aaabbc')
    >>> c['b'] -= 2                     # reduce the count of 'b' by two
    >>> c.most_common()                 # 'b' jest still in, but its count jest zero
    [('a', 3), ('c', 1), ('b', 0)]

    '''
    # References:
    #   http://en.wikipedia.org/wiki/Multiset
    #   http://www.gnu.org/software/smalltalk/manual-base/html_node/Bag.html
    #   http://www.demo2s.com/Tutorial/Cpp/0380__set-multiset/Catalog0380__set-multiset.htm
    #   http://code.activestate.com/recipes/259174/
    #   Knuth, TAOCP Vol. II section 4.6.3

    def __init__(*args, **kwds):
        '''Create a new, empty Counter object.  And jeżeli given, count elements
        z an input iterable.  Or, initialize the count z another mapping
        of elements to their counts.

        >>> c = Counter()                           # a new, empty counter
        >>> c = Counter('gallahad')                 # a new counter z an iterable
        >>> c = Counter({'a': 4, 'b': 2})           # a new counter z a mapping
        >>> c = Counter(a=4, b=2)                   # a new counter z keyword args

        '''
        jeżeli nie args:
            podnieś TypeError("descriptor '__init__' of 'Counter' object "
                            "needs an argument")
        self, *args = args
        jeżeli len(args) > 1:
            podnieś TypeError('expected at most 1 arguments, got %d' % len(args))
        super(Counter, self).__init__()
        self.update(*args, **kwds)

    def __missing__(self, key):
        'The count of elements nie w the Counter jest zero.'
        # Needed so that self[missing_item] does nie podnieś KeyError
        zwróć 0

    def most_common(self, n=Nic):
        '''List the n most common elements oraz their counts z the most
        common to the least.  If n jest Nic, then list all element counts.

        >>> Counter('abcdeabcdabcaba').most_common(3)
        [('a', 5), ('b', 4), ('c', 3)]

        '''
        # Emulate Bag.sortedByCount z Smalltalk
        jeżeli n jest Nic:
            zwróć sorted(self.items(), key=_itemgetter(1), reverse=Prawda)
        zwróć _heapq.nlargest(n, self.items(), key=_itemgetter(1))

    def elements(self):
        '''Iterator over elements repeating each jako many times jako its count.

        >>> c = Counter('ABCABC')
        >>> sorted(c.elements())
        ['A', 'A', 'B', 'B', 'C', 'C']

        # Knuth's example dla prime factors of 1836:  2**2 * 3**3 * 17**1
        >>> prime_factors = Counter({2: 2, 3: 3, 17: 1})
        >>> product = 1
        >>> dla factor w prime_factors.elements():     # loop over factors
        ...     product *= factor                       # oraz multiply them
        >>> product
        1836

        Note, jeżeli an element's count has been set to zero albo jest a negative
        number, elements() will ignore it.

        '''
        # Emulate Bag.do z Smalltalk oraz Multiset.begin z C++.
        zwróć _chain.from_iterable(_starmap(_repeat, self.items()))

    # Override dict methods where necessary

    @classmethod
    def fromkeys(cls, iterable, v=Nic):
        # There jest no equivalent method dla counters because setting v=1
        # means that no element can have a count greater than one.
        podnieś NotImplementedError(
            'Counter.fromkeys() jest undefined.  Use Counter(iterable) instead.')

    def update(*args, **kwds):
        '''Like dict.update() but add counts instead of replacing them.

        Source can be an iterable, a dictionary, albo another Counter instance.

        >>> c = Counter('which')
        >>> c.update('witch')           # add elements z another iterable
        >>> d = Counter('watch')
        >>> c.update(d)                 # add elements z another counter
        >>> c['h']                      # four 'h' w which, witch, oraz watch
        4

        '''
        # The regular dict.update() operation makes no sense here because the
        # replace behavior results w the some of original untouched counts
        # being mixed-in przy all of the other counts dla a mismash that
        # doesn't have a straight-forward interpretation w most counting
        # contexts.  Instead, we implement straight-addition.  Both the inputs
        # oraz outputs are allowed to contain zero oraz negative counts.

        jeżeli nie args:
            podnieś TypeError("descriptor 'update' of 'Counter' object "
                            "needs an argument")
        self, *args = args
        jeżeli len(args) > 1:
            podnieś TypeError('expected at most 1 arguments, got %d' % len(args))
        iterable = args[0] jeżeli args inaczej Nic
        jeżeli iterable jest nie Nic:
            jeżeli isinstance(iterable, Mapping):
                jeżeli self:
                    self_get = self.get
                    dla elem, count w iterable.items():
                        self[elem] = count + self_get(elem, 0)
                inaczej:
                    super(Counter, self).update(iterable) # fast path when counter jest empty
            inaczej:
                _count_elements(self, iterable)
        jeżeli kwds:
            self.update(kwds)

    def subtract(*args, **kwds):
        '''Like dict.update() but subtracts counts instead of replacing them.
        Counts can be reduced below zero.  Both the inputs oraz outputs are
        allowed to contain zero oraz negative counts.

        Source can be an iterable, a dictionary, albo another Counter instance.

        >>> c = Counter('which')
        >>> c.subtract('witch')             # subtract elements z another iterable
        >>> c.subtract(Counter('watch'))    # subtract elements z another counter
        >>> c['h']                          # 2 w which, minus 1 w witch, minus 1 w watch
        0
        >>> c['w']                          # 1 w which, minus 1 w witch, minus 1 w watch
        -1

        '''
        jeżeli nie args:
            podnieś TypeError("descriptor 'subtract' of 'Counter' object "
                            "needs an argument")
        self, *args = args
        jeżeli len(args) > 1:
            podnieś TypeError('expected at most 1 arguments, got %d' % len(args))
        iterable = args[0] jeżeli args inaczej Nic
        jeżeli iterable jest nie Nic:
            self_get = self.get
            jeżeli isinstance(iterable, Mapping):
                dla elem, count w iterable.items():
                    self[elem] = self_get(elem, 0) - count
            inaczej:
                dla elem w iterable:
                    self[elem] = self_get(elem, 0) - 1
        jeżeli kwds:
            self.subtract(kwds)

    def copy(self):
        'Return a shallow copy.'
        zwróć self.__class__(self)

    def __reduce__(self):
        zwróć self.__class__, (dict(self),)

    def __delitem__(self, elem):
        'Like dict.__delitem__() but does nie podnieś KeyError dla missing values.'
        jeżeli elem w self:
            super().__delitem__(elem)

    def __repr__(self):
        jeżeli nie self:
            zwróć '%s()' % self.__class__.__name__
        spróbuj:
            items = ', '.join(map('%r: %r'.__mod__, self.most_common()))
            zwróć '%s({%s})' % (self.__class__.__name__, items)
        wyjąwszy TypeError:
            # handle case where values are nie orderable
            zwróć '{0}({1!r})'.format(self.__class__.__name__, dict(self))

    # Multiset-style mathematical operations discussed in:
    #       Knuth TAOCP Volume II section 4.6.3 exercise 19
    #       oraz at http://en.wikipedia.org/wiki/Multiset
    #
    # Outputs guaranteed to only include positive counts.
    #
    # To strip negative oraz zero counts, add-in an empty counter:
    #       c += Counter()

    def __add__(self, other):
        '''Add counts z two counters.

        >>> Counter('abbb') + Counter('bcc')
        Counter({'b': 4, 'c': 2, 'a': 1})

        '''
        jeżeli nie isinstance(other, Counter):
            zwróć NotImplemented
        result = Counter()
        dla elem, count w self.items():
            newcount = count + other[elem]
            jeżeli newcount > 0:
                result[elem] = newcount
        dla elem, count w other.items():
            jeżeli elem nie w self oraz count > 0:
                result[elem] = count
        zwróć result

    def __sub__(self, other):
        ''' Subtract count, but keep only results przy positive counts.

        >>> Counter('abbbc') - Counter('bccd')
        Counter({'b': 2, 'a': 1})

        '''
        jeżeli nie isinstance(other, Counter):
            zwróć NotImplemented
        result = Counter()
        dla elem, count w self.items():
            newcount = count - other[elem]
            jeżeli newcount > 0:
                result[elem] = newcount
        dla elem, count w other.items():
            jeżeli elem nie w self oraz count < 0:
                result[elem] = 0 - count
        zwróć result

    def __or__(self, other):
        '''Union jest the maximum of value w either of the input counters.

        >>> Counter('abbb') | Counter('bcc')
        Counter({'b': 3, 'c': 2, 'a': 1})

        '''
        jeżeli nie isinstance(other, Counter):
            zwróć NotImplemented
        result = Counter()
        dla elem, count w self.items():
            other_count = other[elem]
            newcount = other_count jeżeli count < other_count inaczej count
            jeżeli newcount > 0:
                result[elem] = newcount
        dla elem, count w other.items():
            jeżeli elem nie w self oraz count > 0:
                result[elem] = count
        zwróć result

    def __and__(self, other):
        ''' Intersection jest the minimum of corresponding counts.

        >>> Counter('abbb') & Counter('bcc')
        Counter({'b': 1})

        '''
        jeżeli nie isinstance(other, Counter):
            zwróć NotImplemented
        result = Counter()
        dla elem, count w self.items():
            other_count = other[elem]
            newcount = count jeżeli count < other_count inaczej other_count
            jeżeli newcount > 0:
                result[elem] = newcount
        zwróć result

    def __pos__(self):
        'Adds an empty counter, effectively stripping negative oraz zero counts'
        result = Counter()
        dla elem, count w self.items():
            jeżeli count > 0:
                result[elem] = count
        zwróć result

    def __neg__(self):
        '''Subtracts z an empty counter.  Strips positive oraz zero counts,
        oraz flips the sign on negative counts.

        '''
        result = Counter()
        dla elem, count w self.items():
            jeżeli count < 0:
                result[elem] = 0 - count
        zwróć result

    def _keep_positive(self):
        '''Internal method to strip elements przy a negative albo zero count'''
        nonpositive = [elem dla elem, count w self.items() jeżeli nie count > 0]
        dla elem w nonpositive:
            usuń self[elem]
        zwróć self

    def __iadd__(self, other):
        '''Inplace add z another counter, keeping only positive counts.

        >>> c = Counter('abbb')
        >>> c += Counter('bcc')
        >>> c
        Counter({'b': 4, 'c': 2, 'a': 1})

        '''
        dla elem, count w other.items():
            self[elem] += count
        zwróć self._keep_positive()

    def __isub__(self, other):
        '''Inplace subtract counter, but keep only results przy positive counts.

        >>> c = Counter('abbbc')
        >>> c -= Counter('bccd')
        >>> c
        Counter({'b': 2, 'a': 1})

        '''
        dla elem, count w other.items():
            self[elem] -= count
        zwróć self._keep_positive()

    def __ior__(self, other):
        '''Inplace union jest the maximum of value z either counter.

        >>> c = Counter('abbb')
        >>> c |= Counter('bcc')
        >>> c
        Counter({'b': 3, 'c': 2, 'a': 1})

        '''
        dla elem, other_count w other.items():
            count = self[elem]
            jeżeli other_count > count:
                self[elem] = other_count
        zwróć self._keep_positive()

    def __iand__(self, other):
        '''Inplace intersection jest the minimum of corresponding counts.

        >>> c = Counter('abbb')
        >>> c &= Counter('bcc')
        >>> c
        Counter({'b': 1})

        '''
        dla elem, count w self.items():
            other_count = other[elem]
            jeżeli other_count < count:
                self[elem] = other_count
        zwróć self._keep_positive()


########################################################################
###  ChainMap (helper dla configparser oraz string.Template)
########################################################################

klasa ChainMap(MutableMapping):
    ''' A ChainMap groups multiple dicts (or other mappings) together
    to create a single, updateable view.

    The underlying mappings are stored w a list.  That list jest public oraz can
    accessed albo updated using the *maps* attribute.  There jest no other state.

    Lookups search the underlying mappings successively until a key jest found.
    In contrast, writes, updates, oraz deletions only operate on the first
    mapping.

    '''

    def __init__(self, *maps):
        '''Initialize a ChainMap by setting *maps* to the given mappings.
        If no mappings are provided, a single empty dictionary jest used.

        '''
        self.maps = list(maps) albo [{}]          # always at least one map

    def __missing__(self, key):
        podnieś KeyError(key)

    def __getitem__(self, key):
        dla mapping w self.maps:
            spróbuj:
                zwróć mapping[key]             # can't use 'key w mapping' przy defaultdict
            wyjąwszy KeyError:
                dalej
        zwróć self.__missing__(key)            # support subclasses that define __missing__

    def get(self, key, default=Nic):
        zwróć self[key] jeżeli key w self inaczej default

    def __len__(self):
        zwróć len(set().union(*self.maps))     # reuses stored hash values jeżeli possible

    def __iter__(self):
        zwróć iter(set().union(*self.maps))

    def __contains__(self, key):
        zwróć any(key w m dla m w self.maps)

    def __bool__(self):
        zwróć any(self.maps)

    @_recursive_repr()
    def __repr__(self):
        zwróć '{0.__class__.__name__}({1})'.format(
            self, ', '.join(map(repr, self.maps)))

    @classmethod
    def fromkeys(cls, iterable, *args):
        'Create a ChainMap przy a single dict created z the iterable.'
        zwróć cls(dict.fromkeys(iterable, *args))

    def copy(self):
        'New ChainMap albo subclass przy a new copy of maps[0] oraz refs to maps[1:]'
        zwróć self.__class__(self.maps[0].copy(), *self.maps[1:])

    __copy__ = copy

    def new_child(self, m=Nic):                # like Django's Context.push()
        '''
        New ChainMap przy a new map followed by all previous maps. If no
        map jest provided, an empty dict jest used.
        '''
        jeżeli m jest Nic:
            m = {}
        zwróć self.__class__(m, *self.maps)

    @property
    def parents(self):                          # like Django's Context.pop()
        'New ChainMap z maps[1:].'
        zwróć self.__class__(*self.maps[1:])

    def __setitem__(self, key, value):
        self.maps[0][key] = value

    def __delitem__(self, key):
        spróbuj:
            usuń self.maps[0][key]
        wyjąwszy KeyError:
            podnieś KeyError('Key nie found w the first mapping: {!r}'.format(key))

    def popitem(self):
        'Remove oraz zwróć an item pair z maps[0]. Raise KeyError jest maps[0] jest empty.'
        spróbuj:
            zwróć self.maps[0].popitem()
        wyjąwszy KeyError:
            podnieś KeyError('No keys found w the first mapping.')

    def pop(self, key, *args):
        'Remove *key* z maps[0] oraz zwróć its value. Raise KeyError jeżeli *key* nie w maps[0].'
        spróbuj:
            zwróć self.maps[0].pop(key, *args)
        wyjąwszy KeyError:
            podnieś KeyError('Key nie found w the first mapping: {!r}'.format(key))

    def clear(self):
        'Clear maps[0], leaving maps[1:] intact.'
        self.maps[0].clear()


################################################################################
### UserDict
################################################################################

klasa UserDict(MutableMapping):

    # Start by filling-out the abstract methods
    def __init__(self, dict=Nic, **kwargs):
        self.data = {}
        jeżeli dict jest nie Nic:
            self.update(dict)
        jeżeli len(kwargs):
            self.update(kwargs)
    def __len__(self): zwróć len(self.data)
    def __getitem__(self, key):
        jeżeli key w self.data:
            zwróć self.data[key]
        jeżeli hasattr(self.__class__, "__missing__"):
            zwróć self.__class__.__missing__(self, key)
        podnieś KeyError(key)
    def __setitem__(self, key, item): self.data[key] = item
    def __delitem__(self, key): usuń self.data[key]
    def __iter__(self):
        zwróć iter(self.data)

    # Modify __contains__ to work correctly when __missing__ jest present
    def __contains__(self, key):
        zwróć key w self.data

    # Now, add the methods w dicts but nie w MutableMapping
    def __repr__(self): zwróć repr(self.data)
    def copy(self):
        jeżeli self.__class__ jest UserDict:
            zwróć UserDict(self.data.copy())
        zaimportuj copy
        data = self.data
        spróbuj:
            self.data = {}
            c = copy.copy(self)
        w_końcu:
            self.data = data
        c.update(self)
        zwróć c
    @classmethod
    def fromkeys(cls, iterable, value=Nic):
        d = cls()
        dla key w iterable:
            d[key] = value
        zwróć d



################################################################################
### UserList
################################################################################

klasa UserList(MutableSequence):
    """A more albo less complete user-defined wrapper around list objects."""
    def __init__(self, initlist=Nic):
        self.data = []
        jeżeli initlist jest nie Nic:
            # XXX should this accept an arbitrary sequence?
            jeżeli type(initlist) == type(self.data):
                self.data[:] = initlist
            albo_inaczej isinstance(initlist, UserList):
                self.data[:] = initlist.data[:]
            inaczej:
                self.data = list(initlist)
    def __repr__(self): zwróć repr(self.data)
    def __lt__(self, other): zwróć self.data <  self.__cast(other)
    def __le__(self, other): zwróć self.data <= self.__cast(other)
    def __eq__(self, other): zwróć self.data == self.__cast(other)
    def __gt__(self, other): zwróć self.data >  self.__cast(other)
    def __ge__(self, other): zwróć self.data >= self.__cast(other)
    def __cast(self, other):
        zwróć other.data jeżeli isinstance(other, UserList) inaczej other
    def __contains__(self, item): zwróć item w self.data
    def __len__(self): zwróć len(self.data)
    def __getitem__(self, i): zwróć self.data[i]
    def __setitem__(self, i, item): self.data[i] = item
    def __delitem__(self, i): usuń self.data[i]
    def __add__(self, other):
        jeżeli isinstance(other, UserList):
            zwróć self.__class__(self.data + other.data)
        albo_inaczej isinstance(other, type(self.data)):
            zwróć self.__class__(self.data + other)
        zwróć self.__class__(self.data + list(other))
    def __radd__(self, other):
        jeżeli isinstance(other, UserList):
            zwróć self.__class__(other.data + self.data)
        albo_inaczej isinstance(other, type(self.data)):
            zwróć self.__class__(other + self.data)
        zwróć self.__class__(list(other) + self.data)
    def __iadd__(self, other):
        jeżeli isinstance(other, UserList):
            self.data += other.data
        albo_inaczej isinstance(other, type(self.data)):
            self.data += other
        inaczej:
            self.data += list(other)
        zwróć self
    def __mul__(self, n):
        zwróć self.__class__(self.data*n)
    __rmul__ = __mul__
    def __imul__(self, n):
        self.data *= n
        zwróć self
    def append(self, item): self.data.append(item)
    def insert(self, i, item): self.data.insert(i, item)
    def pop(self, i=-1): zwróć self.data.pop(i)
    def remove(self, item): self.data.remove(item)
    def clear(self): self.data.clear()
    def copy(self): zwróć self.__class__(self)
    def count(self, item): zwróć self.data.count(item)
    def index(self, item, *args): zwróć self.data.index(item, *args)
    def reverse(self): self.data.reverse()
    def sort(self, *args, **kwds): self.data.sort(*args, **kwds)
    def extend(self, other):
        jeżeli isinstance(other, UserList):
            self.data.extend(other.data)
        inaczej:
            self.data.extend(other)



################################################################################
### UserString
################################################################################

klasa UserString(Sequence):
    def __init__(self, seq):
        jeżeli isinstance(seq, str):
            self.data = seq
        albo_inaczej isinstance(seq, UserString):
            self.data = seq.data[:]
        inaczej:
            self.data = str(seq)
    def __str__(self): zwróć str(self.data)
    def __repr__(self): zwróć repr(self.data)
    def __int__(self): zwróć int(self.data)
    def __float__(self): zwróć float(self.data)
    def __complex__(self): zwróć complex(self.data)
    def __hash__(self): zwróć hash(self.data)
    def __getnewargs__(self):
        zwróć (self.data[:],)

    def __eq__(self, string):
        jeżeli isinstance(string, UserString):
            zwróć self.data == string.data
        zwróć self.data == string
    def __lt__(self, string):
        jeżeli isinstance(string, UserString):
            zwróć self.data < string.data
        zwróć self.data < string
    def __le__(self, string):
        jeżeli isinstance(string, UserString):
            zwróć self.data <= string.data
        zwróć self.data <= string
    def __gt__(self, string):
        jeżeli isinstance(string, UserString):
            zwróć self.data > string.data
        zwróć self.data > string
    def __ge__(self, string):
        jeżeli isinstance(string, UserString):
            zwróć self.data >= string.data
        zwróć self.data >= string

    def __contains__(self, char):
        jeżeli isinstance(char, UserString):
            char = char.data
        zwróć char w self.data

    def __len__(self): zwróć len(self.data)
    def __getitem__(self, index): zwróć self.__class__(self.data[index])
    def __add__(self, other):
        jeżeli isinstance(other, UserString):
            zwróć self.__class__(self.data + other.data)
        albo_inaczej isinstance(other, str):
            zwróć self.__class__(self.data + other)
        zwróć self.__class__(self.data + str(other))
    def __radd__(self, other):
        jeżeli isinstance(other, str):
            zwróć self.__class__(other + self.data)
        zwróć self.__class__(str(other) + self.data)
    def __mul__(self, n):
        zwróć self.__class__(self.data*n)
    __rmul__ = __mul__
    def __mod__(self, args):
        zwróć self.__class__(self.data % args)
    def __rmod__(self, format):
        zwróć self.__class__(format % args)

    # the following methods are defined w alphabetical order:
    def capitalize(self): zwróć self.__class__(self.data.capitalize())
    def casefold(self):
        zwróć self.__class__(self.data.casefold())
    def center(self, width, *args):
        zwróć self.__class__(self.data.center(width, *args))
    def count(self, sub, start=0, end=_sys.maxsize):
        jeżeli isinstance(sub, UserString):
            sub = sub.data
        zwróć self.data.count(sub, start, end)
    def encode(self, encoding=Nic, errors=Nic): # XXX improve this?
        jeżeli encoding:
            jeżeli errors:
                zwróć self.__class__(self.data.encode(encoding, errors))
            zwróć self.__class__(self.data.encode(encoding))
        zwróć self.__class__(self.data.encode())
    def endswith(self, suffix, start=0, end=_sys.maxsize):
        zwróć self.data.endswith(suffix, start, end)
    def expandtabs(self, tabsize=8):
        zwróć self.__class__(self.data.expandtabs(tabsize))
    def find(self, sub, start=0, end=_sys.maxsize):
        jeżeli isinstance(sub, UserString):
            sub = sub.data
        zwróć self.data.find(sub, start, end)
    def format(self, *args, **kwds):
        zwróć self.data.format(*args, **kwds)
    def format_map(self, mapping):
        zwróć self.data.format_map(mapping)
    def index(self, sub, start=0, end=_sys.maxsize):
        zwróć self.data.index(sub, start, end)
    def isalpha(self): zwróć self.data.isalpha()
    def isalnum(self): zwróć self.data.isalnum()
    def isdecimal(self): zwróć self.data.isdecimal()
    def isdigit(self): zwróć self.data.isdigit()
    def isidentifier(self): zwróć self.data.isidentifier()
    def islower(self): zwróć self.data.islower()
    def isnumeric(self): zwróć self.data.isnumeric()
    def isprintable(self): zwróć self.data.isprintable()
    def isspace(self): zwróć self.data.isspace()
    def istitle(self): zwróć self.data.istitle()
    def isupper(self): zwróć self.data.isupper()
    def join(self, seq): zwróć self.data.join(seq)
    def ljust(self, width, *args):
        zwróć self.__class__(self.data.ljust(width, *args))
    def lower(self): zwróć self.__class__(self.data.lower())
    def lstrip(self, chars=Nic): zwróć self.__class__(self.data.lstrip(chars))
    maketrans = str.maketrans
    def partition(self, sep):
        zwróć self.data.partition(sep)
    def replace(self, old, new, maxsplit=-1):
        jeżeli isinstance(old, UserString):
            old = old.data
        jeżeli isinstance(new, UserString):
            new = new.data
        zwróć self.__class__(self.data.replace(old, new, maxsplit))
    def rfind(self, sub, start=0, end=_sys.maxsize):
        jeżeli isinstance(sub, UserString):
            sub = sub.data
        zwróć self.data.rfind(sub, start, end)
    def rindex(self, sub, start=0, end=_sys.maxsize):
        zwróć self.data.rindex(sub, start, end)
    def rjust(self, width, *args):
        zwróć self.__class__(self.data.rjust(width, *args))
    def rpartition(self, sep):
        zwróć self.data.rpartition(sep)
    def rstrip(self, chars=Nic):
        zwróć self.__class__(self.data.rstrip(chars))
    def split(self, sep=Nic, maxsplit=-1):
        zwróć self.data.split(sep, maxsplit)
    def rsplit(self, sep=Nic, maxsplit=-1):
        zwróć self.data.rsplit(sep, maxsplit)
    def splitlines(self, keepends=Nieprawda): zwróć self.data.splitlines(keepends)
    def startswith(self, prefix, start=0, end=_sys.maxsize):
        zwróć self.data.startswith(prefix, start, end)
    def strip(self, chars=Nic): zwróć self.__class__(self.data.strip(chars))
    def swapcase(self): zwróć self.__class__(self.data.swapcase())
    def title(self): zwróć self.__class__(self.data.title())
    def translate(self, *args):
        zwróć self.__class__(self.data.translate(*args))
    def upper(self): zwróć self.__class__(self.data.upper())
    def zfill(self, width): zwróć self.__class__(self.data.zfill(width))
