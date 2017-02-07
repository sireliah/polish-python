"""Python 'bz2_codec' Codec - bz2 compression encoding.

This codec de/encodes z bytes to bytes oraz jest therefore usable with
bytes.transform() oraz bytes.untransform().

Adapted by Raymond Hettinger z zlib_codec.py which was written
by Marc-Andre Lemburg (mal@lemburg.com).
"""

zaimportuj codecs
zaimportuj bz2 # this codec needs the optional bz2 module !

### Codec APIs

def bz2_encode(input, errors='strict'):
    assert errors == 'strict'
    zwróć (bz2.compress(input), len(input))

def bz2_decode(input, errors='strict'):
    assert errors == 'strict'
    zwróć (bz2.decompress(input), len(input))

klasa Codec(codecs.Codec):
    def encode(self, input, errors='strict'):
        zwróć bz2_encode(input, errors)
    def decode(self, input, errors='strict'):
        zwróć bz2_decode(input, errors)

klasa IncrementalEncoder(codecs.IncrementalEncoder):
    def __init__(self, errors='strict'):
        assert errors == 'strict'
        self.errors = errors
        self.compressobj = bz2.BZ2Compressor()

    def encode(self, input, final=Nieprawda):
        jeżeli final:
            c = self.compressobj.compress(input)
            zwróć c + self.compressobj.flush()
        inaczej:
            zwróć self.compressobj.compress(input)

    def reset(self):
        self.compressobj = bz2.BZ2Compressor()

klasa IncrementalDecoder(codecs.IncrementalDecoder):
    def __init__(self, errors='strict'):
        assert errors == 'strict'
        self.errors = errors
        self.decompressobj = bz2.BZ2Decompressor()

    def decode(self, input, final=Nieprawda):
        spróbuj:
            zwróć self.decompressobj.decompress(input)
        wyjąwszy EOFError:
            zwróć ''

    def reset(self):
        self.decompressobj = bz2.BZ2Decompressor()

klasa StreamWriter(Codec, codecs.StreamWriter):
    charbuffertype = bytes

klasa StreamReader(Codec, codecs.StreamReader):
    charbuffertype = bytes

### encodings module API

def getregentry():
    zwróć codecs.CodecInfo(
        name="bz2",
        encode=bz2_encode,
        decode=bz2_decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader,
        _is_text_encoding=Nieprawda,
    )
