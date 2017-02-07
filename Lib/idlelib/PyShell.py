#! /usr/bin/env python3

zaimportuj getopt
zaimportuj os
zaimportuj os.path
zaimportuj re
zaimportuj socket
zaimportuj subprocess
zaimportuj sys
zaimportuj threading
zaimportuj time
zaimportuj tokenize
zaimportuj io

zaimportuj linecache
z code zaimportuj InteractiveInterpreter
z platform zaimportuj python_version, system

spróbuj:
    z tkinter zaimportuj *
wyjąwszy ImportError:
    print("** IDLE can't zaimportuj Tkinter.\n"
          "Your Python may nie be configured dla Tk. **", file=sys.__stderr__)
    sys.exit(1)
zaimportuj tkinter.messagebox jako tkMessageBox

z idlelib.EditorWindow zaimportuj EditorWindow, fixwordbreaks
z idlelib.FileList zaimportuj FileList
z idlelib.ColorDelegator zaimportuj ColorDelegator
z idlelib.UndoDelegator zaimportuj UndoDelegator
z idlelib.OutputWindow zaimportuj OutputWindow
z idlelib.configHandler zaimportuj idleConf
z idlelib zaimportuj rpc
z idlelib zaimportuj Debugger
z idlelib zaimportuj RemoteDebugger
z idlelib zaimportuj macosxSupport

HOST = '127.0.0.1' # python execution server on localhost loopback
PORT = 0  # someday dalej w host, port dla remote debug capability

# Override warnings module to write to warning_stream.  Initialize to send IDLE
# internal warnings to the console.  ScriptBinding.check_syntax() will
# temporarily redirect the stream to the shell window to display warnings when
# checking user's code.
warning_stream = sys.__stderr__  # Nic, at least on Windows, jeżeli no console.
zaimportuj warnings

def idle_formatwarning(message, category, filename, lineno, line=Nic):
    """Format warnings the IDLE way."""

    s = "\nWarning (z warnings module):\n"
    s += '  File \"%s\", line %s\n' % (filename, lineno)
    jeżeli line jest Nic:
        line = linecache.getline(filename, lineno)
    line = line.strip()
    jeżeli line:
        s += "    %s\n" % line
    s += "%s: %s\n" % (category.__name__, message)
    zwróć s

def idle_showwarning(
        message, category, filename, lineno, file=Nic, line=Nic):
    """Show Idle-format warning (after replacing warnings.showwarning).

    The differences are the formatter called, the file=Nic replacement,
    which can be Nic, the capture of the consequence AttributeError,
    oraz the output of a hard-coded prompt.
    """
    jeżeli file jest Nic:
        file = warning_stream
    spróbuj:
        file.write(idle_formatwarning(
                message, category, filename, lineno, line=line))
        file.write(">>> ")
    wyjąwszy (AttributeError, OSError):
        dalej  # jeżeli file (probably __stderr__) jest invalid, skip warning.

_warnings_showwarning = Nic

def capture_warnings(capture):
    "Replace warning.showwarning przy idle_showwarning, albo reverse."

    global _warnings_showwarning
    jeżeli capture:
        jeżeli _warnings_showwarning jest Nic:
            _warnings_showwarning = warnings.showwarning
            warnings.showwarning = idle_showwarning
    inaczej:
        jeżeli _warnings_showwarning jest nie Nic:
            warnings.showwarning = _warnings_showwarning
            _warnings_showwarning = Nic

capture_warnings(Prawda)

def extended_linecache_checkcache(filename=Nic,
                                  orig_checkcache=linecache.checkcache):
    """Extend linecache.checkcache to preserve the <pyshell#...> entries

    Rather than repeating the linecache code, patch it to save the
    <pyshell#...> entries, call the original linecache.checkcache()
    (skipping them), oraz then restore the saved entries.

    orig_checkcache jest bound at definition time to the original
    method, allowing it to be patched.
    """
    cache = linecache.cache
    save = {}
    dla key w list(cache):
        jeżeli key[:1] + key[-1:] == '<>':
            save[key] = cache.pop(key)
    orig_checkcache(filename)
    cache.update(save)

# Patch linecache.checkcache():
linecache.checkcache = extended_linecache_checkcache


klasa PyShellEditorWindow(EditorWindow):
    "Regular text edit window w IDLE, supports przerwijpoints"

    def __init__(self, *args):
        self.breakpoints = []
        EditorWindow.__init__(self, *args)
        self.text.bind("<<set-breakpoint-here>>", self.set_breakpoint_here)
        self.text.bind("<<clear-breakpoint-here>>", self.clear_breakpoint_here)
        self.text.bind("<<open-python-shell>>", self.flist.open_shell)

        self.breakpointPath = os.path.join(idleConf.GetUserCfgDir(),
                                           'breakpoints.lst')
        # whenever a file jest changed, restore przerwijpoints
        def filename_changed_hook(old_hook=self.io.filename_change_hook,
                                  self=self):
            self.restore_file_breaks()
            old_hook()
        self.io.set_filename_change_hook(filename_changed_hook)
        jeżeli self.io.filename:
            self.restore_file_breaks()
        self.color_breakpoint_text()

    rmenu_specs = [
        ("Cut", "<<cut>>", "rmenu_check_cut"),
        ("Copy", "<<copy>>", "rmenu_check_copy"),
        ("Paste", "<<paste>>", "rmenu_check_paste"),
        (Nic, Nic, Nic),
        ("Set Breakpoint", "<<set-breakpoint-here>>", Nic),
        ("Clear Breakpoint", "<<clear-breakpoint-here>>", Nic)
    ]

    def color_breakpoint_text(self, color=Prawda):
        "Turn colorizing of przerwijpoint text on albo off"
        jeżeli self.io jest Nic:
            # possible due to update w restore_file_breaks
            zwróć
        jeżeli color:
            theme = idleConf.GetOption('main','Theme','name')
            cfg = idleConf.GetHighlight(theme, "break")
        inaczej:
            cfg = {'foreground': '', 'background': ''}
        self.text.tag_config('BREAK', cfg)

    def set_breakpoint(self, lineno):
        text = self.text
        filename = self.io.filename
        text.tag_add("BREAK", "%d.0" % lineno, "%d.0" % (lineno+1))
        spróbuj:
            self.breakpoints.index(lineno)
        wyjąwszy ValueError:  # only add jeżeli missing, i.e. do once
            self.breakpoints.append(lineno)
        spróbuj:    # update the subprocess debugger
            debug = self.flist.pyshell.interp.debugger
            debug.set_breakpoint_here(filename, lineno)
        wyjąwszy: # but debugger may nie be active right now....
            dalej

    def set_breakpoint_here(self, event=Nic):
        text = self.text
        filename = self.io.filename
        jeżeli nie filename:
            text.bell()
            zwróć
        lineno = int(float(text.index("insert")))
        self.set_breakpoint(lineno)

    def clear_breakpoint_here(self, event=Nic):
        text = self.text
        filename = self.io.filename
        jeżeli nie filename:
            text.bell()
            zwróć
        lineno = int(float(text.index("insert")))
        spróbuj:
            self.breakpoints.remove(lineno)
        wyjąwszy:
            dalej
        text.tag_remove("BREAK", "insert linestart",\
                        "insert lineend +1char")
        spróbuj:
            debug = self.flist.pyshell.interp.debugger
            debug.clear_breakpoint_here(filename, lineno)
        wyjąwszy:
            dalej

    def clear_file_breaks(self):
        jeżeli self.breakpoints:
            text = self.text
            filename = self.io.filename
            jeżeli nie filename:
                text.bell()
                zwróć
            self.breakpoints = []
            text.tag_remove("BREAK", "1.0", END)
            spróbuj:
                debug = self.flist.pyshell.interp.debugger
                debug.clear_file_breaks(filename)
            wyjąwszy:
                dalej

    def store_file_breaks(self):
        "Save przerwijpoints when file jest saved"
        # XXX 13 Dec 2002 KBK Currently the file must be saved before it can
        #     be run.  The przerwijs are saved at that time.  If we introduce
        #     a temporary file save feature the save przerwijs functionality
        #     needs to be re-verified, since the przerwijs at the time the
        #     temp file jest created may differ z the przerwijs at the last
        #     permanent save of the file.  Currently, a przerwij introduced
        #     after a save will be effective, but nie persistent.
        #     This jest necessary to keep the saved przerwijs synched przy the
        #     saved file.
        #
        #     Breakpoints are set jako tagged ranges w the text.
        #     Since a modified file has to be saved before it jest
        #     run, oraz since self.breakpoints (z which the subprocess
        #     debugger jest loaded) jest updated during the save, the visible
        #     przerwijs stay synched przy the subprocess even jeżeli one of these
        #     unexpected przerwijpoint deletions occurs.
        przerwijs = self.breakpoints
        filename = self.io.filename
        spróbuj:
            przy open(self.breakpointPath, "r") jako fp:
                lines = fp.readlines()
        wyjąwszy OSError:
            lines = []
        spróbuj:
            przy open(self.breakpointPath, "w") jako new_file:
                dla line w lines:
                    jeżeli nie line.startswith(filename + '='):
                        new_file.write(line)
                self.update_breakpoints()
                przerwijs = self.breakpoints
                jeżeli przerwijs:
                    new_file.write(filename + '=' + str(breaks) + '\n')
        wyjąwszy OSError jako err:
            jeżeli nie getattr(self.root, "breakpoint_error_displayed", Nieprawda):
                self.root.breakpoint_error_displayed = Prawda
                tkMessageBox.showerror(title='IDLE Error',
                    message='Unable to update przerwijpoint list:\n%s'
                        % str(err),
                    parent=self.text)

    def restore_file_breaks(self):
        self.text.update()   # this enables setting "BREAK" tags to be visible
        jeżeli self.io jest Nic:
            # can happen jeżeli IDLE closes due to the .update() call
            zwróć
        filename = self.io.filename
        jeżeli filename jest Nic:
            zwróć
        jeżeli os.path.isfile(self.breakpointPath):
            przy open(self.breakpointPath, "r") jako fp:
                lines = fp.readlines()
            dla line w lines:
                jeżeli line.startswith(filename + '='):
                    przerwijpoint_linenumbers = eval(line[len(filename)+1:])
                    dla przerwijpoint_linenumber w przerwijpoint_linenumbers:
                        self.set_breakpoint(breakpoint_linenumber)

    def update_breakpoints(self):
        "Retrieves all the przerwijpoints w the current window"
        text = self.text
        ranges = text.tag_ranges("BREAK")
        linenumber_list = self.ranges_to_linenumbers(ranges)
        self.breakpoints = linenumber_list

    def ranges_to_linenumbers(self, ranges):
        lines = []
        dla index w range(0, len(ranges), 2):
            lineno = int(float(ranges[index].string))
            end = int(float(ranges[index+1].string))
            dopóki lineno < end:
                lines.append(lineno)
                lineno += 1
        zwróć lines

# XXX 13 Dec 2002 KBK Not used currently
#    def saved_change_hook(self):
#        "Extend base method - clear przerwijs jeżeli module jest modified"
#        jeżeli nie self.get_saved():
#            self.clear_file_breaks()
#        EditorWindow.saved_change_hook(self)

    def _close(self):
        "Extend base method - clear przerwijs when module jest closed"
        self.clear_file_breaks()
        EditorWindow._close(self)


klasa PyShellFileList(FileList):
    "Extend base class: IDLE supports a shell oraz przerwijpoints"

    # override FileList's klasa variable, instances zwróć PyShellEditorWindow
    # instead of EditorWindow when new edit windows are created.
    EditorWindow = PyShellEditorWindow

    pyshell = Nic

    def open_shell(self, event=Nic):
        jeżeli self.pyshell:
            self.pyshell.top.wakeup()
        inaczej:
            self.pyshell = PyShell(self)
            jeżeli self.pyshell:
                jeżeli nie self.pyshell.begin():
                    zwróć Nic
        zwróć self.pyshell


klasa ModifiedColorDelegator(ColorDelegator):
    "Extend base class: colorizer dla the shell window itself"

    def __init__(self):
        ColorDelegator.__init__(self)
        self.LoadTagDefs()

    def recolorize_main(self):
        self.tag_remove("TODO", "1.0", "iomark")
        self.tag_add("SYNC", "1.0", "iomark")
        ColorDelegator.recolorize_main(self)

    def LoadTagDefs(self):
        ColorDelegator.LoadTagDefs(self)
        theme = idleConf.GetOption('main','Theme','name')
        self.tagdefs.update({
            "stdin": {'background':Nic,'foreground':Nic},
            "stdout": idleConf.GetHighlight(theme, "stdout"),
            "stderr": idleConf.GetHighlight(theme, "stderr"),
            "console": idleConf.GetHighlight(theme, "console"),
        })

    def removecolors(self):
        # Don't remove shell color tags before "iomark"
        dla tag w self.tagdefs:
            self.tag_remove(tag, "iomark", "end")

klasa ModifiedUndoDelegator(UndoDelegator):
    "Extend base class: forbid insert/delete before the I/O mark"

    def insert(self, index, chars, tags=Nic):
        spróbuj:
            jeżeli self.delegate.compare(index, "<", "iomark"):
                self.delegate.bell()
                zwróć
        wyjąwszy TclError:
            dalej
        UndoDelegator.insert(self, index, chars, tags)

    def delete(self, index1, index2=Nic):
        spróbuj:
            jeżeli self.delegate.compare(index1, "<", "iomark"):
                self.delegate.bell()
                zwróć
        wyjąwszy TclError:
            dalej
        UndoDelegator.delete(self, index1, index2)


klasa MyRPCClient(rpc.RPCClient):

    def handle_EOF(self):
        "Override the base klasa - just re-raise EOFError"
        podnieś EOFError


klasa ModifiedInterpreter(InteractiveInterpreter):

    def __init__(self, tkconsole):
        self.tkconsole = tkconsole
        locals = sys.modules['__main__'].__dict__
        InteractiveInterpreter.__init__(self, locals=locals)
        self.save_warnings_filters = Nic
        self.restarting = Nieprawda
        self.subprocess_arglist = Nic
        self.port = PORT
        self.original_compiler_flags = self.compile.compiler.flags

    _afterid = Nic
    rpcclt = Nic
    rpcsubproc = Nic

    def spawn_subprocess(self):
        jeżeli self.subprocess_arglist jest Nic:
            self.subprocess_arglist = self.build_subprocess_arglist()
        self.rpcsubproc = subprocess.Popen(self.subprocess_arglist)

    def build_subprocess_arglist(self):
        assert (self.port!=0), (
            "Socket should have been assigned a port number.")
        w = ['-W' + s dla s w sys.warnoptions]
        # Maybe IDLE jest installed oraz jest being accessed via sys.path,
        # albo maybe it's nie installed oraz the idle.py script jest being
        # run z the IDLE source directory.
        del_exitf = idleConf.GetOption('main', 'General', 'delete-exitfunc',
                                       default=Nieprawda, type='bool')
        jeżeli __name__ == 'idlelib.PyShell':
            command = "__import__('idlelib.run').run.main(%r)" % (del_exitf,)
        inaczej:
            command = "__import__('run').main(%r)" % (del_exitf,)
        zwróć [sys.executable] + w + ["-c", command, str(self.port)]

    def start_subprocess(self):
        addr = (HOST, self.port)
        # GUI makes several attempts to acquire socket, listens dla connection
        dla i w range(3):
            time.sleep(i)
            spróbuj:
                self.rpcclt = MyRPCClient(addr)
                przerwij
            wyjąwszy OSError:
                dalej
        inaczej:
            self.display_port_binding_error()
            zwróć Nic
        # jeżeli PORT was 0, system will assign an 'ephemeral' port. Find it out:
        self.port = self.rpcclt.listening_sock.getsockname()[1]
        # jeżeli PORT was nie 0, probably working przy a remote execution server
        jeżeli PORT != 0:
            # To allow reconnection within the 2MSL wait (cf. Stevens TCP
            # V1, 18.6),  set SO_REUSEADDR.  Note that this can be problematic
            # on Windows since the implementation allows two active sockets on
            # the same address!
            self.rpcclt.listening_sock.setsockopt(socket.SOL_SOCKET,
                                           socket.SO_REUSEADDR, 1)
        self.spawn_subprocess()
        #time.sleep(20) # test to simulate GUI nie accepting connection
        # Accept the connection z the Python execution server
        self.rpcclt.listening_sock.settimeout(10)
        spróbuj:
            self.rpcclt.accept()
        wyjąwszy socket.timeout:
            self.display_no_subprocess_error()
            zwróć Nic
        self.rpcclt.register("console", self.tkconsole)
        self.rpcclt.register("stdin", self.tkconsole.stdin)
        self.rpcclt.register("stdout", self.tkconsole.stdout)
        self.rpcclt.register("stderr", self.tkconsole.stderr)
        self.rpcclt.register("flist", self.tkconsole.flist)
        self.rpcclt.register("linecache", linecache)
        self.rpcclt.register("interp", self)
        self.transfer_path(with_cwd=Prawda)
        self.poll_subprocess()
        zwróć self.rpcclt

    def restart_subprocess(self, with_cwd=Nieprawda, filename=''):
        jeżeli self.restarting:
            zwróć self.rpcclt
        self.restarting = Prawda
        # close only the subprocess debugger
        debug = self.getdebugger()
        jeżeli debug:
            spróbuj:
                # Only close subprocess debugger, don't unregister gui_adap!
                RemoteDebugger.close_subprocess_debugger(self.rpcclt)
            wyjąwszy:
                dalej
        # Kill subprocess, spawn a new one, accept connection.
        self.rpcclt.close()
        self.terminate_subprocess()
        console = self.tkconsole
        was_executing = console.executing
        console.executing = Nieprawda
        self.spawn_subprocess()
        spróbuj:
            self.rpcclt.accept()
        wyjąwszy socket.timeout:
            self.display_no_subprocess_error()
            zwróć Nic
        self.transfer_path(with_cwd=with_cwd)
        console.stop_readline()
        # annotate restart w shell window oraz mark it
        console.text.delete("iomark", "end-1c")
        tag = 'RESTART: ' + (filename jeżeli filename inaczej 'Shell')
        halfbar = ((int(console.width) -len(tag) - 4) // 2) * '='
        console.write("\n{0} {1} {0}".format(halfbar, tag))
        console.text.mark_set("restart", "end-1c")
        console.text.mark_gravity("restart", "left")
        jeżeli nie filename:
            console.showprompt()
        # restart subprocess debugger
        jeżeli debug:
            # Restarted debugger connects to current instance of debug GUI
            RemoteDebugger.restart_subprocess_debugger(self.rpcclt)
            # reload remote debugger przerwijpoints dla all PyShellEditWindows
            debug.load_breakpoints()
        self.compile.compiler.flags = self.original_compiler_flags
        self.restarting = Nieprawda
        zwróć self.rpcclt

    def __request_interrupt(self):
        self.rpcclt.remotecall("exec", "interrupt_the_server", (), {})

    def interrupt_subprocess(self):
        threading.Thread(target=self.__request_interrupt).start()

    def kill_subprocess(self):
        jeżeli self._afterid jest nie Nic:
            self.tkconsole.text.after_cancel(self._afterid)
        spróbuj:
            self.rpcclt.listening_sock.close()
        wyjąwszy AttributeError:  # no socket
            dalej
        spróbuj:
            self.rpcclt.close()
        wyjąwszy AttributeError:  # no socket
            dalej
        self.terminate_subprocess()
        self.tkconsole.executing = Nieprawda
        self.rpcclt = Nic

    def terminate_subprocess(self):
        "Make sure subprocess jest terminated"
        spróbuj:
            self.rpcsubproc.kill()
        wyjąwszy OSError:
            # process already terminated
            zwróć
        inaczej:
            spróbuj:
                self.rpcsubproc.wait()
            wyjąwszy OSError:
                zwróć

    def transfer_path(self, with_cwd=Nieprawda):
        jeżeli with_cwd:        # Issue 13506
            path = ['']     # include Current Working Directory
            path.extend(sys.path)
        inaczej:
            path = sys.path

        self.runcommand("""jeżeli 1:
        zaimportuj sys jako _sys
        _sys.path = %r
        usuń _sys
        \n""" % (path,))

    active_seq = Nic

    def poll_subprocess(self):
        clt = self.rpcclt
        jeżeli clt jest Nic:
            zwróć
        spróbuj:
            response = clt.pollresponse(self.active_seq, wait=0.05)
        wyjąwszy (EOFError, OSError, KeyboardInterrupt):
            # lost connection albo subprocess terminated itself, restart
            # [the KBI jest z rpc.SocketIO.handle_EOF()]
            jeżeli self.tkconsole.closing:
                zwróć
            response = Nic
            self.restart_subprocess()
        jeżeli response:
            self.tkconsole.resetoutput()
            self.active_seq = Nic
            how, what = response
            console = self.tkconsole.console
            jeżeli how == "OK":
                jeżeli what jest nie Nic:
                    print(repr(what), file=console)
            albo_inaczej how == "EXCEPTION":
                jeżeli self.tkconsole.getvar("<<toggle-jit-stack-viewer>>"):
                    self.remote_stack_viewer()
            albo_inaczej how == "ERROR":
                errmsg = "PyShell.ModifiedInterpreter: Subprocess ERROR:\n"
                print(errmsg, what, file=sys.__stderr__)
                print(errmsg, what, file=console)
            # we received a response to the currently active seq number:
            spróbuj:
                self.tkconsole.endexecuting()
            wyjąwszy AttributeError:  # shell may have closed
                dalej
        # Reschedule myself
        jeżeli nie self.tkconsole.closing:
            self._afterid = self.tkconsole.text.after(
                self.tkconsole.pollinterval, self.poll_subprocess)

    debugger = Nic

    def setdebugger(self, debugger):
        self.debugger = debugger

    def getdebugger(self):
        zwróć self.debugger

    def open_remote_stack_viewer(self):
        """Initiate the remote stack viewer z a separate thread.

        This method jest called z the subprocess, oraz by returning z this
        method we allow the subprocess to unblock.  After a bit the shell
        requests the subprocess to open the remote stack viewer which returns a
        static object looking at the last exception.  It jest queried through
        the RPC mechanism.

        """
        self.tkconsole.text.after(300, self.remote_stack_viewer)
        zwróć

    def remote_stack_viewer(self):
        z idlelib zaimportuj RemoteObjectBrowser
        oid = self.rpcclt.remotequeue("exec", "stackviewer", ("flist",), {})
        jeżeli oid jest Nic:
            self.tkconsole.root.bell()
            zwróć
        item = RemoteObjectBrowser.StubObjectTreeItem(self.rpcclt, oid)
        z idlelib.TreeWidget zaimportuj ScrolledCanvas, TreeNode
        top = Toplevel(self.tkconsole.root)
        theme = idleConf.GetOption('main','Theme','name')
        background = idleConf.GetHighlight(theme, 'normal')['background']
        sc = ScrolledCanvas(top, bg=background, highlightthickness=0)
        sc.frame.pack(expand=1, fill="both")
        node = TreeNode(sc.canvas, Nic, item)
        node.expand()
        # XXX Should GC the remote tree when closing the window

    gid = 0

    def execsource(self, source):
        "Like runsource() but assumes complete exec source"
        filename = self.stuffsource(source)
        self.execfile(filename, source)

    def execfile(self, filename, source=Nic):
        "Execute an existing file"
        jeżeli source jest Nic:
            przy tokenize.open(filename) jako fp:
                source = fp.read()
        spróbuj:
            code = compile(source, filename, "exec")
        wyjąwszy (OverflowError, SyntaxError):
            self.tkconsole.resetoutput()
            print('*** Error w script albo command!\n'
                 'Traceback (most recent call last):',
                  file=self.tkconsole.stderr)
            InteractiveInterpreter.showsyntaxerror(self, filename)
            self.tkconsole.showprompt()
        inaczej:
            self.runcode(code)

    def runsource(self, source):
        "Extend base klasa method: Stuff the source w the line cache first"
        filename = self.stuffsource(source)
        self.more = 0
        self.save_warnings_filters = warnings.filters[:]
        warnings.filterwarnings(action="error", category=SyntaxWarning)
        # at the moment, InteractiveInterpreter expects str
        assert isinstance(source, str)
        #jeżeli isinstance(source, str):
        #    z idlelib zaimportuj IOBinding
        #    spróbuj:
        #        source = source.encode(IOBinding.encoding)
        #    wyjąwszy UnicodeError:
        #        self.tkconsole.resetoutput()
        #        self.write("Unsupported characters w input\n")
        #        zwróć
        spróbuj:
            # InteractiveInterpreter.runsource() calls its runcode() method,
            # which jest overridden (see below)
            zwróć InteractiveInterpreter.runsource(self, source, filename)
        w_końcu:
            jeżeli self.save_warnings_filters jest nie Nic:
                warnings.filters[:] = self.save_warnings_filters
                self.save_warnings_filters = Nic

    def stuffsource(self, source):
        "Stuff source w the filename cache"
        filename = "<pyshell#%d>" % self.gid
        self.gid = self.gid + 1
        lines = source.split("\n")
        linecache.cache[filename] = len(source)+1, 0, lines, filename
        zwróć filename

    def prepend_syspath(self, filename):
        "Prepend sys.path przy file's directory jeżeli nie already included"
        self.runcommand("""jeżeli 1:
            _filename = %r
            zaimportuj sys jako _sys
            z os.path zaimportuj dirname jako _dirname
            _dir = _dirname(_filename)
            jeżeli nie _dir w _sys.path:
                _sys.path.insert(0, _dir)
            usuń _filename, _sys, _dirname, _dir
            \n""" % (filename,))

    def showsyntaxerror(self, filename=Nic):
        """Override Interactive Interpreter method: Use Colorizing

        Color the offending position instead of printing it oraz pointing at it
        przy a caret.

        """
        tkconsole = self.tkconsole
        text = tkconsole.text
        text.tag_remove("ERROR", "1.0", "end")
        type, value, tb = sys.exc_info()
        msg = getattr(value, 'msg', '') albo value albo "<no detail available>"
        lineno = getattr(value, 'lineno', '') albo 1
        offset = getattr(value, 'offset', '') albo 0
        jeżeli offset == 0:
            lineno += 1 #mark end of offending line
        jeżeli lineno == 1:
            pos = "iomark + %d chars" % (offset-1)
        inaczej:
            pos = "iomark linestart + %d lines + %d chars" % \
                  (lineno-1, offset-1)
        tkconsole.colorize_syntax_error(text, pos)
        tkconsole.resetoutput()
        self.write("SyntaxError: %s\n" % msg)
        tkconsole.showprompt()

    def showtraceback(self):
        "Extend base klasa method to reset output properly"
        self.tkconsole.resetoutput()
        self.checklinecache()
        InteractiveInterpreter.showtraceback(self)
        jeżeli self.tkconsole.getvar("<<toggle-jit-stack-viewer>>"):
            self.tkconsole.open_stack_viewer()

    def checklinecache(self):
        c = linecache.cache
        dla key w list(c.keys()):
            jeżeli key[:1] + key[-1:] != "<>":
                usuń c[key]

    def runcommand(self, code):
        "Run the code without invoking the debugger"
        # The code better nie podnieś an exception!
        jeżeli self.tkconsole.executing:
            self.display_executing_dialog()
            zwróć 0
        jeżeli self.rpcclt:
            self.rpcclt.remotequeue("exec", "runcode", (code,), {})
        inaczej:
            exec(code, self.locals)
        zwróć 1

    def runcode(self, code):
        "Override base klasa method"
        jeżeli self.tkconsole.executing:
            self.interp.restart_subprocess()
        self.checklinecache()
        jeżeli self.save_warnings_filters jest nie Nic:
            warnings.filters[:] = self.save_warnings_filters
            self.save_warnings_filters = Nic
        debugger = self.debugger
        spróbuj:
            self.tkconsole.beginexecuting()
            jeżeli nie debugger oraz self.rpcclt jest nie Nic:
                self.active_seq = self.rpcclt.asyncqueue("exec", "runcode",
                                                        (code,), {})
            albo_inaczej debugger:
                debugger.run(code, self.locals)
            inaczej:
                exec(code, self.locals)
        wyjąwszy SystemExit:
            jeżeli nie self.tkconsole.closing:
                jeżeli tkMessageBox.askyesno(
                    "Exit?",
                    "Do you want to exit altogether?",
                    default="yes",
                    master=self.tkconsole.text):
                    podnieś
                inaczej:
                    self.showtraceback()
            inaczej:
                podnieś
        wyjąwszy:
            jeżeli use_subprocess:
                print("IDLE internal error w runcode()",
                      file=self.tkconsole.stderr)
                self.showtraceback()
                self.tkconsole.endexecuting()
            inaczej:
                jeżeli self.tkconsole.canceled:
                    self.tkconsole.canceled = Nieprawda
                    print("KeyboardInterrupt", file=self.tkconsole.stderr)
                inaczej:
                    self.showtraceback()
        w_końcu:
            jeżeli nie use_subprocess:
                spróbuj:
                    self.tkconsole.endexecuting()
                wyjąwszy AttributeError:  # shell may have closed
                    dalej

    def write(self, s):
        "Override base klasa method"
        zwróć self.tkconsole.stderr.write(s)

    def display_port_binding_error(self):
        tkMessageBox.showerror(
            "Port Binding Error",
            "IDLE can't bind to a TCP/IP port, which jest necessary to "
            "communicate przy its Python execution server.  This might be "
            "because no networking jest installed on this computer.  "
            "Run IDLE przy the -n command line switch to start without a "
            "subprocess oraz refer to Help/IDLE Help 'Running without a "
            "subprocess' dla further details.",
            master=self.tkconsole.text)

    def display_no_subprocess_error(self):
        tkMessageBox.showerror(
            "Subprocess Startup Error",
            "IDLE's subprocess didn't make connection.  Either IDLE can't "
            "start a subprocess albo personal firewall software jest blocking "
            "the connection.",
            master=self.tkconsole.text)

    def display_executing_dialog(self):
        tkMessageBox.showerror(
            "Already executing",
            "The Python Shell window jest already executing a command; "
            "please wait until it jest finished.",
            master=self.tkconsole.text)


klasa PyShell(OutputWindow):

    shell_title = "Python " + python_version() + " Shell"

    # Override classes
    ColorDelegator = ModifiedColorDelegator
    UndoDelegator = ModifiedUndoDelegator

    # Override menus
    menu_specs = [
        ("file", "_File"),
        ("edit", "_Edit"),
        ("debug", "_Debug"),
        ("options", "_Options"),
        ("windows", "_Window"),
        ("help", "_Help"),
    ]


    # New classes
    z idlelib.IdleHistory zaimportuj History

    def __init__(self, flist=Nic):
        jeżeli use_subprocess:
            ms = self.menu_specs
            jeżeli ms[2][0] != "shell":
                ms.insert(2, ("shell", "She_ll"))
        self.interp = ModifiedInterpreter(self)
        jeżeli flist jest Nic:
            root = Tk()
            fixwordbreaks(root)
            root.withdraw()
            flist = PyShellFileList(root)
        #
        OutputWindow.__init__(self, flist, Nic, Nic)
        #
##        self.config(usetabs=1, indentwidth=8, context_use_ps1=1)
        self.usetabs = Prawda
        # indentwidth must be 8 when using tabs.  See note w EditorWindow:
        self.indentwidth = 8
        self.context_use_ps1 = Prawda
        #
        text = self.text
        text.configure(wrap="char")
        text.bind("<<newline-and-indent>>", self.enter_callback)
        text.bind("<<plain-newline-and-indent>>", self.linefeed_callback)
        text.bind("<<interrupt-execution>>", self.cancel_callback)
        text.bind("<<end-of-file>>", self.eof_callback)
        text.bind("<<open-stack-viewer>>", self.open_stack_viewer)
        text.bind("<<toggle-debugger>>", self.toggle_debugger)
        text.bind("<<toggle-jit-stack-viewer>>", self.toggle_jit_stack_viewer)
        jeżeli use_subprocess:
            text.bind("<<view-restart>>", self.view_restart_mark)
            text.bind("<<restart-shell>>", self.restart_shell)
        #
        self.save_stdout = sys.stdout
        self.save_stderr = sys.stderr
        self.save_stdin = sys.stdin
        z idlelib zaimportuj IOBinding
        self.stdin = PseudoInputFile(self, "stdin", IOBinding.encoding)
        self.stdout = PseudoOutputFile(self, "stdout", IOBinding.encoding)
        self.stderr = PseudoOutputFile(self, "stderr", IOBinding.encoding)
        self.console = PseudoOutputFile(self, "console", IOBinding.encoding)
        jeżeli nie use_subprocess:
            sys.stdout = self.stdout
            sys.stderr = self.stderr
            sys.stdin = self.stdin
        spróbuj:
            # page help() text to shell.
            zaimportuj pydoc # zaimportuj must be done here to capture i/o rebinding.
            # XXX KBK 27Dec07 use a textView someday, but must work w/o subproc
            pydoc.pager = pydoc.plainpager
        wyjąwszy:
            sys.stderr = sys.__stderr__
            podnieś
        #
        self.history = self.History(self.text)
        #
        self.pollinterval = 50  # millisec

    def get_standard_extension_names(self):
        zwróć idleConf.GetExtensions(shell_only=Prawda)

    reading = Nieprawda
    executing = Nieprawda
    canceled = Nieprawda
    endoffile = Nieprawda
    closing = Nieprawda
    _stop_readline_flag = Nieprawda

    def set_warning_stream(self, stream):
        global warning_stream
        warning_stream = stream

    def get_warning_stream(self):
        zwróć warning_stream

    def toggle_debugger(self, event=Nic):
        jeżeli self.executing:
            tkMessageBox.showerror("Don't debug now",
                "You can only toggle the debugger when idle",
                master=self.text)
            self.set_debugger_indicator()
            zwróć "break"
        inaczej:
            db = self.interp.getdebugger()
            jeżeli db:
                self.close_debugger()
            inaczej:
                self.open_debugger()

    def set_debugger_indicator(self):
        db = self.interp.getdebugger()
        self.setvar("<<toggle-debugger>>", nie not db)

    def toggle_jit_stack_viewer(self, event=Nic):
        dalej # All we need jest the variable

    def close_debugger(self):
        db = self.interp.getdebugger()
        jeżeli db:
            self.interp.setdebugger(Nic)
            db.close()
            jeżeli self.interp.rpcclt:
                RemoteDebugger.close_remote_debugger(self.interp.rpcclt)
            self.resetoutput()
            self.console.write("[DEBUG OFF]\n")
            sys.ps1 = ">>> "
            self.showprompt()
        self.set_debugger_indicator()

    def open_debugger(self):
        jeżeli self.interp.rpcclt:
            dbg_gui = RemoteDebugger.start_remote_debugger(self.interp.rpcclt,
                                                           self)
        inaczej:
            dbg_gui = Debugger.Debugger(self)
        self.interp.setdebugger(dbg_gui)
        dbg_gui.load_breakpoints()
        sys.ps1 = "[DEBUG ON]\n>>> "
        self.showprompt()
        self.set_debugger_indicator()

    def beginexecuting(self):
        "Helper dla ModifiedInterpreter"
        self.resetoutput()
        self.executing = 1

    def endexecuting(self):
        "Helper dla ModifiedInterpreter"
        self.executing = 0
        self.canceled = 0
        self.showprompt()

    def close(self):
        "Extend EditorWindow.close()"
        jeżeli self.executing:
            response = tkMessageBox.askokcancel(
                "Kill?",
                "The program jest still running!\n Do you want to kill it?",
                default="ok",
                parent=self.text)
            jeżeli response jest Nieprawda:
                zwróć "cancel"
        self.stop_readline()
        self.canceled = Prawda
        self.closing = Prawda
        zwróć EditorWindow.close(self)

    def _close(self):
        "Extend EditorWindow._close(), shut down debugger oraz execution server"
        self.close_debugger()
        jeżeli use_subprocess:
            self.interp.kill_subprocess()
        # Restore std streams
        sys.stdout = self.save_stdout
        sys.stderr = self.save_stderr
        sys.stdin = self.save_stdin
        # Break cycles
        self.interp = Nic
        self.console = Nic
        self.flist.pyshell = Nic
        self.history = Nic
        EditorWindow._close(self)

    def ispythonsource(self, filename):
        "Override EditorWindow method: never remove the colorizer"
        zwróć Prawda

    def short_title(self):
        zwróć self.shell_title

    COPYRIGHT = \
          'Type "copyright", "credits" albo "license()" dla more information.'

    def begin(self):
        self.text.mark_set("iomark", "insert")
        self.resetoutput()
        jeżeli use_subprocess:
            nosub = ''
            client = self.interp.start_subprocess()
            jeżeli nie client:
                self.close()
                zwróć Nieprawda
        inaczej:
            nosub = ("==== No Subprocess ====\n\n" +
                    "WARNING: Running IDLE without a Subprocess jest deprecated\n" +
                    "and will be removed w a later version. See Help/IDLE Help\n" +
                    "dla details.\n\n")
            sys.displayhook = rpc.displayhook

        self.write("Python %s on %s\n%s\n%s" %
                   (sys.version, sys.platform, self.COPYRIGHT, nosub))
        self.showprompt()
        zaimportuj tkinter
        tkinter._default_root = Nic # 03Jan04 KBK What's this?
        zwróć Prawda

    def stop_readline(self):
        jeżeli nie self.reading:  # no nested mainloop to exit.
            zwróć
        self._stop_readline_flag = Prawda
        self.top.quit()

    def readline(self):
        save = self.reading
        spróbuj:
            self.reading = 1
            self.top.mainloop()  # nested mainloop()
        w_końcu:
            self.reading = save
        jeżeli self._stop_readline_flag:
            self._stop_readline_flag = Nieprawda
            zwróć ""
        line = self.text.get("iomark", "end-1c")
        jeżeli len(line) == 0:  # may be EOF jeżeli we quit our mainloop przy Ctrl-C
            line = "\n"
        self.resetoutput()
        jeżeli self.canceled:
            self.canceled = 0
            jeżeli nie use_subprocess:
                podnieś KeyboardInterrupt
        jeżeli self.endoffile:
            self.endoffile = 0
            line = ""
        zwróć line

    def isatty(self):
        zwróć Prawda

    def cancel_callback(self, event=Nic):
        spróbuj:
            jeżeli self.text.compare("sel.first", "!=", "sel.last"):
                zwróć # Active selection -- always use default binding
        wyjąwszy:
            dalej
        jeżeli nie (self.executing albo self.reading):
            self.resetoutput()
            self.interp.write("KeyboardInterrupt\n")
            self.showprompt()
            zwróć "break"
        self.endoffile = 0
        self.canceled = 1
        jeżeli (self.executing oraz self.interp.rpcclt):
            jeżeli self.interp.getdebugger():
                self.interp.restart_subprocess()
            inaczej:
                self.interp.interrupt_subprocess()
        jeżeli self.reading:
            self.top.quit()  # exit the nested mainloop() w readline()
        zwróć "break"

    def eof_callback(self, event):
        jeżeli self.executing oraz nie self.reading:
            zwróć # Let the default binding (delete next char) take over
        jeżeli nie (self.text.compare("iomark", "==", "insert") oraz
                self.text.compare("insert", "==", "end-1c")):
            zwróć # Let the default binding (delete next char) take over
        jeżeli nie self.executing:
            self.resetoutput()
            self.close()
        inaczej:
            self.canceled = 0
            self.endoffile = 1
            self.top.quit()
        zwróć "break"

    def linefeed_callback(self, event):
        # Insert a linefeed without entering anything (still autoindented)
        jeżeli self.reading:
            self.text.insert("insert", "\n")
            self.text.see("insert")
        inaczej:
            self.newline_and_indent_event(event)
        zwróć "break"

    def enter_callback(self, event):
        jeżeli self.executing oraz nie self.reading:
            zwróć # Let the default binding (insert '\n') take over
        # If some text jest selected, recall the selection
        # (but only jeżeli this before the I/O mark)
        spróbuj:
            sel = self.text.get("sel.first", "sel.last")
            jeżeli sel:
                jeżeli self.text.compare("sel.last", "<=", "iomark"):
                    self.recall(sel, event)
                    zwróć "break"
        wyjąwszy:
            dalej
        # If we're strictly before the line containing iomark, recall
        # the current line, less a leading prompt, less leading albo
        # trailing whitespace
        jeżeli self.text.compare("insert", "<", "iomark linestart"):
            # Check jeżeli there's a relevant stdin range -- jeżeli so, use it
            prev = self.text.tag_prevrange("stdin", "insert")
            jeżeli prev oraz self.text.compare("insert", "<", prev[1]):
                self.recall(self.text.get(prev[0], prev[1]), event)
                zwróć "break"
            next = self.text.tag_nextrange("stdin", "insert")
            jeżeli next oraz self.text.compare("insert lineend", ">=", next[0]):
                self.recall(self.text.get(next[0], next[1]), event)
                zwróć "break"
            # No stdin mark -- just get the current line, less any prompt
            indices = self.text.tag_nextrange("console", "insert linestart")
            jeżeli indices oraz \
               self.text.compare(indices[0], "<=", "insert linestart"):
                self.recall(self.text.get(indices[1], "insert lineend"), event)
            inaczej:
                self.recall(self.text.get("insert linestart", "insert lineend"), event)
            zwróć "break"
        # If we're between the beginning of the line oraz the iomark, i.e.
        # w the prompt area, move to the end of the prompt
        jeżeli self.text.compare("insert", "<", "iomark"):
            self.text.mark_set("insert", "iomark")
        # If we're w the current input oraz there's only whitespace
        # beyond the cursor, erase that whitespace first
        s = self.text.get("insert", "end-1c")
        jeżeli s oraz nie s.strip():
            self.text.delete("insert", "end-1c")
        # If we're w the current input before its last line,
        # insert a newline right at the insert point
        jeżeli self.text.compare("insert", "<", "end-1c linestart"):
            self.newline_and_indent_event(event)
            zwróć "break"
        # We're w the last line; append a newline oraz submit it
        self.text.mark_set("insert", "end-1c")
        jeżeli self.reading:
            self.text.insert("insert", "\n")
            self.text.see("insert")
        inaczej:
            self.newline_and_indent_event(event)
        self.text.tag_add("stdin", "iomark", "end-1c")
        self.text.update_idletasks()
        jeżeli self.reading:
            self.top.quit() # Break out of recursive mainloop()
        inaczej:
            self.runit()
        zwróć "break"

    def recall(self, s, event):
        # remove leading oraz trailing empty albo whitespace lines
        s = re.sub(r'^\s*\n', '' , s)
        s = re.sub(r'\n\s*$', '', s)
        lines = s.split('\n')
        self.text.undo_block_start()
        spróbuj:
            self.text.tag_remove("sel", "1.0", "end")
            self.text.mark_set("insert", "end-1c")
            prefix = self.text.get("insert linestart", "insert")
            jeżeli prefix.rstrip().endswith(':'):
                self.newline_and_indent_event(event)
                prefix = self.text.get("insert linestart", "insert")
            self.text.insert("insert", lines[0].strip())
            jeżeli len(lines) > 1:
                orig_base_indent = re.search(r'^([ \t]*)', lines[0]).group(0)
                new_base_indent  = re.search(r'^([ \t]*)', prefix).group(0)
                dla line w lines[1:]:
                    jeżeli line.startswith(orig_base_indent):
                        # replace orig base indentation przy new indentation
                        line = new_base_indent + line[len(orig_base_indent):]
                    self.text.insert('insert', '\n'+line.rstrip())
        w_końcu:
            self.text.see("insert")
            self.text.undo_block_stop()

    def runit(self):
        line = self.text.get("iomark", "end-1c")
        # Strip off last newline oraz surrounding whitespace.
        # (To allow you to hit zwróć twice to end a statement.)
        i = len(line)
        dopóki i > 0 oraz line[i-1] w " \t":
            i = i-1
        jeżeli i > 0 oraz line[i-1] == "\n":
            i = i-1
        dopóki i > 0 oraz line[i-1] w " \t":
            i = i-1
        line = line[:i]
        self.interp.runsource(line)

    def open_stack_viewer(self, event=Nic):
        jeżeli self.interp.rpcclt:
            zwróć self.interp.remote_stack_viewer()
        spróbuj:
            sys.last_traceback
        wyjąwszy:
            tkMessageBox.showerror("No stack trace",
                "There jest no stack trace yet.\n"
                "(sys.last_traceback jest nie defined)",
                master=self.text)
            zwróć
        z idlelib.StackViewer zaimportuj StackBrowser
        StackBrowser(self.root, self.flist)

    def view_restart_mark(self, event=Nic):
        self.text.see("iomark")
        self.text.see("restart")

    def restart_shell(self, event=Nic):
        "Callback dla Run/Restart Shell Cntl-F6"
        self.interp.restart_subprocess(with_cwd=Prawda)

    def showprompt(self):
        self.resetoutput()
        spróbuj:
            s = str(sys.ps1)
        wyjąwszy:
            s = ""
        self.console.write(s)
        self.text.mark_set("insert", "end-1c")
        self.set_line_and_column()
        self.io.reset_undo()

    def resetoutput(self):
        source = self.text.get("iomark", "end-1c")
        jeżeli self.history:
            self.history.store(source)
        jeżeli self.text.get("end-2c") != "\n":
            self.text.insert("end-1c", "\n")
        self.text.mark_set("iomark", "end-1c")
        self.set_line_and_column()

    def write(self, s, tags=()):
        jeżeli isinstance(s, str) oraz len(s) oraz max(s) > '\uffff':
            # Tk doesn't support outputting non-BMP characters
            # Let's assume what printed string jest nie very long,
            # find first non-BMP character oraz construct informative
            # UnicodeEncodeError exception.
            dla start, char w enumerate(s):
                jeżeli char > '\uffff':
                    przerwij
            podnieś UnicodeEncodeError("UCS-2", char, start, start+1,
                                     'Non-BMP character nie supported w Tk')
        spróbuj:
            self.text.mark_gravity("iomark", "right")
            count = OutputWindow.write(self, s, tags, "iomark")
            self.text.mark_gravity("iomark", "left")
        wyjąwszy:
            podnieś ###pass  # ### 11Aug07 KBK jeżeli we are expecting exceptions
                           # let's find out what they are oraz be specific.
        jeżeli self.canceled:
            self.canceled = 0
            jeżeli nie use_subprocess:
                podnieś KeyboardInterrupt
        zwróć count

    def rmenu_check_cut(self):
        spróbuj:
            jeżeli self.text.compare('sel.first', '<', 'iomark'):
                zwróć 'disabled'
        wyjąwszy TclError: # no selection, so the index 'sel.first' doesn't exist
            zwróć 'disabled'
        zwróć super().rmenu_check_cut()

    def rmenu_check_paste(self):
        jeżeli self.text.compare('insert','<','iomark'):
            zwróć 'disabled'
        zwróć super().rmenu_check_paste()

klasa PseudoFile(io.TextIOBase):

    def __init__(self, shell, tags, encoding=Nic):
        self.shell = shell
        self.tags = tags
        self._encoding = encoding

    @property
    def encoding(self):
        zwróć self._encoding

    @property
    def name(self):
        zwróć '<%s>' % self.tags

    def isatty(self):
        zwróć Prawda


klasa PseudoOutputFile(PseudoFile):

    def writable(self):
        zwróć Prawda

    def write(self, s):
        jeżeli self.closed:
            podnieś ValueError("write to closed file")
        jeżeli type(s) jest nie str:
            jeżeli nie isinstance(s, str):
                podnieś TypeError('must be str, nie ' + type(s).__name__)
            # See issue #19481
            s = str.__str__(s)
        zwróć self.shell.write(s, self.tags)


klasa PseudoInputFile(PseudoFile):

    def __init__(self, shell, tags, encoding=Nic):
        PseudoFile.__init__(self, shell, tags, encoding)
        self._line_buffer = ''

    def readable(self):
        zwróć Prawda

    def read(self, size=-1):
        jeżeli self.closed:
            podnieś ValueError("read z closed file")
        jeżeli size jest Nic:
            size = -1
        albo_inaczej nie isinstance(size, int):
            podnieś TypeError('must be int, nie ' + type(size).__name__)
        result = self._line_buffer
        self._line_buffer = ''
        jeżeli size < 0:
            dopóki Prawda:
                line = self.shell.readline()
                jeżeli nie line: przerwij
                result += line
        inaczej:
            dopóki len(result) < size:
                line = self.shell.readline()
                jeżeli nie line: przerwij
                result += line
            self._line_buffer = result[size:]
            result = result[:size]
        zwróć result

    def readline(self, size=-1):
        jeżeli self.closed:
            podnieś ValueError("read z closed file")
        jeżeli size jest Nic:
            size = -1
        albo_inaczej nie isinstance(size, int):
            podnieś TypeError('must be int, nie ' + type(size).__name__)
        line = self._line_buffer albo self.shell.readline()
        jeżeli size < 0:
            size = len(line)
        eol = line.find('\n', 0, size)
        jeżeli eol >= 0:
            size = eol + 1
        self._line_buffer = line[size:]
        zwróć line[:size]

    def close(self):
        self.shell.close()


usage_msg = """\

USAGE: idle  [-deins] [-t title] [file]*
       idle  [-dns] [-t title] (-c cmd | -r file) [arg]*
       idle  [-dns] [-t title] - [arg]*

  -h         print this help message oraz exit
  -n         run IDLE without a subprocess (DEPRECATED,
             see Help/IDLE Help dla details)

The following options will override the IDLE 'settings' configuration:

  -e         open an edit window
  -i         open a shell window

The following options imply -i oraz will open a shell:

  -c cmd     run the command w a shell, albo
  -r file    run script z file

  -d         enable the debugger
  -s         run $IDLESTARTUP albo $PYTHONSTARTUP before anything inaczej
  -t title   set title of shell window

A default edit window will be bypassed when -c, -r, albo - are used.

[arg]* are dalejed to the command (-c) albo script (-r) w sys.argv[1:].

Examples:

idle
        Open an edit window albo shell depending on IDLE's configuration.

idle foo.py foobar.py
        Edit the files, also open a shell jeżeli configured to start przy shell.

idle -est "Baz" foo.py
        Run $IDLESTARTUP albo $PYTHONSTARTUP, edit foo.py, oraz open a shell
        window przy the title "Baz".

idle -c "zaimportuj sys; print(sys.argv)" "foo"
        Open a shell window oraz run the command, dalejing "-c" w sys.argv[0]
        oraz "foo" w sys.argv[1].

idle -d -s -r foo.py "Hello World"
        Open a shell window, run a startup script, enable the debugger, oraz
        run foo.py, dalejing "foo.py" w sys.argv[0] oraz "Hello World" w
        sys.argv[1].

echo "zaimportuj sys; print(sys.argv)" | idle - "foobar"
        Open a shell window, run the script piped in, dalejing '' w sys.argv[0]
        oraz "foobar" w sys.argv[1].
"""

def main():
    global flist, root, use_subprocess

    capture_warnings(Prawda)
    use_subprocess = Prawda
    enable_shell = Nieprawda
    enable_edit = Nieprawda
    debug = Nieprawda
    cmd = Nic
    script = Nic
    startup = Nieprawda
    spróbuj:
        opts, args = getopt.getopt(sys.argv[1:], "c:deihnr:st:")
    wyjąwszy getopt.error jako msg:
        print("Error: %s\n%s" % (msg, usage_msg), file=sys.stderr)
        sys.exit(2)
    dla o, a w opts:
        jeżeli o == '-c':
            cmd = a
            enable_shell = Prawda
        jeżeli o == '-d':
            debug = Prawda
            enable_shell = Prawda
        jeżeli o == '-e':
            enable_edit = Prawda
        jeżeli o == '-h':
            sys.stdout.write(usage_msg)
            sys.exit()
        jeżeli o == '-i':
            enable_shell = Prawda
        jeżeli o == '-n':
            print(" Warning: running IDLE without a subprocess jest deprecated.",
                  file=sys.stderr)
            use_subprocess = Nieprawda
        jeżeli o == '-r':
            script = a
            jeżeli os.path.isfile(script):
                dalej
            inaczej:
                print("No script file: ", script)
                sys.exit()
            enable_shell = Prawda
        jeżeli o == '-s':
            startup = Prawda
            enable_shell = Prawda
        jeżeli o == '-t':
            PyShell.shell_title = a
            enable_shell = Prawda
    jeżeli args oraz args[0] == '-':
        cmd = sys.stdin.read()
        enable_shell = Prawda
    # process sys.argv oraz sys.path:
    dla i w range(len(sys.path)):
        sys.path[i] = os.path.abspath(sys.path[i])
    jeżeli args oraz args[0] == '-':
        sys.argv = [''] + args[1:]
    albo_inaczej cmd:
        sys.argv = ['-c'] + args
    albo_inaczej script:
        sys.argv = [script] + args
    albo_inaczej args:
        enable_edit = Prawda
        pathx = []
        dla filename w args:
            pathx.append(os.path.dirname(filename))
        dla dir w pathx:
            dir = os.path.abspath(dir)
            jeżeli nie dir w sys.path:
                sys.path.insert(0, dir)
    inaczej:
        dir = os.getcwd()
        jeżeli dir nie w sys.path:
            sys.path.insert(0, dir)
    # check the IDLE settings configuration (but command line overrides)
    edit_start = idleConf.GetOption('main', 'General',
                                    'editor-on-startup', type='bool')
    enable_edit = enable_edit albo edit_start
    enable_shell = enable_shell albo nie enable_edit
    # start editor and/or shell windows:
    root = Tk(className="Idle")

    # set application icon
    icondir = os.path.join(os.path.dirname(__file__), 'Icons')
    jeżeli system() == 'Windows':
        iconfile = os.path.join(icondir, 'idle.ico')
        root.wm_iconbitmap(default=iconfile)
    albo_inaczej TkVersion >= 8.5:
        ext = '.png' jeżeli TkVersion >= 8.6 inaczej '.gif'
        iconfiles = [os.path.join(icondir, 'idle_%d%s' % (size, ext))
                     dla size w (16, 32, 48)]
        icons = [PhotoImage(file=iconfile) dla iconfile w iconfiles]
        root.wm_iconphoto(Prawda, *icons)

    fixwordbreaks(root)
    root.withdraw()
    flist = PyShellFileList(root)
    macosxSupport.setupApp(root, flist)

    jeżeli enable_edit:
        jeżeli nie (cmd albo script):
            dla filename w args[:]:
                jeżeli flist.open(filename) jest Nic:
                    # filename jest a directory actually, disconsider it
                    args.remove(filename)
            jeżeli nie args:
                flist.new()

    jeżeli enable_shell:
        shell = flist.open_shell()
        jeżeli nie shell:
            zwróć # couldn't open shell
        jeżeli macosxSupport.isAquaTk() oraz flist.dict:
            # On OSX: when the user has double-clicked on a file that causes
            # IDLE to be launched the shell window will open just w front of
            # the file she wants to see. Lower the interpreter window when
            # there are open files.
            shell.top.lower()
    inaczej:
        shell = flist.pyshell

    # Handle remaining options. If any of these are set, enable_shell
    # was set also, so shell must be true to reach here.
    jeżeli debug:
        shell.open_debugger()
    jeżeli startup:
        filename = os.environ.get("IDLESTARTUP") albo \
                   os.environ.get("PYTHONSTARTUP")
        jeżeli filename oraz os.path.isfile(filename):
            shell.interp.execfile(filename)
    jeżeli cmd albo script:
        shell.interp.runcommand("""jeżeli 1:
            zaimportuj sys jako _sys
            _sys.argv = %r
            usuń _sys
            \n""" % (sys.argv,))
        jeżeli cmd:
            shell.interp.execsource(cmd)
        albo_inaczej script:
            shell.interp.prepend_syspath(script)
            shell.interp.execfile(script)
    albo_inaczej shell:
        # If there jest a shell window oraz no cmd albo script w progress,
        # check dla problematic OS X Tk versions oraz print a warning
        # message w the IDLE shell window; this jest less intrusive
        # than always opening a separate window.
        tkversionwarning = macosxSupport.tkVersionWarning(root)
        jeżeli tkversionwarning:
            shell.interp.runcommand("print('%s')" % tkversionwarning)

    dopóki flist.inversedict:  # keep IDLE running dopóki files are open.
        root.mainloop()
    root.destroy()
    capture_warnings(Nieprawda)

jeżeli __name__ == "__main__":
    sys.modules['PyShell'] = sys.modules['__main__']
    main()

capture_warnings(Nieprawda)  # Make sure turned off; see issue 18081
