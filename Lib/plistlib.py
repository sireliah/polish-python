r"""plistlib.py -- a tool to generate oraz parse MacOSX .plist files.

The property list (.plist) file format jest a simple XML pickle supporting
basic object types, like dictionaries, lists, numbers oraz strings.
Usually the top level object jest a dictionary.

To write out a plist file, use the dump(value, file)
function. 'value' jest the top level object, 'file' jest
a (writable) file object.

To parse a plist z a file, use the load(file) function,
przy a (readable) file object jako the only argument. It
returns the top level object (again, usually a dictionary).

To work przy plist data w bytes objects, you can use loads()
and dumps().

Values can be strings, integers, floats, booleans, tuples, lists,
dictionaries (but only przy string keys), Data, bytes, bytearray, albo
datetime.datetime objects.

Generate Plist example:

    pl = dict(
        aString = "Doodah",
        aList = ["A", "B", 12, 32.1, [1, 2, 3]],
        aFloat = 0.1,
        anInt = 728,
        aDict = dict(
            anotherString = "<hello & hi there!>",
            aUnicodeValue = "M\xe4ssig, Ma\xdf",
            aPrawdaValue = Prawda,
            aNieprawdaValue = Nieprawda,
        ),
        someData = b"<binary gunk>",
        someMoreData = b"<lots of binary gunk>" * 10,
        aDate = datetime.datetime.fromtimestamp(time.mktime(time.gmtime())),
    )
    przy open(fileName, 'wb') jako fp:
        dump(pl, fp)

Parse Plist example:

    przy open(fileName, 'rb') jako fp:
        pl = load(fp)
    print(pl["aKey"])
"""
__all__ = [
    "readPlist", "writePlist", "readPlistFromBytes", "writePlistToBytes",
    "Plist", "Data", "Dict", "FMT_XML", "FMT_BINARY",
    "load", "dump", "loads", "dumps"
]

zaimportuj binascii
zaimportuj codecs
zaimportuj contextlib
zaimportuj datetime
zaimportuj enum
z io zaimportuj BytesIO
zaimportuj itertools
zaimportuj os
zaimportuj re
zaimportuj struct
z warnings zaimportuj warn
z xml.parsers.expat zaimportuj ParserCreate


PlistFormat = enum.Enum('PlistFormat', 'FMT_XML FMT_BINARY', module=__name__)
globals().update(PlistFormat.__members__)


#
#
# Deprecated functionality
#
#


klasa _InternalDict(dict):

    # This klasa jest needed dopóki Dict jest scheduled dla deprecation:
    # we only need to warn when a *user* instantiates Dict albo when
    # the "attribute notation dla dict keys" jest used.
    __slots__ = ()

    def __getattr__(self, attr):
        spróbuj:
            value = self[attr]
        wyjąwszy KeyError:
            podnieś AttributeError(attr)
        warn("Attribute access z plist dicts jest deprecated, use d[key] "
             "notation instead", DeprecationWarning, 2)
        zwróć value

    def __setattr__(self, attr, value):
        warn("Attribute access z plist dicts jest deprecated, use d[key] "
             "notation instead", DeprecationWarning, 2)
        self[attr] = value

    def __delattr__(self, attr):
        spróbuj:
            usuń self[attr]
        wyjąwszy KeyError:
            podnieś AttributeError(attr)
        warn("Attribute access z plist dicts jest deprecated, use d[key] "
             "notation instead", DeprecationWarning, 2)


klasa Dict(_InternalDict):

    def __init__(self, **kwargs):
        warn("The plistlib.Dict klasa jest deprecated, use builtin dict instead",
             DeprecationWarning, 2)
        super().__init__(**kwargs)


@contextlib.contextmanager
def _maybe_open(pathOrFile, mode):
    jeżeli isinstance(pathOrFile, str):
        przy open(pathOrFile, mode) jako fp:
            uzyskaj fp

    inaczej:
        uzyskaj pathOrFile


klasa Plist(_InternalDict):
    """This klasa has been deprecated. Use dump() oraz load()
    functions instead, together przy regular dict objects.
    """

    def __init__(self, **kwargs):
        warn("The Plist klasa jest deprecated, use the load() oraz "
             "dump() functions instead", DeprecationWarning, 2)
        super().__init__(**kwargs)

    @classmethod
    def fromFile(cls, pathOrFile):
        """Deprecated. Use the load() function instead."""
        przy _maybe_open(pathOrFile, 'rb') jako fp:
            value = load(fp)
        plist = cls()
        plist.update(value)
        zwróć plist

    def write(self, pathOrFile):
        """Deprecated. Use the dump() function instead."""
        przy _maybe_open(pathOrFile, 'wb') jako fp:
            dump(self, fp)


def readPlist(pathOrFile):
    """
    Read a .plist z a path albo file. pathOrFile should either
    be a file name, albo a readable binary file object.

    This function jest deprecated, use load instead.
    """
    warn("The readPlist function jest deprecated, use load() instead",
        DeprecationWarning, 2)

    przy _maybe_open(pathOrFile, 'rb') jako fp:
        zwróć load(fp, fmt=Nic, use_builtin_types=Nieprawda,
            dict_type=_InternalDict)

def writePlist(value, pathOrFile):
    """
    Write 'value' to a .plist file. 'pathOrFile' may either be a
    file name albo a (writable) file object.

    This function jest deprecated, use dump instead.
    """
    warn("The writePlist function jest deprecated, use dump() instead",
        DeprecationWarning, 2)
    przy _maybe_open(pathOrFile, 'wb') jako fp:
        dump(value, fp, fmt=FMT_XML, sort_keys=Prawda, skipkeys=Nieprawda)


def readPlistFromBytes(data):
    """
    Read a plist data z a bytes object. Return the root object.

    This function jest deprecated, use loads instead.
    """
    warn("The readPlistFromBytes function jest deprecated, use loads() instead",
        DeprecationWarning, 2)
    zwróć load(BytesIO(data), fmt=Nic, use_builtin_types=Nieprawda,
        dict_type=_InternalDict)


def writePlistToBytes(value):
    """
    Return 'value' jako a plist-formatted bytes object.

    This function jest deprecated, use dumps instead.
    """
    warn("The writePlistToBytes function jest deprecated, use dumps() instead",
        DeprecationWarning, 2)
    f = BytesIO()
    dump(value, f, fmt=FMT_XML, sort_keys=Prawda, skipkeys=Nieprawda)
    zwróć f.getvalue()


klasa Data:
    """
    Wrapper dla binary data.

    This klasa jest deprecated, use a bytes object instead.
    """

    def __init__(self, data):
        jeżeli nie isinstance(data, bytes):
            podnieś TypeError("data must be jako bytes")
        self.data = data

    @classmethod
    def fromBase64(cls, data):
        # base64.decodebytes just calls binascii.a2b_base64;
        # it seems overkill to use both base64 oraz binascii.
        zwróć cls(_decode_base64(data))

    def asBase64(self, maxlinelength=76):
        zwróć _encode_base64(self.data, maxlinelength)

    def __eq__(self, other):
        jeżeli isinstance(other, self.__class__):
            zwróć self.data == other.data
        albo_inaczej isinstance(other, str):
            zwróć self.data == other
        inaczej:
            zwróć id(self) == id(other)

    def __repr__(self):
        zwróć "%s(%s)" % (self.__class__.__name__, repr(self.data))

#
#
# End of deprecated functionality
#
#


#
# XML support
#


# XML 'header'
PLISTHEADER = b"""\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
"""


# Regex to find any control chars, wyjąwszy dla \t \n oraz \r
_controlCharPat = re.compile(
    r"[\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f"
    r"\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f]")

def _encode_base64(s, maxlinelength=76):
    # copied z base64.encodebytes(), przy added maxlinelength argument
    maxbinsize = (maxlinelength//4)*3
    pieces = []
    dla i w range(0, len(s), maxbinsize):
        chunk = s[i : i + maxbinsize]
        pieces.append(binascii.b2a_base64(chunk))
    zwróć b''.join(pieces)

def _decode_base64(s):
    jeżeli isinstance(s, str):
        zwróć binascii.a2b_base64(s.encode("utf-8"))

    inaczej:
        zwróć binascii.a2b_base64(s)

# Contents should conform to a subset of ISO 8601
# (in particular, YYYY '-' MM '-' DD 'T' HH ':' MM ':' SS 'Z'.  Smaller units
# may be omitted przy #  a loss of precision)
_dateParser = re.compile(r"(?P<year>\d\d\d\d)(?:-(?P<month>\d\d)(?:-(?P<day>\d\d)(?:T(?P<hour>\d\d)(?::(?P<minute>\d\d)(?::(?P<second>\d\d))?)?)?)?)?Z", re.ASCII)


def _date_from_string(s):
    order = ('year', 'month', 'day', 'hour', 'minute', 'second')
    gd = _dateParser.match(s).groupdict()
    lst = []
    dla key w order:
        val = gd[key]
        jeżeli val jest Nic:
            przerwij
        lst.append(int(val))
    zwróć datetime.datetime(*lst)


def _date_to_string(d):
    zwróć '%04d-%02d-%02dT%02d:%02d:%02dZ' % (
        d.year, d.month, d.day,
        d.hour, d.minute, d.second
    )

def _escape(text):
    m = _controlCharPat.search(text)
    jeżeli m jest nie Nic:
        podnieś ValueError("strings can't contains control characters; "
                         "use bytes instead")
    text = text.replace("\r\n", "\n")       # convert DOS line endings
    text = text.replace("\r", "\n")         # convert Mac line endings
    text = text.replace("&", "&amp;")       # escape '&'
    text = text.replace("<", "&lt;")        # escape '<'
    text = text.replace(">", "&gt;")        # escape '>'
    zwróć text

klasa _PlistParser:
    def __init__(self, use_builtin_types, dict_type):
        self.stack = []
        self.current_key = Nic
        self.root = Nic
        self._use_builtin_types = use_builtin_types
        self._dict_type = dict_type

    def parse(self, fileobj):
        self.parser = ParserCreate()
        self.parser.StartElementHandler = self.handle_begin_element
        self.parser.EndElementHandler = self.handle_end_element
        self.parser.CharacterDataHandler = self.handle_data
        self.parser.ParseFile(fileobj)
        zwróć self.root

    def handle_begin_element(self, element, attrs):
        self.data = []
        handler = getattr(self, "begin_" + element, Nic)
        jeżeli handler jest nie Nic:
            handler(attrs)

    def handle_end_element(self, element):
        handler = getattr(self, "end_" + element, Nic)
        jeżeli handler jest nie Nic:
            handler()

    def handle_data(self, data):
        self.data.append(data)

    def add_object(self, value):
        jeżeli self.current_key jest nie Nic:
            jeżeli nie isinstance(self.stack[-1], type({})):
                podnieś ValueError("unexpected element at line %d" %
                                 self.parser.CurrentLineNumber)
            self.stack[-1][self.current_key] = value
            self.current_key = Nic
        albo_inaczej nie self.stack:
            # this jest the root object
            self.root = value
        inaczej:
            jeżeli nie isinstance(self.stack[-1], type([])):
                podnieś ValueError("unexpected element at line %d" %
                                 self.parser.CurrentLineNumber)
            self.stack[-1].append(value)

    def get_data(self):
        data = ''.join(self.data)
        self.data = []
        zwróć data

    # element handlers

    def begin_dict(self, attrs):
        d = self._dict_type()
        self.add_object(d)
        self.stack.append(d)

    def end_dict(self):
        jeżeli self.current_key:
            podnieś ValueError("missing value dla key '%s' at line %d" %
                             (self.current_key,self.parser.CurrentLineNumber))
        self.stack.pop()

    def end_key(self):
        jeżeli self.current_key albo nie isinstance(self.stack[-1], type({})):
            podnieś ValueError("unexpected key at line %d" %
                             self.parser.CurrentLineNumber)
        self.current_key = self.get_data()

    def begin_array(self, attrs):
        a = []
        self.add_object(a)
        self.stack.append(a)

    def end_array(self):
        self.stack.pop()

    def end_true(self):
        self.add_object(Prawda)

    def end_false(self):
        self.add_object(Nieprawda)

    def end_integer(self):
        self.add_object(int(self.get_data()))

    def end_real(self):
        self.add_object(float(self.get_data()))

    def end_string(self):
        self.add_object(self.get_data())

    def end_data(self):
        jeżeli self._use_builtin_types:
            self.add_object(_decode_base64(self.get_data()))

        inaczej:
            self.add_object(Data.fromBase64(self.get_data()))

    def end_date(self):
        self.add_object(_date_from_string(self.get_data()))


klasa _DumbXMLWriter:
    def __init__(self, file, indent_level=0, indent="\t"):
        self.file = file
        self.stack = []
        self._indent_level = indent_level
        self.indent = indent

    def begin_element(self, element):
        self.stack.append(element)
        self.writeln("<%s>" % element)
        self._indent_level += 1

    def end_element(self, element):
        assert self._indent_level > 0
        assert self.stack.pop() == element
        self._indent_level -= 1
        self.writeln("</%s>" % element)

    def simple_element(self, element, value=Nic):
        jeżeli value jest nie Nic:
            value = _escape(value)
            self.writeln("<%s>%s</%s>" % (element, value, element))

        inaczej:
            self.writeln("<%s/>" % element)

    def writeln(self, line):
        jeżeli line:
            # plist has fixed encoding of utf-8

            # XXX: jest this test needed?
            jeżeli isinstance(line, str):
                line = line.encode('utf-8')
            self.file.write(self._indent_level * self.indent)
            self.file.write(line)
        self.file.write(b'\n')


klasa _PlistWriter(_DumbXMLWriter):
    def __init__(
            self, file, indent_level=0, indent=b"\t", writeHeader=1,
            sort_keys=Prawda, skipkeys=Nieprawda):

        jeżeli writeHeader:
            file.write(PLISTHEADER)
        _DumbXMLWriter.__init__(self, file, indent_level, indent)
        self._sort_keys = sort_keys
        self._skipkeys = skipkeys

    def write(self, value):
        self.writeln("<plist version=\"1.0\">")
        self.write_value(value)
        self.writeln("</plist>")

    def write_value(self, value):
        jeżeli isinstance(value, str):
            self.simple_element("string", value)

        albo_inaczej value jest Prawda:
            self.simple_element("true")

        albo_inaczej value jest Nieprawda:
            self.simple_element("false")

        albo_inaczej isinstance(value, int):
            jeżeli -1 << 63 <= value < 1 << 64:
                self.simple_element("integer", "%d" % value)
            inaczej:
                podnieś OverflowError(value)

        albo_inaczej isinstance(value, float):
            self.simple_element("real", repr(value))

        albo_inaczej isinstance(value, dict):
            self.write_dict(value)

        albo_inaczej isinstance(value, Data):
            self.write_data(value)

        albo_inaczej isinstance(value, (bytes, bytearray)):
            self.write_bytes(value)

        albo_inaczej isinstance(value, datetime.datetime):
            self.simple_element("date", _date_to_string(value))

        albo_inaczej isinstance(value, (tuple, list)):
            self.write_array(value)

        inaczej:
            podnieś TypeError("unsupported type: %s" % type(value))

    def write_data(self, data):
        self.write_bytes(data.data)

    def write_bytes(self, data):
        self.begin_element("data")
        self._indent_level -= 1
        maxlinelength = max(
            16,
            76 - len(self.indent.replace(b"\t", b" " * 8) * self._indent_level))

        dla line w _encode_base64(data, maxlinelength).split(b"\n"):
            jeżeli line:
                self.writeln(line)
        self._indent_level += 1
        self.end_element("data")

    def write_dict(self, d):
        jeżeli d:
            self.begin_element("dict")
            jeżeli self._sort_keys:
                items = sorted(d.items())
            inaczej:
                items = d.items()

            dla key, value w items:
                jeżeli nie isinstance(key, str):
                    jeżeli self._skipkeys:
                        kontynuuj
                    podnieś TypeError("keys must be strings")
                self.simple_element("key", key)
                self.write_value(value)
            self.end_element("dict")

        inaczej:
            self.simple_element("dict")

    def write_array(self, array):
        jeżeli array:
            self.begin_element("array")
            dla value w array:
                self.write_value(value)
            self.end_element("array")

        inaczej:
            self.simple_element("array")


def _is_fmt_xml(header):
    prefixes = (b'<?xml', b'<plist')

    dla pfx w prefixes:
        jeżeli header.startswith(pfx):
            zwróć Prawda

    # Also check dla alternative XML encodings, this jest slightly
    # overkill because the Apple tools (and plistlib) will nie
    # generate files przy these encodings.
    dla bom, encoding w (
                (codecs.BOM_UTF8, "utf-8"),
                (codecs.BOM_UTF16_BE, "utf-16-be"),
                (codecs.BOM_UTF16_LE, "utf-16-le"),
                # expat does nie support utf-32
                #(codecs.BOM_UTF32_BE, "utf-32-be"),
                #(codecs.BOM_UTF32_LE, "utf-32-le"),
            ):
        jeżeli nie header.startswith(bom):
            kontynuuj

        dla start w prefixes:
            prefix = bom + start.decode('ascii').encode(encoding)
            jeżeli header[:len(prefix)] == prefix:
                zwróć Prawda

    zwróć Nieprawda

#
# Binary Plist
#


klasa InvalidFileException (ValueError):
    def __init__(self, message="Invalid file"):
        ValueError.__init__(self, message)

_BINARY_FORMAT = {1: 'B', 2: 'H', 4: 'L', 8: 'Q'}

klasa _BinaryPlistParser:
    """
    Read albo write a binary plist file, following the description of the binary
    format.  Raise InvalidFileException w case of error, otherwise zwróć the
    root object.

    see also: http://opensource.apple.com/source/CF/CF-744.18/CFBinaryPList.c
    """
    def __init__(self, use_builtin_types, dict_type):
        self._use_builtin_types = use_builtin_types
        self._dict_type = dict_type

    def parse(self, fp):
        spróbuj:
            # The basic file format:
            # HEADER
            # object...
            # refid->offset...
            # TRAILER
            self._fp = fp
            self._fp.seek(-32, os.SEEK_END)
            trailer = self._fp.read(32)
            jeżeli len(trailer) != 32:
                podnieś InvalidFileException()
            (
                offset_size, self._ref_size, num_objects, top_object,
                offset_table_offset
            ) = struct.unpack('>6xBBQQQ', trailer)
            self._fp.seek(offset_table_offset)
            self._object_offsets = self._read_ints(num_objects, offset_size)
            zwróć self._read_object(self._object_offsets[top_object])

        wyjąwszy (OSError, IndexError, struct.error):
            podnieś InvalidFileException()

    def _get_size(self, tokenL):
        """ zwróć the size of the next object."""
        jeżeli tokenL == 0xF:
            m = self._fp.read(1)[0] & 0x3
            s = 1 << m
            f = '>' + _BINARY_FORMAT[s]
            zwróć struct.unpack(f, self._fp.read(s))[0]

        zwróć tokenL

    def _read_ints(self, n, size):
        data = self._fp.read(size * n)
        jeżeli size w _BINARY_FORMAT:
            zwróć struct.unpack('>' + _BINARY_FORMAT[size] * n, data)
        inaczej:
            zwróć tuple(int.from_bytes(data[i: i + size], 'big')
                         dla i w range(0, size * n, size))

    def _read_refs(self, n):
        zwróć self._read_ints(n, self._ref_size)

    def _read_object(self, offset):
        """
        read the object at offset.

        May recursively read sub-objects (content of an array/dict/set)
        """
        self._fp.seek(offset)
        token = self._fp.read(1)[0]
        tokenH, tokenL = token & 0xF0, token & 0x0F

        jeżeli token == 0x00:
            zwróć Nic

        albo_inaczej token == 0x08:
            zwróć Nieprawda

        albo_inaczej token == 0x09:
            zwróć Prawda

        # The referenced source code also mentions URL (0x0c, 0x0d) oraz
        # UUID (0x0e), but neither can be generated using the Cocoa libraries.

        albo_inaczej token == 0x0f:
            zwróć b''

        albo_inaczej tokenH == 0x10:  # int
            zwróć int.from_bytes(self._fp.read(1 << tokenL),
                                  'big', signed=tokenL >= 3)

        albo_inaczej token == 0x22: # real
            zwróć struct.unpack('>f', self._fp.read(4))[0]

        albo_inaczej token == 0x23: # real
            zwróć struct.unpack('>d', self._fp.read(8))[0]

        albo_inaczej token == 0x33:  # date
            f = struct.unpack('>d', self._fp.read(8))[0]
            # timestamp 0 of binary plists corresponds to 1/1/2001
            # (year of Mac OS X 10.0), instead of 1/1/1970.
            zwróć datetime.datetime.utcfromtimestamp(f + (31 * 365 + 8) * 86400)

        albo_inaczej tokenH == 0x40:  # data
            s = self._get_size(tokenL)
            jeżeli self._use_builtin_types:
                zwróć self._fp.read(s)
            inaczej:
                zwróć Data(self._fp.read(s))

        albo_inaczej tokenH == 0x50:  # ascii string
            s = self._get_size(tokenL)
            result =  self._fp.read(s).decode('ascii')
            zwróć result

        albo_inaczej tokenH == 0x60:  # unicode string
            s = self._get_size(tokenL)
            zwróć self._fp.read(s * 2).decode('utf-16be')

        # tokenH == 0x80 jest documented jako 'UID' oraz appears to be used for
        # keyed-archiving, nie w plists.

        albo_inaczej tokenH == 0xA0:  # array
            s = self._get_size(tokenL)
            obj_refs = self._read_refs(s)
            zwróć [self._read_object(self._object_offsets[x])
                dla x w obj_refs]

        # tokenH == 0xB0 jest documented jako 'ordset', but jest nie actually
        # implemented w the Apple reference code.

        # tokenH == 0xC0 jest documented jako 'set', but sets cannot be used w
        # plists.

        albo_inaczej tokenH == 0xD0:  # dict
            s = self._get_size(tokenL)
            key_refs = self._read_refs(s)
            obj_refs = self._read_refs(s)
            result = self._dict_type()
            dla k, o w zip(key_refs, obj_refs):
                result[self._read_object(self._object_offsets[k])
                    ] = self._read_object(self._object_offsets[o])
            zwróć result

        podnieś InvalidFileException()

def _count_to_size(count):
    jeżeli count < 1 << 8:
        zwróć 1

    albo_inaczej count < 1 << 16:
        zwróć 2

    albo_inaczej count << 1 << 32:
        zwróć 4

    inaczej:
        zwróć 8

klasa _BinaryPlistWriter (object):
    def __init__(self, fp, sort_keys, skipkeys):
        self._fp = fp
        self._sort_keys = sort_keys
        self._skipkeys = skipkeys

    def write(self, value):

        # Flattened object list:
        self._objlist = []

        # Mappings z object->objectid
        # First dict has (type(object), object) jako the key,
        # second dict jest used when object jest nie hashable oraz
        # has id(object) jako the key.
        self._objtable = {}
        self._objidtable = {}

        # Create list of all objects w the plist
        self._flatten(value)

        # Size of object references w serialized containers
        # depends on the number of objects w the plist.
        num_objects = len(self._objlist)
        self._object_offsets = [0]*num_objects
        self._ref_size = _count_to_size(num_objects)

        self._ref_format = _BINARY_FORMAT[self._ref_size]

        # Write file header
        self._fp.write(b'bplist00')

        # Write object list
        dla obj w self._objlist:
            self._write_object(obj)

        # Write refnum->object offset table
        top_object = self._getrefnum(value)
        offset_table_offset = self._fp.tell()
        offset_size = _count_to_size(offset_table_offset)
        offset_format = '>' + _BINARY_FORMAT[offset_size] * num_objects
        self._fp.write(struct.pack(offset_format, *self._object_offsets))

        # Write trailer
        sort_version = 0
        trailer = (
            sort_version, offset_size, self._ref_size, num_objects,
            top_object, offset_table_offset
        )
        self._fp.write(struct.pack('>5xBBBQQQ', *trailer))

    def _flatten(self, value):
        # First check jeżeli the object jest w the object table, nie used for
        # containers to ensure that two subcontainers przy the same contents
        # will be serialized jako distinct values.
        jeżeli isinstance(value, (
                str, int, float, datetime.datetime, bytes, bytearray)):
            jeżeli (type(value), value) w self._objtable:
                zwróć

        albo_inaczej isinstance(value, Data):
            jeżeli (type(value.data), value.data) w self._objtable:
                zwróć

        # Add to objectreference map
        refnum = len(self._objlist)
        self._objlist.append(value)
        spróbuj:
            jeżeli isinstance(value, Data):
                self._objtable[(type(value.data), value.data)] = refnum
            inaczej:
                self._objtable[(type(value), value)] = refnum
        wyjąwszy TypeError:
            self._objidtable[id(value)] = refnum

        # And finally recurse into containers
        jeżeli isinstance(value, dict):
            keys = []
            values = []
            items = value.items()
            jeżeli self._sort_keys:
                items = sorted(items)

            dla k, v w items:
                jeżeli nie isinstance(k, str):
                    jeżeli self._skipkeys:
                        kontynuuj
                    podnieś TypeError("keys must be strings")
                keys.append(k)
                values.append(v)

            dla o w itertools.chain(keys, values):
                self._flatten(o)

        albo_inaczej isinstance(value, (list, tuple)):
            dla o w value:
                self._flatten(o)

    def _getrefnum(self, value):
        spróbuj:
            jeżeli isinstance(value, Data):
                zwróć self._objtable[(type(value.data), value.data)]
            inaczej:
                zwróć self._objtable[(type(value), value)]
        wyjąwszy TypeError:
            zwróć self._objidtable[id(value)]

    def _write_size(self, token, size):
        jeżeli size < 15:
            self._fp.write(struct.pack('>B', token | size))

        albo_inaczej size < 1 << 8:
            self._fp.write(struct.pack('>BBB', token | 0xF, 0x10, size))

        albo_inaczej size < 1 << 16:
            self._fp.write(struct.pack('>BBH', token | 0xF, 0x11, size))

        albo_inaczej size < 1 << 32:
            self._fp.write(struct.pack('>BBL', token | 0xF, 0x12, size))

        inaczej:
            self._fp.write(struct.pack('>BBQ', token | 0xF, 0x13, size))

    def _write_object(self, value):
        ref = self._getrefnum(value)
        self._object_offsets[ref] = self._fp.tell()
        jeżeli value jest Nic:
            self._fp.write(b'\x00')

        albo_inaczej value jest Nieprawda:
            self._fp.write(b'\x08')

        albo_inaczej value jest Prawda:
            self._fp.write(b'\x09')

        albo_inaczej isinstance(value, int):
            jeżeli value < 0:
                spróbuj:
                    self._fp.write(struct.pack('>Bq', 0x13, value))
                wyjąwszy struct.error:
                    podnieś OverflowError(value) z Nic
            albo_inaczej value < 1 << 8:
                self._fp.write(struct.pack('>BB', 0x10, value))
            albo_inaczej value < 1 << 16:
                self._fp.write(struct.pack('>BH', 0x11, value))
            albo_inaczej value < 1 << 32:
                self._fp.write(struct.pack('>BL', 0x12, value))
            albo_inaczej value < 1 << 63:
                self._fp.write(struct.pack('>BQ', 0x13, value))
            albo_inaczej value < 1 << 64:
                self._fp.write(b'\x14' + value.to_bytes(16, 'big', signed=Prawda))
            inaczej:
                podnieś OverflowError(value)

        albo_inaczej isinstance(value, float):
            self._fp.write(struct.pack('>Bd', 0x23, value))

        albo_inaczej isinstance(value, datetime.datetime):
            f = (value - datetime.datetime(2001, 1, 1)).total_seconds()
            self._fp.write(struct.pack('>Bd', 0x33, f))

        albo_inaczej isinstance(value, Data):
            self._write_size(0x40, len(value.data))
            self._fp.write(value.data)

        albo_inaczej isinstance(value, (bytes, bytearray)):
            self._write_size(0x40, len(value))
            self._fp.write(value)

        albo_inaczej isinstance(value, str):
            spróbuj:
                t = value.encode('ascii')
                self._write_size(0x50, len(value))
            wyjąwszy UnicodeEncodeError:
                t = value.encode('utf-16be')
                self._write_size(0x60, len(value))

            self._fp.write(t)

        albo_inaczej isinstance(value, (list, tuple)):
            refs = [self._getrefnum(o) dla o w value]
            s = len(refs)
            self._write_size(0xA0, s)
            self._fp.write(struct.pack('>' + self._ref_format * s, *refs))

        albo_inaczej isinstance(value, dict):
            keyRefs, valRefs = [], []

            jeżeli self._sort_keys:
                rootItems = sorted(value.items())
            inaczej:
                rootItems = value.items()

            dla k, v w rootItems:
                jeżeli nie isinstance(k, str):
                    jeżeli self._skipkeys:
                        kontynuuj
                    podnieś TypeError("keys must be strings")
                keyRefs.append(self._getrefnum(k))
                valRefs.append(self._getrefnum(v))

            s = len(keyRefs)
            self._write_size(0xD0, s)
            self._fp.write(struct.pack('>' + self._ref_format * s, *keyRefs))
            self._fp.write(struct.pack('>' + self._ref_format * s, *valRefs))

        inaczej:
            podnieś TypeError(value)


def _is_fmt_binary(header):
    zwróć header[:8] == b'bplist00'


#
# Generic bits
#

_FORMATS={
    FMT_XML: dict(
        detect=_is_fmt_xml,
        parser=_PlistParser,
        writer=_PlistWriter,
    ),
    FMT_BINARY: dict(
        detect=_is_fmt_binary,
        parser=_BinaryPlistParser,
        writer=_BinaryPlistWriter,
    )
}


def load(fp, *, fmt=Nic, use_builtin_types=Prawda, dict_type=dict):
    """Read a .plist file. 'fp' should be (readable) file object.
    Return the unpacked root object (which usually jest a dictionary).
    """
    jeżeli fmt jest Nic:
        header = fp.read(32)
        fp.seek(0)
        dla info w _FORMATS.values():
            jeżeli info['detect'](header):
                P = info['parser']
                przerwij

        inaczej:
            podnieś InvalidFileException()

    inaczej:
        P = _FORMATS[fmt]['parser']

    p = P(use_builtin_types=use_builtin_types, dict_type=dict_type)
    zwróć p.parse(fp)


def loads(value, *, fmt=Nic, use_builtin_types=Prawda, dict_type=dict):
    """Read a .plist file z a bytes object.
    Return the unpacked root object (which usually jest a dictionary).
    """
    fp = BytesIO(value)
    zwróć load(
        fp, fmt=fmt, use_builtin_types=use_builtin_types, dict_type=dict_type)


def dump(value, fp, *, fmt=FMT_XML, sort_keys=Prawda, skipkeys=Nieprawda):
    """Write 'value' to a .plist file. 'fp' should be a (writable)
    file object.
    """
    jeżeli fmt nie w _FORMATS:
        podnieś ValueError("Unsupported format: %r"%(fmt,))

    writer = _FORMATS[fmt]["writer"](fp, sort_keys=sort_keys, skipkeys=skipkeys)
    writer.write(value)


def dumps(value, *, fmt=FMT_XML, skipkeys=Nieprawda, sort_keys=Prawda):
    """Return a bytes object przy the contents dla a .plist file.
    """
    fp = BytesIO()
    dump(value, fp, fmt=fmt, skipkeys=skipkeys, sort_keys=sort_keys)
    zwróć fp.getvalue()
