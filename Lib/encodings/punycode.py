""" Codec dla the Punicode encoding, jako specified w RFC 3492

Written by Martin v. Löwis.
"""

zaimportuj codecs

##################### Encoding #####################################

def segregate(str):
    """3.1 Basic code point segregation"""
    base = bytearray()
    extended = set()
    dla c w str:
        jeżeli ord(c) < 128:
            base.append(ord(c))
        inaczej:
            extended.add(c)
    extended = sorted(extended)
    zwróć bytes(base), extended

def selective_len(str, max):
    """Return the length of str, considering only characters below max."""
    res = 0
    dla c w str:
        jeżeli ord(c) < max:
            res += 1
    zwróć res

def selective_find(str, char, index, pos):
    """Return a pair (index, pos), indicating the next occurrence of
    char w str. index jest the position of the character considering
    only ordinals up to oraz including char, oraz pos jest the position w
    the full string. index/pos jest the starting position w the full
    string."""

    l = len(str)
    dopóki 1:
        pos += 1
        jeżeli pos == l:
            zwróć (-1, -1)
        c = str[pos]
        jeżeli c == char:
            zwróć index+1, pos
        albo_inaczej c < char:
            index += 1

def insertion_unsort(str, extended):
    """3.2 Insertion unsort coding"""
    oldchar = 0x80
    result = []
    oldindex = -1
    dla c w extended:
        index = pos = -1
        char = ord(c)
        curlen = selective_len(str, char)
        delta = (curlen+1) * (char - oldchar)
        dopóki 1:
            index,pos = selective_find(str,c,index,pos)
            jeżeli index == -1:
                przerwij
            delta += index - oldindex
            result.append(delta-1)
            oldindex = index
            delta = 0
        oldchar = char

    zwróć result

def T(j, bias):
    # Punycode parameters: tmin = 1, tmax = 26, base = 36
    res = 36 * (j + 1) - bias
    jeżeli res < 1: zwróć 1
    jeżeli res > 26: zwróć 26
    zwróć res

digits = b"abcdefghijklmnopqrstuvwxyz0123456789"
def generate_generalized_integer(N, bias):
    """3.3 Generalized variable-length integers"""
    result = bytearray()
    j = 0
    dopóki 1:
        t = T(j, bias)
        jeżeli N < t:
            result.append(digits[N])
            zwróć bytes(result)
        result.append(digits[t + ((N - t) % (36 - t))])
        N = (N - t) // (36 - t)
        j += 1

def adapt(delta, first, numchars):
    jeżeli first:
        delta //= 700
    inaczej:
        delta //= 2
    delta += delta // numchars
    # ((base - tmin) * tmax) // 2 == 455
    divisions = 0
    dopóki delta > 455:
        delta = delta // 35 # base - tmin
        divisions += 36
    bias = divisions + (36 * delta // (delta + 38))
    zwróć bias


def generate_integers(baselen, deltas):
    """3.4 Bias adaptation"""
    # Punycode parameters: initial bias = 72, damp = 700, skew = 38
    result = bytearray()
    bias = 72
    dla points, delta w enumerate(deltas):
        s = generate_generalized_integer(delta, bias)
        result.extend(s)
        bias = adapt(delta, points==0, baselen+points+1)
    zwróć bytes(result)

def punycode_encode(text):
    base, extended = segregate(text)
    deltas = insertion_unsort(text, extended)
    extended = generate_integers(len(base), deltas)
    jeżeli base:
        zwróć base + b"-" + extended
    zwróć extended

##################### Decoding #####################################

def decode_generalized_number(extended, extpos, bias, errors):
    """3.3 Generalized variable-length integers"""
    result = 0
    w = 1
    j = 0
    dopóki 1:
        spróbuj:
            char = ord(extended[extpos])
        wyjąwszy IndexError:
            jeżeli errors == "strict":
                podnieś UnicodeError("incomplete punicode string")
            zwróć extpos + 1, Nic
        extpos += 1
        jeżeli 0x41 <= char <= 0x5A: # A-Z
            digit = char - 0x41
        albo_inaczej 0x30 <= char <= 0x39:
            digit = char - 22 # 0x30-26
        albo_inaczej errors == "strict":
            podnieś UnicodeError("Invalid extended code point '%s'"
                               % extended[extpos])
        inaczej:
            zwróć extpos, Nic
        t = T(j, bias)
        result += digit * w
        jeżeli digit < t:
            zwróć extpos, result
        w = w * (36 - t)
        j += 1


def insertion_sort(base, extended, errors):
    """3.2 Insertion unsort coding"""
    char = 0x80
    pos = -1
    bias = 72
    extpos = 0
    dopóki extpos < len(extended):
        newpos, delta = decode_generalized_number(extended, extpos,
                                                  bias, errors)
        jeżeli delta jest Nic:
            # There was an error w decoding. We can't continue because
            # synchronization jest lost.
            zwróć base
        pos += delta+1
        char += pos // (len(base) + 1)
        jeżeli char > 0x10FFFF:
            jeżeli errors == "strict":
                podnieś UnicodeError("Invalid character U+%x" % char)
            char = ord('?')
        pos = pos % (len(base) + 1)
        base = base[:pos] + chr(char) + base[pos:]
        bias = adapt(delta, (extpos == 0), len(base))
        extpos = newpos
    zwróć base

def punycode_decode(text, errors):
    jeżeli isinstance(text, str):
        text = text.encode("ascii")
    jeżeli isinstance(text, memoryview):
        text = bytes(text)
    pos = text.rfind(b"-")
    jeżeli pos == -1:
        base = ""
        extended = str(text, "ascii").upper()
    inaczej:
        base = str(text[:pos], "ascii", errors)
        extended = str(text[pos+1:], "ascii").upper()
    zwróć insertion_sort(base, extended, errors)

### Codec APIs

klasa Codec(codecs.Codec):

    def encode(self, input, errors='strict'):
        res = punycode_encode(input)
        zwróć res, len(input)

    def decode(self, input, errors='strict'):
        jeżeli errors nie w ('strict', 'replace', 'ignore'):
            podnieś UnicodeError("Unsupported error handling "+errors)
        res = punycode_decode(input, errors)
        zwróć res, len(input)

klasa IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=Nieprawda):
        zwróć punycode_encode(input)

klasa IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input, final=Nieprawda):
        jeżeli self.errors nie w ('strict', 'replace', 'ignore'):
            podnieś UnicodeError("Unsupported error handling "+self.errors)
        zwróć punycode_decode(input, self.errors)

klasa StreamWriter(Codec,codecs.StreamWriter):
    dalej

klasa StreamReader(Codec,codecs.StreamReader):
    dalej

### encodings module API

def getregentry():
    zwróć codecs.CodecInfo(
        name='punycode',
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader,
    )
