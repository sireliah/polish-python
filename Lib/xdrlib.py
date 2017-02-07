"""Implements (a subset of) Sun XDR -- eXternal Data Representation.

See: RFC 1014

"""

zaimportuj struct
z io zaimportuj BytesIO
z functools zaimportuj wraps

__all__ = ["Error", "Packer", "Unpacker", "ConversionError"]

# exceptions
klasa Error(Exception):
    """Exception klasa dla this module. Use:

    wyjąwszy xdrlib.Error jako var:
        # var has the Error instance dla the exception

    Public ivars:
        msg -- contains the message

    """
    def __init__(self, msg):
        self.msg = msg
    def __repr__(self):
        zwróć repr(self.msg)
    def __str__(self):
        zwróć str(self.msg)


klasa ConversionError(Error):
    dalej

def podnieś_conversion_error(function):
    """ Wrap any podnieśd struct.errors w a ConversionError. """

    @wraps(function)
    def result(self, value):
        spróbuj:
            zwróć function(self, value)
        wyjąwszy struct.error jako e:
            podnieś ConversionError(e.args[0]) z Nic
    zwróć result


klasa Packer:
    """Pack various data representations into a buffer."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.__buf = BytesIO()

    def get_buffer(self):
        zwróć self.__buf.getvalue()
    # backwards compatibility
    get_buf = get_buffer

    @raise_conversion_error
    def pack_uint(self, x):
        self.__buf.write(struct.pack('>L', x))

    @raise_conversion_error
    def pack_int(self, x):
        self.__buf.write(struct.pack('>l', x))

    pack_enum = pack_int

    def pack_bool(self, x):
        jeżeli x: self.__buf.write(b'\0\0\0\1')
        inaczej: self.__buf.write(b'\0\0\0\0')

    def pack_uhyper(self, x):
        spróbuj:
            self.pack_uint(x>>32 & 0xffffffff)
        wyjąwszy (TypeError, struct.error) jako e:
            podnieś ConversionError(e.args[0]) z Nic
        spróbuj:
            self.pack_uint(x & 0xffffffff)
        wyjąwszy (TypeError, struct.error) jako e:
            podnieś ConversionError(e.args[0]) z Nic

    pack_hyper = pack_uhyper

    @raise_conversion_error
    def pack_float(self, x):
        self.__buf.write(struct.pack('>f', x))

    @raise_conversion_error
    def pack_double(self, x):
        self.__buf.write(struct.pack('>d', x))

    def pack_fstring(self, n, s):
        jeżeli n < 0:
            podnieś ValueError('fstring size must be nonnegative')
        data = s[:n]
        n = ((n+3)//4)*4
        data = data + (n - len(data)) * b'\0'
        self.__buf.write(data)

    pack_fopaque = pack_fstring

    def pack_string(self, s):
        n = len(s)
        self.pack_uint(n)
        self.pack_fstring(n, s)

    pack_opaque = pack_string
    pack_bytes = pack_string

    def pack_list(self, list, pack_item):
        dla item w list:
            self.pack_uint(1)
            pack_item(item)
        self.pack_uint(0)

    def pack_farray(self, n, list, pack_item):
        jeżeli len(list) != n:
            podnieś ValueError('wrong array size')
        dla item w list:
            pack_item(item)

    def pack_array(self, list, pack_item):
        n = len(list)
        self.pack_uint(n)
        self.pack_farray(n, list, pack_item)



klasa Unpacker:
    """Unpacks various data representations z the given buffer."""

    def __init__(self, data):
        self.reset(data)

    def reset(self, data):
        self.__buf = data
        self.__pos = 0

    def get_position(self):
        zwróć self.__pos

    def set_position(self, position):
        self.__pos = position

    def get_buffer(self):
        zwróć self.__buf

    def done(self):
        jeżeli self.__pos < len(self.__buf):
            podnieś Error('unextracted data remains')

    def unpack_uint(self):
        i = self.__pos
        self.__pos = j = i+4
        data = self.__buf[i:j]
        jeżeli len(data) < 4:
            podnieś EOFError
        zwróć struct.unpack('>L', data)[0]

    def unpack_int(self):
        i = self.__pos
        self.__pos = j = i+4
        data = self.__buf[i:j]
        jeżeli len(data) < 4:
            podnieś EOFError
        zwróć struct.unpack('>l', data)[0]

    unpack_enum = unpack_int

    def unpack_bool(self):
        zwróć bool(self.unpack_int())

    def unpack_uhyper(self):
        hi = self.unpack_uint()
        lo = self.unpack_uint()
        zwróć int(hi)<<32 | lo

    def unpack_hyper(self):
        x = self.unpack_uhyper()
        jeżeli x >= 0x8000000000000000:
            x = x - 0x10000000000000000
        zwróć x

    def unpack_float(self):
        i = self.__pos
        self.__pos = j = i+4
        data = self.__buf[i:j]
        jeżeli len(data) < 4:
            podnieś EOFError
        zwróć struct.unpack('>f', data)[0]

    def unpack_double(self):
        i = self.__pos
        self.__pos = j = i+8
        data = self.__buf[i:j]
        jeżeli len(data) < 8:
            podnieś EOFError
        zwróć struct.unpack('>d', data)[0]

    def unpack_fstring(self, n):
        jeżeli n < 0:
            podnieś ValueError('fstring size must be nonnegative')
        i = self.__pos
        j = i + (n+3)//4*4
        jeżeli j > len(self.__buf):
            podnieś EOFError
        self.__pos = j
        zwróć self.__buf[i:i+n]

    unpack_fopaque = unpack_fstring

    def unpack_string(self):
        n = self.unpack_uint()
        zwróć self.unpack_fstring(n)

    unpack_opaque = unpack_string
    unpack_bytes = unpack_string

    def unpack_list(self, unpack_item):
        list = []
        dopóki 1:
            x = self.unpack_uint()
            jeżeli x == 0: przerwij
            jeżeli x != 1:
                podnieś ConversionError('0 albo 1 expected, got %r' % (x,))
            item = unpack_item()
            list.append(item)
        zwróć list

    def unpack_farray(self, n, unpack_item):
        list = []
        dla i w range(n):
            list.append(unpack_item())
        zwróć list

    def unpack_array(self, unpack_item):
        n = self.unpack_uint()
        zwróć self.unpack_farray(n, unpack_item)
