""" Python 'unicode-internal' Codec


Written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""
zaimportuj codecs

### Codec APIs

klasa Codec(codecs.Codec):

    # Note: Binding these jako C functions will result w the klasa nie
    # converting them to methods. This jest intended.
    encode = codecs.unicode_internal_encode
    decode = codecs.unicode_internal_decode

klasa IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=Nieprawda):
        zwróć codecs.unicode_internal_encode(input, self.errors)[0]

klasa IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input, final=Nieprawda):
        zwróć codecs.unicode_internal_decode(input, self.errors)[0]

klasa StreamWriter(Codec,codecs.StreamWriter):
    dalej

klasa StreamReader(Codec,codecs.StreamReader):
    dalej

### encodings module API

def getregentry():
    zwróć codecs.CodecInfo(
        name='unicode-internal',
        encode=Codec.encode,
        decode=Codec.decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader,
    )
