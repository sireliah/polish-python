zaimportuj copy
zaimportuj sys
zaimportuj tempfile

zaimportuj unittest
z unittest.test.testmock.support zaimportuj is_instance
z unittest zaimportuj mock
z unittest.mock zaimportuj (
    call, DEFAULT, patch, sentinel,
    MagicMock, Mock, NonCallableMock,
    NonCallableMagicMock, _CallList,
    create_autospec
)


klasa Iter(object):
    def __init__(self):
        self.thing = iter(['this', 'is', 'an', 'iter'])

    def __iter__(self):
        zwróć self

    def next(self):
        zwróć next(self.thing)

    __next__ = next


klasa Something(object):
    def meth(self, a, b, c, d=Nic):
        dalej

    @classmethod
    def cmeth(cls, a, b, c, d=Nic):
        dalej

    @staticmethod
    def smeth(a, b, c, d=Nic):
        dalej


klasa MockTest(unittest.TestCase):

    def test_all(self):
        # jeżeli __all__ jest badly defined then zaimportuj * will podnieś an error
        # We have to exec it because you can't zaimportuj * inside a method
        # w Python 3
        exec("z unittest.mock zaimportuj *")


    def test_constructor(self):
        mock = Mock()

        self.assertNieprawda(mock.called, "called nie initialised correctly")
        self.assertEqual(mock.call_count, 0,
                         "call_count nie initialised correctly")
        self.assertPrawda(is_instance(mock.return_value, Mock),
                        "return_value nie initialised correctly")

        self.assertEqual(mock.call_args, Nic,
                         "call_args nie initialised correctly")
        self.assertEqual(mock.call_args_list, [],
                         "call_args_list nie initialised correctly")
        self.assertEqual(mock.method_calls, [],
                          "method_calls nie initialised correctly")

        # Can't use hasattr dla this test jako it always returns Prawda on a mock
        self.assertNotIn('_items', mock.__dict__,
                         "default mock should nie have '_items' attribute")

        self.assertIsNic(mock._mock_parent,
                          "parent nie initialised correctly")
        self.assertIsNic(mock._mock_methods,
                          "methods nie initialised correctly")
        self.assertEqual(mock._mock_children, {},
                         "children nie initialised incorrectly")


    def test_return_value_in_constructor(self):
        mock = Mock(return_value=Nic)
        self.assertIsNic(mock.return_value,
                          "return value w constructor nie honoured")


    def test_repr(self):
        mock = Mock(name='foo')
        self.assertIn('foo', repr(mock))
        self.assertIn("'%s'" % id(mock), repr(mock))

        mocks = [(Mock(), 'mock'), (Mock(name='bar'), 'bar')]
        dla mock, name w mocks:
            self.assertIn('%s.bar' % name, repr(mock.bar))
            self.assertIn('%s.foo()' % name, repr(mock.foo()))
            self.assertIn('%s.foo().bing' % name, repr(mock.foo().bing))
            self.assertIn('%s()' % name, repr(mock()))
            self.assertIn('%s()()' % name, repr(mock()()))
            self.assertIn('%s()().foo.bar.baz().bing' % name,
                          repr(mock()().foo.bar.baz().bing))


    def test_repr_with_spec(self):
        klasa X(object):
            dalej

        mock = Mock(spec=X)
        self.assertIn(" spec='X' ", repr(mock))

        mock = Mock(spec=X())
        self.assertIn(" spec='X' ", repr(mock))

        mock = Mock(spec_set=X)
        self.assertIn(" spec_set='X' ", repr(mock))

        mock = Mock(spec_set=X())
        self.assertIn(" spec_set='X' ", repr(mock))

        mock = Mock(spec=X, name='foo')
        self.assertIn(" spec='X' ", repr(mock))
        self.assertIn(" name='foo' ", repr(mock))

        mock = Mock(name='foo')
        self.assertNotIn("spec", repr(mock))

        mock = Mock()
        self.assertNotIn("spec", repr(mock))

        mock = Mock(spec=['foo'])
        self.assertNotIn("spec", repr(mock))


    def test_side_effect(self):
        mock = Mock()

        def effect(*args, **kwargs):
            podnieś SystemError('kablooie')

        mock.side_effect = effect
        self.assertRaises(SystemError, mock, 1, 2, fish=3)
        mock.assert_called_with(1, 2, fish=3)

        results = [1, 2, 3]
        def effect():
            zwróć results.pop()
        mock.side_effect = effect

        self.assertEqual([mock(), mock(), mock()], [3, 2, 1],
                          "side effect nie used correctly")

        mock = Mock(side_effect=sentinel.SideEffect)
        self.assertEqual(mock.side_effect, sentinel.SideEffect,
                          "side effect w constructor nie used")

        def side_effect():
            zwróć DEFAULT
        mock = Mock(side_effect=side_effect, return_value=sentinel.RETURN)
        self.assertEqual(mock(), sentinel.RETURN)

    def test_autospec_side_effect(self):
        # Test dla issue17826
        results = [1, 2, 3]
        def effect():
            zwróć results.pop()
        def f():
            dalej

        mock = create_autospec(f)
        mock.side_effect = [1, 2, 3]
        self.assertEqual([mock(), mock(), mock()], [1, 2, 3],
                          "side effect nie used correctly w create_autospec")
        # Test where side effect jest a callable
        results = [1, 2, 3]
        mock = create_autospec(f)
        mock.side_effect = effect
        self.assertEqual([mock(), mock(), mock()], [3, 2, 1],
                          "callable side effect nie used correctly")

    def test_autospec_side_effect_exception(self):
        # Test dla issue 23661
        def f():
            dalej

        mock = create_autospec(f)
        mock.side_effect = ValueError('Bazinga!')
        self.assertRaisesRegex(ValueError, 'Bazinga!', mock)

    @unittest.skipUnless('java' w sys.platform,
                          'This test only applies to Jython')
    def test_java_exception_side_effect(self):
        zaimportuj java
        mock = Mock(side_effect=java.lang.RuntimeException("Boom!"))

        # can't use assertRaises przy java exceptions
        spróbuj:
            mock(1, 2, fish=3)
        wyjąwszy java.lang.RuntimeException:
            dalej
        inaczej:
            self.fail('java exception nie podnieśd')
        mock.assert_called_with(1,2, fish=3)


    def test_reset_mock(self):
        parent = Mock()
        spec = ["something"]
        mock = Mock(name="child", parent=parent, spec=spec)
        mock(sentinel.Something, something=sentinel.SomethingElse)
        something = mock.something
        mock.something()
        mock.side_effect = sentinel.SideEffect
        return_value = mock.return_value
        return_value()

        mock.reset_mock()

        self.assertEqual(mock._mock_name, "child",
                         "name incorrectly reset")
        self.assertEqual(mock._mock_parent, parent,
                         "parent incorrectly reset")
        self.assertEqual(mock._mock_methods, spec,
                         "methods incorrectly reset")

        self.assertNieprawda(mock.called, "called nie reset")
        self.assertEqual(mock.call_count, 0, "call_count nie reset")
        self.assertEqual(mock.call_args, Nic, "call_args nie reset")
        self.assertEqual(mock.call_args_list, [], "call_args_list nie reset")
        self.assertEqual(mock.method_calls, [],
                        "method_calls nie initialised correctly: %r != %r" %
                        (mock.method_calls, []))
        self.assertEqual(mock.mock_calls, [])

        self.assertEqual(mock.side_effect, sentinel.SideEffect,
                          "side_effect incorrectly reset")
        self.assertEqual(mock.return_value, return_value,
                          "return_value incorrectly reset")
        self.assertNieprawda(return_value.called, "return value mock nie reset")
        self.assertEqual(mock._mock_children, {'something': something},
                          "children reset incorrectly")
        self.assertEqual(mock.something, something,
                          "children incorrectly cleared")
        self.assertNieprawda(mock.something.called, "child nie reset")


    def test_reset_mock_recursion(self):
        mock = Mock()
        mock.return_value = mock

        # used to cause recursion
        mock.reset_mock()

    def test_reset_mock_on_mock_open_issue_18622(self):
        a = mock.mock_open()
        a.reset_mock()

    def test_call(self):
        mock = Mock()
        self.assertPrawda(is_instance(mock.return_value, Mock),
                        "Default return_value should be a Mock")

        result = mock()
        self.assertEqual(mock(), result,
                         "different result z consecutive calls")
        mock.reset_mock()

        ret_val = mock(sentinel.Arg)
        self.assertPrawda(mock.called, "called nie set")
        self.assertEqual(mock.call_count, 1, "call_count incoreect")
        self.assertEqual(mock.call_args, ((sentinel.Arg,), {}),
                         "call_args nie set")
        self.assertEqual(mock.call_args_list, [((sentinel.Arg,), {})],
                         "call_args_list nie initialised correctly")

        mock.return_value = sentinel.ReturnValue
        ret_val = mock(sentinel.Arg, key=sentinel.KeyArg)
        self.assertEqual(ret_val, sentinel.ReturnValue,
                         "incorrect zwróć value")

        self.assertEqual(mock.call_count, 2, "call_count incorrect")
        self.assertEqual(mock.call_args,
                         ((sentinel.Arg,), {'key': sentinel.KeyArg}),
                         "call_args nie set")
        self.assertEqual(mock.call_args_list, [
            ((sentinel.Arg,), {}),
            ((sentinel.Arg,), {'key': sentinel.KeyArg})
        ],
            "call_args_list nie set")


    def test_call_args_comparison(self):
        mock = Mock()
        mock()
        mock(sentinel.Arg)
        mock(kw=sentinel.Kwarg)
        mock(sentinel.Arg, kw=sentinel.Kwarg)
        self.assertEqual(mock.call_args_list, [
            (),
            ((sentinel.Arg,),),
            ({"kw": sentinel.Kwarg},),
            ((sentinel.Arg,), {"kw": sentinel.Kwarg})
        ])
        self.assertEqual(mock.call_args,
                         ((sentinel.Arg,), {"kw": sentinel.Kwarg}))


    def test_assert_called_with(self):
        mock = Mock()
        mock()

        # Will podnieś an exception jeżeli it fails
        mock.assert_called_with()
        self.assertRaises(AssertionError, mock.assert_called_with, 1)

        mock.reset_mock()
        self.assertRaises(AssertionError, mock.assert_called_with)

        mock(1, 2, 3, a='fish', b='nothing')
        mock.assert_called_with(1, 2, 3, a='fish', b='nothing')


    def test_assert_called_with_function_spec(self):
        def f(a, b, c, d=Nic):
            dalej

        mock = Mock(spec=f)

        mock(1, b=2, c=3)
        mock.assert_called_with(1, 2, 3)
        mock.assert_called_with(a=1, b=2, c=3)
        self.assertRaises(AssertionError, mock.assert_called_with,
                          1, b=3, c=2)
        # Expected call doesn't match the spec's signature
        przy self.assertRaises(AssertionError) jako cm:
            mock.assert_called_with(e=8)
        self.assertIsInstance(cm.exception.__cause__, TypeError)


    def test_assert_called_with_method_spec(self):
        def _check(mock):
            mock(1, b=2, c=3)
            mock.assert_called_with(1, 2, 3)
            mock.assert_called_with(a=1, b=2, c=3)
            self.assertRaises(AssertionError, mock.assert_called_with,
                              1, b=3, c=2)

        mock = Mock(spec=Something().meth)
        _check(mock)
        mock = Mock(spec=Something.cmeth)
        _check(mock)
        mock = Mock(spec=Something().cmeth)
        _check(mock)
        mock = Mock(spec=Something.smeth)
        _check(mock)
        mock = Mock(spec=Something().smeth)
        _check(mock)


    def test_assert_called_once_with(self):
        mock = Mock()
        mock()

        # Will podnieś an exception jeżeli it fails
        mock.assert_called_once_with()

        mock()
        self.assertRaises(AssertionError, mock.assert_called_once_with)

        mock.reset_mock()
        self.assertRaises(AssertionError, mock.assert_called_once_with)

        mock('foo', 'bar', baz=2)
        mock.assert_called_once_with('foo', 'bar', baz=2)

        mock.reset_mock()
        mock('foo', 'bar', baz=2)
        self.assertRaises(
            AssertionError,
            lambda: mock.assert_called_once_with('bob', 'bar', baz=2)
        )


    def test_assert_called_once_with_function_spec(self):
        def f(a, b, c, d=Nic):
            dalej

        mock = Mock(spec=f)

        mock(1, b=2, c=3)
        mock.assert_called_once_with(1, 2, 3)
        mock.assert_called_once_with(a=1, b=2, c=3)
        self.assertRaises(AssertionError, mock.assert_called_once_with,
                          1, b=3, c=2)
        # Expected call doesn't match the spec's signature
        przy self.assertRaises(AssertionError) jako cm:
            mock.assert_called_once_with(e=8)
        self.assertIsInstance(cm.exception.__cause__, TypeError)
        # Mock called more than once => always fails
        mock(4, 5, 6)
        self.assertRaises(AssertionError, mock.assert_called_once_with,
                          1, 2, 3)
        self.assertRaises(AssertionError, mock.assert_called_once_with,
                          4, 5, 6)


    def test_attribute_access_returns_mocks(self):
        mock = Mock()
        something = mock.something
        self.assertPrawda(is_instance(something, Mock), "attribute isn't a mock")
        self.assertEqual(mock.something, something,
                         "different attributes returned dla same name")

        # Usage example
        mock = Mock()
        mock.something.return_value = 3

        self.assertEqual(mock.something(), 3, "method returned wrong value")
        self.assertPrawda(mock.something.called,
                        "method didn't record being called")


    def test_attributes_have_name_and_parent_set(self):
        mock = Mock()
        something = mock.something

        self.assertEqual(something._mock_name, "something",
                         "attribute name nie set correctly")
        self.assertEqual(something._mock_parent, mock,
                         "attribute parent nie set correctly")


    def test_method_calls_recorded(self):
        mock = Mock()
        mock.something(3, fish=Nic)
        mock.something_inaczej.something(6, cake=sentinel.Cake)

        self.assertEqual(mock.something_inaczej.method_calls,
                          [("something", (6,), {'cake': sentinel.Cake})],
                          "method calls nie recorded correctly")
        self.assertEqual(mock.method_calls, [
            ("something", (3,), {'fish': Nic}),
            ("something_inaczej.something", (6,), {'cake': sentinel.Cake})
        ],
            "method calls nie recorded correctly")


    def test_method_calls_compare_easily(self):
        mock = Mock()
        mock.something()
        self.assertEqual(mock.method_calls, [('something',)])
        self.assertEqual(mock.method_calls, [('something', (), {})])

        mock = Mock()
        mock.something('different')
        self.assertEqual(mock.method_calls, [('something', ('different',))])
        self.assertEqual(mock.method_calls,
                         [('something', ('different',), {})])

        mock = Mock()
        mock.something(x=1)
        self.assertEqual(mock.method_calls, [('something', {'x': 1})])
        self.assertEqual(mock.method_calls, [('something', (), {'x': 1})])

        mock = Mock()
        mock.something('different', some='more')
        self.assertEqual(mock.method_calls, [
            ('something', ('different',), {'some': 'more'})
        ])


    def test_only_allowed_methods_exist(self):
        dla spec w ['something'], ('something',):
            dla arg w 'spec', 'spec_set':
                mock = Mock(**{arg: spec})

                # this should be allowed
                mock.something
                self.assertRaisesRegex(
                    AttributeError,
                    "Mock object has no attribute 'something_inaczej'",
                    getattr, mock, 'something_inaczej'
                )


    def test_from_spec(self):
        klasa Something(object):
            x = 3
            __something__ = Nic
            def y(self):
                dalej

        def test_attributes(mock):
            # should work
            mock.x
            mock.y
            mock.__something__
            self.assertRaisesRegex(
                AttributeError,
                "Mock object has no attribute 'z'",
                getattr, mock, 'z'
            )
            self.assertRaisesRegex(
                AttributeError,
                "Mock object has no attribute '__foobar__'",
                getattr, mock, '__foobar__'
            )

        test_attributes(Mock(spec=Something))
        test_attributes(Mock(spec=Something()))


    def test_wraps_calls(self):
        real = Mock()

        mock = Mock(wraps=real)
        self.assertEqual(mock(), real())

        real.reset_mock()

        mock(1, 2, fish=3)
        real.assert_called_with(1, 2, fish=3)


    def test_wraps_call_with_nondefault_return_value(self):
        real = Mock()

        mock = Mock(wraps=real)
        mock.return_value = 3

        self.assertEqual(mock(), 3)
        self.assertNieprawda(real.called)


    def test_wraps_attributes(self):
        klasa Real(object):
            attribute = Mock()

        real = Real()

        mock = Mock(wraps=real)
        self.assertEqual(mock.attribute(), real.attribute())
        self.assertRaises(AttributeError, lambda: mock.fish)

        self.assertNotEqual(mock.attribute, real.attribute)
        result = mock.attribute.frog(1, 2, fish=3)
        Real.attribute.frog.assert_called_with(1, 2, fish=3)
        self.assertEqual(result, Real.attribute.frog())


    def test_exceptional_side_effect(self):
        mock = Mock(side_effect=AttributeError)
        self.assertRaises(AttributeError, mock)

        mock = Mock(side_effect=AttributeError('foo'))
        self.assertRaises(AttributeError, mock)


    def test_baseexceptional_side_effect(self):
        mock = Mock(side_effect=KeyboardInterrupt)
        self.assertRaises(KeyboardInterrupt, mock)

        mock = Mock(side_effect=KeyboardInterrupt('foo'))
        self.assertRaises(KeyboardInterrupt, mock)


    def test_assert_called_with_message(self):
        mock = Mock()
        self.assertRaisesRegex(AssertionError, 'Not called',
                                mock.assert_called_with)


    def test_assert_called_once_with_message(self):
        mock = Mock(name='geoffrey')
        self.assertRaisesRegex(AssertionError,
                     r"Expected 'geoffrey' to be called once\.",
                     mock.assert_called_once_with)


    def test__name__(self):
        mock = Mock()
        self.assertRaises(AttributeError, lambda: mock.__name__)

        mock.__name__ = 'foo'
        self.assertEqual(mock.__name__, 'foo')


    def test_spec_list_subclass(self):
        klasa Sub(list):
            dalej
        mock = Mock(spec=Sub(['foo']))

        mock.append(3)
        mock.append.assert_called_with(3)
        self.assertRaises(AttributeError, getattr, mock, 'foo')


    def test_spec_class(self):
        klasa X(object):
            dalej

        mock = Mock(spec=X)
        self.assertIsInstance(mock, X)

        mock = Mock(spec=X())
        self.assertIsInstance(mock, X)

        self.assertIs(mock.__class__, X)
        self.assertEqual(Mock().__class__.__name__, 'Mock')

        mock = Mock(spec_set=X)
        self.assertIsInstance(mock, X)

        mock = Mock(spec_set=X())
        self.assertIsInstance(mock, X)


    def test_setting_attribute_with_spec_set(self):
        klasa X(object):
            y = 3

        mock = Mock(spec=X)
        mock.x = 'foo'

        mock = Mock(spec_set=X)
        def set_attr():
            mock.x = 'foo'

        mock.y = 'foo'
        self.assertRaises(AttributeError, set_attr)


    def test_copy(self):
        current = sys.getrecursionlimit()
        self.addCleanup(sys.setrecursionlimit, current)

        # can't use sys.maxint jako this doesn't exist w Python 3
        sys.setrecursionlimit(int(10e8))
        # this segfaults without the fix w place
        copy.copy(Mock())


    def test_subclass_with_properties(self):
        klasa SubClass(Mock):
            def _get(self):
                zwróć 3
            def _set(self, value):
                podnieś NameError('strange error')
            some_attribute = property(_get, _set)

        s = SubClass(spec_set=SubClass)
        self.assertEqual(s.some_attribute, 3)

        def test():
            s.some_attribute = 3
        self.assertRaises(NameError, test)

        def test():
            s.foo = 'bar'
        self.assertRaises(AttributeError, test)


    def test_setting_call(self):
        mock = Mock()
        def __call__(self, a):
            zwróć self._mock_call(a)

        type(mock).__call__ = __call__
        mock('one')
        mock.assert_called_with('one')

        self.assertRaises(TypeError, mock, 'one', 'two')


    def test_dir(self):
        mock = Mock()
        attrs = set(dir(mock))
        type_attrs = set([m dla m w dir(Mock) jeżeli nie m.startswith('_')])

        # all public attributes z the type are included
        self.assertEqual(set(), type_attrs - attrs)

        # creates these attributes
        mock.a, mock.b
        self.assertIn('a', dir(mock))
        self.assertIn('b', dir(mock))

        # instance attributes
        mock.c = mock.d = Nic
        self.assertIn('c', dir(mock))
        self.assertIn('d', dir(mock))

        # magic methods
        mock.__iter__ = lambda s: iter([])
        self.assertIn('__iter__', dir(mock))


    def test_dir_from_spec(self):
        mock = Mock(spec=unittest.TestCase)
        testcase_attrs = set(dir(unittest.TestCase))
        attrs = set(dir(mock))

        # all attributes z the spec are included
        self.assertEqual(set(), testcase_attrs - attrs)

        # shadow a sys attribute
        mock.version = 3
        self.assertEqual(dir(mock).count('version'), 1)


    def test_filter_dir(self):
        patcher = patch.object(mock, 'FILTER_DIR', Nieprawda)
        patcher.start()
        spróbuj:
            attrs = set(dir(Mock()))
            type_attrs = set(dir(Mock))

            # ALL attributes z the type are included
            self.assertEqual(set(), type_attrs - attrs)
        w_końcu:
            patcher.stop()


    def test_configure_mock(self):
        mock = Mock(foo='bar')
        self.assertEqual(mock.foo, 'bar')

        mock = MagicMock(foo='bar')
        self.assertEqual(mock.foo, 'bar')

        kwargs = {'side_effect': KeyError, 'foo.bar.return_value': 33,
                  'foo': MagicMock()}
        mock = Mock(**kwargs)
        self.assertRaises(KeyError, mock)
        self.assertEqual(mock.foo.bar(), 33)
        self.assertIsInstance(mock.foo, MagicMock)

        mock = Mock()
        mock.configure_mock(**kwargs)
        self.assertRaises(KeyError, mock)
        self.assertEqual(mock.foo.bar(), 33)
        self.assertIsInstance(mock.foo, MagicMock)


    def assertRaisesWithMsg(self, exception, message, func, *args, **kwargs):
        # needed because assertRaisesRegex doesn't work easily przy newlines
        spróbuj:
            func(*args, **kwargs)
        wyjąwszy:
            instance = sys.exc_info()[1]
            self.assertIsInstance(instance, exception)
        inaczej:
            self.fail('Exception %r nie podnieśd' % (exception,))

        msg = str(instance)
        self.assertEqual(msg, message)


    def test_assert_called_with_failure_message(self):
        mock = NonCallableMock()

        expected = "mock(1, '2', 3, bar='foo')"
        message = 'Expected call: %s\nNot called'
        self.assertRaisesWithMsg(
            AssertionError, message % (expected,),
            mock.assert_called_with, 1, '2', 3, bar='foo'
        )

        mock.foo(1, '2', 3, foo='foo')


        asserters = [
            mock.foo.assert_called_with, mock.foo.assert_called_once_with
        ]
        dla meth w asserters:
            actual = "foo(1, '2', 3, foo='foo')"
            expected = "foo(1, '2', 3, bar='foo')"
            message = 'Expected call: %s\nActual call: %s'
            self.assertRaisesWithMsg(
                AssertionError, message % (expected, actual),
                meth, 1, '2', 3, bar='foo'
            )

        # just kwargs
        dla meth w asserters:
            actual = "foo(1, '2', 3, foo='foo')"
            expected = "foo(bar='foo')"
            message = 'Expected call: %s\nActual call: %s'
            self.assertRaisesWithMsg(
                AssertionError, message % (expected, actual),
                meth, bar='foo'
            )

        # just args
        dla meth w asserters:
            actual = "foo(1, '2', 3, foo='foo')"
            expected = "foo(1, 2, 3)"
            message = 'Expected call: %s\nActual call: %s'
            self.assertRaisesWithMsg(
                AssertionError, message % (expected, actual),
                meth, 1, 2, 3
            )

        # empty
        dla meth w asserters:
            actual = "foo(1, '2', 3, foo='foo')"
            expected = "foo()"
            message = 'Expected call: %s\nActual call: %s'
            self.assertRaisesWithMsg(
                AssertionError, message % (expected, actual), meth
            )


    def test_mock_calls(self):
        mock = MagicMock()

        # need to do this because MagicMock.mock_calls used to just zwróć
        # a MagicMock which also returned a MagicMock when __eq__ was called
        self.assertIs(mock.mock_calls == [], Prawda)

        mock = MagicMock()
        mock()
        expected = [('', (), {})]
        self.assertEqual(mock.mock_calls, expected)

        mock.foo()
        expected.append(call.foo())
        self.assertEqual(mock.mock_calls, expected)
        # intermediate mock_calls work too
        self.assertEqual(mock.foo.mock_calls, [('', (), {})])

        mock = MagicMock()
        mock().foo(1, 2, 3, a=4, b=5)
        expected = [
            ('', (), {}), ('().foo', (1, 2, 3), dict(a=4, b=5))
        ]
        self.assertEqual(mock.mock_calls, expected)
        self.assertEqual(mock.return_value.foo.mock_calls,
                         [('', (1, 2, 3), dict(a=4, b=5))])
        self.assertEqual(mock.return_value.mock_calls,
                         [('foo', (1, 2, 3), dict(a=4, b=5))])

        mock = MagicMock()
        mock().foo.bar().baz()
        expected = [
            ('', (), {}), ('().foo.bar', (), {}),
            ('().foo.bar().baz', (), {})
        ]
        self.assertEqual(mock.mock_calls, expected)
        self.assertEqual(mock().mock_calls,
                         call.foo.bar().baz().call_list())

        dla kwargs w dict(), dict(name='bar'):
            mock = MagicMock(**kwargs)
            int(mock.foo)
            expected = [('foo.__int__', (), {})]
            self.assertEqual(mock.mock_calls, expected)

            mock = MagicMock(**kwargs)
            mock.a()()
            expected = [('a', (), {}), ('a()', (), {})]
            self.assertEqual(mock.mock_calls, expected)
            self.assertEqual(mock.a().mock_calls, [call()])

            mock = MagicMock(**kwargs)
            mock(1)(2)(3)
            self.assertEqual(mock.mock_calls, call(1)(2)(3).call_list())
            self.assertEqual(mock().mock_calls, call(2)(3).call_list())
            self.assertEqual(mock()().mock_calls, call(3).call_list())

            mock = MagicMock(**kwargs)
            mock(1)(2)(3).a.b.c(4)
            self.assertEqual(mock.mock_calls,
                             call(1)(2)(3).a.b.c(4).call_list())
            self.assertEqual(mock().mock_calls,
                             call(2)(3).a.b.c(4).call_list())
            self.assertEqual(mock()().mock_calls,
                             call(3).a.b.c(4).call_list())

            mock = MagicMock(**kwargs)
            int(mock().foo.bar().baz())
            last_call = ('().foo.bar().baz().__int__', (), {})
            self.assertEqual(mock.mock_calls[-1], last_call)
            self.assertEqual(mock().mock_calls,
                             call.foo.bar().baz().__int__().call_list())
            self.assertEqual(mock().foo.bar().mock_calls,
                             call.baz().__int__().call_list())
            self.assertEqual(mock().foo.bar().baz.mock_calls,
                             call().__int__().call_list())


    def test_subclassing(self):
        klasa Subclass(Mock):
            dalej

        mock = Subclass()
        self.assertIsInstance(mock.foo, Subclass)
        self.assertIsInstance(mock(), Subclass)

        klasa Subclass(Mock):
            def _get_child_mock(self, **kwargs):
                zwróć Mock(**kwargs)

        mock = Subclass()
        self.assertNotIsInstance(mock.foo, Subclass)
        self.assertNotIsInstance(mock(), Subclass)


    def test_arg_lists(self):
        mocks = [
            Mock(),
            MagicMock(),
            NonCallableMock(),
            NonCallableMagicMock()
        ]

        def assert_attrs(mock):
            names = 'call_args_list', 'method_calls', 'mock_calls'
            dla name w names:
                attr = getattr(mock, name)
                self.assertIsInstance(attr, _CallList)
                self.assertIsInstance(attr, list)
                self.assertEqual(attr, [])

        dla mock w mocks:
            assert_attrs(mock)

            jeżeli callable(mock):
                mock()
                mock(1, 2)
                mock(a=3)

                mock.reset_mock()
                assert_attrs(mock)

            mock.foo()
            mock.foo.bar(1, a=3)
            mock.foo(1).bar().baz(3)

            mock.reset_mock()
            assert_attrs(mock)


    def test_call_args_two_tuple(self):
        mock = Mock()
        mock(1, a=3)
        mock(2, b=4)

        self.assertEqual(len(mock.call_args), 2)
        args, kwargs = mock.call_args
        self.assertEqual(args, (2,))
        self.assertEqual(kwargs, dict(b=4))

        expected_list = [((1,), dict(a=3)), ((2,), dict(b=4))]
        dla expected, call_args w zip(expected_list, mock.call_args_list):
            self.assertEqual(len(call_args), 2)
            self.assertEqual(expected[0], call_args[0])
            self.assertEqual(expected[1], call_args[1])


    def test_side_effect_iterator(self):
        mock = Mock(side_effect=iter([1, 2, 3]))
        self.assertEqual([mock(), mock(), mock()], [1, 2, 3])
        self.assertRaises(StopIteration, mock)

        mock = MagicMock(side_effect=['a', 'b', 'c'])
        self.assertEqual([mock(), mock(), mock()], ['a', 'b', 'c'])
        self.assertRaises(StopIteration, mock)

        mock = Mock(side_effect='ghi')
        self.assertEqual([mock(), mock(), mock()], ['g', 'h', 'i'])
        self.assertRaises(StopIteration, mock)

        klasa Foo(object):
            dalej
        mock = MagicMock(side_effect=Foo)
        self.assertIsInstance(mock(), Foo)

        mock = Mock(side_effect=Iter())
        self.assertEqual([mock(), mock(), mock(), mock()],
                         ['this', 'is', 'an', 'iter'])
        self.assertRaises(StopIteration, mock)


    def test_side_effect_iterator_exceptions(self):
        dla Klass w Mock, MagicMock:
            iterable = (ValueError, 3, KeyError, 6)
            m = Klass(side_effect=iterable)
            self.assertRaises(ValueError, m)
            self.assertEqual(m(), 3)
            self.assertRaises(KeyError, m)
            self.assertEqual(m(), 6)


    def test_side_effect_setting_iterator(self):
        mock = Mock()
        mock.side_effect = iter([1, 2, 3])
        self.assertEqual([mock(), mock(), mock()], [1, 2, 3])
        self.assertRaises(StopIteration, mock)
        side_effect = mock.side_effect
        self.assertIsInstance(side_effect, type(iter([])))

        mock.side_effect = ['a', 'b', 'c']
        self.assertEqual([mock(), mock(), mock()], ['a', 'b', 'c'])
        self.assertRaises(StopIteration, mock)
        side_effect = mock.side_effect
        self.assertIsInstance(side_effect, type(iter([])))

        this_iter = Iter()
        mock.side_effect = this_iter
        self.assertEqual([mock(), mock(), mock(), mock()],
                         ['this', 'is', 'an', 'iter'])
        self.assertRaises(StopIteration, mock)
        self.assertIs(mock.side_effect, this_iter)

    def test_side_effect_iterator_default(self):
        mock = Mock(return_value=2)
        mock.side_effect = iter([1, DEFAULT])
        self.assertEqual([mock(), mock()], [1, 2])

    def test_assert_has_calls_any_order(self):
        mock = Mock()
        mock(1, 2)
        mock(a=3)
        mock(3, 4)
        mock(b=6)
        mock(b=6)

        kalls = [
            call(1, 2), ({'a': 3},),
            ((3, 4),), ((), {'a': 3}),
            ('', (1, 2)), ('', {'a': 3}),
            ('', (1, 2), {}), ('', (), {'a': 3})
        ]
        dla kall w kalls:
            mock.assert_has_calls([kall], any_order=Prawda)

        dla kall w call(1, '2'), call(b=3), call(), 3, Nic, 'foo':
            self.assertRaises(
                AssertionError, mock.assert_has_calls,
                [kall], any_order=Prawda
            )

        kall_lists = [
            [call(1, 2), call(b=6)],
            [call(3, 4), call(1, 2)],
            [call(b=6), call(b=6)],
        ]

        dla kall_list w kall_lists:
            mock.assert_has_calls(kall_list, any_order=Prawda)

        kall_lists = [
            [call(b=6), call(b=6), call(b=6)],
            [call(1, 2), call(1, 2)],
            [call(3, 4), call(1, 2), call(5, 7)],
            [call(b=6), call(3, 4), call(b=6), call(1, 2), call(b=6)],
        ]
        dla kall_list w kall_lists:
            self.assertRaises(
                AssertionError, mock.assert_has_calls,
                kall_list, any_order=Prawda
            )

    def test_assert_has_calls(self):
        kalls1 = [
                call(1, 2), ({'a': 3},),
                ((3, 4),), call(b=6),
                ('', (1,), {'b': 6}),
        ]
        kalls2 = [call.foo(), call.bar(1)]
        kalls2.extend(call.spam().baz(a=3).call_list())
        kalls2.extend(call.bam(set(), foo={}).fish([1]).call_list())

        mocks = []
        dla mock w Mock(), MagicMock():
            mock(1, 2)
            mock(a=3)
            mock(3, 4)
            mock(b=6)
            mock(1, b=6)
            mocks.append((mock, kalls1))

        mock = Mock()
        mock.foo()
        mock.bar(1)
        mock.spam().baz(a=3)
        mock.bam(set(), foo={}).fish([1])
        mocks.append((mock, kalls2))

        dla mock, kalls w mocks:
            dla i w range(len(kalls)):
                dla step w 1, 2, 3:
                    these = kalls[i:i+step]
                    mock.assert_has_calls(these)

                    jeżeli len(these) > 1:
                        self.assertRaises(
                            AssertionError,
                            mock.assert_has_calls,
                            list(reversed(these))
                        )


    def test_assert_has_calls_with_function_spec(self):
        def f(a, b, c, d=Nic):
            dalej

        mock = Mock(spec=f)

        mock(1, b=2, c=3)
        mock(4, 5, c=6, d=7)
        mock(10, 11, c=12)
        calls = [
            ('', (1, 2, 3), {}),
            ('', (4, 5, 6), {'d': 7}),
            ((10, 11, 12), {}),
            ]
        mock.assert_has_calls(calls)
        mock.assert_has_calls(calls, any_order=Prawda)
        mock.assert_has_calls(calls[1:])
        mock.assert_has_calls(calls[1:], any_order=Prawda)
        mock.assert_has_calls(calls[:-1])
        mock.assert_has_calls(calls[:-1], any_order=Prawda)
        # Reversed order
        calls = list(reversed(calls))
        przy self.assertRaises(AssertionError):
            mock.assert_has_calls(calls)
        mock.assert_has_calls(calls, any_order=Prawda)
        przy self.assertRaises(AssertionError):
            mock.assert_has_calls(calls[1:])
        mock.assert_has_calls(calls[1:], any_order=Prawda)
        przy self.assertRaises(AssertionError):
            mock.assert_has_calls(calls[:-1])
        mock.assert_has_calls(calls[:-1], any_order=Prawda)


    def test_assert_any_call(self):
        mock = Mock()
        mock(1, 2)
        mock(a=3)
        mock(1, b=6)

        mock.assert_any_call(1, 2)
        mock.assert_any_call(a=3)
        mock.assert_any_call(1, b=6)

        self.assertRaises(
            AssertionError,
            mock.assert_any_call
        )
        self.assertRaises(
            AssertionError,
            mock.assert_any_call,
            1, 3
        )
        self.assertRaises(
            AssertionError,
            mock.assert_any_call,
            a=4
        )


    def test_assert_any_call_with_function_spec(self):
        def f(a, b, c, d=Nic):
            dalej

        mock = Mock(spec=f)

        mock(1, b=2, c=3)
        mock(4, 5, c=6, d=7)
        mock.assert_any_call(1, 2, 3)
        mock.assert_any_call(a=1, b=2, c=3)
        mock.assert_any_call(4, 5, 6, 7)
        mock.assert_any_call(a=4, b=5, c=6, d=7)
        self.assertRaises(AssertionError, mock.assert_any_call,
                          1, b=3, c=2)
        # Expected call doesn't match the spec's signature
        przy self.assertRaises(AssertionError) jako cm:
            mock.assert_any_call(e=8)
        self.assertIsInstance(cm.exception.__cause__, TypeError)


    def test_mock_calls_create_autospec(self):
        def f(a, b):
            dalej
        obj = Iter()
        obj.f = f

        funcs = [
            create_autospec(f),
            create_autospec(obj).f
        ]
        dla func w funcs:
            func(1, 2)
            func(3, 4)

            self.assertEqual(
                func.mock_calls, [call(1, 2), call(3, 4)]
            )

    #Issue21222
    def test_create_autospec_with_name(self):
        m = mock.create_autospec(object(), name='sweet_func')
        self.assertIn('sweet_func', repr(m))

    #Issue21238
    def test_mock_unsafe(self):
        m = Mock()
        przy self.assertRaises(AttributeError):
            m.assert_foo_call()
        przy self.assertRaises(AttributeError):
            m.assret_foo_call()
        m = Mock(unsafe=Prawda)
        m.assert_foo_call()
        m.assret_foo_call()

    #Issue21262
    def test_assert_not_called(self):
        m = Mock()
        m.hello.assert_not_called()
        m.hello()
        przy self.assertRaises(AssertionError):
            m.hello.assert_not_called()

    #Issue21256 printout of keyword args should be w deterministic order
    def test_sorted_call_signature(self):
        m = Mock()
        m.hello(name='hello', daddy='hero')
        text = "call(daddy='hero', name='hello')"
        self.assertEqual(repr(m.hello.call_args), text)

    #Issue21270 overrides tuple methods dla mock.call objects
    def test_override_tuple_methods(self):
        c = call.count()
        i = call.index(132,'hello')
        m = Mock()
        m.count()
        m.index(132,"hello")
        self.assertEqual(m.method_calls[0], c)
        self.assertEqual(m.method_calls[1], i)

    def test_mock_add_spec(self):
        klasa _One(object):
            one = 1
        klasa _Two(object):
            two = 2
        klasa Anything(object):
            one = two = three = 'four'

        klasses = [
            Mock, MagicMock, NonCallableMock, NonCallableMagicMock
        ]
        dla Klass w list(klasses):
            klasses.append(lambda K=Klass: K(spec=Anything))
            klasses.append(lambda K=Klass: K(spec_set=Anything))

        dla Klass w klasses:
            dla kwargs w dict(), dict(spec_set=Prawda):
                mock = Klass()
                #no error
                mock.one, mock.two, mock.three

                dla One, Two w [(_One, _Two), (['one'], ['two'])]:
                    dla kwargs w dict(), dict(spec_set=Prawda):
                        mock.mock_add_spec(One, **kwargs)

                        mock.one
                        self.assertRaises(
                            AttributeError, getattr, mock, 'two'
                        )
                        self.assertRaises(
                            AttributeError, getattr, mock, 'three'
                        )
                        jeżeli 'spec_set' w kwargs:
                            self.assertRaises(
                                AttributeError, setattr, mock, 'three', Nic
                            )

                        mock.mock_add_spec(Two, **kwargs)
                        self.assertRaises(
                            AttributeError, getattr, mock, 'one'
                        )
                        mock.two
                        self.assertRaises(
                            AttributeError, getattr, mock, 'three'
                        )
                        jeżeli 'spec_set' w kwargs:
                            self.assertRaises(
                                AttributeError, setattr, mock, 'three', Nic
                            )
            # note that creating a mock, setting an instance attribute, oraz
            # *then* setting a spec doesn't work. Not the intended use case


    def test_mock_add_spec_magic_methods(self):
        dla Klass w MagicMock, NonCallableMagicMock:
            mock = Klass()
            int(mock)

            mock.mock_add_spec(object)
            self.assertRaises(TypeError, int, mock)

            mock = Klass()
            mock['foo']
            mock.__int__.return_value =4

            mock.mock_add_spec(int)
            self.assertEqual(int(mock), 4)
            self.assertRaises(TypeError, lambda: mock['foo'])


    def test_adding_child_mock(self):
        dla Klass w NonCallableMock, Mock, MagicMock, NonCallableMagicMock:
            mock = Klass()

            mock.foo = Mock()
            mock.foo()

            self.assertEqual(mock.method_calls, [call.foo()])
            self.assertEqual(mock.mock_calls, [call.foo()])

            mock = Klass()
            mock.bar = Mock(name='name')
            mock.bar()
            self.assertEqual(mock.method_calls, [])
            self.assertEqual(mock.mock_calls, [])

            # mock przy an existing _new_parent but no name
            mock = Klass()
            mock.baz = MagicMock()()
            mock.baz()
            self.assertEqual(mock.method_calls, [])
            self.assertEqual(mock.mock_calls, [])


    def test_adding_return_value_mock(self):
        dla Klass w Mock, MagicMock:
            mock = Klass()
            mock.return_value = MagicMock()

            mock()()
            self.assertEqual(mock.mock_calls, [call(), call()()])


    def test_manager_mock(self):
        klasa Foo(object):
            one = 'one'
            two = 'two'
        manager = Mock()
        p1 = patch.object(Foo, 'one')
        p2 = patch.object(Foo, 'two')

        mock_one = p1.start()
        self.addCleanup(p1.stop)
        mock_two = p2.start()
        self.addCleanup(p2.stop)

        manager.attach_mock(mock_one, 'one')
        manager.attach_mock(mock_two, 'two')

        Foo.two()
        Foo.one()

        self.assertEqual(manager.mock_calls, [call.two(), call.one()])


    def test_magic_methods_mock_calls(self):
        dla Klass w Mock, MagicMock:
            m = Klass()
            m.__int__ = Mock(return_value=3)
            m.__float__ = MagicMock(return_value=3.0)
            int(m)
            float(m)

            self.assertEqual(m.mock_calls, [call.__int__(), call.__float__()])
            self.assertEqual(m.method_calls, [])

    def test_mock_open_reuse_issue_21750(self):
        mocked_open = mock.mock_open(read_data='data')
        f1 = mocked_open('a-name')
        f1_data = f1.read()
        f2 = mocked_open('another-name')
        f2_data = f2.read()
        self.assertEqual(f1_data, f2_data)

    def test_mock_open_write(self):
        # Test exception w file writing write()
        mock_namedtemp = mock.mock_open(mock.MagicMock(name='JLV'))
        przy mock.patch('tempfile.NamedTemporaryFile', mock_namedtemp):
            mock_filehandle = mock_namedtemp.return_value
            mock_write = mock_filehandle.write
            mock_write.side_effect = OSError('Test 2 Error')
            def attempt():
                tempfile.NamedTemporaryFile().write('asd')
            self.assertRaises(OSError, attempt)

    def test_mock_open_alter_readline(self):
        mopen = mock.mock_open(read_data='foo\nbarn')
        mopen.return_value.readline.side_effect = lambda *args:'abc'
        first = mopen().readline()
        second = mopen().readline()
        self.assertEqual('abc', first)
        self.assertEqual('abc', second)

    def test_mock_parents(self):
        dla Klass w Mock, MagicMock:
            m = Klass()
            original_repr = repr(m)
            m.return_value = m
            self.assertIs(m(), m)
            self.assertEqual(repr(m), original_repr)

            m.reset_mock()
            self.assertIs(m(), m)
            self.assertEqual(repr(m), original_repr)

            m = Klass()
            m.b = m.a
            self.assertIn("name='mock.a'", repr(m.b))
            self.assertIn("name='mock.a'", repr(m.a))
            m.reset_mock()
            self.assertIn("name='mock.a'", repr(m.b))
            self.assertIn("name='mock.a'", repr(m.a))

            m = Klass()
            original_repr = repr(m)
            m.a = m()
            m.a.return_value = m

            self.assertEqual(repr(m), original_repr)
            self.assertEqual(repr(m.a()), original_repr)


    def test_attach_mock(self):
        classes = Mock, MagicMock, NonCallableMagicMock, NonCallableMock
        dla Klass w classes:
            dla Klass2 w classes:
                m = Klass()

                m2 = Klass2(name='foo')
                m.attach_mock(m2, 'bar')

                self.assertIs(m.bar, m2)
                self.assertIn("name='mock.bar'", repr(m2))

                m.bar.baz(1)
                self.assertEqual(m.mock_calls, [call.bar.baz(1)])
                self.assertEqual(m.method_calls, [call.bar.baz(1)])


    def test_attach_mock_return_value(self):
        classes = Mock, MagicMock, NonCallableMagicMock, NonCallableMock
        dla Klass w Mock, MagicMock:
            dla Klass2 w classes:
                m = Klass()

                m2 = Klass2(name='foo')
                m.attach_mock(m2, 'return_value')

                self.assertIs(m(), m2)
                self.assertIn("name='mock()'", repr(m2))

                m2.foo()
                self.assertEqual(m.mock_calls, call().foo().call_list())


    def test_attribute_deletion(self):
        dla mock w (Mock(), MagicMock(), NonCallableMagicMock(),
                     NonCallableMock()):
            self.assertPrawda(hasattr(mock, 'm'))

            usuń mock.m
            self.assertNieprawda(hasattr(mock, 'm'))

            usuń mock.f
            self.assertNieprawda(hasattr(mock, 'f'))
            self.assertRaises(AttributeError, getattr, mock, 'f')


    def test_class_assignable(self):
        dla mock w Mock(), MagicMock():
            self.assertNotIsInstance(mock, int)

            mock.__class__ = int
            self.assertIsInstance(mock, int)
            mock.foo


jeżeli __name__ == '__main__':
    unittest.main()
