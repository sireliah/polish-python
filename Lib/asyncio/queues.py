"""Queues"""

__all__ = ['Queue', 'PriorityQueue', 'LifoQueue', 'QueueFull', 'QueueEmpty']

zaimportuj collections
zaimportuj heapq

z . zaimportuj compat
z . zaimportuj events
z . zaimportuj futures
z . zaimportuj locks
z .coroutines zaimportuj coroutine


klasa QueueEmpty(Exception):
    """Exception podnieśd when Queue.get_nowait() jest called on a Queue object
    which jest empty.
    """
    dalej


klasa QueueFull(Exception):
    """Exception podnieśd when the Queue.put_nowait() method jest called on a Queue
    object which jest full.
    """
    dalej


klasa Queue:
    """A queue, useful dla coordinating producer oraz consumer coroutines.

    If maxsize jest less than albo equal to zero, the queue size jest infinite. If it
    jest an integer greater than 0, then "uzyskaj z put()" will block when the
    queue reaches maxsize, until an item jest removed by get().

    Unlike the standard library Queue, you can reliably know this Queue's size
    przy qsize(), since your single-threaded asyncio application won't be
    interrupted between calling qsize() oraz doing an operation on the Queue.
    """

    def __init__(self, maxsize=0, *, loop=Nic):
        jeżeli loop jest Nic:
            self._loop = events.get_event_loop()
        inaczej:
            self._loop = loop
        self._maxsize = maxsize

        # Futures.
        self._getters = collections.deque()
        # Futures
        self._putters = collections.deque()
        self._unfinished_tasks = 0
        self._finished = locks.Event(loop=self._loop)
        self._finished.set()
        self._init(maxsize)

    # These three are overridable w subclasses.

    def _init(self, maxsize):
        self._queue = collections.deque()

    def _get(self):
        zwróć self._queue.popleft()

    def _put(self, item):
        self._queue.append(item)

    # End of the overridable methods.

    def __put_internal(self, item):
        self._put(item)
        self._unfinished_tasks += 1
        self._finished.clear()

    def __repr__(self):
        zwróć '<{} at {:#x} {}>'.format(
            type(self).__name__, id(self), self._format())

    def __str__(self):
        zwróć '<{} {}>'.format(type(self).__name__, self._format())

    def _format(self):
        result = 'maxsize={!r}'.format(self._maxsize)
        jeżeli getattr(self, '_queue', Nic):
            result += ' _queue={!r}'.format(list(self._queue))
        jeżeli self._getters:
            result += ' _getters[{}]'.format(len(self._getters))
        jeżeli self._putters:
            result += ' _putters[{}]'.format(len(self._putters))
        jeżeli self._unfinished_tasks:
            result += ' tasks={}'.format(self._unfinished_tasks)
        zwróć result

    def _consume_done_getters(self):
        # Delete waiters at the head of the get() queue who've timed out.
        dopóki self._getters oraz self._getters[0].done():
            self._getters.popleft()

    def _consume_done_putters(self):
        # Delete waiters at the head of the put() queue who've timed out.
        dopóki self._putters oraz self._putters[0].done():
            self._putters.popleft()

    def qsize(self):
        """Number of items w the queue."""
        zwróć len(self._queue)

    @property
    def maxsize(self):
        """Number of items allowed w the queue."""
        zwróć self._maxsize

    def empty(self):
        """Return Prawda jeżeli the queue jest empty, Nieprawda otherwise."""
        zwróć nie self._queue

    def full(self):
        """Return Prawda jeżeli there are maxsize items w the queue.

        Note: jeżeli the Queue was initialized przy maxsize=0 (the default),
        then full() jest never Prawda.
        """
        jeżeli self._maxsize <= 0:
            zwróć Nieprawda
        inaczej:
            zwróć self.qsize() >= self._maxsize

    @coroutine
    def put(self, item):
        """Put an item into the queue.

        Put an item into the queue. If the queue jest full, wait until a free
        slot jest available before adding item.

        This method jest a coroutine.
        """
        self._consume_done_getters()
        jeżeli self._getters:
            assert nie self._queue, (
                'queue non-empty, why are getters waiting?')

            getter = self._getters.popleft()
            self.__put_internal(item)

            # getter cannot be cancelled, we just removed done getters
            getter.set_result(self._get())

        albo_inaczej self._maxsize > 0 oraz self._maxsize <= self.qsize():
            waiter = futures.Future(loop=self._loop)

            self._putters.append(waiter)
            uzyskaj z waiter
            self._put(item)

        inaczej:
            self.__put_internal(item)

    def put_nowait(self, item):
        """Put an item into the queue without blocking.

        If no free slot jest immediately available, podnieś QueueFull.
        """
        self._consume_done_getters()
        jeżeli self._getters:
            assert nie self._queue, (
                'queue non-empty, why are getters waiting?')

            getter = self._getters.popleft()
            self.__put_internal(item)

            # getter cannot be cancelled, we just removed done getters
            getter.set_result(self._get())

        albo_inaczej self._maxsize > 0 oraz self._maxsize <= self.qsize():
            podnieś QueueFull
        inaczej:
            self.__put_internal(item)

    @coroutine
    def get(self):
        """Remove oraz zwróć an item z the queue.

        If queue jest empty, wait until an item jest available.

        This method jest a coroutine.
        """
        self._consume_done_putters()
        jeżeli self._putters:
            assert self.full(), 'queue nie full, why are putters waiting?'
            putter = self._putters.popleft()

            # When a getter runs oraz frees up a slot so this putter can
            # run, we need to defer the put dla a tick to ensure that
            # getters oraz putters alternate perfectly. See
            # ChannelTest.test_wait.
            self._loop.call_soon(putter._set_result_unless_cancelled, Nic)

            zwróć self._get()

        albo_inaczej self.qsize():
            zwróć self._get()
        inaczej:
            waiter = futures.Future(loop=self._loop)
            self._getters.append(waiter)
            spróbuj:
                zwróć (uzyskaj z waiter)
            wyjąwszy futures.CancelledError:
                # jeżeli we get CancelledError, it means someone cancelled this
                # get() coroutine.  But there jest a chance that the waiter
                # already jest ready oraz contains an item that has just been
                # removed z the queue.  In this case, we need to put the item
                # back into the front of the queue.  This get() must either
                # succeed without fault or, jeżeli it gets cancelled, it must be as
                # jeżeli it never happened.
                jeżeli waiter.done():
                    self._put_it_back(waiter.result())
                podnieś

    def _put_it_back(self, item):
        """
        This jest called when we have a waiter to get() an item oraz this waiter
        gets cancelled.  In this case, we put the item back: wake up another
        waiter albo put it w the _queue.
        """
        self._consume_done_getters()
        jeżeli self._getters:
            assert nie self._queue, (
                'queue non-empty, why are getters waiting?')

            getter = self._getters.popleft()
            self.__put_internal(item)

            # getter cannot be cancelled, we just removed done getters
            getter.set_result(item)
        inaczej:
            self._queue.appendleft(item)

    def get_nowait(self):
        """Remove oraz zwróć an item z the queue.

        Return an item jeżeli one jest immediately available, inaczej podnieś QueueEmpty.
        """
        self._consume_done_putters()
        jeżeli self._putters:
            assert self.full(), 'queue nie full, why are putters waiting?'
            putter = self._putters.popleft()
            # Wake putter on next tick.

            # getter cannot be cancelled, we just removed done putters
            putter.set_result(Nic)

            zwróć self._get()

        albo_inaczej self.qsize():
            zwróć self._get()
        inaczej:
            podnieś QueueEmpty

    def task_done(self):
        """Indicate that a formerly enqueued task jest complete.

        Used by queue consumers. For each get() used to fetch a task,
        a subsequent call to task_done() tells the queue that the processing
        on the task jest complete.

        If a join() jest currently blocking, it will resume when all items have
        been processed (meaning that a task_done() call was received dla every
        item that had been put() into the queue).

        Raises ValueError jeżeli called more times than there were items placed w
        the queue.
        """
        jeżeli self._unfinished_tasks <= 0:
            podnieś ValueError('task_done() called too many times')
        self._unfinished_tasks -= 1
        jeżeli self._unfinished_tasks == 0:
            self._finished.set()

    @coroutine
    def join(self):
        """Block until all items w the queue have been gotten oraz processed.

        The count of unfinished tasks goes up whenever an item jest added to the
        queue. The count goes down whenever a consumer calls task_done() to
        indicate that the item was retrieved oraz all work on it jest complete.
        When the count of unfinished tasks drops to zero, join() unblocks.
        """
        jeżeli self._unfinished_tasks > 0:
            uzyskaj z self._finished.wait()


klasa PriorityQueue(Queue):
    """A subclass of Queue; retrieves entries w priority order (lowest first).

    Entries are typically tuples of the form: (priority number, data).
    """

    def _init(self, maxsize):
        self._queue = []

    def _put(self, item, heappush=heapq.heappush):
        heappush(self._queue, item)

    def _get(self, heappop=heapq.heappop):
        zwróć heappop(self._queue)


klasa LifoQueue(Queue):
    """A subclass of Queue that retrieves most recently added entries first."""

    def _init(self, maxsize):
        self._queue = []

    def _put(self, item):
        self._queue.append(item)

    def _get(self):
        zwróć self._queue.pop()


jeżeli nie compat.PY35:
    JoinableQueue = Queue
    """Deprecated alias dla Queue."""
    __all__.append('JoinableQueue')
