#
# Module which supports allocation of memory z an mmap
#
# multiprocessing/heap.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

zaimportuj bisect
zaimportuj mmap
zaimportuj os
zaimportuj sys
zaimportuj tempfile
zaimportuj threading

z . zaimportuj context
z . zaimportuj reduction
z . zaimportuj util

__all__ = ['BufferWrapper']

#
# Inheritable klasa which wraps an mmap, oraz z which blocks can be allocated
#

jeżeli sys.platform == 'win32':

    zaimportuj _winapi

    klasa Arena(object):

        _rand = tempfile._RandomNameSequence()

        def __init__(self, size):
            self.size = size
            dla i w range(100):
                name = 'pym-%d-%s' % (os.getpid(), next(self._rand))
                buf = mmap.mmap(-1, size, tagname=name)
                jeżeli _winapi.GetLastError() == 0:
                    przerwij
                # We have reopened a preexisting mmap.
                buf.close()
            inaczej:
                podnieś FileExistsError('Cannot find name dla new mmap')
            self.name = name
            self.buffer = buf
            self._state = (self.size, self.name)

        def __getstate__(self):
            context.assert_spawning(self)
            zwróć self._state

        def __setstate__(self, state):
            self.size, self.name = self._state = state
            self.buffer = mmap.mmap(-1, self.size, tagname=self.name)
            # XXX Temporarily preventing buildbot failures dopóki determining
            # XXX the correct long-term fix. See issue 23060
            #assert _winapi.GetLastError() == _winapi.ERROR_ALREADY_EXISTS

inaczej:

    klasa Arena(object):

        def __init__(self, size, fd=-1):
            self.size = size
            self.fd = fd
            jeżeli fd == -1:
                self.fd, name = tempfile.mkstemp(
                     prefix='pym-%d-'%os.getpid(), dir=util.get_temp_dir())
                os.unlink(name)
                util.Finalize(self, os.close, (self.fd,))
                przy open(self.fd, 'wb', closefd=Nieprawda) jako f:
                    bs = 1024 * 1024
                    jeżeli size >= bs:
                        zeros = b'\0' * bs
                        dla _ w range(size // bs):
                            f.write(zeros)
                        usuń zeros
                    f.write(b'\0' * (size % bs))
                    assert f.tell() == size
            self.buffer = mmap.mmap(self.fd, self.size)

    def reduce_arena(a):
        jeżeli a.fd == -1:
            podnieś ValueError('Arena jest unpicklable because '
                             'forking was enabled when it was created')
        zwróć rebuild_arena, (a.size, reduction.DupFd(a.fd))

    def rebuild_arena(size, dupfd):
        zwróć Arena(size, dupfd.detach())

    reduction.register(Arena, reduce_arena)

#
# Class allowing allocation of chunks of memory z arenas
#

klasa Heap(object):

    _alignment = 8

    def __init__(self, size=mmap.PAGESIZE):
        self._lastpid = os.getpid()
        self._lock = threading.Lock()
        self._size = size
        self._lengths = []
        self._len_to_seq = {}
        self._start_to_block = {}
        self._stop_to_block = {}
        self._allocated_blocks = set()
        self._arenas = []
        # list of pending blocks to free - see free() comment below
        self._pending_free_blocks = []

    @staticmethod
    def _roundup(n, alignment):
        # alignment must be a power of 2
        mask = alignment - 1
        zwróć (n + mask) & ~mask

    def _malloc(self, size):
        # returns a large enough block -- it might be much larger
        i = bisect.bisect_left(self._lengths, size)
        jeżeli i == len(self._lengths):
            length = self._roundup(max(self._size, size), mmap.PAGESIZE)
            self._size *= 2
            util.info('allocating a new mmap of length %d', length)
            arena = Arena(length)
            self._arenas.append(arena)
            zwróć (arena, 0, length)
        inaczej:
            length = self._lengths[i]
            seq = self._len_to_seq[length]
            block = seq.pop()
            jeżeli nie seq:
                usuń self._len_to_seq[length], self._lengths[i]

        (arena, start, stop) = block
        usuń self._start_to_block[(arena, start)]
        usuń self._stop_to_block[(arena, stop)]
        zwróć block

    def _free(self, block):
        # free location oraz try to merge przy neighbours
        (arena, start, stop) = block

        spróbuj:
            prev_block = self._stop_to_block[(arena, start)]
        wyjąwszy KeyError:
            dalej
        inaczej:
            start, _ = self._absorb(prev_block)

        spróbuj:
            next_block = self._start_to_block[(arena, stop)]
        wyjąwszy KeyError:
            dalej
        inaczej:
            _, stop = self._absorb(next_block)

        block = (arena, start, stop)
        length = stop - start

        spróbuj:
            self._len_to_seq[length].append(block)
        wyjąwszy KeyError:
            self._len_to_seq[length] = [block]
            bisect.insort(self._lengths, length)

        self._start_to_block[(arena, start)] = block
        self._stop_to_block[(arena, stop)] = block

    def _absorb(self, block):
        # deregister this block so it can be merged przy a neighbour
        (arena, start, stop) = block
        usuń self._start_to_block[(arena, start)]
        usuń self._stop_to_block[(arena, stop)]

        length = stop - start
        seq = self._len_to_seq[length]
        seq.remove(block)
        jeżeli nie seq:
            usuń self._len_to_seq[length]
            self._lengths.remove(length)

        zwróć start, stop

    def _free_pending_blocks(self):
        # Free all the blocks w the pending list - called przy the lock held.
        dopóki Prawda:
            spróbuj:
                block = self._pending_free_blocks.pop()
            wyjąwszy IndexError:
                przerwij
            self._allocated_blocks.remove(block)
            self._free(block)

    def free(self, block):
        # free a block returned by malloc()
        # Since free() can be called asynchronously by the GC, it could happen
        # that it's called dopóki self._lock jest held: w that case,
        # self._lock.acquire() would deadlock (issue #12352). To avoid that, a
        # trylock jest used instead, oraz jeżeli the lock can't be acquired
        # immediately, the block jest added to a list of blocks to be freed
        # synchronously sometimes later z malloc() albo free(), by calling
        # _free_pending_blocks() (appending oraz retrieving z a list jest nie
        # strictly thread-safe but under cPython it's atomic thanks to the GIL).
        assert os.getpid() == self._lastpid
        jeżeli nie self._lock.acquire(Nieprawda):
            # can't acquire the lock right now, add the block to the list of
            # pending blocks to free
            self._pending_free_blocks.append(block)
        inaczej:
            # we hold the lock
            spróbuj:
                self._free_pending_blocks()
                self._allocated_blocks.remove(block)
                self._free(block)
            w_końcu:
                self._lock.release()

    def malloc(self, size):
        # zwróć a block of right size (possibly rounded up)
        assert 0 <= size < sys.maxsize
        jeżeli os.getpid() != self._lastpid:
            self.__init__()                     # reinitialize after fork
        przy self._lock:
            self._free_pending_blocks()
            size = self._roundup(max(size,1), self._alignment)
            (arena, start, stop) = self._malloc(size)
            new_stop = start + size
            jeżeli new_stop < stop:
                self._free((arena, new_stop, stop))
            block = (arena, start, new_stop)
            self._allocated_blocks.add(block)
            zwróć block

#
# Class representing a chunk of an mmap -- can be inherited by child process
#

klasa BufferWrapper(object):

    _heap = Heap()

    def __init__(self, size):
        assert 0 <= size < sys.maxsize
        block = BufferWrapper._heap.malloc(size)
        self._state = (block, size)
        util.Finalize(self, BufferWrapper._heap.free, args=(block,))

    def create_memoryview(self):
        (arena, start, stop), size = self._state
        zwróć memoryview(arena.buffer)[start:start+size]
