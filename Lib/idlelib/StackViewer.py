zaimportuj os
zaimportuj sys
zaimportuj linecache
zaimportuj re
zaimportuj tkinter jako tk

z idlelib.TreeWidget zaimportuj TreeNode, TreeItem, ScrolledCanvas
z idlelib.ObjectBrowser zaimportuj ObjectTreeItem, make_objecttreeitem
z idlelib.PyShell zaimportuj PyShellFileList

def StackBrowser(root, flist=Nic, tb=Nic, top=Nic):
    jeżeli top jest Nic:
        z tkinter zaimportuj Toplevel
        top = Toplevel(root)
    sc = ScrolledCanvas(top, bg="white", highlightthickness=0)
    sc.frame.pack(expand=1, fill="both")
    item = StackTreeItem(flist, tb)
    node = TreeNode(sc.canvas, Nic, item)
    node.expand()

klasa StackTreeItem(TreeItem):

    def __init__(self, flist=Nic, tb=Nic):
        self.flist = flist
        self.stack = self.get_stack(tb)
        self.text = self.get_exception()

    def get_stack(self, tb):
        jeżeli tb jest Nic:
            tb = sys.last_traceback
        stack = []
        jeżeli tb oraz tb.tb_frame jest Nic:
            tb = tb.tb_next
        dopóki tb jest nie Nic:
            stack.append((tb.tb_frame, tb.tb_lineno))
            tb = tb.tb_next
        zwróć stack

    def get_exception(self):
        type = sys.last_type
        value = sys.last_value
        jeżeli hasattr(type, "__name__"):
            type = type.__name__
        s = str(type)
        jeżeli value jest nie Nic:
            s = s + ": " + str(value)
        zwróć s

    def GetText(self):
        zwróć self.text

    def GetSubList(self):
        sublist = []
        dla info w self.stack:
            item = FrameTreeItem(info, self.flist)
            sublist.append(item)
        zwróć sublist

klasa FrameTreeItem(TreeItem):

    def __init__(self, info, flist):
        self.info = info
        self.flist = flist

    def GetText(self):
        frame, lineno = self.info
        spróbuj:
            modname = frame.f_globals["__name__"]
        wyjąwszy:
            modname = "?"
        code = frame.f_code
        filename = code.co_filename
        funcname = code.co_name
        sourceline = linecache.getline(filename, lineno)
        sourceline = sourceline.strip()
        jeżeli funcname w ("?", "", Nic):
            item = "%s, line %d: %s" % (modname, lineno, sourceline)
        inaczej:
            item = "%s.%s(...), line %d: %s" % (modname, funcname,
                                             lineno, sourceline)
        zwróć item

    def GetSubList(self):
        frame, lineno = self.info
        sublist = []
        jeżeli frame.f_globals jest nie frame.f_locals:
            item = VariablesTreeItem("<locals>", frame.f_locals, self.flist)
            sublist.append(item)
        item = VariablesTreeItem("<globals>", frame.f_globals, self.flist)
        sublist.append(item)
        zwróć sublist

    def OnDoubleClick(self):
        jeżeli self.flist:
            frame, lineno = self.info
            filename = frame.f_code.co_filename
            jeżeli os.path.isfile(filename):
                self.flist.gotofileline(filename, lineno)

klasa VariablesTreeItem(ObjectTreeItem):

    def GetText(self):
        zwróć self.labeltext

    def GetLabelText(self):
        zwróć Nic

    def IsExpandable(self):
        zwróć len(self.object) > 0

    def keys(self):
        zwróć list(self.object.keys())

    def GetSubList(self):
        sublist = []
        dla key w self.keys():
            spróbuj:
                value = self.object[key]
            wyjąwszy KeyError:
                kontynuuj
            def setfunction(value, key=key, object=self.object):
                object[key] = value
            item = make_objecttreeitem(key + " =", value, setfunction)
            sublist.append(item)
        zwróć sublist

def _stack_viewer(parent):
    root = tk.Tk()
    root.title("Test StackViewer")
    width, height, x, y = list(map(int, re.split('[x+]', parent.geometry())))
    root.geometry("+%d+%d"%(x, y + 150))
    flist = PyShellFileList(root)
    spróbuj: # to obtain a traceback object
        intentional_name_error
    wyjąwszy NameError:
        exc_type, exc_value, exc_tb = sys.exc_info()

    # inject stack trace to sys
    sys.last_type = exc_type
    sys.last_value = exc_value
    sys.last_traceback = exc_tb

    StackBrowser(root, flist=flist, top=root, tb=exc_tb)

    # restore sys to original state
    usuń sys.last_type
    usuń sys.last_value
    usuń sys.last_traceback

jeżeli __name__ == '__main__':
    z idlelib.idle_test.htest zaimportuj run
    run(_stack_viewer)
