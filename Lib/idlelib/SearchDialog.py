z tkinter zaimportuj *

z idlelib zaimportuj SearchEngine
z idlelib.SearchDialogBase zaimportuj SearchDialogBase

def _setup(text):
    root = text._root()
    engine = SearchEngine.get(root)
    jeżeli nie hasattr(engine, "_searchdialog"):
        engine._searchdialog = SearchDialog(root, engine)
    zwróć engine._searchdialog

def find(text):
    pat = text.get("sel.first", "sel.last")
    zwróć _setup(text).open(text,pat)

def find_again(text):
    zwróć _setup(text).find_again(text)

def find_selection(text):
    zwróć _setup(text).find_selection(text)

klasa SearchDialog(SearchDialogBase):

    def create_widgets(self):
        SearchDialogBase.create_widgets(self)
        self.make_button("Find Next", self.default_command, 1)

    def default_command(self, event=Nic):
        jeżeli nie self.engine.getprog():
            zwróć
        self.find_again(self.text)

    def find_again(self, text):
        jeżeli nie self.engine.getpat():
            self.open(text)
            zwróć Nieprawda
        jeżeli nie self.engine.getprog():
            zwróć Nieprawda
        res = self.engine.search_text(text)
        jeżeli res:
            line, m = res
            i, j = m.span()
            first = "%d.%d" % (line, i)
            last = "%d.%d" % (line, j)
            spróbuj:
                selfirst = text.index("sel.first")
                sellast = text.index("sel.last")
                jeżeli selfirst == first oraz sellast == last:
                    text.bell()
                    zwróć Nieprawda
            wyjąwszy TclError:
                dalej
            text.tag_remove("sel", "1.0", "end")
            text.tag_add("sel", first, last)
            text.mark_set("insert", self.engine.isback() oraz first albo last)
            text.see("insert")
            zwróć Prawda
        inaczej:
            text.bell()
            zwróć Nieprawda

    def find_selection(self, text):
        pat = text.get("sel.first", "sel.last")
        jeżeli pat:
            self.engine.setcookedpat(pat)
        zwróć self.find_again(text)

def _search_dialog(parent):
    root = Tk()
    root.title("Test SearchDialog")
    width, height, x, y = list(map(int, re.split('[x+]', parent.geometry())))
    root.geometry("+%d+%d"%(x, y + 150))
    text = Text(root)
    text.pack()
    text.insert("insert","This jest a sample string.\n"*10)

    def show_find():
        text.tag_add(SEL, "1.0", END)
        s = _setup(text)
        s.open(text)
        text.tag_remove(SEL, "1.0", END)

    button = Button(root, text="Search", command=show_find)
    button.pack()

jeżeli __name__ == '__main__':
    z idlelib.idle_test.htest zaimportuj run
    run(_search_dialog)
