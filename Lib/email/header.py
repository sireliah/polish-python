# Copyright (C) 2002-2007 Python Software Foundation
# Author: Ben Gertzfield, Barry Warsaw
# Contact: email-sig@python.org

"""Header encoding oraz decoding functionality."""

__all__ = [
    'Header',
    'decode_header',
    'make_header',
    ]

zaimportuj re
zaimportuj binascii

zaimportuj email.quoprimime
zaimportuj email.base64mime

z email.errors zaimportuj HeaderParseError
z email zaimportuj charset jako _charset
Charset = _charset.Charset

NL = '\n'
SPACE = ' '
BSPACE = b' '
SPACE8 = ' ' * 8
EMPTYSTRING = ''
MAXLINELEN = 78
FWS = ' \t'

USASCII = Charset('us-ascii')
UTF8 = Charset('utf-8')

# Match encoded-word strings w the form =?charset?q?Hello_World?=
ecre = re.compile(r'''
  =\?                   # literal =?
  (?P<charset>[^?]*?)   # non-greedy up to the next ? jest the charset
  \?                    # literal ?
  (?P<encoding>[qb])    # either a "q" albo a "b", case insensitive
  \?                    # literal ?
  (?P<encoded>.*?)      # non-greedy up to the next ?= jest the encoded string
  \?=                   # literal ?=
  ''', re.VERBOSE | re.IGNORECASE | re.MULTILINE)

# Field name regexp, including trailing colon, but nie separating whitespace,
# according to RFC 2822.  Character range jest z tilde to exclamation mark.
# For use przy .match()
fcre = re.compile(r'[\041-\176]+:$')

# Find a header embedded w a putative header value.  Used to check for
# header injection attack.
_embeded_header = re.compile(r'\n[^ \t]+:')



# Helpers
_max_append = email.quoprimime._max_append



def decode_header(header):
    """Decode a message header value without converting charset.

    Returns a list of (string, charset) pairs containing each of the decoded
    parts of the header.  Charset jest Nic dla non-encoded parts of the header,
    otherwise a lower-case string containing the name of the character set
    specified w the encoded string.

    header may be a string that may albo may nie contain RFC2047 encoded words,
    albo it may be a Header object.

    An email.errors.HeaderParseError may be podnieśd when certain decoding error
    occurs (e.g. a base64 decoding exception).
    """
    # If it jest a Header object, we can just zwróć the encoded chunks.
    jeżeli hasattr(header, '_chunks'):
        zwróć [(_charset._encode(string, str(charset)), str(charset))
                    dla string, charset w header._chunks]
    # If no encoding, just zwróć the header przy no charset.
    jeżeli nie ecre.search(header):
        zwróć [(header, Nic)]
    # First step jest to parse all the encoded parts into triplets of the form
    # (encoded_string, encoding, charset).  For unencoded strings, the last
    # two parts will be Nic.
    words = []
    dla line w header.splitlines():
        parts = ecre.split(line)
        first = Prawda
        dopóki parts:
            unencoded = parts.pop(0)
            jeżeli first:
                unencoded = unencoded.lstrip()
                first = Nieprawda
            jeżeli unencoded:
                words.append((unencoded, Nic, Nic))
            jeżeli parts:
                charset = parts.pop(0).lower()
                encoding = parts.pop(0).lower()
                encoded = parts.pop(0)
                words.append((encoded, encoding, charset))
    # Now loop over words oraz remove words that consist of whitespace
    # between two encoded strings.
    droplist = []
    dla n, w w enumerate(words):
        jeżeli n>1 oraz w[1] oraz words[n-2][1] oraz words[n-1][0].isspace():
            droplist.append(n-1)
    dla d w reversed(droplist):
        usuń words[d]

    # The next step jest to decode each encoded word by applying the reverse
    # base64 albo quopri transformation.  decoded_words jest now a list of the
    # form (decoded_word, charset).
    decoded_words = []
    dla encoded_string, encoding, charset w words:
        jeżeli encoding jest Nic:
            # This jest an unencoded word.
            decoded_words.append((encoded_string, charset))
        albo_inaczej encoding == 'q':
            word = email.quoprimime.header_decode(encoded_string)
            decoded_words.append((word, charset))
        albo_inaczej encoding == 'b':
            paderr = len(encoded_string) % 4   # Postel's law: add missing padding
            jeżeli paderr:
                encoded_string += '==='[:4 - paderr]
            spróbuj:
                word = email.base64mime.decode(encoded_string)
            wyjąwszy binascii.Error:
                podnieś HeaderParseError('Base64 decoding error')
            inaczej:
                decoded_words.append((word, charset))
        inaczej:
            podnieś AssertionError('Unexpected encoding: ' + encoding)
    # Now convert all words to bytes oraz collapse consecutive runs of
    # similarly encoded words.
    collapsed = []
    last_word = last_charset = Nic
    dla word, charset w decoded_words:
        jeżeli isinstance(word, str):
            word = bytes(word, 'raw-unicode-escape')
        jeżeli last_word jest Nic:
            last_word = word
            last_charset = charset
        albo_inaczej charset != last_charset:
            collapsed.append((last_word, last_charset))
            last_word = word
            last_charset = charset
        albo_inaczej last_charset jest Nic:
            last_word += BSPACE + word
        inaczej:
            last_word += word
    collapsed.append((last_word, last_charset))
    zwróć collapsed



def make_header(decoded_seq, maxlinelen=Nic, header_name=Nic,
                continuation_ws=' '):
    """Create a Header z a sequence of pairs jako returned by decode_header()

    decode_header() takes a header value string oraz returns a sequence of
    pairs of the format (decoded_string, charset) where charset jest the string
    name of the character set.

    This function takes one of those sequence of pairs oraz returns a Header
    instance.  Optional maxlinelen, header_name, oraz continuation_ws are jako w
    the Header constructor.
    """
    h = Header(maxlinelen=maxlinelen, header_name=header_name,
               continuation_ws=continuation_ws)
    dla s, charset w decoded_seq:
        # Nic means us-ascii but we can simply dalej it on to h.append()
        jeżeli charset jest nie Nic oraz nie isinstance(charset, Charset):
            charset = Charset(charset)
        h.append(s, charset)
    zwróć h



klasa Header:
    def __init__(self, s=Nic, charset=Nic,
                 maxlinelen=Nic, header_name=Nic,
                 continuation_ws=' ', errors='strict'):
        """Create a MIME-compliant header that can contain many character sets.

        Optional s jest the initial header value.  If Nic, the initial header
        value jest nie set.  You can later append to the header przy .append()
        method calls.  s may be a byte string albo a Unicode string, but see the
        .append() documentation dla semantics.

        Optional charset serves two purposes: it has the same meaning jako the
        charset argument to the .append() method.  It also sets the default
        character set dla all subsequent .append() calls that omit the charset
        argument.  If charset jest nie provided w the constructor, the us-ascii
        charset jest used both jako s's initial charset oraz jako the default for
        subsequent .append() calls.

        The maximum line length can be specified explicitly via maxlinelen. For
        splitting the first line to a shorter value (to account dla the field
        header which isn't included w s, e.g. `Subject') dalej w the name of
        the field w header_name.  The default maxlinelen jest 78 jako recommended
        by RFC 2822.

        continuation_ws must be RFC 2822 compliant folding whitespace (usually
        either a space albo a hard tab) which will be prepended to continuation
        lines.

        errors jest dalejed through to the .append() call.
        """
        jeżeli charset jest Nic:
            charset = USASCII
        albo_inaczej nie isinstance(charset, Charset):
            charset = Charset(charset)
        self._charset = charset
        self._continuation_ws = continuation_ws
        self._chunks = []
        jeżeli s jest nie Nic:
            self.append(s, charset, errors)
        jeżeli maxlinelen jest Nic:
            maxlinelen = MAXLINELEN
        self._maxlinelen = maxlinelen
        jeżeli header_name jest Nic:
            self._headerlen = 0
        inaczej:
            # Take the separating colon oraz space into account.
            self._headerlen = len(header_name) + 2

    def __str__(self):
        """Return the string value of the header."""
        self._normalize()
        uchunks = []
        lastcs = Nic
        lastspace = Nic
        dla string, charset w self._chunks:
            # We must preserve spaces between encoded oraz non-encoded word
            # boundaries, which means dla us we need to add a space when we go
            # z a charset to Nic/us-ascii, albo z Nic/us-ascii to a
            # charset.  Only do this dla the second oraz subsequent chunks.
            # Don't add a space jeżeli the Nic/us-ascii string already has
            # a space (trailing albo leading depending on transition)
            nextcs = charset
            jeżeli nextcs == _charset.UNKNOWN8BIT:
                original_bytes = string.encode('ascii', 'surrogateescape')
                string = original_bytes.decode('ascii', 'replace')
            jeżeli uchunks:
                hasspace = string oraz self._nonctext(string[0])
                jeżeli lastcs nie w (Nic, 'us-ascii'):
                    jeżeli nextcs w (Nic, 'us-ascii') oraz nie hasspace:
                        uchunks.append(SPACE)
                        nextcs = Nic
                albo_inaczej nextcs nie w (Nic, 'us-ascii') oraz nie lastspace:
                    uchunks.append(SPACE)
            lastspace = string oraz self._nonctext(string[-1])
            lastcs = nextcs
            uchunks.append(string)
        zwróć EMPTYSTRING.join(uchunks)

    # Rich comparison operators dla equality only.  BAW: does it make sense to
    # have albo explicitly disable <, <=, >, >= operators?
    def __eq__(self, other):
        # other may be a Header albo a string.  Both are fine so coerce
        # ourselves to a unicode (of the unencoded header value), swap the
        # args oraz do another comparison.
        zwróć other == str(self)

    def append(self, s, charset=Nic, errors='strict'):
        """Append a string to the MIME header.

        Optional charset, jeżeli given, should be a Charset instance albo the name
        of a character set (which will be converted to a Charset instance).  A
        value of Nic (the default) means that the charset given w the
        constructor jest used.

        s may be a byte string albo a Unicode string.  If it jest a byte string
        (i.e. isinstance(s, str) jest false), then charset jest the encoding of
        that byte string, oraz a UnicodeError will be podnieśd jeżeli the string
        cannot be decoded przy that charset.  If s jest a Unicode string, then
        charset jest a hint specifying the character set of the characters w
        the string.  In either case, when producing an RFC 2822 compliant
        header using RFC 2047 rules, the string will be encoded using the
        output codec of the charset.  If the string cannot be encoded to the
        output codec, a UnicodeError will be podnieśd.

        Optional `errors' jest dalejed jako the errors argument to the decode
        call jeżeli s jest a byte string.
        """
        jeżeli charset jest Nic:
            charset = self._charset
        albo_inaczej nie isinstance(charset, Charset):
            charset = Charset(charset)
        jeżeli nie isinstance(s, str):
            input_charset = charset.input_codec albo 'us-ascii'
            jeżeli input_charset == _charset.UNKNOWN8BIT:
                s = s.decode('us-ascii', 'surrogateescape')
            inaczej:
                s = s.decode(input_charset, errors)
        # Ensure that the bytes we're storing can be decoded to the output
        # character set, otherwise an early error jest podnieśd.
        output_charset = charset.output_codec albo 'us-ascii'
        jeżeli output_charset != _charset.UNKNOWN8BIT:
            spróbuj:
                s.encode(output_charset, errors)
            wyjąwszy UnicodeEncodeError:
                jeżeli output_charset!='us-ascii':
                    podnieś
                charset = UTF8
        self._chunks.append((s, charset))

    def _nonctext(self, s):
        """Prawda jeżeli string s jest nie a ctext character of RFC822.
        """
        zwróć s.isspace() albo s w ('(', ')', '\\')

    def encode(self, splitchars=';, \t', maxlinelen=Nic, linesep='\n'):
        r"""Encode a message header into an RFC-compliant format.

        There are many issues involved w converting a given string dla use w
        an email header.  Only certain character sets are readable w most
        email clients, oraz jako header strings can only contain a subset of
        7-bit ASCII, care must be taken to properly convert oraz encode (with
        Base64 albo quoted-printable) header strings.  In addition, there jest a
        75-character length limit on any given encoded header field, so
        line-wrapping must be performed, even przy double-byte character sets.

        Optional maxlinelen specifies the maximum length of each generated
        line, exclusive of the linesep string.  Individual lines may be longer
        than maxlinelen jeżeli a folding point cannot be found.  The first line
        will be shorter by the length of the header name plus ": " jeżeli a header
        name was specified at Header construction time.  The default value for
        maxlinelen jest determined at header construction time.

        Optional splitchars jest a string containing characters which should be
        given extra weight by the splitting algorithm during normal header
        wrapping.  This jest w very rough support of RFC 2822's `higher level
        syntactic przerwijs':  split points preceded by a splitchar are preferred
        during line splitting, przy the characters preferred w the order w
        which they appear w the string.  Space oraz tab may be included w the
        string to indicate whether preference should be given to one over the
        other jako a split point when other split chars do nie appear w the line
        being split.  Splitchars does nie affect RFC 2047 encoded lines.

        Optional linesep jest a string to be used to separate the lines of
        the value.  The default value jest the most useful dla typical
        Python applications, but it can be set to \r\n to produce RFC-compliant
        line separators when needed.
        """
        self._normalize()
        jeżeli maxlinelen jest Nic:
            maxlinelen = self._maxlinelen
        # A maxlinelen of 0 means don't wrap.  For all practical purposes,
        # choosing a huge number here accomplishes that oraz makes the
        # _ValueFormatter algorithm much simpler.
        jeżeli maxlinelen == 0:
            maxlinelen = 1000000
        formatter = _ValueFormatter(self._headerlen, maxlinelen,
                                    self._continuation_ws, splitchars)
        lastcs = Nic
        hasspace = lastspace = Nic
        dla string, charset w self._chunks:
            jeżeli hasspace jest nie Nic:
                hasspace = string oraz self._nonctext(string[0])
                jeżeli lastcs nie w (Nic, 'us-ascii'):
                    jeżeli nie hasspace albo charset nie w (Nic, 'us-ascii'):
                        formatter.add_transition()
                albo_inaczej charset nie w (Nic, 'us-ascii') oraz nie lastspace:
                    formatter.add_transition()
            lastspace = string oraz self._nonctext(string[-1])
            lastcs = charset
            hasspace = Nieprawda
            lines = string.splitlines()
            jeżeli lines:
                formatter.feed('', lines[0], charset)
            inaczej:
                formatter.feed('', '', charset)
            dla line w lines[1:]:
                formatter.newline()
                jeżeli charset.header_encoding jest nie Nic:
                    formatter.feed(self._continuation_ws, ' ' + line.lstrip(),
                                   charset)
                inaczej:
                    sline = line.lstrip()
                    fws = line[:len(line)-len(sline)]
                    formatter.feed(fws, sline, charset)
            jeżeli len(lines) > 1:
                formatter.newline()
        jeżeli self._chunks:
            formatter.add_transition()
        value = formatter._str(linesep)
        jeżeli _embeded_header.search(value):
            podnieś HeaderParseError("header value appears to contain "
                "an embedded header: {!r}".format(value))
        zwróć value

    def _normalize(self):
        # Step 1: Normalize the chunks so that all runs of identical charsets
        # get collapsed into a single unicode string.
        chunks = []
        last_charset = Nic
        last_chunk = []
        dla string, charset w self._chunks:
            jeżeli charset == last_charset:
                last_chunk.append(string)
            inaczej:
                jeżeli last_charset jest nie Nic:
                    chunks.append((SPACE.join(last_chunk), last_charset))
                last_chunk = [string]
                last_charset = charset
        jeżeli last_chunk:
            chunks.append((SPACE.join(last_chunk), last_charset))
        self._chunks = chunks



klasa _ValueFormatter:
    def __init__(self, headerlen, maxlen, continuation_ws, splitchars):
        self._maxlen = maxlen
        self._continuation_ws = continuation_ws
        self._continuation_ws_len = len(continuation_ws)
        self._splitchars = splitchars
        self._lines = []
        self._current_line = _Accumulator(headerlen)

    def _str(self, linesep):
        self.newline()
        zwróć linesep.join(self._lines)

    def __str__(self):
        zwróć self._str(NL)

    def newline(self):
        end_of_line = self._current_line.pop()
        jeżeli end_of_line != (' ', ''):
            self._current_line.push(*end_of_line)
        jeżeli len(self._current_line) > 0:
            jeżeli self._current_line.is_onlyws():
                self._lines[-1] += str(self._current_line)
            inaczej:
                self._lines.append(str(self._current_line))
        self._current_line.reset()

    def add_transition(self):
        self._current_line.push(' ', '')

    def feed(self, fws, string, charset):
        # If the charset has no header encoding (i.e. it jest an ASCII encoding)
        # then we must split the header at the "highest level syntactic przerwij"
        # possible. Note that we don't have a lot of smarts about field
        # syntax; we just try to przerwij on semi-colons, then commas, then
        # whitespace.  Eventually, this should be pluggable.
        jeżeli charset.header_encoding jest Nic:
            self._ascii_split(fws, string, self._splitchars)
            zwróć
        # Otherwise, we're doing either a Base64 albo a quoted-printable
        # encoding which means we don't need to split the line on syntactic
        # przerwijs.  We can basically just find enough characters to fit on the
        # current line, minus the RFC 2047 chrome.  What makes this trickier
        # though jest that we have to split at octet boundaries, nie character
        # boundaries but it's only safe to split at character boundaries so at
        # best we can only get close.
        encoded_lines = charset.header_encode_lines(string, self._maxlengths())
        # The first element extends the current line, but jeżeli it's Nic then
        # nothing more fit on the current line so start a new line.
        spróbuj:
            first_line = encoded_lines.pop(0)
        wyjąwszy IndexError:
            # There are no encoded lines, so we're done.
            zwróć
        jeżeli first_line jest nie Nic:
            self._append_chunk(fws, first_line)
        spróbuj:
            last_line = encoded_lines.pop()
        wyjąwszy IndexError:
            # There was only one line.
            zwróć
        self.newline()
        self._current_line.push(self._continuation_ws, last_line)
        # Everything inaczej are full lines w themselves.
        dla line w encoded_lines:
            self._lines.append(self._continuation_ws + line)

    def _maxlengths(self):
        # The first line's length.
        uzyskaj self._maxlen - len(self._current_line)
        dopóki Prawda:
            uzyskaj self._maxlen - self._continuation_ws_len

    def _ascii_split(self, fws, string, splitchars):
        # The RFC 2822 header folding algorithm jest simple w principle but
        # complex w practice.  Lines may be folded any place where "folding
        # white space" appears by inserting a linesep character w front of the
        # FWS.  The complication jest that nie all spaces albo tabs qualify jako FWS,
        # oraz we are also supposed to prefer to przerwij at "higher level
        # syntactic przerwijs".  We can't do either of these without intimate
        # knowledge of the structure of structured headers, which we don't have
        # here.  So the best we can do here jest prefer to przerwij at the specified
        # splitchars, oraz hope that we don't choose any spaces albo tabs that
        # aren't legal FWS.  (This jest at least better than the old algorithm,
        # where we would sometimes *introduce* FWS after a splitchar, albo the
        # algorithm before that, where we would turn all white space runs into
        # single spaces albo tabs.)
        parts = re.split("(["+FWS+"]+)", fws+string)
        jeżeli parts[0]:
            parts[:0] = ['']
        inaczej:
            parts.pop(0)
        dla fws, part w zip(*[iter(parts)]*2):
            self._append_chunk(fws, part)

    def _append_chunk(self, fws, string):
        self._current_line.push(fws, string)
        jeżeli len(self._current_line) > self._maxlen:
            # Find the best split point, working backward z the end.
            # There might be none, on a long first line.
            dla ch w self._splitchars:
                dla i w range(self._current_line.part_count()-1, 0, -1):
                    jeżeli ch.isspace():
                        fws = self._current_line[i][0]
                        jeżeli fws oraz fws[0]==ch:
                            przerwij
                    prevpart = self._current_line[i-1][1]
                    jeżeli prevpart oraz prevpart[-1]==ch:
                        przerwij
                inaczej:
                    kontynuuj
                przerwij
            inaczej:
                fws, part = self._current_line.pop()
                jeżeli self._current_line._initial_size > 0:
                    # There will be a header, so leave it on a line by itself.
                    self.newline()
                    jeżeli nie fws:
                        # We don't use continuation_ws here because the whitespace
                        # after a header should always be a space.
                        fws = ' '
                self._current_line.push(fws, part)
                zwróć
            remainder = self._current_line.pop_from(i)
            self._lines.append(str(self._current_line))
            self._current_line.reset(remainder)


klasa _Accumulator(list):

    def __init__(self, initial_size=0):
        self._initial_size = initial_size
        super().__init__()

    def push(self, fws, string):
        self.append((fws, string))

    def pop_from(self, i=0):
        popped = self[i:]
        self[i:] = []
        zwróć popped

    def pop(self):
        jeżeli self.part_count()==0:
            zwróć ('', '')
        zwróć super().pop()

    def __len__(self):
        zwróć sum((len(fws)+len(part) dla fws, part w self),
                   self._initial_size)

    def __str__(self):
        zwróć EMPTYSTRING.join((EMPTYSTRING.join((fws, part))
                                dla fws, part w self))

    def reset(self, startval=Nic):
        jeżeli startval jest Nic:
            startval = []
        self[:] = startval
        self._initial_size = 0

    def is_onlyws(self):
        zwróć self._initial_size==0 oraz (nie self albo str(self).isspace())

    def part_count(self):
        zwróć super().__len__()
