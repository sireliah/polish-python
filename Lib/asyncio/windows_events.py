"""Selector oraz proactor event loops dla Windows."""

zaimportuj _winapi
zaimportuj errno
zaimportuj math
zaimportuj socket
zaimportuj struct
zaimportuj weakref

z . zaimportuj events
z . zaimportuj base_subprocess
z . zaimportuj futures
z . zaimportuj proactor_events
z . zaimportuj selector_events
z . zaimportuj tasks
z . zaimportuj windows_utils
z . zaimportuj _overlapped
z .coroutines zaimportuj coroutine
z .log zaimportuj logger


__all__ = ['SelectorEventLoop', 'ProactorEventLoop', 'IocpProactor',
           'DefaultEventLoopPolicy',
           ]


NULL = 0
INFINITE = 0xffffffff
ERROR_CONNECTION_REFUSED = 1225
ERROR_CONNECTION_ABORTED = 1236

# Initial delay w seconds dla connect_pipe() before retrying to connect
CONNECT_PIPE_INIT_DELAY = 0.001

# Maximum delay w seconds dla connect_pipe() before retrying to connect
CONNECT_PIPE_MAX_DELAY = 0.100


klasa _OverlappedFuture(futures.Future):
    """Subclass of Future which represents an overlapped operation.

    Cancelling it will immediately cancel the overlapped operation.
    """

    def __init__(self, ov, *, loop=Nic):
        super().__init__(loop=loop)
        jeżeli self._source_traceback:
            usuń self._source_traceback[-1]
        self._ov = ov

    def _repr_info(self):
        info = super()._repr_info()
        jeżeli self._ov jest nie Nic:
            state = 'pending' jeżeli self._ov.pending inaczej 'completed'
            info.insert(1, 'overlapped=<%s, %#x>' % (state, self._ov.address))
        zwróć info

    def _cancel_overlapped(self):
        jeżeli self._ov jest Nic:
            zwróć
        spróbuj:
            self._ov.cancel()
        wyjąwszy OSError jako exc:
            context = {
                'message': 'Cancelling an overlapped future failed',
                'exception': exc,
                'future': self,
            }
            jeżeli self._source_traceback:
                context['source_traceback'] = self._source_traceback
            self._loop.call_exception_handler(context)
        self._ov = Nic

    def cancel(self):
        self._cancel_overlapped()
        zwróć super().cancel()

    def set_exception(self, exception):
        super().set_exception(exception)
        self._cancel_overlapped()

    def set_result(self, result):
        super().set_result(result)
        self._ov = Nic


klasa _BaseWaitHandleFuture(futures.Future):
    """Subclass of Future which represents a wait handle."""

    def __init__(self, ov, handle, wait_handle, *, loop=Nic):
        super().__init__(loop=loop)
        jeżeli self._source_traceback:
            usuń self._source_traceback[-1]
        # Keep a reference to the Overlapped object to keep it alive until the
        # wait jest unregistered
        self._ov = ov
        self._handle = handle
        self._wait_handle = wait_handle

        # Should we call UnregisterWaitEx() jeżeli the wait completes
        # albo jest cancelled?
        self._registered = Prawda

    def _poll(self):
        # non-blocking wait: use a timeout of 0 millisecond
        zwróć (_winapi.WaitForSingleObject(self._handle, 0) ==
                _winapi.WAIT_OBJECT_0)

    def _repr_info(self):
        info = super()._repr_info()
        info.append('handle=%#x' % self._handle)
        jeżeli self._handle jest nie Nic:
            state = 'signaled' jeżeli self._poll() inaczej 'waiting'
            info.append(state)
        jeżeli self._wait_handle jest nie Nic:
            info.append('wait_handle=%#x' % self._wait_handle)
        zwróć info

    def _unregister_wait_cb(self, fut):
        # The wait was unregistered: it's nie safe to destroy the Overlapped
        # object
        self._ov = Nic

    def _unregister_wait(self):
        jeżeli nie self._registered:
            zwróć
        self._registered = Nieprawda

        wait_handle = self._wait_handle
        self._wait_handle = Nic
        spróbuj:
            _overlapped.UnregisterWait(wait_handle)
        wyjąwszy OSError jako exc:
            jeżeli exc.winerror != _overlapped.ERROR_IO_PENDING:
                context = {
                    'message': 'Failed to unregister the wait handle',
                    'exception': exc,
                    'future': self,
                }
                jeżeli self._source_traceback:
                    context['source_traceback'] = self._source_traceback
                self._loop.call_exception_handler(context)
                zwróć
            # ERROR_IO_PENDING means that the unregister jest pending

        self._unregister_wait_cb(Nic)

    def cancel(self):
        self._unregister_wait()
        zwróć super().cancel()

    def set_exception(self, exception):
        self._unregister_wait()
        super().set_exception(exception)

    def set_result(self, result):
        self._unregister_wait()
        super().set_result(result)


klasa _WaitCancelFuture(_BaseWaitHandleFuture):
    """Subclass of Future which represents a wait dla the cancellation of a
    _WaitHandleFuture using an event.
    """

    def __init__(self, ov, event, wait_handle, *, loop=Nic):
        super().__init__(ov, event, wait_handle, loop=loop)

        self._done_callback = Nic

    def cancel(self):
        podnieś RuntimeError("_WaitCancelFuture must nie be cancelled")

    def _schedule_callbacks(self):
        super(_WaitCancelFuture, self)._schedule_callbacks()
        jeżeli self._done_callback jest nie Nic:
            self._done_callback(self)


klasa _WaitHandleFuture(_BaseWaitHandleFuture):
    def __init__(self, ov, handle, wait_handle, proactor, *, loop=Nic):
        super().__init__(ov, handle, wait_handle, loop=loop)
        self._proactor = proactor
        self._unregister_proactor = Prawda
        self._event = _overlapped.CreateEvent(Nic, Prawda, Nieprawda, Nic)
        self._event_fut = Nic

    def _unregister_wait_cb(self, fut):
        jeżeli self._event jest nie Nic:
            _winapi.CloseHandle(self._event)
            self._event = Nic
            self._event_fut = Nic

        # If the wait was cancelled, the wait may never be signalled, so
        # it's required to unregister it. Otherwise, IocpProactor.close() will
        # wait forever dla an event which will never come.
        #
        # If the IocpProactor already received the event, it's safe to call
        # _unregister() because we kept a reference to the Overlapped object
        # which jest used jako an unique key.
        self._proactor._unregister(self._ov)
        self._proactor = Nic

        super()._unregister_wait_cb(fut)

    def _unregister_wait(self):
        jeżeli nie self._registered:
            zwróć
        self._registered = Nieprawda

        wait_handle = self._wait_handle
        self._wait_handle = Nic
        spróbuj:
            _overlapped.UnregisterWaitEx(wait_handle, self._event)
        wyjąwszy OSError jako exc:
            jeżeli exc.winerror != _overlapped.ERROR_IO_PENDING:
                context = {
                    'message': 'Failed to unregister the wait handle',
                    'exception': exc,
                    'future': self,
                }
                jeżeli self._source_traceback:
                    context['source_traceback'] = self._source_traceback
                self._loop.call_exception_handler(context)
                zwróć
            # ERROR_IO_PENDING jest nie an error, the wait was unregistered

        self._event_fut = self._proactor._wait_cancel(self._event,
                                                      self._unregister_wait_cb)


klasa PipeServer(object):
    """Class representing a pipe server.

    This jest much like a bound, listening socket.
    """
    def __init__(self, address):
        self._address = address
        self._free_instances = weakref.WeakSet()
        # initialize the pipe attribute before calling _server_pipe_handle()
        # because this function can podnieś an exception oraz the destructor calls
        # the close() method
        self._pipe = Nic
        self._accept_pipe_future = Nic
        self._pipe = self._server_pipe_handle(Prawda)

    def _get_unconnected_pipe(self):
        # Create new instance oraz zwróć previous one.  This ensures
        # that (until the server jest closed) there jest always at least
        # one pipe handle dla address.  Therefore jeżeli a client attempt
        # to connect it will nie fail przy FileNotFoundError.
        tmp, self._pipe = self._pipe, self._server_pipe_handle(Nieprawda)
        zwróć tmp

    def _server_pipe_handle(self, first):
        # Return a wrapper dla a new pipe handle.
        jeżeli self.closed():
            zwróć Nic
        flags = _winapi.PIPE_ACCESS_DUPLEX | _winapi.FILE_FLAG_OVERLAPPED
        jeżeli first:
            flags |= _winapi.FILE_FLAG_FIRST_PIPE_INSTANCE
        h = _winapi.CreateNamedPipe(
            self._address, flags,
            _winapi.PIPE_TYPE_MESSAGE | _winapi.PIPE_READMODE_MESSAGE |
            _winapi.PIPE_WAIT,
            _winapi.PIPE_UNLIMITED_INSTANCES,
            windows_utils.BUFSIZE, windows_utils.BUFSIZE,
            _winapi.NMPWAIT_WAIT_FOREVER, _winapi.NULL)
        pipe = windows_utils.PipeHandle(h)
        self._free_instances.add(pipe)
        zwróć pipe

    def closed(self):
        zwróć (self._address jest Nic)

    def close(self):
        jeżeli self._accept_pipe_future jest nie Nic:
            self._accept_pipe_future.cancel()
            self._accept_pipe_future = Nic
        # Close all instances which have nie been connected to by a client.
        jeżeli self._address jest nie Nic:
            dla pipe w self._free_instances:
                pipe.close()
            self._pipe = Nic
            self._address = Nic
            self._free_instances.clear()

    __del__ = close


klasa _WindowsSelectorEventLoop(selector_events.BaseSelectorEventLoop):
    """Windows version of selector event loop."""

    def _socketpair(self):
        zwróć windows_utils.socketpair()


klasa ProactorEventLoop(proactor_events.BaseProactorEventLoop):
    """Windows version of proactor event loop using IOCP."""

    def __init__(self, proactor=Nic):
        jeżeli proactor jest Nic:
            proactor = IocpProactor()
        super().__init__(proactor)

    def _socketpair(self):
        zwróć windows_utils.socketpair()

    @coroutine
    def create_pipe_connection(self, protocol_factory, address):
        f = self._proactor.connect_pipe(address)
        pipe = uzyskaj z f
        protocol = protocol_factory()
        trans = self._make_duplex_pipe_transport(pipe, protocol,
                                                 extra={'addr': address})
        zwróć trans, protocol

    @coroutine
    def start_serving_pipe(self, protocol_factory, address):
        server = PipeServer(address)

        def loop_accept_pipe(f=Nic):
            pipe = Nic
            spróbuj:
                jeżeli f:
                    pipe = f.result()
                    server._free_instances.discard(pipe)

                    jeżeli server.closed():
                        # A client connected before the server was closed:
                        # drop the client (close the pipe) oraz exit
                        pipe.close()
                        zwróć

                    protocol = protocol_factory()
                    self._make_duplex_pipe_transport(
                        pipe, protocol, extra={'addr': address})

                pipe = server._get_unconnected_pipe()
                jeżeli pipe jest Nic:
                    zwróć

                f = self._proactor.accept_pipe(pipe)
            wyjąwszy OSError jako exc:
                jeżeli pipe oraz pipe.fileno() != -1:
                    self.call_exception_handler({
                        'message': 'Pipe accept failed',
                        'exception': exc,
                        'pipe': pipe,
                    })
                    pipe.close()
                albo_inaczej self._debug:
                    logger.warning("Accept pipe failed on pipe %r",
                                   pipe, exc_info=Prawda)
            wyjąwszy futures.CancelledError:
                jeżeli pipe:
                    pipe.close()
            inaczej:
                server._accept_pipe_future = f
                f.add_done_callback(loop_accept_pipe)

        self.call_soon(loop_accept_pipe)
        zwróć [server]

    @coroutine
    def _make_subprocess_transport(self, protocol, args, shell,
                                   stdin, stdout, stderr, bufsize,
                                   extra=Nic, **kwargs):
        waiter = futures.Future(loop=self)
        transp = _WindowsSubprocessTransport(self, protocol, args, shell,
                                             stdin, stdout, stderr, bufsize,
                                             waiter=waiter, extra=extra,
                                             **kwargs)
        spróbuj:
            uzyskaj z waiter
        wyjąwszy Exception jako exc:
            # Workaround CPython bug #23353: using uzyskaj/uzyskaj-z w an
            # wyjąwszy block of a generator doesn't clear properly sys.exc_info()
            err = exc
        inaczej:
            err = Nic

        jeżeli err jest nie Nic:
            transp.close()
            uzyskaj z transp._wait()
            podnieś err

        zwróć transp


klasa IocpProactor:
    """Proactor implementation using IOCP."""

    def __init__(self, concurrency=0xffffffff):
        self._loop = Nic
        self._results = []
        self._iocp = _overlapped.CreateIoCompletionPort(
            _overlapped.INVALID_HANDLE_VALUE, NULL, 0, concurrency)
        self._cache = {}
        self._registered = weakref.WeakSet()
        self._unregistered = []
        self._stopped_serving = weakref.WeakSet()

    def __repr__(self):
        zwróć ('<%s overlapped#=%s result#=%s>'
                % (self.__class__.__name__, len(self._cache),
                   len(self._results)))

    def set_loop(self, loop):
        self._loop = loop

    def select(self, timeout=Nic):
        jeżeli nie self._results:
            self._poll(timeout)
        tmp = self._results
        self._results = []
        zwróć tmp

    def _result(self, value):
        fut = futures.Future(loop=self._loop)
        fut.set_result(value)
        zwróć fut

    def recv(self, conn, nbytes, flags=0):
        self._register_with_iocp(conn)
        ov = _overlapped.Overlapped(NULL)
        spróbuj:
            jeżeli isinstance(conn, socket.socket):
                ov.WSARecv(conn.fileno(), nbytes, flags)
            inaczej:
                ov.ReadFile(conn.fileno(), nbytes)
        wyjąwszy BrokenPipeError:
            zwróć self._result(b'')

        def finish_recv(trans, key, ov):
            spróbuj:
                zwróć ov.getresult()
            wyjąwszy OSError jako exc:
                jeżeli exc.winerror == _overlapped.ERROR_NETNAME_DELETED:
                    podnieś ConnectionResetError(*exc.args)
                inaczej:
                    podnieś

        zwróć self._register(ov, conn, finish_recv)

    def send(self, conn, buf, flags=0):
        self._register_with_iocp(conn)
        ov = _overlapped.Overlapped(NULL)
        jeżeli isinstance(conn, socket.socket):
            ov.WSASend(conn.fileno(), buf, flags)
        inaczej:
            ov.WriteFile(conn.fileno(), buf)

        def finish_send(trans, key, ov):
            spróbuj:
                zwróć ov.getresult()
            wyjąwszy OSError jako exc:
                jeżeli exc.winerror == _overlapped.ERROR_NETNAME_DELETED:
                    podnieś ConnectionResetError(*exc.args)
                inaczej:
                    podnieś

        zwróć self._register(ov, conn, finish_send)

    def accept(self, listener):
        self._register_with_iocp(listener)
        conn = self._get_accept_socket(listener.family)
        ov = _overlapped.Overlapped(NULL)
        ov.AcceptEx(listener.fileno(), conn.fileno())

        def finish_accept(trans, key, ov):
            ov.getresult()
            # Use SO_UPDATE_ACCEPT_CONTEXT so getsockname() etc work.
            buf = struct.pack('@P', listener.fileno())
            conn.setsockopt(socket.SOL_SOCKET,
                            _overlapped.SO_UPDATE_ACCEPT_CONTEXT, buf)
            conn.settimeout(listener.gettimeout())
            zwróć conn, conn.getpeername()

        @coroutine
        def accept_coro(future, conn):
            # Coroutine closing the accept socket jeżeli the future jest cancelled
            spróbuj:
                uzyskaj z future
            wyjąwszy futures.CancelledError:
                conn.close()
                podnieś

        future = self._register(ov, listener, finish_accept)
        coro = accept_coro(future, conn)
        tasks.ensure_future(coro, loop=self._loop)
        zwróć future

    def connect(self, conn, address):
        self._register_with_iocp(conn)
        # The socket needs to be locally bound before we call ConnectEx().
        spróbuj:
            _overlapped.BindLocal(conn.fileno(), conn.family)
        wyjąwszy OSError jako e:
            jeżeli e.winerror != errno.WSAEINVAL:
                podnieś
            # Probably already locally bound; check using getsockname().
            jeżeli conn.getsockname()[1] == 0:
                podnieś
        ov = _overlapped.Overlapped(NULL)
        ov.ConnectEx(conn.fileno(), address)

        def finish_connect(trans, key, ov):
            ov.getresult()
            # Use SO_UPDATE_CONNECT_CONTEXT so getsockname() etc work.
            conn.setsockopt(socket.SOL_SOCKET,
                            _overlapped.SO_UPDATE_CONNECT_CONTEXT, 0)
            zwróć conn

        zwróć self._register(ov, conn, finish_connect)

    def accept_pipe(self, pipe):
        self._register_with_iocp(pipe)
        ov = _overlapped.Overlapped(NULL)
        connected = ov.ConnectNamedPipe(pipe.fileno())

        jeżeli connected:
            # ConnectNamePipe() failed przy ERROR_PIPE_CONNECTED which means
            # that the pipe jest connected. There jest no need to wait dla the
            # completion of the connection.
            zwróć self._result(pipe)

        def finish_accept_pipe(trans, key, ov):
            ov.getresult()
            zwróć pipe

        zwróć self._register(ov, pipe, finish_accept_pipe)

    @coroutine
    def connect_pipe(self, address):
        delay = CONNECT_PIPE_INIT_DELAY
        dopóki Prawda:
            # Unfortunately there jest no way to do an overlapped connect to a pipe.
            # Call CreateFile() w a loop until it doesn't fail with
            # ERROR_PIPE_BUSY
            spróbuj:
                handle = _overlapped.ConnectPipe(address)
                przerwij
            wyjąwszy OSError jako exc:
                jeżeli exc.winerror != _overlapped.ERROR_PIPE_BUSY:
                    podnieś

            # ConnectPipe() failed przy ERROR_PIPE_BUSY: retry later
            delay = min(delay * 2, CONNECT_PIPE_MAX_DELAY)
            uzyskaj z tasks.sleep(delay, loop=self._loop)

        zwróć windows_utils.PipeHandle(handle)

    def wait_for_handle(self, handle, timeout=Nic):
        """Wait dla a handle.

        Return a Future object. The result of the future jest Prawda jeżeli the wait
        completed, albo Nieprawda jeżeli the wait did nie complete (on timeout).
        """
        zwróć self._wait_for_handle(handle, timeout, Nieprawda)

    def _wait_cancel(self, event, done_callback):
        fut = self._wait_for_handle(event, Nic, Prawda)
        # add_done_callback() cannot be used because the wait may only complete
        # w IocpProactor.close(), dopóki the event loop jest nie running.
        fut._done_callback = done_callback
        zwróć fut

    def _wait_for_handle(self, handle, timeout, _is_cancel):
        jeżeli timeout jest Nic:
            ms = _winapi.INFINITE
        inaczej:
            # RegisterWaitForSingleObject() has a resolution of 1 millisecond,
            # round away z zero to wait *at least* timeout seconds.
            ms = math.ceil(timeout * 1e3)

        # We only create ov so we can use ov.address jako a key dla the cache.
        ov = _overlapped.Overlapped(NULL)
        wait_handle = _overlapped.RegisterWaitWithQueue(
            handle, self._iocp, ov.address, ms)
        jeżeli _is_cancel:
            f = _WaitCancelFuture(ov, handle, wait_handle, loop=self._loop)
        inaczej:
            f = _WaitHandleFuture(ov, handle, wait_handle, self,
                                  loop=self._loop)
        jeżeli f._source_traceback:
            usuń f._source_traceback[-1]

        def finish_wait_for_handle(trans, key, ov):
            # Note that this second wait means that we should only use
            # this przy handles types where a successful wait has no
            # effect.  So events albo processes are all right, but locks
            # albo semaphores are not.  Also note jeżeli the handle jest
            # signalled oraz then quickly reset, then we may zwróć
            # Nieprawda even though we have nie timed out.
            zwróć f._poll()

        self._cache[ov.address] = (f, ov, 0, finish_wait_for_handle)
        zwróć f

    def _register_with_iocp(self, obj):
        # To get notifications of finished ops on this objects sent to the
        # completion port, were must register the handle.
        jeżeli obj nie w self._registered:
            self._registered.add(obj)
            _overlapped.CreateIoCompletionPort(obj.fileno(), self._iocp, 0, 0)
            # XXX We could also use SetFileCompletionNotificationModes()
            # to avoid sending notifications to completion port of ops
            # that succeed immediately.

    def _register(self, ov, obj, callback):
        # Return a future which will be set przy the result of the
        # operation when it completes.  The future's value jest actually
        # the value returned by callback().
        f = _OverlappedFuture(ov, loop=self._loop)
        jeżeli f._source_traceback:
            usuń f._source_traceback[-1]
        jeżeli nie ov.pending:
            # The operation has completed, so no need to postpone the
            # work.  We cannot take this short cut jeżeli we need the
            # NumberOfBytes, CompletionKey values returned by
            # PostQueuedCompletionStatus().
            spróbuj:
                value = callback(Nic, Nic, ov)
            wyjąwszy OSError jako e:
                f.set_exception(e)
            inaczej:
                f.set_result(value)
            # Even jeżeli GetOverlappedResult() was called, we have to wait dla the
            # notification of the completion w GetQueuedCompletionStatus().
            # Register the overlapped operation to keep a reference to the
            # OVERLAPPED object, otherwise the memory jest freed oraz Windows may
            # read uninitialized memory.

        # Register the overlapped operation dla later.  Note that
        # we only store obj to prevent it z being garbage
        # collected too early.
        self._cache[ov.address] = (f, ov, obj, callback)
        zwróć f

    def _unregister(self, ov):
        """Unregister an overlapped object.

        Call this method when its future has been cancelled. The event can
        already be signalled (pending w the proactor event queue). It jest also
        safe jeżeli the event jest never signalled (because it was cancelled).
        """
        self._unregistered.append(ov)

    def _get_accept_socket(self, family):
        s = socket.socket(family)
        s.settimeout(0)
        zwróć s

    def _poll(self, timeout=Nic):
        jeżeli timeout jest Nic:
            ms = INFINITE
        albo_inaczej timeout < 0:
            podnieś ValueError("negative timeout")
        inaczej:
            # GetQueuedCompletionStatus() has a resolution of 1 millisecond,
            # round away z zero to wait *at least* timeout seconds.
            ms = math.ceil(timeout * 1e3)
            jeżeli ms >= INFINITE:
                podnieś ValueError("timeout too big")

        dopóki Prawda:
            status = _overlapped.GetQueuedCompletionStatus(self._iocp, ms)
            jeżeli status jest Nic:
                przerwij
            ms = 0

            err, transferred, key, address = status
            spróbuj:
                f, ov, obj, callback = self._cache.pop(address)
            wyjąwszy KeyError:
                jeżeli self._loop.get_debug():
                    self._loop.call_exception_handler({
                        'message': ('GetQueuedCompletionStatus() returned an '
                                    'unexpected event'),
                        'status': ('err=%s transferred=%s key=%#x address=%#x'
                                   % (err, transferred, key, address)),
                    })

                # key jest either zero, albo it jest used to zwróć a pipe
                # handle which should be closed to avoid a leak.
                jeżeli key nie w (0, _overlapped.INVALID_HANDLE_VALUE):
                    _winapi.CloseHandle(key)
                kontynuuj

            jeżeli obj w self._stopped_serving:
                f.cancel()
            # Don't call the callback jeżeli _register() already read the result albo
            # jeżeli the overlapped has been cancelled
            albo_inaczej nie f.done():
                spróbuj:
                    value = callback(transferred, key, ov)
                wyjąwszy OSError jako e:
                    f.set_exception(e)
                    self._results.append(f)
                inaczej:
                    f.set_result(value)
                    self._results.append(f)

        # Remove unregisted futures
        dla ov w self._unregistered:
            self._cache.pop(ov.address, Nic)
        self._unregistered.clear()

    def _stop_serving(self, obj):
        # obj jest a socket albo pipe handle.  It will be closed w
        # BaseProactorEventLoop._stop_serving() which will make any
        # pending operations fail quickly.
        self._stopped_serving.add(obj)

    def close(self):
        # Cancel remaining registered operations.
        dla address, (fut, ov, obj, callback) w list(self._cache.items()):
            jeżeli fut.cancelled():
                # Nothing to do przy cancelled futures
                dalej
            albo_inaczej isinstance(fut, _WaitCancelFuture):
                # _WaitCancelFuture must nie be cancelled
                dalej
            inaczej:
                spróbuj:
                    fut.cancel()
                wyjąwszy OSError jako exc:
                    jeżeli self._loop jest nie Nic:
                        context = {
                            'message': 'Cancelling a future failed',
                            'exception': exc,
                            'future': fut,
                        }
                        jeżeli fut._source_traceback:
                            context['source_traceback'] = fut._source_traceback
                        self._loop.call_exception_handler(context)

        dopóki self._cache:
            jeżeli nie self._poll(1):
                logger.debug('taking long time to close proactor')

        self._results = []
        jeżeli self._iocp jest nie Nic:
            _winapi.CloseHandle(self._iocp)
            self._iocp = Nic

    def __del__(self):
        self.close()


klasa _WindowsSubprocessTransport(base_subprocess.BaseSubprocessTransport):

    def _start(self, args, shell, stdin, stdout, stderr, bufsize, **kwargs):
        self._proc = windows_utils.Popen(
            args, shell=shell, stdin=stdin, stdout=stdout, stderr=stderr,
            bufsize=bufsize, **kwargs)

        def callback(f):
            returncode = self._proc.poll()
            self._process_exited(returncode)

        f = self._loop._proactor.wait_for_handle(int(self._proc._handle))
        f.add_done_callback(callback)


SelectorEventLoop = _WindowsSelectorEventLoop


klasa _WindowsDefaultEventLoopPolicy(events.BaseDefaultEventLoopPolicy):
    _loop_factory = SelectorEventLoop


DefaultEventLoopPolicy = _WindowsDefaultEventLoopPolicy
