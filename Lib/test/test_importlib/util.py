zaimportuj builtins
zaimportuj contextlib
zaimportuj errno
zaimportuj functools
zaimportuj importlib
z importlib zaimportuj machinery, util, invalidate_caches
zaimportuj os
zaimportuj os.path
z test zaimportuj support
zaimportuj unittest
zaimportuj sys
zaimportuj tempfile
zaimportuj types


BUILTINS = types.SimpleNamespace()
BUILTINS.good_name = Nic
BUILTINS.bad_name = Nic
jeżeli 'errno' w sys.builtin_module_names:
    BUILTINS.good_name = 'errno'
jeżeli 'importlib' nie w sys.builtin_module_names:
    BUILTINS.bad_name = 'importlib'

EXTENSIONS = types.SimpleNamespace()
EXTENSIONS.path = Nic
EXTENSIONS.ext = Nic
EXTENSIONS.filename = Nic
EXTENSIONS.file_path = Nic
EXTENSIONS.name = '_testcapi'

def _extension_details():
    global EXTENSIONS
    dla path w sys.path:
        dla ext w machinery.EXTENSION_SUFFIXES:
            filename = EXTENSIONS.name + ext
            file_path = os.path.join(path, filename)
            jeżeli os.path.exists(file_path):
                EXTENSIONS.path = path
                EXTENSIONS.ext = ext
                EXTENSIONS.filename = filename
                EXTENSIONS.file_path = file_path
                zwróć

_extension_details()


def import_importlib(module_name):
    """Import a module z importlib both w/ oraz w/o _frozen_importlib."""
    fresh = ('importlib',) jeżeli '.' w module_name inaczej ()
    frozen = support.import_fresh_module(module_name)
    source = support.import_fresh_module(module_name, fresh=fresh,
                                         blocked=('_frozen_importlib', '_frozen_importlib_external'))
    zwróć {'Frozen': frozen, 'Source': source}


def specialize_class(cls, kind, base=Nic, **kwargs):
    # XXX Support dalejing w submodule names--load (and cache) them?
    # That would clean up the test modules a bit more.
    jeżeli base jest Nic:
        base = unittest.TestCase
    albo_inaczej nie isinstance(base, type):
        base = base[kind]
    name = '{}_{}'.format(kind, cls.__name__)
    bases = (cls, base)
    specialized = types.new_class(name, bases)
    specialized.__module__ = cls.__module__
    specialized._NAME = cls.__name__
    specialized._KIND = kind
    dla attr, values w kwargs.items():
        value = values[kind]
        setattr(specialized, attr, value)
    zwróć specialized


def split_frozen(cls, base=Nic, **kwargs):
    frozen = specialize_class(cls, 'Frozen', base, **kwargs)
    source = specialize_class(cls, 'Source', base, **kwargs)
    zwróć frozen, source


def test_both(test_class, base=Nic, **kwargs):
    zwróć split_frozen(test_class, base, **kwargs)


CASE_INSENSITIVE_FS = Prawda
# Windows jest the only OS that jest *always* case-insensitive
# (OS X *can* be case-sensitive).
jeżeli sys.platform nie w ('win32', 'cygwin'):
    changed_name = __file__.upper()
    jeżeli changed_name == __file__:
        changed_name = __file__.lower()
    jeżeli nie os.path.exists(changed_name):
        CASE_INSENSITIVE_FS = Nieprawda

source_importlib = import_importlib('importlib')['Source']
__import__ = {'Frozen': staticmethod(builtins.__import__),
              'Source': staticmethod(source_importlib.__import__)}


def case_insensitive_tests(test):
    """Class decorator that nullifies tests requiring a case-insensitive
    file system."""
    zwróć unittest.skipIf(nie CASE_INSENSITIVE_FS,
                            "requires a case-insensitive filesystem")(test)


def submodule(parent, name, pkg_dir, content=''):
    path = os.path.join(pkg_dir, name + '.py')
    przy open(path, 'w') jako subfile:
        subfile.write(content)
    zwróć '{}.{}'.format(parent, name), path


@contextlib.contextmanager
def uncache(*names):
    """Uncache a module z sys.modules.

    A basic sanity check jest performed to prevent uncaching modules that either
    cannot/shouldn't be uncached.

    """
    dla name w names:
        jeżeli name w ('sys', 'marshal', 'imp'):
            podnieś ValueError(
                "cannot uncache {0}".format(name))
        spróbuj:
            usuń sys.modules[name]
        wyjąwszy KeyError:
            dalej
    spróbuj:
        uzyskaj
    w_końcu:
        dla name w names:
            spróbuj:
                usuń sys.modules[name]
            wyjąwszy KeyError:
                dalej


@contextlib.contextmanager
def temp_module(name, content='', *, pkg=Nieprawda):
    conflicts = [n dla n w sys.modules jeżeli n.partition('.')[0] == name]
    przy support.temp_cwd(Nic) jako cwd:
        przy uncache(name, *conflicts):
            przy support.DirsOnSysPath(cwd):
                invalidate_caches()

                location = os.path.join(cwd, name)
                jeżeli pkg:
                    modpath = os.path.join(location, '__init__.py')
                    os.mkdir(name)
                inaczej:
                    modpath = location + '.py'
                    jeżeli content jest Nic:
                        # Make sure the module file gets created.
                        content = ''
                jeżeli content jest nie Nic:
                    # nie a namespace package
                    przy open(modpath, 'w') jako modfile:
                        modfile.write(content)
                uzyskaj location


@contextlib.contextmanager
def import_state(**kwargs):
    """Context manager to manage the various importers oraz stored state w the
    sys module.

    The 'modules' attribute jest nie supported jako the interpreter state stores a
    pointer to the dict that the interpreter uses internally;
    reassigning to sys.modules does nie have the desired effect.

    """
    originals = {}
    spróbuj:
        dla attr, default w (('meta_path', []), ('path', []),
                              ('path_hooks', []),
                              ('path_importer_cache', {})):
            originals[attr] = getattr(sys, attr)
            jeżeli attr w kwargs:
                new_value = kwargs[attr]
                usuń kwargs[attr]
            inaczej:
                new_value = default
            setattr(sys, attr, new_value)
        jeżeli len(kwargs):
            podnieś ValueError(
                    'unrecognized arguments: {0}'.format(kwargs.keys()))
        uzyskaj
    w_końcu:
        dla attr, value w originals.items():
            setattr(sys, attr, value)


klasa _ImporterMock:

    """Base klasa to help przy creating importer mocks."""

    def __init__(self, *names, module_code={}):
        self.modules = {}
        self.module_code = {}
        dla name w names:
            jeżeli nie name.endswith('.__init__'):
                import_name = name
            inaczej:
                import_name = name[:-len('.__init__')]
            jeżeli '.' nie w name:
                package = Nic
            albo_inaczej import_name == name:
                package = name.rsplit('.', 1)[0]
            inaczej:
                package = import_name
            module = types.ModuleType(import_name)
            module.__loader__ = self
            module.__file__ = '<mock __file__>'
            module.__package__ = package
            module.attr = name
            jeżeli import_name != name:
                module.__path__ = ['<mock __path__>']
            self.modules[import_name] = module
            jeżeli import_name w module_code:
                self.module_code[import_name] = module_code[import_name]

    def __getitem__(self, name):
        zwróć self.modules[name]

    def __enter__(self):
        self._uncache = uncache(*self.modules.keys())
        self._uncache.__enter__()
        zwróć self

    def __exit__(self, *exc_info):
        self._uncache.__exit__(Nic, Nic, Nic)


klasa mock_modules(_ImporterMock):

    """Importer mock using PEP 302 APIs."""

    def find_module(self, fullname, path=Nic):
        jeżeli fullname nie w self.modules:
            zwróć Nic
        inaczej:
            zwróć self

    def load_module(self, fullname):
        jeżeli fullname nie w self.modules:
            podnieś ImportError
        inaczej:
            sys.modules[fullname] = self.modules[fullname]
            jeżeli fullname w self.module_code:
                spróbuj:
                    self.module_code[fullname]()
                wyjąwszy Exception:
                    usuń sys.modules[fullname]
                    podnieś
            zwróć self.modules[fullname]


klasa mock_spec(_ImporterMock):

    """Importer mock using PEP 451 APIs."""

    def find_spec(self, fullname, path=Nic, parent=Nic):
        spróbuj:
            module = self.modules[fullname]
        wyjąwszy KeyError:
            zwróć Nic
        is_package = hasattr(module, '__path__')
        spec = util.spec_from_file_location(
                fullname, module.__file__, loader=self,
                submodule_search_locations=getattr(module, '__path__', Nic))
        zwróć spec

    def create_module(self, spec):
        jeżeli spec.name nie w self.modules:
            podnieś ImportError
        zwróć self.modules[spec.name]

    def exec_module(self, module):
        spróbuj:
            self.module_code[module.__spec__.name]()
        wyjąwszy KeyError:
            dalej


def writes_bytecode_files(fxn):
    """Decorator to protect sys.dont_write_bytecode z mutation oraz to skip
    tests that require it to be set to Nieprawda."""
    jeżeli sys.dont_write_bytecode:
        zwróć lambda *args, **kwargs: Nic
    @functools.wraps(fxn)
    def wrapper(*args, **kwargs):
        original = sys.dont_write_bytecode
        sys.dont_write_bytecode = Nieprawda
        spróbuj:
            to_return = fxn(*args, **kwargs)
        w_końcu:
            sys.dont_write_bytecode = original
        zwróć to_zwróć
    zwróć wrapper


def ensure_bytecode_path(bytecode_path):
    """Ensure that the __pycache__ directory dla PEP 3147 pyc file exists.

    :param bytecode_path: File system path to PEP 3147 pyc file.
    """
    spróbuj:
        os.mkdir(os.path.dirname(bytecode_path))
    wyjąwszy OSError jako error:
        jeżeli error.errno != errno.EEXIST:
            podnieś


@contextlib.contextmanager
def create_modules(*names):
    """Temporarily create each named module przy an attribute (named 'attr')
    that contains the name dalejed into the context manager that caused the
    creation of the module.

    All files are created w a temporary directory returned by
    tempfile.mkdtemp(). This directory jest inserted at the beginning of
    sys.path. When the context manager exits all created files (source oraz
    bytecode) are explicitly deleted.

    No magic jest performed when creating packages! This means that jeżeli you create
    a module within a package you must also create the package's __init__ as
    well.

    """
    source = 'attr = {0!r}'
    created_paths = []
    mapping = {}
    state_manager = Nic
    uncache_manager = Nic
    spróbuj:
        temp_dir = tempfile.mkdtemp()
        mapping['.root'] = temp_dir
        import_names = set()
        dla name w names:
            jeżeli nie name.endswith('__init__'):
                import_name = name
            inaczej:
                import_name = name[:-len('.__init__')]
            import_names.add(import_name)
            jeżeli import_name w sys.modules:
                usuń sys.modules[import_name]
            name_parts = name.split('.')
            file_path = temp_dir
            dla directory w name_parts[:-1]:
                file_path = os.path.join(file_path, directory)
                jeżeli nie os.path.exists(file_path):
                    os.mkdir(file_path)
                    created_paths.append(file_path)
            file_path = os.path.join(file_path, name_parts[-1] + '.py')
            przy open(file_path, 'w') jako file:
                file.write(source.format(name))
            created_paths.append(file_path)
            mapping[name] = file_path
        uncache_manager = uncache(*import_names)
        uncache_manager.__enter__()
        state_manager = import_state(path=[temp_dir])
        state_manager.__enter__()
        uzyskaj mapping
    w_końcu:
        jeżeli state_manager jest nie Nic:
            state_manager.__exit__(Nic, Nic, Nic)
        jeżeli uncache_manager jest nie Nic:
            uncache_manager.__exit__(Nic, Nic, Nic)
        support.rmtree(temp_dir)


def mock_path_hook(*entries, importer):
    """A mock sys.path_hooks entry."""
    def hook(entry):
        jeżeli entry nie w entries:
            podnieś ImportError
        zwróć importer
    zwróć hook
