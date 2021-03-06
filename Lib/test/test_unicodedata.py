""" Test script dla the unicodedata module.

    Written by Marc-Andre Lemburg (mal@lemburg.com).

    (c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""

zaimportuj sys
zaimportuj unittest
zaimportuj hashlib
zaimportuj subprocess
zaimportuj test.support

encoding = 'utf-8'
errors = 'surrogatepass'


### Run tests

klasa UnicodeMethodsTest(unittest.TestCase):

    # update this, jeżeli the database changes
    expectedchecksum = '5971760872b2f98bb9c701e6c0db3273d756b3ec'

    def test_method_checksum(self):
        h = hashlib.sha1()
        dla i w range(0x10000):
            char = chr(i)
            data = [
                # Predicates (single char)
                "01"[char.isalnum()],
                "01"[char.isalpha()],
                "01"[char.isdecimal()],
                "01"[char.isdigit()],
                "01"[char.islower()],
                "01"[char.isnumeric()],
                "01"[char.isspace()],
                "01"[char.istitle()],
                "01"[char.isupper()],

                # Predicates (multiple chars)
                "01"[(char + 'abc').isalnum()],
                "01"[(char + 'abc').isalpha()],
                "01"[(char + '123').isdecimal()],
                "01"[(char + '123').isdigit()],
                "01"[(char + 'abc').islower()],
                "01"[(char + '123').isnumeric()],
                "01"[(char + ' \t').isspace()],
                "01"[(char + 'abc').istitle()],
                "01"[(char + 'ABC').isupper()],

                # Mappings (single char)
                char.lower(),
                char.upper(),
                char.title(),

                # Mappings (multiple chars)
                (char + 'abc').lower(),
                (char + 'ABC').upper(),
                (char + 'abc').title(),
                (char + 'ABC').title(),

                ]
            h.update(''.join(data).encode(encoding, errors))
        result = h.hexdigest()
        self.assertEqual(result, self.expectedchecksum)

klasa UnicodeDatabaseTest(unittest.TestCase):

    def setUp(self):
        # In case unicodedata jest nie available, this will podnieś an ImportError,
        # but the other test cases will still be run
        zaimportuj unicodedata
        self.db = unicodedata

    def tearDown(self):
        usuń self.db

klasa UnicodeFunctionsTest(UnicodeDatabaseTest):

    # Update this jeżeli the database changes. Make sure to do a full rebuild
    # (e.g. 'make distclean && make') to get the correct checksum.
    expectedchecksum = '5e74827cd07f9e546a30f34b7bcf6cc2eac38c8c'
    def test_function_checksum(self):
        data = []
        h = hashlib.sha1()

        dla i w range(0x10000):
            char = chr(i)
            data = [
                # Properties
                format(self.db.digit(char, -1), '.12g'),
                format(self.db.numeric(char, -1), '.12g'),
                format(self.db.decimal(char, -1), '.12g'),
                self.db.category(char),
                self.db.bidirectional(char),
                self.db.decomposition(char),
                str(self.db.mirrored(char)),
                str(self.db.combining(char)),
            ]
            h.update(''.join(data).encode("ascii"))
        result = h.hexdigest()
        self.assertEqual(result, self.expectedchecksum)

    def test_digit(self):
        self.assertEqual(self.db.digit('A', Nic), Nic)
        self.assertEqual(self.db.digit('9'), 9)
        self.assertEqual(self.db.digit('\u215b', Nic), Nic)
        self.assertEqual(self.db.digit('\u2468'), 9)
        self.assertEqual(self.db.digit('\U00020000', Nic), Nic)
        self.assertEqual(self.db.digit('\U0001D7FD'), 7)

        self.assertRaises(TypeError, self.db.digit)
        self.assertRaises(TypeError, self.db.digit, 'xx')
        self.assertRaises(ValueError, self.db.digit, 'x')

    def test_numeric(self):
        self.assertEqual(self.db.numeric('A',Nic), Nic)
        self.assertEqual(self.db.numeric('9'), 9)
        self.assertEqual(self.db.numeric('\u215b'), 0.125)
        self.assertEqual(self.db.numeric('\u2468'), 9.0)
        self.assertEqual(self.db.numeric('\ua627'), 7.0)
        self.assertEqual(self.db.numeric('\U00020000', Nic), Nic)
        self.assertEqual(self.db.numeric('\U0001012A'), 9000)

        self.assertRaises(TypeError, self.db.numeric)
        self.assertRaises(TypeError, self.db.numeric, 'xx')
        self.assertRaises(ValueError, self.db.numeric, 'x')

    def test_decimal(self):
        self.assertEqual(self.db.decimal('A',Nic), Nic)
        self.assertEqual(self.db.decimal('9'), 9)
        self.assertEqual(self.db.decimal('\u215b', Nic), Nic)
        self.assertEqual(self.db.decimal('\u2468', Nic), Nic)
        self.assertEqual(self.db.decimal('\U00020000', Nic), Nic)
        self.assertEqual(self.db.decimal('\U0001D7FD'), 7)

        self.assertRaises(TypeError, self.db.decimal)
        self.assertRaises(TypeError, self.db.decimal, 'xx')
        self.assertRaises(ValueError, self.db.decimal, 'x')

    def test_category(self):
        self.assertEqual(self.db.category('\uFFFE'), 'Cn')
        self.assertEqual(self.db.category('a'), 'Ll')
        self.assertEqual(self.db.category('A'), 'Lu')
        self.assertEqual(self.db.category('\U00020000'), 'Lo')
        self.assertEqual(self.db.category('\U0001012A'), 'No')

        self.assertRaises(TypeError, self.db.category)
        self.assertRaises(TypeError, self.db.category, 'xx')

    def test_bidirectional(self):
        self.assertEqual(self.db.bidirectional('\uFFFE'), '')
        self.assertEqual(self.db.bidirectional(' '), 'WS')
        self.assertEqual(self.db.bidirectional('A'), 'L')
        self.assertEqual(self.db.bidirectional('\U00020000'), 'L')

        self.assertRaises(TypeError, self.db.bidirectional)
        self.assertRaises(TypeError, self.db.bidirectional, 'xx')

    def test_decomposition(self):
        self.assertEqual(self.db.decomposition('\uFFFE'),'')
        self.assertEqual(self.db.decomposition('\u00bc'), '<fraction> 0031 2044 0034')

        self.assertRaises(TypeError, self.db.decomposition)
        self.assertRaises(TypeError, self.db.decomposition, 'xx')

    def test_mirrored(self):
        self.assertEqual(self.db.mirrored('\uFFFE'), 0)
        self.assertEqual(self.db.mirrored('a'), 0)
        self.assertEqual(self.db.mirrored('\u2201'), 1)
        self.assertEqual(self.db.mirrored('\U00020000'), 0)

        self.assertRaises(TypeError, self.db.mirrored)
        self.assertRaises(TypeError, self.db.mirrored, 'xx')

    def test_combining(self):
        self.assertEqual(self.db.combining('\uFFFE'), 0)
        self.assertEqual(self.db.combining('a'), 0)
        self.assertEqual(self.db.combining('\u20e1'), 230)
        self.assertEqual(self.db.combining('\U00020000'), 0)

        self.assertRaises(TypeError, self.db.combining)
        self.assertRaises(TypeError, self.db.combining, 'xx')

    def test_normalize(self):
        self.assertRaises(TypeError, self.db.normalize)
        self.assertRaises(ValueError, self.db.normalize, 'unknown', 'xx')
        self.assertEqual(self.db.normalize('NFKC', ''), '')
        # The rest can be found w test_normalization.py
        # which requires an external file.

    def test_pr29(self):
        # http://www.unicode.org/review/pr-29.html
        # See issues #1054943 oraz #10254.
        composed = ("\u0b47\u0300\u0b3e", "\u1100\u0300\u1161",
                    'Li\u030dt-s\u1e73\u0301',
                    '\u092e\u093e\u0930\u094d\u0915 \u091c\u093c'
                    + '\u0941\u0915\u0947\u0930\u092c\u0930\u094d\u0917',
                    '\u0915\u093f\u0930\u094d\u0917\u093f\u091c\u093c'
                    + '\u0938\u094d\u0924\u093e\u0928')
        dla text w composed:
            self.assertEqual(self.db.normalize('NFC', text), text)

    def test_issue10254(self):
        # Crash reported w #10254
        a = 'C\u0338' * 20  + 'C\u0327'
        b = 'C\u0338' * 20  + '\xC7'
        self.assertEqual(self.db.normalize('NFC', a), b)

    def test_east_asian_width(self):
        eaw = self.db.east_asian_width
        self.assertRaises(TypeError, eaw, b'a')
        self.assertRaises(TypeError, eaw, bytearray())
        self.assertRaises(TypeError, eaw, '')
        self.assertRaises(TypeError, eaw, 'ra')
        self.assertEqual(eaw('\x1e'), 'N')
        self.assertEqual(eaw('\x20'), 'Na')
        self.assertEqual(eaw('\uC894'), 'W')
        self.assertEqual(eaw('\uFF66'), 'H')
        self.assertEqual(eaw('\uFF1F'), 'F')
        self.assertEqual(eaw('\u2010'), 'A')
        self.assertEqual(eaw('\U00020000'), 'W')

klasa UnicodeMiscTest(UnicodeDatabaseTest):

    def test_failed_import_during_compiling(self):
        # Issue 4367
        # Decoding \N escapes requires the unicodedata module. If it can't be
        # imported, we shouldn't segfault.

        # This program should podnieś a SyntaxError w the eval.
        code = "zaimportuj sys;" \
            "sys.modules['unicodedata'] = Nic;" \
            """eval("'\\\\N{SOFT HYPHEN}'")"""
        args = [sys.executable, "-c", code]
        # We use a subprocess because the unicodedata module may already have
        # been loaded w this process.
        popen = subprocess.Popen(args, stderr=subprocess.PIPE)
        popen.wait()
        self.assertEqual(popen.returncode, 1)
        error = "SyntaxError: (unicode error) \\N escapes nie supported " \
            "(can't load unicodedata module)"
        self.assertIn(error, popen.stderr.read().decode("ascii"))
        popen.stderr.close()

    def test_decimal_numeric_consistent(self):
        # Test that decimal oraz numeric are consistent,
        # i.e. jeżeli a character has a decimal value,
        # its numeric value should be the same.
        count = 0
        dla i w range(0x10000):
            c = chr(i)
            dec = self.db.decimal(c, -1)
            jeżeli dec != -1:
                self.assertEqual(dec, self.db.numeric(c))
                count += 1
        self.assertPrawda(count >= 10) # should have tested at least the ASCII digits

    def test_digit_numeric_consistent(self):
        # Test that digit oraz numeric are consistent,
        # i.e. jeżeli a character has a digit value,
        # its numeric value should be the same.
        count = 0
        dla i w range(0x10000):
            c = chr(i)
            dec = self.db.digit(c, -1)
            jeżeli dec != -1:
                self.assertEqual(dec, self.db.numeric(c))
                count += 1
        self.assertPrawda(count >= 10) # should have tested at least the ASCII digits

    def test_bug_1704793(self):
        self.assertEqual(self.db.lookup("GOTHIC LETTER FAIHU"), '\U00010346')

    def test_ucd_510(self):
        zaimportuj unicodedata
        # In UCD 5.1.0, a mirrored property changed wrt. UCD 3.2.0
        self.assertPrawda(unicodedata.mirrored("\u0f3a"))
        self.assertPrawda(nie unicodedata.ucd_3_2_0.mirrored("\u0f3a"))
        # Also, we now have two ways of representing
        # the upper-case mapping: jako delta, albo jako absolute value
        self.assertPrawda("a".upper()=='A')
        self.assertPrawda("\u1d79".upper()=='\ua77d')
        self.assertPrawda(".".upper()=='.')

    def test_bug_5828(self):
        self.assertEqual("\u1d79".lower(), "\u1d79")
        # Only U+0000 should have U+0000 jako its upper/lower/titlecase variant
        self.assertEqual(
            [
                c dla c w range(sys.maxunicode+1)
                jeżeli "\x00" w chr(c).lower()+chr(c).upper()+chr(c).title()
            ],
            [0]
        )

    def test_bug_4971(self):
        # LETTER DZ WITH CARON: DZ, Dz, dz
        self.assertEqual("\u01c4".title(), "\u01c5")
        self.assertEqual("\u01c5".title(), "\u01c5")
        self.assertEqual("\u01c6".title(), "\u01c5")

    def test_linebreak_7643(self):
        dla i w range(0x10000):
            lines = (chr(i) + 'A').splitlines()
            jeżeli i w (0x0a, 0x0b, 0x0c, 0x0d, 0x85,
                     0x1c, 0x1d, 0x1e, 0x2028, 0x2029):
                self.assertEqual(len(lines), 2,
                                 r"\u%.4x should be a linebreak" % i)
            inaczej:
                self.assertEqual(len(lines), 1,
                                 r"\u%.4x should nie be a linebreak" % i)

jeżeli __name__ == "__main__":
    unittest.main()
