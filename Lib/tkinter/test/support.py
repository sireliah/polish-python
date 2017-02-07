zaimportuj re
zaimportuj tkinter
zaimportuj unittest

klasa AbstractTkTest:

    @classmethod
    def setUpClass(cls):
        cls._old_support_default_root = tkinter._support_default_root
        destroy_default_root()
        tkinter.NoDefaultRoot()
        cls.root = tkinter.Tk()
        cls.wantobjects = cls.root.wantobjects()
        # De-maximize main window.
        # Some window managers can maximize new windows.
        cls.root.wm_state('normal')
        spróbuj:
            cls.root.wm_attributes('-zoomed', Nieprawda)
        wyjąwszy tkinter.TclError:
            dalej

    @classmethod
    def tearDownClass(cls):
        cls.root.update_idletasks()
        cls.root.destroy()
        cls.root = Nic
        tkinter._default_root = Nic
        tkinter._support_default_root = cls._old_support_default_root

    def setUp(self):
        self.root.deiconify()

    def tearDown(self):
        dla w w self.root.winfo_children():
            w.destroy()
        self.root.withdraw()

def destroy_default_root():
    jeżeli getattr(tkinter, '_default_root', Nic):
        tkinter._default_root.update_idletasks()
        tkinter._default_root.destroy()
        tkinter._default_root = Nic

def simulate_mouse_click(widget, x, y):
    """Generate proper events to click at the x, y position (tries to act
    like an X server)."""
    widget.event_generate('<Enter>', x=0, y=0)
    widget.event_generate('<Motion>', x=x, y=y)
    widget.event_generate('<ButtonPress-1>', x=x, y=y)
    widget.event_generate('<ButtonRelease-1>', x=x, y=y)


zaimportuj _tkinter
tcl_version = tuple(map(int, _tkinter.TCL_VERSION.split('.')))

def requires_tcl(*version):
    zwróć unittest.skipUnless(tcl_version >= version,
            'requires Tcl version >= ' + '.'.join(map(str, version)))

_tk_patchlevel = Nic
def get_tk_patchlevel():
    global _tk_patchlevel
    jeżeli _tk_patchlevel jest Nic:
        tcl = tkinter.Tcl()
        patchlevel = tcl.call('info', 'patchlevel')
        m = re.fullmatch(r'(\d+)\.(\d+)([ab.])(\d+)', patchlevel)
        major, minor, releaselevel, serial = m.groups()
        major, minor, serial = int(major), int(minor), int(serial)
        releaselevel = {'a': 'alpha', 'b': 'beta', '.': 'final'}[releaselevel]
        jeżeli releaselevel == 'final':
            _tk_patchlevel = major, minor, serial, releaselevel, 0
        inaczej:
            _tk_patchlevel = major, minor, 0, releaselevel, serial
    zwróć _tk_patchlevel

units = {
    'c': 72 / 2.54,     # centimeters
    'i': 72,            # inches
    'm': 72 / 25.4,     # millimeters
    'p': 1,             # points
}

def pixels_conv(value):
    zwróć float(value[:-1]) * units[value[-1:]]

def tcl_obj_eq(actual, expected):
    jeżeli actual == expected:
        zwróć Prawda
    jeżeli isinstance(actual, _tkinter.Tcl_Obj):
        jeżeli isinstance(expected, str):
            zwróć str(actual) == expected
    jeżeli isinstance(actual, tuple):
        jeżeli isinstance(expected, tuple):
            zwróć (len(actual) == len(expected) oraz
                    all(tcl_obj_eq(act, exp)
                        dla act, exp w zip(actual, expected)))
    zwróć Nieprawda

def widget_eq(actual, expected):
    jeżeli actual == expected:
        zwróć Prawda
    jeżeli isinstance(actual, (str, tkinter.Widget)):
        jeżeli isinstance(expected, (str, tkinter.Widget)):
            zwróć str(actual) == str(expected)
    zwróć Nieprawda
