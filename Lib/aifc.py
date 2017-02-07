"""Stuff to parse AIFF-C oraz AIFF files.

Unless explicitly stated otherwise, the description below jest true
both dla AIFF-C files oraz AIFF files.

An AIFF-C file has the following structure.

  +-----------------+
  | FORM            |
  +-----------------+
  | <size>          |
  +----+------------+
  |    | AIFC       |
  |    +------------+
  |    | <chunks>   |
  |    |    .       |
  |    |    .       |
  |    |    .       |
  +----+------------+

An AIFF file has the string "AIFF" instead of "AIFC".

A chunk consists of an identifier (4 bytes) followed by a size (4 bytes,
big endian order), followed by the data.  The size field does nie include
the size of the 8 byte header.

The following chunk types are recognized.

  FVER
      <version number of AIFF-C defining document> (AIFF-C only).
  MARK
      <# of markers> (2 bytes)
      list of markers:
          <marker ID> (2 bytes, must be > 0)
          <position> (4 bytes)
          <marker name> ("pstring")
  COMM
      <# of channels> (2 bytes)
      <# of sound frames> (4 bytes)
      <size of the samples> (2 bytes)
      <sampling frequency> (10 bytes, IEEE 80-bit extended
          floating point)
      w AIFF-C files only:
      <compression type> (4 bytes)
      <human-readable version of compression type> ("pstring")
  SSND
      <offset> (4 bytes, nie used by this program)
      <blocksize> (4 bytes, nie used by this program)
      <sound data>

A pstring consists of 1 byte length, a string of characters, oraz 0 albo 1
byte pad to make the total length even.

Usage.

Reading AIFF files:
  f = aifc.open(file, 'r')
where file jest either the name of a file albo an open file pointer.
The open file pointer must have methods read(), seek(), oraz close().
In some types of audio files, jeżeli the setpos() method jest nie used,
the seek() method jest nie necessary.

This returns an instance of a klasa przy the following public methods:
  getnchannels()  -- returns number of audio channels (1 for
             mono, 2 dla stereo)
  getsampwidth()  -- returns sample width w bytes
  getframerate()  -- returns sampling frequency
  getnframes()    -- returns number of audio frames
  getcomptype()   -- returns compression type ('NONE' dla AIFF files)
  getcompname()   -- returns human-readable version of
             compression type ('not compressed' dla AIFF files)
  getparams() -- returns a namedtuple consisting of all of the
             above w the above order
  getmarkers()    -- get the list of marks w the audio file albo Nic
             jeżeli there are no marks
  getmark(id) -- get mark przy the specified id (raises an error
             jeżeli the mark does nie exist)
  readframes(n)   -- returns at most n frames of audio
  rewind()    -- rewind to the beginning of the audio stream
  setpos(pos) -- seek to the specified position
  tell()      -- zwróć the current position
  close()     -- close the instance (make it unusable)
The position returned by tell(), the position given to setpos() oraz
the position of marks are all compatible oraz have nothing to do with
the actual position w the file.
The close() method jest called automatically when the klasa instance
is destroyed.

Writing AIFF files:
  f = aifc.open(file, 'w')
where file jest either the name of a file albo an open file pointer.
The open file pointer must have methods write(), tell(), seek(), oraz
close().

This returns an instance of a klasa przy the following public methods:
  aiff()      -- create an AIFF file (AIFF-C default)
  aifc()      -- create an AIFF-C file
  setnchannels(n) -- set the number of channels
  setsampwidth(n) -- set the sample width
  setframerate(n) -- set the frame rate
  setnframes(n)   -- set the number of frames
  setcomptype(type, name)
          -- set the compression type oraz the
             human-readable compression type
  setparams(tuple)
          -- set all parameters at once
  setmark(id, pos, name)
          -- add specified mark to the list of marks
  tell()      -- zwróć current position w output file (useful
             w combination przy setmark())
  writeframesraw(data)
          -- write audio frames without pathing up the
             file header
  writeframes(data)
          -- write audio frames oraz patch up the file header
  close()     -- patch up the file header oraz close the
             output file
You should set the parameters before the first writeframesraw albo
writeframes.  The total number of frames does nie need to be set,
but when it jest set to the correct value, the header does nie have to
be patched up.
It jest best to first set all parameters, perhaps possibly the
compression type, oraz then write audio frames using writeframesraw.
When all frames have been written, either call writeframes(b'') albo
close() to patch up the sizes w the header.
Marks can be added anytime.  If there are any marks, you must call
close() after all frames have been written.
The close() method jest called automatically when the klasa instance
is destroyed.

When a file jest opened przy the extension '.aiff', an AIFF file jest
written, otherwise an AIFF-C file jest written.  This default can be
changed by calling aiff() albo aifc() before the first writeframes albo
writeframesraw.
"""

zaimportuj struct
zaimportuj builtins
zaimportuj warnings

__all__ = ["Error", "open", "openfp"]

klasa Error(Exception):
    dalej

_AIFC_version = 0xA2805140     # Version 1 of AIFF-C

def _read_long(file):
    spróbuj:
        zwróć struct.unpack('>l', file.read(4))[0]
    wyjąwszy struct.error:
        podnieś EOFError

def _read_ulong(file):
    spróbuj:
        zwróć struct.unpack('>L', file.read(4))[0]
    wyjąwszy struct.error:
        podnieś EOFError

def _read_short(file):
    spróbuj:
        zwróć struct.unpack('>h', file.read(2))[0]
    wyjąwszy struct.error:
        podnieś EOFError

def _read_ushort(file):
    spróbuj:
        zwróć struct.unpack('>H', file.read(2))[0]
    wyjąwszy struct.error:
        podnieś EOFError

def _read_string(file):
    length = ord(file.read(1))
    jeżeli length == 0:
        data = b''
    inaczej:
        data = file.read(length)
    jeżeli length & 1 == 0:
        dummy = file.read(1)
    zwróć data

_HUGE_VAL = 1.79769313486231e+308 # See <limits.h>

def _read_float(f): # 10 bytes
    expon = _read_short(f) # 2 bytes
    sign = 1
    jeżeli expon < 0:
        sign = -1
        expon = expon + 0x8000
    himant = _read_ulong(f) # 4 bytes
    lomant = _read_ulong(f) # 4 bytes
    jeżeli expon == himant == lomant == 0:
        f = 0.0
    albo_inaczej expon == 0x7FFF:
        f = _HUGE_VAL
    inaczej:
        expon = expon - 16383
        f = (himant * 0x100000000 + lomant) * pow(2.0, expon - 63)
    zwróć sign * f

def _write_short(f, x):
    f.write(struct.pack('>h', x))

def _write_ushort(f, x):
    f.write(struct.pack('>H', x))

def _write_long(f, x):
    f.write(struct.pack('>l', x))

def _write_ulong(f, x):
    f.write(struct.pack('>L', x))

def _write_string(f, s):
    jeżeli len(s) > 255:
        podnieś ValueError("string exceeds maximum pstring length")
    f.write(struct.pack('B', len(s)))
    f.write(s)
    jeżeli len(s) & 1 == 0:
        f.write(b'\x00')

def _write_float(f, x):
    zaimportuj math
    jeżeli x < 0:
        sign = 0x8000
        x = x * -1
    inaczej:
        sign = 0
    jeżeli x == 0:
        expon = 0
        himant = 0
        lomant = 0
    inaczej:
        fmant, expon = math.frexp(x)
        jeżeli expon > 16384 albo fmant >= 1 albo fmant != fmant: # Infinity albo NaN
            expon = sign|0x7FFF
            himant = 0
            lomant = 0
        inaczej:                   # Finite
            expon = expon + 16382
            jeżeli expon < 0:           # denormalized
                fmant = math.ldexp(fmant, expon)
                expon = 0
            expon = expon | sign
            fmant = math.ldexp(fmant, 32)
            fsmant = math.floor(fmant)
            himant = int(fsmant)
            fmant = math.ldexp(fmant - fsmant, 32)
            fsmant = math.floor(fmant)
            lomant = int(fsmant)
    _write_ushort(f, expon)
    _write_ulong(f, himant)
    _write_ulong(f, lomant)

z chunk zaimportuj Chunk
z collections zaimportuj namedtuple

_aifc_params = namedtuple('_aifc_params',
                          'nchannels sampwidth framerate nframes comptype compname')


klasa Aifc_read:
    # Variables used w this class:
    #
    # These variables are available to the user though appropriate
    # methods of this class:
    # _file -- the open file przy methods read(), close(), oraz seek()
    #       set through the __init__() method
    # _nchannels -- the number of audio channels
    #       available through the getnchannels() method
    # _nframes -- the number of audio frames
    #       available through the getnframes() method
    # _sampwidth -- the number of bytes per audio sample
    #       available through the getsampwidth() method
    # _framerate -- the sampling frequency
    #       available through the getframerate() method
    # _comptype -- the AIFF-C compression type ('NONE' jeżeli AIFF)
    #       available through the getcomptype() method
    # _compname -- the human-readable AIFF-C compression type
    #       available through the getcomptype() method
    # _markers -- the marks w the audio file
    #       available through the getmarkers() oraz getmark()
    #       methods
    # _soundpos -- the position w the audio stream
    #       available through the tell() method, set through the
    #       setpos() method
    #
    # These variables are used internally only:
    # _version -- the AIFF-C version number
    # _decomp -- the decompressor z builtin module cl
    # _comm_chunk_read -- 1 iff the COMM chunk has been read
    # _aifc -- 1 iff reading an AIFF-C file
    # _ssnd_seek_needed -- 1 iff positioned correctly w audio
    #       file dla readframes()
    # _ssnd_chunk -- instantiation of a chunk klasa dla the SSND chunk
    # _framesize -- size of one frame w the file

    def initfp(self, file):
        self._version = 0
        self._convert = Nic
        self._markers = []
        self._soundpos = 0
        self._file = file
        chunk = Chunk(file)
        jeżeli chunk.getname() != b'FORM':
            podnieś Error('file does nie start przy FORM id')
        formdata = chunk.read(4)
        jeżeli formdata == b'AIFF':
            self._aifc = 0
        albo_inaczej formdata == b'AIFC':
            self._aifc = 1
        inaczej:
            podnieś Error('not an AIFF albo AIFF-C file')
        self._comm_chunk_read = 0
        dopóki 1:
            self._ssnd_seek_needed = 1
            spróbuj:
                chunk = Chunk(self._file)
            wyjąwszy EOFError:
                przerwij
            chunkname = chunk.getname()
            jeżeli chunkname == b'COMM':
                self._read_comm_chunk(chunk)
                self._comm_chunk_read = 1
            albo_inaczej chunkname == b'SSND':
                self._ssnd_chunk = chunk
                dummy = chunk.read(8)
                self._ssnd_seek_needed = 0
            albo_inaczej chunkname == b'FVER':
                self._version = _read_ulong(chunk)
            albo_inaczej chunkname == b'MARK':
                self._readmark(chunk)
            chunk.skip()
        jeżeli nie self._comm_chunk_read albo nie self._ssnd_chunk:
            podnieś Error('COMM chunk and/or SSND chunk missing')

    def __init__(self, f):
        jeżeli isinstance(f, str):
            f = builtins.open(f, 'rb')
        # inaczej, assume it jest an open file object already
        self.initfp(f)

    def __enter__(self):
        zwróć self

    def __exit__(self, *args):
        self.close()

    #
    # User visible methods.
    #
    def getfp(self):
        zwróć self._file

    def rewind(self):
        self._ssnd_seek_needed = 1
        self._soundpos = 0

    def close(self):
        file = self._file
        jeżeli file jest nie Nic:
            self._file = Nic
            file.close()

    def tell(self):
        zwróć self._soundpos

    def getnchannels(self):
        zwróć self._nchannels

    def getnframes(self):
        zwróć self._nframes

    def getsampwidth(self):
        zwróć self._sampwidth

    def getframerate(self):
        zwróć self._framerate

    def getcomptype(self):
        zwróć self._comptype

    def getcompname(self):
        zwróć self._compname

##  def getversion(self):
##      zwróć self._version

    def getparams(self):
        zwróć _aifc_params(self.getnchannels(), self.getsampwidth(),
                            self.getframerate(), self.getnframes(),
                            self.getcomptype(), self.getcompname())

    def getmarkers(self):
        jeżeli len(self._markers) == 0:
            zwróć Nic
        zwróć self._markers

    def getmark(self, id):
        dla marker w self._markers:
            jeżeli id == marker[0]:
                zwróć marker
        podnieś Error('marker {0!r} does nie exist'.format(id))

    def setpos(self, pos):
        jeżeli pos < 0 albo pos > self._nframes:
            podnieś Error('position nie w range')
        self._soundpos = pos
        self._ssnd_seek_needed = 1

    def readframes(self, nframes):
        jeżeli self._ssnd_seek_needed:
            self._ssnd_chunk.seek(0)
            dummy = self._ssnd_chunk.read(8)
            pos = self._soundpos * self._framesize
            jeżeli pos:
                self._ssnd_chunk.seek(pos + 8)
            self._ssnd_seek_needed = 0
        jeżeli nframes == 0:
            zwróć b''
        data = self._ssnd_chunk.read(nframes * self._framesize)
        jeżeli self._convert oraz data:
            data = self._convert(data)
        self._soundpos = self._soundpos + len(data) // (self._nchannels
                                                        * self._sampwidth)
        zwróć data

    #
    # Internal methods.
    #

    def _alaw2lin(self, data):
        zaimportuj audioop
        zwróć audioop.alaw2lin(data, 2)

    def _ulaw2lin(self, data):
        zaimportuj audioop
        zwróć audioop.ulaw2lin(data, 2)

    def _adpcm2lin(self, data):
        zaimportuj audioop
        jeżeli nie hasattr(self, '_adpcmstate'):
            # first time
            self._adpcmstate = Nic
        data, self._adpcmstate = audioop.adpcm2lin(data, 2, self._adpcmstate)
        zwróć data

    def _read_comm_chunk(self, chunk):
        self._nchannels = _read_short(chunk)
        self._nframes = _read_long(chunk)
        self._sampwidth = (_read_short(chunk) + 7) // 8
        self._framerate = int(_read_float(chunk))
        self._framesize = self._nchannels * self._sampwidth
        jeżeli self._aifc:
            #DEBUG: SGI's soundeditor produces a bad size :-(
            kludge = 0
            jeżeli chunk.chunksize == 18:
                kludge = 1
                warnings.warn('Warning: bad COMM chunk size')
                chunk.chunksize = 23
            #DEBUG end
            self._comptype = chunk.read(4)
            #DEBUG start
            jeżeli kludge:
                length = ord(chunk.file.read(1))
                jeżeli length & 1 == 0:
                    length = length + 1
                chunk.chunksize = chunk.chunksize + length
                chunk.file.seek(-1, 1)
            #DEBUG end
            self._compname = _read_string(chunk)
            jeżeli self._comptype != b'NONE':
                jeżeli self._comptype == b'G722':
                    self._convert = self._adpcm2lin
                albo_inaczej self._comptype w (b'ulaw', b'ULAW'):
                    self._convert = self._ulaw2lin
                albo_inaczej self._comptype w (b'alaw', b'ALAW'):
                    self._convert = self._alaw2lin
                inaczej:
                    podnieś Error('unsupported compression type')
                self._sampwidth = 2
        inaczej:
            self._comptype = b'NONE'
            self._compname = b'not compressed'

    def _readmark(self, chunk):
        nmarkers = _read_short(chunk)
        # Some files appear to contain invalid counts.
        # Cope przy this by testing dla EOF.
        spróbuj:
            dla i w range(nmarkers):
                id = _read_short(chunk)
                pos = _read_long(chunk)
                name = _read_string(chunk)
                jeżeli pos albo name:
                    # some files appear to have
                    # dummy markers consisting of
                    # a position 0 oraz name ''
                    self._markers.append((id, pos, name))
        wyjąwszy EOFError:
            w = ('Warning: MARK chunk contains only %s marker%s instead of %s' %
                 (len(self._markers), '' jeżeli len(self._markers) == 1 inaczej 's',
                  nmarkers))
            warnings.warn(w)

klasa Aifc_write:
    # Variables used w this class:
    #
    # These variables are user settable through appropriate methods
    # of this class:
    # _file -- the open file przy methods write(), close(), tell(), seek()
    #       set through the __init__() method
    # _comptype -- the AIFF-C compression type ('NONE' w AIFF)
    #       set through the setcomptype() albo setparams() method
    # _compname -- the human-readable AIFF-C compression type
    #       set through the setcomptype() albo setparams() method
    # _nchannels -- the number of audio channels
    #       set through the setnchannels() albo setparams() method
    # _sampwidth -- the number of bytes per audio sample
    #       set through the setsampwidth() albo setparams() method
    # _framerate -- the sampling frequency
    #       set through the setframerate() albo setparams() method
    # _nframes -- the number of audio frames written to the header
    #       set through the setnframes() albo setparams() method
    # _aifc -- whether we're writing an AIFF-C file albo an AIFF file
    #       set through the aifc() method, reset through the
    #       aiff() method
    #
    # These variables are used internally only:
    # _version -- the AIFF-C version number
    # _comp -- the compressor z builtin module cl
    # _nframeswritten -- the number of audio frames actually written
    # _datalength -- the size of the audio samples written to the header
    # _datawritten -- the size of the audio samples actually written

    def __init__(self, f):
        jeżeli isinstance(f, str):
            filename = f
            f = builtins.open(f, 'wb')
        inaczej:
            # inaczej, assume it jest an open file object already
            filename = '???'
        self.initfp(f)
        jeżeli filename[-5:] == '.aiff':
            self._aifc = 0
        inaczej:
            self._aifc = 1

    def initfp(self, file):
        self._file = file
        self._version = _AIFC_version
        self._comptype = b'NONE'
        self._compname = b'not compressed'
        self._convert = Nic
        self._nchannels = 0
        self._sampwidth = 0
        self._framerate = 0
        self._nframes = 0
        self._nframeswritten = 0
        self._datawritten = 0
        self._datalength = 0
        self._markers = []
        self._marklength = 0
        self._aifc = 1      # AIFF-C jest default

    def __del__(self):
        self.close()

    def __enter__(self):
        zwróć self

    def __exit__(self, *args):
        self.close()

    #
    # User visible methods.
    #
    def aiff(self):
        jeżeli self._nframeswritten:
            podnieś Error('cannot change parameters after starting to write')
        self._aifc = 0

    def aifc(self):
        jeżeli self._nframeswritten:
            podnieś Error('cannot change parameters after starting to write')
        self._aifc = 1

    def setnchannels(self, nchannels):
        jeżeli self._nframeswritten:
            podnieś Error('cannot change parameters after starting to write')
        jeżeli nchannels < 1:
            podnieś Error('bad # of channels')
        self._nchannels = nchannels

    def getnchannels(self):
        jeżeli nie self._nchannels:
            podnieś Error('number of channels nie set')
        zwróć self._nchannels

    def setsampwidth(self, sampwidth):
        jeżeli self._nframeswritten:
            podnieś Error('cannot change parameters after starting to write')
        jeżeli sampwidth < 1 albo sampwidth > 4:
            podnieś Error('bad sample width')
        self._sampwidth = sampwidth

    def getsampwidth(self):
        jeżeli nie self._sampwidth:
            podnieś Error('sample width nie set')
        zwróć self._sampwidth

    def setframerate(self, framerate):
        jeżeli self._nframeswritten:
            podnieś Error('cannot change parameters after starting to write')
        jeżeli framerate <= 0:
            podnieś Error('bad frame rate')
        self._framerate = framerate

    def getframerate(self):
        jeżeli nie self._framerate:
            podnieś Error('frame rate nie set')
        zwróć self._framerate

    def setnframes(self, nframes):
        jeżeli self._nframeswritten:
            podnieś Error('cannot change parameters after starting to write')
        self._nframes = nframes

    def getnframes(self):
        zwróć self._nframeswritten

    def setcomptype(self, comptype, compname):
        jeżeli self._nframeswritten:
            podnieś Error('cannot change parameters after starting to write')
        jeżeli comptype nie w (b'NONE', b'ulaw', b'ULAW',
                            b'alaw', b'ALAW', b'G722'):
            podnieś Error('unsupported compression type')
        self._comptype = comptype
        self._compname = compname

    def getcomptype(self):
        zwróć self._comptype

    def getcompname(self):
        zwróć self._compname

##  def setversion(self, version):
##      jeżeli self._nframeswritten:
##          podnieś Error, 'cannot change parameters after starting to write'
##      self._version = version

    def setparams(self, params):
        nchannels, sampwidth, framerate, nframes, comptype, compname = params
        jeżeli self._nframeswritten:
            podnieś Error('cannot change parameters after starting to write')
        jeżeli comptype nie w (b'NONE', b'ulaw', b'ULAW',
                            b'alaw', b'ALAW', b'G722'):
            podnieś Error('unsupported compression type')
        self.setnchannels(nchannels)
        self.setsampwidth(sampwidth)
        self.setframerate(framerate)
        self.setnframes(nframes)
        self.setcomptype(comptype, compname)

    def getparams(self):
        jeżeli nie self._nchannels albo nie self._sampwidth albo nie self._framerate:
            podnieś Error('not all parameters set')
        zwróć _aifc_params(self._nchannels, self._sampwidth, self._framerate,
                            self._nframes, self._comptype, self._compname)

    def setmark(self, id, pos, name):
        jeżeli id <= 0:
            podnieś Error('marker ID must be > 0')
        jeżeli pos < 0:
            podnieś Error('marker position must be >= 0')
        jeżeli nie isinstance(name, bytes):
            podnieś Error('marker name must be bytes')
        dla i w range(len(self._markers)):
            jeżeli id == self._markers[i][0]:
                self._markers[i] = id, pos, name
                zwróć
        self._markers.append((id, pos, name))

    def getmark(self, id):
        dla marker w self._markers:
            jeżeli id == marker[0]:
                zwróć marker
        podnieś Error('marker {0!r} does nie exist'.format(id))

    def getmarkers(self):
        jeżeli len(self._markers) == 0:
            zwróć Nic
        zwróć self._markers

    def tell(self):
        zwróć self._nframeswritten

    def writeframesraw(self, data):
        jeżeli nie isinstance(data, (bytes, bytearray)):
            data = memoryview(data).cast('B')
        self._ensure_header_written(len(data))
        nframes = len(data) // (self._sampwidth * self._nchannels)
        jeżeli self._convert:
            data = self._convert(data)
        self._file.write(data)
        self._nframeswritten = self._nframeswritten + nframes
        self._datawritten = self._datawritten + len(data)

    def writeframes(self, data):
        self.writeframesraw(data)
        jeżeli self._nframeswritten != self._nframes albo \
              self._datalength != self._datawritten:
            self._patchheader()

    def close(self):
        jeżeli self._file jest Nic:
            zwróć
        spróbuj:
            self._ensure_header_written(0)
            jeżeli self._datawritten & 1:
                # quick pad to even size
                self._file.write(b'\x00')
                self._datawritten = self._datawritten + 1
            self._writemarkers()
            jeżeli self._nframeswritten != self._nframes albo \
                  self._datalength != self._datawritten albo \
                  self._marklength:
                self._patchheader()
        w_końcu:
            # Prevent ref cycles
            self._convert = Nic
            f = self._file
            self._file = Nic
            f.close()

    #
    # Internal methods.
    #

    def _lin2alaw(self, data):
        zaimportuj audioop
        zwróć audioop.lin2alaw(data, 2)

    def _lin2ulaw(self, data):
        zaimportuj audioop
        zwróć audioop.lin2ulaw(data, 2)

    def _lin2adpcm(self, data):
        zaimportuj audioop
        jeżeli nie hasattr(self, '_adpcmstate'):
            self._adpcmstate = Nic
        data, self._adpcmstate = audioop.lin2adpcm(data, 2, self._adpcmstate)
        zwróć data

    def _ensure_header_written(self, datasize):
        jeżeli nie self._nframeswritten:
            jeżeli self._comptype w (b'ULAW', b'ulaw', b'ALAW', b'alaw', b'G722'):
                jeżeli nie self._sampwidth:
                    self._sampwidth = 2
                jeżeli self._sampwidth != 2:
                    podnieś Error('sample width must be 2 when compressing '
                                'przy ulaw/ULAW, alaw/ALAW albo G7.22 (ADPCM)')
            jeżeli nie self._nchannels:
                podnieś Error('# channels nie specified')
            jeżeli nie self._sampwidth:
                podnieś Error('sample width nie specified')
            jeżeli nie self._framerate:
                podnieś Error('sampling rate nie specified')
            self._write_header(datasize)

    def _init_compression(self):
        jeżeli self._comptype == b'G722':
            self._convert = self._lin2adpcm
        albo_inaczej self._comptype w (b'ulaw', b'ULAW'):
            self._convert = self._lin2ulaw
        albo_inaczej self._comptype w (b'alaw', b'ALAW'):
            self._convert = self._lin2alaw

    def _write_header(self, initlength):
        jeżeli self._aifc oraz self._comptype != b'NONE':
            self._init_compression()
        self._file.write(b'FORM')
        jeżeli nie self._nframes:
            self._nframes = initlength // (self._nchannels * self._sampwidth)
        self._datalength = self._nframes * self._nchannels * self._sampwidth
        jeżeli self._datalength & 1:
            self._datalength = self._datalength + 1
        jeżeli self._aifc:
            jeżeli self._comptype w (b'ulaw', b'ULAW', b'alaw', b'ALAW'):
                self._datalength = self._datalength // 2
                jeżeli self._datalength & 1:
                    self._datalength = self._datalength + 1
            albo_inaczej self._comptype == b'G722':
                self._datalength = (self._datalength + 3) // 4
                jeżeli self._datalength & 1:
                    self._datalength = self._datalength + 1
        spróbuj:
            self._form_length_pos = self._file.tell()
        wyjąwszy (AttributeError, OSError):
            self._form_length_pos = Nic
        commlength = self._write_form_length(self._datalength)
        jeżeli self._aifc:
            self._file.write(b'AIFC')
            self._file.write(b'FVER')
            _write_ulong(self._file, 4)
            _write_ulong(self._file, self._version)
        inaczej:
            self._file.write(b'AIFF')
        self._file.write(b'COMM')
        _write_ulong(self._file, commlength)
        _write_short(self._file, self._nchannels)
        jeżeli self._form_length_pos jest nie Nic:
            self._nframes_pos = self._file.tell()
        _write_ulong(self._file, self._nframes)
        jeżeli self._comptype w (b'ULAW', b'ulaw', b'ALAW', b'alaw', b'G722'):
            _write_short(self._file, 8)
        inaczej:
            _write_short(self._file, self._sampwidth * 8)
        _write_float(self._file, self._framerate)
        jeżeli self._aifc:
            self._file.write(self._comptype)
            _write_string(self._file, self._compname)
        self._file.write(b'SSND')
        jeżeli self._form_length_pos jest nie Nic:
            self._ssnd_length_pos = self._file.tell()
        _write_ulong(self._file, self._datalength + 8)
        _write_ulong(self._file, 0)
        _write_ulong(self._file, 0)

    def _write_form_length(self, datalength):
        jeżeli self._aifc:
            commlength = 18 + 5 + len(self._compname)
            jeżeli commlength & 1:
                commlength = commlength + 1
            verslength = 12
        inaczej:
            commlength = 18
            verslength = 0
        _write_ulong(self._file, 4 + verslength + self._marklength + \
                     8 + commlength + 16 + datalength)
        zwróć commlength

    def _patchheader(self):
        curpos = self._file.tell()
        jeżeli self._datawritten & 1:
            datalength = self._datawritten + 1
            self._file.write(b'\x00')
        inaczej:
            datalength = self._datawritten
        jeżeli datalength == self._datalength oraz \
              self._nframes == self._nframeswritten oraz \
              self._marklength == 0:
            self._file.seek(curpos, 0)
            zwróć
        self._file.seek(self._form_length_pos, 0)
        dummy = self._write_form_length(datalength)
        self._file.seek(self._nframes_pos, 0)
        _write_ulong(self._file, self._nframeswritten)
        self._file.seek(self._ssnd_length_pos, 0)
        _write_ulong(self._file, datalength + 8)
        self._file.seek(curpos, 0)
        self._nframes = self._nframeswritten
        self._datalength = datalength

    def _writemarkers(self):
        jeżeli len(self._markers) == 0:
            zwróć
        self._file.write(b'MARK')
        length = 2
        dla marker w self._markers:
            id, pos, name = marker
            length = length + len(name) + 1 + 6
            jeżeli len(name) & 1 == 0:
                length = length + 1
        _write_ulong(self._file, length)
        self._marklength = length + 8
        _write_short(self._file, len(self._markers))
        dla marker w self._markers:
            id, pos, name = marker
            _write_short(self._file, id)
            _write_ulong(self._file, pos)
            _write_string(self._file, name)

def open(f, mode=Nic):
    jeżeli mode jest Nic:
        jeżeli hasattr(f, 'mode'):
            mode = f.mode
        inaczej:
            mode = 'rb'
    jeżeli mode w ('r', 'rb'):
        zwróć Aifc_read(f)
    albo_inaczej mode w ('w', 'wb'):
        zwróć Aifc_write(f)
    inaczej:
        podnieś Error("mode must be 'r', 'rb', 'w', albo 'wb'")

openfp = open # B/W compatibility

jeżeli __name__ == '__main__':
    zaimportuj sys
    jeżeli nie sys.argv[1:]:
        sys.argv.append('/usr/demos/data/audio/bach.aiff')
    fn = sys.argv[1]
    przy open(fn, 'r') jako f:
        print("Reading", fn)
        print("nchannels =", f.getnchannels())
        print("nframes   =", f.getnframes())
        print("sampwidth =", f.getsampwidth())
        print("framerate =", f.getframerate())
        print("comptype  =", f.getcomptype())
        print("compname  =", f.getcompname())
        jeżeli sys.argv[2:]:
            gn = sys.argv[2]
            print("Writing", gn)
            przy open(gn, 'w') jako g:
                g.setparams(f.getparams())
                dopóki 1:
                    data = f.readframes(1024)
                    jeżeli nie data:
                        przerwij
                    g.writeframes(data)
            print("Done.")
