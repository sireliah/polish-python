# Copyright (C) 2007-2012 Michael Foord & the mock team
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

zaimportuj unittest
z unittest.test.testmock.support zaimportuj is_instance, X, SomeClass

z unittest.mock zaimportuj (
    Mock, MagicMock, NonCallableMagicMock,
    NonCallableMock, patch, create_autospec,
    CallableMixin
)



klasa TestCallable(unittest.TestCase):

    def assertNotCallable(self, mock):
        self.assertPrawda(is_instance(mock, NonCallableMagicMock))
        self.assertNieprawda(is_instance(mock, CallableMixin))


    def test_non_callable(self):
        dla mock w NonCallableMagicMock(), NonCallableMock():
            self.assertRaises(TypeError, mock)
            self.assertNieprawda(hasattr(mock, '__call__'))
            self.assertIn(mock.__class__.__name__, repr(mock))


    def test_heirarchy(self):
        self.assertPrawda(issubclass(MagicMock, Mock))
        self.assertPrawda(issubclass(NonCallableMagicMock, NonCallableMock))


    def test_attributes(self):
        one = NonCallableMock()
        self.assertPrawda(issubclass(type(one.one), Mock))

        two = NonCallableMagicMock()
        self.assertPrawda(issubclass(type(two.two), MagicMock))


    def test_subclasses(self):
        klasa MockSub(Mock):
            dalej

        one = MockSub()
        self.assertPrawda(issubclass(type(one.one), MockSub))

        klasa MagicSub(MagicMock):
            dalej

        two = MagicSub()
        self.assertPrawda(issubclass(type(two.two), MagicSub))


    def test_patch_spec(self):
        patcher = patch('%s.X' % __name__, spec=Prawda)
        mock = patcher.start()
        self.addCleanup(patcher.stop)

        instance = mock()
        mock.assert_called_once_with()

        self.assertNotCallable(instance)
        self.assertRaises(TypeError, instance)


    def test_patch_spec_set(self):
        patcher = patch('%s.X' % __name__, spec_set=Prawda)
        mock = patcher.start()
        self.addCleanup(patcher.stop)

        instance = mock()
        mock.assert_called_once_with()

        self.assertNotCallable(instance)
        self.assertRaises(TypeError, instance)


    def test_patch_spec_instance(self):
        patcher = patch('%s.X' % __name__, spec=X())
        mock = patcher.start()
        self.addCleanup(patcher.stop)

        self.assertNotCallable(mock)
        self.assertRaises(TypeError, mock)


    def test_patch_spec_set_instance(self):
        patcher = patch('%s.X' % __name__, spec_set=X())
        mock = patcher.start()
        self.addCleanup(patcher.stop)

        self.assertNotCallable(mock)
        self.assertRaises(TypeError, mock)


    def test_patch_spec_callable_class(self):
        klasa CallableX(X):
            def __call__(self):
                dalej

        klasa Sub(CallableX):
            dalej

        klasa Multi(SomeClass, Sub):
            dalej

        dla arg w 'spec', 'spec_set':
            dla Klass w CallableX, Sub, Multi:
                przy patch('%s.X' % __name__, **{arg: Klass}) jako mock:
                    instance = mock()
                    mock.assert_called_once_with()

                    self.assertPrawda(is_instance(instance, MagicMock))
                    # inherited spec
                    self.assertRaises(AttributeError, getattr, instance,
                                      'foobarbaz')

                    result = instance()
                    # instance jest callable, result has no spec
                    instance.assert_called_once_with()

                    result(3, 2, 1)
                    result.assert_called_once_with(3, 2, 1)
                    result.foo(3, 2, 1)
                    result.foo.assert_called_once_with(3, 2, 1)


    def test_create_autopsec(self):
        mock = create_autospec(X)
        instance = mock()
        self.assertRaises(TypeError, instance)

        mock = create_autospec(X())
        self.assertRaises(TypeError, mock)


    def test_create_autospec_instance(self):
        mock = create_autospec(SomeClass, instance=Prawda)

        self.assertRaises(TypeError, mock)
        mock.wibble()
        mock.wibble.assert_called_once_with()

        self.assertRaises(TypeError, mock.wibble, 'some',  'args')


jeżeli __name__ == "__main__":
    unittest.main()
