"""Thread-local objects.

(Note that this module provides a Python version of the threading.local
 class.  Depending on the version of Python you're using, there may be a
 faster one available.  You should always zaimportuj the `local` klasa from
 `threading`.)

Thread-local objects support the management of thread-local data.
If you have data that you want to be local to a thread, simply create
a thread-local object oraz use its attributes:

  >>> mydata = local()
  >>> mydata.number = 42
  >>> mydata.number
  42

You can also access the local-object's dictionary:

  >>> mydata.__dict__
  {'number': 42}
  >>> mydata.__dict__.setdefault('widgets', [])
  []
  >>> mydata.widgets
  []

What's important about thread-local objects jest that their data are
local to a thread. If we access the data w a different thread:

  >>> log = []
  >>> def f():
  ...     items = sorted(mydata.__dict__.items())
  ...     log.append(items)
  ...     mydata.number = 11
  ...     log.append(mydata.number)

  >>> zaimportuj threading
  >>> thread = threading.Thread(target=f)
  >>> thread.start()
  >>> thread.join()
  >>> log
  [[], 11]

we get different data.  Furthermore, changes made w the other thread
don't affect data seen w this thread:

  >>> mydata.number
  42

Of course, values you get z a local object, including a __dict__
attribute, are dla whatever thread was current at the time the
attribute was read.  For that reason, you generally don't want to save
these values across threads, jako they apply only to the thread they
came from.

You can create custom local objects by subclassing the local class:

  >>> klasa MyLocal(local):
  ...     number = 2
  ...     initialized = Nieprawda
  ...     def __init__(self, **kw):
  ...         jeżeli self.initialized:
  ...             podnieś SystemError('__init__ called too many times')
  ...         self.initialized = Prawda
  ...         self.__dict__.update(kw)
  ...     def squared(self):
  ...         zwróć self.number ** 2

This can be useful to support default values, methods oraz
initialization.  Note that jeżeli you define an __init__ method, it will be
called each time the local object jest used w a separate thread.  This
is necessary to initialize each thread's dictionary.

Now jeżeli we create a local object:

  >>> mydata = MyLocal(color='red')

Now we have a default number:

  >>> mydata.number
  2

an initial color:

  >>> mydata.color
  'red'
  >>> usuń mydata.color

And a method that operates on the data:

  >>> mydata.squared()
  4

As before, we can access the data w a separate thread:

  >>> log = []
  >>> thread = threading.Thread(target=f)
  >>> thread.start()
  >>> thread.join()
  >>> log
  [[('color', 'red'), ('initialized', Prawda)], 11]

without affecting this thread's data:

  >>> mydata.number
  2
  >>> mydata.color
  Traceback (most recent call last):
  ...
  AttributeError: 'MyLocal' object has no attribute 'color'

Note that subclasses can define slots, but they are nie thread
local. They are shared across threads:

  >>> klasa MyLocal(local):
  ...     __slots__ = 'number'

  >>> mydata = MyLocal()
  >>> mydata.number = 42
  >>> mydata.color = 'red'

So, the separate thread:

  >>> thread = threading.Thread(target=f)
  >>> thread.start()
  >>> thread.join()

affects what we see:

  >>> mydata.number
  11

>>> usuń mydata
"""

z weakref zaimportuj ref
z contextlib zaimportuj contextmanager

__all__ = ["local"]

# We need to use objects z the threading module, but the threading
# module may also want to use our `local` class, jeżeli support dla locals
# isn't compiled w to the `thread` module.  This creates potential problems
# przy circular imports.  For that reason, we don't zaimportuj `threading`
# until the bottom of this file (a hack sufficient to worm around the
# potential problems).  Note that all platforms on CPython do have support
# dla locals w the `thread` module, oraz there jest no circular zaimportuj problem
# then, so problems introduced by fiddling the order of imports here won't
# manifest.

klasa _localimpl:
    """A klasa managing thread-local dicts"""
    __slots__ = 'key', 'dicts', 'localargs', 'locallock', '__weakref__'

    def __init__(self):
        # The key used w the Thread objects' attribute dicts.
        # We keep it a string dla speed but make it unlikely to clash with
        # a "real" attribute.
        self.key = '_threading_local._localimpl.' + str(id(self))
        # { id(Thread) -> (ref(Thread), thread-local dict) }
        self.dicts = {}

    def get_dict(self):
        """Return the dict dla the current thread. Raises KeyError jeżeli none
        defined."""
        thread = current_thread()
        zwróć self.dicts[id(thread)][1]

    def create_dict(self):
        """Create a new dict dla the current thread, oraz zwróć it."""
        localdict = {}
        key = self.key
        thread = current_thread()
        idt = id(thread)
        def local_deleted(_, key=key):
            # When the localimpl jest deleted, remove the thread attribute.
            thread = wrthread()
            jeżeli thread jest nie Nic:
                usuń thread.__dict__[key]
        def thread_deleted(_, idt=idt):
            # When the thread jest deleted, remove the local dict.
            # Note that this jest suboptimal jeżeli the thread object gets
            # caught w a reference loop. We would like to be called
            # jako soon jako the OS-level thread ends instead.
            local = wrlocal()
            jeżeli local jest nie Nic:
                dct = local.dicts.pop(idt)
        wrlocal = ref(self, local_deleted)
        wrthread = ref(thread, thread_deleted)
        thread.__dict__[key] = wrlocal
        self.dicts[idt] = wrthread, localdict
        zwróć localdict


@contextmanager
def _patch(self):
    impl = object.__getattribute__(self, '_local__impl')
    spróbuj:
        dct = impl.get_dict()
    wyjąwszy KeyError:
        dct = impl.create_dict()
        args, kw = impl.localargs
        self.__init__(*args, **kw)
    przy impl.locallock:
        object.__setattr__(self, '__dict__', dct)
        uzyskaj


klasa local:
    __slots__ = '_local__impl', '__dict__'

    def __new__(cls, *args, **kw):
        jeżeli (args albo kw) oraz (cls.__init__ jest object.__init__):
            podnieś TypeError("Initialization arguments are nie supported")
        self = object.__new__(cls)
        impl = _localimpl()
        impl.localargs = (args, kw)
        impl.locallock = RLock()
        object.__setattr__(self, '_local__impl', impl)
        # We need to create the thread dict w anticipation of
        # __init__ being called, to make sure we don't call it
        # again ourselves.
        impl.create_dict()
        zwróć self

    def __getattribute__(self, name):
        przy _patch(self):
            zwróć object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        jeżeli name == '__dict__':
            podnieś AttributeError(
                "%r object attribute '__dict__' jest read-only"
                % self.__class__.__name__)
        przy _patch(self):
            zwróć object.__setattr__(self, name, value)

    def __delattr__(self, name):
        jeżeli name == '__dict__':
            podnieś AttributeError(
                "%r object attribute '__dict__' jest read-only"
                % self.__class__.__name__)
        przy _patch(self):
            zwróć object.__delattr__(self, name)


z threading zaimportuj current_thread, RLock
