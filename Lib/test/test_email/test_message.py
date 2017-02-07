zaimportuj unittest
zaimportuj textwrap
z email zaimportuj policy, message_from_string
z email.message zaimportuj EmailMessage, MIMEPart
z test.test_email zaimportuj TestEmailBase, parameterize


# Helper.
def first(iterable):
    zwróć next(filter(lambda x: x jest nie Nic, iterable), Nic)


klasa Test(TestEmailBase):

    policy = policy.default

    def test_error_on_setitem_if_max_count_exceeded(self):
        m = self._str_msg("")
        m['To'] = 'abc@xyz'
        przy self.assertRaises(ValueError):
            m['To'] = 'xyz@abc'

    def test_rfc2043_auto_decoded_and_emailmessage_used(self):
        m = message_from_string(textwrap.dedent("""\
            Subject: Ayons asperges pour le =?utf-8?q?d=C3=A9jeuner?=
            From: =?utf-8?q?Pep=C3=A9?= Le Pew <pepe@example.com>
            To: "Penelope Pussycat" <"penelope@example.com">
            MIME-Version: 1.0
            Content-Type: text/plain; charset="utf-8"

            sample text
            """), policy=policy.default)
        self.assertEqual(m['subject'], "Ayons asperges pour le déjeuner")
        self.assertEqual(m['from'], "Pepé Le Pew <pepe@example.com>")
        self.assertIsInstance(m, EmailMessage)


@parameterize
klasa TestEmailMessageBase:

    policy = policy.default

    # The first argument jest a triple (related, html, plain) of indices into the
    # list returned by 'walk' called on a Message constructed z the third.
    # The indices indicate which part should match the corresponding part-type
    # when dalejed to get_body (ie: the "first" part of that type w the
    # message).  The second argument jest a list of indices into the 'walk' list
    # of the attachments that should be returned by a call to
    # 'iter_attachments'.  The third argument jest a list of indices into 'walk'
    # that should be returned by a call to 'iter_parts'.  Note that the first
    # item returned by 'walk' jest the Message itself.

    message_params = {

        'empty_message': (
            (Nic, Nic, 0),
            (),
            (),
            ""),

        'non_mime_plain': (
            (Nic, Nic, 0),
            (),
            (),
            textwrap.dedent("""\
                To: foo@example.com

                simple text body
                """)),

        'mime_non_text': (
            (Nic, Nic, Nic),
            (),
            (),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: image/jpg

                bogus body.
                """)),

        'plain_html_alternative': (
            (Nic, 2, 1),
            (),
            (1, 2),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: multipart/alternative; boundary="==="

                preamble

                --===
                Content-Type: text/plain

                simple body

                --===
                Content-Type: text/html

                <p>simple body</p>
                --===--
                """)),

        'plain_html_mixed': (
            (Nic, 2, 1),
            (),
            (1, 2),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: multipart/mixed; boundary="==="

                preamble

                --===
                Content-Type: text/plain

                simple body

                --===
                Content-Type: text/html

                <p>simple body</p>

                --===--
                """)),

        'plain_html_attachment_mixed': (
            (Nic, Nic, 1),
            (2,),
            (1, 2),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: multipart/mixed; boundary="==="

                --===
                Content-Type: text/plain

                simple body

                --===
                Content-Type: text/html
                Content-Disposition: attachment

                <p>simple body</p>

                --===--
                """)),

        'html_text_attachment_mixed': (
            (Nic, 2, Nic),
            (1,),
            (1, 2),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: multipart/mixed; boundary="==="

                --===
                Content-Type: text/plain
                Content-Disposition: AtTaChment

                simple body

                --===
                Content-Type: text/html

                <p>simple body</p>

                --===--
                """)),

        'html_text_attachment_inline_mixed': (
            (Nic, 2, 1),
            (),
            (1, 2),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: multipart/mixed; boundary="==="

                --===
                Content-Type: text/plain
                Content-Disposition: InLine

                simple body

                --===
                Content-Type: text/html
                Content-Disposition: inline

                <p>simple body</p>

                --===--
                """)),

        # RFC 2387
        'related': (
            (0, 1, Nic),
            (2,),
            (1, 2),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: multipart/related; boundary="==="; type=text/html

                --===
                Content-Type: text/html

                <p>simple body</p>

                --===
                Content-Type: image/jpg
                Content-ID: <image1>

                bogus data

                --===--
                """)),

        # This message structure will probably never be seen w the wild, but
        # it proves we distinguish between text parts based on 'start'.  The
        # content would not, of course, actually work :)
        'related_with_start': (
            (0, 2, Nic),
            (1,),
            (1, 2),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: multipart/related; boundary="==="; type=text/html;
                 start="<body>"

                --===
                Content-Type: text/html
                Content-ID: <include>

                useless text

                --===
                Content-Type: text/html
                Content-ID: <body>

                <p>simple body</p>
                <!--#include file="<include>"-->

                --===--
                """)),


        'mixed_alternative_plain_related': (
            (3, 4, 2),
            (6, 7),
            (1, 6, 7),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: multipart/mixed; boundary="==="

                --===
                Content-Type: multipart/alternative; boundary="+++"

                --+++
                Content-Type: text/plain

                simple body

                --+++
                Content-Type: multipart/related; boundary="___"

                --___
                Content-Type: text/html

                <p>simple body</p>

                --___
                Content-Type: image/jpg
                Content-ID: <image1@cid>

                bogus jpg body

                --___--

                --+++--

                --===
                Content-Type: image/jpg
                Content-Disposition: attachment

                bogus jpg body

                --===
                Content-Type: image/jpg
                Content-Disposition: AttacHmenT

                another bogus jpg body

                --===--
                """)),

        # This structure suggested by Stephen J. Turnbull...may nie exist/be
        # supported w the wild, but we want to support it.
        'mixed_related_alternative_plain_html': (
            (1, 4, 3),
            (6, 7),
            (1, 6, 7),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: multipart/mixed; boundary="==="

                --===
                Content-Type: multipart/related; boundary="+++"

                --+++
                Content-Type: multipart/alternative; boundary="___"

                --___
                Content-Type: text/plain

                simple body

                --___
                Content-Type: text/html

                <p>simple body</p>

                --___--

                --+++
                Content-Type: image/jpg
                Content-ID: <image1@cid>

                bogus jpg body

                --+++--

                --===
                Content-Type: image/jpg
                Content-Disposition: attachment

                bogus jpg body

                --===
                Content-Type: image/jpg
                Content-Disposition: attachment

                another bogus jpg body

                --===--
                """)),

        # Same thing, but proving we only look at the root part, which jest the
        # first one jeżeli there isn't any start parameter.  That is, this jest a
        # broken related.
        'mixed_related_alternative_plain_html_wrong_order': (
            (1, Nic, Nic),
            (6, 7),
            (1, 6, 7),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: multipart/mixed; boundary="==="

                --===
                Content-Type: multipart/related; boundary="+++"

                --+++
                Content-Type: image/jpg
                Content-ID: <image1@cid>

                bogus jpg body

                --+++
                Content-Type: multipart/alternative; boundary="___"

                --___
                Content-Type: text/plain

                simple body

                --___
                Content-Type: text/html

                <p>simple body</p>

                --___--

                --+++--

                --===
                Content-Type: image/jpg
                Content-Disposition: attachment

                bogus jpg body

                --===
                Content-Type: image/jpg
                Content-Disposition: attachment

                another bogus jpg body

                --===--
                """)),

        'message_rfc822': (
            (Nic, Nic, Nic),
            (),
            (),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: message/rfc822

                To: bar@example.com
                From: robot@examp.com

                this jest a message body.
                """)),

        'mixed_text_message_rfc822': (
            (Nic, Nic, 1),
            (2,),
            (1, 2),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: multipart/mixed; boundary="==="

                --===
                Content-Type: text/plain

                Your message has bounced, ser.

                --===
                Content-Type: message/rfc822

                To: bar@example.com
                From: robot@examp.com

                this jest a message body.

                --===--
                """)),

         }

    def message_as_get_body(self, body_parts, attachments, parts, msg):
        m = self._str_msg(msg)
        allparts = list(m.walk())
        expected = [Nic jeżeli n jest Nic inaczej allparts[n] dla n w body_parts]
        related = 0; html = 1; plain = 2
        self.assertEqual(m.get_body(), first(expected))
        self.assertEqual(m.get_body(preferencelist=(
                                        'related', 'html', 'plain')),
                         first(expected))
        self.assertEqual(m.get_body(preferencelist=('related', 'html')),
                         first(expected[related:html+1]))
        self.assertEqual(m.get_body(preferencelist=('related', 'plain')),
                         first([expected[related], expected[plain]]))
        self.assertEqual(m.get_body(preferencelist=('html', 'plain')),
                         first(expected[html:plain+1]))
        self.assertEqual(m.get_body(preferencelist=['related']),
                         expected[related])
        self.assertEqual(m.get_body(preferencelist=['html']), expected[html])
        self.assertEqual(m.get_body(preferencelist=['plain']), expected[plain])
        self.assertEqual(m.get_body(preferencelist=('plain', 'html')),
                         first(expected[plain:html-1:-1]))
        self.assertEqual(m.get_body(preferencelist=('plain', 'related')),
                         first([expected[plain], expected[related]]))
        self.assertEqual(m.get_body(preferencelist=('html', 'related')),
                         first(expected[html::-1]))
        self.assertEqual(m.get_body(preferencelist=('plain', 'html', 'related')),
                         first(expected[::-1]))
        self.assertEqual(m.get_body(preferencelist=('html', 'plain', 'related')),
                         first([expected[html],
                                expected[plain],
                                expected[related]]))

    def message_as_iter_attachment(self, body_parts, attachments, parts, msg):
        m = self._str_msg(msg)
        allparts = list(m.walk())
        attachments = [allparts[n] dla n w attachments]
        self.assertEqual(list(m.iter_attachments()), attachments)

    def message_as_iter_parts(self, body_parts, attachments, parts, msg):
        m = self._str_msg(msg)
        allparts = list(m.walk())
        parts = [allparts[n] dla n w parts]
        self.assertEqual(list(m.iter_parts()), parts)

    klasa _TestContentManager:
        def get_content(self, msg, *args, **kw):
            zwróć msg, args, kw
        def set_content(self, msg, *args, **kw):
            self.msg = msg
            self.args = args
            self.kw = kw

    def test_get_content_with_cm(self):
        m = self._str_msg('')
        cm = self._TestContentManager()
        self.assertEqual(m.get_content(content_manager=cm), (m, (), {}))
        msg, args, kw = m.get_content('foo', content_manager=cm, bar=1, k=2)
        self.assertEqual(msg, m)
        self.assertEqual(args, ('foo',))
        self.assertEqual(kw, dict(bar=1, k=2))

    def test_get_content_default_cm_comes_from_policy(self):
        p = policy.default.clone(content_manager=self._TestContentManager())
        m = self._str_msg('', policy=p)
        self.assertEqual(m.get_content(), (m, (), {}))
        msg, args, kw = m.get_content('foo', bar=1, k=2)
        self.assertEqual(msg, m)
        self.assertEqual(args, ('foo',))
        self.assertEqual(kw, dict(bar=1, k=2))

    def test_set_content_with_cm(self):
        m = self._str_msg('')
        cm = self._TestContentManager()
        m.set_content(content_manager=cm)
        self.assertEqual(cm.msg, m)
        self.assertEqual(cm.args, ())
        self.assertEqual(cm.kw, {})
        m.set_content('foo', content_manager=cm, bar=1, k=2)
        self.assertEqual(cm.msg, m)
        self.assertEqual(cm.args, ('foo',))
        self.assertEqual(cm.kw, dict(bar=1, k=2))

    def test_set_content_default_cm_comes_from_policy(self):
        cm = self._TestContentManager()
        p = policy.default.clone(content_manager=cm)
        m = self._str_msg('', policy=p)
        m.set_content()
        self.assertEqual(cm.msg, m)
        self.assertEqual(cm.args, ())
        self.assertEqual(cm.kw, {})
        m.set_content('foo', bar=1, k=2)
        self.assertEqual(cm.msg, m)
        self.assertEqual(cm.args, ('foo',))
        self.assertEqual(cm.kw, dict(bar=1, k=2))

    # outcome jest whether xxx_method should podnieś ValueError error when called
    # on multipart/subtype.  Blank outcome means it depends on xxx (add
    # succeeds, make podnieśs).  Note: 'none' means there are content-type
    # headers but payload jest Nic...this happening w practice would be very
    # unusual, so treating it jako jeżeli there were content seems reasonable.
    #    method          subtype           outcome
    subtype_params = (
        ('related',      'no_content',     'succeeds'),
        ('related',      'none',           'succeeds'),
        ('related',      'plain',          'succeeds'),
        ('related',      'related',        ''),
        ('related',      'alternative',    'raises'),
        ('related',      'mixed',          'raises'),
        ('alternative',  'no_content',     'succeeds'),
        ('alternative',  'none',           'succeeds'),
        ('alternative',  'plain',          'succeeds'),
        ('alternative',  'related',        'succeeds'),
        ('alternative',  'alternative',    ''),
        ('alternative',  'mixed',          'raises'),
        ('mixed',        'no_content',     'succeeds'),
        ('mixed',        'none',           'succeeds'),
        ('mixed',        'plain',          'succeeds'),
        ('mixed',        'related',        'succeeds'),
        ('mixed',        'alternative',    'succeeds'),
        ('mixed',        'mixed',          ''),
        )

    def _make_subtype_test_message(self, subtype):
        m = self.message()
        payload = Nic
        msg_headers =  [
            ('To', 'foo@bar.com'),
            ('From', 'bar@foo.com'),
            ]
        jeżeli subtype != 'no_content':
            ('content-shadow', 'Logrus'),
        msg_headers.append(('X-Random-Header', 'Corwin'))
        jeżeli subtype == 'text':
            payload = ''
            msg_headers.append(('Content-Type', 'text/plain'))
            m.set_payload('')
        albo_inaczej subtype != 'no_content':
            payload = []
            msg_headers.append(('Content-Type', 'multipart/' + subtype))
        msg_headers.append(('X-Trump', 'Random'))
        m.set_payload(payload)
        dla name, value w msg_headers:
            m[name] = value
        zwróć m, msg_headers, payload

    def _check_disallowed_subtype_raises(self, m, method_name, subtype, method):
        przy self.assertRaises(ValueError) jako ar:
            getattr(m, method)()
        exc_text = str(ar.exception)
        self.assertIn(subtype, exc_text)
        self.assertIn(method_name, exc_text)

    def _check_make_multipart(self, m, msg_headers, payload):
        count = 0
        dla name, value w msg_headers:
            jeżeli nie name.lower().startswith('content-'):
                self.assertEqual(m[name], value)
                count += 1
        self.assertEqual(len(m), count+1) # +1 dla new Content-Type
        part = next(m.iter_parts())
        count = 0
        dla name, value w msg_headers:
            jeżeli name.lower().startswith('content-'):
                self.assertEqual(part[name], value)
                count += 1
        self.assertEqual(len(part), count)
        self.assertEqual(part.get_payload(), payload)

    def subtype_as_make(self, method, subtype, outcome):
        m, msg_headers, payload = self._make_subtype_test_message(subtype)
        make_method = 'make_' + method
        jeżeli outcome w ('', 'raises'):
            self._check_disallowed_subtype_raises(m, method, subtype, make_method)
            zwróć
        getattr(m, make_method)()
        self.assertEqual(m.get_content_maintype(), 'multipart')
        self.assertEqual(m.get_content_subtype(), method)
        jeżeli subtype == 'no_content':
            self.assertEqual(len(m.get_payload()), 0)
            self.assertEqual(m.items(),
                             msg_headers + [('Content-Type',
                                             'multipart/'+method)])
        inaczej:
            self.assertEqual(len(m.get_payload()), 1)
            self._check_make_multipart(m, msg_headers, payload)

    def subtype_as_make_with_boundary(self, method, subtype, outcome):
        # Doing all variation jest a bit of overkill...
        m = self.message()
        jeżeli outcome w ('', 'raises'):
            m['Content-Type'] = 'multipart/' + subtype
            przy self.assertRaises(ValueError) jako cm:
                getattr(m, 'make_' + method)()
            zwróć
        jeżeli subtype == 'plain':
            m['Content-Type'] = 'text/plain'
        albo_inaczej subtype != 'no_content':
            m['Content-Type'] = 'multipart/' + subtype
        getattr(m, 'make_' + method)(boundary="abc")
        self.assertPrawda(m.is_multipart())
        self.assertEqual(m.get_boundary(), 'abc')

    def test_policy_on_part_made_by_make_comes_from_message(self):
        dla method w ('make_related', 'make_alternative', 'make_mixed'):
            m = self.message(policy=self.policy.clone(content_manager='foo'))
            m['Content-Type'] = 'text/plain'
            getattr(m, method)()
            self.assertEqual(m.get_payload(0).policy.content_manager, 'foo')

    klasa _TestSetContentManager:
        def set_content(self, msg, content, *args, **kw):
            msg['Content-Type'] = 'text/plain'
            msg.set_payload(content)

    def subtype_as_add(self, method, subtype, outcome):
        m, msg_headers, payload = self._make_subtype_test_message(subtype)
        cm = self._TestSetContentManager()
        add_method = 'add_attachment' jeżeli method=='mixed' inaczej 'add_' + method
        jeżeli outcome == 'raises':
            self._check_disallowed_subtype_raises(m, method, subtype, add_method)
            zwróć
        getattr(m, add_method)('test', content_manager=cm)
        self.assertEqual(m.get_content_maintype(), 'multipart')
        self.assertEqual(m.get_content_subtype(), method)
        jeżeli method == subtype albo subtype == 'no_content':
            self.assertEqual(len(m.get_payload()), 1)
            dla name, value w msg_headers:
                self.assertEqual(m[name], value)
            part = m.get_payload()[0]
        inaczej:
            self.assertEqual(len(m.get_payload()), 2)
            self._check_make_multipart(m, msg_headers, payload)
            part = m.get_payload()[1]
        self.assertEqual(part.get_content_type(), 'text/plain')
        self.assertEqual(part.get_payload(), 'test')
        jeżeli method=='mixed':
            self.assertEqual(part['Content-Disposition'], 'attachment')
        albo_inaczej method=='related':
            self.assertEqual(part['Content-Disposition'], 'inline')
        inaczej:
            # Otherwise we don't guess.
            self.assertIsNic(part['Content-Disposition'])

    klasa _TestSetRaisingContentManager:
        def set_content(self, msg, content, *args, **kw):
            podnieś Exception('test')

    def test_default_content_manager_for_add_comes_from_policy(self):
        cm = self._TestSetRaisingContentManager()
        m = self.message(policy=self.policy.clone(content_manager=cm))
        dla method w ('add_related', 'add_alternative', 'add_attachment'):
            przy self.assertRaises(Exception) jako ar:
                getattr(m, method)('')
            self.assertEqual(str(ar.exception), 'test')

    def message_as_clear(self, body_parts, attachments, parts, msg):
        m = self._str_msg(msg)
        m.clear()
        self.assertEqual(len(m), 0)
        self.assertEqual(list(m.items()), [])
        self.assertIsNic(m.get_payload())
        self.assertEqual(list(m.iter_parts()), [])

    def message_as_clear_content(self, body_parts, attachments, parts, msg):
        m = self._str_msg(msg)
        expected_headers = [h dla h w m.keys()
                            jeżeli nie h.lower().startswith('content-')]
        m.clear_content()
        self.assertEqual(list(m.keys()), expected_headers)
        self.assertIsNic(m.get_payload())
        self.assertEqual(list(m.iter_parts()), [])

    def test_is_attachment(self):
        m = self._make_message()
        self.assertNieprawda(m.is_attachment())
        m['Content-Disposition'] = 'inline'
        self.assertNieprawda(m.is_attachment())
        m.replace_header('Content-Disposition', 'attachment')
        self.assertPrawda(m.is_attachment())
        m.replace_header('Content-Disposition', 'AtTachMent')
        self.assertPrawda(m.is_attachment())
        m.set_param('filename', 'abc.png', 'Content-Disposition')
        self.assertPrawda(m.is_attachment())


klasa TestEmailMessage(TestEmailMessageBase, TestEmailBase):
    message = EmailMessage

    def test_set_content_adds_MIME_Version(self):
        m = self._str_msg('')
        cm = self._TestContentManager()
        self.assertNotIn('MIME-Version', m)
        m.set_content(content_manager=cm)
        self.assertEqual(m['MIME-Version'], '1.0')

    klasa _MIME_Version_adding_CM:
        def set_content(self, msg, *args, **kw):
            msg['MIME-Version'] = '1.0'

    def test_set_content_does_not_duplicate_MIME_Version(self):
        m = self._str_msg('')
        cm = self._MIME_Version_adding_CM()
        self.assertNotIn('MIME-Version', m)
        m.set_content(content_manager=cm)
        self.assertEqual(m['MIME-Version'], '1.0')


klasa TestMIMEPart(TestEmailMessageBase, TestEmailBase):
    # Doing the full test run here may seem a bit redundant, since the two
    # classes are almost identical.  But what jeżeli they drift apart?  So we do
    # the full tests so that any future drift doesn't introduce bugs.
    message = MIMEPart

    def test_set_content_does_not_add_MIME_Version(self):
        m = self._str_msg('')
        cm = self._TestContentManager()
        self.assertNotIn('MIME-Version', m)
        m.set_content(content_manager=cm)
        self.assertNotIn('MIME-Version', m)


jeżeli __name__ == '__main__':
    unittest.main()
