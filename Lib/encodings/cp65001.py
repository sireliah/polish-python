"""
Code page 65001: Windows UTF-8 (CP_UTF8).
"""

zaimportuj codecs
zaimportuj functools

jeżeli nie hasattr(codecs, 'code_page_encode'):
    podnieś LookupError("cp65001 encoding jest only available on Windows")

### Codec APIs

encode = functools.partial(codecs.code_page_encode, 65001)
_decode = functools.partial(codecs.code_page_decode, 65001)

def decode(input, errors='strict'):
    zwróć codecs.code_page_decode(65001, input, errors, Prawda)

klasa IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=Nieprawda):
        zwróć encode(input, self.errors)[0]

klasa IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    _buffer_decode = _decode

klasa StreamWriter(codecs.StreamWriter):
    encode = encode

klasa StreamReader(codecs.StreamReader):
    decode = _decode

### encodings module API

def getregentry():
    zwróć codecs.CodecInfo(
        name='cp65001',
        encode=encode,
        decode=decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
