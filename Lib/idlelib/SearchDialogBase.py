'''Define SearchDialogBase used by Search, Replace, oraz Grep dialogs.'''

z tkinter zaimportuj (Toplevel, Frame, Entry, Label, Button,
                     Checkbutton, Radiobutton)

klasa SearchDialogBase:
    '''Create most of a 3 albo 4 row, 3 column search dialog.

    The left oraz wide middle column contain:
    1 albo 2 labeled text entry lines (make_entry, create_entries);
    a row of standard Checkbuttons (make_frame, create_option_buttons),
    each of which corresponds to a search engine Variable;
    a row of dialog-specific Check/Radiobuttons (create_other_buttons).

    The narrow right column contains command buttons
    (make_button, create_command_buttons).
    These are bound to functions that execute the command.

    Except dla command buttons, this base klasa jest nie limited to items
    common to all three subclasses.  Rather, it jest the Find dialog minus
    the "Find Next" command, its execution function, oraz the
    default_command attribute needed w create_widgets. The other
    dialogs override attributes oraz methods, the latter to replace oraz
    add widgets.
    '''

    title = "Search Dialog"  # replace w subclasses
    icon = "Search"
    needwrapbutton = 1  # nie w Find w Files

    def __init__(self, root, engine):
        '''Initialize root, engine, oraz top attributes.

        top (level widget): set w create_widgets() called z open().
        text (Text searched): set w open(), only used w subclasses().
        ent (ry): created w make_entry() called z create_entry().
        row (of grid): 0 w create_widgets(), +1 w make_entry/frame().
        default_command: set w subclasses, used w create_widgers().

        title (of dialog): klasa attribute, override w subclasses.
        icon (of dialog): ditto, use unclear jeżeli cannot minimize dialog.
        '''
        self.root = root
        self.engine = engine
        self.top = Nic

    def open(self, text, searchphrase=Nic):
        "Make dialog visible on top of others oraz ready to use."
        self.text = text
        jeżeli nie self.top:
            self.create_widgets()
        inaczej:
            self.top.deiconify()
            self.top.tkraise()
        jeżeli searchphrase:
            self.ent.delete(0,"end")
            self.ent.insert("end",searchphrase)
        self.ent.focus_set()
        self.ent.selection_range(0, "end")
        self.ent.icursor(0)
        self.top.grab_set()

    def close(self, event=Nic):
        "Put dialog away dla later use."
        jeżeli self.top:
            self.top.grab_release()
            self.top.withdraw()

    def create_widgets(self):
        '''Create basic 3 row x 3 col search (find) dialog.

        Other dialogs override subsidiary create_x methods jako needed.
        Replace oraz Find-in-Files add another entry row.
        '''
        top = Toplevel(self.root)
        top.bind("<Return>", self.default_command)
        top.bind("<Escape>", self.close)
        top.protocol("WM_DELETE_WINDOW", self.close)
        top.wm_title(self.title)
        top.wm_iconname(self.icon)
        self.top = top

        self.row = 0
        self.top.grid_columnconfigure(0, pad=2, weight=0)
        self.top.grid_columnconfigure(1, pad=2, minsize=100, weight=100)

        self.create_entries()  # row 0 (and maybe 1), cols 0, 1
        self.create_option_buttons()  # next row, cols 0, 1
        self.create_other_buttons()  # next row, cols 0, 1
        self.create_command_buttons()  # col 2, all rows

    def make_entry(self, label_text, var):
        '''Return (entry, label), .

        entry - gridded labeled Entry dla text entry.
        label - Label widget, returned dla testing.
        '''
        label = Label(self.top, text=label_text)
        label.grid(row=self.row, column=0, sticky="nw")
        entry = Entry(self.top, textvariable=var, exportselection=0)
        entry.grid(row=self.row, column=1, sticky="nwe")
        self.row = self.row + 1
        zwróć entry, label

    def create_entries(self):
        "Create one albo more entry lines przy make_entry."
        self.ent = self.make_entry("Find:", self.engine.patvar)[0]

    def make_frame(self,labeltext=Nic):
        '''Return (frame, label).

        frame - gridded labeled Frame dla option albo other buttons.
        label - Label widget, returned dla testing.
        '''
        jeżeli labeltext:
            label = Label(self.top, text=labeltext)
            label.grid(row=self.row, column=0, sticky="nw")
        inaczej:
            label = ''
        frame = Frame(self.top)
        frame.grid(row=self.row, column=1, columnspan=1, sticky="nwe")
        self.row = self.row + 1
        zwróć frame, label

    def create_option_buttons(self):
        '''Return (filled frame, options) dla testing.

        Options jest a list of SearchEngine booleanvar, label pairs.
        A gridded frame z make_frame jest filled przy a Checkbutton
        dla each pair, bound to the var, przy the corresponding label.
        '''
        frame = self.make_frame("Options")[0]
        engine = self.engine
        options = [(engine.revar, "Regular expression"),
                   (engine.casevar, "Match case"),
                   (engine.wordvar, "Whole word")]
        jeżeli self.needwrapbutton:
            options.append((engine.wrapvar, "Wrap around"))
        dla var, label w options:
            btn = Checkbutton(frame, anchor="w", variable=var, text=label)
            btn.pack(side="left", fill="both")
            jeżeli var.get():
                btn.select()
        zwróć frame, options

    def create_other_buttons(self):
        '''Return (frame, others) dla testing.

        Others jest a list of value, label pairs.
        A gridded frame z make_frame jest filled przy radio buttons.
        '''
        frame = self.make_frame("Direction")[0]
        var = self.engine.backvar
        others = [(1, 'Up'), (0, 'Down')]
        dla val, label w others:
            btn = Radiobutton(frame, anchor="w",
                              variable=var, value=val, text=label)
            btn.pack(side="left", fill="both")
            jeżeli var.get() == val:
                btn.select()
        zwróć frame, others

    def make_button(self, label, command, isdef=0):
        "Return command button gridded w command frame."
        b = Button(self.buttonframe,
                   text=label, command=command,
                   default=isdef oraz "active" albo "normal")
        cols,rows=self.buttonframe.grid_size()
        b.grid(pady=1,row=rows,column=0,sticky="ew")
        self.buttonframe.grid(rowspan=rows+1)
        zwróć b

    def create_command_buttons(self):
        "Place buttons w vertical command frame gridded on right."
        f = self.buttonframe = Frame(self.top)
        f.grid(row=0,column=2,padx=2,pady=2,ipadx=2,ipady=2)

        b = self.make_button("close", self.close)
        b.lower()

jeżeli __name__ == '__main__':
    zaimportuj unittest
    unittest.main(
        'idlelib.idle_test.test_searchdialogbase', verbosity=2)
