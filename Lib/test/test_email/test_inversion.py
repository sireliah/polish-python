"""Test the parser oraz generator are inverses.

Note that this jest only strictly true jeżeli we are parsing RFC valid messages oraz
producing RFC valid messages.
"""

zaimportuj io
zaimportuj unittest
z email zaimportuj policy, message_from_bytes
z email.generator zaimportuj BytesGenerator
z test.test_email zaimportuj TestEmailBase, parameterize

# This jest like textwrap.dedent dla bytes, wyjąwszy that it uses \r\n dla the line
# separators on the rebuilt string.
def dedent(bstr):
    lines = bstr.splitlines()
    jeżeli nie lines[0].strip():
        podnieś ValueError("First line must contain text")
    stripamt = len(lines[0]) - len(lines[0].lstrip())
    zwróć b'\r\n'.join(
        [x[stripamt:] jeżeli len(x)>=stripamt inaczej b''
            dla x w lines])


@parameterize
klasa TestInversion(TestEmailBase, unittest.TestCase):

    def msg_as_input(self, msg):
        m = message_from_bytes(msg, policy=policy.SMTP)
        b = io.BytesIO()
        g = BytesGenerator(b)
        g.flatten(m)
        self.assertEqual(b.getvalue(), msg)

    # XXX: spaces are nie preserved correctly here yet w the general case.
    msg_params = {
        'header_with_one_space_body': (dedent(b"""\
            From: abc@xyz.com
            X-Status:\x20
            Subject: test

            foo
            """),),

            }


jeżeli __name__ == '__main__':
    unittest.main()
