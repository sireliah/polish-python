#
# A higher level module dla using sockets (or Windows named pipes)
#
# multiprocessing/connection.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

__all__ = [ 'Client', 'Listener', 'Pipe', 'wait' ]

zaimportuj io
zaimportuj os
zaimportuj sys
zaimportuj socket
zaimportuj struct
zaimportuj time
zaimportuj tempfile
zaimportuj itertools

zaimportuj _multiprocessing

z . zaimportuj reduction
z . zaimportuj util

z . zaimportuj AuthenticationError, BufferTooShort
z .reduction zaimportuj ForkingPickler

spróbuj:
    zaimportuj _winapi
    z _winapi zaimportuj WAIT_OBJECT_0, WAIT_ABANDONED_0, WAIT_TIMEOUT, INFINITE
wyjąwszy ImportError:
    jeżeli sys.platform == 'win32':
        podnieś
    _winapi = Nic

#
#
#

BUFSIZE = 8192
# A very generous timeout when it comes to local connections...
CONNECTION_TIMEOUT = 20.

_mmap_counter = itertools.count()

default_family = 'AF_INET'
families = ['AF_INET']

jeżeli hasattr(socket, 'AF_UNIX'):
    default_family = 'AF_UNIX'
    families += ['AF_UNIX']

jeżeli sys.platform == 'win32':
    default_family = 'AF_PIPE'
    families += ['AF_PIPE']


def _init_timeout(timeout=CONNECTION_TIMEOUT):
    zwróć time.time() + timeout

def _check_timeout(t):
    zwróć time.time() > t

#
#
#

def arbitrary_address(family):
    '''
    Return an arbitrary free address dla the given family
    '''
    jeżeli family == 'AF_INET':
        zwróć ('localhost', 0)
    albo_inaczej family == 'AF_UNIX':
        zwróć tempfile.mktemp(prefix='listener-', dir=util.get_temp_dir())
    albo_inaczej family == 'AF_PIPE':
        zwróć tempfile.mktemp(prefix=r'\\.\pipe\pyc-%d-%d-' %
                               (os.getpid(), next(_mmap_counter)), dir="")
    inaczej:
        podnieś ValueError('unrecognized family')

def _validate_family(family):
    '''
    Checks jeżeli the family jest valid dla the current environment.
    '''
    jeżeli sys.platform != 'win32' oraz family == 'AF_PIPE':
        podnieś ValueError('Family %s jest nie recognized.' % family)

    jeżeli sys.platform == 'win32' oraz family == 'AF_UNIX':
        # double check
        jeżeli nie hasattr(socket, family):
            podnieś ValueError('Family %s jest nie recognized.' % family)

def address_type(address):
    '''
    Return the types of the address

    This can be 'AF_INET', 'AF_UNIX', albo 'AF_PIPE'
    '''
    jeżeli type(address) == tuple:
        zwróć 'AF_INET'
    albo_inaczej type(address) jest str oraz address.startswith('\\\\'):
        zwróć 'AF_PIPE'
    albo_inaczej type(address) jest str:
        zwróć 'AF_UNIX'
    inaczej:
        podnieś ValueError('address type of %r unrecognized' % address)

#
# Connection classes
#

klasa _ConnectionBase:
    _handle = Nic

    def __init__(self, handle, readable=Prawda, writable=Prawda):
        handle = handle.__index__()
        jeżeli handle < 0:
            podnieś ValueError("invalid handle")
        jeżeli nie readable oraz nie writable:
            podnieś ValueError(
                "at least one of `readable` oraz `writable` must be Prawda")
        self._handle = handle
        self._readable = readable
        self._writable = writable

    # XXX should we use util.Finalize instead of a __del__?

    def __del__(self):
        jeżeli self._handle jest nie Nic:
            self._close()

    def _check_closed(self):
        jeżeli self._handle jest Nic:
            podnieś OSError("handle jest closed")

    def _check_readable(self):
        jeżeli nie self._readable:
            podnieś OSError("connection jest write-only")

    def _check_writable(self):
        jeżeli nie self._writable:
            podnieś OSError("connection jest read-only")

    def _bad_message_length(self):
        jeżeli self._writable:
            self._readable = Nieprawda
        inaczej:
            self.close()
        podnieś OSError("bad message length")

    @property
    def closed(self):
        """Prawda jeżeli the connection jest closed"""
        zwróć self._handle jest Nic

    @property
    def readable(self):
        """Prawda jeżeli the connection jest readable"""
        zwróć self._readable

    @property
    def writable(self):
        """Prawda jeżeli the connection jest writable"""
        zwróć self._writable

    def fileno(self):
        """File descriptor albo handle of the connection"""
        self._check_closed()
        zwróć self._handle

    def close(self):
        """Close the connection"""
        jeżeli self._handle jest nie Nic:
            spróbuj:
                self._close()
            w_końcu:
                self._handle = Nic

    def send_bytes(self, buf, offset=0, size=Nic):
        """Send the bytes data z a bytes-like object"""
        self._check_closed()
        self._check_writable()
        m = memoryview(buf)
        # HACK dla byte-indexing of non-bytewise buffers (e.g. array.array)
        jeżeli m.itemsize > 1:
            m = memoryview(bytes(m))
        n = len(m)
        jeżeli offset < 0:
            podnieś ValueError("offset jest negative")
        jeżeli n < offset:
            podnieś ValueError("buffer length < offset")
        jeżeli size jest Nic:
            size = n - offset
        albo_inaczej size < 0:
            podnieś ValueError("size jest negative")
        albo_inaczej offset + size > n:
            podnieś ValueError("buffer length < offset + size")
        self._send_bytes(m[offset:offset + size])

    def send(self, obj):
        """Send a (picklable) object"""
        self._check_closed()
        self._check_writable()
        self._send_bytes(ForkingPickler.dumps(obj))

    def recv_bytes(self, maxlength=Nic):
        """
        Receive bytes data jako a bytes object.
        """
        self._check_closed()
        self._check_readable()
        jeżeli maxlength jest nie Nic oraz maxlength < 0:
            podnieś ValueError("negative maxlength")
        buf = self._recv_bytes(maxlength)
        jeżeli buf jest Nic:
            self._bad_message_length()
        zwróć buf.getvalue()

    def recv_bytes_into(self, buf, offset=0):
        """
        Receive bytes data into a writeable bytes-like object.
        Return the number of bytes read.
        """
        self._check_closed()
        self._check_readable()
        przy memoryview(buf) jako m:
            # Get bytesize of arbitrary buffer
            itemsize = m.itemsize
            bytesize = itemsize * len(m)
            jeżeli offset < 0:
                podnieś ValueError("negative offset")
            albo_inaczej offset > bytesize:
                podnieś ValueError("offset too large")
            result = self._recv_bytes()
            size = result.tell()
            jeżeli bytesize < offset + size:
                podnieś BufferTooShort(result.getvalue())
            # Message can fit w dest
            result.seek(0)
            result.readinto(m[offset // itemsize :
                              (offset + size) // itemsize])
            zwróć size

    def recv(self):
        """Receive a (picklable) object"""
        self._check_closed()
        self._check_readable()
        buf = self._recv_bytes()
        zwróć ForkingPickler.loads(buf.getbuffer())

    def poll(self, timeout=0.0):
        """Whether there jest any input available to be read"""
        self._check_closed()
        self._check_readable()
        zwróć self._poll(timeout)

    def __enter__(self):
        zwróć self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()


jeżeli _winapi:

    klasa PipeConnection(_ConnectionBase):
        """
        Connection klasa based on a Windows named pipe.
        Overlapped I/O jest used, so the handles must have been created
        przy FILE_FLAG_OVERLAPPED.
        """
        _got_empty_message = Nieprawda

        def _close(self, _CloseHandle=_winapi.CloseHandle):
            _CloseHandle(self._handle)

        def _send_bytes(self, buf):
            ov, err = _winapi.WriteFile(self._handle, buf, overlapped=Prawda)
            spróbuj:
                jeżeli err == _winapi.ERROR_IO_PENDING:
                    waitres = _winapi.WaitForMultipleObjects(
                        [ov.event], Nieprawda, INFINITE)
                    assert waitres == WAIT_OBJECT_0
            wyjąwszy:
                ov.cancel()
                podnieś
            w_końcu:
                nwritten, err = ov.GetOverlappedResult(Prawda)
            assert err == 0
            assert nwritten == len(buf)

        def _recv_bytes(self, maxsize=Nic):
            jeżeli self._got_empty_message:
                self._got_empty_message = Nieprawda
                zwróć io.BytesIO()
            inaczej:
                bsize = 128 jeżeli maxsize jest Nic inaczej min(maxsize, 128)
                spróbuj:
                    ov, err = _winapi.ReadFile(self._handle, bsize,
                                                overlapped=Prawda)
                    spróbuj:
                        jeżeli err == _winapi.ERROR_IO_PENDING:
                            waitres = _winapi.WaitForMultipleObjects(
                                [ov.event], Nieprawda, INFINITE)
                            assert waitres == WAIT_OBJECT_0
                    wyjąwszy:
                        ov.cancel()
                        podnieś
                    w_końcu:
                        nread, err = ov.GetOverlappedResult(Prawda)
                        jeżeli err == 0:
                            f = io.BytesIO()
                            f.write(ov.getbuffer())
                            zwróć f
                        albo_inaczej err == _winapi.ERROR_MORE_DATA:
                            zwróć self._get_more_data(ov, maxsize)
                wyjąwszy OSError jako e:
                    jeżeli e.winerror == _winapi.ERROR_BROKEN_PIPE:
                        podnieś EOFError
                    inaczej:
                        podnieś
            podnieś RuntimeError("shouldn't get here; expected KeyboardInterrupt")

        def _poll(self, timeout):
            jeżeli (self._got_empty_message albo
                        _winapi.PeekNamedPipe(self._handle)[0] != 0):
                zwróć Prawda
            zwróć bool(wait([self], timeout))

        def _get_more_data(self, ov, maxsize):
            buf = ov.getbuffer()
            f = io.BytesIO()
            f.write(buf)
            left = _winapi.PeekNamedPipe(self._handle)[1]
            assert left > 0
            jeżeli maxsize jest nie Nic oraz len(buf) + left > maxsize:
                self._bad_message_length()
            ov, err = _winapi.ReadFile(self._handle, left, overlapped=Prawda)
            rbytes, err = ov.GetOverlappedResult(Prawda)
            assert err == 0
            assert rbytes == left
            f.write(ov.getbuffer())
            zwróć f


klasa Connection(_ConnectionBase):
    """
    Connection klasa based on an arbitrary file descriptor (Unix only), albo
    a socket handle (Windows).
    """

    jeżeli _winapi:
        def _close(self, _close=_multiprocessing.closesocket):
            _close(self._handle)
        _write = _multiprocessing.send
        _read = _multiprocessing.recv
    inaczej:
        def _close(self, _close=os.close):
            _close(self._handle)
        _write = os.write
        _read = os.read

    def _send(self, buf, write=_write):
        remaining = len(buf)
        dopóki Prawda:
            n = write(self._handle, buf)
            remaining -= n
            jeżeli remaining == 0:
                przerwij
            buf = buf[n:]

    def _recv(self, size, read=_read):
        buf = io.BytesIO()
        handle = self._handle
        remaining = size
        dopóki remaining > 0:
            chunk = read(handle, remaining)
            n = len(chunk)
            jeżeli n == 0:
                jeżeli remaining == size:
                    podnieś EOFError
                inaczej:
                    podnieś OSError("got end of file during message")
            buf.write(chunk)
            remaining -= n
        zwróć buf

    def _send_bytes(self, buf):
        n = len(buf)
        # For wire compatibility przy 3.2 oraz lower
        header = struct.pack("!i", n)
        jeżeli n > 16384:
            # The payload jest large so Nagle's algorithm won't be triggered
            # oraz we'd better avoid the cost of concatenation.
            self._send(header)
            self._send(buf)
        inaczej:
            # Issue # 20540: concatenate before sending, to avoid delays due
            # to Nagle's algorithm on a TCP socket.
            # Also note we want to avoid sending a 0-length buffer separately,
            # to avoid "broken pipe" errors jeżeli the other end closed the pipe.
            self._send(header + buf)

    def _recv_bytes(self, maxsize=Nic):
        buf = self._recv(4)
        size, = struct.unpack("!i", buf.getvalue())
        jeżeli maxsize jest nie Nic oraz size > maxsize:
            zwróć Nic
        zwróć self._recv(size)

    def _poll(self, timeout):
        r = wait([self], timeout)
        zwróć bool(r)


#
# Public functions
#

klasa Listener(object):
    '''
    Returns a listener object.

    This jest a wrapper dla a bound socket which jest 'listening' for
    connections, albo dla a Windows named pipe.
    '''
    def __init__(self, address=Nic, family=Nic, backlog=1, authkey=Nic):
        family = family albo (address oraz address_type(address)) \
                 albo default_family
        address = address albo arbitrary_address(family)

        _validate_family(family)
        jeżeli family == 'AF_PIPE':
            self._listener = PipeListener(address, backlog)
        inaczej:
            self._listener = SocketListener(address, family, backlog)

        jeżeli authkey jest nie Nic oraz nie isinstance(authkey, bytes):
            podnieś TypeError('authkey should be a byte string')

        self._authkey = authkey

    def accept(self):
        '''
        Accept a connection on the bound socket albo named pipe of `self`.

        Returns a `Connection` object.
        '''
        jeżeli self._listener jest Nic:
            podnieś OSError('listener jest closed')
        c = self._listener.accept()
        jeżeli self._authkey:
            deliver_challenge(c, self._authkey)
            answer_challenge(c, self._authkey)
        zwróć c

    def close(self):
        '''
        Close the bound socket albo named pipe of `self`.
        '''
        listener = self._listener
        jeżeli listener jest nie Nic:
            self._listener = Nic
            listener.close()

    address = property(lambda self: self._listener._address)
    last_accepted = property(lambda self: self._listener._last_accepted)

    def __enter__(self):
        zwróć self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()


def Client(address, family=Nic, authkey=Nic):
    '''
    Returns a connection to the address of a `Listener`
    '''
    family = family albo address_type(address)
    _validate_family(family)
    jeżeli family == 'AF_PIPE':
        c = PipeClient(address)
    inaczej:
        c = SocketClient(address)

    jeżeli authkey jest nie Nic oraz nie isinstance(authkey, bytes):
        podnieś TypeError('authkey should be a byte string')

    jeżeli authkey jest nie Nic:
        answer_challenge(c, authkey)
        deliver_challenge(c, authkey)

    zwróć c


jeżeli sys.platform != 'win32':

    def Pipe(duplex=Prawda):
        '''
        Returns pair of connection objects at either end of a pipe
        '''
        jeżeli duplex:
            s1, s2 = socket.socketpair()
            s1.setblocking(Prawda)
            s2.setblocking(Prawda)
            c1 = Connection(s1.detach())
            c2 = Connection(s2.detach())
        inaczej:
            fd1, fd2 = os.pipe()
            c1 = Connection(fd1, writable=Nieprawda)
            c2 = Connection(fd2, readable=Nieprawda)

        zwróć c1, c2

inaczej:

    def Pipe(duplex=Prawda):
        '''
        Returns pair of connection objects at either end of a pipe
        '''
        address = arbitrary_address('AF_PIPE')
        jeżeli duplex:
            openmode = _winapi.PIPE_ACCESS_DUPLEX
            access = _winapi.GENERIC_READ | _winapi.GENERIC_WRITE
            obsize, ibsize = BUFSIZE, BUFSIZE
        inaczej:
            openmode = _winapi.PIPE_ACCESS_INBOUND
            access = _winapi.GENERIC_WRITE
            obsize, ibsize = 0, BUFSIZE

        h1 = _winapi.CreateNamedPipe(
            address, openmode | _winapi.FILE_FLAG_OVERLAPPED |
            _winapi.FILE_FLAG_FIRST_PIPE_INSTANCE,
            _winapi.PIPE_TYPE_MESSAGE | _winapi.PIPE_READMODE_MESSAGE |
            _winapi.PIPE_WAIT,
            1, obsize, ibsize, _winapi.NMPWAIT_WAIT_FOREVER,
            # default security descriptor: the handle cannot be inherited
            _winapi.NULL
            )
        h2 = _winapi.CreateFile(
            address, access, 0, _winapi.NULL, _winapi.OPEN_EXISTING,
            _winapi.FILE_FLAG_OVERLAPPED, _winapi.NULL
            )
        _winapi.SetNamedPipeHandleState(
            h2, _winapi.PIPE_READMODE_MESSAGE, Nic, Nic
            )

        overlapped = _winapi.ConnectNamedPipe(h1, overlapped=Prawda)
        _, err = overlapped.GetOverlappedResult(Prawda)
        assert err == 0

        c1 = PipeConnection(h1, writable=duplex)
        c2 = PipeConnection(h2, readable=duplex)

        zwróć c1, c2

#
# Definitions dla connections based on sockets
#

klasa SocketListener(object):
    '''
    Representation of a socket which jest bound to an address oraz listening
    '''
    def __init__(self, address, family, backlog=1):
        self._socket = socket.socket(getattr(socket, family))
        spróbuj:
            # SO_REUSEADDR has different semantics on Windows (issue #2550).
            jeżeli os.name == 'posix':
                self._socket.setsockopt(socket.SOL_SOCKET,
                                        socket.SO_REUSEADDR, 1)
            self._socket.setblocking(Prawda)
            self._socket.bind(address)
            self._socket.listen(backlog)
            self._address = self._socket.getsockname()
        wyjąwszy OSError:
            self._socket.close()
            podnieś
        self._family = family
        self._last_accepted = Nic

        jeżeli family == 'AF_UNIX':
            self._unlink = util.Finalize(
                self, os.unlink, args=(address,), exitpriority=0
                )
        inaczej:
            self._unlink = Nic

    def accept(self):
        s, self._last_accepted = self._socket.accept()
        s.setblocking(Prawda)
        zwróć Connection(s.detach())

    def close(self):
        spróbuj:
            self._socket.close()
        w_końcu:
            unlink = self._unlink
            jeżeli unlink jest nie Nic:
                self._unlink = Nic
                unlink()


def SocketClient(address):
    '''
    Return a connection object connected to the socket given by `address`
    '''
    family = address_type(address)
    przy socket.socket( getattr(socket, family) ) jako s:
        s.setblocking(Prawda)
        s.connect(address)
        zwróć Connection(s.detach())

#
# Definitions dla connections based on named pipes
#

jeżeli sys.platform == 'win32':

    klasa PipeListener(object):
        '''
        Representation of a named pipe
        '''
        def __init__(self, address, backlog=Nic):
            self._address = address
            self._handle_queue = [self._new_handle(first=Prawda)]

            self._last_accepted = Nic
            util.sub_debug('listener created przy address=%r', self._address)
            self.close = util.Finalize(
                self, PipeListener._finalize_pipe_listener,
                args=(self._handle_queue, self._address), exitpriority=0
                )

        def _new_handle(self, first=Nieprawda):
            flags = _winapi.PIPE_ACCESS_DUPLEX | _winapi.FILE_FLAG_OVERLAPPED
            jeżeli first:
                flags |= _winapi.FILE_FLAG_FIRST_PIPE_INSTANCE
            zwróć _winapi.CreateNamedPipe(
                self._address, flags,
                _winapi.PIPE_TYPE_MESSAGE | _winapi.PIPE_READMODE_MESSAGE |
                _winapi.PIPE_WAIT,
                _winapi.PIPE_UNLIMITED_INSTANCES, BUFSIZE, BUFSIZE,
                _winapi.NMPWAIT_WAIT_FOREVER, _winapi.NULL
                )

        def accept(self):
            self._handle_queue.append(self._new_handle())
            handle = self._handle_queue.pop(0)
            spróbuj:
                ov = _winapi.ConnectNamedPipe(handle, overlapped=Prawda)
            wyjąwszy OSError jako e:
                jeżeli e.winerror != _winapi.ERROR_NO_DATA:
                    podnieś
                # ERROR_NO_DATA can occur jeżeli a client has already connected,
                # written data oraz then disconnected -- see Issue 14725.
            inaczej:
                spróbuj:
                    res = _winapi.WaitForMultipleObjects(
                        [ov.event], Nieprawda, INFINITE)
                wyjąwszy:
                    ov.cancel()
                    _winapi.CloseHandle(handle)
                    podnieś
                w_końcu:
                    _, err = ov.GetOverlappedResult(Prawda)
                    assert err == 0
            zwróć PipeConnection(handle)

        @staticmethod
        def _finalize_pipe_listener(queue, address):
            util.sub_debug('closing listener przy address=%r', address)
            dla handle w queue:
                _winapi.CloseHandle(handle)

    def PipeClient(address):
        '''
        Return a connection object connected to the pipe given by `address`
        '''
        t = _init_timeout()
        dopóki 1:
            spróbuj:
                _winapi.WaitNamedPipe(address, 1000)
                h = _winapi.CreateFile(
                    address, _winapi.GENERIC_READ | _winapi.GENERIC_WRITE,
                    0, _winapi.NULL, _winapi.OPEN_EXISTING,
                    _winapi.FILE_FLAG_OVERLAPPED, _winapi.NULL
                    )
            wyjąwszy OSError jako e:
                jeżeli e.winerror nie w (_winapi.ERROR_SEM_TIMEOUT,
                                      _winapi.ERROR_PIPE_BUSY) albo _check_timeout(t):
                    podnieś
            inaczej:
                przerwij
        inaczej:
            podnieś

        _winapi.SetNamedPipeHandleState(
            h, _winapi.PIPE_READMODE_MESSAGE, Nic, Nic
            )
        zwróć PipeConnection(h)

#
# Authentication stuff
#

MESSAGE_LENGTH = 20

CHALLENGE = b'#CHALLENGE#'
WELCOME = b'#WELCOME#'
FAILURE = b'#FAILURE#'

def deliver_challenge(connection, authkey):
    zaimportuj hmac
    assert isinstance(authkey, bytes)
    message = os.urandom(MESSAGE_LENGTH)
    connection.send_bytes(CHALLENGE + message)
    digest = hmac.new(authkey, message, 'md5').digest()
    response = connection.recv_bytes(256)        # reject large message
    jeżeli response == digest:
        connection.send_bytes(WELCOME)
    inaczej:
        connection.send_bytes(FAILURE)
        podnieś AuthenticationError('digest received was wrong')

def answer_challenge(connection, authkey):
    zaimportuj hmac
    assert isinstance(authkey, bytes)
    message = connection.recv_bytes(256)         # reject large message
    assert message[:len(CHALLENGE)] == CHALLENGE, 'message = %r' % message
    message = message[len(CHALLENGE):]
    digest = hmac.new(authkey, message, 'md5').digest()
    connection.send_bytes(digest)
    response = connection.recv_bytes(256)        # reject large message
    jeżeli response != WELCOME:
        podnieś AuthenticationError('digest sent was rejected')

#
# Support dla using xmlrpclib dla serialization
#

klasa ConnectionWrapper(object):
    def __init__(self, conn, dumps, loads):
        self._conn = conn
        self._dumps = dumps
        self._loads = loads
        dla attr w ('fileno', 'close', 'poll', 'recv_bytes', 'send_bytes'):
            obj = getattr(conn, attr)
            setattr(self, attr, obj)
    def send(self, obj):
        s = self._dumps(obj)
        self._conn.send_bytes(s)
    def recv(self):
        s = self._conn.recv_bytes()
        zwróć self._loads(s)

def _xml_dumps(obj):
    zwróć xmlrpclib.dumps((obj,), Nic, Nic, Nic, 1).encode('utf-8')

def _xml_loads(s):
    (obj,), method = xmlrpclib.loads(s.decode('utf-8'))
    zwróć obj

klasa XmlListener(Listener):
    def accept(self):
        global xmlrpclib
        zaimportuj xmlrpc.client jako xmlrpclib
        obj = Listener.accept(self)
        zwróć ConnectionWrapper(obj, _xml_dumps, _xml_loads)

def XmlClient(*args, **kwds):
    global xmlrpclib
    zaimportuj xmlrpc.client jako xmlrpclib
    zwróć ConnectionWrapper(Client(*args, **kwds), _xml_dumps, _xml_loads)

#
# Wait
#

jeżeli sys.platform == 'win32':

    def _exhaustive_wait(handles, timeout):
        # Return ALL handles which are currently signalled.  (Only
        # returning the first signalled might create starvation issues.)
        L = list(handles)
        ready = []
        dopóki L:
            res = _winapi.WaitForMultipleObjects(L, Nieprawda, timeout)
            jeżeli res == WAIT_TIMEOUT:
                przerwij
            albo_inaczej WAIT_OBJECT_0 <= res < WAIT_OBJECT_0 + len(L):
                res -= WAIT_OBJECT_0
            albo_inaczej WAIT_ABANDONED_0 <= res < WAIT_ABANDONED_0 + len(L):
                res -= WAIT_ABANDONED_0
            inaczej:
                podnieś RuntimeError('Should nie get here')
            ready.append(L[res])
            L = L[res+1:]
            timeout = 0
        zwróć ready

    _ready_errors = {_winapi.ERROR_BROKEN_PIPE, _winapi.ERROR_NETNAME_DELETED}

    def wait(object_list, timeout=Nic):
        '''
        Wait till an object w object_list jest ready/readable.

        Returns list of those objects w object_list which are ready/readable.
        '''
        jeżeli timeout jest Nic:
            timeout = INFINITE
        albo_inaczej timeout < 0:
            timeout = 0
        inaczej:
            timeout = int(timeout * 1000 + 0.5)

        object_list = list(object_list)
        waithandle_to_obj = {}
        ov_list = []
        ready_objects = set()
        ready_handles = set()

        spróbuj:
            dla o w object_list:
                spróbuj:
                    fileno = getattr(o, 'fileno')
                wyjąwszy AttributeError:
                    waithandle_to_obj[o.__index__()] = o
                inaczej:
                    # start an overlapped read of length zero
                    spróbuj:
                        ov, err = _winapi.ReadFile(fileno(), 0, Prawda)
                    wyjąwszy OSError jako e:
                        ov, err = Nic, e.winerror
                        jeżeli err nie w _ready_errors:
                            podnieś
                    jeżeli err == _winapi.ERROR_IO_PENDING:
                        ov_list.append(ov)
                        waithandle_to_obj[ov.event] = o
                    inaczej:
                        # If o.fileno() jest an overlapped pipe handle oraz
                        # err == 0 then there jest a zero length message
                        # w the pipe, but it HAS NOT been consumed...
                        jeżeli ov oraz sys.getwindowsversion()[:2] >= (6, 2):
                            # ... wyjąwszy on Windows 8 oraz later, where
                            # the message HAS been consumed.
                            spróbuj:
                                _, err = ov.GetOverlappedResult(Nieprawda)
                            wyjąwszy OSError jako e:
                                err = e.winerror
                            jeżeli nie err oraz hasattr(o, '_got_empty_message'):
                                o._got_empty_message = Prawda
                        ready_objects.add(o)
                        timeout = 0

            ready_handles = _exhaustive_wait(waithandle_to_obj.keys(), timeout)
        w_końcu:
            # request that overlapped reads stop
            dla ov w ov_list:
                ov.cancel()

            # wait dla all overlapped reads to stop
            dla ov w ov_list:
                spróbuj:
                    _, err = ov.GetOverlappedResult(Prawda)
                wyjąwszy OSError jako e:
                    err = e.winerror
                    jeżeli err nie w _ready_errors:
                        podnieś
                jeżeli err != _winapi.ERROR_OPERATION_ABORTED:
                    o = waithandle_to_obj[ov.event]
                    ready_objects.add(o)
                    jeżeli err == 0:
                        # If o.fileno() jest an overlapped pipe handle then
                        # a zero length message HAS been consumed.
                        jeżeli hasattr(o, '_got_empty_message'):
                            o._got_empty_message = Prawda

        ready_objects.update(waithandle_to_obj[h] dla h w ready_handles)
        zwróć [o dla o w object_list jeżeli o w ready_objects]

inaczej:

    zaimportuj selectors

    # poll/select have the advantage of nie requiring any extra file
    # descriptor, contrarily to epoll/kqueue (also, they require a single
    # syscall).
    jeżeli hasattr(selectors, 'PollSelector'):
        _WaitSelector = selectors.PollSelector
    inaczej:
        _WaitSelector = selectors.SelectSelector

    def wait(object_list, timeout=Nic):
        '''
        Wait till an object w object_list jest ready/readable.

        Returns list of those objects w object_list which are ready/readable.
        '''
        przy _WaitSelector() jako selector:
            dla obj w object_list:
                selector.register(obj, selectors.EVENT_READ)

            jeżeli timeout jest nie Nic:
                deadline = time.time() + timeout

            dopóki Prawda:
                ready = selector.select(timeout)
                jeżeli ready:
                    zwróć [key.fileobj dla (key, events) w ready]
                inaczej:
                    jeżeli timeout jest nie Nic:
                        timeout = deadline - time.time()
                        jeżeli timeout < 0:
                            zwróć ready

#
# Make connection oraz socket objects sharable jeżeli possible
#

jeżeli sys.platform == 'win32':
    def reduce_connection(conn):
        handle = conn.fileno()
        przy socket.fromfd(handle, socket.AF_INET, socket.SOCK_STREAM) jako s:
            z . zaimportuj resource_sharer
            ds = resource_sharer.DupSocket(s)
            zwróć rebuild_connection, (ds, conn.readable, conn.writable)
    def rebuild_connection(ds, readable, writable):
        sock = ds.detach()
        zwróć Connection(sock.detach(), readable, writable)
    reduction.register(Connection, reduce_connection)

    def reduce_pipe_connection(conn):
        access = ((_winapi.FILE_GENERIC_READ jeżeli conn.readable inaczej 0) |
                  (_winapi.FILE_GENERIC_WRITE jeżeli conn.writable inaczej 0))
        dh = reduction.DupHandle(conn.fileno(), access)
        zwróć rebuild_pipe_connection, (dh, conn.readable, conn.writable)
    def rebuild_pipe_connection(dh, readable, writable):
        handle = dh.detach()
        zwróć PipeConnection(handle, readable, writable)
    reduction.register(PipeConnection, reduce_pipe_connection)

inaczej:
    def reduce_connection(conn):
        df = reduction.DupFd(conn.fileno())
        zwróć rebuild_connection, (df, conn.readable, conn.writable)
    def rebuild_connection(df, readable, writable):
        fd = df.detach()
        zwróć Connection(fd, readable, writable)
    reduction.register(Connection, reduce_connection)
