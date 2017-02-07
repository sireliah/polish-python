'''Unittests dla idlelib/configHandler.py

Coverage: 46% just by creating dialog. The other half jest change code.

'''
zaimportuj unittest
z test.support zaimportuj requires
z tkinter zaimportuj Tk
z idlelib.configDialog zaimportuj ConfigDialog
z idlelib.macosxSupport zaimportuj _initializeTkVariantTests


klasa ConfigDialogTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        _initializeTkVariantTests(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()
        usuń cls.root

    def test_dialog(self):
        d=ConfigDialog(self.root, 'Test', _utest=Prawda)
        d.destroy()


jeżeli __name__ == '__main__':
    unittest.main(verbosity=2)
