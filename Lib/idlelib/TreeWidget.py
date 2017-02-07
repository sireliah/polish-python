# XXX TO DO:
# - popup menu
# - support partial albo total redisplay
# - key bindings (instead of quick-n-dirty bindings on Canvas):
#   - up/down arrow keys to move focus around
#   - ditto dla page up/down, home/end
#   - left/right arrows to expand/collapse & move out/in
# - more doc strings
# - add icons dla "file", "module", "class", "method"; better "python" icon
# - callback dla selection???
# - multiple-item selection
# - tooltips
# - redo geometry without magic numbers
# - keep track of object ids to allow more careful cleaning
# - optimize tree redraw after expand of subnode

zaimportuj os
z tkinter zaimportuj *

z idlelib zaimportuj ZoomHeight
z idlelib.configHandler zaimportuj idleConf

ICONDIR = "Icons"

# Look dla Icons subdirectory w the same directory jako this module
spróbuj:
    _icondir = os.path.join(os.path.dirname(__file__), ICONDIR)
wyjąwszy NameError:
    _icondir = ICONDIR
jeżeli os.path.isdir(_icondir):
    ICONDIR = _icondir
albo_inaczej nie os.path.isdir(ICONDIR):
    podnieś RuntimeError("can't find icon directory (%r)" % (ICONDIR,))

def listicons(icondir=ICONDIR):
    """Utility to display the available icons."""
    root = Tk()
    zaimportuj glob
    list = glob.glob(os.path.join(icondir, "*.gif"))
    list.sort()
    images = []
    row = column = 0
    dla file w list:
        name = os.path.splitext(os.path.basename(file))[0]
        image = PhotoImage(file=file, master=root)
        images.append(image)
        label = Label(root, image=image, bd=1, relief="raised")
        label.grid(row=row, column=column)
        label = Label(root, text=name)
        label.grid(row=row+1, column=column)
        column = column + 1
        jeżeli column >= 10:
            row = row+2
            column = 0
    root.images = images


klasa TreeNode:

    def __init__(self, canvas, parent, item):
        self.canvas = canvas
        self.parent = parent
        self.item = item
        self.state = 'collapsed'
        self.selected = Nieprawda
        self.children = []
        self.x = self.y = Nic
        self.iconimages = {} # cache of PhotoImage instances dla icons

    def destroy(self):
        dla c w self.children[:]:
            self.children.remove(c)
            c.destroy()
        self.parent = Nic

    def geticonimage(self, name):
        spróbuj:
            zwróć self.iconimages[name]
        wyjąwszy KeyError:
            dalej
        file, ext = os.path.splitext(name)
        ext = ext albo ".gif"
        fullname = os.path.join(ICONDIR, file + ext)
        image = PhotoImage(master=self.canvas, file=fullname)
        self.iconimages[name] = image
        zwróć image

    def select(self, event=Nic):
        jeżeli self.selected:
            zwróć
        self.deselectall()
        self.selected = Prawda
        self.canvas.delete(self.image_id)
        self.drawicon()
        self.drawtext()

    def deselect(self, event=Nic):
        jeżeli nie self.selected:
            zwróć
        self.selected = Nieprawda
        self.canvas.delete(self.image_id)
        self.drawicon()
        self.drawtext()

    def deselectall(self):
        jeżeli self.parent:
            self.parent.deselectall()
        inaczej:
            self.deselecttree()

    def deselecttree(self):
        jeżeli self.selected:
            self.deselect()
        dla child w self.children:
            child.deselecttree()

    def flip(self, event=Nic):
        jeżeli self.state == 'expanded':
            self.collapse()
        inaczej:
            self.expand()
        self.item.OnDoubleClick()
        zwróć "break"

    def expand(self, event=Nic):
        jeżeli nie self.item._IsExpandable():
            zwróć
        jeżeli self.state != 'expanded':
            self.state = 'expanded'
            self.update()
            self.view()

    def collapse(self, event=Nic):
        jeżeli self.state != 'collapsed':
            self.state = 'collapsed'
            self.update()

    def view(self):
        top = self.y - 2
        bottom = self.lastvisiblechild().y + 17
        height = bottom - top
        visible_top = self.canvas.canvasy(0)
        visible_height = self.canvas.winfo_height()
        visible_bottom = self.canvas.canvasy(visible_height)
        jeżeli visible_top <= top oraz bottom <= visible_bottom:
            zwróć
        x0, y0, x1, y1 = self.canvas._getints(self.canvas['scrollregion'])
        jeżeli top >= visible_top oraz height <= visible_height:
            fraction = top + height - visible_height
        inaczej:
            fraction = top
        fraction = float(fraction) / y1
        self.canvas.yview_moveto(fraction)

    def lastvisiblechild(self):
        jeżeli self.children oraz self.state == 'expanded':
            zwróć self.children[-1].lastvisiblechild()
        inaczej:
            zwróć self

    def update(self):
        jeżeli self.parent:
            self.parent.update()
        inaczej:
            oldcursor = self.canvas['cursor']
            self.canvas['cursor'] = "watch"
            self.canvas.update()
            self.canvas.delete(ALL)     # XXX could be more subtle
            self.draw(7, 2)
            x0, y0, x1, y1 = self.canvas.bbox(ALL)
            self.canvas.configure(scrollregion=(0, 0, x1, y1))
            self.canvas['cursor'] = oldcursor

    def draw(self, x, y):
        # XXX This hard-codes too many geometry constants!
        dy = 20
        self.x, self.y = x, y
        self.drawicon()
        self.drawtext()
        jeżeli self.state != 'expanded':
            zwróć y + dy
        # draw children
        jeżeli nie self.children:
            sublist = self.item._GetSubList()
            jeżeli nie sublist:
                # _IsExpandable() was mistaken; that's allowed
                zwróć y+17
            dla item w sublist:
                child = self.__class__(self.canvas, self, item)
                self.children.append(child)
        cx = x+20
        cy = y + dy
        cylast = 0
        dla child w self.children:
            cylast = cy
            self.canvas.create_line(x+9, cy+7, cx, cy+7, fill="gray50")
            cy = child.draw(cx, cy)
            jeżeli child.item._IsExpandable():
                jeżeli child.state == 'expanded':
                    iconname = "minusnode"
                    callback = child.collapse
                inaczej:
                    iconname = "plusnode"
                    callback = child.expand
                image = self.geticonimage(iconname)
                id = self.canvas.create_image(x+9, cylast+7, image=image)
                # XXX This leaks bindings until canvas jest deleted:
                self.canvas.tag_bind(id, "<1>", callback)
                self.canvas.tag_bind(id, "<Double-1>", lambda x: Nic)
        id = self.canvas.create_line(x+9, y+10, x+9, cylast+7,
            ##stipple="gray50",     # XXX Seems broken w Tk 8.0.x
            fill="gray50")
        self.canvas.tag_lower(id) # XXX .lower(id) before Python 1.5.2
        zwróć cy

    def drawicon(self):
        jeżeli self.selected:
            imagename = (self.item.GetSelectedIconName() albo
                         self.item.GetIconName() albo
                         "openfolder")
        inaczej:
            imagename = self.item.GetIconName() albo "folder"
        image = self.geticonimage(imagename)
        id = self.canvas.create_image(self.x, self.y, anchor="nw", image=image)
        self.image_id = id
        self.canvas.tag_bind(id, "<1>", self.select)
        self.canvas.tag_bind(id, "<Double-1>", self.flip)

    def drawtext(self):
        textx = self.x+20-1
        texty = self.y-4
        labeltext = self.item.GetLabelText()
        jeżeli labeltext:
            id = self.canvas.create_text(textx, texty, anchor="nw",
                                         text=labeltext)
            self.canvas.tag_bind(id, "<1>", self.select)
            self.canvas.tag_bind(id, "<Double-1>", self.flip)
            x0, y0, x1, y1 = self.canvas.bbox(id)
            textx = max(x1, 200) + 10
        text = self.item.GetText() albo "<no text>"
        spróbuj:
            self.entry
        wyjąwszy AttributeError:
            dalej
        inaczej:
            self.edit_finish()
        spróbuj:
            self.label
        wyjąwszy AttributeError:
            # padding carefully selected (on Windows) to match Entry widget:
            self.label = Label(self.canvas, text=text, bd=0, padx=2, pady=2)
        theme = idleConf.GetOption('main','Theme','name')
        jeżeli self.selected:
            self.label.configure(idleConf.GetHighlight(theme, 'hilite'))
        inaczej:
            self.label.configure(idleConf.GetHighlight(theme, 'normal'))
        id = self.canvas.create_window(textx, texty,
                                       anchor="nw", window=self.label)
        self.label.bind("<1>", self.select_or_edit)
        self.label.bind("<Double-1>", self.flip)
        self.text_id = id

    def select_or_edit(self, event=Nic):
        jeżeli self.selected oraz self.item.IsEditable():
            self.edit(event)
        inaczej:
            self.select(event)

    def edit(self, event=Nic):
        self.entry = Entry(self.label, bd=0, highlightthickness=1, width=0)
        self.entry.insert(0, self.label['text'])
        self.entry.selection_range(0, END)
        self.entry.pack(ipadx=5)
        self.entry.focus_set()
        self.entry.bind("<Return>", self.edit_finish)
        self.entry.bind("<Escape>", self.edit_cancel)

    def edit_finish(self, event=Nic):
        spróbuj:
            entry = self.entry
            usuń self.entry
        wyjąwszy AttributeError:
            zwróć
        text = entry.get()
        entry.destroy()
        jeżeli text oraz text != self.item.GetText():
            self.item.SetText(text)
        text = self.item.GetText()
        self.label['text'] = text
        self.drawtext()
        self.canvas.focus_set()

    def edit_cancel(self, event=Nic):
        spróbuj:
            entry = self.entry
            usuń self.entry
        wyjąwszy AttributeError:
            zwróć
        entry.destroy()
        self.drawtext()
        self.canvas.focus_set()


klasa TreeItem:

    """Abstract klasa representing tree items.

    Methods should typically be overridden, otherwise a default action
    jest used.

    """

    def __init__(self):
        """Constructor.  Do whatever you need to do."""

    def GetText(self):
        """Return text string to display."""

    def GetLabelText(self):
        """Return label text string to display w front of text (jeżeli any)."""

    expandable = Nic

    def _IsExpandable(self):
        """Do nie override!  Called by TreeNode."""
        jeżeli self.expandable jest Nic:
            self.expandable = self.IsExpandable()
        zwróć self.expandable

    def IsExpandable(self):
        """Return whether there are subitems."""
        zwróć 1

    def _GetSubList(self):
        """Do nie override!  Called by TreeNode."""
        jeżeli nie self.IsExpandable():
            zwróć []
        sublist = self.GetSubList()
        jeżeli nie sublist:
            self.expandable = 0
        zwróć sublist

    def IsEditable(self):
        """Return whether the item's text may be edited."""

    def SetText(self, text):
        """Change the item's text (jeżeli it jest editable)."""

    def GetIconName(self):
        """Return name of icon to be displayed normally."""

    def GetSelectedIconName(self):
        """Return name of icon to be displayed when selected."""

    def GetSubList(self):
        """Return list of items forming sublist."""

    def OnDoubleClick(self):
        """Called on a double-click on the item."""


# Example application

klasa FileTreeItem(TreeItem):

    """Example TreeItem subclass -- browse the file system."""

    def __init__(self, path):
        self.path = path

    def GetText(self):
        zwróć os.path.basename(self.path) albo self.path

    def IsEditable(self):
        zwróć os.path.basename(self.path) != ""

    def SetText(self, text):
        newpath = os.path.dirname(self.path)
        newpath = os.path.join(newpath, text)
        jeżeli os.path.dirname(newpath) != os.path.dirname(self.path):
            zwróć
        spróbuj:
            os.rename(self.path, newpath)
            self.path = newpath
        wyjąwszy OSError:
            dalej

    def GetIconName(self):
        jeżeli nie self.IsExpandable():
            zwróć "python" # XXX wish there was a "file" icon

    def IsExpandable(self):
        zwróć os.path.isdir(self.path)

    def GetSubList(self):
        spróbuj:
            names = os.listdir(self.path)
        wyjąwszy OSError:
            zwróć []
        names.sort(key = os.path.normcase)
        sublist = []
        dla name w names:
            item = FileTreeItem(os.path.join(self.path, name))
            sublist.append(item)
        zwróć sublist


# A canvas widget przy scroll bars oraz some useful bindings

klasa ScrolledCanvas:
    def __init__(self, master, **opts):
        jeżeli 'yscrollincrement' nie w opts:
            opts['yscrollincrement'] = 17
        self.master = master
        self.frame = Frame(master)
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.canvas = Canvas(self.frame, **opts)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vbar = Scrollbar(self.frame, name="vbar")
        self.vbar.grid(row=0, column=1, sticky="nse")
        self.hbar = Scrollbar(self.frame, name="hbar", orient="horizontal")
        self.hbar.grid(row=1, column=0, sticky="ews")
        self.canvas['yscrollcommand'] = self.vbar.set
        self.vbar['command'] = self.canvas.yview
        self.canvas['xscrollcommand'] = self.hbar.set
        self.hbar['command'] = self.canvas.xview
        self.canvas.bind("<Key-Prior>", self.page_up)
        self.canvas.bind("<Key-Next>", self.page_down)
        self.canvas.bind("<Key-Up>", self.unit_up)
        self.canvas.bind("<Key-Down>", self.unit_down)
        #jeżeli isinstance(master, Toplevel) albo isinstance(master, Tk):
        self.canvas.bind("<Alt-Key-2>", self.zoom_height)
        self.canvas.focus_set()
    def page_up(self, event):
        self.canvas.yview_scroll(-1, "page")
        zwróć "break"
    def page_down(self, event):
        self.canvas.yview_scroll(1, "page")
        zwróć "break"
    def unit_up(self, event):
        self.canvas.yview_scroll(-1, "unit")
        zwróć "break"
    def unit_down(self, event):
        self.canvas.yview_scroll(1, "unit")
        zwróć "break"
    def zoom_height(self, event):
        ZoomHeight.zoom_height(self.master)
        zwróć "break"


def _tree_widget(parent):
    root = Tk()
    root.title("Test TreeWidget")
    width, height, x, y = list(map(int, re.split('[x+]', parent.geometry())))
    root.geometry("+%d+%d"%(x, y + 150))
    sc = ScrolledCanvas(root, bg="white", highlightthickness=0, takefocus=1)
    sc.frame.pack(expand=1, fill="both", side=LEFT)
    item = FileTreeItem(os.getcwd())
    node = TreeNode(sc.canvas, Nic, item)
    node.expand()
    root.mainloop()

jeżeli __name__ == '__main__':
    z idlelib.idle_test.htest zaimportuj run
    run(_tree_widget)
