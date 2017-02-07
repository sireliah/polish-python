"""
Common tests shared by test_unicode, test_userstring oraz test_string.
"""

zaimportuj unittest, string, sys, struct
z test zaimportuj support
z collections zaimportuj UserList

klasa Sequence:
    def __init__(self, seq='wxyz'): self.seq = seq
    def __len__(self): zwróć len(self.seq)
    def __getitem__(self, i): zwróć self.seq[i]

klasa BadSeq1(Sequence):
    def __init__(self): self.seq = [7, 'hello', 123]
    def __str__(self): zwróć '{0} {1} {2}'.format(*self.seq)

klasa BadSeq2(Sequence):
    def __init__(self): self.seq = ['a', 'b', 'c']
    def __len__(self): zwróć 8

klasa BaseTest:
    # These tests are dla buffers of values (bytes) oraz nie
    # specific to character interpretation, used dla bytes objects
    # oraz various string implementations

    # The type to be tested
    # Change w subclasses to change the behaviour of fixtesttype()
    type2test = Nic

    # Whether the "contained items" of the container are integers w
    # range(0, 256) (i.e. bytes, bytearray) albo strings of length 1
    # (str)
    contains_bytes = Nieprawda

    # All tests dalej their arguments to the testing methods
    # jako str objects. fixtesttype() can be used to propagate
    # these arguments to the appropriate type
    def fixtype(self, obj):
        jeżeli isinstance(obj, str):
            zwróć self.__class__.type2test(obj)
        albo_inaczej isinstance(obj, list):
            zwróć [self.fixtype(x) dla x w obj]
        albo_inaczej isinstance(obj, tuple):
            zwróć tuple([self.fixtype(x) dla x w obj])
        albo_inaczej isinstance(obj, dict):
            zwróć dict([
               (self.fixtype(key), self.fixtype(value))
               dla (key, value) w obj.items()
            ])
        inaczej:
            zwróć obj

    # check that obj.method(*args) returns result
    def checkequal(self, result, obj, methodname, *args, **kwargs):
        result = self.fixtype(result)
        obj = self.fixtype(obj)
        args = self.fixtype(args)
        kwargs = {k: self.fixtype(v) dla k,v w kwargs.items()}
        realresult = getattr(obj, methodname)(*args, **kwargs)
        self.assertEqual(
            result,
            realresult
        )
        # jeżeli the original jest returned make sure that
        # this doesn't happen przy subclasses
        jeżeli obj jest realresult:
            spróbuj:
                klasa subtype(self.__class__.type2test):
                    dalej
            wyjąwszy TypeError:
                dalej  # Skip this jeżeli we can't subclass
            inaczej:
                obj = subtype(obj)
                realresult = getattr(obj, methodname)(*args)
                self.assertIsNot(obj, realresult)

    # check that obj.method(*args) podnieśs exc
    def checkraises(self, exc, obj, methodname, *args):
        obj = self.fixtype(obj)
        args = self.fixtype(args)
        przy self.assertRaises(exc) jako cm:
            getattr(obj, methodname)(*args)
        self.assertNotEqual(str(cm.exception), '')

    # call obj.method(*args) without any checks
    def checkcall(self, obj, methodname, *args):
        obj = self.fixtype(obj)
        args = self.fixtype(args)
        getattr(obj, methodname)(*args)

    def test_count(self):
        self.checkequal(3, 'aaa', 'count', 'a')
        self.checkequal(0, 'aaa', 'count', 'b')
        self.checkequal(3, 'aaa', 'count', 'a')
        self.checkequal(0, 'aaa', 'count', 'b')
        self.checkequal(3, 'aaa', 'count', 'a')
        self.checkequal(0, 'aaa', 'count', 'b')
        self.checkequal(0, 'aaa', 'count', 'b')
        self.checkequal(2, 'aaa', 'count', 'a', 1)
        self.checkequal(0, 'aaa', 'count', 'a', 10)
        self.checkequal(1, 'aaa', 'count', 'a', -1)
        self.checkequal(3, 'aaa', 'count', 'a', -10)
        self.checkequal(1, 'aaa', 'count', 'a', 0, 1)
        self.checkequal(3, 'aaa', 'count', 'a', 0, 10)
        self.checkequal(2, 'aaa', 'count', 'a', 0, -1)
        self.checkequal(0, 'aaa', 'count', 'a', 0, -10)
        self.checkequal(3, 'aaa', 'count', '', 1)
        self.checkequal(1, 'aaa', 'count', '', 3)
        self.checkequal(0, 'aaa', 'count', '', 10)
        self.checkequal(2, 'aaa', 'count', '', -1)
        self.checkequal(4, 'aaa', 'count', '', -10)

        self.checkequal(1, '', 'count', '')
        self.checkequal(0, '', 'count', '', 1, 1)
        self.checkequal(0, '', 'count', '', sys.maxsize, 0)

        self.checkequal(0, '', 'count', 'xx')
        self.checkequal(0, '', 'count', 'xx', 1, 1)
        self.checkequal(0, '', 'count', 'xx', sys.maxsize, 0)

        self.checkraises(TypeError, 'hello', 'count')

        jeżeli self.contains_bytes:
            self.checkequal(0, 'hello', 'count', 42)
        inaczej:
            self.checkraises(TypeError, 'hello', 'count', 42)

        # For a variety of combinations,
        #    verify that str.count() matches an equivalent function
        #    replacing all occurrences oraz then differencing the string lengths
        charset = ['', 'a', 'b']
        digits = 7
        base = len(charset)
        teststrings = set()
        dla i w range(base ** digits):
            entry = []
            dla j w range(digits):
                i, m = divmod(i, base)
                entry.append(charset[m])
            teststrings.add(''.join(entry))
        teststrings = [self.fixtype(ts) dla ts w teststrings]
        dla i w teststrings:
            n = len(i)
            dla j w teststrings:
                r1 = i.count(j)
                jeżeli j:
                    r2, rem = divmod(n - len(i.replace(j, self.fixtype(''))),
                                     len(j))
                inaczej:
                    r2, rem = len(i)+1, 0
                jeżeli rem albo r1 != r2:
                    self.assertEqual(rem, 0, '%s != 0 dla %s' % (rem, i))
                    self.assertEqual(r1, r2, '%s != %s dla %s' % (r1, r2, i))

    def test_find(self):
        self.checkequal(0, 'abcdefghiabc', 'find', 'abc')
        self.checkequal(9, 'abcdefghiabc', 'find', 'abc', 1)
        self.checkequal(-1, 'abcdefghiabc', 'find', 'def', 4)

        self.checkequal(0, 'abc', 'find', '', 0)
        self.checkequal(3, 'abc', 'find', '', 3)
        self.checkequal(-1, 'abc', 'find', '', 4)

        # to check the ability to dalej Nic jako defaults
        self.checkequal( 2, 'rrarrrrrrrrra', 'find', 'a')
        self.checkequal(12, 'rrarrrrrrrrra', 'find', 'a', 4)
        self.checkequal(-1, 'rrarrrrrrrrra', 'find', 'a', 4, 6)
        self.checkequal(12, 'rrarrrrrrrrra', 'find', 'a', 4, Nic)
        self.checkequal( 2, 'rrarrrrrrrrra', 'find', 'a', Nic, 6)

        self.checkraises(TypeError, 'hello', 'find')

        jeżeli self.contains_bytes:
            self.checkequal(-1, 'hello', 'find', 42)
        inaczej:
            self.checkraises(TypeError, 'hello', 'find', 42)

        self.checkequal(0, '', 'find', '')
        self.checkequal(-1, '', 'find', '', 1, 1)
        self.checkequal(-1, '', 'find', '', sys.maxsize, 0)

        self.checkequal(-1, '', 'find', 'xx')
        self.checkequal(-1, '', 'find', 'xx', 1, 1)
        self.checkequal(-1, '', 'find', 'xx', sys.maxsize, 0)

        # issue 7458
        self.checkequal(-1, 'ab', 'find', 'xxx', sys.maxsize + 1, 0)

        # For a variety of combinations,
        #    verify that str.find() matches __contains__
        #    oraz that the found substring jest really at that location
        charset = ['', 'a', 'b', 'c']
        digits = 5
        base = len(charset)
        teststrings = set()
        dla i w range(base ** digits):
            entry = []
            dla j w range(digits):
                i, m = divmod(i, base)
                entry.append(charset[m])
            teststrings.add(''.join(entry))
        teststrings = [self.fixtype(ts) dla ts w teststrings]
        dla i w teststrings:
            dla j w teststrings:
                loc = i.find(j)
                r1 = (loc != -1)
                r2 = j w i
                self.assertEqual(r1, r2)
                jeżeli loc != -1:
                    self.assertEqual(i[loc:loc+len(j)], j)

    def test_rfind(self):
        self.checkequal(9,  'abcdefghiabc', 'rfind', 'abc')
        self.checkequal(12, 'abcdefghiabc', 'rfind', '')
        self.checkequal(0, 'abcdefghiabc', 'rfind', 'abcd')
        self.checkequal(-1, 'abcdefghiabc', 'rfind', 'abcz')

        self.checkequal(3, 'abc', 'rfind', '', 0)
        self.checkequal(3, 'abc', 'rfind', '', 3)
        self.checkequal(-1, 'abc', 'rfind', '', 4)

        # to check the ability to dalej Nic jako defaults
        self.checkequal(12, 'rrarrrrrrrrra', 'rfind', 'a')
        self.checkequal(12, 'rrarrrrrrrrra', 'rfind', 'a', 4)
        self.checkequal(-1, 'rrarrrrrrrrra', 'rfind', 'a', 4, 6)
        self.checkequal(12, 'rrarrrrrrrrra', 'rfind', 'a', 4, Nic)
        self.checkequal( 2, 'rrarrrrrrrrra', 'rfind', 'a', Nic, 6)

        self.checkraises(TypeError, 'hello', 'rfind')

        jeżeli self.contains_bytes:
            self.checkequal(-1, 'hello', 'rfind', 42)
        inaczej:
            self.checkraises(TypeError, 'hello', 'rfind', 42)

        # For a variety of combinations,
        #    verify that str.rfind() matches __contains__
        #    oraz that the found substring jest really at that location
        charset = ['', 'a', 'b', 'c']
        digits = 5
        base = len(charset)
        teststrings = set()
        dla i w range(base ** digits):
            entry = []
            dla j w range(digits):
                i, m = divmod(i, base)
                entry.append(charset[m])
            teststrings.add(''.join(entry))
        teststrings = [self.fixtype(ts) dla ts w teststrings]
        dla i w teststrings:
            dla j w teststrings:
                loc = i.rfind(j)
                r1 = (loc != -1)
                r2 = j w i
                self.assertEqual(r1, r2)
                jeżeli loc != -1:
                    self.assertEqual(i[loc:loc+len(j)], j)

        # issue 7458
        self.checkequal(-1, 'ab', 'rfind', 'xxx', sys.maxsize + 1, 0)

        # issue #15534
        self.checkequal(0, '<......\u043c...', "rfind", "<")

    def test_index(self):
        self.checkequal(0, 'abcdefghiabc', 'index', '')
        self.checkequal(3, 'abcdefghiabc', 'index', 'def')
        self.checkequal(0, 'abcdefghiabc', 'index', 'abc')
        self.checkequal(9, 'abcdefghiabc', 'index', 'abc', 1)

        self.checkraises(ValueError, 'abcdefghiabc', 'index', 'hib')
        self.checkraises(ValueError, 'abcdefghiab', 'index', 'abc', 1)
        self.checkraises(ValueError, 'abcdefghi', 'index', 'ghi', 8)
        self.checkraises(ValueError, 'abcdefghi', 'index', 'ghi', -1)

        # to check the ability to dalej Nic jako defaults
        self.checkequal( 2, 'rrarrrrrrrrra', 'index', 'a')
        self.checkequal(12, 'rrarrrrrrrrra', 'index', 'a', 4)
        self.checkraises(ValueError, 'rrarrrrrrrrra', 'index', 'a', 4, 6)
        self.checkequal(12, 'rrarrrrrrrrra', 'index', 'a', 4, Nic)
        self.checkequal( 2, 'rrarrrrrrrrra', 'index', 'a', Nic, 6)

        self.checkraises(TypeError, 'hello', 'index')

        jeżeli self.contains_bytes:
            self.checkraises(ValueError, 'hello', 'index', 42)
        inaczej:
            self.checkraises(TypeError, 'hello', 'index', 42)

    def test_rindex(self):
        self.checkequal(12, 'abcdefghiabc', 'rindex', '')
        self.checkequal(3,  'abcdefghiabc', 'rindex', 'def')
        self.checkequal(9,  'abcdefghiabc', 'rindex', 'abc')
        self.checkequal(0,  'abcdefghiabc', 'rindex', 'abc', 0, -1)

        self.checkraises(ValueError, 'abcdefghiabc', 'rindex', 'hib')
        self.checkraises(ValueError, 'defghiabc', 'rindex', 'def', 1)
        self.checkraises(ValueError, 'defghiabc', 'rindex', 'abc', 0, -1)
        self.checkraises(ValueError, 'abcdefghi', 'rindex', 'ghi', 0, 8)
        self.checkraises(ValueError, 'abcdefghi', 'rindex', 'ghi', 0, -1)

        # to check the ability to dalej Nic jako defaults
        self.checkequal(12, 'rrarrrrrrrrra', 'rindex', 'a')
        self.checkequal(12, 'rrarrrrrrrrra', 'rindex', 'a', 4)
        self.checkraises(ValueError, 'rrarrrrrrrrra', 'rindex', 'a', 4, 6)
        self.checkequal(12, 'rrarrrrrrrrra', 'rindex', 'a', 4, Nic)
        self.checkequal( 2, 'rrarrrrrrrrra', 'rindex', 'a', Nic, 6)

        self.checkraises(TypeError, 'hello', 'rindex')

        jeżeli self.contains_bytes:
            self.checkraises(ValueError, 'hello', 'rindex', 42)
        inaczej:
            self.checkraises(TypeError, 'hello', 'rindex', 42)

    def test_lower(self):
        self.checkequal('hello', 'HeLLo', 'lower')
        self.checkequal('hello', 'hello', 'lower')
        self.checkraises(TypeError, 'hello', 'lower', 42)

    def test_upper(self):
        self.checkequal('HELLO', 'HeLLo', 'upper')
        self.checkequal('HELLO', 'HELLO', 'upper')
        self.checkraises(TypeError, 'hello', 'upper', 42)

    def test_expandtabs(self):
        self.checkequal('abc\rab      def\ng       hi', 'abc\rab\tdef\ng\thi',
                        'expandtabs')
        self.checkequal('abc\rab      def\ng       hi', 'abc\rab\tdef\ng\thi',
                        'expandtabs', 8)
        self.checkequal('abc\rab  def\ng   hi', 'abc\rab\tdef\ng\thi',
                        'expandtabs', 4)
        self.checkequal('abc\r\nab      def\ng       hi', 'abc\r\nab\tdef\ng\thi',
                        'expandtabs')
        self.checkequal('abc\r\nab      def\ng       hi', 'abc\r\nab\tdef\ng\thi',
                        'expandtabs', 8)
        self.checkequal('abc\r\nab  def\ng   hi', 'abc\r\nab\tdef\ng\thi',
                        'expandtabs', 4)
        self.checkequal('abc\r\nab\r\ndef\ng\r\nhi', 'abc\r\nab\r\ndef\ng\r\nhi',
                        'expandtabs', 4)
        # check keyword args
        self.checkequal('abc\rab      def\ng       hi', 'abc\rab\tdef\ng\thi',
                        'expandtabs', tabsize=8)
        self.checkequal('abc\rab  def\ng   hi', 'abc\rab\tdef\ng\thi',
                        'expandtabs', tabsize=4)

        self.checkequal('  a\n b', ' \ta\n\tb', 'expandtabs', 1)

        self.checkraises(TypeError, 'hello', 'expandtabs', 42, 42)
        # This test jest only valid when sizeof(int) == sizeof(void*) == 4.
        jeżeli sys.maxsize < (1 << 32) oraz struct.calcsize('P') == 4:
            self.checkraises(OverflowError,
                             '\ta\n\tb', 'expandtabs', sys.maxsize)

    def test_split(self):
        # by a char
        self.checkequal(['a', 'b', 'c', 'd'], 'a|b|c|d', 'split', '|')
        self.checkequal(['a|b|c|d'], 'a|b|c|d', 'split', '|', 0)
        self.checkequal(['a', 'b|c|d'], 'a|b|c|d', 'split', '|', 1)
        self.checkequal(['a', 'b', 'c|d'], 'a|b|c|d', 'split', '|', 2)
        self.checkequal(['a', 'b', 'c', 'd'], 'a|b|c|d', 'split', '|', 3)
        self.checkequal(['a', 'b', 'c', 'd'], 'a|b|c|d', 'split', '|', 4)
        self.checkequal(['a', 'b', 'c', 'd'], 'a|b|c|d', 'split', '|',
                        sys.maxsize-2)
        self.checkequal(['a|b|c|d'], 'a|b|c|d', 'split', '|', 0)
        self.checkequal(['a', '', 'b||c||d'], 'a||b||c||d', 'split', '|', 2)
        self.checkequal(['endcase ', ''], 'endcase |', 'split', '|')
        self.checkequal(['', ' startcase'], '| startcase', 'split', '|')
        self.checkequal(['', 'bothcase', ''], '|bothcase|', 'split', '|')
        self.checkequal(['a', '', 'b\x00c\x00d'], 'a\x00\x00b\x00c\x00d', 'split', '\x00', 2)

        self.checkequal(['a']*20, ('a|'*20)[:-1], 'split', '|')
        self.checkequal(['a']*15 +['a|a|a|a|a'],
                                   ('a|'*20)[:-1], 'split', '|', 15)

        # by string
        self.checkequal(['a', 'b', 'c', 'd'], 'a//b//c//d', 'split', '//')
        self.checkequal(['a', 'b//c//d'], 'a//b//c//d', 'split', '//', 1)
        self.checkequal(['a', 'b', 'c//d'], 'a//b//c//d', 'split', '//', 2)
        self.checkequal(['a', 'b', 'c', 'd'], 'a//b//c//d', 'split', '//', 3)
        self.checkequal(['a', 'b', 'c', 'd'], 'a//b//c//d', 'split', '//', 4)
        self.checkequal(['a', 'b', 'c', 'd'], 'a//b//c//d', 'split', '//',
                        sys.maxsize-10)
        self.checkequal(['a//b//c//d'], 'a//b//c//d', 'split', '//', 0)
        self.checkequal(['a', '', 'b////c////d'], 'a////b////c////d', 'split', '//', 2)
        self.checkequal(['endcase ', ''], 'endcase test', 'split', 'test')
        self.checkequal(['', ' begincase'], 'test begincase', 'split', 'test')
        self.checkequal(['', ' bothcase ', ''], 'test bothcase test',
                        'split', 'test')
        self.checkequal(['a', 'bc'], 'abbbc', 'split', 'bb')
        self.checkequal(['', ''], 'aaa', 'split', 'aaa')
        self.checkequal(['aaa'], 'aaa', 'split', 'aaa', 0)
        self.checkequal(['ab', 'ab'], 'abbaab', 'split', 'ba')
        self.checkequal(['aaaa'], 'aaaa', 'split', 'aab')
        self.checkequal([''], '', 'split', 'aaa')
        self.checkequal(['aa'], 'aa', 'split', 'aaa')
        self.checkequal(['A', 'bobb'], 'Abbobbbobb', 'split', 'bbobb')
        self.checkequal(['A', 'B', ''], 'AbbobbBbbobb', 'split', 'bbobb')

        self.checkequal(['a']*20, ('aBLAH'*20)[:-4], 'split', 'BLAH')
        self.checkequal(['a']*20, ('aBLAH'*20)[:-4], 'split', 'BLAH', 19)
        self.checkequal(['a']*18 + ['aBLAHa'], ('aBLAH'*20)[:-4],
                        'split', 'BLAH', 18)

        # przy keyword args
        self.checkequal(['a', 'b', 'c', 'd'], 'a|b|c|d', 'split', sep='|')
        self.checkequal(['a', 'b|c|d'],
                        'a|b|c|d', 'split', '|', maxsplit=1)
        self.checkequal(['a', 'b|c|d'],
                        'a|b|c|d', 'split', sep='|', maxsplit=1)
        self.checkequal(['a', 'b|c|d'],
                        'a|b|c|d', 'split', maxsplit=1, sep='|')
        self.checkequal(['a', 'b c d'],
                        'a b c d', 'split', maxsplit=1)

        # argument type
        self.checkraises(TypeError, 'hello', 'split', 42, 42, 42)

        # null case
        self.checkraises(ValueError, 'hello', 'split', '')
        self.checkraises(ValueError, 'hello', 'split', '', 0)

    def test_rsplit(self):
        # by a char
        self.checkequal(['a', 'b', 'c', 'd'], 'a|b|c|d', 'rsplit', '|')
        self.checkequal(['a|b|c', 'd'], 'a|b|c|d', 'rsplit', '|', 1)
        self.checkequal(['a|b', 'c', 'd'], 'a|b|c|d', 'rsplit', '|', 2)
        self.checkequal(['a', 'b', 'c', 'd'], 'a|b|c|d', 'rsplit', '|', 3)
        self.checkequal(['a', 'b', 'c', 'd'], 'a|b|c|d', 'rsplit', '|', 4)
        self.checkequal(['a', 'b', 'c', 'd'], 'a|b|c|d', 'rsplit', '|',
                        sys.maxsize-100)
        self.checkequal(['a|b|c|d'], 'a|b|c|d', 'rsplit', '|', 0)
        self.checkequal(['a||b||c', '', 'd'], 'a||b||c||d', 'rsplit', '|', 2)
        self.checkequal(['', ' begincase'], '| begincase', 'rsplit', '|')
        self.checkequal(['endcase ', ''], 'endcase |', 'rsplit', '|')
        self.checkequal(['', 'bothcase', ''], '|bothcase|', 'rsplit', '|')

        self.checkequal(['a\x00\x00b', 'c', 'd'], 'a\x00\x00b\x00c\x00d', 'rsplit', '\x00', 2)

        self.checkequal(['a']*20, ('a|'*20)[:-1], 'rsplit', '|')
        self.checkequal(['a|a|a|a|a']+['a']*15,
                        ('a|'*20)[:-1], 'rsplit', '|', 15)

        # by string
        self.checkequal(['a', 'b', 'c', 'd'], 'a//b//c//d', 'rsplit', '//')
        self.checkequal(['a//b//c', 'd'], 'a//b//c//d', 'rsplit', '//', 1)
        self.checkequal(['a//b', 'c', 'd'], 'a//b//c//d', 'rsplit', '//', 2)
        self.checkequal(['a', 'b', 'c', 'd'], 'a//b//c//d', 'rsplit', '//', 3)
        self.checkequal(['a', 'b', 'c', 'd'], 'a//b//c//d', 'rsplit', '//', 4)
        self.checkequal(['a', 'b', 'c', 'd'], 'a//b//c//d', 'rsplit', '//',
                        sys.maxsize-5)
        self.checkequal(['a//b//c//d'], 'a//b//c//d', 'rsplit', '//', 0)
        self.checkequal(['a////b////c', '', 'd'], 'a////b////c////d', 'rsplit', '//', 2)
        self.checkequal(['', ' begincase'], 'test begincase', 'rsplit', 'test')
        self.checkequal(['endcase ', ''], 'endcase test', 'rsplit', 'test')
        self.checkequal(['', ' bothcase ', ''], 'test bothcase test',
                        'rsplit', 'test')
        self.checkequal(['ab', 'c'], 'abbbc', 'rsplit', 'bb')
        self.checkequal(['', ''], 'aaa', 'rsplit', 'aaa')
        self.checkequal(['aaa'], 'aaa', 'rsplit', 'aaa', 0)
        self.checkequal(['ab', 'ab'], 'abbaab', 'rsplit', 'ba')
        self.checkequal(['aaaa'], 'aaaa', 'rsplit', 'aab')
        self.checkequal([''], '', 'rsplit', 'aaa')
        self.checkequal(['aa'], 'aa', 'rsplit', 'aaa')
        self.checkequal(['bbob', 'A'], 'bbobbbobbA', 'rsplit', 'bbobb')
        self.checkequal(['', 'B', 'A'], 'bbobbBbbobbA', 'rsplit', 'bbobb')

        self.checkequal(['a']*20, ('aBLAH'*20)[:-4], 'rsplit', 'BLAH')
        self.checkequal(['a']*20, ('aBLAH'*20)[:-4], 'rsplit', 'BLAH', 19)
        self.checkequal(['aBLAHa'] + ['a']*18, ('aBLAH'*20)[:-4],
                        'rsplit', 'BLAH', 18)

        # przy keyword args
        self.checkequal(['a', 'b', 'c', 'd'], 'a|b|c|d', 'rsplit', sep='|')
        self.checkequal(['a|b|c', 'd'],
                        'a|b|c|d', 'rsplit', '|', maxsplit=1)
        self.checkequal(['a|b|c', 'd'],
                        'a|b|c|d', 'rsplit', sep='|', maxsplit=1)
        self.checkequal(['a|b|c', 'd'],
                        'a|b|c|d', 'rsplit', maxsplit=1, sep='|')
        self.checkequal(['a b c', 'd'],
                        'a b c d', 'rsplit', maxsplit=1)

        # argument type
        self.checkraises(TypeError, 'hello', 'rsplit', 42, 42, 42)

        # null case
        self.checkraises(ValueError, 'hello', 'rsplit', '')
        self.checkraises(ValueError, 'hello', 'rsplit', '', 0)

    def test_replace(self):
        EQ = self.checkequal

        # Operations on the empty string
        EQ("", "", "replace", "", "")
        EQ("A", "", "replace", "", "A")
        EQ("", "", "replace", "A", "")
        EQ("", "", "replace", "A", "A")
        EQ("", "", "replace", "", "", 100)
        EQ("", "", "replace", "", "", sys.maxsize)

        # interleave (from=="", 'to' gets inserted everywhere)
        EQ("A", "A", "replace", "", "")
        EQ("*A*", "A", "replace", "", "*")
        EQ("*1A*1", "A", "replace", "", "*1")
        EQ("*-#A*-#", "A", "replace", "", "*-#")
        EQ("*-A*-A*-", "AA", "replace", "", "*-")
        EQ("*-A*-A*-", "AA", "replace", "", "*-", -1)
        EQ("*-A*-A*-", "AA", "replace", "", "*-", sys.maxsize)
        EQ("*-A*-A*-", "AA", "replace", "", "*-", 4)
        EQ("*-A*-A*-", "AA", "replace", "", "*-", 3)
        EQ("*-A*-A", "AA", "replace", "", "*-", 2)
        EQ("*-AA", "AA", "replace", "", "*-", 1)
        EQ("AA", "AA", "replace", "", "*-", 0)

        # single character deletion (from=="A", to=="")
        EQ("", "A", "replace", "A", "")
        EQ("", "AAA", "replace", "A", "")
        EQ("", "AAA", "replace", "A", "", -1)
        EQ("", "AAA", "replace", "A", "", sys.maxsize)
        EQ("", "AAA", "replace", "A", "", 4)
        EQ("", "AAA", "replace", "A", "", 3)
        EQ("A", "AAA", "replace", "A", "", 2)
        EQ("AA", "AAA", "replace", "A", "", 1)
        EQ("AAA", "AAA", "replace", "A", "", 0)
        EQ("", "AAAAAAAAAA", "replace", "A", "")
        EQ("BCD", "ABACADA", "replace", "A", "")
        EQ("BCD", "ABACADA", "replace", "A", "", -1)
        EQ("BCD", "ABACADA", "replace", "A", "", sys.maxsize)
        EQ("BCD", "ABACADA", "replace", "A", "", 5)
        EQ("BCD", "ABACADA", "replace", "A", "", 4)
        EQ("BCDA", "ABACADA", "replace", "A", "", 3)
        EQ("BCADA", "ABACADA", "replace", "A", "", 2)
        EQ("BACADA", "ABACADA", "replace", "A", "", 1)
        EQ("ABACADA", "ABACADA", "replace", "A", "", 0)
        EQ("BCD", "ABCAD", "replace", "A", "")
        EQ("BCD", "ABCADAA", "replace", "A", "")
        EQ("BCD", "BCD", "replace", "A", "")
        EQ("*************", "*************", "replace", "A", "")
        EQ("^A^", "^"+"A"*1000+"^", "replace", "A", "", 999)

        # substring deletion (from=="the", to=="")
        EQ("", "the", "replace", "the", "")
        EQ("ater", "theater", "replace", "the", "")
        EQ("", "thethe", "replace", "the", "")
        EQ("", "thethethethe", "replace", "the", "")
        EQ("aaaa", "theatheatheathea", "replace", "the", "")
        EQ("that", "that", "replace", "the", "")
        EQ("thaet", "thaet", "replace", "the", "")
        EQ("here oraz re", "here oraz there", "replace", "the", "")
        EQ("here oraz re oraz re", "here oraz there oraz there",
           "replace", "the", "", sys.maxsize)
        EQ("here oraz re oraz re", "here oraz there oraz there",
           "replace", "the", "", -1)
        EQ("here oraz re oraz re", "here oraz there oraz there",
           "replace", "the", "", 3)
        EQ("here oraz re oraz re", "here oraz there oraz there",
           "replace", "the", "", 2)
        EQ("here oraz re oraz there", "here oraz there oraz there",
           "replace", "the", "", 1)
        EQ("here oraz there oraz there", "here oraz there oraz there",
           "replace", "the", "", 0)
        EQ("here oraz re oraz re", "here oraz there oraz there", "replace", "the", "")

        EQ("abc", "abc", "replace", "the", "")
        EQ("abcdefg", "abcdefg", "replace", "the", "")

        # substring deletion (from=="bob", to=="")
        EQ("bob", "bbobob", "replace", "bob", "")
        EQ("bobXbob", "bbobobXbbobob", "replace", "bob", "")
        EQ("aaaaaaa", "aaaaaaabob", "replace", "bob", "")
        EQ("aaaaaaa", "aaaaaaa", "replace", "bob", "")

        # single character replace w place (len(from)==len(to)==1)
        EQ("Who goes there?", "Who goes there?", "replace", "o", "o")
        EQ("WhO gOes there?", "Who goes there?", "replace", "o", "O")
        EQ("WhO gOes there?", "Who goes there?", "replace", "o", "O", sys.maxsize)
        EQ("WhO gOes there?", "Who goes there?", "replace", "o", "O", -1)
        EQ("WhO gOes there?", "Who goes there?", "replace", "o", "O", 3)
        EQ("WhO gOes there?", "Who goes there?", "replace", "o", "O", 2)
        EQ("WhO goes there?", "Who goes there?", "replace", "o", "O", 1)
        EQ("Who goes there?", "Who goes there?", "replace", "o", "O", 0)

        EQ("Who goes there?", "Who goes there?", "replace", "a", "q")
        EQ("who goes there?", "Who goes there?", "replace", "W", "w")
        EQ("wwho goes there?ww", "WWho goes there?WW", "replace", "W", "w")
        EQ("Who goes there!", "Who goes there?", "replace", "?", "!")
        EQ("Who goes there!!", "Who goes there??", "replace", "?", "!")

        EQ("Who goes there?", "Who goes there?", "replace", ".", "!")

        # substring replace w place (len(from)==len(to) > 1)
        EQ("Th** ** a t**sue", "This jest a tissue", "replace", "is", "**")
        EQ("Th** ** a t**sue", "This jest a tissue", "replace", "is", "**", sys.maxsize)
        EQ("Th** ** a t**sue", "This jest a tissue", "replace", "is", "**", -1)
        EQ("Th** ** a t**sue", "This jest a tissue", "replace", "is", "**", 4)
        EQ("Th** ** a t**sue", "This jest a tissue", "replace", "is", "**", 3)
        EQ("Th** ** a tissue", "This jest a tissue", "replace", "is", "**", 2)
        EQ("Th** jest a tissue", "This jest a tissue", "replace", "is", "**", 1)
        EQ("This jest a tissue", "This jest a tissue", "replace", "is", "**", 0)
        EQ("cobob", "bobob", "replace", "bob", "cob")
        EQ("cobobXcobocob", "bobobXbobobob", "replace", "bob", "cob")
        EQ("bobob", "bobob", "replace", "bot", "bot")

        # replace single character (len(from)==1, len(to)>1)
        EQ("ReyKKjaviKK", "Reykjavik", "replace", "k", "KK")
        EQ("ReyKKjaviKK", "Reykjavik", "replace", "k", "KK", -1)
        EQ("ReyKKjaviKK", "Reykjavik", "replace", "k", "KK", sys.maxsize)
        EQ("ReyKKjaviKK", "Reykjavik", "replace", "k", "KK", 2)
        EQ("ReyKKjavik", "Reykjavik", "replace", "k", "KK", 1)
        EQ("Reykjavik", "Reykjavik", "replace", "k", "KK", 0)
        EQ("A----B----C----", "A.B.C.", "replace", ".", "----")
        # issue #15534
        EQ('...\u043c......&lt;', '...\u043c......<', "replace", "<", "&lt;")

        EQ("Reykjavik", "Reykjavik", "replace", "q", "KK")

        # replace substring (len(from)>1, len(to)!=len(from))
        EQ("ham, ham, eggs oraz ham", "spam, spam, eggs oraz spam",
           "replace", "spam", "ham")
        EQ("ham, ham, eggs oraz ham", "spam, spam, eggs oraz spam",
           "replace", "spam", "ham", sys.maxsize)
        EQ("ham, ham, eggs oraz ham", "spam, spam, eggs oraz spam",
           "replace", "spam", "ham", -1)
        EQ("ham, ham, eggs oraz ham", "spam, spam, eggs oraz spam",
           "replace", "spam", "ham", 4)
        EQ("ham, ham, eggs oraz ham", "spam, spam, eggs oraz spam",
           "replace", "spam", "ham", 3)
        EQ("ham, ham, eggs oraz spam", "spam, spam, eggs oraz spam",
           "replace", "spam", "ham", 2)
        EQ("ham, spam, eggs oraz spam", "spam, spam, eggs oraz spam",
           "replace", "spam", "ham", 1)
        EQ("spam, spam, eggs oraz spam", "spam, spam, eggs oraz spam",
           "replace", "spam", "ham", 0)

        EQ("bobob", "bobobob", "replace", "bobob", "bob")
        EQ("bobobXbobob", "bobobobXbobobob", "replace", "bobob", "bob")
        EQ("BOBOBOB", "BOBOBOB", "replace", "bob", "bobby")

        # XXX Commented out. Is there any reason to support buffer objects
        # jako arguments dla str.replace()?  GvR
##         ba = bytearray('a')
##         bb = bytearray('b')
##         EQ("bbc", "abc", "replace", ba, bb)
##         EQ("aac", "abc", "replace", bb, ba)

        #
        self.checkequal('one@two!three!', 'one!two!three!', 'replace', '!', '@', 1)
        self.checkequal('onetwothree', 'one!two!three!', 'replace', '!', '')
        self.checkequal('one@two@three!', 'one!two!three!', 'replace', '!', '@', 2)
        self.checkequal('one@two@three@', 'one!two!three!', 'replace', '!', '@', 3)
        self.checkequal('one@two@three@', 'one!two!three!', 'replace', '!', '@', 4)
        self.checkequal('one!two!three!', 'one!two!three!', 'replace', '!', '@', 0)
        self.checkequal('one@two@three@', 'one!two!three!', 'replace', '!', '@')
        self.checkequal('one!two!three!', 'one!two!three!', 'replace', 'x', '@')
        self.checkequal('one!two!three!', 'one!two!three!', 'replace', 'x', '@', 2)
        self.checkequal('-a-b-c-', 'abc', 'replace', '', '-')
        self.checkequal('-a-b-c', 'abc', 'replace', '', '-', 3)
        self.checkequal('abc', 'abc', 'replace', '', '-', 0)
        self.checkequal('', '', 'replace', '', '')
        self.checkequal('abc', 'abc', 'replace', 'ab', '--', 0)
        self.checkequal('abc', 'abc', 'replace', 'xy', '--')
        # Next three dla SF bug 422088: [OSF1 alpha] string.replace(); died with
        # MemoryError due to empty result (platform malloc issue when requesting
        # 0 bytes).
        self.checkequal('', '123', 'replace', '123', '')
        self.checkequal('', '123123', 'replace', '123', '')
        self.checkequal('x', '123x123', 'replace', '123', '')

        self.checkraises(TypeError, 'hello', 'replace')
        self.checkraises(TypeError, 'hello', 'replace', 42)
        self.checkraises(TypeError, 'hello', 'replace', 42, 'h')
        self.checkraises(TypeError, 'hello', 'replace', 'h', 42)

    @unittest.skipIf(sys.maxsize > (1 << 32) albo struct.calcsize('P') != 4,
                     'only applies to 32-bit platforms')
    def test_replace_overflow(self):
        # Check dla overflow checking on 32 bit machines
        A2_16 = "A" * (2**16)
        self.checkraises(OverflowError, A2_16, "replace", "", A2_16)
        self.checkraises(OverflowError, A2_16, "replace", "A", A2_16)
        self.checkraises(OverflowError, A2_16, "replace", "AA", A2_16+A2_16)



klasa CommonTest(BaseTest):
    # This testcase contains test that can be used w all
    # stringlike classes. Currently this jest str, unicode
    # UserString oraz the string module.

    def test_hash(self):
        # SF bug 1054139:  += optimization was nie invalidating cached hash value
        a = self.type2test('DNSSEC')
        b = self.type2test('')
        dla c w a:
            b += c
            hash(b)
        self.assertEqual(hash(a), hash(b))

    def test_capitalize(self):
        self.checkequal(' hello ', ' hello ', 'capitalize')
        self.checkequal('Hello ', 'Hello ','capitalize')
        self.checkequal('Hello ', 'hello ','capitalize')
        self.checkequal('Aaaa', 'aaaa', 'capitalize')
        self.checkequal('Aaaa', 'AaAa', 'capitalize')

        # check that titlecased chars are lowered correctly
        # \u1ffc jest the titlecased char
        self.checkequal('\u03a9\u0399\u1ff3\u1ff3\u1ff3',
                        '\u1ff3\u1ff3\u1ffc\u1ffc', 'capitalize')
        # check przy cased non-letter chars
        self.checkequal('\u24c5\u24e8\u24e3\u24d7\u24de\u24dd',
                        '\u24c5\u24ce\u24c9\u24bd\u24c4\u24c3', 'capitalize')
        self.checkequal('\u24c5\u24e8\u24e3\u24d7\u24de\u24dd',
                        '\u24df\u24e8\u24e3\u24d7\u24de\u24dd', 'capitalize')
        self.checkequal('\u2160\u2171\u2172',
                        '\u2160\u2161\u2162', 'capitalize')
        self.checkequal('\u2160\u2171\u2172',
                        '\u2170\u2171\u2172', 'capitalize')
        # check przy Ll chars przy no upper - nothing changes here
        self.checkequal('\u019b\u1d00\u1d86\u0221\u1fb7',
                        '\u019b\u1d00\u1d86\u0221\u1fb7', 'capitalize')

        self.checkraises(TypeError, 'hello', 'capitalize', 42)

    def test_additional_split(self):
        self.checkequal(['this', 'is', 'the', 'split', 'function'],
            'this jest the split function', 'split')

        # by whitespace
        self.checkequal(['a', 'b', 'c', 'd'], 'a b c d ', 'split')
        self.checkequal(['a', 'b c d'], 'a b c d', 'split', Nic, 1)
        self.checkequal(['a', 'b', 'c d'], 'a b c d', 'split', Nic, 2)
        self.checkequal(['a', 'b', 'c', 'd'], 'a b c d', 'split', Nic, 3)
        self.checkequal(['a', 'b', 'c', 'd'], 'a b c d', 'split', Nic, 4)
        self.checkequal(['a', 'b', 'c', 'd'], 'a b c d', 'split', Nic,
                        sys.maxsize-1)
        self.checkequal(['a b c d'], 'a b c d', 'split', Nic, 0)
        self.checkequal(['a b c d'], '  a b c d', 'split', Nic, 0)
        self.checkequal(['a', 'b', 'c  d'], 'a  b  c  d', 'split', Nic, 2)

        self.checkequal([], '         ', 'split')
        self.checkequal(['a'], '  a    ', 'split')
        self.checkequal(['a', 'b'], '  a    b   ', 'split')
        self.checkequal(['a', 'b   '], '  a    b   ', 'split', Nic, 1)
        self.checkequal(['a', 'b   c   '], '  a    b   c   ', 'split', Nic, 1)
        self.checkequal(['a', 'b', 'c   '], '  a    b   c   ', 'split', Nic, 2)
        self.checkequal(['a', 'b'], '\n\ta \t\r b \v ', 'split')
        aaa = ' a '*20
        self.checkequal(['a']*20, aaa, 'split')
        self.checkequal(['a'] + [aaa[4:]], aaa, 'split', Nic, 1)
        self.checkequal(['a']*19 + ['a '], aaa, 'split', Nic, 19)

        # mixed use of str oraz unicode
        self.checkequal(['a', 'b', 'c d'], 'a b c d', 'split', ' ', 2)

    def test_additional_rsplit(self):
        self.checkequal(['this', 'is', 'the', 'rsplit', 'function'],
                         'this jest the rsplit function', 'rsplit')

        # by whitespace
        self.checkequal(['a', 'b', 'c', 'd'], 'a b c d ', 'rsplit')
        self.checkequal(['a b c', 'd'], 'a b c d', 'rsplit', Nic, 1)
        self.checkequal(['a b', 'c', 'd'], 'a b c d', 'rsplit', Nic, 2)
        self.checkequal(['a', 'b', 'c', 'd'], 'a b c d', 'rsplit', Nic, 3)
        self.checkequal(['a', 'b', 'c', 'd'], 'a b c d', 'rsplit', Nic, 4)
        self.checkequal(['a', 'b', 'c', 'd'], 'a b c d', 'rsplit', Nic,
                        sys.maxsize-20)
        self.checkequal(['a b c d'], 'a b c d', 'rsplit', Nic, 0)
        self.checkequal(['a b c d'], 'a b c d  ', 'rsplit', Nic, 0)
        self.checkequal(['a  b', 'c', 'd'], 'a  b  c  d', 'rsplit', Nic, 2)

        self.checkequal([], '         ', 'rsplit')
        self.checkequal(['a'], '  a    ', 'rsplit')
        self.checkequal(['a', 'b'], '  a    b   ', 'rsplit')
        self.checkequal(['  a', 'b'], '  a    b   ', 'rsplit', Nic, 1)
        self.checkequal(['  a    b','c'], '  a    b   c   ', 'rsplit',
                        Nic, 1)
        self.checkequal(['  a', 'b', 'c'], '  a    b   c   ', 'rsplit',
                        Nic, 2)
        self.checkequal(['a', 'b'], '\n\ta \t\r b \v ', 'rsplit', Nic, 88)
        aaa = ' a '*20
        self.checkequal(['a']*20, aaa, 'rsplit')
        self.checkequal([aaa[:-4]] + ['a'], aaa, 'rsplit', Nic, 1)
        self.checkequal([' a  a'] + ['a']*18, aaa, 'rsplit', Nic, 18)

        # mixed use of str oraz unicode
        self.checkequal(['a b', 'c', 'd'], 'a b c d', 'rsplit', ' ', 2)

    def test_strip(self):
        self.checkequal('hello', '   hello   ', 'strip')
        self.checkequal('hello   ', '   hello   ', 'lstrip')
        self.checkequal('   hello', '   hello   ', 'rstrip')
        self.checkequal('hello', 'hello', 'strip')

        # strip/lstrip/rstrip przy Nic arg
        self.checkequal('hello', '   hello   ', 'strip', Nic)
        self.checkequal('hello   ', '   hello   ', 'lstrip', Nic)
        self.checkequal('   hello', '   hello   ', 'rstrip', Nic)
        self.checkequal('hello', 'hello', 'strip', Nic)

        # strip/lstrip/rstrip przy str arg
        self.checkequal('hello', 'xyzzyhelloxyzzy', 'strip', 'xyz')
        self.checkequal('helloxyzzy', 'xyzzyhelloxyzzy', 'lstrip', 'xyz')
        self.checkequal('xyzzyhello', 'xyzzyhelloxyzzy', 'rstrip', 'xyz')
        self.checkequal('hello', 'hello', 'strip', 'xyz')

        self.checkraises(TypeError, 'hello', 'strip', 42, 42)
        self.checkraises(TypeError, 'hello', 'lstrip', 42, 42)
        self.checkraises(TypeError, 'hello', 'rstrip', 42, 42)

    def test_ljust(self):
        self.checkequal('abc       ', 'abc', 'ljust', 10)
        self.checkequal('abc   ', 'abc', 'ljust', 6)
        self.checkequal('abc', 'abc', 'ljust', 3)
        self.checkequal('abc', 'abc', 'ljust', 2)
        self.checkequal('abc*******', 'abc', 'ljust', 10, '*')
        self.checkraises(TypeError, 'abc', 'ljust')

    def test_rjust(self):
        self.checkequal('       abc', 'abc', 'rjust', 10)
        self.checkequal('   abc', 'abc', 'rjust', 6)
        self.checkequal('abc', 'abc', 'rjust', 3)
        self.checkequal('abc', 'abc', 'rjust', 2)
        self.checkequal('*******abc', 'abc', 'rjust', 10, '*')
        self.checkraises(TypeError, 'abc', 'rjust')

    def test_center(self):
        self.checkequal('   abc    ', 'abc', 'center', 10)
        self.checkequal(' abc  ', 'abc', 'center', 6)
        self.checkequal('abc', 'abc', 'center', 3)
        self.checkequal('abc', 'abc', 'center', 2)
        self.checkequal('***abc****', 'abc', 'center', 10, '*')
        self.checkraises(TypeError, 'abc', 'center')

    def test_swapcase(self):
        self.checkequal('hEllO CoMPuTErS', 'HeLLo cOmpUteRs', 'swapcase')

        self.checkraises(TypeError, 'hello', 'swapcase', 42)

    def test_zfill(self):
        self.checkequal('123', '123', 'zfill', 2)
        self.checkequal('123', '123', 'zfill', 3)
        self.checkequal('0123', '123', 'zfill', 4)
        self.checkequal('+123', '+123', 'zfill', 3)
        self.checkequal('+123', '+123', 'zfill', 4)
        self.checkequal('+0123', '+123', 'zfill', 5)
        self.checkequal('-123', '-123', 'zfill', 3)
        self.checkequal('-123', '-123', 'zfill', 4)
        self.checkequal('-0123', '-123', 'zfill', 5)
        self.checkequal('000', '', 'zfill', 3)
        self.checkequal('34', '34', 'zfill', 1)
        self.checkequal('0034', '34', 'zfill', 4)

        self.checkraises(TypeError, '123', 'zfill')

klasa MixinStrUnicodeUserStringTest:
    # additional tests that only work for
    # stringlike objects, i.e. str, unicode, UserString
    # (but nie the string module)

    def test_islower(self):
        self.checkequal(Nieprawda, '', 'islower')
        self.checkequal(Prawda, 'a', 'islower')
        self.checkequal(Nieprawda, 'A', 'islower')
        self.checkequal(Nieprawda, '\n', 'islower')
        self.checkequal(Prawda, 'abc', 'islower')
        self.checkequal(Nieprawda, 'aBc', 'islower')
        self.checkequal(Prawda, 'abc\n', 'islower')
        self.checkraises(TypeError, 'abc', 'islower', 42)

    def test_isupper(self):
        self.checkequal(Nieprawda, '', 'isupper')
        self.checkequal(Nieprawda, 'a', 'isupper')
        self.checkequal(Prawda, 'A', 'isupper')
        self.checkequal(Nieprawda, '\n', 'isupper')
        self.checkequal(Prawda, 'ABC', 'isupper')
        self.checkequal(Nieprawda, 'AbC', 'isupper')
        self.checkequal(Prawda, 'ABC\n', 'isupper')
        self.checkraises(TypeError, 'abc', 'isupper', 42)

    def test_istitle(self):
        self.checkequal(Nieprawda, '', 'istitle')
        self.checkequal(Nieprawda, 'a', 'istitle')
        self.checkequal(Prawda, 'A', 'istitle')
        self.checkequal(Nieprawda, '\n', 'istitle')
        self.checkequal(Prawda, 'A Titlecased Line', 'istitle')
        self.checkequal(Prawda, 'A\nTitlecased Line', 'istitle')
        self.checkequal(Prawda, 'A Titlecased, Line', 'istitle')
        self.checkequal(Nieprawda, 'Not a capitalized String', 'istitle')
        self.checkequal(Nieprawda, 'Not\ta Titlecase String', 'istitle')
        self.checkequal(Nieprawda, 'Not--a Titlecase String', 'istitle')
        self.checkequal(Nieprawda, 'NOT', 'istitle')
        self.checkraises(TypeError, 'abc', 'istitle', 42)

    def test_isspace(self):
        self.checkequal(Nieprawda, '', 'isspace')
        self.checkequal(Nieprawda, 'a', 'isspace')
        self.checkequal(Prawda, ' ', 'isspace')
        self.checkequal(Prawda, '\t', 'isspace')
        self.checkequal(Prawda, '\r', 'isspace')
        self.checkequal(Prawda, '\n', 'isspace')
        self.checkequal(Prawda, ' \t\r\n', 'isspace')
        self.checkequal(Nieprawda, ' \t\r\na', 'isspace')
        self.checkraises(TypeError, 'abc', 'isspace', 42)

    def test_isalpha(self):
        self.checkequal(Nieprawda, '', 'isalpha')
        self.checkequal(Prawda, 'a', 'isalpha')
        self.checkequal(Prawda, 'A', 'isalpha')
        self.checkequal(Nieprawda, '\n', 'isalpha')
        self.checkequal(Prawda, 'abc', 'isalpha')
        self.checkequal(Nieprawda, 'aBc123', 'isalpha')
        self.checkequal(Nieprawda, 'abc\n', 'isalpha')
        self.checkraises(TypeError, 'abc', 'isalpha', 42)

    def test_isalnum(self):
        self.checkequal(Nieprawda, '', 'isalnum')
        self.checkequal(Prawda, 'a', 'isalnum')
        self.checkequal(Prawda, 'A', 'isalnum')
        self.checkequal(Nieprawda, '\n', 'isalnum')
        self.checkequal(Prawda, '123abc456', 'isalnum')
        self.checkequal(Prawda, 'a1b3c', 'isalnum')
        self.checkequal(Nieprawda, 'aBc000 ', 'isalnum')
        self.checkequal(Nieprawda, 'abc\n', 'isalnum')
        self.checkraises(TypeError, 'abc', 'isalnum', 42)

    def test_isdigit(self):
        self.checkequal(Nieprawda, '', 'isdigit')
        self.checkequal(Nieprawda, 'a', 'isdigit')
        self.checkequal(Prawda, '0', 'isdigit')
        self.checkequal(Prawda, '0123456789', 'isdigit')
        self.checkequal(Nieprawda, '0123456789a', 'isdigit')

        self.checkraises(TypeError, 'abc', 'isdigit', 42)

    def test_title(self):
        self.checkequal(' Hello ', ' hello ', 'title')
        self.checkequal('Hello ', 'hello ', 'title')
        self.checkequal('Hello ', 'Hello ', 'title')
        self.checkequal('Format This As Title String', "fOrMaT thIs aS titLe String", 'title')
        self.checkequal('Format,This-As*Title;String', "fOrMaT,thIs-aS*titLe;String", 'title', )
        self.checkequal('Getint', "getInt", 'title')
        self.checkraises(TypeError, 'hello', 'title', 42)

    def test_splitlines(self):
        self.checkequal(['abc', 'def', '', 'ghi'], "abc\ndef\n\rghi", 'splitlines')
        self.checkequal(['abc', 'def', '', 'ghi'], "abc\ndef\n\r\nghi", 'splitlines')
        self.checkequal(['abc', 'def', 'ghi'], "abc\ndef\r\nghi", 'splitlines')
        self.checkequal(['abc', 'def', 'ghi'], "abc\ndef\r\nghi\n", 'splitlines')
        self.checkequal(['abc', 'def', 'ghi', ''], "abc\ndef\r\nghi\n\r", 'splitlines')
        self.checkequal(['', 'abc', 'def', 'ghi', ''], "\nabc\ndef\r\nghi\n\r", 'splitlines')
        self.checkequal(['', 'abc', 'def', 'ghi', ''],
                        "\nabc\ndef\r\nghi\n\r", 'splitlines', Nieprawda)
        self.checkequal(['\n', 'abc\n', 'def\r\n', 'ghi\n', '\r'],
                        "\nabc\ndef\r\nghi\n\r", 'splitlines', Prawda)
        self.checkequal(['', 'abc', 'def', 'ghi', ''], "\nabc\ndef\r\nghi\n\r",
                        'splitlines', keepends=Nieprawda)
        self.checkequal(['\n', 'abc\n', 'def\r\n', 'ghi\n', '\r'],
                        "\nabc\ndef\r\nghi\n\r", 'splitlines', keepends=Prawda)

        self.checkraises(TypeError, 'abc', 'splitlines', 42, 42)

    def test_startswith(self):
        self.checkequal(Prawda, 'hello', 'startswith', 'he')
        self.checkequal(Prawda, 'hello', 'startswith', 'hello')
        self.checkequal(Nieprawda, 'hello', 'startswith', 'hello world')
        self.checkequal(Prawda, 'hello', 'startswith', '')
        self.checkequal(Nieprawda, 'hello', 'startswith', 'ello')
        self.checkequal(Prawda, 'hello', 'startswith', 'ello', 1)
        self.checkequal(Prawda, 'hello', 'startswith', 'o', 4)
        self.checkequal(Nieprawda, 'hello', 'startswith', 'o', 5)
        self.checkequal(Prawda, 'hello', 'startswith', '', 5)
        self.checkequal(Nieprawda, 'hello', 'startswith', 'lo', 6)
        self.checkequal(Prawda, 'helloworld', 'startswith', 'lowo', 3)
        self.checkequal(Prawda, 'helloworld', 'startswith', 'lowo', 3, 7)
        self.checkequal(Nieprawda, 'helloworld', 'startswith', 'lowo', 3, 6)
        self.checkequal(Prawda, '', 'startswith', '', 0, 1)
        self.checkequal(Prawda, '', 'startswith', '', 0, 0)
        self.checkequal(Nieprawda, '', 'startswith', '', 1, 0)

        # test negative indices
        self.checkequal(Prawda, 'hello', 'startswith', 'he', 0, -1)
        self.checkequal(Prawda, 'hello', 'startswith', 'he', -53, -1)
        self.checkequal(Nieprawda, 'hello', 'startswith', 'hello', 0, -1)
        self.checkequal(Nieprawda, 'hello', 'startswith', 'hello world', -1, -10)
        self.checkequal(Nieprawda, 'hello', 'startswith', 'ello', -5)
        self.checkequal(Prawda, 'hello', 'startswith', 'ello', -4)
        self.checkequal(Nieprawda, 'hello', 'startswith', 'o', -2)
        self.checkequal(Prawda, 'hello', 'startswith', 'o', -1)
        self.checkequal(Prawda, 'hello', 'startswith', '', -3, -3)
        self.checkequal(Nieprawda, 'hello', 'startswith', 'lo', -9)

        self.checkraises(TypeError, 'hello', 'startswith')
        self.checkraises(TypeError, 'hello', 'startswith', 42)

        # test tuple arguments
        self.checkequal(Prawda, 'hello', 'startswith', ('he', 'ha'))
        self.checkequal(Nieprawda, 'hello', 'startswith', ('lo', 'llo'))
        self.checkequal(Prawda, 'hello', 'startswith', ('hellox', 'hello'))
        self.checkequal(Nieprawda, 'hello', 'startswith', ())
        self.checkequal(Prawda, 'helloworld', 'startswith', ('hellowo',
                                                           'rld', 'lowo'), 3)
        self.checkequal(Nieprawda, 'helloworld', 'startswith', ('hellowo', 'ello',
                                                            'rld'), 3)
        self.checkequal(Prawda, 'hello', 'startswith', ('lo', 'he'), 0, -1)
        self.checkequal(Nieprawda, 'hello', 'startswith', ('he', 'hel'), 0, 1)
        self.checkequal(Prawda, 'hello', 'startswith', ('he', 'hel'), 0, 2)

        self.checkraises(TypeError, 'hello', 'startswith', (42,))

    def test_endswith(self):
        self.checkequal(Prawda, 'hello', 'endswith', 'lo')
        self.checkequal(Nieprawda, 'hello', 'endswith', 'he')
        self.checkequal(Prawda, 'hello', 'endswith', '')
        self.checkequal(Nieprawda, 'hello', 'endswith', 'hello world')
        self.checkequal(Nieprawda, 'helloworld', 'endswith', 'worl')
        self.checkequal(Prawda, 'helloworld', 'endswith', 'worl', 3, 9)
        self.checkequal(Prawda, 'helloworld', 'endswith', 'world', 3, 12)
        self.checkequal(Prawda, 'helloworld', 'endswith', 'lowo', 1, 7)
        self.checkequal(Prawda, 'helloworld', 'endswith', 'lowo', 2, 7)
        self.checkequal(Prawda, 'helloworld', 'endswith', 'lowo', 3, 7)
        self.checkequal(Nieprawda, 'helloworld', 'endswith', 'lowo', 4, 7)
        self.checkequal(Nieprawda, 'helloworld', 'endswith', 'lowo', 3, 8)
        self.checkequal(Nieprawda, 'ab', 'endswith', 'ab', 0, 1)
        self.checkequal(Nieprawda, 'ab', 'endswith', 'ab', 0, 0)
        self.checkequal(Prawda, '', 'endswith', '', 0, 1)
        self.checkequal(Prawda, '', 'endswith', '', 0, 0)
        self.checkequal(Nieprawda, '', 'endswith', '', 1, 0)

        # test negative indices
        self.checkequal(Prawda, 'hello', 'endswith', 'lo', -2)
        self.checkequal(Nieprawda, 'hello', 'endswith', 'he', -2)
        self.checkequal(Prawda, 'hello', 'endswith', '', -3, -3)
        self.checkequal(Nieprawda, 'hello', 'endswith', 'hello world', -10, -2)
        self.checkequal(Nieprawda, 'helloworld', 'endswith', 'worl', -6)
        self.checkequal(Prawda, 'helloworld', 'endswith', 'worl', -5, -1)
        self.checkequal(Prawda, 'helloworld', 'endswith', 'worl', -5, 9)
        self.checkequal(Prawda, 'helloworld', 'endswith', 'world', -7, 12)
        self.checkequal(Prawda, 'helloworld', 'endswith', 'lowo', -99, -3)
        self.checkequal(Prawda, 'helloworld', 'endswith', 'lowo', -8, -3)
        self.checkequal(Prawda, 'helloworld', 'endswith', 'lowo', -7, -3)
        self.checkequal(Nieprawda, 'helloworld', 'endswith', 'lowo', 3, -4)
        self.checkequal(Nieprawda, 'helloworld', 'endswith', 'lowo', -8, -2)

        self.checkraises(TypeError, 'hello', 'endswith')
        self.checkraises(TypeError, 'hello', 'endswith', 42)

        # test tuple arguments
        self.checkequal(Nieprawda, 'hello', 'endswith', ('he', 'ha'))
        self.checkequal(Prawda, 'hello', 'endswith', ('lo', 'llo'))
        self.checkequal(Prawda, 'hello', 'endswith', ('hellox', 'hello'))
        self.checkequal(Nieprawda, 'hello', 'endswith', ())
        self.checkequal(Prawda, 'helloworld', 'endswith', ('hellowo',
                                                           'rld', 'lowo'), 3)
        self.checkequal(Nieprawda, 'helloworld', 'endswith', ('hellowo', 'ello',
                                                            'rld'), 3, -1)
        self.checkequal(Prawda, 'hello', 'endswith', ('hell', 'ell'), 0, -1)
        self.checkequal(Nieprawda, 'hello', 'endswith', ('he', 'hel'), 0, 1)
        self.checkequal(Prawda, 'hello', 'endswith', ('he', 'hell'), 0, 4)

        self.checkraises(TypeError, 'hello', 'endswith', (42,))

    def test___contains__(self):
        self.checkequal(Prawda, '', '__contains__', '')
        self.checkequal(Prawda, 'abc', '__contains__', '')
        self.checkequal(Nieprawda, 'abc', '__contains__', '\0')
        self.checkequal(Prawda, '\0abc', '__contains__', '\0')
        self.checkequal(Prawda, 'abc\0', '__contains__', '\0')
        self.checkequal(Prawda, '\0abc', '__contains__', 'a')
        self.checkequal(Prawda, 'asdf', '__contains__', 'asdf')
        self.checkequal(Nieprawda, 'asd', '__contains__', 'asdf')
        self.checkequal(Nieprawda, '', '__contains__', 'asdf')

    def test_subscript(self):
        self.checkequal('a', 'abc', '__getitem__', 0)
        self.checkequal('c', 'abc', '__getitem__', -1)
        self.checkequal('a', 'abc', '__getitem__', 0)
        self.checkequal('abc', 'abc', '__getitem__', slice(0, 3))
        self.checkequal('abc', 'abc', '__getitem__', slice(0, 1000))
        self.checkequal('a', 'abc', '__getitem__', slice(0, 1))
        self.checkequal('', 'abc', '__getitem__', slice(0, 0))

        self.checkraises(TypeError, 'abc', '__getitem__', 'def')

    def test_slice(self):
        self.checkequal('abc', 'abc', '__getitem__', slice(0, 1000))
        self.checkequal('abc', 'abc', '__getitem__', slice(0, 3))
        self.checkequal('ab', 'abc', '__getitem__', slice(0, 2))
        self.checkequal('bc', 'abc', '__getitem__', slice(1, 3))
        self.checkequal('b', 'abc', '__getitem__', slice(1, 2))
        self.checkequal('', 'abc', '__getitem__', slice(2, 2))
        self.checkequal('', 'abc', '__getitem__', slice(1000, 1000))
        self.checkequal('', 'abc', '__getitem__', slice(2000, 1000))
        self.checkequal('', 'abc', '__getitem__', slice(2, 1))

        self.checkraises(TypeError, 'abc', '__getitem__', 'def')

    def test_extended_getslice(self):
        # Test extended slicing by comparing przy list slicing.
        s = string.ascii_letters + string.digits
        indices = (0, Nic, 1, 3, 41, -1, -2, -37)
        dla start w indices:
            dla stop w indices:
                # Skip step 0 (invalid)
                dla step w indices[1:]:
                    L = list(s)[start:stop:step]
                    self.checkequal("".join(L), s, '__getitem__',
                                    slice(start, stop, step))

    def test_mul(self):
        self.checkequal('', 'abc', '__mul__', -1)
        self.checkequal('', 'abc', '__mul__', 0)
        self.checkequal('abc', 'abc', '__mul__', 1)
        self.checkequal('abcabcabc', 'abc', '__mul__', 3)
        self.checkraises(TypeError, 'abc', '__mul__')
        self.checkraises(TypeError, 'abc', '__mul__', '')
        # XXX: on a 64-bit system, this doesn't podnieś an overflow error,
        # but either podnieśs a MemoryError, albo succeeds (jeżeli you have 54TiB)
        #self.checkraises(OverflowError, 10000*'abc', '__mul__', 2000000000)

    def test_join(self):
        # join now works przy any sequence type
        # moved here, because the argument order jest
        # different w string.join
        self.checkequal('a b c d', ' ', 'join', ['a', 'b', 'c', 'd'])
        self.checkequal('abcd', '', 'join', ('a', 'b', 'c', 'd'))
        self.checkequal('bd', '', 'join', ('', 'b', '', 'd'))
        self.checkequal('ac', '', 'join', ('a', '', 'c', ''))
        self.checkequal('w x y z', ' ', 'join', Sequence())
        self.checkequal('abc', 'a', 'join', ('abc',))
        self.checkequal('z', 'a', 'join', UserList(['z']))
        self.checkequal('a.b.c', '.', 'join', ['a', 'b', 'c'])
        self.assertRaises(TypeError, '.'.join, ['a', 'b', 3])
        dla i w [5, 25, 125]:
            self.checkequal(((('a' * i) + '-') * i)[:-1], '-', 'join',
                 ['a' * i] * i)
            self.checkequal(((('a' * i) + '-') * i)[:-1], '-', 'join',
                 ('a' * i,) * i)

        #self.checkequal(str(BadSeq1()), ' ', 'join', BadSeq1())
        self.checkequal('a b c', ' ', 'join', BadSeq2())

        self.checkraises(TypeError, ' ', 'join')
        self.checkraises(TypeError, ' ', 'join', Nic)
        self.checkraises(TypeError, ' ', 'join', 7)
        self.checkraises(TypeError, ' ', 'join', [1, 2, bytes()])
        spróbuj:
            def f():
                uzyskaj 4 + ""
            self.fixtype(' ').join(f())
        wyjąwszy TypeError jako e:
            jeżeli '+' nie w str(e):
                self.fail('join() ate exception message')
        inaczej:
            self.fail('exception nie podnieśd')

    def test_formatting(self):
        self.checkequal('+hello+', '+%s+', '__mod__', 'hello')
        self.checkequal('+10+', '+%d+', '__mod__', 10)
        self.checkequal('a', "%c", '__mod__', "a")
        self.checkequal('a', "%c", '__mod__', "a")
        self.checkequal('"', "%c", '__mod__', 34)
        self.checkequal('$', "%c", '__mod__', 36)
        self.checkequal('10', "%d", '__mod__', 10)
        self.checkequal('\x7f', "%c", '__mod__', 0x7f)

        dla ordinal w (-100, 0x200000):
            # unicode podnieśs ValueError, str podnieśs OverflowError
            self.checkraises((ValueError, OverflowError), '%c', '__mod__', ordinal)

        longvalue = sys.maxsize + 10
        slongvalue = str(longvalue)
        self.checkequal(' 42', '%3ld', '__mod__', 42)
        self.checkequal('42', '%d', '__mod__', 42.0)
        self.checkequal(slongvalue, '%d', '__mod__', longvalue)
        self.checkcall('%d', '__mod__', float(longvalue))
        self.checkequal('0042.00', '%07.2f', '__mod__', 42)
        self.checkequal('0042.00', '%07.2F', '__mod__', 42)

        self.checkraises(TypeError, 'abc', '__mod__')
        self.checkraises(TypeError, '%(foo)s', '__mod__', 42)
        self.checkraises(TypeError, '%s%s', '__mod__', (42,))
        self.checkraises(TypeError, '%c', '__mod__', (Nic,))
        self.checkraises(ValueError, '%(foo', '__mod__', {})
        self.checkraises(TypeError, '%(foo)s %(bar)s', '__mod__', ('foo', 42))
        self.checkraises(TypeError, '%d', '__mod__', "42") # nie numeric
        self.checkraises(TypeError, '%d', '__mod__', (42+0j)) # no int conversion provided

        # argument names przy properly nested brackets are supported
        self.checkequal('bar', '%((foo))s', '__mod__', {'(foo)': 'bar'})

        # 100 jest a magic number w PyUnicode_Format, this forces a resize
        self.checkequal(103*'a'+'x', '%sx', '__mod__', 103*'a')

        self.checkraises(TypeError, '%*s', '__mod__', ('foo', 'bar'))
        self.checkraises(TypeError, '%10.*f', '__mod__', ('foo', 42.))
        self.checkraises(ValueError, '%10', '__mod__', (42,))

        # Outrageously large width albo precision should podnieś ValueError.
        self.checkraises(ValueError, '%%%df' % (2**64), '__mod__', (3.2))
        self.checkraises(ValueError, '%%.%df' % (2**64), '__mod__', (3.2))
        self.checkraises(OverflowError, '%*s', '__mod__',
                         (sys.maxsize + 1, ''))
        self.checkraises(OverflowError, '%.*f', '__mod__',
                         (sys.maxsize + 1, 1. / 7))

        klasa X(object): dalej
        self.checkraises(TypeError, 'abc', '__mod__', X())

    @support.cpython_only
    def test_formatting_c_limits(self):
        z _testcapi zaimportuj PY_SSIZE_T_MAX, INT_MAX, UINT_MAX
        SIZE_MAX = (1 << (PY_SSIZE_T_MAX.bit_length() + 1)) - 1
        self.checkraises(OverflowError, '%*s', '__mod__',
                         (PY_SSIZE_T_MAX + 1, ''))
        self.checkraises(OverflowError, '%.*f', '__mod__',
                         (INT_MAX + 1, 1. / 7))
        # Issue 15989
        self.checkraises(OverflowError, '%*s', '__mod__',
                         (SIZE_MAX + 1, ''))
        self.checkraises(OverflowError, '%.*f', '__mod__',
                         (UINT_MAX + 1, 1. / 7))

    def test_floatformatting(self):
        # float formatting
        dla prec w range(100):
            format = '%%.%if' % prec
            value = 0.01
            dla x w range(60):
                value = value * 3.14159265359 / 3.0 * 10.0
                self.checkcall(format, "__mod__", value)

    def test_inplace_rewrites(self):
        # Check that strings don't copy oraz modify cached single-character strings
        self.checkequal('a', 'A', 'lower')
        self.checkequal(Prawda, 'A', 'isupper')
        self.checkequal('A', 'a', 'upper')
        self.checkequal(Prawda, 'a', 'islower')

        self.checkequal('a', 'A', 'replace', 'A', 'a')
        self.checkequal(Prawda, 'A', 'isupper')

        self.checkequal('A', 'a', 'capitalize')
        self.checkequal(Prawda, 'a', 'islower')

        self.checkequal('A', 'a', 'swapcase')
        self.checkequal(Prawda, 'a', 'islower')

        self.checkequal('A', 'a', 'title')
        self.checkequal(Prawda, 'a', 'islower')

    def test_partition(self):

        self.checkequal(('this jest the par', 'ti', 'tion method'),
            'this jest the partition method', 'partition', 'ti')

        # z raymond's original specification
        S = 'http://www.python.org'
        self.checkequal(('http', '://', 'www.python.org'), S, 'partition', '://')
        self.checkequal(('http://www.python.org', '', ''), S, 'partition', '?')
        self.checkequal(('', 'http://', 'www.python.org'), S, 'partition', 'http://')
        self.checkequal(('http://www.python.', 'org', ''), S, 'partition', 'org')

        self.checkraises(ValueError, S, 'partition', '')
        self.checkraises(TypeError, S, 'partition', Nic)

    def test_rpartition(self):

        self.checkequal(('this jest the rparti', 'ti', 'on method'),
            'this jest the rpartition method', 'rpartition', 'ti')

        # z raymond's original specification
        S = 'http://www.python.org'
        self.checkequal(('http', '://', 'www.python.org'), S, 'rpartition', '://')
        self.checkequal(('', '', 'http://www.python.org'), S, 'rpartition', '?')
        self.checkequal(('', 'http://', 'www.python.org'), S, 'rpartition', 'http://')
        self.checkequal(('http://www.python.', 'org', ''), S, 'rpartition', 'org')

        self.checkraises(ValueError, S, 'rpartition', '')
        self.checkraises(TypeError, S, 'rpartition', Nic)

    def test_none_arguments(self):
        # issue 11828
        s = 'hello'
        self.checkequal(2, s, 'find', 'l', Nic)
        self.checkequal(3, s, 'find', 'l', -2, Nic)
        self.checkequal(2, s, 'find', 'l', Nic, -2)
        self.checkequal(0, s, 'find', 'h', Nic, Nic)

        self.checkequal(3, s, 'rfind', 'l', Nic)
        self.checkequal(3, s, 'rfind', 'l', -2, Nic)
        self.checkequal(2, s, 'rfind', 'l', Nic, -2)
        self.checkequal(0, s, 'rfind', 'h', Nic, Nic)

        self.checkequal(2, s, 'index', 'l', Nic)
        self.checkequal(3, s, 'index', 'l', -2, Nic)
        self.checkequal(2, s, 'index', 'l', Nic, -2)
        self.checkequal(0, s, 'index', 'h', Nic, Nic)

        self.checkequal(3, s, 'rindex', 'l', Nic)
        self.checkequal(3, s, 'rindex', 'l', -2, Nic)
        self.checkequal(2, s, 'rindex', 'l', Nic, -2)
        self.checkequal(0, s, 'rindex', 'h', Nic, Nic)

        self.checkequal(2, s, 'count', 'l', Nic)
        self.checkequal(1, s, 'count', 'l', -2, Nic)
        self.checkequal(1, s, 'count', 'l', Nic, -2)
        self.checkequal(0, s, 'count', 'x', Nic, Nic)

        self.checkequal(Prawda, s, 'endswith', 'o', Nic)
        self.checkequal(Prawda, s, 'endswith', 'lo', -2, Nic)
        self.checkequal(Prawda, s, 'endswith', 'l', Nic, -2)
        self.checkequal(Nieprawda, s, 'endswith', 'x', Nic, Nic)

        self.checkequal(Prawda, s, 'startswith', 'h', Nic)
        self.checkequal(Prawda, s, 'startswith', 'l', -2, Nic)
        self.checkequal(Prawda, s, 'startswith', 'h', Nic, -2)
        self.checkequal(Nieprawda, s, 'startswith', 'x', Nic, Nic)

    def test_find_etc_raise_correct_error_messages(self):
        # issue 11828
        s = 'hello'
        x = 'x'
        self.assertRaisesRegex(TypeError, r'^find\(', s.find,
                                x, Nic, Nic, Nic)
        self.assertRaisesRegex(TypeError, r'^rfind\(', s.rfind,
                                x, Nic, Nic, Nic)
        self.assertRaisesRegex(TypeError, r'^index\(', s.index,
                                x, Nic, Nic, Nic)
        self.assertRaisesRegex(TypeError, r'^rindex\(', s.rindex,
                                x, Nic, Nic, Nic)
        self.assertRaisesRegex(TypeError, r'^count\(', s.count,
                                x, Nic, Nic, Nic)
        self.assertRaisesRegex(TypeError, r'^startswith\(', s.startswith,
                                x, Nic, Nic, Nic)
        self.assertRaisesRegex(TypeError, r'^endswith\(', s.endswith,
                                x, Nic, Nic, Nic)

        # issue #15534
        self.checkequal(10, "...\u043c......<", "find", "<")


klasa MixinStrUnicodeTest:
    # Additional tests that only work przy str oraz unicode.

    def test_bug1001011(self):
        # Make sure join returns a NEW object dla single item sequences
        # involving a subclass.
        # Make sure that it jest of the appropriate type.
        # Check the optimisation still occurs dla standard objects.
        t = self.type2test
        klasa subclass(t):
            dalej
        s1 = subclass("abcd")
        s2 = t().join([s1])
        self.assertIsNot(s1, s2)
        self.assertIs(type(s2), t)

        s1 = t("abcd")
        s2 = t().join([s1])
        self.assertIs(s1, s2)

        # Should also test mixed-type join.
        jeżeli t jest str:
            s1 = subclass("abcd")
            s2 = "".join([s1])
            self.assertIsNot(s1, s2)
            self.assertIs(type(s2), t)

            s1 = t("abcd")
            s2 = "".join([s1])
            self.assertIs(s1, s2)

##         albo_inaczej t jest str8:
##             s1 = subclass("abcd")
##             s2 = "".join([s1])
##             self.assertIsNot(s1, s2)
##             self.assertIs(type(s2), str) # promotes!

##             s1 = t("abcd")
##             s2 = "".join([s1])
##             self.assertIsNot(s1, s2)
##             self.assertIs(type(s2), str) # promotes!

        inaczej:
            self.fail("unexpected type dla MixinStrUnicodeTest %r" % t)
