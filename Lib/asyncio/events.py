"""Event loop oraz event loop policy."""

__all__ = ['AbstractEventLoopPolicy',
           'AbstractEventLoop', 'AbstractServer',
           'Handle', 'TimerHandle',
           'get_event_loop_policy', 'set_event_loop_policy',
           'get_event_loop', 'set_event_loop', 'new_event_loop',
           'get_child_watcher', 'set_child_watcher',
           ]

zaimportuj functools
zaimportuj inspect
zaimportuj reprlib
zaimportuj socket
zaimportuj subprocess
zaimportuj sys
zaimportuj threading
zaimportuj traceback

z asyncio zaimportuj compat


def _get_function_source(func):
    jeżeli compat.PY34:
        func = inspect.unwrap(func)
    albo_inaczej hasattr(func, '__wrapped__'):
        func = func.__wrapped__
    jeżeli inspect.isfunction(func):
        code = func.__code__
        zwróć (code.co_filename, code.co_firstlineno)
    jeżeli isinstance(func, functools.partial):
        zwróć _get_function_source(func.func)
    jeżeli compat.PY34 oraz isinstance(func, functools.partialmethod):
        zwróć _get_function_source(func.func)
    zwróć Nic


def _format_args(args):
    """Format function arguments.

    Special case dla a single parameter: ('hello',) jest formatted jako ('hello').
    """
    # use reprlib to limit the length of the output
    args_repr = reprlib.repr(args)
    jeżeli len(args) == 1 oraz args_repr.endswith(',)'):
        args_repr = args_repr[:-2] + ')'
    zwróć args_repr


def _format_callback(func, args, suffix=''):
    jeżeli isinstance(func, functools.partial):
        jeżeli args jest nie Nic:
            suffix = _format_args(args) + suffix
        zwróć _format_callback(func.func, func.args, suffix)

    jeżeli hasattr(func, '__qualname__'):
        func_repr = getattr(func, '__qualname__')
    albo_inaczej hasattr(func, '__name__'):
        func_repr = getattr(func, '__name__')
    inaczej:
        func_repr = repr(func)

    jeżeli args jest nie Nic:
        func_repr += _format_args(args)
    jeżeli suffix:
        func_repr += suffix
    zwróć func_repr

def _format_callback_source(func, args):
    func_repr = _format_callback(func, args)
    source = _get_function_source(func)
    jeżeli source:
        func_repr += ' at %s:%s' % source
    zwróć func_repr


klasa Handle:
    """Object returned by callback registration methods."""

    __slots__ = ('_callback', '_args', '_cancelled', '_loop',
                 '_source_traceback', '_repr', '__weakref__')

    def __init__(self, callback, args, loop):
        assert nie isinstance(callback, Handle), 'A Handle jest nie a callback'
        self._loop = loop
        self._callback = callback
        self._args = args
        self._cancelled = Nieprawda
        self._repr = Nic
        jeżeli self._loop.get_debug():
            self._source_traceback = traceback.extract_stack(sys._getframe(1))
        inaczej:
            self._source_traceback = Nic

    def _repr_info(self):
        info = [self.__class__.__name__]
        jeżeli self._cancelled:
            info.append('cancelled')
        jeżeli self._callback jest nie Nic:
            info.append(_format_callback_source(self._callback, self._args))
        jeżeli self._source_traceback:
            frame = self._source_traceback[-1]
            info.append('created at %s:%s' % (frame[0], frame[1]))
        zwróć info

    def __repr__(self):
        jeżeli self._repr jest nie Nic:
            zwróć self._repr
        info = self._repr_info()
        zwróć '<%s>' % ' '.join(info)

    def cancel(self):
        jeżeli nie self._cancelled:
            self._cancelled = Prawda
            jeżeli self._loop.get_debug():
                # Keep a representation w debug mode to keep callback oraz
                # parameters. For example, to log the warning
                # "Executing <Handle...> took 2.5 second"
                self._repr = repr(self)
            self._callback = Nic
            self._args = Nic

    def _run(self):
        spróbuj:
            self._callback(*self._args)
        wyjąwszy Exception jako exc:
            cb = _format_callback_source(self._callback, self._args)
            msg = 'Exception w callback {}'.format(cb)
            context = {
                'message': msg,
                'exception': exc,
                'handle': self,
            }
            jeżeli self._source_traceback:
                context['source_traceback'] = self._source_traceback
            self._loop.call_exception_handler(context)
        self = Nic  # Needed to przerwij cycles when an exception occurs.


klasa TimerHandle(Handle):
    """Object returned by timed callback registration methods."""

    __slots__ = ['_scheduled', '_when']

    def __init__(self, when, callback, args, loop):
        assert when jest nie Nic
        super().__init__(callback, args, loop)
        jeżeli self._source_traceback:
            usuń self._source_traceback[-1]
        self._when = when
        self._scheduled = Nieprawda

    def _repr_info(self):
        info = super()._repr_info()
        pos = 2 jeżeli self._cancelled inaczej 1
        info.insert(pos, 'when=%s' % self._when)
        zwróć info

    def __hash__(self):
        zwróć hash(self._when)

    def __lt__(self, other):
        zwróć self._when < other._when

    def __le__(self, other):
        jeżeli self._when < other._when:
            zwróć Prawda
        zwróć self.__eq__(other)

    def __gt__(self, other):
        zwróć self._when > other._when

    def __ge__(self, other):
        jeżeli self._when > other._when:
            zwróć Prawda
        zwróć self.__eq__(other)

    def __eq__(self, other):
        jeżeli isinstance(other, TimerHandle):
            zwróć (self._when == other._when oraz
                    self._callback == other._callback oraz
                    self._args == other._args oraz
                    self._cancelled == other._cancelled)
        zwróć NotImplemented

    def __ne__(self, other):
        equal = self.__eq__(other)
        zwróć NotImplemented jeżeli equal jest NotImplemented inaczej nie equal

    def cancel(self):
        jeżeli nie self._cancelled:
            self._loop._timer_handle_cancelled(self)
        super().cancel()


klasa AbstractServer:
    """Abstract server returned by create_server()."""

    def close(self):
        """Stop serving.  This leaves existing connections open."""
        zwróć NotImplemented

    def wait_closed(self):
        """Coroutine to wait until service jest closed."""
        zwróć NotImplemented


klasa AbstractEventLoop:
    """Abstract event loop."""

    # Running oraz stopping the event loop.

    def run_forever(self):
        """Run the event loop until stop() jest called."""
        podnieś NotImplementedError

    def run_until_complete(self, future):
        """Run the event loop until a Future jest done.

        Return the Future's result, albo podnieś its exception.
        """
        podnieś NotImplementedError

    def stop(self):
        """Stop the event loop jako soon jako reasonable.

        Exactly how soon that jest may depend on the implementation, but
        no more I/O callbacks should be scheduled.
        """
        podnieś NotImplementedError

    def is_running(self):
        """Return whether the event loop jest currently running."""
        podnieś NotImplementedError

    def is_closed(self):
        """Returns Prawda jeżeli the event loop was closed."""
        podnieś NotImplementedError

    def close(self):
        """Close the loop.

        The loop should nie be running.

        This jest idempotent oraz irreversible.

        No other methods should be called after this one.
        """
        podnieś NotImplementedError

    # Methods scheduling callbacks.  All these zwróć Handles.

    def _timer_handle_cancelled(self, handle):
        """Notification that a TimerHandle has been cancelled."""
        podnieś NotImplementedError

    def call_soon(self, callback, *args):
        zwróć self.call_later(0, callback, *args)

    def call_later(self, delay, callback, *args):
        podnieś NotImplementedError

    def call_at(self, when, callback, *args):
        podnieś NotImplementedError

    def time(self):
        podnieś NotImplementedError

    # Method scheduling a coroutine object: create a task.

    def create_task(self, coro):
        podnieś NotImplementedError

    # Methods dla interacting przy threads.

    def call_soon_threadsafe(self, callback, *args):
        podnieś NotImplementedError

    def run_in_executor(self, executor, func, *args):
        podnieś NotImplementedError

    def set_default_executor(self, executor):
        podnieś NotImplementedError

    # Network I/O methods returning Futures.

    def getaddrinfo(self, host, port, *, family=0, type=0, proto=0, flags=0):
        podnieś NotImplementedError

    def getnameinfo(self, sockaddr, flags=0):
        podnieś NotImplementedError

    def create_connection(self, protocol_factory, host=Nic, port=Nic, *,
                          ssl=Nic, family=0, proto=0, flags=0, sock=Nic,
                          local_addr=Nic, server_hostname=Nic):
        podnieś NotImplementedError

    def create_server(self, protocol_factory, host=Nic, port=Nic, *,
                      family=socket.AF_UNSPEC, flags=socket.AI_PASSIVE,
                      sock=Nic, backlog=100, ssl=Nic, reuse_address=Nic):
        """A coroutine which creates a TCP server bound to host oraz port.

        The zwróć value jest a Server object which can be used to stop
        the service.

        If host jest an empty string albo Nic all interfaces are assumed
        oraz a list of multiple sockets will be returned (most likely
        one dla IPv4 oraz another one dla IPv6).

        family can be set to either AF_INET albo AF_INET6 to force the
        socket to use IPv4 albo IPv6. If nie set it will be determined
        z host (defaults to AF_UNSPEC).

        flags jest a bitmask dla getaddrinfo().

        sock can optionally be specified w order to use a preexisting
        socket object.

        backlog jest the maximum number of queued connections dalejed to
        listen() (defaults to 100).

        ssl can be set to an SSLContext to enable SSL over the
        accepted connections.

        reuse_address tells the kernel to reuse a local socket w
        TIME_WAIT state, without waiting dla its natural timeout to
        expire. If nie specified will automatically be set to Prawda on
        UNIX.
        """
        podnieś NotImplementedError

    def create_unix_connection(self, protocol_factory, path, *,
                               ssl=Nic, sock=Nic,
                               server_hostname=Nic):
        podnieś NotImplementedError

    def create_unix_server(self, protocol_factory, path, *,
                           sock=Nic, backlog=100, ssl=Nic):
        """A coroutine which creates a UNIX Domain Socket server.

        The zwróć value jest a Server object, which can be used to stop
        the service.

        path jest a str, representing a file systsem path to bind the
        server socket to.

        sock can optionally be specified w order to use a preexisting
        socket object.

        backlog jest the maximum number of queued connections dalejed to
        listen() (defaults to 100).

        ssl can be set to an SSLContext to enable SSL over the
        accepted connections.
        """
        podnieś NotImplementedError

    def create_datagram_endpoint(self, protocol_factory,
                                 local_addr=Nic, remote_addr=Nic, *,
                                 family=0, proto=0, flags=0):
        podnieś NotImplementedError

    # Pipes oraz subprocesses.

    def connect_read_pipe(self, protocol_factory, pipe):
        """Register read pipe w event loop. Set the pipe to non-blocking mode.

        protocol_factory should instantiate object przy Protocol interface.
        pipe jest a file-like object.
        Return pair (transport, protocol), where transport supports the
        ReadTransport interface."""
        # The reason to accept file-like object instead of just file descriptor
        # is: we need to own pipe oraz close it at transport finishing
        # Can got complicated errors jeżeli dalej f.fileno(),
        # close fd w pipe transport then close f oraz vise versa.
        podnieś NotImplementedError

    def connect_write_pipe(self, protocol_factory, pipe):
        """Register write pipe w event loop.

        protocol_factory should instantiate object przy BaseProtocol interface.
        Pipe jest file-like object already switched to nonblocking.
        Return pair (transport, protocol), where transport support
        WriteTransport interface."""
        # The reason to accept file-like object instead of just file descriptor
        # is: we need to own pipe oraz close it at transport finishing
        # Can got complicated errors jeżeli dalej f.fileno(),
        # close fd w pipe transport then close f oraz vise versa.
        podnieś NotImplementedError

    def subprocess_shell(self, protocol_factory, cmd, *, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         **kwargs):
        podnieś NotImplementedError

    def subprocess_exec(self, protocol_factory, *args, stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        **kwargs):
        podnieś NotImplementedError

    # Ready-based callback registration methods.
    # The add_*() methods zwróć Nic.
    # The remove_*() methods zwróć Prawda jeżeli something was removed,
    # Nieprawda jeżeli there was nothing to delete.

    def add_reader(self, fd, callback, *args):
        podnieś NotImplementedError

    def remove_reader(self, fd):
        podnieś NotImplementedError

    def add_writer(self, fd, callback, *args):
        podnieś NotImplementedError

    def remove_writer(self, fd):
        podnieś NotImplementedError

    # Completion based I/O methods returning Futures.

    def sock_recv(self, sock, nbytes):
        podnieś NotImplementedError

    def sock_sendall(self, sock, data):
        podnieś NotImplementedError

    def sock_connect(self, sock, address):
        podnieś NotImplementedError

    def sock_accept(self, sock):
        podnieś NotImplementedError

    # Signal handling.

    def add_signal_handler(self, sig, callback, *args):
        podnieś NotImplementedError

    def remove_signal_handler(self, sig):
        podnieś NotImplementedError

    # Task factory.

    def set_task_factory(self, factory):
        podnieś NotImplementedError

    def get_task_factory(self):
        podnieś NotImplementedError

    # Error handlers.

    def set_exception_handler(self, handler):
        podnieś NotImplementedError

    def default_exception_handler(self, context):
        podnieś NotImplementedError

    def call_exception_handler(self, context):
        podnieś NotImplementedError

    # Debug flag management.

    def get_debug(self):
        podnieś NotImplementedError

    def set_debug(self, enabled):
        podnieś NotImplementedError


klasa AbstractEventLoopPolicy:
    """Abstract policy dla accessing the event loop."""

    def get_event_loop(self):
        """Get the event loop dla the current context.

        Returns an event loop object implementing the BaseEventLoop interface,
        albo podnieśs an exception w case no event loop has been set dla the
        current context oraz the current policy does nie specify to create one.

        It should never zwróć Nic."""
        podnieś NotImplementedError

    def set_event_loop(self, loop):
        """Set the event loop dla the current context to loop."""
        podnieś NotImplementedError

    def new_event_loop(self):
        """Create oraz zwróć a new event loop object according to this
        policy's rules. If there's need to set this loop jako the event loop for
        the current context, set_event_loop must be called explicitly."""
        podnieś NotImplementedError

    # Child processes handling (Unix only).

    def get_child_watcher(self):
        "Get the watcher dla child processes."
        podnieś NotImplementedError

    def set_child_watcher(self, watcher):
        """Set the watcher dla child processes."""
        podnieś NotImplementedError


klasa BaseDefaultEventLoopPolicy(AbstractEventLoopPolicy):
    """Default policy implementation dla accessing the event loop.

    In this policy, each thread has its own event loop.  However, we
    only automatically create an event loop by default dla the main
    thread; other threads by default have no event loop.

    Other policies may have different rules (e.g. a single global
    event loop, albo automatically creating an event loop per thread, albo
    using some other notion of context to which an event loop jest
    associated).
    """

    _loop_factory = Nic

    klasa _Local(threading.local):
        _loop = Nic
        _set_called = Nieprawda

    def __init__(self):
        self._local = self._Local()

    def get_event_loop(self):
        """Get the event loop.

        This may be Nic albo an instance of EventLoop.
        """
        jeżeli (self._local._loop jest Nic oraz
            nie self._local._set_called oraz
            isinstance(threading.current_thread(), threading._MainThread)):
            self.set_event_loop(self.new_event_loop())
        jeżeli self._local._loop jest Nic:
            podnieś RuntimeError('There jest no current event loop w thread %r.'
                               % threading.current_thread().name)
        zwróć self._local._loop

    def set_event_loop(self, loop):
        """Set the event loop."""
        self._local._set_called = Prawda
        assert loop jest Nic albo isinstance(loop, AbstractEventLoop)
        self._local._loop = loop

    def new_event_loop(self):
        """Create a new event loop.

        You must call set_event_loop() to make this the current event
        loop.
        """
        zwróć self._loop_factory()


# Event loop policy.  The policy itself jest always global, even jeżeli the
# policy's rules say that there jest an event loop per thread (or other
# notion of context).  The default policy jest installed by the first
# call to get_event_loop_policy().
_event_loop_policy = Nic

# Lock dla protecting the on-the-fly creation of the event loop policy.
_lock = threading.Lock()


def _init_event_loop_policy():
    global _event_loop_policy
    przy _lock:
        jeżeli _event_loop_policy jest Nic:  # pragma: no branch
            z . zaimportuj DefaultEventLoopPolicy
            _event_loop_policy = DefaultEventLoopPolicy()


def get_event_loop_policy():
    """Get the current event loop policy."""
    jeżeli _event_loop_policy jest Nic:
        _init_event_loop_policy()
    zwróć _event_loop_policy


def set_event_loop_policy(policy):
    """Set the current event loop policy.

    If policy jest Nic, the default policy jest restored."""
    global _event_loop_policy
    assert policy jest Nic albo isinstance(policy, AbstractEventLoopPolicy)
    _event_loop_policy = policy


def get_event_loop():
    """Equivalent to calling get_event_loop_policy().get_event_loop()."""
    zwróć get_event_loop_policy().get_event_loop()


def set_event_loop(loop):
    """Equivalent to calling get_event_loop_policy().set_event_loop(loop)."""
    get_event_loop_policy().set_event_loop(loop)


def new_event_loop():
    """Equivalent to calling get_event_loop_policy().new_event_loop()."""
    zwróć get_event_loop_policy().new_event_loop()


def get_child_watcher():
    """Equivalent to calling get_event_loop_policy().get_child_watcher()."""
    zwróć get_event_loop_policy().get_child_watcher()


def set_child_watcher(watcher):
    """Equivalent to calling
    get_event_loop_policy().set_child_watcher(watcher)."""
    zwróć get_event_loop_policy().set_child_watcher(watcher)
