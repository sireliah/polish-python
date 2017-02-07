# Copyright (C) 2001-2007 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""Basic message object dla the email package object model."""

__all__ = ['Message']

zaimportuj re
zaimportuj uu
zaimportuj quopri
zaimportuj warnings
z io zaimportuj BytesIO, StringIO

# Intrapackage imports
z email zaimportuj utils
z email zaimportuj errors
z email._policybase zaimportuj compat32
z email zaimportuj charset jako _charset
z email._encoded_words zaimportuj decode_b
Charset = _charset.Charset

SEMISPACE = '; '

# Regular expression that matches `special' characters w parameters, the
# existence of which force quoting of the parameter value.
tspecials = re.compile(r'[ \(\)<>@,;:\\"/\[\]\?=]')


def _splitparam(param):
    # Split header parameters.  BAW: this may be too simple.  It isn't
    # strictly RFC 2045 (section 5.1) compliant, but it catches most headers
    # found w the wild.  We may eventually need a full fledged parser.
    # RDM: we might have a Header here; dla now just stringify it.
    a, sep, b = str(param).partition(';')
    jeżeli nie sep:
        zwróć a.strip(), Nic
    zwróć a.strip(), b.strip()

def _formatparam(param, value=Nic, quote=Prawda):
    """Convenience function to format oraz zwróć a key=value pair.

    This will quote the value jeżeli needed albo jeżeli quote jest true.  If value jest a
    three tuple (charset, language, value), it will be encoded according
    to RFC2231 rules.  If it contains non-ascii characters it will likewise
    be encoded according to RFC2231 rules, using the utf-8 charset oraz
    a null language.
    """
    jeżeli value jest nie Nic oraz len(value) > 0:
        # A tuple jest used dla RFC 2231 encoded parameter values where items
        # are (charset, language, value).  charset jest a string, nie a Charset
        # instance.  RFC 2231 encoded values are never quoted, per RFC.
        jeżeli isinstance(value, tuple):
            # Encode jako per RFC 2231
            param += '*'
            value = utils.encode_rfc2231(value[2], value[0], value[1])
            zwróć '%s=%s' % (param, value)
        inaczej:
            spróbuj:
                value.encode('ascii')
            wyjąwszy UnicodeEncodeError:
                param += '*'
                value = utils.encode_rfc2231(value, 'utf-8', '')
                zwróć '%s=%s' % (param, value)
        # BAW: Please check this.  I think that jeżeli quote jest set it should
        # force quoting even jeżeli nie necessary.
        jeżeli quote albo tspecials.search(value):
            zwróć '%s="%s"' % (param, utils.quote(value))
        inaczej:
            zwróć '%s=%s' % (param, value)
    inaczej:
        zwróć param

def _parseparam(s):
    # RDM This might be a Header, so dla now stringify it.
    s = ';' + str(s)
    plist = []
    dopóki s[:1] == ';':
        s = s[1:]
        end = s.find(';')
        dopóki end > 0 oraz (s.count('"', 0, end) - s.count('\\"', 0, end)) % 2:
            end = s.find(';', end + 1)
        jeżeli end < 0:
            end = len(s)
        f = s[:end]
        jeżeli '=' w f:
            i = f.index('=')
            f = f[:i].strip().lower() + '=' + f[i+1:].strip()
        plist.append(f.strip())
        s = s[end:]
    zwróć plist


def _unquotevalue(value):
    # This jest different than utils.collapse_rfc2231_value() because it doesn't
    # try to convert the value to a unicode.  Message.get_param() oraz
    # Message.get_params() are both currently defined to zwróć the tuple w
    # the face of RFC 2231 parameters.
    jeżeli isinstance(value, tuple):
        zwróć value[0], value[1], utils.unquote(value[2])
    inaczej:
        zwróć utils.unquote(value)



klasa Message:
    """Basic message object.

    A message object jest defined jako something that has a bunch of RFC 2822
    headers oraz a payload.  It may optionally have an envelope header
    (a.k.a. Unix-From albo From_ header).  If the message jest a container (i.e. a
    multipart albo a message/rfc822), then the payload jest a list of Message
    objects, otherwise it jest a string.

    Message objects implement part of the `mapping' interface, which assumes
    there jest exactly one occurrence of the header per message.  Some headers
    do w fact appear multiple times (e.g. Received) oraz dla those headers,
    you must use the explicit API to set albo get all the headers.  Not all of
    the mapping methods are implemented.
    """
    def __init__(self, policy=compat32):
        self.policy = policy
        self._headers = []
        self._unixz = Nic
        self._payload = Nic
        self._charset = Nic
        # Defaults dla multipart messages
        self.preamble = self.epilogue = Nic
        self.defects = []
        # Default content type
        self._default_type = 'text/plain'

    def __str__(self):
        """Return the entire formatted message jako a string.
        """
        zwróć self.as_string()

    def as_string(self, unixfrom=Nieprawda, maxheaderlen=0, policy=Nic):
        """Return the entire formatted message jako a string.

        Optional 'unixfrom', when true, means include the Unix From_ envelope
        header.  For backward compatibility reasons, jeżeli maxheaderlen jest
        nie specified it defaults to 0, so you must override it explicitly
        jeżeli you want a different maxheaderlen.  'policy' jest dalejed to the
        Generator instance used to serialize the mesasge; jeżeli it jest nie
        specified the policy associated przy the message instance jest used.

        If the message object contains binary data that jest nie encoded
        according to RFC standards, the non-compliant data will be replaced by
        unicode "unknown character" code points.
        """
        z email.generator zaimportuj Generator
        policy = self.policy jeżeli policy jest Nic inaczej policy
        fp = StringIO()
        g = Generator(fp,
                      mangle_from_=Nieprawda,
                      maxheaderlen=maxheaderlen,
                      policy=policy)
        g.flatten(self, unixfrom=unixfrom)
        zwróć fp.getvalue()

    def __bytes__(self):
        """Return the entire formatted message jako a bytes object.
        """
        zwróć self.as_bytes()

    def as_bytes(self, unixfrom=Nieprawda, policy=Nic):
        """Return the entire formatted message jako a bytes object.

        Optional 'unixfrom', when true, means include the Unix From_ envelope
        header.  'policy' jest dalejed to the BytesGenerator instance used to
        serialize the message; jeżeli nie specified the policy associated with
        the message instance jest used.
        """
        z email.generator zaimportuj BytesGenerator
        policy = self.policy jeżeli policy jest Nic inaczej policy
        fp = BytesIO()
        g = BytesGenerator(fp, mangle_from_=Nieprawda, policy=policy)
        g.flatten(self, unixfrom=unixfrom)
        zwróć fp.getvalue()

    def is_multipart(self):
        """Return Prawda jeżeli the message consists of multiple parts."""
        zwróć isinstance(self._payload, list)

    #
    # Unix From_ line
    #
    def set_unixfrom(self, unixfrom):
        self._unixz = unixfrom

    def get_unixfrom(self):
        zwróć self._unixfrom

    #
    # Payload manipulation.
    #
    def attach(self, payload):
        """Add the given payload to the current payload.

        The current payload will always be a list of objects after this method
        jest called.  If you want to set the payload to a scalar object, use
        set_payload() instead.
        """
        jeżeli self._payload jest Nic:
            self._payload = [payload]
        inaczej:
            spróbuj:
                self._payload.append(payload)
            wyjąwszy AttributeError:
                podnieś TypeError("Attach jest nie valid on a message przy a"
                                " non-multipart payload")

    def get_payload(self, i=Nic, decode=Nieprawda):
        """Return a reference to the payload.

        The payload will either be a list object albo a string.  If you mutate
        the list object, you modify the message's payload w place.  Optional
        i returns that index into the payload.

        Optional decode jest a flag indicating whether the payload should be
        decoded albo not, according to the Content-Transfer-Encoding header
        (default jest Nieprawda).

        When Prawda oraz the message jest nie a multipart, the payload will be
        decoded jeżeli this header's value jest `quoted-printable' albo `base64'.  If
        some other encoding jest used, albo the header jest missing, albo jeżeli the
        payload has bogus data (i.e. bogus base64 albo uuencoded data), the
        payload jest returned as-is.

        If the message jest a multipart oraz the decode flag jest Prawda, then Nic
        jest returned.
        """
        # Here jest the logic table dla this code, based on the email5.0.0 code:
        #   i     decode  is_multipart  result
        # ------  ------  ------------  ------------------------------
        #  Nic   Prawda    Prawda          Nic
        #   i     Prawda    Prawda          Nic
        #  Nic   Nieprawda   Prawda          _payload (a list)
        #   i     Nieprawda   Prawda          _payload element i (a Message)
        #   i     Nieprawda   Nieprawda         error (nie a list)
        #   i     Prawda    Nieprawda         error (nie a list)
        #  Nic   Nieprawda   Nieprawda         _payload
        #  Nic   Prawda    Nieprawda         _payload decoded (bytes)
        # Note that Barry planned to factor out the 'decode' case, but that
        # isn't so easy now that we handle the 8 bit data, which needs to be
        # converted w both the decode oraz non-decode path.
        jeżeli self.is_multipart():
            jeżeli decode:
                zwróć Nic
            jeżeli i jest Nic:
                zwróć self._payload
            inaczej:
                zwróć self._payload[i]
        # For backward compatibility, Use isinstance oraz this error message
        # instead of the more logical is_multipart test.
        jeżeli i jest nie Nic oraz nie isinstance(self._payload, list):
            podnieś TypeError('Expected list, got %s' % type(self._payload))
        payload = self._payload
        # cte might be a Header, so dla now stringify it.
        cte = str(self.get('content-transfer-encoding', '')).lower()
        # payload may be bytes here.
        jeżeli isinstance(payload, str):
            jeżeli utils._has_surrogates(payload):
                bpayload = payload.encode('ascii', 'surrogateescape')
                jeżeli nie decode:
                    spróbuj:
                        payload = bpayload.decode(self.get_param('charset', 'ascii'), 'replace')
                    wyjąwszy LookupError:
                        payload = bpayload.decode('ascii', 'replace')
            albo_inaczej decode:
                spróbuj:
                    bpayload = payload.encode('ascii')
                wyjąwszy UnicodeError:
                    # This won't happen dla RFC compliant messages (messages
                    # containing only ASCII code points w the unicode input).
                    # If it does happen, turn the string into bytes w a way
                    # guaranteed nie to fail.
                    bpayload = payload.encode('raw-unicode-escape')
        jeżeli nie decode:
            zwróć payload
        jeżeli cte == 'quoted-printable':
            zwróć quopri.decodestring(bpayload)
        albo_inaczej cte == 'base64':
            # XXX: this jest a bit of a hack; decode_b should probably be factored
            # out somewhere, but I haven't figured out where yet.
            value, defects = decode_b(b''.join(bpayload.splitlines()))
            dla defect w defects:
                self.policy.handle_defect(self, defect)
            zwróć value
        albo_inaczej cte w ('x-uuencode', 'uuencode', 'uue', 'x-uue'):
            in_file = BytesIO(bpayload)
            out_file = BytesIO()
            spróbuj:
                uu.decode(in_file, out_file, quiet=Prawda)
                zwróć out_file.getvalue()
            wyjąwszy uu.Error:
                # Some decoding problem
                zwróć bpayload
        jeżeli isinstance(payload, str):
            zwróć bpayload
        zwróć payload

    def set_payload(self, payload, charset=Nic):
        """Set the payload to the given value.

        Optional charset sets the message's default character set.  See
        set_charset() dla details.
        """
        jeżeli hasattr(payload, 'encode'):
            jeżeli charset jest Nic:
                self._payload = payload
                zwróć
            jeżeli nie isinstance(charset, Charset):
                charset = Charset(charset)
            payload = payload.encode(charset.output_charset)
        jeżeli hasattr(payload, 'decode'):
            self._payload = payload.decode('ascii', 'surrogateescape')
        inaczej:
            self._payload = payload
        jeżeli charset jest nie Nic:
            self.set_charset(charset)

    def set_charset(self, charset):
        """Set the charset of the payload to a given character set.

        charset can be a Charset instance, a string naming a character set, albo
        Nic.  If it jest a string it will be converted to a Charset instance.
        If charset jest Nic, the charset parameter will be removed z the
        Content-Type field.  Anything inaczej will generate a TypeError.

        The message will be assumed to be of type text/* encoded with
        charset.input_charset.  It will be converted to charset.output_charset
        oraz encoded properly, jeżeli needed, when generating the plain text
        representation of the message.  MIME headers (MIME-Version,
        Content-Type, Content-Transfer-Encoding) will be added jako needed.
        """
        jeżeli charset jest Nic:
            self.del_param('charset')
            self._charset = Nic
            zwróć
        jeżeli nie isinstance(charset, Charset):
            charset = Charset(charset)
        self._charset = charset
        jeżeli 'MIME-Version' nie w self:
            self.add_header('MIME-Version', '1.0')
        jeżeli 'Content-Type' nie w self:
            self.add_header('Content-Type', 'text/plain',
                            charset=charset.get_output_charset())
        inaczej:
            self.set_param('charset', charset.get_output_charset())
        jeżeli charset != charset.get_output_charset():
            self._payload = charset.body_encode(self._payload)
        jeżeli 'Content-Transfer-Encoding' nie w self:
            cte = charset.get_body_encoding()
            spróbuj:
                cte(self)
            wyjąwszy TypeError:
                # This 'if' jest dla backward compatibility, it allows unicode
                # through even though that won't work correctly jeżeli the
                # message jest serialized.
                payload = self._payload
                jeżeli payload:
                    spróbuj:
                        payload = payload.encode('ascii', 'surrogateescape')
                    wyjąwszy UnicodeError:
                        payload = payload.encode(charset.output_charset)
                self._payload = charset.body_encode(payload)
                self.add_header('Content-Transfer-Encoding', cte)

    def get_charset(self):
        """Return the Charset instance associated przy the message's payload.
        """
        zwróć self._charset

    #
    # MAPPING INTERFACE (partial)
    #
    def __len__(self):
        """Return the total number of headers, including duplicates."""
        zwróć len(self._headers)

    def __getitem__(self, name):
        """Get a header value.

        Return Nic jeżeli the header jest missing instead of raising an exception.

        Note that jeżeli the header appeared multiple times, exactly which
        occurrence gets returned jest undefined.  Use get_all() to get all
        the values matching a header field name.
        """
        zwróć self.get(name)

    def __setitem__(self, name, val):
        """Set the value of a header.

        Note: this does nie overwrite an existing header przy the same field
        name.  Use __delitem__() first to delete any existing headers.
        """
        max_count = self.policy.header_max_count(name)
        jeżeli max_count:
            lname = name.lower()
            found = 0
            dla k, v w self._headers:
                jeżeli k.lower() == lname:
                    found += 1
                    jeżeli found >= max_count:
                        podnieś ValueError("There may be at most {} {} headers "
                                         "in a message".format(max_count, name))
        self._headers.append(self.policy.header_store_parse(name, val))

    def __delitem__(self, name):
        """Delete all occurrences of a header, jeżeli present.

        Does nie podnieś an exception jeżeli the header jest missing.
        """
        name = name.lower()
        newheaders = []
        dla k, v w self._headers:
            jeżeli k.lower() != name:
                newheaders.append((k, v))
        self._headers = newheaders

    def __contains__(self, name):
        zwróć name.lower() w [k.lower() dla k, v w self._headers]

    def __iter__(self):
        dla field, value w self._headers:
            uzyskaj field

    def keys(self):
        """Return a list of all the message's header field names.

        These will be sorted w the order they appeared w the original
        message, albo were added to the message, oraz may contain duplicates.
        Any fields deleted oraz re-inserted are always appended to the header
        list.
        """
        zwróć [k dla k, v w self._headers]

    def values(self):
        """Return a list of all the message's header values.

        These will be sorted w the order they appeared w the original
        message, albo were added to the message, oraz may contain duplicates.
        Any fields deleted oraz re-inserted are always appended to the header
        list.
        """
        zwróć [self.policy.header_fetch_parse(k, v)
                dla k, v w self._headers]

    def items(self):
        """Get all the message's header fields oraz values.

        These will be sorted w the order they appeared w the original
        message, albo were added to the message, oraz may contain duplicates.
        Any fields deleted oraz re-inserted are always appended to the header
        list.
        """
        zwróć [(k, self.policy.header_fetch_parse(k, v))
                dla k, v w self._headers]

    def get(self, name, failobj=Nic):
        """Get a header value.

        Like __getitem__() but zwróć failobj instead of Nic when the field
        jest missing.
        """
        name = name.lower()
        dla k, v w self._headers:
            jeżeli k.lower() == name:
                zwróć self.policy.header_fetch_parse(k, v)
        zwróć failobj

    #
    # "Internal" methods (public API, but only intended dla use by a parser
    # albo generator, nie normal application code.
    #

    def set_raw(self, name, value):
        """Store name oraz value w the mousuń without modification.

        This jest an "internal" API, intended only dla use by a parser.
        """
        self._headers.append((name, value))

    def raw_items(self):
        """Return the (name, value) header pairs without modification.

        This jest an "internal" API, intended only dla use by a generator.
        """
        zwróć iter(self._headers.copy())

    #
    # Additional useful stuff
    #

    def get_all(self, name, failobj=Nic):
        """Return a list of all the values dla the named field.

        These will be sorted w the order they appeared w the original
        message, oraz may contain duplicates.  Any fields deleted oraz
        re-inserted are always appended to the header list.

        If no such fields exist, failobj jest returned (defaults to Nic).
        """
        values = []
        name = name.lower()
        dla k, v w self._headers:
            jeżeli k.lower() == name:
                values.append(self.policy.header_fetch_parse(k, v))
        jeżeli nie values:
            zwróć failobj
        zwróć values

    def add_header(self, _name, _value, **_params):
        """Extended header setting.

        name jest the header field to add.  keyword arguments can be used to set
        additional parameters dla the header field, przy underscores converted
        to dashes.  Normally the parameter will be added jako key="value" unless
        value jest Nic, w which case only the key will be added.  If a
        parameter value contains non-ASCII characters it can be specified jako a
        three-tuple of (charset, language, value), w which case it will be
        encoded according to RFC2231 rules.  Otherwise it will be encoded using
        the utf-8 charset oraz a language of ''.

        Examples:

        msg.add_header('content-disposition', 'attachment', filename='bud.gif')
        msg.add_header('content-disposition', 'attachment',
                       filename=('utf-8', '', Fußballer.ppt'))
        msg.add_header('content-disposition', 'attachment',
                       filename='Fußballer.ppt'))
        """
        parts = []
        dla k, v w _params.items():
            jeżeli v jest Nic:
                parts.append(k.replace('_', '-'))
            inaczej:
                parts.append(_formatparam(k.replace('_', '-'), v))
        jeżeli _value jest nie Nic:
            parts.insert(0, _value)
        self[_name] = SEMISPACE.join(parts)

    def replace_header(self, _name, _value):
        """Replace a header.

        Replace the first matching header found w the message, retaining
        header order oraz case.  If no matching header was found, a KeyError jest
        podnieśd.
        """
        _name = _name.lower()
        dla i, (k, v) w zip(range(len(self._headers)), self._headers):
            jeżeli k.lower() == _name:
                self._headers[i] = self.policy.header_store_parse(k, _value)
                przerwij
        inaczej:
            podnieś KeyError(_name)

    #
    # Use these three methods instead of the three above.
    #

    def get_content_type(self):
        """Return the message's content type.

        The returned string jest coerced to lower case of the form
        `maintype/subtype'.  If there was no Content-Type header w the
        message, the default type jako given by get_default_type() will be
        returned.  Since according to RFC 2045, messages always have a default
        type this will always zwróć a value.

        RFC 2045 defines a message's default type to be text/plain unless it
        appears inside a multipart/digest container, w which case it would be
        message/rfc822.
        """
        missing = object()
        value = self.get('content-type', missing)
        jeżeli value jest missing:
            # This should have no parameters
            zwróć self.get_default_type()
        ctype = _splitparam(value)[0].lower()
        # RFC 2045, section 5.2 says jeżeli its invalid, use text/plain
        jeżeli ctype.count('/') != 1:
            zwróć 'text/plain'
        zwróć ctype

    def get_content_maintype(self):
        """Return the message's main content type.

        This jest the `maintype' part of the string returned by
        get_content_type().
        """
        ctype = self.get_content_type()
        zwróć ctype.split('/')[0]

    def get_content_subtype(self):
        """Returns the message's sub-content type.

        This jest the `subtype' part of the string returned by
        get_content_type().
        """
        ctype = self.get_content_type()
        zwróć ctype.split('/')[1]

    def get_default_type(self):
        """Return the `default' content type.

        Most messages have a default content type of text/plain, wyjąwszy for
        messages that are subparts of multipart/digest containers.  Such
        subparts have a default content type of message/rfc822.
        """
        zwróć self._default_type

    def set_default_type(self, ctype):
        """Set the `default' content type.

        ctype should be either "text/plain" albo "message/rfc822", although this
        jest nie enforced.  The default content type jest nie stored w the
        Content-Type header.
        """
        self._default_type = ctype

    def _get_params_preserve(self, failobj, header):
        # Like get_params() but preserves the quoting of values.  BAW:
        # should this be part of the public interface?
        missing = object()
        value = self.get(header, missing)
        jeżeli value jest missing:
            zwróć failobj
        params = []
        dla p w _parseparam(value):
            spróbuj:
                name, val = p.split('=', 1)
                name = name.strip()
                val = val.strip()
            wyjąwszy ValueError:
                # Must have been a bare attribute
                name = p.strip()
                val = ''
            params.append((name, val))
        params = utils.decode_params(params)
        zwróć params

    def get_params(self, failobj=Nic, header='content-type', unquote=Prawda):
        """Return the message's Content-Type parameters, jako a list.

        The elements of the returned list are 2-tuples of key/value pairs, as
        split on the `=' sign.  The left hand side of the `=' jest the key,
        dopóki the right hand side jest the value.  If there jest no `=' sign w
        the parameter the value jest the empty string.  The value jest as
        described w the get_param() method.

        Optional failobj jest the object to zwróć jeżeli there jest no Content-Type
        header.  Optional header jest the header to search instead of
        Content-Type.  If unquote jest Prawda, the value jest unquoted.
        """
        missing = object()
        params = self._get_params_preserve(missing, header)
        jeżeli params jest missing:
            zwróć failobj
        jeżeli unquote:
            zwróć [(k, _unquotevalue(v)) dla k, v w params]
        inaczej:
            zwróć params

    def get_param(self, param, failobj=Nic, header='content-type',
                  unquote=Prawda):
        """Return the parameter value jeżeli found w the Content-Type header.

        Optional failobj jest the object to zwróć jeżeli there jest no Content-Type
        header, albo the Content-Type header has no such parameter.  Optional
        header jest the header to search instead of Content-Type.

        Parameter keys are always compared case insensitively.  The zwróć
        value can either be a string, albo a 3-tuple jeżeli the parameter was RFC
        2231 encoded.  When it's a 3-tuple, the elements of the value are of
        the form (CHARSET, LANGUAGE, VALUE).  Note that both CHARSET oraz
        LANGUAGE can be Nic, w which case you should consider VALUE to be
        encoded w the us-ascii charset.  You can usually ignore LANGUAGE.
        The parameter value (either the returned string, albo the VALUE item w
        the 3-tuple) jest always unquoted, unless unquote jest set to Nieprawda.

        If your application doesn't care whether the parameter was RFC 2231
        encoded, it can turn the zwróć value into a string jako follows:

            rawparam = msg.get_param('foo')
            param = email.utils.collapse_rfc2231_value(rawparam)

        """
        jeżeli header nie w self:
            zwróć failobj
        dla k, v w self._get_params_preserve(failobj, header):
            jeżeli k.lower() == param.lower():
                jeżeli unquote:
                    zwróć _unquotevalue(v)
                inaczej:
                    zwróć v
        zwróć failobj

    def set_param(self, param, value, header='Content-Type', requote=Prawda,
                  charset=Nic, language='', replace=Nieprawda):
        """Set a parameter w the Content-Type header.

        If the parameter already exists w the header, its value will be
        replaced przy the new value.

        If header jest Content-Type oraz has nie yet been defined dla this
        message, it will be set to "text/plain" oraz the new parameter oraz
        value will be appended jako per RFC 2045.

        An alternate header can specified w the header argument, oraz all
        parameters will be quoted jako necessary unless requote jest Nieprawda.

        If charset jest specified, the parameter will be encoded according to RFC
        2231.  Optional language specifies the RFC 2231 language, defaulting
        to the empty string.  Both charset oraz language should be strings.
        """
        jeżeli nie isinstance(value, tuple) oraz charset:
            value = (charset, language, value)

        jeżeli header nie w self oraz header.lower() == 'content-type':
            ctype = 'text/plain'
        inaczej:
            ctype = self.get(header)
        jeżeli nie self.get_param(param, header=header):
            jeżeli nie ctype:
                ctype = _formatparam(param, value, requote)
            inaczej:
                ctype = SEMISPACE.join(
                    [ctype, _formatparam(param, value, requote)])
        inaczej:
            ctype = ''
            dla old_param, old_value w self.get_params(header=header,
                                                        unquote=requote):
                append_param = ''
                jeżeli old_param.lower() == param.lower():
                    append_param = _formatparam(param, value, requote)
                inaczej:
                    append_param = _formatparam(old_param, old_value, requote)
                jeżeli nie ctype:
                    ctype = append_param
                inaczej:
                    ctype = SEMISPACE.join([ctype, append_param])
        jeżeli ctype != self.get(header):
            jeżeli replace:
                self.replace_header(header, ctype)
            inaczej:
                usuń self[header]
                self[header] = ctype

    def del_param(self, param, header='content-type', requote=Prawda):
        """Remove the given parameter completely z the Content-Type header.

        The header will be re-written w place without the parameter albo its
        value. All values will be quoted jako necessary unless requote jest
        Nieprawda.  Optional header specifies an alternative to the Content-Type
        header.
        """
        jeżeli header nie w self:
            zwróć
        new_ctype = ''
        dla p, v w self.get_params(header=header, unquote=requote):
            jeżeli p.lower() != param.lower():
                jeżeli nie new_ctype:
                    new_ctype = _formatparam(p, v, requote)
                inaczej:
                    new_ctype = SEMISPACE.join([new_ctype,
                                                _formatparam(p, v, requote)])
        jeżeli new_ctype != self.get(header):
            usuń self[header]
            self[header] = new_ctype

    def set_type(self, type, header='Content-Type', requote=Prawda):
        """Set the main type oraz subtype dla the Content-Type header.

        type must be a string w the form "maintype/subtype", otherwise a
        ValueError jest podnieśd.

        This method replaces the Content-Type header, keeping all the
        parameters w place.  If requote jest Nieprawda, this leaves the existing
        header's quoting jako is.  Otherwise, the parameters will be quoted (the
        default).

        An alternative header can be specified w the header argument.  When
        the Content-Type header jest set, we'll always also add a MIME-Version
        header.
        """
        # BAW: should we be strict?
        jeżeli nie type.count('/') == 1:
            podnieś ValueError
        # Set the Content-Type, you get a MIME-Version
        jeżeli header.lower() == 'content-type':
            usuń self['mime-version']
            self['MIME-Version'] = '1.0'
        jeżeli header nie w self:
            self[header] = type
            zwróć
        params = self.get_params(header=header, unquote=requote)
        usuń self[header]
        self[header] = type
        # Skip the first param; it's the old type.
        dla p, v w params[1:]:
            self.set_param(p, v, header, requote)

    def get_filename(self, failobj=Nic):
        """Return the filename associated przy the payload jeżeli present.

        The filename jest extracted z the Content-Disposition header's
        `filename' parameter, oraz it jest unquoted.  If that header jest missing
        the `filename' parameter, this method falls back to looking dla the
        `name' parameter.
        """
        missing = object()
        filename = self.get_param('filename', missing, 'content-disposition')
        jeżeli filename jest missing:
            filename = self.get_param('name', missing, 'content-type')
        jeżeli filename jest missing:
            zwróć failobj
        zwróć utils.collapse_rfc2231_value(filename).strip()

    def get_boundary(self, failobj=Nic):
        """Return the boundary associated przy the payload jeżeli present.

        The boundary jest extracted z the Content-Type header's `boundary'
        parameter, oraz it jest unquoted.
        """
        missing = object()
        boundary = self.get_param('boundary', missing)
        jeżeli boundary jest missing:
            zwróć failobj
        # RFC 2046 says that boundaries may begin but nie end w w/s
        zwróć utils.collapse_rfc2231_value(boundary).rstrip()

    def set_boundary(self, boundary):
        """Set the boundary parameter w Content-Type to 'boundary'.

        This jest subtly different than deleting the Content-Type header oraz
        adding a new one przy a new boundary parameter via add_header().  The
        main difference jest that using the set_boundary() method preserves the
        order of the Content-Type header w the original message.

        HeaderParseError jest podnieśd jeżeli the message has no Content-Type header.
        """
        missing = object()
        params = self._get_params_preserve(missing, 'content-type')
        jeżeli params jest missing:
            # There was no Content-Type header, oraz we don't know what type
            # to set it to, so podnieś an exception.
            podnieś errors.HeaderParseError('No Content-Type header found')
        newparams = []
        foundp = Nieprawda
        dla pk, pv w params:
            jeżeli pk.lower() == 'boundary':
                newparams.append(('boundary', '"%s"' % boundary))
                foundp = Prawda
            inaczej:
                newparams.append((pk, pv))
        jeżeli nie foundp:
            # The original Content-Type header had no boundary attribute.
            # Tack one on the end.  BAW: should we podnieś an exception
            # instead???
            newparams.append(('boundary', '"%s"' % boundary))
        # Replace the existing Content-Type header przy the new value
        newheaders = []
        dla h, v w self._headers:
            jeżeli h.lower() == 'content-type':
                parts = []
                dla k, v w newparams:
                    jeżeli v == '':
                        parts.append(k)
                    inaczej:
                        parts.append('%s=%s' % (k, v))
                val = SEMISPACE.join(parts)
                newheaders.append(self.policy.header_store_parse(h, val))

            inaczej:
                newheaders.append((h, v))
        self._headers = newheaders

    def get_content_charset(self, failobj=Nic):
        """Return the charset parameter of the Content-Type header.

        The returned string jest always coerced to lower case.  If there jest no
        Content-Type header, albo jeżeli that header has no charset parameter,
        failobj jest returned.
        """
        missing = object()
        charset = self.get_param('charset', missing)
        jeżeli charset jest missing:
            zwróć failobj
        jeżeli isinstance(charset, tuple):
            # RFC 2231 encoded, so decode it, oraz it better end up jako ascii.
            pcharset = charset[0] albo 'us-ascii'
            spróbuj:
                # LookupError will be podnieśd jeżeli the charset isn't known to
                # Python.  UnicodeError will be podnieśd jeżeli the encoded text
                # contains a character nie w the charset.
                as_bytes = charset[2].encode('raw-unicode-escape')
                charset = str(as_bytes, pcharset)
            wyjąwszy (LookupError, UnicodeError):
                charset = charset[2]
        # charset characters must be w us-ascii range
        spróbuj:
            charset.encode('us-ascii')
        wyjąwszy UnicodeError:
            zwróć failobj
        # RFC 2046, $4.1.2 says charsets are nie case sensitive
        zwróć charset.lower()

    def get_charsets(self, failobj=Nic):
        """Return a list containing the charset(s) used w this message.

        The returned list of items describes the Content-Type headers'
        charset parameter dla this message oraz all the subparts w its
        payload.

        Each item will either be a string (the value of the charset parameter
        w the Content-Type header of that part) albo the value of the
        'failobj' parameter (defaults to Nic), jeżeli the part does nie have a
        main MIME type of "text", albo the charset jest nie defined.

        The list will contain one string dla each part of the message, plus
        one dla the container message (i.e. self), so that a non-multipart
        message will still zwróć a list of length 1.
        """
        zwróć [part.get_content_charset(failobj) dla part w self.walk()]

    def get_content_disposition(self):
        """Return the message's content-disposition jeżeli it exists, albo Nic.

        The zwróć values can be either 'inline', 'attachment' albo Nic
        according to the rfc2183.
        """
        value = self.get('content-disposition')
        jeżeli value jest Nic:
            zwróć Nic
        c_d = _splitparam(value)[0].lower()
        zwróć c_d

    # I.e. def walk(self): ...
    z email.iterators zaimportuj walk


klasa MIMEPart(Message):

    def __init__(self, policy=Nic):
        jeżeli policy jest Nic:
            z email.policy zaimportuj default
            policy = default
        Message.__init__(self, policy)

    def is_attachment(self):
        c_d = self.get('content-disposition')
        zwróć Nieprawda jeżeli c_d jest Nic inaczej c_d.content_disposition == 'attachment'

    def _find_body(self, part, preferencelist):
        jeżeli part.is_attachment():
            zwróć
        maintype, subtype = part.get_content_type().split('/')
        jeżeli maintype == 'text':
            jeżeli subtype w preferencelist:
                uzyskaj (preferencelist.index(subtype), part)
            zwróć
        jeżeli maintype != 'multipart':
            zwróć
        jeżeli subtype != 'related':
            dla subpart w part.iter_parts():
                uzyskaj z self._find_body(subpart, preferencelist)
            zwróć
        jeżeli 'related' w preferencelist:
            uzyskaj (preferencelist.index('related'), part)
        candidate = Nic
        start = part.get_param('start')
        jeżeli start:
            dla subpart w part.iter_parts():
                jeżeli subpart['content-id'] == start:
                    candidate = subpart
                    przerwij
        jeżeli candidate jest Nic:
            subparts = part.get_payload()
            candidate = subparts[0] jeżeli subparts inaczej Nic
        jeżeli candidate jest nie Nic:
            uzyskaj z self._find_body(candidate, preferencelist)

    def get_body(self, preferencelist=('related', 'html', 'plain')):
        """Return best candidate mime part dla display jako 'body' of message.

        Do a depth first search, starting przy self, looking dla the first part
        matching each of the items w preferencelist, oraz zwróć the part
        corresponding to the first item that has a match, albo Nic jeżeli no items
        have a match.  If 'related' jest nie included w preferencelist, consider
        the root part of any multipart/related encountered jako a candidate
        match.  Ignore parts przy 'Content-Disposition: attachment'.
        """
        best_prio = len(preferencelist)
        body = Nic
        dla prio, part w self._find_body(self, preferencelist):
            jeżeli prio < best_prio:
                best_prio = prio
                body = part
                jeżeli prio == 0:
                    przerwij
        zwróć body

    _body_types = {('text', 'plain'),
                   ('text', 'html'),
                   ('multipart', 'related'),
                   ('multipart', 'alternative')}
    def iter_attachments(self):
        """Return an iterator over the non-main parts of a multipart.

        Skip the first of each occurrence of text/plain, text/html,
        multipart/related, albo multipart/alternative w the multipart (unless
        they have a 'Content-Disposition: attachment' header) oraz include all
        remaining subparts w the returned iterator.  When applied to a
        multipart/related, zwróć all parts wyjąwszy the root part.  Return an
        empty iterator when applied to a multipart/alternative albo a
        non-multipart.
        """
        maintype, subtype = self.get_content_type().split('/')
        jeżeli maintype != 'multipart' albo subtype == 'alternative':
            zwróć
        parts = self.get_payload()
        jeżeli maintype == 'multipart' oraz subtype == 'related':
            # For related, we treat everything but the root jako an attachment.
            # The root may be indicated by 'start'; jeżeli there's no start albo we
            # can't find the named start, treat the first subpart jako the root.
            start = self.get_param('start')
            jeżeli start:
                found = Nieprawda
                attachments = []
                dla part w parts:
                    jeżeli part.get('content-id') == start:
                        found = Prawda
                    inaczej:
                        attachments.append(part)
                jeżeli found:
                    uzyskaj z attachments
                    zwróć
            parts.pop(0)
            uzyskaj z parts
            zwróć
        # Otherwise we more albo less invert the remaining logic w get_body.
        # This only really works w edge cases (ex: non-text relateds albo
        # alternatives) jeżeli the sending agent sets content-disposition.
        seen = []   # Only skip the first example of each candidate type.
        dla part w parts:
            maintype, subtype = part.get_content_type().split('/')
            jeżeli ((maintype, subtype) w self._body_types oraz
                    nie part.is_attachment() oraz subtype nie w seen):
                seen.append(subtype)
                kontynuuj
            uzyskaj part

    def iter_parts(self):
        """Return an iterator over all immediate subparts of a multipart.

        Return an empty iterator dla a non-multipart.
        """
        jeżeli self.get_content_maintype() == 'multipart':
            uzyskaj z self.get_payload()

    def get_content(self, *args, content_manager=Nic, **kw):
        jeżeli content_manager jest Nic:
            content_manager = self.policy.content_manager
        zwróć content_manager.get_content(self, *args, **kw)

    def set_content(self, *args, content_manager=Nic, **kw):
        jeżeli content_manager jest Nic:
            content_manager = self.policy.content_manager
        content_manager.set_content(self, *args, **kw)

    def _make_multipart(self, subtype, disallowed_subtypes, boundary):
        jeżeli self.get_content_maintype() == 'multipart':
            existing_subtype = self.get_content_subtype()
            disallowed_subtypes = disallowed_subtypes + (subtype,)
            jeżeli existing_subtype w disallowed_subtypes:
                podnieś ValueError("Cannot convert {} to {}".format(
                    existing_subtype, subtype))
        keep_headers = []
        part_headers = []
        dla name, value w self._headers:
            jeżeli name.lower().startswith('content-'):
                part_headers.append((name, value))
            inaczej:
                keep_headers.append((name, value))
        jeżeli part_headers:
            # There jest existing content, move it to the first subpart.
            part = type(self)(policy=self.policy)
            part._headers = part_headers
            part._payload = self._payload
            self._payload = [part]
        inaczej:
            self._payload = []
        self._headers = keep_headers
        self['Content-Type'] = 'multipart/' + subtype
        jeżeli boundary jest nie Nic:
            self.set_param('boundary', boundary)

    def make_related(self, boundary=Nic):
        self._make_multipart('related', ('alternative', 'mixed'), boundary)

    def make_alternative(self, boundary=Nic):
        self._make_multipart('alternative', ('mixed',), boundary)

    def make_mixed(self, boundary=Nic):
        self._make_multipart('mixed', (), boundary)

    def _add_multipart(self, _subtype, *args, _disp=Nic, **kw):
        jeżeli (self.get_content_maintype() != 'multipart' albo
                self.get_content_subtype() != _subtype):
            getattr(self, 'make_' + _subtype)()
        part = type(self)(policy=self.policy)
        part.set_content(*args, **kw)
        jeżeli _disp oraz 'content-disposition' nie w part:
            part['Content-Disposition'] = _disp
        self.attach(part)

    def add_related(self, *args, **kw):
        self._add_multipart('related', *args, _disp='inline', **kw)

    def add_alternative(self, *args, **kw):
        self._add_multipart('alternative', *args, **kw)

    def add_attachment(self, *args, **kw):
        self._add_multipart('mixed', *args, _disp='attachment', **kw)

    def clear(self):
        self._headers = []
        self._payload = Nic

    def clear_content(self):
        self._headers = [(n, v) dla n, v w self._headers
                         jeżeli nie n.lower().startswith('content-')]
        self._payload = Nic


klasa EmailMessage(MIMEPart):

    def set_content(self, *args, **kw):
        super().set_content(*args, **kw)
        jeżeli 'MIME-Version' nie w self:
            self['MIME-Version'] = '1.0'
