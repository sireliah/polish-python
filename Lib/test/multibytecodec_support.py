#
# multibytecodec_support.py
#   Common Unittest Routines dla CJK codecs
#

zaimportuj codecs
zaimportuj os
zaimportuj re
zaimportuj sys
zaimportuj unittest
z http.client zaimportuj HTTPException
z test zaimportuj support
z io zaimportuj BytesIO

klasa TestBase:
    encoding        = ''   # codec name
    codec           = Nic # codec tuple (przy 4 elements)
    tstring         = Nic # must set. 2 strings to test StreamReader

    codectests      = Nic # must set. codec test tuple
    roundtriptest   = 1    # set jeżeli roundtrip jest possible przy unicode
    has_iso10646    = 0    # set jeżeli this encoding contains whole iso10646 map
    xmlcharnametest = Nic # string to test xmlcharrefreplace
    unmappedunicode = '\udeee' # a unicode code point that jest nie mapped.

    def setUp(self):
        jeżeli self.codec jest Nic:
            self.codec = codecs.lookup(self.encoding)
        self.encode = self.codec.encode
        self.decode = self.codec.decode
        self.reader = self.codec.streamreader
        self.writer = self.codec.streamwriter
        self.incrementalencoder = self.codec.incrementalencoder
        self.incrementaldecoder = self.codec.incrementaldecoder

    def test_chunkcoding(self):
        tstring_lines = []
        dla b w self.tstring:
            lines = b.split(b"\n")
            last = lines.pop()
            assert last == b""
            lines = [line + b"\n" dla line w lines]
            tstring_lines.append(lines)
        dla native, utf8 w zip(*tstring_lines):
            u = self.decode(native)[0]
            self.assertEqual(u, utf8.decode('utf-8'))
            jeżeli self.roundtriptest:
                self.assertEqual(native, self.encode(u)[0])

    def test_errorhandle(self):
        dla source, scheme, expected w self.codectests:
            jeżeli isinstance(source, bytes):
                func = self.decode
            inaczej:
                func = self.encode
            jeżeli expected:
                result = func(source, scheme)[0]
                jeżeli func jest self.decode:
                    self.assertPrawda(type(result) jest str, type(result))
                    self.assertEqual(result, expected,
                                     '%a.decode(%r, %r)=%a != %a'
                                     % (source, self.encoding, scheme, result,
                                        expected))
                inaczej:
                    self.assertPrawda(type(result) jest bytes, type(result))
                    self.assertEqual(result, expected,
                                     '%a.encode(%r, %r)=%a != %a'
                                     % (source, self.encoding, scheme, result,
                                        expected))
            inaczej:
                self.assertRaises(UnicodeError, func, source, scheme)

    def test_xmlcharrefreplace(self):
        jeżeli self.has_iso10646:
            self.skipTest('encoding contains full ISO 10646 map')

        s = "\u0b13\u0b23\u0b60 nd eggs"
        self.assertEqual(
            self.encode(s, "xmlcharrefreplace")[0],
            b"&#2835;&#2851;&#2912; nd eggs"
        )

    def test_customreplace_encode(self):
        jeżeli self.has_iso10646:
            self.skipTest('encoding contains full ISO 10646 map')

        z html.entities zaimportuj codepoint2name

        def xmlcharnamereplace(exc):
            jeżeli nie isinstance(exc, UnicodeEncodeError):
                podnieś TypeError("don't know how to handle %r" % exc)
            l = []
            dla c w exc.object[exc.start:exc.end]:
                jeżeli ord(c) w codepoint2name:
                    l.append("&%s;" % codepoint2name[ord(c)])
                inaczej:
                    l.append("&#%d;" % ord(c))
            zwróć ("".join(l), exc.end)

        codecs.register_error("test.xmlcharnamereplace", xmlcharnamereplace)

        jeżeli self.xmlcharnametest:
            sin, sout = self.xmlcharnametest
        inaczej:
            sin = "\xab\u211c\xbb = \u2329\u1234\u232a"
            sout = b"&laquo;&real;&raquo; = &lang;&#4660;&rang;"
        self.assertEqual(self.encode(sin,
                                    "test.xmlcharnamereplace")[0], sout)

    def test_callback_returns_bytes(self):
        def myreplace(exc):
            zwróć (b"1234", exc.end)
        codecs.register_error("test.cjktest", myreplace)
        enc = self.encode("abc" + self.unmappedunicode + "def", "test.cjktest")[0]
        self.assertEqual(enc, b"abc1234def")

    def test_callback_wrong_objects(self):
        def myreplace(exc):
            zwróć (ret, exc.end)
        codecs.register_error("test.cjktest", myreplace)

        dla ret w ([1, 2, 3], [], Nic, object()):
            self.assertRaises(TypeError, self.encode, self.unmappedunicode,
                              'test.cjktest')

    def test_callback_long_index(self):
        def myreplace(exc):
            zwróć ('x', int(exc.end))
        codecs.register_error("test.cjktest", myreplace)
        self.assertEqual(self.encode('abcd' + self.unmappedunicode + 'efgh',
                                     'test.cjktest'), (b'abcdxefgh', 9))

        def myreplace(exc):
            zwróć ('x', sys.maxsize + 1)
        codecs.register_error("test.cjktest", myreplace)
        self.assertRaises(IndexError, self.encode, self.unmappedunicode,
                          'test.cjktest')

    def test_callback_Nic_index(self):
        def myreplace(exc):
            zwróć ('x', Nic)
        codecs.register_error("test.cjktest", myreplace)
        self.assertRaises(TypeError, self.encode, self.unmappedunicode,
                          'test.cjktest')

    def test_callback_backward_index(self):
        def myreplace(exc):
            jeżeli myreplace.limit > 0:
                myreplace.limit -= 1
                zwróć ('REPLACED', 0)
            inaczej:
                zwróć ('TERMINAL', exc.end)
        myreplace.limit = 3
        codecs.register_error("test.cjktest", myreplace)
        self.assertEqual(self.encode('abcd' + self.unmappedunicode + 'efgh',
                                     'test.cjktest'),
                (b'abcdREPLACEDabcdREPLACEDabcdREPLACEDabcdTERMINALefgh', 9))

    def test_callback_forward_index(self):
        def myreplace(exc):
            zwróć ('REPLACED', exc.end + 2)
        codecs.register_error("test.cjktest", myreplace)
        self.assertEqual(self.encode('abcd' + self.unmappedunicode + 'efgh',
                                     'test.cjktest'), (b'abcdREPLACEDgh', 9))

    def test_callback_index_outofbound(self):
        def myreplace(exc):
            zwróć ('TERM', 100)
        codecs.register_error("test.cjktest", myreplace)
        self.assertRaises(IndexError, self.encode, self.unmappedunicode,
                          'test.cjktest')

    def test_incrementalencoder(self):
        UTF8Reader = codecs.getreader('utf-8')
        dla sizehint w [Nic] + list(range(1, 33)) + \
                        [64, 128, 256, 512, 1024]:
            istream = UTF8Reader(BytesIO(self.tstring[1]))
            ostream = BytesIO()
            encoder = self.incrementalencoder()
            dopóki 1:
                jeżeli sizehint jest nie Nic:
                    data = istream.read(sizehint)
                inaczej:
                    data = istream.read()

                jeżeli nie data:
                    przerwij
                e = encoder.encode(data)
                ostream.write(e)

            self.assertEqual(ostream.getvalue(), self.tstring[0])

    def test_incrementaldecoder(self):
        UTF8Writer = codecs.getwriter('utf-8')
        dla sizehint w [Nic, -1] + list(range(1, 33)) + \
                        [64, 128, 256, 512, 1024]:
            istream = BytesIO(self.tstring[0])
            ostream = UTF8Writer(BytesIO())
            decoder = self.incrementaldecoder()
            dopóki 1:
                data = istream.read(sizehint)
                jeżeli nie data:
                    przerwij
                inaczej:
                    u = decoder.decode(data)
                    ostream.write(u)

            self.assertEqual(ostream.getvalue(), self.tstring[1])

    def test_incrementalencoder_error_callback(self):
        inv = self.unmappedunicode

        e = self.incrementalencoder()
        self.assertRaises(UnicodeEncodeError, e.encode, inv, Prawda)

        e.errors = 'ignore'
        self.assertEqual(e.encode(inv, Prawda), b'')

        e.reset()
        def tempreplace(exc):
            zwróć ('called', exc.end)
        codecs.register_error('test.incremental_error_callback', tempreplace)
        e.errors = 'test.incremental_error_callback'
        self.assertEqual(e.encode(inv, Prawda), b'called')

        # again
        e.errors = 'ignore'
        self.assertEqual(e.encode(inv, Prawda), b'')

    def test_streamreader(self):
        UTF8Writer = codecs.getwriter('utf-8')
        dla name w ["read", "readline", "readlines"]:
            dla sizehint w [Nic, -1] + list(range(1, 33)) + \
                            [64, 128, 256, 512, 1024]:
                istream = self.reader(BytesIO(self.tstring[0]))
                ostream = UTF8Writer(BytesIO())
                func = getattr(istream, name)
                dopóki 1:
                    data = func(sizehint)
                    jeżeli nie data:
                        przerwij
                    jeżeli name == "readlines":
                        ostream.writelines(data)
                    inaczej:
                        ostream.write(data)

                self.assertEqual(ostream.getvalue(), self.tstring[1])

    def test_streamwriter(self):
        readfuncs = ('read', 'readline', 'readlines')
        UTF8Reader = codecs.getreader('utf-8')
        dla name w readfuncs:
            dla sizehint w [Nic] + list(range(1, 33)) + \
                            [64, 128, 256, 512, 1024]:
                istream = UTF8Reader(BytesIO(self.tstring[1]))
                ostream = self.writer(BytesIO())
                func = getattr(istream, name)
                dopóki 1:
                    jeżeli sizehint jest nie Nic:
                        data = func(sizehint)
                    inaczej:
                        data = func()

                    jeżeli nie data:
                        przerwij
                    jeżeli name == "readlines":
                        ostream.writelines(data)
                    inaczej:
                        ostream.write(data)

                self.assertEqual(ostream.getvalue(), self.tstring[0])

    def test_streamwriter_reset_no_pending(self):
        # Issue #23247: Calling reset() on a fresh StreamWriter instance
        # (without pending data) must nie crash
        stream = BytesIO()
        writer = self.writer(stream)
        writer.reset()


klasa TestBase_Mapping(unittest.TestCase):
    dalej_enctest = []
    dalej_dectest = []
    supmaps = []
    codectests = []

    def setUp(self):
        spróbuj:
            self.open_mapping_file().close() # test it to report the error early
        wyjąwszy (OSError, HTTPException):
            self.skipTest("Could nie retrieve "+self.mapfileurl)

    def open_mapping_file(self):
        zwróć support.open_urlresource(self.mapfileurl)

    def test_mapping_file(self):
        jeżeli self.mapfileurl.endswith('.xml'):
            self._test_mapping_file_ucm()
        inaczej:
            self._test_mapping_file_plain()

    def _test_mapping_file_plain(self):
        unichrs = lambda s: ''.join(map(chr, map(eval, s.split('+'))))
        urt_wa = {}

        przy self.open_mapping_file() jako f:
            dla line w f:
                jeżeli nie line:
                    przerwij
                data = line.split('#')[0].strip().split()
                jeżeli len(data) != 2:
                    kontynuuj

                csetval = eval(data[0])
                jeżeli csetval <= 0x7F:
                    csetch = bytes([csetval & 0xff])
                albo_inaczej csetval >= 0x1000000:
                    csetch = bytes([(csetval >> 24), ((csetval >> 16) & 0xff),
                                    ((csetval >> 8) & 0xff), (csetval & 0xff)])
                albo_inaczej csetval >= 0x10000:
                    csetch = bytes([(csetval >> 16), ((csetval >> 8) & 0xff),
                                    (csetval & 0xff)])
                albo_inaczej csetval >= 0x100:
                    csetch = bytes([(csetval >> 8), (csetval & 0xff)])
                inaczej:
                    kontynuuj

                unich = unichrs(data[1])
                jeżeli ord(unich) == 0xfffd albo unich w urt_wa:
                    kontynuuj
                urt_wa[unich] = csetch

                self._testpoint(csetch, unich)

    def _test_mapping_file_ucm(self):
        przy self.open_mapping_file() jako f:
            ucmdata = f.read()
        uc = re.findall('<a u="([A-F0-9]{4})" b="([0-9A-F ]+)"/>', ucmdata)
        dla uni, coded w uc:
            unich = chr(int(uni, 16))
            codech = bytes(int(c, 16) dla c w coded.split())
            self._testpoint(codech, unich)

    def test_mapping_supplemental(self):
        dla mapping w self.supmaps:
            self._testpoint(*mapping)

    def _testpoint(self, csetch, unich):
        jeżeli (csetch, unich) nie w self.pass_enctest:
            self.assertEqual(unich.encode(self.encoding), csetch)
        jeżeli (csetch, unich) nie w self.pass_dectest:
            self.assertEqual(str(csetch, self.encoding), unich)

    def test_errorhandle(self):
        dla source, scheme, expected w self.codectests:
            jeżeli isinstance(source, bytes):
                func = source.decode
            inaczej:
                func = source.encode
            jeżeli expected:
                jeżeli isinstance(source, bytes):
                    result = func(self.encoding, scheme)
                    self.assertPrawda(type(result) jest str, type(result))
                    self.assertEqual(result, expected,
                                     '%a.decode(%r, %r)=%a != %a'
                                     % (source, self.encoding, scheme, result,
                                        expected))
                inaczej:
                    result = func(self.encoding, scheme)
                    self.assertPrawda(type(result) jest bytes, type(result))
                    self.assertEqual(result, expected,
                                     '%a.encode(%r, %r)=%a != %a'
                                     % (source, self.encoding, scheme, result,
                                        expected))
            inaczej:
                self.assertRaises(UnicodeError, func, self.encoding, scheme)

def load_teststring(name):
    dir = os.path.join(os.path.dirname(__file__), 'cjkencodings')
    przy open(os.path.join(dir, name + '.txt'), 'rb') jako f:
        encoded = f.read()
    przy open(os.path.join(dir, name + '-utf8.txt'), 'rb') jako f:
        utf8 = f.read()
    zwróć encoded, utf8
