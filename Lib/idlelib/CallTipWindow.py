"""A CallTip window klasa dla Tkinter/IDLE.

After ToolTip.py, which uses ideas gleaned z PySol
Used by the CallTips IDLE extension.
"""
z tkinter zaimportuj Toplevel, Label, LEFT, SOLID, TclError

HIDE_VIRTUAL_EVENT_NAME = "<<calltipwindow-hide>>"
HIDE_SEQUENCES = ("<Key-Escape>", "<FocusOut>")
CHECKHIDE_VIRTUAL_EVENT_NAME = "<<calltipwindow-checkhide>>"
CHECKHIDE_SEQUENCES = ("<KeyRelease>", "<ButtonRelease>")
CHECKHIDE_TIME = 100 # miliseconds

MARK_RIGHT = "calltipwindowregion_right"

klasa CallTip:

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = self.label = Nic
        self.parenline = self.parencol = Nic
        self.lastline = Nic
        self.hideid = self.checkhideid = Nic
        self.checkhide_after_id = Nic

    def position_window(self):
        """Check jeżeli needs to reposition the window, oraz jeżeli so - do it."""
        curline = int(self.widget.index("insert").split('.')[0])
        jeżeli curline == self.lastline:
            zwróć
        self.lastline = curline
        self.widget.see("insert")
        jeżeli curline == self.parenline:
            box = self.widget.bbox("%d.%d" % (self.parenline,
                                              self.parencol))
        inaczej:
            box = self.widget.bbox("%d.0" % curline)
        jeżeli nie box:
            box = list(self.widget.bbox("insert"))
            # align to left of window
            box[0] = 0
            box[2] = 0
        x = box[0] + self.widget.winfo_rootx() + 2
        y = box[1] + box[3] + self.widget.winfo_rooty()
        self.tipwindow.wm_geometry("+%d+%d" % (x, y))

    def showtip(self, text, parenleft, parenright):
        """Show the calltip, bind events which will close it oraz reposition it.
        """
        # Only called w CallTips, where lines are truncated
        self.text = text
        jeżeli self.tipwindow albo nie self.text:
            zwróć

        self.widget.mark_set(MARK_RIGHT, parenright)
        self.parenline, self.parencol = map(
            int, self.widget.index(parenleft).split("."))

        self.tipwindow = tw = Toplevel(self.widget)
        self.position_window()
        # remove border on calltip window
        tw.wm_overrideredirect(1)
        spróbuj:
            # This command jest only needed oraz available on Tk >= 8.4.0 dla OSX
            # Without it, call tips intrude on the typing process by grabbing
            # the focus.
            tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w,
                       "help", "noActivates")
        wyjąwszy TclError:
            dalej
        self.label = Label(tw, text=self.text, justify=LEFT,
                           background="#ffffe0", relief=SOLID, borderwidth=1,
                           font = self.widget['font'])
        self.label.pack()

        self.checkhideid = self.widget.bind(CHECKHIDE_VIRTUAL_EVENT_NAME,
                                            self.checkhide_event)
        dla seq w CHECKHIDE_SEQUENCES:
            self.widget.event_add(CHECKHIDE_VIRTUAL_EVENT_NAME, seq)
        self.widget.after(CHECKHIDE_TIME, self.checkhide_event)
        self.hideid = self.widget.bind(HIDE_VIRTUAL_EVENT_NAME,
                                       self.hide_event)
        dla seq w HIDE_SEQUENCES:
            self.widget.event_add(HIDE_VIRTUAL_EVENT_NAME, seq)

    def checkhide_event(self, event=Nic):
        jeżeli nie self.tipwindow:
            # If the event was triggered by the same event that unbinded
            # this function, the function will be called nevertheless,
            # so do nothing w this case.
            zwróć
        curline, curcol = map(int, self.widget.index("insert").split('.'))
        jeżeli curline < self.parenline albo \
           (curline == self.parenline oraz curcol <= self.parencol) albo \
           self.widget.compare("insert", ">", MARK_RIGHT):
            self.hidetip()
        inaczej:
            self.position_window()
            jeżeli self.checkhide_after_id jest nie Nic:
                self.widget.after_cancel(self.checkhide_after_id)
            self.checkhide_after_id = \
                self.widget.after(CHECKHIDE_TIME, self.checkhide_event)

    def hide_event(self, event):
        jeżeli nie self.tipwindow:
            # See the explanation w checkhide_event.
            zwróć
        self.hidetip()

    def hidetip(self):
        jeżeli nie self.tipwindow:
            zwróć

        dla seq w CHECKHIDE_SEQUENCES:
            self.widget.event_delete(CHECKHIDE_VIRTUAL_EVENT_NAME, seq)
        self.widget.unbind(CHECKHIDE_VIRTUAL_EVENT_NAME, self.checkhideid)
        self.checkhideid = Nic
        dla seq w HIDE_SEQUENCES:
            self.widget.event_delete(HIDE_VIRTUAL_EVENT_NAME, seq)
        self.widget.unbind(HIDE_VIRTUAL_EVENT_NAME, self.hideid)
        self.hideid = Nic

        self.label.destroy()
        self.label = Nic
        self.tipwindow.destroy()
        self.tipwindow = Nic

        self.widget.mark_unset(MARK_RIGHT)
        self.parenline = self.parencol = self.lastline = Nic

    def is_active(self):
        zwróć bool(self.tipwindow)


def _calltip_window(parent):  # htest #
    z tkinter zaimportuj Toplevel, Text, LEFT, BOTH

    top = Toplevel(parent)
    top.title("Test calltips")
    top.geometry("200x100+%d+%d" % (parent.winfo_rootx() + 200,
                  parent.winfo_rooty() + 150))
    text = Text(top)
    text.pack(side=LEFT, fill=BOTH, expand=1)
    text.insert("insert", "string.split")
    top.update()
    calltip = CallTip(text)

    def calltip_show(event):
        calltip.showtip("(s=Hello world)", "insert", "end")
    def calltip_hide(event):
        calltip.hidetip()
    text.event_add("<<calltip-show>>", "(")
    text.event_add("<<calltip-hide>>", ")")
    text.bind("<<calltip-show>>", calltip_show)
    text.bind("<<calltip-hide>>", calltip_hide)
    text.focus_set()

jeżeli __name__=='__main__':
    z idlelib.idle_test.htest zaimportuj run
    run(_calltip_window)
