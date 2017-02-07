"Dialog to specify albo edit the parameters dla a user configured help source."

zaimportuj os
zaimportuj sys

z tkinter zaimportuj *
zaimportuj tkinter.messagebox jako tkMessageBox
zaimportuj tkinter.filedialog jako tkFileDialog

klasa GetHelpSourceDialog(Toplevel):
    def __init__(self, parent, title, menuItem='', filePath='', _htest=Nieprawda):
        """Get menu entry oraz url/ local file location dla Additional Help

        User selects a name dla the Help resource oraz provides a web url
        albo a local file jako its source.  The user can enter a url albo browse
        dla the file.

        _htest - bool, change box location when running htest
        """
        Toplevel.__init__(self, parent)
        self.configure(borderwidth=5)
        self.resizable(height=FALSE, width=FALSE)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.Cancel)
        self.parent = parent
        self.result = Nic
        self.CreateWidgets()
        self.menu.set(menuItem)
        self.path.set(filePath)
        self.withdraw() #hide dopóki setting geometry
        #needs to be done here so that the winfo_reqwidth jest valid
        self.update_idletasks()
        #centre dialog over parent. below parent jeżeli running htest.
        self.geometry(
                "+%d+%d" % (
                    parent.winfo_rootx() +
                    (parent.winfo_width()/2 - self.winfo_reqwidth()/2),
                    parent.winfo_rooty() +
                    ((parent.winfo_height()/2 - self.winfo_reqheight()/2)
                    jeżeli nie _htest inaczej 150)))
        self.deiconify() #geometry set, unhide
        self.bind('<Return>', self.Ok)
        self.wait_window()

    def CreateWidgets(self):
        self.menu = StringVar(self)
        self.path = StringVar(self)
        self.fontSize = StringVar(self)
        self.frameMain = Frame(self, borderwidth=2, relief=GROOVE)
        self.frameMain.pack(side=TOP, expand=TRUE, fill=BOTH)
        labelMenu = Label(self.frameMain, anchor=W, justify=LEFT,
                          text='Menu Item:')
        self.entryMenu = Entry(self.frameMain, textvariable=self.menu,
                               width=30)
        self.entryMenu.focus_set()
        labelPath = Label(self.frameMain, anchor=W, justify=LEFT,
                          text='Help File Path: Enter URL albo browse dla file')
        self.entryPath = Entry(self.frameMain, textvariable=self.path,
                               width=40)
        self.entryMenu.focus_set()
        labelMenu.pack(anchor=W, padx=5, pady=3)
        self.entryMenu.pack(anchor=W, padx=5, pady=3)
        labelPath.pack(anchor=W, padx=5, pady=3)
        self.entryPath.pack(anchor=W, padx=5, pady=3)
        browseButton = Button(self.frameMain, text='Browse', width=8,
                              command=self.browseFile)
        browseButton.pack(pady=3)
        frameButtons = Frame(self)
        frameButtons.pack(side=BOTTOM, fill=X)
        self.buttonOk = Button(frameButtons, text='OK',
                               width=8, default=ACTIVE,  command=self.Ok)
        self.buttonOk.grid(row=0, column=0, padx=5,pady=5)
        self.buttonCancel = Button(frameButtons, text='Cancel',
                                   width=8, command=self.Cancel)
        self.buttonCancel.grid(row=0, column=1, padx=5, pady=5)

    def browseFile(self):
        filetypes = [
            ("HTML Files", "*.htm *.html", "TEXT"),
            ("PDF Files", "*.pdf", "TEXT"),
            ("Windows Help Files", "*.chm"),
            ("Text Files", "*.txt", "TEXT"),
            ("All Files", "*")]
        path = self.path.get()
        jeżeli path:
            dir, base = os.path.split(path)
        inaczej:
            base = Nic
            jeżeli sys.platform[:3] == 'win':
                dir = os.path.join(os.path.dirname(sys.executable), 'Doc')
                jeżeli nie os.path.isdir(dir):
                    dir = os.getcwd()
            inaczej:
                dir = os.getcwd()
        opendialog = tkFileDialog.Open(parent=self, filetypes=filetypes)
        file = opendialog.show(initialdir=dir, initialfile=base)
        jeżeli file:
            self.path.set(file)

    def MenuOk(self):
        "Simple validity check dla a sensible menu item name"
        menuOk = Prawda
        menu = self.menu.get()
        menu.strip()
        jeżeli nie menu:
            tkMessageBox.showerror(title='Menu Item Error',
                                   message='No menu item specified',
                                   parent=self)
            self.entryMenu.focus_set()
            menuOk = Nieprawda
        albo_inaczej len(menu) > 30:
            tkMessageBox.showerror(title='Menu Item Error',
                                   message='Menu item too long:'
                                           '\nLimit 30 characters.',
                                   parent=self)
            self.entryMenu.focus_set()
            menuOk = Nieprawda
        zwróć menuOk

    def PathOk(self):
        "Simple validity check dla menu file path"
        pathOk = Prawda
        path = self.path.get()
        path.strip()
        jeżeli nie path: #no path specified
            tkMessageBox.showerror(title='File Path Error',
                                   message='No help file path specified.',
                                   parent=self)
            self.entryPath.focus_set()
            pathOk = Nieprawda
        albo_inaczej path.startswith(('www.', 'http')):
            dalej
        inaczej:
            jeżeli path[:5] == 'file:':
                path = path[5:]
            jeżeli nie os.path.exists(path):
                tkMessageBox.showerror(title='File Path Error',
                                       message='Help file path does nie exist.',
                                       parent=self)
                self.entryPath.focus_set()
                pathOk = Nieprawda
        zwróć pathOk

    def Ok(self, event=Nic):
        jeżeli self.MenuOk() oraz self.PathOk():
            self.result = (self.menu.get().strip(),
                           self.path.get().strip())
            jeżeli sys.platform == 'darwin':
                path = self.result[1]
                jeżeli path.startswith(('www', 'file:', 'http:')):
                    dalej
                inaczej:
                    # Mac Safari insists on using the URI form dla local files
                    self.result = list(self.result)
                    self.result[1] = "file://" + path
            self.destroy()

    def Cancel(self, event=Nic):
        self.result = Nic
        self.destroy()

jeżeli __name__ == '__main__':
    z idlelib.idle_test.htest zaimportuj run
    run(GetHelpSourceDialog)
