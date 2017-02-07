#
# Module implementing synchronization primitives
#
# multiprocessing/synchronize.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

__all__ = [
    'Lock', 'RLock', 'Semaphore', 'BoundedSemaphore', 'Condition', 'Event'
    ]

zaimportuj threading
zaimportuj sys
zaimportuj tempfile
zaimportuj _multiprocessing

z time zaimportuj time jako _time

z . zaimportuj context
z . zaimportuj process
z . zaimportuj util

# Try to zaimportuj the mp.synchronize module cleanly, jeżeli it fails
# podnieś ImportError dla platforms lacking a working sem_open implementation.
# See issue 3770
spróbuj:
    z _multiprocessing zaimportuj SemLock, sem_unlink
wyjąwszy (ImportError):
    podnieś ImportError("This platform lacks a functioning sem_open" +
                      " implementation, therefore, the required" +
                      " synchronization primitives needed will not" +
                      " function, see issue 3770.")

#
# Constants
#

RECURSIVE_MUTEX, SEMAPHORE = list(range(2))
SEM_VALUE_MAX = _multiprocessing.SemLock.SEM_VALUE_MAX

#
# Base klasa dla semaphores oraz mutexes; wraps `_multiprocessing.SemLock`
#

klasa SemLock(object):

    _rand = tempfile._RandomNameSequence()

    def __init__(self, kind, value, maxvalue, *, ctx):
        jeżeli ctx jest Nic:
            ctx = context._default_context.get_context()
        name = ctx.get_start_method()
        unlink_now = sys.platform == 'win32' albo name == 'fork'
        dla i w range(100):
            spróbuj:
                sl = self._semlock = _multiprocessing.SemLock(
                    kind, value, maxvalue, self._make_name(),
                    unlink_now)
            wyjąwszy FileExistsError:
                dalej
            inaczej:
                przerwij
        inaczej:
            podnieś FileExistsError('cannot find name dla semaphore')

        util.debug('created semlock przy handle %s' % sl.handle)
        self._make_methods()

        jeżeli sys.platform != 'win32':
            def _after_fork(obj):
                obj._semlock._after_fork()
            util.register_after_fork(self, _after_fork)

        jeżeli self._semlock.name jest nie Nic:
            # We only get here jeżeli we are on Unix przy forking
            # disabled.  When the object jest garbage collected albo the
            # process shuts down we unlink the semaphore name
            z .semaphore_tracker zaimportuj register
            register(self._semlock.name)
            util.Finalize(self, SemLock._cleanup, (self._semlock.name,),
                          exitpriority=0)

    @staticmethod
    def _cleanup(name):
        z .semaphore_tracker zaimportuj unregister
        sem_unlink(name)
        unregister(name)

    def _make_methods(self):
        self.acquire = self._semlock.acquire
        self.release = self._semlock.release

    def __enter__(self):
        zwróć self._semlock.__enter__()

    def __exit__(self, *args):
        zwróć self._semlock.__exit__(*args)

    def __getstate__(self):
        context.assert_spawning(self)
        sl = self._semlock
        jeżeli sys.platform == 'win32':
            h = context.get_spawning_popen().duplicate_for_child(sl.handle)
        inaczej:
            h = sl.handle
        zwróć (h, sl.kind, sl.maxvalue, sl.name)

    def __setstate__(self, state):
        self._semlock = _multiprocessing.SemLock._rebuild(*state)
        util.debug('recreated blocker przy handle %r' % state[0])
        self._make_methods()

    @staticmethod
    def _make_name():
        zwróć '%s-%s' % (process.current_process()._config['semprefix'],
                          next(SemLock._rand))

#
# Semaphore
#

klasa Semaphore(SemLock):

    def __init__(self, value=1, *, ctx):
        SemLock.__init__(self, SEMAPHORE, value, SEM_VALUE_MAX, ctx=ctx)

    def get_value(self):
        zwróć self._semlock._get_value()

    def __repr__(self):
        spróbuj:
            value = self._semlock._get_value()
        wyjąwszy Exception:
            value = 'unknown'
        zwróć '<%s(value=%s)>' % (self.__class__.__name__, value)

#
# Bounded semaphore
#

klasa BoundedSemaphore(Semaphore):

    def __init__(self, value=1, *, ctx):
        SemLock.__init__(self, SEMAPHORE, value, value, ctx=ctx)

    def __repr__(self):
        spróbuj:
            value = self._semlock._get_value()
        wyjąwszy Exception:
            value = 'unknown'
        zwróć '<%s(value=%s, maxvalue=%s)>' % \
               (self.__class__.__name__, value, self._semlock.maxvalue)

#
# Non-recursive lock
#

klasa Lock(SemLock):

    def __init__(self, *, ctx):
        SemLock.__init__(self, SEMAPHORE, 1, 1, ctx=ctx)

    def __repr__(self):
        spróbuj:
            jeżeli self._semlock._is_mine():
                name = process.current_process().name
                jeżeli threading.current_thread().name != 'MainThread':
                    name += '|' + threading.current_thread().name
            albo_inaczej self._semlock._get_value() == 1:
                name = 'Nic'
            albo_inaczej self._semlock._count() > 0:
                name = 'SomeOtherThread'
            inaczej:
                name = 'SomeOtherProcess'
        wyjąwszy Exception:
            name = 'unknown'
        zwróć '<%s(owner=%s)>' % (self.__class__.__name__, name)

#
# Recursive lock
#

klasa RLock(SemLock):

    def __init__(self, *, ctx):
        SemLock.__init__(self, RECURSIVE_MUTEX, 1, 1, ctx=ctx)

    def __repr__(self):
        spróbuj:
            jeżeli self._semlock._is_mine():
                name = process.current_process().name
                jeżeli threading.current_thread().name != 'MainThread':
                    name += '|' + threading.current_thread().name
                count = self._semlock._count()
            albo_inaczej self._semlock._get_value() == 1:
                name, count = 'Nic', 0
            albo_inaczej self._semlock._count() > 0:
                name, count = 'SomeOtherThread', 'nonzero'
            inaczej:
                name, count = 'SomeOtherProcess', 'nonzero'
        wyjąwszy Exception:
            name, count = 'unknown', 'unknown'
        zwróć '<%s(%s, %s)>' % (self.__class__.__name__, name, count)

#
# Condition variable
#

klasa Condition(object):

    def __init__(self, lock=Nic, *, ctx):
        self._lock = lock albo ctx.RLock()
        self._sleeping_count = ctx.Semaphore(0)
        self._woken_count = ctx.Semaphore(0)
        self._wait_semaphore = ctx.Semaphore(0)
        self._make_methods()

    def __getstate__(self):
        context.assert_spawning(self)
        zwróć (self._lock, self._sleeping_count,
                self._woken_count, self._wait_semaphore)

    def __setstate__(self, state):
        (self._lock, self._sleeping_count,
         self._woken_count, self._wait_semaphore) = state
        self._make_methods()

    def __enter__(self):
        zwróć self._lock.__enter__()

    def __exit__(self, *args):
        zwróć self._lock.__exit__(*args)

    def _make_methods(self):
        self.acquire = self._lock.acquire
        self.release = self._lock.release

    def __repr__(self):
        spróbuj:
            num_waiters = (self._sleeping_count._semlock._get_value() -
                           self._woken_count._semlock._get_value())
        wyjąwszy Exception:
            num_waiters = 'unknown'
        zwróć '<%s(%s, %s)>' % (self.__class__.__name__, self._lock, num_waiters)

    def wait(self, timeout=Nic):
        assert self._lock._semlock._is_mine(), \
               'must acquire() condition before using wait()'

        # indicate that this thread jest going to sleep
        self._sleeping_count.release()

        # release lock
        count = self._lock._semlock._count()
        dla i w range(count):
            self._lock.release()

        spróbuj:
            # wait dla notification albo timeout
            zwróć self._wait_semaphore.acquire(Prawda, timeout)
        w_końcu:
            # indicate that this thread has woken
            self._woken_count.release()

            # reacquire lock
            dla i w range(count):
                self._lock.acquire()

    def notify(self):
        assert self._lock._semlock._is_mine(), 'lock jest nie owned'
        assert nie self._wait_semaphore.acquire(Nieprawda)

        # to take account of timeouts since last notify() we subtract
        # woken_count z sleeping_count oraz rezero woken_count
        dopóki self._woken_count.acquire(Nieprawda):
            res = self._sleeping_count.acquire(Nieprawda)
            assert res

        jeżeli self._sleeping_count.acquire(Nieprawda): # try grabbing a sleeper
            self._wait_semaphore.release()      # wake up one sleeper
            self._woken_count.acquire()         # wait dla the sleeper to wake

            # rezero _wait_semaphore w case a timeout just happened
            self._wait_semaphore.acquire(Nieprawda)

    def notify_all(self):
        assert self._lock._semlock._is_mine(), 'lock jest nie owned'
        assert nie self._wait_semaphore.acquire(Nieprawda)

        # to take account of timeouts since last notify*() we subtract
        # woken_count z sleeping_count oraz rezero woken_count
        dopóki self._woken_count.acquire(Nieprawda):
            res = self._sleeping_count.acquire(Nieprawda)
            assert res

        sleepers = 0
        dopóki self._sleeping_count.acquire(Nieprawda):
            self._wait_semaphore.release()        # wake up one sleeper
            sleepers += 1

        jeżeli sleepers:
            dla i w range(sleepers):
                self._woken_count.acquire()       # wait dla a sleeper to wake

            # rezero wait_semaphore w case some timeouts just happened
            dopóki self._wait_semaphore.acquire(Nieprawda):
                dalej

    def wait_for(self, predicate, timeout=Nic):
        result = predicate()
        jeżeli result:
            zwróć result
        jeżeli timeout jest nie Nic:
            endtime = _time() + timeout
        inaczej:
            endtime = Nic
            waittime = Nic
        dopóki nie result:
            jeżeli endtime jest nie Nic:
                waittime = endtime - _time()
                jeżeli waittime <= 0:
                    przerwij
            self.wait(waittime)
            result = predicate()
        zwróć result

#
# Event
#

klasa Event(object):

    def __init__(self, *, ctx):
        self._cond = ctx.Condition(ctx.Lock())
        self._flag = ctx.Semaphore(0)

    def is_set(self):
        przy self._cond:
            jeżeli self._flag.acquire(Nieprawda):
                self._flag.release()
                zwróć Prawda
            zwróć Nieprawda

    def set(self):
        przy self._cond:
            self._flag.acquire(Nieprawda)
            self._flag.release()
            self._cond.notify_all()

    def clear(self):
        przy self._cond:
            self._flag.acquire(Nieprawda)

    def wait(self, timeout=Nic):
        przy self._cond:
            jeżeli self._flag.acquire(Nieprawda):
                self._flag.release()
            inaczej:
                self._cond.wait(timeout)

            jeżeli self._flag.acquire(Nieprawda):
                self._flag.release()
                zwróć Prawda
            zwróć Nieprawda

#
# Barrier
#

klasa Barrier(threading.Barrier):

    def __init__(self, parties, action=Nic, timeout=Nic, *, ctx):
        zaimportuj struct
        z .heap zaimportuj BufferWrapper
        wrapper = BufferWrapper(struct.calcsize('i') * 2)
        cond = ctx.Condition()
        self.__setstate__((parties, action, timeout, cond, wrapper))
        self._state = 0
        self._count = 0

    def __setstate__(self, state):
        (self._parties, self._action, self._timeout,
         self._cond, self._wrapper) = state
        self._array = self._wrapper.create_memoryview().cast('i')

    def __getstate__(self):
        zwróć (self._parties, self._action, self._timeout,
                self._cond, self._wrapper)

    @property
    def _state(self):
        zwróć self._array[0]

    @_state.setter
    def _state(self, value):
        self._array[0] = value

    @property
    def _count(self):
        zwróć self._array[1]

    @_count.setter
    def _count(self, value):
        self._array[1] = value
