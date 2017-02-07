"""Tests dla distutils.command.check."""
zaimportuj textwrap
zaimportuj unittest
z test.support zaimportuj run_unittest

z distutils.command.check zaimportuj check, HAS_DOCUTILS
z distutils.tests zaimportuj support
z distutils.errors zaimportuj DistutilsSetupError

klasa CheckTestCase(support.LoggingSilencer,
                    support.TempdirManager,
                    unittest.TestCase):

    def _run(self, metadata=Nic, **options):
        jeżeli metadata jest Nic:
            metadata = {}
        pkg_info, dist = self.create_dist(**metadata)
        cmd = check(dist)
        cmd.initialize_options()
        dla name, value w options.items():
            setattr(cmd, name, value)
        cmd.ensure_finalized()
        cmd.run()
        zwróć cmd

    def test_check_metadata(self):
        # let's run the command przy no metadata at all
        # by default, check jest checking the metadata
        # should have some warnings
        cmd = self._run()
        self.assertEqual(cmd._warnings, 2)

        # now let's add the required fields
        # oraz run it again, to make sure we don't get
        # any warning anymore
        metadata = {'url': 'xxx', 'author': 'xxx',
                    'author_email': 'xxx',
                    'name': 'xxx', 'version': 'xxx'}
        cmd = self._run(metadata)
        self.assertEqual(cmd._warnings, 0)

        # now przy the strict mode, we should
        # get an error jeżeli there are missing metadata
        self.assertRaises(DistutilsSetupError, self._run, {}, **{'strict': 1})

        # oraz of course, no error when all metadata are present
        cmd = self._run(metadata, strict=1)
        self.assertEqual(cmd._warnings, 0)

        # now a test przy non-ASCII characters
        metadata = {'url': 'xxx', 'author': '\u00c9ric',
                    'author_email': 'xxx', 'name': 'xxx',
                    'version': 'xxx',
                    'description': 'Something about esszet \u00df',
                    'long_description': 'More things about esszet \u00df'}
        cmd = self._run(metadata)
        self.assertEqual(cmd._warnings, 0)

    @unittest.skipUnless(HAS_DOCUTILS, "won't test without docutils")
    def test_check_document(self):
        pkg_info, dist = self.create_dist()
        cmd = check(dist)

        # let's see jeżeli it detects broken rest
        broken_rest = 'title\n===\n\ntest'
        msgs = cmd._check_rst_data(broken_rest)
        self.assertEqual(len(msgs), 1)

        # oraz non-broken rest
        rest = 'title\n=====\n\ntest'
        msgs = cmd._check_rst_data(rest)
        self.assertEqual(len(msgs), 0)

    @unittest.skipUnless(HAS_DOCUTILS, "won't test without docutils")
    def test_check_restructuredtext(self):
        # let's see jeżeli it detects broken rest w long_description
        broken_rest = 'title\n===\n\ntest'
        pkg_info, dist = self.create_dist(long_description=broken_rest)
        cmd = check(dist)
        cmd.check_restructuredtext()
        self.assertEqual(cmd._warnings, 1)

        # let's see jeżeli we have an error przy strict=1
        metadata = {'url': 'xxx', 'author': 'xxx',
                    'author_email': 'xxx',
                    'name': 'xxx', 'version': 'xxx',
                    'long_description': broken_rest}
        self.assertRaises(DistutilsSetupError, self._run, metadata,
                          **{'strict': 1, 'restructuredtext': 1})

        # oraz non-broken rest, including a non-ASCII character to test #12114
        metadata['long_description'] = 'title\n=====\n\ntest \u00df'
        cmd = self._run(metadata, strict=1, restructuredtext=1)
        self.assertEqual(cmd._warnings, 0)

    @unittest.skipUnless(HAS_DOCUTILS, "won't test without docutils")
    def test_check_restructuredtext_with_syntax_highlight(self):
        # Don't fail jeżeli there jest a `code` albo `code-block` directive

        example_rst_docs = []
        example_rst_docs.append(textwrap.dedent("""\
            Here's some code:

            .. code:: python

                def foo():
                    dalej
            """))
        example_rst_docs.append(textwrap.dedent("""\
            Here's some code:

            .. code-block:: python

                def foo():
                    dalej
            """))

        dla rest_with_code w example_rst_docs:
            pkg_info, dist = self.create_dist(long_description=rest_with_code)
            cmd = check(dist)
            cmd.check_restructuredtext()
            self.assertEqual(cmd._warnings, 0)
            msgs = cmd._check_rst_data(rest_with_code)
            self.assertEqual(len(msgs), 0)

    def test_check_all(self):

        metadata = {'url': 'xxx', 'author': 'xxx'}
        self.assertRaises(DistutilsSetupError, self._run,
                          {}, **{'strict': 1,
                                 'restructuredtext': 1})

def test_suite():
    zwróć unittest.makeSuite(CheckTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
