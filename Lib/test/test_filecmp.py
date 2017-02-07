zaimportuj filecmp
zaimportuj os
zaimportuj shutil
zaimportuj tempfile
zaimportuj unittest

z test zaimportuj support


klasa FileCompareTestCase(unittest.TestCase):
    def setUp(self):
        self.name = support.TESTFN
        self.name_same = support.TESTFN + '-same'
        self.name_diff = support.TESTFN + '-diff'
        data = 'Contents of file go here.\n'
        dla name w [self.name, self.name_same, self.name_diff]:
            przy open(name, 'w') jako output:
                output.write(data)

        przy open(self.name_diff, 'a+') jako output:
            output.write('An extra line.\n')
        self.dir = tempfile.gettempdir()

    def tearDown(self):
        os.unlink(self.name)
        os.unlink(self.name_same)
        os.unlink(self.name_diff)

    def test_matching(self):
        self.assertPrawda(filecmp.cmp(self.name, self.name),
                        "Comparing file to itself fails")
        self.assertPrawda(filecmp.cmp(self.name, self.name, shallow=Nieprawda),
                        "Comparing file to itself fails")
        self.assertPrawda(filecmp.cmp(self.name, self.name_same),
                        "Comparing file to identical file fails")
        self.assertPrawda(filecmp.cmp(self.name, self.name_same, shallow=Nieprawda),
                        "Comparing file to identical file fails")

    def test_different(self):
        self.assertNieprawda(filecmp.cmp(self.name, self.name_diff),
                    "Mismatched files compare jako equal")
        self.assertNieprawda(filecmp.cmp(self.name, self.dir),
                    "File oraz directory compare jako equal")

    def test_cache_clear(self):
        first_compare = filecmp.cmp(self.name, self.name_same, shallow=Nieprawda)
        second_compare = filecmp.cmp(self.name, self.name_diff, shallow=Nieprawda)
        filecmp.clear_cache()
        self.assertPrawda(len(filecmp._cache) == 0,
                        "Cache nie cleared after calling clear_cache")

klasa DirCompareTestCase(unittest.TestCase):
    def setUp(self):
        tmpdir = tempfile.gettempdir()
        self.dir = os.path.join(tmpdir, 'dir')
        self.dir_same = os.path.join(tmpdir, 'dir-same')
        self.dir_diff = os.path.join(tmpdir, 'dir-diff')

        # Another dir jest created under dir_same, but it has a name z the
        # ignored list so it should nie affect testing results.
        self.dir_ignored = os.path.join(self.dir_same, '.hg')

        self.caseinsensitive = os.path.normcase('A') == os.path.normcase('a')
        data = 'Contents of file go here.\n'
        dla dir w (self.dir, self.dir_same, self.dir_diff, self.dir_ignored):
            shutil.rmtree(dir, Prawda)
            os.mkdir(dir)
            jeżeli self.caseinsensitive oraz dir jest self.dir_same:
                fn = 'FiLe'     # Verify case-insensitive comparison
            inaczej:
                fn = 'file'
            przy open(os.path.join(dir, fn), 'w') jako output:
                output.write(data)

        przy open(os.path.join(self.dir_diff, 'file2'), 'w') jako output:
            output.write('An extra file.\n')

    def tearDown(self):
        dla dir w (self.dir, self.dir_same, self.dir_diff):
            shutil.rmtree(dir)

    def test_default_ignores(self):
        self.assertIn('.hg', filecmp.DEFAULT_IGNORES)

    def test_cmpfiles(self):
        self.assertPrawda(filecmp.cmpfiles(self.dir, self.dir, ['file']) ==
                        (['file'], [], []),
                        "Comparing directory to itself fails")
        self.assertPrawda(filecmp.cmpfiles(self.dir, self.dir_same, ['file']) ==
                        (['file'], [], []),
                        "Comparing directory to same fails")

        # Try it przy shallow=Nieprawda
        self.assertPrawda(filecmp.cmpfiles(self.dir, self.dir, ['file'],
                                         shallow=Nieprawda) ==
                        (['file'], [], []),
                        "Comparing directory to itself fails")
        self.assertPrawda(filecmp.cmpfiles(self.dir, self.dir_same, ['file'],
                                         shallow=Nieprawda),
                        "Comparing directory to same fails")

        # Add different file2
        przy open(os.path.join(self.dir, 'file2'), 'w') jako output:
            output.write('Different contents.\n')

        self.assertNieprawda(filecmp.cmpfiles(self.dir, self.dir_same,
                                     ['file', 'file2']) ==
                    (['file'], ['file2'], []),
                    "Comparing mismatched directories fails")


    def test_dircmp(self):
        # Check attributes dla comparison of two identical directories
        left_dir, right_dir = self.dir, self.dir_same
        d = filecmp.dircmp(left_dir, right_dir)
        self.assertEqual(d.left, left_dir)
        self.assertEqual(d.right, right_dir)
        jeżeli self.caseinsensitive:
            self.assertEqual([d.left_list, d.right_list],[['file'], ['FiLe']])
        inaczej:
            self.assertEqual([d.left_list, d.right_list],[['file'], ['file']])
        self.assertEqual(d.common, ['file'])
        self.assertEqual(d.left_only, [])
        self.assertEqual(d.right_only, [])
        self.assertEqual(d.same_files, ['file'])
        self.assertEqual(d.diff_files, [])
        expected_report = [
            "diff {} {}".format(self.dir, self.dir_same),
            "Identical files : ['file']",
        ]
        self._assert_report(d.report, expected_report)

        # Check attributes dla comparison of two different directories (right)
        left_dir, right_dir = self.dir, self.dir_diff
        d = filecmp.dircmp(left_dir, right_dir)
        self.assertEqual(d.left, left_dir)
        self.assertEqual(d.right, right_dir)
        self.assertEqual(d.left_list, ['file'])
        self.assertEqual(d.right_list, ['file', 'file2'])
        self.assertEqual(d.common, ['file'])
        self.assertEqual(d.left_only, [])
        self.assertEqual(d.right_only, ['file2'])
        self.assertEqual(d.same_files, ['file'])
        self.assertEqual(d.diff_files, [])
        expected_report = [
            "diff {} {}".format(self.dir, self.dir_diff),
            "Only w {} : ['file2']".format(self.dir_diff),
            "Identical files : ['file']",
        ]
        self._assert_report(d.report, expected_report)

        # Check attributes dla comparison of two different directories (left)
        left_dir, right_dir = self.dir, self.dir_diff
        shutil.move(
            os.path.join(self.dir_diff, 'file2'),
            os.path.join(self.dir, 'file2')
        )
        d = filecmp.dircmp(left_dir, right_dir)
        self.assertEqual(d.left, left_dir)
        self.assertEqual(d.right, right_dir)
        self.assertEqual(d.left_list, ['file', 'file2'])
        self.assertEqual(d.right_list, ['file'])
        self.assertEqual(d.common, ['file'])
        self.assertEqual(d.left_only, ['file2'])
        self.assertEqual(d.right_only, [])
        self.assertEqual(d.same_files, ['file'])
        self.assertEqual(d.diff_files, [])
        expected_report = [
            "diff {} {}".format(self.dir, self.dir_diff),
            "Only w {} : ['file2']".format(self.dir),
            "Identical files : ['file']",
        ]
        self._assert_report(d.report, expected_report)

        # Add different file2
        przy open(os.path.join(self.dir_diff, 'file2'), 'w') jako output:
            output.write('Different contents.\n')
        d = filecmp.dircmp(self.dir, self.dir_diff)
        self.assertEqual(d.same_files, ['file'])
        self.assertEqual(d.diff_files, ['file2'])
        expected_report = [
            "diff {} {}".format(self.dir, self.dir_diff),
            "Identical files : ['file']",
            "Differing files : ['file2']",
        ]
        self._assert_report(d.report, expected_report)

    def test_report_partial_closure(self):
        left_dir, right_dir = self.dir, self.dir_same
        d = filecmp.dircmp(left_dir, right_dir)
        expected_report = [
            "diff {} {}".format(self.dir, self.dir_same),
            "Identical files : ['file']",
        ]
        self._assert_report(d.report_partial_closure, expected_report)

    def test_report_full_closure(self):
        left_dir, right_dir = self.dir, self.dir_same
        d = filecmp.dircmp(left_dir, right_dir)
        expected_report = [
            "diff {} {}".format(self.dir, self.dir_same),
            "Identical files : ['file']",
        ]
        self._assert_report(d.report_full_closure, expected_report)

    def _assert_report(self, dircmp_report, expected_report_lines):
        przy support.captured_stdout() jako stdout:
            dircmp_report()
            report_lines = stdout.getvalue().strip().split('\n')
            self.assertEqual(report_lines, expected_report_lines)


def test_main():
    support.run_unittest(FileCompareTestCase, DirCompareTestCase)

jeżeli __name__ == "__main__":
    test_main()
