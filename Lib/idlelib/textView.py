"""Simple text browser dla IDLE

"""

z tkinter zaimportuj *
zaimportuj tkinter.messagebox jako tkMessageBox

klasa TextViewer(Toplevel):
    """A simple text viewer dialog dla IDLE

    """
    def __init__(self, parent, title, text, modal=Prawda, _htest=Nieprawda):
        """Show the given text w a scrollable window przy a 'close' button

        If modal option set to Nieprawda, user can interact przy other windows,
        otherwise they will be unable to interact przy other windows until
        the textview window jest closed.

        _htest - bool; change box location when running htest.
        """
        Toplevel.__init__(self, parent)
        self.configure(borderwidth=5)
        # place dialog below parent jeżeli running htest
        self.geometry("=%dx%d+%d+%d" % (625, 500,
                           parent.winfo_rootx() + 10,
                           parent.winfo_rooty() + (10 jeżeli nie _htest inaczej 100)))
        #elguavas - config placeholders til config stuff completed
        self.bg = '#ffffff'
        self.fg = '#000000'

        self.CreateWidgets()
        self.title(title)
        self.protocol("WM_DELETE_WINDOW", self.Ok)
        self.parent = parent
        self.textView.focus_set()
        #key bindings dla this dialog
        self.bind('<Return>',self.Ok) #dismiss dialog
        self.bind('<Escape>',self.Ok) #dismiss dialog
        self.textView.insert(0.0, text)
        self.textView.config(state=DISABLED)

        jeżeli modal:
            self.transient(parent)
            self.grab_set()
            self.wait_window()

    def CreateWidgets(self):
        frameText = Frame(self, relief=SUNKEN, height=700)
        frameButtons = Frame(self)
        self.buttonOk = Button(frameButtons, text='Close',
                               command=self.Ok, takefocus=FALSE)
        self.scrollbarView = Scrollbar(frameText, orient=VERTICAL,
                                       takefocus=FALSE, highlightthickness=0)
        self.textView = Text(frameText, wrap=WORD, highlightthickness=0,
                             fg=self.fg, bg=self.bg)
        self.scrollbarView.config(command=self.textView.yview)
        self.textView.config(yscrollcommand=self.scrollbarView.set)
        self.buttonOk.pack()
        self.scrollbarView.pack(side=RIGHT,fill=Y)
        self.textView.pack(side=LEFT,expand=TRUE,fill=BOTH)
        frameButtons.pack(side=BOTTOM,fill=X)
        frameText.pack(side=TOP,expand=TRUE,fill=BOTH)

    def Ok(self, event=Nic):
        self.destroy()


def view_text(parent, title, text, modal=Prawda):
    zwróć TextViewer(parent, title, text, modal)

def view_file(parent, title, filename, encoding=Nic, modal=Prawda):
    spróbuj:
        przy open(filename, 'r', encoding=encoding) jako file:
            contents = file.read()
    wyjąwszy IOError:
        tkMessageBox.showerror(title='File Load Error',
                               message='Unable to load file %r .' % filename,
                               parent=parent)
    inaczej:
        zwróć view_text(parent, title, contents, modal)

jeżeli __name__ == '__main__':
    zaimportuj unittest
    unittest.main('idlelib.idle_test.test_textview', verbosity=2, exit=Nieprawda)
    z idlelib.idle_test.htest zaimportuj run
    run(TextViewer)
