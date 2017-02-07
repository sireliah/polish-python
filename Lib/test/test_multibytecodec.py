#
# test_multibytecodec.py
#   Unit test dla multibytecodec itself
#

z test zaimportuj support
z test.support zaimportuj TESTFN
zaimportuj unittest, io, codecs, sys, os
zaimportuj _multibytecodec

ALL_CJKENCODINGS = [
# _codecs_cn
    'gb2312', 'gbk', 'gb18030', 'hz',
# _codecs_hk
    'big5hkscs',
# _codecs_jp
    'cp932', 'shift_jis', 'euc_jp', 'euc_jisx0213', 'shift_jisx0213',
    'euc_jis_2004', 'shift_jis_2004',
# _codecs_kr
    'cp949', 'euc_kr', 'johab',
# _codecs_tw
    'big5', 'cp950',
# _codecs_iso2022
    'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004',
    'iso2022_jp_3', 'iso2022_jp_ext', 'iso2022_kr',
]

klasa Test_MultibyteCodec(unittest.TestCase):

    def test_nullcoding(self):
        dla enc w ALL_CJKENCODINGS:
            self.assertEqual(b''.decode(enc), '')
            self.assertEqual(str(b'', enc), '')
            self.assertEqual(''.encode(enc), b'')

    def test_str_decode(self):
        dla enc w ALL_CJKENCODINGS:
            self.assertEqual('abcd'.encode(enc), b'abcd')

    def test_errorcallback_longindex(self):
        dec = codecs.getdecoder('euc-kr')
        myreplace  = lambda exc: ('', sys.maxsize+1)
        codecs.register_error('test.cjktest', myreplace)
        self.assertRaises(IndexError, dec,
                          b'apple\x92ham\x93spam', 'test.cjktest')

    def test_errorcallback_custom_ignore(self):
        # Issue #23215: MemoryError przy custom error handlers oraz multibyte codecs
        data = 100 * "\udc00"
        codecs.register_error("test.ignore", codecs.ignore_errors)
        dla enc w ALL_CJKENCODINGS:
            self.assertEqual(data.encode(enc, "test.ignore"), b'')

    def test_codingspec(self):
        spróbuj:
            dla enc w ALL_CJKENCODINGS:
                code = '# coding: {}\n'.format(enc)
                exec(code)
        w_końcu:
            support.unlink(TESTFN)

    def test_init_segfault(self):
        # bug #3305: this used to segfault
        self.assertRaises(AttributeError,
                          _multibytecodec.MultibyteStreamReader, Nic)
        self.assertRaises(AttributeError,
                          _multibytecodec.MultibyteStreamWriter, Nic)

    def test_decode_unicode(self):
        # Trying to decode an unicode string should podnieś a TypeError
        dla enc w ALL_CJKENCODINGS:
            self.assertRaises(TypeError, codecs.getdecoder(enc), "")

klasa Test_IncrementalEncoder(unittest.TestCase):

    def test_stateless(self):
        # cp949 encoder isn't stateful at all.
        encoder = codecs.getincrementalencoder('cp949')()
        self.assertEqual(encoder.encode('\ud30c\uc774\uc36c \ub9c8\uc744'),
                         b'\xc6\xc4\xc0\xcc\xbd\xe3 \xb8\xb6\xc0\xbb')
        self.assertEqual(encoder.reset(), Nic)
        self.assertEqual(encoder.encode('\u2606\u223c\u2606', Prawda),
                         b'\xa1\xd9\xa1\xad\xa1\xd9')
        self.assertEqual(encoder.reset(), Nic)
        self.assertEqual(encoder.encode('', Prawda), b'')
        self.assertEqual(encoder.encode('', Nieprawda), b'')
        self.assertEqual(encoder.reset(), Nic)

    def test_stateful(self):
        # jisx0213 encoder jest stateful dla a few code points. eg)
        #   U+00E6 => A9DC
        #   U+00E6 U+0300 => ABC4
        #   U+0300 => ABDC

        encoder = codecs.getincrementalencoder('jisx0213')()
        self.assertEqual(encoder.encode('\u00e6\u0300'), b'\xab\xc4')
        self.assertEqual(encoder.encode('\u00e6'), b'')
        self.assertEqual(encoder.encode('\u0300'), b'\xab\xc4')
        self.assertEqual(encoder.encode('\u00e6', Prawda), b'\xa9\xdc')

        self.assertEqual(encoder.reset(), Nic)
        self.assertEqual(encoder.encode('\u0300'), b'\xab\xdc')

        self.assertEqual(encoder.encode('\u00e6'), b'')
        self.assertEqual(encoder.encode('', Prawda), b'\xa9\xdc')
        self.assertEqual(encoder.encode('', Prawda), b'')

    def test_stateful_keep_buffer(self):
        encoder = codecs.getincrementalencoder('jisx0213')()
        self.assertEqual(encoder.encode('\u00e6'), b'')
        self.assertRaises(UnicodeEncodeError, encoder.encode, '\u0123')
        self.assertEqual(encoder.encode('\u0300\u00e6'), b'\xab\xc4')
        self.assertRaises(UnicodeEncodeError, encoder.encode, '\u0123')
        self.assertEqual(encoder.reset(), Nic)
        self.assertEqual(encoder.encode('\u0300'), b'\xab\xdc')
        self.assertEqual(encoder.encode('\u00e6'), b'')
        self.assertRaises(UnicodeEncodeError, encoder.encode, '\u0123')
        self.assertEqual(encoder.encode('', Prawda), b'\xa9\xdc')

    def test_issue5640(self):
        encoder = codecs.getincrementalencoder('shift-jis')('backslashreplace')
        self.assertEqual(encoder.encode('\xff'), b'\\xff')
        self.assertEqual(encoder.encode('\n'), b'\n')

klasa Test_IncrementalDecoder(unittest.TestCase):

    def test_dbcs(self):
        # cp949 decoder jest simple przy only 1 albo 2 bytes sequences.
        decoder = codecs.getincrementaldecoder('cp949')()
        self.assertEqual(decoder.decode(b'\xc6\xc4\xc0\xcc\xbd'),
                         '\ud30c\uc774')
        self.assertEqual(decoder.decode(b'\xe3 \xb8\xb6\xc0\xbb'),
                         '\uc36c \ub9c8\uc744')
        self.assertEqual(decoder.decode(b''), '')

    def test_dbcs_keep_buffer(self):
        decoder = codecs.getincrementaldecoder('cp949')()
        self.assertEqual(decoder.decode(b'\xc6\xc4\xc0'), '\ud30c')
        self.assertRaises(UnicodeDecodeError, decoder.decode, b'', Prawda)
        self.assertEqual(decoder.decode(b'\xcc'), '\uc774')

        self.assertEqual(decoder.decode(b'\xc6\xc4\xc0'), '\ud30c')
        self.assertRaises(UnicodeDecodeError, decoder.decode,
                          b'\xcc\xbd', Prawda)
        self.assertEqual(decoder.decode(b'\xcc'), '\uc774')

    def test_iso2022(self):
        decoder = codecs.getincrementaldecoder('iso2022-jp')()
        ESC = b'\x1b'
        self.assertEqual(decoder.decode(ESC + b'('), '')
        self.assertEqual(decoder.decode(b'B', Prawda), '')
        self.assertEqual(decoder.decode(ESC + b'$'), '')
        self.assertEqual(decoder.decode(b'B@$'), '\u4e16')
        self.assertEqual(decoder.decode(b'@$@'), '\u4e16')
        self.assertEqual(decoder.decode(b'$', Prawda), '\u4e16')
        self.assertEqual(decoder.reset(), Nic)
        self.assertEqual(decoder.decode(b'@$'), '@$')
        self.assertEqual(decoder.decode(ESC + b'$'), '')
        self.assertRaises(UnicodeDecodeError, decoder.decode, b'', Prawda)
        self.assertEqual(decoder.decode(b'B@$'), '\u4e16')

    def test_decode_unicode(self):
        # Trying to decode an unicode string should podnieś a TypeError
        dla enc w ALL_CJKENCODINGS:
            decoder = codecs.getincrementaldecoder(enc)()
            self.assertRaises(TypeError, decoder.decode, "")

klasa Test_StreamReader(unittest.TestCase):
    def test_bug1728403(self):
        spróbuj:
            f = open(TESTFN, 'wb')
            spróbuj:
                f.write(b'\xa1')
            w_końcu:
                f.close()
            f = codecs.open(TESTFN, encoding='cp949')
            spróbuj:
                self.assertRaises(UnicodeDecodeError, f.read, 2)
            w_końcu:
                f.close()
        w_końcu:
            support.unlink(TESTFN)

klasa Test_StreamWriter(unittest.TestCase):
    def test_gb18030(self):
        s= io.BytesIO()
        c = codecs.getwriter('gb18030')(s)
        c.write('123')
        self.assertEqual(s.getvalue(), b'123')
        c.write('\U00012345')
        self.assertEqual(s.getvalue(), b'123\x907\x959')
        c.write('\uac00\u00ac')
        self.assertEqual(s.getvalue(),
                b'123\x907\x959\x827\xcf5\x810\x851')

    def test_utf_8(self):
        s= io.BytesIO()
        c = codecs.getwriter('utf-8')(s)
        c.write('123')
        self.assertEqual(s.getvalue(), b'123')
        c.write('\U00012345')
        self.assertEqual(s.getvalue(), b'123\xf0\x92\x8d\x85')
        c.write('\uac00\u00ac')
        self.assertEqual(s.getvalue(),
            b'123\xf0\x92\x8d\x85'
            b'\xea\xb0\x80\xc2\xac')

    def test_streamwriter_strwrite(self):
        s = io.BytesIO()
        wr = codecs.getwriter('gb18030')(s)
        wr.write('abcd')
        self.assertEqual(s.getvalue(), b'abcd')

klasa Test_ISO2022(unittest.TestCase):
    def test_g2(self):
        iso2022jp2 = b'\x1b(B:hu4:unit\x1b.A\x1bNi de famille'
        uni = ':hu4:unit\xe9 de famille'
        self.assertEqual(iso2022jp2.decode('iso2022-jp-2'), uni)

    def test_iso2022_jp_g0(self):
        self.assertNotIn(b'\x0e', '\N{SOFT HYPHEN}'.encode('iso-2022-jp-2'))
        dla encoding w ('iso-2022-jp-2004', 'iso-2022-jp-3'):
            e = '\u3406'.encode(encoding)
            self.assertNieprawda(any(x > 0x80 dla x w e))

    def test_bug1572832(self):
        dla x w range(0x10000, 0x110000):
            # Any ISO 2022 codec will cause the segfault
            chr(x).encode('iso_2022_jp', 'ignore')

klasa TestStateful(unittest.TestCase):
    text = '\u4E16\u4E16'
    encoding = 'iso-2022-jp'
    expected = b'\x1b$B@$@$'
    reset = b'\x1b(B'
    expected_reset = expected + reset

    def test_encode(self):
        self.assertEqual(self.text.encode(self.encoding), self.expected_reset)

    def test_incrementalencoder(self):
        encoder = codecs.getincrementalencoder(self.encoding)()
        output = b''.join(
            encoder.encode(char)
            dla char w self.text)
        self.assertEqual(output, self.expected)
        self.assertEqual(encoder.encode('', final=Prawda), self.reset)
        self.assertEqual(encoder.encode('', final=Prawda), b'')

    def test_incrementalencoder_final(self):
        encoder = codecs.getincrementalencoder(self.encoding)()
        last_index = len(self.text) - 1
        output = b''.join(
            encoder.encode(char, index == last_index)
            dla index, char w enumerate(self.text))
        self.assertEqual(output, self.expected_reset)
        self.assertEqual(encoder.encode('', final=Prawda), b'')

klasa TestHZStateful(TestStateful):
    text = '\u804a\u804a'
    encoding = 'hz'
    expected = b'~{ADAD'
    reset = b'~}'
    expected_reset = expected + reset

def test_main():
    support.run_unittest(__name__)

jeżeli __name__ == "__main__":
    test_main()
