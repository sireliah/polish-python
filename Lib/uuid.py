r"""UUID objects (universally unique identifiers) according to RFC 4122.

This module provides immutable UUID objects (class UUID) oraz the functions
uuid1(), uuid3(), uuid4(), uuid5() dla generating version 1, 3, 4, oraz 5
UUIDs jako specified w RFC 4122.

If all you want jest a unique ID, you should probably call uuid1() albo uuid4().
Note that uuid1() may compromise privacy since it creates a UUID containing
the computer's network address.  uuid4() creates a random UUID.

Typical usage:

    >>> zaimportuj uuid

    # make a UUID based on the host ID oraz current time
    >>> uuid.uuid1()    # doctest: +SKIP
    UUID('a8098c1a-f86e-11da-bd1a-00112444be1e')

    # make a UUID using an MD5 hash of a namespace UUID oraz a name
    >>> uuid.uuid3(uuid.NAMESPACE_DNS, 'python.org')
    UUID('6fa459ea-ee8a-3ca4-894e-db77e160355e')

    # make a random UUID
    >>> uuid.uuid4()    # doctest: +SKIP
    UUID('16fd2706-8baf-433b-82eb-8c7fada847da')

    # make a UUID using a SHA-1 hash of a namespace UUID oraz a name
    >>> uuid.uuid5(uuid.NAMESPACE_DNS, 'python.org')
    UUID('886313e1-3b8a-5372-9b90-0c9aee199e5d')

    # make a UUID z a string of hex digits (braces oraz hyphens ignored)
    >>> x = uuid.UUID('{00010203-0405-0607-0809-0a0b0c0d0e0f}')

    # convert a UUID to a string of hex digits w standard form
    >>> str(x)
    '00010203-0405-0607-0809-0a0b0c0d0e0f'

    # get the raw 16 bytes of the UUID
    >>> x.bytes
    b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f'

    # make a UUID z a 16-byte string
    >>> uuid.UUID(bytes=x.bytes)
    UUID('00010203-0405-0607-0809-0a0b0c0d0e0f')
"""

__author__ = 'Ka-Ping Yee <ping@zesty.ca>'

RESERVED_NCS, RFC_4122, RESERVED_MICROSOFT, RESERVED_FUTURE = [
    'reserved dla NCS compatibility', 'specified w RFC 4122',
    'reserved dla Microsoft compatibility', 'reserved dla future definition']

int_ = int      # The built-in int type
bytes_ = bytes  # The built-in bytes type

klasa UUID(object):
    """Instances of the UUID klasa represent UUIDs jako specified w RFC 4122.
    UUID objects are immutable, hashable, oraz usable jako dictionary keys.
    Converting a UUID to a string przy str() uzyskajs something w the form
    '12345678-1234-1234-1234-123456789abc'.  The UUID constructor accepts
    five possible forms: a similar string of hexadecimal digits, albo a tuple
    of six integer fields (przy 32-bit, 16-bit, 16-bit, 8-bit, 8-bit, oraz
    48-bit values respectively) jako an argument named 'fields', albo a string
    of 16 bytes (przy all the integer fields w big-endian order) jako an
    argument named 'bytes', albo a string of 16 bytes (przy the first three
    fields w little-endian order) jako an argument named 'bytes_le', albo a
    single 128-bit integer jako an argument named 'int'.

    UUIDs have these read-only attributes:

        bytes       the UUID jako a 16-byte string (containing the six
                    integer fields w big-endian byte order)

        bytes_le    the UUID jako a 16-byte string (przy time_low, time_mid,
                    oraz time_hi_version w little-endian byte order)

        fields      a tuple of the six integer fields of the UUID,
                    which are also available jako six individual attributes
                    oraz two derived attributes:

            time_low                the first 32 bits of the UUID
            time_mid                the next 16 bits of the UUID
            time_hi_version         the next 16 bits of the UUID
            clock_seq_hi_variant    the next 8 bits of the UUID
            clock_seq_low           the next 8 bits of the UUID
            node                    the last 48 bits of the UUID

            time                    the 60-bit timestamp
            clock_seq               the 14-bit sequence number

        hex         the UUID jako a 32-character hexadecimal string

        int         the UUID jako a 128-bit integer

        urn         the UUID jako a URN jako specified w RFC 4122

        variant     the UUID variant (one of the constants RESERVED_NCS,
                    RFC_4122, RESERVED_MICROSOFT, albo RESERVED_FUTURE)

        version     the UUID version number (1 through 5, meaningful only
                    when the variant jest RFC_4122)
    """

    def __init__(self, hex=Nic, bytes=Nic, bytes_le=Nic, fields=Nic,
                       int=Nic, version=Nic):
        r"""Create a UUID z either a string of 32 hexadecimal digits,
        a string of 16 bytes jako the 'bytes' argument, a string of 16 bytes
        w little-endian order jako the 'bytes_le' argument, a tuple of six
        integers (32-bit time_low, 16-bit time_mid, 16-bit time_hi_version,
        8-bit clock_seq_hi_variant, 8-bit clock_seq_low, 48-bit node) as
        the 'fields' argument, albo a single 128-bit integer jako the 'int'
        argument.  When a string of hex digits jest given, curly braces,
        hyphens, oraz a URN prefix are all optional.  For example, these
        expressions all uzyskaj the same UUID:

        UUID('{12345678-1234-5678-1234-567812345678}')
        UUID('12345678123456781234567812345678')
        UUID('urn:uuid:12345678-1234-5678-1234-567812345678')
        UUID(bytes='\x12\x34\x56\x78'*4)
        UUID(bytes_le='\x78\x56\x34\x12\x34\x12\x78\x56' +
                      '\x12\x34\x56\x78\x12\x34\x56\x78')
        UUID(fields=(0x12345678, 0x1234, 0x5678, 0x12, 0x34, 0x567812345678))
        UUID(int=0x12345678123456781234567812345678)

        Exactly one of 'hex', 'bytes', 'bytes_le', 'fields', albo 'int' must
        be given.  The 'version' argument jest optional; jeżeli given, the resulting
        UUID will have its variant oraz version set according to RFC 4122,
        overriding the given 'hex', 'bytes', 'bytes_le', 'fields', albo 'int'.
        """

        jeżeli [hex, bytes, bytes_le, fields, int].count(Nic) != 4:
            podnieś TypeError('need one of hex, bytes, bytes_le, fields, albo int')
        jeżeli hex jest nie Nic:
            hex = hex.replace('urn:', '').replace('uuid:', '')
            hex = hex.strip('{}').replace('-', '')
            jeżeli len(hex) != 32:
                podnieś ValueError('badly formed hexadecimal UUID string')
            int = int_(hex, 16)
        jeżeli bytes_le jest nie Nic:
            jeżeli len(bytes_le) != 16:
                podnieś ValueError('bytes_le jest nie a 16-char string')
            bytes = (bytes_le[4-1::-1] + bytes_le[6-1:4-1:-1] +
                     bytes_le[8-1:6-1:-1] + bytes_le[8:])
        jeżeli bytes jest nie Nic:
            jeżeli len(bytes) != 16:
                podnieś ValueError('bytes jest nie a 16-char string')
            assert isinstance(bytes, bytes_), repr(bytes)
            int = int_.from_bytes(bytes, byteorder='big')
        jeżeli fields jest nie Nic:
            jeżeli len(fields) != 6:
                podnieś ValueError('fields jest nie a 6-tuple')
            (time_low, time_mid, time_hi_version,
             clock_seq_hi_variant, clock_seq_low, node) = fields
            jeżeli nie 0 <= time_low < 1<<32:
                podnieś ValueError('field 1 out of range (need a 32-bit value)')
            jeżeli nie 0 <= time_mid < 1<<16:
                podnieś ValueError('field 2 out of range (need a 16-bit value)')
            jeżeli nie 0 <= time_hi_version < 1<<16:
                podnieś ValueError('field 3 out of range (need a 16-bit value)')
            jeżeli nie 0 <= clock_seq_hi_variant < 1<<8:
                podnieś ValueError('field 4 out of range (need an 8-bit value)')
            jeżeli nie 0 <= clock_seq_low < 1<<8:
                podnieś ValueError('field 5 out of range (need an 8-bit value)')
            jeżeli nie 0 <= node < 1<<48:
                podnieś ValueError('field 6 out of range (need a 48-bit value)')
            clock_seq = (clock_seq_hi_variant << 8) | clock_seq_low
            int = ((time_low << 96) | (time_mid << 80) |
                   (time_hi_version << 64) | (clock_seq << 48) | node)
        jeżeli int jest nie Nic:
            jeżeli nie 0 <= int < 1<<128:
                podnieś ValueError('int jest out of range (need a 128-bit value)')
        jeżeli version jest nie Nic:
            jeżeli nie 1 <= version <= 5:
                podnieś ValueError('illegal version number')
            # Set the variant to RFC 4122.
            int &= ~(0xc000 << 48)
            int |= 0x8000 << 48
            # Set the version number.
            int &= ~(0xf000 << 64)
            int |= version << 76
        self.__dict__['int'] = int

    def __eq__(self, other):
        jeżeli isinstance(other, UUID):
            zwróć self.int == other.int
        zwróć NotImplemented

    # Q. What's the value of being able to sort UUIDs?
    # A. Use them jako keys w a B-Tree albo similar mapping.

    def __lt__(self, other):
        jeżeli isinstance(other, UUID):
            zwróć self.int < other.int
        zwróć NotImplemented

    def __gt__(self, other):
        jeżeli isinstance(other, UUID):
            zwróć self.int > other.int
        zwróć NotImplemented

    def __le__(self, other):
        jeżeli isinstance(other, UUID):
            zwróć self.int <= other.int
        zwróć NotImplemented

    def __ge__(self, other):
        jeżeli isinstance(other, UUID):
            zwróć self.int >= other.int
        zwróć NotImplemented

    def __hash__(self):
        zwróć hash(self.int)

    def __int__(self):
        zwróć self.int

    def __repr__(self):
        zwróć '%s(%r)' % (self.__class__.__name__, str(self))

    def __setattr__(self, name, value):
        podnieś TypeError('UUID objects are immutable')

    def __str__(self):
        hex = '%032x' % self.int
        zwróć '%s-%s-%s-%s-%s' % (
            hex[:8], hex[8:12], hex[12:16], hex[16:20], hex[20:])

    @property
    def bytes(self):
        zwróć self.int.to_bytes(16, 'big')

    @property
    def bytes_le(self):
        bytes = self.bytes
        zwróć (bytes[4-1::-1] + bytes[6-1:4-1:-1] + bytes[8-1:6-1:-1] +
                bytes[8:])

    @property
    def fields(self):
        zwróć (self.time_low, self.time_mid, self.time_hi_version,
                self.clock_seq_hi_variant, self.clock_seq_low, self.node)

    @property
    def time_low(self):
        zwróć self.int >> 96

    @property
    def time_mid(self):
        zwróć (self.int >> 80) & 0xffff

    @property
    def time_hi_version(self):
        zwróć (self.int >> 64) & 0xffff

    @property
    def clock_seq_hi_variant(self):
        zwróć (self.int >> 56) & 0xff

    @property
    def clock_seq_low(self):
        zwróć (self.int >> 48) & 0xff

    @property
    def time(self):
        zwróć (((self.time_hi_version & 0x0fff) << 48) |
                (self.time_mid << 32) | self.time_low)

    @property
    def clock_seq(self):
        zwróć (((self.clock_seq_hi_variant & 0x3f) << 8) |
                self.clock_seq_low)

    @property
    def node(self):
        zwróć self.int & 0xffffffffffff

    @property
    def hex(self):
        zwróć '%032x' % self.int

    @property
    def urn(self):
        zwróć 'urn:uuid:' + str(self)

    @property
    def variant(self):
        jeżeli nie self.int & (0x8000 << 48):
            zwróć RESERVED_NCS
        albo_inaczej nie self.int & (0x4000 << 48):
            zwróć RFC_4122
        albo_inaczej nie self.int & (0x2000 << 48):
            zwróć RESERVED_MICROSOFT
        inaczej:
            zwróć RESERVED_FUTURE

    @property
    def version(self):
        # The version bits are only meaningful dla RFC 4122 UUIDs.
        jeżeli self.variant == RFC_4122:
            zwróć int((self.int >> 76) & 0xf)

def _popen(command, *args):
    zaimportuj os, shutil, subprocess
    executable = shutil.which(command)
    jeżeli executable jest Nic:
        path = os.pathsep.join(('/sbin', '/usr/sbin'))
        executable = shutil.which(command, path=path)
        jeżeli executable jest Nic:
            zwróć Nic
    # LC_ALL=C to ensure English output, stderr=DEVNULL to prevent output
    # on stderr (Note: we don't have an example where the words we search
    # dla are actually localized, but w theory some system could do so.)
    env = dict(os.environ)
    env['LC_ALL'] = 'C'
    proc = subprocess.Popen((executable,) + args,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL,
                            env=env)
    zwróć proc

def _find_mac(command, args, hw_identifiers, get_index):
    spróbuj:
        proc = _popen(command, *args.split())
        jeżeli nie proc:
            zwróć
        przy proc:
            dla line w proc.stdout:
                words = line.lower().rstrip().split()
                dla i w range(len(words)):
                    jeżeli words[i] w hw_identifiers:
                        spróbuj:
                            word = words[get_index(i)]
                            mac = int(word.replace(b':', b''), 16)
                            jeżeli mac:
                                zwróć mac
                        wyjąwszy (ValueError, IndexError):
                            # Virtual interfaces, such jako those provided by
                            # VPNs, do nie have a colon-delimited MAC address
                            # jako expected, but a 16-byte HWAddr separated by
                            # dashes. These should be ignored w favor of a
                            # real MAC address
                            dalej
    wyjąwszy OSError:
        dalej

def _ifconfig_getnode():
    """Get the hardware address on Unix by running ifconfig."""
    # This works on Linux ('' albo '-a'), Tru64 ('-av'), but nie all Unixes.
    dla args w ('', '-a', '-av'):
        mac = _find_mac('ifconfig', args, [b'hwaddr', b'ether'], lambda i: i+1)
        jeżeli mac:
            zwróć mac

def _ip_getnode():
    """Get the hardware address on Unix by running ip."""
    # This works on Linux przy iproute2.
    mac = _find_mac('ip', 'link list', [b'link/ether'], lambda i: i+1)
    jeżeli mac:
        zwróć mac

def _arp_getnode():
    """Get the hardware address on Unix by running arp."""
    zaimportuj os, socket
    spróbuj:
        ip_addr = socket.gethostbyname(socket.gethostname())
    wyjąwszy OSError:
        zwróć Nic

    # Try getting the MAC addr z arp based on our IP address (Solaris).
    zwróć _find_mac('arp', '-an', [os.fsencode(ip_addr)], lambda i: -1)

def _lanscan_getnode():
    """Get the hardware address on Unix by running lanscan."""
    # This might work on HP-UX.
    zwróć _find_mac('lanscan', '-ai', [b'lan0'], lambda i: 0)

def _netstat_getnode():
    """Get the hardware address on Unix by running netstat."""
    # This might work on AIX, Tru64 UNIX oraz presumably on IRIX.
    spróbuj:
        proc = _popen('netstat', '-ia')
        jeżeli nie proc:
            zwróć
        przy proc:
            words = proc.stdout.readline().rstrip().split()
            spróbuj:
                i = words.index(b'Address')
            wyjąwszy ValueError:
                zwróć
            dla line w proc.stdout:
                spróbuj:
                    words = line.rstrip().split()
                    word = words[i]
                    jeżeli len(word) == 17 oraz word.count(b':') == 5:
                        mac = int(word.replace(b':', b''), 16)
                        jeżeli mac:
                            zwróć mac
                wyjąwszy (ValueError, IndexError):
                    dalej
    wyjąwszy OSError:
        dalej

def _ipconfig_getnode():
    """Get the hardware address on Windows by running ipconfig.exe."""
    zaimportuj os, re
    dirs = ['', r'c:\windows\system32', r'c:\winnt\system32']
    spróbuj:
        zaimportuj ctypes
        buffer = ctypes.create_string_buffer(300)
        ctypes.windll.kernel32.GetSystemDirectoryA(buffer, 300)
        dirs.insert(0, buffer.value.decode('mbcs'))
    wyjąwszy:
        dalej
    dla dir w dirs:
        spróbuj:
            pipe = os.popen(os.path.join(dir, 'ipconfig') + ' /all')
        wyjąwszy OSError:
            kontynuuj
        przy pipe:
            dla line w pipe:
                value = line.split(':')[-1].strip().lower()
                jeżeli re.match('([0-9a-f][0-9a-f]-){5}[0-9a-f][0-9a-f]', value):
                    zwróć int(value.replace('-', ''), 16)

def _netbios_getnode():
    """Get the hardware address on Windows using NetBIOS calls.
    See http://support.microsoft.com/kb/118623 dla details."""
    zaimportuj win32wnet, netbios
    ncb = netbios.NCB()
    ncb.Command = netbios.NCBENUM
    ncb.Buffer = adapters = netbios.LANA_ENUM()
    adapters._pack()
    jeżeli win32wnet.Netbios(ncb) != 0:
        zwróć
    adapters._unpack()
    dla i w range(adapters.length):
        ncb.Reset()
        ncb.Command = netbios.NCBRESET
        ncb.Lana_num = ord(adapters.lana[i])
        jeżeli win32wnet.Netbios(ncb) != 0:
            kontynuuj
        ncb.Reset()
        ncb.Command = netbios.NCBASTAT
        ncb.Lana_num = ord(adapters.lana[i])
        ncb.Callname = '*'.ljust(16)
        ncb.Buffer = status = netbios.ADAPTER_STATUS()
        jeżeli win32wnet.Netbios(ncb) != 0:
            kontynuuj
        status._unpack()
        bytes = status.adapter_address[:6]
        jeżeli len(bytes) != 6:
            kontynuuj
        zwróć int.from_bytes(bytes, 'big')

# Thanks to Thomas Heller dla ctypes oraz dla his help przy its use here.

# If ctypes jest available, use it to find system routines dla UUID generation.
# XXX This makes the module non-thread-safe!
_uuid_generate_random = _uuid_generate_time = _UuidCreate = Nic
spróbuj:
    zaimportuj ctypes, ctypes.util
    zaimportuj sys

    # The uuid_generate_* routines are provided by libuuid on at least
    # Linux oraz FreeBSD, oraz provided by libc on Mac OS X.
    _libnames = ['uuid']
    jeżeli nie sys.platform.startswith('win'):
        _libnames.append('c')
    dla libname w _libnames:
        spróbuj:
            lib = ctypes.CDLL(ctypes.util.find_library(libname))
        wyjąwszy Exception:
            kontynuuj
        jeżeli hasattr(lib, 'uuid_generate_random'):
            _uuid_generate_random = lib.uuid_generate_random
        jeżeli hasattr(lib, 'uuid_generate_time'):
            _uuid_generate_time = lib.uuid_generate_time
            jeżeli _uuid_generate_random jest nie Nic:
                przerwij  # found everything we were looking for
    usuń _libnames

    # The uuid_generate_* functions are broken on MacOS X 10.5, jako noted
    # w issue #8621 the function generates the same sequence of values
    # w the parent process oraz all children created using fork (unless
    # those children use exec jako well).
    #
    # Assume that the uuid_generate functions are broken z 10.5 onward,
    # the test can be adjusted when a later version jest fixed.
    jeżeli sys.platform == 'darwin':
        zaimportuj os
        jeżeli int(os.uname().release.split('.')[0]) >= 9:
            _uuid_generate_random = _uuid_generate_time = Nic

    # On Windows prior to 2000, UuidCreate gives a UUID containing the
    # hardware address.  On Windows 2000 oraz later, UuidCreate makes a
    # random UUID oraz UuidCreateSequential gives a UUID containing the
    # hardware address.  These routines are provided by the RPC runtime.
    # NOTE:  at least on Tim's WinXP Pro SP2 desktop box, dopóki the last
    # 6 bytes returned by UuidCreateSequential are fixed, they don't appear
    # to bear any relationship to the MAC address of any network device
    # on the box.
    spróbuj:
        lib = ctypes.windll.rpcrt4
    wyjąwszy:
        lib = Nic
    _UuidCreate = getattr(lib, 'UuidCreateSequential',
                          getattr(lib, 'UuidCreate', Nic))
wyjąwszy:
    dalej

def _unixdll_getnode():
    """Get the hardware address on Unix using ctypes."""
    _buffer = ctypes.create_string_buffer(16)
    _uuid_generate_time(_buffer)
    zwróć UUID(bytes=bytes_(_buffer.raw)).node

def _windll_getnode():
    """Get the hardware address on Windows using ctypes."""
    _buffer = ctypes.create_string_buffer(16)
    jeżeli _UuidCreate(_buffer) == 0:
        zwróć UUID(bytes=bytes_(_buffer.raw)).node

def _random_getnode():
    """Get a random node ID, przy eighth bit set jako suggested by RFC 4122."""
    zaimportuj random
    zwróć random.getrandbits(48) | 0x010000000000

_node = Nic

def getnode():
    """Get the hardware address jako a 48-bit positive integer.

    The first time this runs, it may launch a separate program, which could
    be quite slow.  If all attempts to obtain the hardware address fail, we
    choose a random 48-bit number przy its eighth bit set to 1 jako recommended
    w RFC 4122.
    """

    global _node
    jeżeli _node jest nie Nic:
        zwróć _node

    zaimportuj sys
    jeżeli sys.platform == 'win32':
        getters = [_windll_getnode, _netbios_getnode, _ipconfig_getnode]
    inaczej:
        getters = [_unixdll_getnode, _ifconfig_getnode, _ip_getnode,
                   _arp_getnode, _lanscan_getnode, _netstat_getnode]

    dla getter w getters + [_random_getnode]:
        spróbuj:
            _node = getter()
        wyjąwszy:
            kontynuuj
        jeżeli _node jest nie Nic:
            zwróć _node

_last_timestamp = Nic

def uuid1(node=Nic, clock_seq=Nic):
    """Generate a UUID z a host ID, sequence number, oraz the current time.
    If 'node' jest nie given, getnode() jest used to obtain the hardware
    address.  If 'clock_seq' jest given, it jest used jako the sequence number;
    otherwise a random 14-bit sequence number jest chosen."""

    # When the system provides a version-1 UUID generator, use it (but don't
    # use UuidCreate here because its UUIDs don't conform to RFC 4122).
    jeżeli _uuid_generate_time oraz node jest clock_seq jest Nic:
        _buffer = ctypes.create_string_buffer(16)
        _uuid_generate_time(_buffer)
        zwróć UUID(bytes=bytes_(_buffer.raw))

    global _last_timestamp
    zaimportuj time
    nanoseconds = int(time.time() * 1e9)
    # 0x01b21dd213814000 jest the number of 100-ns intervals between the
    # UUID epoch 1582-10-15 00:00:00 oraz the Unix epoch 1970-01-01 00:00:00.
    timestamp = int(nanoseconds/100) + 0x01b21dd213814000
    jeżeli _last_timestamp jest nie Nic oraz timestamp <= _last_timestamp:
        timestamp = _last_timestamp + 1
    _last_timestamp = timestamp
    jeżeli clock_seq jest Nic:
        zaimportuj random
        clock_seq = random.getrandbits(14) # instead of stable storage
    time_low = timestamp & 0xffffffff
    time_mid = (timestamp >> 32) & 0xffff
    time_hi_version = (timestamp >> 48) & 0x0fff
    clock_seq_low = clock_seq & 0xff
    clock_seq_hi_variant = (clock_seq >> 8) & 0x3f
    jeżeli node jest Nic:
        node = getnode()
    zwróć UUID(fields=(time_low, time_mid, time_hi_version,
                        clock_seq_hi_variant, clock_seq_low, node), version=1)

def uuid3(namespace, name):
    """Generate a UUID z the MD5 hash of a namespace UUID oraz a name."""
    z hashlib zaimportuj md5
    hash = md5(namespace.bytes + bytes(name, "utf-8")).digest()
    zwróć UUID(bytes=hash[:16], version=3)

def uuid4():
    """Generate a random UUID."""

    # When the system provides a version-4 UUID generator, use it.
    jeżeli _uuid_generate_random:
        _buffer = ctypes.create_string_buffer(16)
        _uuid_generate_random(_buffer)
        zwróć UUID(bytes=bytes_(_buffer.raw))

    # Otherwise, get randomness z urandom albo the 'random' module.
    spróbuj:
        zaimportuj os
        zwróć UUID(bytes=os.urandom(16), version=4)
    wyjąwszy Exception:
        zaimportuj random
        zwróć UUID(int=random.getrandbits(128), version=4)

def uuid5(namespace, name):
    """Generate a UUID z the SHA-1 hash of a namespace UUID oraz a name."""
    z hashlib zaimportuj sha1
    hash = sha1(namespace.bytes + bytes(name, "utf-8")).digest()
    zwróć UUID(bytes=hash[:16], version=5)

# The following standard UUIDs are dla use przy uuid3() albo uuid5().

NAMESPACE_DNS = UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
NAMESPACE_URL = UUID('6ba7b811-9dad-11d1-80b4-00c04fd430c8')
NAMESPACE_OID = UUID('6ba7b812-9dad-11d1-80b4-00c04fd430c8')
NAMESPACE_X500 = UUID('6ba7b814-9dad-11d1-80b4-00c04fd430c8')
