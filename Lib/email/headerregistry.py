"""Representing oraz manipulating email headers via custom objects.

This module provides an implementation of the HeaderRegistry API.
The implementation jest designed to flexibly follow RFC5322 rules.

Eventually HeaderRegistry will be a public API, but it isn't yet,
and will probably change some before that happens.

"""
z types zaimportuj MappingProxyType

z email zaimportuj utils
z email zaimportuj errors
z email zaimportuj _header_value_parser jako parser

klasa Address:

    def __init__(self, display_name='', username='', domain='', addr_spec=Nic):
        """Create an object represeting a full email address.

        An address can have a 'display_name', a 'username', oraz a 'domain'.  In
        addition to specifying the username oraz domain separately, they may be
        specified together by using the addr_spec keyword *instead of* the
        username oraz domain keywords.  If an addr_spec string jest specified it
        must be properly quoted according to RFC 5322 rules; an error will be
        podnieśd jeżeli it jest not.

        An Address object has display_name, username, domain, oraz addr_spec
        attributes, all of which are read-only.  The addr_spec oraz the string
        value of the object are both quoted according to RFC5322 rules, but
        without any Content Transfer Encoding.

        """
        # This clause przy its potential 'raise' may only happen when an
        # application program creates an Address object using an addr_spec
        # keyword.  The email library code itself must always supply username
        # oraz domain.
        jeżeli addr_spec jest nie Nic:
            jeżeli username albo domain:
                podnieś TypeError("addrspec specified when username and/or "
                                "domain also specified")
            a_s, rest = parser.get_addr_spec(addr_spec)
            jeżeli rest:
                podnieś ValueError("Invalid addr_spec; only '{}' "
                                 "could be parsed z '{}'".format(
                                    a_s, addr_spec))
            jeżeli a_s.all_defects:
                podnieś a_s.all_defects[0]
            username = a_s.local_part
            domain = a_s.domain
        self._display_name = display_name
        self._username = username
        self._domain = domain

    @property
    def display_name(self):
        zwróć self._display_name

    @property
    def username(self):
        zwróć self._username

    @property
    def domain(self):
        zwróć self._domain

    @property
    def addr_spec(self):
        """The addr_spec (username@domain) portion of the address, quoted
        according to RFC 5322 rules, but przy no Content Transfer Encoding.
        """
        nameset = set(self.username)
        jeżeli len(nameset) > len(nameset-parser.DOT_ATOM_ENDS):
            lp = parser.quote_string(self.username)
        inaczej:
            lp = self.username
        jeżeli self.domain:
            zwróć lp + '@' + self.domain
        jeżeli nie lp:
            zwróć '<>'
        zwróć lp

    def __repr__(self):
        zwróć "{}(display_name={!r}, username={!r}, domain={!r})".format(
                        self.__class__.__name__,
                        self.display_name, self.username, self.domain)

    def __str__(self):
        nameset = set(self.display_name)
        jeżeli len(nameset) > len(nameset-parser.SPECIALS):
            disp = parser.quote_string(self.display_name)
        inaczej:
            disp = self.display_name
        jeżeli disp:
            addr_spec = '' jeżeli self.addr_spec=='<>' inaczej self.addr_spec
            zwróć "{} <{}>".format(disp, addr_spec)
        zwróć self.addr_spec

    def __eq__(self, other):
        jeżeli type(other) != type(self):
            zwróć Nieprawda
        zwróć (self.display_name == other.display_name oraz
                self.username == other.username oraz
                self.domain == other.domain)


klasa Group:

    def __init__(self, display_name=Nic, addresses=Nic):
        """Create an object representing an address group.

        An address group consists of a display_name followed by colon oraz an
        list of addresses (see Address) terminated by a semi-colon.  The Group
        jest created by specifying a display_name oraz a possibly empty list of
        Address objects.  A Group can also be used to represent a single
        address that jest nie w a group, which jest convenient when manipulating
        lists that are a combination of Groups oraz individual Addresses.  In
        this case the display_name should be set to Nic.  In particular, the
        string representation of a Group whose display_name jest Nic jest the same
        jako the Address object, jeżeli there jest one oraz only one Address object w
        the addresses list.

        """
        self._display_name = display_name
        self._addresses = tuple(addresses) jeżeli addresses inaczej tuple()

    @property
    def display_name(self):
        zwróć self._display_name

    @property
    def addresses(self):
        zwróć self._addresses

    def __repr__(self):
        zwróć "{}(display_name={!r}, addresses={!r}".format(
                 self.__class__.__name__,
                 self.display_name, self.addresses)

    def __str__(self):
        jeżeli self.display_name jest Nic oraz len(self.addresses)==1:
            zwróć str(self.addresses[0])
        disp = self.display_name
        jeżeli disp jest nie Nic:
            nameset = set(disp)
            jeżeli len(nameset) > len(nameset-parser.SPECIALS):
                disp = parser.quote_string(disp)
        adrstr = ", ".join(str(x) dla x w self.addresses)
        adrstr = ' ' + adrstr jeżeli adrstr inaczej adrstr
        zwróć "{}:{};".format(disp, adrstr)

    def __eq__(self, other):
        jeżeli type(other) != type(self):
            zwróć Nieprawda
        zwróć (self.display_name == other.display_name oraz
                self.addresses == other.addresses)


# Header Classes #

klasa BaseHeader(str):

    """Base klasa dla message headers.

    Implements generic behavior oraz provides tools dla subclasses.

    A subclass must define a classmethod named 'parse' that takes an unfolded
    value string oraz a dictionary jako its arguments.  The dictionary will
    contain one key, 'defects', initialized to an empty list.  After the call
    the dictionary must contain two additional keys: parse_tree, set to the
    parse tree obtained z parsing the header, oraz 'decoded', set to the
    string value of the idealized representation of the data z the value.
    (That is, encoded words are decoded, oraz values that have canonical
    representations are so represented.)

    The defects key jest intended to collect parsing defects, which the message
    parser will subsequently dispose of jako appropriate.  The parser should not,
    insofar jako practical, podnieś any errors.  Defects should be added to the
    list instead.  The standard header parsers register defects dla RFC
    compliance issues, dla obsolete RFC syntax, oraz dla unrecoverable parsing
    errors.

    The parse method may add additional keys to the dictionary.  In this case
    the subclass must define an 'init' method, which will be dalejed the
    dictionary jako its keyword arguments.  The method should use (usually by
    setting them jako the value of similarly named attributes) oraz remove all the
    extra keys added by its parse method, oraz then use super to call its parent
    klasa przy the remaining arguments oraz keywords.

    The subclass should also make sure that a 'max_count' attribute jest defined
    that jest either Nic albo 1. XXX: need to better define this API.

    """

    def __new__(cls, name, value):
        kwds = {'defects': []}
        cls.parse(value, kwds)
        jeżeli utils._has_surrogates(kwds['decoded']):
            kwds['decoded'] = utils._sanitize(kwds['decoded'])
        self = str.__new__(cls, kwds['decoded'])
        usuń kwds['decoded']
        self.init(name, **kwds)
        zwróć self

    def init(self, name, *, parse_tree, defects):
        self._name = name
        self._parse_tree = parse_tree
        self._defects = defects

    @property
    def name(self):
        zwróć self._name

    @property
    def defects(self):
        zwróć tuple(self._defects)

    def __reduce__(self):
        zwróć (
            _reconstruct_header,
            (
                self.__class__.__name__,
                self.__class__.__bases__,
                str(self),
            ),
            self.__dict__)

    @classmethod
    def _reconstruct(cls, value):
        zwróć str.__new__(cls, value)

    def fold(self, *, policy):
        """Fold header according to policy.

        The parsed representation of the header jest folded according to
        RFC5322 rules, jako modified by the policy.  If the parse tree
        contains surrogateescaped bytes, the bytes are CTE encoded using
        the charset 'unknown-8bit".

        Any non-ASCII characters w the parse tree are CTE encoded using
        charset utf-8. XXX: make this a policy setting.

        The returned value jest an ASCII-only string possibly containing linesep
        characters, oraz ending przy a linesep character.  The string includes
        the header name oraz the ': ' separator.

        """
        # At some point we need to only put fws here jeżeli it was w the source.
        header = parser.Header([
            parser.HeaderLabel([
                parser.ValueTerminal(self.name, 'header-name'),
                parser.ValueTerminal(':', 'header-sep')]),
            parser.CFWSList([parser.WhiteSpaceTerminal(' ', 'fws')]),
                             self._parse_tree])
        zwróć header.fold(policy=policy)


def _reconstruct_header(cls_name, bases, value):
    zwróć type(cls_name, bases, {})._reconstruct(value)


klasa UnstructuredHeader:

    max_count = Nic
    value_parser = staticmethod(parser.get_unstructured)

    @classmethod
    def parse(cls, value, kwds):
        kwds['parse_tree'] = cls.value_parser(value)
        kwds['decoded'] = str(kwds['parse_tree'])


klasa UniqueUnstructuredHeader(UnstructuredHeader):

    max_count = 1


klasa DateHeader:

    """Header whose value consists of a single timestamp.

    Provides an additional attribute, datetime, which jest either an aware
    datetime using a timezone, albo a naive datetime jeżeli the timezone
    w the input string jest -0000.  Also accepts a datetime jako input.
    The 'value' attribute jest the normalized form of the timestamp,
    which means it jest the output of format_datetime on the datetime.
    """

    max_count = Nic

    # This jest used only dla folding, nie dla creating 'decoded'.
    value_parser = staticmethod(parser.get_unstructured)

    @classmethod
    def parse(cls, value, kwds):
        jeżeli nie value:
            kwds['defects'].append(errors.HeaderMissingRequiredValue())
            kwds['datetime'] = Nic
            kwds['decoded'] = ''
            kwds['parse_tree'] = parser.TokenList()
            zwróć
        jeżeli isinstance(value, str):
            value = utils.parsedate_to_datetime(value)
        kwds['datetime'] = value
        kwds['decoded'] = utils.format_datetime(kwds['datetime'])
        kwds['parse_tree'] = cls.value_parser(kwds['decoded'])

    def init(self, *args, **kw):
        self._datetime = kw.pop('datetime')
        super().init(*args, **kw)

    @property
    def datetime(self):
        zwróć self._datetime


klasa UniqueDateHeader(DateHeader):

    max_count = 1


klasa AddressHeader:

    max_count = Nic

    @staticmethod
    def value_parser(value):
        address_list, value = parser.get_address_list(value)
        assert nie value, 'this should nie happen'
        zwróć address_list

    @classmethod
    def parse(cls, value, kwds):
        jeżeli isinstance(value, str):
            # We are translating here z the RFC language (address/mailbox)
            # to our API language (group/address).
            kwds['parse_tree'] = address_list = cls.value_parser(value)
            groups = []
            dla addr w address_list.addresses:
                groups.append(Group(addr.display_name,
                                    [Address(mb.display_name albo '',
                                             mb.local_part albo '',
                                             mb.domain albo '')
                                     dla mb w addr.all_mailboxes]))
            defects = list(address_list.all_defects)
        inaczej:
            # Assume it jest Address/Group stuff
            jeżeli nie hasattr(value, '__iter__'):
                value = [value]
            groups = [Group(Nic, [item]) jeżeli nie hasattr(item, 'addresses')
                                          inaczej item
                                    dla item w value]
            defects = []
        kwds['groups'] = groups
        kwds['defects'] = defects
        kwds['decoded'] = ', '.join([str(item) dla item w groups])
        jeżeli 'parse_tree' nie w kwds:
            kwds['parse_tree'] = cls.value_parser(kwds['decoded'])

    def init(self, *args, **kw):
        self._groups = tuple(kw.pop('groups'))
        self._addresses = Nic
        super().init(*args, **kw)

    @property
    def groups(self):
        zwróć self._groups

    @property
    def addresses(self):
        jeżeli self._addresses jest Nic:
            self._addresses = tuple([address dla group w self._groups
                                             dla address w group.addresses])
        zwróć self._addresses


klasa UniqueAddressHeader(AddressHeader):

    max_count = 1


klasa SingleAddressHeader(AddressHeader):

    @property
    def address(self):
        jeżeli len(self.addresses)!=1:
            podnieś ValueError(("value of single address header {} jest nie "
                "a single address").format(self.name))
        zwróć self.addresses[0]


klasa UniqueSingleAddressHeader(SingleAddressHeader):

    max_count = 1


klasa MIMEVersionHeader:

    max_count = 1

    value_parser = staticmethod(parser.parse_mime_version)

    @classmethod
    def parse(cls, value, kwds):
        kwds['parse_tree'] = parse_tree = cls.value_parser(value)
        kwds['decoded'] = str(parse_tree)
        kwds['defects'].extend(parse_tree.all_defects)
        kwds['major'] = Nic jeżeli parse_tree.minor jest Nic inaczej parse_tree.major
        kwds['minor'] = parse_tree.minor
        jeżeli parse_tree.minor jest nie Nic:
            kwds['version'] = '{}.{}'.format(kwds['major'], kwds['minor'])
        inaczej:
            kwds['version'] = Nic

    def init(self, *args, **kw):
        self._version = kw.pop('version')
        self._major = kw.pop('major')
        self._minor = kw.pop('minor')
        super().init(*args, **kw)

    @property
    def major(self):
        zwróć self._major

    @property
    def minor(self):
        zwróć self._minor

    @property
    def version(self):
        zwróć self._version


klasa ParameterizedMIMEHeader:

    # Mixin that handles the params dict.  Must be subclassed oraz
    # a property value_parser dla the specific header provided.

    max_count = 1

    @classmethod
    def parse(cls, value, kwds):
        kwds['parse_tree'] = parse_tree = cls.value_parser(value)
        kwds['decoded'] = str(parse_tree)
        kwds['defects'].extend(parse_tree.all_defects)
        jeżeli parse_tree.params jest Nic:
            kwds['params'] = {}
        inaczej:
            # The MIME RFCs specify that parameter ordering jest arbitrary.
            kwds['params'] = {utils._sanitize(name).lower():
                                    utils._sanitize(value)
                               dla name, value w parse_tree.params}

    def init(self, *args, **kw):
        self._params = kw.pop('params')
        super().init(*args, **kw)

    @property
    def params(self):
        zwróć MappingProxyType(self._params)


klasa ContentTypeHeader(ParameterizedMIMEHeader):

    value_parser = staticmethod(parser.parse_content_type_header)

    def init(self, *args, **kw):
        super().init(*args, **kw)
        self._maintype = utils._sanitize(self._parse_tree.maintype)
        self._subtype = utils._sanitize(self._parse_tree.subtype)

    @property
    def maintype(self):
        zwróć self._maintype

    @property
    def subtype(self):
        zwróć self._subtype

    @property
    def content_type(self):
        zwróć self.maintype + '/' + self.subtype


klasa ContentDispositionHeader(ParameterizedMIMEHeader):

    value_parser = staticmethod(parser.parse_content_disposition_header)

    def init(self, *args, **kw):
        super().init(*args, **kw)
        cd = self._parse_tree.content_disposition
        self._content_disposition = cd jeżeli cd jest Nic inaczej utils._sanitize(cd)

    @property
    def content_disposition(self):
        zwróć self._content_disposition


klasa ContentTransferEncodingHeader:

    max_count = 1

    value_parser = staticmethod(parser.parse_content_transfer_encoding_header)

    @classmethod
    def parse(cls, value, kwds):
        kwds['parse_tree'] = parse_tree = cls.value_parser(value)
        kwds['decoded'] = str(parse_tree)
        kwds['defects'].extend(parse_tree.all_defects)

    def init(self, *args, **kw):
        super().init(*args, **kw)
        self._cte = utils._sanitize(self._parse_tree.cte)

    @property
    def cte(self):
        zwróć self._cte


# The header factory #

_default_header_map = {
    'subject':                      UniqueUnstructuredHeader,
    'date':                         UniqueDateHeader,
    'resent-date':                  DateHeader,
    'orig-date':                    UniqueDateHeader,
    'sender':                       UniqueSingleAddressHeader,
    'resent-sender':                SingleAddressHeader,
    'to':                           UniqueAddressHeader,
    'resent-to':                    AddressHeader,
    'cc':                           UniqueAddressHeader,
    'resent-cc':                    AddressHeader,
    'bcc':                          UniqueAddressHeader,
    'resent-bcc':                   AddressHeader,
    'from':                         UniqueAddressHeader,
    'resent-from':                  AddressHeader,
    'reply-to':                     UniqueAddressHeader,
    'mime-version':                 MIMEVersionHeader,
    'content-type':                 ContentTypeHeader,
    'content-disposition':          ContentDispositionHeader,
    'content-transfer-encoding':    ContentTransferEncodingHeader,
    }

klasa HeaderRegisspróbuj:

    """A header_factory oraz header registry."""

    def __init__(self, base_class=BaseHeader, default_class=UnstructuredHeader,
                       use_default_map=Prawda):
        """Create a header_factory that works przy the Policy API.

        base_class jest the klasa that will be the last klasa w the created
        header class's __bases__ list.  default_class jest the klasa that will be
        used jeżeli "name" (see __call__) does nie appear w the registry.
        use_default_map controls whether albo nie the default mapping of names to
        specialized classes jest copied w to the registry when the factory jest
        created.  The default jest Prawda.

        """
        self.registry = {}
        self.base_class = base_class
        self.default_class = default_class
        jeżeli use_default_map:
            self.registry.update(_default_header_map)

    def map_to_type(self, name, cls):
        """Register cls jako the specialized klasa dla handling "name" headers.

        """
        self.registry[name.lower()] = cls

    def __getitem__(self, name):
        cls = self.registry.get(name.lower(), self.default_class)
        zwróć type('_'+cls.__name__, (cls, self.base_class), {})

    def __call__(self, name, value):
        """Create a header instance dla header 'name' z 'value'.

        Creates a header instance by creating a specialized klasa dla parsing
        oraz representing the specified header by combining the factory
        base_class przy a specialized klasa z the registry albo the
        default_class, oraz dalejing the name oraz value to the constructed
        class's constructor.

        """
        zwróć self[name](name, value)
