""" Python 'utf-7' Codec

Written by Brian Quinlan (brian@sweetapp.com).
"""
zaimportuj codecs

### Codec APIs

encode = codecs.utf_7_encode

def decode(input, errors='strict'):
    zwróć codecs.utf_7_decode(input, errors, Prawda)

klasa IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=Nieprawda):
        zwróć codecs.utf_7_encode(input, self.errors)[0]

klasa IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    _buffer_decode = codecs.utf_7_decode

klasa StreamWriter(codecs.StreamWriter):
    encode = codecs.utf_7_encode

klasa StreamReader(codecs.StreamReader):
    decode = codecs.utf_7_decode

### encodings module API

def getregentry():
    zwróć codecs.CodecInfo(
        name='utf-7',
        encode=encode,
        decode=decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
