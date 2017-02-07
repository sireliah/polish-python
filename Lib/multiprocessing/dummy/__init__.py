#
# Support dla the API of the multiprocessing package using threads
#
# multiprocessing/dummy/__init__.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

__all__ = [
    'Process', 'current_process', 'active_children', 'freeze_support',
    'Lock', 'RLock', 'Semaphore', 'BoundedSemaphore', 'Condition',
    'Event', 'Barrier', 'Queue', 'Manager', 'Pipe', 'Pool', 'JoinableQueue'
    ]

#
# Imports
#

zaimportuj threading
zaimportuj sys
zaimportuj weakref
zaimportuj array

z .connection zaimportuj Pipe
z threading zaimportuj Lock, RLock, Semaphore, BoundedSemaphore
z threading zaimportuj Event, Condition, Barrier
z queue zaimportuj Queue

#
#
#

klasa DummyProcess(threading.Thread):

    def __init__(self, group=Nic, target=Nic, name=Nic, args=(), kwargs={}):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._pid = Nic
        self._children = weakref.WeakKeyDictionary()
        self._start_called = Nieprawda
        self._parent = current_process()

    def start(self):
        assert self._parent jest current_process()
        self._start_called = Prawda
        jeżeli hasattr(self._parent, '_children'):
            self._parent._children[self] = Nic
        threading.Thread.start(self)

    @property
    def exitcode(self):
        jeżeli self._start_called oraz nie self.is_alive():
            zwróć 0
        inaczej:
            zwróć Nic

#
#
#

Process = DummyProcess
current_process = threading.current_thread
current_process()._children = weakref.WeakKeyDictionary()

def active_children():
    children = current_process()._children
    dla p w list(children):
        jeżeli nie p.is_alive():
            children.pop(p, Nic)
    zwróć list(children)

def freeze_support():
    dalej

#
#
#

klasa Namespace(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)
    def __repr__(self):
        items = list(self.__dict__.items())
        temp = []
        dla name, value w items:
            jeżeli nie name.startswith('_'):
                temp.append('%s=%r' % (name, value))
        temp.sort()
        zwróć '%s(%s)' % (self.__class__.__name__, ', '.join(temp))

dict = dict
list = list

def Array(typecode, sequence, lock=Prawda):
    zwróć array.array(typecode, sequence)

klasa Value(object):
    def __init__(self, typecode, value, lock=Prawda):
        self._typecode = typecode
        self._value = value
    def _get(self):
        zwróć self._value
    def _set(self, value):
        self._value = value
    value = property(_get, _set)
    def __repr__(self):
        zwróć '<%s(%r, %r)>'%(type(self).__name__,self._typecode,self._value)

def Manager():
    zwróć sys.modules[__name__]

def shutdown():
    dalej

def Pool(processes=Nic, initializer=Nic, initargs=()):
    z ..pool zaimportuj ThreadPool
    zwróć ThreadPool(processes, initializer, initargs)

JoinableQueue = Queue
