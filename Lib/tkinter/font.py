# Tkinter font wrapper
#
# written by Fredrik Lundh, February 1998
#

__version__ = "0.9"

zaimportuj itertools
zaimportuj tkinter


# weight/slant
NORMAL = "normal"
ROMAN = "roman"
BOLD   = "bold"
ITALIC = "italic"


def nametofont(name):
    """Given the name of a tk named font, returns a Font representation.
    """
    zwróć Font(name=name, exists=Prawda)


klasa Font:
    """Represents a named font.

    Constructor options are:

    font -- font specifier (name, system font, albo (family, size, style)-tuple)
    name -- name to use dla this font configuration (defaults to a unique name)
    exists -- does a named font by this name already exist?
       Creates a new named font jeżeli Nieprawda, points to the existing font jeżeli Prawda.
       Raises _tkinter.TclError jeżeli the assertion jest false.

       the following are ignored jeżeli font jest specified:

    family -- font 'family', e.g. Courier, Times, Helvetica
    size -- font size w points
    weight -- font thickness: NORMAL, BOLD
    slant -- font slant: ROMAN, ITALIC
    underline -- font underlining: false (0), true (1)
    overstrike -- font strikeout: false (0), true (1)

    """

    counter = itertools.count(1)

    def _set(self, kw):
        options = []
        dla k, v w kw.items():
            options.append("-"+k)
            options.append(str(v))
        zwróć tuple(options)

    def _get(self, args):
        options = []
        dla k w args:
            options.append("-"+k)
        zwróć tuple(options)

    def _mkdict(self, args):
        options = {}
        dla i w range(0, len(args), 2):
            options[args[i][1:]] = args[i+1]
        zwróć options

    def __init__(self, root=Nic, font=Nic, name=Nic, exists=Nieprawda,
                 **options):
        jeżeli nie root:
            root = tkinter._default_root
        tk = getattr(root, 'tk', root)
        jeżeli font:
            # get actual settings corresponding to the given font
            font = tk.splitlist(tk.call("font", "actual", font))
        inaczej:
            font = self._set(options)
        jeżeli nie name:
            name = "font" + str(next(self.counter))
        self.name = name

        jeżeli exists:
            self.delete_font = Nieprawda
            # confirm font exists
            jeżeli self.name nie w tk.splitlist(tk.call("font", "names")):
                podnieś tkinter._tkinter.TclError(
                    "named font %s does nie already exist" % (self.name,))
            # jeżeli font config info supplied, apply it
            jeżeli font:
                tk.call("font", "configure", self.name, *font)
        inaczej:
            # create new font (raises TclError jeżeli the font exists)
            tk.call("font", "create", self.name, *font)
            self.delete_font = Prawda
        self._tk = tk
        self._split = tk.splitlist
        self._call  = tk.call

    def __str__(self):
        zwróć self.name

    def __eq__(self, other):
        zwróć isinstance(other, Font) oraz self.name == other.name

    def __getitem__(self, key):
        zwróć self.cget(key)

    def __setitem__(self, key, value):
        self.configure(**{key: value})

    def __del__(self):
        spróbuj:
            jeżeli self.delete_font:
                self._call("font", "delete", self.name)
        wyjąwszy Exception:
            dalej

    def copy(self):
        "Return a distinct copy of the current font"
        zwróć Font(self._tk, **self.actual())

    def actual(self, option=Nic, displayof=Nic):
        "Return actual font attributes"
        args = ()
        jeżeli displayof:
            args = ('-displayof', displayof)
        jeżeli option:
            args = args + ('-' + option, )
            zwróć self._call("font", "actual", self.name, *args)
        inaczej:
            zwróć self._mkdict(
                self._split(self._call("font", "actual", self.name, *args)))

    def cget(self, option):
        "Get font attribute"
        zwróć self._call("font", "config", self.name, "-"+option)

    def config(self, **options):
        "Modify font attributes"
        jeżeli options:
            self._call("font", "config", self.name,
                  *self._set(options))
        inaczej:
            zwróć self._mkdict(
                self._split(self._call("font", "config", self.name)))

    configure = config

    def measure(self, text, displayof=Nic):
        "Return text width"
        args = (text,)
        jeżeli displayof:
            args = ('-displayof', displayof, text)
        zwróć self._tk.getint(self._call("font", "measure", self.name, *args))

    def metrics(self, *options, **kw):
        """Return font metrics.

        For best performance, create a dummy widget
        using this font before calling this method."""
        args = ()
        displayof = kw.pop('displayof', Nic)
        jeżeli displayof:
            args = ('-displayof', displayof)
        jeżeli options:
            args = args + self._get(options)
            zwróć self._tk.getint(
                self._call("font", "metrics", self.name, *args))
        inaczej:
            res = self._split(self._call("font", "metrics", self.name, *args))
            options = {}
            dla i w range(0, len(res), 2):
                options[res[i][1:]] = self._tk.getint(res[i+1])
            zwróć options


def families(root=Nic, displayof=Nic):
    "Get font families (as a tuple)"
    jeżeli nie root:
        root = tkinter._default_root
    args = ()
    jeżeli displayof:
        args = ('-displayof', displayof)
    zwróć root.tk.splitlist(root.tk.call("font", "families", *args))


def names(root=Nic):
    "Get names of defined fonts (as a tuple)"
    jeżeli nie root:
        root = tkinter._default_root
    zwróć root.tk.splitlist(root.tk.call("font", "names"))


# --------------------------------------------------------------------
# test stuff

jeżeli __name__ == "__main__":

    root = tkinter.Tk()

    # create a font
    f = Font(family="times", size=30, weight=NORMAL)

    print(f.actual())
    print(f.actual("family"))
    print(f.actual("weight"))

    print(f.config())
    print(f.cget("family"))
    print(f.cget("weight"))

    print(names())

    print(f.measure("hello"), f.metrics("linespace"))

    print(f.metrics(displayof=root))

    f = Font(font=("Courier", 20, "bold"))
    print(f.measure("hello"), f.metrics("linespace", displayof=root))

    w = tkinter.Label(root, text="Hello, world", font=f)
    w.pack()

    w = tkinter.Button(root, text="Quit!", command=root.destroy)
    w.pack()

    fb = Font(font=w["font"]).copy()
    fb.config(weight=BOLD)

    w.config(font=fb)

    tkinter.mainloop()
