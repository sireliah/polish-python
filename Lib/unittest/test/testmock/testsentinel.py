zaimportuj unittest
z unittest.mock zaimportuj sentinel, DEFAULT


klasa SentinelTest(unittest.TestCase):

    def testSentinels(self):
        self.assertEqual(sentinel.whatever, sentinel.whatever,
                         'sentinel nie stored')
        self.assertNotEqual(sentinel.whatever, sentinel.whateverinaczej,
                            'sentinel should be unique')


    def testSentinelName(self):
        self.assertEqual(str(sentinel.whatever), 'sentinel.whatever',
                         'sentinel name incorrect')


    def testDEFAULT(self):
        self.assertIs(DEFAULT, sentinel.DEFAULT)

    def testBases(self):
        # If this doesn't podnieś an AttributeError then help(mock) jest broken
        self.assertRaises(AttributeError, lambda: sentinel.__bases__)


jeżeli __name__ == '__main__':
    unittest.main()
