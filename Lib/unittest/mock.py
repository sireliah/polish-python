# mock.py
# Test tools dla mocking oraz patching.
# Maintained by Michael Foord
# Backport dla other versions of Python available from
# http://pypi.python.org/pypi/mock

__all__ = (
    'Mock',
    'MagicMock',
    'patch',
    'sentinel',
    'DEFAULT',
    'ANY',
    'call',
    'create_autospec',
    'FILTER_DIR',
    'NonCallableMock',
    'NonCallableMagicMock',
    'mock_open',
    'PropertyMock',
)


__version__ = '1.0'


zaimportuj inspect
zaimportuj pprint
zaimportuj sys
zaimportuj builtins
z types zaimportuj ModuleType
z functools zaimportuj wraps, partial


_builtins = {name dla name w dir(builtins) jeżeli nie name.startswith('_')}

BaseExceptions = (BaseException,)
jeżeli 'java' w sys.platform:
    # jython
    zaimportuj java
    BaseExceptions = (BaseException, java.lang.Throwable)


FILTER_DIR = Prawda

# Workaround dla issue #12370
# Without this, the __class__ properties wouldn't be set correctly
_safe_super = super

def _is_instance_mock(obj):
    # can't use isinstance on Mock objects because they override __class__
    # The base klasa dla all mocks jest NonCallableMock
    zwróć issubclass(type(obj), NonCallableMock)


def _is_exception(obj):
    zwróć (
        isinstance(obj, BaseExceptions) albo
        isinstance(obj, type) oraz issubclass(obj, BaseExceptions)
    )


klasa _slotted(object):
    __slots__ = ['a']


DescriptorTypes = (
    type(_slotted.a),
    property,
)


def _get_signature_object(func, as_instance, eat_self):
    """
    Given an arbitrary, possibly callable object, try to create a suitable
    signature object.
    Return a (reduced func, signature) tuple, albo Nic.
    """
    jeżeli isinstance(func, type) oraz nie as_instance:
        # If it's a type oraz should be modelled jako a type, use __init__.
        spróbuj:
            func = func.__init__
        wyjąwszy AttributeError:
            zwróć Nic
        # Skip the `self` argument w __init__
        eat_self = Prawda
    albo_inaczej nie isinstance(func, FunctionTypes):
        # If we really want to mousuń an instance of the dalejed type,
        # __call__ should be looked up, nie __init__.
        spróbuj:
            func = func.__call__
        wyjąwszy AttributeError:
            zwróć Nic
    jeżeli eat_self:
        sig_func = partial(func, Nic)
    inaczej:
        sig_func = func
    spróbuj:
        zwróć func, inspect.signature(sig_func)
    wyjąwszy ValueError:
        # Certain callable types are nie supported by inspect.signature()
        zwróć Nic


def _check_signature(func, mock, skipfirst, instance=Nieprawda):
    sig = _get_signature_object(func, instance, skipfirst)
    jeżeli sig jest Nic:
        zwróć
    func, sig = sig
    def checksig(_mock_self, *args, **kwargs):
        sig.bind(*args, **kwargs)
    _copy_func_details(func, checksig)
    type(mock)._mock_check_sig = checksig


def _copy_func_details(func, funcopy):
    funcopy.__name__ = func.__name__
    funcopy.__doc__ = func.__doc__
    spróbuj:
        funcopy.__text_signature__ = func.__text_signature__
    wyjąwszy AttributeError:
        dalej
    # we explicitly don't copy func.__dict__ into this copy jako it would
    # expose original attributes that should be mocked
    spróbuj:
        funcopy.__module__ = func.__module__
    wyjąwszy AttributeError:
        dalej
    spróbuj:
        funcopy.__defaults__ = func.__defaults__
    wyjąwszy AttributeError:
        dalej
    spróbuj:
        funcopy.__kwdefaults__ = func.__kwdefaults__
    wyjąwszy AttributeError:
        dalej


def _callable(obj):
    jeżeli isinstance(obj, type):
        zwróć Prawda
    jeżeli getattr(obj, '__call__', Nic) jest nie Nic:
        zwróć Prawda
    zwróć Nieprawda


def _is_list(obj):
    # checks dla list albo tuples
    # XXXX badly named!
    zwróć type(obj) w (list, tuple)


def _instance_callable(obj):
    """Given an object, zwróć Prawda jeżeli the object jest callable.
    For classes, zwróć Prawda jeżeli instances would be callable."""
    jeżeli nie isinstance(obj, type):
        # already an instance
        zwróć getattr(obj, '__call__', Nic) jest nie Nic

    # *could* be broken by a klasa overriding __mro__ albo __dict__ via
    # a metaclass
    dla base w (obj,) + obj.__mro__:
        jeżeli base.__dict__.get('__call__') jest nie Nic:
            zwróć Prawda
    zwróć Nieprawda


def _set_signature(mock, original, instance=Nieprawda):
    # creates a function przy signature (*args, **kwargs) that delegates to a
    # mock. It still does signature checking by calling a lambda przy the same
    # signature jako the original.
    jeżeli nie _callable(original):
        zwróć

    skipfirst = isinstance(original, type)
    result = _get_signature_object(original, instance, skipfirst)
    jeżeli result jest Nic:
        zwróć
    func, sig = result
    def checksig(*args, **kwargs):
        sig.bind(*args, **kwargs)
    _copy_func_details(func, checksig)

    name = original.__name__
    jeżeli nie name.isidentifier():
        name = 'funcopy'
    context = {'_checksig_': checksig, 'mock': mock}
    src = """def %s(*args, **kwargs):
    _checksig_(*args, **kwargs)
    zwróć mock(*args, **kwargs)""" % name
    exec (src, context)
    funcopy = context[name]
    _setup_func(funcopy, mock)
    zwróć funcopy


def _setup_func(funcopy, mock):
    funcopy.mock = mock

    # can't use isinstance przy mocks
    jeżeli nie _is_instance_mock(mock):
        zwróć

    def assert_called_with(*args, **kwargs):
        zwróć mock.assert_called_with(*args, **kwargs)
    def assert_called_once_with(*args, **kwargs):
        zwróć mock.assert_called_once_with(*args, **kwargs)
    def assert_has_calls(*args, **kwargs):
        zwróć mock.assert_has_calls(*args, **kwargs)
    def assert_any_call(*args, **kwargs):
        zwróć mock.assert_any_call(*args, **kwargs)
    def reset_mock():
        funcopy.method_calls = _CallList()
        funcopy.mock_calls = _CallList()
        mock.reset_mock()
        ret = funcopy.return_value
        jeżeli _is_instance_mock(ret) oraz nie ret jest mock:
            ret.reset_mock()

    funcopy.called = Nieprawda
    funcopy.call_count = 0
    funcopy.call_args = Nic
    funcopy.call_args_list = _CallList()
    funcopy.method_calls = _CallList()
    funcopy.mock_calls = _CallList()

    funcopy.return_value = mock.return_value
    funcopy.side_effect = mock.side_effect
    funcopy._mock_children = mock._mock_children

    funcopy.assert_called_przy = assert_called_with
    funcopy.assert_called_once_przy = assert_called_once_with
    funcopy.assert_has_calls = assert_has_calls
    funcopy.assert_any_call = assert_any_call
    funcopy.reset_mock = reset_mock

    mock._mock_delegate = funcopy


def _is_magic(name):
    zwróć '__%s__' % name[2:-2] == name


klasa _SentinelObject(object):
    "A unique, named, sentinel object."
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        zwróć 'sentinel.%s' % self.name


klasa _Sentinel(object):
    """Access attributes to zwróć a named object, usable jako a sentinel."""
    def __init__(self):
        self._sentinels = {}

    def __getattr__(self, name):
        jeżeli name == '__bases__':
            # Without this help(unittest.mock) podnieśs an exception
            podnieś AttributeError
        zwróć self._sentinels.setdefault(name, _SentinelObject(name))


sentinel = _Sentinel()

DEFAULT = sentinel.DEFAULT
_missing = sentinel.MISSING
_deleted = sentinel.DELETED


def _copy(value):
    jeżeli type(value) w (dict, list, tuple, set):
        zwróć type(value)(value)
    zwróć value


_allowed_names = {
    'return_value', '_mock_return_value', 'side_effect',
    '_mock_side_effect', '_mock_parent', '_mock_new_parent',
    '_mock_name', '_mock_new_name'
}


def _delegating_property(name):
    _allowed_names.add(name)
    _the_name = '_mock_' + name
    def _get(self, name=name, _the_name=_the_name):
        sig = self._mock_delegate
        jeżeli sig jest Nic:
            zwróć getattr(self, _the_name)
        zwróć getattr(sig, name)
    def _set(self, value, name=name, _the_name=_the_name):
        sig = self._mock_delegate
        jeżeli sig jest Nic:
            self.__dict__[_the_name] = value
        inaczej:
            setattr(sig, name, value)

    zwróć property(_get, _set)



klasa _CallList(list):

    def __contains__(self, value):
        jeżeli nie isinstance(value, list):
            zwróć list.__contains__(self, value)
        len_value = len(value)
        len_self = len(self)
        jeżeli len_value > len_self:
            zwróć Nieprawda

        dla i w range(0, len_self - len_value + 1):
            sub_list = self[i:i+len_value]
            jeżeli sub_list == value:
                zwróć Prawda
        zwróć Nieprawda

    def __repr__(self):
        zwróć pprint.pformat(list(self))


def _check_and_set_parent(parent, value, name, new_name):
    jeżeli nie _is_instance_mock(value):
        zwróć Nieprawda
    jeżeli ((value._mock_name albo value._mock_new_name) albo
        (value._mock_parent jest nie Nic) albo
        (value._mock_new_parent jest nie Nic)):
        zwróć Nieprawda

    _parent = parent
    dopóki _parent jest nie Nic:
        # setting a mock (value) jako a child albo zwróć value of itself
        # should nie modify the mock
        jeżeli _parent jest value:
            zwróć Nieprawda
        _parent = _parent._mock_new_parent

    jeżeli new_name:
        value._mock_new_parent = parent
        value._mock_new_name = new_name
    jeżeli name:
        value._mock_parent = parent
        value._mock_name = name
    zwróć Prawda

# Internal klasa to identify jeżeli we wrapped an iterator object albo not.
klasa _MockIter(object):
    def __init__(self, obj):
        self.obj = iter(obj)
    def __iter__(self):
        zwróć self
    def __next__(self):
        zwróć next(self.obj)

klasa Base(object):
    _mock_return_value = DEFAULT
    _mock_side_effect = Nic
    def __init__(self, *args, **kwargs):
        dalej



klasa NonCallableMock(Base):
    """A non-callable version of `Mock`"""

    def __new__(cls, *args, **kw):
        # every instance has its own class
        # so we can create magic methods on the
        # klasa without stomping on other mocks
        new = type(cls.__name__, (cls,), {'__doc__': cls.__doc__})
        instance = object.__new__(new)
        zwróć instance


    def __init__(
            self, spec=Nic, wraps=Nic, name=Nic, spec_set=Nic,
            parent=Nic, _spec_state=Nic, _new_name='', _new_parent=Nic,
            _spec_as_instance=Nieprawda, _eat_self=Nic, unsafe=Nieprawda, **kwargs
        ):
        jeżeli _new_parent jest Nic:
            _new_parent = parent

        __dict__ = self.__dict__
        __dict__['_mock_parent'] = parent
        __dict__['_mock_name'] = name
        __dict__['_mock_new_name'] = _new_name
        __dict__['_mock_new_parent'] = _new_parent

        jeżeli spec_set jest nie Nic:
            spec = spec_set
            spec_set = Prawda
        jeżeli _eat_self jest Nic:
            _eat_self = parent jest nie Nic

        self._mock_add_spec(spec, spec_set, _spec_as_instance, _eat_self)

        __dict__['_mock_children'] = {}
        __dict__['_mock_wraps'] = wraps
        __dict__['_mock_delegate'] = Nic

        __dict__['_mock_called'] = Nieprawda
        __dict__['_mock_call_args'] = Nic
        __dict__['_mock_call_count'] = 0
        __dict__['_mock_call_args_list'] = _CallList()
        __dict__['_mock_mock_calls'] = _CallList()

        __dict__['method_calls'] = _CallList()
        __dict__['_mock_unsafe'] = unsafe

        jeżeli kwargs:
            self.configure_mock(**kwargs)

        _safe_super(NonCallableMock, self).__init__(
            spec, wraps, name, spec_set, parent,
            _spec_state
        )


    def attach_mock(self, mock, attribute):
        """
        Attach a mock jako an attribute of this one, replacing its name oraz
        parent. Calls to the attached mock will be recorded w the
        `method_calls` oraz `mock_calls` attributes of this one."""
        mock._mock_parent = Nic
        mock._mock_new_parent = Nic
        mock._mock_name = ''
        mock._mock_new_name = Nic

        setattr(self, attribute, mock)


    def mock_add_spec(self, spec, spec_set=Nieprawda):
        """Add a spec to a mock. `spec` can either be an object albo a
        list of strings. Only attributes on the `spec` can be fetched as
        attributes z the mock.

        If `spec_set` jest Prawda then only attributes on the spec can be set."""
        self._mock_add_spec(spec, spec_set)


    def _mock_add_spec(self, spec, spec_set, _spec_as_instance=Nieprawda,
                       _eat_self=Nieprawda):
        _spec_class = Nic
        _spec_signature = Nic

        jeżeli spec jest nie Nic oraz nie _is_list(spec):
            jeżeli isinstance(spec, type):
                _spec_class = spec
            inaczej:
                _spec_class = _get_class(spec)
            res = _get_signature_object(spec,
                                        _spec_as_instance, _eat_self)
            _spec_signature = res oraz res[1]

            spec = dir(spec)

        __dict__ = self.__dict__
        __dict__['_spec_class'] = _spec_class
        __dict__['_spec_set'] = spec_set
        __dict__['_spec_signature'] = _spec_signature
        __dict__['_mock_methods'] = spec


    def __get_return_value(self):
        ret = self._mock_return_value
        jeżeli self._mock_delegate jest nie Nic:
            ret = self._mock_delegate.return_value

        jeżeli ret jest DEFAULT:
            ret = self._get_child_mock(
                _new_parent=self, _new_name='()'
            )
            self.return_value = ret
        zwróć ret


    def __set_return_value(self, value):
        jeżeli self._mock_delegate jest nie Nic:
            self._mock_delegate.return_value = value
        inaczej:
            self._mock_return_value = value
            _check_and_set_parent(self, value, Nic, '()')

    __return_value_doc = "The value to be returned when the mock jest called."
    return_value = property(__get_return_value, __set_return_value,
                            __return_value_doc)


    @property
    def __class__(self):
        jeżeli self._spec_class jest Nic:
            zwróć type(self)
        zwróć self._spec_class

    called = _delegating_property('called')
    call_count = _delegating_property('call_count')
    call_args = _delegating_property('call_args')
    call_args_list = _delegating_property('call_args_list')
    mock_calls = _delegating_property('mock_calls')


    def __get_side_effect(self):
        delegated = self._mock_delegate
        jeżeli delegated jest Nic:
            zwróć self._mock_side_effect
        sf = delegated.side_effect
        jeżeli (sf jest nie Nic oraz nie callable(sf)
                oraz nie isinstance(sf, _MockIter) oraz nie _is_exception(sf)):
            sf = _MockIter(sf)
            delegated.side_effect = sf
        zwróć sf

    def __set_side_effect(self, value):
        value = _try_iter(value)
        delegated = self._mock_delegate
        jeżeli delegated jest Nic:
            self._mock_side_effect = value
        inaczej:
            delegated.side_effect = value

    side_effect = property(__get_side_effect, __set_side_effect)


    def reset_mock(self, visited=Nic):
        "Restore the mock object to its initial state."
        jeżeli visited jest Nic:
            visited = []
        jeżeli id(self) w visited:
            zwróć
        visited.append(id(self))

        self.called = Nieprawda
        self.call_args = Nic
        self.call_count = 0
        self.mock_calls = _CallList()
        self.call_args_list = _CallList()
        self.method_calls = _CallList()

        dla child w self._mock_children.values():
            jeżeli isinstance(child, _SpecState):
                kontynuuj
            child.reset_mock(visited)

        ret = self._mock_return_value
        jeżeli _is_instance_mock(ret) oraz ret jest nie self:
            ret.reset_mock(visited)


    def configure_mock(self, **kwargs):
        """Set attributes on the mock through keyword arguments.

        Attributes plus zwróć values oraz side effects can be set on child
        mocks using standard dot notation oraz unpacking a dictionary w the
        method call:

        >>> attrs = {'method.return_value': 3, 'other.side_effect': KeyError}
        >>> mock.configure_mock(**attrs)"""
        dla arg, val w sorted(kwargs.items(),
                               # we sort on the number of dots so that
                               # attributes are set before we set attributes on
                               # attributes
                               key=lambda enspróbuj: entry[0].count('.')):
            args = arg.split('.')
            final = args.pop()
            obj = self
            dla entry w args:
                obj = getattr(obj, entry)
            setattr(obj, final, val)


    def __getattr__(self, name):
        jeżeli name w {'_mock_methods', '_mock_unsafe'}:
            podnieś AttributeError(name)
        albo_inaczej self._mock_methods jest nie Nic:
            jeżeli name nie w self._mock_methods albo name w _all_magics:
                podnieś AttributeError("Mock object has no attribute %r" % name)
        albo_inaczej _is_magic(name):
            podnieś AttributeError(name)
        jeżeli nie self._mock_unsafe:
            jeżeli name.startswith(('assert', 'assret')):
                podnieś AttributeError(name)

        result = self._mock_children.get(name)
        jeżeli result jest _deleted:
            podnieś AttributeError(name)
        albo_inaczej result jest Nic:
            wraps = Nic
            jeżeli self._mock_wraps jest nie Nic:
                # XXXX should we get the attribute without triggering code
                # execution?
                wraps = getattr(self._mock_wraps, name)

            result = self._get_child_mock(
                parent=self, name=name, wraps=wraps, _new_name=name,
                _new_parent=self
            )
            self._mock_children[name]  = result

        albo_inaczej isinstance(result, _SpecState):
            result = create_autospec(
                result.spec, result.spec_set, result.instance,
                result.parent, result.name
            )
            self._mock_children[name]  = result

        zwróć result


    def __repr__(self):
        _name_list = [self._mock_new_name]
        _parent = self._mock_new_parent
        last = self

        dot = '.'
        jeżeli _name_list == ['()']:
            dot = ''
        seen = set()
        dopóki _parent jest nie Nic:
            last = _parent

            _name_list.append(_parent._mock_new_name + dot)
            dot = '.'
            jeżeli _parent._mock_new_name == '()':
                dot = ''

            _parent = _parent._mock_new_parent

            # use ids here so jako nie to call __hash__ on the mocks
            jeżeli id(_parent) w seen:
                przerwij
            seen.add(id(_parent))

        _name_list = list(reversed(_name_list))
        _first = last._mock_name albo 'mock'
        jeżeli len(_name_list) > 1:
            jeżeli _name_list[1] nie w ('()', '().'):
                _first += '.'
        _name_list[0] = _first
        name = ''.join(_name_list)

        name_string = ''
        jeżeli name nie w ('mock', 'mock.'):
            name_string = ' name=%r' % name

        spec_string = ''
        jeżeli self._spec_class jest nie Nic:
            spec_string = ' spec=%r'
            jeżeli self._spec_set:
                spec_string = ' spec_set=%r'
            spec_string = spec_string % self._spec_class.__name__
        zwróć "<%s%s%s id='%s'>" % (
            type(self).__name__,
            name_string,
            spec_string,
            id(self)
        )


    def __dir__(self):
        """Filter the output of `dir(mock)` to only useful members."""
        jeżeli nie FILTER_DIR:
            zwróć object.__dir__(self)

        extras = self._mock_methods albo []
        from_type = dir(type(self))
        from_dict = list(self.__dict__)

        from_type = [e dla e w from_type jeżeli nie e.startswith('_')]
        from_dict = [e dla e w from_dict jeżeli nie e.startswith('_') albo
                     _is_magic(e)]
        zwróć sorted(set(extras + from_type + from_dict +
                          list(self._mock_children)))


    def __setattr__(self, name, value):
        jeżeli name w _allowed_names:
            # property setters go through here
            zwróć object.__setattr__(self, name, value)
        albo_inaczej (self._spec_set oraz self._mock_methods jest nie Nic oraz
            name nie w self._mock_methods oraz
            name nie w self.__dict__):
            podnieś AttributeError("Mock object has no attribute '%s'" % name)
        albo_inaczej name w _unsupported_magics:
            msg = 'Attempting to set unsupported magic method %r.' % name
            podnieś AttributeError(msg)
        albo_inaczej name w _all_magics:
            jeżeli self._mock_methods jest nie Nic oraz name nie w self._mock_methods:
                podnieś AttributeError("Mock object has no attribute '%s'" % name)

            jeżeli nie _is_instance_mock(value):
                setattr(type(self), name, _get_method(name, value))
                original = value
                value = lambda *args, **kw: original(self, *args, **kw)
            inaczej:
                # only set _new_name oraz nie name so that mock_calls jest tracked
                # but nie method calls
                _check_and_set_parent(self, value, Nic, name)
                setattr(type(self), name, value)
                self._mock_children[name] = value
        albo_inaczej name == '__class__':
            self._spec_class = value
            zwróć
        inaczej:
            jeżeli _check_and_set_parent(self, value, name, name):
                self._mock_children[name] = value
        zwróć object.__setattr__(self, name, value)


    def __delattr__(self, name):
        jeżeli name w _all_magics oraz name w type(self).__dict__:
            delattr(type(self), name)
            jeżeli name nie w self.__dict__:
                # dla magic methods that are still MagicProxy objects oraz
                # nie set on the instance itself
                zwróć

        jeżeli name w self.__dict__:
            object.__delattr__(self, name)

        obj = self._mock_children.get(name, _missing)
        jeżeli obj jest _deleted:
            podnieś AttributeError(name)
        jeżeli obj jest nie _missing:
            usuń self._mock_children[name]
        self._mock_children[name] = _deleted


    def _format_mock_call_signature(self, args, kwargs):
        name = self._mock_name albo 'mock'
        zwróć _format_call_signature(name, args, kwargs)


    def _format_mock_failure_message(self, args, kwargs):
        message = 'Expected call: %s\nActual call: %s'
        expected_string = self._format_mock_call_signature(args, kwargs)
        call_args = self.call_args
        jeżeli len(call_args) == 3:
            call_args = call_args[1:]
        actual_string = self._format_mock_call_signature(*call_args)
        zwróć message % (expected_string, actual_string)


    def _call_matcher(self, _call):
        """
        Given a call (or simply a (args, kwargs) tuple), zwróć a
        comparison key suitable dla matching przy other calls.
        This jest a best effort method which relies on the spec's signature,
        jeżeli available, albo falls back on the arguments themselves.
        """
        sig = self._spec_signature
        jeżeli sig jest nie Nic:
            jeżeli len(_call) == 2:
                name = ''
                args, kwargs = _call
            inaczej:
                name, args, kwargs = _call
            spróbuj:
                zwróć name, sig.bind(*args, **kwargs)
            wyjąwszy TypeError jako e:
                zwróć e.with_traceback(Nic)
        inaczej:
            zwróć _call

    def assert_not_called(_mock_self):
        """assert that the mock was never called.
        """
        self = _mock_self
        jeżeli self.call_count != 0:
            msg = ("Expected '%s' to nie have been called. Called %s times." %
                   (self._mock_name albo 'mock', self.call_count))
            podnieś AssertionError(msg)

    def assert_called_with(_mock_self, *args, **kwargs):
        """assert that the mock was called przy the specified arguments.

        Raises an AssertionError jeżeli the args oraz keyword args dalejed w are
        different to the last call to the mock."""
        self = _mock_self
        jeżeli self.call_args jest Nic:
            expected = self._format_mock_call_signature(args, kwargs)
            podnieś AssertionError('Expected call: %s\nNot called' % (expected,))

        def _error_message():
            msg = self._format_mock_failure_message(args, kwargs)
            zwróć msg
        expected = self._call_matcher((args, kwargs))
        actual = self._call_matcher(self.call_args)
        jeżeli expected != actual:
            cause = expected jeżeli isinstance(expected, Exception) inaczej Nic
            podnieś AssertionError(_error_message()) z cause


    def assert_called_once_with(_mock_self, *args, **kwargs):
        """assert that the mock was called exactly once oraz przy the specified
        arguments."""
        self = _mock_self
        jeżeli nie self.call_count == 1:
            msg = ("Expected '%s' to be called once. Called %s times." %
                   (self._mock_name albo 'mock', self.call_count))
            podnieś AssertionError(msg)
        zwróć self.assert_called_with(*args, **kwargs)


    def assert_has_calls(self, calls, any_order=Nieprawda):
        """assert the mock has been called przy the specified calls.
        The `mock_calls` list jest checked dla the calls.

        If `any_order` jest Nieprawda (the default) then the calls must be
        sequential. There can be extra calls before albo after the
        specified calls.

        If `any_order` jest Prawda then the calls can be w any order, but
        they must all appear w `mock_calls`."""
        expected = [self._call_matcher(c) dla c w calls]
        cause = expected jeżeli isinstance(expected, Exception) inaczej Nic
        all_calls = _CallList(self._call_matcher(c) dla c w self.mock_calls)
        jeżeli nie any_order:
            jeżeli expected nie w all_calls:
                podnieś AssertionError(
                    'Calls nie found.\nExpected: %r\n'
                    'Actual: %r' % (calls, self.mock_calls)
                ) z cause
            zwróć

        all_calls = list(all_calls)

        not_found = []
        dla kall w expected:
            spróbuj:
                all_calls.remove(kall)
            wyjąwszy ValueError:
                not_found.append(kall)
        jeżeli not_found:
            podnieś AssertionError(
                '%r nie all found w call list' % (tuple(nie_found),)
            ) z cause


    def assert_any_call(self, *args, **kwargs):
        """assert the mock has been called przy the specified arguments.

        The assert dalejes jeżeli the mock has *ever* been called, unlike
        `assert_called_with` oraz `assert_called_once_with` that only dalej if
        the call jest the most recent one."""
        expected = self._call_matcher((args, kwargs))
        actual = [self._call_matcher(c) dla c w self.call_args_list]
        jeżeli expected nie w actual:
            cause = expected jeżeli isinstance(expected, Exception) inaczej Nic
            expected_string = self._format_mock_call_signature(args, kwargs)
            podnieś AssertionError(
                '%s call nie found' % expected_string
            ) z cause


    def _get_child_mock(self, **kw):
        """Create the child mocks dla attributes oraz zwróć value.
        By default child mocks will be the same type jako the parent.
        Subclasses of Mock may want to override this to customize the way
        child mocks are made.

        For non-callable mocks the callable variant will be used (rather than
        any custom subclass)."""
        _type = type(self)
        jeżeli nie issubclass(_type, CallableMixin):
            jeżeli issubclass(_type, NonCallableMagicMock):
                klass = MagicMock
            albo_inaczej issubclass(_type, NonCallableMock) :
                klass = Mock
        inaczej:
            klass = _type.__mro__[1]
        zwróć klass(**kw)



def _try_iter(obj):
    jeżeli obj jest Nic:
        zwróć obj
    jeżeli _is_exception(obj):
        zwróć obj
    jeżeli _callable(obj):
        zwróć obj
    spróbuj:
        zwróć iter(obj)
    wyjąwszy TypeError:
        # XXXX backwards compatibility
        # but this will blow up on first call - so maybe we should fail early?
        zwróć obj



klasa CallableMixin(Base):

    def __init__(self, spec=Nic, side_effect=Nic, return_value=DEFAULT,
                 wraps=Nic, name=Nic, spec_set=Nic, parent=Nic,
                 _spec_state=Nic, _new_name='', _new_parent=Nic, **kwargs):
        self.__dict__['_mock_return_value'] = return_value

        _safe_super(CallableMixin, self).__init__(
            spec, wraps, name, spec_set, parent,
            _spec_state, _new_name, _new_parent, **kwargs
        )

        self.side_effect = side_effect


    def _mock_check_sig(self, *args, **kwargs):
        # stub method that can be replaced przy one przy a specific signature
        dalej


    def __call__(_mock_self, *args, **kwargs):
        # can't use self in-case a function / method we are mocking uses self
        # w the signature
        _mock_self._mock_check_sig(*args, **kwargs)
        zwróć _mock_self._mock_call(*args, **kwargs)


    def _mock_call(_mock_self, *args, **kwargs):
        self = _mock_self
        self.called = Prawda
        self.call_count += 1
        _new_name = self._mock_new_name
        _new_parent = self._mock_new_parent

        _call = _Call((args, kwargs), two=Prawda)
        self.call_args = _call
        self.call_args_list.append(_call)
        self.mock_calls.append(_Call(('', args, kwargs)))

        seen = set()
        skip_next_dot = _new_name == '()'
        do_method_calls = self._mock_parent jest nie Nic
        name = self._mock_name
        dopóki _new_parent jest nie Nic:
            this_mock_call = _Call((_new_name, args, kwargs))
            jeżeli _new_parent._mock_new_name:
                dot = '.'
                jeżeli skip_next_dot:
                    dot = ''

                skip_next_dot = Nieprawda
                jeżeli _new_parent._mock_new_name == '()':
                    skip_next_dot = Prawda

                _new_name = _new_parent._mock_new_name + dot + _new_name

            jeżeli do_method_calls:
                jeżeli _new_name == name:
                    this_method_call = this_mock_call
                inaczej:
                    this_method_call = _Call((name, args, kwargs))
                _new_parent.method_calls.append(this_method_call)

                do_method_calls = _new_parent._mock_parent jest nie Nic
                jeżeli do_method_calls:
                    name = _new_parent._mock_name + '.' + name

            _new_parent.mock_calls.append(this_mock_call)
            _new_parent = _new_parent._mock_new_parent

            # use ids here so jako nie to call __hash__ on the mocks
            _new_parent_id = id(_new_parent)
            jeżeli _new_parent_id w seen:
                przerwij
            seen.add(_new_parent_id)

        ret_val = DEFAULT
        effect = self.side_effect
        jeżeli effect jest nie Nic:
            jeżeli _is_exception(effect):
                podnieś effect

            jeżeli nie _callable(effect):
                result = next(effect)
                jeżeli _is_exception(result):
                    podnieś result
                jeżeli result jest DEFAULT:
                    result = self.return_value
                zwróć result

            ret_val = effect(*args, **kwargs)

        jeżeli (self._mock_wraps jest nie Nic oraz
             self._mock_return_value jest DEFAULT):
            zwróć self._mock_wraps(*args, **kwargs)
        jeżeli ret_val jest DEFAULT:
            ret_val = self.return_value
        zwróć ret_val



klasa Mock(CallableMixin, NonCallableMock):
    """
    Create a new `Mock` object. `Mock` takes several optional arguments
    that specify the behaviour of the Mock object:

    * `spec`: This can be either a list of strings albo an existing object (a
      klasa albo instance) that acts jako the specification dla the mock object. If
      you dalej w an object then a list of strings jest formed by calling dir on
      the object (excluding unsupported magic attributes oraz methods). Accessing
      any attribute nie w this list will podnieś an `AttributeError`.

      If `spec` jest an object (rather than a list of strings) then
      `mock.__class__` returns the klasa of the spec object. This allows mocks
      to dalej `isinstance` tests.

    * `spec_set`: A stricter variant of `spec`. If used, attempting to *set*
      albo get an attribute on the mock that isn't on the object dalejed as
      `spec_set` will podnieś an `AttributeError`.

    * `side_effect`: A function to be called whenever the Mock jest called. See
      the `side_effect` attribute. Useful dla raising exceptions albo
      dynamically changing zwróć values. The function jest called przy the same
      arguments jako the mock, oraz unless it returns `DEFAULT`, the zwróć
      value of this function jest used jako the zwróć value.

      If `side_effect` jest an iterable then each call to the mock will zwróć
      the next value z the iterable. If any of the members of the iterable
      are exceptions they will be podnieśd instead of returned.

    * `return_value`: The value returned when the mock jest called. By default
      this jest a new Mock (created on first access). See the
      `return_value` attribute.

    * `wraps`: Item dla the mock object to wrap. If `wraps` jest nie Nic then
      calling the Mock will dalej the call through to the wrapped object
      (returning the real result). Attribute access on the mock will zwróć a
      Mock object that wraps the corresponding attribute of the wrapped object
      (so attempting to access an attribute that doesn't exist will podnieś an
      `AttributeError`).

      If the mock has an explicit `return_value` set then calls are nie dalejed
      to the wrapped object oraz the `return_value` jest returned instead.

    * `name`: If the mock has a name then it will be used w the repr of the
      mock. This can be useful dla debugging. The name jest propagated to child
      mocks.

    Mocks can also be called przy arbitrary keyword arguments. These will be
    used to set attributes on the mock after it jest created.
    """



def _dot_lookup(thing, comp, import_path):
    spróbuj:
        zwróć getattr(thing, comp)
    wyjąwszy AttributeError:
        __import__(import_path)
        zwróć getattr(thing, comp)


def _importer(target):
    components = target.split('.')
    import_path = components.pop(0)
    thing = __import__(import_path)

    dla comp w components:
        import_path += ".%s" % comp
        thing = _dot_lookup(thing, comp, import_path)
    zwróć thing


def _is_started(patcher):
    # XXXX horrible
    zwróć hasattr(patcher, 'is_local')


klasa _patch(object):

    attribute_name = Nic
    _active_patches = []

    def __init__(
            self, getter, attribute, new, spec, create,
            spec_set, autospec, new_callable, kwargs
        ):
        jeżeli new_callable jest nie Nic:
            jeżeli new jest nie DEFAULT:
                podnieś ValueError(
                    "Cannot use 'new' oraz 'new_callable' together"
                )
            jeżeli autospec jest nie Nic:
                podnieś ValueError(
                    "Cannot use 'autospec' oraz 'new_callable' together"
                )

        self.getter = getter
        self.attribute = attribute
        self.new = new
        self.new_callable = new_callable
        self.spec = spec
        self.create = create
        self.has_local = Nieprawda
        self.spec_set = spec_set
        self.autospec = autospec
        self.kwargs = kwargs
        self.additional_patchers = []


    def copy(self):
        patcher = _patch(
            self.getter, self.attribute, self.new, self.spec,
            self.create, self.spec_set,
            self.autospec, self.new_callable, self.kwargs
        )
        patcher.attribute_name = self.attribute_name
        patcher.additional_patchers = [
            p.copy() dla p w self.additional_patchers
        ]
        zwróć patcher


    def __call__(self, func):
        jeżeli isinstance(func, type):
            zwróć self.decorate_class(func)
        zwróć self.decorate_callable(func)


    def decorate_class(self, klass):
        dla attr w dir(klass):
            jeżeli nie attr.startswith(patch.TEST_PREFIX):
                kontynuuj

            attr_value = getattr(klass, attr)
            jeżeli nie hasattr(attr_value, "__call__"):
                kontynuuj

            patcher = self.copy()
            setattr(klass, attr, patcher(attr_value))
        zwróć klass


    def decorate_callable(self, func):
        jeżeli hasattr(func, 'patchings'):
            func.patchings.append(self)
            zwróć func

        @wraps(func)
        def patched(*args, **keywargs):
            extra_args = []
            entered_patchers = []

            exc_info = tuple()
            spróbuj:
                dla patching w patched.patchings:
                    arg = patching.__enter__()
                    entered_patchers.append(patching)
                    jeżeli patching.attribute_name jest nie Nic:
                        keywargs.update(arg)
                    albo_inaczej patching.new jest DEFAULT:
                        extra_args.append(arg)

                args += tuple(extra_args)
                zwróć func(*args, **keywargs)
            wyjąwszy:
                jeżeli (patching nie w entered_patchers oraz
                    _is_started(patching)):
                    # the patcher may have been started, but an exception
                    # podnieśd whilst entering one of its additional_patchers
                    entered_patchers.append(patching)
                # Pass the exception to __exit__
                exc_info = sys.exc_info()
                # re-raise the exception
                podnieś
            w_końcu:
                dla patching w reversed(entered_patchers):
                    patching.__exit__(*exc_info)

        patched.patchings = [self]
        zwróć patched


    def get_original(self):
        target = self.getter()
        name = self.attribute

        original = DEFAULT
        local = Nieprawda

        spróbuj:
            original = target.__dict__[name]
        wyjąwszy (AttributeError, KeyError):
            original = getattr(target, name, DEFAULT)
        inaczej:
            local = Prawda

        jeżeli name w _builtins oraz isinstance(target, ModuleType):
            self.create = Prawda

        jeżeli nie self.create oraz original jest DEFAULT:
            podnieś AttributeError(
                "%s does nie have the attribute %r" % (target, name)
            )
        zwróć original, local


    def __enter__(self):
        """Perform the patch."""
        new, spec, spec_set = self.new, self.spec, self.spec_set
        autospec, kwargs = self.autospec, self.kwargs
        new_callable = self.new_callable
        self.target = self.getter()

        # normalise Nieprawda to Nic
        jeżeli spec jest Nieprawda:
            spec = Nic
        jeżeli spec_set jest Nieprawda:
            spec_set = Nic
        jeżeli autospec jest Nieprawda:
            autospec = Nic

        jeżeli spec jest nie Nic oraz autospec jest nie Nic:
            podnieś TypeError("Can't specify spec oraz autospec")
        jeżeli ((spec jest nie Nic albo autospec jest nie Nic) oraz
            spec_set nie w (Prawda, Nic)):
            podnieś TypeError("Can't provide explicit spec_set *and* spec albo autospec")

        original, local = self.get_original()

        jeżeli new jest DEFAULT oraz autospec jest Nic:
            inherit = Nieprawda
            jeżeli spec jest Prawda:
                # set spec to the object we are replacing
                spec = original
                jeżeli spec_set jest Prawda:
                    spec_set = original
                    spec = Nic
            albo_inaczej spec jest nie Nic:
                jeżeli spec_set jest Prawda:
                    spec_set = spec
                    spec = Nic
            albo_inaczej spec_set jest Prawda:
                spec_set = original

            jeżeli spec jest nie Nic albo spec_set jest nie Nic:
                jeżeli original jest DEFAULT:
                    podnieś TypeError("Can't use 'spec' przy create=Prawda")
                jeżeli isinstance(original, type):
                    # If we're patching out a klasa oraz there jest a spec
                    inherit = Prawda

            Klass = MagicMock
            _kwargs = {}
            jeżeli new_callable jest nie Nic:
                Klass = new_callable
            albo_inaczej spec jest nie Nic albo spec_set jest nie Nic:
                this_spec = spec
                jeżeli spec_set jest nie Nic:
                    this_spec = spec_set
                jeżeli _is_list(this_spec):
                    not_callable = '__call__' nie w this_spec
                inaczej:
                    not_callable = nie callable(this_spec)
                jeżeli not_callable:
                    Klass = NonCallableMagicMock

            jeżeli spec jest nie Nic:
                _kwargs['spec'] = spec
            jeżeli spec_set jest nie Nic:
                _kwargs['spec_set'] = spec_set

            # add a name to mocks
            jeżeli (isinstance(Klass, type) oraz
                issubclass(Klass, NonCallableMock) oraz self.attribute):
                _kwargs['name'] = self.attribute

            _kwargs.update(kwargs)
            new = Klass(**_kwargs)

            jeżeli inherit oraz _is_instance_mock(new):
                # we can only tell jeżeli the instance should be callable jeżeli the
                # spec jest nie a list
                this_spec = spec
                jeżeli spec_set jest nie Nic:
                    this_spec = spec_set
                jeżeli (nie _is_list(this_spec) oraz nie
                    _instance_callable(this_spec)):
                    Klass = NonCallableMagicMock

                _kwargs.pop('name')
                new.return_value = Klass(_new_parent=new, _new_name='()',
                                         **_kwargs)
        albo_inaczej autospec jest nie Nic:
            # spec jest ignored, new *must* be default, spec_set jest treated
            # jako a boolean. Should we check spec jest nie Nic oraz that spec_set
            # jest a bool?
            jeżeli new jest nie DEFAULT:
                podnieś TypeError(
                    "autospec creates the mock dla you. Can't specify "
                    "autospec oraz new."
                )
            jeżeli original jest DEFAULT:
                podnieś TypeError("Can't use 'autospec' przy create=Prawda")
            spec_set = bool(spec_set)
            jeżeli autospec jest Prawda:
                autospec = original

            new = create_autospec(autospec, spec_set=spec_set,
                                  _name=self.attribute, **kwargs)
        albo_inaczej kwargs:
            # can't set keyword args when we aren't creating the mock
            # XXXX If new jest a Mock we could call new.configure_mock(**kwargs)
            podnieś TypeError("Can't dalej kwargs to a mock we aren't creating")

        new_attr = new

        self.temp_original = original
        self.is_local = local
        setattr(self.target, self.attribute, new_attr)
        jeżeli self.attribute_name jest nie Nic:
            extra_args = {}
            jeżeli self.new jest DEFAULT:
                extra_args[self.attribute_name] =  new
            dla patching w self.additional_patchers:
                arg = patching.__enter__()
                jeżeli patching.new jest DEFAULT:
                    extra_args.update(arg)
            zwróć extra_args

        zwróć new


    def __exit__(self, *exc_info):
        """Undo the patch."""
        jeżeli nie _is_started(self):
            podnieś RuntimeError('stop called on unstarted patcher')

        jeżeli self.is_local oraz self.temp_original jest nie DEFAULT:
            setattr(self.target, self.attribute, self.temp_original)
        inaczej:
            delattr(self.target, self.attribute)
            jeżeli nie self.create oraz nie hasattr(self.target, self.attribute):
                # needed dla proxy objects like django settings
                setattr(self.target, self.attribute, self.temp_original)

        usuń self.temp_original
        usuń self.is_local
        usuń self.target
        dla patcher w reversed(self.additional_patchers):
            jeżeli _is_started(patcher):
                patcher.__exit__(*exc_info)


    def start(self):
        """Activate a patch, returning any created mock."""
        result = self.__enter__()
        self._active_patches.append(self)
        zwróć result


    def stop(self):
        """Stop an active patch."""
        spróbuj:
            self._active_patches.remove(self)
        wyjąwszy ValueError:
            # If the patch hasn't been started this will fail
            dalej

        zwróć self.__exit__()



def _get_target(target):
    spróbuj:
        target, attribute = target.rsplit('.', 1)
    wyjąwszy (TypeError, ValueError):
        podnieś TypeError("Need a valid target to patch. You supplied: %r" %
                        (target,))
    getter = lambda: _importer(target)
    zwróć getter, attribute


def _patch_object(
        target, attribute, new=DEFAULT, spec=Nic,
        create=Nieprawda, spec_set=Nic, autospec=Nic,
        new_callable=Nic, **kwargs
    ):
    """
    patch the named member (`attribute`) on an object (`target`) przy a mock
    object.

    `patch.object` can be used jako a decorator, klasa decorator albo a context
    manager. Arguments `new`, `spec`, `create`, `spec_set`,
    `autospec` oraz `new_callable` have the same meaning jako dla `patch`. Like
    `patch`, `patch.object` takes arbitrary keyword arguments dla configuring
    the mock object it creates.

    When used jako a klasa decorator `patch.object` honours `patch.TEST_PREFIX`
    dla choosing which methods to wrap.
    """
    getter = lambda: target
    zwróć _patch(
        getter, attribute, new, spec, create,
        spec_set, autospec, new_callable, kwargs
    )


def _patch_multiple(target, spec=Nic, create=Nieprawda, spec_set=Nic,
                    autospec=Nic, new_callable=Nic, **kwargs):
    """Perform multiple patches w a single call. It takes the object to be
    patched (either jako an object albo a string to fetch the object by importing)
    oraz keyword arguments dla the patches::

        przy patch.multiple(settings, FIRST_PATCH='one', SECOND_PATCH='two'):
            ...

    Use `DEFAULT` jako the value jeżeli you want `patch.multiple` to create
    mocks dla you. In this case the created mocks are dalejed into a decorated
    function by keyword, oraz a dictionary jest returned when `patch.multiple` jest
    used jako a context manager.

    `patch.multiple` can be used jako a decorator, klasa decorator albo a context
    manager. The arguments `spec`, `spec_set`, `create`,
    `autospec` oraz `new_callable` have the same meaning jako dla `patch`. These
    arguments will be applied to *all* patches done by `patch.multiple`.

    When used jako a klasa decorator `patch.multiple` honours `patch.TEST_PREFIX`
    dla choosing which methods to wrap.
    """
    jeżeli type(target) jest str:
        getter = lambda: _importer(target)
    inaczej:
        getter = lambda: target

    jeżeli nie kwargs:
        podnieś ValueError(
            'Must supply at least one keyword argument przy patch.multiple'
        )
    # need to wrap w a list dla python 3, where items jest a view
    items = list(kwargs.items())
    attribute, new = items[0]
    patcher = _patch(
        getter, attribute, new, spec, create, spec_set,
        autospec, new_callable, {}
    )
    patcher.attribute_name = attribute
    dla attribute, new w items[1:]:
        this_patcher = _patch(
            getter, attribute, new, spec, create, spec_set,
            autospec, new_callable, {}
        )
        this_patcher.attribute_name = attribute
        patcher.additional_patchers.append(this_patcher)
    zwróć patcher


def patch(
        target, new=DEFAULT, spec=Nic, create=Nieprawda,
        spec_set=Nic, autospec=Nic, new_callable=Nic, **kwargs
    ):
    """
    `patch` acts jako a function decorator, klasa decorator albo a context
    manager. Inside the body of the function albo przy statement, the `target`
    jest patched przy a `new` object. When the function/przy statement exits
    the patch jest undone.

    If `new` jest omitted, then the target jest replaced przy a
    `MagicMock`. If `patch` jest used jako a decorator oraz `new` jest
    omitted, the created mock jest dalejed w jako an extra argument to the
    decorated function. If `patch` jest used jako a context manager the created
    mock jest returned by the context manager.

    `target` should be a string w the form `'package.module.ClassName'`. The
    `target` jest imported oraz the specified object replaced przy the `new`
    object, so the `target` must be importable z the environment you are
    calling `patch` from. The target jest imported when the decorated function
    jest executed, nie at decoration time.

    The `spec` oraz `spec_set` keyword arguments are dalejed to the `MagicMock`
    jeżeli patch jest creating one dla you.

    In addition you can dalej `spec=Prawda` albo `spec_set=Prawda`, which causes
    patch to dalej w the object being mocked jako the spec/spec_set object.

    `new_callable` allows you to specify a different class, albo callable object,
    that will be called to create the `new` object. By default `MagicMock` jest
    used.

    A more powerful form of `spec` jest `autospec`. If you set `autospec=Prawda`
    then the mock will be created przy a spec z the object being replaced.
    All attributes of the mock will also have the spec of the corresponding
    attribute of the object being replaced. Methods oraz functions being
    mocked will have their arguments checked oraz will podnieś a `TypeError` if
    they are called przy the wrong signature. For mocks replacing a class,
    their zwróć value (the 'instance') will have the same spec jako the class.

    Instead of `autospec=Prawda` you can dalej `autospec=some_object` to use an
    arbitrary object jako the spec instead of the one being replaced.

    By default `patch` will fail to replace attributes that don't exist. If
    you dalej w `create=Prawda`, oraz the attribute doesn't exist, patch will
    create the attribute dla you when the patched function jest called, oraz
    delete it again afterwards. This jest useful dla writing tests against
    attributes that your production code creates at runtime. It jest off by
    default because it can be dangerous. With it switched on you can write
    dalejing tests against APIs that don't actually exist!

    Patch can be used jako a `TestCase` klasa decorator. It works by
    decorating each test method w the class. This reduces the boilerplate
    code when your test methods share a common patchings set. `patch` finds
    tests by looking dla method names that start przy `patch.TEST_PREFIX`.
    By default this jest `test`, which matches the way `unittest` finds tests.
    You can specify an alternative prefix by setting `patch.TEST_PREFIX`.

    Patch can be used jako a context manager, przy the przy statement. Here the
    patching applies to the indented block after the przy statement. If you
    use "as" then the patched object will be bound to the name after the
    "as"; very useful jeżeli `patch` jest creating a mock object dla you.

    `patch` takes arbitrary keyword arguments. These will be dalejed to
    the `Mock` (or `new_callable`) on construction.

    `patch.dict(...)`, `patch.multiple(...)` oraz `patch.object(...)` are
    available dla alternate use-cases.
    """
    getter, attribute = _get_target(target)
    zwróć _patch(
        getter, attribute, new, spec, create,
        spec_set, autospec, new_callable, kwargs
    )


klasa _patch_dict(object):
    """
    Patch a dictionary, albo dictionary like object, oraz restore the dictionary
    to its original state after the test.

    `in_dict` can be a dictionary albo a mapping like container. If it jest a
    mapping then it must at least support getting, setting oraz deleting items
    plus iterating over keys.

    `in_dict` can also be a string specifying the name of the dictionary, which
    will then be fetched by importing it.

    `values` can be a dictionary of values to set w the dictionary. `values`
    can also be an iterable of `(key, value)` pairs.

    If `clear` jest Prawda then the dictionary will be cleared before the new
    values are set.

    `patch.dict` can also be called przy arbitrary keyword arguments to set
    values w the dictionary::

        przy patch.dict('sys.modules', mymodule=Mock(), other_module=Mock()):
            ...

    `patch.dict` can be used jako a context manager, decorator albo class
    decorator. When used jako a klasa decorator `patch.dict` honours
    `patch.TEST_PREFIX` dla choosing which methods to wrap.
    """

    def __init__(self, in_dict, values=(), clear=Nieprawda, **kwargs):
        jeżeli isinstance(in_dict, str):
            in_dict = _importer(in_dict)
        self.in_dict = in_dict
        # support any argument supported by dict(...) constructor
        self.values = dict(values)
        self.values.update(kwargs)
        self.clear = clear
        self._original = Nic


    def __call__(self, f):
        jeżeli isinstance(f, type):
            zwróć self.decorate_class(f)
        @wraps(f)
        def _inner(*args, **kw):
            self._patch_dict()
            spróbuj:
                zwróć f(*args, **kw)
            w_końcu:
                self._unpatch_dict()

        zwróć _inner


    def decorate_class(self, klass):
        dla attr w dir(klass):
            attr_value = getattr(klass, attr)
            jeżeli (attr.startswith(patch.TEST_PREFIX) oraz
                 hasattr(attr_value, "__call__")):
                decorator = _patch_dict(self.in_dict, self.values, self.clear)
                decorated = decorator(attr_value)
                setattr(klass, attr, decorated)
        zwróć klass


    def __enter__(self):
        """Patch the dict."""
        self._patch_dict()


    def _patch_dict(self):
        values = self.values
        in_dict = self.in_dict
        clear = self.clear

        spróbuj:
            original = in_dict.copy()
        wyjąwszy AttributeError:
            # dict like object przy no copy method
            # must support iteration over keys
            original = {}
            dla key w in_dict:
                original[key] = in_dict[key]
        self._original = original

        jeżeli clear:
            _clear_dict(in_dict)

        spróbuj:
            in_dict.update(values)
        wyjąwszy AttributeError:
            # dict like object przy no update method
            dla key w values:
                in_dict[key] = values[key]


    def _unpatch_dict(self):
        in_dict = self.in_dict
        original = self._original

        _clear_dict(in_dict)

        spróbuj:
            in_dict.update(original)
        wyjąwszy AttributeError:
            dla key w original:
                in_dict[key] = original[key]


    def __exit__(self, *args):
        """Unpatch the dict."""
        self._unpatch_dict()
        zwróć Nieprawda

    start = __enter__
    stop = __exit__


def _clear_dict(in_dict):
    spróbuj:
        in_dict.clear()
    wyjąwszy AttributeError:
        keys = list(in_dict)
        dla key w keys:
            usuń in_dict[key]


def _patch_stopall():
    """Stop all active patches. LIFO to unroll nested patches."""
    dla patch w reversed(_patch._active_patches):
        patch.stop()


patch.object = _patch_object
patch.dict = _patch_dict
patch.multiple = _patch_multiple
patch.stopall = _patch_stopall
patch.TEST_PREFIX = 'test'

magic_methods = (
    "lt le gt ge eq ne "
    "getitem setitem delitem "
    "len contains iter "
    "hash str sizeof "
    "enter exit "
    # we added divmod oraz rdivmod here instead of numerics
    # because there jest no idivmod
    "divmod rdivmod neg pos abs invert "
    "complex int float index "
    "trunc floor ceil "
    "bool next "
)

numerics = (
    "add sub mul matmul div floordiv mod lshift rshift oraz xor albo pow truediv"
)
inplace = ' '.join('i%s' % n dla n w numerics.split())
right = ' '.join('r%s' % n dla n w numerics.split())

# nie including __prepare__, __instancecheck__, __subclasscheck__
# (as they are metaclass methods)
# __del__ jest nie supported at all jako it causes problems jeżeli it exists

_non_defaults = {
    '__get__', '__set__', '__delete__', '__reversed__', '__missing__',
    '__reduce__', '__reduce_ex__', '__getinitargs__', '__getnewargs__',
    '__getstate__', '__setstate__', '__getformat__', '__setformat__',
    '__repr__', '__dir__', '__subclasses__', '__format__',
}


def _get_method(name, func):
    "Turns a callable object (like a mock) into a real function"
    def method(self, *args, **kw):
        zwróć func(self, *args, **kw)
    method.__name__ = name
    zwróć method


_magics = {
    '__%s__' % method dla method w
    ' '.join([magic_methods, numerics, inplace, right]).split()
}

_all_magics = _magics | _non_defaults

_unsupported_magics = {
    '__getattr__', '__setattr__',
    '__init__', '__new__', '__prepare__'
    '__instancecheck__', '__subclasscheck__',
    '__del__'
}

_calculate_return_value = {
    '__hash__': lambda self: object.__hash__(self),
    '__str__': lambda self: object.__str__(self),
    '__sizeof__': lambda self: object.__sizeof__(self),
}

_return_values = {
    '__lt__': NotImplemented,
    '__gt__': NotImplemented,
    '__le__': NotImplemented,
    '__ge__': NotImplemented,
    '__int__': 1,
    '__contains__': Nieprawda,
    '__len__': 0,
    '__exit__': Nieprawda,
    '__complex__': 1j,
    '__float__': 1.0,
    '__bool__': Prawda,
    '__index__': 1,
}


def _get_eq(self):
    def __eq__(other):
        ret_val = self.__eq__._mock_return_value
        jeżeli ret_val jest nie DEFAULT:
            zwróć ret_val
        zwróć self jest other
    zwróć __eq__

def _get_ne(self):
    def __ne__(other):
        jeżeli self.__ne__._mock_return_value jest nie DEFAULT:
            zwróć DEFAULT
        zwróć self jest nie other
    zwróć __ne__

def _get_iter(self):
    def __iter__():
        ret_val = self.__iter__._mock_return_value
        jeżeli ret_val jest DEFAULT:
            zwróć iter([])
        # jeżeli ret_val was already an iterator, then calling iter on it should
        # zwróć the iterator unchanged
        zwróć iter(ret_val)
    zwróć __iter__

_side_effect_methods = {
    '__eq__': _get_eq,
    '__ne__': _get_ne,
    '__iter__': _get_iter,
}



def _set_return_value(mock, method, name):
    fixed = _return_values.get(name, DEFAULT)
    jeżeli fixed jest nie DEFAULT:
        method.return_value = fixed
        zwróć

    return_calulator = _calculate_return_value.get(name)
    jeżeli return_calulator jest nie Nic:
        spróbuj:
            return_value = return_calulator(mock)
        wyjąwszy AttributeError:
            # XXXX why do we zwróć AttributeError here?
            #      set it jako a side_effect instead?
            return_value = AttributeError(name)
        method.return_value = return_value
        zwróć

    side_effector = _side_effect_methods.get(name)
    jeżeli side_effector jest nie Nic:
        method.side_effect = side_effector(mock)



klasa MagicMixin(object):
    def __init__(self, *args, **kw):
        self._mock_set_magics()  # make magic work dla kwargs w init
        _safe_super(MagicMixin, self).__init__(*args, **kw)
        self._mock_set_magics()  # fix magic broken by upper level init


    def _mock_set_magics(self):
        these_magics = _magics

        jeżeli getattr(self, "_mock_methods", Nic) jest nie Nic:
            these_magics = _magics.intersection(self._mock_methods)

            remove_magics = set()
            remove_magics = _magics - these_magics

            dla entry w remove_magics:
                jeżeli entry w type(self).__dict__:
                    # remove unneeded magic methods
                    delattr(self, entry)

        # don't overwrite existing attributes jeżeli called a second time
        these_magics = these_magics - set(type(self).__dict__)

        _type = type(self)
        dla entry w these_magics:
            setattr(_type, entry, MagicProxy(entry, self))



klasa NonCallableMagicMock(MagicMixin, NonCallableMock):
    """A version of `MagicMock` that isn't callable."""
    def mock_add_spec(self, spec, spec_set=Nieprawda):
        """Add a spec to a mock. `spec` can either be an object albo a
        list of strings. Only attributes on the `spec` can be fetched as
        attributes z the mock.

        If `spec_set` jest Prawda then only attributes on the spec can be set."""
        self._mock_add_spec(spec, spec_set)
        self._mock_set_magics()



klasa MagicMock(MagicMixin, Mock):
    """
    MagicMock jest a subclass of Mock przy default implementations
    of most of the magic methods. You can use MagicMock without having to
    configure the magic methods yourself.

    If you use the `spec` albo `spec_set` arguments then *only* magic
    methods that exist w the spec will be created.

    Attributes oraz the zwróć value of a `MagicMock` will also be `MagicMocks`.
    """
    def mock_add_spec(self, spec, spec_set=Nieprawda):
        """Add a spec to a mock. `spec` can either be an object albo a
        list of strings. Only attributes on the `spec` can be fetched as
        attributes z the mock.

        If `spec_set` jest Prawda then only attributes on the spec can be set."""
        self._mock_add_spec(spec, spec_set)
        self._mock_set_magics()



klasa MagicProxy(object):
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

    def __call__(self, *args, **kwargs):
        m = self.create_mock()
        zwróć m(*args, **kwargs)

    def create_mock(self):
        entry = self.name
        parent = self.parent
        m = parent._get_child_mock(name=entry, _new_name=entry,
                                   _new_parent=parent)
        setattr(parent, entry, m)
        _set_return_value(parent, m, entry)
        zwróć m

    def __get__(self, obj, _type=Nic):
        zwróć self.create_mock()



klasa _ANY(object):
    "A helper object that compares equal to everything."

    def __eq__(self, other):
        zwróć Prawda

    def __ne__(self, other):
        zwróć Nieprawda

    def __repr__(self):
        zwróć '<ANY>'

ANY = _ANY()



def _format_call_signature(name, args, kwargs):
    message = '%s(%%s)' % name
    formatted_args = ''
    args_string = ', '.join([repr(arg) dla arg w args])
    kwargs_string = ', '.join([
        '%s=%r' % (key, value) dla key, value w sorted(kwargs.items())
    ])
    jeżeli args_string:
        formatted_args = args_string
    jeżeli kwargs_string:
        jeżeli formatted_args:
            formatted_args += ', '
        formatted_args += kwargs_string

    zwróć message % formatted_args



klasa _Call(tuple):
    """
    A tuple dla holding the results of a call to a mock, either w the form
    `(args, kwargs)` albo `(name, args, kwargs)`.

    If args albo kwargs are empty then a call tuple will compare equal to
    a tuple without those values. This makes comparisons less verbose::

        _Call(('name', (), {})) == ('name',)
        _Call(('name', (1,), {})) == ('name', (1,))
        _Call(((), {'a': 'b'})) == ({'a': 'b'},)

    The `_Call` object provides a useful shortcut dla comparing przy call::

        _Call(((1, 2), {'a': 3})) == call(1, 2, a=3)
        _Call(('foo', (1, 2), {'a': 3})) == call.foo(1, 2, a=3)

    If the _Call has no name then it will match any name.
    """
    def __new__(cls, value=(), name=Nic, parent=Nic, two=Nieprawda,
                from_kall=Prawda):
        name = ''
        args = ()
        kwargs = {}
        _len = len(value)
        jeżeli _len == 3:
            name, args, kwargs = value
        albo_inaczej _len == 2:
            first, second = value
            jeżeli isinstance(first, str):
                name = first
                jeżeli isinstance(second, tuple):
                    args = second
                inaczej:
                    kwargs = second
            inaczej:
                args, kwargs = first, second
        albo_inaczej _len == 1:
            value, = value
            jeżeli isinstance(value, str):
                name = value
            albo_inaczej isinstance(value, tuple):
                args = value
            inaczej:
                kwargs = value

        jeżeli two:
            zwróć tuple.__new__(cls, (args, kwargs))

        zwróć tuple.__new__(cls, (name, args, kwargs))


    def __init__(self, value=(), name=Nic, parent=Nic, two=Nieprawda,
                 from_kall=Prawda):
        self.name = name
        self.parent = parent
        self.from_kall = from_kall


    def __eq__(self, other):
        jeżeli other jest ANY:
            zwróć Prawda
        spróbuj:
            len_other = len(other)
        wyjąwszy TypeError:
            zwróć Nieprawda

        self_name = ''
        jeżeli len(self) == 2:
            self_args, self_kwargs = self
        inaczej:
            self_name, self_args, self_kwargs = self

        other_name = ''
        jeżeli len_other == 0:
            other_args, other_kwargs = (), {}
        albo_inaczej len_other == 3:
            other_name, other_args, other_kwargs = other
        albo_inaczej len_other == 1:
            value, = other
            jeżeli isinstance(value, tuple):
                other_args = value
                other_kwargs = {}
            albo_inaczej isinstance(value, str):
                other_name = value
                other_args, other_kwargs = (), {}
            inaczej:
                other_args = ()
                other_kwargs = value
        inaczej:
            # len 2
            # could be (name, args) albo (name, kwargs) albo (args, kwargs)
            first, second = other
            jeżeli isinstance(first, str):
                other_name = first
                jeżeli isinstance(second, tuple):
                    other_args, other_kwargs = second, {}
                inaczej:
                    other_args, other_kwargs = (), second
            inaczej:
                other_args, other_kwargs = first, second

        jeżeli self_name oraz other_name != self_name:
            zwróć Nieprawda

        # this order jest important dla ANY to work!
        zwróć (other_args, other_kwargs) == (self_args, self_kwargs)


    def __call__(self, *args, **kwargs):
        jeżeli self.name jest Nic:
            zwróć _Call(('', args, kwargs), name='()')

        name = self.name + '()'
        zwróć _Call((self.name, args, kwargs), name=name, parent=self)


    def __getattr__(self, attr):
        jeżeli self.name jest Nic:
            zwróć _Call(name=attr, from_kall=Nieprawda)
        name = '%s.%s' % (self.name, attr)
        zwróć _Call(name=name, parent=self, from_kall=Nieprawda)


    def count(self, *args, **kwargs):
        zwróć self.__getattr__('count')(*args, **kwargs)

    def index(self, *args, **kwargs):
        zwróć self.__getattr__('index')(*args, **kwargs)

    def __repr__(self):
        jeżeli nie self.from_kall:
            name = self.name albo 'call'
            jeżeli name.startswith('()'):
                name = 'call%s' % name
            zwróć name

        jeżeli len(self) == 2:
            name = 'call'
            args, kwargs = self
        inaczej:
            name, args, kwargs = self
            jeżeli nie name:
                name = 'call'
            albo_inaczej nie name.startswith('()'):
                name = 'call.%s' % name
            inaczej:
                name = 'call%s' % name
        zwróć _format_call_signature(name, args, kwargs)


    def call_list(self):
        """For a call object that represents multiple calls, `call_list`
        returns a list of all the intermediate calls jako well jako the
        final call."""
        vals = []
        thing = self
        dopóki thing jest nie Nic:
            jeżeli thing.from_kall:
                vals.append(thing)
            thing = thing.parent
        zwróć _CallList(reversed(vals))


call = _Call(from_kall=Nieprawda)



def create_autospec(spec, spec_set=Nieprawda, instance=Nieprawda, _parent=Nic,
                    _name=Nic, **kwargs):
    """Create a mock object using another object jako a spec. Attributes on the
    mock will use the corresponding attribute on the `spec` object jako their
    spec.

    Functions albo methods being mocked will have their arguments checked
    to check that they are called przy the correct signature.

    If `spec_set` jest Prawda then attempting to set attributes that don't exist
    on the spec object will podnieś an `AttributeError`.

    If a klasa jest used jako a spec then the zwróć value of the mock (the
    instance of the class) will have the same spec. You can use a klasa jako the
    spec dla an instance object by dalejing `instance=Prawda`. The returned mock
    will only be callable jeżeli instances of the mock are callable.

    `create_autospec` also takes arbitrary keyword arguments that are dalejed to
    the constructor of the created mock."""
    jeżeli _is_list(spec):
        # can't dalej a list instance to the mock constructor jako it will be
        # interpreted jako a list of strings
        spec = type(spec)

    is_type = isinstance(spec, type)

    _kwargs = {'spec': spec}
    jeżeli spec_set:
        _kwargs = {'spec_set': spec}
    albo_inaczej spec jest Nic:
        # Nic we mock przy a normal mock without a spec
        _kwargs = {}
    jeżeli _kwargs oraz instance:
        _kwargs['_spec_as_instance'] = Prawda

    _kwargs.update(kwargs)

    Klass = MagicMock
    jeżeli type(spec) w DescriptorTypes:
        # descriptors don't have a spec
        # because we don't know what type they zwróć
        _kwargs = {}
    albo_inaczej nie _callable(spec):
        Klass = NonCallableMagicMock
    albo_inaczej is_type oraz instance oraz nie _instance_callable(spec):
        Klass = NonCallableMagicMock

    _name = _kwargs.pop('name', _name)

    _new_name = _name
    jeżeli _parent jest Nic:
        # dla a top level object no _new_name should be set
        _new_name = ''

    mock = Klass(parent=_parent, _new_parent=_parent, _new_name=_new_name,
                 name=_name, **_kwargs)

    jeżeli isinstance(spec, FunctionTypes):
        # should only happen at the top level because we don't
        # recurse dla functions
        mock = _set_signature(mock, spec)
    inaczej:
        _check_signature(spec, mock, is_type, instance)

    jeżeli _parent jest nie Nic oraz nie instance:
        _parent._mock_children[_name] = mock

    jeżeli is_type oraz nie instance oraz 'return_value' nie w kwargs:
        mock.return_value = create_autospec(spec, spec_set, instance=Prawda,
                                            _name='()', _parent=mock)

    dla entry w dir(spec):
        jeżeli _is_magic(entry):
            # MagicMock already does the useful magic methods dla us
            kontynuuj

        # XXXX do we need a better way of getting attributes without
        # triggering code execution (?) Probably nie - we need the actual
        # object to mock it so we would rather trigger a property than mock
        # the property descriptor. Likewise we want to mock out dynamically
        # provided attributes.
        # XXXX what about attributes that podnieś exceptions other than
        # AttributeError on being fetched?
        # we could be resilient against it, albo catch oraz propagate the
        # exception when the attribute jest fetched z the mock
        spróbuj:
            original = getattr(spec, entry)
        wyjąwszy AttributeError:
            kontynuuj

        kwargs = {'spec': original}
        jeżeli spec_set:
            kwargs = {'spec_set': original}

        jeżeli nie isinstance(original, FunctionTypes):
            new = _SpecState(original, spec_set, mock, entry, instance)
            mock._mock_children[entry] = new
        inaczej:
            parent = mock
            jeżeli isinstance(spec, FunctionTypes):
                parent = mock.mock

            skipfirst = _must_skip(spec, entry, is_type)
            kwargs['_eat_self'] = skipfirst
            new = MagicMock(parent=parent, name=entry, _new_name=entry,
                            _new_parent=parent,
                            **kwargs)
            mock._mock_children[entry] = new
            _check_signature(original, new, skipfirst=skipfirst)

        # so functions created przy _set_signature become instance attributes,
        # *plus* their underlying mock exists w _mock_children of the parent
        # mock. Adding to _mock_children may be unnecessary where we are also
        # setting jako an instance attribute?
        jeżeli isinstance(new, FunctionTypes):
            setattr(mock, entry, new)

    zwróć mock


def _must_skip(spec, entry, is_type):
    """
    Return whether we should skip the first argument on spec's `entry`
    attribute.
    """
    jeżeli nie isinstance(spec, type):
        jeżeli entry w getattr(spec, '__dict__', {}):
            # instance attribute - shouldn't skip
            zwróć Nieprawda
        spec = spec.__class__

    dla klass w spec.__mro__:
        result = klass.__dict__.get(entry, DEFAULT)
        jeżeli result jest DEFAULT:
            kontynuuj
        jeżeli isinstance(result, (staticmethod, classmethod)):
            zwróć Nieprawda
        albo_inaczej isinstance(getattr(result, '__get__', Nic), MethodWrapperTypes):
            # Normal method => skip jeżeli looked up on type
            # (jeżeli looked up on instance, self jest already skipped)
            zwróć is_type
        inaczej:
            zwróć Nieprawda

    # shouldn't get here unless function jest a dynamically provided attribute
    # XXXX untested behaviour
    zwróć is_type


def _get_class(obj):
    spróbuj:
        zwróć obj.__class__
    wyjąwszy AttributeError:
        # it jest possible dla objects to have no __class__
        zwróć type(obj)


klasa _SpecState(object):

    def __init__(self, spec, spec_set=Nieprawda, parent=Nic,
                 name=Nic, ids=Nic, instance=Nieprawda):
        self.spec = spec
        self.ids = ids
        self.spec_set = spec_set
        self.parent = parent
        self.instance = instance
        self.name = name


FunctionTypes = (
    # python function
    type(create_autospec),
    # instance method
    type(ANY.__eq__),
)

MethodWrapperTypes = (
    type(ANY.__eq__.__get__),
)


file_spec = Nic

def _iterate_read_data(read_data):
    # Helper dla mock_open:
    # Retrieve lines z read_data via a generator so that separate calls to
    # readline, read, oraz readlines are properly interleaved
    sep = b'\n' jeżeli isinstance(read_data, bytes) inaczej '\n'
    data_as_list = [l + sep dla l w read_data.split(sep)]

    jeżeli data_as_list[-1] == sep:
        # If the last line ended w a newline, the list comprehension will have an
        # extra entry that's just a newline.  Remove this.
        data_as_list = data_as_list[:-1]
    inaczej:
        # If there wasn't an extra newline by itself, then the file being
        # emulated doesn't have a newline to end the last line  remove the
        # newline that our naive format() added
        data_as_list[-1] = data_as_list[-1][:-1]

    dla line w data_as_list:
        uzyskaj line


def mock_open(mock=Nic, read_data=''):
    """
    A helper function to create a mock to replace the use of `open`. It works
    dla `open` called directly albo used jako a context manager.

    The `mock` argument jest the mock object to configure. If `Nic` (the
    default) then a `MagicMock` will be created dla you, przy the API limited
    to methods albo attributes available on standard file handles.

    `read_data` jest a string dla the `read` methoddline`, oraz `readlines` of the
    file handle to return.  This jest an empty string by default.
    """
    def _readlines_side_effect(*args, **kwargs):
        jeżeli handle.readlines.return_value jest nie Nic:
            zwróć handle.readlines.return_value
        zwróć list(_state[0])

    def _read_side_effect(*args, **kwargs):
        jeżeli handle.read.return_value jest nie Nic:
            zwróć handle.read.return_value
        zwróć type(read_data)().join(_state[0])

    def _readline_side_effect():
        jeżeli handle.readline.return_value jest nie Nic:
            dopóki Prawda:
                uzyskaj handle.readline.return_value
        dla line w _state[0]:
            uzyskaj line


    global file_spec
    jeżeli file_spec jest Nic:
        zaimportuj _io
        file_spec = list(set(dir(_io.TextIOWrapper)).union(set(dir(_io.BytesIO))))

    jeżeli mock jest Nic:
        mock = MagicMock(name='open', spec=open)

    handle = MagicMock(spec=file_spec)
    handle.__enter__.return_value = handle

    _state = [_iterate_read_data(read_data), Nic]

    handle.write.return_value = Nic
    handle.read.return_value = Nic
    handle.readline.return_value = Nic
    handle.readlines.return_value = Nic

    handle.read.side_effect = _read_side_effect
    _state[1] = _readline_side_effect()
    handle.readline.side_effect = _state[1]
    handle.readlines.side_effect = _readlines_side_effect

    def reset_data(*args, **kwargs):
        _state[0] = _iterate_read_data(read_data)
        jeżeli handle.readline.side_effect == _state[1]:
            # Only reset the side effect jeżeli the user hasn't overridden it.
            _state[1] = _readline_side_effect()
            handle.readline.side_effect = _state[1]
        zwróć DEFAULT

    mock.side_effect = reset_data
    mock.return_value = handle
    zwróć mock


klasa PropertyMock(Mock):
    """
    A mock intended to be used jako a property, albo other descriptor, on a class.
    `PropertyMock` provides `__get__` oraz `__set__` methods so you can specify
    a zwróć value when it jest fetched.

    Fetching a `PropertyMock` instance z an object calls the mock, with
    no args. Setting it calls the mock przy the value being set.
    """
    def _get_child_mock(self, **kwargs):
        zwróć MagicMock(**kwargs)

    def __get__(self, obj, obj_type):
        zwróć self()
    def __set__(self, obj, val):
        self(val)
