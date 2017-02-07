zaimportuj sys
zaimportuj linecache
zaimportuj time
zaimportuj traceback
zaimportuj _thread jako thread
zaimportuj threading
zaimportuj queue
zaimportuj tkinter

z idlelib zaimportuj CallTips
z idlelib zaimportuj AutoComplete

z idlelib zaimportuj RemoteDebugger
z idlelib zaimportuj RemoteObjectBrowser
z idlelib zaimportuj StackViewer
z idlelib zaimportuj rpc
z idlelib zaimportuj PyShell
z idlelib zaimportuj IOBinding

zaimportuj __main__

LOCALHOST = '127.0.0.1'

zaimportuj warnings

def idle_showwarning_subproc(
        message, category, filename, lineno, file=Nic, line=Nic):
    """Show Idle-format warning after replacing warnings.showwarning.

    The only difference jest the formatter called.
    """
    jeżeli file jest Nic:
        file = sys.stderr
    spróbuj:
        file.write(PyShell.idle_formatwarning(
                message, category, filename, lineno, line))
    wyjąwszy IOError:
        dalej # the file (probably stderr) jest invalid - this warning gets lost.

_warnings_showwarning = Nic

def capture_warnings(capture):
    "Replace warning.showwarning przy idle_showwarning_subproc, albo reverse."

    global _warnings_showwarning
    jeżeli capture:
        jeżeli _warnings_showwarning jest Nic:
            _warnings_showwarning = warnings.showwarning
            warnings.showwarning = idle_showwarning_subproc
    inaczej:
        jeżeli _warnings_showwarning jest nie Nic:
            warnings.showwarning = _warnings_showwarning
            _warnings_showwarning = Nic

capture_warnings(Prawda)
tcl = tkinter.Tcl()

def handle_tk_events(tcl=tcl):
    """Process any tk events that are ready to be dispatched jeżeli tkinter
    has been imported, a tcl interpreter has been created oraz tk has been
    loaded."""
    tcl.eval("update")

# Thread shared globals: Establish a queue between a subthread (which handles
# the socket) oraz the main thread (which runs user code), plus global
# completion, exit oraz interruptable (the main thread) flags:

exit_now = Nieprawda
quitting = Nieprawda
interruptable = Nieprawda

def main(del_exitfunc=Nieprawda):
    """Start the Python execution server w a subprocess

    In the Python subprocess, RPCServer jest instantiated przy handlerclass
    MyHandler, which inherits register/unregister methods z RPCHandler via
    the mix-in klasa SocketIO.

    When the RPCServer 'server' jest instantiated, the TCPServer initialization
    creates an instance of run.MyHandler oraz calls its handle() method.
    handle() instantiates a run.Executive object, dalejing it a reference to the
    MyHandler object.  That reference jest saved jako attribute rpchandler of the
    Executive instance.  The Executive methods have access to the reference oraz
    can dalej it on to entities that they command
    (e.g. RemoteDebugger.Debugger.start_debugger()).  The latter, w turn, can
    call MyHandler(SocketIO) register/unregister methods via the reference to
    register oraz unregister themselves.

    """
    global exit_now
    global quitting
    global no_exitfunc
    no_exitfunc = del_exitfunc
    #time.sleep(15) # test subprocess nie responding
    spróbuj:
        assert(len(sys.argv) > 1)
        port = int(sys.argv[-1])
    wyjąwszy:
        print("IDLE Subprocess: no IP port dalejed w sys.argv.",
              file=sys.__stderr__)
        zwróć

    capture_warnings(Prawda)
    sys.argv[:] = [""]
    sockthread = threading.Thread(target=manage_socket,
                                  name='SockThread',
                                  args=((LOCALHOST, port),))
    sockthread.daemon = Prawda
    sockthread.start()
    dopóki 1:
        spróbuj:
            jeżeli exit_now:
                spróbuj:
                    exit()
                wyjąwszy KeyboardInterrupt:
                    # exiting but got an extra KBI? Try again!
                    kontynuuj
            spróbuj:
                seq, request = rpc.request_queue.get(block=Prawda, timeout=0.05)
            wyjąwszy queue.Empty:
                handle_tk_events()
                kontynuuj
            method, args, kwargs = request
            ret = method(*args, **kwargs)
            rpc.response_queue.put((seq, ret))
        wyjąwszy KeyboardInterrupt:
            jeżeli quitting:
                exit_now = Prawda
            kontynuuj
        wyjąwszy SystemExit:
            capture_warnings(Nieprawda)
            podnieś
        wyjąwszy:
            type, value, tb = sys.exc_info()
            spróbuj:
                print_exception()
                rpc.response_queue.put((seq, Nic))
            wyjąwszy:
                # Link didn't work, print same exception to __stderr__
                traceback.print_exception(type, value, tb, file=sys.__stderr__)
                exit()
            inaczej:
                kontynuuj

def manage_socket(address):
    dla i w range(3):
        time.sleep(i)
        spróbuj:
            server = MyRPCServer(address, MyHandler)
            przerwij
        wyjąwszy OSError jako err:
            print("IDLE Subprocess: OSError: " + err.args[1] +
                  ", retrying....", file=sys.__stderr__)
            socket_error = err
    inaczej:
        print("IDLE Subprocess: Connection to "
              "IDLE GUI failed, exiting.", file=sys.__stderr__)
        show_socket_error(socket_error, address)
        global exit_now
        exit_now = Prawda
        zwróć
    server.handle_request() # A single request only

def show_socket_error(err, address):
    zaimportuj tkinter
    zaimportuj tkinter.messagebox jako tkMessageBox
    root = tkinter.Tk()
    root.withdraw()
    jeżeli err.args[0] == 61: # connection refused
        msg = "IDLE's subprocess can't connect to %s:%d.  This may be due "\
              "to your personal firewall configuration.  It jest safe to "\
              "allow this internal connection because no data jest visible on "\
              "external ports." % address
        tkMessageBox.showerror("IDLE Subprocess Error", msg, parent=root)
    inaczej:
        tkMessageBox.showerror("IDLE Subprocess Error",
                               "Socket Error: %s" % err.args[1])
    root.destroy()

def print_exception():
    zaimportuj linecache
    linecache.checkcache()
    flush_stdout()
    efile = sys.stderr
    typ, val, tb = excinfo = sys.exc_info()
    sys.last_type, sys.last_value, sys.last_traceback = excinfo
    seen = set()

    def print_exc(typ, exc, tb):
        seen.add(exc)
        context = exc.__context__
        cause = exc.__cause__
        jeżeli cause jest nie Nic oraz cause nie w seen:
            print_exc(type(cause), cause, cause.__traceback__)
            print("\nThe above exception was the direct cause "
                  "of the following exception:\n", file=efile)
        albo_inaczej (context jest nie Nic oraz
              nie exc.__suppress_context__ oraz
              context nie w seen):
            print_exc(type(context), context, context.__traceback__)
            print("\nDuring handling of the above exception, "
                  "another exception occurred:\n", file=efile)
        jeżeli tb:
            tbe = traceback.extract_tb(tb)
            print('Traceback (most recent call last):', file=efile)
            exclude = ("run.py", "rpc.py", "threading.py", "queue.py",
                       "RemoteDebugger.py", "bdb.py")
            cleanup_traceback(tbe, exclude)
            traceback.print_list(tbe, file=efile)
        lines = traceback.format_exception_only(typ, exc)
        dla line w lines:
            print(line, end='', file=efile)

    print_exc(typ, val, tb)

def cleanup_traceback(tb, exclude):
    "Remove excluded traces z beginning/end of tb; get cached lines"
    orig_tb = tb[:]
    dopóki tb:
        dla rpcfile w exclude:
            jeżeli tb[0][0].count(rpcfile):
                przerwij    # found an exclude, przerwij for: oraz delete tb[0]
        inaczej:
            przerwij        # no excludes, have left RPC code, przerwij while:
        usuń tb[0]
    dopóki tb:
        dla rpcfile w exclude:
            jeżeli tb[-1][0].count(rpcfile):
                przerwij
        inaczej:
            przerwij
        usuń tb[-1]
    jeżeli len(tb) == 0:
        # exception was w IDLE internals, don't prune!
        tb[:] = orig_tb[:]
        print("** IDLE Internal Exception: ", file=sys.stderr)
    rpchandler = rpc.objecttable['exec'].rpchandler
    dla i w range(len(tb)):
        fn, ln, nm, line = tb[i]
        jeżeli nm == '?':
            nm = "-toplevel-"
        jeżeli nie line oraz fn.startswith("<pyshell#"):
            line = rpchandler.remotecall('linecache', 'getline',
                                              (fn, ln), {})
        tb[i] = fn, ln, nm, line

def flush_stdout():
    """XXX How to do this now?"""

def exit():
    """Exit subprocess, possibly after first clearing exit functions.

    If config-main.cfg/.def 'General' 'delete-exitfunc' jest Prawda, then any
    functions registered przy atexit will be removed before exiting.
    (VPython support)

    """
    jeżeli no_exitfunc:
        zaimportuj atexit
        atexit._clear()
    capture_warnings(Nieprawda)
    sys.exit(0)

klasa MyRPCServer(rpc.RPCServer):

    def handle_error(self, request, client_address):
        """Override RPCServer method dla IDLE

        Interrupt the MainThread oraz exit server jeżeli link jest dropped.

        """
        global quitting
        spróbuj:
            podnieś
        wyjąwszy SystemExit:
            podnieś
        wyjąwszy EOFError:
            global exit_now
            exit_now = Prawda
            thread.interrupt_main()
        wyjąwszy:
            erf = sys.__stderr__
            print('\n' + '-'*40, file=erf)
            print('Unhandled server exception!', file=erf)
            print('Thread: %s' % threading.current_thread().name, file=erf)
            print('Client Address: ', client_address, file=erf)
            print('Request: ', repr(request), file=erf)
            traceback.print_exc(file=erf)
            print('\n*** Unrecoverable, server exiting!', file=erf)
            print('-'*40, file=erf)
            quitting = Prawda
            thread.interrupt_main()

klasa MyHandler(rpc.RPCHandler):

    def handle(self):
        """Override base method"""
        executive = Executive(self)
        self.register("exec", executive)
        self.console = self.get_remote_proxy("console")
        sys.stdin = PyShell.PseudoInputFile(self.console, "stdin",
                IOBinding.encoding)
        sys.stdout = PyShell.PseudoOutputFile(self.console, "stdout",
                IOBinding.encoding)
        sys.stderr = PyShell.PseudoOutputFile(self.console, "stderr",
                IOBinding.encoding)

        sys.displayhook = rpc.displayhook
        # page help() text to shell.
        zaimportuj pydoc # zaimportuj must be done here to capture i/o binding
        pydoc.pager = pydoc.plainpager

        # Keep a reference to stdin so that it won't try to exit IDLE if
        # sys.stdin gets changed z within IDLE's shell. See issue17838.
        self._keep_stdin = sys.stdin

        self.interp = self.get_remote_proxy("interp")
        rpc.RPCHandler.getresponse(self, myseq=Nic, wait=0.05)

    def exithook(self):
        "override SocketIO method - wait dla MainThread to shut us down"
        time.sleep(10)

    def EOFhook(self):
        "Override SocketIO method - terminate wait on callback oraz exit thread"
        global quitting
        quitting = Prawda
        thread.interrupt_main()

    def decode_interrupthook(self):
        "interrupt awakened thread"
        global quitting
        quitting = Prawda
        thread.interrupt_main()


klasa Executive(object):

    def __init__(self, rpchandler):
        self.rpchandler = rpchandler
        self.locals = __main__.__dict__
        self.calltip = CallTips.CallTips()
        self.autocomplete = AutoComplete.AutoComplete()

    def runcode(self, code):
        global interruptable
        spróbuj:
            self.usr_exc_info = Nic
            interruptable = Prawda
            spróbuj:
                exec(code, self.locals)
            w_końcu:
                interruptable = Nieprawda
        wyjąwszy SystemExit:
            # Scripts that podnieś SystemExit should just
            # zwróć to the interactive prompt
            dalej
        wyjąwszy:
            self.usr_exc_info = sys.exc_info()
            jeżeli quitting:
                exit()
            # even print a user code SystemExit exception, kontynuuj
            print_exception()
            jit = self.rpchandler.console.getvar("<<toggle-jit-stack-viewer>>")
            jeżeli jit:
                self.rpchandler.interp.open_remote_stack_viewer()
        inaczej:
            flush_stdout()

    def interrupt_the_server(self):
        jeżeli interruptable:
            thread.interrupt_main()

    def start_the_debugger(self, gui_adap_oid):
        zwróć RemoteDebugger.start_debugger(self.rpchandler, gui_adap_oid)

    def stop_the_debugger(self, idb_adap_oid):
        "Unregister the Idb Adapter.  Link objects oraz Idb then subject to GC"
        self.rpchandler.unregister(idb_adap_oid)

    def get_the_calltip(self, name):
        zwróć self.calltip.fetch_tip(name)

    def get_the_completion_list(self, what, mode):
        zwróć self.autocomplete.fetch_completions(what, mode)

    def stackviewer(self, flist_oid=Nic):
        jeżeli self.usr_exc_info:
            typ, val, tb = self.usr_exc_info
        inaczej:
            zwróć Nic
        flist = Nic
        jeżeli flist_oid jest nie Nic:
            flist = self.rpchandler.get_remote_proxy(flist_oid)
        dopóki tb oraz tb.tb_frame.f_globals["__name__"] w ["rpc", "run"]:
            tb = tb.tb_next
        sys.last_type = typ
        sys.last_value = val
        item = StackViewer.StackTreeItem(flist, tb)
        zwróć RemoteObjectBrowser.remote_object_tree_item(item)

capture_warnings(Nieprawda)  # Make sure turned off; see issue 18081
