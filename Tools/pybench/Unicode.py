spróbuj:
    unicode
wyjąwszy NameError:
    podnieś ImportError

z pybench zaimportuj Test

klasa ConcatUnicode(Test):

    version = 2.0
    operations = 10 * 5
    rounds = 60000

    def test(self):

        # Make sure the strings are *not* interned
        s = unicode(u''.join(map(str,range(100))))
        t = unicode(u''.join(map(str,range(1,101))))

        dla i w range(self.rounds):
            t + s
            t + s
            t + s
            t + s
            t + s

            t + s
            t + s
            t + s
            t + s
            t + s

            t + s
            t + s
            t + s
            t + s
            t + s

            t + s
            t + s
            t + s
            t + s
            t + s

            t + s
            t + s
            t + s
            t + s
            t + s

            t + s
            t + s
            t + s
            t + s
            t + s

            t + s
            t + s
            t + s
            t + s
            t + s

            t + s
            t + s
            t + s
            t + s
            t + s

            t + s
            t + s
            t + s
            t + s
            t + s

            t + s
            t + s
            t + s
            t + s
            t + s

    def calibrate(self):

        s = unicode(u''.join(map(str,range(100))))
        t = unicode(u''.join(map(str,range(1,101))))

        dla i w range(self.rounds):
            dalej


klasa CompareUnicode(Test):

    version = 2.0
    operations = 10 * 5
    rounds = 150000

    def test(self):

        # Make sure the strings are *not* interned
        s = unicode(u''.join(map(str,range(10))))
        t = unicode(u''.join(map(str,range(10))) + "abc")

        dla i w range(self.rounds):
            t < s
            t > s
            t == s
            t > s
            t < s

            t < s
            t > s
            t == s
            t > s
            t < s

            t < s
            t > s
            t == s
            t > s
            t < s

            t < s
            t > s
            t == s
            t > s
            t < s

            t < s
            t > s
            t == s
            t > s
            t < s

            t < s
            t > s
            t == s
            t > s
            t < s

            t < s
            t > s
            t == s
            t > s
            t < s

            t < s
            t > s
            t == s
            t > s
            t < s

            t < s
            t > s
            t == s
            t > s
            t < s

            t < s
            t > s
            t == s
            t > s
            t < s

    def calibrate(self):

        s = unicode(u''.join(map(str,range(10))))
        t = unicode(u''.join(map(str,range(10))) + "abc")

        dla i w range(self.rounds):
            dalej


klasa CreateUnicodeWithConcat(Test):

    version = 2.0
    operations = 10 * 5
    rounds = 80000

    def test(self):

        dla i w range(self.rounds):
            s = u'om'
            s = s + u'xbx'
            s = s + u'xcx'
            s = s + u'xdx'
            s = s + u'xex'

            s = s + u'xax'
            s = s + u'xbx'
            s = s + u'xcx'
            s = s + u'xdx'
            s = s + u'xex'

            s = s + u'xax'
            s = s + u'xbx'
            s = s + u'xcx'
            s = s + u'xdx'
            s = s + u'xex'

            s = s + u'xax'
            s = s + u'xbx'
            s = s + u'xcx'
            s = s + u'xdx'
            s = s + u'xex'

            s = s + u'xax'
            s = s + u'xbx'
            s = s + u'xcx'
            s = s + u'xdx'
            s = s + u'xex'

            s = s + u'xax'
            s = s + u'xbx'
            s = s + u'xcx'
            s = s + u'xdx'
            s = s + u'xex'

            s = s + u'xax'
            s = s + u'xbx'
            s = s + u'xcx'
            s = s + u'xdx'
            s = s + u'xex'

            s = s + u'xax'
            s = s + u'xbx'
            s = s + u'xcx'
            s = s + u'xdx'
            s = s + u'xex'

            s = s + u'xax'
            s = s + u'xbx'
            s = s + u'xcx'
            s = s + u'xdx'
            s = s + u'xex'

            s = s + u'xax'
            s = s + u'xbx'
            s = s + u'xcx'
            s = s + u'xdx'
            s = s + u'xex'

    def calibrate(self):

        dla i w range(self.rounds):
            dalej


klasa UnicodeSlicing(Test):

    version = 2.0
    operations = 5 * 7
    rounds = 140000

    def test(self):

        s = unicode(u''.join(map(str,range(100))))

        dla i w range(self.rounds):

            s[50:]
            s[:25]
            s[50:55]
            s[-1:]
            s[:1]
            s[2:]
            s[11:-11]

            s[50:]
            s[:25]
            s[50:55]
            s[-1:]
            s[:1]
            s[2:]
            s[11:-11]

            s[50:]
            s[:25]
            s[50:55]
            s[-1:]
            s[:1]
            s[2:]
            s[11:-11]

            s[50:]
            s[:25]
            s[50:55]
            s[-1:]
            s[:1]
            s[2:]
            s[11:-11]

            s[50:]
            s[:25]
            s[50:55]
            s[-1:]
            s[:1]
            s[2:]
            s[11:-11]

    def calibrate(self):

        s = unicode(u''.join(map(str,range(100))))

        dla i w range(self.rounds):
            dalej

### String methods

klasa UnicodeMappings(Test):

    version = 2.0
    operations = 3 * (5 + 4 + 2 + 1)
    rounds = 10000

    def test(self):

        s = u''.join(map(unichr,range(20)))
        t = u''.join(map(unichr,range(100)))
        u = u''.join(map(unichr,range(500)))
        v = u''.join(map(unichr,range(1000)))

        dla i w range(self.rounds):

            s.lower()
            s.lower()
            s.lower()
            s.lower()
            s.lower()

            s.upper()
            s.upper()
            s.upper()
            s.upper()
            s.upper()

            s.title()
            s.title()
            s.title()
            s.title()
            s.title()

            t.lower()
            t.lower()
            t.lower()
            t.lower()

            t.upper()
            t.upper()
            t.upper()
            t.upper()

            t.title()
            t.title()
            t.title()
            t.title()

            u.lower()
            u.lower()

            u.upper()
            u.upper()

            u.title()
            u.title()

            v.lower()

            v.upper()

            v.title()

    def calibrate(self):

        s = u''.join(map(unichr,range(20)))
        t = u''.join(map(unichr,range(100)))
        u = u''.join(map(unichr,range(500)))
        v = u''.join(map(unichr,range(1000)))

        dla i w range(self.rounds):
            dalej

klasa UnicodePredicates(Test):

    version = 2.0
    operations = 5 * 9
    rounds = 120000

    def test(self):

        data = (u'abc', u'123', u'   ', u'\u1234\u2345\u3456', u'\uFFFF'*10)
        len_data = len(data)

        dla i w range(self.rounds):
            s = data[i % len_data]

            s.isalnum()
            s.isalpha()
            s.isdecimal()
            s.isdigit()
            s.islower()
            s.isnumeric()
            s.isspace()
            s.istitle()
            s.isupper()

            s.isalnum()
            s.isalpha()
            s.isdecimal()
            s.isdigit()
            s.islower()
            s.isnumeric()
            s.isspace()
            s.istitle()
            s.isupper()

            s.isalnum()
            s.isalpha()
            s.isdecimal()
            s.isdigit()
            s.islower()
            s.isnumeric()
            s.isspace()
            s.istitle()
            s.isupper()

            s.isalnum()
            s.isalpha()
            s.isdecimal()
            s.isdigit()
            s.islower()
            s.isnumeric()
            s.isspace()
            s.istitle()
            s.isupper()

            s.isalnum()
            s.isalpha()
            s.isdecimal()
            s.isdigit()
            s.islower()
            s.isnumeric()
            s.isspace()
            s.istitle()
            s.isupper()

    def calibrate(self):

        data = (u'abc', u'123', u'   ', u'\u1234\u2345\u3456', u'\uFFFF'*10)
        len_data = len(data)

        dla i w range(self.rounds):
            s = data[i % len_data]

spróbuj:
    zaimportuj unicodedata
wyjąwszy ImportError:
    dalej
inaczej:
    klasa UnicodeProperties(Test):

        version = 2.0
        operations = 5 * 8
        rounds = 100000

        def test(self):

            data = (u'a', u'1', u' ', u'\u1234', u'\uFFFF')
            len_data = len(data)
            digit = unicodedata.digit
            numeric = unicodedata.numeric
            decimal = unicodedata.decimal
            category = unicodedata.category
            bidirectional = unicodedata.bidirectional
            decomposition = unicodedata.decomposition
            mirrored = unicodedata.mirrored
            combining = unicodedata.combining

            dla i w range(self.rounds):

                c = data[i % len_data]

                digit(c, Nic)
                numeric(c, Nic)
                decimal(c, Nic)
                category(c)
                bidirectional(c)
                decomposition(c)
                mirrored(c)
                combining(c)

                digit(c, Nic)
                numeric(c, Nic)
                decimal(c, Nic)
                category(c)
                bidirectional(c)
                decomposition(c)
                mirrored(c)
                combining(c)

                digit(c, Nic)
                numeric(c, Nic)
                decimal(c, Nic)
                category(c)
                bidirectional(c)
                decomposition(c)
                mirrored(c)
                combining(c)

                digit(c, Nic)
                numeric(c, Nic)
                decimal(c, Nic)
                category(c)
                bidirectional(c)
                decomposition(c)
                mirrored(c)
                combining(c)

                digit(c, Nic)
                numeric(c, Nic)
                decimal(c, Nic)
                category(c)
                bidirectional(c)
                decomposition(c)
                mirrored(c)
                combining(c)

        def calibrate(self):

            data = (u'a', u'1', u' ', u'\u1234', u'\uFFFF')
            len_data = len(data)
            digit = unicodedata.digit
            numeric = unicodedata.numeric
            decimal = unicodedata.decimal
            category = unicodedata.category
            bidirectional = unicodedata.bidirectional
            decomposition = unicodedata.decomposition
            mirrored = unicodedata.mirrored
            combining = unicodedata.combining

            dla i w range(self.rounds):

                c = data[i % len_data]
