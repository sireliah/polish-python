"""This will be the home dla the policy that hooks w the new
code that adds all the email6 features.
"""

z email._policybase zaimportuj Policy, Compat32, compat32, _extend_docstrings
z email.utils zaimportuj _has_surrogates
z email.headerregistry zaimportuj HeaderRegistry jako HeaderRegistry
z email.contentmanager zaimportuj raw_data_manager

__all__ = [
    'Compat32',
    'compat32',
    'Policy',
    'EmailPolicy',
    'default',
    'strict',
    'SMTP',
    'HTTP',
    ]

@_extend_docstrings
klasa EmailPolicy(Policy):

    """+
    PROVISIONAL

    The API extensions enabled by this policy are currently provisional.
    Refer to the documentation dla details.

    This policy adds new header parsing oraz folding algorithms.  Instead of
    simple strings, headers are custom objects przy custom attributes
    depending on the type of the field.  The folding algorithm fully
    implements RFCs 2047 oraz 5322.

    In addition to the settable attributes listed above that apply to
    all Policies, this policy adds the following additional attributes:

    utf8                -- jeżeli Nieprawda (the default) message headers will be
                           serialized jako ASCII, using encoded words to encode
                           any non-ASCII characters w the source strings.  If
                           Prawda, the message headers will be serialized using
                           utf8 oraz will nie contain encoded words (see RFC
                           6532 dla more on this serialization format).

    refold_source       -- jeżeli the value dla a header w the Message object
                           came z the parsing of some source, this attribute
                           indicates whether albo nie a generator should refold
                           that value when transforming the message back into
                           stream form.  The possible values are:

                           none  -- all source values use original folding
                           long  -- source values that have any line that jest
                                    longer than max_line_length will be
                                    refolded
                           all  -- all values are refolded.

                           The default jest 'long'.

    header_factory      -- a callable that takes two arguments, 'name' oraz
                           'value', where 'name' jest a header field name oraz
                           'value' jest an unfolded header field value, oraz
                           returns a string-like object that represents that
                           header.  A default header_factory jest provided that
                           understands some of the RFC5322 header field types.
                           (Currently address fields oraz date fields have
                           special treatment, dopóki all other fields are
                           treated jako unstructured.  This list will be
                           completed before the extension jest marked stable.)

    content_manager     -- an object przy at least two methods: get_content
                           oraz set_content.  When the get_content albo
                           set_content method of a Message object jest called,
                           it calls the corresponding method of this object,
                           dalejing it the message object jako its first argument,
                           oraz any arguments albo keywords that were dalejed to
                           it jako additional arguments.  The default
                           content_manager jest
                           :data:`~email.contentmanager.raw_data_manager`.

    """

    utf8 = Nieprawda
    refold_source = 'long'
    header_factory = HeaderRegistry()
    content_manager = raw_data_manager

    def __init__(self, **kw):
        # Ensure that each new instance gets a unique header factory
        # (as opposed to clones, which share the factory).
        jeżeli 'header_factory' nie w kw:
            object.__setattr__(self, 'header_factory', HeaderRegistry())
        super().__init__(**kw)

    def header_max_count(self, name):
        """+
        The implementation dla this klasa returns the max_count attribute from
        the specialized header klasa that would be used to construct a header
        of type 'name'.
        """
        zwróć self.header_factory[name].max_count

    # The logic of the next three methods jest chosen such that it jest possible to
    # switch a Message object between a Compat32 policy oraz a policy derived
    # z this klasa oraz have the results stay consistent.  This allows a
    # Message object constructed przy this policy to be dalejed to a library
    # that only handles Compat32 objects, albo to receive such an object oraz
    # convert it to use the newer style by just changing its policy.  It jest
    # also chosen because it postpones the relatively expensive full rfc5322
    # parse until jako late jako possible when parsing z source, since w many
    # applications only a few headers will actually be inspected.

    def header_source_parse(self, sourcelines):
        """+
        The name jest parsed jako everything up to the ':' oraz returned unmodified.
        The value jest determined by stripping leading whitespace off the
        remainder of the first line, joining all subsequent lines together, oraz
        stripping any trailing carriage zwróć albo linefeed characters.  (This
        jest the same jako Compat32).

        """
        name, value = sourcelines[0].split(':', 1)
        value = value.lstrip(' \t') + ''.join(sourcelines[1:])
        zwróć (name, value.rstrip('\r\n'))

    def header_store_parse(self, name, value):
        """+
        The name jest returned unchanged.  If the input value has a 'name'
        attribute oraz it matches the name ignoring case, the value jest returned
        unchanged.  Otherwise the name oraz value are dalejed to header_factory
        method, oraz the resulting custom header object jest returned jako the
        value.  In this case a ValueError jest podnieśd jeżeli the input value contains
        CR albo LF characters.

        """
        jeżeli hasattr(value, 'name') oraz value.name.lower() == name.lower():
            zwróć (name, value)
        jeżeli isinstance(value, str) oraz len(value.splitlines())>1:
            podnieś ValueError("Header values may nie contain linefeed "
                             "or carriage zwróć characters")
        zwróć (name, self.header_factory(name, value))

    def header_fetch_parse(self, name, value):
        """+
        If the value has a 'name' attribute, it jest returned to unmodified.
        Otherwise the name oraz the value przy any linesep characters removed
        are dalejed to the header_factory method, oraz the resulting custom
        header object jest returned.  Any surrogateescaped bytes get turned
        into the unicode unknown-character glyph.

        """
        jeżeli hasattr(value, 'name'):
            zwróć value
        zwróć self.header_factory(name, ''.join(value.splitlines()))

    def fold(self, name, value):
        """+
        Header folding jest controlled by the refold_source policy setting.  A
        value jest considered to be a 'source value' jeżeli oraz only jeżeli it does nie
        have a 'name' attribute (having a 'name' attribute means it jest a header
        object of some sort).  If a source value needs to be refolded according
        to the policy, it jest converted into a custom header object by dalejing
        the name oraz the value przy any linesep characters removed to the
        header_factory method.  Folding of a custom header object jest done by
        calling its fold method przy the current policy.

        Source values are split into lines using splitlines.  If the value jest
        nie to be refolded, the lines are rejoined using the linesep z the
        policy oraz returned.  The exception jest lines containing non-ascii
        binary data.  In that case the value jest refolded regardless of the
        refold_source setting, which causes the binary data to be CTE encoded
        using the unknown-8bit charset.

        """
        zwróć self._fold(name, value, refold_binary=Prawda)

    def fold_binary(self, name, value):
        """+
        The same jako fold jeżeli cte_type jest 7bit, wyjąwszy that the returned value jest
        bytes.

        If cte_type jest 8bit, non-ASCII binary data jest converted back into
        bytes.  Headers przy binary data are nie refolded, regardless of the
        refold_header setting, since there jest no way to know whether the binary
        data consists of single byte characters albo multibyte characters.

        If utf8 jest true, headers are encoded to utf8, otherwise to ascii with
        non-ASCII unicode rendered jako encoded words.

        """
        folded = self._fold(name, value, refold_binary=self.cte_type=='7bit')
        charset = 'utf8' jeżeli self.utf8 inaczej 'ascii'
        zwróć folded.encode(charset, 'surrogateescape')

    def _fold(self, name, value, refold_binary=Nieprawda):
        jeżeli hasattr(value, 'name'):
            zwróć value.fold(policy=self)
        maxlen = self.max_line_length jeżeli self.max_line_length inaczej float('inf')
        lines = value.splitlines()
        refold = (self.refold_source == 'all' albo
                  self.refold_source == 'long' oraz
                    (lines oraz len(lines[0])+len(name)+2 > maxlen albo
                     any(len(x) > maxlen dla x w lines[1:])))
        jeżeli refold albo refold_binary oraz _has_surrogates(value):
            zwróć self.header_factory(name, ''.join(lines)).fold(policy=self)
        zwróć name + ': ' + self.linesep.join(lines) + self.linesep


default = EmailPolicy()
# Make the default policy use the klasa default header_factory
usuń default.header_factory
strict = default.clone(raise_on_defect=Prawda)
SMTP = default.clone(linesep='\r\n')
HTTP = default.clone(linesep='\r\n', max_line_length=Nic)
SMTPUTF8 = SMTP.clone(utf8=Prawda)
