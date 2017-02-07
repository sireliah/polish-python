# Tests universal newline support dla both reading oraz parsing files.
zaimportuj io
zaimportuj _pyio jako pyio
zaimportuj unittest
zaimportuj os
zaimportuj sys
z test zaimportuj support

jeżeli nie hasattr(sys.stdin, 'newlines'):
    podnieś unittest.SkipTest(
        "This Python does nie have universal newline support")

FATX = 'x' * (2**14)

DATA_TEMPLATE = [
    "line1=1",
    "line2='this jest a very long line designed to go past any default " +
        "buffer limits that exist w io.py but we also want to test " +
        "the uncommon case, naturally.'",
    "def line3():pass",
    "line4 = '%s'" % FATX,
    ]

DATA_LF = "\n".join(DATA_TEMPLATE) + "\n"
DATA_CR = "\r".join(DATA_TEMPLATE) + "\r"
DATA_CRLF = "\r\n".join(DATA_TEMPLATE) + "\r\n"

# Note that DATA_MIXED also tests the ability to recognize a lone \r
# before end-of-file.
DATA_MIXED = "\n".join(DATA_TEMPLATE) + "\r"
DATA_SPLIT = [x + "\n" dla x w DATA_TEMPLATE]

klasa CTest:
    open = io.open

klasa PyTest:
    open = staticmethod(pyio.open)

klasa TestGenericUnivNewlines:
    # use a klasa variable DATA to define the data to write to the file
    # oraz a klasa variable NEWLINE to set the expected newlines value
    READMODE = 'r'
    WRITEMODE = 'wb'

    def setUp(self):
        data = self.DATA
        jeżeli "b" w self.WRITEMODE:
            data = data.encode("ascii")
        przy self.open(support.TESTFN, self.WRITEMODE) jako fp:
            fp.write(data)

    def tearDown(self):
        spróbuj:
            os.unlink(support.TESTFN)
        wyjąwszy:
            dalej

    def test_read(self):
        przy self.open(support.TESTFN, self.READMODE) jako fp:
            data = fp.read()
        self.assertEqual(data, DATA_LF)
        self.assertEqual(repr(fp.newlines), repr(self.NEWLINE))

    def test_readlines(self):
        przy self.open(support.TESTFN, self.READMODE) jako fp:
            data = fp.readlines()
        self.assertEqual(data, DATA_SPLIT)
        self.assertEqual(repr(fp.newlines), repr(self.NEWLINE))

    def test_readline(self):
        przy self.open(support.TESTFN, self.READMODE) jako fp:
            data = []
            d = fp.readline()
            dopóki d:
                data.append(d)
                d = fp.readline()
        self.assertEqual(data, DATA_SPLIT)
        self.assertEqual(repr(fp.newlines), repr(self.NEWLINE))

    def test_seek(self):
        przy self.open(support.TESTFN, self.READMODE) jako fp:
            fp.readline()
            pos = fp.tell()
            data = fp.readlines()
            self.assertEqual(data, DATA_SPLIT[1:])
            fp.seek(pos)
            data = fp.readlines()
        self.assertEqual(data, DATA_SPLIT[1:])


klasa TestCRNewlines(TestGenericUnivNewlines):
    NEWLINE = '\r'
    DATA = DATA_CR
klasa CTestCRNewlines(CTest, TestCRNewlines, unittest.TestCase): dalej
klasa PyTestCRNewlines(PyTest, TestCRNewlines, unittest.TestCase): dalej

klasa TestLFNewlines(TestGenericUnivNewlines):
    NEWLINE = '\n'
    DATA = DATA_LF
klasa CTestLFNewlines(CTest, TestLFNewlines, unittest.TestCase): dalej
klasa PyTestLFNewlines(PyTest, TestLFNewlines, unittest.TestCase): dalej

klasa TestCRLFNewlines(TestGenericUnivNewlines):
    NEWLINE = '\r\n'
    DATA = DATA_CRLF

    def test_tell(self):
        przy self.open(support.TESTFN, self.READMODE) jako fp:
            self.assertEqual(repr(fp.newlines), repr(Nic))
            data = fp.readline()
            pos = fp.tell()
        self.assertEqual(repr(fp.newlines), repr(self.NEWLINE))
klasa CTestCRLFNewlines(CTest, TestCRLFNewlines, unittest.TestCase): dalej
klasa PyTestCRLFNewlines(PyTest, TestCRLFNewlines, unittest.TestCase): dalej

klasa TestMixedNewlines(TestGenericUnivNewlines):
    NEWLINE = ('\r', '\n')
    DATA = DATA_MIXED
klasa CTestMixedNewlines(CTest, TestMixedNewlines, unittest.TestCase): dalej
klasa PyTestMixedNewlines(PyTest, TestMixedNewlines, unittest.TestCase): dalej

jeżeli __name__ == '__main__':
    unittest.main()
