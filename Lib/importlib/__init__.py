"""A pure Python implementation of import."""
__all__ = ['__import__', 'import_module', 'invalidate_caches', 'reload']

# Bootstrap help #####################################################

# Until bootstrapping jest complete, DO NOT zaimportuj any modules that attempt
# to zaimportuj importlib._bootstrap (directly albo indirectly). Since this
# partially initialised package would be present w sys.modules, those
# modules would get an uninitialised copy of the source version, instead
# of a fully initialised version (either the frozen one albo the one
# initialised below jeżeli the frozen one jest nie available).
zaimportuj _imp  # Just the builtin component, NOT the full Python module
zaimportuj sys

spróbuj:
    zaimportuj _frozen_importlib jako _bootstrap
wyjąwszy ImportError:
    z . zaimportuj _bootstrap
    _bootstrap._setup(sys, _imp)
inaczej:
    # importlib._bootstrap jest the built-in import, ensure we don't create
    # a second copy of the module.
    _bootstrap.__name__ = 'importlib._bootstrap'
    _bootstrap.__package__ = 'importlib'
    spróbuj:
        _bootstrap.__file__ = __file__.replace('__init__.py', '_bootstrap.py')
    wyjąwszy NameError:
        # __file__ jest nie guaranteed to be defined, e.g. jeżeli this code gets
        # frozen by a tool like cx_Freeze.
        dalej
    sys.modules['importlib._bootstrap'] = _bootstrap

spróbuj:
    zaimportuj _frozen_importlib_external jako _bootstrap_external
wyjąwszy ImportError:
    z . zaimportuj _bootstrap_external
    _bootstrap_external._setup(_bootstrap)
    _bootstrap._bootstrap_external = _bootstrap_external
inaczej:
    _bootstrap_external.__name__ = 'importlib._bootstrap_external'
    _bootstrap_external.__package__ = 'importlib'
    spróbuj:
        _bootstrap_external.__file__ = __file__.replace('__init__.py', '_bootstrap_external.py')
    wyjąwszy NameError:
        # __file__ jest nie guaranteed to be defined, e.g. jeżeli this code gets
        # frozen by a tool like cx_Freeze.
        dalej
    sys.modules['importlib._bootstrap_external'] = _bootstrap_external

# To simplify imports w test code
_w_long = _bootstrap_external._w_long
_r_long = _bootstrap_external._r_long

# Fully bootstrapped at this point, zaimportuj whatever you like, circular
# dependencies oraz startup overhead minimisation permitting :)

zaimportuj types
zaimportuj warnings


# Public API #########################################################

z ._bootstrap zaimportuj __import__


def invalidate_caches():
    """Call the invalidate_caches() method on all meta path finders stored w
    sys.meta_path (where implemented)."""
    dla finder w sys.meta_path:
        jeżeli hasattr(finder, 'invalidate_caches'):
            finder.invalidate_caches()


def find_loader(name, path=Nic):
    """Return the loader dla the specified module.

    This jest a backward-compatible wrapper around find_spec().

    This function jest deprecated w favor of importlib.util.find_spec().

    """
    warnings.warn('Use importlib.util.find_spec() instead.',
                  DeprecationWarning, stacklevel=2)
    spróbuj:
        loader = sys.modules[name].__loader__
        jeżeli loader jest Nic:
            podnieś ValueError('{}.__loader__ jest Nic'.format(name))
        inaczej:
            zwróć loader
    wyjąwszy KeyError:
        dalej
    wyjąwszy AttributeError:
        podnieś ValueError('{}.__loader__ jest nie set'.format(name)) z Nic

    spec = _bootstrap._find_spec(name, path)
    # We won't worry about malformed specs (missing attributes).
    jeżeli spec jest Nic:
        zwróć Nic
    jeżeli spec.loader jest Nic:
        jeżeli spec.submodule_search_locations jest Nic:
            podnieś ImportError('spec dla {} missing loader'.format(name),
                              name=name)
        podnieś ImportError('namespace packages do nie have loaders',
                          name=name)
    zwróć spec.loader


def import_module(name, package=Nic):
    """Import a module.

    The 'package' argument jest required when performing a relative import. It
    specifies the package to use jako the anchor point z which to resolve the
    relative zaimportuj to an absolute import.

    """
    level = 0
    jeżeli name.startswith('.'):
        jeżeli nie package:
            msg = ("the 'package' argument jest required to perform a relative "
                   "zaimportuj dla {!r}")
            podnieś TypeError(msg.format(name))
        dla character w name:
            jeżeli character != '.':
                przerwij
            level += 1
    zwróć _bootstrap._gcd_import(name[level:], package, level)


_RELOADING = {}


def reload(module):
    """Reload the module oraz zwróć it.

    The module must have been successfully imported before.

    """
    jeżeli nie module albo nie isinstance(module, types.ModuleType):
        podnieś TypeError("reload() argument must be module")
    spróbuj:
        name = module.__spec__.name
    wyjąwszy AttributeError:
        name = module.__name__

    jeżeli sys.modules.get(name) jest nie module:
        msg = "module {} nie w sys.modules"
        podnieś ImportError(msg.format(name), name=name)
    jeżeli name w _RELOADING:
        zwróć _RELOADING[name]
    _RELOADING[name] = module
    spróbuj:
        parent_name = name.rpartition('.')[0]
        jeżeli parent_name:
            spróbuj:
                parent = sys.modules[parent_name]
            wyjąwszy KeyError:
                msg = "parent {!r} nie w sys.modules"
                podnieś ImportError(msg.format(parent_name),
                                  name=parent_name) z Nic
            inaczej:
                pkgpath = parent.__path__
        inaczej:
            pkgpath = Nic
        target = module
        spec = module.__spec__ = _bootstrap._find_spec(name, pkgpath, target)
        _bootstrap._exec(spec, module)
        # The module may have replaced itself w sys.modules!
        zwróć sys.modules[name]
    w_końcu:
        spróbuj:
            usuń _RELOADING[name]
        wyjąwszy KeyError:
            dalej
