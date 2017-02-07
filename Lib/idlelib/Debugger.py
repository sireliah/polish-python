zaimportuj os
zaimportuj bdb
z tkinter zaimportuj *
z idlelib.WindowList zaimportuj ListedToplevel
z idlelib.ScrolledList zaimportuj ScrolledList
z idlelib zaimportuj macosxSupport


klasa Idb(bdb.Bdb):

    def __init__(self, gui):
        self.gui = gui
        bdb.Bdb.__init__(self)

    def user_line(self, frame):
        jeżeli self.in_rpc_code(frame):
            self.set_step()
            zwróć
        message = self.__frame2message(frame)
        self.gui.interaction(message, frame)

    def user_exception(self, frame, info):
        jeżeli self.in_rpc_code(frame):
            self.set_step()
            zwróć
        message = self.__frame2message(frame)
        self.gui.interaction(message, frame, info)

    def in_rpc_code(self, frame):
        jeżeli frame.f_code.co_filename.count('rpc.py'):
            zwróć Prawda
        inaczej:
            prev_frame = frame.f_back
            jeżeli prev_frame.f_code.co_filename.count('Debugger.py'):
                # (that test will catch both Debugger.py oraz RemoteDebugger.py)
                zwróć Nieprawda
            zwróć self.in_rpc_code(prev_frame)

    def __frame2message(self, frame):
        code = frame.f_code
        filename = code.co_filename
        lineno = frame.f_lineno
        basename = os.path.basename(filename)
        message = "%s:%s" % (basename, lineno)
        jeżeli code.co_name != "?":
            message = "%s: %s()" % (message, code.co_name)
        zwróć message


klasa Debugger:

    vstack = vsource = vlocals = vglobals = Nic

    def __init__(self, pyshell, idb=Nic):
        jeżeli idb jest Nic:
            idb = Idb(self)
        self.pyshell = pyshell
        self.idb = idb
        self.frame = Nic
        self.make_gui()
        self.interacting = 0

    def run(self, *args):
        spróbuj:
            self.interacting = 1
            zwróć self.idb.run(*args)
        w_końcu:
            self.interacting = 0

    def close(self, event=Nic):
        jeżeli self.interacting:
            self.top.bell()
            zwróć
        jeżeli self.stackviewer:
            self.stackviewer.close(); self.stackviewer = Nic
        # Clean up pyshell jeżeli user clicked debugger control close widget.
        # (Causes a harmless extra cycle through close_debugger() jeżeli user
        # toggled debugger z pyshell Debug menu)
        self.pyshell.close_debugger()
        # Now close the debugger control window....
        self.top.destroy()

    def make_gui(self):
        pyshell = self.pyshell
        self.flist = pyshell.flist
        self.root = root = pyshell.root
        self.top = top = ListedToplevel(root)
        self.top.wm_title("Debug Control")
        self.top.wm_iconname("Debug")
        top.wm_protocol("WM_DELETE_WINDOW", self.close)
        self.top.bind("<Escape>", self.close)
        #
        self.bframe = bframe = Frame(top)
        self.bframe.pack(anchor="w")
        self.buttons = bl = []
        #
        self.bcont = b = Button(bframe, text="Go", command=self.cont)
        bl.append(b)
        self.bstep = b = Button(bframe, text="Step", command=self.step)
        bl.append(b)
        self.bnext = b = Button(bframe, text="Over", command=self.next)
        bl.append(b)
        self.bret = b = Button(bframe, text="Out", command=self.ret)
        bl.append(b)
        self.bret = b = Button(bframe, text="Quit", command=self.quit)
        bl.append(b)
        #
        dla b w bl:
            b.configure(state="disabled")
            b.pack(side="left")
        #
        self.cframe = cframe = Frame(bframe)
        self.cframe.pack(side="left")
        #
        jeżeli nie self.vstack:
            self.__class__.vstack = BooleanVar(top)
            self.vstack.set(1)
        self.bstack = Checkbutton(cframe,
            text="Stack", command=self.show_stack, variable=self.vstack)
        self.bstack.grid(row=0, column=0)
        jeżeli nie self.vsource:
            self.__class__.vsource = BooleanVar(top)
        self.bsource = Checkbutton(cframe,
            text="Source", command=self.show_source, variable=self.vsource)
        self.bsource.grid(row=0, column=1)
        jeżeli nie self.vlocals:
            self.__class__.vlocals = BooleanVar(top)
            self.vlocals.set(1)
        self.blocals = Checkbutton(cframe,
            text="Locals", command=self.show_locals, variable=self.vlocals)
        self.blocals.grid(row=1, column=0)
        jeżeli nie self.vglobals:
            self.__class__.vglobals = BooleanVar(top)
        self.bglobals = Checkbutton(cframe,
            text="Globals", command=self.show_globals, variable=self.vglobals)
        self.bglobals.grid(row=1, column=1)
        #
        self.status = Label(top, anchor="w")
        self.status.pack(anchor="w")
        self.error = Label(top, anchor="w")
        self.error.pack(anchor="w", fill="x")
        self.errorbg = self.error.cget("background")
        #
        self.fstack = Frame(top, height=1)
        self.fstack.pack(expand=1, fill="both")
        self.flocals = Frame(top)
        self.flocals.pack(expand=1, fill="both")
        self.fglobals = Frame(top, height=1)
        self.fglobals.pack(expand=1, fill="both")
        #
        jeżeli self.vstack.get():
            self.show_stack()
        jeżeli self.vlocals.get():
            self.show_locals()
        jeżeli self.vglobals.get():
            self.show_globals()

    def interaction(self, message, frame, info=Nic):
        self.frame = frame
        self.status.configure(text=message)
        #
        jeżeli info:
            type, value, tb = info
            spróbuj:
                m1 = type.__name__
            wyjąwszy AttributeError:
                m1 = "%s" % str(type)
            jeżeli value jest nie Nic:
                spróbuj:
                    m1 = "%s: %s" % (m1, str(value))
                wyjąwszy:
                    dalej
            bg = "yellow"
        inaczej:
            m1 = ""
            tb = Nic
            bg = self.errorbg
        self.error.configure(text=m1, background=bg)
        #
        sv = self.stackviewer
        jeżeli sv:
            stack, i = self.idb.get_stack(self.frame, tb)
            sv.load_stack(stack, i)
        #
        self.show_variables(1)
        #
        jeżeli self.vsource.get():
            self.sync_source_line()
        #
        dla b w self.buttons:
            b.configure(state="normal")
        #
        self.top.wakeup()
        self.root.mainloop()
        #
        dla b w self.buttons:
            b.configure(state="disabled")
        self.status.configure(text="")
        self.error.configure(text="", background=self.errorbg)
        self.frame = Nic

    def sync_source_line(self):
        frame = self.frame
        jeżeli nie frame:
            zwróć
        filename, lineno = self.__frame2fileline(frame)
        jeżeli filename[:1] + filename[-1:] != "<>" oraz os.path.exists(filename):
            self.flist.gotofileline(filename, lineno)

    def __frame2fileline(self, frame):
        code = frame.f_code
        filename = code.co_filename
        lineno = frame.f_lineno
        zwróć filename, lineno

    def cont(self):
        self.idb.set_continue()
        self.root.quit()

    def step(self):
        self.idb.set_step()
        self.root.quit()

    def next(self):
        self.idb.set_next(self.frame)
        self.root.quit()

    def ret(self):
        self.idb.set_return(self.frame)
        self.root.quit()

    def quit(self):
        self.idb.set_quit()
        self.root.quit()

    stackviewer = Nic

    def show_stack(self):
        jeżeli nie self.stackviewer oraz self.vstack.get():
            self.stackviewer = sv = StackViewer(self.fstack, self.flist, self)
            jeżeli self.frame:
                stack, i = self.idb.get_stack(self.frame, Nic)
                sv.load_stack(stack, i)
        inaczej:
            sv = self.stackviewer
            jeżeli sv oraz nie self.vstack.get():
                self.stackviewer = Nic
                sv.close()
            self.fstack['height'] = 1

    def show_source(self):
        jeżeli self.vsource.get():
            self.sync_source_line()

    def show_frame(self, stackitem):
        self.frame = stackitem[0]  # lineno jest stackitem[1]
        self.show_variables()

    localsviewer = Nic
    globalsviewer = Nic

    def show_locals(self):
        lv = self.localsviewer
        jeżeli self.vlocals.get():
            jeżeli nie lv:
                self.localsviewer = NamespaceViewer(self.flocals, "Locals")
        inaczej:
            jeżeli lv:
                self.localsviewer = Nic
                lv.close()
                self.flocals['height'] = 1
        self.show_variables()

    def show_globals(self):
        gv = self.globalsviewer
        jeżeli self.vglobals.get():
            jeżeli nie gv:
                self.globalsviewer = NamespaceViewer(self.fglobals, "Globals")
        inaczej:
            jeżeli gv:
                self.globalsviewer = Nic
                gv.close()
                self.fglobals['height'] = 1
        self.show_variables()

    def show_variables(self, force=0):
        lv = self.localsviewer
        gv = self.globalsviewer
        frame = self.frame
        jeżeli nie frame:
            ldict = gdict = Nic
        inaczej:
            ldict = frame.f_locals
            gdict = frame.f_globals
            jeżeli lv oraz gv oraz ldict jest gdict:
                ldict = Nic
        jeżeli lv:
            lv.load_dict(ldict, force, self.pyshell.interp.rpcclt)
        jeżeli gv:
            gv.load_dict(gdict, force, self.pyshell.interp.rpcclt)

    def set_breakpoint_here(self, filename, lineno):
        self.idb.set_break(filename, lineno)

    def clear_breakpoint_here(self, filename, lineno):
        self.idb.clear_break(filename, lineno)

    def clear_file_breaks(self, filename):
        self.idb.clear_all_file_breaks(filename)

    def load_breakpoints(self):
        "Load PyShellEditorWindow przerwijpoints into subprocess debugger"
        dla editwin w self.pyshell.flist.inversedict:
            filename = editwin.io.filename
            spróbuj:
                dla lineno w editwin.breakpoints:
                    self.set_breakpoint_here(filename, lineno)
            wyjąwszy AttributeError:
                kontynuuj

klasa StackViewer(ScrolledList):

    def __init__(self, master, flist, gui):
        jeżeli macosxSupport.isAquaTk():
            # At least on przy the stock AquaTk version on OSX 10.4 you'll
            # get an shaking GUI that eventually kills IDLE jeżeli the width
            # argument jest specified.
            ScrolledList.__init__(self, master)
        inaczej:
            ScrolledList.__init__(self, master, width=80)
        self.flist = flist
        self.gui = gui
        self.stack = []

    def load_stack(self, stack, index=Nic):
        self.stack = stack
        self.clear()
        dla i w range(len(stack)):
            frame, lineno = stack[i]
            spróbuj:
                modname = frame.f_globals["__name__"]
            wyjąwszy:
                modname = "?"
            code = frame.f_code
            filename = code.co_filename
            funcname = code.co_name
            zaimportuj linecache
            sourceline = linecache.getline(filename, lineno)
            sourceline = sourceline.strip()
            jeżeli funcname w ("?", "", Nic):
                item = "%s, line %d: %s" % (modname, lineno, sourceline)
            inaczej:
                item = "%s.%s(), line %d: %s" % (modname, funcname,
                                                 lineno, sourceline)
            jeżeli i == index:
                item = "> " + item
            self.append(item)
        jeżeli index jest nie Nic:
            self.select(index)

    def popup_event(self, event):
        "override base method"
        jeżeli self.stack:
            zwróć ScrolledList.popup_event(self, event)

    def fill_menu(self):
        "override base method"
        menu = self.menu
        menu.add_command(label="Go to source line",
                         command=self.goto_source_line)
        menu.add_command(label="Show stack frame",
                         command=self.show_stack_frame)

    def on_select(self, index):
        "override base method"
        jeżeli 0 <= index < len(self.stack):
            self.gui.show_frame(self.stack[index])

    def on_double(self, index):
        "override base method"
        self.show_source(index)

    def goto_source_line(self):
        index = self.listbox.index("active")
        self.show_source(index)

    def show_stack_frame(self):
        index = self.listbox.index("active")
        jeżeli 0 <= index < len(self.stack):
            self.gui.show_frame(self.stack[index])

    def show_source(self, index):
        jeżeli nie (0 <= index < len(self.stack)):
            zwróć
        frame, lineno = self.stack[index]
        code = frame.f_code
        filename = code.co_filename
        jeżeli os.path.isfile(filename):
            edit = self.flist.open(filename)
            jeżeli edit:
                edit.gotoline(lineno)


klasa NamespaceViewer:

    def __init__(self, master, title, dict=Nic):
        width = 0
        height = 40
        jeżeli dict:
            height = 20*len(dict) # XXX 20 == observed height of Entry widget
        self.master = master
        self.title = title
        zaimportuj reprlib
        self.repr = reprlib.Repr()
        self.repr.maxstring = 60
        self.repr.maxother = 60
        self.frame = frame = Frame(master)
        self.frame.pack(expand=1, fill="both")
        self.label = Label(frame, text=title, borderwidth=2, relief="groove")
        self.label.pack(fill="x")
        self.vbar = vbar = Scrollbar(frame, name="vbar")
        vbar.pack(side="right", fill="y")
        self.canvas = canvas = Canvas(frame,
                                      height=min(300, max(40, height)),
                                      scrollregion=(0, 0, width, height))
        canvas.pack(side="left", fill="both", expand=1)
        vbar["command"] = canvas.yview
        canvas["yscrollcommand"] = vbar.set
        self.subframe = subframe = Frame(canvas)
        self.sfid = canvas.create_window(0, 0, window=subframe, anchor="nw")
        self.load_dict(dict)

    dict = -1

    def load_dict(self, dict, force=0, rpc_client=Nic):
        jeżeli dict jest self.dict oraz nie force:
            zwróć
        subframe = self.subframe
        frame = self.frame
        dla c w list(subframe.children.values()):
            c.destroy()
        self.dict = Nic
        jeżeli nie dict:
            l = Label(subframe, text="Nic")
            l.grid(row=0, column=0)
        inaczej:
            #names = sorted(dict)
            ###
            # Because of (temporary) limitations on the dict_keys type (nie yet
            # public albo pickleable), have the subprocess to send a list of
            # keys, nie a dict_keys object.  sorted() will take a dict_keys
            # (no subprocess) albo a list.
            #
            # There jest also an obscure bug w sorted(dict) where the
            # interpreter gets into a loop requesting non-existing dict[0],
            # dict[1], dict[2], etc z the RemoteDebugger.DictProxy.
            ###
            keys_list = dict.keys()
            names = sorted(keys_list)
            ###
            row = 0
            dla name w names:
                value = dict[name]
                svalue = self.repr.repr(value) # repr(value)
                # Strip extra quotes caused by calling repr on the (already)
                # repr'd value sent across the RPC interface:
                jeżeli rpc_client:
                    svalue = svalue[1:-1]
                l = Label(subframe, text=name)
                l.grid(row=row, column=0, sticky="nw")
                l = Entry(subframe, width=0, borderwidth=0)
                l.insert(0, svalue)
                l.grid(row=row, column=1, sticky="nw")
                row = row+1
        self.dict = dict
        # XXX Could we use a <Configure> callback dla the following?
        subframe.update_idletasks() # Alas!
        width = subframe.winfo_reqwidth()
        height = subframe.winfo_reqheight()
        canvas = self.canvas
        self.canvas["scrollregion"] = (0, 0, width, height)
        jeżeli height > 300:
            canvas["height"] = 300
            frame.pack(expand=1)
        inaczej:
            canvas["height"] = height
            frame.pack(expand=0)

    def close(self):
        self.frame.destroy()
