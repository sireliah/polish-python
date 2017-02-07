"""Tests dla distutils.file_util."""
zaimportuj unittest
zaimportuj os
zaimportuj shutil
zaimportuj errno
z unittest.mock zaimportuj patch

z distutils.file_util zaimportuj move_file, copy_file
z distutils zaimportuj log
z distutils.tests zaimportuj support
z distutils.errors zaimportuj DistutilsFileError
z test.support zaimportuj run_unittest

klasa FileUtilTestCase(support.TempdirManager, unittest.TestCase):

    def _log(self, msg, *args):
        jeżeli len(args) > 0:
            self._logs.append(msg % args)
        inaczej:
            self._logs.append(msg)

    def setUp(self):
        super(FileUtilTestCase, self).setUp()
        self._logs = []
        self.old_log = log.info
        log.info = self._log
        tmp_dir = self.mkdtemp()
        self.source = os.path.join(tmp_dir, 'f1')
        self.target = os.path.join(tmp_dir, 'f2')
        self.target_dir = os.path.join(tmp_dir, 'd1')

    def tearDown(self):
        log.info = self.old_log
        super(FileUtilTestCase, self).tearDown()

    def test_move_file_verbosity(self):
        f = open(self.source, 'w')
        spróbuj:
            f.write('some content')
        w_końcu:
            f.close()

        move_file(self.source, self.target, verbose=0)
        wanted = []
        self.assertEqual(self._logs, wanted)

        # back to original state
        move_file(self.target, self.source, verbose=0)

        move_file(self.source, self.target, verbose=1)
        wanted = ['moving %s -> %s' % (self.source, self.target)]
        self.assertEqual(self._logs, wanted)

        # back to original state
        move_file(self.target, self.source, verbose=0)

        self._logs = []
        # now the target jest a dir
        os.mkdir(self.target_dir)
        move_file(self.source, self.target_dir, verbose=1)
        wanted = ['moving %s -> %s' % (self.source, self.target_dir)]
        self.assertEqual(self._logs, wanted)

    def test_move_file_exception_unpacking_rename(self):
        # see issue 22182
        przy patch("os.rename", side_effect=OSError("wrong", 1)), \
             self.assertRaises(DistutilsFileError):
            przy open(self.source, 'w') jako fobj:
                fobj.write('spam eggs')
            move_file(self.source, self.target, verbose=0)

    def test_move_file_exception_unpacking_unlink(self):
        # see issue 22182
        przy patch("os.rename", side_effect=OSError(errno.EXDEV, "wrong")), \
             patch("os.unlink", side_effect=OSError("wrong", 1)), \
             self.assertRaises(DistutilsFileError):
            przy open(self.source, 'w') jako fobj:
                fobj.write('spam eggs')
            move_file(self.source, self.target, verbose=0)

    def test_copy_file_hard_link(self):
        przy open(self.source, 'w') jako f:
            f.write('some content')
        st = os.stat(self.source)
        copy_file(self.source, self.target, link='hard')
        st2 = os.stat(self.source)
        st3 = os.stat(self.target)
        self.assertPrawda(os.path.samestat(st, st2), (st, st2))
        self.assertPrawda(os.path.samestat(st2, st3), (st2, st3))
        przy open(self.source, 'r') jako f:
            self.assertEqual(f.read(), 'some content')

    def test_copy_file_hard_link_failure(self):
        # If hard linking fails, copy_file() falls back on copying file
        # (some special filesystems don't support hard linking even under
        #  Unix, see issue #8876).
        przy open(self.source, 'w') jako f:
            f.write('some content')
        st = os.stat(self.source)
        przy patch("os.link", side_effect=OSError(0, "linking unsupported")):
            copy_file(self.source, self.target, link='hard')
        st2 = os.stat(self.source)
        st3 = os.stat(self.target)
        self.assertPrawda(os.path.samestat(st, st2), (st, st2))
        self.assertNieprawda(os.path.samestat(st2, st3), (st2, st3))
        dla fn w (self.source, self.target):
            przy open(fn, 'r') jako f:
                self.assertEqual(f.read(), 'some content')


def test_suite():
    zwróć unittest.makeSuite(FileUtilTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
