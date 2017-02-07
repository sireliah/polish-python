#
# Module which deals przy pickling of objects.
#
# multiprocessing/reduction.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

zaimportuj copyreg
zaimportuj functools
zaimportuj io
zaimportuj os
zaimportuj pickle
zaimportuj socket
zaimportuj sys

z . zaimportuj context

__all__ = ['send_handle', 'recv_handle', 'ForkingPickler', 'register', 'dump']


HAVE_SEND_HANDLE = (sys.platform == 'win32' albo
                    (hasattr(socket, 'CMSG_LEN') oraz
                     hasattr(socket, 'SCM_RIGHTS') oraz
                     hasattr(socket.socket, 'sendmsg')))

#
# Pickler subclass
#

klasa ForkingPickler(pickle.Pickler):
    '''Pickler subclass used by multiprocessing.'''
    _extra_reducers = {}
    _copyreg_dispatch_table = copyreg.dispatch_table

    def __init__(self, *args):
        super().__init__(*args)
        self.dispatch_table = self._copyreg_dispatch_table.copy()
        self.dispatch_table.update(self._extra_reducers)

    @classmethod
    def register(cls, type, reduce):
        '''Register a reduce function dla a type.'''
        cls._extra_reducers[type] = reduce

    @classmethod
    def dumps(cls, obj, protocol=Nic):
        buf = io.BytesIO()
        cls(buf, protocol).dump(obj)
        zwróć buf.getbuffer()

    loads = pickle.loads

register = ForkingPickler.register

def dump(obj, file, protocol=Nic):
    '''Replacement dla pickle.dump() using ForkingPickler.'''
    ForkingPickler(file, protocol).dump(obj)

#
# Platform specific definitions
#

jeżeli sys.platform == 'win32':
    # Windows
    __all__ += ['DupHandle', 'duplicate', 'steal_handle']
    zaimportuj _winapi

    def duplicate(handle, target_process=Nic, inheritable=Nieprawda):
        '''Duplicate a handle.  (target_process jest a handle nie a pid!)'''
        jeżeli target_process jest Nic:
            target_process = _winapi.GetCurrentProcess()
        zwróć _winapi.DuplicateHandle(
            _winapi.GetCurrentProcess(), handle, target_process,
            0, inheritable, _winapi.DUPLICATE_SAME_ACCESS)

    def steal_handle(source_pid, handle):
        '''Steal a handle z process identified by source_pid.'''
        source_process_handle = _winapi.OpenProcess(
            _winapi.PROCESS_DUP_HANDLE, Nieprawda, source_pid)
        spróbuj:
            zwróć _winapi.DuplicateHandle(
                source_process_handle, handle,
                _winapi.GetCurrentProcess(), 0, Nieprawda,
                _winapi.DUPLICATE_SAME_ACCESS | _winapi.DUPLICATE_CLOSE_SOURCE)
        w_końcu:
            _winapi.CloseHandle(source_process_handle)

    def send_handle(conn, handle, destination_pid):
        '''Send a handle over a local connection.'''
        dh = DupHandle(handle, _winapi.DUPLICATE_SAME_ACCESS, destination_pid)
        conn.send(dh)

    def recv_handle(conn):
        '''Receive a handle over a local connection.'''
        zwróć conn.recv().detach()

    klasa DupHandle(object):
        '''Picklable wrapper dla a handle.'''
        def __init__(self, handle, access, pid=Nic):
            jeżeli pid jest Nic:
                # We just duplicate the handle w the current process oraz
                # let the receiving process steal the handle.
                pid = os.getpid()
            proc = _winapi.OpenProcess(_winapi.PROCESS_DUP_HANDLE, Nieprawda, pid)
            spróbuj:
                self._handle = _winapi.DuplicateHandle(
                    _winapi.GetCurrentProcess(),
                    handle, proc, access, Nieprawda, 0)
            w_końcu:
                _winapi.CloseHandle(proc)
            self._access = access
            self._pid = pid

        def detach(self):
            '''Get the handle.  This should only be called once.'''
            # retrieve handle z process which currently owns it
            jeżeli self._pid == os.getpid():
                # The handle has already been duplicated dla this process.
                zwróć self._handle
            # We must steal the handle z the process whose pid jest self._pid.
            proc = _winapi.OpenProcess(_winapi.PROCESS_DUP_HANDLE, Nieprawda,
                                       self._pid)
            spróbuj:
                zwróć _winapi.DuplicateHandle(
                    proc, self._handle, _winapi.GetCurrentProcess(),
                    self._access, Nieprawda, _winapi.DUPLICATE_CLOSE_SOURCE)
            w_końcu:
                _winapi.CloseHandle(proc)

inaczej:
    # Unix
    __all__ += ['DupFd', 'sendfds', 'recvfds']
    zaimportuj array

    # On MacOSX we should acknowledge receipt of fds -- see Issue14669
    ACKNOWLEDGE = sys.platform == 'darwin'

    def sendfds(sock, fds):
        '''Send an array of fds over an AF_UNIX socket.'''
        fds = array.array('i', fds)
        msg = bytes([len(fds) % 256])
        sock.sendmsg([msg], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, fds)])
        jeżeli ACKNOWLEDGE oraz sock.recv(1) != b'A':
            podnieś RuntimeError('did nie receive acknowledgement of fd')

    def recvfds(sock, size):
        '''Receive an array of fds over an AF_UNIX socket.'''
        a = array.array('i')
        bytes_size = a.itemsize * size
        msg, ancdata, flags, addr = sock.recvmsg(1, socket.CMSG_LEN(bytes_size))
        jeżeli nie msg oraz nie ancdata:
            podnieś EOFError
        spróbuj:
            jeżeli ACKNOWLEDGE:
                sock.send(b'A')
            jeżeli len(ancdata) != 1:
                podnieś RuntimeError('received %d items of ancdata' %
                                   len(ancdata))
            cmsg_level, cmsg_type, cmsg_data = ancdata[0]
            jeżeli (cmsg_level == socket.SOL_SOCKET oraz
                cmsg_type == socket.SCM_RIGHTS):
                jeżeli len(cmsg_data) % a.itemsize != 0:
                    podnieś ValueError
                a.frombytes(cmsg_data)
                assert len(a) % 256 == msg[0]
                zwróć list(a)
        wyjąwszy (ValueError, IndexError):
            dalej
        podnieś RuntimeError('Invalid data received')

    def send_handle(conn, handle, destination_pid):
        '''Send a handle over a local connection.'''
        przy socket.fromfd(conn.fileno(), socket.AF_UNIX, socket.SOCK_STREAM) jako s:
            sendfds(s, [handle])

    def recv_handle(conn):
        '''Receive a handle over a local connection.'''
        przy socket.fromfd(conn.fileno(), socket.AF_UNIX, socket.SOCK_STREAM) jako s:
            zwróć recvfds(s, 1)[0]

    def DupFd(fd):
        '''Return a wrapper dla an fd.'''
        popen_obj = context.get_spawning_popen()
        jeżeli popen_obj jest nie Nic:
            zwróć popen_obj.DupFd(popen_obj.duplicate_for_child(fd))
        albo_inaczej HAVE_SEND_HANDLE:
            z . zaimportuj resource_sharer
            zwróć resource_sharer.DupFd(fd)
        inaczej:
            podnieś ValueError('SCM_RIGHTS appears nie to be available')

#
# Try making some callable types picklable
#

def _reduce_method(m):
    jeżeli m.__self__ jest Nic:
        zwróć getattr, (m.__class__, m.__func__.__name__)
    inaczej:
        zwróć getattr, (m.__self__, m.__func__.__name__)
klasa _C:
    def f(self):
        dalej
register(type(_C().f), _reduce_method)


def _reduce_method_descriptor(m):
    zwróć getattr, (m.__objclass__, m.__name__)
register(type(list.append), _reduce_method_descriptor)
register(type(int.__add__), _reduce_method_descriptor)


def _reduce_partial(p):
    zwróć _rebuild_partial, (p.func, p.args, p.keywords albo {})
def _rebuild_partial(func, args, keywords):
    zwróć functools.partial(func, *args, **keywords)
register(functools.partial, _reduce_partial)

#
# Make sockets picklable
#

jeżeli sys.platform == 'win32':
    def _reduce_socket(s):
        z .resource_sharer zaimportuj DupSocket
        zwróć _rebuild_socket, (DupSocket(s),)
    def _rebuild_socket(ds):
        zwróć ds.detach()
    register(socket.socket, _reduce_socket)

inaczej:
    def _reduce_socket(s):
        df = DupFd(s.fileno())
        zwróć _rebuild_socket, (df, s.family, s.type, s.proto)
    def _rebuild_socket(df, family, type, proto):
        fd = df.detach()
        zwróć socket.socket(family, type, proto, fileno=fd)
    register(socket.socket, _reduce_socket)
