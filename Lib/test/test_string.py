zaimportuj unittest, string


klasa ModuleTest(unittest.TestCase):

    def test_attrs(self):
        # While the exact order of the items w these attributes jest nie
        # technically part of the "language spec", w practice there jest almost
        # certainly user code that depends on the order, so de-facto it *is*
        # part of the spec.
        self.assertEqual(string.whitespace, ' \t\n\r\x0b\x0c')
        self.assertEqual(string.ascii_lowercase, 'abcdefghijklmnopqrstuvwxyz')
        self.assertEqual(string.ascii_uppercase, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        self.assertEqual(string.ascii_letters, string.ascii_lowercase + string.ascii_uppercase)
        self.assertEqual(string.digits, '0123456789')
        self.assertEqual(string.hexdigits, string.digits + 'abcdefABCDEF')
        self.assertEqual(string.octdigits, '01234567')
        self.assertEqual(string.punctuation, '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')
        self.assertEqual(string.printable, string.digits + string.ascii_lowercase + string.ascii_uppercase + string.punctuation + string.whitespace)

    def test_capwords(self):
        self.assertEqual(string.capwords('abc def ghi'), 'Abc Def Ghi')
        self.assertEqual(string.capwords('abc\tdef\nghi'), 'Abc Def Ghi')
        self.assertEqual(string.capwords('abc\t   def  \nghi'), 'Abc Def Ghi')
        self.assertEqual(string.capwords('ABC DEF GHI'), 'Abc Def Ghi')
        self.assertEqual(string.capwords('ABC-DEF-GHI', '-'), 'Abc-Def-Ghi')
        self.assertEqual(string.capwords('ABC-def DEF-ghi GHI'), 'Abc-def Def-ghi Ghi')
        self.assertEqual(string.capwords('   aBc  DeF   '), 'Abc Def')
        self.assertEqual(string.capwords('\taBc\tDeF\t'), 'Abc Def')
        self.assertEqual(string.capwords('\taBc\tDeF\t', '\t'), '\tAbc\tDef\t')

    def test_basic_formatter(self):
        fmt = string.Formatter()
        self.assertEqual(fmt.format("foo"), "foo")
        self.assertEqual(fmt.format("foo{0}", "bar"), "foobar")
        self.assertEqual(fmt.format("foo{1}{0}-{1}", "bar", 6), "foo6bar-6")
        self.assertRaises(TypeError, fmt.format)
        self.assertRaises(TypeError, string.Formatter.format)

    def test_format_keyword_arguments(self):
        fmt = string.Formatter()
        self.assertEqual(fmt.format("-{arg}-", arg='test'), '-test-')
        self.assertRaises(KeyError, fmt.format, "-{arg}-")
        self.assertEqual(fmt.format("-{self}-", self='test'), '-test-')
        self.assertRaises(KeyError, fmt.format, "-{self}-")
        self.assertEqual(fmt.format("-{format_string}-", format_string='test'),
                         '-test-')
        self.assertRaises(KeyError, fmt.format, "-{format_string}-")
        przy self.assertWarnsRegex(DeprecationWarning, "format_string"):
            self.assertEqual(fmt.format(arg='test', format_string="-{arg}-"),
                             '-test-')

    def test_auto_numbering(self):
        fmt = string.Formatter()
        self.assertEqual(fmt.format('foo{}{}', 'bar', 6),
                         'foo{}{}'.format('bar', 6))
        self.assertEqual(fmt.format('foo{1}{num}{1}', Nic, 'bar', num=6),
                         'foo{1}{num}{1}'.format(Nic, 'bar', num=6))
        self.assertEqual(fmt.format('{:^{}}', 'bar', 6),
                         '{:^{}}'.format('bar', 6))
        self.assertEqual(fmt.format('{:^{pad}}{}', 'foo', 'bar', pad=6),
                         '{:^{pad}}{}'.format('foo', 'bar', pad=6))

        przy self.assertRaises(ValueError):
            fmt.format('foo{1}{}', 'bar', 6)

        przy self.assertRaises(ValueError):
            fmt.format('foo{}{1}', 'bar', 6)

    def test_conversion_specifiers(self):
        fmt = string.Formatter()
        self.assertEqual(fmt.format("-{arg!r}-", arg='test'), "-'test'-")
        self.assertEqual(fmt.format("{0!s}", 'test'), 'test')
        self.assertRaises(ValueError, fmt.format, "{0!h}", 'test')
        # issue13579
        self.assertEqual(fmt.format("{0!a}", 42), '42')
        self.assertEqual(fmt.format("{0!a}",  string.ascii_letters),
            "'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'")
        self.assertEqual(fmt.format("{0!a}",  chr(255)), "'\\xff'")
        self.assertEqual(fmt.format("{0!a}",  chr(256)), "'\\u0100'")

    def test_name_lookup(self):
        fmt = string.Formatter()
        klasa AnyAttr:
            def __getattr__(self, attr):
                zwróć attr
        x = AnyAttr()
        self.assertEqual(fmt.format("{0.lumber}{0.jack}", x), 'lumberjack')
        przy self.assertRaises(AttributeError):
            fmt.format("{0.lumber}{0.jack}", '')

    def test_index_lookup(self):
        fmt = string.Formatter()
        lookup = ["eggs", "and", "spam"]
        self.assertEqual(fmt.format("{0[2]}{0[0]}", lookup), 'spameggs')
        przy self.assertRaises(IndexError):
            fmt.format("{0[2]}{0[0]}", [])
        przy self.assertRaises(KeyError):
            fmt.format("{0[2]}{0[0]}", {})

    def test_override_get_value(self):
        klasa NamespaceFormatter(string.Formatter):
            def __init__(self, namespace={}):
                string.Formatter.__init__(self)
                self.namespace = namespace

            def get_value(self, key, args, kwds):
                jeżeli isinstance(key, str):
                    spróbuj:
                        # Check explicitly dalejed arguments first
                        zwróć kwds[key]
                    wyjąwszy KeyError:
                        zwróć self.namespace[key]
                inaczej:
                    string.Formatter.get_value(key, args, kwds)

        fmt = NamespaceFormatter({'greeting':'hello'})
        self.assertEqual(fmt.format("{greeting}, world!"), 'hello, world!')


    def test_override_format_field(self):
        klasa CallFormatter(string.Formatter):
            def format_field(self, value, format_spec):
                zwróć format(value(), format_spec)

        fmt = CallFormatter()
        self.assertEqual(fmt.format('*{0}*', lambda : 'result'), '*result*')


    def test_override_convert_field(self):
        klasa XFormatter(string.Formatter):
            def convert_field(self, value, conversion):
                jeżeli conversion == 'x':
                    zwróć Nic
                zwróć super().convert_field(value, conversion)

        fmt = XFormatter()
        self.assertEqual(fmt.format("{0!r}:{0!x}", 'foo', 'foo'), "'foo':Nic")


    def test_override_parse(self):
        klasa BarFormatter(string.Formatter):
            # returns an iterable that contains tuples of the form:
            # (literal_text, field_name, format_spec, conversion)
            def parse(self, format_string):
                dla field w format_string.split('|'):
                    jeżeli field[0] == '+':
                        # it's markup
                        field_name, _, format_spec = field[1:].partition(':')
                        uzyskaj '', field_name, format_spec, Nic
                    inaczej:
                        uzyskaj field, Nic, Nic, Nic

        fmt = BarFormatter()
        self.assertEqual(fmt.format('*|+0:^10s|*', 'foo'), '*   foo    *')

    def test_check_unused_args(self):
        klasa CheckAllUsedFormatter(string.Formatter):
            def check_unused_args(self, used_args, args, kwargs):
                # Track which arguments actually got used
                unused_args = set(kwargs.keys())
                unused_args.update(range(0, len(args)))

                dla arg w used_args:
                    unused_args.remove(arg)

                jeżeli unused_args:
                    podnieś ValueError("unused arguments")

        fmt = CheckAllUsedFormatter()
        self.assertEqual(fmt.format("{0}", 10), "10")
        self.assertEqual(fmt.format("{0}{i}", 10, i=100), "10100")
        self.assertEqual(fmt.format("{0}{i}{1}", 10, 20, i=100), "1010020")
        self.assertRaises(ValueError, fmt.format, "{0}{i}{1}", 10, 20, i=100, j=0)
        self.assertRaises(ValueError, fmt.format, "{0}", 10, 20)
        self.assertRaises(ValueError, fmt.format, "{0}", 10, 20, i=100)
        self.assertRaises(ValueError, fmt.format, "{i}", 10, 20, i=100)

    def test_vformat_recursion_limit(self):
        fmt = string.Formatter()
        args = ()
        kwargs = dict(i=100)
        przy self.assertRaises(ValueError) jako err:
            fmt._vformat("{i}", args, kwargs, set(), -1)
        self.assertIn("recursion", str(err.exception))


jeżeli __name__ == "__main__":
    unittest.main()
