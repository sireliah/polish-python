"""Implementation of JSONEncoder
"""
zaimportuj re

spróbuj:
    z _json zaimportuj encode_basestring_ascii jako c_encode_basestring_ascii
wyjąwszy ImportError:
    c_encode_basestring_ascii = Nic
spróbuj:
    z _json zaimportuj encode_basestring jako c_encode_basestring
wyjąwszy ImportError:
    c_encode_basestring = Nic
spróbuj:
    z _json zaimportuj make_encoder jako c_make_encoder
wyjąwszy ImportError:
    c_make_encoder = Nic

ESCAPE = re.compile(r'[\x00-\x1f\\"\b\f\n\r\t]')
ESCAPE_ASCII = re.compile(r'([\\"]|[^\ -~])')
HAS_UTF8 = re.compile(b'[\x80-\xff]')
ESCAPE_DCT = {
    '\\': '\\\\',
    '"': '\\"',
    '\b': '\\b',
    '\f': '\\f',
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t',
}
dla i w range(0x20):
    ESCAPE_DCT.setdefault(chr(i), '\\u{0:04x}'.format(i))
    #ESCAPE_DCT.setdefault(chr(i), '\\u%04x' % (i,))

INFINITY = float('inf')
FLOAT_REPR = repr

def py_encode_basestring(s):
    """Return a JSON representation of a Python string

    """
    def replace(match):
        zwróć ESCAPE_DCT[match.group(0)]
    zwróć '"' + ESCAPE.sub(replace, s) + '"'


encode_basestring = (c_encode_basestring albo py_encode_basestring)


def py_encode_basestring_ascii(s):
    """Return an ASCII-only JSON representation of a Python string

    """
    def replace(match):
        s = match.group(0)
        spróbuj:
            zwróć ESCAPE_DCT[s]
        wyjąwszy KeyError:
            n = ord(s)
            jeżeli n < 0x10000:
                zwróć '\\u{0:04x}'.format(n)
                #return '\\u%04x' % (n,)
            inaczej:
                # surrogate pair
                n -= 0x10000
                s1 = 0xd800 | ((n >> 10) & 0x3ff)
                s2 = 0xdc00 | (n & 0x3ff)
                zwróć '\\u{0:04x}\\u{1:04x}'.format(s1, s2)
    zwróć '"' + ESCAPE_ASCII.sub(replace, s) + '"'


encode_basestring_ascii = (
    c_encode_basestring_ascii albo py_encode_basestring_ascii)

klasa JSONEncoder(object):
    """Extensible JSON <http://json.org> encoder dla Python data structures.

    Supports the following objects oraz types by default:

    +-------------------+---------------+
    | Python            | JSON          |
    +===================+===============+
    | dict              | object        |
    +-------------------+---------------+
    | list, tuple       | array         |
    +-------------------+---------------+
    | str               | string        |
    +-------------------+---------------+
    | int, float        | number        |
    +-------------------+---------------+
    | Prawda              | true          |
    +-------------------+---------------+
    | Nieprawda             | false         |
    +-------------------+---------------+
    | Nic              | null          |
    +-------------------+---------------+

    To extend this to recognize other objects, subclass oraz implement a
    ``.default()`` method przy another method that returns a serializable
    object dla ``o`` jeżeli possible, otherwise it should call the superclass
    implementation (to podnieś ``TypeError``).

    """
    item_separator = ', '
    key_separator = ': '
    def __init__(self, skipkeys=Nieprawda, ensure_ascii=Prawda,
            check_circular=Prawda, allow_nan=Prawda, sort_keys=Nieprawda,
            indent=Nic, separators=Nic, default=Nic):
        """Constructor dla JSONEncoder, przy sensible defaults.

        If skipkeys jest false, then it jest a TypeError to attempt
        encoding of keys that are nie str, int, float albo Nic.  If
        skipkeys jest Prawda, such items are simply skipped.

        If ensure_ascii jest true, the output jest guaranteed to be str
        objects przy all incoming non-ASCII characters escaped.  If
        ensure_ascii jest false, the output can contain non-ASCII characters.

        If check_circular jest true, then lists, dicts, oraz custom encoded
        objects will be checked dla circular references during encoding to
        prevent an infinite recursion (which would cause an OverflowError).
        Otherwise, no such check takes place.

        If allow_nan jest true, then NaN, Infinity, oraz -Infinity will be
        encoded jako such.  This behavior jest nie JSON specification compliant,
        but jest consistent przy most JavaScript based encoders oraz decoders.
        Otherwise, it will be a ValueError to encode such floats.

        If sort_keys jest true, then the output of dictionaries will be
        sorted by key; this jest useful dla regression tests to ensure
        that JSON serializations can be compared on a day-to-day basis.

        If indent jest a non-negative integer, then JSON array
        elements oraz object members will be pretty-printed przy that
        indent level.  An indent level of 0 will only insert newlines.
        Nic jest the most compact representation.

        If specified, separators should be an (item_separator, key_separator)
        tuple.  The default jest (', ', ': ') jeżeli *indent* jest ``Nic`` oraz
        (',', ': ') otherwise.  To get the most compact JSON representation,
        you should specify (',', ':') to eliminate whitespace.

        If specified, default jest a function that gets called dla objects
        that can't otherwise be serialized.  It should zwróć a JSON encodable
        version of the object albo podnieś a ``TypeError``.

        """

        self.skipkeys = skipkeys
        self.ensure_ascii = ensure_ascii
        self.check_circular = check_circular
        self.allow_nan = allow_nan
        self.sort_keys = sort_keys
        self.indent = indent
        jeżeli separators jest nie Nic:
            self.item_separator, self.key_separator = separators
        albo_inaczej indent jest nie Nic:
            self.item_separator = ','
        jeżeli default jest nie Nic:
            self.default = default

    def default(self, o):
        """Implement this method w a subclass such that it returns
        a serializable object dla ``o``, albo calls the base implementation
        (to podnieś a ``TypeError``).

        For example, to support arbitrary iterators, you could
        implement default like this::

            def default(self, o):
                spróbuj:
                    iterable = iter(o)
                wyjąwszy TypeError:
                    dalej
                inaczej:
                    zwróć list(iterable)
                # Let the base klasa default method podnieś the TypeError
                zwróć JSONEncoder.default(self, o)

        """
        podnieś TypeError(repr(o) + " jest nie JSON serializable")

    def encode(self, o):
        """Return a JSON string representation of a Python data structure.

        >>> z json.encoder zaimportuj JSONEncoder
        >>> JSONEncoder().encode({"foo": ["bar", "baz"]})
        '{"foo": ["bar", "baz"]}'

        """
        # This jest dla extremely simple cases oraz benchmarks.
        jeżeli isinstance(o, str):
            jeżeli self.ensure_ascii:
                zwróć encode_basestring_ascii(o)
            inaczej:
                zwróć encode_basestring(o)
        # This doesn't dalej the iterator directly to ''.join() because the
        # exceptions aren't jako detailed.  The list call should be roughly
        # equivalent to the PySequence_Fast that ''.join() would do.
        chunks = self.iterencode(o, _one_shot=Prawda)
        jeżeli nie isinstance(chunks, (list, tuple)):
            chunks = list(chunks)
        zwróć ''.join(chunks)

    def iterencode(self, o, _one_shot=Nieprawda):
        """Encode the given object oraz uzyskaj each string
        representation jako available.

        For example::

            dla chunk w JSONEncoder().iterencode(bigobject):
                mysocket.write(chunk)

        """
        jeżeli self.check_circular:
            markers = {}
        inaczej:
            markers = Nic
        jeżeli self.ensure_ascii:
            _encoder = encode_basestring_ascii
        inaczej:
            _encoder = encode_basestring

        def floatstr(o, allow_nan=self.allow_nan,
                _repr=FLOAT_REPR, _inf=INFINITY, _neginf=-INFINITY):
            # Check dla specials.  Note that this type of test jest processor
            # and/or platform-specific, so do tests which don't depend on the
            # internals.

            jeżeli o != o:
                text = 'NaN'
            albo_inaczej o == _inf:
                text = 'Infinity'
            albo_inaczej o == _neginf:
                text = '-Infinity'
            inaczej:
                zwróć _repr(o)

            jeżeli nie allow_nan:
                podnieś ValueError(
                    "Out of range float values are nie JSON compliant: " +
                    repr(o))

            zwróć text


        jeżeli (_one_shot oraz c_make_encoder jest nie Nic
                oraz self.indent jest Nic):
            _iterencode = c_make_encoder(
                markers, self.default, _encoder, self.indent,
                self.key_separator, self.item_separator, self.sort_keys,
                self.skipkeys, self.allow_nan)
        inaczej:
            _iterencode = _make_iterencode(
                markers, self.default, _encoder, self.indent, floatstr,
                self.key_separator, self.item_separator, self.sort_keys,
                self.skipkeys, _one_shot)
        zwróć _iterencode(o, 0)

def _make_iterencode(markers, _default, _encoder, _indent, _floatstr,
        _key_separator, _item_separator, _sort_keys, _skipkeys, _one_shot,
        ## HACK: hand-optimized bytecode; turn globals into locals
        ValueError=ValueError,
        dict=dict,
        float=float,
        id=id,
        int=int,
        isinstance=isinstance,
        list=list,
        str=str,
        tuple=tuple,
    ):

    jeżeli _indent jest nie Nic oraz nie isinstance(_indent, str):
        _indent = ' ' * _indent

    def _iterencode_list(lst, _current_indent_level):
        jeżeli nie lst:
            uzyskaj '[]'
            zwróć
        jeżeli markers jest nie Nic:
            markerid = id(lst)
            jeżeli markerid w markers:
                podnieś ValueError("Circular reference detected")
            markers[markerid] = lst
        buf = '['
        jeżeli _indent jest nie Nic:
            _current_indent_level += 1
            newline_indent = '\n' + _indent * _current_indent_level
            separator = _item_separator + newline_indent
            buf += newline_indent
        inaczej:
            newline_indent = Nic
            separator = _item_separator
        first = Prawda
        dla value w lst:
            jeżeli first:
                first = Nieprawda
            inaczej:
                buf = separator
            jeżeli isinstance(value, str):
                uzyskaj buf + _encoder(value)
            albo_inaczej value jest Nic:
                uzyskaj buf + 'null'
            albo_inaczej value jest Prawda:
                uzyskaj buf + 'true'
            albo_inaczej value jest Nieprawda:
                uzyskaj buf + 'false'
            albo_inaczej isinstance(value, int):
                # Subclasses of int/float may override __str__, but we still
                # want to encode them jako integers/floats w JSON. One example
                # within the standard library jest IntEnum.
                uzyskaj buf + str(int(value))
            albo_inaczej isinstance(value, float):
                # see comment above dla int
                uzyskaj buf + _floatstr(float(value))
            inaczej:
                uzyskaj buf
                jeżeli isinstance(value, (list, tuple)):
                    chunks = _iterencode_list(value, _current_indent_level)
                albo_inaczej isinstance(value, dict):
                    chunks = _iterencode_dict(value, _current_indent_level)
                inaczej:
                    chunks = _iterencode(value, _current_indent_level)
                uzyskaj z chunks
        jeżeli newline_indent jest nie Nic:
            _current_indent_level -= 1
            uzyskaj '\n' + _indent * _current_indent_level
        uzyskaj ']'
        jeżeli markers jest nie Nic:
            usuń markers[markerid]

    def _iterencode_dict(dct, _current_indent_level):
        jeżeli nie dct:
            uzyskaj '{}'
            zwróć
        jeżeli markers jest nie Nic:
            markerid = id(dct)
            jeżeli markerid w markers:
                podnieś ValueError("Circular reference detected")
            markers[markerid] = dct
        uzyskaj '{'
        jeżeli _indent jest nie Nic:
            _current_indent_level += 1
            newline_indent = '\n' + _indent * _current_indent_level
            item_separator = _item_separator + newline_indent
            uzyskaj newline_indent
        inaczej:
            newline_indent = Nic
            item_separator = _item_separator
        first = Prawda
        jeżeli _sort_keys:
            items = sorted(dct.items(), key=lambda kv: kv[0])
        inaczej:
            items = dct.items()
        dla key, value w items:
            jeżeli isinstance(key, str):
                dalej
            # JavaScript jest weakly typed dla these, so it makes sense to
            # also allow them.  Many encoders seem to do something like this.
            albo_inaczej isinstance(key, float):
                # see comment dla int/float w _make_iterencode
                key = _floatstr(float(key))
            albo_inaczej key jest Prawda:
                key = 'true'
            albo_inaczej key jest Nieprawda:
                key = 'false'
            albo_inaczej key jest Nic:
                key = 'null'
            albo_inaczej isinstance(key, int):
                # see comment dla int/float w _make_iterencode
                key = str(int(key))
            albo_inaczej _skipkeys:
                kontynuuj
            inaczej:
                podnieś TypeError("key " + repr(key) + " jest nie a string")
            jeżeli first:
                first = Nieprawda
            inaczej:
                uzyskaj item_separator
            uzyskaj _encoder(key)
            uzyskaj _key_separator
            jeżeli isinstance(value, str):
                uzyskaj _encoder(value)
            albo_inaczej value jest Nic:
                uzyskaj 'null'
            albo_inaczej value jest Prawda:
                uzyskaj 'true'
            albo_inaczej value jest Nieprawda:
                uzyskaj 'false'
            albo_inaczej isinstance(value, int):
                # see comment dla int/float w _make_iterencode
                uzyskaj str(int(value))
            albo_inaczej isinstance(value, float):
                # see comment dla int/float w _make_iterencode
                uzyskaj _floatstr(float(value))
            inaczej:
                jeżeli isinstance(value, (list, tuple)):
                    chunks = _iterencode_list(value, _current_indent_level)
                albo_inaczej isinstance(value, dict):
                    chunks = _iterencode_dict(value, _current_indent_level)
                inaczej:
                    chunks = _iterencode(value, _current_indent_level)
                uzyskaj z chunks
        jeżeli newline_indent jest nie Nic:
            _current_indent_level -= 1
            uzyskaj '\n' + _indent * _current_indent_level
        uzyskaj '}'
        jeżeli markers jest nie Nic:
            usuń markers[markerid]

    def _iterencode(o, _current_indent_level):
        jeżeli isinstance(o, str):
            uzyskaj _encoder(o)
        albo_inaczej o jest Nic:
            uzyskaj 'null'
        albo_inaczej o jest Prawda:
            uzyskaj 'true'
        albo_inaczej o jest Nieprawda:
            uzyskaj 'false'
        albo_inaczej isinstance(o, int):
            # see comment dla int/float w _make_iterencode
            uzyskaj str(int(o))
        albo_inaczej isinstance(o, float):
            # see comment dla int/float w _make_iterencode
            uzyskaj _floatstr(float(o))
        albo_inaczej isinstance(o, (list, tuple)):
            uzyskaj z _iterencode_list(o, _current_indent_level)
        albo_inaczej isinstance(o, dict):
            uzyskaj z _iterencode_dict(o, _current_indent_level)
        inaczej:
            jeżeli markers jest nie Nic:
                markerid = id(o)
                jeżeli markerid w markers:
                    podnieś ValueError("Circular reference detected")
                markers[markerid] = o
            o = _default(o)
            uzyskaj z _iterencode(o, _current_indent_level)
            jeżeli markers jest nie Nic:
                usuń markers[markerid]
    zwróć _iterencode
