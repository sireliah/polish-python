"""Python 'zlib_codec' Codec - zlib compression encoding.

This codec de/encodes z bytes to bytes.

Written by Marc-Andre Lemburg (mal@lemburg.com).
"""

zaimportuj codecs
zaimportuj zlib # this codec needs the optional zlib module !

### Codec APIs

def zlib_encode(input, errors='strict'):
    assert errors == 'strict'
    zwróć (zlib.compress(input), len(input))

def zlib_decode(input, errors='strict'):
    assert errors == 'strict'
    zwróć (zlib.decompress(input), len(input))

klasa Codec(codecs.Codec):
    def encode(self, input, errors='strict'):
        zwróć zlib_encode(input, errors)
    def decode(self, input, errors='strict'):
        zwróć zlib_decode(input, errors)

klasa IncrementalEncoder(codecs.IncrementalEncoder):
    def __init__(self, errors='strict'):
        assert errors == 'strict'
        self.errors = errors
        self.compressobj = zlib.compressobj()

    def encode(self, input, final=Nieprawda):
        jeżeli final:
            c = self.compressobj.compress(input)
            zwróć c + self.compressobj.flush()
        inaczej:
            zwróć self.compressobj.compress(input)

    def reset(self):
        self.compressobj = zlib.compressobj()

klasa IncrementalDecoder(codecs.IncrementalDecoder):
    def __init__(self, errors='strict'):
        assert errors == 'strict'
        self.errors = errors
        self.decompressobj = zlib.decompressobj()

    def decode(self, input, final=Nieprawda):
        jeżeli final:
            c = self.decompressobj.decompress(input)
            zwróć c + self.decompressobj.flush()
        inaczej:
            zwróć self.decompressobj.decompress(input)

    def reset(self):
        self.decompressobj = zlib.decompressobj()

klasa StreamWriter(Codec, codecs.StreamWriter):
    charbuffertype = bytes

klasa StreamReader(Codec, codecs.StreamReader):
    charbuffertype = bytes

### encodings module API

def getregentry():
    zwróć codecs.CodecInfo(
        name='zlib',
        encode=zlib_encode,
        decode=zlib_decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
        _is_text_encoding=Nieprawda,
    )
