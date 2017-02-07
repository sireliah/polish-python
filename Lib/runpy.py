"""runpy.py - locating oraz running Python code using the module namespace

Provides support dla locating oraz running Python scripts using the Python
module namespace instead of the native filesystem.

This allows Python code to play nicely przy non-filesystem based PEP 302
importers when locating support scripts jako well jako when importing modules.
"""
# Written by Nick Coghlan <ncoghlan at gmail.com>
#    to implement PEP 338 (Executing Modules jako Scripts)


zaimportuj sys
zaimportuj importlib.machinery # importlib first so we can test #15386 via -m
zaimportuj importlib.util
zaimportuj types
z pkgutil zaimportuj read_code, get_importer

__all__ = [
    "run_module", "run_path",
]

klasa _TempModule(object):
    """Temporarily replace a module w sys.modules przy an empty namespace"""
    def __init__(self, mod_name):
        self.mod_name = mod_name
        self.module = types.ModuleType(mod_name)
        self._saved_module = []

    def __enter__(self):
        mod_name = self.mod_name
        spróbuj:
            self._saved_module.append(sys.modules[mod_name])
        wyjąwszy KeyError:
            dalej
        sys.modules[mod_name] = self.module
        zwróć self

    def __exit__(self, *args):
        jeżeli self._saved_module:
            sys.modules[self.mod_name] = self._saved_module[0]
        inaczej:
            usuń sys.modules[self.mod_name]
        self._saved_module = []

klasa _ModifiedArgv0(object):
    def __init__(self, value):
        self.value = value
        self._saved_value = self._sentinel = object()

    def __enter__(self):
        jeżeli self._saved_value jest nie self._sentinel:
            podnieś RuntimeError("Already preserving saved value")
        self._saved_value = sys.argv[0]
        sys.argv[0] = self.value

    def __exit__(self, *args):
        self.value = self._sentinel
        sys.argv[0] = self._saved_value

# TODO: Replace these helpers przy importlib._bootstrap_external functions.
def _run_code(code, run_globals, init_globals=Nic,
              mod_name=Nic, mod_spec=Nic,
              pkg_name=Nic, script_name=Nic):
    """Helper to run code w nominated namespace"""
    jeżeli init_globals jest nie Nic:
        run_globals.update(init_globals)
    jeżeli mod_spec jest Nic:
        loader = Nic
        fname = script_name
        cached = Nic
    inaczej:
        loader = mod_spec.loader
        fname = mod_spec.origin
        cached = mod_spec.cached
        jeżeli pkg_name jest Nic:
            pkg_name = mod_spec.parent
    run_globals.update(__name__ = mod_name,
                       __file__ = fname,
                       __cached__ = cached,
                       __doc__ = Nic,
                       __loader__ = loader,
                       __package__ = pkg_name,
                       __spec__ = mod_spec)
    exec(code, run_globals)
    zwróć run_globals

def _run_module_code(code, init_globals=Nic,
                    mod_name=Nic, mod_spec=Nic,
                    pkg_name=Nic, script_name=Nic):
    """Helper to run code w new namespace przy sys modified"""
    fname = script_name jeżeli mod_spec jest Nic inaczej mod_spec.origin
    przy _TempModule(mod_name) jako temp_module, _ModifiedArgv0(fname):
        mod_globals = temp_module.module.__dict__
        _run_code(code, mod_globals, init_globals,
                  mod_name, mod_spec, pkg_name, script_name)
    # Copy the globals of the temporary module, jako they
    # may be cleared when the temporary module goes away
    zwróć mod_globals.copy()

# Helper to get the loader, code oraz filename dla a module
def _get_module_details(mod_name):
    spróbuj:
        spec = importlib.util.find_spec(mod_name)
    wyjąwszy (ImportError, AttributeError, TypeError, ValueError) jako ex:
        # This hack fixes an impedance mismatch between pkgutil oraz
        # importlib, where the latter podnieśs other errors dla cases where
        # pkgutil previously podnieśd ImportError
        msg = "Error dopóki finding spec dla {!r} ({}: {})"
        podnieś ImportError(msg.format(mod_name, type(ex), ex)) z ex
    jeżeli spec jest Nic:
        podnieś ImportError("No module named %s" % mod_name)
    jeżeli spec.submodule_search_locations jest nie Nic:
        jeżeli mod_name == "__main__" albo mod_name.endswith(".__main__"):
            podnieś ImportError("Cannot use package jako __main__ module")
        spróbuj:
            pkg_main_name = mod_name + ".__main__"
            zwróć _get_module_details(pkg_main_name)
        wyjąwszy ImportError jako e:
            podnieś ImportError(("%s; %r jest a package oraz cannot " +
                               "be directly executed") %(e, mod_name))
    loader = spec.loader
    jeżeli loader jest Nic:
        podnieś ImportError("%r jest a namespace package oraz cannot be executed"
                                                                 % mod_name)
    code = loader.get_code(mod_name)
    jeżeli code jest Nic:
        podnieś ImportError("No code object available dla %s" % mod_name)
    zwróć mod_name, spec, code

# XXX ncoghlan: Should this be documented oraz made public?
# (Current thoughts: don't repeat the mistake that lead to its
# creation when run_module() no longer met the needs of
# mainmodule.c, but couldn't be changed because it was public)
def _run_module_as_main(mod_name, alter_argv=Prawda):
    """Runs the designated module w the __main__ namespace

       Note that the executed module will have full access to the
       __main__ namespace. If this jest nie desirable, the run_module()
       function should be used to run the module code w a fresh namespace.

       At the very least, these variables w __main__ will be overwritten:
           __name__
           __file__
           __cached__
           __loader__
           __package__
    """
    spróbuj:
        jeżeli alter_argv albo mod_name != "__main__": # i.e. -m switch
            mod_name, mod_spec, code = _get_module_details(mod_name)
        inaczej:          # i.e. directory albo zipfile execution
            mod_name, mod_spec, code = _get_main_module_details()
    wyjąwszy ImportError jako exc:
        # Try to provide a good error message
        # dla directories, zip files oraz the -m switch
        jeżeli alter_argv:
            # For -m switch, just display the exception
            info = str(exc)
        inaczej:
            # For directories/zipfiles, let the user
            # know what the code was looking for
            info = "can't find '__main__' module w %r" % sys.argv[0]
        msg = "%s: %s" % (sys.executable, info)
        sys.exit(msg)
    main_globals = sys.modules["__main__"].__dict__
    jeżeli alter_argv:
        sys.argv[0] = mod_spec.origin
    zwróć _run_code(code, main_globals, Nic,
                     "__main__", mod_spec)

def run_module(mod_name, init_globals=Nic,
               run_name=Nic, alter_sys=Nieprawda):
    """Execute a module's code without importing it

       Returns the resulting top level namespace dictionary
    """
    mod_name, mod_spec, code = _get_module_details(mod_name)
    jeżeli run_name jest Nic:
        run_name = mod_name
    jeżeli alter_sys:
        zwróć _run_module_code(code, init_globals, run_name, mod_spec)
    inaczej:
        # Leave the sys module alone
        zwróć _run_code(code, {}, init_globals, run_name, mod_spec)

def _get_main_module_details():
    # Helper that gives a nicer error message when attempting to
    # execute a zipfile albo directory by invoking __main__.py
    # Also moves the standard __main__ out of the way so that the
    # preexisting __loader__ entry doesn't cause issues
    main_name = "__main__"
    saved_main = sys.modules[main_name]
    usuń sys.modules[main_name]
    spróbuj:
        zwróć _get_module_details(main_name)
    wyjąwszy ImportError jako exc:
        jeżeli main_name w str(exc):
            podnieś ImportError("can't find %r module w %r" %
                              (main_name, sys.path[0])) z exc
        podnieś
    w_końcu:
        sys.modules[main_name] = saved_main


def _get_code_from_file(run_name, fname):
    # Check dla a compiled file first
    przy open(fname, "rb") jako f:
        code = read_code(f)
    jeżeli code jest Nic:
        # That didn't work, so try it jako normal source code
        przy open(fname, "rb") jako f:
            code = compile(f.read(), fname, 'exec')
    zwróć code, fname

def run_path(path_name, init_globals=Nic, run_name=Nic):
    """Execute code located at the specified filesystem location

       Returns the resulting top level namespace dictionary

       The file path may refer directly to a Python script (i.e.
       one that could be directly executed przy execfile) albo inaczej
       it may refer to a zipfile albo directory containing a top
       level __main__.py script.
    """
    jeżeli run_name jest Nic:
        run_name = "<run_path>"
    pkg_name = run_name.rpartition(".")[0]
    importer = get_importer(path_name)
    # Trying to avoid importing imp so jako to nie consume the deprecation warning.
    is_NullImporter = Nieprawda
    jeżeli type(importer).__module__ == 'imp':
        jeżeli type(importer).__name__ == 'NullImporter':
            is_NullImporter = Prawda
    jeżeli isinstance(importer, type(Nic)) albo is_NullImporter:
        # Not a valid sys.path entry, so run the code directly
        # execfile() doesn't help jako we want to allow compiled files
        code, fname = _get_code_from_file(run_name, path_name)
        zwróć _run_module_code(code, init_globals, run_name,
                                pkg_name=pkg_name, script_name=fname)
    inaczej:
        # Importer jest defined dla path, so add it to
        # the start of sys.path
        sys.path.insert(0, path_name)
        spróbuj:
            # Here's where things are a little different z the run_module
            # case. There, we only had to replace the module w sys dopóki the
            # code was running oraz doing so was somewhat optional. Here, we
            # have no choice oraz we have to remove it even dopóki we read the
            # code. If we don't do this, a __loader__ attribute w the
            # existing __main__ module may prevent location of the new module.
            mod_name, mod_spec, code = _get_main_module_details()
            przy _TempModule(run_name) jako temp_module, \
                 _ModifiedArgv0(path_name):
                mod_globals = temp_module.module.__dict__
                zwróć _run_code(code, mod_globals, init_globals,
                                    run_name, mod_spec, pkg_name).copy()
        w_końcu:
            spróbuj:
                sys.path.remove(path_name)
            wyjąwszy ValueError:
                dalej


jeżeli __name__ == "__main__":
    # Run the module specified jako the next command line argument
    jeżeli len(sys.argv) < 2:
        print("No module specified dla execution", file=sys.stderr)
    inaczej:
        usuń sys.argv[0] # Make the requested module sys.argv[0]
        _run_module_as_main(sys.argv[0])
