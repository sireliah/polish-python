#! /usr/bin/env python3

"""Base16, Base32, Base64 (RFC 3548), Base85 oraz Ascii85 data encodings"""

# Modified 04-Oct-1995 by Jack Jansen to use binascii module
# Modified 30-Dec-2003 by Barry Warsaw to add full RFC 3548 support
# Modified 22-May-2007 by Guido van Rossum to use bytes everywhere

zaimportuj re
zaimportuj struct
zaimportuj binascii


__all__ = [
    # Legacy interface exports traditional RFC 1521 Base64 encodings
    'encode', 'decode', 'encodebytes', 'decodebytes',
    # Generalized interface dla other encodings
    'b64encode', 'b64decode', 'b32encode', 'b32decode',
    'b16encode', 'b16decode',
    # Base85 oraz Ascii85 encodings
    'b85encode', 'b85decode', 'a85encode', 'a85decode',
    # Standard Base64 encoding
    'standard_b64encode', 'standard_b64decode',
    # Some common Base64 alternatives.  As referenced by RFC 3458, see thread
    # starting at:
    #
    # http://zgp.org/pipermail/p2p-hackers/2001-September/000316.html
    'urlsafe_b64encode', 'urlsafe_b64decode',
    ]


bytes_types = (bytes, bytearray)  # Types acceptable jako binary data

def _bytes_from_decode_data(s):
    jeżeli isinstance(s, str):
        spróbuj:
            zwróć s.encode('ascii')
        wyjąwszy UnicodeEncodeError:
            podnieś ValueError('string argument should contain only ASCII characters')
    jeżeli isinstance(s, bytes_types):
        zwróć s
    spróbuj:
        zwróć memoryview(s).tobytes()
    wyjąwszy TypeError:
        podnieś TypeError("argument should be a bytes-like object albo ASCII "
                        "string, nie %r" % s.__class__.__name__) z Nic


# Base64 encoding/decoding uses binascii

def b64encode(s, altchars=Nic):
    """Encode a byte string using Base64.

    s jest the byte string to encode.  Optional altchars must be a byte
    string of length 2 which specifies an alternative alphabet dla the
    '+' oraz '/' characters.  This allows an application to
    e.g. generate url albo filesystem safe Base64 strings.

    The encoded byte string jest returned.
    """
    # Strip off the trailing newline
    encoded = binascii.b2a_base64(s)[:-1]
    jeżeli altchars jest nie Nic:
        assert len(altchars) == 2, repr(altchars)
        zwróć encoded.translate(bytes.maketrans(b'+/', altchars))
    zwróć encoded


def b64decode(s, altchars=Nic, validate=Nieprawda):
    """Decode a Base64 encoded byte string.

    s jest the byte string to decode.  Optional altchars must be a
    string of length 2 which specifies the alternative alphabet used
    instead of the '+' oraz '/' characters.

    The decoded string jest returned.  A binascii.Error jest podnieśd jeżeli s jest
    incorrectly padded.

    If validate jest Nieprawda (the default), non-base64-alphabet characters are
    discarded prior to the padding check.  If validate jest Prawda,
    non-base64-alphabet characters w the input result w a binascii.Error.
    """
    s = _bytes_from_decode_data(s)
    jeżeli altchars jest nie Nic:
        altchars = _bytes_from_decode_data(altchars)
        assert len(altchars) == 2, repr(altchars)
        s = s.translate(bytes.maketrans(altchars, b'+/'))
    jeżeli validate oraz nie re.match(b'^[A-Za-z0-9+/]*={0,2}$', s):
        podnieś binascii.Error('Non-base64 digit found')
    zwróć binascii.a2b_base64(s)


def standard_b64encode(s):
    """Encode a byte string using the standard Base64 alphabet.

    s jest the byte string to encode.  The encoded byte string jest returned.
    """
    zwróć b64encode(s)

def standard_b64decode(s):
    """Decode a byte string encoded przy the standard Base64 alphabet.

    s jest the byte string to decode.  The decoded byte string jest
    returned.  binascii.Error jest podnieśd jeżeli the input jest incorrectly
    padded albo jeżeli there are non-alphabet characters present w the
    input.
    """
    zwróć b64decode(s)


_urlsafe_encode_translation = bytes.maketrans(b'+/', b'-_')
_urlsafe_decode_translation = bytes.maketrans(b'-_', b'+/')

def urlsafe_b64encode(s):
    """Encode a byte string using a url-safe Base64 alphabet.

    s jest the byte string to encode.  The encoded byte string jest
    returned.  The alphabet uses '-' instead of '+' oraz '_' instead of
    '/'.
    """
    zwróć b64encode(s).translate(_urlsafe_encode_translation)

def urlsafe_b64decode(s):
    """Decode a byte string encoded przy the standard Base64 alphabet.

    s jest the byte string to decode.  The decoded byte string jest
    returned.  binascii.Error jest podnieśd jeżeli the input jest incorrectly
    padded albo jeżeli there are non-alphabet characters present w the
    input.

    The alphabet uses '-' instead of '+' oraz '_' instead of '/'.
    """
    s = _bytes_from_decode_data(s)
    s = s.translate(_urlsafe_decode_translation)
    zwróć b64decode(s)



# Base32 encoding/decoding must be done w Python
_b32alphabet = b'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
_b32tab2 = Nic
_b32rev = Nic

def b32encode(s):
    """Encode a byte string using Base32.

    s jest the byte string to encode.  The encoded byte string jest returned.
    """
    global _b32tab2
    # Delay the initialization of the table to nie waste memory
    # jeżeli the function jest never called
    jeżeli _b32tab2 jest Nic:
        b32tab = [bytes((i,)) dla i w _b32alphabet]
        _b32tab2 = [a + b dla a w b32tab dla b w b32tab]
        b32tab = Nic

    jeżeli nie isinstance(s, bytes_types):
        s = memoryview(s).tobytes()
    leftover = len(s) % 5
    # Pad the last quantum przy zero bits jeżeli necessary
    jeżeli leftover:
        s = s + bytes(5 - leftover)  # Don't use += !
    encoded = bytearray()
    from_bytes = int.from_bytes
    b32tab2 = _b32tab2
    dla i w range(0, len(s), 5):
        c = from_bytes(s[i: i + 5], 'big')
        encoded += (b32tab2[c >> 30] +           # bits 1 - 10
                    b32tab2[(c >> 20) & 0x3ff] + # bits 11 - 20
                    b32tab2[(c >> 10) & 0x3ff] + # bits 21 - 30
                    b32tab2[c & 0x3ff]           # bits 31 - 40
                   )
    # Adjust dla any leftover partial quanta
    jeżeli leftover == 1:
        encoded[-6:] = b'======'
    albo_inaczej leftover == 2:
        encoded[-4:] = b'===='
    albo_inaczej leftover == 3:
        encoded[-3:] = b'==='
    albo_inaczej leftover == 4:
        encoded[-1:] = b'='
    zwróć bytes(encoded)

def b32decode(s, casefold=Nieprawda, map01=Nic):
    """Decode a Base32 encoded byte string.

    s jest the byte string to decode.  Optional casefold jest a flag
    specifying whether a lowercase alphabet jest acceptable jako input.
    For security purposes, the default jest Nieprawda.

    RFC 3548 allows dla optional mapping of the digit 0 (zero) to the
    letter O (oh), oraz dla optional mapping of the digit 1 (one) to
    either the letter I (eye) albo letter L (el).  The optional argument
    map01 when nie Nic, specifies which letter the digit 1 should be
    mapped to (when map01 jest nie Nic, the digit 0 jest always mapped to
    the letter O).  For security purposes the default jest Nic, so that
    0 oraz 1 are nie allowed w the input.

    The decoded byte string jest returned.  binascii.Error jest podnieśd if
    the input jest incorrectly padded albo jeżeli there are non-alphabet
    characters present w the input.
    """
    global _b32rev
    # Delay the initialization of the table to nie waste memory
    # jeżeli the function jest never called
    jeżeli _b32rev jest Nic:
        _b32rev = {v: k dla k, v w enumerate(_b32alphabet)}
    s = _bytes_from_decode_data(s)
    jeżeli len(s) % 8:
        podnieś binascii.Error('Incorrect padding')
    # Handle section 2.4 zero oraz one mapping.  The flag map01 will be either
    # Nieprawda, albo the character to map the digit 1 (one) to.  It should be
    # either L (el) albo I (eye).
    jeżeli map01 jest nie Nic:
        map01 = _bytes_from_decode_data(map01)
        assert len(map01) == 1, repr(map01)
        s = s.translate(bytes.maketrans(b'01', b'O' + map01))
    jeżeli casefold:
        s = s.upper()
    # Strip off pad characters z the right.  We need to count the pad
    # characters because this will tell us how many null bytes to remove from
    # the end of the decoded string.
    l = len(s)
    s = s.rstrip(b'=')
    padchars = l - len(s)
    # Now decode the full quanta
    decoded = bytearray()
    b32rev = _b32rev
    dla i w range(0, len(s), 8):
        quanta = s[i: i + 8]
        acc = 0
        spróbuj:
            dla c w quanta:
                acc = (acc << 5) + b32rev[c]
        wyjąwszy KeyError:
            podnieś binascii.Error('Non-base32 digit found') z Nic
        decoded += acc.to_bytes(5, 'big')
    # Process the last, partial quanta
    jeżeli padchars:
        acc <<= 5 * padchars
        last = acc.to_bytes(5, 'big')
        jeżeli padchars == 1:
            decoded[-5:] = last[:-1]
        albo_inaczej padchars == 3:
            decoded[-5:] = last[:-2]
        albo_inaczej padchars == 4:
            decoded[-5:] = last[:-3]
        albo_inaczej padchars == 6:
            decoded[-5:] = last[:-4]
        inaczej:
            podnieś binascii.Error('Incorrect padding')
    zwróć bytes(decoded)



# RFC 3548, Base 16 Alphabet specifies uppercase, but hexlify() returns
# lowercase.  The RFC also recommends against accepting input case
# insensitively.
def b16encode(s):
    """Encode a byte string using Base16.

    s jest the byte string to encode.  The encoded byte string jest returned.
    """
    zwróć binascii.hexlify(s).upper()


def b16decode(s, casefold=Nieprawda):
    """Decode a Base16 encoded byte string.

    s jest the byte string to decode.  Optional casefold jest a flag
    specifying whether a lowercase alphabet jest acceptable jako input.
    For security purposes, the default jest Nieprawda.

    The decoded byte string jest returned.  binascii.Error jest podnieśd if
    s were incorrectly padded albo jeżeli there are non-alphabet characters
    present w the string.
    """
    s = _bytes_from_decode_data(s)
    jeżeli casefold:
        s = s.upper()
    jeżeli re.search(b'[^0-9A-F]', s):
        podnieś binascii.Error('Non-base16 digit found')
    zwróć binascii.unhexlify(s)

#
# Ascii85 encoding/decoding
#

_a85chars = Nic
_a85chars2 = Nic
_A85START = b"<~"
_A85END = b"~>"

def _85encode(b, chars, chars2, pad=Nieprawda, foldnuls=Nieprawda, foldspaces=Nieprawda):
    # Helper function dla a85encode oraz b85encode
    jeżeli nie isinstance(b, bytes_types):
        b = memoryview(b).tobytes()

    padding = (-len(b)) % 4
    jeżeli padding:
        b = b + b'\0' * padding
    words = struct.Struct('!%dI' % (len(b) // 4)).unpack(b)

    chunks = [b'z' jeżeli foldnuls oraz nie word inaczej
              b'y' jeżeli foldspaces oraz word == 0x20202020 inaczej
              (chars2[word // 614125] +
               chars2[word // 85 % 7225] +
               chars[word % 85])
              dla word w words]

    jeżeli padding oraz nie pad:
        jeżeli chunks[-1] == b'z':
            chunks[-1] = chars[0] * 5
        chunks[-1] = chunks[-1][:-padding]

    zwróć b''.join(chunks)

def a85encode(b, *, foldspaces=Nieprawda, wrapcol=0, pad=Nieprawda, adobe=Nieprawda):
    """Encode a byte string using Ascii85.

    b jest the byte string to encode. The encoded byte string jest returned.

    foldspaces jest an optional flag that uses the special short sequence 'y'
    instead of 4 consecutive spaces (ASCII 0x20) jako supported by 'btoa'. This
    feature jest nie supported by the "standard" Adobe encoding.

    wrapcol controls whether the output should have newline ('\\n') characters
    added to it. If this jest non-zero, each output line will be at most this
    many characters long.

    pad controls whether the input string jest padded to a multiple of 4 before
    encoding. Note that the btoa implementation always pads.

    adobe controls whether the encoded byte sequence jest framed przy <~ oraz ~>,
    which jest used by the Adobe implementation.
    """
    global _a85chars, _a85chars2
    # Delay the initialization of tables to nie waste memory
    # jeżeli the function jest never called
    jeżeli _a85chars jest Nic:
        _a85chars = [bytes((i,)) dla i w range(33, 118)]
        _a85chars2 = [(a + b) dla a w _a85chars dla b w _a85chars]

    result = _85encode(b, _a85chars, _a85chars2, pad, Prawda, foldspaces)

    jeżeli adobe:
        result = _A85START + result
    jeżeli wrapcol:
        wrapcol = max(2 jeżeli adobe inaczej 1, wrapcol)
        chunks = [result[i: i + wrapcol]
                  dla i w range(0, len(result), wrapcol)]
        jeżeli adobe:
            jeżeli len(chunks[-1]) + 2 > wrapcol:
                chunks.append(b'')
        result = b'\n'.join(chunks)
    jeżeli adobe:
        result += _A85END

    zwróć result

def a85decode(b, *, foldspaces=Nieprawda, adobe=Nieprawda, ignorechars=b' \t\n\r\v'):
    """Decode an Ascii85 encoded byte string.

    s jest the byte string to decode.

    foldspaces jest a flag that specifies whether the 'y' short sequence should be
    accepted jako shorthand dla 4 consecutive spaces (ASCII 0x20). This feature jest
    nie supported by the "standard" Adobe encoding.

    adobe controls whether the input sequence jest w Adobe Ascii85 format (i.e.
    jest framed przy <~ oraz ~>).

    ignorechars should be a byte string containing characters to ignore z the
    input. This should only contain whitespace characters, oraz by default
    contains all whitespace characters w ASCII.
    """
    b = _bytes_from_decode_data(b)
    jeżeli adobe:
        jeżeli nie (b.startswith(_A85START) oraz b.endswith(_A85END)):
            podnieś ValueError("Ascii85 encoded byte sequences must be bracketed "
                             "by {!r} oraz {!r}".format(_A85START, _A85END))
        b = b[2:-2] # Strip off start/end markers
    #
    # We have to go through this stepwise, so jako to ignore spaces oraz handle
    # special short sequences
    #
    packI = struct.Struct('!I').pack
    decoded = []
    decoded_append = decoded.append
    curr = []
    curr_append = curr.append
    curr_clear = curr.clear
    dla x w b + b'u' * 4:
        jeżeli b'!'[0] <= x <= b'u'[0]:
            curr_append(x)
            jeżeli len(curr) == 5:
                acc = 0
                dla x w curr:
                    acc = 85 * acc + (x - 33)
                spróbuj:
                    decoded_append(packI(acc))
                wyjąwszy struct.error:
                    podnieś ValueError('Ascii85 overflow') z Nic
                curr_clear()
        albo_inaczej x == b'z'[0]:
            jeżeli curr:
                podnieś ValueError('z inside Ascii85 5-tuple')
            decoded_append(b'\0\0\0\0')
        albo_inaczej foldspaces oraz x == b'y'[0]:
            jeżeli curr:
                podnieś ValueError('y inside Ascii85 5-tuple')
            decoded_append(b'\x20\x20\x20\x20')
        albo_inaczej x w ignorechars:
            # Skip whitespace
            kontynuuj
        inaczej:
            podnieś ValueError('Non-Ascii85 digit found: %c' % x)

    result = b''.join(decoded)
    padding = 4 - len(curr)
    jeżeli padding:
        # Throw away the extra padding
        result = result[:-padding]
    zwróć result

# The following code jest originally taken (przy permission) z Mercurial

_b85alphabet = (b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                b"abcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~")
_b85chars = Nic
_b85chars2 = Nic
_b85dec = Nic

def b85encode(b, pad=Nieprawda):
    """Encode an ASCII-encoded byte array w base85 format.

    If pad jest true, the input jest padded przy "\\0" so its length jest a multiple of
    4 characters before encoding.
    """
    global _b85chars, _b85chars2
    # Delay the initialization of tables to nie waste memory
    # jeżeli the function jest never called
    jeżeli _b85chars jest Nic:
        _b85chars = [bytes((i,)) dla i w _b85alphabet]
        _b85chars2 = [(a + b) dla a w _b85chars dla b w _b85chars]
    zwróć _85encode(b, _b85chars, _b85chars2, pad)

def b85decode(b):
    """Decode base85-encoded byte array"""
    global _b85dec
    # Delay the initialization of tables to nie waste memory
    # jeżeli the function jest never called
    jeżeli _b85dec jest Nic:
        _b85dec = [Nic] * 256
        dla i, c w enumerate(_b85alphabet):
            _b85dec[c] = i

    b = _bytes_from_decode_data(b)
    padding = (-len(b)) % 5
    b = b + b'~' * padding
    out = []
    packI = struct.Struct('!I').pack
    dla i w range(0, len(b), 5):
        chunk = b[i:i + 5]
        acc = 0
        spróbuj:
            dla c w chunk:
                acc = acc * 85 + _b85dec[c]
        wyjąwszy TypeError:
            dla j, c w enumerate(chunk):
                jeżeli _b85dec[c] jest Nic:
                    podnieś ValueError('bad base85 character at position %d'
                                    % (i + j)) z Nic
            podnieś
        spróbuj:
            out.append(packI(acc))
        wyjąwszy struct.error:
            podnieś ValueError('base85 overflow w hunk starting at byte %d'
                             % i) z Nic

    result = b''.join(out)
    jeżeli padding:
        result = result[:-padding]
    zwróć result

# Legacy interface.  This code could be cleaned up since I don't believe
# binascii has any line length limitations.  It just doesn't seem worth it
# though.  The files should be opened w binary mode.

MAXLINESIZE = 76 # Excluding the CRLF
MAXBINSIZE = (MAXLINESIZE//4)*3

def encode(input, output):
    """Encode a file; input oraz output are binary files."""
    dopóki Prawda:
        s = input.read(MAXBINSIZE)
        jeżeli nie s:
            przerwij
        dopóki len(s) < MAXBINSIZE:
            ns = input.read(MAXBINSIZE-len(s))
            jeżeli nie ns:
                przerwij
            s += ns
        line = binascii.b2a_base64(s)
        output.write(line)


def decode(input, output):
    """Decode a file; input oraz output are binary files."""
    dopóki Prawda:
        line = input.readline()
        jeżeli nie line:
            przerwij
        s = binascii.a2b_base64(line)
        output.write(s)

def _input_type_check(s):
    spróbuj:
        m = memoryview(s)
    wyjąwszy TypeError jako err:
        msg = "expected bytes-like object, nie %s" % s.__class__.__name__
        podnieś TypeError(msg) z err
    jeżeli m.format nie w ('c', 'b', 'B'):
        msg = ("expected single byte elements, nie %r z %s" %
                                          (m.format, s.__class__.__name__))
        podnieś TypeError(msg)
    jeżeli m.ndim != 1:
        msg = ("expected 1-D data, nie %d-D data z %s" %
                                          (m.ndim, s.__class__.__name__))
        podnieś TypeError(msg)


def encodebytes(s):
    """Encode a bytestring into a bytestring containing multiple lines
    of base-64 data."""
    _input_type_check(s)
    pieces = []
    dla i w range(0, len(s), MAXBINSIZE):
        chunk = s[i : i + MAXBINSIZE]
        pieces.append(binascii.b2a_base64(chunk))
    zwróć b"".join(pieces)

def encodestring(s):
    """Legacy alias of encodebytes()."""
    zaimportuj warnings
    warnings.warn("encodestring() jest a deprecated alias, use encodebytes()",
                  DeprecationWarning, 2)
    zwróć encodebytes(s)


def decodebytes(s):
    """Decode a bytestring of base-64 data into a bytestring."""
    _input_type_check(s)
    zwróć binascii.a2b_base64(s)

def decodestring(s):
    """Legacy alias of decodebytes()."""
    zaimportuj warnings
    warnings.warn("decodestring() jest a deprecated alias, use decodebytes()",
                  DeprecationWarning, 2)
    zwróć decodebytes(s)


# Usable jako a script...
def main():
    """Small main program"""
    zaimportuj sys, getopt
    spróbuj:
        opts, args = getopt.getopt(sys.argv[1:], 'deut')
    wyjąwszy getopt.error jako msg:
        sys.stdout = sys.stderr
        print(msg)
        print("""usage: %s [-d|-e|-u|-t] [file|-]
        -d, -u: decode
        -e: encode (default)
        -t: encode oraz decode string 'Aladdin:open sesame'"""%sys.argv[0])
        sys.exit(2)
    func = encode
    dla o, a w opts:
        jeżeli o == '-e': func = encode
        jeżeli o == '-d': func = decode
        jeżeli o == '-u': func = decode
        jeżeli o == '-t': test(); zwróć
    jeżeli args oraz args[0] != '-':
        przy open(args[0], 'rb') jako f:
            func(f, sys.stdout.buffer)
    inaczej:
        func(sys.stdin.buffer, sys.stdout.buffer)


def test():
    s0 = b"Aladdin:open sesame"
    print(repr(s0))
    s1 = encodebytes(s0)
    print(repr(s1))
    s2 = decodebytes(s1)
    print(repr(s2))
    assert s0 == s2


jeżeli __name__ == '__main__':
    main()
