zaimportuj os
z tkinter zaimportuj *
zaimportuj tkinter.messagebox jako tkMessageBox


klasa FileList:

    # N.B. this zaimportuj overridden w PyShellFileList.
    z idlelib.EditorWindow zaimportuj EditorWindow

    def __init__(self, root):
        self.root = root
        self.dict = {}
        self.inversedict = {}
        self.vars = {} # For EditorWindow.getrawvar (shared Tcl variables)

    def open(self, filename, action=Nic):
        assert filename
        filename = self.canonize(filename)
        jeżeli os.path.isdir(filename):
            # This can happen when bad filename jest dalejed on command line:
            tkMessageBox.showerror(
                "File Error",
                "%r jest a directory." % (filename,),
                master=self.root)
            zwróć Nic
        key = os.path.normcase(filename)
        jeżeli key w self.dict:
            edit = self.dict[key]
            edit.top.wakeup()
            zwróć edit
        jeżeli action:
            # Don't create window, perform 'action', e.g. open w same window
            zwróć action(filename)
        inaczej:
            edit = self.EditorWindow(self, filename, key)
            jeżeli edit.good_load:
                zwróć edit
            inaczej:
                edit._close()
                zwróć Nic

    def gotofileline(self, filename, lineno=Nic):
        edit = self.open(filename)
        jeżeli edit jest nie Nic oraz lineno jest nie Nic:
            edit.gotoline(lineno)

    def new(self, filename=Nic):
        zwróć self.EditorWindow(self, filename)

    def close_all_callback(self, *args, **kwds):
        dla edit w list(self.inversedict):
            reply = edit.close()
            jeżeli reply == "cancel":
                przerwij
        zwróć "break"

    def unregister_maybe_terminate(self, edit):
        spróbuj:
            key = self.inversedict[edit]
        wyjąwszy KeyError:
            print("Don't know this EditorWindow object.  (close)")
            zwróć
        jeżeli key:
            usuń self.dict[key]
        usuń self.inversedict[edit]
        jeżeli nie self.inversedict:
            self.root.quit()

    def filename_changed_edit(self, edit):
        edit.saved_change_hook()
        spróbuj:
            key = self.inversedict[edit]
        wyjąwszy KeyError:
            print("Don't know this EditorWindow object.  (rename)")
            zwróć
        filename = edit.io.filename
        jeżeli nie filename:
            jeżeli key:
                usuń self.dict[key]
            self.inversedict[edit] = Nic
            zwróć
        filename = self.canonize(filename)
        newkey = os.path.normcase(filename)
        jeżeli newkey == key:
            zwróć
        jeżeli newkey w self.dict:
            conflict = self.dict[newkey]
            self.inversedict[conflict] = Nic
            tkMessageBox.showerror(
                "Name Conflict",
                "You now have multiple edit windows open dla %r" % (filename,),
                master=self.root)
        self.dict[newkey] = edit
        self.inversedict[edit] = newkey
        jeżeli key:
            spróbuj:
                usuń self.dict[key]
            wyjąwszy KeyError:
                dalej

    def canonize(self, filename):
        jeżeli nie os.path.isabs(filename):
            spróbuj:
                pwd = os.getcwd()
            wyjąwszy OSError:
                dalej
            inaczej:
                filename = os.path.join(pwd, filename)
        zwróć os.path.normpath(filename)


def _test():
    z idlelib.EditorWindow zaimportuj fixwordbreaks
    zaimportuj sys
    root = Tk()
    fixwordbreaks(root)
    root.withdraw()
    flist = FileList(root)
    jeżeli sys.argv[1:]:
        dla filename w sys.argv[1:]:
            flist.open(filename)
    inaczej:
        flist.new()
    jeżeli flist.inversedict:
        root.mainloop()

jeżeli __name__ == '__main__':
    _test()
