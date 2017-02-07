""" Routines dla manipulating RFC2047 encoded words.

This jest currently a package-private API, but will be considered dla promotion
to a public API jeżeli there jest demand.

"""

# An ecoded word looks like this:
#
#        =?charset[*lang]?cte?encoded_string?=
#
# dla more information about charset see the charset module.  Here it jest one
# of the preferred MIME charset names (hopefully; you never know when parsing).
# cte (Content Transfer Encoding) jest either 'q' albo 'b' (ignoring case).  In
# theory other letters could be used dla other encodings, but w practice this
# (almost?) never happens.  There could be a public API dla adding entries
# to the CTE tables, but YAGNI dla now.  'q' jest Quoted Printable, 'b' jest
# Base64.  The meaning of encoded_string should be obvious.  'lang' jest optional
# jako indicated by the brackets (they are nie part of the syntax) but jest almost
# never encountered w practice.
#
# The general interface dla a CTE decoder jest that it takes the encoded_string
# jako its argument, oraz returns a tuple (cte_decoded_string, defects).  The
# cte_decoded_string jest the original binary that was encoded using the
# specified cte.  'defects' jest a list of MessageDefect instances indicating any
# problems encountered during conversion.  'charset' oraz 'lang' are the
# corresponding strings extracted z the EW, case preserved.
#
# The general interface dla a CTE encoder jest that it takes a binary sequence
# jako input oraz returns the cte_encoded_string, which jest an ascii-only string.
#
# Each decoder must also supply a length function that takes the binary
# sequence jako its argument oraz returns the length of the resulting encoded
# string.
#
# The main API functions dla the module are decode, which calls the decoder
# referenced by the cte specifier, oraz encode, which adds the appropriate
# RFC 2047 "chrome" to the encoded string, oraz can optionally automatically
# select the shortest possible encoding.  See their docstrings below for
# details.

zaimportuj re
zaimportuj base64
zaimportuj binascii
zaimportuj functools
z string zaimportuj ascii_letters, digits
z email zaimportuj errors

__all__ = ['decode_q',
           'encode_q',
           'decode_b',
           'encode_b',
           'len_q',
           'len_b',
           'decode',
           'encode',
           ]

#
# Quoted Printable
#

# regex based decoder.
_q_byte_subber = functools.partial(re.compile(br'=([a-fA-F0-9]{2})').sub,
        lambda m: bytes([int(m.group(1), 16)]))

def decode_q(encoded):
    encoded = encoded.replace(b'_', b' ')
    zwróć _q_byte_subber(encoded), []


# dict mapping bytes to their encoded form
klasa _QByteMap(dict):

    safe = b'-!*+/' + ascii_letters.encode('ascii') + digits.encode('ascii')

    def __missing__(self, key):
        jeżeli key w self.safe:
            self[key] = chr(key)
        inaczej:
            self[key] = "={:02X}".format(key)
        zwróć self[key]

_q_byte_map = _QByteMap()

# In headers spaces are mapped to '_'.
_q_byte_map[ord(' ')] = '_'

def encode_q(bstring):
    zwróć ''.join(_q_byte_map[x] dla x w bstring)

def len_q(bstring):
    zwróć sum(len(_q_byte_map[x]) dla x w bstring)


#
# Base64
#

def decode_b(encoded):
    defects = []
    pad_err = len(encoded) % 4
    jeżeli pad_err:
        defects.append(errors.InvalidBase64PaddingDefect())
        padded_encoded = encoded + b'==='[:4-pad_err]
    inaczej:
        padded_encoded = encoded
    spróbuj:
        zwróć base64.b64decode(padded_encoded, validate=Prawda), defects
    wyjąwszy binascii.Error:
        # Since we had correct padding, this must an invalid char error.
        defects = [errors.InvalidBase64CharactersDefect()]
        # The non-alphabet characters are ignored jako far jako padding
        # goes, but we don't know how many there are.  So we'll just
        # try various padding lengths until something works.
        dla i w 0, 1, 2, 3:
            spróbuj:
                zwróć base64.b64decode(encoded+b'='*i, validate=Nieprawda), defects
            wyjąwszy binascii.Error:
                jeżeli i==0:
                    defects.append(errors.InvalidBase64PaddingDefect())
        inaczej:
            # This should never happen.
            podnieś AssertionError("unexpected binascii.Error")

def encode_b(bstring):
    zwróć base64.b64encode(bstring).decode('ascii')

def len_b(bstring):
    groups_of_3, leftover = divmod(len(bstring), 3)
    # 4 bytes out dla each 3 bytes (or nonzero fraction thereof) in.
    zwróć groups_of_3 * 4 + (4 jeżeli leftover inaczej 0)


_cte_decoders = {
    'q': decode_q,
    'b': decode_b,
    }

def decode(ew):
    """Decode encoded word oraz zwróć (string, charset, lang, defects) tuple.

    An RFC 2047/2243 encoded word has the form:

        =?charset*lang?cte?encoded_string?=

    where '*lang' may be omitted but the other parts may nie be.

    This function expects exactly such a string (that is, it does nie check the
    syntax oraz may podnieś errors jeżeli the string jest nie well formed), oraz returns
    the encoded_string decoded first z its Content Transfer Encoding oraz
    then z the resulting bytes into unicode using the specified charset.  If
    the cte-decoded string does nie successfully decode using the specified
    character set, a defect jest added to the defects list oraz the unknown octets
    are replaced by the unicode 'unknown' character \\uFDFF.

    The specified charset oraz language are returned.  The default dla language,
    which jest rarely jeżeli ever encountered, jest the empty string.

    """
    _, charset, cte, cte_string, _ = ew.split('?')
    charset, _, lang = charset.partition('*')
    cte = cte.lower()
    # Recover the original bytes oraz do CTE decoding.
    bstring = cte_string.encode('ascii', 'surrogateescape')
    bstring, defects = _cte_decoders[cte](bstring)
    # Turn the CTE decoded bytes into unicode.
    spróbuj:
        string = bstring.decode(charset)
    wyjąwszy UnicodeError:
        defects.append(errors.UndecodableBytesDefect("Encoded word "
            "contains bytes nie decodable using {} charset".format(charset)))
        string = bstring.decode(charset, 'surrogateescape')
    wyjąwszy LookupError:
        string = bstring.decode('ascii', 'surrogateescape')
        jeżeli charset.lower() != 'unknown-8bit':
            defects.append(errors.CharsetError("Unknown charset {} "
                "in encoded word; decoded jako unknown bytes".format(charset)))
    zwróć string, charset, lang, defects


_cte_encoders = {
    'q': encode_q,
    'b': encode_b,
    }

_cte_encode_length = {
    'q': len_q,
    'b': len_b,
    }

def encode(string, charset='utf-8', encoding=Nic, lang=''):
    """Encode string using the CTE encoding that produces the shorter result.

    Produces an RFC 2047/2243 encoded word of the form:

        =?charset*lang?cte?encoded_string?=

    where '*lang' jest omitted unless the 'lang' parameter jest given a value.
    Optional argument charset (defaults to utf-8) specifies the charset to use
    to encode the string to binary before CTE encoding it.  Optional argument
    'encoding' jest the cte specifier dla the encoding that should be used ('q'
    albo 'b'); jeżeli it jest Nic (the default) the encoding which produces the
    shortest encoded sequence jest used, wyjąwszy that 'q' jest preferred jeżeli it jest up
    to five characters longer.  Optional argument 'lang' (default '') gives the
    RFC 2243 language string to specify w the encoded word.

    """
    jeżeli charset == 'unknown-8bit':
        bstring = string.encode('ascii', 'surrogateescape')
    inaczej:
        bstring = string.encode(charset)
    jeżeli encoding jest Nic:
        qlen = _cte_encode_length['q'](bstring)
        blen = _cte_encode_length['b'](bstring)
        # Bias toward q.  5 jest arbitrary.
        encoding = 'q' jeżeli qlen - blen < 5 inaczej 'b'
    encoded = _cte_encoders[encoding](bstring)
    jeżeli lang:
        lang = '*' + lang
    zwróć "=?{}{}?{}?{}?=".format(charset, lang, encoding, encoded)
