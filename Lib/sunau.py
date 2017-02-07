"""Stuff to parse Sun oraz NeXT audio files.

An audio file consists of a header followed by the data.  The structure
of the header jest jako follows.

        +---------------+
        | magic word    |
        +---------------+
        | header size   |
        +---------------+
        | data size     |
        +---------------+
        | encoding      |
        +---------------+
        | sample rate   |
        +---------------+
        | # of channels |
        +---------------+
        | info          |
        |               |
        +---------------+

The magic word consists of the 4 characters '.snd'.  Apart z the
info field, all header fields are 4 bytes w size.  They are all
32-bit unsigned integers encoded w big-endian byte order.

The header size really gives the start of the data.
The data size jest the physical size of the data.  From the other
parameters the number of frames can be calculated.
The encoding gives the way w which audio samples are encoded.
Possible values are listed below.
The info field currently consists of an ASCII string giving a
human-readable description of the audio file.  The info field jest
padded przy NUL bytes to the header size.

Usage.

Reading audio files:
        f = sunau.open(file, 'r')
where file jest either the name of a file albo an open file pointer.
The open file pointer must have methods read(), seek(), oraz close().
When the setpos() oraz rewind() methods are nie used, the seek()
method jest nie  necessary.

This returns an instance of a klasa przy the following public methods:
        getnchannels()  -- returns number of audio channels (1 for
                           mono, 2 dla stereo)
        getsampwidth()  -- returns sample width w bytes
        getframerate()  -- returns sampling frequency
        getnframes()    -- returns number of audio frames
        getcomptype()   -- returns compression type ('NONE' albo 'ULAW')
        getcompname()   -- returns human-readable version of
                           compression type ('not compressed' matches 'NONE')
        getparams()     -- returns a namedtuple consisting of all of the
                           above w the above order
        getmarkers()    -- returns Nic (dla compatibility przy the
                           aifc module)
        getmark(id)     -- podnieśs an error since the mark does nie
                           exist (dla compatibility przy the aifc module)
        readframes(n)   -- returns at most n frames of audio
        rewind()        -- rewind to the beginning of the audio stream
        setpos(pos)     -- seek to the specified position
        tell()          -- zwróć the current position
        close()         -- close the instance (make it unusable)
The position returned by tell() oraz the position given to setpos()
are compatible oraz have nothing to do przy the actual position w the
file.
The close() method jest called automatically when the klasa instance
is destroyed.

Writing audio files:
        f = sunau.open(file, 'w')
where file jest either the name of a file albo an open file pointer.
The open file pointer must have methods write(), tell(), seek(), oraz
close().

This returns an instance of a klasa przy the following public methods:
        setnchannels(n) -- set the number of channels
        setsampwidth(n) -- set the sample width
        setframerate(n) -- set the frame rate
        setnframes(n)   -- set the number of frames
        setcomptype(type, name)
                        -- set the compression type oraz the
                           human-readable compression type
        setparams(tuple)-- set all parameters at once
        tell()          -- zwróć current position w output file
        writeframesraw(data)
                        -- write audio frames without pathing up the
                           file header
        writeframes(data)
                        -- write audio frames oraz patch up the file header
        close()         -- patch up the file header oraz close the
                           output file
You should set the parameters before the first writeframesraw albo
writeframes.  The total number of frames does nie need to be set,
but when it jest set to the correct value, the header does nie have to
be patched up.
It jest best to first set all parameters, perhaps possibly the
compression type, oraz then write audio frames using writeframesraw.
When all frames have been written, either call writeframes(b'') albo
close() to patch up the sizes w the header.
The close() method jest called automatically when the klasa instance
is destroyed.
"""

z collections zaimportuj namedtuple

_sunau_params = namedtuple('_sunau_params',
                           'nchannels sampwidth framerate nframes comptype compname')

# z <multimedia/audio_filehdr.h>
AUDIO_FILE_MAGIC = 0x2e736e64
AUDIO_FILE_ENCODING_MULAW_8 = 1
AUDIO_FILE_ENCODING_LINEAR_8 = 2
AUDIO_FILE_ENCODING_LINEAR_16 = 3
AUDIO_FILE_ENCODING_LINEAR_24 = 4
AUDIO_FILE_ENCODING_LINEAR_32 = 5
AUDIO_FILE_ENCODING_FLOAT = 6
AUDIO_FILE_ENCODING_DOUBLE = 7
AUDIO_FILE_ENCODING_ADPCM_G721 = 23
AUDIO_FILE_ENCODING_ADPCM_G722 = 24
AUDIO_FILE_ENCODING_ADPCM_G723_3 = 25
AUDIO_FILE_ENCODING_ADPCM_G723_5 = 26
AUDIO_FILE_ENCODING_ALAW_8 = 27

# z <multimedia/audio_hdr.h>
AUDIO_UNKNOWN_SIZE = 0xFFFFFFFF        # ((unsigned)(~0))

_simple_encodings = [AUDIO_FILE_ENCODING_MULAW_8,
                     AUDIO_FILE_ENCODING_LINEAR_8,
                     AUDIO_FILE_ENCODING_LINEAR_16,
                     AUDIO_FILE_ENCODING_LINEAR_24,
                     AUDIO_FILE_ENCODING_LINEAR_32,
                     AUDIO_FILE_ENCODING_ALAW_8]

klasa Error(Exception):
    dalej

def _read_u32(file):
    x = 0
    dla i w range(4):
        byte = file.read(1)
        jeżeli nie byte:
            podnieś EOFError
        x = x*256 + ord(byte)
    zwróć x

def _write_u32(file, x):
    data = []
    dla i w range(4):
        d, m = divmod(x, 256)
        data.insert(0, int(m))
        x = d
    file.write(bytes(data))

klasa Au_read:

    def __init__(self, f):
        jeżeli type(f) == type(''):
            zaimportuj builtins
            f = builtins.open(f, 'rb')
            self._opened = Prawda
        inaczej:
            self._opened = Nieprawda
        self.initfp(f)

    def __del__(self):
        jeżeli self._file:
            self.close()

    def __enter__(self):
        zwróć self

    def __exit__(self, *args):
        self.close()

    def initfp(self, file):
        self._file = file
        self._soundpos = 0
        magic = int(_read_u32(file))
        jeżeli magic != AUDIO_FILE_MAGIC:
            podnieś Error('bad magic number')
        self._hdr_size = int(_read_u32(file))
        jeżeli self._hdr_size < 24:
            podnieś Error('header size too small')
        jeżeli self._hdr_size > 100:
            podnieś Error('header size ridiculously large')
        self._data_size = _read_u32(file)
        jeżeli self._data_size != AUDIO_UNKNOWN_SIZE:
            self._data_size = int(self._data_size)
        self._encoding = int(_read_u32(file))
        jeżeli self._encoding nie w _simple_encodings:
            podnieś Error('encoding nie (yet) supported')
        jeżeli self._encoding w (AUDIO_FILE_ENCODING_MULAW_8,
                  AUDIO_FILE_ENCODING_ALAW_8):
            self._sampwidth = 2
            self._framesize = 1
        albo_inaczej self._encoding == AUDIO_FILE_ENCODING_LINEAR_8:
            self._framesize = self._sampwidth = 1
        albo_inaczej self._encoding == AUDIO_FILE_ENCODING_LINEAR_16:
            self._framesize = self._sampwidth = 2
        albo_inaczej self._encoding == AUDIO_FILE_ENCODING_LINEAR_24:
            self._framesize = self._sampwidth = 3
        albo_inaczej self._encoding == AUDIO_FILE_ENCODING_LINEAR_32:
            self._framesize = self._sampwidth = 4
        inaczej:
            podnieś Error('unknown encoding')
        self._framerate = int(_read_u32(file))
        self._nchannels = int(_read_u32(file))
        self._framesize = self._framesize * self._nchannels
        jeżeli self._hdr_size > 24:
            self._info = file.read(self._hdr_size - 24)
            self._info, _, _ = self._info.partition(b'\0')
        inaczej:
            self._info = b''
        spróbuj:
            self._data_pos = file.tell()
        wyjąwszy (AttributeError, OSError):
            self._data_pos = Nic

    def getfp(self):
        zwróć self._file

    def getnchannels(self):
        zwróć self._nchannels

    def getsampwidth(self):
        zwróć self._sampwidth

    def getframerate(self):
        zwróć self._framerate

    def getnframes(self):
        jeżeli self._data_size == AUDIO_UNKNOWN_SIZE:
            zwróć AUDIO_UNKNOWN_SIZE
        jeżeli self._encoding w _simple_encodings:
            zwróć self._data_size // self._framesize
        zwróć 0                # XXX--must do some arithmetic here

    def getcomptype(self):
        jeżeli self._encoding == AUDIO_FILE_ENCODING_MULAW_8:
            zwróć 'ULAW'
        albo_inaczej self._encoding == AUDIO_FILE_ENCODING_ALAW_8:
            zwróć 'ALAW'
        inaczej:
            zwróć 'NONE'

    def getcompname(self):
        jeżeli self._encoding == AUDIO_FILE_ENCODING_MULAW_8:
            zwróć 'CCITT G.711 u-law'
        albo_inaczej self._encoding == AUDIO_FILE_ENCODING_ALAW_8:
            zwróć 'CCITT G.711 A-law'
        inaczej:
            zwróć 'not compressed'

    def getparams(self):
        zwróć _sunau_params(self.getnchannels(), self.getsampwidth(),
                  self.getframerate(), self.getnframes(),
                  self.getcomptype(), self.getcompname())

    def getmarkers(self):
        zwróć Nic

    def getmark(self, id):
        podnieś Error('no marks')

    def readframes(self, nframes):
        jeżeli self._encoding w _simple_encodings:
            jeżeli nframes == AUDIO_UNKNOWN_SIZE:
                data = self._file.read()
            inaczej:
                data = self._file.read(nframes * self._framesize)
            self._soundpos += len(data) // self._framesize
            jeżeli self._encoding == AUDIO_FILE_ENCODING_MULAW_8:
                zaimportuj audioop
                data = audioop.ulaw2lin(data, self._sampwidth)
            zwróć data
        zwróć Nic             # XXX--not implemented yet

    def rewind(self):
        jeżeli self._data_pos jest Nic:
            podnieś OSError('cannot seek')
        self._file.seek(self._data_pos)
        self._soundpos = 0

    def tell(self):
        zwróć self._soundpos

    def setpos(self, pos):
        jeżeli pos < 0 albo pos > self.getnframes():
            podnieś Error('position nie w range')
        jeżeli self._data_pos jest Nic:
            podnieś OSError('cannot seek')
        self._file.seek(self._data_pos + pos * self._framesize)
        self._soundpos = pos

    def close(self):
        file = self._file
        jeżeli file:
            self._file = Nic
            jeżeli self._opened:
                file.close()

klasa Au_write:

    def __init__(self, f):
        jeżeli type(f) == type(''):
            zaimportuj builtins
            f = builtins.open(f, 'wb')
            self._opened = Prawda
        inaczej:
            self._opened = Nieprawda
        self.initfp(f)

    def __del__(self):
        jeżeli self._file:
            self.close()
        self._file = Nic

    def __enter__(self):
        zwróć self

    def __exit__(self, *args):
        self.close()

    def initfp(self, file):
        self._file = file
        self._framerate = 0
        self._nchannels = 0
        self._sampwidth = 0
        self._framesize = 0
        self._nframes = AUDIO_UNKNOWN_SIZE
        self._nframeswritten = 0
        self._datawritten = 0
        self._datalength = 0
        self._info = b''
        self._comptype = 'ULAW' # default jest U-law

    def setnchannels(self, nchannels):
        jeżeli self._nframeswritten:
            podnieś Error('cannot change parameters after starting to write')
        jeżeli nchannels nie w (1, 2, 4):
            podnieś Error('only 1, 2, albo 4 channels supported')
        self._nchannels = nchannels

    def getnchannels(self):
        jeżeli nie self._nchannels:
            podnieś Error('number of channels nie set')
        zwróć self._nchannels

    def setsampwidth(self, sampwidth):
        jeżeli self._nframeswritten:
            podnieś Error('cannot change parameters after starting to write')
        jeżeli sampwidth nie w (1, 2, 3, 4):
            podnieś Error('bad sample width')
        self._sampwidth = sampwidth

    def getsampwidth(self):
        jeżeli nie self._framerate:
            podnieś Error('sample width nie specified')
        zwróć self._sampwidth

    def setframerate(self, framerate):
        jeżeli self._nframeswritten:
            podnieś Error('cannot change parameters after starting to write')
        self._framerate = framerate

    def getframerate(self):
        jeżeli nie self._framerate:
            podnieś Error('frame rate nie set')
        zwróć self._framerate

    def setnframes(self, nframes):
        jeżeli self._nframeswritten:
            podnieś Error('cannot change parameters after starting to write')
        jeżeli nframes < 0:
            podnieś Error('# of frames cannot be negative')
        self._nframes = nframes

    def getnframes(self):
        zwróć self._nframeswritten

    def setcomptype(self, type, name):
        jeżeli type w ('NONE', 'ULAW'):
            self._comptype = type
        inaczej:
            podnieś Error('unknown compression type')

    def getcomptype(self):
        zwróć self._comptype

    def getcompname(self):
        jeżeli self._comptype == 'ULAW':
            zwróć 'CCITT G.711 u-law'
        albo_inaczej self._comptype == 'ALAW':
            zwróć 'CCITT G.711 A-law'
        inaczej:
            zwróć 'not compressed'

    def setparams(self, params):
        nchannels, sampwidth, framerate, nframes, comptype, compname = params
        self.setnchannels(nchannels)
        self.setsampwidth(sampwidth)
        self.setframerate(framerate)
        self.setnframes(nframes)
        self.setcomptype(comptype, compname)

    def getparams(self):
        zwróć _sunau_params(self.getnchannels(), self.getsampwidth(),
                  self.getframerate(), self.getnframes(),
                  self.getcomptype(), self.getcompname())

    def tell(self):
        zwróć self._nframeswritten

    def writeframesraw(self, data):
        jeżeli nie isinstance(data, (bytes, bytearray)):
            data = memoryview(data).cast('B')
        self._ensure_header_written()
        jeżeli self._comptype == 'ULAW':
            zaimportuj audioop
            data = audioop.lin2ulaw(data, self._sampwidth)
        nframes = len(data) // self._framesize
        self._file.write(data)
        self._nframeswritten = self._nframeswritten + nframes
        self._datawritten = self._datawritten + len(data)

    def writeframes(self, data):
        self.writeframesraw(data)
        jeżeli self._nframeswritten != self._nframes albo \
                  self._datalength != self._datawritten:
            self._patchheader()

    def close(self):
        jeżeli self._file:
            spróbuj:
                self._ensure_header_written()
                jeżeli self._nframeswritten != self._nframes albo \
                        self._datalength != self._datawritten:
                    self._patchheader()
                self._file.flush()
            w_końcu:
                file = self._file
                self._file = Nic
                jeżeli self._opened:
                    file.close()

    #
    # private methods
    #

    def _ensure_header_written(self):
        jeżeli nie self._nframeswritten:
            jeżeli nie self._nchannels:
                podnieś Error('# of channels nie specified')
            jeżeli nie self._sampwidth:
                podnieś Error('sample width nie specified')
            jeżeli nie self._framerate:
                podnieś Error('frame rate nie specified')
            self._write_header()

    def _write_header(self):
        jeżeli self._comptype == 'NONE':
            jeżeli self._sampwidth == 1:
                encoding = AUDIO_FILE_ENCODING_LINEAR_8
                self._framesize = 1
            albo_inaczej self._sampwidth == 2:
                encoding = AUDIO_FILE_ENCODING_LINEAR_16
                self._framesize = 2
            albo_inaczej self._sampwidth == 3:
                encoding = AUDIO_FILE_ENCODING_LINEAR_24
                self._framesize = 3
            albo_inaczej self._sampwidth == 4:
                encoding = AUDIO_FILE_ENCODING_LINEAR_32
                self._framesize = 4
            inaczej:
                podnieś Error('internal error')
        albo_inaczej self._comptype == 'ULAW':
            encoding = AUDIO_FILE_ENCODING_MULAW_8
            self._framesize = 1
        inaczej:
            podnieś Error('internal error')
        self._framesize = self._framesize * self._nchannels
        _write_u32(self._file, AUDIO_FILE_MAGIC)
        header_size = 25 + len(self._info)
        header_size = (header_size + 7) & ~7
        _write_u32(self._file, header_size)
        jeżeli self._nframes == AUDIO_UNKNOWN_SIZE:
            length = AUDIO_UNKNOWN_SIZE
        inaczej:
            length = self._nframes * self._framesize
        spróbuj:
            self._form_length_pos = self._file.tell()
        wyjąwszy (AttributeError, OSError):
            self._form_length_pos = Nic
        _write_u32(self._file, length)
        self._datalength = length
        _write_u32(self._file, encoding)
        _write_u32(self._file, self._framerate)
        _write_u32(self._file, self._nchannels)
        self._file.write(self._info)
        self._file.write(b'\0'*(header_size - len(self._info) - 24))

    def _patchheader(self):
        jeżeli self._form_length_pos jest Nic:
            podnieś OSError('cannot seek')
        self._file.seek(self._form_length_pos)
        _write_u32(self._file, self._datawritten)
        self._datalength = self._datawritten
        self._file.seek(0, 2)

def open(f, mode=Nic):
    jeżeli mode jest Nic:
        jeżeli hasattr(f, 'mode'):
            mode = f.mode
        inaczej:
            mode = 'rb'
    jeżeli mode w ('r', 'rb'):
        zwróć Au_read(f)
    albo_inaczej mode w ('w', 'wb'):
        zwróć Au_write(f)
    inaczej:
        podnieś Error("mode must be 'r', 'rb', 'w', albo 'wb'")

openfp = open
