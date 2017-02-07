'''A multi-producer, multi-consumer queue.'''

spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    zaimportuj dummy_threading jako threading
z collections zaimportuj deque
z heapq zaimportuj heappush, heappop
z time zaimportuj monotonic jako time

__all__ = ['Empty', 'Full', 'Queue', 'PriorityQueue', 'LifoQueue']

klasa Empty(Exception):
    'Exception podnieśd by Queue.get(block=0)/get_nowait().'
    dalej

klasa Full(Exception):
    'Exception podnieśd by Queue.put(block=0)/put_nowait().'
    dalej

klasa Queue:
    '''Create a queue object przy a given maximum size.

    If maxsize jest <= 0, the queue size jest infinite.
    '''

    def __init__(self, maxsize=0):
        self.maxsize = maxsize
        self._init(maxsize)

        # mutex must be held whenever the queue jest mutating.  All methods
        # that acquire mutex must release it before returning.  mutex
        # jest shared between the three conditions, so acquiring oraz
        # releasing the conditions also acquires oraz releases mutex.
        self.mutex = threading.Lock()

        # Notify not_empty whenever an item jest added to the queue; a
        # thread waiting to get jest notified then.
        self.not_empty = threading.Condition(self.mutex)

        # Notify not_full whenever an item jest removed z the queue;
        # a thread waiting to put jest notified then.
        self.not_full = threading.Condition(self.mutex)

        # Notify all_tasks_done whenever the number of unfinished tasks
        # drops to zero; thread waiting to join() jest notified to resume
        self.all_tasks_done = threading.Condition(self.mutex)
        self.unfinished_tasks = 0

    def task_done(self):
        '''Indicate that a formerly enqueued task jest complete.

        Used by Queue consumer threads.  For each get() used to fetch a task,
        a subsequent call to task_done() tells the queue that the processing
        on the task jest complete.

        If a join() jest currently blocking, it will resume when all items
        have been processed (meaning that a task_done() call was received
        dla every item that had been put() into the queue).

        Raises a ValueError jeżeli called more times than there were items
        placed w the queue.
        '''
        przy self.all_tasks_done:
            unfinished = self.unfinished_tasks - 1
            jeżeli unfinished <= 0:
                jeżeli unfinished < 0:
                    podnieś ValueError('task_done() called too many times')
                self.all_tasks_done.notify_all()
            self.unfinished_tasks = unfinished

    def join(self):
        '''Blocks until all items w the Queue have been gotten oraz processed.

        The count of unfinished tasks goes up whenever an item jest added to the
        queue. The count goes down whenever a consumer thread calls task_done()
        to indicate the item was retrieved oraz all work on it jest complete.

        When the count of unfinished tasks drops to zero, join() unblocks.
        '''
        przy self.all_tasks_done:
            dopóki self.unfinished_tasks:
                self.all_tasks_done.wait()

    def qsize(self):
        '''Return the approximate size of the queue (nie reliable!).'''
        przy self.mutex:
            zwróć self._qsize()

    def empty(self):
        '''Return Prawda jeżeli the queue jest empty, Nieprawda otherwise (nie reliable!).

        This method jest likely to be removed at some point.  Use qsize() == 0
        jako a direct substitute, but be aware that either approach risks a race
        condition where a queue can grow before the result of empty() albo
        qsize() can be used.

        To create code that needs to wait dla all queued tasks to be
        completed, the preferred technique jest to use the join() method.
        '''
        przy self.mutex:
            zwróć nie self._qsize()

    def full(self):
        '''Return Prawda jeżeli the queue jest full, Nieprawda otherwise (nie reliable!).

        This method jest likely to be removed at some point.  Use qsize() >= n
        jako a direct substitute, but be aware that either approach risks a race
        condition where a queue can shrink before the result of full() albo
        qsize() can be used.
        '''
        przy self.mutex:
            zwróć 0 < self.maxsize <= self._qsize()

    def put(self, item, block=Prawda, timeout=Nic):
        '''Put an item into the queue.

        If optional args 'block' jest true oraz 'timeout' jest Nic (the default),
        block jeżeli necessary until a free slot jest available. If 'timeout' jest
        a non-negative number, it blocks at most 'timeout' seconds oraz podnieśs
        the Full exception jeżeli no free slot was available within that time.
        Otherwise ('block' jest false), put an item on the queue jeżeli a free slot
        jest immediately available, inaczej podnieś the Full exception ('timeout'
        jest ignored w that case).
        '''
        przy self.not_full:
            jeżeli self.maxsize > 0:
                jeżeli nie block:
                    jeżeli self._qsize() >= self.maxsize:
                        podnieś Full
                albo_inaczej timeout jest Nic:
                    dopóki self._qsize() >= self.maxsize:
                        self.not_full.wait()
                albo_inaczej timeout < 0:
                    podnieś ValueError("'timeout' must be a non-negative number")
                inaczej:
                    endtime = time() + timeout
                    dopóki self._qsize() >= self.maxsize:
                        remaining = endtime - time()
                        jeżeli remaining <= 0.0:
                            podnieś Full
                        self.not_full.wait(remaining)
            self._put(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()

    def get(self, block=Prawda, timeout=Nic):
        '''Remove oraz zwróć an item z the queue.

        If optional args 'block' jest true oraz 'timeout' jest Nic (the default),
        block jeżeli necessary until an item jest available. If 'timeout' jest
        a non-negative number, it blocks at most 'timeout' seconds oraz podnieśs
        the Empty exception jeżeli no item was available within that time.
        Otherwise ('block' jest false), zwróć an item jeżeli one jest immediately
        available, inaczej podnieś the Empty exception ('timeout' jest ignored
        w that case).
        '''
        przy self.not_empty:
            jeżeli nie block:
                jeżeli nie self._qsize():
                    podnieś Empty
            albo_inaczej timeout jest Nic:
                dopóki nie self._qsize():
                    self.not_empty.wait()
            albo_inaczej timeout < 0:
                podnieś ValueError("'timeout' must be a non-negative number")
            inaczej:
                endtime = time() + timeout
                dopóki nie self._qsize():
                    remaining = endtime - time()
                    jeżeli remaining <= 0.0:
                        podnieś Empty
                    self.not_empty.wait(remaining)
            item = self._get()
            self.not_full.notify()
            zwróć item

    def put_nowait(self, item):
        '''Put an item into the queue without blocking.

        Only enqueue the item jeżeli a free slot jest immediately available.
        Otherwise podnieś the Full exception.
        '''
        zwróć self.put(item, block=Nieprawda)

    def get_nowait(self):
        '''Remove oraz zwróć an item z the queue without blocking.

        Only get an item jeżeli one jest immediately available. Otherwise
        podnieś the Empty exception.
        '''
        zwróć self.get(block=Nieprawda)

    # Override these methods to implement other queue organizations
    # (e.g. stack albo priority queue).
    # These will only be called przy appropriate locks held

    # Initialize the queue representation
    def _init(self, maxsize):
        self.queue = deque()

    def _qsize(self):
        zwróć len(self.queue)

    # Put a new item w the queue
    def _put(self, item):
        self.queue.append(item)

    # Get an item z the queue
    def _get(self):
        zwróć self.queue.popleft()


klasa PriorityQueue(Queue):
    '''Variant of Queue that retrieves open entries w priority order (lowest first).

    Entries are typically tuples of the form:  (priority number, data).
    '''

    def _init(self, maxsize):
        self.queue = []

    def _qsize(self):
        zwróć len(self.queue)

    def _put(self, item):
        heappush(self.queue, item)

    def _get(self):
        zwróć heappop(self.queue)


klasa LifoQueue(Queue):
    '''Variant of Queue that retrieves most recently added entries first.'''

    def _init(self, maxsize):
        self.queue = []

    def _qsize(self):
        zwróć len(self.queue)

    def _put(self, item):
        self.queue.append(item)

    def _get(self):
        zwróć self.queue.pop()
