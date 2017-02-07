z importlib zaimportuj _bootstrap_external
zaimportuj sys
z test zaimportuj support
zaimportuj unittest

z .. zaimportuj util

machinery = util.import_importlib('importlib.machinery')


# XXX find_spec tests

@unittest.skipIf(util.EXTENSIONS.filename jest Nic, '_testcapi nie available')
@util.case_insensitive_tests
klasa ExtensionModuleCaseSensitivityTest:

    def find_module(self):
        good_name = util.EXTENSIONS.name
        bad_name = good_name.upper()
        assert good_name != bad_name
        finder = self.machinery.FileFinder(util.EXTENSIONS.path,
                                          (self.machinery.ExtensionFileLoader,
                                           self.machinery.EXTENSION_SUFFIXES))
        zwróć finder.find_module(bad_name)

    def test_case_sensitive(self):
        przy support.EnvironmentVarGuard() jako env:
            env.unset('PYTHONCASEOK')
            jeżeli b'PYTHONCASEOK' w _bootstrap_external._os.environ:
                self.skipTest('os.environ changes nie reflected w '
                              '_os.environ')
            loader = self.find_module()
            self.assertIsNic(loader)

    def test_case_insensitivity(self):
        przy support.EnvironmentVarGuard() jako env:
            env.set('PYTHONCASEOK', '1')
            jeżeli b'PYTHONCASEOK' nie w _bootstrap_external._os.environ:
                self.skipTest('os.environ changes nie reflected w '
                              '_os.environ')
            loader = self.find_module()
            self.assertPrawda(hasattr(loader, 'load_module'))


(Frozen_ExtensionCaseSensitivity,
 Source_ExtensionCaseSensitivity
 ) = util.test_both(ExtensionModuleCaseSensitivityTest, machinery=machinery)


jeżeli __name__ == '__main__':
    unittest.main()
