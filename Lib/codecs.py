""" codecs -- Python Codec Registry, API oraz helpers.


Written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""#"

zaimportuj builtins, sys

### Registry oraz builtin stateless codec functions

spróbuj:
    z _codecs zaimportuj *
wyjąwszy ImportError jako why:
    podnieś SystemError('Failed to load the builtin codecs: %s' % why)

__all__ = ["register", "lookup", "open", "EncodedFile", "BOM", "BOM_BE",
           "BOM_LE", "BOM32_BE", "BOM32_LE", "BOM64_BE", "BOM64_LE",
           "BOM_UTF8", "BOM_UTF16", "BOM_UTF16_LE", "BOM_UTF16_BE",
           "BOM_UTF32", "BOM_UTF32_LE", "BOM_UTF32_BE",
           "CodecInfo", "Codec", "IncrementalEncoder", "IncrementalDecoder",
           "StreamReader", "StreamWriter",
           "StreamReaderWriter", "StreamRecoder",
           "getencoder", "getdecoder", "getincrementalencoder",
           "getincrementaldecoder", "getreader", "getwriter",
           "encode", "decode", "iterencode", "iterdecode",
           "strict_errors", "ignore_errors", "replace_errors",
           "xmlcharrefreplace_errors",
           "backslashreplace_errors", "namereplace_errors",
           "register_error", "lookup_error"]

### Constants

#
# Byte Order Mark (BOM = ZERO WIDTH NO-BREAK SPACE = U+FEFF)
# oraz its possible byte string values
# dla UTF8/UTF16/UTF32 output oraz little/big endian machines
#

# UTF-8
BOM_UTF8 = b'\xef\xbb\xbf'

# UTF-16, little endian
BOM_LE = BOM_UTF16_LE = b'\xff\xfe'

# UTF-16, big endian
BOM_BE = BOM_UTF16_BE = b'\xfe\xff'

# UTF-32, little endian
BOM_UTF32_LE = b'\xff\xfe\x00\x00'

# UTF-32, big endian
BOM_UTF32_BE = b'\x00\x00\xfe\xff'

jeżeli sys.byteorder == 'little':

    # UTF-16, native endianness
    BOM = BOM_UTF16 = BOM_UTF16_LE

    # UTF-32, native endianness
    BOM_UTF32 = BOM_UTF32_LE

inaczej:

    # UTF-16, native endianness
    BOM = BOM_UTF16 = BOM_UTF16_BE

    # UTF-32, native endianness
    BOM_UTF32 = BOM_UTF32_BE

# Old broken names (don't use w new code)
BOM32_LE = BOM_UTF16_LE
BOM32_BE = BOM_UTF16_BE
BOM64_LE = BOM_UTF32_LE
BOM64_BE = BOM_UTF32_BE


### Codec base classes (defining the API)

klasa CodecInfo(tuple):
    """Codec details when looking up the codec registry"""

    # Private API to allow Python 3.4 to blacklist the known non-Unicode
    # codecs w the standard library. A more general mechanism to
    # reliably distinguish test encodings z other codecs will hopefully
    # be defined dla Python 3.5
    #
    # See http://bugs.python.org/issue19619
    _is_text_encoding = Prawda # Assume codecs are text encodings by default

    def __new__(cls, encode, decode, streamreader=Nic, streamwriter=Nic,
        incrementalencoder=Nic, incrementaldecoder=Nic, name=Nic,
        *, _is_text_encoding=Nic):
        self = tuple.__new__(cls, (encode, decode, streamreader, streamwriter))
        self.name = name
        self.encode = encode
        self.decode = decode
        self.incrementalencoder = incrementalencoder
        self.incrementaldecoder = incrementaldecoder
        self.streamwriter = streamwriter
        self.streamreader = streamreader
        jeżeli _is_text_encoding jest nie Nic:
            self._is_text_encoding = _is_text_encoding
        zwróć self

    def __repr__(self):
        zwróć "<%s.%s object dla encoding %s at %#x>" % \
                (self.__class__.__module__, self.__class__.__qualname__,
                 self.name, id(self))

klasa Codec:

    """ Defines the interface dla stateless encoders/decoders.

        The .encode()/.decode() methods may use different error
        handling schemes by providing the errors argument. These
        string values are predefined:

         'strict' - podnieś a ValueError error (or a subclass)
         'ignore' - ignore the character oraz continue przy the next
         'replace' - replace przy a suitable replacement character;
                    Python will use the official U+FFFD REPLACEMENT
                    CHARACTER dla the builtin Unicode codecs on
                    decoding oraz '?' on encoding.
         'surrogateescape' - replace przy private code points U+DCnn.
         'xmlcharrefreplace' - Replace przy the appropriate XML
                               character reference (only dla encoding).
         'backslashreplace'  - Replace przy backslashed escape sequences.
         'namereplace'       - Replace przy \\N{...} escape sequences
                               (only dla encoding).

        The set of allowed values can be extended via register_error.

    """
    def encode(self, input, errors='strict'):

        """ Encodes the object input oraz returns a tuple (output
            object, length consumed).

            errors defines the error handling to apply. It defaults to
            'strict' handling.

            The method may nie store state w the Codec instance. Use
            StreamWriter dla codecs which have to keep state w order to
            make encoding efficient.

            The encoder must be able to handle zero length input oraz
            zwróć an empty object of the output object type w this
            situation.

        """
        podnieś NotImplementedError

    def decode(self, input, errors='strict'):

        """ Decodes the object input oraz returns a tuple (output
            object, length consumed).

            input must be an object which provides the bf_getreadbuf
            buffer slot. Python strings, buffer objects oraz memory
            mapped files are examples of objects providing this slot.

            errors defines the error handling to apply. It defaults to
            'strict' handling.

            The method may nie store state w the Codec instance. Use
            StreamReader dla codecs which have to keep state w order to
            make decoding efficient.

            The decoder must be able to handle zero length input oraz
            zwróć an empty object of the output object type w this
            situation.

        """
        podnieś NotImplementedError

klasa IncrementalEncoder(object):
    """
    An IncrementalEncoder encodes an input w multiple steps. The input can
    be dalejed piece by piece to the encode() method. The IncrementalEncoder
    remembers the state of the encoding process between calls to encode().
    """
    def __init__(self, errors='strict'):
        """
        Creates an IncrementalEncoder instance.

        The IncrementalEncoder may use different error handling schemes by
        providing the errors keyword argument. See the module docstring
        dla a list of possible values.
        """
        self.errors = errors
        self.buffer = ""

    def encode(self, input, final=Nieprawda):
        """
        Encodes input oraz returns the resulting object.
        """
        podnieś NotImplementedError

    def reset(self):
        """
        Resets the encoder to the initial state.
        """

    def getstate(self):
        """
        Return the current state of the encoder.
        """
        zwróć 0

    def setstate(self, state):
        """
        Set the current state of the encoder. state must have been
        returned by getstate().
        """

klasa BufferedIncrementalEncoder(IncrementalEncoder):
    """
    This subclass of IncrementalEncoder can be used jako the baseclass dla an
    incremental encoder jeżeli the encoder must keep some of the output w a
    buffer between calls to encode().
    """
    def __init__(self, errors='strict'):
        IncrementalEncoder.__init__(self, errors)
        # unencoded input that jest kept between calls to encode()
        self.buffer = ""

    def _buffer_encode(self, input, errors, final):
        # Overwrite this method w subclasses: It must encode input
        # oraz zwróć an (output, length consumed) tuple
        podnieś NotImplementedError

    def encode(self, input, final=Nieprawda):
        # encode input (taking the buffer into account)
        data = self.buffer + input
        (result, consumed) = self._buffer_encode(data, self.errors, final)
        # keep unencoded input until the next call
        self.buffer = data[consumed:]
        zwróć result

    def reset(self):
        IncrementalEncoder.reset(self)
        self.buffer = ""

    def getstate(self):
        zwróć self.buffer albo 0

    def setstate(self, state):
        self.buffer = state albo ""

klasa IncrementalDecoder(object):
    """
    An IncrementalDecoder decodes an input w multiple steps. The input can
    be dalejed piece by piece to the decode() method. The IncrementalDecoder
    remembers the state of the decoding process between calls to decode().
    """
    def __init__(self, errors='strict'):
        """
        Create a IncrementalDecoder instance.

        The IncrementalDecoder may use different error handling schemes by
        providing the errors keyword argument. See the module docstring
        dla a list of possible values.
        """
        self.errors = errors

    def decode(self, input, final=Nieprawda):
        """
        Decode input oraz returns the resulting object.
        """
        podnieś NotImplementedError

    def reset(self):
        """
        Reset the decoder to the initial state.
        """

    def getstate(self):
        """
        Return the current state of the decoder.

        This must be a (buffered_input, additional_state_info) tuple.
        buffered_input must be a bytes object containing bytes that
        were dalejed to decode() that have nie yet been converted.
        additional_state_info must be a non-negative integer
        representing the state of the decoder WITHOUT yet having
        processed the contents of buffered_input.  In the initial state
        oraz after reset(), getstate() must zwróć (b"", 0).
        """
        zwróć (b"", 0)

    def setstate(self, state):
        """
        Set the current state of the decoder.

        state must have been returned by getstate().  The effect of
        setstate((b"", 0)) must be equivalent to reset().
        """

klasa BufferedIncrementalDecoder(IncrementalDecoder):
    """
    This subclass of IncrementalDecoder can be used jako the baseclass dla an
    incremental decoder jeżeli the decoder must be able to handle incomplete
    byte sequences.
    """
    def __init__(self, errors='strict'):
        IncrementalDecoder.__init__(self, errors)
        # undecoded input that jest kept between calls to decode()
        self.buffer = b""

    def _buffer_decode(self, input, errors, final):
        # Overwrite this method w subclasses: It must decode input
        # oraz zwróć an (output, length consumed) tuple
        podnieś NotImplementedError

    def decode(self, input, final=Nieprawda):
        # decode input (taking the buffer into account)
        data = self.buffer + input
        (result, consumed) = self._buffer_decode(data, self.errors, final)
        # keep undecoded input until the next call
        self.buffer = data[consumed:]
        zwróć result

    def reset(self):
        IncrementalDecoder.reset(self)
        self.buffer = b""

    def getstate(self):
        # additional state info jest always 0
        zwróć (self.buffer, 0)

    def setstate(self, state):
        # ignore additional state info
        self.buffer = state[0]

#
# The StreamWriter oraz StreamReader klasa provide generic working
# interfaces which can be used to implement new encoding submodules
# very easily. See encodings/utf_8.py dla an example on how this jest
# done.
#

klasa StreamWriter(Codec):

    def __init__(self, stream, errors='strict'):

        """ Creates a StreamWriter instance.

            stream must be a file-like object open dla writing.

            The StreamWriter may use different error handling
            schemes by providing the errors keyword argument. These
            parameters are predefined:

             'strict' - podnieś a ValueError (or a subclass)
             'ignore' - ignore the character oraz continue przy the next
             'replace'- replace przy a suitable replacement character
             'xmlcharrefreplace' - Replace przy the appropriate XML
                                   character reference.
             'backslashreplace'  - Replace przy backslashed escape
                                   sequences.
             'namereplace'       - Replace przy \\N{...} escape sequences.

            The set of allowed parameter values can be extended via
            register_error.
        """
        self.stream = stream
        self.errors = errors

    def write(self, object):

        """ Writes the object's contents encoded to self.stream.
        """
        data, consumed = self.encode(object, self.errors)
        self.stream.write(data)

    def writelines(self, list):

        """ Writes the concatenated list of strings to the stream
            using .write().
        """
        self.write(''.join(list))

    def reset(self):

        """ Flushes oraz resets the codec buffers used dla keeping state.

            Calling this method should ensure that the data on the
            output jest put into a clean state, that allows appending
            of new fresh data without having to rescan the whole
            stream to recover state.

        """
        dalej

    def seek(self, offset, whence=0):
        self.stream.seek(offset, whence)
        jeżeli whence == 0 oraz offset == 0:
            self.reset()

    def __getattr__(self, name,
                    getattr=getattr):

        """ Inherit all other methods z the underlying stream.
        """
        zwróć getattr(self.stream, name)

    def __enter__(self):
        zwróć self

    def __exit__(self, type, value, tb):
        self.stream.close()

###

klasa StreamReader(Codec):

    charbuffertype = str

    def __init__(self, stream, errors='strict'):

        """ Creates a StreamReader instance.

            stream must be a file-like object open dla reading.

            The StreamReader may use different error handling
            schemes by providing the errors keyword argument. These
            parameters are predefined:

             'strict' - podnieś a ValueError (or a subclass)
             'ignore' - ignore the character oraz continue przy the next
             'replace'- replace przy a suitable replacement character
             'backslashreplace' - Replace przy backslashed escape sequences;

            The set of allowed parameter values can be extended via
            register_error.
        """
        self.stream = stream
        self.errors = errors
        self.bytebuffer = b""
        self._empty_charbuffer = self.charbuffertype()
        self.charbuffer = self._empty_charbuffer
        self.linebuffer = Nic

    def decode(self, input, errors='strict'):
        podnieś NotImplementedError

    def read(self, size=-1, chars=-1, firstline=Nieprawda):

        """ Decodes data z the stream self.stream oraz returns the
            resulting object.

            chars indicates the number of decoded code points albo bytes to
            return. read() will never zwróć more data than requested,
            but it might zwróć less, jeżeli there jest nie enough available.

            size indicates the approximate maximum number of decoded
            bytes albo code points to read dla decoding. The decoder
            can modify this setting jako appropriate. The default value
            -1 indicates to read oraz decode jako much jako possible.  size
            jest intended to prevent having to decode huge files w one
            step.

            If firstline jest true, oraz a UnicodeDecodeError happens
            after the first line terminator w the input only the first line
            will be returned, the rest of the input will be kept until the
            next call to read().

            The method should use a greedy read strategy, meaning that
            it should read jako much data jako jest allowed within the
            definition of the encoding oraz the given size, e.g.  if
            optional encoding endings albo state markers are available
            on the stream, these should be read too.
        """
        # If we have lines cached, first merge them back into characters
        jeżeli self.linebuffer:
            self.charbuffer = self._empty_charbuffer.join(self.linebuffer)
            self.linebuffer = Nic

        # read until we get the required number of characters (jeżeli available)
        dopóki Prawda:
            # can the request be satisfied z the character buffer?
            jeżeli chars >= 0:
                jeżeli len(self.charbuffer) >= chars:
                    przerwij
            albo_inaczej size >= 0:
                jeżeli len(self.charbuffer) >= size:
                    przerwij
            # we need more data
            jeżeli size < 0:
                newdata = self.stream.read()
            inaczej:
                newdata = self.stream.read(size)
            # decode bytes (those remaining z the last call included)
            data = self.bytebuffer + newdata
            jeżeli nie data:
                przerwij
            spróbuj:
                newchars, decodedbytes = self.decode(data, self.errors)
            wyjąwszy UnicodeDecodeError jako exc:
                jeżeli firstline:
                    newchars, decodedbytes = \
                        self.decode(data[:exc.start], self.errors)
                    lines = newchars.splitlines(keepends=Prawda)
                    jeżeli len(lines)<=1:
                        podnieś
                inaczej:
                    podnieś
            # keep undecoded bytes until the next call
            self.bytebuffer = data[decodedbytes:]
            # put new characters w the character buffer
            self.charbuffer += newchars
            # there was no data available
            jeżeli nie newdata:
                przerwij
        jeżeli chars < 0:
            # Return everything we've got
            result = self.charbuffer
            self.charbuffer = self._empty_charbuffer
        inaczej:
            # Return the first chars characters
            result = self.charbuffer[:chars]
            self.charbuffer = self.charbuffer[chars:]
        zwróć result

    def readline(self, size=Nic, keepends=Prawda):

        """ Read one line z the input stream oraz zwróć the
            decoded data.

            size, jeżeli given, jest dalejed jako size argument to the
            read() method.

        """
        # If we have lines cached z an earlier read, zwróć
        # them unconditionally
        jeżeli self.linebuffer:
            line = self.linebuffer[0]
            usuń self.linebuffer[0]
            jeżeli len(self.linebuffer) == 1:
                # revert to charbuffer mode; we might need more data
                # next time
                self.charbuffer = self.linebuffer[0]
                self.linebuffer = Nic
            jeżeli nie keepends:
                line = line.splitlines(keepends=Nieprawda)[0]
            zwróć line

        readsize = size albo 72
        line = self._empty_charbuffer
        # If size jest given, we call read() only once
        dopóki Prawda:
            data = self.read(readsize, firstline=Prawda)
            jeżeli data:
                # If we're at a "\r" read one extra character (which might
                # be a "\n") to get a proper line ending. If the stream jest
                # temporarily exhausted we zwróć the wrong line ending.
                jeżeli (isinstance(data, str) oraz data.endswith("\r")) albo \
                   (isinstance(data, bytes) oraz data.endswith(b"\r")):
                    data += self.read(size=1, chars=1)

            line += data
            lines = line.splitlines(keepends=Prawda)
            jeżeli lines:
                jeżeli len(lines) > 1:
                    # More than one line result; the first line jest a full line
                    # to zwróć
                    line = lines[0]
                    usuń lines[0]
                    jeżeli len(lines) > 1:
                        # cache the remaining lines
                        lines[-1] += self.charbuffer
                        self.linebuffer = lines
                        self.charbuffer = Nic
                    inaczej:
                        # only one remaining line, put it back into charbuffer
                        self.charbuffer = lines[0] + self.charbuffer
                    jeżeli nie keepends:
                        line = line.splitlines(keepends=Nieprawda)[0]
                    przerwij
                line0withend = lines[0]
                line0withoutend = lines[0].splitlines(keepends=Nieprawda)[0]
                jeżeli line0withend != line0withoutend: # We really have a line end
                    # Put the rest back together oraz keep it until the next call
                    self.charbuffer = self._empty_charbuffer.join(lines[1:]) + \
                                      self.charbuffer
                    jeżeli keepends:
                        line = line0withend
                    inaczej:
                        line = line0withoutend
                    przerwij
            # we didn't get anything albo this was our only try
            jeżeli nie data albo size jest nie Nic:
                jeżeli line oraz nie keepends:
                    line = line.splitlines(keepends=Nieprawda)[0]
                przerwij
            jeżeli readsize < 8000:
                readsize *= 2
        zwróć line

    def readlines(self, sizehint=Nic, keepends=Prawda):

        """ Read all lines available on the input stream
            oraz zwróć them jako a list.

            Line przerwijs are implemented using the codec's decoder
            method oraz are included w the list entries.

            sizehint, jeżeli given, jest ignored since there jest no efficient
            way to finding the true end-of-line.

        """
        data = self.read()
        zwróć data.splitlines(keepends)

    def reset(self):

        """ Resets the codec buffers used dla keeping state.

            Note that no stream repositioning should take place.
            This method jest primarily intended to be able to recover
            z decoding errors.

        """
        self.bytebuffer = b""
        self.charbuffer = self._empty_charbuffer
        self.linebuffer = Nic

    def seek(self, offset, whence=0):
        """ Set the input stream's current position.

            Resets the codec buffers used dla keeping state.
        """
        self.stream.seek(offset, whence)
        self.reset()

    def __next__(self):

        """ Return the next decoded line z the input stream."""
        line = self.readline()
        jeżeli line:
            zwróć line
        podnieś StopIteration

    def __iter__(self):
        zwróć self

    def __getattr__(self, name,
                    getattr=getattr):

        """ Inherit all other methods z the underlying stream.
        """
        zwróć getattr(self.stream, name)

    def __enter__(self):
        zwróć self

    def __exit__(self, type, value, tb):
        self.stream.close()

###

klasa StreamReaderWriter:

    """ StreamReaderWriter instances allow wrapping streams which
        work w both read oraz write modes.

        The design jest such that one can use the factory functions
        returned by the codec.lookup() function to construct the
        instance.

    """
    # Optional attributes set by the file wrappers below
    encoding = 'unknown'

    def __init__(self, stream, Reader, Writer, errors='strict'):

        """ Creates a StreamReaderWriter instance.

            stream must be a Stream-like object.

            Reader, Writer must be factory functions albo classes
            providing the StreamReader, StreamWriter interface resp.

            Error handling jest done w the same way jako defined dla the
            StreamWriter/Readers.

        """
        self.stream = stream
        self.reader = Reader(stream, errors)
        self.writer = Writer(stream, errors)
        self.errors = errors

    def read(self, size=-1):

        zwróć self.reader.read(size)

    def readline(self, size=Nic):

        zwróć self.reader.readline(size)

    def readlines(self, sizehint=Nic):

        zwróć self.reader.readlines(sizehint)

    def __next__(self):

        """ Return the next decoded line z the input stream."""
        zwróć next(self.reader)

    def __iter__(self):
        zwróć self

    def write(self, data):

        zwróć self.writer.write(data)

    def writelines(self, list):

        zwróć self.writer.writelines(list)

    def reset(self):

        self.reader.reset()
        self.writer.reset()

    def seek(self, offset, whence=0):
        self.stream.seek(offset, whence)
        self.reader.reset()
        jeżeli whence == 0 oraz offset == 0:
            self.writer.reset()

    def __getattr__(self, name,
                    getattr=getattr):

        """ Inherit all other methods z the underlying stream.
        """
        zwróć getattr(self.stream, name)

    # these are needed to make "przy codecs.open(...)" work properly

    def __enter__(self):
        zwróć self

    def __exit__(self, type, value, tb):
        self.stream.close()

###

klasa StreamRecoder:

    """ StreamRecoder instances translate data z one encoding to another.

        They use the complete set of APIs returned by the
        codecs.lookup() function to implement their task.

        Data written to the StreamRecoder jest first decoded into an
        intermediate format (depending on the "decode" codec) oraz then
        written to the underlying stream using an instance of the provided
        Writer class.

        In the other direction, data jest read z the underlying stream using
        a Reader instance oraz then encoded oraz returned to the caller.

    """
    # Optional attributes set by the file wrappers below
    data_encoding = 'unknown'
    file_encoding = 'unknown'

    def __init__(self, stream, encode, decode, Reader, Writer,
                 errors='strict'):

        """ Creates a StreamRecoder instance which implements a two-way
            conversion: encode oraz decode work on the frontend (the
            data visible to .read() oraz .write()) dopóki Reader oraz Writer
            work on the backend (the data w stream).

            You can use these objects to do transparent
            transcodings z e.g. latin-1 to utf-8 oraz back.

            stream must be a file-like object.

            encode oraz decode must adhere to the Codec interface; Reader oraz
            Writer must be factory functions albo classes providing the
            StreamReader oraz StreamWriter interfaces resp.

            Error handling jest done w the same way jako defined dla the
            StreamWriter/Readers.

        """
        self.stream = stream
        self.encode = encode
        self.decode = decode
        self.reader = Reader(stream, errors)
        self.writer = Writer(stream, errors)
        self.errors = errors

    def read(self, size=-1):

        data = self.reader.read(size)
        data, bytesencoded = self.encode(data, self.errors)
        zwróć data

    def readline(self, size=Nic):

        jeżeli size jest Nic:
            data = self.reader.readline()
        inaczej:
            data = self.reader.readline(size)
        data, bytesencoded = self.encode(data, self.errors)
        zwróć data

    def readlines(self, sizehint=Nic):

        data = self.reader.read()
        data, bytesencoded = self.encode(data, self.errors)
        zwróć data.splitlines(keepends=Prawda)

    def __next__(self):

        """ Return the next decoded line z the input stream."""
        data = next(self.reader)
        data, bytesencoded = self.encode(data, self.errors)
        zwróć data

    def __iter__(self):
        zwróć self

    def write(self, data):

        data, bytesdecoded = self.decode(data, self.errors)
        zwróć self.writer.write(data)

    def writelines(self, list):

        data = ''.join(list)
        data, bytesdecoded = self.decode(data, self.errors)
        zwróć self.writer.write(data)

    def reset(self):

        self.reader.reset()
        self.writer.reset()

    def __getattr__(self, name,
                    getattr=getattr):

        """ Inherit all other methods z the underlying stream.
        """
        zwróć getattr(self.stream, name)

    def __enter__(self):
        zwróć self

    def __exit__(self, type, value, tb):
        self.stream.close()

### Shortcuts

def open(filename, mode='r', encoding=Nic, errors='strict', buffering=1):

    """ Open an encoded file using the given mode oraz zwróć
        a wrapped version providing transparent encoding/decoding.

        Note: The wrapped version will only accept the object format
        defined by the codecs, i.e. Unicode objects dla most builtin
        codecs. Output jest also codec dependent oraz will usually be
        Unicode jako well.

        Underlying encoded files are always opened w binary mode.
        The default file mode jest 'r', meaning to open the file w read mode.

        encoding specifies the encoding which jest to be used dla the
        file.

        errors may be given to define the error handling. It defaults
        to 'strict' which causes ValueErrors to be podnieśd w case an
        encoding error occurs.

        buffering has the same meaning jako dla the builtin open() API.
        It defaults to line buffered.

        The returned wrapped file object provides an extra attribute
        .encoding which allows querying the used encoding. This
        attribute jest only available jeżeli an encoding was specified as
        parameter.

    """
    jeżeli encoding jest nie Nic oraz \
       'b' nie w mode:
        # Force opening of the file w binary mode
        mode = mode + 'b'
    file = builtins.open(filename, mode, buffering)
    jeżeli encoding jest Nic:
        zwróć file
    info = lookup(encoding)
    srw = StreamReaderWriter(file, info.streamreader, info.streamwriter, errors)
    # Add attributes to simplify introspection
    srw.encoding = encoding
    zwróć srw

def EncodedFile(file, data_encoding, file_encoding=Nic, errors='strict'):

    """ Return a wrapped version of file which provides transparent
        encoding translation.

        Data written to the wrapped file jest decoded according
        to the given data_encoding oraz then encoded to the underlying
        file using file_encoding. The intermediate data type
        will usually be Unicode but depends on the specified codecs.

        Bytes read z the file are decoded using file_encoding oraz then
        dalejed back to the caller encoded using data_encoding.

        If file_encoding jest nie given, it defaults to data_encoding.

        errors may be given to define the error handling. It defaults
        to 'strict' which causes ValueErrors to be podnieśd w case an
        encoding error occurs.

        The returned wrapped file object provides two extra attributes
        .data_encoding oraz .file_encoding which reflect the given
        parameters of the same name. The attributes can be used for
        introspection by Python programs.

    """
    jeżeli file_encoding jest Nic:
        file_encoding = data_encoding
    data_info = lookup(data_encoding)
    file_info = lookup(file_encoding)
    sr = StreamRecoder(file, data_info.encode, data_info.decode,
                       file_info.streamreader, file_info.streamwriter, errors)
    # Add attributes to simplify introspection
    sr.data_encoding = data_encoding
    sr.file_encoding = file_encoding
    zwróć sr

### Helpers dla codec lookup

def getencoder(encoding):

    """ Lookup up the codec dla the given encoding oraz zwróć
        its encoder function.

        Raises a LookupError w case the encoding cannot be found.

    """
    zwróć lookup(encoding).encode

def getdecoder(encoding):

    """ Lookup up the codec dla the given encoding oraz zwróć
        its decoder function.

        Raises a LookupError w case the encoding cannot be found.

    """
    zwróć lookup(encoding).decode

def getincrementalencoder(encoding):

    """ Lookup up the codec dla the given encoding oraz zwróć
        its IncrementalEncoder klasa albo factory function.

        Raises a LookupError w case the encoding cannot be found
        albo the codecs doesn't provide an incremental encoder.

    """
    encoder = lookup(encoding).incrementalencoder
    jeżeli encoder jest Nic:
        podnieś LookupError(encoding)
    zwróć encoder

def getincrementaldecoder(encoding):

    """ Lookup up the codec dla the given encoding oraz zwróć
        its IncrementalDecoder klasa albo factory function.

        Raises a LookupError w case the encoding cannot be found
        albo the codecs doesn't provide an incremental decoder.

    """
    decoder = lookup(encoding).incrementaldecoder
    jeżeli decoder jest Nic:
        podnieś LookupError(encoding)
    zwróć decoder

def getreader(encoding):

    """ Lookup up the codec dla the given encoding oraz zwróć
        its StreamReader klasa albo factory function.

        Raises a LookupError w case the encoding cannot be found.

    """
    zwróć lookup(encoding).streamreader

def getwriter(encoding):

    """ Lookup up the codec dla the given encoding oraz zwróć
        its StreamWriter klasa albo factory function.

        Raises a LookupError w case the encoding cannot be found.

    """
    zwróć lookup(encoding).streamwriter

def iterencode(iterator, encoding, errors='strict', **kwargs):
    """
    Encoding iterator.

    Encodes the input strings z the iterator using a IncrementalEncoder.

    errors oraz kwargs are dalejed through to the IncrementalEncoder
    constructor.
    """
    encoder = getincrementalencoder(encoding)(errors, **kwargs)
    dla input w iterator:
        output = encoder.encode(input)
        jeżeli output:
            uzyskaj output
    output = encoder.encode("", Prawda)
    jeżeli output:
        uzyskaj output

def iterdecode(iterator, encoding, errors='strict', **kwargs):
    """
    Decoding iterator.

    Decodes the input strings z the iterator using a IncrementalDecoder.

    errors oraz kwargs are dalejed through to the IncrementalDecoder
    constructor.
    """
    decoder = getincrementaldecoder(encoding)(errors, **kwargs)
    dla input w iterator:
        output = decoder.decode(input)
        jeżeli output:
            uzyskaj output
    output = decoder.decode(b"", Prawda)
    jeżeli output:
        uzyskaj output

### Helpers dla charmap-based codecs

def make_identity_dict(rng):

    """ make_identity_dict(rng) -> dict

        Return a dictionary where elements of the rng sequence are
        mapped to themselves.

    """
    zwróć {i:i dla i w rng}

def make_encoding_map(decoding_map):

    """ Creates an encoding map z a decoding map.

        If a target mapping w the decoding map occurs multiple
        times, then that target jest mapped to Nic (undefined mapping),
        causing an exception when encountered by the charmap codec
        during translation.

        One example where this happens jest cp875.py which decodes
        multiple character to \\u001a.

    """
    m = {}
    dla k,v w decoding_map.items():
        jeżeli nie v w m:
            m[v] = k
        inaczej:
            m[v] = Nic
    zwróć m

### error handlers

spróbuj:
    strict_errors = lookup_error("strict")
    ignore_errors = lookup_error("ignore")
    replace_errors = lookup_error("replace")
    xmlcharrefreplace_errors = lookup_error("xmlcharrefreplace")
    backslashreplace_errors = lookup_error("backslashreplace")
    namereplace_errors = lookup_error("namereplace")
wyjąwszy LookupError:
    # In --disable-unicode builds, these error handler are missing
    strict_errors = Nic
    ignore_errors = Nic
    replace_errors = Nic
    xmlcharrefreplace_errors = Nic
    backslashreplace_errors = Nic
    namereplace_errors = Nic

# Tell modulefinder that using codecs probably needs the encodings
# package
_false = 0
jeżeli _false:
    zaimportuj encodings

### Tests

jeżeli __name__ == '__main__':

    # Make stdout translate Latin-1 output into UTF-8 output
    sys.stdout = EncodedFile(sys.stdout, 'latin-1', 'utf-8')

    # Have stdin translate Latin-1 input into UTF-8 input
    sys.stdin = EncodedFile(sys.stdin, 'utf-8', 'latin-1')
