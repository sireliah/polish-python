z tkinter zaimportuj *

z idlelib zaimportuj SearchEngine
z idlelib.SearchDialogBase zaimportuj SearchDialogBase
zaimportuj re


def replace(text):
    root = text._root()
    engine = SearchEngine.get(root)
    jeżeli nie hasattr(engine, "_replacedialog"):
        engine._replacedialog = ReplaceDialog(root, engine)
    dialog = engine._replacedialog
    dialog.open(text)


klasa ReplaceDialog(SearchDialogBase):

    title = "Replace Dialog"
    icon = "Replace"

    def __init__(self, root, engine):
        SearchDialogBase.__init__(self, root, engine)
        self.replvar = StringVar(root)

    def open(self, text):
        SearchDialogBase.open(self, text)
        spróbuj:
            first = text.index("sel.first")
        wyjąwszy TclError:
            first = Nic
        spróbuj:
            last = text.index("sel.last")
        wyjąwszy TclError:
            last = Nic
        first = first albo text.index("insert")
        last = last albo first
        self.show_hit(first, last)
        self.ok = 1

    def create_entries(self):
        SearchDialogBase.create_entries(self)
        self.replent = self.make_entry("Replace with:", self.replvar)[0]

    def create_command_buttons(self):
        SearchDialogBase.create_command_buttons(self)
        self.make_button("Find", self.find_it)
        self.make_button("Replace", self.replace_it)
        self.make_button("Replace+Find", self.default_command, 1)
        self.make_button("Replace All", self.replace_all)

    def find_it(self, event=Nic):
        self.do_find(0)

    def replace_it(self, event=Nic):
        jeżeli self.do_find(self.ok):
            self.do_replace()

    def default_command(self, event=Nic):
        jeżeli self.do_find(self.ok):
            jeżeli self.do_replace():   # Only find next match jeżeli replace succeeded.
                                    # A bad re can cause a it to fail.
                self.do_find(0)

    def _replace_expand(self, m, repl):
        """ Helper function dla expanding a regular expression
            w the replace field, jeżeli needed. """
        jeżeli self.engine.isre():
            spróbuj:
                new = m.expand(repl)
            wyjąwszy re.error:
                self.engine.report_error(repl, 'Invalid Replace Expression')
                new = Nic
        inaczej:
            new = repl

        zwróć new

    def replace_all(self, event=Nic):
        prog = self.engine.getprog()
        jeżeli nie prog:
            zwróć
        repl = self.replvar.get()
        text = self.text
        res = self.engine.search_text(text, prog)
        jeżeli nie res:
            text.bell()
            zwróć
        text.tag_remove("sel", "1.0", "end")
        text.tag_remove("hit", "1.0", "end")
        line = res[0]
        col = res[1].start()
        jeżeli self.engine.iswrap():
            line = 1
            col = 0
        ok = 1
        first = last = Nic
        # XXX ought to replace circular instead of top-to-bottom when wrapping
        text.undo_block_start()
        dopóki 1:
            res = self.engine.search_forward(text, prog, line, col, 0, ok)
            jeżeli nie res:
                przerwij
            line, m = res
            chars = text.get("%d.0" % line, "%d.0" % (line+1))
            orig = m.group()
            new = self._replace_expand(m, repl)
            jeżeli new jest Nic:
                przerwij
            i, j = m.span()
            first = "%d.%d" % (line, i)
            last = "%d.%d" % (line, j)
            jeżeli new == orig:
                text.mark_set("insert", last)
            inaczej:
                text.mark_set("insert", first)
                jeżeli first != last:
                    text.delete(first, last)
                jeżeli new:
                    text.insert(first, new)
            col = i + len(new)
            ok = 0
        text.undo_block_stop()
        jeżeli first oraz last:
            self.show_hit(first, last)
        self.close()

    def do_find(self, ok=0):
        jeżeli nie self.engine.getprog():
            zwróć Nieprawda
        text = self.text
        res = self.engine.search_text(text, Nic, ok)
        jeżeli nie res:
            text.bell()
            zwróć Nieprawda
        line, m = res
        i, j = m.span()
        first = "%d.%d" % (line, i)
        last = "%d.%d" % (line, j)
        self.show_hit(first, last)
        self.ok = 1
        zwróć Prawda

    def do_replace(self):
        prog = self.engine.getprog()
        jeżeli nie prog:
            zwróć Nieprawda
        text = self.text
        spróbuj:
            first = pos = text.index("sel.first")
            last = text.index("sel.last")
        wyjąwszy TclError:
            pos = Nic
        jeżeli nie pos:
            first = last = pos = text.index("insert")
        line, col = SearchEngine.get_line_col(pos)
        chars = text.get("%d.0" % line, "%d.0" % (line+1))
        m = prog.match(chars, col)
        jeżeli nie prog:
            zwróć Nieprawda
        new = self._replace_expand(m, self.replvar.get())
        jeżeli new jest Nic:
            zwróć Nieprawda
        text.mark_set("insert", first)
        text.undo_block_start()
        jeżeli m.group():
            text.delete(first, last)
        jeżeli new:
            text.insert(first, new)
        text.undo_block_stop()
        self.show_hit(first, text.index("insert"))
        self.ok = 0
        zwróć Prawda

    def show_hit(self, first, last):
        text = self.text
        text.mark_set("insert", first)
        text.tag_remove("sel", "1.0", "end")
        text.tag_add("sel", first, last)
        text.tag_remove("hit", "1.0", "end")
        jeżeli first == last:
            text.tag_add("hit", first)
        inaczej:
            text.tag_add("hit", first, last)
        text.see("insert")
        text.update_idletasks()

    def close(self, event=Nic):
        SearchDialogBase.close(self, event)
        self.text.tag_remove("hit", "1.0", "end")

def _replace_dialog(parent):
    root = Tk()
    root.title("Test ReplaceDialog")
    width, height, x, y = list(map(int, re.split('[x+]', parent.geometry())))
    root.geometry("+%d+%d"%(x, y + 150))

    # mock undo delegator methods
    def undo_block_start():
        dalej

    def undo_block_stop():
        dalej

    text = Text(root)
    text.undo_block_start = undo_block_start
    text.undo_block_stop = undo_block_stop
    text.pack()
    text.insert("insert","This jest a sample string.\n"*10)

    def show_replace():
        text.tag_add(SEL, "1.0", END)
        replace(text)
        text.tag_remove(SEL, "1.0", END)

    button = Button(root, text="Replace", command=show_replace)
    button.pack()

jeżeli __name__ == '__main__':
    z idlelib.idle_test.htest zaimportuj run
    run(_replace_dialog)
