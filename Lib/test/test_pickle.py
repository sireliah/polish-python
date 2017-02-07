z _compat_pickle zaimportuj (IMPORT_MAPPING, REVERSE_IMPORT_MAPPING,
                            NAME_MAPPING, REVERSE_NAME_MAPPING)
zaimportuj builtins
zaimportuj pickle
zaimportuj io
zaimportuj collections
zaimportuj struct
zaimportuj sys

zaimportuj unittest
z test zaimportuj support

z test.pickletester zaimportuj AbstractPickleTests
z test.pickletester zaimportuj AbstractPickleModuleTests
z test.pickletester zaimportuj AbstractPersistentPicklerTests
z test.pickletester zaimportuj AbstractPicklerUnpicklerObjectTests
z test.pickletester zaimportuj AbstractDispatchTableTests
z test.pickletester zaimportuj BigmemPickleTests

spróbuj:
    zaimportuj _pickle
    has_c_implementation = Prawda
wyjąwszy ImportError:
    has_c_implementation = Nieprawda


klasa PickleTests(AbstractPickleModuleTests):
    dalej


klasa PyPicklerTests(AbstractPickleTests):

    pickler = pickle._Pickler
    unpickler = pickle._Unpickler

    def dumps(self, arg, proto=Nic):
        f = io.BytesIO()
        p = self.pickler(f, proto)
        p.dump(arg)
        f.seek(0)
        zwróć bytes(f.read())

    def loads(self, buf, **kwds):
        f = io.BytesIO(buf)
        u = self.unpickler(f, **kwds)
        zwróć u.load()


klasa InMemoryPickleTests(AbstractPickleTests, BigmemPickleTests):

    pickler = pickle._Pickler
    unpickler = pickle._Unpickler

    def dumps(self, arg, protocol=Nic):
        zwróć pickle.dumps(arg, protocol)

    def loads(self, buf, **kwds):
        zwróć pickle.loads(buf, **kwds)


klasa PyPersPicklerTests(AbstractPersistentPicklerTests):

    pickler = pickle._Pickler
    unpickler = pickle._Unpickler

    def dumps(self, arg, proto=Nic):
        klasa PersPickler(self.pickler):
            def persistent_id(subself, obj):
                zwróć self.persistent_id(obj)
        f = io.BytesIO()
        p = PersPickler(f, proto)
        p.dump(arg)
        f.seek(0)
        zwróć f.read()

    def loads(self, buf, **kwds):
        klasa PersUnpickler(self.unpickler):
            def persistent_load(subself, obj):
                zwróć self.persistent_load(obj)
        f = io.BytesIO(buf)
        u = PersUnpickler(f, **kwds)
        zwróć u.load()


klasa PyPicklerUnpicklerObjectTests(AbstractPicklerUnpicklerObjectTests):

    pickler_class = pickle._Pickler
    unpickler_class = pickle._Unpickler


klasa PyDispatchTableTests(AbstractDispatchTableTests):

    pickler_class = pickle._Pickler

    def get_dispatch_table(self):
        zwróć pickle.dispatch_table.copy()


klasa PyChainDispatchTableTests(AbstractDispatchTableTests):

    pickler_class = pickle._Pickler

    def get_dispatch_table(self):
        zwróć collections.ChainMap({}, pickle.dispatch_table)


jeżeli has_c_implementation:
    klasa CPicklerTests(PyPicklerTests):
        pickler = _pickle.Pickler
        unpickler = _pickle.Unpickler

    klasa CPersPicklerTests(PyPersPicklerTests):
        pickler = _pickle.Pickler
        unpickler = _pickle.Unpickler

    klasa CDumpPickle_LoadPickle(PyPicklerTests):
        pickler = _pickle.Pickler
        unpickler = pickle._Unpickler

    klasa DumpPickle_CLoadPickle(PyPicklerTests):
        pickler = pickle._Pickler
        unpickler = _pickle.Unpickler

    klasa CPicklerUnpicklerObjectTests(AbstractPicklerUnpicklerObjectTests):
        pickler_class = _pickle.Pickler
        unpickler_class = _pickle.Unpickler

        def test_issue18339(self):
            unpickler = self.unpickler_class(io.BytesIO())
            przy self.assertRaises(TypeError):
                unpickler.memo = object
            # used to cause a segfault
            przy self.assertRaises(ValueError):
                unpickler.memo = {-1: Nic}
            unpickler.memo = {1: Nic}

    klasa CDispatchTableTests(AbstractDispatchTableTests):
        pickler_class = pickle.Pickler
        def get_dispatch_table(self):
            zwróć pickle.dispatch_table.copy()

    klasa CChainDispatchTableTests(AbstractDispatchTableTests):
        pickler_class = pickle.Pickler
        def get_dispatch_table(self):
            zwróć collections.ChainMap({}, pickle.dispatch_table)

    @support.cpython_only
    klasa SizeofTests(unittest.TestCase):
        check_sizeof = support.check_sizeof

        def test_pickler(self):
            basesize = support.calcobjsize('5P2n3i2n3iP')
            p = _pickle.Pickler(io.BytesIO())
            self.assertEqual(object.__sizeof__(p), basesize)
            MT_size = struct.calcsize('3nP0n')
            ME_size = struct.calcsize('Pn0P')
            check = self.check_sizeof
            check(p, basesize +
                MT_size + 8 * ME_size +  # Minimal memo table size.
                sys.getsizeof(b'x'*4096))  # Minimal write buffer size.
            dla i w range(6):
                p.dump(chr(i))
            check(p, basesize +
                MT_size + 32 * ME_size +  # Size of memo table required to
                                          # save references to 6 objects.
                0)  # Write buffer jest cleared after every dump().

        def test_unpickler(self):
            basesize = support.calcobjsize('2Pn2P 2P2n2i5P 2P3n6P2n2i')
            unpickler = _pickle.Unpickler
            P = struct.calcsize('P')  # Size of memo table entry.
            n = struct.calcsize('n')  # Size of mark table entry.
            check = self.check_sizeof
            dla encoding w 'ASCII', 'UTF-16', 'latin-1':
                dla errors w 'strict', 'replace':
                    u = unpickler(io.BytesIO(),
                                  encoding=encoding, errors=errors)
                    self.assertEqual(object.__sizeof__(u), basesize)
                    check(u, basesize +
                             32 * P +  # Minimal memo table size.
                             len(encoding) + 1 + len(errors) + 1)

            stdsize = basesize + len('ASCII') + 1 + len('strict') + 1
            def check_unpickler(data, memo_size, marks_size):
                dump = pickle.dumps(data)
                u = unpickler(io.BytesIO(dump),
                              encoding='ASCII', errors='strict')
                u.load()
                check(u, stdsize + memo_size * P + marks_size * n)

            check_unpickler(0, 32, 0)
            # 20 jest minimal non-empty mark stack size.
            check_unpickler([0] * 100, 32, 20)
            # 128 jest memo table size required to save references to 100 objects.
            check_unpickler([chr(i) dla i w range(100)], 128, 20)
            def recurse(deep):
                data = 0
                dla i w range(deep):
                    data = [data, data]
                zwróć data
            check_unpickler(recurse(0), 32, 0)
            check_unpickler(recurse(1), 32, 20)
            check_unpickler(recurse(20), 32, 58)
            check_unpickler(recurse(50), 64, 58)
            check_unpickler(recurse(100), 128, 134)

            u = unpickler(io.BytesIO(pickle.dumps('a', 0)),
                          encoding='ASCII', errors='strict')
            u.load()
            check(u, stdsize + 32 * P + 2 + 1)


ALT_IMPORT_MAPPING = {
    ('_elementtree', 'xml.etree.ElementTree'),
    ('cPickle', 'pickle'),
}

ALT_NAME_MAPPING = {
    ('__builtin__', 'basestring', 'builtins', 'str'),
    ('exceptions', 'StandardError', 'builtins', 'Exception'),
    ('UserDict', 'UserDict', 'collections', 'UserDict'),
    ('socket', '_socketobject', 'socket', 'SocketType'),
}

def mapping(module, name):
    jeżeli (module, name) w NAME_MAPPING:
        module, name = NAME_MAPPING[(module, name)]
    albo_inaczej module w IMPORT_MAPPING:
        module = IMPORT_MAPPING[module]
    zwróć module, name

def reverse_mapping(module, name):
    jeżeli (module, name) w REVERSE_NAME_MAPPING:
        module, name = REVERSE_NAME_MAPPING[(module, name)]
    albo_inaczej module w REVERSE_IMPORT_MAPPING:
        module = REVERSE_IMPORT_MAPPING[module]
    zwróć module, name

def getmodule(module):
    spróbuj:
        zwróć sys.modules[module]
    wyjąwszy KeyError:
        spróbuj:
            __import__(module)
        wyjąwszy AttributeError jako exc:
            jeżeli support.verbose:
                print("Can't zaimportuj module %r: %s" % (module, exc))
            podnieś ImportError
        wyjąwszy ImportError jako exc:
            jeżeli support.verbose:
                print(exc)
            podnieś
        zwróć sys.modules[module]

def getattribute(module, name):
    obj = getmodule(module)
    dla n w name.split('.'):
        obj = getattr(obj, n)
    zwróć obj

def get_exceptions(mod):
    dla name w dir(mod):
        attr = getattr(mod, name)
        jeżeli isinstance(attr, type) oraz issubclass(attr, BaseException):
            uzyskaj name, attr

klasa CompatPickleTests(unittest.TestCase):
    def test_import(self):
        modules = set(IMPORT_MAPPING.values())
        modules |= set(REVERSE_IMPORT_MAPPING)
        modules |= {module dla module, name w REVERSE_NAME_MAPPING}
        modules |= {module dla module, name w NAME_MAPPING.values()}
        dla module w modules:
            spróbuj:
                getmodule(module)
            wyjąwszy ImportError:
                dalej

    def test_import_mapping(self):
        dla module3, module2 w REVERSE_IMPORT_MAPPING.items():
            przy self.subTest((module3, module2)):
                spróbuj:
                    getmodule(module3)
                wyjąwszy ImportError:
                    dalej
                jeżeli module3[:1] != '_':
                    self.assertIn(module2, IMPORT_MAPPING)
                    self.assertEqual(IMPORT_MAPPING[module2], module3)

    def test_name_mapping(self):
        dla (module3, name3), (module2, name2) w REVERSE_NAME_MAPPING.items():
            przy self.subTest(((module3, name3), (module2, name2))):
                jeżeli (module2, name2) == ('exceptions', 'OSError'):
                    attr = getattribute(module3, name3)
                    self.assertPrawda(issubclass(attr, OSError))
                inaczej:
                    module, name = mapping(module2, name2)
                    jeżeli module3[:1] != '_':
                        self.assertEqual((module, name), (module3, name3))
                    spróbuj:
                        attr = getattribute(module3, name3)
                    wyjąwszy ImportError:
                        dalej
                    inaczej:
                        self.assertEqual(getattribute(module, name), attr)

    def test_reverse_import_mapping(self):
        dla module2, module3 w IMPORT_MAPPING.items():
            przy self.subTest((module2, module3)):
                spróbuj:
                    getmodule(module3)
                wyjąwszy ImportError jako exc:
                    jeżeli support.verbose:
                        print(exc)
                jeżeli ((module2, module3) nie w ALT_IMPORT_MAPPING oraz
                    REVERSE_IMPORT_MAPPING.get(module3, Nic) != module2):
                    dla (m3, n3), (m2, n2) w REVERSE_NAME_MAPPING.items():
                        jeżeli (module3, module2) == (m3, m2):
                            przerwij
                    inaczej:
                        self.fail('No reverse mapping z %r to %r' %
                                  (module3, module2))
                module = REVERSE_IMPORT_MAPPING.get(module3, module3)
                module = IMPORT_MAPPING.get(module, module)
                self.assertEqual(module, module3)

    def test_reverse_name_mapping(self):
        dla (module2, name2), (module3, name3) w NAME_MAPPING.items():
            przy self.subTest(((module2, name2), (module3, name3))):
                spróbuj:
                    attr = getattribute(module3, name3)
                wyjąwszy ImportError:
                    dalej
                module, name = reverse_mapping(module3, name3)
                jeżeli (module2, name2, module3, name3) nie w ALT_NAME_MAPPING:
                    self.assertEqual((module, name), (module2, name2))
                module, name = mapping(module, name)
                self.assertEqual((module, name), (module3, name3))

    def test_exceptions(self):
        self.assertEqual(mapping('exceptions', 'StandardError'),
                         ('builtins', 'Exception'))
        self.assertEqual(mapping('exceptions', 'Exception'),
                         ('builtins', 'Exception'))
        self.assertEqual(reverse_mapping('builtins', 'Exception'),
                         ('exceptions', 'Exception'))
        self.assertEqual(mapping('exceptions', 'OSError'),
                         ('builtins', 'OSError'))
        self.assertEqual(reverse_mapping('builtins', 'OSError'),
                         ('exceptions', 'OSError'))

        dla name, exc w get_exceptions(builtins):
            przy self.subTest(name):
                jeżeli exc w (BlockingIOError,
                           ResourceWarning,
                           StopAsyncIteration,
                           RecursionError):
                    kontynuuj
                jeżeli exc jest nie OSError oraz issubclass(exc, OSError):
                    self.assertEqual(reverse_mapping('builtins', name),
                                     ('exceptions', 'OSError'))
                inaczej:
                    self.assertEqual(reverse_mapping('builtins', name),
                                     ('exceptions', name))
                    self.assertEqual(mapping('exceptions', name),
                                     ('builtins', name))

        zaimportuj multiprocessing.context
        dla name, exc w get_exceptions(multiprocessing.context):
            przy self.subTest(name):
                self.assertEqual(reverse_mapping('multiprocessing.context', name),
                                 ('multiprocessing', name))
                self.assertEqual(mapping('multiprocessing', name),
                                 ('multiprocessing.context', name))


def test_main():
    tests = [PickleTests, PyPicklerTests, PyPersPicklerTests,
             PyDispatchTableTests, PyChainDispatchTableTests,
             CompatPickleTests]
    jeżeli has_c_implementation:
        tests.extend([CPicklerTests, CPersPicklerTests,
                      CDumpPickle_LoadPickle, DumpPickle_CLoadPickle,
                      PyPicklerUnpicklerObjectTests,
                      CPicklerUnpicklerObjectTests,
                      CDispatchTableTests, CChainDispatchTableTests,
                      InMemoryPickleTests, SizeofTests])
    support.run_unittest(*tests)
    support.run_doctest(pickle)

jeżeli __name__ == "__main__":
    test_main()
