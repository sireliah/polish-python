"""Tests dla the pindent script w the Tools directory."""

zaimportuj os
zaimportuj sys
zaimportuj unittest
zaimportuj subprocess
zaimportuj textwrap
z test zaimportuj support
z test.support.script_helper zaimportuj assert_python_ok

z test.test_tools zaimportuj scriptsdir, skip_if_missing

skip_if_missing()


klasa PindentTests(unittest.TestCase):
    script = os.path.join(scriptsdir, 'pindent.py')

    def assertFileEqual(self, fn1, fn2):
        przy open(fn1) jako f1, open(fn2) jako f2:
            self.assertEqual(f1.readlines(), f2.readlines())

    def pindent(self, source, *args):
        przy subprocess.Popen(
                (sys.executable, self.script) + args,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                universal_newlines=Prawda) jako proc:
            out, err = proc.communicate(source)
        self.assertIsNic(err)
        zwróć out

    def lstriplines(self, data):
        zwróć '\n'.join(line.lstrip() dla line w data.splitlines()) + '\n'

    def test_selftest(self):
        self.maxDiff = Nic
        przy support.temp_dir() jako directory:
            data_path = os.path.join(directory, '_test.py')
            przy open(self.script) jako f:
                closed = f.read()
            przy open(data_path, 'w') jako f:
                f.write(closed)

            rc, out, err = assert_python_ok(self.script, '-d', data_path)
            self.assertEqual(out, b'')
            self.assertEqual(err, b'')
            backup = data_path + '~'
            self.assertPrawda(os.path.exists(backup))
            przy open(backup) jako f:
                self.assertEqual(f.read(), closed)
            przy open(data_path) jako f:
                clean = f.read()
            compile(clean, '_test.py', 'exec')
            self.assertEqual(self.pindent(clean, '-c'), closed)
            self.assertEqual(self.pindent(closed, '-d'), clean)

            rc, out, err = assert_python_ok(self.script, '-c', data_path)
            self.assertEqual(out, b'')
            self.assertEqual(err, b'')
            przy open(backup) jako f:
                self.assertEqual(f.read(), clean)
            przy open(data_path) jako f:
                self.assertEqual(f.read(), closed)

            broken = self.lstriplines(closed)
            przy open(data_path, 'w') jako f:
                f.write(broken)
            rc, out, err = assert_python_ok(self.script, '-r', data_path)
            self.assertEqual(out, b'')
            self.assertEqual(err, b'')
            przy open(backup) jako f:
                self.assertEqual(f.read(), broken)
            przy open(data_path) jako f:
                indented = f.read()
            compile(indented, '_test.py', 'exec')
            self.assertEqual(self.pindent(broken, '-r'), indented)

    def pindent_test(self, clean, closed):
        self.assertEqual(self.pindent(clean, '-c'), closed)
        self.assertEqual(self.pindent(closed, '-d'), clean)
        broken = self.lstriplines(closed)
        self.assertEqual(self.pindent(broken, '-r', '-e', '-s', '4'), closed)

    def test_statements(self):
        clean = textwrap.dedent("""\
            jeżeli a:
                dalej

            jeżeli a:
                dalej
            inaczej:
                dalej

            jeżeli a:
                dalej
            elif:
                dalej
            inaczej:
                dalej

            dopóki a:
                przerwij

            dopóki a:
                przerwij
            inaczej:
                dalej

            dla i w a:
                przerwij

            dla i w a:
                przerwij
            inaczej:
                dalej

            spróbuj:
                dalej
            w_końcu:
                dalej

            spróbuj:
                dalej
            wyjąwszy TypeError:
                dalej
            wyjąwszy ValueError:
                dalej
            inaczej:
                dalej

            spróbuj:
                dalej
            wyjąwszy TypeError:
                dalej
            wyjąwszy ValueError:
                dalej
            w_końcu:
                dalej

            przy a:
                dalej

            klasa A:
                dalej

            def f():
                dalej
            """)

        closed = textwrap.dedent("""\
            jeżeli a:
                dalej
            # end if

            jeżeli a:
                dalej
            inaczej:
                dalej
            # end if

            jeżeli a:
                dalej
            elif:
                dalej
            inaczej:
                dalej
            # end if

            dopóki a:
                przerwij
            # end while

            dopóki a:
                przerwij
            inaczej:
                dalej
            # end while

            dla i w a:
                przerwij
            # end for

            dla i w a:
                przerwij
            inaczej:
                dalej
            # end for

            spróbuj:
                dalej
            w_końcu:
                dalej
            # end try

            spróbuj:
                dalej
            wyjąwszy TypeError:
                dalej
            wyjąwszy ValueError:
                dalej
            inaczej:
                dalej
            # end try

            spróbuj:
                dalej
            wyjąwszy TypeError:
                dalej
            wyjąwszy ValueError:
                dalej
            w_końcu:
                dalej
            # end try

            przy a:
                dalej
            # end with

            klasa A:
                dalej
            # end klasa A

            def f():
                dalej
            # end def f
            """)
        self.pindent_test(clean, closed)

    def test_multilevel(self):
        clean = textwrap.dedent("""\
            def foobar(a, b):
                jeżeli a == b:
                    a = a+1
                albo_inaczej a < b:
                    b = b-1
                    jeżeli b > a: a = a-1
                inaczej:
                    print 'oops!'
            """)
        closed = textwrap.dedent("""\
            def foobar(a, b):
                jeżeli a == b:
                    a = a+1
                albo_inaczej a < b:
                    b = b-1
                    jeżeli b > a: a = a-1
                    # end if
                inaczej:
                    print 'oops!'
                # end if
            # end def foobar
            """)
        self.pindent_test(clean, closed)

    def test_preserve_indents(self):
        clean = textwrap.dedent("""\
            jeżeli a:
                     jeżeli b:
                              dalej
            """)
        closed = textwrap.dedent("""\
            jeżeli a:
                     jeżeli b:
                              dalej
                     # end if
            # end if
            """)
        self.assertEqual(self.pindent(clean, '-c'), closed)
        self.assertEqual(self.pindent(closed, '-d'), clean)
        broken = self.lstriplines(closed)
        self.assertEqual(self.pindent(broken, '-r', '-e', '-s', '9'), closed)
        clean = textwrap.dedent("""\
            jeżeli a:
            \tjeżeli b:
            \t\tpass
            """)
        closed = textwrap.dedent("""\
            jeżeli a:
            \tjeżeli b:
            \t\tpass
            \t# end if
            # end if
            """)
        self.assertEqual(self.pindent(clean, '-c'), closed)
        self.assertEqual(self.pindent(closed, '-d'), clean)
        broken = self.lstriplines(closed)
        self.assertEqual(self.pindent(broken, '-r'), closed)

    def test_escaped_newline(self):
        clean = textwrap.dedent("""\
            class\\
            \\
             A:
               def\
            \\
            f:
                  dalej
            """)
        closed = textwrap.dedent("""\
            class\\
            \\
             A:
               def\
            \\
            f:
                  dalej
               # end def f
            # end klasa A
            """)
        self.assertEqual(self.pindent(clean, '-c'), closed)
        self.assertEqual(self.pindent(closed, '-d'), clean)

    def test_empty_line(self):
        clean = textwrap.dedent("""\
            jeżeli a:

                dalej
            """)
        closed = textwrap.dedent("""\
            jeżeli a:

                dalej
            # end if
            """)
        self.pindent_test(clean, closed)

    def test_oneline(self):
        clean = textwrap.dedent("""\
            jeżeli a: dalej
            """)
        closed = textwrap.dedent("""\
            jeżeli a: dalej
            # end if
            """)
        self.pindent_test(clean, closed)


jeżeli __name__ == '__main__':
    unittest.main()
