""" Python 'utf-16' Codec


Written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""
zaimportuj codecs, sys

### Codec APIs

encode = codecs.utf_16_encode

def decode(input, errors='strict'):
    zwróć codecs.utf_16_decode(input, errors, Prawda)

klasa IncrementalEncoder(codecs.IncrementalEncoder):
    def __init__(self, errors='strict'):
        codecs.IncrementalEncoder.__init__(self, errors)
        self.encoder = Nic

    def encode(self, input, final=Nieprawda):
        jeżeli self.encoder jest Nic:
            result = codecs.utf_16_encode(input, self.errors)[0]
            jeżeli sys.byteorder == 'little':
                self.encoder = codecs.utf_16_le_encode
            inaczej:
                self.encoder = codecs.utf_16_be_encode
            zwróć result
        zwróć self.encoder(input, self.errors)[0]

    def reset(self):
        codecs.IncrementalEncoder.reset(self)
        self.encoder = Nic

    def getstate(self):
        # state info we zwróć to the caller:
        # 0: stream jest w natural order dla this platform
        # 2: endianness hasn't been determined yet
        # (we're never writing w unnatural order)
        zwróć (2 jeżeli self.encoder jest Nic inaczej 0)

    def setstate(self, state):
        jeżeli state:
            self.encoder = Nic
        inaczej:
            jeżeli sys.byteorder == 'little':
                self.encoder = codecs.utf_16_le_encode
            inaczej:
                self.encoder = codecs.utf_16_be_encode

klasa IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    def __init__(self, errors='strict'):
        codecs.BufferedIncrementalDecoder.__init__(self, errors)
        self.decoder = Nic

    def _buffer_decode(self, input, errors, final):
        jeżeli self.decoder jest Nic:
            (output, consumed, byteorder) = \
                codecs.utf_16_ex_decode(input, errors, 0, final)
            jeżeli byteorder == -1:
                self.decoder = codecs.utf_16_le_decode
            albo_inaczej byteorder == 1:
                self.decoder = codecs.utf_16_be_decode
            albo_inaczej consumed >= 2:
                podnieś UnicodeError("UTF-16 stream does nie start przy BOM")
            zwróć (output, consumed)
        zwróć self.decoder(input, self.errors, final)

    def reset(self):
        codecs.BufferedIncrementalDecoder.reset(self)
        self.decoder = Nic

    def getstate(self):
        # additonal state info z the base klasa must be Nic here,
        # jako it isn't dalejed along to the caller
        state = codecs.BufferedIncrementalDecoder.getstate(self)[0]
        # additional state info we dalej to the caller:
        # 0: stream jest w natural order dla this platform
        # 1: stream jest w unnatural order
        # 2: endianness hasn't been determined yet
        jeżeli self.decoder jest Nic:
            zwróć (state, 2)
        addstate = int((sys.byteorder == "big") !=
                       (self.decoder jest codecs.utf_16_be_decode))
        zwróć (state, addstate)

    def setstate(self, state):
        # state[1] will be ignored by BufferedIncrementalDecoder.setstate()
        codecs.BufferedIncrementalDecoder.setstate(self, state)
        state = state[1]
        jeżeli state == 0:
            self.decoder = (codecs.utf_16_be_decode
                            jeżeli sys.byteorder == "big"
                            inaczej codecs.utf_16_le_decode)
        albo_inaczej state == 1:
            self.decoder = (codecs.utf_16_le_decode
                            jeżeli sys.byteorder == "big"
                            inaczej codecs.utf_16_be_decode)
        inaczej:
            self.decoder = Nic

klasa StreamWriter(codecs.StreamWriter):
    def __init__(self, stream, errors='strict'):
        codecs.StreamWriter.__init__(self, stream, errors)
        self.encoder = Nic

    def reset(self):
        codecs.StreamWriter.reset(self)
        self.encoder = Nic

    def encode(self, input, errors='strict'):
        jeżeli self.encoder jest Nic:
            result = codecs.utf_16_encode(input, errors)
            jeżeli sys.byteorder == 'little':
                self.encoder = codecs.utf_16_le_encode
            inaczej:
                self.encoder = codecs.utf_16_be_encode
            zwróć result
        inaczej:
            zwróć self.encoder(input, errors)

klasa StreamReader(codecs.StreamReader):

    def reset(self):
        codecs.StreamReader.reset(self)
        spróbuj:
            usuń self.decode
        wyjąwszy AttributeError:
            dalej

    def decode(self, input, errors='strict'):
        (object, consumed, byteorder) = \
            codecs.utf_16_ex_decode(input, errors, 0, Nieprawda)
        jeżeli byteorder == -1:
            self.decode = codecs.utf_16_le_decode
        albo_inaczej byteorder == 1:
            self.decode = codecs.utf_16_be_decode
        albo_inaczej consumed>=2:
            podnieś UnicodeError("UTF-16 stream does nie start przy BOM")
        zwróć (object, consumed)

### encodings module API

def getregentry():
    zwróć codecs.CodecInfo(
        name='utf-16',
        encode=encode,
        decode=decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
