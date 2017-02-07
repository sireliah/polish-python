# Copyright 2009 Brian Quinlan. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

__author__ = 'Brian Quinlan (brian@sweetapp.com)'

zaimportuj collections
zaimportuj logging
zaimportuj threading
zaimportuj time

FIRST_COMPLETED = 'FIRST_COMPLETED'
FIRST_EXCEPTION = 'FIRST_EXCEPTION'
ALL_COMPLETED = 'ALL_COMPLETED'
_AS_COMPLETED = '_AS_COMPLETED'

# Possible future states (dla internal use by the futures package).
PENDING = 'PENDING'
RUNNING = 'RUNNING'
# The future was cancelled by the user...
CANCELLED = 'CANCELLED'
# ...and _Waiter.add_cancelled() was called by a worker.
CANCELLED_AND_NOTIFIED = 'CANCELLED_AND_NOTIFIED'
FINISHED = 'FINISHED'

_FUTURE_STATES = [
    PENDING,
    RUNNING,
    CANCELLED,
    CANCELLED_AND_NOTIFIED,
    FINISHED
]

_STATE_TO_DESCRIPTION_MAP = {
    PENDING: "pending",
    RUNNING: "running",
    CANCELLED: "cancelled",
    CANCELLED_AND_NOTIFIED: "cancelled",
    FINISHED: "finished"
}

# Logger dla internal use by the futures package.
LOGGER = logging.getLogger("concurrent.futures")

klasa Error(Exception):
    """Base klasa dla all future-related exceptions."""
    dalej

klasa CancelledError(Error):
    """The Future was cancelled."""
    dalej

klasa TimeoutError(Error):
    """The operation exceeded the given deadline."""
    dalej

klasa _Waiter(object):
    """Provides the event that wait() oraz as_completed() block on."""
    def __init__(self):
        self.event = threading.Event()
        self.finished_futures = []

    def add_result(self, future):
        self.finished_futures.append(future)

    def add_exception(self, future):
        self.finished_futures.append(future)

    def add_cancelled(self, future):
        self.finished_futures.append(future)

klasa _AsCompletedWaiter(_Waiter):
    """Used by as_completed()."""

    def __init__(self):
        super(_AsCompletedWaiter, self).__init__()
        self.lock = threading.Lock()

    def add_result(self, future):
        przy self.lock:
            super(_AsCompletedWaiter, self).add_result(future)
            self.event.set()

    def add_exception(self, future):
        przy self.lock:
            super(_AsCompletedWaiter, self).add_exception(future)
            self.event.set()

    def add_cancelled(self, future):
        przy self.lock:
            super(_AsCompletedWaiter, self).add_cancelled(future)
            self.event.set()

klasa _FirstCompletedWaiter(_Waiter):
    """Used by wait(return_when=FIRST_COMPLETED)."""

    def add_result(self, future):
        super().add_result(future)
        self.event.set()

    def add_exception(self, future):
        super().add_exception(future)
        self.event.set()

    def add_cancelled(self, future):
        super().add_cancelled(future)
        self.event.set()

klasa _AllCompletedWaiter(_Waiter):
    """Used by wait(return_when=FIRST_EXCEPTION oraz ALL_COMPLETED)."""

    def __init__(self, num_pending_calls, stop_on_exception):
        self.num_pending_calls = num_pending_calls
        self.stop_on_exception = stop_on_exception
        self.lock = threading.Lock()
        super().__init__()

    def _decrement_pending_calls(self):
        przy self.lock:
            self.num_pending_calls -= 1
            jeżeli nie self.num_pending_calls:
                self.event.set()

    def add_result(self, future):
        super().add_result(future)
        self._decrement_pending_calls()

    def add_exception(self, future):
        super().add_exception(future)
        jeżeli self.stop_on_exception:
            self.event.set()
        inaczej:
            self._decrement_pending_calls()

    def add_cancelled(self, future):
        super().add_cancelled(future)
        self._decrement_pending_calls()

klasa _AcquireFutures(object):
    """A context manager that does an ordered acquire of Future conditions."""

    def __init__(self, futures):
        self.futures = sorted(futures, key=id)

    def __enter__(self):
        dla future w self.futures:
            future._condition.acquire()

    def __exit__(self, *args):
        dla future w self.futures:
            future._condition.release()

def _create_and_install_waiters(fs, return_when):
    jeżeli return_when == _AS_COMPLETED:
        waiter = _AsCompletedWaiter()
    albo_inaczej return_when == FIRST_COMPLETED:
        waiter = _FirstCompletedWaiter()
    inaczej:
        pending_count = sum(
                f._state nie w [CANCELLED_AND_NOTIFIED, FINISHED] dla f w fs)

        jeżeli return_when == FIRST_EXCEPTION:
            waiter = _AllCompletedWaiter(pending_count, stop_on_exception=Prawda)
        albo_inaczej return_when == ALL_COMPLETED:
            waiter = _AllCompletedWaiter(pending_count, stop_on_exception=Nieprawda)
        inaczej:
            podnieś ValueError("Invalid zwróć condition: %r" % return_when)

    dla f w fs:
        f._waiters.append(waiter)

    zwróć waiter

def as_completed(fs, timeout=Nic):
    """An iterator over the given futures that uzyskajs each jako it completes.

    Args:
        fs: The sequence of Futures (possibly created by different Executors) to
            iterate over.
        timeout: The maximum number of seconds to wait. If Nic, then there
            jest no limit on the wait time.

    Returns:
        An iterator that uzyskajs the given Futures jako they complete (finished albo
        cancelled). If any given Futures are duplicated, they will be returned
        once.

    Raises:
        TimeoutError: If the entire result iterator could nie be generated
            before the given timeout.
    """
    jeżeli timeout jest nie Nic:
        end_time = timeout + time.time()

    fs = set(fs)
    przy _AcquireFutures(fs):
        finished = set(
                f dla f w fs
                jeżeli f._state w [CANCELLED_AND_NOTIFIED, FINISHED])
        pending = fs - finished
        waiter = _create_and_install_waiters(fs, _AS_COMPLETED)

    spróbuj:
        uzyskaj z finished

        dopóki pending:
            jeżeli timeout jest Nic:
                wait_timeout = Nic
            inaczej:
                wait_timeout = end_time - time.time()
                jeżeli wait_timeout < 0:
                    podnieś TimeoutError(
                            '%d (of %d) futures unfinished' % (
                            len(pending), len(fs)))

            waiter.event.wait(wait_timeout)

            przy waiter.lock:
                finished = waiter.finished_futures
                waiter.finished_futures = []
                waiter.event.clear()

            dla future w finished:
                uzyskaj future
                pending.remove(future)

    w_końcu:
        dla f w fs:
            przy f._condition:
                f._waiters.remove(waiter)

DoneAndNotDoneFutures = collections.namedtuple(
        'DoneAndNotDoneFutures', 'done not_done')
def wait(fs, timeout=Nic, return_when=ALL_COMPLETED):
    """Wait dla the futures w the given sequence to complete.

    Args:
        fs: The sequence of Futures (possibly created by different Executors) to
            wait upon.
        timeout: The maximum number of seconds to wait. If Nic, then there
            jest no limit on the wait time.
        return_when: Indicates when this function should return. The options
            are:

            FIRST_COMPLETED - Return when any future finishes albo jest
                              cancelled.
            FIRST_EXCEPTION - Return when any future finishes by raising an
                              exception. If no future podnieśs an exception
                              then it jest equivalent to ALL_COMPLETED.
            ALL_COMPLETED -   Return when all futures finish albo are cancelled.

    Returns:
        A named 2-tuple of sets. The first set, named 'done', contains the
        futures that completed (is finished albo cancelled) before the wait
        completed. The second set, named 'not_done', contains uncompleted
        futures.
    """
    przy _AcquireFutures(fs):
        done = set(f dla f w fs
                   jeżeli f._state w [CANCELLED_AND_NOTIFIED, FINISHED])
        not_done = set(fs) - done

        jeżeli (return_when == FIRST_COMPLETED) oraz done:
            zwróć DoneAndNotDoneFutures(done, not_done)
        albo_inaczej (return_when == FIRST_EXCEPTION) oraz done:
            jeżeli any(f dla f w done
                   jeżeli nie f.cancelled() oraz f.exception() jest nie Nic):
                zwróć DoneAndNotDoneFutures(done, not_done)

        jeżeli len(done) == len(fs):
            zwróć DoneAndNotDoneFutures(done, not_done)

        waiter = _create_and_install_waiters(fs, return_when)

    waiter.event.wait(timeout)
    dla f w fs:
        przy f._condition:
            f._waiters.remove(waiter)

    done.update(waiter.finished_futures)
    zwróć DoneAndNotDoneFutures(done, set(fs) - done)

klasa Future(object):
    """Represents the result of an asynchronous computation."""

    def __init__(self):
        """Initializes the future. Should nie be called by clients."""
        self._condition = threading.Condition()
        self._state = PENDING
        self._result = Nic
        self._exception = Nic
        self._waiters = []
        self._done_callbacks = []

    def _invoke_callbacks(self):
        dla callback w self._done_callbacks:
            spróbuj:
                callback(self)
            wyjąwszy Exception:
                LOGGER.exception('exception calling callback dla %r', self)

    def __repr__(self):
        przy self._condition:
            jeżeli self._state == FINISHED:
                jeżeli self._exception:
                    zwróć '<%s at %#x state=%s podnieśd %s>' % (
                        self.__class__.__name__,
                        id(self),
                        _STATE_TO_DESCRIPTION_MAP[self._state],
                        self._exception.__class__.__name__)
                inaczej:
                    zwróć '<%s at %#x state=%s returned %s>' % (
                        self.__class__.__name__,
                        id(self),
                        _STATE_TO_DESCRIPTION_MAP[self._state],
                        self._result.__class__.__name__)
            zwróć '<%s at %#x state=%s>' % (
                    self.__class__.__name__,
                    id(self),
                   _STATE_TO_DESCRIPTION_MAP[self._state])

    def cancel(self):
        """Cancel the future jeżeli possible.

        Returns Prawda jeżeli the future was cancelled, Nieprawda otherwise. A future
        cannot be cancelled jeżeli it jest running albo has already completed.
        """
        przy self._condition:
            jeżeli self._state w [RUNNING, FINISHED]:
                zwróć Nieprawda

            jeżeli self._state w [CANCELLED, CANCELLED_AND_NOTIFIED]:
                zwróć Prawda

            self._state = CANCELLED
            self._condition.notify_all()

        self._invoke_callbacks()
        zwróć Prawda

    def cancelled(self):
        """Return Prawda jeżeli the future was cancelled."""
        przy self._condition:
            zwróć self._state w [CANCELLED, CANCELLED_AND_NOTIFIED]

    def running(self):
        """Return Prawda jeżeli the future jest currently executing."""
        przy self._condition:
            zwróć self._state == RUNNING

    def done(self):
        """Return Prawda of the future was cancelled albo finished executing."""
        przy self._condition:
            zwróć self._state w [CANCELLED, CANCELLED_AND_NOTIFIED, FINISHED]

    def __get_result(self):
        jeżeli self._exception:
            podnieś self._exception
        inaczej:
            zwróć self._result

    def add_done_callback(self, fn):
        """Attaches a callable that will be called when the future finishes.

        Args:
            fn: A callable that will be called przy this future jako its only
                argument when the future completes albo jest cancelled. The callable
                will always be called by a thread w the same process w which
                it was added. If the future has already completed albo been
                cancelled then the callable will be called immediately. These
                callables are called w the order that they were added.
        """
        przy self._condition:
            jeżeli self._state nie w [CANCELLED, CANCELLED_AND_NOTIFIED, FINISHED]:
                self._done_callbacks.append(fn)
                zwróć
        fn(self)

    def result(self, timeout=Nic):
        """Return the result of the call that the future represents.

        Args:
            timeout: The number of seconds to wait dla the result jeżeli the future
                isn't done. If Nic, then there jest no limit on the wait time.

        Returns:
            The result of the call that the future represents.

        Raises:
            CancelledError: If the future was cancelled.
            TimeoutError: If the future didn't finish executing before the given
                timeout.
            Exception: If the call podnieśd then that exception will be podnieśd.
        """
        przy self._condition:
            jeżeli self._state w [CANCELLED, CANCELLED_AND_NOTIFIED]:
                podnieś CancelledError()
            albo_inaczej self._state == FINISHED:
                zwróć self.__get_result()

            self._condition.wait(timeout)

            jeżeli self._state w [CANCELLED, CANCELLED_AND_NOTIFIED]:
                podnieś CancelledError()
            albo_inaczej self._state == FINISHED:
                zwróć self.__get_result()
            inaczej:
                podnieś TimeoutError()

    def exception(self, timeout=Nic):
        """Return the exception podnieśd by the call that the future represents.

        Args:
            timeout: The number of seconds to wait dla the exception jeżeli the
                future isn't done. If Nic, then there jest no limit on the wait
                time.

        Returns:
            The exception podnieśd by the call that the future represents albo Nic
            jeżeli the call completed without raising.

        Raises:
            CancelledError: If the future was cancelled.
            TimeoutError: If the future didn't finish executing before the given
                timeout.
        """

        przy self._condition:
            jeżeli self._state w [CANCELLED, CANCELLED_AND_NOTIFIED]:
                podnieś CancelledError()
            albo_inaczej self._state == FINISHED:
                zwróć self._exception

            self._condition.wait(timeout)

            jeżeli self._state w [CANCELLED, CANCELLED_AND_NOTIFIED]:
                podnieś CancelledError()
            albo_inaczej self._state == FINISHED:
                zwróć self._exception
            inaczej:
                podnieś TimeoutError()

    # The following methods should only be used by Executors oraz w tests.
    def set_running_or_notify_cancel(self):
        """Mark the future jako running albo process any cancel notifications.

        Should only be used by Executor implementations oraz unit tests.

        If the future has been cancelled (cancel() was called oraz returned
        Prawda) then any threads waiting on the future completing (though calls
        to as_completed() albo wait()) are notified oraz Nieprawda jest returned.

        If the future was nie cancelled then it jest put w the running state
        (future calls to running() will zwróć Prawda) oraz Prawda jest returned.

        This method should be called by Executor implementations before
        executing the work associated przy this future. If this method returns
        Nieprawda then the work should nie be executed.

        Returns:
            Nieprawda jeżeli the Future was cancelled, Prawda otherwise.

        Raises:
            RuntimeError: jeżeli this method was already called albo jeżeli set_result()
                albo set_exception() was called.
        """
        przy self._condition:
            jeżeli self._state == CANCELLED:
                self._state = CANCELLED_AND_NOTIFIED
                dla waiter w self._waiters:
                    waiter.add_cancelled(self)
                # self._condition.notify_all() jest nie necessary because
                # self.cancel() triggers a notification.
                zwróć Nieprawda
            albo_inaczej self._state == PENDING:
                self._state = RUNNING
                zwróć Prawda
            inaczej:
                LOGGER.critical('Future %s w unexpected state: %s',
                                id(self),
                                self._state)
                podnieś RuntimeError('Future w unexpected state')

    def set_result(self, result):
        """Sets the zwróć value of work associated przy the future.

        Should only be used by Executor implementations oraz unit tests.
        """
        przy self._condition:
            self._result = result
            self._state = FINISHED
            dla waiter w self._waiters:
                waiter.add_result(self)
            self._condition.notify_all()
        self._invoke_callbacks()

    def set_exception(self, exception):
        """Sets the result of the future jako being the given exception.

        Should only be used by Executor implementations oraz unit tests.
        """
        przy self._condition:
            self._exception = exception
            self._state = FINISHED
            dla waiter w self._waiters:
                waiter.add_exception(self)
            self._condition.notify_all()
        self._invoke_callbacks()

klasa Executor(object):
    """This jest an abstract base klasa dla concrete asynchronous executors."""

    def submit(self, fn, *args, **kwargs):
        """Submits a callable to be executed przy the given arguments.

        Schedules the callable to be executed jako fn(*args, **kwargs) oraz returns
        a Future instance representing the execution of the callable.

        Returns:
            A Future representing the given call.
        """
        podnieś NotImplementedError()

    def map(self, fn, *iterables, timeout=Nic, chunksize=1):
        """Returns a iterator equivalent to map(fn, iter).

        Args:
            fn: A callable that will take jako many arguments jako there are
                dalejed iterables.
            timeout: The maximum number of seconds to wait. If Nic, then there
                jest no limit on the wait time.
            chunksize: The size of the chunks the iterable will be broken into
                before being dalejed to a child process. This argument jest only
                used by ProcessPoolExecutor; it jest ignored by
                ThreadPoolExecutor.

        Returns:
            An iterator equivalent to: map(func, *iterables) but the calls may
            be evaluated out-of-order.

        Raises:
            TimeoutError: If the entire result iterator could nie be generated
                before the given timeout.
            Exception: If fn(*args) podnieśs dla any values.
        """
        jeżeli timeout jest nie Nic:
            end_time = timeout + time.time()

        fs = [self.submit(fn, *args) dla args w zip(*iterables)]

        # Yield must be hidden w closure so that the futures are submitted
        # before the first iterator value jest required.
        def result_iterator():
            spróbuj:
                dla future w fs:
                    jeżeli timeout jest Nic:
                        uzyskaj future.result()
                    inaczej:
                        uzyskaj future.result(end_time - time.time())
            w_końcu:
                dla future w fs:
                    future.cancel()
        zwróć result_iterator()

    def shutdown(self, wait=Prawda):
        """Clean-up the resources associated przy the Executor.

        It jest safe to call this method several times. Otherwise, no other
        methods can be called after this one.

        Args:
            wait: If Prawda then shutdown will nie zwróć until all running
                futures have finished executing oraz the resources used by the
                executor have been reclaimed.
        """
        dalej

    def __enter__(self):
        zwróć self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown(wait=Prawda)
        zwróć Nieprawda
