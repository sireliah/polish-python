zaimportuj io
zaimportuj os

z . zaimportuj reduction
jeżeli nie reduction.HAVE_SEND_HANDLE:
    podnieś ImportError('No support dla sending fds between processes')
z . zaimportuj context
z . zaimportuj forkserver
z . zaimportuj popen_fork
z . zaimportuj spawn
z . zaimportuj util


__all__ = ['Popen']

#
# Wrapper dla an fd used dopóki launching a process
#

klasa _DupFd(object):
    def __init__(self, ind):
        self.ind = ind
    def detach(self):
        zwróć forkserver.get_inherited_fds()[self.ind]

#
# Start child process using a server process
#

klasa Popen(popen_fork.Popen):
    method = 'forkserver'
    DupFd = _DupFd

    def __init__(self, process_obj):
        self._fds = []
        super().__init__(process_obj)

    def duplicate_for_child(self, fd):
        self._fds.append(fd)
        zwróć len(self._fds) - 1

    def _launch(self, process_obj):
        prep_data = spawn.get_preparation_data(process_obj._name)
        buf = io.BytesIO()
        context.set_spawning_popen(self)
        spróbuj:
            reduction.dump(prep_data, buf)
            reduction.dump(process_obj, buf)
        w_końcu:
            context.set_spawning_popen(Nic)

        self.sentinel, w = forkserver.connect_to_new_process(self._fds)
        util.Finalize(self, os.close, (self.sentinel,))
        przy open(w, 'wb', closefd=Prawda) jako f:
            f.write(buf.getbuffer())
        self.pid = forkserver.read_unsigned(self.sentinel)

    def poll(self, flag=os.WNOHANG):
        jeżeli self.returncode jest Nic:
            z multiprocessing.connection zaimportuj wait
            timeout = 0 jeżeli flag == os.WNOHANG inaczej Nic
            jeżeli nie wait([self.sentinel], timeout):
                zwróć Nic
            spróbuj:
                self.returncode = forkserver.read_unsigned(self.sentinel)
            wyjąwszy (OSError, EOFError):
                # The process ended abnormally perhaps because of a signal
                self.returncode = 255
        zwróć self.returncode
