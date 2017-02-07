z pybench zaimportuj Test
zaimportuj sys

spróbuj:
    intern
wyjąwszy NameError:
    intern = sys.intern


klasa ConcatStrings(Test):

    version = 2.0
    operations = 10 * 5
    rounds = 100000

    def test(self):

        # Make sure the strings are *not* interned
        s = ''.join(map(str,range(100)))
        t = ''.join(map(str,range(1,101)))

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

        s = ''.join(map(str,range(100)))
        t = ''.join(map(str,range(1,101)))

        dla i w range(self.rounds):
            dalej


klasa CompareStrings(Test):

    version = 2.0
    operations = 10 * 5
    rounds = 200000

    def test(self):

        # Make sure the strings are *not* interned
        s = ''.join(map(str,range(10)))
        t = ''.join(map(str,range(10))) + "abc"

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

        s = ''.join(map(str,range(10)))
        t = ''.join(map(str,range(10))) + "abc"

        dla i w range(self.rounds):
            dalej


klasa CompareInternedStrings(Test):

    version = 2.0
    operations = 10 * 5
    rounds = 300000

    def test(self):

        # Make sure the strings *are* interned
        s = intern(''.join(map(str,range(10))))
        t = s

        dla i w range(self.rounds):
            t == s
            t == s
            t >= s
            t > s
            t < s

            t == s
            t == s
            t >= s
            t > s
            t < s

            t == s
            t == s
            t >= s
            t > s
            t < s

            t == s
            t == s
            t >= s
            t > s
            t < s

            t == s
            t == s
            t >= s
            t > s
            t < s

            t == s
            t == s
            t >= s
            t > s
            t < s

            t == s
            t == s
            t >= s
            t > s
            t < s

            t == s
            t == s
            t >= s
            t > s
            t < s

            t == s
            t == s
            t >= s
            t > s
            t < s

            t == s
            t == s
            t >= s
            t > s
            t < s

    def calibrate(self):

        s = intern(''.join(map(str,range(10))))
        t = s

        dla i w range(self.rounds):
            dalej


klasa CreateStringsWithConcat(Test):

    version = 2.0
    operations = 10 * 5
    rounds = 200000

    def test(self):

        dla i w range(self.rounds):
            s = 'om'
            s = s + 'xbx'
            s = s + 'xcx'
            s = s + 'xdx'
            s = s + 'xex'

            s = s + 'xax'
            s = s + 'xbx'
            s = s + 'xcx'
            s = s + 'xdx'
            s = s + 'xex'

            s = s + 'xax'
            s = s + 'xbx'
            s = s + 'xcx'
            s = s + 'xdx'
            s = s + 'xex'

            s = s + 'xax'
            s = s + 'xbx'
            s = s + 'xcx'
            s = s + 'xdx'
            s = s + 'xex'

            s = s + 'xax'
            s = s + 'xbx'
            s = s + 'xcx'
            s = s + 'xdx'
            s = s + 'xex'

            s = s + 'xax'
            s = s + 'xbx'
            s = s + 'xcx'
            s = s + 'xdx'
            s = s + 'xex'

            s = s + 'xax'
            s = s + 'xbx'
            s = s + 'xcx'
            s = s + 'xdx'
            s = s + 'xex'

            s = s + 'xax'
            s = s + 'xbx'
            s = s + 'xcx'
            s = s + 'xdx'
            s = s + 'xex'

            s = s + 'xax'
            s = s + 'xbx'
            s = s + 'xcx'
            s = s + 'xdx'
            s = s + 'xex'

            s = s + 'xax'
            s = s + 'xbx'
            s = s + 'xcx'
            s = s + 'xdx'
            s = s + 'xex'

    def calibrate(self):

        dla i w range(self.rounds):
            dalej


klasa StringSlicing(Test):

    version = 2.0
    operations = 5 * 7
    rounds = 160000

    def test(self):

        s = ''.join(map(str,range(100)))

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

        s = ''.join(map(str,range(100)))

        dla i w range(self.rounds):
            dalej

### String methods

jeżeli hasattr('', 'lower'):

    klasa StringMappings(Test):

        version = 2.0
        operations = 3 * (5 + 4 + 2 + 1)
        rounds = 70000

        def test(self):

            s = ''.join(map(chr,range(20)))
            t = ''.join(map(chr,range(50)))
            u = ''.join(map(chr,range(100)))
            v = ''.join(map(chr,range(256)))

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

            s = ''.join(map(chr,range(20)))
            t = ''.join(map(chr,range(50)))
            u = ''.join(map(chr,range(100)))
            v = ''.join(map(chr,range(256)))

            dla i w range(self.rounds):
                dalej

    klasa StringPredicates(Test):

        version = 2.0
        operations = 10 * 7
        rounds = 100000

        def test(self):

            data = ('abc', '123', '   ', '\xe4\xf6\xfc', '\xdf'*10)
            len_data = len(data)

            dla i w range(self.rounds):
                s = data[i % len_data]

                s.isalnum()
                s.isalpha()
                s.isdigit()
                s.islower()
                s.isspace()
                s.istitle()
                s.isupper()

                s.isalnum()
                s.isalpha()
                s.isdigit()
                s.islower()
                s.isspace()
                s.istitle()
                s.isupper()

                s.isalnum()
                s.isalpha()
                s.isdigit()
                s.islower()
                s.isspace()
                s.istitle()
                s.isupper()

                s.isalnum()
                s.isalpha()
                s.isdigit()
                s.islower()
                s.isspace()
                s.istitle()
                s.isupper()

                s.isalnum()
                s.isalpha()
                s.isdigit()
                s.islower()
                s.isspace()
                s.istitle()
                s.isupper()

                s.isalnum()
                s.isalpha()
                s.isdigit()
                s.islower()
                s.isspace()
                s.istitle()
                s.isupper()

                s.isalnum()
                s.isalpha()
                s.isdigit()
                s.islower()
                s.isspace()
                s.istitle()
                s.isupper()

                s.isalnum()
                s.isalpha()
                s.isdigit()
                s.islower()
                s.isspace()
                s.istitle()
                s.isupper()

                s.isalnum()
                s.isalpha()
                s.isdigit()
                s.islower()
                s.isspace()
                s.istitle()
                s.isupper()

                s.isalnum()
                s.isalpha()
                s.isdigit()
                s.islower()
                s.isspace()
                s.istitle()
                s.isupper()

        def calibrate(self):

            data = ('abc', '123', '   ', '\u1234\u2345\u3456', '\uFFFF'*10)
            data = ('abc', '123', '   ', '\xe4\xf6\xfc', '\xdf'*10)
            len_data = len(data)

            dla i w range(self.rounds):
                s = data[i % len_data]
