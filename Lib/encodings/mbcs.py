""" Python 'mbcs' Codec dla Windows


Cloned by Mark Hammond (mhammond@skippinet.com.au) z ascii.py,
which was written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""
# Import them explicitly to cause an ImportError
# on non-Windows systems
z codecs zaimportuj mbcs_encode, mbcs_decode
# dla IncrementalDecoder, IncrementalEncoder, ...
zaimportuj codecs

### Codec APIs

encode = mbcs_encode

def decode(input, errors='strict'):
    zwróć mbcs_decode(input, errors, Prawda)

klasa IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=Nieprawda):
        zwróć mbcs_encode(input, self.errors)[0]

klasa IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    _buffer_decode = mbcs_decode

klasa StreamWriter(codecs.StreamWriter):
    encode = mbcs_encode

klasa StreamReader(codecs.StreamReader):
    decode = mbcs_decode

### encodings module API

def getregentry():
    zwróć codecs.CodecInfo(
        name='mbcs',
        encode=encode,
        decode=decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
