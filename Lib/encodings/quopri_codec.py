"""Codec dla quoted-printable encoding.

This codec de/encodes z bytes to bytes.
"""

zaimportuj codecs
zaimportuj quopri
z io zaimportuj BytesIO

def quopri_encode(input, errors='strict'):
    assert errors == 'strict'
    f = BytesIO(input)
    g = BytesIO()
    quopri.encode(f, g, 1)
    zwróć (g.getvalue(), len(input))

def quopri_decode(input, errors='strict'):
    assert errors == 'strict'
    f = BytesIO(input)
    g = BytesIO()
    quopri.decode(f, g)
    zwróć (g.getvalue(), len(input))

klasa Codec(codecs.Codec):
    def encode(self, input, errors='strict'):
        zwróć quopri_encode(input, errors)
    def decode(self, input, errors='strict'):
        zwróć quopri_decode(input, errors)

klasa IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=Nieprawda):
        zwróć quopri_encode(input, self.errors)[0]

klasa IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input, final=Nieprawda):
        zwróć quopri_decode(input, self.errors)[0]

klasa StreamWriter(Codec, codecs.StreamWriter):
    charbuffertype = bytes

klasa StreamReader(Codec, codecs.StreamReader):
    charbuffertype = bytes

# encodings module API

def getregentry():
    zwróć codecs.CodecInfo(
        name='quopri',
        encode=quopri_encode,
        decode=quopri_decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader,
        _is_text_encoding=Nieprawda,
    )
