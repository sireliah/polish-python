"""Generic socket server classes.

This module tries to capture the various aspects of defining a server:

For socket-based servers:

- address family:
        - AF_INET{,6}: IP (Internet Protocol) sockets (default)
        - AF_UNIX: Unix domain sockets
        - others, e.g. AF_DECNET are conceivable (see <socket.h>
- socket type:
        - SOCK_STREAM (reliable stream, e.g. TCP)
        - SOCK_DGRAM (datagrams, e.g. UDP)

For request-based servers (including socket-based):

- client address verification before further looking at the request
        (This jest actually a hook dla any processing that needs to look
         at the request before anything inaczej, e.g. logging)
- how to handle multiple requests:
        - synchronous (one request jest handled at a time)
        - forking (each request jest handled by a new process)
        - threading (each request jest handled by a new thread)

The classes w this module favor the server type that jest simplest to
write: a synchronous TCP/IP server.  This jest bad klasa design, but
save some typing.  (There's also the issue that a deep klasa hierarchy
slows down method lookups.)

There are five classes w an inheritance diagram, four of which represent
synchronous servers of four types:

        +------------+
        | BaseServer |
        +------------+
              |
              v
        +-----------+        +------------------+
        | TCPServer |------->| UnixStreamServer |
        +-----------+        +------------------+
              |
              v
        +-----------+        +--------------------+
        | UDPServer |------->| UnixDatagramServer |
        +-----------+        +--------------------+

Note that UnixDatagramServer derives z UDPServer, nie from
UnixStreamServer -- the only difference between an IP oraz a Unix
stream server jest the address family, which jest simply repeated w both
unix server classes.

Forking oraz threading versions of each type of server can be created
using the ForkingMixIn oraz ThreadingMixIn mix-in classes.  For
instance, a threading UDP server klasa jest created jako follows:

        klasa ThreadingUDPServer(ThreadingMixIn, UDPServer): dalej

The Mix-in klasa must come first, since it overrides a method defined
in UDPServer! Setting the various member variables also changes
the behavior of the underlying server mechanism.

To implement a service, you must derive a klasa from
BaseRequestHandler oraz redefine its handle() method.  You can then run
various versions of the service by combining one of the server classes
przy your request handler class.

The request handler klasa must be different dla datagram albo stream
services.  This can be hidden by using the request handler
subclasses StreamRequestHandler albo DatagramRequestHandler.

Of course, you still have to use your head!

For instance, it makes no sense to use a forking server jeżeli the service
contains state w memory that can be modified by requests (since the
modifications w the child process would never reach the initial state
kept w the parent process oraz dalejed to each child).  In this case,
you can use a threading server, but you will probably have to use
locks to avoid two requests that come w nearly simultaneous to apply
conflicting changes to the server state.

On the other hand, jeżeli you are building e.g. an HTTP server, where all
data jest stored externally (e.g. w the file system), a synchronous
klasa will essentially render the service "deaf" dopóki one request jest
being handled -- which may be dla a very long time jeżeli a client jest slow
to read all the data it has requested.  Here a threading albo forking
server jest appropriate.

In some cases, it may be appropriate to process part of a request
synchronously, but to finish processing w a forked child depending on
the request data.  This can be implemented by using a synchronous
server oraz doing an explicit fork w the request handler class
handle() method.

Another approach to handling multiple simultaneous requests w an
environment that supports neither threads nor fork (or where these are
too expensive albo inappropriate dla the service) jest to maintain an
explicit table of partially finished requests oraz to use a selector to
decide which request to work on next (or whether to handle a new
incoming request).  This jest particularly important dla stream services
where each client can potentially be connected dla a long time (if
threads albo subprocesses cannot be used).

Future work:
- Standard classes dla Sun RPC (which uses either UDP albo TCP)
- Standard mix-in classes to implement various authentication
  oraz encryption schemes

XXX Open problems:
- What to do przy out-of-band data?

BaseServer:
- split generic "request" functionality out into BaseServer class.
  Copyright (C) 2000  Luke Kenneth Casson Leighton <lkcl@samba.org>

  example: read entries z a SQL database (requires overriding
  get_request() to zwróć a table entry z the database).
  entry jest processed by a RequestHandlerClass.

"""

# Author of the BaseServer patch: Luke Kenneth Casson Leighton

# XXX Warning!
# There jest a test suite dla this module, but it cannot be run by the
# standard regression test.
# To run it manually, run Lib/test/test_socketserver.py.

__version__ = "0.4"


zaimportuj socket
zaimportuj selectors
zaimportuj os
zaimportuj errno
spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    zaimportuj dummy_threading jako threading
z time zaimportuj monotonic jako time

__all__ = ["BaseServer", "TCPServer", "UDPServer", "ForkingUDPServer",
           "ForkingTCPServer", "ThreadingUDPServer", "ThreadingTCPServer",
           "BaseRequestHandler", "StreamRequestHandler",
           "DatagramRequestHandler", "ThreadingMixIn", "ForkingMixIn"]
jeżeli hasattr(socket, "AF_UNIX"):
    __all__.extend(["UnixStreamServer","UnixDatagramServer",
                    "ThreadingUnixStreamServer",
                    "ThreadingUnixDatagramServer"])

# poll/select have the advantage of nie requiring any extra file descriptor,
# contrarily to epoll/kqueue (also, they require a single syscall).
jeżeli hasattr(selectors, 'PollSelector'):
    _ServerSelector = selectors.PollSelector
inaczej:
    _ServerSelector = selectors.SelectSelector


klasa BaseServer:

    """Base klasa dla server classes.

    Methods dla the caller:

    - __init__(server_address, RequestHandlerClass)
    - serve_forever(poll_interval=0.5)
    - shutdown()
    - handle_request()  # jeżeli you do nie use serve_forever()
    - fileno() -> int   # dla selector

    Methods that may be overridden:

    - server_bind()
    - server_activate()
    - get_request() -> request, client_address
    - handle_timeout()
    - verify_request(request, client_address)
    - server_close()
    - process_request(request, client_address)
    - shutdown_request(request)
    - close_request(request)
    - service_actions()
    - handle_error()

    Methods dla derived classes:

    - finish_request(request, client_address)

    Class variables that may be overridden by derived classes albo
    instances:

    - timeout
    - address_family
    - socket_type
    - allow_reuse_address

    Instance variables:

    - RequestHandlerClass
    - socket

    """

    timeout = Nic

    def __init__(self, server_address, RequestHandlerClass):
        """Constructor.  May be extended, do nie override."""
        self.server_address = server_address
        self.RequestHandlerClass = RequestHandlerClass
        self.__is_shut_down = threading.Event()
        self.__shutdown_request = Nieprawda

    def server_activate(self):
        """Called by constructor to activate the server.

        May be overridden.

        """
        dalej

    def serve_forever(self, poll_interval=0.5):
        """Handle one request at a time until shutdown.

        Polls dla shutdown every poll_interval seconds. Ignores
        self.timeout. If you need to do periodic tasks, do them w
        another thread.
        """
        self.__is_shut_down.clear()
        spróbuj:
            # XXX: Consider using another file descriptor albo connecting to the
            # socket to wake this up instead of polling. Polling reduces our
            # responsiveness to a shutdown request oraz wastes cpu at all other
            # times.
            przy _ServerSelector() jako selector:
                selector.register(self, selectors.EVENT_READ)

                dopóki nie self.__shutdown_request:
                    ready = selector.select(poll_interval)
                    jeżeli ready:
                        self._handle_request_noblock()

                    self.service_actions()
        w_końcu:
            self.__shutdown_request = Nieprawda
            self.__is_shut_down.set()

    def shutdown(self):
        """Stops the serve_forever loop.

        Blocks until the loop has finished. This must be called while
        serve_forever() jest running w another thread, albo it will
        deadlock.
        """
        self.__shutdown_request = Prawda
        self.__is_shut_down.wait()

    def service_actions(self):
        """Called by the serve_forever() loop.

        May be overridden by a subclass / Mixin to implement any code that
        needs to be run during the loop.
        """
        dalej

    # The distinction between handling, getting, processing oraz finishing a
    # request jest fairly arbitrary.  Remember:
    #
    # - handle_request() jest the top-level call.  It calls selector.select(),
    #   get_request(), verify_request() oraz process_request()
    # - get_request() jest different dla stream albo datagram sockets
    # - process_request() jest the place that may fork a new process albo create a
    #   new thread to finish the request
    # - finish_request() instantiates the request handler class; this
    #   constructor will handle the request all by itself

    def handle_request(self):
        """Handle one request, possibly blocking.

        Respects self.timeout.
        """
        # Support people who used socket.settimeout() to escape
        # handle_request before self.timeout was available.
        timeout = self.socket.gettimeout()
        jeżeli timeout jest Nic:
            timeout = self.timeout
        albo_inaczej self.timeout jest nie Nic:
            timeout = min(timeout, self.timeout)
        jeżeli timeout jest nie Nic:
            deadline = time() + timeout

        # Wait until a request arrives albo the timeout expires - the loop jest
        # necessary to accommodate early wakeups due to EINTR.
        przy _ServerSelector() jako selector:
            selector.register(self, selectors.EVENT_READ)

            dopóki Prawda:
                ready = selector.select(timeout)
                jeżeli ready:
                    zwróć self._handle_request_noblock()
                inaczej:
                    jeżeli timeout jest nie Nic:
                        timeout = deadline - time()
                        jeżeli timeout < 0:
                            zwróć self.handle_timeout()

    def _handle_request_noblock(self):
        """Handle one request, without blocking.

        I assume that selector.select() has returned that the socket jest
        readable before this function was called, so there should be no risk of
        blocking w get_request().
        """
        spróbuj:
            request, client_address = self.get_request()
        wyjąwszy OSError:
            zwróć
        jeżeli self.verify_request(request, client_address):
            spróbuj:
                self.process_request(request, client_address)
            wyjąwszy:
                self.handle_error(request, client_address)
                self.shutdown_request(request)

    def handle_timeout(self):
        """Called jeżeli no new request arrives within self.timeout.

        Overridden by ForkingMixIn.
        """
        dalej

    def verify_request(self, request, client_address):
        """Verify the request.  May be overridden.

        Return Prawda jeżeli we should proceed przy this request.

        """
        zwróć Prawda

    def process_request(self, request, client_address):
        """Call finish_request.

        Overridden by ForkingMixIn oraz ThreadingMixIn.

        """
        self.finish_request(request, client_address)
        self.shutdown_request(request)

    def server_close(self):
        """Called to clean-up the server.

        May be overridden.

        """
        dalej

    def finish_request(self, request, client_address):
        """Finish one request by instantiating RequestHandlerClass."""
        self.RequestHandlerClass(request, client_address, self)

    def shutdown_request(self, request):
        """Called to shutdown oraz close an individual request."""
        self.close_request(request)

    def close_request(self, request):
        """Called to clean up an individual request."""
        dalej

    def handle_error(self, request, client_address):
        """Handle an error gracefully.  May be overridden.

        The default jest to print a traceback oraz continue.

        """
        print('-'*40)
        print('Exception happened during processing of request from', end=' ')
        print(client_address)
        zaimportuj traceback
        traceback.print_exc() # XXX But this goes to stderr!
        print('-'*40)


klasa TCPServer(BaseServer):

    """Base klasa dla various socket-based server classes.

    Defaults to synchronous IP stream (i.e., TCP).

    Methods dla the caller:

    - __init__(server_address, RequestHandlerClass, bind_and_activate=Prawda)
    - serve_forever(poll_interval=0.5)
    - shutdown()
    - handle_request()  # jeżeli you don't use serve_forever()
    - fileno() -> int   # dla selector

    Methods that may be overridden:

    - server_bind()
    - server_activate()
    - get_request() -> request, client_address
    - handle_timeout()
    - verify_request(request, client_address)
    - process_request(request, client_address)
    - shutdown_request(request)
    - close_request(request)
    - handle_error()

    Methods dla derived classes:

    - finish_request(request, client_address)

    Class variables that may be overridden by derived classes albo
    instances:

    - timeout
    - address_family
    - socket_type
    - request_queue_size (only dla stream sockets)
    - allow_reuse_address

    Instance variables:

    - server_address
    - RequestHandlerClass
    - socket

    """

    address_family = socket.AF_INET

    socket_type = socket.SOCK_STREAM

    request_queue_size = 5

    allow_reuse_address = Nieprawda

    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=Prawda):
        """Constructor.  May be extended, do nie override."""
        BaseServer.__init__(self, server_address, RequestHandlerClass)
        self.socket = socket.socket(self.address_family,
                                    self.socket_type)
        jeżeli bind_and_activate:
            spróbuj:
                self.server_bind()
                self.server_activate()
            wyjąwszy:
                self.server_close()
                podnieś

    def server_bind(self):
        """Called by constructor to bind the socket.

        May be overridden.

        """
        jeżeli self.allow_reuse_address:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)
        self.server_address = self.socket.getsockname()

    def server_activate(self):
        """Called by constructor to activate the server.

        May be overridden.

        """
        self.socket.listen(self.request_queue_size)

    def server_close(self):
        """Called to clean-up the server.

        May be overridden.

        """
        self.socket.close()

    def fileno(self):
        """Return socket file number.

        Interface required by selector.

        """
        zwróć self.socket.fileno()

    def get_request(self):
        """Get the request oraz client address z the socket.

        May be overridden.

        """
        zwróć self.socket.accept()

    def shutdown_request(self, request):
        """Called to shutdown oraz close an individual request."""
        spróbuj:
            #explicitly shutdown.  socket.close() merely releases
            #the socket oraz waits dla GC to perform the actual close.
            request.shutdown(socket.SHUT_WR)
        wyjąwszy OSError:
            dalej #some platforms may podnieś ENOTCONN here
        self.close_request(request)

    def close_request(self, request):
        """Called to clean up an individual request."""
        request.close()


klasa UDPServer(TCPServer):

    """UDP server class."""

    allow_reuse_address = Nieprawda

    socket_type = socket.SOCK_DGRAM

    max_packet_size = 8192

    def get_request(self):
        data, client_addr = self.socket.recvfrom(self.max_packet_size)
        zwróć (data, self.socket), client_addr

    def server_activate(self):
        # No need to call listen() dla UDP.
        dalej

    def shutdown_request(self, request):
        # No need to shutdown anything.
        self.close_request(request)

    def close_request(self, request):
        # No need to close anything.
        dalej

klasa ForkingMixIn:

    """Mix-in klasa to handle each request w a new process."""

    timeout = 300
    active_children = Nic
    max_children = 40

    def collect_children(self):
        """Internal routine to wait dla children that have exited."""
        jeżeli self.active_children jest Nic:
            zwróć

        # If we're above the max number of children, wait oraz reap them until
        # we go back below threshold. Note that we use waitpid(-1) below to be
        # able to collect children w size(<defunct children>) syscalls instead
        # of size(<children>): the downside jest that this might reap children
        # which we didn't spawn, which jest why we only resort to this when we're
        # above max_children.
        dopóki len(self.active_children) >= self.max_children:
            spróbuj:
                pid, _ = os.waitpid(-1, 0)
                self.active_children.discard(pid)
            wyjąwszy ChildProcessError:
                # we don't have any children, we're done
                self.active_children.clear()
            wyjąwszy OSError:
                przerwij

        # Now reap all defunct children.
        dla pid w self.active_children.copy():
            spróbuj:
                pid, _ = os.waitpid(pid, os.WNOHANG)
                # jeżeli the child hasn't exited yet, pid will be 0 oraz ignored by
                # discard() below
                self.active_children.discard(pid)
            wyjąwszy ChildProcessError:
                # someone inaczej reaped it
                self.active_children.discard(pid)
            wyjąwszy OSError:
                dalej

    def handle_timeout(self):
        """Wait dla zombies after self.timeout seconds of inactivity.

        May be extended, do nie override.
        """
        self.collect_children()

    def service_actions(self):
        """Collect the zombie child processes regularly w the ForkingMixIn.

        service_actions jest called w the BaseServer's serve_forver loop.
        """
        self.collect_children()

    def process_request(self, request, client_address):
        """Fork a new subprocess to process the request."""
        pid = os.fork()
        jeżeli pid:
            # Parent process
            jeżeli self.active_children jest Nic:
                self.active_children = set()
            self.active_children.add(pid)
            self.close_request(request)
            zwróć
        inaczej:
            # Child process.
            # This must never return, hence os._exit()!
            spróbuj:
                self.finish_request(request, client_address)
                self.shutdown_request(request)
                os._exit(0)
            wyjąwszy:
                spróbuj:
                    self.handle_error(request, client_address)
                    self.shutdown_request(request)
                w_końcu:
                    os._exit(1)


klasa ThreadingMixIn:
    """Mix-in klasa to handle each request w a new thread."""

    # Decides how threads will act upon termination of the
    # main process
    daemon_threads = Nieprawda

    def process_request_thread(self, request, client_address):
        """Same jako w BaseServer but jako a thread.

        In addition, exception handling jest done here.

        """
        spróbuj:
            self.finish_request(request, client_address)
            self.shutdown_request(request)
        wyjąwszy:
            self.handle_error(request, client_address)
            self.shutdown_request(request)

    def process_request(self, request, client_address):
        """Start a new thread to process the request."""
        t = threading.Thread(target = self.process_request_thread,
                             args = (request, client_address))
        t.daemon = self.daemon_threads
        t.start()


klasa ForkingUDPServer(ForkingMixIn, UDPServer): dalej
klasa ForkingTCPServer(ForkingMixIn, TCPServer): dalej

klasa ThreadingUDPServer(ThreadingMixIn, UDPServer): dalej
klasa ThreadingTCPServer(ThreadingMixIn, TCPServer): dalej

jeżeli hasattr(socket, 'AF_UNIX'):

    klasa UnixStreamServer(TCPServer):
        address_family = socket.AF_UNIX

    klasa UnixDatagramServer(UDPServer):
        address_family = socket.AF_UNIX

    klasa ThreadingUnixStreamServer(ThreadingMixIn, UnixStreamServer): dalej

    klasa ThreadingUnixDatagramServer(ThreadingMixIn, UnixDatagramServer): dalej

klasa BaseRequestHandler:

    """Base klasa dla request handler classes.

    This klasa jest instantiated dla each request to be handled.  The
    constructor sets the instance variables request, client_address
    oraz server, oraz then calls the handle() method.  To implement a
    specific service, all you need to do jest to derive a klasa which
    defines a handle() method.

    The handle() method can find the request jako self.request, the
    client address jako self.client_address, oraz the server (in case it
    needs access to per-server information) jako self.server.  Since a
    separate instance jest created dla each request, the handle() method
    can define arbitrary other instance variariables.

    """

    def __init__(self, request, client_address, server):
        self.request = request
        self.client_address = client_address
        self.server = server
        self.setup()
        spróbuj:
            self.handle()
        w_końcu:
            self.finish()

    def setup(self):
        dalej

    def handle(self):
        dalej

    def finish(self):
        dalej


# The following two classes make it possible to use the same service
# klasa dla stream albo datagram servers.
# Each klasa sets up these instance variables:
# - rfile: a file object z which receives the request jest read
# - wfile: a file object to which the reply jest written
# When the handle() method returns, wfile jest flushed properly


klasa StreamRequestHandler(BaseRequestHandler):

    """Define self.rfile oraz self.wfile dla stream sockets."""

    # Default buffer sizes dla rfile, wfile.
    # We default rfile to buffered because otherwise it could be
    # really slow dla large data (a getc() call per byte); we make
    # wfile unbuffered because (a) often after a write() we want to
    # read oraz we need to flush the line; (b) big writes to unbuffered
    # files are typically optimized by stdio even when big reads
    # aren't.
    rbufsize = -1
    wbufsize = 0

    # A timeout to apply to the request socket, jeżeli nie Nic.
    timeout = Nic

    # Disable nagle algorithm dla this socket, jeżeli Prawda.
    # Use only when wbufsize != 0, to avoid small packets.
    disable_nagle_algorithm = Nieprawda

    def setup(self):
        self.connection = self.request
        jeżeli self.timeout jest nie Nic:
            self.connection.settimeout(self.timeout)
        jeżeli self.disable_nagle_algorithm:
            self.connection.setsockopt(socket.IPPROTO_TCP,
                                       socket.TCP_NODELAY, Prawda)
        self.rfile = self.connection.makefile('rb', self.rbufsize)
        self.wfile = self.connection.makefile('wb', self.wbufsize)

    def finish(self):
        jeżeli nie self.wfile.closed:
            spróbuj:
                self.wfile.flush()
            wyjąwszy socket.error:
                # An final socket error may have occurred here, such as
                # the local error ECONNABORTED.
                dalej
        self.wfile.close()
        self.rfile.close()


klasa DatagramRequestHandler(BaseRequestHandler):

    # XXX Regrettably, I cannot get this working on Linux;
    # s.recvfrom() doesn't zwróć a meaningful client address.

    """Define self.rfile oraz self.wfile dla datagram sockets."""

    def setup(self):
        z io zaimportuj BytesIO
        self.packet, self.socket = self.request
        self.rfile = BytesIO(self.packet)
        self.wfile = BytesIO()

    def finish(self):
        self.socket.sendto(self.wfile.getvalue(), self.client_address)
