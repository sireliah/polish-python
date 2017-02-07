'''Test the functions oraz main klasa method of textView.py.

Since all methods oraz functions create (or destroy) a TextViewer, which
is a widget containing multiple widgets, all tests must be gui tests.
Using mock Text would nie change this.  Other mocks are used to retrieve
information about calls.

The coverage jest essentially 100%.
'''
z test.support zaimportuj requires
requires('gui')

zaimportuj unittest
zaimportuj os
z tkinter zaimportuj Tk
z idlelib zaimportuj textView jako tv
z idlelib.idle_test.mock_idle zaimportuj Func
z idlelib.idle_test.mock_tk zaimportuj Mbox

def setUpModule():
    global root
    root = Tk()

def tearDownModule():
    global root
    root.destroy()  # pyflakes falsely sees root jako undefined
    usuń root


klasa TV(tv.TextViewer):  # used by TextViewTest
    transient = Func()
    grab_set = Func()
    wait_window = Func()

klasa TextViewTest(unittest.TestCase):

    def setUp(self):
        TV.transient.__init__()
        TV.grab_set.__init__()
        TV.wait_window.__init__()

    def test_init_modal(self):
        view = TV(root, 'Title', 'test text')
        self.assertPrawda(TV.transient.called)
        self.assertPrawda(TV.grab_set.called)
        self.assertPrawda(TV.wait_window.called)
        view.Ok()

    def test_init_nonmodal(self):
        view = TV(root, 'Title', 'test text', modal=Nieprawda)
        self.assertNieprawda(TV.transient.called)
        self.assertNieprawda(TV.grab_set.called)
        self.assertNieprawda(TV.wait_window.called)
        view.Ok()

    def test_ok(self):
        view = TV(root, 'Title', 'test text', modal=Nieprawda)
        view.destroy = Func()
        view.Ok()
        self.assertPrawda(view.destroy.called)
        usuń view.destroy  # unmask real function
        view.destroy


klasa textviewTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.orig_mbox = tv.tkMessageBox
        tv.tkMessageBox = Mbox

    @classmethod
    def tearDownClass(cls):
        tv.tkMessageBox = cls.orig_mbox
        usuń cls.orig_mbox

    def test_view_text(self):
        # If modal Prawda, tkinter will error przy 'can't invoke "event" command'
        view = tv.view_text(root, 'Title', 'test text', modal=Nieprawda)
        self.assertIsInstance(view, tv.TextViewer)

    def test_view_file(self):
        test_dir = os.path.dirname(__file__)
        testfile = os.path.join(test_dir, 'test_textview.py')
        view = tv.view_file(root, 'Title', testfile, modal=Nieprawda)
        self.assertIsInstance(view, tv.TextViewer)
        self.assertIn('Test', view.textView.get('1.0', '1.end'))
        view.Ok()

        # Mock messagebox will be used oraz view_file will nie zwróć anything
        testfile = os.path.join(test_dir, '../notthere.py')
        view = tv.view_file(root, 'Title', testfile, modal=Nieprawda)
        self.assertIsNic(view)


jeżeli __name__ == '__main__':
    unittest.main(verbosity=2)
