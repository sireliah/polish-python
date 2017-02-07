"""Python 'base64_codec' Codec - base64 content transfer encoding.

This codec de/encodes z bytes to bytes.

Written by Marc-Andre Lemburg (mal@lemburg.com).
"""

zaimportuj codecs
zaimportuj base64

### Codec APIs

def base64_encode(input, errors='strict'):
    assert errors == 'strict'
    zwróć (base64.encodebytes(input), len(input))

def base64_decode(input, errors='strict'):
    assert errors == 'strict'
    zwróć (base64.decodebytes(input), len(input))

klasa Codec(codecs.Codec):
    def encode(self, input, errors='strict'):
        zwróć base64_encode(input, errors)
    def decode(self, input, errors='strict'):
        zwróć base64_decode(input, errors)

klasa IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=Nieprawda):
        assert self.errors == 'strict'
        zwróć base64.encodebytes(input)

klasa IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input, final=Nieprawda):
        assert self.errors == 'strict'
        zwróć base64.decodebytes(input)

klasa StreamWriter(Codec, codecs.StreamWriter):
    charbuffertype = bytes

klasa StreamReader(Codec, codecs.StreamReader):
    charbuffertype = bytes

### encodings module API

def getregentry():
    zwróć codecs.CodecInfo(
        name='base64',
        encode=base64_encode,
        decode=base64_decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader,
        _is_text_encoding=Nieprawda,
    )
