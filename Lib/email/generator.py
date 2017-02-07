# Copyright (C) 2001-2010 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""Classes to generate plain text z a message object tree."""

__all__ = ['Generator', 'DecodedGenerator', 'BytesGenerator']

zaimportuj re
zaimportuj sys
zaimportuj time
zaimportuj random

z copy zaimportuj deepcopy
z io zaimportuj StringIO, BytesIO
z email.utils zaimportuj _has_surrogates

UNDERSCORE = '_'
NL = '\n'  # XXX: no longer used by the code below.

fcre = re.compile(r'^From ', re.MULTILINE)



klasa Generator:
    """Generates output z a Message object tree.

    This basic generator writes the message to the given file object jako plain
    text.
    """
    #
    # Public interface
    #

    def __init__(self, outfp, mangle_from_=Nic, maxheaderlen=Nic, *,
                 policy=Nic):
        """Create the generator dla message flattening.

        outfp jest the output file-like object dla writing the message to.  It
        must have a write() method.

        Optional mangle_from_ jest a flag that, when Prawda (the default jeżeli policy
        jest nie set), escapes From_ lines w the body of the message by putting
        a `>' w front of them.

        Optional maxheaderlen specifies the longest length dla a non-continued
        header.  When a header line jest longer (in characters, przy tabs
        expanded to 8 spaces) than maxheaderlen, the header will split as
        defined w the Header class.  Set maxheaderlen to zero to disable
        header wrapping.  The default jest 78, jako recommended (but nie required)
        by RFC 2822.

        The policy keyword specifies a policy object that controls a number of
        aspects of the generator's operation.  If no policy jest specified,
        the policy associated przy the Message object dalejed to the
        flatten method jest used.

        """

        jeżeli mangle_from_ jest Nic:
            mangle_from_ = Prawda jeżeli policy jest Nic inaczej policy.mangle_from_
        self._fp = outfp
        self._mangle_from_ = mangle_from_
        self.maxheaderlen = maxheaderlen
        self.policy = policy

    def write(self, s):
        # Just delegate to the file object
        self._fp.write(s)

    def flatten(self, msg, unixfrom=Nieprawda, linesep=Nic):
        r"""Print the message object tree rooted at msg to the output file
        specified when the Generator instance was created.

        unixz jest a flag that forces the printing of a Unix From_ delimiter
        before the first object w the message tree.  If the original message
        has no From_ delimiter, a `standard' one jest crafted.  By default, this
        jest Nieprawda to inhibit the printing of any From_ delimiter.

        Note that dla subobjects, no From_ line jest printed.

        linesep specifies the characters used to indicate a new line w
        the output.  The default value jest determined by the policy specified
        when the Generator instance was created or, jeżeli none was specified,
        z the policy associated przy the msg.

        """
        # We use the _XXX constants dla operating on data that comes directly
        # z the msg, oraz _encoded_XXX constants dla operating on data that
        # has already been converted (to bytes w the BytesGenerator) oraz
        # inserted into a temporary buffer.
        policy = msg.policy jeżeli self.policy jest Nic inaczej self.policy
        jeżeli linesep jest nie Nic:
            policy = policy.clone(linesep=linesep)
        jeżeli self.maxheaderlen jest nie Nic:
            policy = policy.clone(max_line_length=self.maxheaderlen)
        self._NL = policy.linesep
        self._encoded_NL = self._encode(self._NL)
        self._EMPTY = ''
        self._encoded_EMTPY = self._encode('')
        # Because we use clone (below) when we recursively process message
        # subparts, oraz because clone uses the computed policy (nie Nic),
        # submessages will automatically get set to the computed policy when
        # they are processed by this code.
        old_gen_policy = self.policy
        old_msg_policy = msg.policy
        spróbuj:
            self.policy = policy
            msg.policy = policy
            jeżeli unixfrom:
                uz = msg.get_unixfrom()
                jeżeli nie ufrom:
                    uz = 'From nobody ' + time.ctime(time.time())
                self.write(uz + self._NL)
            self._write(msg)
        w_końcu:
            self.policy = old_gen_policy
            msg.policy = old_msg_policy

    def clone(self, fp):
        """Clone this generator przy the exact same options."""
        zwróć self.__class__(fp,
                              self._mangle_from_,
                              Nic, # Use policy setting, which we've adjusted
                              policy=self.policy)

    #
    # Protected interface - undocumented ;/
    #

    # Note that we use 'self.write' when what we are writing jest coming from
    # the source, oraz self._fp.write when what we are writing jest coming z a
    # buffer (because the Bytes subclass has already had a chance to transform
    # the data w its write method w that case).  This jest an entirely
    # pragmatic split determined by experiment; we could be more general by
    # always using write oraz having the Bytes subclass write method detect when
    # it has already transformed the input; but, since this whole thing jest a
    # hack anyway this seems good enough.

    # Similarly, we have _XXX oraz _encoded_XXX attributes that are used on
    # source oraz buffer data, respectively.
    _encoded_EMPTY = ''

    def _new_buffer(self):
        # BytesGenerator overrides this to zwróć BytesIO.
        zwróć StringIO()

    def _encode(self, s):
        # BytesGenerator overrides this to encode strings to bytes.
        zwróć s

    def _write_lines(self, lines):
        # We have to transform the line endings.
        jeżeli nie lines:
            zwróć
        lines = lines.splitlines(Prawda)
        dla line w lines[:-1]:
            self.write(line.rstrip('\r\n'))
            self.write(self._NL)
        laststripped = lines[-1].rstrip('\r\n')
        self.write(laststripped)
        jeżeli len(lines[-1]) != len(laststripped):
            self.write(self._NL)

    def _write(self, msg):
        # We can't write the headers yet because of the following scenario:
        # say a multipart message includes the boundary string somewhere w
        # its body.  We'd have to calculate the new boundary /before/ we write
        # the headers so that we can write the correct Content-Type:
        # parameter.
        #
        # The way we do this, so jako to make the _handle_*() methods simpler,
        # jest to cache any subpart writes into a buffer.  The we write the
        # headers oraz the buffer contents.  That way, subpart handlers can
        # Do The Right Thing, oraz can still modify the Content-Type: header if
        # necessary.
        oldfp = self._fp
        spróbuj:
            self._munge_cte = Nic
            self._fp = sfp = self._new_buffer()
            self._dispatch(msg)
        w_końcu:
            self._fp = oldfp
            munge_cte = self._munge_cte
            usuń self._munge_cte
        # If we munged the cte, copy the message again oraz re-fix the CTE.
        jeżeli munge_cte:
            msg = deepcopy(msg)
            msg.replace_header('content-transfer-encoding', munge_cte[0])
            msg.replace_header('content-type', munge_cte[1])
        # Write the headers.  First we see jeżeli the message object wants to
        # handle that itself.  If not, we'll do it generically.
        meth = getattr(msg, '_write_headers', Nic)
        jeżeli meth jest Nic:
            self._write_headers(msg)
        inaczej:
            meth(self)
        self._fp.write(sfp.getvalue())

    def _dispatch(self, msg):
        # Get the Content-Type: dla the message, then try to dispatch to
        # self._handle_<maintype>_<subtype>().  If there's no handler dla the
        # full MIME type, then dispatch to self._handle_<maintype>().  If
        # that's missing too, then dispatch to self._writeBody().
        main = msg.get_content_maintype()
        sub = msg.get_content_subtype()
        specific = UNDERSCORE.join((main, sub)).replace('-', '_')
        meth = getattr(self, '_handle_' + specific, Nic)
        jeżeli meth jest Nic:
            generic = main.replace('-', '_')
            meth = getattr(self, '_handle_' + generic, Nic)
            jeżeli meth jest Nic:
                meth = self._writeBody
        meth(msg)

    #
    # Default handlers
    #

    def _write_headers(self, msg):
        dla h, v w msg.raw_items():
            self.write(self.policy.fold(h, v))
        # A blank line always separates headers z body
        self.write(self._NL)

    #
    # Handlers dla writing types oraz subtypes
    #

    def _handle_text(self, msg):
        payload = msg.get_payload()
        jeżeli payload jest Nic:
            zwróć
        jeżeli nie isinstance(payload, str):
            podnieś TypeError('string payload expected: %s' % type(payload))
        jeżeli _has_surrogates(msg._payload):
            charset = msg.get_param('charset')
            jeżeli charset jest nie Nic:
                # XXX: This copy stuff jest an ugly hack to avoid modifying the
                # existing message.
                msg = deepcopy(msg)
                usuń msg['content-transfer-encoding']
                msg.set_payload(payload, charset)
                payload = msg.get_payload()
                self._munge_cte = (msg['content-transfer-encoding'],
                                   msg['content-type'])
        jeżeli self._mangle_from_:
            payload = fcre.sub('>From ', payload)
        self._write_lines(payload)

    # Default body handler
    _writeBody = _handle_text

    def _handle_multipart(self, msg):
        # The trick here jest to write out each part separately, merge them all
        # together, oraz then make sure that the boundary we've chosen isn't
        # present w the payload.
        msgtexts = []
        subparts = msg.get_payload()
        jeżeli subparts jest Nic:
            subparts = []
        albo_inaczej isinstance(subparts, str):
            # e.g. a non-strict parse of a message przy no starting boundary.
            self.write(subparts)
            zwróć
        albo_inaczej nie isinstance(subparts, list):
            # Scalar payload
            subparts = [subparts]
        dla part w subparts:
            s = self._new_buffer()
            g = self.clone(s)
            g.flatten(part, unixfrom=Nieprawda, linesep=self._NL)
            msgtexts.append(s.getvalue())
        # BAW: What about boundaries that are wrapped w double-quotes?
        boundary = msg.get_boundary()
        jeżeli nie boundary:
            # Create a boundary that doesn't appear w any of the
            # message texts.
            alltext = self._encoded_NL.join(msgtexts)
            boundary = self._make_boundary(alltext)
            msg.set_boundary(boundary)
        # If there's a preamble, write it out, przy a trailing CRLF
        jeżeli msg.preamble jest nie Nic:
            jeżeli self._mangle_from_:
                preamble = fcre.sub('>From ', msg.preamble)
            inaczej:
                preamble = msg.preamble
            self._write_lines(preamble)
            self.write(self._NL)
        # dash-boundary transport-padding CRLF
        self.write('--' + boundary + self._NL)
        # body-part
        jeżeli msgtexts:
            self._fp.write(msgtexts.pop(0))
        # *encapsulation
        # --> delimiter transport-padding
        # --> CRLF body-part
        dla body_part w msgtexts:
            # delimiter transport-padding CRLF
            self.write(self._NL + '--' + boundary + self._NL)
            # body-part
            self._fp.write(body_part)
        # close-delimiter transport-padding
        self.write(self._NL + '--' + boundary + '--' + self._NL)
        jeżeli msg.epilogue jest nie Nic:
            jeżeli self._mangle_from_:
                epilogue = fcre.sub('>From ', msg.epilogue)
            inaczej:
                epilogue = msg.epilogue
            self._write_lines(epilogue)

    def _handle_multipart_signed(self, msg):
        # The contents of signed parts has to stay unmodified w order to keep
        # the signature intact per RFC1847 2.1, so we disable header wrapping.
        # RDM: This isn't enough to completely preserve the part, but it helps.
        p = self.policy
        self.policy = p.clone(max_line_length=0)
        spróbuj:
            self._handle_multipart(msg)
        w_końcu:
            self.policy = p

    def _handle_message_delivery_status(self, msg):
        # We can't just write the headers directly to self's file object
        # because this will leave an extra newline between the last header
        # block oraz the boundary.  Sigh.
        blocks = []
        dla part w msg.get_payload():
            s = self._new_buffer()
            g = self.clone(s)
            g.flatten(part, unixfrom=Nieprawda, linesep=self._NL)
            text = s.getvalue()
            lines = text.split(self._encoded_NL)
            # Strip off the unnecessary trailing empty line
            jeżeli lines oraz lines[-1] == self._encoded_EMPTY:
                blocks.append(self._encoded_NL.join(lines[:-1]))
            inaczej:
                blocks.append(text)
        # Now join all the blocks przy an empty line.  This has the lovely
        # effect of separating each block przy an empty line, but nie adding
        # an extra one after the last one.
        self._fp.write(self._encoded_NL.join(blocks))

    def _handle_message(self, msg):
        s = self._new_buffer()
        g = self.clone(s)
        # The payload of a message/rfc822 part should be a multipart sequence
        # of length 1.  The zeroth element of the list should be the Message
        # object dla the subpart.  Extract that object, stringify it, oraz
        # write it out.
        # Except, it turns out, when it's a string instead, which happens when
        # oraz only when HeaderParser jest used on a message of mime type
        # message/rfc822.  Such messages are generated by, dla example,
        # Groupwise when forwarding unadorned messages.  (Issue 7970.)  So
        # w that case we just emit the string body.
        payload = msg._payload
        jeżeli isinstance(payload, list):
            g.flatten(msg.get_payload(0), unixfrom=Nieprawda, linesep=self._NL)
            payload = s.getvalue()
        inaczej:
            payload = self._encode(payload)
        self._fp.write(payload)

    # This used to be a module level function; we use a classmethod dla this
    # oraz _compile_re so we can continue to provide the module level function
    # dla backward compatibility by doing
    #   _make_boundary = Generator._make_boundary
    # at the end of the module.  It *is* internal, so we could drop that...
    @classmethod
    def _make_boundary(cls, text=Nic):
        # Craft a random boundary.  If text jest given, ensure that the chosen
        # boundary doesn't appear w the text.
        token = random.randrange(sys.maxsize)
        boundary = ('=' * 15) + (_fmt % token) + '=='
        jeżeli text jest Nic:
            zwróć boundary
        b = boundary
        counter = 0
        dopóki Prawda:
            cre = cls._compile_re('^--' + re.escape(b) + '(--)?$', re.MULTILINE)
            jeżeli nie cre.search(text):
                przerwij
            b = boundary + '.' + str(counter)
            counter += 1
        zwróć b

    @classmethod
    def _compile_re(cls, s, flags):
        zwróć re.compile(s, flags)


klasa BytesGenerator(Generator):
    """Generates a bytes version of a Message object tree.

    Functionally identical to the base Generator wyjąwszy that the output jest
    bytes oraz nie string.  When surrogates were used w the input to encode
    bytes, these are decoded back to bytes dla output.  If the policy has
    cte_type set to 7bit, then the message jest transformed such that the
    non-ASCII bytes are properly content transfer encoded, using the charset
    unknown-8bit.

    The outfp object must accept bytes w its write method.
    """

    # Bytes versions of this constant dla use w manipulating data from
    # the BytesIO buffer.
    _encoded_EMPTY = b''

    def write(self, s):
        self._fp.write(s.encode('ascii', 'surrogateescape'))

    def _new_buffer(self):
        zwróć BytesIO()

    def _encode(self, s):
        zwróć s.encode('ascii')

    def _write_headers(self, msg):
        # This jest almost the same jako the string version, wyjąwszy dla handling
        # strings przy 8bit bytes.
        dla h, v w msg.raw_items():
            self._fp.write(self.policy.fold_binary(h, v))
        # A blank line always separates headers z body
        self.write(self._NL)

    def _handle_text(self, msg):
        # If the string has surrogates the original source was bytes, so
        # just write it back out.
        jeżeli msg._payload jest Nic:
            zwróć
        jeżeli _has_surrogates(msg._payload) oraz nie self.policy.cte_type=='7bit':
            jeżeli self._mangle_from_:
                msg._payload = fcre.sub(">From ", msg._payload)
            self._write_lines(msg._payload)
        inaczej:
            super(BytesGenerator,self)._handle_text(msg)

    # Default body handler
    _writeBody = _handle_text

    @classmethod
    def _compile_re(cls, s, flags):
        zwróć re.compile(s.encode('ascii'), flags)



_FMT = '[Non-text (%(type)s) part of message omitted, filename %(filename)s]'

klasa DecodedGenerator(Generator):
    """Generates a text representation of a message.

    Like the Generator base class, wyjąwszy that non-text parts are substituted
    przy a format string representing the part.
    """
    def __init__(self, outfp, mangle_from_=Nic, maxheaderlen=78, fmt=Nic):
        """Like Generator.__init__() wyjąwszy that an additional optional
        argument jest allowed.

        Walks through all subparts of a message.  If the subpart jest of main
        type `text', then it prints the decoded payload of the subpart.

        Otherwise, fmt jest a format string that jest used instead of the message
        payload.  fmt jest expanded przy the following keywords (in
        %(keyword)s format):

        type       : Full MIME type of the non-text part
        maintype   : Main MIME type of the non-text part
        subtype    : Sub-MIME type of the non-text part
        filename   : Filename of the non-text part
        description: Description associated przy the non-text part
        encoding   : Content transfer encoding of the non-text part

        The default value dla fmt jest Nic, meaning

        [Non-text (%(type)s) part of message omitted, filename %(filename)s]
        """
        Generator.__init__(self, outfp, mangle_from_, maxheaderlen)
        jeżeli fmt jest Nic:
            self._fmt = _FMT
        inaczej:
            self._fmt = fmt

    def _dispatch(self, msg):
        dla part w msg.walk():
            maintype = part.get_content_maintype()
            jeżeli maintype == 'text':
                print(part.get_payload(decode=Nieprawda), file=self)
            albo_inaczej maintype == 'multipart':
                # Just skip this
                dalej
            inaczej:
                print(self._fmt % {
                    'type'       : part.get_content_type(),
                    'maintype'   : part.get_content_maintype(),
                    'subtype'    : part.get_content_subtype(),
                    'filename'   : part.get_filename('[no filename]'),
                    'description': part.get('Content-Description',
                                            '[no description]'),
                    'encoding'   : part.get('Content-Transfer-Encoding',
                                            '[no encoding]'),
                    }, file=self)



# Helper used by Generator._make_boundary
_width = len(repr(sys.maxsize-1))
_fmt = '%%0%dd' % _width

# Backward compatibility
_make_boundary = Generator._make_boundary
