"""The io module provides the Python interfaces to stream handling. The
builtin open function jest defined w this module.

At the top of the I/O hierarchy jest the abstract base klasa IOBase. It
defines the basic interface to a stream. Note, however, that there jest no
separation between reading oraz writing to streams; implementations are
allowed to podnieś an OSError jeżeli they do nie support a given operation.

Extending IOBase jest RawIOBase which deals simply przy the reading oraz
writing of raw bytes to a stream. FileIO subclasses RawIOBase to provide
an interface to OS files.

BufferedIOBase deals przy buffering on a raw byte stream (RawIOBase). Its
subclasses, BufferedWriter, BufferedReader, oraz BufferedRWPair buffer
streams that are readable, writable, oraz both respectively.
BufferedRandom provides a buffered interface to random access
streams. BytesIO jest a simple stream of in-memory bytes.

Another IOBase subclass, TextIOBase, deals przy the encoding oraz decoding
of streams into text. TextIOWrapper, which extends it, jest a buffered text
interface to a buffered raw stream (`BufferedIOBase`). Finally, StringIO
is a in-memory stream dla text.

Argument names are nie part of the specification, oraz only the arguments
of open() are intended to be used jako keyword arguments.

data:

DEFAULT_BUFFER_SIZE

   An int containing the default buffer size used by the module's buffered
   I/O classes. open() uses the file's blksize (as obtained by os.stat) if
   possible.
"""
# New I/O library conforming to PEP 3116.

__author__ = ("Guido van Rossum <guido@python.org>, "
              "Mike Verdone <mike.verdone@gmail.com>, "
              "Mark Russell <mark.russell@zen.co.uk>, "
              "Antoine Pitrou <solipsis@pitrou.net>, "
              "Amaury Forgeot d'Arc <amauryfa@gmail.com>, "
              "Benjamin Peterson <benjamin@python.org>")

__all__ = ["BlockingIOError", "open", "IOBase", "RawIOBase", "FileIO",
           "BytesIO", "StringIO", "BufferedIOBase",
           "BufferedReader", "BufferedWriter", "BufferedRWPair",
           "BufferedRandom", "TextIOBase", "TextIOWrapper",
           "UnsupportedOperation", "SEEK_SET", "SEEK_CUR", "SEEK_END"]


zaimportuj _io
zaimportuj abc

z _io zaimportuj (DEFAULT_BUFFER_SIZE, BlockingIOError, UnsupportedOperation,
                 open, FileIO, BytesIO, StringIO, BufferedReader,
                 BufferedWriter, BufferedRWPair, BufferedRandom,
                 IncrementalNewlineDecoder, TextIOWrapper)

OpenWrapper = _io.open # dla compatibility przy _pyio

# Pretend this exception was created here.
UnsupportedOperation.__module__ = "io"

# dla seek()
SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2

# Declaring ABCs w C jest tricky so we do it here.
# Method descriptions oraz default implementations are inherited z the C
# version however.
klasa IOBase(_io._IOBase, metaclass=abc.ABCMeta):
    __doc__ = _io._IOBase.__doc__

klasa RawIOBase(_io._RawIOBase, IOBase):
    __doc__ = _io._RawIOBase.__doc__

klasa BufferedIOBase(_io._BufferedIOBase, IOBase):
    __doc__ = _io._BufferedIOBase.__doc__

klasa TextIOBase(_io._TextIOBase, IOBase):
    __doc__ = _io._TextIOBase.__doc__

RawIOBase.register(FileIO)

dla klass w (BytesIO, BufferedReader, BufferedWriter, BufferedRandom,
              BufferedRWPair):
    BufferedIOBase.register(klass)

dla klass w (StringIO, TextIOWrapper):
    TextIOBase.register(klass)
usuń klass
