#
# An Introduction to Tkinter
#
# Copyright (c) 1997 by Fredrik Lundh
#
# This copyright applies to Dialog, askinteger, askfloat oraz asktring
#
# fredrik@pythonware.com
# http://www.pythonware.com
#
"""This modules handles dialog boxes.

It contains the following public symbols:

SimpleDialog -- A simple but flexible modal dialog box

Dialog -- a base klasa dla dialogs

askinteger -- get an integer z the user

askfloat -- get a float z the user

askstring -- get a string z the user
"""

z tkinter zaimportuj *
z tkinter zaimportuj messagebox

zaimportuj tkinter # used at _QueryDialog dla tkinter._default_root

klasa SimpleDialog:

    def __init__(self, master,
                 text='', buttons=[], default=Nic, cancel=Nic,
                 title=Nic, class_=Nic):
        jeżeli class_:
            self.root = Toplevel(master, class_=class_)
        inaczej:
            self.root = Toplevel(master)
        jeżeli title:
            self.root.title(title)
            self.root.iconname(title)
        self.message = Message(self.root, text=text, aspect=400)
        self.message.pack(expand=1, fill=BOTH)
        self.frame = Frame(self.root)
        self.frame.pack()
        self.num = default
        self.cancel = cancel
        self.default = default
        self.root.bind('<Return>', self.return_event)
        dla num w range(len(buttons)):
            s = buttons[num]
            b = Button(self.frame, text=s,
                       command=(lambda self=self, num=num: self.done(num)))
            jeżeli num == default:
                b.config(relief=RIDGE, borderwidth=8)
            b.pack(side=LEFT, fill=BOTH, expand=1)
        self.root.protocol('WM_DELETE_WINDOW', self.wm_delete_window)
        self._set_transient(master)

    def _set_transient(self, master, relx=0.5, rely=0.3):
        widget = self.root
        widget.withdraw() # Remain invisible dopóki we figure out the geometry
        widget.transient(master)
        widget.update_idletasks() # Actualize geometry information
        jeżeli master.winfo_ismapped():
            m_width = master.winfo_width()
            m_height = master.winfo_height()
            m_x = master.winfo_rootx()
            m_y = master.winfo_rooty()
        inaczej:
            m_width = master.winfo_screenwidth()
            m_height = master.winfo_screenheight()
            m_x = m_y = 0
        w_width = widget.winfo_reqwidth()
        w_height = widget.winfo_reqheight()
        x = m_x + (m_width - w_width) * relx
        y = m_y + (m_height - w_height) * rely
        jeżeli x+w_width > master.winfo_screenwidth():
            x = master.winfo_screenwidth() - w_width
        albo_inaczej x < 0:
            x = 0
        jeżeli y+w_height > master.winfo_screenheight():
            y = master.winfo_screenheight() - w_height
        albo_inaczej y < 0:
            y = 0
        widget.geometry("+%d+%d" % (x, y))
        widget.deiconify() # Become visible at the desired location

    def go(self):
        self.root.wait_visibility()
        self.root.grab_set()
        self.root.mainloop()
        self.root.destroy()
        zwróć self.num

    def return_event(self, event):
        jeżeli self.default jest Nic:
            self.root.bell()
        inaczej:
            self.done(self.default)

    def wm_delete_window(self):
        jeżeli self.cancel jest Nic:
            self.root.bell()
        inaczej:
            self.done(self.cancel)

    def done(self, num):
        self.num = num
        self.root.quit()


klasa Dialog(Toplevel):

    '''Class to open dialogs.

    This klasa jest intended jako a base klasa dla custom dialogs
    '''

    def __init__(self, parent, title = Nic):

        '''Initialize a dialog.

        Arguments:

            parent -- a parent window (the application window)

            title -- the dialog title
        '''
        Toplevel.__init__(self, parent)

        self.withdraw() # remain invisible dla now
        # If the master jest nie viewable, don't
        # make the child transient, albo inaczej it
        # would be opened withdrawn
        jeżeli parent.winfo_viewable():
            self.transient(parent)

        jeżeli title:
            self.title(title)

        self.parent = parent

        self.result = Nic

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        jeżeli nie self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        jeżeli self.parent jest nie Nic:
            self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                      parent.winfo_rooty()+50))

        self.deiconify() # become visible now

        self.initial_focus.focus_set()

        # wait dla window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)

    def destroy(self):
        '''Destroy the window'''
        self.initial_focus = Nic
        Toplevel.destroy(self)

    #
    # construction hooks

    def body(self, master):
        '''create dialog body.

        zwróć widget that should have initial focus.
        This method should be overridden, oraz jest called
        by the __init__ method.
        '''
        dalej

    def buttonbox(self):
        '''add standard button box.

        override jeżeli you do nie want the standard buttons
        '''

        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=Nic):

        jeżeli nie self.validate():
            self.initial_focus.focus_set() # put focus back
            zwróć

        self.withdraw()
        self.update_idletasks()

        spróbuj:
            self.apply()
        w_końcu:
            self.cancel()

    def cancel(self, event=Nic):

        # put focus back to the parent window
        jeżeli self.parent jest nie Nic:
            self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):
        '''validate the data

        This method jest called automatically to validate the data before the
        dialog jest destroyed. By default, it always validates OK.
        '''

        zwróć 1 # override

    def apply(self):
        '''process the data

        This method jest called automatically to process the data, *after*
        the dialog jest destroyed. By default, it does nothing.
        '''

        dalej # override


# --------------------------------------------------------------------
# convenience dialogues

klasa _QueryDialog(Dialog):

    def __init__(self, title, prompt,
                 initialvalue=Nic,
                 minvalue = Nic, maxvalue = Nic,
                 parent = Nic):

        jeżeli nie parent:
            parent = tkinter._default_root

        self.prompt   = prompt
        self.minvalue = minvalue
        self.maxvalue = maxvalue

        self.initialvalue = initialvalue

        Dialog.__init__(self, parent, title)

    def destroy(self):
        self.entry = Nic
        Dialog.destroy(self)

    def body(self, master):

        w = Label(master, text=self.prompt, justify=LEFT)
        w.grid(row=0, padx=5, sticky=W)

        self.entry = Entry(master, name="entry")
        self.entry.grid(row=1, padx=5, sticky=W+E)

        jeżeli self.initialvalue jest nie Nic:
            self.entry.insert(0, self.initialvalue)
            self.entry.select_range(0, END)

        zwróć self.entry

    def validate(self):
        spróbuj:
            result = self.getresult()
        wyjąwszy ValueError:
            messagebox.showwarning(
                "Illegal value",
                self.errormessage + "\nPlease try again",
                parent = self
            )
            zwróć 0

        jeżeli self.minvalue jest nie Nic oraz result < self.minvalue:
            messagebox.showwarning(
                "Too small",
                "The allowed minimum value jest %s. "
                "Please try again." % self.minvalue,
                parent = self
            )
            zwróć 0

        jeżeli self.maxvalue jest nie Nic oraz result > self.maxvalue:
            messagebox.showwarning(
                "Too large",
                "The allowed maximum value jest %s. "
                "Please try again." % self.maxvalue,
                parent = self
            )
            zwróć 0

        self.result = result

        zwróć 1


klasa _QueryInteger(_QueryDialog):
    errormessage = "Not an integer."
    def getresult(self):
        zwróć self.getint(self.entry.get())

def askinteger(title, prompt, **kw):
    '''get an integer z the user

    Arguments:

        title -- the dialog title
        prompt -- the label text
        **kw -- see SimpleDialog class

    Return value jest an integer
    '''
    d = _QueryInteger(title, prompt, **kw)
    zwróć d.result

klasa _QueryFloat(_QueryDialog):
    errormessage = "Not a floating point value."
    def getresult(self):
        zwróć self.getdouble(self.entry.get())

def askfloat(title, prompt, **kw):
    '''get a float z the user

    Arguments:

        title -- the dialog title
        prompt -- the label text
        **kw -- see SimpleDialog class

    Return value jest a float
    '''
    d = _QueryFloat(title, prompt, **kw)
    zwróć d.result

klasa _QueryString(_QueryDialog):
    def __init__(self, *args, **kw):
        jeżeli "show" w kw:
            self.__show = kw["show"]
            usuń kw["show"]
        inaczej:
            self.__show = Nic
        _QueryDialog.__init__(self, *args, **kw)

    def body(self, master):
        entry = _QueryDialog.body(self, master)
        jeżeli self.__show jest nie Nic:
            entry.configure(show=self.__show)
        zwróć entry

    def getresult(self):
        zwróć self.entry.get()

def askstring(title, prompt, **kw):
    '''get a string z the user

    Arguments:

        title -- the dialog title
        prompt -- the label text
        **kw -- see SimpleDialog class

    Return value jest a string
    '''
    d = _QueryString(title, prompt, **kw)
    zwróć d.result



jeżeli __name__ == '__main__':

    def test():
        root = Tk()
        def doit(root=root):
            d = SimpleDialog(root,
                         text="This jest a test dialog.  "
                              "Would this have been an actual dialog, "
                              "the buttons below would have been glowing "
                              "in soft pink light.\n"
                              "Do you believe this?",
                         buttons=["Yes", "No", "Cancel"],
                         default=0,
                         cancel=2,
                         title="Test Dialog")
            print(d.go())
            print(askinteger("Spam", "Egg count", initialvalue=12*12))
            print(askfloat("Spam", "Egg weight\n(in tons)", minvalue=1,
                           maxvalue=100))
            print(askstring("Spam", "Egg label"))
        t = Button(root, text='Test', command=doit)
        t.pack()
        q = Button(root, text='Quit', command=t.quit)
        q.pack()
        t.mainloop()

    test()
