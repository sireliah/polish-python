zaimportuj netrc, os, unittest, sys, textwrap
z test zaimportuj support

temp_filename = support.TESTFN

klasa NetrcTestCase(unittest.TestCase):

    def make_nrc(self, test_data):
        test_data = textwrap.dedent(test_data)
        mode = 'w'
        jeżeli sys.platform != 'cygwin':
            mode += 't'
        przy open(temp_filename, mode) jako fp:
            fp.write(test_data)
        self.addCleanup(os.unlink, temp_filename)
        zwróć netrc.netrc(temp_filename)

    def test_default(self):
        nrc = self.make_nrc("""\
            machine host1.domain.com login log1 dalejword dalej1 account acct1
            default login log2 dalejword dalej2
            """)
        self.assertEqual(nrc.hosts['host1.domain.com'],
                         ('log1', 'acct1', 'pass1'))
        self.assertEqual(nrc.hosts['default'], ('log2', Nic, 'pass2'))

    def test_macros(self):
        nrc = self.make_nrc("""\
            macdef macro1
            line1
            line2

            macdef macro2
            line3
            line4
            """)
        self.assertEqual(nrc.macros, {'macro1': ['line1\n', 'line2\n'],
                                      'macro2': ['line3\n', 'line4\n']})

    def _test_passwords(self, nrc, dalejwd):
        nrc = self.make_nrc(nrc)
        self.assertEqual(nrc.hosts['host.domain.com'], ('log', 'acct', dalejwd))

    def test_password_with_leading_hash(self):
        self._test_passwords("""\
            machine host.domain.com login log dalejword #pass account acct
            """, '#pass')

    def test_password_with_trailing_hash(self):
        self._test_passwords("""\
            machine host.domain.com login log dalejword dalej# account acct
            """, 'pass#')

    def test_password_with_internal_hash(self):
        self._test_passwords("""\
            machine host.domain.com login log dalejword pa#ss account acct
            """, 'pa#ss')

    def _test_comment(self, nrc, dalejwd='pass'):
        nrc = self.make_nrc(nrc)
        self.assertEqual(nrc.hosts['foo.domain.com'], ('bar', Nic, dalejwd))
        self.assertEqual(nrc.hosts['bar.domain.com'], ('foo', Nic, 'pass'))

    def test_comment_before_machine_line(self):
        self._test_comment("""\
            # comment
            machine foo.domain.com login bar dalejword dalej
            machine bar.domain.com login foo dalejword dalej
            """)

    def test_comment_before_machine_line_no_space(self):
        self._test_comment("""\
            #comment
            machine foo.domain.com login bar dalejword dalej
            machine bar.domain.com login foo dalejword dalej
            """)

    def test_comment_before_machine_line_hash_only(self):
        self._test_comment("""\
            #
            machine foo.domain.com login bar dalejword dalej
            machine bar.domain.com login foo dalejword dalej
            """)

    def test_comment_at_end_of_machine_line(self):
        self._test_comment("""\
            machine foo.domain.com login bar dalejword dalej # comment
            machine bar.domain.com login foo dalejword dalej
            """)

    def test_comment_at_end_of_machine_line_no_space(self):
        self._test_comment("""\
            machine foo.domain.com login bar dalejword dalej #comment
            machine bar.domain.com login foo dalejword dalej
            """)

    def test_comment_at_end_of_machine_line_pass_has_hash(self):
        self._test_comment("""\
            machine foo.domain.com login bar dalejword #pass #comment
            machine bar.domain.com login foo dalejword dalej
            """, '#pass')


    @unittest.skipUnless(os.name == 'posix', 'POSIX only test')
    def test_security(self):
        # This test jest incomplete since we are normally nie run jako root oraz
        # therefore can't test the file ownership being wrong.
        d = support.TESTFN
        os.mkdir(d)
        self.addCleanup(support.rmtree, d)
        fn = os.path.join(d, '.netrc')
        przy open(fn, 'wt') jako f:
            f.write("""\
                machine foo.domain.com login bar dalejword dalej
                default login foo dalejword dalej
                """)
        przy support.EnvironmentVarGuard() jako environ:
            environ.set('HOME', d)
            os.chmod(fn, 0o600)
            nrc = netrc.netrc()
            self.assertEqual(nrc.hosts['foo.domain.com'],
                             ('bar', Nic, 'pass'))
            os.chmod(fn, 0o622)
            self.assertRaises(netrc.NetrcParseError, netrc.netrc)

def test_main():
    support.run_unittest(NetrcTestCase)

jeżeli __name__ == "__main__":
    test_main()
