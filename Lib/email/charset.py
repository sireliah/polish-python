# Copyright (C) 2001-2007 Python Software Foundation
# Author: Ben Gertzfield, Barry Warsaw
# Contact: email-sig@python.org

__all__ = [
    'Charset',
    'add_alias',
    'add_charset',
    'add_codec',
    ]

z functools zaimportuj partial

zaimportuj email.base64mime
zaimportuj email.quoprimime

z email zaimportuj errors
z email.encoders zaimportuj encode_7or8bit



# Flags dla types of header encodings
QP          = 1 # Quoted-Printable
BASE64      = 2 # Base64
SHORTEST    = 3 # the shorter of QP oraz base64, but only dla headers

# In "=?charset?q?hello_world?=", the =?, ?q?, oraz ?= add up to 7
RFC2047_CHROME_LEN = 7

DEFAULT_CHARSET = 'us-ascii'
UNKNOWN8BIT = 'unknown-8bit'
EMPTYSTRING = ''



# Defaults
CHARSETS = {
    # input        header enc  body enc output conv
    'iso-8859-1':  (QP,        QP,      Nic),
    'iso-8859-2':  (QP,        QP,      Nic),
    'iso-8859-3':  (QP,        QP,      Nic),
    'iso-8859-4':  (QP,        QP,      Nic),
    # iso-8859-5 jest Cyrillic, oraz nie especially used
    # iso-8859-6 jest Arabic, also nie particularly used
    # iso-8859-7 jest Greek, QP will nie make it readable
    # iso-8859-8 jest Hebrew, QP will nie make it readable
    'iso-8859-9':  (QP,        QP,      Nic),
    'iso-8859-10': (QP,        QP,      Nic),
    # iso-8859-11 jest Thai, QP will nie make it readable
    'iso-8859-13': (QP,        QP,      Nic),
    'iso-8859-14': (QP,        QP,      Nic),
    'iso-8859-15': (QP,        QP,      Nic),
    'iso-8859-16': (QP,        QP,      Nic),
    'windows-1252':(QP,        QP,      Nic),
    'viscii':      (QP,        QP,      Nic),
    'us-ascii':    (Nic,      Nic,    Nic),
    'big5':        (BASE64,    BASE64,  Nic),
    'gb2312':      (BASE64,    BASE64,  Nic),
    'euc-jp':      (BASE64,    Nic,    'iso-2022-jp'),
    'shift_jis':   (BASE64,    Nic,    'iso-2022-jp'),
    'iso-2022-jp': (BASE64,    Nic,    Nic),
    'koi8-r':      (BASE64,    BASE64,  Nic),
    'utf-8':       (SHORTEST,  BASE64, 'utf-8'),
    }

# Aliases dla other commonly-used names dla character sets.  Map
# them to the real ones used w email.
ALIASES = {
    'latin_1': 'iso-8859-1',
    'latin-1': 'iso-8859-1',
    'latin_2': 'iso-8859-2',
    'latin-2': 'iso-8859-2',
    'latin_3': 'iso-8859-3',
    'latin-3': 'iso-8859-3',
    'latin_4': 'iso-8859-4',
    'latin-4': 'iso-8859-4',
    'latin_5': 'iso-8859-9',
    'latin-5': 'iso-8859-9',
    'latin_6': 'iso-8859-10',
    'latin-6': 'iso-8859-10',
    'latin_7': 'iso-8859-13',
    'latin-7': 'iso-8859-13',
    'latin_8': 'iso-8859-14',
    'latin-8': 'iso-8859-14',
    'latin_9': 'iso-8859-15',
    'latin-9': 'iso-8859-15',
    'latin_10':'iso-8859-16',
    'latin-10':'iso-8859-16',
    'cp949':   'ks_c_5601-1987',
    'euc_jp':  'euc-jp',
    'euc_kr':  'euc-kr',
    'ascii':   'us-ascii',
    }


# Map charsets to their Unicode codec strings.
CODEC_MAP = {
    'gb2312':      'eucgb2312_cn',
    'big5':        'big5_tw',
    # Hack: We don't want *any* conversion dla stuff marked us-ascii, jako all
    # sorts of garbage might be sent to us w the guise of 7-bit us-ascii.
    # Let that stuff dalej through without conversion to/z Unicode.
    'us-ascii':    Nic,
    }



# Convenience functions dla extending the above mappings
def add_charset(charset, header_enc=Nic, body_enc=Nic, output_charset=Nic):
    """Add character set properties to the global registry.

    charset jest the input character set, oraz must be the canonical name of a
    character set.

    Optional header_enc oraz body_enc jest either Charset.QP for
    quoted-printable, Charset.BASE64 dla base64 encoding, Charset.SHORTEST for
    the shortest of qp albo base64 encoding, albo Nic dla no encoding.  SHORTEST
    jest only valid dla header_enc.  It describes how message headers oraz
    message bodies w the input charset are to be encoded.  Default jest no
    encoding.

    Optional output_charset jest the character set that the output should be
    in.  Conversions will proceed z input charset, to Unicode, to the
    output charset when the method Charset.convert() jest called.  The default
    jest to output w the same character set jako the input.

    Both input_charset oraz output_charset must have Unicode codec entries w
    the module's charset-to-codec mapping; use add_codec(charset, codecname)
    to add codecs the module does nie know about.  See the codecs module's
    documentation dla more information.
    """
    jeżeli body_enc == SHORTEST:
        podnieś ValueError('SHORTEST nie allowed dla body_enc')
    CHARSETS[charset] = (header_enc, body_enc, output_charset)


def add_alias(alias, canonical):
    """Add a character set alias.

    alias jest the alias name, e.g. latin-1
    canonical jest the character set's canonical name, e.g. iso-8859-1
    """
    ALIASES[alias] = canonical


def add_codec(charset, codecname):
    """Add a codec that map characters w the given charset to/z Unicode.

    charset jest the canonical name of a character set.  codecname jest the name
    of a Python codec, jako appropriate dla the second argument to the unicode()
    built-in, albo to the encode() method of a Unicode string.
    """
    CODEC_MAP[charset] = codecname



# Convenience function dla encoding strings, taking into account
# that they might be unknown-8bit (ie: have surrogate-escaped bytes)
def _encode(string, codec):
    jeżeli codec == UNKNOWN8BIT:
        zwróć string.encode('ascii', 'surrogateescape')
    inaczej:
        zwróć string.encode(codec)



klasa Charset:
    """Map character sets to their email properties.

    This klasa provides information about the requirements imposed on email
    dla a specific character set.  It also provides convenience routines for
    converting between character sets, given the availability of the
    applicable codecs.  Given a character set, it will do its best to provide
    information on how to use that character set w an email w an
    RFC-compliant way.

    Certain character sets must be encoded przy quoted-printable albo base64
    when used w email headers albo bodies.  Certain character sets must be
    converted outright, oraz are nie allowed w email.  Instances of this
    module expose the following information about a character set:

    input_charset: The initial character set specified.  Common aliases
                   are converted to their `official' email names (e.g. latin_1
                   jest converted to iso-8859-1).  Defaults to 7-bit us-ascii.

    header_encoding: If the character set must be encoded before it can be
                     used w an email header, this attribute will be set to
                     Charset.QP (dla quoted-printable), Charset.BASE64 (for
                     base64 encoding), albo Charset.SHORTEST dla the shortest of
                     QP albo BASE64 encoding.  Otherwise, it will be Nic.

    body_encoding: Same jako header_encoding, but describes the encoding dla the
                   mail message's body, which indeed may be different than the
                   header encoding.  Charset.SHORTEST jest nie allowed for
                   body_encoding.

    output_charset: Some character sets must be converted before they can be
                    used w email headers albo bodies.  If the input_charset jest
                    one of them, this attribute will contain the name of the
                    charset output will be converted to.  Otherwise, it will
                    be Nic.

    input_codec: The name of the Python codec used to convert the
                 input_charset to Unicode.  If no conversion codec jest
                 necessary, this attribute will be Nic.

    output_codec: The name of the Python codec used to convert Unicode
                  to the output_charset.  If no conversion codec jest necessary,
                  this attribute will have the same value jako the input_codec.
    """
    def __init__(self, input_charset=DEFAULT_CHARSET):
        # RFC 2046, $4.1.2 says charsets are nie case sensitive.  We coerce to
        # unicode because its .lower() jest locale insensitive.  If the argument
        # jest already a unicode, we leave it at that, but ensure that the
        # charset jest ASCII, jako the standard (RFC XXX) requires.
        spróbuj:
            jeżeli isinstance(input_charset, str):
                input_charset.encode('ascii')
            inaczej:
                input_charset = str(input_charset, 'ascii')
        wyjąwszy UnicodeError:
            podnieś errors.CharsetError(input_charset)
        input_charset = input_charset.lower()
        # Set the input charset after filtering through the aliases
        self.input_charset = ALIASES.get(input_charset, input_charset)
        # We can try to guess which encoding oraz conversion to use by the
        # charset_map dictionary.  Try that first, but let the user override
        # it.
        henc, benc, conv = CHARSETS.get(self.input_charset,
                                        (SHORTEST, BASE64, Nic))
        jeżeli nie conv:
            conv = self.input_charset
        # Set the attributes, allowing the arguments to override the default.
        self.header_encoding = henc
        self.body_encoding = benc
        self.output_charset = ALIASES.get(conv, conv)
        # Now set the codecs.  If one isn't defined dla input_charset,
        # guess oraz try a Unicode codec przy the same name jako input_codec.
        self.input_codec = CODEC_MAP.get(self.input_charset,
                                         self.input_charset)
        self.output_codec = CODEC_MAP.get(self.output_charset,
                                          self.output_charset)

    def __str__(self):
        zwróć self.input_charset.lower()

    __repr__ = __str__

    def __eq__(self, other):
        zwróć str(self) == str(other).lower()

    def get_body_encoding(self):
        """Return the content-transfer-encoding used dla body encoding.

        This jest either the string `quoted-printable' albo `base64' depending on
        the encoding used, albo it jest a function w which case you should call
        the function przy a single argument, the Message object being
        encoded.  The function should then set the Content-Transfer-Encoding
        header itself to whatever jest appropriate.

        Returns "quoted-printable" jeżeli self.body_encoding jest QP.
        Returns "base64" jeżeli self.body_encoding jest BASE64.
        Returns conversion function otherwise.
        """
        assert self.body_encoding != SHORTEST
        jeżeli self.body_encoding == QP:
            zwróć 'quoted-printable'
        albo_inaczej self.body_encoding == BASE64:
            zwróć 'base64'
        inaczej:
            zwróć encode_7or8bit

    def get_output_charset(self):
        """Return the output character set.

        This jest self.output_charset jeżeli that jest nie Nic, otherwise it jest
        self.input_charset.
        """
        zwróć self.output_charset albo self.input_charset

    def header_encode(self, string):
        """Header-encode a string by converting it first to bytes.

        The type of encoding (base64 albo quoted-printable) will be based on
        this charset's `header_encoding`.

        :param string: A unicode string dla the header.  It must be possible
            to encode this string to bytes using the character set's
            output codec.
        :return: The encoded string, przy RFC 2047 chrome.
        """
        codec = self.output_codec albo 'us-ascii'
        header_bytes = _encode(string, codec)
        # 7bit/8bit encodings zwróć the string unchanged (modulo conversions)
        encoder_module = self._get_encoder(header_bytes)
        jeżeli encoder_module jest Nic:
            zwróć string
        zwróć encoder_module.header_encode(header_bytes, codec)

    def header_encode_lines(self, string, maxlengths):
        """Header-encode a string by converting it first to bytes.

        This jest similar to `header_encode()` wyjąwszy that the string jest fit
        into maximum line lengths jako given by the argument.

        :param string: A unicode string dla the header.  It must be possible
            to encode this string to bytes using the character set's
            output codec.
        :param maxlengths: Maximum line length iterator.  Each element
            returned z this iterator will provide the next maximum line
            length.  This parameter jest used jako an argument to built-in next()
            oraz should never be exhausted.  The maximum line lengths should
            nie count the RFC 2047 chrome.  These line lengths are only a
            hint; the splitter does the best it can.
        :return: Lines of encoded strings, each przy RFC 2047 chrome.
        """
        # See which encoding we should use.
        codec = self.output_codec albo 'us-ascii'
        header_bytes = _encode(string, codec)
        encoder_module = self._get_encoder(header_bytes)
        encoder = partial(encoder_module.header_encode, charset=codec)
        # Calculate the number of characters that the RFC 2047 chrome will
        # contribute to each line.
        charset = self.get_output_charset()
        extra = len(charset) + RFC2047_CHROME_LEN
        # Now comes the hard part.  We must encode bytes but we can't split on
        # bytes because some character sets are variable length oraz each
        # encoded word must stand on its own.  So the problem jest you have to
        # encode to bytes to figure out this word's length, but you must split
        # on characters.  This causes two problems: first, we don't know how
        # many octets a specific substring of unicode characters will get
        # encoded to, oraz second, we don't know how many ASCII characters
        # those octets will get encoded to.  Unless we try it.  Which seems
        # inefficient.  In the interest of being correct rather than fast (and
        # w the hope that there will be few encoded headers w any such
        # message), brute force it. :(
        lines = []
        current_line = []
        maxlen = next(maxlengths) - extra
        dla character w string:
            current_line.append(character)
            this_line = EMPTYSTRING.join(current_line)
            length = encoder_module.header_length(_encode(this_line, charset))
            jeżeli length > maxlen:
                # This last character doesn't fit so pop it off.
                current_line.pop()
                # Does nothing fit on the first line?
                jeżeli nie lines oraz nie current_line:
                    lines.append(Nic)
                inaczej:
                    separator = (' ' jeżeli lines inaczej '')
                    joined_line = EMPTYSTRING.join(current_line)
                    header_bytes = _encode(joined_line, codec)
                    lines.append(encoder(header_bytes))
                current_line = [character]
                maxlen = next(maxlengths) - extra
        joined_line = EMPTYSTRING.join(current_line)
        header_bytes = _encode(joined_line, codec)
        lines.append(encoder(header_bytes))
        zwróć lines

    def _get_encoder(self, header_bytes):
        jeżeli self.header_encoding == BASE64:
            zwróć email.base64mime
        albo_inaczej self.header_encoding == QP:
            zwróć email.quoprimime
        albo_inaczej self.header_encoding == SHORTEST:
            len64 = email.base64mime.header_length(header_bytes)
            lenqp = email.quoprimime.header_length(header_bytes)
            jeżeli len64 < lenqp:
                zwróć email.base64mime
            inaczej:
                zwróć email.quoprimime
        inaczej:
            zwróć Nic

    def body_encode(self, string):
        """Body-encode a string by converting it first to bytes.

        The type of encoding (base64 albo quoted-printable) will be based on
        self.body_encoding.  If body_encoding jest Nic, we assume the
        output charset jest a 7bit encoding, so re-encoding the decoded
        string using the ascii codec produces the correct string version
        of the content.
        """
        jeżeli nie string:
            zwróć string
        jeżeli self.body_encoding jest BASE64:
            jeżeli isinstance(string, str):
                string = string.encode(self.output_charset)
            zwróć email.base64mime.body_encode(string)
        albo_inaczej self.body_encoding jest QP:
            # quopromime.body_encode takes a string, but operates on it jako if
            # it were a list of byte codes.  For a (minimal) history on why
            # this jest so, see changeset 0cf700464177.  To correctly encode a
            # character set, then, we must turn it into pseudo bytes via the
            # latin1 charset, which will encode any byte jako a single code point
            # between 0 oraz 255, which jest what body_encode jest expecting.
            jeżeli isinstance(string, str):
                string = string.encode(self.output_charset)
            string = string.decode('latin1')
            zwróć email.quoprimime.body_encode(string)
        inaczej:
            jeżeli isinstance(string, str):
                string = string.encode(self.output_charset).decode('ascii')
            zwróć string
