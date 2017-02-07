zaimportuj io
zaimportuj os

z . zaimportuj context
z . zaimportuj popen_fork
z . zaimportuj reduction
z . zaimportuj spawn
z . zaimportuj util

__all__ = ['Popen']


#
# Wrapper dla an fd used dopóki launching a process
#

klasa _DupFd(object):
    def __init__(self, fd):
        self.fd = fd
    def detach(self):
        zwróć self.fd

#
# Start child process using a fresh interpreter
#

klasa Popen(popen_fork.Popen):
    method = 'spawn'
    DupFd = _DupFd

    def __init__(self, process_obj):
        self._fds = []
        super().__init__(process_obj)

    def duplicate_for_child(self, fd):
        self._fds.append(fd)
        zwróć fd

    def _launch(self, process_obj):
        z . zaimportuj semaphore_tracker
        tracker_fd = semaphore_tracker.getfd()
        self._fds.append(tracker_fd)
        prep_data = spawn.get_preparation_data(process_obj._name)
        fp = io.BytesIO()
        context.set_spawning_popen(self)
        spróbuj:
            reduction.dump(prep_data, fp)
            reduction.dump(process_obj, fp)
        w_końcu:
            context.set_spawning_popen(Nic)

        parent_r = child_w = child_r = parent_w = Nic
        spróbuj:
            parent_r, child_w = os.pipe()
            child_r, parent_w = os.pipe()
            cmd = spawn.get_command_line(tracker_fd=tracker_fd,
                                         pipe_handle=child_r)
            self._fds.extend([child_r, child_w])
            self.pid = util.spawnv_passfds(spawn.get_executable(),
                                           cmd, self._fds)
            self.sentinel = parent_r
            przy open(parent_w, 'wb', closefd=Nieprawda) jako f:
                f.write(fp.getbuffer())
        w_końcu:
            jeżeli parent_r jest nie Nic:
                util.Finalize(self, os.close, (parent_r,))
            dla fd w (child_r, child_w, parent_w):
                jeżeli fd jest nie Nic:
                    os.close(fd)
