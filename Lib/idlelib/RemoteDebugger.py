"""Support dla remote Python debugging.

Some ASCII art to describe the structure:

       IN PYTHON SUBPROCESS          #             IN IDLE PROCESS
                                     #
                                     #        oid='gui_adapter'
                 +----------+        #       +------------+          +-----+
                 | GUIProxy |--remote#call-->| GUIAdapter |--calls-->| GUI |
+-----+--calls-->+----------+        #       +------------+          +-----+
| Idb |                               #                             /
+-----+<-calls--+------------+         #      +----------+<--calls-/
                | IdbAdapter |<--remote#call--| IdbProxy |
                +------------+         #      +----------+
                oid='idb_adapter'      #

The purpose of the Proxy oraz Adapter classes jest to translate certain
arguments oraz zwróć values that cannot be transported through the RPC
barrier, w particular frame oraz traceback objects.

"""

zaimportuj types
z idlelib zaimportuj Debugger

debugging = 0

idb_adap_oid = "idb_adapter"
gui_adap_oid = "gui_adapter"

#=======================================
#
# In the PYTHON subprocess:

frametable = {}
dicttable = {}
codetable = {}
tracebacktable = {}

def wrap_frame(frame):
    fid = id(frame)
    frametable[fid] = frame
    zwróć fid

def wrap_info(info):
    "replace info[2], a traceback instance, by its ID"
    jeżeli info jest Nic:
        zwróć Nic
    inaczej:
        traceback = info[2]
        assert isinstance(traceback, types.TracebackType)
        traceback_id = id(traceback)
        tracebacktable[traceback_id] = traceback
        modified_info = (info[0], info[1], traceback_id)
        zwróć modified_info

klasa GUIProxy:

    def __init__(self, conn, gui_adap_oid):
        self.conn = conn
        self.oid = gui_adap_oid

    def interaction(self, message, frame, info=Nic):
        # calls rpc.SocketIO.remotecall() via run.MyHandler instance
        # dalej frame oraz traceback object IDs instead of the objects themselves
        self.conn.remotecall(self.oid, "interaction",
                             (message, wrap_frame(frame), wrap_info(info)),
                             {})

klasa IdbAdapter:

    def __init__(self, idb):
        self.idb = idb

    #----------called by an IdbProxy----------

    def set_step(self):
        self.idb.set_step()

    def set_quit(self):
        self.idb.set_quit()

    def set_continue(self):
        self.idb.set_continue()

    def set_next(self, fid):
        frame = frametable[fid]
        self.idb.set_next(frame)

    def set_return(self, fid):
        frame = frametable[fid]
        self.idb.set_return(frame)

    def get_stack(self, fid, tbid):
        frame = frametable[fid]
        jeżeli tbid jest Nic:
            tb = Nic
        inaczej:
            tb = tracebacktable[tbid]
        stack, i = self.idb.get_stack(frame, tb)
        stack = [(wrap_frame(frame2), k) dla frame2, k w stack]
        zwróć stack, i

    def run(self, cmd):
        zaimportuj __main__
        self.idb.run(cmd, __main__.__dict__)

    def set_break(self, filename, lineno):
        msg = self.idb.set_break(filename, lineno)
        zwróć msg

    def clear_break(self, filename, lineno):
        msg = self.idb.clear_break(filename, lineno)
        zwróć msg

    def clear_all_file_breaks(self, filename):
        msg = self.idb.clear_all_file_breaks(filename)
        zwróć msg

    #----------called by a FrameProxy----------

    def frame_attr(self, fid, name):
        frame = frametable[fid]
        zwróć getattr(frame, name)

    def frame_globals(self, fid):
        frame = frametable[fid]
        dict = frame.f_globals
        did = id(dict)
        dicttable[did] = dict
        zwróć did

    def frame_locals(self, fid):
        frame = frametable[fid]
        dict = frame.f_locals
        did = id(dict)
        dicttable[did] = dict
        zwróć did

    def frame_code(self, fid):
        frame = frametable[fid]
        code = frame.f_code
        cid = id(code)
        codetable[cid] = code
        zwróć cid

    #----------called by a CodeProxy----------

    def code_name(self, cid):
        code = codetable[cid]
        zwróć code.co_name

    def code_filename(self, cid):
        code = codetable[cid]
        zwróć code.co_filename

    #----------called by a DictProxy----------

    def dict_keys(self, did):
        podnieś NotImplemented("dict_keys nie public albo pickleable")
##         dict = dicttable[did]
##         zwróć dict.keys()

    ### Needed until dict_keys jest type jest finished oraz pickealable.
    ### Will probably need to extend rpc.py:SocketIO._proxify at that time.
    def dict_keys_list(self, did):
        dict = dicttable[did]
        zwróć list(dict.keys())

    def dict_item(self, did, key):
        dict = dicttable[did]
        value = dict[key]
        value = repr(value) ### can't pickle module 'builtins'
        zwróć value

#----------end klasa IdbAdapter----------


def start_debugger(rpchandler, gui_adap_oid):
    """Start the debugger oraz its RPC link w the Python subprocess

    Start the subprocess side of the split debugger oraz set up that side of the
    RPC link by instantiating the GUIProxy, Idb debugger, oraz IdbAdapter
    objects oraz linking them together.  Register the IdbAdapter przy the
    RPCServer to handle RPC requests z the split debugger GUI via the
    IdbProxy.

    """
    gui_proxy = GUIProxy(rpchandler, gui_adap_oid)
    idb = Debugger.Idb(gui_proxy)
    idb_adap = IdbAdapter(idb)
    rpchandler.register(idb_adap_oid, idb_adap)
    zwróć idb_adap_oid


#=======================================
#
# In the IDLE process:


klasa FrameProxy:

    def __init__(self, conn, fid):
        self._conn = conn
        self._fid = fid
        self._oid = "idb_adapter"
        self._dictcache = {}

    def __getattr__(self, name):
        jeżeli name[:1] == "_":
            podnieś AttributeError(name)
        jeżeli name == "f_code":
            zwróć self._get_f_code()
        jeżeli name == "f_globals":
            zwróć self._get_f_globals()
        jeżeli name == "f_locals":
            zwróć self._get_f_locals()
        zwróć self._conn.remotecall(self._oid, "frame_attr",
                                     (self._fid, name), {})

    def _get_f_code(self):
        cid = self._conn.remotecall(self._oid, "frame_code", (self._fid,), {})
        zwróć CodeProxy(self._conn, self._oid, cid)

    def _get_f_globals(self):
        did = self._conn.remotecall(self._oid, "frame_globals",
                                    (self._fid,), {})
        zwróć self._get_dict_proxy(did)

    def _get_f_locals(self):
        did = self._conn.remotecall(self._oid, "frame_locals",
                                    (self._fid,), {})
        zwróć self._get_dict_proxy(did)

    def _get_dict_proxy(self, did):
        jeżeli did w self._dictcache:
            zwróć self._dictcache[did]
        dp = DictProxy(self._conn, self._oid, did)
        self._dictcache[did] = dp
        zwróć dp


klasa CodeProxy:

    def __init__(self, conn, oid, cid):
        self._conn = conn
        self._oid = oid
        self._cid = cid

    def __getattr__(self, name):
        jeżeli name == "co_name":
            zwróć self._conn.remotecall(self._oid, "code_name",
                                         (self._cid,), {})
        jeżeli name == "co_filename":
            zwróć self._conn.remotecall(self._oid, "code_filename",
                                         (self._cid,), {})


klasa DictProxy:

    def __init__(self, conn, oid, did):
        self._conn = conn
        self._oid = oid
        self._did = did

##    def keys(self):
##        zwróć self._conn.remotecall(self._oid, "dict_keys", (self._did,), {})

    # 'temporary' until dict_keys jest a pickleable built-in type
    def keys(self):
        zwróć self._conn.remotecall(self._oid,
                                     "dict_keys_list", (self._did,), {})

    def __getitem__(self, key):
        zwróć self._conn.remotecall(self._oid, "dict_item",
                                     (self._did, key), {})

    def __getattr__(self, name):
        ##print("*** Failed DictProxy.__getattr__:", name)
        podnieś AttributeError(name)


klasa GUIAdapter:

    def __init__(self, conn, gui):
        self.conn = conn
        self.gui = gui

    def interaction(self, message, fid, modified_info):
        ##print("*** Interaction: (%s, %s, %s)" % (message, fid, modified_info))
        frame = FrameProxy(self.conn, fid)
        self.gui.interaction(message, frame, modified_info)


klasa IdbProxy:

    def __init__(self, conn, shell, oid):
        self.oid = oid
        self.conn = conn
        self.shell = shell

    def call(self, methodname, *args, **kwargs):
        ##print("*** IdbProxy.call %s %s %s" % (methodname, args, kwargs))
        value = self.conn.remotecall(self.oid, methodname, args, kwargs)
        ##print("*** IdbProxy.call %s returns %r" % (methodname, value))
        zwróć value

    def run(self, cmd, locals):
        # Ignores locals on purpose!
        seq = self.conn.asyncqueue(self.oid, "run", (cmd,), {})
        self.shell.interp.active_seq = seq

    def get_stack(self, frame, tbid):
        # dalejing frame oraz traceback IDs, nie the objects themselves
        stack, i = self.call("get_stack", frame._fid, tbid)
        stack = [(FrameProxy(self.conn, fid), k) dla fid, k w stack]
        zwróć stack, i

    def set_continue(self):
        self.call("set_continue")

    def set_step(self):
        self.call("set_step")

    def set_next(self, frame):
        self.call("set_next", frame._fid)

    def set_return(self, frame):
        self.call("set_return", frame._fid)

    def set_quit(self):
        self.call("set_quit")

    def set_break(self, filename, lineno):
        msg = self.call("set_break", filename, lineno)
        zwróć msg

    def clear_break(self, filename, lineno):
        msg = self.call("clear_break", filename, lineno)
        zwróć msg

    def clear_all_file_breaks(self, filename):
        msg = self.call("clear_all_file_breaks", filename)
        zwróć msg

def start_remote_debugger(rpcclt, pyshell):
    """Start the subprocess debugger, initialize the debugger GUI oraz RPC link

    Request the RPCServer start the Python subprocess debugger oraz link.  Set
    up the Idle side of the split debugger by instantiating the IdbProxy,
    debugger GUI, oraz debugger GUIAdapter objects oraz linking them together.

    Register the GUIAdapter przy the RPCClient to handle debugger GUI
    interaction requests coming z the subprocess debugger via the GUIProxy.

    The IdbAdapter will dalej execution oraz environment requests coming z the
    Idle debugger GUI to the subprocess debugger via the IdbProxy.

    """
    global idb_adap_oid

    idb_adap_oid = rpcclt.remotecall("exec", "start_the_debugger",\
                                   (gui_adap_oid,), {})
    idb_proxy = IdbProxy(rpcclt, pyshell, idb_adap_oid)
    gui = Debugger.Debugger(pyshell, idb_proxy)
    gui_adap = GUIAdapter(rpcclt, gui)
    rpcclt.register(gui_adap_oid, gui_adap)
    zwróć gui

def close_remote_debugger(rpcclt):
    """Shut down subprocess debugger oraz Idle side of debugger RPC link

    Request that the RPCServer shut down the subprocess debugger oraz link.
    Unregister the GUIAdapter, which will cause a GC on the Idle process
    debugger oraz RPC link objects.  (The second reference to the debugger GUI
    jest deleted w PyShell.close_remote_debugger().)

    """
    close_subprocess_debugger(rpcclt)
    rpcclt.unregister(gui_adap_oid)

def close_subprocess_debugger(rpcclt):
    rpcclt.remotecall("exec", "stop_the_debugger", (idb_adap_oid,), {})

def restart_subprocess_debugger(rpcclt):
    idb_adap_oid_ret = rpcclt.remotecall("exec", "start_the_debugger",\
                                         (gui_adap_oid,), {})
    assert idb_adap_oid_ret == idb_adap_oid, 'Idb restarted przy different oid'
