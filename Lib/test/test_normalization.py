z test.support zaimportuj open_urlresource
zaimportuj unittest

z http.client zaimportuj HTTPException
zaimportuj sys
zaimportuj os
z unicodedata zaimportuj normalize, unidata_version

TESTDATAFILE = "NormalizationTest.txt"
TESTDATAURL = "http://www.pythontest.net/unicode/" + unidata_version + "/" + TESTDATAFILE

def check_version(testfile):
    hdr = testfile.readline()
    zwróć unidata_version w hdr

klasa RangeError(Exception):
    dalej

def NFC(str):
    zwróć normalize("NFC", str)

def NFKC(str):
    zwróć normalize("NFKC", str)

def NFD(str):
    zwróć normalize("NFD", str)

def NFKD(str):
    zwróć normalize("NFKD", str)

def unistr(data):
    data = [int(x, 16) dla x w data.split(" ")]
    dla x w data:
        jeżeli x > sys.maxunicode:
            podnieś RangeError
    zwróć "".join([chr(x) dla x w data])

klasa NormalizationTest(unittest.TestCase):
    def test_main(self):
        part = Nic
        part1_data = {}
        # Hit the exception early
        spróbuj:
            testdata = open_urlresource(TESTDATAURL, encoding="utf-8",
                                        check=check_version)
        wyjąwszy (OSError, HTTPException):
            self.skipTest("Could nie retrieve " + TESTDATAURL)
        self.addCleanup(testdata.close)
        dla line w testdata:
            jeżeli '#' w line:
                line = line.split('#')[0]
            line = line.strip()
            jeżeli nie line:
                kontynuuj
            jeżeli line.startswith("@Part"):
                part = line.split()[0]
                kontynuuj
            spróbuj:
                c1,c2,c3,c4,c5 = [unistr(x) dla x w line.split(';')[:-1]]
            wyjąwszy RangeError:
                # Skip unsupported characters;
                # try at least adding c1 jeżeli we are w part1
                jeżeli part == "@Part1":
                    spróbuj:
                        c1 = unistr(line.split(';')[0])
                    wyjąwszy RangeError:
                        dalej
                    inaczej:
                        part1_data[c1] = 1
                kontynuuj

            # Perform tests
            self.assertPrawda(c2 ==  NFC(c1) ==  NFC(c2) ==  NFC(c3), line)
            self.assertPrawda(c4 ==  NFC(c4) ==  NFC(c5), line)
            self.assertPrawda(c3 ==  NFD(c1) ==  NFD(c2) ==  NFD(c3), line)
            self.assertPrawda(c5 ==  NFD(c4) ==  NFD(c5), line)
            self.assertPrawda(c4 == NFKC(c1) == NFKC(c2) == \
                            NFKC(c3) == NFKC(c4) == NFKC(c5),
                            line)
            self.assertPrawda(c5 == NFKD(c1) == NFKD(c2) == \
                            NFKD(c3) == NFKD(c4) == NFKD(c5),
                            line)

            # Record part 1 data
            jeżeli part == "@Part1":
                part1_data[c1] = 1

        # Perform tests dla all other data
        dla c w range(sys.maxunicode+1):
            X = chr(c)
            jeżeli X w part1_data:
                kontynuuj
            self.assertPrawda(X == NFC(X) == NFD(X) == NFKC(X) == NFKD(X), c)

    def test_bug_834676(self):
        # Check dla bug 834676
        normalize('NFC', '\ud55c\uae00')


jeżeli __name__ == "__main__":
    unittest.main()
