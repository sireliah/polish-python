# XXX TO DO:
# - popup menu
# - support partial albo total redisplay
# - more doc strings
# - tooltips

# object browser

# XXX TO DO:
# - dla classes/modules, add "open source" to object browser

zaimportuj re

z idlelib.TreeWidget zaimportuj TreeItem, TreeNode, ScrolledCanvas

z reprlib zaimportuj Repr

myrepr = Repr()
myrepr.maxstring = 100
myrepr.maxother = 100

klasa ObjectTreeItem(TreeItem):
    def __init__(self, labeltext, object, setfunction=Nic):
        self.labeltext = labeltext
        self.object = object
        self.setfunction = setfunction
    def GetLabelText(self):
        zwróć self.labeltext
    def GetText(self):
        zwróć myrepr.repr(self.object)
    def GetIconName(self):
        jeżeli nie self.IsExpandable():
            zwróć "python"
    def IsEditable(self):
        zwróć self.setfunction jest nie Nic
    def SetText(self, text):
        spróbuj:
            value = eval(text)
            self.setfunction(value)
        wyjąwszy:
            dalej
        inaczej:
            self.object = value
    def IsExpandable(self):
        zwróć nie not dir(self.object)
    def GetSubList(self):
        keys = dir(self.object)
        sublist = []
        dla key w keys:
            spróbuj:
                value = getattr(self.object, key)
            wyjąwszy AttributeError:
                kontynuuj
            item = make_objecttreeitem(
                str(key) + " =",
                value,
                lambda value, key=key, object=self.object:
                    setattr(object, key, value))
            sublist.append(item)
        zwróć sublist

klasa ClassTreeItem(ObjectTreeItem):
    def IsExpandable(self):
        zwróć Prawda
    def GetSubList(self):
        sublist = ObjectTreeItem.GetSubList(self)
        jeżeli len(self.object.__bases__) == 1:
            item = make_objecttreeitem("__bases__[0] =",
                self.object.__bases__[0])
        inaczej:
            item = make_objecttreeitem("__bases__ =", self.object.__bases__)
        sublist.insert(0, item)
        zwróć sublist

klasa AtomicObjectTreeItem(ObjectTreeItem):
    def IsExpandable(self):
        zwróć 0

klasa SequenceTreeItem(ObjectTreeItem):
    def IsExpandable(self):
        zwróć len(self.object) > 0
    def keys(self):
        zwróć range(len(self.object))
    def GetSubList(self):
        sublist = []
        dla key w self.keys():
            spróbuj:
                value = self.object[key]
            wyjąwszy KeyError:
                kontynuuj
            def setfunction(value, key=key, object=self.object):
                object[key] = value
            item = make_objecttreeitem("%r:" % (key,), value, setfunction)
            sublist.append(item)
        zwróć sublist

klasa DictTreeItem(SequenceTreeItem):
    def keys(self):
        keys = list(self.object.keys())
        spróbuj:
            keys.sort()
        wyjąwszy:
            dalej
        zwróć keys

dispatch = {
    int: AtomicObjectTreeItem,
    float: AtomicObjectTreeItem,
    str: AtomicObjectTreeItem,
    tuple: SequenceTreeItem,
    list: SequenceTreeItem,
    dict: DictTreeItem,
    type: ClassTreeItem,
}

def make_objecttreeitem(labeltext, object, setfunction=Nic):
    t = type(object)
    jeżeli t w dispatch:
        c = dispatch[t]
    inaczej:
        c = ObjectTreeItem
    zwróć c(labeltext, object, setfunction)


def _object_browser(parent):
    zaimportuj sys
    z tkinter zaimportuj Tk
    root = Tk()
    root.title("Test ObjectBrowser")
    width, height, x, y = list(map(int, re.split('[x+]', parent.geometry())))
    root.geometry("+%d+%d"%(x, y + 150))
    root.configure(bd=0, bg="yellow")
    root.focus_set()
    sc = ScrolledCanvas(root, bg="white", highlightthickness=0, takefocus=1)
    sc.frame.pack(expand=1, fill="both")
    item = make_objecttreeitem("sys", sys)
    node = TreeNode(sc.canvas, Nic, item)
    node.update()
    root.mainloop()

jeżeli __name__ == '__main__':
    z idlelib.idle_test.htest zaimportuj run
    run(_object_browser)
