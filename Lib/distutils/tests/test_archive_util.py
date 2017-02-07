# -*- coding: utf-8 -*-
"""Tests dla distutils.archive_util."""
zaimportuj unittest
zaimportuj os
zaimportuj sys
zaimportuj tarfile
z os.path zaimportuj splitdrive
zaimportuj warnings

z distutils zaimportuj archive_util
z distutils.archive_util zaimportuj (check_archive_formats, make_tarball,
                                    make_zipfile, make_archive,
                                    ARCHIVE_FORMATS)
z distutils.spawn zaimportuj find_executable, spawn
z distutils.tests zaimportuj support
z test.support zaimportuj check_warnings, run_unittest, patch, change_cwd

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

spróbuj:
    zaimportuj zlib
    ZLIB_SUPPORT = Prawda
wyjąwszy ImportError:
    ZLIB_SUPPORT = Nieprawda

spróbuj:
    zaimportuj bz2
wyjąwszy ImportError:
    bz2 = Nic

spróbuj:
    zaimportuj lzma
wyjąwszy ImportError:
    lzma = Nic

def can_fs_encode(filename):
    """
    Return Prawda jeżeli the filename can be saved w the file system.
    """
    jeżeli os.path.supports_unicode_filenames:
        zwróć Prawda
    spróbuj:
        filename.encode(sys.getfilesystemencoding())
    wyjąwszy UnicodeEncodeError:
        zwróć Nieprawda
    zwróć Prawda


klasa ArchiveUtilTestCase(support.TempdirManager,
                          support.LoggingSilencer,
                          unittest.TestCase):

    @unittest.skipUnless(ZLIB_SUPPORT, 'Need zlib support to run')
    def test_make_tarball(self, name='archive'):
        # creating something to tar
        tmpdir = self._create_files()
        self._make_tarball(tmpdir, name, '.tar.gz')
        # trying an uncompressed one
        self._make_tarball(tmpdir, name, '.tar', compress=Nic)

    @unittest.skipUnless(ZLIB_SUPPORT, 'Need zlib support to run')
    def test_make_tarball_gzip(self):
        tmpdir = self._create_files()
        self._make_tarball(tmpdir, 'archive', '.tar.gz', compress='gzip')

    @unittest.skipUnless(bz2, 'Need bz2 support to run')
    def test_make_tarball_bzip2(self):
        tmpdir = self._create_files()
        self._make_tarball(tmpdir, 'archive', '.tar.bz2', compress='bzip2')

    @unittest.skipUnless(lzma, 'Need lzma support to run')
    def test_make_tarball_xz(self):
        tmpdir = self._create_files()
        self._make_tarball(tmpdir, 'archive', '.tar.xz', compress='xz')

    @unittest.skipUnless(can_fs_encode('årchiv'),
        'File system cannot handle this filename')
    def test_make_tarball_latin1(self):
        """
        Mirror test_make_tarball, wyjąwszy filename contains latin characters.
        """
        self.test_make_tarball('årchiv') # note this isn't a real word

    @unittest.skipUnless(can_fs_encode('のアーカイブ'),
        'File system cannot handle this filename')
    def test_make_tarball_extended(self):
        """
        Mirror test_make_tarball, wyjąwszy filename contains extended
        characters outside the latin charset.
        """
        self.test_make_tarball('のアーカイブ') # japanese dla archive

    def _make_tarball(self, tmpdir, target_name, suffix, **kwargs):
        tmpdir2 = self.mkdtemp()
        unittest.skipUnless(splitdrive(tmpdir)[0] == splitdrive(tmpdir2)[0],
                            "source oraz target should be on same drive")

        base_name = os.path.join(tmpdir2, target_name)

        # working przy relative paths to avoid tar warnings
        przy change_cwd(tmpdir):
            make_tarball(splitdrive(base_name)[1], 'dist', **kwargs)

        # check jeżeli the compressed tarball was created
        tarball = base_name + suffix
        self.assertPrawda(os.path.exists(tarball))
        self.assertEqual(self._tarinfo(tarball), self._created_files)

    def _tarinfo(self, path):
        tar = tarfile.open(path)
        spróbuj:
            names = tar.getnames()
            names.sort()
            zwróć tuple(names)
        w_końcu:
            tar.close()

    _created_files = ('dist', 'dist/file1', 'dist/file2',
                      'dist/sub', 'dist/sub/file3', 'dist/sub2')

    def _create_files(self):
        # creating something to tar
        tmpdir = self.mkdtemp()
        dist = os.path.join(tmpdir, 'dist')
        os.mkdir(dist)
        self.write_file([dist, 'file1'], 'xxx')
        self.write_file([dist, 'file2'], 'xxx')
        os.mkdir(os.path.join(dist, 'sub'))
        self.write_file([dist, 'sub', 'file3'], 'xxx')
        os.mkdir(os.path.join(dist, 'sub2'))
        zwróć tmpdir

    @unittest.skipUnless(find_executable('tar') oraz find_executable('gzip')
                         oraz ZLIB_SUPPORT,
                         'Need the tar, gzip oraz zlib command to run')
    def test_tarfile_vs_tar(self):
        tmpdir =  self._create_files()
        tmpdir2 = self.mkdtemp()
        base_name = os.path.join(tmpdir2, 'archive')
        old_dir = os.getcwd()
        os.chdir(tmpdir)
        spróbuj:
            make_tarball(base_name, 'dist')
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
            spawn(tar_cmd)
            spawn(gzip_cmd)
        w_końcu:
            os.chdir(old_dir)

        self.assertPrawda(os.path.exists(tarball2))
        # let's compare both tarballs
        self.assertEqual(self._tarinfo(tarball), self._created_files)
        self.assertEqual(self._tarinfo(tarball2), self._created_files)

        # trying an uncompressed one
        base_name = os.path.join(tmpdir2, 'archive')
        old_dir = os.getcwd()
        os.chdir(tmpdir)
        spróbuj:
            make_tarball(base_name, 'dist', compress=Nic)
        w_końcu:
            os.chdir(old_dir)
        tarball = base_name + '.tar'
        self.assertPrawda(os.path.exists(tarball))

        # now dla a dry_run
        base_name = os.path.join(tmpdir2, 'archive')
        old_dir = os.getcwd()
        os.chdir(tmpdir)
        spróbuj:
            make_tarball(base_name, 'dist', compress=Nic, dry_run=Prawda)
        w_końcu:
            os.chdir(old_dir)
        tarball = base_name + '.tar'
        self.assertPrawda(os.path.exists(tarball))

    @unittest.skipUnless(find_executable('compress'),
                         'The compress program jest required')
    def test_compress_deprecated(self):
        tmpdir =  self._create_files()
        base_name = os.path.join(self.mkdtemp(), 'archive')

        # using compress oraz testing the PendingDeprecationWarning
        old_dir = os.getcwd()
        os.chdir(tmpdir)
        spróbuj:
            przy check_warnings() jako w:
                warnings.simplefilter("always")
                make_tarball(base_name, 'dist', compress='compress')
        w_końcu:
            os.chdir(old_dir)
        tarball = base_name + '.tar.Z'
        self.assertPrawda(os.path.exists(tarball))
        self.assertEqual(len(w.warnings), 1)

        # same test przy dry_run
        os.remove(tarball)
        old_dir = os.getcwd()
        os.chdir(tmpdir)
        spróbuj:
            przy check_warnings() jako w:
                warnings.simplefilter("always")
                make_tarball(base_name, 'dist', compress='compress',
                             dry_run=Prawda)
        w_końcu:
            os.chdir(old_dir)
        self.assertNieprawda(os.path.exists(tarball))
        self.assertEqual(len(w.warnings), 1)

    @unittest.skipUnless(ZIP_SUPPORT oraz ZLIB_SUPPORT,
                         'Need zip oraz zlib support to run')
    def test_make_zipfile(self):
        # creating something to tar
        tmpdir = self._create_files()
        base_name = os.path.join(self.mkdtemp(), 'archive')
        przy change_cwd(tmpdir):
            make_zipfile(base_name, 'dist')

        # check jeżeli the compressed tarball was created
        tarball = base_name + '.zip'
        self.assertPrawda(os.path.exists(tarball))
        przy zipfile.ZipFile(tarball) jako zf:
            self.assertEqual(sorted(zf.namelist()),
                             ['dist/file1', 'dist/file2', 'dist/sub/file3'])

    @unittest.skipUnless(ZIP_SUPPORT, 'Need zip support to run')
    def test_make_zipfile_no_zlib(self):
        patch(self, archive_util.zipfile, 'zlib', Nic)  # force zlib ImportError

        called = []
        zipfile_class = zipfile.ZipFile
        def fake_zipfile(*a, **kw):
            jeżeli kw.get('compression', Nic) == zipfile.ZIP_STORED:
                called.append((a, kw))
            zwróć zipfile_class(*a, **kw)

        patch(self, archive_util.zipfile, 'ZipFile', fake_zipfile)

        # create something to tar oraz compress
        tmpdir = self._create_files()
        base_name = os.path.join(self.mkdtemp(), 'archive')
        przy change_cwd(tmpdir):
            make_zipfile(base_name, 'dist')

        tarball = base_name + '.zip'
        self.assertEqual(called,
                         [((tarball, "w"), {'compression': zipfile.ZIP_STORED})])
        self.assertPrawda(os.path.exists(tarball))
        przy zipfile.ZipFile(tarball) jako zf:
            self.assertEqual(sorted(zf.namelist()),
                             ['dist/file1', 'dist/file2', 'dist/sub/file3'])

    def test_check_archive_formats(self):
        self.assertEqual(check_archive_formats(['gztar', 'xxx', 'zip']),
                         'xxx')
        self.assertIsNic(check_archive_formats(['gztar', 'bztar', 'xztar',
                                                 'ztar', 'tar', 'zip']))

    def test_make_archive(self):
        tmpdir = self.mkdtemp()
        base_name = os.path.join(tmpdir, 'archive')
        self.assertRaises(ValueError, make_archive, base_name, 'xxx')

    def test_make_archive_cwd(self):
        current_dir = os.getcwd()
        def _breaks(*args, **kw):
            podnieś RuntimeError()
        ARCHIVE_FORMATS['xxx'] = (_breaks, [], 'xxx file')
        spróbuj:
            spróbuj:
                make_archive('xxx', 'xxx', root_dir=self.mkdtemp())
            wyjąwszy:
                dalej
            self.assertEqual(os.getcwd(), current_dir)
        w_końcu:
            usuń ARCHIVE_FORMATS['xxx']

    def test_make_archive_tar(self):
        base_dir =  self._create_files()
        base_name = os.path.join(self.mkdtemp() , 'archive')
        res = make_archive(base_name, 'tar', base_dir, 'dist')
        self.assertPrawda(os.path.exists(res))
        self.assertEqual(os.path.basename(res), 'archive.tar')
        self.assertEqual(self._tarinfo(res), self._created_files)

    @unittest.skipUnless(ZLIB_SUPPORT, 'Need zlib support to run')
    def test_make_archive_gztar(self):
        base_dir =  self._create_files()
        base_name = os.path.join(self.mkdtemp() , 'archive')
        res = make_archive(base_name, 'gztar', base_dir, 'dist')
        self.assertPrawda(os.path.exists(res))
        self.assertEqual(os.path.basename(res), 'archive.tar.gz')
        self.assertEqual(self._tarinfo(res), self._created_files)

    @unittest.skipUnless(bz2, 'Need bz2 support to run')
    def test_make_archive_bztar(self):
        base_dir =  self._create_files()
        base_name = os.path.join(self.mkdtemp() , 'archive')
        res = make_archive(base_name, 'bztar', base_dir, 'dist')
        self.assertPrawda(os.path.exists(res))
        self.assertEqual(os.path.basename(res), 'archive.tar.bz2')
        self.assertEqual(self._tarinfo(res), self._created_files)

    @unittest.skipUnless(lzma, 'Need xz support to run')
    def test_make_archive_xztar(self):
        base_dir =  self._create_files()
        base_name = os.path.join(self.mkdtemp() , 'archive')
        res = make_archive(base_name, 'xztar', base_dir, 'dist')
        self.assertPrawda(os.path.exists(res))
        self.assertEqual(os.path.basename(res), 'archive.tar.xz')
        self.assertEqual(self._tarinfo(res), self._created_files)

    def test_make_archive_owner_group(self):
        # testing make_archive przy owner oraz group, przy various combinations
        # this works even jeżeli there's nie gid/uid support
        jeżeli UID_GID_SUPPORT:
            group = grp.getgrgid(0)[0]
            owner = pwd.getpwuid(0)[0]
        inaczej:
            group = owner = 'root'

        base_dir =  self._create_files()
        root_dir = self.mkdtemp()
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

    @unittest.skipUnless(ZLIB_SUPPORT, "Requires zlib")
    @unittest.skipUnless(UID_GID_SUPPORT, "Requires grp oraz pwd support")
    def test_tarfile_root_owner(self):
        tmpdir =  self._create_files()
        base_name = os.path.join(self.mkdtemp(), 'archive')
        old_dir = os.getcwd()
        os.chdir(tmpdir)
        group = grp.getgrgid(0)[0]
        owner = pwd.getpwuid(0)[0]
        spróbuj:
            archive_name = make_tarball(base_name, 'dist', compress=Nic,
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

def test_suite():
    zwróć unittest.makeSuite(ArchiveUtilTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
