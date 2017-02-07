#
# On Unix we run a server process which keeps track of unlinked
# semaphores. The server ignores SIGINT oraz SIGTERM oraz reads z a
# pipe.  Every other process of the program has a copy of the writable
# end of the pipe, so we get EOF when all other processes have exited.
# Then the server process unlinks any remaining semaphore names.
#
# This jest important because the system only supports a limited number
# of named semaphores, oraz they will nie be automatically removed till
# the next reboot.  Without this semaphore tracker process, "killall
# python" would probably leave unlinked semaphores.
#

zaimportuj os
zaimportuj signal
zaimportuj sys
zaimportuj threading
zaimportuj warnings
zaimportuj _multiprocessing

z . zaimportuj spawn
z . zaimportuj util

__all__ = ['ensure_running', 'register', 'unregister']


klasa SemaphoreTracker(object):

    def __init__(self):
        self._lock = threading.Lock()
        self._fd = Nic

    def getfd(self):
        self.ensure_running()
        zwróć self._fd

    def ensure_running(self):
        '''Make sure that semaphore tracker process jest running.

        This can be run z any process.  Usually a child process will use
        the semaphore created by its parent.'''
        przy self._lock:
            jeżeli self._fd jest nie Nic:
                zwróć
            fds_to_pass = []
            spróbuj:
                fds_to_pass.append(sys.stderr.fileno())
            wyjąwszy Exception:
                dalej
            cmd = 'z multiprocessing.semaphore_tracker zaimportuj main;main(%d)'
            r, w = os.pipe()
            spróbuj:
                fds_to_pass.append(r)
                # process will out live us, so no need to wait on pid
                exe = spawn.get_executable()
                args = [exe] + util._args_from_interpreter_flags()
                args += ['-c', cmd % r]
                util.spawnv_passfds(exe, args, fds_to_pass)
            wyjąwszy:
                os.close(w)
                podnieś
            inaczej:
                self._fd = w
            w_końcu:
                os.close(r)

    def register(self, name):
        '''Register name of semaphore przy semaphore tracker.'''
        self._send('REGISTER', name)

    def unregister(self, name):
        '''Unregister name of semaphore przy semaphore tracker.'''
        self._send('UNREGISTER', name)

    def _send(self, cmd, name):
        self.ensure_running()
        msg = '{0}:{1}\n'.format(cmd, name).encode('ascii')
        jeżeli len(name) > 512:
            # posix guarantees that writes to a pipe of less than PIPE_BUF
            # bytes are atomic, oraz that PIPE_BUF >= 512
            podnieś ValueError('name too long')
        nbytes = os.write(self._fd, msg)
        assert nbytes == len(msg)


_semaphore_tracker = SemaphoreTracker()
ensure_running = _semaphore_tracker.ensure_running
register = _semaphore_tracker.register
unregister = _semaphore_tracker.unregister
getfd = _semaphore_tracker.getfd


def main(fd):
    '''Run semaphore tracker.'''
    # protect the process z ^C oraz "killall python" etc
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)

    dla f w (sys.stdin, sys.stdout):
        spróbuj:
            f.close()
        wyjąwszy Exception:
            dalej

    cache = set()
    spróbuj:
        # keep track of registered/unregistered semaphores
        przy open(fd, 'rb') jako f:
            dla line w f:
                spróbuj:
                    cmd, name = line.strip().split(b':')
                    jeżeli cmd == b'REGISTER':
                        cache.add(name)
                    albo_inaczej cmd == b'UNREGISTER':
                        cache.remove(name)
                    inaczej:
                        podnieś RuntimeError('unrecognized command %r' % cmd)
                wyjąwszy Exception:
                    spróbuj:
                        sys.excepthook(*sys.exc_info())
                    wyjąwszy:
                        dalej
    w_końcu:
        # all processes have terminated; cleanup any remaining semaphores
        jeżeli cache:
            spróbuj:
                warnings.warn('semaphore_tracker: There appear to be %d '
                              'leaked semaphores to clean up at shutdown' %
                              len(cache))
            wyjąwszy Exception:
                dalej
        dla name w cache:
            # For some reason the process which created oraz registered this
            # semaphore has failed to unregister it. Presumably it has died.
            # We therefore unlink it.
            spróbuj:
                name = name.decode('ascii')
                spróbuj:
                    _multiprocessing.sem_unlink(name)
                wyjąwszy Exception jako e:
                    warnings.warn('semaphore_tracker: %r: %s' % (name, e))
            w_końcu:
                dalej
