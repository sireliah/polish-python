#
# Module providing the `SyncManager` klasa dla dealing
# przy shared objects
#
# multiprocessing/managers.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

__all__ = [ 'BaseManager', 'SyncManager', 'BaseProxy', 'Token' ]

#
# Imports
#

zaimportuj sys
zaimportuj threading
zaimportuj array
zaimportuj queue

z time zaimportuj time jako _time
z traceback zaimportuj format_exc

z . zaimportuj connection
z . zaimportuj context
z . zaimportuj pool
z . zaimportuj process
z . zaimportuj reduction
z . zaimportuj util
z . zaimportuj get_context

#
# Register some things dla pickling
#

def reduce_array(a):
    zwróć array.array, (a.typecode, a.tobytes())
reduction.register(array.array, reduce_array)

view_types = [type(getattr({}, name)()) dla name w ('items','keys','values')]
jeżeli view_types[0] jest nie list:       # only needed w Py3.0
    def rebuild_as_list(obj):
        zwróć list, (list(obj),)
    dla view_type w view_types:
        reduction.register(view_type, rebuild_as_list)

#
# Type dla identifying shared objects
#

klasa Token(object):
    '''
    Type to uniquely indentify a shared object
    '''
    __slots__ = ('typeid', 'address', 'id')

    def __init__(self, typeid, address, id):
        (self.typeid, self.address, self.id) = (typeid, address, id)

    def __getstate__(self):
        zwróć (self.typeid, self.address, self.id)

    def __setstate__(self, state):
        (self.typeid, self.address, self.id) = state

    def __repr__(self):
        zwróć '%s(typeid=%r, address=%r, id=%r)' % \
               (self.__class__.__name__, self.typeid, self.address, self.id)

#
# Function dla communication przy a manager's server process
#

def dispatch(c, id, methodname, args=(), kwds={}):
    '''
    Send a message to manager using connection `c` oraz zwróć response
    '''
    c.send((id, methodname, args, kwds))
    kind, result = c.recv()
    jeżeli kind == '#RETURN':
        zwróć result
    podnieś convert_to_error(kind, result)

def convert_to_error(kind, result):
    jeżeli kind == '#ERROR':
        zwróć result
    albo_inaczej kind == '#TRACEBACK':
        assert type(result) jest str
        zwróć  RemoteError(result)
    albo_inaczej kind == '#UNSERIALIZABLE':
        assert type(result) jest str
        zwróć RemoteError('Unserializable message: %s\n' % result)
    inaczej:
        zwróć ValueError('Unrecognized message type')

klasa RemoteError(Exception):
    def __str__(self):
        zwróć ('\n' + '-'*75 + '\n' + str(self.args[0]) + '-'*75)

#
# Functions dla finding the method names of an object
#

def all_methods(obj):
    '''
    Return a list of names of methods of `obj`
    '''
    temp = []
    dla name w dir(obj):
        func = getattr(obj, name)
        jeżeli callable(func):
            temp.append(name)
    zwróć temp

def public_methods(obj):
    '''
    Return a list of names of methods of `obj` which do nie start przy '_'
    '''
    zwróć [name dla name w all_methods(obj) jeżeli name[0] != '_']

#
# Server which jest run w a process controlled by a manager
#

klasa Server(object):
    '''
    Server klasa which runs w a process controlled by a manager object
    '''
    public = ['shutdown', 'create', 'accept_connection', 'get_methods',
              'debug_info', 'number_of_objects', 'dummy', 'incref', 'decref']

    def __init__(self, registry, address, authkey, serializer):
        assert isinstance(authkey, bytes)
        self.registry = registry
        self.authkey = process.AuthenticationString(authkey)
        Listener, Client = listener_client[serializer]

        # do authentication later
        self.listener = Listener(address=address, backlog=16)
        self.address = self.listener.address

        self.id_to_obj = {'0': (Nic, ())}
        self.id_to_refcount = {}
        self.mutex = threading.RLock()

    def serve_forever(self):
        '''
        Run the server forever
        '''
        self.stop_event = threading.Event()
        process.current_process()._manager_server = self
        spróbuj:
            accepter = threading.Thread(target=self.accepter)
            accepter.daemon = Prawda
            accepter.start()
            spróbuj:
                dopóki nie self.stop_event.is_set():
                    self.stop_event.wait(1)
            wyjąwszy (KeyboardInterrupt, SystemExit):
                dalej
        w_końcu:
            jeżeli sys.stdout != sys.__stdout__:
                util.debug('resetting stdout, stderr')
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
            sys.exit(0)

    def accepter(self):
        dopóki Prawda:
            spróbuj:
                c = self.listener.accept()
            wyjąwszy OSError:
                kontynuuj
            t = threading.Thread(target=self.handle_request, args=(c,))
            t.daemon = Prawda
            t.start()

    def handle_request(self, c):
        '''
        Handle a new connection
        '''
        funcname = result = request = Nic
        spróbuj:
            connection.deliver_challenge(c, self.authkey)
            connection.answer_challenge(c, self.authkey)
            request = c.recv()
            ignore, funcname, args, kwds = request
            assert funcname w self.public, '%r unrecognized' % funcname
            func = getattr(self, funcname)
        wyjąwszy Exception:
            msg = ('#TRACEBACK', format_exc())
        inaczej:
            spróbuj:
                result = func(c, *args, **kwds)
            wyjąwszy Exception:
                msg = ('#TRACEBACK', format_exc())
            inaczej:
                msg = ('#RETURN', result)
        spróbuj:
            c.send(msg)
        wyjąwszy Exception jako e:
            spróbuj:
                c.send(('#TRACEBACK', format_exc()))
            wyjąwszy Exception:
                dalej
            util.info('Failure to send message: %r', msg)
            util.info(' ... request was %r', request)
            util.info(' ... exception was %r', e)

        c.close()

    def serve_client(self, conn):
        '''
        Handle requests z the proxies w a particular process/thread
        '''
        util.debug('starting server thread to service %r',
                   threading.current_thread().name)

        recv = conn.recv
        send = conn.send
        id_to_obj = self.id_to_obj

        dopóki nie self.stop_event.is_set():

            spróbuj:
                methodname = obj = Nic
                request = recv()
                ident, methodname, args, kwds = request
                obj, exposed, gettypeid = id_to_obj[ident]

                jeżeli methodname nie w exposed:
                    podnieś AttributeError(
                        'method %r of %r object jest nie w exposed=%r' %
                        (methodname, type(obj), exposed)
                        )

                function = getattr(obj, methodname)

                spróbuj:
                    res = function(*args, **kwds)
                wyjąwszy Exception jako e:
                    msg = ('#ERROR', e)
                inaczej:
                    typeid = gettypeid oraz gettypeid.get(methodname, Nic)
                    jeżeli typeid:
                        rident, rexposed = self.create(conn, typeid, res)
                        token = Token(typeid, self.address, rident)
                        msg = ('#PROXY', (rexposed, token))
                    inaczej:
                        msg = ('#RETURN', res)

            wyjąwszy AttributeError:
                jeżeli methodname jest Nic:
                    msg = ('#TRACEBACK', format_exc())
                inaczej:
                    spróbuj:
                        fallback_func = self.fallback_mapping[methodname]
                        result = fallback_func(
                            self, conn, ident, obj, *args, **kwds
                            )
                        msg = ('#RETURN', result)
                    wyjąwszy Exception:
                        msg = ('#TRACEBACK', format_exc())

            wyjąwszy EOFError:
                util.debug('got EOF -- exiting thread serving %r',
                           threading.current_thread().name)
                sys.exit(0)

            wyjąwszy Exception:
                msg = ('#TRACEBACK', format_exc())

            spróbuj:
                spróbuj:
                    send(msg)
                wyjąwszy Exception jako e:
                    send(('#UNSERIALIZABLE', repr(msg)))
            wyjąwszy Exception jako e:
                util.info('exception w thread serving %r',
                        threading.current_thread().name)
                util.info(' ... message was %r', msg)
                util.info(' ... exception was %r', e)
                conn.close()
                sys.exit(1)

    def fallback_getvalue(self, conn, ident, obj):
        zwróć obj

    def fallback_str(self, conn, ident, obj):
        zwróć str(obj)

    def fallback_repr(self, conn, ident, obj):
        zwróć repr(obj)

    fallback_mapping = {
        '__str__':fallback_str,
        '__repr__':fallback_repr,
        '#GETVALUE':fallback_getvalue
        }

    def dummy(self, c):
        dalej

    def debug_info(self, c):
        '''
        Return some info --- useful to spot problems przy refcounting
        '''
        przy self.mutex:
            result = []
            keys = list(self.id_to_obj.keys())
            keys.sort()
            dla ident w keys:
                jeżeli ident != '0':
                    result.append('  %s:       refcount=%s\n    %s' %
                                  (ident, self.id_to_refcount[ident],
                                   str(self.id_to_obj[ident][0])[:75]))
            zwróć '\n'.join(result)

    def number_of_objects(self, c):
        '''
        Number of shared objects
        '''
        zwróć len(self.id_to_obj) - 1      # don't count ident='0'

    def shutdown(self, c):
        '''
        Shutdown this process
        '''
        spróbuj:
            util.debug('manager received shutdown message')
            c.send(('#RETURN', Nic))
        wyjąwszy:
            zaimportuj traceback
            traceback.print_exc()
        w_końcu:
            self.stop_event.set()

    def create(self, c, typeid, *args, **kwds):
        '''
        Create a new shared object oraz zwróć its id
        '''
        przy self.mutex:
            callable, exposed, method_to_typeid, proxytype = \
                      self.registry[typeid]

            jeżeli callable jest Nic:
                assert len(args) == 1 oraz nie kwds
                obj = args[0]
            inaczej:
                obj = callable(*args, **kwds)

            jeżeli exposed jest Nic:
                exposed = public_methods(obj)
            jeżeli method_to_typeid jest nie Nic:
                assert type(method_to_typeid) jest dict
                exposed = list(exposed) + list(method_to_typeid)

            ident = '%x' % id(obj)  # convert to string because xmlrpclib
                                    # only has 32 bit signed integers
            util.debug('%r callable returned object przy id %r', typeid, ident)

            self.id_to_obj[ident] = (obj, set(exposed), method_to_typeid)
            jeżeli ident nie w self.id_to_refcount:
                self.id_to_refcount[ident] = 0
            # increment the reference count immediately, to avoid
            # this object being garbage collected before a Proxy
            # object dla it can be created.  The caller of create()
            # jest responsible dla doing a decref once the Proxy object
            # has been created.
            self.incref(c, ident)
            zwróć ident, tuple(exposed)

    def get_methods(self, c, token):
        '''
        Return the methods of the shared object indicated by token
        '''
        zwróć tuple(self.id_to_obj[token.id][1])

    def accept_connection(self, c, name):
        '''
        Spawn a new thread to serve this connection
        '''
        threading.current_thread().name = name
        c.send(('#RETURN', Nic))
        self.serve_client(c)

    def incref(self, c, ident):
        przy self.mutex:
            self.id_to_refcount[ident] += 1

    def decref(self, c, ident):
        przy self.mutex:
            assert self.id_to_refcount[ident] >= 1
            self.id_to_refcount[ident] -= 1
            jeżeli self.id_to_refcount[ident] == 0:
                usuń self.id_to_obj[ident], self.id_to_refcount[ident]
                util.debug('disposing of obj przy id %r', ident)

#
# Class to represent state of a manager
#

klasa State(object):
    __slots__ = ['value']
    INITIAL = 0
    STARTED = 1
    SHUTDOWN = 2

#
# Mapping z serializer name to Listener oraz Client types
#

listener_client = {
    'pickle' : (connection.Listener, connection.Client),
    'xmlrpclib' : (connection.XmlListener, connection.XmlClient)
    }

#
# Definition of BaseManager
#

klasa BaseManager(object):
    '''
    Base klasa dla managers
    '''
    _registry = {}
    _Server = Server

    def __init__(self, address=Nic, authkey=Nic, serializer='pickle',
                 ctx=Nic):
        jeżeli authkey jest Nic:
            authkey = process.current_process().authkey
        self._address = address     # XXX nie final address jeżeli eg ('', 0)
        self._authkey = process.AuthenticationString(authkey)
        self._state = State()
        self._state.value = State.INITIAL
        self._serializer = serializer
        self._Listener, self._Client = listener_client[serializer]
        self._ctx = ctx albo get_context()

    def get_server(self):
        '''
        Return server object przy serve_forever() method oraz address attribute
        '''
        assert self._state.value == State.INITIAL
        zwróć Server(self._registry, self._address,
                      self._authkey, self._serializer)

    def connect(self):
        '''
        Connect manager object to the server process
        '''
        Listener, Client = listener_client[self._serializer]
        conn = Client(self._address, authkey=self._authkey)
        dispatch(conn, Nic, 'dummy')
        self._state.value = State.STARTED

    def start(self, initializer=Nic, initargs=()):
        '''
        Spawn a server process dla this manager object
        '''
        assert self._state.value == State.INITIAL

        jeżeli initializer jest nie Nic oraz nie callable(initializer):
            podnieś TypeError('initializer must be a callable')

        # pipe over which we will retrieve address of server
        reader, writer = connection.Pipe(duplex=Nieprawda)

        # spawn process which runs a server
        self._process = self._ctx.Process(
            target=type(self)._run_server,
            args=(self._registry, self._address, self._authkey,
                  self._serializer, writer, initializer, initargs),
            )
        ident = ':'.join(str(i) dla i w self._process._identity)
        self._process.name = type(self).__name__  + '-' + ident
        self._process.start()

        # get address of server
        writer.close()
        self._address = reader.recv()
        reader.close()

        # register a finalizer
        self._state.value = State.STARTED
        self.shutdown = util.Finalize(
            self, type(self)._finalize_manager,
            args=(self._process, self._address, self._authkey,
                  self._state, self._Client),
            exitpriority=0
            )

    @classmethod
    def _run_server(cls, registry, address, authkey, serializer, writer,
                    initializer=Nic, initargs=()):
        '''
        Create a server, report its address oraz run it
        '''
        jeżeli initializer jest nie Nic:
            initializer(*initargs)

        # create server
        server = cls._Server(registry, address, authkey, serializer)

        # inform parent process of the server's address
        writer.send(server.address)
        writer.close()

        # run the manager
        util.info('manager serving at %r', server.address)
        server.serve_forever()

    def _create(self, typeid, *args, **kwds):
        '''
        Create a new shared object; zwróć the token oraz exposed tuple
        '''
        assert self._state.value == State.STARTED, 'server nie yet started'
        conn = self._Client(self._address, authkey=self._authkey)
        spróbuj:
            id, exposed = dispatch(conn, Nic, 'create', (typeid,)+args, kwds)
        w_końcu:
            conn.close()
        zwróć Token(typeid, self._address, id), exposed

    def join(self, timeout=Nic):
        '''
        Join the manager process (jeżeli it has been spawned)
        '''
        jeżeli self._process jest nie Nic:
            self._process.join(timeout)
            jeżeli nie self._process.is_alive():
                self._process = Nic

    def _debug_info(self):
        '''
        Return some info about the servers shared objects oraz connections
        '''
        conn = self._Client(self._address, authkey=self._authkey)
        spróbuj:
            zwróć dispatch(conn, Nic, 'debug_info')
        w_końcu:
            conn.close()

    def _number_of_objects(self):
        '''
        Return the number of shared objects
        '''
        conn = self._Client(self._address, authkey=self._authkey)
        spróbuj:
            zwróć dispatch(conn, Nic, 'number_of_objects')
        w_końcu:
            conn.close()

    def __enter__(self):
        jeżeli self._state.value == State.INITIAL:
            self.start()
        assert self._state.value == State.STARTED
        zwróć self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    @staticmethod
    def _finalize_manager(process, address, authkey, state, _Client):
        '''
        Shutdown the manager process; will be registered jako a finalizer
        '''
        jeżeli process.is_alive():
            util.info('sending shutdown message to manager')
            spróbuj:
                conn = _Client(address, authkey=authkey)
                spróbuj:
                    dispatch(conn, Nic, 'shutdown')
                w_końcu:
                    conn.close()
            wyjąwszy Exception:
                dalej

            process.join(timeout=1.0)
            jeżeli process.is_alive():
                util.info('manager still alive')
                jeżeli hasattr(process, 'terminate'):
                    util.info('trying to `terminate()` manager process')
                    process.terminate()
                    process.join(timeout=0.1)
                    jeżeli process.is_alive():
                        util.info('manager still alive after terminate')

        state.value = State.SHUTDOWN
        spróbuj:
            usuń BaseProxy._address_to_local[address]
        wyjąwszy KeyError:
            dalej

    address = property(lambda self: self._address)

    @classmethod
    def register(cls, typeid, callable=Nic, proxytype=Nic, exposed=Nic,
                 method_to_typeid=Nic, create_method=Prawda):
        '''
        Register a typeid przy the manager type
        '''
        jeżeli '_registry' nie w cls.__dict__:
            cls._registry = cls._registry.copy()

        jeżeli proxytype jest Nic:
            proxytype = AutoProxy

        exposed = exposed albo getattr(proxytype, '_exposed_', Nic)

        method_to_typeid = method_to_typeid albo \
                           getattr(proxytype, '_method_to_typeid_', Nic)

        jeżeli method_to_typeid:
            dla key, value w list(method_to_typeid.items()):
                assert type(key) jest str, '%r jest nie a string' % key
                assert type(value) jest str, '%r jest nie a string' % value

        cls._registry[typeid] = (
            callable, exposed, method_to_typeid, proxytype
            )

        jeżeli create_method:
            def temp(self, *args, **kwds):
                util.debug('requesting creation of a shared %r object', typeid)
                token, exp = self._create(typeid, *args, **kwds)
                proxy = proxytype(
                    token, self._serializer, manager=self,
                    authkey=self._authkey, exposed=exp
                    )
                conn = self._Client(token.address, authkey=self._authkey)
                dispatch(conn, Nic, 'decref', (token.id,))
                zwróć proxy
            temp.__name__ = typeid
            setattr(cls, typeid, temp)

#
# Subclass of set which get cleared after a fork
#

klasa ProcessLocalSet(set):
    def __init__(self):
        util.register_after_fork(self, lambda obj: obj.clear())
    def __reduce__(self):
        zwróć type(self), ()

#
# Definition of BaseProxy
#

klasa BaseProxy(object):
    '''
    A base dla proxies of shared objects
    '''
    _address_to_local = {}
    _mutex = util.ForkAwareThreadLock()

    def __init__(self, token, serializer, manager=Nic,
                 authkey=Nic, exposed=Nic, incref=Prawda):
        przy BaseProxy._mutex:
            tls_idset = BaseProxy._address_to_local.get(token.address, Nic)
            jeżeli tls_idset jest Nic:
                tls_idset = util.ForkAwareLocal(), ProcessLocalSet()
                BaseProxy._address_to_local[token.address] = tls_idset

        # self._tls jest used to record the connection used by this
        # thread to communicate przy the manager at token.address
        self._tls = tls_idset[0]

        # self._idset jest used to record the identities of all shared
        # objects dla which the current process owns references oraz
        # which are w the manager at token.address
        self._idset = tls_idset[1]

        self._token = token
        self._id = self._token.id
        self._manager = manager
        self._serializer = serializer
        self._Client = listener_client[serializer][1]

        jeżeli authkey jest nie Nic:
            self._authkey = process.AuthenticationString(authkey)
        albo_inaczej self._manager jest nie Nic:
            self._authkey = self._manager._authkey
        inaczej:
            self._authkey = process.current_process().authkey

        jeżeli incref:
            self._incref()

        util.register_after_fork(self, BaseProxy._after_fork)

    def _connect(self):
        util.debug('making connection to manager')
        name = process.current_process().name
        jeżeli threading.current_thread().name != 'MainThread':
            name += '|' + threading.current_thread().name
        conn = self._Client(self._token.address, authkey=self._authkey)
        dispatch(conn, Nic, 'accept_connection', (name,))
        self._tls.connection = conn

    def _callmethod(self, methodname, args=(), kwds={}):
        '''
        Try to call a method of the referrent oraz zwróć a copy of the result
        '''
        spróbuj:
            conn = self._tls.connection
        wyjąwszy AttributeError:
            util.debug('thread %r does nie own a connection',
                       threading.current_thread().name)
            self._connect()
            conn = self._tls.connection

        conn.send((self._id, methodname, args, kwds))
        kind, result = conn.recv()

        jeżeli kind == '#RETURN':
            zwróć result
        albo_inaczej kind == '#PROXY':
            exposed, token = result
            proxytype = self._manager._registry[token.typeid][-1]
            token.address = self._token.address
            proxy = proxytype(
                token, self._serializer, manager=self._manager,
                authkey=self._authkey, exposed=exposed
                )
            conn = self._Client(token.address, authkey=self._authkey)
            dispatch(conn, Nic, 'decref', (token.id,))
            zwróć proxy
        podnieś convert_to_error(kind, result)

    def _getvalue(self):
        '''
        Get a copy of the value of the referent
        '''
        zwróć self._callmethod('#GETVALUE')

    def _incref(self):
        conn = self._Client(self._token.address, authkey=self._authkey)
        dispatch(conn, Nic, 'incref', (self._id,))
        util.debug('INCREF %r', self._token.id)

        self._idset.add(self._id)

        state = self._manager oraz self._manager._state

        self._close = util.Finalize(
            self, BaseProxy._decref,
            args=(self._token, self._authkey, state,
                  self._tls, self._idset, self._Client),
            exitpriority=10
            )

    @staticmethod
    def _decref(token, authkey, state, tls, idset, _Client):
        idset.discard(token.id)

        # check whether manager jest still alive
        jeżeli state jest Nic albo state.value == State.STARTED:
            # tell manager this process no longer cares about referent
            spróbuj:
                util.debug('DECREF %r', token.id)
                conn = _Client(token.address, authkey=authkey)
                dispatch(conn, Nic, 'decref', (token.id,))
            wyjąwszy Exception jako e:
                util.debug('... decref failed %s', e)

        inaczej:
            util.debug('DECREF %r -- manager already shutdown', token.id)

        # check whether we can close this thread's connection because
        # the process owns no more references to objects dla this manager
        jeżeli nie idset oraz hasattr(tls, 'connection'):
            util.debug('thread %r has no more proxies so closing conn',
                       threading.current_thread().name)
            tls.connection.close()
            usuń tls.connection

    def _after_fork(self):
        self._manager = Nic
        spróbuj:
            self._incref()
        wyjąwszy Exception jako e:
            # the proxy may just be dla a manager which has shutdown
            util.info('incref failed: %s' % e)

    def __reduce__(self):
        kwds = {}
        jeżeli context.get_spawning_popen() jest nie Nic:
            kwds['authkey'] = self._authkey

        jeżeli getattr(self, '_isauto', Nieprawda):
            kwds['exposed'] = self._exposed_
            zwróć (RebuildProxy,
                    (AutoProxy, self._token, self._serializer, kwds))
        inaczej:
            zwróć (RebuildProxy,
                    (type(self), self._token, self._serializer, kwds))

    def __deepcopy__(self, memo):
        zwróć self._getvalue()

    def __repr__(self):
        zwróć '<%s object, typeid %r at %#x>' % \
               (type(self).__name__, self._token.typeid, id(self))

    def __str__(self):
        '''
        Return representation of the referent (or a fall-back jeżeli that fails)
        '''
        spróbuj:
            zwróć self._callmethod('__repr__')
        wyjąwszy Exception:
            zwróć repr(self)[:-1] + "; '__str__()' failed>"

#
# Function used dla unpickling
#

def RebuildProxy(func, token, serializer, kwds):
    '''
    Function used dla unpickling proxy objects.

    If possible the shared object jest returned, albo otherwise a proxy dla it.
    '''
    server = getattr(process.current_process(), '_manager_server', Nic)

    jeżeli server oraz server.address == token.address:
        zwróć server.id_to_obj[token.id][0]
    inaczej:
        incref = (
            kwds.pop('incref', Prawda) oraz
            nie getattr(process.current_process(), '_inheriting', Nieprawda)
            )
        zwróć func(token, serializer, incref=incref, **kwds)

#
# Functions to create proxies oraz proxy types
#

def MakeProxyType(name, exposed, _cache={}):
    '''
    Return an proxy type whose methods are given by `exposed`
    '''
    exposed = tuple(exposed)
    spróbuj:
        zwróć _cache[(name, exposed)]
    wyjąwszy KeyError:
        dalej

    dic = {}

    dla meth w exposed:
        exec('''def %s(self, *args, **kwds):
        zwróć self._callmethod(%r, args, kwds)''' % (meth, meth), dic)

    ProxyType = type(name, (BaseProxy,), dic)
    ProxyType._exposed_ = exposed
    _cache[(name, exposed)] = ProxyType
    zwróć ProxyType


def AutoProxy(token, serializer, manager=Nic, authkey=Nic,
              exposed=Nic, incref=Prawda):
    '''
    Return an auto-proxy dla `token`
    '''
    _Client = listener_client[serializer][1]

    jeżeli exposed jest Nic:
        conn = _Client(token.address, authkey=authkey)
        spróbuj:
            exposed = dispatch(conn, Nic, 'get_methods', (token,))
        w_końcu:
            conn.close()

    jeżeli authkey jest Nic oraz manager jest nie Nic:
        authkey = manager._authkey
    jeżeli authkey jest Nic:
        authkey = process.current_process().authkey

    ProxyType = MakeProxyType('AutoProxy[%s]' % token.typeid, exposed)
    proxy = ProxyType(token, serializer, manager=manager, authkey=authkey,
                      incref=incref)
    proxy._isauto = Prawda
    zwróć proxy

#
# Types/callables which we will register przy SyncManager
#

klasa Namespace(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)
    def __repr__(self):
        items = list(self.__dict__.items())
        temp = []
        dla name, value w items:
            jeżeli nie name.startswith('_'):
                temp.append('%s=%r' % (name, value))
        temp.sort()
        zwróć '%s(%s)' % (self.__class__.__name__, ', '.join(temp))

klasa Value(object):
    def __init__(self, typecode, value, lock=Prawda):
        self._typecode = typecode
        self._value = value
    def get(self):
        zwróć self._value
    def set(self, value):
        self._value = value
    def __repr__(self):
        zwróć '%s(%r, %r)'%(type(self).__name__, self._typecode, self._value)
    value = property(get, set)

def Array(typecode, sequence, lock=Prawda):
    zwróć array.array(typecode, sequence)

#
# Proxy types used by SyncManager
#

klasa IteratorProxy(BaseProxy):
    _exposed_ = ('__next__', 'send', 'throw', 'close')
    def __iter__(self):
        zwróć self
    def __next__(self, *args):
        zwróć self._callmethod('__next__', args)
    def send(self, *args):
        zwróć self._callmethod('send', args)
    def throw(self, *args):
        zwróć self._callmethod('throw', args)
    def close(self, *args):
        zwróć self._callmethod('close', args)


klasa AcquirerProxy(BaseProxy):
    _exposed_ = ('acquire', 'release')
    def acquire(self, blocking=Prawda, timeout=Nic):
        args = (blocking,) jeżeli timeout jest Nic inaczej (blocking, timeout)
        zwróć self._callmethod('acquire', args)
    def release(self):
        zwróć self._callmethod('release')
    def __enter__(self):
        zwróć self._callmethod('acquire')
    def __exit__(self, exc_type, exc_val, exc_tb):
        zwróć self._callmethod('release')


klasa ConditionProxy(AcquirerProxy):
    _exposed_ = ('acquire', 'release', 'wait', 'notify', 'notify_all')
    def wait(self, timeout=Nic):
        zwróć self._callmethod('wait', (timeout,))
    def notify(self):
        zwróć self._callmethod('notify')
    def notify_all(self):
        zwróć self._callmethod('notify_all')
    def wait_for(self, predicate, timeout=Nic):
        result = predicate()
        jeżeli result:
            zwróć result
        jeżeli timeout jest nie Nic:
            endtime = _time() + timeout
        inaczej:
            endtime = Nic
            waittime = Nic
        dopóki nie result:
            jeżeli endtime jest nie Nic:
                waittime = endtime - _time()
                jeżeli waittime <= 0:
                    przerwij
            self.wait(waittime)
            result = predicate()
        zwróć result


klasa EventProxy(BaseProxy):
    _exposed_ = ('is_set', 'set', 'clear', 'wait')
    def is_set(self):
        zwróć self._callmethod('is_set')
    def set(self):
        zwróć self._callmethod('set')
    def clear(self):
        zwróć self._callmethod('clear')
    def wait(self, timeout=Nic):
        zwróć self._callmethod('wait', (timeout,))


klasa BarrierProxy(BaseProxy):
    _exposed_ = ('__getattribute__', 'wait', 'abort', 'reset')
    def wait(self, timeout=Nic):
        zwróć self._callmethod('wait', (timeout,))
    def abort(self):
        zwróć self._callmethod('abort')
    def reset(self):
        zwróć self._callmethod('reset')
    @property
    def parties(self):
        zwróć self._callmethod('__getattribute__', ('parties',))
    @property
    def n_waiting(self):
        zwróć self._callmethod('__getattribute__', ('n_waiting',))
    @property
    def broken(self):
        zwróć self._callmethod('__getattribute__', ('broken',))


klasa NamespaceProxy(BaseProxy):
    _exposed_ = ('__getattribute__', '__setattr__', '__delattr__')
    def __getattr__(self, key):
        jeżeli key[0] == '_':
            zwróć object.__getattribute__(self, key)
        callmethod = object.__getattribute__(self, '_callmethod')
        zwróć callmethod('__getattribute__', (key,))
    def __setattr__(self, key, value):
        jeżeli key[0] == '_':
            zwróć object.__setattr__(self, key, value)
        callmethod = object.__getattribute__(self, '_callmethod')
        zwróć callmethod('__setattr__', (key, value))
    def __delattr__(self, key):
        jeżeli key[0] == '_':
            zwróć object.__delattr__(self, key)
        callmethod = object.__getattribute__(self, '_callmethod')
        zwróć callmethod('__delattr__', (key,))


klasa ValueProxy(BaseProxy):
    _exposed_ = ('get', 'set')
    def get(self):
        zwróć self._callmethod('get')
    def set(self, value):
        zwróć self._callmethod('set', (value,))
    value = property(get, set)


BaseListProxy = MakeProxyType('BaseListProxy', (
    '__add__', '__contains__', '__delitem__', '__getitem__', '__len__',
    '__mul__', '__reversed__', '__rmul__', '__setitem__',
    'append', 'count', 'extend', 'index', 'insert', 'pop', 'remove',
    'reverse', 'sort', '__imul__'
    ))
klasa ListProxy(BaseListProxy):
    def __iadd__(self, value):
        self._callmethod('extend', (value,))
        zwróć self
    def __imul__(self, value):
        self._callmethod('__imul__', (value,))
        zwróć self


DictProxy = MakeProxyType('DictProxy', (
    '__contains__', '__delitem__', '__getitem__', '__len__',
    '__setitem__', 'clear', 'copy', 'get', 'has_key', 'items',
    'keys', 'pop', 'popitem', 'setdefault', 'update', 'values'
    ))


ArrayProxy = MakeProxyType('ArrayProxy', (
    '__len__', '__getitem__', '__setitem__'
    ))


BasePoolProxy = MakeProxyType('PoolProxy', (
    'apply', 'apply_async', 'close', 'imap', 'imap_unordered', 'join',
    'map', 'map_async', 'starmap', 'starmap_async', 'terminate',
    ))
BasePoolProxy._method_to_typeid_ = {
    'apply_async': 'AsyncResult',
    'map_async': 'AsyncResult',
    'starmap_async': 'AsyncResult',
    'imap': 'Iterator',
    'imap_unordered': 'Iterator'
    }
klasa PoolProxy(BasePoolProxy):
    def __enter__(self):
        zwróć self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()

#
# Definition of SyncManager
#

klasa SyncManager(BaseManager):
    '''
    Subclass of `BaseManager` which supports a number of shared object types.

    The types registered are those intended dla the synchronization
    of threads, plus `dict`, `list` oraz `Namespace`.

    The `multiprocessing.Manager()` function creates started instances of
    this class.
    '''

SyncManager.register('Queue', queue.Queue)
SyncManager.register('JoinableQueue', queue.Queue)
SyncManager.register('Event', threading.Event, EventProxy)
SyncManager.register('Lock', threading.Lock, AcquirerProxy)
SyncManager.register('RLock', threading.RLock, AcquirerProxy)
SyncManager.register('Semaphore', threading.Semaphore, AcquirerProxy)
SyncManager.register('BoundedSemaphore', threading.BoundedSemaphore,
                     AcquirerProxy)
SyncManager.register('Condition', threading.Condition, ConditionProxy)
SyncManager.register('Barrier', threading.Barrier, BarrierProxy)
SyncManager.register('Pool', pool.Pool, PoolProxy)
SyncManager.register('list', list, ListProxy)
SyncManager.register('dict', dict, DictProxy)
SyncManager.register('Value', Value, ValueProxy)
SyncManager.register('Array', Array, ArrayProxy)
SyncManager.register('Namespace', Namespace, NamespaceProxy)

# types returned by methods of PoolProxy
SyncManager.register('Iterator', proxytype=IteratorProxy, create_method=Nieprawda)
SyncManager.register('AsyncResult', create_method=Nieprawda)
