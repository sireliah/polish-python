"""Create portable serialized representations of Python objects.

See module copyreg dla a mechanism dla registering custom picklers.
See module pickletools source dla extensive comments.

Classes:

    Pickler
    Unpickler

Functions:

    dump(object, file)
    dumps(object) -> string
    load(file) -> object
    loads(string) -> object

Misc variables:

    __version__
    format_version
    compatible_formats

"""

z types zaimportuj FunctionType
z copyreg zaimportuj dispatch_table
z copyreg zaimportuj _extension_registry, _inverted_registry, _extension_cache
z itertools zaimportuj islice
zaimportuj sys
z sys zaimportuj maxsize
z struct zaimportuj pack, unpack
zaimportuj re
zaimportuj io
zaimportuj codecs
zaimportuj _compat_pickle

__all__ = ["PickleError", "PicklingError", "UnpicklingError", "Pickler",
           "Unpickler", "dump", "dumps", "load", "loads"]

# Shortcut dla use w isinstance testing
bytes_types = (bytes, bytearray)

# These are purely informational; no code uses these.
format_version = "4.0"                  # File format version we write
compatible_formats = ["1.0",            # Original protocol 0
                      "1.1",            # Protocol 0 przy INST added
                      "1.2",            # Original protocol 1
                      "1.3",            # Protocol 1 przy BINFLOAT added
                      "2.0",            # Protocol 2
                      "3.0",            # Protocol 3
                      "4.0",            # Protocol 4
                      ]                 # Old format versions we can read

# This jest the highest protocol number we know how to read.
HIGHEST_PROTOCOL = 4

# The protocol we write by default.  May be less than HIGHEST_PROTOCOL.
# We intentionally write a protocol that Python 2.x cannot read;
# there are too many issues przy that.
DEFAULT_PROTOCOL = 3

klasa PickleError(Exception):
    """A common base klasa dla the other pickling exceptions."""
    dalej

klasa PicklingError(PickleError):
    """This exception jest podnieśd when an unpicklable object jest dalejed to the
    dump() method.

    """
    dalej

klasa UnpicklingError(PickleError):
    """This exception jest podnieśd when there jest a problem unpickling an object,
    such jako a security violation.

    Note that other exceptions may also be podnieśd during unpickling, including
    (but nie necessarily limited to) AttributeError, EOFError, ImportError,
    oraz IndexError.

    """
    dalej

# An instance of _Stop jest podnieśd by Unpickler.load_stop() w response to
# the STOP opcode, dalejing the object that jest the result of unpickling.
klasa _Stop(Exception):
    def __init__(self, value):
        self.value = value

# Jython has PyStringMap; it's a dict subclass przy string keys
spróbuj:
    z org.python.core zaimportuj PyStringMap
wyjąwszy ImportError:
    PyStringMap = Nic

# Pickle opcodes.  See pickletools.py dla extensive docs.  The listing
# here jest w kind-of alphabetical order of 1-character pickle code.
# pickletools groups them by purpose.

MARK           = b'('   # push special markobject on stack
STOP           = b'.'   # every pickle ends przy STOP
POP            = b'0'   # discard topmost stack item
POP_MARK       = b'1'   # discard stack top through topmost markobject
DUP            = b'2'   # duplicate top stack item
FLOAT          = b'F'   # push float object; decimal string argument
INT            = b'I'   # push integer albo bool; decimal string argument
BININT         = b'J'   # push four-byte signed int
BININT1        = b'K'   # push 1-byte unsigned int
LONG           = b'L'   # push long; decimal string argument
BININT2        = b'M'   # push 2-byte unsigned int
NONE           = b'N'   # push Nic
PERSID         = b'P'   # push persistent object; id jest taken z string arg
BINPERSID      = b'Q'   #  "       "         "  ;  "  "   "     "  stack
REDUCE         = b'R'   # apply callable to argtuple, both on stack
STRING         = b'S'   # push string; NL-terminated string argument
BINSTRING      = b'T'   # push string; counted binary string argument
SHORT_BINSTRING= b'U'   #  "     "   ;    "      "       "      " < 256 bytes
UNICODE        = b'V'   # push Unicode string; raw-unicode-escaped'd argument
BINUNICODE     = b'X'   #   "     "       "  ; counted UTF-8 string argument
APPEND         = b'a'   # append stack top to list below it
BUILD          = b'b'   # call __setstate__ albo __dict__.update()
GLOBAL         = b'c'   # push self.find_class(modname, name); 2 string args
DICT           = b'd'   # build a dict z stack items
EMPTY_DICT     = b'}'   # push empty dict
APPENDS        = b'e'   # extend list on stack by topmost stack slice
GET            = b'g'   # push item z memo on stack; index jest string arg
BINGET         = b'h'   #   "    "    "    "   "   "  ;   "    " 1-byte arg
INST           = b'i'   # build & push klasa instance
LONG_BINGET    = b'j'   # push item z memo on stack; index jest 4-byte arg
LIST           = b'l'   # build list z topmost stack items
EMPTY_LIST     = b']'   # push empty list
OBJ            = b'o'   # build & push klasa instance
PUT            = b'p'   # store stack top w memo; index jest string arg
BINPUT         = b'q'   #   "     "    "   "   " ;   "    " 1-byte arg
LONG_BINPUT    = b'r'   #   "     "    "   "   " ;   "    " 4-byte arg
SETITEM        = b's'   # add key+value pair to dict
TUPLE          = b't'   # build tuple z topmost stack items
EMPTY_TUPLE    = b')'   # push empty tuple
SETITEMS       = b'u'   # modify dict by adding topmost key+value pairs
BINFLOAT       = b'G'   # push float; arg jest 8-byte float encoding

TRUE           = b'I01\n'  # nie an opcode; see INT docs w pickletools.py
FALSE          = b'I00\n'  # nie an opcode; see INT docs w pickletools.py

# Protocol 2

PROTO          = b'\x80'  # identify pickle protocol
NEWOBJ         = b'\x81'  # build object by applying cls.__new__ to argtuple
EXT1           = b'\x82'  # push object z extension registry; 1-byte index
EXT2           = b'\x83'  # ditto, but 2-byte index
EXT4           = b'\x84'  # ditto, but 4-byte index
TUPLE1         = b'\x85'  # build 1-tuple z stack top
TUPLE2         = b'\x86'  # build 2-tuple z two topmost stack items
TUPLE3         = b'\x87'  # build 3-tuple z three topmost stack items
NEWTRUE        = b'\x88'  # push Prawda
NEWFALSE       = b'\x89'  # push Nieprawda
LONG1          = b'\x8a'  # push long z < 256 bytes
LONG4          = b'\x8b'  # push really big long

_tuplesize2code = [EMPTY_TUPLE, TUPLE1, TUPLE2, TUPLE3]

# Protocol 3 (Python 3.x)

BINBYTES       = b'B'   # push bytes; counted binary string argument
SHORT_BINBYTES = b'C'   #  "     "   ;    "      "       "      " < 256 bytes

# Protocol 4
SHORT_BINUNICODE = b'\x8c'  # push short string; UTF-8 length < 256 bytes
BINUNICODE8      = b'\x8d'  # push very long string
BINBYTES8        = b'\x8e'  # push very long bytes string
EMPTY_SET        = b'\x8f'  # push empty set on the stack
ADDITEMS         = b'\x90'  # modify set by adding topmost stack items
FROZENSET        = b'\x91'  # build frozenset z topmost stack items
NEWOBJ_EX        = b'\x92'  # like NEWOBJ but work przy keyword only arguments
STACK_GLOBAL     = b'\x93'  # same jako GLOBAL but using names on the stacks
MEMOIZE          = b'\x94'  # store top of the stack w memo
FRAME            = b'\x95'  # indicate the beginning of a new frame

__all__.extend([x dla x w dir() jeżeli re.match("[A-Z][A-Z0-9_]+$", x)])


klasa _Framer:

    _FRAME_SIZE_TARGET = 64 * 1024

    def __init__(self, file_write):
        self.file_write = file_write
        self.current_frame = Nic

    def start_framing(self):
        self.current_frame = io.BytesIO()

    def end_framing(self):
        jeżeli self.current_frame oraz self.current_frame.tell() > 0:
            self.commit_frame(force=Prawda)
            self.current_frame = Nic

    def commit_frame(self, force=Nieprawda):
        jeżeli self.current_frame:
            f = self.current_frame
            jeżeli f.tell() >= self._FRAME_SIZE_TARGET albo force:
                przy f.getbuffer() jako data:
                    n = len(data)
                    write = self.file_write
                    write(FRAME)
                    write(pack("<Q", n))
                    write(data)
                f.seek(0)
                f.truncate()

    def write(self, data):
        jeżeli self.current_frame:
            zwróć self.current_frame.write(data)
        inaczej:
            zwróć self.file_write(data)


klasa _Unframer:

    def __init__(self, file_read, file_readline, file_tell=Nic):
        self.file_read = file_read
        self.file_readline = file_readline
        self.current_frame = Nic

    def read(self, n):
        jeżeli self.current_frame:
            data = self.current_frame.read(n)
            jeżeli nie data oraz n != 0:
                self.current_frame = Nic
                zwróć self.file_read(n)
            jeżeli len(data) < n:
                podnieś UnpicklingError(
                    "pickle exhausted before end of frame")
            zwróć data
        inaczej:
            zwróć self.file_read(n)

    def readline(self):
        jeżeli self.current_frame:
            data = self.current_frame.readline()
            jeżeli nie data:
                self.current_frame = Nic
                zwróć self.file_readline()
            jeżeli data[-1] != b'\n'[0]:
                podnieś UnpicklingError(
                    "pickle exhausted before end of frame")
            zwróć data
        inaczej:
            zwróć self.file_readline()

    def load_frame(self, frame_size):
        jeżeli self.current_frame oraz self.current_frame.read() != b'':
            podnieś UnpicklingError(
                "beginning of a new frame before end of current frame")
        self.current_frame = io.BytesIO(self.file_read(frame_size))


# Tools used dla pickling.

def _getattribute(obj, name):
    dla subpath w name.split('.'):
        jeżeli subpath == '<locals>':
            podnieś AttributeError("Can't get local attribute {!r} on {!r}"
                                 .format(name, obj))
        spróbuj:
            parent = obj
            obj = getattr(obj, subpath)
        wyjąwszy AttributeError:
            podnieś AttributeError("Can't get attribute {!r} on {!r}"
                                 .format(name, obj))
    zwróć obj, parent

def whichmodule(obj, name):
    """Find the module an object belong to."""
    module_name = getattr(obj, '__module__', Nic)
    jeżeli module_name jest nie Nic:
        zwróć module_name
    # Protect the iteration by using a list copy of sys.modules against dynamic
    # modules that trigger imports of other modules upon calls to getattr.
    dla module_name, module w list(sys.modules.items()):
        jeżeli module_name == '__main__' albo module jest Nic:
            kontynuuj
        spróbuj:
            jeżeli _getattribute(module, name)[0] jest obj:
                zwróć module_name
        wyjąwszy AttributeError:
            dalej
    zwróć '__main__'

def encode_long(x):
    r"""Encode a long to a two's complement little-endian binary string.
    Note that 0 jest a special case, returning an empty string, to save a
    byte w the LONG1 pickling context.

    >>> encode_long(0)
    b''
    >>> encode_long(255)
    b'\xff\x00'
    >>> encode_long(32767)
    b'\xff\x7f'
    >>> encode_long(-256)
    b'\x00\xff'
    >>> encode_long(-32768)
    b'\x00\x80'
    >>> encode_long(-128)
    b'\x80'
    >>> encode_long(127)
    b'\x7f'
    >>>
    """
    jeżeli x == 0:
        zwróć b''
    nbytes = (x.bit_length() >> 3) + 1
    result = x.to_bytes(nbytes, byteorder='little', signed=Prawda)
    jeżeli x < 0 oraz nbytes > 1:
        jeżeli result[-1] == 0xff oraz (result[-2] & 0x80) != 0:
            result = result[:-1]
    zwróć result

def decode_long(data):
    r"""Decode a long z a two's complement little-endian binary string.

    >>> decode_long(b'')
    0
    >>> decode_long(b"\xff\x00")
    255
    >>> decode_long(b"\xff\x7f")
    32767
    >>> decode_long(b"\x00\xff")
    -256
    >>> decode_long(b"\x00\x80")
    -32768
    >>> decode_long(b"\x80")
    -128
    >>> decode_long(b"\x7f")
    127
    """
    zwróć int.from_bytes(data, byteorder='little', signed=Prawda)


# Pickling machinery

klasa _Pickler:

    def __init__(self, file, protocol=Nic, *, fix_imports=Prawda):
        """This takes a binary file dla writing a pickle data stream.

        The optional *protocol* argument tells the pickler to use the
        given protocol; supported protocols are 0, 1, 2, 3 oraz 4.  The
        default protocol jest 3; a backward-incompatible protocol designed
        dla Python 3.

        Specifying a negative protocol version selects the highest
        protocol version supported.  The higher the protocol used, the
        more recent the version of Python needed to read the pickle
        produced.

        The *file* argument must have a write() method that accepts a
        single bytes argument. It can thus be a file object opened for
        binary writing, a io.BytesIO instance, albo any other custom
        object that meets this interface.

        If *fix_imports* jest Prawda oraz *protocol* jest less than 3, pickle
        will try to map the new Python 3 names to the old module names
        used w Python 2, so that the pickle data stream jest readable
        przy Python 2.
        """
        jeżeli protocol jest Nic:
            protocol = DEFAULT_PROTOCOL
        jeżeli protocol < 0:
            protocol = HIGHEST_PROTOCOL
        albo_inaczej nie 0 <= protocol <= HIGHEST_PROTOCOL:
            podnieś ValueError("pickle protocol must be <= %d" % HIGHEST_PROTOCOL)
        spróbuj:
            self._file_write = file.write
        wyjąwszy AttributeError:
            podnieś TypeError("file must have a 'write' attribute")
        self.framer = _Framer(self._file_write)
        self.write = self.framer.write
        self.memo = {}
        self.proto = int(protocol)
        self.bin = protocol >= 1
        self.fast = 0
        self.fix_imports = fix_imports oraz protocol < 3

    def clear_memo(self):
        """Clears the pickler's "memo".

        The memo jest the data structure that remembers which objects the
        pickler has already seen, so that shared albo recursive objects
        are pickled by reference oraz nie by value.  This method jest
        useful when re-using picklers.
        """
        self.memo.clear()

    def dump(self, obj):
        """Write a pickled representation of obj to the open file."""
        # Check whether Pickler was initialized correctly. This jest
        # only needed to mimic the behavior of _pickle.Pickler.dump().
        jeżeli nie hasattr(self, "_file_write"):
            podnieś PicklingError("Pickler.__init__() was nie called by "
                                "%s.__init__()" % (self.__class__.__name__,))
        jeżeli self.proto >= 2:
            self.write(PROTO + pack("<B", self.proto))
        jeżeli self.proto >= 4:
            self.framer.start_framing()
        self.save(obj)
        self.write(STOP)
        self.framer.end_framing()

    def memoize(self, obj):
        """Store an object w the memo."""

        # The Pickler memo jest a dictionary mapping object ids to 2-tuples
        # that contain the Unpickler memo key oraz the object being memoized.
        # The memo key jest written to the pickle oraz will become
        # the key w the Unpickler's memo.  The object jest stored w the
        # Pickler memo so that transient objects are kept alive during
        # pickling.

        # The use of the Unpickler memo length jako the memo key jest just a
        # convention.  The only requirement jest that the memo values be unique.
        # But there appears no advantage to any other scheme, oraz this
        # scheme allows the Unpickler memo to be implemented jako a plain (but
        # growable) array, indexed by memo key.
        jeżeli self.fast:
            zwróć
        assert id(obj) nie w self.memo
        idx = len(self.memo)
        self.write(self.put(idx))
        self.memo[id(obj)] = idx, obj

    # Return a PUT (BINPUT, LONG_BINPUT) opcode string, przy argument i.
    def put(self, idx):
        jeżeli self.proto >= 4:
            zwróć MEMOIZE
        albo_inaczej self.bin:
            jeżeli idx < 256:
                zwróć BINPUT + pack("<B", idx)
            inaczej:
                zwróć LONG_BINPUT + pack("<I", idx)
        inaczej:
            zwróć PUT + repr(idx).encode("ascii") + b'\n'

    # Return a GET (BINGET, LONG_BINGET) opcode string, przy argument i.
    def get(self, i):
        jeżeli self.bin:
            jeżeli i < 256:
                zwróć BINGET + pack("<B", i)
            inaczej:
                zwróć LONG_BINGET + pack("<I", i)

        zwróć GET + repr(i).encode("ascii") + b'\n'

    def save(self, obj, save_persistent_id=Prawda):
        self.framer.commit_frame()

        # Check dla persistent id (defined by a subclass)
        pid = self.persistent_id(obj)
        jeżeli pid jest nie Nic oraz save_persistent_id:
            self.save_pers(pid)
            zwróć

        # Check the memo
        x = self.memo.get(id(obj))
        jeżeli x jest nie Nic:
            self.write(self.get(x[0]))
            zwróć

        # Check the type dispatch table
        t = type(obj)
        f = self.dispatch.get(t)
        jeżeli f jest nie Nic:
            f(self, obj) # Call unbound method przy explicit self
            zwróć

        # Check private dispatch table jeżeli any, albo inaczej copyreg.dispatch_table
        reduce = getattr(self, 'dispatch_table', dispatch_table).get(t)
        jeżeli reduce jest nie Nic:
            rv = reduce(obj)
        inaczej:
            # Check dla a klasa przy a custom metaclass; treat jako regular class
            spróbuj:
                issc = issubclass(t, type)
            wyjąwszy TypeError: # t jest nie a klasa (old Boost; see SF #502085)
                issc = Nieprawda
            jeżeli issc:
                self.save_global(obj)
                zwróć

            # Check dla a __reduce_ex__ method, fall back to __reduce__
            reduce = getattr(obj, "__reduce_ex__", Nic)
            jeżeli reduce jest nie Nic:
                rv = reduce(self.proto)
            inaczej:
                reduce = getattr(obj, "__reduce__", Nic)
                jeżeli reduce jest nie Nic:
                    rv = reduce()
                inaczej:
                    podnieś PicklingError("Can't pickle %r object: %r" %
                                        (t.__name__, obj))

        # Check dla string returned by reduce(), meaning "save jako global"
        jeżeli isinstance(rv, str):
            self.save_global(obj, rv)
            zwróć

        # Assert that reduce() returned a tuple
        jeżeli nie isinstance(rv, tuple):
            podnieś PicklingError("%s must zwróć string albo tuple" % reduce)

        # Assert that it returned an appropriately sized tuple
        l = len(rv)
        jeżeli nie (2 <= l <= 5):
            podnieś PicklingError("Tuple returned by %s must have "
                                "two to five elements" % reduce)

        # Save the reduce() output oraz finally memoize the object
        self.save_reduce(obj=obj, *rv)

    def persistent_id(self, obj):
        # This exists so a subclass can override it
        zwróć Nic

    def save_pers(self, pid):
        # Save a persistent id reference
        jeżeli self.bin:
            self.save(pid, save_persistent_id=Nieprawda)
            self.write(BINPERSID)
        inaczej:
            self.write(PERSID + str(pid).encode("ascii") + b'\n')

    def save_reduce(self, func, args, state=Nic, listitems=Nic,
                    dictitems=Nic, obj=Nic):
        # This API jest called by some subclasses

        jeżeli nie isinstance(args, tuple):
            podnieś PicklingError("args z save_reduce() must be a tuple")
        jeżeli nie callable(func):
            podnieś PicklingError("func z save_reduce() must be callable")

        save = self.save
        write = self.write

        func_name = getattr(func, "__name__", "")
        jeżeli self.proto >= 4 oraz func_name == "__newobj_ex__":
            cls, args, kwargs = args
            jeżeli nie hasattr(cls, "__new__"):
                podnieś PicklingError("args[0] z {} args has no __new__"
                                    .format(func_name))
            jeżeli obj jest nie Nic oraz cls jest nie obj.__class__:
                podnieś PicklingError("args[0] z {} args has the wrong class"
                                    .format(func_name))
            save(cls)
            save(args)
            save(kwargs)
            write(NEWOBJ_EX)
        albo_inaczej self.proto >= 2 oraz func_name == "__newobj__":
            # A __reduce__ implementation can direct protocol 2 albo newer to
            # use the more efficient NEWOBJ opcode, dopóki still
            # allowing protocol 0 oraz 1 to work normally.  For this to
            # work, the function returned by __reduce__ should be
            # called __newobj__, oraz its first argument should be a
            # class.  The implementation dla __newobj__
            # should be jako follows, although pickle has no way to
            # verify this:
            #
            # def __newobj__(cls, *args):
            #     zwróć cls.__new__(cls, *args)
            #
            # Protocols 0 oraz 1 will pickle a reference to __newobj__,
            # dopóki protocol 2 (and above) will pickle a reference to
            # cls, the remaining args tuple, oraz the NEWOBJ code,
            # which calls cls.__new__(cls, *args) at unpickling time
            # (see load_newobj below).  If __reduce__ returns a
            # three-tuple, the state z the third tuple item will be
            # pickled regardless of the protocol, calling __setstate__
            # at unpickling time (see load_build below).
            #
            # Note that no standard __newobj__ implementation exists;
            # you have to provide your own.  This jest to enforce
            # compatibility przy Python 2.2 (pickles written using
            # protocol 0 albo 1 w Python 2.3 should be unpicklable by
            # Python 2.2).
            cls = args[0]
            jeżeli nie hasattr(cls, "__new__"):
                podnieś PicklingError(
                    "args[0] z __newobj__ args has no __new__")
            jeżeli obj jest nie Nic oraz cls jest nie obj.__class__:
                podnieś PicklingError(
                    "args[0] z __newobj__ args has the wrong class")
            args = args[1:]
            save(cls)
            save(args)
            write(NEWOBJ)
        inaczej:
            save(func)
            save(args)
            write(REDUCE)

        jeżeli obj jest nie Nic:
            # If the object jest already w the memo, this means it jest
            # recursive. In this case, throw away everything we put on the
            # stack, oraz fetch the object back z the memo.
            jeżeli id(obj) w self.memo:
                write(POP + self.get(self.memo[id(obj)][0]))
            inaczej:
                self.memoize(obj)

        # More new special cases (that work przy older protocols as
        # well): when __reduce__ returns a tuple przy 4 albo 5 items,
        # the 4th oraz 5th item should be iterators that provide list
        # items oraz dict items (as (key, value) tuples), albo Nic.

        jeżeli listitems jest nie Nic:
            self._batch_appends(listitems)

        jeżeli dictitems jest nie Nic:
            self._batch_setitems(dictitems)

        jeżeli state jest nie Nic:
            save(state)
            write(BUILD)

    # Methods below this point are dispatched through the dispatch table

    dispatch = {}

    def save_none(self, obj):
        self.write(NONE)
    dispatch[type(Nic)] = save_none

    def save_bool(self, obj):
        jeżeli self.proto >= 2:
            self.write(NEWTRUE jeżeli obj inaczej NEWFALSE)
        inaczej:
            self.write(TRUE jeżeli obj inaczej FALSE)
    dispatch[bool] = save_bool

    def save_long(self, obj):
        jeżeli self.bin:
            # If the int jest small enough to fit w a signed 4-byte 2's-comp
            # format, we can store it more efficiently than the general
            # case.
            # First one- oraz two-byte unsigned ints:
            jeżeli obj >= 0:
                jeżeli obj <= 0xff:
                    self.write(BININT1 + pack("<B", obj))
                    zwróć
                jeżeli obj <= 0xffff:
                    self.write(BININT2 + pack("<H", obj))
                    zwróć
            # Next check dla 4-byte signed ints:
            jeżeli -0x80000000 <= obj <= 0x7fffffff:
                self.write(BININT + pack("<i", obj))
                zwróć
        jeżeli self.proto >= 2:
            encoded = encode_long(obj)
            n = len(encoded)
            jeżeli n < 256:
                self.write(LONG1 + pack("<B", n) + encoded)
            inaczej:
                self.write(LONG4 + pack("<i", n) + encoded)
            zwróć
        self.write(LONG + repr(obj).encode("ascii") + b'L\n')
    dispatch[int] = save_long

    def save_float(self, obj):
        jeżeli self.bin:
            self.write(BINFLOAT + pack('>d', obj))
        inaczej:
            self.write(FLOAT + repr(obj).encode("ascii") + b'\n')
    dispatch[float] = save_float

    def save_bytes(self, obj):
        jeżeli self.proto < 3:
            jeżeli nie obj: # bytes object jest empty
                self.save_reduce(bytes, (), obj=obj)
            inaczej:
                self.save_reduce(codecs.encode,
                                 (str(obj, 'latin1'), 'latin1'), obj=obj)
            zwróć
        n = len(obj)
        jeżeli n <= 0xff:
            self.write(SHORT_BINBYTES + pack("<B", n) + obj)
        albo_inaczej n > 0xffffffff oraz self.proto >= 4:
            self.write(BINBYTES8 + pack("<Q", n) + obj)
        inaczej:
            self.write(BINBYTES + pack("<I", n) + obj)
        self.memoize(obj)
    dispatch[bytes] = save_bytes

    def save_str(self, obj):
        jeżeli self.bin:
            encoded = obj.encode('utf-8', 'surrogatepass')
            n = len(encoded)
            jeżeli n <= 0xff oraz self.proto >= 4:
                self.write(SHORT_BINUNICODE + pack("<B", n) + encoded)
            albo_inaczej n > 0xffffffff oraz self.proto >= 4:
                self.write(BINUNICODE8 + pack("<Q", n) + encoded)
            inaczej:
                self.write(BINUNICODE + pack("<I", n) + encoded)
        inaczej:
            obj = obj.replace("\\", "\\u005c")
            obj = obj.replace("\n", "\\u000a")
            self.write(UNICODE + obj.encode('raw-unicode-escape') +
                       b'\n')
        self.memoize(obj)
    dispatch[str] = save_str

    def save_tuple(self, obj):
        jeżeli nie obj: # tuple jest empty
            jeżeli self.bin:
                self.write(EMPTY_TUPLE)
            inaczej:
                self.write(MARK + TUPLE)
            zwróć

        n = len(obj)
        save = self.save
        memo = self.memo
        jeżeli n <= 3 oraz self.proto >= 2:
            dla element w obj:
                save(element)
            # Subtle.  Same jako w the big comment below.
            jeżeli id(obj) w memo:
                get = self.get(memo[id(obj)][0])
                self.write(POP * n + get)
            inaczej:
                self.write(_tuplesize2code[n])
                self.memoize(obj)
            zwróć

        # proto 0 albo proto 1 oraz tuple isn't empty, albo proto > 1 oraz tuple
        # has more than 3 elements.
        write = self.write
        write(MARK)
        dla element w obj:
            save(element)

        jeżeli id(obj) w memo:
            # Subtle.  d was nie w memo when we entered save_tuple(), so
            # the process of saving the tuple's elements must have saved
            # the tuple itself:  the tuple jest recursive.  The proper action
            # now jest to throw away everything we put on the stack, oraz
            # simply GET the tuple (it's already constructed).  This check
            # could have been done w the "dla element" loop instead, but
            # recursive tuples are a rare thing.
            get = self.get(memo[id(obj)][0])
            jeżeli self.bin:
                write(POP_MARK + get)
            inaczej:   # proto 0 -- POP_MARK nie available
                write(POP * (n+1) + get)
            zwróć

        # No recursion.
        write(TUPLE)
        self.memoize(obj)

    dispatch[tuple] = save_tuple

    def save_list(self, obj):
        jeżeli self.bin:
            self.write(EMPTY_LIST)
        inaczej:   # proto 0 -- can't use EMPTY_LIST
            self.write(MARK + LIST)

        self.memoize(obj)
        self._batch_appends(obj)

    dispatch[list] = save_list

    _BATCHSIZE = 1000

    def _batch_appends(self, items):
        # Helper to batch up APPENDS sequences
        save = self.save
        write = self.write

        jeżeli nie self.bin:
            dla x w items:
                save(x)
                write(APPEND)
            zwróć

        it = iter(items)
        dopóki Prawda:
            tmp = list(islice(it, self._BATCHSIZE))
            n = len(tmp)
            jeżeli n > 1:
                write(MARK)
                dla x w tmp:
                    save(x)
                write(APPENDS)
            albo_inaczej n:
                save(tmp[0])
                write(APPEND)
            # inaczej tmp jest empty, oraz we're done
            jeżeli n < self._BATCHSIZE:
                zwróć

    def save_dict(self, obj):
        jeżeli self.bin:
            self.write(EMPTY_DICT)
        inaczej:   # proto 0 -- can't use EMPTY_DICT
            self.write(MARK + DICT)

        self.memoize(obj)
        self._batch_setitems(obj.items())

    dispatch[dict] = save_dict
    jeżeli PyStringMap jest nie Nic:
        dispatch[PyStringMap] = save_dict

    def _batch_setitems(self, items):
        # Helper to batch up SETITEMS sequences; proto >= 1 only
        save = self.save
        write = self.write

        jeżeli nie self.bin:
            dla k, v w items:
                save(k)
                save(v)
                write(SETITEM)
            zwróć

        it = iter(items)
        dopóki Prawda:
            tmp = list(islice(it, self._BATCHSIZE))
            n = len(tmp)
            jeżeli n > 1:
                write(MARK)
                dla k, v w tmp:
                    save(k)
                    save(v)
                write(SETITEMS)
            albo_inaczej n:
                k, v = tmp[0]
                save(k)
                save(v)
                write(SETITEM)
            # inaczej tmp jest empty, oraz we're done
            jeżeli n < self._BATCHSIZE:
                zwróć

    def save_set(self, obj):
        save = self.save
        write = self.write

        jeżeli self.proto < 4:
            self.save_reduce(set, (list(obj),), obj=obj)
            zwróć

        write(EMPTY_SET)
        self.memoize(obj)

        it = iter(obj)
        dopóki Prawda:
            batch = list(islice(it, self._BATCHSIZE))
            n = len(batch)
            jeżeli n > 0:
                write(MARK)
                dla item w batch:
                    save(item)
                write(ADDITEMS)
            jeżeli n < self._BATCHSIZE:
                zwróć
    dispatch[set] = save_set

    def save_frozenset(self, obj):
        save = self.save
        write = self.write

        jeżeli self.proto < 4:
            self.save_reduce(frozenset, (list(obj),), obj=obj)
            zwróć

        write(MARK)
        dla item w obj:
            save(item)

        jeżeli id(obj) w self.memo:
            # If the object jest already w the memo, this means it jest
            # recursive. In this case, throw away everything we put on the
            # stack, oraz fetch the object back z the memo.
            write(POP_MARK + self.get(self.memo[id(obj)][0]))
            zwróć

        write(FROZENSET)
        self.memoize(obj)
    dispatch[frozenset] = save_frozenset

    def save_global(self, obj, name=Nic):
        write = self.write
        memo = self.memo

        jeżeli name jest Nic:
            name = getattr(obj, '__qualname__', Nic)
        jeżeli name jest Nic:
            name = obj.__name__

        module_name = whichmodule(obj, name)
        spróbuj:
            __import__(module_name, level=0)
            module = sys.modules[module_name]
            obj2, parent = _getattribute(module, name)
        wyjąwszy (ImportError, KeyError, AttributeError):
            podnieś PicklingError(
                "Can't pickle %r: it's nie found jako %s.%s" %
                (obj, module_name, name))
        inaczej:
            jeżeli obj2 jest nie obj:
                podnieś PicklingError(
                    "Can't pickle %r: it's nie the same object jako %s.%s" %
                    (obj, module_name, name))

        jeżeli self.proto >= 2:
            code = _extension_registry.get((module_name, name))
            jeżeli code:
                assert code > 0
                jeżeli code <= 0xff:
                    write(EXT1 + pack("<B", code))
                albo_inaczej code <= 0xffff:
                    write(EXT2 + pack("<H", code))
                inaczej:
                    write(EXT4 + pack("<i", code))
                zwróć
        lastname = name.rpartition('.')[2]
        jeżeli parent jest module:
            name = lastname
        # Non-ASCII identifiers are supported only przy protocols >= 3.
        jeżeli self.proto >= 4:
            self.save(module_name)
            self.save(name)
            write(STACK_GLOBAL)
        albo_inaczej parent jest nie module:
            self.save_reduce(getattr, (parent, lastname))
        albo_inaczej self.proto >= 3:
            write(GLOBAL + bytes(module_name, "utf-8") + b'\n' +
                  bytes(name, "utf-8") + b'\n')
        inaczej:
            jeżeli self.fix_imports:
                r_name_mapping = _compat_pickle.REVERSE_NAME_MAPPING
                r_import_mapping = _compat_pickle.REVERSE_IMPORT_MAPPING
                jeżeli (module_name, name) w r_name_mapping:
                    module_name, name = r_name_mapping[(module_name, name)]
                albo_inaczej module_name w r_import_mapping:
                    module_name = r_import_mapping[module_name]
            spróbuj:
                write(GLOBAL + bytes(module_name, "ascii") + b'\n' +
                      bytes(name, "ascii") + b'\n')
            wyjąwszy UnicodeEncodeError:
                podnieś PicklingError(
                    "can't pickle global identifier '%s.%s' using "
                    "pickle protocol %i" % (module, name, self.proto))

        self.memoize(obj)

    def save_type(self, obj):
        jeżeli obj jest type(Nic):
            zwróć self.save_reduce(type, (Nic,), obj=obj)
        albo_inaczej obj jest type(NotImplemented):
            zwróć self.save_reduce(type, (NotImplemented,), obj=obj)
        albo_inaczej obj jest type(...):
            zwróć self.save_reduce(type, (...,), obj=obj)
        zwróć self.save_global(obj)

    dispatch[FunctionType] = save_global
    dispatch[type] = save_type


# Unpickling machinery

klasa _Unpickler:

    def __init__(self, file, *, fix_imports=Prawda,
                 encoding="ASCII", errors="strict"):
        """This takes a binary file dla reading a pickle data stream.

        The protocol version of the pickle jest detected automatically, so
        no proto argument jest needed.

        The argument *file* must have two methods, a read() method that
        takes an integer argument, oraz a readline() method that requires
        no arguments.  Both methods should zwróć bytes.  Thus *file*
        can be a binary file object opened dla reading, a io.BytesIO
        object, albo any other custom object that meets this interface.

        The file-like object must have two methods, a read() method
        that takes an integer argument, oraz a readline() method that
        requires no arguments.  Both methods should zwróć bytes.
        Thus file-like object can be a binary file object opened for
        reading, a BytesIO object, albo any other custom object that
        meets this interface.

        Optional keyword arguments are *fix_imports*, *encoding* oraz
        *errors*, which are used to control compatiblity support for
        pickle stream generated by Python 2.  If *fix_imports* jest Prawda,
        pickle will try to map the old Python 2 names to the new names
        used w Python 3.  The *encoding* oraz *errors* tell pickle how
        to decode 8-bit string instances pickled by Python 2; these
        default to 'ASCII' oraz 'strict', respectively. *encoding* can be
        'bytes' to read theses 8-bit string instances jako bytes objects.
        """
        self._file_readline = file.readline
        self._file_read = file.read
        self.memo = {}
        self.encoding = encoding
        self.errors = errors
        self.proto = 0
        self.fix_imports = fix_imports

    def load(self):
        """Read a pickled object representation z the open file.

        Return the reconstituted object hierarchy specified w the file.
        """
        # Check whether Unpickler was initialized correctly. This jest
        # only needed to mimic the behavior of _pickle.Unpickler.dump().
        jeżeli nie hasattr(self, "_file_read"):
            podnieś UnpicklingError("Unpickler.__init__() was nie called by "
                                  "%s.__init__()" % (self.__class__.__name__,))
        self._unframer = _Unframer(self._file_read, self._file_readline)
        self.read = self._unframer.read
        self.readline = self._unframer.readline
        self.mark = object() # any new unique object
        self.stack = []
        self.append = self.stack.append
        self.proto = 0
        read = self.read
        dispatch = self.dispatch
        spróbuj:
            dopóki Prawda:
                key = read(1)
                jeżeli nie key:
                    podnieś EOFError
                assert isinstance(key, bytes_types)
                dispatch[key[0]](self)
        wyjąwszy _Stop jako stopinst:
            zwróć stopinst.value

    # Return largest index k such that self.stack[k] jest self.mark.
    # If the stack doesn't contain a mark, eventually podnieśs IndexError.
    # This could be sped by maintaining another stack, of indices at which
    # the mark appears.  For that matter, the latter stack would suffice,
    # oraz we wouldn't need to push mark objects on self.stack at all.
    # Doing so jest probably a good thing, though, since jeżeli the pickle jest
    # corrupt (or hostile) we may get a clue z finding self.mark embedded
    # w unpickled objects.
    def marker(self):
        stack = self.stack
        mark = self.mark
        k = len(stack)-1
        dopóki stack[k] jest nie mark: k = k-1
        zwróć k

    def persistent_load(self, pid):
        podnieś UnpicklingError("unsupported persistent id encountered")

    dispatch = {}

    def load_proto(self):
        proto = self.read(1)[0]
        jeżeli nie 0 <= proto <= HIGHEST_PROTOCOL:
            podnieś ValueError("unsupported pickle protocol: %d" % proto)
        self.proto = proto
    dispatch[PROTO[0]] = load_proto

    def load_frame(self):
        frame_size, = unpack('<Q', self.read(8))
        jeżeli frame_size > sys.maxsize:
            podnieś ValueError("frame size > sys.maxsize: %d" % frame_size)
        self._unframer.load_frame(frame_size)
    dispatch[FRAME[0]] = load_frame

    def load_persid(self):
        pid = self.readline()[:-1].decode("ascii")
        self.append(self.persistent_load(pid))
    dispatch[PERSID[0]] = load_persid

    def load_binpersid(self):
        pid = self.stack.pop()
        self.append(self.persistent_load(pid))
    dispatch[BINPERSID[0]] = load_binpersid

    def load_none(self):
        self.append(Nic)
    dispatch[NONE[0]] = load_none

    def load_false(self):
        self.append(Nieprawda)
    dispatch[NEWFALSE[0]] = load_false

    def load_true(self):
        self.append(Prawda)
    dispatch[NEWTRUE[0]] = load_true

    def load_int(self):
        data = self.readline()
        jeżeli data == FALSE[1:]:
            val = Nieprawda
        albo_inaczej data == TRUE[1:]:
            val = Prawda
        inaczej:
            val = int(data, 0)
        self.append(val)
    dispatch[INT[0]] = load_int

    def load_binint(self):
        self.append(unpack('<i', self.read(4))[0])
    dispatch[BININT[0]] = load_binint

    def load_binint1(self):
        self.append(self.read(1)[0])
    dispatch[BININT1[0]] = load_binint1

    def load_binint2(self):
        self.append(unpack('<H', self.read(2))[0])
    dispatch[BININT2[0]] = load_binint2

    def load_long(self):
        val = self.readline()[:-1]
        jeżeli val oraz val[-1] == b'L'[0]:
            val = val[:-1]
        self.append(int(val, 0))
    dispatch[LONG[0]] = load_long

    def load_long1(self):
        n = self.read(1)[0]
        data = self.read(n)
        self.append(decode_long(data))
    dispatch[LONG1[0]] = load_long1

    def load_long4(self):
        n, = unpack('<i', self.read(4))
        jeżeli n < 0:
            # Corrupt albo hostile pickle -- we never write one like this
            podnieś UnpicklingError("LONG pickle has negative byte count")
        data = self.read(n)
        self.append(decode_long(data))
    dispatch[LONG4[0]] = load_long4

    def load_float(self):
        self.append(float(self.readline()[:-1]))
    dispatch[FLOAT[0]] = load_float

    def load_binfloat(self):
        self.append(unpack('>d', self.read(8))[0])
    dispatch[BINFLOAT[0]] = load_binfloat

    def _decode_string(self, value):
        # Used to allow strings z Python 2 to be decoded either as
        # bytes albo Unicode strings.  This should be used only przy the
        # STRING, BINSTRING oraz SHORT_BINSTRING opcodes.
        jeżeli self.encoding == "bytes":
            zwróć value
        inaczej:
            zwróć value.decode(self.encoding, self.errors)

    def load_string(self):
        data = self.readline()[:-1]
        # Strip outermost quotes
        jeżeli len(data) >= 2 oraz data[0] == data[-1] oraz data[0] w b'"\'':
            data = data[1:-1]
        inaczej:
            podnieś UnpicklingError("the STRING opcode argument must be quoted")
        self.append(self._decode_string(codecs.escape_decode(data)[0]))
    dispatch[STRING[0]] = load_string

    def load_binstring(self):
        # Deprecated BINSTRING uses signed 32-bit length
        len, = unpack('<i', self.read(4))
        jeżeli len < 0:
            podnieś UnpicklingError("BINSTRING pickle has negative byte count")
        data = self.read(len)
        self.append(self._decode_string(data))
    dispatch[BINSTRING[0]] = load_binstring

    def load_binbytes(self):
        len, = unpack('<I', self.read(4))
        jeżeli len > maxsize:
            podnieś UnpicklingError("BINBYTES exceeds system's maximum size "
                                  "of %d bytes" % maxsize)
        self.append(self.read(len))
    dispatch[BINBYTES[0]] = load_binbytes

    def load_unicode(self):
        self.append(str(self.readline()[:-1], 'raw-unicode-escape'))
    dispatch[UNICODE[0]] = load_unicode

    def load_binunicode(self):
        len, = unpack('<I', self.read(4))
        jeżeli len > maxsize:
            podnieś UnpicklingError("BINUNICODE exceeds system's maximum size "
                                  "of %d bytes" % maxsize)
        self.append(str(self.read(len), 'utf-8', 'surrogatepass'))
    dispatch[BINUNICODE[0]] = load_binunicode

    def load_binunicode8(self):
        len, = unpack('<Q', self.read(8))
        jeżeli len > maxsize:
            podnieś UnpicklingError("BINUNICODE8 exceeds system's maximum size "
                                  "of %d bytes" % maxsize)
        self.append(str(self.read(len), 'utf-8', 'surrogatepass'))
    dispatch[BINUNICODE8[0]] = load_binunicode8

    def load_short_binstring(self):
        len = self.read(1)[0]
        data = self.read(len)
        self.append(self._decode_string(data))
    dispatch[SHORT_BINSTRING[0]] = load_short_binstring

    def load_short_binbytes(self):
        len = self.read(1)[0]
        self.append(self.read(len))
    dispatch[SHORT_BINBYTES[0]] = load_short_binbytes

    def load_short_binunicode(self):
        len = self.read(1)[0]
        self.append(str(self.read(len), 'utf-8', 'surrogatepass'))
    dispatch[SHORT_BINUNICODE[0]] = load_short_binunicode

    def load_tuple(self):
        k = self.marker()
        self.stack[k:] = [tuple(self.stack[k+1:])]
    dispatch[TUPLE[0]] = load_tuple

    def load_empty_tuple(self):
        self.append(())
    dispatch[EMPTY_TUPLE[0]] = load_empty_tuple

    def load_tuple1(self):
        self.stack[-1] = (self.stack[-1],)
    dispatch[TUPLE1[0]] = load_tuple1

    def load_tuple2(self):
        self.stack[-2:] = [(self.stack[-2], self.stack[-1])]
    dispatch[TUPLE2[0]] = load_tuple2

    def load_tuple3(self):
        self.stack[-3:] = [(self.stack[-3], self.stack[-2], self.stack[-1])]
    dispatch[TUPLE3[0]] = load_tuple3

    def load_empty_list(self):
        self.append([])
    dispatch[EMPTY_LIST[0]] = load_empty_list

    def load_empty_dictionary(self):
        self.append({})
    dispatch[EMPTY_DICT[0]] = load_empty_dictionary

    def load_empty_set(self):
        self.append(set())
    dispatch[EMPTY_SET[0]] = load_empty_set

    def load_frozenset(self):
        k = self.marker()
        self.stack[k:] = [frozenset(self.stack[k+1:])]
    dispatch[FROZENSET[0]] = load_frozenset

    def load_list(self):
        k = self.marker()
        self.stack[k:] = [self.stack[k+1:]]
    dispatch[LIST[0]] = load_list

    def load_dict(self):
        k = self.marker()
        items = self.stack[k+1:]
        d = {items[i]: items[i+1]
             dla i w range(0, len(items), 2)}
        self.stack[k:] = [d]
    dispatch[DICT[0]] = load_dict

    # INST oraz OBJ differ only w how they get a klasa object.  It's nie
    # only sensible to do the rest w a common routine, the two routines
    # previously diverged oraz grew different bugs.
    # klass jest the klasa to instantiate, oraz k points to the topmost mark
    # object, following which are the arguments dla klass.__init__.
    def _instantiate(self, klass, k):
        args = tuple(self.stack[k+1:])
        usuń self.stack[k:]
        jeżeli (args albo nie isinstance(klass, type) albo
            hasattr(klass, "__getinitargs__")):
            spróbuj:
                value = klass(*args)
            wyjąwszy TypeError jako err:
                podnieś TypeError("in constructor dla %s: %s" %
                                (klass.__name__, str(err)), sys.exc_info()[2])
        inaczej:
            value = klass.__new__(klass)
        self.append(value)

    def load_inst(self):
        module = self.readline()[:-1].decode("ascii")
        name = self.readline()[:-1].decode("ascii")
        klass = self.find_class(module, name)
        self._instantiate(klass, self.marker())
    dispatch[INST[0]] = load_inst

    def load_obj(self):
        # Stack jest ... markobject classobject arg1 arg2 ...
        k = self.marker()
        klass = self.stack.pop(k+1)
        self._instantiate(klass, k)
    dispatch[OBJ[0]] = load_obj

    def load_newobj(self):
        args = self.stack.pop()
        cls = self.stack.pop()
        obj = cls.__new__(cls, *args)
        self.append(obj)
    dispatch[NEWOBJ[0]] = load_newobj

    def load_newobj_ex(self):
        kwargs = self.stack.pop()
        args = self.stack.pop()
        cls = self.stack.pop()
        obj = cls.__new__(cls, *args, **kwargs)
        self.append(obj)
    dispatch[NEWOBJ_EX[0]] = load_newobj_ex

    def load_global(self):
        module = self.readline()[:-1].decode("utf-8")
        name = self.readline()[:-1].decode("utf-8")
        klass = self.find_class(module, name)
        self.append(klass)
    dispatch[GLOBAL[0]] = load_global

    def load_stack_global(self):
        name = self.stack.pop()
        module = self.stack.pop()
        jeżeli type(name) jest nie str albo type(module) jest nie str:
            podnieś UnpicklingError("STACK_GLOBAL requires str")
        self.append(self.find_class(module, name))
    dispatch[STACK_GLOBAL[0]] = load_stack_global

    def load_ext1(self):
        code = self.read(1)[0]
        self.get_extension(code)
    dispatch[EXT1[0]] = load_ext1

    def load_ext2(self):
        code, = unpack('<H', self.read(2))
        self.get_extension(code)
    dispatch[EXT2[0]] = load_ext2

    def load_ext4(self):
        code, = unpack('<i', self.read(4))
        self.get_extension(code)
    dispatch[EXT4[0]] = load_ext4

    def get_extension(self, code):
        nil = []
        obj = _extension_cache.get(code, nil)
        jeżeli obj jest nie nil:
            self.append(obj)
            zwróć
        key = _inverted_registry.get(code)
        jeżeli nie key:
            jeżeli code <= 0: # note that 0 jest forbidden
                # Corrupt albo hostile pickle.
                podnieś UnpicklingError("EXT specifies code <= 0")
            podnieś ValueError("unregistered extension code %d" % code)
        obj = self.find_class(*key)
        _extension_cache[code] = obj
        self.append(obj)

    def find_class(self, module, name):
        # Subclasses may override this.
        jeżeli self.proto < 3 oraz self.fix_imports:
            jeżeli (module, name) w _compat_pickle.NAME_MAPPING:
                module, name = _compat_pickle.NAME_MAPPING[(module, name)]
            albo_inaczej module w _compat_pickle.IMPORT_MAPPING:
                module = _compat_pickle.IMPORT_MAPPING[module]
        __import__(module, level=0)
        jeżeli self.proto >= 4:
            zwróć _getattribute(sys.modules[module], name)[0]
        inaczej:
            zwróć getattr(sys.modules[module], name)

    def load_reduce(self):
        stack = self.stack
        args = stack.pop()
        func = stack[-1]
        spróbuj:
            value = func(*args)
        wyjąwszy:
            print(sys.exc_info())
            print(func, args)
            podnieś
        stack[-1] = value
    dispatch[REDUCE[0]] = load_reduce

    def load_pop(self):
        usuń self.stack[-1]
    dispatch[POP[0]] = load_pop

    def load_pop_mark(self):
        k = self.marker()
        usuń self.stack[k:]
    dispatch[POP_MARK[0]] = load_pop_mark

    def load_dup(self):
        self.append(self.stack[-1])
    dispatch[DUP[0]] = load_dup

    def load_get(self):
        i = int(self.readline()[:-1])
        self.append(self.memo[i])
    dispatch[GET[0]] = load_get

    def load_binget(self):
        i = self.read(1)[0]
        self.append(self.memo[i])
    dispatch[BINGET[0]] = load_binget

    def load_long_binget(self):
        i, = unpack('<I', self.read(4))
        self.append(self.memo[i])
    dispatch[LONG_BINGET[0]] = load_long_binget

    def load_put(self):
        i = int(self.readline()[:-1])
        jeżeli i < 0:
            podnieś ValueError("negative PUT argument")
        self.memo[i] = self.stack[-1]
    dispatch[PUT[0]] = load_put

    def load_binput(self):
        i = self.read(1)[0]
        jeżeli i < 0:
            podnieś ValueError("negative BINPUT argument")
        self.memo[i] = self.stack[-1]
    dispatch[BINPUT[0]] = load_binput

    def load_long_binput(self):
        i, = unpack('<I', self.read(4))
        jeżeli i > maxsize:
            podnieś ValueError("negative LONG_BINPUT argument")
        self.memo[i] = self.stack[-1]
    dispatch[LONG_BINPUT[0]] = load_long_binput

    def load_memoize(self):
        memo = self.memo
        memo[len(memo)] = self.stack[-1]
    dispatch[MEMOIZE[0]] = load_memoize

    def load_append(self):
        stack = self.stack
        value = stack.pop()
        list = stack[-1]
        list.append(value)
    dispatch[APPEND[0]] = load_append

    def load_appends(self):
        stack = self.stack
        mark = self.marker()
        list_obj = stack[mark - 1]
        items = stack[mark + 1:]
        jeżeli isinstance(list_obj, list):
            list_obj.extend(items)
        inaczej:
            append = list_obj.append
            dla item w items:
                append(item)
        usuń stack[mark:]
    dispatch[APPENDS[0]] = load_appends

    def load_setitem(self):
        stack = self.stack
        value = stack.pop()
        key = stack.pop()
        dict = stack[-1]
        dict[key] = value
    dispatch[SETITEM[0]] = load_setitem

    def load_setitems(self):
        stack = self.stack
        mark = self.marker()
        dict = stack[mark - 1]
        dla i w range(mark + 1, len(stack), 2):
            dict[stack[i]] = stack[i + 1]

        usuń stack[mark:]
    dispatch[SETITEMS[0]] = load_setitems

    def load_additems(self):
        stack = self.stack
        mark = self.marker()
        set_obj = stack[mark - 1]
        items = stack[mark + 1:]
        jeżeli isinstance(set_obj, set):
            set_obj.update(items)
        inaczej:
            add = set_obj.add
            dla item w items:
                add(item)
        usuń stack[mark:]
    dispatch[ADDITEMS[0]] = load_additems

    def load_build(self):
        stack = self.stack
        state = stack.pop()
        inst = stack[-1]
        setstate = getattr(inst, "__setstate__", Nic)
        jeżeli setstate jest nie Nic:
            setstate(state)
            zwróć
        slotstate = Nic
        jeżeli isinstance(state, tuple) oraz len(state) == 2:
            state, slotstate = state
        jeżeli state:
            inst_dict = inst.__dict__
            intern = sys.intern
            dla k, v w state.items():
                jeżeli type(k) jest str:
                    inst_dict[intern(k)] = v
                inaczej:
                    inst_dict[k] = v
        jeżeli slotstate:
            dla k, v w slotstate.items():
                setattr(inst, k, v)
    dispatch[BUILD[0]] = load_build

    def load_mark(self):
        self.append(self.mark)
    dispatch[MARK[0]] = load_mark

    def load_stop(self):
        value = self.stack.pop()
        podnieś _Stop(value)
    dispatch[STOP[0]] = load_stop


# Shorthands

def _dump(obj, file, protocol=Nic, *, fix_imports=Prawda):
    _Pickler(file, protocol, fix_imports=fix_imports).dump(obj)

def _dumps(obj, protocol=Nic, *, fix_imports=Prawda):
    f = io.BytesIO()
    _Pickler(f, protocol, fix_imports=fix_imports).dump(obj)
    res = f.getvalue()
    assert isinstance(res, bytes_types)
    zwróć res

def _load(file, *, fix_imports=Prawda, encoding="ASCII", errors="strict"):
    zwróć _Unpickler(file, fix_imports=fix_imports,
                     encoding=encoding, errors=errors).load()

def _loads(s, *, fix_imports=Prawda, encoding="ASCII", errors="strict"):
    jeżeli isinstance(s, str):
        podnieś TypeError("Can't load pickle z unicode string")
    file = io.BytesIO(s)
    zwróć _Unpickler(file, fix_imports=fix_imports,
                      encoding=encoding, errors=errors).load()

# Use the faster _pickle jeżeli possible
spróbuj:
    z _pickle zaimportuj (
        PickleError,
        PicklingError,
        UnpicklingError,
        Pickler,
        Unpickler,
        dump,
        dumps,
        load,
        loads
    )
wyjąwszy ImportError:
    Pickler, Unpickler = _Pickler, _Unpickler
    dump, dumps, load, loads = _dump, _dumps, _load, _loads

# Doctest
def _test():
    zaimportuj doctest
    zwróć doctest.testmod()

jeżeli __name__ == "__main__":
    zaimportuj argparse
    parser = argparse.ArgumentParser(
        description='display contents of the pickle files')
    parser.add_argument(
        'pickle_file', type=argparse.FileType('br'),
        nargs='*', help='the pickle file')
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
        jeżeli nie args.pickle_file:
            parser.print_help()
        inaczej:
            zaimportuj pprint
            dla f w args.pickle_file:
                obj = load(f)
                pprint.pprint(obj)
