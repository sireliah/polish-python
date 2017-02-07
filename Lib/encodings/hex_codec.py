"""Python 'hex_codec' Codec - 2-digit hex content transfer encoding.

This codec de/encodes z bytes to bytes.

Written by Marc-Andre Lemburg (mal@lemburg.com).
"""

zaimportuj codecs
zaimportuj binascii

### Codec APIs

def hex_encode(input, errors='strict'):
    assert errors == 'strict'
    zwróć (binascii.b2a_hex(input), len(input))

def hex_decode(input, errors='strict'):
    assert errors == 'strict'
    zwróć (binascii.a2b_hex(input), len(input))

klasa Codec(codecs.Codec):
    def encode(self, input, errors='strict'):
        zwróć hex_encode(input, errors)
    def decode(self, input, errors='strict'):
        zwróć hex_decode(input, errors)

klasa IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=Nieprawda):
        assert self.errors == 'strict'
        zwróć binascii.b2a_hex(input)

klasa IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input, final=Nieprawda):
        assert self.errors == 'strict'
        zwróć binascii.a2b_hex(input)

klasa StreamWriter(Codec, codecs.StreamWriter):
    charbuffertype = bytes

klasa StreamReader(Codec, codecs.StreamReader):
    charbuffertype = bytes

### encodings module API

def getregentry():
    zwróć codecs.CodecInfo(
        name='hex',
        encode=hex_encode,
        decode=hex_decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader,
        _is_text_encoding=Nieprawda,
    )
