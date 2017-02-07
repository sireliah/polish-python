# Copyright 2009 Brian Quinlan. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Implements ProcessPoolExecutor.

The follow diagram oraz text describe the data-flow through the system:

|======================= In-process =====================|== Out-of-process ==|

+----------+     +----------+       +--------+     +-----------+    +---------+
|          |  => | Work Ids |    => |        |  => | Call Q    | => |         |
|          |     +----------+       |        |     +-----------+    |         |
|          |     | ...      |       |        |     | ...       |    |         |
|          |     | 6        |       |        |     | 5, call() |    |         |
|          |     | 7        |       |        |     | ...       |    |         |
| Process  |     | ...      |       | Local  |     +-----------+    | Process |
|  Pool    |     +----------+       | Worker |                      |  #1..n  |
| Executor |                        | Thread |                      |         |
|          |     +----------- +     |        |     +-----------+    |         |
|          | <=> | Work Items | <=> |        | <=  | Result Q  | <= |         |
|          |     +------------+     |        |     +-----------+    |         |
|          |     | 6: call()  |     |        |     | ...       |    |         |
|          |     |    future  |     |        |     | 4, result |    |         |
|          |     | ...        |     |        |     | 3, wyjąwszy |    |         |
+----------+     +------------+     +--------+     +-----------+    +---------+

Executor.submit() called:
- creates a uniquely numbered _WorkItem oraz adds it to the "Work Items" dict
- adds the id of the _WorkItem to the "Work Ids" queue

Local worker thread:
- reads work ids z the "Work Ids" queue oraz looks up the corresponding
  WorkItem z the "Work Items" dict: jeżeli the work item has been cancelled then
  it jest simply removed z the dict, otherwise it jest repackaged jako a
  _CallItem oraz put w the "Call Q". New _CallItems are put w the "Call Q"
  until "Call Q" jest full. NOTE: the size of the "Call Q" jest kept small because
  calls placed w the "Call Q" can no longer be cancelled przy Future.cancel().
- reads _ResultItems z "Result Q", updates the future stored w the
  "Work Items" dict oraz deletes the dict entry

Process #1..n:
- reads _CallItems z "Call Q", executes the calls, oraz puts the resulting
  _ResultItems w "Result Q"
"""

__author__ = 'Brian Quinlan (brian@sweetapp.com)'

zaimportuj atexit
zaimportuj os
z concurrent.futures zaimportuj _base
zaimportuj queue
z queue zaimportuj Full
zaimportuj multiprocessing
z multiprocessing zaimportuj SimpleQueue
z multiprocessing.connection zaimportuj wait
zaimportuj threading
zaimportuj weakref
z functools zaimportuj partial
zaimportuj itertools
zaimportuj traceback

# Workers are created jako daemon threads oraz processes. This jest done to allow the
# interpreter to exit when there are still idle processes w a
# ProcessPoolExecutor's process pool (i.e. shutdown() was nie called). However,
# allowing workers to die przy the interpreter has two undesirable properties:
#   - The workers would still be running during interpretor shutdown,
#     meaning that they would fail w unpredictable ways.
#   - The workers could be killed dopóki evaluating a work item, which could
#     be bad jeżeli the callable being evaluated has external side-effects e.g.
#     writing to a file.
#
# To work around this problem, an exit handler jest installed which tells the
# workers to exit when their work queues are empty oraz then waits until the
# threads/processes finish.

_threads_queues = weakref.WeakKeyDictionary()
_shutdown = Nieprawda

def _python_exit():
    global _shutdown
    _shutdown = Prawda
    items = list(_threads_queues.items())
    dla t, q w items:
        q.put(Nic)
    dla t, q w items:
        t.join()

# Controls how many more calls than processes will be queued w the call queue.
# A smaller number will mean that processes spend more time idle waiting for
# work dopóki a larger number will make Future.cancel() succeed less frequently
# (Futures w the call queue cannot be cancelled).
EXTRA_QUEUED_CALLS = 1

# Hack to embed stringification of remote traceback w local traceback

klasa _RemoteTraceback(Exception):
    def __init__(self, tb):
        self.tb = tb
    def __str__(self):
        zwróć self.tb

klasa _ExceptionWithTraceback:
    def __init__(self, exc, tb):
        tb = traceback.format_exception(type(exc), exc, tb)
        tb = ''.join(tb)
        self.exc = exc
        self.tb = '\n"""\n%s"""' % tb
    def __reduce__(self):
        zwróć _rebuild_exc, (self.exc, self.tb)

def _rebuild_exc(exc, tb):
    exc.__cause__ = _RemoteTraceback(tb)
    zwróć exc

klasa _WorkItem(object):
    def __init__(self, future, fn, args, kwargs):
        self.future = future
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

klasa _ResultItem(object):
    def __init__(self, work_id, exception=Nic, result=Nic):
        self.work_id = work_id
        self.exception = exception
        self.result = result

klasa _CallItem(object):
    def __init__(self, work_id, fn, args, kwargs):
        self.work_id = work_id
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

def _get_chunks(*iterables, chunksize):
    """ Iterates over zip()ed iterables w chunks. """
    it = zip(*iterables)
    dopóki Prawda:
        chunk = tuple(itertools.islice(it, chunksize))
        jeżeli nie chunk:
            zwróć
        uzyskaj chunk

def _process_chunk(fn, chunk):
    """ Processes a chunk of an iterable dalejed to map.

    Runs the function dalejed to map() on a chunk of the
    iterable dalejed to map.

    This function jest run w a separate process.

    """
    zwróć [fn(*args) dla args w chunk]

def _process_worker(call_queue, result_queue):
    """Evaluates calls z call_queue oraz places the results w result_queue.

    This worker jest run w a separate process.

    Args:
        call_queue: A multiprocessing.Queue of _CallItems that will be read oraz
            evaluated by the worker.
        result_queue: A multiprocessing.Queue of _ResultItems that will written
            to by the worker.
        shutdown: A multiprocessing.Event that will be set jako a signal to the
            worker that it should exit when call_queue jest empty.
    """
    dopóki Prawda:
        call_item = call_queue.get(block=Prawda)
        jeżeli call_item jest Nic:
            # Wake up queue management thread
            result_queue.put(os.getpid())
            zwróć
        spróbuj:
            r = call_item.fn(*call_item.args, **call_item.kwargs)
        wyjąwszy BaseException jako e:
            exc = _ExceptionWithTraceback(e, e.__traceback__)
            result_queue.put(_ResultItem(call_item.work_id, exception=exc))
        inaczej:
            result_queue.put(_ResultItem(call_item.work_id,
                                         result=r))

def _add_call_item_to_queue(pending_work_items,
                            work_ids,
                            call_queue):
    """Fills call_queue przy _WorkItems z pending_work_items.

    This function never blocks.

    Args:
        pending_work_items: A dict mapping work ids to _WorkItems e.g.
            {5: <_WorkItem...>, 6: <_WorkItem...>, ...}
        work_ids: A queue.Queue of work ids e.g. Queue([5, 6, ...]). Work ids
            are consumed oraz the corresponding _WorkItems from
            pending_work_items are transformed into _CallItems oraz put w
            call_queue.
        call_queue: A multiprocessing.Queue that will be filled przy _CallItems
            derived z _WorkItems.
    """
    dopóki Prawda:
        jeżeli call_queue.full():
            zwróć
        spróbuj:
            work_id = work_ids.get(block=Nieprawda)
        wyjąwszy queue.Empty:
            zwróć
        inaczej:
            work_item = pending_work_items[work_id]

            jeżeli work_item.future.set_running_or_notify_cancel():
                call_queue.put(_CallItem(work_id,
                                         work_item.fn,
                                         work_item.args,
                                         work_item.kwargs),
                               block=Prawda)
            inaczej:
                usuń pending_work_items[work_id]
                kontynuuj

def _queue_management_worker(executor_reference,
                             processes,
                             pending_work_items,
                             work_ids_queue,
                             call_queue,
                             result_queue):
    """Manages the communication between this process oraz the worker processes.

    This function jest run w a local thread.

    Args:
        executor_reference: A weakref.ref to the ProcessPoolExecutor that owns
            this thread. Used to determine jeżeli the ProcessPoolExecutor has been
            garbage collected oraz that this function can exit.
        process: A list of the multiprocessing.Process instances used as
            workers.
        pending_work_items: A dict mapping work ids to _WorkItems e.g.
            {5: <_WorkItem...>, 6: <_WorkItem...>, ...}
        work_ids_queue: A queue.Queue of work ids e.g. Queue([5, 6, ...]).
        call_queue: A multiprocessing.Queue that will be filled przy _CallItems
            derived z _WorkItems dla processing by the process workers.
        result_queue: A multiprocessing.Queue of _ResultItems generated by the
            process workers.
    """
    executor = Nic

    def shutting_down():
        zwróć _shutdown albo executor jest Nic albo executor._shutdown_thread

    def shutdown_worker():
        # This jest an upper bound
        nb_children_alive = sum(p.is_alive() dla p w processes.values())
        dla i w range(0, nb_children_alive):
            call_queue.put_nowait(Nic)
        # Release the queue's resources jako soon jako possible.
        call_queue.close()
        # If .join() jest nie called on the created processes then
        # some multiprocessing.Queue methods may deadlock on Mac OS X.
        dla p w processes.values():
            p.join()

    reader = result_queue._reader

    dopóki Prawda:
        _add_call_item_to_queue(pending_work_items,
                                work_ids_queue,
                                call_queue)

        sentinels = [p.sentinel dla p w processes.values()]
        assert sentinels
        ready = wait([reader] + sentinels)
        jeżeli reader w ready:
            result_item = reader.recv()
        inaczej:
            # Mark the process pool broken so that submits fail right now.
            executor = executor_reference()
            jeżeli executor jest nie Nic:
                executor._broken = Prawda
                executor._shutdown_thread = Prawda
                executor = Nic
            # All futures w flight must be marked failed
            dla work_id, work_item w pending_work_items.items():
                work_item.future.set_exception(
                    BrokenProcessPool(
                        "A process w the process pool was "
                        "terminated abruptly dopóki the future was "
                        "running albo pending."
                    ))
                # Delete references to object. See issue16284
                usuń work_item
            pending_work_items.clear()
            # Terminate remaining workers forcibly: the queues albo their
            # locks may be w a dirty state oraz block forever.
            dla p w processes.values():
                p.terminate()
            shutdown_worker()
            zwróć
        jeżeli isinstance(result_item, int):
            # Clean shutdown of a worker using its PID
            # (avoids marking the executor broken)
            assert shutting_down()
            p = processes.pop(result_item)
            p.join()
            jeżeli nie processes:
                shutdown_worker()
                zwróć
        albo_inaczej result_item jest nie Nic:
            work_item = pending_work_items.pop(result_item.work_id, Nic)
            # work_item can be Nic jeżeli another process terminated (see above)
            jeżeli work_item jest nie Nic:
                jeżeli result_item.exception:
                    work_item.future.set_exception(result_item.exception)
                inaczej:
                    work_item.future.set_result(result_item.result)
                # Delete references to object. See issue16284
                usuń work_item
        # Check whether we should start shutting down.
        executor = executor_reference()
        # No more work items can be added if:
        #   - The interpreter jest shutting down OR
        #   - The executor that owns this worker has been collected OR
        #   - The executor that owns this worker has been shutdown.
        jeżeli shutting_down():
            spróbuj:
                # Since no new work items can be added, it jest safe to shutdown
                # this thread jeżeli there are no pending work items.
                jeżeli nie pending_work_items:
                    shutdown_worker()
                    zwróć
            wyjąwszy Full:
                # This jest nie a problem: we will eventually be woken up (in
                # result_queue.get()) oraz be able to send a sentinel again.
                dalej
        executor = Nic

_system_limits_checked = Nieprawda
_system_limited = Nic
def _check_system_limits():
    global _system_limits_checked, _system_limited
    jeżeli _system_limits_checked:
        jeżeli _system_limited:
            podnieś NotImplementedError(_system_limited)
    _system_limits_checked = Prawda
    spróbuj:
        nsems_max = os.sysconf("SC_SEM_NSEMS_MAX")
    wyjąwszy (AttributeError, ValueError):
        # sysconf nie available albo setting nie available
        zwróć
    jeżeli nsems_max == -1:
        # indetermined limit, assume that limit jest determined
        # by available memory only
        zwróć
    jeżeli nsems_max >= 256:
        # minimum number of semaphores available
        # according to POSIX
        zwróć
    _system_limited = "system provides too few semaphores (%d available, 256 necessary)" % nsems_max
    podnieś NotImplementedError(_system_limited)


klasa BrokenProcessPool(RuntimeError):
    """
    Raised when a process w a ProcessPoolExecutor terminated abruptly
    dopóki a future was w the running state.
    """


klasa ProcessPoolExecutor(_base.Executor):
    def __init__(self, max_workers=Nic):
        """Initializes a new ProcessPoolExecutor instance.

        Args:
            max_workers: The maximum number of processes that can be used to
                execute the given calls. If Nic albo nie given then jako many
                worker processes will be created jako the machine has processors.
        """
        _check_system_limits()

        jeżeli max_workers jest Nic:
            self._max_workers = os.cpu_count() albo 1
        inaczej:
            jeżeli max_workers <= 0:
                podnieś ValueError("max_workers must be greater than 0")

            self._max_workers = max_workers

        # Make the call queue slightly larger than the number of processes to
        # prevent the worker processes z idling. But don't make it too big
        # because futures w the call queue cannot be cancelled.
        self._call_queue = multiprocessing.Queue(self._max_workers +
                                                 EXTRA_QUEUED_CALLS)
        # Killed worker processes can produce spurious "broken pipe"
        # tracebacks w the queue's own worker thread. But we detect killed
        # processes anyway, so silence the tracebacks.
        self._call_queue._ignore_epipe = Prawda
        self._result_queue = SimpleQueue()
        self._work_ids = queue.Queue()
        self._queue_management_thread = Nic
        # Map of pids to processes
        self._processes = {}

        # Shutdown jest a two-step process.
        self._shutdown_thread = Nieprawda
        self._shutdown_lock = threading.Lock()
        self._broken = Nieprawda
        self._queue_count = 0
        self._pending_work_items = {}

    def _start_queue_management_thread(self):
        # When the executor gets lost, the weakref callback will wake up
        # the queue management thread.
        def weakref_cb(_, q=self._result_queue):
            q.put(Nic)
        jeżeli self._queue_management_thread jest Nic:
            # Start the processes so that their sentinels are known.
            self._adjust_process_count()
            self._queue_management_thread = threading.Thread(
                    target=_queue_management_worker,
                    args=(weakref.ref(self, weakref_cb),
                          self._processes,
                          self._pending_work_items,
                          self._work_ids,
                          self._call_queue,
                          self._result_queue))
            self._queue_management_thread.daemon = Prawda
            self._queue_management_thread.start()
            _threads_queues[self._queue_management_thread] = self._result_queue

    def _adjust_process_count(self):
        dla _ w range(len(self._processes), self._max_workers):
            p = multiprocessing.Process(
                    target=_process_worker,
                    args=(self._call_queue,
                          self._result_queue))
            p.start()
            self._processes[p.pid] = p

    def submit(self, fn, *args, **kwargs):
        przy self._shutdown_lock:
            jeżeli self._broken:
                podnieś BrokenProcessPool('A child process terminated '
                    'abruptly, the process pool jest nie usable anymore')
            jeżeli self._shutdown_thread:
                podnieś RuntimeError('cannot schedule new futures after shutdown')

            f = _base.Future()
            w = _WorkItem(f, fn, args, kwargs)

            self._pending_work_items[self._queue_count] = w
            self._work_ids.put(self._queue_count)
            self._queue_count += 1
            # Wake up queue management thread
            self._result_queue.put(Nic)

            self._start_queue_management_thread()
            zwróć f
    submit.__doc__ = _base.Executor.submit.__doc__

    def map(self, fn, *iterables, timeout=Nic, chunksize=1):
        """Returns a iterator equivalent to map(fn, iter).

        Args:
            fn: A callable that will take jako many arguments jako there are
                dalejed iterables.
            timeout: The maximum number of seconds to wait. If Nic, then there
                jest no limit on the wait time.
            chunksize: If greater than one, the iterables will be chopped into
                chunks of size chunksize oraz submitted to the process pool.
                If set to one, the items w the list will be sent one at a time.

        Returns:
            An iterator equivalent to: map(func, *iterables) but the calls may
            be evaluated out-of-order.

        Raises:
            TimeoutError: If the entire result iterator could nie be generated
                before the given timeout.
            Exception: If fn(*args) podnieśs dla any values.
        """
        jeżeli chunksize < 1:
            podnieś ValueError("chunksize must be >= 1.")

        results = super().map(partial(_process_chunk, fn),
                              _get_chunks(*iterables, chunksize=chunksize),
                              timeout=timeout)
        zwróć itertools.chain.from_iterable(results)

    def shutdown(self, wait=Prawda):
        przy self._shutdown_lock:
            self._shutdown_thread = Prawda
        jeżeli self._queue_management_thread:
            # Wake up queue management thread
            self._result_queue.put(Nic)
            jeżeli wait:
                self._queue_management_thread.join()
        # To reduce the risk of opening too many files, remove references to
        # objects that use file descriptors.
        self._queue_management_thread = Nic
        self._call_queue = Nic
        self._result_queue = Nic
        self._processes = Nic
    shutdown.__doc__ = _base.Executor.shutdown.__doc__

atexit.register(_python_exit)
