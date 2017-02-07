""" Python 'utf-8-sig' Codec
This work similar to UTF-8 przy the following changes:

* On encoding/writing a UTF-8 encoded BOM will be prepended/written jako the
  first three bytes.

* On decoding/reading jeżeli the first three bytes are a UTF-8 encoded BOM, these
  bytes will be skipped.
"""
zaimportuj codecs

### Codec APIs

def encode(input, errors='strict'):
    zwróć (codecs.BOM_UTF8 + codecs.utf_8_encode(input, errors)[0],
            len(input))

def decode(input, errors='strict'):
    prefix = 0
    jeżeli input[:3] == codecs.BOM_UTF8:
        input = input[3:]
        prefix = 3
    (output, consumed) = codecs.utf_8_decode(input, errors, Prawda)
    zwróć (output, consumed+prefix)

klasa IncrementalEncoder(codecs.IncrementalEncoder):
    def __init__(self, errors='strict'):
        codecs.IncrementalEncoder.__init__(self, errors)
        self.first = 1

    def encode(self, input, final=Nieprawda):
        jeżeli self.first:
            self.first = 0
            zwróć codecs.BOM_UTF8 + \
                   codecs.utf_8_encode(input, self.errors)[0]
        inaczej:
            zwróć codecs.utf_8_encode(input, self.errors)[0]

    def reset(self):
        codecs.IncrementalEncoder.reset(self)
        self.first = 1

    def getstate(self):
        zwróć self.first

    def setstate(self, state):
        self.first = state

klasa IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    def __init__(self, errors='strict'):
        codecs.BufferedIncrementalDecoder.__init__(self, errors)
        self.first = 1

    def _buffer_decode(self, input, errors, final):
        jeżeli self.first:
            jeżeli len(input) < 3:
                jeżeli codecs.BOM_UTF8.startswith(input):
                    # nie enough data to decide jeżeli this really jest a BOM
                    # => try again on the next call
                    zwróć ("", 0)
                inaczej:
                    self.first = 0
            inaczej:
                self.first = 0
                jeżeli input[:3] == codecs.BOM_UTF8:
                    (output, consumed) = \
                       codecs.utf_8_decode(input[3:], errors, final)
                    zwróć (output, consumed+3)
        zwróć codecs.utf_8_decode(input, errors, final)

    def reset(self):
        codecs.BufferedIncrementalDecoder.reset(self)
        self.first = 1

    def getstate(self):
        state = codecs.BufferedIncrementalDecoder.getstate(self)
        # state[1] must be 0 here, jako it isn't dalejed along to the caller
        zwróć (state[0], self.first)

    def setstate(self, state):
        # state[1] will be ignored by BufferedIncrementalDecoder.setstate()
        codecs.BufferedIncrementalDecoder.setstate(self, state)
        self.first = state[1]

klasa StreamWriter(codecs.StreamWriter):
    def reset(self):
        codecs.StreamWriter.reset(self)
        spróbuj:
            usuń self.encode
        wyjąwszy AttributeError:
            dalej

    def encode(self, input, errors='strict'):
        self.encode = codecs.utf_8_encode
        zwróć encode(input, errors)

klasa StreamReader(codecs.StreamReader):
    def reset(self):
        codecs.StreamReader.reset(self)
        spróbuj:
            usuń self.decode
        wyjąwszy AttributeError:
            dalej

    def decode(self, input, errors='strict'):
        jeżeli len(input) < 3:
            jeżeli codecs.BOM_UTF8.startswith(input):
                # nie enough data to decide jeżeli this jest a BOM
                # => try again on the next call
                zwróć ("", 0)
        albo_inaczej input[:3] == codecs.BOM_UTF8:
            self.decode = codecs.utf_8_decode
            (output, consumed) = codecs.utf_8_decode(input[3:],errors)
            zwróć (output, consumed+3)
        # (inaczej) no BOM present
        self.decode = codecs.utf_8_decode
        zwróć codecs.utf_8_decode(input, errors)

### encodings module API

def getregentry():
    zwróć codecs.CodecInfo(
        name='utf-8-sig',
        encode=encode,
        decode=decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
