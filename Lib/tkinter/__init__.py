"""Wrapper functions dla Tcl/Tk.

Tkinter provides classes which allow the display, positioning oraz
control of widgets. Toplevel widgets are Tk oraz Toplevel. Other
widgets are Frame, Label, Entry, Text, Canvas, Button, Radiobutton,
Checkbutton, Scale, Listbox, Scrollbar, OptionMenu, Spinbox
LabelFrame oraz PanedWindow.

Properties of the widgets are specified przy keyword arguments.
Keyword arguments have the same name jako the corresponding resource
under Tk.

Widgets are positioned przy one of the geometry managers Place, Pack
or Grid. These managers can be called przy methods place, pack, grid
available w every Widget.

Actions are bound to events by resources (e.g. keyword argument
command) albo przy the method bind.

Example (Hello, World):
zaimportuj tkinter
z tkinter.constants zaimportuj *
tk = tkinter.Tk()
frame = tkinter.Frame(tk, relief=RIDGE, borderwidth=2)
frame.pack(fill=BOTH,expand=1)
label = tkinter.Label(frame, text="Hello, World")
label.pack(fill=X, expand=1)
button = tkinter.Button(frame,text="Exit",command=tk.destroy)
button.pack(side=BOTTOM)
tk.mainloop()
"""

zaimportuj sys

zaimportuj _tkinter # If this fails your Python may nie be configured dla Tk
TclError = _tkinter.TclError
z tkinter.constants zaimportuj *
zaimportuj re


wantobjects = 1

TkVersion = float(_tkinter.TK_VERSION)
TclVersion = float(_tkinter.TCL_VERSION)

READABLE = _tkinter.READABLE
WRITABLE = _tkinter.WRITABLE
EXCEPTION = _tkinter.EXCEPTION


_magic_re = re.compile(r'([\\{}])')
_space_re = re.compile(r'([\s])', re.ASCII)

def _join(value):
    """Internal function."""
    zwróć ' '.join(map(_stringify, value))

def _stringify(value):
    """Internal function."""
    jeżeli isinstance(value, (list, tuple)):
        jeżeli len(value) == 1:
            value = _stringify(value[0])
            jeżeli value[0] == '{':
                value = '{%s}' % value
        inaczej:
            value = '{%s}' % _join(value)
    inaczej:
        value = str(value)
        jeżeli nie value:
            value = '{}'
        albo_inaczej _magic_re.search(value):
            # add '\' before special characters oraz spaces
            value = _magic_re.sub(r'\\\1', value)
            value = _space_re.sub(r'\\\1', value)
        albo_inaczej value[0] == '"' albo _space_re.search(value):
            value = '{%s}' % value
    zwróć value

def _flatten(seq):
    """Internal function."""
    res = ()
    dla item w seq:
        jeżeli isinstance(item, (tuple, list)):
            res = res + _flatten(item)
        albo_inaczej item jest nie Nic:
            res = res + (item,)
    zwróć res

spróbuj: _flatten = _tkinter._flatten
wyjąwszy AttributeError: dalej

def _cnfmerge(cnfs):
    """Internal function."""
    jeżeli isinstance(cnfs, dict):
        zwróć cnfs
    albo_inaczej isinstance(cnfs, (type(Nic), str)):
        zwróć cnfs
    inaczej:
        cnf = {}
        dla c w _flatten(cnfs):
            spróbuj:
                cnf.update(c)
            wyjąwszy (AttributeError, TypeError) jako msg:
                print("_cnfmerge: fallback due to:", msg)
                dla k, v w c.items():
                    cnf[k] = v
        zwróć cnf

spróbuj: _cnfmerge = _tkinter._cnfmerge
wyjąwszy AttributeError: dalej

def _splitdict(tk, v, cut_minus=Prawda, conv=Nic):
    """Return a properly formatted dict built z Tcl list pairs.

    If cut_minus jest Prawda, the supposed '-' prefix will be removed from
    keys. If conv jest specified, it jest used to convert values.

    Tcl list jest expected to contain an even number of elements.
    """
    t = tk.splitlist(v)
    jeżeli len(t) % 2:
        podnieś RuntimeError('Tcl list representing a dict jest expected '
                           'to contain an even number of elements')
    it = iter(t)
    dict = {}
    dla key, value w zip(it, it):
        key = str(key)
        jeżeli cut_minus oraz key[0] == '-':
            key = key[1:]
        jeżeli conv:
            value = conv(value)
        dict[key] = value
    zwróć dict

klasa Event:
    """Container dla the properties of an event.

    Instances of this type are generated jeżeli one of the following events occurs:

    KeyPress, KeyRelease - dla keyboard events
    ButtonPress, ButtonRelease, Motion, Enter, Leave, MouseWheel - dla mouse events
    Visibility, Unmap, Map, Expose, FocusIn, FocusOut, Circulate,
    Colormap, Gravity, Reparent, Property, Destroy, Activate,
    Deactivate - dla window events.

    If a callback function dla one of these events jest registered
    using bind, bind_all, bind_class, albo tag_bind, the callback jest
    called przy an Event jako first argument. It will have the
    following attributes (in braces are the event types dla which
    the attribute jest valid):

        serial - serial number of event
    num - mouse button pressed (ButtonPress, ButtonRelease)
    focus - whether the window has the focus (Enter, Leave)
    height - height of the exposed window (Configure, Expose)
    width - width of the exposed window (Configure, Expose)
    keycode - keycode of the pressed key (KeyPress, KeyRelease)
    state - state of the event jako a number (ButtonPress, ButtonRelease,
                            Enter, KeyPress, KeyRelease,
                            Leave, Motion)
    state - state jako a string (Visibility)
    time - when the event occurred
    x - x-position of the mouse
    y - y-position of the mouse
    x_root - x-position of the mouse on the screen
             (ButtonPress, ButtonRelease, KeyPress, KeyRelease, Motion)
    y_root - y-position of the mouse on the screen
             (ButtonPress, ButtonRelease, KeyPress, KeyRelease, Motion)
    char - pressed character (KeyPress, KeyRelease)
    send_event - see X/Windows documentation
    keysym - keysym of the event jako a string (KeyPress, KeyRelease)
    keysym_num - keysym of the event jako a number (KeyPress, KeyRelease)
    type - type of the event jako a number
    widget - widget w which the event occurred
    delta - delta of wheel movement (MouseWheel)
    """
    dalej

_support_default_root = 1
_default_root = Nic

def NoDefaultRoot():
    """Inhibit setting of default root window.

    Call this function to inhibit that the first instance of
    Tk jest used dla windows without an explicit parent window.
    """
    global _support_default_root
    _support_default_root = 0
    global _default_root
    _default_root = Nic
    usuń _default_root

def _tkerror(err):
    """Internal function."""
    dalej

def _exit(code=0):
    """Internal function. Calling it will podnieś the exception SystemExit."""
    spróbuj:
        code = int(code)
    wyjąwszy ValueError:
        dalej
    podnieś SystemExit(code)

_varnum = 0
klasa Variable:
    """Class to define value holders dla e.g. buttons.

    Subclasses StringVar, IntVar, DoubleVar, BooleanVar are specializations
    that constrain the type of the value returned z get()."""
    _default = ""
    _tk = Nic
    _tclCommands = Nic
    def __init__(self, master=Nic, value=Nic, name=Nic):
        """Construct a variable

        MASTER can be given jako master widget.
        VALUE jest an optional value (defaults to "")
        NAME jest an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable oraz VALUE jest omitted
        then the existing value jest retained.
        """
        # check dla type of NAME parameter to override weird error message
        # podnieśd z Modules/_tkinter.c:SetVar like:
        # TypeError: setvar() takes exactly 3 arguments (2 given)
        jeżeli name jest nie Nic oraz nie isinstance(name, str):
            podnieś TypeError("name must be a string")
        global _varnum
        jeżeli nie master:
            master = _default_root
        self._root = master._root()
        self._tk = master.tk
        jeżeli name:
            self._name = name
        inaczej:
            self._name = 'PY_VAR' + repr(_varnum)
            _varnum += 1
        jeżeli value jest nie Nic:
            self.initialize(value)
        albo_inaczej nie self._tk.getboolean(self._tk.call("info", "exists", self._name)):
            self.initialize(self._default)
    def __del__(self):
        """Unset the variable w Tcl."""
        jeżeli self._tk jest Nic:
            zwróć
        jeżeli self._tk.getboolean(self._tk.call("info", "exists", self._name)):
            self._tk.globalunsetvar(self._name)
        jeżeli self._tclCommands jest nie Nic:
            dla name w self._tclCommands:
                #print '- Tkinter: deleted command', name
                self._tk.deletecommand(name)
            self._tclCommands = Nic
    def __str__(self):
        """Return the name of the variable w Tcl."""
        zwróć self._name
    def set(self, value):
        """Set the variable to VALUE."""
        zwróć self._tk.globalsetvar(self._name, value)
    initialize = set
    def get(self):
        """Return value of variable."""
        zwróć self._tk.globalgetvar(self._name)
    def trace_variable(self, mode, callback):
        """Define a trace callback dla the variable.

        MODE jest one of "r", "w", "u" dla read, write, undefine.
        CALLBACK must be a function which jest called when
        the variable jest read, written albo undefined.

        Return the name of the callback.
        """
        f = CallWrapper(callback, Nic, self).__call__
        cbname = repr(id(f))
        spróbuj:
            callback = callback.__func__
        wyjąwszy AttributeError:
            dalej
        spróbuj:
            cbname = cbname + callback.__name__
        wyjąwszy AttributeError:
            dalej
        self._tk.createcommand(cbname, f)
        jeżeli self._tclCommands jest Nic:
            self._tclCommands = []
        self._tclCommands.append(cbname)
        self._tk.call("trace", "variable", self._name, mode, cbname)
        zwróć cbname
    trace = trace_variable
    def trace_vdelete(self, mode, cbname):
        """Delete the trace callback dla a variable.

        MODE jest one of "r", "w", "u" dla read, write, undefine.
        CBNAME jest the name of the callback returned z trace_variable albo trace.
        """
        self._tk.call("trace", "vdelete", self._name, mode, cbname)
        self._tk.deletecommand(cbname)
        spróbuj:
            self._tclCommands.remove(cbname)
        wyjąwszy ValueError:
            dalej
    def trace_vinfo(self):
        """Return all trace callback information."""
        zwróć [self._tk.split(x) dla x w self._tk.splitlist(
            self._tk.call("trace", "vinfo", self._name))]
    def __eq__(self, other):
        """Comparison dla equality (==).

        Note: jeżeli the Variable's master matters to behavior
        also compare self._master == other._master
        """
        zwróć self.__class__.__name__ == other.__class__.__name__ \
            oraz self._name == other._name

klasa StringVar(Variable):
    """Value holder dla strings variables."""
    _default = ""
    def __init__(self, master=Nic, value=Nic, name=Nic):
        """Construct a string variable.

        MASTER can be given jako master widget.
        VALUE jest an optional value (defaults to "")
        NAME jest an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable oraz VALUE jest omitted
        then the existing value jest retained.
        """
        Variable.__init__(self, master, value, name)

    def get(self):
        """Return value of variable jako string."""
        value = self._tk.globalgetvar(self._name)
        jeżeli isinstance(value, str):
            zwróć value
        zwróć str(value)

klasa IntVar(Variable):
    """Value holder dla integer variables."""
    _default = 0
    def __init__(self, master=Nic, value=Nic, name=Nic):
        """Construct an integer variable.

        MASTER can be given jako master widget.
        VALUE jest an optional value (defaults to 0)
        NAME jest an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable oraz VALUE jest omitted
        then the existing value jest retained.
        """
        Variable.__init__(self, master, value, name)

    def get(self):
        """Return the value of the variable jako an integer."""
        zwróć self._tk.getint(self._tk.globalgetvar(self._name))

klasa DoubleVar(Variable):
    """Value holder dla float variables."""
    _default = 0.0
    def __init__(self, master=Nic, value=Nic, name=Nic):
        """Construct a float variable.

        MASTER can be given jako master widget.
        VALUE jest an optional value (defaults to 0.0)
        NAME jest an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable oraz VALUE jest omitted
        then the existing value jest retained.
        """
        Variable.__init__(self, master, value, name)

    def get(self):
        """Return the value of the variable jako a float."""
        zwróć self._tk.getdouble(self._tk.globalgetvar(self._name))

klasa BooleanVar(Variable):
    """Value holder dla boolean variables."""
    _default = Nieprawda
    def __init__(self, master=Nic, value=Nic, name=Nic):
        """Construct a boolean variable.

        MASTER can be given jako master widget.
        VALUE jest an optional value (defaults to Nieprawda)
        NAME jest an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable oraz VALUE jest omitted
        then the existing value jest retained.
        """
        Variable.__init__(self, master, value, name)

    def set(self, value):
        """Set the variable to VALUE."""
        zwróć self._tk.globalsetvar(self._name, self._tk.getboolean(value))
    initialize = set

    def get(self):
        """Return the value of the variable jako a bool."""
        spróbuj:
            zwróć self._tk.getboolean(self._tk.globalgetvar(self._name))
        wyjąwszy TclError:
            podnieś ValueError("invalid literal dla getboolean()")

def mainloop(n=0):
    """Run the main loop of Tcl."""
    _default_root.tk.mainloop(n)

getint = int

getdouble = float

def getboolean(s):
    """Convert true oraz false to integer values 1 oraz 0."""
    spróbuj:
        zwróć _default_root.tk.getboolean(s)
    wyjąwszy TclError:
        podnieś ValueError("invalid literal dla getboolean()")

# Methods defined on both toplevel oraz interior widgets
klasa Misc:
    """Internal class.

    Base klasa which defines methods common dla interior widgets."""

    # XXX font command?
    _tclCommands = Nic
    def destroy(self):
        """Internal function.

        Delete all Tcl commands created for
        this widget w the Tcl interpreter."""
        jeżeli self._tclCommands jest nie Nic:
            dla name w self._tclCommands:
                #print '- Tkinter: deleted command', name
                self.tk.deletecommand(name)
            self._tclCommands = Nic
    def deletecommand(self, name):
        """Internal function.

        Delete the Tcl command provided w NAME."""
        #print '- Tkinter: deleted command', name
        self.tk.deletecommand(name)
        spróbuj:
            self._tclCommands.remove(name)
        wyjąwszy ValueError:
            dalej
    def tk_strictMotif(self, boolean=Nic):
        """Set Tcl internal variable, whether the look oraz feel
        should adhere to Motif.

        A parameter of 1 means adhere to Motjeżeli (e.g. no color
        change jeżeli mouse dalejes over slider).
        Returns the set value."""
        zwróć self.tk.getboolean(self.tk.call(
            'set', 'tk_strictMotif', boolean))
    def tk_bisque(self):
        """Change the color scheme to light brown jako used w Tk 3.6 oraz before."""
        self.tk.call('tk_bisque')
    def tk_setPalette(self, *args, **kw):
        """Set a new color scheme dla all widget elements.

        A single color jako argument will cause that all colors of Tk
        widget elements are derived z this.
        Alternatively several keyword parameters oraz its associated
        colors can be given. The following keywords are valid:
        activeBackground, foreground, selectColor,
        activeForeground, highlightBackground, selectBackground,
        background, highlightColor, selectForeground,
        disabledForeground, insertBackground, troughColor."""
        self.tk.call(('tk_setPalette',)
              + _flatten(args) + _flatten(list(kw.items())))
    def tk_menuBar(self, *args):
        """Do nie use. Needed w Tk 3.6 oraz earlier."""
        # obsolete since Tk 4.0
        zaimportuj warnings
        warnings.warn('tk_menuBar() does nothing oraz will be removed w 3.6',
                      DeprecationWarning, stacklevel=2)
    def wait_variable(self, name='PY_VAR'):
        """Wait until the variable jest modified.

        A parameter of type IntVar, StringVar, DoubleVar albo
        BooleanVar must be given."""
        self.tk.call('tkwait', 'variable', name)
    waitvar = wait_variable # XXX b/w compat
    def wait_window(self, window=Nic):
        """Wait until a WIDGET jest destroyed.

        If no parameter jest given self jest used."""
        jeżeli window jest Nic:
            window = self
        self.tk.call('tkwait', 'window', window._w)
    def wait_visibility(self, window=Nic):
        """Wait until the visibility of a WIDGET changes
        (e.g. it appears).

        If no parameter jest given self jest used."""
        jeżeli window jest Nic:
            window = self
        self.tk.call('tkwait', 'visibility', window._w)
    def setvar(self, name='PY_VAR', value='1'):
        """Set Tcl variable NAME to VALUE."""
        self.tk.setvar(name, value)
    def getvar(self, name='PY_VAR'):
        """Return value of Tcl variable NAME."""
        zwróć self.tk.getvar(name)

    def getint(self, s):
        spróbuj:
            zwróć self.tk.getint(s)
        wyjąwszy TclError jako exc:
            podnieś ValueError(str(exc))

    def getdouble(self, s):
        spróbuj:
            zwróć self.tk.getdouble(s)
        wyjąwszy TclError jako exc:
            podnieś ValueError(str(exc))

    def getboolean(self, s):
        """Return a boolean value dla Tcl boolean values true oraz false given jako parameter."""
        spróbuj:
            zwróć self.tk.getboolean(s)
        wyjąwszy TclError:
            podnieś ValueError("invalid literal dla getboolean()")

    def focus_set(self):
        """Direct input focus to this widget.

        If the application currently does nie have the focus
        this widget will get the focus jeżeli the application gets
        the focus through the window manager."""
        self.tk.call('focus', self._w)
    focus = focus_set # XXX b/w compat?
    def focus_force(self):
        """Direct input focus to this widget even jeżeli the
        application does nie have the focus. Use with
        caution!"""
        self.tk.call('focus', '-force', self._w)
    def focus_get(self):
        """Return the widget which has currently the focus w the
        application.

        Use focus_displayof to allow working przy several
        displays. Return Nic jeżeli application does nie have
        the focus."""
        name = self.tk.call('focus')
        jeżeli name == 'none' albo nie name: zwróć Nic
        zwróć self._nametowidget(name)
    def focus_displayof(self):
        """Return the widget which has currently the focus on the
        display where this widget jest located.

        Return Nic jeżeli the application does nie have the focus."""
        name = self.tk.call('focus', '-displayof', self._w)
        jeżeli name == 'none' albo nie name: zwróć Nic
        zwróć self._nametowidget(name)
    def focus_lastfor(self):
        """Return the widget which would have the focus jeżeli top level
        dla this widget gets the focus z the window manager."""
        name = self.tk.call('focus', '-lastfor', self._w)
        jeżeli name == 'none' albo nie name: zwróć Nic
        zwróć self._nametowidget(name)
    def tk_focusFollowsMouse(self):
        """The widget under mouse will get automatically focus. Can nie
        be disabled easily."""
        self.tk.call('tk_focusFollowsMouse')
    def tk_focusNext(self):
        """Return the next widget w the focus order which follows
        widget which has currently the focus.

        The focus order first goes to the next child, then to
        the children of the child recursively oraz then to the
        next sibling which jest higher w the stacking order.  A
        widget jest omitted jeżeli it has the takefocus resource set
        to 0."""
        name = self.tk.call('tk_focusNext', self._w)
        jeżeli nie name: zwróć Nic
        zwróć self._nametowidget(name)
    def tk_focusPrev(self):
        """Return previous widget w the focus order. See tk_focusNext dla details."""
        name = self.tk.call('tk_focusPrev', self._w)
        jeżeli nie name: zwróć Nic
        zwróć self._nametowidget(name)
    def after(self, ms, func=Nic, *args):
        """Call function once after given time.

        MS specifies the time w milliseconds. FUNC gives the
        function which shall be called. Additional parameters
        are given jako parameters to the function call.  Return
        identifier to cancel scheduling przy after_cancel."""
        jeżeli nie func:
            # I'd rather use time.sleep(ms*0.001)
            self.tk.call('after', ms)
        inaczej:
            def callit():
                spróbuj:
                    func(*args)
                w_końcu:
                    spróbuj:
                        self.deletecommand(name)
                    wyjąwszy TclError:
                        dalej
            callit.__name__ = func.__name__
            name = self._register(callit)
            zwróć self.tk.call('after', ms, name)
    def after_idle(self, func, *args):
        """Call FUNC once jeżeli the Tcl main loop has no event to
        process.

        Return an identifier to cancel the scheduling with
        after_cancel."""
        zwróć self.after('idle', func, *args)
    def after_cancel(self, id):
        """Cancel scheduling of function identified przy ID.

        Identifier returned by after albo after_idle must be
        given jako first parameter."""
        spróbuj:
            data = self.tk.call('after', 'info', id)
            # In Tk 8.3, splitlist returns: (script, type)
            # In Tk 8.4, splitlist may zwróć (script, type) albo (script,)
            script = self.tk.splitlist(data)[0]
            self.deletecommand(script)
        wyjąwszy TclError:
            dalej
        self.tk.call('after', 'cancel', id)
    def bell(self, displayof=0):
        """Ring a display's bell."""
        self.tk.call(('bell',) + self._displayof(displayof))

    # Clipboard handling:
    def clipboard_get(self, **kw):
        """Retrieve data z the clipboard on window's display.

        The window keyword defaults to the root window of the Tkinter
        application.

        The type keyword specifies the form w which the data jest
        to be returned oraz should be an atom name such jako STRING
        albo FILE_NAME.  Type defaults to STRING, wyjąwszy on X11, where the default
        jest to try UTF8_STRING oraz fall back to STRING.

        This command jest equivalent to:

        selection_get(CLIPBOARD)
        """
        jeżeli 'type' nie w kw oraz self._windowingsystem == 'x11':
            spróbuj:
                kw['type'] = 'UTF8_STRING'
                zwróć self.tk.call(('clipboard', 'get') + self._options(kw))
            wyjąwszy TclError:
                usuń kw['type']
        zwróć self.tk.call(('clipboard', 'get') + self._options(kw))

    def clipboard_clear(self, **kw):
        """Clear the data w the Tk clipboard.

        A widget specified dla the optional displayof keyword
        argument specifies the target display."""
        jeżeli 'displayof' nie w kw: kw['displayof'] = self._w
        self.tk.call(('clipboard', 'clear') + self._options(kw))
    def clipboard_append(self, string, **kw):
        """Append STRING to the Tk clipboard.

        A widget specified at the optional displayof keyword
        argument specifies the target display. The clipboard
        can be retrieved przy selection_get."""
        jeżeli 'displayof' nie w kw: kw['displayof'] = self._w
        self.tk.call(('clipboard', 'append') + self._options(kw)
              + ('--', string))
    # XXX grab current w/o window argument
    def grab_current(self):
        """Return widget which has currently the grab w this application
        albo Nic."""
        name = self.tk.call('grab', 'current', self._w)
        jeżeli nie name: zwróć Nic
        zwróć self._nametowidget(name)
    def grab_release(self):
        """Release grab dla this widget jeżeli currently set."""
        self.tk.call('grab', 'release', self._w)
    def grab_set(self):
        """Set grab dla this widget.

        A grab directs all events to this oraz descendant
        widgets w the application."""
        self.tk.call('grab', 'set', self._w)
    def grab_set_global(self):
        """Set global grab dla this widget.

        A global grab directs all events to this oraz
        descendant widgets on the display. Use przy caution -
        other applications do nie get events anymore."""
        self.tk.call('grab', 'set', '-global', self._w)
    def grab_status(self):
        """Return Nic, "local" albo "global" jeżeli this widget has
        no, a local albo a global grab."""
        status = self.tk.call('grab', 'status', self._w)
        jeżeli status == 'none': status = Nic
        zwróć status
    def option_add(self, pattern, value, priority = Nic):
        """Set a VALUE (second parameter) dla an option
        PATTERN (first parameter).

        An optional third parameter gives the numeric priority
        (defaults to 80)."""
        self.tk.call('option', 'add', pattern, value, priority)
    def option_clear(self):
        """Clear the option database.

        It will be reloaded jeżeli option_add jest called."""
        self.tk.call('option', 'clear')
    def option_get(self, name, className):
        """Return the value dla an option NAME dla this widget
        przy CLASSNAME.

        Values przy higher priority override lower values."""
        zwróć self.tk.call('option', 'get', self._w, name, className)
    def option_readfile(self, fileName, priority = Nic):
        """Read file FILENAME into the option database.

        An optional second parameter gives the numeric
        priority."""
        self.tk.call('option', 'readfile', fileName, priority)
    def selection_clear(self, **kw):
        """Clear the current X selection."""
        jeżeli 'displayof' nie w kw: kw['displayof'] = self._w
        self.tk.call(('selection', 'clear') + self._options(kw))
    def selection_get(self, **kw):
        """Return the contents of the current X selection.

        A keyword parameter selection specifies the name of
        the selection oraz defaults to PRIMARY.  A keyword
        parameter displayof specifies a widget on the display
        to use. A keyword parameter type specifies the form of data to be
        fetched, defaulting to STRING wyjąwszy on X11, where UTF8_STRING jest tried
        before STRING."""
        jeżeli 'displayof' nie w kw: kw['displayof'] = self._w
        jeżeli 'type' nie w kw oraz self._windowingsystem == 'x11':
            spróbuj:
                kw['type'] = 'UTF8_STRING'
                zwróć self.tk.call(('selection', 'get') + self._options(kw))
            wyjąwszy TclError:
                usuń kw['type']
        zwróć self.tk.call(('selection', 'get') + self._options(kw))
    def selection_handle(self, command, **kw):
        """Specify a function COMMAND to call jeżeli the X
        selection owned by this widget jest queried by another
        application.

        This function must zwróć the contents of the
        selection. The function will be called przy the
        arguments OFFSET oraz LENGTH which allows the chunking
        of very long selections. The following keyword
        parameters can be provided:
        selection - name of the selection (default PRIMARY),
        type - type of the selection (e.g. STRING, FILE_NAME)."""
        name = self._register(command)
        self.tk.call(('selection', 'handle') + self._options(kw)
              + (self._w, name))
    def selection_own(self, **kw):
        """Become owner of X selection.

        A keyword parameter selection specifies the name of
        the selection (default PRIMARY)."""
        self.tk.call(('selection', 'own') +
                 self._options(kw) + (self._w,))
    def selection_own_get(self, **kw):
        """Return owner of X selection.

        The following keyword parameter can
        be provided:
        selection - name of the selection (default PRIMARY),
        type - type of the selection (e.g. STRING, FILE_NAME)."""
        jeżeli 'displayof' nie w kw: kw['displayof'] = self._w
        name = self.tk.call(('selection', 'own') + self._options(kw))
        jeżeli nie name: zwróć Nic
        zwróć self._nametowidget(name)
    def send(self, interp, cmd, *args):
        """Send Tcl command CMD to different interpreter INTERP to be executed."""
        zwróć self.tk.call(('send', interp, cmd) + args)
    def lower(self, belowThis=Nic):
        """Lower this widget w the stacking order."""
        self.tk.call('lower', self._w, belowThis)
    def tkraise(self, aboveThis=Nic):
        """Raise this widget w the stacking order."""
        self.tk.call('raise', self._w, aboveThis)
    lift = tkraise
    def winfo_atom(self, name, displayof=0):
        """Return integer which represents atom NAME."""
        args = ('winfo', 'atom') + self._displayof(displayof) + (name,)
        zwróć self.tk.getint(self.tk.call(args))
    def winfo_atomname(self, id, displayof=0):
        """Return name of atom przy identifier ID."""
        args = ('winfo', 'atomname') \
               + self._displayof(displayof) + (id,)
        zwróć self.tk.call(args)
    def winfo_cells(self):
        """Return number of cells w the colormap dla this widget."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'cells', self._w))
    def winfo_children(self):
        """Return a list of all widgets which are children of this widget."""
        result = []
        dla child w self.tk.splitlist(
            self.tk.call('winfo', 'children', self._w)):
            spróbuj:
                # Tcl sometimes returns extra windows, e.g. for
                # menus; those need to be skipped
                result.append(self._nametowidget(child))
            wyjąwszy KeyError:
                dalej
        zwróć result

    def winfo_class(self):
        """Return window klasa name of this widget."""
        zwróć self.tk.call('winfo', 'class', self._w)
    def winfo_colormapfull(self):
        """Return true jeżeli at the last color request the colormap was full."""
        zwróć self.tk.getboolean(
            self.tk.call('winfo', 'colormapfull', self._w))
    def winfo_containing(self, rootX, rootY, displayof=0):
        """Return the widget which jest at the root coordinates ROOTX, ROOTY."""
        args = ('winfo', 'containing') \
               + self._displayof(displayof) + (rootX, rootY)
        name = self.tk.call(args)
        jeżeli nie name: zwróć Nic
        zwróć self._nametowidget(name)
    def winfo_depth(self):
        """Return the number of bits per pixel."""
        zwróć self.tk.getint(self.tk.call('winfo', 'depth', self._w))
    def winfo_exists(self):
        """Return true jeżeli this widget exists."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'exists', self._w))
    def winfo_fpixels(self, number):
        """Return the number of pixels dla the given distance NUMBER
        (e.g. "3c") jako float."""
        zwróć self.tk.getdouble(self.tk.call(
            'winfo', 'fpixels', self._w, number))
    def winfo_geometry(self):
        """Return geometry string dla this widget w the form "widthxheight+X+Y"."""
        zwróć self.tk.call('winfo', 'geometry', self._w)
    def winfo_height(self):
        """Return height of this widget."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'height', self._w))
    def winfo_id(self):
        """Return identifier ID dla this widget."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'id', self._w))
    def winfo_interps(self, displayof=0):
        """Return the name of all Tcl interpreters dla this display."""
        args = ('winfo', 'interps') + self._displayof(displayof)
        zwróć self.tk.splitlist(self.tk.call(args))
    def winfo_ismapped(self):
        """Return true jeżeli this widget jest mapped."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'ismapped', self._w))
    def winfo_manager(self):
        """Return the window mananger name dla this widget."""
        zwróć self.tk.call('winfo', 'manager', self._w)
    def winfo_name(self):
        """Return the name of this widget."""
        zwróć self.tk.call('winfo', 'name', self._w)
    def winfo_parent(self):
        """Return the name of the parent of this widget."""
        zwróć self.tk.call('winfo', 'parent', self._w)
    def winfo_pathname(self, id, displayof=0):
        """Return the pathname of the widget given by ID."""
        args = ('winfo', 'pathname') \
               + self._displayof(displayof) + (id,)
        zwróć self.tk.call(args)
    def winfo_pixels(self, number):
        """Rounded integer value of winfo_fpixels."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'pixels', self._w, number))
    def winfo_pointerx(self):
        """Return the x coordinate of the pointer on the root window."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'pointerx', self._w))
    def winfo_pointerxy(self):
        """Return a tuple of x oraz y coordinates of the pointer on the root window."""
        zwróć self._getints(
            self.tk.call('winfo', 'pointerxy', self._w))
    def winfo_pointery(self):
        """Return the y coordinate of the pointer on the root window."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'pointery', self._w))
    def winfo_reqheight(self):
        """Return requested height of this widget."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'reqheight', self._w))
    def winfo_reqwidth(self):
        """Return requested width of this widget."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'reqwidth', self._w))
    def winfo_rgb(self, color):
        """Return tuple of decimal values dla red, green, blue for
        COLOR w this widget."""
        zwróć self._getints(
            self.tk.call('winfo', 'rgb', self._w, color))
    def winfo_rootx(self):
        """Return x coordinate of upper left corner of this widget on the
        root window."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'rootx', self._w))
    def winfo_rooty(self):
        """Return y coordinate of upper left corner of this widget on the
        root window."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'rooty', self._w))
    def winfo_screen(self):
        """Return the screen name of this widget."""
        zwróć self.tk.call('winfo', 'screen', self._w)
    def winfo_screencells(self):
        """Return the number of the cells w the colormap of the screen
        of this widget."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'screencells', self._w))
    def winfo_screendepth(self):
        """Return the number of bits per pixel of the root window of the
        screen of this widget."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'screendepth', self._w))
    def winfo_screenheight(self):
        """Return the number of pixels of the height of the screen of this widget
        w pixel."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'screenheight', self._w))
    def winfo_screenmmheight(self):
        """Return the number of pixels of the height of the screen of
        this widget w mm."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'screenmmheight', self._w))
    def winfo_screenmmwidth(self):
        """Return the number of pixels of the width of the screen of
        this widget w mm."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'screenmmwidth', self._w))
    def winfo_screenvisual(self):
        """Return one of the strings directcolor, grayscale, pseudocolor,
        staticcolor, staticgray, albo truecolor dla the default
        colormousuń of this screen."""
        zwróć self.tk.call('winfo', 'screenvisual', self._w)
    def winfo_screenwidth(self):
        """Return the number of pixels of the width of the screen of
        this widget w pixel."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'screenwidth', self._w))
    def winfo_server(self):
        """Return information of the X-Server of the screen of this widget w
        the form "XmajorRminor vendor vendorVersion"."""
        zwróć self.tk.call('winfo', 'server', self._w)
    def winfo_toplevel(self):
        """Return the toplevel widget of this widget."""
        zwróć self._nametowidget(self.tk.call(
            'winfo', 'toplevel', self._w))
    def winfo_viewable(self):
        """Return true jeżeli the widget oraz all its higher ancestors are mapped."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'viewable', self._w))
    def winfo_visual(self):
        """Return one of the strings directcolor, grayscale, pseudocolor,
        staticcolor, staticgray, albo truecolor dla the
        colormousuń of this widget."""
        zwróć self.tk.call('winfo', 'visual', self._w)
    def winfo_visualid(self):
        """Return the X identifier dla the visual dla this widget."""
        zwróć self.tk.call('winfo', 'visualid', self._w)
    def winfo_visualsavailable(self, includeids=0):
        """Return a list of all visuals available dla the screen
        of this widget.

        Each item w the list consists of a visual name (see winfo_visual), a
        depth oraz jeżeli INCLUDEIDS=1 jest given also the X identifier."""
        data = self.tk.split(
            self.tk.call('winfo', 'visualsavailable', self._w,
                     includeids oraz 'includeids' albo Nic))
        jeżeli isinstance(data, str):
            data = [self.tk.split(data)]
        zwróć [self.__winfo_parseitem(x) dla x w  data]
    def __winfo_parseitem(self, t):
        """Internal function."""
        zwróć t[:1] + tuple(map(self.__winfo_getint, t[1:]))
    def __winfo_getint(self, x):
        """Internal function."""
        zwróć int(x, 0)
    def winfo_vrootheight(self):
        """Return the height of the virtual root window associated przy this
        widget w pixels. If there jest no virtual root window zwróć the
        height of the screen."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'vrootheight', self._w))
    def winfo_vrootwidth(self):
        """Return the width of the virtual root window associated przy this
        widget w pixel. If there jest no virtual root window zwróć the
        width of the screen."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'vrootwidth', self._w))
    def winfo_vrootx(self):
        """Return the x offset of the virtual root relative to the root
        window of the screen of this widget."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'vrootx', self._w))
    def winfo_vrooty(self):
        """Return the y offset of the virtual root relative to the root
        window of the screen of this widget."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'vrooty', self._w))
    def winfo_width(self):
        """Return the width of this widget."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'width', self._w))
    def winfo_x(self):
        """Return the x coordinate of the upper left corner of this widget
        w the parent."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'x', self._w))
    def winfo_y(self):
        """Return the y coordinate of the upper left corner of this widget
        w the parent."""
        zwróć self.tk.getint(
            self.tk.call('winfo', 'y', self._w))
    def update(self):
        """Enter event loop until all pending events have been processed by Tcl."""
        self.tk.call('update')
    def update_idletasks(self):
        """Enter event loop until all idle callbacks have been called. This
        will update the display of windows but nie process events caused by
        the user."""
        self.tk.call('update', 'idletasks')
    def bindtags(self, tagList=Nic):
        """Set albo get the list of bindtags dla this widget.

        With no argument zwróć the list of all bindtags associated with
        this widget. With a list of strings jako argument the bindtags are
        set to this list. The bindtags determine w which order events are
        processed (see bind)."""
        jeżeli tagList jest Nic:
            zwróć self.tk.splitlist(
                self.tk.call('bindtags', self._w))
        inaczej:
            self.tk.call('bindtags', self._w, tagList)
    def _bind(self, what, sequence, func, add, needcleanup=1):
        """Internal function."""
        jeżeli isinstance(func, str):
            self.tk.call(what + (sequence, func))
        albo_inaczej func:
            funcid = self._register(func, self._substitute,
                        needcleanup)
            cmd = ('%sjeżeli {"[%s %s]" == "break"} przerwij\n'
                   %
                   (add oraz '+' albo '',
                funcid, self._subst_format_str))
            self.tk.call(what + (sequence, cmd))
            zwróć funcid
        albo_inaczej sequence:
            zwróć self.tk.call(what + (sequence,))
        inaczej:
            zwróć self.tk.splitlist(self.tk.call(what))
    def bind(self, sequence=Nic, func=Nic, add=Nic):
        """Bind to this widget at event SEQUENCE a call to function FUNC.

        SEQUENCE jest a string of concatenated event
        patterns. An event pattern jest of the form
        <MODIFIER-MODIFIER-TYPE-DETAIL> where MODIFIER jest one
        of Control, Mod2, M2, Shift, Mod3, M3, Lock, Mod4, M4,
        Button1, B1, Mod5, M5 Button2, B2, Meta, M, Button3,
        B3, Alt, Button4, B4, Double, Button5, B5 Triple,
        Mod1, M1. TYPE jest one of Activate, Enter, Map,
        ButtonPress, Button, Expose, Motion, ButtonRelease
        FocusIn, MouseWheel, Circulate, FocusOut, Property,
        Colormap, Gravity Reparent, Configure, KeyPress, Key,
        Unmap, Deactivate, KeyRelease Visibility, Destroy,
        Leave oraz DETAIL jest the button number dla ButtonPress,
        ButtonRelease oraz DETAIL jest the Keysym dla KeyPress oraz
        KeyRelease. Examples are
        <Control-Button-1> dla pressing Control oraz mouse button 1 albo
        <Alt-A> dla pressing A oraz the Alt key (KeyPress can be omitted).
        An event pattern can also be a virtual event of the form
        <<AString>> where AString can be arbitrary. This
        event can be generated by event_generate.
        If events are concatenated they must appear shortly
        after each other.

        FUNC will be called jeżeli the event sequence occurs przy an
        instance of Event jako argument. If the zwróć value of FUNC jest
        "break" no further bound function jest invoked.

        An additional boolean parameter ADD specifies whether FUNC will
        be called additionally to the other bound function albo whether
        it will replace the previous function.

        Bind will zwróć an identifier to allow deletion of the bound function with
        unbind without memory leak.

        If FUNC albo SEQUENCE jest omitted the bound function albo list
        of bound events are returned."""

        zwróć self._bind(('bind', self._w), sequence, func, add)
    def unbind(self, sequence, funcid=Nic):
        """Unbind dla this widget dla event SEQUENCE  the
        function identified przy FUNCID."""
        self.tk.call('bind', self._w, sequence, '')
        jeżeli funcid:
            self.deletecommand(funcid)
    def bind_all(self, sequence=Nic, func=Nic, add=Nic):
        """Bind to all widgets at an event SEQUENCE a call to function FUNC.
        An additional boolean parameter ADD specifies whether FUNC will
        be called additionally to the other bound function albo whether
        it will replace the previous function. See bind dla the zwróć value."""
        zwróć self._bind(('bind', 'all'), sequence, func, add, 0)
    def unbind_all(self, sequence):
        """Unbind dla all widgets dla event SEQUENCE all functions."""
        self.tk.call('bind', 'all' , sequence, '')
    def bind_class(self, className, sequence=Nic, func=Nic, add=Nic):

        """Bind to widgets przy bindtag CLASSNAME at event
        SEQUENCE a call of function FUNC. An additional
        boolean parameter ADD specifies whether FUNC will be
        called additionally to the other bound function albo
        whether it will replace the previous function. See bind for
        the zwróć value."""

        zwróć self._bind(('bind', className), sequence, func, add, 0)
    def unbind_class(self, className, sequence):
        """Unbind dla a all widgets przy bindtag CLASSNAME dla event SEQUENCE
        all functions."""
        self.tk.call('bind', className , sequence, '')
    def mainloop(self, n=0):
        """Call the mainloop of Tk."""
        self.tk.mainloop(n)
    def quit(self):
        """Quit the Tcl interpreter. All widgets will be destroyed."""
        self.tk.quit()
    def _getints(self, string):
        """Internal function."""
        jeżeli string:
            zwróć tuple(map(self.tk.getint, self.tk.splitlist(string)))
    def _getdoubles(self, string):
        """Internal function."""
        jeżeli string:
            zwróć tuple(map(self.tk.getdouble, self.tk.splitlist(string)))
    def _getboolean(self, string):
        """Internal function."""
        jeżeli string:
            zwróć self.tk.getboolean(string)
    def _displayof(self, displayof):
        """Internal function."""
        jeżeli displayof:
            zwróć ('-displayof', displayof)
        jeżeli displayof jest Nic:
            zwróć ('-displayof', self._w)
        zwróć ()
    @property
    def _windowingsystem(self):
        """Internal function."""
        spróbuj:
            zwróć self._root()._windowingsystem_cached
        wyjąwszy AttributeError:
            ws = self._root()._windowingsystem_cached = \
                        self.tk.call('tk', 'windowingsystem')
            zwróć ws
    def _options(self, cnf, kw = Nic):
        """Internal function."""
        jeżeli kw:
            cnf = _cnfmerge((cnf, kw))
        inaczej:
            cnf = _cnfmerge(cnf)
        res = ()
        dla k, v w cnf.items():
            jeżeli v jest nie Nic:
                jeżeli k[-1] == '_': k = k[:-1]
                jeżeli callable(v):
                    v = self._register(v)
                albo_inaczej isinstance(v, (tuple, list)):
                    nv = []
                    dla item w v:
                        jeżeli isinstance(item, int):
                            nv.append(str(item))
                        albo_inaczej isinstance(item, str):
                            nv.append(_stringify(item))
                        inaczej:
                            przerwij
                    inaczej:
                        v = ' '.join(nv)
                res = res + ('-'+k, v)
        zwróć res
    def nametowidget(self, name):
        """Return the Tkinter instance of a widget identified by
        its Tcl name NAME."""
        name = str(name).split('.')
        w = self

        jeżeli nie name[0]:
            w = w._root()
            name = name[1:]

        dla n w name:
            jeżeli nie n:
                przerwij
            w = w.children[n]

        zwróć w
    _nametowidget = nametowidget
    def _register(self, func, subst=Nic, needcleanup=1):
        """Return a newly created Tcl function. If this
        function jest called, the Python function FUNC will
        be executed. An optional function SUBST can
        be given which will be executed before FUNC."""
        f = CallWrapper(func, subst, self).__call__
        name = repr(id(f))
        spróbuj:
            func = func.__func__
        wyjąwszy AttributeError:
            dalej
        spróbuj:
            name = name + func.__name__
        wyjąwszy AttributeError:
            dalej
        self.tk.createcommand(name, f)
        jeżeli needcleanup:
            jeżeli self._tclCommands jest Nic:
                self._tclCommands = []
            self._tclCommands.append(name)
        zwróć name
    register = _register
    def _root(self):
        """Internal function."""
        w = self
        dopóki w.master: w = w.master
        zwróć w
    _subst_format = ('%#', '%b', '%f', '%h', '%k',
             '%s', '%t', '%w', '%x', '%y',
             '%A', '%E', '%K', '%N', '%W', '%T', '%X', '%Y', '%D')
    _subst_format_str = " ".join(_subst_format)
    def _substitute(self, *args):
        """Internal function."""
        jeżeli len(args) != len(self._subst_format): zwróć args
        getboolean = self.tk.getboolean

        getint = self.tk.getint
        def getint_event(s):
            """Tk changed behavior w 8.4.2, returning "??" rather more often."""
            spróbuj:
                zwróć getint(s)
            wyjąwszy (ValueError, TclError):
                zwróć s

        nsign, b, f, h, k, s, t, w, x, y, A, E, K, N, W, T, X, Y, D = args
        # Missing: (a, c, d, m, o, v, B, R)
        e = Event()
        # serial field: valid vor all events
        # number of button: ButtonPress oraz ButtonRelease events only
        # height field: Configure, ConfigureRequest, Create,
        # ResizeRequest, oraz Expose events only
        # keycode field: KeyPress oraz KeyRelease events only
        # time field: "valid dla events that contain a time field"
        # width field: Configure, ConfigureRequest, Create, ResizeRequest,
        # oraz Expose events only
        # x field: "valid dla events that contain a x field"
        # y field: "valid dla events that contain a y field"
        # keysym jako decimal: KeyPress oraz KeyRelease events only
        # x_root, y_root fields: ButtonPress, ButtonRelease, KeyPress,
        # KeyRelease,and Motion events
        e.serial = getint(nsign)
        e.num = getint_event(b)
        spróbuj: e.focus = getboolean(f)
        wyjąwszy TclError: dalej
        e.height = getint_event(h)
        e.keycode = getint_event(k)
        e.state = getint_event(s)
        e.time = getint_event(t)
        e.width = getint_event(w)
        e.x = getint_event(x)
        e.y = getint_event(y)
        e.char = A
        spróbuj: e.send_event = getboolean(E)
        wyjąwszy TclError: dalej
        e.keysym = K
        e.keysym_num = getint_event(N)
        e.type = T
        spróbuj:
            e.widget = self._nametowidget(W)
        wyjąwszy KeyError:
            e.widget = W
        e.x_root = getint_event(X)
        e.y_root = getint_event(Y)
        spróbuj:
            e.delta = getint(D)
        wyjąwszy (ValueError, TclError):
            e.delta = 0
        zwróć (e,)
    def _report_exception(self):
        """Internal function."""
        exc, val, tb = sys.exc_info()
        root = self._root()
        root.report_callback_exception(exc, val, tb)

    def _getconfigure(self, *args):
        """Call Tcl configure command oraz zwróć the result jako a dict."""
        cnf = {}
        dla x w self.tk.splitlist(self.tk.call(*args)):
            x = self.tk.splitlist(x)
            cnf[x[0][1:]] = (x[0][1:],) + x[1:]
        zwróć cnf

    def _getconfigure1(self, *args):
        x = self.tk.splitlist(self.tk.call(*args))
        zwróć (x[0][1:],) + x[1:]

    def _configure(self, cmd, cnf, kw):
        """Internal function."""
        jeżeli kw:
            cnf = _cnfmerge((cnf, kw))
        albo_inaczej cnf:
            cnf = _cnfmerge(cnf)
        jeżeli cnf jest Nic:
            zwróć self._getconfigure(_flatten((self._w, cmd)))
        jeżeli isinstance(cnf, str):
            zwróć self._getconfigure1(_flatten((self._w, cmd, '-'+cnf)))
        self.tk.call(_flatten((self._w, cmd)) + self._options(cnf))
    # These used to be defined w Widget:
    def configure(self, cnf=Nic, **kw):
        """Configure resources of a widget.

        The values dla resources are specified jako keyword
        arguments. To get an overview about
        the allowed keyword arguments call the method keys.
        """
        zwróć self._configure('configure', cnf, kw)
    config = configure
    def cget(self, key):
        """Return the resource value dla a KEY given jako string."""
        zwróć self.tk.call(self._w, 'cget', '-' + key)
    __getitem__ = cget
    def __setitem__(self, key, value):
        self.configure({key: value})
    def keys(self):
        """Return a list of all resource names of this widget."""
        zwróć [x[0][1:] dla x w
                self.tk.splitlist(self.tk.call(self._w, 'configure'))]
    def __str__(self):
        """Return the window path name of this widget."""
        zwróć self._w

    def __repr__(self):
        zwróć '<%s.%s object %s>' % (
            self.__class__.__module__, self.__class__.__qualname__, self._w)

    # Pack methods that apply to the master
    _noarg_ = ['_noarg_']
    def pack_propagate(self, flag=_noarg_):
        """Set albo get the status dla propagation of geometry information.

        A boolean argument specifies whether the geometry information
        of the slaves will determine the size of this widget. If no argument
        jest given the current setting will be returned.
        """
        jeżeli flag jest Misc._noarg_:
            zwróć self._getboolean(self.tk.call(
                'pack', 'propagate', self._w))
        inaczej:
            self.tk.call('pack', 'propagate', self._w, flag)
    propagate = pack_propagate
    def pack_slaves(self):
        """Return a list of all slaves of this widget
        w its packing order."""
        zwróć [self._nametowidget(x) dla x w
                self.tk.splitlist(
                   self.tk.call('pack', 'slaves', self._w))]
    slaves = pack_slaves
    # Place method that applies to the master
    def place_slaves(self):
        """Return a list of all slaves of this widget
        w its packing order."""
        zwróć [self._nametowidget(x) dla x w
                self.tk.splitlist(
                   self.tk.call(
                       'place', 'slaves', self._w))]
    # Grid methods that apply to the master
    def grid_anchor(self, anchor=Nic): # new w Tk 8.5
        """The anchor value controls how to place the grid within the
        master when no row/column has any weight.

        The default anchor jest nw."""
        self.tk.call('grid', 'anchor', self._w, anchor)
    anchor = grid_anchor
    def grid_bbox(self, column=Nic, row=Nic, col2=Nic, row2=Nic):
        """Return a tuple of integer coordinates dla the bounding
        box of this widget controlled by the geometry manager grid.

        If COLUMN, ROW jest given the bounding box applies from
        the cell przy row oraz column 0 to the specified
        cell. If COL2 oraz ROW2 are given the bounding box
        starts at that cell.

        The returned integers specify the offset of the upper left
        corner w the master widget oraz the width oraz height.
        """
        args = ('grid', 'bbox', self._w)
        jeżeli column jest nie Nic oraz row jest nie Nic:
            args = args + (column, row)
        jeżeli col2 jest nie Nic oraz row2 jest nie Nic:
            args = args + (col2, row2)
        zwróć self._getints(self.tk.call(*args)) albo Nic
    bbox = grid_bbox

    def _gridconvvalue(self, value):
        jeżeli isinstance(value, (str, _tkinter.Tcl_Obj)):
            spróbuj:
                svalue = str(value)
                jeżeli nie svalue:
                    zwróć Nic
                albo_inaczej '.' w svalue:
                    zwróć self.tk.getdouble(svalue)
                inaczej:
                    zwróć self.tk.getint(svalue)
            wyjąwszy (ValueError, TclError):
                dalej
        zwróć value

    def _grid_configure(self, command, index, cnf, kw):
        """Internal function."""
        jeżeli isinstance(cnf, str) oraz nie kw:
            jeżeli cnf[-1:] == '_':
                cnf = cnf[:-1]
            jeżeli cnf[:1] != '-':
                cnf = '-'+cnf
            options = (cnf,)
        inaczej:
            options = self._options(cnf, kw)
        jeżeli nie options:
            zwróć _splitdict(
                self.tk,
                self.tk.call('grid', command, self._w, index),
                conv=self._gridconvvalue)
        res = self.tk.call(
                  ('grid', command, self._w, index)
                  + options)
        jeżeli len(options) == 1:
            zwróć self._gridconvvalue(res)

    def grid_columnconfigure(self, index, cnf={}, **kw):
        """Configure column INDEX of a grid.

        Valid resources are minsize (minimum size of the column),
        weight (how much does additional space propagate to this column)
        oraz pad (how much space to let additionally)."""
        zwróć self._grid_configure('columnconfigure', index, cnf, kw)
    columnconfigure = grid_columnconfigure
    def grid_location(self, x, y):
        """Return a tuple of column oraz row which identify the cell
        at which the pixel at position X oraz Y inside the master
        widget jest located."""
        zwróć self._getints(
            self.tk.call(
                'grid', 'location', self._w, x, y)) albo Nic
    def grid_propagate(self, flag=_noarg_):
        """Set albo get the status dla propagation of geometry information.

        A boolean argument specifies whether the geometry information
        of the slaves will determine the size of this widget. If no argument
        jest given, the current setting will be returned.
        """
        jeżeli flag jest Misc._noarg_:
            zwróć self._getboolean(self.tk.call(
                'grid', 'propagate', self._w))
        inaczej:
            self.tk.call('grid', 'propagate', self._w, flag)
    def grid_rowconfigure(self, index, cnf={}, **kw):
        """Configure row INDEX of a grid.

        Valid resources are minsize (minimum size of the row),
        weight (how much does additional space propagate to this row)
        oraz pad (how much space to let additionally)."""
        zwróć self._grid_configure('rowconfigure', index, cnf, kw)
    rowconfigure = grid_rowconfigure
    def grid_size(self):
        """Return a tuple of the number of column oraz rows w the grid."""
        zwróć self._getints(
            self.tk.call('grid', 'size', self._w)) albo Nic
    size = grid_size
    def grid_slaves(self, row=Nic, column=Nic):
        """Return a list of all slaves of this widget
        w its packing order."""
        args = ()
        jeżeli row jest nie Nic:
            args = args + ('-row', row)
        jeżeli column jest nie Nic:
            args = args + ('-column', column)
        zwróć [self._nametowidget(x) dla x w
                self.tk.splitlist(self.tk.call(
                   ('grid', 'slaves', self._w) + args))]

    # Support dla the "event" command, new w Tk 4.2.
    # By Case Roole.

    def event_add(self, virtual, *sequences):
        """Bind a virtual event VIRTUAL (of the form <<Name>>)
        to an event SEQUENCE such that the virtual event jest triggered
        whenever SEQUENCE occurs."""
        args = ('event', 'add', virtual) + sequences
        self.tk.call(args)

    def event_delete(self, virtual, *sequences):
        """Unbind a virtual event VIRTUAL z SEQUENCE."""
        args = ('event', 'delete', virtual) + sequences
        self.tk.call(args)

    def event_generate(self, sequence, **kw):
        """Generate an event SEQUENCE. Additional
        keyword arguments specify parameter of the event
        (e.g. x, y, rootx, rooty)."""
        args = ('event', 'generate', self._w, sequence)
        dla k, v w kw.items():
            args = args + ('-%s' % k, str(v))
        self.tk.call(args)

    def event_info(self, virtual=Nic):
        """Return a list of all virtual events albo the information
        about the SEQUENCE bound to the virtual event VIRTUAL."""
        zwróć self.tk.splitlist(
            self.tk.call('event', 'info', virtual))

    # Image related commands

    def image_names(self):
        """Return a list of all existing image names."""
        zwróć self.tk.splitlist(self.tk.call('image', 'names'))

    def image_types(self):
        """Return a list of all available image types (e.g. phote bitmap)."""
        zwróć self.tk.splitlist(self.tk.call('image', 'types'))


klasa CallWrapper:
    """Internal class. Stores function to call when some user
    defined Tcl function jest called e.g. after an event occurred."""
    def __init__(self, func, subst, widget):
        """Store FUNC, SUBST oraz WIDGET jako members."""
        self.func = func
        self.subst = subst
        self.widget = widget
    def __call__(self, *args):
        """Apply first function SUBST to arguments, than FUNC."""
        spróbuj:
            jeżeli self.subst:
                args = self.subst(*args)
            zwróć self.func(*args)
        wyjąwszy SystemExit:
            podnieś
        wyjąwszy:
            self.widget._report_exception()


klasa XView:
    """Mix-in klasa dla querying oraz changing the horizontal position
    of a widget's window."""

    def xview(self, *args):
        """Query oraz change the horizontal position of the view."""
        res = self.tk.call(self._w, 'xview', *args)
        jeżeli nie args:
            zwróć self._getdoubles(res)

    def xview_moveto(self, fraction):
        """Adjusts the view w the window so that FRACTION of the
        total width of the canvas jest off-screen to the left."""
        self.tk.call(self._w, 'xview', 'moveto', fraction)

    def xview_scroll(self, number, what):
        """Shift the x-view according to NUMBER which jest measured w "units"
        albo "pages" (WHAT)."""
        self.tk.call(self._w, 'xview', 'scroll', number, what)


klasa YView:
    """Mix-in klasa dla querying oraz changing the vertical position
    of a widget's window."""

    def yview(self, *args):
        """Query oraz change the vertical position of the view."""
        res = self.tk.call(self._w, 'yview', *args)
        jeżeli nie args:
            zwróć self._getdoubles(res)

    def yview_moveto(self, fraction):
        """Adjusts the view w the window so that FRACTION of the
        total height of the canvas jest off-screen to the top."""
        self.tk.call(self._w, 'yview', 'moveto', fraction)

    def yview_scroll(self, number, what):
        """Shift the y-view according to NUMBER which jest measured w
        "units" albo "pages" (WHAT)."""
        self.tk.call(self._w, 'yview', 'scroll', number, what)


klasa Wm:
    """Provides functions dla the communication przy the window manager."""

    def wm_aspect(self,
              minNumer=Nic, minDenom=Nic,
              maxNumer=Nic, maxDenom=Nic):
        """Instruct the window manager to set the aspect ratio (width/height)
        of this widget to be between MINNUMER/MINDENOM oraz MAXNUMER/MAXDENOM. Return a tuple
        of the actual values jeżeli no argument jest given."""
        zwróć self._getints(
            self.tk.call('wm', 'aspect', self._w,
                     minNumer, minDenom,
                     maxNumer, maxDenom))
    aspect = wm_aspect

    def wm_attributes(self, *args):
        """This subcommand returns albo sets platform specific attributes

        The first form returns a list of the platform specific flags oraz
        their values. The second form returns the value dla the specific
        option. The third form sets one albo more of the values. The values
        are jako follows:

        On Windows, -disabled gets albo sets whether the window jest w a
        disabled state. -toolwindow gets albo sets the style of the window
        to toolwindow (as defined w the MSDN). -topmost gets albo sets
        whether this jest a topmost window (displays above all other
        windows).

        On Macintosh, XXXXX

        On Unix, there are currently no special attribute values.
        """
        args = ('wm', 'attributes', self._w) + args
        zwróć self.tk.call(args)
    attributes=wm_attributes

    def wm_client(self, name=Nic):
        """Store NAME w WM_CLIENT_MACHINE property of this widget. Return
        current value."""
        zwróć self.tk.call('wm', 'client', self._w, name)
    client = wm_client
    def wm_colormapwindows(self, *wlist):
        """Store list of window names (WLIST) into WM_COLORMAPWINDOWS property
        of this widget. This list contains windows whose colormaps differ z their
        parents. Return current list of widgets jeżeli WLIST jest empty."""
        jeżeli len(wlist) > 1:
            wlist = (wlist,) # Tk needs a list of windows here
        args = ('wm', 'colormapwindows', self._w) + wlist
        jeżeli wlist:
            self.tk.call(args)
        inaczej:
            zwróć [self._nametowidget(x)
                    dla x w self.tk.splitlist(self.tk.call(args))]
    colormapwindows = wm_colormapwindows
    def wm_command(self, value=Nic):
        """Store VALUE w WM_COMMAND property. It jest the command
        which shall be used to invoke the application. Return current
        command jeżeli VALUE jest Nic."""
        zwróć self.tk.call('wm', 'command', self._w, value)
    command = wm_command
    def wm_deiconify(self):
        """Deiconify this widget. If it was never mapped it will nie be mapped.
        On Windows it will podnieś this widget oraz give it the focus."""
        zwróć self.tk.call('wm', 'deiconify', self._w)
    deiconify = wm_deiconify
    def wm_focusmodel(self, model=Nic):
        """Set focus mousuń to MODEL. "active" means that this widget will claim
        the focus itself, "passive" means that the window manager shall give
        the focus. Return current focus mousuń jeżeli MODEL jest Nic."""
        zwróć self.tk.call('wm', 'focusmodel', self._w, model)
    focusmousuń = wm_focusmodel
    def wm_forget(self, window): # new w Tk 8.5
        """The window will be unmappend z the screen oraz will no longer
        be managed by wm. toplevel windows will be treated like frame
        windows once they are no longer managed by wm, however, the menu
        option configuration will be remembered oraz the menus will zwróć
        once the widget jest managed again."""
        self.tk.call('wm', 'forget', window)
    forget = wm_forget
    def wm_frame(self):
        """Return identifier dla decorative frame of this widget jeżeli present."""
        zwróć self.tk.call('wm', 'frame', self._w)
    frame = wm_frame
    def wm_geometry(self, newGeometry=Nic):
        """Set geometry to NEWGEOMETRY of the form =widthxheight+x+y. Return
        current value jeżeli Nic jest given."""
        zwróć self.tk.call('wm', 'geometry', self._w, newGeometry)
    geometry = wm_geometry
    def wm_grid(self,
         baseWidth=Nic, baseHeight=Nic,
         widthInc=Nic, heightInc=Nic):
        """Instruct the window manager that this widget shall only be
        resized on grid boundaries. WIDTHINC oraz HEIGHTINC are the width oraz
        height of a grid unit w pixels. BASEWIDTH oraz BASEHEIGHT are the
        number of grid units requested w Tk_GeometryRequest."""
        zwróć self._getints(self.tk.call(
            'wm', 'grid', self._w,
            baseWidth, baseHeight, widthInc, heightInc))
    grid = wm_grid
    def wm_group(self, pathName=Nic):
        """Set the group leader widgets dla related widgets to PATHNAME. Return
        the group leader of this widget jeżeli Nic jest given."""
        zwróć self.tk.call('wm', 'group', self._w, pathName)
    group = wm_group
    def wm_iconbitmap(self, bitmap=Nic, default=Nic):
        """Set bitmap dla the iconified widget to BITMAP. Return
        the bitmap jeżeli Nic jest given.

        Under Windows, the DEFAULT parameter can be used to set the icon
        dla the widget oraz any descendents that don't have an icon set
        explicitly.  DEFAULT can be the relative path to a .ico file
        (example: root.iconbitmap(default='myicon.ico') ).  See Tk
        documentation dla more information."""
        jeżeli default:
            zwróć self.tk.call('wm', 'iconbitmap', self._w, '-default', default)
        inaczej:
            zwróć self.tk.call('wm', 'iconbitmap', self._w, bitmap)
    iconbitmap = wm_iconbitmap
    def wm_iconify(self):
        """Display widget jako icon."""
        zwróć self.tk.call('wm', 'iconify', self._w)
    iconify = wm_iconify
    def wm_iconmask(self, bitmap=Nic):
        """Set mask dla the icon bitmap of this widget. Return the
        mask jeżeli Nic jest given."""
        zwróć self.tk.call('wm', 'iconmask', self._w, bitmap)
    iconmask = wm_iconmask
    def wm_iconname(self, newName=Nic):
        """Set the name of the icon dla this widget. Return the name if
        Nic jest given."""
        zwróć self.tk.call('wm', 'iconname', self._w, newName)
    iconname = wm_iconname
    def wm_iconphoto(self, default=Nieprawda, *args): # new w Tk 8.5
        """Sets the titlebar icon dla this window based on the named photo
        images dalejed through args. If default jest Prawda, this jest applied to
        all future created toplevels jako well.

        The data w the images jest taken jako a snapshot at the time of
        invocation. If the images are later changed, this jest nie reflected
        to the titlebar icons. Multiple images are accepted to allow
        different images sizes to be provided. The window manager may scale
        provided icons to an appropriate size.

        On Windows, the images are packed into a Windows icon structure.
        This will override an icon specified to wm_iconbitmap, oraz vice
        versa.

        On X, the images are arranged into the _NET_WM_ICON X property,
        which most modern window managers support. An icon specified by
        wm_iconbitmap may exist simultaneously.

        On Macintosh, this currently does nothing."""
        jeżeli default:
            self.tk.call('wm', 'iconphoto', self._w, "-default", *args)
        inaczej:
            self.tk.call('wm', 'iconphoto', self._w, *args)
    iconphoto = wm_iconphoto
    def wm_iconposition(self, x=Nic, y=Nic):
        """Set the position of the icon of this widget to X oraz Y. Return
        a tuple of the current values of X oraz X jeżeli Nic jest given."""
        zwróć self._getints(self.tk.call(
            'wm', 'iconposition', self._w, x, y))
    iconposition = wm_iconposition
    def wm_iconwindow(self, pathName=Nic):
        """Set widget PATHNAME to be displayed instead of icon. Return the current
        value jeżeli Nic jest given."""
        zwróć self.tk.call('wm', 'iconwindow', self._w, pathName)
    iconwindow = wm_iconwindow
    def wm_manage(self, widget): # new w Tk 8.5
        """The widget specified will become a stand alone top-level window.
        The window will be decorated przy the window managers title bar,
        etc."""
        self.tk.call('wm', 'manage', widget)
    manage = wm_manage
    def wm_maxsize(self, width=Nic, height=Nic):
        """Set max WIDTH oraz HEIGHT dla this widget. If the window jest gridded
        the values are given w grid units. Return the current values jeżeli Nic
        jest given."""
        zwróć self._getints(self.tk.call(
            'wm', 'maxsize', self._w, width, height))
    maxsize = wm_maxsize
    def wm_minsize(self, width=Nic, height=Nic):
        """Set min WIDTH oraz HEIGHT dla this widget. If the window jest gridded
        the values are given w grid units. Return the current values jeżeli Nic
        jest given."""
        zwróć self._getints(self.tk.call(
            'wm', 'minsize', self._w, width, height))
    minsize = wm_minsize
    def wm_overrideredirect(self, boolean=Nic):
        """Instruct the window manager to ignore this widget
        jeżeli BOOLEAN jest given przy 1. Return the current value jeżeli Nic
        jest given."""
        zwróć self._getboolean(self.tk.call(
            'wm', 'overrideredirect', self._w, boolean))
    overrideredirect = wm_overrideredirect
    def wm_positionfrom(self, who=Nic):
        """Instruct the window manager that the position of this widget shall
        be defined by the user jeżeli WHO jest "user", oraz by its own policy jeżeli WHO jest
        "program"."""
        zwróć self.tk.call('wm', 'positionfrom', self._w, who)
    positionz = wm_positionfrom
    def wm_protocol(self, name=Nic, func=Nic):
        """Bind function FUNC to command NAME dla this widget.
        Return the function bound to NAME jeżeli Nic jest given. NAME could be
        e.g. "WM_SAVE_YOURSELF" albo "WM_DELETE_WINDOW"."""
        jeżeli callable(func):
            command = self._register(func)
        inaczej:
            command = func
        zwróć self.tk.call(
            'wm', 'protocol', self._w, name, command)
    protocol = wm_protocol
    def wm_resizable(self, width=Nic, height=Nic):
        """Instruct the window manager whether this width can be resized
        w WIDTH albo HEIGHT. Both values are boolean values."""
        zwróć self.tk.call('wm', 'resizable', self._w, width, height)
    resizable = wm_resizable
    def wm_sizefrom(self, who=Nic):
        """Instruct the window manager that the size of this widget shall
        be defined by the user jeżeli WHO jest "user", oraz by its own policy jeżeli WHO jest
        "program"."""
        zwróć self.tk.call('wm', 'sizefrom', self._w, who)
    sizez = wm_sizefrom
    def wm_state(self, newstate=Nic):
        """Query albo set the state of this widget jako one of normal, icon,
        iconic (see wm_iconwindow), withdrawn, albo zoomed (Windows only)."""
        zwróć self.tk.call('wm', 'state', self._w, newstate)
    state = wm_state
    def wm_title(self, string=Nic):
        """Set the title of this widget."""
        zwróć self.tk.call('wm', 'title', self._w, string)
    title = wm_title
    def wm_transient(self, master=Nic):
        """Instruct the window manager that this widget jest transient
        przy regard to widget MASTER."""
        zwróć self.tk.call('wm', 'transient', self._w, master)
    transient = wm_transient
    def wm_withdraw(self):
        """Withdraw this widget z the screen such that it jest unmapped
        oraz forgotten by the window manager. Re-draw it przy wm_deiconify."""
        zwróć self.tk.call('wm', 'withdraw', self._w)
    withdraw = wm_withdraw


klasa Tk(Misc, Wm):
    """Toplevel widget of Tk which represents mostly the main window
    of an application. It has an associated Tcl interpreter."""
    _w = '.'
    def __init__(self, screenName=Nic, baseName=Nic, className='Tk',
                 useTk=1, sync=0, use=Nic):
        """Return a new Toplevel widget on screen SCREENNAME. A new Tcl interpreter will
        be created. BASENAME will be used dla the identification of the profile file (see
        readprofile).
        It jest constructed z sys.argv[0] without extensions jeżeli Nic jest given. CLASSNAME
        jest the name of the widget class."""
        self.master = Nic
        self.children = {}
        self._tkloaded = 0
        # to avoid recursions w the getattr code w case of failure, we
        # ensure that self.tk jest always _something_.
        self.tk = Nic
        jeżeli baseName jest Nic:
            zaimportuj os
            baseName = os.path.basename(sys.argv[0])
            baseName, ext = os.path.splitext(baseName)
            jeżeli ext nie w ('.py', '.pyc'):
                baseName = baseName + ext
        interactive = 0
        self.tk = _tkinter.create(screenName, baseName, className, interactive, wantobjects, useTk, sync, use)
        jeżeli useTk:
            self._loadtk()
        jeżeli nie sys.flags.ignore_environment:
            # Issue #16248: Honor the -E flag to avoid code injection.
            self.readprofile(baseName, className)
    def loadtk(self):
        jeżeli nie self._tkloaded:
            self.tk.loadtk()
            self._loadtk()
    def _loadtk(self):
        self._tkloaded = 1
        global _default_root
        # Version sanity checks
        tk_version = self.tk.getvar('tk_version')
        jeżeli tk_version != _tkinter.TK_VERSION:
            podnieś RuntimeError("tk.h version (%s) doesn't match libtk.a version (%s)"
                               % (_tkinter.TK_VERSION, tk_version))
        # Under unknown circumstances, tcl_version gets coerced to float
        tcl_version = str(self.tk.getvar('tcl_version'))
        jeżeli tcl_version != _tkinter.TCL_VERSION:
            podnieś RuntimeError("tcl.h version (%s) doesn't match libtcl.a version (%s)" \
                               % (_tkinter.TCL_VERSION, tcl_version))
        jeżeli TkVersion < 4.0:
            podnieś RuntimeError("Tk 4.0 albo higher jest required; found Tk %s"
                               % str(TkVersion))
        # Create oraz register the tkerror oraz exit commands
        # We need to inline parts of _register here, _ register
        # would register differently-named commands.
        jeżeli self._tclCommands jest Nic:
            self._tclCommands = []
        self.tk.createcommand('tkerror', _tkerror)
        self.tk.createcommand('exit', _exit)
        self._tclCommands.append('tkerror')
        self._tclCommands.append('exit')
        jeżeli _support_default_root oraz nie _default_root:
            _default_root = self
        self.protocol("WM_DELETE_WINDOW", self.destroy)
    def destroy(self):
        """Destroy this oraz all descendants widgets. This will
        end the application of this Tcl interpreter."""
        dla c w list(self.children.values()): c.destroy()
        self.tk.call('destroy', self._w)
        Misc.destroy(self)
        global _default_root
        jeżeli _support_default_root oraz _default_root jest self:
            _default_root = Nic
    def readprofile(self, baseName, className):
        """Internal function. It reads BASENAME.tcl oraz CLASSNAME.tcl into
        the Tcl Interpreter oraz calls exec on the contents of BASENAME.py oraz
        CLASSNAME.py jeżeli such a file exists w the home directory."""
        zaimportuj os
        jeżeli 'HOME' w os.environ: home = os.environ['HOME']
        inaczej: home = os.curdir
        class_tcl = os.path.join(home, '.%s.tcl' % className)
        class_py = os.path.join(home, '.%s.py' % className)
        base_tcl = os.path.join(home, '.%s.tcl' % baseName)
        base_py = os.path.join(home, '.%s.py' % baseName)
        dir = {'self': self}
        exec('z tkinter zaimportuj *', dir)
        jeżeli os.path.isfile(class_tcl):
            self.tk.call('source', class_tcl)
        jeżeli os.path.isfile(class_py):
            exec(open(class_py).read(), dir)
        jeżeli os.path.isfile(base_tcl):
            self.tk.call('source', base_tcl)
        jeżeli os.path.isfile(base_py):
            exec(open(base_py).read(), dir)
    def report_callback_exception(self, exc, val, tb):
        """Report callback exception on sys.stderr.

        Applications may want to override this internal function, oraz
        should when sys.stderr jest Nic."""
        zaimportuj traceback
        print("Exception w Tkinter callback", file=sys.stderr)
        sys.last_type = exc
        sys.last_value = val
        sys.last_traceback = tb
        traceback.print_exception(exc, val, tb)
    def __getattr__(self, attr):
        "Delegate attribute access to the interpreter object"
        zwróć getattr(self.tk, attr)

# Ideally, the classes Pack, Place oraz Grid disappear, the
# pack/place/grid methods are defined on the Widget class, oraz
# everybody uses w.pack_whatever(...) instead of Pack.whatever(w,
# ...), przy pack(), place() oraz grid() being short for
# pack_configure(), place_configure() oraz grid_columnconfigure(), oraz
# forget() being short dla pack_forget().  As a practical matter, I'm
# afraid that there jest too much code out there that may be using the
# Pack, Place albo Grid class, so I leave them intact -- but only as
# backwards compatibility features.  Also note that those methods that
# take a master jako argument (e.g. pack_propagate) have been moved to
# the Misc klasa (which now incorporates all methods common between
# toplevel oraz interior widgets).  Again, dla compatibility, these are
# copied into the Pack, Place albo Grid class.


def Tcl(screenName=Nic, baseName=Nic, className='Tk', useTk=0):
    zwróć Tk(screenName, baseName, className, useTk)

klasa Pack:
    """Geometry manager Pack.

    Base klasa to use the methods pack_* w every widget."""
    def pack_configure(self, cnf={}, **kw):
        """Pack a widget w the parent widget. Use jako options:
        after=widget - pack it after you have packed widget
        anchor=NSEW (or subset) - position widget according to
                                  given direction
        before=widget - pack it before you will pack widget
        expand=bool - expand widget jeżeli parent size grows
        fill=NONE albo X albo Y albo BOTH - fill widget jeżeli widget grows
        in=master - use master to contain this widget
        in_=master - see 'in' option description
        ipadx=amount - add internal padding w x direction
        ipady=amount - add internal padding w y direction
        padx=amount - add padding w x direction
        pady=amount - add padding w y direction
        side=TOP albo BOTTOM albo LEFT albo RIGHT -  where to add this widget.
        """
        self.tk.call(
              ('pack', 'configure', self._w)
              + self._options(cnf, kw))
    pack = configure = config = pack_configure
    def pack_forget(self):
        """Unmap this widget oraz do nie use it dla the packing order."""
        self.tk.call('pack', 'forget', self._w)
    forget = pack_forget
    def pack_info(self):
        """Return information about the packing options
        dla this widget."""
        d = _splitdict(self.tk, self.tk.call('pack', 'info', self._w))
        jeżeli 'in' w d:
            d['in'] = self.nametowidget(d['in'])
        zwróć d
    info = pack_info
    propagate = pack_propagate = Misc.pack_propagate
    slaves = pack_slaves = Misc.pack_slaves

klasa Place:
    """Geometry manager Place.

    Base klasa to use the methods place_* w every widget."""
    def place_configure(self, cnf={}, **kw):
        """Place a widget w the parent widget. Use jako options:
        in=master - master relative to which the widget jest placed
        in_=master - see 'in' option description
        x=amount - locate anchor of this widget at position x of master
        y=amount - locate anchor of this widget at position y of master
        relx=amount - locate anchor of this widget between 0.0 oraz 1.0
                      relative to width of master (1.0 jest right edge)
        rely=amount - locate anchor of this widget between 0.0 oraz 1.0
                      relative to height of master (1.0 jest bottom edge)
        anchor=NSEW (or subset) - position anchor according to given direction
        width=amount - width of this widget w pixel
        height=amount - height of this widget w pixel
        relwidth=amount - width of this widget between 0.0 oraz 1.0
                          relative to width of master (1.0 jest the same width
                          jako the master)
        relheight=amount - height of this widget between 0.0 oraz 1.0
                           relative to height of master (1.0 jest the same
                           height jako the master)
        bordermode="inside" albo "outside" - whether to take border width of
                                           master widget into account
        """
        self.tk.call(
              ('place', 'configure', self._w)
              + self._options(cnf, kw))
    place = configure = config = place_configure
    def place_forget(self):
        """Unmap this widget."""
        self.tk.call('place', 'forget', self._w)
    forget = place_forget
    def place_info(self):
        """Return information about the placing options
        dla this widget."""
        d = _splitdict(self.tk, self.tk.call('place', 'info', self._w))
        jeżeli 'in' w d:
            d['in'] = self.nametowidget(d['in'])
        zwróć d
    info = place_info
    slaves = place_slaves = Misc.place_slaves

klasa Grid:
    """Geometry manager Grid.

    Base klasa to use the methods grid_* w every widget."""
    # Thanks to Masazumi Yoshikawa (yosikawa@isi.edu)
    def grid_configure(self, cnf={}, **kw):
        """Position a widget w the parent widget w a grid. Use jako options:
        column=number - use cell identified przy given column (starting przy 0)
        columnspan=number - this widget will span several columns
        in=master - use master to contain this widget
        in_=master - see 'in' option description
        ipadx=amount - add internal padding w x direction
        ipady=amount - add internal padding w y direction
        padx=amount - add padding w x direction
        pady=amount - add padding w y direction
        row=number - use cell identified przy given row (starting przy 0)
        rowspan=number - this widget will span several rows
        sticky=NSEW - jeżeli cell jest larger on which sides will this
                      widget stick to the cell boundary
        """
        self.tk.call(
              ('grid', 'configure', self._w)
              + self._options(cnf, kw))
    grid = configure = config = grid_configure
    bbox = grid_bbox = Misc.grid_bbox
    columnconfigure = grid_columnconfigure = Misc.grid_columnconfigure
    def grid_forget(self):
        """Unmap this widget."""
        self.tk.call('grid', 'forget', self._w)
    forget = grid_forget
    def grid_remove(self):
        """Unmap this widget but remember the grid options."""
        self.tk.call('grid', 'remove', self._w)
    def grid_info(self):
        """Return information about the options
        dla positioning this widget w a grid."""
        d = _splitdict(self.tk, self.tk.call('grid', 'info', self._w))
        jeżeli 'in' w d:
            d['in'] = self.nametowidget(d['in'])
        zwróć d
    info = grid_info
    location = grid_location = Misc.grid_location
    propagate = grid_propagate = Misc.grid_propagate
    rowconfigure = grid_rowconfigure = Misc.grid_rowconfigure
    size = grid_size = Misc.grid_size
    slaves = grid_slaves = Misc.grid_slaves

klasa BaseWidget(Misc):
    """Internal class."""
    def _setup(self, master, cnf):
        """Internal function. Sets up information about children."""
        jeżeli _support_default_root:
            global _default_root
            jeżeli nie master:
                jeżeli nie _default_root:
                    _default_root = Tk()
                master = _default_root
        self.master = master
        self.tk = master.tk
        name = Nic
        jeżeli 'name' w cnf:
            name = cnf['name']
            usuń cnf['name']
        jeżeli nie name:
            name = repr(id(self))
        self._name = name
        jeżeli master._w=='.':
            self._w = '.' + name
        inaczej:
            self._w = master._w + '.' + name
        self.children = {}
        jeżeli self._name w self.master.children:
            self.master.children[self._name].destroy()
        self.master.children[self._name] = self
    def __init__(self, master, widgetName, cnf={}, kw={}, extra=()):
        """Construct a widget przy the parent widget MASTER, a name WIDGETNAME
        oraz appropriate options."""
        jeżeli kw:
            cnf = _cnfmerge((cnf, kw))
        self.widgetName = widgetName
        BaseWidget._setup(self, master, cnf)
        jeżeli self._tclCommands jest Nic:
            self._tclCommands = []
        classes = [(k, v) dla k, v w cnf.items() jeżeli isinstance(k, type)]
        dla k, v w classes:
            usuń cnf[k]
        self.tk.call(
            (widgetName, self._w) + extra + self._options(cnf))
        dla k, v w classes:
            k.configure(self, v)
    def destroy(self):
        """Destroy this oraz all descendants widgets."""
        dla c w list(self.children.values()): c.destroy()
        self.tk.call('destroy', self._w)
        jeżeli self._name w self.master.children:
            usuń self.master.children[self._name]
        Misc.destroy(self)
    def _do(self, name, args=()):
        # XXX Obsolete -- better use self.tk.call directly!
        zwróć self.tk.call((self._w, name) + args)

klasa Widget(BaseWidget, Pack, Place, Grid):
    """Internal class.

    Base klasa dla a widget which can be positioned przy the geometry managers
    Pack, Place albo Grid."""
    dalej

klasa Toplevel(BaseWidget, Wm):
    """Toplevel widget, e.g. dla dialogs."""
    def __init__(self, master=Nic, cnf={}, **kw):
        """Construct a toplevel widget przy the parent MASTER.

        Valid resource names: background, bd, bg, borderwidth, class,
        colormap, container, cursor, height, highlightbackground,
        highlightcolor, highlightthickness, menu, relief, screen, takefocus,
        use, visual, width."""
        jeżeli kw:
            cnf = _cnfmerge((cnf, kw))
        extra = ()
        dla wmkey w ['screen', 'class_', 'class', 'visual',
                  'colormap']:
            jeżeli wmkey w cnf:
                val = cnf[wmkey]
                # TBD: a hack needed because some keys
                # are nie valid jako keyword arguments
                jeżeli wmkey[-1] == '_': opt = '-'+wmkey[:-1]
                inaczej: opt = '-'+wmkey
                extra = extra + (opt, val)
                usuń cnf[wmkey]
        BaseWidget.__init__(self, master, 'toplevel', cnf, {}, extra)
        root = self._root()
        self.iconname(root.iconname())
        self.title(root.title())
        self.protocol("WM_DELETE_WINDOW", self.destroy)

klasa Button(Widget):
    """Button widget."""
    def __init__(self, master=Nic, cnf={}, **kw):
        """Construct a button widget przy the parent MASTER.

        STANDARD OPTIONS

            activebackground, activeforeground, anchor,
            background, bitmap, borderwidth, cursor,
            disabledforeground, font, foreground
            highlightbackground, highlightcolor,
            highlightthickness, image, justify,
            padx, pady, relief, repeatdelay,
            repeatinterval, takefocus, text,
            textvariable, underline, wraplength

        WIDGET-SPECIFIC OPTIONS

            command, compound, default, height,
            overrelief, state, width
        """
        Widget.__init__(self, master, 'button', cnf, kw)

    def flash(self):
        """Flash the button.

        This jest accomplished by redisplaying
        the button several times, alternating between active oraz
        normal colors. At the end of the flash the button jest left
        w the same normal/active state jako when the command was
        invoked. This command jest ignored jeżeli the button's state jest
        disabled.
        """
        self.tk.call(self._w, 'flash')

    def invoke(self):
        """Invoke the command associated przy the button.

        The zwróć value jest the zwróć value z the command,
        albo an empty string jeżeli there jest no command associated with
        the button. This command jest ignored jeżeli the button's state
        jest disabled.
        """
        zwróć self.tk.call(self._w, 'invoke')

klasa Canvas(Widget, XView, YView):
    """Canvas widget to display graphical elements like lines albo text."""
    def __init__(self, master=Nic, cnf={}, **kw):
        """Construct a canvas widget przy the parent MASTER.

        Valid resource names: background, bd, bg, borderwidth, closeenough,
        confine, cursor, height, highlightbackground, highlightcolor,
        highlightthickness, insertbackground, insertborderwidth,
        insertofftime, insertontime, insertwidth, offset, relief,
        scrollregion, selectbackground, selectborderwidth, selectforeground,
        state, takefocus, width, xscrollcommand, xscrollincrement,
        yscrollcommand, yscrollincrement."""
        Widget.__init__(self, master, 'canvas', cnf, kw)
    def addtag(self, *args):
        """Internal function."""
        self.tk.call((self._w, 'addtag') + args)
    def addtag_above(self, newtag, tagOrId):
        """Add tag NEWTAG to all items above TAGORID."""
        self.addtag(newtag, 'above', tagOrId)
    def addtag_all(self, newtag):
        """Add tag NEWTAG to all items."""
        self.addtag(newtag, 'all')
    def addtag_below(self, newtag, tagOrId):
        """Add tag NEWTAG to all items below TAGORID."""
        self.addtag(newtag, 'below', tagOrId)
    def addtag_closest(self, newtag, x, y, halo=Nic, start=Nic):
        """Add tag NEWTAG to item which jest closest to pixel at X, Y.
        If several match take the top-most.
        All items closer than HALO are considered overlapping (all are
        closests). If START jest specified the next below this tag jest taken."""
        self.addtag(newtag, 'closest', x, y, halo, start)
    def addtag_enclosed(self, newtag, x1, y1, x2, y2):
        """Add tag NEWTAG to all items w the rectangle defined
        by X1,Y1,X2,Y2."""
        self.addtag(newtag, 'enclosed', x1, y1, x2, y2)
    def addtag_overlapping(self, newtag, x1, y1, x2, y2):
        """Add tag NEWTAG to all items which overlap the rectangle
        defined by X1,Y1,X2,Y2."""
        self.addtag(newtag, 'overlapping', x1, y1, x2, y2)
    def addtag_withtag(self, newtag, tagOrId):
        """Add tag NEWTAG to all items przy TAGORID."""
        self.addtag(newtag, 'withtag', tagOrId)
    def bbox(self, *args):
        """Return a tuple of X1,Y1,X2,Y2 coordinates dla a rectangle
        which encloses all items przy tags specified jako arguments."""
        zwróć self._getints(
            self.tk.call((self._w, 'bbox') + args)) albo Nic
    def tag_unbind(self, tagOrId, sequence, funcid=Nic):
        """Unbind dla all items przy TAGORID dla event SEQUENCE  the
        function identified przy FUNCID."""
        self.tk.call(self._w, 'bind', tagOrId, sequence, '')
        jeżeli funcid:
            self.deletecommand(funcid)
    def tag_bind(self, tagOrId, sequence=Nic, func=Nic, add=Nic):
        """Bind to all items przy TAGORID at event SEQUENCE a call to function FUNC.

        An additional boolean parameter ADD specifies whether FUNC will be
        called additionally to the other bound function albo whether it will
        replace the previous function. See bind dla the zwróć value."""
        zwróć self._bind((self._w, 'bind', tagOrId),
                  sequence, func, add)
    def canvasx(self, screenx, gridspacing=Nic):
        """Return the canvas x coordinate of pixel position SCREENX rounded
        to nearest multiple of GRIDSPACING units."""
        zwróć self.tk.getdouble(self.tk.call(
            self._w, 'canvasx', screenx, gridspacing))
    def canvasy(self, screeny, gridspacing=Nic):
        """Return the canvas y coordinate of pixel position SCREENY rounded
        to nearest multiple of GRIDSPACING units."""
        zwróć self.tk.getdouble(self.tk.call(
            self._w, 'canvasy', screeny, gridspacing))
    def coords(self, *args):
        """Return a list of coordinates dla the item given w ARGS."""
        # XXX Should use _flatten on args
        zwróć [self.tk.getdouble(x) dla x w
                           self.tk.splitlist(
                   self.tk.call((self._w, 'coords') + args))]
    def _create(self, itemType, args, kw): # Args: (val, val, ..., cnf={})
        """Internal function."""
        args = _flatten(args)
        cnf = args[-1]
        jeżeli isinstance(cnf, (dict, tuple)):
            args = args[:-1]
        inaczej:
            cnf = {}
        zwróć self.tk.getint(self.tk.call(
            self._w, 'create', itemType,
            *(args + self._options(cnf, kw))))
    def create_arc(self, *args, **kw):
        """Create arc shaped region przy coordinates x1,y1,x2,y2."""
        zwróć self._create('arc', args, kw)
    def create_bitmap(self, *args, **kw):
        """Create bitmap przy coordinates x1,y1."""
        zwróć self._create('bitmap', args, kw)
    def create_image(self, *args, **kw):
        """Create image item przy coordinates x1,y1."""
        zwróć self._create('image', args, kw)
    def create_line(self, *args, **kw):
        """Create line przy coordinates x1,y1,...,xn,yn."""
        zwróć self._create('line', args, kw)
    def create_oval(self, *args, **kw):
        """Create oval przy coordinates x1,y1,x2,y2."""
        zwróć self._create('oval', args, kw)
    def create_polygon(self, *args, **kw):
        """Create polygon przy coordinates x1,y1,...,xn,yn."""
        zwróć self._create('polygon', args, kw)
    def create_rectangle(self, *args, **kw):
        """Create rectangle przy coordinates x1,y1,x2,y2."""
        zwróć self._create('rectangle', args, kw)
    def create_text(self, *args, **kw):
        """Create text przy coordinates x1,y1."""
        zwróć self._create('text', args, kw)
    def create_window(self, *args, **kw):
        """Create window przy coordinates x1,y1,x2,y2."""
        zwróć self._create('window', args, kw)
    def dchars(self, *args):
        """Delete characters of text items identified by tag albo id w ARGS (possibly
        several times) z FIRST to LAST character (including)."""
        self.tk.call((self._w, 'dchars') + args)
    def delete(self, *args):
        """Delete items identified by all tag albo ids contained w ARGS."""
        self.tk.call((self._w, 'delete') + args)
    def dtag(self, *args):
        """Delete tag albo id given jako last arguments w ARGS z items
        identified by first argument w ARGS."""
        self.tk.call((self._w, 'dtag') + args)
    def find(self, *args):
        """Internal function."""
        zwróć self._getints(
            self.tk.call((self._w, 'find') + args)) albo ()
    def find_above(self, tagOrId):
        """Return items above TAGORID."""
        zwróć self.find('above', tagOrId)
    def find_all(self):
        """Return all items."""
        zwróć self.find('all')
    def find_below(self, tagOrId):
        """Return all items below TAGORID."""
        zwróć self.find('below', tagOrId)
    def find_closest(self, x, y, halo=Nic, start=Nic):
        """Return item which jest closest to pixel at X, Y.
        If several match take the top-most.
        All items closer than HALO are considered overlapping (all are
        closests). If START jest specified the next below this tag jest taken."""
        zwróć self.find('closest', x, y, halo, start)
    def find_enclosed(self, x1, y1, x2, y2):
        """Return all items w rectangle defined
        by X1,Y1,X2,Y2."""
        zwróć self.find('enclosed', x1, y1, x2, y2)
    def find_overlapping(self, x1, y1, x2, y2):
        """Return all items which overlap the rectangle
        defined by X1,Y1,X2,Y2."""
        zwróć self.find('overlapping', x1, y1, x2, y2)
    def find_withtag(self, tagOrId):
        """Return all items przy TAGORID."""
        zwróć self.find('withtag', tagOrId)
    def focus(self, *args):
        """Set focus to the first item specified w ARGS."""
        zwróć self.tk.call((self._w, 'focus') + args)
    def gettags(self, *args):
        """Return tags associated przy the first item specified w ARGS."""
        zwróć self.tk.splitlist(
            self.tk.call((self._w, 'gettags') + args))
    def icursor(self, *args):
        """Set cursor at position POS w the item identified by TAGORID.
        In ARGS TAGORID must be first."""
        self.tk.call((self._w, 'icursor') + args)
    def index(self, *args):
        """Return position of cursor jako integer w item specified w ARGS."""
        zwróć self.tk.getint(self.tk.call((self._w, 'index') + args))
    def insert(self, *args):
        """Insert TEXT w item TAGORID at position POS. ARGS must
        be TAGORID POS TEXT."""
        self.tk.call((self._w, 'insert') + args)
    def itemcget(self, tagOrId, option):
        """Return the resource value dla an OPTION dla item TAGORID."""
        zwróć self.tk.call(
            (self._w, 'itemcget') + (tagOrId, '-'+option))
    def itemconfigure(self, tagOrId, cnf=Nic, **kw):
        """Configure resources of an item TAGORID.

        The values dla resources are specified jako keyword
        arguments. To get an overview about
        the allowed keyword arguments call the method without arguments.
        """
        zwróć self._configure(('itemconfigure', tagOrId), cnf, kw)
    itemconfig = itemconfigure
    # lower, tkraise/lift hide Misc.lower, Misc.tkraise/lift,
    # so the preferred name dla them jest tag_lower, tag_raise
    # (similar to tag_bind, oraz similar to the Text widget);
    # unfortunately can't delete the old ones yet (maybe w 1.6)
    def tag_lower(self, *args):
        """Lower an item TAGORID given w ARGS
        (optional below another item)."""
        self.tk.call((self._w, 'lower') + args)
    lower = tag_lower
    def move(self, *args):
        """Move an item TAGORID given w ARGS."""
        self.tk.call((self._w, 'move') + args)
    def postscript(self, cnf={}, **kw):
        """Print the contents of the canvas to a postscript
        file. Valid options: colormap, colormode, file, fontmap,
        height, pageanchor, pageheight, pagewidth, pagex, pagey,
        rotate, witdh, x, y."""
        zwróć self.tk.call((self._w, 'postscript') +
                    self._options(cnf, kw))
    def tag_raise(self, *args):
        """Raise an item TAGORID given w ARGS
        (optional above another item)."""
        self.tk.call((self._w, 'raise') + args)
    lift = tkraise = tag_raise
    def scale(self, *args):
        """Scale item TAGORID przy XORIGIN, YORIGIN, XSCALE, YSCALE."""
        self.tk.call((self._w, 'scale') + args)
    def scan_mark(self, x, y):
        """Remember the current X, Y coordinates."""
        self.tk.call(self._w, 'scan', 'mark', x, y)
    def scan_dragto(self, x, y, gain=10):
        """Adjust the view of the canvas to GAIN times the
        difference between X oraz Y oraz the coordinates given w
        scan_mark."""
        self.tk.call(self._w, 'scan', 'dragto', x, y, gain)
    def select_adjust(self, tagOrId, index):
        """Adjust the end of the selection near the cursor of an item TAGORID to index."""
        self.tk.call(self._w, 'select', 'adjust', tagOrId, index)
    def select_clear(self):
        """Clear the selection jeżeli it jest w this widget."""
        self.tk.call(self._w, 'select', 'clear')
    def select_from(self, tagOrId, index):
        """Set the fixed end of a selection w item TAGORID to INDEX."""
        self.tk.call(self._w, 'select', 'from', tagOrId, index)
    def select_item(self):
        """Return the item which has the selection."""
        zwróć self.tk.call(self._w, 'select', 'item') albo Nic
    def select_to(self, tagOrId, index):
        """Set the variable end of a selection w item TAGORID to INDEX."""
        self.tk.call(self._w, 'select', 'to', tagOrId, index)
    def type(self, tagOrId):
        """Return the type of the item TAGORID."""
        zwróć self.tk.call(self._w, 'type', tagOrId) albo Nic

klasa Checkbutton(Widget):
    """Checkbutton widget which jest either w on- albo off-state."""
    def __init__(self, master=Nic, cnf={}, **kw):
        """Construct a checkbutton widget przy the parent MASTER.

        Valid resource names: activebackground, activeforeground, anchor,
        background, bd, bg, bitmap, borderwidth, command, cursor,
        disabledforeground, fg, font, foreground, height,
        highlightbackground, highlightcolor, highlightthickness, image,
        indicatoron, justify, offvalue, onvalue, padx, pady, relief,
        selectcolor, selectimage, state, takefocus, text, textvariable,
        underline, variable, width, wraplength."""
        Widget.__init__(self, master, 'checkbutton', cnf, kw)
    def deselect(self):
        """Put the button w off-state."""
        self.tk.call(self._w, 'deselect')
    def flash(self):
        """Flash the button."""
        self.tk.call(self._w, 'flash')
    def invoke(self):
        """Toggle the button oraz invoke a command jeżeli given jako resource."""
        zwróć self.tk.call(self._w, 'invoke')
    def select(self):
        """Put the button w on-state."""
        self.tk.call(self._w, 'select')
    def toggle(self):
        """Toggle the button."""
        self.tk.call(self._w, 'toggle')

klasa Entry(Widget, XView):
    """Entry widget which allows to display simple text."""
    def __init__(self, master=Nic, cnf={}, **kw):
        """Construct an entry widget przy the parent MASTER.

        Valid resource names: background, bd, bg, borderwidth, cursor,
        exportselection, fg, font, foreground, highlightbackground,
        highlightcolor, highlightthickness, insertbackground,
        insertborderwidth, insertofftime, insertontime, insertwidth,
        invalidcommand, invcmd, justify, relief, selectbackground,
        selectborderwidth, selectforeground, show, state, takefocus,
        textvariable, validate, validatecommand, vcmd, width,
        xscrollcommand."""
        Widget.__init__(self, master, 'entry', cnf, kw)
    def delete(self, first, last=Nic):
        """Delete text z FIRST to LAST (nie included)."""
        self.tk.call(self._w, 'delete', first, last)
    def get(self):
        """Return the text."""
        zwróć self.tk.call(self._w, 'get')
    def icursor(self, index):
        """Insert cursor at INDEX."""
        self.tk.call(self._w, 'icursor', index)
    def index(self, index):
        """Return position of cursor."""
        zwróć self.tk.getint(self.tk.call(
            self._w, 'index', index))
    def insert(self, index, string):
        """Insert STRING at INDEX."""
        self.tk.call(self._w, 'insert', index, string)
    def scan_mark(self, x):
        """Remember the current X, Y coordinates."""
        self.tk.call(self._w, 'scan', 'mark', x)
    def scan_dragto(self, x):
        """Adjust the view of the canvas to 10 times the
        difference between X oraz Y oraz the coordinates given w
        scan_mark."""
        self.tk.call(self._w, 'scan', 'dragto', x)
    def selection_adjust(self, index):
        """Adjust the end of the selection near the cursor to INDEX."""
        self.tk.call(self._w, 'selection', 'adjust', index)
    select_adjust = selection_adjust
    def selection_clear(self):
        """Clear the selection jeżeli it jest w this widget."""
        self.tk.call(self._w, 'selection', 'clear')
    select_clear = selection_clear
    def selection_from(self, index):
        """Set the fixed end of a selection to INDEX."""
        self.tk.call(self._w, 'selection', 'from', index)
    select_z = selection_from
    def selection_present(self):
        """Return Prawda jeżeli there are characters selected w the entry, Nieprawda
        otherwise."""
        zwróć self.tk.getboolean(
            self.tk.call(self._w, 'selection', 'present'))
    select_present = selection_present
    def selection_range(self, start, end):
        """Set the selection z START to END (nie included)."""
        self.tk.call(self._w, 'selection', 'range', start, end)
    select_range = selection_range
    def selection_to(self, index):
        """Set the variable end of a selection to INDEX."""
        self.tk.call(self._w, 'selection', 'to', index)
    select_to = selection_to

klasa Frame(Widget):
    """Frame widget which may contain other widgets oraz can have a 3D border."""
    def __init__(self, master=Nic, cnf={}, **kw):
        """Construct a frame widget przy the parent MASTER.

        Valid resource names: background, bd, bg, borderwidth, class,
        colormap, container, cursor, height, highlightbackground,
        highlightcolor, highlightthickness, relief, takefocus, visual, width."""
        cnf = _cnfmerge((cnf, kw))
        extra = ()
        jeżeli 'class_' w cnf:
            extra = ('-class', cnf['class_'])
            usuń cnf['class_']
        albo_inaczej 'class' w cnf:
            extra = ('-class', cnf['class'])
            usuń cnf['class']
        Widget.__init__(self, master, 'frame', cnf, {}, extra)

klasa Label(Widget):
    """Label widget which can display text oraz bitmaps."""
    def __init__(self, master=Nic, cnf={}, **kw):
        """Construct a label widget przy the parent MASTER.

        STANDARD OPTIONS

            activebackground, activeforeground, anchor,
            background, bitmap, borderwidth, cursor,
            disabledforeground, font, foreground,
            highlightbackground, highlightcolor,
            highlightthickness, image, justify,
            padx, pady, relief, takefocus, text,
            textvariable, underline, wraplength

        WIDGET-SPECIFIC OPTIONS

            height, state, width

        """
        Widget.__init__(self, master, 'label', cnf, kw)

klasa Listbox(Widget, XView, YView):
    """Listbox widget which can display a list of strings."""
    def __init__(self, master=Nic, cnf={}, **kw):
        """Construct a listbox widget przy the parent MASTER.

        Valid resource names: background, bd, bg, borderwidth, cursor,
        exportselection, fg, font, foreground, height, highlightbackground,
        highlightcolor, highlightthickness, relief, selectbackground,
        selectborderwidth, selectforeground, selectmode, setgrid, takefocus,
        width, xscrollcommand, yscrollcommand, listvariable."""
        Widget.__init__(self, master, 'listbox', cnf, kw)
    def activate(self, index):
        """Activate item identified by INDEX."""
        self.tk.call(self._w, 'activate', index)
    def bbox(self, index):
        """Return a tuple of X1,Y1,X2,Y2 coordinates dla a rectangle
        which encloses the item identified by the given index."""
        zwróć self._getints(self.tk.call(self._w, 'bbox', index)) albo Nic
    def curselection(self):
        """Return the indices of currently selected item."""
        zwróć self._getints(self.tk.call(self._w, 'curselection')) albo ()
    def delete(self, first, last=Nic):
        """Delete items z FIRST to LAST (included)."""
        self.tk.call(self._w, 'delete', first, last)
    def get(self, first, last=Nic):
        """Get list of items z FIRST to LAST (included)."""
        jeżeli last jest nie Nic:
            zwróć self.tk.splitlist(self.tk.call(
                self._w, 'get', first, last))
        inaczej:
            zwróć self.tk.call(self._w, 'get', first)
    def index(self, index):
        """Return index of item identified przy INDEX."""
        i = self.tk.call(self._w, 'index', index)
        jeżeli i == 'none': zwróć Nic
        zwróć self.tk.getint(i)
    def insert(self, index, *elements):
        """Insert ELEMENTS at INDEX."""
        self.tk.call((self._w, 'insert', index) + elements)
    def nearest(self, y):
        """Get index of item which jest nearest to y coordinate Y."""
        zwróć self.tk.getint(self.tk.call(
            self._w, 'nearest', y))
    def scan_mark(self, x, y):
        """Remember the current X, Y coordinates."""
        self.tk.call(self._w, 'scan', 'mark', x, y)
    def scan_dragto(self, x, y):
        """Adjust the view of the listbox to 10 times the
        difference between X oraz Y oraz the coordinates given w
        scan_mark."""
        self.tk.call(self._w, 'scan', 'dragto', x, y)
    def see(self, index):
        """Scroll such that INDEX jest visible."""
        self.tk.call(self._w, 'see', index)
    def selection_anchor(self, index):
        """Set the fixed end oft the selection to INDEX."""
        self.tk.call(self._w, 'selection', 'anchor', index)
    select_anchor = selection_anchor
    def selection_clear(self, first, last=Nic):
        """Clear the selection z FIRST to LAST (included)."""
        self.tk.call(self._w,
                 'selection', 'clear', first, last)
    select_clear = selection_clear
    def selection_includes(self, index):
        """Return 1 jeżeli INDEX jest part of the selection."""
        zwróć self.tk.getboolean(self.tk.call(
            self._w, 'selection', 'includes', index))
    select_includes = selection_includes
    def selection_set(self, first, last=Nic):
        """Set the selection z FIRST to LAST (included) without
        changing the currently selected elements."""
        self.tk.call(self._w, 'selection', 'set', first, last)
    select_set = selection_set
    def size(self):
        """Return the number of elements w the listbox."""
        zwróć self.tk.getint(self.tk.call(self._w, 'size'))
    def itemcget(self, index, option):
        """Return the resource value dla an ITEM oraz an OPTION."""
        zwróć self.tk.call(
            (self._w, 'itemcget') + (index, '-'+option))
    def itemconfigure(self, index, cnf=Nic, **kw):
        """Configure resources of an ITEM.

        The values dla resources are specified jako keyword arguments.
        To get an overview about the allowed keyword arguments
        call the method without arguments.
        Valid resource names: background, bg, foreground, fg,
        selectbackground, selectforeground."""
        zwróć self._configure(('itemconfigure', index), cnf, kw)
    itemconfig = itemconfigure

klasa Menu(Widget):
    """Menu widget which allows to display menu bars, pull-down menus oraz pop-up menus."""
    def __init__(self, master=Nic, cnf={}, **kw):
        """Construct menu widget przy the parent MASTER.

        Valid resource names: activebackground, activeborderwidth,
        activeforeground, background, bd, bg, borderwidth, cursor,
        disabledforeground, fg, font, foreground, postcommand, relief,
        selectcolor, takefocus, tearoff, tearoffcommand, title, type."""
        Widget.__init__(self, master, 'menu', cnf, kw)
    def tk_popup(self, x, y, entry=""):
        """Post the menu at position X,Y przy entry ENTRY."""
        self.tk.call('tk_popup', self._w, x, y, entry)
    def tk_bindForTraversal(self):
        # obsolete since Tk 4.0
        zaimportuj warnings
        warnings.warn('tk_bindForTraversal() does nothing oraz '
                      'will be removed w 3.6',
                      DeprecationWarning, stacklevel=2)
    def activate(self, index):
        """Activate entry at INDEX."""
        self.tk.call(self._w, 'activate', index)
    def add(self, itemType, cnf={}, **kw):
        """Internal function."""
        self.tk.call((self._w, 'add', itemType) +
                 self._options(cnf, kw))
    def add_cascade(self, cnf={}, **kw):
        """Add hierarchical menu item."""
        self.add('cascade', cnf albo kw)
    def add_checkbutton(self, cnf={}, **kw):
        """Add checkbutton menu item."""
        self.add('checkbutton', cnf albo kw)
    def add_command(self, cnf={}, **kw):
        """Add command menu item."""
        self.add('command', cnf albo kw)
    def add_radiobutton(self, cnf={}, **kw):
        """Addd radio menu item."""
        self.add('radiobutton', cnf albo kw)
    def add_separator(self, cnf={}, **kw):
        """Add separator."""
        self.add('separator', cnf albo kw)
    def insert(self, index, itemType, cnf={}, **kw):
        """Internal function."""
        self.tk.call((self._w, 'insert', index, itemType) +
                 self._options(cnf, kw))
    def insert_cascade(self, index, cnf={}, **kw):
        """Add hierarchical menu item at INDEX."""
        self.insert(index, 'cascade', cnf albo kw)
    def insert_checkbutton(self, index, cnf={}, **kw):
        """Add checkbutton menu item at INDEX."""
        self.insert(index, 'checkbutton', cnf albo kw)
    def insert_command(self, index, cnf={}, **kw):
        """Add command menu item at INDEX."""
        self.insert(index, 'command', cnf albo kw)
    def insert_radiobutton(self, index, cnf={}, **kw):
        """Addd radio menu item at INDEX."""
        self.insert(index, 'radiobutton', cnf albo kw)
    def insert_separator(self, index, cnf={}, **kw):
        """Add separator at INDEX."""
        self.insert(index, 'separator', cnf albo kw)
    def delete(self, index1, index2=Nic):
        """Delete menu items between INDEX1 oraz INDEX2 (included)."""
        jeżeli index2 jest Nic:
            index2 = index1

        num_index1, num_index2 = self.index(index1), self.index(index2)
        jeżeli (num_index1 jest Nic) albo (num_index2 jest Nic):
            num_index1, num_index2 = 0, -1

        dla i w range(num_index1, num_index2 + 1):
            jeżeli 'command' w self.entryconfig(i):
                c = str(self.entrycget(i, 'command'))
                jeżeli c:
                    self.deletecommand(c)
        self.tk.call(self._w, 'delete', index1, index2)
    def entrycget(self, index, option):
        """Return the resource value of an menu item dla OPTION at INDEX."""
        zwróć self.tk.call(self._w, 'entrycget', index, '-' + option)
    def entryconfigure(self, index, cnf=Nic, **kw):
        """Configure a menu item at INDEX."""
        zwróć self._configure(('entryconfigure', index), cnf, kw)
    entryconfig = entryconfigure
    def index(self, index):
        """Return the index of a menu item identified by INDEX."""
        i = self.tk.call(self._w, 'index', index)
        jeżeli i == 'none': zwróć Nic
        zwróć self.tk.getint(i)
    def invoke(self, index):
        """Invoke a menu item identified by INDEX oraz execute
        the associated command."""
        zwróć self.tk.call(self._w, 'invoke', index)
    def post(self, x, y):
        """Display a menu at position X,Y."""
        self.tk.call(self._w, 'post', x, y)
    def type(self, index):
        """Return the type of the menu item at INDEX."""
        zwróć self.tk.call(self._w, 'type', index)
    def unpost(self):
        """Unmap a menu."""
        self.tk.call(self._w, 'unpost')
    def xposition(self, index): # new w Tk 8.5
        """Return the x-position of the leftmost pixel of the menu item
        at INDEX."""
        zwróć self.tk.getint(self.tk.call(self._w, 'xposition', index))
    def yposition(self, index):
        """Return the y-position of the topmost pixel of the menu item at INDEX."""
        zwróć self.tk.getint(self.tk.call(
            self._w, 'yposition', index))

klasa Menubutton(Widget):
    """Menubutton widget, obsolete since Tk8.0."""
    def __init__(self, master=Nic, cnf={}, **kw):
        Widget.__init__(self, master, 'menubutton', cnf, kw)

klasa Message(Widget):
    """Message widget to display multiline text. Obsolete since Label does it too."""
    def __init__(self, master=Nic, cnf={}, **kw):
        Widget.__init__(self, master, 'message', cnf, kw)

klasa Radiobutton(Widget):
    """Radiobutton widget which shows only one of several buttons w on-state."""
    def __init__(self, master=Nic, cnf={}, **kw):
        """Construct a radiobutton widget przy the parent MASTER.

        Valid resource names: activebackground, activeforeground, anchor,
        background, bd, bg, bitmap, borderwidth, command, cursor,
        disabledforeground, fg, font, foreground, height,
        highlightbackground, highlightcolor, highlightthickness, image,
        indicatoron, justify, padx, pady, relief, selectcolor, selectimage,
        state, takefocus, text, textvariable, underline, value, variable,
        width, wraplength."""
        Widget.__init__(self, master, 'radiobutton', cnf, kw)
    def deselect(self):
        """Put the button w off-state."""

        self.tk.call(self._w, 'deselect')
    def flash(self):
        """Flash the button."""
        self.tk.call(self._w, 'flash')
    def invoke(self):
        """Toggle the button oraz invoke a command jeżeli given jako resource."""
        zwróć self.tk.call(self._w, 'invoke')
    def select(self):
        """Put the button w on-state."""
        self.tk.call(self._w, 'select')

klasa Scale(Widget):
    """Scale widget which can display a numerical scale."""
    def __init__(self, master=Nic, cnf={}, **kw):
        """Construct a scale widget przy the parent MASTER.

        Valid resource names: activebackground, background, bigincrement, bd,
        bg, borderwidth, command, cursor, digits, fg, font, foreground, from,
        highlightbackground, highlightcolor, highlightthickness, label,
        length, orient, relief, repeatdelay, repeatinterval, resolution,
        showvalue, sliderlength, sliderrelief, state, takefocus,
        tickinterval, to, troughcolor, variable, width."""
        Widget.__init__(self, master, 'scale', cnf, kw)
    def get(self):
        """Get the current value jako integer albo float."""
        value = self.tk.call(self._w, 'get')
        spróbuj:
            zwróć self.tk.getint(value)
        wyjąwszy (ValueError, TclError):
            zwróć self.tk.getdouble(value)
    def set(self, value):
        """Set the value to VALUE."""
        self.tk.call(self._w, 'set', value)
    def coords(self, value=Nic):
        """Return a tuple (X,Y) of the point along the centerline of the
        trough that corresponds to VALUE albo the current value jeżeli Nic jest
        given."""

        zwróć self._getints(self.tk.call(self._w, 'coords', value))
    def identify(self, x, y):
        """Return where the point X,Y lies. Valid zwróć values are "slider",
        "though1" oraz "though2"."""
        zwróć self.tk.call(self._w, 'identify', x, y)

klasa Scrollbar(Widget):
    """Scrollbar widget which displays a slider at a certain position."""
    def __init__(self, master=Nic, cnf={}, **kw):
        """Construct a scrollbar widget przy the parent MASTER.

        Valid resource names: activebackground, activerelief,
        background, bd, bg, borderwidth, command, cursor,
        elementborderwidth, highlightbackground,
        highlightcolor, highlightthickness, jump, orient,
        relief, repeatdelay, repeatinterval, takefocus,
        troughcolor, width."""
        Widget.__init__(self, master, 'scrollbar', cnf, kw)
    def activate(self, index=Nic):
        """Marks the element indicated by index jako active.
        The only index values understood by this method are "arrow1",
        "slider", albo "arrow2".  If any other value jest specified then no
        element of the scrollbar will be active.  If index jest nie specified,
        the method returns the name of the element that jest currently active,
        albo Nic jeżeli no element jest active."""
        zwróć self.tk.call(self._w, 'activate', index) albo Nic
    def delta(self, deltax, deltay):
        """Return the fractional change of the scrollbar setting jeżeli it
        would be moved by DELTAX albo DELTAY pixels."""
        zwróć self.tk.getdouble(
            self.tk.call(self._w, 'delta', deltax, deltay))
    def fraction(self, x, y):
        """Return the fractional value which corresponds to a slider
        position of X,Y."""
        zwróć self.tk.getdouble(self.tk.call(self._w, 'fraction', x, y))
    def identify(self, x, y):
        """Return the element under position X,Y jako one of
        "arrow1","slider","arrow2" albo ""."""
        zwróć self.tk.call(self._w, 'identify', x, y)
    def get(self):
        """Return the current fractional values (upper oraz lower end)
        of the slider position."""
        zwróć self._getdoubles(self.tk.call(self._w, 'get'))
    def set(self, first, last):
        """Set the fractional values of the slider position (upper oraz
        lower ends jako value between 0 oraz 1)."""
        self.tk.call(self._w, 'set', first, last)



klasa Text(Widget, XView, YView):
    """Text widget which can display text w various forms."""
    def __init__(self, master=Nic, cnf={}, **kw):
        """Construct a text widget przy the parent MASTER.

        STANDARD OPTIONS

            background, borderwidth, cursor,
            exportselection, font, foreground,
            highlightbackground, highlightcolor,
            highlightthickness, insertbackground,
            insertborderwidth, insertofftime,
            insertontime, insertwidth, padx, pady,
            relief, selectbackground,
            selectborderwidth, selectforeground,
            setgrid, takefocus,
            xscrollcommand, yscrollcommand,

        WIDGET-SPECIFIC OPTIONS

            autoseparators, height, maxundo,
            spacing1, spacing2, spacing3,
            state, tabs, undo, width, wrap,

        """
        Widget.__init__(self, master, 'text', cnf, kw)
    def bbox(self, index):
        """Return a tuple of (x,y,width,height) which gives the bounding
        box of the visible part of the character at the given index."""
        zwróć self._getints(
                self.tk.call(self._w, 'bbox', index)) albo Nic
    def compare(self, index1, op, index2):
        """Return whether between index INDEX1 oraz index INDEX2 the
        relation OP jest satisfied. OP jest one of <, <=, ==, >=, >, albo !=."""
        zwróć self.tk.getboolean(self.tk.call(
            self._w, 'compare', index1, op, index2))
    def count(self, index1, index2, *args): # new w Tk 8.5
        """Counts the number of relevant things between the two indices.
        If index1 jest after index2, the result will be a negative number
        (and this holds dla each of the possible options).

        The actual items which are counted depends on the options given by
        args. The result jest a list of integers, one dla the result of each
        counting option given. Valid counting options are "chars",
        "displaychars", "displayindices", "displaylines", "indices",
        "lines", "xpixels" oraz "ypixels". There jest an additional possible
        option "update", which jeżeli given then all subsequent options ensure
        that any possible out of date information jest recalculated."""
        args = ['-%s' % arg dla arg w args jeżeli nie arg.startswith('-')]
        args += [index1, index2]
        res = self.tk.call(self._w, 'count', *args) albo Nic
        jeżeli res jest nie Nic oraz len(args) <= 3:
            zwróć (res, )
        inaczej:
            zwróć res
    def debug(self, boolean=Nic):
        """Turn on the internal consistency checks of the B-Tree inside the text
        widget according to BOOLEAN."""
        jeżeli boolean jest Nic:
            zwróć self.tk.getboolean(self.tk.call(self._w, 'debug'))
        self.tk.call(self._w, 'debug', boolean)
    def delete(self, index1, index2=Nic):
        """Delete the characters between INDEX1 oraz INDEX2 (nie included)."""
        self.tk.call(self._w, 'delete', index1, index2)
    def dlineinfo(self, index):
        """Return tuple (x,y,width,height,baseline) giving the bounding box
        oraz baseline position of the visible part of the line containing
        the character at INDEX."""
        zwróć self._getints(self.tk.call(self._w, 'dlineinfo', index))
    def dump(self, index1, index2=Nic, command=Nic, **kw):
        """Return the contents of the widget between index1 oraz index2.

        The type of contents returned w filtered based on the keyword
        parameters; jeżeli 'all', 'image', 'mark', 'tag', 'text', albo 'window' are
        given oraz true, then the corresponding items are returned. The result
        jest a list of triples of the form (key, value, index). If none of the
        keywords are true then 'all' jest used by default.

        If the 'command' argument jest given, it jest called once dla each element
        of the list of triples, przy the values of each triple serving jako the
        arguments to the function. In this case the list jest nie returned."""
        args = []
        func_name = Nic
        result = Nic
        jeżeli nie command:
            # Never call the dump command without the -command flag, since the
            # output could involve Tcl quoting oraz would be a pain to parse
            # right. Instead just set the command to build a list of triples
            # jako jeżeli we had done the parsing.
            result = []
            def append_triple(key, value, index, result=result):
                result.append((key, value, index))
            command = append_triple
        spróbuj:
            jeżeli nie isinstance(command, str):
                func_name = command = self._register(command)
            args += ["-command", command]
            dla key w kw:
                jeżeli kw[key]: args.append("-" + key)
            args.append(index1)
            jeżeli index2:
                args.append(index2)
            self.tk.call(self._w, "dump", *args)
            zwróć result
        w_końcu:
            jeżeli func_name:
                self.deletecommand(func_name)

    ## new w tk8.4
    def edit(self, *args):
        """Internal method

        This method controls the undo mechanism oraz
        the modified flag. The exact behavior of the
        command depends on the option argument that
        follows the edit argument. The following forms
        of the command are currently supported:

        edit_modified, edit_redo, edit_reset, edit_separator
        oraz edit_undo

        """
        zwróć self.tk.call(self._w, 'edit', *args)

    def edit_modified(self, arg=Nic):
        """Get albo Set the modified flag

        If arg jest nie specified, returns the modified
        flag of the widget. The insert, delete, edit undo oraz
        edit redo commands albo the user can set albo clear the
        modified flag. If boolean jest specified, sets the
        modified flag of the widget to arg.
        """
        zwróć self.edit("modified", arg)

    def edit_redo(self):
        """Redo the last undone edit

        When the undo option jest true, reapplies the last
        undone edits provided no other edits were done since
        then. Generates an error when the redo stack jest empty.
        Does nothing when the undo option jest false.
        """
        zwróć self.edit("redo")

    def edit_reset(self):
        """Clears the undo oraz redo stacks
        """
        zwróć self.edit("reset")

    def edit_separator(self):
        """Inserts a separator (boundary) on the undo stack.

        Does nothing when the undo option jest false
        """
        zwróć self.edit("separator")

    def edit_undo(self):
        """Undoes the last edit action

        If the undo option jest true. An edit action jest defined
        jako all the insert oraz delete commands that are recorded
        on the undo stack w between two separators. Generates
        an error when the undo stack jest empty. Does nothing
        when the undo option jest false
        """
        zwróć self.edit("undo")

    def get(self, index1, index2=Nic):
        """Return the text z INDEX1 to INDEX2 (nie included)."""
        zwróć self.tk.call(self._w, 'get', index1, index2)
    # (Image commands are new w 8.0)
    def image_cget(self, index, option):
        """Return the value of OPTION of an embedded image at INDEX."""
        jeżeli option[:1] != "-":
            option = "-" + option
        jeżeli option[-1:] == "_":
            option = option[:-1]
        zwróć self.tk.call(self._w, "image", "cget", index, option)
    def image_configure(self, index, cnf=Nic, **kw):
        """Configure an embedded image at INDEX."""
        zwróć self._configure(('image', 'configure', index), cnf, kw)
    def image_create(self, index, cnf={}, **kw):
        """Create an embedded image at INDEX."""
        zwróć self.tk.call(
                 self._w, "image", "create", index,
                 *self._options(cnf, kw))
    def image_names(self):
        """Return all names of embedded images w this widget."""
        zwróć self.tk.call(self._w, "image", "names")
    def index(self, index):
        """Return the index w the form line.char dla INDEX."""
        zwróć str(self.tk.call(self._w, 'index', index))
    def insert(self, index, chars, *args):
        """Insert CHARS before the characters at INDEX. An additional
        tag can be given w ARGS. Additional CHARS oraz tags can follow w ARGS."""
        self.tk.call((self._w, 'insert', index, chars) + args)
    def mark_gravity(self, markName, direction=Nic):
        """Change the gravity of a mark MARKNAME to DIRECTION (LEFT albo RIGHT).
        Return the current value jeżeli Nic jest given dla DIRECTION."""
        zwróć self.tk.call(
            (self._w, 'mark', 'gravity', markName, direction))
    def mark_names(self):
        """Return all mark names."""
        zwróć self.tk.splitlist(self.tk.call(
            self._w, 'mark', 'names'))
    def mark_set(self, markName, index):
        """Set mark MARKNAME before the character at INDEX."""
        self.tk.call(self._w, 'mark', 'set', markName, index)
    def mark_unset(self, *markNames):
        """Delete all marks w MARKNAMES."""
        self.tk.call((self._w, 'mark', 'unset') + markNames)
    def mark_next(self, index):
        """Return the name of the next mark after INDEX."""
        zwróć self.tk.call(self._w, 'mark', 'next', index) albo Nic
    def mark_previous(self, index):
        """Return the name of the previous mark before INDEX."""
        zwróć self.tk.call(self._w, 'mark', 'previous', index) albo Nic
    def peer_create(self, newPathName, cnf={}, **kw): # new w Tk 8.5
        """Creates a peer text widget przy the given newPathName, oraz any
        optional standard configuration options. By default the peer will
        have the same start oraz end line jako the parent widget, but
        these can be overriden przy the standard configuration options."""
        self.tk.call(self._w, 'peer', 'create', newPathName,
            *self._options(cnf, kw))
    def peer_names(self): # new w Tk 8.5
        """Returns a list of peers of this widget (this does nie include
        the widget itself)."""
        zwróć self.tk.splitlist(self.tk.call(self._w, 'peer', 'names'))
    def replace(self, index1, index2, chars, *args): # new w Tk 8.5
        """Replaces the range of characters between index1 oraz index2 with
        the given characters oraz tags specified by args.

        See the method insert dla some more information about args, oraz the
        method delete dla information about the indices."""
        self.tk.call(self._w, 'replace', index1, index2, chars, *args)
    def scan_mark(self, x, y):
        """Remember the current X, Y coordinates."""
        self.tk.call(self._w, 'scan', 'mark', x, y)
    def scan_dragto(self, x, y):
        """Adjust the view of the text to 10 times the
        difference between X oraz Y oraz the coordinates given w
        scan_mark."""
        self.tk.call(self._w, 'scan', 'dragto', x, y)
    def search(self, pattern, index, stopindex=Nic,
           forwards=Nic, backwards=Nic, exact=Nic,
           regexp=Nic, nocase=Nic, count=Nic, elide=Nic):
        """Search PATTERN beginning z INDEX until STOPINDEX.
        Return the index of the first character of a match albo an
        empty string."""
        args = [self._w, 'search']
        jeżeli forwards: args.append('-forwards')
        jeżeli backwards: args.append('-backwards')
        jeżeli exact: args.append('-exact')
        jeżeli regexp: args.append('-regexp')
        jeżeli nocase: args.append('-nocase')
        jeżeli elide: args.append('-elide')
        jeżeli count: args.append('-count'); args.append(count)
        jeżeli pattern oraz pattern[0] == '-': args.append('--')
        args.append(pattern)
        args.append(index)
        jeżeli stopindex: args.append(stopindex)
        zwróć str(self.tk.call(tuple(args)))
    def see(self, index):
        """Scroll such that the character at INDEX jest visible."""
        self.tk.call(self._w, 'see', index)
    def tag_add(self, tagName, index1, *args):
        """Add tag TAGNAME to all characters between INDEX1 oraz index2 w ARGS.
        Additional pairs of indices may follow w ARGS."""
        self.tk.call(
            (self._w, 'tag', 'add', tagName, index1) + args)
    def tag_unbind(self, tagName, sequence, funcid=Nic):
        """Unbind dla all characters przy TAGNAME dla event SEQUENCE  the
        function identified przy FUNCID."""
        self.tk.call(self._w, 'tag', 'bind', tagName, sequence, '')
        jeżeli funcid:
            self.deletecommand(funcid)
    def tag_bind(self, tagName, sequence, func, add=Nic):
        """Bind to all characters przy TAGNAME at event SEQUENCE a call to function FUNC.

        An additional boolean parameter ADD specifies whether FUNC will be
        called additionally to the other bound function albo whether it will
        replace the previous function. See bind dla the zwróć value."""
        zwróć self._bind((self._w, 'tag', 'bind', tagName),
                  sequence, func, add)
    def tag_cget(self, tagName, option):
        """Return the value of OPTION dla tag TAGNAME."""
        jeżeli option[:1] != '-':
            option = '-' + option
        jeżeli option[-1:] == '_':
            option = option[:-1]
        zwróć self.tk.call(self._w, 'tag', 'cget', tagName, option)
    def tag_configure(self, tagName, cnf=Nic, **kw):
        """Configure a tag TAGNAME."""
        zwróć self._configure(('tag', 'configure', tagName), cnf, kw)
    tag_config = tag_configure
    def tag_delete(self, *tagNames):
        """Delete all tags w TAGNAMES."""
        self.tk.call((self._w, 'tag', 'delete') + tagNames)
    def tag_lower(self, tagName, belowThis=Nic):
        """Change the priority of tag TAGNAME such that it jest lower
        than the priority of BELOWTHIS."""
        self.tk.call(self._w, 'tag', 'lower', tagName, belowThis)
    def tag_names(self, index=Nic):
        """Return a list of all tag names."""
        zwróć self.tk.splitlist(
            self.tk.call(self._w, 'tag', 'names', index))
    def tag_nextrange(self, tagName, index1, index2=Nic):
        """Return a list of start oraz end index dla the first sequence of
        characters between INDEX1 oraz INDEX2 which all have tag TAGNAME.
        The text jest searched forward z INDEX1."""
        zwróć self.tk.splitlist(self.tk.call(
            self._w, 'tag', 'nextrange', tagName, index1, index2))
    def tag_prevrange(self, tagName, index1, index2=Nic):
        """Return a list of start oraz end index dla the first sequence of
        characters between INDEX1 oraz INDEX2 which all have tag TAGNAME.
        The text jest searched backwards z INDEX1."""
        zwróć self.tk.splitlist(self.tk.call(
            self._w, 'tag', 'prevrange', tagName, index1, index2))
    def tag_raise(self, tagName, aboveThis=Nic):
        """Change the priority of tag TAGNAME such that it jest higher
        than the priority of ABOVETHIS."""
        self.tk.call(
            self._w, 'tag', 'raise', tagName, aboveThis)
    def tag_ranges(self, tagName):
        """Return a list of ranges of text which have tag TAGNAME."""
        zwróć self.tk.splitlist(self.tk.call(
            self._w, 'tag', 'ranges', tagName))
    def tag_remove(self, tagName, index1, index2=Nic):
        """Remove tag TAGNAME z all characters between INDEX1 oraz INDEX2."""
        self.tk.call(
            self._w, 'tag', 'remove', tagName, index1, index2)
    def window_cget(self, index, option):
        """Return the value of OPTION of an embedded window at INDEX."""
        jeżeli option[:1] != '-':
            option = '-' + option
        jeżeli option[-1:] == '_':
            option = option[:-1]
        zwróć self.tk.call(self._w, 'window', 'cget', index, option)
    def window_configure(self, index, cnf=Nic, **kw):
        """Configure an embedded window at INDEX."""
        zwróć self._configure(('window', 'configure', index), cnf, kw)
    window_config = window_configure
    def window_create(self, index, cnf={}, **kw):
        """Create a window at INDEX."""
        self.tk.call(
              (self._w, 'window', 'create', index)
              + self._options(cnf, kw))
    def window_names(self):
        """Return all names of embedded windows w this widget."""
        zwróć self.tk.splitlist(
            self.tk.call(self._w, 'window', 'names'))
    def yview_pickplace(self, *what):
        """Obsolete function, use see."""
        self.tk.call((self._w, 'yview', '-pickplace') + what)


klasa _setit:
    """Internal class. It wraps the command w the widget OptionMenu."""
    def __init__(self, var, value, callback=Nic):
        self.__value = value
        self.__var = var
        self.__callback = callback
    def __call__(self, *args):
        self.__var.set(self.__value)
        jeżeli self.__callback:
            self.__callback(self.__value, *args)

klasa OptionMenu(Menubutton):
    """OptionMenu which allows the user to select a value z a menu."""
    def __init__(self, master, variable, value, *values, **kwargs):
        """Construct an optionmenu widget przy the parent MASTER, with
        the resource textvariable set to VARIABLE, the initially selected
        value VALUE, the other menu values VALUES oraz an additional
        keyword argument command."""
        kw = {"borderwidth": 2, "textvariable": variable,
              "indicatoron": 1, "relief": RAISED, "anchor": "c",
              "highlightthickness": 2}
        Widget.__init__(self, master, "menubutton", kw)
        self.widgetName = 'tk_optionMenu'
        menu = self.__menu = Menu(self, name="menu", tearoff=0)
        self.menuname = menu._w
        # 'command' jest the only supported keyword
        callback = kwargs.get('command')
        jeżeli 'command' w kwargs:
            usuń kwargs['command']
        jeżeli kwargs:
            podnieś TclError('unknown option -'+kwargs.keys()[0])
        menu.add_command(label=value,
                 command=_setit(variable, value, callback))
        dla v w values:
            menu.add_command(label=v,
                     command=_setit(variable, v, callback))
        self["menu"] = menu

    def __getitem__(self, name):
        jeżeli name == 'menu':
            zwróć self.__menu
        zwróć Widget.__getitem__(self, name)

    def destroy(self):
        """Destroy this widget oraz the associated menu."""
        Menubutton.destroy(self)
        self.__menu = Nic

klasa Image:
    """Base klasa dla images."""
    _last_id = 0
    def __init__(self, imgtype, name=Nic, cnf={}, master=Nic, **kw):
        self.name = Nic
        jeżeli nie master:
            master = _default_root
            jeżeli nie master:
                podnieś RuntimeError('Too early to create image')
        self.tk = getattr(master, 'tk', master)
        jeżeli nie name:
            Image._last_id += 1
            name = "pyimage%r" % (Image._last_id,) # tk itself would use image<x>
            # The following jest needed dla systems where id(x)
            # can zwróć a negative number, such jako Linux/m68k:
            jeżeli name[0] == '-': name = '_' + name[1:]
        jeżeli kw oraz cnf: cnf = _cnfmerge((cnf, kw))
        albo_inaczej kw: cnf = kw
        options = ()
        dla k, v w cnf.items():
            jeżeli callable(v):
                v = self._register(v)
            options = options + ('-'+k, v)
        self.tk.call(('image', 'create', imgtype, name,) + options)
        self.name = name
    def __str__(self): zwróć self.name
    def __del__(self):
        jeżeli self.name:
            spróbuj:
                self.tk.call('image', 'delete', self.name)
            wyjąwszy TclError:
                # May happen jeżeli the root was destroyed
                dalej
    def __setitem__(self, key, value):
        self.tk.call(self.name, 'configure', '-'+key, value)
    def __getitem__(self, key):
        zwróć self.tk.call(self.name, 'configure', '-'+key)
    def configure(self, **kw):
        """Configure the image."""
        res = ()
        dla k, v w _cnfmerge(kw).items():
            jeżeli v jest nie Nic:
                jeżeli k[-1] == '_': k = k[:-1]
                jeżeli callable(v):
                    v = self._register(v)
                res = res + ('-'+k, v)
        self.tk.call((self.name, 'config') + res)
    config = configure
    def height(self):
        """Return the height of the image."""
        zwróć self.tk.getint(
            self.tk.call('image', 'height', self.name))
    def type(self):
        """Return the type of the imgage, e.g. "photo" albo "bitmap"."""
        zwróć self.tk.call('image', 'type', self.name)
    def width(self):
        """Return the width of the image."""
        zwróć self.tk.getint(
            self.tk.call('image', 'width', self.name))

klasa PhotoImage(Image):
    """Widget which can display colored images w GIF, PPM/PGM format."""
    def __init__(self, name=Nic, cnf={}, master=Nic, **kw):
        """Create an image przy NAME.

        Valid resource names: data, format, file, gamma, height, palette,
        width."""
        Image.__init__(self, 'photo', name, cnf, master, **kw)
    def blank(self):
        """Display a transparent image."""
        self.tk.call(self.name, 'blank')
    def cget(self, option):
        """Return the value of OPTION."""
        zwróć self.tk.call(self.name, 'cget', '-' + option)
    # XXX config
    def __getitem__(self, key):
        zwróć self.tk.call(self.name, 'cget', '-' + key)
    # XXX copy -from, -to, ...?
    def copy(self):
        """Return a new PhotoImage przy the same image jako this widget."""
        destImage = PhotoImage(master=self.tk)
        self.tk.call(destImage, 'copy', self.name)
        zwróć destImage
    def zoom(self,x,y=''):
        """Return a new PhotoImage przy the same image jako this widget
        but zoom it przy X oraz Y."""
        destImage = PhotoImage(master=self.tk)
        jeżeli y=='': y=x
        self.tk.call(destImage, 'copy', self.name, '-zoom',x,y)
        zwróć destImage
    def subsample(self,x,y=''):
        """Return a new PhotoImage based on the same image jako this widget
        but use only every Xth albo Yth pixel."""
        destImage = PhotoImage(master=self.tk)
        jeżeli y=='': y=x
        self.tk.call(destImage, 'copy', self.name, '-subsample',x,y)
        zwróć destImage
    def get(self, x, y):
        """Return the color (red, green, blue) of the pixel at X,Y."""
        zwróć self.tk.call(self.name, 'get', x, y)
    def put(self, data, to=Nic):
        """Put row formatted colors to image starting from
        position TO, e.g. image.put("{red green} {blue yellow}", to=(4,6))"""
        args = (self.name, 'put', data)
        jeżeli to:
            jeżeli to[0] == '-to':
                to = to[1:]
            args = args + ('-to',) + tuple(to)
        self.tk.call(args)
    # XXX read
    def write(self, filename, format=Nic, from_coords=Nic):
        """Write image to file FILENAME w FORMAT starting from
        position FROM_COORDS."""
        args = (self.name, 'write', filename)
        jeżeli format:
            args = args + ('-format', format)
        jeżeli from_coords:
            args = args + ('-from',) + tuple(from_coords)
        self.tk.call(args)

klasa BitmapImage(Image):
    """Widget which can display a bitmap."""
    def __init__(self, name=Nic, cnf={}, master=Nic, **kw):
        """Create a bitmap przy NAME.

        Valid resource names: background, data, file, foreground, maskdata, maskfile."""
        Image.__init__(self, 'bitmap', name, cnf, master, **kw)

def image_names():
    zwróć _default_root.tk.splitlist(_default_root.tk.call('image', 'names'))

def image_types():
    zwróć _default_root.tk.splitlist(_default_root.tk.call('image', 'types'))


klasa Spinbox(Widget, XView):
    """spinbox widget."""
    def __init__(self, master=Nic, cnf={}, **kw):
        """Construct a spinbox widget przy the parent MASTER.

        STANDARD OPTIONS

            activebackground, background, borderwidth,
            cursor, exportselection, font, foreground,
            highlightbackground, highlightcolor,
            highlightthickness, insertbackground,
            insertborderwidth, insertofftime,
            insertontime, insertwidth, justify, relief,
            repeatdelay, repeatinterval,
            selectbackground, selectborderwidth
            selectforeground, takefocus, textvariable
            xscrollcommand.

        WIDGET-SPECIFIC OPTIONS

            buttonbackground, buttoncursor,
            buttondownrelief, buttonuprelief,
            command, disabledbackground,
            disabledforeground, format, from,
            invalidcommand, increment,
            readonlybackground, state, to,
            validate, validatecommand values,
            width, wrap,
        """
        Widget.__init__(self, master, 'spinbox', cnf, kw)

    def bbox(self, index):
        """Return a tuple of X1,Y1,X2,Y2 coordinates dla a
        rectangle which encloses the character given by index.

        The first two elements of the list give the x oraz y
        coordinates of the upper-left corner of the screen
        area covered by the character (in pixels relative
        to the widget) oraz the last two elements give the
        width oraz height of the character, w pixels. The
        bounding box may refer to a region outside the
        visible area of the window.
        """
        zwróć self._getints(self.tk.call(self._w, 'bbox', index)) albo Nic

    def delete(self, first, last=Nic):
        """Delete one albo more elements of the spinbox.

        First jest the index of the first character to delete,
        oraz last jest the index of the character just after
        the last one to delete. If last isn't specified it
        defaults to first+1, i.e. a single character jest
        deleted.  This command returns an empty string.
        """
        zwróć self.tk.call(self._w, 'delete', first, last)

    def get(self):
        """Returns the spinbox's string"""
        zwróć self.tk.call(self._w, 'get')

    def icursor(self, index):
        """Alter the position of the insertion cursor.

        The insertion cursor will be displayed just before
        the character given by index. Returns an empty string
        """
        zwróć self.tk.call(self._w, 'icursor', index)

    def identify(self, x, y):
        """Returns the name of the widget at position x, y

        Return value jest one of: none, buttondown, buttonup, entry
        """
        zwróć self.tk.call(self._w, 'identify', x, y)

    def index(self, index):
        """Returns the numerical index corresponding to index
        """
        zwróć self.tk.call(self._w, 'index', index)

    def insert(self, index, s):
        """Insert string s at index

         Returns an empty string.
        """
        zwróć self.tk.call(self._w, 'insert', index, s)

    def invoke(self, element):
        """Causes the specified element to be invoked

        The element could be buttondown albo buttonup
        triggering the action associated przy it.
        """
        zwróć self.tk.call(self._w, 'invoke', element)

    def scan(self, *args):
        """Internal function."""
        zwróć self._getints(
            self.tk.call((self._w, 'scan') + args)) albo ()

    def scan_mark(self, x):
        """Records x oraz the current view w the spinbox window;

        used w conjunction przy later scan dragto commands.
        Typically this command jest associated przy a mouse button
        press w the widget. It returns an empty string.
        """
        zwróć self.scan("mark", x)

    def scan_dragto(self, x):
        """Compute the difference between the given x argument
        oraz the x argument to the last scan mark command

        It then adjusts the view left albo right by 10 times the
        difference w x-coordinates. This command jest typically
        associated przy mouse motion events w the widget, to
        produce the effect of dragging the spinbox at high speed
        through the window. The zwróć value jest an empty string.
        """
        zwróć self.scan("dragto", x)

    def selection(self, *args):
        """Internal function."""
        zwróć self._getints(
            self.tk.call((self._w, 'selection') + args)) albo ()

    def selection_adjust(self, index):
        """Locate the end of the selection nearest to the character
        given by index,

        Then adjust that end of the selection to be at index
        (i.e including but nie going beyond index). The other
        end of the selection jest made the anchor point dla future
        select to commands. If the selection isn't currently w
        the spinbox, then a new selection jest created to include
        the characters between index oraz the most recent selection
        anchor point, inclusive. Returns an empty string.
        """
        zwróć self.selection("adjust", index)

    def selection_clear(self):
        """Clear the selection

        If the selection isn't w this widget then the
        command has no effect. Returns an empty string.
        """
        zwróć self.selection("clear")

    def selection_element(self, element=Nic):
        """Sets albo gets the currently selected element.

        If a spinbutton element jest specified, it will be
        displayed depressed
        """
        zwróć self.selection("element", element)

###########################################################################

klasa LabelFrame(Widget):
    """labelframe widget."""
    def __init__(self, master=Nic, cnf={}, **kw):
        """Construct a labelframe widget przy the parent MASTER.

        STANDARD OPTIONS

            borderwidth, cursor, font, foreground,
            highlightbackground, highlightcolor,
            highlightthickness, padx, pady, relief,
            takefocus, text

        WIDGET-SPECIFIC OPTIONS

            background, class, colormap, container,
            height, labelanchor, labelwidget,
            visual, width
        """
        Widget.__init__(self, master, 'labelframe', cnf, kw)

########################################################################

klasa PanedWindow(Widget):
    """panedwindow widget."""
    def __init__(self, master=Nic, cnf={}, **kw):
        """Construct a panedwindow widget przy the parent MASTER.

        STANDARD OPTIONS

            background, borderwidth, cursor, height,
            orient, relief, width

        WIDGET-SPECIFIC OPTIONS

            handlepad, handlesize, opaqueresize,
            sashcursor, sashpad, sashrelief,
            sashwidth, showhandle,
        """
        Widget.__init__(self, master, 'panedwindow', cnf, kw)

    def add(self, child, **kw):
        """Add a child widget to the panedwindow w a new pane.

        The child argument jest the name of the child widget
        followed by pairs of arguments that specify how to
        manage the windows. The possible options oraz values
        are the ones accepted by the paneconfigure method.
        """
        self.tk.call((self._w, 'add', child) + self._options(kw))

    def remove(self, child):
        """Remove the pane containing child z the panedwindow

        All geometry management options dla child will be forgotten.
        """
        self.tk.call(self._w, 'forget', child)
    forget=remove

    def identify(self, x, y):
        """Identify the panedwindow component at point x, y

        If the point jest over a sash albo a sash handle, the result
        jest a two element list containing the index of the sash albo
        handle, oraz a word indicating whether it jest over a sash
        albo a handle, such jako {0 sash} albo {2 handle}. If the point
        jest over any other part of the panedwindow, the result jest
        an empty list.
        """
        zwróć self.tk.call(self._w, 'identify', x, y)

    def proxy(self, *args):
        """Internal function."""
        zwróć self._getints(
            self.tk.call((self._w, 'proxy') + args)) albo ()

    def proxy_coord(self):
        """Return the x oraz y pair of the most recent proxy location
        """
        zwróć self.proxy("coord")

    def proxy_forget(self):
        """Remove the proxy z the display.
        """
        zwróć self.proxy("forget")

    def proxy_place(self, x, y):
        """Place the proxy at the given x oraz y coordinates.
        """
        zwróć self.proxy("place", x, y)

    def sash(self, *args):
        """Internal function."""
        zwróć self._getints(
            self.tk.call((self._w, 'sash') + args)) albo ()

    def sash_coord(self, index):
        """Return the current x oraz y pair dla the sash given by index.

        Index must be an integer between 0 oraz 1 less than the
        number of panes w the panedwindow. The coordinates given are
        those of the top left corner of the region containing the sash.
        pathName sash dragto index x y This command computes the
        difference between the given coordinates oraz the coordinates
        given to the last sash coord command dla the given sash. It then
        moves that sash the computed difference. The zwróć value jest the
        empty string.
        """
        zwróć self.sash("coord", index)

    def sash_mark(self, index):
        """Records x oraz y dla the sash given by index;

        Used w conjunction przy later dragto commands to move the sash.
        """
        zwróć self.sash("mark", index)

    def sash_place(self, index, x, y):
        """Place the sash given by index at the given coordinates
        """
        zwróć self.sash("place", index, x, y)

    def panecget(self, child, option):
        """Query a management option dla window.

        Option may be any value allowed by the paneconfigure subcommand
        """
        zwróć self.tk.call(
            (self._w, 'panecget') + (child, '-'+option))

    def paneconfigure(self, tagOrId, cnf=Nic, **kw):
        """Query albo modify the management options dla window.

        If no option jest specified, returns a list describing all
        of the available options dla pathName.  If option jest
        specified przy no value, then the command returns a list
        describing the one named option (this list will be identical
        to the corresponding sublist of the value returned jeżeli no
        option jest specified). If one albo more option-value pairs are
        specified, then the command modifies the given widget
        option(s) to have the given value(s); w this case the
        command returns an empty string. The following options
        are supported:

        after window
            Insert the window after the window specified. window
            should be the name of a window already managed by pathName.
        before window
            Insert the window before the window specified. window
            should be the name of a window already managed by pathName.
        height size
            Specify a height dla the window. The height will be the
            outer dimension of the window including its border, if
            any. If size jest an empty string, albo jeżeli -height jest nie
            specified, then the height requested internally by the
            window will be used initially; the height may later be
            adjusted by the movement of sashes w the panedwindow.
            Size may be any value accepted by Tk_GetPixels.
        minsize n
            Specifies that the size of the window cannot be made
            less than n. This constraint only affects the size of
            the widget w the paned dimension -- the x dimension
            dla horizontal panedwindows, the y dimension for
            vertical panedwindows. May be any value accepted by
            Tk_GetPixels.
        padx n
            Specifies a non-negative value indicating how much
            extra space to leave on each side of the window w
            the X-direction. The value may have any of the forms
            accepted by Tk_GetPixels.
        pady n
            Specifies a non-negative value indicating how much
            extra space to leave on each side of the window w
            the Y-direction. The value may have any of the forms
            accepted by Tk_GetPixels.
        sticky style
            If a window's pane jest larger than the requested
            dimensions of the window, this option may be used
            to position (or stretch) the window within its pane.
            Style jest a string that contains zero albo more of the
            characters n, s, e albo w. The string can optionally
            contains spaces albo commas, but they are ignored. Each
            letter refers to a side (north, south, east, albo west)
            that the window will "stick" to. If both n oraz s
            (or e oraz w) are specified, the window will be
            stretched to fill the entire height (or width) of
            its cavity.
        width size
            Specify a width dla the window. The width will be
            the outer dimension of the window including its
            border, jeżeli any. If size jest an empty string, albo
            jeżeli -width jest nie specified, then the width requested
            internally by the window will be used initially; the
            width may later be adjusted by the movement of sashes
            w the panedwindow. Size may be any value accepted by
            Tk_GetPixels.

        """
        jeżeli cnf jest Nic oraz nie kw:
            zwróć self._getconfigure(self._w, 'paneconfigure', tagOrId)
        jeżeli isinstance(cnf, str) oraz nie kw:
            zwróć self._getconfigure1(
                self._w, 'paneconfigure', tagOrId, '-'+cnf)
        self.tk.call((self._w, 'paneconfigure', tagOrId) +
                 self._options(cnf, kw))
    paneconfig = paneconfigure

    def panes(self):
        """Returns an ordered list of the child panes."""
        zwróć self.tk.splitlist(self.tk.call(self._w, 'panes'))

# Test:

def _test():
    root = Tk()
    text = "This jest Tcl/Tk version %s" % TclVersion
    text += "\nThis should be a cedilla: \xe7"
    label = Label(root, text=text)
    label.pack()
    test = Button(root, text="Click me!",
              command=lambda root=root: root.test.configure(
                  text="[%s]" % root.test['text']))
    test.pack()
    root.test = test
    quit = Button(root, text="QUIT", command=root.destroy)
    quit.pack()
    # The following three commands are needed so the window pops
    # up on top on Windows...
    root.iconify()
    root.update()
    root.deiconify()
    root.mainloop()

jeżeli __name__ == '__main__':
    _test()
