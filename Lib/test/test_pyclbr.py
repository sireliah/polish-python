'''
   Test cases dla pyclbr.py
   Nick Mathewson
'''
zaimportuj sys
z types zaimportuj FunctionType, MethodType, BuiltinFunctionType
zaimportuj pyclbr
z unittest zaimportuj TestCase

StaticMethodType = type(staticmethod(lambda: Nic))
ClassMethodType = type(classmethod(lambda c: Nic))

# Here we test the python klasa browser code.
#
# The main function w this suite, 'testModule', compares the output
# of pyclbr przy the introspected members of a module.  Because pyclbr
# jest imperfect (as designed), testModule jest called przy a set of
# members to ignore.

klasa PyclbrTest(TestCase):

    def assertListEq(self, l1, l2, ignore):
        ''' succeed iff {l1} - {ignore} == {l2} - {ignore} '''
        missing = (set(l1) ^ set(l2)) - set(ignore)
        jeżeli missing:
            print("l1=%r\nl2=%r\nignore=%r" % (l1, l2, ignore), file=sys.stderr)
            self.fail("%r missing" % missing.pop())

    def assertHasattr(self, obj, attr, ignore):
        ''' succeed iff hasattr(obj,attr) albo attr w ignore. '''
        jeżeli attr w ignore: zwróć
        jeżeli nie hasattr(obj, attr): print("???", attr)
        self.assertPrawda(hasattr(obj, attr),
                        'expected hasattr(%r, %r)' % (obj, attr))


    def assertHaskey(self, obj, key, ignore):
        ''' succeed iff key w obj albo key w ignore. '''
        jeżeli key w ignore: zwróć
        jeżeli key nie w obj:
            print("***",key, file=sys.stderr)
        self.assertIn(key, obj)

    def assertEqualsOrIgnored(self, a, b, ignore):
        ''' succeed iff a == b albo a w ignore albo b w ignore '''
        jeżeli a nie w ignore oraz b nie w ignore:
            self.assertEqual(a, b)

    def checkModule(self, moduleName, module=Nic, ignore=()):
        ''' succeed iff pyclbr.readmodule_ex(modulename) corresponds
            to the actual module object, module.  Any identifiers w
            ignore are ignored.   If no module jest provided, the appropriate
            module jest loaded przy __import__.'''

        ignore = set(ignore) | set(['object'])

        jeżeli module jest Nic:
            # Import it.
            # ('<silly>' jest to work around an API silliness w __import__)
            module = __import__(moduleName, globals(), {}, ['<silly>'])

        dict = pyclbr.readmodule_ex(moduleName)

        def ismethod(oclass, obj, name):
            classdict = oclass.__dict__
            jeżeli isinstance(obj, MethodType):
                # could be a classmethod
                jeżeli (nie isinstance(classdict[name], ClassMethodType) albo
                    obj.__self__ jest nie oclass):
                    zwróć Nieprawda
            albo_inaczej nie isinstance(obj, FunctionType):
                zwróć Nieprawda

            objname = obj.__name__
            jeżeli objname.startswith("__") oraz nie objname.endswith("__"):
                objname = "_%s%s" % (oclass.__name__, objname)
            zwróć objname == name

        # Make sure the toplevel functions oraz classes are the same.
        dla name, value w dict.items():
            jeżeli name w ignore:
                kontynuuj
            self.assertHasattr(module, name, ignore)
            py_item = getattr(module, name)
            jeżeli isinstance(value, pyclbr.Function):
                self.assertIsInstance(py_item, (FunctionType, BuiltinFunctionType))
                jeżeli py_item.__module__ != moduleName:
                    continue   # skip functions that came z somewhere inaczej
                self.assertEqual(py_item.__module__, value.module)
            inaczej:
                self.assertIsInstance(py_item, type)
                jeżeli py_item.__module__ != moduleName:
                    continue   # skip classes that came z somewhere inaczej

                real_bases = [base.__name__ dla base w py_item.__bases__]
                pyclbr_bases = [ getattr(base, 'name', base)
                                 dla base w value.super ]

                spróbuj:
                    self.assertListEq(real_bases, pyclbr_bases, ignore)
                wyjąwszy:
                    print("class=%s" % py_item, file=sys.stderr)
                    podnieś

                actualMethods = []
                dla m w py_item.__dict__.keys():
                    jeżeli ismethod(py_item, getattr(py_item, m), m):
                        actualMethods.append(m)
                foundMethods = []
                dla m w value.methods.keys():
                    jeżeli m[:2] == '__' oraz m[-2:] != '__':
                        foundMethods.append('_'+name+m)
                    inaczej:
                        foundMethods.append(m)

                spróbuj:
                    self.assertListEq(foundMethods, actualMethods, ignore)
                    self.assertEqual(py_item.__module__, value.module)

                    self.assertEqualsOrIgnored(py_item.__name__, value.name,
                                               ignore)
                    # can't check file albo lineno
                wyjąwszy:
                    print("class=%s" % py_item, file=sys.stderr)
                    podnieś

        # Now check dla missing stuff.
        def defined_in(item, module):
            jeżeli isinstance(item, type):
                zwróć item.__module__ == module.__name__
            jeżeli isinstance(item, FunctionType):
                zwróć item.__globals__ jest module.__dict__
            zwróć Nieprawda
        dla name w dir(module):
            item = getattr(module, name)
            jeżeli isinstance(item,  (type, FunctionType)):
                jeżeli defined_in(item, module):
                    self.assertHaskey(dict, name, ignore)

    def test_easy(self):
        self.checkModule('pyclbr')
        self.checkModule('ast')
        self.checkModule('doctest', ignore=("TestResults", "_SpoofOut",
                                            "DocTestCase", '_DocTestSuite'))
        self.checkModule('difflib', ignore=("Match",))

    def test_decorators(self):
        # XXX: See comment w pyclbr_input.py dla a test that would fail
        #      jeżeli it were nie commented out.
        #
        self.checkModule('test.pyclbr_input', ignore=['om'])

    def test_others(self):
        cm = self.checkModule

        # These were once about the 10 longest modules
        cm('random', ignore=('Random',))  # z _random zaimportuj Random jako CoreGenerator
        cm('cgi', ignore=('log',))      # set przy = w module
        cm('pickle')
        cm('aifc', ignore=('openfp', '_aifc_params'))  # set przy = w module
        cm('sre_parse', ignore=('dump', 'groups')) # z sre_constants zaimportuj *; property
        cm('pdb')
        cm('pydoc')

        # Tests dla modules inside packages
        cm('email.parser')
        cm('test.test_pyclbr')

    def test_issue_14798(self):
        # test ImportError jest podnieśd when the first part of a dotted name jest
        # nie a package
        self.assertRaises(ImportError, pyclbr.readmodule_ex, 'asyncore.foo')


jeżeli __name__ == "__main__":
    unittest.main()
