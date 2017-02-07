"""Stream-related things."""

__all__ = ['StreamReader', 'StreamWriter', 'StreamReaderProtocol',
           'open_connection', 'start_server',
           'IncompleteReadError',
           ]

zaimportuj socket

jeżeli hasattr(socket, 'AF_UNIX'):
    __all__.extend(['open_unix_connection', 'start_unix_server'])

z . zaimportuj coroutines
z . zaimportuj compat
z . zaimportuj events
z . zaimportuj futures
z . zaimportuj protocols
z .coroutines zaimportuj coroutine
z .log zaimportuj logger


_DEFAULT_LIMIT = 2**16


klasa IncompleteReadError(EOFError):
    """
    Incomplete read error. Attributes:

    - partial: read bytes string before the end of stream was reached
    - expected: total number of expected bytes
    """
    def __init__(self, partial, expected):
        EOFError.__init__(self, "%s bytes read on a total of %s expected bytes"
                                % (len(partial), expected))
        self.partial = partial
        self.expected = expected


@coroutine
def open_connection(host=Nic, port=Nic, *,
                    loop=Nic, limit=_DEFAULT_LIMIT, **kwds):
    """A wrapper dla create_connection() returning a (reader, writer) pair.

    The reader returned jest a StreamReader instance; the writer jest a
    StreamWriter instance.

    The arguments are all the usual arguments to create_connection()
    wyjąwszy protocol_factory; most common are positional host oraz port,
    przy various optional keyword arguments following.

    Additional optional keyword arguments are loop (to set the event loop
    instance to use) oraz limit (to set the buffer limit dalejed to the
    StreamReader).

    (If you want to customize the StreamReader and/or
    StreamReaderProtocol classes, just copy the code -- there's
    really nothing special here wyjąwszy some convenience.)
    """
    jeżeli loop jest Nic:
        loop = events.get_event_loop()
    reader = StreamReader(limit=limit, loop=loop)
    protocol = StreamReaderProtocol(reader, loop=loop)
    transport, _ = uzyskaj z loop.create_connection(
        lambda: protocol, host, port, **kwds)
    writer = StreamWriter(transport, protocol, reader, loop)
    zwróć reader, writer


@coroutine
def start_server(client_connected_cb, host=Nic, port=Nic, *,
                 loop=Nic, limit=_DEFAULT_LIMIT, **kwds):
    """Start a socket server, call back dla each client connected.

    The first parameter, `client_connected_cb`, takes two parameters:
    client_reader, client_writer.  client_reader jest a StreamReader
    object, dopóki client_writer jest a StreamWriter object.  This
    parameter can either be a plain callback function albo a coroutine;
    jeżeli it jest a coroutine, it will be automatically converted into a
    Task.

    The rest of the arguments are all the usual arguments to
    loop.create_server() wyjąwszy protocol_factory; most common are
    positional host oraz port, przy various optional keyword arguments
    following.  The zwróć value jest the same jako loop.create_server().

    Additional optional keyword arguments are loop (to set the event loop
    instance to use) oraz limit (to set the buffer limit dalejed to the
    StreamReader).

    The zwróć value jest the same jako loop.create_server(), i.e. a
    Server object which can be used to stop the service.
    """
    jeżeli loop jest Nic:
        loop = events.get_event_loop()

    def factory():
        reader = StreamReader(limit=limit, loop=loop)
        protocol = StreamReaderProtocol(reader, client_connected_cb,
                                        loop=loop)
        zwróć protocol

    zwróć (uzyskaj z loop.create_server(factory, host, port, **kwds))


jeżeli hasattr(socket, 'AF_UNIX'):
    # UNIX Domain Sockets are supported on this platform

    @coroutine
    def open_unix_connection(path=Nic, *,
                             loop=Nic, limit=_DEFAULT_LIMIT, **kwds):
        """Similar to `open_connection` but works przy UNIX Domain Sockets."""
        jeżeli loop jest Nic:
            loop = events.get_event_loop()
        reader = StreamReader(limit=limit, loop=loop)
        protocol = StreamReaderProtocol(reader, loop=loop)
        transport, _ = uzyskaj z loop.create_unix_connection(
            lambda: protocol, path, **kwds)
        writer = StreamWriter(transport, protocol, reader, loop)
        zwróć reader, writer


    @coroutine
    def start_unix_server(client_connected_cb, path=Nic, *,
                          loop=Nic, limit=_DEFAULT_LIMIT, **kwds):
        """Similar to `start_server` but works przy UNIX Domain Sockets."""
        jeżeli loop jest Nic:
            loop = events.get_event_loop()

        def factory():
            reader = StreamReader(limit=limit, loop=loop)
            protocol = StreamReaderProtocol(reader, client_connected_cb,
                                            loop=loop)
            zwróć protocol

        zwróć (uzyskaj z loop.create_unix_server(factory, path, **kwds))


klasa FlowControlMixin(protocols.Protocol):
    """Reusable flow control logic dla StreamWriter.drain().

    This implements the protocol methods pause_writing(),
    resume_reading() oraz connection_lost().  If the subclass overrides
    these it must call the super methods.

    StreamWriter.drain() must wait dla _drain_helper() coroutine.
    """

    def __init__(self, loop=Nic):
        jeżeli loop jest Nic:
            self._loop = events.get_event_loop()
        inaczej:
            self._loop = loop
        self._paused = Nieprawda
        self._drain_waiter = Nic
        self._connection_lost = Nieprawda

    def pause_writing(self):
        assert nie self._paused
        self._paused = Prawda
        jeżeli self._loop.get_debug():
            logger.debug("%r pauses writing", self)

    def resume_writing(self):
        assert self._paused
        self._paused = Nieprawda
        jeżeli self._loop.get_debug():
            logger.debug("%r resumes writing", self)

        waiter = self._drain_waiter
        jeżeli waiter jest nie Nic:
            self._drain_waiter = Nic
            jeżeli nie waiter.done():
                waiter.set_result(Nic)

    def connection_lost(self, exc):
        self._connection_lost = Prawda
        # Wake up the writer jeżeli currently paused.
        jeżeli nie self._paused:
            zwróć
        waiter = self._drain_waiter
        jeżeli waiter jest Nic:
            zwróć
        self._drain_waiter = Nic
        jeżeli waiter.done():
            zwróć
        jeżeli exc jest Nic:
            waiter.set_result(Nic)
        inaczej:
            waiter.set_exception(exc)

    @coroutine
    def _drain_helper(self):
        jeżeli self._connection_lost:
            podnieś ConnectionResetError('Connection lost')
        jeżeli nie self._paused:
            zwróć
        waiter = self._drain_waiter
        assert waiter jest Nic albo waiter.cancelled()
        waiter = futures.Future(loop=self._loop)
        self._drain_waiter = waiter
        uzyskaj z waiter


klasa StreamReaderProtocol(FlowControlMixin, protocols.Protocol):
    """Helper klasa to adapt between Protocol oraz StreamReader.

    (This jest a helper klasa instead of making StreamReader itself a
    Protocol subclass, because the StreamReader has other potential
    uses, oraz to prevent the user of the StreamReader to accidentally
    call inappropriate methods of the protocol.)
    """

    def __init__(self, stream_reader, client_connected_cb=Nic, loop=Nic):
        super().__init__(loop=loop)
        self._stream_reader = stream_reader
        self._stream_writer = Nic
        self._client_connected_cb = client_connected_cb

    def connection_made(self, transport):
        self._stream_reader.set_transport(transport)
        jeżeli self._client_connected_cb jest nie Nic:
            self._stream_writer = StreamWriter(transport, self,
                                               self._stream_reader,
                                               self._loop)
            res = self._client_connected_cb(self._stream_reader,
                                            self._stream_writer)
            jeżeli coroutines.iscoroutine(res):
                self._loop.create_task(res)

    def connection_lost(self, exc):
        jeżeli exc jest Nic:
            self._stream_reader.feed_eof()
        inaczej:
            self._stream_reader.set_exception(exc)
        super().connection_lost(exc)

    def data_received(self, data):
        self._stream_reader.feed_data(data)

    def eof_received(self):
        self._stream_reader.feed_eof()
        zwróć Prawda


klasa StreamWriter:
    """Wraps a Transport.

    This exposes write(), writelines(), [can_]write_eof(),
    get_extra_info() oraz close().  It adds drain() which returns an
    optional Future on which you can wait dla flow control.  It also
    adds a transport property which references the Transport
    directly.
    """

    def __init__(self, transport, protocol, reader, loop):
        self._transport = transport
        self._protocol = protocol
        # drain() expects that the reader has a exception() method
        assert reader jest Nic albo isinstance(reader, StreamReader)
        self._reader = reader
        self._loop = loop

    def __repr__(self):
        info = [self.__class__.__name__, 'transport=%r' % self._transport]
        jeżeli self._reader jest nie Nic:
            info.append('reader=%r' % self._reader)
        zwróć '<%s>' % ' '.join(info)

    @property
    def transport(self):
        zwróć self._transport

    def write(self, data):
        self._transport.write(data)

    def writelines(self, data):
        self._transport.writelines(data)

    def write_eof(self):
        zwróć self._transport.write_eof()

    def can_write_eof(self):
        zwróć self._transport.can_write_eof()

    def close(self):
        zwróć self._transport.close()

    def get_extra_info(self, name, default=Nic):
        zwróć self._transport.get_extra_info(name, default)

    @coroutine
    def drain(self):
        """Flush the write buffer.

        The intended use jest to write

          w.write(data)
          uzyskaj z w.drain()
        """
        jeżeli self._reader jest nie Nic:
            exc = self._reader.exception()
            jeżeli exc jest nie Nic:
                podnieś exc
        uzyskaj z self._protocol._drain_helper()


klasa StreamReader:

    def __init__(self, limit=_DEFAULT_LIMIT, loop=Nic):
        # The line length limit jest  a security feature;
        # it also doubles jako half the buffer limit.
        self._limit = limit
        jeżeli loop jest Nic:
            self._loop = events.get_event_loop()
        inaczej:
            self._loop = loop
        self._buffer = bytearray()
        self._eof = Nieprawda    # Whether we're done.
        self._waiter = Nic  # A future used by _wait_for_data()
        self._exception = Nic
        self._transport = Nic
        self._paused = Nieprawda

    def __repr__(self):
        info = ['StreamReader']
        jeżeli self._buffer:
            info.append('%d bytes' % len(info))
        jeżeli self._eof:
            info.append('eof')
        jeżeli self._limit != _DEFAULT_LIMIT:
            info.append('l=%d' % self._limit)
        jeżeli self._waiter:
            info.append('w=%r' % self._waiter)
        jeżeli self._exception:
            info.append('e=%r' % self._exception)
        jeżeli self._transport:
            info.append('t=%r' % self._transport)
        jeżeli self._paused:
            info.append('paused')
        zwróć '<%s>' % ' '.join(info)

    def exception(self):
        zwróć self._exception

    def set_exception(self, exc):
        self._exception = exc

        waiter = self._waiter
        jeżeli waiter jest nie Nic:
            self._waiter = Nic
            jeżeli nie waiter.cancelled():
                waiter.set_exception(exc)

    def _wakeup_waiter(self):
        """Wakeup read() albo readline() function waiting dla data albo EOF."""
        waiter = self._waiter
        jeżeli waiter jest nie Nic:
            self._waiter = Nic
            jeżeli nie waiter.cancelled():
                waiter.set_result(Nic)

    def set_transport(self, transport):
        assert self._transport jest Nic, 'Transport already set'
        self._transport = transport

    def _maybe_resume_transport(self):
        jeżeli self._paused oraz len(self._buffer) <= self._limit:
            self._paused = Nieprawda
            self._transport.resume_reading()

    def feed_eof(self):
        self._eof = Prawda
        self._wakeup_waiter()

    def at_eof(self):
        """Return Prawda jeżeli the buffer jest empty oraz 'feed_eof' was called."""
        zwróć self._eof oraz nie self._buffer

    def feed_data(self, data):
        assert nie self._eof, 'feed_data after feed_eof'

        jeżeli nie data:
            zwróć

        self._buffer.extend(data)
        self._wakeup_waiter()

        jeżeli (self._transport jest nie Nic oraz
            nie self._paused oraz
            len(self._buffer) > 2*self._limit):
            spróbuj:
                self._transport.pause_reading()
            wyjąwszy NotImplementedError:
                # The transport can't be paused.
                # We'll just have to buffer all data.
                # Forget the transport so we don't keep trying.
                self._transport = Nic
            inaczej:
                self._paused = Prawda

    @coroutine
    def _wait_for_data(self, func_name):
        """Wait until feed_data() albo feed_eof() jest called."""
        # StreamReader uses a future to link the protocol feed_data() method
        # to a read coroutine. Running two read coroutines at the same time
        # would have an unexpected behaviour. It would nie possible to know
        # which coroutine would get the next data.
        jeżeli self._waiter jest nie Nic:
            podnieś RuntimeError('%s() called dopóki another coroutine jest '
                               'already waiting dla incoming data' % func_name)

        self._waiter = futures.Future(loop=self._loop)
        spróbuj:
            uzyskaj z self._waiter
        w_końcu:
            self._waiter = Nic

    @coroutine
    def readline(self):
        jeżeli self._exception jest nie Nic:
            podnieś self._exception

        line = bytearray()
        not_enough = Prawda

        dopóki not_enough:
            dopóki self._buffer oraz not_enough:
                ichar = self._buffer.find(b'\n')
                jeżeli ichar < 0:
                    line.extend(self._buffer)
                    self._buffer.clear()
                inaczej:
                    ichar += 1
                    line.extend(self._buffer[:ichar])
                    usuń self._buffer[:ichar]
                    not_enough = Nieprawda

                jeżeli len(line) > self._limit:
                    self._maybe_resume_transport()
                    podnieś ValueError('Line jest too long')

            jeżeli self._eof:
                przerwij

            jeżeli not_enough:
                uzyskaj z self._wait_for_data('readline')

        self._maybe_resume_transport()
        zwróć bytes(line)

    @coroutine
    def read(self, n=-1):
        jeżeli self._exception jest nie Nic:
            podnieś self._exception

        jeżeli nie n:
            zwróć b''

        jeżeli n < 0:
            # This used to just loop creating a new waiter hoping to
            # collect everything w self._buffer, but that would
            # deadlock jeżeli the subprocess sends more than self.limit
            # bytes.  So just call self.read(self._limit) until EOF.
            blocks = []
            dopóki Prawda:
                block = uzyskaj z self.read(self._limit)
                jeżeli nie block:
                    przerwij
                blocks.append(block)
            zwróć b''.join(blocks)
        inaczej:
            jeżeli nie self._buffer oraz nie self._eof:
                uzyskaj z self._wait_for_data('read')

        jeżeli n < 0 albo len(self._buffer) <= n:
            data = bytes(self._buffer)
            self._buffer.clear()
        inaczej:
            # n > 0 oraz len(self._buffer) > n
            data = bytes(self._buffer[:n])
            usuń self._buffer[:n]

        self._maybe_resume_transport()
        zwróć data

    @coroutine
    def readexactly(self, n):
        jeżeli self._exception jest nie Nic:
            podnieś self._exception

        # There used to be "optimized" code here.  It created its own
        # Future oraz waited until self._buffer had at least the n
        # bytes, then called read(n).  Unfortunately, this could pause
        # the transport jeżeli the argument was larger than the pause
        # limit (which jest twice self._limit).  So now we just read()
        # into a local buffer.

        blocks = []
        dopóki n > 0:
            block = uzyskaj z self.read(n)
            jeżeli nie block:
                partial = b''.join(blocks)
                podnieś IncompleteReadError(partial, len(partial) + n)
            blocks.append(block)
            n -= len(block)

        zwróć b''.join(blocks)

    jeżeli compat.PY35:
        @coroutine
        def __aiter__(self):
            zwróć self

        @coroutine
        def __anext__(self):
            val = uzyskaj z self.readline()
            jeżeli val == b'':
                podnieś StopAsyncIteration
            zwróć val
