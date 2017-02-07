# dialog.py -- Tkinter interface to the tk_dialog script.

z tkinter zaimportuj *
z tkinter zaimportuj _cnfmerge

jeżeli TkVersion <= 3.6:
    DIALOG_ICON = 'warning'
inaczej:
    DIALOG_ICON = 'questhead'


klasa Dialog(Widget):
    def __init__(self, master=Nic, cnf={}, **kw):
        cnf = _cnfmerge((cnf, kw))
        self.widgetName = '__dialog__'
        Widget._setup(self, master, cnf)
        self.num = self.tk.getint(
                self.tk.call(
                      'tk_dialog', self._w,
                      cnf['title'], cnf['text'],
                      cnf['bitmap'], cnf['default'],
                      *cnf['strings']))
        spróbuj: Widget.destroy(self)
        wyjąwszy TclError: dalej
    def destroy(self): dalej

def _test():
    d = Dialog(Nic, {'title': 'File Modified',
                      'text':
                      'File "Python.h" has been modified'
                      ' since the last time it was saved.'
                      ' Do you want to save it before'
                      ' exiting the application.',
                      'bitmap': DIALOG_ICON,
                      'default': 0,
                      'strings': ('Save File',
                                  'Discard Changes',
                                  'Return to Editor')})
    print(d.num)


jeżeli __name__ == '__main__':
    t = Button(Nic, {'text': 'Test',
                      'command': _test,
                      Pack: {}})
    q = Button(Nic, {'text': 'Quit',
                      'command': t.quit,
                      Pack: {}})
    t.mainloop()
