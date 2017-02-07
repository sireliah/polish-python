"""Ttk wrapper.

This module provides classes to allow using Tk themed widget set.

Ttk jest based on a revised oraz enhanced version of
TIP #48 (http://tip.tcl.tk/48) specified style engine.

Its basic idea jest to separate, to the extent possible, the code
implementing a widget's behavior z the code implementing its
appearance. Widget klasa bindings are primarily responsible for
maintaining the widget state oraz invoking callbacks, all aspects
of the widgets appearance lies at Themes.
"""

__version__ = "0.3.1"

__author__ = "Guilherme Polo <ggpolo@gmail.com>"

__all__ = ["Button", "Checkbutton", "Combobox", "Entry", "Frame", "Label",
           "Labelframe", "LabelFrame", "Menubutton", "Notebook", "Panedwindow",
           "PanedWindow", "Progressbar", "Radiobutton", "Scale", "Scrollbar",
           "Separator", "Sizegrip", "Style", "Treeview",
           # Extensions
           "LabeledScale", "OptionMenu",
           # functions
           "tclobjs_to_py", "setup_master"]

zaimportuj tkinter
z tkinter zaimportuj _flatten, _join, _stringify, _splitdict

# Verify jeżeli Tk jest new enough to nie need the Tile package
_REQUIRE_TILE = Prawda jeżeli tkinter.TkVersion < 8.5 inaczej Nieprawda

def _load_tile(master):
    jeżeli _REQUIRE_TILE:
        zaimportuj os
        tilelib = os.environ.get('TILE_LIBRARY')
        jeżeli tilelib:
            # append custom tile path to the list of directories that
            # Tcl uses when attempting to resolve packages przy the package
            # command
            master.tk.eval(
                    'global auto_path; '
                    'lappend auto_path {%s}' % tilelib)

        master.tk.eval('package require tile') # TclError may be podnieśd here
        master._tile_loaded = Prawda

def _format_optvalue(value, script=Nieprawda):
    """Internal function."""
    jeżeli script:
        # jeżeli caller dalejes a Tcl script to tk.call, all the values need to
        # be grouped into words (arguments to a command w Tcl dialect)
        value = _stringify(value)
    albo_inaczej isinstance(value, (list, tuple)):
        value = _join(value)
    zwróć value

def _format_optdict(optdict, script=Nieprawda, ignore=Nic):
    """Formats optdict to a tuple to dalej it to tk.call.

    E.g. (script=Nieprawda):
      {'foreground': 'blue', 'padding': [1, 2, 3, 4]} returns:
      ('-foreground', 'blue', '-padding', '1 2 3 4')"""

    opts = []
    dla opt, value w optdict.items():
        jeżeli nie ignore albo opt nie w ignore:
            opts.append("-%s" % opt)
            jeżeli value jest nie Nic:
                opts.append(_format_optvalue(value, script))

    zwróć _flatten(opts)

def _mapdict_values(items):
    # each value w mapdict jest expected to be a sequence, where each item
    # jest another sequence containing a state (or several) oraz a value
    # E.g. (script=Nieprawda):
    #   [('active', 'selected', 'grey'), ('focus', [1, 2, 3, 4])]
    #   returns:
    #   ['active selected', 'grey', 'focus', [1, 2, 3, 4]]
    opt_val = []
    dla *state, val w items:
        # hacks dla bakward compatibility
        state[0] # podnieś IndexError jeżeli empty
        jeżeli len(state) == 1:
            # jeżeli it jest empty (something that evaluates to Nieprawda), then
            # format it to Tcl code to denote the "normal" state
            state = state[0] albo ''
        inaczej:
            # group multiple states
            state = ' '.join(state) # podnieś TypeError jeżeli nie str
        opt_val.append(state)
        jeżeli val jest nie Nic:
            opt_val.append(val)
    zwróć opt_val

def _format_mapdict(mapdict, script=Nieprawda):
    """Formats mapdict to dalej it to tk.call.

    E.g. (script=Nieprawda):
      {'expand': [('active', 'selected', 'grey'), ('focus', [1, 2, 3, 4])]}

      returns:

      ('-expand', '{active selected} grey focus {1, 2, 3, 4}')"""

    opts = []
    dla opt, value w mapdict.items():
        opts.extend(("-%s" % opt,
                     _format_optvalue(_mapdict_values(value), script)))

    zwróć _flatten(opts)

def _format_elemcreate(etype, script=Nieprawda, *args, **kw):
    """Formats args oraz kw according to the given element factory etype."""
    spec = Nic
    opts = ()
    jeżeli etype w ("image", "vsapi"):
        jeżeli etype == "image": # define an element based on an image
            # first arg should be the default image name
            iname = args[0]
            # next args, jeżeli any, are statespec/value pairs which jest almost
            # a mapdict, but we just need the value
            imagespec = _join(_mapdict_values(args[1:]))
            spec = "%s %s" % (iname, imagespec)

        inaczej:
            # define an element whose visual appearance jest drawn using the
            # Microsoft Visual Styles API which jest responsible dla the
            # themed styles on Windows XP oraz Vista.
            # Availability: Tk 8.6, Windows XP oraz Vista.
            class_name, part_id = args[:2]
            statemap = _join(_mapdict_values(args[2:]))
            spec = "%s %s %s" % (class_name, part_id, statemap)

        opts = _format_optdict(kw, script)

    albo_inaczej etype == "from": # clone an element
        # it expects a themename oraz optionally an element to clone from,
        # otherwise it will clone {} (empty element)
        spec = args[0] # theme name
        jeżeli len(args) > 1: # elementz specified
            opts = (_format_optvalue(args[1], script),)

    jeżeli script:
        spec = '{%s}' % spec
        opts = ' '.join(opts)

    zwróć spec, opts

def _format_layoutlist(layout, indent=0, indent_size=2):
    """Formats a layout list so we can dalej the result to ttk::style
    layout oraz ttk::style settings. Note that the layout doesn't has to
    be a list necessarily.

    E.g.:
      [("Menubutton.background", Nic),
       ("Menubutton.button", {"children":
           [("Menubutton.focus", {"children":
               [("Menubutton.padding", {"children":
                [("Menubutton.label", {"side": "left", "expand": 1})]
               })]
           })]
       }),
       ("Menubutton.indicator", {"side": "right"})
      ]

      returns:

      Menubutton.background
      Menubutton.button -children {
        Menubutton.focus -children {
          Menubutton.padding -children {
            Menubutton.label -side left -expand 1
          }
        }
      }
      Menubutton.indicator -side right"""
    script = []

    dla layout_elem w layout:
        elem, opts = layout_elem
        opts = opts albo {}
        fopts = ' '.join(_format_optdict(opts, Prawda, ("children",)))
        head = "%s%s%s" % (' ' * indent, elem, (" %s" % fopts) jeżeli fopts inaczej '')

        jeżeli "children" w opts:
            script.append(head + " -children {")
            indent += indent_size
            newscript, indent = _format_layoutlist(opts['children'], indent,
                indent_size)
            script.append(newscript)
            indent -= indent_size
            script.append('%s}' % (' ' * indent))
        inaczej:
            script.append(head)

    zwróć '\n'.join(script), indent

def _script_from_settings(settings):
    """Returns an appropriate script, based on settings, according to
    theme_settings definition to be used by theme_settings oraz
    theme_create."""
    script = []
    # a script will be generated according to settings dalejed, which
    # will then be evaluated by Tcl
    dla name, opts w settings.items():
        # will format specific keys according to Tcl code
        jeżeli opts.get('configure'): # format 'configure'
            s = ' '.join(_format_optdict(opts['configure'], Prawda))
            script.append("ttk::style configure %s %s;" % (name, s))

        jeżeli opts.get('map'): # format 'map'
            s = ' '.join(_format_mapdict(opts['map'], Prawda))
            script.append("ttk::style map %s %s;" % (name, s))

        jeżeli 'layout' w opts: # format 'layout' which may be empty
            jeżeli nie opts['layout']:
                s = 'null' # could be any other word, but this one makes sense
            inaczej:
                s, _ = _format_layoutlist(opts['layout'])
            script.append("ttk::style layout %s {\n%s\n}" % (name, s))

        jeżeli opts.get('element create'): # format 'element create'
            eopts = opts['element create']
            etype = eopts[0]

            # find where args end, oraz where kwargs start
            argc = 1 # etype was the first one
            dopóki argc < len(eopts) oraz nie hasattr(eopts[argc], 'items'):
                argc += 1

            elemargs = eopts[1:argc]
            elemkw = eopts[argc] jeżeli argc < len(eopts) oraz eopts[argc] inaczej {}
            spec, opts = _format_elemcreate(etype, Prawda, *elemargs, **elemkw)

            script.append("ttk::style element create %s %s %s %s" % (
                name, etype, spec, opts))

    zwróć '\n'.join(script)

def _list_from_statespec(stuple):
    """Construct a list z the given statespec tuple according to the
    accepted statespec accepted by _format_mapdict."""
    nval = []
    dla val w stuple:
        typename = getattr(val, 'typename', Nic)
        jeżeli typename jest Nic:
            nval.append(val)
        inaczej: # this jest a Tcl object
            val = str(val)
            jeżeli typename == 'StateSpec':
                val = val.split()
            nval.append(val)

    it = iter(nval)
    zwróć [_flatten(spec) dla spec w zip(it, it)]

def _list_from_layouttuple(tk, ltuple):
    """Construct a list z the tuple returned by ttk::layout, this jest
    somewhat the reverse of _format_layoutlist."""
    ltuple = tk.splitlist(ltuple)
    res = []

    indx = 0
    dopóki indx < len(ltuple):
        name = ltuple[indx]
        opts = {}
        res.append((name, opts))
        indx += 1

        dopóki indx < len(ltuple): # grab name's options
            opt, val = ltuple[indx:indx + 2]
            jeżeli nie opt.startswith('-'): # found next name
                przerwij

            opt = opt[1:] # remove the '-' z the option
            indx += 2

            jeżeli opt == 'children':
                val = _list_from_layouttuple(tk, val)

            opts[opt] = val

    zwróć res

def _val_or_dict(tk, options, *args):
    """Format options then call Tk command przy args oraz options oraz zwróć
    the appropriate result.

    If no option jest specified, a dict jest returned. If a option jest
    specified przy the Nic value, the value dla that option jest returned.
    Otherwise, the function just sets the dalejed options oraz the caller
    shouldn't be expecting a zwróć value anyway."""
    options = _format_optdict(options)
    res = tk.call(*(args + options))

    jeżeli len(options) % 2: # option specified without a value, zwróć its value
        zwróć res

    zwróć _splitdict(tk, res, conv=_tclobj_to_py)

def _convert_stringval(value):
    """Converts a value to, hopefully, a more appropriate Python object."""
    value = str(value)
    spróbuj:
        value = int(value)
    wyjąwszy (ValueError, TypeError):
        dalej

    zwróć value

def _to_number(x):
    jeżeli isinstance(x, str):
        jeżeli '.' w x:
            x = float(x)
        inaczej:
            x = int(x)
    zwróć x

def _tclobj_to_py(val):
    """Return value converted z Tcl object to Python object."""
    jeżeli val oraz hasattr(val, '__len__') oraz nie isinstance(val, str):
        jeżeli getattr(val[0], 'typename', Nic) == 'StateSpec':
            val = _list_from_statespec(val)
        inaczej:
            val = list(map(_convert_stringval, val))

    albo_inaczej hasattr(val, 'typename'): # some other (single) Tcl object
        val = _convert_stringval(val)

    zwróć val

def tclobjs_to_py(adict):
    """Returns adict przy its values converted z Tcl objects to Python
    objects."""
    dla opt, val w adict.items():
        adict[opt] = _tclobj_to_py(val)

    zwróć adict

def setup_master(master=Nic):
    """If master jest nie Nic, itself jest returned. If master jest Nic,
    the default master jest returned jeżeli there jest one, otherwise a new
    master jest created oraz returned.

    If it jest nie allowed to use the default root oraz master jest Nic,
    RuntimeError jest podnieśd."""
    jeżeli master jest Nic:
        jeżeli tkinter._support_default_root:
            master = tkinter._default_root albo tkinter.Tk()
        inaczej:
            podnieś RuntimeError(
                    "No master specified oraz tkinter jest "
                    "configured to nie support default root")
    zwróć master


klasa Style(object):
    """Manipulate style database."""

    _name = "ttk::style"

    def __init__(self, master=Nic):
        master = setup_master(master)

        jeżeli nie getattr(master, '_tile_loaded', Nieprawda):
            # Load tile now, jeżeli needed
            _load_tile(master)

        self.master = master
        self.tk = self.master.tk


    def configure(self, style, query_opt=Nic, **kw):
        """Query albo sets the default value of the specified option(s) w
        style.

        Each key w kw jest an option oraz each value jest either a string albo
        a sequence identifying the value dla that option."""
        jeżeli query_opt jest nie Nic:
            kw[query_opt] = Nic
        zwróć _val_or_dict(self.tk, kw, self._name, "configure", style)


    def map(self, style, query_opt=Nic, **kw):
        """Query albo sets dynamic values of the specified option(s) w
        style.

        Each key w kw jest an option oraz each value should be a list albo a
        tuple (usually) containing statespecs grouped w tuples, albo list,
        albo something inaczej of your preference. A statespec jest compound of
        one albo more states oraz then a value."""
        jeżeli query_opt jest nie Nic:
            zwróć _list_from_statespec(self.tk.splitlist(
                self.tk.call(self._name, "map", style, '-%s' % query_opt)))

        zwróć _splitdict(
            self.tk,
            self.tk.call(self._name, "map", style, *_format_mapdict(kw)),
            conv=_tclobj_to_py)


    def lookup(self, style, option, state=Nic, default=Nic):
        """Returns the value specified dla option w style.

        If state jest specified it jest expected to be a sequence of one
        albo more states. If the default argument jest set, it jest used as
        a fallback value w case no specification dla option jest found."""
        state = ' '.join(state) jeżeli state inaczej ''

        zwróć self.tk.call(self._name, "lookup", style, '-%s' % option,
            state, default)


    def layout(self, style, layoutspec=Nic):
        """Define the widget layout dla given style. If layoutspec jest
        omitted, zwróć the layout specification dla given style.

        layoutspec jest expected to be a list albo an object different than
        Nic that evaluates to Nieprawda jeżeli you want to "turn off" that style.
        If it jest a list (or tuple, albo something inaczej), each item should be
        a tuple where the first item jest the layout name oraz the second item
        should have the format described below:

        LAYOUTS

            A layout can contain the value Nic, jeżeli takes no options, albo
            a dict of options specifying how to arrange the element.
            The layout mechanism uses a simplified version of the pack
            geometry manager: given an initial cavity, each element jest
            allocated a parcel. Valid options/values are:

                side: whichside
                    Specifies which side of the cavity to place the
                    element; one of top, right, bottom albo left. If
                    omitted, the element occupies the entire cavity.

                sticky: nswe
                    Specifies where the element jest placed inside its
                    allocated parcel.

                children: [sublayout... ]
                    Specifies a list of elements to place inside the
                    element. Each element jest a tuple (or other sequence)
                    where the first item jest the layout name, oraz the other
                    jest a LAYOUT."""
        lspec = Nic
        jeżeli layoutspec:
            lspec = _format_layoutlist(layoutspec)[0]
        albo_inaczej layoutspec jest nie Nic: # will disable the layout ({}, '', etc)
            lspec = "null" # could be any other word, but this may make sense
                           # when calling layout(style) later

        zwróć _list_from_layouttuple(self.tk,
            self.tk.call(self._name, "layout", style, lspec))


    def element_create(self, elementname, etype, *args, **kw):
        """Create a new element w the current theme of given etype."""
        spec, opts = _format_elemcreate(etype, Nieprawda, *args, **kw)
        self.tk.call(self._name, "element", "create", elementname, etype,
            spec, *opts)


    def element_names(self):
        """Returns the list of elements defined w the current theme."""
        zwróć self.tk.splitlist(self.tk.call(self._name, "element", "names"))


    def element_options(self, elementname):
        """Return the list of elementname's options."""
        zwróć self.tk.splitlist(self.tk.call(self._name, "element", "options", elementname))


    def theme_create(self, themename, parent=Nic, settings=Nic):
        """Creates a new theme.

        It jest an error jeżeli themename already exists. If parent jest
        specified, the new theme will inherit styles, elements oraz
        layouts z the specified parent theme. If settings are present,
        they are expected to have the same syntax used dla theme_settings."""
        script = _script_from_settings(settings) jeżeli settings inaczej ''

        jeżeli parent:
            self.tk.call(self._name, "theme", "create", themename,
                "-parent", parent, "-settings", script)
        inaczej:
            self.tk.call(self._name, "theme", "create", themename,
                "-settings", script)


    def theme_settings(self, themename, settings):
        """Temporarily sets the current theme to themename, apply specified
        settings oraz then restore the previous theme.

        Each key w settings jest a style oraz each value may contain the
        keys 'configure', 'map', 'layout' oraz 'element create' oraz they
        are expected to have the same format jako specified by the methods
        configure, map, layout oraz element_create respectively."""
        script = _script_from_settings(settings)
        self.tk.call(self._name, "theme", "settings", themename, script)


    def theme_names(self):
        """Returns a list of all known themes."""
        zwróć self.tk.splitlist(self.tk.call(self._name, "theme", "names"))


    def theme_use(self, themename=Nic):
        """If themename jest Nic, returns the theme w use, otherwise, set
        the current theme to themename, refreshes all widgets oraz emits
        a <<ThemeChanged>> event."""
        jeżeli themename jest Nic:
            # Starting on Tk 8.6, checking this global jest no longer needed
            # since it allows doing self.tk.call(self._name, "theme", "use")
            zwróć self.tk.eval("return $ttk::currentTheme")

        # using "ttk::setTheme" instead of "ttk::style theme use" causes
        # the variable currentTheme to be updated, also, ttk::setTheme calls
        # "ttk::style theme use" w order to change theme.
        self.tk.call("ttk::setTheme", themename)


klasa Widget(tkinter.Widget):
    """Base klasa dla Tk themed widgets."""

    def __init__(self, master, widgetname, kw=Nic):
        """Constructs a Ttk Widget przy the parent master.

        STANDARD OPTIONS

            class, cursor, takefocus, style

        SCROLLABLE WIDGET OPTIONS

            xscrollcommand, yscrollcommand

        LABEL WIDGET OPTIONS

            text, textvariable, underline, image, compound, width

        WIDGET STATES

            active, disabled, focus, pressed, selected, background,
            readonly, alternate, invalid
        """
        master = setup_master(master)
        jeżeli nie getattr(master, '_tile_loaded', Nieprawda):
            # Load tile now, jeżeli needed
            _load_tile(master)
        tkinter.Widget.__init__(self, master, widgetname, kw=kw)


    def identify(self, x, y):
        """Returns the name of the element at position x, y, albo the empty
        string jeżeli the point does nie lie within any element.

        x oraz y are pixel coordinates relative to the widget."""
        zwróć self.tk.call(self._w, "identify", x, y)


    def instate(self, statespec, callback=Nic, *args, **kw):
        """Test the widget's state.

        If callback jest nie specified, returns Prawda jeżeli the widget state
        matches statespec oraz Nieprawda otherwise. If callback jest specified,
        then it will be invoked przy *args, **kw jeżeli the widget state
        matches statespec. statespec jest expected to be a sequence."""
        ret = self.tk.getboolean(
                self.tk.call(self._w, "instate", ' '.join(statespec)))
        jeżeli ret oraz callback:
            zwróć callback(*args, **kw)

        zwróć ret


    def state(self, statespec=Nic):
        """Modify albo inquire widget state.

        Widget state jest returned jeżeli statespec jest Nic, otherwise it jest
        set according to the statespec flags oraz then a new state spec
        jest returned indicating which flags were changed. statespec jest
        expected to be a sequence."""
        jeżeli statespec jest nie Nic:
            statespec = ' '.join(statespec)

        zwróć self.tk.splitlist(str(self.tk.call(self._w, "state", statespec)))


klasa Button(Widget):
    """Ttk Button widget, displays a textual label and/or image, oraz
    evaluates a command when pressed."""

    def __init__(self, master=Nic, **kw):
        """Construct a Ttk Button widget przy the parent master.

        STANDARD OPTIONS

            class, compound, cursor, image, state, style, takefocus,
            text, textvariable, underline, width

        WIDGET-SPECIFIC OPTIONS

            command, default, width
        """
        Widget.__init__(self, master, "ttk::button", kw)


    def invoke(self):
        """Invokes the command associated przy the button."""
        zwróć self.tk.call(self._w, "invoke")


klasa Checkbutton(Widget):
    """Ttk Checkbutton widget which jest either w on- albo off-state."""

    def __init__(self, master=Nic, **kw):
        """Construct a Ttk Checkbutton widget przy the parent master.

        STANDARD OPTIONS

            class, compound, cursor, image, state, style, takefocus,
            text, textvariable, underline, width

        WIDGET-SPECIFIC OPTIONS

            command, offvalue, onvalue, variable
        """
        Widget.__init__(self, master, "ttk::checkbutton", kw)


    def invoke(self):
        """Toggles between the selected oraz deselected states oraz
        invokes the associated command. If the widget jest currently
        selected, sets the option variable to the offvalue option
        oraz deselects the widget; otherwise, sets the option variable
        to the option onvalue.

        Returns the result of the associated command."""
        zwróć self.tk.call(self._w, "invoke")


klasa Entry(Widget, tkinter.Entry):
    """Ttk Entry widget displays a one-line text string oraz allows that
    string to be edited by the user."""

    def __init__(self, master=Nic, widget=Nic, **kw):
        """Constructs a Ttk Entry widget przy the parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus, xscrollcommand

        WIDGET-SPECIFIC OPTIONS

            exportselection, invalidcommand, justify, show, state,
            textvariable, validate, validatecommand, width

        VALIDATION MODES

            none, key, focus, focusin, focusout, all
        """
        Widget.__init__(self, master, widget albo "ttk::entry", kw)


    def bbox(self, index):
        """Return a tuple of (x, y, width, height) which describes the
        bounding box of the character given by index."""
        zwróć self._getints(self.tk.call(self._w, "bbox", index))


    def identify(self, x, y):
        """Returns the name of the element at position x, y, albo the
        empty string jeżeli the coordinates are outside the window."""
        zwróć self.tk.call(self._w, "identify", x, y)


    def validate(self):
        """Force revalidation, independent of the conditions specified
        by the validate option. Returns Nieprawda jeżeli validation fails, Prawda
        jeżeli it succeeds. Sets albo clears the invalid state accordingly."""
        zwróć self.tk.getboolean(self.tk.call(self._w, "validate"))


klasa Combobox(Entry):
    """Ttk Combobox widget combines a text field przy a pop-down list of
    values."""

    def __init__(self, master=Nic, **kw):
        """Construct a Ttk Combobox widget przy the parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus

        WIDGET-SPECIFIC OPTIONS

            exportselection, justify, height, postcommand, state,
            textvariable, values, width
        """
        Entry.__init__(self, master, "ttk::combobox", **kw)


    def current(self, newindex=Nic):
        """If newindex jest supplied, sets the combobox value to the
        element at position newindex w the list of values. Otherwise,
        returns the index of the current value w the list of values
        albo -1 jeżeli the current value does nie appear w the list."""
        jeżeli newindex jest Nic:
            zwróć self.tk.getint(self.tk.call(self._w, "current"))
        zwróć self.tk.call(self._w, "current", newindex)


    def set(self, value):
        """Sets the value of the combobox to value."""
        self.tk.call(self._w, "set", value)


klasa Frame(Widget):
    """Ttk Frame widget jest a container, used to group other widgets
    together."""

    def __init__(self, master=Nic, **kw):
        """Construct a Ttk Frame przy parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus

        WIDGET-SPECIFIC OPTIONS

            borderwidth, relief, padding, width, height
        """
        Widget.__init__(self, master, "ttk::frame", kw)


klasa Label(Widget):
    """Ttk Label widget displays a textual label and/or image."""

    def __init__(self, master=Nic, **kw):
        """Construct a Ttk Label przy parent master.

        STANDARD OPTIONS

            class, compound, cursor, image, style, takefocus, text,
            textvariable, underline, width

        WIDGET-SPECIFIC OPTIONS

            anchor, background, font, foreground, justify, padding,
            relief, text, wraplength
        """
        Widget.__init__(self, master, "ttk::label", kw)


klasa Labelframe(Widget):
    """Ttk Labelframe widget jest a container used to group other widgets
    together. It has an optional label, which may be a plain text string
    albo another widget."""

    def __init__(self, master=Nic, **kw):
        """Construct a Ttk Labelframe przy parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus

        WIDGET-SPECIFIC OPTIONS
            labelanchor, text, underline, padding, labelwidget, width,
            height
        """
        Widget.__init__(self, master, "ttk::labelframe", kw)

LabelFrame = Labelframe # tkinter name compatibility


klasa Menubutton(Widget):
    """Ttk Menubutton widget displays a textual label and/or image, oraz
    displays a menu when pressed."""

    def __init__(self, master=Nic, **kw):
        """Construct a Ttk Menubutton przy parent master.

        STANDARD OPTIONS

            class, compound, cursor, image, state, style, takefocus,
            text, textvariable, underline, width

        WIDGET-SPECIFIC OPTIONS

            direction, menu
        """
        Widget.__init__(self, master, "ttk::menubutton", kw)


klasa Notebook(Widget):
    """Ttk Notebook widget manages a collection of windows oraz displays
    a single one at a time. Each child window jest associated przy a tab,
    which the user may select to change the currently-displayed window."""

    def __init__(self, master=Nic, **kw):
        """Construct a Ttk Notebook przy parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus

        WIDGET-SPECIFIC OPTIONS

            height, padding, width

        TAB OPTIONS

            state, sticky, padding, text, image, compound, underline

        TAB IDENTIFIERS (tab_id)

            The tab_id argument found w several methods may take any of
            the following forms:

                * An integer between zero oraz the number of tabs
                * The name of a child window
                * A positional specification of the form "@x,y", which
                  defines the tab
                * The string "current", which identifies the
                  currently-selected tab
                * The string "end", which returns the number of tabs (only
                  valid dla method index)
        """
        Widget.__init__(self, master, "ttk::notebook", kw)


    def add(self, child, **kw):
        """Adds a new tab to the notebook.

        If window jest currently managed by the notebook but hidden, it jest
        restored to its previous position."""
        self.tk.call(self._w, "add", child, *(_format_optdict(kw)))


    def forget(self, tab_id):
        """Removes the tab specified by tab_id, unmaps oraz unmanages the
        associated window."""
        self.tk.call(self._w, "forget", tab_id)


    def hide(self, tab_id):
        """Hides the tab specified by tab_id.

        The tab will nie be displayed, but the associated window remains
        managed by the notebook oraz its configuration remembered. Hidden
        tabs may be restored przy the add command."""
        self.tk.call(self._w, "hide", tab_id)


    def identify(self, x, y):
        """Returns the name of the tab element at position x, y, albo the
        empty string jeżeli none."""
        zwróć self.tk.call(self._w, "identify", x, y)


    def index(self, tab_id):
        """Returns the numeric index of the tab specified by tab_id, albo
        the total number of tabs jeżeli tab_id jest the string "end"."""
        zwróć self.tk.getint(self.tk.call(self._w, "index", tab_id))


    def insert(self, pos, child, **kw):
        """Inserts a pane at the specified position.

        pos jest either the string end, an integer index, albo the name of
        a managed child. If child jest already managed by the notebook,
        moves it to the specified position."""
        self.tk.call(self._w, "insert", pos, child, *(_format_optdict(kw)))


    def select(self, tab_id=Nic):
        """Selects the specified tab.

        The associated child window will be displayed, oraz the
        previously-selected window (jeżeli different) jest unmapped. If tab_id
        jest omitted, returns the widget name of the currently selected
        pane."""
        zwróć self.tk.call(self._w, "select", tab_id)


    def tab(self, tab_id, option=Nic, **kw):
        """Query albo modify the options of the specific tab_id.

        If kw jest nie given, returns a dict of the tab option values. If option
        jest specified, returns the value of that option. Otherwise, sets the
        options to the corresponding values."""
        jeżeli option jest nie Nic:
            kw[option] = Nic
        zwróć _val_or_dict(self.tk, kw, self._w, "tab", tab_id)


    def tabs(self):
        """Returns a list of windows managed by the notebook."""
        zwróć self.tk.splitlist(self.tk.call(self._w, "tabs") albo ())


    def enable_traversal(self):
        """Enable keyboard traversal dla a toplevel window containing
        this notebook.

        This will extend the bindings dla the toplevel window containing
        this notebook jako follows:

            Control-Tab: selects the tab following the currently selected
                         one

            Shift-Control-Tab: selects the tab preceding the currently
                               selected one

            Alt-K: where K jest the mnemonic (underlined) character of any
                   tab, will select that tab.

        Multiple notebooks w a single toplevel may be enabled for
        traversal, including nested notebooks. However, notebook traversal
        only works properly jeżeli all panes are direct children of the
        notebook."""
        # The only, oraz good, difference I see jest about mnemonics, which works
        # after calling this method. Control-Tab oraz Shift-Control-Tab always
        # works (here at least).
        self.tk.call("ttk::notebook::enableTraversal", self._w)


klasa Panedwindow(Widget, tkinter.PanedWindow):
    """Ttk Panedwindow widget displays a number of subwindows, stacked
    either vertically albo horizontally."""

    def __init__(self, master=Nic, **kw):
        """Construct a Ttk Panedwindow przy parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus

        WIDGET-SPECIFIC OPTIONS

            orient, width, height

        PANE OPTIONS

            weight
        """
        Widget.__init__(self, master, "ttk::panedwindow", kw)


    forget = tkinter.PanedWindow.forget # overrides Pack.forget


    def insert(self, pos, child, **kw):
        """Inserts a pane at the specified positions.

        pos jest either the string end, oraz integer index, albo the name
        of a child. If child jest already managed by the paned window,
        moves it to the specified position."""
        self.tk.call(self._w, "insert", pos, child, *(_format_optdict(kw)))


    def pane(self, pane, option=Nic, **kw):
        """Query albo modify the options of the specified pane.

        pane jest either an integer index albo the name of a managed subwindow.
        If kw jest nie given, returns a dict of the pane option values. If
        option jest specified then the value dla that option jest returned.
        Otherwise, sets the options to the corresponding values."""
        jeżeli option jest nie Nic:
            kw[option] = Nic
        zwróć _val_or_dict(self.tk, kw, self._w, "pane", pane)


    def sashpos(self, index, newpos=Nic):
        """If newpos jest specified, sets the position of sash number index.

        May adjust the positions of adjacent sashes to ensure that
        positions are monotonically increasing. Sash positions are further
        constrained to be between 0 oraz the total size of the widget.

        Returns the new position of sash number index."""
        zwróć self.tk.getint(self.tk.call(self._w, "sashpos", index, newpos))

PanedWindow = Panedwindow # tkinter name compatibility


klasa Progressbar(Widget):
    """Ttk Progressbar widget shows the status of a long-running
    operation. They can operate w two modes: determinate mode shows the
    amount completed relative to the total amount of work to be done, oraz
    indeterminate mode provides an animated display to let the user know
    that something jest happening."""

    def __init__(self, master=Nic, **kw):
        """Construct a Ttk Progressbar przy parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus

        WIDGET-SPECIFIC OPTIONS

            orient, length, mode, maximum, value, variable, phase
        """
        Widget.__init__(self, master, "ttk::progressbar", kw)


    def start(self, interval=Nic):
        """Begin autoincrement mode: schedules a recurring timer event
        that calls method step every interval milliseconds.

        interval defaults to 50 milliseconds (20 steps/second) jeżeli ommited."""
        self.tk.call(self._w, "start", interval)


    def step(self, amount=Nic):
        """Increments the value option by amount.

        amount defaults to 1.0 jeżeli omitted."""
        self.tk.call(self._w, "step", amount)


    def stop(self):
        """Stop autoincrement mode: cancels any recurring timer event
        initiated by start."""
        self.tk.call(self._w, "stop")


klasa Radiobutton(Widget):
    """Ttk Radiobutton widgets are used w groups to show albo change a
    set of mutually-exclusive options."""

    def __init__(self, master=Nic, **kw):
        """Construct a Ttk Radiobutton przy parent master.

        STANDARD OPTIONS

            class, compound, cursor, image, state, style, takefocus,
            text, textvariable, underline, width

        WIDGET-SPECIFIC OPTIONS

            command, value, variable
        """
        Widget.__init__(self, master, "ttk::radiobutton", kw)


    def invoke(self):
        """Sets the option variable to the option value, selects the
        widget, oraz invokes the associated command.

        Returns the result of the command, albo an empty string if
        no command jest specified."""
        zwróć self.tk.call(self._w, "invoke")


klasa Scale(Widget, tkinter.Scale):
    """Ttk Scale widget jest typically used to control the numeric value of
    a linked variable that varies uniformly over some range."""

    def __init__(self, master=Nic, **kw):
        """Construct a Ttk Scale przy parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus

        WIDGET-SPECIFIC OPTIONS

            command, from, length, orient, to, value, variable
        """
        Widget.__init__(self, master, "ttk::scale", kw)


    def configure(self, cnf=Nic, **kw):
        """Modify albo query scale options.

        Setting a value dla any of the "from", "from_" albo "to" options
        generates a <<RangeChanged>> event."""
        jeżeli cnf:
            kw.update(cnf)
        Widget.configure(self, **kw)
        jeżeli any(['from' w kw, 'from_' w kw, 'to' w kw]):
            self.event_generate('<<RangeChanged>>')


    def get(self, x=Nic, y=Nic):
        """Get the current value of the value option, albo the value
        corresponding to the coordinates x, y jeżeli they are specified.

        x oraz y are pixel coordinates relative to the scale widget
        origin."""
        zwróć self.tk.call(self._w, 'get', x, y)


klasa Scrollbar(Widget, tkinter.Scrollbar):
    """Ttk Scrollbar controls the viewport of a scrollable widget."""

    def __init__(self, master=Nic, **kw):
        """Construct a Ttk Scrollbar przy parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus

        WIDGET-SPECIFIC OPTIONS

            command, orient
        """
        Widget.__init__(self, master, "ttk::scrollbar", kw)


klasa Separator(Widget):
    """Ttk Separator widget displays a horizontal albo vertical separator
    bar."""

    def __init__(self, master=Nic, **kw):
        """Construct a Ttk Separator przy parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus

        WIDGET-SPECIFIC OPTIONS

            orient
        """
        Widget.__init__(self, master, "ttk::separator", kw)


klasa Sizegrip(Widget):
    """Ttk Sizegrip allows the user to resize the containing toplevel
    window by pressing oraz dragging the grip."""

    def __init__(self, master=Nic, **kw):
        """Construct a Ttk Sizegrip przy parent master.

        STANDARD OPTIONS

            class, cursor, state, style, takefocus
        """
        Widget.__init__(self, master, "ttk::sizegrip", kw)


klasa Treeview(Widget, tkinter.XView, tkinter.YView):
    """Ttk Treeview widget displays a hierarchical collection of items.

    Each item has a textual label, an optional image, oraz an optional list
    of data values. The data values are displayed w successive columns
    after the tree label."""

    def __init__(self, master=Nic, **kw):
        """Construct a Ttk Treeview przy parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus, xscrollcommand,
            yscrollcommand

        WIDGET-SPECIFIC OPTIONS

            columns, displaycolumns, height, padding, selectmode, show

        ITEM OPTIONS

            text, image, values, open, tags

        TAG OPTIONS

            foreground, background, font, image
        """
        Widget.__init__(self, master, "ttk::treeview", kw)


    def bbox(self, item, column=Nic):
        """Returns the bounding box (relative to the treeview widget's
        window) of the specified item w the form x y width height.

        If column jest specified, returns the bounding box of that cell.
        If the item jest nie visible (i.e., jeżeli it jest a descendant of a
        closed item albo jest scrolled offscreen), returns an empty string."""
        zwróć self._getints(self.tk.call(self._w, "bbox", item, column)) albo ''


    def get_children(self, item=Nic):
        """Returns a tuple of children belonging to item.

        If item jest nie specified, returns root children."""
        zwróć self.tk.splitlist(
                self.tk.call(self._w, "children", item albo '') albo ())


    def set_children(self, item, *newchildren):
        """Replaces item's child przy newchildren.

        Children present w item that are nie present w newchildren
        are detached z tree. No items w newchildren may be an
        ancestor of item."""
        self.tk.call(self._w, "children", item, newchildren)


    def column(self, column, option=Nic, **kw):
        """Query albo modify the options dla the specified column.

        If kw jest nie given, returns a dict of the column option values. If
        option jest specified then the value dla that option jest returned.
        Otherwise, sets the options to the corresponding values."""
        jeżeli option jest nie Nic:
            kw[option] = Nic
        zwróć _val_or_dict(self.tk, kw, self._w, "column", column)


    def delete(self, *items):
        """Delete all specified items oraz all their descendants. The root
        item may nie be deleted."""
        self.tk.call(self._w, "delete", items)


    def detach(self, *items):
        """Unlinks all of the specified items z the tree.

        The items oraz all of their descendants are still present, oraz may
        be reinserted at another point w the tree, but will nie be
        displayed. The root item may nie be detached."""
        self.tk.call(self._w, "detach", items)


    def exists(self, item):
        """Returns Prawda jeżeli the specified item jest present w the tree,
        Nieprawda otherwise."""
        zwróć self.tk.getboolean(self.tk.call(self._w, "exists", item))


    def focus(self, item=Nic):
        """If item jest specified, sets the focus item to item. Otherwise,
        returns the current focus item, albo '' jeżeli there jest none."""
        zwróć self.tk.call(self._w, "focus", item)


    def heading(self, column, option=Nic, **kw):
        """Query albo modify the heading options dla the specified column.

        If kw jest nie given, returns a dict of the heading option values. If
        option jest specified then the value dla that option jest returned.
        Otherwise, sets the options to the corresponding values.

        Valid options/values are:
            text: text
                The text to display w the column heading
            image: image_name
                Specifies an image to display to the right of the column
                heading
            anchor: anchor
                Specifies how the heading text should be aligned. One of
                the standard Tk anchor values
            command: callback
                A callback to be invoked when the heading label jest
                pressed.

        To configure the tree column heading, call this przy column = "#0" """
        cmd = kw.get('command')
        jeżeli cmd oraz nie isinstance(cmd, str):
            # callback nie registered yet, do it now
            kw['command'] = self.master.register(cmd, self._substitute)

        jeżeli option jest nie Nic:
            kw[option] = Nic

        zwróć _val_or_dict(self.tk, kw, self._w, 'heading', column)


    def identify(self, component, x, y):
        """Returns a description of the specified component under the
        point given by x oraz y, albo the empty string jeżeli no such component
        jest present at that position."""
        zwróć self.tk.call(self._w, "identify", component, x, y)


    def identify_row(self, y):
        """Returns the item ID of the item at position y."""
        zwróć self.identify("row", 0, y)


    def identify_column(self, x):
        """Returns the data column identifier of the cell at position x.

        The tree column has ID #0."""
        zwróć self.identify("column", x, 0)


    def identify_region(self, x, y):
        """Returns one of:

        heading: Tree heading area.
        separator: Space between two columns headings;
        tree: The tree area.
        cell: A data cell.

        * Availability: Tk 8.6"""
        zwróć self.identify("region", x, y)


    def identify_element(self, x, y):
        """Returns the element at position x, y.

        * Availability: Tk 8.6"""
        zwróć self.identify("element", x, y)


    def index(self, item):
        """Returns the integer index of item within its parent's list
        of children."""
        zwróć self.tk.getint(self.tk.call(self._w, "index", item))


    def insert(self, parent, index, iid=Nic, **kw):
        """Creates a new item oraz zwróć the item identifier of the newly
        created item.

        parent jest the item ID of the parent item, albo the empty string
        to create a new top-level item. index jest an integer, albo the value
        end, specifying where w the list of parent's children to insert
        the new item. If index jest less than albo equal to zero, the new node
        jest inserted at the beginning, jeżeli index jest greater than albo equal to
        the current number of children, it jest inserted at the end. If iid
        jest specified, it jest used jako the item identifier, iid must nie
        already exist w the tree. Otherwise, a new unique identifier
        jest generated."""
        opts = _format_optdict(kw)
        jeżeli iid:
            res = self.tk.call(self._w, "insert", parent, index,
                "-id", iid, *opts)
        inaczej:
            res = self.tk.call(self._w, "insert", parent, index, *opts)

        zwróć res


    def item(self, item, option=Nic, **kw):
        """Query albo modify the options dla the specified item.

        If no options are given, a dict przy options/values dla the item
        jest returned. If option jest specified then the value dla that option
        jest returned. Otherwise, sets the options to the corresponding
        values jako given by kw."""
        jeżeli option jest nie Nic:
            kw[option] = Nic
        zwróć _val_or_dict(self.tk, kw, self._w, "item", item)


    def move(self, item, parent, index):
        """Moves item to position index w parent's list of children.

        It jest illegal to move an item under one of its descendants. If
        index jest less than albo equal to zero, item jest moved to the
        beginning, jeżeli greater than albo equal to the number of children,
        it jest moved to the end. If item was detached it jest reattached."""
        self.tk.call(self._w, "move", item, parent, index)

    reattach = move # A sensible method name dla reattaching detached items


    def next(self, item):
        """Returns the identifier of item's next sibling, albo '' jeżeli item
        jest the last child of its parent."""
        zwróć self.tk.call(self._w, "next", item)


    def parent(self, item):
        """Returns the ID of the parent of item, albo '' jeżeli item jest at the
        top level of the hierarchy."""
        zwróć self.tk.call(self._w, "parent", item)


    def prev(self, item):
        """Returns the identifier of item's previous sibling, albo '' if
        item jest the first child of its parent."""
        zwróć self.tk.call(self._w, "prev", item)


    def see(self, item):
        """Ensure that item jest visible.

        Sets all of item's ancestors open option to Prawda, oraz scrolls
        the widget jeżeli necessary so that item jest within the visible
        portion of the tree."""
        self.tk.call(self._w, "see", item)


    def selection(self, selop=Nic, items=Nic):
        """If selop jest nie specified, returns selected items."""
        zwróć self.tk.call(self._w, "selection", selop, items)


    def selection_set(self, items):
        """items becomes the new selection."""
        self.selection("set", items)


    def selection_add(self, items):
        """Add items to the selection."""
        self.selection("add", items)


    def selection_remove(self, items):
        """Remove items z the selection."""
        self.selection("remove", items)


    def selection_toggle(self, items):
        """Toggle the selection state of each item w items."""
        self.selection("toggle", items)


    def set(self, item, column=Nic, value=Nic):
        """Query albo set the value of given item.

        With one argument, zwróć a dictionary of column/value pairs
        dla the specified item. With two arguments, zwróć the current
        value of the specified column. With three arguments, set the
        value of given column w given item to the specified value."""
        res = self.tk.call(self._w, "set", item, column, value)
        jeżeli column jest Nic oraz value jest Nic:
            zwróć _splitdict(self.tk, res,
                              cut_minus=Nieprawda, conv=_tclobj_to_py)
        inaczej:
            zwróć res


    def tag_bind(self, tagname, sequence=Nic, callback=Nic):
        """Bind a callback dla the given event sequence to the tag tagname.
        When an event jest delivered to an item, the callbacks dla each
        of the item's tags option are called."""
        self._bind((self._w, "tag", "bind", tagname), sequence, callback, add=0)


    def tag_configure(self, tagname, option=Nic, **kw):
        """Query albo modify the options dla the specified tagname.

        If kw jest nie given, returns a dict of the option settings dla tagname.
        If option jest specified, returns the value dla that option dla the
        specified tagname. Otherwise, sets the options to the corresponding
        values dla the given tagname."""
        jeżeli option jest nie Nic:
            kw[option] = Nic
        zwróć _val_or_dict(self.tk, kw, self._w, "tag", "configure",
            tagname)


    def tag_has(self, tagname, item=Nic):
        """If item jest specified, returns 1 albo 0 depending on whether the
        specified item has the given tagname. Otherwise, returns a list of
        all items which have the specified tag.

        * Availability: Tk 8.6"""
        jeżeli item jest Nic:
            zwróć self.tk.splitlist(
                self.tk.call(self._w, "tag", "has", tagname))
        inaczej:
            zwróć self.tk.getboolean(
                self.tk.call(self._w, "tag", "has", tagname, item))


# Extensions

klasa LabeledScale(Frame):
    """A Ttk Scale widget przy a Ttk Label widget indicating its
    current value.

    The Ttk Scale can be accessed through instance.scale, oraz Ttk Label
    can be accessed through instance.label"""

    def __init__(self, master=Nic, variable=Nic, from_=0, to=10, **kw):
        """Construct an horizontal LabeledScale przy parent master, a
        variable to be associated przy the Ttk Scale widget oraz its range.
        If variable jest nie specified, a tkinter.IntVar jest created.

        WIDGET-SPECIFIC OPTIONS

            compound: 'top' albo 'bottom'
                Specifies how to display the label relative to the scale.
                Defaults to 'top'.
        """
        self._label_top = kw.pop('compound', 'top') == 'top'

        Frame.__init__(self, master, **kw)
        self._variable = variable albo tkinter.IntVar(master)
        self._variable.set(from_)
        self._last_valid = from_

        self.label = Label(self)
        self.scale = Scale(self, variable=self._variable, from_=from_, to=to)
        self.scale.bind('<<RangeChanged>>', self._adjust)

        # position scale oraz label according to the compound option
        scale_side = 'bottom' jeżeli self._label_top inaczej 'top'
        label_side = 'top' jeżeli scale_side == 'bottom' inaczej 'bottom'
        self.scale.pack(side=scale_side, fill='x')
        tmp = Label(self).pack(side=label_side) # place holder
        self.label.place(anchor='n' jeżeli label_side == 'top' inaczej 's')

        # update the label jako scale albo variable changes
        self.__tracecb = self._variable.trace_variable('w', self._adjust)
        self.bind('<Configure>', self._adjust)
        self.bind('<Map>', self._adjust)


    def destroy(self):
        """Destroy this widget oraz possibly its associated variable."""
        spróbuj:
            self._variable.trace_vdelete('w', self.__tracecb)
        wyjąwszy AttributeError:
            # widget has been destroyed already
            dalej
        inaczej:
            usuń self._variable
            Frame.destroy(self)


    def _adjust(self, *args):
        """Adjust the label position according to the scale."""
        def adjust_label():
            self.update_idletasks() # "force" scale redraw

            x, y = self.scale.coords()
            jeżeli self._label_top:
                y = self.scale.winfo_y() - self.label.winfo_reqheight()
            inaczej:
                y = self.scale.winfo_reqheight() + self.label.winfo_reqheight()

            self.label.place_configure(x=x, y=y)

        from_ = _to_number(self.scale['from'])
        to = _to_number(self.scale['to'])
        jeżeli to < from_:
            from_, to = to, from_
        newval = self._variable.get()
        jeżeli nie from_ <= newval <= to:
            # value outside range, set value back to the last valid one
            self.value = self._last_valid
            zwróć

        self._last_valid = newval
        self.label['text'] = newval
        self.after_idle(adjust_label)


    def _get_value(self):
        """Return current scale value."""
        zwróć self._variable.get()


    def _set_value(self, val):
        """Set new scale value."""
        self._variable.set(val)


    value = property(_get_value, _set_value)


klasa OptionMenu(Menubutton):
    """Themed OptionMenu, based after tkinter's OptionMenu, which allows
    the user to select a value z a menu."""

    def __init__(self, master, variable, default=Nic, *values, **kwargs):
        """Construct a themed OptionMenu widget przy master jako the parent,
        the resource textvariable set to variable, the initially selected
        value specified by the default parameter, the menu values given by
        *values oraz additional keywords.

        WIDGET-SPECIFIC OPTIONS

            style: stylename
                Menubutton style.
            direction: 'above', 'below', 'left', 'right', albo 'flush'
                Menubutton direction.
            command: callback
                A callback that will be invoked after selecting an item.
        """
        kw = {'textvariable': variable, 'style': kwargs.pop('style', Nic),
              'direction': kwargs.pop('direction', Nic)}
        Menubutton.__init__(self, master, **kw)
        self['menu'] = tkinter.Menu(self, tearoff=Nieprawda)

        self._variable = variable
        self._callback = kwargs.pop('command', Nic)
        jeżeli kwargs:
            podnieś tkinter.TclError('unknown option -%s' % (
                next(iter(kwargs.keys()))))

        self.set_menu(default, *values)


    def __getitem__(self, item):
        jeżeli item == 'menu':
            zwróć self.nametowidget(Menubutton.__getitem__(self, item))

        zwróć Menubutton.__getitem__(self, item)


    def set_menu(self, default=Nic, *values):
        """Build a new menu of radiobuttons przy *values oraz optionally
        a default value."""
        menu = self['menu']
        menu.delete(0, 'end')
        dla val w values:
            menu.add_radiobutton(label=val,
                command=tkinter._setit(self._variable, val, self._callback))

        jeżeli default:
            self._variable.set(default)


    def destroy(self):
        """Destroy this widget oraz its associated variable."""
        usuń self._variable
        Menubutton.destroy(self)
