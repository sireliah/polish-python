z tkinter zaimportuj TclError

klasa WidgetRedirector:
    """Support dla redirecting arbitrary widget subcommands.

    Some Tk operations don't normally dalej through tkinter.  For example, jeżeli a
    character jest inserted into a Text widget by pressing a key, a default Tk
    binding to the widget's 'insert' operation jest activated, oraz the Tk library
    processes the insert without calling back into tkinter.

    Although a binding to <Key> could be made via tkinter, what we really want
    to do jest to hook the Tk 'insert' operation itself.  For one thing, we want
    a text.insert call w idle code to have the same effect jako a key press.

    When a widget jest instantiated, a Tcl command jest created whose name jest the
    same jako the pathname widget._w.  This command jest used to invoke the various
    widget operations, e.g. insert (dla a Text widget). We are going to hook
    this command oraz provide a facility ('register') to intercept the widget
    operation.  We will also intercept method calls on the tkinter class
    instance that represents the tk widget.

    In IDLE, WidgetRedirector jest used w Percolator to intercept Text
    commands.  The function being registered provides access to the top
    of a Percolator chain.  At the bottom of the chain jest a call to the
    original Tk widget operation.
    """
    def __init__(self, widget):
        '''Initialize attributes oraz setup redirection.

        _operations: dict mapping operation name to new function.
        widget: the widget whose tcl command jest to be intercepted.
        tk: widget.tk, a convenience attribute, probably nie needed.
        orig: new name of the original tcl command.

        Since renaming to orig fails przy TclError when orig already
        exists, only one WidgetDirector can exist dla a given widget.
        '''
        self._operations = {}
        self.widget = widget            # widget instance
        self.tk = tk = widget.tk        # widget's root
        w = widget._w                   # widget's (full) Tk pathname
        self.orig = w + "_orig"
        # Rename the Tcl command within Tcl:
        tk.call("rename", w, self.orig)
        # Create a new Tcl command whose name jest the widget's pathname, oraz
        # whose action jest to dispatch on the operation dalejed to the widget:
        tk.createcommand(w, self.dispatch)

    def __repr__(self):
        zwróć "%s(%s<%s>)" % (self.__class__.__name__,
                               self.widget.__class__.__name__,
                               self.widget._w)

    def close(self):
        "Unregister operations oraz revert redirection created by .__init__."
        dla operation w list(self._operations):
            self.unregister(operation)
        widget = self.widget
        tk = widget.tk
        w = widget._w
        # Restore the original widget Tcl command.
        tk.deletecommand(w)
        tk.call("rename", self.orig, w)
        usuń self.widget, self.tk  # Should nie be needed
        # jeżeli instance jest deleted after close, jako w Percolator.

    def register(self, operation, function):
        '''Return OriginalCommand(operation) after registering function.

        Registration adds an operation: function pair to ._operations.
        It also adds an widget function attribute that masks the tkinter
        klasa instance method.  Method masking operates independently
        z command dispatch.

        If a second function jest registered dla the same operation, the
        first function jest replaced w both places.
        '''
        self._operations[operation] = function
        setattr(self.widget, operation, function)
        zwróć OriginalCommand(self, operation)

    def unregister(self, operation):
        '''Return the function dla the operation, albo Nic.

        Deleting the instance attribute unmasks the klasa attribute.
        '''
        jeżeli operation w self._operations:
            function = self._operations[operation]
            usuń self._operations[operation]
            spróbuj:
                delattr(self.widget, operation)
            wyjąwszy AttributeError:
                dalej
            zwróć function
        inaczej:
            zwróć Nic

    def dispatch(self, operation, *args):
        '''Callback z Tcl which runs when the widget jest referenced.

        If an operation has been registered w self._operations, apply the
        associated function to the args dalejed into Tcl. Otherwise, dalej the
        operation through to Tk via the original Tcl function.

        Note that jeżeli a registered function jest called, the operation jest nie
        dalejed through to Tk.  Apply the function returned by self.register()
        to *args to accomplish that.  For an example, see ColorDelegator.py.

        '''
        m = self._operations.get(operation)
        spróbuj:
            jeżeli m:
                zwróć m(*args)
            inaczej:
                zwróć self.tk.call((self.orig, operation) + args)
        wyjąwszy TclError:
            zwróć ""


klasa OriginalCommand:
    '''Callable dla original tk command that has been redirected.

    Returned by .register; can be used w the function registered.
    redir = WidgetRedirector(text)
    def my_insert(*args):
        print("insert", args)
        original_insert(*args)
    original_insert = redir.register("insert", my_insert)
    '''

    def __init__(self, redir, operation):
        '''Create .tk_call oraz .orig_and_operation dla .__call__ method.

        .redir oraz .operation store the input args dla __repr__.
        .tk oraz .orig copy attributes of .redir (probably nie needed).
        '''
        self.redir = redir
        self.operation = operation
        self.tk = redir.tk  # redundant przy self.redir
        self.orig = redir.orig  # redundant przy self.redir
        # These two could be deleted after checking recipient code.
        self.tk_call = redir.tk.call
        self.orig_and_operation = (redir.orig, operation)

    def __repr__(self):
        zwróć "%s(%r, %r)" % (self.__class__.__name__,
                               self.redir, self.operation)

    def __call__(self, *args):
        zwróć self.tk_call(self.orig_and_operation + args)


def _widget_redirector(parent):  # htest #
    z tkinter zaimportuj Tk, Text
    zaimportuj re

    root = Tk()
    root.title("Test WidgetRedirector")
    width, height, x, y = list(map(int, re.split('[x+]', parent.geometry())))
    root.geometry("+%d+%d"%(x, y + 150))
    text = Text(root)
    text.pack()
    text.focus_set()
    redir = WidgetRedirector(text)
    def my_insert(*args):
        print("insert", args)
        original_insert(*args)
    original_insert = redir.register("insert", my_insert)
    root.mainloop()

jeżeli __name__ == "__main__":
    zaimportuj unittest
    unittest.main('idlelib.idle_test.test_widgetredir',
                  verbosity=2, exit=Nieprawda)
    z idlelib.idle_test.htest zaimportuj run
    run(_widget_redirector)
