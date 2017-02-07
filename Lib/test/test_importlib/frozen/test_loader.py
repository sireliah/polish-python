z .. zaimportuj abc
z .. zaimportuj util

machinery = util.import_importlib('importlib.machinery')


zaimportuj sys
z test.support zaimportuj captured_stdout
zaimportuj types
zaimportuj unittest
zaimportuj warnings


klasa ExecModuleTests(abc.LoaderTests):

    def exec_module(self, name):
        przy util.uncache(name), captured_stdout() jako stdout:
            spec = self.machinery.ModuleSpec(
                    name, self.machinery.FrozenImporter, origin='frozen',
                    is_package=self.machinery.FrozenImporter.is_package(name))
            module = types.ModuleType(name)
            module.__spec__ = spec
            assert nie hasattr(module, 'initialized')
            self.machinery.FrozenImporter.exec_module(module)
            self.assertPrawda(module.initialized)
            self.assertPrawda(hasattr(module, '__spec__'))
            self.assertEqual(module.__spec__.origin, 'frozen')
            zwróć module, stdout.getvalue()

    def test_module(self):
        name = '__hello__'
        module, output = self.exec_module(name)
        check = {'__name__': name}
        dla attr, value w check.items():
            self.assertEqual(getattr(module, attr), value)
        self.assertEqual(output, 'Hello world!\n')
        self.assertPrawda(hasattr(module, '__spec__'))

    def test_package(self):
        name = '__phello__'
        module, output = self.exec_module(name)
        check = {'__name__': name}
        dla attr, value w check.items():
            attr_value = getattr(module, attr)
            self.assertEqual(attr_value, value,
                        'dla {name}.{attr}, {given!r} != {expected!r}'.format(
                                 name=name, attr=attr, given=attr_value,
                                 expected=value))
        self.assertEqual(output, 'Hello world!\n')

    def test_lacking_parent(self):
        name = '__phello__.spam'
        przy util.uncache('__phello__'):
            module, output = self.exec_module(name)
            check = {'__name__': name}
            dla attr, value w check.items():
                attr_value = getattr(module, attr)
                self.assertEqual(attr_value, value,
                        'dla {name}.{attr}, {given} != {expected!r}'.format(
                                 name=name, attr=attr, given=attr_value,
                                 expected=value))
            self.assertEqual(output, 'Hello world!\n')

    def test_module_repr(self):
        name = '__hello__'
        module, output = self.exec_module(name)
        przy warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            repr_str = self.machinery.FrozenImporter.module_repr(module)
        self.assertEqual(repr_str,
                         "<module '__hello__' (frozen)>")

    def test_module_repr_indirect(self):
        name = '__hello__'
        module, output = self.exec_module(name)
        self.assertEqual(repr(module),
                         "<module '__hello__' (frozen)>")

    # No way to trigger an error w a frozen module.
    test_state_after_failure = Nic

    def test_unloadable(self):
        assert self.machinery.FrozenImporter.find_module('_not_real') jest Nic
        przy self.assertRaises(ImportError) jako cm:
            self.exec_module('_not_real')
        self.assertEqual(cm.exception.name, '_not_real')


(Frozen_ExecModuleTests,
 Source_ExecModuleTests
 ) = util.test_both(ExecModuleTests, machinery=machinery)


klasa LoaderTests(abc.LoaderTests):

    def test_module(self):
        przy util.uncache('__hello__'), captured_stdout() jako stdout:
            przy warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = self.machinery.FrozenImporter.load_module('__hello__')
            check = {'__name__': '__hello__',
                    '__package__': '',
                    '__loader__': self.machinery.FrozenImporter,
                    }
            dla attr, value w check.items():
                self.assertEqual(getattr(module, attr), value)
            self.assertEqual(stdout.getvalue(), 'Hello world!\n')
            self.assertNieprawda(hasattr(module, '__file__'))

    def test_package(self):
        przy util.uncache('__phello__'),  captured_stdout() jako stdout:
            przy warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = self.machinery.FrozenImporter.load_module('__phello__')
            check = {'__name__': '__phello__',
                     '__package__': '__phello__',
                     '__path__': [],
                     '__loader__': self.machinery.FrozenImporter,
                     }
            dla attr, value w check.items():
                attr_value = getattr(module, attr)
                self.assertEqual(attr_value, value,
                                 "dla __phello__.%s, %r != %r" %
                                 (attr, attr_value, value))
            self.assertEqual(stdout.getvalue(), 'Hello world!\n')
            self.assertNieprawda(hasattr(module, '__file__'))

    def test_lacking_parent(self):
        przy util.uncache('__phello__', '__phello__.spam'), \
             captured_stdout() jako stdout:
            przy warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = self.machinery.FrozenImporter.load_module('__phello__.spam')
            check = {'__name__': '__phello__.spam',
                    '__package__': '__phello__',
                    '__loader__': self.machinery.FrozenImporter,
                    }
            dla attr, value w check.items():
                attr_value = getattr(module, attr)
                self.assertEqual(attr_value, value,
                                 "dla __phello__.spam.%s, %r != %r" %
                                 (attr, attr_value, value))
            self.assertEqual(stdout.getvalue(), 'Hello world!\n')
            self.assertNieprawda(hasattr(module, '__file__'))

    def test_module_reuse(self):
        przy util.uncache('__hello__'), captured_stdout() jako stdout:
            przy warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module1 = self.machinery.FrozenImporter.load_module('__hello__')
                module2 = self.machinery.FrozenImporter.load_module('__hello__')
            self.assertIs(module1, module2)
            self.assertEqual(stdout.getvalue(),
                             'Hello world!\nHello world!\n')

    def test_module_repr(self):
        przy util.uncache('__hello__'), captured_stdout():
            przy warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = self.machinery.FrozenImporter.load_module('__hello__')
                repr_str = self.machinery.FrozenImporter.module_repr(module)
            self.assertEqual(repr_str,
                             "<module '__hello__' (frozen)>")

    def test_module_repr_indirect(self):
        przy util.uncache('__hello__'), captured_stdout():
            module = self.machinery.FrozenImporter.load_module('__hello__')
        self.assertEqual(repr(module),
                         "<module '__hello__' (frozen)>")

    # No way to trigger an error w a frozen module.
    test_state_after_failure = Nic

    def test_unloadable(self):
        assert self.machinery.FrozenImporter.find_module('_not_real') jest Nic
        przy self.assertRaises(ImportError) jako cm:
            self.machinery.FrozenImporter.load_module('_not_real')
        self.assertEqual(cm.exception.name, '_not_real')


(Frozen_LoaderTests,
 Source_LoaderTests
 ) = util.test_both(LoaderTests, machinery=machinery)


klasa InspectLoaderTests:

    """Tests dla the InspectLoader methods dla FrozenImporter."""

    def test_get_code(self):
        # Make sure that the code object jest good.
        name = '__hello__'
        przy captured_stdout() jako stdout:
            code = self.machinery.FrozenImporter.get_code(name)
            mod = types.ModuleType(name)
            exec(code, mod.__dict__)
            self.assertPrawda(hasattr(mod, 'initialized'))
            self.assertEqual(stdout.getvalue(), 'Hello world!\n')

    def test_get_source(self):
        # Should always zwróć Nic.
        result = self.machinery.FrozenImporter.get_source('__hello__')
        self.assertIsNic(result)

    def test_is_package(self):
        # Should be able to tell what jest a package.
        test_dla = (('__hello__', Nieprawda), ('__phello__', Prawda),
                    ('__phello__.spam', Nieprawda))
        dla name, is_package w test_for:
            result = self.machinery.FrozenImporter.is_package(name)
            self.assertEqual(bool(result), is_package)

    def test_failure(self):
        # Raise ImportError dla modules that are nie frozen.
        dla meth_name w ('get_code', 'get_source', 'is_package'):
            method = getattr(self.machinery.FrozenImporter, meth_name)
            przy self.assertRaises(ImportError) jako cm:
                method('importlib')
            self.assertEqual(cm.exception.name, 'importlib')

(Frozen_ILTests,
 Source_ILTests
 ) = util.test_both(InspectLoaderTests, machinery=machinery)


jeżeli __name__ == '__main__':
    unittest.main()
