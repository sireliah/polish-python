"""Synchronization primitives."""

__all__ = ['Lock', 'Event', 'Condition', 'Semaphore', 'BoundedSemaphore']

zaimportuj collections

z . zaimportuj compat
z . zaimportuj events
z . zaimportuj futures
z .coroutines zaimportuj coroutine


klasa _ContextManager:
    """Context manager.

    This enables the following idiom dla acquiring oraz releasing a
    lock around a block:

        przy (uzyskaj z lock):
            <block>

    dopóki failing loudly when accidentally using:

        przy lock:
            <block>
    """

    def __init__(self, lock):
        self._lock = lock

    def __enter__(self):
        # We have no use dla the "as ..."  clause w the with
        # statement dla locks.
        zwróć Nic

    def __exit__(self, *args):
        spróbuj:
            self._lock.release()
        w_końcu:
            self._lock = Nic  # Crudely prevent reuse.


klasa _ContextManagerMixin:
    def __enter__(self):
        podnieś RuntimeError(
            '"uzyskaj from" should be used jako context manager expression')

    def __exit__(self, *args):
        # This must exist because __enter__ exists, even though that
        # always podnieśs; that's how the with-statement works.
        dalej

    @coroutine
    def __iter__(self):
        # This jest nie a coroutine.  It jest meant to enable the idiom:
        #
        #     przy (uzyskaj z lock):
        #         <block>
        #
        # jako an alternative to:
        #
        #     uzyskaj z lock.acquire()
        #     spróbuj:
        #         <block>
        #     w_końcu:
        #         lock.release()
        uzyskaj z self.acquire()
        zwróć _ContextManager(self)

    jeżeli compat.PY35:

        def __await__(self):
            # To make "przy await lock" work.
            uzyskaj z self.acquire()
            zwróć _ContextManager(self)

        @coroutine
        def __aenter__(self):
            uzyskaj z self.acquire()
            # We have no use dla the "as ..."  clause w the with
            # statement dla locks.
            zwróć Nic

        @coroutine
        def __aexit__(self, exc_type, exc, tb):
            self.release()


klasa Lock(_ContextManagerMixin):
    """Primitive lock objects.

    A primitive lock jest a synchronization primitive that jest nie owned
    by a particular coroutine when locked.  A primitive lock jest w one
    of two states, 'locked' albo 'unlocked'.

    It jest created w the unlocked state.  It has two basic methods,
    acquire() oraz release().  When the state jest unlocked, acquire()
    changes the state to locked oraz returns immediately.  When the
    state jest locked, acquire() blocks until a call to release() w
    another coroutine changes it to unlocked, then the acquire() call
    resets it to locked oraz returns.  The release() method should only
    be called w the locked state; it changes the state to unlocked
    oraz returns immediately.  If an attempt jest made to release an
    unlocked lock, a RuntimeError will be podnieśd.

    When more than one coroutine jest blocked w acquire() waiting for
    the state to turn to unlocked, only one coroutine proceeds when a
    release() call resets the state to unlocked; first coroutine which
    jest blocked w acquire() jest being processed.

    acquire() jest a coroutine oraz should be called przy 'uzyskaj from'.

    Locks also support the context management protocol.  '(uzyskaj z lock)'
    should be used jako context manager expression.

    Usage:

        lock = Lock()
        ...
        uzyskaj z lock
        spróbuj:
            ...
        w_końcu:
            lock.release()

    Context manager usage:

        lock = Lock()
        ...
        przy (uzyskaj z lock):
             ...

    Lock objects can be tested dla locking state:

        jeżeli nie lock.locked():
           uzyskaj z lock
        inaczej:
           # lock jest acquired
           ...

    """

    def __init__(self, *, loop=Nic):
        self._waiters = collections.deque()
        self._locked = Nieprawda
        jeżeli loop jest nie Nic:
            self._loop = loop
        inaczej:
            self._loop = events.get_event_loop()

    def __repr__(self):
        res = super().__repr__()
        extra = 'locked' jeżeli self._locked inaczej 'unlocked'
        jeżeli self._waiters:
            extra = '{},waiters:{}'.format(extra, len(self._waiters))
        zwróć '<{} [{}]>'.format(res[1:-1], extra)

    def locked(self):
        """Return Prawda jeżeli lock jest acquired."""
        zwróć self._locked

    @coroutine
    def acquire(self):
        """Acquire a lock.

        This method blocks until the lock jest unlocked, then sets it to
        locked oraz returns Prawda.
        """
        jeżeli nie self._waiters oraz nie self._locked:
            self._locked = Prawda
            zwróć Prawda

        fut = futures.Future(loop=self._loop)
        self._waiters.append(fut)
        spróbuj:
            uzyskaj z fut
            self._locked = Prawda
            zwróć Prawda
        w_końcu:
            self._waiters.remove(fut)

    def release(self):
        """Release a lock.

        When the lock jest locked, reset it to unlocked, oraz return.
        If any other coroutines are blocked waiting dla the lock to become
        unlocked, allow exactly one of them to proceed.

        When invoked on an unlocked lock, a RuntimeError jest podnieśd.

        There jest no zwróć value.
        """
        jeżeli self._locked:
            self._locked = Nieprawda
            # Wake up the first waiter who isn't cancelled.
            dla fut w self._waiters:
                jeżeli nie fut.done():
                    fut.set_result(Prawda)
                    przerwij
        inaczej:
            podnieś RuntimeError('Lock jest nie acquired.')


klasa Event:
    """Asynchronous equivalent to threading.Event.

    Class implementing event objects. An event manages a flag that can be set
    to true przy the set() method oraz reset to false przy the clear() method.
    The wait() method blocks until the flag jest true. The flag jest initially
    false.
    """

    def __init__(self, *, loop=Nic):
        self._waiters = collections.deque()
        self._value = Nieprawda
        jeżeli loop jest nie Nic:
            self._loop = loop
        inaczej:
            self._loop = events.get_event_loop()

    def __repr__(self):
        res = super().__repr__()
        extra = 'set' jeżeli self._value inaczej 'unset'
        jeżeli self._waiters:
            extra = '{},waiters:{}'.format(extra, len(self._waiters))
        zwróć '<{} [{}]>'.format(res[1:-1], extra)

    def is_set(self):
        """Return Prawda jeżeli oraz only jeżeli the internal flag jest true."""
        zwróć self._value

    def set(self):
        """Set the internal flag to true. All coroutines waiting dla it to
        become true are awakened. Coroutine that call wait() once the flag jest
        true will nie block at all.
        """
        jeżeli nie self._value:
            self._value = Prawda

            dla fut w self._waiters:
                jeżeli nie fut.done():
                    fut.set_result(Prawda)

    def clear(self):
        """Reset the internal flag to false. Subsequently, coroutines calling
        wait() will block until set() jest called to set the internal flag
        to true again."""
        self._value = Nieprawda

    @coroutine
    def wait(self):
        """Block until the internal flag jest true.

        If the internal flag jest true on entry, zwróć Prawda
        immediately.  Otherwise, block until another coroutine calls
        set() to set the flag to true, then zwróć Prawda.
        """
        jeżeli self._value:
            zwróć Prawda

        fut = futures.Future(loop=self._loop)
        self._waiters.append(fut)
        spróbuj:
            uzyskaj z fut
            zwróć Prawda
        w_końcu:
            self._waiters.remove(fut)


klasa Condition(_ContextManagerMixin):
    """Asynchronous equivalent to threading.Condition.

    This klasa implements condition variable objects. A condition variable
    allows one albo more coroutines to wait until they are notified by another
    coroutine.

    A new Lock object jest created oraz used jako the underlying lock.
    """

    def __init__(self, lock=Nic, *, loop=Nic):
        jeżeli loop jest nie Nic:
            self._loop = loop
        inaczej:
            self._loop = events.get_event_loop()

        jeżeli lock jest Nic:
            lock = Lock(loop=self._loop)
        albo_inaczej lock._loop jest nie self._loop:
            podnieś ValueError("loop argument must agree przy lock")

        self._lock = lock
        # Export the lock's locked(), acquire() oraz release() methods.
        self.locked = lock.locked
        self.acquire = lock.acquire
        self.release = lock.release

        self._waiters = collections.deque()

    def __repr__(self):
        res = super().__repr__()
        extra = 'locked' jeżeli self.locked() inaczej 'unlocked'
        jeżeli self._waiters:
            extra = '{},waiters:{}'.format(extra, len(self._waiters))
        zwróć '<{} [{}]>'.format(res[1:-1], extra)

    @coroutine
    def wait(self):
        """Wait until notified.

        If the calling coroutine has nie acquired the lock when this
        method jest called, a RuntimeError jest podnieśd.

        This method releases the underlying lock, oraz then blocks
        until it jest awakened by a notify() albo notify_all() call for
        the same condition variable w another coroutine.  Once
        awakened, it re-acquires the lock oraz returns Prawda.
        """
        jeżeli nie self.locked():
            podnieś RuntimeError('cannot wait on un-acquired lock')

        self.release()
        spróbuj:
            fut = futures.Future(loop=self._loop)
            self._waiters.append(fut)
            spróbuj:
                uzyskaj z fut
                zwróć Prawda
            w_końcu:
                self._waiters.remove(fut)

        w_końcu:
            uzyskaj z self.acquire()

    @coroutine
    def wait_for(self, predicate):
        """Wait until a predicate becomes true.

        The predicate should be a callable which result will be
        interpreted jako a boolean value.  The final predicate value jest
        the zwróć value.
        """
        result = predicate()
        dopóki nie result:
            uzyskaj z self.wait()
            result = predicate()
        zwróć result

    def notify(self, n=1):
        """By default, wake up one coroutine waiting on this condition, jeżeli any.
        If the calling coroutine has nie acquired the lock when this method
        jest called, a RuntimeError jest podnieśd.

        This method wakes up at most n of the coroutines waiting dla the
        condition variable; it jest a no-op jeżeli no coroutines are waiting.

        Note: an awakened coroutine does nie actually zwróć z its
        wait() call until it can reacquire the lock. Since notify() does
        nie release the lock, its caller should.
        """
        jeżeli nie self.locked():
            podnieś RuntimeError('cannot notify on un-acquired lock')

        idx = 0
        dla fut w self._waiters:
            jeżeli idx >= n:
                przerwij

            jeżeli nie fut.done():
                idx += 1
                fut.set_result(Nieprawda)

    def notify_all(self):
        """Wake up all threads waiting on this condition. This method acts
        like notify(), but wakes up all waiting threads instead of one. If the
        calling thread has nie acquired the lock when this method jest called,
        a RuntimeError jest podnieśd.
        """
        self.notify(len(self._waiters))


klasa Semaphore(_ContextManagerMixin):
    """A Semaphore implementation.

    A semaphore manages an internal counter which jest decremented by each
    acquire() call oraz incremented by each release() call. The counter
    can never go below zero; when acquire() finds that it jest zero, it blocks,
    waiting until some other thread calls release().

    Semaphores also support the context management protocol.

    The optional argument gives the initial value dla the internal
    counter; it defaults to 1. If the value given jest less than 0,
    ValueError jest podnieśd.
    """

    def __init__(self, value=1, *, loop=Nic):
        jeżeli value < 0:
            podnieś ValueError("Semaphore initial value must be >= 0")
        self._value = value
        self._waiters = collections.deque()
        jeżeli loop jest nie Nic:
            self._loop = loop
        inaczej:
            self._loop = events.get_event_loop()

    def __repr__(self):
        res = super().__repr__()
        extra = 'locked' jeżeli self.locked() inaczej 'unlocked,value:{}'.format(
            self._value)
        jeżeli self._waiters:
            extra = '{},waiters:{}'.format(extra, len(self._waiters))
        zwróć '<{} [{}]>'.format(res[1:-1], extra)

    def locked(self):
        """Returns Prawda jeżeli semaphore can nie be acquired immediately."""
        zwróć self._value == 0

    @coroutine
    def acquire(self):
        """Acquire a semaphore.

        If the internal counter jest larger than zero on entry,
        decrement it by one oraz zwróć Prawda immediately.  If it jest
        zero on entry, block, waiting until some other coroutine has
        called release() to make it larger than 0, oraz then zwróć
        Prawda.
        """
        jeżeli nie self._waiters oraz self._value > 0:
            self._value -= 1
            zwróć Prawda

        fut = futures.Future(loop=self._loop)
        self._waiters.append(fut)
        spróbuj:
            uzyskaj z fut
            self._value -= 1
            zwróć Prawda
        w_końcu:
            self._waiters.remove(fut)

    def release(self):
        """Release a semaphore, incrementing the internal counter by one.
        When it was zero on entry oraz another coroutine jest waiting dla it to
        become larger than zero again, wake up that coroutine.
        """
        self._value += 1
        dla waiter w self._waiters:
            jeżeli nie waiter.done():
                waiter.set_result(Prawda)
                przerwij


klasa BoundedSemaphore(Semaphore):
    """A bounded semaphore implementation.

    This podnieśs ValueError w release() jeżeli it would increase the value
    above the initial value.
    """

    def __init__(self, value=1, *, loop=Nic):
        self._bound_value = value
        super().__init__(value, loop=loop)

    def release(self):
        jeżeli self._value >= self._bound_value:
            podnieś ValueError('BoundedSemaphore released too many times')
        super().release()
