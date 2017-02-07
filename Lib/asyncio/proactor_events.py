"""Event loop using a proactor oraz related classes.

A proactor jest a "notify-on-completion" multiplexer.  Currently a
proactor jest only implemented on Windows przy IOCP.
"""

__all__ = ['BaseProactorEventLoop']

zaimportuj socket
zaimportuj warnings

z . zaimportuj base_events
z . zaimportuj compat
z . zaimportuj constants
z . zaimportuj futures
z . zaimportuj sslproto
z . zaimportuj transports
z .log zaimportuj logger


klasa _ProactorBasePipeTransport(transports._FlowControlMixin,
                                 transports.BaseTransport):
    """Base klasa dla pipe oraz socket transports."""

    def __init__(self, loop, sock, protocol, waiter=Nic,
                 extra=Nic, server=Nic):
        super().__init__(extra, loop)
        self._set_extra(sock)
        self._sock = sock
        self._protocol = protocol
        self._server = server
        self._buffer = Nic  # Nic albo bytearray.
        self._read_fut = Nic
        self._write_fut = Nic
        self._pending_write = 0
        self._conn_lost = 0
        self._closing = Nieprawda  # Set when close() called.
        self._eof_written = Nieprawda
        jeżeli self._server jest nie Nic:
            self._server._attach()
        self._loop.call_soon(self._protocol.connection_made, self)
        jeżeli waiter jest nie Nic:
            # only wake up the waiter when connection_made() has been called
            self._loop.call_soon(waiter._set_result_unless_cancelled, Nic)

    def __repr__(self):
        info = [self.__class__.__name__]
        jeżeli self._sock jest Nic:
            info.append('closed')
        albo_inaczej self._closing:
            info.append('closing')
        jeżeli self._sock jest nie Nic:
            info.append('fd=%s' % self._sock.fileno())
        jeżeli self._read_fut jest nie Nic:
            info.append('read=%s' % self._read_fut)
        jeżeli self._write_fut jest nie Nic:
            info.append("write=%r" % self._write_fut)
        jeżeli self._buffer:
            bufsize = len(self._buffer)
            info.append('write_bufsize=%s' % bufsize)
        jeżeli self._eof_written:
            info.append('EOF written')
        zwróć '<%s>' % ' '.join(info)

    def _set_extra(self, sock):
        self._extra['pipe'] = sock

    def close(self):
        jeżeli self._closing:
            zwróć
        self._closing = Prawda
        self._conn_lost += 1
        jeżeli nie self._buffer oraz self._write_fut jest Nic:
            self._loop.call_soon(self._call_connection_lost, Nic)
        jeżeli self._read_fut jest nie Nic:
            self._read_fut.cancel()
            self._read_fut = Nic

    # On Python 3.3 oraz older, objects przy a destructor part of a reference
    # cycle are never destroyed. It's nie more the case on Python 3.4 thanks
    # to the PEP 442.
    jeżeli compat.PY34:
        def __del__(self):
            jeżeli self._sock jest nie Nic:
                warnings.warn("unclosed transport %r" % self, ResourceWarning)
                self.close()

    def _fatal_error(self, exc, message='Fatal error on pipe transport'):
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
        self._force_close(exc)

    def _force_close(self, exc):
        jeżeli self._closing:
            zwróć
        self._closing = Prawda
        self._conn_lost += 1
        jeżeli self._write_fut:
            self._write_fut.cancel()
            self._write_fut = Nic
        jeżeli self._read_fut:
            self._read_fut.cancel()
            self._read_fut = Nic
        self._pending_write = 0
        self._buffer = Nic
        self._loop.call_soon(self._call_connection_lost, exc)

    def _call_connection_lost(self, exc):
        spróbuj:
            self._protocol.connection_lost(exc)
        w_końcu:
            # XXX If there jest a pending overlapped read on the other
            # end then it may fail przy ERROR_NETNAME_DELETED jeżeli we
            # just close our end.  First calling shutdown() seems to
            # cure it, but maybe using DisconnectEx() would be better.
            jeżeli hasattr(self._sock, 'shutdown'):
                self._sock.shutdown(socket.SHUT_RDWR)
            self._sock.close()
            self._sock = Nic
            server = self._server
            jeżeli server jest nie Nic:
                server._detach()
                self._server = Nic

    def get_write_buffer_size(self):
        size = self._pending_write
        jeżeli self._buffer jest nie Nic:
            size += len(self._buffer)
        zwróć size


klasa _ProactorReadPipeTransport(_ProactorBasePipeTransport,
                                 transports.ReadTransport):
    """Transport dla read pipes."""

    def __init__(self, loop, sock, protocol, waiter=Nic,
                 extra=Nic, server=Nic):
        super().__init__(loop, sock, protocol, waiter, extra, server)
        self._paused = Nieprawda
        self._loop.call_soon(self._loop_reading)

    def pause_reading(self):
        jeżeli self._closing:
            podnieś RuntimeError('Cannot pause_reading() when closing')
        jeżeli self._paused:
            podnieś RuntimeError('Already paused')
        self._paused = Prawda
        jeżeli self._loop.get_debug():
            logger.debug("%r pauses reading", self)

    def resume_reading(self):
        jeżeli nie self._paused:
            podnieś RuntimeError('Not paused')
        self._paused = Nieprawda
        jeżeli self._closing:
            zwróć
        self._loop.call_soon(self._loop_reading, self._read_fut)
        jeżeli self._loop.get_debug():
            logger.debug("%r resumes reading", self)

    def _loop_reading(self, fut=Nic):
        jeżeli self._paused:
            zwróć
        data = Nic

        spróbuj:
            jeżeli fut jest nie Nic:
                assert self._read_fut jest fut albo (self._read_fut jest Nic oraz
                                                 self._closing)
                self._read_fut = Nic
                data = fut.result()  # deliver data later w "finally" clause

            jeżeli self._closing:
                # since close() has been called we ignore any read data
                data = Nic
                zwróć

            jeżeli data == b'':
                # we got end-of-file so no need to reschedule a new read
                zwróć

            # reschedule a new read
            self._read_fut = self._loop._proactor.recv(self._sock, 4096)
        wyjąwszy ConnectionAbortedError jako exc:
            jeżeli nie self._closing:
                self._fatal_error(exc, 'Fatal read error on pipe transport')
            albo_inaczej self._loop.get_debug():
                logger.debug("Read error on pipe transport dopóki closing",
                             exc_info=Prawda)
        wyjąwszy ConnectionResetError jako exc:
            self._force_close(exc)
        wyjąwszy OSError jako exc:
            self._fatal_error(exc, 'Fatal read error on pipe transport')
        wyjąwszy futures.CancelledError:
            jeżeli nie self._closing:
                podnieś
        inaczej:
            self._read_fut.add_done_callback(self._loop_reading)
        w_końcu:
            jeżeli data:
                self._protocol.data_received(data)
            albo_inaczej data jest nie Nic:
                jeżeli self._loop.get_debug():
                    logger.debug("%r received EOF", self)
                keep_open = self._protocol.eof_received()
                jeżeli nie keep_open:
                    self.close()


klasa _ProactorBaseWritePipeTransport(_ProactorBasePipeTransport,
                                      transports.WriteTransport):
    """Transport dla write pipes."""

    def write(self, data):
        jeżeli nie isinstance(data, (bytes, bytearray, memoryview)):
            podnieś TypeError('data argument must be byte-ish (%r)',
                            type(data))
        jeżeli self._eof_written:
            podnieś RuntimeError('write_eof() already called')

        jeżeli nie data:
            zwróć

        jeżeli self._conn_lost:
            jeżeli self._conn_lost >= constants.LOG_THRESHOLD_FOR_CONNLOST_WRITES:
                logger.warning('socket.send() podnieśd exception.')
            self._conn_lost += 1
            zwróć

        # Observable states:
        # 1. IDLE: _write_fut oraz _buffer both Nic
        # 2. WRITING: _write_fut set; _buffer Nic
        # 3. BACKED UP: _write_fut set; _buffer a bytearray
        # We always copy the data, so the caller can't modify it
        # dopóki we're still waiting dla the I/O to happen.
        jeżeli self._write_fut jest Nic:  # IDLE -> WRITING
            assert self._buffer jest Nic
            # Pass a copy, wyjąwszy jeżeli it's already immutable.
            self._loop_writing(data=bytes(data))
        albo_inaczej nie self._buffer:  # WRITING -> BACKED UP
            # Make a mutable copy which we can extend.
            self._buffer = bytearray(data)
            self._maybe_pause_protocol()
        inaczej:  # BACKED UP
            # Append to buffer (also copies).
            self._buffer.extend(data)
            self._maybe_pause_protocol()

    def _loop_writing(self, f=Nic, data=Nic):
        spróbuj:
            assert f jest self._write_fut
            self._write_fut = Nic
            self._pending_write = 0
            jeżeli f:
                f.result()
            jeżeli data jest Nic:
                data = self._buffer
                self._buffer = Nic
            jeżeli nie data:
                jeżeli self._closing:
                    self._loop.call_soon(self._call_connection_lost, Nic)
                jeżeli self._eof_written:
                    self._sock.shutdown(socket.SHUT_WR)
                # Now that we've reduced the buffer size, tell the
                # protocol to resume writing jeżeli it was paused.  Note that
                # we do this last since the callback jest called immediately
                # oraz it may add more data to the buffer (even causing the
                # protocol to be paused again).
                self._maybe_resume_protocol()
            inaczej:
                self._write_fut = self._loop._proactor.send(self._sock, data)
                jeżeli nie self._write_fut.done():
                    assert self._pending_write == 0
                    self._pending_write = len(data)
                    self._write_fut.add_done_callback(self._loop_writing)
                    self._maybe_pause_protocol()
                inaczej:
                    self._write_fut.add_done_callback(self._loop_writing)
        wyjąwszy ConnectionResetError jako exc:
            self._force_close(exc)
        wyjąwszy OSError jako exc:
            self._fatal_error(exc, 'Fatal write error on pipe transport')

    def can_write_eof(self):
        zwróć Prawda

    def write_eof(self):
        self.close()

    def abort(self):
        self._force_close(Nic)


klasa _ProactorWritePipeTransport(_ProactorBaseWritePipeTransport):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._read_fut = self._loop._proactor.recv(self._sock, 16)
        self._read_fut.add_done_callback(self._pipe_closed)

    def _pipe_closed(self, fut):
        jeżeli fut.cancelled():
            # the transport has been closed
            zwróć
        assert fut.result() == b''
        jeżeli self._closing:
            assert self._read_fut jest Nic
            zwróć
        assert fut jest self._read_fut, (fut, self._read_fut)
        self._read_fut = Nic
        jeżeli self._write_fut jest nie Nic:
            self._force_close(BrokenPipeError())
        inaczej:
            self.close()


klasa _ProactorDuplexPipeTransport(_ProactorReadPipeTransport,
                                   _ProactorBaseWritePipeTransport,
                                   transports.Transport):
    """Transport dla duplex pipes."""

    def can_write_eof(self):
        zwróć Nieprawda

    def write_eof(self):
        podnieś NotImplementedError


klasa _ProactorSocketTransport(_ProactorReadPipeTransport,
                               _ProactorBaseWritePipeTransport,
                               transports.Transport):
    """Transport dla connected sockets."""

    def _set_extra(self, sock):
        self._extra['socket'] = sock
        spróbuj:
            self._extra['sockname'] = sock.getsockname()
        wyjąwszy (socket.error, AttributeError):
            jeżeli self._loop.get_debug():
                logger.warning("getsockname() failed on %r",
                             sock, exc_info=Prawda)
        jeżeli 'peername' nie w self._extra:
            spróbuj:
                self._extra['peername'] = sock.getpeername()
            wyjąwszy (socket.error, AttributeError):
                jeżeli self._loop.get_debug():
                    logger.warning("getpeername() failed on %r",
                                   sock, exc_info=Prawda)

    def can_write_eof(self):
        zwróć Prawda

    def write_eof(self):
        jeżeli self._closing albo self._eof_written:
            zwróć
        self._eof_written = Prawda
        jeżeli self._write_fut jest Nic:
            self._sock.shutdown(socket.SHUT_WR)


klasa BaseProactorEventLoop(base_events.BaseEventLoop):

    def __init__(self, proactor):
        super().__init__()
        logger.debug('Using proactor: %s', proactor.__class__.__name__)
        self._proactor = proactor
        self._selector = proactor   # convenient alias
        self._self_reading_future = Nic
        self._accept_futures = {}   # socket file descriptor => Future
        proactor.set_loop(self)
        self._make_self_pipe()

    def _make_socket_transport(self, sock, protocol, waiter=Nic,
                               extra=Nic, server=Nic):
        zwróć _ProactorSocketTransport(self, sock, protocol, waiter,
                                        extra, server)

    def _make_ssl_transport(self, rawsock, protocol, sslcontext, waiter=Nic,
                            *, server_side=Nieprawda, server_hostname=Nic,
                            extra=Nic, server=Nic):
        jeżeli nie sslproto._is_sslproto_available():
            podnieś NotImplementedError("Proactor event loop requires Python 3.5"
                                      " albo newer (ssl.MemoryBIO) to support "
                                      "SSL")

        ssl_protocol = sslproto.SSLProtocol(self, protocol, sslcontext, waiter,
                                            server_side, server_hostname)
        _ProactorSocketTransport(self, rawsock, ssl_protocol,
                                 extra=extra, server=server)
        zwróć ssl_protocol._app_transport

    def _make_duplex_pipe_transport(self, sock, protocol, waiter=Nic,
                                    extra=Nic):
        zwróć _ProactorDuplexPipeTransport(self,
                                            sock, protocol, waiter, extra)

    def _make_read_pipe_transport(self, sock, protocol, waiter=Nic,
                                  extra=Nic):
        zwróć _ProactorReadPipeTransport(self, sock, protocol, waiter, extra)

    def _make_write_pipe_transport(self, sock, protocol, waiter=Nic,
                                   extra=Nic):
        # We want connection_lost() to be called when other end closes
        zwróć _ProactorWritePipeTransport(self,
                                           sock, protocol, waiter, extra)

    def close(self):
        jeżeli self.is_running():
            podnieś RuntimeError("Cannot close a running event loop")
        jeżeli self.is_closed():
            zwróć

        # Call these methods before closing the event loop (before calling
        # BaseEventLoop.close), because they can schedule callbacks with
        # call_soon(), which jest forbidden when the event loop jest closed.
        self._stop_accept_futures()
        self._close_self_pipe()
        self._proactor.close()
        self._proactor = Nic
        self._selector = Nic

        # Close the event loop
        super().close()

    def sock_recv(self, sock, n):
        zwróć self._proactor.recv(sock, n)

    def sock_sendall(self, sock, data):
        zwróć self._proactor.send(sock, data)

    def sock_connect(self, sock, address):
        spróbuj:
            jeżeli self._debug:
                base_events._check_resolved_address(sock, address)
        wyjąwszy ValueError jako err:
            fut = futures.Future(loop=self)
            fut.set_exception(err)
            zwróć fut
        inaczej:
            zwróć self._proactor.connect(sock, address)

    def sock_accept(self, sock):
        zwróć self._proactor.accept(sock)

    def _socketpair(self):
        podnieś NotImplementedError

    def _close_self_pipe(self):
        jeżeli self._self_reading_future jest nie Nic:
            self._self_reading_future.cancel()
            self._self_reading_future = Nic
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
        self.call_soon(self._loop_self_reading)

    def _loop_self_reading(self, f=Nic):
        spróbuj:
            jeżeli f jest nie Nic:
                f.result()  # may podnieś
            f = self._proactor.recv(self._ssock, 4096)
        wyjąwszy futures.CancelledError:
            # _close_self_pipe() has been called, stop waiting dla data
            zwróć
        wyjąwszy Exception jako exc:
            self.call_exception_handler({
                'message': 'Error on reading z the event loop self pipe',
                'exception': exc,
                'loop': self,
            })
        inaczej:
            self._self_reading_future = f
            f.add_done_callback(self._loop_self_reading)

    def _write_to_self(self):
        self._csock.send(b'\0')

    def _start_serving(self, protocol_factory, sock,
                       sslcontext=Nic, server=Nic):

        def loop(f=Nic):
            spróbuj:
                jeżeli f jest nie Nic:
                    conn, addr = f.result()
                    jeżeli self._debug:
                        logger.debug("%r got a new connection z %r: %r",
                                     server, addr, conn)
                    protocol = protocol_factory()
                    jeżeli sslcontext jest nie Nic:
                        self._make_ssl_transport(
                            conn, protocol, sslcontext, server_side=Prawda,
                            extra={'peername': addr}, server=server)
                    inaczej:
                        self._make_socket_transport(
                            conn, protocol,
                            extra={'peername': addr}, server=server)
                jeżeli self.is_closed():
                    zwróć
                f = self._proactor.accept(sock)
            wyjąwszy OSError jako exc:
                jeżeli sock.fileno() != -1:
                    self.call_exception_handler({
                        'message': 'Accept failed on a socket',
                        'exception': exc,
                        'socket': sock,
                    })
                    sock.close()
                albo_inaczej self._debug:
                    logger.debug("Accept failed on socket %r",
                                 sock, exc_info=Prawda)
            wyjąwszy futures.CancelledError:
                sock.close()
            inaczej:
                self._accept_futures[sock.fileno()] = f
                f.add_done_callback(loop)

        self.call_soon(loop)

    def _process_events(self, event_list):
        # Events are processed w the IocpProactor._poll() method
        dalej

    def _stop_accept_futures(self):
        dla future w self._accept_futures.values():
            future.cancel()
        self._accept_futures.clear()

    def _stop_serving(self, sock):
        self._stop_accept_futures()
        self._proactor._stop_serving(sock)
        sock.close()
