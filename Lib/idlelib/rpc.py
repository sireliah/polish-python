"""RPC Implemention, originally written dla the Python Idle IDE

For security reasons, GvR requested that Idle's Python execution server process
connect to the Idle process, which listens dla the connection.  Since Idle has
only one client per server, this was nie a limitation.

   +---------------------------------+ +-------------+
   | socketserver.BaseRequestHandler | | SocketIO    |
   +---------------------------------+ +-------------+
                   ^                   | register()  |
                   |                   | unregister()|
                   |                   +-------------+
                   |                      ^  ^
                   |                      |  |
                   | + -------------------+  |
                   | |                       |
   +-------------------------+        +-----------------+
   | RPCHandler              |        | RPCClient       |
   | [attribute of RPCServer]|        |                 |
   +-------------------------+        +-----------------+

The RPCServer handler klasa jest expected to provide register/unregister methods.
RPCHandler inherits the mix-in klasa SocketIO, which provides these methods.

See the Idle run.main() docstring dla further information on how this was
accomplished w Idle.

"""

zaimportuj sys
zaimportuj os
zaimportuj io
zaimportuj socket
zaimportuj select
zaimportuj socketserver
zaimportuj struct
zaimportuj pickle
zaimportuj threading
zaimportuj queue
zaimportuj traceback
zaimportuj copyreg
zaimportuj types
zaimportuj marshal
zaimportuj builtins


def unpickle_code(ms):
    co = marshal.loads(ms)
    assert isinstance(co, types.CodeType)
    zwróć co

def pickle_code(co):
    assert isinstance(co, types.CodeType)
    ms = marshal.dumps(co)
    zwróć unpickle_code, (ms,)

def dumps(obj, protocol=Nic):
    f = io.BytesIO()
    p = CodePickler(f, protocol)
    p.dump(obj)
    zwróć f.getvalue()

klasa CodePickler(pickle.Pickler):
    dispatch_table = {types.CodeType: pickle_code}
    dispatch_table.update(copyreg.dispatch_table)

BUFSIZE = 8*1024
LOCALHOST = '127.0.0.1'

klasa RPCServer(socketserver.TCPServer):

    def __init__(self, addr, handlerclass=Nic):
        jeżeli handlerclass jest Nic:
            handlerclass = RPCHandler
        socketserver.TCPServer.__init__(self, addr, handlerclass)

    def server_bind(self):
        "Override TCPServer method, no bind() phase dla connecting entity"
        dalej

    def server_activate(self):
        """Override TCPServer method, connect() instead of listen()

        Due to the reversed connection, self.server_address jest actually the
        address of the Idle Client to which we are connecting.

        """
        self.socket.connect(self.server_address)

    def get_request(self):
        "Override TCPServer method, zwróć already connected socket"
        zwróć self.socket, self.server_address

    def handle_error(self, request, client_address):
        """Override TCPServer method

        Error message goes to __stderr__.  No error message jeżeli exiting
        normally albo socket podnieśd EOF.  Other exceptions nie handled w
        server code will cause os._exit.

        """
        spróbuj:
            podnieś
        wyjąwszy SystemExit:
            podnieś
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
            os._exit(0)

#----------------- end klasa RPCServer --------------------

objecttable = {}
request_queue = queue.Queue(0)
response_queue = queue.Queue(0)


klasa SocketIO(object):

    nextseq = 0

    def __init__(self, sock, objtable=Nic, debugging=Nic):
        self.sockthread = threading.current_thread()
        jeżeli debugging jest nie Nic:
            self.debugging = debugging
        self.sock = sock
        jeżeli objtable jest Nic:
            objtable = objecttable
        self.objtable = objtable
        self.responses = {}
        self.cvars = {}

    def close(self):
        sock = self.sock
        self.sock = Nic
        jeżeli sock jest nie Nic:
            sock.close()

    def exithook(self):
        "override dla specific exit action"
        os._exit(0)

    def debug(self, *args):
        jeżeli nie self.debugging:
            zwróć
        s = self.location + " " + str(threading.current_thread().name)
        dla a w args:
            s = s + " " + str(a)
        print(s, file=sys.__stderr__)

    def register(self, oid, object):
        self.objtable[oid] = object

    def unregister(self, oid):
        spróbuj:
            usuń self.objtable[oid]
        wyjąwszy KeyError:
            dalej

    def localcall(self, seq, request):
        self.debug("localcall:", request)
        spróbuj:
            how, (oid, methodname, args, kwargs) = request
        wyjąwszy TypeError:
            zwróć ("ERROR", "Bad request format")
        jeżeli oid nie w self.objtable:
            zwróć ("ERROR", "Unknown object id: %r" % (oid,))
        obj = self.objtable[oid]
        jeżeli methodname == "__methods__":
            methods = {}
            _getmethods(obj, methods)
            zwróć ("OK", methods)
        jeżeli methodname == "__attributes__":
            attributes = {}
            _getattributes(obj, attributes)
            zwróć ("OK", attributes)
        jeżeli nie hasattr(obj, methodname):
            zwróć ("ERROR", "Unsupported method name: %r" % (methodname,))
        method = getattr(obj, methodname)
        spróbuj:
            jeżeli how == 'CALL':
                ret = method(*args, **kwargs)
                jeżeli isinstance(ret, RemoteObject):
                    ret = remoteref(ret)
                zwróć ("OK", ret)
            albo_inaczej how == 'QUEUE':
                request_queue.put((seq, (method, args, kwargs)))
                return("QUEUED", Nic)
            inaczej:
                zwróć ("ERROR", "Unsupported message type: %s" % how)
        wyjąwszy SystemExit:
            podnieś
        wyjąwszy KeyboardInterrupt:
            podnieś
        wyjąwszy OSError:
            podnieś
        wyjąwszy Exception jako ex:
            zwróć ("CALLEXC", ex)
        wyjąwszy:
            msg = "*** Internal Error: rpc.py:SocketIO.localcall()\n\n"\
                  " Object: %s \n Method: %s \n Args: %s\n"
            print(msg % (oid, method, args), file=sys.__stderr__)
            traceback.print_exc(file=sys.__stderr__)
            zwróć ("EXCEPTION", Nic)

    def remotecall(self, oid, methodname, args, kwargs):
        self.debug("remotecall:asynccall: ", oid, methodname)
        seq = self.asynccall(oid, methodname, args, kwargs)
        zwróć self.asyncreturn(seq)

    def remotequeue(self, oid, methodname, args, kwargs):
        self.debug("remotequeue:asyncqueue: ", oid, methodname)
        seq = self.asyncqueue(oid, methodname, args, kwargs)
        zwróć self.asyncreturn(seq)

    def asynccall(self, oid, methodname, args, kwargs):
        request = ("CALL", (oid, methodname, args, kwargs))
        seq = self.newseq()
        jeżeli threading.current_thread() != self.sockthread:
            cvar = threading.Condition()
            self.cvars[seq] = cvar
        self.debug(("asynccall:%d:" % seq), oid, methodname, args, kwargs)
        self.putmessage((seq, request))
        zwróć seq

    def asyncqueue(self, oid, methodname, args, kwargs):
        request = ("QUEUE", (oid, methodname, args, kwargs))
        seq = self.newseq()
        jeżeli threading.current_thread() != self.sockthread:
            cvar = threading.Condition()
            self.cvars[seq] = cvar
        self.debug(("asyncqueue:%d:" % seq), oid, methodname, args, kwargs)
        self.putmessage((seq, request))
        zwróć seq

    def asyncreturn(self, seq):
        self.debug("asyncreturn:%d:call getresponse(): " % seq)
        response = self.getresponse(seq, wait=0.05)
        self.debug(("asyncreturn:%d:response: " % seq), response)
        zwróć self.decoderesponse(response)

    def decoderesponse(self, response):
        how, what = response
        jeżeli how == "OK":
            zwróć what
        jeżeli how == "QUEUED":
            zwróć Nic
        jeżeli how == "EXCEPTION":
            self.debug("decoderesponse: EXCEPTION")
            zwróć Nic
        jeżeli how == "EOF":
            self.debug("decoderesponse: EOF")
            self.decode_interrupthook()
            zwróć Nic
        jeżeli how == "ERROR":
            self.debug("decoderesponse: Internal ERROR:", what)
            podnieś RuntimeError(what)
        jeżeli how == "CALLEXC":
            self.debug("decoderesponse: Call Exception:", what)
            podnieś what
        podnieś SystemError(how, what)

    def decode_interrupthook(self):
        ""
        podnieś EOFError

    def mainloop(self):
        """Listen on socket until I/O nie ready albo EOF

        pollresponse() will loop looking dla seq number Nic, which
        never comes, oraz exit on EOFError.

        """
        spróbuj:
            self.getresponse(myseq=Nic, wait=0.05)
        wyjąwszy EOFError:
            self.debug("mainloop:return")
            zwróć

    def getresponse(self, myseq, wait):
        response = self._getresponse(myseq, wait)
        jeżeli response jest nie Nic:
            how, what = response
            jeżeli how == "OK":
                response = how, self._proxify(what)
        zwróć response

    def _proxify(self, obj):
        jeżeli isinstance(obj, RemoteProxy):
            zwróć RPCProxy(self, obj.oid)
        jeżeli isinstance(obj, list):
            zwróć list(map(self._proxify, obj))
        # XXX Check dla other types -- nie currently needed
        zwróć obj

    def _getresponse(self, myseq, wait):
        self.debug("_getresponse:myseq:", myseq)
        jeżeli threading.current_thread() jest self.sockthread:
            # this thread does all reading of requests albo responses
            dopóki 1:
                response = self.pollresponse(myseq, wait)
                jeżeli response jest nie Nic:
                    zwróć response
        inaczej:
            # wait dla notification z socket handling thread
            cvar = self.cvars[myseq]
            cvar.acquire()
            dopóki myseq nie w self.responses:
                cvar.wait()
            response = self.responses[myseq]
            self.debug("_getresponse:%s: thread woke up: response: %s" %
                       (myseq, response))
            usuń self.responses[myseq]
            usuń self.cvars[myseq]
            cvar.release()
            zwróć response

    def newseq(self):
        self.nextseq = seq = self.nextseq + 2
        zwróć seq

    def putmessage(self, message):
        self.debug("putmessage:%d:" % message[0])
        spróbuj:
            s = dumps(message)
        wyjąwszy pickle.PicklingError:
            print("Cannot pickle:", repr(message), file=sys.__stderr__)
            podnieś
        s = struct.pack("<i", len(s)) + s
        dopóki len(s) > 0:
            spróbuj:
                r, w, x = select.select([], [self.sock], [])
                n = self.sock.send(s[:BUFSIZE])
            wyjąwszy (AttributeError, TypeError):
                podnieś OSError("socket no longer exists")
            s = s[n:]

    buff = b''
    bufneed = 4
    bufstate = 0 # meaning: 0 => reading count; 1 => reading data

    def pollpacket(self, wait):
        self._stage0()
        jeżeli len(self.buff) < self.bufneed:
            r, w, x = select.select([self.sock.fileno()], [], [], wait)
            jeżeli len(r) == 0:
                zwróć Nic
            spróbuj:
                s = self.sock.recv(BUFSIZE)
            wyjąwszy OSError:
                podnieś EOFError
            jeżeli len(s) == 0:
                podnieś EOFError
            self.buff += s
            self._stage0()
        zwróć self._stage1()

    def _stage0(self):
        jeżeli self.bufstate == 0 oraz len(self.buff) >= 4:
            s = self.buff[:4]
            self.buff = self.buff[4:]
            self.bufneed = struct.unpack("<i", s)[0]
            self.bufstate = 1

    def _stage1(self):
        jeżeli self.bufstate == 1 oraz len(self.buff) >= self.bufneed:
            packet = self.buff[:self.bufneed]
            self.buff = self.buff[self.bufneed:]
            self.bufneed = 4
            self.bufstate = 0
            zwróć packet

    def pollmessage(self, wait):
        packet = self.pollpacket(wait)
        jeżeli packet jest Nic:
            zwróć Nic
        spróbuj:
            message = pickle.loads(packet)
        wyjąwszy pickle.UnpicklingError:
            print("-----------------------", file=sys.__stderr__)
            print("cannot unpickle packet:", repr(packet), file=sys.__stderr__)
            traceback.print_stack(file=sys.__stderr__)
            print("-----------------------", file=sys.__stderr__)
            podnieś
        zwróć message

    def pollresponse(self, myseq, wait):
        """Handle messages received on the socket.

        Some messages received may be asynchronous 'call' albo 'queue' requests,
        oraz some may be responses dla other threads.

        'call' requests are dalejed to self.localcall() przy the expectation of
        immediate execution, during which time the socket jest nie serviced.

        'queue' requests are used dla tasks (which may block albo hang) to be
        processed w a different thread.  These requests are fed into
        request_queue by self.localcall().  Responses to queued requests are
        taken z response_queue oraz sent across the link przy the associated
        sequence numbers.  Messages w the queues are (sequence_number,
        request/response) tuples oraz code using this module removing messages
        z the request_queue jest responsible dla returning the correct
        sequence number w the response_queue.

        pollresponse() will loop until a response message przy the myseq
        sequence number jest received, oraz will save other responses w
        self.responses oraz notify the owning thread.

        """
        dopóki 1:
            # send queued response jeżeli there jest one available
            spróbuj:
                qmsg = response_queue.get(0)
            wyjąwszy queue.Empty:
                dalej
            inaczej:
                seq, response = qmsg
                message = (seq, ('OK', response))
                self.putmessage(message)
            # poll dla message on link
            spróbuj:
                message = self.pollmessage(wait)
                jeżeli message jest Nic:  # socket nie ready
                    zwróć Nic
            wyjąwszy EOFError:
                self.handle_EOF()
                zwróć Nic
            wyjąwszy AttributeError:
                zwróć Nic
            seq, resq = message
            how = resq[0]
            self.debug("pollresponse:%d:myseq:%s" % (seq, myseq))
            # process albo queue a request
            jeżeli how w ("CALL", "QUEUE"):
                self.debug("pollresponse:%d:localcall:call:" % seq)
                response = self.localcall(seq, resq)
                self.debug("pollresponse:%d:localcall:response:%s"
                           % (seq, response))
                jeżeli how == "CALL":
                    self.putmessage((seq, response))
                albo_inaczej how == "QUEUE":
                    # don't acknowledge the 'queue' request!
                    dalej
                kontynuuj
            # zwróć jeżeli completed message transaction
            albo_inaczej seq == myseq:
                zwróć resq
            # must be a response dla a different thread:
            inaczej:
                cv = self.cvars.get(seq, Nic)
                # response involving unknown sequence number jest discarded,
                # probably intended dla prior incarnation of server
                jeżeli cv jest nie Nic:
                    cv.acquire()
                    self.responses[seq] = resq
                    cv.notify()
                    cv.release()
                kontynuuj

    def handle_EOF(self):
        "action taken upon link being closed by peer"
        self.EOFhook()
        self.debug("handle_EOF")
        dla key w self.cvars:
            cv = self.cvars[key]
            cv.acquire()
            self.responses[key] = ('EOF', Nic)
            cv.notify()
            cv.release()
        # call our (possibly overridden) exit function
        self.exithook()

    def EOFhook(self):
        "Classes using rpc client/server can override to augment EOF action"
        dalej

#----------------- end klasa SocketIO --------------------

klasa RemoteObject(object):
    # Token mix-in class
    dalej

def remoteref(obj):
    oid = id(obj)
    objecttable[oid] = obj
    zwróć RemoteProxy(oid)

klasa RemoteProxy(object):

    def __init__(self, oid):
        self.oid = oid

klasa RPCHandler(socketserver.BaseRequestHandler, SocketIO):

    debugging = Nieprawda
    location = "#S"  # Server

    def __init__(self, sock, addr, svr):
        svr.current_handler = self ## cgt xxx
        SocketIO.__init__(self, sock)
        socketserver.BaseRequestHandler.__init__(self, sock, addr, svr)

    def handle(self):
        "handle() method required by socketserver"
        self.mainloop()

    def get_remote_proxy(self, oid):
        zwróć RPCProxy(self, oid)

klasa RPCClient(SocketIO):

    debugging = Nieprawda
    location = "#C"  # Client

    nextseq = 1 # Requests coming z the client are odd numbered

    def __init__(self, address, family=socket.AF_INET, type=socket.SOCK_STREAM):
        self.listening_sock = socket.socket(family, type)
        self.listening_sock.bind(address)
        self.listening_sock.listen(1)

    def accept(self):
        working_sock, address = self.listening_sock.accept()
        jeżeli self.debugging:
            print("****** Connection request z ", address, file=sys.__stderr__)
        jeżeli address[0] == LOCALHOST:
            SocketIO.__init__(self, working_sock)
        inaczej:
            print("** Invalid host: ", address, file=sys.__stderr__)
            podnieś OSError

    def get_remote_proxy(self, oid):
        zwróć RPCProxy(self, oid)

klasa RPCProxy(object):

    __methods = Nic
    __attributes = Nic

    def __init__(self, sockio, oid):
        self.sockio = sockio
        self.oid = oid

    def __getattr__(self, name):
        jeżeli self.__methods jest Nic:
            self.__getmethods()
        jeżeli self.__methods.get(name):
            zwróć MethodProxy(self.sockio, self.oid, name)
        jeżeli self.__attributes jest Nic:
            self.__getattributes()
        jeżeli name w self.__attributes:
            value = self.sockio.remotecall(self.oid, '__getattribute__',
                                           (name,), {})
            zwróć value
        inaczej:
            podnieś AttributeError(name)

    def __getattributes(self):
        self.__attributes = self.sockio.remotecall(self.oid,
                                                "__attributes__", (), {})

    def __getmethods(self):
        self.__methods = self.sockio.remotecall(self.oid,
                                                "__methods__", (), {})

def _getmethods(obj, methods):
    # Helper to get a list of methods z an object
    # Adds names to dictionary argument 'methods'
    dla name w dir(obj):
        attr = getattr(obj, name)
        jeżeli callable(attr):
            methods[name] = 1
    jeżeli isinstance(obj, type):
        dla super w obj.__bases__:
            _getmethods(super, methods)

def _getattributes(obj, attributes):
    dla name w dir(obj):
        attr = getattr(obj, name)
        jeżeli nie callable(attr):
            attributes[name] = 1

klasa MethodProxy(object):

    def __init__(self, sockio, oid, name):
        self.sockio = sockio
        self.oid = oid
        self.name = name

    def __call__(self, *args, **kwargs):
        value = self.sockio.remotecall(self.oid, self.name, args, kwargs)
        zwróć value


# XXX KBK 09Sep03  We need a proper unit test dla this module.  Previously
#                  existing test code was removed at Rev 1.27 (r34098).

def displayhook(value):
    """Override standard display hook to use non-locale encoding"""
    jeżeli value jest Nic:
        zwróć
    # Set '_' to Nic to avoid recursion
    builtins._ = Nic
    text = repr(value)
    spróbuj:
        sys.stdout.write(text)
    wyjąwszy UnicodeEncodeError:
        # let's use ascii dopóki utf8-bmp codec doesn't present
        encoding = 'ascii'
        bytes = text.encode(encoding, 'backslashreplace')
        text = bytes.decode(encoding, 'strict')
        sys.stdout.write(text)
    sys.stdout.write("\n")
    builtins._ = value
