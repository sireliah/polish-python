#
# Module implementing queues
#
# multiprocessing/queues.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

__all__ = ['Queue', 'SimpleQueue', 'JoinableQueue']

zaimportuj sys
zaimportuj os
zaimportuj threading
zaimportuj collections
zaimportuj time
zaimportuj weakref
zaimportuj errno

z queue zaimportuj Empty, Full

zaimportuj _multiprocessing

z . zaimportuj connection
z . zaimportuj context

z .util zaimportuj debug, info, Finalize, register_after_fork, is_exiting
z .reduction zaimportuj ForkingPickler

#
# Queue type using a pipe, buffer oraz thread
#

klasa Queue(object):

    def __init__(self, maxsize=0, *, ctx):
        jeżeli maxsize <= 0:
            # Can podnieś ImportError (see issues #3770 oraz #23400)
            z .synchronize zaimportuj SEM_VALUE_MAX jako maxsize
        self._maxsize = maxsize
        self._reader, self._writer = connection.Pipe(duplex=Nieprawda)
        self._rlock = ctx.Lock()
        self._opid = os.getpid()
        jeżeli sys.platform == 'win32':
            self._wlock = Nic
        inaczej:
            self._wlock = ctx.Lock()
        self._sem = ctx.BoundedSemaphore(maxsize)
        # For use by concurrent.futures
        self._ignore_epipe = Nieprawda

        self._after_fork()

        jeżeli sys.platform != 'win32':
            register_after_fork(self, Queue._after_fork)

    def __getstate__(self):
        context.assert_spawning(self)
        zwróć (self._ignore_epipe, self._maxsize, self._reader, self._writer,
                self._rlock, self._wlock, self._sem, self._opid)

    def __setstate__(self, state):
        (self._ignore_epipe, self._maxsize, self._reader, self._writer,
         self._rlock, self._wlock, self._sem, self._opid) = state
        self._after_fork()

    def _after_fork(self):
        debug('Queue._after_fork()')
        self._notempty = threading.Condition(threading.Lock())
        self._buffer = collections.deque()
        self._thread = Nic
        self._jointhread = Nic
        self._joincancelled = Nieprawda
        self._closed = Nieprawda
        self._close = Nic
        self._send_bytes = self._writer.send_bytes
        self._recv_bytes = self._reader.recv_bytes
        self._poll = self._reader.poll

    def put(self, obj, block=Prawda, timeout=Nic):
        assert nie self._closed
        jeżeli nie self._sem.acquire(block, timeout):
            podnieś Full

        przy self._notempty:
            jeżeli self._thread jest Nic:
                self._start_thread()
            self._buffer.append(obj)
            self._notempty.notify()

    def get(self, block=Prawda, timeout=Nic):
        jeżeli block oraz timeout jest Nic:
            przy self._rlock:
                res = self._recv_bytes()
            self._sem.release()
        inaczej:
            jeżeli block:
                deadline = time.time() + timeout
            jeżeli nie self._rlock.acquire(block, timeout):
                podnieś Empty
            spróbuj:
                jeżeli block:
                    timeout = deadline - time.time()
                    jeżeli timeout < 0 albo nie self._poll(timeout):
                        podnieś Empty
                albo_inaczej nie self._poll():
                    podnieś Empty
                res = self._recv_bytes()
                self._sem.release()
            w_końcu:
                self._rlock.release()
        # unserialize the data after having released the lock
        zwróć ForkingPickler.loads(res)

    def qsize(self):
        # Raises NotImplementedError on Mac OSX because of broken sem_getvalue()
        zwróć self._maxsize - self._sem._semlock._get_value()

    def empty(self):
        zwróć nie self._poll()

    def full(self):
        zwróć self._sem._semlock._is_zero()

    def get_nowait(self):
        zwróć self.get(Nieprawda)

    def put_nowait(self, obj):
        zwróć self.put(obj, Nieprawda)

    def close(self):
        self._closed = Prawda
        spróbuj:
            self._reader.close()
        w_końcu:
            close = self._close
            jeżeli close:
                self._close = Nic
                close()

    def join_thread(self):
        debug('Queue.join_thread()')
        assert self._closed
        jeżeli self._jointhread:
            self._jointhread()

    def cancel_join_thread(self):
        debug('Queue.cancel_join_thread()')
        self._joincancelled = Prawda
        spróbuj:
            self._jointhread.cancel()
        wyjąwszy AttributeError:
            dalej

    def _start_thread(self):
        debug('Queue._start_thread()')

        # Start thread which transfers data z buffer to pipe
        self._buffer.clear()
        self._thread = threading.Thread(
            target=Queue._feed,
            args=(self._buffer, self._notempty, self._send_bytes,
                  self._wlock, self._writer.close, self._ignore_epipe),
            name='QueueFeederThread'
            )
        self._thread.daemon = Prawda

        debug('doing self._thread.start()')
        self._thread.start()
        debug('... done self._thread.start()')

        # On process exit we will wait dla data to be flushed to pipe.
        #
        # However, jeżeli this process created the queue then all
        # processes which use the queue will be descendants of this
        # process.  Therefore waiting dla the queue to be flushed
        # jest pointless once all the child processes have been joined.
        created_by_this_process = (self._opid == os.getpid())
        jeżeli nie self._joincancelled oraz nie created_by_this_process:
            self._jointhread = Finalize(
                self._thread, Queue._finalize_join,
                [weakref.ref(self._thread)],
                exitpriority=-5
                )

        # Send sentinel to the thread queue object when garbage collected
        self._close = Finalize(
            self, Queue._finalize_close,
            [self._buffer, self._notempty],
            exitpriority=10
            )

    @staticmethod
    def _finalize_join(twr):
        debug('joining queue thread')
        thread = twr()
        jeżeli thread jest nie Nic:
            thread.join()
            debug('... queue thread joined')
        inaczej:
            debug('... queue thread already dead')

    @staticmethod
    def _finalize_close(buffer, notempty):
        debug('telling queue thread to quit')
        przy notempty:
            buffer.append(_sentinel)
            notempty.notify()

    @staticmethod
    def _feed(buffer, notempty, send_bytes, writelock, close, ignore_epipe):
        debug('starting thread to feed data to pipe')
        nacquire = notempty.acquire
        nrelease = notempty.release
        nwait = notempty.wait
        bpopleft = buffer.popleft
        sentinel = _sentinel
        jeżeli sys.platform != 'win32':
            wacquire = writelock.acquire
            wrelease = writelock.release
        inaczej:
            wacquire = Nic

        spróbuj:
            dopóki 1:
                nacquire()
                spróbuj:
                    jeżeli nie buffer:
                        nwait()
                w_końcu:
                    nrelease()
                spróbuj:
                    dopóki 1:
                        obj = bpopleft()
                        jeżeli obj jest sentinel:
                            debug('feeder thread got sentinel -- exiting')
                            close()
                            zwróć

                        # serialize the data before acquiring the lock
                        obj = ForkingPickler.dumps(obj)
                        jeżeli wacquire jest Nic:
                            send_bytes(obj)
                        inaczej:
                            wacquire()
                            spróbuj:
                                send_bytes(obj)
                            w_końcu:
                                wrelease()
                wyjąwszy IndexError:
                    dalej
        wyjąwszy Exception jako e:
            jeżeli ignore_epipe oraz getattr(e, 'errno', 0) == errno.EPIPE:
                zwróć
            # Since this runs w a daemon thread the resources it uses
            # may be become unusable dopóki the process jest cleaning up.
            # We ignore errors which happen after the process has
            # started to cleanup.
            spróbuj:
                jeżeli is_exiting():
                    info('error w queue thread: %s', e)
                inaczej:
                    zaimportuj traceback
                    traceback.print_exc()
            wyjąwszy Exception:
                dalej

_sentinel = object()

#
# A queue type which also supports join() oraz task_done() methods
#
# Note that jeżeli you do nie call task_done() dla each finished task then
# eventually the counter's semaphore may overflow causing Bad Things
# to happen.
#

klasa JoinableQueue(Queue):

    def __init__(self, maxsize=0, *, ctx):
        Queue.__init__(self, maxsize, ctx=ctx)
        self._unfinished_tasks = ctx.Semaphore(0)
        self._cond = ctx.Condition()

    def __getstate__(self):
        zwróć Queue.__getstate__(self) + (self._cond, self._unfinished_tasks)

    def __setstate__(self, state):
        Queue.__setstate__(self, state[:-2])
        self._cond, self._unfinished_tasks = state[-2:]

    def put(self, obj, block=Prawda, timeout=Nic):
        assert nie self._closed
        jeżeli nie self._sem.acquire(block, timeout):
            podnieś Full

        przy self._notempty, self._cond:
            jeżeli self._thread jest Nic:
                self._start_thread()
            self._buffer.append(obj)
            self._unfinished_tasks.release()
            self._notempty.notify()

    def task_done(self):
        przy self._cond:
            jeżeli nie self._unfinished_tasks.acquire(Nieprawda):
                podnieś ValueError('task_done() called too many times')
            jeżeli self._unfinished_tasks._semlock._is_zero():
                self._cond.notify_all()

    def join(self):
        przy self._cond:
            jeżeli nie self._unfinished_tasks._semlock._is_zero():
                self._cond.wait()

#
# Simplified Queue type -- really just a locked pipe
#

klasa SimpleQueue(object):

    def __init__(self, *, ctx):
        self._reader, self._writer = connection.Pipe(duplex=Nieprawda)
        self._rlock = ctx.Lock()
        self._poll = self._reader.poll
        jeżeli sys.platform == 'win32':
            self._wlock = Nic
        inaczej:
            self._wlock = ctx.Lock()

    def empty(self):
        zwróć nie self._poll()

    def __getstate__(self):
        context.assert_spawning(self)
        zwróć (self._reader, self._writer, self._rlock, self._wlock)

    def __setstate__(self, state):
        (self._reader, self._writer, self._rlock, self._wlock) = state

    def get(self):
        przy self._rlock:
            res = self._reader.recv_bytes()
        # unserialize the data after having released the lock
        zwróć ForkingPickler.loads(res)

    def put(self, obj):
        # serialize the data before acquiring the lock
        obj = ForkingPickler.dumps(obj)
        jeżeli self._wlock jest Nic:
            # writes to a message oriented win32 pipe are atomic
            self._writer.send_bytes(obj)
        inaczej:
            przy self._wlock:
                self._writer.send_bytes(obj)
