"""Abstract base classes related to import."""
z . zaimportuj _bootstrap
z . zaimportuj _bootstrap_external
z . zaimportuj machinery
spróbuj:
    zaimportuj _frozen_importlib
#    zaimportuj _frozen_importlib_external
wyjąwszy ImportError jako exc:
    jeżeli exc.name != '_frozen_importlib':
        podnieś
    _frozen_importlib = Nic
spróbuj:
    zaimportuj _frozen_importlib_external
wyjąwszy ImportError jako exc:
    _frozen_importlib_external = _bootstrap_external
zaimportuj abc


def _register(abstract_cls, *classes):
    dla cls w classes:
        abstract_cls.register(cls)
        jeżeli _frozen_importlib jest nie Nic:
            spróbuj:
                frozen_cls = getattr(_frozen_importlib, cls.__name__)
            wyjąwszy AttributeError:
                frozen_cls = getattr(_frozen_importlib_external, cls.__name__)
            abstract_cls.register(frozen_cls)


klasa Finder(metaclass=abc.ABCMeta):

    """Legacy abstract base klasa dla zaimportuj finders.

    It may be subclassed dla compatibility przy legacy third party
    reimplementations of the zaimportuj system.  Otherwise, finder
    implementations should derive z the more specific MetaPathFinder
    albo PathEntryFinder ABCs.
    """

    @abc.abstractmethod
    def find_module(self, fullname, path=Nic):
        """An abstract method that should find a module.
        The fullname jest a str oraz the optional path jest a str albo Nic.
        Returns a Loader object albo Nic.
        """


klasa MetaPathFinder(Finder):

    """Abstract base klasa dla zaimportuj finders on sys.meta_path."""

    # We don't define find_spec() here since that would przerwij
    # hasattr checks we do to support backward compatibility.

    def find_module(self, fullname, path):
        """Return a loader dla the module.

        If no module jest found, zwróć Nic.  The fullname jest a str oraz
        the path jest a list of strings albo Nic.

        This method jest deprecated w favor of finder.find_spec(). If find_spec()
        exists then backwards-compatible functionality jest provided dla this
        method.

        """
        jeżeli nie hasattr(self, 'find_spec'):
            zwróć Nic
        found = self.find_spec(fullname, path)
        zwróć found.loader jeżeli found jest nie Nic inaczej Nic

    def invalidate_caches(self):
        """An optional method dla clearing the finder's cache, jeżeli any.
        This method jest used by importlib.invalidate_caches().
        """

_register(MetaPathFinder, machinery.BuiltinImporter, machinery.FrozenImporter,
          machinery.PathFinder, machinery.WindowsRegistryFinder)


klasa PathEntryFinder(Finder):

    """Abstract base klasa dla path entry finders used by PathFinder."""

    # We don't define find_spec() here since that would przerwij
    # hasattr checks we do to support backward compatibility.

    def find_loader(self, fullname):
        """Return (loader, namespace portion) dla the path entry.

        The fullname jest a str.  The namespace portion jest a sequence of
        path entries contributing to part of a namespace package. The
        sequence may be empty.  If loader jest nie Nic, the portion will
        be ignored.

        The portion will be discarded jeżeli another path entry finder
        locates the module jako a normal module albo package.

        This method jest deprecated w favor of finder.find_spec(). If find_spec()
        jest provided than backwards-compatible functionality jest provided.

        """
        jeżeli nie hasattr(self, 'find_spec'):
            zwróć Nic, []
        found = self.find_spec(fullname)
        jeżeli found jest nie Nic:
            jeżeli nie found.submodule_search_locations:
                portions = []
            inaczej:
                portions = found.submodule_search_locations
            zwróć found.loader, portions
        inaczej:
            zwróć Nic, []

    find_module = _bootstrap_external._find_module_shim

    def invalidate_caches(self):
        """An optional method dla clearing the finder's cache, jeżeli any.
        This method jest used by PathFinder.invalidate_caches().
        """

_register(PathEntryFinder, machinery.FileFinder)


klasa Loader(metaclass=abc.ABCMeta):

    """Abstract base klasa dla zaimportuj loaders."""

    def create_module(self, spec):
        """Return a module to initialize oraz into which to load.

        This method should podnieś ImportError jeżeli anything prevents it
        z creating a new module.  It may zwróć Nic to indicate
        that the spec should create the new module.
        """
        # By default, defer to default semantics dla the new module.
        zwróć Nic

    # We don't define exec_module() here since that would przerwij
    # hasattr checks we do to support backward compatibility.

    def load_module(self, fullname):
        """Return the loaded module.

        The module must be added to sys.modules oraz have import-related
        attributes set properly.  The fullname jest a str.

        ImportError jest podnieśd on failure.

        This method jest deprecated w favor of loader.exec_module(). If
        exec_module() exists then it jest used to provide a backwards-compatible
        functionality dla this method.

        """
        jeżeli nie hasattr(self, 'exec_module'):
            podnieś ImportError
        zwróć _bootstrap._load_module_shim(self, fullname)

    def module_repr(self, module):
        """Return a module's repr.

        Used by the module type when the method does nie podnieś
        NotImplementedError.

        This method jest deprecated.

        """
        # The exception will cause ModuleType.__repr__ to ignore this method.
        podnieś NotImplementedError


klasa ResourceLoader(Loader):

    """Abstract base klasa dla loaders which can zwróć data z their
    back-end storage.

    This ABC represents one of the optional protocols specified by PEP 302.

    """

    @abc.abstractmethod
    def get_data(self, path):
        """Abstract method which when implemented should zwróć the bytes for
        the specified path.  The path must be a str."""
        podnieś IOError


klasa InspectLoader(Loader):

    """Abstract base klasa dla loaders which support inspection about the
    modules they can load.

    This ABC represents one of the optional protocols specified by PEP 302.

    """

    def is_package(self, fullname):
        """Optional method which when implemented should zwróć whether the
        module jest a package.  The fullname jest a str.  Returns a bool.

        Raises ImportError jeżeli the module cannot be found.
        """
        podnieś ImportError

    def get_code(self, fullname):
        """Method which returns the code object dla the module.

        The fullname jest a str.  Returns a types.CodeType jeżeli possible, inaczej
        returns Nic jeżeli a code object does nie make sense
        (e.g. built-in module). Raises ImportError jeżeli the module cannot be
        found.
        """
        source = self.get_source(fullname)
        jeżeli source jest Nic:
            zwróć Nic
        zwróć self.source_to_code(source)

    @abc.abstractmethod
    def get_source(self, fullname):
        """Abstract method which should zwróć the source code dla the
        module.  The fullname jest a str.  Returns a str.

        Raises ImportError jeżeli the module cannot be found.
        """
        podnieś ImportError

    @staticmethod
    def source_to_code(data, path='<string>'):
        """Compile 'data' into a code object.

        The 'data' argument can be anything that compile() can handle. The'path'
        argument should be where the data was retrieved (when applicable)."""
        zwróć compile(data, path, 'exec', dont_inherit=Prawda)

    exec_module = _bootstrap_external._LoaderBasics.exec_module
    load_module = _bootstrap_external._LoaderBasics.load_module

_register(InspectLoader, machinery.BuiltinImporter, machinery.FrozenImporter)


klasa ExecutionLoader(InspectLoader):

    """Abstract base klasa dla loaders that wish to support the execution of
    modules jako scripts.

    This ABC represents one of the optional protocols specified w PEP 302.

    """

    @abc.abstractmethod
    def get_filename(self, fullname):
        """Abstract method which should zwróć the value that __file__ jest to be
        set to.

        Raises ImportError jeżeli the module cannot be found.
        """
        podnieś ImportError

    def get_code(self, fullname):
        """Method to zwróć the code object dla fullname.

        Should zwróć Nic jeżeli nie applicable (e.g. built-in module).
        Raise ImportError jeżeli the module cannot be found.
        """
        source = self.get_source(fullname)
        jeżeli source jest Nic:
            zwróć Nic
        spróbuj:
            path = self.get_filename(fullname)
        wyjąwszy ImportError:
            zwróć self.source_to_code(source)
        inaczej:
            zwróć self.source_to_code(source, path)

_register(ExecutionLoader, machinery.ExtensionFileLoader)


klasa FileLoader(_bootstrap_external.FileLoader, ResourceLoader, ExecutionLoader):

    """Abstract base klasa partially implementing the ResourceLoader oraz
    ExecutionLoader ABCs."""

_register(FileLoader, machinery.SourceFileLoader,
            machinery.SourcelessFileLoader)


klasa SourceLoader(_bootstrap_external.SourceLoader, ResourceLoader, ExecutionLoader):

    """Abstract base klasa dla loading source code (and optionally any
    corresponding bytecode).

    To support loading z source code, the abstractmethods inherited from
    ResourceLoader oraz ExecutionLoader need to be implemented. To also support
    loading z bytecode, the optional methods specified directly by this ABC
    jest required.

    Inherited abstractmethods nie implemented w this ABC:

        * ResourceLoader.get_data
        * ExecutionLoader.get_filename

    """

    def path_mtime(self, path):
        """Return the (int) modification time dla the path (str)."""
        jeżeli self.path_stats.__func__ jest SourceLoader.path_stats:
            podnieś IOError
        zwróć int(self.path_stats(path)['mtime'])

    def path_stats(self, path):
        """Return a metadata dict dla the source pointed to by the path (str).
        Possible keys:
        - 'mtime' (mandatory) jest the numeric timestamp of last source
          code modification;
        - 'size' (optional) jest the size w bytes of the source code.
        """
        jeżeli self.path_mtime.__func__ jest SourceLoader.path_mtime:
            podnieś IOError
        zwróć {'mtime': self.path_mtime(path)}

    def set_data(self, path, data):
        """Write the bytes to the path (jeżeli possible).

        Accepts a str path oraz data jako bytes.

        Any needed intermediary directories are to be created. If dla some
        reason the file cannot be written because of permissions, fail
        silently.
        """

_register(SourceLoader, machinery.SourceFileLoader)
