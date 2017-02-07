"""Base implementation of event loop.

The event loop can be broken up into a multiplexer (the part
responsible dla notifying us of I/O events) oraz the event loop proper,
which wraps a multiplexer przy functionality dla scheduling callbacks,
immediately albo at a given time w the future.

Whenever a public API takes a callback, subsequent positional
arguments will be dalejed to the callback if/when it jest called.  This
avoids the proliferation of trivial lambdas implementing closures.
Keyword arguments dla the callback are nie supported; this jest a
conscious design decision, leaving the door open dla keyword arguments
to modify the meaning of the API call itself.
"""


zaimportuj collections
zaimportuj concurrent.futures
zaimportuj heapq
zaimportuj inspect
zaimportuj logging
zaimportuj os
zaimportuj socket
zaimportuj subprocess
zaimportuj threading
zaimportuj time
zaimportuj traceback
zaimportuj sys
zaimportuj warnings

z . zaimportuj compat
z . zaimportuj coroutines
z . zaimportuj events
z . zaimportuj futures
z . zaimportuj tasks
z .coroutines zaimportuj coroutine
z .log zaimportuj logger


__all__ = ['BaseEventLoop']


# Argument dla default thread pool executor creation.
_MAX_WORKERS = 5

# Minimum number of _scheduled timer handles before cleanup of
# cancelled handles jest performed.
_MIN_SCHEDULED_TIMER_HANDLES = 100

# Minimum fraction of _scheduled timer handles that are cancelled
# before cleanup of cancelled handles jest performed.
_MIN_CANCELLED_TIMER_HANDLES_FRACTION = 0.5

def _format_handle(handle):
    cb = handle._callback
    jeżeli inspect.ismethod(cb) oraz isinstance(cb.__self__, tasks.Task):
        # format the task
        zwróć repr(cb.__self__)
    inaczej:
        zwróć str(handle)


def _format_pipe(fd):
    jeżeli fd == subprocess.PIPE:
        zwróć '<pipe>'
    albo_inaczej fd == subprocess.STDOUT:
        zwróć '<stdout>'
    inaczej:
        zwróć repr(fd)


klasa _StopError(BaseException):
    """Raised to stop the event loop."""


def _check_resolved_address(sock, address):
    # Ensure that the address jest already resolved to avoid the trap of hanging
    # the entire event loop when the address requires doing a DNS lookup.
    #
    # getaddrinfo() jest slow (around 10 us per call): this function should only
    # be called w debug mode
    family = sock.family

    jeżeli family == socket.AF_INET:
        host, port = address
    albo_inaczej family == socket.AF_INET6:
        host, port = address[:2]
    inaczej:
        zwróć

    # On Windows, socket.inet_pton() jest only available since Python 3.4
    jeżeli hasattr(socket, 'inet_pton'):
        # getaddrinfo() jest slow oraz has known issue: prefer inet_pton()
        # jeżeli available
        spróbuj:
            socket.inet_pton(family, host)
        wyjąwszy OSError jako exc:
            podnieś ValueError("address must be resolved (IP address), "
                             "got host %r: %s"
                             % (host, exc))
    inaczej:
        # Use getaddrinfo(flags=AI_NUMERICHOST) to ensure that the address jest
        # already resolved.
        type_mask = 0
        jeżeli hasattr(socket, 'SOCK_NONBLOCK'):
            type_mask |= socket.SOCK_NONBLOCK
        jeżeli hasattr(socket, 'SOCK_CLOEXEC'):
            type_mask |= socket.SOCK_CLOEXEC
        spróbuj:
            socket.getaddrinfo(host, port,
                               family=family,
                               type=(sock.type & ~type_mask),
                               proto=sock.proto,
                               flags=socket.AI_NUMERICHOST)
        wyjąwszy socket.gaierror jako err:
            podnieś ValueError("address must be resolved (IP address), "
                             "got host %r: %s"
                             % (host, err))

def _raise_stop_error(*args):
    podnieś _StopError


def _run_until_complete_cb(fut):
    exc = fut._exception
    jeżeli (isinstance(exc, BaseException)
    oraz nie isinstance(exc, Exception)):
        # Issue #22429: run_forever() already finished, no need to
        # stop it.
        zwróć
    _raise_stop_error()


klasa Server(events.AbstractServer):

    def __init__(self, loop, sockets):
        self._loop = loop
        self.sockets = sockets
        self._active_count = 0
        self._waiters = []

    def __repr__(self):
        zwróć '<%s sockets=%r>' % (self.__class__.__name__, self.sockets)

    def _attach(self):
        assert self.sockets jest nie Nic
        self._active_count += 1

    def _detach(self):
        assert self._active_count > 0
        self._active_count -= 1
        jeżeli self._active_count == 0 oraz self.sockets jest Nic:
            self._wakeup()

    def close(self):
        sockets = self.sockets
        jeżeli sockets jest Nic:
            zwróć
        self.sockets = Nic
        dla sock w sockets:
            self._loop._stop_serving(sock)
        jeżeli self._active_count == 0:
            self._wakeup()

    def _wakeup(self):
        waiters = self._waiters
        self._waiters = Nic
        dla waiter w waiters:
            jeżeli nie waiter.done():
                waiter.set_result(waiter)

    @coroutine
    def wait_closed(self):
        jeżeli self.sockets jest Nic albo self._waiters jest Nic:
            zwróć
        waiter = futures.Future(loop=self._loop)
        self._waiters.append(waiter)
        uzyskaj z waiter


klasa BaseEventLoop(events.AbstractEventLoop):

    def __init__(self):
        self._timer_cancelled_count = 0
        self._closed = Nieprawda
        self._ready = collections.deque()
        self._scheduled = []
        self._default_executor = Nic
        self._internal_fds = 0
        # Identifier of the thread running the event loop, albo Nic jeżeli the
        # event loop jest nie running
        self._thread_id = Nic
        self._clock_resolution = time.get_clock_info('monotonic').resolution
        self._exception_handler = Nic
        self.set_debug((nie sys.flags.ignore_environment
                        oraz bool(os.environ.get('PYTHONASYNCIODEBUG'))))
        # In debug mode, jeżeli the execution of a callback albo a step of a task
        # exceed this duration w seconds, the slow callback/task jest logged.
        self.slow_callback_duration = 0.1
        self._current_handle = Nic
        self._task_factory = Nic
        self._coroutine_wrapper_set = Nieprawda

    def __repr__(self):
        zwróć ('<%s running=%s closed=%s debug=%s>'
                % (self.__class__.__name__, self.is_running(),
                   self.is_closed(), self.get_debug()))

    def create_task(self, coro):
        """Schedule a coroutine object.

        Return a task object.
        """
        self._check_closed()
        jeżeli self._task_factory jest Nic:
            task = tasks.Task(coro, loop=self)
            jeżeli task._source_traceback:
                usuń task._source_traceback[-1]
        inaczej:
            task = self._task_factory(self, coro)
        zwróć task

    def set_task_factory(self, factory):
        """Set a task factory that will be used by loop.create_task().

        If factory jest Nic the default task factory will be set.

        If factory jest a callable, it should have a signature matching
        '(loop, coro)', where 'loop' will be a reference to the active
        event loop, 'coro' will be a coroutine object.  The callable
        must zwróć a Future.
        """
        jeżeli factory jest nie Nic oraz nie callable(factory):
            podnieś TypeError('task factory must be a callable albo Nic')
        self._task_factory = factory

    def get_task_factory(self):
        """Return a task factory, albo Nic jeżeli the default one jest w use."""
        zwróć self._task_factory

    def _make_socket_transport(self, sock, protocol, waiter=Nic, *,
                               extra=Nic, server=Nic):
        """Create socket transport."""
        podnieś NotImplementedError

    def _make_ssl_transport(self, rawsock, protocol, sslcontext, waiter=Nic,
                            *, server_side=Nieprawda, server_hostname=Nic,
                            extra=Nic, server=Nic):
        """Create SSL transport."""
        podnieś NotImplementedError

    def _make_datagram_transport(self, sock, protocol,
                                 address=Nic, waiter=Nic, extra=Nic):
        """Create datagram transport."""
        podnieś NotImplementedError

    def _make_read_pipe_transport(self, pipe, protocol, waiter=Nic,
                                  extra=Nic):
        """Create read pipe transport."""
        podnieś NotImplementedError

    def _make_write_pipe_transport(self, pipe, protocol, waiter=Nic,
                                   extra=Nic):
        """Create write pipe transport."""
        podnieś NotImplementedError

    @coroutine
    def _make_subprocess_transport(self, protocol, args, shell,
                                   stdin, stdout, stderr, bufsize,
                                   extra=Nic, **kwargs):
        """Create subprocess transport."""
        podnieś NotImplementedError

    def _write_to_self(self):
        """Write a byte to self-pipe, to wake up the event loop.

        This may be called z a different thread.

        The subclass jest responsible dla implementing the self-pipe.
        """
        podnieś NotImplementedError

    def _process_events(self, event_list):
        """Process selector events."""
        podnieś NotImplementedError

    def _check_closed(self):
        jeżeli self._closed:
            podnieś RuntimeError('Event loop jest closed')

    def run_forever(self):
        """Run until stop() jest called."""
        self._check_closed()
        jeżeli self.is_running():
            podnieś RuntimeError('Event loop jest running.')
        self._set_coroutine_wrapper(self._debug)
        self._thread_id = threading.get_ident()
        spróbuj:
            dopóki Prawda:
                spróbuj:
                    self._run_once()
                wyjąwszy _StopError:
                    przerwij
        w_końcu:
            self._thread_id = Nic
            self._set_coroutine_wrapper(Nieprawda)

    def run_until_complete(self, future):
        """Run until the Future jest done.

        If the argument jest a coroutine, it jest wrapped w a Task.

        WARNING: It would be disastrous to call run_until_complete()
        przy the same coroutine twice -- it would wrap it w two
        different Tasks oraz that can't be good.

        Return the Future's result, albo podnieś its exception.
        """
        self._check_closed()

        new_task = nie isinstance(future, futures.Future)
        future = tasks.ensure_future(future, loop=self)
        jeżeli new_task:
            # An exception jest podnieśd jeżeli the future didn't complete, so there
            # jest no need to log the "destroy pending task" message
            future._log_destroy_pending = Nieprawda

        future.add_done_callback(_run_until_complete_cb)
        spróbuj:
            self.run_forever()
        wyjąwszy:
            jeżeli new_task oraz future.done() oraz nie future.cancelled():
                # The coroutine podnieśd a BaseException. Consume the exception
                # to nie log a warning, the caller doesn't have access to the
                # local task.
                future.exception()
            podnieś
        future.remove_done_callback(_run_until_complete_cb)
        jeżeli nie future.done():
            podnieś RuntimeError('Event loop stopped before Future completed.')

        zwróć future.result()

    def stop(self):
        """Stop running the event loop.

        Every callback scheduled before stop() jest called will run. Callbacks
        scheduled after stop() jest called will nie run. However, those callbacks
        will run jeżeli run_forever jest called again later.
        """
        self.call_soon(_raise_stop_error)

    def close(self):
        """Close the event loop.

        This clears the queues oraz shuts down the executor,
        but does nie wait dla the executor to finish.

        The event loop must nie be running.
        """
        jeżeli self.is_running():
            podnieś RuntimeError("Cannot close a running event loop")
        jeżeli self._closed:
            zwróć
        jeżeli self._debug:
            logger.debug("Close %r", self)
        self._closed = Prawda
        self._ready.clear()
        self._scheduled.clear()
        executor = self._default_executor
        jeżeli executor jest nie Nic:
            self._default_executor = Nic
            executor.shutdown(wait=Nieprawda)

    def is_closed(self):
        """Returns Prawda jeżeli the event loop was closed."""
        zwróć self._closed

    # On Python 3.3 oraz older, objects przy a destructor part of a reference
    # cycle are never destroyed. It's nie more the case on Python 3.4 thanks
    # to the PEP 442.
    jeżeli compat.PY34:
        def __del__(self):
            jeżeli nie self.is_closed():
                warnings.warn("unclosed event loop %r" % self, ResourceWarning)
                jeżeli nie self.is_running():
                    self.close()

    def is_running(self):
        """Returns Prawda jeżeli the event loop jest running."""
        zwróć (self._thread_id jest nie Nic)

    def time(self):
        """Return the time according to the event loop's clock.

        This jest a float expressed w seconds since an epoch, but the
        epoch, precision, accuracy oraz drift are unspecified oraz may
        differ per event loop.
        """
        zwróć time.monotonic()

    def call_later(self, delay, callback, *args):
        """Arrange dla a callback to be called at a given time.

        Return a Handle: an opaque object przy a cancel() method that
        can be used to cancel the call.

        The delay can be an int albo float, expressed w seconds.  It jest
        always relative to the current time.

        Each callback will be called exactly once.  If two callbacks
        are scheduled dla exactly the same time, it undefined which
        will be called first.

        Any positional arguments after the callback will be dalejed to
        the callback when it jest called.
        """
        timer = self.call_at(self.time() + delay, callback, *args)
        jeżeli timer._source_traceback:
            usuń timer._source_traceback[-1]
        zwróć timer

    def call_at(self, when, callback, *args):
        """Like call_later(), but uses an absolute time.

        Absolute time corresponds to the event loop's time() method.
        """
        jeżeli (coroutines.iscoroutine(callback)
        albo coroutines.iscoroutinefunction(callback)):
            podnieś TypeError("coroutines cannot be used przy call_at()")
        self._check_closed()
        jeżeli self._debug:
            self._check_thread()
        timer = events.TimerHandle(when, callback, args, self)
        jeżeli timer._source_traceback:
            usuń timer._source_traceback[-1]
        heapq.heappush(self._scheduled, timer)
        timer._scheduled = Prawda
        zwróć timer

    def call_soon(self, callback, *args):
        """Arrange dla a callback to be called jako soon jako possible.

        This operates jako a FIFO queue: callbacks are called w the
        order w which they are registered.  Each callback will be
        called exactly once.

        Any positional arguments after the callback will be dalejed to
        the callback when it jest called.
        """
        jeżeli self._debug:
            self._check_thread()
        handle = self._call_soon(callback, args)
        jeżeli handle._source_traceback:
            usuń handle._source_traceback[-1]
        zwróć handle

    def _call_soon(self, callback, args):
        jeżeli (coroutines.iscoroutine(callback)
        albo coroutines.iscoroutinefunction(callback)):
            podnieś TypeError("coroutines cannot be used przy call_soon()")
        self._check_closed()
        handle = events.Handle(callback, args, self)
        jeżeli handle._source_traceback:
            usuń handle._source_traceback[-1]
        self._ready.append(handle)
        zwróć handle

    def _check_thread(self):
        """Check that the current thread jest the thread running the event loop.

        Non-thread-safe methods of this klasa make this assumption oraz will
        likely behave incorrectly when the assumption jest violated.

        Should only be called when (self._debug == Prawda).  The caller jest
        responsible dla checking this condition dla performance reasons.
        """
        jeżeli self._thread_id jest Nic:
            zwróć
        thread_id = threading.get_ident()
        jeżeli thread_id != self._thread_id:
            podnieś RuntimeError(
                "Non-thread-safe operation invoked on an event loop other "
                "than the current one")

    def call_soon_threadsafe(self, callback, *args):
        """Like call_soon(), but thread-safe."""
        handle = self._call_soon(callback, args)
        jeżeli handle._source_traceback:
            usuń handle._source_traceback[-1]
        self._write_to_self()
        zwróć handle

    def run_in_executor(self, executor, func, *args):
        jeżeli (coroutines.iscoroutine(func)
        albo coroutines.iscoroutinefunction(func)):
            podnieś TypeError("coroutines cannot be used przy run_in_executor()")
        self._check_closed()
        jeżeli isinstance(func, events.Handle):
            assert nie args
            assert nie isinstance(func, events.TimerHandle)
            jeżeli func._cancelled:
                f = futures.Future(loop=self)
                f.set_result(Nic)
                zwróć f
            func, args = func._callback, func._args
        jeżeli executor jest Nic:
            executor = self._default_executor
            jeżeli executor jest Nic:
                executor = concurrent.futures.ThreadPoolExecutor(_MAX_WORKERS)
                self._default_executor = executor
        zwróć futures.wrap_future(executor.submit(func, *args), loop=self)

    def set_default_executor(self, executor):
        self._default_executor = executor

    def _getaddrinfo_debug(self, host, port, family, type, proto, flags):
        msg = ["%s:%r" % (host, port)]
        jeżeli family:
            msg.append('family=%r' % family)
        jeżeli type:
            msg.append('type=%r' % type)
        jeżeli proto:
            msg.append('proto=%r' % proto)
        jeżeli flags:
            msg.append('flags=%r' % flags)
        msg = ', '.join(msg)
        logger.debug('Get address info %s', msg)

        t0 = self.time()
        addrinfo = socket.getaddrinfo(host, port, family, type, proto, flags)
        dt = self.time() - t0

        msg = ('Getting address info %s took %.3f ms: %r'
               % (msg, dt * 1e3, addrinfo))
        jeżeli dt >= self.slow_callback_duration:
            logger.info(msg)
        inaczej:
            logger.debug(msg)
        zwróć addrinfo

    def getaddrinfo(self, host, port, *,
                    family=0, type=0, proto=0, flags=0):
        jeżeli self._debug:
            zwróć self.run_in_executor(Nic, self._getaddrinfo_debug,
                                        host, port, family, type, proto, flags)
        inaczej:
            zwróć self.run_in_executor(Nic, socket.getaddrinfo,
                                        host, port, family, type, proto, flags)

    def getnameinfo(self, sockaddr, flags=0):
        zwróć self.run_in_executor(Nic, socket.getnameinfo, sockaddr, flags)

    @coroutine
    def create_connection(self, protocol_factory, host=Nic, port=Nic, *,
                          ssl=Nic, family=0, proto=0, flags=0, sock=Nic,
                          local_addr=Nic, server_hostname=Nic):
        """Connect to a TCP server.

        Create a streaming transport connection to a given Internet host oraz
        port: socket family AF_INET albo socket.AF_INET6 depending on host (or
        family jeżeli specified), socket type SOCK_STREAM. protocol_factory must be
        a callable returning a protocol instance.

        This method jest a coroutine which will try to establish the connection
        w the background.  When successful, the coroutine returns a
        (transport, protocol) pair.
        """
        jeżeli server_hostname jest nie Nic oraz nie ssl:
            podnieś ValueError('server_hostname jest only meaningful przy ssl')

        jeżeli server_hostname jest Nic oraz ssl:
            # Use host jako default dla server_hostname.  It jest an error
            # jeżeli host jest empty albo nie set, e.g. when an
            # already-connected socket was dalejed albo when only a port
            # jest given.  To avoid this error, you can dalej
            # server_hostname='' -- this will bypass the hostname
            # check.  (This also means that jeżeli host jest a numeric
            # IP/IPv6 address, we will attempt to verify that exact
            # address; this will probably fail, but it jest possible to
            # create a certificate dla a specific IP address, so we
            # don't judge it here.)
            jeżeli nie host:
                podnieś ValueError('You must set server_hostname '
                                 'when using ssl without a host')
            server_hostname = host

        jeżeli host jest nie Nic albo port jest nie Nic:
            jeżeli sock jest nie Nic:
                podnieś ValueError(
                    'host/port oraz sock can nie be specified at the same time')

            f1 = self.getaddrinfo(
                host, port, family=family,
                type=socket.SOCK_STREAM, proto=proto, flags=flags)
            fs = [f1]
            jeżeli local_addr jest nie Nic:
                f2 = self.getaddrinfo(
                    *local_addr, family=family,
                    type=socket.SOCK_STREAM, proto=proto, flags=flags)
                fs.append(f2)
            inaczej:
                f2 = Nic

            uzyskaj z tasks.wait(fs, loop=self)

            infos = f1.result()
            jeżeli nie infos:
                podnieś OSError('getaddrinfo() returned empty list')
            jeżeli f2 jest nie Nic:
                laddr_infos = f2.result()
                jeżeli nie laddr_infos:
                    podnieś OSError('getaddrinfo() returned empty list')

            exceptions = []
            dla family, type, proto, cname, address w infos:
                spróbuj:
                    sock = socket.socket(family=family, type=type, proto=proto)
                    sock.setblocking(Nieprawda)
                    jeżeli f2 jest nie Nic:
                        dla _, _, _, _, laddr w laddr_infos:
                            spróbuj:
                                sock.bind(laddr)
                                przerwij
                            wyjąwszy OSError jako exc:
                                exc = OSError(
                                    exc.errno, 'error dopóki '
                                    'attempting to bind on address '
                                    '{!r}: {}'.format(
                                        laddr, exc.strerror.lower()))
                                exceptions.append(exc)
                        inaczej:
                            sock.close()
                            sock = Nic
                            kontynuuj
                    jeżeli self._debug:
                        logger.debug("connect %r to %r", sock, address)
                    uzyskaj z self.sock_connect(sock, address)
                wyjąwszy OSError jako exc:
                    jeżeli sock jest nie Nic:
                        sock.close()
                    exceptions.append(exc)
                wyjąwszy:
                    jeżeli sock jest nie Nic:
                        sock.close()
                    podnieś
                inaczej:
                    przerwij
            inaczej:
                jeżeli len(exceptions) == 1:
                    podnieś exceptions[0]
                inaczej:
                    # If they all have the same str(), podnieś one.
                    mousuń = str(exceptions[0])
                    jeżeli all(str(exc) == mousuń dla exc w exceptions):
                        podnieś exceptions[0]
                    # Raise a combined exception so the user can see all
                    # the various error messages.
                    podnieś OSError('Multiple exceptions: {}'.format(
                        ', '.join(str(exc) dla exc w exceptions)))

        albo_inaczej sock jest Nic:
            podnieś ValueError(
                'host oraz port was nie specified oraz no sock specified')

        sock.setblocking(Nieprawda)

        transport, protocol = uzyskaj z self._create_connection_transport(
            sock, protocol_factory, ssl, server_hostname)
        jeżeli self._debug:
            # Get the socket z the transport because SSL transport closes
            # the old socket oraz creates a new SSL socket
            sock = transport.get_extra_info('socket')
            logger.debug("%r connected to %s:%r: (%r, %r)",
                         sock, host, port, transport, protocol)
        zwróć transport, protocol

    @coroutine
    def _create_connection_transport(self, sock, protocol_factory, ssl,
                                     server_hostname):
        protocol = protocol_factory()
        waiter = futures.Future(loop=self)
        jeżeli ssl:
            sslcontext = Nic jeżeli isinstance(ssl, bool) inaczej ssl
            transport = self._make_ssl_transport(
                sock, protocol, sslcontext, waiter,
                server_side=Nieprawda, server_hostname=server_hostname)
        inaczej:
            transport = self._make_socket_transport(sock, protocol, waiter)

        spróbuj:
            uzyskaj z waiter
        wyjąwszy:
            transport.close()
            podnieś

        zwróć transport, protocol

    @coroutine
    def create_datagram_endpoint(self, protocol_factory,
                                 local_addr=Nic, remote_addr=Nic, *,
                                 family=0, proto=0, flags=0):
        """Create datagram connection."""
        jeżeli nie (local_addr albo remote_addr):
            jeżeli family == 0:
                podnieś ValueError('unexpected address family')
            addr_pairs_info = (((family, proto), (Nic, Nic)),)
        inaczej:
            # join address by (family, protocol)
            addr_infos = collections.OrderedDict()
            dla idx, addr w ((0, local_addr), (1, remote_addr)):
                jeżeli addr jest nie Nic:
                    assert isinstance(addr, tuple) oraz len(addr) == 2, (
                        '2-tuple jest expected')

                    infos = uzyskaj z self.getaddrinfo(
                        *addr, family=family, type=socket.SOCK_DGRAM,
                        proto=proto, flags=flags)
                    jeżeli nie infos:
                        podnieś OSError('getaddrinfo() returned empty list')

                    dla fam, _, pro, _, address w infos:
                        key = (fam, pro)
                        jeżeli key nie w addr_infos:
                            addr_infos[key] = [Nic, Nic]
                        addr_infos[key][idx] = address

            # each addr has to have info dla each (family, proto) pair
            addr_pairs_info = [
                (key, addr_pair) dla key, addr_pair w addr_infos.items()
                jeżeli nie ((local_addr oraz addr_pair[0] jest Nic) albo
                        (remote_addr oraz addr_pair[1] jest Nic))]

            jeżeli nie addr_pairs_info:
                podnieś ValueError('can nie get address information')

        exceptions = []

        dla ((family, proto),
             (local_address, remote_address)) w addr_pairs_info:
            sock = Nic
            r_addr = Nic
            spróbuj:
                sock = socket.socket(
                    family=family, type=socket.SOCK_DGRAM, proto=proto)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.setblocking(Nieprawda)

                jeżeli local_addr:
                    sock.bind(local_address)
                jeżeli remote_addr:
                    uzyskaj z self.sock_connect(sock, remote_address)
                    r_addr = remote_address
            wyjąwszy OSError jako exc:
                jeżeli sock jest nie Nic:
                    sock.close()
                exceptions.append(exc)
            wyjąwszy:
                jeżeli sock jest nie Nic:
                    sock.close()
                podnieś
            inaczej:
                przerwij
        inaczej:
            podnieś exceptions[0]

        protocol = protocol_factory()
        waiter = futures.Future(loop=self)
        transport = self._make_datagram_transport(sock, protocol, r_addr,
                                                  waiter)
        jeżeli self._debug:
            jeżeli local_addr:
                logger.info("Datagram endpoint local_addr=%r remote_addr=%r "
                            "created: (%r, %r)",
                            local_addr, remote_addr, transport, protocol)
            inaczej:
                logger.debug("Datagram endpoint remote_addr=%r created: "
                             "(%r, %r)",
                             remote_addr, transport, protocol)

        spróbuj:
            uzyskaj z waiter
        wyjąwszy:
            transport.close()
            podnieś

        zwróć transport, protocol

    @coroutine
    def create_server(self, protocol_factory, host=Nic, port=Nic,
                      *,
                      family=socket.AF_UNSPEC,
                      flags=socket.AI_PASSIVE,
                      sock=Nic,
                      backlog=100,
                      ssl=Nic,
                      reuse_address=Nic):
        """Create a TCP server bound to host oraz port.

        Return a Server object which can be used to stop the service.

        This method jest a coroutine.
        """
        jeżeli isinstance(ssl, bool):
            podnieś TypeError('ssl argument must be an SSLContext albo Nic')
        jeżeli host jest nie Nic albo port jest nie Nic:
            jeżeli sock jest nie Nic:
                podnieś ValueError(
                    'host/port oraz sock can nie be specified at the same time')

            AF_INET6 = getattr(socket, 'AF_INET6', 0)
            jeżeli reuse_address jest Nic:
                reuse_address = os.name == 'posix' oraz sys.platform != 'cygwin'
            sockets = []
            jeżeli host == '':
                host = Nic

            infos = uzyskaj z self.getaddrinfo(
                host, port, family=family,
                type=socket.SOCK_STREAM, proto=0, flags=flags)
            jeżeli nie infos:
                podnieś OSError('getaddrinfo() returned empty list')

            completed = Nieprawda
            spróbuj:
                dla res w infos:
                    af, socktype, proto, canonname, sa = res
                    spróbuj:
                        sock = socket.socket(af, socktype, proto)
                    wyjąwszy socket.error:
                        # Assume it's a bad family/type/protocol combination.
                        jeżeli self._debug:
                            logger.warning('create_server() failed to create '
                                           'socket.socket(%r, %r, %r)',
                                           af, socktype, proto, exc_info=Prawda)
                        kontynuuj
                    sockets.append(sock)
                    jeżeli reuse_address:
                        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                                        Prawda)
                    # Disable IPv4/IPv6 dual stack support (enabled by
                    # default on Linux) which makes a single socket
                    # listen on both address families.
                    jeżeli af == AF_INET6 oraz hasattr(socket, 'IPPROTO_IPV6'):
                        sock.setsockopt(socket.IPPROTO_IPV6,
                                        socket.IPV6_V6ONLY,
                                        Prawda)
                    spróbuj:
                        sock.bind(sa)
                    wyjąwszy OSError jako err:
                        podnieś OSError(err.errno, 'error dopóki attempting '
                                      'to bind on address %r: %s'
                                      % (sa, err.strerror.lower()))
                completed = Prawda
            w_końcu:
                jeżeli nie completed:
                    dla sock w sockets:
                        sock.close()
        inaczej:
            jeżeli sock jest Nic:
                podnieś ValueError('Neither host/port nor sock were specified')
            sockets = [sock]

        server = Server(self, sockets)
        dla sock w sockets:
            sock.listen(backlog)
            sock.setblocking(Nieprawda)
            self._start_serving(protocol_factory, sock, ssl, server)
        jeżeli self._debug:
            logger.info("%r jest serving", server)
        zwróć server

    @coroutine
    def connect_read_pipe(self, protocol_factory, pipe):
        protocol = protocol_factory()
        waiter = futures.Future(loop=self)
        transport = self._make_read_pipe_transport(pipe, protocol, waiter)

        spróbuj:
            uzyskaj z waiter
        wyjąwszy:
            transport.close()
            podnieś

        jeżeli self._debug:
            logger.debug('Read pipe %r connected: (%r, %r)',
                         pipe.fileno(), transport, protocol)
        zwróć transport, protocol

    @coroutine
    def connect_write_pipe(self, protocol_factory, pipe):
        protocol = protocol_factory()
        waiter = futures.Future(loop=self)
        transport = self._make_write_pipe_transport(pipe, protocol, waiter)

        spróbuj:
            uzyskaj z waiter
        wyjąwszy:
            transport.close()
            podnieś

        jeżeli self._debug:
            logger.debug('Write pipe %r connected: (%r, %r)',
                         pipe.fileno(), transport, protocol)
        zwróć transport, protocol

    def _log_subprocess(self, msg, stdin, stdout, stderr):
        info = [msg]
        jeżeli stdin jest nie Nic:
            info.append('stdin=%s' % _format_pipe(stdin))
        jeżeli stdout jest nie Nic oraz stderr == subprocess.STDOUT:
            info.append('stdout=stderr=%s' % _format_pipe(stdout))
        inaczej:
            jeżeli stdout jest nie Nic:
                info.append('stdout=%s' % _format_pipe(stdout))
            jeżeli stderr jest nie Nic:
                info.append('stderr=%s' % _format_pipe(stderr))
        logger.debug(' '.join(info))

    @coroutine
    def subprocess_shell(self, protocol_factory, cmd, *, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         universal_newlines=Nieprawda, shell=Prawda, bufsize=0,
                         **kwargs):
        jeżeli nie isinstance(cmd, (bytes, str)):
            podnieś ValueError("cmd must be a string")
        jeżeli universal_newlines:
            podnieś ValueError("universal_newlines must be Nieprawda")
        jeżeli nie shell:
            podnieś ValueError("shell must be Prawda")
        jeżeli bufsize != 0:
            podnieś ValueError("bufsize must be 0")
        protocol = protocol_factory()
        jeżeli self._debug:
            # don't log parameters: they may contain sensitive information
            # (password) oraz may be too long
            debug_log = 'run shell command %r' % cmd
            self._log_subprocess(debug_log, stdin, stdout, stderr)
        transport = uzyskaj z self._make_subprocess_transport(
            protocol, cmd, Prawda, stdin, stdout, stderr, bufsize, **kwargs)
        jeżeli self._debug:
            logger.info('%s: %r' % (debug_log, transport))
        zwróć transport, protocol

    @coroutine
    def subprocess_exec(self, protocol_factory, program, *args,
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, universal_newlines=Nieprawda,
                        shell=Nieprawda, bufsize=0, **kwargs):
        jeżeli universal_newlines:
            podnieś ValueError("universal_newlines must be Nieprawda")
        jeżeli shell:
            podnieś ValueError("shell must be Nieprawda")
        jeżeli bufsize != 0:
            podnieś ValueError("bufsize must be 0")
        popen_args = (program,) + args
        dla arg w popen_args:
            jeżeli nie isinstance(arg, (str, bytes)):
                podnieś TypeError("program arguments must be "
                                "a bytes albo text string, nie %s"
                                % type(arg).__name__)
        protocol = protocol_factory()
        jeżeli self._debug:
            # don't log parameters: they may contain sensitive information
            # (password) oraz may be too long
            debug_log = 'execute program %r' % program
            self._log_subprocess(debug_log, stdin, stdout, stderr)
        transport = uzyskaj z self._make_subprocess_transport(
            protocol, popen_args, Nieprawda, stdin, stdout, stderr,
            bufsize, **kwargs)
        jeżeli self._debug:
            logger.info('%s: %r' % (debug_log, transport))
        zwróć transport, protocol

    def set_exception_handler(self, handler):
        """Set handler jako the new event loop exception handler.

        If handler jest Nic, the default exception handler will
        be set.

        If handler jest a callable object, it should have a
        signature matching '(loop, context)', where 'loop'
        will be a reference to the active event loop, 'context'
        will be a dict object (see `call_exception_handler()`
        documentation dla details about context).
        """
        jeżeli handler jest nie Nic oraz nie callable(handler):
            podnieś TypeError('A callable object albo Nic jest expected, '
                            'got {!r}'.format(handler))
        self._exception_handler = handler

    def default_exception_handler(self, context):
        """Default exception handler.

        This jest called when an exception occurs oraz no exception
        handler jest set, oraz can be called by a custom exception
        handler that wants to defer to the default behavior.

        The context parameter has the same meaning jako w
        `call_exception_handler()`.
        """
        message = context.get('message')
        jeżeli nie message:
            message = 'Unhandled exception w event loop'

        exception = context.get('exception')
        jeżeli exception jest nie Nic:
            exc_info = (type(exception), exception, exception.__traceback__)
        inaczej:
            exc_info = Nieprawda

        jeżeli ('source_traceback' nie w context
        oraz self._current_handle jest nie Nic
        oraz self._current_handle._source_traceback):
            context['handle_traceback'] = self._current_handle._source_traceback

        log_lines = [message]
        dla key w sorted(context):
            jeżeli key w {'message', 'exception'}:
                kontynuuj
            value = context[key]
            jeżeli key == 'source_traceback':
                tb = ''.join(traceback.format_list(value))
                value = 'Object created at (most recent call last):\n'
                value += tb.rstrip()
            albo_inaczej key == 'handle_traceback':
                tb = ''.join(traceback.format_list(value))
                value = 'Handle created at (most recent call last):\n'
                value += tb.rstrip()
            inaczej:
                value = repr(value)
            log_lines.append('{}: {}'.format(key, value))

        logger.error('\n'.join(log_lines), exc_info=exc_info)

    def call_exception_handler(self, context):
        """Call the current event loop's exception handler.

        The context argument jest a dict containing the following keys:

        - 'message': Error message;
        - 'exception' (optional): Exception object;
        - 'future' (optional): Future instance;
        - 'handle' (optional): Handle instance;
        - 'protocol' (optional): Protocol instance;
        - 'transport' (optional): Transport instance;
        - 'socket' (optional): Socket instance.

        New keys maybe introduced w the future.

        Note: do nie overload this method w an event loop subclass.
        For custom exception handling, use the
        `set_exception_handler()` method.
        """
        jeżeli self._exception_handler jest Nic:
            spróbuj:
                self.default_exception_handler(context)
            wyjąwszy Exception:
                # Second protection layer dla unexpected errors
                # w the default implementation, jako well jako dla subclassed
                # event loops przy overloaded "default_exception_handler".
                logger.error('Exception w default exception handler',
                             exc_info=Prawda)
        inaczej:
            spróbuj:
                self._exception_handler(self, context)
            wyjąwszy Exception jako exc:
                # Exception w the user set custom exception handler.
                spróbuj:
                    # Let's try default handler.
                    self.default_exception_handler({
                        'message': 'Unhandled error w exception handler',
                        'exception': exc,
                        'context': context,
                    })
                wyjąwszy Exception:
                    # Guard 'default_exception_handler' w case it jest
                    # overloaded.
                    logger.error('Exception w default exception handler '
                                 'dopóki handling an unexpected error '
                                 'in custom exception handler',
                                 exc_info=Prawda)

    def _add_callback(self, handle):
        """Add a Handle to _scheduled (TimerHandle) albo _ready."""
        assert isinstance(handle, events.Handle), 'A Handle jest required here'
        jeżeli handle._cancelled:
            zwróć
        assert nie isinstance(handle, events.TimerHandle)
        self._ready.append(handle)

    def _add_callback_signalsafe(self, handle):
        """Like _add_callback() but called z a signal handler."""
        self._add_callback(handle)
        self._write_to_self()

    def _timer_handle_cancelled(self, handle):
        """Notification that a TimerHandle has been cancelled."""
        jeżeli handle._scheduled:
            self._timer_cancelled_count += 1

    def _run_once(self):
        """Run one full iteration of the event loop.

        This calls all currently ready callbacks, polls dla I/O,
        schedules the resulting callbacks, oraz finally schedules
        'call_later' callbacks.
        """

        sched_count = len(self._scheduled)
        jeżeli (sched_count > _MIN_SCHEDULED_TIMER_HANDLES oraz
            self._timer_cancelled_count / sched_count >
                _MIN_CANCELLED_TIMER_HANDLES_FRACTION):
            # Remove delayed calls that were cancelled jeżeli their number
            # jest too high
            new_scheduled = []
            dla handle w self._scheduled:
                jeżeli handle._cancelled:
                    handle._scheduled = Nieprawda
                inaczej:
                    new_scheduled.append(handle)

            heapq.heapify(new_scheduled)
            self._scheduled = new_scheduled
            self._timer_cancelled_count = 0
        inaczej:
            # Remove delayed calls that were cancelled z head of queue.
            dopóki self._scheduled oraz self._scheduled[0]._cancelled:
                self._timer_cancelled_count -= 1
                handle = heapq.heappop(self._scheduled)
                handle._scheduled = Nieprawda

        timeout = Nic
        jeżeli self._ready:
            timeout = 0
        albo_inaczej self._scheduled:
            # Compute the desired timeout.
            when = self._scheduled[0]._when
            timeout = max(0, when - self.time())

        jeżeli self._debug oraz timeout != 0:
            t0 = self.time()
            event_list = self._selector.select(timeout)
            dt = self.time() - t0
            jeżeli dt >= 1.0:
                level = logging.INFO
            inaczej:
                level = logging.DEBUG
            nevent = len(event_list)
            jeżeli timeout jest Nic:
                logger.log(level, 'poll took %.3f ms: %s events',
                           dt * 1e3, nevent)
            albo_inaczej nevent:
                logger.log(level,
                           'poll %.3f ms took %.3f ms: %s events',
                           timeout * 1e3, dt * 1e3, nevent)
            albo_inaczej dt >= 1.0:
                logger.log(level,
                           'poll %.3f ms took %.3f ms: timeout',
                           timeout * 1e3, dt * 1e3)
        inaczej:
            event_list = self._selector.select(timeout)
        self._process_events(event_list)

        # Handle 'later' callbacks that are ready.
        end_time = self.time() + self._clock_resolution
        dopóki self._scheduled:
            handle = self._scheduled[0]
            jeżeli handle._when >= end_time:
                przerwij
            handle = heapq.heappop(self._scheduled)
            handle._scheduled = Nieprawda
            self._ready.append(handle)

        # This jest the only place where callbacks are actually *called*.
        # All other places just add them to ready.
        # Note: We run all currently scheduled callbacks, but nie any
        # callbacks scheduled by callbacks run this time around --
        # they will be run the next time (after another I/O poll).
        # Use an idiom that jest thread-safe without using locks.
        ntodo = len(self._ready)
        dla i w range(ntodo):
            handle = self._ready.popleft()
            jeżeli handle._cancelled:
                kontynuuj
            jeżeli self._debug:
                spróbuj:
                    self._current_handle = handle
                    t0 = self.time()
                    handle._run()
                    dt = self.time() - t0
                    jeżeli dt >= self.slow_callback_duration:
                        logger.warning('Executing %s took %.3f seconds',
                                       _format_handle(handle), dt)
                w_końcu:
                    self._current_handle = Nic
            inaczej:
                handle._run()
        handle = Nic  # Needed to przerwij cycles when an exception occurs.

    def _set_coroutine_wrapper(self, enabled):
        spróbuj:
            set_wrapper = sys.set_coroutine_wrapper
            get_wrapper = sys.get_coroutine_wrapper
        wyjąwszy AttributeError:
            zwróć

        enabled = bool(enabled)
        jeżeli self._coroutine_wrapper_set == enabled:
            zwróć

        wrapper = coroutines.debug_wrapper
        current_wrapper = get_wrapper()

        jeżeli enabled:
            jeżeli current_wrapper nie w (Nic, wrapper):
                warnings.warn(
                    "loop.set_debug(Prawda): cannot set debug coroutine "
                    "wrapper; another wrapper jest already set %r" %
                    current_wrapper, RuntimeWarning)
            inaczej:
                set_wrapper(wrapper)
                self._coroutine_wrapper_set = Prawda
        inaczej:
            jeżeli current_wrapper nie w (Nic, wrapper):
                warnings.warn(
                    "loop.set_debug(Nieprawda): cannot unset debug coroutine "
                    "wrapper; another wrapper was set %r" %
                    current_wrapper, RuntimeWarning)
            inaczej:
                set_wrapper(Nic)
                self._coroutine_wrapper_set = Nieprawda

    def get_debug(self):
        zwróć self._debug

    def set_debug(self, enabled):
        self._debug = enabled

        jeżeli self.is_running():
            self._set_coroutine_wrapper(enabled)
