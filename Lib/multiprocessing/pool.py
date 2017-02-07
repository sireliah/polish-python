#
# Module providing the `Pool` klasa dla managing a process pool
#
# multiprocessing/pool.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

__all__ = ['Pool', 'ThreadPool']

#
# Imports
#

zaimportuj threading
zaimportuj queue
zaimportuj itertools
zaimportuj collections
zaimportuj os
zaimportuj time
zaimportuj traceback

# If threading jest available then ThreadPool should be provided.  Therefore
# we avoid top-level imports which are liable to fail on some systems.
z . zaimportuj util
z . zaimportuj get_context, TimeoutError

#
# Constants representing the state of a pool
#

RUN = 0
CLOSE = 1
TERMINATE = 2

#
# Miscellaneous
#

job_counter = itertools.count()

def mapstar(args):
    zwróć list(map(*args))

def starmapstar(args):
    zwróć list(itertools.starmap(args[0], args[1]))

#
# Hack to embed stringification of remote traceback w local traceback
#

klasa RemoteTraceback(Exception):
    def __init__(self, tb):
        self.tb = tb
    def __str__(self):
        zwróć self.tb

klasa ExceptionWithTraceback:
    def __init__(self, exc, tb):
        tb = traceback.format_exception(type(exc), exc, tb)
        tb = ''.join(tb)
        self.exc = exc
        self.tb = '\n"""\n%s"""' % tb
    def __reduce__(self):
        zwróć rebuild_exc, (self.exc, self.tb)

def rebuild_exc(exc, tb):
    exc.__cause__ = RemoteTraceback(tb)
    zwróć exc

#
# Code run by worker processes
#

klasa MaybeEncodingError(Exception):
    """Wraps possible unpickleable errors, so they can be
    safely sent through the socket."""

    def __init__(self, exc, value):
        self.exc = repr(exc)
        self.value = repr(value)
        super(MaybeEncodingError, self).__init__(self.exc, self.value)

    def __str__(self):
        zwróć "Error sending result: '%s'. Reason: '%s'" % (self.value,
                                                             self.exc)

    def __repr__(self):
        zwróć "<%s: %s>" % (self.__class__.__name__, self)


def worker(inqueue, outqueue, initializer=Nic, initargs=(), maxtasks=Nic,
           wrap_exception=Nieprawda):
    assert maxtasks jest Nic albo (type(maxtasks) == int oraz maxtasks > 0)
    put = outqueue.put
    get = inqueue.get
    jeżeli hasattr(inqueue, '_writer'):
        inqueue._writer.close()
        outqueue._reader.close()

    jeżeli initializer jest nie Nic:
        initializer(*initargs)

    completed = 0
    dopóki maxtasks jest Nic albo (maxtasks oraz completed < maxtasks):
        spróbuj:
            task = get()
        wyjąwszy (EOFError, OSError):
            util.debug('worker got EOFError albo OSError -- exiting')
            przerwij

        jeżeli task jest Nic:
            util.debug('worker got sentinel -- exiting')
            przerwij

        job, i, func, args, kwds = task
        spróbuj:
            result = (Prawda, func(*args, **kwds))
        wyjąwszy Exception jako e:
            jeżeli wrap_exception:
                e = ExceptionWithTraceback(e, e.__traceback__)
            result = (Nieprawda, e)
        spróbuj:
            put((job, i, result))
        wyjąwszy Exception jako e:
            wrapped = MaybeEncodingError(e, result[1])
            util.debug("Possible encoding error dopóki sending result: %s" % (
                wrapped))
            put((job, i, (Nieprawda, wrapped)))
        completed += 1
    util.debug('worker exiting after %d tasks' % completed)

#
# Class representing a process pool
#

klasa Pool(object):
    '''
    Class which supports an async version of applying functions to arguments.
    '''
    _wrap_exception = Prawda

    def Process(self, *args, **kwds):
        zwróć self._ctx.Process(*args, **kwds)

    def __init__(self, processes=Nic, initializer=Nic, initargs=(),
                 maxtasksperchild=Nic, context=Nic):
        self._ctx = context albo get_context()
        self._setup_queues()
        self._taskqueue = queue.Queue()
        self._cache = {}
        self._state = RUN
        self._maxtasksperchild = maxtasksperchild
        self._initializer = initializer
        self._initargs = initargs

        jeżeli processes jest Nic:
            processes = os.cpu_count() albo 1
        jeżeli processes < 1:
            podnieś ValueError("Number of processes must be at least 1")

        jeżeli initializer jest nie Nic oraz nie callable(initializer):
            podnieś TypeError('initializer must be a callable')

        self._processes = processes
        self._pool = []
        self._repopulate_pool()

        self._worker_handler = threading.Thread(
            target=Pool._handle_workers,
            args=(self, )
            )
        self._worker_handler.daemon = Prawda
        self._worker_handler._state = RUN
        self._worker_handler.start()


        self._task_handler = threading.Thread(
            target=Pool._handle_tasks,
            args=(self._taskqueue, self._quick_put, self._outqueue,
                  self._pool, self._cache)
            )
        self._task_handler.daemon = Prawda
        self._task_handler._state = RUN
        self._task_handler.start()

        self._result_handler = threading.Thread(
            target=Pool._handle_results,
            args=(self._outqueue, self._quick_get, self._cache)
            )
        self._result_handler.daemon = Prawda
        self._result_handler._state = RUN
        self._result_handler.start()

        self._terminate = util.Finalize(
            self, self._terminate_pool,
            args=(self._taskqueue, self._inqueue, self._outqueue, self._pool,
                  self._worker_handler, self._task_handler,
                  self._result_handler, self._cache),
            exitpriority=15
            )

    def _join_exited_workers(self):
        """Cleanup after any worker processes which have exited due to reaching
        their specified lifetime.  Returns Prawda jeżeli any workers were cleaned up.
        """
        cleaned = Nieprawda
        dla i w reversed(range(len(self._pool))):
            worker = self._pool[i]
            jeżeli worker.exitcode jest nie Nic:
                # worker exited
                util.debug('cleaning up worker %d' % i)
                worker.join()
                cleaned = Prawda
                usuń self._pool[i]
        zwróć cleaned

    def _repopulate_pool(self):
        """Bring the number of pool processes up to the specified number,
        dla use after reaping workers which have exited.
        """
        dla i w range(self._processes - len(self._pool)):
            w = self.Process(target=worker,
                             args=(self._inqueue, self._outqueue,
                                   self._initializer,
                                   self._initargs, self._maxtasksperchild,
                                   self._wrap_exception)
                            )
            self._pool.append(w)
            w.name = w.name.replace('Process', 'PoolWorker')
            w.daemon = Prawda
            w.start()
            util.debug('added worker')

    def _maintain_pool(self):
        """Clean up any exited workers oraz start replacements dla them.
        """
        jeżeli self._join_exited_workers():
            self._repopulate_pool()

    def _setup_queues(self):
        self._inqueue = self._ctx.SimpleQueue()
        self._outqueue = self._ctx.SimpleQueue()
        self._quick_put = self._inqueue._writer.send
        self._quick_get = self._outqueue._reader.recv

    def apply(self, func, args=(), kwds={}):
        '''
        Equivalent of `func(*args, **kwds)`.
        '''
        assert self._state == RUN
        zwróć self.apply_async(func, args, kwds).get()

    def map(self, func, iterable, chunksize=Nic):
        '''
        Apply `func` to each element w `iterable`, collecting the results
        w a list that jest returned.
        '''
        zwróć self._map_async(func, iterable, mapstar, chunksize).get()

    def starmap(self, func, iterable, chunksize=Nic):
        '''
        Like `map()` method but the elements of the `iterable` are expected to
        be iterables jako well oraz will be unpacked jako arguments. Hence
        `func` oraz (a, b) becomes func(a, b).
        '''
        zwróć self._map_async(func, iterable, starmapstar, chunksize).get()

    def starmap_async(self, func, iterable, chunksize=Nic, callback=Nic,
            error_callback=Nic):
        '''
        Asynchronous version of `starmap()` method.
        '''
        zwróć self._map_async(func, iterable, starmapstar, chunksize,
                               callback, error_callback)

    def imap(self, func, iterable, chunksize=1):
        '''
        Equivalent of `map()` -- can be MUCH slower than `Pool.map()`.
        '''
        jeżeli self._state != RUN:
            podnieś ValueError("Pool nie running")
        jeżeli chunksize == 1:
            result = IMapIterator(self._cache)
            self._taskqueue.put((((result._job, i, func, (x,), {})
                         dla i, x w enumerate(iterable)), result._set_length))
            zwróć result
        inaczej:
            assert chunksize > 1
            task_batches = Pool._get_tasks(func, iterable, chunksize)
            result = IMapIterator(self._cache)
            self._taskqueue.put((((result._job, i, mapstar, (x,), {})
                     dla i, x w enumerate(task_batches)), result._set_length))
            zwróć (item dla chunk w result dla item w chunk)

    def imap_unordered(self, func, iterable, chunksize=1):
        '''
        Like `imap()` method but ordering of results jest arbitrary.
        '''
        jeżeli self._state != RUN:
            podnieś ValueError("Pool nie running")
        jeżeli chunksize == 1:
            result = IMapUnorderedIterator(self._cache)
            self._taskqueue.put((((result._job, i, func, (x,), {})
                         dla i, x w enumerate(iterable)), result._set_length))
            zwróć result
        inaczej:
            assert chunksize > 1
            task_batches = Pool._get_tasks(func, iterable, chunksize)
            result = IMapUnorderedIterator(self._cache)
            self._taskqueue.put((((result._job, i, mapstar, (x,), {})
                     dla i, x w enumerate(task_batches)), result._set_length))
            zwróć (item dla chunk w result dla item w chunk)

    def apply_async(self, func, args=(), kwds={}, callback=Nic,
            error_callback=Nic):
        '''
        Asynchronous version of `apply()` method.
        '''
        jeżeli self._state != RUN:
            podnieś ValueError("Pool nie running")
        result = ApplyResult(self._cache, callback, error_callback)
        self._taskqueue.put(([(result._job, Nic, func, args, kwds)], Nic))
        zwróć result

    def map_async(self, func, iterable, chunksize=Nic, callback=Nic,
            error_callback=Nic):
        '''
        Asynchronous version of `map()` method.
        '''
        zwróć self._map_async(func, iterable, mapstar, chunksize, callback,
            error_callback)

    def _map_async(self, func, iterable, mapper, chunksize=Nic, callback=Nic,
            error_callback=Nic):
        '''
        Helper function to implement map, starmap oraz their async counterparts.
        '''
        jeżeli self._state != RUN:
            podnieś ValueError("Pool nie running")
        jeżeli nie hasattr(iterable, '__len__'):
            iterable = list(iterable)

        jeżeli chunksize jest Nic:
            chunksize, extra = divmod(len(iterable), len(self._pool) * 4)
            jeżeli extra:
                chunksize += 1
        jeżeli len(iterable) == 0:
            chunksize = 0

        task_batches = Pool._get_tasks(func, iterable, chunksize)
        result = MapResult(self._cache, chunksize, len(iterable), callback,
                           error_callback=error_callback)
        self._taskqueue.put((((result._job, i, mapper, (x,), {})
                              dla i, x w enumerate(task_batches)), Nic))
        zwróć result

    @staticmethod
    def _handle_workers(pool):
        thread = threading.current_thread()

        # Keep maintaining workers until the cache gets drained, unless the pool
        # jest terminated.
        dopóki thread._state == RUN albo (pool._cache oraz thread._state != TERMINATE):
            pool._maintain_pool()
            time.sleep(0.1)
        # send sentinel to stop workers
        pool._taskqueue.put(Nic)
        util.debug('worker handler exiting')

    @staticmethod
    def _handle_tasks(taskqueue, put, outqueue, pool, cache):
        thread = threading.current_thread()

        dla taskseq, set_length w iter(taskqueue.get, Nic):
            task = Nic
            i = -1
            spróbuj:
                dla i, task w enumerate(taskseq):
                    jeżeli thread._state:
                        util.debug('task handler found thread._state != RUN')
                        przerwij
                    spróbuj:
                        put(task)
                    wyjąwszy Exception jako e:
                        job, ind = task[:2]
                        spróbuj:
                            cache[job]._set(ind, (Nieprawda, e))
                        wyjąwszy KeyError:
                            dalej
                inaczej:
                    jeżeli set_length:
                        util.debug('doing set_length()')
                        set_length(i+1)
                    kontynuuj
                przerwij
            wyjąwszy Exception jako ex:
                job, ind = task[:2] jeżeli task inaczej (0, 0)
                jeżeli job w cache:
                    cache[job]._set(ind + 1, (Nieprawda, ex))
                jeżeli set_length:
                    util.debug('doing set_length()')
                    set_length(i+1)
        inaczej:
            util.debug('task handler got sentinel')


        spróbuj:
            # tell result handler to finish when cache jest empty
            util.debug('task handler sending sentinel to result handler')
            outqueue.put(Nic)

            # tell workers there jest no more work
            util.debug('task handler sending sentinel to workers')
            dla p w pool:
                put(Nic)
        wyjąwszy OSError:
            util.debug('task handler got OSError when sending sentinels')

        util.debug('task handler exiting')

    @staticmethod
    def _handle_results(outqueue, get, cache):
        thread = threading.current_thread()

        dopóki 1:
            spróbuj:
                task = get()
            wyjąwszy (OSError, EOFError):
                util.debug('result handler got EOFError/OSError -- exiting')
                zwróć

            jeżeli thread._state:
                assert thread._state == TERMINATE
                util.debug('result handler found thread._state=TERMINATE')
                przerwij

            jeżeli task jest Nic:
                util.debug('result handler got sentinel')
                przerwij

            job, i, obj = task
            spróbuj:
                cache[job]._set(i, obj)
            wyjąwszy KeyError:
                dalej

        dopóki cache oraz thread._state != TERMINATE:
            spróbuj:
                task = get()
            wyjąwszy (OSError, EOFError):
                util.debug('result handler got EOFError/OSError -- exiting')
                zwróć

            jeżeli task jest Nic:
                util.debug('result handler ignoring extra sentinel')
                kontynuuj
            job, i, obj = task
            spróbuj:
                cache[job]._set(i, obj)
            wyjąwszy KeyError:
                dalej

        jeżeli hasattr(outqueue, '_reader'):
            util.debug('ensuring that outqueue jest nie full')
            # If we don't make room available w outqueue then
            # attempts to add the sentinel (Nic) to outqueue may
            # block.  There jest guaranteed to be no more than 2 sentinels.
            spróbuj:
                dla i w range(10):
                    jeżeli nie outqueue._reader.poll():
                        przerwij
                    get()
            wyjąwszy (OSError, EOFError):
                dalej

        util.debug('result handler exiting: len(cache)=%s, thread._state=%s',
              len(cache), thread._state)

    @staticmethod
    def _get_tasks(func, it, size):
        it = iter(it)
        dopóki 1:
            x = tuple(itertools.islice(it, size))
            jeżeli nie x:
                zwróć
            uzyskaj (func, x)

    def __reduce__(self):
        podnieś NotImplementedError(
              'pool objects cannot be dalejed between processes albo pickled'
              )

    def close(self):
        util.debug('closing pool')
        jeżeli self._state == RUN:
            self._state = CLOSE
            self._worker_handler._state = CLOSE

    def terminate(self):
        util.debug('terminating pool')
        self._state = TERMINATE
        self._worker_handler._state = TERMINATE
        self._terminate()

    def join(self):
        util.debug('joining pool')
        assert self._state w (CLOSE, TERMINATE)
        self._worker_handler.join()
        self._task_handler.join()
        self._result_handler.join()
        dla p w self._pool:
            p.join()

    @staticmethod
    def _help_stuff_finish(inqueue, task_handler, size):
        # task_handler may be blocked trying to put items on inqueue
        util.debug('removing tasks z inqueue until task handler finished')
        inqueue._rlock.acquire()
        dopóki task_handler.is_alive() oraz inqueue._reader.poll():
            inqueue._reader.recv()
            time.sleep(0)

    @classmethod
    def _terminate_pool(cls, taskqueue, inqueue, outqueue, pool,
                        worker_handler, task_handler, result_handler, cache):
        # this jest guaranteed to only be called once
        util.debug('finalizing pool')

        worker_handler._state = TERMINATE
        task_handler._state = TERMINATE

        util.debug('helping task handler/workers to finish')
        cls._help_stuff_finish(inqueue, task_handler, len(pool))

        assert result_handler.is_alive() albo len(cache) == 0

        result_handler._state = TERMINATE
        outqueue.put(Nic)                  # sentinel

        # We must wait dla the worker handler to exit before terminating
        # workers because we don't want workers to be restarted behind our back.
        util.debug('joining worker handler')
        jeżeli threading.current_thread() jest nie worker_handler:
            worker_handler.join()

        # Terminate workers which haven't already finished.
        jeżeli pool oraz hasattr(pool[0], 'terminate'):
            util.debug('terminating workers')
            dla p w pool:
                jeżeli p.exitcode jest Nic:
                    p.terminate()

        util.debug('joining task handler')
        jeżeli threading.current_thread() jest nie task_handler:
            task_handler.join()

        util.debug('joining result handler')
        jeżeli threading.current_thread() jest nie result_handler:
            result_handler.join()

        jeżeli pool oraz hasattr(pool[0], 'terminate'):
            util.debug('joining pool workers')
            dla p w pool:
                jeżeli p.is_alive():
                    # worker has nie yet exited
                    util.debug('cleaning up worker %d' % p.pid)
                    p.join()

    def __enter__(self):
        zwróć self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()

#
# Class whose instances are returned by `Pool.apply_async()`
#

klasa ApplyResult(object):

    def __init__(self, cache, callback, error_callback):
        self._event = threading.Event()
        self._job = next(job_counter)
        self._cache = cache
        self._callback = callback
        self._error_callback = error_callback
        cache[self._job] = self

    def ready(self):
        zwróć self._event.is_set()

    def successful(self):
        assert self.ready()
        zwróć self._success

    def wait(self, timeout=Nic):
        self._event.wait(timeout)

    def get(self, timeout=Nic):
        self.wait(timeout)
        jeżeli nie self.ready():
            podnieś TimeoutError
        jeżeli self._success:
            zwróć self._value
        inaczej:
            podnieś self._value

    def _set(self, i, obj):
        self._success, self._value = obj
        jeżeli self._callback oraz self._success:
            self._callback(self._value)
        jeżeli self._error_callback oraz nie self._success:
            self._error_callback(self._value)
        self._event.set()
        usuń self._cache[self._job]

AsyncResult = ApplyResult       # create alias -- see #17805

#
# Class whose instances are returned by `Pool.map_async()`
#

klasa MapResult(ApplyResult):

    def __init__(self, cache, chunksize, length, callback, error_callback):
        ApplyResult.__init__(self, cache, callback,
                             error_callback=error_callback)
        self._success = Prawda
        self._value = [Nic] * length
        self._chunksize = chunksize
        jeżeli chunksize <= 0:
            self._number_left = 0
            self._event.set()
            usuń cache[self._job]
        inaczej:
            self._number_left = length//chunksize + bool(length % chunksize)

    def _set(self, i, success_result):
        success, result = success_result
        jeżeli success:
            self._value[i*self._chunksize:(i+1)*self._chunksize] = result
            self._number_left -= 1
            jeżeli self._number_left == 0:
                jeżeli self._callback:
                    self._callback(self._value)
                usuń self._cache[self._job]
                self._event.set()
        inaczej:
            self._success = Nieprawda
            self._value = result
            jeżeli self._error_callback:
                self._error_callback(self._value)
            usuń self._cache[self._job]
            self._event.set()

#
# Class whose instances are returned by `Pool.imap()`
#

klasa IMapIterator(object):

    def __init__(self, cache):
        self._cond = threading.Condition(threading.Lock())
        self._job = next(job_counter)
        self._cache = cache
        self._items = collections.deque()
        self._index = 0
        self._length = Nic
        self._unsorted = {}
        cache[self._job] = self

    def __iter__(self):
        zwróć self

    def next(self, timeout=Nic):
        przy self._cond:
            spróbuj:
                item = self._items.popleft()
            wyjąwszy IndexError:
                jeżeli self._index == self._length:
                    podnieś StopIteration
                self._cond.wait(timeout)
                spróbuj:
                    item = self._items.popleft()
                wyjąwszy IndexError:
                    jeżeli self._index == self._length:
                        podnieś StopIteration
                    podnieś TimeoutError

        success, value = item
        jeżeli success:
            zwróć value
        podnieś value

    __next__ = next                    # XXX

    def _set(self, i, obj):
        przy self._cond:
            jeżeli self._index == i:
                self._items.append(obj)
                self._index += 1
                dopóki self._index w self._unsorted:
                    obj = self._unsorted.pop(self._index)
                    self._items.append(obj)
                    self._index += 1
                self._cond.notify()
            inaczej:
                self._unsorted[i] = obj

            jeżeli self._index == self._length:
                usuń self._cache[self._job]

    def _set_length(self, length):
        przy self._cond:
            self._length = length
            jeżeli self._index == self._length:
                self._cond.notify()
                usuń self._cache[self._job]

#
# Class whose instances are returned by `Pool.imap_unordered()`
#

klasa IMapUnorderedIterator(IMapIterator):

    def _set(self, i, obj):
        przy self._cond:
            self._items.append(obj)
            self._index += 1
            self._cond.notify()
            jeżeli self._index == self._length:
                usuń self._cache[self._job]

#
#
#

klasa ThreadPool(Pool):
    _wrap_exception = Nieprawda

    @staticmethod
    def Process(*args, **kwds):
        z .dummy zaimportuj Process
        zwróć Process(*args, **kwds)

    def __init__(self, processes=Nic, initializer=Nic, initargs=()):
        Pool.__init__(self, processes, initializer, initargs)

    def _setup_queues(self):
        self._inqueue = queue.Queue()
        self._outqueue = queue.Queue()
        self._quick_put = self._inqueue.put
        self._quick_get = self._outqueue.get

    @staticmethod
    def _help_stuff_finish(inqueue, task_handler, size):
        # put sentinels at head of inqueue to make workers finish
        przy inqueue.not_empty:
            inqueue.queue.clear()
            inqueue.queue.extend([Nic] * size)
            inqueue.not_empty.notify_all()
