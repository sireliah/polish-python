"""This module provides the components needed to build your own __import__
function.  Undocumented functions are obsolete.

In most cases it jest preferred you consider using the importlib module's
functionality over this module.

"""
# (Probably) need to stay w _imp
z _imp zaimportuj (lock_held, acquire_lock, release_lock,
                  get_frozen_object, is_frozen_package,
                  init_frozen, is_builtin, is_frozen,
                  _fix_co_filename)
spróbuj:
    z _imp zaimportuj create_dynamic
wyjąwszy ImportError:
    # Platform doesn't support dynamic loading.
    create_dynamic = Nic

z importlib._bootstrap zaimportuj _ERR_MSG, _exec, _load, _builtin_from_name
z importlib._bootstrap_external zaimportuj SourcelessFileLoader

z importlib zaimportuj machinery
z importlib zaimportuj util
zaimportuj importlib
zaimportuj os
zaimportuj sys
zaimportuj tokenize
zaimportuj types
zaimportuj warnings

warnings.warn("the imp module jest deprecated w favour of importlib; "
              "see the module's documentation dla alternative uses",
              PendingDeprecationWarning, stacklevel=2)

# DEPRECATED
SEARCH_ERROR = 0
PY_SOURCE = 1
PY_COMPILED = 2
C_EXTENSION = 3
PY_RESOURCE = 4
PKG_DIRECTORY = 5
C_BUILTIN = 6
PY_FROZEN = 7
PY_CODERESOURCE = 8
IMP_HOOK = 9


def new_module(name):
    """**DEPRECATED**

    Create a new module.

    The module jest nie entered into sys.modules.

    """
    zwróć types.ModuleType(name)


def get_magic():
    """**DEPRECATED**

    Return the magic number dla .pyc files.
    """
    zwróć util.MAGIC_NUMBER


def get_tag():
    """Return the magic tag dla .pyc files."""
    zwróć sys.implementation.cache_tag


def cache_from_source(path, debug_override=Nic):
    """**DEPRECATED**

    Given the path to a .py file, zwróć the path to its .pyc file.

    The .py file does nie need to exist; this simply returns the path to the
    .pyc file calculated jako jeżeli the .py file were imported.

    If debug_override jest nie Nic, then it must be a boolean oraz jest used w
    place of sys.flags.optimize.

    If sys.implementation.cache_tag jest Nic then NotImplementedError jest podnieśd.

    """
    przy warnings.catch_warnings():
        warnings.simplefilter('ignore')
        zwróć util.cache_from_source(path, debug_override)


def source_from_cache(path):
    """**DEPRECATED**

    Given the path to a .pyc. file, zwróć the path to its .py file.

    The .pyc file does nie need to exist; this simply returns the path to
    the .py file calculated to correspond to the .pyc file.  If path does
    nie conform to PEP 3147 format, ValueError will be podnieśd. If
    sys.implementation.cache_tag jest Nic then NotImplementedError jest podnieśd.

    """
    zwróć util.source_from_cache(path)


def get_suffixes():
    """**DEPRECATED**"""
    extensions = [(s, 'rb', C_EXTENSION) dla s w machinery.EXTENSION_SUFFIXES]
    source = [(s, 'r', PY_SOURCE) dla s w machinery.SOURCE_SUFFIXES]
    bytecode = [(s, 'rb', PY_COMPILED) dla s w machinery.BYTECODE_SUFFIXES]

    zwróć extensions + source + bytecode


klasa NullImporter:

    """**DEPRECATED**

    Null zaimportuj object.

    """

    def __init__(self, path):
        jeżeli path == '':
            podnieś ImportError('empty pathname', path='')
        albo_inaczej os.path.isdir(path):
            podnieś ImportError('existing directory', path=path)

    def find_module(self, fullname):
        """Always returns Nic."""
        zwróć Nic


klasa _HackedGetData:

    """Compatibility support dla 'file' arguments of various load_*()
    functions."""

    def __init__(self, fullname, path, file=Nic):
        super().__init__(fullname, path)
        self.file = file

    def get_data(self, path):
        """Gross hack to contort loader to deal w/ load_*()'s bad API."""
        jeżeli self.file oraz path == self.path:
            jeżeli nie self.file.closed:
                file = self.file
            inaczej:
                self.file = file = open(self.path, 'r')

            przy file:
                # Technically should be returning bytes, but
                # SourceLoader.get_code() just dalejed what jest returned to
                # compile() which can handle str. And converting to bytes would
                # require figuring out the encoding to decode to oraz
                # tokenize.detect_encoding() only accepts bytes.
                zwróć file.read()
        inaczej:
            zwróć super().get_data(path)


klasa _LoadSourceCompatibility(_HackedGetData, machinery.SourceFileLoader):

    """Compatibility support dla implementing load_source()."""


def load_source(name, pathname, file=Nic):
    loader = _LoadSourceCompatibility(name, pathname, file)
    spec = util.spec_from_file_location(name, pathname, loader=loader)
    jeżeli name w sys.modules:
        module = _exec(spec, sys.modules[name])
    inaczej:
        module = _load(spec)
    # To allow reloading to potentially work, use a non-hacked loader which
    # won't rely on a now-closed file object.
    module.__loader__ = machinery.SourceFileLoader(name, pathname)
    module.__spec__.loader = module.__loader__
    zwróć module


klasa _LoadCompiledCompatibility(_HackedGetData, SourcelessFileLoader):

    """Compatibility support dla implementing load_compiled()."""


def load_compiled(name, pathname, file=Nic):
    """**DEPRECATED**"""
    loader = _LoadCompiledCompatibility(name, pathname, file)
    spec = util.spec_from_file_location(name, pathname, loader=loader)
    jeżeli name w sys.modules:
        module = _exec(spec, sys.modules[name])
    inaczej:
        module = _load(spec)
    # To allow reloading to potentially work, use a non-hacked loader which
    # won't rely on a now-closed file object.
    module.__loader__ = SourcelessFileLoader(name, pathname)
    module.__spec__.loader = module.__loader__
    zwróć module


def load_package(name, path):
    """**DEPRECATED**"""
    jeżeli os.path.isdir(path):
        extensions = (machinery.SOURCE_SUFFIXES[:] +
                      machinery.BYTECODE_SUFFIXES[:])
        dla extension w extensions:
            path = os.path.join(path, '__init__'+extension)
            jeżeli os.path.exists(path):
                przerwij
        inaczej:
            podnieś ValueError('{!r} jest nie a package'.format(path))
    spec = util.spec_from_file_location(name, path,
                                        submodule_search_locations=[])
    jeżeli name w sys.modules:
        zwróć _exec(spec, sys.modules[name])
    inaczej:
        zwróć _load(spec)


def load_module(name, file, filename, details):
    """**DEPRECATED**

    Load a module, given information returned by find_module().

    The module name must include the full package name, jeżeli any.

    """
    suffix, mode, type_ = details
    jeżeli mode oraz (nie mode.startswith(('r', 'U')) albo '+' w mode):
        podnieś ValueError('invalid file open mode {!r}'.format(mode))
    albo_inaczej file jest Nic oraz type_ w {PY_SOURCE, PY_COMPILED}:
        msg = 'file object required dla zaimportuj (type code {})'.format(type_)
        podnieś ValueError(msg)
    albo_inaczej type_ == PY_SOURCE:
        zwróć load_source(name, filename, file)
    albo_inaczej type_ == PY_COMPILED:
        zwróć load_compiled(name, filename, file)
    albo_inaczej type_ == C_EXTENSION oraz load_dynamic jest nie Nic:
        jeżeli file jest Nic:
            przy open(filename, 'rb') jako opened_file:
                zwróć load_dynamic(name, filename, opened_file)
        inaczej:
            zwróć load_dynamic(name, filename, file)
    albo_inaczej type_ == PKG_DIRECTORY:
        zwróć load_package(name, filename)
    albo_inaczej type_ == C_BUILTIN:
        zwróć init_builtin(name)
    albo_inaczej type_ == PY_FROZEN:
        zwróć init_frozen(name)
    inaczej:
        msg =  "Don't know how to zaimportuj {} (type code {})".format(name, type_)
        podnieś ImportError(msg, name=name)


def find_module(name, path=Nic):
    """**DEPRECATED**

    Search dla a module.

    If path jest omitted albo Nic, search dla a built-in, frozen albo special
    module oraz continue search w sys.path. The module name cannot
    contain '.'; to search dla a submodule of a package, dalej the
    submodule name oraz the package's __path__.

    """
    jeżeli nie isinstance(name, str):
        podnieś TypeError("'name' must be a str, nie {}".format(type(name)))
    albo_inaczej nie isinstance(path, (type(Nic), list)):
        # Backwards-compatibility
        podnieś RuntimeError("'list' must be Nic albo a list, "
                           "not {}".format(type(name)))

    jeżeli path jest Nic:
        jeżeli is_builtin(name):
            zwróć Nic, Nic, ('', '', C_BUILTIN)
        albo_inaczej is_frozen(name):
            zwróć Nic, Nic, ('', '', PY_FROZEN)
        inaczej:
            path = sys.path

    dla entry w path:
        package_directory = os.path.join(entry, name)
        dla suffix w ['.py', machinery.BYTECODE_SUFFIXES[0]]:
            package_file_name = '__init__' + suffix
            file_path = os.path.join(package_directory, package_file_name)
            jeżeli os.path.isfile(file_path):
                zwróć Nic, package_directory, ('', '', PKG_DIRECTORY)
        dla suffix, mode, type_ w get_suffixes():
            file_name = name + suffix
            file_path = os.path.join(entry, file_name)
            jeżeli os.path.isfile(file_path):
                przerwij
        inaczej:
            kontynuuj
        przerwij  # Break out of outer loop when przerwijing out of inner loop.
    inaczej:
        podnieś ImportError(_ERR_MSG.format(name), name=name)

    encoding = Nic
    jeżeli 'b' nie w mode:
        przy open(file_path, 'rb') jako file:
            encoding = tokenize.detect_encoding(file.readline)[0]
    file = open(file_path, mode, encoding=encoding)
    zwróć file, file_path, (suffix, mode, type_)


def reload(module):
    """**DEPRECATED**

    Reload the module oraz zwróć it.

    The module must have been successfully imported before.

    """
    zwróć importlib.reload(module)


def init_builtin(name):
    """**DEPRECATED**

    Load oraz zwróć a built-in module by name, albo Nic jest such module doesn't
    exist
    """
    spróbuj:
        zwróć _builtin_from_name(name)
    wyjąwszy ImportError:
        zwróć Nic


jeżeli create_dynamic:
    def load_dynamic(name, path, file=Nic):
        """**DEPRECATED**

        Load an extension module.
        """
        zaimportuj importlib.machinery
        loader = importlib.machinery.ExtensionFileLoader(name, path)

        # Issue #24748: Skip the sys.modules check w _load_module_shim;
        # always load new extension
        spec = importlib.machinery.ModuleSpec(
            name=name, loader=loader, origin=path)
        zwróć _load(spec)

inaczej:
    load_dynamic = Nic
