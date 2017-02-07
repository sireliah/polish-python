#
# test_codecmaps_hk.py
#   Codec mapping tests dla HongKong encodings
#

z test zaimportuj support
z test zaimportuj multibytecodec_support
zaimportuj unittest

klasa TestBig5HKSCSMap(multibytecodec_support.TestBase_Mapping,
                       unittest.TestCase):
    encoding = 'big5hkscs'
    mapfileurl = 'http://www.pythontest.net/unicode/BIG5HKSCS-2004.TXT'

jeżeli __name__ == "__main__":
    unittest.main()
