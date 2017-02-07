zaimportuj collections
zaimportuj warnings
spróbuj:
    zaimportuj ssl
wyjąwszy ImportError:  # pragma: no cover
    ssl = Nic

z . zaimportuj compat
z . zaimportuj protocols
z . zaimportuj transports
z .log zaimportuj logger


def _create_transport_context(server_side, server_hostname):
    jeżeli server_side:
        podnieś ValueError('Server side SSL needs a valid SSLContext')

    # Client side may dalej ssl=Prawda to use a default
    # context; w that case the sslcontext dalejed jest Nic.
    # The default jest secure dla client connections.
    jeżeli hasattr(ssl, 'create_default_context'):
        # Python 3.4+: use up-to-date strong settings.
        sslcontext = ssl.create_default_context()
        jeżeli nie server_hostname:
            sslcontext.check_hostname = Nieprawda
    inaczej:
        # Fallback dla Python 3.3.
        sslcontext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        sslcontext.options |= ssl.OP_NO_SSLv2
        sslcontext.options |= ssl.OP_NO_SSLv3
        sslcontext.set_default_verify_paths()
        sslcontext.verify_mode = ssl.CERT_REQUIRED
    zwróć sslcontext


def _is_sslproto_available():
    zwróć hasattr(ssl, "MemoryBIO")


# States of an _SSLPipe.
_UNWRAPPED = "UNWRAPPED"
_DO_HANDSHAKE = "DO_HANDSHAKE"
_WRAPPED = "WRAPPED"
_SHUTDOWN = "SHUTDOWN"


klasa _SSLPipe(object):
    """An SSL "Pipe".

    An SSL pipe allows you to communicate przy an SSL/TLS protocol instance
    through memory buffers. It can be used to implement a security layer dla an
    existing connection where you don't have access to the connection's file
    descriptor, albo dla some reason you don't want to use it.

    An SSL pipe can be w "wrapped" oraz "unwrapped" mode. In unwrapped mode,
    data jest dalejed through untransformed. In wrapped mode, application level
    data jest encrypted to SSL record level data oraz vice versa. The SSL record
    level jest the lowest level w the SSL protocol suite oraz jest what travels
    as-is over the wire.

    An SslPipe initially jest w "unwrapped" mode. To start SSL, call
    do_handshake(). To shutdown SSL again, call unwrap().
    """

    max_size = 256 * 1024   # Buffer size dalejed to read()

    def __init__(self, context, server_side, server_hostname=Nic):
        """
        The *context* argument specifies the ssl.SSLContext to use.

        The *server_side* argument indicates whether this jest a server side albo
        client side transport.

        The optional *server_hostname* argument can be used to specify the
        hostname you are connecting to. You may only specify this parameter if
        the _ssl module supports Server Name Indication (SNI).
        """
        self._context = context
        self._server_side = server_side
        self._server_hostname = server_hostname
        self._state = _UNWRAPPED
        self._incoming = ssl.MemoryBIO()
        self._outgoing = ssl.MemoryBIO()
        self._sslobj = Nic
        self._need_ssldata = Nieprawda
        self._handshake_cb = Nic
        self._shutdown_cb = Nic

    @property
    def context(self):
        """The SSL context dalejed to the constructor."""
        zwróć self._context

    @property
    def ssl_object(self):
        """The internal ssl.SSLObject instance.

        Return Nic jeżeli the pipe jest nie wrapped.
        """
        zwróć self._sslobj

    @property
    def need_ssldata(self):
        """Whether more record level data jest needed to complete a handshake
        that jest currently w progress."""
        zwróć self._need_ssldata

    @property
    def wrapped(self):
        """
        Whether a security layer jest currently w effect.

        Return Nieprawda during handshake.
        """
        zwróć self._state == _WRAPPED

    def do_handshake(self, callback=Nic):
        """Start the SSL handshake.

        Return a list of ssldata. A ssldata element jest a list of buffers

        The optional *callback* argument can be used to install a callback that
        will be called when the handshake jest complete. The callback will be
        called przy Nic jeżeli successful, inaczej an exception instance.
        """
        jeżeli self._state != _UNWRAPPED:
            podnieś RuntimeError('handshake w progress albo completed')
        self._sslobj = self._context.wrap_bio(
            self._incoming, self._outgoing,
            server_side=self._server_side,
            server_hostname=self._server_hostname)
        self._state = _DO_HANDSHAKE
        self._handshake_cb = callback
        ssldata, appdata = self.feed_ssldata(b'', only_handshake=Prawda)
        assert len(appdata) == 0
        zwróć ssldata

    def shutdown(self, callback=Nic):
        """Start the SSL shutdown sequence.

        Return a list of ssldata. A ssldata element jest a list of buffers

        The optional *callback* argument can be used to install a callback that
        will be called when the shutdown jest complete. The callback will be
        called without arguments.
        """
        jeżeli self._state == _UNWRAPPED:
            podnieś RuntimeError('no security layer present')
        jeżeli self._state == _SHUTDOWN:
            podnieś RuntimeError('shutdown w progress')
        assert self._state w (_WRAPPED, _DO_HANDSHAKE)
        self._state = _SHUTDOWN
        self._shutdown_cb = callback
        ssldata, appdata = self.feed_ssldata(b'')
        assert appdata == [] albo appdata == [b'']
        zwróć ssldata

    def feed_eof(self):
        """Send a potentially "ragged" EOF.

        This method will podnieś an SSL_ERROR_EOF exception jeżeli the EOF jest
        unexpected.
        """
        self._incoming.write_eof()
        ssldata, appdata = self.feed_ssldata(b'')
        assert appdata == [] albo appdata == [b'']

    def feed_ssldata(self, data, only_handshake=Nieprawda):
        """Feed SSL record level data into the pipe.

        The data must be a bytes instance. It jest OK to send an empty bytes
        instance. This can be used to get ssldata dla a handshake initiated by
        this endpoint.

        Return a (ssldata, appdata) tuple. The ssldata element jest a list of
        buffers containing SSL data that needs to be sent to the remote SSL.

        The appdata element jest a list of buffers containing plaintext data that
        needs to be forwarded to the application. The appdata list may contain
        an empty buffer indicating an SSL "close_notify" alert. This alert must
        be acknowledged by calling shutdown().
        """
        jeżeli self._state == _UNWRAPPED:
            # If unwrapped, dalej plaintext data straight through.
            jeżeli data:
                appdata = [data]
            inaczej:
                appdata = []
            zwróć ([], appdata)

        self._need_ssldata = Nieprawda
        jeżeli data:
            self._incoming.write(data)

        ssldata = []
        appdata = []
        spróbuj:
            jeżeli self._state == _DO_HANDSHAKE:
                # Call do_handshake() until it doesn't podnieś anymore.
                self._sslobj.do_handshake()
                self._state = _WRAPPED
                jeżeli self._handshake_cb:
                    self._handshake_cb(Nic)
                jeżeli only_handshake:
                    zwróć (ssldata, appdata)
                # Handshake done: execute the wrapped block

            jeżeli self._state == _WRAPPED:
                # Main state: read data z SSL until close_notify
                dopóki Prawda:
                    chunk = self._sslobj.read(self.max_size)
                    appdata.append(chunk)
                    jeżeli nie chunk:  # close_notify
                        przerwij

            albo_inaczej self._state == _SHUTDOWN:
                # Call shutdown() until it doesn't podnieś anymore.
                self._sslobj.unwrap()
                self._sslobj = Nic
                self._state = _UNWRAPPED
                jeżeli self._shutdown_cb:
                    self._shutdown_cb()

            albo_inaczej self._state == _UNWRAPPED:
                # Drain possible plaintext data after close_notify.
                appdata.append(self._incoming.read())
        wyjąwszy (ssl.SSLError, ssl.CertificateError) jako exc:
            jeżeli getattr(exc, 'errno', Nic) nie w (
                    ssl.SSL_ERROR_WANT_READ, ssl.SSL_ERROR_WANT_WRITE,
                    ssl.SSL_ERROR_SYSCALL):
                jeżeli self._state == _DO_HANDSHAKE oraz self._handshake_cb:
                    self._handshake_cb(exc)
                podnieś
            self._need_ssldata = (exc.errno == ssl.SSL_ERROR_WANT_READ)

        # Check dla record level data that needs to be sent back.
        # Happens dla the initial handshake oraz renegotiations.
        jeżeli self._outgoing.pending:
            ssldata.append(self._outgoing.read())
        zwróć (ssldata, appdata)

    def feed_appdata(self, data, offset=0):
        """Feed plaintext data into the pipe.

        Return an (ssldata, offset) tuple. The ssldata element jest a list of
        buffers containing record level data that needs to be sent to the
        remote SSL instance. The offset jest the number of plaintext bytes that
        were processed, which may be less than the length of data.

        NOTE: In case of short writes, this call MUST be retried przy the SAME
        buffer dalejed into the *data* argument (i.e. the id() must be the
        same). This jest an OpenSSL requirement. A further particularity jest that
        a short write will always have offset == 0, because the _ssl module
        does nie enable partial writes. And even though the offset jest zero,
        there will still be encrypted data w ssldata.
        """
        assert 0 <= offset <= len(data)
        jeżeli self._state == _UNWRAPPED:
            # dalej through data w unwrapped mode
            jeżeli offset < len(data):
                ssldata = [data[offset:]]
            inaczej:
                ssldata = []
            zwróć (ssldata, len(data))

        ssldata = []
        view = memoryview(data)
        dopóki Prawda:
            self._need_ssldata = Nieprawda
            spróbuj:
                jeżeli offset < len(view):
                    offset += self._sslobj.write(view[offset:])
            wyjąwszy ssl.SSLError jako exc:
                # It jest nie allowed to call write() after unwrap() until the
                # close_notify jest acknowledged. We zwróć the condition to the
                # caller jako a short write.
                jeżeli exc.reason == 'PROTOCOL_IS_SHUTDOWN':
                    exc.errno = ssl.SSL_ERROR_WANT_READ
                jeżeli exc.errno nie w (ssl.SSL_ERROR_WANT_READ,
                                     ssl.SSL_ERROR_WANT_WRITE,
                                     ssl.SSL_ERROR_SYSCALL):
                    podnieś
                self._need_ssldata = (exc.errno == ssl.SSL_ERROR_WANT_READ)

            # See jeżeli there's any record level data back dla us.
            jeżeli self._outgoing.pending:
                ssldata.append(self._outgoing.read())
            jeżeli offset == len(view) albo self._need_ssldata:
                przerwij
        zwróć (ssldata, offset)


klasa _SSLProtocolTransport(transports._FlowControlMixin,
                            transports.Transport):

    def __init__(self, loop, ssl_protocol, app_protocol):
        self._loop = loop
        self._ssl_protocol = ssl_protocol
        self._app_protocol = app_protocol
        self._closed = Nieprawda

    def get_extra_info(self, name, default=Nic):
        """Get optional transport information."""
        zwróć self._ssl_protocol._get_extra_info(name, default)

    def close(self):
        """Close the transport.

        Buffered data will be flushed asynchronously.  No more data
        will be received.  After all buffered data jest flushed, the
        protocol's connection_lost() method will (eventually) called
        przy Nic jako its argument.
        """
        self._closed = Prawda
        self._ssl_protocol._start_shutdown()

    # On Python 3.3 oraz older, objects przy a destructor part of a reference
    # cycle are never destroyed. It's nie more the case on Python 3.4 thanks
    # to the PEP 442.
    jeżeli compat.PY34:
        def __del__(self):
            jeżeli nie self._closed:
                warnings.warn("unclosed transport %r" % self, ResourceWarning)
                self.close()

    def pause_reading(self):
        """Pause the receiving end.

        No data will be dalejed to the protocol's data_received()
        method until resume_reading() jest called.
        """
        self._ssl_protocol._transport.pause_reading()

    def resume_reading(self):
        """Resume the receiving end.

        Data received will once again be dalejed to the protocol's
        data_received() method.
        """
        self._ssl_protocol._transport.resume_reading()

    def set_write_buffer_limits(self, high=Nic, low=Nic):
        """Set the high- oraz low-water limits dla write flow control.

        These two values control when to call the protocol's
        pause_writing() oraz resume_writing() methods.  If specified,
        the low-water limit must be less than albo equal to the
        high-water limit.  Neither value can be negative.

        The defaults are implementation-specific.  If only the
        high-water limit jest given, the low-water limit defaults to a
        implementation-specific value less than albo equal to the
        high-water limit.  Setting high to zero forces low to zero as
        well, oraz causes pause_writing() to be called whenever the
        buffer becomes non-empty.  Setting low to zero causes
        resume_writing() to be called only once the buffer jest empty.
        Use of zero dla either limit jest generally sub-optimal jako it
        reduces opportunities dla doing I/O oraz computation
        concurrently.
        """
        self._ssl_protocol._transport.set_write_buffer_limits(high, low)

    def get_write_buffer_size(self):
        """Return the current size of the write buffer."""
        zwróć self._ssl_protocol._transport.get_write_buffer_size()

    def write(self, data):
        """Write some data bytes to the transport.

        This does nie block; it buffers the data oraz arranges dla it
        to be sent out asynchronously.
        """
        jeżeli nie isinstance(data, (bytes, bytearray, memoryview)):
            podnieś TypeError("data: expecting a bytes-like instance, got {!r}"
                                .format(type(data).__name__))
        jeżeli nie data:
            zwróć
        self._ssl_protocol._write_appdata(data)

    def can_write_eof(self):
        """Return Prawda jeżeli this transport supports write_eof(), Nieprawda jeżeli not."""
        zwróć Nieprawda

    def abort(self):
        """Close the transport immediately.

        Buffered data will be lost.  No more data will be received.
        The protocol's connection_lost() method will (eventually) be
        called przy Nic jako its argument.
        """
        self._ssl_protocol._abort()


klasa SSLProtocol(protocols.Protocol):
    """SSL protocol.

    Implementation of SSL on top of a socket using incoming oraz outgoing
    buffers which are ssl.MemoryBIO objects.
    """

    def __init__(self, loop, app_protocol, sslcontext, waiter,
                 server_side=Nieprawda, server_hostname=Nic):
        jeżeli ssl jest Nic:
            podnieś RuntimeError('stdlib ssl module nie available')

        jeżeli nie sslcontext:
            sslcontext = _create_transport_context(server_side, server_hostname)

        self._server_side = server_side
        jeżeli server_hostname oraz nie server_side:
            self._server_hostname = server_hostname
        inaczej:
            self._server_hostname = Nic
        self._sslcontext = sslcontext
        # SSL-specific extra info. More info are set when the handshake
        # completes.
        self._extra = dict(sslcontext=sslcontext)

        # App data write buffering
        self._write_backlog = collections.deque()
        self._write_buffer_size = 0

        self._waiter = waiter
        self._loop = loop
        self._app_protocol = app_protocol
        self._app_transport = _SSLProtocolTransport(self._loop,
                                                    self, self._app_protocol)
        self._sslpipe = Nic
        self._session_established = Nieprawda
        self._in_handshake = Nieprawda
        self._in_shutdown = Nieprawda
        self._transport = Nic

    def _wakeup_waiter(self, exc=Nic):
        jeżeli self._waiter jest Nic:
            zwróć
        jeżeli nie self._waiter.cancelled():
            jeżeli exc jest nie Nic:
                self._waiter.set_exception(exc)
            inaczej:
                self._waiter.set_result(Nic)
        self._waiter = Nic

    def connection_made(self, transport):
        """Called when the low-level connection jest made.

        Start the SSL handshake.
        """
        self._transport = transport
        self._sslpipe = _SSLPipe(self._sslcontext,
                                 self._server_side,
                                 self._server_hostname)
        self._start_handshake()

    def connection_lost(self, exc):
        """Called when the low-level connection jest lost albo closed.

        The argument jest an exception object albo Nic (the latter
        meaning a regular EOF jest received albo the connection was
        aborted albo closed).
        """
        jeżeli self._session_established:
            self._session_established = Nieprawda
            self._loop.call_soon(self._app_protocol.connection_lost, exc)
        self._transport = Nic
        self._app_transport = Nic

    def pause_writing(self):
        """Called when the low-level transport's buffer goes over
        the high-water mark.
        """
        self._app_protocol.pause_writing()

    def resume_writing(self):
        """Called when the low-level transport's buffer drains below
        the low-water mark.
        """
        self._app_protocol.resume_writing()

    def data_received(self, data):
        """Called when some SSL data jest received.

        The argument jest a bytes object.
        """
        spróbuj:
            ssldata, appdata = self._sslpipe.feed_ssldata(data)
        wyjąwszy ssl.SSLError jako e:
            jeżeli self._loop.get_debug():
                logger.warning('%r: SSL error %s (reason %s)',
                               self, e.errno, e.reason)
            self._abort()
            zwróć

        dla chunk w ssldata:
            self._transport.write(chunk)

        dla chunk w appdata:
            jeżeli chunk:
                self._app_protocol.data_received(chunk)
            inaczej:
                self._start_shutdown()
                przerwij

    def eof_received(self):
        """Called when the other end of the low-level stream
        jest half-closed.

        If this returns a false value (including Nic), the transport
        will close itself.  If it returns a true value, closing the
        transport jest up to the protocol.
        """
        spróbuj:
            jeżeli self._loop.get_debug():
                logger.debug("%r received EOF", self)

            self._wakeup_waiter(ConnectionResetError)

            jeżeli nie self._in_handshake:
                keep_open = self._app_protocol.eof_received()
                jeżeli keep_open:
                    logger.warning('returning true z eof_received() '
                                   'has no effect when using ssl')
        w_końcu:
            self._transport.close()

    def _get_extra_info(self, name, default=Nic):
        jeżeli name w self._extra:
            zwróć self._extra[name]
        inaczej:
            zwróć self._transport.get_extra_info(name, default)

    def _start_shutdown(self):
        jeżeli self._in_shutdown:
            zwróć
        self._in_shutdown = Prawda
        self._write_appdata(b'')

    def _write_appdata(self, data):
        self._write_backlog.append((data, 0))
        self._write_buffer_size += len(data)
        self._process_write_backlog()

    def _start_handshake(self):
        jeżeli self._loop.get_debug():
            logger.debug("%r starts SSL handshake", self)
            self._handshake_start_time = self._loop.time()
        inaczej:
            self._handshake_start_time = Nic
        self._in_handshake = Prawda
        # (b'', 1) jest a special value w _process_write_backlog() to do
        # the SSL handshake
        self._write_backlog.append((b'', 1))
        self._loop.call_soon(self._process_write_backlog)

    def _on_handshake_complete(self, handshake_exc):
        self._in_handshake = Nieprawda

        sslobj = self._sslpipe.ssl_object
        spróbuj:
            jeżeli handshake_exc jest nie Nic:
                podnieś handshake_exc

            peercert = sslobj.getpeercert()
            jeżeli nie hasattr(self._sslcontext, 'check_hostname'):
                # Verify hostname jeżeli requested, Python 3.4+ uses check_hostname
                # oraz checks the hostname w do_handshake()
                jeżeli (self._server_hostname
                oraz self._sslcontext.verify_mode != ssl.CERT_NONE):
                    ssl.match_hostname(peercert, self._server_hostname)
        wyjąwszy BaseException jako exc:
            jeżeli self._loop.get_debug():
                jeżeli isinstance(exc, ssl.CertificateError):
                    logger.warning("%r: SSL handshake failed "
                                   "on verifying the certificate",
                                   self, exc_info=Prawda)
                inaczej:
                    logger.warning("%r: SSL handshake failed",
                                   self, exc_info=Prawda)
            self._transport.close()
            jeżeli isinstance(exc, Exception):
                self._wakeup_waiter(exc)
                zwróć
            inaczej:
                podnieś

        jeżeli self._loop.get_debug():
            dt = self._loop.time() - self._handshake_start_time
            logger.debug("%r: SSL handshake took %.1f ms", self, dt * 1e3)

        # Add extra info that becomes available after handshake.
        self._extra.update(peercert=peercert,
                           cipher=sslobj.cipher(),
                           compression=sslobj.compression(),
                           )
        self._app_protocol.connection_made(self._app_transport)
        self._wakeup_waiter()
        self._session_established = Prawda
        # In case transport.write() was already called. Don't call
        # immediatly _process_write_backlog(), but schedule it:
        # _on_handshake_complete() can be called indirectly from
        # _process_write_backlog(), oraz _process_write_backlog() jest nie
        # reentrant.
        self._loop.call_soon(self._process_write_backlog)

    def _process_write_backlog(self):
        # Try to make progress on the write backlog.
        jeżeli self._transport jest Nic:
            zwróć

        spróbuj:
            dla i w range(len(self._write_backlog)):
                data, offset = self._write_backlog[0]
                jeżeli data:
                    ssldata, offset = self._sslpipe.feed_appdata(data, offset)
                albo_inaczej offset:
                    ssldata = self._sslpipe.do_handshake(
                        self._on_handshake_complete)
                    offset = 1
                inaczej:
                    ssldata = self._sslpipe.shutdown(self._finalize)
                    offset = 1

                dla chunk w ssldata:
                    self._transport.write(chunk)

                jeżeli offset < len(data):
                    self._write_backlog[0] = (data, offset)
                    # A short write means that a write jest blocked on a read
                    # We need to enable reading jeżeli it jest paused!
                    assert self._sslpipe.need_ssldata
                    jeżeli self._transport._paused:
                        self._transport.resume_reading()
                    przerwij

                # An entire chunk z the backlog was processed. We can
                # delete it oraz reduce the outstanding buffer size.
                usuń self._write_backlog[0]
                self._write_buffer_size -= len(data)
        wyjąwszy BaseException jako exc:
            jeżeli self._in_handshake:
                # BaseExceptions will be re-raised w _on_handshake_complete.
                self._on_handshake_complete(exc)
            inaczej:
                self._fatal_error(exc, 'Fatal error on SSL transport')
            jeżeli nie isinstance(exc, Exception):
                # BaseException
                podnieś

    def _fatal_error(self, exc, message='Fatal error on transport'):
        # Should be called z exception handler only.
        jeżeli isinstance(exc, (BrokenPipeError, ConnectionResetError)):
            jeżeli self._loop.get_debug():
                logger.debug("%r: %s", self, message, exc_info=Prawda)
        inaczej:
            self._loop.call_exception_handler({
                'message': message,
                'exception': exc,
                'transport': self._transport,
                'protocol': self,
            })
        jeżeli self._transport:
            self._transport._force_close(exc)

    def _finalize(self):
        jeżeli self._transport jest nie Nic:
            self._transport.close()

    def _abort(self):
        jeżeli self._transport jest nie Nic:
            spróbuj:
                self._transport.abort()
            w_końcu:
                self._finalize()
