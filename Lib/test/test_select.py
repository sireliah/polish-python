zaimportuj errno
zaimportuj os
zaimportuj select
zaimportuj sys
zaimportuj unittest
z test zaimportuj support

@unittest.skipIf((sys.platform[:3]=='win'),
                 "can't easily test on this system")
klasa SelectTestCase(unittest.TestCase):

    klasa Nope:
        dalej

    klasa Almost:
        def fileno(self):
            zwróć 'fileno'

    def test_error_conditions(self):
        self.assertRaises(TypeError, select.select, 1, 2, 3)
        self.assertRaises(TypeError, select.select, [self.Nope()], [], [])
        self.assertRaises(TypeError, select.select, [self.Almost()], [], [])
        self.assertRaises(TypeError, select.select, [], [], [], "not a number")
        self.assertRaises(ValueError, select.select, [], [], [], -1)

    # Issue #12367: http://www.freebsd.org/cgi/query-pr.cgi?pr=kern/155606
    @unittest.skipIf(sys.platform.startswith('freebsd'),
                     'skip because of a FreeBSD bug: kern/155606')
    def test_errno(self):
        przy open(__file__, 'rb') jako fp:
            fd = fp.fileno()
            fp.close()
            spróbuj:
                select.select([fd], [], [], 0)
            wyjąwszy OSError jako err:
                self.assertEqual(err.errno, errno.EBADF)
            inaczej:
                self.fail("exception nie podnieśd")

    def test_returned_list_identity(self):
        # See issue #8329
        r, w, x = select.select([], [], [], 1)
        self.assertIsNot(r, w)
        self.assertIsNot(r, x)
        self.assertIsNot(w, x)

    def test_select(self):
        cmd = 'dla i w 0 1 2 3 4 5 6 7 8 9; do echo testing...; sleep 1; done'
        p = os.popen(cmd, 'r')
        dla tout w (0, 1, 2, 4, 8, 16) + (Nic,)*10:
            jeżeli support.verbose:
                print('timeout =', tout)
            rfd, wfd, xfd = select.select([p], [], [], tout)
            jeżeli (rfd, wfd, xfd) == ([], [], []):
                kontynuuj
            jeżeli (rfd, wfd, xfd) == ([p], [], []):
                line = p.readline()
                jeżeli support.verbose:
                    print(repr(line))
                jeżeli nie line:
                    jeżeli support.verbose:
                        print('EOF')
                    przerwij
                kontynuuj
            self.fail('Unexpected zwróć values z select():', rfd, wfd, xfd)
        p.close()

    # Issue 16230: Crash on select resized list
    def test_select_mutated(self):
        a = []
        klasa F:
            def fileno(self):
                usuń a[-1]
                zwróć sys.__stdout__.fileno()
        a[:] = [F()] * 10
        self.assertEqual(select.select([], a, []), ([], a[:5], []))

def tearDownModule():
    support.reap_children()

jeżeli __name__ == "__main__":
    unittest.main()
