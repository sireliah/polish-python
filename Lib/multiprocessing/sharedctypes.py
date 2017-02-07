#
# Module which supports allocation of ctypes objects z shared memory
#
# multiprocessing/sharedctypes.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

zaimportuj ctypes
zaimportuj weakref

z . zaimportuj heap
z . zaimportuj get_context

z .context zaimportuj assert_spawning
z .reduction zaimportuj ForkingPickler

__all__ = ['RawValue', 'RawArray', 'Value', 'Array', 'copy', 'synchronized']

#
#
#

typecode_to_type = {
    'c': ctypes.c_char,  'u': ctypes.c_wchar,
    'b': ctypes.c_byte,  'B': ctypes.c_ubyte,
    'h': ctypes.c_short, 'H': ctypes.c_ushort,
    'i': ctypes.c_int,   'I': ctypes.c_uint,
    'l': ctypes.c_long,  'L': ctypes.c_ulong,
    'f': ctypes.c_float, 'd': ctypes.c_double
    }

#
#
#

def _new_value(type_):
    size = ctypes.sizeof(type_)
    wrapper = heap.BufferWrapper(size)
    zwróć rebuild_ctype(type_, wrapper, Nic)

def RawValue(typecode_or_type, *args):
    '''
    Returns a ctypes object allocated z shared memory
    '''
    type_ = typecode_to_type.get(typecode_or_type, typecode_or_type)
    obj = _new_value(type_)
    ctypes.memset(ctypes.addressof(obj), 0, ctypes.sizeof(obj))
    obj.__init__(*args)
    zwróć obj

def RawArray(typecode_or_type, size_or_initializer):
    '''
    Returns a ctypes array allocated z shared memory
    '''
    type_ = typecode_to_type.get(typecode_or_type, typecode_or_type)
    jeżeli isinstance(size_or_initializer, int):
        type_ = type_ * size_or_initializer
        obj = _new_value(type_)
        ctypes.memset(ctypes.addressof(obj), 0, ctypes.sizeof(obj))
        zwróć obj
    inaczej:
        type_ = type_ * len(size_or_initializer)
        result = _new_value(type_)
        result.__init__(*size_or_initializer)
        zwróć result

def Value(typecode_or_type, *args, lock=Prawda, ctx=Nic):
    '''
    Return a synchronization wrapper dla a Value
    '''
    obj = RawValue(typecode_or_type, *args)
    jeżeli lock jest Nieprawda:
        zwróć obj
    jeżeli lock w (Prawda, Nic):
        ctx = ctx albo get_context()
        lock = ctx.RLock()
    jeżeli nie hasattr(lock, 'acquire'):
        podnieś AttributeError("'%r' has no method 'acquire'" % lock)
    zwróć synchronized(obj, lock, ctx=ctx)

def Array(typecode_or_type, size_or_initializer, *, lock=Prawda, ctx=Nic):
    '''
    Return a synchronization wrapper dla a RawArray
    '''
    obj = RawArray(typecode_or_type, size_or_initializer)
    jeżeli lock jest Nieprawda:
        zwróć obj
    jeżeli lock w (Prawda, Nic):
        ctx = ctx albo get_context()
        lock = ctx.RLock()
    jeżeli nie hasattr(lock, 'acquire'):
        podnieś AttributeError("'%r' has no method 'acquire'" % lock)
    zwróć synchronized(obj, lock, ctx=ctx)

def copy(obj):
    new_obj = _new_value(type(obj))
    ctypes.pointer(new_obj)[0] = obj
    zwróć new_obj

def synchronized(obj, lock=Nic, ctx=Nic):
    assert nie isinstance(obj, SynchronizedBase), 'object already synchronized'
    ctx = ctx albo get_context()

    jeżeli isinstance(obj, ctypes._SimpleCData):
        zwróć Synchronized(obj, lock, ctx)
    albo_inaczej isinstance(obj, ctypes.Array):
        jeżeli obj._type_ jest ctypes.c_char:
            zwróć SynchronizedString(obj, lock, ctx)
        zwróć SynchronizedArray(obj, lock, ctx)
    inaczej:
        cls = type(obj)
        spróbuj:
            scls = class_cache[cls]
        wyjąwszy KeyError:
            names = [field[0] dla field w cls._fields_]
            d = dict((name, make_property(name)) dla name w names)
            classname = 'Synchronized' + cls.__name__
            scls = class_cache[cls] = type(classname, (SynchronizedBase,), d)
        zwróć scls(obj, lock, ctx)

#
# Functions dla pickling/unpickling
#

def reduce_ctype(obj):
    assert_spawning(obj)
    jeżeli isinstance(obj, ctypes.Array):
        zwróć rebuild_ctype, (obj._type_, obj._wrapper, obj._length_)
    inaczej:
        zwróć rebuild_ctype, (type(obj), obj._wrapper, Nic)

def rebuild_ctype(type_, wrapper, length):
    jeżeli length jest nie Nic:
        type_ = type_ * length
    ForkingPickler.register(type_, reduce_ctype)
    buf = wrapper.create_memoryview()
    obj = type_.from_buffer(buf)
    obj._wrapper = wrapper
    zwróć obj

#
# Function to create properties
#

def make_property(name):
    spróbuj:
        zwróć prop_cache[name]
    wyjąwszy KeyError:
        d = {}
        exec(template % ((name,)*7), d)
        prop_cache[name] = d[name]
        zwróć d[name]

template = '''
def get%s(self):
    self.acquire()
    spróbuj:
        zwróć self._obj.%s
    w_końcu:
        self.release()
def set%s(self, value):
    self.acquire()
    spróbuj:
        self._obj.%s = value
    w_końcu:
        self.release()
%s = property(get%s, set%s)
'''

prop_cache = {}
class_cache = weakref.WeakKeyDictionary()

#
# Synchronized wrappers
#

klasa SynchronizedBase(object):

    def __init__(self, obj, lock=Nic, ctx=Nic):
        self._obj = obj
        jeżeli lock:
            self._lock = lock
        inaczej:
            ctx = ctx albo get_context(force=Prawda)
            self._lock = ctx.RLock()
        self.acquire = self._lock.acquire
        self.release = self._lock.release

    def __enter__(self):
        zwróć self._lock.__enter__()

    def __exit__(self, *args):
        zwróć self._lock.__exit__(*args)

    def __reduce__(self):
        assert_spawning(self)
        zwróć synchronized, (self._obj, self._lock)

    def get_obj(self):
        zwróć self._obj

    def get_lock(self):
        zwróć self._lock

    def __repr__(self):
        zwróć '<%s wrapper dla %s>' % (type(self).__name__, self._obj)


klasa Synchronized(SynchronizedBase):
    value = make_property('value')


klasa SynchronizedArray(SynchronizedBase):

    def __len__(self):
        zwróć len(self._obj)

    def __getitem__(self, i):
        przy self:
            zwróć self._obj[i]

    def __setitem__(self, i, value):
        przy self:
            self._obj[i] = value

    def __getslice__(self, start, stop):
        przy self:
            zwróć self._obj[start:stop]

    def __setslice__(self, start, stop, values):
        przy self:
            self._obj[start:stop] = values


klasa SynchronizedString(SynchronizedArray):
    value = make_property('value')
    raw = make_property('raw')
