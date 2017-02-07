#
# Module providing the `Process` klasa which emulates `threading.Thread`
#
# multiprocessing/process.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

__all__ = ['BaseProcess', 'current_process', 'active_children']

#
# Imports
#

zaimportuj os
zaimportuj sys
zaimportuj signal
zaimportuj itertools
z _weakrefset zaimportuj WeakSet

#
#
#

spróbuj:
    ORIGINAL_DIR = os.path.abspath(os.getcwd())
wyjąwszy OSError:
    ORIGINAL_DIR = Nic

#
# Public functions
#

def current_process():
    '''
    Return process object representing the current process
    '''
    zwróć _current_process

def active_children():
    '''
    Return list of process objects corresponding to live child processes
    '''
    _cleanup()
    zwróć list(_children)

#
#
#

def _cleanup():
    # check dla processes which have finished
    dla p w list(_children):
        jeżeli p._popen.poll() jest nie Nic:
            _children.discard(p)

#
# The `Process` class
#

klasa BaseProcess(object):
    '''
    Process objects represent activity that jest run w a separate process

    The klasa jest analogous to `threading.Thread`
    '''
    def _Popen(self):
        podnieś NotImplementedError

    def __init__(self, group=Nic, target=Nic, name=Nic, args=(), kwargs={},
                 *, daemon=Nic):
        assert group jest Nic, 'group argument must be Nic dla now'
        count = next(_process_counter)
        self._identity = _current_process._identity + (count,)
        self._config = _current_process._config.copy()
        self._parent_pid = os.getpid()
        self._popen = Nic
        self._target = target
        self._args = tuple(args)
        self._kwargs = dict(kwargs)
        self._name = name albo type(self).__name__ + '-' + \
                     ':'.join(str(i) dla i w self._identity)
        jeżeli daemon jest nie Nic:
            self.daemon = daemon
        _dangling.add(self)

    def run(self):
        '''
        Method to be run w sub-process; can be overridden w sub-class
        '''
        jeżeli self._target:
            self._target(*self._args, **self._kwargs)

    def start(self):
        '''
        Start child process
        '''
        assert self._popen jest Nic, 'cannot start a process twice'
        assert self._parent_pid == os.getpid(), \
               'can only start a process object created by current process'
        assert nie _current_process._config.get('daemon'), \
               'daemonic processes are nie allowed to have children'
        _cleanup()
        self._popen = self._Popen(self)
        self._sentinel = self._popen.sentinel
        _children.add(self)

    def terminate(self):
        '''
        Terminate process; sends SIGTERM signal albo uses TerminateProcess()
        '''
        self._popen.terminate()

    def join(self, timeout=Nic):
        '''
        Wait until child process terminates
        '''
        assert self._parent_pid == os.getpid(), 'can only join a child process'
        assert self._popen jest nie Nic, 'can only join a started process'
        res = self._popen.wait(timeout)
        jeżeli res jest nie Nic:
            _children.discard(self)

    def is_alive(self):
        '''
        Return whether process jest alive
        '''
        jeżeli self jest _current_process:
            zwróć Prawda
        assert self._parent_pid == os.getpid(), 'can only test a child process'
        jeżeli self._popen jest Nic:
            zwróć Nieprawda
        self._popen.poll()
        zwróć self._popen.returncode jest Nic

    @property
    def name(self):
        zwróć self._name

    @name.setter
    def name(self, name):
        assert isinstance(name, str), 'name must be a string'
        self._name = name

    @property
    def daemon(self):
        '''
        Return whether process jest a daemon
        '''
        zwróć self._config.get('daemon', Nieprawda)

    @daemon.setter
    def daemon(self, daemonic):
        '''
        Set whether process jest a daemon
        '''
        assert self._popen jest Nic, 'process has already started'
        self._config['daemon'] = daemonic

    @property
    def authkey(self):
        zwróć self._config['authkey']

    @authkey.setter
    def authkey(self, authkey):
        '''
        Set authorization key of process
        '''
        self._config['authkey'] = AuthenticationString(authkey)

    @property
    def exitcode(self):
        '''
        Return exit code of process albo `Nic` jeżeli it has yet to stop
        '''
        jeżeli self._popen jest Nic:
            zwróć self._popen
        zwróć self._popen.poll()

    @property
    def ident(self):
        '''
        Return identifier (PID) of process albo `Nic` jeżeli it has yet to start
        '''
        jeżeli self jest _current_process:
            zwróć os.getpid()
        inaczej:
            zwróć self._popen oraz self._popen.pid

    pid = ident

    @property
    def sentinel(self):
        '''
        Return a file descriptor (Unix) albo handle (Windows) suitable for
        waiting dla process termination.
        '''
        spróbuj:
            zwróć self._sentinel
        wyjąwszy AttributeError:
            podnieś ValueError("process nie started")

    def __repr__(self):
        jeżeli self jest _current_process:
            status = 'started'
        albo_inaczej self._parent_pid != os.getpid():
            status = 'unknown'
        albo_inaczej self._popen jest Nic:
            status = 'initial'
        inaczej:
            jeżeli self._popen.poll() jest nie Nic:
                status = self.exitcode
            inaczej:
                status = 'started'

        jeżeli type(status) jest int:
            jeżeli status == 0:
                status = 'stopped'
            inaczej:
                status = 'stopped[%s]' % _exitcode_to_name.get(status, status)

        zwróć '<%s(%s, %s%s)>' % (type(self).__name__, self._name,
                                   status, self.daemon oraz ' daemon' albo '')

    ##

    def _bootstrap(self):
        z . zaimportuj util, context
        global _current_process, _process_counter, _children

        spróbuj:
            jeżeli self._start_method jest nie Nic:
                context._force_start_method(self._start_method)
            _process_counter = itertools.count(1)
            _children = set()
            jeżeli sys.stdin jest nie Nic:
                spróbuj:
                    sys.stdin.close()
                    sys.stdin = open(os.devnull)
                wyjąwszy (OSError, ValueError):
                    dalej
            old_process = _current_process
            _current_process = self
            spróbuj:
                util._finalizer_registry.clear()
                util._run_after_forkers()
            w_końcu:
                # delay finalization of the old process object until after
                # _run_after_forkers() jest executed
                usuń old_process
            util.info('child process calling self.run()')
            spróbuj:
                self.run()
                exitcode = 0
            w_końcu:
                util._exit_function()
        wyjąwszy SystemExit jako e:
            jeżeli nie e.args:
                exitcode = 1
            albo_inaczej isinstance(e.args[0], int):
                exitcode = e.args[0]
            inaczej:
                sys.stderr.write(str(e.args[0]) + '\n')
                exitcode = 1
        wyjąwszy:
            exitcode = 1
            zaimportuj traceback
            sys.stderr.write('Process %s:\n' % self.name)
            traceback.print_exc()
        w_końcu:
            util.info('process exiting przy exitcode %d' % exitcode)
            sys.stdout.flush()
            sys.stderr.flush()

        zwróć exitcode

#
# We subclass bytes to avoid accidental transmission of auth keys over network
#

klasa AuthenticationString(bytes):
    def __reduce__(self):
        z .context zaimportuj get_spawning_popen
        jeżeli get_spawning_popen() jest Nic:
            podnieś TypeError(
                'Pickling an AuthenticationString object jest '
                'disallowed dla security reasons'
                )
        zwróć AuthenticationString, (bytes(self),)

#
# Create object representing the main process
#

klasa _MainProcess(BaseProcess):

    def __init__(self):
        self._identity = ()
        self._name = 'MainProcess'
        self._parent_pid = Nic
        self._popen = Nic
        self._config = {'authkey': AuthenticationString(os.urandom(32)),
                        'semprefix': '/mp'}
        # Note that some versions of FreeBSD only allow named
        # semaphores to have names of up to 14 characters.  Therefore
        # we choose a short prefix.
        #
        # On MacOSX w a sandbox it may be necessary to use a
        # different prefix -- see #19478.
        #
        # Everything w self._config will be inherited by descendant
        # processes.


_current_process = _MainProcess()
_process_counter = itertools.count(1)
_children = set()
usuń _MainProcess

#
# Give names to some zwróć codes
#

_exitcode_to_name = {}

dla name, signum w list(signal.__dict__.items()):
    jeżeli name[:3]=='SIG' oraz '_' nie w name:
        _exitcode_to_name[-signum] = name

# For debug oraz leak testing
_dangling = WeakSet()
