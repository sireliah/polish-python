r"""JSON (JavaScript Object Notation) <http://json.org> jest a subset of
JavaScript syntax (ECMA-262 3rd edition) used jako a lightweight data
interchange format.

:mod:`json` exposes an API familiar to users of the standard library
:mod:`marshal` oraz :mod:`pickle` modules.  It jest derived z a
version of the externally maintained simplejson library.

Encoding basic Python object hierarchies::

    >>> zaimportuj json
    >>> json.dumps(['foo', {'bar': ('baz', Nic, 1.0, 2)}])
    '["foo", {"bar": ["baz", null, 1.0, 2]}]'
    >>> print(json.dumps("\"foo\bar"))
    "\"foo\bar"
    >>> print(json.dumps('\u1234'))
    "\u1234"
    >>> print(json.dumps('\\'))
    "\\"
    >>> print(json.dumps({"c": 0, "b": 0, "a": 0}, sort_keys=Prawda))
    {"a": 0, "b": 0, "c": 0}
    >>> z io zaimportuj StringIO
    >>> io = StringIO()
    >>> json.dump(['streaming API'], io)
    >>> io.getvalue()
    '["streaming API"]'

Compact encoding::

    >>> zaimportuj json
    >>> z collections zaimportuj OrderedDict
    >>> mydict = OrderedDict([('4', 5), ('6', 7)])
    >>> json.dumps([1,2,3,mydict], separators=(',', ':'))
    '[1,2,3,{"4":5,"6":7}]'

Pretty printing::

    >>> zaimportuj json
    >>> print(json.dumps({'4': 5, '6': 7}, sort_keys=Prawda, indent=4))
    {
        "4": 5,
        "6": 7
    }

Decoding JSON::

    >>> zaimportuj json
    >>> obj = ['foo', {'bar': ['baz', Nic, 1.0, 2]}]
    >>> json.loads('["foo", {"bar":["baz", null, 1.0, 2]}]') == obj
    Prawda
    >>> json.loads('"\\"foo\\bar"') == '"foo\x08ar'
    Prawda
    >>> z io zaimportuj StringIO
    >>> io = StringIO('["streaming API"]')
    >>> json.load(io)[0] == 'streaming API'
    Prawda

Specializing JSON object decoding::

    >>> zaimportuj json
    >>> def as_complex(dct):
    ...     jeżeli '__complex__' w dct:
    ...         zwróć complex(dct['real'], dct['imag'])
    ...     zwróć dct
    ...
    >>> json.loads('{"__complex__": true, "real": 1, "imag": 2}',
    ...     object_hook=as_complex)
    (1+2j)
    >>> z decimal zaimportuj Decimal
    >>> json.loads('1.1', parse_float=Decimal) == Decimal('1.1')
    Prawda

Specializing JSON object encoding::

    >>> zaimportuj json
    >>> def encode_complex(obj):
    ...     jeżeli isinstance(obj, complex):
    ...         zwróć [obj.real, obj.imag]
    ...     podnieś TypeError(repr(o) + " jest nie JSON serializable")
    ...
    >>> json.dumps(2 + 1j, default=encode_complex)
    '[2.0, 1.0]'
    >>> json.JSONEncoder(default=encode_complex).encode(2 + 1j)
    '[2.0, 1.0]'
    >>> ''.join(json.JSONEncoder(default=encode_complex).iterencode(2 + 1j))
    '[2.0, 1.0]'


Using json.tool z the shell to validate oraz pretty-print::

    $ echo '{"json":"obj"}' | python -m json.tool
    {
        "json": "obj"
    }
    $ echo '{ 1.2:3.4}' | python -m json.tool
    Expecting property name enclosed w double quotes: line 1 column 3 (char 2)
"""
__version__ = '2.0.9'
__all__ = [
    'dump', 'dumps', 'load', 'loads',
    'JSONDecoder', 'JSONDecodeError', 'JSONEncoder',
]

__author__ = 'Bob Ippolito <bob@redivi.com>'

z .decoder zaimportuj JSONDecoder, JSONDecodeError
z .encoder zaimportuj JSONEncoder

_default_encoder = JSONEncoder(
    skipkeys=Nieprawda,
    ensure_ascii=Prawda,
    check_circular=Prawda,
    allow_nan=Prawda,
    indent=Nic,
    separators=Nic,
    default=Nic,
)

def dump(obj, fp, skipkeys=Nieprawda, ensure_ascii=Prawda, check_circular=Prawda,
        allow_nan=Prawda, cls=Nic, indent=Nic, separators=Nic,
        default=Nic, sort_keys=Nieprawda, **kw):
    """Serialize ``obj`` jako a JSON formatted stream to ``fp`` (a
    ``.write()``-supporting file-like object).

    If ``skipkeys`` jest true then ``dict`` keys that are nie basic types
    (``str``, ``int``, ``float``, ``bool``, ``Nic``) will be skipped
    instead of raising a ``TypeError``.

    If ``ensure_ascii`` jest false, then the strings written to ``fp`` can
    contain non-ASCII characters jeżeli they appear w strings contained w
    ``obj``. Otherwise, all such characters are escaped w JSON strings.

    If ``check_circular`` jest false, then the circular reference check
    dla container types will be skipped oraz a circular reference will
    result w an ``OverflowError`` (or worse).

    If ``allow_nan`` jest false, then it will be a ``ValueError`` to
    serialize out of range ``float`` values (``nan``, ``inf``, ``-inf``)
    w strict compliance of the JSON specification, instead of using the
    JavaScript equivalents (``NaN``, ``Infinity``, ``-Infinity``).

    If ``indent`` jest a non-negative integer, then JSON array elements oraz
    object members will be pretty-printed przy that indent level. An indent
    level of 0 will only insert newlines. ``Nic`` jest the most compact
    representation.

    If specified, ``separators`` should be an ``(item_separator, key_separator)``
    tuple.  The default jest ``(', ', ': ')`` jeżeli *indent* jest ``Nic`` oraz
    ``(',', ': ')`` otherwise.  To get the most compact JSON representation,
    you should specify ``(',', ':')`` to eliminate whitespace.

    ``default(obj)`` jest a function that should zwróć a serializable version
    of obj albo podnieś TypeError. The default simply podnieśs TypeError.

    If *sort_keys* jest ``Prawda`` (default: ``Nieprawda``), then the output of
    dictionaries will be sorted by key.

    To use a custom ``JSONEncoder`` subclass (e.g. one that overrides the
    ``.default()`` method to serialize additional types), specify it with
    the ``cls`` kwarg; otherwise ``JSONEncoder`` jest used.

    """
    # cached encoder
    jeżeli (nie skipkeys oraz ensure_ascii oraz
        check_circular oraz allow_nan oraz
        cls jest Nic oraz indent jest Nic oraz separators jest Nic oraz
        default jest Nic oraz nie sort_keys oraz nie kw):
        iterable = _default_encoder.iterencode(obj)
    inaczej:
        jeżeli cls jest Nic:
            cls = JSONEncoder
        iterable = cls(skipkeys=skipkeys, ensure_ascii=ensure_ascii,
            check_circular=check_circular, allow_nan=allow_nan, indent=indent,
            separators=separators,
            default=default, sort_keys=sort_keys, **kw).iterencode(obj)
    # could accelerate przy writelines w some versions of Python, at
    # a debuggability cost
    dla chunk w iterable:
        fp.write(chunk)


def dumps(obj, skipkeys=Nieprawda, ensure_ascii=Prawda, check_circular=Prawda,
        allow_nan=Prawda, cls=Nic, indent=Nic, separators=Nic,
        default=Nic, sort_keys=Nieprawda, **kw):
    """Serialize ``obj`` to a JSON formatted ``str``.

    If ``skipkeys`` jest true then ``dict`` keys that are nie basic types
    (``str``, ``int``, ``float``, ``bool``, ``Nic``) will be skipped
    instead of raising a ``TypeError``.

    If ``ensure_ascii`` jest false, then the zwróć value can contain non-ASCII
    characters jeżeli they appear w strings contained w ``obj``. Otherwise, all
    such characters are escaped w JSON strings.

    If ``check_circular`` jest false, then the circular reference check
    dla container types will be skipped oraz a circular reference will
    result w an ``OverflowError`` (or worse).

    If ``allow_nan`` jest false, then it will be a ``ValueError`` to
    serialize out of range ``float`` values (``nan``, ``inf``, ``-inf``) w
    strict compliance of the JSON specification, instead of using the
    JavaScript equivalents (``NaN``, ``Infinity``, ``-Infinity``).

    If ``indent`` jest a non-negative integer, then JSON array elements oraz
    object members will be pretty-printed przy that indent level. An indent
    level of 0 will only insert newlines. ``Nic`` jest the most compact
    representation.

    If specified, ``separators`` should be an ``(item_separator, key_separator)``
    tuple.  The default jest ``(', ', ': ')`` jeżeli *indent* jest ``Nic`` oraz
    ``(',', ': ')`` otherwise.  To get the most compact JSON representation,
    you should specify ``(',', ':')`` to eliminate whitespace.

    ``default(obj)`` jest a function that should zwróć a serializable version
    of obj albo podnieś TypeError. The default simply podnieśs TypeError.

    If *sort_keys* jest ``Prawda`` (default: ``Nieprawda``), then the output of
    dictionaries will be sorted by key.

    To use a custom ``JSONEncoder`` subclass (e.g. one that overrides the
    ``.default()`` method to serialize additional types), specify it with
    the ``cls`` kwarg; otherwise ``JSONEncoder`` jest used.

    """
    # cached encoder
    jeżeli (nie skipkeys oraz ensure_ascii oraz
        check_circular oraz allow_nan oraz
        cls jest Nic oraz indent jest Nic oraz separators jest Nic oraz
        default jest Nic oraz nie sort_keys oraz nie kw):
        zwróć _default_encoder.encode(obj)
    jeżeli cls jest Nic:
        cls = JSONEncoder
    zwróć cls(
        skipkeys=skipkeys, ensure_ascii=ensure_ascii,
        check_circular=check_circular, allow_nan=allow_nan, indent=indent,
        separators=separators, default=default, sort_keys=sort_keys,
        **kw).encode(obj)


_default_decoder = JSONDecoder(object_hook=Nic, object_pairs_hook=Nic)


def load(fp, cls=Nic, object_hook=Nic, parse_float=Nic,
        parse_int=Nic, parse_constant=Nic, object_pairs_hook=Nic, **kw):
    """Deserialize ``fp`` (a ``.read()``-supporting file-like object containing
    a JSON document) to a Python object.

    ``object_hook`` jest an optional function that will be called przy the
    result of any object literal decode (a ``dict``). The zwróć value of
    ``object_hook`` will be used instead of the ``dict``. This feature
    can be used to implement custom decoders (e.g. JSON-RPC klasa hinting).

    ``object_pairs_hook`` jest an optional function that will be called przy the
    result of any object literal decoded przy an ordered list of pairs.  The
    zwróć value of ``object_pairs_hook`` will be used instead of the ``dict``.
    This feature can be used to implement custom decoders that rely on the
    order that the key oraz value pairs are decoded (dla example,
    collections.OrderedDict will remember the order of insertion). If
    ``object_hook`` jest also defined, the ``object_pairs_hook`` takes priority.

    To use a custom ``JSONDecoder`` subclass, specify it przy the ``cls``
    kwarg; otherwise ``JSONDecoder`` jest used.

    """
    zwróć loads(fp.read(),
        cls=cls, object_hook=object_hook,
        parse_float=parse_float, parse_int=parse_int,
        parse_constant=parse_constant, object_pairs_hook=object_pairs_hook, **kw)


def loads(s, encoding=Nic, cls=Nic, object_hook=Nic, parse_float=Nic,
        parse_int=Nic, parse_constant=Nic, object_pairs_hook=Nic, **kw):
    """Deserialize ``s`` (a ``str`` instance containing a JSON
    document) to a Python object.

    ``object_hook`` jest an optional function that will be called przy the
    result of any object literal decode (a ``dict``). The zwróć value of
    ``object_hook`` will be used instead of the ``dict``. This feature
    can be used to implement custom decoders (e.g. JSON-RPC klasa hinting).

    ``object_pairs_hook`` jest an optional function that will be called przy the
    result of any object literal decoded przy an ordered list of pairs.  The
    zwróć value of ``object_pairs_hook`` will be used instead of the ``dict``.
    This feature can be used to implement custom decoders that rely on the
    order that the key oraz value pairs are decoded (dla example,
    collections.OrderedDict will remember the order of insertion). If
    ``object_hook`` jest also defined, the ``object_pairs_hook`` takes priority.

    ``parse_float``, jeżeli specified, will be called przy the string
    of every JSON float to be decoded. By default this jest equivalent to
    float(num_str). This can be used to use another datatype albo parser
    dla JSON floats (e.g. decimal.Decimal).

    ``parse_int``, jeżeli specified, will be called przy the string
    of every JSON int to be decoded. By default this jest equivalent to
    int(num_str). This can be used to use another datatype albo parser
    dla JSON integers (e.g. float).

    ``parse_constant``, jeżeli specified, will be called przy one of the
    following strings: -Infinity, Infinity, NaN, null, true, false.
    This can be used to podnieś an exception jeżeli invalid JSON numbers
    are encountered.

    To use a custom ``JSONDecoder`` subclass, specify it przy the ``cls``
    kwarg; otherwise ``JSONDecoder`` jest used.

    The ``encoding`` argument jest ignored oraz deprecated.

    """
    jeżeli nie isinstance(s, str):
        podnieś TypeError('the JSON object must be str, nie {!r}'.format(
                            s.__class__.__name__))
    jeżeli s.startswith(u'\ufeff'):
        podnieś JSONDecodeError("Unexpected UTF-8 BOM (decode using utf-8-sig)",
                              s, 0)
    jeżeli (cls jest Nic oraz object_hook jest Nic oraz
            parse_int jest Nic oraz parse_float jest Nic oraz
            parse_constant jest Nic oraz object_pairs_hook jest Nic oraz nie kw):
        zwróć _default_decoder.decode(s)
    jeżeli cls jest Nic:
        cls = JSONDecoder
    jeżeli object_hook jest nie Nic:
        kw['object_hook'] = object_hook
    jeżeli object_pairs_hook jest nie Nic:
        kw['object_pairs_hook'] = object_pairs_hook
    jeżeli parse_float jest nie Nic:
        kw['parse_float'] = parse_float
    jeżeli parse_int jest nie Nic:
        kw['parse_int'] = parse_int
    jeżeli parse_constant jest nie Nic:
        kw['parse_constant'] = parse_constant
    zwróć cls(**kw).decode(s)
