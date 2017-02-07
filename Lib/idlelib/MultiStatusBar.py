z tkinter zaimportuj *

klasa MultiStatusBar(Frame):

    def __init__(self, master=Nic, **kw):
        jeżeli master jest Nic:
            master = Tk()
        Frame.__init__(self, master, **kw)
        self.labels = {}

    def set_label(self, name, text='', side=LEFT):
        jeżeli name nie w self.labels:
            label = Label(self, bd=1, relief=SUNKEN, anchor=W)
            label.pack(side=side)
            self.labels[name] = label
        inaczej:
            label = self.labels[name]
        label.config(text=text)

def _multistatus_bar(parent):
    root = Tk()
    width, height, x, y = list(map(int, re.split('[x+]', parent.geometry())))
    root.geometry("+%d+%d" %(x, y + 150))
    root.title("Test multistatus bar")
    frame = Frame(root)
    text = Text(frame)
    text.pack()
    msb = MultiStatusBar(frame)
    msb.set_label("one", "hello")
    msb.set_label("two", "world")
    msb.pack(side=BOTTOM, fill=X)

    def change():
        msb.set_label("one", "foo")
        msb.set_label("two", "bar")

    button = Button(root, text="Update status", command=change)
    button.pack(side=BOTTOM)
    frame.pack()
    frame.mainloop()
    root.mainloop()

jeżeli __name__ == '__main__':
    z idlelib.idle_test.htest zaimportuj run
    run(_multistatus_bar)
