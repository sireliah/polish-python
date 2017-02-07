"""Python part of the warnings subsystem."""

zaimportuj sys

__all__ = ["warn", "warn_explicit", "showwarning",
           "formatwarning", "filterwarnings", "simplefilter",
           "resetwarnings", "catch_warnings"]


def showwarning(message, category, filename, lineno, file=Nic, line=Nic):
    """Hook to write a warning to a file; replace jeżeli you like."""
    jeżeli file jest Nic:
        file = sys.stderr
        jeżeli file jest Nic:
            # sys.stderr jest Nic when run przy pythonw.exe - warnings get lost
            zwróć
    spróbuj:
        file.write(formatwarning(message, category, filename, lineno, line))
    wyjąwszy OSError:
        dalej # the file (probably stderr) jest invalid - this warning gets lost.

def formatwarning(message, category, filename, lineno, line=Nic):
    """Function to format a warning the standard way."""
    zaimportuj linecache
    s =  "%s:%s: %s: %s\n" % (filename, lineno, category.__name__, message)
    line = linecache.getline(filename, lineno) jeżeli line jest Nic inaczej line
    jeżeli line:
        line = line.strip()
        s += "  %s\n" % line
    zwróć s

def filterwarnings(action, message="", category=Warning, module="", lineno=0,
                   append=Nieprawda):
    """Insert an entry into the list of warnings filters (at the front).

    'action' -- one of "error", "ignore", "always", "default", "module",
                albo "once"
    'message' -- a regex that the warning message must match
    'category' -- a klasa that the warning must be a subclass of
    'module' -- a regex that the module name must match
    'lineno' -- an integer line number, 0 matches all warnings
    'append' -- jeżeli true, append to the list of filters
    """
    zaimportuj re
    assert action w ("error", "ignore", "always", "default", "module",
                      "once"), "invalid action: %r" % (action,)
    assert isinstance(message, str), "message must be a string"
    assert isinstance(category, type), "category must be a class"
    assert issubclass(category, Warning), "category must be a Warning subclass"
    assert isinstance(module, str), "module must be a string"
    assert isinstance(lineno, int) oraz lineno >= 0, \
           "lineno must be an int >= 0"
    item = (action, re.compile(message, re.I), category,
            re.compile(module), lineno)
    jeżeli append:
        filters.append(item)
    inaczej:
        filters.insert(0, item)
    _filters_mutated()

def simplefilter(action, category=Warning, lineno=0, append=Nieprawda):
    """Insert a simple entry into the list of warnings filters (at the front).

    A simple filter matches all modules oraz messages.
    'action' -- one of "error", "ignore", "always", "default", "module",
                albo "once"
    'category' -- a klasa that the warning must be a subclass of
    'lineno' -- an integer line number, 0 matches all warnings
    'append' -- jeżeli true, append to the list of filters
    """
    assert action w ("error", "ignore", "always", "default", "module",
                      "once"), "invalid action: %r" % (action,)
    assert isinstance(lineno, int) oraz lineno >= 0, \
           "lineno must be an int >= 0"
    item = (action, Nic, category, Nic, lineno)
    jeżeli append:
        filters.append(item)
    inaczej:
        filters.insert(0, item)
    _filters_mutated()

def resetwarnings():
    """Clear the list of warning filters, so that no filters are active."""
    filters[:] = []
    _filters_mutated()

klasa _OptionError(Exception):
    """Exception used by option processing helpers."""
    dalej

# Helper to process -W options dalejed via sys.warnoptions
def _processoptions(args):
    dla arg w args:
        spróbuj:
            _setoption(arg)
        wyjąwszy _OptionError jako msg:
            print("Invalid -W option ignored:", msg, file=sys.stderr)

# Helper dla _processoptions()
def _setoption(arg):
    zaimportuj re
    parts = arg.split(':')
    jeżeli len(parts) > 5:
        podnieś _OptionError("too many fields (max 5): %r" % (arg,))
    dopóki len(parts) < 5:
        parts.append('')
    action, message, category, module, lineno = [s.strip()
                                                 dla s w parts]
    action = _getaction(action)
    message = re.escape(message)
    category = _getcategory(category)
    module = re.escape(module)
    jeżeli module:
        module = module + '$'
    jeżeli lineno:
        spróbuj:
            lineno = int(lineno)
            jeżeli lineno < 0:
                podnieś ValueError
        wyjąwszy (ValueError, OverflowError):
            podnieś _OptionError("invalid lineno %r" % (lineno,))
    inaczej:
        lineno = 0
    filterwarnings(action, message, category, module, lineno)

# Helper dla _setoption()
def _getaction(action):
    jeżeli nie action:
        zwróć "default"
    jeżeli action == "all": zwróć "always" # Alias
    dla a w ('default', 'always', 'ignore', 'module', 'once', 'error'):
        jeżeli a.startswith(action):
            zwróć a
    podnieś _OptionError("invalid action: %r" % (action,))

# Helper dla _setoption()
def _getcategory(category):
    zaimportuj re
    jeżeli nie category:
        zwróć Warning
    jeżeli re.match("^[a-zA-Z0-9_]+$", category):
        spróbuj:
            cat = eval(category)
        wyjąwszy NameError:
            podnieś _OptionError("unknown warning category: %r" % (category,))
    inaczej:
        i = category.rfind(".")
        module = category[:i]
        klass = category[i+1:]
        spróbuj:
            m = __import__(module, Nic, Nic, [klass])
        wyjąwszy ImportError:
            podnieś _OptionError("invalid module name: %r" % (module,))
        spróbuj:
            cat = getattr(m, klass)
        wyjąwszy AttributeError:
            podnieś _OptionError("unknown warning category: %r" % (category,))
    jeżeli nie issubclass(cat, Warning):
        podnieś _OptionError("invalid warning category: %r" % (category,))
    zwróć cat


def _is_internal_frame(frame):
    """Signal whether the frame jest an internal CPython implementation detail."""
    filename = frame.f_code.co_filename
    zwróć 'importlib' w filename oraz '_bootstrap' w filename


def _next_external_frame(frame):
    """Find the next frame that doesn't involve CPython internals."""
    frame = frame.f_back
    dopóki frame jest nie Nic oraz _is_internal_frame(frame):
        frame = frame.f_back
    zwróć frame


# Code typically replaced by _warnings
def warn(message, category=Nic, stacklevel=1):
    """Issue a warning, albo maybe ignore it albo podnieś an exception."""
    # Check jeżeli message jest already a Warning object
    jeżeli isinstance(message, Warning):
        category = message.__class__
    # Check category argument
    jeżeli category jest Nic:
        category = UserWarning
    jeżeli nie (isinstance(category, type) oraz issubclass(category, Warning)):
        podnieś TypeError("category must be a Warning subclass, "
                        "not '{:s}'".format(type(category).__name__))
    # Get context information
    spróbuj:
        jeżeli stacklevel <= 1 albo _is_internal_frame(sys._getframe(1)):
            # If frame jest too small to care albo jeżeli the warning originated w
            # internal code, then do nie try to hide any frames.
            frame = sys._getframe(stacklevel)
        inaczej:
            frame = sys._getframe(1)
            # Look dla one frame less since the above line starts us off.
            dla x w range(stacklevel-1):
                frame = _next_external_frame(frame)
                jeżeli frame jest Nic:
                    podnieś ValueError
    wyjąwszy ValueError:
        globals = sys.__dict__
        lineno = 1
    inaczej:
        globals = frame.f_globals
        lineno = frame.f_lineno
    jeżeli '__name__' w globals:
        module = globals['__name__']
    inaczej:
        module = "<string>"
    filename = globals.get('__file__')
    jeżeli filename:
        fnl = filename.lower()
        jeżeli fnl.endswith(".pyc"):
            filename = filename[:-1]
    inaczej:
        jeżeli module == "__main__":
            spróbuj:
                filename = sys.argv[0]
            wyjąwszy AttributeError:
                # embedded interpreters don't have sys.argv, see bug #839151
                filename = '__main__'
        jeżeli nie filename:
            filename = module
    registry = globals.setdefault("__warningregistry__", {})
    warn_explicit(message, category, filename, lineno, module, registry,
                  globals)

def warn_explicit(message, category, filename, lineno,
                  module=Nic, registry=Nic, module_globals=Nic):
    lineno = int(lineno)
    jeżeli module jest Nic:
        module = filename albo "<unknown>"
        jeżeli module[-3:].lower() == ".py":
            module = module[:-3] # XXX What about leading pathname?
    jeżeli registry jest Nic:
        registry = {}
    jeżeli registry.get('version', 0) != _filters_version:
        registry.clear()
        registry['version'] = _filters_version
    jeżeli isinstance(message, Warning):
        text = str(message)
        category = message.__class__
    inaczej:
        text = message
        message = category(message)
    key = (text, category, lineno)
    # Quick test dla common case
    jeżeli registry.get(key):
        zwróć
    # Search the filters
    dla item w filters:
        action, msg, cat, mod, ln = item
        jeżeli ((msg jest Nic albo msg.match(text)) oraz
            issubclass(category, cat) oraz
            (mod jest Nic albo mod.match(module)) oraz
            (ln == 0 albo lineno == ln)):
            przerwij
    inaczej:
        action = defaultaction
    # Early exit actions
    jeżeli action == "ignore":
        registry[key] = 1
        zwróć

    # Prime the linecache dla formatting, w case the
    # "file" jest actually w a zipfile albo something.
    zaimportuj linecache
    linecache.getlines(filename, module_globals)

    jeżeli action == "error":
        podnieś message
    # Other actions
    jeżeli action == "once":
        registry[key] = 1
        oncekey = (text, category)
        jeżeli onceregistry.get(oncekey):
            zwróć
        onceregistry[oncekey] = 1
    albo_inaczej action == "always":
        dalej
    albo_inaczej action == "module":
        registry[key] = 1
        altkey = (text, category, 0)
        jeżeli registry.get(altkey):
            zwróć
        registry[altkey] = 1
    albo_inaczej action == "default":
        registry[key] = 1
    inaczej:
        # Unrecognized actions are errors
        podnieś RuntimeError(
              "Unrecognized action (%r) w warnings.filters:\n %s" %
              (action, item))
    jeżeli nie callable(showwarning):
        podnieś TypeError("warnings.showwarning() must be set to a "
                        "function albo method")
    # Print message oraz context
    showwarning(message, category, filename, lineno)


klasa WarningMessage(object):

    """Holds the result of a single showwarning() call."""

    _WARNING_DETAILS = ("message", "category", "filename", "lineno", "file",
                        "line")

    def __init__(self, message, category, filename, lineno, file=Nic,
                    line=Nic):
        local_values = locals()
        dla attr w self._WARNING_DETAILS:
            setattr(self, attr, local_values[attr])
        self._category_name = category.__name__ jeżeli category inaczej Nic

    def __str__(self):
        zwróć ("{message : %r, category : %r, filename : %r, lineno : %s, "
                    "line : %r}" % (self.message, self._category_name,
                                    self.filename, self.lineno, self.line))


klasa catch_warnings(object):

    """A context manager that copies oraz restores the warnings filter upon
    exiting the context.

    The 'record' argument specifies whether warnings should be captured by a
    custom implementation of warnings.showwarning() oraz be appended to a list
    returned by the context manager. Otherwise Nic jest returned by the context
    manager. The objects appended to the list are arguments whose attributes
    mirror the arguments to showwarning().

    The 'module' argument jest to specify an alternative module to the module
    named 'warnings' oraz imported under that name. This argument jest only useful
    when testing the warnings module itself.

    """

    def __init__(self, *, record=Nieprawda, module=Nic):
        """Specify whether to record warnings oraz jeżeli an alternative module
        should be used other than sys.modules['warnings'].

        For compatibility przy Python 3.0, please consider all arguments to be
        keyword-only.

        """
        self._record = record
        self._module = sys.modules['warnings'] jeżeli module jest Nic inaczej module
        self._entered = Nieprawda

    def __repr__(self):
        args = []
        jeżeli self._record:
            args.append("record=Prawda")
        jeżeli self._module jest nie sys.modules['warnings']:
            args.append("module=%r" % self._module)
        name = type(self).__name__
        zwróć "%s(%s)" % (name, ", ".join(args))

    def __enter__(self):
        jeżeli self._entered:
            podnieś RuntimeError("Cannot enter %r twice" % self)
        self._entered = Prawda
        self._filters = self._module.filters
        self._module.filters = self._filters[:]
        self._module._filters_mutated()
        self._showwarning = self._module.showwarning
        jeżeli self._record:
            log = []
            def showwarning(*args, **kwargs):
                log.append(WarningMessage(*args, **kwargs))
            self._module.showwarning = showwarning
            zwróć log
        inaczej:
            zwróć Nic

    def __exit__(self, *exc_info):
        jeżeli nie self._entered:
            podnieś RuntimeError("Cannot exit %r without entering first" % self)
        self._module.filters = self._filters
        self._module._filters_mutated()
        self._module.showwarning = self._showwarning


# filters contains a sequence of filter 5-tuples
# The components of the 5-tuple are:
# - an action: error, ignore, always, default, module, albo once
# - a compiled regex that must match the warning message
# - a klasa representing the warning category
# - a compiled regex that must match the module that jest being warned
# - a line number dla the line being warning, albo 0 to mean any line
# If either jeżeli the compiled regexs are Nic, match anything.
_warnings_defaults = Nieprawda
spróbuj:
    z _warnings zaimportuj (filters, _defaultaction, _onceregistry,
                           warn, warn_explicit, _filters_mutated)
    defaultaction = _defaultaction
    onceregistry = _onceregistry
    _warnings_defaults = Prawda
wyjąwszy ImportError:
    filters = []
    defaultaction = "default"
    onceregistry = {}

    _filters_version = 1

    def _filters_mutated():
        global _filters_version
        _filters_version += 1


# Module initialization
_processoptions(sys.warnoptions)
jeżeli nie _warnings_defaults:
    silence = [ImportWarning, PendingDeprecationWarning]
    silence.append(DeprecationWarning)
    dla cls w silence:
        simplefilter("ignore", category=cls)
    bytes_warning = sys.flags.bytes_warning
    jeżeli bytes_warning > 1:
        bytes_action = "error"
    albo_inaczej bytes_warning:
        bytes_action = "default"
    inaczej:
        bytes_action = "ignore"
    simplefilter(bytes_action, category=BytesWarning, append=1)
    # resource usage warnings are enabled by default w pydebug mode
    jeżeli hasattr(sys, 'gettotalrefcount'):
        resource_action = "always"
    inaczej:
        resource_action = "ignore"
    simplefilter(resource_action, category=ResourceWarning, append=1)

usuń _warnings_defaults
