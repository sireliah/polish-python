# base klasa dla tk common dialogues
#
# this module provides a base klasa dla accessing the common
# dialogues available w Tk 4.2 oraz newer.  use filedialog,
# colorchooser, oraz messagebox to access the individual
# dialogs.
#
# written by Fredrik Lundh, May 1997
#

z tkinter zaimportuj *

klasa Dialog:

    command  = Nic

    def __init__(self, master=Nic, **options):

        # FIXME: should this be placed on the module level instead?
        jeżeli TkVersion < 4.2:
            podnieś TclError("this module requires Tk 4.2 albo newer")

        self.master  = master
        self.options = options
        jeżeli nie master oraz options.get('parent'):
            self.master = options['parent']

    def _fixoptions(self):
        dalej # hook

    def _fixresult(self, widget, result):
        zwróć result # hook

    def show(self, **options):

        # update instance options
        dla k, v w options.items():
            self.options[k] = v

        self._fixoptions()

        # we need a dummy widget to properly process the options
        # (at least jako long jako we use Tkinter 1.63)
        w = Frame(self.master)

        spróbuj:

            s = w.tk.call(self.command, *w._options(self.options))

            s = self._fixresult(w, s)

        w_końcu:

            spróbuj:
                # get rid of the widget
                w.destroy()
            wyjąwszy:
                dalej

        zwróć s
