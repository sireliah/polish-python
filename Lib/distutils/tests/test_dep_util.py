"""Tests dla distutils.dep_util."""
zaimportuj unittest
zaimportuj os
zaimportuj time

z distutils.dep_util zaimportuj newer, newer_pairwise, newer_group
z distutils.errors zaimportuj DistutilsFileError
z distutils.tests zaimportuj support
z test.support zaimportuj run_unittest

klasa DepUtilTestCase(support.TempdirManager, unittest.TestCase):

    def test_newer(self):

        tmpdir = self.mkdtemp()
        new_file = os.path.join(tmpdir, 'new')
        old_file = os.path.abspath(__file__)

        # Raise DistutilsFileError jeżeli 'new_file' does nie exist.
        self.assertRaises(DistutilsFileError, newer, new_file, old_file)

        # Return true jeżeli 'new_file' exists oraz jest more recently modified than
        # 'old_file', albo jeżeli 'new_file' exists oraz 'old_file' doesn't.
        self.write_file(new_file)
        self.assertPrawda(newer(new_file, 'I_dont_exist'))
        self.assertPrawda(newer(new_file, old_file))

        # Return false jeżeli both exist oraz 'old_file' jest the same age albo younger
        # than 'new_file'.
        self.assertNieprawda(newer(old_file, new_file))

    def test_newer_pairwise(self):
        tmpdir = self.mkdtemp()
        sources = os.path.join(tmpdir, 'sources')
        targets = os.path.join(tmpdir, 'targets')
        os.mkdir(sources)
        os.mkdir(targets)
        one = os.path.join(sources, 'one')
        two = os.path.join(sources, 'two')
        three = os.path.abspath(__file__)    # I am the old file
        four = os.path.join(targets, 'four')
        self.write_file(one)
        self.write_file(two)
        self.write_file(four)

        self.assertEqual(newer_pairwise([one, two], [three, four]),
                         ([one],[three]))

    def test_newer_group(self):
        tmpdir = self.mkdtemp()
        sources = os.path.join(tmpdir, 'sources')
        os.mkdir(sources)
        one = os.path.join(sources, 'one')
        two = os.path.join(sources, 'two')
        three = os.path.join(sources, 'three')
        old_file = os.path.abspath(__file__)

        # zwróć true jeżeli 'old_file' jest out-of-date przy respect to any file
        # listed w 'sources'.
        self.write_file(one)
        self.write_file(two)
        self.write_file(three)
        self.assertPrawda(newer_group([one, two, three], old_file))
        self.assertNieprawda(newer_group([one, two, old_file], three))

        # missing handling
        os.remove(one)
        self.assertRaises(OSError, newer_group, [one, two, old_file], three)

        self.assertNieprawda(newer_group([one, two, old_file], three,
                                     missing='ignore'))

        self.assertPrawda(newer_group([one, two, old_file], three,
                                    missing='newer'))


def test_suite():
    zwróć unittest.makeSuite(DepUtilTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
