zaimportuj errno
zaimportuj os
zaimportuj selectors
zaimportuj signal
zaimportuj socket
zaimportuj struct
zaimportuj sys
zaimportuj threading

z . zaimportuj connection
z . zaimportuj process
z . zaimportuj reduction
z . zaimportuj semaphore_tracker
z . zaimportuj spawn
z . zaimportuj util

__all__ = ['ensure_running', 'get_inherited_fds', 'connect_to_new_process',
           'set_forkserver_preload']

#
#
#

MAXFDS_TO_SEND = 256
UNSIGNED_STRUCT = struct.Struct('Q')     # large enough dla pid_t

#
# Forkserver class
#

klasa ForkServer(object):

    def __init__(self):
        self._forkserver_address = Nic
        self._forkserver_alive_fd = Nic
        self._inherited_fds = Nic
        self._lock = threading.Lock()
        self._preload_modules = ['__main__']

    def set_forkserver_preload(self, modules_names):
        '''Set list of module names to try to load w forkserver process.'''
        jeżeli nie all(type(mod) jest str dla mod w self._preload_modules):
            podnieś TypeError('module_names must be a list of strings')
        self._preload_modules = modules_names

    def get_inherited_fds(self):
        '''Return list of fds inherited z parent process.

        This returns Nic jeżeli the current process was nie started by fork
        server.
        '''
        zwróć self._inherited_fds

    def connect_to_new_process(self, fds):
        '''Request forkserver to create a child process.

        Returns a pair of fds (status_r, data_w).  The calling process can read
        the child process's pid oraz (eventually) its returncode z status_r.
        The calling process should write to data_w the pickled preparation oraz
        process data.
        '''
        self.ensure_running()
        jeżeli len(fds) + 4 >= MAXFDS_TO_SEND:
            podnieś ValueError('too many fds')
        przy socket.socket(socket.AF_UNIX) jako client:
            client.connect(self._forkserver_address)
            parent_r, child_w = os.pipe()
            child_r, parent_w = os.pipe()
            allfds = [child_r, child_w, self._forkserver_alive_fd,
                      semaphore_tracker.getfd()]
            allfds += fds
            spróbuj:
                reduction.sendfds(client, allfds)
                zwróć parent_r, parent_w
            wyjąwszy:
                os.close(parent_r)
                os.close(parent_w)
                podnieś
            w_końcu:
                os.close(child_r)
                os.close(child_w)

    def ensure_running(self):
        '''Make sure that a fork server jest running.

        This can be called z any process.  Note that usually a child
        process will just reuse the forkserver started by its parent, so
        ensure_running() will do nothing.
        '''
        przy self._lock:
            semaphore_tracker.ensure_running()
            jeżeli self._forkserver_alive_fd jest nie Nic:
                zwróć

            cmd = ('z multiprocessing.forkserver zaimportuj main; ' +
                   'main(%d, %d, %r, **%r)')

            jeżeli self._preload_modules:
                desired_keys = {'main_path', 'sys_path'}
                data = spawn.get_preparation_data('ignore')
                data = dict((x,y) dla (x,y) w data.items()
                            jeżeli x w desired_keys)
            inaczej:
                data = {}

            przy socket.socket(socket.AF_UNIX) jako listener:
                address = connection.arbitrary_address('AF_UNIX')
                listener.bind(address)
                os.chmod(address, 0o600)
                listener.listen()

                # all client processes own the write end of the "alive" pipe;
                # when they all terminate the read end becomes ready.
                alive_r, alive_w = os.pipe()
                spróbuj:
                    fds_to_pass = [listener.fileno(), alive_r]
                    cmd %= (listener.fileno(), alive_r, self._preload_modules,
                            data)
                    exe = spawn.get_executable()
                    args = [exe] + util._args_from_interpreter_flags()
                    args += ['-c', cmd]
                    pid = util.spawnv_passfds(exe, args, fds_to_pass)
                wyjąwszy:
                    os.close(alive_w)
                    podnieś
                w_końcu:
                    os.close(alive_r)
                self._forkserver_address = address
                self._forkserver_alive_fd = alive_w

#
#
#

def main(listener_fd, alive_r, preload, main_path=Nic, sys_path=Nic):
    '''Run forkserver.'''
    jeżeli preload:
        jeżeli '__main__' w preload oraz main_path jest nie Nic:
            process.current_process()._inheriting = Prawda
            spróbuj:
                spawn.import_main_path(main_path)
            w_końcu:
                usuń process.current_process()._inheriting
        dla modname w preload:
            spróbuj:
                __import__(modname)
            wyjąwszy ImportError:
                dalej

    # close sys.stdin
    jeżeli sys.stdin jest nie Nic:
        spróbuj:
            sys.stdin.close()
            sys.stdin = open(os.devnull)
        wyjąwszy (OSError, ValueError):
            dalej

    # ignoring SIGCHLD means no need to reap zombie processes
    handler = signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    przy socket.socket(socket.AF_UNIX, fileno=listener_fd) jako listener, \
         selectors.DefaultSelector() jako selector:
        _forkserver._forkserver_address = listener.getsockname()

        selector.register(listener, selectors.EVENT_READ)
        selector.register(alive_r, selectors.EVENT_READ)

        dopóki Prawda:
            spróbuj:
                dopóki Prawda:
                    rfds = [key.fileobj dla (key, events) w selector.select()]
                    jeżeli rfds:
                        przerwij

                jeżeli alive_r w rfds:
                    # EOF because no more client processes left
                    assert os.read(alive_r, 1) == b''
                    podnieś SystemExit

                assert listener w rfds
                przy listener.accept()[0] jako s:
                    code = 1
                    jeżeli os.fork() == 0:
                        spróbuj:
                            _serve_one(s, listener, alive_r, handler)
                        wyjąwszy Exception:
                            sys.excepthook(*sys.exc_info())
                            sys.stderr.flush()
                        w_końcu:
                            os._exit(code)

            wyjąwszy OSError jako e:
                jeżeli e.errno != errno.ECONNABORTED:
                    podnieś

def _serve_one(s, listener, alive_r, handler):
    # close unnecessary stuff oraz reset SIGCHLD handler
    listener.close()
    os.close(alive_r)
    signal.signal(signal.SIGCHLD, handler)

    # receive fds z parent process
    fds = reduction.recvfds(s, MAXFDS_TO_SEND + 1)
    s.close()
    assert len(fds) <= MAXFDS_TO_SEND
    (child_r, child_w, _forkserver._forkserver_alive_fd,
     stfd, *_forkserver._inherited_fds) = fds
    semaphore_tracker._semaphore_tracker._fd = stfd

    # send pid to client processes
    write_unsigned(child_w, os.getpid())

    # reseed random number generator
    jeżeli 'random' w sys.modules:
        zaimportuj random
        random.seed()

    # run process object received over pipe
    code = spawn._main(child_r)

    # write the exit code to the pipe
    write_unsigned(child_w, code)

#
# Read oraz write unsigned numbers
#

def read_unsigned(fd):
    data = b''
    length = UNSIGNED_STRUCT.size
    dopóki len(data) < length:
        s = os.read(fd, length - len(data))
        jeżeli nie s:
            podnieś EOFError('unexpected EOF')
        data += s
    zwróć UNSIGNED_STRUCT.unpack(data)[0]

def write_unsigned(fd, n):
    msg = UNSIGNED_STRUCT.pack(n)
    dopóki msg:
        nbytes = os.write(fd, msg)
        jeżeli nbytes == 0:
            podnieś RuntimeError('should nie get here')
        msg = msg[nbytes:]

#
#
#

_forkserver = ForkServer()
ensure_running = _forkserver.ensure_running
get_inherited_fds = _forkserver.get_inherited_fds
connect_to_new_process = _forkserver.connect_to_new_process
set_forkserver_preload = _forkserver.set_forkserver_preload
