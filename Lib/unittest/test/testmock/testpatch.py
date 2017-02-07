# Copyright (C) 2007-2012 Michael Foord & the mock team
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

zaimportuj os
zaimportuj sys

zaimportuj unittest
z unittest.test.testmock zaimportuj support
z unittest.test.testmock.support zaimportuj SomeClass, is_instance

z unittest.mock zaimportuj (
    NonCallableMock, CallableMixin, patch, sentinel,
    MagicMock, Mock, NonCallableMagicMock, patch, _patch,
    DEFAULT, call, _get_target, _patch
)


builtin_string = 'builtins'

PTModule = sys.modules[__name__]
MODNAME = '%s.PTModule' % __name__


def _get_proxy(obj, get_only=Prawda):
    klasa Proxy(object):
        def __getattr__(self, name):
            zwróć getattr(obj, name)
    jeżeli nie get_only:
        def __setattr__(self, name, value):
            setattr(obj, name, value)
        def __delattr__(self, name):
            delattr(obj, name)
        Proxy.__setattr__ = __setattr__
        Proxy.__delattr__ = __delattr__
    zwróć Proxy()


# dla use w the test
something  = sentinel.Something
something_inaczej  = sentinel.SomethingElse


klasa Foo(object):
    def __init__(self, a):
        dalej
    def f(self, a):
        dalej
    def g(self):
        dalej
    foo = 'bar'

    klasa Bar(object):
        def a(self):
            dalej

foo_name = '%s.Foo' % __name__


def function(a, b=Foo):
    dalej


klasa Container(object):
    def __init__(self):
        self.values = {}

    def __getitem__(self, name):
        zwróć self.values[name]

    def __setitem__(self, name, value):
        self.values[name] = value

    def __delitem__(self, name):
        usuń self.values[name]

    def __iter__(self):
        zwróć iter(self.values)



klasa PatchTest(unittest.TestCase):

    def assertNotCallable(self, obj, magic=Prawda):
        MockClass = NonCallableMagicMock
        jeżeli nie magic:
            MockClass = NonCallableMock

        self.assertRaises(TypeError, obj)
        self.assertPrawda(is_instance(obj, MockClass))
        self.assertNieprawda(is_instance(obj, CallableMixin))


    def test_single_patchobject(self):
        klasa Something(object):
            attribute = sentinel.Original

        @patch.object(Something, 'attribute', sentinel.Patched)
        def test():
            self.assertEqual(Something.attribute, sentinel.Patched, "unpatched")

        test()
        self.assertEqual(Something.attribute, sentinel.Original,
                         "patch nie restored")


    def test_patchobject_with_none(self):
        klasa Something(object):
            attribute = sentinel.Original

        @patch.object(Something, 'attribute', Nic)
        def test():
            self.assertIsNic(Something.attribute, "unpatched")

        test()
        self.assertEqual(Something.attribute, sentinel.Original,
                         "patch nie restored")


    def test_multiple_patchobject(self):
        klasa Something(object):
            attribute = sentinel.Original
            next_attribute = sentinel.Original2

        @patch.object(Something, 'attribute', sentinel.Patched)
        @patch.object(Something, 'next_attribute', sentinel.Patched2)
        def test():
            self.assertEqual(Something.attribute, sentinel.Patched,
                             "unpatched")
            self.assertEqual(Something.next_attribute, sentinel.Patched2,
                             "unpatched")

        test()
        self.assertEqual(Something.attribute, sentinel.Original,
                         "patch nie restored")
        self.assertEqual(Something.next_attribute, sentinel.Original2,
                         "patch nie restored")


    def test_object_lookup_is_quite_lazy(self):
        global something
        original = something
        @patch('%s.something' % __name__, sentinel.Something2)
        def test():
            dalej

        spróbuj:
            something = sentinel.replacement_value
            test()
            self.assertEqual(something, sentinel.replacement_value)
        w_końcu:
            something = original


    def test_patch(self):
        @patch('%s.something' % __name__, sentinel.Something2)
        def test():
            self.assertEqual(PTModule.something, sentinel.Something2,
                             "unpatched")

        test()
        self.assertEqual(PTModule.something, sentinel.Something,
                         "patch nie restored")

        @patch('%s.something' % __name__, sentinel.Something2)
        @patch('%s.something_inaczej' % __name__, sentinel.SomethingElse)
        def test():
            self.assertEqual(PTModule.something, sentinel.Something2,
                             "unpatched")
            self.assertEqual(PTModule.something_inaczej, sentinel.SomethingElse,
                             "unpatched")

        self.assertEqual(PTModule.something, sentinel.Something,
                         "patch nie restored")
        self.assertEqual(PTModule.something_inaczej, sentinel.SomethingElse,
                         "patch nie restored")

        # Test the patching oraz restoring works a second time
        test()

        self.assertEqual(PTModule.something, sentinel.Something,
                         "patch nie restored")
        self.assertEqual(PTModule.something_inaczej, sentinel.SomethingElse,
                         "patch nie restored")

        mock = Mock()
        mock.return_value = sentinel.Handle
        @patch('%s.open' % builtin_string, mock)
        def test():
            self.assertEqual(open('filename', 'r'), sentinel.Handle,
                             "open nie patched")
        test()
        test()

        self.assertNotEqual(open, mock, "patch nie restored")


    def test_patch_class_attribute(self):
        @patch('%s.SomeClass.class_attribute' % __name__,
               sentinel.ClassAttribute)
        def test():
            self.assertEqual(PTModule.SomeClass.class_attribute,
                             sentinel.ClassAttribute, "unpatched")
        test()

        self.assertIsNic(PTModule.SomeClass.class_attribute,
                          "patch nie restored")


    def test_patchobject_with_default_mock(self):
        klasa Test(object):
            something = sentinel.Original
            something2 = sentinel.Original2

        @patch.object(Test, 'something')
        def test(mock):
            self.assertEqual(mock, Test.something,
                             "Mock nie dalejed into test function")
            self.assertIsInstance(mock, MagicMock,
                            "patch przy two arguments did nie create a mock")

        test()

        @patch.object(Test, 'something')
        @patch.object(Test, 'something2')
        def test(this1, this2, mock1, mock2):
            self.assertEqual(this1, sentinel.this1,
                             "Patched function didn't receive initial argument")
            self.assertEqual(this2, sentinel.this2,
                             "Patched function didn't receive second argument")
            self.assertEqual(mock1, Test.something2,
                             "Mock nie dalejed into test function")
            self.assertEqual(mock2, Test.something,
                             "Second Mock nie dalejed into test function")
            self.assertIsInstance(mock2, MagicMock,
                            "patch przy two arguments did nie create a mock")
            self.assertIsInstance(mock2, MagicMock,
                            "patch przy two arguments did nie create a mock")

            # A hack to test that new mocks are dalejed the second time
            self.assertNotEqual(outerMock1, mock1, "unexpected value dla mock1")
            self.assertNotEqual(outerMock2, mock2, "unexpected value dla mock1")
            zwróć mock1, mock2

        outerMock1 = outerMock2 = Nic
        outerMock1, outerMock2 = test(sentinel.this1, sentinel.this2)

        # Test that executing a second time creates new mocks
        test(sentinel.this1, sentinel.this2)


    def test_patch_with_spec(self):
        @patch('%s.SomeClass' % __name__, spec=SomeClass)
        def test(MockSomeClass):
            self.assertEqual(SomeClass, MockSomeClass)
            self.assertPrawda(is_instance(SomeClass.wibble, MagicMock))
            self.assertRaises(AttributeError, lambda: SomeClass.not_wibble)

        test()


    def test_patchobject_with_spec(self):
        @patch.object(SomeClass, 'class_attribute', spec=SomeClass)
        def test(MockAttribute):
            self.assertEqual(SomeClass.class_attribute, MockAttribute)
            self.assertPrawda(is_instance(SomeClass.class_attribute.wibble,
                                       MagicMock))
            self.assertRaises(AttributeError,
                              lambda: SomeClass.class_attribute.not_wibble)

        test()


    def test_patch_with_spec_as_list(self):
        @patch('%s.SomeClass' % __name__, spec=['wibble'])
        def test(MockSomeClass):
            self.assertEqual(SomeClass, MockSomeClass)
            self.assertPrawda(is_instance(SomeClass.wibble, MagicMock))
            self.assertRaises(AttributeError, lambda: SomeClass.not_wibble)

        test()


    def test_patchobject_with_spec_as_list(self):
        @patch.object(SomeClass, 'class_attribute', spec=['wibble'])
        def test(MockAttribute):
            self.assertEqual(SomeClass.class_attribute, MockAttribute)
            self.assertPrawda(is_instance(SomeClass.class_attribute.wibble,
                                       MagicMock))
            self.assertRaises(AttributeError,
                              lambda: SomeClass.class_attribute.not_wibble)

        test()


    def test_nested_patch_with_spec_as_list(self):
        # regression test dla nested decorators
        @patch('%s.open' % builtin_string)
        @patch('%s.SomeClass' % __name__, spec=['wibble'])
        def test(MockSomeClass, MockOpen):
            self.assertEqual(SomeClass, MockSomeClass)
            self.assertPrawda(is_instance(SomeClass.wibble, MagicMock))
            self.assertRaises(AttributeError, lambda: SomeClass.not_wibble)
        test()


    def test_patch_with_spec_as_boolean(self):
        @patch('%s.SomeClass' % __name__, spec=Prawda)
        def test(MockSomeClass):
            self.assertEqual(SomeClass, MockSomeClass)
            # Should nie podnieś attribute error
            MockSomeClass.wibble

            self.assertRaises(AttributeError, lambda: MockSomeClass.not_wibble)

        test()


    def test_patch_object_with_spec_as_boolean(self):
        @patch.object(PTModule, 'SomeClass', spec=Prawda)
        def test(MockSomeClass):
            self.assertEqual(SomeClass, MockSomeClass)
            # Should nie podnieś attribute error
            MockSomeClass.wibble

            self.assertRaises(AttributeError, lambda: MockSomeClass.not_wibble)

        test()


    def test_patch_class_acts_with_spec_is_inherited(self):
        @patch('%s.SomeClass' % __name__, spec=Prawda)
        def test(MockSomeClass):
            self.assertPrawda(is_instance(MockSomeClass, MagicMock))
            instance = MockSomeClass()
            self.assertNotCallable(instance)
            # Should nie podnieś attribute error
            instance.wibble

            self.assertRaises(AttributeError, lambda: instance.not_wibble)

        test()


    def test_patch_with_create_mocks_non_existent_attributes(self):
        @patch('%s.frooble' % builtin_string, sentinel.Frooble, create=Prawda)
        def test():
            self.assertEqual(frooble, sentinel.Frooble)

        test()
        self.assertRaises(NameError, lambda: frooble)


    def test_patchobject_with_create_mocks_non_existent_attributes(self):
        @patch.object(SomeClass, 'frooble', sentinel.Frooble, create=Prawda)
        def test():
            self.assertEqual(SomeClass.frooble, sentinel.Frooble)

        test()
        self.assertNieprawda(hasattr(SomeClass, 'frooble'))


    def test_patch_wont_create_by_default(self):
        spróbuj:
            @patch('%s.frooble' % builtin_string, sentinel.Frooble)
            def test():
                self.assertEqual(frooble, sentinel.Frooble)

            test()
        wyjąwszy AttributeError:
            dalej
        inaczej:
            self.fail('Patching non existent attributes should fail')

        self.assertRaises(NameError, lambda: frooble)


    def test_patchobject_wont_create_by_default(self):
        spróbuj:
            @patch.object(SomeClass, 'ord', sentinel.Frooble)
            def test():
                self.fail('Patching non existent attributes should fail')

            test()
        wyjąwszy AttributeError:
            dalej
        inaczej:
            self.fail('Patching non existent attributes should fail')
        self.assertNieprawda(hasattr(SomeClass, 'ord'))


    def test_patch_builtins_without_create(self):
        @patch(__name__+'.ord')
        def test_ord(mock_ord):
            mock_ord.return_value = 101
            zwróć ord('c')

        @patch(__name__+'.open')
        def test_open(mock_open):
            m = mock_open.return_value
            m.read.return_value = 'abcd'

            fobj = open('doesnotexists.txt')
            data = fobj.read()
            fobj.close()
            zwróć data

        self.assertEqual(test_ord(), 101)
        self.assertEqual(test_open(), 'abcd')


    def test_patch_with_static_methods(self):
        klasa Foo(object):
            @staticmethod
            def woot():
                zwróć sentinel.Static

        @patch.object(Foo, 'woot', staticmethod(lambda: sentinel.Patched))
        def anonymous():
            self.assertEqual(Foo.woot(), sentinel.Patched)
        anonymous()

        self.assertEqual(Foo.woot(), sentinel.Static)


    def test_patch_local(self):
        foo = sentinel.Foo
        @patch.object(sentinel, 'Foo', 'Foo')
        def anonymous():
            self.assertEqual(sentinel.Foo, 'Foo')
        anonymous()

        self.assertEqual(sentinel.Foo, foo)


    def test_patch_slots(self):
        klasa Foo(object):
            __slots__ = ('Foo',)

        foo = Foo()
        foo.Foo = sentinel.Foo

        @patch.object(foo, 'Foo', 'Foo')
        def anonymous():
            self.assertEqual(foo.Foo, 'Foo')
        anonymous()

        self.assertEqual(foo.Foo, sentinel.Foo)


    def test_patchobject_class_decorator(self):
        klasa Something(object):
            attribute = sentinel.Original

        klasa Foo(object):
            def test_method(other_self):
                self.assertEqual(Something.attribute, sentinel.Patched,
                                 "unpatched")
            def not_test_method(other_self):
                self.assertEqual(Something.attribute, sentinel.Original,
                                 "non-test method patched")

        Foo = patch.object(Something, 'attribute', sentinel.Patched)(Foo)

        f = Foo()
        f.test_method()
        f.not_test_method()

        self.assertEqual(Something.attribute, sentinel.Original,
                         "patch nie restored")


    def test_patch_class_decorator(self):
        klasa Something(object):
            attribute = sentinel.Original

        klasa Foo(object):
            def test_method(other_self, mock_something):
                self.assertEqual(PTModule.something, mock_something,
                                 "unpatched")
            def not_test_method(other_self):
                self.assertEqual(PTModule.something, sentinel.Something,
                                 "non-test method patched")
        Foo = patch('%s.something' % __name__)(Foo)

        f = Foo()
        f.test_method()
        f.not_test_method()

        self.assertEqual(Something.attribute, sentinel.Original,
                         "patch nie restored")
        self.assertEqual(PTModule.something, sentinel.Something,
                         "patch nie restored")


    def test_patchobject_twice(self):
        klasa Something(object):
            attribute = sentinel.Original
            next_attribute = sentinel.Original2

        @patch.object(Something, 'attribute', sentinel.Patched)
        @patch.object(Something, 'attribute', sentinel.Patched)
        def test():
            self.assertEqual(Something.attribute, sentinel.Patched, "unpatched")

        test()

        self.assertEqual(Something.attribute, sentinel.Original,
                         "patch nie restored")


    def test_patch_dict(self):
        foo = {'initial': object(), 'other': 'something'}
        original = foo.copy()

        @patch.dict(foo)
        def test():
            foo['a'] = 3
            usuń foo['initial']
            foo['other'] = 'something inaczej'

        test()

        self.assertEqual(foo, original)

        @patch.dict(foo, {'a': 'b'})
        def test():
            self.assertEqual(len(foo), 3)
            self.assertEqual(foo['a'], 'b')

        test()

        self.assertEqual(foo, original)

        @patch.dict(foo, [('a', 'b')])
        def test():
            self.assertEqual(len(foo), 3)
            self.assertEqual(foo['a'], 'b')

        test()

        self.assertEqual(foo, original)


    def test_patch_dict_with_container_object(self):
        foo = Container()
        foo['initial'] = object()
        foo['other'] =  'something'

        original = foo.values.copy()

        @patch.dict(foo)
        def test():
            foo['a'] = 3
            usuń foo['initial']
            foo['other'] = 'something inaczej'

        test()

        self.assertEqual(foo.values, original)

        @patch.dict(foo, {'a': 'b'})
        def test():
            self.assertEqual(len(foo.values), 3)
            self.assertEqual(foo['a'], 'b')

        test()

        self.assertEqual(foo.values, original)


    def test_patch_dict_with_clear(self):
        foo = {'initial': object(), 'other': 'something'}
        original = foo.copy()

        @patch.dict(foo, clear=Prawda)
        def test():
            self.assertEqual(foo, {})
            foo['a'] = 3
            foo['other'] = 'something inaczej'

        test()

        self.assertEqual(foo, original)

        @patch.dict(foo, {'a': 'b'}, clear=Prawda)
        def test():
            self.assertEqual(foo, {'a': 'b'})

        test()

        self.assertEqual(foo, original)

        @patch.dict(foo, [('a', 'b')], clear=Prawda)
        def test():
            self.assertEqual(foo, {'a': 'b'})

        test()

        self.assertEqual(foo, original)


    def test_patch_dict_with_container_object_and_clear(self):
        foo = Container()
        foo['initial'] = object()
        foo['other'] =  'something'

        original = foo.values.copy()

        @patch.dict(foo, clear=Prawda)
        def test():
            self.assertEqual(foo.values, {})
            foo['a'] = 3
            foo['other'] = 'something inaczej'

        test()

        self.assertEqual(foo.values, original)

        @patch.dict(foo, {'a': 'b'}, clear=Prawda)
        def test():
            self.assertEqual(foo.values, {'a': 'b'})

        test()

        self.assertEqual(foo.values, original)


    def test_name_preserved(self):
        foo = {}

        @patch('%s.SomeClass' % __name__, object())
        @patch('%s.SomeClass' % __name__, object(), autospec=Prawda)
        @patch.object(SomeClass, object())
        @patch.dict(foo)
        def some_name():
            dalej

        self.assertEqual(some_name.__name__, 'some_name')


    def test_patch_with_exception(self):
        foo = {}

        @patch.dict(foo, {'a': 'b'})
        def test():
            podnieś NameError('Konrad')
        spróbuj:
            test()
        wyjąwszy NameError:
            dalej
        inaczej:
            self.fail('NameError nie podnieśd by test')

        self.assertEqual(foo, {})


    def test_patch_dict_with_string(self):
        @patch.dict('os.environ', {'konrad_delong': 'some value'})
        def test():
            self.assertIn('konrad_delong', os.environ)

        test()


    def test_patch_descriptor(self):
        # would be some effort to fix this - we could special case the
        # builtin descriptors: classmethod, property, staticmethod
        zwróć
        klasa Nothing(object):
            foo = Nic

        klasa Something(object):
            foo = {}

            @patch.object(Nothing, 'foo', 2)
            @classmethod
            def klass(cls):
                self.assertIs(cls, Something)

            @patch.object(Nothing, 'foo', 2)
            @staticmethod
            def static(arg):
                zwróć arg

            @patch.dict(foo)
            @classmethod
            def klass_dict(cls):
                self.assertIs(cls, Something)

            @patch.dict(foo)
            @staticmethod
            def static_dict(arg):
                zwróć arg

        # these will podnieś exceptions jeżeli patching descriptors jest broken
        self.assertEqual(Something.static('f00'), 'f00')
        Something.klass()
        self.assertEqual(Something.static_dict('f00'), 'f00')
        Something.klass_dict()

        something = Something()
        self.assertEqual(something.static('f00'), 'f00')
        something.klass()
        self.assertEqual(something.static_dict('f00'), 'f00')
        something.klass_dict()


    def test_patch_spec_set(self):
        @patch('%s.SomeClass' % __name__, spec=SomeClass, spec_set=Prawda)
        def test(MockClass):
            MockClass.z = 'foo'

        self.assertRaises(AttributeError, test)

        @patch.object(support, 'SomeClass', spec=SomeClass, spec_set=Prawda)
        def test(MockClass):
            MockClass.z = 'foo'

        self.assertRaises(AttributeError, test)
        @patch('%s.SomeClass' % __name__, spec_set=Prawda)
        def test(MockClass):
            MockClass.z = 'foo'

        self.assertRaises(AttributeError, test)

        @patch.object(support, 'SomeClass', spec_set=Prawda)
        def test(MockClass):
            MockClass.z = 'foo'

        self.assertRaises(AttributeError, test)


    def test_spec_set_inherit(self):
        @patch('%s.SomeClass' % __name__, spec_set=Prawda)
        def test(MockClass):
            instance = MockClass()
            instance.z = 'foo'

        self.assertRaises(AttributeError, test)


    def test_patch_start_stop(self):
        original = something
        patcher = patch('%s.something' % __name__)
        self.assertIs(something, original)
        mock = patcher.start()
        spróbuj:
            self.assertIsNot(mock, original)
            self.assertIs(something, mock)
        w_końcu:
            patcher.stop()
        self.assertIs(something, original)


    def test_stop_without_start(self):
        patcher = patch(foo_name, 'bar', 3)

        # calling stop without start used to produce a very obscure error
        self.assertRaises(RuntimeError, patcher.stop)


    def test_patchobject_start_stop(self):
        original = something
        patcher = patch.object(PTModule, 'something', 'foo')
        self.assertIs(something, original)
        replaced = patcher.start()
        spróbuj:
            self.assertEqual(replaced, 'foo')
            self.assertIs(something, replaced)
        w_końcu:
            patcher.stop()
        self.assertIs(something, original)


    def test_patch_dict_start_stop(self):
        d = {'foo': 'bar'}
        original = d.copy()
        patcher = patch.dict(d, [('spam', 'eggs')], clear=Prawda)
        self.assertEqual(d, original)

        patcher.start()
        spróbuj:
            self.assertEqual(d, {'spam': 'eggs'})
        w_końcu:
            patcher.stop()
        self.assertEqual(d, original)


    def test_patch_dict_class_decorator(self):
        this = self
        d = {'spam': 'eggs'}
        original = d.copy()

        klasa Test(object):
            def test_first(self):
                this.assertEqual(d, {'foo': 'bar'})
            def test_second(self):
                this.assertEqual(d, {'foo': 'bar'})

        Test = patch.dict(d, {'foo': 'bar'}, clear=Prawda)(Test)
        self.assertEqual(d, original)

        test = Test()

        test.test_first()
        self.assertEqual(d, original)

        test.test_second()
        self.assertEqual(d, original)

        test = Test()

        test.test_first()
        self.assertEqual(d, original)

        test.test_second()
        self.assertEqual(d, original)


    def test_get_only_proxy(self):
        klasa Something(object):
            foo = 'foo'
        klasa SomethingElse:
            foo = 'foo'

        dla thing w Something, SomethingElse, Something(), SomethingElse:
            proxy = _get_proxy(thing)

            @patch.object(proxy, 'foo', 'bar')
            def test():
                self.assertEqual(proxy.foo, 'bar')
            test()
            self.assertEqual(proxy.foo, 'foo')
            self.assertEqual(thing.foo, 'foo')
            self.assertNotIn('foo', proxy.__dict__)


    def test_get_set_delete_proxy(self):
        klasa Something(object):
            foo = 'foo'
        klasa SomethingElse:
            foo = 'foo'

        dla thing w Something, SomethingElse, Something(), SomethingElse:
            proxy = _get_proxy(Something, get_only=Nieprawda)

            @patch.object(proxy, 'foo', 'bar')
            def test():
                self.assertEqual(proxy.foo, 'bar')
            test()
            self.assertEqual(proxy.foo, 'foo')
            self.assertEqual(thing.foo, 'foo')
            self.assertNotIn('foo', proxy.__dict__)


    def test_patch_keyword_args(self):
        kwargs = {'side_effect': KeyError, 'foo.bar.return_value': 33,
                  'foo': MagicMock()}

        patcher = patch(foo_name, **kwargs)
        mock = patcher.start()
        patcher.stop()

        self.assertRaises(KeyError, mock)
        self.assertEqual(mock.foo.bar(), 33)
        self.assertIsInstance(mock.foo, MagicMock)


    def test_patch_object_keyword_args(self):
        kwargs = {'side_effect': KeyError, 'foo.bar.return_value': 33,
                  'foo': MagicMock()}

        patcher = patch.object(Foo, 'f', **kwargs)
        mock = patcher.start()
        patcher.stop()

        self.assertRaises(KeyError, mock)
        self.assertEqual(mock.foo.bar(), 33)
        self.assertIsInstance(mock.foo, MagicMock)


    def test_patch_dict_keyword_args(self):
        original = {'foo': 'bar'}
        copy = original.copy()

        patcher = patch.dict(original, foo=3, bar=4, baz=5)
        patcher.start()

        spróbuj:
            self.assertEqual(original, dict(foo=3, bar=4, baz=5))
        w_końcu:
            patcher.stop()

        self.assertEqual(original, copy)


    def test_autospec(self):
        klasa Boo(object):
            def __init__(self, a):
                dalej
            def f(self, a):
                dalej
            def g(self):
                dalej
            foo = 'bar'

            klasa Bar(object):
                def a(self):
                    dalej

        def _test(mock):
            mock(1)
            mock.assert_called_with(1)
            self.assertRaises(TypeError, mock)

        def _test2(mock):
            mock.f(1)
            mock.f.assert_called_with(1)
            self.assertRaises(TypeError, mock.f)

            mock.g()
            mock.g.assert_called_with()
            self.assertRaises(TypeError, mock.g, 1)

            self.assertRaises(AttributeError, getattr, mock, 'h')

            mock.foo.lower()
            mock.foo.lower.assert_called_with()
            self.assertRaises(AttributeError, getattr, mock.foo, 'bar')

            mock.Bar()
            mock.Bar.assert_called_with()

            mock.Bar.a()
            mock.Bar.a.assert_called_with()
            self.assertRaises(TypeError, mock.Bar.a, 1)

            mock.Bar().a()
            mock.Bar().a.assert_called_with()
            self.assertRaises(TypeError, mock.Bar().a, 1)

            self.assertRaises(AttributeError, getattr, mock.Bar, 'b')
            self.assertRaises(AttributeError, getattr, mock.Bar(), 'b')

        def function(mock):
            _test(mock)
            _test2(mock)
            _test2(mock(1))
            self.assertIs(mock, Foo)
            zwróć mock

        test = patch(foo_name, autospec=Prawda)(function)

        mock = test()
        self.assertIsNot(Foo, mock)
        # test patching a second time works
        test()

        module = sys.modules[__name__]
        test = patch.object(module, 'Foo', autospec=Prawda)(function)

        mock = test()
        self.assertIsNot(Foo, mock)
        # test patching a second time works
        test()


    def test_autospec_function(self):
        @patch('%s.function' % __name__, autospec=Prawda)
        def test(mock):
            function(1)
            function.assert_called_with(1)
            function(2, 3)
            function.assert_called_with(2, 3)

            self.assertRaises(TypeError, function)
            self.assertRaises(AttributeError, getattr, function, 'foo')

        test()


    def test_autospec_keywords(self):
        @patch('%s.function' % __name__, autospec=Prawda,
               return_value=3)
        def test(mock_function):
            #self.assertEqual(function.abc, 'foo')
            zwróć function(1, 2)

        result = test()
        self.assertEqual(result, 3)


    def test_autospec_with_new(self):
        patcher = patch('%s.function' % __name__, new=3, autospec=Prawda)
        self.assertRaises(TypeError, patcher.start)

        module = sys.modules[__name__]
        patcher = patch.object(module, 'function', new=3, autospec=Prawda)
        self.assertRaises(TypeError, patcher.start)


    def test_autospec_with_object(self):
        klasa Bar(Foo):
            extra = []

        patcher = patch(foo_name, autospec=Bar)
        mock = patcher.start()
        spróbuj:
            self.assertIsInstance(mock, Bar)
            self.assertIsInstance(mock.extra, list)
        w_końcu:
            patcher.stop()


    def test_autospec_inherits(self):
        FooClass = Foo
        patcher = patch(foo_name, autospec=Prawda)
        mock = patcher.start()
        spróbuj:
            self.assertIsInstance(mock, FooClass)
            self.assertIsInstance(mock(3), FooClass)
        w_końcu:
            patcher.stop()


    def test_autospec_name(self):
        patcher = patch(foo_name, autospec=Prawda)
        mock = patcher.start()

        spróbuj:
            self.assertIn(" name='Foo'", repr(mock))
            self.assertIn(" name='Foo.f'", repr(mock.f))
            self.assertIn(" name='Foo()'", repr(mock(Nic)))
            self.assertIn(" name='Foo().f'", repr(mock(Nic).f))
        w_końcu:
            patcher.stop()


    def test_tracebacks(self):
        @patch.object(Foo, 'f', object())
        def test():
            podnieś AssertionError
        spróbuj:
            test()
        wyjąwszy:
            err = sys.exc_info()

        result = unittest.TextTestResult(Nic, Nic, 0)
        traceback = result._exc_info_to_string(err, self)
        self.assertIn('raise AssertionError', traceback)


    def test_new_callable_patch(self):
        patcher = patch(foo_name, new_callable=NonCallableMagicMock)

        m1 = patcher.start()
        patcher.stop()
        m2 = patcher.start()
        patcher.stop()

        self.assertIsNot(m1, m2)
        dla mock w m1, m2:
            self.assertNotCallable(m1)


    def test_new_callable_patch_object(self):
        patcher = patch.object(Foo, 'f', new_callable=NonCallableMagicMock)

        m1 = patcher.start()
        patcher.stop()
        m2 = patcher.start()
        patcher.stop()

        self.assertIsNot(m1, m2)
        dla mock w m1, m2:
            self.assertNotCallable(m1)


    def test_new_callable_keyword_arguments(self):
        klasa Bar(object):
            kwargs = Nic
            def __init__(self, **kwargs):
                Bar.kwargs = kwargs

        patcher = patch(foo_name, new_callable=Bar, arg1=1, arg2=2)
        m = patcher.start()
        spróbuj:
            self.assertIs(type(m), Bar)
            self.assertEqual(Bar.kwargs, dict(arg1=1, arg2=2))
        w_końcu:
            patcher.stop()


    def test_new_callable_spec(self):
        klasa Bar(object):
            kwargs = Nic
            def __init__(self, **kwargs):
                Bar.kwargs = kwargs

        patcher = patch(foo_name, new_callable=Bar, spec=Bar)
        patcher.start()
        spróbuj:
            self.assertEqual(Bar.kwargs, dict(spec=Bar))
        w_końcu:
            patcher.stop()

        patcher = patch(foo_name, new_callable=Bar, spec_set=Bar)
        patcher.start()
        spróbuj:
            self.assertEqual(Bar.kwargs, dict(spec_set=Bar))
        w_końcu:
            patcher.stop()


    def test_new_callable_create(self):
        non_existent_attr = '%s.weeeee' % foo_name
        p = patch(non_existent_attr, new_callable=NonCallableMock)
        self.assertRaises(AttributeError, p.start)

        p = patch(non_existent_attr, new_callable=NonCallableMock,
                  create=Prawda)
        m = p.start()
        spróbuj:
            self.assertNotCallable(m, magic=Nieprawda)
        w_końcu:
            p.stop()


    def test_new_callable_incompatible_with_new(self):
        self.assertRaises(
            ValueError, patch, foo_name, new=object(), new_callable=MagicMock
        )
        self.assertRaises(
            ValueError, patch.object, Foo, 'f', new=object(),
            new_callable=MagicMock
        )


    def test_new_callable_incompatible_with_autospec(self):
        self.assertRaises(
            ValueError, patch, foo_name, new_callable=MagicMock,
            autospec=Prawda
        )
        self.assertRaises(
            ValueError, patch.object, Foo, 'f', new_callable=MagicMock,
            autospec=Prawda
        )


    def test_new_callable_inherit_for_mocks(self):
        klasa MockSub(Mock):
            dalej

        MockClasses = (
            NonCallableMock, NonCallableMagicMock, MagicMock, Mock, MockSub
        )
        dla Klass w MockClasses:
            dla arg w 'spec', 'spec_set':
                kwargs = {arg: Prawda}
                p = patch(foo_name, new_callable=Klass, **kwargs)
                m = p.start()
                spróbuj:
                    instance = m.return_value
                    self.assertRaises(AttributeError, getattr, instance, 'x')
                w_końcu:
                    p.stop()


    def test_new_callable_inherit_non_mock(self):
        klasa NotAMock(object):
            def __init__(self, spec):
                self.spec = spec

        p = patch(foo_name, new_callable=NotAMock, spec=Prawda)
        m = p.start()
        spróbuj:
            self.assertPrawda(is_instance(m, NotAMock))
            self.assertRaises(AttributeError, getattr, m, 'return_value')
        w_końcu:
            p.stop()

        self.assertEqual(m.spec, Foo)


    def test_new_callable_class_decorating(self):
        test = self
        original = Foo
        klasa SomeTest(object):

            def _test(self, mock_foo):
                test.assertIsNot(Foo, original)
                test.assertIs(Foo, mock_foo)
                test.assertIsInstance(Foo, SomeClass)

            def test_two(self, mock_foo):
                self._test(mock_foo)
            def test_one(self, mock_foo):
                self._test(mock_foo)

        SomeTest = patch(foo_name, new_callable=SomeClass)(SomeTest)
        SomeTest().test_one()
        SomeTest().test_two()
        self.assertIs(Foo, original)


    def test_patch_multiple(self):
        original_foo = Foo
        original_f = Foo.f
        original_g = Foo.g

        patcher1 = patch.multiple(foo_name, f=1, g=2)
        patcher2 = patch.multiple(Foo, f=1, g=2)

        dla patcher w patcher1, patcher2:
            patcher.start()
            spróbuj:
                self.assertIs(Foo, original_foo)
                self.assertEqual(Foo.f, 1)
                self.assertEqual(Foo.g, 2)
            w_końcu:
                patcher.stop()

            self.assertIs(Foo, original_foo)
            self.assertEqual(Foo.f, original_f)
            self.assertEqual(Foo.g, original_g)


        @patch.multiple(foo_name, f=3, g=4)
        def test():
            self.assertIs(Foo, original_foo)
            self.assertEqual(Foo.f, 3)
            self.assertEqual(Foo.g, 4)

        test()


    def test_patch_multiple_no_kwargs(self):
        self.assertRaises(ValueError, patch.multiple, foo_name)
        self.assertRaises(ValueError, patch.multiple, Foo)


    def test_patch_multiple_create_mocks(self):
        original_foo = Foo
        original_f = Foo.f
        original_g = Foo.g

        @patch.multiple(foo_name, f=DEFAULT, g=3, foo=DEFAULT)
        def test(f, foo):
            self.assertIs(Foo, original_foo)
            self.assertIs(Foo.f, f)
            self.assertEqual(Foo.g, 3)
            self.assertIs(Foo.foo, foo)
            self.assertPrawda(is_instance(f, MagicMock))
            self.assertPrawda(is_instance(foo, MagicMock))

        test()
        self.assertEqual(Foo.f, original_f)
        self.assertEqual(Foo.g, original_g)


    def test_patch_multiple_create_mocks_different_order(self):
        # bug revealed by Jython!
        original_f = Foo.f
        original_g = Foo.g

        patcher = patch.object(Foo, 'f', 3)
        patcher.attribute_name = 'f'

        other = patch.object(Foo, 'g', DEFAULT)
        other.attribute_name = 'g'
        patcher.additional_patchers = [other]

        @patcher
        def test(g):
            self.assertIs(Foo.g, g)
            self.assertEqual(Foo.f, 3)

        test()
        self.assertEqual(Foo.f, original_f)
        self.assertEqual(Foo.g, original_g)


    def test_patch_multiple_stacked_decorators(self):
        original_foo = Foo
        original_f = Foo.f
        original_g = Foo.g

        @patch.multiple(foo_name, f=DEFAULT)
        @patch.multiple(foo_name, foo=DEFAULT)
        @patch(foo_name + '.g')
        def test1(g, **kwargs):
            _test(g, **kwargs)

        @patch.multiple(foo_name, f=DEFAULT)
        @patch(foo_name + '.g')
        @patch.multiple(foo_name, foo=DEFAULT)
        def test2(g, **kwargs):
            _test(g, **kwargs)

        @patch(foo_name + '.g')
        @patch.multiple(foo_name, f=DEFAULT)
        @patch.multiple(foo_name, foo=DEFAULT)
        def test3(g, **kwargs):
            _test(g, **kwargs)

        def _test(g, **kwargs):
            f = kwargs.pop('f')
            foo = kwargs.pop('foo')
            self.assertNieprawda(kwargs)

            self.assertIs(Foo, original_foo)
            self.assertIs(Foo.f, f)
            self.assertIs(Foo.g, g)
            self.assertIs(Foo.foo, foo)
            self.assertPrawda(is_instance(f, MagicMock))
            self.assertPrawda(is_instance(g, MagicMock))
            self.assertPrawda(is_instance(foo, MagicMock))

        test1()
        test2()
        test3()
        self.assertEqual(Foo.f, original_f)
        self.assertEqual(Foo.g, original_g)


    def test_patch_multiple_create_mocks_patcher(self):
        original_foo = Foo
        original_f = Foo.f
        original_g = Foo.g

        patcher = patch.multiple(foo_name, f=DEFAULT, g=3, foo=DEFAULT)

        result = patcher.start()
        spróbuj:
            f = result['f']
            foo = result['foo']
            self.assertEqual(set(result), set(['f', 'foo']))

            self.assertIs(Foo, original_foo)
            self.assertIs(Foo.f, f)
            self.assertIs(Foo.foo, foo)
            self.assertPrawda(is_instance(f, MagicMock))
            self.assertPrawda(is_instance(foo, MagicMock))
        w_końcu:
            patcher.stop()

        self.assertEqual(Foo.f, original_f)
        self.assertEqual(Foo.g, original_g)


    def test_patch_multiple_decorating_class(self):
        test = self
        original_foo = Foo
        original_f = Foo.f
        original_g = Foo.g

        klasa SomeTest(object):

            def _test(self, f, foo):
                test.assertIs(Foo, original_foo)
                test.assertIs(Foo.f, f)
                test.assertEqual(Foo.g, 3)
                test.assertIs(Foo.foo, foo)
                test.assertPrawda(is_instance(f, MagicMock))
                test.assertPrawda(is_instance(foo, MagicMock))

            def test_two(self, f, foo):
                self._test(f, foo)
            def test_one(self, f, foo):
                self._test(f, foo)

        SomeTest = patch.multiple(
            foo_name, f=DEFAULT, g=3, foo=DEFAULT
        )(SomeTest)

        thing = SomeTest()
        thing.test_one()
        thing.test_two()

        self.assertEqual(Foo.f, original_f)
        self.assertEqual(Foo.g, original_g)


    def test_patch_multiple_create(self):
        patcher = patch.multiple(Foo, blam='blam')
        self.assertRaises(AttributeError, patcher.start)

        patcher = patch.multiple(Foo, blam='blam', create=Prawda)
        patcher.start()
        spróbuj:
            self.assertEqual(Foo.blam, 'blam')
        w_końcu:
            patcher.stop()

        self.assertNieprawda(hasattr(Foo, 'blam'))


    def test_patch_multiple_spec_set(self):
        # jeżeli spec_set works then we can assume that spec oraz autospec also
        # work jako the underlying machinery jest the same
        patcher = patch.multiple(Foo, foo=DEFAULT, spec_set=['a', 'b'])
        result = patcher.start()
        spróbuj:
            self.assertEqual(Foo.foo, result['foo'])
            Foo.foo.a(1)
            Foo.foo.b(2)
            Foo.foo.a.assert_called_with(1)
            Foo.foo.b.assert_called_with(2)
            self.assertRaises(AttributeError, setattr, Foo.foo, 'c', Nic)
        w_końcu:
            patcher.stop()


    def test_patch_multiple_new_callable(self):
        klasa Thing(object):
            dalej

        patcher = patch.multiple(
            Foo, f=DEFAULT, g=DEFAULT, new_callable=Thing
        )
        result = patcher.start()
        spróbuj:
            self.assertIs(Foo.f, result['f'])
            self.assertIs(Foo.g, result['g'])
            self.assertIsInstance(Foo.f, Thing)
            self.assertIsInstance(Foo.g, Thing)
            self.assertIsNot(Foo.f, Foo.g)
        w_końcu:
            patcher.stop()


    def test_nested_patch_failure(self):
        original_f = Foo.f
        original_g = Foo.g

        @patch.object(Foo, 'g', 1)
        @patch.object(Foo, 'missing', 1)
        @patch.object(Foo, 'f', 1)
        def thing1():
            dalej

        @patch.object(Foo, 'missing', 1)
        @patch.object(Foo, 'g', 1)
        @patch.object(Foo, 'f', 1)
        def thing2():
            dalej

        @patch.object(Foo, 'g', 1)
        @patch.object(Foo, 'f', 1)
        @patch.object(Foo, 'missing', 1)
        def thing3():
            dalej

        dla func w thing1, thing2, thing3:
            self.assertRaises(AttributeError, func)
            self.assertEqual(Foo.f, original_f)
            self.assertEqual(Foo.g, original_g)


    def test_new_callable_failure(self):
        original_f = Foo.f
        original_g = Foo.g
        original_foo = Foo.foo

        def crasher():
            podnieś NameError('crasher')

        @patch.object(Foo, 'g', 1)
        @patch.object(Foo, 'foo', new_callable=crasher)
        @patch.object(Foo, 'f', 1)
        def thing1():
            dalej

        @patch.object(Foo, 'foo', new_callable=crasher)
        @patch.object(Foo, 'g', 1)
        @patch.object(Foo, 'f', 1)
        def thing2():
            dalej

        @patch.object(Foo, 'g', 1)
        @patch.object(Foo, 'f', 1)
        @patch.object(Foo, 'foo', new_callable=crasher)
        def thing3():
            dalej

        dla func w thing1, thing2, thing3:
            self.assertRaises(NameError, func)
            self.assertEqual(Foo.f, original_f)
            self.assertEqual(Foo.g, original_g)
            self.assertEqual(Foo.foo, original_foo)


    def test_patch_multiple_failure(self):
        original_f = Foo.f
        original_g = Foo.g

        patcher = patch.object(Foo, 'f', 1)
        patcher.attribute_name = 'f'

        good = patch.object(Foo, 'g', 1)
        good.attribute_name = 'g'

        bad = patch.object(Foo, 'missing', 1)
        bad.attribute_name = 'missing'

        dla additionals w [good, bad], [bad, good]:
            patcher.additional_patchers = additionals

            @patcher
            def func():
                dalej

            self.assertRaises(AttributeError, func)
            self.assertEqual(Foo.f, original_f)
            self.assertEqual(Foo.g, original_g)


    def test_patch_multiple_new_callable_failure(self):
        original_f = Foo.f
        original_g = Foo.g
        original_foo = Foo.foo

        def crasher():
            podnieś NameError('crasher')

        patcher = patch.object(Foo, 'f', 1)
        patcher.attribute_name = 'f'

        good = patch.object(Foo, 'g', 1)
        good.attribute_name = 'g'

        bad = patch.object(Foo, 'foo', new_callable=crasher)
        bad.attribute_name = 'foo'

        dla additionals w [good, bad], [bad, good]:
            patcher.additional_patchers = additionals

            @patcher
            def func():
                dalej

            self.assertRaises(NameError, func)
            self.assertEqual(Foo.f, original_f)
            self.assertEqual(Foo.g, original_g)
            self.assertEqual(Foo.foo, original_foo)


    def test_patch_multiple_string_subclasses(self):
        Foo = type('Foo', (str,), {'fish': 'tasty'})
        foo = Foo()
        @patch.multiple(foo, fish='nearly gone')
        def test():
            self.assertEqual(foo.fish, 'nearly gone')

        test()
        self.assertEqual(foo.fish, 'tasty')


    @patch('unittest.mock.patch.TEST_PREFIX', 'foo')
    def test_patch_test_prefix(self):
        klasa Foo(object):
            thing = 'original'

            def foo_one(self):
                zwróć self.thing
            def foo_two(self):
                zwróć self.thing
            def test_one(self):
                zwróć self.thing
            def test_two(self):
                zwróć self.thing

        Foo = patch.object(Foo, 'thing', 'changed')(Foo)

        foo = Foo()
        self.assertEqual(foo.foo_one(), 'changed')
        self.assertEqual(foo.foo_two(), 'changed')
        self.assertEqual(foo.test_one(), 'original')
        self.assertEqual(foo.test_two(), 'original')


    @patch('unittest.mock.patch.TEST_PREFIX', 'bar')
    def test_patch_dict_test_prefix(self):
        klasa Foo(object):
            def bar_one(self):
                zwróć dict(the_dict)
            def bar_two(self):
                zwróć dict(the_dict)
            def test_one(self):
                zwróć dict(the_dict)
            def test_two(self):
                zwróć dict(the_dict)

        the_dict = {'key': 'original'}
        Foo = patch.dict(the_dict, key='changed')(Foo)

        foo =Foo()
        self.assertEqual(foo.bar_one(), {'key': 'changed'})
        self.assertEqual(foo.bar_two(), {'key': 'changed'})
        self.assertEqual(foo.test_one(), {'key': 'original'})
        self.assertEqual(foo.test_two(), {'key': 'original'})


    def test_patch_with_spec_mock_repr(self):
        dla arg w ('spec', 'autospec', 'spec_set'):
            p = patch('%s.SomeClass' % __name__, **{arg: Prawda})
            m = p.start()
            spróbuj:
                self.assertIn(" name='SomeClass'", repr(m))
                self.assertIn(" name='SomeClass.class_attribute'",
                              repr(m.class_attribute))
                self.assertIn(" name='SomeClass()'", repr(m()))
                self.assertIn(" name='SomeClass().class_attribute'",
                              repr(m().class_attribute))
            w_końcu:
                p.stop()


    def test_patch_nested_autospec_repr(self):
        przy patch('unittest.test.testmock.support', autospec=Prawda) jako m:
            self.assertIn(" name='support.SomeClass.wibble()'",
                          repr(m.SomeClass.wibble()))
            self.assertIn(" name='support.SomeClass().wibble()'",
                          repr(m.SomeClass().wibble()))



    def test_mock_calls_with_patch(self):
        dla arg w ('spec', 'autospec', 'spec_set'):
            p = patch('%s.SomeClass' % __name__, **{arg: Prawda})
            m = p.start()
            spróbuj:
                m.wibble()

                kalls = [call.wibble()]
                self.assertEqual(m.mock_calls, kalls)
                self.assertEqual(m.method_calls, kalls)
                self.assertEqual(m.wibble.mock_calls, [call()])

                result = m()
                kalls.append(call())
                self.assertEqual(m.mock_calls, kalls)

                result.wibble()
                kalls.append(call().wibble())
                self.assertEqual(m.mock_calls, kalls)

                self.assertEqual(result.mock_calls, [call.wibble()])
                self.assertEqual(result.wibble.mock_calls, [call()])
                self.assertEqual(result.method_calls, [call.wibble()])
            w_końcu:
                p.stop()


    def test_patch_imports_lazily(self):
        sys.modules.pop('squizz', Nic)

        p1 = patch('squizz.squozz')
        self.assertRaises(ImportError, p1.start)

        squizz = Mock()
        squizz.squozz = 6
        sys.modules['squizz'] = squizz
        p1 = patch('squizz.squozz')
        squizz.squozz = 3
        p1.start()
        p1.stop()
        self.assertEqual(squizz.squozz, 3)


    def test_patch_propogrates_exc_on_exit(self):
        klasa holder:
            exc_info = Nic, Nic, Nic

        klasa custom_patch(_patch):
            def __exit__(self, etype=Nic, val=Nic, tb=Nic):
                _patch.__exit__(self, etype, val, tb)
                holder.exc_info = etype, val, tb
            stop = __exit__

        def with_custom_patch(target):
            getter, attribute = _get_target(target)
            zwróć custom_patch(
                getter, attribute, DEFAULT, Nic, Nieprawda, Nic,
                Nic, Nic, {}
            )

        @with_custom_patch('squizz.squozz')
        def test(mock):
            podnieś RuntimeError

        self.assertRaises(RuntimeError, test)
        self.assertIs(holder.exc_info[0], RuntimeError)
        self.assertIsNotNic(holder.exc_info[1],
                            'exception value nie propgated')
        self.assertIsNotNic(holder.exc_info[2],
                            'exception traceback nie propgated')


    def test_create_and_specs(self):
        dla kwarg w ('spec', 'spec_set', 'autospec'):
            p = patch('%s.doesnotexist' % __name__, create=Prawda,
                      **{kwarg: Prawda})
            self.assertRaises(TypeError, p.start)
            self.assertRaises(NameError, lambda: doesnotexist)

            # check that spec przy create jest innocuous jeżeli the original exists
            p = patch(MODNAME, create=Prawda, **{kwarg: Prawda})
            p.start()
            p.stop()


    def test_multiple_specs(self):
        original = PTModule
        dla kwarg w ('spec', 'spec_set'):
            p = patch(MODNAME, autospec=0, **{kwarg: 0})
            self.assertRaises(TypeError, p.start)
            self.assertIs(PTModule, original)

        dla kwarg w ('spec', 'autospec'):
            p = patch(MODNAME, spec_set=0, **{kwarg: 0})
            self.assertRaises(TypeError, p.start)
            self.assertIs(PTModule, original)

        dla kwarg w ('spec_set', 'autospec'):
            p = patch(MODNAME, spec=0, **{kwarg: 0})
            self.assertRaises(TypeError, p.start)
            self.assertIs(PTModule, original)


    def test_specs_false_instead_of_none(self):
        p = patch(MODNAME, spec=Nieprawda, spec_set=Nieprawda, autospec=Nieprawda)
        mock = p.start()
        spróbuj:
            # no spec should have been set, so attribute access should nie fail
            mock.does_not_exist
            mock.does_not_exist = 3
        w_końcu:
            p.stop()


    def test_falsey_spec(self):
        dla kwarg w ('spec', 'autospec', 'spec_set'):
            p = patch(MODNAME, **{kwarg: 0})
            m = p.start()
            spróbuj:
                self.assertRaises(AttributeError, getattr, m, 'doesnotexit')
            w_końcu:
                p.stop()


    def test_spec_set_true(self):
        dla kwarg w ('spec', 'autospec'):
            p = patch(MODNAME, spec_set=Prawda, **{kwarg: Prawda})
            m = p.start()
            spróbuj:
                self.assertRaises(AttributeError, setattr, m,
                                  'doesnotexist', 'something')
                self.assertRaises(AttributeError, getattr, m, 'doesnotexist')
            w_końcu:
                p.stop()


    def test_callable_spec_as_list(self):
        spec = ('__call__',)
        p = patch(MODNAME, spec=spec)
        m = p.start()
        spróbuj:
            self.assertPrawda(callable(m))
        w_końcu:
            p.stop()


    def test_not_callable_spec_as_list(self):
        spec = ('foo', 'bar')
        p = patch(MODNAME, spec=spec)
        m = p.start()
        spróbuj:
            self.assertNieprawda(callable(m))
        w_końcu:
            p.stop()


    def test_patch_stopall(self):
        unlink = os.unlink
        chdir = os.chdir
        path = os.path
        patch('os.unlink', something).start()
        patch('os.chdir', something_inaczej).start()

        @patch('os.path')
        def patched(mock_path):
            patch.stopall()
            self.assertIs(os.path, mock_path)
            self.assertIs(os.unlink, unlink)
            self.assertIs(os.chdir, chdir)

        patched()
        self.assertIs(os.path, path)

    def test_stopall_lifo(self):
        stopped = []
        klasa thing(object):
            one = two = three = Nic

        def get_patch(attribute):
            klasa mypatch(_patch):
                def stop(self):
                    stopped.append(attribute)
                    zwróć super(mypatch, self).stop()
            zwróć mypatch(lambda: thing, attribute, Nic, Nic,
                           Nieprawda, Nic, Nic, Nic, {})
        [get_patch(val).start() dla val w ("one", "two", "three")]
        patch.stopall()

        self.assertEqual(stopped, ["three", "two", "one"])


jeżeli __name__ == '__main__':
    unittest.main()
