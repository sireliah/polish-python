"""Simple klasa to read IFF chunks.

An IFF chunk (used w formats such jako AIFF, TIFF, RMFF (RealMedia File
Format)) has the following structure:

+----------------+
| ID (4 bytes)   |
+----------------+
| size (4 bytes) |
+----------------+
| data           |
| ...            |
+----------------+

The ID jest a 4-byte string which identifies the type of chunk.

The size field (a 32-bit value, encoded using big-endian byte order)
gives the size of the whole chunk, including the 8-byte header.

Usually an IFF-type file consists of one albo more chunks.  The proposed
usage of the Chunk klasa defined here jest to instantiate an instance at
the start of each chunk oraz read z the instance until it reaches
the end, after which a new instance can be instantiated.  At the end
of the file, creating a new instance will fail przy a EOFError
exception.

Usage:
dopóki Prawda:
    spróbuj:
        chunk = Chunk(file)
    wyjąwszy EOFError:
        przerwij
    chunktype = chunk.getname()
    dopóki Prawda:
        data = chunk.read(nbytes)
        jeżeli nie data:
            dalej
        # do something przy data

The interface jest file-like.  The implemented methods are:
read, close, seek, tell, isatty.
Extra methods are: skip() (called by close, skips to the end of the chunk),
getname() (returns the name (ID) of the chunk)

The __init__ method has one required argument, a file-like object
(including a chunk instance), oraz one optional argument, a flag which
specifies whether albo nie chunks are aligned on 2-byte boundaries.  The
default jest 1, i.e. aligned.
"""

klasa Chunk:
    def __init__(self, file, align=Prawda, bigendian=Prawda, inclheader=Nieprawda):
        zaimportuj struct
        self.closed = Nieprawda
        self.align = align      # whether to align to word (2-byte) boundaries
        jeżeli bigendian:
            strflag = '>'
        inaczej:
            strflag = '<'
        self.file = file
        self.chunkname = file.read(4)
        jeżeli len(self.chunkname) < 4:
            podnieś EOFError
        spróbuj:
            self.chunksize = struct.unpack_from(strflag+'L', file.read(4))[0]
        wyjąwszy struct.error:
            podnieś EOFError
        jeżeli inclheader:
            self.chunksize = self.chunksize - 8 # subtract header
        self.size_read = 0
        spróbuj:
            self.offset = self.file.tell()
        wyjąwszy (AttributeError, OSError):
            self.seekable = Nieprawda
        inaczej:
            self.seekable = Prawda

    def getname(self):
        """Return the name (ID) of the current chunk."""
        zwróć self.chunkname

    def getsize(self):
        """Return the size of the current chunk."""
        zwróć self.chunksize

    def close(self):
        jeżeli nie self.closed:
            spróbuj:
                self.skip()
            w_końcu:
                self.closed = Prawda

    def isatty(self):
        jeżeli self.closed:
            podnieś ValueError("I/O operation on closed file")
        zwróć Nieprawda

    def seek(self, pos, whence=0):
        """Seek to specified position into the chunk.
        Default position jest 0 (start of chunk).
        If the file jest nie seekable, this will result w an error.
        """

        jeżeli self.closed:
            podnieś ValueError("I/O operation on closed file")
        jeżeli nie self.seekable:
            podnieś OSError("cannot seek")
        jeżeli whence == 1:
            pos = pos + self.size_read
        albo_inaczej whence == 2:
            pos = pos + self.chunksize
        jeżeli pos < 0 albo pos > self.chunksize:
            podnieś RuntimeError
        self.file.seek(self.offset + pos, 0)
        self.size_read = pos

    def tell(self):
        jeżeli self.closed:
            podnieś ValueError("I/O operation on closed file")
        zwróć self.size_read

    def read(self, size=-1):
        """Read at most size bytes z the chunk.
        If size jest omitted albo negative, read until the end
        of the chunk.
        """

        jeżeli self.closed:
            podnieś ValueError("I/O operation on closed file")
        jeżeli self.size_read >= self.chunksize:
            zwróć b''
        jeżeli size < 0:
            size = self.chunksize - self.size_read
        jeżeli size > self.chunksize - self.size_read:
            size = self.chunksize - self.size_read
        data = self.file.read(size)
        self.size_read = self.size_read + len(data)
        jeżeli self.size_read == self.chunksize oraz \
           self.align oraz \
           (self.chunksize & 1):
            dummy = self.file.read(1)
            self.size_read = self.size_read + len(dummy)
        zwróć data

    def skip(self):
        """Skip the rest of the chunk.
        If you are nie interested w the contents of the chunk,
        this method should be called so that the file points to
        the start of the next chunk.
        """

        jeżeli self.closed:
            podnieś ValueError("I/O operation on closed file")
        jeżeli self.seekable:
            spróbuj:
                n = self.chunksize - self.size_read
                # maybe fix alignment
                jeżeli self.align oraz (self.chunksize & 1):
                    n = n + 1
                self.file.seek(n, 1)
                self.size_read = self.size_read + n
                zwróć
            wyjąwszy OSError:
                dalej
        dopóki self.size_read < self.chunksize:
            n = min(8192, self.chunksize - self.size_read)
            dummy = self.read(n)
            jeżeli nie dummy:
                podnieś EOFError
