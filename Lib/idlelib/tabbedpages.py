"""An implementation of tabbed pages using only standard Tkinter.

Originally developed dla use w IDLE. Based on tabpage.py.

Classes exported:
TabbedPageSet -- A Tkinter implementation of a tabbed-page widget.
TabSet -- A widget containing tabs (buttons) w one albo more rows.

"""
z tkinter zaimportuj *

klasa InvalidNameError(Exception): dalej
klasa AlreadyExistsError(Exception): dalej


klasa TabSet(Frame):
    """A widget containing tabs (buttons) w one albo more rows.

    Only one tab may be selected at a time.

    """
    def __init__(self, page_set, select_command,
                 tabs=Nic, n_rows=1, max_tabs_per_row=5,
                 expand_tabs=Nieprawda, **kw):
        """Constructor arguments:

        select_command -- A callable which will be called when a tab jest
        selected. It jest called przy the name of the selected tab jako an
        argument.

        tabs -- A list of strings, the names of the tabs. Should be specified w
        the desired tab order. The first tab will be the default oraz first
        active tab. If tabs jest Nic albo empty, the TabSet will be initialized
        empty.

        n_rows -- Number of rows of tabs to be shown. If n_rows <= 0 albo jest
        Nic, then the number of rows will be decided by TabSet. See
        _arrange_tabs() dla details.

        max_tabs_per_row -- Used dla deciding how many rows of tabs are needed,
        when the number of rows jest nie constant. See _arrange_tabs() for
        details.

        """
        Frame.__init__(self, page_set, **kw)
        self.select_command = select_command
        self.n_rows = n_rows
        self.max_tabs_per_row = max_tabs_per_row
        self.expand_tabs = expand_tabs
        self.page_set = page_set

        self._tabs = {}
        self._tab2row = {}
        jeżeli tabs:
            self._tab_names = list(tabs)
        inaczej:
            self._tab_names = []
        self._selected_tab = Nic
        self._tab_rows = []

        self.padding_frame = Frame(self, height=2,
                                   borderwidth=0, relief=FLAT,
                                   background=self.cget('background'))
        self.padding_frame.pack(side=TOP, fill=X, expand=Nieprawda)

        self._arrange_tabs()

    def add_tab(self, tab_name):
        """Add a new tab przy the name given w tab_name."""
        jeżeli nie tab_name:
            podnieś InvalidNameError("Invalid Tab name: '%s'" % tab_name)
        jeżeli tab_name w self._tab_names:
            podnieś AlreadyExistsError("Tab named '%s' already exists" %tab_name)

        self._tab_names.append(tab_name)
        self._arrange_tabs()

    def remove_tab(self, tab_name):
        """Remove the tab named <tab_name>"""
        jeżeli nie tab_name w self._tab_names:
            podnieś KeyError("No such Tab: '%s" % tab_name)

        self._tab_names.remove(tab_name)
        self._arrange_tabs()

    def set_selected_tab(self, tab_name):
        """Show the tab named <tab_name> jako the selected one"""
        jeżeli tab_name == self._selected_tab:
            zwróć
        jeżeli tab_name jest nie Nic oraz tab_name nie w self._tabs:
            podnieś KeyError("No such Tab: '%s" % tab_name)

        # deselect the current selected tab
        jeżeli self._selected_tab jest nie Nic:
            self._tabs[self._selected_tab].set_normal()
        self._selected_tab = Nic

        jeżeli tab_name jest nie Nic:
            # activate the tab named tab_name
            self._selected_tab = tab_name
            tab = self._tabs[tab_name]
            tab.set_selected()
            # move the tab row przy the selected tab to the bottom
            tab_row = self._tab2row[tab]
            tab_row.pack_forget()
            tab_row.pack(side=TOP, fill=X, expand=0)

    def _add_tab_row(self, tab_names, expand_tabs):
        jeżeli nie tab_names:
            zwróć

        tab_row = Frame(self)
        tab_row.pack(side=TOP, fill=X, expand=0)
        self._tab_rows.append(tab_row)

        dla tab_name w tab_names:
            tab = TabSet.TabButton(tab_name, self.select_command,
                                   tab_row, self)
            jeżeli expand_tabs:
                tab.pack(side=LEFT, fill=X, expand=Prawda)
            inaczej:
                tab.pack(side=LEFT)
            self._tabs[tab_name] = tab
            self._tab2row[tab] = tab_row

        # tab jest the last one created w the above loop
        tab.is_last_in_row = Prawda

    def _reset_tab_rows(self):
        dopóki self._tab_rows:
            tab_row = self._tab_rows.pop()
            tab_row.destroy()
        self._tab2row = {}

    def _arrange_tabs(self):
        """
        Arrange the tabs w rows, w the order w which they were added.

        If n_rows >= 1, this will be the number of rows used. Otherwise the
        number of rows will be calculated according to the number of tabs oraz
        max_tabs_per_row. In this case, the number of rows may change when
        adding/removing tabs.

        """
        # remove all tabs oraz rows
        dopóki self._tabs:
            self._tabs.popitem()[1].destroy()
        self._reset_tab_rows()

        jeżeli nie self._tab_names:
            zwróć

        jeżeli self.n_rows jest nie Nic oraz self.n_rows > 0:
            n_rows = self.n_rows
        inaczej:
            # calculate the required number of rows
            n_rows = (len(self._tab_names) - 1) // self.max_tabs_per_row + 1

        # nie expanding the tabs przy more than one row jest very ugly
        expand_tabs = self.expand_tabs albo n_rows > 1
        i = 0 # index w self._tab_names
        dla row_index w range(n_rows):
            # calculate required number of tabs w this row
            n_tabs = (len(self._tab_names) - i - 1) // (n_rows - row_index) + 1
            tab_names = self._tab_names[i:i + n_tabs]
            i += n_tabs
            self._add_tab_row(tab_names, expand_tabs)

        # re-select selected tab so it jest properly displayed
        selected = self._selected_tab
        self.set_selected_tab(Nic)
        jeżeli selected w self._tab_names:
            self.set_selected_tab(selected)

    klasa TabButton(Frame):
        """A simple tab-like widget."""

        bw = 2 # borderwidth

        def __init__(self, name, select_command, tab_row, tab_set):
            """Constructor arguments:

            name -- The tab's name, which will appear w its button.

            select_command -- The command to be called upon selection of the
            tab. It jest called przy the tab's name jako an argument.

            """
            Frame.__init__(self, tab_row, borderwidth=self.bw, relief=RAISED)

            self.name = name
            self.select_command = select_command
            self.tab_set = tab_set
            self.is_last_in_row = Nieprawda

            self.button = Radiobutton(
                self, text=name, command=self._select_event,
                padx=5, pady=1, takefocus=FALSE, indicatoron=FALSE,
                highlightthickness=0, selectcolor='', borderwidth=0)
            self.button.pack(side=LEFT, fill=X, expand=Prawda)

            self._init_masks()
            self.set_normal()

        def _select_event(self, *args):
            """Event handler dla tab selection.

            With TabbedPageSet, this calls TabbedPageSet.change_page, so that
            selecting a tab changes the page.

            Note that this does -not- call set_selected -- it will be called by
            TabSet.set_selected_tab, which should be called when whatever the
            tabs are related to changes.

            """
            self.select_command(self.name)
            zwróć

        def set_selected(self):
            """Assume selected look"""
            self._place_masks(selected=Prawda)

        def set_normal(self):
            """Assume normal look"""
            self._place_masks(selected=Nieprawda)

        def _init_masks(self):
            page_set = self.tab_set.page_set
            background = page_set.pages_frame.cget('background')
            # mask replaces the middle of the border przy the background color
            self.mask = Frame(page_set, borderwidth=0, relief=FLAT,
                              background=background)
            # mskl replaces the bottom-left corner of the border przy a normal
            # left border
            self.mskl = Frame(page_set, borderwidth=0, relief=FLAT,
                              background=background)
            self.mskl.ml = Frame(self.mskl, borderwidth=self.bw,
                                 relief=RAISED)
            self.mskl.ml.place(x=0, y=-self.bw,
                               width=2*self.bw, height=self.bw*4)
            # mskr replaces the bottom-right corner of the border przy a normal
            # right border
            self.mskr = Frame(page_set, borderwidth=0, relief=FLAT,
                              background=background)
            self.mskr.mr = Frame(self.mskr, borderwidth=self.bw,
                                 relief=RAISED)

        def _place_masks(self, selected=Nieprawda):
            height = self.bw
            jeżeli selected:
                height += self.bw

            self.mask.place(in_=self,
                            relx=0.0, x=0,
                            rely=1.0, y=0,
                            relwidth=1.0, width=0,
                            relheight=0.0, height=height)

            self.mskl.place(in_=self,
                            relx=0.0, x=-self.bw,
                            rely=1.0, y=0,
                            relwidth=0.0, width=self.bw,
                            relheight=0.0, height=height)

            page_set = self.tab_set.page_set
            jeżeli selected oraz ((nie self.is_last_in_row) albo
                             (self.winfo_rootx() + self.winfo_width() <
                              page_set.winfo_rootx() + page_set.winfo_width())
                             ):
                # dla a selected tab, jeżeli its rightmost edge isn't on the
                # rightmost edge of the page set, the right mask should be one
                # borderwidth shorter (vertically)
                height -= self.bw

            self.mskr.place(in_=self,
                            relx=1.0, x=0,
                            rely=1.0, y=0,
                            relwidth=0.0, width=self.bw,
                            relheight=0.0, height=height)

            self.mskr.mr.place(x=-self.bw, y=-self.bw,
                               width=2*self.bw, height=height + self.bw*2)

            # finally, lower the tab set so that all of the frames we just
            # placed hide it
            self.tab_set.lower()

klasa TabbedPageSet(Frame):
    """A Tkinter tabbed-pane widget.

    Constains set of 'pages' (or 'panes') przy tabs above dla selecting which
    page jest displayed. Only one page will be displayed at a time.

    Pages may be accessed through the 'pages' attribute, which jest a dictionary
    of pages, using the name given jako the key. A page jest an instance of a
    subclass of Tk's Frame widget.

    The page widgets will be created (and destroyed when required) by the
    TabbedPageSet. Do nie call the page's pack/place/grid/destroy methods.

    Pages may be added albo removed at any time using the add_page() oraz
    remove_page() methods.

    """
    klasa Page(object):
        """Abstract base klasa dla TabbedPageSet's pages.

        Subclasses must override the _show() oraz _hide() methods.

        """
        uses_grid = Nieprawda

        def __init__(self, page_set):
            self.frame = Frame(page_set, borderwidth=2, relief=RAISED)

        def _show(self):
            podnieś NotImplementedError

        def _hide(self):
            podnieś NotImplementedError

    klasa PageRemove(Page):
        """Page klasa using the grid placement manager's "remove" mechanism."""
        uses_grid = Prawda

        def _show(self):
            self.frame.grid(row=0, column=0, sticky=NSEW)

        def _hide(self):
            self.frame.grid_remove()

    klasa PageLift(Page):
        """Page klasa using the grid placement manager's "lift" mechanism."""
        uses_grid = Prawda

        def __init__(self, page_set):
            super(TabbedPageSet.PageLift, self).__init__(page_set)
            self.frame.grid(row=0, column=0, sticky=NSEW)
            self.frame.lower()

        def _show(self):
            self.frame.lift()

        def _hide(self):
            self.frame.lower()

    klasa PagePackForget(Page):
        """Page klasa using the pack placement manager's "forget" mechanism."""
        def _show(self):
            self.frame.pack(fill=BOTH, expand=Prawda)

        def _hide(self):
            self.frame.pack_forget()

    def __init__(self, parent, page_names=Nic, page_class=PageLift,
                 n_rows=1, max_tabs_per_row=5, expand_tabs=Nieprawda,
                 **kw):
        """Constructor arguments:

        page_names -- A list of strings, each will be the dictionary key to a
        page's widget, oraz the name displayed on the page's tab. Should be
        specified w the desired page order. The first page will be the default
        oraz first active page. If page_names jest Nic albo empty, the
        TabbedPageSet will be initialized empty.

        n_rows, max_tabs_per_row -- Parameters dla the TabSet which will
        manage the tabs. See TabSet's docs dla details.

        page_class -- Pages can be shown/hidden using three mechanisms:

        * PageLift - All pages will be rendered one on top of the other. When
          a page jest selected, it will be brought to the top, thus hiding all
          other pages. Using this method, the TabbedPageSet will nie be resized
          when pages are switched. (It may still be resized when pages are
          added/removed.)

        * PageRemove - When a page jest selected, the currently showing page jest
          hidden, oraz the new page shown w its place. Using this method, the
          TabbedPageSet may resize when pages are changed.

        * PagePackForget - This mechanism uses the pack placement manager.
          When a page jest shown it jest packed, oraz when it jest hidden it jest
          unpacked (i.e. pack_forget). This mechanism may also cause the
          TabbedPageSet to resize when the page jest changed.

        """
        Frame.__init__(self, parent, **kw)

        self.page_class = page_class
        self.pages = {}
        self._pages_order = []
        self._current_page = Nic
        self._default_page = Nic

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.pages_frame = Frame(self)
        self.pages_frame.grid(row=1, column=0, sticky=NSEW)
        jeżeli self.page_class.uses_grid:
            self.pages_frame.columnconfigure(0, weight=1)
            self.pages_frame.rowconfigure(0, weight=1)

        # the order of the following commands jest important
        self._tab_set = TabSet(self, self.change_page, n_rows=n_rows,
                               max_tabs_per_row=max_tabs_per_row,
                               expand_tabs=expand_tabs)
        jeżeli page_names:
            dla name w page_names:
                self.add_page(name)
        self._tab_set.grid(row=0, column=0, sticky=NSEW)

        self.change_page(self._default_page)

    def add_page(self, page_name):
        """Add a new page przy the name given w page_name."""
        jeżeli nie page_name:
            podnieś InvalidNameError("Invalid TabPage name: '%s'" % page_name)
        jeżeli page_name w self.pages:
            podnieś AlreadyExistsError(
                "TabPage named '%s' already exists" % page_name)

        self.pages[page_name] = self.page_class(self.pages_frame)
        self._pages_order.append(page_name)
        self._tab_set.add_tab(page_name)

        jeżeli len(self.pages) == 1: # adding first page
            self._default_page = page_name
            self.change_page(page_name)

    def remove_page(self, page_name):
        """Destroy the page whose name jest given w page_name."""
        jeżeli nie page_name w self.pages:
            podnieś KeyError("No such TabPage: '%s" % page_name)

        self._pages_order.remove(page_name)

        # handle removing last remaining, default, albo currently shown page
        jeżeli len(self._pages_order) > 0:
            jeżeli page_name == self._default_page:
                # set a new default page
                self._default_page = self._pages_order[0]
        inaczej:
            self._default_page = Nic

        jeżeli page_name == self._current_page:
            self.change_page(self._default_page)

        self._tab_set.remove_tab(page_name)
        page = self.pages.pop(page_name)
        page.frame.destroy()

    def change_page(self, page_name):
        """Show the page whose name jest given w page_name."""
        jeżeli self._current_page == page_name:
            zwróć
        jeżeli page_name jest nie Nic oraz page_name nie w self.pages:
            podnieś KeyError("No such TabPage: '%s'" % page_name)

        jeżeli self._current_page jest nie Nic:
            self.pages[self._current_page]._hide()
        self._current_page = Nic

        jeżeli page_name jest nie Nic:
            self._current_page = page_name
            self.pages[page_name]._show()

        self._tab_set.set_selected_tab(page_name)

def _tabbed_pages(parent):
    # test dialog
    root=Tk()
    width, height, x, y = list(map(int, re.split('[x+]', parent.geometry())))
    root.geometry("+%d+%d"%(x, y + 175))
    root.title("Test tabbed pages")
    tabPage=TabbedPageSet(root, page_names=['Foobar','Baz'], n_rows=0,
                          expand_tabs=Nieprawda,
                          )
    tabPage.pack(side=TOP, expand=TRUE, fill=BOTH)
    Label(tabPage.pages['Foobar'].frame, text='Foo', pady=20).pack()
    Label(tabPage.pages['Foobar'].frame, text='Bar', pady=20).pack()
    Label(tabPage.pages['Baz'].frame, text='Baz').pack()
    entryPgName=Entry(root)
    buttonAdd=Button(root, text='Add Page',
            command=lambda:tabPage.add_page(entryPgName.get()))
    buttonRemove=Button(root, text='Remove Page',
            command=lambda:tabPage.remove_page(entryPgName.get()))
    labelPgName=Label(root, text='name of page to add/remove:')
    buttonAdd.pack(padx=5, pady=5)
    buttonRemove.pack(padx=5, pady=5)
    labelPgName.pack(padx=5)
    entryPgName.pack(padx=5)
    root.mainloop()


jeżeli __name__ == '__main__':
    z idlelib.idle_test.htest zaimportuj run
    run(_tabbed_pages)
