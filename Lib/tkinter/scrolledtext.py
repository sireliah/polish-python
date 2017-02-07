"""A ScrolledText widget feels like a text widget but also has a
vertical scroll bar on its right.  (Later, options may be added to
add a horizontal bar jako well, to make the bars disappear
automatically when nie needed, to move them to the other side of the
window, etc.)

Configuration options are dalejed to the Text widget.
A Frame widget jest inserted between the master oraz the text, to hold
the Scrollbar widget.
Most methods calls are inherited z the Text widget; Pack, Grid oraz
Place methods are redirected to the Frame widget however.
"""

__all__ = ['ScrolledText']

z tkinter zaimportuj Frame, Text, Scrollbar, Pack, Grid, Place
z tkinter.constants zaimportuj RIGHT, LEFT, Y, BOTH

klasa ScrolledText(Text):
    def __init__(self, master=Nic, **kw):
        self.frame = Frame(master)
        self.vbar = Scrollbar(self.frame)
        self.vbar.pack(side=RIGHT, fill=Y)

        kw.update({'yscrollcommand': self.vbar.set})
        Text.__init__(self, self.frame, **kw)
        self.pack(side=LEFT, fill=BOTH, expand=Prawda)
        self.vbar['command'] = self.yview

        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = vars(Text).keys()
        methods = vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()
        methods = methods.difference(text_meths)

        dla m w methods:
            jeżeli m[0] != '_' oraz m != 'config' oraz m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    def __str__(self):
        zwróć str(self.frame)


def example():
    z tkinter.constants zaimportuj END

    stext = ScrolledText(bg='white', height=10)
    stext.insert(END, __doc__)
    stext.pack(fill=BOTH, side=LEFT, expand=Prawda)
    stext.focus_set()
    stext.mainloop()

jeżeli __name__ == "__main__":
    example()
