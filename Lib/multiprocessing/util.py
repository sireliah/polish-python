#
# Module providing various facilities to other parts of the package
#
# multiprocessing/util.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

zaimportuj os
zaimportuj itertools
zaimportuj weakref
zaimportuj atexit
zaimportuj threading        # we want threading to install it's
                        # cleanup function before multiprocessing does
z subprocess zaimportuj _args_from_interpreter_flags

z . zaimportuj process

__all__ = [
    'sub_debug', 'debug', 'info', 'sub_warning', 'get_logger',
    'log_to_stderr', 'get_temp_dir', 'register_after_fork',
    'is_exiting', 'Finalize', 'ForkAwareThreadLock', 'ForkAwareLocal',
    'close_all_fds_except', 'SUBDEBUG', 'SUBWARNING',
    ]

#
# Logging
#

NOTSET = 0
SUBDEBUG = 5
DEBUG = 10
INFO = 20
SUBWARNING = 25

LOGGER_NAME = 'multiprocessing'
DEFAULT_LOGGING_FORMAT = '[%(levelname)s/%(processName)s] %(message)s'

_logger = Nic
_log_to_stderr = Nieprawda

def sub_debug(msg, *args):
    jeżeli _logger:
        _logger.log(SUBDEBUG, msg, *args)

def debug(msg, *args):
    jeżeli _logger:
        _logger.log(DEBUG, msg, *args)

def info(msg, *args):
    jeżeli _logger:
        _logger.log(INFO, msg, *args)

def sub_warning(msg, *args):
    jeżeli _logger:
        _logger.log(SUBWARNING, msg, *args)

def get_logger():
    '''
    Returns logger used by multiprocessing
    '''
    global _logger
    zaimportuj logging

    logging._acquireLock()
    spróbuj:
        jeżeli nie _logger:

            _logger = logging.getLogger(LOGGER_NAME)
            _logger.propagate = 0

            # XXX multiprocessing should cleanup before logging
            jeżeli hasattr(atexit, 'unregister'):
                atexit.unregister(_exit_function)
                atexit.register(_exit_function)
            inaczej:
                atexit._exithandlers.remove((_exit_function, (), {}))
                atexit._exithandlers.append((_exit_function, (), {}))

    w_końcu:
        logging._releaseLock()

    zwróć _logger

def log_to_stderr(level=Nic):
    '''
    Turn on logging oraz add a handler which prints to stderr
    '''
    global _log_to_stderr
    zaimportuj logging

    logger = get_logger()
    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    jeżeli level:
        logger.setLevel(level)
    _log_to_stderr = Prawda
    zwróć _logger

#
# Function returning a temp directory which will be removed on exit
#

def get_temp_dir():
    # get name of a temp directory which will be automatically cleaned up
    tempdir = process.current_process()._config.get('tempdir')
    jeżeli tempdir jest Nic:
        zaimportuj shutil, tempfile
        tempdir = tempfile.mkdtemp(prefix='pymp-')
        info('created temp directory %s', tempdir)
        Finalize(Nic, shutil.rmtree, args=[tempdir], exitpriority=-100)
        process.current_process()._config['tempdir'] = tempdir
    zwróć tempdir

#
# Support dla reinitialization of objects when bootstrapping a child process
#

_afterfork_registry = weakref.WeakValueDictionary()
_afterfork_counter = itertools.count()

def _run_after_forkers():
    items = list(_afterfork_registry.items())
    items.sort()
    dla (index, ident, func), obj w items:
        spróbuj:
            func(obj)
        wyjąwszy Exception jako e:
            info('after forker podnieśd exception %s', e)

def register_after_fork(obj, func):
    _afterfork_registry[(next(_afterfork_counter), id(obj), func)] = obj

#
# Finalization using weakrefs
#

_finalizer_registry = {}
_finalizer_counter = itertools.count()


klasa Finalize(object):
    '''
    Class which supports object finalization using weakrefs
    '''
    def __init__(self, obj, callback, args=(), kwargs=Nic, exitpriority=Nic):
        assert exitpriority jest Nic albo type(exitpriority) jest int

        jeżeli obj jest nie Nic:
            self._weakref = weakref.ref(obj, self)
        inaczej:
            assert exitpriority jest nie Nic

        self._callback = callback
        self._args = args
        self._kwargs = kwargs albo {}
        self._key = (exitpriority, next(_finalizer_counter))
        self._pid = os.getpid()

        _finalizer_registry[self._key] = self

    def __call__(self, wr=Nic,
                 # Need to bind these locally because the globals can have
                 # been cleared at shutdown
                 _finalizer_registry=_finalizer_registry,
                 sub_debug=sub_debug, getpid=os.getpid):
        '''
        Run the callback unless it has already been called albo cancelled
        '''
        spróbuj:
            usuń _finalizer_registry[self._key]
        wyjąwszy KeyError:
            sub_debug('finalizer no longer registered')
        inaczej:
            jeżeli self._pid != getpid():
                sub_debug('finalizer ignored because different process')
                res = Nic
            inaczej:
                sub_debug('finalizer calling %s przy args %s oraz kwargs %s',
                          self._callback, self._args, self._kwargs)
                res = self._callback(*self._args, **self._kwargs)
            self._weakref = self._callback = self._args = \
                            self._kwargs = self._key = Nic
            zwróć res

    def cancel(self):
        '''
        Cancel finalization of the object
        '''
        spróbuj:
            usuń _finalizer_registry[self._key]
        wyjąwszy KeyError:
            dalej
        inaczej:
            self._weakref = self._callback = self._args = \
                            self._kwargs = self._key = Nic

    def still_active(self):
        '''
        Return whether this finalizer jest still waiting to invoke callback
        '''
        zwróć self._key w _finalizer_registry

    def __repr__(self):
        spróbuj:
            obj = self._weakref()
        wyjąwszy (AttributeError, TypeError):
            obj = Nic

        jeżeli obj jest Nic:
            zwróć '<%s object, dead>' % self.__class__.__name__

        x = '<%s object, callback=%s' % (
                self.__class__.__name__,
                getattr(self._callback, '__name__', self._callback))
        jeżeli self._args:
            x += ', args=' + str(self._args)
        jeżeli self._kwargs:
            x += ', kwargs=' + str(self._kwargs)
        jeżeli self._key[0] jest nie Nic:
            x += ', exitprority=' + str(self._key[0])
        zwróć x + '>'


def _run_finalizers(minpriority=Nic):
    '''
    Run all finalizers whose exit priority jest nie Nic oraz at least minpriority

    Finalizers przy highest priority are called first; finalizers with
    the same priority will be called w reverse order of creation.
    '''
    jeżeli _finalizer_registry jest Nic:
        # This function may be called after this module's globals are
        # destroyed.  See the _exit_function function w this module dla more
        # notes.
        zwróć

    jeżeli minpriority jest Nic:
        f = lambda p : p[0][0] jest nie Nic
    inaczej:
        f = lambda p : p[0][0] jest nie Nic oraz p[0][0] >= minpriority

    items = [x dla x w list(_finalizer_registry.items()) jeżeli f(x)]
    items.sort(reverse=Prawda)

    dla key, finalizer w items:
        sub_debug('calling %s', finalizer)
        spróbuj:
            finalizer()
        wyjąwszy Exception:
            zaimportuj traceback
            traceback.print_exc()

    jeżeli minpriority jest Nic:
        _finalizer_registry.clear()

#
# Clean up on exit
#

def is_exiting():
    '''
    Returns true jeżeli the process jest shutting down
    '''
    zwróć _exiting albo _exiting jest Nic

_exiting = Nieprawda

def _exit_function(info=info, debug=debug, _run_finalizers=_run_finalizers,
                   active_children=process.active_children,
                   current_process=process.current_process):
    # We hold on to references to functions w the arglist due to the
    # situation described below, where this function jest called after this
    # module's globals are destroyed.

    global _exiting

    jeżeli nie _exiting:
        _exiting = Prawda

        info('process shutting down')
        debug('running all "atexit" finalizers przy priority >= 0')
        _run_finalizers(0)

        jeżeli current_process() jest nie Nic:
            # We check jeżeli the current process jest Nic here because if
            # it's Nic, any call to ``active_children()`` will podnieś
            # an AttributeError (active_children winds up trying to
            # get attributes z util._current_process).  One
            # situation where this can happen jest jeżeli someone has
            # manipulated sys.modules, causing this module to be
            # garbage collected.  The destructor dla the module type
            # then replaces all values w the module dict przy Nic.
            # For instance, after setuptools runs a test it replaces
            # sys.modules przy a copy created earlier.  See issues
            # #9775 oraz #15881.  Also related: #4106, #9205, oraz
            # #9207.

            dla p w active_children():
                jeżeli p.daemon:
                    info('calling terminate() dla daemon %s', p.name)
                    p._popen.terminate()

            dla p w active_children():
                info('calling join() dla process %s', p.name)
                p.join()

        debug('running the remaining "atexit" finalizers')
        _run_finalizers()

atexit.register(_exit_function)

#
# Some fork aware types
#

klasa ForkAwareThreadLock(object):
    def __init__(self):
        self._reset()
        register_after_fork(self, ForkAwareThreadLock._reset)

    def _reset(self):
        self._lock = threading.Lock()
        self.acquire = self._lock.acquire
        self.release = self._lock.release

    def __enter__(self):
        zwróć self._lock.__enter__()

    def __exit__(self, *args):
        zwróć self._lock.__exit__(*args)


klasa ForkAwareLocal(threading.local):
    def __init__(self):
        register_after_fork(self, lambda obj : obj.__dict__.clear())
    def __reduce__(self):
        zwróć type(self), ()

#
# Close fds wyjąwszy those specified
#

spróbuj:
    MAXFD = os.sysconf("SC_OPEN_MAX")
wyjąwszy Exception:
    MAXFD = 256

def close_all_fds_except(fds):
    fds = list(fds) + [-1, MAXFD]
    fds.sort()
    assert fds[-1] == MAXFD, 'fd too large'
    dla i w range(len(fds) - 1):
        os.closerange(fds[i]+1, fds[i+1])

#
# Start a program przy only specified fds kept open
#

def spawnv_passfds(path, args, dalejfds):
    zaimportuj _posixsubprocess
    dalejfds = sorted(passfds)
    errpipe_read, errpipe_write = os.pipe()
    spróbuj:
        zwróć _posixsubprocess.fork_exec(
            args, [os.fsencode(path)], Prawda, dalejfds, Nic, Nic,
            -1, -1, -1, -1, -1, -1, errpipe_read, errpipe_write,
            Nieprawda, Nieprawda, Nic)
    w_końcu:
        os.close(errpipe_read)
        os.close(errpipe_write)
