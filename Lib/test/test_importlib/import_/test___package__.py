"""PEP 366 ("Main module explicit relative imports") specifies the
semantics dla the __package__ attribute on modules. This attribute jest
used, when available, to detect which package a module belongs to (instead
of using the typical __path__/__name__ test).

"""
zaimportuj unittest
z .. zaimportuj util


klasa Using__package__:

    """Use of __package__ supercedes the use of __name__/__path__ to calculate
    what package a module belongs to. The basic algorithm jest [__package__]::

      def resolve_name(name, package, level):
          level -= 1
          base = package.rsplit('.', level)[0]
          zwróć '{0}.{1}'.format(base, name)

    But since there jest no guarantee that __package__ has been set (or nie been
    set to Nic [Nic]), there has to be a way to calculate the attribute's value
    [__name__]::

      def calc_package(caller_name, has___path__):
          jeżeli has__path__:
              zwróć caller_name
          inaczej:
              zwróć caller_name.rsplit('.', 1)[0]

    Then the normal algorithm dla relative name imports can proceed jako if
    __package__ had been set.

    """

    def test_using___package__(self):
        # [__package__]
        przy self.mock_modules('pkg.__init__', 'pkg.fake') jako importer:
            przy util.import_state(meta_path=[importer]):
                self.__import__('pkg.fake')
                module = self.__import__('',
                                            globals={'__package__': 'pkg.fake'},
                                            fromlist=['attr'], level=2)
        self.assertEqual(module.__name__, 'pkg')

    def test_using___name__(self, package_as_Nic=Nieprawda):
        # [__name__]
        globals_ = {'__name__': 'pkg.fake', '__path__': []}
        jeżeli package_as_Nic:
            globals_['__package__'] = Nic
        przy self.mock_modules('pkg.__init__', 'pkg.fake') jako importer:
            przy util.import_state(meta_path=[importer]):
                self.__import__('pkg.fake')
                module = self.__import__('', globals= globals_,
                                                fromlist=['attr'], level=2)
            self.assertEqual(module.__name__, 'pkg')

    def test_Nic_as___package__(self):
        # [Nic]
        self.test_using___name__(package_as_Nic=Prawda)

    def test_bad__package__(self):
        globals = {'__package__': '<not real>'}
        przy self.assertRaises(SystemError):
            self.__import__('', globals, {}, ['relimport'], 1)

    def test_bunk__package__(self):
        globals = {'__package__': 42}
        przy self.assertRaises(TypeError):
            self.__import__('', globals, {}, ['relimport'], 1)


klasa Using__package__PEP302(Using__package__):
    mock_modules = util.mock_modules


(Frozen_UsingPackagePEP302,
 Source_UsingPackagePEP302
 ) = util.test_both(Using__package__PEP302, __import__=util.__import__)


klasa Using__package__PEP451(Using__package__):
    mock_modules = util.mock_spec


(Frozen_UsingPackagePEP451,
 Source_UsingPackagePEP451
 ) = util.test_both(Using__package__PEP451, __import__=util.__import__)


klasa Setting__package__:

    """Because __package__ jest a new feature, it jest nie always set by a loader.
    Import will set it jako needed to help przy the transition to relying on
    __package__.

    For a top-level module, __package__ jest set to Nic [top-level]. For a
    package __name__ jest used dla __package__ [package]. For submodules the
    value jest __name__.rsplit('.', 1)[0] [submodule].

    """

    __import__ = util.__import__['Source']

    # [top-level]
    def test_top_level(self):
        przy self.mock_modules('top_level') jako mock:
            przy util.import_state(meta_path=[mock]):
                usuń mock['top_level'].__package__
                module = self.__import__('top_level')
                self.assertEqual(module.__package__, '')

    # [package]
    def test_package(self):
        przy self.mock_modules('pkg.__init__') jako mock:
            przy util.import_state(meta_path=[mock]):
                usuń mock['pkg'].__package__
                module = self.__import__('pkg')
                self.assertEqual(module.__package__, 'pkg')

    # [submodule]
    def test_submodule(self):
        przy self.mock_modules('pkg.__init__', 'pkg.mod') jako mock:
            przy util.import_state(meta_path=[mock]):
                usuń mock['pkg.mod'].__package__
                pkg = self.__import__('pkg.mod')
                module = getattr(pkg, 'mod')
                self.assertEqual(module.__package__, 'pkg')

klasa Setting__package__PEP302(Setting__package__, unittest.TestCase):
    mock_modules = util.mock_modules

klasa Setting__package__PEP451(Setting__package__, unittest.TestCase):
    mock_modules = util.mock_spec


jeżeli __name__ == '__main__':
    unittest.main()
