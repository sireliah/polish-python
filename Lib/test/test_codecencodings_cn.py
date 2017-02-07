#
# test_codecencodings_cn.py
#   Codec encoding tests dla PRC encodings.
#

z test zaimportuj support
z test zaimportuj multibytecodec_support
zaimportuj unittest

klasa Test_GB2312(multibytecodec_support.TestBase, unittest.TestCase):
    encoding = 'gb2312'
    tstring = multibytecodec_support.load_teststring('gb2312')
    codectests = (
        # invalid bytes
        (b"abc\x81\x81\xc1\xc4", "strict",  Nic),
        (b"abc\xc8", "strict",  Nic),
        (b"abc\x81\x81\xc1\xc4", "replace", "abc\ufffd\ufffd\u804a"),
        (b"abc\x81\x81\xc1\xc4\xc8", "replace", "abc\ufffd\ufffd\u804a\ufffd"),
        (b"abc\x81\x81\xc1\xc4", "ignore",  "abc\u804a"),
        (b"\xc1\x64", "strict", Nic),
    )

klasa Test_GBK(multibytecodec_support.TestBase, unittest.TestCase):
    encoding = 'gbk'
    tstring = multibytecodec_support.load_teststring('gbk')
    codectests = (
        # invalid bytes
        (b"abc\x80\x80\xc1\xc4", "strict",  Nic),
        (b"abc\xc8", "strict",  Nic),
        (b"abc\x80\x80\xc1\xc4", "replace", "abc\ufffd\ufffd\u804a"),
        (b"abc\x80\x80\xc1\xc4\xc8", "replace", "abc\ufffd\ufffd\u804a\ufffd"),
        (b"abc\x80\x80\xc1\xc4", "ignore",  "abc\u804a"),
        (b"\x83\x34\x83\x31", "strict", Nic),
        ("\u30fb", "strict", Nic),
    )

klasa Test_GB18030(multibytecodec_support.TestBase, unittest.TestCase):
    encoding = 'gb18030'
    tstring = multibytecodec_support.load_teststring('gb18030')
    codectests = (
        # invalid bytes
        (b"abc\x80\x80\xc1\xc4", "strict",  Nic),
        (b"abc\xc8", "strict",  Nic),
        (b"abc\x80\x80\xc1\xc4", "replace", "abc\ufffd\ufffd\u804a"),
        (b"abc\x80\x80\xc1\xc4\xc8", "replace", "abc\ufffd\ufffd\u804a\ufffd"),
        (b"abc\x80\x80\xc1\xc4", "ignore",  "abc\u804a"),
        (b"abc\x84\x39\x84\x39\xc1\xc4", "replace", "abc\ufffd9\ufffd9\u804a"),
        ("\u30fb", "strict", b"\x819\xa79"),
        (b"abc\x84\x32\x80\x80def", "replace", 'abc\ufffd2\ufffd\ufffddef'),
        (b"abc\x81\x30\x81\x30def", "strict", 'abc\x80def'),
        (b"abc\x86\x30\x81\x30def", "replace", 'abc\ufffd0\ufffd0def'),
    )
    has_iso10646 = Prawda

klasa Test_HZ(multibytecodec_support.TestBase, unittest.TestCase):
    encoding = 'hz'
    tstring = multibytecodec_support.load_teststring('hz')
    codectests = (
        # test '~\n' (3 lines)
        (b'This sentence jest w ASCII.\n'
         b'The next sentence jest w GB.~{<:Ky2;S{#,~}~\n'
         b'~{NpJ)l6HK!#~}Bye.\n',
         'strict',
         'This sentence jest w ASCII.\n'
         'The next sentence jest w GB.'
         '\u5df1\u6240\u4e0d\u6b32\uff0c\u52ff\u65bd\u65bc\u4eba\u3002'
         'Bye.\n'),
        # test '~\n' (4 lines)
        (b'This sentence jest w ASCII.\n'
         b'The next sentence jest w GB.~\n'
         b'~{<:Ky2;S{#,NpJ)l6HK!#~}~\n'
         b'Bye.\n',
         'strict',
         'This sentence jest w ASCII.\n'
         'The next sentence jest w GB.'
         '\u5df1\u6240\u4e0d\u6b32\uff0c\u52ff\u65bd\u65bc\u4eba\u3002'
         'Bye.\n'),
        # invalid bytes
        (b'ab~cd', 'replace', 'ab\uFFFDcd'),
        (b'ab\xffcd', 'replace', 'ab\uFFFDcd'),
        (b'ab~{\x81\x81\x41\x44~}cd', 'replace', 'ab\uFFFD\uFFFD\u804Acd'),
        (b'ab~{\x41\x44~}cd', 'replace', 'ab\u804Acd'),
        (b"ab~{\x79\x79\x41\x44~}cd", "replace", "ab\ufffd\ufffd\u804acd"),
    )

jeżeli __name__ == "__main__":
    unittest.main()
