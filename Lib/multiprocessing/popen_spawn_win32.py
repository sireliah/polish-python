zaimportuj os
zaimportuj msvcrt
zaimportuj signal
zaimportuj sys
zaimportuj _winapi

z . zaimportuj context
z . zaimportuj spawn
z . zaimportuj reduction
z . zaimportuj util

__all__ = ['Popen']

#
#
#

TERMINATE = 0x10000
WINEXE = (sys.platform == 'win32' oraz getattr(sys, 'frozen', Nieprawda))
WINSERVICE = sys.executable.lower().endswith("pythonservice.exe")

#
# We define a Popen klasa similar to the one z subprocess, but
# whose constructor takes a process object jako its argument.
#

klasa Popen(object):
    '''
    Start a subprocess to run the code of a process object
    '''
    method = 'spawn'

    def __init__(self, process_obj):
        prep_data = spawn.get_preparation_data(process_obj._name)

        # read end of pipe will be "stolen" by the child process
        # -- see spawn_main() w spawn.py.
        rhandle, whandle = _winapi.CreatePipe(Nic, 0)
        wfd = msvcrt.open_osfhandle(whandle, 0)
        cmd = spawn.get_command_line(parent_pid=os.getpid(),
                                     pipe_handle=rhandle)
        cmd = ' '.join('"%s"' % x dla x w cmd)

        przy open(wfd, 'wb', closefd=Prawda) jako to_child:
            # start process
            spróbuj:
                hp, ht, pid, tid = _winapi.CreateProcess(
                    spawn.get_executable(), cmd,
                    Nic, Nic, Nieprawda, 0, Nic, Nic, Nic)
                _winapi.CloseHandle(ht)
            wyjąwszy:
                _winapi.CloseHandle(rhandle)
                podnieś

            # set attributes of self
            self.pid = pid
            self.returncode = Nic
            self._handle = hp
            self.sentinel = int(hp)
            util.Finalize(self, _winapi.CloseHandle, (self.sentinel,))

            # send information to child
            context.set_spawning_popen(self)
            spróbuj:
                reduction.dump(prep_data, to_child)
                reduction.dump(process_obj, to_child)
            w_końcu:
                context.set_spawning_popen(Nic)

    def duplicate_for_child(self, handle):
        assert self jest context.get_spawning_popen()
        zwróć reduction.duplicate(handle, self.sentinel)

    def wait(self, timeout=Nic):
        jeżeli self.returncode jest Nic:
            jeżeli timeout jest Nic:
                msecs = _winapi.INFINITE
            inaczej:
                msecs = max(0, int(timeout * 1000 + 0.5))

            res = _winapi.WaitForSingleObject(int(self._handle), msecs)
            jeżeli res == _winapi.WAIT_OBJECT_0:
                code = _winapi.GetExitCodeProcess(self._handle)
                jeżeli code == TERMINATE:
                    code = -signal.SIGTERM
                self.returncode = code

        zwróć self.returncode

    def poll(self):
        zwróć self.wait(timeout=0)

    def terminate(self):
        jeżeli self.returncode jest Nic:
            spróbuj:
                _winapi.TerminateProcess(int(self._handle), TERMINATE)
            wyjąwszy OSError:
                jeżeli self.wait(timeout=1.0) jest Nic:
                    podnieś
