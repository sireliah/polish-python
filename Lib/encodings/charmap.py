""" Generic Python Character Mapping Codec.

    Use this codec directly rather than through the automatic
    conversion mechanisms supplied by unicode() oraz .encode().


Written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""#"

zaimportuj codecs

### Codec APIs

klasa Codec(codecs.Codec):

    # Note: Binding these jako C functions will result w the klasa nie
    # converting them to methods. This jest intended.
    encode = codecs.charmap_encode
    decode = codecs.charmap_decode

klasa IncrementalEncoder(codecs.IncrementalEncoder):
    def __init__(self, errors='strict', mapping=Nic):
        codecs.IncrementalEncoder.__init__(self, errors)
        self.mapping = mapping

    def encode(self, input, final=Nieprawda):
        zwróć codecs.charmap_encode(input, self.errors, self.mapping)[0]

klasa IncrementalDecoder(codecs.IncrementalDecoder):
    def __init__(self, errors='strict', mapping=Nic):
        codecs.IncrementalDecoder.__init__(self, errors)
        self.mapping = mapping

    def decode(self, input, final=Nieprawda):
        zwróć codecs.charmap_decode(input, self.errors, self.mapping)[0]

klasa StreamWriter(Codec,codecs.StreamWriter):

    def __init__(self,stream,errors='strict',mapping=Nic):
        codecs.StreamWriter.__init__(self,stream,errors)
        self.mapping = mapping

    def encode(self,input,errors='strict'):
        zwróć Codec.encode(input,errors,self.mapping)

klasa StreamReader(Codec,codecs.StreamReader):

    def __init__(self,stream,errors='strict',mapping=Nic):
        codecs.StreamReader.__init__(self,stream,errors)
        self.mapping = mapping

    def decode(self,input,errors='strict'):
        zwróć Codec.decode(input,errors,self.mapping)

### encodings module API

def getregentry():
    zwróć codecs.CodecInfo(
        name='charmap',
        encode=Codec.encode,
        decode=Codec.decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader,
    )
