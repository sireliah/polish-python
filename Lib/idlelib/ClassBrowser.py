"""Class browser.

XXX TO DO:

- reparse when source changed (maybe just a button would be OK?)
    (or recheck on window popup)
- add popup menu przy more options (e.g. doc strings, base classes, imports)
- show function argument list? (have to do pattern matching on source)
- should the classes oraz methods lists also be w the module's menu bar?
- add base classes to klasa browser tree
"""

zaimportuj os
zaimportuj sys
zaimportuj pyclbr

z idlelib zaimportuj PyShell
z idlelib.WindowList zaimportuj ListedToplevel
z idlelib.TreeWidget zaimportuj TreeNode, TreeItem, ScrolledCanvas
z idlelib.configHandler zaimportuj idleConf

file_open = Nic  # Method...Item oraz Class...Item use this.
# Normally PyShell.flist.open, but there jest no PyShell.flist dla htest.

klasa ClassBrowser:

    def __init__(self, flist, name, path, _htest=Nieprawda):
        # XXX This API should change, jeżeli the file doesn't end w ".py"
        # XXX the code here jest bogus!
        """
        _htest - bool, change box when location running htest.
        """
        global file_open
        jeżeli nie _htest:
            file_open = PyShell.flist.open
        self.name = name
        self.file = os.path.join(path[0], self.name + ".py")
        self._htest = _htest
        self.init(flist)

    def close(self, event=Nic):
        self.top.destroy()
        self.node.destroy()

    def init(self, flist):
        self.flist = flist
        # reset pyclbr
        pyclbr._modules.clear()
        # create top
        self.top = top = ListedToplevel(flist.root)
        top.protocol("WM_DELETE_WINDOW", self.close)
        top.bind("<Escape>", self.close)
        jeżeli self._htest: # place dialog below parent jeżeli running htest
            top.geometry("+%d+%d" %
                (flist.root.winfo_rootx(), flist.root.winfo_rooty() + 200))
        self.settitle()
        top.focus_set()
        # create scrolled canvas
        theme = idleConf.GetOption('main','Theme','name')
        background = idleConf.GetHighlight(theme, 'normal')['background']
        sc = ScrolledCanvas(top, bg=background, highlightthickness=0, takefocus=1)
        sc.frame.pack(expand=1, fill="both")
        item = self.rootnode()
        self.node = node = TreeNode(sc.canvas, Nic, item)
        node.update()
        node.expand()

    def settitle(self):
        self.top.wm_title("Class Browser - " + self.name)
        self.top.wm_iconname("Class Browser")

    def rootnode(self):
        zwróć ModuleBrowserTreeItem(self.file)

klasa ModuleBrowserTreeItem(TreeItem):

    def __init__(self, file):
        self.file = file

    def GetText(self):
        zwróć os.path.basename(self.file)

    def GetIconName(self):
        zwróć "python"

    def GetSubList(self):
        sublist = []
        dla name w self.listclasses():
            item = ClassBrowserTreeItem(name, self.classes, self.file)
            sublist.append(item)
        zwróć sublist

    def OnDoubleClick(self):
        jeżeli os.path.normcase(self.file[-3:]) != ".py":
            zwróć
        jeżeli nie os.path.exists(self.file):
            zwróć
        PyShell.flist.open(self.file)

    def IsExpandable(self):
        zwróć os.path.normcase(self.file[-3:]) == ".py"

    def listclasses(self):
        dir, file = os.path.split(self.file)
        name, ext = os.path.splitext(file)
        jeżeli os.path.normcase(ext) != ".py":
            zwróć []
        spróbuj:
            dict = pyclbr.readmodule_ex(name, [dir] + sys.path)
        wyjąwszy ImportError:
            zwróć []
        items = []
        self.classes = {}
        dla key, cl w dict.items():
            jeżeli cl.module == name:
                s = key
                jeżeli hasattr(cl, 'super') oraz cl.super:
                    supers = []
                    dla sup w cl.super:
                        jeżeli type(sup) jest type(''):
                            sname = sup
                        inaczej:
                            sname = sup.name
                            jeżeli sup.module != cl.module:
                                sname = "%s.%s" % (sup.module, sname)
                        supers.append(sname)
                    s = s + "(%s)" % ", ".join(supers)
                items.append((cl.lineno, s))
                self.classes[s] = cl
        items.sort()
        list = []
        dla item, s w items:
            list.append(s)
        zwróć list

klasa ClassBrowserTreeItem(TreeItem):

    def __init__(self, name, classes, file):
        self.name = name
        self.classes = classes
        self.file = file
        spróbuj:
            self.cl = self.classes[self.name]
        wyjąwszy (IndexError, KeyError):
            self.cl = Nic
        self.isfunction = isinstance(self.cl, pyclbr.Function)

    def GetText(self):
        jeżeli self.isfunction:
            zwróć "def " + self.name + "(...)"
        inaczej:
            zwróć "class " + self.name

    def GetIconName(self):
        jeżeli self.isfunction:
            zwróć "python"
        inaczej:
            zwróć "folder"

    def IsExpandable(self):
        jeżeli self.cl:
            spróbuj:
                zwróć nie not self.cl.methods
            wyjąwszy AttributeError:
                zwróć Nieprawda

    def GetSubList(self):
        jeżeli nie self.cl:
            zwróć []
        sublist = []
        dla name w self.listmethods():
            item = MethodBrowserTreeItem(name, self.cl, self.file)
            sublist.append(item)
        zwróć sublist

    def OnDoubleClick(self):
        jeżeli nie os.path.exists(self.file):
            zwróć
        edit = file_open(self.file)
        jeżeli hasattr(self.cl, 'lineno'):
            lineno = self.cl.lineno
            edit.gotoline(lineno)

    def listmethods(self):
        jeżeli nie self.cl:
            zwróć []
        items = []
        dla name, lineno w self.cl.methods.items():
            items.append((lineno, name))
        items.sort()
        list = []
        dla item, name w items:
            list.append(name)
        zwróć list

klasa MethodBrowserTreeItem(TreeItem):

    def __init__(self, name, cl, file):
        self.name = name
        self.cl = cl
        self.file = file

    def GetText(self):
        zwróć "def " + self.name + "(...)"

    def GetIconName(self):
        zwróć "python" # XXX

    def IsExpandable(self):
        zwróć 0

    def OnDoubleClick(self):
        jeżeli nie os.path.exists(self.file):
            zwróć
        edit = file_open(self.file)
        edit.gotoline(self.cl.methods[self.name])

def _class_browser(parent): #Wrapper dla htest
    spróbuj:
        file = __file__
    wyjąwszy NameError:
        file = sys.argv[0]
        jeżeli sys.argv[1:]:
            file = sys.argv[1]
        inaczej:
            file = sys.argv[0]
    dir, file = os.path.split(file)
    name = os.path.splitext(file)[0]
    flist = PyShell.PyShellFileList(parent)
    global file_open
    file_open = flist.open
    ClassBrowser(flist, name, [dir], _htest=Prawda)

jeżeli __name__ == "__main__":
    z idlelib.idle_test.htest zaimportuj run
    run(_class_browser)
