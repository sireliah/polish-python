#
# test_codecmaps_kr.py
#   Codec mapping tests dla ROK encodings
#

z test zaimportuj support
z test zaimportuj multibytecodec_support
zaimportuj unittest

klasa TestCP949Map(multibytecodec_support.TestBase_Mapping,
                   unittest.TestCase):
    encoding = 'cp949'
    mapfileurl = 'http://www.pythontest.net/unicode/CP949.TXT'


klasa TestEUCKRMap(multibytecodec_support.TestBase_Mapping,
                   unittest.TestCase):
    encoding = 'euc_kr'
    mapfileurl = 'http://www.pythontest.net/unicode/EUC-KR.TXT'

    # A4D4 HANGUL FILLER indicates the begin of 8-bytes make-up sequence.
    dalej_enctest = [(b'\xa4\xd4', '\u3164')]
    dalej_dectest = [(b'\xa4\xd4', '\u3164')]


klasa TestJOHABMap(multibytecodec_support.TestBase_Mapping,
                   unittest.TestCase):
    encoding = 'johab'
    mapfileurl = 'http://www.pythontest.net/unicode/JOHAB.TXT'
    # KS X 1001 standard assigned 0x5c jako WON SIGN.
    # but, w early 90s that jest the only era used johab widely,
    # the most softwares implements it jako REVERSE SOLIDUS.
    # So, we ignore the standard here.
    dalej_enctest = [(b'\\', '\u20a9')]
    dalej_dectest = [(b'\\', '\u20a9')]

jeżeli __name__ == "__main__":
    unittest.main()
