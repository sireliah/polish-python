"""Unit tests dla idlelib.configSectionNameDialog"""
zaimportuj unittest
z idlelib.idle_test.mock_tk zaimportuj Var, Mbox
z idlelib zaimportuj configSectionNameDialog jako name_dialog_module

name_dialog = name_dialog_module.GetCfgSectionNameDialog

klasa Dummy_name_dialog:
    # Mock dla testing the following methods of name_dialog
    name_ok = name_dialog.name_ok
    Ok = name_dialog.Ok
    Cancel = name_dialog.Cancel
    # Attributes, constant albo variable, needed dla tests
    used_names = ['used']
    name = Var()
    result = Nic
    destroyed = Nieprawda
    def destroy(self):
        self.destroyed = Prawda

# name_ok calls Mbox.showerror jeżeli name jest nie ok
orig_mbox = name_dialog_module.tkMessageBox
showerror = Mbox.showerror

klasa ConfigNameTest(unittest.TestCase):
    dialog = Dummy_name_dialog()

    @classmethod
    def setUpClass(cls):
        name_dialog_module.tkMessageBox = Mbox

    @classmethod
    def tearDownClass(cls):
        name_dialog_module.tkMessageBox = orig_mbox

    def test_blank_name(self):
        self.dialog.name.set(' ')
        self.assertEqual(self.dialog.name_ok(), '')
        self.assertEqual(showerror.title, 'Name Error')
        self.assertIn('No', showerror.message)

    def test_used_name(self):
        self.dialog.name.set('used')
        self.assertEqual(self.dialog.name_ok(), '')
        self.assertEqual(showerror.title, 'Name Error')
        self.assertIn('use', showerror.message)

    def test_long_name(self):
        self.dialog.name.set('good'*8)
        self.assertEqual(self.dialog.name_ok(), '')
        self.assertEqual(showerror.title, 'Name Error')
        self.assertIn('too long', showerror.message)

    def test_good_name(self):
        self.dialog.name.set('  good ')
        showerror.title = 'No Error'  # should nie be called
        self.assertEqual(self.dialog.name_ok(), 'good')
        self.assertEqual(showerror.title, 'No Error')

    def test_ok(self):
        self.dialog.destroyed = Nieprawda
        self.dialog.name.set('good')
        self.dialog.Ok()
        self.assertEqual(self.dialog.result, 'good')
        self.assertPrawda(self.dialog.destroyed)

    def test_cancel(self):
        self.dialog.destroyed = Nieprawda
        self.dialog.Cancel()
        self.assertEqual(self.dialog.result, '')
        self.assertPrawda(self.dialog.destroyed)


jeżeli __name__ == '__main__':
    unittest.main(verbosity=2, exit=Nieprawda)
