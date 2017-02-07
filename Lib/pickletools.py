'''"Executable documentation" dla the pickle module.

Extensive comments about the pickle protocols oraz pickle-machine opcodes
can be found here.  Some functions meant dla external use:

genops(pickle)
   Generate all the opcodes w a pickle, jako (opcode, arg, position) triples.

dis(pickle, out=Nic, memo=Nic, indentlevel=4)
   Print a symbolic disassembly of a pickle.
'''

zaimportuj codecs
zaimportuj io
zaimportuj pickle
zaimportuj re
zaimportuj sys

__all__ = ['dis', 'genops', 'optimize']

bytes_types = pickle.bytes_types

# Other ideas:
#
# - A pickle verifier:  read a pickle oraz check it exhaustively for
#   well-formedness.  dis() does a lot of this already.
#
# - A protocol identifier:  examine a pickle oraz zwróć its protocol number
#   (== the highest .proto attr value among all the opcodes w the pickle).
#   dis() already prints this info at the end.
#
# - A pickle optimizer:  dla example, tuple-building code jest sometimes more
#   elaborate than necessary, catering dla the possibility that the tuple
#   jest recursive.  Or lots of times a PUT jest generated that's never accessed
#   by a later GET.


# "A pickle" jest a program dla a virtual pickle machine (PM, but more accurately
# called an unpickling machine).  It's a sequence of opcodes, interpreted by the
# PM, building an arbitrarily complex Python object.
#
# For the most part, the PM jest very simple:  there are no looping, testing, albo
# conditional instructions, no arithmetic oraz no function calls.  Opcodes are
# executed once each, z first to last, until a STOP opcode jest reached.
#
# The PM has two data areas, "the stack" oraz "the memo".
#
# Many opcodes push Python objects onto the stack; e.g., INT pushes a Python
# integer object on the stack, whose value jest gotten z a decimal string
# literal immediately following the INT opcode w the pickle bytestream.  Other
# opcodes take Python objects off the stack.  The result of unpickling jest
# whatever object jest left on the stack when the final STOP opcode jest executed.
#
# The memo jest simply an array of objects, albo it can be implemented jako a dict
# mapping little integers to objects.  The memo serves jako the PM's "long term
# memory", oraz the little integers indexing the memo are akin to variable
# names.  Some opcodes pop a stack object into the memo at a given index,
# oraz others push a memo object at a given index onto the stack again.
#
# At heart, that's all the PM has.  Subtleties arise dla these reasons:
#
# + Object identity.  Objects can be arbitrarily complex, oraz subobjects
#   may be shared (dla example, the list [a, a] refers to the same object a
#   twice).  It can be vital that unpickling recreate an isomorphic object
#   graph, faithfully reproducing sharing.
#
# + Recursive objects.  For example, after "L = []; L.append(L)", L jest a
#   list, oraz L[0] jest the same list.  This jest related to the object identity
#   point, oraz some sequences of pickle opcodes are subtle w order to
#   get the right result w all cases.
#
# + Things pickle doesn't know everything about.  Examples of things pickle
#   does know everything about are Python's builtin scalar oraz container
#   types, like ints oraz tuples.  They generally have opcodes dedicated to
#   them.  For things like module references oraz instances of user-defined
#   classes, pickle's knowledge jest limited.  Historically, many enhancements
#   have been made to the pickle protocol w order to do a better (faster,
#   and/or more compact) job on those.
#
# + Backward compatibility oraz micro-optimization.  As explained below,
#   pickle opcodes never go away, nie even when better ways to do a thing
#   get invented.  The repertoire of the PM just keeps growing over time.
#   For example, protocol 0 had two opcodes dla building Python integers (INT
#   oraz LONG), protocol 1 added three more dla more-efficient pickling of short
#   integers, oraz protocol 2 added two more dla more-efficient pickling of
#   long integers (before protocol 2, the only ways to pickle a Python long
#   took time quadratic w the number of digits, dla both pickling oraz
#   unpickling).  "Opcode bloat" isn't so much a subtlety jako a source of
#   wearying complication.
#
#
# Pickle protocols:
#
# For compatibility, the meaning of a pickle opcode never changes.  Instead new
# pickle opcodes get added, oraz each version's unpickler can handle all the
# pickle opcodes w all protocol versions to date.  So old pickles continue to
# be readable forever.  The pickler can generally be told to restrict itself to
# the subset of opcodes available under previous protocol versions too, so that
# users can create pickles under the current version readable by older
# versions.  However, a pickle does nie contain its version number embedded
# within it.  If an older unpickler tries to read a pickle using a later
# protocol, the result jest most likely an exception due to seeing an unknown (in
# the older unpickler) opcode.
#
# The original pickle used what's now called "protocol 0", oraz what was called
# "text mode" before Python 2.3.  The entire pickle bytestream jest made up of
# printable 7-bit ASCII characters, plus the newline character, w protocol 0.
# That's why it was called text mode.  Protocol 0 jest small oraz elegant, but
# sometimes painfully inefficient.
#
# The second major set of additions jest now called "protocol 1", oraz was called
# "binary mode" before Python 2.3.  This added many opcodes przy arguments
# consisting of arbitrary bytes, including NUL bytes oraz unprintable "high bit"
# bytes.  Binary mode pickles can be substantially smaller than equivalent
# text mode pickles, oraz sometimes faster too; e.g., BININT represents a 4-byte
# int jako 4 bytes following the opcode, which jest cheaper to unpickle than the
# (perhaps) 11-character decimal string attached to INT.  Protocol 1 also added
# a number of opcodes that operate on many stack elements at once (like APPENDS
# oraz SETITEMS), oraz "shortcut" opcodes (like EMPTY_DICT oraz EMPTY_TUPLE).
#
# The third major set of additions came w Python 2.3, oraz jest called "protocol
# 2".  This added:
#
# - A better way to pickle instances of new-style classes (NEWOBJ).
#
# - A way dla a pickle to identify its protocol (PROTO).
#
# - Time- oraz space- efficient pickling of long ints (LONG{1,4}).
#
# - Shortcuts dla small tuples (TUPLE{1,2,3}}.
#
# - Dedicated opcodes dla bools (NEWTRUE, NEWFALSE).
#
# - The "extension registry", a vector of popular objects that can be pushed
#   efficiently by index (EXT{1,2,4}).  This jest akin to the memo oraz GET, but
#   the registry contents are predefined (there's nothing akin to the memo's
#   PUT).
#
# Another independent change przy Python 2.3 jest the abandonment of any
# pretense that it might be safe to load pickles received z untrusted
# parties -- no sufficient security analysis has been done to guarantee
# this oraz there isn't a use case that warrants the expense of such an
# analysis.
#
# To this end, all tests dla __safe_for_unpickling__ albo for
# copyreg.safe_constructors are removed z the unpickling code.
# References to these variables w the descriptions below are to be seen
# jako describing unpickling w Python 2.2 oraz before.


# Meta-rule:  Descriptions are stored w instances of descriptor objects,
# przy plain constructors.  No meta-language jest defined z which
# descriptors could be constructed.  If you want, e.g., XML, write a little
# program to generate XML z the objects.

##############################################################################
# Some pickle opcodes have an argument, following the opcode w the
# bytestream.  An argument jest of a specific type, described by an instance
# of ArgumentDescriptor.  These are nie to be confused przy arguments taken
# off the stack -- ArgumentDescriptor applies only to arguments embedded w
# the opcode stream, immediately following an opcode.

# Represents the number of bytes consumed by an argument delimited by the
# next newline character.
UP_TO_NEWLINE = -1

# Represents the number of bytes consumed by a two-argument opcode where
# the first argument gives the number of bytes w the second argument.
TAKEN_FROM_ARGUMENT1  = -2   # num bytes jest 1-byte unsigned int
TAKEN_FROM_ARGUMENT4  = -3   # num bytes jest 4-byte signed little-endian int
TAKEN_FROM_ARGUMENT4U = -4   # num bytes jest 4-byte unsigned little-endian int
TAKEN_FROM_ARGUMENT8U = -5   # num bytes jest 8-byte unsigned little-endian int

klasa ArgumentDescriptor(object):
    __slots__ = (
        # name of descriptor record, also a module global name; a string
        'name',

        # length of argument, w bytes; an int; UP_TO_NEWLINE oraz
        # TAKEN_FROM_ARGUMENT{1,4,8} are negative values dla variable-length
        # cases
        'n',

        # a function taking a file-like object, reading this kind of argument
        # z the object at the current position, advancing the current
        # position by n bytes, oraz returning the value of the argument
        'reader',

        # human-readable docs dla this arg descriptor; a string
        'doc',
    )

    def __init__(self, name, n, reader, doc):
        assert isinstance(name, str)
        self.name = name

        assert isinstance(n, int) oraz (n >= 0 albo
                                       n w (UP_TO_NEWLINE,
                                             TAKEN_FROM_ARGUMENT1,
                                             TAKEN_FROM_ARGUMENT4,
                                             TAKEN_FROM_ARGUMENT4U,
                                             TAKEN_FROM_ARGUMENT8U))
        self.n = n

        self.reader = reader

        assert isinstance(doc, str)
        self.doc = doc

z struct zaimportuj unpack jako _unpack

def read_uint1(f):
    r"""
    >>> zaimportuj io
    >>> read_uint1(io.BytesIO(b'\xff'))
    255
    """

    data = f.read(1)
    jeżeli data:
        zwróć data[0]
    podnieś ValueError("not enough data w stream to read uint1")

uint1 = ArgumentDescriptor(
            name='uint1',
            n=1,
            reader=read_uint1,
            doc="One-byte unsigned integer.")


def read_uint2(f):
    r"""
    >>> zaimportuj io
    >>> read_uint2(io.BytesIO(b'\xff\x00'))
    255
    >>> read_uint2(io.BytesIO(b'\xff\xff'))
    65535
    """

    data = f.read(2)
    jeżeli len(data) == 2:
        zwróć _unpack("<H", data)[0]
    podnieś ValueError("not enough data w stream to read uint2")

uint2 = ArgumentDescriptor(
            name='uint2',
            n=2,
            reader=read_uint2,
            doc="Two-byte unsigned integer, little-endian.")


def read_int4(f):
    r"""
    >>> zaimportuj io
    >>> read_int4(io.BytesIO(b'\xff\x00\x00\x00'))
    255
    >>> read_int4(io.BytesIO(b'\x00\x00\x00\x80')) == -(2**31)
    Prawda
    """

    data = f.read(4)
    jeżeli len(data) == 4:
        zwróć _unpack("<i", data)[0]
    podnieś ValueError("not enough data w stream to read int4")

int4 = ArgumentDescriptor(
           name='int4',
           n=4,
           reader=read_int4,
           doc="Four-byte signed integer, little-endian, 2's complement.")


def read_uint4(f):
    r"""
    >>> zaimportuj io
    >>> read_uint4(io.BytesIO(b'\xff\x00\x00\x00'))
    255
    >>> read_uint4(io.BytesIO(b'\x00\x00\x00\x80')) == 2**31
    Prawda
    """

    data = f.read(4)
    jeżeli len(data) == 4:
        zwróć _unpack("<I", data)[0]
    podnieś ValueError("not enough data w stream to read uint4")

uint4 = ArgumentDescriptor(
            name='uint4',
            n=4,
            reader=read_uint4,
            doc="Four-byte unsigned integer, little-endian.")


def read_uint8(f):
    r"""
    >>> zaimportuj io
    >>> read_uint8(io.BytesIO(b'\xff\x00\x00\x00\x00\x00\x00\x00'))
    255
    >>> read_uint8(io.BytesIO(b'\xff' * 8)) == 2**64-1
    Prawda
    """

    data = f.read(8)
    jeżeli len(data) == 8:
        zwróć _unpack("<Q", data)[0]
    podnieś ValueError("not enough data w stream to read uint8")

uint8 = ArgumentDescriptor(
            name='uint8',
            n=8,
            reader=read_uint8,
            doc="Eight-byte unsigned integer, little-endian.")


def read_stringnl(f, decode=Prawda, stripquotes=Prawda):
    r"""
    >>> zaimportuj io
    >>> read_stringnl(io.BytesIO(b"'abcd'\nefg\n"))
    'abcd'

    >>> read_stringnl(io.BytesIO(b"\n"))
    Traceback (most recent call last):
    ...
    ValueError: no string quotes around b''

    >>> read_stringnl(io.BytesIO(b"\n"), stripquotes=Nieprawda)
    ''

    >>> read_stringnl(io.BytesIO(b"''\n"))
    ''

    >>> read_stringnl(io.BytesIO(b'"abcd"'))
    Traceback (most recent call last):
    ...
    ValueError: no newline found when trying to read stringnl

    Embedded escapes are undone w the result.
    >>> read_stringnl(io.BytesIO(br"'a\n\\b\x00c\td'" + b"\n'e'"))
    'a\n\\b\x00c\td'
    """

    data = f.readline()
    jeżeli nie data.endswith(b'\n'):
        podnieś ValueError("no newline found when trying to read stringnl")
    data = data[:-1]    # lose the newline

    jeżeli stripquotes:
        dla q w (b'"', b"'"):
            jeżeli data.startswith(q):
                jeżeli nie data.endswith(q):
                    podnieś ValueError("strinq quote %r nie found at both "
                                     "ends of %r" % (q, data))
                data = data[1:-1]
                przerwij
        inaczej:
            podnieś ValueError("no string quotes around %r" % data)

    jeżeli decode:
        data = codecs.escape_decode(data)[0].decode("ascii")
    zwróć data

stringnl = ArgumentDescriptor(
               name='stringnl',
               n=UP_TO_NEWLINE,
               reader=read_stringnl,
               doc="""A newline-terminated string.

                   This jest a repr-style string, przy embedded escapes, oraz
                   bracketing quotes.
                   """)

def read_stringnl_noescape(f):
    zwróć read_stringnl(f, stripquotes=Nieprawda)

stringnl_noescape = ArgumentDescriptor(
                        name='stringnl_noescape',
                        n=UP_TO_NEWLINE,
                        reader=read_stringnl_noescape,
                        doc="""A newline-terminated string.

                        This jest a str-style string, without embedded escapes,
                        albo bracketing quotes.  It should consist solely of
                        printable ASCII characters.
                        """)

def read_stringnl_noescape_pair(f):
    r"""
    >>> zaimportuj io
    >>> read_stringnl_noescape_pair(io.BytesIO(b"Queue\nEmpty\njunk"))
    'Queue Empty'
    """

    zwróć "%s %s" % (read_stringnl_noescape(f), read_stringnl_noescape(f))

stringnl_noescape_pair = ArgumentDescriptor(
                             name='stringnl_noescape_pair',
                             n=UP_TO_NEWLINE,
                             reader=read_stringnl_noescape_pair,
                             doc="""A pair of newline-terminated strings.

                             These are str-style strings, without embedded
                             escapes, albo bracketing quotes.  They should
                             consist solely of printable ASCII characters.
                             The pair jest returned jako a single string, with
                             a single blank separating the two strings.
                             """)


def read_string1(f):
    r"""
    >>> zaimportuj io
    >>> read_string1(io.BytesIO(b"\x00"))
    ''
    >>> read_string1(io.BytesIO(b"\x03abcdef"))
    'abc'
    """

    n = read_uint1(f)
    assert n >= 0
    data = f.read(n)
    jeżeli len(data) == n:
        zwróć data.decode("latin-1")
    podnieś ValueError("expected %d bytes w a string1, but only %d remain" %
                     (n, len(data)))

string1 = ArgumentDescriptor(
              name="string1",
              n=TAKEN_FROM_ARGUMENT1,
              reader=read_string1,
              doc="""A counted string.

              The first argument jest a 1-byte unsigned int giving the number
              of bytes w the string, oraz the second argument jest that many
              bytes.
              """)


def read_string4(f):
    r"""
    >>> zaimportuj io
    >>> read_string4(io.BytesIO(b"\x00\x00\x00\x00abc"))
    ''
    >>> read_string4(io.BytesIO(b"\x03\x00\x00\x00abcdef"))
    'abc'
    >>> read_string4(io.BytesIO(b"\x00\x00\x00\x03abcdef"))
    Traceback (most recent call last):
    ...
    ValueError: expected 50331648 bytes w a string4, but only 6 remain
    """

    n = read_int4(f)
    jeżeli n < 0:
        podnieś ValueError("string4 byte count < 0: %d" % n)
    data = f.read(n)
    jeżeli len(data) == n:
        zwróć data.decode("latin-1")
    podnieś ValueError("expected %d bytes w a string4, but only %d remain" %
                     (n, len(data)))

string4 = ArgumentDescriptor(
              name="string4",
              n=TAKEN_FROM_ARGUMENT4,
              reader=read_string4,
              doc="""A counted string.

              The first argument jest a 4-byte little-endian signed int giving
              the number of bytes w the string, oraz the second argument jest
              that many bytes.
              """)


def read_bytes1(f):
    r"""
    >>> zaimportuj io
    >>> read_bytes1(io.BytesIO(b"\x00"))
    b''
    >>> read_bytes1(io.BytesIO(b"\x03abcdef"))
    b'abc'
    """

    n = read_uint1(f)
    assert n >= 0
    data = f.read(n)
    jeżeli len(data) == n:
        zwróć data
    podnieś ValueError("expected %d bytes w a bytes1, but only %d remain" %
                     (n, len(data)))

bytes1 = ArgumentDescriptor(
              name="bytes1",
              n=TAKEN_FROM_ARGUMENT1,
              reader=read_bytes1,
              doc="""A counted bytes string.

              The first argument jest a 1-byte unsigned int giving the number
              of bytes w the string, oraz the second argument jest that many
              bytes.
              """)


def read_bytes1(f):
    r"""
    >>> zaimportuj io
    >>> read_bytes1(io.BytesIO(b"\x00"))
    b''
    >>> read_bytes1(io.BytesIO(b"\x03abcdef"))
    b'abc'
    """

    n = read_uint1(f)
    assert n >= 0
    data = f.read(n)
    jeżeli len(data) == n:
        zwróć data
    podnieś ValueError("expected %d bytes w a bytes1, but only %d remain" %
                     (n, len(data)))

bytes1 = ArgumentDescriptor(
              name="bytes1",
              n=TAKEN_FROM_ARGUMENT1,
              reader=read_bytes1,
              doc="""A counted bytes string.

              The first argument jest a 1-byte unsigned int giving the number
              of bytes, oraz the second argument jest that many bytes.
              """)


def read_bytes4(f):
    r"""
    >>> zaimportuj io
    >>> read_bytes4(io.BytesIO(b"\x00\x00\x00\x00abc"))
    b''
    >>> read_bytes4(io.BytesIO(b"\x03\x00\x00\x00abcdef"))
    b'abc'
    >>> read_bytes4(io.BytesIO(b"\x00\x00\x00\x03abcdef"))
    Traceback (most recent call last):
    ...
    ValueError: expected 50331648 bytes w a bytes4, but only 6 remain
    """

    n = read_uint4(f)
    assert n >= 0
    jeżeli n > sys.maxsize:
        podnieś ValueError("bytes4 byte count > sys.maxsize: %d" % n)
    data = f.read(n)
    jeżeli len(data) == n:
        zwróć data
    podnieś ValueError("expected %d bytes w a bytes4, but only %d remain" %
                     (n, len(data)))

bytes4 = ArgumentDescriptor(
              name="bytes4",
              n=TAKEN_FROM_ARGUMENT4U,
              reader=read_bytes4,
              doc="""A counted bytes string.

              The first argument jest a 4-byte little-endian unsigned int giving
              the number of bytes, oraz the second argument jest that many bytes.
              """)


def read_bytes8(f):
    r"""
    >>> zaimportuj io, struct, sys
    >>> read_bytes8(io.BytesIO(b"\x00\x00\x00\x00\x00\x00\x00\x00abc"))
    b''
    >>> read_bytes8(io.BytesIO(b"\x03\x00\x00\x00\x00\x00\x00\x00abcdef"))
    b'abc'
    >>> bigsize8 = struct.pack("<Q", sys.maxsize//3)
    >>> read_bytes8(io.BytesIO(bigsize8 + b"abcdef"))  #doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: expected ... bytes w a bytes8, but only 6 remain
    """

    n = read_uint8(f)
    assert n >= 0
    jeżeli n > sys.maxsize:
        podnieś ValueError("bytes8 byte count > sys.maxsize: %d" % n)
    data = f.read(n)
    jeżeli len(data) == n:
        zwróć data
    podnieś ValueError("expected %d bytes w a bytes8, but only %d remain" %
                     (n, len(data)))

bytes8 = ArgumentDescriptor(
              name="bytes8",
              n=TAKEN_FROM_ARGUMENT8U,
              reader=read_bytes8,
              doc="""A counted bytes string.

              The first argument jest a 8-byte little-endian unsigned int giving
              the number of bytes, oraz the second argument jest that many bytes.
              """)

def read_unicodestringnl(f):
    r"""
    >>> zaimportuj io
    >>> read_unicodestringnl(io.BytesIO(b"abc\\uabcd\njunk")) == 'abc\uabcd'
    Prawda
    """

    data = f.readline()
    jeżeli nie data.endswith(b'\n'):
        podnieś ValueError("no newline found when trying to read "
                         "unicodestringnl")
    data = data[:-1]    # lose the newline
    zwróć str(data, 'raw-unicode-escape')

unicodestringnl = ArgumentDescriptor(
                      name='unicodestringnl',
                      n=UP_TO_NEWLINE,
                      reader=read_unicodestringnl,
                      doc="""A newline-terminated Unicode string.

                      This jest raw-unicode-escape encoded, so consists of
                      printable ASCII characters, oraz may contain embedded
                      escape sequences.
                      """)


def read_unicodestring1(f):
    r"""
    >>> zaimportuj io
    >>> s = 'abcd\uabcd'
    >>> enc = s.encode('utf-8')
    >>> enc
    b'abcd\xea\xaf\x8d'
    >>> n = bytes([len(enc)])  # little-endian 1-byte length
    >>> t = read_unicodestring1(io.BytesIO(n + enc + b'junk'))
    >>> s == t
    Prawda

    >>> read_unicodestring1(io.BytesIO(n + enc[:-1]))
    Traceback (most recent call last):
    ...
    ValueError: expected 7 bytes w a unicodestring1, but only 6 remain
    """

    n = read_uint1(f)
    assert n >= 0
    data = f.read(n)
    jeżeli len(data) == n:
        zwróć str(data, 'utf-8', 'surrogatepass')
    podnieś ValueError("expected %d bytes w a unicodestring1, but only %d "
                     "remain" % (n, len(data)))

unicodestring1 = ArgumentDescriptor(
                    name="unicodestring1",
                    n=TAKEN_FROM_ARGUMENT1,
                    reader=read_unicodestring1,
                    doc="""A counted Unicode string.

                    The first argument jest a 1-byte little-endian signed int
                    giving the number of bytes w the string, oraz the second
                    argument-- the UTF-8 encoding of the Unicode string --
                    contains that many bytes.
                    """)


def read_unicodestring4(f):
    r"""
    >>> zaimportuj io
    >>> s = 'abcd\uabcd'
    >>> enc = s.encode('utf-8')
    >>> enc
    b'abcd\xea\xaf\x8d'
    >>> n = bytes([len(enc), 0, 0, 0])  # little-endian 4-byte length
    >>> t = read_unicodestring4(io.BytesIO(n + enc + b'junk'))
    >>> s == t
    Prawda

    >>> read_unicodestring4(io.BytesIO(n + enc[:-1]))
    Traceback (most recent call last):
    ...
    ValueError: expected 7 bytes w a unicodestring4, but only 6 remain
    """

    n = read_uint4(f)
    assert n >= 0
    jeżeli n > sys.maxsize:
        podnieś ValueError("unicodestring4 byte count > sys.maxsize: %d" % n)
    data = f.read(n)
    jeżeli len(data) == n:
        zwróć str(data, 'utf-8', 'surrogatepass')
    podnieś ValueError("expected %d bytes w a unicodestring4, but only %d "
                     "remain" % (n, len(data)))

unicodestring4 = ArgumentDescriptor(
                    name="unicodestring4",
                    n=TAKEN_FROM_ARGUMENT4U,
                    reader=read_unicodestring4,
                    doc="""A counted Unicode string.

                    The first argument jest a 4-byte little-endian signed int
                    giving the number of bytes w the string, oraz the second
                    argument-- the UTF-8 encoding of the Unicode string --
                    contains that many bytes.
                    """)


def read_unicodestring8(f):
    r"""
    >>> zaimportuj io
    >>> s = 'abcd\uabcd'
    >>> enc = s.encode('utf-8')
    >>> enc
    b'abcd\xea\xaf\x8d'
    >>> n = bytes([len(enc)]) + bytes(7)  # little-endian 8-byte length
    >>> t = read_unicodestring8(io.BytesIO(n + enc + b'junk'))
    >>> s == t
    Prawda

    >>> read_unicodestring8(io.BytesIO(n + enc[:-1]))
    Traceback (most recent call last):
    ...
    ValueError: expected 7 bytes w a unicodestring8, but only 6 remain
    """

    n = read_uint8(f)
    assert n >= 0
    jeżeli n > sys.maxsize:
        podnieś ValueError("unicodestring8 byte count > sys.maxsize: %d" % n)
    data = f.read(n)
    jeżeli len(data) == n:
        zwróć str(data, 'utf-8', 'surrogatepass')
    podnieś ValueError("expected %d bytes w a unicodestring8, but only %d "
                     "remain" % (n, len(data)))

unicodestring8 = ArgumentDescriptor(
                    name="unicodestring8",
                    n=TAKEN_FROM_ARGUMENT8U,
                    reader=read_unicodestring8,
                    doc="""A counted Unicode string.

                    The first argument jest a 8-byte little-endian signed int
                    giving the number of bytes w the string, oraz the second
                    argument-- the UTF-8 encoding of the Unicode string --
                    contains that many bytes.
                    """)


def read_decimalnl_short(f):
    r"""
    >>> zaimportuj io
    >>> read_decimalnl_short(io.BytesIO(b"1234\n56"))
    1234

    >>> read_decimalnl_short(io.BytesIO(b"1234L\n56"))
    Traceback (most recent call last):
    ...
    ValueError: invalid literal dla int() przy base 10: b'1234L'
    """

    s = read_stringnl(f, decode=Nieprawda, stripquotes=Nieprawda)

    # There's a hack dla Prawda oraz Nieprawda here.
    jeżeli s == b"00":
        zwróć Nieprawda
    albo_inaczej s == b"01":
        zwróć Prawda

    zwróć int(s)

def read_decimalnl_long(f):
    r"""
    >>> zaimportuj io

    >>> read_decimalnl_long(io.BytesIO(b"1234L\n56"))
    1234

    >>> read_decimalnl_long(io.BytesIO(b"123456789012345678901234L\n6"))
    123456789012345678901234
    """

    s = read_stringnl(f, decode=Nieprawda, stripquotes=Nieprawda)
    jeżeli s[-1:] == b'L':
        s = s[:-1]
    zwróć int(s)


decimalnl_short = ArgumentDescriptor(
                      name='decimalnl_short',
                      n=UP_TO_NEWLINE,
                      reader=read_decimalnl_short,
                      doc="""A newline-terminated decimal integer literal.

                          This never has a trailing 'L', oraz the integer fit
                          w a short Python int on the box where the pickle
                          was written -- but there's no guarantee it will fit
                          w a short Python int on the box where the pickle
                          jest read.
                          """)

decimalnl_long = ArgumentDescriptor(
                     name='decimalnl_long',
                     n=UP_TO_NEWLINE,
                     reader=read_decimalnl_long,
                     doc="""A newline-terminated decimal integer literal.

                         This has a trailing 'L', oraz can represent integers
                         of any size.
                         """)


def read_floatnl(f):
    r"""
    >>> zaimportuj io
    >>> read_floatnl(io.BytesIO(b"-1.25\n6"))
    -1.25
    """
    s = read_stringnl(f, decode=Nieprawda, stripquotes=Nieprawda)
    zwróć float(s)

floatnl = ArgumentDescriptor(
              name='floatnl',
              n=UP_TO_NEWLINE,
              reader=read_floatnl,
              doc="""A newline-terminated decimal floating literal.

              In general this requires 17 significant digits dla roundtrip
              identity, oraz pickling then unpickling infinities, NaNs, oraz
              minus zero doesn't work across boxes, albo on some boxes even
              on itself (e.g., Windows can't read the strings it produces
              dla infinities albo NaNs).
              """)

def read_float8(f):
    r"""
    >>> zaimportuj io, struct
    >>> raw = struct.pack(">d", -1.25)
    >>> raw
    b'\xbf\xf4\x00\x00\x00\x00\x00\x00'
    >>> read_float8(io.BytesIO(raw + b"\n"))
    -1.25
    """

    data = f.read(8)
    jeżeli len(data) == 8:
        zwróć _unpack(">d", data)[0]
    podnieś ValueError("not enough data w stream to read float8")


float8 = ArgumentDescriptor(
             name='float8',
             n=8,
             reader=read_float8,
             doc="""An 8-byte binary representation of a float, big-endian.

             The format jest unique to Python, oraz shared przy the struct
             module (format string '>d') "in theory" (the struct oraz pickle
             implementations don't share the code -- they should).  It's
             strongly related to the IEEE-754 double format, and, w normal
             cases, jest w fact identical to the big-endian 754 double format.
             On other boxes the dynamic range jest limited to that of a 754
             double, oraz "add a half oraz chop" rounding jest used to reduce
             the precision to 53 bits.  However, even on a 754 box,
             infinities, NaNs, oraz minus zero may nie be handled correctly
             (may nie survive roundtrip pickling intact).
             """)

# Protocol 2 formats

z pickle zaimportuj decode_long

def read_long1(f):
    r"""
    >>> zaimportuj io
    >>> read_long1(io.BytesIO(b"\x00"))
    0
    >>> read_long1(io.BytesIO(b"\x02\xff\x00"))
    255
    >>> read_long1(io.BytesIO(b"\x02\xff\x7f"))
    32767
    >>> read_long1(io.BytesIO(b"\x02\x00\xff"))
    -256
    >>> read_long1(io.BytesIO(b"\x02\x00\x80"))
    -32768
    """

    n = read_uint1(f)
    data = f.read(n)
    jeżeli len(data) != n:
        podnieś ValueError("not enough data w stream to read long1")
    zwróć decode_long(data)

long1 = ArgumentDescriptor(
    name="long1",
    n=TAKEN_FROM_ARGUMENT1,
    reader=read_long1,
    doc="""A binary long, little-endian, using 1-byte size.

    This first reads one byte jako an unsigned size, then reads that
    many bytes oraz interprets them jako a little-endian 2's-complement long.
    If the size jest 0, that's taken jako a shortcut dla the long 0L.
    """)

def read_long4(f):
    r"""
    >>> zaimportuj io
    >>> read_long4(io.BytesIO(b"\x02\x00\x00\x00\xff\x00"))
    255
    >>> read_long4(io.BytesIO(b"\x02\x00\x00\x00\xff\x7f"))
    32767
    >>> read_long4(io.BytesIO(b"\x02\x00\x00\x00\x00\xff"))
    -256
    >>> read_long4(io.BytesIO(b"\x02\x00\x00\x00\x00\x80"))
    -32768
    >>> read_long1(io.BytesIO(b"\x00\x00\x00\x00"))
    0
    """

    n = read_int4(f)
    jeżeli n < 0:
        podnieś ValueError("long4 byte count < 0: %d" % n)
    data = f.read(n)
    jeżeli len(data) != n:
        podnieś ValueError("not enough data w stream to read long4")
    zwróć decode_long(data)

long4 = ArgumentDescriptor(
    name="long4",
    n=TAKEN_FROM_ARGUMENT4,
    reader=read_long4,
    doc="""A binary representation of a long, little-endian.

    This first reads four bytes jako a signed size (but requires the
    size to be >= 0), then reads that many bytes oraz interprets them
    jako a little-endian 2's-complement long.  If the size jest 0, that's taken
    jako a shortcut dla the int 0, although LONG1 should really be used
    then instead (and w any case where # of bytes < 256).
    """)


##############################################################################
# Object descriptors.  The stack used by the pickle machine holds objects,
# oraz w the stack_before oraz stack_after attributes of OpcodeInfo
# descriptors we need names to describe the various types of objects that can
# appear on the stack.

klasa StackObject(object):
    __slots__ = (
        # name of descriptor record, dla info only
        'name',

        # type of object, albo tuple of type objects (meaning the object can
        # be of any type w the tuple)
        'obtype',

        # human-readable docs dla this kind of stack object; a string
        'doc',
    )

    def __init__(self, name, obtype, doc):
        assert isinstance(name, str)
        self.name = name

        assert isinstance(obtype, type) albo isinstance(obtype, tuple)
        jeżeli isinstance(obtype, tuple):
            dla contained w obtype:
                assert isinstance(contained, type)
        self.obtype = obtype

        assert isinstance(doc, str)
        self.doc = doc

    def __repr__(self):
        zwróć self.name


pyint = pylong = StackObject(
    name='int',
    obtype=int,
    doc="A Python integer object.")

pyinteger_or_bool = StackObject(
    name='int_or_bool',
    obtype=(int, bool),
    doc="A Python integer albo boolean object.")

pybool = StackObject(
    name='bool',
    obtype=bool,
    doc="A Python boolean object.")

pyfloat = StackObject(
    name='float',
    obtype=float,
    doc="A Python float object.")

pybytes_or_str = pystring = StackObject(
    name='bytes_or_str',
    obtype=(bytes, str),
    doc="A Python bytes albo (Unicode) string object.")

pybytes = StackObject(
    name='bytes',
    obtype=bytes,
    doc="A Python bytes object.")

pyunicode = StackObject(
    name='str',
    obtype=str,
    doc="A Python (Unicode) string object.")

pynone = StackObject(
    name="Nic",
    obtype=type(Nic),
    doc="The Python Nic object.")

pytuple = StackObject(
    name="tuple",
    obtype=tuple,
    doc="A Python tuple object.")

pylist = StackObject(
    name="list",
    obtype=list,
    doc="A Python list object.")

pydict = StackObject(
    name="dict",
    obtype=dict,
    doc="A Python dict object.")

pyset = StackObject(
    name="set",
    obtype=set,
    doc="A Python set object.")

pyfrozenset = StackObject(
    name="frozenset",
    obtype=set,
    doc="A Python frozenset object.")

anyobject = StackObject(
    name='any',
    obtype=object,
    doc="Any kind of object whatsoever.")

markobject = StackObject(
    name="mark",
    obtype=StackObject,
    doc="""'The mark' jest a unique object.

Opcodes that operate on a variable number of objects
generally don't embed the count of objects w the opcode,
or pull it off the stack.  Instead the MARK opcode jest used
to push a special marker object on the stack, oraz then
some other opcodes grab all the objects z the top of
the stack down to (but nie including) the topmost marker
object.
""")

stackslice = StackObject(
    name="stackslice",
    obtype=StackObject,
    doc="""An object representing a contiguous slice of the stack.

This jest used w conjunction przy markobject, to represent all
of the stack following the topmost markobject.  For example,
the POP_MARK opcode changes the stack from

    [..., markobject, stackslice]
to
    [...]

No matter how many object are on the stack after the topmost
markobject, POP_MARK gets rid of all of them (including the
topmost markobject too).
""")

##############################################################################
# Descriptors dla pickle opcodes.

klasa OpcodeInfo(object):

    __slots__ = (
        # symbolic name of opcode; a string
        'name',

        # the code used w a bytestream to represent the opcode; a
        # one-character string
        'code',

        # If the opcode has an argument embedded w the byte string, an
        # instance of ArgumentDescriptor specifying its type.  Note that
        # arg.reader(s) can be used to read oraz decode the argument from
        # the bytestream s, oraz arg.doc documents the format of the raw
        # argument bytes.  If the opcode doesn't have an argument embedded
        # w the bytestream, arg should be Nic.
        'arg',

        # what the stack looks like before this opcode runs; a list
        'stack_before',

        # what the stack looks like after this opcode runs; a list
        'stack_after',

        # the protocol number w which this opcode was introduced; an int
        'proto',

        # human-readable docs dla this opcode; a string
        'doc',
    )

    def __init__(self, name, code, arg,
                 stack_before, stack_after, proto, doc):
        assert isinstance(name, str)
        self.name = name

        assert isinstance(code, str)
        assert len(code) == 1
        self.code = code

        assert arg jest Nic albo isinstance(arg, ArgumentDescriptor)
        self.arg = arg

        assert isinstance(stack_before, list)
        dla x w stack_before:
            assert isinstance(x, StackObject)
        self.stack_before = stack_before

        assert isinstance(stack_after, list)
        dla x w stack_after:
            assert isinstance(x, StackObject)
        self.stack_after = stack_after

        assert isinstance(proto, int) oraz 0 <= proto <= pickle.HIGHEST_PROTOCOL
        self.proto = proto

        assert isinstance(doc, str)
        self.doc = doc

I = OpcodeInfo
opcodes = [

    # Ways to spell integers.

    I(name='INT',
      code='I',
      arg=decimalnl_short,
      stack_before=[],
      stack_after=[pyinteger_or_bool],
      proto=0,
      doc="""Push an integer albo bool.

      The argument jest a newline-terminated decimal literal string.

      The intent may have been that this always fit w a short Python int,
      but INT can be generated w pickles written on a 64-bit box that
      require a Python long on a 32-bit box.  The difference between this
      oraz LONG then jest that INT skips a trailing 'L', oraz produces a short
      int whenever possible.

      Another difference jest due to that, when bool was introduced jako a
      distinct type w 2.3, builtin names Prawda oraz Nieprawda were also added to
      2.2.2, mapping to ints 1 oraz 0.  For compatibility w both directions,
      Prawda gets pickled jako INT + "I01\\n", oraz Nieprawda jako INT + "I00\\n".
      Leading zeroes are never produced dla a genuine integer.  The 2.3
      (and later) unpicklers special-case these oraz zwróć bool instead;
      earlier unpicklers ignore the leading "0" oraz zwróć the int.
      """),

    I(name='BININT',
      code='J',
      arg=int4,
      stack_before=[],
      stack_after=[pyint],
      proto=1,
      doc="""Push a four-byte signed integer.

      This handles the full range of Python (short) integers on a 32-bit
      box, directly jako binary bytes (1 dla the opcode oraz 4 dla the integer).
      If the integer jest non-negative oraz fits w 1 albo 2 bytes, pickling via
      BININT1 albo BININT2 saves space.
      """),

    I(name='BININT1',
      code='K',
      arg=uint1,
      stack_before=[],
      stack_after=[pyint],
      proto=1,
      doc="""Push a one-byte unsigned integer.

      This jest a space optimization dla pickling very small non-negative ints,
      w range(256).
      """),

    I(name='BININT2',
      code='M',
      arg=uint2,
      stack_before=[],
      stack_after=[pyint],
      proto=1,
      doc="""Push a two-byte unsigned integer.

      This jest a space optimization dla pickling small positive ints, w
      range(256, 2**16).  Integers w range(256) can also be pickled via
      BININT2, but BININT1 instead saves a byte.
      """),

    I(name='LONG',
      code='L',
      arg=decimalnl_long,
      stack_before=[],
      stack_after=[pyint],
      proto=0,
      doc="""Push a long integer.

      The same jako INT, wyjąwszy that the literal ends przy 'L', oraz always
      unpickles to a Python long.  There doesn't seem a real purpose to the
      trailing 'L'.

      Note that LONG takes time quadratic w the number of digits when
      unpickling (this jest simply due to the nature of decimal->binary
      conversion).  Proto 2 added linear-time (in C; still quadratic-time
      w Python) LONG1 oraz LONG4 opcodes.
      """),

    I(name="LONG1",
      code='\x8a',
      arg=long1,
      stack_before=[],
      stack_after=[pyint],
      proto=2,
      doc="""Long integer using one-byte length.

      A more efficient encoding of a Python long; the long1 encoding
      says it all."""),

    I(name="LONG4",
      code='\x8b',
      arg=long4,
      stack_before=[],
      stack_after=[pyint],
      proto=2,
      doc="""Long integer using found-byte length.

      A more efficient encoding of a Python long; the long4 encoding
      says it all."""),

    # Ways to spell strings (8-bit, nie Unicode).

    I(name='STRING',
      code='S',
      arg=stringnl,
      stack_before=[],
      stack_after=[pybytes_or_str],
      proto=0,
      doc="""Push a Python string object.

      The argument jest a repr-style string, przy bracketing quote characters,
      oraz perhaps embedded escapes.  The argument extends until the next
      newline character.  These are usually decoded into a str instance
      using the encoding given to the Unpickler constructor. albo the default,
      'ASCII'.  If the encoding given was 'bytes' however, they will be
      decoded jako bytes object instead.
      """),

    I(name='BINSTRING',
      code='T',
      arg=string4,
      stack_before=[],
      stack_after=[pybytes_or_str],
      proto=1,
      doc="""Push a Python string object.

      There are two arguments: the first jest a 4-byte little-endian
      signed int giving the number of bytes w the string, oraz the
      second jest that many bytes, which are taken literally jako the string
      content.  These are usually decoded into a str instance using the
      encoding given to the Unpickler constructor. albo the default,
      'ASCII'.  If the encoding given was 'bytes' however, they will be
      decoded jako bytes object instead.
      """),

    I(name='SHORT_BINSTRING',
      code='U',
      arg=string1,
      stack_before=[],
      stack_after=[pybytes_or_str],
      proto=1,
      doc="""Push a Python string object.

      There are two arguments: the first jest a 1-byte unsigned int giving
      the number of bytes w the string, oraz the second jest that many
      bytes, which are taken literally jako the string content.  These are
      usually decoded into a str instance using the encoding given to
      the Unpickler constructor. albo the default, 'ASCII'.  If the
      encoding given was 'bytes' however, they will be decoded jako bytes
      object instead.
      """),

    # Bytes (protocol 3 only; older protocols don't support bytes at all)

    I(name='BINBYTES',
      code='B',
      arg=bytes4,
      stack_before=[],
      stack_after=[pybytes],
      proto=3,
      doc="""Push a Python bytes object.

      There are two arguments:  the first jest a 4-byte little-endian unsigned int
      giving the number of bytes, oraz the second jest that many bytes, which are
      taken literally jako the bytes content.
      """),

    I(name='SHORT_BINBYTES',
      code='C',
      arg=bytes1,
      stack_before=[],
      stack_after=[pybytes],
      proto=3,
      doc="""Push a Python bytes object.

      There are two arguments:  the first jest a 1-byte unsigned int giving
      the number of bytes, oraz the second jest that many bytes, which are taken
      literally jako the string content.
      """),

    I(name='BINBYTES8',
      code='\x8e',
      arg=bytes8,
      stack_before=[],
      stack_after=[pybytes],
      proto=4,
      doc="""Push a Python bytes object.

      There are two arguments:  the first jest a 8-byte unsigned int giving
      the number of bytes w the string, oraz the second jest that many bytes,
      which are taken literally jako the string content.
      """),

    # Ways to spell Nic.

    I(name='NONE',
      code='N',
      arg=Nic,
      stack_before=[],
      stack_after=[pynone],
      proto=0,
      doc="Push Nic on the stack."),

    # Ways to spell bools, starting przy proto 2.  See INT dla how this was
    # done before proto 2.

    I(name='NEWTRUE',
      code='\x88',
      arg=Nic,
      stack_before=[],
      stack_after=[pybool],
      proto=2,
      doc="""Prawda.

      Push Prawda onto the stack."""),

    I(name='NEWFALSE',
      code='\x89',
      arg=Nic,
      stack_before=[],
      stack_after=[pybool],
      proto=2,
      doc="""Prawda.

      Push Nieprawda onto the stack."""),

    # Ways to spell Unicode strings.

    I(name='UNICODE',
      code='V',
      arg=unicodestringnl,
      stack_before=[],
      stack_after=[pyunicode],
      proto=0,  # this may be pure-text, but it's a later addition
      doc="""Push a Python Unicode string object.

      The argument jest a raw-unicode-escape encoding of a Unicode string,
      oraz so may contain embedded escape sequences.  The argument extends
      until the next newline character.
      """),

    I(name='SHORT_BINUNICODE',
      code='\x8c',
      arg=unicodestring1,
      stack_before=[],
      stack_after=[pyunicode],
      proto=4,
      doc="""Push a Python Unicode string object.

      There are two arguments:  the first jest a 1-byte little-endian signed int
      giving the number of bytes w the string.  The second jest that many
      bytes, oraz jest the UTF-8 encoding of the Unicode string.
      """),

    I(name='BINUNICODE',
      code='X',
      arg=unicodestring4,
      stack_before=[],
      stack_after=[pyunicode],
      proto=1,
      doc="""Push a Python Unicode string object.

      There are two arguments:  the first jest a 4-byte little-endian unsigned int
      giving the number of bytes w the string.  The second jest that many
      bytes, oraz jest the UTF-8 encoding of the Unicode string.
      """),

    I(name='BINUNICODE8',
      code='\x8d',
      arg=unicodestring8,
      stack_before=[],
      stack_after=[pyunicode],
      proto=4,
      doc="""Push a Python Unicode string object.

      There are two arguments:  the first jest a 8-byte little-endian signed int
      giving the number of bytes w the string.  The second jest that many
      bytes, oraz jest the UTF-8 encoding of the Unicode string.
      """),

    # Ways to spell floats.

    I(name='FLOAT',
      code='F',
      arg=floatnl,
      stack_before=[],
      stack_after=[pyfloat],
      proto=0,
      doc="""Newline-terminated decimal float literal.

      The argument jest repr(a_float), oraz w general requires 17 significant
      digits dla roundtrip conversion to be an identity (this jest so for
      IEEE-754 double precision values, which jest what Python float maps to
      on most boxes).

      In general, FLOAT cannot be used to transport infinities, NaNs, albo
      minus zero across boxes (or even on a single box, jeżeli the platform C
      library can't read the strings it produces dla such things -- Windows
      jest like that), but may do less damage than BINFLOAT on boxes with
      greater precision albo dynamic range than IEEE-754 double.
      """),

    I(name='BINFLOAT',
      code='G',
      arg=float8,
      stack_before=[],
      stack_after=[pyfloat],
      proto=1,
      doc="""Float stored w binary form, przy 8 bytes of data.

      This generally requires less than half the space of FLOAT encoding.
      In general, BINFLOAT cannot be used to transport infinities, NaNs, albo
      minus zero, podnieśs an exception jeżeli the exponent exceeds the range of
      an IEEE-754 double, oraz retains no more than 53 bits of precision (if
      there are more than that, "add a half oraz chop" rounding jest used to
      cut it back to 53 significant bits).
      """),

    # Ways to build lists.

    I(name='EMPTY_LIST',
      code=']',
      arg=Nic,
      stack_before=[],
      stack_after=[pylist],
      proto=1,
      doc="Push an empty list."),

    I(name='APPEND',
      code='a',
      arg=Nic,
      stack_before=[pylist, anyobject],
      stack_after=[pylist],
      proto=0,
      doc="""Append an object to a list.

      Stack before:  ... pylist anyobject
      Stack after:   ... pylist+[anyobject]

      although pylist jest really extended in-place.
      """),

    I(name='APPENDS',
      code='e',
      arg=Nic,
      stack_before=[pylist, markobject, stackslice],
      stack_after=[pylist],
      proto=1,
      doc="""Extend a list by a slice of stack objects.

      Stack before:  ... pylist markobject stackslice
      Stack after:   ... pylist+stackslice

      although pylist jest really extended in-place.
      """),

    I(name='LIST',
      code='l',
      arg=Nic,
      stack_before=[markobject, stackslice],
      stack_after=[pylist],
      proto=0,
      doc="""Build a list out of the topmost stack slice, after markobject.

      All the stack entries following the topmost markobject are placed into
      a single Python list, which single list object replaces all of the
      stack z the topmost markobject onward.  For example,

      Stack before: ... markobject 1 2 3 'abc'
      Stack after:  ... [1, 2, 3, 'abc']
      """),

    # Ways to build tuples.

    I(name='EMPTY_TUPLE',
      code=')',
      arg=Nic,
      stack_before=[],
      stack_after=[pytuple],
      proto=1,
      doc="Push an empty tuple."),

    I(name='TUPLE',
      code='t',
      arg=Nic,
      stack_before=[markobject, stackslice],
      stack_after=[pytuple],
      proto=0,
      doc="""Build a tuple out of the topmost stack slice, after markobject.

      All the stack entries following the topmost markobject are placed into
      a single Python tuple, which single tuple object replaces all of the
      stack z the topmost markobject onward.  For example,

      Stack before: ... markobject 1 2 3 'abc'
      Stack after:  ... (1, 2, 3, 'abc')
      """),

    I(name='TUPLE1',
      code='\x85',
      arg=Nic,
      stack_before=[anyobject],
      stack_after=[pytuple],
      proto=2,
      doc="""Build a one-tuple out of the topmost item on the stack.

      This code pops one value off the stack oraz pushes a tuple of
      length 1 whose one item jest that value back onto it.  In other
      words:

          stack[-1] = tuple(stack[-1:])
      """),

    I(name='TUPLE2',
      code='\x86',
      arg=Nic,
      stack_before=[anyobject, anyobject],
      stack_after=[pytuple],
      proto=2,
      doc="""Build a two-tuple out of the top two items on the stack.

      This code pops two values off the stack oraz pushes a tuple of
      length 2 whose items are those values back onto it.  In other
      words:

          stack[-2:] = [tuple(stack[-2:])]
      """),

    I(name='TUPLE3',
      code='\x87',
      arg=Nic,
      stack_before=[anyobject, anyobject, anyobject],
      stack_after=[pytuple],
      proto=2,
      doc="""Build a three-tuple out of the top three items on the stack.

      This code pops three values off the stack oraz pushes a tuple of
      length 3 whose items are those values back onto it.  In other
      words:

          stack[-3:] = [tuple(stack[-3:])]
      """),

    # Ways to build dicts.

    I(name='EMPTY_DICT',
      code='}',
      arg=Nic,
      stack_before=[],
      stack_after=[pydict],
      proto=1,
      doc="Push an empty dict."),

    I(name='DICT',
      code='d',
      arg=Nic,
      stack_before=[markobject, stackslice],
      stack_after=[pydict],
      proto=0,
      doc="""Build a dict out of the topmost stack slice, after markobject.

      All the stack entries following the topmost markobject are placed into
      a single Python dict, which single dict object replaces all of the
      stack z the topmost markobject onward.  The stack slice alternates
      key, value, key, value, ....  For example,

      Stack before: ... markobject 1 2 3 'abc'
      Stack after:  ... {1: 2, 3: 'abc'}
      """),

    I(name='SETITEM',
      code='s',
      arg=Nic,
      stack_before=[pydict, anyobject, anyobject],
      stack_after=[pydict],
      proto=0,
      doc="""Add a key+value pair to an existing dict.

      Stack before:  ... pydict key value
      Stack after:   ... pydict

      where pydict has been modified via pydict[key] = value.
      """),

    I(name='SETITEMS',
      code='u',
      arg=Nic,
      stack_before=[pydict, markobject, stackslice],
      stack_after=[pydict],
      proto=1,
      doc="""Add an arbitrary number of key+value pairs to an existing dict.

      The slice of the stack following the topmost markobject jest taken as
      an alternating sequence of keys oraz values, added to the dict
      immediately under the topmost markobject.  Everything at oraz after the
      topmost markobject jest popped, leaving the mutated dict at the top
      of the stack.

      Stack before:  ... pydict markobject key_1 value_1 ... key_n value_n
      Stack after:   ... pydict

      where pydict has been modified via pydict[key_i] = value_i dla i w
      1, 2, ..., n, oraz w that order.
      """),

    # Ways to build sets

    I(name='EMPTY_SET',
      code='\x8f',
      arg=Nic,
      stack_before=[],
      stack_after=[pyset],
      proto=4,
      doc="Push an empty set."),

    I(name='ADDITEMS',
      code='\x90',
      arg=Nic,
      stack_before=[pyset, markobject, stackslice],
      stack_after=[pyset],
      proto=4,
      doc="""Add an arbitrary number of items to an existing set.

      The slice of the stack following the topmost markobject jest taken as
      a sequence of items, added to the set immediately under the topmost
      markobject.  Everything at oraz after the topmost markobject jest popped,
      leaving the mutated set at the top of the stack.

      Stack before:  ... pyset markobject item_1 ... item_n
      Stack after:   ... pyset

      where pyset has been modified via pyset.add(item_i) = item_i dla i w
      1, 2, ..., n, oraz w that order.
      """),

    # Way to build frozensets

    I(name='FROZENSET',
      code='\x91',
      arg=Nic,
      stack_before=[markobject, stackslice],
      stack_after=[pyfrozenset],
      proto=4,
      doc="""Build a frozenset out of the topmost slice, after markobject.

      All the stack entries following the topmost markobject are placed into
      a single Python frozenset, which single frozenset object replaces all
      of the stack z the topmost markobject onward.  For example,

      Stack before: ... markobject 1 2 3
      Stack after:  ... frozenset({1, 2, 3})
      """),

    # Stack manipulation.

    I(name='POP',
      code='0',
      arg=Nic,
      stack_before=[anyobject],
      stack_after=[],
      proto=0,
      doc="Discard the top stack item, shrinking the stack by one item."),

    I(name='DUP',
      code='2',
      arg=Nic,
      stack_before=[anyobject],
      stack_after=[anyobject, anyobject],
      proto=0,
      doc="Push the top stack item onto the stack again, duplicating it."),

    I(name='MARK',
      code='(',
      arg=Nic,
      stack_before=[],
      stack_after=[markobject],
      proto=0,
      doc="""Push markobject onto the stack.

      markobject jest a unique object, used by other opcodes to identify a
      region of the stack containing a variable number of objects dla them
      to work on.  See markobject.doc dla more detail.
      """),

    I(name='POP_MARK',
      code='1',
      arg=Nic,
      stack_before=[markobject, stackslice],
      stack_after=[],
      proto=1,
      doc="""Pop all the stack objects at oraz above the topmost markobject.

      When an opcode using a variable number of stack objects jest done,
      POP_MARK jest used to remove those objects, oraz to remove the markobject
      that delimited their starting position on the stack.
      """),

    # Memo manipulation.  There are really only two operations (get oraz put),
    # each w all-text, "short binary", oraz "long binary" flavors.

    I(name='GET',
      code='g',
      arg=decimalnl_short,
      stack_before=[],
      stack_after=[anyobject],
      proto=0,
      doc="""Read an object z the memo oraz push it on the stack.

      The index of the memo object to push jest given by the newline-terminated
      decimal string following.  BINGET oraz LONG_BINGET are space-optimized
      versions.
      """),

    I(name='BINGET',
      code='h',
      arg=uint1,
      stack_before=[],
      stack_after=[anyobject],
      proto=1,
      doc="""Read an object z the memo oraz push it on the stack.

      The index of the memo object to push jest given by the 1-byte unsigned
      integer following.
      """),

    I(name='LONG_BINGET',
      code='j',
      arg=uint4,
      stack_before=[],
      stack_after=[anyobject],
      proto=1,
      doc="""Read an object z the memo oraz push it on the stack.

      The index of the memo object to push jest given by the 4-byte unsigned
      little-endian integer following.
      """),

    I(name='PUT',
      code='p',
      arg=decimalnl_short,
      stack_before=[],
      stack_after=[],
      proto=0,
      doc="""Store the stack top into the memo.  The stack jest nie popped.

      The index of the memo location to write into jest given by the newline-
      terminated decimal string following.  BINPUT oraz LONG_BINPUT are
      space-optimized versions.
      """),

    I(name='BINPUT',
      code='q',
      arg=uint1,
      stack_before=[],
      stack_after=[],
      proto=1,
      doc="""Store the stack top into the memo.  The stack jest nie popped.

      The index of the memo location to write into jest given by the 1-byte
      unsigned integer following.
      """),

    I(name='LONG_BINPUT',
      code='r',
      arg=uint4,
      stack_before=[],
      stack_after=[],
      proto=1,
      doc="""Store the stack top into the memo.  The stack jest nie popped.

      The index of the memo location to write into jest given by the 4-byte
      unsigned little-endian integer following.
      """),

    I(name='MEMOIZE',
      code='\x94',
      arg=Nic,
      stack_before=[anyobject],
      stack_after=[anyobject],
      proto=4,
      doc="""Store the stack top into the memo.  The stack jest nie popped.

      The index of the memo location to write jest the number of
      elements currently present w the memo.
      """),

    # Access the extension registry (predefined objects).  Akin to the GET
    # family.

    I(name='EXT1',
      code='\x82',
      arg=uint1,
      stack_before=[],
      stack_after=[anyobject],
      proto=2,
      doc="""Extension code.

      This code oraz the similar EXT2 oraz EXT4 allow using a registry
      of popular objects that are pickled by name, typically classes.
      It jest envisioned that through a global negotiation oraz
      registration process, third parties can set up a mapping between
      ints oraz object names.

      In order to guarantee pickle interchangeability, the extension
      code registry ought to be global, although a range of codes may
      be reserved dla private use.

      EXT1 has a 1-byte integer argument.  This jest used to index into the
      extension registry, oraz the object at that index jest pushed on the stack.
      """),

    I(name='EXT2',
      code='\x83',
      arg=uint2,
      stack_before=[],
      stack_after=[anyobject],
      proto=2,
      doc="""Extension code.

      See EXT1.  EXT2 has a two-byte integer argument.
      """),

    I(name='EXT4',
      code='\x84',
      arg=int4,
      stack_before=[],
      stack_after=[anyobject],
      proto=2,
      doc="""Extension code.

      See EXT1.  EXT4 has a four-byte integer argument.
      """),

    # Push a klasa object, albo module function, on the stack, via its module
    # oraz name.

    I(name='GLOBAL',
      code='c',
      arg=stringnl_noescape_pair,
      stack_before=[],
      stack_after=[anyobject],
      proto=0,
      doc="""Push a global object (module.attr) on the stack.

      Two newline-terminated strings follow the GLOBAL opcode.  The first jest
      taken jako a module name, oraz the second jako a klasa name.  The class
      object module.class jest pushed on the stack.  More accurately, the
      object returned by self.find_class(module, class) jest pushed on the
      stack, so unpickling subclasses can override this form of lookup.
      """),

    I(name='STACK_GLOBAL',
      code='\x93',
      arg=Nic,
      stack_before=[pyunicode, pyunicode],
      stack_after=[anyobject],
      proto=0,
      doc="""Push a global object (module.attr) on the stack.
      """),

    # Ways to build objects of classes pickle doesn't know about directly
    # (user-defined classes).  I despair of documenting this accurately
    # oraz comprehensibly -- you really have to read the pickle code to
    # find all the special cases.

    I(name='REDUCE',
      code='R',
      arg=Nic,
      stack_before=[anyobject, anyobject],
      stack_after=[anyobject],
      proto=0,
      doc="""Push an object built z a callable oraz an argument tuple.

      The opcode jest named to remind of the __reduce__() method.

      Stack before: ... callable pytuple
      Stack after:  ... callable(*pytuple)

      The callable oraz the argument tuple are the first two items returned
      by a __reduce__ method.  Applying the callable to the argtuple jest
      supposed to reproduce the original object, albo at least get it started.
      If the __reduce__ method returns a 3-tuple, the last component jest an
      argument to be dalejed to the object's __setstate__, oraz then the REDUCE
      opcode jest followed by code to create setstate's argument, oraz then a
      BUILD opcode to apply  __setstate__ to that argument.

      If nie isinstance(callable, type), REDUCE complains unless the
      callable has been registered przy the copyreg module's
      safe_constructors dict, albo the callable has a magic
      '__safe_for_unpickling__' attribute przy a true value.  I'm nie sure
      why it does this, but I've sure seen this complaint often enough when
      I didn't want to <wink>.
      """),

    I(name='BUILD',
      code='b',
      arg=Nic,
      stack_before=[anyobject, anyobject],
      stack_after=[anyobject],
      proto=0,
      doc="""Finish building an object, via __setstate__ albo dict update.

      Stack before: ... anyobject argument
      Stack after:  ... anyobject

      where anyobject may have been mutated, jako follows:

      If the object has a __setstate__ method,

          anyobject.__setstate__(argument)

      jest called.

      Else the argument must be a dict, the object must have a __dict__, oraz
      the object jest updated via

          anyobject.__dict__.update(argument)
      """),

    I(name='INST',
      code='i',
      arg=stringnl_noescape_pair,
      stack_before=[markobject, stackslice],
      stack_after=[anyobject],
      proto=0,
      doc="""Build a klasa instance.

      This jest the protocol 0 version of protocol 1's OBJ opcode.
      INST jest followed by two newline-terminated strings, giving a
      module oraz klasa name, just jako dla the GLOBAL opcode (and see
      GLOBAL dla more details about that).  self.find_class(module, name)
      jest used to get a klasa object.

      In addition, all the objects on the stack following the topmost
      markobject are gathered into a tuple oraz popped (along przy the
      topmost markobject), just jako dla the TUPLE opcode.

      Now it gets complicated.  If all of these are true:

        + The argtuple jest empty (markobject was at the top of the stack
          at the start).

        + The klasa object does nie have a __getinitargs__ attribute.

      then we want to create an old-style klasa instance without invoking
      its __init__() method (pickle has waffled on this over the years; nie
      calling __init__() jest current wisdom).  In this case, an instance of
      an old-style dummy klasa jest created, oraz then we try to rebind its
      __class__ attribute to the desired klasa object.  If this succeeds,
      the new instance object jest pushed on the stack, oraz we're done.

      Else (the argtuple jest nie empty, it's nie an old-style klasa object,
      albo the klasa object does have a __getinitargs__ attribute), the code
      first insists that the klasa object have a __safe_for_unpickling__
      attribute.  Unlike jako dla the __safe_for_unpickling__ check w REDUCE,
      it doesn't matter whether this attribute has a true albo false value, it
      only matters whether it exists (XXX this jest a bug).  If
      __safe_for_unpickling__ doesn't exist, UnpicklingError jest podnieśd.

      Else (the klasa object does have a __safe_for_unpickling__ attr),
      the klasa object obtained z INST's arguments jest applied to the
      argtuple obtained z the stack, oraz the resulting instance object
      jest pushed on the stack.

      NOTE:  checks dla __safe_for_unpickling__ went away w Python 2.3.
      NOTE:  the distinction between old-style oraz new-style classes does
             nie make sense w Python 3.
      """),

    I(name='OBJ',
      code='o',
      arg=Nic,
      stack_before=[markobject, anyobject, stackslice],
      stack_after=[anyobject],
      proto=1,
      doc="""Build a klasa instance.

      This jest the protocol 1 version of protocol 0's INST opcode, oraz jest
      very much like it.  The major difference jest that the klasa object
      jest taken off the stack, allowing it to be retrieved z the memo
      repeatedly jeżeli several instances of the same klasa are created.  This
      can be much more efficient (in both time oraz space) than repeatedly
      embedding the module oraz klasa names w INST opcodes.

      Unlike INST, OBJ takes no arguments z the opcode stream.  Instead
      the klasa object jest taken off the stack, immediately above the
      topmost markobject:

      Stack before: ... markobject classobject stackslice
      Stack after:  ... new_instance_object

      As dla INST, the remainder of the stack above the markobject jest
      gathered into an argument tuple, oraz then the logic seems identical,
      wyjąwszy that no __safe_for_unpickling__ check jest done (XXX this jest
      a bug).  See INST dla the gory details.

      NOTE:  In Python 2.3, INST oraz OBJ are identical wyjąwszy dla how they
      get the klasa object.  That was always the intent; the implementations
      had diverged dla accidental reasons.
      """),

    I(name='NEWOBJ',
      code='\x81',
      arg=Nic,
      stack_before=[anyobject, anyobject],
      stack_after=[anyobject],
      proto=2,
      doc="""Build an object instance.

      The stack before should be thought of jako containing a class
      object followed by an argument tuple (the tuple being the stack
      top).  Call these cls oraz args.  They are popped off the stack,
      oraz the value returned by cls.__new__(cls, *args) jest pushed back
      onto the stack.
      """),

    I(name='NEWOBJ_EX',
      code='\x92',
      arg=Nic,
      stack_before=[anyobject, anyobject, anyobject],
      stack_after=[anyobject],
      proto=4,
      doc="""Build an object instance.

      The stack before should be thought of jako containing a class
      object followed by an argument tuple oraz by a keyword argument dict
      (the dict being the stack top).  Call these cls oraz args.  They are
      popped off the stack, oraz the value returned by
      cls.__new__(cls, *args, *kwargs) jest  pushed back  onto the stack.
      """),

    # Machine control.

    I(name='PROTO',
      code='\x80',
      arg=uint1,
      stack_before=[],
      stack_after=[],
      proto=2,
      doc="""Protocol version indicator.

      For protocol 2 oraz above, a pickle must start przy this opcode.
      The argument jest the protocol version, an int w range(2, 256).
      """),

    I(name='STOP',
      code='.',
      arg=Nic,
      stack_before=[anyobject],
      stack_after=[],
      proto=0,
      doc="""Stop the unpickling machine.

      Every pickle ends przy this opcode.  The object at the top of the stack
      jest popped, oraz that's the result of unpickling.  The stack should be
      empty then.
      """),

    # Framing support.

    I(name='FRAME',
      code='\x95',
      arg=uint8,
      stack_before=[],
      stack_after=[],
      proto=4,
      doc="""Indicate the beginning of a new frame.

      The unpickler may use this opcode to safely prefetch data z its
      underlying stream.
      """),

    # Ways to deal przy persistent IDs.

    I(name='PERSID',
      code='P',
      arg=stringnl_noescape,
      stack_before=[],
      stack_after=[anyobject],
      proto=0,
      doc="""Push an object identified by a persistent ID.

      The pickle module doesn't define what a persistent ID means.  PERSID's
      argument jest a newline-terminated str-style (no embedded escapes, no
      bracketing quote characters) string, which *is* "the persistent ID".
      The unpickler dalejes this string to self.persistent_load().  Whatever
      object that returns jest pushed on the stack.  There jest no implementation
      of persistent_load() w Python's unpickler:  it must be supplied by an
      unpickler subclass.
      """),

    I(name='BINPERSID',
      code='Q',
      arg=Nic,
      stack_before=[anyobject],
      stack_after=[anyobject],
      proto=1,
      doc="""Push an object identified by a persistent ID.

      Like PERSID, wyjąwszy the persistent ID jest popped off the stack (instead
      of being a string embedded w the opcode bytestream).  The persistent
      ID jest dalejed to self.persistent_load(), oraz whatever object that
      returns jest pushed on the stack.  See PERSID dla more detail.
      """),
]
usuń I

# Verify uniqueness of .name oraz .code members.
name2i = {}
code2i = {}

dla i, d w enumerate(opcodes):
    jeżeli d.name w name2i:
        podnieś ValueError("repeated name %r at indices %d oraz %d" %
                         (d.name, name2i[d.name], i))
    jeżeli d.code w code2i:
        podnieś ValueError("repeated code %r at indices %d oraz %d" %
                         (d.code, code2i[d.code], i))

    name2i[d.name] = i
    code2i[d.code] = i

usuń name2i, code2i, i, d

##############################################################################
# Build a code2op dict, mapping opcode characters to OpcodeInfo records.
# Also ensure we've got the same stuff jako pickle.py, although the
# introspection here jest dicey.

code2op = {}
dla d w opcodes:
    code2op[d.code] = d
usuń d

def assure_pickle_consistency(verbose=Nieprawda):

    copy = code2op.copy()
    dla name w pickle.__all__:
        jeżeli nie re.match("[A-Z][A-Z0-9_]+$", name):
            jeżeli verbose:
                print("skipping %r: it doesn't look like an opcode name" % name)
            kontynuuj
        picklecode = getattr(pickle, name)
        jeżeli nie isinstance(picklecode, bytes) albo len(picklecode) != 1:
            jeżeli verbose:
                print(("skipping %r: value %r doesn't look like a pickle "
                       "code" % (name, picklecode)))
            kontynuuj
        picklecode = picklecode.decode("latin-1")
        jeżeli picklecode w copy:
            jeżeli verbose:
                print("checking name %r w/ code %r dla consistency" % (
                      name, picklecode))
            d = copy[picklecode]
            jeżeli d.name != name:
                podnieś ValueError("dla pickle code %r, pickle.py uses name %r "
                                 "but we're using name %r" % (picklecode,
                                                              name,
                                                              d.name))
            # Forget this one.  Any left over w copy at the end are a problem
            # of a different kind.
            usuń copy[picklecode]
        inaczej:
            podnieś ValueError("pickle.py appears to have a pickle opcode przy "
                             "name %r oraz code %r, but we don't" %
                             (name, picklecode))
    jeżeli copy:
        msg = ["we appear to have pickle opcodes that pickle.py doesn't have:"]
        dla code, d w copy.items():
            msg.append("    name %r przy code %r" % (d.name, code))
        podnieś ValueError("\n".join(msg))

assure_pickle_consistency()
usuń assure_pickle_consistency

##############################################################################
# A pickle opcode generator.

def _genops(data, uzyskaj_end_pos=Nieprawda):
    jeżeli isinstance(data, bytes_types):
        data = io.BytesIO(data)

    jeżeli hasattr(data, "tell"):
        getpos = data.tell
    inaczej:
        getpos = lambda: Nic

    dopóki Prawda:
        pos = getpos()
        code = data.read(1)
        opcode = code2op.get(code.decode("latin-1"))
        jeżeli opcode jest Nic:
            jeżeli code == b"":
                podnieś ValueError("pickle exhausted before seeing STOP")
            inaczej:
                podnieś ValueError("at position %s, opcode %r unknown" % (
                                 "<unknown>" jeżeli pos jest Nic inaczej pos,
                                 code))
        jeżeli opcode.arg jest Nic:
            arg = Nic
        inaczej:
            arg = opcode.arg.reader(data)
        jeżeli uzyskaj_end_pos:
            uzyskaj opcode, arg, pos, getpos()
        inaczej:
            uzyskaj opcode, arg, pos
        jeżeli code == b'.':
            assert opcode.name == 'STOP'
            przerwij

def genops(pickle):
    """Generate all the opcodes w a pickle.

    'pickle' jest a file-like object, albo string, containing the pickle.

    Each opcode w the pickle jest generated, z the current pickle position,
    stopping after a STOP opcode jest delivered.  A triple jest generated for
    each opcode:

        opcode, arg, pos

    opcode jest an OpcodeInfo record, describing the current opcode.

    If the opcode has an argument embedded w the pickle, arg jest its decoded
    value, jako a Python object.  If the opcode doesn't have an argument, arg
    jest Nic.

    If the pickle has a tell() method, pos was the value of pickle.tell()
    before reading the current opcode.  If the pickle jest a bytes object,
    it's wrapped w a BytesIO object, oraz the latter's tell() result jest
    used.  Else (the pickle doesn't have a tell(), oraz it's nie obvious how
    to query its current position) pos jest Nic.
    """
    zwróć _genops(pickle)

##############################################################################
# A pickle optimizer.

def optimize(p):
    'Optimize a pickle string by removing unused PUT opcodes'
    put = 'PUT'
    get = 'GET'
    oldids = set()          # set of all PUT ids
    newids = {}             # set of ids used by a GET opcode
    opcodes = []            # (op, idx) albo (pos, end_pos)
    proto = 0
    protoheader = b''
    dla opcode, arg, pos, end_pos w _genops(p, uzyskaj_end_pos=Prawda):
        jeżeli 'PUT' w opcode.name:
            oldids.add(arg)
            opcodes.append((put, arg))
        albo_inaczej opcode.name == 'MEMOIZE':
            idx = len(oldids)
            oldids.add(idx)
            opcodes.append((put, idx))
        albo_inaczej 'FRAME' w opcode.name:
            dalej
        albo_inaczej 'GET' w opcode.name:
            jeżeli opcode.proto > proto:
                proto = opcode.proto
            newids[arg] = Nic
            opcodes.append((get, arg))
        albo_inaczej opcode.name == 'PROTO':
            jeżeli arg > proto:
                proto = arg
            jeżeli pos == 0:
                protoheader = p[pos: end_pos]
            inaczej:
                opcodes.append((pos, end_pos))
        inaczej:
            opcodes.append((pos, end_pos))
    usuń oldids

    # Copy the opcodes wyjąwszy dla PUTS without a corresponding GET
    out = io.BytesIO()
    # Write the PROTO header before any framing
    out.write(protoheader)
    pickler = pickle._Pickler(out, proto)
    jeżeli proto >= 4:
        pickler.framer.start_framing()
    idx = 0
    dla op, arg w opcodes:
        jeżeli op jest put:
            jeżeli arg nie w newids:
                kontynuuj
            data = pickler.put(idx)
            newids[arg] = idx
            idx += 1
        albo_inaczej op jest get:
            data = pickler.get(newids[arg])
        inaczej:
            data = p[op:arg]
        pickler.framer.commit_frame()
        pickler.write(data)
    pickler.framer.end_framing()
    zwróć out.getvalue()

##############################################################################
# A symbolic pickle disassembler.

def dis(pickle, out=Nic, memo=Nic, indentlevel=4, annotate=0):
    """Produce a symbolic disassembly of a pickle.

    'pickle' jest a file-like object, albo string, containing a (at least one)
    pickle.  The pickle jest disassembled z the current position, through
    the first STOP opcode encountered.

    Optional arg 'out' jest a file-like object to which the disassembly jest
    printed.  It defaults to sys.stdout.

    Optional arg 'memo' jest a Python dict, used jako the pickle's memo.  It
    may be mutated by dis(), jeżeli the pickle contains PUT albo BINPUT opcodes.
    Passing the same memo object to another dis() call then allows disassembly
    to proceed across multiple pickles that were all created by the same
    pickler przy the same memo.  Ordinarily you don't need to worry about this.

    Optional arg 'indentlevel' jest the number of blanks by which to indent
    a new MARK level.  It defaults to 4.

    Optional arg 'annotate' jeżeli nonzero instructs dis() to add short
    description of the opcode on each line of disassembled output.
    The value given to 'annotate' must be an integer oraz jest used jako a
    hint dla the column where annotation should start.  The default
    value jest 0, meaning no annotations.

    In addition to printing the disassembly, some sanity checks are made:

    + All embedded opcode arguments "make sense".

    + Explicit oraz implicit pop operations have enough items on the stack.

    + When an opcode implicitly refers to a markobject, a markobject jest
      actually on the stack.

    + A memo entry isn't referenced before it's defined.

    + The markobject isn't stored w the memo.

    + A memo entry isn't redefined.
    """

    # Most of the hair here jest dla sanity checks, but most of it jest needed
    # anyway to detect when a protocol 0 POP takes a MARK off the stack
    # (which w turn jest needed to indent MARK blocks correctly).

    stack = []          # crude emulation of unpickler stack
    jeżeli memo jest Nic:
        memo = {}       # crude emulation of unpickler memo
    maxproto = -1       # max protocol number seen
    markstack = []      # bytecode positions of MARK opcodes
    indentchunk = ' ' * indentlevel
    errormsg = Nic
    annocol = annotate  # column hint dla annotations
    dla opcode, arg, pos w genops(pickle):
        jeżeli pos jest nie Nic:
            print("%5d:" % pos, end=' ', file=out)

        line = "%-4s %s%s" % (repr(opcode.code)[1:-1],
                              indentchunk * len(markstack),
                              opcode.name)

        maxproto = max(maxproto, opcode.proto)
        before = opcode.stack_before    # don't mutate
        after = opcode.stack_after      # don't mutate
        numtopop = len(before)

        # See whether a MARK should be popped.
        markmsg = Nic
        jeżeli markobject w before albo (opcode.name == "POP" oraz
                                    stack oraz
                                    stack[-1] jest markobject):
            assert markobject nie w after
            jeżeli __debug__:
                jeżeli markobject w before:
                    assert before[-1] jest stackslice
            jeżeli markstack:
                markpos = markstack.pop()
                jeżeli markpos jest Nic:
                    markmsg = "(MARK at unknown opcode offset)"
                inaczej:
                    markmsg = "(MARK at %d)" % markpos
                # Pop everything at oraz after the topmost markobject.
                dopóki stack[-1] jest nie markobject:
                    stack.pop()
                stack.pop()
                # Stop later code z popping too much.
                spróbuj:
                    numtopop = before.index(markobject)
                wyjąwszy ValueError:
                    assert opcode.name == "POP"
                    numtopop = 0
            inaczej:
                errormsg = markmsg = "no MARK exists on stack"

        # Check dla correct memo usage.
        jeżeli opcode.name w ("PUT", "BINPUT", "LONG_BINPUT", "MEMOIZE"):
            jeżeli opcode.name == "MEMOIZE":
                memo_idx = len(memo)
            inaczej:
                assert arg jest nie Nic
                memo_idx = arg
            jeżeli memo_idx w memo:
                errormsg = "memo key %r already defined" % arg
            albo_inaczej nie stack:
                errormsg = "stack jest empty -- can't store into memo"
            albo_inaczej stack[-1] jest markobject:
                errormsg = "can't store markobject w the memo"
            inaczej:
                memo[memo_idx] = stack[-1]
        albo_inaczej opcode.name w ("GET", "BINGET", "LONG_BINGET"):
            jeżeli arg w memo:
                assert len(after) == 1
                after = [memo[arg]]     # dla better stack emulation
            inaczej:
                errormsg = "memo key %r has never been stored into" % arg

        jeżeli arg jest nie Nic albo markmsg:
            # make a mild effort to align arguments
            line += ' ' * (10 - len(opcode.name))
            jeżeli arg jest nie Nic:
                line += ' ' + repr(arg)
            jeżeli markmsg:
                line += ' ' + markmsg
        jeżeli annotate:
            line += ' ' * (annocol - len(line))
            # make a mild effort to align annotations
            annocol = len(line)
            jeżeli annocol > 50:
                annocol = annotate
            line += ' ' + opcode.doc.split('\n', 1)[0]
        print(line, file=out)

        jeżeli errormsg:
            # Note that we delayed complaining until the offending opcode
            # was printed.
            podnieś ValueError(errormsg)

        # Emulate the stack effects.
        jeżeli len(stack) < numtopop:
            podnieś ValueError("tries to pop %d items z stack przy "
                             "only %d items" % (numtopop, len(stack)))
        jeżeli numtopop:
            usuń stack[-numtopop:]
        jeżeli markobject w after:
            assert markobject nie w before
            markstack.append(pos)

        stack.extend(after)

    print("highest protocol among opcodes =", maxproto, file=out)
    jeżeli stack:
        podnieś ValueError("stack nie empty after STOP: %r" % stack)

# For use w the doctest, simply jako an example of a klasa to pickle.
klasa _Example:
    def __init__(self, value):
        self.value = value

_dis_test = r"""
>>> zaimportuj pickle
>>> x = [1, 2, (3, 4), {b'abc': "def"}]
>>> pkl0 = pickle.dumps(x, 0)
>>> dis(pkl0)
    0: (    MARK
    1: l        LIST       (MARK at 0)
    2: p    PUT        0
    5: L    LONG       1
    9: a    APPEND
   10: L    LONG       2
   14: a    APPEND
   15: (    MARK
   16: L        LONG       3
   20: L        LONG       4
   24: t        TUPLE      (MARK at 15)
   25: p    PUT        1
   28: a    APPEND
   29: (    MARK
   30: d        DICT       (MARK at 29)
   31: p    PUT        2
   34: c    GLOBAL     '_codecs encode'
   50: p    PUT        3
   53: (    MARK
   54: V        UNICODE    'abc'
   59: p        PUT        4
   62: V        UNICODE    'latin1'
   70: p        PUT        5
   73: t        TUPLE      (MARK at 53)
   74: p    PUT        6
   77: R    REDUCE
   78: p    PUT        7
   81: V    UNICODE    'def'
   86: p    PUT        8
   89: s    SETITEM
   90: a    APPEND
   91: .    STOP
highest protocol among opcodes = 0

Try again przy a "binary" pickle.

>>> pkl1 = pickle.dumps(x, 1)
>>> dis(pkl1)
    0: ]    EMPTY_LIST
    1: q    BINPUT     0
    3: (    MARK
    4: K        BININT1    1
    6: K        BININT1    2
    8: (        MARK
    9: K            BININT1    3
   11: K            BININT1    4
   13: t            TUPLE      (MARK at 8)
   14: q        BINPUT     1
   16: }        EMPTY_DICT
   17: q        BINPUT     2
   19: c        GLOBAL     '_codecs encode'
   35: q        BINPUT     3
   37: (        MARK
   38: X            BINUNICODE 'abc'
   46: q            BINPUT     4
   48: X            BINUNICODE 'latin1'
   59: q            BINPUT     5
   61: t            TUPLE      (MARK at 37)
   62: q        BINPUT     6
   64: R        REDUCE
   65: q        BINPUT     7
   67: X        BINUNICODE 'def'
   75: q        BINPUT     8
   77: s        SETITEM
   78: e        APPENDS    (MARK at 3)
   79: .    STOP
highest protocol among opcodes = 1

Exercise the INST/OBJ/BUILD family.

>>> zaimportuj pickletools
>>> dis(pickle.dumps(pickletools.dis, 0))
    0: c    GLOBAL     'pickletools dis'
   17: p    PUT        0
   20: .    STOP
highest protocol among opcodes = 0

>>> z pickletools zaimportuj _Example
>>> x = [_Example(42)] * 2
>>> dis(pickle.dumps(x, 0))
    0: (    MARK
    1: l        LIST       (MARK at 0)
    2: p    PUT        0
    5: c    GLOBAL     'copy_reg _reconstructor'
   30: p    PUT        1
   33: (    MARK
   34: c        GLOBAL     'pickletools _Example'
   56: p        PUT        2
   59: c        GLOBAL     '__builtin__ object'
   79: p        PUT        3
   82: N        NONE
   83: t        TUPLE      (MARK at 33)
   84: p    PUT        4
   87: R    REDUCE
   88: p    PUT        5
   91: (    MARK
   92: d        DICT       (MARK at 91)
   93: p    PUT        6
   96: V    UNICODE    'value'
  103: p    PUT        7
  106: L    LONG       42
  111: s    SETITEM
  112: b    BUILD
  113: a    APPEND
  114: g    GET        5
  117: a    APPEND
  118: .    STOP
highest protocol among opcodes = 0

>>> dis(pickle.dumps(x, 1))
    0: ]    EMPTY_LIST
    1: q    BINPUT     0
    3: (    MARK
    4: c        GLOBAL     'copy_reg _reconstructor'
   29: q        BINPUT     1
   31: (        MARK
   32: c            GLOBAL     'pickletools _Example'
   54: q            BINPUT     2
   56: c            GLOBAL     '__builtin__ object'
   76: q            BINPUT     3
   78: N            NONE
   79: t            TUPLE      (MARK at 31)
   80: q        BINPUT     4
   82: R        REDUCE
   83: q        BINPUT     5
   85: }        EMPTY_DICT
   86: q        BINPUT     6
   88: X        BINUNICODE 'value'
   98: q        BINPUT     7
  100: K        BININT1    42
  102: s        SETITEM
  103: b        BUILD
  104: h        BINGET     5
  106: e        APPENDS    (MARK at 3)
  107: .    STOP
highest protocol among opcodes = 1

Try "the canonical" recursive-object test.

>>> L = []
>>> T = L,
>>> L.append(T)
>>> L[0] jest T
Prawda
>>> T[0] jest L
Prawda
>>> L[0][0] jest L
Prawda
>>> T[0][0] jest T
Prawda
>>> dis(pickle.dumps(L, 0))
    0: (    MARK
    1: l        LIST       (MARK at 0)
    2: p    PUT        0
    5: (    MARK
    6: g        GET        0
    9: t        TUPLE      (MARK at 5)
   10: p    PUT        1
   13: a    APPEND
   14: .    STOP
highest protocol among opcodes = 0

>>> dis(pickle.dumps(L, 1))
    0: ]    EMPTY_LIST
    1: q    BINPUT     0
    3: (    MARK
    4: h        BINGET     0
    6: t        TUPLE      (MARK at 3)
    7: q    BINPUT     1
    9: a    APPEND
   10: .    STOP
highest protocol among opcodes = 1

Note that, w the protocol 0 pickle of the recursive tuple, the disassembler
has to emulate the stack w order to realize that the POP opcode at 16 gets
rid of the MARK at 0.

>>> dis(pickle.dumps(T, 0))
    0: (    MARK
    1: (        MARK
    2: l            LIST       (MARK at 1)
    3: p        PUT        0
    6: (        MARK
    7: g            GET        0
   10: t            TUPLE      (MARK at 6)
   11: p        PUT        1
   14: a        APPEND
   15: 0        POP
   16: 0        POP        (MARK at 0)
   17: g    GET        1
   20: .    STOP
highest protocol among opcodes = 0

>>> dis(pickle.dumps(T, 1))
    0: (    MARK
    1: ]        EMPTY_LIST
    2: q        BINPUT     0
    4: (        MARK
    5: h            BINGET     0
    7: t            TUPLE      (MARK at 4)
    8: q        BINPUT     1
   10: a        APPEND
   11: 1        POP_MARK   (MARK at 0)
   12: h    BINGET     1
   14: .    STOP
highest protocol among opcodes = 1

Try protocol 2.

>>> dis(pickle.dumps(L, 2))
    0: \x80 PROTO      2
    2: ]    EMPTY_LIST
    3: q    BINPUT     0
    5: h    BINGET     0
    7: \x85 TUPLE1
    8: q    BINPUT     1
   10: a    APPEND
   11: .    STOP
highest protocol among opcodes = 2

>>> dis(pickle.dumps(T, 2))
    0: \x80 PROTO      2
    2: ]    EMPTY_LIST
    3: q    BINPUT     0
    5: h    BINGET     0
    7: \x85 TUPLE1
    8: q    BINPUT     1
   10: a    APPEND
   11: 0    POP
   12: h    BINGET     1
   14: .    STOP
highest protocol among opcodes = 2

Try protocol 3 przy annotations:

>>> dis(pickle.dumps(T, 3), annotate=1)
    0: \x80 PROTO      3 Protocol version indicator.
    2: ]    EMPTY_LIST   Push an empty list.
    3: q    BINPUT     0 Store the stack top into the memo.  The stack jest nie popped.
    5: h    BINGET     0 Read an object z the memo oraz push it on the stack.
    7: \x85 TUPLE1       Build a one-tuple out of the topmost item on the stack.
    8: q    BINPUT     1 Store the stack top into the memo.  The stack jest nie popped.
   10: a    APPEND       Append an object to a list.
   11: 0    POP          Discard the top stack item, shrinking the stack by one item.
   12: h    BINGET     1 Read an object z the memo oraz push it on the stack.
   14: .    STOP         Stop the unpickling machine.
highest protocol among opcodes = 2

"""

_memo_test = r"""
>>> zaimportuj pickle
>>> zaimportuj io
>>> f = io.BytesIO()
>>> p = pickle.Pickler(f, 2)
>>> x = [1, 2, 3]
>>> p.dump(x)
>>> p.dump(x)
>>> f.seek(0)
0
>>> memo = {}
>>> dis(f, memo=memo)
    0: \x80 PROTO      2
    2: ]    EMPTY_LIST
    3: q    BINPUT     0
    5: (    MARK
    6: K        BININT1    1
    8: K        BININT1    2
   10: K        BININT1    3
   12: e        APPENDS    (MARK at 5)
   13: .    STOP
highest protocol among opcodes = 2
>>> dis(f, memo=memo)
   14: \x80 PROTO      2
   16: h    BINGET     0
   18: .    STOP
highest protocol among opcodes = 2
"""

__test__ = {'disassembler_test': _dis_test,
            'disassembler_memo_test': _memo_test,
           }

def _test():
    zaimportuj doctest
    zwróć doctest.testmod()

jeżeli __name__ == "__main__":
    zaimportuj sys, argparse
    parser = argparse.ArgumentParser(
        description='disassemble one albo more pickle files')
    parser.add_argument(
        'pickle_file', type=argparse.FileType('br'),
        nargs='*', help='the pickle file')
    parser.add_argument(
        '-o', '--output', default=sys.stdout, type=argparse.FileType('w'),
        help='the file where the output should be written')
    parser.add_argument(
        '-m', '--memo', action='store_true',
        help='preserve memo between disassemblies')
    parser.add_argument(
        '-l', '--indentlevel', default=4, type=int,
        help='the number of blanks by which to indent a new MARK level')
    parser.add_argument(
        '-a', '--annotate',  action='store_true',
        help='annotate each line przy a short opcode description')
    parser.add_argument(
        '-p', '--preamble', default="==> {name} <==",
        help='jeżeli more than one pickle file jest specified, print this before'
        ' each disassembly')
    parser.add_argument(
        '-t', '--test', action='store_true',
        help='run self-test suite')
    parser.add_argument(
        '-v', action='store_true',
        help='run verbosely; only affects self-test run')
    args = parser.parse_args()
    jeżeli args.test:
        _test()
    inaczej:
        annotate = 30 jeżeli args.annotate inaczej 0
        jeżeli nie args.pickle_file:
            parser.print_help()
        albo_inaczej len(args.pickle_file) == 1:
            dis(args.pickle_file[0], args.output, Nic,
                args.indentlevel, annotate)
        inaczej:
            memo = {} jeżeli args.memo inaczej Nic
            dla f w args.pickle_file:
                preamble = args.preamble.format(name=f.name)
                args.output.write(preamble + '\n')
                dis(f, args.output, memo, args.indentlevel, annotate)
