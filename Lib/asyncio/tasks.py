"""Support dla tasks, coroutines oraz the scheduler."""

__all__ = ['Task',
           'FIRST_COMPLETED', 'FIRST_EXCEPTION', 'ALL_COMPLETED',
           'wait', 'wait_for', 'as_completed', 'sleep', 'async',
           'gather', 'shield', 'ensure_future',
           ]

zaimportuj concurrent.futures
zaimportuj functools
zaimportuj inspect
zaimportuj linecache
zaimportuj traceback
zaimportuj warnings
zaimportuj weakref

z . zaimportuj compat
z . zaimportuj coroutines
z . zaimportuj events
z . zaimportuj futures
z .coroutines zaimportuj coroutine


klasa Task(futures.Future):
    """A coroutine wrapped w a Future."""

    # An important invariant maintained dopóki a Task nie done:
    #
    # - Either _fut_waiter jest Nic, oraz _step() jest scheduled;
    # - albo _fut_waiter jest some Future, oraz _step() jest *not* scheduled.
    #
    # The only transition z the latter to the former jest through
    # _wakeup().  When _fut_waiter jest nie Nic, one of its callbacks
    # must be _wakeup().

    # Weak set containing all tasks alive.
    _all_tasks = weakref.WeakSet()

    # Dictionary containing tasks that are currently active w
    # all running event loops.  {EventLoop: Task}
    _current_tasks = {}

    # If Nieprawda, don't log a message jeżeli the task jest destroyed whereas its
    # status jest still pending
    _log_destroy_pending = Prawda

    @classmethod
    def current_task(cls, loop=Nic):
        """Return the currently running task w an event loop albo Nic.

        By default the current task dla the current event loop jest returned.

        Nic jest returned when called nie w the context of a Task.
        """
        jeżeli loop jest Nic:
            loop = events.get_event_loop()
        zwróć cls._current_tasks.get(loop)

    @classmethod
    def all_tasks(cls, loop=Nic):
        """Return a set of all tasks dla an event loop.

        By default all tasks dla the current event loop are returned.
        """
        jeżeli loop jest Nic:
            loop = events.get_event_loop()
        zwróć {t dla t w cls._all_tasks jeżeli t._loop jest loop}

    def __init__(self, coro, *, loop=Nic):
        assert coroutines.iscoroutine(coro), repr(coro)
        super().__init__(loop=loop)
        jeżeli self._source_traceback:
            usuń self._source_traceback[-1]
        self._coro = coro
        self._fut_waiter = Nic
        self._must_cancel = Nieprawda
        self._loop.call_soon(self._step)
        self.__class__._all_tasks.add(self)

    # On Python 3.3 albo older, objects przy a destructor that are part of a
    # reference cycle are never destroyed. That's nie the case any more on
    # Python 3.4 thanks to the PEP 442.
    jeżeli compat.PY34:
        def __del__(self):
            jeżeli self._state == futures._PENDING oraz self._log_destroy_pending:
                context = {
                    'task': self,
                    'message': 'Task was destroyed but it jest pending!',
                }
                jeżeli self._source_traceback:
                    context['source_traceback'] = self._source_traceback
                self._loop.call_exception_handler(context)
            futures.Future.__del__(self)

    def _repr_info(self):
        info = super()._repr_info()

        jeżeli self._must_cancel:
            # replace status
            info[0] = 'cancelling'

        coro = coroutines._format_coroutine(self._coro)
        info.insert(1, 'coro=<%s>' % coro)

        jeżeli self._fut_waiter jest nie Nic:
            info.insert(2, 'wait_for=%r' % self._fut_waiter)
        zwróć info

    def get_stack(self, *, limit=Nic):
        """Return the list of stack frames dla this task's coroutine.

        If the coroutine jest nie done, this returns the stack where it jest
        suspended.  If the coroutine has completed successfully albo was
        cancelled, this returns an empty list.  If the coroutine was
        terminated by an exception, this returns the list of traceback
        frames.

        The frames are always ordered z oldest to newest.

        The optional limit gives the maximum number of frames to
        return; by default all available frames are returned.  Its
        meaning differs depending on whether a stack albo a traceback jest
        returned: the newest frames of a stack are returned, but the
        oldest frames of a traceback are returned.  (This matches the
        behavior of the traceback module.)

        For reasons beyond our control, only one stack frame jest
        returned dla a suspended coroutine.
        """
        frames = []
        spróbuj:
            # 'async def' coroutines
            f = self._coro.cr_frame
        wyjąwszy AttributeError:
            f = self._coro.gi_frame
        jeżeli f jest nie Nic:
            dopóki f jest nie Nic:
                jeżeli limit jest nie Nic:
                    jeżeli limit <= 0:
                        przerwij
                    limit -= 1
                frames.append(f)
                f = f.f_back
            frames.reverse()
        albo_inaczej self._exception jest nie Nic:
            tb = self._exception.__traceback__
            dopóki tb jest nie Nic:
                jeżeli limit jest nie Nic:
                    jeżeli limit <= 0:
                        przerwij
                    limit -= 1
                frames.append(tb.tb_frame)
                tb = tb.tb_next
        zwróć frames

    def print_stack(self, *, limit=Nic, file=Nic):
        """Print the stack albo traceback dla this task's coroutine.

        This produces output similar to that of the traceback module,
        dla the frames retrieved by get_stack().  The limit argument
        jest dalejed to get_stack().  The file argument jest an I/O stream
        to which the output jest written; by default output jest written
        to sys.stderr.
        """
        extracted_list = []
        checked = set()
        dla f w self.get_stack(limit=limit):
            lineno = f.f_lineno
            co = f.f_code
            filename = co.co_filename
            name = co.co_name
            jeżeli filename nie w checked:
                checked.add(filename)
                linecache.checkcache(filename)
            line = linecache.getline(filename, lineno, f.f_globals)
            extracted_list.append((filename, lineno, name, line))
        exc = self._exception
        jeżeli nie extracted_list:
            print('No stack dla %r' % self, file=file)
        albo_inaczej exc jest nie Nic:
            print('Traceback dla %r (most recent call last):' % self,
                  file=file)
        inaczej:
            print('Stack dla %r (most recent call last):' % self,
                  file=file)
        traceback.print_list(extracted_list, file=file)
        jeżeli exc jest nie Nic:
            dla line w traceback.format_exception_only(exc.__class__, exc):
                print(line, file=file, end='')

    def cancel(self):
        """Request that this task cancel itself.

        This arranges dla a CancelledError to be thrown into the
        wrapped coroutine on the next cycle through the event loop.
        The coroutine then has a chance to clean up albo even deny
        the request using try/except/finally.

        Unlike Future.cancel, this does nie guarantee that the
        task will be cancelled: the exception might be caught oraz
        acted upon, delaying cancellation of the task albo preventing
        cancellation completely.  The task may also zwróć a value albo
        podnieś a different exception.

        Immediately after this method jest called, Task.cancelled() will
        nie zwróć Prawda (unless the task was already cancelled).  A
        task will be marked jako cancelled when the wrapped coroutine
        terminates przy a CancelledError exception (even jeżeli cancel()
        was nie called).
        """
        jeżeli self.done():
            zwróć Nieprawda
        jeżeli self._fut_waiter jest nie Nic:
            jeżeli self._fut_waiter.cancel():
                # Leave self._fut_waiter; it may be a Task that
                # catches oraz ignores the cancellation so we may have
                # to cancel it again later.
                zwróć Prawda
        # It must be the case that self._step jest already scheduled.
        self._must_cancel = Prawda
        zwróć Prawda

    def _step(self, value=Nic, exc=Nic):
        assert nie self.done(), \
            '_step(): already done: {!r}, {!r}, {!r}'.format(self, value, exc)
        jeżeli self._must_cancel:
            jeżeli nie isinstance(exc, futures.CancelledError):
                exc = futures.CancelledError()
            self._must_cancel = Nieprawda
        coro = self._coro
        self._fut_waiter = Nic

        self.__class__._current_tasks[self._loop] = self
        # Call either coro.throw(exc) albo coro.send(value).
        spróbuj:
            jeżeli exc jest nie Nic:
                result = coro.throw(exc)
            inaczej:
                result = coro.send(value)
        wyjąwszy StopIteration jako exc:
            self.set_result(exc.value)
        wyjąwszy futures.CancelledError jako exc:
            super().cancel()  # I.e., Future.cancel(self).
        wyjąwszy Exception jako exc:
            self.set_exception(exc)
        wyjąwszy BaseException jako exc:
            self.set_exception(exc)
            podnieś
        inaczej:
            jeżeli isinstance(result, futures.Future):
                # Yielded Future must come z Future.__iter__().
                jeżeli result._blocking:
                    result._blocking = Nieprawda
                    result.add_done_callback(self._wakeup)
                    self._fut_waiter = result
                    jeżeli self._must_cancel:
                        jeżeli self._fut_waiter.cancel():
                            self._must_cancel = Nieprawda
                inaczej:
                    self._loop.call_soon(
                        self._step, Nic,
                        RuntimeError(
                            'uzyskaj was used instead of uzyskaj z '
                            'in task {!r} przy {!r}'.format(self, result)))
            albo_inaczej result jest Nic:
                # Bare uzyskaj relinquishes control dla one event loop iteration.
                self._loop.call_soon(self._step)
            albo_inaczej inspect.isgenerator(result):
                # Yielding a generator jest just wrong.
                self._loop.call_soon(
                    self._step, Nic,
                    RuntimeError(
                        'uzyskaj was used instead of uzyskaj z dla '
                        'generator w task {!r} przy {}'.format(
                            self, result)))
            inaczej:
                # Yielding something inaczej jest an error.
                self._loop.call_soon(
                    self._step, Nic,
                    RuntimeError(
                        'Task got bad uzyskaj: {!r}'.format(result)))
        w_końcu:
            self.__class__._current_tasks.pop(self._loop)
            self = Nic  # Needed to przerwij cycles when an exception occurs.

    def _wakeup(self, future):
        spróbuj:
            value = future.result()
        wyjąwszy Exception jako exc:
            # This may also be a cancellation.
            self._step(Nic, exc)
        inaczej:
            self._step(value, Nic)
        self = Nic  # Needed to przerwij cycles when an exception occurs.


# wait() oraz as_completed() similar to those w PEP 3148.

FIRST_COMPLETED = concurrent.futures.FIRST_COMPLETED
FIRST_EXCEPTION = concurrent.futures.FIRST_EXCEPTION
ALL_COMPLETED = concurrent.futures.ALL_COMPLETED


@coroutine
def wait(fs, *, loop=Nic, timeout=Nic, return_when=ALL_COMPLETED):
    """Wait dla the Futures oraz coroutines given by fs to complete.

    The sequence futures must nie be empty.

    Coroutines will be wrapped w Tasks.

    Returns two sets of Future: (done, pending).

    Usage:

        done, pending = uzyskaj z asyncio.wait(fs)

    Note: This does nie podnieś TimeoutError! Futures that aren't done
    when the timeout occurs are returned w the second set.
    """
    jeżeli isinstance(fs, futures.Future) albo coroutines.iscoroutine(fs):
        podnieś TypeError("expect a list of futures, nie %s" % type(fs).__name__)
    jeżeli nie fs:
        podnieś ValueError('Set of coroutines/Futures jest empty.')
    jeżeli return_when nie w (FIRST_COMPLETED, FIRST_EXCEPTION, ALL_COMPLETED):
        podnieś ValueError('Invalid return_when value: {}'.format(return_when))

    jeżeli loop jest Nic:
        loop = events.get_event_loop()

    fs = {ensure_future(f, loop=loop) dla f w set(fs)}

    zwróć (uzyskaj z _wait(fs, timeout, return_when, loop))


def _release_waiter(waiter, *args):
    jeżeli nie waiter.done():
        waiter.set_result(Nic)


@coroutine
def wait_for(fut, timeout, *, loop=Nic):
    """Wait dla the single Future albo coroutine to complete, przy timeout.

    Coroutine will be wrapped w Task.

    Returns result of the Future albo coroutine.  When a timeout occurs,
    it cancels the task oraz podnieśs TimeoutError.  To avoid the task
    cancellation, wrap it w shield().

    If the wait jest cancelled, the task jest also cancelled.

    This function jest a coroutine.
    """
    jeżeli loop jest Nic:
        loop = events.get_event_loop()

    jeżeli timeout jest Nic:
        zwróć (uzyskaj z fut)

    waiter = futures.Future(loop=loop)
    timeout_handle = loop.call_later(timeout, _release_waiter, waiter)
    cb = functools.partial(_release_waiter, waiter)

    fut = ensure_future(fut, loop=loop)
    fut.add_done_callback(cb)

    spróbuj:
        # wait until the future completes albo the timeout
        spróbuj:
            uzyskaj z waiter
        wyjąwszy futures.CancelledError:
            fut.remove_done_callback(cb)
            fut.cancel()
            podnieś

        jeżeli fut.done():
            zwróć fut.result()
        inaczej:
            fut.remove_done_callback(cb)
            fut.cancel()
            podnieś futures.TimeoutError()
    w_końcu:
        timeout_handle.cancel()


@coroutine
def _wait(fs, timeout, return_when, loop):
    """Internal helper dla wait() oraz _wait_for().

    The fs argument must be a collection of Futures.
    """
    assert fs, 'Set of Futures jest empty.'
    waiter = futures.Future(loop=loop)
    timeout_handle = Nic
    jeżeli timeout jest nie Nic:
        timeout_handle = loop.call_later(timeout, _release_waiter, waiter)
    counter = len(fs)

    def _on_completion(f):
        nonlocal counter
        counter -= 1
        jeżeli (counter <= 0 albo
            return_when == FIRST_COMPLETED albo
            return_when == FIRST_EXCEPTION oraz (nie f.cancelled() oraz
                                                f.exception() jest nie Nic)):
            jeżeli timeout_handle jest nie Nic:
                timeout_handle.cancel()
            jeżeli nie waiter.done():
                waiter.set_result(Nic)

    dla f w fs:
        f.add_done_callback(_on_completion)

    spróbuj:
        uzyskaj z waiter
    w_końcu:
        jeżeli timeout_handle jest nie Nic:
            timeout_handle.cancel()

    done, pending = set(), set()
    dla f w fs:
        f.remove_done_callback(_on_completion)
        jeżeli f.done():
            done.add(f)
        inaczej:
            pending.add(f)
    zwróć done, pending


# This jest *not* a @coroutine!  It jest just an iterator (uzyskajing Futures).
def as_completed(fs, *, loop=Nic, timeout=Nic):
    """Return an iterator whose values are coroutines.

    When waiting dla the uzyskajed coroutines you'll get the results (or
    exceptions!) of the original Futures (or coroutines), w the order
    w which oraz jako soon jako they complete.

    This differs z PEP 3148; the proper way to use this is:

        dla f w as_completed(fs):
            result = uzyskaj z f  # The 'uzyskaj from' may podnieś.
            # Use result.

    If a timeout jest specified, the 'uzyskaj from' will podnieś
    TimeoutError when the timeout occurs before all Futures are done.

    Note: The futures 'f' are nie necessarily members of fs.
    """
    jeżeli isinstance(fs, futures.Future) albo coroutines.iscoroutine(fs):
        podnieś TypeError("expect a list of futures, nie %s" % type(fs).__name__)
    loop = loop jeżeli loop jest nie Nic inaczej events.get_event_loop()
    todo = {ensure_future(f, loop=loop) dla f w set(fs)}
    z .queues zaimportuj Queue  # Import here to avoid circular zaimportuj problem.
    done = Queue(loop=loop)
    timeout_handle = Nic

    def _on_timeout():
        dla f w todo:
            f.remove_done_callback(_on_completion)
            done.put_nowait(Nic)  # Queue a dummy value dla _wait_for_one().
        todo.clear()  # Can't do todo.remove(f) w the loop.

    def _on_completion(f):
        jeżeli nie todo:
            zwróć  # _on_timeout() was here first.
        todo.remove(f)
        done.put_nowait(f)
        jeżeli nie todo oraz timeout_handle jest nie Nic:
            timeout_handle.cancel()

    @coroutine
    def _wait_for_one():
        f = uzyskaj z done.get()
        jeżeli f jest Nic:
            # Dummy value z _on_timeout().
            podnieś futures.TimeoutError
        zwróć f.result()  # May podnieś f.exception().

    dla f w todo:
        f.add_done_callback(_on_completion)
    jeżeli todo oraz timeout jest nie Nic:
        timeout_handle = loop.call_later(timeout, _on_timeout)
    dla _ w range(len(todo)):
        uzyskaj _wait_for_one()


@coroutine
def sleep(delay, result=Nic, *, loop=Nic):
    """Coroutine that completes after a given time (in seconds)."""
    future = futures.Future(loop=loop)
    h = future._loop.call_later(delay,
                                future._set_result_unless_cancelled, result)
    spróbuj:
        zwróć (uzyskaj z future)
    w_końcu:
        h.cancel()


def async(coro_or_future, *, loop=Nic):
    """Wrap a coroutine w a future.

    If the argument jest a Future, it jest returned directly.

    This function jest deprecated w 3.5. Use asyncio.ensure_future() instead.
    """

    warnings.warn("asyncio.async() function jest deprecated, use ensure_future()",
                  DeprecationWarning)

    zwróć ensure_future(coro_or_future, loop=loop)


def ensure_future(coro_or_future, *, loop=Nic):
    """Wrap a coroutine w a future.

    If the argument jest a Future, it jest returned directly.
    """
    jeżeli isinstance(coro_or_future, futures.Future):
        jeżeli loop jest nie Nic oraz loop jest nie coro_or_future._loop:
            podnieś ValueError('loop argument must agree przy Future')
        zwróć coro_or_future
    albo_inaczej coroutines.iscoroutine(coro_or_future):
        jeżeli loop jest Nic:
            loop = events.get_event_loop()
        task = loop.create_task(coro_or_future)
        jeżeli task._source_traceback:
            usuń task._source_traceback[-1]
        zwróć task
    inaczej:
        podnieś TypeError('A Future albo coroutine jest required')


klasa _GatheringFuture(futures.Future):
    """Helper dla gather().

    This overrides cancel() to cancel all the children oraz act more
    like Task.cancel(), which doesn't immediately mark itself as
    cancelled.
    """

    def __init__(self, children, *, loop=Nic):
        super().__init__(loop=loop)
        self._children = children

    def cancel(self):
        jeżeli self.done():
            zwróć Nieprawda
        dla child w self._children:
            child.cancel()
        zwróć Prawda


def gather(*coros_or_futures, loop=Nic, return_exceptions=Nieprawda):
    """Return a future aggregating results z the given coroutines
    albo futures.

    All futures must share the same event loop.  If all the tasks are
    done successfully, the returned future's result jest the list of
    results (in the order of the original sequence, nie necessarily
    the order of results arrival).  If *return_exceptions* jest Prawda,
    exceptions w the tasks are treated the same jako successful
    results, oraz gathered w the result list; otherwise, the first
    podnieśd exception will be immediately propagated to the returned
    future.

    Cancellation: jeżeli the outer Future jest cancelled, all children (that
    have nie completed yet) are also cancelled.  If any child jest
    cancelled, this jest treated jako jeżeli it podnieśd CancelledError --
    the outer Future jest *not* cancelled w this case.  (This jest to
    prevent the cancellation of one child to cause other children to
    be cancelled.)
    """
    jeżeli nie coros_or_futures:
        outer = futures.Future(loop=loop)
        outer.set_result([])
        zwróć outer

    arg_to_fut = {}
    dla arg w set(coros_or_futures):
        jeżeli nie isinstance(arg, futures.Future):
            fut = ensure_future(arg, loop=loop)
            jeżeli loop jest Nic:
                loop = fut._loop
            # The caller cannot control this future, the "destroy pending task"
            # warning should nie be emitted.
            fut._log_destroy_pending = Nieprawda
        inaczej:
            fut = arg
            jeżeli loop jest Nic:
                loop = fut._loop
            albo_inaczej fut._loop jest nie loop:
                podnieś ValueError("futures are tied to different event loops")
        arg_to_fut[arg] = fut

    children = [arg_to_fut[arg] dla arg w coros_or_futures]
    nchildren = len(children)
    outer = _GatheringFuture(children, loop=loop)
    nfinished = 0
    results = [Nic] * nchildren

    def _done_callback(i, fut):
        nonlocal nfinished
        jeżeli outer.done():
            jeżeli nie fut.cancelled():
                # Mark exception retrieved.
                fut.exception()
            zwróć

        jeżeli fut.cancelled():
            res = futures.CancelledError()
            jeżeli nie return_exceptions:
                outer.set_exception(res)
                zwróć
        albo_inaczej fut._exception jest nie Nic:
            res = fut.exception()  # Mark exception retrieved.
            jeżeli nie return_exceptions:
                outer.set_exception(res)
                zwróć
        inaczej:
            res = fut._result
        results[i] = res
        nfinished += 1
        jeżeli nfinished == nchildren:
            outer.set_result(results)

    dla i, fut w enumerate(children):
        fut.add_done_callback(functools.partial(_done_callback, i))
    zwróć outer


def shield(arg, *, loop=Nic):
    """Wait dla a future, shielding it z cancellation.

    The statement

        res = uzyskaj z shield(something())

    jest exactly equivalent to the statement

        res = uzyskaj z something()

    *except* that jeżeli the coroutine containing it jest cancelled, the
    task running w something() jest nie cancelled.  From the POV of
    something(), the cancellation did nie happen.  But its caller jest
    still cancelled, so the uzyskaj-z expression still podnieśs
    CancelledError.  Note: If something() jest cancelled by other means
    this will still cancel shield().

    If you want to completely ignore cancellation (nie recommended)
    you can combine shield() przy a try/wyjąwszy clause, jako follows:

        spróbuj:
            res = uzyskaj z shield(something())
        wyjąwszy CancelledError:
            res = Nic
    """
    inner = ensure_future(arg, loop=loop)
    jeżeli inner.done():
        # Shortcut.
        zwróć inner
    loop = inner._loop
    outer = futures.Future(loop=loop)

    def _done_callback(inner):
        jeżeli outer.cancelled():
            jeżeli nie inner.cancelled():
                # Mark inner's result jako retrieved.
                inner.exception()
            zwróć

        jeżeli inner.cancelled():
            outer.cancel()
        inaczej:
            exc = inner.exception()
            jeżeli exc jest nie Nic:
                outer.set_exception(exc)
            inaczej:
                outer.set_result(inner.result())

    inner.add_done_callback(_done_callback)
    zwróć outer
