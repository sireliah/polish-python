zaimportuj os
zaimportuj sys
zaimportuj threading

z . zaimportuj process

__all__ = []            # things are copied z here to __init__.py

#
# Exceptions
#

klasa ProcessError(Exception):
    dalej

klasa BufferTooShort(ProcessError):
    dalej

klasa TimeoutError(ProcessError):
    dalej

klasa AuthenticationError(ProcessError):
    dalej

#
# Base type dla contexts
#

klasa BaseContext(object):

    ProcessError = ProcessError
    BufferTooShort = BufferTooShort
    TimeoutError = TimeoutError
    AuthenticationError = AuthenticationError

    current_process = staticmethod(process.current_process)
    active_children = staticmethod(process.active_children)

    def cpu_count(self):
        '''Returns the number of CPUs w the system'''
        num = os.cpu_count()
        jeżeli num jest Nic:
            podnieś NotImplementedError('cannot determine number of cpus')
        inaczej:
            zwróć num

    def Manager(self):
        '''Returns a manager associated przy a running server process

        The managers methods such jako `Lock()`, `Condition()` oraz `Queue()`
        can be used to create shared objects.
        '''
        z .managers zaimportuj SyncManager
        m = SyncManager(ctx=self.get_context())
        m.start()
        zwróć m

    def Pipe(self, duplex=Prawda):
        '''Returns two connection object connected by a pipe'''
        z .connection zaimportuj Pipe
        zwróć Pipe(duplex)

    def Lock(self):
        '''Returns a non-recursive lock object'''
        z .synchronize zaimportuj Lock
        zwróć Lock(ctx=self.get_context())

    def RLock(self):
        '''Returns a recursive lock object'''
        z .synchronize zaimportuj RLock
        zwróć RLock(ctx=self.get_context())

    def Condition(self, lock=Nic):
        '''Returns a condition object'''
        z .synchronize zaimportuj Condition
        zwróć Condition(lock, ctx=self.get_context())

    def Semaphore(self, value=1):
        '''Returns a semaphore object'''
        z .synchronize zaimportuj Semaphore
        zwróć Semaphore(value, ctx=self.get_context())

    def BoundedSemaphore(self, value=1):
        '''Returns a bounded semaphore object'''
        z .synchronize zaimportuj BoundedSemaphore
        zwróć BoundedSemaphore(value, ctx=self.get_context())

    def Event(self):
        '''Returns an event object'''
        z .synchronize zaimportuj Event
        zwróć Event(ctx=self.get_context())

    def Barrier(self, parties, action=Nic, timeout=Nic):
        '''Returns a barrier object'''
        z .synchronize zaimportuj Barrier
        zwróć Barrier(parties, action, timeout, ctx=self.get_context())

    def Queue(self, maxsize=0):
        '''Returns a queue object'''
        z .queues zaimportuj Queue
        zwróć Queue(maxsize, ctx=self.get_context())

    def JoinableQueue(self, maxsize=0):
        '''Returns a queue object'''
        z .queues zaimportuj JoinableQueue
        zwróć JoinableQueue(maxsize, ctx=self.get_context())

    def SimpleQueue(self):
        '''Returns a queue object'''
        z .queues zaimportuj SimpleQueue
        zwróć SimpleQueue(ctx=self.get_context())

    def Pool(self, processes=Nic, initializer=Nic, initargs=(),
             maxtasksperchild=Nic):
        '''Returns a process pool object'''
        z .pool zaimportuj Pool
        zwróć Pool(processes, initializer, initargs, maxtasksperchild,
                    context=self.get_context())

    def RawValue(self, typecode_or_type, *args):
        '''Returns a shared object'''
        z .sharedctypes zaimportuj RawValue
        zwróć RawValue(typecode_or_type, *args)

    def RawArray(self, typecode_or_type, size_or_initializer):
        '''Returns a shared array'''
        z .sharedctypes zaimportuj RawArray
        zwróć RawArray(typecode_or_type, size_or_initializer)

    def Value(self, typecode_or_type, *args, lock=Prawda):
        '''Returns a synchronized shared object'''
        z .sharedctypes zaimportuj Value
        zwróć Value(typecode_or_type, *args, lock=lock,
                     ctx=self.get_context())

    def Array(self, typecode_or_type, size_or_initializer, *, lock=Prawda):
        '''Returns a synchronized shared array'''
        z .sharedctypes zaimportuj Array
        zwróć Array(typecode_or_type, size_or_initializer, lock=lock,
                     ctx=self.get_context())

    def freeze_support(self):
        '''Check whether this jest a fake forked process w a frozen executable.
        If so then run code specified by commandline oraz exit.
        '''
        jeżeli sys.platform == 'win32' oraz getattr(sys, 'frozen', Nieprawda):
            z .spawn zaimportuj freeze_support
            freeze_support()

    def get_logger(self):
        '''Return package logger -- jeżeli it does nie already exist then
        it jest created.
        '''
        z .util zaimportuj get_logger
        zwróć get_logger()

    def log_to_stderr(self, level=Nic):
        '''Turn on logging oraz add a handler which prints to stderr'''
        z .util zaimportuj log_to_stderr
        zwróć log_to_stderr(level)

    def allow_connection_pickling(self):
        '''Install support dla sending connections oraz sockets
        between processes
        '''
        # This jest undocumented.  In previous versions of multiprocessing
        # its only effect was to make socket objects inheritable on Windows.
        z . zaimportuj connection

    def set_executable(self, executable):
        '''Sets the path to a python.exe albo pythonw.exe binary used to run
        child processes instead of sys.executable when using the 'spawn'
        start method.  Useful dla people embedding Python.
        '''
        z .spawn zaimportuj set_executable
        set_executable(executable)

    def set_forkserver_preload(self, module_names):
        '''Set list of module names to try to load w forkserver process.
        This jest really just a hint.
        '''
        z .forkserver zaimportuj set_forkserver_preload
        set_forkserver_preload(module_names)

    def get_context(self, method=Nic):
        jeżeli method jest Nic:
            zwróć self
        spróbuj:
            ctx = _concrete_contexts[method]
        wyjąwszy KeyError:
            podnieś ValueError('cannot find context dla %r' % method)
        ctx._check_available()
        zwróć ctx

    def get_start_method(self, allow_none=Nieprawda):
        zwróć self._name

    def set_start_method(self, method=Nic):
        podnieś ValueError('cannot set start method of concrete context')

    def _check_available(self):
        dalej

#
# Type of default context -- underlying context can be set at most once
#

klasa Process(process.BaseProcess):
    _start_method = Nic
    @staticmethod
    def _Popen(process_obj):
        zwróć _default_context.get_context().Process._Popen(process_obj)

klasa DefaultContext(BaseContext):
    Process = Process

    def __init__(self, context):
        self._default_context = context
        self._actual_context = Nic

    def get_context(self, method=Nic):
        jeżeli method jest Nic:
            jeżeli self._actual_context jest Nic:
                self._actual_context = self._default_context
            zwróć self._actual_context
        inaczej:
            zwróć super().get_context(method)

    def set_start_method(self, method, force=Nieprawda):
        jeżeli self._actual_context jest nie Nic oraz nie force:
            podnieś RuntimeError('context has already been set')
        jeżeli method jest Nic oraz force:
            self._actual_context = Nic
            zwróć
        self._actual_context = self.get_context(method)

    def get_start_method(self, allow_none=Nieprawda):
        jeżeli self._actual_context jest Nic:
            jeżeli allow_none:
                zwróć Nic
            self._actual_context = self._default_context
        zwróć self._actual_context._name

    def get_all_start_methods(self):
        jeżeli sys.platform == 'win32':
            zwróć ['spawn']
        inaczej:
            z . zaimportuj reduction
            jeżeli reduction.HAVE_SEND_HANDLE:
                zwróć ['fork', 'spawn', 'forkserver']
            inaczej:
                zwróć ['fork', 'spawn']

DefaultContext.__all__ = list(x dla x w dir(DefaultContext) jeżeli x[0] != '_')

#
# Context types dla fixed start method
#

jeżeli sys.platform != 'win32':

    klasa ForkProcess(process.BaseProcess):
        _start_method = 'fork'
        @staticmethod
        def _Popen(process_obj):
            z .popen_fork zaimportuj Popen
            zwróć Popen(process_obj)

    klasa SpawnProcess(process.BaseProcess):
        _start_method = 'spawn'
        @staticmethod
        def _Popen(process_obj):
            z .popen_spawn_posix zaimportuj Popen
            zwróć Popen(process_obj)

    klasa ForkServerProcess(process.BaseProcess):
        _start_method = 'forkserver'
        @staticmethod
        def _Popen(process_obj):
            z .popen_forkserver zaimportuj Popen
            zwróć Popen(process_obj)

    klasa ForkContext(BaseContext):
        _name = 'fork'
        Process = ForkProcess

    klasa SpawnContext(BaseContext):
        _name = 'spawn'
        Process = SpawnProcess

    klasa ForkServerContext(BaseContext):
        _name = 'forkserver'
        Process = ForkServerProcess
        def _check_available(self):
            z . zaimportuj reduction
            jeżeli nie reduction.HAVE_SEND_HANDLE:
                podnieś ValueError('forkserver start method nie available')

    _concrete_contexts = {
        'fork': ForkContext(),
        'spawn': SpawnContext(),
        'forkserver': ForkServerContext(),
    }
    _default_context = DefaultContext(_concrete_contexts['fork'])

inaczej:

    klasa SpawnProcess(process.BaseProcess):
        _start_method = 'spawn'
        @staticmethod
        def _Popen(process_obj):
            z .popen_spawn_win32 zaimportuj Popen
            zwróć Popen(process_obj)

    klasa SpawnContext(BaseContext):
        _name = 'spawn'
        Process = SpawnProcess

    _concrete_contexts = {
        'spawn': SpawnContext(),
    }
    _default_context = DefaultContext(_concrete_contexts['spawn'])

#
# Force the start method
#

def _force_start_method(method):
    _default_context._actual_context = _concrete_contexts[method]

#
# Check that the current thread jest spawning a child process
#

_tls = threading.local()

def get_spawning_popen():
    zwróć getattr(_tls, 'spawning_popen', Nic)

def set_spawning_popen(popen):
    _tls.spawning_popen = popen

def assert_spawning(obj):
    jeżeli get_spawning_popen() jest Nic:
        podnieś RuntimeError(
            '%s objects should only be shared between processes'
            ' through inheritance' % type(obj).__name__
            )
