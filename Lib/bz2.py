"""Interface to the libbzip2 compression library.

This module provides a file interface, classes dla incremental
(de)compression, oraz functions dla one-shot (de)compression.
"""

__all__ = ["BZ2File", "BZ2Compressor", "BZ2Decompressor",
           "open", "compress", "decompress"]

__author__ = "Nadeem Vawda <nadeem.vawda@gmail.com>"

z builtins zaimportuj open jako _builtin_open
zaimportuj io
zaimportuj warnings
zaimportuj _compression

spróbuj:
    z threading zaimportuj RLock
wyjąwszy ImportError:
    z dummy_threading zaimportuj RLock

z _bz2 zaimportuj BZ2Compressor, BZ2Decompressor


_MODE_CLOSED   = 0
_MODE_READ     = 1
# Value 2 no longer used
_MODE_WRITE    = 3


klasa BZ2File(_compression.BaseStream):

    """A file object providing transparent bzip2 (de)compression.

    A BZ2File can act jako a wrapper dla an existing file object, albo refer
    directly to a named file on disk.

    Note that BZ2File provides a *binary* file interface - data read jest
    returned jako bytes, oraz data to be written should be given jako bytes.
    """

    def __init__(self, filename, mode="r", buffering=Nic, compresslevel=9):
        """Open a bzip2-compressed file.

        If filename jest a str albo bytes object, it gives the name
        of the file to be opened. Otherwise, it should be a file object,
        which will be used to read albo write the compressed data.

        mode can be 'r' dla reading (default), 'w' dla (over)writing,
        'x' dla creating exclusively, albo 'a' dla appending. These can
        equivalently be given jako 'rb', 'wb', 'xb', oraz 'ab'.

        buffering jest ignored. Its use jest deprecated.

        If mode jest 'w', 'x' albo 'a', compresslevel can be a number between 1
        oraz 9 specifying the level of compression: 1 produces the least
        compression, oraz 9 (default) produces the most compression.

        If mode jest 'r', the input file may be the concatenation of
        multiple compressed streams.
        """
        # This lock must be recursive, so that BufferedIOBase's
        # writelines() does nie deadlock.
        self._lock = RLock()
        self._fp = Nic
        self._closefp = Nieprawda
        self._mode = _MODE_CLOSED

        jeżeli buffering jest nie Nic:
            warnings.warn("Use of 'buffering' argument jest deprecated",
                          DeprecationWarning)

        jeżeli nie (1 <= compresslevel <= 9):
            podnieś ValueError("compresslevel must be between 1 oraz 9")

        jeżeli mode w ("", "r", "rb"):
            mode = "rb"
            mode_code = _MODE_READ
        albo_inaczej mode w ("w", "wb"):
            mode = "wb"
            mode_code = _MODE_WRITE
            self._compressor = BZ2Compressor(compresslevel)
        albo_inaczej mode w ("x", "xb"):
            mode = "xb"
            mode_code = _MODE_WRITE
            self._compressor = BZ2Compressor(compresslevel)
        albo_inaczej mode w ("a", "ab"):
            mode = "ab"
            mode_code = _MODE_WRITE
            self._compressor = BZ2Compressor(compresslevel)
        inaczej:
            podnieś ValueError("Invalid mode: %r" % (mode,))

        jeżeli isinstance(filename, (str, bytes)):
            self._fp = _builtin_open(filename, mode)
            self._closefp = Prawda
            self._mode = mode_code
        albo_inaczej hasattr(filename, "read") albo hasattr(filename, "write"):
            self._fp = filename
            self._mode = mode_code
        inaczej:
            podnieś TypeError("filename must be a str albo bytes object, albo a file")

        jeżeli self._mode == _MODE_READ:
            raw = _compression.DecompressReader(self._fp,
                BZ2Decompressor, trailing_error=OSError)
            self._buffer = io.BufferedReader(raw)
        inaczej:
            self._pos = 0

    def close(self):
        """Flush oraz close the file.

        May be called more than once without error. Once the file jest
        closed, any other operation on it will podnieś a ValueError.
        """
        przy self._lock:
            jeżeli self._mode == _MODE_CLOSED:
                zwróć
            spróbuj:
                jeżeli self._mode == _MODE_READ:
                    self._buffer.close()
                albo_inaczej self._mode == _MODE_WRITE:
                    self._fp.write(self._compressor.flush())
                    self._compressor = Nic
            w_końcu:
                spróbuj:
                    jeżeli self._closefp:
                        self._fp.close()
                w_końcu:
                    self._fp = Nic
                    self._closefp = Nieprawda
                    self._mode = _MODE_CLOSED
                    self._buffer = Nic

    @property
    def closed(self):
        """Prawda jeżeli this file jest closed."""
        zwróć self._mode == _MODE_CLOSED

    def fileno(self):
        """Return the file descriptor dla the underlying file."""
        self._check_not_closed()
        zwróć self._fp.fileno()

    def seekable(self):
        """Return whether the file supports seeking."""
        zwróć self.readable() oraz self._buffer.seekable()

    def readable(self):
        """Return whether the file was opened dla reading."""
        self._check_not_closed()
        zwróć self._mode == _MODE_READ

    def writable(self):
        """Return whether the file was opened dla writing."""
        self._check_not_closed()
        zwróć self._mode == _MODE_WRITE

    def peek(self, n=0):
        """Return buffered data without advancing the file position.

        Always returns at least one byte of data, unless at EOF.
        The exact number of bytes returned jest unspecified.
        """
        przy self._lock:
            self._check_can_read()
            # Relies on the undocumented fact that BufferedReader.peek()
            # always returns at least one byte (wyjąwszy at EOF), independent
            # of the value of n
            zwróć self._buffer.peek(n)

    def read(self, size=-1):
        """Read up to size uncompressed bytes z the file.

        If size jest negative albo omitted, read until EOF jest reached.
        Returns b'' jeżeli the file jest already at EOF.
        """
        przy self._lock:
            self._check_can_read()
            zwróć self._buffer.read(size)

    def read1(self, size=-1):
        """Read up to size uncompressed bytes, dopóki trying to avoid
        making multiple reads z the underlying stream. Reads up to a
        buffer's worth of data jeżeli size jest negative.

        Returns b'' jeżeli the file jest at EOF.
        """
        przy self._lock:
            self._check_can_read()
            jeżeli size < 0:
                size = io.DEFAULT_BUFFER_SIZE
            zwróć self._buffer.read1(size)

    def readinto(self, b):
        """Read bytes into b.

        Returns the number of bytes read (0 dla EOF).
        """
        przy self._lock:
            self._check_can_read()
            zwróć self._buffer.readinto(b)

    def readline(self, size=-1):
        """Read a line of uncompressed bytes z the file.

        The terminating newline (jeżeli present) jest retained. If size jest
        non-negative, no more than size bytes will be read (in which
        case the line may be incomplete). Returns b'' jeżeli already at EOF.
        """
        jeżeli nie isinstance(size, int):
            jeżeli nie hasattr(size, "__index__"):
                podnieś TypeError("Integer argument expected")
            size = size.__index__()
        przy self._lock:
            self._check_can_read()
            zwróć self._buffer.readline(size)

    def readlines(self, size=-1):
        """Read a list of lines of uncompressed bytes z the file.

        size can be specified to control the number of lines read: no
        further lines will be read once the total size of the lines read
        so far equals albo exceeds size.
        """
        jeżeli nie isinstance(size, int):
            jeżeli nie hasattr(size, "__index__"):
                podnieś TypeError("Integer argument expected")
            size = size.__index__()
        przy self._lock:
            self._check_can_read()
            zwróć self._buffer.readlines(size)

    def write(self, data):
        """Write a byte string to the file.

        Returns the number of uncompressed bytes written, which jest
        always len(data). Note that due to buffering, the file on disk
        may nie reflect the data written until close() jest called.
        """
        przy self._lock:
            self._check_can_write()
            compressed = self._compressor.compress(data)
            self._fp.write(compressed)
            self._pos += len(data)
            zwróć len(data)

    def writelines(self, seq):
        """Write a sequence of byte strings to the file.

        Returns the number of uncompressed bytes written.
        seq can be any iterable uzyskajing byte strings.

        Line separators are nie added between the written byte strings.
        """
        przy self._lock:
            zwróć _compression.BaseStream.writelines(self, seq)

    def seek(self, offset, whence=io.SEEK_SET):
        """Change the file position.

        The new position jest specified by offset, relative to the
        position indicated by whence. Values dla whence are:

            0: start of stream (default); offset must nie be negative
            1: current stream position
            2: end of stream; offset must nie be positive

        Returns the new file position.

        Note that seeking jest emulated, so depending on the parameters,
        this operation may be extremely slow.
        """
        przy self._lock:
            self._check_can_seek()
            zwróć self._buffer.seek(offset, whence)

    def tell(self):
        """Return the current file position."""
        przy self._lock:
            self._check_not_closed()
            jeżeli self._mode == _MODE_READ:
                zwróć self._buffer.tell()
            zwróć self._pos


def open(filename, mode="rb", compresslevel=9,
         encoding=Nic, errors=Nic, newline=Nic):
    """Open a bzip2-compressed file w binary albo text mode.

    The filename argument can be an actual filename (a str albo bytes
    object), albo an existing file object to read z albo write to.

    The mode argument can be "r", "rb", "w", "wb", "x", "xb", "a" albo
    "ab" dla binary mode, albo "rt", "wt", "xt" albo "at" dla text mode.
    The default mode jest "rb", oraz the default compresslevel jest 9.

    For binary mode, this function jest equivalent to the BZ2File
    constructor: BZ2File(filename, mode, compresslevel). In this case,
    the encoding, errors oraz newline arguments must nie be provided.

    For text mode, a BZ2File object jest created, oraz wrapped w an
    io.TextIOWrapper instance przy the specified encoding, error
    handling behavior, oraz line ending(s).

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

    bz_mode = mode.replace("t", "")
    binary_file = BZ2File(filename, bz_mode, compresslevel=compresslevel)

    jeżeli "t" w mode:
        zwróć io.TextIOWrapper(binary_file, encoding, errors, newline)
    inaczej:
        zwróć binary_file


def compress(data, compresslevel=9):
    """Compress a block of data.

    compresslevel, jeżeli given, must be a number between 1 oraz 9.

    For incremental compression, use a BZ2Compressor object instead.
    """
    comp = BZ2Compressor(compresslevel)
    zwróć comp.compress(data) + comp.flush()


def decompress(data):
    """Decompress a block of data.

    For incremental decompression, use a BZ2Decompressor object instead.
    """
    results = []
    dopóki data:
        decomp = BZ2Decompressor()
        spróbuj:
            res = decomp.decompress(data)
        wyjąwszy OSError:
            jeżeli results:
                przerwij  # Leftover data jest nie a valid bzip2 stream; ignore it.
            inaczej:
                podnieś  # Error on the first iteration; bail out.
        results.append(res)
        jeżeli nie decomp.eof:
            podnieś ValueError("Compressed data ended before the "
                             "end-of-stream marker was reached")
        data = decomp.unused_data
    zwróć b"".join(results)
