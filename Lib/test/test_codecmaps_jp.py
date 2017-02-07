#
# test_codecmaps_jp.py
#   Codec mapping tests dla Japanese encodings
#

z test zaimportuj support
z test zaimportuj multibytecodec_support
zaimportuj unittest

klasa TestCP932Map(multibytecodec_support.TestBase_Mapping,
                   unittest.TestCase):
    encoding = 'cp932'
    mapfileurl = 'http://www.pythontest.net/unicode/CP932.TXT'
    supmaps = [
        (b'\x80', '\u0080'),
        (b'\xa0', '\uf8f0'),
        (b'\xfd', '\uf8f1'),
        (b'\xfe', '\uf8f2'),
        (b'\xff', '\uf8f3'),
    ]
    dla i w range(0xa1, 0xe0):
        supmaps.append((bytes([i]), chr(i+0xfec0)))


klasa TestEUCJPCOMPATMap(multibytecodec_support.TestBase_Mapping,
                         unittest.TestCase):
    encoding = 'euc_jp'
    mapfilename = 'EUC-JP.TXT'
    mapfileurl = 'http://www.pythontest.net/unicode/EUC-JP.TXT'


klasa TestSJISCOMPATMap(multibytecodec_support.TestBase_Mapping,
                        unittest.TestCase):
    encoding = 'shift_jis'
    mapfilename = 'SHIFTJIS.TXT'
    mapfileurl = 'http://www.pythontest.net/unicode/SHIFTJIS.TXT'
    dalej_enctest = [
        (b'\x81_', '\\'),
    ]
    dalej_dectest = [
        (b'\\', '\xa5'),
        (b'~', '\u203e'),
        (b'\x81_', '\\'),
    ]

klasa TestEUCJISX0213Map(multibytecodec_support.TestBase_Mapping,
                         unittest.TestCase):
    encoding = 'euc_jisx0213'
    mapfilename = 'EUC-JISX0213.TXT'
    mapfileurl = 'http://www.pythontest.net/unicode/EUC-JISX0213.TXT'


klasa TestSJISX0213Map(multibytecodec_support.TestBase_Mapping,
                       unittest.TestCase):
    encoding = 'shift_jisx0213'
    mapfilename = 'SHIFT_JISX0213.TXT'
    mapfileurl = 'http://www.pythontest.net/unicode/SHIFT_JISX0213.TXT'


jeżeli __name__ == "__main__":
    unittest.main()
