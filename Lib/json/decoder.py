"""Implementation of JSONDecoder
"""
zaimportuj re

z json zaimportuj scanner
spróbuj:
    z _json zaimportuj scanstring jako c_scanstring
wyjąwszy ImportError:
    c_scanstring = Nic

__all__ = ['JSONDecoder', 'JSONDecodeError']

FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL

NaN = float('nan')
PosInf = float('inf')
NegInf = float('-inf')


klasa JSONDecodeError(ValueError):
    """Subclass of ValueError przy the following additional properties:

    msg: The unformatted error message
    doc: The JSON document being parsed
    pos: The start index of doc where parsing failed
    lineno: The line corresponding to pos
    colno: The column corresponding to pos

    """
    # Note that this exception jest used z _json
    def __init__(self, msg, doc, pos):
        lineno = doc.count('\n', 0, pos) + 1
        colno = pos - doc.rfind('\n', 0, pos)
        errmsg = '%s: line %d column %d (char %d)' % (msg, lineno, colno, pos)
        ValueError.__init__(self, errmsg)
        self.msg = msg
        self.doc = doc
        self.pos = pos
        self.lineno = lineno
        self.colno = colno

    def __reduce__(self):
        zwróć self.__class__, (self.msg, self.doc, self.pos)


_CONSTANTS = {
    '-Infinity': NegInf,
    'Infinity': PosInf,
    'NaN': NaN,
}


STRINGCHUNK = re.compile(r'(.*?)(["\\\x00-\x1f])', FLAGS)
BACKSLASH = {
    '"': '"', '\\': '\\', '/': '/',
    'b': '\b', 'f': '\f', 'n': '\n', 'r': '\r', 't': '\t',
}

def _decode_uXXXX(s, pos):
    esc = s[pos + 1:pos + 5]
    jeżeli len(esc) == 4 oraz esc[1] nie w 'xX':
        spróbuj:
            zwróć int(esc, 16)
        wyjąwszy ValueError:
            dalej
    msg = "Invalid \\uXXXX escape"
    podnieś JSONDecodeError(msg, s, pos)

def py_scanstring(s, end, strict=Prawda,
        _b=BACKSLASH, _m=STRINGCHUNK.match):
    """Scan the string s dla a JSON string. End jest the index of the
    character w s after the quote that started the JSON string.
    Unescapes all valid JSON string escape sequences oraz podnieśs ValueError
    on attempt to decode an invalid string. If strict jest Nieprawda then literal
    control characters are allowed w the string.

    Returns a tuple of the decoded string oraz the index of the character w s
    after the end quote."""
    chunks = []
    _append = chunks.append
    begin = end - 1
    dopóki 1:
        chunk = _m(s, end)
        jeżeli chunk jest Nic:
            podnieś JSONDecodeError("Unterminated string starting at", s, begin)
        end = chunk.end()
        content, terminator = chunk.groups()
        # Content jest contains zero albo more unescaped string characters
        jeżeli content:
            _append(content)
        # Terminator jest the end of string, a literal control character,
        # albo a backslash denoting that an escape sequence follows
        jeżeli terminator == '"':
            przerwij
        albo_inaczej terminator != '\\':
            jeżeli strict:
                #msg = "Invalid control character %r at" % (terminator,)
                msg = "Invalid control character {0!r} at".format(terminator)
                podnieś JSONDecodeError(msg, s, end)
            inaczej:
                _append(terminator)
                kontynuuj
        spróbuj:
            esc = s[end]
        wyjąwszy IndexError:
            podnieś JSONDecodeError("Unterminated string starting at", s, begin)
        # If nie a unicode escape sequence, must be w the lookup table
        jeżeli esc != 'u':
            spróbuj:
                char = _b[esc]
            wyjąwszy KeyError:
                msg = "Invalid \\escape: {0!r}".format(esc)
                podnieś JSONDecodeError(msg, s, end)
            end += 1
        inaczej:
            uni = _decode_uXXXX(s, end)
            end += 5
            jeżeli 0xd800 <= uni <= 0xdbff oraz s[end:end + 2] == '\\u':
                uni2 = _decode_uXXXX(s, end + 1)
                jeżeli 0xdc00 <= uni2 <= 0xdfff:
                    uni = 0x10000 + (((uni - 0xd800) << 10) | (uni2 - 0xdc00))
                    end += 6
            char = chr(uni)
        _append(char)
    zwróć ''.join(chunks), end


# Use speedup jeżeli available
scanstring = c_scanstring albo py_scanstring

WHITESPACE = re.compile(r'[ \t\n\r]*', FLAGS)
WHITESPACE_STR = ' \t\n\r'


def JSONObject(s_and_end, strict, scan_once, object_hook, object_pairs_hook,
               memo=Nic, _w=WHITESPACE.match, _ws=WHITESPACE_STR):
    s, end = s_and_end
    pairs = []
    pairs_append = pairs.append
    # Backwards compatibility
    jeżeli memo jest Nic:
        memo = {}
    memo_get = memo.setdefault
    # Use a slice to prevent IndexError z being podnieśd, the following
    # check will podnieś a more specific ValueError jeżeli the string jest empty
    nextchar = s[end:end + 1]
    # Normally we expect nextchar == '"'
    jeżeli nextchar != '"':
        jeżeli nextchar w _ws:
            end = _w(s, end).end()
            nextchar = s[end:end + 1]
        # Trivial empty object
        jeżeli nextchar == '}':
            jeżeli object_pairs_hook jest nie Nic:
                result = object_pairs_hook(pairs)
                zwróć result, end + 1
            pairs = {}
            jeżeli object_hook jest nie Nic:
                pairs = object_hook(pairs)
            zwróć pairs, end + 1
        albo_inaczej nextchar != '"':
            podnieś JSONDecodeError(
                "Expecting property name enclosed w double quotes", s, end)
    end += 1
    dopóki Prawda:
        key, end = scanstring(s, end, strict)
        key = memo_get(key, key)
        # To skip some function call overhead we optimize the fast paths where
        # the JSON key separator jest ": " albo just ":".
        jeżeli s[end:end + 1] != ':':
            end = _w(s, end).end()
            jeżeli s[end:end + 1] != ':':
                podnieś JSONDecodeError("Expecting ':' delimiter", s, end)
        end += 1

        spróbuj:
            jeżeli s[end] w _ws:
                end += 1
                jeżeli s[end] w _ws:
                    end = _w(s, end + 1).end()
        wyjąwszy IndexError:
            dalej

        spróbuj:
            value, end = scan_once(s, end)
        wyjąwszy StopIteration jako err:
            podnieś JSONDecodeError("Expecting value", s, err.value) z Nic
        pairs_append((key, value))
        spróbuj:
            nextchar = s[end]
            jeżeli nextchar w _ws:
                end = _w(s, end + 1).end()
                nextchar = s[end]
        wyjąwszy IndexError:
            nextchar = ''
        end += 1

        jeżeli nextchar == '}':
            przerwij
        albo_inaczej nextchar != ',':
            podnieś JSONDecodeError("Expecting ',' delimiter", s, end - 1)
        end = _w(s, end).end()
        nextchar = s[end:end + 1]
        end += 1
        jeżeli nextchar != '"':
            podnieś JSONDecodeError(
                "Expecting property name enclosed w double quotes", s, end - 1)
    jeżeli object_pairs_hook jest nie Nic:
        result = object_pairs_hook(pairs)
        zwróć result, end
    pairs = dict(pairs)
    jeżeli object_hook jest nie Nic:
        pairs = object_hook(pairs)
    zwróć pairs, end

def JSONArray(s_and_end, scan_once, _w=WHITESPACE.match, _ws=WHITESPACE_STR):
    s, end = s_and_end
    values = []
    nextchar = s[end:end + 1]
    jeżeli nextchar w _ws:
        end = _w(s, end + 1).end()
        nextchar = s[end:end + 1]
    # Look-ahead dla trivial empty array
    jeżeli nextchar == ']':
        zwróć values, end + 1
    _append = values.append
    dopóki Prawda:
        spróbuj:
            value, end = scan_once(s, end)
        wyjąwszy StopIteration jako err:
            podnieś JSONDecodeError("Expecting value", s, err.value) z Nic
        _append(value)
        nextchar = s[end:end + 1]
        jeżeli nextchar w _ws:
            end = _w(s, end + 1).end()
            nextchar = s[end:end + 1]
        end += 1
        jeżeli nextchar == ']':
            przerwij
        albo_inaczej nextchar != ',':
            podnieś JSONDecodeError("Expecting ',' delimiter", s, end - 1)
        spróbuj:
            jeżeli s[end] w _ws:
                end += 1
                jeżeli s[end] w _ws:
                    end = _w(s, end + 1).end()
        wyjąwszy IndexError:
            dalej

    zwróć values, end


klasa JSONDecoder(object):
    """Simple JSON <http://json.org> decoder

    Performs the following translations w decoding by default:

    +---------------+-------------------+
    | JSON          | Python            |
    +===============+===================+
    | object        | dict              |
    +---------------+-------------------+
    | array         | list              |
    +---------------+-------------------+
    | string        | str               |
    +---------------+-------------------+
    | number (int)  | int               |
    +---------------+-------------------+
    | number (real) | float             |
    +---------------+-------------------+
    | true          | Prawda              |
    +---------------+-------------------+
    | false         | Nieprawda             |
    +---------------+-------------------+
    | null          | Nic              |
    +---------------+-------------------+

    It also understands ``NaN``, ``Infinity``, oraz ``-Infinity`` as
    their corresponding ``float`` values, which jest outside the JSON spec.

    """

    def __init__(self, object_hook=Nic, parse_float=Nic,
            parse_int=Nic, parse_constant=Nic, strict=Prawda,
            object_pairs_hook=Nic):
        """``object_hook``, jeżeli specified, will be called przy the result
        of every JSON object decoded oraz its zwróć value will be used w
        place of the given ``dict``.  This can be used to provide custom
        deserializations (e.g. to support JSON-RPC klasa hinting).

        ``object_pairs_hook``, jeżeli specified will be called przy the result of
        every JSON object decoded przy an ordered list of pairs.  The zwróć
        value of ``object_pairs_hook`` will be used instead of the ``dict``.
        This feature can be used to implement custom decoders that rely on the
        order that the key oraz value pairs are decoded (dla example,
        collections.OrderedDict will remember the order of insertion). If
        ``object_hook`` jest also defined, the ``object_pairs_hook`` takes
        priority.

        ``parse_float``, jeżeli specified, will be called przy the string
        of every JSON float to be decoded. By default this jest equivalent to
        float(num_str). This can be used to use another datatype albo parser
        dla JSON floats (e.g. decimal.Decimal).

        ``parse_int``, jeżeli specified, will be called przy the string
        of every JSON int to be decoded. By default this jest equivalent to
        int(num_str). This can be used to use another datatype albo parser
        dla JSON integers (e.g. float).

        ``parse_constant``, jeżeli specified, will be called przy one of the
        following strings: -Infinity, Infinity, NaN.
        This can be used to podnieś an exception jeżeli invalid JSON numbers
        are encountered.

        If ``strict`` jest false (true jest the default), then control
        characters will be allowed inside strings.  Control characters w
        this context are those przy character codes w the 0-31 range,
        including ``'\\t'`` (tab), ``'\\n'``, ``'\\r'`` oraz ``'\\0'``.

        """
        self.object_hook = object_hook
        self.parse_float = parse_float albo float
        self.parse_int = parse_int albo int
        self.parse_constant = parse_constant albo _CONSTANTS.__getitem__
        self.strict = strict
        self.object_pairs_hook = object_pairs_hook
        self.parse_object = JSONObject
        self.parse_array = JSONArray
        self.parse_string = scanstring
        self.memo = {}
        self.scan_once = scanner.make_scanner(self)


    def decode(self, s, _w=WHITESPACE.match):
        """Return the Python representation of ``s`` (a ``str`` instance
        containing a JSON document).

        """
        obj, end = self.raw_decode(s, idx=_w(s, 0).end())
        end = _w(s, end).end()
        jeżeli end != len(s):
            podnieś JSONDecodeError("Extra data", s, end)
        zwróć obj

    def raw_decode(self, s, idx=0):
        """Decode a JSON document z ``s`` (a ``str`` beginning with
        a JSON document) oraz zwróć a 2-tuple of the Python
        representation oraz the index w ``s`` where the document ended.

        This can be used to decode a JSON document z a string that may
        have extraneous data at the end.

        """
        spróbuj:
            obj, end = self.scan_once(s, idx)
        wyjąwszy StopIteration jako err:
            podnieś JSONDecodeError("Expecting value", s, err.value) z Nic
        zwróć obj, end
