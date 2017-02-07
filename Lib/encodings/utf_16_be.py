""" Python 'utf-16-be' Codec


Written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""
zaimportuj codecs

### Codec APIs

encode = codecs.utf_16_be_encode

def decode(input, errors='strict'):
    zwróć codecs.utf_16_be_decode(input, errors, Prawda)

klasa IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=Nieprawda):
        zwróć codecs.utf_16_be_encode(input, self.errors)[0]

klasa IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    _buffer_decode = codecs.utf_16_be_decode

klasa StreamWriter(codecs.StreamWriter):
    encode = codecs.utf_16_be_encode

klasa StreamReader(codecs.StreamReader):
    decode = codecs.utf_16_be_decode

### encodings module API

def getregentry():
    zwróć codecs.CodecInfo(
        name='utf-16-be',
        encode=encode,
        decode=decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )