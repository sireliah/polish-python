"""
Python implementation of the io module.
"""

zaimportuj os
zaimportuj abc
zaimportuj codecs
zaimportuj errno
zaimportuj array
zaimportuj stat
# Import _thread instead of threading to reduce startup cost
spróbuj:
    z _thread zaimportuj allocate_lock jako Lock
wyjąwszy ImportError:
    z _dummy_thread zaimportuj allocate_lock jako Lock
jeżeli os.name == 'win32':
    z msvcrt zaimportuj setmode jako _setmode
inaczej:
    _setmode = Nic

zaimportuj io
z io zaimportuj (__all__, SEEK_SET, SEEK_CUR, SEEK_END)

valid_seek_flags = {0, 1, 2}  # Hardwired values
jeżeli hasattr(os, 'SEEK_HOLE') :
    valid_seek_flags.add(os.SEEK_HOLE)
    valid_seek_flags.add(os.SEEK_DATA)

# open() uses st_blksize whenever we can
DEFAULT_BUFFER_SIZE = 8 * 1024  # bytes

# NOTE: Base classes defined here are registered przy the "official" ABCs
# defined w io.py. We don't use real inheritance though, because we don't want
# to inherit the C implementations.

# Rebind dla compatibility
BlockingIOError = BlockingIOError


def open(file, mode="r", buffering=-1, encoding=Nic, errors=Nic,
         newline=Nic, closefd=Prawda, opener=Nic):

    r"""Open file oraz zwróć a stream.  Raise OSError upon failure.

    file jest either a text albo byte string giving the name (and the path
    jeżeli the file isn't w the current working directory) of the file to
    be opened albo an integer file descriptor of the file to be
    wrapped. (If a file descriptor jest given, it jest closed when the
    returned I/O object jest closed, unless closefd jest set to Nieprawda.)

    mode jest an optional string that specifies the mode w which the file jest
    opened. It defaults to 'r' which means open dla reading w text mode. Other
    common values are 'w' dla writing (truncating the file jeżeli it already
    exists), 'x' dla exclusive creation of a new file, oraz 'a' dla appending
    (which on some Unix systems, means that all writes append to the end of the
    file regardless of the current seek position). In text mode, jeżeli encoding jest
    nie specified the encoding used jest platform dependent. (For reading oraz
    writing raw bytes use binary mode oraz leave encoding unspecified.) The
    available modes are:

    ========= ===============================================================
    Character Meaning
    --------- ---------------------------------------------------------------
    'r'       open dla reading (default)
    'w'       open dla writing, truncating the file first
    'x'       create a new file oraz open it dla writing
    'a'       open dla writing, appending to the end of the file jeżeli it exists
    'b'       binary mode
    't'       text mode (default)
    '+'       open a disk file dla updating (reading oraz writing)
    'U'       universal newline mode (deprecated)
    ========= ===============================================================

    The default mode jest 'rt' (open dla reading text). For binary random
    access, the mode 'w+b' opens oraz truncates the file to 0 bytes, while
    'r+b' opens the file without truncation. The 'x' mode implies 'w' oraz
    podnieśs an `FileExistsError` jeżeli the file already exists.

    Python distinguishes between files opened w binary oraz text modes,
    even when the underlying operating system doesn't. Files opened w
    binary mode (appending 'b' to the mode argument) zwróć contents as
    bytes objects without any decoding. In text mode (the default, albo when
    't' jest appended to the mode argument), the contents of the file are
    returned jako strings, the bytes having been first decoded using a
    platform-dependent encoding albo using the specified encoding jeżeli given.

    'U' mode jest deprecated oraz will podnieś an exception w future versions
    of Python.  It has no effect w Python 3.  Use newline to control
    universal newlines mode.

    buffering jest an optional integer used to set the buffering policy.
    Pass 0 to switch buffering off (only allowed w binary mode), 1 to select
    line buffering (only usable w text mode), oraz an integer > 1 to indicate
    the size of a fixed-size chunk buffer.  When no buffering argument jest
    given, the default buffering policy works jako follows:

    * Binary files are buffered w fixed-size chunks; the size of the buffer
      jest chosen using a heuristic trying to determine the underlying device's
      "block size" oraz falling back on `io.DEFAULT_BUFFER_SIZE`.
      On many systems, the buffer will typically be 4096 albo 8192 bytes long.

    * "Interactive" text files (files dla which isatty() returns Prawda)
      use line buffering.  Other text files use the policy described above
      dla binary files.

    encoding jest the str name of the encoding used to decode albo encode the
    file. This should only be used w text mode. The default encoding jest
    platform dependent, but any encoding supported by Python can be
    dalejed.  See the codecs module dla the list of supported encodings.

    errors jest an optional string that specifies how encoding errors are to
    be handled---this argument should nie be used w binary mode. Pass
    'strict' to podnieś a ValueError exception jeżeli there jest an encoding error
    (the default of Nic has the same effect), albo dalej 'ignore' to ignore
    errors. (Note that ignoring encoding errors can lead to data loss.)
    See the documentation dla codecs.register dla a list of the permitted
    encoding error strings.

    newline jest a string controlling how universal newlines works (it only
    applies to text mode). It can be Nic, '', '\n', '\r', oraz '\r\n'.  It works
    jako follows:

    * On input, jeżeli newline jest Nic, universal newlines mode jest
      enabled. Lines w the input can end w '\n', '\r', albo '\r\n', oraz
      these are translated into '\n' before being returned to the
      caller. If it jest '', universal newline mode jest enabled, but line
      endings are returned to the caller untranslated. If it has any of
      the other legal values, input lines are only terminated by the given
      string, oraz the line ending jest returned to the caller untranslated.

    * On output, jeżeli newline jest Nic, any '\n' characters written are
      translated to the system default line separator, os.linesep. If
      newline jest '', no translation takes place. If newline jest any of the
      other legal values, any '\n' characters written are translated to
      the given string.

    closedfd jest a bool. If closefd jest Nieprawda, the underlying file descriptor will
    be kept open when the file jest closed. This does nie work when a file name jest
    given oraz must be Prawda w that case.

    The newly created file jest non-inheritable.

    A custom opener can be used by dalejing a callable jako *opener*. The
    underlying file descriptor dla the file object jest then obtained by calling
    *opener* przy (*file*, *flags*). *opener* must zwróć an open file
    descriptor (passing os.open jako *opener* results w functionality similar to
    dalejing Nic).

    open() returns a file object whose type depends on the mode, oraz
    through which the standard file operations such jako reading oraz writing
    are performed. When open() jest used to open a file w a text mode ('w',
    'r', 'wt', 'rt', etc.), it returns a TextIOWrapper. When used to open
    a file w a binary mode, the returned klasa varies: w read binary
    mode, it returns a BufferedReader; w write binary oraz append binary
    modes, it returns a BufferedWriter, oraz w read/write mode, it returns
    a BufferedRandom.

    It jest also possible to use a string albo bytearray jako a file dla both
    reading oraz writing. For strings StringIO can be used like a file
    opened w a text mode, oraz dla bytes a BytesIO can be used like a file
    opened w a binary mode.
    """
    jeżeli nie isinstance(file, (str, bytes, int)):
        podnieś TypeError("invalid file: %r" % file)
    jeżeli nie isinstance(mode, str):
        podnieś TypeError("invalid mode: %r" % mode)
    jeżeli nie isinstance(buffering, int):
        podnieś TypeError("invalid buffering: %r" % buffering)
    jeżeli encoding jest nie Nic oraz nie isinstance(encoding, str):
        podnieś TypeError("invalid encoding: %r" % encoding)
    jeżeli errors jest nie Nic oraz nie isinstance(errors, str):
        podnieś TypeError("invalid errors: %r" % errors)
    modes = set(mode)
    jeżeli modes - set("axrwb+tU") albo len(mode) > len(modes):
        podnieś ValueError("invalid mode: %r" % mode)
    creating = "x" w modes
    reading = "r" w modes
    writing = "w" w modes
    appending = "a" w modes
    updating = "+" w modes
    text = "t" w modes
    binary = "b" w modes
    jeżeli "U" w modes:
        jeżeli creating albo writing albo appending:
            podnieś ValueError("can't use U oraz writing mode at once")
        zaimportuj warnings
        warnings.warn("'U' mode jest deprecated",
                      DeprecationWarning, 2)
        reading = Prawda
    jeżeli text oraz binary:
        podnieś ValueError("can't have text oraz binary mode at once")
    jeżeli creating + reading + writing + appending > 1:
        podnieś ValueError("can't have read/write/append mode at once")
    jeżeli nie (creating albo reading albo writing albo appending):
        podnieś ValueError("must have exactly one of read/write/append mode")
    jeżeli binary oraz encoding jest nie Nic:
        podnieś ValueError("binary mode doesn't take an encoding argument")
    jeżeli binary oraz errors jest nie Nic:
        podnieś ValueError("binary mode doesn't take an errors argument")
    jeżeli binary oraz newline jest nie Nic:
        podnieś ValueError("binary mode doesn't take a newline argument")
    raw = FileIO(file,
                 (creating oraz "x" albo "") +
                 (reading oraz "r" albo "") +
                 (writing oraz "w" albo "") +
                 (appending oraz "a" albo "") +
                 (updating oraz "+" albo ""),
                 closefd, opener=opener)
    result = raw
    spróbuj:
        line_buffering = Nieprawda
        jeżeli buffering == 1 albo buffering < 0 oraz raw.isatty():
            buffering = -1
            line_buffering = Prawda
        jeżeli buffering < 0:
            buffering = DEFAULT_BUFFER_SIZE
            spróbuj:
                bs = os.fstat(raw.fileno()).st_blksize
            wyjąwszy (OSError, AttributeError):
                dalej
            inaczej:
                jeżeli bs > 1:
                    buffering = bs
        jeżeli buffering < 0:
            podnieś ValueError("invalid buffering size")
        jeżeli buffering == 0:
            jeżeli binary:
                zwróć result
            podnieś ValueError("can't have unbuffered text I/O")
        jeżeli updating:
            buffer = BufferedRandom(raw, buffering)
        albo_inaczej creating albo writing albo appending:
            buffer = BufferedWriter(raw, buffering)
        albo_inaczej reading:
            buffer = BufferedReader(raw, buffering)
        inaczej:
            podnieś ValueError("unknown mode: %r" % mode)
        result = buffer
        jeżeli binary:
            zwróć result
        text = TextIOWrapper(buffer, encoding, errors, newline, line_buffering)
        result = text
        text.mode = mode
        zwróć result
    wyjąwszy:
        result.close()
        podnieś


klasa DocDescriptor:
    """Helper dla builtins.open.__doc__
    """
    def __get__(self, obj, typ):
        zwróć (
            "open(file, mode='r', buffering=-1, encoding=Nic, "
                 "errors=Nic, newline=Nic, closefd=Prawda)\n\n" +
            open.__doc__)

klasa OpenWrapper:
    """Wrapper dla builtins.open

    Trick so that open won't become a bound method when stored
    jako a klasa variable (as dbm.dumb does).

    See initstdio() w Python/pylifecycle.c.
    """
    __doc__ = DocDescriptor()

    def __new__(cls, *args, **kwargs):
        zwróć open(*args, **kwargs)


# In normal operation, both `UnsupportedOperation`s should be bound to the
# same object.
spróbuj:
    UnsupportedOperation = io.UnsupportedOperation
wyjąwszy AttributeError:
    klasa UnsupportedOperation(ValueError, OSError):
        dalej


klasa IOBase(metaclass=abc.ABCMeta):

    """The abstract base klasa dla all I/O classes, acting on streams of
    bytes. There jest no public constructor.

    This klasa provides dummy implementations dla many methods that
    derived classes can override selectively; the default implementations
    represent a file that cannot be read, written albo seeked.

    Even though IOBase does nie declare read, readinto, albo write because
    their signatures will vary, implementations oraz clients should
    consider those methods part of the interface. Also, implementations
    may podnieś UnsupportedOperation when operations they do nie support are
    called.

    The basic type used dla binary data read z albo written to a file jest
    bytes. bytearrays are accepted too, oraz w some cases (such as
    readinto) needed. Text I/O classes work przy str data.

    Note that calling any method (even inquiries) on a closed stream jest
    undefined. Implementations may podnieś OSError w this case.

    IOBase (and its subclasses) support the iterator protocol, meaning
    that an IOBase object can be iterated over uzyskajing the lines w a
    stream.

    IOBase also supports the :keyword:`with` statement. In this example,
    fp jest closed after the suite of the przy statement jest complete:

    przy open('spam.txt', 'r') jako fp:
        fp.write('Spam oraz eggs!')
    """

    ### Internal ###

    def _unsupported(self, name):
        """Internal: podnieś an OSError exception dla unsupported operations."""
        podnieś UnsupportedOperation("%s.%s() nie supported" %
                                   (self.__class__.__name__, name))

    ### Positioning ###

    def seek(self, pos, whence=0):
        """Change stream position.

        Change the stream position to byte offset pos. Argument pos jest
        interpreted relative to the position indicated by whence.  Values
        dla whence are ints:

        * 0 -- start of stream (the default); offset should be zero albo positive
        * 1 -- current stream position; offset may be negative
        * 2 -- end of stream; offset jest usually negative
        Some operating systems / file systems could provide additional values.

        Return an int indicating the new absolute position.
        """
        self._unsupported("seek")

    def tell(self):
        """Return an int indicating the current stream position."""
        zwróć self.seek(0, 1)

    def truncate(self, pos=Nic):
        """Truncate file to size bytes.

        Size defaults to the current IO position jako reported by tell().  Return
        the new size.
        """
        self._unsupported("truncate")

    ### Flush oraz close ###

    def flush(self):
        """Flush write buffers, jeżeli applicable.

        This jest nie implemented dla read-only oraz non-blocking streams.
        """
        self._checkClosed()
        # XXX Should this zwróć the number of bytes written???

    __closed = Nieprawda

    def close(self):
        """Flush oraz close the IO object.

        This method has no effect jeżeli the file jest already closed.
        """
        jeżeli nie self.__closed:
            spróbuj:
                self.flush()
            w_końcu:
                self.__closed = Prawda

    def __del__(self):
        """Destructor.  Calls close()."""
        # The try/wyjąwszy block jest w case this jest called at program
        # exit time, when it's possible that globals have already been
        # deleted, oraz then the close() call might fail.  Since
        # there's nothing we can do about such failures oraz they annoy
        # the end users, we suppress the traceback.
        spróbuj:
            self.close()
        wyjąwszy:
            dalej

    ### Inquiries ###

    def seekable(self):
        """Return a bool indicating whether object supports random access.

        If Nieprawda, seek(), tell() oraz truncate() will podnieś UnsupportedOperation.
        This method may need to do a test seek().
        """
        zwróć Nieprawda

    def _checkSeekable(self, msg=Nic):
        """Internal: podnieś UnsupportedOperation jeżeli file jest nie seekable
        """
        jeżeli nie self.seekable():
            podnieś UnsupportedOperation("File albo stream jest nie seekable."
                                       jeżeli msg jest Nic inaczej msg)

    def readable(self):
        """Return a bool indicating whether object was opened dla reading.

        If Nieprawda, read() will podnieś UnsupportedOperation.
        """
        zwróć Nieprawda

    def _checkReadable(self, msg=Nic):
        """Internal: podnieś UnsupportedOperation jeżeli file jest nie readable
        """
        jeżeli nie self.readable():
            podnieś UnsupportedOperation("File albo stream jest nie readable."
                                       jeżeli msg jest Nic inaczej msg)

    def writable(self):
        """Return a bool indicating whether object was opened dla writing.

        If Nieprawda, write() oraz truncate() will podnieś UnsupportedOperation.
        """
        zwróć Nieprawda

    def _checkWritable(self, msg=Nic):
        """Internal: podnieś UnsupportedOperation jeżeli file jest nie writable
        """
        jeżeli nie self.writable():
            podnieś UnsupportedOperation("File albo stream jest nie writable."
                                       jeżeli msg jest Nic inaczej msg)

    @property
    def closed(self):
        """closed: bool.  Prawda iff the file has been closed.

        For backwards compatibility, this jest a property, nie a predicate.
        """
        zwróć self.__closed

    def _checkClosed(self, msg=Nic):
        """Internal: podnieś an ValueError jeżeli file jest closed
        """
        jeżeli self.closed:
            podnieś ValueError("I/O operation on closed file."
                             jeżeli msg jest Nic inaczej msg)

    ### Context manager ###

    def __enter__(self):  # That's a forward reference
        """Context management protocol.  Returns self (an instance of IOBase)."""
        self._checkClosed()
        zwróć self

    def __exit__(self, *args):
        """Context management protocol.  Calls close()"""
        self.close()

    ### Lower-level APIs ###

    # XXX Should these be present even jeżeli unimplemented?

    def fileno(self):
        """Returns underlying file descriptor (an int) jeżeli one exists.

        An OSError jest podnieśd jeżeli the IO object does nie use a file descriptor.
        """
        self._unsupported("fileno")

    def isatty(self):
        """Return a bool indicating whether this jest an 'interactive' stream.

        Return Nieprawda jeżeli it can't be determined.
        """
        self._checkClosed()
        zwróć Nieprawda

    ### Readline[s] oraz writelines ###

    def readline(self, size=-1):
        r"""Read oraz zwróć a line of bytes z the stream.

        If size jest specified, at most size bytes will be read.
        Size should be an int.

        The line terminator jest always b'\n' dla binary files; dla text
        files, the newlines argument to open can be used to select the line
        terminator(s) recognized.
        """
        # For backwards compatibility, a (slowish) readline().
        jeżeli hasattr(self, "peek"):
            def nreadahead():
                readahead = self.peek(1)
                jeżeli nie readahead:
                    zwróć 1
                n = (readahead.find(b"\n") + 1) albo len(readahead)
                jeżeli size >= 0:
                    n = min(n, size)
                zwróć n
        inaczej:
            def nreadahead():
                zwróć 1
        jeżeli size jest Nic:
            size = -1
        albo_inaczej nie isinstance(size, int):
            podnieś TypeError("size must be an integer")
        res = bytearray()
        dopóki size < 0 albo len(res) < size:
            b = self.read(nreadahead())
            jeżeli nie b:
                przerwij
            res += b
            jeżeli res.endswith(b"\n"):
                przerwij
        zwróć bytes(res)

    def __iter__(self):
        self._checkClosed()
        zwróć self

    def __next__(self):
        line = self.readline()
        jeżeli nie line:
            podnieś StopIteration
        zwróć line

    def readlines(self, hint=Nic):
        """Return a list of lines z the stream.

        hint can be specified to control the number of lines read: no more
        lines will be read jeżeli the total size (in bytes/characters) of all
        lines so far exceeds hint.
        """
        jeżeli hint jest Nic albo hint <= 0:
            zwróć list(self)
        n = 0
        lines = []
        dla line w self:
            lines.append(line)
            n += len(line)
            jeżeli n >= hint:
                przerwij
        zwróć lines

    def writelines(self, lines):
        self._checkClosed()
        dla line w lines:
            self.write(line)

io.IOBase.register(IOBase)


klasa RawIOBase(IOBase):

    """Base klasa dla raw binary I/O."""

    # The read() method jest implemented by calling readinto(); derived
    # classes that want to support read() only need to implement
    # readinto() jako a primitive operation.  In general, readinto() can be
    # more efficient than read().

    # (It would be tempting to also provide an implementation of
    # readinto() w terms of read(), w case the latter jest a more suitable
    # primitive operation, but that would lead to nasty recursion w case
    # a subclass doesn't implement either.)

    def read(self, size=-1):
        """Read oraz zwróć up to size bytes, where size jest an int.

        Returns an empty bytes object on EOF, albo Nic jeżeli the object jest
        set nie to block oraz has no data to read.
        """
        jeżeli size jest Nic:
            size = -1
        jeżeli size < 0:
            zwróć self.readall()
        b = bytearray(size.__index__())
        n = self.readinto(b)
        jeżeli n jest Nic:
            zwróć Nic
        usuń b[n:]
        zwróć bytes(b)

    def readall(self):
        """Read until EOF, using multiple read() call."""
        res = bytearray()
        dopóki Prawda:
            data = self.read(DEFAULT_BUFFER_SIZE)
            jeżeli nie data:
                przerwij
            res += data
        jeżeli res:
            zwróć bytes(res)
        inaczej:
            # b'' albo Nic
            zwróć data

    def readinto(self, b):
        """Read up to len(b) bytes into bytearray b.

        Returns an int representing the number of bytes read (0 dla EOF), albo
        Nic jeżeli the object jest set nie to block oraz has no data to read.
        """
        self._unsupported("readinto")

    def write(self, b):
        """Write the given buffer to the IO stream.

        Returns the number of bytes written, which may be less than len(b).
        """
        self._unsupported("write")

io.RawIOBase.register(RawIOBase)
z _io zaimportuj FileIO
RawIOBase.register(FileIO)


klasa BufferedIOBase(IOBase):

    """Base klasa dla buffered IO objects.

    The main difference przy RawIOBase jest that the read() method
    supports omitting the size argument, oraz does nie have a default
    implementation that defers to readinto().

    In addition, read(), readinto() oraz write() may podnieś
    BlockingIOError jeżeli the underlying raw stream jest w non-blocking
    mode oraz nie ready; unlike their raw counterparts, they will never
    zwróć Nic.

    A typical implementation should nie inherit z a RawIOBase
    implementation, but wrap one.
    """

    def read(self, size=Nic):
        """Read oraz zwróć up to size bytes, where size jest an int.

        If the argument jest omitted, Nic, albo negative, reads oraz
        returns all data until EOF.

        If the argument jest positive, oraz the underlying raw stream jest
        nie 'interactive', multiple raw reads may be issued to satisfy
        the byte count (unless EOF jest reached first).  But for
        interactive raw streams (XXX oraz dla pipes?), at most one raw
        read will be issued, oraz a short result does nie imply that
        EOF jest imminent.

        Returns an empty bytes array on EOF.

        Raises BlockingIOError jeżeli the underlying raw stream has no
        data at the moment.
        """
        self._unsupported("read")

    def read1(self, size=Nic):
        """Read up to size bytes przy at most one read() system call,
        where size jest an int.
        """
        self._unsupported("read1")

    def readinto(self, b):
        """Read up to len(b) bytes into bytearray b.

        Like read(), this may issue multiple reads to the underlying raw
        stream, unless the latter jest 'interactive'.

        Returns an int representing the number of bytes read (0 dla EOF).

        Raises BlockingIOError jeżeli the underlying raw stream has no
        data at the moment.
        """

        zwróć self._readinto(b, read1=Nieprawda)

    def readinto1(self, b):
        """Read up to len(b) bytes into *b*, using at most one system call

        Returns an int representing the number of bytes read (0 dla EOF).

        Raises BlockingIOError jeżeli the underlying raw stream has no
        data at the moment.
        """

        zwróć self._readinto(b, read1=Prawda)

    def _readinto(self, b, read1):
        jeżeli nie isinstance(b, memoryview):
            b = memoryview(b)
        b = b.cast('B')

        jeżeli read1:
            data = self.read1(len(b))
        inaczej:
            data = self.read(len(b))
        n = len(data)

        b[:n] = data

        zwróć n

    def write(self, b):
        """Write the given bytes buffer to the IO stream.

        Return the number of bytes written, which jest never less than
        len(b).

        Raises BlockingIOError jeżeli the buffer jest full oraz the
        underlying raw stream cannot accept more data at the moment.
        """
        self._unsupported("write")

    def detach(self):
        """
        Separate the underlying raw stream z the buffer oraz zwróć it.

        After the raw stream has been detached, the buffer jest w an unusable
        state.
        """
        self._unsupported("detach")

io.BufferedIOBase.register(BufferedIOBase)


klasa _BufferedIOMixin(BufferedIOBase):

    """A mixin implementation of BufferedIOBase przy an underlying raw stream.

    This dalejes most requests on to the underlying raw stream.  It
    does *not* provide implementations of read(), readinto() albo
    write().
    """

    def __init__(self, raw):
        self._raw = raw

    ### Positioning ###

    def seek(self, pos, whence=0):
        new_position = self.raw.seek(pos, whence)
        jeżeli new_position < 0:
            podnieś OSError("seek() returned an invalid position")
        zwróć new_position

    def tell(self):
        pos = self.raw.tell()
        jeżeli pos < 0:
            podnieś OSError("tell() returned an invalid position")
        zwróć pos

    def truncate(self, pos=Nic):
        # Flush the stream.  We're mixing buffered I/O przy lower-level I/O,
        # oraz a flush may be necessary to synch both views of the current
        # file state.
        self.flush()

        jeżeli pos jest Nic:
            pos = self.tell()
        # XXX: Should seek() be used, instead of dalejing the position
        # XXX  directly to truncate?
        zwróć self.raw.truncate(pos)

    ### Flush oraz close ###

    def flush(self):
        jeżeli self.closed:
            podnieś ValueError("flush of closed file")
        self.raw.flush()

    def close(self):
        jeżeli self.raw jest nie Nic oraz nie self.closed:
            spróbuj:
                # may podnieś BlockingIOError albo BrokenPipeError etc
                self.flush()
            w_końcu:
                self.raw.close()

    def detach(self):
        jeżeli self.raw jest Nic:
            podnieś ValueError("raw stream already detached")
        self.flush()
        raw = self._raw
        self._raw = Nic
        zwróć raw

    ### Inquiries ###

    def seekable(self):
        zwróć self.raw.seekable()

    def readable(self):
        zwróć self.raw.readable()

    def writable(self):
        zwróć self.raw.writable()

    @property
    def raw(self):
        zwróć self._raw

    @property
    def closed(self):
        zwróć self.raw.closed

    @property
    def name(self):
        zwróć self.raw.name

    @property
    def mode(self):
        zwróć self.raw.mode

    def __getstate__(self):
        podnieś TypeError("can nie serialize a '{0}' object"
                        .format(self.__class__.__name__))

    def __repr__(self):
        modname = self.__class__.__module__
        clsname = self.__class__.__qualname__
        spróbuj:
            name = self.name
        wyjąwszy Exception:
            zwróć "<{}.{}>".format(modname, clsname)
        inaczej:
            zwróć "<{}.{} name={!r}>".format(modname, clsname, name)

    ### Lower-level APIs ###

    def fileno(self):
        zwróć self.raw.fileno()

    def isatty(self):
        zwróć self.raw.isatty()


klasa BytesIO(BufferedIOBase):

    """Buffered I/O implementation using an in-memory bytes buffer."""

    def __init__(self, initial_bytes=Nic):
        buf = bytearray()
        jeżeli initial_bytes jest nie Nic:
            buf += initial_bytes
        self._buffer = buf
        self._pos = 0

    def __getstate__(self):
        jeżeli self.closed:
            podnieś ValueError("__getstate__ on closed file")
        zwróć self.__dict__.copy()

    def getvalue(self):
        """Return the bytes value (contents) of the buffer
        """
        jeżeli self.closed:
            podnieś ValueError("getvalue on closed file")
        zwróć bytes(self._buffer)

    def getbuffer(self):
        """Return a readable oraz writable view of the buffer.
        """
        jeżeli self.closed:
            podnieś ValueError("getbuffer on closed file")
        zwróć memoryview(self._buffer)

    def close(self):
        self._buffer.clear()
        super().close()

    def read(self, size=Nic):
        jeżeli self.closed:
            podnieś ValueError("read z closed file")
        jeżeli size jest Nic:
            size = -1
        jeżeli size < 0:
            size = len(self._buffer)
        jeżeli len(self._buffer) <= self._pos:
            zwróć b""
        newpos = min(len(self._buffer), self._pos + size)
        b = self._buffer[self._pos : newpos]
        self._pos = newpos
        zwróć bytes(b)

    def read1(self, size):
        """This jest the same jako read.
        """
        zwróć self.read(size)

    def write(self, b):
        jeżeli self.closed:
            podnieś ValueError("write to closed file")
        jeżeli isinstance(b, str):
            podnieś TypeError("can't write str to binary stream")
        n = len(b)
        jeżeli n == 0:
            zwróć 0
        pos = self._pos
        jeżeli pos > len(self._buffer):
            # Inserts null bytes between the current end of the file
            # oraz the new write position.
            padding = b'\x00' * (pos - len(self._buffer))
            self._buffer += padding
        self._buffer[pos:pos + n] = b
        self._pos += n
        zwróć n

    def seek(self, pos, whence=0):
        jeżeli self.closed:
            podnieś ValueError("seek on closed file")
        spróbuj:
            pos.__index__
        wyjąwszy AttributeError jako err:
            podnieś TypeError("an integer jest required") z err
        jeżeli whence == 0:
            jeżeli pos < 0:
                podnieś ValueError("negative seek position %r" % (pos,))
            self._pos = pos
        albo_inaczej whence == 1:
            self._pos = max(0, self._pos + pos)
        albo_inaczej whence == 2:
            self._pos = max(0, len(self._buffer) + pos)
        inaczej:
            podnieś ValueError("unsupported whence value")
        zwróć self._pos

    def tell(self):
        jeżeli self.closed:
            podnieś ValueError("tell on closed file")
        zwróć self._pos

    def truncate(self, pos=Nic):
        jeżeli self.closed:
            podnieś ValueError("truncate on closed file")
        jeżeli pos jest Nic:
            pos = self._pos
        inaczej:
            spróbuj:
                pos.__index__
            wyjąwszy AttributeError jako err:
                podnieś TypeError("an integer jest required") z err
            jeżeli pos < 0:
                podnieś ValueError("negative truncate position %r" % (pos,))
        usuń self._buffer[pos:]
        zwróć pos

    def readable(self):
        jeżeli self.closed:
            podnieś ValueError("I/O operation on closed file.")
        zwróć Prawda

    def writable(self):
        jeżeli self.closed:
            podnieś ValueError("I/O operation on closed file.")
        zwróć Prawda

    def seekable(self):
        jeżeli self.closed:
            podnieś ValueError("I/O operation on closed file.")
        zwróć Prawda


klasa BufferedReader(_BufferedIOMixin):

    """BufferedReader(raw[, buffer_size])

    A buffer dla a readable, sequential BaseRawIO object.

    The constructor creates a BufferedReader dla the given readable raw
    stream oraz buffer_size. If buffer_size jest omitted, DEFAULT_BUFFER_SIZE
    jest used.
    """

    def __init__(self, raw, buffer_size=DEFAULT_BUFFER_SIZE):
        """Create a new buffered reader using the given readable raw IO object.
        """
        jeżeli nie raw.readable():
            podnieś OSError('"raw" argument must be readable.')

        _BufferedIOMixin.__init__(self, raw)
        jeżeli buffer_size <= 0:
            podnieś ValueError("invalid buffer size")
        self.buffer_size = buffer_size
        self._reset_read_buf()
        self._read_lock = Lock()

    def _reset_read_buf(self):
        self._read_buf = b""
        self._read_pos = 0

    def read(self, size=Nic):
        """Read size bytes.

        Returns exactly size bytes of data unless the underlying raw IO
        stream reaches EOF albo jeżeli the call would block w non-blocking
        mode. If size jest negative, read until EOF albo until read() would
        block.
        """
        jeżeli size jest nie Nic oraz size < -1:
            podnieś ValueError("invalid number of bytes to read")
        przy self._read_lock:
            zwróć self._read_unlocked(size)

    def _read_unlocked(self, n=Nic):
        nodata_val = b""
        empty_values = (b"", Nic)
        buf = self._read_buf
        pos = self._read_pos

        # Special case dla when the number of bytes to read jest unspecified.
        jeżeli n jest Nic albo n == -1:
            self._reset_read_buf()
            jeżeli hasattr(self.raw, 'readall'):
                chunk = self.raw.readall()
                jeżeli chunk jest Nic:
                    zwróć buf[pos:] albo Nic
                inaczej:
                    zwróć buf[pos:] + chunk
            chunks = [buf[pos:]]  # Strip the consumed bytes.
            current_size = 0
            dopóki Prawda:
                # Read until EOF albo until read() would block.
                chunk = self.raw.read()
                jeżeli chunk w empty_values:
                    nodata_val = chunk
                    przerwij
                current_size += len(chunk)
                chunks.append(chunk)
            zwróć b"".join(chunks) albo nodata_val

        # The number of bytes to read jest specified, zwróć at most n bytes.
        avail = len(buf) - pos  # Length of the available buffered data.
        jeżeli n <= avail:
            # Fast path: the data to read jest fully buffered.
            self._read_pos += n
            zwróć buf[pos:pos+n]
        # Slow path: read z the stream until enough bytes are read,
        # albo until an EOF occurs albo until read() would block.
        chunks = [buf[pos:]]
        wanted = max(self.buffer_size, n)
        dopóki avail < n:
            chunk = self.raw.read(wanted)
            jeżeli chunk w empty_values:
                nodata_val = chunk
                przerwij
            avail += len(chunk)
            chunks.append(chunk)
        # n jest more then avail only when an EOF occurred albo when
        # read() would have blocked.
        n = min(n, avail)
        out = b"".join(chunks)
        self._read_buf = out[n:]  # Save the extra data w the buffer.
        self._read_pos = 0
        zwróć out[:n] jeżeli out inaczej nodata_val

    def peek(self, size=0):
        """Returns buffered bytes without advancing the position.

        The argument indicates a desired minimal number of bytes; we
        do at most one raw read to satisfy it.  We never zwróć more
        than self.buffer_size.
        """
        przy self._read_lock:
            zwróć self._peek_unlocked(size)

    def _peek_unlocked(self, n=0):
        want = min(n, self.buffer_size)
        have = len(self._read_buf) - self._read_pos
        jeżeli have < want albo have <= 0:
            to_read = self.buffer_size - have
            current = self.raw.read(to_read)
            jeżeli current:
                self._read_buf = self._read_buf[self._read_pos:] + current
                self._read_pos = 0
        zwróć self._read_buf[self._read_pos:]

    def read1(self, size):
        """Reads up to size bytes, przy at most one read() system call."""
        # Returns up to size bytes.  If at least one byte jest buffered, we
        # only zwróć buffered bytes.  Otherwise, we do one raw read.
        jeżeli size < 0:
            podnieś ValueError("number of bytes to read must be positive")
        jeżeli size == 0:
            zwróć b""
        przy self._read_lock:
            self._peek_unlocked(1)
            zwróć self._read_unlocked(
                min(size, len(self._read_buf) - self._read_pos))

    # Implementing readinto() oraz readinto1() jest nie strictly necessary (we
    # could rely on the base klasa that provides an implementation w terms of
    # read() oraz read1()). We do it anyway to keep the _pyio implementation
    # similar to the io implementation (which implements the methods for
    # performance reasons).
    def _readinto(self, buf, read1):
        """Read data into *buf* przy at most one system call."""

        jeżeli len(buf) == 0:
            zwróć 0

        # Need to create a memoryview object of type 'b', otherwise
        # we may nie be able to assign bytes to it, oraz slicing it
        # would create a new object.
        jeżeli nie isinstance(buf, memoryview):
            buf = memoryview(buf)
        buf = buf.cast('B')

        written = 0
        przy self._read_lock:
            dopóki written < len(buf):

                # First try to read z internal buffer
                avail = min(len(self._read_buf) - self._read_pos, len(buf))
                jeżeli avail:
                    buf[written:written+avail] = \
                        self._read_buf[self._read_pos:self._read_pos+avail]
                    self._read_pos += avail
                    written += avail
                    jeżeli written == len(buf):
                        przerwij

                # If remaining space w callers buffer jest larger than
                # internal buffer, read directly into callers buffer
                jeżeli len(buf) - written > self.buffer_size:
                    n = self.raw.readinto(buf[written:])
                    jeżeli nie n:
                        przerwij # eof
                    written += n

                # Otherwise refill internal buffer - unless we're
                # w read1 mode oraz already got some data
                albo_inaczej nie (read1 oraz written):
                    jeżeli nie self._peek_unlocked(1):
                        przerwij # eof

                # In readinto1 mode, zwróć jako soon jako we have some data
                jeżeli read1 oraz written:
                    przerwij

        zwróć written

    def tell(self):
        zwróć _BufferedIOMixin.tell(self) - len(self._read_buf) + self._read_pos

    def seek(self, pos, whence=0):
        jeżeli whence nie w valid_seek_flags:
            podnieś ValueError("invalid whence value")
        przy self._read_lock:
            jeżeli whence == 1:
                pos -= len(self._read_buf) - self._read_pos
            pos = _BufferedIOMixin.seek(self, pos, whence)
            self._reset_read_buf()
            zwróć pos

klasa BufferedWriter(_BufferedIOMixin):

    """A buffer dla a writeable sequential RawIO object.

    The constructor creates a BufferedWriter dla the given writeable raw
    stream. If the buffer_size jest nie given, it defaults to
    DEFAULT_BUFFER_SIZE.
    """

    def __init__(self, raw, buffer_size=DEFAULT_BUFFER_SIZE):
        jeżeli nie raw.writable():
            podnieś OSError('"raw" argument must be writable.')

        _BufferedIOMixin.__init__(self, raw)
        jeżeli buffer_size <= 0:
            podnieś ValueError("invalid buffer size")
        self.buffer_size = buffer_size
        self._write_buf = bytearray()
        self._write_lock = Lock()

    def write(self, b):
        jeżeli self.closed:
            podnieś ValueError("write to closed file")
        jeżeli isinstance(b, str):
            podnieś TypeError("can't write str to binary stream")
        przy self._write_lock:
            # XXX we can implement some more tricks to try oraz avoid
            # partial writes
            jeżeli len(self._write_buf) > self.buffer_size:
                # We're full, so let's pre-flush the buffer.  (This may
                # podnieś BlockingIOError przy characters_written == 0.)
                self._flush_unlocked()
            before = len(self._write_buf)
            self._write_buf.extend(b)
            written = len(self._write_buf) - before
            jeżeli len(self._write_buf) > self.buffer_size:
                spróbuj:
                    self._flush_unlocked()
                wyjąwszy BlockingIOError jako e:
                    jeżeli len(self._write_buf) > self.buffer_size:
                        # We've hit the buffer_size. We have to accept a partial
                        # write oraz cut back our buffer.
                        overage = len(self._write_buf) - self.buffer_size
                        written -= overage
                        self._write_buf = self._write_buf[:self.buffer_size]
                        podnieś BlockingIOError(e.errno, e.strerror, written)
            zwróć written

    def truncate(self, pos=Nic):
        przy self._write_lock:
            self._flush_unlocked()
            jeżeli pos jest Nic:
                pos = self.raw.tell()
            zwróć self.raw.truncate(pos)

    def flush(self):
        przy self._write_lock:
            self._flush_unlocked()

    def _flush_unlocked(self):
        jeżeli self.closed:
            podnieś ValueError("flush of closed file")
        dopóki self._write_buf:
            spróbuj:
                n = self.raw.write(self._write_buf)
            wyjąwszy BlockingIOError:
                podnieś RuntimeError("self.raw should implement RawIOBase: it "
                                   "should nie podnieś BlockingIOError")
            jeżeli n jest Nic:
                podnieś BlockingIOError(
                    errno.EAGAIN,
                    "write could nie complete without blocking", 0)
            jeżeli n > len(self._write_buf) albo n < 0:
                podnieś OSError("write() returned incorrect number of bytes")
            usuń self._write_buf[:n]

    def tell(self):
        zwróć _BufferedIOMixin.tell(self) + len(self._write_buf)

    def seek(self, pos, whence=0):
        jeżeli whence nie w valid_seek_flags:
            podnieś ValueError("invalid whence value")
        przy self._write_lock:
            self._flush_unlocked()
            zwróć _BufferedIOMixin.seek(self, pos, whence)


klasa BufferedRWPair(BufferedIOBase):

    """A buffered reader oraz writer object together.

    A buffered reader object oraz buffered writer object put together to
    form a sequential IO object that can read oraz write. This jest typically
    used przy a socket albo two-way pipe.

    reader oraz writer are RawIOBase objects that are readable oraz
    writeable respectively. If the buffer_size jest omitted it defaults to
    DEFAULT_BUFFER_SIZE.
    """

    # XXX The usefulness of this (compared to having two separate IO
    # objects) jest questionable.

    def __init__(self, reader, writer, buffer_size=DEFAULT_BUFFER_SIZE):
        """Constructor.

        The arguments are two RawIO instances.
        """
        jeżeli nie reader.readable():
            podnieś OSError('"reader" argument must be readable.')

        jeżeli nie writer.writable():
            podnieś OSError('"writer" argument must be writable.')

        self.reader = BufferedReader(reader, buffer_size)
        self.writer = BufferedWriter(writer, buffer_size)

    def read(self, size=Nic):
        jeżeli size jest Nic:
            size = -1
        zwróć self.reader.read(size)

    def readinto(self, b):
        zwróć self.reader.readinto(b)

    def write(self, b):
        zwróć self.writer.write(b)

    def peek(self, size=0):
        zwróć self.reader.peek(size)

    def read1(self, size):
        zwróć self.reader.read1(size)

    def readinto1(self, b):
        zwróć self.reader.readinto1(b)

    def readable(self):
        zwróć self.reader.readable()

    def writable(self):
        zwróć self.writer.writable()

    def flush(self):
        zwróć self.writer.flush()

    def close(self):
        spróbuj:
            self.writer.close()
        w_końcu:
            self.reader.close()

    def isatty(self):
        zwróć self.reader.isatty() albo self.writer.isatty()

    @property
    def closed(self):
        zwróć self.writer.closed


klasa BufferedRandom(BufferedWriter, BufferedReader):

    """A buffered interface to random access streams.

    The constructor creates a reader oraz writer dla a seekable stream,
    raw, given w the first argument. If the buffer_size jest omitted it
    defaults to DEFAULT_BUFFER_SIZE.
    """

    def __init__(self, raw, buffer_size=DEFAULT_BUFFER_SIZE):
        raw._checkSeekable()
        BufferedReader.__init__(self, raw, buffer_size)
        BufferedWriter.__init__(self, raw, buffer_size)

    def seek(self, pos, whence=0):
        jeżeli whence nie w valid_seek_flags:
            podnieś ValueError("invalid whence value")
        self.flush()
        jeżeli self._read_buf:
            # Undo read ahead.
            przy self._read_lock:
                self.raw.seek(self._read_pos - len(self._read_buf), 1)
        # First do the raw seek, then empty the read buffer, so that
        # jeżeli the raw seek fails, we don't lose buffered data forever.
        pos = self.raw.seek(pos, whence)
        przy self._read_lock:
            self._reset_read_buf()
        jeżeli pos < 0:
            podnieś OSError("seek() returned invalid position")
        zwróć pos

    def tell(self):
        jeżeli self._write_buf:
            zwróć BufferedWriter.tell(self)
        inaczej:
            zwróć BufferedReader.tell(self)

    def truncate(self, pos=Nic):
        jeżeli pos jest Nic:
            pos = self.tell()
        # Use seek to flush the read buffer.
        zwróć BufferedWriter.truncate(self, pos)

    def read(self, size=Nic):
        jeżeli size jest Nic:
            size = -1
        self.flush()
        zwróć BufferedReader.read(self, size)

    def readinto(self, b):
        self.flush()
        zwróć BufferedReader.readinto(self, b)

    def peek(self, size=0):
        self.flush()
        zwróć BufferedReader.peek(self, size)

    def read1(self, size):
        self.flush()
        zwróć BufferedReader.read1(self, size)

    def readinto1(self, b):
        self.flush()
        zwróć BufferedReader.readinto1(self, b)

    def write(self, b):
        jeżeli self._read_buf:
            # Undo readahead
            przy self._read_lock:
                self.raw.seek(self._read_pos - len(self._read_buf), 1)
                self._reset_read_buf()
        zwróć BufferedWriter.write(self, b)


klasa FileIO(RawIOBase):
    _fd = -1
    _created = Nieprawda
    _readable = Nieprawda
    _writable = Nieprawda
    _appending = Nieprawda
    _seekable = Nic
    _closefd = Prawda

    def __init__(self, file, mode='r', closefd=Prawda, opener=Nic):
        """Open a file.  The mode can be 'r' (default), 'w', 'x' albo 'a' dla reading,
        writing, exclusive creation albo appending.  The file will be created jeżeli it
        doesn't exist when opened dla writing albo appending; it will be truncated
        when opened dla writing.  A FileExistsError will be podnieśd jeżeli it already
        exists when opened dla creating. Opening a file dla creating implies
        writing so this mode behaves w a similar way to 'w'. Add a '+' to the mode
        to allow simultaneous reading oraz writing. A custom opener can be used by
        dalejing a callable jako *opener*. The underlying file descriptor dla the file
        object jest then obtained by calling opener przy (*name*, *flags*).
        *opener* must zwróć an open file descriptor (passing os.open jako *opener*
        results w functionality similar to dalejing Nic).
        """
        jeżeli self._fd >= 0:
            # Have to close the existing file first.
            spróbuj:
                jeżeli self._closefd:
                    os.close(self._fd)
            w_końcu:
                self._fd = -1

        jeżeli isinstance(file, float):
            podnieś TypeError('integer argument expected, got float')
        jeżeli isinstance(file, int):
            fd = file
            jeżeli fd < 0:
                podnieś ValueError('negative file descriptor')
        inaczej:
            fd = -1

        jeżeli nie isinstance(mode, str):
            podnieś TypeError('invalid mode: %s' % (mode,))
        jeżeli nie set(mode) <= set('xrwab+'):
            podnieś ValueError('invalid mode: %s' % (mode,))
        jeżeli sum(c w 'rwax' dla c w mode) != 1 albo mode.count('+') > 1:
            podnieś ValueError('Must have exactly one of create/read/write/append '
                             'mode oraz at most one plus')

        jeżeli 'x' w mode:
            self._created = Prawda
            self._writable = Prawda
            flags = os.O_EXCL | os.O_CREAT
        albo_inaczej 'r' w mode:
            self._readable = Prawda
            flags = 0
        albo_inaczej 'w' w mode:
            self._writable = Prawda
            flags = os.O_CREAT | os.O_TRUNC
        albo_inaczej 'a' w mode:
            self._writable = Prawda
            self._appending = Prawda
            flags = os.O_APPEND | os.O_CREAT

        jeżeli '+' w mode:
            self._readable = Prawda
            self._writable = Prawda

        jeżeli self._readable oraz self._writable:
            flags |= os.O_RDWR
        albo_inaczej self._readable:
            flags |= os.O_RDONLY
        inaczej:
            flags |= os.O_WRONLY

        flags |= getattr(os, 'O_BINARY', 0)

        noinherit_flag = (getattr(os, 'O_NOINHERIT', 0) albo
                          getattr(os, 'O_CLOEXEC', 0))
        flags |= noinherit_flag

        owned_fd = Nic
        spróbuj:
            jeżeli fd < 0:
                jeżeli nie closefd:
                    podnieś ValueError('Cannot use closefd=Nieprawda przy file name')
                jeżeli opener jest Nic:
                    fd = os.open(file, flags, 0o666)
                inaczej:
                    fd = opener(file, flags)
                    jeżeli nie isinstance(fd, int):
                        podnieś TypeError('expected integer z opener')
                    jeżeli fd < 0:
                        podnieś OSError('Negative file descriptor')
                owned_fd = fd
                jeżeli nie noinherit_flag:
                    os.set_inheritable(fd, Nieprawda)

            self._closefd = closefd
            fdfstat = os.fstat(fd)
            spróbuj:
                jeżeli stat.S_ISDIR(fdfstat.st_mode):
                    podnieś IsADirectoryError(errno.EISDIR,
                                            os.strerror(errno.EISDIR), file)
            wyjąwszy AttributeError:
                # Ignore the AttribueError jeżeli stat.S_ISDIR albo errno.EISDIR
                # don't exist.
                dalej
            self._blksize = getattr(fdfstat, 'st_blksize', 0)
            jeżeli self._blksize <= 1:
                self._blksize = DEFAULT_BUFFER_SIZE

            jeżeli _setmode:
                # don't translate newlines (\r\n <=> \n)
                _setmode(fd, os.O_BINARY)

            self.name = file
            jeżeli self._appending:
                # For consistent behaviour, we explicitly seek to the
                # end of file (otherwise, it might be done only on the
                # first write()).
                os.lseek(fd, 0, SEEK_END)
        wyjąwszy:
            jeżeli owned_fd jest nie Nic:
                os.close(owned_fd)
            podnieś
        self._fd = fd

    def __del__(self):
        jeżeli self._fd >= 0 oraz self._closefd oraz nie self.closed:
            zaimportuj warnings
            warnings.warn('unclosed file %r' % (self,), ResourceWarning,
                          stacklevel=2)
            self.close()

    def __getstate__(self):
        podnieś TypeError("cannot serialize '%s' object", self.__class__.__name__)

    def __repr__(self):
        class_name = '%s.%s' % (self.__class__.__module__,
                                self.__class__.__qualname__)
        jeżeli self.closed:
            zwróć '<%s [closed]>' % class_name
        spróbuj:
            name = self.name
        wyjąwszy AttributeError:
            zwróć ('<%s fd=%d mode=%r closefd=%r>' %
                    (class_name, self._fd, self.mode, self._closefd))
        inaczej:
            zwróć ('<%s name=%r mode=%r closefd=%r>' %
                    (class_name, name, self.mode, self._closefd))

    def _checkReadable(self):
        jeżeli nie self._readable:
            podnieś UnsupportedOperation('File nie open dla reading')

    def _checkWritable(self, msg=Nic):
        jeżeli nie self._writable:
            podnieś UnsupportedOperation('File nie open dla writing')

    def read(self, size=Nic):
        """Read at most size bytes, returned jako bytes.

        Only makes one system call, so less data may be returned than requested
        In non-blocking mode, returns Nic jeżeli no data jest available.
        Return an empty bytes object at EOF.
        """
        self._checkClosed()
        self._checkReadable()
        jeżeli size jest Nic albo size < 0:
            zwróć self.readall()
        spróbuj:
            zwróć os.read(self._fd, size)
        wyjąwszy BlockingIOError:
            zwróć Nic

    def readall(self):
        """Read all data z the file, returned jako bytes.

        In non-blocking mode, returns jako much jako jest immediately available,
        albo Nic jeżeli no data jest available.  Return an empty bytes object at EOF.
        """
        self._checkClosed()
        self._checkReadable()
        bufsize = DEFAULT_BUFFER_SIZE
        spróbuj:
            pos = os.lseek(self._fd, 0, SEEK_CUR)
            end = os.fstat(self._fd).st_size
            jeżeli end >= pos:
                bufsize = end - pos + 1
        wyjąwszy OSError:
            dalej

        result = bytearray()
        dopóki Prawda:
            jeżeli len(result) >= bufsize:
                bufsize = len(result)
                bufsize += max(bufsize, DEFAULT_BUFFER_SIZE)
            n = bufsize - len(result)
            spróbuj:
                chunk = os.read(self._fd, n)
            wyjąwszy BlockingIOError:
                jeżeli result:
                    przerwij
                zwróć Nic
            jeżeli nie chunk: # reached the end of the file
                przerwij
            result += chunk

        zwróć bytes(result)

    def readinto(self, b):
        """Same jako RawIOBase.readinto()."""
        m = memoryview(b).cast('B')
        data = self.read(len(m))
        n = len(data)
        m[:n] = data
        zwróć n

    def write(self, b):
        """Write bytes b to file, zwróć number written.

        Only makes one system call, so nie all of the data may be written.
        The number of bytes actually written jest returned.  In non-blocking mode,
        returns Nic jeżeli the write would block.
        """
        self._checkClosed()
        self._checkWritable()
        spróbuj:
            zwróć os.write(self._fd, b)
        wyjąwszy BlockingIOError:
            zwróć Nic

    def seek(self, pos, whence=SEEK_SET):
        """Move to new file position.

        Argument offset jest a byte count.  Optional argument whence defaults to
        SEEK_SET albo 0 (offset z start of file, offset should be >= 0); other values
        are SEEK_CUR albo 1 (move relative to current position, positive albo negative),
        oraz SEEK_END albo 2 (move relative to end of file, usually negative, although
        many platforms allow seeking beyond the end of a file).

        Note that nie all file objects are seekable.
        """
        jeżeli isinstance(pos, float):
            podnieś TypeError('an integer jest required')
        self._checkClosed()
        zwróć os.lseek(self._fd, pos, whence)

    def tell(self):
        """tell() -> int.  Current file position.

        Can podnieś OSError dla non seekable files."""
        self._checkClosed()
        zwróć os.lseek(self._fd, 0, SEEK_CUR)

    def truncate(self, size=Nic):
        """Truncate the file to at most size bytes.

        Size defaults to the current file position, jako returned by tell().
        The current file position jest changed to the value of size.
        """
        self._checkClosed()
        self._checkWritable()
        jeżeli size jest Nic:
            size = self.tell()
        os.ftruncate(self._fd, size)
        zwróć size

    def close(self):
        """Close the file.

        A closed file cannot be used dla further I/O operations.  close() may be
        called more than once without error.
        """
        jeżeli nie self.closed:
            spróbuj:
                jeżeli self._closefd:
                    os.close(self._fd)
            w_końcu:
                super().close()

    def seekable(self):
        """Prawda jeżeli file supports random-access."""
        self._checkClosed()
        jeżeli self._seekable jest Nic:
            spróbuj:
                self.tell()
            wyjąwszy OSError:
                self._seekable = Nieprawda
            inaczej:
                self._seekable = Prawda
        zwróć self._seekable

    def readable(self):
        """Prawda jeżeli file was opened w a read mode."""
        self._checkClosed()
        zwróć self._readable

    def writable(self):
        """Prawda jeżeli file was opened w a write mode."""
        self._checkClosed()
        zwróć self._writable

    def fileno(self):
        """Return the underlying file descriptor (an integer)."""
        self._checkClosed()
        zwróć self._fd

    def isatty(self):
        """Prawda jeżeli the file jest connected to a TTY device."""
        self._checkClosed()
        zwróć os.isatty(self._fd)

    @property
    def closefd(self):
        """Prawda jeżeli the file descriptor will be closed by close()."""
        zwróć self._closefd

    @property
    def mode(self):
        """String giving the file mode"""
        jeżeli self._created:
            jeżeli self._readable:
                zwróć 'xb+'
            inaczej:
                zwróć 'xb'
        albo_inaczej self._appending:
            jeżeli self._readable:
                zwróć 'ab+'
            inaczej:
                zwróć 'ab'
        albo_inaczej self._readable:
            jeżeli self._writable:
                zwróć 'rb+'
            inaczej:
                zwróć 'rb'
        inaczej:
            zwróć 'wb'


klasa TextIOBase(IOBase):

    """Base klasa dla text I/O.

    This klasa provides a character oraz line based interface to stream
    I/O. There jest no readinto method because Python's character strings
    are immutable. There jest no public constructor.
    """

    def read(self, size=-1):
        """Read at most size characters z stream, where size jest an int.

        Read z underlying buffer until we have size characters albo we hit EOF.
        If size jest negative albo omitted, read until EOF.

        Returns a string.
        """
        self._unsupported("read")

    def write(self, s):
        """Write string s to stream oraz returning an int."""
        self._unsupported("write")

    def truncate(self, pos=Nic):
        """Truncate size to pos, where pos jest an int."""
        self._unsupported("truncate")

    def readline(self):
        """Read until newline albo EOF.

        Returns an empty string jeżeli EOF jest hit immediately.
        """
        self._unsupported("readline")

    def detach(self):
        """
        Separate the underlying buffer z the TextIOBase oraz zwróć it.

        After the underlying buffer has been detached, the TextIO jest w an
        unusable state.
        """
        self._unsupported("detach")

    @property
    def encoding(self):
        """Subclasses should override."""
        zwróć Nic

    @property
    def newlines(self):
        """Line endings translated so far.

        Only line endings translated during reading are considered.

        Subclasses should override.
        """
        zwróć Nic

    @property
    def errors(self):
        """Error setting of the decoder albo encoder.

        Subclasses should override."""
        zwróć Nic

io.TextIOBase.register(TextIOBase)


klasa IncrementalNewlineDecoder(codecs.IncrementalDecoder):
    r"""Codec used when reading a file w universal newlines mode.  It wraps
    another incremental decoder, translating \r\n oraz \r into \n.  It also
    records the types of newlines encountered.  When used with
    translate=Nieprawda, it ensures that the newline sequence jest returned w
    one piece.
    """
    def __init__(self, decoder, translate, errors='strict'):
        codecs.IncrementalDecoder.__init__(self, errors=errors)
        self.translate = translate
        self.decoder = decoder
        self.seennl = 0
        self.pendingcr = Nieprawda

    def decode(self, input, final=Nieprawda):
        # decode input (przy the eventual \r z a previous dalej)
        jeżeli self.decoder jest Nic:
            output = input
        inaczej:
            output = self.decoder.decode(input, final=final)
        jeżeli self.pendingcr oraz (output albo final):
            output = "\r" + output
            self.pendingcr = Nieprawda

        # retain last \r even when nie translating data:
        # then readline() jest sure to get \r\n w one dalej
        jeżeli output.endswith("\r") oraz nie final:
            output = output[:-1]
            self.pendingcr = Prawda

        # Record which newlines are read
        crlf = output.count('\r\n')
        cr = output.count('\r') - crlf
        lf = output.count('\n') - crlf
        self.seennl |= (lf oraz self._LF) | (cr oraz self._CR) \
                    | (crlf oraz self._CRLF)

        jeżeli self.translate:
            jeżeli crlf:
                output = output.replace("\r\n", "\n")
            jeżeli cr:
                output = output.replace("\r", "\n")

        zwróć output

    def getstate(self):
        jeżeli self.decoder jest Nic:
            buf = b""
            flag = 0
        inaczej:
            buf, flag = self.decoder.getstate()
        flag <<= 1
        jeżeli self.pendingcr:
            flag |= 1
        zwróć buf, flag

    def setstate(self, state):
        buf, flag = state
        self.pendingcr = bool(flag & 1)
        jeżeli self.decoder jest nie Nic:
            self.decoder.setstate((buf, flag >> 1))

    def reset(self):
        self.seennl = 0
        self.pendingcr = Nieprawda
        jeżeli self.decoder jest nie Nic:
            self.decoder.reset()

    _LF = 1
    _CR = 2
    _CRLF = 4

    @property
    def newlines(self):
        zwróć (Nic,
                "\n",
                "\r",
                ("\r", "\n"),
                "\r\n",
                ("\n", "\r\n"),
                ("\r", "\r\n"),
                ("\r", "\n", "\r\n")
               )[self.seennl]


klasa TextIOWrapper(TextIOBase):

    r"""Character oraz line based layer over a BufferedIOBase object, buffer.

    encoding gives the name of the encoding that the stream will be
    decoded albo encoded with. It defaults to locale.getpreferredencoding(Nieprawda).

    errors determines the strictness of encoding oraz decoding (see the
    codecs.register) oraz defaults to "strict".

    newline can be Nic, '', '\n', '\r', albo '\r\n'.  It controls the
    handling of line endings. If it jest Nic, universal newlines jest
    enabled.  With this enabled, on input, the lines endings '\n', '\r',
    albo '\r\n' are translated to '\n' before being returned to the
    caller. Conversely, on output, '\n' jest translated to the system
    default line separator, os.linesep. If newline jest any other of its
    legal values, that newline becomes the newline when the file jest read
    oraz it jest returned untranslated. On output, '\n' jest converted to the
    newline.

    If line_buffering jest Prawda, a call to flush jest implied when a call to
    write contains a newline character.
    """

    _CHUNK_SIZE = 2048

    # The write_through argument has no effect here since this
    # implementation always writes through.  The argument jest present only
    # so that the signature can match the signature of the C version.
    def __init__(self, buffer, encoding=Nic, errors=Nic, newline=Nic,
                 line_buffering=Nieprawda, write_through=Nieprawda):
        jeżeli newline jest nie Nic oraz nie isinstance(newline, str):
            podnieś TypeError("illegal newline type: %r" % (type(newline),))
        jeżeli newline nie w (Nic, "", "\n", "\r", "\r\n"):
            podnieś ValueError("illegal newline value: %r" % (newline,))
        jeżeli encoding jest Nic:
            spróbuj:
                encoding = os.device_encoding(buffer.fileno())
            wyjąwszy (AttributeError, UnsupportedOperation):
                dalej
            jeżeli encoding jest Nic:
                spróbuj:
                    zaimportuj locale
                wyjąwszy ImportError:
                    # Importing locale may fail jeżeli Python jest being built
                    encoding = "ascii"
                inaczej:
                    encoding = locale.getpreferredencoding(Nieprawda)

        jeżeli nie isinstance(encoding, str):
            podnieś ValueError("invalid encoding: %r" % encoding)

        jeżeli nie codecs.lookup(encoding)._is_text_encoding:
            msg = ("%r jest nie a text encoding; "
                   "use codecs.open() to handle arbitrary codecs")
            podnieś LookupError(msg % encoding)

        jeżeli errors jest Nic:
            errors = "strict"
        inaczej:
            jeżeli nie isinstance(errors, str):
                podnieś ValueError("invalid errors: %r" % errors)

        self._buffer = buffer
        self._line_buffering = line_buffering
        self._encoding = encoding
        self._errors = errors
        self._readuniversal = nie newline
        self._readtranslate = newline jest Nic
        self._readnl = newline
        self._writetranslate = newline != ''
        self._writenl = newline albo os.linesep
        self._encoder = Nic
        self._decoder = Nic
        self._decoded_chars = ''  # buffer dla text returned z decoder
        self._decoded_chars_used = 0  # offset into _decoded_chars dla read()
        self._snapshot = Nic  # info dla reconstructing decoder state
        self._seekable = self._telling = self.buffer.seekable()
        self._has_read1 = hasattr(self.buffer, 'read1')
        self._b2cratio = 0.0

        jeżeli self._seekable oraz self.writable():
            position = self.buffer.tell()
            jeżeli position != 0:
                spróbuj:
                    self._get_encoder().setstate(0)
                wyjąwszy LookupError:
                    # Sometimes the encoder doesn't exist
                    dalej

    # self._snapshot jest either Nic, albo a tuple (dec_flags, next_input)
    # where dec_flags jest the second (integer) item of the decoder state
    # oraz next_input jest the chunk of input bytes that comes next after the
    # snapshot point.  We use this to reconstruct decoder states w tell().

    # Naming convention:
    #   - "bytes_..." dla integer variables that count input bytes
    #   - "chars_..." dla integer variables that count decoded characters

    def __repr__(self):
        result = "<{}.{}".format(self.__class__.__module__,
                                 self.__class__.__qualname__)
        spróbuj:
            name = self.name
        wyjąwszy Exception:
            dalej
        inaczej:
            result += " name={0!r}".format(name)
        spróbuj:
            mode = self.mode
        wyjąwszy Exception:
            dalej
        inaczej:
            result += " mode={0!r}".format(mode)
        zwróć result + " encoding={0!r}>".format(self.encoding)

    @property
    def encoding(self):
        zwróć self._encoding

    @property
    def errors(self):
        zwróć self._errors

    @property
    def line_buffering(self):
        zwróć self._line_buffering

    @property
    def buffer(self):
        zwróć self._buffer

    def seekable(self):
        jeżeli self.closed:
            podnieś ValueError("I/O operation on closed file.")
        zwróć self._seekable

    def readable(self):
        zwróć self.buffer.readable()

    def writable(self):
        zwróć self.buffer.writable()

    def flush(self):
        self.buffer.flush()
        self._telling = self._seekable

    def close(self):
        jeżeli self.buffer jest nie Nic oraz nie self.closed:
            spróbuj:
                self.flush()
            w_końcu:
                self.buffer.close()

    @property
    def closed(self):
        zwróć self.buffer.closed

    @property
    def name(self):
        zwróć self.buffer.name

    def fileno(self):
        zwróć self.buffer.fileno()

    def isatty(self):
        zwróć self.buffer.isatty()

    def write(self, s):
        'Write data, where s jest a str'
        jeżeli self.closed:
            podnieś ValueError("write to closed file")
        jeżeli nie isinstance(s, str):
            podnieś TypeError("can't write %s to text stream" %
                            s.__class__.__name__)
        length = len(s)
        haslf = (self._writetranslate albo self._line_buffering) oraz "\n" w s
        jeżeli haslf oraz self._writetranslate oraz self._writenl != "\n":
            s = s.replace("\n", self._writenl)
        encoder = self._encoder albo self._get_encoder()
        # XXX What jeżeli we were just reading?
        b = encoder.encode(s)
        self.buffer.write(b)
        jeżeli self._line_buffering oraz (haslf albo "\r" w s):
            self.flush()
        self._snapshot = Nic
        jeżeli self._decoder:
            self._decoder.reset()
        zwróć length

    def _get_encoder(self):
        make_encoder = codecs.getincrementalencoder(self._encoding)
        self._encoder = make_encoder(self._errors)
        zwróć self._encoder

    def _get_decoder(self):
        make_decoder = codecs.getincrementaldecoder(self._encoding)
        decoder = make_decoder(self._errors)
        jeżeli self._readuniversal:
            decoder = IncrementalNewlineDecoder(decoder, self._readtranslate)
        self._decoder = decoder
        zwróć decoder

    # The following three methods implement an ADT dla _decoded_chars.
    # Text returned z the decoder jest buffered here until the client
    # requests it by calling our read() albo readline() method.
    def _set_decoded_chars(self, chars):
        """Set the _decoded_chars buffer."""
        self._decoded_chars = chars
        self._decoded_chars_used = 0

    def _get_decoded_chars(self, n=Nic):
        """Advance into the _decoded_chars buffer."""
        offset = self._decoded_chars_used
        jeżeli n jest Nic:
            chars = self._decoded_chars[offset:]
        inaczej:
            chars = self._decoded_chars[offset:offset + n]
        self._decoded_chars_used += len(chars)
        zwróć chars

    def _rewind_decoded_chars(self, n):
        """Rewind the _decoded_chars buffer."""
        jeżeli self._decoded_chars_used < n:
            podnieś AssertionError("rewind decoded_chars out of bounds")
        self._decoded_chars_used -= n

    def _read_chunk(self):
        """
        Read oraz decode the next chunk of data z the BufferedReader.
        """

        # The zwróć value jest Prawda unless EOF was reached.  The decoded
        # string jest placed w self._decoded_chars (replacing its previous
        # value).  The entire input chunk jest sent to the decoder, though
        # some of it may remain buffered w the decoder, yet to be
        # converted.

        jeżeli self._decoder jest Nic:
            podnieś ValueError("no decoder")

        jeżeli self._telling:
            # To prepare dla tell(), we need to snapshot a point w the
            # file where the decoder's input buffer jest empty.

            dec_buffer, dec_flags = self._decoder.getstate()
            # Given this, we know there was a valid snapshot point
            # len(dec_buffer) bytes ago przy decoder state (b'', dec_flags).

        # Read a chunk, decode it, oraz put the result w self._decoded_chars.
        jeżeli self._has_read1:
            input_chunk = self.buffer.read1(self._CHUNK_SIZE)
        inaczej:
            input_chunk = self.buffer.read(self._CHUNK_SIZE)
        eof = nie input_chunk
        decoded_chars = self._decoder.decode(input_chunk, eof)
        self._set_decoded_chars(decoded_chars)
        jeżeli decoded_chars:
            self._b2cratio = len(input_chunk) / len(self._decoded_chars)
        inaczej:
            self._b2cratio = 0.0

        jeżeli self._telling:
            # At the snapshot point, len(dec_buffer) bytes before the read,
            # the next input to be decoded jest dec_buffer + input_chunk.
            self._snapshot = (dec_flags, dec_buffer + input_chunk)

        zwróć nie eof

    def _pack_cookie(self, position, dec_flags=0,
                           bytes_to_feed=0, need_eof=0, chars_to_skip=0):
        # The meaning of a tell() cookie is: seek to position, set the
        # decoder flags to dec_flags, read bytes_to_feed bytes, feed them
        # into the decoder przy need_eof jako the EOF flag, then skip
        # chars_to_skip characters of the decoded result.  For most simple
        # decoders, tell() will often just give a byte offset w the file.
        zwróć (position | (dec_flags<<64) | (bytes_to_feed<<128) |
               (chars_to_skip<<192) | bool(need_eof)<<256)

    def _unpack_cookie(self, bigint):
        rest, position = divmod(bigint, 1<<64)
        rest, dec_flags = divmod(rest, 1<<64)
        rest, bytes_to_feed = divmod(rest, 1<<64)
        need_eof, chars_to_skip = divmod(rest, 1<<64)
        zwróć position, dec_flags, bytes_to_feed, need_eof, chars_to_skip

    def tell(self):
        jeżeli nie self._seekable:
            podnieś UnsupportedOperation("underlying stream jest nie seekable")
        jeżeli nie self._telling:
            podnieś OSError("telling position disabled by next() call")
        self.flush()
        position = self.buffer.tell()
        decoder = self._decoder
        jeżeli decoder jest Nic albo self._snapshot jest Nic:
            jeżeli self._decoded_chars:
                # This should never happen.
                podnieś AssertionError("pending decoded text")
            zwróć position

        # Skip backward to the snapshot point (see _read_chunk).
        dec_flags, next_input = self._snapshot
        position -= len(next_input)

        # How many decoded characters have been used up since the snapshot?
        chars_to_skip = self._decoded_chars_used
        jeżeli chars_to_skip == 0:
            # We haven't moved z the snapshot point.
            zwróć self._pack_cookie(position, dec_flags)

        # Starting z the snapshot position, we will walk the decoder
        # forward until it gives us enough decoded characters.
        saved_state = decoder.getstate()
        spróbuj:
            # Fast search dla an acceptable start point, close to our
            # current pos.
            # Rationale: calling decoder.decode() has a large overhead
            # regardless of chunk size; we want the number of such calls to
            # be O(1) w most situations (common decoders, non-crazy input).
            # Actually, it will be exactly 1 dla fixed-size codecs (all
            # 8-bit codecs, also UTF-16 oraz UTF-32).
            skip_bytes = int(self._b2cratio * chars_to_skip)
            skip_back = 1
            assert skip_bytes <= len(next_input)
            dopóki skip_bytes > 0:
                decoder.setstate((b'', dec_flags))
                # Decode up to temptative start point
                n = len(decoder.decode(next_input[:skip_bytes]))
                jeżeli n <= chars_to_skip:
                    b, d = decoder.getstate()
                    jeżeli nie b:
                        # Before pos oraz no bytes buffered w decoder => OK
                        dec_flags = d
                        chars_to_skip -= n
                        przerwij
                    # Skip back by buffered amount oraz reset heuristic
                    skip_bytes -= len(b)
                    skip_back = 1
                inaczej:
                    # We're too far ahead, skip back a bit
                    skip_bytes -= skip_back
                    skip_back = skip_back * 2
            inaczej:
                skip_bytes = 0
                decoder.setstate((b'', dec_flags))

            # Note our initial start point.
            start_pos = position + skip_bytes
            start_flags = dec_flags
            jeżeli chars_to_skip == 0:
                # We haven't moved z the start point.
                zwróć self._pack_cookie(start_pos, start_flags)

            # Feed the decoder one byte at a time.  As we go, note the
            # nearest "safe start point" before the current location
            # (a point where the decoder has nothing buffered, so seek()
            # can safely start z there oraz advance to this location).
            bytes_fed = 0
            need_eof = 0
            # Chars decoded since `start_pos`
            chars_decoded = 0
            dla i w range(skip_bytes, len(next_input)):
                bytes_fed += 1
                chars_decoded += len(decoder.decode(next_input[i:i+1]))
                dec_buffer, dec_flags = decoder.getstate()
                jeżeli nie dec_buffer oraz chars_decoded <= chars_to_skip:
                    # Decoder buffer jest empty, so this jest a safe start point.
                    start_pos += bytes_fed
                    chars_to_skip -= chars_decoded
                    start_flags, bytes_fed, chars_decoded = dec_flags, 0, 0
                jeżeli chars_decoded >= chars_to_skip:
                    przerwij
            inaczej:
                # We didn't get enough decoded data; signal EOF to get more.
                chars_decoded += len(decoder.decode(b'', final=Prawda))
                need_eof = 1
                jeżeli chars_decoded < chars_to_skip:
                    podnieś OSError("can't reconstruct logical file position")

            # The returned cookie corresponds to the last safe start point.
            zwróć self._pack_cookie(
                start_pos, start_flags, bytes_fed, need_eof, chars_to_skip)
        w_końcu:
            decoder.setstate(saved_state)

    def truncate(self, pos=Nic):
        self.flush()
        jeżeli pos jest Nic:
            pos = self.tell()
        zwróć self.buffer.truncate(pos)

    def detach(self):
        jeżeli self.buffer jest Nic:
            podnieś ValueError("buffer jest already detached")
        self.flush()
        buffer = self._buffer
        self._buffer = Nic
        zwróć buffer

    def seek(self, cookie, whence=0):
        def _reset_encoder(position):
            """Reset the encoder (merely useful dla proper BOM handling)"""
            spróbuj:
                encoder = self._encoder albo self._get_encoder()
            wyjąwszy LookupError:
                # Sometimes the encoder doesn't exist
                dalej
            inaczej:
                jeżeli position != 0:
                    encoder.setstate(0)
                inaczej:
                    encoder.reset()

        jeżeli self.closed:
            podnieś ValueError("tell on closed file")
        jeżeli nie self._seekable:
            podnieś UnsupportedOperation("underlying stream jest nie seekable")
        jeżeli whence == 1: # seek relative to current position
            jeżeli cookie != 0:
                podnieś UnsupportedOperation("can't do nonzero cur-relative seeks")
            # Seeking to the current position should attempt to
            # sync the underlying buffer przy the current position.
            whence = 0
            cookie = self.tell()
        jeżeli whence == 2: # seek relative to end of file
            jeżeli cookie != 0:
                podnieś UnsupportedOperation("can't do nonzero end-relative seeks")
            self.flush()
            position = self.buffer.seek(0, 2)
            self._set_decoded_chars('')
            self._snapshot = Nic
            jeżeli self._decoder:
                self._decoder.reset()
            _reset_encoder(position)
            zwróć position
        jeżeli whence != 0:
            podnieś ValueError("unsupported whence (%r)" % (whence,))
        jeżeli cookie < 0:
            podnieś ValueError("negative seek position %r" % (cookie,))
        self.flush()

        # The strategy of seek() jest to go back to the safe start point
        # oraz replay the effect of read(chars_to_skip) z there.
        start_pos, dec_flags, bytes_to_feed, need_eof, chars_to_skip = \
            self._unpack_cookie(cookie)

        # Seek back to the safe start point.
        self.buffer.seek(start_pos)
        self._set_decoded_chars('')
        self._snapshot = Nic

        # Restore the decoder to its state z the safe start point.
        jeżeli cookie == 0 oraz self._decoder:
            self._decoder.reset()
        albo_inaczej self._decoder albo dec_flags albo chars_to_skip:
            self._decoder = self._decoder albo self._get_decoder()
            self._decoder.setstate((b'', dec_flags))
            self._snapshot = (dec_flags, b'')

        jeżeli chars_to_skip:
            # Just like _read_chunk, feed the decoder oraz save a snapshot.
            input_chunk = self.buffer.read(bytes_to_feed)
            self._set_decoded_chars(
                self._decoder.decode(input_chunk, need_eof))
            self._snapshot = (dec_flags, input_chunk)

            # Skip chars_to_skip of the decoded characters.
            jeżeli len(self._decoded_chars) < chars_to_skip:
                podnieś OSError("can't restore logical file position")
            self._decoded_chars_used = chars_to_skip

        _reset_encoder(cookie)
        zwróć cookie

    def read(self, size=Nic):
        self._checkReadable()
        jeżeli size jest Nic:
            size = -1
        decoder = self._decoder albo self._get_decoder()
        spróbuj:
            size.__index__
        wyjąwszy AttributeError jako err:
            podnieś TypeError("an integer jest required") z err
        jeżeli size < 0:
            # Read everything.
            result = (self._get_decoded_chars() +
                      decoder.decode(self.buffer.read(), final=Prawda))
            self._set_decoded_chars('')
            self._snapshot = Nic
            zwróć result
        inaczej:
            # Keep reading chunks until we have size characters to return.
            eof = Nieprawda
            result = self._get_decoded_chars(size)
            dopóki len(result) < size oraz nie eof:
                eof = nie self._read_chunk()
                result += self._get_decoded_chars(size - len(result))
            zwróć result

    def __next__(self):
        self._telling = Nieprawda
        line = self.readline()
        jeżeli nie line:
            self._snapshot = Nic
            self._telling = self._seekable
            podnieś StopIteration
        zwróć line

    def readline(self, size=Nic):
        jeżeli self.closed:
            podnieś ValueError("read z closed file")
        jeżeli size jest Nic:
            size = -1
        albo_inaczej nie isinstance(size, int):
            podnieś TypeError("size must be an integer")

        # Grab all the decoded text (we will rewind any extra bits later).
        line = self._get_decoded_chars()

        start = 0
        # Make the decoder jeżeli it doesn't already exist.
        jeżeli nie self._decoder:
            self._get_decoder()

        pos = endpos = Nic
        dopóki Prawda:
            jeżeli self._readtranslate:
                # Newlines are already translated, only search dla \n
                pos = line.find('\n', start)
                jeżeli pos >= 0:
                    endpos = pos + 1
                    przerwij
                inaczej:
                    start = len(line)

            albo_inaczej self._readuniversal:
                # Universal newline search. Find any of \r, \r\n, \n
                # The decoder ensures that \r\n are nie split w two pieces

                # In C we'd look dla these w parallel of course.
                nlpos = line.find("\n", start)
                crpos = line.find("\r", start)
                jeżeli crpos == -1:
                    jeżeli nlpos == -1:
                        # Nothing found
                        start = len(line)
                    inaczej:
                        # Found \n
                        endpos = nlpos + 1
                        przerwij
                albo_inaczej nlpos == -1:
                    # Found lone \r
                    endpos = crpos + 1
                    przerwij
                albo_inaczej nlpos < crpos:
                    # Found \n
                    endpos = nlpos + 1
                    przerwij
                albo_inaczej nlpos == crpos + 1:
                    # Found \r\n
                    endpos = crpos + 2
                    przerwij
                inaczej:
                    # Found \r
                    endpos = crpos + 1
                    przerwij
            inaczej:
                # non-universal
                pos = line.find(self._readnl)
                jeżeli pos >= 0:
                    endpos = pos + len(self._readnl)
                    przerwij

            jeżeli size >= 0 oraz len(line) >= size:
                endpos = size  # reached length size
                przerwij

            # No line ending seen yet - get more data'
            dopóki self._read_chunk():
                jeżeli self._decoded_chars:
                    przerwij
            jeżeli self._decoded_chars:
                line += self._get_decoded_chars()
            inaczej:
                # end of file
                self._set_decoded_chars('')
                self._snapshot = Nic
                zwróć line

        jeżeli size >= 0 oraz endpos > size:
            endpos = size  # don't exceed size

        # Rewind _decoded_chars to just after the line ending we found.
        self._rewind_decoded_chars(len(line) - endpos)
        zwróć line[:endpos]

    @property
    def newlines(self):
        zwróć self._decoder.newlines jeżeli self._decoder inaczej Nic


klasa StringIO(TextIOWrapper):
    """Text I/O implementation using an in-memory buffer.

    The initial_value argument sets the value of object.  The newline
    argument jest like the one of TextIOWrapper's constructor.
    """

    def __init__(self, initial_value="", newline="\n"):
        super(StringIO, self).__init__(BytesIO(),
                                       encoding="utf-8",
                                       errors="surrogatepass",
                                       newline=newline)
        # Issue #5645: make universal newlines semantics the same jako w the
        # C version, even under Windows.
        jeżeli newline jest Nic:
            self._writetranslate = Nieprawda
        jeżeli initial_value jest nie Nic:
            jeżeli nie isinstance(initial_value, str):
                podnieś TypeError("initial_value must be str albo Nic, nie {0}"
                                .format(type(initial_value).__name__))
            self.write(initial_value)
            self.seek(0)

    def getvalue(self):
        self.flush()
        decoder = self._decoder albo self._get_decoder()
        old_state = decoder.getstate()
        decoder.reset()
        spróbuj:
            zwróć decoder.decode(self.buffer.getvalue(), final=Prawda)
        w_końcu:
            decoder.setstate(old_state)

    def __repr__(self):
        # TextIOWrapper tells the encoding w its repr. In StringIO,
        # that's a implementation detail.
        zwróć object.__repr__(self)

    @property
    def errors(self):
        zwróć Nic

    @property
    def encoding(self):
        zwróć Nic

    def detach(self):
        # This doesn't make sense on StringIO.
        self._unsupported("detach")
