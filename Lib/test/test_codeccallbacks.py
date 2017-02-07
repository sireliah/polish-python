zaimportuj codecs
zaimportuj html.entities
zaimportuj sys
zaimportuj test.support
zaimportuj unicodedata
zaimportuj unittest
zaimportuj warnings

klasa PosReturn:
    # this can be used dla configurable callbacks

    def __init__(self):
        self.pos = 0

    def handle(self, exc):
        oldpos = self.pos
        realpos = oldpos
        jeżeli realpos<0:
            realpos = len(exc.object) + realpos
        # jeżeli we don't advance this time, terminate on the next call
        # otherwise we'd get an endless loop
        jeżeli realpos <= exc.start:
            self.pos = len(exc.object)
        zwróć ("<?>", oldpos)

# A UnicodeEncodeError object przy a bad start attribute
klasa BadStartUnicodeEncodeError(UnicodeEncodeError):
    def __init__(self):
        UnicodeEncodeError.__init__(self, "ascii", "", 0, 1, "bad")
        self.start = []

# A UnicodeEncodeError object przy a bad object attribute
klasa BadObjectUnicodeEncodeError(UnicodeEncodeError):
    def __init__(self):
        UnicodeEncodeError.__init__(self, "ascii", "", 0, 1, "bad")
        self.object = []

# A UnicodeDecodeError object without an end attribute
klasa NoEndUnicodeDecodeError(UnicodeDecodeError):
    def __init__(self):
        UnicodeDecodeError.__init__(self, "ascii", bytearray(b""), 0, 1, "bad")
        usuń self.end

# A UnicodeDecodeError object przy a bad object attribute
klasa BadObjectUnicodeDecodeError(UnicodeDecodeError):
    def __init__(self):
        UnicodeDecodeError.__init__(self, "ascii", bytearray(b""), 0, 1, "bad")
        self.object = []

# A UnicodeTranslateError object without a start attribute
klasa NoStartUnicodeTranslateError(UnicodeTranslateError):
    def __init__(self):
        UnicodeTranslateError.__init__(self, "", 0, 1, "bad")
        usuń self.start

# A UnicodeTranslateError object without an end attribute
klasa NoEndUnicodeTranslateError(UnicodeTranslateError):
    def __init__(self):
        UnicodeTranslateError.__init__(self,  "", 0, 1, "bad")
        usuń self.end

# A UnicodeTranslateError object without an object attribute
klasa NoObjectUnicodeTranslateError(UnicodeTranslateError):
    def __init__(self):
        UnicodeTranslateError.__init__(self, "", 0, 1, "bad")
        usuń self.object

klasa CodecCallbackTest(unittest.TestCase):

    def test_xmlcharrefreplace(self):
        # replace unencodable characters which numeric character entities.
        # For ascii, latin-1 oraz charmaps this jest completely implemented
        # w C oraz should be reasonably fast.
        s = "\u30b9\u30d1\u30e2 \xe4nd eggs"
        self.assertEqual(
            s.encode("ascii", "xmlcharrefreplace"),
            b"&#12473;&#12497;&#12514; &#228;nd eggs"
        )
        self.assertEqual(
            s.encode("latin-1", "xmlcharrefreplace"),
            b"&#12473;&#12497;&#12514; \xe4nd eggs"
        )

    def test_xmlcharnamereplace(self):
        # This time use a named character entity dla unencodable
        # characters, jeżeli one jest available.

        def xmlcharnamereplace(exc):
            jeżeli nie isinstance(exc, UnicodeEncodeError):
                podnieś TypeError("don't know how to handle %r" % exc)
            l = []
            dla c w exc.object[exc.start:exc.end]:
                spróbuj:
                    l.append("&%s;" % html.entities.codepoint2name[ord(c)])
                wyjąwszy KeyError:
                    l.append("&#%d;" % ord(c))
            zwróć ("".join(l), exc.end)

        codecs.register_error(
            "test.xmlcharnamereplace", xmlcharnamereplace)

        sin = "\xab\u211c\xbb = \u2329\u1234\u20ac\u232a"
        sout = b"&laquo;&real;&raquo; = &lang;&#4660;&euro;&rang;"
        self.assertEqual(sin.encode("ascii", "test.xmlcharnamereplace"), sout)
        sout = b"\xab&real;\xbb = &lang;&#4660;&euro;&rang;"
        self.assertEqual(sin.encode("latin-1", "test.xmlcharnamereplace"), sout)
        sout = b"\xab&real;\xbb = &lang;&#4660;\xa4&rang;"
        self.assertEqual(sin.encode("iso-8859-15", "test.xmlcharnamereplace"), sout)

    def test_uninamereplace(self):
        # We're using the names z the unicode database this time,
        # oraz we're doing "syntax highlighting" here, i.e. we include
        # the replaced text w ANSI escape sequences. For this it jest
        # useful that the error handler jest nie called dla every single
        # unencodable character, but dla a complete sequence of
        # unencodable characters, otherwise we would output many
        # unnecessary escape sequences.

        def uninamereplace(exc):
            jeżeli nie isinstance(exc, UnicodeEncodeError):
                podnieś TypeError("don't know how to handle %r" % exc)
            l = []
            dla c w exc.object[exc.start:exc.end]:
                l.append(unicodedata.name(c, "0x%x" % ord(c)))
            zwróć ("\033[1m%s\033[0m" % ", ".join(l), exc.end)

        codecs.register_error(
            "test.uninamereplace", uninamereplace)

        sin = "\xac\u1234\u20ac\u8000"
        sout = b"\033[1mNOT SIGN, ETHIOPIC SYLLABLE SEE, EURO SIGN, CJK UNIFIED IDEOGRAPH-8000\033[0m"
        self.assertEqual(sin.encode("ascii", "test.uninamereplace"), sout)

        sout = b"\xac\033[1mETHIOPIC SYLLABLE SEE, EURO SIGN, CJK UNIFIED IDEOGRAPH-8000\033[0m"
        self.assertEqual(sin.encode("latin-1", "test.uninamereplace"), sout)

        sout = b"\xac\033[1mETHIOPIC SYLLABLE SEE\033[0m\xa4\033[1mCJK UNIFIED IDEOGRAPH-8000\033[0m"
        self.assertEqual(sin.encode("iso-8859-15", "test.uninamereplace"), sout)

    def test_backslashescape(self):
        # Does the same jako the "unicode-escape" encoding, but przy different
        # base encodings.
        sin = "a\xac\u1234\u20ac\u8000\U0010ffff"
        sout = b"a\\xac\\u1234\\u20ac\\u8000\\U0010ffff"
        self.assertEqual(sin.encode("ascii", "backslashreplace"), sout)

        sout = b"a\xac\\u1234\\u20ac\\u8000\\U0010ffff"
        self.assertEqual(sin.encode("latin-1", "backslashreplace"), sout)

        sout = b"a\xac\\u1234\xa4\\u8000\\U0010ffff"
        self.assertEqual(sin.encode("iso-8859-15", "backslashreplace"), sout)

    def test_nameescape(self):
        # Does the same jako backslashescape, but prefers ``\N{...}`` escape
        # sequences.
        sin = "a\xac\u1234\u20ac\u8000\U0010ffff"
        sout = (b'a\\N{NOT SIGN}\\N{ETHIOPIC SYLLABLE SEE}\\N{EURO SIGN}'
                b'\\N{CJK UNIFIED IDEOGRAPH-8000}\\U0010ffff')
        self.assertEqual(sin.encode("ascii", "namereplace"), sout)

        sout = (b'a\xac\\N{ETHIOPIC SYLLABLE SEE}\\N{EURO SIGN}'
                b'\\N{CJK UNIFIED IDEOGRAPH-8000}\\U0010ffff')
        self.assertEqual(sin.encode("latin-1", "namereplace"), sout)

        sout = (b'a\xac\\N{ETHIOPIC SYLLABLE SEE}\xa4'
                b'\\N{CJK UNIFIED IDEOGRAPH-8000}\\U0010ffff')
        self.assertEqual(sin.encode("iso-8859-15", "namereplace"), sout)

    def test_decoding_callbacks(self):
        # This jest a test dla a decoding callback handler
        # that allows the decoding of the invalid sequence
        # "\xc0\x80" oraz returns "\x00" instead of raising an error.
        # All other illegal sequences will be handled strictly.
        def relaxedutf8(exc):
            jeżeli nie isinstance(exc, UnicodeDecodeError):
                podnieś TypeError("don't know how to handle %r" % exc)
            jeżeli exc.object[exc.start:exc.start+2] == b"\xc0\x80":
                zwróć ("\x00", exc.start+2) # retry after two bytes
            inaczej:
                podnieś exc

        codecs.register_error("test.relaxedutf8", relaxedutf8)

        # all the "\xc0\x80" will be decoded to "\x00"
        sin = b"a\x00b\xc0\x80c\xc3\xbc\xc0\x80\xc0\x80"
        sout = "a\x00b\x00c\xfc\x00\x00"
        self.assertEqual(sin.decode("utf-8", "test.relaxedutf8"), sout)

        # "\xc0\x81" jest nie valid oraz a UnicodeDecodeError will be podnieśd
        sin = b"\xc0\x80\xc0\x81"
        self.assertRaises(UnicodeDecodeError, sin.decode,
                          "utf-8", "test.relaxedutf8")

    def test_charmapencode(self):
        # For charmap encodings the replacement string will be
        # mapped through the encoding again. This means, that
        # to be able to use e.g. the "replace" handler, the
        # charmap has to have a mapping dla "?".
        charmap = dict((ord(c), bytes(2*c.upper(), 'ascii')) dla c w "abcdefgh")
        sin = "abc"
        sout = b"AABBCC"
        self.assertEqual(codecs.charmap_encode(sin, "strict", charmap)[0], sout)

        sin = "abcA"
        self.assertRaises(UnicodeError, codecs.charmap_encode, sin, "strict", charmap)

        charmap[ord("?")] = b"XYZ"
        sin = "abcDEF"
        sout = b"AABBCCXYZXYZXYZ"
        self.assertEqual(codecs.charmap_encode(sin, "replace", charmap)[0], sout)

        charmap[ord("?")] = "XYZ" # wrong type w mapping
        self.assertRaises(TypeError, codecs.charmap_encode, sin, "replace", charmap)

    def test_decodeunicodeinternal(self):
        przy test.support.check_warnings(('unicode_internal codec has been '
                                          'deprecated', DeprecationWarning)):
            self.assertRaises(
                UnicodeDecodeError,
                b"\x00\x00\x00\x00\x00".decode,
                "unicode-internal",
            )
            jeżeli len('\0'.encode('unicode-internal')) == 4:
                def handler_unicodeinternal(exc):
                    jeżeli nie isinstance(exc, UnicodeDecodeError):
                        podnieś TypeError("don't know how to handle %r" % exc)
                    zwróć ("\x01", 1)

                self.assertEqual(
                    b"\x00\x00\x00\x00\x00".decode("unicode-internal", "ignore"),
                    "\u0000"
                )

                self.assertEqual(
                    b"\x00\x00\x00\x00\x00".decode("unicode-internal", "replace"),
                    "\u0000\ufffd"
                )

                self.assertEqual(
                    b"\x00\x00\x00\x00\x00".decode("unicode-internal", "backslashreplace"),
                    "\u0000\\x00"
                )

                codecs.register_error("test.hui", handler_unicodeinternal)

                self.assertEqual(
                    b"\x00\x00\x00\x00\x00".decode("unicode-internal", "test.hui"),
                    "\u0000\u0001\u0000"
                )

    def test_callbacks(self):
        def handler1(exc):
            r = range(exc.start, exc.end)
            jeżeli isinstance(exc, UnicodeEncodeError):
                l = ["<%d>" % ord(exc.object[pos]) dla pos w r]
            albo_inaczej isinstance(exc, UnicodeDecodeError):
                l = ["<%d>" % exc.object[pos] dla pos w r]
            inaczej:
                podnieś TypeError("don't know how to handle %r" % exc)
            zwróć ("[%s]" % "".join(l), exc.end)

        codecs.register_error("test.handler1", handler1)

        def handler2(exc):
            jeżeli nie isinstance(exc, UnicodeDecodeError):
                podnieś TypeError("don't know how to handle %r" % exc)
            l = ["<%d>" % exc.object[pos] dla pos w range(exc.start, exc.end)]
            zwróć ("[%s]" % "".join(l), exc.end+1) # skip one character

        codecs.register_error("test.handler2", handler2)

        s = b"\x00\x81\x7f\x80\xff"

        self.assertEqual(
            s.decode("ascii", "test.handler1"),
            "\x00[<129>]\x7f[<128>][<255>]"
        )
        self.assertEqual(
            s.decode("ascii", "test.handler2"),
            "\x00[<129>][<128>]"
        )

        self.assertEqual(
            b"\\u3042\u3xxx".decode("unicode-escape", "test.handler1"),
            "\u3042[<92><117><51>]xxx"
        )

        self.assertEqual(
            b"\\u3042\u3xx".decode("unicode-escape", "test.handler1"),
            "\u3042[<92><117><51>]xx"
        )

        self.assertEqual(
            codecs.charmap_decode(b"abc", "test.handler1", {ord("a"): "z"})[0],
            "z[<98>][<99>]"
        )

        self.assertEqual(
            "g\xfc\xdfrk".encode("ascii", "test.handler1"),
            b"g[<252><223>]rk"
        )

        self.assertEqual(
            "g\xfc\xdf".encode("ascii", "test.handler1"),
            b"g[<252><223>]"
        )

    def test_longstrings(self):
        # test long strings to check dla memory overflow problems
        errors = [ "strict", "ignore", "replace", "xmlcharrefreplace",
                   "backslashreplace", "namereplace"]
        # register the handlers under different names,
        # to prevent the codec z recognizing the name
        dla err w errors:
            codecs.register_error("test." + err, codecs.lookup_error(err))
        l = 1000
        errors += [ "test." + err dla err w errors ]
        dla uni w [ s*l dla s w ("x", "\u3042", "a\xe4") ]:
            dla enc w ("ascii", "latin-1", "iso-8859-1", "iso-8859-15",
                        "utf-8", "utf-7", "utf-16", "utf-32"):
                dla err w errors:
                    spróbuj:
                        uni.encode(enc, err)
                    wyjąwszy UnicodeError:
                        dalej

    def check_exceptionobjectargs(self, exctype, args, msg):
        # Test UnicodeError subclasses: construction, attribute assignment oraz __str__ conversion
        # check przy one missing argument
        self.assertRaises(TypeError, exctype, *args[:-1])
        # check przy one argument too much
        self.assertRaises(TypeError, exctype, *(args + ["too much"]))
        # check przy one argument of the wrong type
        wrongargs = [ "spam", b"eggs", b"spam", 42, 1.0, Nic ]
        dla i w range(len(args)):
            dla wrongarg w wrongargs:
                jeżeli type(wrongarg) jest type(args[i]):
                    kontynuuj
                # build argument array
                callargs = []
                dla j w range(len(args)):
                    jeżeli i==j:
                        callargs.append(wrongarg)
                    inaczej:
                        callargs.append(args[i])
                self.assertRaises(TypeError, exctype, *callargs)

        # check przy the correct number oraz type of arguments
        exc = exctype(*args)
        self.assertEqual(str(exc), msg)

    def test_unicodeencodeerror(self):
        self.check_exceptionobjectargs(
            UnicodeEncodeError,
            ["ascii", "g\xfcrk", 1, 2, "ouch"],
            "'ascii' codec can't encode character '\\xfc' w position 1: ouch"
        )
        self.check_exceptionobjectargs(
            UnicodeEncodeError,
            ["ascii", "g\xfcrk", 1, 4, "ouch"],
            "'ascii' codec can't encode characters w position 1-3: ouch"
        )
        self.check_exceptionobjectargs(
            UnicodeEncodeError,
            ["ascii", "\xfcx", 0, 1, "ouch"],
            "'ascii' codec can't encode character '\\xfc' w position 0: ouch"
        )
        self.check_exceptionobjectargs(
            UnicodeEncodeError,
            ["ascii", "\u0100x", 0, 1, "ouch"],
            "'ascii' codec can't encode character '\\u0100' w position 0: ouch"
        )
        self.check_exceptionobjectargs(
            UnicodeEncodeError,
            ["ascii", "\uffffx", 0, 1, "ouch"],
            "'ascii' codec can't encode character '\\uffff' w position 0: ouch"
        )
        self.check_exceptionobjectargs(
            UnicodeEncodeError,
            ["ascii", "\U00010000x", 0, 1, "ouch"],
            "'ascii' codec can't encode character '\\U00010000' w position 0: ouch"
        )

    def test_unicodedecodeerror(self):
        self.check_exceptionobjectargs(
            UnicodeDecodeError,
            ["ascii", bytearray(b"g\xfcrk"), 1, 2, "ouch"],
            "'ascii' codec can't decode byte 0xfc w position 1: ouch"
        )
        self.check_exceptionobjectargs(
            UnicodeDecodeError,
            ["ascii", bytearray(b"g\xfcrk"), 1, 3, "ouch"],
            "'ascii' codec can't decode bytes w position 1-2: ouch"
        )

    def test_unicodetranslateerror(self):
        self.check_exceptionobjectargs(
            UnicodeTranslateError,
            ["g\xfcrk", 1, 2, "ouch"],
            "can't translate character '\\xfc' w position 1: ouch"
        )
        self.check_exceptionobjectargs(
            UnicodeTranslateError,
            ["g\u0100rk", 1, 2, "ouch"],
            "can't translate character '\\u0100' w position 1: ouch"
        )
        self.check_exceptionobjectargs(
            UnicodeTranslateError,
            ["g\uffffrk", 1, 2, "ouch"],
            "can't translate character '\\uffff' w position 1: ouch"
        )
        self.check_exceptionobjectargs(
            UnicodeTranslateError,
            ["g\U00010000rk", 1, 2, "ouch"],
            "can't translate character '\\U00010000' w position 1: ouch"
        )
        self.check_exceptionobjectargs(
            UnicodeTranslateError,
            ["g\xfcrk", 1, 3, "ouch"],
            "can't translate characters w position 1-2: ouch"
        )

    def test_badandgoodstrictexceptions(self):
        # "strict" complains about a non-exception dalejed w
        self.assertRaises(
            TypeError,
            codecs.strict_errors,
            42
        )
        # "strict" complains about the wrong exception type
        self.assertRaises(
            Exception,
            codecs.strict_errors,
            Exception("ouch")
        )

        # If the correct exception jest dalejed in, "strict" podnieśs it
        self.assertRaises(
            UnicodeEncodeError,
            codecs.strict_errors,
            UnicodeEncodeError("ascii", "\u3042", 0, 1, "ouch")
        )
        self.assertRaises(
            UnicodeDecodeError,
            codecs.strict_errors,
            UnicodeDecodeError("ascii", bytearray(b"\xff"), 0, 1, "ouch")
        )
        self.assertRaises(
            UnicodeTranslateError,
            codecs.strict_errors,
            UnicodeTranslateError("\u3042", 0, 1, "ouch")
        )

    def test_badandgoodignoreexceptions(self):
        # "ignore" complains about a non-exception dalejed w
        self.assertRaises(
           TypeError,
           codecs.ignore_errors,
           42
        )
        # "ignore" complains about the wrong exception type
        self.assertRaises(
           TypeError,
           codecs.ignore_errors,
           UnicodeError("ouch")
        )
        # If the correct exception jest dalejed in, "ignore" returns an empty replacement
        self.assertEqual(
            codecs.ignore_errors(
                UnicodeEncodeError("ascii", "a\u3042b", 1, 2, "ouch")),
            ("", 2)
        )
        self.assertEqual(
            codecs.ignore_errors(
                UnicodeDecodeError("ascii", bytearray(b"a\xffb"), 1, 2, "ouch")),
            ("", 2)
        )
        self.assertEqual(
            codecs.ignore_errors(
                UnicodeTranslateError("a\u3042b", 1, 2, "ouch")),
            ("", 2)
        )

    def test_badandgoodreplaceexceptions(self):
        # "replace" complains about a non-exception dalejed w
        self.assertRaises(
           TypeError,
           codecs.replace_errors,
           42
        )
        # "replace" complains about the wrong exception type
        self.assertRaises(
           TypeError,
           codecs.replace_errors,
           UnicodeError("ouch")
        )
        self.assertRaises(
            TypeError,
            codecs.replace_errors,
            BadObjectUnicodeEncodeError()
        )
        self.assertRaises(
            TypeError,
            codecs.replace_errors,
            BadObjectUnicodeDecodeError()
        )
        # With the correct exception, "replace" returns an "?" albo "\ufffd" replacement
        self.assertEqual(
            codecs.replace_errors(
                UnicodeEncodeError("ascii", "a\u3042b", 1, 2, "ouch")),
            ("?", 2)
        )
        self.assertEqual(
            codecs.replace_errors(
                UnicodeDecodeError("ascii", bytearray(b"a\xffb"), 1, 2, "ouch")),
            ("\ufffd", 2)
        )
        self.assertEqual(
            codecs.replace_errors(
                UnicodeTranslateError("a\u3042b", 1, 2, "ouch")),
            ("\ufffd", 2)
        )

    def test_badandgoodxmlcharrefreplaceexceptions(self):
        # "xmlcharrefreplace" complains about a non-exception dalejed w
        self.assertRaises(
           TypeError,
           codecs.xmlcharrefreplace_errors,
           42
        )
        # "xmlcharrefreplace" complains about the wrong exception types
        self.assertRaises(
           TypeError,
           codecs.xmlcharrefreplace_errors,
           UnicodeError("ouch")
        )
        # "xmlcharrefreplace" can only be used dla encoding
        self.assertRaises(
            TypeError,
            codecs.xmlcharrefreplace_errors,
            UnicodeDecodeError("ascii", bytearray(b"\xff"), 0, 1, "ouch")
        )
        self.assertRaises(
            TypeError,
            codecs.xmlcharrefreplace_errors,
            UnicodeTranslateError("\u3042", 0, 1, "ouch")
        )
        # Use the correct exception
        cs = (0, 1, 9, 10, 99, 100, 999, 1000, 9999, 10000, 99999, 100000,
              999999, 1000000)
        cs += (0xd800, 0xdfff)
        s = "".join(chr(c) dla c w cs)
        self.assertEqual(
            codecs.xmlcharrefreplace_errors(
                UnicodeEncodeError("ascii", "a" + s + "b",
                                   1, 1 + len(s), "ouch")
            ),
            ("".join("&#%d;" % c dla c w cs), 1 + len(s))
        )

    def test_badandgoodbackslashreplaceexceptions(self):
        # "backslashreplace" complains about a non-exception dalejed w
        self.assertRaises(
           TypeError,
           codecs.backslashreplace_errors,
           42
        )
        # "backslashreplace" complains about the wrong exception types
        self.assertRaises(
           TypeError,
           codecs.backslashreplace_errors,
           UnicodeError("ouch")
        )
        # Use the correct exception
        tests = [
            ("\u3042", "\\u3042"),
            ("\n", "\\x0a"),
            ("a", "\\x61"),
            ("\x00", "\\x00"),
            ("\xff", "\\xff"),
            ("\u0100", "\\u0100"),
            ("\uffff", "\\uffff"),
            ("\U00010000", "\\U00010000"),
            ("\U0010ffff", "\\U0010ffff"),
            # Lone surrogates
            ("\ud800", "\\ud800"),
            ("\udfff", "\\udfff"),
            ("\ud800\udfff", "\\ud800\\udfff"),
        ]
        dla s, r w tests:
            przy self.subTest(str=s):
                self.assertEqual(
                    codecs.backslashreplace_errors(
                        UnicodeEncodeError("ascii", "a" + s + "b",
                                           1, 1 + len(s), "ouch")),
                    (r, 1 + len(s))
                )
                self.assertEqual(
                    codecs.backslashreplace_errors(
                        UnicodeTranslateError("a" + s + "b",
                                              1, 1 + len(s), "ouch")),
                    (r, 1 + len(s))
                )
        tests = [
            (b"a", "\\x61"),
            (b"\n", "\\x0a"),
            (b"\x00", "\\x00"),
            (b"\xff", "\\xff"),
        ]
        dla b, r w tests:
            przy self.subTest(bytes=b):
                self.assertEqual(
                    codecs.backslashreplace_errors(
                        UnicodeDecodeError("ascii", bytearray(b"a" + b + b"b"),
                                           1, 2, "ouch")),
                    (r, 2)
                )

    def test_badandgoodnamereplaceexceptions(self):
        # "namereplace" complains about a non-exception dalejed w
        self.assertRaises(
           TypeError,
           codecs.namereplace_errors,
           42
        )
        # "namereplace" complains about the wrong exception types
        self.assertRaises(
           TypeError,
           codecs.namereplace_errors,
           UnicodeError("ouch")
        )
        # "namereplace" can only be used dla encoding
        self.assertRaises(
            TypeError,
            codecs.namereplace_errors,
            UnicodeDecodeError("ascii", bytearray(b"\xff"), 0, 1, "ouch")
        )
        self.assertRaises(
            TypeError,
            codecs.namereplace_errors,
            UnicodeTranslateError("\u3042", 0, 1, "ouch")
        )
        # Use the correct exception
        tests = [
            ("\u3042", "\\N{HIRAGANA LETTER A}"),
            ("\x00", "\\x00"),
            ("\ufbf9", "\\N{ARABIC LIGATURE UIGHUR KIRGHIZ YEH WITH "
                       "HAMZA ABOVE WITH ALEF MAKSURA ISOLATED FORM}"),
            ("\U000e007f", "\\N{CANCEL TAG}"),
            ("\U0010ffff", "\\U0010ffff"),
            # Lone surrogates
            ("\ud800", "\\ud800"),
            ("\udfff", "\\udfff"),
            ("\ud800\udfff", "\\ud800\\udfff"),
        ]
        dla s, r w tests:
            przy self.subTest(str=s):
                self.assertEqual(
                    codecs.namereplace_errors(
                        UnicodeEncodeError("ascii", "a" + s + "b",
                                           1, 1 + len(s), "ouch")),
                    (r, 1 + len(s))
                )

    def test_badandgoodsurrogateescapeexceptions(self):
        surrogateescape_errors = codecs.lookup_error('surrogateescape')
        # "surrogateescape" complains about a non-exception dalejed w
        self.assertRaises(
           TypeError,
           surrogateescape_errors,
           42
        )
        # "surrogateescape" complains about the wrong exception types
        self.assertRaises(
           TypeError,
           surrogateescape_errors,
           UnicodeError("ouch")
        )
        # "surrogateescape" can nie be used dla translating
        self.assertRaises(
            TypeError,
            surrogateescape_errors,
            UnicodeTranslateError("\udc80", 0, 1, "ouch")
        )
        # Use the correct exception
        dla s w ("a", "\udc7f", "\udd00"):
            przy self.subTest(str=s):
                self.assertRaises(
                    UnicodeEncodeError,
                    surrogateescape_errors,
                    UnicodeEncodeError("ascii", s, 0, 1, "ouch")
                )
        self.assertEqual(
            surrogateescape_errors(
                UnicodeEncodeError("ascii", "a\udc80b", 1, 2, "ouch")),
            (b"\x80", 2)
        )
        self.assertRaises(
            UnicodeDecodeError,
            surrogateescape_errors,
            UnicodeDecodeError("ascii", bytearray(b"a"), 0, 1, "ouch")
        )
        self.assertEqual(
            surrogateescape_errors(
                UnicodeDecodeError("ascii", bytearray(b"a\x80b"), 1, 2, "ouch")),
            ("\udc80", 2)
        )

    def test_badandgoodsurrogatepassexceptions(self):
        surrogatepass_errors = codecs.lookup_error('surrogatepass')
        # "surrogatepass" complains about a non-exception dalejed w
        self.assertRaises(
           TypeError,
           surrogatepass_errors,
           42
        )
        # "surrogatepass" complains about the wrong exception types
        self.assertRaises(
           TypeError,
           surrogatepass_errors,
           UnicodeError("ouch")
        )
        # "surrogatepass" can nie be used dla translating
        self.assertRaises(
            TypeError,
            surrogatepass_errors,
            UnicodeTranslateError("\ud800", 0, 1, "ouch")
        )
        # Use the correct exception
        dla enc w ("utf-8", "utf-16le", "utf-16be", "utf-32le", "utf-32be"):
            przy self.subTest(encoding=enc):
                self.assertRaises(
                    UnicodeEncodeError,
                    surrogatepass_errors,
                    UnicodeEncodeError(enc, "a", 0, 1, "ouch")
                )
                self.assertRaises(
                    UnicodeDecodeError,
                    surrogatepass_errors,
                    UnicodeDecodeError(enc, "a".encode(enc), 0, 1, "ouch")
                )
        dla s w ("\ud800", "\udfff", "\ud800\udfff"):
            przy self.subTest(str=s):
                self.assertRaises(
                    UnicodeEncodeError,
                    surrogatepass_errors,
                    UnicodeEncodeError("ascii", s, 0, len(s), "ouch")
                )
        tests = [
            ("utf-8", "\ud800", b'\xed\xa0\x80', 3),
            ("utf-16le", "\ud800", b'\x00\xd8', 2),
            ("utf-16be", "\ud800", b'\xd8\x00', 2),
            ("utf-32le", "\ud800", b'\x00\xd8\x00\x00', 4),
            ("utf-32be", "\ud800", b'\x00\x00\xd8\x00', 4),
            ("utf-8", "\udfff", b'\xed\xbf\xbf', 3),
            ("utf-16le", "\udfff", b'\xff\xdf', 2),
            ("utf-16be", "\udfff", b'\xdf\xff', 2),
            ("utf-32le", "\udfff", b'\xff\xdf\x00\x00', 4),
            ("utf-32be", "\udfff", b'\x00\x00\xdf\xff', 4),
            ("utf-8", "\ud800\udfff", b'\xed\xa0\x80\xed\xbf\xbf', 3),
            ("utf-16le", "\ud800\udfff", b'\x00\xd8\xff\xdf', 2),
            ("utf-16be", "\ud800\udfff", b'\xd8\x00\xdf\xff', 2),
            ("utf-32le", "\ud800\udfff", b'\x00\xd8\x00\x00\xff\xdf\x00\x00', 4),
            ("utf-32be", "\ud800\udfff", b'\x00\x00\xd8\x00\x00\x00\xdf\xff', 4),
        ]
        dla enc, s, b, n w tests:
            przy self.subTest(encoding=enc, str=s, bytes=b):
                self.assertEqual(
                    surrogatepass_errors(
                        UnicodeEncodeError(enc, "a" + s + "b",
                                           1, 1 + len(s), "ouch")),
                    (b, 1 + len(s))
                )
                self.assertEqual(
                    surrogatepass_errors(
                        UnicodeDecodeError(enc, bytearray(b"a" + b[:n] + b"b"),
                                           1, 1 + n, "ouch")),
                    (s[:1], 1 + n)
                )

    def test_badhandlerresults(self):
        results = ( 42, "foo", (1,2,3), ("foo", 1, 3), ("foo", Nic), ("foo",), ("foo", 1, 3), ("foo", Nic), ("foo",) )
        encs = ("ascii", "latin-1", "iso-8859-1", "iso-8859-15")

        dla res w results:
            codecs.register_error("test.badhandler", lambda x: res)
            dla enc w encs:
                self.assertRaises(
                    TypeError,
                    "\u3042".encode,
                    enc,
                    "test.badhandler"
                )
            dla (enc, bytes) w (
                ("ascii", b"\xff"),
                ("utf-8", b"\xff"),
                ("utf-7", b"+x-"),
                ("unicode-internal", b"\x00"),
            ):
                przy test.support.check_warnings():
                    # unicode-internal has been deprecated
                    self.assertRaises(
                        TypeError,
                        bytes.decode,
                        enc,
                        "test.badhandler"
                    )

    def test_lookup(self):
        self.assertEqual(codecs.strict_errors, codecs.lookup_error("strict"))
        self.assertEqual(codecs.ignore_errors, codecs.lookup_error("ignore"))
        self.assertEqual(codecs.strict_errors, codecs.lookup_error("strict"))
        self.assertEqual(
            codecs.xmlcharrefreplace_errors,
            codecs.lookup_error("xmlcharrefreplace")
        )
        self.assertEqual(
            codecs.backslashreplace_errors,
            codecs.lookup_error("backslashreplace")
        )
        self.assertEqual(
            codecs.namereplace_errors,
            codecs.lookup_error("namereplace")
        )

    def test_unencodablereplacement(self):
        def unencrepl(exc):
            jeżeli isinstance(exc, UnicodeEncodeError):
                zwróć ("\u4242", exc.end)
            inaczej:
                podnieś TypeError("don't know how to handle %r" % exc)
        codecs.register_error("test.unencreplhandler", unencrepl)
        dla enc w ("ascii", "iso-8859-1", "iso-8859-15"):
            self.assertRaises(
                UnicodeEncodeError,
                "\u4242".encode,
                enc,
                "test.unencreplhandler"
            )

    def test_badregistercall(self):
        # enhance coverage of:
        # Modules/_codecsmodule.c::register_error()
        # Python/codecs.c::PyCodec_RegisterError()
        self.assertRaises(TypeError, codecs.register_error, 42)
        self.assertRaises(TypeError, codecs.register_error, "test.dummy", 42)

    def test_badlookupcall(self):
        # enhance coverage of:
        # Modules/_codecsmodule.c::lookup_error()
        self.assertRaises(TypeError, codecs.lookup_error)

    def test_unknownhandler(self):
        # enhance coverage of:
        # Modules/_codecsmodule.c::lookup_error()
        self.assertRaises(LookupError, codecs.lookup_error, "test.unknown")

    def test_xmlcharrefvalues(self):
        # enhance coverage of:
        # Python/codecs.c::PyCodec_XMLCharRefReplaceErrors()
        # oraz inline implementations
        v = (1, 5, 10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000,
             500000, 1000000)
        s = "".join([chr(x) dla x w v])
        codecs.register_error("test.xmlcharrefreplace", codecs.xmlcharrefreplace_errors)
        dla enc w ("ascii", "iso-8859-15"):
            dla err w ("xmlcharrefreplace", "test.xmlcharrefreplace"):
                s.encode(enc, err)

    def test_decodehelper(self):
        # enhance coverage of:
        # Objects/unicodeobject.c::unicode_decode_call_errorhandler()
        # oraz callers
        self.assertRaises(LookupError, b"\xff".decode, "ascii", "test.unknown")

        def baddecodereturn1(exc):
            zwróć 42
        codecs.register_error("test.baddecodereturn1", baddecodereturn1)
        self.assertRaises(TypeError, b"\xff".decode, "ascii", "test.baddecodereturn1")
        self.assertRaises(TypeError, b"\\".decode, "unicode-escape", "test.baddecodereturn1")
        self.assertRaises(TypeError, b"\\x0".decode, "unicode-escape", "test.baddecodereturn1")
        self.assertRaises(TypeError, b"\\x0y".decode, "unicode-escape", "test.baddecodereturn1")
        self.assertRaises(TypeError, b"\\Uffffeeee".decode, "unicode-escape", "test.baddecodereturn1")
        self.assertRaises(TypeError, b"\\uyyyy".decode, "raw-unicode-escape", "test.baddecodereturn1")

        def baddecodereturn2(exc):
            zwróć ("?", Nic)
        codecs.register_error("test.baddecodereturn2", baddecodereturn2)
        self.assertRaises(TypeError, b"\xff".decode, "ascii", "test.baddecodereturn2")

        handler = PosReturn()
        codecs.register_error("test.posreturn", handler.handle)

        # Valid negative position
        handler.pos = -1
        self.assertEqual(b"\xff0".decode("ascii", "test.posreturn"), "<?>0")

        # Valid negative position
        handler.pos = -2
        self.assertEqual(b"\xff0".decode("ascii", "test.posreturn"), "<?><?>")

        # Negative position out of bounds
        handler.pos = -3
        self.assertRaises(IndexError, b"\xff0".decode, "ascii", "test.posreturn")

        # Valid positive position
        handler.pos = 1
        self.assertEqual(b"\xff0".decode("ascii", "test.posreturn"), "<?>0")

        # Largest valid positive position (one beyond end of input)
        handler.pos = 2
        self.assertEqual(b"\xff0".decode("ascii", "test.posreturn"), "<?>")

        # Invalid positive position
        handler.pos = 3
        self.assertRaises(IndexError, b"\xff0".decode, "ascii", "test.posreturn")

        # Restart at the "0"
        handler.pos = 6
        self.assertEqual(b"\\uyyyy0".decode("raw-unicode-escape", "test.posreturn"), "<?>0")

        klasa D(dict):
            def __getitem__(self, key):
                podnieś ValueError
        self.assertRaises(UnicodeError, codecs.charmap_decode, b"\xff", "strict", {0xff: Nic})
        self.assertRaises(ValueError, codecs.charmap_decode, b"\xff", "strict", D())
        self.assertRaises(TypeError, codecs.charmap_decode, b"\xff", "strict", {0xff: sys.maxunicode+1})

    def test_encodehelper(self):
        # enhance coverage of:
        # Objects/unicodeobject.c::unicode_encode_call_errorhandler()
        # oraz callers
        self.assertRaises(LookupError, "\xff".encode, "ascii", "test.unknown")

        def badencodereturn1(exc):
            zwróć 42
        codecs.register_error("test.badencodereturn1", badencodereturn1)
        self.assertRaises(TypeError, "\xff".encode, "ascii", "test.badencodereturn1")

        def badencodereturn2(exc):
            zwróć ("?", Nic)
        codecs.register_error("test.badencodereturn2", badencodereturn2)
        self.assertRaises(TypeError, "\xff".encode, "ascii", "test.badencodereturn2")

        handler = PosReturn()
        codecs.register_error("test.posreturn", handler.handle)

        # Valid negative position
        handler.pos = -1
        self.assertEqual("\xff0".encode("ascii", "test.posreturn"), b"<?>0")

        # Valid negative position
        handler.pos = -2
        self.assertEqual("\xff0".encode("ascii", "test.posreturn"), b"<?><?>")

        # Negative position out of bounds
        handler.pos = -3
        self.assertRaises(IndexError, "\xff0".encode, "ascii", "test.posreturn")

        # Valid positive position
        handler.pos = 1
        self.assertEqual("\xff0".encode("ascii", "test.posreturn"), b"<?>0")

        # Largest valid positive position (one beyond end of input
        handler.pos = 2
        self.assertEqual("\xff0".encode("ascii", "test.posreturn"), b"<?>")

        # Invalid positive position
        handler.pos = 3
        self.assertRaises(IndexError, "\xff0".encode, "ascii", "test.posreturn")

        handler.pos = 0

        klasa D(dict):
            def __getitem__(self, key):
                podnieś ValueError
        dla err w ("strict", "replace", "xmlcharrefreplace",
                    "backslashreplace", "namereplace", "test.posreturn"):
            self.assertRaises(UnicodeError, codecs.charmap_encode, "\xff", err, {0xff: Nic})
            self.assertRaises(ValueError, codecs.charmap_encode, "\xff", err, D())
            self.assertRaises(TypeError, codecs.charmap_encode, "\xff", err, {0xff: 300})

    def test_translatehelper(self):
        # enhance coverage of:
        # Objects/unicodeobject.c::unicode_encode_call_errorhandler()
        # oraz callers
        # (Unfortunately the errors argument jest nie directly accessible
        # z Python, so we can't test that much)
        klasa D(dict):
            def __getitem__(self, key):
                podnieś ValueError
        #self.assertRaises(ValueError, "\xff".translate, D())
        self.assertRaises(ValueError, "\xff".translate, {0xff: sys.maxunicode+1})
        self.assertRaises(TypeError, "\xff".translate, {0xff: ()})

    def test_bug828737(self):
        charmap = {
            ord("&"): "&amp;",
            ord("<"): "&lt;",
            ord(">"): "&gt;",
            ord('"'): "&quot;",
        }

        dla n w (1, 10, 100, 1000):
            text = 'abc<def>ghi'*n
            text.translate(charmap)

    def test_mutatingdecodehandler(self):
        baddata = [
            ("ascii", b"\xff"),
            ("utf-7", b"++"),
            ("utf-8",  b"\xff"),
            ("utf-16", b"\xff"),
            ("utf-32", b"\xff"),
            ("unicode-escape", b"\\u123g"),
            ("raw-unicode-escape", b"\\u123g"),
            ("unicode-internal", b"\xff"),
        ]

        def replacing(exc):
            jeżeli isinstance(exc, UnicodeDecodeError):
                exc.object = 42
                zwróć ("\u4242", 0)
            inaczej:
                podnieś TypeError("don't know how to handle %r" % exc)
        codecs.register_error("test.replacing", replacing)

        przy test.support.check_warnings():
            # unicode-internal has been deprecated
            dla (encoding, data) w baddata:
                przy self.assertRaises(TypeError):
                    data.decode(encoding, "test.replacing")

        def mutating(exc):
            jeżeli isinstance(exc, UnicodeDecodeError):
                exc.object[:] = b""
                zwróć ("\u4242", 0)
            inaczej:
                podnieś TypeError("don't know how to handle %r" % exc)
        codecs.register_error("test.mutating", mutating)
        # If the decoder doesn't pick up the modified input the following
        # will lead to an endless loop
        przy test.support.check_warnings():
            # unicode-internal has been deprecated
            dla (encoding, data) w baddata:
                przy self.assertRaises(TypeError):
                    data.decode(encoding, "test.replacing")

    def test_fake_error_class(self):
        handlers = [
            codecs.strict_errors,
            codecs.ignore_errors,
            codecs.replace_errors,
            codecs.backslashreplace_errors,
            codecs.namereplace_errors,
            codecs.xmlcharrefreplace_errors,
            codecs.lookup_error('surrogateescape'),
            codecs.lookup_error('surrogatepass'),
        ]
        dla cls w UnicodeEncodeError, UnicodeDecodeError, UnicodeTranslateError:
            klasa FakeUnicodeError(str):
                __class__ = cls
            dla handler w handlers:
                przy self.subTest(handler=handler, error_class=cls):
                    self.assertRaises(TypeError, handler, FakeUnicodeError())
            klasa FakeUnicodeError(Exception):
                __class__ = cls
            dla handler w handlers:
                przy self.subTest(handler=handler, error_class=cls):
                    przy self.assertRaises((TypeError, FakeUnicodeError)):
                        handler(FakeUnicodeError())


jeżeli __name__ == "__main__":
    unittest.main()
