zaimportuj textwrap
zaimportuj unittest
zaimportuj contextlib
z email zaimportuj policy
z email zaimportuj errors
z test.test_email zaimportuj TestEmailBase


klasa TestDefectsBase:

    policy = policy.default
    podnieś_expected = Nieprawda

    @contextlib.contextmanager
    def _raise_point(self, defect):
        uzyskaj

    def test_same_boundary_inner_outer(self):
        source = textwrap.dedent("""\
            Subject: XX
            From: xx@xx.dk
            To: XX
            Mime-version: 1.0
            Content-type: multipart/mixed;
               boundary="MS_Mac_OE_3071477847_720252_MIME_Part"

            --MS_Mac_OE_3071477847_720252_MIME_Part
            Content-type: multipart/alternative;
               boundary="MS_Mac_OE_3071477847_720252_MIME_Part"

            --MS_Mac_OE_3071477847_720252_MIME_Part
            Content-type: text/plain; charset="ISO-8859-1"
            Content-transfer-encoding: quoted-printable

            text

            --MS_Mac_OE_3071477847_720252_MIME_Part
            Content-type: text/html; charset="ISO-8859-1"
            Content-transfer-encoding: quoted-printable

            <HTML></HTML>

            --MS_Mac_OE_3071477847_720252_MIME_Part--

            --MS_Mac_OE_3071477847_720252_MIME_Part
            Content-type: image/gif; name="xx.gif";
            Content-disposition: attachment
            Content-transfer-encoding: base64

            Some removed base64 encoded chars.

            --MS_Mac_OE_3071477847_720252_MIME_Part--

            """)
        # XXX better would be to actually detect the duplicate.
        przy self._raise_point(errors.StartBoundaryNotFoundDefect):
            msg = self._str_msg(source)
        jeżeli self.raise_expected: zwróć
        inner = msg.get_payload(0)
        self.assertPrawda(hasattr(inner, 'defects'))
        self.assertEqual(len(self.get_defects(inner)), 1)
        self.assertIsInstance(self.get_defects(inner)[0],
                              errors.StartBoundaryNotFoundDefect)

    def test_multipart_no_boundary(self):
        source = textwrap.dedent("""\
            Date: Fri, 6 Apr 2001 09:23:06 -0800 (GMT-0800)
            From: foobar
            Subject: broken mail
            MIME-Version: 1.0
            Content-Type: multipart/report; report-type=delivery-status;

            --JAB03225.986577786/zinfandel.lacita.com

            One part

            --JAB03225.986577786/zinfandel.lacita.com
            Content-Type: message/delivery-status

            Header: Another part

            --JAB03225.986577786/zinfandel.lacita.com--
            """)
        przy self._raise_point(errors.NoBoundaryInMultipartDefect):
            msg = self._str_msg(source)
        jeżeli self.raise_expected: zwróć
        self.assertIsInstance(msg.get_payload(), str)
        self.assertEqual(len(self.get_defects(msg)), 2)
        self.assertIsInstance(self.get_defects(msg)[0],
                              errors.NoBoundaryInMultipartDefect)
        self.assertIsInstance(self.get_defects(msg)[1],
                              errors.MultipartInvariantViolationDefect)

    multipart_msg = textwrap.dedent("""\
        Date: Wed, 14 Nov 2007 12:56:23 GMT
        From: foo@bar.invalid
        To: foo@bar.invalid
        Subject: Content-Transfer-Encoding: base64 oraz multipart
        MIME-Version: 1.0
        Content-Type: multipart/mixed;
            boundary="===============3344438784458119861=="{}

        --===============3344438784458119861==
        Content-Type: text/plain

        Test message

        --===============3344438784458119861==
        Content-Type: application/octet-stream
        Content-Transfer-Encoding: base64

        YWJj

        --===============3344438784458119861==--
        """)

    def test_multipart_invalid_cte(self):
        przy self._raise_point(
                errors.InvalidMultipartContentTransferEncodingDefect):
            msg = self._str_msg(
                    self.multipart_msg.format(
                        "\nContent-Transfer-Encoding: base64"))
        jeżeli self.raise_expected: zwróć
        self.assertEqual(len(self.get_defects(msg)), 1)
        self.assertIsInstance(self.get_defects(msg)[0],
            errors.InvalidMultipartContentTransferEncodingDefect)

    def test_multipart_no_cte_no_defect(self):
        jeżeli self.raise_expected: zwróć
        msg = self._str_msg(self.multipart_msg.format(''))
        self.assertEqual(len(self.get_defects(msg)), 0)

    def test_multipart_valid_cte_no_defect(self):
        jeżeli self.raise_expected: zwróć
        dla cte w ('7bit', '8bit', 'BINary'):
            msg = self._str_msg(
                self.multipart_msg.format("\nContent-Transfer-Encoding: "+cte))
            self.assertEqual(len(self.get_defects(msg)), 0, "cte="+cte)

    def test_lying_multipart(self):
        source = textwrap.dedent("""\
            From: "Allison Dunlap" <xxx@example.com>
            To: yyy@example.com
            Subject: 64423
            Date: Sun, 11 Jul 2004 16:09:27 -0300
            MIME-Version: 1.0
            Content-Type: multipart/alternative;

            Blah blah blah
            """)
        przy self._raise_point(errors.NoBoundaryInMultipartDefect):
            msg = self._str_msg(source)
        jeżeli self.raise_expected: zwróć
        self.assertPrawda(hasattr(msg, 'defects'))
        self.assertEqual(len(self.get_defects(msg)), 2)
        self.assertIsInstance(self.get_defects(msg)[0],
                              errors.NoBoundaryInMultipartDefect)
        self.assertIsInstance(self.get_defects(msg)[1],
                              errors.MultipartInvariantViolationDefect)

    def test_missing_start_boundary(self):
        source = textwrap.dedent("""\
            Content-Type: multipart/mixed; boundary="AAA"
            From: Mail Delivery Subsystem <xxx@example.com>
            To: yyy@example.com

            --AAA

            Stuff

            --AAA
            Content-Type: message/rfc822

            From: webmaster@python.org
            To: zzz@example.com
            Content-Type: multipart/mixed; boundary="BBB"

            --BBB--

            --AAA--

            """)
        # The message structure is:
        #
        # multipart/mixed
        #    text/plain
        #    message/rfc822
        #        multipart/mixed [*]
        #
        # [*] This message jest missing its start boundary
        przy self._raise_point(errors.StartBoundaryNotFoundDefect):
            outer = self._str_msg(source)
        jeżeli self.raise_expected: zwróć
        bad = outer.get_payload(1).get_payload(0)
        self.assertEqual(len(self.get_defects(bad)), 1)
        self.assertIsInstance(self.get_defects(bad)[0],
                              errors.StartBoundaryNotFoundDefect)

    def test_first_line_is_continuation_header(self):
        przy self._raise_point(errors.FirstHeaderLineIsContinuationDefect):
            msg = self._str_msg(' Line 1\nSubject: test\n\nbody')
        jeżeli self.raise_expected: zwróć
        self.assertEqual(msg.keys(), ['Subject'])
        self.assertEqual(msg.get_payload(), 'body')
        self.assertEqual(len(self.get_defects(msg)), 1)
        self.assertDefectsEqual(self.get_defects(msg),
                                 [errors.FirstHeaderLineIsContinuationDefect])
        self.assertEqual(self.get_defects(msg)[0].line, ' Line 1\n')

    def test_missing_header_body_separator(self):
        # Our heuristic jeżeli we see a line that doesn't look like a header (no
        # leading whitespace but no ':') jest to assume that the blank line that
        # separates the header z the body jest missing, oraz to stop parsing
        # headers oraz start parsing the body.
        przy self._raise_point(errors.MissingHeaderBodySeparatorDefect):
            msg = self._str_msg('Subject: test\nnot a header\nTo: abc\n\nb\n')
        jeżeli self.raise_expected: zwróć
        self.assertEqual(msg.keys(), ['Subject'])
        self.assertEqual(msg.get_payload(), 'not a header\nTo: abc\n\nb\n')
        self.assertDefectsEqual(self.get_defects(msg),
                                [errors.MissingHeaderBodySeparatorDefect])

    def test_bad_padding_in_base64_payload(self):
        source = textwrap.dedent("""\
            Subject: test
            MIME-Version: 1.0
            Content-Type: text/plain; charset="utf-8"
            Content-Transfer-Encoding: base64

            dmk
            """)
        msg = self._str_msg(source)
        przy self._raise_point(errors.InvalidBase64PaddingDefect):
            payload = msg.get_payload(decode=Prawda)
        jeżeli self.raise_expected: zwróć
        self.assertEqual(payload, b'vi')
        self.assertDefectsEqual(self.get_defects(msg),
                                [errors.InvalidBase64PaddingDefect])

    def test_invalid_chars_in_base64_payload(self):
        source = textwrap.dedent("""\
            Subject: test
            MIME-Version: 1.0
            Content-Type: text/plain; charset="utf-8"
            Content-Transfer-Encoding: base64

            dm\x01k===
            """)
        msg = self._str_msg(source)
        przy self._raise_point(errors.InvalidBase64CharactersDefect):
            payload = msg.get_payload(decode=Prawda)
        jeżeli self.raise_expected: zwróć
        self.assertEqual(payload, b'vi')
        self.assertDefectsEqual(self.get_defects(msg),
                                [errors.InvalidBase64CharactersDefect])

    def test_missing_ending_boundary(self):
        source = textwrap.dedent("""\
            To: 1@harrydomain4.com
            Subject: Fwd: 1
            MIME-Version: 1.0
            Content-Type: multipart/alternative;
             boundary="------------000101020201080900040301"

            --------------000101020201080900040301
            Content-Type: text/plain; charset=ISO-8859-1
            Content-Transfer-Encoding: 7bit

            Alternative 1

            --------------000101020201080900040301
            Content-Type: text/html; charset=ISO-8859-1
            Content-Transfer-Encoding: 7bit

            Alternative 2

            """)
        przy self._raise_point(errors.CloseBoundaryNotFoundDefect):
            msg = self._str_msg(source)
        jeżeli self.raise_expected: zwróć
        self.assertEqual(len(msg.get_payload()), 2)
        self.assertEqual(msg.get_payload(1).get_payload(), 'Alternative 2\n')
        self.assertDefectsEqual(self.get_defects(msg),
                                [errors.CloseBoundaryNotFoundDefect])


klasa TestDefectDetection(TestDefectsBase, TestEmailBase):

    def get_defects(self, obj):
        zwróć obj.defects


klasa TestDefectCapture(TestDefectsBase, TestEmailBase):

    klasa CapturePolicy(policy.EmailPolicy):
        captured = Nic
        def register_defect(self, obj, defect):
            self.captured.append(defect)

    def setUp(self):
        self.policy = self.CapturePolicy(captured=list())

    def get_defects(self, obj):
        zwróć self.policy.captured


klasa TestDefectRaising(TestDefectsBase, TestEmailBase):

    policy = TestDefectsBase.policy
    policy = policy.clone(raise_on_defect=Prawda)
    podnieś_expected = Prawda

    @contextlib.contextmanager
    def _raise_point(self, defect):
        przy self.assertRaises(defect):
            uzyskaj


jeżeli __name__ == '__main__':
    unittest.main()
