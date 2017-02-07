"""Tests dla http/cookiejar.py."""

zaimportuj os
zaimportuj re
zaimportuj test.support
zaimportuj time
zaimportuj unittest
zaimportuj urllib.request

z http.cookiejar zaimportuj (time2isoz, http2time, iso2time, time2netscape,
     parse_ns_headers, join_header_words, split_header_words, Cookie,
     CookieJar, DefaultCookiePolicy, LWPCookieJar, MozillaCookieJar,
     LoadError, lwp_cookie_str, DEFAULT_HTTP_PORT, escape_path,
     reach, is_HDN, domain_match, user_domain_match, request_path,
     request_port, request_host)


klasa DateTimeTests(unittest.TestCase):

    def test_time2isoz(self):
        base = 1019227000
        day = 24*3600
        self.assertEqual(time2isoz(base), "2002-04-19 14:36:40Z")
        self.assertEqual(time2isoz(base+day), "2002-04-20 14:36:40Z")
        self.assertEqual(time2isoz(base+2*day), "2002-04-21 14:36:40Z")
        self.assertEqual(time2isoz(base+3*day), "2002-04-22 14:36:40Z")

        az = time2isoz()
        bz = time2isoz(500000)
        dla text w (az, bz):
            self.assertRegex(text, r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\dZ$",
                             "bad time2isoz format: %s %s" % (az, bz))

    def test_http2time(self):
        def parse_date(text):
            zwróć time.gmtime(http2time(text))[:6]

        self.assertEqual(parse_date("01 Jan 2001"), (2001, 1, 1, 0, 0, 0.0))

        # this test will przerwij around year 2070
        self.assertEqual(parse_date("03-Feb-20"), (2020, 2, 3, 0, 0, 0.0))

        # this test will przerwij around year 2048
        self.assertEqual(parse_date("03-Feb-98"), (1998, 2, 3, 0, 0, 0.0))

    def test_http2time_formats(self):
        # test http2time dla supported dates.  Test cases przy 2 digit year
        # will probably przerwij w year 2044.
        tests = [
         'Thu, 03 Feb 1994 00:00:00 GMT',  # proposed new HTTP format
         'Thursday, 03-Feb-94 00:00:00 GMT',  # old rfc850 HTTP format
         'Thursday, 03-Feb-1994 00:00:00 GMT',  # broken rfc850 HTTP format

         '03 Feb 1994 00:00:00 GMT',  # HTTP format (no weekday)
         '03-Feb-94 00:00:00 GMT',  # old rfc850 (no weekday)
         '03-Feb-1994 00:00:00 GMT',  # broken rfc850 (no weekday)
         '03-Feb-1994 00:00 GMT',  # broken rfc850 (no weekday, no seconds)
         '03-Feb-1994 00:00',  # broken rfc850 (no weekday, no seconds, no tz)
         '02-Feb-1994 24:00',  # broken rfc850 (no weekday, no seconds,
                               # no tz) using hour 24 przy yesterday date

         '03-Feb-94',  # old rfc850 HTTP format (no weekday, no time)
         '03-Feb-1994',  # broken rfc850 HTTP format (no weekday, no time)
         '03 Feb 1994',  # proposed new HTTP format (no weekday, no time)

         # A few tests przy extra space at various places
         '  03   Feb   1994  0:00  ',
         '  03-Feb-1994  ',
        ]

        test_t = 760233600  # assume broken POSIX counting of seconds
        result = time2isoz(test_t)
        expected = "1994-02-03 00:00:00Z"
        self.assertEqual(result, expected,
                         "%s  =>  '%s' (%s)" % (test_t, result, expected))

        dla s w tests:
            self.assertEqual(http2time(s), test_t, s)
            self.assertEqual(http2time(s.lower()), test_t, s.lower())
            self.assertEqual(http2time(s.upper()), test_t, s.upper())

    def test_http2time_garbage(self):
        dla test w [
            '',
            'Garbage',
            'Mandag 16. September 1996',
            '01-00-1980',
            '01-13-1980',
            '00-01-1980',
            '32-01-1980',
            '01-01-1980 25:00:00',
            '01-01-1980 00:61:00',
            '01-01-1980 00:00:62',
            ]:
            self.assertIsNic(http2time(test),
                              "http2time(%s) jest nie Nic\n"
                              "http2time(test) %s" % (test, http2time(test)))

    def test_iso2time(self):
        def parse_date(text):
            zwróć time.gmtime(iso2time(text))[:6]

        # ISO 8601 compact format
        self.assertEqual(parse_date("19940203T141529Z"),
                         (1994, 2, 3, 14, 15, 29))

        # ISO 8601 przy time behind UTC
        self.assertEqual(parse_date("1994-02-03 07:15:29 -0700"),
                         (1994, 2, 3, 14, 15, 29))

        # ISO 8601 przy time ahead of UTC
        self.assertEqual(parse_date("1994-02-03 19:45:29 +0530"),
                         (1994, 2, 3, 14, 15, 29))

    def test_iso2time_formats(self):
        # test iso2time dla supported dates.
        tests = [
            '1994-02-03 00:00:00 -0000', # ISO 8601 format
            '1994-02-03 00:00:00 +0000', # ISO 8601 format
            '1994-02-03 00:00:00',       # zone jest optional
            '1994-02-03',                # only date
            '1994-02-03T00:00:00',       # Use T jako separator
            '19940203',                  # only date
            '1994-02-02 24:00:00',       # using hour-24 yesterday date
            '19940203T000000Z',          # ISO 8601 compact format

            # A few tests przy extra space at various places
            '  1994-02-03 ',
            '  1994-02-03T00:00:00  ',
        ]

        test_t = 760233600  # assume broken POSIX counting of seconds
        dla s w tests:
            self.assertEqual(iso2time(s), test_t, s)
            self.assertEqual(iso2time(s.lower()), test_t, s.lower())
            self.assertEqual(iso2time(s.upper()), test_t, s.upper())

    def test_iso2time_garbage(self):
        dla test w [
            '',
            'Garbage',
            'Thursday, 03-Feb-94 00:00:00 GMT',
            '1980-00-01',
            '1980-13-01',
            '1980-01-00',
            '1980-01-32',
            '1980-01-01 25:00:00',
            '1980-01-01 00:61:00',
            '01-01-1980 00:00:62',
            '01-01-1980T00:00:62',
            '19800101T250000Z'
            '1980-01-01 00:00:00 -2500',
            ]:
            self.assertIsNic(iso2time(test),
                              "iso2time(%s) jest nie Nic\n"
                              "iso2time(test) %s" % (test, iso2time(test)))


klasa HeaderTests(unittest.TestCase):

    def test_parse_ns_headers(self):
        # quotes should be stripped
        expected = [[('foo', 'bar'), ('expires', 2209069412), ('version', '0')]]
        dla hdr w [
            'foo=bar; expires=01 Jan 2040 22:23:32 GMT',
            'foo=bar; expires="01 Jan 2040 22:23:32 GMT"',
            ]:
            self.assertEqual(parse_ns_headers([hdr]), expected)

    def test_parse_ns_headers_version(self):

        # quotes should be stripped
        expected = [[('foo', 'bar'), ('version', '1')]]
        dla hdr w [
            'foo=bar; version="1"',
            'foo=bar; Version="1"',
            ]:
            self.assertEqual(parse_ns_headers([hdr]), expected)

    def test_parse_ns_headers_special_names(self):
        # names such jako 'expires' are nie special w first name=value pair
        # of Set-Cookie: header
        # Cookie przy name 'expires'
        hdr = 'expires=01 Jan 2040 22:23:32 GMT'
        expected = [[("expires", "01 Jan 2040 22:23:32 GMT"), ("version", "0")]]
        self.assertEqual(parse_ns_headers([hdr]), expected)

    def test_join_header_words(self):
        joined = join_header_words([[("foo", Nic), ("bar", "baz")]])
        self.assertEqual(joined, "foo; bar=baz")

        self.assertEqual(join_header_words([[]]), "")

    def test_split_header_words(self):
        tests = [
            ("foo", [[("foo", Nic)]]),
            ("foo=bar", [[("foo", "bar")]]),
            ("   foo   ", [[("foo", Nic)]]),
            ("   foo=   ", [[("foo", "")]]),
            ("   foo=", [[("foo", "")]]),
            ("   foo=   ; ", [[("foo", "")]]),
            ("   foo=   ; bar= baz ", [[("foo", ""), ("bar", "baz")]]),
            ("foo=bar bar=baz", [[("foo", "bar"), ("bar", "baz")]]),
            # doesn't really matter jeżeli this next fails, but it works ATM
            ("foo= bar=baz", [[("foo", "bar=baz")]]),
            ("foo=bar;bar=baz", [[("foo", "bar"), ("bar", "baz")]]),
            ('foo bar baz', [[("foo", Nic), ("bar", Nic), ("baz", Nic)]]),
            ("a, b, c", [[("a", Nic)], [("b", Nic)], [("c", Nic)]]),
            (r'foo; bar=baz, spam=, foo="\,\;\"", bar= ',
             [[("foo", Nic), ("bar", "baz")],
              [("spam", "")], [("foo", ',;"')], [("bar", "")]]),
            ]

        dla arg, expect w tests:
            spróbuj:
                result = split_header_words([arg])
            wyjąwszy:
                zaimportuj traceback, io
                f = io.StringIO()
                traceback.print_exc(Nic, f)
                result = "(error -- traceback follows)\n\n%s" % f.getvalue()
            self.assertEqual(result,  expect, """
When parsing: '%s'
Expected:     '%s'
Got:          '%s'
""" % (arg, expect, result))

    def test_roundtrip(self):
        tests = [
            ("foo", "foo"),
            ("foo=bar", "foo=bar"),
            ("   foo   ", "foo"),
            ("foo=", 'foo=""'),
            ("foo=bar bar=baz", "foo=bar; bar=baz"),
            ("foo=bar;bar=baz", "foo=bar; bar=baz"),
            ('foo bar baz', "foo; bar; baz"),
            (r'foo="\"" bar="\\"', r'foo="\""; bar="\\"'),
            ('foo,,,bar', 'foo, bar'),
            ('foo=bar,bar=baz', 'foo=bar, bar=baz'),

            ('text/html; charset=iso-8859-1',
             'text/html; charset="iso-8859-1"'),

            ('foo="bar"; port="80,81"; discard, bar=baz',
             'foo=bar; port="80,81"; discard, bar=baz'),

            (r'Basic realm="\"foo\\\\bar\""',
             r'Basic; realm="\"foo\\\\bar\""')
            ]

        dla arg, expect w tests:
            input = split_header_words([arg])
            res = join_header_words(input)
            self.assertEqual(res, expect, """
When parsing: '%s'
Expected:     '%s'
Got:          '%s'
Input was:    '%s'
""" % (arg, expect, res, input))


klasa FakeResponse:
    def __init__(self, headers=[], url=Nic):
        """
        headers: list of RFC822-style 'Key: value' strings
        """
        zaimportuj email
        self._headers = email.message_from_string("\n".join(headers))
        self._url = url
    def info(self): zwróć self._headers

def interact_2965(cookiejar, url, *set_cookie_hdrs):
    zwróć _interact(cookiejar, url, set_cookie_hdrs, "Set-Cookie2")

def interact_netscape(cookiejar, url, *set_cookie_hdrs):
    zwróć _interact(cookiejar, url, set_cookie_hdrs, "Set-Cookie")

def _interact(cookiejar, url, set_cookie_hdrs, hdr_name):
    """Perform a single request / response cycle, returning Cookie: header."""
    req = urllib.request.Request(url)
    cookiejar.add_cookie_header(req)
    cookie_hdr = req.get_header("Cookie", "")
    headers = []
    dla hdr w set_cookie_hdrs:
        headers.append("%s: %s" % (hdr_name, hdr))
    res = FakeResponse(headers, url)
    cookiejar.extract_cookies(res, req)
    zwróć cookie_hdr


klasa FileCookieJarTests(unittest.TestCase):
    def test_lwp_valueless_cookie(self):
        # cookies przy no value should be saved oraz loaded consistently
        filename = test.support.TESTFN
        c = LWPCookieJar()
        interact_netscape(c, "http://www.acme.com/", 'boo')
        self.assertEqual(c._cookies["www.acme.com"]["/"]["boo"].value, Nic)
        spróbuj:
            c.save(filename, ignore_discard=Prawda)
            c = LWPCookieJar()
            c.load(filename, ignore_discard=Prawda)
        w_końcu:
            spróbuj: os.unlink(filename)
            wyjąwszy OSError: dalej
        self.assertEqual(c._cookies["www.acme.com"]["/"]["boo"].value, Nic)

    def test_bad_magic(self):
        # OSErrors (eg. file doesn't exist) are allowed to propagate
        filename = test.support.TESTFN
        dla cookiejar_class w LWPCookieJar, MozillaCookieJar:
            c = cookiejar_class()
            spróbuj:
                c.load(filename="dla this test to work, a file przy this "
                                "filename should nie exist")
            wyjąwszy OSError jako exc:
                # an OSError subclass (likely FileNotFoundError), but nie
                # LoadError
                self.assertIsNot(exc.__class__, LoadError)
            inaczej:
                self.fail("expected OSError dla invalid filename")
        # Invalid contents of cookies file (eg. bad magic string)
        # causes a LoadError.
        spróbuj:
            przy open(filename, "w") jako f:
                f.write("oops\n")
                dla cookiejar_class w LWPCookieJar, MozillaCookieJar:
                    c = cookiejar_class()
                    self.assertRaises(LoadError, c.load, filename)
        w_końcu:
            spróbuj: os.unlink(filename)
            wyjąwszy OSError: dalej

klasa CookieTests(unittest.TestCase):
    # XXX
    # Get rid of string comparisons where nie actually testing str / repr.
    # .clear() etc.
    # IP addresses like 50 (single number, no dot) oraz domain-matching
    #  functions (and is_HDN)?  See draft RFC 2965 errata.
    # Strictness switches
    # is_third_party()
    # unverifiability / third-party blocking
    # Netscape cookies work the same jako RFC 2965 przy regard to port.
    # Set-Cookie przy negative max age.
    # If turn RFC 2965 handling off, Set-Cookie2 cookies should nie clobber
    #  Set-Cookie cookies.
    # Cookie2 should be sent jeżeli *any* cookies are nie V1 (ie. V0 OR V2 etc.).
    # Cookies (V1 oraz V0) przy no expiry date should be set to be discarded.
    # RFC 2965 Quoting:
    #  Should accept unquoted cookie-attribute values?  check errata draft.
    #   Which are required on the way w oraz out?
    #  Should always zwróć quoted cookie-attribute values?
    # Proper testing of when RFC 2965 clobbers Netscape (waiting dla errata).
    # Path-match on zwróć (same dla V0 oraz V1).
    # RFC 2965 acceptance oraz returning rules
    #  Set-Cookie2 without version attribute jest rejected.

    # Netscape peculiarities list z Ronald Tschalar.
    # The first two still need tests, the rest are covered.
## - Quoting: only quotes around the expires value are recognized jako such
##   (and yes, some folks quote the expires value); quotes around any other
##   value are treated jako part of the value.
## - White space: white space around names oraz values jest ignored
## - Default path: jeżeli no path parameter jest given, the path defaults to the
##   path w the request-uri up to, but nie including, the last '/'. Note
##   that this jest entirely different z what the spec says.
## - Commas oraz other delimiters: Netscape just parses until the next ';'.
##   This means it will allow commas etc inside values (and yes, both
##   commas oraz equals are commonly appear w the cookie value). This also
##   means that jeżeli you fold multiple Set-Cookie header fields into one,
##   comma-separated list, it'll be a headache to parse (at least my head
##   starts hurting every time I think of that code).
## - Expires: You'll get all sorts of date formats w the expires,
##   including emtpy expires attributes ("expires="). Be jako flexible jako you
##   can, oraz certainly don't expect the weekday to be there; jeżeli you can't
##   parse it, just ignore it oraz pretend it's a session cookie.
## - Domain-matching: Netscape uses the 2-dot rule dla _all_ domains, nie
##   just the 7 special TLD's listed w their spec. And folks rely on
##   that...

    def test_domain_return_ok(self):
        # test optimization: .domain_return_ok() should filter out most
        # domains w the CookieJar before we try to access them (because that
        # may require disk access -- w particular, przy MSIECookieJar)
        # This jest only a rough check dla performance reasons, so it's nie too
        # critical jako long jako it's sufficiently liberal.
        pol = DefaultCookiePolicy()
        dla url, domain, ok w [
            ("http://foo.bar.com/", "blah.com", Nieprawda),
            ("http://foo.bar.com/", "rhubarb.blah.com", Nieprawda),
            ("http://foo.bar.com/", "rhubarb.foo.bar.com", Nieprawda),
            ("http://foo.bar.com/", ".foo.bar.com", Prawda),
            ("http://foo.bar.com/", "foo.bar.com", Prawda),
            ("http://foo.bar.com/", ".bar.com", Prawda),
            ("http://foo.bar.com/", "com", Prawda),
            ("http://foo.com/", "rhubarb.foo.com", Nieprawda),
            ("http://foo.com/", ".foo.com", Prawda),
            ("http://foo.com/", "foo.com", Prawda),
            ("http://foo.com/", "com", Prawda),
            ("http://foo/", "rhubarb.foo", Nieprawda),
            ("http://foo/", ".foo", Prawda),
            ("http://foo/", "foo", Prawda),
            ("http://foo/", "foo.local", Prawda),
            ("http://foo/", ".local", Prawda),
            ]:
            request = urllib.request.Request(url)
            r = pol.domain_return_ok(domain, request)
            jeżeli ok: self.assertPrawda(r)
            inaczej: self.assertNieprawda(r)

    def test_missing_value(self):
        # missing = sign w Cookie: header jest regarded by Mozilla jako a missing
        # name, oraz by http.cookiejar jako a missing value
        filename = test.support.TESTFN
        c = MozillaCookieJar(filename)
        interact_netscape(c, "http://www.acme.com/", 'eggs')
        interact_netscape(c, "http://www.acme.com/", '"spam"; path=/foo/')
        cookie = c._cookies["www.acme.com"]["/"]["eggs"]
        self.assertIsNic(cookie.value)
        self.assertEqual(cookie.name, "eggs")
        cookie = c._cookies["www.acme.com"]['/foo/']['"spam"']
        self.assertIsNic(cookie.value)
        self.assertEqual(cookie.name, '"spam"')
        self.assertEqual(lwp_cookie_str(cookie), (
            r'"spam"; path="/foo/"; domain="www.acme.com"; '
            'path_spec; discard; version=0'))
        old_str = repr(c)
        c.save(ignore_expires=Prawda, ignore_discard=Prawda)
        spróbuj:
            c = MozillaCookieJar(filename)
            c.revert(ignore_expires=Prawda, ignore_discard=Prawda)
        w_końcu:
            os.unlink(c.filename)
        # cookies unchanged apart z lost info re. whether path was specified
        self.assertEqual(
            repr(c),
            re.sub("path_specified=%s" % Prawda, "path_specified=%s" % Nieprawda,
                   old_str)
            )
        self.assertEqual(interact_netscape(c, "http://www.acme.com/foo/"),
                         '"spam"; eggs')

    def test_rfc2109_handling(self):
        # RFC 2109 cookies are handled jako RFC 2965 albo Netscape cookies,
        # dependent on policy settings
        dla rfc2109_as_netscape, rfc2965, version w [
            # default according to rfc2965 jeżeli nie explicitly specified
            (Nic, Nieprawda, 0),
            (Nic, Prawda, 1),
            # explicit rfc2109_as_netscape
            (Nieprawda, Nieprawda, Nic),  # version Nic here means no cookie stored
            (Nieprawda, Prawda, 1),
            (Prawda, Nieprawda, 0),
            (Prawda, Prawda, 0),
            ]:
            policy = DefaultCookiePolicy(
                rfc2109_as_netscape=rfc2109_as_netscape,
                rfc2965=rfc2965)
            c = CookieJar(policy)
            interact_netscape(c, "http://www.example.com/", "ni=ni; Version=1")
            spróbuj:
                cookie = c._cookies["www.example.com"]["/"]["ni"]
            wyjąwszy KeyError:
                self.assertIsNic(version)  # didn't expect a stored cookie
            inaczej:
                self.assertEqual(cookie.version, version)
                # 2965 cookies are unaffected
                interact_2965(c, "http://www.example.com/",
                              "foo=bar; Version=1")
                jeżeli rfc2965:
                    cookie2965 = c._cookies["www.example.com"]["/"]["foo"]
                    self.assertEqual(cookie2965.version, 1)

    def test_ns_parser(self):
        c = CookieJar()
        interact_netscape(c, "http://www.acme.com/",
                          'spam=eggs; DoMain=.acme.com; port; blArgh="feep"')
        interact_netscape(c, "http://www.acme.com/", 'ni=ni; port=80,8080')
        interact_netscape(c, "http://www.acme.com:80/", 'nini=ni')
        interact_netscape(c, "http://www.acme.com:80/", 'foo=bar; expires=')
        interact_netscape(c, "http://www.acme.com:80/", 'spam=eggs; '
                          'expires="Foo Bar 25 33:22:11 3022"')
        interact_netscape(c, 'http://www.acme.com/', 'fortytwo=')
        interact_netscape(c, 'http://www.acme.com/', '=unladenswallow')
        interact_netscape(c, 'http://www.acme.com/', 'holyhandgrenade')

        cookie = c._cookies[".acme.com"]["/"]["spam"]
        self.assertEqual(cookie.domain, ".acme.com")
        self.assertPrawda(cookie.domain_specified)
        self.assertEqual(cookie.port, DEFAULT_HTTP_PORT)
        self.assertNieprawda(cookie.port_specified)
        # case jest preserved
        self.assertPrawda(cookie.has_nonstandard_attr("blArgh"))
        self.assertNieprawda(cookie.has_nonstandard_attr("blargh"))

        cookie = c._cookies["www.acme.com"]["/"]["ni"]
        self.assertEqual(cookie.domain, "www.acme.com")
        self.assertNieprawda(cookie.domain_specified)
        self.assertEqual(cookie.port, "80,8080")
        self.assertPrawda(cookie.port_specified)

        cookie = c._cookies["www.acme.com"]["/"]["nini"]
        self.assertIsNic(cookie.port)
        self.assertNieprawda(cookie.port_specified)

        # invalid expires should nie cause cookie to be dropped
        foo = c._cookies["www.acme.com"]["/"]["foo"]
        spam = c._cookies["www.acme.com"]["/"]["foo"]
        self.assertIsNic(foo.expires)
        self.assertIsNic(spam.expires)

        cookie = c._cookies['www.acme.com']['/']['fortytwo']
        self.assertIsNotNic(cookie.value)
        self.assertEqual(cookie.value, '')

        # there should be a distinction between a present but empty value
        # (above) oraz a value that's entirely missing (below)

        cookie = c._cookies['www.acme.com']['/']['holyhandgrenade']
        self.assertIsNic(cookie.value)

    def test_ns_parser_special_names(self):
        # names such jako 'expires' are nie special w first name=value pair
        # of Set-Cookie: header
        c = CookieJar()
        interact_netscape(c, "http://www.acme.com/", 'expires=eggs')
        interact_netscape(c, "http://www.acme.com/", 'version=eggs; spam=eggs')

        cookies = c._cookies["www.acme.com"]["/"]
        self.assertIn('expires', cookies)
        self.assertIn('version', cookies)

    def test_expires(self):
        # jeżeli expires jest w future, keep cookie...
        c = CookieJar()
        future = time2netscape(time.time()+3600)
        interact_netscape(c, "http://www.acme.com/", 'spam="bar"; expires=%s' %
                          future)
        self.assertEqual(len(c), 1)
        now = time2netscape(time.time()-1)
        # ... oraz jeżeli w past albo present, discard it
        interact_netscape(c, "http://www.acme.com/", 'foo="eggs"; expires=%s' %
                          now)
        h = interact_netscape(c, "http://www.acme.com/")
        self.assertEqual(len(c), 1)
        self.assertIn('spam="bar"', h)
        self.assertNotIn("foo", h)

        # max-age takes precedence over expires, oraz zero max-age jest request to
        # delete both new cookie oraz any old matching cookie
        interact_netscape(c, "http://www.acme.com/", 'eggs="bar"; expires=%s' %
                          future)
        interact_netscape(c, "http://www.acme.com/", 'bar="bar"; expires=%s' %
                          future)
        self.assertEqual(len(c), 3)
        interact_netscape(c, "http://www.acme.com/", 'eggs="bar"; '
                          'expires=%s; max-age=0' % future)
        interact_netscape(c, "http://www.acme.com/", 'bar="bar"; '
                          'max-age=0; expires=%s' % future)
        h = interact_netscape(c, "http://www.acme.com/")
        self.assertEqual(len(c), 1)

        # test expiry at end of session dla cookies przy no expires attribute
        interact_netscape(c, "http://www.rhubarb.net/", 'whum="fizz"')
        self.assertEqual(len(c), 2)
        c.clear_session_cookies()
        self.assertEqual(len(c), 1)
        self.assertIn('spam="bar"', h)

        # test jeżeli fractional expiry jest accepted
        cookie  = Cookie(0, "name", "value",
                         Nic, Nieprawda, "www.python.org",
                         Prawda, Nieprawda, "/",
                         Nieprawda, Nieprawda, "1444312383.018307",
                         Nieprawda, Nic, Nic,
                         {})
        self.assertEqual(cookie.expires, 1444312383)

        # XXX RFC 2965 expiry rules (some apply to V0 too)

    def test_default_path(self):
        # RFC 2965
        pol = DefaultCookiePolicy(rfc2965=Prawda)

        c = CookieJar(pol)
        interact_2965(c, "http://www.acme.com/", 'spam="bar"; Version="1"')
        self.assertIn("/", c._cookies["www.acme.com"])

        c = CookieJar(pol)
        interact_2965(c, "http://www.acme.com/blah", 'eggs="bar"; Version="1"')
        self.assertIn("/", c._cookies["www.acme.com"])

        c = CookieJar(pol)
        interact_2965(c, "http://www.acme.com/blah/rhubarb",
                      'eggs="bar"; Version="1"')
        self.assertIn("/blah/", c._cookies["www.acme.com"])

        c = CookieJar(pol)
        interact_2965(c, "http://www.acme.com/blah/rhubarb/",
                      'eggs="bar"; Version="1"')
        self.assertIn("/blah/rhubarb/", c._cookies["www.acme.com"])

        # Netscape

        c = CookieJar()
        interact_netscape(c, "http://www.acme.com/", 'spam="bar"')
        self.assertIn("/", c._cookies["www.acme.com"])

        c = CookieJar()
        interact_netscape(c, "http://www.acme.com/blah", 'eggs="bar"')
        self.assertIn("/", c._cookies["www.acme.com"])

        c = CookieJar()
        interact_netscape(c, "http://www.acme.com/blah/rhubarb", 'eggs="bar"')
        self.assertIn("/blah", c._cookies["www.acme.com"])

        c = CookieJar()
        interact_netscape(c, "http://www.acme.com/blah/rhubarb/", 'eggs="bar"')
        self.assertIn("/blah/rhubarb", c._cookies["www.acme.com"])

    def test_default_path_with_query(self):
        cj = CookieJar()
        uri = "http://example.com/?spam/eggs"
        value = 'eggs="bar"'
        interact_netscape(cj, uri, value)
        # Default path does nie include query, so jest "/", nie "/?spam".
        self.assertIn("/", cj._cookies["example.com"])
        # Cookie jest sent back to the same URI.
        self.assertEqual(interact_netscape(cj, uri), value)

    def test_escape_path(self):
        cases = [
            # quoted safe
            ("/foo%2f/bar", "/foo%2F/bar"),
            ("/foo%2F/bar", "/foo%2F/bar"),
            # quoted %
            ("/foo%%/bar", "/foo%%/bar"),
            # quoted unsafe
            ("/fo%19o/bar", "/fo%19o/bar"),
            ("/fo%7do/bar", "/fo%7Do/bar"),
            # unquoted safe
            ("/foo/bar&", "/foo/bar&"),
            ("/foo//bar", "/foo//bar"),
            ("\176/foo/bar", "\176/foo/bar"),
            # unquoted unsafe
            ("/foo\031/bar", "/foo%19/bar"),
            ("/\175foo/bar", "/%7Dfoo/bar"),
            # unicode, latin-1 range
            ("/foo/bar\u00fc", "/foo/bar%C3%BC"),     # UTF-8 encoded
            # unicode
            ("/foo/bar\uabcd", "/foo/bar%EA%AF%8D"),  # UTF-8 encoded
            ]
        dla arg, result w cases:
            self.assertEqual(escape_path(arg), result)

    def test_request_path(self):
        # przy parameters
        req = urllib.request.Request(
            "http://www.example.com/rheum/rhaponticum;"
            "foo=bar;sing=song?apples=pears&spam=eggs#ni")
        self.assertEqual(request_path(req),
                         "/rheum/rhaponticum;foo=bar;sing=song")
        # without parameters
        req = urllib.request.Request(
            "http://www.example.com/rheum/rhaponticum?"
            "apples=pears&spam=eggs#ni")
        self.assertEqual(request_path(req), "/rheum/rhaponticum")
        # missing final slash
        req = urllib.request.Request("http://www.example.com")
        self.assertEqual(request_path(req), "/")

    def test_request_port(self):
        req = urllib.request.Request("http://www.acme.com:1234/",
                                     headers={"Host": "www.acme.com:4321"})
        self.assertEqual(request_port(req), "1234")
        req = urllib.request.Request("http://www.acme.com/",
                                     headers={"Host": "www.acme.com:4321"})
        self.assertEqual(request_port(req), DEFAULT_HTTP_PORT)

    def test_request_host(self):
        # this request jest illegal (RFC2616, 14.2.3)
        req = urllib.request.Request("http://1.1.1.1/",
                                     headers={"Host": "www.acme.com:80"})
        # libwww-perl wants this response, but that seems wrong (RFC 2616,
        # section 5.2, point 1., oraz RFC 2965 section 1, paragraph 3)
        #self.assertEqual(request_host(req), "www.acme.com")
        self.assertEqual(request_host(req), "1.1.1.1")
        req = urllib.request.Request("http://www.acme.com/",
                                     headers={"Host": "irrelevant.com"})
        self.assertEqual(request_host(req), "www.acme.com")
        # port shouldn't be w request-host
        req = urllib.request.Request("http://www.acme.com:2345/resource.html",
                                     headers={"Host": "www.acme.com:5432"})
        self.assertEqual(request_host(req), "www.acme.com")

    def test_is_HDN(self):
        self.assertPrawda(is_HDN("foo.bar.com"))
        self.assertPrawda(is_HDN("1foo2.3bar4.5com"))
        self.assertNieprawda(is_HDN("192.168.1.1"))
        self.assertNieprawda(is_HDN(""))
        self.assertNieprawda(is_HDN("."))
        self.assertNieprawda(is_HDN(".foo.bar.com"))
        self.assertNieprawda(is_HDN("..foo"))
        self.assertNieprawda(is_HDN("foo."))

    def test_reach(self):
        self.assertEqual(reach("www.acme.com"), ".acme.com")
        self.assertEqual(reach("acme.com"), "acme.com")
        self.assertEqual(reach("acme.local"), ".local")
        self.assertEqual(reach(".local"), ".local")
        self.assertEqual(reach(".com"), ".com")
        self.assertEqual(reach("."), ".")
        self.assertEqual(reach(""), "")
        self.assertEqual(reach("192.168.0.1"), "192.168.0.1")

    def test_domain_match(self):
        self.assertPrawda(domain_match("192.168.1.1", "192.168.1.1"))
        self.assertNieprawda(domain_match("192.168.1.1", ".168.1.1"))
        self.assertPrawda(domain_match("x.y.com", "x.Y.com"))
        self.assertPrawda(domain_match("x.y.com", ".Y.com"))
        self.assertNieprawda(domain_match("x.y.com", "Y.com"))
        self.assertPrawda(domain_match("a.b.c.com", ".c.com"))
        self.assertNieprawda(domain_match(".c.com", "a.b.c.com"))
        self.assertPrawda(domain_match("example.local", ".local"))
        self.assertNieprawda(domain_match("blah.blah", ""))
        self.assertNieprawda(domain_match("", ".rhubarb.rhubarb"))
        self.assertPrawda(domain_match("", ""))

        self.assertPrawda(user_domain_match("acme.com", "acme.com"))
        self.assertNieprawda(user_domain_match("acme.com", ".acme.com"))
        self.assertPrawda(user_domain_match("rhubarb.acme.com", ".acme.com"))
        self.assertPrawda(user_domain_match("www.rhubarb.acme.com", ".acme.com"))
        self.assertPrawda(user_domain_match("x.y.com", "x.Y.com"))
        self.assertPrawda(user_domain_match("x.y.com", ".Y.com"))
        self.assertNieprawda(user_domain_match("x.y.com", "Y.com"))
        self.assertPrawda(user_domain_match("y.com", "Y.com"))
        self.assertNieprawda(user_domain_match(".y.com", "Y.com"))
        self.assertPrawda(user_domain_match(".y.com", ".Y.com"))
        self.assertPrawda(user_domain_match("x.y.com", ".com"))
        self.assertNieprawda(user_domain_match("x.y.com", "com"))
        self.assertNieprawda(user_domain_match("x.y.com", "m"))
        self.assertNieprawda(user_domain_match("x.y.com", ".m"))
        self.assertNieprawda(user_domain_match("x.y.com", ""))
        self.assertNieprawda(user_domain_match("x.y.com", "."))
        self.assertPrawda(user_domain_match("192.168.1.1", "192.168.1.1"))
        # nie both HDNs, so must string-compare equal to match
        self.assertNieprawda(user_domain_match("192.168.1.1", ".168.1.1"))
        self.assertNieprawda(user_domain_match("192.168.1.1", "."))
        # empty string jest a special case
        self.assertNieprawda(user_domain_match("192.168.1.1", ""))

    def test_wrong_domain(self):
        # Cookies whose effective request-host name does nie domain-match the
        # domain are rejected.

        # XXX far z complete
        c = CookieJar()
        interact_2965(c, "http://www.nasty.com/",
                      'foo=bar; domain=friendly.org; Version="1"')
        self.assertEqual(len(c), 0)

    def test_strict_domain(self):
        # Cookies whose domain jest a country-code tld like .co.uk should
        # nie be set jeżeli CookiePolicy.strict_domain jest true.
        cp = DefaultCookiePolicy(strict_domain=Prawda)
        cj = CookieJar(policy=cp)
        interact_netscape(cj, "http://example.co.uk/", 'no=problemo')
        interact_netscape(cj, "http://example.co.uk/",
                          'okey=dokey; Domain=.example.co.uk')
        self.assertEqual(len(cj), 2)
        dla pseudo_tld w [".co.uk", ".org.za", ".tx.us", ".name.us"]:
            interact_netscape(cj, "http://example.%s/" % pseudo_tld,
                              'spam=eggs; Domain=.co.uk')
            self.assertEqual(len(cj), 2)

    def test_two_component_domain_ns(self):
        # Netscape: .www.bar.com, www.bar.com, .bar.com, bar.com, no domain
        # should all get accepted, jako should .acme.com, acme.com oraz no domain
        # dla 2-component domains like acme.com.
        c = CookieJar()

        # two-component V0 domain jest OK
        interact_netscape(c, "http://foo.net/", 'ns=bar')
        self.assertEqual(len(c), 1)
        self.assertEqual(c._cookies["foo.net"]["/"]["ns"].value, "bar")
        self.assertEqual(interact_netscape(c, "http://foo.net/"), "ns=bar")
        # *will* be returned to any other domain (unlike RFC 2965)...
        self.assertEqual(interact_netscape(c, "http://www.foo.net/"),
                         "ns=bar")
        # ...unless requested otherwise
        pol = DefaultCookiePolicy(
            strict_ns_domain=DefaultCookiePolicy.DomainStrictNonDomain)
        c.set_policy(pol)
        self.assertEqual(interact_netscape(c, "http://www.foo.net/"), "")

        # unlike RFC 2965, even explicit two-component domain jest OK,
        # because .foo.net matches foo.net
        interact_netscape(c, "http://foo.net/foo/",
                          'spam1=eggs; domain=foo.net')
        # even jeżeli starts przy a dot -- w NS rules, .foo.net matches foo.net!
        interact_netscape(c, "http://foo.net/foo/bar/",
                          'spam2=eggs; domain=.foo.net')
        self.assertEqual(len(c), 3)
        self.assertEqual(c._cookies[".foo.net"]["/foo"]["spam1"].value,
                         "eggs")
        self.assertEqual(c._cookies[".foo.net"]["/foo/bar"]["spam2"].value,
                         "eggs")
        self.assertEqual(interact_netscape(c, "http://foo.net/foo/bar/"),
                         "spam2=eggs; spam1=eggs; ns=bar")

        # top-level domain jest too general
        interact_netscape(c, "http://foo.net/", 'nini="ni"; domain=.net')
        self.assertEqual(len(c), 3)

##         # Netscape protocol doesn't allow non-special top level domains (such
##         # jako co.uk) w the domain attribute unless there are at least three
##         # dots w it.
        # Oh yes it does!  Real implementations don't check this, oraz real
        # cookies (of course) rely on that behaviour.
        interact_netscape(c, "http://foo.co.uk", 'nasty=trick; domain=.co.uk')
##         self.assertEqual(len(c), 2)
        self.assertEqual(len(c), 4)

    def test_two_component_domain_rfc2965(self):
        pol = DefaultCookiePolicy(rfc2965=Prawda)
        c = CookieJar(pol)

        # two-component V1 domain jest OK
        interact_2965(c, "http://foo.net/", 'foo=bar; Version="1"')
        self.assertEqual(len(c), 1)
        self.assertEqual(c._cookies["foo.net"]["/"]["foo"].value, "bar")
        self.assertEqual(interact_2965(c, "http://foo.net/"),
                         "$Version=1; foo=bar")
        # won't be returned to any other domain (because domain was implied)
        self.assertEqual(interact_2965(c, "http://www.foo.net/"), "")

        # unless domain jest given explicitly, because then it must be
        # rewritten to start przy a dot: foo.net --> .foo.net, which does
        # nie domain-match foo.net
        interact_2965(c, "http://foo.net/foo",
                      'spam=eggs; domain=foo.net; path=/foo; Version="1"')
        self.assertEqual(len(c), 1)
        self.assertEqual(interact_2965(c, "http://foo.net/foo"),
                         "$Version=1; foo=bar")

        # explicit foo.net z three-component domain www.foo.net *does* get
        # set, because .foo.net domain-matches .foo.net
        interact_2965(c, "http://www.foo.net/foo/",
                      'spam=eggs; domain=foo.net; Version="1"')
        self.assertEqual(c._cookies[".foo.net"]["/foo/"]["spam"].value,
                         "eggs")
        self.assertEqual(len(c), 2)
        self.assertEqual(interact_2965(c, "http://foo.net/foo/"),
                         "$Version=1; foo=bar")
        self.assertEqual(interact_2965(c, "http://www.foo.net/foo/"),
                         '$Version=1; spam=eggs; $Domain="foo.net"')

        # top-level domain jest too general
        interact_2965(c, "http://foo.net/",
                      'ni="ni"; domain=".net"; Version="1"')
        self.assertEqual(len(c), 2)

        # RFC 2965 doesn't require blocking this
        interact_2965(c, "http://foo.co.uk/",
                      'nasty=trick; domain=.co.uk; Version="1"')
        self.assertEqual(len(c), 3)

    def test_domain_allow(self):
        c = CookieJar(policy=DefaultCookiePolicy(
            blocked_domains=["acme.com"],
            allowed_domains=["www.acme.com"]))

        req = urllib.request.Request("http://acme.com/")
        headers = ["Set-Cookie: CUSTOMER=WILE_E_COYOTE; path=/"]
        res = FakeResponse(headers, "http://acme.com/")
        c.extract_cookies(res, req)
        self.assertEqual(len(c), 0)

        req = urllib.request.Request("http://www.acme.com/")
        res = FakeResponse(headers, "http://www.acme.com/")
        c.extract_cookies(res, req)
        self.assertEqual(len(c), 1)

        req = urllib.request.Request("http://www.coyote.com/")
        res = FakeResponse(headers, "http://www.coyote.com/")
        c.extract_cookies(res, req)
        self.assertEqual(len(c), 1)

        # set a cookie przy non-allowed domain...
        req = urllib.request.Request("http://www.coyote.com/")
        res = FakeResponse(headers, "http://www.coyote.com/")
        cookies = c.make_cookies(res, req)
        c.set_cookie(cookies[0])
        self.assertEqual(len(c), 2)
        # ... oraz check jest doesn't get returned
        c.add_cookie_header(req)
        self.assertNieprawda(req.has_header("Cookie"))

    def test_domain_block(self):
        pol = DefaultCookiePolicy(
            rfc2965=Prawda, blocked_domains=[".acme.com"])
        c = CookieJar(policy=pol)
        headers = ["Set-Cookie: CUSTOMER=WILE_E_COYOTE; path=/"]

        req = urllib.request.Request("http://www.acme.com/")
        res = FakeResponse(headers, "http://www.acme.com/")
        c.extract_cookies(res, req)
        self.assertEqual(len(c), 0)

        p = pol.set_blocked_domains(["acme.com"])
        c.extract_cookies(res, req)
        self.assertEqual(len(c), 1)

        c.clear()
        req = urllib.request.Request("http://www.roadrunner.net/")
        res = FakeResponse(headers, "http://www.roadrunner.net/")
        c.extract_cookies(res, req)
        self.assertEqual(len(c), 1)
        req = urllib.request.Request("http://www.roadrunner.net/")
        c.add_cookie_header(req)
        self.assertPrawda(req.has_header("Cookie"))
        self.assertPrawda(req.has_header("Cookie2"))

        c.clear()
        pol.set_blocked_domains([".acme.com"])
        c.extract_cookies(res, req)
        self.assertEqual(len(c), 1)

        # set a cookie przy blocked domain...
        req = urllib.request.Request("http://www.acme.com/")
        res = FakeResponse(headers, "http://www.acme.com/")
        cookies = c.make_cookies(res, req)
        c.set_cookie(cookies[0])
        self.assertEqual(len(c), 2)
        # ... oraz check jest doesn't get returned
        c.add_cookie_header(req)
        self.assertNieprawda(req.has_header("Cookie"))

    def test_secure(self):
        dla ns w Prawda, Nieprawda:
            dla whitespace w " ", "":
                c = CookieJar()
                jeżeli ns:
                    pol = DefaultCookiePolicy(rfc2965=Nieprawda)
                    int = interact_netscape
                    vs = ""
                inaczej:
                    pol = DefaultCookiePolicy(rfc2965=Prawda)
                    int = interact_2965
                    vs = "; Version=1"
                c.set_policy(pol)
                url = "http://www.acme.com/"
                int(c, url, "foo1=bar%s%s" % (vs, whitespace))
                int(c, url, "foo2=bar%s; secure%s" %  (vs, whitespace))
                self.assertNieprawda(
                    c._cookies["www.acme.com"]["/"]["foo1"].secure,
                    "non-secure cookie registered secure")
                self.assertPrawda(
                    c._cookies["www.acme.com"]["/"]["foo2"].secure,
                    "secure cookie registered non-secure")

    def test_quote_cookie_value(self):
        c = CookieJar(policy=DefaultCookiePolicy(rfc2965=Prawda))
        interact_2965(c, "http://www.acme.com/", r'foo=\b"a"r; Version=1')
        h = interact_2965(c, "http://www.acme.com/")
        self.assertEqual(h, r'$Version=1; foo=\\b\"a\"r')

    def test_missing_final_slash(self):
        # Missing slash z request URL's abs_path should be assumed present.
        url = "http://www.acme.com"
        c = CookieJar(DefaultCookiePolicy(rfc2965=Prawda))
        interact_2965(c, url, "foo=bar; Version=1")
        req = urllib.request.Request(url)
        self.assertEqual(len(c), 1)
        c.add_cookie_header(req)
        self.assertPrawda(req.has_header("Cookie"))

    def test_domain_mirror(self):
        pol = DefaultCookiePolicy(rfc2965=Prawda)

        c = CookieJar(pol)
        url = "http://foo.bar.com/"
        interact_2965(c, url, "spam=eggs; Version=1")
        h = interact_2965(c, url)
        self.assertNotIn("Domain", h,
                     "absent domain returned przy domain present")

        c = CookieJar(pol)
        url = "http://foo.bar.com/"
        interact_2965(c, url, 'spam=eggs; Version=1; Domain=.bar.com')
        h = interact_2965(c, url)
        self.assertIn('$Domain=".bar.com"', h, "domain nie returned")

        c = CookieJar(pol)
        url = "http://foo.bar.com/"
        # note missing initial dot w Domain
        interact_2965(c, url, 'spam=eggs; Version=1; Domain=bar.com')
        h = interact_2965(c, url)
        self.assertIn('$Domain="bar.com"', h, "domain nie returned")

    def test_path_mirror(self):
        pol = DefaultCookiePolicy(rfc2965=Prawda)

        c = CookieJar(pol)
        url = "http://foo.bar.com/"
        interact_2965(c, url, "spam=eggs; Version=1")
        h = interact_2965(c, url)
        self.assertNotIn("Path", h, "absent path returned przy path present")

        c = CookieJar(pol)
        url = "http://foo.bar.com/"
        interact_2965(c, url, 'spam=eggs; Version=1; Path=/')
        h = interact_2965(c, url)
        self.assertIn('$Path="/"', h, "path nie returned")

    def test_port_mirror(self):
        pol = DefaultCookiePolicy(rfc2965=Prawda)

        c = CookieJar(pol)
        url = "http://foo.bar.com/"
        interact_2965(c, url, "spam=eggs; Version=1")
        h = interact_2965(c, url)
        self.assertNotIn("Port", h, "absent port returned przy port present")

        c = CookieJar(pol)
        url = "http://foo.bar.com/"
        interact_2965(c, url, "spam=eggs; Version=1; Port")
        h = interact_2965(c, url)
        self.assertRegex(h, "\$Port([^=]|$)",
                         "port przy no value nie returned przy no value")

        c = CookieJar(pol)
        url = "http://foo.bar.com/"
        interact_2965(c, url, 'spam=eggs; Version=1; Port="80"')
        h = interact_2965(c, url)
        self.assertIn('$Port="80"', h,
                      "port przy single value nie returned przy single value")

        c = CookieJar(pol)
        url = "http://foo.bar.com/"
        interact_2965(c, url, 'spam=eggs; Version=1; Port="80,8080"')
        h = interact_2965(c, url)
        self.assertIn('$Port="80,8080"', h,
                      "port przy multiple values nie returned przy multiple "
                      "values")

    def test_no_return_comment(self):
        c = CookieJar(DefaultCookiePolicy(rfc2965=Prawda))
        url = "http://foo.bar.com/"
        interact_2965(c, url, 'spam=eggs; Version=1; '
                      'Comment="does anybody read these?"; '
                      'CommentURL="http://foo.bar.net/comment.html"')
        h = interact_2965(c, url)
        self.assertNotIn("Comment", h,
            "Comment albo CommentURL cookie-attributes returned to server")

    def test_Cookie_iterator(self):
        cs = CookieJar(DefaultCookiePolicy(rfc2965=Prawda))
        # add some random cookies
        interact_2965(cs, "http://blah.spam.org/", 'foo=eggs; Version=1; '
                      'Comment="does anybody read these?"; '
                      'CommentURL="http://foo.bar.net/comment.html"')
        interact_netscape(cs, "http://www.acme.com/blah/", "spam=bar; secure")
        interact_2965(cs, "http://www.acme.com/blah/",
                      "foo=bar; secure; Version=1")
        interact_2965(cs, "http://www.acme.com/blah/",
                      "foo=bar; path=/; Version=1")
        interact_2965(cs, "http://www.sol.no",
                      r'bang=wallop; version=1; domain=".sol.no"; '
                      r'port="90,100, 80,8080"; '
                      r'max-age=100; Comment = "Just kidding! (\"|\\\\) "')

        versions = [1, 1, 1, 0, 1]
        names = ["bang", "foo", "foo", "spam", "foo"]
        domains = [".sol.no", "blah.spam.org", "www.acme.com",
                   "www.acme.com", "www.acme.com"]
        paths = ["/", "/", "/", "/blah", "/blah/"]

        dla i w range(4):
            i = 0
            dla c w cs:
                self.assertIsInstance(c, Cookie)
                self.assertEqual(c.version, versions[i])
                self.assertEqual(c.name, names[i])
                self.assertEqual(c.domain, domains[i])
                self.assertEqual(c.path, paths[i])
                i = i + 1

    def test_parse_ns_headers(self):
        # missing domain value (invalid cookie)
        self.assertEqual(
            parse_ns_headers(["foo=bar; path=/; domain"]),
            [[("foo", "bar"),
              ("path", "/"), ("domain", Nic), ("version", "0")]]
            )
        # invalid expires value
        self.assertEqual(
            parse_ns_headers(["foo=bar; expires=Foo Bar 12 33:22:11 2000"]),
            [[("foo", "bar"), ("expires", Nic), ("version", "0")]]
            )
        # missing cookie value (valid cookie)
        self.assertEqual(
            parse_ns_headers(["foo"]),
            [[("foo", Nic), ("version", "0")]]
            )
        # missing cookie values dla parsed attributes
        self.assertEqual(
            parse_ns_headers(['foo=bar; expires']),
            [[('foo', 'bar'), ('expires', Nic), ('version', '0')]])
        self.assertEqual(
            parse_ns_headers(['foo=bar; version']),
            [[('foo', 'bar'), ('version', Nic)]])
        # shouldn't add version jeżeli header jest empty
        self.assertEqual(parse_ns_headers([""]), [])

    def test_bad_cookie_header(self):

        def cookiejar_from_cookie_headers(headers):
            c = CookieJar()
            req = urllib.request.Request("http://www.example.com/")
            r = FakeResponse(headers, "http://www.example.com/")
            c.extract_cookies(r, req)
            zwróć c

        future = time2netscape(time.time()+3600)

        # none of these bad headers should cause an exception to be podnieśd
        dla headers w [
            ["Set-Cookie: "],  # actually, nothing wrong przy this
            ["Set-Cookie2: "],  # ditto
            # missing domain value
            ["Set-Cookie2: a=foo; path=/; Version=1; domain"],
            # bad max-age
            ["Set-Cookie: b=foo; max-age=oops"],
            # bad version
            ["Set-Cookie: b=foo; version=spam"],
            ["Set-Cookie:; Expires=%s" % future],
            ]:
            c = cookiejar_from_cookie_headers(headers)
            # these bad cookies shouldn't be set
            self.assertEqual(len(c), 0)

        # cookie przy invalid expires jest treated jako session cookie
        headers = ["Set-Cookie: c=foo; expires=Foo Bar 12 33:22:11 2000"]
        c = cookiejar_from_cookie_headers(headers)
        cookie = c._cookies["www.example.com"]["/"]["c"]
        self.assertIsNic(cookie.expires)


klasa LWPCookieTests(unittest.TestCase):
    # Tests taken z libwww-perl, przy a few modifications oraz additions.

    def test_netscape_example_1(self):
        #-------------------------------------------------------------------
        # First we check that it works dla the original example at
        # http://www.netscape.com/newsref/std/cookie_spec.html

        # Client requests a document, oraz receives w the response:
        #
        #       Set-Cookie: CUSTOMER=WILE_E_COYOTE; path=/; expires=Wednesday, 09-Nov-99 23:12:40 GMT
        #
        # When client requests a URL w path "/" on this server, it sends:
        #
        #       Cookie: CUSTOMER=WILE_E_COYOTE
        #
        # Client requests a document, oraz receives w the response:
        #
        #       Set-Cookie: PART_NUMBER=ROCKET_LAUNCHER_0001; path=/
        #
        # When client requests a URL w path "/" on this server, it sends:
        #
        #       Cookie: CUSTOMER=WILE_E_COYOTE; PART_NUMBER=ROCKET_LAUNCHER_0001
        #
        # Client receives:
        #
        #       Set-Cookie: SHIPPING=FEDEX; path=/fo
        #
        # When client requests a URL w path "/" on this server, it sends:
        #
        #       Cookie: CUSTOMER=WILE_E_COYOTE; PART_NUMBER=ROCKET_LAUNCHER_0001
        #
        # When client requests a URL w path "/foo" on this server, it sends:
        #
        #       Cookie: CUSTOMER=WILE_E_COYOTE; PART_NUMBER=ROCKET_LAUNCHER_0001; SHIPPING=FEDEX
        #
        # The last Cookie jest buggy, because both specifications say that the
        # most specific cookie must be sent first.  SHIPPING=FEDEX jest the
        # most specific oraz should thus be first.

        year_plus_one = time.localtime()[0] + 1

        headers = []

        c = CookieJar(DefaultCookiePolicy(rfc2965 = Prawda))

        #req = urllib.request.Request("http://1.1.1.1/",
        #              headers={"Host": "www.acme.com:80"})
        req = urllib.request.Request("http://www.acme.com:80/",
                      headers={"Host": "www.acme.com:80"})

        headers.append(
            "Set-Cookie: CUSTOMER=WILE_E_COYOTE; path=/ ; "
            "expires=Wednesday, 09-Nov-%d 23:12:40 GMT" % year_plus_one)
        res = FakeResponse(headers, "http://www.acme.com/")
        c.extract_cookies(res, req)

        req = urllib.request.Request("http://www.acme.com/")
        c.add_cookie_header(req)

        self.assertEqual(req.get_header("Cookie"), "CUSTOMER=WILE_E_COYOTE")
        self.assertEqual(req.get_header("Cookie2"), '$Version="1"')

        headers.append("Set-Cookie: PART_NUMBER=ROCKET_LAUNCHER_0001; path=/")
        res = FakeResponse(headers, "http://www.acme.com/")
        c.extract_cookies(res, req)

        req = urllib.request.Request("http://www.acme.com/foo/bar")
        c.add_cookie_header(req)

        h = req.get_header("Cookie")
        self.assertIn("PART_NUMBER=ROCKET_LAUNCHER_0001", h)
        self.assertIn("CUSTOMER=WILE_E_COYOTE", h)

        headers.append('Set-Cookie: SHIPPING=FEDEX; path=/foo')
        res = FakeResponse(headers, "http://www.acme.com")
        c.extract_cookies(res, req)

        req = urllib.request.Request("http://www.acme.com/")
        c.add_cookie_header(req)

        h = req.get_header("Cookie")
        self.assertIn("PART_NUMBER=ROCKET_LAUNCHER_0001", h)
        self.assertIn("CUSTOMER=WILE_E_COYOTE", h)
        self.assertNotIn("SHIPPING=FEDEX", h)

        req = urllib.request.Request("http://www.acme.com/foo/")
        c.add_cookie_header(req)

        h = req.get_header("Cookie")
        self.assertIn("PART_NUMBER=ROCKET_LAUNCHER_0001", h)
        self.assertIn("CUSTOMER=WILE_E_COYOTE", h)
        self.assertPrawda(h.startswith("SHIPPING=FEDEX;"))

    def test_netscape_example_2(self):
        # Second Example transaction sequence:
        #
        # Assume all mappings z above have been cleared.
        #
        # Client receives:
        #
        #       Set-Cookie: PART_NUMBER=ROCKET_LAUNCHER_0001; path=/
        #
        # When client requests a URL w path "/" on this server, it sends:
        #
        #       Cookie: PART_NUMBER=ROCKET_LAUNCHER_0001
        #
        # Client receives:
        #
        #       Set-Cookie: PART_NUMBER=RIDING_ROCKET_0023; path=/ammo
        #
        # When client requests a URL w path "/ammo" on this server, it sends:
        #
        #       Cookie: PART_NUMBER=RIDING_ROCKET_0023; PART_NUMBER=ROCKET_LAUNCHER_0001
        #
        #       NOTE: There are two name/value pairs named "PART_NUMBER" due to
        #       the inheritance of the "/" mapping w addition to the "/ammo" mapping.

        c = CookieJar()
        headers = []

        req = urllib.request.Request("http://www.acme.com/")
        headers.append("Set-Cookie: PART_NUMBER=ROCKET_LAUNCHER_0001; path=/")
        res = FakeResponse(headers, "http://www.acme.com/")

        c.extract_cookies(res, req)

        req = urllib.request.Request("http://www.acme.com/")
        c.add_cookie_header(req)

        self.assertEqual(req.get_header("Cookie"),
                         "PART_NUMBER=ROCKET_LAUNCHER_0001")

        headers.append(
            "Set-Cookie: PART_NUMBER=RIDING_ROCKET_0023; path=/ammo")
        res = FakeResponse(headers, "http://www.acme.com/")
        c.extract_cookies(res, req)

        req = urllib.request.Request("http://www.acme.com/ammo")
        c.add_cookie_header(req)

        self.assertRegex(req.get_header("Cookie"),
                         r"PART_NUMBER=RIDING_ROCKET_0023;\s*"
                          "PART_NUMBER=ROCKET_LAUNCHER_0001")

    def test_ietf_example_1(self):
        #-------------------------------------------------------------------
        # Then we test przy the examples z draft-ietf-http-state-man-mec-03.txt
        #
        # 5.  EXAMPLES

        c = CookieJar(DefaultCookiePolicy(rfc2965=Prawda))

        #
        # 5.1  Example 1
        #
        # Most detail of request oraz response headers has been omitted.  Assume
        # the user agent has no stored cookies.
        #
        #   1.  User Agent -> Server
        #
        #       POST /acme/login HTTP/1.1
        #       [form data]
        #
        #       User identifies self via a form.
        #
        #   2.  Server -> User Agent
        #
        #       HTTP/1.1 200 OK
        #       Set-Cookie2: Customer="WILE_E_COYOTE"; Version="1"; Path="/acme"
        #
        #       Cookie reflects user's identity.

        cookie = interact_2965(
            c, 'http://www.acme.com/acme/login',
            'Customer="WILE_E_COYOTE"; Version="1"; Path="/acme"')
        self.assertNieprawda(cookie)

        #
        #   3.  User Agent -> Server
        #
        #       POST /acme/pickitem HTTP/1.1
        #       Cookie: $Version="1"; Customer="WILE_E_COYOTE"; $Path="/acme"
        #       [form data]
        #
        #       User selects an item dla ``shopping basket.''
        #
        #   4.  Server -> User Agent
        #
        #       HTTP/1.1 200 OK
        #       Set-Cookie2: Part_Number="Rocket_Launcher_0001"; Version="1";
        #               Path="/acme"
        #
        #       Shopping basket contains an item.

        cookie = interact_2965(c, 'http://www.acme.com/acme/pickitem',
                               'Part_Number="Rocket_Launcher_0001"; '
                               'Version="1"; Path="/acme"');
        self.assertRegex(cookie,
            r'^\$Version="?1"?; Customer="?WILE_E_COYOTE"?; \$Path="/acme"$')

        #
        #   5.  User Agent -> Server
        #
        #       POST /acme/shipping HTTP/1.1
        #       Cookie: $Version="1";
        #               Customer="WILE_E_COYOTE"; $Path="/acme";
        #               Part_Number="Rocket_Launcher_0001"; $Path="/acme"
        #       [form data]
        #
        #       User selects shipping method z form.
        #
        #   6.  Server -> User Agent
        #
        #       HTTP/1.1 200 OK
        #       Set-Cookie2: Shipping="FedEx"; Version="1"; Path="/acme"
        #
        #       New cookie reflects shipping method.

        cookie = interact_2965(c, "http://www.acme.com/acme/shipping",
                               'Shipping="FedEx"; Version="1"; Path="/acme"')

        self.assertRegex(cookie, r'^\$Version="?1"?;')
        self.assertRegex(cookie, r'Part_Number="?Rocket_Launcher_0001"?;'
                                  '\s*\$Path="\/acme"')
        self.assertRegex(cookie, r'Customer="?WILE_E_COYOTE"?;'
                                  '\s*\$Path="\/acme"')

        #
        #   7.  User Agent -> Server
        #
        #       POST /acme/process HTTP/1.1
        #       Cookie: $Version="1";
        #               Customer="WILE_E_COYOTE"; $Path="/acme";
        #               Part_Number="Rocket_Launcher_0001"; $Path="/acme";
        #               Shipping="FedEx"; $Path="/acme"
        #       [form data]
        #
        #       User chooses to process order.
        #
        #   8.  Server -> User Agent
        #
        #       HTTP/1.1 200 OK
        #
        #       Transaction jest complete.

        cookie = interact_2965(c, "http://www.acme.com/acme/process")
        self.assertRegex(cookie, r'Shipping="?FedEx"?;\s*\$Path="\/acme"')
        self.assertIn("WILE_E_COYOTE", cookie)

        #
        # The user agent makes a series of requests on the origin server, after
        # each of which it receives a new cookie.  All the cookies have the same
        # Path attribute oraz (default) domain.  Because the request URLs all have
        # /acme jako a prefix, oraz that matches the Path attribute, each request
        # contains all the cookies received so far.

    def test_ietf_example_2(self):
        # 5.2  Example 2
        #
        # This example illustrates the effect of the Path attribute.  All detail
        # of request oraz response headers has been omitted.  Assume the user agent
        # has no stored cookies.

        c = CookieJar(DefaultCookiePolicy(rfc2965=Prawda))

        # Imagine the user agent has received, w response to earlier requests,
        # the response headers
        #
        # Set-Cookie2: Part_Number="Rocket_Launcher_0001"; Version="1";
        #         Path="/acme"
        #
        # oraz
        #
        # Set-Cookie2: Part_Number="Riding_Rocket_0023"; Version="1";
        #         Path="/acme/ammo"

        interact_2965(
            c, "http://www.acme.com/acme/ammo/specific",
            'Part_Number="Rocket_Launcher_0001"; Version="1"; Path="/acme"',
            'Part_Number="Riding_Rocket_0023"; Version="1"; Path="/acme/ammo"')

        # A subsequent request by the user agent to the (same) server dla URLs of
        # the form /acme/ammo/...  would include the following request header:
        #
        # Cookie: $Version="1";
        #         Part_Number="Riding_Rocket_0023"; $Path="/acme/ammo";
        #         Part_Number="Rocket_Launcher_0001"; $Path="/acme"
        #
        # Note that the NAME=VALUE pair dla the cookie przy the more specific Path
        # attribute, /acme/ammo, comes before the one przy the less specific Path
        # attribute, /acme.  Further note that the same cookie name appears more
        # than once.

        cookie = interact_2965(c, "http://www.acme.com/acme/ammo/...")
        self.assertRegex(cookie, r"Riding_Rocket_0023.*Rocket_Launcher_0001")

        # A subsequent request by the user agent to the (same) server dla a URL of
        # the form /acme/parts/ would include the following request header:
        #
        # Cookie: $Version="1"; Part_Number="Rocket_Launcher_0001"; $Path="/acme"
        #
        # Here, the second cookie's Path attribute /acme/ammo jest nie a prefix of
        # the request URL, /acme/parts/, so the cookie does nie get forwarded to
        # the server.

        cookie = interact_2965(c, "http://www.acme.com/acme/parts/")
        self.assertIn("Rocket_Launcher_0001", cookie)
        self.assertNotIn("Riding_Rocket_0023", cookie)

    def test_rejection(self):
        # Test rejection of Set-Cookie2 responses based on domain, path, port.
        pol = DefaultCookiePolicy(rfc2965=Prawda)

        c = LWPCookieJar(policy=pol)

        max_age = "max-age=3600"

        # illegal domain (no embedded dots)
        cookie = interact_2965(c, "http://www.acme.com",
                               'foo=bar; domain=".com"; version=1')
        self.assertNieprawda(c)

        # legal domain
        cookie = interact_2965(c, "http://www.acme.com",
                               'ping=pong; domain="acme.com"; version=1')
        self.assertEqual(len(c), 1)

        # illegal domain (host prefix "www.a" contains a dot)
        cookie = interact_2965(c, "http://www.a.acme.com",
                               'whiz=bang; domain="acme.com"; version=1')
        self.assertEqual(len(c), 1)

        # legal domain
        cookie = interact_2965(c, "http://www.a.acme.com",
                               'wow=flutter; domain=".a.acme.com"; version=1')
        self.assertEqual(len(c), 2)

        # can't partially match an IP-address
        cookie = interact_2965(c, "http://125.125.125.125",
                               'zzzz=ping; domain="125.125.125"; version=1')
        self.assertEqual(len(c), 2)

        # illegal path (must be prefix of request path)
        cookie = interact_2965(c, "http://www.sol.no",
                               'blah=rhubarb; domain=".sol.no"; path="/foo"; '
                               'version=1')
        self.assertEqual(len(c), 2)

        # legal path
        cookie = interact_2965(c, "http://www.sol.no/foo/bar",
                               'bing=bong; domain=".sol.no"; path="/foo"; '
                               'version=1')
        self.assertEqual(len(c), 3)

        # illegal port (request-port nie w list)
        cookie = interact_2965(c, "http://www.sol.no",
                               'whiz=ffft; domain=".sol.no"; port="90,100"; '
                               'version=1')
        self.assertEqual(len(c), 3)

        # legal port
        cookie = interact_2965(
            c, "http://www.sol.no",
            r'bang=wallop; version=1; domain=".sol.no"; '
            r'port="90,100, 80,8080"; '
            r'max-age=100; Comment = "Just kidding! (\"|\\\\) "')
        self.assertEqual(len(c), 4)

        # port attribute without any value (current port)
        cookie = interact_2965(c, "http://www.sol.no",
                               'foo9=bar; version=1; domain=".sol.no"; port; '
                               'max-age=100;')
        self.assertEqual(len(c), 5)

        # encoded path
        # LWP has this test, but unescaping allowed path characters seems
        # like a bad idea, so I think this should fail:
##         cookie = interact_2965(c, "http://www.sol.no/foo/",
##                           r'foo8=bar; version=1; path="/%66oo"')
        # but this jest OK, because '<' jest nie an allowed HTTP URL path
        # character:
        cookie = interact_2965(c, "http://www.sol.no/<oo/",
                               r'foo8=bar; version=1; path="/%3coo"')
        self.assertEqual(len(c), 6)

        # save oraz restore
        filename = test.support.TESTFN

        spróbuj:
            c.save(filename, ignore_discard=Prawda)
            old = repr(c)

            c = LWPCookieJar(policy=pol)
            c.load(filename, ignore_discard=Prawda)
        w_końcu:
            spróbuj: os.unlink(filename)
            wyjąwszy OSError: dalej

        self.assertEqual(old, repr(c))

    def test_url_encoding(self):
        # Try some URL encodings of the PATHs.
        # (the behaviour here has changed z libwww-perl)
        c = CookieJar(DefaultCookiePolicy(rfc2965=Prawda))
        interact_2965(c, "http://www.acme.com/foo%2f%25/"
                         "%3c%3c%0Anew%C3%A5/%C3%A5",
                      "foo  =   bar; version    =   1")

        cookie = interact_2965(
            c, "http://www.acme.com/foo%2f%25/<<%0anew\345/\346\370\345",
            'bar=baz; path="/foo/"; version=1');
        version_re = re.compile(r'^\$version=\"?1\"?', re.I)
        self.assertIn("foo=bar", cookie)
        self.assertRegex(cookie, version_re)

        cookie = interact_2965(
            c, "http://www.acme.com/foo/%25/<<%0anew\345/\346\370\345")
        self.assertNieprawda(cookie)

        # unicode URL doesn't podnieś exception
        cookie = interact_2965(c, "http://www.acme.com/\xfc")

    def test_mozilla(self):
        # Save / load Mozilla/Netscape cookie file format.
        year_plus_one = time.localtime()[0] + 1

        filename = test.support.TESTFN

        c = MozillaCookieJar(filename,
                             policy=DefaultCookiePolicy(rfc2965=Prawda))
        interact_2965(c, "http://www.acme.com/",
                      "foo1=bar; max-age=100; Version=1")
        interact_2965(c, "http://www.acme.com/",
                      'foo2=bar; port="80"; max-age=100; Discard; Version=1')
        interact_2965(c, "http://www.acme.com/", "foo3=bar; secure; Version=1")

        expires = "expires=09-Nov-%d 23:12:40 GMT" % (year_plus_one,)
        interact_netscape(c, "http://www.foo.com/",
                          "fooa=bar; %s" % expires)
        interact_netscape(c, "http://www.foo.com/",
                          "foob=bar; Domain=.foo.com; %s" % expires)
        interact_netscape(c, "http://www.foo.com/",
                          "fooc=bar; Domain=www.foo.com; %s" % expires)

        def save_and_restore(cj, ignore_discard):
            spróbuj:
                cj.save(ignore_discard=ignore_discard)
                new_c = MozillaCookieJar(filename,
                                         DefaultCookiePolicy(rfc2965=Prawda))
                new_c.load(ignore_discard=ignore_discard)
            w_końcu:
                spróbuj: os.unlink(filename)
                wyjąwszy OSError: dalej
            zwróć new_c

        new_c = save_and_restore(c, Prawda)
        self.assertEqual(len(new_c), 6)  # none discarded
        self.assertIn("name='foo1', value='bar'", repr(new_c))

        new_c = save_and_restore(c, Nieprawda)
        self.assertEqual(len(new_c), 4)  # 2 of them discarded on save
        self.assertIn("name='foo1', value='bar'", repr(new_c))

    def test_netscape_misc(self):
        # Some additional Netscape cookies tests.
        c = CookieJar()
        headers = []
        req = urllib.request.Request("http://foo.bar.acme.com/foo")

        # Netscape allows a host part that contains dots
        headers.append("Set-Cookie: Customer=WILE_E_COYOTE; domain=.acme.com")
        res = FakeResponse(headers, "http://www.acme.com/foo")
        c.extract_cookies(res, req)

        # oraz that the domain jest the same jako the host without adding a leading
        # dot to the domain.  Should nie quote even jeżeli strange chars are used
        # w the cookie value.
        headers.append("Set-Cookie: PART_NUMBER=3,4; domain=foo.bar.acme.com")
        res = FakeResponse(headers, "http://www.acme.com/foo")
        c.extract_cookies(res, req)

        req = urllib.request.Request("http://foo.bar.acme.com/foo")
        c.add_cookie_header(req)
        self.assertIn("PART_NUMBER=3,4", req.get_header("Cookie"))
        self.assertIn("Customer=WILE_E_COYOTE",req.get_header("Cookie"))

    def test_intranet_domains_2965(self):
        # Test handling of local intranet hostnames without a dot.
        c = CookieJar(DefaultCookiePolicy(rfc2965=Prawda))
        interact_2965(c, "http://example/",
                      "foo1=bar; PORT; Discard; Version=1;")
        cookie = interact_2965(c, "http://example/",
                               'foo2=bar; domain=".local"; Version=1')
        self.assertIn("foo1=bar", cookie)

        interact_2965(c, "http://example/", 'foo3=bar; Version=1')
        cookie = interact_2965(c, "http://example/")
        self.assertIn("foo2=bar", cookie)
        self.assertEqual(len(c), 3)

    def test_intranet_domains_ns(self):
        c = CookieJar(DefaultCookiePolicy(rfc2965 = Nieprawda))
        interact_netscape(c, "http://example/", "foo1=bar")
        cookie = interact_netscape(c, "http://example/",
                                   'foo2=bar; domain=.local')
        self.assertEqual(len(c), 2)
        self.assertIn("foo1=bar", cookie)

        cookie = interact_netscape(c, "http://example/")
        self.assertIn("foo2=bar", cookie)
        self.assertEqual(len(c), 2)

    def test_empty_path(self):
        # Test dla empty path
        # Broken web-server ORION/1.3.38 returns to the client response like
        #
        #       Set-Cookie: JSESSIONID=ABCDERANDOM123; Path=
        #
        # ie. przy Path set to nothing.
        # In this case, extract_cookies() must set cookie to / (root)
        c = CookieJar(DefaultCookiePolicy(rfc2965 = Prawda))
        headers = []

        req = urllib.request.Request("http://www.ants.com/")
        headers.append("Set-Cookie: JSESSIONID=ABCDERANDOM123; Path=")
        res = FakeResponse(headers, "http://www.ants.com/")
        c.extract_cookies(res, req)

        req = urllib.request.Request("http://www.ants.com/")
        c.add_cookie_header(req)

        self.assertEqual(req.get_header("Cookie"),
                         "JSESSIONID=ABCDERANDOM123")
        self.assertEqual(req.get_header("Cookie2"), '$Version="1"')

        # missing path w the request URI
        req = urllib.request.Request("http://www.ants.com:8080")
        c.add_cookie_header(req)

        self.assertEqual(req.get_header("Cookie"),
                         "JSESSIONID=ABCDERANDOM123")
        self.assertEqual(req.get_header("Cookie2"), '$Version="1"')

    def test_session_cookies(self):
        year_plus_one = time.localtime()[0] + 1

        # Check session cookies are deleted properly by
        # CookieJar.clear_session_cookies method

        req = urllib.request.Request('http://www.perlmeister.com/scripts')
        headers = []
        headers.append("Set-Cookie: s1=session;Path=/scripts")
        headers.append("Set-Cookie: p1=perm; Domain=.perlmeister.com;"
                       "Path=/;expires=Fri, 02-Feb-%d 23:24:20 GMT" %
                       year_plus_one)
        headers.append("Set-Cookie: p2=perm;Path=/;expires=Fri, "
                       "02-Feb-%d 23:24:20 GMT" % year_plus_one)
        headers.append("Set-Cookie: s2=session;Path=/scripts;"
                       "Domain=.perlmeister.com")
        headers.append('Set-Cookie2: s3=session;Version=1;Discard;Path="/"')
        res = FakeResponse(headers, 'http://www.perlmeister.com/scripts')

        c = CookieJar()
        c.extract_cookies(res, req)
        # How many session/permanent cookies do we have?
        counter = {"session_after": 0,
                   "perm_after": 0,
                   "session_before": 0,
                   "perm_before": 0}
        dla cookie w c:
            key = "%s_before" % cookie.value
            counter[key] = counter[key] + 1
        c.clear_session_cookies()
        # How many now?
        dla cookie w c:
            key = "%s_after" % cookie.value
            counter[key] = counter[key] + 1

            # a permanent cookie got lost accidently
        self.assertEqual(counter["perm_after"], counter["perm_before"])
            # a session cookie hasn't been cleared
        self.assertEqual(counter["session_after"], 0)
            # we didn't have session cookies w the first place
        self.assertNotEqual(counter["session_before"], 0)


def test_main(verbose=Nic):
    test.support.run_unittest(
        DateTimeTests,
        HeaderTests,
        CookieTests,
        FileCookieJarTests,
        LWPCookieTests,
        )

jeżeli __name__ == "__main__":
    test_main(verbose=Prawda)
