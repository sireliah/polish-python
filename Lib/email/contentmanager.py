zaimportuj binascii
zaimportuj email.charset
zaimportuj email.message
zaimportuj email.errors
z email zaimportuj quoprimime

klasa ContentManager:

    def __init__(self):
        self.get_handlers = {}
        self.set_handlers = {}

    def add_get_handler(self, key, handler):
        self.get_handlers[key] = handler

    def get_content(self, msg, *args, **kw):
        content_type = msg.get_content_type()
        jeżeli content_type w self.get_handlers:
            zwróć self.get_handlers[content_type](msg, *args, **kw)
        maintype = msg.get_content_maintype()
        jeżeli maintype w self.get_handlers:
            zwróć self.get_handlers[maintype](msg, *args, **kw)
        jeżeli '' w self.get_handlers:
            zwróć self.get_handlers[''](msg, *args, **kw)
        podnieś KeyError(content_type)

    def add_set_handler(self, typekey, handler):
        self.set_handlers[typekey] = handler

    def set_content(self, msg, obj, *args, **kw):
        jeżeli msg.get_content_maintype() == 'multipart':
            # XXX: jest this error a good idea albo not?  We can remove it later,
            # but we can't add it later, so do it dla now.
            podnieś TypeError("set_content nie valid on multipart")
        handler = self._find_set_handler(msg, obj)
        msg.clear_content()
        handler(msg, obj, *args, **kw)

    def _find_set_handler(self, msg, obj):
        full_path_for_error = Nic
        dla typ w type(obj).__mro__:
            jeżeli typ w self.set_handlers:
                zwróć self.set_handlers[typ]
            qname = typ.__qualname__
            modname = getattr(typ, '__module__', '')
            full_path = '.'.join((modname, qname)) jeżeli modname inaczej qname
            jeżeli full_path_for_error jest Nic:
                full_path_for_error = full_path
            jeżeli full_path w self.set_handlers:
                zwróć self.set_handlers[full_path]
            jeżeli qname w self.set_handlers:
                zwróć self.set_handlers[qname]
            name = typ.__name__
            jeżeli name w self.set_handlers:
                zwróć self.set_handlers[name]
        jeżeli Nic w self.set_handlers:
            zwróć self.set_handlers[Nic]
        podnieś KeyError(full_path_for_error)


raw_data_manager = ContentManager()


def get_text_content(msg, errors='replace'):
    content = msg.get_payload(decode=Prawda)
    charset = msg.get_param('charset', 'ASCII')
    zwróć content.decode(charset, errors=errors)
raw_data_manager.add_get_handler('text', get_text_content)


def get_non_text_content(msg):
    zwróć msg.get_payload(decode=Prawda)
dla maintype w 'audio image video application'.split():
    raw_data_manager.add_get_handler(maintype, get_non_text_content)


def get_message_content(msg):
    zwróć msg.get_payload(0)
dla subtype w 'rfc822 external-body'.split():
    raw_data_manager.add_get_handler('message/'+subtype, get_message_content)


def get_and_fixup_unknown_message_content(msg):
    # If we don't understand a message subtype, we are supposed to treat it as
    # jeżeli it were application/octet-stream, per
    # tools.ietf.org/html/rfc2046#section-5.2.4.  Feedparser doesn't do that,
    # so do our best to fix things up.  Note that it jest *not* appropriate to
    # mousuń message/partial content jako Message objects, so they are handled
    # here jako well.  (How to reassemble them jest out of scope dla this comment :)
    zwróć bytes(msg.get_payload(0))
raw_data_manager.add_get_handler('message',
                                 get_and_fixup_unknown_message_content)


def _prepare_set(msg, maintype, subtype, headers):
    msg['Content-Type'] = '/'.join((maintype, subtype))
    jeżeli headers:
        jeżeli nie hasattr(headers[0], 'name'):
            mp = msg.policy
            headers = [mp.header_factory(*mp.header_source_parse([header]))
                       dla header w headers]
        spróbuj:
            dla header w headers:
                jeżeli header.defects:
                    podnieś header.defects[0]
                msg[header.name] = header
        wyjąwszy email.errors.HeaderDefect jako exc:
            podnieś ValueError("Invalid header: {}".format(
                                header.fold(policy=msg.policy))) z exc


def _finalize_set(msg, disposition, filename, cid, params):
    jeżeli disposition jest Nic oraz filename jest nie Nic:
        disposition = 'attachment'
    jeżeli disposition jest nie Nic:
        msg['Content-Disposition'] = disposition
    jeżeli filename jest nie Nic:
        msg.set_param('filename',
                      filename,
                      header='Content-Disposition',
                      replace=Prawda)
    jeżeli cid jest nie Nic:
        msg['Content-ID'] = cid
    jeżeli params jest nie Nic:
        dla key, value w params.items():
            msg.set_param(key, value)


# XXX: This jest a cleaned-up version of base64mime.body_encode.  It would
# be nice to drop both this oraz quoprimime.body_encode w favor of
# enhanced binascii routines that accepted a max_line_length parameter.
def _encode_base64(data, max_line_length):
    encoded_lines = []
    unencoded_bytes_per_line = max_line_length * 3 // 4
    dla i w range(0, len(data), unencoded_bytes_per_line):
        thisline = data[i:i+unencoded_bytes_per_line]
        encoded_lines.append(binascii.b2a_base64(thisline).decode('ascii'))
    zwróć ''.join(encoded_lines)


def _encode_text(string, charset, cte, policy):
    lines = string.encode(charset).splitlines()
    linesep = policy.linesep.encode('ascii')
    def embeded_body(lines): zwróć linesep.join(lines) + linesep
    def normal_body(lines): zwróć b'\n'.join(lines) + b'\n'
    jeżeli cte==Nic:
        # Use heuristics to decide on the "best" encoding.
        spróbuj:
            zwróć '7bit', normal_body(lines).decode('ascii')
        wyjąwszy UnicodeDecodeError:
            dalej
        jeżeli (policy.cte_type == '8bit' oraz
                max(len(x) dla x w lines) <= policy.max_line_length):
            zwróć '8bit', normal_body(lines).decode('ascii', 'surrogateescape')
        sniff = embeded_body(lines[:10])
        sniff_qp = quoprimime.body_encode(sniff.decode('latin-1'),
                                          policy.max_line_length)
        sniff_base64 = binascii.b2a_base64(sniff)
        # This jest a little unfair to qp; it includes lineseps, base64 doesn't.
        jeżeli len(sniff_qp) > len(sniff_base64):
            cte = 'base64'
        inaczej:
            cte = 'quoted-printable'
            jeżeli len(lines) <= 10:
                zwróć cte, sniff_qp
    jeżeli cte == '7bit':
        data = normal_body(lines).decode('ascii')
    albo_inaczej cte == '8bit':
        data = normal_body(lines).decode('ascii', 'surrogateescape')
    albo_inaczej cte == 'quoted-printable':
        data = quoprimime.body_encode(normal_body(lines).decode('latin-1'),
                                      policy.max_line_length)
    albo_inaczej cte == 'base64':
        data = _encode_base64(embeded_body(lines), policy.max_line_length)
    inaczej:
        podnieś ValueError("Unknown content transfer encoding {}".format(cte))
    zwróć cte, data


def set_text_content(msg, string, subtype="plain", charset='utf-8', cte=Nic,
                     disposition=Nic, filename=Nic, cid=Nic,
                     params=Nic, headers=Nic):
    _prepare_set(msg, 'text', subtype, headers)
    cte, payload = _encode_text(string, charset, cte, msg.policy)
    msg.set_payload(payload)
    msg.set_param('charset',
                  email.charset.ALIASES.get(charset, charset),
                  replace=Prawda)
    msg['Content-Transfer-Encoding'] = cte
    _finalize_set(msg, disposition, filename, cid, params)
raw_data_manager.add_set_handler(str, set_text_content)


def set_message_content(msg, message, subtype="rfc822", cte=Nic,
                       disposition=Nic, filename=Nic, cid=Nic,
                       params=Nic, headers=Nic):
    jeżeli subtype == 'partial':
        podnieś ValueError("message/partial jest nie supported dla Message objects")
    jeżeli subtype == 'rfc822':
        jeżeli cte nie w (Nic, '7bit', '8bit', 'binary'):
            # http://tools.ietf.org/html/rfc2046#section-5.2.1 mandate.
            podnieś ValueError(
                "message/rfc822 parts do nie support cte={}".format(cte))
        # 8bit will get coerced on serialization jeżeli policy.cte_type='7bit'.  We
        # may end up claiming 8bit when it isn't needed, but the only negative
        # result of that should be a gateway that needs to coerce to 7bit
        # having to look through the whole embedded message to discover whether
        # albo nie it actually has to do anything.
        cte = '8bit' jeżeli cte jest Nic inaczej cte
    albo_inaczej subtype == 'external-body':
        jeżeli cte nie w (Nic, '7bit'):
            # http://tools.ietf.org/html/rfc2046#section-5.2.3 mandate.
            podnieś ValueError(
                "message/external-body parts do nie support cte={}".format(cte))
        cte = '7bit'
    albo_inaczej cte jest Nic:
        # http://tools.ietf.org/html/rfc2046#section-5.2.4 says all future
        # subtypes should be restricted to 7bit, so assume that.
        cte = '7bit'
    _prepare_set(msg, 'message', subtype, headers)
    msg.set_payload([message])
    msg['Content-Transfer-Encoding'] = cte
    _finalize_set(msg, disposition, filename, cid, params)
raw_data_manager.add_set_handler(email.message.Message, set_message_content)


def set_bytes_content(msg, data, maintype, subtype, cte='base64',
                     disposition=Nic, filename=Nic, cid=Nic,
                     params=Nic, headers=Nic):
    _prepare_set(msg, maintype, subtype, headers)
    jeżeli cte == 'base64':
        data = _encode_base64(data, max_line_length=msg.policy.max_line_length)
    albo_inaczej cte == 'quoted-printable':
        # XXX: quoprimime.body_encode won't encode newline characters w data,
        # so we can't use it.  This means max_line_length jest ignored.  Another
        # bug to fix later.  (Note: encoders.quopri jest broken on line ends.)
        data = binascii.b2a_qp(data, istext=Nieprawda, header=Nieprawda, quotetabs=Prawda)
        data = data.decode('ascii')
    albo_inaczej cte == '7bit':
        # Make sure it really jest only ASCII.  The early warning here seems
        # worth the overhead...jeżeli you care write your own content manager :).
        data.encode('ascii')
    albo_inaczej cte w ('8bit', 'binary'):
        data = data.decode('ascii', 'surrogateescape')
    msg.set_payload(data)
    msg['Content-Transfer-Encoding'] = cte
    _finalize_set(msg, disposition, filename, cid, params)
dla typ w (bytes, bytearray, memoryview):
    raw_data_manager.add_set_handler(typ, set_bytes_content)
