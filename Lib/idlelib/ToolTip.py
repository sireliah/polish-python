# general purpose 'tooltip' routines - currently unused w idlefork
# (although the 'calltips' extension jest partly based on this code)
# may be useful dla some purposes w (or almost w ;) the current project scope
# Ideas gleaned z PySol

z tkinter zaimportuj *

klasa ToolTipBase:

    def __init__(self, button):
        self.button = button
        self.tipwindow = Nic
        self.id = Nic
        self.x = self.y = 0
        self._id1 = self.button.bind("<Enter>", self.enter)
        self._id2 = self.button.bind("<Leave>", self.leave)
        self._id3 = self.button.bind("<ButtonPress>", self.leave)

    def enter(self, event=Nic):
        self.schedule()

    def leave(self, event=Nic):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.button.after(1500, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = Nic
        jeżeli id:
            self.button.after_cancel(id)

    def showtip(self):
        jeżeli self.tipwindow:
            zwróć
        # The tip window must be completely outside the button;
        # otherwise when the mouse enters the tip window we get
        # a leave event oraz it disappears, oraz then we get an enter
        # event oraz it reappears, oraz so on forever :-(
        x = self.button.winfo_rootx() + 20
        y = self.button.winfo_rooty() + self.button.winfo_height() + 1
        self.tipwindow = tw = Toplevel(self.button)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        self.showcontents()

    def showcontents(self, text="Your text here"):
        # Override this w derived class
        label = Label(self.tipwindow, text=text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1)
        label.pack()

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = Nic
        jeżeli tw:
            tw.destroy()

klasa ToolTip(ToolTipBase):
    def __init__(self, button, text):
        ToolTipBase.__init__(self, button)
        self.text = text
    def showcontents(self):
        ToolTipBase.showcontents(self, self.text)

klasa ListboxToolTip(ToolTipBase):
    def __init__(self, button, items):
        ToolTipBase.__init__(self, button)
        self.items = items
    def showcontents(self):
        listbox = Listbox(self.tipwindow, background="#ffffe0")
        listbox.pack()
        dla item w self.items:
            listbox.insert(END, item)

def _tooltip(parent):
    root = Tk()
    root.title("Test tooltip")
    width, height, x, y = list(map(int, re.split('[x+]', parent.geometry())))
    root.geometry("+%d+%d"%(x, y + 150))
    label = Label(root, text="Place your mouse over buttons")
    label.pack()
    button1 = Button(root, text="Button 1")
    button2 = Button(root, text="Button 2")
    button1.pack()
    button2.pack()
    ToolTip(button1, "This jest tooltip text dla button1.")
    ListboxToolTip(button2, ["This is","multiple line",
                            "tooltip text","dla button2"])
    root.mainloop()

jeżeli __name__ == '__main__':
    z idlelib.idle_test.htest zaimportuj run
    run(_tooltip)
