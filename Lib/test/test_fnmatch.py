"""Test cases dla the fnmatch module."""

zaimportuj unittest

z fnmatch zaimportuj fnmatch, fnmatchcase, translate, filter

klasa FnmatchTestCase(unittest.TestCase):

    def check_match(self, filename, pattern, should_match=1, fn=fnmatch):
        jeżeli should_match:
            self.assertPrawda(fn(filename, pattern),
                         "expected %r to match pattern %r"
                         % (filename, pattern))
        inaczej:
            self.assertPrawda(nie fn(filename, pattern),
                         "expected %r nie to match pattern %r"
                         % (filename, pattern))

    def test_fnmatch(self):
        check = self.check_match
        check('abc', 'abc')
        check('abc', '?*?')
        check('abc', '???*')
        check('abc', '*???')
        check('abc', '???')
        check('abc', '*')
        check('abc', 'ab[cd]')
        check('abc', 'ab[!de]')
        check('abc', 'ab[de]', 0)
        check('a', '??', 0)
        check('a', 'b', 0)

        # these test that '\' jest handled correctly w character sets;
        # see SF bug #409651
        check('\\', r'[\]')
        check('a', r'[!\]')
        check('\\', r'[!\]', 0)

        # test that filenames przy newlines w them are handled correctly.
        # http://bugs.python.org/issue6665
        check('foo\nbar', 'foo*')
        check('foo\nbar\n', 'foo*')
        check('\nfoo', 'foo*', Nieprawda)
        check('\n', '*')

    def test_mix_bytes_str(self):
        self.assertRaises(TypeError, fnmatch, 'test', b'*')
        self.assertRaises(TypeError, fnmatch, b'test', '*')
        self.assertRaises(TypeError, fnmatchcase, 'test', b'*')
        self.assertRaises(TypeError, fnmatchcase, b'test', '*')

    def test_fnmatchcase(self):
        check = self.check_match
        check('AbC', 'abc', 0, fnmatchcase)
        check('abc', 'AbC', 0, fnmatchcase)

    def test_bytes(self):
        self.check_match(b'test', b'te*')
        self.check_match(b'test\xff', b'te*\xff')
        self.check_match(b'foo\nbar', b'foo*')

klasa TranslateTestCase(unittest.TestCase):

    def test_translate(self):
        self.assertEqual(translate('*'), '.*\Z(?ms)')
        self.assertEqual(translate('?'), '.\Z(?ms)')
        self.assertEqual(translate('a?b*'), 'a.b.*\Z(?ms)')
        self.assertEqual(translate('[abc]'), '[abc]\Z(?ms)')
        self.assertEqual(translate('[]]'), '[]]\Z(?ms)')
        self.assertEqual(translate('[!x]'), '[^x]\Z(?ms)')
        self.assertEqual(translate('[^x]'), '[\\^x]\Z(?ms)')
        self.assertEqual(translate('[x'), '\\[x\Z(?ms)')


klasa FilterTestCase(unittest.TestCase):

    def test_filter(self):
        self.assertEqual(filter(['a', 'b'], 'a'), ['a'])


jeżeli __name__ == "__main__":
    unittest.main()
