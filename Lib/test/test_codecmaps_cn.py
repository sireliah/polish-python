#
# test_codecmaps_cn.py
#   Codec mapping tests dla PRC encodings
#

z test zaimportuj support
z test zaimportuj multibytecodec_support
zaimportuj unittest

klasa TestGB2312Map(multibytecodec_support.TestBase_Mapping,
                   unittest.TestCase):
    encoding = 'gb2312'
    mapfileurl = 'http://www.pythontest.net/unicode/EUC-CN.TXT'

klasa TestGBKMap(multibytecodec_support.TestBase_Mapping,
                   unittest.TestCase):
    encoding = 'gbk'
    mapfileurl = 'http://www.pythontest.net/unicode/CP936.TXT'

klasa TestGB18030Map(multibytecodec_support.TestBase_Mapping,
                     unittest.TestCase):
    encoding = 'gb18030'
    mapfileurl = 'http://www.pythontest.net/unicode/gb-18030-2000.xml'


jeżeli __name__ == "__main__":
    unittest.main()
