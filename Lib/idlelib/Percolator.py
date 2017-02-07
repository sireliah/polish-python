z idlelib.WidgetRedirector zaimportuj WidgetRedirector
z idlelib.Delegator zaimportuj Delegator

klasa Percolator:

    def __init__(self, text):
        # XXX would be nice to inherit z Delegator
        self.text = text
        self.redir = WidgetRedirector(text)
        self.top = self.bottom = Delegator(text)
        self.bottom.insert = self.redir.register("insert", self.insert)
        self.bottom.delete = self.redir.register("delete", self.delete)
        self.filters = []

    def close(self):
        dopóki self.top jest nie self.bottom:
            self.removefilter(self.top)
        self.top = Nic
        self.bottom.setdelegate(Nic); self.bottom = Nic
        self.redir.close(); self.redir = Nic
        self.text = Nic

    def insert(self, index, chars, tags=Nic):
        # Could go away jeżeli inheriting z Delegator
        self.top.insert(index, chars, tags)

    def delete(self, index1, index2=Nic):
        # Could go away jeżeli inheriting z Delegator
        self.top.delete(index1, index2)

    def insertfilter(self, filter):
        # Perhaps rename to pushfilter()?
        assert isinstance(filter, Delegator)
        assert filter.delegate jest Nic
        filter.setdelegate(self.top)
        self.top = filter

    def removefilter(self, filter):
        # XXX Perhaps should only support popfilter()?
        assert isinstance(filter, Delegator)
        assert filter.delegate jest nie Nic
        f = self.top
        jeżeli f jest filter:
            self.top = filter.delegate
            filter.setdelegate(Nic)
        inaczej:
            dopóki f.delegate jest nie filter:
                assert f jest nie self.bottom
                f.resetcache()
                f = f.delegate
            f.setdelegate(filter.delegate)
            filter.setdelegate(Nic)

def _percolator(parent):
    zaimportuj tkinter jako tk
    zaimportuj re
    klasa Tracer(Delegator):
        def __init__(self, name):
            self.name = name
            Delegator.__init__(self, Nic)
        def insert(self, *args):
            print(self.name, ": insert", args)
            self.delegate.insert(*args)
        def delete(self, *args):
            print(self.name, ": delete", args)
            self.delegate.delete(*args)
    root = tk.Tk()
    root.title("Test Percolator")
    width, height, x, y = list(map(int, re.split('[x+]', parent.geometry())))
    root.geometry("+%d+%d"%(x, y + 150))
    text = tk.Text(root)
    p = Percolator(text)
    t1 = Tracer("t1")
    t2 = Tracer("t2")

    def toggle1():
        jeżeli var1.get() == 0:
            var1.set(1)
            p.insertfilter(t1)
        albo_inaczej var1.get() == 1:
            var1.set(0)
            p.removefilter(t1)

    def toggle2():
        jeżeli var2.get() == 0:
            var2.set(1)
            p.insertfilter(t2)
        albo_inaczej var2.get() == 1:
            var2.set(0)
            p.removefilter(t2)

    text.pack()
    var1 = tk.IntVar()
    cb1 = tk.Checkbutton(root, text="Tracer1", command=toggle1, variable=var1)
    cb1.pack()
    var2 = tk.IntVar()
    cb2 = tk.Checkbutton(root, text="Tracer2", command=toggle2, variable=var2)
    cb2.pack()

    root.mainloop()

jeżeli __name__ == "__main__":
    z idlelib.idle_test.htest zaimportuj run
    run(_percolator)
