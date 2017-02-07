"""Test that sys.modules jest used properly by import."""
z .. zaimportuj util
zaimportuj sys
z types zaimportuj MethodType
zaimportuj unittest


klasa UseCache:

    """When it comes to sys.modules, zaimportuj prefers it over anything inaczej.

    Once a name has been resolved, sys.modules jest checked to see jeżeli it contains
    the module desired. If so, then it jest returned [use cache]. If it jest nie
    found, then the proper steps are taken to perform the import, but
    sys.modules jest still used to zwróć the imported module (e.g., nie what a
    loader returns) [z cache on return]. This also applies to imports of
    things contained within a package oraz thus get assigned jako an attribute
    [z cache to attribute] albo pulled w thanks to a fromlist import
    [z cache dla fromlist]. But jeżeli sys.modules contains Nic then
    ImportError jest podnieśd [Nic w cache].

    """

    def test_using_cache(self):
        # [use cache]
        module_to_use = "some module found!"
        przy util.uncache('some_module'):
            sys.modules['some_module'] = module_to_use
            module = self.__import__('some_module')
            self.assertEqual(id(module_to_use), id(module))

    def test_Nic_in_cache(self):
        #[Nic w cache]
        name = 'using_Nic'
        przy util.uncache(name):
            sys.modules[name] = Nic
            przy self.assertRaises(ImportError) jako cm:
                self.__import__(name)
            self.assertEqual(cm.exception.name, name)


(Frozen_UseCache,
 Source_UseCache
 ) = util.test_both(UseCache, __import__=util.__import__)


klasa ImportlibUseCache(UseCache, unittest.TestCase):

    # Pertinent only to PEP 302; exec_module() doesn't zwróć a module.

    __import__ = util.__import__['Source']

    def create_mock(self, *names, return_=Nic):
        mock = util.mock_modules(*names)
        original_load = mock.load_module
        def load_module(self, fullname):
            original_load(fullname)
            zwróć return_
        mock.load_module = MethodType(load_module, mock)
        zwróć mock

    # __import__ inconsistent between loaders oraz built-in zaimportuj when it comes
    #   to when to use the module w sys.modules oraz when nie to.
    def test_using_cache_after_loader(self):
        # [z cache on return]
        przy self.create_mock('module') jako mock:
            przy util.import_state(meta_path=[mock]):
                module = self.__import__('module')
                self.assertEqual(id(module), id(sys.modules['module']))

    # See test_using_cache_after_loader() dla reasoning.
    def test_using_cache_for_assigning_to_attribute(self):
        # [z cache to attribute]
        przy self.create_mock('pkg.__init__', 'pkg.module') jako importer:
            przy util.import_state(meta_path=[importer]):
                module = self.__import__('pkg.module')
                self.assertPrawda(hasattr(module, 'module'))
                self.assertEqual(id(module.module),
                                 id(sys.modules['pkg.module']))

    # See test_using_cache_after_loader() dla reasoning.
    def test_using_cache_for_fromlist(self):
        # [z cache dla fromlist]
        przy self.create_mock('pkg.__init__', 'pkg.module') jako importer:
            przy util.import_state(meta_path=[importer]):
                module = self.__import__('pkg', fromlist=['module'])
                self.assertPrawda(hasattr(module, 'module'))
                self.assertEqual(id(module.module),
                                 id(sys.modules['pkg.module']))


jeżeli __name__ == '__main__':
    unittest.main()
