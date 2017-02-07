""" Python 'undefined' Codec

    This codec will always podnieś a ValueError exception when being
    used. It jest intended dla use by the site.py file to switch off
    automatic string to Unicode coercion.

Written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""
zaimportuj codecs

### Codec APIs

klasa Codec(codecs.Codec):

    def encode(self,input,errors='strict'):
        podnieś UnicodeError("undefined encoding")

    def decode(self,input,errors='strict'):
        podnieś UnicodeError("undefined encoding")

klasa IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=Nieprawda):
        podnieś UnicodeError("undefined encoding")

klasa IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input, final=Nieprawda):
        podnieś UnicodeError("undefined encoding")

klasa StreamWriter(Codec,codecs.StreamWriter):
    dalej

klasa StreamReader(Codec,codecs.StreamReader):
    dalej

### encodings module API

def getregentry():
    zwróć codecs.CodecInfo(
        name='undefined',
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader,
    )
