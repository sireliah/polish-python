"""Manage shelves of pickled objects.

A "shelf" jest a persistent, dictionary-like object.  The difference
przy dbm databases jest that the values (nie the keys!) w a shelf can
be essentially arbitrary Python objects -- anything that the "pickle"
module can handle.  This includes most klasa instances, recursive data
types, oraz objects containing lots of shared sub-objects.  The keys
are ordinary strings.

To summarize the interface (key jest a string, data jest an arbitrary
object):

        zaimportuj shelve
        d = shelve.open(filename) # open, przy (g)dbm filename -- no suffix

        d[key] = data   # store data at key (overwrites old data if
                        # using an existing key)
        data = d[key]   # retrieve a COPY of the data at key (raise
                        # KeyError jeżeli no such key) -- NOTE that this
                        # access returns a *copy* of the entry!
        usuń d[key]      # delete data stored at key (raises KeyError
                        # jeżeli no such key)
        flag = key w d # true jeżeli the key exists
        list = d.keys() # a list of all existing keys (slow!)

        d.close()       # close it

Dependent on the implementation, closing a persistent dictionary may
or may nie be necessary to flush changes to disk.

Normally, d[key] returns a COPY of the entry.  This needs care when
mutable entries are mutated: dla example, jeżeli d[key] jest a list,
        d[key].append(anitem)
does NOT modify the entry d[key] itself, jako stored w the persistent
mapping -- it only modifies the copy, which jest then immediately
discarded, so that the append has NO effect whatsoever.  To append an
item to d[key] w a way that will affect the persistent mapping, use:
        data = d[key]
        data.append(anitem)
        d[key] = data

To avoid the problem przy mutable entries, you may dalej the keyword
argument writeback=Prawda w the call to shelve.open.  When you use:
        d = shelve.open(filename, writeback=Prawda)
then d keeps a cache of all entries you access, oraz writes them all back
to the persistent mapping when you call d.close().  This ensures that
such usage jako d[key].append(anitem) works jako intended.

However, using keyword argument writeback=Prawda may consume vast amount
of memory dla the cache, oraz it may make d.close() very slow, jeżeli you
access many of d's entries after opening it w this way: d has no way to
check which of the entries you access are mutable and/or which ones you
actually mutate, so it must cache, oraz write back at close, all of the
entries that you access.  You can call d.sync() to write back all the
entries w the cache, oraz empty the cache (d.sync() also synchronizes
the persistent dictionary on disk, jeżeli feasible).
"""

z pickle zaimportuj Pickler, Unpickler
z io zaimportuj BytesIO

zaimportuj collections

__all__ = ["Shelf", "BsdDbShelf", "DbfilenameShelf", "open"]

klasa _ClosedDict(collections.MutableMapping):
    'Marker dla a closed dict.  Access attempts podnieś a ValueError.'

    def closed(self, *args):
        podnieś ValueError('invalid operation on closed shelf')
    __iter__ = __len__ = __getitem__ = __setitem__ = __delitem__ = keys = closed

    def __repr__(self):
        zwróć '<Closed Dictionary>'


klasa Shelf(collections.MutableMapping):
    """Base klasa dla shelf implementations.

    This jest initialized przy a dictionary-like object.
    See the module's __doc__ string dla an overview of the interface.
    """

    def __init__(self, dict, protocol=Nic, writeback=Nieprawda,
                 keyencoding="utf-8"):
        self.dict = dict
        jeżeli protocol jest Nic:
            protocol = 3
        self._protocol = protocol
        self.writeback = writeback
        self.cache = {}
        self.keyencoding = keyencoding

    def __iter__(self):
        dla k w self.dict.keys():
            uzyskaj k.decode(self.keyencoding)

    def __len__(self):
        zwróć len(self.dict)

    def __contains__(self, key):
        zwróć key.encode(self.keyencoding) w self.dict

    def get(self, key, default=Nic):
        jeżeli key.encode(self.keyencoding) w self.dict:
            zwróć self[key]
        zwróć default

    def __getitem__(self, key):
        spróbuj:
            value = self.cache[key]
        wyjąwszy KeyError:
            f = BytesIO(self.dict[key.encode(self.keyencoding)])
            value = Unpickler(f).load()
            jeżeli self.writeback:
                self.cache[key] = value
        zwróć value

    def __setitem__(self, key, value):
        jeżeli self.writeback:
            self.cache[key] = value
        f = BytesIO()
        p = Pickler(f, self._protocol)
        p.dump(value)
        self.dict[key.encode(self.keyencoding)] = f.getvalue()

    def __delitem__(self, key):
        usuń self.dict[key.encode(self.keyencoding)]
        spróbuj:
            usuń self.cache[key]
        wyjąwszy KeyError:
            dalej

    def __enter__(self):
        zwróć self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        jeżeli self.dict jest Nic:
            zwróć
        spróbuj:
            self.sync()
            spróbuj:
                self.dict.close()
            wyjąwszy AttributeError:
                dalej
        w_końcu:
            # Catch errors that may happen when close jest called z __del__
            # because CPython jest w interpreter shutdown.
            spróbuj:
                self.dict = _ClosedDict()
            wyjąwszy:
                self.dict = Nic

    def __del__(self):
        jeżeli nie hasattr(self, 'writeback'):
            # __init__ didn't succeed, so don't bother closing
            # see http://bugs.python.org/issue1339007 dla details
            zwróć
        self.close()

    def sync(self):
        jeżeli self.writeback oraz self.cache:
            self.writeback = Nieprawda
            dla key, entry w self.cache.items():
                self[key] = entry
            self.writeback = Prawda
            self.cache = {}
        jeżeli hasattr(self.dict, 'sync'):
            self.dict.sync()


klasa BsdDbShelf(Shelf):
    """Shelf implementation using the "BSD" db interface.

    This adds methods first(), next(), previous(), last() oraz
    set_location() that have no counterpart w [g]dbm databases.

    The actual database must be opened using one of the "bsddb"
    modules "open" routines (i.e. bsddb.hashopen, bsddb.btopen albo
    bsddb.rnopen) oraz dalejed to the constructor.

    See the module's __doc__ string dla an overview of the interface.
    """

    def __init__(self, dict, protocol=Nic, writeback=Nieprawda,
                 keyencoding="utf-8"):
        Shelf.__init__(self, dict, protocol, writeback, keyencoding)

    def set_location(self, key):
        (key, value) = self.dict.set_location(key)
        f = BytesIO(value)
        zwróć (key.decode(self.keyencoding), Unpickler(f).load())

    def next(self):
        (key, value) = next(self.dict)
        f = BytesIO(value)
        zwróć (key.decode(self.keyencoding), Unpickler(f).load())

    def previous(self):
        (key, value) = self.dict.previous()
        f = BytesIO(value)
        zwróć (key.decode(self.keyencoding), Unpickler(f).load())

    def first(self):
        (key, value) = self.dict.first()
        f = BytesIO(value)
        zwróć (key.decode(self.keyencoding), Unpickler(f).load())

    def last(self):
        (key, value) = self.dict.last()
        f = BytesIO(value)
        zwróć (key.decode(self.keyencoding), Unpickler(f).load())


klasa DbfilenameShelf(Shelf):
    """Shelf implementation using the "dbm" generic dbm interface.

    This jest initialized przy the filename dla the dbm database.
    See the module's __doc__ string dla an overview of the interface.
    """

    def __init__(self, filename, flag='c', protocol=Nic, writeback=Nieprawda):
        zaimportuj dbm
        Shelf.__init__(self, dbm.open(filename, flag), protocol, writeback)


def open(filename, flag='c', protocol=Nic, writeback=Nieprawda):
    """Open a persistent dictionary dla reading oraz writing.

    The filename parameter jest the base filename dla the underlying
    database.  As a side-effect, an extension may be added to the
    filename oraz more than one file may be created.  The optional flag
    parameter has the same interpretation jako the flag parameter of
    dbm.open(). The optional protocol parameter specifies the
    version of the pickle protocol (0, 1, albo 2).

    See the module's __doc__ string dla an overview of the interface.
    """

    zwróć DbfilenameShelf(filename, flag, protocol, writeback)
