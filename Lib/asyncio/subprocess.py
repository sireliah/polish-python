__all__ = ['create_subprocess_exec', 'create_subprocess_shell']

zaimportuj subprocess

z . zaimportuj events
z . zaimportuj protocols
z . zaimportuj streams
z . zaimportuj tasks
z .coroutines zaimportuj coroutine
z .log zaimportuj logger


PIPE = subprocess.PIPE
STDOUT = subprocess.STDOUT
DEVNULL = subprocess.DEVNULL


klasa SubprocessStreamProtocol(streams.FlowControlMixin,
                               protocols.SubprocessProtocol):
    """Like StreamReaderProtocol, but dla a subprocess."""

    def __init__(self, limit, loop):
        super().__init__(loop=loop)
        self._limit = limit
        self.stdin = self.stdout = self.stderr = Nic
        self._transport = Nic

    def __repr__(self):
        info = [self.__class__.__name__]
        jeżeli self.stdin jest nie Nic:
            info.append('stdin=%r' % self.stdin)
        jeżeli self.stdout jest nie Nic:
            info.append('stdout=%r' % self.stdout)
        jeżeli self.stderr jest nie Nic:
            info.append('stderr=%r' % self.stderr)
        zwróć '<%s>' % ' '.join(info)

    def connection_made(self, transport):
        self._transport = transport

        stdout_transport = transport.get_pipe_transport(1)
        jeżeli stdout_transport jest nie Nic:
            self.stdout = streams.StreamReader(limit=self._limit,
                                               loop=self._loop)
            self.stdout.set_transport(stdout_transport)

        stderr_transport = transport.get_pipe_transport(2)
        jeżeli stderr_transport jest nie Nic:
            self.stderr = streams.StreamReader(limit=self._limit,
                                               loop=self._loop)
            self.stderr.set_transport(stderr_transport)

        stdin_transport = transport.get_pipe_transport(0)
        jeżeli stdin_transport jest nie Nic:
            self.stdin = streams.StreamWriter(stdin_transport,
                                              protocol=self,
                                              reader=Nic,
                                              loop=self._loop)

    def pipe_data_received(self, fd, data):
        jeżeli fd == 1:
            reader = self.stdout
        albo_inaczej fd == 2:
            reader = self.stderr
        inaczej:
            reader = Nic
        jeżeli reader jest nie Nic:
            reader.feed_data(data)

    def pipe_connection_lost(self, fd, exc):
        jeżeli fd == 0:
            pipe = self.stdin
            jeżeli pipe jest nie Nic:
                pipe.close()
            self.connection_lost(exc)
            zwróć
        jeżeli fd == 1:
            reader = self.stdout
        albo_inaczej fd == 2:
            reader = self.stderr
        inaczej:
            reader = Nic
        jeżeli reader != Nic:
            jeżeli exc jest Nic:
                reader.feed_eof()
            inaczej:
                reader.set_exception(exc)

    def process_exited(self):
        self._transport.close()
        self._transport = Nic


klasa Process:
    def __init__(self, transport, protocol, loop):
        self._transport = transport
        self._protocol = protocol
        self._loop = loop
        self.stdin = protocol.stdin
        self.stdout = protocol.stdout
        self.stderr = protocol.stderr
        self.pid = transport.get_pid()

    def __repr__(self):
        zwróć '<%s %s>' % (self.__class__.__name__, self.pid)

    @property
    def returncode(self):
        zwróć self._transport.get_returncode()

    @coroutine
    def wait(self):
        """Wait until the process exit oraz zwróć the process zwróć code.

        This method jest a coroutine."""
        zwróć (uzyskaj z self._transport._wait())

    def send_signal(self, signal):
        self._transport.send_signal(signal)

    def terminate(self):
        self._transport.terminate()

    def kill(self):
        self._transport.kill()

    @coroutine
    def _feed_stdin(self, input):
        debug = self._loop.get_debug()
        self.stdin.write(input)
        jeżeli debug:
            logger.debug('%r communicate: feed stdin (%s bytes)',
                        self, len(input))
        spróbuj:
            uzyskaj z self.stdin.drain()
        wyjąwszy (BrokenPipeError, ConnectionResetError) jako exc:
            # communicate() ignores BrokenPipeError oraz ConnectionResetError
            jeżeli debug:
                logger.debug('%r communicate: stdin got %r', self, exc)

        jeżeli debug:
            logger.debug('%r communicate: close stdin', self)
        self.stdin.close()

    @coroutine
    def _noop(self):
        zwróć Nic

    @coroutine
    def _read_stream(self, fd):
        transport = self._transport.get_pipe_transport(fd)
        jeżeli fd == 2:
            stream = self.stderr
        inaczej:
            assert fd == 1
            stream = self.stdout
        jeżeli self._loop.get_debug():
            name = 'stdout' jeżeli fd == 1 inaczej 'stderr'
            logger.debug('%r communicate: read %s', self, name)
        output = uzyskaj z stream.read()
        jeżeli self._loop.get_debug():
            name = 'stdout' jeżeli fd == 1 inaczej 'stderr'
            logger.debug('%r communicate: close %s', self, name)
        transport.close()
        zwróć output

    @coroutine
    def communicate(self, input=Nic):
        jeżeli input:
            stdin = self._feed_stdin(input)
        inaczej:
            stdin = self._noop()
        jeżeli self.stdout jest nie Nic:
            stdout = self._read_stream(1)
        inaczej:
            stdout = self._noop()
        jeżeli self.stderr jest nie Nic:
            stderr = self._read_stream(2)
        inaczej:
            stderr = self._noop()
        stdin, stdout, stderr = uzyskaj z tasks.gather(stdin, stdout, stderr,
                                                        loop=self._loop)
        uzyskaj z self.wait()
        zwróć (stdout, stderr)


@coroutine
def create_subprocess_shell(cmd, stdin=Nic, stdout=Nic, stderr=Nic,
                            loop=Nic, limit=streams._DEFAULT_LIMIT, **kwds):
    jeżeli loop jest Nic:
        loop = events.get_event_loop()
    protocol_factory = lambda: SubprocessStreamProtocol(limit=limit,
                                                        loop=loop)
    transport, protocol = uzyskaj z loop.subprocess_shell(
                                            protocol_factory,
                                            cmd, stdin=stdin, stdout=stdout,
                                            stderr=stderr, **kwds)
    zwróć Process(transport, protocol, loop)

@coroutine
def create_subprocess_exec(program, *args, stdin=Nic, stdout=Nic,
                           stderr=Nic, loop=Nic,
                           limit=streams._DEFAULT_LIMIT, **kwds):
    jeżeli loop jest Nic:
        loop = events.get_event_loop()
    protocol_factory = lambda: SubprocessStreamProtocol(limit=limit,
                                                        loop=loop)
    transport, protocol = uzyskaj z loop.subprocess_exec(
                                            protocol_factory,
                                            program, *args,
                                            stdin=stdin, stdout=stdout,
                                            stderr=stderr, **kwds)
    zwróć Process(transport, protocol, loop)
