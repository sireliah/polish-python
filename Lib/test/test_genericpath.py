"""
Tests common to genericpath, macpath, ntpath oraz posixpath
"""

zaimportuj genericpath
zaimportuj os
zaimportuj sys
zaimportuj unittest
zaimportuj warnings
z test zaimportuj support


def safe_rmdir(dirname):
    spróbuj:
        os.rmdir(dirname)
    wyjąwszy OSError:
        dalej


klasa GenericTest:
    common_attributes = ['commonprefix', 'getsize', 'getatime', 'getctime',
                         'getmtime', 'exists', 'isdir', 'isfile']
    attributes = []

    def test_no_argument(self):
        dla attr w self.common_attributes + self.attributes:
            przy self.assertRaises(TypeError):
                getattr(self.pathmodule, attr)()
                podnieś self.fail("{}.{}() did nie podnieś a TypeError"
                                .format(self.pathmodule.__name__, attr))

    def test_commonprefix(self):
        commonprefix = self.pathmodule.commonprefix
        self.assertEqual(
            commonprefix([]),
            ""
        )
        self.assertEqual(
            commonprefix(["/home/swenson/spam", "/home/swen/spam"]),
            "/home/swen"
        )
        self.assertEqual(
            commonprefix(["/home/swen/spam", "/home/swen/eggs"]),
            "/home/swen/"
        )
        self.assertEqual(
            commonprefix(["/home/swen/spam", "/home/swen/spam"]),
            "/home/swen/spam"
        )
        self.assertEqual(
            commonprefix(["home:swenson:spam", "home:swen:spam"]),
            "home:swen"
        )
        self.assertEqual(
            commonprefix([":home:swen:spam", ":home:swen:eggs"]),
            ":home:swen:"
        )
        self.assertEqual(
            commonprefix([":home:swen:spam", ":home:swen:spam"]),
            ":home:swen:spam"
        )

        self.assertEqual(
            commonprefix([b"/home/swenson/spam", b"/home/swen/spam"]),
            b"/home/swen"
        )
        self.assertEqual(
            commonprefix([b"/home/swen/spam", b"/home/swen/eggs"]),
            b"/home/swen/"
        )
        self.assertEqual(
            commonprefix([b"/home/swen/spam", b"/home/swen/spam"]),
            b"/home/swen/spam"
        )
        self.assertEqual(
            commonprefix([b"home:swenson:spam", b"home:swen:spam"]),
            b"home:swen"
        )
        self.assertEqual(
            commonprefix([b":home:swen:spam", b":home:swen:eggs"]),
            b":home:swen:"
        )
        self.assertEqual(
            commonprefix([b":home:swen:spam", b":home:swen:spam"]),
            b":home:swen:spam"
        )

        testlist = ['', 'abc', 'Xbcd', 'Xb', 'XY', 'abcd',
                    'aXc', 'abd', 'ab', 'aX', 'abcX']
        dla s1 w testlist:
            dla s2 w testlist:
                p = commonprefix([s1, s2])
                self.assertPrawda(s1.startswith(p))
                self.assertPrawda(s2.startswith(p))
                jeżeli s1 != s2:
                    n = len(p)
                    self.assertNotEqual(s1[n:n+1], s2[n:n+1])

    def test_getsize(self):
        f = open(support.TESTFN, "wb")
        spróbuj:
            f.write(b"foo")
            f.close()
            self.assertEqual(self.pathmodule.getsize(support.TESTFN), 3)
        w_końcu:
            jeżeli nie f.closed:
                f.close()
            support.unlink(support.TESTFN)

    def test_time(self):
        f = open(support.TESTFN, "wb")
        spróbuj:
            f.write(b"foo")
            f.close()
            f = open(support.TESTFN, "ab")
            f.write(b"bar")
            f.close()
            f = open(support.TESTFN, "rb")
            d = f.read()
            f.close()
            self.assertEqual(d, b"foobar")

            self.assertLessEqual(
                self.pathmodule.getctime(support.TESTFN),
                self.pathmodule.getmtime(support.TESTFN)
            )
        w_końcu:
            jeżeli nie f.closed:
                f.close()
            support.unlink(support.TESTFN)

    def test_exists(self):
        self.assertIs(self.pathmodule.exists(support.TESTFN), Nieprawda)
        f = open(support.TESTFN, "wb")
        spróbuj:
            f.write(b"foo")
            f.close()
            self.assertIs(self.pathmodule.exists(support.TESTFN), Prawda)
            jeżeli nie self.pathmodule == genericpath:
                self.assertIs(self.pathmodule.lexists(support.TESTFN),
                              Prawda)
        w_końcu:
            jeżeli nie f.close():
                f.close()
            support.unlink(support.TESTFN)

    @unittest.skipUnless(hasattr(os, "pipe"), "requires os.pipe()")
    def test_exists_fd(self):
        r, w = os.pipe()
        spróbuj:
            self.assertPrawda(self.pathmodule.exists(r))
        w_końcu:
            os.close(r)
            os.close(w)
        self.assertNieprawda(self.pathmodule.exists(r))

    def test_isdir(self):
        self.assertIs(self.pathmodule.isdir(support.TESTFN), Nieprawda)
        f = open(support.TESTFN, "wb")
        spróbuj:
            f.write(b"foo")
            f.close()
            self.assertIs(self.pathmodule.isdir(support.TESTFN), Nieprawda)
            os.remove(support.TESTFN)
            os.mkdir(support.TESTFN)
            self.assertIs(self.pathmodule.isdir(support.TESTFN), Prawda)
            os.rmdir(support.TESTFN)
        w_końcu:
            jeżeli nie f.close():
                f.close()
            support.unlink(support.TESTFN)
            safe_rmdir(support.TESTFN)

    def test_isfile(self):
        self.assertIs(self.pathmodule.isfile(support.TESTFN), Nieprawda)
        f = open(support.TESTFN, "wb")
        spróbuj:
            f.write(b"foo")
            f.close()
            self.assertIs(self.pathmodule.isfile(support.TESTFN), Prawda)
            os.remove(support.TESTFN)
            os.mkdir(support.TESTFN)
            self.assertIs(self.pathmodule.isfile(support.TESTFN), Nieprawda)
            os.rmdir(support.TESTFN)
        w_końcu:
            jeżeli nie f.close():
                f.close()
            support.unlink(support.TESTFN)
            safe_rmdir(support.TESTFN)

    @staticmethod
    def _create_file(filename):
        przy open(filename, 'wb') jako f:
            f.write(b'foo')

    def test_samefile(self):
        spróbuj:
            test_fn = support.TESTFN + "1"
            self._create_file(test_fn)
            self.assertPrawda(self.pathmodule.samefile(test_fn, test_fn))
            self.assertRaises(TypeError, self.pathmodule.samefile)
        w_końcu:
            os.remove(test_fn)

    @support.skip_unless_symlink
    def test_samefile_on_symlink(self):
        self._test_samefile_on_link_func(os.symlink)

    def test_samefile_on_link(self):
        self._test_samefile_on_link_func(os.link)

    def _test_samefile_on_link_func(self, func):
        spróbuj:
            test_fn1 = support.TESTFN + "1"
            test_fn2 = support.TESTFN + "2"
            self._create_file(test_fn1)

            func(test_fn1, test_fn2)
            self.assertPrawda(self.pathmodule.samefile(test_fn1, test_fn2))
            os.remove(test_fn2)

            self._create_file(test_fn2)
            self.assertNieprawda(self.pathmodule.samefile(test_fn1, test_fn2))
        w_końcu:
            os.remove(test_fn1)
            os.remove(test_fn2)

    def test_samestat(self):
        spróbuj:
            test_fn = support.TESTFN + "1"
            self._create_file(test_fn)
            test_fns = [test_fn]*2
            stats = map(os.stat, test_fns)
            self.assertPrawda(self.pathmodule.samestat(*stats))
        w_końcu:
            os.remove(test_fn)

    @support.skip_unless_symlink
    def test_samestat_on_symlink(self):
        self._test_samestat_on_link_func(os.symlink)

    def test_samestat_on_link(self):
        self._test_samestat_on_link_func(os.link)

    def _test_samestat_on_link_func(self, func):
        spróbuj:
            test_fn1 = support.TESTFN + "1"
            test_fn2 = support.TESTFN + "2"
            self._create_file(test_fn1)
            test_fns = (test_fn1, test_fn2)
            func(*test_fns)
            stats = map(os.stat, test_fns)
            self.assertPrawda(self.pathmodule.samestat(*stats))
            os.remove(test_fn2)

            self._create_file(test_fn2)
            stats = map(os.stat, test_fns)
            self.assertNieprawda(self.pathmodule.samestat(*stats))

            self.assertRaises(TypeError, self.pathmodule.samestat)
        w_końcu:
            os.remove(test_fn1)
            os.remove(test_fn2)

    def test_sameopenfile(self):
        fname = support.TESTFN + "1"
        przy open(fname, "wb") jako a, open(fname, "wb") jako b:
            self.assertPrawda(self.pathmodule.sameopenfile(
                                a.fileno(), b.fileno()))

klasa TestGenericTest(GenericTest, unittest.TestCase):
    # Issue 16852: GenericTest can't inherit z unittest.TestCase
    # dla test discovery purposes; CommonTest inherits z GenericTest
    # oraz jest only meant to be inherited by others.
    pathmodule = genericpath


# Following TestCase jest nie supposed to be run z test_genericpath.
# It jest inherited by other test modules (macpath, ntpath, posixpath).

klasa CommonTest(GenericTest):
    common_attributes = GenericTest.common_attributes + [
        # Properties
        'curdir', 'pardir', 'extsep', 'sep',
        'pathsep', 'defpath', 'altsep', 'devnull',
        # Methods
        'normcase', 'splitdrive', 'expandvars', 'normpath', 'abspath',
        'join', 'split', 'splitext', 'isabs', 'basename', 'dirname',
        'lexists', 'islink', 'ismount', 'expanduser', 'normpath', 'realpath',
    ]

    def test_normcase(self):
        normcase = self.pathmodule.normcase
        # check that normcase() jest idempotent
        dla p w ["FoO/./BaR", b"FoO/./BaR"]:
            p = normcase(p)
            self.assertEqual(p, normcase(p))

        self.assertEqual(normcase(''), '')
        self.assertEqual(normcase(b''), b'')

        # check that normcase podnieśs a TypeError dla invalid types
        dla path w (Nic, Prawda, 0, 2.5, [], bytearray(b''), {'o','o'}):
            self.assertRaises(TypeError, normcase, path)

    def test_splitdrive(self):
        # splitdrive dla non-NT paths
        splitdrive = self.pathmodule.splitdrive
        self.assertEqual(splitdrive("/foo/bar"), ("", "/foo/bar"))
        self.assertEqual(splitdrive("foo:bar"), ("", "foo:bar"))
        self.assertEqual(splitdrive(":foo:bar"), ("", ":foo:bar"))

        self.assertEqual(splitdrive(b"/foo/bar"), (b"", b"/foo/bar"))
        self.assertEqual(splitdrive(b"foo:bar"), (b"", b"foo:bar"))
        self.assertEqual(splitdrive(b":foo:bar"), (b"", b":foo:bar"))

    def test_expandvars(self):
        jeżeli self.pathmodule.__name__ == 'macpath':
            self.skipTest('macpath.expandvars jest a stub')
        expandvars = self.pathmodule.expandvars
        przy support.EnvironmentVarGuard() jako env:
            env.clear()
            env["foo"] = "bar"
            env["{foo"] = "baz1"
            env["{foo}"] = "baz2"
            self.assertEqual(expandvars("foo"), "foo")
            self.assertEqual(expandvars("$foo bar"), "bar bar")
            self.assertEqual(expandvars("${foo}bar"), "barbar")
            self.assertEqual(expandvars("$[foo]bar"), "$[foo]bar")
            self.assertEqual(expandvars("$bar bar"), "$bar bar")
            self.assertEqual(expandvars("$?bar"), "$?bar")
            self.assertEqual(expandvars("$foo}bar"), "bar}bar")
            self.assertEqual(expandvars("${foo"), "${foo")
            self.assertEqual(expandvars("${{foo}}"), "baz1}")
            self.assertEqual(expandvars("$foo$foo"), "barbar")
            self.assertEqual(expandvars("$bar$bar"), "$bar$bar")

            self.assertEqual(expandvars(b"foo"), b"foo")
            self.assertEqual(expandvars(b"$foo bar"), b"bar bar")
            self.assertEqual(expandvars(b"${foo}bar"), b"barbar")
            self.assertEqual(expandvars(b"$[foo]bar"), b"$[foo]bar")
            self.assertEqual(expandvars(b"$bar bar"), b"$bar bar")
            self.assertEqual(expandvars(b"$?bar"), b"$?bar")
            self.assertEqual(expandvars(b"$foo}bar"), b"bar}bar")
            self.assertEqual(expandvars(b"${foo"), b"${foo")
            self.assertEqual(expandvars(b"${{foo}}"), b"baz1}")
            self.assertEqual(expandvars(b"$foo$foo"), b"barbar")
            self.assertEqual(expandvars(b"$bar$bar"), b"$bar$bar")

    @unittest.skipUnless(support.FS_NONASCII, 'need support.FS_NONASCII')
    def test_expandvars_nonascii(self):
        jeżeli self.pathmodule.__name__ == 'macpath':
            self.skipTest('macpath.expandvars jest a stub')
        expandvars = self.pathmodule.expandvars
        def check(value, expected):
            self.assertEqual(expandvars(value), expected)
        przy support.EnvironmentVarGuard() jako env:
            env.clear()
            nonascii = support.FS_NONASCII
            env['spam'] = nonascii
            env[nonascii] = 'ham' + nonascii
            check(nonascii, nonascii)
            check('$spam bar', '%s bar' % nonascii)
            check('${spam}bar', '%sbar' % nonascii)
            check('${%s}bar' % nonascii, 'ham%sbar' % nonascii)
            check('$bar%s bar' % nonascii, '$bar%s bar' % nonascii)
            check('$spam}bar', '%s}bar' % nonascii)

            check(os.fsencode(nonascii), os.fsencode(nonascii))
            check(b'$spam bar', os.fsencode('%s bar' % nonascii))
            check(b'${spam}bar', os.fsencode('%sbar' % nonascii))
            check(os.fsencode('${%s}bar' % nonascii),
                  os.fsencode('ham%sbar' % nonascii))
            check(os.fsencode('$bar%s bar' % nonascii),
                  os.fsencode('$bar%s bar' % nonascii))
            check(b'$spam}bar', os.fsencode('%s}bar' % nonascii))

    def test_abspath(self):
        self.assertIn("foo", self.pathmodule.abspath("foo"))
        przy warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.assertIn(b"foo", self.pathmodule.abspath(b"foo"))

        # Abspath returns bytes when the arg jest bytes
        przy warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            dla path w (b'', b'foo', b'f\xf2\xf2', b'/foo', b'C:\\'):
                self.assertIsInstance(self.pathmodule.abspath(path), bytes)

    def test_realpath(self):
        self.assertIn("foo", self.pathmodule.realpath("foo"))
        przy warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.assertIn(b"foo", self.pathmodule.realpath(b"foo"))

    def test_normpath_issue5827(self):
        # Make sure normpath preserves unicode
        dla path w ('', '.', '/', '\\', '///foo/.//bar//'):
            self.assertIsInstance(self.pathmodule.normpath(path), str)

    def test_abspath_issue3426(self):
        # Check that abspath returns unicode when the arg jest unicode
        # przy both ASCII oraz non-ASCII cwds.
        abspath = self.pathmodule.abspath
        dla path w ('', 'fuu', 'f\xf9\xf9', '/fuu', 'U:\\'):
            self.assertIsInstance(abspath(path), str)

        unicwd = '\xe7w\xf0'
        spróbuj:
            os.fsencode(unicwd)
        wyjąwszy (AttributeError, UnicodeEncodeError):
            # FS encoding jest probably ASCII
            dalej
        inaczej:
            przy support.temp_cwd(unicwd):
                dla path w ('', 'fuu', 'f\xf9\xf9', '/fuu', 'U:\\'):
                    self.assertIsInstance(abspath(path), str)

    def test_nonascii_abspath(self):
        jeżeli (support.TESTFN_UNDECODABLE
        # Mac OS X denies the creation of a directory przy an invalid
        # UTF-8 name. Windows allows to create a directory przy an
        # arbitrary bytes name, but fails to enter this directory
        # (when the bytes name jest used).
        oraz sys.platform nie w ('win32', 'darwin')):
            name = support.TESTFN_UNDECODABLE
        albo_inaczej support.TESTFN_NONASCII:
            name = support.TESTFN_NONASCII
        inaczej:
            self.skipTest("need support.TESTFN_NONASCII")

        przy warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            przy support.temp_cwd(name):
                self.test_abspath()

    def test_join_errors(self):
        # Check join() podnieśs friendly TypeErrors.
        przy support.check_warnings(('', BytesWarning), quiet=Prawda):
            errmsg = "Can't mix strings oraz bytes w path components"
            przy self.assertRaisesRegex(TypeError, errmsg):
                self.pathmodule.join(b'bytes', 'str')
            przy self.assertRaisesRegex(TypeError, errmsg):
                self.pathmodule.join('str', b'bytes')
            # regression, see #15377
            errmsg = r'join\(\) argument must be str albo bytes, nie %r'
            przy self.assertRaisesRegex(TypeError, errmsg % 'int'):
                self.pathmodule.join(42, 'str')
            przy self.assertRaisesRegex(TypeError, errmsg % 'int'):
                self.pathmodule.join('str', 42)
            przy self.assertRaisesRegex(TypeError, errmsg % 'int'):
                self.pathmodule.join(42)
            przy self.assertRaisesRegex(TypeError, errmsg % 'list'):
                self.pathmodule.join([])
            przy self.assertRaisesRegex(TypeError, errmsg % 'bytearray'):
                self.pathmodule.join(bytearray(b'foo'), bytearray(b'bar'))

    def test_relpath_errors(self):
        # Check relpath() podnieśs friendly TypeErrors.
        przy support.check_warnings(('', (BytesWarning, DeprecationWarning)),
                                    quiet=Prawda):
            errmsg = "Can't mix strings oraz bytes w path components"
            przy self.assertRaisesRegex(TypeError, errmsg):
                self.pathmodule.relpath(b'bytes', 'str')
            przy self.assertRaisesRegex(TypeError, errmsg):
                self.pathmodule.relpath('str', b'bytes')
            errmsg = r'relpath\(\) argument must be str albo bytes, nie %r'
            przy self.assertRaisesRegex(TypeError, errmsg % 'int'):
                self.pathmodule.relpath(42, 'str')
            przy self.assertRaisesRegex(TypeError, errmsg % 'int'):
                self.pathmodule.relpath('str', 42)
            przy self.assertRaisesRegex(TypeError, errmsg % 'bytearray'):
                self.pathmodule.relpath(bytearray(b'foo'), bytearray(b'bar'))


jeżeli __name__=="__main__":
    unittest.main()
