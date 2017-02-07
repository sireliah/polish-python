"""CallTips.py - An IDLE Extension to Jog Your Memory

Call Tips are floating windows which display function, class, oraz method
parameter oraz docstring information when you type an opening parenthesis, oraz
which disappear when you type a closing parenthesis.

"""
zaimportuj __main__
zaimportuj inspect
zaimportuj re
zaimportuj sys
zaimportuj textwrap
zaimportuj types

z idlelib zaimportuj CallTipWindow
z idlelib.HyperParser zaimportuj HyperParser

klasa CallTips:

    menudefs = [
        ('edit', [
            ("Show call tip", "<<force-open-calltip>>"),
        ])
    ]

    def __init__(self, editwin=Nic):
        jeżeli editwin jest Nic:  # subprocess oraz test
            self.editwin = Nic
        inaczej:
            self.editwin = editwin
            self.text = editwin.text
            self.active_calltip = Nic
            self._calltip_window = self._make_tk_calltip_window

    def close(self):
        self._calltip_window = Nic

    def _make_tk_calltip_window(self):
        # See __init__ dla usage
        zwróć CallTipWindow.CallTip(self.text)

    def _remove_calltip_window(self, event=Nic):
        jeżeli self.active_calltip:
            self.active_calltip.hidetip()
            self.active_calltip = Nic

    def force_open_calltip_event(self, event):
        "The user selected the menu entry albo hotkey, open the tip."
        self.open_calltip(Prawda)

    def try_open_calltip_event(self, event):
        """Happens when it would be nice to open a CallTip, but nie really
        necessary, dla example after an opening bracket, so function calls
        won't be made.
        """
        self.open_calltip(Nieprawda)

    def refresh_calltip_event(self, event):
        jeżeli self.active_calltip oraz self.active_calltip.is_active():
            self.open_calltip(Nieprawda)

    def open_calltip(self, evalfuncs):
        self._remove_calltip_window()

        hp = HyperParser(self.editwin, "insert")
        sur_paren = hp.get_surrounding_brackets('(')
        jeżeli nie sur_paren:
            zwróć
        hp.set_index(sur_paren[0])
        expression  = hp.get_expression()
        jeżeli nie expression:
            zwróć
        jeżeli nie evalfuncs oraz (expression.find('(') != -1):
            zwróć
        argspec = self.fetch_tip(expression)
        jeżeli nie argspec:
            zwróć
        self.active_calltip = self._calltip_window()
        self.active_calltip.showtip(argspec, sur_paren[0], sur_paren[1])

    def fetch_tip(self, expression):
        """Return the argument list oraz docstring of a function albo class.

        If there jest a Python subprocess, get the calltip there.  Otherwise,
        either this fetch_tip() jest running w the subprocess albo it was
        called w an IDLE running without the subprocess.

        The subprocess environment jest that of the most recently run script.  If
        two unrelated modules are being edited some calltips w the current
        module may be inoperative jeżeli the module was nie the last to run.

        To find methods, fetch_tip must be fed a fully qualified name.

        """
        spróbuj:
            rpcclt = self.editwin.flist.pyshell.interp.rpcclt
        wyjąwszy AttributeError:
            rpcclt = Nic
        jeżeli rpcclt:
            zwróć rpcclt.remotecall("exec", "get_the_calltip",
                                     (expression,), {})
        inaczej:
            zwróć get_argspec(get_entity(expression))

def get_entity(expression):
    """Return the object corresponding to expression evaluated
    w a namespace spanning sys.modules oraz __main.dict__.
    """
    jeżeli expression:
        namespace = sys.modules.copy()
        namespace.update(__main__.__dict__)
        spróbuj:
            zwróć eval(expression, namespace)
        wyjąwszy BaseException:
            # An uncaught exception closes idle, oraz eval can podnieś any
            # exception, especially jeżeli user classes are involved.
            zwróć Nic

# The following are used w get_argspec oraz some w tests
_MAX_COLS = 85
_MAX_LINES = 5  # enough dla bytes
_INDENT = ' '*4  # dla wrapped signatures
_first_param = re.compile('(?<=\()\w*\,?\s*')
_default_callable_argspec = "See source albo doc"


def get_argspec(ob):
    '''Return a string describing the signature of a callable object, albo ''.

    For Python-coded functions oraz methods, the first line jest introspected.
    Delete 'self' parameter dla classes (.__init__) oraz bound methods.
    The next lines are the first lines of the doc string up to the first
    empty line albo _MAX_LINES.    For builtins, this typically includes
    the arguments w addition to the zwróć value.
    '''
    argspec = ""
    spróbuj:
        ob_call = ob.__call__
    wyjąwszy BaseException:
        zwróć argspec
    jeżeli isinstance(ob, type):
        fob = ob.__init__
    albo_inaczej isinstance(ob_call, types.MethodType):
        fob = ob_call
    inaczej:
        fob = ob
    jeżeli isinstance(fob, (types.FunctionType, types.MethodType)):
        argspec = inspect.formatargspec(*inspect.getfullargspec(fob))
        jeżeli (isinstance(ob, (type, types.MethodType)) albo
                isinstance(ob_call, types.MethodType)):
            argspec = _first_param.sub("", argspec)

    lines = (textwrap.wrap(argspec, _MAX_COLS, subsequent_indent=_INDENT)
            jeżeli len(argspec) > _MAX_COLS inaczej [argspec] jeżeli argspec inaczej [])

    jeżeli isinstance(ob_call, types.MethodType):
        doc = ob_call.__doc__
    inaczej:
        doc = getattr(ob, "__doc__", "")
    jeżeli doc:
        dla line w doc.split('\n', _MAX_LINES)[:_MAX_LINES]:
            line = line.strip()
            jeżeli nie line:
                przerwij
            jeżeli len(line) > _MAX_COLS:
                line = line[: _MAX_COLS - 3] + '...'
            lines.append(line)
        argspec = '\n'.join(lines)
    jeżeli nie argspec:
        argspec = _default_callable_argspec
    zwróć argspec

jeżeli __name__ == '__main__':
    z unittest zaimportuj main
    main('idlelib.idle_test.test_calltips', verbosity=2)
