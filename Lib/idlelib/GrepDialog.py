zaimportuj os
zaimportuj fnmatch
zaimportuj re  # dla htest
zaimportuj sys
z tkinter zaimportuj StringVar, BooleanVar, Checkbutton  # dla GrepDialog
z tkinter zaimportuj Tk, Text, Button, SEL, END  # dla htest
z idlelib zaimportuj SearchEngine
z idlelib.SearchDialogBase zaimportuj SearchDialogBase
# Importing OutputWindow fails due to zaimportuj loop
# EditorWindow -> GrepDialop -> OutputWindow -> EditorWindow

def grep(text, io=Nic, flist=Nic):
    root = text._root()
    engine = SearchEngine.get(root)
    jeżeli nie hasattr(engine, "_grepdialog"):
        engine._grepdialog = GrepDialog(root, engine, flist)
    dialog = engine._grepdialog
    searchphrase = text.get("sel.first", "sel.last")
    dialog.open(text, searchphrase, io)

klasa GrepDialog(SearchDialogBase):

    title = "Find w Files Dialog"
    icon = "Grep"
    needwrapbutton = 0

    def __init__(self, root, engine, flist):
        SearchDialogBase.__init__(self, root, engine)
        self.flist = flist
        self.globvar = StringVar(root)
        self.recvar = BooleanVar(root)

    def open(self, text, searchphrase, io=Nic):
        SearchDialogBase.open(self, text, searchphrase)
        jeżeli io:
            path = io.filename albo ""
        inaczej:
            path = ""
        dir, base = os.path.split(path)
        head, tail = os.path.splitext(base)
        jeżeli nie tail:
            tail = ".py"
        self.globvar.set(os.path.join(dir, "*" + tail))

    def create_entries(self):
        SearchDialogBase.create_entries(self)
        self.globent = self.make_entry("In files:", self.globvar)[0]

    def create_other_buttons(self):
        f = self.make_frame()[0]

        btn = Checkbutton(f, anchor="w",
                variable=self.recvar,
                text="Recurse down subdirectories")
        btn.pack(side="top", fill="both")
        btn.select()

    def create_command_buttons(self):
        SearchDialogBase.create_command_buttons(self)
        self.make_button("Search Files", self.default_command, 1)

    def default_command(self, event=Nic):
        prog = self.engine.getprog()
        jeżeli nie prog:
            zwróć
        path = self.globvar.get()
        jeżeli nie path:
            self.top.bell()
            zwróć
        z idlelib.OutputWindow zaimportuj OutputWindow  # leave here!
        save = sys.stdout
        spróbuj:
            sys.stdout = OutputWindow(self.flist)
            self.grep_it(prog, path)
        w_końcu:
            sys.stdout = save

    def grep_it(self, prog, path):
        dir, base = os.path.split(path)
        list = self.findfiles(dir, base, self.recvar.get())
        list.sort()
        self.close()
        pat = self.engine.getpat()
        print("Searching %r w %s ..." % (pat, path))
        hits = 0
        spróbuj:
            dla fn w list:
                spróbuj:
                    przy open(fn, errors='replace') jako f:
                        dla lineno, line w enumerate(f, 1):
                            jeżeli line[-1:] == '\n':
                                line = line[:-1]
                            jeżeli prog.search(line):
                                sys.stdout.write("%s: %s: %s\n" %
                                                 (fn, lineno, line))
                                hits += 1
                wyjąwszy OSError jako msg:
                    print(msg)
            print(("Hits found: %s\n"
                  "(Hint: right-click to open locations.)"
                  % hits) jeżeli hits inaczej "No hits.")
        wyjąwszy AttributeError:
            # Tk window has been closed, OutputWindow.text = Nic,
            # so w OW.write, OW.text.insert fails.
            dalej

    def findfiles(self, dir, base, rec):
        spróbuj:
            names = os.listdir(dir albo os.curdir)
        wyjąwszy OSError jako msg:
            print(msg)
            zwróć []
        list = []
        subdirs = []
        dla name w names:
            fn = os.path.join(dir, name)
            jeżeli os.path.isdir(fn):
                subdirs.append(fn)
            inaczej:
                jeżeli fnmatch.fnmatch(name, base):
                    list.append(fn)
        jeżeli rec:
            dla subdir w subdirs:
                list.extend(self.findfiles(subdir, base, rec))
        zwróć list

    def close(self, event=Nic):
        jeżeli self.top:
            self.top.grab_release()
            self.top.withdraw()


def _grep_dialog(parent):  # htest #
    z idlelib.PyShell zaimportuj PyShellFileList
    root = Tk()
    root.title("Test GrepDialog")
    width, height, x, y = list(map(int, re.split('[x+]', parent.geometry())))
    root.geometry("+%d+%d"%(x, y + 150))

    flist = PyShellFileList(root)
    text = Text(root, height=5)
    text.pack()

    def show_grep_dialog():
        text.tag_add(SEL, "1.0", END)
        grep(text, flist=flist)
        text.tag_remove(SEL, "1.0", END)

    button = Button(root, text="Show GrepDialog", command=show_grep_dialog)
    button.pack()
    root.mainloop()

jeżeli __name__ == "__main__":
    zaimportuj unittest
    unittest.main('idlelib.idle_test.test_grep', verbosity=2, exit=Nieprawda)

    z idlelib.idle_test.htest zaimportuj run
    run(_grep_dialog)
