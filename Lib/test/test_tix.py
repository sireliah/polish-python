zaimportuj unittest
z test zaimportuj support
zaimportuj sys

# Skip this test jeżeli the _tkinter module wasn't built.
_tkinter = support.import_module('_tkinter')

# Skip test jeżeli tk cannot be initialized.
support.requires('gui')

z tkinter zaimportuj tix, TclError


klasa TestTix(unittest.TestCase):

    def setUp(self):
        spróbuj:
            self.root = tix.Tk()
        wyjąwszy TclError:
            jeżeli sys.platform.startswith('win'):
                self.fail('Tix should always be available on Windows')
            self.skipTest('Tix nie available')
        inaczej:
            self.addCleanup(self.root.destroy)

    def test_tix_available(self):
        # this test jest just here to make setUp run
        dalej


jeżeli __name__ == '__main__':
    unittest.main()
