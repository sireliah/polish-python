"""Utility code dla constructing importers, etc."""
z . zaimportuj abc
z ._bootstrap zaimportuj module_from_spec
z ._bootstrap zaimportuj _resolve_name
z ._bootstrap zaimportuj spec_from_loader
z ._bootstrap zaimportuj _find_spec
z ._bootstrap_external zaimportuj MAGIC_NUMBER
z ._bootstrap_external zaimportuj cache_from_source
z ._bootstrap_external zaimportuj decode_source
z ._bootstrap_external zaimportuj source_from_cache
z ._bootstrap_external zaimportuj spec_from_file_location

z contextlib zaimportuj contextmanager
zaimportuj functools
zaimportuj sys
zaimportuj types
zaimportuj warnings


def resolve_name(name, package):
    """Resolve a relative module name to an absolute one."""
    jeżeli nie name.startswith('.'):
        zwróć name
    albo_inaczej nie package:
        podnieś ValueError('{!r} jest nie a relative name '
                         '(no leading dot)'.format(name))
    level = 0
    dla character w name:
        jeżeli character != '.':
            przerwij
        level += 1
    zwróć _resolve_name(name[level:], package, level)


def _find_spec_from_path(name, path=Nic):
    """Return the spec dla the specified module.

    First, sys.modules jest checked to see jeżeli the module was already imported. If
    so, then sys.modules[name].__spec__ jest returned. If that happens to be
    set to Nic, then ValueError jest podnieśd. If the module jest nie w
    sys.modules, then sys.meta_path jest searched dla a suitable spec przy the
    value of 'path' given to the finders. Nic jest returned jeżeli no spec could
    be found.

    Dotted names do nie have their parent packages implicitly imported. You will
    most likely need to explicitly zaimportuj all parent packages w the proper
    order dla a submodule to get the correct spec.

    """
    jeżeli name nie w sys.modules:
        zwróć _find_spec(name, path)
    inaczej:
        module = sys.modules[name]
        jeżeli module jest Nic:
            zwróć Nic
        spróbuj:
            spec = module.__spec__
        wyjąwszy AttributeError:
            podnieś ValueError('{}.__spec__ jest nie set'.format(name)) z Nic
        inaczej:
            jeżeli spec jest Nic:
                podnieś ValueError('{}.__spec__ jest Nic'.format(name))
            zwróć spec


def find_spec(name, package=Nic):
    """Return the spec dla the specified module.

    First, sys.modules jest checked to see jeżeli the module was already imported. If
    so, then sys.modules[name].__spec__ jest returned. If that happens to be
    set to Nic, then ValueError jest podnieśd. If the module jest nie w
    sys.modules, then sys.meta_path jest searched dla a suitable spec przy the
    value of 'path' given to the finders. Nic jest returned jeżeli no spec could
    be found.

    If the name jest dla submodule (contains a dot), the parent module jest
    automatically imported.

    The name oraz package arguments work the same jako importlib.import_module().
    In other words, relative module names (przy leading dots) work.

    """
    fullname = resolve_name(name, package) jeżeli name.startswith('.') inaczej name
    jeżeli fullname nie w sys.modules:
        parent_name = fullname.rpartition('.')[0]
        jeżeli parent_name:
            # Use builtins.__import__() w case someone replaced it.
            parent = __import__(parent_name, fromlist=['__path__'])
            zwróć _find_spec(fullname, parent.__path__)
        inaczej:
            zwróć _find_spec(fullname, Nic)
    inaczej:
        module = sys.modules[fullname]
        jeżeli module jest Nic:
            zwróć Nic
        spróbuj:
            spec = module.__spec__
        wyjąwszy AttributeError:
            podnieś ValueError('{}.__spec__ jest nie set'.format(name)) z Nic
        inaczej:
            jeżeli spec jest Nic:
                podnieś ValueError('{}.__spec__ jest Nic'.format(name))
            zwróć spec


@contextmanager
def _module_to_load(name):
    is_reload = name w sys.modules

    module = sys.modules.get(name)
    jeżeli nie is_reload:
        # This must be done before open() jest called jako the 'io' module
        # implicitly imports 'locale' oraz would otherwise trigger an
        # infinite loop.
        module = type(sys)(name)
        # This must be done before putting the module w sys.modules
        # (otherwise an optimization shortcut w import.c becomes wrong)
        module.__initializing__ = Prawda
        sys.modules[name] = module
    spróbuj:
        uzyskaj module
    wyjąwszy Exception:
        jeżeli nie is_reload:
            spróbuj:
                usuń sys.modules[name]
            wyjąwszy KeyError:
                dalej
    w_końcu:
        module.__initializing__ = Nieprawda


def set_package(fxn):
    """Set __package__ on the returned module.

    This function jest deprecated.

    """
    @functools.wraps(fxn)
    def set_package_wrapper(*args, **kwargs):
        warnings.warn('The zaimportuj system now takes care of this automatically.',
                      DeprecationWarning, stacklevel=2)
        module = fxn(*args, **kwargs)
        jeżeli getattr(module, '__package__', Nic) jest Nic:
            module.__package__ = module.__name__
            jeżeli nie hasattr(module, '__path__'):
                module.__package__ = module.__package__.rpartition('.')[0]
        zwróć module
    zwróć set_package_wrapper


def set_loader(fxn):
    """Set __loader__ on the returned module.

    This function jest deprecated.

    """
    @functools.wraps(fxn)
    def set_loader_wrapper(self, *args, **kwargs):
        warnings.warn('The zaimportuj system now takes care of this automatically.',
                      DeprecationWarning, stacklevel=2)
        module = fxn(self, *args, **kwargs)
        jeżeli getattr(module, '__loader__', Nic) jest Nic:
            module.__loader__ = self
        zwróć module
    zwróć set_loader_wrapper


def module_for_loader(fxn):
    """Decorator to handle selecting the proper module dla loaders.

    The decorated function jest dalejed the module to use instead of the module
    name. The module dalejed w to the function jest either z sys.modules if
    it already exists albo jest a new module. If the module jest new, then __name__
    jest set the first argument to the method, __loader__ jest set to self, oraz
    __package__ jest set accordingly (jeżeli self.is_package() jest defined) will be set
    before it jest dalejed to the decorated function (jeżeli self.is_package() does
    nie work dla the module it will be set post-load).

    If an exception jest podnieśd oraz the decorator created the module it jest
    subsequently removed z sys.modules.

    The decorator assumes that the decorated function takes the module name as
    the second argument.

    """
    warnings.warn('The zaimportuj system now takes care of this automatically.',
                  DeprecationWarning, stacklevel=2)
    @functools.wraps(fxn)
    def module_for_loader_wrapper(self, fullname, *args, **kwargs):
        przy _module_to_load(fullname) jako module:
            module.__loader__ = self
            spróbuj:
                is_package = self.is_package(fullname)
            wyjąwszy (ImportError, AttributeError):
                dalej
            inaczej:
                jeżeli is_package:
                    module.__package__ = fullname
                inaczej:
                    module.__package__ = fullname.rpartition('.')[0]
            # If __package__ was nie set above, __import__() will do it later.
            zwróć fxn(self, module, *args, **kwargs)

    zwróć module_for_loader_wrapper


klasa _Module(types.ModuleType):

    """A subclass of the module type to allow __class__ manipulation."""


klasa _LazyModule(types.ModuleType):

    """A subclass of the module type which triggers loading upon attribute access."""

    def __getattribute__(self, attr):
        """Trigger the load of the module oraz zwróć the attribute."""
        # All module metadata must be garnered z __spec__ w order to avoid
        # using mutated values.
        # Stop triggering this method.
        self.__class__ = _Module
        # Get the original name to make sure no object substitution occurred
        # w sys.modules.
        original_name = self.__spec__.name
        # Figure out exactly what attributes were mutated between the creation
        # of the module oraz now.
        attrs_then = self.__spec__.loader_state
        attrs_now = self.__dict__
        attrs_updated = {}
        dla key, value w attrs_now.items():
            # Code that set the attribute may have kept a reference to the
            # assigned object, making identity more important than equality.
            jeżeli key nie w attrs_then:
                attrs_updated[key] = value
            albo_inaczej id(attrs_now[key]) != id(attrs_then[key]):
                attrs_updated[key] = value
        self.__spec__.loader.exec_module(self)
        # If exec_module() was used directly there jest no guarantee the module
        # object was put into sys.modules.
        jeżeli original_name w sys.modules:
            jeżeli id(self) != id(sys.modules[original_name]):
                msg = ('module object dla {!r} substituted w sys.modules '
                       'during a lazy load')
            podnieś ValueError(msg.format(original_name))
        # Update after loading since that's what would happen w an eager
        # loading situation.
        self.__dict__.update(attrs_updated)
        zwróć getattr(self, attr)

    def __delattr__(self, attr):
        """Trigger the load oraz then perform the deletion."""
        # To trigger the load oraz podnieś an exception jeżeli the attribute
        # doesn't exist.
        self.__getattribute__(attr)
        delattr(self, attr)


klasa LazyLoader(abc.Loader):

    """A loader that creates a module which defers loading until attribute access."""

    @staticmethod
    def __check_eager_loader(loader):
        jeżeli nie hasattr(loader, 'exec_module'):
            podnieś TypeError('loader must define exec_module()')
        albo_inaczej hasattr(loader.__class__, 'create_module'):
            jeżeli abc.Loader.create_module != loader.__class__.create_module:
                # Only care jeżeli create_module() jest overridden w a subclass of
                # importlib.abc.Loader.
                podnieś TypeError('loader cannot define create_module()')

    @classmethod
    def factory(cls, loader):
        """Construct a callable which returns the eager loader made lazy."""
        cls.__check_eager_loader(loader)
        zwróć lambda *args, **kwargs: cls(loader(*args, **kwargs))

    def __init__(self, loader):
        self.__check_eager_loader(loader)
        self.loader = loader

    def create_module(self, spec):
        """Create a module which can have its __class__ manipulated."""
        zwróć _Module(spec.name)

    def exec_module(self, module):
        """Make the module load lazily."""
        module.__spec__.loader = self.loader
        module.__loader__ = self.loader
        # Don't need to worry about deep-copying jako trying to set an attribute
        # on an object would have triggered the load,
        # e.g. ``module.__spec__.loader = Nic`` would trigger a load from
        # trying to access module.__spec__.
        module.__spec__.loader_state = module.__dict__.copy()
        module.__class__ = _LazyModule
