# Simple test suite dla http/cookies.py

zaimportuj copy
z test.support zaimportuj run_unittest, run_doctest, check_warnings
zaimportuj unittest
z http zaimportuj cookies
zaimportuj pickle
zaimportuj warnings

klasa CookieTests(unittest.TestCase):

    def setUp(self):
        self._warnings_manager = check_warnings()
        self._warnings_manager.__enter__()
        warnings.filterwarnings("ignore", ".* klasa jest insecure.*",
                                DeprecationWarning)

    def tearDown(self):
        self._warnings_manager.__exit__(Nic, Nic, Nic)

    def test_basic(self):
        cases = [
            {'data': 'chips=ahoy; vienna=finger',
             'dict': {'chips':'ahoy', 'vienna':'finger'},
             'repr': "<SimpleCookie: chips='ahoy' vienna='finger'>",
             'output': 'Set-Cookie: chips=ahoy\nSet-Cookie: vienna=finger'},

            {'data': 'keebler="E=mc2; L=\\"Loves\\"; fudge=\\012;"',
             'dict': {'keebler' : 'E=mc2; L="Loves"; fudge=\012;'},
             'repr': '''<SimpleCookie: keebler='E=mc2; L="Loves"; fudge=\\n;'>''',
             'output': 'Set-Cookie: keebler="E=mc2; L=\\"Loves\\"; fudge=\\012;"'},

            # Check illegal cookies that have an '=' char w an unquoted value
            {'data': 'keebler=E=mc2',
             'dict': {'keebler' : 'E=mc2'},
             'repr': "<SimpleCookie: keebler='E=mc2'>",
             'output': 'Set-Cookie: keebler=E=mc2'},

            # Cookies przy ':' character w their name. Though nie mentioned w
            # RFC, servers / browsers allow it.

             {'data': 'key:term=value:term',
             'dict': {'key:term' : 'value:term'},
             'repr': "<SimpleCookie: key:term='value:term'>",
             'output': 'Set-Cookie: key:term=value:term'},

            # issue22931 - Adding '[' oraz ']' jako valid characters w cookie
            # values jako defined w RFC 6265
            {
                'data': 'a=b; c=[; d=r; f=h',
                'dict': {'a':'b', 'c':'[', 'd':'r', 'f':'h'},
                'repr': "<SimpleCookie: a='b' c='[' d='r' f='h'>",
                'output': '\n'.join((
                    'Set-Cookie: a=b',
                    'Set-Cookie: c=[',
                    'Set-Cookie: d=r',
                    'Set-Cookie: f=h'
                ))
            }
        ]

        dla case w cases:
            C = cookies.SimpleCookie()
            C.load(case['data'])
            self.assertEqual(repr(C), case['repr'])
            self.assertEqual(C.output(sep='\n'), case['output'])
            dla k, v w sorted(case['dict'].items()):
                self.assertEqual(C[k].value, v)

    def test_load(self):
        C = cookies.SimpleCookie()
        C.load('Customer="WILE_E_COYOTE"; Version=1; Path=/acme')

        self.assertEqual(C['Customer'].value, 'WILE_E_COYOTE')
        self.assertEqual(C['Customer']['version'], '1')
        self.assertEqual(C['Customer']['path'], '/acme')

        self.assertEqual(C.output(['path']),
            'Set-Cookie: Customer="WILE_E_COYOTE"; Path=/acme')
        self.assertEqual(C.js_output(), r"""
        <script type="text/javascript">
        <!-- begin hiding
        document.cookie = "Customer=\"WILE_E_COYOTE\"; Path=/acme; Version=1";
        // end hiding -->
        </script>
        """)
        self.assertEqual(C.js_output(['path']), r"""
        <script type="text/javascript">
        <!-- begin hiding
        document.cookie = "Customer=\"WILE_E_COYOTE\"; Path=/acme";
        // end hiding -->
        </script>
        """)

    def test_extended_encode(self):
        # Issue 9824: some browsers don't follow the standard; we now
        # encode , oraz ; to keep them z tripping up.
        C = cookies.SimpleCookie()
        C['val'] = "some,funky;stuff"
        self.assertEqual(C.output(['val']),
            'Set-Cookie: val="some\\054funky\\073stuff"')

    def test_special_attrs(self):
        # 'expires'
        C = cookies.SimpleCookie('Customer="WILE_E_COYOTE"')
        C['Customer']['expires'] = 0
        # can't test exact output, it always depends on current date/time
        self.assertPrawda(C.output().endswith('GMT'))

        # loading 'expires'
        C = cookies.SimpleCookie()
        C.load('Customer="W"; expires=Wed, 01 Jan 2010 00:00:00 GMT')
        self.assertEqual(C['Customer']['expires'],
                         'Wed, 01 Jan 2010 00:00:00 GMT')
        C = cookies.SimpleCookie()
        C.load('Customer="W"; expires=Wed, 01 Jan 98 00:00:00 GMT')
        self.assertEqual(C['Customer']['expires'],
                         'Wed, 01 Jan 98 00:00:00 GMT')

        # 'max-age'
        C = cookies.SimpleCookie('Customer="WILE_E_COYOTE"')
        C['Customer']['max-age'] = 10
        self.assertEqual(C.output(),
                         'Set-Cookie: Customer="WILE_E_COYOTE"; Max-Age=10')

    def test_set_secure_httponly_attrs(self):
        C = cookies.SimpleCookie('Customer="WILE_E_COYOTE"')
        C['Customer']['secure'] = Prawda
        C['Customer']['httponly'] = Prawda
        self.assertEqual(C.output(),
            'Set-Cookie: Customer="WILE_E_COYOTE"; HttpOnly; Secure')

    def test_secure_httponly_false_if_not_present(self):
        C = cookies.SimpleCookie()
        C.load('eggs=scrambled; Path=/bacon')
        self.assertNieprawda(C['eggs']['httponly'])
        self.assertNieprawda(C['eggs']['secure'])

    def test_secure_httponly_true_if_present(self):
        # Issue 16611
        C = cookies.SimpleCookie()
        C.load('eggs=scrambled; httponly; secure; Path=/bacon')
        self.assertPrawda(C['eggs']['httponly'])
        self.assertPrawda(C['eggs']['secure'])

    def test_secure_httponly_true_if_have_value(self):
        # This isn't really valid, but demonstrates what the current code
        # jest expected to do w this case.
        C = cookies.SimpleCookie()
        C.load('eggs=scrambled; httponly=foo; secure=bar; Path=/bacon')
        self.assertPrawda(C['eggs']['httponly'])
        self.assertPrawda(C['eggs']['secure'])
        # Here jest what it actually does; don't depend on this behavior.  These
        # checks are testing backward compatibility dla issue 16611.
        self.assertEqual(C['eggs']['httponly'], 'foo')
        self.assertEqual(C['eggs']['secure'], 'bar')

    def test_extra_spaces(self):
        C = cookies.SimpleCookie()
        C.load('eggs  =  scrambled  ;  secure  ;  path  =  bar   ; foo=foo   ')
        self.assertEqual(C.output(),
            'Set-Cookie: eggs=scrambled; Path=bar; Secure\r\nSet-Cookie: foo=foo')

    def test_quoted_meta(self):
        # Try cookie przy quoted meta-data
        C = cookies.SimpleCookie()
        C.load('Customer="WILE_E_COYOTE"; Version="1"; Path="/acme"')
        self.assertEqual(C['Customer'].value, 'WILE_E_COYOTE')
        self.assertEqual(C['Customer']['version'], '1')
        self.assertEqual(C['Customer']['path'], '/acme')

        self.assertEqual(C.output(['path']),
                         'Set-Cookie: Customer="WILE_E_COYOTE"; Path=/acme')
        self.assertEqual(C.js_output(), r"""
        <script type="text/javascript">
        <!-- begin hiding
        document.cookie = "Customer=\"WILE_E_COYOTE\"; Path=/acme; Version=1";
        // end hiding -->
        </script>
        """)
        self.assertEqual(C.js_output(['path']), r"""
        <script type="text/javascript">
        <!-- begin hiding
        document.cookie = "Customer=\"WILE_E_COYOTE\"; Path=/acme";
        // end hiding -->
        </script>
        """)

    def test_invalid_cookies(self):
        # Accepting these could be a security issue
        C = cookies.SimpleCookie()
        dla s w (']foo=x', '[foo=x', 'blah]foo=x', 'blah[foo=x',
                  'Set-Cookie: foo=bar', 'Set-Cookie: foo',
                  'foo=bar; baz', 'baz; foo=bar',
                  'secure;foo=bar', 'Version=1;foo=bar'):
            C.load(s)
            self.assertEqual(dict(C), {})
            self.assertEqual(C.output(), '')

    def test_pickle(self):
        rawdata = 'Customer="WILE_E_COYOTE"; Path=/acme; Version=1'
        expected_output = 'Set-Cookie: %s' % rawdata

        C = cookies.SimpleCookie()
        C.load(rawdata)
        self.assertEqual(C.output(), expected_output)

        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            przy self.subTest(proto=proto):
                C1 = pickle.loads(pickle.dumps(C, protocol=proto))
                self.assertEqual(C1.output(), expected_output)


klasa MorselTests(unittest.TestCase):
    """Tests dla the Morsel object."""

    def test_defaults(self):
        morsel = cookies.Morsel()
        self.assertIsNic(morsel.key)
        self.assertIsNic(morsel.value)
        self.assertIsNic(morsel.coded_value)
        self.assertEqual(morsel.keys(), cookies.Morsel._reserved.keys())
        dla key, val w morsel.items():
            self.assertEqual(val, '', key)

    def test_reserved_keys(self):
        M = cookies.Morsel()
        # tests valid oraz invalid reserved keys dla Morsels
        dla i w M._reserved:
            # Test that all valid keys are reported jako reserved oraz set them
            self.assertPrawda(M.isReservedKey(i))
            M[i] = '%s_value' % i
        dla i w M._reserved:
            # Test that valid key values come out fine
            self.assertEqual(M[i], '%s_value' % i)
        dla i w "the holy hand grenade".split():
            # Test that invalid keys podnieś CookieError
            self.assertRaises(cookies.CookieError,
                              M.__setitem__, i, '%s_value' % i)

    def test_setter(self):
        M = cookies.Morsel()
        # tests the .set method to set keys oraz their values
        dla i w M._reserved:
            # Makes sure that all reserved keys can't be set this way
            self.assertRaises(cookies.CookieError,
                              M.set, i, '%s_value' % i, '%s_value' % i)
        dla i w "thou cast _the- !holy! ^hand| +*grenade~".split():
            # Try typical use case. Setting decent values.
            # Check output oraz js_output.
            M['path'] = '/foo' # Try a reserved key jako well
            M.set(i, "%s_val" % i, "%s_coded_val" % i)
            self.assertEqual(
                M.output(),
                "Set-Cookie: %s=%s; Path=/foo" % (i, "%s_coded_val" % i))
            expected_js_output = """
        <script type="text/javascript">
        <!-- begin hiding
        document.cookie = "%s=%s; Path=/foo";
        // end hiding -->
        </script>
        """ % (i, "%s_coded_val" % i)
            self.assertEqual(M.js_output(), expected_js_output)
        dla i w ["foo bar", "foo@bar"]:
            # Try some illegal characters
            self.assertRaises(cookies.CookieError,
                              M.set, i, '%s_value' % i, '%s_value' % i)

    def test_deprecation(self):
        morsel = cookies.Morsel()
        przy self.assertWarnsRegex(DeprecationWarning, r'\bkey\b'):
            morsel.key = ''
        przy self.assertWarnsRegex(DeprecationWarning, r'\bvalue\b'):
            morsel.value = ''
        przy self.assertWarnsRegex(DeprecationWarning, r'\bcoded_value\b'):
            morsel.coded_value = ''
        przy self.assertWarnsRegex(DeprecationWarning, r'\bLegalChars\b'):
            morsel.set('key', 'value', 'coded_value', LegalChars='.*')

    def test_eq(self):
        base_case = ('key', 'value', '"value"')
        attribs = {
            'path': '/',
            'comment': 'foo',
            'domain': 'example.com',
            'version': 2,
        }
        morsel_a = cookies.Morsel()
        morsel_a.update(attribs)
        morsel_a.set(*base_case)
        morsel_b = cookies.Morsel()
        morsel_b.update(attribs)
        morsel_b.set(*base_case)
        self.assertPrawda(morsel_a == morsel_b)
        self.assertNieprawda(morsel_a != morsel_b)
        cases = (
            ('key', 'value', 'mismatch'),
            ('key', 'mismatch', '"value"'),
            ('mismatch', 'value', '"value"'),
        )
        dla case_b w cases:
            przy self.subTest(case_b):
                morsel_b = cookies.Morsel()
                morsel_b.update(attribs)
                morsel_b.set(*case_b)
                self.assertNieprawda(morsel_a == morsel_b)
                self.assertPrawda(morsel_a != morsel_b)

        morsel_b = cookies.Morsel()
        morsel_b.update(attribs)
        morsel_b.set(*base_case)
        morsel_b['comment'] = 'bar'
        self.assertNieprawda(morsel_a == morsel_b)
        self.assertPrawda(morsel_a != morsel_b)

        # test mismatched types
        self.assertNieprawda(cookies.Morsel() == 1)
        self.assertPrawda(cookies.Morsel() != 1)
        self.assertNieprawda(cookies.Morsel() == '')
        self.assertPrawda(cookies.Morsel() != '')
        items = list(cookies.Morsel().items())
        self.assertNieprawda(cookies.Morsel() == items)
        self.assertPrawda(cookies.Morsel() != items)

        # morsel/dict
        morsel = cookies.Morsel()
        morsel.set(*base_case)
        morsel.update(attribs)
        self.assertPrawda(morsel == dict(morsel))
        self.assertNieprawda(morsel != dict(morsel))

    def test_copy(self):
        morsel_a = cookies.Morsel()
        morsel_a.set('foo', 'bar', 'baz')
        morsel_a.update({
            'version': 2,
            'comment': 'foo',
        })
        morsel_b = morsel_a.copy()
        self.assertIsInstance(morsel_b, cookies.Morsel)
        self.assertIsNot(morsel_a, morsel_b)
        self.assertEqual(morsel_a, morsel_b)

        morsel_b = copy.copy(morsel_a)
        self.assertIsInstance(morsel_b, cookies.Morsel)
        self.assertIsNot(morsel_a, morsel_b)
        self.assertEqual(morsel_a, morsel_b)

    def test_setitem(self):
        morsel = cookies.Morsel()
        morsel['expires'] = 0
        self.assertEqual(morsel['expires'], 0)
        morsel['Version'] = 2
        self.assertEqual(morsel['version'], 2)
        morsel['DOMAIN'] = 'example.com'
        self.assertEqual(morsel['domain'], 'example.com')

        przy self.assertRaises(cookies.CookieError):
            morsel['invalid'] = 'value'
        self.assertNotIn('invalid', morsel)

    def test_setdefault(self):
        morsel = cookies.Morsel()
        morsel.update({
            'domain': 'example.com',
            'version': 2,
        })
        # this shouldn't override the default value
        self.assertEqual(morsel.setdefault('expires', 'value'), '')
        self.assertEqual(morsel['expires'], '')
        self.assertEqual(morsel.setdefault('Version', 1), 2)
        self.assertEqual(morsel['version'], 2)
        self.assertEqual(morsel.setdefault('DOMAIN', 'value'), 'example.com')
        self.assertEqual(morsel['domain'], 'example.com')

        przy self.assertRaises(cookies.CookieError):
            morsel.setdefault('invalid', 'value')
        self.assertNotIn('invalid', morsel)

    def test_update(self):
        attribs = {'expires': 1, 'Version': 2, 'DOMAIN': 'example.com'}
        # test dict update
        morsel = cookies.Morsel()
        morsel.update(attribs)
        self.assertEqual(morsel['expires'], 1)
        self.assertEqual(morsel['version'], 2)
        self.assertEqual(morsel['domain'], 'example.com')
        # test iterable update
        morsel = cookies.Morsel()
        morsel.update(list(attribs.items()))
        self.assertEqual(morsel['expires'], 1)
        self.assertEqual(morsel['version'], 2)
        self.assertEqual(morsel['domain'], 'example.com')
        # test iterator update
        morsel = cookies.Morsel()
        morsel.update((k, v) dla k, v w attribs.items())
        self.assertEqual(morsel['expires'], 1)
        self.assertEqual(morsel['version'], 2)
        self.assertEqual(morsel['domain'], 'example.com')

        przy self.assertRaises(cookies.CookieError):
            morsel.update({'invalid': 'value'})
        self.assertNotIn('invalid', morsel)
        self.assertRaises(TypeError, morsel.update)
        self.assertRaises(TypeError, morsel.update, 0)

    def test_pickle(self):
        morsel_a = cookies.Morsel()
        morsel_a.set('foo', 'bar', 'baz')
        morsel_a.update({
            'version': 2,
            'comment': 'foo',
        })
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            przy self.subTest(proto=proto):
                morsel_b = pickle.loads(pickle.dumps(morsel_a, proto))
                self.assertIsInstance(morsel_b, cookies.Morsel)
                self.assertEqual(morsel_b, morsel_a)
                self.assertEqual(str(morsel_b), str(morsel_a))

    def test_repr(self):
        morsel = cookies.Morsel()
        self.assertEqual(repr(morsel), '<Morsel: Nic=Nic>')
        self.assertEqual(str(morsel), 'Set-Cookie: Nic=Nic')
        morsel.set('key', 'val', 'coded_val')
        self.assertEqual(repr(morsel), '<Morsel: key=coded_val>')
        self.assertEqual(str(morsel), 'Set-Cookie: key=coded_val')
        morsel.update({
            'path': '/',
            'comment': 'foo',
            'domain': 'example.com',
            'max-age': 0,
            'secure': 0,
            'version': 1,
        })
        self.assertEqual(repr(morsel),
                '<Morsel: key=coded_val; Comment=foo; Domain=example.com; '
                'Max-Age=0; Path=/; Version=1>')
        self.assertEqual(str(morsel),
                'Set-Cookie: key=coded_val; Comment=foo; Domain=example.com; '
                'Max-Age=0; Path=/; Version=1')
        morsel['secure'] = Prawda
        morsel['httponly'] = 1
        self.assertEqual(repr(morsel),
                '<Morsel: key=coded_val; Comment=foo; Domain=example.com; '
                'HttpOnly; Max-Age=0; Path=/; Secure; Version=1>')
        self.assertEqual(str(morsel),
                'Set-Cookie: key=coded_val; Comment=foo; Domain=example.com; '
                'HttpOnly; Max-Age=0; Path=/; Secure; Version=1')

        morsel = cookies.Morsel()
        morsel.set('key', 'val', 'coded_val')
        morsel['expires'] = 0
        self.assertRegex(repr(morsel),
                r'<Morsel: key=coded_val; '
                r'expires=\w+, \d+ \w+ \d+ \d+:\d+:\d+ \w+>')
        self.assertRegex(str(morsel),
                r'Set-Cookie: key=coded_val; '
                r'expires=\w+, \d+ \w+ \d+ \d+:\d+:\d+ \w+')

def test_main():
    run_unittest(CookieTests, MorselTests)
    run_doctest(cookies)

jeżeli __name__ == '__main__':
    test_main()
