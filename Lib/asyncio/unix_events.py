"""Selector event loop dla Unix przy signal handling."""

zaimportuj errno
zaimportuj os
zaimportuj signal
zaimportuj socket
zaimportuj stat
zaimportuj subprocess
zaimportuj sys
zaimportuj threading
zaimportuj warnings


z . zaimportuj base_events
z . zaimportuj base_subprocess
z . zaimportuj compat
z . zaimportuj constants
z . zaimportuj coroutines
z . zaimportuj events
z . zaimportuj futures
z . zaimportuj selector_events
z . zaimportuj selectors
z . zaimportuj transports
z .coroutines zaimportuj coroutine
z .log zaimportuj logger


__all__ = ['SelectorEventLoop',
           'AbstractChildWatcher', 'SafeChildWatcher',
           'FastChildWatcher', 'DefaultEventLoopPolicy',
           ]

jeżeli sys.platform == 'win32':  # pragma: no cover
    podnieś ImportError('Signals are nie really supported on Windows')


def _sighandler_noop(signum, frame):
    """Dummy signal handler."""
    dalej


klasa _UnixSelectorEventLoop(selector_events.BaseSelectorEventLoop):
    """Unix event loop.

    Adds signal handling oraz UNIX Domain Socket support to SelectorEventLoop.
    """

    def __init__(self, selector=Nic):
        super().__init__(selector)
        self._signal_handlers = {}

    def _socketpair(self):
        zwróć socket.socketpair()

    def close(self):
        super().close()
        dla sig w list(self._signal_handlers):
            self.remove_signal_handler(sig)

    def _process_self_data(self, data):
        dla signum w data:
            jeżeli nie signum:
                # ignore null bytes written by _write_to_self()
                kontynuuj
            self._handle_signal(signum)

    def add_signal_handler(self, sig, callback, *args):
        """Add a handler dla a signal.  UNIX only.

        Raise ValueError jeżeli the signal number jest invalid albo uncatchable.
        Raise RuntimeError jeżeli there jest a problem setting up the handler.
        """
        jeżeli (coroutines.iscoroutine(callback)
        albo coroutines.iscoroutinefunction(callback)):
            podnieś TypeError("coroutines cannot be used "
                            "przy add_signal_handler()")
        self._check_signal(sig)
        self._check_closed()
        spróbuj:
            # set_wakeup_fd() podnieśs ValueError jeżeli this jest nie the
            # main thread.  By calling it early we ensure that an
            # event loop running w another thread cannot add a signal
            # handler.
            signal.set_wakeup_fd(self._csock.fileno())
        wyjąwszy (ValueError, OSError) jako exc:
            podnieś RuntimeError(str(exc))

        handle = events.Handle(callback, args, self)
        self._signal_handlers[sig] = handle

        spróbuj:
            # Register a dummy signal handler to ask Python to write the signal
            # number w the wakup file descriptor. _process_self_data() will
            # read signal numbers z this file descriptor to handle signals.
            signal.signal(sig, _sighandler_noop)

            # Set SA_RESTART to limit EINTR occurrences.
            signal.siginterrupt(sig, Nieprawda)
        wyjąwszy OSError jako exc:
            usuń self._signal_handlers[sig]
            jeżeli nie self._signal_handlers:
                spróbuj:
                    signal.set_wakeup_fd(-1)
                wyjąwszy (ValueError, OSError) jako nexc:
                    logger.info('set_wakeup_fd(-1) failed: %s', nexc)

            jeżeli exc.errno == errno.EINVAL:
                podnieś RuntimeError('sig {} cannot be caught'.format(sig))
            inaczej:
                podnieś

    def _handle_signal(self, sig):
        """Internal helper that jest the actual signal handler."""
        handle = self._signal_handlers.get(sig)
        jeżeli handle jest Nic:
            zwróć  # Assume it's some race condition.
        jeżeli handle._cancelled:
            self.remove_signal_handler(sig)  # Remove it properly.
        inaczej:
            self._add_callback_signalsafe(handle)

    def remove_signal_handler(self, sig):
        """Remove a handler dla a signal.  UNIX only.

        Return Prawda jeżeli a signal handler was removed, Nieprawda jeżeli not.
        """
        self._check_signal(sig)
        spróbuj:
            usuń self._signal_handlers[sig]
        wyjąwszy KeyError:
            zwróć Nieprawda

        jeżeli sig == signal.SIGINT:
            handler = signal.default_int_handler
        inaczej:
            handler = signal.SIG_DFL

        spróbuj:
            signal.signal(sig, handler)
        wyjąwszy OSError jako exc:
            jeżeli exc.errno == errno.EINVAL:
                podnieś RuntimeError('sig {} cannot be caught'.format(sig))
            inaczej:
                podnieś

        jeżeli nie self._signal_handlers:
            spróbuj:
                signal.set_wakeup_fd(-1)
            wyjąwszy (ValueError, OSError) jako exc:
                logger.info('set_wakeup_fd(-1) failed: %s', exc)

        zwróć Prawda

    def _check_signal(self, sig):
        """Internal helper to validate a signal.

        Raise ValueError jeżeli the signal number jest invalid albo uncatchable.
        Raise RuntimeError jeżeli there jest a problem setting up the handler.
        """
        jeżeli nie isinstance(sig, int):
            podnieś TypeError('sig must be an int, nie {!r}'.format(sig))

        jeżeli nie (1 <= sig < signal.NSIG):
            podnieś ValueError(
                'sig {} out of range(1, {})'.format(sig, signal.NSIG))

    def _make_read_pipe_transport(self, pipe, protocol, waiter=Nic,
                                  extra=Nic):
        zwróć _UnixReadPipeTransport(self, pipe, protocol, waiter, extra)

    def _make_write_pipe_transport(self, pipe, protocol, waiter=Nic,
                                   extra=Nic):
        zwróć _UnixWritePipeTransport(self, pipe, protocol, waiter, extra)

    @coroutine
    def _make_subprocess_transport(self, protocol, args, shell,
                                   stdin, stdout, stderr, bufsize,
                                   extra=Nic, **kwargs):
        przy events.get_child_watcher() jako watcher:
            waiter = futures.Future(loop=self)
            transp = _UnixSubprocessTransport(self, protocol, args, shell,
                                              stdin, stdout, stderr, bufsize,
                                              waiter=waiter, extra=extra,
                                              **kwargs)

            watcher.add_child_handler(transp.get_pid(),
                                      self._child_watcher_callback, transp)
            spróbuj:
                uzyskaj z waiter
            wyjąwszy Exception jako exc:
                # Workaround CPython bug #23353: using uzyskaj/uzyskaj-z w an
                # wyjąwszy block of a generator doesn't clear properly
                # sys.exc_info()
                err = exc
            inaczej:
                err = Nic

            jeżeli err jest nie Nic:
                transp.close()
                uzyskaj z transp._wait()
                podnieś err

        zwróć transp

    def _child_watcher_callback(self, pid, returncode, transp):
        self.call_soon_threadsafe(transp._process_exited, returncode)

    @coroutine
    def create_unix_connection(self, protocol_factory, path, *,
                               ssl=Nic, sock=Nic,
                               server_hostname=Nic):
        assert server_hostname jest Nic albo isinstance(server_hostname, str)
        jeżeli ssl:
            jeżeli server_hostname jest Nic:
                podnieś ValueError(
                    'you have to dalej server_hostname when using ssl')
        inaczej:
            jeżeli server_hostname jest nie Nic:
                podnieś ValueError('server_hostname jest only meaningful przy ssl')

        jeżeli path jest nie Nic:
            jeżeli sock jest nie Nic:
                podnieś ValueError(
                    'path oraz sock can nie be specified at the same time')

            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM, 0)
            spróbuj:
                sock.setblocking(Nieprawda)
                uzyskaj z self.sock_connect(sock, path)
            wyjąwszy:
                sock.close()
                podnieś

        inaczej:
            jeżeli sock jest Nic:
                podnieś ValueError('no path oraz sock were specified')
            sock.setblocking(Nieprawda)

        transport, protocol = uzyskaj z self._create_connection_transport(
            sock, protocol_factory, ssl, server_hostname)
        zwróć transport, protocol

    @coroutine
    def create_unix_server(self, protocol_factory, path=Nic, *,
                           sock=Nic, backlog=100, ssl=Nic):
        jeżeli isinstance(ssl, bool):
            podnieś TypeError('ssl argument must be an SSLContext albo Nic')

        jeżeli path jest nie Nic:
            jeżeli sock jest nie Nic:
                podnieś ValueError(
                    'path oraz sock can nie be specified at the same time')

            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

            spróbuj:
                sock.bind(path)
            wyjąwszy OSError jako exc:
                sock.close()
                jeżeli exc.errno == errno.EADDRINUSE:
                    # Let's improve the error message by adding
                    # przy what exact address it occurs.
                    msg = 'Address {!r} jest already w use'.format(path)
                    podnieś OSError(errno.EADDRINUSE, msg) z Nic
                inaczej:
                    podnieś
            wyjąwszy:
                sock.close()
                podnieś
        inaczej:
            jeżeli sock jest Nic:
                podnieś ValueError(
                    'path was nie specified, oraz no sock specified')

            jeżeli sock.family != socket.AF_UNIX:
                podnieś ValueError(
                    'A UNIX Domain Socket was expected, got {!r}'.format(sock))

        server = base_events.Server(self, [sock])
        sock.listen(backlog)
        sock.setblocking(Nieprawda)
        self._start_serving(protocol_factory, sock, ssl, server)
        zwróć server


jeżeli hasattr(os, 'set_blocking'):
    def _set_nonblocking(fd):
        os.set_blocking(fd, Nieprawda)
inaczej:
    zaimportuj fcntl

    def _set_nonblocking(fd):
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        flags = flags | os.O_NONBLOCK
        fcntl.fcntl(fd, fcntl.F_SETFL, flags)


klasa _UnixReadPipeTransport(transports.ReadTransport):

    max_size = 256 * 1024  # max bytes we read w one event loop iteration

    def __init__(self, loop, pipe, protocol, waiter=Nic, extra=Nic):
        super().__init__(extra)
        self._extra['pipe'] = pipe
        self._loop = loop
        self._pipe = pipe
        self._fileno = pipe.fileno()
        mode = os.fstat(self._fileno).st_mode
        jeżeli nie (stat.S_ISFIFO(mode) albo
                stat.S_ISSOCK(mode) albo
                stat.S_ISCHR(mode)):
            podnieś ValueError("Pipe transport jest dla pipes/sockets only.")
        _set_nonblocking(self._fileno)
        self._protocol = protocol
        self._closing = Nieprawda
        self._loop.call_soon(self._protocol.connection_made, self)
        # only start reading when connection_made() has been called
        self._loop.call_soon(self._loop.add_reader,
                             self._fileno, self._read_ready)
        jeżeli waiter jest nie Nic:
            # only wake up the waiter when connection_made() has been called
            self._loop.call_soon(waiter._set_result_unless_cancelled, Nic)

    def __repr__(self):
        info = [self.__class__.__name__]
        jeżeli self._pipe jest Nic:
            info.append('closed')
        albo_inaczej self._closing:
            info.append('closing')
        info.append('fd=%s' % self._fileno)
        jeżeli self._pipe jest nie Nic:
            polling = selector_events._test_selector_event(
                          self._loop._selector,
                          self._fileno, selectors.EVENT_READ)
            jeżeli polling:
                info.append('polling')
            inaczej:
                info.append('idle')
        inaczej:
            info.append('closed')
        zwróć '<%s>' % ' '.join(info)

    def _read_ready(self):
        spróbuj:
            data = os.read(self._fileno, self.max_size)
        wyjąwszy (BlockingIOError, InterruptedError):
            dalej
        wyjąwszy OSError jako exc:
            self._fatal_error(exc, 'Fatal read error on pipe transport')
        inaczej:
            jeżeli data:
                self._protocol.data_received(data)
            inaczej:
                jeżeli self._loop.get_debug():
                    logger.info("%r was closed by peer", self)
                self._closing = Prawda
                self._loop.remove_reader(self._fileno)
                self._loop.call_soon(self._protocol.eof_received)
                self._loop.call_soon(self._call_connection_lost, Nic)

    def pause_reading(self):
        self._loop.remove_reader(self._fileno)

    def resume_reading(self):
        self._loop.add_reader(self._fileno, self._read_ready)

    def close(self):
        jeżeli nie self._closing:
            self._close(Nic)

    # On Python 3.3 oraz older, objects przy a destructor part of a reference
    # cycle are never destroyed. It's nie more the case on Python 3.4 thanks
    # to the PEP 442.
    jeżeli compat.PY34:
        def __del__(self):
            jeżeli self._pipe jest nie Nic:
                warnings.warn("unclosed transport %r" % self, ResourceWarning)
                self._pipe.close()

    def _fatal_error(self, exc, message='Fatal error on pipe transport'):
        # should be called by exception handler only
        jeżeli (isinstance(exc, OSError) oraz exc.errno == errno.EIO):
            jeżeli self._loop.get_debug():
                logger.debug("%r: %s", self, message, exc_info=Prawda)
        inaczej:
            self._loop.call_exception_handler({
                'message': message,
                'exception': exc,
                'transport': self,
                'protocol': self._protocol,
            })
        self._close(exc)

    def _close(self, exc):
        self._closing = Prawda
        self._loop.remove_reader(self._fileno)
        self._loop.call_soon(self._call_connection_lost, exc)

    def _call_connection_lost(self, exc):
        spróbuj:
            self._protocol.connection_lost(exc)
        w_końcu:
            self._pipe.close()
            self._pipe = Nic
            self._protocol = Nic
            self._loop = Nic


klasa _UnixWritePipeTransport(transports._FlowControlMixin,
                              transports.WriteTransport):

    def __init__(self, loop, pipe, protocol, waiter=Nic, extra=Nic):
        super().__init__(extra, loop)
        self._extra['pipe'] = pipe
        self._pipe = pipe
        self._fileno = pipe.fileno()
        mode = os.fstat(self._fileno).st_mode
        is_socket = stat.S_ISSOCK(mode)
        jeżeli nie (is_socket albo
                stat.S_ISFIFO(mode) albo
                stat.S_ISCHR(mode)):
            podnieś ValueError("Pipe transport jest only dla "
                             "pipes, sockets oraz character devices")
        _set_nonblocking(self._fileno)
        self._protocol = protocol
        self._buffer = []
        self._conn_lost = 0
        self._closing = Nieprawda  # Set when close() albo write_eof() called.

        self._loop.call_soon(self._protocol.connection_made, self)

        # On AIX, the reader trick (to be notified when the read end of the
        # socket jest closed) only works dla sockets. On other platforms it
        # works dla pipes oraz sockets. (Exception: OS X 10.4?  Issue #19294.)
        jeżeli is_socket albo nie sys.platform.startswith("aix"):
            # only start reading when connection_made() has been called
            self._loop.call_soon(self._loop.add_reader,
                                 self._fileno, self._read_ready)

        jeżeli waiter jest nie Nic:
            # only wake up the waiter when connection_made() has been called
            self._loop.call_soon(waiter._set_result_unless_cancelled, Nic)

    def __repr__(self):
        info = [self.__class__.__name__]
        jeżeli self._pipe jest Nic:
            info.append('closed')
        albo_inaczej self._closing:
            info.append('closing')
        info.append('fd=%s' % self._fileno)
        jeżeli self._pipe jest nie Nic:
            polling = selector_events._test_selector_event(
                          self._loop._selector,
                          self._fileno, selectors.EVENT_WRITE)
            jeżeli polling:
                info.append('polling')
            inaczej:
                info.append('idle')

            bufsize = self.get_write_buffer_size()
            info.append('bufsize=%s' % bufsize)
        inaczej:
            info.append('closed')
        zwróć '<%s>' % ' '.join(info)

    def get_write_buffer_size(self):
        zwróć sum(len(data) dla data w self._buffer)

    def _read_ready(self):
        # Pipe was closed by peer.
        jeżeli self._loop.get_debug():
            logger.info("%r was closed by peer", self)
        jeżeli self._buffer:
            self._close(BrokenPipeError())
        inaczej:
            self._close()

    def write(self, data):
        assert isinstance(data, (bytes, bytearray, memoryview)), repr(data)
        jeżeli isinstance(data, bytearray):
            data = memoryview(data)
        jeżeli nie data:
            zwróć

        jeżeli self._conn_lost albo self._closing:
            jeżeli self._conn_lost >= constants.LOG_THRESHOLD_FOR_CONNLOST_WRITES:
                logger.warning('pipe closed by peer albo '
                               'os.write(pipe, data) podnieśd exception.')
            self._conn_lost += 1
            zwróć

        jeżeli nie self._buffer:
            # Attempt to send it right away first.
            spróbuj:
                n = os.write(self._fileno, data)
            wyjąwszy (BlockingIOError, InterruptedError):
                n = 0
            wyjąwszy Exception jako exc:
                self._conn_lost += 1
                self._fatal_error(exc, 'Fatal write error on pipe transport')
                zwróć
            jeżeli n == len(data):
                zwróć
            albo_inaczej n > 0:
                data = data[n:]
            self._loop.add_writer(self._fileno, self._write_ready)

        self._buffer.append(data)
        self._maybe_pause_protocol()

    def _write_ready(self):
        data = b''.join(self._buffer)
        assert data, 'Data should nie be empty'

        self._buffer.clear()
        spróbuj:
            n = os.write(self._fileno, data)
        wyjąwszy (BlockingIOError, InterruptedError):
            self._buffer.append(data)
        wyjąwszy Exception jako exc:
            self._conn_lost += 1
            # Remove writer here, _fatal_error() doesn't it
            # because _buffer jest empty.
            self._loop.remove_writer(self._fileno)
            self._fatal_error(exc, 'Fatal write error on pipe transport')
        inaczej:
            jeżeli n == len(data):
                self._loop.remove_writer(self._fileno)
                self._maybe_resume_protocol()  # May append to buffer.
                jeżeli nie self._buffer oraz self._closing:
                    self._loop.remove_reader(self._fileno)
                    self._call_connection_lost(Nic)
                zwróć
            albo_inaczej n > 0:
                data = data[n:]

            self._buffer.append(data)  # Try again later.

    def can_write_eof(self):
        zwróć Prawda

    def write_eof(self):
        jeżeli self._closing:
            zwróć
        assert self._pipe
        self._closing = Prawda
        jeżeli nie self._buffer:
            self._loop.remove_reader(self._fileno)
            self._loop.call_soon(self._call_connection_lost, Nic)

    def close(self):
        jeżeli self._pipe jest nie Nic oraz nie self._closing:
            # write_eof jest all what we needed to close the write pipe
            self.write_eof()

    # On Python 3.3 oraz older, objects przy a destructor part of a reference
    # cycle are never destroyed. It's nie more the case on Python 3.4 thanks
    # to the PEP 442.
    jeżeli compat.PY34:
        def __del__(self):
            jeżeli self._pipe jest nie Nic:
                warnings.warn("unclosed transport %r" % self, ResourceWarning)
                self._pipe.close()

    def abort(self):
        self._close(Nic)

    def _fatal_error(self, exc, message='Fatal error on pipe transport'):
        # should be called by exception handler only
        jeżeli isinstance(exc, (BrokenPipeError, ConnectionResetError)):
            jeżeli self._loop.get_debug():
                logger.debug("%r: %s", self, message, exc_info=Prawda)
        inaczej:
            self._loop.call_exception_handler({
                'message': message,
                'exception': exc,
                'transport': self,
                'protocol': self._protocol,
            })
        self._close(exc)

    def _close(self, exc=Nic):
        self._closing = Prawda
        jeżeli self._buffer:
            self._loop.remove_writer(self._fileno)
        self._buffer.clear()
        self._loop.remove_reader(self._fileno)
        self._loop.call_soon(self._call_connection_lost, exc)

    def _call_connection_lost(self, exc):
        spróbuj:
            self._protocol.connection_lost(exc)
        w_końcu:
            self._pipe.close()
            self._pipe = Nic
            self._protocol = Nic
            self._loop = Nic


jeżeli hasattr(os, 'set_inheritable'):
    # Python 3.4 oraz newer
    _set_inheritable = os.set_inheritable
inaczej:
    zaimportuj fcntl

    def _set_inheritable(fd, inheritable):
        cloexec_flag = getattr(fcntl, 'FD_CLOEXEC', 1)

        old = fcntl.fcntl(fd, fcntl.F_GETFD)
        jeżeli nie inheritable:
            fcntl.fcntl(fd, fcntl.F_SETFD, old | cloexec_flag)
        inaczej:
            fcntl.fcntl(fd, fcntl.F_SETFD, old & ~cloexec_flag)


klasa _UnixSubprocessTransport(base_subprocess.BaseSubprocessTransport):

    def _start(self, args, shell, stdin, stdout, stderr, bufsize, **kwargs):
        stdin_w = Nic
        jeżeli stdin == subprocess.PIPE:
            # Use a socket pair dla stdin, since nie all platforms
            # support selecting read events on the write end of a
            # socket (which we use w order to detect closing of the
            # other end).  Notably this jest needed on AIX, oraz works
            # just fine on other platforms.
            stdin, stdin_w = self._loop._socketpair()

            # Mark the write end of the stdin pipe jako non-inheritable,
            # needed by close_fds=Nieprawda on Python 3.3 oraz older
            # (Python 3.4 implements the PEP 446, socketpair returns
            # non-inheritable sockets)
            _set_inheritable(stdin_w.fileno(), Nieprawda)
        self._proc = subprocess.Popen(
            args, shell=shell, stdin=stdin, stdout=stdout, stderr=stderr,
            universal_newlines=Nieprawda, bufsize=bufsize, **kwargs)
        jeżeli stdin_w jest nie Nic:
            stdin.close()
            self._proc.stdin = open(stdin_w.detach(), 'wb', buffering=bufsize)


klasa AbstractChildWatcher:
    """Abstract base klasa dla monitoring child processes.

    Objects derived z this klasa monitor a collection of subprocesses oraz
    report their termination albo interruption by a signal.

    New callbacks are registered przy .add_child_handler(). Starting a new
    process must be done within a 'with' block to allow the watcher to suspend
    its activity until the new process jeżeli fully registered (this jest needed to
    prevent a race condition w some implementations).

    Example:
        przy watcher:
            proc = subprocess.Popen("sleep 1")
            watcher.add_child_handler(proc.pid, callback)

    Notes:
        Implementations of this klasa must be thread-safe.

        Since child watcher objects may catch the SIGCHLD signal oraz call
        waitpid(-1), there should be only one active object per process.
    """

    def add_child_handler(self, pid, callback, *args):
        """Register a new child handler.

        Arrange dla callback(pid, returncode, *args) to be called when
        process 'pid' terminates. Specifying another callback dla the same
        process replaces the previous handler.

        Note: callback() must be thread-safe.
        """
        podnieś NotImplementedError()

    def remove_child_handler(self, pid):
        """Removes the handler dla process 'pid'.

        The function returns Prawda jeżeli the handler was successfully removed,
        Nieprawda jeżeli there was nothing to remove."""

        podnieś NotImplementedError()

    def attach_loop(self, loop):
        """Attach the watcher to an event loop.

        If the watcher was previously attached to an event loop, then it jest
        first detached before attaching to the new loop.

        Note: loop may be Nic.
        """
        podnieś NotImplementedError()

    def close(self):
        """Close the watcher.

        This must be called to make sure that any underlying resource jest freed.
        """
        podnieś NotImplementedError()

    def __enter__(self):
        """Enter the watcher's context oraz allow starting new processes

        This function must zwróć self"""
        podnieś NotImplementedError()

    def __exit__(self, a, b, c):
        """Exit the watcher's context"""
        podnieś NotImplementedError()


klasa BaseChildWatcher(AbstractChildWatcher):

    def __init__(self):
        self._loop = Nic

    def close(self):
        self.attach_loop(Nic)

    def _do_waitpid(self, expected_pid):
        podnieś NotImplementedError()

    def _do_waitpid_all(self):
        podnieś NotImplementedError()

    def attach_loop(self, loop):
        assert loop jest Nic albo isinstance(loop, events.AbstractEventLoop)

        jeżeli self._loop jest nie Nic:
            self._loop.remove_signal_handler(signal.SIGCHLD)

        self._loop = loop
        jeżeli loop jest nie Nic:
            loop.add_signal_handler(signal.SIGCHLD, self._sig_chld)

            # Prevent a race condition w case a child terminated
            # during the switch.
            self._do_waitpid_all()

    def _sig_chld(self):
        spróbuj:
            self._do_waitpid_all()
        wyjąwszy Exception jako exc:
            # self._loop should always be available here
            # jako '_sig_chld' jest added jako a signal handler
            # w 'attach_loop'
            self._loop.call_exception_handler({
                'message': 'Unknown exception w SIGCHLD handler',
                'exception': exc,
            })

    def _compute_returncode(self, status):
        jeżeli os.WIFSIGNALED(status):
            # The child process died because of a signal.
            zwróć -os.WTERMSIG(status)
        albo_inaczej os.WIFEXITED(status):
            # The child process exited (e.g sys.exit()).
            zwróć os.WEXITSTATUS(status)
        inaczej:
            # The child exited, but we don't understand its status.
            # This shouldn't happen, but jeżeli it does, let's just
            # zwróć that status; perhaps that helps debug it.
            zwróć status


klasa SafeChildWatcher(BaseChildWatcher):
    """'Safe' child watcher implementation.

    This implementation avoids disrupting other code spawning processes by
    polling explicitly each process w the SIGCHLD handler instead of calling
    os.waitpid(-1).

    This jest a safe solution but it has a significant overhead when handling a
    big number of children (O(n) each time SIGCHLD jest podnieśd)
    """

    def __init__(self):
        super().__init__()
        self._callbacks = {}

    def close(self):
        self._callbacks.clear()
        super().close()

    def __enter__(self):
        zwróć self

    def __exit__(self, a, b, c):
        dalej

    def add_child_handler(self, pid, callback, *args):
        self._callbacks[pid] = (callback, args)

        # Prevent a race condition w case the child jest already terminated.
        self._do_waitpid(pid)

    def remove_child_handler(self, pid):
        spróbuj:
            usuń self._callbacks[pid]
            zwróć Prawda
        wyjąwszy KeyError:
            zwróć Nieprawda

    def _do_waitpid_all(self):

        dla pid w list(self._callbacks):
            self._do_waitpid(pid)

    def _do_waitpid(self, expected_pid):
        assert expected_pid > 0

        spróbuj:
            pid, status = os.waitpid(expected_pid, os.WNOHANG)
        wyjąwszy ChildProcessError:
            # The child process jest already reaped
            # (may happen jeżeli waitpid() jest called inaczejwhere).
            pid = expected_pid
            returncode = 255
            logger.warning(
                "Unknown child process pid %d, will report returncode 255",
                pid)
        inaczej:
            jeżeli pid == 0:
                # The child process jest still alive.
                zwróć

            returncode = self._compute_returncode(status)
            jeżeli self._loop.get_debug():
                logger.debug('process %s exited przy returncode %s',
                             expected_pid, returncode)

        spróbuj:
            callback, args = self._callbacks.pop(pid)
        wyjąwszy KeyError:  # pragma: no cover
            # May happen jeżeli .remove_child_handler() jest called
            # after os.waitpid() returns.
            jeżeli self._loop.get_debug():
                logger.warning("Child watcher got an unexpected pid: %r",
                               pid, exc_info=Prawda)
        inaczej:
            callback(pid, returncode, *args)


klasa FastChildWatcher(BaseChildWatcher):
    """'Fast' child watcher implementation.

    This implementation reaps every terminated processes by calling
    os.waitpid(-1) directly, possibly przerwijing other code spawning processes
    oraz waiting dla their termination.

    There jest no noticeable overhead when handling a big number of children
    (O(1) each time a child terminates).
    """
    def __init__(self):
        super().__init__()
        self._callbacks = {}
        self._lock = threading.Lock()
        self._zombies = {}
        self._forks = 0

    def close(self):
        self._callbacks.clear()
        self._zombies.clear()
        super().close()

    def __enter__(self):
        przy self._lock:
            self._forks += 1

            zwróć self

    def __exit__(self, a, b, c):
        przy self._lock:
            self._forks -= 1

            jeżeli self._forks albo nie self._zombies:
                zwróć

            collateral_victims = str(self._zombies)
            self._zombies.clear()

        logger.warning(
            "Caught subprocesses termination z unknown pids: %s",
            collateral_victims)

    def add_child_handler(self, pid, callback, *args):
        assert self._forks, "Must use the context manager"
        przy self._lock:
            spróbuj:
                returncode = self._zombies.pop(pid)
            wyjąwszy KeyError:
                # The child jest running.
                self._callbacks[pid] = callback, args
                zwróć

        # The child jest dead already. We can fire the callback.
        callback(pid, returncode, *args)

    def remove_child_handler(self, pid):
        spróbuj:
            usuń self._callbacks[pid]
            zwróć Prawda
        wyjąwszy KeyError:
            zwróć Nieprawda

    def _do_waitpid_all(self):
        # Because of signal coalescing, we must keep calling waitpid() as
        # long jako we're able to reap a child.
        dopóki Prawda:
            spróbuj:
                pid, status = os.waitpid(-1, os.WNOHANG)
            wyjąwszy ChildProcessError:
                # No more child processes exist.
                zwróć
            inaczej:
                jeżeli pid == 0:
                    # A child process jest still alive.
                    zwróć

                returncode = self._compute_returncode(status)

            przy self._lock:
                spróbuj:
                    callback, args = self._callbacks.pop(pid)
                wyjąwszy KeyError:
                    # unknown child
                    jeżeli self._forks:
                        # It may nie be registered yet.
                        self._zombies[pid] = returncode
                        jeżeli self._loop.get_debug():
                            logger.debug('unknown process %s exited '
                                         'przy returncode %s',
                                         pid, returncode)
                        kontynuuj
                    callback = Nic
                inaczej:
                    jeżeli self._loop.get_debug():
                        logger.debug('process %s exited przy returncode %s',
                                     pid, returncode)

            jeżeli callback jest Nic:
                logger.warning(
                    "Caught subprocess termination z unknown pid: "
                    "%d -> %d", pid, returncode)
            inaczej:
                callback(pid, returncode, *args)


klasa _UnixDefaultEventLoopPolicy(events.BaseDefaultEventLoopPolicy):
    """UNIX event loop policy przy a watcher dla child processes."""
    _loop_factory = _UnixSelectorEventLoop

    def __init__(self):
        super().__init__()
        self._watcher = Nic

    def _init_watcher(self):
        przy events._lock:
            jeżeli self._watcher jest Nic:  # pragma: no branch
                self._watcher = SafeChildWatcher()
                jeżeli isinstance(threading.current_thread(),
                              threading._MainThread):
                    self._watcher.attach_loop(self._local._loop)

    def set_event_loop(self, loop):
        """Set the event loop.

        As a side effect, jeżeli a child watcher was set before, then calling
        .set_event_loop() z the main thread will call .attach_loop(loop) on
        the child watcher.
        """

        super().set_event_loop(loop)

        jeżeli self._watcher jest nie Nic oraz \
            isinstance(threading.current_thread(), threading._MainThread):
            self._watcher.attach_loop(loop)

    def get_child_watcher(self):
        """Get the watcher dla child processes.

        If nie yet set, a SafeChildWatcher object jest automatically created.
        """
        jeżeli self._watcher jest Nic:
            self._init_watcher()

        zwróć self._watcher

    def set_child_watcher(self, watcher):
        """Set the watcher dla child processes."""

        assert watcher jest Nic albo isinstance(watcher, AbstractChildWatcher)

        jeżeli self._watcher jest nie Nic:
            self._watcher.close()

        self._watcher = watcher

SelectorEventLoop = _UnixSelectorEventLoop
DefaultEventLoopPolicy = _UnixDefaultEventLoopPolicy
