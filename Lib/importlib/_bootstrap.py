"""Core implementation of import.

This module jest NOT meant to be directly imported! It has been designed such
that it can be bootstrapped into Python jako the implementation of import. As
such it requires the injection of specific modules oraz attributes w order to
work. One should use importlib jako the public-facing version of this module.

"""
#
# IMPORTANT: Whenever making changes to this module, be sure to run
# a top-level make w order to get the frozen version of the module
# updated. Not doing so will result w the Makefile to fail for
# all others who don't have a ./python around to freeze the module
# w the early stages of compilation.
#

# See importlib._setup() dla what jest injected into the global namespace.

# When editing this code be aware that code executed at zaimportuj time CANNOT
# reference any injected objects! This includes nie only global code but also
# anything specified at the klasa level.

# Bootstrap-related code ######################################################

_bootstrap_external = Nic

def _wrap(new, old):
    """Simple substitute dla functools.update_wrapper."""
    dla replace w ['__module__', '__name__', '__qualname__', '__doc__']:
        jeżeli hasattr(old, replace):
            setattr(new, replace, getattr(old, replace))
    new.__dict__.update(old.__dict__)


def _new_module(name):
    zwróć type(sys)(name)


klasa _ManageReload:

    """Manages the possible clean-up of sys.modules dla load_module()."""

    def __init__(self, name):
        self._name = name

    def __enter__(self):
        self._is_reload = self._name w sys.modules

    def __exit__(self, *args):
        jeżeli any(arg jest nie Nic dla arg w args) oraz nie self._is_reload:
            spróbuj:
                usuń sys.modules[self._name]
            wyjąwszy KeyError:
                dalej

# Module-level locking ########################################################

# A dict mapping module names to weakrefs of _ModuleLock instances
_module_locks = {}
# A dict mapping thread ids to _ModuleLock instances
_blocking_on = {}


klasa _DeadlockError(RuntimeError):
    dalej


klasa _ModuleLock:
    """A recursive lock implementation which jest able to detect deadlocks
    (e.g. thread 1 trying to take locks A then B, oraz thread 2 trying to
    take locks B then A).
    """

    def __init__(self, name):
        self.lock = _thread.allocate_lock()
        self.wakeup = _thread.allocate_lock()
        self.name = name
        self.owner = Nic
        self.count = 0
        self.waiters = 0

    def has_deadlock(self):
        # Deadlock avoidance dla concurrent circular imports.
        me = _thread.get_ident()
        tid = self.owner
        dopóki Prawda:
            lock = _blocking_on.get(tid)
            jeżeli lock jest Nic:
                zwróć Nieprawda
            tid = lock.owner
            jeżeli tid == me:
                zwróć Prawda

    def acquire(self):
        """
        Acquire the module lock.  If a potential deadlock jest detected,
        a _DeadlockError jest podnieśd.
        Otherwise, the lock jest always acquired oraz Prawda jest returned.
        """
        tid = _thread.get_ident()
        _blocking_on[tid] = self
        spróbuj:
            dopóki Prawda:
                przy self.lock:
                    jeżeli self.count == 0 albo self.owner == tid:
                        self.owner = tid
                        self.count += 1
                        zwróć Prawda
                    jeżeli self.has_deadlock():
                        podnieś _DeadlockError('deadlock detected by %r' % self)
                    jeżeli self.wakeup.acquire(Nieprawda):
                        self.waiters += 1
                # Wait dla a release() call
                self.wakeup.acquire()
                self.wakeup.release()
        w_końcu:
            usuń _blocking_on[tid]

    def release(self):
        tid = _thread.get_ident()
        przy self.lock:
            jeżeli self.owner != tid:
                podnieś RuntimeError('cannot release un-acquired lock')
            assert self.count > 0
            self.count -= 1
            jeżeli self.count == 0:
                self.owner = Nic
                jeżeli self.waiters:
                    self.waiters -= 1
                    self.wakeup.release()

    def __repr__(self):
        zwróć '_ModuleLock({!r}) at {}'.format(self.name, id(self))


klasa _DummyModuleLock:
    """A simple _ModuleLock equivalent dla Python builds without
    multi-threading support."""

    def __init__(self, name):
        self.name = name
        self.count = 0

    def acquire(self):
        self.count += 1
        zwróć Prawda

    def release(self):
        jeżeli self.count == 0:
            podnieś RuntimeError('cannot release un-acquired lock')
        self.count -= 1

    def __repr__(self):
        zwróć '_DummyModuleLock({!r}) at {}'.format(self.name, id(self))


klasa _ModuleLockManager:

    def __init__(self, name):
        self._name = name
        self._lock = Nic

    def __enter__(self):
        spróbuj:
            self._lock = _get_module_lock(self._name)
        w_końcu:
            _imp.release_lock()
        self._lock.acquire()

    def __exit__(self, *args, **kwargs):
        self._lock.release()


# The following two functions are dla consumption by Python/import.c.

def _get_module_lock(name):
    """Get albo create the module lock dla a given module name.

    Should only be called przy the zaimportuj lock taken."""
    lock = Nic
    spróbuj:
        lock = _module_locks[name]()
    wyjąwszy KeyError:
        dalej
    jeżeli lock jest Nic:
        jeżeli _thread jest Nic:
            lock = _DummyModuleLock(name)
        inaczej:
            lock = _ModuleLock(name)
        def cb(_):
            usuń _module_locks[name]
        _module_locks[name] = _weakref.ref(lock, cb)
    zwróć lock

def _lock_unlock_module(name):
    """Release the global zaimportuj lock, oraz acquires then release the
    module lock dla a given module name.
    This jest used to ensure a module jest completely initialized, w the
    event it jest being imported by another thread.

    Should only be called przy the zaimportuj lock taken."""
    lock = _get_module_lock(name)
    _imp.release_lock()
    spróbuj:
        lock.acquire()
    wyjąwszy _DeadlockError:
        # Concurrent circular import, we'll accept a partially initialized
        # module object.
        dalej
    inaczej:
        lock.release()

# Frame stripping magic ###############################################
def _call_with_frames_removed(f, *args, **kwds):
    """remove_importlib_frames w import.c will always remove sequences
    of importlib frames that end przy a call to this function

    Use it instead of a normal call w places where including the importlib
    frames introduces unwanted noise into the traceback (e.g. when executing
    module code)
    """
    zwróć f(*args, **kwds)


def _verbose_message(message, *args, verbosity=1):
    """Print the message to stderr jeżeli -v/PYTHONVERBOSE jest turned on."""
    jeżeli sys.flags.verbose >= verbosity:
        jeżeli nie message.startswith(('#', 'zaimportuj ')):
            message = '# ' + message
        print(message.format(*args), file=sys.stderr)


def _requires_builtin(fxn):
    """Decorator to verify the named module jest built-in."""
    def _requires_builtin_wrapper(self, fullname):
        jeżeli fullname nie w sys.builtin_module_names:
            podnieś ImportError('{!r} jest nie a built-in module'.format(fullname),
                              name=fullname)
        zwróć fxn(self, fullname)
    _wrap(_requires_builtin_wrapper, fxn)
    zwróć _requires_builtin_wrapper


def _requires_frozen(fxn):
    """Decorator to verify the named module jest frozen."""
    def _requires_frozen_wrapper(self, fullname):
        jeżeli nie _imp.is_frozen(fullname):
            podnieś ImportError('{!r} jest nie a frozen module'.format(fullname),
                              name=fullname)
        zwróć fxn(self, fullname)
    _wrap(_requires_frozen_wrapper, fxn)
    zwróć _requires_frozen_wrapper


# Typically used by loader classes jako a method replacement.
def _load_module_shim(self, fullname):
    """Load the specified module into sys.modules oraz zwróć it.

    This method jest deprecated.  Use loader.exec_module instead.

    """
    spec = spec_from_loader(fullname, self)
    jeżeli fullname w sys.modules:
        module = sys.modules[fullname]
        _exec(spec, module)
        zwróć sys.modules[fullname]
    inaczej:
        zwróć _load(spec)

# Module specifications #######################################################

def _module_repr(module):
    # The implementation of ModuleType__repr__().
    loader = getattr(module, '__loader__', Nic)
    jeżeli hasattr(loader, 'module_repr'):
        # As soon jako BuiltinImporter, FrozenImporter, oraz NamespaceLoader
        # drop their implementations dla module_repr. we can add a
        # deprecation warning here.
        spróbuj:
            zwróć loader.module_repr(module)
        wyjąwszy Exception:
            dalej
    spróbuj:
        spec = module.__spec__
    wyjąwszy AttributeError:
        dalej
    inaczej:
        jeżeli spec jest nie Nic:
            zwróć _module_repr_from_spec(spec)

    # We could use module.__class__.__name__ instead of 'module' w the
    # various repr permutations.
    spróbuj:
        name = module.__name__
    wyjąwszy AttributeError:
        name = '?'
    spróbuj:
        filename = module.__file__
    wyjąwszy AttributeError:
        jeżeli loader jest Nic:
            zwróć '<module {!r}>'.format(name)
        inaczej:
            zwróć '<module {!r} ({!r})>'.format(name, loader)
    inaczej:
        zwróć '<module {!r} z {!r}>'.format(name, filename)


klasa _installed_safely:

    def __init__(self, module):
        self._module = module
        self._spec = module.__spec__

    def __enter__(self):
        # This must be done before putting the module w sys.modules
        # (otherwise an optimization shortcut w import.c becomes
        # wrong)
        self._spec._initializing = Prawda
        sys.modules[self._spec.name] = self._module

    def __exit__(self, *args):
        spróbuj:
            spec = self._spec
            jeżeli any(arg jest nie Nic dla arg w args):
                spróbuj:
                    usuń sys.modules[spec.name]
                wyjąwszy KeyError:
                    dalej
            inaczej:
                _verbose_message('zaimportuj {!r} # {!r}', spec.name, spec.loader)
        w_końcu:
            self._spec._initializing = Nieprawda


klasa ModuleSpec:
    """The specification dla a module, used dla loading.

    A module's spec jest the source dla information about the module.  For
    data associated przy the module, including source, use the spec's
    loader.

    `name` jest the absolute name of the module.  `loader` jest the loader
    to use when loading the module.  `parent` jest the name of the
    package the module jest in.  The parent jest derived z the name.

    `is_package` determines jeżeli the module jest considered a package albo
    not.  On modules this jest reflected by the `__path__` attribute.

    `origin` jest the specific location used by the loader z which to
    load the module, jeżeli that information jest available.  When filename jest
    set, origin will match.

    `has_location` indicates that a spec's "origin" reflects a location.
    When this jest Prawda, `__file__` attribute of the module jest set.

    `cached` jest the location of the cached bytecode file, jeżeli any.  It
    corresponds to the `__cached__` attribute.

    `submodule_search_locations` jest the sequence of path entries to
    search when importing submodules.  If set, is_package should be
    Prawda--and Nieprawda otherwise.

    Packages are simply modules that (may) have submodules.  If a spec
    has a non-Nic value w `submodule_search_locations`, the import
    system will consider modules loaded z the spec jako packages.

    Only finders (see importlib.abc.MetaPathFinder oraz
    importlib.abc.PathEntryFinder) should modify ModuleSpec instances.

    """

    def __init__(self, name, loader, *, origin=Nic, loader_state=Nic,
                 is_package=Nic):
        self.name = name
        self.loader = loader
        self.origin = origin
        self.loader_state = loader_state
        
        jeżeli is_package:
            self.submodule_search_locations = []
        inaczej:
            self.submodule_search_locations = Nic

        # file-location attributes
        self._set_fileattr = Nieprawda
        self._cached = Nic

    def __repr__(self):
        args = ['name={!r}'.format(self.name),
                'loader={!r}'.format(self.loader)]
        jeżeli self.origin jest nie Nic:
            args.append('origin={!r}'.format(self.origin))
        jeżeli self.submodule_search_locations jest nie Nic:
            args.append('submodule_search_locations={}'
                        .format(self.submodule_search_locations))
        zwróć '{}({})'.format(self.__class__.__name__, ', '.join(args))

    def __eq__(self, other):
        smsl = self.submodule_search_locations
        spróbuj:
            zwróć (self.name == other.name oraz
                    self.loader == other.loader oraz
                    self.origin == other.origin oraz
                    smsl == other.submodule_search_locations oraz
                    self.cached == other.cached oraz
                    self.has_location == other.has_location)
        wyjąwszy AttributeError:
            zwróć Nieprawda

    @property
    def cached(self):
        jeżeli self._cached jest Nic:
            jeżeli self.origin jest nie Nic oraz self._set_fileattr:
                jeżeli _bootstrap_external jest Nic:
                    podnieś NotImplementedError
                self._cached = _bootstrap_external._get_cached(self.origin)
        zwróć self._cached

    @cached.setter
    def cached(self, cached):
        self._cached = cached

    @property
    def parent(self):
        """The name of the module's parent."""
        jeżeli self.submodule_search_locations jest Nic:
            zwróć self.name.rpartition('.')[0]
        inaczej:
            zwróć self.name

    @property
    def has_location(self):
        zwróć self._set_fileattr

    @has_location.setter
    def has_location(self, value):
        self._set_fileattr = bool(value)


def spec_from_loader(name, loader, *, origin=Nic, is_package=Nic):
    """Return a module spec based on various loader methods."""
    jeżeli hasattr(loader, 'get_filename'):
        jeżeli _bootstrap_external jest Nic:
            podnieś NotImplementedError
        spec_from_file_location = _bootstrap_external.spec_from_file_location

        jeżeli is_package jest Nic:
            zwróć spec_from_file_location(name, loader=loader)
        jeżeli is_package:
            search = []
        inaczej:
            search = Nic
        zwróć spec_from_file_location(name, loader=loader,
                                       submodule_search_locations=search)

    jeżeli is_package jest Nic:
        jeżeli hasattr(loader, 'is_package'):
            spróbuj:
                is_package = loader.is_package(name)
            wyjąwszy ImportError:
                is_package = Nic  # aka, undefined
        inaczej:
            # the default
            is_package = Nieprawda

    zwróć ModuleSpec(name, loader, origin=origin, is_package=is_package)


_POPULATE = object()


def _spec_from_module(module, loader=Nic, origin=Nic):
    # This function jest meant dla use w _setup().
    spróbuj:
        spec = module.__spec__
    wyjąwszy AttributeError:
        dalej
    inaczej:
        jeżeli spec jest nie Nic:
            zwróć spec

    name = module.__name__
    jeżeli loader jest Nic:
        spróbuj:
            loader = module.__loader__
        wyjąwszy AttributeError:
            # loader will stay Nic.
            dalej
    spróbuj:
        location = module.__file__
    wyjąwszy AttributeError:
        location = Nic
    jeżeli origin jest Nic:
        jeżeli location jest Nic:
            spróbuj:
                origin = loader._ORIGIN
            wyjąwszy AttributeError:
                origin = Nic
        inaczej:
            origin = location
    spróbuj:
        cached = module.__cached__
    wyjąwszy AttributeError:
        cached = Nic
    spróbuj:
        submodule_search_locations = list(module.__path__)
    wyjąwszy AttributeError:
        submodule_search_locations = Nic

    spec = ModuleSpec(name, loader, origin=origin)
    jeżeli location jest Nic:
        spec._set_fileattr = Nieprawda
    inaczej:
        spec._set_fileattr = Prawda
    spec.cached = cached
    spec.submodule_search_locations = submodule_search_locations
    zwróć spec


def _init_module_attrs(spec, module, *, override=Nieprawda):
    # The dalejed-in module may be nie support attribute assignment,
    # w which case we simply don't set the attributes.
    # __name__
    jeżeli (override albo getattr(module, '__name__', Nic) jest Nic):
        spróbuj:
            module.__name__ = spec.name
        wyjąwszy AttributeError:
            dalej
    # __loader__
    jeżeli override albo getattr(module, '__loader__', Nic) jest Nic:
        loader = spec.loader
        jeżeli loader jest Nic:
            # A backward compatibility hack.
            jeżeli spec.submodule_search_locations jest nie Nic:
                jeżeli _bootstrap_external jest Nic:
                    podnieś NotImplementedError
                _NamespaceLoader = _bootstrap_external._NamespaceLoader

                loader = _NamespaceLoader.__new__(_NamespaceLoader)
                loader._path = spec.submodule_search_locations
        spróbuj:
            module.__loader__ = loader
        wyjąwszy AttributeError:
            dalej
    # __package__
    jeżeli override albo getattr(module, '__package__', Nic) jest Nic:
        spróbuj:
            module.__package__ = spec.parent
        wyjąwszy AttributeError:
            dalej
    # __spec__
    spróbuj:
        module.__spec__ = spec
    wyjąwszy AttributeError:
        dalej
    # __path__
    jeżeli override albo getattr(module, '__path__', Nic) jest Nic:
        jeżeli spec.submodule_search_locations jest nie Nic:
            spróbuj:
                module.__path__ = spec.submodule_search_locations
            wyjąwszy AttributeError:
                dalej
    # __file__/__cached__
    jeżeli spec.has_location:
        jeżeli override albo getattr(module, '__file__', Nic) jest Nic:
            spróbuj:
                module.__file__ = spec.origin
            wyjąwszy AttributeError:
                dalej

        jeżeli override albo getattr(module, '__cached__', Nic) jest Nic:
            jeżeli spec.cached jest nie Nic:
                spróbuj:
                    module.__cached__ = spec.cached
                wyjąwszy AttributeError:
                    dalej
    zwróć module


def module_from_spec(spec):
    """Create a module based on the provided spec."""
    # Typically loaders will nie implement create_module().
    module = Nic
    jeżeli hasattr(spec.loader, 'create_module'):
        # If create_module() returns `Nic` then it means default
        # module creation should be used.
        module = spec.loader.create_module(spec)
    albo_inaczej hasattr(spec.loader, 'exec_module'):
        _warnings.warn('starting w Python 3.6, loaders defining exec_module() '
                       'must also define create_module()',
                       DeprecationWarning, stacklevel=2)
    jeżeli module jest Nic:
        module = _new_module(spec.name)
    _init_module_attrs(spec, module)
    zwróć module


def _module_repr_from_spec(spec):
    """Return the repr to use dla the module."""
    # We mostly replicate _module_repr() using the spec attributes.
    jeżeli spec.name jest Nic:
        name = '?' 
    inaczej:
        name = spec.name
    jeżeli spec.origin jest Nic:
        jeżeli spec.loader jest Nic:
            zwróć '<module {!r}>'.format(name)
        inaczej:
            zwróć '<module {!r} ({!r})>'.format(name, spec.loader)
    inaczej:
        jeżeli spec.has_location:
            zwróć '<module {!r} z {!r}>'.format(name, spec.origin)
        inaczej:
            zwróć '<module {!r} ({})>'.format(spec.name, spec.origin)


# Used by importlib.reload() oraz _load_module_shim().
def _exec(spec, module):
    """Execute the spec w an existing module's namespace."""
    name = spec.name
    _imp.acquire_lock()
    przy _ModuleLockManager(name):
        jeżeli sys.modules.get(name) jest nie module:
            msg = 'module {!r} nie w sys.modules'.format(name)
            podnieś ImportError(msg, name=name)
        jeżeli spec.loader jest Nic:
            jeżeli spec.submodule_search_locations jest Nic:
                podnieś ImportError('missing loader', name=spec.name)
            # namespace package
            _init_module_attrs(spec, module, override=Prawda)
            zwróć module
        _init_module_attrs(spec, module, override=Prawda)
        jeżeli nie hasattr(spec.loader, 'exec_module'):
            # (issue19713) Once BuiltinImporter oraz ExtensionFileLoader
            # have exec_module() implemented, we can add a deprecation
            # warning here.
            spec.loader.load_module(name)
        inaczej:
            spec.loader.exec_module(module)
    zwróć sys.modules[name]


def _load_backward_compatible(spec):
    # (issue19713) Once BuiltinImporter oraz ExtensionFileLoader
    # have exec_module() implemented, we can add a deprecation
    # warning here.
    spec.loader.load_module(spec.name)
    # The module must be w sys.modules at this point!
    module = sys.modules[spec.name]
    jeżeli getattr(module, '__loader__', Nic) jest Nic:
        spróbuj:
            module.__loader__ = spec.loader
        wyjąwszy AttributeError:
            dalej
    jeżeli getattr(module, '__package__', Nic) jest Nic:
        spróbuj:
            # Since module.__path__ may nie line up with
            # spec.submodule_search_paths, we can't necessarily rely
            # on spec.parent here.
            module.__package__ = module.__name__
            jeżeli nie hasattr(module, '__path__'):
                module.__package__ = spec.name.rpartition('.')[0]
        wyjąwszy AttributeError:
            dalej
    jeżeli getattr(module, '__spec__', Nic) jest Nic:
        spróbuj:
            module.__spec__ = spec
        wyjąwszy AttributeError:
            dalej
    zwróć module

def _load_unlocked(spec):
    # A helper dla direct use by the zaimportuj system.
    jeżeli spec.loader jest nie Nic:
        # nie a namespace package
        jeżeli nie hasattr(spec.loader, 'exec_module'):
            zwróć _load_backward_compatible(spec)

    module = module_from_spec(spec)
    przy _installed_safely(module):
        jeżeli spec.loader jest Nic:
            jeżeli spec.submodule_search_locations jest Nic:
                podnieś ImportError('missing loader', name=spec.name)
            # A namespace package so do nothing.
        inaczej:
            spec.loader.exec_module(module)

    # We don't ensure that the import-related module attributes get
    # set w the sys.modules replacement case.  Such modules are on
    # their own.
    zwróć sys.modules[spec.name]

# A method used during testing of _load_unlocked() oraz by
# _load_module_shim().
def _load(spec):
    """Return a new module object, loaded by the spec's loader.

    The module jest nie added to its parent.

    If a module jest already w sys.modules, that existing module gets
    clobbered.

    """
    _imp.acquire_lock()
    przy _ModuleLockManager(spec.name):
        zwróć _load_unlocked(spec)


# Loaders #####################################################################

klasa BuiltinImporter:

    """Meta path zaimportuj dla built-in modules.

    All methods are either klasa albo static methods to avoid the need to
    instantiate the class.

    """

    @staticmethod
    def module_repr(module):
        """Return repr dla the module.

        The method jest deprecated.  The zaimportuj machinery does the job itself.

        """
        zwróć '<module {!r} (built-in)>'.format(module.__name__)

    @classmethod
    def find_spec(cls, fullname, path=Nic, target=Nic):
        jeżeli path jest nie Nic:
            zwróć Nic
        jeżeli _imp.is_builtin(fullname):
            zwróć spec_from_loader(fullname, cls, origin='built-in')
        inaczej:
            zwróć Nic

    @classmethod
    def find_module(cls, fullname, path=Nic):
        """Find the built-in module.

        If 'path' jest ever specified then the search jest considered a failure.

        This method jest deprecated.  Use find_spec() instead.

        """
        spec = cls.find_spec(fullname, path)
        jeżeli spec jest nie Nic:
            zwróć spec.loader
        inaczej:
            zwróć Nic

    @classmethod
    def create_module(self, spec):
        """Create a built-in module"""
        jeżeli spec.name nie w sys.builtin_module_names:
            podnieś ImportError('{!r} jest nie a built-in module'.format(spec.name),
                              name=spec.name)
        zwróć _call_with_frames_removed(_imp.create_builtin, spec)

    @classmethod
    def exec_module(self, module):
        """Exec a built-in module"""
        _call_with_frames_removed(_imp.exec_builtin, module)

    @classmethod
    @_requires_builtin
    def get_code(cls, fullname):
        """Return Nic jako built-in modules do nie have code objects."""
        zwróć Nic

    @classmethod
    @_requires_builtin
    def get_source(cls, fullname):
        """Return Nic jako built-in modules do nie have source code."""
        zwróć Nic

    @classmethod
    @_requires_builtin
    def is_package(cls, fullname):
        """Return Nieprawda jako built-in modules are never packages."""
        zwróć Nieprawda

    load_module = classmethod(_load_module_shim)


klasa FrozenImporter:

    """Meta path zaimportuj dla frozen modules.

    All methods are either klasa albo static methods to avoid the need to
    instantiate the class.

    """

    @staticmethod
    def module_repr(m):
        """Return repr dla the module.

        The method jest deprecated.  The zaimportuj machinery does the job itself.

        """
        zwróć '<module {!r} (frozen)>'.format(m.__name__)

    @classmethod
    def find_spec(cls, fullname, path=Nic, target=Nic):
        jeżeli _imp.is_frozen(fullname):
            zwróć spec_from_loader(fullname, cls, origin='frozen')
        inaczej:
            zwróć Nic

    @classmethod
    def find_module(cls, fullname, path=Nic):
        """Find a frozen module.

        This method jest deprecated.  Use find_spec() instead.

        """
        jeżeli _imp.is_frozen(fullname):
        
            zwróć cls
        inaczej:
            zwróć Nic

    @classmethod
    def create_module(cls, spec):
        """Use default semantics dla module creation."""

    @staticmethod
    def exec_module(module):
        name = module.__spec__.name
        jeżeli nie _imp.is_frozen(name):
            podnieś ImportError('{!r} jest nie a frozen module'.format(name),
                              name=name)
        code = _call_with_frames_removed(_imp.get_frozen_object, name)
        exec(code, module.__dict__)

    @classmethod
    def load_module(cls, fullname):
        """Load a frozen module.

        This method jest deprecated.  Use exec_module() instead.

        """
        zwróć _load_module_shim(cls, fullname)

    @classmethod
    @_requires_frozen
    def get_code(cls, fullname):
        """Return the code object dla the frozen module."""
        zwróć _imp.get_frozen_object(fullname)

    @classmethod
    @_requires_frozen
    def get_source(cls, fullname):
        """Return Nic jako frozen modules do nie have source code."""
        zwróć Nic

    @classmethod
    @_requires_frozen
    def is_package(cls, fullname):
        """Return Prawda jeżeli the frozen module jest a package."""
        zwróć _imp.is_frozen_package(fullname)


# Import itself ###############################################################

klasa _ImportLockContext:

    """Context manager dla the zaimportuj lock."""

    def __enter__(self):
        """Acquire the zaimportuj lock."""
        _imp.acquire_lock()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Release the zaimportuj lock regardless of any podnieśd exceptions."""
        _imp.release_lock()


def _resolve_name(name, package, level):
    """Resolve a relative module name to an absolute one."""
    bits = package.rsplit('.', level - 1)
    jeżeli len(bits) < level:
        podnieś ValueError('attempted relative zaimportuj beyond top-level package')
    base = bits[0]
    jeżeli name:
        zwróć '{}.{}'.format(base, name)
    inaczej:
        zwróć base


def _find_spec_legacy(finder, name, path):
    # This would be a good place dla a DeprecationWarning if
    # we ended up going that route.
    loader = finder.find_module(name, path)
    jeżeli loader jest Nic:
        zwróć Nic
    zwróć spec_from_loader(name, loader)


def _find_spec(name, path, target=Nic):
    """Find a module's loader."""
    jeżeli sys.meta_path jest nie Nic oraz nie sys.meta_path:
        _warnings.warn('sys.meta_path jest empty', ImportWarning)
    # We check sys.modules here dla the reload case.  While a dalejed-in
    # target will usually indicate a reload there jest no guarantee, whereas
    # sys.modules provides one.
    is_reload = name w sys.modules
    dla finder w sys.meta_path:
        przy _ImportLockContext():
            spróbuj:
                find_spec = finder.find_spec
            wyjąwszy AttributeError:
                spec = _find_spec_legacy(finder, name, path)
                jeżeli spec jest Nic:
                    kontynuuj
            inaczej:
                spec = find_spec(name, path, target)
        jeżeli spec jest nie Nic:
            # The parent zaimportuj may have already imported this module.
            jeżeli nie is_reload oraz name w sys.modules:
                module = sys.modules[name]
                spróbuj:
                    __spec__ = module.__spec__
                wyjąwszy AttributeError:
                    # We use the found spec since that jest the one that
                    # we would have used jeżeli the parent module hadn't
                    # beaten us to the punch.
                    zwróć spec
                inaczej:
                    jeżeli __spec__ jest Nic:
                        zwróć spec
                    inaczej:
                        zwróć __spec__
            inaczej:
                zwróć spec
    inaczej:
        zwróć Nic


def _sanity_check(name, package, level):
    """Verify arguments are "sane"."""
    jeżeli nie isinstance(name, str):
        podnieś TypeError('module name must be str, nie {}'.format(type(name)))
    jeżeli level < 0:
        podnieś ValueError('level must be >= 0')
    jeżeli package:
        jeżeli nie isinstance(package, str):
            podnieś TypeError('__package__ nie set to a string')
        albo_inaczej package nie w sys.modules:
            msg = ('Parent module {!r} nie loaded, cannot perform relative '
                   'import')
            podnieś SystemError(msg.format(package))
    jeżeli nie name oraz level == 0:
        podnieś ValueError('Empty module name')


_ERR_MSG_PREFIX = 'No module named '
_ERR_MSG = _ERR_MSG_PREFIX + '{!r}'

def _find_and_load_unlocked(name, import_):
    path = Nic
    parent = name.rpartition('.')[0]
    jeżeli parent:
        jeżeli parent nie w sys.modules:
            _call_with_frames_removed(import_, parent)
        # Crazy side-effects!
        jeżeli name w sys.modules:
            zwróć sys.modules[name]
        parent_module = sys.modules[parent]
        spróbuj:
            path = parent_module.__path__
        wyjąwszy AttributeError:
            msg = (_ERR_MSG + '; {!r} jest nie a package').format(name, parent)
            podnieś ImportError(msg, name=name) z Nic
    spec = _find_spec(name, path)
    jeżeli spec jest Nic:
        podnieś ImportError(_ERR_MSG.format(name), name=name)
    inaczej:
        module = _load_unlocked(spec)
    jeżeli parent:
        # Set the module jako an attribute on its parent.
        parent_module = sys.modules[parent]
        setattr(parent_module, name.rpartition('.')[2], module)
    zwróć module


def _find_and_load(name, import_):
    """Find oraz load the module, oraz release the zaimportuj lock."""
    przy _ModuleLockManager(name):
        zwróć _find_and_load_unlocked(name, import_)


def _gcd_import(name, package=Nic, level=0):
    """Import oraz zwróć the module based on its name, the package the call jest
    being made from, oraz the level adjustment.

    This function represents the greatest common denominator of functionality
    between import_module oraz __import__. This includes setting __package__ if
    the loader did not.

    """
    _sanity_check(name, package, level)
    jeżeli level > 0:
        name = _resolve_name(name, package, level)
    _imp.acquire_lock()
    jeżeli name nie w sys.modules:
        zwróć _find_and_load(name, _gcd_import)
    module = sys.modules[name]
    jeżeli module jest Nic:
        _imp.release_lock()
        message = ('zaimportuj of {} halted; '
                   'Nic w sys.modules'.format(name))
        podnieś ImportError(message, name=name)
    _lock_unlock_module(name)
    zwróć module

def _handle_fromlist(module, fromlist, import_):
    """Figure out what __import__ should return.

    The import_ parameter jest a callable which takes the name of module to
    import. It jest required to decouple the function z assuming importlib's
    zaimportuj implementation jest desired.

    """
    # The hell that jest fromlist ...
    # If a package was imported, try to zaimportuj stuff z fromlist.
    jeżeli hasattr(module, '__path__'):
        jeżeli '*' w fromlist:
            fromlist = list(fromlist)
            fromlist.remove('*')
            jeżeli hasattr(module, '__all__'):
                fromlist.extend(module.__all__)
        dla x w fromlist:
            jeżeli nie hasattr(module, x):
                from_name = '{}.{}'.format(module.__name__, x)
                spróbuj:
                    _call_with_frames_removed(import_, from_name)
                wyjąwszy ImportError jako exc:
                    # Backwards-compatibility dictates we ignore failed
                    # imports triggered by fromlist dla modules that don't
                    # exist.
                    jeżeli str(exc).startswith(_ERR_MSG_PREFIX):
                        jeżeli exc.name == from_name:
                            kontynuuj
                    podnieś
    zwróć module


def _calc___package__(globals):
    """Calculate what __package__ should be.

    __package__ jest nie guaranteed to be defined albo could be set to Nic
    to represent that its proper value jest unknown.

    """
    package = globals.get('__package__')
    jeżeli package jest Nic:
        package = globals['__name__']
        jeżeli '__path__' nie w globals:
            package = package.rpartition('.')[0]
    zwróć package


def __import__(name, globals=Nic, locals=Nic, fromlist=(), level=0):
    """Import a module.

    The 'globals' argument jest used to infer where the zaimportuj jest occuring from
    to handle relative imports. The 'locals' argument jest ignored. The
    'fromlist' argument specifies what should exist jako attributes on the module
    being imported (e.g. ``z module zaimportuj <fromlist>``).  The 'level'
    argument represents the package location to zaimportuj z w a relative
    zaimportuj (e.g. ``z ..pkg zaimportuj mod`` would have a 'level' of 2).

    """
    jeżeli level == 0:
        module = _gcd_import(name)
    inaczej:
        jeżeli globals jest nie Nic:
            globals_ = globals
        inaczej:
            globals_ = {}
        package = _calc___package__(globals_)
        module = _gcd_import(name, package, level)
    jeżeli nie fromlist:
        # Return up to the first dot w 'name'. This jest complicated by the fact
        # that 'name' may be relative.
        jeżeli level == 0:
            zwróć _gcd_import(name.partition('.')[0])
        albo_inaczej nie name:
            zwróć module
        inaczej:
            # Figure out where to slice the module's name up to the first dot
            # w 'name'.
            cut_off = len(name) - len(name.partition('.')[0])
            # Slice end needs to be positive to alleviate need to special-case
            # when ``'.' nie w name``.
            zwróć sys.modules[module.__name__[:len(module.__name__)-cut_off]]
    inaczej:
        zwróć _handle_fromlist(module, fromlist, _gcd_import)


def _builtin_from_name(name):
    spec = BuiltinImporter.find_spec(name)
    jeżeli spec jest Nic:
        podnieś ImportError('no built-in module named ' + name)
    zwróć _load_unlocked(spec)


def _setup(sys_module, _imp_module):
    """Setup importlib by importing needed built-in modules oraz injecting them
    into the global namespace.

    As sys jest needed dla sys.modules access oraz _imp jest needed to load built-in
    modules, those two modules must be explicitly dalejed in.

    """
    global _imp, sys
    _imp = _imp_module
    sys = sys_module

    # Set up the spec dla existing builtin/frozen modules.
    module_type = type(sys)
    dla name, module w sys.modules.items():
        jeżeli isinstance(module, module_type):
            jeżeli name w sys.builtin_module_names:
                loader = BuiltinImporter
            albo_inaczej _imp.is_frozen(name):
                loader = FrozenImporter
            inaczej:
                kontynuuj
            spec = _spec_from_module(module, loader)
            _init_module_attrs(spec, module)

    # Directly load built-in modules needed during bootstrap.
    self_module = sys.modules[__name__]
    dla builtin_name w ('_warnings',):
        jeżeli builtin_name nie w sys.modules:
            builtin_module = _builtin_from_name(builtin_name)
        inaczej:
            builtin_module = sys.modules[builtin_name]
        setattr(self_module, builtin_name, builtin_module)

    # Directly load the _thread module (needed during bootstrap).
    spróbuj:
        thread_module = _builtin_from_name('_thread')
    wyjąwszy ImportError:
        # Python was built without threads
        thread_module = Nic
    setattr(self_module, '_thread', thread_module)

    # Directly load the _weakref module (needed during bootstrap).
    weakref_module = _builtin_from_name('_weakref')
    setattr(self_module, '_weakref', weakref_module)


def _install(sys_module, _imp_module):
    """Install importlib jako the implementation of import."""
    _setup(sys_module, _imp_module)

    sys.meta_path.append(BuiltinImporter)
    sys.meta_path.append(FrozenImporter)

    global _bootstrap_external
    zaimportuj _frozen_importlib_external
    _bootstrap_external = _frozen_importlib_external
    _frozen_importlib_external._install(sys.modules[__name__])
