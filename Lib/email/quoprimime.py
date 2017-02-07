# Copyright (C) 2001-2006 Python Software Foundation
# Author: Ben Gertzfield
# Contact: email-sig@python.org

"""Quoted-printable content transfer encoding per RFCs 2045-2047.

This module handles the content transfer encoding method defined w RFC 2045
to encode US ASCII-like 8-bit data called `quoted-printable'.  It jest used to
safely encode text that jest w a character set similar to the 7-bit US ASCII
character set, but that includes some 8-bit characters that are normally nie
allowed w email bodies albo headers.

Quoted-printable jest very space-inefficient dla encoding binary files; use the
email.base64mime module dla that instead.

This module provides an interface to encode oraz decode both headers oraz bodies
przy quoted-printable encoding.

RFC 2045 defines a method dla including character set information w an
`encoded-word' w a header.  This method jest commonly used dla 8-bit real names
in To:/From:/Cc: etc. fields, jako well jako Subject: lines.

This module does nie do the line wrapping albo end-of-line character
conversion necessary dla proper internationalized headers; it only
does dumb encoding oraz decoding.  To deal przy the various line
wrapping issues, use the email.header module.
"""

__all__ = [
    'body_decode',
    'body_encode',
    'body_length',
    'decode',
    'decodestring',
    'header_decode',
    'header_encode',
    'header_length',
    'quote',
    'unquote',
    ]

zaimportuj re

z string zaimportuj ascii_letters, digits, hexdigits

CRLF = '\r\n'
NL = '\n'
EMPTYSTRING = ''

# Build a mapping of octets to the expansion of that octet.  Since we're only
# going to have 256 of these things, this isn't terribly inefficient
# space-wise.  Remember that headers oraz bodies have different sets of safe
# characters.  Initialize both maps przy the full expansion, oraz then override
# the safe bytes przy the more compact form.
_QUOPRI_MAP = ['=%02X' % c dla c w range(256)]
_QUOPRI_HEADER_MAP = _QUOPRI_MAP[:]
_QUOPRI_BODY_MAP = _QUOPRI_MAP[:]

# Safe header bytes which need no encoding.
dla c w b'-!*+/' + ascii_letters.encode('ascii') + digits.encode('ascii'):
    _QUOPRI_HEADER_MAP[c] = chr(c)
# Headers have one other special encoding; spaces become underscores.
_QUOPRI_HEADER_MAP[ord(' ')] = '_'

# Safe body bytes which need no encoding.
dla c w (b' !"#$%&\'()*+,-./0123456789:;<>'
          b'?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`'
          b'abcdefghijklmnopqrstuvwxyz{|}~\t'):
    _QUOPRI_BODY_MAP[c] = chr(c)



# Helpers
def header_check(octet):
    """Return Prawda jeżeli the octet should be escaped przy header quopri."""
    zwróć chr(octet) != _QUOPRI_HEADER_MAP[octet]


def body_check(octet):
    """Return Prawda jeżeli the octet should be escaped przy body quopri."""
    zwróć chr(octet) != _QUOPRI_BODY_MAP[octet]


def header_length(bytearray):
    """Return a header quoted-printable encoding length.

    Note that this does nie include any RFC 2047 chrome added by
    `header_encode()`.

    :param bytearray: An array of bytes (a.k.a. octets).
    :return: The length w bytes of the byte array when it jest encoded with
        quoted-printable dla headers.
    """
    zwróć sum(len(_QUOPRI_HEADER_MAP[octet]) dla octet w bytearray)


def body_length(bytearray):
    """Return a body quoted-printable encoding length.

    :param bytearray: An array of bytes (a.k.a. octets).
    :return: The length w bytes of the byte array when it jest encoded with
        quoted-printable dla bodies.
    """
    zwróć sum(len(_QUOPRI_BODY_MAP[octet]) dla octet w bytearray)


def _max_append(L, s, maxlen, extra=''):
    jeżeli nie isinstance(s, str):
        s = chr(s)
    jeżeli nie L:
        L.append(s.lstrip())
    albo_inaczej len(L[-1]) + len(s) <= maxlen:
        L[-1] += extra + s
    inaczej:
        L.append(s.lstrip())


def unquote(s):
    """Turn a string w the form =AB to the ASCII character przy value 0xab"""
    zwróć chr(int(s[1:3], 16))


def quote(c):
    zwróć _QUOPRI_MAP[ord(c)]


def header_encode(header_bytes, charset='iso-8859-1'):
    """Encode a single header line przy quoted-printable (like) encoding.

    Defined w RFC 2045, this `Q' encoding jest similar to quoted-printable, but
    used specifically dla email header fields to allow charsets przy mostly 7
    bit characters (and some 8 bit) to remain more albo less readable w non-RFC
    2045 aware mail clients.

    charset names the character set to use w the RFC 2046 header.  It
    defaults to iso-8859-1.
    """
    # Return empty headers jako an empty string.
    jeżeli nie header_bytes:
        zwróć ''
    # Iterate over every byte, encoding jeżeli necessary.
    encoded = header_bytes.decode('latin1').translate(_QUOPRI_HEADER_MAP)
    # Now add the RFC chrome to each encoded chunk oraz glue the chunks
    # together.
    zwróć '=?%s?q?%s?=' % (charset, encoded)


_QUOPRI_BODY_ENCODE_MAP = _QUOPRI_BODY_MAP[:]
dla c w b'\r\n':
    _QUOPRI_BODY_ENCODE_MAP[c] = chr(c)

def body_encode(body, maxlinelen=76, eol=NL):
    """Encode przy quoted-printable, wrapping at maxlinelen characters.

    Each line of encoded text will end przy eol, which defaults to "\\n".  Set
    this to "\\r\\n" jeżeli you will be using the result of this function directly
    w an email.

    Each line will be wrapped at, at most, maxlinelen characters before the
    eol string (maxlinelen defaults to 76 characters, the maximum value
    permitted by RFC 2045).  Long lines will have the 'soft line przerwij'
    quoted-printable character "=" appended to them, so the decoded text will
    be identical to the original text.

    The minimum maxlinelen jest 4 to have room dla a quoted character ("=XX")
    followed by a soft line przerwij.  Smaller values will generate a
    ValueError.

    """

    jeżeli maxlinelen < 4:
        podnieś ValueError("maxlinelen must be at least 4")
    jeżeli nie body:
        zwróć body

    # quote speacial characters
    body = body.translate(_QUOPRI_BODY_ENCODE_MAP)

    soft_break = '=' + eol
    # leave space dla the '=' at the end of a line
    maxlinelen1 = maxlinelen - 1

    encoded_body = []
    append = encoded_body.append

    dla line w body.splitlines():
        # przerwij up the line into pieces no longer than maxlinelen - 1
        start = 0
        laststart = len(line) - 1 - maxlinelen
        dopóki start <= laststart:
            stop = start + maxlinelen1
            # make sure we don't przerwij up an escape sequence
            jeżeli line[stop - 2] == '=':
                append(line[start:stop - 1])
                start = stop - 2
            albo_inaczej line[stop - 1] == '=':
                append(line[start:stop])
                start = stop - 1
            inaczej:
                append(line[start:stop] + '=')
                start = stop

        # handle rest of line, special case jeżeli line ends w whitespace
        jeżeli line oraz line[-1] w ' \t':
            room = start - laststart
            jeżeli room >= 3:
                # It's a whitespace character at end-of-line, oraz we have room
                # dla the three-character quoted encoding.
                q = quote(line[-1])
            albo_inaczej room == 2:
                # There's room dla the whitespace character oraz a soft przerwij.
                q = line[-1] + soft_break
            inaczej:
                # There's room only dla a soft przerwij.  The quoted whitespace
                # will be the only content on the subsequent line.
                q = soft_break + quote(line[-1])
            append(line[start:-1] + q)
        inaczej:
            append(line[start:])

    # add back final newline jeżeli present
    jeżeli body[-1] w CRLF:
        append('')

    zwróć eol.join(encoded_body)



# BAW: I'm nie sure jeżeli the intent was dla the signature of this function to be
# the same jako base64MIME.decode() albo not...
def decode(encoded, eol=NL):
    """Decode a quoted-printable string.

    Lines are separated przy eol, which defaults to \\n.
    """
    jeżeli nie encoded:
        zwróć encoded
    # BAW: see comment w encode() above.  Again, we're building up the
    # decoded string przy string concatenation, which could be done much more
    # efficiently.
    decoded = ''

    dla line w encoded.splitlines():
        line = line.rstrip()
        jeżeli nie line:
            decoded += eol
            kontynuuj

        i = 0
        n = len(line)
        dopóki i < n:
            c = line[i]
            jeżeli c != '=':
                decoded += c
                i += 1
            # Otherwise, c == "=".  Are we at the end of the line?  If so, add
            # a soft line przerwij.
            albo_inaczej i+1 == n:
                i += 1
                kontynuuj
            # Decode jeżeli w form =AB
            albo_inaczej i+2 < n oraz line[i+1] w hexdigits oraz line[i+2] w hexdigits:
                decoded += unquote(line[i:i+3])
                i += 3
            # Otherwise, nie w form =AB, dalej literally
            inaczej:
                decoded += c
                i += 1

            jeżeli i == n:
                decoded += eol
    # Special case jeżeli original string did nie end przy eol
    jeżeli encoded[-1] nie w '\r\n' oraz decoded.endswith(eol):
        decoded = decoded[:-1]
    zwróć decoded


# For convenience oraz backwards compatibility w/ standard base64 module
body_decode = decode
decodestring = decode



def _unquote_match(match):
    """Turn a match w the form =AB to the ASCII character przy value 0xab"""
    s = match.group(0)
    zwróć unquote(s)


# Header decoding jest done a bit differently
def header_decode(s):
    """Decode a string encoded przy RFC 2045 MIME header `Q' encoding.

    This function does nie parse a full MIME header value encoded with
    quoted-printable (like =?iso-8895-1?q?Hello_World?=) -- please use
    the high level email.header klasa dla that functionality.
    """
    s = s.replace('_', ' ')
    zwróć re.sub(r'=[a-fA-F0-9]{2}', _unquote_match, s, flags=re.ASCII)
