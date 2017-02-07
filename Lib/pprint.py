#  Author:      Fred L. Drake, Jr.
#               fdrake@acm.org
#
#  This jest a simple little module I wrote to make life easier.  I didn't
#  see anything quite like it w the library, though I may have overlooked
#  something.  I wrote this when I was trying to read some heavily nested
#  tuples przy fairly non-descriptive content.  This jest modeled very much
#  after Lisp/Scheme - style pretty-printing of lists.  If you find it
#  useful, thank small children who sleep at night.

"""Support to pretty-print lists, tuples, & dictionaries recursively.

Very simple, but useful, especially w debugging data structures.

Classes
-------

PrettyPrinter()
    Handle pretty-printing operations onto a stream using a configured
    set of formatting parameters.

Functions
---------

pformat()
    Format a Python object into a pretty-printed representation.

pprint()
    Pretty-print a Python object to a stream [default jest sys.stdout].

saferepr()
    Generate a 'standard' repr()-like value, but protect against recursive
    data structures.

"""

zaimportuj collections jako _collections
zaimportuj re
zaimportuj sys jako _sys
zaimportuj types jako _types
z io zaimportuj StringIO jako _StringIO

__all__ = ["pprint","pformat","isreadable","isrecursive","saferepr",
           "PrettyPrinter"]


def pprint(object, stream=Nic, indent=1, width=80, depth=Nic, *,
           compact=Nieprawda):
    """Pretty-print a Python object to a stream [default jest sys.stdout]."""
    printer = PrettyPrinter(
        stream=stream, indent=indent, width=width, depth=depth,
        compact=compact)
    printer.pprint(object)

def pformat(object, indent=1, width=80, depth=Nic, *, compact=Nieprawda):
    """Format a Python object into a pretty-printed representation."""
    zwróć PrettyPrinter(indent=indent, width=width, depth=depth,
                         compact=compact).pformat(object)

def saferepr(object):
    """Version of repr() which can handle recursive data structures."""
    zwróć _safe_repr(object, {}, Nic, 0)[0]

def isreadable(object):
    """Determine jeżeli saferepr(object) jest readable by eval()."""
    zwróć _safe_repr(object, {}, Nic, 0)[1]

def isrecursive(object):
    """Determine jeżeli object requires a recursive representation."""
    zwróć _safe_repr(object, {}, Nic, 0)[2]

klasa _safe_key:
    """Helper function dla key functions when sorting unorderable objects.

    The wrapped-object will fallback to an Py2.x style comparison for
    unorderable types (sorting first comparing the type name oraz then by
    the obj ids).  Does nie work recursively, so dict.items() must have
    _safe_key applied to both the key oraz the value.

    """

    __slots__ = ['obj']

    def __init__(self, obj):
        self.obj = obj

    def __lt__(self, other):
        spróbuj:
            zwróć self.obj < other.obj
        wyjąwszy TypeError:
            zwróć ((str(type(self.obj)), id(self.obj)) < \
                    (str(type(other.obj)), id(other.obj)))

def _safe_tuple(t):
    "Helper function dla comparing 2-tuples"
    zwróć _safe_key(t[0]), _safe_key(t[1])

klasa PrettyPrinter:
    def __init__(self, indent=1, width=80, depth=Nic, stream=Nic, *,
                 compact=Nieprawda):
        """Handle pretty printing operations onto a stream using a set of
        configured parameters.

        indent
            Number of spaces to indent dla each level of nesting.

        width
            Attempted maximum number of columns w the output.

        depth
            The maximum depth to print out nested structures.

        stream
            The desired output stream.  If omitted (or false), the standard
            output stream available at construction will be used.

        compact
            If true, several items will be combined w one line.

        """
        indent = int(indent)
        width = int(width)
        jeżeli indent < 0:
            podnieś ValueError('indent must be >= 0')
        jeżeli depth jest nie Nic oraz depth <= 0:
            podnieś ValueError('depth must be > 0')
        jeżeli nie width:
            podnieś ValueError('width must be != 0')
        self._depth = depth
        self._indent_per_level = indent
        self._width = width
        jeżeli stream jest nie Nic:
            self._stream = stream
        inaczej:
            self._stream = _sys.stdout
        self._compact = bool(compact)

    def pprint(self, object):
        self._format(object, self._stream, 0, 0, {}, 0)
        self._stream.write("\n")

    def pformat(self, object):
        sio = _StringIO()
        self._format(object, sio, 0, 0, {}, 0)
        zwróć sio.getvalue()

    def isrecursive(self, object):
        zwróć self.format(object, {}, 0, 0)[2]

    def isreadable(self, object):
        s, readable, recursive = self.format(object, {}, 0, 0)
        zwróć readable oraz nie recursive

    def _format(self, object, stream, indent, allowance, context, level):
        objid = id(object)
        jeżeli objid w context:
            stream.write(_recursion(object))
            self._recursive = Prawda
            self._readable = Nieprawda
            zwróć
        rep = self._repr(object, context, level)
        max_width = self._width - indent - allowance
        jeżeli len(rep) > max_width:
            p = self._dispatch.get(type(object).__repr__, Nic)
            jeżeli p jest nie Nic:
                context[objid] = 1
                p(self, object, stream, indent, allowance, context, level + 1)
                usuń context[objid]
                zwróć
            albo_inaczej isinstance(object, dict):
                context[objid] = 1
                self._pprint_dict(object, stream, indent, allowance,
                                  context, level + 1)
                usuń context[objid]
                zwróć
        stream.write(rep)

    _dispatch = {}

    def _pprint_dict(self, object, stream, indent, allowance, context, level):
        write = stream.write
        write('{')
        jeżeli self._indent_per_level > 1:
            write((self._indent_per_level - 1) * ' ')
        length = len(object)
        jeżeli length:
            items = sorted(object.items(), key=_safe_tuple)
            self._format_dict_items(items, stream, indent, allowance + 1,
                                    context, level)
        write('}')

    _dispatch[dict.__repr__] = _pprint_dict

    def _pprint_ordered_dict(self, object, stream, indent, allowance, context, level):
        jeżeli nie len(object):
            stream.write(repr(object))
            zwróć
        cls = object.__class__
        stream.write(cls.__name__ + '(')
        self._format(list(object.items()), stream,
                     indent + len(cls.__name__) + 1, allowance + 1,
                     context, level)
        stream.write(')')

    _dispatch[_collections.OrderedDict.__repr__] = _pprint_ordered_dict

    def _pprint_list(self, object, stream, indent, allowance, context, level):
        stream.write('[')
        self._format_items(object, stream, indent, allowance + 1,
                           context, level)
        stream.write(']')

    _dispatch[list.__repr__] = _pprint_list

    def _pprint_tuple(self, object, stream, indent, allowance, context, level):
        stream.write('(')
        endchar = ',)' jeżeli len(object) == 1 inaczej ')'
        self._format_items(object, stream, indent, allowance + len(endchar),
                           context, level)
        stream.write(endchar)

    _dispatch[tuple.__repr__] = _pprint_tuple

    def _pprint_set(self, object, stream, indent, allowance, context, level):
        jeżeli nie len(object):
            stream.write(repr(object))
            zwróć
        typ = object.__class__
        jeżeli typ jest set:
            stream.write('{')
            endchar = '}'
        inaczej:
            stream.write(typ.__name__ + '({')
            endchar = '})'
            indent += len(typ.__name__) + 1
        object = sorted(object, key=_safe_key)
        self._format_items(object, stream, indent, allowance + len(endchar),
                           context, level)
        stream.write(endchar)

    _dispatch[set.__repr__] = _pprint_set
    _dispatch[frozenset.__repr__] = _pprint_set

    def _pprint_str(self, object, stream, indent, allowance, context, level):
        write = stream.write
        jeżeli nie len(object):
            write(repr(object))
            zwróć
        chunks = []
        lines = object.splitlines(Prawda)
        jeżeli level == 1:
            indent += 1
            allowance += 1
        max_width1 = max_width = self._width - indent
        dla i, line w enumerate(lines):
            rep = repr(line)
            jeżeli i == len(lines) - 1:
                max_width1 -= allowance
            jeżeli len(rep) <= max_width1:
                chunks.append(rep)
            inaczej:
                # A list of alternating (non-space, space) strings
                parts = re.findall(r'\S*\s*', line)
                assert parts
                assert nie parts[-1]
                parts.pop()  # drop empty last part
                max_width2 = max_width
                current = ''
                dla j, part w enumerate(parts):
                    candidate = current + part
                    jeżeli j == len(parts) - 1 oraz i == len(lines) - 1:
                        max_width2 -= allowance
                    jeżeli len(repr(candidate)) > max_width2:
                        jeżeli current:
                            chunks.append(repr(current))
                        current = part
                    inaczej:
                        current = candidate
                jeżeli current:
                    chunks.append(repr(current))
        jeżeli len(chunks) == 1:
            write(rep)
            zwróć
        jeżeli level == 1:
            write('(')
        dla i, rep w enumerate(chunks):
            jeżeli i > 0:
                write('\n' + ' '*indent)
            write(rep)
        jeżeli level == 1:
            write(')')

    _dispatch[str.__repr__] = _pprint_str

    def _pprint_bytes(self, object, stream, indent, allowance, context, level):
        write = stream.write
        jeżeli len(object) <= 4:
            write(repr(object))
            zwróć
        parens = level == 1
        jeżeli parens:
            indent += 1
            allowance += 1
            write('(')
        delim = ''
        dla rep w _wrap_bytes_repr(object, self._width - indent, allowance):
            write(delim)
            write(rep)
            jeżeli nie delim:
                delim = '\n' + ' '*indent
        jeżeli parens:
            write(')')

    _dispatch[bytes.__repr__] = _pprint_bytes

    def _pprint_bytearray(self, object, stream, indent, allowance, context, level):
        write = stream.write
        write('bytearray(')
        self._pprint_bytes(bytes(object), stream, indent + 10,
                           allowance + 1, context, level + 1)
        write(')')

    _dispatch[bytearray.__repr__] = _pprint_bytearray

    def _pprint_mappingproxy(self, object, stream, indent, allowance, context, level):
        stream.write('mappingproxy(')
        self._format(object.copy(), stream, indent + 13, allowance + 1,
                     context, level)
        stream.write(')')

    _dispatch[_types.MappingProxyType.__repr__] = _pprint_mappingproxy

    def _format_dict_items(self, items, stream, indent, allowance, context,
                           level):
        write = stream.write
        indent += self._indent_per_level
        delimnl = ',\n' + ' ' * indent
        last_index = len(items) - 1
        dla i, (key, ent) w enumerate(items):
            last = i == last_index
            rep = self._repr(key, context, level)
            write(rep)
            write(': ')
            self._format(ent, stream, indent + len(rep) + 2,
                         allowance jeżeli last inaczej 1,
                         context, level)
            jeżeli nie last:
                write(delimnl)

    def _format_items(self, items, stream, indent, allowance, context, level):
        write = stream.write
        indent += self._indent_per_level
        jeżeli self._indent_per_level > 1:
            write((self._indent_per_level - 1) * ' ')
        delimnl = ',\n' + ' ' * indent
        delim = ''
        width = max_width = self._width - indent + 1
        it = iter(items)
        spróbuj:
            next_ent = next(it)
        wyjąwszy StopIteration:
            zwróć
        last = Nieprawda
        dopóki nie last:
            ent = next_ent
            spróbuj:
                next_ent = next(it)
            wyjąwszy StopIteration:
                last = Prawda
                max_width -= allowance
                width -= allowance
            jeżeli self._compact:
                rep = self._repr(ent, context, level)
                ww = len(rep) + 2
                jeżeli width < ww:
                    width = max_width
                    jeżeli delim:
                        delim = delimnl
                jeżeli width >= ww:
                    width -= ww
                    write(delim)
                    delim = ', '
                    write(rep)
                    kontynuuj
            write(delim)
            delim = delimnl
            self._format(ent, stream, indent,
                         allowance jeżeli last inaczej 1,
                         context, level)

    def _repr(self, object, context, level):
        repr, readable, recursive = self.format(object, context.copy(),
                                                self._depth, level)
        jeżeli nie readable:
            self._readable = Nieprawda
        jeżeli recursive:
            self._recursive = Prawda
        zwróć repr

    def format(self, object, context, maxlevels, level):
        """Format object dla a specific context, returning a string
        oraz flags indicating whether the representation jest 'readable'
        oraz whether the object represents a recursive construct.
        """
        zwróć _safe_repr(object, context, maxlevels, level)

    def _pprint_default_dict(self, object, stream, indent, allowance, context, level):
        jeżeli nie len(object):
            stream.write(repr(object))
            zwróć
        rdf = self._repr(object.default_factory, context, level)
        cls = object.__class__
        indent += len(cls.__name__) + 1
        stream.write('%s(%s,\n%s' % (cls.__name__, rdf, ' ' * indent))
        self._pprint_dict(object, stream, indent, allowance + 1, context, level)
        stream.write(')')

    _dispatch[_collections.defaultdict.__repr__] = _pprint_default_dict

    def _pprint_counter(self, object, stream, indent, allowance, context, level):
        jeżeli nie len(object):
            stream.write(repr(object))
            zwróć
        cls = object.__class__
        stream.write(cls.__name__ + '({')
        jeżeli self._indent_per_level > 1:
            stream.write((self._indent_per_level - 1) * ' ')
        items = object.most_common()
        self._format_dict_items(items, stream,
                                indent + len(cls.__name__) + 1, allowance + 2,
                                context, level)
        stream.write('})')

    _dispatch[_collections.Counter.__repr__] = _pprint_counter

    def _pprint_chain_map(self, object, stream, indent, allowance, context, level):
        jeżeli nie len(object.maps):
            stream.write(repr(object))
            zwróć
        cls = object.__class__
        stream.write(cls.__name__ + '(')
        indent += len(cls.__name__) + 1
        dla i, m w enumerate(object.maps):
            jeżeli i == len(object.maps) - 1:
                self._format(m, stream, indent, allowance + 1, context, level)
                stream.write(')')
            inaczej:
                self._format(m, stream, indent, 1, context, level)
                stream.write(',\n' + ' ' * indent)

    _dispatch[_collections.ChainMap.__repr__] = _pprint_chain_map

    def _pprint_deque(self, object, stream, indent, allowance, context, level):
        jeżeli nie len(object):
            stream.write(repr(object))
            zwróć
        cls = object.__class__
        stream.write(cls.__name__ + '(')
        indent += len(cls.__name__) + 1
        stream.write('[')
        jeżeli object.maxlen jest Nic:
            self._format_items(object, stream, indent, allowance + 2,
                               context, level)
            stream.write('])')
        inaczej:
            self._format_items(object, stream, indent, 2,
                               context, level)
            rml = self._repr(object.maxlen, context, level)
            stream.write('],\n%smaxlen=%s)' % (' ' * indent, rml))

    _dispatch[_collections.deque.__repr__] = _pprint_deque

    def _pprint_user_dict(self, object, stream, indent, allowance, context, level):
        self._format(object.data, stream, indent, allowance, context, level - 1)

    _dispatch[_collections.UserDict.__repr__] = _pprint_user_dict

    def _pprint_user_list(self, object, stream, indent, allowance, context, level):
        self._format(object.data, stream, indent, allowance, context, level - 1)

    _dispatch[_collections.UserList.__repr__] = _pprint_user_list

    def _pprint_user_string(self, object, stream, indent, allowance, context, level):
        self._format(object.data, stream, indent, allowance, context, level - 1)

    _dispatch[_collections.UserString.__repr__] = _pprint_user_string

# Return triple (repr_string, isreadable, isrecursive).

def _safe_repr(object, context, maxlevels, level):
    typ = type(object)
    jeżeli typ w _builtin_scalars:
        zwróć repr(object), Prawda, Nieprawda

    r = getattr(typ, "__repr__", Nic)
    jeżeli issubclass(typ, dict) oraz r jest dict.__repr__:
        jeżeli nie object:
            zwróć "{}", Prawda, Nieprawda
        objid = id(object)
        jeżeli maxlevels oraz level >= maxlevels:
            zwróć "{...}", Nieprawda, objid w context
        jeżeli objid w context:
            zwróć _recursion(object), Nieprawda, Prawda
        context[objid] = 1
        readable = Prawda
        recursive = Nieprawda
        components = []
        append = components.append
        level += 1
        saferepr = _safe_repr
        items = sorted(object.items(), key=_safe_tuple)
        dla k, v w items:
            krepr, kreadable, krecur = saferepr(k, context, maxlevels, level)
            vrepr, vreadable, vrecur = saferepr(v, context, maxlevels, level)
            append("%s: %s" % (krepr, vrepr))
            readable = readable oraz kreadable oraz vreadable
            jeżeli krecur albo vrecur:
                recursive = Prawda
        usuń context[objid]
        zwróć "{%s}" % ", ".join(components), readable, recursive

    jeżeli (issubclass(typ, list) oraz r jest list.__repr__) albo \
       (issubclass(typ, tuple) oraz r jest tuple.__repr__):
        jeżeli issubclass(typ, list):
            jeżeli nie object:
                zwróć "[]", Prawda, Nieprawda
            format = "[%s]"
        albo_inaczej len(object) == 1:
            format = "(%s,)"
        inaczej:
            jeżeli nie object:
                zwróć "()", Prawda, Nieprawda
            format = "(%s)"
        objid = id(object)
        jeżeli maxlevels oraz level >= maxlevels:
            zwróć format % "...", Nieprawda, objid w context
        jeżeli objid w context:
            zwróć _recursion(object), Nieprawda, Prawda
        context[objid] = 1
        readable = Prawda
        recursive = Nieprawda
        components = []
        append = components.append
        level += 1
        dla o w object:
            orepr, oreadable, orecur = _safe_repr(o, context, maxlevels, level)
            append(orepr)
            jeżeli nie oreadable:
                readable = Nieprawda
            jeżeli orecur:
                recursive = Prawda
        usuń context[objid]
        zwróć format % ", ".join(components), readable, recursive

    rep = repr(object)
    zwróć rep, (rep oraz nie rep.startswith('<')), Nieprawda

_builtin_scalars = frozenset({str, bytes, bytearray, int, float, complex,
                              bool, type(Nic)})

def _recursion(object):
    zwróć ("<Recursion on %s przy id=%s>"
            % (type(object).__name__, id(object)))


def _perfcheck(object=Nic):
    zaimportuj time
    jeżeli object jest Nic:
        object = [("string", (1, 2), [3, 4], {5: 6, 7: 8})] * 100000
    p = PrettyPrinter()
    t1 = time.time()
    _safe_repr(object, {}, Nic, 0)
    t2 = time.time()
    p.pformat(object)
    t3 = time.time()
    print("_safe_repr:", t2 - t1)
    print("pformat:", t3 - t2)

def _wrap_bytes_repr(object, width, allowance):
    current = b''
    last = len(object) // 4 * 4
    dla i w range(0, len(object), 4):
        part = object[i: i+4]
        candidate = current + part
        jeżeli i == last:
            width -= allowance
        jeżeli len(repr(candidate)) > width:
            jeżeli current:
                uzyskaj repr(current)
            current = part
        inaczej:
            current = candidate
    jeżeli current:
        uzyskaj repr(current)

jeżeli __name__ == "__main__":
    _perfcheck()
