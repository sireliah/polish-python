"""Thread module emulating a subset of Java's threading model."""

zaimportuj sys jako _sys
zaimportuj _thread

z time zaimportuj monotonic jako _time
z traceback zaimportuj format_exc jako _format_exc
z _weakrefset zaimportuj WeakSet
z itertools zaimportuj islice jako _islice, count jako _count
spróbuj:
    z _collections zaimportuj deque jako _deque
wyjąwszy ImportError:
    z collections zaimportuj deque jako _deque

# Note regarding PEP 8 compliant names
#  This threading mousuń was originally inspired by Java, oraz inherited
# the convention of camelCase function oraz method names z that
# language. Those original names are nie w any imminent danger of
# being deprecated (even dla Py3k),so this module provides them jako an
# alias dla the PEP 8 compliant names
# Note that using the new PEP 8 compliant names facilitates substitution
# przy the multiprocessing module, which doesn't provide the old
# Java inspired names.

__all__ = ['active_count', 'Condition', 'current_thread', 'enumerate', 'Event',
           'Lock', 'RLock', 'Semaphore', 'BoundedSemaphore', 'Thread', 'Barrier',
           'Timer', 'ThreadError', 'setprofile', 'settrace', 'local', 'stack_size']

# Rename some stuff so "z threading zaimportuj *" jest safe
_start_new_thread = _thread.start_new_thread
_allocate_lock = _thread.allocate_lock
_set_sentinel = _thread._set_sentinel
get_ident = _thread.get_ident
ThreadError = _thread.error
spróbuj:
    _CRLock = _thread.RLock
wyjąwszy AttributeError:
    _CRLock = Nic
TIMEOUT_MAX = _thread.TIMEOUT_MAX
usuń _thread


# Support dla profile oraz trace hooks

_profile_hook = Nic
_trace_hook = Nic

def setprofile(func):
    """Set a profile function dla all threads started z the threading module.

    The func will be dalejed to sys.setprofile() dla each thread, before its
    run() method jest called.

    """
    global _profile_hook
    _profile_hook = func

def settrace(func):
    """Set a trace function dla all threads started z the threading module.

    The func will be dalejed to sys.settrace() dla each thread, before its run()
    method jest called.

    """
    global _trace_hook
    _trace_hook = func

# Synchronization classes

Lock = _allocate_lock

def RLock(*args, **kwargs):
    """Factory function that returns a new reentrant lock.

    A reentrant lock must be released by the thread that acquired it. Once a
    thread has acquired a reentrant lock, the same thread may acquire it again
    without blocking; the thread must release it once dla each time it has
    acquired it.

    """
    jeżeli _CRLock jest Nic:
        zwróć _PyRLock(*args, **kwargs)
    zwróć _CRLock(*args, **kwargs)

klasa _RLock:
    """This klasa implements reentrant lock objects.

    A reentrant lock must be released by the thread that acquired it. Once a
    thread has acquired a reentrant lock, the same thread may acquire it
    again without blocking; the thread must release it once dla each time it
    has acquired it.

    """

    def __init__(self):
        self._block = _allocate_lock()
        self._owner = Nic
        self._count = 0

    def __repr__(self):
        owner = self._owner
        spróbuj:
            owner = _active[owner].name
        wyjąwszy KeyError:
            dalej
        zwróć "<%s %s.%s object owner=%r count=%d at %s>" % (
            "locked" jeżeli self._block.locked() inaczej "unlocked",
            self.__class__.__module__,
            self.__class__.__qualname__,
            owner,
            self._count,
            hex(id(self))
        )

    def acquire(self, blocking=Prawda, timeout=-1):
        """Acquire a lock, blocking albo non-blocking.

        When invoked without arguments: jeżeli this thread already owns the lock,
        increment the recursion level by one, oraz zwróć immediately. Otherwise,
        jeżeli another thread owns the lock, block until the lock jest unlocked. Once
        the lock jest unlocked (nie owned by any thread), then grab ownership, set
        the recursion level to one, oraz return. If more than one thread jest
        blocked waiting until the lock jest unlocked, only one at a time will be
        able to grab ownership of the lock. There jest no zwróć value w this
        case.

        When invoked przy the blocking argument set to true, do the same thing
        jako when called without arguments, oraz zwróć true.

        When invoked przy the blocking argument set to false, do nie block. If a
        call without an argument would block, zwróć false immediately;
        otherwise, do the same thing jako when called without arguments, oraz
        zwróć true.

        When invoked przy the floating-point timeout argument set to a positive
        value, block dla at most the number of seconds specified by timeout
        oraz jako long jako the lock cannot be acquired.  Return true jeżeli the lock has
        been acquired, false jeżeli the timeout has elapsed.

        """
        me = get_ident()
        jeżeli self._owner == me:
            self._count += 1
            zwróć 1
        rc = self._block.acquire(blocking, timeout)
        jeżeli rc:
            self._owner = me
            self._count = 1
        zwróć rc

    __enter__ = acquire

    def release(self):
        """Release a lock, decrementing the recursion level.

        If after the decrement it jest zero, reset the lock to unlocked (nie owned
        by any thread), oraz jeżeli any other threads are blocked waiting dla the
        lock to become unlocked, allow exactly one of them to proceed. If after
        the decrement the recursion level jest still nonzero, the lock remains
        locked oraz owned by the calling thread.

        Only call this method when the calling thread owns the lock. A
        RuntimeError jest podnieśd jeżeli this method jest called when the lock jest
        unlocked.

        There jest no zwróć value.

        """
        jeżeli self._owner != get_ident():
            podnieś RuntimeError("cannot release un-acquired lock")
        self._count = count = self._count - 1
        jeżeli nie count:
            self._owner = Nic
            self._block.release()

    def __exit__(self, t, v, tb):
        self.release()

    # Internal methods used by condition variables

    def _acquire_restore(self, state):
        self._block.acquire()
        self._count, self._owner = state

    def _release_save(self):
        jeżeli self._count == 0:
            podnieś RuntimeError("cannot release un-acquired lock")
        count = self._count
        self._count = 0
        owner = self._owner
        self._owner = Nic
        self._block.release()
        zwróć (count, owner)

    def _is_owned(self):
        zwróć self._owner == get_ident()

_PyRLock = _RLock


klasa Condition:
    """Class that implements a condition variable.

    A condition variable allows one albo more threads to wait until they are
    notified by another thread.

    If the lock argument jest given oraz nie Nic, it must be a Lock albo RLock
    object, oraz it jest used jako the underlying lock. Otherwise, a new RLock object
    jest created oraz used jako the underlying lock.

    """

    def __init__(self, lock=Nic):
        jeżeli lock jest Nic:
            lock = RLock()
        self._lock = lock
        # Export the lock's acquire() oraz release() methods
        self.acquire = lock.acquire
        self.release = lock.release
        # If the lock defines _release_save() and/or _acquire_restore(),
        # these override the default implementations (which just call
        # release() oraz acquire() on the lock).  Ditto dla _is_owned().
        spróbuj:
            self._release_save = lock._release_save
        wyjąwszy AttributeError:
            dalej
        spróbuj:
            self._acquire_restore = lock._acquire_restore
        wyjąwszy AttributeError:
            dalej
        spróbuj:
            self._is_owned = lock._is_owned
        wyjąwszy AttributeError:
            dalej
        self._waiters = _deque()

    def __enter__(self):
        zwróć self._lock.__enter__()

    def __exit__(self, *args):
        zwróć self._lock.__exit__(*args)

    def __repr__(self):
        zwróć "<Condition(%s, %d)>" % (self._lock, len(self._waiters))

    def _release_save(self):
        self._lock.release()           # No state to save

    def _acquire_restore(self, x):
        self._lock.acquire()           # Ignore saved state

    def _is_owned(self):
        # Return Prawda jeżeli lock jest owned by current_thread.
        # This method jest called only jeżeli _lock doesn't have _is_owned().
        jeżeli self._lock.acquire(0):
            self._lock.release()
            zwróć Nieprawda
        inaczej:
            zwróć Prawda

    def wait(self, timeout=Nic):
        """Wait until notified albo until a timeout occurs.

        If the calling thread has nie acquired the lock when this method jest
        called, a RuntimeError jest podnieśd.

        This method releases the underlying lock, oraz then blocks until it jest
        awakened by a notify() albo notify_all() call dla the same condition
        variable w another thread, albo until the optional timeout occurs. Once
        awakened albo timed out, it re-acquires the lock oraz returns.

        When the timeout argument jest present oraz nie Nic, it should be a
        floating point number specifying a timeout dla the operation w seconds
        (or fractions thereof).

        When the underlying lock jest an RLock, it jest nie released using its
        release() method, since this may nie actually unlock the lock when it
        was acquired multiple times recursively. Instead, an internal interface
        of the RLock klasa jest used, which really unlocks it even when it has
        been recursively acquired several times. Another internal interface jest
        then used to restore the recursion level when the lock jest reacquired.

        """
        jeżeli nie self._is_owned():
            podnieś RuntimeError("cannot wait on un-acquired lock")
        waiter = _allocate_lock()
        waiter.acquire()
        self._waiters.append(waiter)
        saved_state = self._release_save()
        gotit = Nieprawda
        spróbuj:    # restore state no matter what (e.g., KeyboardInterrupt)
            jeżeli timeout jest Nic:
                waiter.acquire()
                gotit = Prawda
            inaczej:
                jeżeli timeout > 0:
                    gotit = waiter.acquire(Prawda, timeout)
                inaczej:
                    gotit = waiter.acquire(Nieprawda)
            zwróć gotit
        w_końcu:
            self._acquire_restore(saved_state)
            jeżeli nie gotit:
                spróbuj:
                    self._waiters.remove(waiter)
                wyjąwszy ValueError:
                    dalej

    def wait_for(self, predicate, timeout=Nic):
        """Wait until a condition evaluates to Prawda.

        predicate should be a callable which result will be interpreted jako a
        boolean value.  A timeout may be provided giving the maximum time to
        wait.

        """
        endtime = Nic
        waittime = timeout
        result = predicate()
        dopóki nie result:
            jeżeli waittime jest nie Nic:
                jeżeli endtime jest Nic:
                    endtime = _time() + waittime
                inaczej:
                    waittime = endtime - _time()
                    jeżeli waittime <= 0:
                        przerwij
            self.wait(waittime)
            result = predicate()
        zwróć result

    def notify(self, n=1):
        """Wake up one albo more threads waiting on this condition, jeżeli any.

        If the calling thread has nie acquired the lock when this method jest
        called, a RuntimeError jest podnieśd.

        This method wakes up at most n of the threads waiting dla the condition
        variable; it jest a no-op jeżeli no threads are waiting.

        """
        jeżeli nie self._is_owned():
            podnieś RuntimeError("cannot notify on un-acquired lock")
        all_waiters = self._waiters
        waiters_to_notify = _deque(_islice(all_waiters, n))
        jeżeli nie waiters_to_notify:
            zwróć
        dla waiter w waiters_to_notify:
            waiter.release()
            spróbuj:
                all_waiters.remove(waiter)
            wyjąwszy ValueError:
                dalej

    def notify_all(self):
        """Wake up all threads waiting on this condition.

        If the calling thread has nie acquired the lock when this method
        jest called, a RuntimeError jest podnieśd.

        """
        self.notify(len(self._waiters))

    notifyAll = notify_all


klasa Semaphore:
    """This klasa implements semaphore objects.

    Semaphores manage a counter representing the number of release() calls minus
    the number of acquire() calls, plus an initial value. The acquire() method
    blocks jeżeli necessary until it can zwróć without making the counter
    negative. If nie given, value defaults to 1.

    """

    # After Tim Peters' semaphore class, but nie quite the same (no maximum)

    def __init__(self, value=1):
        jeżeli value < 0:
            podnieś ValueError("semaphore initial value must be >= 0")
        self._cond = Condition(Lock())
        self._value = value

    def acquire(self, blocking=Prawda, timeout=Nic):
        """Acquire a semaphore, decrementing the internal counter by one.

        When invoked without arguments: jeżeli the internal counter jest larger than
        zero on entry, decrement it by one oraz zwróć immediately. If it jest zero
        on entry, block, waiting until some other thread has called release() to
        make it larger than zero. This jest done przy proper interlocking so that
        jeżeli multiple acquire() calls are blocked, release() will wake exactly one
        of them up. The implementation may pick one at random, so the order w
        which blocked threads are awakened should nie be relied on. There jest no
        zwróć value w this case.

        When invoked przy blocking set to true, do the same thing jako when called
        without arguments, oraz zwróć true.

        When invoked przy blocking set to false, do nie block. If a call without
        an argument would block, zwróć false immediately; otherwise, do the
        same thing jako when called without arguments, oraz zwróć true.

        When invoked przy a timeout other than Nic, it will block dla at
        most timeout seconds.  If acquire does nie complete successfully w
        that interval, zwróć false.  Return true otherwise.

        """
        jeżeli nie blocking oraz timeout jest nie Nic:
            podnieś ValueError("can't specify timeout dla non-blocking acquire")
        rc = Nieprawda
        endtime = Nic
        przy self._cond:
            dopóki self._value == 0:
                jeżeli nie blocking:
                    przerwij
                jeżeli timeout jest nie Nic:
                    jeżeli endtime jest Nic:
                        endtime = _time() + timeout
                    inaczej:
                        timeout = endtime - _time()
                        jeżeli timeout <= 0:
                            przerwij
                self._cond.wait(timeout)
            inaczej:
                self._value -= 1
                rc = Prawda
        zwróć rc

    __enter__ = acquire

    def release(self):
        """Release a semaphore, incrementing the internal counter by one.

        When the counter jest zero on entry oraz another thread jest waiting dla it
        to become larger than zero again, wake up that thread.

        """
        przy self._cond:
            self._value += 1
            self._cond.notify()

    def __exit__(self, t, v, tb):
        self.release()


klasa BoundedSemaphore(Semaphore):
    """Implements a bounded semaphore.

    A bounded semaphore checks to make sure its current value doesn't exceed its
    initial value. If it does, ValueError jest podnieśd. In most situations
    semaphores are used to guard resources przy limited capacity.

    If the semaphore jest released too many times it's a sign of a bug. If nie
    given, value defaults to 1.

    Like regular semaphores, bounded semaphores manage a counter representing
    the number of release() calls minus the number of acquire() calls, plus an
    initial value. The acquire() method blocks jeżeli necessary until it can zwróć
    without making the counter negative. If nie given, value defaults to 1.

    """

    def __init__(self, value=1):
        Semaphore.__init__(self, value)
        self._initial_value = value

    def release(self):
        """Release a semaphore, incrementing the internal counter by one.

        When the counter jest zero on entry oraz another thread jest waiting dla it
        to become larger than zero again, wake up that thread.

        If the number of releases exceeds the number of acquires,
        podnieś a ValueError.

        """
        przy self._cond:
            jeżeli self._value >= self._initial_value:
                podnieś ValueError("Semaphore released too many times")
            self._value += 1
            self._cond.notify()


klasa Event:
    """Class implementing event objects.

    Events manage a flag that can be set to true przy the set() method oraz reset
    to false przy the clear() method. The wait() method blocks until the flag jest
    true.  The flag jest initially false.

    """

    # After Tim Peters' event klasa (without is_posted())

    def __init__(self):
        self._cond = Condition(Lock())
        self._flag = Nieprawda

    def _reset_internal_locks(self):
        # private!  called by Thread._reset_internal_locks by _after_fork()
        self._cond.__init__()

    def is_set(self):
        """Return true jeżeli oraz only jeżeli the internal flag jest true."""
        zwróć self._flag

    isSet = is_set

    def set(self):
        """Set the internal flag to true.

        All threads waiting dla it to become true are awakened. Threads
        that call wait() once the flag jest true will nie block at all.

        """
        self._cond.acquire()
        spróbuj:
            self._flag = Prawda
            self._cond.notify_all()
        w_końcu:
            self._cond.release()

    def clear(self):
        """Reset the internal flag to false.

        Subsequently, threads calling wait() will block until set() jest called to
        set the internal flag to true again.

        """
        self._cond.acquire()
        spróbuj:
            self._flag = Nieprawda
        w_końcu:
            self._cond.release()

    def wait(self, timeout=Nic):
        """Block until the internal flag jest true.

        If the internal flag jest true on entry, zwróć immediately. Otherwise,
        block until another thread calls set() to set the flag to true, albo until
        the optional timeout occurs.

        When the timeout argument jest present oraz nie Nic, it should be a
        floating point number specifying a timeout dla the operation w seconds
        (or fractions thereof).

        This method returns the internal flag on exit, so it will always zwróć
        Prawda wyjąwszy jeżeli a timeout jest given oraz the operation times out.

        """
        self._cond.acquire()
        spróbuj:
            signaled = self._flag
            jeżeli nie signaled:
                signaled = self._cond.wait(timeout)
            zwróć signaled
        w_końcu:
            self._cond.release()


# A barrier class.  Inspired w part by the pthread_barrier_* api oraz
# the CyclicBarrier klasa z Java.  See
# http://sourceware.org/pthreads-win32/manual/pthread_barrier_init.html oraz
# http://java.sun.com/j2se/1.5.0/docs/api/java/util/concurrent/
#        CyclicBarrier.html
# dla information.
# We maintain two main states, 'filling' oraz 'draining' enabling the barrier
# to be cyclic.  Threads are nie allowed into it until it has fully drained
# since the previous cycle.  In addition, a 'resetting' state exists which jest
# similar to 'draining' wyjąwszy that threads leave przy a BrokenBarrierError,
# oraz a 'broken' state w which all threads get the exception.
klasa Barrier:
    """Implements a Barrier.

    Useful dla synchronizing a fixed number of threads at known synchronization
    points.  Threads block on 'wait()' oraz are simultaneously once they have all
    made that call.

    """

    def __init__(self, parties, action=Nic, timeout=Nic):
        """Create a barrier, initialised to 'parties' threads.

        'action' jest a callable which, when supplied, will be called by one of
        the threads after they have all entered the barrier oraz just prior to
        releasing them all. If a 'timeout' jest provided, it jest uses jako the
        default dla all subsequent 'wait()' calls.

        """
        self._cond = Condition(Lock())
        self._action = action
        self._timeout = timeout
        self._parties = parties
        self._state = 0 #0 filling, 1, draining, -1 resetting, -2 broken
        self._count = 0

    def wait(self, timeout=Nic):
        """Wait dla the barrier.

        When the specified number of threads have started waiting, they are all
        simultaneously awoken. If an 'action' was provided dla the barrier, one
        of the threads will have executed that callback prior to returning.
        Returns an individual index number z 0 to 'parties-1'.

        """
        jeżeli timeout jest Nic:
            timeout = self._timeout
        przy self._cond:
            self._enter() # Block dopóki the barrier drains.
            index = self._count
            self._count += 1
            spróbuj:
                jeżeli index + 1 == self._parties:
                    # We release the barrier
                    self._release()
                inaczej:
                    # We wait until someone releases us
                    self._wait(timeout)
                zwróć index
            w_końcu:
                self._count -= 1
                # Wake up any threads waiting dla barrier to drain.
                self._exit()

    # Block until the barrier jest ready dla us, albo podnieś an exception
    # jeżeli it jest broken.
    def _enter(self):
        dopóki self._state w (-1, 1):
            # It jest draining albo resetting, wait until done
            self._cond.wait()
        #see jeżeli the barrier jest w a broken state
        jeżeli self._state < 0:
            podnieś BrokenBarrierError
        assert self._state == 0

    # Optionally run the 'action' oraz release the threads waiting
    # w the barrier.
    def _release(self):
        spróbuj:
            jeżeli self._action:
                self._action()
            # enter draining state
            self._state = 1
            self._cond.notify_all()
        wyjąwszy:
            #an exception during the _action handler.  Break oraz reraise
            self._break()
            podnieś

    # Wait w the barrier until we are relased.  Raise an exception
    # jeżeli the barrier jest reset albo broken.
    def _wait(self, timeout):
        jeżeli nie self._cond.wait_for(lambda : self._state != 0, timeout):
            #timed out.  Break the barrier
            self._break()
            podnieś BrokenBarrierError
        jeżeli self._state < 0:
            podnieś BrokenBarrierError
        assert self._state == 1

    # If we are the last thread to exit the barrier, signal any threads
    # waiting dla the barrier to drain.
    def _exit(self):
        jeżeli self._count == 0:
            jeżeli self._state w (-1, 1):
                #resetting albo draining
                self._state = 0
                self._cond.notify_all()

    def reset(self):
        """Reset the barrier to the initial state.

        Any threads currently waiting will get the BrokenBarrier exception
        podnieśd.

        """
        przy self._cond:
            jeżeli self._count > 0:
                jeżeli self._state == 0:
                    #reset the barrier, waking up threads
                    self._state = -1
                albo_inaczej self._state == -2:
                    #was broken, set it to reset state
                    #which clears when the last thread exits
                    self._state = -1
            inaczej:
                self._state = 0
            self._cond.notify_all()

    def abort(self):
        """Place the barrier into a 'broken' state.

        Useful w case of error.  Any currently waiting threads oraz threads
        attempting to 'wait()' will have BrokenBarrierError podnieśd.

        """
        przy self._cond:
            self._break()

    def _break(self):
        # An internal error was detected.  The barrier jest set to
        # a broken state all parties awakened.
        self._state = -2
        self._cond.notify_all()

    @property
    def parties(self):
        """Return the number of threads required to trip the barrier."""
        zwróć self._parties

    @property
    def n_waiting(self):
        """Return the number of threads currently waiting at the barrier."""
        # We don't need synchronization here since this jest an ephemeral result
        # anyway.  It returns the correct value w the steady state.
        jeżeli self._state == 0:
            zwróć self._count
        zwróć 0

    @property
    def broken(self):
        """Return Prawda jeżeli the barrier jest w a broken state."""
        zwróć self._state == -2

# exception podnieśd by the Barrier class
klasa BrokenBarrierError(RuntimeError):
    dalej


# Helper to generate new thread names
_counter = _count().__next__
_counter() # Consume 0 so first non-main thread has id 1.
def _newname(template="Thread-%d"):
    zwróć template % _counter()

# Active thread administration
_active_limbo_lock = _allocate_lock()
_active = {}    # maps thread id to Thread object
_limbo = {}
_dangling = WeakSet()

# Main klasa dla threads

klasa Thread:
    """A klasa that represents a thread of control.

    This klasa can be safely subclassed w a limited fashion. There are two ways
    to specify the activity: by dalejing a callable object to the constructor, albo
    by overriding the run() method w a subclass.

    """

    _initialized = Nieprawda
    # Need to store a reference to sys.exc_info dla printing
    # out exceptions when a thread tries to use a global var. during interp.
    # shutdown oraz thus podnieśs an exception about trying to perform some
    # operation on/przy a NicType
    _exc_info = _sys.exc_info
    # Keep sys.exc_clear too to clear the exception just before
    # allowing .join() to return.
    #XXX __exc_clear = _sys.exc_clear

    def __init__(self, group=Nic, target=Nic, name=Nic,
                 args=(), kwargs=Nic, *, daemon=Nic):
        """This constructor should always be called przy keyword arguments. Arguments are:

        *group* should be Nic; reserved dla future extension when a ThreadGroup
        klasa jest implemented.

        *target* jest the callable object to be invoked by the run()
        method. Defaults to Nic, meaning nothing jest called.

        *name* jest the thread name. By default, a unique name jest constructed of
        the form "Thread-N" where N jest a small decimal number.

        *args* jest the argument tuple dla the target invocation. Defaults to ().

        *kwargs* jest a dictionary of keyword arguments dla the target
        invocation. Defaults to {}.

        If a subclass overrides the constructor, it must make sure to invoke
        the base klasa constructor (Thread.__init__()) before doing anything
        inaczej to the thread.

        """
        assert group jest Nic, "group argument must be Nic dla now"
        jeżeli kwargs jest Nic:
            kwargs = {}
        self._target = target
        self._name = str(name albo _newname())
        self._args = args
        self._kwargs = kwargs
        jeżeli daemon jest nie Nic:
            self._daemonic = daemon
        inaczej:
            self._daemonic = current_thread().daemon
        self._ident = Nic
        self._tstate_lock = Nic
        self._started = Event()
        self._is_stopped = Nieprawda
        self._initialized = Prawda
        # sys.stderr jest nie stored w the klasa like
        # sys.exc_info since it can be changed between instances
        self._stderr = _sys.stderr
        # For debugging oraz _after_fork()
        _dangling.add(self)

    def _reset_internal_locks(self, is_alive):
        # private!  Called by _after_fork() to reset our internal locks as
        # they may be w an invalid state leading to a deadlock albo crash.
        self._started._reset_internal_locks()
        jeżeli is_alive:
            self._set_tstate_lock()
        inaczej:
            # The thread isn't alive after fork: it doesn't have a tstate
            # anymore.
            self._is_stopped = Prawda
            self._tstate_lock = Nic

    def __repr__(self):
        assert self._initialized, "Thread.__init__() was nie called"
        status = "initial"
        jeżeli self._started.is_set():
            status = "started"
        self.is_alive() # easy way to get ._is_stopped set when appropriate
        jeżeli self._is_stopped:
            status = "stopped"
        jeżeli self._daemonic:
            status += " daemon"
        jeżeli self._ident jest nie Nic:
            status += " %s" % self._ident
        zwróć "<%s(%s, %s)>" % (self.__class__.__name__, self._name, status)

    def start(self):
        """Start the thread's activity.

        It must be called at most once per thread object. It arranges dla the
        object's run() method to be invoked w a separate thread of control.

        This method will podnieś a RuntimeError jeżeli called more than once on the
        same thread object.

        """
        jeżeli nie self._initialized:
            podnieś RuntimeError("thread.__init__() nie called")

        jeżeli self._started.is_set():
            podnieś RuntimeError("threads can only be started once")
        przy _active_limbo_lock:
            _limbo[self] = self
        spróbuj:
            _start_new_thread(self._bootstrap, ())
        wyjąwszy Exception:
            przy _active_limbo_lock:
                usuń _limbo[self]
            podnieś
        self._started.wait()

    def run(self):
        """Method representing the thread's activity.

        You may override this method w a subclass. The standard run() method
        invokes the callable object dalejed to the object's constructor jako the
        target argument, jeżeli any, przy sequential oraz keyword arguments taken
        z the args oraz kwargs arguments, respectively.

        """
        spróbuj:
            jeżeli self._target:
                self._target(*self._args, **self._kwargs)
        w_końcu:
            # Avoid a refcycle jeżeli the thread jest running a function with
            # an argument that has a member that points to the thread.
            usuń self._target, self._args, self._kwargs

    def _bootstrap(self):
        # Wrapper around the real bootstrap code that ignores
        # exceptions during interpreter cleanup.  Those typically
        # happen when a daemon thread wakes up at an unfortunate
        # moment, finds the world around it destroyed, oraz podnieśs some
        # random exception *** dopóki trying to report the exception w
        # _bootstrap_inner() below ***.  Those random exceptions
        # don't help anybody, oraz they confuse users, so we suppress
        # them.  We suppress them only when it appears that the world
        # indeed has already been destroyed, so that exceptions w
        # _bootstrap_inner() during normal business hours are properly
        # reported.  Also, we only suppress them dla daemonic threads;
        # jeżeli a non-daemonic encounters this, something inaczej jest wrong.
        spróbuj:
            self._bootstrap_inner()
        wyjąwszy:
            jeżeli self._daemonic oraz _sys jest Nic:
                zwróć
            podnieś

    def _set_ident(self):
        self._ident = get_ident()

    def _set_tstate_lock(self):
        """
        Set a lock object which will be released by the interpreter when
        the underlying thread state (see pystate.h) gets deleted.
        """
        self._tstate_lock = _set_sentinel()
        self._tstate_lock.acquire()

    def _bootstrap_inner(self):
        spróbuj:
            self._set_ident()
            self._set_tstate_lock()
            self._started.set()
            przy _active_limbo_lock:
                _active[self._ident] = self
                usuń _limbo[self]

            jeżeli _trace_hook:
                _sys.settrace(_trace_hook)
            jeżeli _profile_hook:
                _sys.setprofile(_profile_hook)

            spróbuj:
                self.run()
            wyjąwszy SystemExit:
                dalej
            wyjąwszy:
                # If sys.stderr jest no more (most likely z interpreter
                # shutdown) use self._stderr.  Otherwise still use sys (as w
                # _sys) w case sys.stderr was redefined since the creation of
                # self.
                jeżeli _sys oraz _sys.stderr jest nie Nic:
                    print("Exception w thread %s:\n%s" %
                          (self.name, _format_exc()), file=self._stderr)
                albo_inaczej self._stderr jest nie Nic:
                    # Do the best job possible w/o a huge amt. of code to
                    # approximate a traceback (code ideas from
                    # Lib/traceback.py)
                    exc_type, exc_value, exc_tb = self._exc_info()
                    spróbuj:
                        print((
                            "Exception w thread " + self.name +
                            " (most likely podnieśd during interpreter shutdown):"), file=self._stderr)
                        print((
                            "Traceback (most recent call last):"), file=self._stderr)
                        dopóki exc_tb:
                            print((
                                '  File "%s", line %s, w %s' %
                                (exc_tb.tb_frame.f_code.co_filename,
                                    exc_tb.tb_lineno,
                                    exc_tb.tb_frame.f_code.co_name)), file=self._stderr)
                            exc_tb = exc_tb.tb_next
                        print(("%s: %s" % (exc_type, exc_value)), file=self._stderr)
                    # Make sure that exc_tb gets deleted since it jest a memory
                    # hog; deleting everything inaczej jest just dla thoroughness
                    w_końcu:
                        usuń exc_type, exc_value, exc_tb
            w_końcu:
                # Prevent a race w
                # test_threading.test_no_refcycle_through_target when
                # the exception keeps the target alive past when we
                # assert that it's dead.
                #XXX self._exc_clear()
                dalej
        w_końcu:
            przy _active_limbo_lock:
                spróbuj:
                    # We don't call self._delete() because it also
                    # grabs _active_limbo_lock.
                    usuń _active[get_ident()]
                wyjąwszy:
                    dalej

    def _stop(self):
        # After calling ._stop(), .is_alive() returns Nieprawda oraz .join() returns
        # immediately.  ._tstate_lock must be released before calling ._stop().
        #
        # Normal case:  C code at the end of the thread's life
        # (release_sentinel w _threadmodule.c) releases ._tstate_lock, oraz
        # that's detected by our ._wait_for_tstate_lock(), called by .join()
        # oraz .is_alive().  Any number of threads _may_ call ._stop()
        # simultaneously (dla example, jeżeli multiple threads are blocked w
        # .join() calls), oraz they're nie serialized.  That's harmless -
        # they'll just make redundant rebindings of ._is_stopped oraz
        # ._tstate_lock.  Obscure:  we rebind ._tstate_lock last so that the
        # "assert self._is_stopped" w ._wait_for_tstate_lock() always works
        # (the assert jest executed only jeżeli ._tstate_lock jest Nic).
        #
        # Special case:  _main_thread releases ._tstate_lock via this
        # module's _shutdown() function.
        lock = self._tstate_lock
        jeżeli lock jest nie Nic:
            assert nie lock.locked()
        self._is_stopped = Prawda
        self._tstate_lock = Nic

    def _delete(self):
        "Remove current thread z the dict of currently running threads."

        # Notes about running przy _dummy_thread:
        #
        # Must take care to nie podnieś an exception jeżeli _dummy_thread jest being
        # used (and thus this module jest being used jako an instance of
        # dummy_threading).  _dummy_thread.get_ident() always returns -1 since
        # there jest only one thread jeżeli _dummy_thread jest being used.  Thus
        # len(_active) jest always <= 1 here, oraz any Thread instance created
        # overwrites the (jeżeli any) thread currently registered w _active.
        #
        # An instance of _MainThread jest always created by 'threading'.  This
        # gets overwritten the instant an instance of Thread jest created; both
        # threads zwróć -1 z _dummy_thread.get_ident() oraz thus have the
        # same key w the dict.  So when the _MainThread instance created by
        # 'threading' tries to clean itself up when atexit calls this method
        # it gets a KeyError jeżeli another Thread instance was created.
        #
        # This all means that KeyError z trying to delete something from
        # _active jeżeli dummy_threading jest being used jest a red herring.  But
        # since it isn't jeżeli dummy_threading jest *not* being used then don't
        # hide the exception.

        spróbuj:
            przy _active_limbo_lock:
                usuń _active[get_ident()]
                # There must nie be any python code between the previous line
                # oraz after the lock jest released.  Otherwise a tracing function
                # could try to acquire the lock again w the same thread, (in
                # current_thread()), oraz would block.
        wyjąwszy KeyError:
            jeżeli 'dummy_threading' nie w _sys.modules:
                podnieś

    def join(self, timeout=Nic):
        """Wait until the thread terminates.

        This blocks the calling thread until the thread whose join() method jest
        called terminates -- either normally albo through an unhandled exception
        albo until the optional timeout occurs.

        When the timeout argument jest present oraz nie Nic, it should be a
        floating point number specifying a timeout dla the operation w seconds
        (or fractions thereof). As join() always returns Nic, you must call
        isAlive() after join() to decide whether a timeout happened -- jeżeli the
        thread jest still alive, the join() call timed out.

        When the timeout argument jest nie present albo Nic, the operation will
        block until the thread terminates.

        A thread can be join()ed many times.

        join() podnieśs a RuntimeError jeżeli an attempt jest made to join the current
        thread jako that would cause a deadlock. It jest also an error to join() a
        thread before it has been started oraz attempts to do so podnieśs the same
        exception.

        """
        jeżeli nie self._initialized:
            podnieś RuntimeError("Thread.__init__() nie called")
        jeżeli nie self._started.is_set():
            podnieś RuntimeError("cannot join thread before it jest started")
        jeżeli self jest current_thread():
            podnieś RuntimeError("cannot join current thread")

        jeżeli timeout jest Nic:
            self._wait_for_tstate_lock()
        inaczej:
            # the behavior of a negative timeout isn't documented, but
            # historically .join(timeout=x) dla x<0 has acted jako jeżeli timeout=0
            self._wait_for_tstate_lock(timeout=max(timeout, 0))

    def _wait_for_tstate_lock(self, block=Prawda, timeout=-1):
        # Issue #18808: wait dla the thread state to be gone.
        # At the end of the thread's life, after all knowledge of the thread
        # jest removed z C data structures, C code releases our _tstate_lock.
        # This method dalejes its arguments to _tstate_lock.aquire().
        # If the lock jest acquired, the C code jest done, oraz self._stop() jest
        # called.  That sets ._is_stopped to Prawda, oraz ._tstate_lock to Nic.
        lock = self._tstate_lock
        jeżeli lock jest Nic:  # already determined that the C code jest done
            assert self._is_stopped
        albo_inaczej lock.acquire(block, timeout):
            lock.release()
            self._stop()

    @property
    def name(self):
        """A string used dla identification purposes only.

        It has no semantics. Multiple threads may be given the same name. The
        initial name jest set by the constructor.

        """
        assert self._initialized, "Thread.__init__() nie called"
        zwróć self._name

    @name.setter
    def name(self, name):
        assert self._initialized, "Thread.__init__() nie called"
        self._name = str(name)

    @property
    def ident(self):
        """Thread identifier of this thread albo Nic jeżeli it has nie been started.

        This jest a nonzero integer. See the thread.get_ident() function. Thread
        identifiers may be recycled when a thread exits oraz another thread jest
        created. The identifier jest available even after the thread has exited.

        """
        assert self._initialized, "Thread.__init__() nie called"
        zwróć self._ident

    def is_alive(self):
        """Return whether the thread jest alive.

        This method returns Prawda just before the run() method starts until just
        after the run() method terminates. The module function enumerate()
        returns a list of all alive threads.

        """
        assert self._initialized, "Thread.__init__() nie called"
        jeżeli self._is_stopped albo nie self._started.is_set():
            zwróć Nieprawda
        self._wait_for_tstate_lock(Nieprawda)
        zwróć nie self._is_stopped

    isAlive = is_alive

    @property
    def daemon(self):
        """A boolean value indicating whether this thread jest a daemon thread.

        This must be set before start() jest called, otherwise RuntimeError jest
        podnieśd. Its initial value jest inherited z the creating thread; the
        main thread jest nie a daemon thread oraz therefore all threads created w
        the main thread default to daemon = Nieprawda.

        The entire Python program exits when no alive non-daemon threads are
        left.

        """
        assert self._initialized, "Thread.__init__() nie called"
        zwróć self._daemonic

    @daemon.setter
    def daemon(self, daemonic):
        jeżeli nie self._initialized:
            podnieś RuntimeError("Thread.__init__() nie called")
        jeżeli self._started.is_set():
            podnieś RuntimeError("cannot set daemon status of active thread")
        self._daemonic = daemonic

    def isDaemon(self):
        zwróć self.daemon

    def setDaemon(self, daemonic):
        self.daemon = daemonic

    def getName(self):
        zwróć self.name

    def setName(self, name):
        self.name = name

# The timer klasa was contributed by Itamar Shtull-Trauring

klasa Timer(Thread):
    """Call a function after a specified number of seconds:

            t = Timer(30.0, f, args=Nic, kwargs=Nic)
            t.start()
            t.cancel()     # stop the timer's action jeżeli it's still waiting

    """

    def __init__(self, interval, function, args=Nic, kwargs=Nic):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args jeżeli args jest nie Nic inaczej []
        self.kwargs = kwargs jeżeli kwargs jest nie Nic inaczej {}
        self.finished = Event()

    def cancel(self):
        """Stop the timer jeżeli it hasn't finished yet."""
        self.finished.set()

    def run(self):
        self.finished.wait(self.interval)
        jeżeli nie self.finished.is_set():
            self.function(*self.args, **self.kwargs)
        self.finished.set()

# Special thread klasa to represent the main thread
# This jest garbage collected through an exit handler

klasa _MainThread(Thread):

    def __init__(self):
        Thread.__init__(self, name="MainThread", daemon=Nieprawda)
        self._set_tstate_lock()
        self._started.set()
        self._set_ident()
        przy _active_limbo_lock:
            _active[self._ident] = self


# Dummy thread klasa to represent threads nie started here.
# These aren't garbage collected when they die, nor can they be waited for.
# If they invoke anything w threading.py that calls current_thread(), they
# leave an entry w the _active dict forever after.
# Their purpose jest to zwróć *something* z current_thread().
# They are marked jako daemon threads so we won't wait dla them
# when we exit (conform previous semantics).

klasa _DummyThread(Thread):

    def __init__(self):
        Thread.__init__(self, name=_newname("Dummy-%d"), daemon=Prawda)

        self._started.set()
        self._set_ident()
        przy _active_limbo_lock:
            _active[self._ident] = self

    def _stop(self):
        dalej

    def join(self, timeout=Nic):
        assert Nieprawda, "cannot join a dummy thread"


# Global API functions

def current_thread():
    """Return the current Thread object, corresponding to the caller's thread of control.

    If the caller's thread of control was nie created through the threading
    module, a dummy thread object przy limited functionality jest returned.

    """
    spróbuj:
        zwróć _active[get_ident()]
    wyjąwszy KeyError:
        zwróć _DummyThread()

currentThread = current_thread

def active_count():
    """Return the number of Thread objects currently alive.

    The returned count jest equal to the length of the list returned by
    enumerate().

    """
    przy _active_limbo_lock:
        zwróć len(_active) + len(_limbo)

activeCount = active_count

def _enumerate():
    # Same jako enumerate(), but without the lock. Internal use only.
    zwróć list(_active.values()) + list(_limbo.values())

def enumerate():
    """Return a list of all Thread objects currently alive.

    The list includes daemonic threads, dummy thread objects created by
    current_thread(), oraz the main thread. It excludes terminated threads oraz
    threads that have nie yet been started.

    """
    przy _active_limbo_lock:
        zwróć list(_active.values()) + list(_limbo.values())

z _thread zaimportuj stack_size

# Create the main thread object,
# oraz make it available dla the interpreter
# (Py_Main) jako threading._shutdown.

_main_thread = _MainThread()

def _shutdown():
    # Obscure:  other threads may be waiting to join _main_thread.  That's
    # dubious, but some code does it.  We can't wait dla C code to release
    # the main thread's tstate_lock - that won't happen until the interpreter
    # jest nearly dead.  So we release it here.  Note that just calling _stop()
    # isn't enough:  other threads may already be waiting on _tstate_lock.
    tlock = _main_thread._tstate_lock
    # The main thread isn't finished yet, so its thread state lock can't have
    # been released.
    assert tlock jest nie Nic
    assert tlock.locked()
    tlock.release()
    _main_thread._stop()
    t = _pickSomeNonDaemonThread()
    dopóki t:
        t.join()
        t = _pickSomeNonDaemonThread()
    _main_thread._delete()

def _pickSomeNonDaemonThread():
    dla t w enumerate():
        jeżeli nie t.daemon oraz t.is_alive():
            zwróć t
    zwróć Nic

def main_thread():
    """Return the main thread object.

    In normal conditions, the main thread jest the thread z which the
    Python interpreter was started.
    """
    zwróć _main_thread

# get thread-local implementation, either z the thread
# module, albo z the python fallback

spróbuj:
    z _thread zaimportuj _local jako local
wyjąwszy ImportError:
    z _threading_local zaimportuj local


def _after_fork():
    # This function jest called by Python/ceval.c:PyEval_ReInitThreads which
    # jest called z PyOS_AfterFork.  Here we cleanup threading module state
    # that should nie exist after a fork.

    # Reset _active_limbo_lock, w case we forked dopóki the lock was held
    # by another (non-forked) thread.  http://bugs.python.org/issue874900
    global _active_limbo_lock, _main_thread
    _active_limbo_lock = _allocate_lock()

    # fork() only copied the current thread; clear references to others.
    new_active = {}
    current = current_thread()
    _main_thread = current
    przy _active_limbo_lock:
        # Dangling thread instances must still have their locks reset,
        # because someone may join() them.
        threads = set(_enumerate())
        threads.update(_dangling)
        dla thread w threads:
            # Any lock/condition variable may be currently locked albo w an
            # invalid state, so we reinitialize them.
            jeżeli thread jest current:
                # There jest only one active thread. We reset the ident to
                # its new value since it can have changed.
                thread._reset_internal_locks(Prawda)
                ident = get_ident()
                thread._ident = ident
                new_active[ident] = thread
            inaczej:
                # All the others are already stopped.
                thread._reset_internal_locks(Nieprawda)
                thread._stop()

        _limbo.clear()
        _active.clear()
        _active.update(new_active)
        assert len(_active) == 1
