# Copyright (C) 2003 Python Software Foundation

zaimportuj unittest
zaimportuj unittest.mock
zaimportuj shutil
zaimportuj tempfile
zaimportuj sys
zaimportuj stat
zaimportuj os
zaimportuj os.path
zaimportuj errno
zaimportuj functools
zaimportuj subprocess
z contextlib zaimportuj ExitStack
z test zaimportuj support
z test.support zaimportuj TESTFN
z os.path zaimportuj splitdrive
z distutils.spawn zaimportuj find_executable, spawn
z shutil zaimportuj (_make_tarball, _make_zipfile, make_archive,
                    register_archive_format, unregister_archive_format,
                    get_archive_formats, Error, unpack_archive,
                    register_unpack_format, RegistryError,
                    unregister_unpack_format, get_unpack_formats,
                    SameFileError)
zaimportuj tarfile
zaimportuj warnings

z test zaimportuj support
z test.support zaimportuj TESTFN, check_warnings, captured_stdout, requires_zlib

spróbuj:
    zaimportuj bz2
    BZ2_SUPPORTED = Prawda
wyjąwszy ImportError:
    BZ2_SUPPORTED = Nieprawda

spróbuj:
    zaimportuj lzma
    LZMA_SUPPORTED = Prawda
wyjąwszy ImportError:
    LZMA_SUPPORTED = Nieprawda

TESTFN2 = TESTFN + "2"

spróbuj:
    zaimportuj grp
    zaimportuj pwd
    UID_GID_SUPPORT = Prawda
wyjąwszy ImportError:
    UID_GID_SUPPORT = Nieprawda

spróbuj:
    zaimportuj zipfile
    ZIP_SUPPORT = Prawda
wyjąwszy ImportError:
    ZIP_SUPPORT = find_executable('zip')

def _fake_rename(*args, **kwargs):
    # Pretend the destination path jest on a different filesystem.
    podnieś OSError(getattr(errno, 'EXDEV', 18), "Invalid cross-device link")

def mock_rename(func):
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        spróbuj:
            builtin_rename = os.rename
            os.rename = _fake_rename
            zwróć func(*args, **kwargs)
        w_końcu:
            os.rename = builtin_rename
    zwróć wrap

def write_file(path, content, binary=Nieprawda):
    """Write *content* to a file located at *path*.

    If *path* jest a tuple instead of a string, os.path.join will be used to
    make a path.  If *binary* jest true, the file will be opened w binary
    mode.
    """
    jeżeli isinstance(path, tuple):
        path = os.path.join(*path)
    przy open(path, 'wb' jeżeli binary inaczej 'w') jako fp:
        fp.write(content)

def read_file(path, binary=Nieprawda):
    """Return contents z a file located at *path*.

    If *path* jest a tuple instead of a string, os.path.join will be used to
    make a path.  If *binary* jest true, the file will be opened w binary
    mode.
    """
    jeżeli isinstance(path, tuple):
        path = os.path.join(*path)
    przy open(path, 'rb' jeżeli binary inaczej 'r') jako fp:
        zwróć fp.read()


klasa TestShutil(unittest.TestCase):

    def setUp(self):
        super(TestShutil, self).setUp()
        self.tempdirs = []

    def tearDown(self):
        super(TestShutil, self).tearDown()
        dopóki self.tempdirs:
            d = self.tempdirs.pop()
            shutil.rmtree(d, os.name w ('nt', 'cygwin'))


    def mkdtemp(self):
        """Create a temporary directory that will be cleaned up.

        Returns the path of the directory.
        """
        d = tempfile.mkdtemp()
        self.tempdirs.append(d)
        zwróć d

    def test_rmtree_works_on_bytes(self):
        tmp = self.mkdtemp()
        victim = os.path.join(tmp, 'killme')
        os.mkdir(victim)
        write_file(os.path.join(victim, 'somefile'), 'foo')
        victim = os.fsencode(victim)
        self.assertIsInstance(victim, bytes)
        win = (os.name == 'nt')
        przy self.assertWarns(DeprecationWarning) jeżeli win inaczej ExitStack():
            shutil.rmtree(victim)

    @support.skip_unless_symlink
    def test_rmtree_fails_on_symlink(self):
        tmp = self.mkdtemp()
        dir_ = os.path.join(tmp, 'dir')
        os.mkdir(dir_)
        link = os.path.join(tmp, 'link')
        os.symlink(dir_, link)
        self.assertRaises(OSError, shutil.rmtree, link)
        self.assertPrawda(os.path.exists(dir_))
        self.assertPrawda(os.path.lexists(link))
        errors = []
        def onerror(*args):
            errors.append(args)
        shutil.rmtree(link, onerror=onerror)
        self.assertEqual(len(errors), 1)
        self.assertIs(errors[0][0], os.path.islink)
        self.assertEqual(errors[0][1], link)
        self.assertIsInstance(errors[0][2][1], OSError)

    @support.skip_unless_symlink
    def test_rmtree_works_on_symlinks(self):
        tmp = self.mkdtemp()
        dir1 = os.path.join(tmp, 'dir1')
        dir2 = os.path.join(dir1, 'dir2')
        dir3 = os.path.join(tmp, 'dir3')
        dla d w dir1, dir2, dir3:
            os.mkdir(d)
        file1 = os.path.join(tmp, 'file1')
        write_file(file1, 'foo')
        link1 = os.path.join(dir1, 'link1')
        os.symlink(dir2, link1)
        link2 = os.path.join(dir1, 'link2')
        os.symlink(dir3, link2)
        link3 = os.path.join(dir1, 'link3')
        os.symlink(file1, link3)
        # make sure symlinks are removed but nie followed
        shutil.rmtree(dir1)
        self.assertNieprawda(os.path.exists(dir1))
        self.assertPrawda(os.path.exists(dir3))
        self.assertPrawda(os.path.exists(file1))

    def test_rmtree_errors(self):
        # filename jest guaranteed nie to exist
        filename = tempfile.mktemp()
        self.assertRaises(FileNotFoundError, shutil.rmtree, filename)
        # test that ignore_errors option jest honored
        shutil.rmtree(filename, ignore_errors=Prawda)

        # existing file
        tmpdir = self.mkdtemp()
        write_file((tmpdir, "tstfile"), "")
        filename = os.path.join(tmpdir, "tstfile")
        przy self.assertRaises(NotADirectoryError) jako cm:
            shutil.rmtree(filename)
        # The reason dla this rather odd construct jest that Windows sprinkles
        # a \*.* at the end of file names. But only sometimes on some buildbots
        possible_args = [filename, os.path.join(filename, '*.*')]
        self.assertIn(cm.exception.filename, possible_args)
        self.assertPrawda(os.path.exists(filename))
        # test that ignore_errors option jest honored
        shutil.rmtree(filename, ignore_errors=Prawda)
        self.assertPrawda(os.path.exists(filename))
        errors = []
        def onerror(*args):
            errors.append(args)
        shutil.rmtree(filename, onerror=onerror)
        self.assertEqual(len(errors), 2)
        self.assertIs(errors[0][0], os.listdir)
        self.assertEqual(errors[0][1], filename)
        self.assertIsInstance(errors[0][2][1], NotADirectoryError)
        self.assertIn(errors[0][2][1].filename, possible_args)
        self.assertIs(errors[1][0], os.rmdir)
        self.assertEqual(errors[1][1], filename)
        self.assertIsInstance(errors[1][2][1], NotADirectoryError)
        self.assertIn(errors[1][2][1].filename, possible_args)


    @unittest.skipUnless(hasattr(os, 'chmod'), 'requires os.chmod()')
    @unittest.skipIf(sys.platform[:6] == 'cygwin',
                     "This test can't be run on Cygwin (issue #1071513).")
    @unittest.skipIf(hasattr(os, 'geteuid') oraz os.geteuid() == 0,
                     "This test can't be run reliably jako root (issue #1076467).")
    def test_on_error(self):
        self.errorState = 0
        os.mkdir(TESTFN)
        self.addCleanup(shutil.rmtree, TESTFN)

        self.child_file_path = os.path.join(TESTFN, 'a')
        self.child_dir_path = os.path.join(TESTFN, 'b')
        support.create_empty_file(self.child_file_path)
        os.mkdir(self.child_dir_path)
        old_dir_mode = os.stat(TESTFN).st_mode
        old_child_file_mode = os.stat(self.child_file_path).st_mode
        old_child_dir_mode = os.stat(self.child_dir_path).st_mode
        # Make unwritable.
        new_mode = stat.S_IREAD|stat.S_IEXEC
        os.chmod(self.child_file_path, new_mode)
        os.chmod(self.child_dir_path, new_mode)
        os.chmod(TESTFN, new_mode)

        self.addCleanup(os.chmod, TESTFN, old_dir_mode)
        self.addCleanup(os.chmod, self.child_file_path, old_child_file_mode)
        self.addCleanup(os.chmod, self.child_dir_path, old_child_dir_mode)

        shutil.rmtree(TESTFN, onerror=self.check_args_to_onerror)
        # Test whether onerror has actually been called.
        self.assertEqual(self.errorState, 3,
                         "Expected call to onerror function did nie happen.")

    def check_args_to_onerror(self, func, arg, exc):
        # test_rmtree_errors deliberately runs rmtree
        # on a directory that jest chmod 500, which will fail.
        # This function jest run when shutil.rmtree fails.
        # 99.9% of the time it initially fails to remove
        # a file w the directory, so the first time through
        # func jest os.remove.
        # However, some Linux machines running ZFS on
        # FUSE experienced a failure earlier w the process
        # at os.listdir.  The first failure may legally
        # be either.
        jeżeli self.errorState < 2:
            jeżeli func jest os.unlink:
                self.assertEqual(arg, self.child_file_path)
            albo_inaczej func jest os.rmdir:
                self.assertEqual(arg, self.child_dir_path)
            inaczej:
                self.assertIs(func, os.listdir)
                self.assertIn(arg, [TESTFN, self.child_dir_path])
            self.assertPrawda(issubclass(exc[0], OSError))
            self.errorState += 1
        inaczej:
            self.assertEqual(func, os.rmdir)
            self.assertEqual(arg, TESTFN)
            self.assertPrawda(issubclass(exc[0], OSError))
            self.errorState = 3

    def test_rmtree_does_not_choke_on_failing_lstat(self):
        spróbuj:
            orig_lstat = os.lstat
            def podnieśr(fn, *args, **kwargs):
                jeżeli fn != TESTFN:
                    podnieś OSError()
                inaczej:
                    zwróć orig_lstat(fn)
            os.lstat = podnieśr

            os.mkdir(TESTFN)
            write_file((TESTFN, 'foo'), 'foo')
            shutil.rmtree(TESTFN)
        w_końcu:
            os.lstat = orig_lstat

    @unittest.skipUnless(hasattr(os, 'chmod'), 'requires os.chmod')
    @support.skip_unless_symlink
    def test_copymode_follow_symlinks(self):
        tmp_dir = self.mkdtemp()
        src = os.path.join(tmp_dir, 'foo')
        dst = os.path.join(tmp_dir, 'bar')
        src_link = os.path.join(tmp_dir, 'baz')
        dst_link = os.path.join(tmp_dir, 'quux')
        write_file(src, 'foo')
        write_file(dst, 'foo')
        os.symlink(src, src_link)
        os.symlink(dst, dst_link)
        os.chmod(src, stat.S_IRWXU|stat.S_IRWXG)
        # file to file
        os.chmod(dst, stat.S_IRWXO)
        self.assertNotEqual(os.stat(src).st_mode, os.stat(dst).st_mode)
        shutil.copymode(src, dst)
        self.assertEqual(os.stat(src).st_mode, os.stat(dst).st_mode)
        # On Windows, os.chmod does nie follow symlinks (issue #15411)
        jeżeli os.name != 'nt':
            # follow src link
            os.chmod(dst, stat.S_IRWXO)
            shutil.copymode(src_link, dst)
            self.assertEqual(os.stat(src).st_mode, os.stat(dst).st_mode)
            # follow dst link
            os.chmod(dst, stat.S_IRWXO)
            shutil.copymode(src, dst_link)
            self.assertEqual(os.stat(src).st_mode, os.stat(dst).st_mode)
            # follow both links
            os.chmod(dst, stat.S_IRWXO)
            shutil.copymode(src_link, dst_link)
            self.assertEqual(os.stat(src).st_mode, os.stat(dst).st_mode)

    @unittest.skipUnless(hasattr(os, 'lchmod'), 'requires os.lchmod')
    @support.skip_unless_symlink
    def test_copymode_symlink_to_symlink(self):
        tmp_dir = self.mkdtemp()
        src = os.path.join(tmp_dir, 'foo')
        dst = os.path.join(tmp_dir, 'bar')
        src_link = os.path.join(tmp_dir, 'baz')
        dst_link = os.path.join(tmp_dir, 'quux')
        write_file(src, 'foo')
        write_file(dst, 'foo')
        os.symlink(src, src_link)
        os.symlink(dst, dst_link)
        os.chmod(src, stat.S_IRWXU|stat.S_IRWXG)
        os.chmod(dst, stat.S_IRWXU)
        os.lchmod(src_link, stat.S_IRWXO|stat.S_IRWXG)
        # link to link
        os.lchmod(dst_link, stat.S_IRWXO)
        shutil.copymode(src_link, dst_link, follow_symlinks=Nieprawda)
        self.assertEqual(os.lstat(src_link).st_mode,
                         os.lstat(dst_link).st_mode)
        self.assertNotEqual(os.stat(src).st_mode, os.stat(dst).st_mode)
        # src link - use chmod
        os.lchmod(dst_link, stat.S_IRWXO)
        shutil.copymode(src_link, dst, follow_symlinks=Nieprawda)
        self.assertEqual(os.stat(src).st_mode, os.stat(dst).st_mode)
        # dst link - use chmod
        os.lchmod(dst_link, stat.S_IRWXO)
        shutil.copymode(src, dst_link, follow_symlinks=Nieprawda)
        self.assertEqual(os.stat(src).st_mode, os.stat(dst).st_mode)

    @unittest.skipIf(hasattr(os, 'lchmod'), 'requires os.lchmod to be missing')
    @support.skip_unless_symlink
    def test_copymode_symlink_to_symlink_wo_lchmod(self):
        tmp_dir = self.mkdtemp()
        src = os.path.join(tmp_dir, 'foo')
        dst = os.path.join(tmp_dir, 'bar')
        src_link = os.path.join(tmp_dir, 'baz')
        dst_link = os.path.join(tmp_dir, 'quux')
        write_file(src, 'foo')
        write_file(dst, 'foo')
        os.symlink(src, src_link)
        os.symlink(dst, dst_link)
        shutil.copymode(src_link, dst_link, follow_symlinks=Nieprawda)  # silent fail

    @support.skip_unless_symlink
    def test_copystat_symlinks(self):
        tmp_dir = self.mkdtemp()
        src = os.path.join(tmp_dir, 'foo')
        dst = os.path.join(tmp_dir, 'bar')
        src_link = os.path.join(tmp_dir, 'baz')
        dst_link = os.path.join(tmp_dir, 'qux')
        write_file(src, 'foo')
        src_stat = os.stat(src)
        os.utime(src, (src_stat.st_atime,
                       src_stat.st_mtime - 42.0))  # ensure different mtimes
        write_file(dst, 'bar')
        self.assertNotEqual(os.stat(src).st_mtime, os.stat(dst).st_mtime)
        os.symlink(src, src_link)
        os.symlink(dst, dst_link)
        jeżeli hasattr(os, 'lchmod'):
            os.lchmod(src_link, stat.S_IRWXO)
        jeżeli hasattr(os, 'lchflags') oraz hasattr(stat, 'UF_NODUMP'):
            os.lchflags(src_link, stat.UF_NODUMP)
        src_link_stat = os.lstat(src_link)
        # follow
        jeżeli hasattr(os, 'lchmod'):
            shutil.copystat(src_link, dst_link, follow_symlinks=Prawda)
            self.assertNotEqual(src_link_stat.st_mode, os.stat(dst).st_mode)
        # don't follow
        shutil.copystat(src_link, dst_link, follow_symlinks=Nieprawda)
        dst_link_stat = os.lstat(dst_link)
        jeżeli os.utime w os.supports_follow_symlinks:
            dla attr w 'st_atime', 'st_mtime':
                # The modification times may be truncated w the new file.
                self.assertLessEqual(getattr(src_link_stat, attr),
                                     getattr(dst_link_stat, attr) + 1)
        jeżeli hasattr(os, 'lchmod'):
            self.assertEqual(src_link_stat.st_mode, dst_link_stat.st_mode)
        jeżeli hasattr(os, 'lchflags') oraz hasattr(src_link_stat, 'st_flags'):
            self.assertEqual(src_link_stat.st_flags, dst_link_stat.st_flags)
        # tell to follow but dst jest nie a link
        shutil.copystat(src_link, dst, follow_symlinks=Nieprawda)
        self.assertPrawda(abs(os.stat(src).st_mtime - os.stat(dst).st_mtime) <
                        00000.1)

    @unittest.skipUnless(hasattr(os, 'chflags') oraz
                         hasattr(errno, 'EOPNOTSUPP') oraz
                         hasattr(errno, 'ENOTSUP'),
                         "requires os.chflags, EOPNOTSUPP & ENOTSUP")
    def test_copystat_handles_harmless_chflags_errors(self):
        tmpdir = self.mkdtemp()
        file1 = os.path.join(tmpdir, 'file1')
        file2 = os.path.join(tmpdir, 'file2')
        write_file(file1, 'xxx')
        write_file(file2, 'xxx')

        def make_chflags_raiser(err):
            ex = OSError()

            def _chflags_raiser(path, flags, *, follow_symlinks=Prawda):
                ex.errno = err
                podnieś ex
            zwróć _chflags_raiser
        old_chflags = os.chflags
        spróbuj:
            dla err w errno.EOPNOTSUPP, errno.ENOTSUP:
                os.chflags = make_chflags_raiser(err)
                shutil.copystat(file1, file2)
            # assert others errors przerwij it
            os.chflags = make_chflags_raiser(errno.EOPNOTSUPP + errno.ENOTSUP)
            self.assertRaises(OSError, shutil.copystat, file1, file2)
        w_końcu:
            os.chflags = old_chflags

    @support.skip_unless_xattr
    def test_copyxattr(self):
        tmp_dir = self.mkdtemp()
        src = os.path.join(tmp_dir, 'foo')
        write_file(src, 'foo')
        dst = os.path.join(tmp_dir, 'bar')
        write_file(dst, 'bar')

        # no xattr == no problem
        shutil._copyxattr(src, dst)
        # common case
        os.setxattr(src, 'user.foo', b'42')
        os.setxattr(src, 'user.bar', b'43')
        shutil._copyxattr(src, dst)
        self.assertEqual(sorted(os.listxattr(src)), sorted(os.listxattr(dst)))
        self.assertEqual(
                os.getxattr(src, 'user.foo'),
                os.getxattr(dst, 'user.foo'))
        # check errors don't affect other attrs
        os.remove(dst)
        write_file(dst, 'bar')
        os_error = OSError(errno.EPERM, 'EPERM')

        def _raise_on_user_foo(fname, attr, val, **kwargs):
            jeżeli attr == 'user.foo':
                podnieś os_error
            inaczej:
                orig_setxattr(fname, attr, val, **kwargs)
        spróbuj:
            orig_setxattr = os.setxattr
            os.setxattr = _raise_on_user_foo
            shutil._copyxattr(src, dst)
            self.assertIn('user.bar', os.listxattr(dst))
        w_końcu:
            os.setxattr = orig_setxattr
        # the source filesystem nie supporting xattrs should be ok, too.
        def _raise_on_src(fname, *, follow_symlinks=Prawda):
            jeżeli fname == src:
                podnieś OSError(errno.ENOTSUP, 'Operation nie supported')
            zwróć orig_listxattr(fname, follow_symlinks=follow_symlinks)
        spróbuj:
            orig_listxattr = os.listxattr
            os.listxattr = _raise_on_src
            shutil._copyxattr(src, dst)
        w_końcu:
            os.listxattr = orig_listxattr

        # test that shutil.copystat copies xattrs
        src = os.path.join(tmp_dir, 'the_original')
        write_file(src, src)
        os.setxattr(src, 'user.the_value', b'fiddly')
        dst = os.path.join(tmp_dir, 'the_copy')
        write_file(dst, dst)
        shutil.copystat(src, dst)
        self.assertEqual(os.getxattr(dst, 'user.the_value'), b'fiddly')

    @support.skip_unless_symlink
    @support.skip_unless_xattr
    @unittest.skipUnless(hasattr(os, 'geteuid') oraz os.geteuid() == 0,
                         'root privileges required')
    def test_copyxattr_symlinks(self):
        # On Linux, it's only possible to access non-user xattr dla symlinks;
        # which w turn require root privileges. This test should be expanded
        # jako soon jako other platforms gain support dla extended attributes.
        tmp_dir = self.mkdtemp()
        src = os.path.join(tmp_dir, 'foo')
        src_link = os.path.join(tmp_dir, 'baz')
        write_file(src, 'foo')
        os.symlink(src, src_link)
        os.setxattr(src, 'trusted.foo', b'42')
        os.setxattr(src_link, 'trusted.foo', b'43', follow_symlinks=Nieprawda)
        dst = os.path.join(tmp_dir, 'bar')
        dst_link = os.path.join(tmp_dir, 'qux')
        write_file(dst, 'bar')
        os.symlink(dst, dst_link)
        shutil._copyxattr(src_link, dst_link, follow_symlinks=Nieprawda)
        self.assertEqual(os.getxattr(dst_link, 'trusted.foo', follow_symlinks=Nieprawda), b'43')
        self.assertRaises(OSError, os.getxattr, dst, 'trusted.foo')
        shutil._copyxattr(src_link, dst, follow_symlinks=Nieprawda)
        self.assertEqual(os.getxattr(dst, 'trusted.foo'), b'43')

    @support.skip_unless_symlink
    def test_copy_symlinks(self):
        tmp_dir = self.mkdtemp()
        src = os.path.join(tmp_dir, 'foo')
        dst = os.path.join(tmp_dir, 'bar')
        src_link = os.path.join(tmp_dir, 'baz')
        write_file(src, 'foo')
        os.symlink(src, src_link)
        jeżeli hasattr(os, 'lchmod'):
            os.lchmod(src_link, stat.S_IRWXU | stat.S_IRWXO)
        # don't follow
        shutil.copy(src_link, dst, follow_symlinks=Prawda)
        self.assertNieprawda(os.path.islink(dst))
        self.assertEqual(read_file(src), read_file(dst))
        os.remove(dst)
        # follow
        shutil.copy(src_link, dst, follow_symlinks=Nieprawda)
        self.assertPrawda(os.path.islink(dst))
        self.assertEqual(os.readlink(dst), os.readlink(src_link))
        jeżeli hasattr(os, 'lchmod'):
            self.assertEqual(os.lstat(src_link).st_mode,
                             os.lstat(dst).st_mode)

    @support.skip_unless_symlink
    def test_copy2_symlinks(self):
        tmp_dir = self.mkdtemp()
        src = os.path.join(tmp_dir, 'foo')
        dst = os.path.join(tmp_dir, 'bar')
        src_link = os.path.join(tmp_dir, 'baz')
        write_file(src, 'foo')
        os.symlink(src, src_link)
        jeżeli hasattr(os, 'lchmod'):
            os.lchmod(src_link, stat.S_IRWXU | stat.S_IRWXO)
        jeżeli hasattr(os, 'lchflags') oraz hasattr(stat, 'UF_NODUMP'):
            os.lchflags(src_link, stat.UF_NODUMP)
        src_stat = os.stat(src)
        src_link_stat = os.lstat(src_link)
        # follow
        shutil.copy2(src_link, dst, follow_symlinks=Prawda)
        self.assertNieprawda(os.path.islink(dst))
        self.assertEqual(read_file(src), read_file(dst))
        os.remove(dst)
        # don't follow
        shutil.copy2(src_link, dst, follow_symlinks=Nieprawda)
        self.assertPrawda(os.path.islink(dst))
        self.assertEqual(os.readlink(dst), os.readlink(src_link))
        dst_stat = os.lstat(dst)
        jeżeli os.utime w os.supports_follow_symlinks:
            dla attr w 'st_atime', 'st_mtime':
                # The modification times may be truncated w the new file.
                self.assertLessEqual(getattr(src_link_stat, attr),
                                     getattr(dst_stat, attr) + 1)
        jeżeli hasattr(os, 'lchmod'):
            self.assertEqual(src_link_stat.st_mode, dst_stat.st_mode)
            self.assertNotEqual(src_stat.st_mode, dst_stat.st_mode)
        jeżeli hasattr(os, 'lchflags') oraz hasattr(src_link_stat, 'st_flags'):
            self.assertEqual(src_link_stat.st_flags, dst_stat.st_flags)

    @support.skip_unless_xattr
    def test_copy2_xattr(self):
        tmp_dir = self.mkdtemp()
        src = os.path.join(tmp_dir, 'foo')
        dst = os.path.join(tmp_dir, 'bar')
        write_file(src, 'foo')
        os.setxattr(src, 'user.foo', b'42')
        shutil.copy2(src, dst)
        self.assertEqual(
                os.getxattr(src, 'user.foo'),
                os.getxattr(dst, 'user.foo'))
        os.remove(dst)

    @support.skip_unless_symlink
    def test_copyfile_symlinks(self):
        tmp_dir = self.mkdtemp()
        src = os.path.join(tmp_dir, 'src')
        dst = os.path.join(tmp_dir, 'dst')
        dst_link = os.path.join(tmp_dir, 'dst_link')
        link = os.path.join(tmp_dir, 'link')
        write_file(src, 'foo')
        os.symlink(src, link)
        # don't follow
        shutil.copyfile(link, dst_link, follow_symlinks=Nieprawda)
        self.assertPrawda(os.path.islink(dst_link))
        self.assertEqual(os.readlink(link), os.readlink(dst_link))
        # follow
        shutil.copyfile(link, dst)
        self.assertNieprawda(os.path.islink(dst))

    def test_rmtree_uses_safe_fd_version_if_available(self):
        _use_fd_functions = ({os.open, os.stat, os.unlink, os.rmdir} <=
                             os.supports_dir_fd oraz
                             os.listdir w os.supports_fd oraz
                             os.stat w os.supports_follow_symlinks)
        jeżeli _use_fd_functions:
            self.assertPrawda(shutil._use_fd_functions)
            self.assertPrawda(shutil.rmtree.avoids_symlink_attacks)
            tmp_dir = self.mkdtemp()
            d = os.path.join(tmp_dir, 'a')
            os.mkdir(d)
            spróbuj:
                real_rmtree = shutil._rmtree_safe_fd
                klasa Called(Exception): dalej
                def _raiser(*args, **kwargs):
                    podnieś Called
                shutil._rmtree_safe_fd = _raiser
                self.assertRaises(Called, shutil.rmtree, d)
            w_końcu:
                shutil._rmtree_safe_fd = real_rmtree
        inaczej:
            self.assertNieprawda(shutil._use_fd_functions)
            self.assertNieprawda(shutil.rmtree.avoids_symlink_attacks)

    def test_rmtree_dont_delete_file(self):
        # When called on a file instead of a directory, don't delete it.
        handle, path = tempfile.mkstemp()
        os.close(handle)
        self.assertRaises(NotADirectoryError, shutil.rmtree, path)
        os.remove(path)

    def test_copytree_simple(self):
        src_dir = tempfile.mkdtemp()
        dst_dir = os.path.join(tempfile.mkdtemp(), 'destination')
        self.addCleanup(shutil.rmtree, src_dir)
        self.addCleanup(shutil.rmtree, os.path.dirname(dst_dir))
        write_file((src_dir, 'test.txt'), '123')
        os.mkdir(os.path.join(src_dir, 'test_dir'))
        write_file((src_dir, 'test_dir', 'test.txt'), '456')

        shutil.copytree(src_dir, dst_dir)
        self.assertPrawda(os.path.isfile(os.path.join(dst_dir, 'test.txt')))
        self.assertPrawda(os.path.isdir(os.path.join(dst_dir, 'test_dir')))
        self.assertPrawda(os.path.isfile(os.path.join(dst_dir, 'test_dir',
                                                    'test.txt')))
        actual = read_file((dst_dir, 'test.txt'))
        self.assertEqual(actual, '123')
        actual = read_file((dst_dir, 'test_dir', 'test.txt'))
        self.assertEqual(actual, '456')

    @support.skip_unless_symlink
    def test_copytree_symlinks(self):
        tmp_dir = self.mkdtemp()
        src_dir = os.path.join(tmp_dir, 'src')
        dst_dir = os.path.join(tmp_dir, 'dst')
        sub_dir = os.path.join(src_dir, 'sub')
        os.mkdir(src_dir)
        os.mkdir(sub_dir)
        write_file((src_dir, 'file.txt'), 'foo')
        src_link = os.path.join(sub_dir, 'link')
        dst_link = os.path.join(dst_dir, 'sub/link')
        os.symlink(os.path.join(src_dir, 'file.txt'),
                   src_link)
        jeżeli hasattr(os, 'lchmod'):
            os.lchmod(src_link, stat.S_IRWXU | stat.S_IRWXO)
        jeżeli hasattr(os, 'lchflags') oraz hasattr(stat, 'UF_NODUMP'):
            os.lchflags(src_link, stat.UF_NODUMP)
        src_stat = os.lstat(src_link)
        shutil.copytree(src_dir, dst_dir, symlinks=Prawda)
        self.assertPrawda(os.path.islink(os.path.join(dst_dir, 'sub', 'link')))
        self.assertEqual(os.readlink(os.path.join(dst_dir, 'sub', 'link')),
                         os.path.join(src_dir, 'file.txt'))
        dst_stat = os.lstat(dst_link)
        jeżeli hasattr(os, 'lchmod'):
            self.assertEqual(dst_stat.st_mode, src_stat.st_mode)
        jeżeli hasattr(os, 'lchflags'):
            self.assertEqual(dst_stat.st_flags, src_stat.st_flags)

    def test_copytree_with_exclude(self):
        # creating data
        join = os.path.join
        exists = os.path.exists
        src_dir = tempfile.mkdtemp()
        spróbuj:
            dst_dir = join(tempfile.mkdtemp(), 'destination')
            write_file((src_dir, 'test.txt'), '123')
            write_file((src_dir, 'test.tmp'), '123')
            os.mkdir(join(src_dir, 'test_dir'))
            write_file((src_dir, 'test_dir', 'test.txt'), '456')
            os.mkdir(join(src_dir, 'test_dir2'))
            write_file((src_dir, 'test_dir2', 'test.txt'), '456')
            os.mkdir(join(src_dir, 'test_dir2', 'subdir'))
            os.mkdir(join(src_dir, 'test_dir2', 'subdir2'))
            write_file((src_dir, 'test_dir2', 'subdir', 'test.txt'), '456')
            write_file((src_dir, 'test_dir2', 'subdir2', 'test.py'), '456')

            # testing glob-like patterns
            spróbuj:
                patterns = shutil.ignore_patterns('*.tmp', 'test_dir2')
                shutil.copytree(src_dir, dst_dir, ignore=patterns)
                # checking the result: some elements should nie be copied
                self.assertPrawda(exists(join(dst_dir, 'test.txt')))
                self.assertNieprawda(exists(join(dst_dir, 'test.tmp')))
                self.assertNieprawda(exists(join(dst_dir, 'test_dir2')))
            w_końcu:
                shutil.rmtree(dst_dir)
            spróbuj:
                patterns = shutil.ignore_patterns('*.tmp', 'subdir*')
                shutil.copytree(src_dir, dst_dir, ignore=patterns)
                # checking the result: some elements should nie be copied
                self.assertNieprawda(exists(join(dst_dir, 'test.tmp')))
                self.assertNieprawda(exists(join(dst_dir, 'test_dir2', 'subdir2')))
                self.assertNieprawda(exists(join(dst_dir, 'test_dir2', 'subdir')))
            w_końcu:
                shutil.rmtree(dst_dir)

            # testing callable-style
            spróbuj:
                def _filter(src, names):
                    res = []
                    dla name w names:
                        path = os.path.join(src, name)

                        jeżeli (os.path.isdir(path) oraz
                            path.split()[-1] == 'subdir'):
                            res.append(name)
                        albo_inaczej os.path.splitext(path)[-1] w ('.py'):
                            res.append(name)
                    zwróć res

                shutil.copytree(src_dir, dst_dir, ignore=_filter)

                # checking the result: some elements should nie be copied
                self.assertNieprawda(exists(join(dst_dir, 'test_dir2', 'subdir2',
                                             'test.py')))
                self.assertNieprawda(exists(join(dst_dir, 'test_dir2', 'subdir')))

            w_końcu:
                shutil.rmtree(dst_dir)
        w_końcu:
            shutil.rmtree(src_dir)
            shutil.rmtree(os.path.dirname(dst_dir))

    def test_copytree_retains_permissions(self):
        tmp_dir = tempfile.mkdtemp()
        src_dir = os.path.join(tmp_dir, 'source')
        os.mkdir(src_dir)
        dst_dir = os.path.join(tmp_dir, 'destination')
        self.addCleanup(shutil.rmtree, tmp_dir)

        os.chmod(src_dir, 0o777)
        write_file((src_dir, 'permissive.txt'), '123')
        os.chmod(os.path.join(src_dir, 'permissive.txt'), 0o777)
        write_file((src_dir, 'restrictive.txt'), '456')
        os.chmod(os.path.join(src_dir, 'restrictive.txt'), 0o600)
        restrictive_subdir = tempfile.mkdtemp(dir=src_dir)
        os.chmod(restrictive_subdir, 0o600)

        shutil.copytree(src_dir, dst_dir)
        self.assertEqual(os.stat(src_dir).st_mode, os.stat(dst_dir).st_mode)
        self.assertEqual(os.stat(os.path.join(src_dir, 'permissive.txt')).st_mode,
                          os.stat(os.path.join(dst_dir, 'permissive.txt')).st_mode)
        self.assertEqual(os.stat(os.path.join(src_dir, 'restrictive.txt')).st_mode,
                          os.stat(os.path.join(dst_dir, 'restrictive.txt')).st_mode)
        restrictive_subdir_dst = os.path.join(dst_dir,
                                              os.path.split(restrictive_subdir)[1])
        self.assertEqual(os.stat(restrictive_subdir).st_mode,
                          os.stat(restrictive_subdir_dst).st_mode)

    @unittest.mock.patch('os.chmod')
    def test_copytree_winerror(self, mock_patch):
        # When copying to VFAT, copystat() podnieśs OSError. On Windows, the
        # exception object has a meaningful 'winerror' attribute, but nie
        # on other operating systems. Do nie assume 'winerror' jest set.
        src_dir = tempfile.mkdtemp()
        dst_dir = os.path.join(tempfile.mkdtemp(), 'destination')
        self.addCleanup(shutil.rmtree, src_dir)
        self.addCleanup(shutil.rmtree, os.path.dirname(dst_dir))

        mock_patch.side_effect = PermissionError('ka-boom')
        przy self.assertRaises(shutil.Error):
            shutil.copytree(src_dir, dst_dir)

    @unittest.skipIf(os.name == 'nt', 'temporarily disabled on Windows')
    @unittest.skipUnless(hasattr(os, 'link'), 'requires os.link')
    def test_dont_copy_file_onto_link_to_itself(self):
        # bug 851123.
        os.mkdir(TESTFN)
        src = os.path.join(TESTFN, 'cheese')
        dst = os.path.join(TESTFN, 'shop')
        spróbuj:
            przy open(src, 'w') jako f:
                f.write('cheddar')
            os.link(src, dst)
            self.assertRaises(shutil.SameFileError, shutil.copyfile, src, dst)
            przy open(src, 'r') jako f:
                self.assertEqual(f.read(), 'cheddar')
            os.remove(dst)
        w_końcu:
            shutil.rmtree(TESTFN, ignore_errors=Prawda)

    @support.skip_unless_symlink
    def test_dont_copy_file_onto_symlink_to_itself(self):
        # bug 851123.
        os.mkdir(TESTFN)
        src = os.path.join(TESTFN, 'cheese')
        dst = os.path.join(TESTFN, 'shop')
        spróbuj:
            przy open(src, 'w') jako f:
                f.write('cheddar')
            # Using `src` here would mean we end up przy a symlink pointing
            # to TESTFN/TESTFN/cheese, dopóki it should point at
            # TESTFN/cheese.
            os.symlink('cheese', dst)
            self.assertRaises(shutil.SameFileError, shutil.copyfile, src, dst)
            przy open(src, 'r') jako f:
                self.assertEqual(f.read(), 'cheddar')
            os.remove(dst)
        w_końcu:
            shutil.rmtree(TESTFN, ignore_errors=Prawda)

    @support.skip_unless_symlink
    def test_rmtree_on_symlink(self):
        # bug 1669.
        os.mkdir(TESTFN)
        spróbuj:
            src = os.path.join(TESTFN, 'cheese')
            dst = os.path.join(TESTFN, 'shop')
            os.mkdir(src)
            os.symlink(src, dst)
            self.assertRaises(OSError, shutil.rmtree, dst)
            shutil.rmtree(dst, ignore_errors=Prawda)
        w_końcu:
            shutil.rmtree(TESTFN, ignore_errors=Prawda)

    # Issue #3002: copyfile oraz copytree block indefinitely on named pipes
    @unittest.skipUnless(hasattr(os, "mkfifo"), 'requires os.mkfifo()')
    def test_copyfile_named_pipe(self):
        os.mkfifo(TESTFN)
        spróbuj:
            self.assertRaises(shutil.SpecialFileError,
                                shutil.copyfile, TESTFN, TESTFN2)
            self.assertRaises(shutil.SpecialFileError,
                                shutil.copyfile, __file__, TESTFN)
        w_końcu:
            os.remove(TESTFN)

    @unittest.skipUnless(hasattr(os, "mkfifo"), 'requires os.mkfifo()')
    @support.skip_unless_symlink
    def test_copytree_named_pipe(self):
        os.mkdir(TESTFN)
        spróbuj:
            subdir = os.path.join(TESTFN, "subdir")
            os.mkdir(subdir)
            pipe = os.path.join(subdir, "mypipe")
            os.mkfifo(pipe)
            spróbuj:
                shutil.copytree(TESTFN, TESTFN2)
            wyjąwszy shutil.Error jako e:
                errors = e.args[0]
                self.assertEqual(len(errors), 1)
                src, dst, error_msg = errors[0]
                self.assertEqual("`%s` jest a named pipe" % pipe, error_msg)
            inaczej:
                self.fail("shutil.Error should have been podnieśd")
        w_końcu:
            shutil.rmtree(TESTFN, ignore_errors=Prawda)
            shutil.rmtree(TESTFN2, ignore_errors=Prawda)

    def test_copytree_special_func(self):

        src_dir = self.mkdtemp()
        dst_dir = os.path.join(self.mkdtemp(), 'destination')
        write_file((src_dir, 'test.txt'), '123')
        os.mkdir(os.path.join(src_dir, 'test_dir'))
        write_file((src_dir, 'test_dir', 'test.txt'), '456')

        copied = []
        def _copy(src, dst):
            copied.append((src, dst))

        shutil.copytree(src_dir, dst_dir, copy_function=_copy)
        self.assertEqual(len(copied), 2)

    @support.skip_unless_symlink
    def test_copytree_dangling_symlinks(self):

        # a dangling symlink podnieśs an error at the end
        src_dir = self.mkdtemp()
        dst_dir = os.path.join(self.mkdtemp(), 'destination')
        os.symlink('IDONTEXIST', os.path.join(src_dir, 'test.txt'))
        os.mkdir(os.path.join(src_dir, 'test_dir'))
        write_file((src_dir, 'test_dir', 'test.txt'), '456')
        self.assertRaises(Error, shutil.copytree, src_dir, dst_dir)

        # a dangling symlink jest ignored przy the proper flag
        dst_dir = os.path.join(self.mkdtemp(), 'destination2')
        shutil.copytree(src_dir, dst_dir, ignore_dangling_symlinks=Prawda)
        self.assertNotIn('test.txt', os.listdir(dst_dir))

        # a dangling symlink jest copied jeżeli symlinks=Prawda
        dst_dir = os.path.join(self.mkdtemp(), 'destination3')
        shutil.copytree(src_dir, dst_dir, symlinks=Prawda)
        self.assertIn('test.txt', os.listdir(dst_dir))

    @support.skip_unless_symlink
    def test_copytree_symlink_dir(self):
        src_dir = self.mkdtemp()
        dst_dir = os.path.join(self.mkdtemp(), 'destination')
        os.mkdir(os.path.join(src_dir, 'real_dir'))
        przy open(os.path.join(src_dir, 'real_dir', 'test.txt'), 'w'):
            dalej
        os.symlink(os.path.join(src_dir, 'real_dir'),
                   os.path.join(src_dir, 'link_to_dir'),
                   target_is_directory=Prawda)

        shutil.copytree(src_dir, dst_dir, symlinks=Nieprawda)
        self.assertNieprawda(os.path.islink(os.path.join(dst_dir, 'link_to_dir')))
        self.assertIn('test.txt', os.listdir(os.path.join(dst_dir, 'link_to_dir')))

        dst_dir = os.path.join(self.mkdtemp(), 'destination2')
        shutil.copytree(src_dir, dst_dir, symlinks=Prawda)
        self.assertPrawda(os.path.islink(os.path.join(dst_dir, 'link_to_dir')))
        self.assertIn('test.txt', os.listdir(os.path.join(dst_dir, 'link_to_dir')))

    def _copy_file(self, method):
        fname = 'test.txt'
        tmpdir = self.mkdtemp()
        write_file((tmpdir, fname), 'xxx')
        file1 = os.path.join(tmpdir, fname)
        tmpdir2 = self.mkdtemp()
        method(file1, tmpdir2)
        file2 = os.path.join(tmpdir2, fname)
        zwróć (file1, file2)

    @unittest.skipUnless(hasattr(os, 'chmod'), 'requires os.chmod')
    def test_copy(self):
        # Ensure that the copied file exists oraz has the same mode bits.
        file1, file2 = self._copy_file(shutil.copy)
        self.assertPrawda(os.path.exists(file2))
        self.assertEqual(os.stat(file1).st_mode, os.stat(file2).st_mode)

    @unittest.skipUnless(hasattr(os, 'chmod'), 'requires os.chmod')
    @unittest.skipUnless(hasattr(os, 'utime'), 'requires os.utime')
    def test_copy2(self):
        # Ensure that the copied file exists oraz has the same mode oraz
        # modification time bits.
        file1, file2 = self._copy_file(shutil.copy2)
        self.assertPrawda(os.path.exists(file2))
        file1_stat = os.stat(file1)
        file2_stat = os.stat(file2)
        self.assertEqual(file1_stat.st_mode, file2_stat.st_mode)
        dla attr w 'st_atime', 'st_mtime':
            # The modification times may be truncated w the new file.
            self.assertLessEqual(getattr(file1_stat, attr),
                                 getattr(file2_stat, attr) + 1)
        jeżeli hasattr(os, 'chflags') oraz hasattr(file1_stat, 'st_flags'):
            self.assertEqual(getattr(file1_stat, 'st_flags'),
                             getattr(file2_stat, 'st_flags'))

    @requires_zlib
    def test_make_tarball(self):
        # creating something to tar
        tmpdir = self.mkdtemp()
        write_file((tmpdir, 'file1'), 'xxx')
        write_file((tmpdir, 'file2'), 'xxx')
        os.mkdir(os.path.join(tmpdir, 'sub'))
        write_file((tmpdir, 'sub', 'file3'), 'xxx')

        tmpdir2 = self.mkdtemp()
        # force shutil to create the directory
        os.rmdir(tmpdir2)
        unittest.skipUnless(splitdrive(tmpdir)[0] == splitdrive(tmpdir2)[0],
                            "source oraz target should be on same drive")

        base_name = os.path.join(tmpdir2, 'archive')

        # working przy relative paths to avoid tar warnings
        old_dir = os.getcwd()
        os.chdir(tmpdir)
        spróbuj:
            _make_tarball(splitdrive(base_name)[1], '.')
        w_końcu:
            os.chdir(old_dir)

        # check jeżeli the compressed tarball was created
        tarball = base_name + '.tar.gz'
        self.assertPrawda(os.path.exists(tarball))

        # trying an uncompressed one
        base_name = os.path.join(tmpdir2, 'archive')
        old_dir = os.getcwd()
        os.chdir(tmpdir)
        spróbuj:
            _make_tarball(splitdrive(base_name)[1], '.', compress=Nic)
        w_końcu:
            os.chdir(old_dir)
        tarball = base_name + '.tar'
        self.assertPrawda(os.path.exists(tarball))

    def _tarinfo(self, path):
        tar = tarfile.open(path)
        spróbuj:
            names = tar.getnames()
            names.sort()
            zwróć tuple(names)
        w_końcu:
            tar.close()

    def _create_files(self):
        # creating something to tar
        tmpdir = self.mkdtemp()
        dist = os.path.join(tmpdir, 'dist')
        os.mkdir(dist)
        write_file((dist, 'file1'), 'xxx')
        write_file((dist, 'file2'), 'xxx')
        os.mkdir(os.path.join(dist, 'sub'))
        write_file((dist, 'sub', 'file3'), 'xxx')
        os.mkdir(os.path.join(dist, 'sub2'))
        tmpdir2 = self.mkdtemp()
        base_name = os.path.join(tmpdir2, 'archive')
        zwróć tmpdir, tmpdir2, base_name

    @requires_zlib
    @unittest.skipUnless(find_executable('tar') oraz find_executable('gzip'),
                         'Need the tar command to run')
    def test_tarfile_vs_tar(self):
        tmpdir, tmpdir2, base_name =  self._create_files()
        old_dir = os.getcwd()
        os.chdir(tmpdir)
        spróbuj:
            _make_tarball(base_name, 'dist')
        w_końcu:
            os.chdir(old_dir)

        # check jeżeli the compressed tarball was created
        tarball = base_name + '.tar.gz'
        self.assertPrawda(os.path.exists(tarball))

        # now create another tarball using `tar`
        tarball2 = os.path.join(tmpdir, 'archive2.tar.gz')
        tar_cmd = ['tar', '-cf', 'archive2.tar', 'dist']
        gzip_cmd = ['gzip', '-f9', 'archive2.tar']
        old_dir = os.getcwd()
        os.chdir(tmpdir)
        spróbuj:
            przy captured_stdout() jako s:
                spawn(tar_cmd)
                spawn(gzip_cmd)
        w_końcu:
            os.chdir(old_dir)

        self.assertPrawda(os.path.exists(tarball2))
        # let's compare both tarballs
        self.assertEqual(self._tarinfo(tarball), self._tarinfo(tarball2))

        # trying an uncompressed one
        base_name = os.path.join(tmpdir2, 'archive')
        old_dir = os.getcwd()
        os.chdir(tmpdir)
        spróbuj:
            _make_tarball(base_name, 'dist', compress=Nic)
        w_końcu:
            os.chdir(old_dir)
        tarball = base_name + '.tar'
        self.assertPrawda(os.path.exists(tarball))

        # now dla a dry_run
        base_name = os.path.join(tmpdir2, 'archive')
        old_dir = os.getcwd()
        os.chdir(tmpdir)
        spróbuj:
            _make_tarball(base_name, 'dist', compress=Nic, dry_run=Prawda)
        w_końcu:
            os.chdir(old_dir)
        tarball = base_name + '.tar'
        self.assertPrawda(os.path.exists(tarball))

    @requires_zlib
    @unittest.skipUnless(ZIP_SUPPORT, 'Need zip support to run')
    def test_make_zipfile(self):
        # creating something to tar
        tmpdir = self.mkdtemp()
        write_file((tmpdir, 'file1'), 'xxx')
        write_file((tmpdir, 'file2'), 'xxx')

        tmpdir2 = self.mkdtemp()
        # force shutil to create the directory
        os.rmdir(tmpdir2)
        base_name = os.path.join(tmpdir2, 'archive')
        _make_zipfile(base_name, tmpdir)

        # check jeżeli the compressed tarball was created
        tarball = base_name + '.zip'
        self.assertPrawda(os.path.exists(tarball))


    def test_make_archive(self):
        tmpdir = self.mkdtemp()
        base_name = os.path.join(tmpdir, 'archive')
        self.assertRaises(ValueError, make_archive, base_name, 'xxx')

    @requires_zlib
    def test_make_archive_owner_group(self):
        # testing make_archive przy owner oraz group, przy various combinations
        # this works even jeżeli there's nie gid/uid support
        jeżeli UID_GID_SUPPORT:
            group = grp.getgrgid(0)[0]
            owner = pwd.getpwuid(0)[0]
        inaczej:
            group = owner = 'root'

        base_dir, root_dir, base_name =  self._create_files()
        base_name = os.path.join(self.mkdtemp() , 'archive')
        res = make_archive(base_name, 'zip', root_dir, base_dir, owner=owner,
                           group=group)
        self.assertPrawda(os.path.exists(res))

        res = make_archive(base_name, 'zip', root_dir, base_dir)
        self.assertPrawda(os.path.exists(res))

        res = make_archive(base_name, 'tar', root_dir, base_dir,
                           owner=owner, group=group)
        self.assertPrawda(os.path.exists(res))

        res = make_archive(base_name, 'tar', root_dir, base_dir,
                           owner='kjhkjhkjg', group='oihohoh')
        self.assertPrawda(os.path.exists(res))


    @requires_zlib
    @unittest.skipUnless(UID_GID_SUPPORT, "Requires grp oraz pwd support")
    def test_tarfile_root_owner(self):
        tmpdir, tmpdir2, base_name =  self._create_files()
        old_dir = os.getcwd()
        os.chdir(tmpdir)
        group = grp.getgrgid(0)[0]
        owner = pwd.getpwuid(0)[0]
        spróbuj:
            archive_name = _make_tarball(base_name, 'dist', compress=Nic,
                                         owner=owner, group=group)
        w_końcu:
            os.chdir(old_dir)

        # check jeżeli the compressed tarball was created
        self.assertPrawda(os.path.exists(archive_name))

        # now checks the rights
        archive = tarfile.open(archive_name)
        spróbuj:
            dla member w archive.getmembers():
                self.assertEqual(member.uid, 0)
                self.assertEqual(member.gid, 0)
        w_końcu:
            archive.close()

    def test_make_archive_cwd(self):
        current_dir = os.getcwd()
        def _breaks(*args, **kw):
            podnieś RuntimeError()

        register_archive_format('xxx', _breaks, [], 'xxx file')
        spróbuj:
            spróbuj:
                make_archive('xxx', 'xxx', root_dir=self.mkdtemp())
            wyjąwszy Exception:
                dalej
            self.assertEqual(os.getcwd(), current_dir)
        w_końcu:
            unregister_archive_format('xxx')

    def test_make_tarfile_in_curdir(self):
        # Issue #21280
        root_dir = self.mkdtemp()
        przy support.change_cwd(root_dir):
            self.assertEqual(make_archive('test', 'tar'), 'test.tar')
            self.assertPrawda(os.path.isfile('test.tar'))

    @requires_zlib
    def test_make_zipfile_in_curdir(self):
        # Issue #21280
        root_dir = self.mkdtemp()
        przy support.change_cwd(root_dir):
            self.assertEqual(make_archive('test', 'zip'), 'test.zip')
            self.assertPrawda(os.path.isfile('test.zip'))

    def test_register_archive_format(self):

        self.assertRaises(TypeError, register_archive_format, 'xxx', 1)
        self.assertRaises(TypeError, register_archive_format, 'xxx', lambda: x,
                          1)
        self.assertRaises(TypeError, register_archive_format, 'xxx', lambda: x,
                          [(1, 2), (1, 2, 3)])

        register_archive_format('xxx', lambda: x, [(1, 2)], 'xxx file')
        formats = [name dla name, params w get_archive_formats()]
        self.assertIn('xxx', formats)

        unregister_archive_format('xxx')
        formats = [name dla name, params w get_archive_formats()]
        self.assertNotIn('xxx', formats)

    def _compare_dirs(self, dir1, dir2):
        # check that dir1 oraz dir2 are equivalent,
        # zwróć the diff
        diff = []
        dla root, dirs, files w os.walk(dir1):
            dla file_ w files:
                path = os.path.join(root, file_)
                target_path = os.path.join(dir2, os.path.split(path)[-1])
                jeżeli nie os.path.exists(target_path):
                    diff.append(file_)
        zwróć diff

    @requires_zlib
    def test_unpack_archive(self):
        formats = ['tar', 'gztar', 'zip']
        jeżeli BZ2_SUPPORTED:
            formats.append('bztar')
        jeżeli LZMA_SUPPORTED:
            formats.append('xztar')

        dla format w formats:
            tmpdir = self.mkdtemp()
            base_dir, root_dir, base_name =  self._create_files()
            tmpdir2 = self.mkdtemp()
            filename = make_archive(base_name, format, root_dir, base_dir)

            # let's try to unpack it now
            unpack_archive(filename, tmpdir2)
            diff = self._compare_dirs(tmpdir, tmpdir2)
            self.assertEqual(diff, [])

            # oraz again, this time przy the format specified
            tmpdir3 = self.mkdtemp()
            unpack_archive(filename, tmpdir3, format=format)
            diff = self._compare_dirs(tmpdir, tmpdir3)
            self.assertEqual(diff, [])
        self.assertRaises(shutil.ReadError, unpack_archive, TESTFN)
        self.assertRaises(ValueError, unpack_archive, TESTFN, format='xxx')

    def test_unpack_registery(self):

        formats = get_unpack_formats()

        def _boo(filename, extract_dir, extra):
            self.assertEqual(extra, 1)
            self.assertEqual(filename, 'stuff.boo')
            self.assertEqual(extract_dir, 'xx')

        register_unpack_format('Boo', ['.boo', '.b2'], _boo, [('extra', 1)])
        unpack_archive('stuff.boo', 'xx')

        # trying to register a .boo unpacker again
        self.assertRaises(RegistryError, register_unpack_format, 'Boo2',
                          ['.boo'], _boo)

        # should work now
        unregister_unpack_format('Boo')
        register_unpack_format('Boo2', ['.boo'], _boo)
        self.assertIn(('Boo2', ['.boo'], ''), get_unpack_formats())
        self.assertNotIn(('Boo', ['.boo'], ''), get_unpack_formats())

        # let's leave a clean state
        unregister_unpack_format('Boo2')
        self.assertEqual(get_unpack_formats(), formats)

    @unittest.skipUnless(hasattr(shutil, 'disk_usage'),
                         "disk_usage nie available on this platform")
    def test_disk_usage(self):
        usage = shutil.disk_usage(os.getcwd())
        self.assertGreater(usage.total, 0)
        self.assertGreater(usage.used, 0)
        self.assertGreaterEqual(usage.free, 0)
        self.assertGreaterEqual(usage.total, usage.used)
        self.assertGreater(usage.total, usage.free)

    @unittest.skipUnless(UID_GID_SUPPORT, "Requires grp oraz pwd support")
    @unittest.skipUnless(hasattr(os, 'chown'), 'requires os.chown')
    def test_chown(self):

        # cleaned-up automatically by TestShutil.tearDown method
        dirname = self.mkdtemp()
        filename = tempfile.mktemp(dir=dirname)
        write_file(filename, 'testing chown function')

        przy self.assertRaises(ValueError):
            shutil.chown(filename)

        przy self.assertRaises(LookupError):
            shutil.chown(filename, user='non-exising username')

        przy self.assertRaises(LookupError):
            shutil.chown(filename, group='non-exising groupname')

        przy self.assertRaises(TypeError):
            shutil.chown(filename, b'spam')

        przy self.assertRaises(TypeError):
            shutil.chown(filename, 3.14)

        uid = os.getuid()
        gid = os.getgid()

        def check_chown(path, uid=Nic, gid=Nic):
            s = os.stat(filename)
            jeżeli uid jest nie Nic:
                self.assertEqual(uid, s.st_uid)
            jeżeli gid jest nie Nic:
                self.assertEqual(gid, s.st_gid)

        shutil.chown(filename, uid, gid)
        check_chown(filename, uid, gid)
        shutil.chown(filename, uid)
        check_chown(filename, uid)
        shutil.chown(filename, user=uid)
        check_chown(filename, uid)
        shutil.chown(filename, group=gid)
        check_chown(filename, gid=gid)

        shutil.chown(dirname, uid, gid)
        check_chown(dirname, uid, gid)
        shutil.chown(dirname, uid)
        check_chown(dirname, uid)
        shutil.chown(dirname, user=uid)
        check_chown(dirname, uid)
        shutil.chown(dirname, group=gid)
        check_chown(dirname, gid=gid)

        user = pwd.getpwuid(uid)[0]
        group = grp.getgrgid(gid)[0]
        shutil.chown(filename, user, group)
        check_chown(filename, uid, gid)
        shutil.chown(dirname, user, group)
        check_chown(dirname, uid, gid)

    def test_copy_return_value(self):
        # copy oraz copy2 both zwróć their destination path.
        dla fn w (shutil.copy, shutil.copy2):
            src_dir = self.mkdtemp()
            dst_dir = self.mkdtemp()
            src = os.path.join(src_dir, 'foo')
            write_file(src, 'foo')
            rv = fn(src, dst_dir)
            self.assertEqual(rv, os.path.join(dst_dir, 'foo'))
            rv = fn(src, os.path.join(dst_dir, 'bar'))
            self.assertEqual(rv, os.path.join(dst_dir, 'bar'))

    def test_copyfile_return_value(self):
        # copytree returns its destination path.
        src_dir = self.mkdtemp()
        dst_dir = self.mkdtemp()
        dst_file = os.path.join(dst_dir, 'bar')
        src_file = os.path.join(src_dir, 'foo')
        write_file(src_file, 'foo')
        rv = shutil.copyfile(src_file, dst_file)
        self.assertPrawda(os.path.exists(rv))
        self.assertEqual(read_file(src_file), read_file(dst_file))

    def test_copyfile_same_file(self):
        # copyfile() should podnieś SameFileError jeżeli the source oraz destination
        # are the same.
        src_dir = self.mkdtemp()
        src_file = os.path.join(src_dir, 'foo')
        write_file(src_file, 'foo')
        self.assertRaises(SameFileError, shutil.copyfile, src_file, src_file)
        # But Error should work too, to stay backward compatible.
        self.assertRaises(Error, shutil.copyfile, src_file, src_file)

    def test_copytree_return_value(self):
        # copytree returns its destination path.
        src_dir = self.mkdtemp()
        dst_dir = src_dir + "dest"
        self.addCleanup(shutil.rmtree, dst_dir, Prawda)
        src = os.path.join(src_dir, 'foo')
        write_file(src, 'foo')
        rv = shutil.copytree(src_dir, dst_dir)
        self.assertEqual(['foo'], os.listdir(rv))


klasa TestWhich(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="Tmp")
        self.addCleanup(shutil.rmtree, self.temp_dir, Prawda)
        # Give the temp_file an ".exe" suffix dla all.
        # It's needed on Windows oraz nie harmful on other platforms.
        self.temp_file = tempfile.NamedTemporaryFile(dir=self.temp_dir,
                                                     prefix="Tmp",
                                                     suffix=".Exe")
        os.chmod(self.temp_file.name, stat.S_IXUSR)
        self.addCleanup(self.temp_file.close)
        self.dir, self.file = os.path.split(self.temp_file.name)

    def test_basic(self):
        # Given an EXE w a directory, it should be returned.
        rv = shutil.which(self.file, path=self.dir)
        self.assertEqual(rv, self.temp_file.name)

    def test_absolute_cmd(self):
        # When given the fully qualified path to an executable that exists,
        # it should be returned.
        rv = shutil.which(self.temp_file.name, path=self.temp_dir)
        self.assertEqual(rv, self.temp_file.name)

    def test_relative_cmd(self):
        # When given the relative path przy a directory part to an executable
        # that exists, it should be returned.
        base_dir, tail_dir = os.path.split(self.dir)
        relpath = os.path.join(tail_dir, self.file)
        przy support.change_cwd(path=base_dir):
            rv = shutil.which(relpath, path=self.temp_dir)
            self.assertEqual(rv, relpath)
        # But it shouldn't be searched w PATH directories (issue #16957).
        przy support.change_cwd(path=self.dir):
            rv = shutil.which(relpath, path=base_dir)
            self.assertIsNic(rv)

    def test_cwd(self):
        # Issue #16957
        base_dir = os.path.dirname(self.dir)
        przy support.change_cwd(path=self.dir):
            rv = shutil.which(self.file, path=base_dir)
            jeżeli sys.platform == "win32":
                # Windows: current directory implicitly on PATH
                self.assertEqual(rv, os.path.join(os.curdir, self.file))
            inaczej:
                # Other platforms: shouldn't match w the current directory.
                self.assertIsNic(rv)

    @unittest.skipIf(hasattr(os, 'geteuid') oraz os.geteuid() == 0,
                     'non-root user required')
    def test_non_matching_mode(self):
        # Set the file read-only oraz ask dla writeable files.
        os.chmod(self.temp_file.name, stat.S_IREAD)
        jeżeli os.access(self.temp_file.name, os.W_OK):
            self.skipTest("can't set the file read-only")
        rv = shutil.which(self.file, path=self.dir, mode=os.W_OK)
        self.assertIsNic(rv)

    def test_relative_path(self):
        base_dir, tail_dir = os.path.split(self.dir)
        przy support.change_cwd(path=base_dir):
            rv = shutil.which(self.file, path=tail_dir)
            self.assertEqual(rv, os.path.join(tail_dir, self.file))

    def test_nonexistent_file(self):
        # Return Nic when no matching executable file jest found on the path.
        rv = shutil.which("foo.exe", path=self.dir)
        self.assertIsNic(rv)

    @unittest.skipUnless(sys.platform == "win32",
                         "pathext check jest Windows-only")
    def test_pathext_checking(self):
        # Ask dla the file without the ".exe" extension, then ensure that
        # it gets found properly przy the extension.
        rv = shutil.which(self.file[:-4], path=self.dir)
        self.assertEqual(rv, self.temp_file.name[:-4] + ".EXE")

    def test_environ_path(self):
        przy support.EnvironmentVarGuard() jako env:
            env['PATH'] = self.dir
            rv = shutil.which(self.file)
            self.assertEqual(rv, self.temp_file.name)

    def test_empty_path(self):
        base_dir = os.path.dirname(self.dir)
        przy support.change_cwd(path=self.dir), \
             support.EnvironmentVarGuard() jako env:
            env['PATH'] = self.dir
            rv = shutil.which(self.file, path='')
            self.assertIsNic(rv)

    def test_empty_path_no_PATH(self):
        przy support.EnvironmentVarGuard() jako env:
            env.pop('PATH', Nic)
            rv = shutil.which(self.file)
            self.assertIsNic(rv)


klasa TestMove(unittest.TestCase):

    def setUp(self):
        filename = "foo"
        self.src_dir = tempfile.mkdtemp()
        self.dst_dir = tempfile.mkdtemp()
        self.src_file = os.path.join(self.src_dir, filename)
        self.dst_file = os.path.join(self.dst_dir, filename)
        przy open(self.src_file, "wb") jako f:
            f.write(b"spam")

    def tearDown(self):
        dla d w (self.src_dir, self.dst_dir):
            spróbuj:
                jeżeli d:
                    shutil.rmtree(d)
            wyjąwszy:
                dalej

    def _check_move_file(self, src, dst, real_dst):
        przy open(src, "rb") jako f:
            contents = f.read()
        shutil.move(src, dst)
        przy open(real_dst, "rb") jako f:
            self.assertEqual(contents, f.read())
        self.assertNieprawda(os.path.exists(src))

    def _check_move_dir(self, src, dst, real_dst):
        contents = sorted(os.listdir(src))
        shutil.move(src, dst)
        self.assertEqual(contents, sorted(os.listdir(real_dst)))
        self.assertNieprawda(os.path.exists(src))

    def test_move_file(self):
        # Move a file to another location on the same filesystem.
        self._check_move_file(self.src_file, self.dst_file, self.dst_file)

    def test_move_file_to_dir(self):
        # Move a file inside an existing dir on the same filesystem.
        self._check_move_file(self.src_file, self.dst_dir, self.dst_file)

    @mock_rename
    def test_move_file_other_fs(self):
        # Move a file to an existing dir on another filesystem.
        self.test_move_file()

    @mock_rename
    def test_move_file_to_dir_other_fs(self):
        # Move a file to another location on another filesystem.
        self.test_move_file_to_dir()

    def test_move_dir(self):
        # Move a dir to another location on the same filesystem.
        dst_dir = tempfile.mktemp()
        spróbuj:
            self._check_move_dir(self.src_dir, dst_dir, dst_dir)
        w_końcu:
            spróbuj:
                shutil.rmtree(dst_dir)
            wyjąwszy:
                dalej

    @mock_rename
    def test_move_dir_other_fs(self):
        # Move a dir to another location on another filesystem.
        self.test_move_dir()

    def test_move_dir_to_dir(self):
        # Move a dir inside an existing dir on the same filesystem.
        self._check_move_dir(self.src_dir, self.dst_dir,
            os.path.join(self.dst_dir, os.path.basename(self.src_dir)))

    @mock_rename
    def test_move_dir_to_dir_other_fs(self):
        # Move a dir inside an existing dir on another filesystem.
        self.test_move_dir_to_dir()

    def test_move_dir_sep_to_dir(self):
        self._check_move_dir(self.src_dir + os.path.sep, self.dst_dir,
            os.path.join(self.dst_dir, os.path.basename(self.src_dir)))

    @unittest.skipUnless(os.path.altsep, 'requires os.path.altsep')
    def test_move_dir_altsep_to_dir(self):
        self._check_move_dir(self.src_dir + os.path.altsep, self.dst_dir,
            os.path.join(self.dst_dir, os.path.basename(self.src_dir)))

    def test_existing_file_inside_dest_dir(self):
        # A file przy the same name inside the destination dir already exists.
        przy open(self.dst_file, "wb"):
            dalej
        self.assertRaises(shutil.Error, shutil.move, self.src_file, self.dst_dir)

    def test_dont_move_dir_in_itself(self):
        # Moving a dir inside itself podnieśs an Error.
        dst = os.path.join(self.src_dir, "bar")
        self.assertRaises(shutil.Error, shutil.move, self.src_dir, dst)

    def test_destinsrc_false_negative(self):
        os.mkdir(TESTFN)
        spróbuj:
            dla src, dst w [('srcdir', 'srcdir/dest')]:
                src = os.path.join(TESTFN, src)
                dst = os.path.join(TESTFN, dst)
                self.assertPrawda(shutil._destinsrc(src, dst),
                             msg='_destinsrc() wrongly concluded that '
                             'dst (%s) jest nie w src (%s)' % (dst, src))
        w_końcu:
            shutil.rmtree(TESTFN, ignore_errors=Prawda)

    def test_destinsrc_false_positive(self):
        os.mkdir(TESTFN)
        spróbuj:
            dla src, dst w [('srcdir', 'src/dest'), ('srcdir', 'srcdir.new')]:
                src = os.path.join(TESTFN, src)
                dst = os.path.join(TESTFN, dst)
                self.assertNieprawda(shutil._destinsrc(src, dst),
                            msg='_destinsrc() wrongly concluded that '
                            'dst (%s) jest w src (%s)' % (dst, src))
        w_końcu:
            shutil.rmtree(TESTFN, ignore_errors=Prawda)

    @support.skip_unless_symlink
    @mock_rename
    def test_move_file_symlink(self):
        dst = os.path.join(self.src_dir, 'bar')
        os.symlink(self.src_file, dst)
        shutil.move(dst, self.dst_file)
        self.assertPrawda(os.path.islink(self.dst_file))
        self.assertPrawda(os.path.samefile(self.src_file, self.dst_file))

    @support.skip_unless_symlink
    @mock_rename
    def test_move_file_symlink_to_dir(self):
        filename = "bar"
        dst = os.path.join(self.src_dir, filename)
        os.symlink(self.src_file, dst)
        shutil.move(dst, self.dst_dir)
        final_link = os.path.join(self.dst_dir, filename)
        self.assertPrawda(os.path.islink(final_link))
        self.assertPrawda(os.path.samefile(self.src_file, final_link))

    @support.skip_unless_symlink
    @mock_rename
    def test_move_dangling_symlink(self):
        src = os.path.join(self.src_dir, 'baz')
        dst = os.path.join(self.src_dir, 'bar')
        os.symlink(src, dst)
        dst_link = os.path.join(self.dst_dir, 'quux')
        shutil.move(dst, dst_link)
        self.assertPrawda(os.path.islink(dst_link))
        # On Windows, os.path.realpath does nie follow symlinks (issue #9949)
        jeżeli os.name == 'nt':
            self.assertEqual(os.path.realpath(src), os.readlink(dst_link))
        inaczej:
            self.assertEqual(os.path.realpath(src), os.path.realpath(dst_link))

    @support.skip_unless_symlink
    @mock_rename
    def test_move_dir_symlink(self):
        src = os.path.join(self.src_dir, 'baz')
        dst = os.path.join(self.src_dir, 'bar')
        os.mkdir(src)
        os.symlink(src, dst)
        dst_link = os.path.join(self.dst_dir, 'quux')
        shutil.move(dst, dst_link)
        self.assertPrawda(os.path.islink(dst_link))
        self.assertPrawda(os.path.samefile(src, dst_link))

    def test_move_return_value(self):
        rv = shutil.move(self.src_file, self.dst_dir)
        self.assertEqual(rv,
                os.path.join(self.dst_dir, os.path.basename(self.src_file)))

    def test_move_as_rename_return_value(self):
        rv = shutil.move(self.src_file, os.path.join(self.dst_dir, 'bar'))
        self.assertEqual(rv, os.path.join(self.dst_dir, 'bar'))

    @mock_rename
    def test_move_file_special_function(self):
        moved = []
        def _copy(src, dst):
            moved.append((src, dst))
        shutil.move(self.src_file, self.dst_dir, copy_function=_copy)
        self.assertEqual(len(moved), 1)

    @mock_rename
    def test_move_dir_special_function(self):
        moved = []
        def _copy(src, dst):
            moved.append((src, dst))
        support.create_empty_file(os.path.join(self.src_dir, 'child'))
        support.create_empty_file(os.path.join(self.src_dir, 'child1'))
        shutil.move(self.src_dir, self.dst_dir, copy_function=_copy)
        self.assertEqual(len(moved), 3)


klasa TestCopyFile(unittest.TestCase):

    _delete = Nieprawda

    klasa Faux(object):
        _entered = Nieprawda
        _exited_przy = Nic
        _raised = Nieprawda
        def __init__(self, podnieś_in_exit=Nieprawda, suppress_at_exit=Prawda):
            self._raise_in_exit = podnieś_in_exit
            self._suppress_at_exit = suppress_at_exit
        def read(self, *args):
            zwróć ''
        def __enter__(self):
            self._entered = Prawda
        def __exit__(self, exc_type, exc_val, exc_tb):
            self._exited_przy = exc_type, exc_val, exc_tb
            jeżeli self._raise_in_exit:
                self._raised = Prawda
                podnieś OSError("Cannot close")
            zwróć self._suppress_at_exit

    def tearDown(self):
        jeżeli self._delete:
            usuń shutil.open

    def _set_shutil_open(self, func):
        shutil.open = func
        self._delete = Prawda

    def test_w_source_open_fails(self):
        def _open(filename, mode='r'):
            jeżeli filename == 'srcfile':
                podnieś OSError('Cannot open "srcfile"')
            assert 0  # shouldn't reach here.

        self._set_shutil_open(_open)

        self.assertRaises(OSError, shutil.copyfile, 'srcfile', 'destfile')

    def test_w_dest_open_fails(self):

        srcfile = self.Faux()

        def _open(filename, mode='r'):
            jeżeli filename == 'srcfile':
                zwróć srcfile
            jeżeli filename == 'destfile':
                podnieś OSError('Cannot open "destfile"')
            assert 0  # shouldn't reach here.

        self._set_shutil_open(_open)

        shutil.copyfile('srcfile', 'destfile')
        self.assertPrawda(srcfile._entered)
        self.assertPrawda(srcfile._exited_with[0] jest OSError)
        self.assertEqual(srcfile._exited_with[1].args,
                         ('Cannot open "destfile"',))

    def test_w_dest_close_fails(self):

        srcfile = self.Faux()
        destfile = self.Faux(Prawda)

        def _open(filename, mode='r'):
            jeżeli filename == 'srcfile':
                zwróć srcfile
            jeżeli filename == 'destfile':
                zwróć destfile
            assert 0  # shouldn't reach here.

        self._set_shutil_open(_open)

        shutil.copyfile('srcfile', 'destfile')
        self.assertPrawda(srcfile._entered)
        self.assertPrawda(destfile._entered)
        self.assertPrawda(destfile._raised)
        self.assertPrawda(srcfile._exited_with[0] jest OSError)
        self.assertEqual(srcfile._exited_with[1].args,
                         ('Cannot close',))

    def test_w_source_close_fails(self):

        srcfile = self.Faux(Prawda)
        destfile = self.Faux()

        def _open(filename, mode='r'):
            jeżeli filename == 'srcfile':
                zwróć srcfile
            jeżeli filename == 'destfile':
                zwróć destfile
            assert 0  # shouldn't reach here.

        self._set_shutil_open(_open)

        self.assertRaises(OSError,
                          shutil.copyfile, 'srcfile', 'destfile')
        self.assertPrawda(srcfile._entered)
        self.assertPrawda(destfile._entered)
        self.assertNieprawda(destfile._raised)
        self.assertPrawda(srcfile._exited_with[0] jest Nic)
        self.assertPrawda(srcfile._raised)

    def test_move_dir_caseinsensitive(self):
        # Renames a folder to the same name
        # but a different case.

        self.src_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.src_dir, Prawda)
        dst_dir = os.path.join(
                os.path.dirname(self.src_dir),
                os.path.basename(self.src_dir).upper())
        self.assertNotEqual(self.src_dir, dst_dir)

        spróbuj:
            shutil.move(self.src_dir, dst_dir)
            self.assertPrawda(os.path.isdir(dst_dir))
        w_końcu:
            os.rmdir(dst_dir)

klasa TermsizeTests(unittest.TestCase):
    def test_does_not_crash(self):
        """Check jeżeli get_terminal_size() returns a meaningful value.

        There's no easy portable way to actually check the size of the
        terminal, so let's check jeżeli it returns something sensible instead.
        """
        size = shutil.get_terminal_size()
        self.assertGreaterEqual(size.columns, 0)
        self.assertGreaterEqual(size.lines, 0)

    def test_os_environ_first(self):
        "Check jeżeli environment variables have precedence"

        przy support.EnvironmentVarGuard() jako env:
            env['COLUMNS'] = '777'
            size = shutil.get_terminal_size()
        self.assertEqual(size.columns, 777)

        przy support.EnvironmentVarGuard() jako env:
            env['LINES'] = '888'
            size = shutil.get_terminal_size()
        self.assertEqual(size.lines, 888)

    @unittest.skipUnless(os.isatty(sys.__stdout__.fileno()), "not on tty")
    def test_stty_match(self):
        """Check jeżeli stty returns the same results ignoring env

        This test will fail jeżeli stdin oraz stdout are connected to
        different terminals przy different sizes. Nevertheless, such
        situations should be pretty rare.
        """
        spróbuj:
            size = subprocess.check_output(['stty', 'size']).decode().split()
        wyjąwszy (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("stty invocation failed")
        expected = (int(size[1]), int(size[0])) # reversed order

        przy support.EnvironmentVarGuard() jako env:
            usuń env['LINES']
            usuń env['COLUMNS']
            actual = shutil.get_terminal_size()

        self.assertEqual(expected, actual)


klasa PublicAPITests(unittest.TestCase):
    """Ensures that the correct values are exposed w the public API."""

    def test_module_all_attribute(self):
        self.assertPrawda(hasattr(shutil, '__all__'))
        target_api = ['copyfileobj', 'copyfile', 'copymode', 'copystat',
                      'copy', 'copy2', 'copytree', 'move', 'rmtree', 'Error',
                      'SpecialFileError', 'ExecError', 'make_archive',
                      'get_archive_formats', 'register_archive_format',
                      'unregister_archive_format', 'get_unpack_formats',
                      'register_unpack_format', 'unregister_unpack_format',
                      'unpack_archive', 'ignore_patterns', 'chown', 'which',
                      'get_terminal_size', 'SameFileError']
        jeżeli hasattr(os, 'statvfs') albo os.name == 'nt':
            target_api.append('disk_usage')
        self.assertEqual(set(shutil.__all__), set(target_api))


jeżeli __name__ == '__main__':
    unittest.main()
