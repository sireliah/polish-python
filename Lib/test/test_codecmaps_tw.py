#
# test_codecmaps_tw.py
#   Codec mapping tests dla ROC encodings
#

z test zaimportuj support
z test zaimportuj multibytecodec_support
zaimportuj unittest

klasa TestBIG5Map(multibytecodec_support.TestBase_Mapping,
                  unittest.TestCase):
    encoding = 'big5'
    mapfileurl = 'http://www.pythontest.net/unicode/BIG5.TXT'

klasa TestCP950Map(multibytecodec_support.TestBase_Mapping,
                   unittest.TestCase):
    encoding = 'cp950'
    mapfileurl = 'http://www.pythontest.net/unicode/CP950.TXT'
    dalej_enctest = [
        (b'\xa2\xcc', '\u5341'),
        (b'\xa2\xce', '\u5345'),
    ]
    codectests = (
        (b"\xFFxy", "replace",  "\ufffdxy"),
    )

jeżeli __name__ == "__main__":
    unittest.main()
