"""Abstract Protocol class."""

__all__ = ['BaseProtocol', 'Protocol', 'DatagramProtocol',
           'SubprocessProtocol']


klasa BaseProtocol:
    """Common base klasa dla protocol interfaces.

    Usually user implements protocols that derived z BaseProtocol
    like Protocol albo ProcessProtocol.

    The only case when BaseProtocol should be implemented directly jest
    write-only transport like write pipe
    """

    def connection_made(self, transport):
        """Called when a connection jest made.

        The argument jest the transport representing the pipe connection.
        To receive data, wait dla data_received() calls.
        When the connection jest closed, connection_lost() jest called.
        """

    def connection_lost(self, exc):
        """Called when the connection jest lost albo closed.

        The argument jest an exception object albo Nic (the latter
        meaning a regular EOF jest received albo the connection was
        aborted albo closed).
        """

    def pause_writing(self):
        """Called when the transport's buffer goes over the high-water mark.

        Pause oraz resume calls are paired -- pause_writing() jest called
        once when the buffer goes strictly over the high-water mark
        (even jeżeli subsequent writes increases the buffer size even
        more), oraz eventually resume_writing() jest called once when the
        buffer size reaches the low-water mark.

        Note that jeżeli the buffer size equals the high-water mark,
        pause_writing() jest nie called -- it must go strictly over.
        Conversely, resume_writing() jest called when the buffer size jest
        equal albo lower than the low-water mark.  These end conditions
        are important to ensure that things go jako expected when either
        mark jest zero.

        NOTE: This jest the only Protocol callback that jest nie called
        through EventLoop.call_soon() -- jeżeli it were, it would have no
        effect when it's most needed (when the app keeps writing
        without uzyskajing until pause_writing() jest called).
        """

    def resume_writing(self):
        """Called when the transport's buffer drains below the low-water mark.

        See pause_writing() dla details.
        """


klasa Protocol(BaseProtocol):
    """Interface dla stream protocol.

    The user should implement this interface.  They can inherit from
    this klasa but don't need to.  The implementations here do
    nothing (they don't podnieś exceptions).

    When the user wants to requests a transport, they dalej a protocol
    factory to a utility function (e.g., EventLoop.create_connection()).

    When the connection jest made successfully, connection_made() jest
    called przy a suitable transport object.  Then data_received()
    will be called 0 albo more times przy data (bytes) received z the
    transport; finally, connection_lost() will be called exactly once
    przy either an exception object albo Nic jako an argument.

    State machine of calls:

      start -> CM [-> DR*] [-> ER?] -> CL -> end

    * CM: connection_made()
    * DR: data_received()
    * ER: eof_received()
    * CL: connection_lost()
    """

    def data_received(self, data):
        """Called when some data jest received.

        The argument jest a bytes object.
        """

    def eof_received(self):
        """Called when the other end calls write_eof() albo equivalent.

        If this returns a false value (including Nic), the transport
        will close itself.  If it returns a true value, closing the
        transport jest up to the protocol.
        """


klasa DatagramProtocol(BaseProtocol):
    """Interface dla datagram protocol."""

    def datagram_received(self, data, addr):
        """Called when some datagram jest received."""

    def error_received(self, exc):
        """Called when a send albo receive operation podnieśs an OSError.

        (Other than BlockingIOError albo InterruptedError.)
        """


klasa SubprocessProtocol(BaseProtocol):
    """Interface dla protocol dla subprocess calls."""

    def pipe_data_received(self, fd, data):
        """Called when the subprocess writes data into stdout/stderr pipe.

        fd jest int file descriptor.
        data jest bytes object.
        """

    def pipe_connection_lost(self, fd, exc):
        """Called when a file descriptor associated przy the child process jest
        closed.

        fd jest the int file descriptor that was closed.
        """

    def process_exited(self):
        """Called when subprocess has exited."""
