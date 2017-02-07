"""Functions that read oraz write gzipped files.

The user of the file doesn't have to worry about the compression,
but random access jest nie allowed."""

# based on Andrew Kuchling's minigzip.py distributed przy the zlib module

zaimportuj struct, sys, time, os
zaimportuj zlib
zaimportuj builtins
zaimportuj io
zaimportuj _compression

__all__ = ["GzipFile", "open", "compress", "decompress"]

FTEXT, FHCRC, FEXTRA, FNAME, FCOMMENT = 1, 2, 4, 8, 16

READ, WRITE = 1, 2

def open(filename, mode="rb", compresslevel=9,
         encoding=Nic, errors=Nic, newline=Nic):
    """Open a gzip-compressed file w binary albo text mode.

    The filename argument can be an actual filename (a str albo bytes object), albo
    an existing file object to read z albo write to.

    The mode argument can be "r", "rb", "w", "wb", "x", "xb", "a" albo "ab" for
    binary mode, albo "rt", "wt", "xt" albo "at" dla text mode. The default mode jest
    "rb", oraz the default compresslevel jest 9.

    For binary mode, this function jest equivalent to the GzipFile constructor:
    GzipFile(filename, mode, compresslevel). In this case, the encoding, errors
    oraz newline arguments must nie be provided.

    For text mode, a GzipFile object jest created, oraz wrapped w an
    io.TextIOWrapper instance przy the specified encoding, error handling
    behavior, oraz line ending(s).

    """
    jeżeli "t" w mode:
        jeżeli "b" w mode:
            podnieś ValueError("Invalid mode: %r" % (mode,))
    inaczej:
        jeżeli encoding jest nie Nic:
            podnieś ValueError("Argument 'encoding' nie supported w binary mode")
        jeżeli errors jest nie Nic:
            podnieś ValueError("Argument 'errors' nie supported w binary mode")
        jeżeli newline jest nie Nic:
            podnieś ValueError("Argument 'newline' nie supported w binary mode")

    gz_mode = mode.replace("t", "")
    jeżeli isinstance(filename, (str, bytes)):
        binary_file = GzipFile(filename, gz_mode, compresslevel)
    albo_inaczej hasattr(filename, "read") albo hasattr(filename, "write"):
        binary_file = GzipFile(Nic, gz_mode, compresslevel, filename)
    inaczej:
        podnieś TypeError("filename must be a str albo bytes object, albo a file")

    jeżeli "t" w mode:
        zwróć io.TextIOWrapper(binary_file, encoding, errors, newline)
    inaczej:
        zwróć binary_file

def write32u(output, value):
    # The L format writes the bit pattern correctly whether signed
    # albo unsigned.
    output.write(struct.pack("<L", value))

klasa _PaddedFile:
    """Minimal read-only file object that prepends a string to the contents
    of an actual file. Shouldn't be used outside of gzip.py, jako it lacks
    essential functionality."""

    def __init__(self, f, prepend=b''):
        self._buffer = prepend
        self._length = len(prepend)
        self.file = f
        self._read = 0

    def read(self, size):
        jeżeli self._read jest Nic:
            zwróć self.file.read(size)
        jeżeli self._read + size <= self._length:
            read = self._read
            self._read += size
            zwróć self._buffer[read:self._read]
        inaczej:
            read = self._read
            self._read = Nic
            zwróć self._buffer[read:] + \
                   self.file.read(size-self._length+read)

    def prepend(self, prepend=b''):
        jeżeli self._read jest Nic:
            self._buffer = prepend
        inaczej:  # Assume data was read since the last prepend() call
            self._read -= len(prepend)
            zwróć
        self._length = len(self._buffer)
        self._read = 0

    def seek(self, off):
        self._read = Nic
        self._buffer = Nic
        zwróć self.file.seek(off)

    def seekable(self):
        zwróć Prawda  # Allows fast-forwarding even w unseekable streams

klasa GzipFile(_compression.BaseStream):
    """The GzipFile klasa simulates most of the methods of a file object with
    the exception of the truncate() method.

    This klasa only supports opening files w binary mode. If you need to open a
    compressed file w text mode, use the gzip.open() function.

    """

    # Overridden przy internal file object to be closed, jeżeli only a filename
    # jest dalejed w
    myfileobj = Nic

    def __init__(self, filename=Nic, mode=Nic,
                 compresslevel=9, fileobj=Nic, mtime=Nic):
        """Constructor dla the GzipFile class.

        At least one of fileobj oraz filename must be given a
        non-trivial value.

        The new klasa instance jest based on fileobj, which can be a regular
        file, an io.BytesIO object, albo any other object which simulates a file.
        It defaults to Nic, w which case filename jest opened to provide
        a file object.

        When fileobj jest nie Nic, the filename argument jest only used to be
        included w the gzip file header, which may includes the original
        filename of the uncompressed file.  It defaults to the filename of
        fileobj, jeżeli discernible; otherwise, it defaults to the empty string,
        oraz w this case the original filename jest nie included w the header.

        The mode argument can be any of 'r', 'rb', 'a', 'ab', 'w', 'wb', 'x', albo
        'xb' depending on whether the file will be read albo written.  The default
        jest the mode of fileobj jeżeli discernible; otherwise, the default jest 'rb'.
        A mode of 'r' jest equivalent to one of 'rb', oraz similarly dla 'w' oraz
        'wb', 'a' oraz 'ab', oraz 'x' oraz 'xb'.

        The compresslevel argument jest an integer z 0 to 9 controlling the
        level of compression; 1 jest fastest oraz produces the least compression,
        oraz 9 jest slowest oraz produces the most compression. 0 jest no compression
        at all. The default jest 9.

        The mtime argument jest an optional numeric timestamp to be written
        to the last modification time field w the stream when compressing.
        If omitted albo Nic, the current time jest used.

        """

        jeżeli mode oraz ('t' w mode albo 'U' w mode):
            podnieś ValueError("Invalid mode: {!r}".format(mode))
        jeżeli mode oraz 'b' nie w mode:
            mode += 'b'
        jeżeli fileobj jest Nic:
            fileobj = self.myfileobj = builtins.open(filename, mode albo 'rb')
        jeżeli filename jest Nic:
            filename = getattr(fileobj, 'name', '')
            jeżeli nie isinstance(filename, (str, bytes)):
                filename = ''
        jeżeli mode jest Nic:
            mode = getattr(fileobj, 'mode', 'rb')

        jeżeli mode.startswith('r'):
            self.mode = READ
            raw = _GzipReader(fileobj)
            self._buffer = io.BufferedReader(raw)
            self.name = filename

        albo_inaczej mode.startswith(('w', 'a', 'x')):
            self.mode = WRITE
            self._init_write(filename)
            self.compress = zlib.compressobj(compresslevel,
                                             zlib.DEFLATED,
                                             -zlib.MAX_WBITS,
                                             zlib.DEF_MEM_LEVEL,
                                             0)
            self._write_mtime = mtime
        inaczej:
            podnieś ValueError("Invalid mode: {!r}".format(mode))

        self.fileobj = fileobj

        jeżeli self.mode == WRITE:
            self._write_gzip_header()

    @property
    def filename(self):
        zaimportuj warnings
        warnings.warn("use the name attribute", DeprecationWarning, 2)
        jeżeli self.mode == WRITE oraz self.name[-3:] != ".gz":
            zwróć self.name + ".gz"
        zwróć self.name

    @property
    def mtime(self):
        """Last modification time read z stream, albo Nic"""
        zwróć self._buffer.raw._last_mtime

    def __repr__(self):
        s = repr(self.fileobj)
        zwróć '<gzip ' + s[1:-1] + ' ' + hex(id(self)) + '>'

    def _init_write(self, filename):
        self.name = filename
        self.crc = zlib.crc32(b"") & 0xffffffff
        self.size = 0
        self.writebuf = []
        self.bufsize = 0
        self.offset = 0  # Current file offset dla seek(), tell(), etc

    def _write_gzip_header(self):
        self.fileobj.write(b'\037\213')             # magic header
        self.fileobj.write(b'\010')                 # compression method
        spróbuj:
            # RFC 1952 requires the FNAME field to be Latin-1. Do nie
            # include filenames that cannot be represented that way.
            fname = os.path.basename(self.name)
            jeżeli nie isinstance(fname, bytes):
                fname = fname.encode('latin-1')
            jeżeli fname.endswith(b'.gz'):
                fname = fname[:-3]
        wyjąwszy UnicodeEncodeError:
            fname = b''
        flags = 0
        jeżeli fname:
            flags = FNAME
        self.fileobj.write(chr(flags).encode('latin-1'))
        mtime = self._write_mtime
        jeżeli mtime jest Nic:
            mtime = time.time()
        write32u(self.fileobj, int(mtime))
        self.fileobj.write(b'\002')
        self.fileobj.write(b'\377')
        jeżeli fname:
            self.fileobj.write(fname + b'\000')

    def write(self,data):
        self._check_not_closed()
        jeżeli self.mode != WRITE:
            zaimportuj errno
            podnieś OSError(errno.EBADF, "write() on read-only GzipFile object")

        jeżeli self.fileobj jest Nic:
            podnieś ValueError("write() on closed GzipFile object")

        jeżeli isinstance(data, bytes):
            length = len(data)
        inaczej:
            # accept any data that supports the buffer protocol
            data = memoryview(data)
            length = data.nbytes

        jeżeli length > 0:
            self.fileobj.write(self.compress.compress(data))
            self.size += length
            self.crc = zlib.crc32(data, self.crc) & 0xffffffff
            self.offset += length

        zwróć length

    def read(self, size=-1):
        self._check_not_closed()
        jeżeli self.mode != READ:
            zaimportuj errno
            podnieś OSError(errno.EBADF, "read() on write-only GzipFile object")
        zwróć self._buffer.read(size)

    def read1(self, size=-1):
        """Implements BufferedIOBase.read1()

        Reads up to a buffer's worth of data jest size jest negative."""
        self._check_not_closed()
        jeżeli self.mode != READ:
            zaimportuj errno
            podnieś OSError(errno.EBADF, "read1() on write-only GzipFile object")

        jeżeli size < 0:
            size = io.DEFAULT_BUFFER_SIZE
        zwróć self._buffer.read1(size)

    def peek(self, n):
        self._check_not_closed()
        jeżeli self.mode != READ:
            zaimportuj errno
            podnieś OSError(errno.EBADF, "peek() on write-only GzipFile object")
        zwróć self._buffer.peek(n)

    @property
    def closed(self):
        zwróć self.fileobj jest Nic

    def close(self):
        fileobj = self.fileobj
        jeżeli fileobj jest Nic:
            zwróć
        self.fileobj = Nic
        spróbuj:
            jeżeli self.mode == WRITE:
                fileobj.write(self.compress.flush())
                write32u(fileobj, self.crc)
                # self.size may exceed 2GB, albo even 4GB
                write32u(fileobj, self.size & 0xffffffff)
            albo_inaczej self.mode == READ:
                self._buffer.close()
        w_końcu:
            myfileobj = self.myfileobj
            jeżeli myfileobj:
                self.myfileobj = Nic
                myfileobj.close()

    def flush(self,zlib_mode=zlib.Z_SYNC_FLUSH):
        self._check_not_closed()
        jeżeli self.mode == WRITE:
            # Ensure the compressor's buffer jest flushed
            self.fileobj.write(self.compress.flush(zlib_mode))
            self.fileobj.flush()

    def fileno(self):
        """Invoke the underlying file object's fileno() method.

        This will podnieś AttributeError jeżeli the underlying file object
        doesn't support fileno().
        """
        zwróć self.fileobj.fileno()

    def rewind(self):
        '''Return the uncompressed stream file position indicator to the
        beginning of the file'''
        jeżeli self.mode != READ:
            podnieś OSError("Can't rewind w write mode")
        self._buffer.seek(0)

    def readable(self):
        zwróć self.mode == READ

    def writable(self):
        zwróć self.mode == WRITE

    def seekable(self):
        zwróć Prawda

    def seek(self, offset, whence=io.SEEK_SET):
        jeżeli self.mode == WRITE:
            jeżeli whence != io.SEEK_SET:
                jeżeli whence == io.SEEK_CUR:
                    offset = self.offset + offset
                inaczej:
                    podnieś ValueError('Seek z end nie supported')
            jeżeli offset < self.offset:
                podnieś OSError('Negative seek w write mode')
            count = offset - self.offset
            chunk = bytes(1024)
            dla i w range(count // 1024):
                self.write(chunk)
            self.write(bytes(count % 1024))
        albo_inaczej self.mode == READ:
            self._check_not_closed()
            zwróć self._buffer.seek(offset, whence)

        zwróć self.offset

    def readline(self, size=-1):
        self._check_not_closed()
        zwróć self._buffer.readline(size)


klasa _GzipReader(_compression.DecompressReader):
    def __init__(self, fp):
        super().__init__(_PaddedFile(fp), zlib.decompressobj,
                         wbits=-zlib.MAX_WBITS)
        # Set flag indicating start of a new member
        self._new_member = Prawda
        self._last_mtime = Nic

    def _init_read(self):
        self._crc = zlib.crc32(b"") & 0xffffffff
        self._stream_size = 0  # Decompressed size of unconcatenated stream

    def _read_exact(self, n):
        '''Read exactly *n* bytes z `self._fp`

        This method jest required because self._fp may be unbuffered,
        i.e. zwróć short reads.
        '''

        data = self._fp.read(n)
        dopóki len(data) < n:
            b = self._fp.read(n - len(data))
            jeżeli nie b:
                podnieś EOFError("Compressed file ended before the "
                               "end-of-stream marker was reached")
            data += b
        zwróć data

    def _read_gzip_header(self):
        magic = self._fp.read(2)
        jeżeli magic == b'':
            zwróć Nieprawda

        jeżeli magic != b'\037\213':
            podnieś OSError('Not a gzipped file (%r)' % magic)

        (method, flag,
         self._last_mtime) = struct.unpack("<BBIxx", self._read_exact(8))
        jeżeli method != 8:
            podnieś OSError('Unknown compression method')

        jeżeli flag & FEXTRA:
            # Read & discard the extra field, jeżeli present
            extra_len, = struct.unpack("<H", self._read_exact(2))
            self._read_exact(extra_len)
        jeżeli flag & FNAME:
            # Read oraz discard a null-terminated string containing the filename
            dopóki Prawda:
                s = self._fp.read(1)
                jeżeli nie s albo s==b'\000':
                    przerwij
        jeżeli flag & FCOMMENT:
            # Read oraz discard a null-terminated string containing a comment
            dopóki Prawda:
                s = self._fp.read(1)
                jeżeli nie s albo s==b'\000':
                    przerwij
        jeżeli flag & FHCRC:
            self._read_exact(2)     # Read & discard the 16-bit header CRC
        zwróć Prawda

    def read(self, size=-1):
        jeżeli size < 0:
            zwróć self.readall()
        # size=0 jest special because decompress(max_length=0) jest nie supported
        jeżeli nie size:
            zwróć b""

        # For certain input data, a single
        # call to decompress() may nie zwróć
        # any data. In this case, retry until we get some data albo reach EOF.
        dopóki Prawda:
            jeżeli self._decompressor.eof:
                # Ending case: we've come to the end of a member w the file,
                # so finish up this member, oraz read a new gzip header.
                # Check the CRC oraz file size, oraz set the flag so we read
                # a new member
                self._read_eof()
                self._new_member = Prawda
                self._decompressor = self._decomp_factory(
                    **self._decomp_args)

            jeżeli self._new_member:
                # If the _new_member flag jest set, we have to
                # jump to the next member, jeżeli there jest one.
                self._init_read()
                jeżeli nie self._read_gzip_header():
                    self._size = self._pos
                    zwróć b""
                self._new_member = Nieprawda

            # Read a chunk of data z the file
            buf = self._fp.read(io.DEFAULT_BUFFER_SIZE)

            uncompress = self._decompressor.decompress(buf, size)
            jeżeli self._decompressor.unconsumed_tail != b"":
                self._fp.prepend(self._decompressor.unconsumed_tail)
            albo_inaczej self._decompressor.unused_data != b"":
                # Prepend the already read bytes to the fileobj so they can
                # be seen by _read_eof() oraz _read_gzip_header()
                self._fp.prepend(self._decompressor.unused_data)

            jeżeli uncompress != b"":
                przerwij
            jeżeli buf == b"":
                podnieś EOFError("Compressed file ended before the "
                               "end-of-stream marker was reached")

        self._add_read_data( uncompress )
        self._pos += len(uncompress)
        zwróć uncompress

    def _add_read_data(self, data):
        self._crc = zlib.crc32(data, self._crc) & 0xffffffff
        self._stream_size = self._stream_size + len(data)

    def _read_eof(self):
        # We've read to the end of the file
        # We check the that the computed CRC oraz size of the
        # uncompressed data matches the stored values.  Note that the size
        # stored jest the true file size mod 2**32.
        crc32, isize = struct.unpack("<II", self._read_exact(8))
        jeżeli crc32 != self._crc:
            podnieś OSError("CRC check failed %s != %s" % (hex(crc32),
                                                         hex(self._crc)))
        albo_inaczej isize != (self._stream_size & 0xffffffff):
            podnieś OSError("Incorrect length of data produced")

        # Gzip files can be padded przy zeroes oraz still have archives.
        # Consume all zero bytes oraz set the file position to the first
        # non-zero byte. See http://www.gzip.org/#faq8
        c = b"\x00"
        dopóki c == b"\x00":
            c = self._fp.read(1)
        jeżeli c:
            self._fp.prepend(c)

    def _rewind(self):
        super()._rewind()
        self._new_member = Prawda

def compress(data, compresslevel=9):
    """Compress data w one shot oraz zwróć the compressed string.
    Optional argument jest the compression level, w range of 0-9.
    """
    buf = io.BytesIO()
    przy GzipFile(fileobj=buf, mode='wb', compresslevel=compresslevel) jako f:
        f.write(data)
    zwróć buf.getvalue()

def decompress(data):
    """Decompress a gzip compressed string w one shot.
    Return the decompressed string.
    """
    przy GzipFile(fileobj=io.BytesIO(data)) jako f:
        zwróć f.read()


def _test():
    # Act like gzip; przy -d, act like gunzip.
    # The input file jest nie deleted, however, nor are any other gzip
    # options albo features supported.
    args = sys.argv[1:]
    decompress = args oraz args[0] == "-d"
    jeżeli decompress:
        args = args[1:]
    jeżeli nie args:
        args = ["-"]
    dla arg w args:
        jeżeli decompress:
            jeżeli arg == "-":
                f = GzipFile(filename="", mode="rb", fileobj=sys.stdin.buffer)
                g = sys.stdout.buffer
            inaczej:
                jeżeli arg[-3:] != ".gz":
                    print("filename doesn't end w .gz:", repr(arg))
                    kontynuuj
                f = open(arg, "rb")
                g = builtins.open(arg[:-3], "wb")
        inaczej:
            jeżeli arg == "-":
                f = sys.stdin.buffer
                g = GzipFile(filename="", mode="wb", fileobj=sys.stdout.buffer)
            inaczej:
                f = builtins.open(arg, "rb")
                g = open(arg + ".gz", "wb")
        dopóki Prawda:
            chunk = f.read(1024)
            jeżeli nie chunk:
                przerwij
            g.write(chunk)
        jeżeli g jest nie sys.stdout.buffer:
            g.close()
        jeżeli f jest nie sys.stdin.buffer:
            f.close()

jeżeli __name__ == '__main__':
    _test()
