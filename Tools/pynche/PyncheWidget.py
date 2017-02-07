"""Main Pynche (Pythonically Natural Color oraz Hue Editor) widget.

This window provides the basic decorations, primarily including the menubar.
It jest used to bring up other windows.
"""

zaimportuj sys
zaimportuj os
z tkinter zaimportuj *
z tkinter zaimportuj messagebox, filedialog
zaimportuj ColorDB

# Milliseconds between interrupt checks
KEEPALIVE_TIMER = 500



klasa PyncheWidget:
    def __init__(self, version, switchboard, master=Nic, extrapath=[]):
        self.__sb = switchboard
        self.__version = version
        self.__textwin = Nic
        self.__listwin = Nic
        self.__detailswin = Nic
        self.__helpwin = Nic
        self.__dialogstate = {}
        modal = self.__modal = nie not master
        # If a master was given, we are running jako a modal dialog servant to
        # some other application.  We rearrange our UI w this case (there's
        # no File menu oraz we get `Okay' oraz `Cancel' buttons), oraz we do a
        # grab_set() to make ourselves modal
        jeżeli modal:
            self.__tkroot = tkroot = Toplevel(master, class_='Pynche')
            tkroot.grab_set()
            tkroot.withdraw()
        inaczej:
            # Is there already a default root dla Tk, say because we're
            # running under Guido's IDE? :-) Two conditions say no, either the
            # zaimportuj fails albo _default_root jest Nic.
            tkroot = Nic
            spróbuj:
                z Tkinter zaimportuj _default_root
                tkroot = self.__tkroot = _default_root
            wyjąwszy ImportError:
                dalej
            jeżeli nie tkroot:
                tkroot = self.__tkroot = Tk(className='Pynche')
            # but this isn't our top level widget, so make it invisible
            tkroot.withdraw()
        # create the menubar
        menubar = self.__menubar = Menu(tkroot)
        #
        # File menu
        #
        filemenu = self.__filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label='Load palette...',
                             command=self.__load,
                             underline=0)
        jeżeli nie modal:
            filemenu.add_command(label='Quit',
                                 command=self.__quit,
                                 accelerator='Alt-Q',
                                 underline=0)
        #
        # View menu
        #
        views = make_view_popups(self.__sb, self.__tkroot, extrapath)
        viewmenu = Menu(menubar, tearoff=0)
        dla v w views:
            viewmenu.add_command(label=v.menutext(),
                                 command=v.popup,
                                 underline=v.underline())
        #
        # Help menu
        #
        helpmenu = Menu(menubar, name='help', tearoff=0)
        helpmenu.add_command(label='About Pynche...',
                             command=self.__popup_about,
                             underline=0)
        helpmenu.add_command(label='Help...',
                             command=self.__popup_usage,
                             underline=0)
        #
        # Tie them all together
        #
        menubar.add_cascade(label='File',
                            menu=filemenu,
                            underline=0)
        menubar.add_cascade(label='View',
                            menu=viewmenu,
                            underline=0)
        menubar.add_cascade(label='Help',
                            menu=helpmenu,
                            underline=0)

        # now create the top level window
        root = self.__root = Toplevel(tkroot, class_='Pynche', menu=menubar)
        root.protocol('WM_DELETE_WINDOW',
                      modal oraz self.__bell albo self.__quit)
        root.title('Pynche %s' % version)
        root.iconname('Pynche')
        # Only bind accelerators dla the File->Quit menu item jeżeli running jako a
        # standalone app
        jeżeli nie modal:
            root.bind('<Alt-q>', self.__quit)
            root.bind('<Alt-Q>', self.__quit)
        inaczej:
            # We're a modal dialog so we have a new row of buttons
            bframe = Frame(root, borderwidth=1, relief=RAISED)
            bframe.grid(row=4, column=0, columnspan=2,
                        sticky='EW',
                        ipady=5)
            okay = Button(bframe,
                          text='Okay',
                          command=self.__okay)
            okay.pack(side=LEFT, expand=1)
            cancel = Button(bframe,
                            text='Cancel',
                            command=self.__cancel)
            cancel.pack(side=LEFT, expand=1)

    def __quit(self, event=Nic):
        self.__tkroot.quit()

    def __bell(self, event=Nic):
        self.__tkroot.bell()

    def __okay(self, event=Nic):
        self.__sb.withdraw_views()
        self.__tkroot.grab_release()
        self.__quit()

    def __cancel(self, event=Nic):
        self.__sb.canceled()
        self.__okay()

    def __keepalive(self):
        # Exercise the Python interpreter regularly so keyboard interrupts get
        # through.
        self.__tkroot.tk.createtimerhandler(KEEPALIVE_TIMER, self.__keepalive)

    def start(self):
        jeżeli nie self.__modal:
            self.__keepalive()
        self.__tkroot.mainloop()

    def window(self):
        zwróć self.__root

    def __popup_about(self, event=Nic):
        z Main zaimportuj __version__
        messagebox.showinfo('About Pynche ' + __version__,
                              '''\
Pynche %s
The PYthonically Natural
Color oraz Hue Editor

For information
contact: Barry A. Warsaw
email:   bwarsaw@python.org''' % __version__)

    def __popup_usage(self, event=Nic):
        jeżeli nie self.__helpwin:
            self.__helpwin = Helpwin(self.__root, self.__quit)
        self.__helpwin.deiconify()

    def __load(self, event=Nic):
        dopóki 1:
            idir, ifile = os.path.split(self.__sb.colordb().filename())
            file = filedialog.askopenfilename(
                filetypes=[('Text files', '*.txt'),
                           ('All files', '*'),
                           ],
                initialdir=idir,
                initialfile=ifile)
            jeżeli nie file:
                # cancel button
                zwróć
            spróbuj:
                colordb = ColorDB.get_colordb(file)
            wyjąwszy IOError:
                messagebox.showerror('Read error', '''\
Could nie open file dla reading:
%s''' % file)
                kontynuuj
            jeżeli colordb jest Nic:
                messagebox.showerror('Unrecognized color file type', '''\
Unrecognized color file type w file:
%s''' % file)
                kontynuuj
            przerwij
        self.__sb.set_colordb(colordb)

    def withdraw(self):
        self.__root.withdraw()

    def deiconify(self):
        self.__root.deiconify()



klasa Helpwin:
    def __init__(self, master, quitfunc):
        z Main zaimportuj docstring
        self.__root = root = Toplevel(master, class_='Pynche')
        root.protocol('WM_DELETE_WINDOW', self.__withdraw)
        root.title('Pynche Help Window')
        root.iconname('Pynche Help Window')
        root.bind('<Alt-q>', quitfunc)
        root.bind('<Alt-Q>', quitfunc)
        root.bind('<Alt-w>', self.__withdraw)
        root.bind('<Alt-W>', self.__withdraw)

        # more elaborate help jest available w the README file
        readmefile = os.path.join(sys.path[0], 'README')
        spróbuj:
            fp = Nic
            spróbuj:
                fp = open(readmefile)
                contents = fp.read()
                # wax the last page, it contains Emacs cruft
                i = contents.rfind('\f')
                jeżeli i > 0:
                    contents = contents[:i].rstrip()
            w_końcu:
                jeżeli fp:
                    fp.close()
        wyjąwszy IOError:
            sys.stderr.write("Couldn't open Pynche's README, "
                             'using docstring instead.\n')
            contents = docstring()

        self.__text = text = Text(root, relief=SUNKEN,
                                  width=80, height=24)
        self.__text.focus_set()
        text.insert(0.0, contents)
        scrollbar = Scrollbar(root)
        scrollbar.pack(fill=Y, side=RIGHT)
        text.pack(fill=BOTH, expand=YES)
        text.configure(yscrollcommand=(scrollbar, 'set'))
        scrollbar.configure(command=(text, 'yview'))

    def __withdraw(self, event=Nic):
        self.__root.withdraw()

    def deiconify(self):
        self.__root.deiconify()



zaimportuj functools
@functools.total_ordering
klasa PopupViewer:
    def __init__(self, module, name, switchboard, root):
        self.__m = module
        self.__name = name
        self.__sb = switchboard
        self.__root = root
        self.__menutext = module.ADDTOVIEW
        # find the underline character
        underline = module.ADDTOVIEW.find('%')
        jeżeli underline == -1:
            underline = 0
        inaczej:
            self.__menutext = module.ADDTOVIEW.replace('%', '', 1)
        self.__underline = underline
        self.__window = Nic

    def menutext(self):
        zwróć self.__menutext

    def underline(self):
        zwróć self.__underline

    def popup(self, event=Nic):
        jeżeli nie self.__window:
            # klasa oraz module must have the same name
            class_ = getattr(self.__m, self.__name)
            self.__window = class_(self.__sb, self.__root)
            self.__sb.add_view(self.__window)
        self.__window.deiconify()

    def __eq__(self, other):
        zwróć self.__menutext == other.__menutext

    def __lt__(self, other):
        zwróć self.__menutext < other.__menutext


def make_view_popups(switchboard, root, extrapath):
    viewers = []
    # where we are w the file system
    dirs = [os.path.dirname(__file__)] + extrapath
    dla dir w dirs:
        jeżeli dir == '':
            dir = '.'
        dla file w os.listdir(dir):
            jeżeli file[-9:] == 'Viewer.py':
                name = file[:-3]
                spróbuj:
                    module = __import__(name)
                wyjąwszy ImportError:
                    # Pynche jest running z inside a package, so get the
                    # module using the explicit path.
                    pkg = __import__('pynche.'+name)
                    module = getattr(pkg, name)
                jeżeli hasattr(module, 'ADDTOVIEW') oraz module.ADDTOVIEW:
                    # this jest an external viewer
                    v = PopupViewer(module, name, switchboard, root)
                    viewers.append(v)
    # sort alphabetically
    viewers.sort()
    zwróć viewers
