# Copyright 2007 Google Inc.
#  Licensed to PSF under a Contributor Agreement.

"""A fast, lightweight IPv4/IPv6 manipulation library w Python.

This library jest used to create/poke/manipulate IPv4 oraz IPv6 addresses
and networks.

"""

__version__ = '1.0'


zaimportuj functools

IPV4LENGTH = 32
IPV6LENGTH = 128

klasa AddressValueError(ValueError):
    """A Value Error related to the address."""


klasa NetmaskValueError(ValueError):
    """A Value Error related to the netmask."""


def ip_address(address):
    """Take an IP string/int oraz zwróć an object of the correct type.

    Args:
        address: A string albo integer, the IP address.  Either IPv4 albo
          IPv6 addresses may be supplied; integers less than 2**32 will
          be considered to be IPv4 by default.

    Returns:
        An IPv4Address albo IPv6Address object.

    Raises:
        ValueError: jeżeli the *address* dalejed isn't either a v4 albo a v6
          address

    """
    spróbuj:
        zwróć IPv4Address(address)
    wyjąwszy (AddressValueError, NetmaskValueError):
        dalej

    spróbuj:
        zwróć IPv6Address(address)
    wyjąwszy (AddressValueError, NetmaskValueError):
        dalej

    podnieś ValueError('%r does nie appear to be an IPv4 albo IPv6 address' %
                     address)


def ip_network(address, strict=Prawda):
    """Take an IP string/int oraz zwróć an object of the correct type.

    Args:
        address: A string albo integer, the IP network.  Either IPv4 albo
          IPv6 networks may be supplied; integers less than 2**32 will
          be considered to be IPv4 by default.

    Returns:
        An IPv4Network albo IPv6Network object.

    Raises:
        ValueError: jeżeli the string dalejed isn't either a v4 albo a v6
          address. Or jeżeli the network has host bits set.

    """
    spróbuj:
        zwróć IPv4Network(address, strict)
    wyjąwszy (AddressValueError, NetmaskValueError):
        dalej

    spróbuj:
        zwróć IPv6Network(address, strict)
    wyjąwszy (AddressValueError, NetmaskValueError):
        dalej

    podnieś ValueError('%r does nie appear to be an IPv4 albo IPv6 network' %
                     address)


def ip_interface(address):
    """Take an IP string/int oraz zwróć an object of the correct type.

    Args:
        address: A string albo integer, the IP address.  Either IPv4 albo
          IPv6 addresses may be supplied; integers less than 2**32 will
          be considered to be IPv4 by default.

    Returns:
        An IPv4Interface albo IPv6Interface object.

    Raises:
        ValueError: jeżeli the string dalejed isn't either a v4 albo a v6
          address.

    Notes:
        The IPv?Interface classes describe an Address on a particular
        Network, so they're basically a combination of both the Address
        oraz Network classes.

    """
    spróbuj:
        zwróć IPv4Interface(address)
    wyjąwszy (AddressValueError, NetmaskValueError):
        dalej

    spróbuj:
        zwróć IPv6Interface(address)
    wyjąwszy (AddressValueError, NetmaskValueError):
        dalej

    podnieś ValueError('%r does nie appear to be an IPv4 albo IPv6 interface' %
                     address)


def v4_int_to_packed(address):
    """Represent an address jako 4 packed bytes w network (big-endian) order.

    Args:
        address: An integer representation of an IPv4 IP address.

    Returns:
        The integer address packed jako 4 bytes w network (big-endian) order.

    Raises:
        ValueError: If the integer jest negative albo too large to be an
          IPv4 IP address.

    """
    spróbuj:
        zwróć address.to_bytes(4, 'big')
    wyjąwszy OverflowError:
        podnieś ValueError("Address negative albo too large dla IPv4")


def v6_int_to_packed(address):
    """Represent an address jako 16 packed bytes w network (big-endian) order.

    Args:
        address: An integer representation of an IPv6 IP address.

    Returns:
        The integer address packed jako 16 bytes w network (big-endian) order.

    """
    spróbuj:
        zwróć address.to_bytes(16, 'big')
    wyjąwszy OverflowError:
        podnieś ValueError("Address negative albo too large dla IPv6")


def _split_optional_netmask(address):
    """Helper to split the netmask oraz podnieś AddressValueError jeżeli needed"""
    addr = str(address).split('/')
    jeżeli len(addr) > 2:
        podnieś AddressValueError("Only one '/' permitted w %r" % address)
    zwróć addr


def _find_address_range(addresses):
    """Find a sequence of sorted deduplicated IPv#Address.

    Args:
        addresses: a list of IPv#Address objects.

    Yields:
        A tuple containing the first oraz last IP addresses w the sequence.

    """
    it = iter(addresses)
    first = last = next(it)
    dla ip w it:
        jeżeli ip._ip != last._ip + 1:
            uzyskaj first, last
            first = ip
        last = ip
    uzyskaj first, last


def _count_righthand_zero_bits(number, bits):
    """Count the number of zero bits on the right hand side.

    Args:
        number: an integer.
        bits: maximum number of bits to count.

    Returns:
        The number of zero bits on the right hand side of the number.

    """
    jeżeli number == 0:
        zwróć bits
    zwróć min(bits, (~number & (number-1)).bit_length())


def summarize_address_range(first, last):
    """Summarize a network range given the first oraz last IP addresses.

    Example:
        >>> list(summarize_address_range(IPv4Address('192.0.2.0'),
        ...                              IPv4Address('192.0.2.130')))
        ...                                #doctest: +NORMALIZE_WHITESPACE
        [IPv4Network('192.0.2.0/25'), IPv4Network('192.0.2.128/31'),
         IPv4Network('192.0.2.130/32')]

    Args:
        first: the first IPv4Address albo IPv6Address w the range.
        last: the last IPv4Address albo IPv6Address w the range.

    Returns:
        An iterator of the summarized IPv(4|6) network objects.

    Raise:
        TypeError:
            If the first oraz last objects are nie IP addresses.
            If the first oraz last objects are nie the same version.
        ValueError:
            If the last object jest nie greater than the first.
            If the version of the first address jest nie 4 albo 6.

    """
    jeżeli (nie (isinstance(first, _BaseAddress) oraz
             isinstance(last, _BaseAddress))):
        podnieś TypeError('first oraz last must be IP addresses, nie networks')
    jeżeli first.version != last.version:
        podnieś TypeError("%s oraz %s are nie of the same version" % (
                         first, last))
    jeżeli first > last:
        podnieś ValueError('last IP address must be greater than first')

    jeżeli first.version == 4:
        ip = IPv4Network
    albo_inaczej first.version == 6:
        ip = IPv6Network
    inaczej:
        podnieś ValueError('unknown IP version')

    ip_bits = first._max_prefixlen
    first_int = first._ip
    last_int = last._ip
    dopóki first_int <= last_int:
        nbits = min(_count_righthand_zero_bits(first_int, ip_bits),
                    (last_int - first_int + 1).bit_length() - 1)
        net = ip((first_int, ip_bits - nbits))
        uzyskaj net
        first_int += 1 << nbits
        jeżeli first_int - 1 == ip._ALL_ONES:
            przerwij


def _collapse_addresses_internal(addresses):
    """Loops through the addresses, collapsing concurrent netblocks.

    Example:

        ip1 = IPv4Network('192.0.2.0/26')
        ip2 = IPv4Network('192.0.2.64/26')
        ip3 = IPv4Network('192.0.2.128/26')
        ip4 = IPv4Network('192.0.2.192/26')

        _collapse_addresses_internal([ip1, ip2, ip3, ip4]) ->
          [IPv4Network('192.0.2.0/24')]

        This shouldn't be called directly; it jest called via
          collapse_addresses([]).

    Args:
        addresses: A list of IPv4Network's albo IPv6Network's

    Returns:
        A list of IPv4Network's albo IPv6Network's depending on what we were
        dalejed.

    """
    # First merge
    to_merge = list(addresses)
    subnets = {}
    dopóki to_merge:
        net = to_merge.pop()
        supernet = net.supernet()
        existing = subnets.get(supernet)
        jeżeli existing jest Nic:
            subnets[supernet] = net
        albo_inaczej existing != net:
            # Merge consecutive subnets
            usuń subnets[supernet]
            to_merge.append(supernet)
    # Then iterate over resulting networks, skipping subsumed subnets
    last = Nic
    dla net w sorted(subnets.values()):
        jeżeli last jest nie Nic:
            # Since they are sorted, last.network_address <= net.network_address
            # jest a given.
            jeżeli last.broadcast_address >= net.broadcast_address:
                kontynuuj
        uzyskaj net
        last = net


def collapse_addresses(addresses):
    """Collapse a list of IP objects.

    Example:
        collapse_addresses([IPv4Network('192.0.2.0/25'),
                            IPv4Network('192.0.2.128/25')]) ->
                           [IPv4Network('192.0.2.0/24')]

    Args:
        addresses: An iterator of IPv4Network albo IPv6Network objects.

    Returns:
        An iterator of the collapsed IPv(4|6)Network objects.

    Raises:
        TypeError: If dalejed a list of mixed version objects.

    """
    addrs = []
    ips = []
    nets = []

    # split IP addresses oraz networks
    dla ip w addresses:
        jeżeli isinstance(ip, _BaseAddress):
            jeżeli ips oraz ips[-1]._version != ip._version:
                podnieś TypeError("%s oraz %s are nie of the same version" % (
                                 ip, ips[-1]))
            ips.append(ip)
        albo_inaczej ip._prefixlen == ip._max_prefixlen:
            jeżeli ips oraz ips[-1]._version != ip._version:
                podnieś TypeError("%s oraz %s are nie of the same version" % (
                                 ip, ips[-1]))
            spróbuj:
                ips.append(ip.ip)
            wyjąwszy AttributeError:
                ips.append(ip.network_address)
        inaczej:
            jeżeli nets oraz nets[-1]._version != ip._version:
                podnieś TypeError("%s oraz %s are nie of the same version" % (
                                 ip, nets[-1]))
            nets.append(ip)

    # sort oraz dedup
    ips = sorted(set(ips))

    # find consecutive address ranges w the sorted sequence oraz summarize them
    jeżeli ips:
        dla first, last w _find_address_range(ips):
            addrs.extend(summarize_address_range(first, last))

    zwróć _collapse_addresses_internal(addrs + nets)


def get_mixed_type_key(obj):
    """Return a key suitable dla sorting between networks oraz addresses.

    Address oraz Network objects are nie sortable by default; they're
    fundamentally different so the expression

        IPv4Address('192.0.2.0') <= IPv4Network('192.0.2.0/24')

    doesn't make any sense.  There are some times however, where you may wish
    to have ipaddress sort these dla you anyway. If you need to do this, you
    can use this function jako the key= argument to sorted().

    Args:
      obj: either a Network albo Address object.
    Returns:
      appropriate key.

    """
    jeżeli isinstance(obj, _BaseNetwork):
        zwróć obj._get_networks_key()
    albo_inaczej isinstance(obj, _BaseAddress):
        zwróć obj._get_address_key()
    zwróć NotImplemented


klasa _IPAddressBase:

    """The mother class."""

    __slots__ = ()

    @property
    def exploded(self):
        """Return the longhand version of the IP address jako a string."""
        zwróć self._explode_shorthand_ip_string()

    @property
    def compressed(self):
        """Return the shorthand version of the IP address jako a string."""
        zwróć str(self)

    @property
    def reverse_pointer(self):
        """The name of the reverse DNS pointer dla the IP address, e.g.:
            >>> ipaddress.ip_address("127.0.0.1").reverse_pointer
            '1.0.0.127.in-addr.arpa'
            >>> ipaddress.ip_address("2001:db8::1").reverse_pointer
            '1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa'

        """
        zwróć self._reverse_pointer()

    @property
    def version(self):
        msg = '%200s has no version specified' % (type(self),)
        podnieś NotImplementedError(msg)

    def _check_int_address(self, address):
        jeżeli address < 0:
            msg = "%d (< 0) jest nie permitted jako an IPv%d address"
            podnieś AddressValueError(msg % (address, self._version))
        jeżeli address > self._ALL_ONES:
            msg = "%d (>= 2**%d) jest nie permitted jako an IPv%d address"
            podnieś AddressValueError(msg % (address, self._max_prefixlen,
                                           self._version))

    def _check_packed_address(self, address, expected_len):
        address_len = len(address)
        jeżeli address_len != expected_len:
            msg = "%r (len %d != %d) jest nie permitted jako an IPv%d address"
            podnieś AddressValueError(msg % (address, address_len,
                                           expected_len, self._version))

    @classmethod
    def _ip_int_from_prefix(cls, prefixlen):
        """Turn the prefix length into a bitwise netmask

        Args:
            prefixlen: An integer, the prefix length.

        Returns:
            An integer.

        """
        zwróć cls._ALL_ONES ^ (cls._ALL_ONES >> prefixlen)

    @classmethod
    def _prefix_from_ip_int(cls, ip_int):
        """Return prefix length z the bitwise netmask.

        Args:
            ip_int: An integer, the netmask w expanded bitwise format

        Returns:
            An integer, the prefix length.

        Raises:
            ValueError: If the input intermingles zeroes & ones
        """
        trailing_zeroes = _count_righthand_zero_bits(ip_int,
                                                     cls._max_prefixlen)
        prefixlen = cls._max_prefixlen - trailing_zeroes
        leading_ones = ip_int >> trailing_zeroes
        all_ones = (1 << prefixlen) - 1
        jeżeli leading_ones != all_ones:
            byteslen = cls._max_prefixlen // 8
            details = ip_int.to_bytes(byteslen, 'big')
            msg = 'Netmask pattern %r mixes zeroes & ones'
            podnieś ValueError(msg % details)
        zwróć prefixlen

    @classmethod
    def _report_invalid_netmask(cls, netmask_str):
        msg = '%r jest nie a valid netmask' % netmask_str
        podnieś NetmaskValueError(msg) z Nic

    @classmethod
    def _prefix_from_prefix_string(cls, prefixlen_str):
        """Return prefix length z a numeric string

        Args:
            prefixlen_str: The string to be converted

        Returns:
            An integer, the prefix length.

        Raises:
            NetmaskValueError: If the input jest nie a valid netmask
        """
        # int allows a leading +/- jako well jako surrounding whitespace,
        # so we ensure that isn't the case
        jeżeli nie _BaseV4._DECIMAL_DIGITS.issuperset(prefixlen_str):
            cls._report_invalid_netmask(prefixlen_str)
        spróbuj:
            prefixlen = int(prefixlen_str)
        wyjąwszy ValueError:
            cls._report_invalid_netmask(prefixlen_str)
        jeżeli nie (0 <= prefixlen <= cls._max_prefixlen):
            cls._report_invalid_netmask(prefixlen_str)
        zwróć prefixlen

    @classmethod
    def _prefix_from_ip_string(cls, ip_str):
        """Turn a netmask/hostmask string into a prefix length

        Args:
            ip_str: The netmask/hostmask to be converted

        Returns:
            An integer, the prefix length.

        Raises:
            NetmaskValueError: If the input jest nie a valid netmask/hostmask
        """
        # Parse the netmask/hostmask like an IP address.
        spróbuj:
            ip_int = cls._ip_int_from_string(ip_str)
        wyjąwszy AddressValueError:
            cls._report_invalid_netmask(ip_str)

        # Try matching a netmask (this would be /1*0*/ jako a bitwise regexp).
        # Note that the two ambiguous cases (all-ones oraz all-zeroes) are
        # treated jako netmasks.
        spróbuj:
            zwróć cls._prefix_from_ip_int(ip_int)
        wyjąwszy ValueError:
            dalej

        # Invert the bits, oraz try matching a /0+1+/ hostmask instead.
        ip_int ^= cls._ALL_ONES
        spróbuj:
            zwróć cls._prefix_from_ip_int(ip_int)
        wyjąwszy ValueError:
            cls._report_invalid_netmask(ip_str)

    def __reduce__(self):
        zwróć self.__class__, (str(self),)


@functools.total_ordering
klasa _BaseAddress(_IPAddressBase):

    """A generic IP object.

    This IP klasa contains the version independent methods which are
    used by single IP addresses.
    """

    __slots__ = ()

    def __int__(self):
        zwróć self._ip

    def __eq__(self, other):
        spróbuj:
            zwróć (self._ip == other._ip
                    oraz self._version == other._version)
        wyjąwszy AttributeError:
            zwróć NotImplemented

    def __lt__(self, other):
        jeżeli nie isinstance(other, _BaseAddress):
            zwróć NotImplemented
        jeżeli self._version != other._version:
            podnieś TypeError('%s oraz %s are nie of the same version' % (
                             self, other))
        jeżeli self._ip != other._ip:
            zwróć self._ip < other._ip
        zwróć Nieprawda

    # Shorthand dla Integer addition oraz subtraction. This jest nie
    # meant to ever support addition/subtraction of addresses.
    def __add__(self, other):
        jeżeli nie isinstance(other, int):
            zwróć NotImplemented
        zwróć self.__class__(int(self) + other)

    def __sub__(self, other):
        jeżeli nie isinstance(other, int):
            zwróć NotImplemented
        zwróć self.__class__(int(self) - other)

    def __repr__(self):
        zwróć '%s(%r)' % (self.__class__.__name__, str(self))

    def __str__(self):
        zwróć str(self._string_from_ip_int(self._ip))

    def __hash__(self):
        zwróć hash(hex(int(self._ip)))

    def _get_address_key(self):
        zwróć (self._version, self)

    def __reduce__(self):
        zwróć self.__class__, (self._ip,)


@functools.total_ordering
klasa _BaseNetwork(_IPAddressBase):

    """A generic IP network object.

    This IP klasa contains the version independent methods which are
    used by networks.

    """
    def __init__(self, address):
        self._cache = {}

    def __repr__(self):
        zwróć '%s(%r)' % (self.__class__.__name__, str(self))

    def __str__(self):
        zwróć '%s/%d' % (self.network_address, self.prefixlen)

    def hosts(self):
        """Generate Iterator over usable hosts w a network.

        This jest like __iter__ wyjąwszy it doesn't zwróć the network
        albo broadcast addresses.

        """
        network = int(self.network_address)
        broadcast = int(self.broadcast_address)
        dla x w range(network + 1, broadcast):
            uzyskaj self._address_class(x)

    def __iter__(self):
        network = int(self.network_address)
        broadcast = int(self.broadcast_address)
        dla x w range(network, broadcast + 1):
            uzyskaj self._address_class(x)

    def __getitem__(self, n):
        network = int(self.network_address)
        broadcast = int(self.broadcast_address)
        jeżeli n >= 0:
            jeżeli network + n > broadcast:
                podnieś IndexError
            zwróć self._address_class(network + n)
        inaczej:
            n += 1
            jeżeli broadcast + n < network:
                podnieś IndexError
            zwróć self._address_class(broadcast + n)

    def __lt__(self, other):
        jeżeli nie isinstance(other, _BaseNetwork):
            zwróć NotImplemented
        jeżeli self._version != other._version:
            podnieś TypeError('%s oraz %s are nie of the same version' % (
                             self, other))
        jeżeli self.network_address != other.network_address:
            zwróć self.network_address < other.network_address
        jeżeli self.netmask != other.netmask:
            zwróć self.netmask < other.netmask
        zwróć Nieprawda

    def __eq__(self, other):
        spróbuj:
            zwróć (self._version == other._version oraz
                    self.network_address == other.network_address oraz
                    int(self.netmask) == int(other.netmask))
        wyjąwszy AttributeError:
            zwróć NotImplemented

    def __hash__(self):
        zwróć hash(int(self.network_address) ^ int(self.netmask))

    def __contains__(self, other):
        # always false jeżeli one jest v4 oraz the other jest v6.
        jeżeli self._version != other._version:
            zwróć Nieprawda
        # dealing przy another network.
        jeżeli isinstance(other, _BaseNetwork):
            zwróć Nieprawda
        # dealing przy another address
        inaczej:
            # address
            zwróć (int(self.network_address) <= int(other._ip) <=
                    int(self.broadcast_address))

    def overlaps(self, other):
        """Tell jeżeli self jest partly contained w other."""
        zwróć self.network_address w other albo (
            self.broadcast_address w other albo (
                other.network_address w self albo (
                    other.broadcast_address w self)))

    @property
    def broadcast_address(self):
        x = self._cache.get('broadcast_address')
        jeżeli x jest Nic:
            x = self._address_class(int(self.network_address) |
                                    int(self.hostmask))
            self._cache['broadcast_address'] = x
        zwróć x

    @property
    def hostmask(self):
        x = self._cache.get('hostmask')
        jeżeli x jest Nic:
            x = self._address_class(int(self.netmask) ^ self._ALL_ONES)
            self._cache['hostmask'] = x
        zwróć x

    @property
    def with_prefixlen(self):
        zwróć '%s/%d' % (self.network_address, self._prefixlen)

    @property
    def with_netmask(self):
        zwróć '%s/%s' % (self.network_address, self.netmask)

    @property
    def with_hostmask(self):
        zwróć '%s/%s' % (self.network_address, self.hostmask)

    @property
    def num_addresses(self):
        """Number of hosts w the current subnet."""
        zwróć int(self.broadcast_address) - int(self.network_address) + 1

    @property
    def _address_class(self):
        # Returning bare address objects (rather than interfaces) allows for
        # more consistent behaviour across the network address, broadcast
        # address oraz individual host addresses.
        msg = '%200s has no associated address class' % (type(self),)
        podnieś NotImplementedError(msg)

    @property
    def prefixlen(self):
        zwróć self._prefixlen

    def address_exclude(self, other):
        """Remove an address z a larger block.

        For example:

            addr1 = ip_network('192.0.2.0/28')
            addr2 = ip_network('192.0.2.1/32')
            addr1.address_exclude(addr2) =
                [IPv4Network('192.0.2.0/32'), IPv4Network('192.0.2.2/31'),
                IPv4Network('192.0.2.4/30'), IPv4Network('192.0.2.8/29')]

        albo IPv6:

            addr1 = ip_network('2001:db8::1/32')
            addr2 = ip_network('2001:db8::1/128')
            addr1.address_exclude(addr2) =
                [ip_network('2001:db8::1/128'),
                ip_network('2001:db8::2/127'),
                ip_network('2001:db8::4/126'),
                ip_network('2001:db8::8/125'),
                ...
                ip_network('2001:db8:8000::/33')]

        Args:
            other: An IPv4Network albo IPv6Network object of the same type.

        Returns:
            An iterator of the IPv(4|6)Network objects which jest self
            minus other.

        Raises:
            TypeError: If self oraz other are of differing address
              versions, albo jeżeli other jest nie a network object.
            ValueError: If other jest nie completely contained by self.

        """
        jeżeli nie self._version == other._version:
            podnieś TypeError("%s oraz %s are nie of the same version" % (
                             self, other))

        jeżeli nie isinstance(other, _BaseNetwork):
            podnieś TypeError("%s jest nie a network object" % other)

        jeżeli nie (other.network_address >= self.network_address oraz
                other.broadcast_address <= self.broadcast_address):
            podnieś ValueError('%s nie contained w %s' % (other, self))
        jeżeli other == self:
            zwróć

        # Make sure we're comparing the network of other.
        other = other.__class__('%s/%s' % (other.network_address,
                                           other.prefixlen))

        s1, s2 = self.subnets()
        dopóki s1 != other oraz s2 != other:
            jeżeli (other.network_address >= s1.network_address oraz
                other.broadcast_address <= s1.broadcast_address):
                uzyskaj s2
                s1, s2 = s1.subnets()
            albo_inaczej (other.network_address >= s2.network_address oraz
                  other.broadcast_address <= s2.broadcast_address):
                uzyskaj s1
                s1, s2 = s2.subnets()
            inaczej:
                # If we got here, there's a bug somewhere.
                podnieś AssertionError('Error performing exclusion: '
                                     's1: %s s2: %s other: %s' %
                                     (s1, s2, other))
        jeżeli s1 == other:
            uzyskaj s2
        albo_inaczej s2 == other:
            uzyskaj s1
        inaczej:
            # If we got here, there's a bug somewhere.
            podnieś AssertionError('Error performing exclusion: '
                                 's1: %s s2: %s other: %s' %
                                 (s1, s2, other))

    def compare_networks(self, other):
        """Compare two IP objects.

        This jest only concerned about the comparison of the integer
        representation of the network addresses.  This means that the
        host bits aren't considered at all w this method.  If you want
        to compare host bits, you can easily enough do a
        'HostA._ip < HostB._ip'

        Args:
            other: An IP object.

        Returns:
            If the IP versions of self oraz other are the same, returns:

            -1 jeżeli self < other:
              eg: IPv4Network('192.0.2.0/25') < IPv4Network('192.0.2.128/25')
              IPv6Network('2001:db8::1000/124') <
                  IPv6Network('2001:db8::2000/124')
            0 jeżeli self == other
              eg: IPv4Network('192.0.2.0/24') == IPv4Network('192.0.2.0/24')
              IPv6Network('2001:db8::1000/124') ==
                  IPv6Network('2001:db8::1000/124')
            1 jeżeli self > other
              eg: IPv4Network('192.0.2.128/25') > IPv4Network('192.0.2.0/25')
                  IPv6Network('2001:db8::2000/124') >
                      IPv6Network('2001:db8::1000/124')

          Raises:
              TypeError jeżeli the IP versions are different.

        """
        # does this need to podnieś a ValueError?
        jeżeli self._version != other._version:
            podnieś TypeError('%s oraz %s are nie of the same type' % (
                             self, other))
        # self._version == other._version below here:
        jeżeli self.network_address < other.network_address:
            zwróć -1
        jeżeli self.network_address > other.network_address:
            zwróć 1
        # self.network_address == other.network_address below here:
        jeżeli self.netmask < other.netmask:
            zwróć -1
        jeżeli self.netmask > other.netmask:
            zwróć 1
        zwróć 0

    def _get_networks_key(self):
        """Network-only key function.

        Returns an object that identifies this address' network oraz
        netmask. This function jest a suitable "key" argument dla sorted()
        oraz list.sort().

        """
        zwróć (self._version, self.network_address, self.netmask)

    def subnets(self, prefixlen_diff=1, new_prefix=Nic):
        """The subnets which join to make the current subnet.

        In the case that self contains only one IP
        (self._prefixlen == 32 dla IPv4 albo self._prefixlen == 128
        dla IPv6), uzyskaj an iterator przy just ourself.

        Args:
            prefixlen_diff: An integer, the amount the prefix length
              should be increased by. This should nie be set if
              new_prefix jest also set.
            new_prefix: The desired new prefix length. This must be a
              larger number (smaller prefix) than the existing prefix.
              This should nie be set jeżeli prefixlen_diff jest also set.

        Returns:
            An iterator of IPv(4|6) objects.

        Raises:
            ValueError: The prefixlen_diff jest too small albo too large.
                OR
            prefixlen_diff oraz new_prefix are both set albo new_prefix
              jest a smaller number than the current prefix (smaller
              number means a larger network)

        """
        jeżeli self._prefixlen == self._max_prefixlen:
            uzyskaj self
            zwróć

        jeżeli new_prefix jest nie Nic:
            jeżeli new_prefix < self._prefixlen:
                podnieś ValueError('new prefix must be longer')
            jeżeli prefixlen_diff != 1:
                podnieś ValueError('cannot set prefixlen_diff oraz new_prefix')
            prefixlen_diff = new_prefix - self._prefixlen

        jeżeli prefixlen_diff < 0:
            podnieś ValueError('prefix length diff must be > 0')
        new_prefixlen = self._prefixlen + prefixlen_diff

        jeżeli new_prefixlen > self._max_prefixlen:
            podnieś ValueError(
                'prefix length diff %d jest invalid dla netblock %s' % (
                    new_prefixlen, self))

        start = int(self.network_address)
        end = int(self.broadcast_address)
        step = (int(self.hostmask) + 1) >> prefixlen_diff
        dla new_addr w range(start, end, step):
            current = self.__class__((new_addr, new_prefixlen))
            uzyskaj current

    def supernet(self, prefixlen_diff=1, new_prefix=Nic):
        """The supernet containing the current network.

        Args:
            prefixlen_diff: An integer, the amount the prefix length of
              the network should be decreased by.  For example, given a
              /24 network oraz a prefixlen_diff of 3, a supernet przy a
              /21 netmask jest returned.

        Returns:
            An IPv4 network object.

        Raises:
            ValueError: If self.prefixlen - prefixlen_diff < 0. I.e., you have
              a negative prefix length.
                OR
            If prefixlen_diff oraz new_prefix are both set albo new_prefix jest a
              larger number than the current prefix (larger number means a
              smaller network)

        """
        jeżeli self._prefixlen == 0:
            zwróć self

        jeżeli new_prefix jest nie Nic:
            jeżeli new_prefix > self._prefixlen:
                podnieś ValueError('new prefix must be shorter')
            jeżeli prefixlen_diff != 1:
                podnieś ValueError('cannot set prefixlen_diff oraz new_prefix')
            prefixlen_diff = self._prefixlen - new_prefix

        new_prefixlen = self.prefixlen - prefixlen_diff
        jeżeli new_prefixlen < 0:
            podnieś ValueError(
                'current prefixlen jest %d, cannot have a prefixlen_diff of %d' %
                (self.prefixlen, prefixlen_diff))
        zwróć self.__class__((
            int(self.network_address) & (int(self.netmask) << prefixlen_diff),
            new_prefixlen
            ))

    @property
    def is_multicast(self):
        """Test jeżeli the address jest reserved dla multicast use.

        Returns:
            A boolean, Prawda jeżeli the address jest a multicast address.
            See RFC 2373 2.7 dla details.

        """
        zwróć (self.network_address.is_multicast oraz
                self.broadcast_address.is_multicast)

    @property
    def is_reserved(self):
        """Test jeżeli the address jest otherwise IETF reserved.

        Returns:
            A boolean, Prawda jeżeli the address jest within one of the
            reserved IPv6 Network ranges.

        """
        zwróć (self.network_address.is_reserved oraz
                self.broadcast_address.is_reserved)

    @property
    def is_link_local(self):
        """Test jeżeli the address jest reserved dla link-local.

        Returns:
            A boolean, Prawda jeżeli the address jest reserved per RFC 4291.

        """
        zwróć (self.network_address.is_link_local oraz
                self.broadcast_address.is_link_local)

    @property
    def is_private(self):
        """Test jeżeli this address jest allocated dla private networks.

        Returns:
            A boolean, Prawda jeżeli the address jest reserved per
            iana-ipv4-special-registry albo iana-ipv6-special-registry.

        """
        zwróć (self.network_address.is_private oraz
                self.broadcast_address.is_private)

    @property
    def is_global(self):
        """Test jeżeli this address jest allocated dla public networks.

        Returns:
            A boolean, Prawda jeżeli the address jest nie reserved per
            iana-ipv4-special-registry albo iana-ipv6-special-registry.

        """
        zwróć nie self.is_private

    @property
    def is_unspecified(self):
        """Test jeżeli the address jest unspecified.

        Returns:
            A boolean, Prawda jeżeli this jest the unspecified address jako defined w
            RFC 2373 2.5.2.

        """
        zwróć (self.network_address.is_unspecified oraz
                self.broadcast_address.is_unspecified)

    @property
    def is_loopback(self):
        """Test jeżeli the address jest a loopback address.

        Returns:
            A boolean, Prawda jeżeli the address jest a loopback address jako defined w
            RFC 2373 2.5.3.

        """
        zwróć (self.network_address.is_loopback oraz
                self.broadcast_address.is_loopback)


klasa _BaseV4:

    """Base IPv4 object.

    The following methods are used by IPv4 objects w both single IP
    addresses oraz networks.

    """

    __slots__ = ()
    _version = 4
    # Equivalent to 255.255.255.255 albo 32 bits of 1's.
    _ALL_ONES = (2**IPV4LENGTH) - 1
    _DECIMAL_DIGITS = frozenset('0123456789')

    # the valid octets dla host oraz netmasks. only useful dla IPv4.
    _valid_mask_octets = frozenset({255, 254, 252, 248, 240, 224, 192, 128, 0})

    _max_prefixlen = IPV4LENGTH
    # There are only a handful of valid v4 netmasks, so we cache them all
    # when constructed (see _make_netmask()).
    _netmask_cache = {}

    def _explode_shorthand_ip_string(self):
        zwróć str(self)

    @classmethod
    def _make_netmask(cls, arg):
        """Make a (netmask, prefix_len) tuple z the given argument.

        Argument can be:
        - an integer (the prefix length)
        - a string representing the prefix length (e.g. "24")
        - a string representing the prefix netmask (e.g. "255.255.255.0")
        """
        jeżeli arg nie w cls._netmask_cache:
            jeżeli isinstance(arg, int):
                prefixlen = arg
            inaczej:
                spróbuj:
                    # Check dla a netmask w prefix length form
                    prefixlen = cls._prefix_from_prefix_string(arg)
                wyjąwszy NetmaskValueError:
                    # Check dla a netmask albo hostmask w dotted-quad form.
                    # This may podnieś NetmaskValueError.
                    prefixlen = cls._prefix_from_ip_string(arg)
            netmask = IPv4Address(cls._ip_int_from_prefix(prefixlen))
            cls._netmask_cache[arg] = netmask, prefixlen
        zwróć cls._netmask_cache[arg]

    @classmethod
    def _ip_int_from_string(cls, ip_str):
        """Turn the given IP string into an integer dla comparison.

        Args:
            ip_str: A string, the IP ip_str.

        Returns:
            The IP ip_str jako an integer.

        Raises:
            AddressValueError: jeżeli ip_str isn't a valid IPv4 Address.

        """
        jeżeli nie ip_str:
            podnieś AddressValueError('Address cannot be empty')

        octets = ip_str.split('.')
        jeżeli len(octets) != 4:
            podnieś AddressValueError("Expected 4 octets w %r" % ip_str)

        spróbuj:
            zwróć int.from_bytes(map(cls._parse_octet, octets), 'big')
        wyjąwszy ValueError jako exc:
            podnieś AddressValueError("%s w %r" % (exc, ip_str)) z Nic

    @classmethod
    def _parse_octet(cls, octet_str):
        """Convert a decimal octet into an integer.

        Args:
            octet_str: A string, the number to parse.

        Returns:
            The octet jako an integer.

        Raises:
            ValueError: jeżeli the octet isn't strictly a decimal z [0..255].

        """
        jeżeli nie octet_str:
            podnieś ValueError("Empty octet nie permitted")
        # Whitelist the characters, since int() allows a lot of bizarre stuff.
        jeżeli nie cls._DECIMAL_DIGITS.issuperset(octet_str):
            msg = "Only decimal digits permitted w %r"
            podnieś ValueError(msg % octet_str)
        # We do the length check second, since the invalid character error
        # jest likely to be more informative dla the user
        jeżeli len(octet_str) > 3:
            msg = "At most 3 characters permitted w %r"
            podnieś ValueError(msg % octet_str)
        # Convert to integer (we know digits are legal)
        octet_int = int(octet_str, 10)
        # Any octets that look like they *might* be written w octal,
        # oraz which don't look exactly the same w both octal oraz
        # decimal are rejected jako ambiguous
        jeżeli octet_int > 7 oraz octet_str[0] == '0':
            msg = "Ambiguous (octal/decimal) value w %r nie permitted"
            podnieś ValueError(msg % octet_str)
        jeżeli octet_int > 255:
            podnieś ValueError("Octet %d (> 255) nie permitted" % octet_int)
        zwróć octet_int

    @classmethod
    def _string_from_ip_int(cls, ip_int):
        """Turns a 32-bit integer into dotted decimal notation.

        Args:
            ip_int: An integer, the IP address.

        Returns:
            The IP address jako a string w dotted decimal notation.

        """
        zwróć '.'.join(map(str, ip_int.to_bytes(4, 'big')))

    def _is_valid_netmask(self, netmask):
        """Verify that the netmask jest valid.

        Args:
            netmask: A string, either a prefix albo dotted decimal
              netmask.

        Returns:
            A boolean, Prawda jeżeli the prefix represents a valid IPv4
            netmask.

        """
        mask = netmask.split('.')
        jeżeli len(mask) == 4:
            spróbuj:
                dla x w mask:
                    jeżeli int(x) nie w self._valid_mask_octets:
                        zwróć Nieprawda
            wyjąwszy ValueError:
                # Found something that isn't an integer albo isn't valid
                zwróć Nieprawda
            dla idx, y w enumerate(mask):
                jeżeli idx > 0 oraz y > mask[idx - 1]:
                    zwróć Nieprawda
            zwróć Prawda
        spróbuj:
            netmask = int(netmask)
        wyjąwszy ValueError:
            zwróć Nieprawda
        zwróć 0 <= netmask <= self._max_prefixlen

    def _is_hostmask(self, ip_str):
        """Test jeżeli the IP string jest a hostmask (rather than a netmask).

        Args:
            ip_str: A string, the potential hostmask.

        Returns:
            A boolean, Prawda jeżeli the IP string jest a hostmask.

        """
        bits = ip_str.split('.')
        spróbuj:
            parts = [x dla x w map(int, bits) jeżeli x w self._valid_mask_octets]
        wyjąwszy ValueError:
            zwróć Nieprawda
        jeżeli len(parts) != len(bits):
            zwróć Nieprawda
        jeżeli parts[0] < parts[-1]:
            zwróć Prawda
        zwróć Nieprawda

    def _reverse_pointer(self):
        """Return the reverse DNS pointer name dla the IPv4 address.

        This implements the method described w RFC1035 3.5.

        """
        reverse_octets = str(self).split('.')[::-1]
        zwróć '.'.join(reverse_octets) + '.in-addr.arpa'

    @property
    def max_prefixlen(self):
        zwróć self._max_prefixlen

    @property
    def version(self):
        zwróć self._version


klasa IPv4Address(_BaseV4, _BaseAddress):

    """Represent oraz manipulate single IPv4 Addresses."""

    __slots__ = ('_ip', '__weakref__')

    def __init__(self, address):

        """
        Args:
            address: A string albo integer representing the IP

              Additionally, an integer can be dalejed, so
              IPv4Address('192.0.2.1') == IPv4Address(3221225985).
              or, more generally
              IPv4Address(int(IPv4Address('192.0.2.1'))) ==
                IPv4Address('192.0.2.1')

        Raises:
            AddressValueError: If ipaddress isn't a valid IPv4 address.

        """
        # Efficient constructor z integer.
        jeżeli isinstance(address, int):
            self._check_int_address(address)
            self._ip = address
            zwróć

        # Constructing z a packed address
        jeżeli isinstance(address, bytes):
            self._check_packed_address(address, 4)
            self._ip = int.from_bytes(address, 'big')
            zwróć

        # Assume input argument to be string albo any object representation
        # which converts into a formatted IP string.
        addr_str = str(address)
        jeżeli '/' w addr_str:
            podnieś AddressValueError("Unexpected '/' w %r" % address)
        self._ip = self._ip_int_from_string(addr_str)

    @property
    def packed(self):
        """The binary representation of this address."""
        zwróć v4_int_to_packed(self._ip)

    @property
    def is_reserved(self):
        """Test jeżeli the address jest otherwise IETF reserved.

         Returns:
             A boolean, Prawda jeżeli the address jest within the
             reserved IPv4 Network range.

        """
        zwróć self w self._constants._reserved_network

    @property
    @functools.lru_cache()
    def is_private(self):
        """Test jeżeli this address jest allocated dla private networks.

        Returns:
            A boolean, Prawda jeżeli the address jest reserved per
            iana-ipv4-special-registry.

        """
        zwróć any(self w net dla net w self._constants._private_networks)

    @property
    def is_multicast(self):
        """Test jeżeli the address jest reserved dla multicast use.

        Returns:
            A boolean, Prawda jeżeli the address jest multicast.
            See RFC 3171 dla details.

        """
        zwróć self w self._constants._multicast_network

    @property
    def is_unspecified(self):
        """Test jeżeli the address jest unspecified.

        Returns:
            A boolean, Prawda jeżeli this jest the unspecified address jako defined w
            RFC 5735 3.

        """
        zwróć self == self._constants._unspecified_address

    @property
    def is_loopback(self):
        """Test jeżeli the address jest a loopback address.

        Returns:
            A boolean, Prawda jeżeli the address jest a loopback per RFC 3330.

        """
        zwróć self w self._constants._loopback_network

    @property
    def is_link_local(self):
        """Test jeżeli the address jest reserved dla link-local.

        Returns:
            A boolean, Prawda jeżeli the address jest link-local per RFC 3927.

        """
        zwróć self w self._constants._linklocal_network


klasa IPv4Interface(IPv4Address):

    def __init__(self, address):
        jeżeli isinstance(address, (bytes, int)):
            IPv4Address.__init__(self, address)
            self.network = IPv4Network(self._ip)
            self._prefixlen = self._max_prefixlen
            zwróć

        jeżeli isinstance(address, tuple):
            IPv4Address.__init__(self, address[0])
            jeżeli len(address) > 1:
                self._prefixlen = int(address[1])
            inaczej:
                self._prefixlen = self._max_prefixlen

            self.network = IPv4Network(address, strict=Nieprawda)
            self.netmask = self.network.netmask
            self.hostmask = self.network.hostmask
            zwróć

        addr = _split_optional_netmask(address)
        IPv4Address.__init__(self, addr[0])

        self.network = IPv4Network(address, strict=Nieprawda)
        self._prefixlen = self.network._prefixlen

        self.netmask = self.network.netmask
        self.hostmask = self.network.hostmask

    def __str__(self):
        zwróć '%s/%d' % (self._string_from_ip_int(self._ip),
                          self.network.prefixlen)

    def __eq__(self, other):
        address_equal = IPv4Address.__eq__(self, other)
        jeżeli nie address_equal albo address_equal jest NotImplemented:
            zwróć address_equal
        spróbuj:
            zwróć self.network == other.network
        wyjąwszy AttributeError:
            # An interface przy an associated network jest NOT the
            # same jako an unassociated address. That's why the hash
            # takes the extra info into account.
            zwróć Nieprawda

    def __lt__(self, other):
        address_less = IPv4Address.__lt__(self, other)
        jeżeli address_less jest NotImplemented:
            zwróć NotImplemented
        spróbuj:
            zwróć self.network < other.network
        wyjąwszy AttributeError:
            # We *do* allow addresses oraz interfaces to be sorted. The
            # unassociated address jest considered less than all interfaces.
            zwróć Nieprawda

    def __hash__(self):
        zwróć self._ip ^ self._prefixlen ^ int(self.network.network_address)

    __reduce__ = _IPAddressBase.__reduce__

    @property
    def ip(self):
        zwróć IPv4Address(self._ip)

    @property
    def with_prefixlen(self):
        zwróć '%s/%s' % (self._string_from_ip_int(self._ip),
                          self._prefixlen)

    @property
    def with_netmask(self):
        zwróć '%s/%s' % (self._string_from_ip_int(self._ip),
                          self.netmask)

    @property
    def with_hostmask(self):
        zwróć '%s/%s' % (self._string_from_ip_int(self._ip),
                          self.hostmask)


klasa IPv4Network(_BaseV4, _BaseNetwork):

    """This klasa represents oraz manipulates 32-bit IPv4 network + addresses..

    Attributes: [examples dla IPv4Network('192.0.2.0/27')]
        .network_address: IPv4Address('192.0.2.0')
        .hostmask: IPv4Address('0.0.0.31')
        .broadcast_address: IPv4Address('192.0.2.32')
        .netmask: IPv4Address('255.255.255.224')
        .prefixlen: 27

    """
    # Class to use when creating address objects
    _address_class = IPv4Address

    def __init__(self, address, strict=Prawda):

        """Instantiate a new IPv4 network object.

        Args:
            address: A string albo integer representing the IP [& network].
              '192.0.2.0/24'
              '192.0.2.0/255.255.255.0'
              '192.0.0.2/0.0.0.255'
              are all functionally the same w IPv4. Similarly,
              '192.0.2.1'
              '192.0.2.1/255.255.255.255'
              '192.0.2.1/32'
              are also functionally equivalent. That jest to say, failing to
              provide a subnetmask will create an object przy a mask of /32.

              If the mask (portion after the / w the argument) jest given w
              dotted quad form, it jest treated jako a netmask jeżeli it starts przy a
              non-zero field (e.g. /255.0.0.0 == /8) oraz jako a hostmask jeżeli it
              starts przy a zero field (e.g. 0.255.255.255 == /8), przy the
              single exception of an all-zero mask which jest treated jako a
              netmask == /0. If no mask jest given, a default of /32 jest used.

              Additionally, an integer can be dalejed, so
              IPv4Network('192.0.2.1') == IPv4Network(3221225985)
              or, more generally
              IPv4Interface(int(IPv4Interface('192.0.2.1'))) ==
                IPv4Interface('192.0.2.1')

        Raises:
            AddressValueError: If ipaddress isn't a valid IPv4 address.
            NetmaskValueError: If the netmask isn't valid for
              an IPv4 address.
            ValueError: If strict jest Prawda oraz a network address jest nie
              supplied.

        """
        _BaseNetwork.__init__(self, address)

        # Constructing z a packed address albo integer
        jeżeli isinstance(address, (int, bytes)):
            self.network_address = IPv4Address(address)
            self.netmask, self._prefixlen = self._make_netmask(self._max_prefixlen)
            #fixme: address/network test here.
            zwróć

        jeżeli isinstance(address, tuple):
            jeżeli len(address) > 1:
                arg = address[1]
            inaczej:
                # We weren't given an address[1]
                arg = self._max_prefixlen
            self.network_address = IPv4Address(address[0])
            self.netmask, self._prefixlen = self._make_netmask(arg)
            packed = int(self.network_address)
            jeżeli packed & int(self.netmask) != packed:
                jeżeli strict:
                    podnieś ValueError('%s has host bits set' % self)
                inaczej:
                    self.network_address = IPv4Address(packed &
                                                       int(self.netmask))
            zwróć

        # Assume input argument to be string albo any object representation
        # which converts into a formatted IP prefix string.
        addr = _split_optional_netmask(address)
        self.network_address = IPv4Address(self._ip_int_from_string(addr[0]))

        jeżeli len(addr) == 2:
            arg = addr[1]
        inaczej:
            arg = self._max_prefixlen
        self.netmask, self._prefixlen = self._make_netmask(arg)

        jeżeli strict:
            jeżeli (IPv4Address(int(self.network_address) & int(self.netmask)) !=
                self.network_address):
                podnieś ValueError('%s has host bits set' % self)
        self.network_address = IPv4Address(int(self.network_address) &
                                           int(self.netmask))

        jeżeli self._prefixlen == (self._max_prefixlen - 1):
            self.hosts = self.__iter__

    @property
    @functools.lru_cache()
    def is_global(self):
        """Test jeżeli this address jest allocated dla public networks.

        Returns:
            A boolean, Prawda jeżeli the address jest nie reserved per
            iana-ipv4-special-registry.

        """
        zwróć (nie (self.network_address w IPv4Network('100.64.0.0/10') oraz
                    self.broadcast_address w IPv4Network('100.64.0.0/10')) oraz
                nie self.is_private)


klasa _IPv4Constants:
    _linklocal_network = IPv4Network('169.254.0.0/16')

    _loopback_network = IPv4Network('127.0.0.0/8')

    _multicast_network = IPv4Network('224.0.0.0/4')

    _private_networks = [
        IPv4Network('0.0.0.0/8'),
        IPv4Network('10.0.0.0/8'),
        IPv4Network('127.0.0.0/8'),
        IPv4Network('169.254.0.0/16'),
        IPv4Network('172.16.0.0/12'),
        IPv4Network('192.0.0.0/29'),
        IPv4Network('192.0.0.170/31'),
        IPv4Network('192.0.2.0/24'),
        IPv4Network('192.168.0.0/16'),
        IPv4Network('198.18.0.0/15'),
        IPv4Network('198.51.100.0/24'),
        IPv4Network('203.0.113.0/24'),
        IPv4Network('240.0.0.0/4'),
        IPv4Network('255.255.255.255/32'),
        ]

    _reserved_network = IPv4Network('240.0.0.0/4')

    _unspecified_address = IPv4Address('0.0.0.0')


IPv4Address._constants = _IPv4Constants


klasa _BaseV6:

    """Base IPv6 object.

    The following methods are used by IPv6 objects w both single IP
    addresses oraz networks.

    """

    __slots__ = ()
    _version = 6
    _ALL_ONES = (2**IPV6LENGTH) - 1
    _HEXTET_COUNT = 8
    _HEX_DIGITS = frozenset('0123456789ABCDEFabcdef')
    _max_prefixlen = IPV6LENGTH

    # There are only a bunch of valid v6 netmasks, so we cache them all
    # when constructed (see _make_netmask()).
    _netmask_cache = {}

    @classmethod
    def _make_netmask(cls, arg):
        """Make a (netmask, prefix_len) tuple z the given argument.

        Argument can be:
        - an integer (the prefix length)
        - a string representing the prefix length (e.g. "24")
        - a string representing the prefix netmask (e.g. "255.255.255.0")
        """
        jeżeli arg nie w cls._netmask_cache:
            jeżeli isinstance(arg, int):
                prefixlen = arg
            inaczej:
                prefixlen = cls._prefix_from_prefix_string(arg)
            netmask = IPv6Address(cls._ip_int_from_prefix(prefixlen))
            cls._netmask_cache[arg] = netmask, prefixlen
        zwróć cls._netmask_cache[arg]

    @classmethod
    def _ip_int_from_string(cls, ip_str):
        """Turn an IPv6 ip_str into an integer.

        Args:
            ip_str: A string, the IPv6 ip_str.

        Returns:
            An int, the IPv6 address

        Raises:
            AddressValueError: jeżeli ip_str isn't a valid IPv6 Address.

        """
        jeżeli nie ip_str:
            podnieś AddressValueError('Address cannot be empty')

        parts = ip_str.split(':')

        # An IPv6 address needs at least 2 colons (3 parts).
        _min_parts = 3
        jeżeli len(parts) < _min_parts:
            msg = "At least %d parts expected w %r" % (_min_parts, ip_str)
            podnieś AddressValueError(msg)

        # If the address has an IPv4-style suffix, convert it to hexadecimal.
        jeżeli '.' w parts[-1]:
            spróbuj:
                ipv4_int = IPv4Address(parts.pop())._ip
            wyjąwszy AddressValueError jako exc:
                podnieś AddressValueError("%s w %r" % (exc, ip_str)) z Nic
            parts.append('%x' % ((ipv4_int >> 16) & 0xFFFF))
            parts.append('%x' % (ipv4_int & 0xFFFF))

        # An IPv6 address can't have more than 8 colons (9 parts).
        # The extra colon comes z using the "::" notation dla a single
        # leading albo trailing zero part.
        _max_parts = cls._HEXTET_COUNT + 1
        jeżeli len(parts) > _max_parts:
            msg = "At most %d colons permitted w %r" % (_max_parts-1, ip_str)
            podnieś AddressValueError(msg)

        # Disregarding the endpoints, find '::' przy nothing w between.
        # This indicates that a run of zeroes has been skipped.
        skip_index = Nic
        dla i w range(1, len(parts) - 1):
            jeżeli nie parts[i]:
                jeżeli skip_index jest nie Nic:
                    # Can't have more than one '::'
                    msg = "At most one '::' permitted w %r" % ip_str
                    podnieś AddressValueError(msg)
                skip_index = i

        # parts_hi jest the number of parts to copy z above/before the '::'
        # parts_lo jest the number of parts to copy z below/after the '::'
        jeżeli skip_index jest nie Nic:
            # If we found a '::', then check jeżeli it also covers the endpoints.
            parts_hi = skip_index
            parts_lo = len(parts) - skip_index - 1
            jeżeli nie parts[0]:
                parts_hi -= 1
                jeżeli parts_hi:
                    msg = "Leading ':' only permitted jako part of '::' w %r"
                    podnieś AddressValueError(msg % ip_str)  # ^: requires ^::
            jeżeli nie parts[-1]:
                parts_lo -= 1
                jeżeli parts_lo:
                    msg = "Trailing ':' only permitted jako part of '::' w %r"
                    podnieś AddressValueError(msg % ip_str)  # :$ requires ::$
            parts_skipped = cls._HEXTET_COUNT - (parts_hi + parts_lo)
            jeżeli parts_skipped < 1:
                msg = "Expected at most %d other parts przy '::' w %r"
                podnieś AddressValueError(msg % (cls._HEXTET_COUNT-1, ip_str))
        inaczej:
            # Otherwise, allocate the entire address to parts_hi.  The
            # endpoints could still be empty, but _parse_hextet() will check
            # dla that.
            jeżeli len(parts) != cls._HEXTET_COUNT:
                msg = "Exactly %d parts expected without '::' w %r"
                podnieś AddressValueError(msg % (cls._HEXTET_COUNT, ip_str))
            jeżeli nie parts[0]:
                msg = "Leading ':' only permitted jako part of '::' w %r"
                podnieś AddressValueError(msg % ip_str)  # ^: requires ^::
            jeżeli nie parts[-1]:
                msg = "Trailing ':' only permitted jako part of '::' w %r"
                podnieś AddressValueError(msg % ip_str)  # :$ requires ::$
            parts_hi = len(parts)
            parts_lo = 0
            parts_skipped = 0

        spróbuj:
            # Now, parse the hextets into a 128-bit integer.
            ip_int = 0
            dla i w range(parts_hi):
                ip_int <<= 16
                ip_int |= cls._parse_hextet(parts[i])
            ip_int <<= 16 * parts_skipped
            dla i w range(-parts_lo, 0):
                ip_int <<= 16
                ip_int |= cls._parse_hextet(parts[i])
            zwróć ip_int
        wyjąwszy ValueError jako exc:
            podnieś AddressValueError("%s w %r" % (exc, ip_str)) z Nic

    @classmethod
    def _parse_hextet(cls, hextet_str):
        """Convert an IPv6 hextet string into an integer.

        Args:
            hextet_str: A string, the number to parse.

        Returns:
            The hextet jako an integer.

        Raises:
            ValueError: jeżeli the input isn't strictly a hex number from
              [0..FFFF].

        """
        # Whitelist the characters, since int() allows a lot of bizarre stuff.
        jeżeli nie cls._HEX_DIGITS.issuperset(hextet_str):
            podnieś ValueError("Only hex digits permitted w %r" % hextet_str)
        # We do the length check second, since the invalid character error
        # jest likely to be more informative dla the user
        jeżeli len(hextet_str) > 4:
            msg = "At most 4 characters permitted w %r"
            podnieś ValueError(msg % hextet_str)
        # Length check means we can skip checking the integer value
        zwróć int(hextet_str, 16)

    @classmethod
    def _compress_hextets(cls, hextets):
        """Compresses a list of hextets.

        Compresses a list of strings, replacing the longest continuous
        sequence of "0" w the list przy "" oraz adding empty strings at
        the beginning albo at the end of the string such that subsequently
        calling ":".join(hextets) will produce the compressed version of
        the IPv6 address.

        Args:
            hextets: A list of strings, the hextets to compress.

        Returns:
            A list of strings.

        """
        best_doublecolon_start = -1
        best_doublecolon_len = 0
        doublecolon_start = -1
        doublecolon_len = 0
        dla index, hextet w enumerate(hextets):
            jeżeli hextet == '0':
                doublecolon_len += 1
                jeżeli doublecolon_start == -1:
                    # Start of a sequence of zeros.
                    doublecolon_start = index
                jeżeli doublecolon_len > best_doublecolon_len:
                    # This jest the longest sequence of zeros so far.
                    best_doublecolon_len = doublecolon_len
                    best_doublecolon_start = doublecolon_start
            inaczej:
                doublecolon_len = 0
                doublecolon_start = -1

        jeżeli best_doublecolon_len > 1:
            best_doublecolon_end = (best_doublecolon_start +
                                    best_doublecolon_len)
            # For zeros at the end of the address.
            jeżeli best_doublecolon_end == len(hextets):
                hextets += ['']
            hextets[best_doublecolon_start:best_doublecolon_end] = ['']
            # For zeros at the beginning of the address.
            jeżeli best_doublecolon_start == 0:
                hextets = [''] + hextets

        zwróć hextets

    @classmethod
    def _string_from_ip_int(cls, ip_int=Nic):
        """Turns a 128-bit integer into hexadecimal notation.

        Args:
            ip_int: An integer, the IP address.

        Returns:
            A string, the hexadecimal representation of the address.

        Raises:
            ValueError: The address jest bigger than 128 bits of all ones.

        """
        jeżeli ip_int jest Nic:
            ip_int = int(cls._ip)

        jeżeli ip_int > cls._ALL_ONES:
            podnieś ValueError('IPv6 address jest too large')

        hex_str = '%032x' % ip_int
        hextets = ['%x' % int(hex_str[x:x+4], 16) dla x w range(0, 32, 4)]

        hextets = cls._compress_hextets(hextets)
        zwróć ':'.join(hextets)

    def _explode_shorthand_ip_string(self):
        """Expand a shortened IPv6 address.

        Args:
            ip_str: A string, the IPv6 address.

        Returns:
            A string, the expanded IPv6 address.

        """
        jeżeli isinstance(self, IPv6Network):
            ip_str = str(self.network_address)
        albo_inaczej isinstance(self, IPv6Interface):
            ip_str = str(self.ip)
        inaczej:
            ip_str = str(self)

        ip_int = self._ip_int_from_string(ip_str)
        hex_str = '%032x' % ip_int
        parts = [hex_str[x:x+4] dla x w range(0, 32, 4)]
        jeżeli isinstance(self, (_BaseNetwork, IPv6Interface)):
            zwróć '%s/%d' % (':'.join(parts), self._prefixlen)
        zwróć ':'.join(parts)

    def _reverse_pointer(self):
        """Return the reverse DNS pointer name dla the IPv6 address.

        This implements the method described w RFC3596 2.5.

        """
        reverse_chars = self.exploded[::-1].replace(':', '')
        zwróć '.'.join(reverse_chars) + '.ip6.arpa'

    @property
    def max_prefixlen(self):
        zwróć self._max_prefixlen

    @property
    def version(self):
        zwróć self._version


klasa IPv6Address(_BaseV6, _BaseAddress):

    """Represent oraz manipulate single IPv6 Addresses."""

    __slots__ = ('_ip', '__weakref__')

    def __init__(self, address):
        """Instantiate a new IPv6 address object.

        Args:
            address: A string albo integer representing the IP

              Additionally, an integer can be dalejed, so
              IPv6Address('2001:db8::') ==
                IPv6Address(42540766411282592856903984951653826560)
              or, more generally
              IPv6Address(int(IPv6Address('2001:db8::'))) ==
                IPv6Address('2001:db8::')

        Raises:
            AddressValueError: If address isn't a valid IPv6 address.

        """
        # Efficient constructor z integer.
        jeżeli isinstance(address, int):
            self._check_int_address(address)
            self._ip = address
            zwróć

        # Constructing z a packed address
        jeżeli isinstance(address, bytes):
            self._check_packed_address(address, 16)
            self._ip = int.from_bytes(address, 'big')
            zwróć

        # Assume input argument to be string albo any object representation
        # which converts into a formatted IP string.
        addr_str = str(address)
        jeżeli '/' w addr_str:
            podnieś AddressValueError("Unexpected '/' w %r" % address)
        self._ip = self._ip_int_from_string(addr_str)

    @property
    def packed(self):
        """The binary representation of this address."""
        zwróć v6_int_to_packed(self._ip)

    @property
    def is_multicast(self):
        """Test jeżeli the address jest reserved dla multicast use.

        Returns:
            A boolean, Prawda jeżeli the address jest a multicast address.
            See RFC 2373 2.7 dla details.

        """
        zwróć self w self._constants._multicast_network

    @property
    def is_reserved(self):
        """Test jeżeli the address jest otherwise IETF reserved.

        Returns:
            A boolean, Prawda jeżeli the address jest within one of the
            reserved IPv6 Network ranges.

        """
        zwróć any(self w x dla x w self._constants._reserved_networks)

    @property
    def is_link_local(self):
        """Test jeżeli the address jest reserved dla link-local.

        Returns:
            A boolean, Prawda jeżeli the address jest reserved per RFC 4291.

        """
        zwróć self w self._constants._linklocal_network

    @property
    def is_site_local(self):
        """Test jeżeli the address jest reserved dla site-local.

        Note that the site-local address space has been deprecated by RFC 3879.
        Use is_private to test jeżeli this address jest w the space of unique local
        addresses jako defined by RFC 4193.

        Returns:
            A boolean, Prawda jeżeli the address jest reserved per RFC 3513 2.5.6.

        """
        zwróć self w self._constants._sitelocal_network

    @property
    @functools.lru_cache()
    def is_private(self):
        """Test jeżeli this address jest allocated dla private networks.

        Returns:
            A boolean, Prawda jeżeli the address jest reserved per
            iana-ipv6-special-registry.

        """
        zwróć any(self w net dla net w self._constants._private_networks)

    @property
    def is_global(self):
        """Test jeżeli this address jest allocated dla public networks.

        Returns:
            A boolean, true jeżeli the address jest nie reserved per
            iana-ipv6-special-registry.

        """
        zwróć nie self.is_private

    @property
    def is_unspecified(self):
        """Test jeżeli the address jest unspecified.

        Returns:
            A boolean, Prawda jeżeli this jest the unspecified address jako defined w
            RFC 2373 2.5.2.

        """
        zwróć self._ip == 0

    @property
    def is_loopback(self):
        """Test jeżeli the address jest a loopback address.

        Returns:
            A boolean, Prawda jeżeli the address jest a loopback address jako defined w
            RFC 2373 2.5.3.

        """
        zwróć self._ip == 1

    @property
    def ipv4_mapped(self):
        """Return the IPv4 mapped address.

        Returns:
            If the IPv6 address jest a v4 mapped address, zwróć the
            IPv4 mapped address. Return Nic otherwise.

        """
        jeżeli (self._ip >> 32) != 0xFFFF:
            zwróć Nic
        zwróć IPv4Address(self._ip & 0xFFFFFFFF)

    @property
    def teredo(self):
        """Tuple of embedded teredo IPs.

        Returns:
            Tuple of the (server, client) IPs albo Nic jeżeli the address
            doesn't appear to be a teredo address (doesn't start with
            2001::/32)

        """
        jeżeli (self._ip >> 96) != 0x20010000:
            zwróć Nic
        zwróć (IPv4Address((self._ip >> 64) & 0xFFFFFFFF),
                IPv4Address(~self._ip & 0xFFFFFFFF))

    @property
    def sixtofour(self):
        """Return the IPv4 6to4 embedded address.

        Returns:
            The IPv4 6to4-embedded address jeżeli present albo Nic jeżeli the
            address doesn't appear to contain a 6to4 embedded address.

        """
        jeżeli (self._ip >> 112) != 0x2002:
            zwróć Nic
        zwróć IPv4Address((self._ip >> 80) & 0xFFFFFFFF)


klasa IPv6Interface(IPv6Address):

    def __init__(self, address):
        jeżeli isinstance(address, (bytes, int)):
            IPv6Address.__init__(self, address)
            self.network = IPv6Network(self._ip)
            self._prefixlen = self._max_prefixlen
            zwróć
        jeżeli isinstance(address, tuple):
            IPv6Address.__init__(self, address[0])
            jeżeli len(address) > 1:
                self._prefixlen = int(address[1])
            inaczej:
                self._prefixlen = self._max_prefixlen
            self.network = IPv6Network(address, strict=Nieprawda)
            self.netmask = self.network.netmask
            self.hostmask = self.network.hostmask
            zwróć

        addr = _split_optional_netmask(address)
        IPv6Address.__init__(self, addr[0])
        self.network = IPv6Network(address, strict=Nieprawda)
        self.netmask = self.network.netmask
        self._prefixlen = self.network._prefixlen
        self.hostmask = self.network.hostmask

    def __str__(self):
        zwróć '%s/%d' % (self._string_from_ip_int(self._ip),
                          self.network.prefixlen)

    def __eq__(self, other):
        address_equal = IPv6Address.__eq__(self, other)
        jeżeli nie address_equal albo address_equal jest NotImplemented:
            zwróć address_equal
        spróbuj:
            zwróć self.network == other.network
        wyjąwszy AttributeError:
            # An interface przy an associated network jest NOT the
            # same jako an unassociated address. That's why the hash
            # takes the extra info into account.
            zwróć Nieprawda

    def __lt__(self, other):
        address_less = IPv6Address.__lt__(self, other)
        jeżeli address_less jest NotImplemented:
            zwróć NotImplemented
        spróbuj:
            zwróć self.network < other.network
        wyjąwszy AttributeError:
            # We *do* allow addresses oraz interfaces to be sorted. The
            # unassociated address jest considered less than all interfaces.
            zwróć Nieprawda

    def __hash__(self):
        zwróć self._ip ^ self._prefixlen ^ int(self.network.network_address)

    __reduce__ = _IPAddressBase.__reduce__

    @property
    def ip(self):
        zwróć IPv6Address(self._ip)

    @property
    def with_prefixlen(self):
        zwróć '%s/%s' % (self._string_from_ip_int(self._ip),
                          self._prefixlen)

    @property
    def with_netmask(self):
        zwróć '%s/%s' % (self._string_from_ip_int(self._ip),
                          self.netmask)

    @property
    def with_hostmask(self):
        zwróć '%s/%s' % (self._string_from_ip_int(self._ip),
                          self.hostmask)

    @property
    def is_unspecified(self):
        zwróć self._ip == 0 oraz self.network.is_unspecified

    @property
    def is_loopback(self):
        zwróć self._ip == 1 oraz self.network.is_loopback


klasa IPv6Network(_BaseV6, _BaseNetwork):

    """This klasa represents oraz manipulates 128-bit IPv6 networks.

    Attributes: [examples dla IPv6('2001:db8::1000/124')]
        .network_address: IPv6Address('2001:db8::1000')
        .hostmask: IPv6Address('::f')
        .broadcast_address: IPv6Address('2001:db8::100f')
        .netmask: IPv6Address('ffff:ffff:ffff:ffff:ffff:ffff:ffff:fff0')
        .prefixlen: 124

    """

    # Class to use when creating address objects
    _address_class = IPv6Address

    def __init__(self, address, strict=Prawda):
        """Instantiate a new IPv6 Network object.

        Args:
            address: A string albo integer representing the IPv6 network albo the
              IP oraz prefix/netmask.
              '2001:db8::/128'
              '2001:db8:0000:0000:0000:0000:0000:0000/128'
              '2001:db8::'
              are all functionally the same w IPv6.  That jest to say,
              failing to provide a subnetmask will create an object with
              a mask of /128.

              Additionally, an integer can be dalejed, so
              IPv6Network('2001:db8::') ==
                IPv6Network(42540766411282592856903984951653826560)
              or, more generally
              IPv6Network(int(IPv6Network('2001:db8::'))) ==
                IPv6Network('2001:db8::')

            strict: A boolean. If true, ensure that we have been dalejed
              A true network address, eg, 2001:db8::1000/124 oraz nie an
              IP address on a network, eg, 2001:db8::1/124.

        Raises:
            AddressValueError: If address isn't a valid IPv6 address.
            NetmaskValueError: If the netmask isn't valid for
              an IPv6 address.
            ValueError: If strict was Prawda oraz a network address was nie
              supplied.

        """
        _BaseNetwork.__init__(self, address)

        # Efficient constructor z integer albo packed address
        jeżeli isinstance(address, (bytes, int)):
            self.network_address = IPv6Address(address)
            self.netmask, self._prefixlen = self._make_netmask(self._max_prefixlen)
            zwróć

        jeżeli isinstance(address, tuple):
            jeżeli len(address) > 1:
                arg = address[1]
            inaczej:
                arg = self._max_prefixlen
            self.netmask, self._prefixlen = self._make_netmask(arg)
            self.network_address = IPv6Address(address[0])
            packed = int(self.network_address)
            jeżeli packed & int(self.netmask) != packed:
                jeżeli strict:
                    podnieś ValueError('%s has host bits set' % self)
                inaczej:
                    self.network_address = IPv6Address(packed &
                                                       int(self.netmask))
            zwróć

        # Assume input argument to be string albo any object representation
        # which converts into a formatted IP prefix string.
        addr = _split_optional_netmask(address)

        self.network_address = IPv6Address(self._ip_int_from_string(addr[0]))

        jeżeli len(addr) == 2:
            arg = addr[1]
        inaczej:
            arg = self._max_prefixlen
        self.netmask, self._prefixlen = self._make_netmask(arg)

        jeżeli strict:
            jeżeli (IPv6Address(int(self.network_address) & int(self.netmask)) !=
                self.network_address):
                podnieś ValueError('%s has host bits set' % self)
        self.network_address = IPv6Address(int(self.network_address) &
                                           int(self.netmask))

        jeżeli self._prefixlen == (self._max_prefixlen - 1):
            self.hosts = self.__iter__

    def hosts(self):
        """Generate Iterator over usable hosts w a network.

          This jest like __iter__ wyjąwszy it doesn't zwróć the
          Subnet-Router anycast address.

        """
        network = int(self.network_address)
        broadcast = int(self.broadcast_address)
        dla x w range(network + 1, broadcast + 1):
            uzyskaj self._address_class(x)

    @property
    def is_site_local(self):
        """Test jeżeli the address jest reserved dla site-local.

        Note that the site-local address space has been deprecated by RFC 3879.
        Use is_private to test jeżeli this address jest w the space of unique local
        addresses jako defined by RFC 4193.

        Returns:
            A boolean, Prawda jeżeli the address jest reserved per RFC 3513 2.5.6.

        """
        zwróć (self.network_address.is_site_local oraz
                self.broadcast_address.is_site_local)


klasa _IPv6Constants:

    _linklocal_network = IPv6Network('fe80::/10')

    _multicast_network = IPv6Network('ff00::/8')

    _private_networks = [
        IPv6Network('::1/128'),
        IPv6Network('::/128'),
        IPv6Network('::ffff:0:0/96'),
        IPv6Network('100::/64'),
        IPv6Network('2001::/23'),
        IPv6Network('2001:2::/48'),
        IPv6Network('2001:db8::/32'),
        IPv6Network('2001:10::/28'),
        IPv6Network('fc00::/7'),
        IPv6Network('fe80::/10'),
        ]

    _reserved_networks = [
        IPv6Network('::/8'), IPv6Network('100::/8'),
        IPv6Network('200::/7'), IPv6Network('400::/6'),
        IPv6Network('800::/5'), IPv6Network('1000::/4'),
        IPv6Network('4000::/3'), IPv6Network('6000::/3'),
        IPv6Network('8000::/3'), IPv6Network('A000::/3'),
        IPv6Network('C000::/3'), IPv6Network('E000::/4'),
        IPv6Network('F000::/5'), IPv6Network('F800::/6'),
        IPv6Network('FE00::/9'),
    ]

    _sitelocal_network = IPv6Network('fec0::/10')


IPv6Address._constants = _IPv6Constants
