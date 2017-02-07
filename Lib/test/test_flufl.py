zaimportuj __future__
zaimportuj unittest

klasa FLUFLTests(unittest.TestCase):

    def test_barry_as_bdfl(self):
        code = "z __future__ zaimportuj barry_as_FLUFL; 2 {0} 3"
        compile(code.format('<>'), '<BDFL test>', 'exec',
                __future__.CO_FUTURE_BARRY_AS_BDFL)
        self.assertRaises(SyntaxError, compile, code.format('!='),
                            '<FLUFL test>', 'exec',
                            __future__.CO_FUTURE_BARRY_AS_BDFL)

    def test_guido_as_bdfl(self):
        code = '2 {0} 3'
        compile(code.format('!='), '<BDFL test>', 'exec')
        self.assertRaises(SyntaxError, compile, code.format('<>'),
                            '<FLUFL test>', 'exec')


jeżeli __name__ == '__main__':
    unittest.main()
