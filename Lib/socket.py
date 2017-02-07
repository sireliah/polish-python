# Wrapper module dla _socket, providing some additional facilities
# implemented w Python.

"""\
This module provides socket operations oraz some related functions.
On Unix, it supports IP (Internet Protocol) oraz Unix domain sockets.
On other systems, it only supports IP. Functions specific dla a
socket are available jako methods of the socket object.

Functions:

socket() -- create a new socket object
socketpair() -- create a pair of new socket objects [*]
fromfd() -- create a socket object z an open file descriptor [*]
fromshare() -- create a socket object z data received z socket.share() [*]
gethostname() -- zwróć the current hostname
gethostbyname() -- map a hostname to its IP number
gethostbyaddr() -- map an IP number albo hostname to DNS info
getservbyname() -- map a service name oraz a protocol name to a port number
getprotobyname() -- map a protocol name (e.g. 'tcp') to a number
ntohs(), ntohl() -- convert 16, 32 bit int z network to host byte order
htons(), htonl() -- convert 16, 32 bit int z host to network byte order
inet_aton() -- convert IP addr string (123.45.67.89) to 32-bit packed format
inet_ntoa() -- convert 32-bit packed format IP to string (123.45.67.89)
socket.getdefaulttimeout() -- get the default timeout value
socket.setdefaulttimeout() -- set the default timeout value
create_connection() -- connects to an address, przy an optional timeout oraz
                       optional source address.

 [*] nie available on all platforms!

Special objects:

SocketType -- type object dla socket objects
error -- exception podnieśd dla I/O errors
has_ipv6 -- boolean value indicating jeżeli IPv6 jest supported

IntEnum constants:

AF_INET, AF_UNIX -- socket domains (first argument to socket() call)
SOCK_STREAM, SOCK_DGRAM, SOCK_RAW -- socket types (second argument)

Integer constants:

Many other constants may be defined; these may be used w calls to
the setsockopt() oraz getsockopt() methods.
"""

zaimportuj _socket
z _socket zaimportuj *

zaimportuj os, sys, io, selectors
z enum zaimportuj IntEnum

spróbuj:
    zaimportuj errno
wyjąwszy ImportError:
    errno = Nic
EBADF = getattr(errno, 'EBADF', 9)
EAGAIN = getattr(errno, 'EAGAIN', 11)
EWOULDBLOCK = getattr(errno, 'EWOULDBLOCK', 11)

__all__ = ["fromfd", "getfqdn", "create_connection",
        "AddressFamily", "SocketKind"]
__all__.extend(os._get_exports_list(_socket))

# Set up the socket.AF_* socket.SOCK_* constants jako members of IntEnums for
# nicer string representations.
# Note that _socket only knows about the integer values. The public interface
# w this module understands the enums oraz translates them back z integers
# where needed (e.g. .family property of a socket object).

IntEnum._convert(
        'AddressFamily',
        __name__,
        lambda C: C.isupper() oraz C.startswith('AF_'))

IntEnum._convert(
        'SocketKind',
        __name__,
        lambda C: C.isupper() oraz C.startswith('SOCK_'))

_LOCALHOST    = '127.0.0.1'
_LOCALHOST_V6 = '::1'


def _intenum_converter(value, enum_klass):
    """Convert a numeric family value to an IntEnum member.

    If it's nie a known member, zwróć the numeric value itself.
    """
    spróbuj:
        zwróć enum_klass(value)
    wyjąwszy ValueError:
        zwróć value

_realsocket = socket

# WSA error codes
jeżeli sys.platform.lower().startswith("win"):
    errorTab = {}
    errorTab[10004] = "The operation was interrupted."
    errorTab[10009] = "A bad file handle was dalejed."
    errorTab[10013] = "Permission denied."
    errorTab[10014] = "A fault occurred on the network??" # WSAEFAULT
    errorTab[10022] = "An invalid operation was attempted."
    errorTab[10035] = "The socket operation would block"
    errorTab[10036] = "A blocking operation jest already w progress."
    errorTab[10048] = "The network address jest w use."
    errorTab[10054] = "The connection has been reset."
    errorTab[10058] = "The network has been shut down."
    errorTab[10060] = "The operation timed out."
    errorTab[10061] = "Connection refused."
    errorTab[10063] = "The name jest too long."
    errorTab[10064] = "The host jest down."
    errorTab[10065] = "The host jest unreachable."
    __all__.append("errorTab")


klasa _GiveupOnSendfile(Exception): dalej


klasa socket(_socket.socket):

    """A subclass of _socket.socket adding the makefile() method."""

    __slots__ = ["__weakref__", "_io_refs", "_closed"]

    def __init__(self, family=AF_INET, type=SOCK_STREAM, proto=0, fileno=Nic):
        # For user code address family oraz type values are IntEnum members, but
        # dla the underlying _socket.socket they're just integers. The
        # constructor of _socket.socket converts the given argument to an
        # integer automatically.
        _socket.socket.__init__(self, family, type, proto, fileno)
        self._io_refs = 0
        self._closed = Nieprawda

    def __enter__(self):
        zwróć self

    def __exit__(self, *args):
        jeżeli nie self._closed:
            self.close()

    def __repr__(self):
        """Wrap __repr__() to reveal the real klasa name oraz socket
        address(es).
        """
        closed = getattr(self, '_closed', Nieprawda)
        s = "<%s.%s%s fd=%i, family=%s, type=%s, proto=%i" \
            % (self.__class__.__module__,
               self.__class__.__qualname__,
               " [closed]" jeżeli closed inaczej "",
               self.fileno(),
               self.family,
               self.type,
               self.proto)
        jeżeli nie closed:
            spróbuj:
                laddr = self.getsockname()
                jeżeli laddr:
                    s += ", laddr=%s" % str(laddr)
            wyjąwszy error:
                dalej
            spróbuj:
                raddr = self.getpeername()
                jeżeli raddr:
                    s += ", raddr=%s" % str(raddr)
            wyjąwszy error:
                dalej
        s += '>'
        zwróć s

    def __getstate__(self):
        podnieś TypeError("Cannot serialize socket object")

    def dup(self):
        """dup() -> socket object

        Duplicate the socket. Return a new socket object connected to the same
        system resource. The new socket jest non-inheritable.
        """
        fd = dup(self.fileno())
        sock = self.__class__(self.family, self.type, self.proto, fileno=fd)
        sock.settimeout(self.gettimeout())
        zwróć sock

    def accept(self):
        """accept() -> (socket object, address info)

        Wait dla an incoming connection.  Return a new socket
        representing the connection, oraz the address of the client.
        For IP sockets, the address info jest a pair (hostaddr, port).
        """
        fd, addr = self._accept()
        sock = socket(self.family, self.type, self.proto, fileno=fd)
        # Issue #7995: jeżeli no default timeout jest set oraz the listening
        # socket had a (non-zero) timeout, force the new socket w blocking
        # mode to override platform-specific socket flags inheritance.
        jeżeli getdefaulttimeout() jest Nic oraz self.gettimeout():
            sock.setblocking(Prawda)
        zwróć sock, addr

    def makefile(self, mode="r", buffering=Nic, *,
                 encoding=Nic, errors=Nic, newline=Nic):
        """makefile(...) -> an I/O stream connected to the socket

        The arguments are jako dla io.open() after the filename,
        wyjąwszy the only mode characters supported are 'r', 'w' oraz 'b'.
        The semantics are similar too.  (XXX refactor to share code?)
        """
        jeżeli nie set(mode) <= {"r", "w", "b"}:
            podnieś ValueError("invalid mode %r (only r, w, b allowed)" % (mode,))
        writing = "w" w mode
        reading = "r" w mode albo nie writing
        assert reading albo writing
        binary = "b" w mode
        rawmode = ""
        jeżeli reading:
            rawmode += "r"
        jeżeli writing:
            rawmode += "w"
        raw = SocketIO(self, rawmode)
        self._io_refs += 1
        jeżeli buffering jest Nic:
            buffering = -1
        jeżeli buffering < 0:
            buffering = io.DEFAULT_BUFFER_SIZE
        jeżeli buffering == 0:
            jeżeli nie binary:
                podnieś ValueError("unbuffered streams must be binary")
            zwróć raw
        jeżeli reading oraz writing:
            buffer = io.BufferedRWPair(raw, raw, buffering)
        albo_inaczej reading:
            buffer = io.BufferedReader(raw, buffering)
        inaczej:
            assert writing
            buffer = io.BufferedWriter(raw, buffering)
        jeżeli binary:
            zwróć buffer
        text = io.TextIOWrapper(buffer, encoding, errors, newline)
        text.mode = mode
        zwróć text

    jeżeli hasattr(os, 'sendfile'):

        def _sendfile_use_sendfile(self, file, offset=0, count=Nic):
            self._check_sendfile_params(file, offset, count)
            sockno = self.fileno()
            spróbuj:
                fileno = file.fileno()
            wyjąwszy (AttributeError, io.UnsupportedOperation) jako err:
                podnieś _GiveupOnSendfile(err)  # nie a regular file
            spróbuj:
                fsize = os.fstat(fileno).st_size
            wyjąwszy OSError:
                podnieś _GiveupOnSendfile(err)  # nie a regular file
            jeżeli nie fsize:
                zwróć 0  # empty file
            blocksize = fsize jeżeli nie count inaczej count

            timeout = self.gettimeout()
            jeżeli timeout == 0:
                podnieś ValueError("non-blocking sockets are nie supported")
            # poll/select have the advantage of nie requiring any
            # extra file descriptor, contrarily to epoll/kqueue
            # (also, they require a single syscall).
            jeżeli hasattr(selectors, 'PollSelector'):
                selector = selectors.PollSelector()
            inaczej:
                selector = selectors.SelectSelector()
            selector.register(sockno, selectors.EVENT_WRITE)

            total_sent = 0
            # localize variable access to minimize overhead
            selector_select = selector.select
            os_sendfile = os.sendfile
            spróbuj:
                dopóki Prawda:
                    jeżeli timeout oraz nie selector_select(timeout):
                        podnieś _socket.timeout('timed out')
                    jeżeli count:
                        blocksize = count - total_sent
                        jeżeli blocksize <= 0:
                            przerwij
                    spróbuj:
                        sent = os_sendfile(sockno, fileno, offset, blocksize)
                    wyjąwszy BlockingIOError:
                        jeżeli nie timeout:
                            # Block until the socket jest ready to send some
                            # data; avoids hogging CPU resources.
                            selector_select()
                        kontynuuj
                    wyjąwszy OSError jako err:
                        jeżeli total_sent == 0:
                            # We can get here dla different reasons, the main
                            # one being 'file' jest nie a regular mmap(2)-like
                            # file, w which case we'll fall back on using
                            # plain send().
                            podnieś _GiveupOnSendfile(err)
                        podnieś err z Nic
                    inaczej:
                        jeżeli sent == 0:
                            przerwij  # EOF
                        offset += sent
                        total_sent += sent
                zwróć total_sent
            w_końcu:
                jeżeli total_sent > 0 oraz hasattr(file, 'seek'):
                    file.seek(offset)
    inaczej:
        def _sendfile_use_sendfile(self, file, offset=0, count=Nic):
            podnieś _GiveupOnSendfile(
                "os.sendfile() nie available on this platform")

    def _sendfile_use_send(self, file, offset=0, count=Nic):
        self._check_sendfile_params(file, offset, count)
        jeżeli self.gettimeout() == 0:
            podnieś ValueError("non-blocking sockets are nie supported")
        jeżeli offset:
            file.seek(offset)
        blocksize = min(count, 8192) jeżeli count inaczej 8192
        total_sent = 0
        # localize variable access to minimize overhead
        file_read = file.read
        sock_send = self.send
        spróbuj:
            dopóki Prawda:
                jeżeli count:
                    blocksize = min(count - total_sent, blocksize)
                    jeżeli blocksize <= 0:
                        przerwij
                data = memoryview(file_read(blocksize))
                jeżeli nie data:
                    przerwij  # EOF
                dopóki Prawda:
                    spróbuj:
                        sent = sock_send(data)
                    wyjąwszy BlockingIOError:
                        kontynuuj
                    inaczej:
                        total_sent += sent
                        jeżeli sent < len(data):
                            data = data[sent:]
                        inaczej:
                            przerwij
            zwróć total_sent
        w_końcu:
            jeżeli total_sent > 0 oraz hasattr(file, 'seek'):
                file.seek(offset + total_sent)

    def _check_sendfile_params(self, file, offset, count):
        jeżeli 'b' nie w getattr(file, 'mode', 'b'):
            podnieś ValueError("file should be opened w binary mode")
        jeżeli nie self.type & SOCK_STREAM:
            podnieś ValueError("only SOCK_STREAM type sockets are supported")
        jeżeli count jest nie Nic:
            jeżeli nie isinstance(count, int):
                podnieś TypeError(
                    "count must be a positive integer (got {!r})".format(count))
            jeżeli count <= 0:
                podnieś ValueError(
                    "count must be a positive integer (got {!r})".format(count))

    def sendfile(self, file, offset=0, count=Nic):
        """sendfile(file[, offset[, count]]) -> sent

        Send a file until EOF jest reached by using high-performance
        os.sendfile() oraz zwróć the total number of bytes which
        were sent.
        *file* must be a regular file object opened w binary mode.
        If os.sendfile() jest nie available (e.g. Windows) albo file jest
        nie a regular file socket.send() will be used instead.
        *offset* tells z where to start reading the file.
        If specified, *count* jest the total number of bytes to transmit
        jako opposed to sending the file until EOF jest reached.
        File position jest updated on zwróć albo also w case of error w
        which case file.tell() can be used to figure out the number of
        bytes which were sent.
        The socket must be of SOCK_STREAM type.
        Non-blocking sockets are nie supported.
        """
        spróbuj:
            zwróć self._sendfile_use_sendfile(file, offset, count)
        wyjąwszy _GiveupOnSendfile:
            zwróć self._sendfile_use_send(file, offset, count)

    def _decref_socketios(self):
        jeżeli self._io_refs > 0:
            self._io_refs -= 1
        jeżeli self._closed:
            self.close()

    def _real_close(self, _ss=_socket.socket):
        # This function should nie reference any globals. See issue #808164.
        _ss.close(self)

    def close(self):
        # This function should nie reference any globals. See issue #808164.
        self._closed = Prawda
        jeżeli self._io_refs <= 0:
            self._real_close()

    def detach(self):
        """detach() -> file descriptor

        Close the socket object without closing the underlying file descriptor.
        The object cannot be used after this call, but the file descriptor
        can be reused dla other purposes.  The file descriptor jest returned.
        """
        self._closed = Prawda
        zwróć super().detach()

    @property
    def family(self):
        """Read-only access to the address family dla this socket.
        """
        zwróć _intenum_converter(super().family, AddressFamily)

    @property
    def type(self):
        """Read-only access to the socket type.
        """
        zwróć _intenum_converter(super().type, SocketKind)

    jeżeli os.name == 'nt':
        def get_inheritable(self):
            zwróć os.get_handle_inheritable(self.fileno())
        def set_inheritable(self, inheritable):
            os.set_handle_inheritable(self.fileno(), inheritable)
    inaczej:
        def get_inheritable(self):
            zwróć os.get_inheritable(self.fileno())
        def set_inheritable(self, inheritable):
            os.set_inheritable(self.fileno(), inheritable)
    get_inheritable.__doc__ = "Get the inheritable flag of the socket"
    set_inheritable.__doc__ = "Set the inheritable flag of the socket"

def fromfd(fd, family, type, proto=0):
    """ fromfd(fd, family, type[, proto]) -> socket object

    Create a socket object z a duplicate of the given file
    descriptor.  The remaining arguments are the same jako dla socket().
    """
    nfd = dup(fd)
    zwróć socket(family, type, proto, nfd)

jeżeli hasattr(_socket.socket, "share"):
    def fromshare(info):
        """ fromshare(info) -> socket object

        Create a socket object z the bytes object returned by
        socket.share(pid).
        """
        zwróć socket(0, 0, 0, info)
    __all__.append("fromshare")

jeżeli hasattr(_socket, "socketpair"):

    def socketpair(family=Nic, type=SOCK_STREAM, proto=0):
        """socketpair([family[, type[, proto]]]) -> (socket object, socket object)

        Create a pair of socket objects z the sockets returned by the platform
        socketpair() function.
        The arguments are the same jako dla socket() wyjąwszy the default family jest
        AF_UNIX jeżeli defined on the platform; otherwise, the default jest AF_INET.
        """
        jeżeli family jest Nic:
            spróbuj:
                family = AF_UNIX
            wyjąwszy NameError:
                family = AF_INET
        a, b = _socket.socketpair(family, type, proto)
        a = socket(family, type, proto, a.detach())
        b = socket(family, type, proto, b.detach())
        zwróć a, b

inaczej:

    # Origin: https://gist.github.com/4325783, by Geert Jansen.  Public domain.
    def socketpair(family=AF_INET, type=SOCK_STREAM, proto=0):
        jeżeli family == AF_INET:
            host = _LOCALHOST
        albo_inaczej family == AF_INET6:
            host = _LOCALHOST_V6
        inaczej:
            podnieś ValueError("Only AF_INET oraz AF_INET6 socket address families "
                             "are supported")
        jeżeli type != SOCK_STREAM:
            podnieś ValueError("Only SOCK_STREAM socket type jest supported")
        jeżeli proto != 0:
            podnieś ValueError("Only protocol zero jest supported")

        # We create a connected TCP socket. Note the trick with
        # setblocking(Nieprawda) that prevents us z having to create a thread.
        lsock = socket(family, type, proto)
        spróbuj:
            lsock.bind((host, 0))
            lsock.listen()
            # On IPv6, ignore flow_info oraz scope_id
            addr, port = lsock.getsockname()[:2]
            csock = socket(family, type, proto)
            spróbuj:
                csock.setblocking(Nieprawda)
                spróbuj:
                    csock.connect((addr, port))
                wyjąwszy (BlockingIOError, InterruptedError):
                    dalej
                csock.setblocking(Prawda)
                ssock, _ = lsock.accept()
            wyjąwszy:
                csock.close()
                podnieś
        w_końcu:
            lsock.close()
        zwróć (ssock, csock)

socketpair.__doc__ = """socketpair([family[, type[, proto]]]) -> (socket object, socket object)
Create a pair of socket objects z the sockets returned by the platform
socketpair() function.
The arguments are the same jako dla socket() wyjąwszy the default family jest AF_UNIX
jeżeli defined on the platform; otherwise, the default jest AF_INET.
"""

_blocking_errnos = { EAGAIN, EWOULDBLOCK }

klasa SocketIO(io.RawIOBase):

    """Raw I/O implementation dla stream sockets.

    This klasa supports the makefile() method on sockets.  It provides
    the raw I/O interface on top of a socket object.
    """

    # One might wonder why nie let FileIO do the job instead.  There are two
    # main reasons why FileIO jest nie adapted:
    # - it wouldn't work under Windows (where you can't used read() oraz
    #   write() on a socket handle)
    # - it wouldn't work przy socket timeouts (FileIO would ignore the
    #   timeout oraz consider the socket non-blocking)

    # XXX More docs

    def __init__(self, sock, mode):
        jeżeli mode nie w ("r", "w", "rw", "rb", "wb", "rwb"):
            podnieś ValueError("invalid mode: %r" % mode)
        io.RawIOBase.__init__(self)
        self._sock = sock
        jeżeli "b" nie w mode:
            mode += "b"
        self._mode = mode
        self._reading = "r" w mode
        self._writing = "w" w mode
        self._timeout_occurred = Nieprawda

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* oraz zwróć
        the number of bytes read.  If the socket jest non-blocking oraz no bytes
        are available, Nic jest returned.

        If *b* jest non-empty, a 0 zwróć value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        jeżeli self._timeout_occurred:
            podnieś OSError("cannot read z timed out object")
        dopóki Prawda:
            spróbuj:
                zwróć self._sock.recv_into(b)
            wyjąwszy timeout:
                self._timeout_occurred = Prawda
                podnieś
            wyjąwszy error jako e:
                jeżeli e.args[0] w _blocking_errnos:
                    zwróć Nic
                podnieś

    def write(self, b):
        """Write the given bytes albo bytearray object *b* to the socket
        oraz zwróć the number of bytes written.  This can be less than
        len(b) jeżeli nie all data could be written.  If the socket jest
        non-blocking oraz no bytes could be written Nic jest returned.
        """
        self._checkClosed()
        self._checkWritable()
        spróbuj:
            zwróć self._sock.send(b)
        wyjąwszy error jako e:
            # XXX what about EINTR?
            jeżeli e.args[0] w _blocking_errnos:
                zwróć Nic
            podnieś

    def readable(self):
        """Prawda jeżeli the SocketIO jest open dla reading.
        """
        jeżeli self.closed:
            podnieś ValueError("I/O operation on closed socket.")
        zwróć self._reading

    def writable(self):
        """Prawda jeżeli the SocketIO jest open dla writing.
        """
        jeżeli self.closed:
            podnieś ValueError("I/O operation on closed socket.")
        zwróć self._writing

    def seekable(self):
        """Prawda jeżeli the SocketIO jest open dla seeking.
        """
        jeżeli self.closed:
            podnieś ValueError("I/O operation on closed socket.")
        zwróć super().seekable()

    def fileno(self):
        """Return the file descriptor of the underlying socket.
        """
        self._checkClosed()
        zwróć self._sock.fileno()

    @property
    def name(self):
        jeżeli nie self.closed:
            zwróć self.fileno()
        inaczej:
            zwróć -1

    @property
    def mode(self):
        zwróć self._mode

    def close(self):
        """Close the SocketIO object.  This doesn't close the underlying
        socket, wyjąwszy jeżeli all references to it have disappeared.
        """
        jeżeli self.closed:
            zwróć
        io.RawIOBase.close(self)
        self._sock._decref_socketios()
        self._sock = Nic


def getfqdn(name=''):
    """Get fully qualified domain name z name.

    An empty argument jest interpreted jako meaning the local host.

    First the hostname returned by gethostbyaddr() jest checked, then
    possibly existing aliases. In case no FQDN jest available, hostname
    z gethostname() jest returned.
    """
    name = name.strip()
    jeżeli nie name albo name == '0.0.0.0':
        name = gethostname()
    spróbuj:
        hostname, aliases, ipaddrs = gethostbyaddr(name)
    wyjąwszy error:
        dalej
    inaczej:
        aliases.insert(0, hostname)
        dla name w aliases:
            jeżeli '.' w name:
                przerwij
        inaczej:
            name = hostname
    zwróć name


_GLOBAL_DEFAULT_TIMEOUT = object()

def create_connection(address, timeout=_GLOBAL_DEFAULT_TIMEOUT,
                      source_address=Nic):
    """Connect to *address* oraz zwróć the socket object.

    Convenience function.  Connect to *address* (a 2-tuple ``(host,
    port)``) oraz zwróć the socket object.  Passing the optional
    *timeout* parameter will set the timeout on the socket instance
    before attempting to connect.  If no *timeout* jest supplied, the
    global default timeout setting returned by :func:`getdefaulttimeout`
    jest used.  If *source_address* jest set it must be a tuple of (host, port)
    dla the socket to bind jako a source address before making the connection.
    An host of '' albo port 0 tells the OS to use the default.
    """

    host, port = address
    err = Nic
    dla res w getaddrinfo(host, port, 0, SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        sock = Nic
        spróbuj:
            sock = socket(af, socktype, proto)
            jeżeli timeout jest nie _GLOBAL_DEFAULT_TIMEOUT:
                sock.settimeout(timeout)
            jeżeli source_address:
                sock.bind(source_address)
            sock.connect(sa)
            zwróć sock

        wyjąwszy error jako _:
            err = _
            jeżeli sock jest nie Nic:
                sock.close()

    jeżeli err jest nie Nic:
        podnieś err
    inaczej:
        podnieś error("getaddrinfo returns an empty list")

def getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    """Resolve host oraz port into list of address info entries.

    Translate the host/port argument into a sequence of 5-tuples that contain
    all the necessary arguments dla creating a socket connected to that service.
    host jest a domain name, a string representation of an IPv4/v6 address albo
    Nic. port jest a string service name such jako 'http', a numeric port number albo
    Nic. By dalejing Nic jako the value of host oraz port, you can dalej NULL to
    the underlying C API.

    The family, type oraz proto arguments can be optionally specified w order to
    narrow the list of addresses returned. Passing zero jako a value dla each of
    these arguments selects the full range of results.
    """
    # We override this function since we want to translate the numeric family
    # oraz socket type values to enum constants.
    addrlist = []
    dla res w _socket.getaddrinfo(host, port, family, type, proto, flags):
        af, socktype, proto, canonname, sa = res
        addrlist.append((_intenum_converter(af, AddressFamily),
                         _intenum_converter(socktype, SocketKind),
                         proto, canonname, sa))
    zwróć addrlist
