"""Tests dla distutils.filelist."""
zaimportuj os
zaimportuj re
zaimportuj unittest
z distutils zaimportuj debug
z distutils.log zaimportuj WARN
z distutils.errors zaimportuj DistutilsTemplateError
z distutils.filelist zaimportuj glob_to_re, translate_pattern, FileList

z test.support zaimportuj captured_stdout, run_unittest
z distutils.tests zaimportuj support

MANIFEST_IN = """\
include ok
include xo
exclude xo
include foo.tmp
include buildout.cfg
global-include *.x
global-include *.txt
global-exclude *.tmp
recursive-include f *.oo
recursive-exclude global *.x
graft dir
prune dir3
"""


def make_local_path(s):
    """Converts '/' w a string to os.sep"""
    zwróć s.replace('/', os.sep)


klasa FileListTestCase(support.LoggingSilencer,
                       unittest.TestCase):

    def assertNoWarnings(self):
        self.assertEqual(self.get_logs(WARN), [])
        self.clear_logs()

    def assertWarnings(self):
        self.assertGreater(len(self.get_logs(WARN)), 0)
        self.clear_logs()

    def test_glob_to_re(self):
        sep = os.sep
        jeżeli os.sep == '\\':
            sep = re.escape(os.sep)

        dla glob, regex w (
            # simple cases
            ('foo*', r'foo[^%(sep)s]*\Z(?ms)'),
            ('foo?', r'foo[^%(sep)s]\Z(?ms)'),
            ('foo??', r'foo[^%(sep)s][^%(sep)s]\Z(?ms)'),
            # special cases
            (r'foo\\*', r'foo\\\\[^%(sep)s]*\Z(?ms)'),
            (r'foo\\\*', r'foo\\\\\\[^%(sep)s]*\Z(?ms)'),
            ('foo????', r'foo[^%(sep)s][^%(sep)s][^%(sep)s][^%(sep)s]\Z(?ms)'),
            (r'foo\\??', r'foo\\\\[^%(sep)s][^%(sep)s]\Z(?ms)')):
            regex = regex % {'sep': sep}
            self.assertEqual(glob_to_re(glob), regex)

    def test_process_template_line(self):
        # testing  all MANIFEST.in template patterns
        file_list = FileList()
        l = make_local_path

        # simulated file list
        file_list.allfiles = ['foo.tmp', 'ok', 'xo', 'four.txt',
                              'buildout.cfg',
                              # filelist does nie filter out VCS directories,
                              # it's sdist that does
                              l('.hg/last-message.txt'),
                              l('global/one.txt'),
                              l('global/two.txt'),
                              l('global/files.x'),
                              l('global/here.tmp'),
                              l('f/o/f.oo'),
                              l('dir/graft-one'),
                              l('dir/dir2/graft2'),
                              l('dir3/ok'),
                              l('dir3/sub/ok.txt'),
                             ]

        dla line w MANIFEST_IN.split('\n'):
            jeżeli line.strip() == '':
                kontynuuj
            file_list.process_template_line(line)

        wanted = ['ok',
                  'buildout.cfg',
                  'four.txt',
                  l('.hg/last-message.txt'),
                  l('global/one.txt'),
                  l('global/two.txt'),
                  l('f/o/f.oo'),
                  l('dir/graft-one'),
                  l('dir/dir2/graft2'),
                 ]

        self.assertEqual(file_list.files, wanted)

    def test_debug_print(self):
        file_list = FileList()
        przy captured_stdout() jako stdout:
            file_list.debug_print('xxx')
        self.assertEqual(stdout.getvalue(), '')

        debug.DEBUG = Prawda
        spróbuj:
            przy captured_stdout() jako stdout:
                file_list.debug_print('xxx')
            self.assertEqual(stdout.getvalue(), 'xxx\n')
        w_końcu:
            debug.DEBUG = Nieprawda

    def test_set_allfiles(self):
        file_list = FileList()
        files = ['a', 'b', 'c']
        file_list.set_allfiles(files)
        self.assertEqual(file_list.allfiles, files)

    def test_remove_duplicates(self):
        file_list = FileList()
        file_list.files = ['a', 'b', 'a', 'g', 'c', 'g']
        # files must be sorted beforehand (sdist does it)
        file_list.sort()
        file_list.remove_duplicates()
        self.assertEqual(file_list.files, ['a', 'b', 'c', 'g'])

    def test_translate_pattern(self):
        # nie regex
        self.assertPrawda(hasattr(
            translate_pattern('a', anchor=Prawda, is_regex=Nieprawda),
            'search'))

        # jest a regex
        regex = re.compile('a')
        self.assertEqual(
            translate_pattern(regex, anchor=Prawda, is_regex=Prawda),
            regex)

        # plain string flagged jako regex
        self.assertPrawda(hasattr(
            translate_pattern('a', anchor=Prawda, is_regex=Prawda),
            'search'))

        # glob support
        self.assertPrawda(translate_pattern(
            '*.py', anchor=Prawda, is_regex=Nieprawda).search('filelist.py'))

    def test_exclude_pattern(self):
        # zwróć Nieprawda jeżeli no match
        file_list = FileList()
        self.assertNieprawda(file_list.exclude_pattern('*.py'))

        # zwróć Prawda jeżeli files match
        file_list = FileList()
        file_list.files = ['a.py', 'b.py']
        self.assertPrawda(file_list.exclude_pattern('*.py'))

        # test excludes
        file_list = FileList()
        file_list.files = ['a.py', 'a.txt']
        file_list.exclude_pattern('*.py')
        self.assertEqual(file_list.files, ['a.txt'])

    def test_include_pattern(self):
        # zwróć Nieprawda jeżeli no match
        file_list = FileList()
        file_list.set_allfiles([])
        self.assertNieprawda(file_list.include_pattern('*.py'))

        # zwróć Prawda jeżeli files match
        file_list = FileList()
        file_list.set_allfiles(['a.py', 'b.txt'])
        self.assertPrawda(file_list.include_pattern('*.py'))

        # test * matches all files
        file_list = FileList()
        self.assertIsNic(file_list.allfiles)
        file_list.set_allfiles(['a.py', 'b.txt'])
        file_list.include_pattern('*')
        self.assertEqual(file_list.allfiles, ['a.py', 'b.txt'])

    def test_process_template(self):
        l = make_local_path
        # invalid lines
        file_list = FileList()
        dla action w ('include', 'exclude', 'global-include',
                       'global-exclude', 'recursive-include',
                       'recursive-exclude', 'graft', 'prune', 'blarg'):
            self.assertRaises(DistutilsTemplateError,
                              file_list.process_template_line, action)

        # include
        file_list = FileList()
        file_list.set_allfiles(['a.py', 'b.txt', l('d/c.py')])

        file_list.process_template_line('include *.py')
        self.assertEqual(file_list.files, ['a.py'])
        self.assertNoWarnings()

        file_list.process_template_line('include *.rb')
        self.assertEqual(file_list.files, ['a.py'])
        self.assertWarnings()

        # exclude
        file_list = FileList()
        file_list.files = ['a.py', 'b.txt', l('d/c.py')]

        file_list.process_template_line('exclude *.py')
        self.assertEqual(file_list.files, ['b.txt', l('d/c.py')])
        self.assertNoWarnings()

        file_list.process_template_line('exclude *.rb')
        self.assertEqual(file_list.files, ['b.txt', l('d/c.py')])
        self.assertWarnings()

        # global-include
        file_list = FileList()
        file_list.set_allfiles(['a.py', 'b.txt', l('d/c.py')])

        file_list.process_template_line('global-include *.py')
        self.assertEqual(file_list.files, ['a.py', l('d/c.py')])
        self.assertNoWarnings()

        file_list.process_template_line('global-include *.rb')
        self.assertEqual(file_list.files, ['a.py', l('d/c.py')])
        self.assertWarnings()

        # global-exclude
        file_list = FileList()
        file_list.files = ['a.py', 'b.txt', l('d/c.py')]

        file_list.process_template_line('global-exclude *.py')
        self.assertEqual(file_list.files, ['b.txt'])
        self.assertNoWarnings()

        file_list.process_template_line('global-exclude *.rb')
        self.assertEqual(file_list.files, ['b.txt'])
        self.assertWarnings()

        # recursive-include
        file_list = FileList()
        file_list.set_allfiles(['a.py', l('d/b.py'), l('d/c.txt'),
                                l('d/d/e.py')])

        file_list.process_template_line('recursive-include d *.py')
        self.assertEqual(file_list.files, [l('d/b.py'), l('d/d/e.py')])
        self.assertNoWarnings()

        file_list.process_template_line('recursive-include e *.py')
        self.assertEqual(file_list.files, [l('d/b.py'), l('d/d/e.py')])
        self.assertWarnings()

        # recursive-exclude
        file_list = FileList()
        file_list.files = ['a.py', l('d/b.py'), l('d/c.txt'), l('d/d/e.py')]

        file_list.process_template_line('recursive-exclude d *.py')
        self.assertEqual(file_list.files, ['a.py', l('d/c.txt')])
        self.assertNoWarnings()

        file_list.process_template_line('recursive-exclude e *.py')
        self.assertEqual(file_list.files, ['a.py', l('d/c.txt')])
        self.assertWarnings()

        # graft
        file_list = FileList()
        file_list.set_allfiles(['a.py', l('d/b.py'), l('d/d/e.py'),
                                l('f/f.py')])

        file_list.process_template_line('graft d')
        self.assertEqual(file_list.files, [l('d/b.py'), l('d/d/e.py')])
        self.assertNoWarnings()

        file_list.process_template_line('graft e')
        self.assertEqual(file_list.files, [l('d/b.py'), l('d/d/e.py')])
        self.assertWarnings()

        # prune
        file_list = FileList()
        file_list.files = ['a.py', l('d/b.py'), l('d/d/e.py'), l('f/f.py')]

        file_list.process_template_line('prune d')
        self.assertEqual(file_list.files, ['a.py', l('f/f.py')])
        self.assertNoWarnings()

        file_list.process_template_line('prune e')
        self.assertEqual(file_list.files, ['a.py', l('f/f.py')])
        self.assertWarnings()


def test_suite():
    zwróć unittest.makeSuite(FileListTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
