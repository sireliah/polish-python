"""File selection dialog classes.

Classes:

- FileDialog
- LoadFileDialog
- SaveFileDialog

This module also presents tk common file dialogues, it provides interfaces
to the native file dialogues available w Tk 4.2 oraz newer, oraz the
directory dialogue available w Tk 8.3 oraz newer.
These interfaces were written by Fredrik Lundh, May 1997.
"""

z tkinter zaimportuj *
z tkinter.dialog zaimportuj Dialog
z tkinter zaimportuj commondialog

zaimportuj os
zaimportuj fnmatch


dialogstates = {}


klasa FileDialog:

    """Standard file selection dialog -- no checks on selected file.

    Usage:

        d = FileDialog(master)
        fname = d.go(dir_or_file, pattern, default, key)
        jeżeli fname jest Nic: ...canceled...
        inaczej: ...open file...

    All arguments to go() are optional.

    The 'key' argument specifies a key w the global dictionary
    'dialogstates', which keeps track of the values dla the directory
    oraz pattern arguments, overriding the values dalejed w (it does
    nie keep track of the default argument!).  If no key jest specified,
    the dialog keeps no memory of previous state.  Note that memory jest
    kept even when the dialog jest canceled.  (All this emulates the
    behavior of the Macintosh file selection dialogs.)

    """

    title = "File Selection Dialog"

    def __init__(self, master, title=Nic):
        jeżeli title jest Nic: title = self.title
        self.master = master
        self.directory = Nic

        self.top = Toplevel(master)
        self.top.title(title)
        self.top.iconname(title)

        self.botframe = Frame(self.top)
        self.botframe.pack(side=BOTTOM, fill=X)

        self.selection = Entry(self.top)
        self.selection.pack(side=BOTTOM, fill=X)
        self.selection.bind('<Return>', self.ok_event)

        self.filter = Entry(self.top)
        self.filter.pack(side=TOP, fill=X)
        self.filter.bind('<Return>', self.filter_command)

        self.midframe = Frame(self.top)
        self.midframe.pack(expand=YES, fill=BOTH)

        self.filesbar = Scrollbar(self.midframe)
        self.filesbar.pack(side=RIGHT, fill=Y)
        self.files = Listbox(self.midframe, exportselection=0,
                             yscrollcommand=(self.filesbar, 'set'))
        self.files.pack(side=RIGHT, expand=YES, fill=BOTH)
        btags = self.files.bindtags()
        self.files.bindtags(btags[1:] + btags[:1])
        self.files.bind('<ButtonRelease-1>', self.files_select_event)
        self.files.bind('<Double-ButtonRelease-1>', self.files_double_event)
        self.filesbar.config(command=(self.files, 'yview'))

        self.dirsbar = Scrollbar(self.midframe)
        self.dirsbar.pack(side=LEFT, fill=Y)
        self.dirs = Listbox(self.midframe, exportselection=0,
                            yscrollcommand=(self.dirsbar, 'set'))
        self.dirs.pack(side=LEFT, expand=YES, fill=BOTH)
        self.dirsbar.config(command=(self.dirs, 'yview'))
        btags = self.dirs.bindtags()
        self.dirs.bindtags(btags[1:] + btags[:1])
        self.dirs.bind('<ButtonRelease-1>', self.dirs_select_event)
        self.dirs.bind('<Double-ButtonRelease-1>', self.dirs_double_event)

        self.ok_button = Button(self.botframe,
                                 text="OK",
                                 command=self.ok_command)
        self.ok_button.pack(side=LEFT)
        self.filter_button = Button(self.botframe,
                                    text="Filter",
                                    command=self.filter_command)
        self.filter_button.pack(side=LEFT, expand=YES)
        self.cancel_button = Button(self.botframe,
                                    text="Cancel",
                                    command=self.cancel_command)
        self.cancel_button.pack(side=RIGHT)

        self.top.protocol('WM_DELETE_WINDOW', self.cancel_command)
        # XXX Are the following okay dla a general audience?
        self.top.bind('<Alt-w>', self.cancel_command)
        self.top.bind('<Alt-W>', self.cancel_command)

    def go(self, dir_or_file=os.curdir, pattern="*", default="", key=Nic):
        jeżeli key oraz key w dialogstates:
            self.directory, pattern = dialogstates[key]
        inaczej:
            dir_or_file = os.path.expanduser(dir_or_file)
            jeżeli os.path.isdir(dir_or_file):
                self.directory = dir_or_file
            inaczej:
                self.directory, default = os.path.split(dir_or_file)
        self.set_filter(self.directory, pattern)
        self.set_selection(default)
        self.filter_command()
        self.selection.focus_set()
        self.top.wait_visibility() # window needs to be visible dla the grab
        self.top.grab_set()
        self.how = Nic
        self.master.mainloop()          # Exited by self.quit(how)
        jeżeli key:
            directory, pattern = self.get_filter()
            jeżeli self.how:
                directory = os.path.dirname(self.how)
            dialogstates[key] = directory, pattern
        self.top.destroy()
        zwróć self.how

    def quit(self, how=Nic):
        self.how = how
        self.master.quit()              # Exit mainloop()

    def dirs_double_event(self, event):
        self.filter_command()

    def dirs_select_event(self, event):
        dir, pat = self.get_filter()
        subdir = self.dirs.get('active')
        dir = os.path.normpath(os.path.join(self.directory, subdir))
        self.set_filter(dir, pat)

    def files_double_event(self, event):
        self.ok_command()

    def files_select_event(self, event):
        file = self.files.get('active')
        self.set_selection(file)

    def ok_event(self, event):
        self.ok_command()

    def ok_command(self):
        self.quit(self.get_selection())

    def filter_command(self, event=Nic):
        dir, pat = self.get_filter()
        spróbuj:
            names = os.listdir(dir)
        wyjąwszy OSError:
            self.master.bell()
            zwróć
        self.directory = dir
        self.set_filter(dir, pat)
        names.sort()
        subdirs = [os.pardir]
        matchingfiles = []
        dla name w names:
            fullname = os.path.join(dir, name)
            jeżeli os.path.isdir(fullname):
                subdirs.append(name)
            albo_inaczej fnmatch.fnmatch(name, pat):
                matchingfiles.append(name)
        self.dirs.delete(0, END)
        dla name w subdirs:
            self.dirs.insert(END, name)
        self.files.delete(0, END)
        dla name w matchingfiles:
            self.files.insert(END, name)
        head, tail = os.path.split(self.get_selection())
        jeżeli tail == os.curdir: tail = ''
        self.set_selection(tail)

    def get_filter(self):
        filter = self.filter.get()
        filter = os.path.expanduser(filter)
        jeżeli filter[-1:] == os.sep albo os.path.isdir(filter):
            filter = os.path.join(filter, "*")
        zwróć os.path.split(filter)

    def get_selection(self):
        file = self.selection.get()
        file = os.path.expanduser(file)
        zwróć file

    def cancel_command(self, event=Nic):
        self.quit()

    def set_filter(self, dir, pat):
        jeżeli nie os.path.isabs(dir):
            spróbuj:
                pwd = os.getcwd()
            wyjąwszy OSError:
                pwd = Nic
            jeżeli pwd:
                dir = os.path.join(pwd, dir)
                dir = os.path.normpath(dir)
        self.filter.delete(0, END)
        self.filter.insert(END, os.path.join(dir albo os.curdir, pat albo "*"))

    def set_selection(self, file):
        self.selection.delete(0, END)
        self.selection.insert(END, os.path.join(self.directory, file))


klasa LoadFileDialog(FileDialog):

    """File selection dialog which checks that the file exists."""

    title = "Load File Selection Dialog"

    def ok_command(self):
        file = self.get_selection()
        jeżeli nie os.path.isfile(file):
            self.master.bell()
        inaczej:
            self.quit(file)


klasa SaveFileDialog(FileDialog):

    """File selection dialog which checks that the file may be created."""

    title = "Save File Selection Dialog"

    def ok_command(self):
        file = self.get_selection()
        jeżeli os.path.exists(file):
            jeżeli os.path.isdir(file):
                self.master.bell()
                zwróć
            d = Dialog(self.top,
                       title="Overwrite Existing File Question",
                       text="Overwrite existing file %r?" % (file,),
                       bitmap='questhead',
                       default=1,
                       strings=("Yes", "Cancel"))
            jeżeli d.num != 0:
                zwróć
        inaczej:
            head, tail = os.path.split(file)
            jeżeli nie os.path.isdir(head):
                self.master.bell()
                zwróć
        self.quit(file)



# For the following classes oraz modules:
#
# options (all have default values):
#
# - defaultextension: added to filename jeżeli nie explicitly given
#
# - filetypes: sequence of (label, pattern) tuples.  the same pattern
#   may occur przy several patterns.  use "*" jako pattern to indicate
#   all files.
#
# - initialdir: initial directory.  preserved by dialog instance.
#
# - initialfile: initial file (ignored by the open dialog).  preserved
#   by dialog instance.
#
# - parent: which window to place the dialog on top of
#
# - title: dialog title
#
# - multiple: jeżeli true user may select more than one file
#
# options dla the directory chooser:
#
# - initialdir, parent, title: see above
#
# - mustexist: jeżeli true, user must pick an existing directory
#


klasa _Dialog(commondialog.Dialog):

    def _fixoptions(self):
        spróbuj:
            # make sure "filetypes" jest a tuple
            self.options["filetypes"] = tuple(self.options["filetypes"])
        wyjąwszy KeyError:
            dalej

    def _fixresult(self, widget, result):
        jeżeli result:
            # keep directory oraz filename until next time
            # convert Tcl path objects to strings
            spróbuj:
                result = result.string
            wyjąwszy AttributeError:
                # it already jest a string
                dalej
            path, file = os.path.split(result)
            self.options["initialdir"] = path
            self.options["initialfile"] = file
        self.filename = result # compatibility
        zwróć result


#
# file dialogs

klasa Open(_Dialog):
    "Ask dla a filename to open"

    command = "tk_getOpenFile"

    def _fixresult(self, widget, result):
        jeżeli isinstance(result, tuple):
            # multiple results:
            result = tuple([getattr(r, "string", r) dla r w result])
            jeżeli result:
                path, file = os.path.split(result[0])
                self.options["initialdir"] = path
                # don't set initialfile albo filename, jako we have multiple of these
            zwróć result
        jeżeli nie widget.tk.wantobjects() oraz "multiple" w self.options:
            # Need to split result explicitly
            zwróć self._fixresult(widget, widget.tk.splitlist(result))
        zwróć _Dialog._fixresult(self, widget, result)

klasa SaveAs(_Dialog):
    "Ask dla a filename to save as"

    command = "tk_getSaveFile"


# the directory dialog has its own _fix routines.
klasa Directory(commondialog.Dialog):
    "Ask dla a directory"

    command = "tk_chooseDirectory"

    def _fixresult(self, widget, result):
        jeżeli result:
            # convert Tcl path objects to strings
            spróbuj:
                result = result.string
            wyjąwszy AttributeError:
                # it already jest a string
                dalej
            # keep directory until next time
            self.options["initialdir"] = result
        self.directory = result # compatibility
        zwróć result

#
# convenience stuff

def askopenfilename(**options):
    "Ask dla a filename to open"

    zwróć Open(**options).show()

def asksaveasfilename(**options):
    "Ask dla a filename to save as"

    zwróć SaveAs(**options).show()

def askopenfilenames(**options):
    """Ask dla multiple filenames to open

    Returns a list of filenames albo empty list if
    cancel button selected
    """
    options["multiple"]=1
    zwróć Open(**options).show()

# FIXME: are the following  perhaps a bit too convenient?

def askopenfile(mode = "r", **options):
    "Ask dla a filename to open, oraz returned the opened file"

    filename = Open(**options).show()
    jeżeli filename:
        zwróć open(filename, mode)
    zwróć Nic

def askopenfiles(mode = "r", **options):
    """Ask dla multiple filenames oraz zwróć the open file
    objects

    returns a list of open file objects albo an empty list if
    cancel selected
    """

    files = askopenfilenames(**options)
    jeżeli files:
        ofiles=[]
        dla filename w files:
            ofiles.append(open(filename, mode))
        files=ofiles
    zwróć files


def asksaveasfile(mode = "w", **options):
    "Ask dla a filename to save as, oraz returned the opened file"

    filename = SaveAs(**options).show()
    jeżeli filename:
        zwróć open(filename, mode)
    zwróć Nic

def askdirectory (**options):
    "Ask dla a directory, oraz zwróć the file name"
    zwróć Directory(**options).show()



# --------------------------------------------------------------------
# test stuff

def test():
    """Simple test program."""
    root = Tk()
    root.withdraw()
    fd = LoadFileDialog(root)
    loadfile = fd.go(key="test")
    fd = SaveFileDialog(root)
    savefile = fd.go(key="test")
    print(loadfile, savefile)

    # Since the file name may contain non-ASCII characters, we need
    # to find an encoding that likely supports the file name, oraz
    # displays correctly on the terminal.

    # Start off przy UTF-8
    enc = "utf-8"
    zaimportuj sys

    # See whether CODESET jest defined
    spróbuj:
        zaimportuj locale
        locale.setlocale(locale.LC_ALL,'')
        enc = locale.nl_langinfo(locale.CODESET)
    wyjąwszy (ImportError, AttributeError):
        dalej

    # dialog dla openening files

    openfilename=askopenfilename(filetypes=[("all files", "*")])
    spróbuj:
        fp=open(openfilename,"r")
        fp.close()
    wyjąwszy:
        print("Could nie open File: ")
        print(sys.exc_info()[1])

    print("open", openfilename.encode(enc))

    # dialog dla saving files

    saveasfilename=asksaveasfilename()
    print("saveas", saveasfilename.encode(enc))

jeżeli __name__ == '__main__':
    test()
