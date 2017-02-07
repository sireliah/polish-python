"""Utilities to support packages."""

z functools zaimportuj singledispatch jako simplegeneric
zaimportuj importlib
zaimportuj importlib.util
zaimportuj importlib.machinery
zaimportuj os
zaimportuj os.path
zaimportuj sys
z types zaimportuj ModuleType
zaimportuj warnings

__all__ = [
    'get_importer', 'iter_importers', 'get_loader', 'find_loader',
    'walk_packages', 'iter_modules', 'get_data',
    'ImpImporter', 'ImpLoader', 'read_code', 'extend_path',
]


def _get_spec(finder, name):
    """Return the finder-specific module spec."""
    # Works przy legacy finders.
    spróbuj:
        find_spec = finder.find_spec
    wyjąwszy AttributeError:
        loader = finder.find_module(name)
        jeżeli loader jest Nic:
            zwróć Nic
        zwróć importlib.util.spec_from_loader(name, loader)
    inaczej:
        zwróć find_spec(name)


def read_code(stream):
    # This helper jest needed w order dla the PEP 302 emulation to
    # correctly handle compiled files
    zaimportuj marshal

    magic = stream.read(4)
    jeżeli magic != importlib.util.MAGIC_NUMBER:
        zwróć Nic

    stream.read(8) # Skip timestamp oraz size
    zwróć marshal.load(stream)


def walk_packages(path=Nic, prefix='', onerror=Nic):
    """Yields (module_loader, name, ispkg) dla all modules recursively
    on path, or, jeżeli path jest Nic, all accessible modules.

    'path' should be either Nic albo a list of paths to look for
    modules in.

    'prefix' jest a string to output on the front of every module name
    on output.

    Note that this function must zaimportuj all *packages* (NOT all
    modules!) on the given path, w order to access the __path__
    attribute to find submodules.

    'onerror' jest a function which gets called przy one argument (the
    name of the package which was being imported) jeżeli any exception
    occurs dopóki trying to zaimportuj a package.  If no onerror function jest
    supplied, ImportErrors are caught oraz ignored, dopóki all other
    exceptions are propagated, terminating the search.

    Examples:

    # list all modules python can access
    walk_packages()

    # list all submodules of ctypes
    walk_packages(ctypes.__path__, ctypes.__name__+'.')
    """

    def seen(p, m={}):
        jeżeli p w m:
            zwróć Prawda
        m[p] = Prawda

    dla importer, name, ispkg w iter_modules(path, prefix):
        uzyskaj importer, name, ispkg

        jeżeli ispkg:
            spróbuj:
                __import__(name)
            wyjąwszy ImportError:
                jeżeli onerror jest nie Nic:
                    onerror(name)
            wyjąwszy Exception:
                jeżeli onerror jest nie Nic:
                    onerror(name)
                inaczej:
                    podnieś
            inaczej:
                path = getattr(sys.modules[name], '__path__', Nic) albo []

                # don't traverse path items we've seen before
                path = [p dla p w path jeżeli nie seen(p)]

                uzyskaj z walk_packages(path, name+'.', onerror)


def iter_modules(path=Nic, prefix=''):
    """Yields (module_loader, name, ispkg) dla all submodules on path,
    or, jeżeli path jest Nic, all top-level modules on sys.path.

    'path' should be either Nic albo a list of paths to look for
    modules in.

    'prefix' jest a string to output on the front of every module name
    on output.
    """

    jeżeli path jest Nic:
        importers = iter_importers()
    inaczej:
        importers = map(get_importer, path)

    uzyskajed = {}
    dla i w importers:
        dla name, ispkg w iter_importer_modules(i, prefix):
            jeżeli name nie w uzyskajed:
                uzyskajed[name] = 1
                uzyskaj i, name, ispkg


@simplegeneric
def iter_importer_modules(importer, prefix=''):
    jeżeli nie hasattr(importer, 'iter_modules'):
        zwróć []
    zwróć importer.iter_modules(prefix)


# Implement a file walker dla the normal importlib path hook
def _iter_file_finder_modules(importer, prefix=''):
    jeżeli importer.path jest Nic albo nie os.path.isdir(importer.path):
        zwróć

    uzyskajed = {}
    zaimportuj inspect
    spróbuj:
        filenames = os.listdir(importer.path)
    wyjąwszy OSError:
        # ignore unreadable directories like zaimportuj does
        filenames = []
    filenames.sort()  # handle packages before same-named modules

    dla fn w filenames:
        modname = inspect.getmodulename(fn)
        jeżeli modname=='__init__' albo modname w uzyskajed:
            kontynuuj

        path = os.path.join(importer.path, fn)
        ispkg = Nieprawda

        jeżeli nie modname oraz os.path.isdir(path) oraz '.' nie w fn:
            modname = fn
            spróbuj:
                dircontents = os.listdir(path)
            wyjąwszy OSError:
                # ignore unreadable directories like zaimportuj does
                dircontents = []
            dla fn w dircontents:
                subname = inspect.getmodulename(fn)
                jeżeli subname=='__init__':
                    ispkg = Prawda
                    przerwij
            inaczej:
                continue    # nie a package

        jeżeli modname oraz '.' nie w modname:
            uzyskajed[modname] = 1
            uzyskaj prefix + modname, ispkg

iter_importer_modules.register(
    importlib.machinery.FileFinder, _iter_file_finder_modules)


def _import_imp():
    global imp
    przy warnings.catch_warnings():
        warnings.simplefilter('ignore', PendingDeprecationWarning)
        imp = importlib.import_module('imp')

klasa ImpImporter:
    """PEP 302 Importer that wraps Python's "classic" zaimportuj algorithm

    ImpImporter(dirname) produces a PEP 302 importer that searches that
    directory.  ImpImporter(Nic) produces a PEP 302 importer that searches
    the current sys.path, plus any modules that are frozen albo built-in.

    Note that ImpImporter does nie currently support being used by placement
    on sys.meta_path.
    """

    def __init__(self, path=Nic):
        global imp
        warnings.warn("This emulation jest deprecated, use 'importlib' instead",
             DeprecationWarning)
        _import_imp()
        self.path = path

    def find_module(self, fullname, path=Nic):
        # Note: we ignore 'path' argument since it jest only used via meta_path
        subname = fullname.split(".")[-1]
        jeżeli subname != fullname oraz self.path jest Nic:
            zwróć Nic
        jeżeli self.path jest Nic:
            path = Nic
        inaczej:
            path = [os.path.realpath(self.path)]
        spróbuj:
            file, filename, etc = imp.find_module(subname, path)
        wyjąwszy ImportError:
            zwróć Nic
        zwróć ImpLoader(fullname, file, filename, etc)

    def iter_modules(self, prefix=''):
        jeżeli self.path jest Nic albo nie os.path.isdir(self.path):
            zwróć

        uzyskajed = {}
        zaimportuj inspect
        spróbuj:
            filenames = os.listdir(self.path)
        wyjąwszy OSError:
            # ignore unreadable directories like zaimportuj does
            filenames = []
        filenames.sort()  # handle packages before same-named modules

        dla fn w filenames:
            modname = inspect.getmodulename(fn)
            jeżeli modname=='__init__' albo modname w uzyskajed:
                kontynuuj

            path = os.path.join(self.path, fn)
            ispkg = Nieprawda

            jeżeli nie modname oraz os.path.isdir(path) oraz '.' nie w fn:
                modname = fn
                spróbuj:
                    dircontents = os.listdir(path)
                wyjąwszy OSError:
                    # ignore unreadable directories like zaimportuj does
                    dircontents = []
                dla fn w dircontents:
                    subname = inspect.getmodulename(fn)
                    jeżeli subname=='__init__':
                        ispkg = Prawda
                        przerwij
                inaczej:
                    continue    # nie a package

            jeżeli modname oraz '.' nie w modname:
                uzyskajed[modname] = 1
                uzyskaj prefix + modname, ispkg


klasa ImpLoader:
    """PEP 302 Loader that wraps Python's "classic" zaimportuj algorithm
    """
    code = source = Nic

    def __init__(self, fullname, file, filename, etc):
        warnings.warn("This emulation jest deprecated, use 'importlib' instead",
                      DeprecationWarning)
        _import_imp()
        self.file = file
        self.filename = filename
        self.fullname = fullname
        self.etc = etc

    def load_module(self, fullname):
        self._reopen()
        spróbuj:
            mod = imp.load_module(fullname, self.file, self.filename, self.etc)
        w_końcu:
            jeżeli self.file:
                self.file.close()
        # Note: we don't set __loader__ because we want the module to look
        # normal; i.e. this jest just a wrapper dla standard zaimportuj machinery
        zwróć mod

    def get_data(self, pathname):
        przy open(pathname, "rb") jako file:
            zwróć file.read()

    def _reopen(self):
        jeżeli self.file oraz self.file.closed:
            mod_type = self.etc[2]
            jeżeli mod_type==imp.PY_SOURCE:
                self.file = open(self.filename, 'r')
            albo_inaczej mod_type w (imp.PY_COMPILED, imp.C_EXTENSION):
                self.file = open(self.filename, 'rb')

    def _fix_name(self, fullname):
        jeżeli fullname jest Nic:
            fullname = self.fullname
        albo_inaczej fullname != self.fullname:
            podnieś ImportError("Loader dla module %s cannot handle "
                              "module %s" % (self.fullname, fullname))
        zwróć fullname

    def is_package(self, fullname):
        fullname = self._fix_name(fullname)
        zwróć self.etc[2]==imp.PKG_DIRECTORY

    def get_code(self, fullname=Nic):
        fullname = self._fix_name(fullname)
        jeżeli self.code jest Nic:
            mod_type = self.etc[2]
            jeżeli mod_type==imp.PY_SOURCE:
                source = self.get_source(fullname)
                self.code = compile(source, self.filename, 'exec')
            albo_inaczej mod_type==imp.PY_COMPILED:
                self._reopen()
                spróbuj:
                    self.code = read_code(self.file)
                w_końcu:
                    self.file.close()
            albo_inaczej mod_type==imp.PKG_DIRECTORY:
                self.code = self._get_delegate().get_code()
        zwróć self.code

    def get_source(self, fullname=Nic):
        fullname = self._fix_name(fullname)
        jeżeli self.source jest Nic:
            mod_type = self.etc[2]
            jeżeli mod_type==imp.PY_SOURCE:
                self._reopen()
                spróbuj:
                    self.source = self.file.read()
                w_końcu:
                    self.file.close()
            albo_inaczej mod_type==imp.PY_COMPILED:
                jeżeli os.path.exists(self.filename[:-1]):
                    przy open(self.filename[:-1], 'r') jako f:
                        self.source = f.read()
            albo_inaczej mod_type==imp.PKG_DIRECTORY:
                self.source = self._get_delegate().get_source()
        zwróć self.source

    def _get_delegate(self):
        finder = ImpImporter(self.filename)
        spec = _get_spec(finder, '__init__')
        zwróć spec.loader

    def get_filename(self, fullname=Nic):
        fullname = self._fix_name(fullname)
        mod_type = self.etc[2]
        jeżeli mod_type==imp.PKG_DIRECTORY:
            zwróć self._get_delegate().get_filename()
        albo_inaczej mod_type w (imp.PY_SOURCE, imp.PY_COMPILED, imp.C_EXTENSION):
            zwróć self.filename
        zwróć Nic


spróbuj:
    zaimportuj zipimport
    z zipzaimportuj zaimportuj zipimporter

    def iter_zipimport_modules(importer, prefix=''):
        dirlist = sorted(zipimport._zip_directory_cache[importer.archive])
        _prefix = importer.prefix
        plen = len(_prefix)
        uzyskajed = {}
        zaimportuj inspect
        dla fn w dirlist:
            jeżeli nie fn.startswith(_prefix):
                kontynuuj

            fn = fn[plen:].split(os.sep)

            jeżeli len(fn)==2 oraz fn[1].startswith('__init__.py'):
                jeżeli fn[0] nie w uzyskajed:
                    uzyskajed[fn[0]] = 1
                    uzyskaj fn[0], Prawda

            jeżeli len(fn)!=1:
                kontynuuj

            modname = inspect.getmodulename(fn[0])
            jeżeli modname=='__init__':
                kontynuuj

            jeżeli modname oraz '.' nie w modname oraz modname nie w uzyskajed:
                uzyskajed[modname] = 1
                uzyskaj prefix + modname, Nieprawda

    iter_importer_modules.register(zipimporter, iter_zipimport_modules)

wyjąwszy ImportError:
    dalej


def get_importer(path_item):
    """Retrieve a PEP 302 importer dla the given path item

    The returned importer jest cached w sys.path_importer_cache
    jeżeli it was newly created by a path hook.

    The cache (or part of it) can be cleared manually jeżeli a
    rescan of sys.path_hooks jest necessary.
    """
    spróbuj:
        importer = sys.path_importer_cache[path_item]
    wyjąwszy KeyError:
        dla path_hook w sys.path_hooks:
            spróbuj:
                importer = path_hook(path_item)
                sys.path_importer_cache.setdefault(path_item, importer)
                przerwij
            wyjąwszy ImportError:
                dalej
        inaczej:
            importer = Nic
    zwróć importer


def iter_importers(fullname=""):
    """Yield PEP 302 importers dla the given module name

    If fullname contains a '.', the importers will be dla the package
    containing fullname, otherwise they will be all registered top level
    importers (i.e. those on both sys.meta_path oraz sys.path_hooks).

    If the named module jest w a package, that package jest imported jako a side
    effect of invoking this function.

    If no module name jest specified, all top level importers are produced.
    """
    jeżeli fullname.startswith('.'):
        msg = "Relative module name {!r} nie supported".format(fullname)
        podnieś ImportError(msg)
    jeżeli '.' w fullname:
        # Get the containing package's __path__
        pkg_name = fullname.rpartition(".")[0]
        pkg = importlib.import_module(pkg_name)
        path = getattr(pkg, '__path__', Nic)
        jeżeli path jest Nic:
            zwróć
    inaczej:
        uzyskaj z sys.meta_path
        path = sys.path
    dla item w path:
        uzyskaj get_importer(item)


def get_loader(module_or_name):
    """Get a PEP 302 "loader" object dla module_or_name

    Returns Nic jeżeli the module cannot be found albo imported.
    If the named module jest nie already imported, its containing package
    (jeżeli any) jest imported, w order to establish the package __path__.
    """
    jeżeli module_or_name w sys.modules:
        module_or_name = sys.modules[module_or_name]
        jeżeli module_or_name jest Nic:
            zwróć Nic
    jeżeli isinstance(module_or_name, ModuleType):
        module = module_or_name
        loader = getattr(module, '__loader__', Nic)
        jeżeli loader jest nie Nic:
            zwróć loader
        jeżeli getattr(module, '__spec__', Nic) jest Nic:
            zwróć Nic
        fullname = module.__name__
    inaczej:
        fullname = module_or_name
    zwróć find_loader(fullname)


def find_loader(fullname):
    """Find a PEP 302 "loader" object dla fullname

    This jest a backwards compatibility wrapper around
    importlib.util.find_spec that converts most failures to ImportError
    oraz only returns the loader rather than the full spec
    """
    jeżeli fullname.startswith('.'):
        msg = "Relative module name {!r} nie supported".format(fullname)
        podnieś ImportError(msg)
    spróbuj:
        spec = importlib.util.find_spec(fullname)
    wyjąwszy (ImportError, AttributeError, TypeError, ValueError) jako ex:
        # This hack fixes an impedance mismatch between pkgutil oraz
        # importlib, where the latter podnieśs other errors dla cases where
        # pkgutil previously podnieśd ImportError
        msg = "Error dopóki finding loader dla {!r} ({}: {})"
        podnieś ImportError(msg.format(fullname, type(ex), ex)) z ex
    zwróć spec.loader jeżeli spec jest nie Nic inaczej Nic


def extend_path(path, name):
    """Extend a package's path.

    Intended use jest to place the following code w a package's __init__.py:

        z pkgutil zaimportuj extend_path
        __path__ = extend_path(__path__, __name__)

    This will add to the package's __path__ all subdirectories of
    directories on sys.path named after the package.  This jest useful
    jeżeli one wants to distribute different parts of a single logical
    package jako multiple directories.

    It also looks dla *.pkg files beginning where * matches the name
    argument.  This feature jest similar to *.pth files (see site.py),
    wyjąwszy that it doesn't special-case lines starting przy 'import'.
    A *.pkg file jest trusted at face value: apart z checking for
    duplicates, all entries found w a *.pkg file are added to the
    path, regardless of whether they are exist the filesystem.  (This
    jest a feature.)

    If the input path jest nie a list (as jest the case dla frozen
    packages) it jest returned unchanged.  The input path jest nie
    modified; an extended copy jest returned.  Items are only appended
    to the copy at the end.

    It jest assumed that sys.path jest a sequence.  Items of sys.path that
    are nie (unicode albo 8-bit) strings referring to existing
    directories are ignored.  Unicode items of sys.path that cause
    errors when used jako filenames may cause this function to podnieś an
    exception (in line przy os.path.isdir() behavior).
    """

    jeżeli nie isinstance(path, list):
        # This could happen e.g. when this jest called z inside a
        # frozen package.  Return the path unchanged w that case.
        zwróć path

    sname_pkg = name + ".pkg"

    path = path[:] # Start przy a copy of the existing path

    parent_package, _, final_name = name.rpartition('.')
    jeżeli parent_package:
        spróbuj:
            search_path = sys.modules[parent_package].__path__
        wyjąwszy (KeyError, AttributeError):
            # We can't do anything: find_loader() returns Nic when
            # dalejed a dotted name.
            zwróć path
    inaczej:
        search_path = sys.path

    dla dir w search_path:
        jeżeli nie isinstance(dir, str):
            kontynuuj

        finder = get_importer(dir)
        jeżeli finder jest nie Nic:
            portions = []
            jeżeli hasattr(finder, 'find_spec'):
                spec = finder.find_spec(final_name)
                jeżeli spec jest nie Nic:
                    portions = spec.submodule_search_locations albo []
            # Is this finder PEP 420 compliant?
            albo_inaczej hasattr(finder, 'find_loader'):
                _, portions = finder.find_loader(final_name)

            dla portion w portions:
                # XXX This may still add duplicate entries to path on
                # case-insensitive filesystems
                jeżeli portion nie w path:
                    path.append(portion)

        # XXX Is this the right thing dla subpackages like zope.app?
        # It looks dla a file named "zope.app.pkg"
        pkgfile = os.path.join(dir, sname_pkg)
        jeżeli os.path.isfile(pkgfile):
            spróbuj:
                f = open(pkgfile)
            wyjąwszy OSError jako msg:
                sys.stderr.write("Can't open %s: %s\n" %
                                 (pkgfile, msg))
            inaczej:
                przy f:
                    dla line w f:
                        line = line.rstrip('\n')
                        jeżeli nie line albo line.startswith('#'):
                            kontynuuj
                        path.append(line) # Don't check dla existence!

    zwróć path


def get_data(package, resource):
    """Get a resource z a package.

    This jest a wrapper round the PEP 302 loader get_data API. The package
    argument should be the name of a package, w standard module format
    (foo.bar). The resource argument should be w the form of a relative
    filename, using '/' jako the path separator. The parent directory name '..'
    jest nie allowed, oraz nor jest a rooted name (starting przy a '/').

    The function returns a binary string, which jest the contents of the
    specified resource.

    For packages located w the filesystem, which have already been imported,
    this jest the rough equivalent of

        d = os.path.dirname(sys.modules[package].__file__)
        data = open(os.path.join(d, resource), 'rb').read()

    If the package cannot be located albo loaded, albo it uses a PEP 302 loader
    which does nie support get_data(), then Nic jest returned.
    """

    spec = importlib.util.find_spec(package)
    jeżeli spec jest Nic:
        zwróć Nic
    loader = spec.loader
    jeżeli loader jest Nic albo nie hasattr(loader, 'get_data'):
        zwróć Nic
    # XXX needs test
    mod = (sys.modules.get(package) albo
           importlib._bootstrap._load(spec))
    jeżeli mod jest Nic albo nie hasattr(mod, '__file__'):
        zwróć Nic

    # Modify the resource name to be compatible przy the loader.get_data
    # signature - an os.path format "filename" starting przy the dirname of
    # the package's __file__
    parts = resource.split('/')
    parts.insert(0, os.path.dirname(mod.__file__))
    resource_name = os.path.join(*parts)
    zwróć loader.get_data(resource_name)
