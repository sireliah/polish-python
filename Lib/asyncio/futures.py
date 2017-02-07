"""A Future klasa similar to the one w PEP 3148."""

__all__ = ['CancelledError', 'TimeoutError',
           'InvalidStateError',
           'Future', 'wrap_future',
           ]

zaimportuj concurrent.futures._base
zaimportuj logging
zaimportuj reprlib
zaimportuj sys
zaimportuj traceback

z . zaimportuj compat
z . zaimportuj events

# States dla Future.
_PENDING = 'PENDING'
_CANCELLED = 'CANCELLED'
_FINISHED = 'FINISHED'

Error = concurrent.futures._base.Error
CancelledError = concurrent.futures.CancelledError
TimeoutError = concurrent.futures.TimeoutError

STACK_DEBUG = logging.DEBUG - 1  # heavy-duty debugging


klasa InvalidStateError(Error):
    """The operation jest nie allowed w this state."""


klasa _TracebackLogger:
    """Helper to log a traceback upon destruction jeżeli nie cleared.

    This solves a nasty problem przy Futures oraz Tasks that have an
    exception set: jeżeli nobody asks dla the exception, the exception jest
    never logged.  This violates the Zen of Python: 'Errors should
    never dalej silently.  Unless explicitly silenced.'

    However, we don't want to log the exception jako soon as
    set_exception() jest called: jeżeli the calling code jest written
    properly, it will get the exception oraz handle it properly.  But
    we *do* want to log it jeżeli result() albo exception() was never called
    -- otherwise developers waste a lot of time wondering why their
    buggy code fails silently.

    An earlier attempt added a __del__() method to the Future class
    itself, but this backfired because the presence of __del__()
    prevents garbage collection z przerwijing cycles.  A way out of
    this catch-22 jest to avoid having a __del__() method on the Future
    klasa itself, but instead to have a reference to a helper object
    przy a __del__() method that logs the traceback, where we ensure
    that the helper object doesn't participate w cycles, oraz only the
    Future has a reference to it.

    The helper object jest added when set_exception() jest called.  When
    the Future jest collected, oraz the helper jest present, the helper
    object jest also collected, oraz its __del__() method will log the
    traceback.  When the Future's result() albo exception() method jest
    called (and a helper object jest present), it removes the helper
    object, after calling its clear() method to prevent it from
    logging.

    One downside jest that we do a fair amount of work to extract the
    traceback z the exception, even when it jest never logged.  It
    would seem cheaper to just store the exception object, but that
    references the traceback, which references stack frames, which may
    reference the Future, which references the _TracebackLogger, oraz
    then the _TracebackLogger would be included w a cycle, which jest
    what we're trying to avoid!  As an optimization, we don't
    immediately format the exception; we only do the work when
    activate() jest called, which call jest delayed until after all the
    Future's callbacks have run.  Since usually a Future has at least
    one callback (typically set by 'uzyskaj from') oraz usually that
    callback extracts the callback, thereby removing the need to
    format the exception.

    PS. I don't claim credit dla this solution.  I first heard of it
    w a discussion about closing files when they are collected.
    """

    __slots__ = ('loop', 'source_traceback', 'exc', 'tb')

    def __init__(self, future, exc):
        self.loop = future._loop
        self.source_traceback = future._source_traceback
        self.exc = exc
        self.tb = Nic

    def activate(self):
        exc = self.exc
        jeżeli exc jest nie Nic:
            self.exc = Nic
            self.tb = traceback.format_exception(exc.__class__, exc,
                                                 exc.__traceback__)

    def clear(self):
        self.exc = Nic
        self.tb = Nic

    def __del__(self):
        jeżeli self.tb:
            msg = 'Future/Task exception was never retrieved\n'
            jeżeli self.source_traceback:
                src = ''.join(traceback.format_list(self.source_traceback))
                msg += 'Future/Task created at (most recent call last):\n'
                msg += '%s\n' % src.rstrip()
            msg += ''.join(self.tb).rstrip()
            self.loop.call_exception_handler({'message': msg})


klasa Future:
    """This klasa jest *almost* compatible przy concurrent.futures.Future.

    Differences:

    - result() oraz exception() do nie take a timeout argument oraz
      podnieś an exception when the future isn't done yet.

    - Callbacks registered przy add_done_callback() are always called
      via the event loop's call_soon_threadsafe().

    - This klasa jest nie compatible przy the wait() oraz as_completed()
      methods w the concurrent.futures package.

    (In Python 3.4 albo later we may be able to unify the implementations.)
    """

    # Class variables serving jako defaults dla instance variables.
    _state = _PENDING
    _result = Nic
    _exception = Nic
    _loop = Nic
    _source_traceback = Nic

    _blocking = Nieprawda  # proper use of future (uzyskaj vs uzyskaj from)

    _log_traceback = Nieprawda   # Used dla Python 3.4 oraz later
    _tb_logger = Nic        # Used dla Python 3.3 only

    def __init__(self, *, loop=Nic):
        """Initialize the future.

        The optional event_loop argument allows to explicitly set the event
        loop object used by the future. If it's nie provided, the future uses
        the default event loop.
        """
        jeżeli loop jest Nic:
            self._loop = events.get_event_loop()
        inaczej:
            self._loop = loop
        self._callbacks = []
        jeżeli self._loop.get_debug():
            self._source_traceback = traceback.extract_stack(sys._getframe(1))

    def _format_callbacks(self):
        cb = self._callbacks
        size = len(cb)
        jeżeli nie size:
            cb = ''

        def format_cb(callback):
            zwróć events._format_callback_source(callback, ())

        jeżeli size == 1:
            cb = format_cb(cb[0])
        albo_inaczej size == 2:
            cb = '{}, {}'.format(format_cb(cb[0]), format_cb(cb[1]))
        albo_inaczej size > 2:
            cb = '{}, <{} more>, {}'.format(format_cb(cb[0]),
                                            size-2,
                                            format_cb(cb[-1]))
        zwróć 'cb=[%s]' % cb

    def _repr_info(self):
        info = [self._state.lower()]
        jeżeli self._state == _FINISHED:
            jeżeli self._exception jest nie Nic:
                info.append('exception={!r}'.format(self._exception))
            inaczej:
                # use reprlib to limit the length of the output, especially
                # dla very long strings
                result = reprlib.repr(self._result)
                info.append('result={}'.format(result))
        jeżeli self._callbacks:
            info.append(self._format_callbacks())
        jeżeli self._source_traceback:
            frame = self._source_traceback[-1]
            info.append('created at %s:%s' % (frame[0], frame[1]))
        zwróć info

    def __repr__(self):
        info = self._repr_info()
        zwróć '<%s %s>' % (self.__class__.__name__, ' '.join(info))

    # On Python 3.3 oraz older, objects przy a destructor part of a reference
    # cycle are never destroyed. It's nie more the case on Python 3.4 thanks
    # to the PEP 442.
    jeżeli compat.PY34:
        def __del__(self):
            jeżeli nie self._log_traceback:
                # set_exception() was nie called, albo result() albo exception()
                # has consumed the exception
                zwróć
            exc = self._exception
            context = {
                'message': ('%s exception was never retrieved'
                            % self.__class__.__name__),
                'exception': exc,
                'future': self,
            }
            jeżeli self._source_traceback:
                context['source_traceback'] = self._source_traceback
            self._loop.call_exception_handler(context)

    def cancel(self):
        """Cancel the future oraz schedule callbacks.

        If the future jest already done albo cancelled, zwróć Nieprawda.  Otherwise,
        change the future's state to cancelled, schedule the callbacks oraz
        zwróć Prawda.
        """
        jeżeli self._state != _PENDING:
            zwróć Nieprawda
        self._state = _CANCELLED
        self._schedule_callbacks()
        zwróć Prawda

    def _schedule_callbacks(self):
        """Internal: Ask the event loop to call all callbacks.

        The callbacks are scheduled to be called jako soon jako possible. Also
        clears the callback list.
        """
        callbacks = self._callbacks[:]
        jeżeli nie callbacks:
            zwróć

        self._callbacks[:] = []
        dla callback w callbacks:
            self._loop.call_soon(callback, self)

    def cancelled(self):
        """Return Prawda jeżeli the future was cancelled."""
        zwróć self._state == _CANCELLED

    # Don't implement running(); see http://bugs.python.org/issue18699

    def done(self):
        """Return Prawda jeżeli the future jest done.

        Done means either that a result / exception are available, albo that the
        future was cancelled.
        """
        zwróć self._state != _PENDING

    def result(self):
        """Return the result this future represents.

        If the future has been cancelled, podnieśs CancelledError.  If the
        future's result isn't yet available, podnieśs InvalidStateError.  If
        the future jest done oraz has an exception set, this exception jest podnieśd.
        """
        jeżeli self._state == _CANCELLED:
            podnieś CancelledError
        jeżeli self._state != _FINISHED:
            podnieś InvalidStateError('Result jest nie ready.')
        self._log_traceback = Nieprawda
        jeżeli self._tb_logger jest nie Nic:
            self._tb_logger.clear()
            self._tb_logger = Nic
        jeżeli self._exception jest nie Nic:
            podnieś self._exception
        zwróć self._result

    def exception(self):
        """Return the exception that was set on this future.

        The exception (or Nic jeżeli no exception was set) jest returned only if
        the future jest done.  If the future has been cancelled, podnieśs
        CancelledError.  If the future isn't done yet, podnieśs
        InvalidStateError.
        """
        jeżeli self._state == _CANCELLED:
            podnieś CancelledError
        jeżeli self._state != _FINISHED:
            podnieś InvalidStateError('Exception jest nie set.')
        self._log_traceback = Nieprawda
        jeżeli self._tb_logger jest nie Nic:
            self._tb_logger.clear()
            self._tb_logger = Nic
        zwróć self._exception

    def add_done_callback(self, fn):
        """Add a callback to be run when the future becomes done.

        The callback jest called przy a single argument - the future object. If
        the future jest already done when this jest called, the callback jest
        scheduled przy call_soon.
        """
        jeżeli self._state != _PENDING:
            self._loop.call_soon(fn, self)
        inaczej:
            self._callbacks.append(fn)

    # New method nie w PEP 3148.

    def remove_done_callback(self, fn):
        """Remove all instances of a callback z the "call when done" list.

        Returns the number of callbacks removed.
        """
        filtered_callbacks = [f dla f w self._callbacks jeżeli f != fn]
        removed_count = len(self._callbacks) - len(filtered_callbacks)
        jeżeli removed_count:
            self._callbacks[:] = filtered_callbacks
        zwróć removed_count

    # So-called internal methods (niee: no set_running_or_notify_cancel()).

    def _set_result_unless_cancelled(self, result):
        """Helper setting the result only jeżeli the future was nie cancelled."""
        jeżeli self.cancelled():
            zwróć
        self.set_result(result)

    def set_result(self, result):
        """Mark the future done oraz set its result.

        If the future jest already done when this method jest called, podnieśs
        InvalidStateError.
        """
        jeżeli self._state != _PENDING:
            podnieś InvalidStateError('{}: {!r}'.format(self._state, self))
        self._result = result
        self._state = _FINISHED
        self._schedule_callbacks()

    def set_exception(self, exception):
        """Mark the future done oraz set an exception.

        If the future jest already done when this method jest called, podnieśs
        InvalidStateError.
        """
        jeżeli self._state != _PENDING:
            podnieś InvalidStateError('{}: {!r}'.format(self._state, self))
        jeżeli isinstance(exception, type):
            exception = exception()
        self._exception = exception
        self._state = _FINISHED
        self._schedule_callbacks()
        jeżeli compat.PY34:
            self._log_traceback = Prawda
        inaczej:
            self._tb_logger = _TracebackLogger(self, exception)
            # Arrange dla the logger to be activated after all callbacks
            # have had a chance to call result() albo exception().
            self._loop.call_soon(self._tb_logger.activate)

    # Truly internal methods.

    def _copy_state(self, other):
        """Internal helper to copy state z another Future.

        The other Future may be a concurrent.futures.Future.
        """
        assert other.done()
        jeżeli self.cancelled():
            zwróć
        assert nie self.done()
        jeżeli other.cancelled():
            self.cancel()
        inaczej:
            exception = other.exception()
            jeżeli exception jest nie Nic:
                self.set_exception(exception)
            inaczej:
                result = other.result()
                self.set_result(result)

    def __iter__(self):
        jeżeli nie self.done():
            self._blocking = Prawda
            uzyskaj self  # This tells Task to wait dla completion.
        assert self.done(), "uzyskaj z wasn't used przy future"
        zwróć self.result()  # May podnieś too.

    jeżeli compat.PY35:
        __await__ = __iter__ # make compatible przy 'await' expression


def wrap_future(fut, *, loop=Nic):
    """Wrap concurrent.futures.Future object."""
    jeżeli isinstance(fut, Future):
        zwróć fut
    assert isinstance(fut, concurrent.futures.Future), \
        'concurrent.futures.Future jest expected, got {!r}'.format(fut)
    jeżeli loop jest Nic:
        loop = events.get_event_loop()
    new_future = Future(loop=loop)

    def _check_cancel_other(f):
        jeżeli f.cancelled():
            fut.cancel()

    new_future.add_done_callback(_check_cancel_other)
    fut.add_done_callback(
        lambda future: loop.call_soon_threadsafe(
            new_future._copy_state, future))
    zwróć new_future
