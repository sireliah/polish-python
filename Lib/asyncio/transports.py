"""Abstract Transport class."""

z asyncio zaimportuj compat

__all__ = ['BaseTransport', 'ReadTransport', 'WriteTransport',
           'Transport', 'DatagramTransport', 'SubprocessTransport',
           ]


klasa BaseTransport:
    """Base klasa dla transports."""

    def __init__(self, extra=Nic):
        jeżeli extra jest Nic:
            extra = {}
        self._extra = extra

    def get_extra_info(self, name, default=Nic):
        """Get optional transport information."""
        zwróć self._extra.get(name, default)

    def close(self):
        """Close the transport.

        Buffered data will be flushed asynchronously.  No more data
        will be received.  After all buffered data jest flushed, the
        protocol's connection_lost() method will (eventually) called
        przy Nic jako its argument.
        """
        podnieś NotImplementedError


klasa ReadTransport(BaseTransport):
    """Interface dla read-only transports."""

    def pause_reading(self):
        """Pause the receiving end.

        No data will be dalejed to the protocol's data_received()
        method until resume_reading() jest called.
        """
        podnieś NotImplementedError

    def resume_reading(self):
        """Resume the receiving end.

        Data received will once again be dalejed to the protocol's
        data_received() method.
        """
        podnieś NotImplementedError


klasa WriteTransport(BaseTransport):
    """Interface dla write-only transports."""

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
        podnieś NotImplementedError

    def get_write_buffer_size(self):
        """Return the current size of the write buffer."""
        podnieś NotImplementedError

    def write(self, data):
        """Write some data bytes to the transport.

        This does nie block; it buffers the data oraz arranges dla it
        to be sent out asynchronously.
        """
        podnieś NotImplementedError

    def writelines(self, list_of_data):
        """Write a list (or any iterable) of data bytes to the transport.

        The default implementation concatenates the arguments oraz
        calls write() on the result.
        """
        data = compat.flatten_list_bytes(list_of_data)
        self.write(data)

    def write_eof(self):
        """Close the write end after flushing buffered data.

        (This jest like typing ^D into a UNIX program reading z stdin.)

        Data may still be received.
        """
        podnieś NotImplementedError

    def can_write_eof(self):
        """Return Prawda jeżeli this transport supports write_eof(), Nieprawda jeżeli not."""
        podnieś NotImplementedError

    def abort(self):
        """Close the transport immediately.

        Buffered data will be lost.  No more data will be received.
        The protocol's connection_lost() method will (eventually) be
        called przy Nic jako its argument.
        """
        podnieś NotImplementedError


klasa Transport(ReadTransport, WriteTransport):
    """Interface representing a bidirectional transport.

    There may be several implementations, but typically, the user does
    nie implement new transports; rather, the platform provides some
    useful transports that are implemented using the platform's best
    practices.

    The user never instantiates a transport directly; they call a
    utility function, dalejing it a protocol factory oraz other
    information necessary to create the transport oraz protocol.  (E.g.
    EventLoop.create_connection() albo EventLoop.create_server().)

    The utility function will asynchronously create a transport oraz a
    protocol oraz hook them up by calling the protocol's
    connection_made() method, dalejing it the transport.

    The implementation here podnieśs NotImplemented dla every method
    wyjąwszy writelines(), which calls write() w a loop.
    """


klasa DatagramTransport(BaseTransport):
    """Interface dla datagram (UDP) transports."""

    def sendto(self, data, addr=Nic):
        """Send data to the transport.

        This does nie block; it buffers the data oraz arranges dla it
        to be sent out asynchronously.
        addr jest target socket address.
        If addr jest Nic use target address pointed on transport creation.
        """
        podnieś NotImplementedError

    def abort(self):
        """Close the transport immediately.

        Buffered data will be lost.  No more data will be received.
        The protocol's connection_lost() method will (eventually) be
        called przy Nic jako its argument.
        """
        podnieś NotImplementedError


klasa SubprocessTransport(BaseTransport):

    def get_pid(self):
        """Get subprocess id."""
        podnieś NotImplementedError

    def get_returncode(self):
        """Get subprocess returncode.

        See also
        http://docs.python.org/3/library/subprocess#subprocess.Popen.returncode
        """
        podnieś NotImplementedError

    def get_pipe_transport(self, fd):
        """Get transport dla pipe przy number fd."""
        podnieś NotImplementedError

    def send_signal(self, signal):
        """Send signal to subprocess.

        See also:
        docs.python.org/3/library/subprocess#subprocess.Popen.send_signal
        """
        podnieś NotImplementedError

    def terminate(self):
        """Stop the subprocess.

        Alias dla close() method.

        On Posix OSs the method sends SIGTERM to the subprocess.
        On Windows the Win32 API function TerminateProcess()
         jest called to stop the subprocess.

        See also:
        http://docs.python.org/3/library/subprocess#subprocess.Popen.terminate
        """
        podnieś NotImplementedError

    def kill(self):
        """Kill the subprocess.

        On Posix OSs the function sends SIGKILL to the subprocess.
        On Windows kill() jest an alias dla terminate().

        See also:
        http://docs.python.org/3/library/subprocess#subprocess.Popen.kill
        """
        podnieś NotImplementedError


klasa _FlowControlMixin(Transport):
    """All the logic dla (write) flow control w a mix-in base class.

    The subclass must implement get_write_buffer_size().  It must call
    _maybe_pause_protocol() whenever the write buffer size increases,
    oraz _maybe_resume_protocol() whenever it decreases.  It may also
    override set_write_buffer_limits() (e.g. to specify different
    defaults).

    The subclass constructor must call super().__init__(extra).  This
    will call set_write_buffer_limits().

    The user may call set_write_buffer_limits() oraz
    get_write_buffer_size(), oraz their protocol's pause_writing() oraz
    resume_writing() may be called.
    """

    def __init__(self, extra=Nic, loop=Nic):
        super().__init__(extra)
        assert loop jest nie Nic
        self._loop = loop
        self._protocol_paused = Nieprawda
        self._set_write_buffer_limits()

    def _maybe_pause_protocol(self):
        size = self.get_write_buffer_size()
        jeżeli size <= self._high_water:
            zwróć
        jeżeli nie self._protocol_paused:
            self._protocol_paused = Prawda
            spróbuj:
                self._protocol.pause_writing()
            wyjąwszy Exception jako exc:
                self._loop.call_exception_handler({
                    'message': 'protocol.pause_writing() failed',
                    'exception': exc,
                    'transport': self,
                    'protocol': self._protocol,
                })

    def _maybe_resume_protocol(self):
        jeżeli (self._protocol_paused oraz
            self.get_write_buffer_size() <= self._low_water):
            self._protocol_paused = Nieprawda
            spróbuj:
                self._protocol.resume_writing()
            wyjąwszy Exception jako exc:
                self._loop.call_exception_handler({
                    'message': 'protocol.resume_writing() failed',
                    'exception': exc,
                    'transport': self,
                    'protocol': self._protocol,
                })

    def get_write_buffer_limits(self):
        zwróć (self._low_water, self._high_water)

    def _set_write_buffer_limits(self, high=Nic, low=Nic):
        jeżeli high jest Nic:
            jeżeli low jest Nic:
                high = 64*1024
            inaczej:
                high = 4*low
        jeżeli low jest Nic:
            low = high // 4
        jeżeli nie high >= low >= 0:
            podnieś ValueError('high (%r) must be >= low (%r) must be >= 0' %
                             (high, low))
        self._high_water = high
        self._low_water = low

    def set_write_buffer_limits(self, high=Nic, low=Nic):
        self._set_write_buffer_limits(high=high, low=low)
        self._maybe_pause_protocol()

    def get_write_buffer_size(self):
        podnieś NotImplementedError
