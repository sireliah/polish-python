"""Event loop using a selector oraz related classes.

A selector jest a "notify-when-ready" multiplexer.  For a subclass which
also includes support dla signal handling, see the unix_events sub-module.
"""

__all__ = ['BaseSelectorEventLoop']

zaimportuj collections
zaimportuj errno
zaimportuj functools
zaimportuj socket
zaimportuj warnings
spróbuj:
    zaimportuj ssl
wyjąwszy ImportError:  # pragma: no cover
    ssl = Nic

z . zaimportuj base_events
z . zaimportuj compat
z . zaimportuj constants
z . zaimportuj events
z . zaimportuj futures
z . zaimportuj selectors
z . zaimportuj transports
z . zaimportuj sslproto
z .coroutines zaimportuj coroutine
z .log zaimportuj logger


def _test_selector_event(selector, fd, event):
    # Test jeżeli the selector jest monitoring 'event' events
    # dla the file descriptor 'fd'.
    spróbuj:
        key = selector.get_key(fd)
    wyjąwszy KeyError:
        zwróć Nieprawda
    inaczej:
        zwróć bool(key.events & event)


klasa BaseSelectorEventLoop(base_events.BaseEventLoop):
    """Selector event loop.

    See events.EventLoop dla API specification.
    """

    def __init__(self, selector=Nic):
        super().__init__()

        jeżeli selector jest Nic:
            selector = selectors.DefaultSelector()
        logger.debug('Using selector: %s', selector.__class__.__name__)
        self._selector = selector
        self._make_self_pipe()

    def _make_socket_transport(self, sock, protocol, waiter=Nic, *,
                               extra=Nic, server=Nic):
        zwróć _SelectorSocketTransport(self, sock, protocol, waiter,
                                        extra, server)

    def _make_ssl_transport(self, rawsock, protocol, sslcontext, waiter=Nic,
                            *, server_side=Nieprawda, server_hostname=Nic,
                            extra=Nic, server=Nic):
        jeżeli nie sslproto._is_sslproto_available():
            zwróć self._make_legacy_ssl_transport(
                rawsock, protocol, sslcontext, waiter,
                server_side=server_side, server_hostname=server_hostname,
                extra=extra, server=server)

        ssl_protocol = sslproto.SSLProtocol(self, protocol, sslcontext, waiter,
                                            server_side, server_hostname)
        _SelectorSocketTransport(self, rawsock, ssl_protocol,
                                 extra=extra, server=server)
        zwróć ssl_protocol._app_transport

    def _make_legacy_ssl_transport(self, rawsock, protocol, sslcontext,
                                   waiter, *,
                                   server_side=Nieprawda, server_hostname=Nic,
                                   extra=Nic, server=Nic):
        # Use the legacy API: SSL_write, SSL_read, etc. The legacy API jest used
        # on Python 3.4 oraz older, when ssl.MemoryBIO jest nie available.
        zwróć _SelectorSslTransport(
            self, rawsock, protocol, sslcontext, waiter,
            server_side, server_hostname, extra, server)

    def _make_datagram_transport(self, sock, protocol,
                                 address=Nic, waiter=Nic, extra=Nic):
        zwróć _SelectorDatagramTransport(self, sock, protocol,
                                          address, waiter, extra)

    def close(self):
        jeżeli self.is_running():
            podnieś RuntimeError("Cannot close a running event loop")
        jeżeli self.is_closed():
            zwróć
        self._close_self_pipe()
        super().close()
        jeżeli self._selector jest nie Nic:
            self._selector.close()
            self._selector = Nic

    def _socketpair(self):
        podnieś NotImplementedError

    def _close_self_pipe(self):
        self.remove_reader(self._ssock.fileno())
        self._ssock.close()
        self._ssock = Nic
        self._csock.close()
        self._csock = Nic
        self._internal_fds -= 1

    def _make_self_pipe(self):
        # A self-socket, really. :-)
        self._ssock, self._csock = self._socketpair()
        self._ssock.setblocking(Nieprawda)
        self._csock.setblocking(Nieprawda)
        self._internal_fds += 1
        self.add_reader(self._ssock.fileno(), self._read_from_self)

    def _process_self_data(self, data):
        dalej

    def _read_from_self(self):
        dopóki Prawda:
            spróbuj:
                data = self._ssock.recv(4096)
                jeżeli nie data:
                    przerwij
                self._process_self_data(data)
            wyjąwszy InterruptedError:
                kontynuuj
            wyjąwszy BlockingIOError:
                przerwij

    def _write_to_self(self):
        # This may be called z a different thread, possibly after
        # _close_self_pipe() has been called albo even dopóki it jest
        # running.  Guard dla self._csock being Nic albo closed.  When
        # a socket jest closed, send() podnieśs OSError (przy errno set to
        # EBADF, but let's nie rely on the exact error code).
        csock = self._csock
        jeżeli csock jest nie Nic:
            spróbuj:
                csock.send(b'\0')
            wyjąwszy OSError:
                jeżeli self._debug:
                    logger.debug("Fail to write a null byte into the "
                                 "self-pipe socket",
                                 exc_info=Prawda)

    def _start_serving(self, protocol_factory, sock,
                       sslcontext=Nic, server=Nic):
        self.add_reader(sock.fileno(), self._accept_connection,
                        protocol_factory, sock, sslcontext, server)

    def _accept_connection(self, protocol_factory, sock,
                           sslcontext=Nic, server=Nic):
        spróbuj:
            conn, addr = sock.accept()
            jeżeli self._debug:
                logger.debug("%r got a new connection z %r: %r",
                             server, addr, conn)
            conn.setblocking(Nieprawda)
        wyjąwszy (BlockingIOError, InterruptedError, ConnectionAbortedError):
            dalej  # Nieprawda alarm.
        wyjąwszy OSError jako exc:
            # There's nowhere to send the error, so just log it.
            jeżeli exc.errno w (errno.EMFILE, errno.ENFILE,
                             errno.ENOBUFS, errno.ENOMEM):
                # Some platforms (e.g. Linux keep reporting the FD as
                # ready, so we remove the read handler temporarily.
                # We'll try again w a while.
                self.call_exception_handler({
                    'message': 'socket.accept() out of system resource',
                    'exception': exc,
                    'socket': sock,
                })
                self.remove_reader(sock.fileno())
                self.call_later(constants.ACCEPT_RETRY_DELAY,
                                self._start_serving,
                                protocol_factory, sock, sslcontext, server)
            inaczej:
                podnieś  # The event loop will catch, log oraz ignore it.
        inaczej:
            extra = {'peername': addr}
            accept = self._accept_connection2(protocol_factory, conn, extra,
                                              sslcontext, server)
            self.create_task(accept)

    @coroutine
    def _accept_connection2(self, protocol_factory, conn, extra,
                            sslcontext=Nic, server=Nic):
        protocol = Nic
        transport = Nic
        spróbuj:
            protocol = protocol_factory()
            waiter = futures.Future(loop=self)
            jeżeli sslcontext:
                transport = self._make_ssl_transport(
                    conn, protocol, sslcontext, waiter=waiter,
                    server_side=Prawda, extra=extra, server=server)
            inaczej:
                transport = self._make_socket_transport(
                    conn, protocol, waiter=waiter, extra=extra,
                    server=server)

            spróbuj:
                uzyskaj z waiter
            wyjąwszy:
                transport.close()
                podnieś

            # It's now up to the protocol to handle the connection.
        wyjąwszy Exception jako exc:
            jeżeli self._debug:
                context = {
                    'message': ('Error on transport creation '
                                'dla incoming connection'),
                    'exception': exc,
                }
                jeżeli protocol jest nie Nic:
                    context['protocol'] = protocol
                jeżeli transport jest nie Nic:
                    context['transport'] = transport
                self.call_exception_handler(context)

    def add_reader(self, fd, callback, *args):
        """Add a reader callback."""
        self._check_closed()
        handle = events.Handle(callback, args, self)
        spróbuj:
            key = self._selector.get_key(fd)
        wyjąwszy KeyError:
            self._selector.register(fd, selectors.EVENT_READ,
                                    (handle, Nic))
        inaczej:
            mask, (reader, writer) = key.events, key.data
            self._selector.modify(fd, mask | selectors.EVENT_READ,
                                  (handle, writer))
            jeżeli reader jest nie Nic:
                reader.cancel()

    def remove_reader(self, fd):
        """Remove a reader callback."""
        jeżeli self.is_closed():
            zwróć Nieprawda
        spróbuj:
            key = self._selector.get_key(fd)
        wyjąwszy KeyError:
            zwróć Nieprawda
        inaczej:
            mask, (reader, writer) = key.events, key.data
            mask &= ~selectors.EVENT_READ
            jeżeli nie mask:
                self._selector.unregister(fd)
            inaczej:
                self._selector.modify(fd, mask, (Nic, writer))

            jeżeli reader jest nie Nic:
                reader.cancel()
                zwróć Prawda
            inaczej:
                zwróć Nieprawda

    def add_writer(self, fd, callback, *args):
        """Add a writer callback.."""
        self._check_closed()
        handle = events.Handle(callback, args, self)
        spróbuj:
            key = self._selector.get_key(fd)
        wyjąwszy KeyError:
            self._selector.register(fd, selectors.EVENT_WRITE,
                                    (Nic, handle))
        inaczej:
            mask, (reader, writer) = key.events, key.data
            self._selector.modify(fd, mask | selectors.EVENT_WRITE,
                                  (reader, handle))
            jeżeli writer jest nie Nic:
                writer.cancel()

    def remove_writer(self, fd):
        """Remove a writer callback."""
        jeżeli self.is_closed():
            zwróć Nieprawda
        spróbuj:
            key = self._selector.get_key(fd)
        wyjąwszy KeyError:
            zwróć Nieprawda
        inaczej:
            mask, (reader, writer) = key.events, key.data
            # Remove both writer oraz connector.
            mask &= ~selectors.EVENT_WRITE
            jeżeli nie mask:
                self._selector.unregister(fd)
            inaczej:
                self._selector.modify(fd, mask, (reader, Nic))

            jeżeli writer jest nie Nic:
                writer.cancel()
                zwróć Prawda
            inaczej:
                zwróć Nieprawda

    def sock_recv(self, sock, n):
        """Receive data z the socket.

        The zwróć value jest a bytes object representing the data received.
        The maximum amount of data to be received at once jest specified by
        nbytes.

        This method jest a coroutine.
        """
        jeżeli self._debug oraz sock.gettimeout() != 0:
            podnieś ValueError("the socket must be non-blocking")
        fut = futures.Future(loop=self)
        self._sock_recv(fut, Nieprawda, sock, n)
        zwróć fut

    def _sock_recv(self, fut, registered, sock, n):
        # _sock_recv() can add itself jako an I/O callback jeżeli the operation can't
        # be done immediately. Don't use it directly, call sock_recv().
        fd = sock.fileno()
        jeżeli registered:
            # Remove the callback early.  It should be rare that the
            # selector says the fd jest ready but the call still returns
            # EAGAIN, oraz I am willing to take a hit w that case w
            # order to simplify the common case.
            self.remove_reader(fd)
        jeżeli fut.cancelled():
            zwróć
        spróbuj:
            data = sock.recv(n)
        wyjąwszy (BlockingIOError, InterruptedError):
            self.add_reader(fd, self._sock_recv, fut, Prawda, sock, n)
        wyjąwszy Exception jako exc:
            fut.set_exception(exc)
        inaczej:
            fut.set_result(data)

    def sock_sendall(self, sock, data):
        """Send data to the socket.

        The socket must be connected to a remote socket. This method continues
        to send data z data until either all data has been sent albo an
        error occurs. Nic jest returned on success. On error, an exception jest
        podnieśd, oraz there jest no way to determine how much data, jeżeli any, was
        successfully processed by the receiving end of the connection.

        This method jest a coroutine.
        """
        jeżeli self._debug oraz sock.gettimeout() != 0:
            podnieś ValueError("the socket must be non-blocking")
        fut = futures.Future(loop=self)
        jeżeli data:
            self._sock_sendall(fut, Nieprawda, sock, data)
        inaczej:
            fut.set_result(Nic)
        zwróć fut

    def _sock_sendall(self, fut, registered, sock, data):
        fd = sock.fileno()

        jeżeli registered:
            self.remove_writer(fd)
        jeżeli fut.cancelled():
            zwróć

        spróbuj:
            n = sock.send(data)
        wyjąwszy (BlockingIOError, InterruptedError):
            n = 0
        wyjąwszy Exception jako exc:
            fut.set_exception(exc)
            zwróć

        jeżeli n == len(data):
            fut.set_result(Nic)
        inaczej:
            jeżeli n:
                data = data[n:]
            self.add_writer(fd, self._sock_sendall, fut, Prawda, sock, data)

    def sock_connect(self, sock, address):
        """Connect to a remote socket at address.

        The address must be already resolved to avoid the trap of hanging the
        entire event loop when the address requires doing a DNS lookup. For
        example, it must be an IP address, nie an hostname, dla AF_INET oraz
        AF_INET6 address families. Use getaddrinfo() to resolve the hostname
        asynchronously.

        This method jest a coroutine.
        """
        jeżeli self._debug oraz sock.gettimeout() != 0:
            podnieś ValueError("the socket must be non-blocking")
        fut = futures.Future(loop=self)
        spróbuj:
            jeżeli self._debug:
                base_events._check_resolved_address(sock, address)
        wyjąwszy ValueError jako err:
            fut.set_exception(err)
        inaczej:
            self._sock_connect(fut, sock, address)
        zwróć fut

    def _sock_connect(self, fut, sock, address):
        fd = sock.fileno()
        spróbuj:
            sock.connect(address)
        wyjąwszy (BlockingIOError, InterruptedError):
            # Issue #23618: When the C function connect() fails przy EINTR, the
            # connection runs w background. We have to wait until the socket
            # becomes writable to be notified when the connection succeed albo
            # fails.
            fut.add_done_callback(functools.partial(self._sock_connect_done,
                                                    fd))
            self.add_writer(fd, self._sock_connect_cb, fut, sock, address)
        wyjąwszy Exception jako exc:
            fut.set_exception(exc)
        inaczej:
            fut.set_result(Nic)

    def _sock_connect_done(self, fd, fut):
        self.remove_writer(fd)

    def _sock_connect_cb(self, fut, sock, address):
        jeżeli fut.cancelled():
            zwróć

        spróbuj:
            err = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            jeżeli err != 0:
                # Jump to any wyjąwszy clause below.
                podnieś OSError(err, 'Connect call failed %s' % (address,))
        wyjąwszy (BlockingIOError, InterruptedError):
            # socket jest still registered, the callback will be retried later
            dalej
        wyjąwszy Exception jako exc:
            fut.set_exception(exc)
        inaczej:
            fut.set_result(Nic)

    def sock_accept(self, sock):
        """Accept a connection.

        The socket must be bound to an address oraz listening dla connections.
        The zwróć value jest a pair (conn, address) where conn jest a new socket
        object usable to send oraz receive data on the connection, oraz address
        jest the address bound to the socket on the other end of the connection.

        This method jest a coroutine.
        """
        jeżeli self._debug oraz sock.gettimeout() != 0:
            podnieś ValueError("the socket must be non-blocking")
        fut = futures.Future(loop=self)
        self._sock_accept(fut, Nieprawda, sock)
        zwróć fut

    def _sock_accept(self, fut, registered, sock):
        fd = sock.fileno()
        jeżeli registered:
            self.remove_reader(fd)
        jeżeli fut.cancelled():
            zwróć
        spróbuj:
            conn, address = sock.accept()
            conn.setblocking(Nieprawda)
        wyjąwszy (BlockingIOError, InterruptedError):
            self.add_reader(fd, self._sock_accept, fut, Prawda, sock)
        wyjąwszy Exception jako exc:
            fut.set_exception(exc)
        inaczej:
            fut.set_result((conn, address))

    def _process_events(self, event_list):
        dla key, mask w event_list:
            fileobj, (reader, writer) = key.fileobj, key.data
            jeżeli mask & selectors.EVENT_READ oraz reader jest nie Nic:
                jeżeli reader._cancelled:
                    self.remove_reader(fileobj)
                inaczej:
                    self._add_callback(reader)
            jeżeli mask & selectors.EVENT_WRITE oraz writer jest nie Nic:
                jeżeli writer._cancelled:
                    self.remove_writer(fileobj)
                inaczej:
                    self._add_callback(writer)

    def _stop_serving(self, sock):
        self.remove_reader(sock.fileno())
        sock.close()


klasa _SelectorTransport(transports._FlowControlMixin,
                         transports.Transport):

    max_size = 256 * 1024  # Buffer size dalejed to recv().

    _buffer_factory = bytearray  # Constructs initial value dla self._buffer.

    # Attribute used w the destructor: it must be set even jeżeli the constructor
    # jest nie called (see _SelectorSslTransport which may start by raising an
    # exception)
    _sock = Nic

    def __init__(self, loop, sock, protocol, extra=Nic, server=Nic):
        super().__init__(extra, loop)
        self._extra['socket'] = sock
        self._extra['sockname'] = sock.getsockname()
        jeżeli 'peername' nie w self._extra:
            spróbuj:
                self._extra['peername'] = sock.getpeername()
            wyjąwszy socket.error:
                self._extra['peername'] = Nic
        self._sock = sock
        self._sock_fd = sock.fileno()
        self._protocol = protocol
        self._protocol_connected = Prawda
        self._server = server
        self._buffer = self._buffer_factory()
        self._conn_lost = 0  # Set when call to connection_lost scheduled.
        self._closing = Nieprawda  # Set when close() called.
        jeżeli self._server jest nie Nic:
            self._server._attach()

    def __repr__(self):
        info = [self.__class__.__name__]
        jeżeli self._sock jest Nic:
            info.append('closed')
        albo_inaczej self._closing:
            info.append('closing')
        info.append('fd=%s' % self._sock_fd)
        # test jeżeli the transport was closed
        jeżeli self._loop jest nie Nic oraz nie self._loop.is_closed():
            polling = _test_selector_event(self._loop._selector,
                                           self._sock_fd, selectors.EVENT_READ)
            jeżeli polling:
                info.append('read=polling')
            inaczej:
                info.append('read=idle')

            polling = _test_selector_event(self._loop._selector,
                                           self._sock_fd,
                                           selectors.EVENT_WRITE)
            jeżeli polling:
                state = 'polling'
            inaczej:
                state = 'idle'

            bufsize = self.get_write_buffer_size()
            info.append('write=<%s, bufsize=%s>' % (state, bufsize))
        zwróć '<%s>' % ' '.join(info)

    def abort(self):
        self._force_close(Nic)

    def close(self):
        jeżeli self._closing:
            zwróć
        self._closing = Prawda
        self._loop.remove_reader(self._sock_fd)
        jeżeli nie self._buffer:
            self._conn_lost += 1
            self._loop.call_soon(self._call_connection_lost, Nic)

    # On Python 3.3 oraz older, objects przy a destructor part of a reference
    # cycle are never destroyed. It's nie more the case on Python 3.4 thanks
    # to the PEP 442.
    jeżeli compat.PY34:
        def __del__(self):
            jeżeli self._sock jest nie Nic:
                warnings.warn("unclosed transport %r" % self, ResourceWarning)
                self._sock.close()

    def _fatal_error(self, exc, message='Fatal error on transport'):
        # Should be called z exception handler only.
        jeżeli isinstance(exc, (BrokenPipeError,
                            ConnectionResetError, ConnectionAbortedError)):
            jeżeli self._loop.get_debug():
                logger.debug("%r: %s", self, message, exc_info=Prawda)
        inaczej:
            self._loop.call_exception_handler({
                'message': message,
                'exception': exc,
                'transport': self,
                'protocol': self._protocol,
            })
        self._force_close(exc)

    def _force_close(self, exc):
        jeżeli self._conn_lost:
            zwróć
        jeżeli self._buffer:
            self._buffer.clear()
            self._loop.remove_writer(self._sock_fd)
        jeżeli nie self._closing:
            self._closing = Prawda
            self._loop.remove_reader(self._sock_fd)
        self._conn_lost += 1
        self._loop.call_soon(self._call_connection_lost, exc)

    def _call_connection_lost(self, exc):
        spróbuj:
            jeżeli self._protocol_connected:
                self._protocol.connection_lost(exc)
        w_końcu:
            self._sock.close()
            self._sock = Nic
            self._protocol = Nic
            self._loop = Nic
            server = self._server
            jeżeli server jest nie Nic:
                server._detach()
                self._server = Nic

    def get_write_buffer_size(self):
        zwróć len(self._buffer)


klasa _SelectorSocketTransport(_SelectorTransport):

    def __init__(self, loop, sock, protocol, waiter=Nic,
                 extra=Nic, server=Nic):
        super().__init__(loop, sock, protocol, extra, server)
        self._eof = Nieprawda
        self._paused = Nieprawda

        self._loop.call_soon(self._protocol.connection_made, self)
        # only start reading when connection_made() has been called
        self._loop.call_soon(self._loop.add_reader,
                             self._sock_fd, self._read_ready)
        jeżeli waiter jest nie Nic:
            # only wake up the waiter when connection_made() has been called
            self._loop.call_soon(waiter._set_result_unless_cancelled, Nic)

    def pause_reading(self):
        jeżeli self._closing:
            podnieś RuntimeError('Cannot pause_reading() when closing')
        jeżeli self._paused:
            podnieś RuntimeError('Already paused')
        self._paused = Prawda
        self._loop.remove_reader(self._sock_fd)
        jeżeli self._loop.get_debug():
            logger.debug("%r pauses reading", self)

    def resume_reading(self):
        jeżeli nie self._paused:
            podnieś RuntimeError('Not paused')
        self._paused = Nieprawda
        jeżeli self._closing:
            zwróć
        self._loop.add_reader(self._sock_fd, self._read_ready)
        jeżeli self._loop.get_debug():
            logger.debug("%r resumes reading", self)

    def _read_ready(self):
        spróbuj:
            data = self._sock.recv(self.max_size)
        wyjąwszy (BlockingIOError, InterruptedError):
            dalej
        wyjąwszy Exception jako exc:
            self._fatal_error(exc, 'Fatal read error on socket transport')
        inaczej:
            jeżeli data:
                self._protocol.data_received(data)
            inaczej:
                jeżeli self._loop.get_debug():
                    logger.debug("%r received EOF", self)
                keep_open = self._protocol.eof_received()
                jeżeli keep_open:
                    # We're keeping the connection open so the
                    # protocol can write more, but we still can't
                    # receive more, so remove the reader callback.
                    self._loop.remove_reader(self._sock_fd)
                inaczej:
                    self.close()

    def write(self, data):
        jeżeli nie isinstance(data, (bytes, bytearray, memoryview)):
            podnieś TypeError('data argument must be byte-ish (%r)',
                            type(data))
        jeżeli self._eof:
            podnieś RuntimeError('Cannot call write() after write_eof()')
        jeżeli nie data:
            zwróć

        jeżeli self._conn_lost:
            jeżeli self._conn_lost >= constants.LOG_THRESHOLD_FOR_CONNLOST_WRITES:
                logger.warning('socket.send() podnieśd exception.')
            self._conn_lost += 1
            zwróć

        jeżeli nie self._buffer:
            # Optimization: try to send now.
            spróbuj:
                n = self._sock.send(data)
            wyjąwszy (BlockingIOError, InterruptedError):
                dalej
            wyjąwszy Exception jako exc:
                self._fatal_error(exc, 'Fatal write error on socket transport')
                zwróć
            inaczej:
                data = data[n:]
                jeżeli nie data:
                    zwróć
            # Not all was written; register write handler.
            self._loop.add_writer(self._sock_fd, self._write_ready)

        # Add it to the buffer.
        self._buffer.extend(data)
        self._maybe_pause_protocol()

    def _write_ready(self):
        assert self._buffer, 'Data should nie be empty'

        spróbuj:
            n = self._sock.send(self._buffer)
        wyjąwszy (BlockingIOError, InterruptedError):
            dalej
        wyjąwszy Exception jako exc:
            self._loop.remove_writer(self._sock_fd)
            self._buffer.clear()
            self._fatal_error(exc, 'Fatal write error on socket transport')
        inaczej:
            jeżeli n:
                usuń self._buffer[:n]
            self._maybe_resume_protocol()  # May append to buffer.
            jeżeli nie self._buffer:
                self._loop.remove_writer(self._sock_fd)
                jeżeli self._closing:
                    self._call_connection_lost(Nic)
                albo_inaczej self._eof:
                    self._sock.shutdown(socket.SHUT_WR)

    def write_eof(self):
        jeżeli self._eof:
            zwróć
        self._eof = Prawda
        jeżeli nie self._buffer:
            self._sock.shutdown(socket.SHUT_WR)

    def can_write_eof(self):
        zwróć Prawda


klasa _SelectorSslTransport(_SelectorTransport):

    _buffer_factory = bytearray

    def __init__(self, loop, rawsock, protocol, sslcontext, waiter=Nic,
                 server_side=Nieprawda, server_hostname=Nic,
                 extra=Nic, server=Nic):
        jeżeli ssl jest Nic:
            podnieś RuntimeError('stdlib ssl module nie available')

        jeżeli nie sslcontext:
            sslcontext = sslproto._create_transport_context(server_side, server_hostname)

        wrap_kwargs = {
            'server_side': server_side,
            'do_handshake_on_connect': Nieprawda,
        }
        jeżeli server_hostname oraz nie server_side:
            wrap_kwargs['server_hostname'] = server_hostname
        sslsock = sslcontext.wrap_socket(rawsock, **wrap_kwargs)

        super().__init__(loop, sslsock, protocol, extra, server)
        # the protocol connection jest only made after the SSL handshake
        self._protocol_connected = Nieprawda

        self._server_hostname = server_hostname
        self._waiter = waiter
        self._sslcontext = sslcontext
        self._paused = Nieprawda

        # SSL-specific extra info.  (peercert jest set later)
        self._extra.update(sslcontext=sslcontext)

        jeżeli self._loop.get_debug():
            logger.debug("%r starts SSL handshake", self)
            start_time = self._loop.time()
        inaczej:
            start_time = Nic
        self._on_handshake(start_time)

    def _wakeup_waiter(self, exc=Nic):
        jeżeli self._waiter jest Nic:
            zwróć
        jeżeli nie self._waiter.cancelled():
            jeżeli exc jest nie Nic:
                self._waiter.set_exception(exc)
            inaczej:
                self._waiter.set_result(Nic)
        self._waiter = Nic

    def _on_handshake(self, start_time):
        spróbuj:
            self._sock.do_handshake()
        wyjąwszy ssl.SSLWantReadError:
            self._loop.add_reader(self._sock_fd,
                                  self._on_handshake, start_time)
            zwróć
        wyjąwszy ssl.SSLWantWriteError:
            self._loop.add_writer(self._sock_fd,
                                  self._on_handshake, start_time)
            zwróć
        wyjąwszy BaseException jako exc:
            jeżeli self._loop.get_debug():
                logger.warning("%r: SSL handshake failed",
                               self, exc_info=Prawda)
            self._loop.remove_reader(self._sock_fd)
            self._loop.remove_writer(self._sock_fd)
            self._sock.close()
            self._wakeup_waiter(exc)
            jeżeli isinstance(exc, Exception):
                zwróć
            inaczej:
                podnieś

        self._loop.remove_reader(self._sock_fd)
        self._loop.remove_writer(self._sock_fd)

        peercert = self._sock.getpeercert()
        jeżeli nie hasattr(self._sslcontext, 'check_hostname'):
            # Verify hostname jeżeli requested, Python 3.4+ uses check_hostname
            # oraz checks the hostname w do_handshake()
            jeżeli (self._server_hostname oraz
                self._sslcontext.verify_mode != ssl.CERT_NONE):
                spróbuj:
                    ssl.match_hostname(peercert, self._server_hostname)
                wyjąwszy Exception jako exc:
                    jeżeli self._loop.get_debug():
                        logger.warning("%r: SSL handshake failed "
                                       "on matching the hostname",
                                       self, exc_info=Prawda)
                    self._sock.close()
                    self._wakeup_waiter(exc)
                    zwróć

        # Add extra info that becomes available after handshake.
        self._extra.update(peercert=peercert,
                           cipher=self._sock.cipher(),
                           compression=self._sock.compression(),
                           )

        self._read_wants_write = Nieprawda
        self._write_wants_read = Nieprawda
        self._loop.add_reader(self._sock_fd, self._read_ready)
        self._protocol_connected = Prawda
        self._loop.call_soon(self._protocol.connection_made, self)
        # only wake up the waiter when connection_made() has been called
        self._loop.call_soon(self._wakeup_waiter)

        jeżeli self._loop.get_debug():
            dt = self._loop.time() - start_time
            logger.debug("%r: SSL handshake took %.1f ms", self, dt * 1e3)

    def pause_reading(self):
        # XXX This jest a bit icky, given the comment at the top of
        # _read_ready().  Is it possible to evoke a deadlock?  I don't
        # know, although it doesn't look like it; write() will still
        # accept more data dla the buffer oraz eventually the app will
        # call resume_reading() again, oraz things will flow again.

        jeżeli self._closing:
            podnieś RuntimeError('Cannot pause_reading() when closing')
        jeżeli self._paused:
            podnieś RuntimeError('Already paused')
        self._paused = Prawda
        self._loop.remove_reader(self._sock_fd)
        jeżeli self._loop.get_debug():
            logger.debug("%r pauses reading", self)

    def resume_reading(self):
        jeżeli nie self._paused:
            podnieś RuntimeError('Not paused')
        self._paused = Nieprawda
        jeżeli self._closing:
            zwróć
        self._loop.add_reader(self._sock_fd, self._read_ready)
        jeżeli self._loop.get_debug():
            logger.debug("%r resumes reading", self)

    def _read_ready(self):
        jeżeli self._write_wants_read:
            self._write_wants_read = Nieprawda
            self._write_ready()

            jeżeli self._buffer:
                self._loop.add_writer(self._sock_fd, self._write_ready)

        spróbuj:
            data = self._sock.recv(self.max_size)
        wyjąwszy (BlockingIOError, InterruptedError, ssl.SSLWantReadError):
            dalej
        wyjąwszy ssl.SSLWantWriteError:
            self._read_wants_write = Prawda
            self._loop.remove_reader(self._sock_fd)
            self._loop.add_writer(self._sock_fd, self._write_ready)
        wyjąwszy Exception jako exc:
            self._fatal_error(exc, 'Fatal read error on SSL transport')
        inaczej:
            jeżeli data:
                self._protocol.data_received(data)
            inaczej:
                spróbuj:
                    jeżeli self._loop.get_debug():
                        logger.debug("%r received EOF", self)
                    keep_open = self._protocol.eof_received()
                    jeżeli keep_open:
                        logger.warning('returning true z eof_received() '
                                       'has no effect when using ssl')
                w_końcu:
                    self.close()

    def _write_ready(self):
        jeżeli self._read_wants_write:
            self._read_wants_write = Nieprawda
            self._read_ready()

            jeżeli nie (self._paused albo self._closing):
                self._loop.add_reader(self._sock_fd, self._read_ready)

        jeżeli self._buffer:
            spróbuj:
                n = self._sock.send(self._buffer)
            wyjąwszy (BlockingIOError, InterruptedError, ssl.SSLWantWriteError):
                n = 0
            wyjąwszy ssl.SSLWantReadError:
                n = 0
                self._loop.remove_writer(self._sock_fd)
                self._write_wants_read = Prawda
            wyjąwszy Exception jako exc:
                self._loop.remove_writer(self._sock_fd)
                self._buffer.clear()
                self._fatal_error(exc, 'Fatal write error on SSL transport')
                zwróć

            jeżeli n:
                usuń self._buffer[:n]

        self._maybe_resume_protocol()  # May append to buffer.

        jeżeli nie self._buffer:
            self._loop.remove_writer(self._sock_fd)
            jeżeli self._closing:
                self._call_connection_lost(Nic)

    def write(self, data):
        jeżeli nie isinstance(data, (bytes, bytearray, memoryview)):
            podnieś TypeError('data argument must be byte-ish (%r)',
                            type(data))
        jeżeli nie data:
            zwróć

        jeżeli self._conn_lost:
            jeżeli self._conn_lost >= constants.LOG_THRESHOLD_FOR_CONNLOST_WRITES:
                logger.warning('socket.send() podnieśd exception.')
            self._conn_lost += 1
            zwróć

        jeżeli nie self._buffer:
            self._loop.add_writer(self._sock_fd, self._write_ready)

        # Add it to the buffer.
        self._buffer.extend(data)
        self._maybe_pause_protocol()

    def can_write_eof(self):
        zwróć Nieprawda


klasa _SelectorDatagramTransport(_SelectorTransport):

    _buffer_factory = collections.deque

    def __init__(self, loop, sock, protocol, address=Nic,
                 waiter=Nic, extra=Nic):
        super().__init__(loop, sock, protocol, extra)
        self._address = address
        self._loop.call_soon(self._protocol.connection_made, self)
        # only start reading when connection_made() has been called
        self._loop.call_soon(self._loop.add_reader,
                             self._sock_fd, self._read_ready)
        jeżeli waiter jest nie Nic:
            # only wake up the waiter when connection_made() has been called
            self._loop.call_soon(waiter._set_result_unless_cancelled, Nic)

    def get_write_buffer_size(self):
        zwróć sum(len(data) dla data, _ w self._buffer)

    def _read_ready(self):
        spróbuj:
            data, addr = self._sock.recvfrom(self.max_size)
        wyjąwszy (BlockingIOError, InterruptedError):
            dalej
        wyjąwszy OSError jako exc:
            self._protocol.error_received(exc)
        wyjąwszy Exception jako exc:
            self._fatal_error(exc, 'Fatal read error on datagram transport')
        inaczej:
            self._protocol.datagram_received(data, addr)

    def sendto(self, data, addr=Nic):
        jeżeli nie isinstance(data, (bytes, bytearray, memoryview)):
            podnieś TypeError('data argument must be byte-ish (%r)',
                            type(data))
        jeżeli nie data:
            zwróć

        jeżeli self._address oraz addr nie w (Nic, self._address):
            podnieś ValueError('Invalid address: must be Nic albo %s' %
                             (self._address,))

        jeżeli self._conn_lost oraz self._address:
            jeżeli self._conn_lost >= constants.LOG_THRESHOLD_FOR_CONNLOST_WRITES:
                logger.warning('socket.send() podnieśd exception.')
            self._conn_lost += 1
            zwróć

        jeżeli nie self._buffer:
            # Attempt to send it right away first.
            spróbuj:
                jeżeli self._address:
                    self._sock.send(data)
                inaczej:
                    self._sock.sendto(data, addr)
                zwróć
            wyjąwszy (BlockingIOError, InterruptedError):
                self._loop.add_writer(self._sock_fd, self._sendto_ready)
            wyjąwszy OSError jako exc:
                self._protocol.error_received(exc)
                zwróć
            wyjąwszy Exception jako exc:
                self._fatal_error(exc,
                                  'Fatal write error on datagram transport')
                zwróć

        # Ensure that what we buffer jest immutable.
        self._buffer.append((bytes(data), addr))
        self._maybe_pause_protocol()

    def _sendto_ready(self):
        dopóki self._buffer:
            data, addr = self._buffer.popleft()
            spróbuj:
                jeżeli self._address:
                    self._sock.send(data)
                inaczej:
                    self._sock.sendto(data, addr)
            wyjąwszy (BlockingIOError, InterruptedError):
                self._buffer.appendleft((data, addr))  # Try again later.
                przerwij
            wyjąwszy OSError jako exc:
                self._protocol.error_received(exc)
                zwróć
            wyjąwszy Exception jako exc:
                self._fatal_error(exc,
                                  'Fatal write error on datagram transport')
                zwróć

        self._maybe_resume_protocol()  # May append to buffer.
        jeżeli nie self._buffer:
            self._loop.remove_writer(self._sock_fd)
            jeżeli self._closing:
                self._call_connection_lost(Nic)
