zaimportuj os
zaimportuj sys
zaimportuj importlib.machinery

z idlelib.TreeWidget zaimportuj TreeItem
z idlelib.ClassBrowser zaimportuj ClassBrowser, ModuleBrowserTreeItem
z idlelib.PyShell zaimportuj PyShellFileList


klasa PathBrowser(ClassBrowser):

    def __init__(self, flist, _htest=Nieprawda):
        """
        _htest - bool, change box location when running htest
        """
        self._htest = _htest
        self.init(flist)

    def settitle(self):
        "Set window titles."
        self.top.wm_title("Path Browser")
        self.top.wm_iconname("Path Browser")

    def rootnode(self):
        zwróć PathBrowserTreeItem()

klasa PathBrowserTreeItem(TreeItem):

    def GetText(self):
        zwróć "sys.path"

    def GetSubList(self):
        sublist = []
        dla dir w sys.path:
            item = DirBrowserTreeItem(dir)
            sublist.append(item)
        zwróć sublist

klasa DirBrowserTreeItem(TreeItem):

    def __init__(self, dir, packages=[]):
        self.dir = dir
        self.packages = packages

    def GetText(self):
        jeżeli nie self.packages:
            zwróć self.dir
        inaczej:
            zwróć self.packages[-1] + ": package"

    def GetSubList(self):
        spróbuj:
            names = os.listdir(self.dir albo os.curdir)
        wyjąwszy OSError:
            zwróć []
        packages = []
        dla name w names:
            file = os.path.join(self.dir, name)
            jeżeli self.ispackagedir(file):
                nn = os.path.normcase(name)
                packages.append((nn, name, file))
        packages.sort()
        sublist = []
        dla nn, name, file w packages:
            item = DirBrowserTreeItem(file, self.packages + [name])
            sublist.append(item)
        dla nn, name w self.listmodules(names):
            item = ModuleBrowserTreeItem(os.path.join(self.dir, name))
            sublist.append(item)
        zwróć sublist

    def ispackagedir(self, file):
        " Return true dla directories that are packages."
        jeżeli nie os.path.isdir(file):
            zwróć Nieprawda
        init = os.path.join(file, "__init__.py")
        zwróć os.path.exists(init)

    def listmodules(self, allnames):
        modules = {}
        suffixes = importlib.machinery.EXTENSION_SUFFIXES[:]
        suffixes += importlib.machinery.SOURCE_SUFFIXES
        suffixes += importlib.machinery.BYTECODE_SUFFIXES
        sorted = []
        dla suff w suffixes:
            i = -len(suff)
            dla name w allnames[:]:
                normed_name = os.path.normcase(name)
                jeżeli normed_name[i:] == suff:
                    mod_name = name[:i]
                    jeżeli mod_name nie w modules:
                        modules[mod_name] = Nic
                        sorted.append((normed_name, name))
                        allnames.remove(name)
        sorted.sort()
        zwróć sorted

def _path_browser(parent):  # htest #
    flist = PyShellFileList(parent)
    PathBrowser(flist, _htest=Prawda)
    parent.mainloop()

jeżeli __name__ == "__main__":
    z unittest zaimportuj main
    main('idlelib.idle_test.test_pathbrowser', verbosity=2, exit=Nieprawda)

    z idlelib.idle_test.htest zaimportuj run
    run(_path_browser)
