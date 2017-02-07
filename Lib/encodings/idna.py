# This module implements the RFCs 3490 (IDNA) oraz 3491 (Nameprep)

zaimportuj stringprep, re, codecs
z unicodedata zaimportuj ucd_3_2_0 jako unicodedata

# IDNA section 3.1
dots = re.compile("[\u002E\u3002\uFF0E\uFF61]")

# IDNA section 5
ace_prefix = b"xn--"
sace_prefix = "xn--"

# This assumes query strings, so AllowUnassigned jest true
def nameprep(label):
    # Map
    newlabel = []
    dla c w label:
        jeżeli stringprep.in_table_b1(c):
            # Map to nothing
            kontynuuj
        newlabel.append(stringprep.map_table_b2(c))
    label = "".join(newlabel)

    # Normalize
    label = unicodedata.normalize("NFKC", label)

    # Prohibit
    dla c w label:
        jeżeli stringprep.in_table_c12(c) albo \
           stringprep.in_table_c22(c) albo \
           stringprep.in_table_c3(c) albo \
           stringprep.in_table_c4(c) albo \
           stringprep.in_table_c5(c) albo \
           stringprep.in_table_c6(c) albo \
           stringprep.in_table_c7(c) albo \
           stringprep.in_table_c8(c) albo \
           stringprep.in_table_c9(c):
            podnieś UnicodeError("Invalid character %r" % c)

    # Check bidi
    RandAL = [stringprep.in_table_d1(x) dla x w label]
    dla c w RandAL:
        jeżeli c:
            # There jest a RandAL char w the string. Must perform further
            # tests:
            # 1) The characters w section 5.8 MUST be prohibited.
            # This jest table C.8, which was already checked
            # 2) If a string contains any RandALCat character, the string
            # MUST NOT contain any LCat character.
            jeżeli any(stringprep.in_table_d2(x) dla x w label):
                podnieś UnicodeError("Violation of BIDI requirement 2")

            # 3) If a string contains any RandALCat character, a
            # RandALCat character MUST be the first character of the
            # string, oraz a RandALCat character MUST be the last
            # character of the string.
            jeżeli nie RandAL[0] albo nie RandAL[-1]:
                podnieś UnicodeError("Violation of BIDI requirement 3")

    zwróć label

def ToASCII(label):
    spróbuj:
        # Step 1: try ASCII
        label = label.encode("ascii")
    wyjąwszy UnicodeError:
        dalej
    inaczej:
        # Skip to step 3: UseSTD3ASCIIRules jest false, so
        # Skip to step 8.
        jeżeli 0 < len(label) < 64:
            zwróć label
        podnieś UnicodeError("label empty albo too long")

    # Step 2: nameprep
    label = nameprep(label)

    # Step 3: UseSTD3ASCIIRules jest false
    # Step 4: try ASCII
    spróbuj:
        label = label.encode("ascii")
    wyjąwszy UnicodeError:
        dalej
    inaczej:
        # Skip to step 8.
        jeżeli 0 < len(label) < 64:
            zwróć label
        podnieś UnicodeError("label empty albo too long")

    # Step 5: Check ACE prefix
    jeżeli label.startswith(sace_prefix):
        podnieś UnicodeError("Label starts przy ACE prefix")

    # Step 6: Encode przy PUNYCODE
    label = label.encode("punycode")

    # Step 7: Prepend ACE prefix
    label = ace_prefix + label

    # Step 8: Check size
    jeżeli 0 < len(label) < 64:
        zwróć label
    podnieś UnicodeError("label empty albo too long")

def ToUnicode(label):
    # Step 1: Check dla ASCII
    jeżeli isinstance(label, bytes):
        pure_ascii = Prawda
    inaczej:
        spróbuj:
            label = label.encode("ascii")
            pure_ascii = Prawda
        wyjąwszy UnicodeError:
            pure_ascii = Nieprawda
    jeżeli nie pure_ascii:
        # Step 2: Perform nameprep
        label = nameprep(label)
        # It doesn't say this, but apparently, it should be ASCII now
        spróbuj:
            label = label.encode("ascii")
        wyjąwszy UnicodeError:
            podnieś UnicodeError("Invalid character w IDN label")
    # Step 3: Check dla ACE prefix
    jeżeli nie label.startswith(ace_prefix):
        zwróć str(label, "ascii")

    # Step 4: Remove ACE prefix
    label1 = label[len(ace_prefix):]

    # Step 5: Decode using PUNYCODE
    result = label1.decode("punycode")

    # Step 6: Apply ToASCII
    label2 = ToASCII(result)

    # Step 7: Compare the result of step 6 przy the one of step 3
    # label2 will already be w lower case.
    jeżeli str(label, "ascii").lower() != str(label2, "ascii"):
        podnieś UnicodeError("IDNA does nie round-trip", label, label2)

    # Step 8: zwróć the result of step 5
    zwróć result

### Codec APIs

klasa Codec(codecs.Codec):
    def encode(self, input, errors='strict'):

        jeżeli errors != 'strict':
            # IDNA jest quite clear that implementations must be strict
            podnieś UnicodeError("unsupported error handling "+errors)

        jeżeli nie input:
            zwróć b'', 0

        spróbuj:
            result = input.encode('ascii')
        wyjąwszy UnicodeEncodeError:
            dalej
        inaczej:
            # ASCII name: fast path
            labels = result.split(b'.')
            dla label w labels[:-1]:
                jeżeli nie (0 < len(label) < 64):
                    podnieś UnicodeError("label empty albo too long")
            jeżeli len(labels[-1]) >= 64:
                podnieś UnicodeError("label too long")
            zwróć result, len(input)

        result = bytearray()
        labels = dots.split(input)
        jeżeli labels oraz nie labels[-1]:
            trailing_dot = b'.'
            usuń labels[-1]
        inaczej:
            trailing_dot = b''
        dla label w labels:
            jeżeli result:
                # Join przy U+002E
                result.extend(b'.')
            result.extend(ToASCII(label))
        zwróć bytes(result+trailing_dot), len(input)

    def decode(self, input, errors='strict'):

        jeżeli errors != 'strict':
            podnieś UnicodeError("Unsupported error handling "+errors)

        jeżeli nie input:
            zwróć "", 0

        # IDNA allows decoding to operate on Unicode strings, too.
        jeżeli nie isinstance(input, bytes):
            # XXX obviously wrong, see #3232
            input = bytes(input)

        jeżeli ace_prefix nie w input:
            # Fast path
            spróbuj:
                zwróć input.decode('ascii'), len(input)
            wyjąwszy UnicodeDecodeError:
                dalej

        labels = input.split(b".")

        jeżeli labels oraz len(labels[-1]) == 0:
            trailing_dot = '.'
            usuń labels[-1]
        inaczej:
            trailing_dot = ''

        result = []
        dla label w labels:
            result.append(ToUnicode(label))

        zwróć ".".join(result)+trailing_dot, len(input)

klasa IncrementalEncoder(codecs.BufferedIncrementalEncoder):
    def _buffer_encode(self, input, errors, final):
        jeżeli errors != 'strict':
            # IDNA jest quite clear that implementations must be strict
            podnieś UnicodeError("unsupported error handling "+errors)

        jeżeli nie input:
            zwróć (b'', 0)

        labels = dots.split(input)
        trailing_dot = b''
        jeżeli labels:
            jeżeli nie labels[-1]:
                trailing_dot = b'.'
                usuń labels[-1]
            albo_inaczej nie final:
                # Keep potentially unfinished label until the next call
                usuń labels[-1]
                jeżeli labels:
                    trailing_dot = b'.'

        result = bytearray()
        size = 0
        dla label w labels:
            jeżeli size:
                # Join przy U+002E
                result.extend(b'.')
                size += 1
            result.extend(ToASCII(label))
            size += len(label)

        result += trailing_dot
        size += len(trailing_dot)
        zwróć (bytes(result), size)

klasa IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    def _buffer_decode(self, input, errors, final):
        jeżeli errors != 'strict':
            podnieś UnicodeError("Unsupported error handling "+errors)

        jeżeli nie input:
            zwróć ("", 0)

        # IDNA allows decoding to operate on Unicode strings, too.
        jeżeli isinstance(input, str):
            labels = dots.split(input)
        inaczej:
            # Must be ASCII string
            input = str(input, "ascii")
            labels = input.split(".")

        trailing_dot = ''
        jeżeli labels:
            jeżeli nie labels[-1]:
                trailing_dot = '.'
                usuń labels[-1]
            albo_inaczej nie final:
                # Keep potentially unfinished label until the next call
                usuń labels[-1]
                jeżeli labels:
                    trailing_dot = '.'

        result = []
        size = 0
        dla label w labels:
            result.append(ToUnicode(label))
            jeżeli size:
                size += 1
            size += len(label)

        result = ".".join(result) + trailing_dot
        size += len(trailing_dot)
        zwróć (result, size)

klasa StreamWriter(Codec,codecs.StreamWriter):
    dalej

klasa StreamReader(Codec,codecs.StreamReader):
    dalej

### encodings module API

def getregentry():
    zwróć codecs.CodecInfo(
        name='idna',
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader,
    )
