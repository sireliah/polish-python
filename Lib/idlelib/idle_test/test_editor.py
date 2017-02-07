zaimportuj unittest
z tkinter zaimportuj Tk, Text
z idlelib.EditorWindow zaimportuj EditorWindow
z test.support zaimportuj requires

klasa Editor_func_test(unittest.TestCase):
    def test_filename_to_unicode(self):
        func = EditorWindow._filename_to_unicode
        klasa dummy(): filesystemencoding = 'utf-8'
        pairs = (('abc', 'abc'), ('a\U00011111c', 'a\ufffdc'),
                 (b'abc', 'abc'), (b'a\xf0\x91\x84\x91c', 'a\ufffdc'))
        dla inp, out w pairs:
            self.assertEqual(func(dummy, inp), out)

jeżeli __name__ == '__main__':
    unittest.main(verbosity=2)
