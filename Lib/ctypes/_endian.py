zaimportuj sys
z ctypes zaimportuj *

_array_type = type(Array)

def _other_endian(typ):
    """Return the type przy the 'other' byte order.  Simple types like
    c_int oraz so on already have __ctype_be__ oraz __ctype_le__
    attributes which contain the types, dla more complicated types
    arrays oraz structures are supported.
    """
    # check _OTHER_ENDIAN attribute (present jeżeli typ jest primitive type)
    jeżeli hasattr(typ, _OTHER_ENDIAN):
        zwróć getattr(typ, _OTHER_ENDIAN)
    # jeżeli typ jest array
    jeżeli isinstance(typ, _array_type):
        zwróć _other_endian(typ._type_) * typ._length_
    # jeżeli typ jest structure
    jeżeli issubclass(typ, Structure):
        zwróć typ
    podnieś TypeError("This type does nie support other endian: %s" % typ)

klasa _swapped_meta(type(Structure)):
    def __setattr__(self, attrname, value):
        jeżeli attrname == "_fields_":
            fields = []
            dla desc w value:
                name = desc[0]
                typ = desc[1]
                rest = desc[2:]
                fields.append((name, _other_endian(typ)) + rest)
            value = fields
        super().__setattr__(attrname, value)

################################################################

# Note: The Structure metaclass checks dla the *presence* (nie the
# value!) of a _swapped_bytes_ attribute to determine the bit order w
# structures containing bit fields.

jeżeli sys.byteorder == "little":
    _OTHER_ENDIAN = "__ctype_be__"

    LittleEndianStructure = Structure

    klasa BigEndianStructure(Structure, metaclass=_swapped_meta):
        """Structure przy big endian byte order"""
        __slots__ = ()
        _swappedbytes_ = Nic

albo_inaczej sys.byteorder == "big":
    _OTHER_ENDIAN = "__ctype_le__"

    BigEndianStructure = Structure
    klasa LittleEndianStructure(Structure, metaclass=_swapped_meta):
        """Structure przy little endian byte order"""
        __slots__ = ()
        _swappedbytes_ = Nic

inaczej:
    podnieś RuntimeError("Invalid byteorder")
