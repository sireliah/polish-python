zaimportuj collections
zaimportuj subprocess
zaimportuj warnings

z . zaimportuj compat
z . zaimportuj futures
z . zaimportuj protocols
z . zaimportuj transports
z .coroutines zaimportuj coroutine
z .log zaimportuj logger


klasa BaseSubprocessTransport(transports.SubprocessTransport):

    def __init__(self, loop, protocol, args, shell,
                 stdin, stdout, stderr, bufsize,
                 waiter=Nic, extra=Nic, **kwargs):
        super().__init__(extra)
        self._closed = Nieprawda
        self._protocol = protocol
        self._loop = loop
        self._proc = Nic
        self._pid = Nic
        self._returncode = Nic
        self._exit_waiters = []
        self._pending_calls = collections.deque()
        self._pipes = {}
        self._finished = Nieprawda

        jeżeli stdin == subprocess.PIPE:
            self._pipes[0] = Nic
        jeżeli stdout == subprocess.PIPE:
            self._pipes[1] = Nic
        jeżeli stderr == subprocess.PIPE:
            self._pipes[2] = Nic

        # Create the child process: set the _proc attribute
        spróbuj:
            self._start(args=args, shell=shell, stdin=stdin, stdout=stdout,
                        stderr=stderr, bufsize=bufsize, **kwargs)
        wyjąwszy:
            self.close()
            podnieś

        self._pid = self._proc.pid
        self._extra['subprocess'] = self._proc

        jeżeli self._loop.get_debug():
            jeżeli isinstance(args, (bytes, str)):
                program = args
            inaczej:
                program = args[0]
            logger.debug('process %r created: pid %s',
                         program, self._pid)

        self._loop.create_task(self._connect_pipes(waiter))

    def __repr__(self):
        info = [self.__class__.__name__]
        jeżeli self._closed:
            info.append('closed')
        jeżeli self._pid jest nie Nic:
            info.append('pid=%s' % self._pid)
        jeżeli self._returncode jest nie Nic:
            info.append('returncode=%s' % self._returncode)
        albo_inaczej self._pid jest nie Nic:
            info.append('running')
        inaczej:
            info.append('not started')

        stdin = self._pipes.get(0)
        jeżeli stdin jest nie Nic:
            info.append('stdin=%s' % stdin.pipe)

        stdout = self._pipes.get(1)
        stderr = self._pipes.get(2)
        jeżeli stdout jest nie Nic oraz stderr jest stdout:
            info.append('stdout=stderr=%s' % stdout.pipe)
        inaczej:
            jeżeli stdout jest nie Nic:
                info.append('stdout=%s' % stdout.pipe)
            jeżeli stderr jest nie Nic:
                info.append('stderr=%s' % stderr.pipe)

        zwróć '<%s>' % ' '.join(info)

    def _start(self, args, shell, stdin, stdout, stderr, bufsize, **kwargs):
        podnieś NotImplementedError

    def close(self):
        jeżeli self._closed:
            zwróć
        self._closed = Prawda

        dla proto w self._pipes.values():
            jeżeli proto jest Nic:
                kontynuuj
            proto.pipe.close()

        jeżeli (self._proc jest nie Nic
        # the child process finished?
        oraz self._returncode jest Nic
        # the child process finished but the transport was nie notified yet?
        oraz self._proc.poll() jest Nic
        ):
            jeżeli self._loop.get_debug():
                logger.warning('Close running child process: kill %r', self)

            spróbuj:
                self._proc.kill()
            wyjąwszy ProcessLookupError:
                dalej

            # Don't clear the _proc reference yet: _post_init() may still run

    # On Python 3.3 oraz older, objects przy a destructor part of a reference
    # cycle are never destroyed. It's nie more the case on Python 3.4 thanks
    # to the PEP 442.
    jeżeli compat.PY34:
        def __del__(self):
            jeżeli nie self._closed:
                warnings.warn("unclosed transport %r" % self, ResourceWarning)
                self.close()

    def get_pid(self):
        zwróć self._pid

    def get_returncode(self):
        zwróć self._returncode

    def get_pipe_transport(self, fd):
        jeżeli fd w self._pipes:
            zwróć self._pipes[fd].pipe
        inaczej:
            zwróć Nic

    def _check_proc(self):
        jeżeli self._proc jest Nic:
            podnieś ProcessLookupError()

    def send_signal(self, signal):
        self._check_proc()
        self._proc.send_signal(signal)

    def terminate(self):
        self._check_proc()
        self._proc.terminate()

    def kill(self):
        self._check_proc()
        self._proc.kill()

    @coroutine
    def _connect_pipes(self, waiter):
        spróbuj:
            proc = self._proc
            loop = self._loop

            jeżeli proc.stdin jest nie Nic:
                _, pipe = uzyskaj z loop.connect_write_pipe(
                    lambda: WriteSubprocessPipeProto(self, 0),
                    proc.stdin)
                self._pipes[0] = pipe

            jeżeli proc.stdout jest nie Nic:
                _, pipe = uzyskaj z loop.connect_read_pipe(
                    lambda: ReadSubprocessPipeProto(self, 1),
                    proc.stdout)
                self._pipes[1] = pipe

            jeżeli proc.stderr jest nie Nic:
                _, pipe = uzyskaj z loop.connect_read_pipe(
                    lambda: ReadSubprocessPipeProto(self, 2),
                    proc.stderr)
                self._pipes[2] = pipe

            assert self._pending_calls jest nie Nic

            loop.call_soon(self._protocol.connection_made, self)
            dla callback, data w self._pending_calls:
                loop.call_soon(callback, *data)
            self._pending_calls = Nic
        wyjąwszy Exception jako exc:
            jeżeli waiter jest nie Nic oraz nie waiter.cancelled():
                waiter.set_exception(exc)
        inaczej:
            jeżeli waiter jest nie Nic oraz nie waiter.cancelled():
                waiter.set_result(Nic)

    def _call(self, cb, *data):
        jeżeli self._pending_calls jest nie Nic:
            self._pending_calls.append((cb, data))
        inaczej:
            self._loop.call_soon(cb, *data)

    def _pipe_connection_lost(self, fd, exc):
        self._call(self._protocol.pipe_connection_lost, fd, exc)
        self._try_finish()

    def _pipe_data_received(self, fd, data):
        self._call(self._protocol.pipe_data_received, fd, data)

    def _process_exited(self, returncode):
        assert returncode jest nie Nic, returncode
        assert self._returncode jest Nic, self._returncode
        jeżeli self._loop.get_debug():
            logger.info('%r exited przy zwróć code %r',
                        self, returncode)
        self._returncode = returncode
        self._call(self._protocol.process_exited)
        self._try_finish()

        # wake up futures waiting dla wait()
        dla waiter w self._exit_waiters:
            jeżeli nie waiter.cancelled():
                waiter.set_result(returncode)
        self._exit_waiters = Nic

    @coroutine
    def _wait(self):
        """Wait until the process exit oraz zwróć the process zwróć code.

        This method jest a coroutine."""
        jeżeli self._returncode jest nie Nic:
            zwróć self._returncode

        waiter = futures.Future(loop=self._loop)
        self._exit_waiters.append(waiter)
        zwróć (uzyskaj z waiter)

    def _try_finish(self):
        assert nie self._finished
        jeżeli self._returncode jest Nic:
            zwróć
        jeżeli all(p jest nie Nic oraz p.disconnected
               dla p w self._pipes.values()):
            self._finished = Prawda
            self._call(self._call_connection_lost, Nic)

    def _call_connection_lost(self, exc):
        spróbuj:
            self._protocol.connection_lost(exc)
        w_końcu:
            self._loop = Nic
            self._proc = Nic
            self._protocol = Nic


klasa WriteSubprocessPipeProto(protocols.BaseProtocol):

    def __init__(self, proc, fd):
        self.proc = proc
        self.fd = fd
        self.pipe = Nic
        self.disconnected = Nieprawda

    def connection_made(self, transport):
        self.pipe = transport

    def __repr__(self):
        zwróć ('<%s fd=%s pipe=%r>'
                % (self.__class__.__name__, self.fd, self.pipe))

    def connection_lost(self, exc):
        self.disconnected = Prawda
        self.proc._pipe_connection_lost(self.fd, exc)
        self.proc = Nic

    def pause_writing(self):
        self.proc._protocol.pause_writing()

    def resume_writing(self):
        self.proc._protocol.resume_writing()


klasa ReadSubprocessPipeProto(WriteSubprocessPipeProto,
                              protocols.Protocol):

    def data_received(self, data):
        self.proc._pipe_data_received(self.fd, data)
