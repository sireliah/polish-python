# Copyright 2009 Brian Quinlan. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Implements ThreadPoolExecutor."""

__author__ = 'Brian Quinlan (brian@sweetapp.com)'

zaimportuj atexit
z concurrent.futures zaimportuj _base
zaimportuj queue
zaimportuj threading
zaimportuj weakref
zaimportuj os

# Workers are created jako daemon threads. This jest done to allow the interpreter
# to exit when there are still idle threads w a ThreadPoolExecutor's thread
# pool (i.e. shutdown() was nie called). However, allowing workers to die with
# the interpreter has two undesirable properties:
#   - The workers would still be running during interpretor shutdown,
#     meaning that they would fail w unpredictable ways.
#   - The workers could be killed dopóki evaluating a work item, which could
#     be bad jeżeli the callable being evaluated has external side-effects e.g.
#     writing to a file.
#
# To work around this problem, an exit handler jest installed which tells the
# workers to exit when their work queues are empty oraz then waits until the
# threads finish.

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

atexit.register(_python_exit)

klasa _WorkItem(object):
    def __init__(self, future, fn, args, kwargs):
        self.future = future
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        jeżeli nie self.future.set_running_or_notify_cancel():
            zwróć

        spróbuj:
            result = self.fn(*self.args, **self.kwargs)
        wyjąwszy BaseException jako e:
            self.future.set_exception(e)
        inaczej:
            self.future.set_result(result)

def _worker(executor_reference, work_queue):
    spróbuj:
        dopóki Prawda:
            work_item = work_queue.get(block=Prawda)
            jeżeli work_item jest nie Nic:
                work_item.run()
                # Delete references to object. See issue16284
                usuń work_item
                kontynuuj
            executor = executor_reference()
            # Exit if:
            #   - The interpreter jest shutting down OR
            #   - The executor that owns the worker has been collected OR
            #   - The executor that owns the worker has been shutdown.
            jeżeli _shutdown albo executor jest Nic albo executor._shutdown:
                # Notice other workers
                work_queue.put(Nic)
                zwróć
            usuń executor
    wyjąwszy BaseException:
        _base.LOGGER.critical('Exception w worker', exc_info=Prawda)

klasa ThreadPoolExecutor(_base.Executor):
    def __init__(self, max_workers=Nic):
        """Initializes a new ThreadPoolExecutor instance.

        Args:
            max_workers: The maximum number of threads that can be used to
                execute the given calls.
        """
        jeżeli max_workers jest Nic:
            # Use this number because ThreadPoolExecutor jest often
            # used to overlap I/O instead of CPU work.
            max_workers = (os.cpu_count() albo 1) * 5
        jeżeli max_workers <= 0:
            podnieś ValueError("max_workers must be greater than 0")

        self._max_workers = max_workers
        self._work_queue = queue.Queue()
        self._threads = set()
        self._shutdown = Nieprawda
        self._shutdown_lock = threading.Lock()

    def submit(self, fn, *args, **kwargs):
        przy self._shutdown_lock:
            jeżeli self._shutdown:
                podnieś RuntimeError('cannot schedule new futures after shutdown')

            f = _base.Future()
            ww = _WorkItem(f, fn, args, kwargs)

            self._work_queue.put(ww)
            self._adjust_thread_count()
            zwróć f
    submit.__doc__ = _base.Executor.submit.__doc__

    def _adjust_thread_count(self):
        # When the executor gets lost, the weakref callback will wake up
        # the worker threads.
        def weakref_cb(_, q=self._work_queue):
            q.put(Nic)
        # TODO(bquinlan): Should avoid creating new threads jeżeli there are more
        # idle threads than items w the work queue.
        jeżeli len(self._threads) < self._max_workers:
            t = threading.Thread(target=_worker,
                                 args=(weakref.ref(self, weakref_cb),
                                       self._work_queue))
            t.daemon = Prawda
            t.start()
            self._threads.add(t)
            _threads_queues[t] = self._work_queue

    def shutdown(self, wait=Prawda):
        przy self._shutdown_lock:
            self._shutdown = Prawda
            self._work_queue.put(Nic)
        jeżeli wait:
            dla t w self._threads:
                t.join()
    shutdown.__doc__ = _base.Executor.shutdown.__doc__
