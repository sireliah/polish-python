# Tests that work dla both bytes oraz buffer objects.
# See PEP 3137.

zaimportuj struct
zaimportuj sys

klasa MixinBytesBufferCommonTests(object):
    """Tests that work dla both bytes oraz buffer objects.
    See PEP 3137.
    """

    def marshal(self, x):
        """Convert x into the appropriate type dla these tests."""
        podnieś RuntimeError('test klasa must provide a marshal method')

    def test_islower(self):
        self.assertNieprawda(self.marshal(b'').islower())
        self.assertPrawda(self.marshal(b'a').islower())
        self.assertNieprawda(self.marshal(b'A').islower())
        self.assertNieprawda(self.marshal(b'\n').islower())
        self.assertPrawda(self.marshal(b'abc').islower())
        self.assertNieprawda(self.marshal(b'aBc').islower())
        self.assertPrawda(self.marshal(b'abc\n').islower())
        self.assertRaises(TypeError, self.marshal(b'abc').islower, 42)

    def test_isupper(self):
        self.assertNieprawda(self.marshal(b'').isupper())
        self.assertNieprawda(self.marshal(b'a').isupper())
        self.assertPrawda(self.marshal(b'A').isupper())
        self.assertNieprawda(self.marshal(b'\n').isupper())
        self.assertPrawda(self.marshal(b'ABC').isupper())
        self.assertNieprawda(self.marshal(b'AbC').isupper())
        self.assertPrawda(self.marshal(b'ABC\n').isupper())
        self.assertRaises(TypeError, self.marshal(b'abc').isupper, 42)

    def test_istitle(self):
        self.assertNieprawda(self.marshal(b'').istitle())
        self.assertNieprawda(self.marshal(b'a').istitle())
        self.assertPrawda(self.marshal(b'A').istitle())
        self.assertNieprawda(self.marshal(b'\n').istitle())
        self.assertPrawda(self.marshal(b'A Titlecased Line').istitle())
        self.assertPrawda(self.marshal(b'A\nTitlecased Line').istitle())
        self.assertPrawda(self.marshal(b'A Titlecased, Line').istitle())
        self.assertNieprawda(self.marshal(b'Not a capitalized String').istitle())
        self.assertNieprawda(self.marshal(b'Not\ta Titlecase String').istitle())
        self.assertNieprawda(self.marshal(b'Not--a Titlecase String').istitle())
        self.assertNieprawda(self.marshal(b'NOT').istitle())
        self.assertRaises(TypeError, self.marshal(b'abc').istitle, 42)

    def test_isspace(self):
        self.assertNieprawda(self.marshal(b'').isspace())
        self.assertNieprawda(self.marshal(b'a').isspace())
        self.assertPrawda(self.marshal(b' ').isspace())
        self.assertPrawda(self.marshal(b'\t').isspace())
        self.assertPrawda(self.marshal(b'\r').isspace())
        self.assertPrawda(self.marshal(b'\n').isspace())
        self.assertPrawda(self.marshal(b' \t\r\n').isspace())
        self.assertNieprawda(self.marshal(b' \t\r\na').isspace())
        self.assertRaises(TypeError, self.marshal(b'abc').isspace, 42)

    def test_isalpha(self):
        self.assertNieprawda(self.marshal(b'').isalpha())
        self.assertPrawda(self.marshal(b'a').isalpha())
        self.assertPrawda(self.marshal(b'A').isalpha())
        self.assertNieprawda(self.marshal(b'\n').isalpha())
        self.assertPrawda(self.marshal(b'abc').isalpha())
        self.assertNieprawda(self.marshal(b'aBc123').isalpha())
        self.assertNieprawda(self.marshal(b'abc\n').isalpha())
        self.assertRaises(TypeError, self.marshal(b'abc').isalpha, 42)

    def test_isalnum(self):
        self.assertNieprawda(self.marshal(b'').isalnum())
        self.assertPrawda(self.marshal(b'a').isalnum())
        self.assertPrawda(self.marshal(b'A').isalnum())
        self.assertNieprawda(self.marshal(b'\n').isalnum())
        self.assertPrawda(self.marshal(b'123abc456').isalnum())
        self.assertPrawda(self.marshal(b'a1b3c').isalnum())
        self.assertNieprawda(self.marshal(b'aBc000 ').isalnum())
        self.assertNieprawda(self.marshal(b'abc\n').isalnum())
        self.assertRaises(TypeError, self.marshal(b'abc').isalnum, 42)

    def test_isdigit(self):
        self.assertNieprawda(self.marshal(b'').isdigit())
        self.assertNieprawda(self.marshal(b'a').isdigit())
        self.assertPrawda(self.marshal(b'0').isdigit())
        self.assertPrawda(self.marshal(b'0123456789').isdigit())
        self.assertNieprawda(self.marshal(b'0123456789a').isdigit())

        self.assertRaises(TypeError, self.marshal(b'abc').isdigit, 42)

    def test_lower(self):
        self.assertEqual(b'hello', self.marshal(b'HeLLo').lower())
        self.assertEqual(b'hello', self.marshal(b'hello').lower())
        self.assertRaises(TypeError, self.marshal(b'hello').lower, 42)

    def test_upper(self):
        self.assertEqual(b'HELLO', self.marshal(b'HeLLo').upper())
        self.assertEqual(b'HELLO', self.marshal(b'HELLO').upper())
        self.assertRaises(TypeError, self.marshal(b'hello').upper, 42)

    def test_capitalize(self):
        self.assertEqual(b' hello ', self.marshal(b' hello ').capitalize())
        self.assertEqual(b'Hello ', self.marshal(b'Hello ').capitalize())
        self.assertEqual(b'Hello ', self.marshal(b'hello ').capitalize())
        self.assertEqual(b'Aaaa', self.marshal(b'aaaa').capitalize())
        self.assertEqual(b'Aaaa', self.marshal(b'AaAa').capitalize())

        self.assertRaises(TypeError, self.marshal(b'hello').capitalize, 42)

    def test_ljust(self):
        self.assertEqual(b'abc       ', self.marshal(b'abc').ljust(10))
        self.assertEqual(b'abc   ', self.marshal(b'abc').ljust(6))
        self.assertEqual(b'abc', self.marshal(b'abc').ljust(3))
        self.assertEqual(b'abc', self.marshal(b'abc').ljust(2))
        self.assertEqual(b'abc*******', self.marshal(b'abc').ljust(10, b'*'))
        self.assertRaises(TypeError, self.marshal(b'abc').ljust)

    def test_rjust(self):
        self.assertEqual(b'       abc', self.marshal(b'abc').rjust(10))
        self.assertEqual(b'   abc', self.marshal(b'abc').rjust(6))
        self.assertEqual(b'abc', self.marshal(b'abc').rjust(3))
        self.assertEqual(b'abc', self.marshal(b'abc').rjust(2))
        self.assertEqual(b'*******abc', self.marshal(b'abc').rjust(10, b'*'))
        self.assertRaises(TypeError, self.marshal(b'abc').rjust)

    def test_center(self):
        self.assertEqual(b'   abc    ', self.marshal(b'abc').center(10))
        self.assertEqual(b' abc  ', self.marshal(b'abc').center(6))
        self.assertEqual(b'abc', self.marshal(b'abc').center(3))
        self.assertEqual(b'abc', self.marshal(b'abc').center(2))
        self.assertEqual(b'***abc****', self.marshal(b'abc').center(10, b'*'))
        self.assertRaises(TypeError, self.marshal(b'abc').center)

    def test_swapcase(self):
        self.assertEqual(b'hEllO CoMPuTErS',
            self.marshal(b'HeLLo cOmpUteRs').swapcase())

        self.assertRaises(TypeError, self.marshal(b'hello').swapcase, 42)

    def test_zfill(self):
        self.assertEqual(b'123', self.marshal(b'123').zfill(2))
        self.assertEqual(b'123', self.marshal(b'123').zfill(3))
        self.assertEqual(b'0123', self.marshal(b'123').zfill(4))
        self.assertEqual(b'+123', self.marshal(b'+123').zfill(3))
        self.assertEqual(b'+123', self.marshal(b'+123').zfill(4))
        self.assertEqual(b'+0123', self.marshal(b'+123').zfill(5))
        self.assertEqual(b'-123', self.marshal(b'-123').zfill(3))
        self.assertEqual(b'-123', self.marshal(b'-123').zfill(4))
        self.assertEqual(b'-0123', self.marshal(b'-123').zfill(5))
        self.assertEqual(b'000', self.marshal(b'').zfill(3))
        self.assertEqual(b'34', self.marshal(b'34').zfill(1))
        self.assertEqual(b'0034', self.marshal(b'34').zfill(4))

        self.assertRaises(TypeError, self.marshal(b'123').zfill)

    def test_expandtabs(self):
        self.assertEqual(b'abc\rab      def\ng       hi',
                         self.marshal(b'abc\rab\tdef\ng\thi').expandtabs())
        self.assertEqual(b'abc\rab      def\ng       hi',
                         self.marshal(b'abc\rab\tdef\ng\thi').expandtabs(8))
        self.assertEqual(b'abc\rab  def\ng   hi',
                         self.marshal(b'abc\rab\tdef\ng\thi').expandtabs(4))
        self.assertEqual(b'abc\r\nab      def\ng       hi',
                         self.marshal(b'abc\r\nab\tdef\ng\thi').expandtabs())
        self.assertEqual(b'abc\r\nab      def\ng       hi',
                         self.marshal(b'abc\r\nab\tdef\ng\thi').expandtabs(8))
        self.assertEqual(b'abc\r\nab  def\ng   hi',
                         self.marshal(b'abc\r\nab\tdef\ng\thi').expandtabs(4))
        self.assertEqual(b'abc\r\nab\r\ndef\ng\r\nhi',
                         self.marshal(b'abc\r\nab\r\ndef\ng\r\nhi').expandtabs(4))
        # check keyword args
        self.assertEqual(b'abc\rab      def\ng       hi',
                         self.marshal(b'abc\rab\tdef\ng\thi').expandtabs(tabsize=8))
        self.assertEqual(b'abc\rab  def\ng   hi',
                         self.marshal(b'abc\rab\tdef\ng\thi').expandtabs(tabsize=4))

        self.assertEqual(b'  a\n b', self.marshal(b' \ta\n\tb').expandtabs(1))

        self.assertRaises(TypeError, self.marshal(b'hello').expandtabs, 42, 42)
        # This test jest only valid when sizeof(int) == sizeof(void*) == 4.
        jeżeli sys.maxsize < (1 << 32) oraz struct.calcsize('P') == 4:
            self.assertRaises(OverflowError,
                              self.marshal(b'\ta\n\tb').expandtabs, sys.maxsize)

    def test_title(self):
        self.assertEqual(b' Hello ', self.marshal(b' hello ').title())
        self.assertEqual(b'Hello ', self.marshal(b'hello ').title())
        self.assertEqual(b'Hello ', self.marshal(b'Hello ').title())
        self.assertEqual(b'Format This As Title String',
                         self.marshal(b'fOrMaT thIs aS titLe String').title())
        self.assertEqual(b'Format,This-As*Title;String',
                         self.marshal(b'fOrMaT,thIs-aS*titLe;String').title())
        self.assertEqual(b'Getint', self.marshal(b'getInt').title())
        self.assertRaises(TypeError, self.marshal(b'hello').title, 42)

    def test_splitlines(self):
        self.assertEqual([b'abc', b'def', b'', b'ghi'],
                         self.marshal(b'abc\ndef\n\rghi').splitlines())
        self.assertEqual([b'abc', b'def', b'', b'ghi'],
                         self.marshal(b'abc\ndef\n\r\nghi').splitlines())
        self.assertEqual([b'abc', b'def', b'ghi'],
                         self.marshal(b'abc\ndef\r\nghi').splitlines())
        self.assertEqual([b'abc', b'def', b'ghi'],
                         self.marshal(b'abc\ndef\r\nghi\n').splitlines())
        self.assertEqual([b'abc', b'def', b'ghi', b''],
                         self.marshal(b'abc\ndef\r\nghi\n\r').splitlines())
        self.assertEqual([b'', b'abc', b'def', b'ghi', b''],
                         self.marshal(b'\nabc\ndef\r\nghi\n\r').splitlines())
        self.assertEqual([b'', b'abc', b'def', b'ghi', b''],
                         self.marshal(b'\nabc\ndef\r\nghi\n\r').splitlines(Nieprawda))
        self.assertEqual([b'\n', b'abc\n', b'def\r\n', b'ghi\n', b'\r'],
                         self.marshal(b'\nabc\ndef\r\nghi\n\r').splitlines(Prawda))
        self.assertEqual([b'', b'abc', b'def', b'ghi', b''],
                         self.marshal(b'\nabc\ndef\r\nghi\n\r').splitlines(keepends=Nieprawda))
        self.assertEqual([b'\n', b'abc\n', b'def\r\n', b'ghi\n', b'\r'],
                         self.marshal(b'\nabc\ndef\r\nghi\n\r').splitlines(keepends=Prawda))

        self.assertRaises(TypeError, self.marshal(b'abc').splitlines, 42, 42)
