"""
Various Windows specific bits oraz pieces
"""

zaimportuj sys

jeżeli sys.platform != 'win32':  # pragma: no cover
    podnieś ImportError('win32 only')

zaimportuj _winapi
zaimportuj itertools
zaimportuj msvcrt
zaimportuj os
zaimportuj socket
zaimportuj subprocess
zaimportuj tempfile
zaimportuj warnings


__all__ = ['socketpair', 'pipe', 'Popen', 'PIPE', 'PipeHandle']


# Constants/globals


BUFSIZE = 8192
PIPE = subprocess.PIPE
STDOUT = subprocess.STDOUT
_mmap_counter = itertools.count()


jeżeli hasattr(socket, 'socketpair'):
    # Since Python 3.5, socket.socketpair() jest now also available on Windows
    socketpair = socket.socketpair
inaczej:
    # Replacement dla socket.socketpair()
    def socketpair(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0):
        """A socket pair usable jako a self-pipe, dla Windows.

        Origin: https://gist.github.com/4325783, by Geert Jansen.
        Public domain.
        """
        jeżeli family == socket.AF_INET:
            host = '127.0.0.1'
        albo_inaczej family == socket.AF_INET6:
            host = '::1'
        inaczej:
            podnieś ValueError("Only AF_INET oraz AF_INET6 socket address "
                             "families are supported")
        jeżeli type != socket.SOCK_STREAM:
            podnieś ValueError("Only SOCK_STREAM socket type jest supported")
        jeżeli proto != 0:
            podnieś ValueError("Only protocol zero jest supported")

        # We create a connected TCP socket. Note the trick przy setblocking(0)
        # that prevents us z having to create a thread.
        lsock = socket.socket(family, type, proto)
        spróbuj:
            lsock.bind((host, 0))
            lsock.listen(1)
            # On IPv6, ignore flow_info oraz scope_id
            addr, port = lsock.getsockname()[:2]
            csock = socket.socket(family, type, proto)
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


# Replacement dla os.pipe() using handles instead of fds


def pipe(*, duplex=Nieprawda, overlapped=(Prawda, Prawda), bufsize=BUFSIZE):
    """Like os.pipe() but przy overlapped support oraz using handles nie fds."""
    address = tempfile.mktemp(prefix=r'\\.\pipe\python-pipe-%d-%d-' %
                              (os.getpid(), next(_mmap_counter)))

    jeżeli duplex:
        openmode = _winapi.PIPE_ACCESS_DUPLEX
        access = _winapi.GENERIC_READ | _winapi.GENERIC_WRITE
        obsize, ibsize = bufsize, bufsize
    inaczej:
        openmode = _winapi.PIPE_ACCESS_INBOUND
        access = _winapi.GENERIC_WRITE
        obsize, ibsize = 0, bufsize

    openmode |= _winapi.FILE_FLAG_FIRST_PIPE_INSTANCE

    jeżeli overlapped[0]:
        openmode |= _winapi.FILE_FLAG_OVERLAPPED

    jeżeli overlapped[1]:
        flags_and_attribs = _winapi.FILE_FLAG_OVERLAPPED
    inaczej:
        flags_and_attribs = 0

    h1 = h2 = Nic
    spróbuj:
        h1 = _winapi.CreateNamedPipe(
            address, openmode, _winapi.PIPE_WAIT,
            1, obsize, ibsize, _winapi.NMPWAIT_WAIT_FOREVER, _winapi.NULL)

        h2 = _winapi.CreateFile(
            address, access, 0, _winapi.NULL, _winapi.OPEN_EXISTING,
            flags_and_attribs, _winapi.NULL)

        ov = _winapi.ConnectNamedPipe(h1, overlapped=Prawda)
        ov.GetOverlappedResult(Prawda)
        zwróć h1, h2
    wyjąwszy:
        jeżeli h1 jest nie Nic:
            _winapi.CloseHandle(h1)
        jeżeli h2 jest nie Nic:
            _winapi.CloseHandle(h2)
        podnieś


# Wrapper dla a pipe handle


klasa PipeHandle:
    """Wrapper dla an overlapped pipe handle which jest vaguely file-object like.

    The IOCP event loop can use these instead of socket objects.
    """
    def __init__(self, handle):
        self._handle = handle

    def __repr__(self):
        jeżeli self._handle jest nie Nic:
            handle = 'handle=%r' % self._handle
        inaczej:
            handle = 'closed'
        zwróć '<%s %s>' % (self.__class__.__name__, handle)

    @property
    def handle(self):
        zwróć self._handle

    def fileno(self):
        jeżeli self._handle jest Nic:
            podnieś ValueError("I/O operatioon on closed pipe")
        zwróć self._handle

    def close(self, *, CloseHandle=_winapi.CloseHandle):
        jeżeli self._handle jest nie Nic:
            CloseHandle(self._handle)
            self._handle = Nic

    def __del__(self):
        jeżeli self._handle jest nie Nic:
            warnings.warn("unclosed %r" % self, ResourceWarning)
            self.close()

    def __enter__(self):
        zwróć self

    def __exit__(self, t, v, tb):
        self.close()


# Replacement dla subprocess.Popen using overlapped pipe handles


klasa Popen(subprocess.Popen):
    """Replacement dla subprocess.Popen using overlapped pipe handles.

    The stdin, stdout, stderr are Nic albo instances of PipeHandle.
    """
    def __init__(self, args, stdin=Nic, stdout=Nic, stderr=Nic, **kwds):
        assert nie kwds.get('universal_newlines')
        assert kwds.get('bufsize', 0) == 0
        stdin_rfd = stdout_wfd = stderr_wfd = Nic
        stdin_wh = stdout_rh = stderr_rh = Nic
        jeżeli stdin == PIPE:
            stdin_rh, stdin_wh = pipe(overlapped=(Nieprawda, Prawda), duplex=Prawda)
            stdin_rfd = msvcrt.open_osfhandle(stdin_rh, os.O_RDONLY)
        inaczej:
            stdin_rfd = stdin
        jeżeli stdout == PIPE:
            stdout_rh, stdout_wh = pipe(overlapped=(Prawda, Nieprawda))
            stdout_wfd = msvcrt.open_osfhandle(stdout_wh, 0)
        inaczej:
            stdout_wfd = stdout
        jeżeli stderr == PIPE:
            stderr_rh, stderr_wh = pipe(overlapped=(Prawda, Nieprawda))
            stderr_wfd = msvcrt.open_osfhandle(stderr_wh, 0)
        albo_inaczej stderr == STDOUT:
            stderr_wfd = stdout_wfd
        inaczej:
            stderr_wfd = stderr
        spróbuj:
            super().__init__(args, stdin=stdin_rfd, stdout=stdout_wfd,
                             stderr=stderr_wfd, **kwds)
        wyjąwszy:
            dla h w (stdin_wh, stdout_rh, stderr_rh):
                jeżeli h jest nie Nic:
                    _winapi.CloseHandle(h)
            podnieś
        inaczej:
            jeżeli stdin_wh jest nie Nic:
                self.stdin = PipeHandle(stdin_wh)
            jeżeli stdout_rh jest nie Nic:
                self.stdout = PipeHandle(stdout_rh)
            jeżeli stderr_rh jest nie Nic:
                self.stderr = PipeHandle(stderr_rh)
        w_końcu:
            jeżeli stdin == PIPE:
                os.close(stdin_rfd)
            jeżeli stdout == PIPE:
                os.close(stdout_wfd)
            jeżeli stderr == PIPE:
                os.close(stderr_wfd)
