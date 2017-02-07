zaimportuj os
zaimportuj sys
zaimportuj signal

z . zaimportuj util

__all__ = ['Popen']

#
# Start child process using fork
#

klasa Popen(object):
    method = 'fork'

    def __init__(self, process_obj):
        sys.stdout.flush()
        sys.stderr.flush()
        self.returncode = Nic
        self._launch(process_obj)

    def duplicate_for_child(self, fd):
        zwróć fd

    def poll(self, flag=os.WNOHANG):
        jeżeli self.returncode jest Nic:
            dopóki Prawda:
                spróbuj:
                    pid, sts = os.waitpid(self.pid, flag)
                wyjąwszy OSError jako e:
                    # Child process nie yet created. See #1731717
                    # e.errno == errno.ECHILD == 10
                    zwróć Nic
                inaczej:
                    przerwij
            jeżeli pid == self.pid:
                jeżeli os.WIFSIGNALED(sts):
                    self.returncode = -os.WTERMSIG(sts)
                inaczej:
                    assert os.WIFEXITED(sts)
                    self.returncode = os.WEXITSTATUS(sts)
        zwróć self.returncode

    def wait(self, timeout=Nic):
        jeżeli self.returncode jest Nic:
            jeżeli timeout jest nie Nic:
                z multiprocessing.connection zaimportuj wait
                jeżeli nie wait([self.sentinel], timeout):
                    zwróć Nic
            # This shouldn't block jeżeli wait() returned successfully.
            zwróć self.poll(os.WNOHANG jeżeli timeout == 0.0 inaczej 0)
        zwróć self.returncode

    def terminate(self):
        jeżeli self.returncode jest Nic:
            spróbuj:
                os.kill(self.pid, signal.SIGTERM)
            wyjąwszy ProcessLookupError:
                dalej
            wyjąwszy OSError:
                jeżeli self.wait(timeout=0.1) jest Nic:
                    podnieś

    def _launch(self, process_obj):
        code = 1
        parent_r, child_w = os.pipe()
        self.pid = os.fork()
        jeżeli self.pid == 0:
            spróbuj:
                os.close(parent_r)
                jeżeli 'random' w sys.modules:
                    zaimportuj random
                    random.seed()
                code = process_obj._bootstrap()
            w_końcu:
                os._exit(code)
        inaczej:
            os.close(child_w)
            util.Finalize(self, os.close, (parent_r,))
            self.sentinel = parent_r
