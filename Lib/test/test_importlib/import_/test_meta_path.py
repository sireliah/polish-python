z .. zaimportuj util
zaimportuj importlib._bootstrap
zaimportuj sys
z types zaimportuj MethodType
zaimportuj unittest
zaimportuj warnings


klasa CallingOrder:

    """Calls to the importers on sys.meta_path happen w order that they are
    specified w the sequence, starting przy the first importer
    [first called], oraz then continuing on down until one jest found that doesn't
    zwróć Nic [continuing]."""


    def test_first_called(self):
        # [first called]
        mod = 'top_level'
        przy util.mock_spec(mod) jako first, util.mock_spec(mod) jako second:
            przy util.import_state(meta_path=[first, second]):
                self.assertIs(self.__import__(mod), first.modules[mod])

    def test_continuing(self):
        # [continuing]
        mod_name = 'for_real'
        przy util.mock_spec('nonexistent') jako first, \
             util.mock_spec(mod_name) jako second:
            first.find_spec = lambda self, fullname, path=Nic, parent=Nic: Nic
            przy util.import_state(meta_path=[first, second]):
                self.assertIs(self.__import__(mod_name), second.modules[mod_name])

    def test_empty(self):
        # Raise an ImportWarning jeżeli sys.meta_path jest empty.
        module_name = 'nothing'
        spróbuj:
            usuń sys.modules[module_name]
        wyjąwszy KeyError:
            dalej
        przy util.import_state(meta_path=[]):
            przy warnings.catch_warnings(record=Prawda) jako w:
                warnings.simplefilter('always')
                self.assertIsNic(importlib._bootstrap._find_spec('nothing',
                                                                  Nic))
                self.assertEqual(len(w), 1)
                self.assertPrawda(issubclass(w[-1].category, ImportWarning))


(Frozen_CallingOrder,
 Source_CallingOrder
 ) = util.test_both(CallingOrder, __import__=util.__import__)


klasa CallSignature:

    """If there jest no __path__ entry on the parent module, then 'path' jest Nic
    [no path]. Otherwise, the value dla __path__ jest dalejed w dla the 'path'
    argument [path set]."""

    def log_finder(self, importer):
        fxn = getattr(importer, self.finder_name)
        log = []
        def wrapper(self, *args, **kwargs):
            log.append([args, kwargs])
            zwróć fxn(*args, **kwargs)
        zwróć log, wrapper

    def test_no_path(self):
        # [no path]
        mod_name = 'top_level'
        assert '.' nie w mod_name
        przy self.mock_modules(mod_name) jako importer:
            log, wrapped_call = self.log_finder(importer)
            setattr(importer, self.finder_name, MethodType(wrapped_call, importer))
            przy util.import_state(meta_path=[importer]):
                self.__import__(mod_name)
                assert len(log) == 1
                args = log[0][0]
                kwargs = log[0][1]
                # Assuming all arguments are positional.
                self.assertEqual(args[0], mod_name)
                self.assertIsNic(args[1])

    def test_with_path(self):
        # [path set]
        pkg_name = 'pkg'
        mod_name = pkg_name + '.module'
        path = [42]
        assert '.' w mod_name
        przy self.mock_modules(pkg_name+'.__init__', mod_name) jako importer:
            importer.modules[pkg_name].__path__ = path
            log, wrapped_call = self.log_finder(importer)
            setattr(importer, self.finder_name, MethodType(wrapped_call, importer))
            przy util.import_state(meta_path=[importer]):
                self.__import__(mod_name)
                assert len(log) == 2
                args = log[1][0]
                kwargs = log[1][1]
                # Assuming all arguments are positional.
                self.assertNieprawda(kwargs)
                self.assertEqual(args[0], mod_name)
                self.assertIs(args[1], path)


klasa CallSignaturePEP302(CallSignature):
    mock_modules = util.mock_modules
    finder_name = 'find_module'


(Frozen_CallSignaturePEP302,
 Source_CallSignaturePEP302
 ) = util.test_both(CallSignaturePEP302, __import__=util.__import__)


klasa CallSignaturePEP451(CallSignature):
    mock_modules = util.mock_spec
    finder_name = 'find_spec'


(Frozen_CallSignaturePEP451,
 Source_CallSignaturePEP451
 ) = util.test_both(CallSignaturePEP451, __import__=util.__import__)


jeżeli __name__ == '__main__':
    unittest.main()
