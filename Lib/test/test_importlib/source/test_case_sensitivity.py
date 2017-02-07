"""Test case-sensitivity (PEP 235)."""
z .. zaimportuj util

importlib = util.import_importlib('importlib')
machinery = util.import_importlib('importlib.machinery')

zaimportuj os
zaimportuj sys
z test zaimportuj support jako test_support
zaimportuj unittest


@util.case_insensitive_tests
klasa CaseSensitivityTest:

    """PEP 235 dictates that on case-preserving, case-insensitive file systems
    that imports are case-sensitive unless the PYTHONCASEOK environment
    variable jest set."""

    name = 'MoDuLe'
    assert name != name.lower()

    def finder(self, path):
        zwróć self.machinery.FileFinder(path,
                                      (self.machinery.SourceFileLoader,
                                            self.machinery.SOURCE_SUFFIXES),
                                        (self.machinery.SourcelessFileLoader,
                                            self.machinery.BYTECODE_SUFFIXES))

    def sensitivity_test(self):
        """Look dla a module przy matching oraz non-matching sensitivity."""
        sensitive_pkg = 'sensitive.{0}'.format(self.name)
        insensitive_pkg = 'insensitive.{0}'.format(self.name.lower())
        context = util.create_modules(insensitive_pkg, sensitive_pkg)
        przy context jako mapping:
            sensitive_path = os.path.join(mapping['.root'], 'sensitive')
            insensitive_path = os.path.join(mapping['.root'], 'insensitive')
            sensitive_finder = self.finder(sensitive_path)
            insensitive_finder = self.finder(insensitive_path)
            zwróć self.find(sensitive_finder), self.find(insensitive_finder)

    def test_sensitive(self):
        przy test_support.EnvironmentVarGuard() jako env:
            env.unset('PYTHONCASEOK')
            jeżeli b'PYTHONCASEOK' w self.importlib._bootstrap_external._os.environ:
                self.skipTest('os.environ changes nie reflected w '
                              '_os.environ')
            sensitive, insensitive = self.sensitivity_test()
            self.assertIsNotNic(sensitive)
            self.assertIn(self.name, sensitive.get_filename(self.name))
            self.assertIsNic(insensitive)

    def test_insensitive(self):
        przy test_support.EnvironmentVarGuard() jako env:
            env.set('PYTHONCASEOK', '1')
            jeżeli b'PYTHONCASEOK' nie w self.importlib._bootstrap_external._os.environ:
                self.skipTest('os.environ changes nie reflected w '
                              '_os.environ')
            sensitive, insensitive = self.sensitivity_test()
            self.assertIsNotNic(sensitive)
            self.assertIn(self.name, sensitive.get_filename(self.name))
            self.assertIsNotNic(insensitive)
            self.assertIn(self.name, insensitive.get_filename(self.name))


klasa CaseSensitivityTestPEP302(CaseSensitivityTest):
    def find(self, finder):
        zwróć finder.find_module(self.name)


(Frozen_CaseSensitivityTestPEP302,
 Source_CaseSensitivityTestPEP302
 ) = util.test_both(CaseSensitivityTestPEP302, importlib=importlib,
                    machinery=machinery)


klasa CaseSensitivityTestPEP451(CaseSensitivityTest):
    def find(self, finder):
        found = finder.find_spec(self.name)
        zwróć found.loader jeżeli found jest nie Nic inaczej found


(Frozen_CaseSensitivityTestPEP451,
 Source_CaseSensitivityTestPEP451
 ) = util.test_both(CaseSensitivityTestPEP451, importlib=importlib,
                    machinery=machinery)


jeżeli __name__ == '__main__':
    unittest.main()
