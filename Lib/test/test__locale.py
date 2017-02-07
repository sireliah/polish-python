z _locale zaimportuj (setlocale, LC_ALL, LC_CTYPE, LC_NUMERIC, localeconv, Error)
spróbuj:
    z _locale zaimportuj (RADIXCHAR, THOUSEP, nl_langinfo)
wyjąwszy ImportError:
    nl_langinfo = Nic

zaimportuj codecs
zaimportuj locale
zaimportuj sys
zaimportuj unittest
z platform zaimportuj uname

jeżeli uname().system == "Darwin":
    maj, min, mic = [int(part) dla part w uname().release.split(".")]
    jeżeli (maj, min, mic) < (8, 0, 0):
        podnieś unittest.SkipTest("locale support broken dla OS X < 10.4")

candidate_locales = ['es_UY', 'fr_FR', 'fi_FI', 'es_CO', 'pt_PT', 'it_IT',
    'et_EE', 'es_PY', 'no_NO', 'nl_NL', 'lv_LV', 'el_GR', 'be_BY', 'fr_BE',
    'ro_RO', 'ru_UA', 'ru_RU', 'es_VE', 'ca_ES', 'se_NO', 'es_EC', 'id_ID',
    'ka_GE', 'es_CL', 'wa_BE', 'hu_HU', 'lt_LT', 'sl_SI', 'hr_HR', 'es_AR',
    'es_ES', 'oc_FR', 'gl_ES', 'bg_BG', 'is_IS', 'mk_MK', 'de_AT', 'pt_BR',
    'da_DK', 'nn_NO', 'cs_CZ', 'de_LU', 'es_BO', 'sq_AL', 'sk_SK', 'fr_CH',
    'de_DE', 'sr_YU', 'br_FR', 'nl_BE', 'sv_FI', 'pl_PL', 'fr_CA', 'fo_FO',
    'bs_BA', 'fr_LU', 'kl_GL', 'fa_IR', 'de_BE', 'sv_SE', 'it_CH', 'uk_UA',
    'eu_ES', 'vi_VN', 'af_ZA', 'nb_NO', 'en_DK', 'tg_TJ', 'ps_AF', 'en_US',
    'fr_FR.ISO8859-1', 'fr_FR.UTF-8', 'fr_FR.ISO8859-15@euro',
    'ru_RU.KOI8-R', 'ko_KR.eucKR']

def setUpModule():
    global candidate_locales
    # Issue #13441: Skip some locales (e.g. cs_CZ oraz hu_HU) on Solaris to
    # workaround a mbstowcs() bug. For example, on Solaris, the hu_HU locale uses
    # the locale encoding ISO-8859-2, the thousauds separator jest b'\xA0' oraz it jest
    # decoded jako U+30000020 (an invalid character) by mbstowcs().
    jeżeli sys.platform == 'sunos5':
        old_locale = locale.setlocale(locale.LC_ALL)
        spróbuj:
            locales = []
            dla loc w candidate_locales:
                spróbuj:
                    locale.setlocale(locale.LC_ALL, loc)
                wyjąwszy Error:
                    kontynuuj
                encoding = locale.getpreferredencoding(Nieprawda)
                spróbuj:
                    localeconv()
                wyjąwszy Exception jako err:
                    print("WARNING: Skip locale %s (encoding %s): [%s] %s"
                        % (loc, encoding, type(err), err))
                inaczej:
                    locales.append(loc)
            candidate_locales = locales
        w_końcu:
            locale.setlocale(locale.LC_ALL, old_locale)

    # Workaround dla MSVC6(debug) crash bug
    jeżeli "MSC v.1200" w sys.version:
        def accept(loc):
            a = loc.split(".")
            zwróć not(len(a) == 2 oraz len(a[-1]) >= 9)
        candidate_locales = [loc dla loc w candidate_locales jeżeli accept(loc)]

# List known locale values to test against when available.
# Dict formatted jako ``<locale> : (<decimal_point>, <thousands_sep>)``.  If a
# value jest nie known, use '' .
known_numerics = {
    'en_US': ('.', ','),
    'de_DE' : (',', '.'),
    'fr_FR.UTF-8' : (',', ' '),
    'ps_AF': ('\u066b', '\u066c'),
}

klasa _LocaleTests(unittest.TestCase):

    def setUp(self):
        self.oldlocale = setlocale(LC_ALL)

    def tearDown(self):
        setlocale(LC_ALL, self.oldlocale)

    # Want to know what value was calculated, what it was compared against,
    # what function was used dla the calculation, what type of data was used,
    # the locale that was supposedly set, oraz the actual locale that jest set.
    lc_numeric_err_msg = "%s != %s (%s dla %s; set to %s, using %s)"

    def numeric_tester(self, calc_type, calc_value, data_type, used_locale):
        """Compare calculation against known value, jeżeli available"""
        spróbuj:
            set_locale = setlocale(LC_NUMERIC)
        wyjąwszy Error:
            set_locale = "<not able to determine>"
        known_value = known_numerics.get(used_locale,
                                    ('', ''))[data_type == 'thousands_sep']
        jeżeli known_value oraz calc_value:
            self.assertEqual(calc_value, known_value,
                                self.lc_numeric_err_msg % (
                                    calc_value, known_value,
                                    calc_type, data_type, set_locale,
                                    used_locale))
            zwróć Prawda

    @unittest.skipUnless(nl_langinfo, "nl_langinfo jest nie available")
    def test_lc_numeric_nl_langinfo(self):
        # Test nl_langinfo against known values
        tested = Nieprawda
        dla loc w candidate_locales:
            spróbuj:
                setlocale(LC_NUMERIC, loc)
                setlocale(LC_CTYPE, loc)
            wyjąwszy Error:
                kontynuuj
            dla li, lc w ((RADIXCHAR, "decimal_point"),
                            (THOUSEP, "thousands_sep")):
                jeżeli self.numeric_tester('nl_langinfo', nl_langinfo(li), lc, loc):
                    tested = Prawda
        jeżeli nie tested:
            self.skipTest('no suitable locales')

    def test_lc_numeric_localeconv(self):
        # Test localeconv against known values
        tested = Nieprawda
        dla loc w candidate_locales:
            spróbuj:
                setlocale(LC_NUMERIC, loc)
                setlocale(LC_CTYPE, loc)
            wyjąwszy Error:
                kontynuuj
            formatting = localeconv()
            dla lc w ("decimal_point",
                        "thousands_sep"):
                jeżeli self.numeric_tester('localeconv', formatting[lc], lc, loc):
                    tested = Prawda
        jeżeli nie tested:
            self.skipTest('no suitable locales')

    @unittest.skipUnless(nl_langinfo, "nl_langinfo jest nie available")
    def test_lc_numeric_basic(self):
        # Test nl_langinfo against localeconv
        tested = Nieprawda
        dla loc w candidate_locales:
            spróbuj:
                setlocale(LC_NUMERIC, loc)
                setlocale(LC_CTYPE, loc)
            wyjąwszy Error:
                kontynuuj
            dla li, lc w ((RADIXCHAR, "decimal_point"),
                            (THOUSEP, "thousands_sep")):
                nl_radixchar = nl_langinfo(li)
                li_radixchar = localeconv()[lc]
                spróbuj:
                    set_locale = setlocale(LC_NUMERIC)
                wyjąwszy Error:
                    set_locale = "<not able to determine>"
                self.assertEqual(nl_radixchar, li_radixchar,
                                "%s (nl_langinfo) != %s (localeconv) "
                                "(set to %s, using %s)" % (
                                                nl_radixchar, li_radixchar,
                                                loc, set_locale))
                tested = Prawda
        jeżeli nie tested:
            self.skipTest('no suitable locales')

    def test_float_parsing(self):
        # Bug #1391872: Test whether float parsing jest okay on European
        # locales.
        tested = Nieprawda
        dla loc w candidate_locales:
            spróbuj:
                setlocale(LC_NUMERIC, loc)
                setlocale(LC_CTYPE, loc)
            wyjąwszy Error:
                kontynuuj

            # Ignore buggy locale databases. (Mac OS 10.4 oraz some other BSDs)
            jeżeli loc == 'eu_ES' oraz localeconv()['decimal_point'] == "' ":
                kontynuuj

            self.assertEqual(int(eval('3.14') * 100), 314,
                                "using eval('3.14') failed dla %s" % loc)
            self.assertEqual(int(float('3.14') * 100), 314,
                                "using float('3.14') failed dla %s" % loc)
            jeżeli localeconv()['decimal_point'] != '.':
                self.assertRaises(ValueError, float,
                                  localeconv()['decimal_point'].join(['1', '23']))
            tested = Prawda
        jeżeli nie tested:
            self.skipTest('no suitable locales')


jeżeli __name__ == '__main__':
    unittest.main()
