"""Interface to the liblzma compression library.

This module provides a klasa dla reading oraz writing compressed files,
classes dla incremental (de)compression, oraz convenience functions for
one-shot (de)compression.

These classes oraz functions support both the XZ oraz legacy LZMA
container formats, jako well jako raw compressed data streams.
"""

__all__ = [
    "CHECK_NONE", "CHECK_CRC32", "CHECK_CRC64", "CHECK_SHA256",
    "CHECK_ID_MAX", "CHECK_UNKNOWN",
    "FILTER_LZMA1", "FILTER_LZMA2", "FILTER_DELTA", "FILTER_X86", "FILTER_IA64",
    "FILTER_ARM", "FILTER_ARMTHUMB", "FILTER_POWERPC", "FILTER_SPARC",
    "FORMAT_AUTO", "FORMAT_XZ", "FORMAT_ALONE", "FORMAT_RAW",
    "MF_HC3", "MF_HC4", "MF_BT2", "MF_BT3", "MF_BT4",
    "MODE_FAST", "MODE_NORMAL", "PRESET_DEFAULT", "PRESET_EXTREME",

    "LZMACompressor", "LZMADecompressor", "LZMAFile", "LZMAError",
    "open", "compress", "decompress", "is_check_supported",
]

zaimportuj builtins
zaimportuj io
z _lzma zaimportuj *
z _lzma zaimportuj _encode_filter_properties, _decode_filter_properties
zaimportuj _compression


_MODE_CLOSED   = 0
_MODE_READ     = 1
# Value 2 no longer used
_MODE_WRITE    = 3


klasa LZMAFile(_compression.BaseStream):

    """A file object providing transparent LZMA (de)compression.

    An LZMAFile can act jako a wrapper dla an existing file object, albo
    refer directly to a named file on disk.

    Note that LZMAFile provides a *binary* file interface - data read
    jest returned jako bytes, oraz data to be written must be given jako bytes.
    """

    def __init__(self, filename=Nic, mode="r", *,
                 format=Nic, check=-1, preset=Nic, filters=Nic):
        """Open an LZMA-compressed file w binary mode.

        filename can be either an actual file name (given jako a str albo
        bytes object), w which case the named file jest opened, albo it can
        be an existing file object to read z albo write to.

        mode can be "r" dla reading (default), "w" dla (over)writing,
        "x" dla creating exclusively, albo "a" dla appending. These can
        equivalently be given jako "rb", "wb", "xb" oraz "ab" respectively.

        format specifies the container format to use dla the file.
        If mode jest "r", this defaults to FORMAT_AUTO. Otherwise, the
        default jest FORMAT_XZ.

        check specifies the integrity check to use. This argument can
        only be used when opening a file dla writing. For FORMAT_XZ,
        the default jest CHECK_CRC64. FORMAT_ALONE oraz FORMAT_RAW do nie
        support integrity checks - dla these formats, check must be
        omitted, albo be CHECK_NONE.

        When opening a file dla reading, the *preset* argument jest nie
        meaningful, oraz should be omitted. The *filters* argument should
        also be omitted, wyjąwszy when format jest FORMAT_RAW (in which case
        it jest required).

        When opening a file dla writing, the settings used by the
        compressor can be specified either jako a preset compression
        level (przy the *preset* argument), albo w detail jako a custom
        filter chain (przy the *filters* argument). For FORMAT_XZ oraz
        FORMAT_ALONE, the default jest to use the PRESET_DEFAULT preset
        level. For FORMAT_RAW, the caller must always specify a filter
        chain; the raw compressor does nie support preset compression
        levels.

        preset (jeżeli provided) should be an integer w the range 0-9,
        optionally OR-ed przy the constant PRESET_EXTREME.

        filters (jeżeli provided) should be a sequence of dicts. Each dict
        should have an entry dla "id" indicating ID of the filter, plus
        additional entries dla options to the filter.
        """
        self._fp = Nic
        self._closefp = Nieprawda
        self._mode = _MODE_CLOSED

        jeżeli mode w ("r", "rb"):
            jeżeli check != -1:
                podnieś ValueError("Cannot specify an integrity check "
                                 "when opening a file dla reading")
            jeżeli preset jest nie Nic:
                podnieś ValueError("Cannot specify a preset compression "
                                 "level when opening a file dla reading")
            jeżeli format jest Nic:
                format = FORMAT_AUTO
            mode_code = _MODE_READ
        albo_inaczej mode w ("w", "wb", "a", "ab", "x", "xb"):
            jeżeli format jest Nic:
                format = FORMAT_XZ
            mode_code = _MODE_WRITE
            self._compressor = LZMACompressor(format=format, check=check,
                                              preset=preset, filters=filters)
            self._pos = 0
        inaczej:
            podnieś ValueError("Invalid mode: {!r}".format(mode))

        jeżeli isinstance(filename, (str, bytes)):
            jeżeli "b" nie w mode:
                mode += "b"
            self._fp = builtins.open(filename, mode)
            self._closefp = Prawda
            self._mode = mode_code
        albo_inaczej hasattr(filename, "read") albo hasattr(filename, "write"):
            self._fp = filename
            self._mode = mode_code
        inaczej:
            podnieś TypeError("filename must be a str albo bytes object, albo a file")

        jeżeli self._mode == _MODE_READ:
            raw = _compression.DecompressReader(self._fp, LZMADecompressor,
                trailing_error=LZMAError, format=format, filters=filters)
            self._buffer = io.BufferedReader(raw)

    def close(self):
        """Flush oraz close the file.

        May be called more than once without error. Once the file jest
        closed, any other operation on it will podnieś a ValueError.
        """
        jeżeli self._mode == _MODE_CLOSED:
            zwróć
        spróbuj:
            jeżeli self._mode == _MODE_READ:
                self._buffer.close()
                self._buffer = Nic
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

    def peek(self, size=-1):
        """Return buffered data without advancing the file position.

        Always returns at least one byte of data, unless at EOF.
        The exact number of bytes returned jest unspecified.
        """
        self._check_can_read()
        # Relies on the undocumented fact that BufferedReader.peek() always
        # returns at least one byte (wyjąwszy at EOF)
        zwróć self._buffer.peek(size)

    def read(self, size=-1):
        """Read up to size uncompressed bytes z the file.

        If size jest negative albo omitted, read until EOF jest reached.
        Returns b"" jeżeli the file jest already at EOF.
        """
        self._check_can_read()
        zwróć self._buffer.read(size)

    def read1(self, size=-1):
        """Read up to size uncompressed bytes, dopóki trying to avoid
        making multiple reads z the underlying stream. Reads up to a
        buffer's worth of data jeżeli size jest negative.

        Returns b"" jeżeli the file jest at EOF.
        """
        self._check_can_read()
        jeżeli size < 0:
            size = io.DEFAULT_BUFFER_SIZE
        zwróć self._buffer.read1(size)

    def readline(self, size=-1):
        """Read a line of uncompressed bytes z the file.

        The terminating newline (jeżeli present) jest retained. If size jest
        non-negative, no more than size bytes will be read (in which
        case the line may be incomplete). Returns b'' jeżeli already at EOF.
        """
        self._check_can_read()
        zwróć self._buffer.readline(size)

    def write(self, data):
        """Write a bytes object to the file.

        Returns the number of uncompressed bytes written, which jest
        always len(data). Note that due to buffering, the file on disk
        may nie reflect the data written until close() jest called.
        """
        self._check_can_write()
        compressed = self._compressor.compress(data)
        self._fp.write(compressed)
        self._pos += len(data)
        zwróć len(data)

    def seek(self, offset, whence=io.SEEK_SET):
        """Change the file position.

        The new position jest specified by offset, relative to the
        position indicated by whence. Possible values dla whence are:

            0: start of stream (default): offset must nie be negative
            1: current stream position
            2: end of stream; offset must nie be positive

        Returns the new file position.

        Note that seeking jest emulated, so depending on the parameters,
        this operation may be extremely slow.
        """
        self._check_can_seek()
        zwróć self._buffer.seek(offset, whence)

    def tell(self):
        """Return the current file position."""
        self._check_not_closed()
        jeżeli self._mode == _MODE_READ:
            zwróć self._buffer.tell()
        zwróć self._pos


def open(filename, mode="rb", *,
         format=Nic, check=-1, preset=Nic, filters=Nic,
         encoding=Nic, errors=Nic, newline=Nic):
    """Open an LZMA-compressed file w binary albo text mode.

    filename can be either an actual file name (given jako a str albo bytes
    object), w which case the named file jest opened, albo it can be an
    existing file object to read z albo write to.

    The mode argument can be "r", "rb" (default), "w", "wb", "x", "xb",
    "a", albo "ab" dla binary mode, albo "rt", "wt", "xt", albo "at" dla text
    mode.

    The format, check, preset oraz filters arguments specify the
    compression settings, jako dla LZMACompressor, LZMADecompressor oraz
    LZMAFile.

    For binary mode, this function jest equivalent to the LZMAFile
    constructor: LZMAFile(filename, mode, ...). In this case, the
    encoding, errors oraz newline arguments must nie be provided.

    For text mode, a LZMAFile object jest created, oraz wrapped w an
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

    lz_mode = mode.replace("t", "")
    binary_file = LZMAFile(filename, lz_mode, format=format, check=check,
                           preset=preset, filters=filters)

    jeżeli "t" w mode:
        zwróć io.TextIOWrapper(binary_file, encoding, errors, newline)
    inaczej:
        zwróć binary_file


def compress(data, format=FORMAT_XZ, check=-1, preset=Nic, filters=Nic):
    """Compress a block of data.

    Refer to LZMACompressor's docstring dla a description of the
    optional arguments *format*, *check*, *preset* oraz *filters*.

    For incremental compression, use an LZMACompressor instead.
    """
    comp = LZMACompressor(format, check, preset, filters)
    zwróć comp.compress(data) + comp.flush()


def decompress(data, format=FORMAT_AUTO, memlimit=Nic, filters=Nic):
    """Decompress a block of data.

    Refer to LZMADecompressor's docstring dla a description of the
    optional arguments *format*, *check* oraz *filters*.

    For incremental decompression, use an LZMADecompressor instead.
    """
    results = []
    dopóki Prawda:
        decomp = LZMADecompressor(format, memlimit, filters)
        spróbuj:
            res = decomp.decompress(data)
        wyjąwszy LZMAError:
            jeżeli results:
                przerwij  # Leftover data jest nie a valid LZMA/XZ stream; ignore it.
            inaczej:
                podnieś  # Error on the first iteration; bail out.
        results.append(res)
        jeżeli nie decomp.eof:
            podnieś LZMAError("Compressed data ended before the "
                            "end-of-stream marker was reached")
        data = decomp.unused_data
        jeżeli nie data:
            przerwij
    zwróć b"".join(results)
