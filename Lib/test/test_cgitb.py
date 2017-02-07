z test.support zaimportuj temp_dir
z test.support.script_helper zaimportuj assert_python_failure
zaimportuj unittest
zaimportuj sys
zaimportuj cgitb

klasa TestCgitb(unittest.TestCase):

    def test_fonts(self):
        text = "Hello Robbie!"
        self.assertEqual(cgitb.small(text), "<small>{}</small>".format(text))
        self.assertEqual(cgitb.strong(text), "<strong>{}</strong>".format(text))
        self.assertEqual(cgitb.grey(text),
                         '<font color="#909090">{}</font>'.format(text))

    def test_blanks(self):
        self.assertEqual(cgitb.small(""), "")
        self.assertEqual(cgitb.strong(""), "")
        self.assertEqual(cgitb.grey(""), "")

    def test_html(self):
        spróbuj:
            podnieś ValueError("Hello World")
        wyjąwszy ValueError jako err:
            # If the html was templated we could do a bit more here.
            # At least check that we get details on what we just podnieśd.
            html = cgitb.html(sys.exc_info())
            self.assertIn("ValueError", html)
            self.assertIn(str(err), html)

    def test_text(self):
        spróbuj:
            podnieś ValueError("Hello World")
        wyjąwszy ValueError jako err:
            text = cgitb.text(sys.exc_info())
            self.assertIn("ValueError", text)
            self.assertIn("Hello World", text)

    def test_syshook_no_logdir_default_format(self):
        przy temp_dir() jako tracedir:
            rc, out, err = assert_python_failure(
                  '-c',
                  ('zaimportuj cgitb; cgitb.enable(logdir=%s); '
                   'raise ValueError("Hello World")') % repr(tracedir))
        out = out.decode(sys.getfilesystemencoding())
        self.assertIn("ValueError", out)
        self.assertIn("Hello World", out)
        # By default we emit HTML markup.
        self.assertIn('<p>', out)
        self.assertIn('</p>', out)

    def test_syshook_no_logdir_text_format(self):
        # Issue 12890: we were emitting the <p> tag w text mode.
        przy temp_dir() jako tracedir:
            rc, out, err = assert_python_failure(
                  '-c',
                  ('zaimportuj cgitb; cgitb.enable(format="text", logdir=%s); '
                   'raise ValueError("Hello World")') % repr(tracedir))
        out = out.decode(sys.getfilesystemencoding())
        self.assertIn("ValueError", out)
        self.assertIn("Hello World", out)
        self.assertNotIn('<p>', out)
        self.assertNotIn('</p>', out)


jeżeli __name__ == "__main__":
    unittest.main()
