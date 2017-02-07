"""
Python 'utf-32-le' Codec
"""
zaimportuj codecs

### Codec APIs

encode = codecs.utf_32_le_encode

def decode(input, errors='strict'):
    zwróć codecs.utf_32_le_decode(input, errors, Prawda)

klasa IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=Nieprawda):
        zwróć codecs.utf_32_le_encode(input, self.errors)[0]

klasa IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    _buffer_decode = codecs.utf_32_le_decode

klasa StreamWriter(codecs.StreamWriter):
    encode = codecs.utf_32_le_encode

klasa StreamReader(codecs.StreamReader):
    decode = codecs.utf_32_le_decode

### encodings module API

def getregentry():
    zwróć codecs.CodecInfo(
        name='utf-32-le',
        encode=encode,
        decode=decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
