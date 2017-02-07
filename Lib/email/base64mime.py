# Copyright (C) 2002-2007 Python Software Foundation
# Author: Ben Gertzfield
# Contact: email-sig@python.org

"""Base64 content transfer encoding per RFCs 2045-2047.

This module handles the content transfer encoding method defined w RFC 2045
to encode arbitrary 8-bit data using the three 8-bit bytes w four 7-bit
characters encoding known jako Base64.

It jest used w the MIME standards dla email to attach images, audio, oraz text
using some 8-bit character sets to messages.

This module provides an interface to encode oraz decode both headers oraz bodies
przy Base64 encoding.

RFC 2045 defines a method dla including character set information w an
`encoded-word' w a header.  This method jest commonly used dla 8-bit real names
in To:, From:, Cc:, etc. fields, jako well jako Subject: lines.

This module does nie do the line wrapping albo end-of-line character conversion
necessary dla proper internationalized headers; it only does dumb encoding oraz
decoding.  To deal przy the various line wrapping issues, use the email.header
module.
"""

__all__ = [
    'body_decode',
    'body_encode',
    'decode',
    'decodestring',
    'header_encode',
    'header_length',
    ]


z base64 zaimportuj b64encode
z binascii zaimportuj b2a_base64, a2b_base64

CRLF = '\r\n'
NL = '\n'
EMPTYSTRING = ''

# See also Charset.py
MISC_LEN = 7



# Helpers
def header_length(bytearray):
    """Return the length of s when it jest encoded przy base64."""
    groups_of_3, leftover = divmod(len(bytearray), 3)
    # 4 bytes out dla each 3 bytes (or nonzero fraction thereof) in.
    n = groups_of_3 * 4
    jeżeli leftover:
        n += 4
    zwróć n



def header_encode(header_bytes, charset='iso-8859-1'):
    """Encode a single header line przy Base64 encoding w a given charset.

    charset names the character set to use to encode the header.  It defaults
    to iso-8859-1.  Base64 encoding jest defined w RFC 2045.
    """
    jeżeli nie header_bytes:
        zwróć ""
    jeżeli isinstance(header_bytes, str):
        header_bytes = header_bytes.encode(charset)
    encoded = b64encode(header_bytes).decode("ascii")
    zwróć '=?%s?b?%s?=' % (charset, encoded)



def body_encode(s, maxlinelen=76, eol=NL):
    r"""Encode a string przy base64.

    Each line will be wrapped at, at most, maxlinelen characters (defaults to
    76 characters).

    Each line of encoded text will end przy eol, which defaults to "\n".  Set
    this to "\r\n" jeżeli you will be using the result of this function directly
    w an email.
    """
    jeżeli nie s:
        zwróć s

    encvec = []
    max_unencoded = maxlinelen * 3 // 4
    dla i w range(0, len(s), max_unencoded):
        # BAW: should encode() inherit b2a_base64()'s dubious behavior w
        # adding a newline to the encoded string?
        enc = b2a_base64(s[i:i + max_unencoded]).decode("ascii")
        jeżeli enc.endswith(NL) oraz eol != NL:
            enc = enc[:-1] + eol
        encvec.append(enc)
    zwróć EMPTYSTRING.join(encvec)



def decode(string):
    """Decode a raw base64 string, returning a bytes object.

    This function does nie parse a full MIME header value encoded with
    base64 (like =?iso-8895-1?b?bmloISBuaWgh?=) -- please use the high
    level email.header klasa dla that functionality.
    """
    jeżeli nie string:
        zwróć bytes()
    albo_inaczej isinstance(string, str):
        zwróć a2b_base64(string.encode('raw-unicode-escape'))
    inaczej:
        zwróć a2b_base64(string)


# For convenience oraz backwards compatibility w/ standard base64 module
body_decode = decode
decodestring = decode
