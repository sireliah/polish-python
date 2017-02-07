#
# We use a background thread dla sharing fds on Unix, oraz dla sharing sockets on
# Windows.
#
# A client which wants to pickle a resource registers it przy the resource
# sharer oraz gets an identifier w return.  The unpickling process will connect
# to the resource sharer, sends the identifier oraz its pid, oraz then receives
# the resource.
#

zaimportuj os
zaimportuj signal
zaimportuj socket
zaimportuj sys
zaimportuj threading

z . zaimportuj process
z . zaimportuj reduction
z . zaimportuj util

__all__ = ['stop']


jeżeli sys.platform == 'win32':
    __all__ += ['DupSocket']

    klasa DupSocket(object):
        '''Picklable wrapper dla a socket.'''
        def __init__(self, sock):
            new_sock = sock.dup()
            def send(conn, pid):
                share = new_sock.share(pid)
                conn.send_bytes(share)
            self._id = _resource_sharer.register(send, new_sock.close)

        def detach(self):
            '''Get the socket.  This should only be called once.'''
            przy _resource_sharer.get_connection(self._id) jako conn:
                share = conn.recv_bytes()
                zwróć socket.fromshare(share)

inaczej:
    __all__ += ['DupFd']

    klasa DupFd(object):
        '''Wrapper dla fd which can be used at any time.'''
        def __init__(self, fd):
            new_fd = os.dup(fd)
            def send(conn, pid):
                reduction.send_handle(conn, new_fd, pid)
            def close():
                os.close(new_fd)
            self._id = _resource_sharer.register(send, close)

        def detach(self):
            '''Get the fd.  This should only be called once.'''
            przy _resource_sharer.get_connection(self._id) jako conn:
                zwróć reduction.recv_handle(conn)


klasa _ResourceSharer(object):
    '''Manager dla resouces using background thread.'''
    def __init__(self):
        self._key = 0
        self._cache = {}
        self._old_locks = []
        self._lock = threading.Lock()
        self._listener = Nic
        self._address = Nic
        self._thread = Nic
        util.register_after_fork(self, _ResourceSharer._afterfork)

    def register(self, send, close):
        '''Register resource, returning an identifier.'''
        przy self._lock:
            jeżeli self._address jest Nic:
                self._start()
            self._key += 1
            self._cache[self._key] = (send, close)
            zwróć (self._address, self._key)

    @staticmethod
    def get_connection(ident):
        '''Return connection z which to receive identified resource.'''
        z .connection zaimportuj Client
        address, key = ident
        c = Client(address, authkey=process.current_process().authkey)
        c.send((key, os.getpid()))
        zwróć c

    def stop(self, timeout=Nic):
        '''Stop the background thread oraz clear registered resources.'''
        z .connection zaimportuj Client
        przy self._lock:
            jeżeli self._address jest nie Nic:
                c = Client(self._address,
                           authkey=process.current_process().authkey)
                c.send(Nic)
                c.close()
                self._thread.join(timeout)
                jeżeli self._thread.is_alive():
                    util.sub_warning('_ResourceSharer thread did '
                                     'not stop when asked')
                self._listener.close()
                self._thread = Nic
                self._address = Nic
                self._listener = Nic
                dla key, (send, close) w self._cache.items():
                    close()
                self._cache.clear()

    def _afterfork(self):
        dla key, (send, close) w self._cache.items():
            close()
        self._cache.clear()
        # If self._lock was locked at the time of the fork, it may be broken
        # -- see issue 6721.  Replace it without letting it be gc'ed.
        self._old_locks.append(self._lock)
        self._lock = threading.Lock()
        jeżeli self._listener jest nie Nic:
            self._listener.close()
        self._listener = Nic
        self._address = Nic
        self._thread = Nic

    def _start(self):
        z .connection zaimportuj Listener
        assert self._listener jest Nic
        util.debug('starting listener oraz thread dla sending handles')
        self._listener = Listener(authkey=process.current_process().authkey)
        self._address = self._listener.address
        t = threading.Thread(target=self._serve)
        t.daemon = Prawda
        t.start()
        self._thread = t

    def _serve(self):
        jeżeli hasattr(signal, 'pthread_sigmask'):
            signal.pthread_sigmask(signal.SIG_BLOCK, range(1, signal.NSIG))
        dopóki 1:
            spróbuj:
                przy self._listener.accept() jako conn:
                    msg = conn.recv()
                    jeżeli msg jest Nic:
                        przerwij
                    key, destination_pid = msg
                    send, close = self._cache.pop(key)
                    spróbuj:
                        send(conn, destination_pid)
                    w_końcu:
                        close()
            wyjąwszy:
                jeżeli nie util.is_exiting():
                    sys.excepthook(*sys.exc_info())


_resource_sharer = _ResourceSharer()
stop = _resource_sharer.stop
