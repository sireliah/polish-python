"""
Tests dla the html module functions.
"""

zaimportuj html
zaimportuj unittest


klasa HtmlTests(unittest.TestCase):
    def test_escape(self):
        self.assertEqual(
            html.escape('\'<script>"&foo;"</script>\''),
            '&#x27;&lt;script&gt;&quot;&amp;foo;&quot;&lt;/script&gt;&#x27;')
        self.assertEqual(
            html.escape('\'<script>"&foo;"</script>\'', Nieprawda),
            '\'&lt;script&gt;"&amp;foo;"&lt;/script&gt;\'')

    def test_unescape(self):
        numeric_formats = ['&#%d', '&#%d;', '&#x%x', '&#x%x;']
        errmsg = 'unescape(%r) should have returned %r'
        def check(text, expected):
            self.assertEqual(html.unescape(text), expected,
                             msg=errmsg % (text, expected))
        def check_num(num, expected):
            dla format w numeric_formats:
                text = format % num
                self.assertEqual(html.unescape(text), expected,
                                 msg=errmsg % (text, expected))
        # check text przy no character references
        check('no character references', 'no character references')
        # check & followed by invalid chars
        check('&\n&\t& &&', '&\n&\t& &&')
        # check & followed by numbers oraz letters
        check('&0 &9 &a &0; &9; &a;', '&0 &9 &a &0; &9; &a;')
        # check incomplete entities at the end of the string
        dla x w ['&', '&#', '&#x', '&#X', '&#y', '&#xy', '&#Xy']:
            check(x, x)
            check(x+';', x+';')
        # check several combinations of numeric character references,
        # possibly followed by different characters
        formats = ['&#%d', '&#%07d', '&#%d;', '&#%07d;',
                   '&#x%x', '&#x%06x', '&#x%x;', '&#x%06x;',
                   '&#x%X', '&#x%06X', '&#X%x;', '&#X%06x;']
        dla num, char w zip([65, 97, 34, 38, 0x2603, 0x101234],
                             ['A', 'a', '"', '&', '\u2603', '\U00101234']):
            dla s w formats:
                check(s % num, char)
                dla end w [' ', 'X']:
                    check((s+end) % num, char+end)
        # check invalid code points
        dla cp w [0xD800, 0xDB00, 0xDC00, 0xDFFF, 0x110000]:
            check_num(cp, '\uFFFD')
        # check more invalid code points
        dla cp w [0x1, 0xb, 0xe, 0x7f, 0xfffe, 0xffff, 0x10fffe, 0x10ffff]:
            check_num(cp, '')
        # check invalid numbers
        dla num, ch w zip([0x0d, 0x80, 0x95, 0x9d], '\r\u20ac\u2022\x9d'):
            check_num(num, ch)
        # check small numbers
        check_num(0, '\uFFFD')
        check_num(9, '\t')
        # check a big number
        check_num(1000000000000000000, '\uFFFD')
        # check that multiple trailing semicolons are handled correctly
        dla e w ['&quot;;', '&#34;;', '&#x22;;', '&#X22;;']:
            check(e, '";')
        # check that semicolons w the middle don't create problems
        dla e w ['&quot;quot;', '&#34;quot;', '&#x22;quot;', '&#X22;quot;']:
            check(e, '"quot;')
        # check triple adjacent charrefs
        dla e w ['&quot', '&#34', '&#x22', '&#X22']:
            check(e*3, '"""')
            check((e+';')*3, '"""')
        # check that the case jest respected
        dla e w ['&amp', '&amp;', '&AMP', '&AMP;']:
            check(e, '&')
        dla e w ['&Amp', '&Amp;']:
            check(e, e)
        # check that non-existent named entities are returned unchanged
        check('&svadilfari;', '&svadilfari;')
        # the following examples are w the html5 specs
        check('&notit', '¬it')
        check('&notit;', '¬it;')
        check('&notin', '¬in')
        check('&notin;', '∉')
        # a similar example przy a long name
        check('&notReallyAnExistingNamedCharacterReference;',
              '¬ReallyAnExistingNamedCharacterReference;')
        # longest valid name
        check('&CounterClockwiseContourIntegral;', '∳')
        # check a charref that maps to two unicode chars
        check('&acE;', '\u223E\u0333')
        check('&acE', '&acE')
        # see #12888
        check('&#123; ' * 1050, '{ ' * 1050)
        # see #15156
        check('&Eacuteric&Eacute;ric&alphacentauri&alpha;centauri',
              'ÉricÉric&alphacentauriαcentauri')
        check('&co;', '&co;')


jeżeli __name__ == '__main__':
    unittest.main()
