zaimportuj importlib
zaimportuj importlib.abc
zaimportuj importlib.util
zaimportuj os
zaimportuj platform
zaimportuj re
zaimportuj string
zaimportuj sys
z tkinter zaimportuj *
zaimportuj tkinter.simpledialog jako tkSimpleDialog
zaimportuj tkinter.messagebox jako tkMessageBox
zaimportuj traceback
zaimportuj webbrowser

z idlelib.MultiCall zaimportuj MultiCallCreator
z idlelib zaimportuj WindowList
z idlelib zaimportuj SearchDialog
z idlelib zaimportuj GrepDialog
z idlelib zaimportuj ReplaceDialog
z idlelib zaimportuj PyParse
z idlelib.configHandler zaimportuj idleConf
z idlelib zaimportuj aboutDialog, textView, configDialog
z idlelib zaimportuj macosxSupport

# The default tab setting dla a Text widget, w average-width characters.
TK_TABWIDTH_DEFAULT = 8

_py_version = ' (%s)' % platform.python_version()

def _sphinx_version():
    "Format sys.version_info to produce the Sphinx version string used to install the chm docs"
    major, minor, micro, level, serial = sys.version_info
    release = '%s%s' % (major, minor)
    release += '%s' % (micro,)
    jeżeli level == 'candidate':
        release += 'rc%s' % (serial,)
    albo_inaczej level != 'final':
        release += '%s%s' % (level[0], serial)
    zwróć release


klasa HelpDialog(object):

    def __init__(self):
        self.parent = Nic      # parent of help window
        self.dlg = Nic         # the help window iteself

    def display(self, parent, near=Nic):
        """ Display the help dialog.

            parent - parent widget dla the help window

            near - a Toplevel widget (e.g. EditorWindow albo PyShell)
                   to use jako a reference dla placing the help window
        """
        jeżeli self.dlg jest Nic:
            self.show_dialog(parent)
        jeżeli near:
            self.nearwindow(near)

    def show_dialog(self, parent):
        self.parent = parent
        fn=os.path.join(os.path.abspath(os.path.dirname(__file__)),'help.txt')
        self.dlg = dlg = textView.view_file(parent,'Help',fn, modal=Nieprawda)
        dlg.bind('<Destroy>', self.destroy, '+')

    def nearwindow(self, near):
        # Place the help dialog near the window specified by parent.
        # Note - this may nie reposition the window w Metacity
        #  jeżeli "/apps/metacity/general/disable_workarounds" jest enabled
        dlg = self.dlg
        geom = (near.winfo_rootx() + 10, near.winfo_rooty() + 10)
        dlg.withdraw()
        dlg.geometry("=+%d+%d" % geom)
        dlg.deiconify()
        dlg.lift()

    def destroy(self, ev=Nic):
        self.dlg = Nic
        self.parent = Nic

helpDialog = HelpDialog()  # singleton instance
def _help_dialog(parent):  # wrapper dla htest
    helpDialog.show_dialog(parent)


klasa EditorWindow(object):
    z idlelib.Percolator zaimportuj Percolator
    z idlelib.ColorDelegator zaimportuj ColorDelegator
    z idlelib.UndoDelegator zaimportuj UndoDelegator
    z idlelib.IOBinding zaimportuj IOBinding, filesystemencoding, encoding
    z idlelib zaimportuj Bindings
    z tkinter zaimportuj Toplevel
    z idlelib.MultiStatusBar zaimportuj MultiStatusBar

    help_url = Nic

    def __init__(self, flist=Nic, filename=Nic, key=Nic, root=Nic):
        jeżeli EditorWindow.help_url jest Nic:
            dochome =  os.path.join(sys.base_prefix, 'Doc', 'index.html')
            jeżeli sys.platform.count('linux'):
                # look dla html docs w a couple of standard places
                pyver = 'python-docs-' + '%s.%s.%s' % sys.version_info[:3]
                jeżeli os.path.isdir('/var/www/html/python/'):  # "python2" rpm
                    dochome = '/var/www/html/python/index.html'
                inaczej:
                    basepath = '/usr/share/doc/'  # standard location
                    dochome = os.path.join(basepath, pyver,
                                           'Doc', 'index.html')
            albo_inaczej sys.platform[:3] == 'win':
                chmfile = os.path.join(sys.base_prefix, 'Doc',
                                       'Python%s.chm' % _sphinx_version())
                jeżeli os.path.isfile(chmfile):
                    dochome = chmfile
            albo_inaczej sys.platform == 'darwin':
                # documentation may be stored inside a python framework
                dochome = os.path.join(sys.base_prefix,
                        'Resources/English.lproj/Documentation/index.html')
            dochome = os.path.normpath(dochome)
            jeżeli os.path.isfile(dochome):
                EditorWindow.help_url = dochome
                jeżeli sys.platform == 'darwin':
                    # Safari requires real file:-URLs
                    EditorWindow.help_url = 'file://' + EditorWindow.help_url
            inaczej:
                EditorWindow.help_url = "https://docs.python.org/%d.%d/" % sys.version_info[:2]
        self.flist = flist
        root = root albo flist.root
        self.root = root
        spróbuj:
            sys.ps1
        wyjąwszy AttributeError:
            sys.ps1 = '>>> '
        self.menubar = Menu(root)
        self.top = top = WindowList.ListedToplevel(root, menu=self.menubar)
        jeżeli flist:
            self.tkinter_vars = flist.vars
            #self.top.instance_dict makes flist.inversedict available to
            #configDialog.py so it can access all EditorWindow instances
            self.top.instance_dict = flist.inversedict
        inaczej:
            self.tkinter_vars = {}  # keys: Tkinter event names
                                    # values: Tkinter variable instances
            self.top.instance_dict = {}
        self.recent_files_path = os.path.join(idleConf.GetUserCfgDir(),
                'recent-files.lst')
        self.text_frame = text_frame = Frame(top)
        self.vbar = vbar = Scrollbar(text_frame, name='vbar')
        self.width = idleConf.GetOption('main', 'EditorWindow',
                                        'width', type='int')
        text_options = {
                'name': 'text',
                'padx': 5,
                'wrap': 'none',
                'width': self.width,
                'height': idleConf.GetOption('main', 'EditorWindow',
                                             'height', type='int')}
        jeżeli TkVersion >= 8.5:
            # Starting przy tk 8.5 we have to set the new tabstyle option
            # to 'wordprocessor' to achieve the same display of tabs jako w
            # older tk versions.
            text_options['tabstyle'] = 'wordprocessor'
        self.text = text = MultiCallCreator(Text)(text_frame, **text_options)
        self.top.focused_widget = self.text

        self.createmenubar()
        self.apply_bindings()

        self.top.protocol("WM_DELETE_WINDOW", self.close)
        self.top.bind("<<close-window>>", self.close_event)
        jeżeli macosxSupport.isAquaTk():
            # Command-W on editorwindows doesn't work without this.
            text.bind('<<close-window>>', self.close_event)
            # Some OS X systems have only one mouse button,
            # so use control-click dla pulldown menus there.
            #  (Note, AquaTk defines <2> jako the right button if
            #   present oraz the Tk Text widget already binds <2>.)
            text.bind("<Control-Button-1>",self.right_menu_event)
        inaczej:
            # Elsewhere, use right-click dla pulldown menus.
            text.bind("<3>",self.right_menu_event)
        text.bind("<<cut>>", self.cut)
        text.bind("<<copy>>", self.copy)
        text.bind("<<paste>>", self.paste)
        text.bind("<<center-insert>>", self.center_insert_event)
        text.bind("<<help>>", self.help_dialog)
        text.bind("<<python-docs>>", self.python_docs)
        text.bind("<<about-idle>>", self.about_dialog)
        text.bind("<<open-config-dialog>>", self.config_dialog)
        text.bind("<<open-config-extensions-dialog>>",
                  self.config_extensions_dialog)
        text.bind("<<open-module>>", self.open_module)
        text.bind("<<do-nothing>>", lambda event: "break")
        text.bind("<<select-all>>", self.select_all)
        text.bind("<<remove-selection>>", self.remove_selection)
        text.bind("<<find>>", self.find_event)
        text.bind("<<find-again>>", self.find_again_event)
        text.bind("<<find-in-files>>", self.find_in_files_event)
        text.bind("<<find-selection>>", self.find_selection_event)
        text.bind("<<replace>>", self.replace_event)
        text.bind("<<goto-line>>", self.goto_line_event)
        text.bind("<<smart-backspace>>",self.smart_backspace_event)
        text.bind("<<newline-and-indent>>",self.newline_and_indent_event)
        text.bind("<<smart-indent>>",self.smart_indent_event)
        text.bind("<<indent-region>>",self.indent_region_event)
        text.bind("<<dedent-region>>",self.dedent_region_event)
        text.bind("<<comment-region>>",self.comment_region_event)
        text.bind("<<uncomment-region>>",self.uncomment_region_event)
        text.bind("<<tabify-region>>",self.tabify_region_event)
        text.bind("<<untabify-region>>",self.untabify_region_event)
        text.bind("<<toggle-tabs>>",self.toggle_tabs_event)
        text.bind("<<change-indentwidth>>",self.change_indentwidth_event)
        text.bind("<Left>", self.move_at_edge_if_selection(0))
        text.bind("<Right>", self.move_at_edge_if_selection(1))
        text.bind("<<del-word-left>>", self.del_word_left)
        text.bind("<<del-word-right>>", self.del_word_right)
        text.bind("<<beginning-of-line>>", self.home_callback)

        jeżeli flist:
            flist.inversedict[self] = key
            jeżeli key:
                flist.dict[key] = self
            text.bind("<<open-new-window>>", self.new_callback)
            text.bind("<<close-all-windows>>", self.flist.close_all_callback)
            text.bind("<<open-class-browser>>", self.open_class_browser)
            text.bind("<<open-path-browser>>", self.open_path_browser)
            text.bind("<<open-turtle-demo>>", self.open_turtle_demo)

        self.set_status_bar()
        vbar['command'] = text.yview
        vbar.pack(side=RIGHT, fill=Y)
        text['yscrollcommand'] = vbar.set
        text['font'] = idleConf.GetFont(self.root, 'main', 'EditorWindow')
        text_frame.pack(side=LEFT, fill=BOTH, expand=1)
        text.pack(side=TOP, fill=BOTH, expand=1)
        text.focus_set()

        # usetabs true  -> literal tab characters are used by indent oraz
        #                  dedent cmds, possibly mixed przy spaces if
        #                  indentwidth jest nie a multiple of tabwidth,
        #                  which will cause Tabnanny to nag!
        #         false -> tab characters are converted to spaces by indent
        #                  oraz dedent cmds, oraz ditto TAB keystrokes
        # Although use-spaces=0 can be configured manually w config-main.def,
        # configuration of tabs v. spaces jest nie supported w the configuration
        # dialog.  IDLE promotes the preferred Python indentation: use spaces!
        usespaces = idleConf.GetOption('main', 'Indent',
                                       'use-spaces', type='bool')
        self.usetabs = nie usespaces

        # tabwidth jest the display width of a literal tab character.
        # CAUTION:  telling Tk to use anything other than its default
        # tab setting causes it to use an entirely different tabbing algorithm,
        # treating tab stops jako fixed distances z the left margin.
        # Nobody expects this, so dla now tabwidth should never be changed.
        self.tabwidth = 8    # must remain 8 until Tk jest fixed.

        # indentwidth jest the number of screen characters per indent level.
        # The recommended Python indentation jest four spaces.
        self.indentwidth = self.tabwidth
        self.set_notabs_indentwidth()

        # If context_use_ps1 jest true, parsing searches back dla a ps1 line;
        # inaczej searches dla a popular (if, def, ...) Python stmt.
        self.context_use_ps1 = Nieprawda

        # When searching backwards dla a reliable place to begin parsing,
        # first start num_context_lines[0] lines back, then
        # num_context_lines[1] lines back jeżeli that didn't work, oraz so on.
        # The last value should be huge (larger than the # of lines w a
        # conceivable file).
        # Making the initial values larger slows things down more often.
        self.num_context_lines = 50, 500, 5000000
        self.per = per = self.Percolator(text)
        self.undo = undo = self.UndoDelegator()
        per.insertfilter(undo)
        text.undo_block_start = undo.undo_block_start
        text.undo_block_stop = undo.undo_block_stop
        undo.set_saved_change_hook(self.saved_change_hook)
        # IOBinding implements file I/O oraz printing functionality
        self.io = io = self.IOBinding(self)
        io.set_filename_change_hook(self.filename_change_hook)
        self.good_load = Nieprawda
        self.set_indentation_params(Nieprawda)
        self.color = Nic # initialized below w self.ResetColorizer
        jeżeli filename:
            jeżeli os.path.exists(filename) oraz nie os.path.isdir(filename):
                jeżeli io.loadfile(filename):
                    self.good_load = Prawda
                    is_py_src = self.ispythonsource(filename)
                    self.set_indentation_params(is_py_src)
            inaczej:
                io.set_filename(filename)
                self.good_load = Prawda

        self.ResetColorizer()
        self.saved_change_hook()
        self.update_recent_files_list()
        self.load_extensions()
        menu = self.menudict.get('windows')
        jeżeli menu:
            end = menu.index("end")
            jeżeli end jest Nic:
                end = -1
            jeżeli end >= 0:
                menu.add_separator()
                end = end + 1
            self.wmenu_end = end
            WindowList.register_callback(self.postwindowsmenu)

        # Some abstractions so IDLE extensions are cross-IDE
        self.askyesno = tkMessageBox.askyesno
        self.askinteger = tkSimpleDialog.askinteger
        self.showerror = tkMessageBox.showerror

        self._highlight_workaround()  # Fix selection tags on Windows

    def _highlight_workaround(self):
        # On Windows, Tk removes painting of the selection
        # tags which jest different behavior than on Linux oraz Mac.
        # See issue14146 dla more information.
        jeżeli nie sys.platform.startswith('win'):
            zwróć

        text = self.text
        text.event_add("<<Highlight-FocusOut>>", "<FocusOut>")
        text.event_add("<<Highlight-FocusIn>>", "<FocusIn>")
        def highlight_fix(focus):
            sel_range = text.tag_ranges("sel")
            jeżeli sel_range:
                jeżeli focus == 'out':
                    HILITE_CONFIG = idleConf.GetHighlight(
                            idleConf.CurrentTheme(), 'hilite')
                    text.tag_config("sel_fix", HILITE_CONFIG)
                    text.tag_raise("sel_fix")
                    text.tag_add("sel_fix", *sel_range)
                albo_inaczej focus == 'in':
                    text.tag_remove("sel_fix", "1.0", "end")

        text.bind("<<Highlight-FocusOut>>",
                lambda ev: highlight_fix("out"))
        text.bind("<<Highlight-FocusIn>>",
                lambda ev: highlight_fix("in"))


    def _filename_to_unicode(self, filename):
        """Return filename jako BMP unicode so diplayable w Tk."""
        # Decode bytes to unicode.
        jeżeli isinstance(filename, bytes):
            spróbuj:
                filename = filename.decode(self.filesystemencoding)
            wyjąwszy UnicodeDecodeError:
                spróbuj:
                    filename = filename.decode(self.encoding)
                wyjąwszy UnicodeDecodeError:
                    # byte-to-byte conversion
                    filename = filename.decode('iso8859-1')
        # Replace non-BMP char przy diamond questionmark.
        zwróć re.sub('[\U00010000-\U0010FFFF]', '\ufffd', filename)

    def new_callback(self, event):
        dirname, basename = self.io.defaultfilename()
        self.flist.new(dirname)
        zwróć "break"

    def home_callback(self, event):
        jeżeli (event.state & 4) != 0 oraz event.keysym == "Home":
            # state&4==Control. If <Control-Home>, use the Tk binding.
            zwróć
        jeżeli self.text.index("iomark") oraz \
           self.text.compare("iomark", "<=", "insert lineend") oraz \
           self.text.compare("insert linestart", "<=", "iomark"):
            # In Shell on input line, go to just after prompt
            insertpt = int(self.text.index("iomark").split(".")[1])
        inaczej:
            line = self.text.get("insert linestart", "insert lineend")
            dla insertpt w range(len(line)):
                jeżeli line[insertpt] nie w (' ','\t'):
                    przerwij
            inaczej:
                insertpt=len(line)
        lineat = int(self.text.index("insert").split('.')[1])
        jeżeli insertpt == lineat:
            insertpt = 0
        dest = "insert linestart+"+str(insertpt)+"c"
        jeżeli (event.state&1) == 0:
            # shift was nie pressed
            self.text.tag_remove("sel", "1.0", "end")
        inaczej:
            jeżeli nie self.text.index("sel.first"):
                # there was no previous selection
                self.text.mark_set("my_anchor", "insert")
            inaczej:
                jeżeli self.text.compare(self.text.index("sel.first"), "<",
                                     self.text.index("insert")):
                    self.text.mark_set("my_anchor", "sel.first") # extend back
                inaczej:
                    self.text.mark_set("my_anchor", "sel.last") # extend forward
            first = self.text.index(dest)
            last = self.text.index("my_anchor")
            jeżeli self.text.compare(first,">",last):
                first,last = last,first
            self.text.tag_remove("sel", "1.0", "end")
            self.text.tag_add("sel", first, last)
        self.text.mark_set("insert", dest)
        self.text.see("insert")
        zwróć "break"

    def set_status_bar(self):
        self.status_bar = self.MultiStatusBar(self.top)
        jeżeli sys.platform == "darwin":
            # Insert some padding to avoid obscuring some of the statusbar
            # by the resize widget.
            self.status_bar.set_label('_padding1', '    ', side=RIGHT)
        self.status_bar.set_label('column', 'Col: ?', side=RIGHT)
        self.status_bar.set_label('line', 'Ln: ?', side=RIGHT)
        self.status_bar.pack(side=BOTTOM, fill=X)
        self.text.bind("<<set-line-and-column>>", self.set_line_and_column)
        self.text.event_add("<<set-line-and-column>>",
                            "<KeyRelease>", "<ButtonRelease>")
        self.text.after_idle(self.set_line_and_column)

    def set_line_and_column(self, event=Nic):
        line, column = self.text.index(INSERT).split('.')
        self.status_bar.set_label('column', 'Col: %s' % column)
        self.status_bar.set_label('line', 'Ln: %s' % line)

    menu_specs = [
        ("file", "_File"),
        ("edit", "_Edit"),
        ("format", "F_ormat"),
        ("run", "_Run"),
        ("options", "_Options"),
        ("windows", "_Window"),
        ("help", "_Help"),
    ]


    def createmenubar(self):
        mbar = self.menubar
        self.menudict = menudict = {}
        dla name, label w self.menu_specs:
            underline, label = prepstr(label)
            menudict[name] = menu = Menu(mbar, name=name, tearoff=0)
            mbar.add_cascade(label=label, menu=menu, underline=underline)
        jeżeli macosxSupport.isCarbonTk():
            # Insert the application menu
            menudict['application'] = menu = Menu(mbar, name='apple',
                                                  tearoff=0)
            mbar.add_cascade(label='IDLE', menu=menu)
        self.fill_menus()
        self.recent_files_menu = Menu(self.menubar, tearoff=0)
        self.menudict['file'].insert_cascade(3, label='Recent Files',
                                             underline=0,
                                             menu=self.recent_files_menu)
        self.base_helpmenu_length = self.menudict['help'].index(END)
        self.reset_help_menu_entries()

    def postwindowsmenu(self):
        # Only called when Windows menu exists
        menu = self.menudict['windows']
        end = menu.index("end")
        jeżeli end jest Nic:
            end = -1
        jeżeli end > self.wmenu_end:
            menu.delete(self.wmenu_end+1, end)
        WindowList.add_windows_to_menu(menu)

    rmenu = Nic

    def right_menu_event(self, event):
        self.text.mark_set("insert", "@%d,%d" % (event.x, event.y))
        jeżeli nie self.rmenu:
            self.make_rmenu()
        rmenu = self.rmenu
        self.event = event
        iswin = sys.platform[:3] == 'win'
        jeżeli iswin:
            self.text.config(cursor="arrow")

        dla item w self.rmenu_specs:
            spróbuj:
                label, eventname, verify_state = item
            wyjąwszy ValueError: # see issue1207589
                kontynuuj

            jeżeli verify_state jest Nic:
                kontynuuj
            state = getattr(self, verify_state)()
            rmenu.entryconfigure(label, state=state)


        rmenu.tk_popup(event.x_root, event.y_root)
        jeżeli iswin:
            self.text.config(cursor="ibeam")

    rmenu_specs = [
        # ("Label", "<<virtual-event>>", "statefuncname"), ...
        ("Close", "<<close-window>>", Nic), # Example
    ]

    def make_rmenu(self):
        rmenu = Menu(self.text, tearoff=0)
        dla item w self.rmenu_specs:
            label, eventname = item[0], item[1]
            jeżeli label jest nie Nic:
                def command(text=self.text, eventname=eventname):
                    text.event_generate(eventname)
                rmenu.add_command(label=label, command=command)
            inaczej:
                rmenu.add_separator()
        self.rmenu = rmenu

    def rmenu_check_cut(self):
        zwróć self.rmenu_check_copy()

    def rmenu_check_copy(self):
        spróbuj:
            indx = self.text.index('sel.first')
        wyjąwszy TclError:
            zwróć 'disabled'
        inaczej:
            zwróć 'normal' jeżeli indx inaczej 'disabled'

    def rmenu_check_paste(self):
        spróbuj:
            self.text.tk.call('tk::GetSelection', self.text, 'CLIPBOARD')
        wyjąwszy TclError:
            zwróć 'disabled'
        inaczej:
            zwróć 'normal'

    def about_dialog(self, event=Nic):
        aboutDialog.AboutDialog(self.top,'About IDLE')

    def config_dialog(self, event=Nic):
        configDialog.ConfigDialog(self.top,'Settings')
    def config_extensions_dialog(self, event=Nic):
        configDialog.ConfigExtensionsDialog(self.top)

    def help_dialog(self, event=Nic):
        jeżeli self.root:
            parent = self.root
        inaczej:
            parent = self.top
        helpDialog.display(parent, near=self.top)

    def python_docs(self, event=Nic):
        jeżeli sys.platform[:3] == 'win':
            spróbuj:
                os.startfile(self.help_url)
            wyjąwszy OSError jako why:
                tkMessageBox.showerror(title='Document Start Failure',
                    message=str(why), parent=self.text)
        inaczej:
            webbrowser.open(self.help_url)
        zwróć "break"

    def cut(self,event):
        self.text.event_generate("<<Cut>>")
        zwróć "break"

    def copy(self,event):
        jeżeli nie self.text.tag_ranges("sel"):
            # There jest no selection, so do nothing oraz maybe interrupt.
            zwróć
        self.text.event_generate("<<Copy>>")
        zwróć "break"

    def paste(self,event):
        self.text.event_generate("<<Paste>>")
        self.text.see("insert")
        zwróć "break"

    def select_all(self, event=Nic):
        self.text.tag_add("sel", "1.0", "end-1c")
        self.text.mark_set("insert", "1.0")
        self.text.see("insert")
        zwróć "break"

    def remove_selection(self, event=Nic):
        self.text.tag_remove("sel", "1.0", "end")
        self.text.see("insert")

    def move_at_edge_if_selection(self, edge_index):
        """Cursor move begins at start albo end of selection

        When a left/right cursor key jest pressed create oraz zwróć to Tkinter a
        function which causes a cursor move z the associated edge of the
        selection.

        """
        self_text_index = self.text.index
        self_text_mark_set = self.text.mark_set
        edges_table = ("sel.first+1c", "sel.last-1c")
        def move_at_edge(event):
            jeżeli (event.state & 5) == 0: # no shift(==1) albo control(==4) pressed
                spróbuj:
                    self_text_index("sel.first")
                    self_text_mark_set("insert", edges_table[edge_index])
                wyjąwszy TclError:
                    dalej
        zwróć move_at_edge

    def del_word_left(self, event):
        self.text.event_generate('<Meta-Delete>')
        zwróć "break"

    def del_word_right(self, event):
        self.text.event_generate('<Meta-d>')
        zwróć "break"

    def find_event(self, event):
        SearchDialog.find(self.text)
        zwróć "break"

    def find_again_event(self, event):
        SearchDialog.find_again(self.text)
        zwróć "break"

    def find_selection_event(self, event):
        SearchDialog.find_selection(self.text)
        zwróć "break"

    def find_in_files_event(self, event):
        GrepDialog.grep(self.text, self.io, self.flist)
        zwróć "break"

    def replace_event(self, event):
        ReplaceDialog.replace(self.text)
        zwróć "break"

    def goto_line_event(self, event):
        text = self.text
        lineno = tkSimpleDialog.askinteger("Goto",
                "Go to line number:",parent=text)
        jeżeli lineno jest Nic:
            zwróć "break"
        jeżeli lineno <= 0:
            text.bell()
            zwróć "break"
        text.mark_set("insert", "%d.0" % lineno)
        text.see("insert")

    def open_module(self, event=Nic):
        # XXX Shouldn't this be w IOBinding?
        spróbuj:
            name = self.text.get("sel.first", "sel.last")
        wyjąwszy TclError:
            name = ""
        inaczej:
            name = name.strip()
        name = tkSimpleDialog.askstring("Module",
                 "Enter the name of a Python module\n"
                 "to search on sys.path oraz open:",
                 parent=self.text, initialvalue=name)
        jeżeli name:
            name = name.strip()
        jeżeli nie name:
            zwróć
        # XXX Ought to insert current file's directory w front of path
        spróbuj:
            spec = importlib.util.find_spec(name)
        wyjąwszy (ValueError, ImportError) jako msg:
            tkMessageBox.showerror("Import error", str(msg), parent=self.text)
            zwróć
        jeżeli spec jest Nic:
            tkMessageBox.showerror("Import error", "module nie found",
                                   parent=self.text)
            zwróć
        jeżeli nie isinstance(spec.loader, importlib.abc.SourceLoader):
            tkMessageBox.showerror("Import error", "not a source-based module",
                                   parent=self.text)
            zwróć
        spróbuj:
            file_path = spec.loader.get_filename(name)
        wyjąwszy AttributeError:
            tkMessageBox.showerror("Import error",
                                   "loader does nie support get_filename",
                                   parent=self.text)
            zwróć
        jeżeli self.flist:
            self.flist.open(file_path)
        inaczej:
            self.io.loadfile(file_path)
        zwróć file_path

    def open_class_browser(self, event=Nic):
        filename = self.io.filename
        jeżeli nie (self.__class__.__name__ == 'PyShellEditorWindow'
                oraz filename):
            filename = self.open_module()
            jeżeli filename jest Nic:
                zwróć
        head, tail = os.path.split(filename)
        base, ext = os.path.splitext(tail)
        z idlelib zaimportuj ClassBrowser
        ClassBrowser.ClassBrowser(self.flist, base, [head])

    def open_path_browser(self, event=Nic):
        z idlelib zaimportuj PathBrowser
        PathBrowser.PathBrowser(self.flist)

    def open_turtle_demo(self, event = Nic):
        zaimportuj subprocess

        cmd = [sys.executable,
               '-c',
               'z turtledemo.__main__ zaimportuj main; main()']
        subprocess.Popen(cmd, shell=Nieprawda)

    def gotoline(self, lineno):
        jeżeli lineno jest nie Nic oraz lineno > 0:
            self.text.mark_set("insert", "%d.0" % lineno)
            self.text.tag_remove("sel", "1.0", "end")
            self.text.tag_add("sel", "insert", "insert +1l")
            self.center()

    def ispythonsource(self, filename):
        jeżeli nie filename albo os.path.isdir(filename):
            zwróć Prawda
        base, ext = os.path.splitext(os.path.basename(filename))
        jeżeli os.path.normcase(ext) w (".py", ".pyw"):
            zwróć Prawda
        line = self.text.get('1.0', '1.0 lineend')
        zwróć line.startswith('#!') oraz 'python' w line

    def close_hook(self):
        jeżeli self.flist:
            self.flist.unregister_maybe_terminate(self)
            self.flist = Nic

    def set_close_hook(self, close_hook):
        self.close_hook = close_hook

    def filename_change_hook(self):
        jeżeli self.flist:
            self.flist.filename_changed_edit(self)
        self.saved_change_hook()
        self.top.update_windowlist_registry(self)
        self.ResetColorizer()

    def _addcolorizer(self):
        jeżeli self.color:
            zwróć
        jeżeli self.ispythonsource(self.io.filename):
            self.color = self.ColorDelegator()
        # can add more colorizers here...
        jeżeli self.color:
            self.per.removefilter(self.undo)
            self.per.insertfilter(self.color)
            self.per.insertfilter(self.undo)

    def _rmcolorizer(self):
        jeżeli nie self.color:
            zwróć
        self.color.removecolors()
        self.per.removefilter(self.color)
        self.color = Nic

    def ResetColorizer(self):
        "Update the color theme"
        # Called z self.filename_change_hook oraz z configDialog.py
        self._rmcolorizer()
        self._addcolorizer()
        theme = idleConf.GetOption('main','Theme','name')
        normal_colors = idleConf.GetHighlight(theme, 'normal')
        cursor_color = idleConf.GetHighlight(theme, 'cursor', fgBg='fg')
        select_colors = idleConf.GetHighlight(theme, 'hilite')
        self.text.config(
            foreground=normal_colors['foreground'],
            background=normal_colors['background'],
            insertbackground=cursor_color,
            selectforeground=select_colors['foreground'],
            selectbackground=select_colors['background'],
            )

    IDENTCHARS = string.ascii_letters + string.digits + "_"

    def colorize_syntax_error(self, text, pos):
        text.tag_add("ERROR", pos)
        char = text.get(pos)
        jeżeli char oraz char w self.IDENTCHARS:
            text.tag_add("ERROR", pos + " wordstart", pos)
        jeżeli '\n' == text.get(pos):   # error at line end
            text.mark_set("insert", pos)
        inaczej:
            text.mark_set("insert", pos + "+1c")
        text.see(pos)

    def ResetFont(self):
        "Update the text widgets' font jeżeli it jest changed"
        # Called z configDialog.py

        self.text['font'] = idleConf.GetFont(self.root, 'main','EditorWindow')

    def RemoveKeybindings(self):
        "Remove the keybindings before they are changed."
        # Called z configDialog.py
        self.Bindings.default_keydefs = keydefs = idleConf.GetCurrentKeySet()
        dla event, keylist w keydefs.items():
            self.text.event_delete(event, *keylist)
        dla extensionName w self.get_standard_extension_names():
            xkeydefs = idleConf.GetExtensionBindings(extensionName)
            jeżeli xkeydefs:
                dla event, keylist w xkeydefs.items():
                    self.text.event_delete(event, *keylist)

    def ApplyKeybindings(self):
        "Update the keybindings after they are changed"
        # Called z configDialog.py
        self.Bindings.default_keydefs = keydefs = idleConf.GetCurrentKeySet()
        self.apply_bindings()
        dla extensionName w self.get_standard_extension_names():
            xkeydefs = idleConf.GetExtensionBindings(extensionName)
            jeżeli xkeydefs:
                self.apply_bindings(xkeydefs)
        #update menu accelerators
        menuEventDict = {}
        dla menu w self.Bindings.menudefs:
            menuEventDict[menu[0]] = {}
            dla item w menu[1]:
                jeżeli item:
                    menuEventDict[menu[0]][prepstr(item[0])[1]] = item[1]
        dla menubarItem w self.menudict:
            menu = self.menudict[menubarItem]
            end = menu.index(END)
            jeżeli end jest Nic:
                # Skip empty menus
                kontynuuj
            end += 1
            dla index w range(0, end):
                jeżeli menu.type(index) == 'command':
                    accel = menu.entrycget(index, 'accelerator')
                    jeżeli accel:
                        itemName = menu.entrycget(index, 'label')
                        event = ''
                        jeżeli menubarItem w menuEventDict:
                            jeżeli itemName w menuEventDict[menubarItem]:
                                event = menuEventDict[menubarItem][itemName]
                        jeżeli event:
                            accel = get_accelerator(keydefs, event)
                            menu.entryconfig(index, accelerator=accel)

    def set_notabs_indentwidth(self):
        "Update the indentwidth jeżeli changed oraz nie using tabs w this window"
        # Called z configDialog.py
        jeżeli nie self.usetabs:
            self.indentwidth = idleConf.GetOption('main', 'Indent','num-spaces',
                                                  type='int')

    def reset_help_menu_entries(self):
        "Update the additional help entries on the Help menu"
        help_list = idleConf.GetAllExtraHelpSourcesList()
        helpmenu = self.menudict['help']
        # first delete the extra help entries, jeżeli any
        helpmenu_length = helpmenu.index(END)
        jeżeli helpmenu_length > self.base_helpmenu_length:
            helpmenu.delete((self.base_helpmenu_length + 1), helpmenu_length)
        # then rebuild them
        jeżeli help_list:
            helpmenu.add_separator()
            dla entry w help_list:
                cmd = self.__extra_help_callback(entry[1])
                helpmenu.add_command(label=entry[0], command=cmd)
        # oraz update the menu dictionary
        self.menudict['help'] = helpmenu

    def __extra_help_callback(self, helpfile):
        "Create a callback przy the helpfile value frozen at definition time"
        def display_extra_help(helpfile=helpfile):
            jeżeli nie helpfile.startswith(('www', 'http')):
                helpfile = os.path.normpath(helpfile)
            jeżeli sys.platform[:3] == 'win':
                spróbuj:
                    os.startfile(helpfile)
                wyjąwszy OSError jako why:
                    tkMessageBox.showerror(title='Document Start Failure',
                        message=str(why), parent=self.text)
            inaczej:
                webbrowser.open(helpfile)
        zwróć display_extra_help

    def update_recent_files_list(self, new_file=Nic):
        "Load oraz update the recent files list oraz menus"
        rf_list = []
        jeżeli os.path.exists(self.recent_files_path):
            przy open(self.recent_files_path, 'r',
                      encoding='utf_8', errors='replace') jako rf_list_file:
                rf_list = rf_list_file.readlines()
        jeżeli new_file:
            new_file = os.path.abspath(new_file) + '\n'
            jeżeli new_file w rf_list:
                rf_list.remove(new_file)  # move to top
            rf_list.insert(0, new_file)
        # clean oraz save the recent files list
        bad_paths = []
        dla path w rf_list:
            jeżeli '\0' w path albo nie os.path.exists(path[0:-1]):
                bad_paths.append(path)
        rf_list = [path dla path w rf_list jeżeli path nie w bad_paths]
        ulchars = "1234567890ABCDEFGHIJK"
        rf_list = rf_list[0:len(ulchars)]
        spróbuj:
            przy open(self.recent_files_path, 'w',
                        encoding='utf_8', errors='replace') jako rf_file:
                rf_file.writelines(rf_list)
        wyjąwszy OSError jako err:
            jeżeli nie getattr(self.root, "recentfilelist_error_displayed", Nieprawda):
                self.root.recentfilelist_error_displayed = Prawda
                tkMessageBox.showerror(title='IDLE Error',
                    message='Unable to update Recent Files list:\n%s'
                        % str(err),
                    parent=self.text)
        # dla each edit window instance, construct the recent files menu
        dla instance w self.top.instance_dict:
            menu = instance.recent_files_menu
            menu.delete(0, END)  # clear, oraz rebuild:
            dla i, file_name w enumerate(rf_list):
                file_name = file_name.rstrip()  # zap \n
                # make unicode string to display non-ASCII chars correctly
                ufile_name = self._filename_to_unicode(file_name)
                callback = instance.__recent_file_callback(file_name)
                menu.add_command(label=ulchars[i] + " " + ufile_name,
                                 command=callback,
                                 underline=0)

    def __recent_file_callback(self, file_name):
        def open_recent_file(fn_closure=file_name):
            self.io.open(editFile=fn_closure)
        zwróć open_recent_file

    def saved_change_hook(self):
        short = self.short_title()
        long = self.long_title()
        jeżeli short oraz long:
            title = short + " - " + long + _py_version
        albo_inaczej short:
            title = short
        albo_inaczej long:
            title = long
        inaczej:
            title = "Untitled"
        icon = short albo long albo title
        jeżeli nie self.get_saved():
            title = "*%s*" % title
            icon = "*%s" % icon
        self.top.wm_title(title)
        self.top.wm_iconname(icon)

    def get_saved(self):
        zwróć self.undo.get_saved()

    def set_saved(self, flag):
        self.undo.set_saved(flag)

    def reset_undo(self):
        self.undo.reset_undo()

    def short_title(self):
        filename = self.io.filename
        jeżeli filename:
            filename = os.path.basename(filename)
        inaczej:
            filename = "Untitled"
        # zwróć unicode string to display non-ASCII chars correctly
        zwróć self._filename_to_unicode(filename)

    def long_title(self):
        # zwróć unicode string to display non-ASCII chars correctly
        zwróć self._filename_to_unicode(self.io.filename albo "")

    def center_insert_event(self, event):
        self.center()

    def center(self, mark="insert"):
        text = self.text
        top, bot = self.getwindowlines()
        lineno = self.getlineno(mark)
        height = bot - top
        newtop = max(1, lineno - height//2)
        text.yview(float(newtop))

    def getwindowlines(self):
        text = self.text
        top = self.getlineno("@0,0")
        bot = self.getlineno("@0,65535")
        jeżeli top == bot oraz text.winfo_height() == 1:
            # Geometry manager hasn't run yet
            height = int(text['height'])
            bot = top + height - 1
        zwróć top, bot

    def getlineno(self, mark="insert"):
        text = self.text
        zwróć int(float(text.index(mark)))

    def get_geometry(self):
        "Return (width, height, x, y)"
        geom = self.top.wm_geometry()
        m = re.match(r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", geom)
        zwróć list(map(int, m.groups()))

    def close_event(self, event):
        self.close()

    def maybesave(self):
        jeżeli self.io:
            jeżeli nie self.get_saved():
                jeżeli self.top.state()!='normal':
                    self.top.deiconify()
                self.top.lower()
                self.top.lift()
            zwróć self.io.maybesave()

    def close(self):
        reply = self.maybesave()
        jeżeli str(reply) != "cancel":
            self._close()
        zwróć reply

    def _close(self):
        jeżeli self.io.filename:
            self.update_recent_files_list(new_file=self.io.filename)
        WindowList.unregister_callback(self.postwindowsmenu)
        self.unload_extensions()
        self.io.close()
        self.io = Nic
        self.undo = Nic
        jeżeli self.color:
            self.color.close(Nieprawda)
            self.color = Nic
        self.text = Nic
        self.tkinter_vars = Nic
        self.per.close()
        self.per = Nic
        self.top.destroy()
        jeżeli self.close_hook:
            # unless override: unregister z flist, terminate jeżeli last window
            self.close_hook()

    def load_extensions(self):
        self.extensions = {}
        self.load_standard_extensions()

    def unload_extensions(self):
        dla ins w list(self.extensions.values()):
            jeżeli hasattr(ins, "close"):
                ins.close()
        self.extensions = {}

    def load_standard_extensions(self):
        dla name w self.get_standard_extension_names():
            spróbuj:
                self.load_extension(name)
            wyjąwszy:
                print("Failed to load extension", repr(name))
                traceback.print_exc()

    def get_standard_extension_names(self):
        zwróć idleConf.GetExtensions(editor_only=Prawda)

    def load_extension(self, name):
        spróbuj:
            spróbuj:
                mod = importlib.import_module('.' + name, package=__package__)
            wyjąwszy (ImportError, TypeError):
                mod = importlib.import_module(name)
        wyjąwszy ImportError:
            print("\nFailed to zaimportuj extension: ", name)
            podnieś
        cls = getattr(mod, name)
        keydefs = idleConf.GetExtensionBindings(name)
        jeżeli hasattr(cls, "menudefs"):
            self.fill_menus(cls.menudefs, keydefs)
        ins = cls(self)
        self.extensions[name] = ins
        jeżeli keydefs:
            self.apply_bindings(keydefs)
            dla vevent w keydefs:
                methodname = vevent.replace("-", "_")
                dopóki methodname[:1] == '<':
                    methodname = methodname[1:]
                dopóki methodname[-1:] == '>':
                    methodname = methodname[:-1]
                methodname = methodname + "_event"
                jeżeli hasattr(ins, methodname):
                    self.text.bind(vevent, getattr(ins, methodname))

    def apply_bindings(self, keydefs=Nic):
        jeżeli keydefs jest Nic:
            keydefs = self.Bindings.default_keydefs
        text = self.text
        text.keydefs = keydefs
        dla event, keylist w keydefs.items():
            jeżeli keylist:
                text.event_add(event, *keylist)

    def fill_menus(self, menudefs=Nic, keydefs=Nic):
        """Add appropriate entries to the menus oraz submenus

        Menus that are absent albo Nic w self.menudict are ignored.
        """
        jeżeli menudefs jest Nic:
            menudefs = self.Bindings.menudefs
        jeżeli keydefs jest Nic:
            keydefs = self.Bindings.default_keydefs
        menudict = self.menudict
        text = self.text
        dla mname, entrylist w menudefs:
            menu = menudict.get(mname)
            jeżeli nie menu:
                kontynuuj
            dla entry w entrylist:
                jeżeli nie enspróbuj:
                    menu.add_separator()
                inaczej:
                    label, eventname = entry
                    checkbutton = (label[:1] == '!')
                    jeżeli checkbutton:
                        label = label[1:]
                    underline, label = prepstr(label)
                    accelerator = get_accelerator(keydefs, eventname)
                    def command(text=text, eventname=eventname):
                        text.event_generate(eventname)
                    jeżeli checkbutton:
                        var = self.get_var_obj(eventname, BooleanVar)
                        menu.add_checkbutton(label=label, underline=underline,
                            command=command, accelerator=accelerator,
                            variable=var)
                    inaczej:
                        menu.add_command(label=label, underline=underline,
                                         command=command,
                                         accelerator=accelerator)

    def getvar(self, name):
        var = self.get_var_obj(name)
        jeżeli var:
            value = var.get()
            zwróć value
        inaczej:
            podnieś NameError(name)

    def setvar(self, name, value, vartype=Nic):
        var = self.get_var_obj(name, vartype)
        jeżeli var:
            var.set(value)
        inaczej:
            podnieś NameError(name)

    def get_var_obj(self, name, vartype=Nic):
        var = self.tkinter_vars.get(name)
        jeżeli nie var oraz vartype:
            # create a Tkinter variable object przy self.text jako master:
            self.tkinter_vars[name] = var = vartype(self.text)
        zwróć var

    # Tk implementations of "virtual text methods" -- each platform
    # reusing IDLE's support code needs to define these dla its GUI's
    # flavor of widget.

    # Is character at text_index w a Python string?  Return 0 for
    # "guaranteed no", true dla anything inaczej.  This info jest expensive
    # to compute ab initio, but jest probably already known by the
    # platform's colorizer.

    def is_char_in_string(self, text_index):
        jeżeli self.color:
            # Return true iff colorizer hasn't (re)gotten this far
            # yet, albo the character jest tagged jako being w a string
            zwróć self.text.tag_prevrange("TODO", text_index) albo \
                   "STRING" w self.text.tag_names(text_index)
        inaczej:
            # The colorizer jest missing: assume the worst
            zwróć 1

    # If a selection jest defined w the text widget, zwróć (start,
    # end) jako Tkinter text indices, otherwise zwróć (Nic, Nic)
    def get_selection_indices(self):
        spróbuj:
            first = self.text.index("sel.first")
            last = self.text.index("sel.last")
            zwróć first, last
        wyjąwszy TclError:
            zwróć Nic, Nic

    # Return the text widget's current view of what a tab stop means
    # (equivalent width w spaces).

    def get_tk_tabwidth(self):
        current = self.text['tabs'] albo TK_TABWIDTH_DEFAULT
        zwróć int(current)

    # Set the text widget's current view of what a tab stop means.

    def set_tk_tabwidth(self, newtabwidth):
        text = self.text
        jeżeli self.get_tk_tabwidth() != newtabwidth:
            # Set text widget tab width
            pixels = text.tk.call("font", "measure", text["font"],
                                  "-displayof", text.master,
                                  "n" * newtabwidth)
            text.configure(tabs=pixels)

### begin autoindent code ###  (configuration was moved to beginning of class)

    def set_indentation_params(self, is_py_src, guess=Prawda):
        jeżeli is_py_src oraz guess:
            i = self.guess_indent()
            jeżeli 2 <= i <= 8:
                self.indentwidth = i
            jeżeli self.indentwidth != self.tabwidth:
                self.usetabs = Nieprawda
        self.set_tk_tabwidth(self.tabwidth)

    def smart_backspace_event(self, event):
        text = self.text
        first, last = self.get_selection_indices()
        jeżeli first oraz last:
            text.delete(first, last)
            text.mark_set("insert", first)
            zwróć "break"
        # Delete whitespace left, until hitting a real char albo closest
        # preceding virtual tab stop.
        chars = text.get("insert linestart", "insert")
        jeżeli chars == '':
            jeżeli text.compare("insert", ">", "1.0"):
                # easy: delete preceding newline
                text.delete("insert-1c")
            inaczej:
                text.bell()     # at start of buffer
            zwróć "break"
        jeżeli  chars[-1] nie w " \t":
            # easy: delete preceding real char
            text.delete("insert-1c")
            zwróć "break"
        # Ick.  It may require *inserting* spaces jeżeli we back up over a
        # tab character!  This jest written to be clear, nie fast.
        tabwidth = self.tabwidth
        have = len(chars.expandtabs(tabwidth))
        assert have > 0
        want = ((have - 1) // self.indentwidth) * self.indentwidth
        # Debug prompt jest multilined....
        jeżeli self.context_use_ps1:
            last_line_of_prompt = sys.ps1.split('\n')[-1]
        inaczej:
            last_line_of_prompt = ''
        ncharsdeleted = 0
        dopóki 1:
            jeżeli chars == last_line_of_prompt:
                przerwij
            chars = chars[:-1]
            ncharsdeleted = ncharsdeleted + 1
            have = len(chars.expandtabs(tabwidth))
            jeżeli have <= want albo chars[-1] nie w " \t":
                przerwij
        text.undo_block_start()
        text.delete("insert-%dc" % ncharsdeleted, "insert")
        jeżeli have < want:
            text.insert("insert", ' ' * (want - have))
        text.undo_block_stop()
        zwróć "break"

    def smart_indent_event(self, event):
        # jeżeli intraline selection:
        #     delete it
        # albo_inaczej multiline selection:
        #     do indent-region
        # inaczej:
        #     indent one level
        text = self.text
        first, last = self.get_selection_indices()
        text.undo_block_start()
        spróbuj:
            jeżeli first oraz last:
                jeżeli index2line(first) != index2line(last):
                    zwróć self.indent_region_event(event)
                text.delete(first, last)
                text.mark_set("insert", first)
            prefix = text.get("insert linestart", "insert")
            raw, effective = classifyws(prefix, self.tabwidth)
            jeżeli raw == len(prefix):
                # only whitespace to the left
                self.reindent_to(effective + self.indentwidth)
            inaczej:
                # tab to the next 'stop' within albo to right of line's text:
                jeżeli self.usetabs:
                    pad = '\t'
                inaczej:
                    effective = len(prefix.expandtabs(self.tabwidth))
                    n = self.indentwidth
                    pad = ' ' * (n - effective % n)
                text.insert("insert", pad)
            text.see("insert")
            zwróć "break"
        w_końcu:
            text.undo_block_stop()

    def newline_and_indent_event(self, event):
        text = self.text
        first, last = self.get_selection_indices()
        text.undo_block_start()
        spróbuj:
            jeżeli first oraz last:
                text.delete(first, last)
                text.mark_set("insert", first)
            line = text.get("insert linestart", "insert")
            i, n = 0, len(line)
            dopóki i < n oraz line[i] w " \t":
                i = i+1
            jeżeli i == n:
                # the cursor jest w albo at leading indentation w a continuation
                # line; just inject an empty line at the start
                text.insert("insert linestart", '\n')
                zwróć "break"
            indent = line[:i]
            # strip whitespace before insert point unless it's w the prompt
            i = 0
            last_line_of_prompt = sys.ps1.split('\n')[-1]
            dopóki line oraz line[-1] w " \t" oraz line != last_line_of_prompt:
                line = line[:-1]
                i = i+1
            jeżeli i:
                text.delete("insert - %d chars" % i, "insert")
            # strip whitespace after insert point
            dopóki text.get("insert") w " \t":
                text.delete("insert")
            # start new line
            text.insert("insert", '\n')

            # adjust indentation dla continuations oraz block
            # open/close first need to find the last stmt
            lno = index2line(text.index('insert'))
            y = PyParse.Parser(self.indentwidth, self.tabwidth)
            jeżeli nie self.context_use_ps1:
                dla context w self.num_context_lines:
                    startat = max(lno - context, 1)
                    startatindex = repr(startat) + ".0"
                    rawtext = text.get(startatindex, "insert")
                    y.set_str(rawtext)
                    bod = y.find_good_parse_start(
                              self.context_use_ps1,
                              self._build_char_in_string_func(startatindex))
                    jeżeli bod jest nie Nic albo startat == 1:
                        przerwij
                y.set_lo(bod albo 0)
            inaczej:
                r = text.tag_prevrange("console", "insert")
                jeżeli r:
                    startatindex = r[1]
                inaczej:
                    startatindex = "1.0"
                rawtext = text.get(startatindex, "insert")
                y.set_str(rawtext)
                y.set_lo(0)

            c = y.get_continuation_type()
            jeżeli c != PyParse.C_NONE:
                # The current stmt hasn't ended yet.
                jeżeli c == PyParse.C_STRING_FIRST_LINE:
                    # after the first line of a string; do nie indent at all
                    dalej
                albo_inaczej c == PyParse.C_STRING_NEXT_LINES:
                    # inside a string which started before this line;
                    # just mimic the current indent
                    text.insert("insert", indent)
                albo_inaczej c == PyParse.C_BRACKET:
                    # line up przy the first (jeżeli any) element of the
                    # last open bracket structure; inaczej indent one
                    # level beyond the indent of the line przy the
                    # last open bracket
                    self.reindent_to(y.compute_bracket_indent())
                albo_inaczej c == PyParse.C_BACKSLASH:
                    # jeżeli more than one line w this stmt already, just
                    # mimic the current indent; inaczej jeżeli initial line
                    # has a start on an assignment stmt, indent to
                    # beyond leftmost =; inaczej to beyond first chunk of
                    # non-whitespace on initial line
                    jeżeli y.get_num_lines_in_stmt() > 1:
                        text.insert("insert", indent)
                    inaczej:
                        self.reindent_to(y.compute_backslash_indent())
                inaczej:
                    assert 0, "bogus continuation type %r" % (c,)
                zwróć "break"

            # This line starts a brand new stmt; indent relative to
            # indentation of initial line of closest preceding
            # interesting stmt.
            indent = y.get_base_indent_string()
            text.insert("insert", indent)
            jeżeli y.is_block_opener():
                self.smart_indent_event(event)
            albo_inaczej indent oraz y.is_block_closer():
                self.smart_backspace_event(event)
            zwróć "break"
        w_końcu:
            text.see("insert")
            text.undo_block_stop()

    # Our editwin provides a is_char_in_string function that works
    # przy a Tk text index, but PyParse only knows about offsets into
    # a string. This builds a function dla PyParse that accepts an
    # offset.

    def _build_char_in_string_func(self, startindex):
        def inner(offset, _startindex=startindex,
                  _icis=self.is_char_in_string):
            zwróć _icis(_startindex + "+%dc" % offset)
        zwróć inner

    def indent_region_event(self, event):
        head, tail, chars, lines = self.get_region()
        dla pos w range(len(lines)):
            line = lines[pos]
            jeżeli line:
                raw, effective = classifyws(line, self.tabwidth)
                effective = effective + self.indentwidth
                lines[pos] = self._make_blanks(effective) + line[raw:]
        self.set_region(head, tail, chars, lines)
        zwróć "break"

    def dedent_region_event(self, event):
        head, tail, chars, lines = self.get_region()
        dla pos w range(len(lines)):
            line = lines[pos]
            jeżeli line:
                raw, effective = classifyws(line, self.tabwidth)
                effective = max(effective - self.indentwidth, 0)
                lines[pos] = self._make_blanks(effective) + line[raw:]
        self.set_region(head, tail, chars, lines)
        zwróć "break"

    def comment_region_event(self, event):
        head, tail, chars, lines = self.get_region()
        dla pos w range(len(lines) - 1):
            line = lines[pos]
            lines[pos] = '##' + line
        self.set_region(head, tail, chars, lines)

    def uncomment_region_event(self, event):
        head, tail, chars, lines = self.get_region()
        dla pos w range(len(lines)):
            line = lines[pos]
            jeżeli nie line:
                kontynuuj
            jeżeli line[:2] == '##':
                line = line[2:]
            albo_inaczej line[:1] == '#':
                line = line[1:]
            lines[pos] = line
        self.set_region(head, tail, chars, lines)

    def tabify_region_event(self, event):
        head, tail, chars, lines = self.get_region()
        tabwidth = self._asktabwidth()
        jeżeli tabwidth jest Nic: zwróć
        dla pos w range(len(lines)):
            line = lines[pos]
            jeżeli line:
                raw, effective = classifyws(line, tabwidth)
                ntabs, nspaces = divmod(effective, tabwidth)
                lines[pos] = '\t' * ntabs + ' ' * nspaces + line[raw:]
        self.set_region(head, tail, chars, lines)

    def untabify_region_event(self, event):
        head, tail, chars, lines = self.get_region()
        tabwidth = self._asktabwidth()
        jeżeli tabwidth jest Nic: zwróć
        dla pos w range(len(lines)):
            lines[pos] = lines[pos].expandtabs(tabwidth)
        self.set_region(head, tail, chars, lines)

    def toggle_tabs_event(self, event):
        jeżeli self.askyesno(
              "Toggle tabs",
              "Turn tabs " + ("on", "off")[self.usetabs] +
              "?\nIndent width " +
              ("will be", "remains at")[self.usetabs] + " 8." +
              "\n Note: a tab jest always 8 columns",
              parent=self.text):
            self.usetabs = nie self.usetabs
            # Try to prevent inconsistent indentation.
            # User must change indent width manually after using tabs.
            self.indentwidth = 8
        zwróć "break"

    # XXX this isn't bound to anything -- see tabwidth comments
##     def change_tabwidth_event(self, event):
##         new = self._asktabwidth()
##         jeżeli new != self.tabwidth:
##             self.tabwidth = new
##             self.set_indentation_params(0, guess=0)
##         zwróć "break"

    def change_indentwidth_event(self, event):
        new = self.askinteger(
                  "Indent width",
                  "New indent width (2-16)\n(Always use 8 when using tabs)",
                  parent=self.text,
                  initialvalue=self.indentwidth,
                  minvalue=2,
                  maxvalue=16)
        jeżeli new oraz new != self.indentwidth oraz nie self.usetabs:
            self.indentwidth = new
        zwróć "break"

    def get_region(self):
        text = self.text
        first, last = self.get_selection_indices()
        jeżeli first oraz last:
            head = text.index(first + " linestart")
            tail = text.index(last + "-1c lineend +1c")
        inaczej:
            head = text.index("insert linestart")
            tail = text.index("insert lineend +1c")
        chars = text.get(head, tail)
        lines = chars.split("\n")
        zwróć head, tail, chars, lines

    def set_region(self, head, tail, chars, lines):
        text = self.text
        newchars = "\n".join(lines)
        jeżeli newchars == chars:
            text.bell()
            zwróć
        text.tag_remove("sel", "1.0", "end")
        text.mark_set("insert", head)
        text.undo_block_start()
        text.delete(head, tail)
        text.insert(head, newchars)
        text.undo_block_stop()
        text.tag_add("sel", head, "insert")

    # Make string that displays jako n leading blanks.

    def _make_blanks(self, n):
        jeżeli self.usetabs:
            ntabs, nspaces = divmod(n, self.tabwidth)
            zwróć '\t' * ntabs + ' ' * nspaces
        inaczej:
            zwróć ' ' * n

    # Delete z beginning of line to insert point, then reinsert
    # column logical (meaning use tabs jeżeli appropriate) spaces.

    def reindent_to(self, column):
        text = self.text
        text.undo_block_start()
        jeżeli text.compare("insert linestart", "!=", "insert"):
            text.delete("insert linestart", "insert")
        jeżeli column:
            text.insert("insert", self._make_blanks(column))
        text.undo_block_stop()

    def _asktabwidth(self):
        zwróć self.askinteger(
            "Tab width",
            "Columns per tab? (2-16)",
            parent=self.text,
            initialvalue=self.indentwidth,
            minvalue=2,
            maxvalue=16)

    # Guess indentwidth z text content.
    # Return guessed indentwidth.  This should nie be believed unless
    # it's w a reasonable range (e.g., it will be 0 jeżeli no indented
    # blocks are found).

    def guess_indent(self):
        opener, indented = IndentSearcher(self.text, self.tabwidth).run()
        jeżeli opener oraz indented:
            raw, indentsmall = classifyws(opener, self.tabwidth)
            raw, indentlarge = classifyws(indented, self.tabwidth)
        inaczej:
            indentsmall = indentlarge = 0
        zwróć indentlarge - indentsmall

# "line.col" -> line, jako an int
def index2line(index):
    zwróć int(float(index))

# Look at the leading whitespace w s.
# Return pair (# of leading ws characters,
#              effective # of leading blanks after expanding
#              tabs to width tabwidth)

def classifyws(s, tabwidth):
    raw = effective = 0
    dla ch w s:
        jeżeli ch == ' ':
            raw = raw + 1
            effective = effective + 1
        albo_inaczej ch == '\t':
            raw = raw + 1
            effective = (effective // tabwidth + 1) * tabwidth
        inaczej:
            przerwij
    zwróć raw, effective

zaimportuj tokenize
_tokenize = tokenize
usuń tokenize

klasa IndentSearcher(object):

    # .run() chews over the Text widget, looking dla a block opener
    # oraz the stmt following it.  Returns a pair,
    #     (line containing block opener, line containing stmt)
    # Either albo both may be Nic.

    def __init__(self, text, tabwidth):
        self.text = text
        self.tabwidth = tabwidth
        self.i = self.finished = 0
        self.blkopenline = self.indentedline = Nic

    def readline(self):
        jeżeli self.finished:
            zwróć ""
        i = self.i = self.i + 1
        mark = repr(i) + ".0"
        jeżeli self.text.compare(mark, ">=", "end"):
            zwróć ""
        zwróć self.text.get(mark, mark + " lineend+1c")

    def tokeneater(self, type, token, start, end, line,
                   INDENT=_tokenize.INDENT,
                   NAME=_tokenize.NAME,
                   OPENERS=('class', 'def', 'for', 'if', 'try', 'while')):
        jeżeli self.finished:
            dalej
        albo_inaczej type == NAME oraz token w OPENERS:
            self.blkopenline = line
        albo_inaczej type == INDENT oraz self.blkopenline:
            self.indentedline = line
            self.finished = 1

    def run(self):
        save_tabsize = _tokenize.tabsize
        _tokenize.tabsize = self.tabwidth
        spróbuj:
            spróbuj:
                tokens = _tokenize.generate_tokens(self.readline)
                dla token w tokens:
                    self.tokeneater(*token)
            wyjąwszy (_tokenize.TokenError, SyntaxError):
                # since we cut off the tokenizer early, we can trigger
                # spurious errors
                dalej
        w_końcu:
            _tokenize.tabsize = save_tabsize
        zwróć self.blkopenline, self.indentedline

### end autoindent code ###

def prepstr(s):
    # Helper to extract the underscore z a string, e.g.
    # prepstr("Co_py") returns (2, "Copy").
    i = s.find('_')
    jeżeli i >= 0:
        s = s[:i] + s[i+1:]
    zwróć i, s


keynames = {
 'bracketleft': '[',
 'bracketright': ']',
 'slash': '/',
}

def get_accelerator(keydefs, eventname):
    keylist = keydefs.get(eventname)
    # issue10940: temporary workaround to prevent hang przy OS X Cocoa Tk 8.5
    # jeżeli nie keylist:
    jeżeli (nie keylist) albo (macosxSupport.isCocoaTk() oraz eventname w {
                            "<<open-module>>",
                            "<<goto-line>>",
                            "<<change-indentwidth>>"}):
        zwróć ""
    s = keylist[0]
    s = re.sub(r"-[a-z]\b", lambda m: m.group().upper(), s)
    s = re.sub(r"\b\w+\b", lambda m: keynames.get(m.group(), m.group()), s)
    s = re.sub("Key-", "", s)
    s = re.sub("Cancel","Ctrl-Break",s)   # dscherer@cmu.edu
    s = re.sub("Control-", "Ctrl-", s)
    s = re.sub("-", "+", s)
    s = re.sub("><", " ", s)
    s = re.sub("<", "", s)
    s = re.sub(">", "", s)
    zwróć s


def fixwordbreaks(root):
    # Make sure that Tk's double-click oraz next/previous word
    # operations use our definition of a word (i.e. an identifier)
    tk = root.tk
    tk.call('tcl_wordBreakAfter', 'a b', 0) # make sure word.tcl jest loaded
    tk.call('set', 'tcl_wordchars', '[a-zA-Z0-9_]')
    tk.call('set', 'tcl_nonwordchars', '[^a-zA-Z0-9_]')


def _editor_window(parent):  # htest #
    # error jeżeli close master window first - timer event, after script
    root = parent
    fixwordbreaks(root)
    jeżeli sys.argv[1:]:
        filename = sys.argv[1]
    inaczej:
        filename = Nic
    macosxSupport.setupApp(root, Nic)
    edit = EditorWindow(root=root, filename=filename)
    edit.text.bind("<<close-all-windows>>", edit.close_event)
    # Does nie stop error, neither does following
    # edit.text.bind("<<close-window>>", edit.close_event)

jeżeli __name__ == '__main__':
    z idlelib.idle_test.htest zaimportuj run
    run(_help_dialog, _editor_window)
