zaimportuj builtins
zaimportuj copyreg
zaimportuj gc
zaimportuj itertools
zaimportuj math
zaimportuj pickle
zaimportuj sys
zaimportuj types
zaimportuj unittest
zaimportuj weakref

z copy zaimportuj deepcopy
z test zaimportuj support


klasa OperatorsTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.binops = {
            'add': '+',
            'sub': '-',
            'mul': '*',
            'matmul': '@',
            'truediv': '/',
            'floordiv': '//',
            'divmod': 'divmod',
            'pow': '**',
            'lshift': '<<',
            'rshift': '>>',
            'and': '&',
            'xor': '^',
            'or': '|',
            'cmp': 'cmp',
            'lt': '<',
            'le': '<=',
            'eq': '==',
            'ne': '!=',
            'gt': '>',
            'ge': '>=',
        }

        dla name, expr w list(self.binops.items()):
            jeżeli expr.islower():
                expr = expr + "(a, b)"
            inaczej:
                expr = 'a %s b' % expr
            self.binops[name] = expr

        self.unops = {
            'pos': '+',
            'neg': '-',
            'abs': 'abs',
            'invert': '~',
            'int': 'int',
            'float': 'float',
        }

        dla name, expr w list(self.unops.items()):
            jeżeli expr.islower():
                expr = expr + "(a)"
            inaczej:
                expr = '%s a' % expr
            self.unops[name] = expr

    def unop_test(self, a, res, expr="len(a)", meth="__len__"):
        d = {'a': a}
        self.assertEqual(eval(expr, d), res)
        t = type(a)
        m = getattr(t, meth)

        # Find method w parent class
        dopóki meth nie w t.__dict__:
            t = t.__bases__[0]
        # w some implementations (e.g. PyPy), 'm' can be a regular unbound
        # method object; the getattr() below obtains its underlying function.
        self.assertEqual(getattr(m, 'im_func', m), t.__dict__[meth])
        self.assertEqual(m(a), res)
        bm = getattr(a, meth)
        self.assertEqual(bm(), res)

    def binop_test(self, a, b, res, expr="a+b", meth="__add__"):
        d = {'a': a, 'b': b}

        self.assertEqual(eval(expr, d), res)
        t = type(a)
        m = getattr(t, meth)
        dopóki meth nie w t.__dict__:
            t = t.__bases__[0]
        # w some implementations (e.g. PyPy), 'm' can be a regular unbound
        # method object; the getattr() below obtains its underlying function.
        self.assertEqual(getattr(m, 'im_func', m), t.__dict__[meth])
        self.assertEqual(m(a, b), res)
        bm = getattr(a, meth)
        self.assertEqual(bm(b), res)

    def sliceop_test(self, a, b, c, res, expr="a[b:c]", meth="__getitem__"):
        d = {'a': a, 'b': b, 'c': c}
        self.assertEqual(eval(expr, d), res)
        t = type(a)
        m = getattr(t, meth)
        dopóki meth nie w t.__dict__:
            t = t.__bases__[0]
        # w some implementations (e.g. PyPy), 'm' can be a regular unbound
        # method object; the getattr() below obtains its underlying function.
        self.assertEqual(getattr(m, 'im_func', m), t.__dict__[meth])
        self.assertEqual(m(a, slice(b, c)), res)
        bm = getattr(a, meth)
        self.assertEqual(bm(slice(b, c)), res)

    def setop_test(self, a, b, res, stmt="a+=b", meth="__iadd__"):
        d = {'a': deepcopy(a), 'b': b}
        exec(stmt, d)
        self.assertEqual(d['a'], res)
        t = type(a)
        m = getattr(t, meth)
        dopóki meth nie w t.__dict__:
            t = t.__bases__[0]
        # w some implementations (e.g. PyPy), 'm' can be a regular unbound
        # method object; the getattr() below obtains its underlying function.
        self.assertEqual(getattr(m, 'im_func', m), t.__dict__[meth])
        d['a'] = deepcopy(a)
        m(d['a'], b)
        self.assertEqual(d['a'], res)
        d['a'] = deepcopy(a)
        bm = getattr(d['a'], meth)
        bm(b)
        self.assertEqual(d['a'], res)

    def set2op_test(self, a, b, c, res, stmt="a[b]=c", meth="__setitem__"):
        d = {'a': deepcopy(a), 'b': b, 'c': c}
        exec(stmt, d)
        self.assertEqual(d['a'], res)
        t = type(a)
        m = getattr(t, meth)
        dopóki meth nie w t.__dict__:
            t = t.__bases__[0]
        # w some implementations (e.g. PyPy), 'm' can be a regular unbound
        # method object; the getattr() below obtains its underlying function.
        self.assertEqual(getattr(m, 'im_func', m), t.__dict__[meth])
        d['a'] = deepcopy(a)
        m(d['a'], b, c)
        self.assertEqual(d['a'], res)
        d['a'] = deepcopy(a)
        bm = getattr(d['a'], meth)
        bm(b, c)
        self.assertEqual(d['a'], res)

    def setsliceop_test(self, a, b, c, d, res, stmt="a[b:c]=d", meth="__setitem__"):
        dictionary = {'a': deepcopy(a), 'b': b, 'c': c, 'd': d}
        exec(stmt, dictionary)
        self.assertEqual(dictionary['a'], res)
        t = type(a)
        dopóki meth nie w t.__dict__:
            t = t.__bases__[0]
        m = getattr(t, meth)
        # w some implementations (e.g. PyPy), 'm' can be a regular unbound
        # method object; the getattr() below obtains its underlying function.
        self.assertEqual(getattr(m, 'im_func', m), t.__dict__[meth])
        dictionary['a'] = deepcopy(a)
        m(dictionary['a'], slice(b, c), d)
        self.assertEqual(dictionary['a'], res)
        dictionary['a'] = deepcopy(a)
        bm = getattr(dictionary['a'], meth)
        bm(slice(b, c), d)
        self.assertEqual(dictionary['a'], res)

    def test_lists(self):
        # Testing list operations...
        # Asserts are within individual test methods
        self.binop_test([1], [2], [1,2], "a+b", "__add__")
        self.binop_test([1,2,3], 2, 1, "b w a", "__contains__")
        self.binop_test([1,2,3], 4, 0, "b w a", "__contains__")
        self.binop_test([1,2,3], 1, 2, "a[b]", "__getitem__")
        self.sliceop_test([1,2,3], 0, 2, [1,2], "a[b:c]", "__getitem__")
        self.setop_test([1], [2], [1,2], "a+=b", "__iadd__")
        self.setop_test([1,2], 3, [1,2,1,2,1,2], "a*=b", "__imul__")
        self.unop_test([1,2,3], 3, "len(a)", "__len__")
        self.binop_test([1,2], 3, [1,2,1,2,1,2], "a*b", "__mul__")
        self.binop_test([1,2], 3, [1,2,1,2,1,2], "b*a", "__rmul__")
        self.set2op_test([1,2], 1, 3, [1,3], "a[b]=c", "__setitem__")
        self.setsliceop_test([1,2,3,4], 1, 3, [5,6], [1,5,6,4], "a[b:c]=d",
                        "__setitem__")

    def test_dicts(self):
        # Testing dict operations...
        self.binop_test({1:2,3:4}, 1, 1, "b w a", "__contains__")
        self.binop_test({1:2,3:4}, 2, 0, "b w a", "__contains__")
        self.binop_test({1:2,3:4}, 1, 2, "a[b]", "__getitem__")

        d = {1:2, 3:4}
        l1 = []
        dla i w list(d.keys()):
            l1.append(i)
        l = []
        dla i w iter(d):
            l.append(i)
        self.assertEqual(l, l1)
        l = []
        dla i w d.__iter__():
            l.append(i)
        self.assertEqual(l, l1)
        l = []
        dla i w dict.__iter__(d):
            l.append(i)
        self.assertEqual(l, l1)
        d = {1:2, 3:4}
        self.unop_test(d, 2, "len(a)", "__len__")
        self.assertEqual(eval(repr(d), {}), d)
        self.assertEqual(eval(d.__repr__(), {}), d)
        self.set2op_test({1:2,3:4}, 2, 3, {1:2,2:3,3:4}, "a[b]=c",
                        "__setitem__")

    # Tests dla unary oraz binary operators
    def number_operators(self, a, b, skip=[]):
        dict = {'a': a, 'b': b}

        dla name, expr w self.binops.items():
            jeżeli name nie w skip:
                name = "__%s__" % name
                jeżeli hasattr(a, name):
                    res = eval(expr, dict)
                    self.binop_test(a, b, res, expr, name)

        dla name, expr w list(self.unops.items()):
            jeżeli name nie w skip:
                name = "__%s__" % name
                jeżeli hasattr(a, name):
                    res = eval(expr, dict)
                    self.unop_test(a, res, expr, name)

    def test_ints(self):
        # Testing int operations...
        self.number_operators(100, 3)
        # The following crashes w Python 2.2
        self.assertEqual((1).__bool__(), 1)
        self.assertEqual((0).__bool__(), 0)
        # This returns 'NotImplemented' w Python 2.2
        klasa C(int):
            def __add__(self, other):
                zwróć NotImplemented
        self.assertEqual(C(5), 5)
        spróbuj:
            C() + ""
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("NotImplemented should have caused TypeError")

    def test_floats(self):
        # Testing float operations...
        self.number_operators(100.0, 3.0)

    def test_complexes(self):
        # Testing complex operations...
        self.number_operators(100.0j, 3.0j, skip=['lt', 'le', 'gt', 'ge',
                                                  'int', 'float',
                                                  'floordiv', 'divmod', 'mod'])

        klasa Number(complex):
            __slots__ = ['prec']
            def __new__(cls, *args, **kwds):
                result = complex.__new__(cls, *args)
                result.prec = kwds.get('prec', 12)
                zwróć result
            def __repr__(self):
                prec = self.prec
                jeżeli self.imag == 0.0:
                    zwróć "%.*g" % (prec, self.real)
                jeżeli self.real == 0.0:
                    zwróć "%.*gj" % (prec, self.imag)
                zwróć "(%.*g+%.*gj)" % (prec, self.real, prec, self.imag)
            __str__ = __repr__

        a = Number(3.14, prec=6)
        self.assertEqual(repr(a), "3.14")
        self.assertEqual(a.prec, 6)

        a = Number(a, prec=2)
        self.assertEqual(repr(a), "3.1")
        self.assertEqual(a.prec, 2)

        a = Number(234.5)
        self.assertEqual(repr(a), "234.5")
        self.assertEqual(a.prec, 12)

    def test_explicit_reverse_methods(self):
        # see issue 9930
        self.assertEqual(complex.__radd__(3j, 4.0), complex(4.0, 3.0))
        self.assertEqual(float.__rsub__(3.0, 1), -2.0)

    @support.impl_detail("the module 'xxsubtype' jest internal")
    def test_spam_lists(self):
        # Testing spamlist operations...
        zaimportuj copy, xxsubtype jako spam

        def spamlist(l, memo=Nic):
            zaimportuj xxsubtype jako spam
            zwróć spam.spamlist(l)

        # This jest an ugly hack:
        copy._deepcopy_dispatch[spam.spamlist] = spamlist

        self.binop_test(spamlist([1]), spamlist([2]), spamlist([1,2]), "a+b",
                       "__add__")
        self.binop_test(spamlist([1,2,3]), 2, 1, "b w a", "__contains__")
        self.binop_test(spamlist([1,2,3]), 4, 0, "b w a", "__contains__")
        self.binop_test(spamlist([1,2,3]), 1, 2, "a[b]", "__getitem__")
        self.sliceop_test(spamlist([1,2,3]), 0, 2, spamlist([1,2]), "a[b:c]",
                          "__getitem__")
        self.setop_test(spamlist([1]), spamlist([2]), spamlist([1,2]), "a+=b",
                        "__iadd__")
        self.setop_test(spamlist([1,2]), 3, spamlist([1,2,1,2,1,2]), "a*=b",
                        "__imul__")
        self.unop_test(spamlist([1,2,3]), 3, "len(a)", "__len__")
        self.binop_test(spamlist([1,2]), 3, spamlist([1,2,1,2,1,2]), "a*b",
                        "__mul__")
        self.binop_test(spamlist([1,2]), 3, spamlist([1,2,1,2,1,2]), "b*a",
                        "__rmul__")
        self.set2op_test(spamlist([1,2]), 1, 3, spamlist([1,3]), "a[b]=c",
                         "__setitem__")
        self.setsliceop_test(spamlist([1,2,3,4]), 1, 3, spamlist([5,6]),
                             spamlist([1,5,6,4]), "a[b:c]=d", "__setitem__")
        # Test subclassing
        klasa C(spam.spamlist):
            def foo(self): zwróć 1
        a = C()
        self.assertEqual(a, [])
        self.assertEqual(a.foo(), 1)
        a.append(100)
        self.assertEqual(a, [100])
        self.assertEqual(a.getstate(), 0)
        a.setstate(42)
        self.assertEqual(a.getstate(), 42)

    @support.impl_detail("the module 'xxsubtype' jest internal")
    def test_spam_dicts(self):
        # Testing spamdict operations...
        zaimportuj copy, xxsubtype jako spam
        def spamdict(d, memo=Nic):
            zaimportuj xxsubtype jako spam
            sd = spam.spamdict()
            dla k, v w list(d.items()):
                sd[k] = v
            zwróć sd
        # This jest an ugly hack:
        copy._deepcopy_dispatch[spam.spamdict] = spamdict

        self.binop_test(spamdict({1:2,3:4}), 1, 1, "b w a", "__contains__")
        self.binop_test(spamdict({1:2,3:4}), 2, 0, "b w a", "__contains__")
        self.binop_test(spamdict({1:2,3:4}), 1, 2, "a[b]", "__getitem__")
        d = spamdict({1:2,3:4})
        l1 = []
        dla i w list(d.keys()):
            l1.append(i)
        l = []
        dla i w iter(d):
            l.append(i)
        self.assertEqual(l, l1)
        l = []
        dla i w d.__iter__():
            l.append(i)
        self.assertEqual(l, l1)
        l = []
        dla i w type(spamdict({})).__iter__(d):
            l.append(i)
        self.assertEqual(l, l1)
        straightd = {1:2, 3:4}
        spamd = spamdict(straightd)
        self.unop_test(spamd, 2, "len(a)", "__len__")
        self.unop_test(spamd, repr(straightd), "repr(a)", "__repr__")
        self.set2op_test(spamdict({1:2,3:4}), 2, 3, spamdict({1:2,2:3,3:4}),
                   "a[b]=c", "__setitem__")
        # Test subclassing
        klasa C(spam.spamdict):
            def foo(self): zwróć 1
        a = C()
        self.assertEqual(list(a.items()), [])
        self.assertEqual(a.foo(), 1)
        a['foo'] = 'bar'
        self.assertEqual(list(a.items()), [('foo', 'bar')])
        self.assertEqual(a.getstate(), 0)
        a.setstate(100)
        self.assertEqual(a.getstate(), 100)

klasa ClassPropertiesAndMethods(unittest.TestCase):

    def assertHasAttr(self, obj, name):
        self.assertPrawda(hasattr(obj, name),
                        '%r has no attribute %r' % (obj, name))

    def assertNotHasAttr(self, obj, name):
        self.assertNieprawda(hasattr(obj, name),
                         '%r has unexpected attribute %r' % (obj, name))

    def test_python_dicts(self):
        # Testing Python subclass of dict...
        self.assertPrawda(issubclass(dict, dict))
        self.assertIsInstance({}, dict)
        d = dict()
        self.assertEqual(d, {})
        self.assertIs(d.__class__, dict)
        self.assertIsInstance(d, dict)
        klasa C(dict):
            state = -1
            def __init__(self_local, *a, **kw):
                jeżeli a:
                    self.assertEqual(len(a), 1)
                    self_local.state = a[0]
                jeżeli kw:
                    dla k, v w list(kw.items()):
                        self_local[v] = k
            def __getitem__(self, key):
                zwróć self.get(key, 0)
            def __setitem__(self_local, key, value):
                self.assertIsInstance(key, type(0))
                dict.__setitem__(self_local, key, value)
            def setstate(self, state):
                self.state = state
            def getstate(self):
                zwróć self.state
        self.assertPrawda(issubclass(C, dict))
        a1 = C(12)
        self.assertEqual(a1.state, 12)
        a2 = C(foo=1, bar=2)
        self.assertEqual(a2[1] == 'foo' oraz a2[2], 'bar')
        a = C()
        self.assertEqual(a.state, -1)
        self.assertEqual(a.getstate(), -1)
        a.setstate(0)
        self.assertEqual(a.state, 0)
        self.assertEqual(a.getstate(), 0)
        a.setstate(10)
        self.assertEqual(a.state, 10)
        self.assertEqual(a.getstate(), 10)
        self.assertEqual(a[42], 0)
        a[42] = 24
        self.assertEqual(a[42], 24)
        N = 50
        dla i w range(N):
            a[i] = C()
            dla j w range(N):
                a[i][j] = i*j
        dla i w range(N):
            dla j w range(N):
                self.assertEqual(a[i][j], i*j)

    def test_python_lists(self):
        # Testing Python subclass of list...
        klasa C(list):
            def __getitem__(self, i):
                jeżeli isinstance(i, slice):
                    zwróć i.start, i.stop
                zwróć list.__getitem__(self, i) + 100
        a = C()
        a.extend([0,1,2])
        self.assertEqual(a[0], 100)
        self.assertEqual(a[1], 101)
        self.assertEqual(a[2], 102)
        self.assertEqual(a[100:200], (100,200))

    def test_metaclass(self):
        # Testing metaclasses...
        klasa C(metaclass=type):
            def __init__(self):
                self.__state = 0
            def getstate(self):
                zwróć self.__state
            def setstate(self, state):
                self.__state = state
        a = C()
        self.assertEqual(a.getstate(), 0)
        a.setstate(10)
        self.assertEqual(a.getstate(), 10)
        klasa _metaclass(type):
            def myself(cls): zwróć cls
        klasa D(metaclass=_metaclass):
            dalej
        self.assertEqual(D.myself(), D)
        d = D()
        self.assertEqual(d.__class__, D)
        klasa M1(type):
            def __new__(cls, name, bases, dict):
                dict['__spam__'] = 1
                zwróć type.__new__(cls, name, bases, dict)
        klasa C(metaclass=M1):
            dalej
        self.assertEqual(C.__spam__, 1)
        c = C()
        self.assertEqual(c.__spam__, 1)

        klasa _instance(object):
            dalej
        klasa M2(object):
            @staticmethod
            def __new__(cls, name, bases, dict):
                self = object.__new__(cls)
                self.name = name
                self.bases = bases
                self.dict = dict
                zwróć self
            def __call__(self):
                it = _instance()
                # Early binding of methods
                dla key w self.dict:
                    jeżeli key.startswith("__"):
                        kontynuuj
                    setattr(it, key, self.dict[key].__get__(it, self))
                zwróć it
        klasa C(metaclass=M2):
            def spam(self):
                zwróć 42
        self.assertEqual(C.name, 'C')
        self.assertEqual(C.bases, ())
        self.assertIn('spam', C.dict)
        c = C()
        self.assertEqual(c.spam(), 42)

        # More metaclass examples

        klasa autosuper(type):
            # Automatically add __super to the class
            # This trick only works dla dynamic classes
            def __new__(metaclass, name, bases, dict):
                cls = super(autosuper, metaclass).__new__(metaclass,
                                                          name, bases, dict)
                # Name mangling dla __super removes leading underscores
                dopóki name[:1] == "_":
                    name = name[1:]
                jeżeli name:
                    name = "_%s__super" % name
                inaczej:
                    name = "__super"
                setattr(cls, name, super(cls))
                zwróć cls
        klasa A(metaclass=autosuper):
            def meth(self):
                zwróć "A"
        klasa B(A):
            def meth(self):
                zwróć "B" + self.__super.meth()
        klasa C(A):
            def meth(self):
                zwróć "C" + self.__super.meth()
        klasa D(C, B):
            def meth(self):
                zwróć "D" + self.__super.meth()
        self.assertEqual(D().meth(), "DCBA")
        klasa E(B, C):
            def meth(self):
                zwróć "E" + self.__super.meth()
        self.assertEqual(E().meth(), "EBCA")

        klasa autoproperty(type):
            # Automatically create property attributes when methods
            # named _get_x and/or _set_x are found
            def __new__(metaclass, name, bases, dict):
                hits = {}
                dla key, val w dict.items():
                    jeżeli key.startswith("_get_"):
                        key = key[5:]
                        get, set = hits.get(key, (Nic, Nic))
                        get = val
                        hits[key] = get, set
                    albo_inaczej key.startswith("_set_"):
                        key = key[5:]
                        get, set = hits.get(key, (Nic, Nic))
                        set = val
                        hits[key] = get, set
                dla key, (get, set) w hits.items():
                    dict[key] = property(get, set)
                zwróć super(autoproperty, metaclass).__new__(metaclass,
                                                            name, bases, dict)
        klasa A(metaclass=autoproperty):
            def _get_x(self):
                zwróć -self.__x
            def _set_x(self, x):
                self.__x = -x
        a = A()
        self.assertNotHasAttr(a, "x")
        a.x = 12
        self.assertEqual(a.x, 12)
        self.assertEqual(a._A__x, -12)

        klasa multimetaclass(autoproperty, autosuper):
            # Merge of multiple cooperating metaclasses
            dalej
        klasa A(metaclass=multimetaclass):
            def _get_x(self):
                zwróć "A"
        klasa B(A):
            def _get_x(self):
                zwróć "B" + self.__super._get_x()
        klasa C(A):
            def _get_x(self):
                zwróć "C" + self.__super._get_x()
        klasa D(C, B):
            def _get_x(self):
                zwróć "D" + self.__super._get_x()
        self.assertEqual(D().x, "DCBA")

        # Make sure type(x) doesn't call x.__class__.__init__
        klasa T(type):
            counter = 0
            def __init__(self, *args):
                T.counter += 1
        klasa C(metaclass=T):
            dalej
        self.assertEqual(T.counter, 1)
        a = C()
        self.assertEqual(type(a), C)
        self.assertEqual(T.counter, 1)

        klasa C(object): dalej
        c = C()
        spróbuj: c()
        wyjąwszy TypeError: dalej
        inaczej: self.fail("calling object w/o call method should podnieś "
                        "TypeError")

        # Testing code to find most derived baseclass
        klasa A(type):
            def __new__(*args, **kwargs):
                zwróć type.__new__(*args, **kwargs)

        klasa B(object):
            dalej

        klasa C(object, metaclass=A):
            dalej

        # The most derived metaclass of D jest A rather than type.
        klasa D(B, C):
            dalej
        self.assertIs(A, type(D))

        # issue1294232: correct metaclass calculation
        new_calls = []  # to check the order of __new__ calls
        klasa AMeta(type):
            @staticmethod
            def __new__(mcls, name, bases, ns):
                new_calls.append('AMeta')
                zwróć super().__new__(mcls, name, bases, ns)
            @classmethod
            def __prepare__(mcls, name, bases):
                zwróć {}

        klasa BMeta(AMeta):
            @staticmethod
            def __new__(mcls, name, bases, ns):
                new_calls.append('BMeta')
                zwróć super().__new__(mcls, name, bases, ns)
            @classmethod
            def __prepare__(mcls, name, bases):
                ns = super().__prepare__(name, bases)
                ns['BMeta_was_here'] = Prawda
                zwróć ns

        klasa A(metaclass=AMeta):
            dalej
        self.assertEqual(['AMeta'], new_calls)
        new_calls.clear()

        klasa B(metaclass=BMeta):
            dalej
        # BMeta.__new__ calls AMeta.__new__ przy super:
        self.assertEqual(['BMeta', 'AMeta'], new_calls)
        new_calls.clear()

        klasa C(A, B):
            dalej
        # The most derived metaclass jest BMeta:
        self.assertEqual(['BMeta', 'AMeta'], new_calls)
        new_calls.clear()
        # BMeta.__prepare__ should've been called:
        self.assertIn('BMeta_was_here', C.__dict__)

        # The order of the bases shouldn't matter:
        klasa C2(B, A):
            dalej
        self.assertEqual(['BMeta', 'AMeta'], new_calls)
        new_calls.clear()
        self.assertIn('BMeta_was_here', C2.__dict__)

        # Check correct metaclass calculation when a metaclass jest declared:
        klasa D(C, metaclass=type):
            dalej
        self.assertEqual(['BMeta', 'AMeta'], new_calls)
        new_calls.clear()
        self.assertIn('BMeta_was_here', D.__dict__)

        klasa E(C, metaclass=AMeta):
            dalej
        self.assertEqual(['BMeta', 'AMeta'], new_calls)
        new_calls.clear()
        self.assertIn('BMeta_was_here', E.__dict__)

        # Special case: the given metaclass isn't a class,
        # so there jest no metaclass calculation.
        marker = object()
        def func(*args, **kwargs):
            zwróć marker
        klasa X(metaclass=func):
            dalej
        klasa Y(object, metaclass=func):
            dalej
        klasa Z(D, metaclass=func):
            dalej
        self.assertIs(marker, X)
        self.assertIs(marker, Y)
        self.assertIs(marker, Z)

        # The given metaclass jest a class,
        # but nie a descendant of type.
        prepare_calls = []  # to track __prepare__ calls
        klasa ANotMeta:
            def __new__(mcls, *args, **kwargs):
                new_calls.append('ANotMeta')
                zwróć super().__new__(mcls)
            @classmethod
            def __prepare__(mcls, name, bases):
                prepare_calls.append('ANotMeta')
                zwróć {}
        klasa BNotMeta(ANotMeta):
            def __new__(mcls, *args, **kwargs):
                new_calls.append('BNotMeta')
                zwróć super().__new__(mcls)
            @classmethod
            def __prepare__(mcls, name, bases):
                prepare_calls.append('BNotMeta')
                zwróć super().__prepare__(name, bases)

        klasa A(metaclass=ANotMeta):
            dalej
        self.assertIs(ANotMeta, type(A))
        self.assertEqual(['ANotMeta'], prepare_calls)
        prepare_calls.clear()
        self.assertEqual(['ANotMeta'], new_calls)
        new_calls.clear()

        klasa B(metaclass=BNotMeta):
            dalej
        self.assertIs(BNotMeta, type(B))
        self.assertEqual(['BNotMeta', 'ANotMeta'], prepare_calls)
        prepare_calls.clear()
        self.assertEqual(['BNotMeta', 'ANotMeta'], new_calls)
        new_calls.clear()

        klasa C(A, B):
            dalej
        self.assertIs(BNotMeta, type(C))
        self.assertEqual(['BNotMeta', 'ANotMeta'], new_calls)
        new_calls.clear()
        self.assertEqual(['BNotMeta', 'ANotMeta'], prepare_calls)
        prepare_calls.clear()

        klasa C2(B, A):
            dalej
        self.assertIs(BNotMeta, type(C2))
        self.assertEqual(['BNotMeta', 'ANotMeta'], new_calls)
        new_calls.clear()
        self.assertEqual(['BNotMeta', 'ANotMeta'], prepare_calls)
        prepare_calls.clear()

        # This jest a TypeError, because of a metaclass conflict:
        # BNotMeta jest neither a subclass, nor a superclass of type
        przy self.assertRaises(TypeError):
            klasa D(C, metaclass=type):
                dalej

        klasa E(C, metaclass=ANotMeta):
            dalej
        self.assertIs(BNotMeta, type(E))
        self.assertEqual(['BNotMeta', 'ANotMeta'], new_calls)
        new_calls.clear()
        self.assertEqual(['BNotMeta', 'ANotMeta'], prepare_calls)
        prepare_calls.clear()

        klasa F(object(), C):
            dalej
        self.assertIs(BNotMeta, type(F))
        self.assertEqual(['BNotMeta', 'ANotMeta'], new_calls)
        new_calls.clear()
        self.assertEqual(['BNotMeta', 'ANotMeta'], prepare_calls)
        prepare_calls.clear()

        klasa F2(C, object()):
            dalej
        self.assertIs(BNotMeta, type(F2))
        self.assertEqual(['BNotMeta', 'ANotMeta'], new_calls)
        new_calls.clear()
        self.assertEqual(['BNotMeta', 'ANotMeta'], prepare_calls)
        prepare_calls.clear()

        # TypeError: BNotMeta jest neither a
        # subclass, nor a superclass of int
        przy self.assertRaises(TypeError):
            klasa X(C, int()):
                dalej
        przy self.assertRaises(TypeError):
            klasa X(int(), C):
                dalej

    def test_module_subclasses(self):
        # Testing Python subclass of module...
        log = []
        MT = type(sys)
        klasa MM(MT):
            def __init__(self, name):
                MT.__init__(self, name)
            def __getattribute__(self, name):
                log.append(("getattr", name))
                zwróć MT.__getattribute__(self, name)
            def __setattr__(self, name, value):
                log.append(("setattr", name, value))
                MT.__setattr__(self, name, value)
            def __delattr__(self, name):
                log.append(("delattr", name))
                MT.__delattr__(self, name)
        a = MM("a")
        a.foo = 12
        x = a.foo
        usuń a.foo
        self.assertEqual(log, [("setattr", "foo", 12),
                               ("getattr", "foo"),
                               ("delattr", "foo")])

        # http://python.org/sf/1174712
        spróbuj:
            klasa Module(types.ModuleType, str):
                dalej
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("inheriting z ModuleType oraz str at the same time "
                      "should fail")

    def test_multiple_inheritance(self):
        # Testing multiple inheritance...
        klasa C(object):
            def __init__(self):
                self.__state = 0
            def getstate(self):
                zwróć self.__state
            def setstate(self, state):
                self.__state = state
        a = C()
        self.assertEqual(a.getstate(), 0)
        a.setstate(10)
        self.assertEqual(a.getstate(), 10)
        klasa D(dict, C):
            def __init__(self):
                type({}).__init__(self)
                C.__init__(self)
        d = D()
        self.assertEqual(list(d.keys()), [])
        d["hello"] = "world"
        self.assertEqual(list(d.items()), [("hello", "world")])
        self.assertEqual(d["hello"], "world")
        self.assertEqual(d.getstate(), 0)
        d.setstate(10)
        self.assertEqual(d.getstate(), 10)
        self.assertEqual(D.__mro__, (D, dict, C, object))

        # SF bug #442833
        klasa Node(object):
            def __int__(self):
                zwróć int(self.foo())
            def foo(self):
                zwróć "23"
        klasa Frag(Node, list):
            def foo(self):
                zwróć "42"
        self.assertEqual(Node().__int__(), 23)
        self.assertEqual(int(Node()), 23)
        self.assertEqual(Frag().__int__(), 42)
        self.assertEqual(int(Frag()), 42)

    def test_diamond_inheritence(self):
        # Testing multiple inheritance special cases...
        klasa A(object):
            def spam(self): zwróć "A"
        self.assertEqual(A().spam(), "A")
        klasa B(A):
            def boo(self): zwróć "B"
            def spam(self): zwróć "B"
        self.assertEqual(B().spam(), "B")
        self.assertEqual(B().boo(), "B")
        klasa C(A):
            def boo(self): zwróć "C"
        self.assertEqual(C().spam(), "A")
        self.assertEqual(C().boo(), "C")
        klasa D(B, C): dalej
        self.assertEqual(D().spam(), "B")
        self.assertEqual(D().boo(), "B")
        self.assertEqual(D.__mro__, (D, B, C, A, object))
        klasa E(C, B): dalej
        self.assertEqual(E().spam(), "B")
        self.assertEqual(E().boo(), "C")
        self.assertEqual(E.__mro__, (E, C, B, A, object))
        # MRO order disagreement
        spróbuj:
            klasa F(D, E): dalej
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("expected MRO order disagreement (F)")
        spróbuj:
            klasa G(E, D): dalej
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("expected MRO order disagreement (G)")

    # see thread python-dev/2002-October/029035.html
    def test_ex5_from_c3_switch(self):
        # Testing ex5 z C3 switch discussion...
        klasa A(object): dalej
        klasa B(object): dalej
        klasa C(object): dalej
        klasa X(A): dalej
        klasa Y(A): dalej
        klasa Z(X,B,Y,C): dalej
        self.assertEqual(Z.__mro__, (Z, X, B, Y, A, C, object))

    # see "A Monotonic Superclass Linearization dla Dylan",
    # by Kim Barrett et al. (OOPSLA 1996)
    def test_monotonicity(self):
        # Testing MRO monotonicity...
        klasa Boat(object): dalej
        klasa DayBoat(Boat): dalej
        klasa WheelBoat(Boat): dalej
        klasa EngineLess(DayBoat): dalej
        klasa SmallMultihull(DayBoat): dalej
        klasa PedalWheelBoat(EngineLess,WheelBoat): dalej
        klasa SmallCatamaran(SmallMultihull): dalej
        klasa Pedalo(PedalWheelBoat,SmallCatamaran): dalej

        self.assertEqual(PedalWheelBoat.__mro__,
              (PedalWheelBoat, EngineLess, DayBoat, WheelBoat, Boat, object))
        self.assertEqual(SmallCatamaran.__mro__,
              (SmallCatamaran, SmallMultihull, DayBoat, Boat, object))
        self.assertEqual(Pedalo.__mro__,
              (Pedalo, PedalWheelBoat, EngineLess, SmallCatamaran,
               SmallMultihull, DayBoat, WheelBoat, Boat, object))

    # see "A Monotonic Superclass Linearization dla Dylan",
    # by Kim Barrett et al. (OOPSLA 1996)
    def test_consistency_with_epg(self):
        # Testing consistency przy EPG...
        klasa Pane(object): dalej
        klasa ScrollingMixin(object): dalej
        klasa EditingMixin(object): dalej
        klasa ScrollablePane(Pane,ScrollingMixin): dalej
        klasa EditablePane(Pane,EditingMixin): dalej
        klasa EditableScrollablePane(ScrollablePane,EditablePane): dalej

        self.assertEqual(EditableScrollablePane.__mro__,
              (EditableScrollablePane, ScrollablePane, EditablePane, Pane,
                ScrollingMixin, EditingMixin, object))

    def test_mro_disagreement(self):
        # Testing error messages dla MRO disagreement...
        mro_err_msg = """Cannot create a consistent method resolution
order (MRO) dla bases """

        def podnieśs(exc, expected, callable, *args):
            spróbuj:
                callable(*args)
            wyjąwszy exc jako msg:
                # the exact msg jest generally considered an impl detail
                jeżeli support.check_impl_detail():
                    jeżeli nie str(msg).startswith(expected):
                        self.fail("Message %r, expected %r" %
                                  (str(msg), expected))
            inaczej:
                self.fail("Expected %s" % exc)

        klasa A(object): dalej
        klasa B(A): dalej
        klasa C(object): dalej

        # Test some very simple errors
        podnieśs(TypeError, "duplicate base klasa A",
               type, "X", (A, A), {})
        podnieśs(TypeError, mro_err_msg,
               type, "X", (A, B), {})
        podnieśs(TypeError, mro_err_msg,
               type, "X", (A, C, B), {})
        # Test a slightly more complex error
        klasa GridLayout(object): dalej
        klasa HorizontalGrid(GridLayout): dalej
        klasa VerticalGrid(GridLayout): dalej
        klasa HVGrid(HorizontalGrid, VerticalGrid): dalej
        klasa VHGrid(VerticalGrid, HorizontalGrid): dalej
        podnieśs(TypeError, mro_err_msg,
               type, "ConfusedGrid", (HVGrid, VHGrid), {})

    def test_object_class(self):
        # Testing object class...
        a = object()
        self.assertEqual(a.__class__, object)
        self.assertEqual(type(a), object)
        b = object()
        self.assertNotEqual(a, b)
        self.assertNotHasAttr(a, "foo")
        spróbuj:
            a.foo = 12
        wyjąwszy (AttributeError, TypeError):
            dalej
        inaczej:
            self.fail("object() should nie allow setting a foo attribute")
        self.assertNotHasAttr(object(), "__dict__")

        klasa Cdict(object):
            dalej
        x = Cdict()
        self.assertEqual(x.__dict__, {})
        x.foo = 1
        self.assertEqual(x.foo, 1)
        self.assertEqual(x.__dict__, {'foo': 1})

    def test_object_class_assignment_between_heaptypes_and_nonheaptypes(self):
        klasa SubType(types.ModuleType):
            a = 1

        m = types.ModuleType("m")
        self.assertPrawda(m.__class__ jest types.ModuleType)
        self.assertNieprawda(hasattr(m, "a"))

        m.__class__ = SubType
        self.assertPrawda(m.__class__ jest SubType)
        self.assertPrawda(hasattr(m, "a"))

        m.__class__ = types.ModuleType
        self.assertPrawda(m.__class__ jest types.ModuleType)
        self.assertNieprawda(hasattr(m, "a"))

        # Make sure that builtin immutable objects don't support __class__
        # assignment, because the object instances may be interned.
        # We set __slots__ = () to ensure that the subclasses are
        # memory-layout compatible, oraz thus otherwise reasonable candidates
        # dla __class__ assignment.

        # The following types have immutable instances, but are nie
        # subclassable oraz thus don't need to be checked:
        #   NicType, bool

        klasa MyInt(int):
            __slots__ = ()
        przy self.assertRaises(TypeError):
            (1).__class__ = MyInt

        klasa MyFloat(float):
            __slots__ = ()
        przy self.assertRaises(TypeError):
            (1.0).__class__ = MyFloat

        klasa MyComplex(complex):
            __slots__ = ()
        przy self.assertRaises(TypeError):
            (1 + 2j).__class__ = MyComplex

        klasa MyStr(str):
            __slots__ = ()
        przy self.assertRaises(TypeError):
            "a".__class__ = MyStr

        klasa MyBytes(bytes):
            __slots__ = ()
        przy self.assertRaises(TypeError):
            b"a".__class__ = MyBytes

        klasa MyTuple(tuple):
            __slots__ = ()
        przy self.assertRaises(TypeError):
            ().__class__ = MyTuple

        klasa MyFrozenSet(frozenset):
            __slots__ = ()
        przy self.assertRaises(TypeError):
            frozenset().__class__ = MyFrozenSet

    def test_slots(self):
        # Testing __slots__...
        klasa C0(object):
            __slots__ = []
        x = C0()
        self.assertNotHasAttr(x, "__dict__")
        self.assertNotHasAttr(x, "foo")

        klasa C1(object):
            __slots__ = ['a']
        x = C1()
        self.assertNotHasAttr(x, "__dict__")
        self.assertNotHasAttr(x, "a")
        x.a = 1
        self.assertEqual(x.a, 1)
        x.a = Nic
        self.assertEqual(x.a, Nic)
        usuń x.a
        self.assertNotHasAttr(x, "a")

        klasa C3(object):
            __slots__ = ['a', 'b', 'c']
        x = C3()
        self.assertNotHasAttr(x, "__dict__")
        self.assertNotHasAttr(x, 'a')
        self.assertNotHasAttr(x, 'b')
        self.assertNotHasAttr(x, 'c')
        x.a = 1
        x.b = 2
        x.c = 3
        self.assertEqual(x.a, 1)
        self.assertEqual(x.b, 2)
        self.assertEqual(x.c, 3)

        klasa C4(object):
            """Validate name mangling"""
            __slots__ = ['__a']
            def __init__(self, value):
                self.__a = value
            def get(self):
                zwróć self.__a
        x = C4(5)
        self.assertNotHasAttr(x, '__dict__')
        self.assertNotHasAttr(x, '__a')
        self.assertEqual(x.get(), 5)
        spróbuj:
            x.__a = 6
        wyjąwszy AttributeError:
            dalej
        inaczej:
            self.fail("Double underscored names nie mangled")

        # Make sure slot names are proper identifiers
        spróbuj:
            klasa C(object):
                __slots__ = [Nic]
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("[Nic] slots nie caught")
        spróbuj:
            klasa C(object):
                __slots__ = ["foo bar"]
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("['foo bar'] slots nie caught")
        spróbuj:
            klasa C(object):
                __slots__ = ["foo\0bar"]
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("['foo\\0bar'] slots nie caught")
        spróbuj:
            klasa C(object):
                __slots__ = ["1"]
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("['1'] slots nie caught")
        spróbuj:
            klasa C(object):
                __slots__ = [""]
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("[''] slots nie caught")
        klasa C(object):
            __slots__ = ["a", "a_b", "_a", "A0123456789Z"]
        # XXX(nnorwitz): was there supposed to be something tested
        # z the klasa above?

        # Test a single string jest nie expanded jako a sequence.
        klasa C(object):
            __slots__ = "abc"
        c = C()
        c.abc = 5
        self.assertEqual(c.abc, 5)

        # Test unicode slot names
        # Test a single unicode string jest nie expanded jako a sequence.
        klasa C(object):
            __slots__ = "abc"
        c = C()
        c.abc = 5
        self.assertEqual(c.abc, 5)

        # _unicode_to_string used to modify slots w certain circumstances
        slots = ("foo", "bar")
        klasa C(object):
            __slots__ = slots
        x = C()
        x.foo = 5
        self.assertEqual(x.foo, 5)
        self.assertIs(type(slots[0]), str)
        # this used to leak references
        spróbuj:
            klasa C(object):
                __slots__ = [chr(128)]
        wyjąwszy (TypeError, UnicodeEncodeError):
            dalej
        inaczej:
            self.fail("[chr(128)] slots nie caught")

        # Test leaks
        klasa Counted(object):
            counter = 0    # counts the number of instances alive
            def __init__(self):
                Counted.counter += 1
            def __del__(self):
                Counted.counter -= 1
        klasa C(object):
            __slots__ = ['a', 'b', 'c']
        x = C()
        x.a = Counted()
        x.b = Counted()
        x.c = Counted()
        self.assertEqual(Counted.counter, 3)
        usuń x
        support.gc_collect()
        self.assertEqual(Counted.counter, 0)
        klasa D(C):
            dalej
        x = D()
        x.a = Counted()
        x.z = Counted()
        self.assertEqual(Counted.counter, 2)
        usuń x
        support.gc_collect()
        self.assertEqual(Counted.counter, 0)
        klasa E(D):
            __slots__ = ['e']
        x = E()
        x.a = Counted()
        x.z = Counted()
        x.e = Counted()
        self.assertEqual(Counted.counter, 3)
        usuń x
        support.gc_collect()
        self.assertEqual(Counted.counter, 0)

        # Test cyclical leaks [SF bug 519621]
        klasa F(object):
            __slots__ = ['a', 'b']
        s = F()
        s.a = [Counted(), s]
        self.assertEqual(Counted.counter, 1)
        s = Nic
        support.gc_collect()
        self.assertEqual(Counted.counter, 0)

        # Test lookup leaks [SF bug 572567]
        jeżeli hasattr(gc, 'get_objects'):
            klasa G(object):
                def __eq__(self, other):
                    zwróć Nieprawda
            g = G()
            orig_objects = len(gc.get_objects())
            dla i w range(10):
                g==g
            new_objects = len(gc.get_objects())
            self.assertEqual(orig_objects, new_objects)

        klasa H(object):
            __slots__ = ['a', 'b']
            def __init__(self):
                self.a = 1
                self.b = 2
            def __del__(self_):
                self.assertEqual(self_.a, 1)
                self.assertEqual(self_.b, 2)
        przy support.captured_output('stderr') jako s:
            h = H()
            usuń h
        self.assertEqual(s.getvalue(), '')

        klasa X(object):
            __slots__ = "a"
        przy self.assertRaises(AttributeError):
            usuń X().a

    def test_slots_special(self):
        # Testing __dict__ oraz __weakref__ w __slots__...
        klasa D(object):
            __slots__ = ["__dict__"]
        a = D()
        self.assertHasAttr(a, "__dict__")
        self.assertNotHasAttr(a, "__weakref__")
        a.foo = 42
        self.assertEqual(a.__dict__, {"foo": 42})

        klasa W(object):
            __slots__ = ["__weakref__"]
        a = W()
        self.assertHasAttr(a, "__weakref__")
        self.assertNotHasAttr(a, "__dict__")
        spróbuj:
            a.foo = 42
        wyjąwszy AttributeError:
            dalej
        inaczej:
            self.fail("shouldn't be allowed to set a.foo")

        klasa C1(W, D):
            __slots__ = []
        a = C1()
        self.assertHasAttr(a, "__dict__")
        self.assertHasAttr(a, "__weakref__")
        a.foo = 42
        self.assertEqual(a.__dict__, {"foo": 42})

        klasa C2(D, W):
            __slots__ = []
        a = C2()
        self.assertHasAttr(a, "__dict__")
        self.assertHasAttr(a, "__weakref__")
        a.foo = 42
        self.assertEqual(a.__dict__, {"foo": 42})

    def test_slots_descriptor(self):
        # Issue2115: slot descriptors did nie correctly check
        # the type of the given object
        zaimportuj abc
        klasa MyABC(metaclass=abc.ABCMeta):
            __slots__ = "a"

        klasa Unrelated(object):
            dalej
        MyABC.register(Unrelated)

        u = Unrelated()
        self.assertIsInstance(u, MyABC)

        # This used to crash
        self.assertRaises(TypeError, MyABC.a.__set__, u, 3)

    def test_dynamics(self):
        # Testing klasa attribute propagation...
        klasa D(object):
            dalej
        klasa E(D):
            dalej
        klasa F(D):
            dalej
        D.foo = 1
        self.assertEqual(D.foo, 1)
        # Test that dynamic attributes are inherited
        self.assertEqual(E.foo, 1)
        self.assertEqual(F.foo, 1)
        # Test dynamic instances
        klasa C(object):
            dalej
        a = C()
        self.assertNotHasAttr(a, "foobar")
        C.foobar = 2
        self.assertEqual(a.foobar, 2)
        C.method = lambda self: 42
        self.assertEqual(a.method(), 42)
        C.__repr__ = lambda self: "C()"
        self.assertEqual(repr(a), "C()")
        C.__int__ = lambda self: 100
        self.assertEqual(int(a), 100)
        self.assertEqual(a.foobar, 2)
        self.assertNotHasAttr(a, "spam")
        def mygetattr(self, name):
            jeżeli name == "spam":
                zwróć "spam"
            podnieś AttributeError
        C.__getattr__ = mygetattr
        self.assertEqual(a.spam, "spam")
        a.new = 12
        self.assertEqual(a.new, 12)
        def mysetattr(self, name, value):
            jeżeli name == "spam":
                podnieś AttributeError
            zwróć object.__setattr__(self, name, value)
        C.__setattr__ = mysetattr
        spróbuj:
            a.spam = "not spam"
        wyjąwszy AttributeError:
            dalej
        inaczej:
            self.fail("expected AttributeError")
        self.assertEqual(a.spam, "spam")
        klasa D(C):
            dalej
        d = D()
        d.foo = 1
        self.assertEqual(d.foo, 1)

        # Test handling of int*seq oraz seq*int
        klasa I(int):
            dalej
        self.assertEqual("a"*I(2), "aa")
        self.assertEqual(I(2)*"a", "aa")
        self.assertEqual(2*I(3), 6)
        self.assertEqual(I(3)*2, 6)
        self.assertEqual(I(3)*I(2), 6)

        # Test comparison of classes przy dynamic metaclasses
        klasa dynamicmetaclass(type):
            dalej
        klasa someclass(metaclass=dynamicmetaclass):
            dalej
        self.assertNotEqual(someclass, object)

    def test_errors(self):
        # Testing errors...
        spróbuj:
            klasa C(list, dict):
                dalej
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("inheritance z both list oraz dict should be illegal")

        spróbuj:
            klasa C(object, Nic):
                dalej
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("inheritance z non-type should be illegal")
        klasa Classic:
            dalej

        spróbuj:
            klasa C(type(len)):
                dalej
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("inheritance z CFunction should be illegal")

        spróbuj:
            klasa C(object):
                __slots__ = 1
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("__slots__ = 1 should be illegal")

        spróbuj:
            klasa C(object):
                __slots__ = [1]
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("__slots__ = [1] should be illegal")

        klasa M1(type):
            dalej
        klasa M2(type):
            dalej
        klasa A1(object, metaclass=M1):
            dalej
        klasa A2(object, metaclass=M2):
            dalej
        spróbuj:
            klasa B(A1, A2):
                dalej
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("finding the most derived metaclass should have failed")

    def test_classmethods(self):
        # Testing klasa methods...
        klasa C(object):
            def foo(*a): zwróć a
            goo = classmethod(foo)
        c = C()
        self.assertEqual(C.goo(1), (C, 1))
        self.assertEqual(c.goo(1), (C, 1))
        self.assertEqual(c.foo(1), (c, 1))
        klasa D(C):
            dalej
        d = D()
        self.assertEqual(D.goo(1), (D, 1))
        self.assertEqual(d.goo(1), (D, 1))
        self.assertEqual(d.foo(1), (d, 1))
        self.assertEqual(D.foo(d, 1), (d, 1))
        # Test dla a specific crash (SF bug 528132)
        def f(cls, arg): zwróć (cls, arg)
        ff = classmethod(f)
        self.assertEqual(ff.__get__(0, int)(42), (int, 42))
        self.assertEqual(ff.__get__(0)(42), (int, 42))

        # Test super() przy classmethods (SF bug 535444)
        self.assertEqual(C.goo.__self__, C)
        self.assertEqual(D.goo.__self__, D)
        self.assertEqual(super(D,D).goo.__self__, D)
        self.assertEqual(super(D,d).goo.__self__, D)
        self.assertEqual(super(D,D).goo(), (D,))
        self.assertEqual(super(D,d).goo(), (D,))

        # Verify that a non-callable will podnieś
        meth = classmethod(1).__get__(1)
        self.assertRaises(TypeError, meth)

        # Verify that classmethod() doesn't allow keyword args
        spróbuj:
            classmethod(f, kw=1)
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("classmethod shouldn't accept keyword args")

        cm = classmethod(f)
        self.assertEqual(cm.__dict__, {})
        cm.x = 42
        self.assertEqual(cm.x, 42)
        self.assertEqual(cm.__dict__, {"x" : 42})
        usuń cm.x
        self.assertNotHasAttr(cm, "x")

    @support.impl_detail("the module 'xxsubtype' jest internal")
    def test_classmethods_in_c(self):
        # Testing C-based klasa methods...
        zaimportuj xxsubtype jako spam
        a = (1, 2, 3)
        d = {'abc': 123}
        x, a1, d1 = spam.spamlist.classmeth(*a, **d)
        self.assertEqual(x, spam.spamlist)
        self.assertEqual(a, a1)
        self.assertEqual(d, d1)
        x, a1, d1 = spam.spamlist().classmeth(*a, **d)
        self.assertEqual(x, spam.spamlist)
        self.assertEqual(a, a1)
        self.assertEqual(d, d1)
        spam_cm = spam.spamlist.__dict__['classmeth']
        x2, a2, d2 = spam_cm(spam.spamlist, *a, **d)
        self.assertEqual(x2, spam.spamlist)
        self.assertEqual(a2, a1)
        self.assertEqual(d2, d1)
        klasa SubSpam(spam.spamlist): dalej
        x2, a2, d2 = spam_cm(SubSpam, *a, **d)
        self.assertEqual(x2, SubSpam)
        self.assertEqual(a2, a1)
        self.assertEqual(d2, d1)
        przy self.assertRaises(TypeError):
            spam_cm()
        przy self.assertRaises(TypeError):
            spam_cm(spam.spamlist())
        przy self.assertRaises(TypeError):
            spam_cm(list)

    def test_staticmethods(self):
        # Testing static methods...
        klasa C(object):
            def foo(*a): zwróć a
            goo = staticmethod(foo)
        c = C()
        self.assertEqual(C.goo(1), (1,))
        self.assertEqual(c.goo(1), (1,))
        self.assertEqual(c.foo(1), (c, 1,))
        klasa D(C):
            dalej
        d = D()
        self.assertEqual(D.goo(1), (1,))
        self.assertEqual(d.goo(1), (1,))
        self.assertEqual(d.foo(1), (d, 1))
        self.assertEqual(D.foo(d, 1), (d, 1))
        sm = staticmethod(Nic)
        self.assertEqual(sm.__dict__, {})
        sm.x = 42
        self.assertEqual(sm.x, 42)
        self.assertEqual(sm.__dict__, {"x" : 42})
        usuń sm.x
        self.assertNotHasAttr(sm, "x")

    @support.impl_detail("the module 'xxsubtype' jest internal")
    def test_staticmethods_in_c(self):
        # Testing C-based static methods...
        zaimportuj xxsubtype jako spam
        a = (1, 2, 3)
        d = {"abc": 123}
        x, a1, d1 = spam.spamlist.staticmeth(*a, **d)
        self.assertEqual(x, Nic)
        self.assertEqual(a, a1)
        self.assertEqual(d, d1)
        x, a1, d2 = spam.spamlist().staticmeth(*a, **d)
        self.assertEqual(x, Nic)
        self.assertEqual(a, a1)
        self.assertEqual(d, d1)

    def test_classic(self):
        # Testing classic classes...
        klasa C:
            def foo(*a): zwróć a
            goo = classmethod(foo)
        c = C()
        self.assertEqual(C.goo(1), (C, 1))
        self.assertEqual(c.goo(1), (C, 1))
        self.assertEqual(c.foo(1), (c, 1))
        klasa D(C):
            dalej
        d = D()
        self.assertEqual(D.goo(1), (D, 1))
        self.assertEqual(d.goo(1), (D, 1))
        self.assertEqual(d.foo(1), (d, 1))
        self.assertEqual(D.foo(d, 1), (d, 1))
        klasa E: # *not* subclassing z C
            foo = C.foo
        self.assertEqual(E().foo.__func__, C.foo) # i.e., unbound
        self.assertPrawda(repr(C.foo.__get__(C())).startswith("<bound method "))

    def test_compattr(self):
        # Testing computed attributes...
        klasa C(object):
            klasa computed_attribute(object):
                def __init__(self, get, set=Nic, delete=Nic):
                    self.__get = get
                    self.__set = set
                    self.__delete = delete
                def __get__(self, obj, type=Nic):
                    zwróć self.__get(obj)
                def __set__(self, obj, value):
                    zwróć self.__set(obj, value)
                def __delete__(self, obj):
                    zwróć self.__delete(obj)
            def __init__(self):
                self.__x = 0
            def __get_x(self):
                x = self.__x
                self.__x = x+1
                zwróć x
            def __set_x(self, x):
                self.__x = x
            def __delete_x(self):
                usuń self.__x
            x = computed_attribute(__get_x, __set_x, __delete_x)
        a = C()
        self.assertEqual(a.x, 0)
        self.assertEqual(a.x, 1)
        a.x = 10
        self.assertEqual(a.x, 10)
        self.assertEqual(a.x, 11)
        usuń a.x
        self.assertNotHasAttr(a, 'x')

    def test_newslots(self):
        # Testing __new__ slot override...
        klasa C(list):
            def __new__(cls):
                self = list.__new__(cls)
                self.foo = 1
                zwróć self
            def __init__(self):
                self.foo = self.foo + 2
        a = C()
        self.assertEqual(a.foo, 3)
        self.assertEqual(a.__class__, C)
        klasa D(C):
            dalej
        b = D()
        self.assertEqual(b.foo, 3)
        self.assertEqual(b.__class__, D)

    def test_altmro(self):
        # Testing mro() oraz overriding it...
        klasa A(object):
            def f(self): zwróć "A"
        klasa B(A):
            dalej
        klasa C(A):
            def f(self): zwróć "C"
        klasa D(B, C):
            dalej
        self.assertEqual(D.mro(), [D, B, C, A, object])
        self.assertEqual(D.__mro__, (D, B, C, A, object))
        self.assertEqual(D().f(), "C")

        klasa PerverseMetaType(type):
            def mro(cls):
                L = type.mro(cls)
                L.reverse()
                zwróć L
        klasa X(D,B,C,A, metaclass=PerverseMetaType):
            dalej
        self.assertEqual(X.__mro__, (object, A, C, B, D, X))
        self.assertEqual(X().f(), "A")

        spróbuj:
            klasa _metaclass(type):
                def mro(self):
                    zwróć [self, dict, object]
            klasa X(object, metaclass=_metaclass):
                dalej
            # In CPython, the klasa creation above already podnieśs
            # TypeError, jako a protection against the fact that
            # instances of X would segfault it.  In other Python
            # implementations it would be ok to let the klasa X
            # be created, but instead get a clean TypeError on the
            # __setitem__ below.
            x = object.__new__(X)
            x[5] = 6
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("devious mro() zwróć nie caught")

        spróbuj:
            klasa _metaclass(type):
                def mro(self):
                    zwróć [1]
            klasa X(object, metaclass=_metaclass):
                dalej
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("non-class mro() zwróć nie caught")

        spróbuj:
            klasa _metaclass(type):
                def mro(self):
                    zwróć 1
            klasa X(object, metaclass=_metaclass):
                dalej
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("non-sequence mro() zwróć nie caught")

    def test_overloading(self):
        # Testing operator overloading...

        klasa B(object):
            "Intermediate klasa because object doesn't have a __setattr__"

        klasa C(B):
            def __getattr__(self, name):
                jeżeli name == "foo":
                    zwróć ("getattr", name)
                inaczej:
                    podnieś AttributeError
            def __setattr__(self, name, value):
                jeżeli name == "foo":
                    self.setattr = (name, value)
                inaczej:
                    zwróć B.__setattr__(self, name, value)
            def __delattr__(self, name):
                jeżeli name == "foo":
                    self.delattr = name
                inaczej:
                    zwróć B.__delattr__(self, name)

            def __getitem__(self, key):
                zwróć ("getitem", key)
            def __setitem__(self, key, value):
                self.setitem = (key, value)
            def __delitem__(self, key):
                self.delitem = key

        a = C()
        self.assertEqual(a.foo, ("getattr", "foo"))
        a.foo = 12
        self.assertEqual(a.setattr, ("foo", 12))
        usuń a.foo
        self.assertEqual(a.delattr, "foo")

        self.assertEqual(a[12], ("getitem", 12))
        a[12] = 21
        self.assertEqual(a.setitem, (12, 21))
        usuń a[12]
        self.assertEqual(a.delitem, 12)

        self.assertEqual(a[0:10], ("getitem", slice(0, 10)))
        a[0:10] = "foo"
        self.assertEqual(a.setitem, (slice(0, 10), "foo"))
        usuń a[0:10]
        self.assertEqual(a.delitem, (slice(0, 10)))

    def test_methods(self):
        # Testing methods...
        klasa C(object):
            def __init__(self, x):
                self.x = x
            def foo(self):
                zwróć self.x
        c1 = C(1)
        self.assertEqual(c1.foo(), 1)
        klasa D(C):
            boo = C.foo
            goo = c1.foo
        d2 = D(2)
        self.assertEqual(d2.foo(), 2)
        self.assertEqual(d2.boo(), 2)
        self.assertEqual(d2.goo(), 1)
        klasa E(object):
            foo = C.foo
        self.assertEqual(E().foo.__func__, C.foo) # i.e., unbound
        self.assertPrawda(repr(C.foo.__get__(C(1))).startswith("<bound method "))

    def test_special_method_lookup(self):
        # The lookup of special methods bypasses __getattr__ oraz
        # __getattribute__, but they still can be descriptors.

        def run_context(manager):
            przy manager:
                dalej
        def iden(self):
            zwróć self
        def hello(self):
            zwróć b"hello"
        def empty_seq(self):
            zwróć []
        def zero(self):
            zwróć 0
        def complex_num(self):
            zwróć 1j
        def stop(self):
            podnieś StopIteration
        def return_true(self, thing=Nic):
            zwróć Prawda
        def do_isinstance(obj):
            zwróć isinstance(int, obj)
        def do_issubclass(obj):
            zwróć issubclass(int, obj)
        def do_dict_missing(checker):
            klasa DictSub(checker.__class__, dict):
                dalej
            self.assertEqual(DictSub()["hi"], 4)
        def some_number(self_, key):
            self.assertEqual(key, "hi")
            zwróć 4
        def swallow(*args): dalej
        def format_impl(self, spec):
            zwróć "hello"

        # It would be nice to have every special method tested here, but I'm
        # only listing the ones I can remember outside of typeobject.c, since it
        # does it right.
        specials = [
            ("__bytes__", bytes, hello, set(), {}),
            ("__reversed__", reversed, empty_seq, set(), {}),
            ("__length_hint__", list, zero, set(),
             {"__iter__" : iden, "__next__" : stop}),
            ("__sizeof__", sys.getsizeof, zero, set(), {}),
            ("__instancecheck__", do_isinstance, return_true, set(), {}),
            ("__missing__", do_dict_missing, some_number,
             set(("__class__",)), {}),
            ("__subclasscheck__", do_issubclass, return_true,
             set(("__bases__",)), {}),
            ("__enter__", run_context, iden, set(), {"__exit__" : swallow}),
            ("__exit__", run_context, swallow, set(), {"__enter__" : iden}),
            ("__complex__", complex, complex_num, set(), {}),
            ("__format__", format, format_impl, set(), {}),
            ("__floor__", math.floor, zero, set(), {}),
            ("__trunc__", math.trunc, zero, set(), {}),
            ("__trunc__", int, zero, set(), {}),
            ("__ceil__", math.ceil, zero, set(), {}),
            ("__dir__", dir, empty_seq, set(), {}),
            ("__round__", round, zero, set(), {}),
            ]

        klasa Checker(object):
            def __getattr__(self, attr, test=self):
                test.fail("__getattr__ called przy {0}".format(attr))
            def __getattribute__(self, attr, test=self):
                jeżeli attr nie w ok:
                    test.fail("__getattribute__ called przy {0}".format(attr))
                zwróć object.__getattribute__(self, attr)
        klasa SpecialDescr(object):
            def __init__(self, impl):
                self.impl = impl
            def __get__(self, obj, owner):
                record.append(1)
                zwróć self.impl.__get__(obj, owner)
        klasa MyException(Exception):
            dalej
        klasa ErrDescr(object):
            def __get__(self, obj, owner):
                podnieś MyException

        dla name, runner, meth_impl, ok, env w specials:
            klasa X(Checker):
                dalej
            dla attr, obj w env.items():
                setattr(X, attr, obj)
            setattr(X, name, meth_impl)
            runner(X())

            record = []
            klasa X(Checker):
                dalej
            dla attr, obj w env.items():
                setattr(X, attr, obj)
            setattr(X, name, SpecialDescr(meth_impl))
            runner(X())
            self.assertEqual(record, [1], name)

            klasa X(Checker):
                dalej
            dla attr, obj w env.items():
                setattr(X, attr, obj)
            setattr(X, name, ErrDescr())
            self.assertRaises(MyException, runner, X())

    def test_specials(self):
        # Testing special operators...
        # Test operators like __hash__ dla which a built-in default exists

        # Test the default behavior dla static classes
        klasa C(object):
            def __getitem__(self, i):
                jeżeli 0 <= i < 10: zwróć i
                podnieś IndexError
        c1 = C()
        c2 = C()
        self.assertNieprawda(nie c1)
        self.assertNotEqual(id(c1), id(c2))
        hash(c1)
        hash(c2)
        self.assertEqual(c1, c1)
        self.assertPrawda(c1 != c2)
        self.assertNieprawda(c1 != c1)
        self.assertNieprawda(c1 == c2)
        # Note that the module name appears w str/repr, oraz that varies
        # depending on whether this test jest run standalone albo z a framework.
        self.assertGreaterEqual(str(c1).find('C object at '), 0)
        self.assertEqual(str(c1), repr(c1))
        self.assertNotIn(-1, c1)
        dla i w range(10):
            self.assertIn(i, c1)
        self.assertNotIn(10, c1)
        # Test the default behavior dla dynamic classes
        klasa D(object):
            def __getitem__(self, i):
                jeżeli 0 <= i < 10: zwróć i
                podnieś IndexError
        d1 = D()
        d2 = D()
        self.assertNieprawda(nie d1)
        self.assertNotEqual(id(d1), id(d2))
        hash(d1)
        hash(d2)
        self.assertEqual(d1, d1)
        self.assertNotEqual(d1, d2)
        self.assertNieprawda(d1 != d1)
        self.assertNieprawda(d1 == d2)
        # Note that the module name appears w str/repr, oraz that varies
        # depending on whether this test jest run standalone albo z a framework.
        self.assertGreaterEqual(str(d1).find('D object at '), 0)
        self.assertEqual(str(d1), repr(d1))
        self.assertNotIn(-1, d1)
        dla i w range(10):
            self.assertIn(i, d1)
        self.assertNotIn(10, d1)
        # Test overridden behavior
        klasa Proxy(object):
            def __init__(self, x):
                self.x = x
            def __bool__(self):
                zwróć nie not self.x
            def __hash__(self):
                zwróć hash(self.x)
            def __eq__(self, other):
                zwróć self.x == other
            def __ne__(self, other):
                zwróć self.x != other
            def __ge__(self, other):
                zwróć self.x >= other
            def __gt__(self, other):
                zwróć self.x > other
            def __le__(self, other):
                zwróć self.x <= other
            def __lt__(self, other):
                zwróć self.x < other
            def __str__(self):
                zwróć "Proxy:%s" % self.x
            def __repr__(self):
                zwróć "Proxy(%r)" % self.x
            def __contains__(self, value):
                zwróć value w self.x
        p0 = Proxy(0)
        p1 = Proxy(1)
        p_1 = Proxy(-1)
        self.assertNieprawda(p0)
        self.assertNieprawda(nie p1)
        self.assertEqual(hash(p0), hash(0))
        self.assertEqual(p0, p0)
        self.assertNotEqual(p0, p1)
        self.assertNieprawda(p0 != p0)
        self.assertEqual(nie p0, p1)
        self.assertPrawda(p0 < p1)
        self.assertPrawda(p0 <= p1)
        self.assertPrawda(p1 > p0)
        self.assertPrawda(p1 >= p0)
        self.assertEqual(str(p0), "Proxy:0")
        self.assertEqual(repr(p0), "Proxy(0)")
        p10 = Proxy(range(10))
        self.assertNotIn(-1, p10)
        dla i w range(10):
            self.assertIn(i, p10)
        self.assertNotIn(10, p10)

    def test_weakrefs(self):
        # Testing weak references...
        zaimportuj weakref
        klasa C(object):
            dalej
        c = C()
        r = weakref.ref(c)
        self.assertEqual(r(), c)
        usuń c
        support.gc_collect()
        self.assertEqual(r(), Nic)
        usuń r
        klasa NoWeak(object):
            __slots__ = ['foo']
        no = NoWeak()
        spróbuj:
            weakref.ref(no)
        wyjąwszy TypeError jako msg:
            self.assertIn("weak reference", str(msg))
        inaczej:
            self.fail("weakref.ref(no) should be illegal")
        klasa Weak(object):
            __slots__ = ['foo', '__weakref__']
        yes = Weak()
        r = weakref.ref(yes)
        self.assertEqual(r(), yes)
        usuń yes
        support.gc_collect()
        self.assertEqual(r(), Nic)
        usuń r

    def test_properties(self):
        # Testing property...
        klasa C(object):
            def getx(self):
                zwróć self.__x
            def setx(self, value):
                self.__x = value
            def delx(self):
                usuń self.__x
            x = property(getx, setx, delx, doc="I'm the x property.")
        a = C()
        self.assertNotHasAttr(a, "x")
        a.x = 42
        self.assertEqual(a._C__x, 42)
        self.assertEqual(a.x, 42)
        usuń a.x
        self.assertNotHasAttr(a, "x")
        self.assertNotHasAttr(a, "_C__x")
        C.x.__set__(a, 100)
        self.assertEqual(C.x.__get__(a), 100)
        C.x.__delete__(a)
        self.assertNotHasAttr(a, "x")

        raw = C.__dict__['x']
        self.assertIsInstance(raw, property)

        attrs = dir(raw)
        self.assertIn("__doc__", attrs)
        self.assertIn("fget", attrs)
        self.assertIn("fset", attrs)
        self.assertIn("fdel", attrs)

        self.assertEqual(raw.__doc__, "I'm the x property.")
        self.assertIs(raw.fget, C.__dict__['getx'])
        self.assertIs(raw.fset, C.__dict__['setx'])
        self.assertIs(raw.fdel, C.__dict__['delx'])

        dla attr w "fget", "fset", "fdel":
            spróbuj:
                setattr(raw, attr, 42)
            wyjąwszy AttributeError jako msg:
                jeżeli str(msg).find('readonly') < 0:
                    self.fail("when setting readonly attr %r on a property, "
                              "got unexpected AttributeError msg %r" % (attr, str(msg)))
            inaczej:
                self.fail("expected AttributeError z trying to set readonly %r "
                          "attr on a property" % attr)

        raw.__doc__ = 42
        self.assertEqual(raw.__doc__, 42)

        klasa D(object):
            __getitem__ = property(lambda s: 1/0)

        d = D()
        spróbuj:
            dla i w d:
                str(i)
        wyjąwszy ZeroDivisionError:
            dalej
        inaczej:
            self.fail("expected ZeroDivisionError z bad property")

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted przy -O2 oraz above")
    def test_properties_doc_attrib(self):
        klasa E(object):
            def getter(self):
                "getter method"
                zwróć 0
            def setter(self_, value):
                "setter method"
                dalej
            prop = property(getter)
            self.assertEqual(prop.__doc__, "getter method")
            prop2 = property(fset=setter)
            self.assertEqual(prop2.__doc__, Nic)

    @support.cpython_only
    def test_testcapi_no_segfault(self):
        # this segfaulted w 2.5b2
        spróbuj:
            zaimportuj _testcapi
        wyjąwszy ImportError:
            dalej
        inaczej:
            klasa X(object):
                p = property(_testcapi.test_with_docstring)

    def test_properties_plus(self):
        klasa C(object):
            foo = property(doc="hello")
            @foo.getter
            def foo(self):
                zwróć self._foo
            @foo.setter
            def foo(self, value):
                self._foo = abs(value)
            @foo.deleter
            def foo(self):
                usuń self._foo
        c = C()
        self.assertEqual(C.foo.__doc__, "hello")
        self.assertNotHasAttr(c, "foo")
        c.foo = -42
        self.assertHasAttr(c, '_foo')
        self.assertEqual(c._foo, 42)
        self.assertEqual(c.foo, 42)
        usuń c.foo
        self.assertNotHasAttr(c, '_foo')
        self.assertNotHasAttr(c, "foo")

        klasa D(C):
            @C.foo.deleter
            def foo(self):
                spróbuj:
                    usuń self._foo
                wyjąwszy AttributeError:
                    dalej
        d = D()
        d.foo = 24
        self.assertEqual(d.foo, 24)
        usuń d.foo
        usuń d.foo

        klasa E(object):
            @property
            def foo(self):
                zwróć self._foo
            @foo.setter
            def foo(self, value):
                podnieś RuntimeError
            @foo.setter
            def foo(self, value):
                self._foo = abs(value)
            @foo.deleter
            def foo(self, value=Nic):
                usuń self._foo

        e = E()
        e.foo = -42
        self.assertEqual(e.foo, 42)
        usuń e.foo

        klasa F(E):
            @E.foo.deleter
            def foo(self):
                usuń self._foo
            @foo.setter
            def foo(self, value):
                self._foo = max(0, value)
        f = F()
        f.foo = -10
        self.assertEqual(f.foo, 0)
        usuń f.foo

    def test_dict_constructors(self):
        # Testing dict constructor ...
        d = dict()
        self.assertEqual(d, {})
        d = dict({})
        self.assertEqual(d, {})
        d = dict({1: 2, 'a': 'b'})
        self.assertEqual(d, {1: 2, 'a': 'b'})
        self.assertEqual(d, dict(list(d.items())))
        self.assertEqual(d, dict(iter(d.items())))
        d = dict({'one':1, 'two':2})
        self.assertEqual(d, dict(one=1, two=2))
        self.assertEqual(d, dict(**d))
        self.assertEqual(d, dict({"one": 1}, two=2))
        self.assertEqual(d, dict([("two", 2)], one=1))
        self.assertEqual(d, dict([("one", 100), ("two", 200)], **d))
        self.assertEqual(d, dict(**d))

        dla badarg w 0, 0, 0j, "0", [0], (0,):
            spróbuj:
                dict(badarg)
            wyjąwszy TypeError:
                dalej
            wyjąwszy ValueError:
                jeżeli badarg == "0":
                    # It's a sequence, oraz its elements are also sequences (gotta
                    # love strings <wink>), but they aren't of length 2, so this
                    # one seemed better jako a ValueError than a TypeError.
                    dalej
                inaczej:
                    self.fail("no TypeError z dict(%r)" % badarg)
            inaczej:
                self.fail("no TypeError z dict(%r)" % badarg)

        spróbuj:
            dict({}, {})
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("no TypeError z dict({}, {})")

        klasa Mapping:
            # Lacks a .keys() method; will be added later.
            dict = {1:2, 3:4, 'a':1j}

        spróbuj:
            dict(Mapping())
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("no TypeError z dict(incomplete mapping)")

        Mapping.keys = lambda self: list(self.dict.keys())
        Mapping.__getitem__ = lambda self, i: self.dict[i]
        d = dict(Mapping())
        self.assertEqual(d, Mapping.dict)

        # Init z sequence of iterable objects, each producing a 2-sequence.
        klasa AddressBookEnspróbuj:
            def __init__(self, first, last):
                self.first = first
                self.last = last
            def __iter__(self):
                zwróć iter([self.first, self.last])

        d = dict([AddressBookEntry('Tim', 'Warsaw'),
                  AddressBookEntry('Barry', 'Peters'),
                  AddressBookEntry('Tim', 'Peters'),
                  AddressBookEntry('Barry', 'Warsaw')])
        self.assertEqual(d, {'Barry': 'Warsaw', 'Tim': 'Peters'})

        d = dict(zip(range(4), range(1, 5)))
        self.assertEqual(d, dict([(i, i+1) dla i w range(4)]))

        # Bad sequence lengths.
        dla bad w [('tooshort',)], [('too', 'long', 'by 1')]:
            spróbuj:
                dict(bad)
            wyjąwszy ValueError:
                dalej
            inaczej:
                self.fail("no ValueError z dict(%r)" % bad)

    def test_dir(self):
        # Testing dir() ...
        junk = 12
        self.assertEqual(dir(), ['junk', 'self'])
        usuń junk

        # Just make sure these don't blow up!
        dla arg w 2, 2, 2j, 2e0, [2], "2", b"2", (2,), {2:2}, type, self.test_dir:
            dir(arg)

        # Test dir on new-style classes.  Since these have object jako a
        # base class, a lot more gets sucked in.
        def interesting(strings):
            zwróć [s dla s w strings jeżeli nie s.startswith('_')]

        klasa C(object):
            Cdata = 1
            def Cmethod(self): dalej

        cstuff = ['Cdata', 'Cmethod']
        self.assertEqual(interesting(dir(C)), cstuff)

        c = C()
        self.assertEqual(interesting(dir(c)), cstuff)
        ## self.assertIn('__self__', dir(C.Cmethod))

        c.cdata = 2
        c.cmethod = lambda self: 0
        self.assertEqual(interesting(dir(c)), cstuff + ['cdata', 'cmethod'])
        ## self.assertIn('__self__', dir(c.Cmethod))

        klasa A(C):
            Adata = 1
            def Amethod(self): dalej

        astuff = ['Adata', 'Amethod'] + cstuff
        self.assertEqual(interesting(dir(A)), astuff)
        ## self.assertIn('__self__', dir(A.Amethod))
        a = A()
        self.assertEqual(interesting(dir(a)), astuff)
        a.adata = 42
        a.amethod = lambda self: 3
        self.assertEqual(interesting(dir(a)), astuff + ['adata', 'amethod'])
        ## self.assertIn('__self__', dir(a.Amethod))

        # Try a module subclass.
        klasa M(type(sys)):
            dalej
        minstance = M("m")
        minstance.b = 2
        minstance.a = 1
        default_attributes = ['__name__', '__doc__', '__package__',
                              '__loader__', '__spec__']
        names = [x dla x w dir(minstance) jeżeli x nie w default_attributes]
        self.assertEqual(names, ['a', 'b'])

        klasa M2(M):
            def getdict(self):
                zwróć "Not a dict!"
            __dict__ = property(getdict)

        m2instance = M2("m2")
        m2instance.b = 2
        m2instance.a = 1
        self.assertEqual(m2instance.__dict__, "Not a dict!")
        spróbuj:
            dir(m2instance)
        wyjąwszy TypeError:
            dalej

        # Two essentially featureless objects, just inheriting stuff from
        # object.
        self.assertEqual(dir(NotImplemented), dir(Ellipsis))

        # Nasty test case dla proxied objects
        klasa Wrapper(object):
            def __init__(self, obj):
                self.__obj = obj
            def __repr__(self):
                zwróć "Wrapper(%s)" % repr(self.__obj)
            def __getitem__(self, key):
                zwróć Wrapper(self.__obj[key])
            def __len__(self):
                zwróć len(self.__obj)
            def __getattr__(self, name):
                zwróć Wrapper(getattr(self.__obj, name))

        klasa C(object):
            def __getclass(self):
                zwróć Wrapper(type(self))
            __class__ = property(__getclass)

        dir(C()) # This used to segfault

    def test_supers(self):
        # Testing super...

        klasa A(object):
            def meth(self, a):
                zwróć "A(%r)" % a

        self.assertEqual(A().meth(1), "A(1)")

        klasa B(A):
            def __init__(self):
                self.__super = super(B, self)
            def meth(self, a):
                zwróć "B(%r)" % a + self.__super.meth(a)

        self.assertEqual(B().meth(2), "B(2)A(2)")

        klasa C(A):
            def meth(self, a):
                zwróć "C(%r)" % a + self.__super.meth(a)
        C._C__super = super(C)

        self.assertEqual(C().meth(3), "C(3)A(3)")

        klasa D(C, B):
            def meth(self, a):
                zwróć "D(%r)" % a + super(D, self).meth(a)

        self.assertEqual(D().meth(4), "D(4)C(4)B(4)A(4)")

        # Test dla subclassing super

        klasa mysuper(super):
            def __init__(self, *args):
                zwróć super(mysuper, self).__init__(*args)

        klasa E(D):
            def meth(self, a):
                zwróć "E(%r)" % a + mysuper(E, self).meth(a)

        self.assertEqual(E().meth(5), "E(5)D(5)C(5)B(5)A(5)")

        klasa F(E):
            def meth(self, a):
                s = self.__super # == mysuper(F, self)
                zwróć "F(%r)[%s]" % (a, s.__class__.__name__) + s.meth(a)
        F._F__super = mysuper(F)

        self.assertEqual(F().meth(6), "F(6)[mysuper]E(6)D(6)C(6)B(6)A(6)")

        # Make sure certain errors are podnieśd

        spróbuj:
            super(D, 42)
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("shouldn't allow super(D, 42)")

        spróbuj:
            super(D, C())
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("shouldn't allow super(D, C())")

        spróbuj:
            super(D).__get__(12)
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("shouldn't allow super(D).__get__(12)")

        spróbuj:
            super(D).__get__(C())
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("shouldn't allow super(D).__get__(C())")

        # Make sure data descriptors can be overridden oraz accessed via super
        # (new feature w Python 2.3)

        klasa DDbase(object):
            def getx(self): zwróć 42
            x = property(getx)

        klasa DDsub(DDbase):
            def getx(self): zwróć "hello"
            x = property(getx)

        dd = DDsub()
        self.assertEqual(dd.x, "hello")
        self.assertEqual(super(DDsub, dd).x, 42)

        # Ensure that super() lookup of descriptor z classmethod
        # works (SF ID# 743627)

        klasa Base(object):
            aProp = property(lambda self: "foo")

        klasa Sub(Base):
            @classmethod
            def test(klass):
                zwróć super(Sub,klass).aProp

        self.assertEqual(Sub.test(), Base.aProp)

        # Verify that super() doesn't allow keyword args
        spróbuj:
            super(Base, kw=1)
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.assertEqual("super shouldn't accept keyword args")

    def test_basic_inheritance(self):
        # Testing inheritance z basic types...

        klasa hexint(int):
            def __repr__(self):
                zwróć hex(self)
            def __add__(self, other):
                zwróć hexint(int.__add__(self, other))
            # (Note that overriding __radd__ doesn't work,
            # because the int type gets first dibs.)
        self.assertEqual(repr(hexint(7) + 9), "0x10")
        self.assertEqual(repr(hexint(1000) + 7), "0x3ef")
        a = hexint(12345)
        self.assertEqual(a, 12345)
        self.assertEqual(int(a), 12345)
        self.assertIs(int(a).__class__, int)
        self.assertEqual(hash(a), hash(12345))
        self.assertIs((+a).__class__, int)
        self.assertIs((a >> 0).__class__, int)
        self.assertIs((a << 0).__class__, int)
        self.assertIs((hexint(0) << 12).__class__, int)
        self.assertIs((hexint(0) >> 12).__class__, int)

        klasa octlong(int):
            __slots__ = []
            def __str__(self):
                zwróć oct(self)
            def __add__(self, other):
                zwróć self.__class__(super(octlong, self).__add__(other))
            __radd__ = __add__
        self.assertEqual(str(octlong(3) + 5), "0o10")
        # (Note that overriding __radd__ here only seems to work
        # because the example uses a short int left argument.)
        self.assertEqual(str(5 + octlong(3000)), "0o5675")
        a = octlong(12345)
        self.assertEqual(a, 12345)
        self.assertEqual(int(a), 12345)
        self.assertEqual(hash(a), hash(12345))
        self.assertIs(int(a).__class__, int)
        self.assertIs((+a).__class__, int)
        self.assertIs((-a).__class__, int)
        self.assertIs((-octlong(0)).__class__, int)
        self.assertIs((a >> 0).__class__, int)
        self.assertIs((a << 0).__class__, int)
        self.assertIs((a - 0).__class__, int)
        self.assertIs((a * 1).__class__, int)
        self.assertIs((a ** 1).__class__, int)
        self.assertIs((a // 1).__class__, int)
        self.assertIs((1 * a).__class__, int)
        self.assertIs((a | 0).__class__, int)
        self.assertIs((a ^ 0).__class__, int)
        self.assertIs((a & -1).__class__, int)
        self.assertIs((octlong(0) << 12).__class__, int)
        self.assertIs((octlong(0) >> 12).__class__, int)
        self.assertIs(abs(octlong(0)).__class__, int)

        # Because octlong overrides __add__, we can't check the absence of +0
        # optimizations using octlong.
        klasa longclone(int):
            dalej
        a = longclone(1)
        self.assertIs((a + 0).__class__, int)
        self.assertIs((0 + a).__class__, int)

        # Check that negative clones don't segfault
        a = longclone(-1)
        self.assertEqual(a.__dict__, {})
        self.assertEqual(int(a), -1)  # self.assertPrawda PyNumber_Long() copies the sign bit

        klasa precfloat(float):
            __slots__ = ['prec']
            def __init__(self, value=0.0, prec=12):
                self.prec = int(prec)
            def __repr__(self):
                zwróć "%.*g" % (self.prec, self)
        self.assertEqual(repr(precfloat(1.1)), "1.1")
        a = precfloat(12345)
        self.assertEqual(a, 12345.0)
        self.assertEqual(float(a), 12345.0)
        self.assertIs(float(a).__class__, float)
        self.assertEqual(hash(a), hash(12345.0))
        self.assertIs((+a).__class__, float)

        klasa madcomplex(complex):
            def __repr__(self):
                zwróć "%.17gj%+.17g" % (self.imag, self.real)
        a = madcomplex(-3, 4)
        self.assertEqual(repr(a), "4j-3")
        base = complex(-3, 4)
        self.assertEqual(base.__class__, complex)
        self.assertEqual(a, base)
        self.assertEqual(complex(a), base)
        self.assertEqual(complex(a).__class__, complex)
        a = madcomplex(a)  # just trying another form of the constructor
        self.assertEqual(repr(a), "4j-3")
        self.assertEqual(a, base)
        self.assertEqual(complex(a), base)
        self.assertEqual(complex(a).__class__, complex)
        self.assertEqual(hash(a), hash(base))
        self.assertEqual((+a).__class__, complex)
        self.assertEqual((a + 0).__class__, complex)
        self.assertEqual(a + 0, base)
        self.assertEqual((a - 0).__class__, complex)
        self.assertEqual(a - 0, base)
        self.assertEqual((a * 1).__class__, complex)
        self.assertEqual(a * 1, base)
        self.assertEqual((a / 1).__class__, complex)
        self.assertEqual(a / 1, base)

        klasa madtuple(tuple):
            _rev = Nic
            def rev(self):
                jeżeli self._rev jest nie Nic:
                    zwróć self._rev
                L = list(self)
                L.reverse()
                self._rev = self.__class__(L)
                zwróć self._rev
        a = madtuple((1,2,3,4,5,6,7,8,9,0))
        self.assertEqual(a, (1,2,3,4,5,6,7,8,9,0))
        self.assertEqual(a.rev(), madtuple((0,9,8,7,6,5,4,3,2,1)))
        self.assertEqual(a.rev().rev(), madtuple((1,2,3,4,5,6,7,8,9,0)))
        dla i w range(512):
            t = madtuple(range(i))
            u = t.rev()
            v = u.rev()
            self.assertEqual(v, t)
        a = madtuple((1,2,3,4,5))
        self.assertEqual(tuple(a), (1,2,3,4,5))
        self.assertIs(tuple(a).__class__, tuple)
        self.assertEqual(hash(a), hash((1,2,3,4,5)))
        self.assertIs(a[:].__class__, tuple)
        self.assertIs((a * 1).__class__, tuple)
        self.assertIs((a * 0).__class__, tuple)
        self.assertIs((a + ()).__class__, tuple)
        a = madtuple(())
        self.assertEqual(tuple(a), ())
        self.assertIs(tuple(a).__class__, tuple)
        self.assertIs((a + a).__class__, tuple)
        self.assertIs((a * 0).__class__, tuple)
        self.assertIs((a * 1).__class__, tuple)
        self.assertIs((a * 2).__class__, tuple)
        self.assertIs(a[:].__class__, tuple)

        klasa madstring(str):
            _rev = Nic
            def rev(self):
                jeżeli self._rev jest nie Nic:
                    zwróć self._rev
                L = list(self)
                L.reverse()
                self._rev = self.__class__("".join(L))
                zwróć self._rev
        s = madstring("abcdefghijklmnopqrstuvwxyz")
        self.assertEqual(s, "abcdefghijklmnopqrstuvwxyz")
        self.assertEqual(s.rev(), madstring("zyxwvutsrqponmlkjihgfedcba"))
        self.assertEqual(s.rev().rev(), madstring("abcdefghijklmnopqrstuvwxyz"))
        dla i w range(256):
            s = madstring("".join(map(chr, range(i))))
            t = s.rev()
            u = t.rev()
            self.assertEqual(u, s)
        s = madstring("12345")
        self.assertEqual(str(s), "12345")
        self.assertIs(str(s).__class__, str)

        base = "\x00" * 5
        s = madstring(base)
        self.assertEqual(s, base)
        self.assertEqual(str(s), base)
        self.assertIs(str(s).__class__, str)
        self.assertEqual(hash(s), hash(base))
        self.assertEqual({s: 1}[base], 1)
        self.assertEqual({base: 1}[s], 1)
        self.assertIs((s + "").__class__, str)
        self.assertEqual(s + "", base)
        self.assertIs(("" + s).__class__, str)
        self.assertEqual("" + s, base)
        self.assertIs((s * 0).__class__, str)
        self.assertEqual(s * 0, "")
        self.assertIs((s * 1).__class__, str)
        self.assertEqual(s * 1, base)
        self.assertIs((s * 2).__class__, str)
        self.assertEqual(s * 2, base + base)
        self.assertIs(s[:].__class__, str)
        self.assertEqual(s[:], base)
        self.assertIs(s[0:0].__class__, str)
        self.assertEqual(s[0:0], "")
        self.assertIs(s.strip().__class__, str)
        self.assertEqual(s.strip(), base)
        self.assertIs(s.lstrip().__class__, str)
        self.assertEqual(s.lstrip(), base)
        self.assertIs(s.rstrip().__class__, str)
        self.assertEqual(s.rstrip(), base)
        identitytab = {}
        self.assertIs(s.translate(identitytab).__class__, str)
        self.assertEqual(s.translate(identitytab), base)
        self.assertIs(s.replace("x", "x").__class__, str)
        self.assertEqual(s.replace("x", "x"), base)
        self.assertIs(s.ljust(len(s)).__class__, str)
        self.assertEqual(s.ljust(len(s)), base)
        self.assertIs(s.rjust(len(s)).__class__, str)
        self.assertEqual(s.rjust(len(s)), base)
        self.assertIs(s.center(len(s)).__class__, str)
        self.assertEqual(s.center(len(s)), base)
        self.assertIs(s.lower().__class__, str)
        self.assertEqual(s.lower(), base)

        klasa madunicode(str):
            _rev = Nic
            def rev(self):
                jeżeli self._rev jest nie Nic:
                    zwróć self._rev
                L = list(self)
                L.reverse()
                self._rev = self.__class__("".join(L))
                zwróć self._rev
        u = madunicode("ABCDEF")
        self.assertEqual(u, "ABCDEF")
        self.assertEqual(u.rev(), madunicode("FEDCBA"))
        self.assertEqual(u.rev().rev(), madunicode("ABCDEF"))
        base = "12345"
        u = madunicode(base)
        self.assertEqual(str(u), base)
        self.assertIs(str(u).__class__, str)
        self.assertEqual(hash(u), hash(base))
        self.assertEqual({u: 1}[base], 1)
        self.assertEqual({base: 1}[u], 1)
        self.assertIs(u.strip().__class__, str)
        self.assertEqual(u.strip(), base)
        self.assertIs(u.lstrip().__class__, str)
        self.assertEqual(u.lstrip(), base)
        self.assertIs(u.rstrip().__class__, str)
        self.assertEqual(u.rstrip(), base)
        self.assertIs(u.replace("x", "x").__class__, str)
        self.assertEqual(u.replace("x", "x"), base)
        self.assertIs(u.replace("xy", "xy").__class__, str)
        self.assertEqual(u.replace("xy", "xy"), base)
        self.assertIs(u.center(len(u)).__class__, str)
        self.assertEqual(u.center(len(u)), base)
        self.assertIs(u.ljust(len(u)).__class__, str)
        self.assertEqual(u.ljust(len(u)), base)
        self.assertIs(u.rjust(len(u)).__class__, str)
        self.assertEqual(u.rjust(len(u)), base)
        self.assertIs(u.lower().__class__, str)
        self.assertEqual(u.lower(), base)
        self.assertIs(u.upper().__class__, str)
        self.assertEqual(u.upper(), base)
        self.assertIs(u.capitalize().__class__, str)
        self.assertEqual(u.capitalize(), base)
        self.assertIs(u.title().__class__, str)
        self.assertEqual(u.title(), base)
        self.assertIs((u + "").__class__, str)
        self.assertEqual(u + "", base)
        self.assertIs(("" + u).__class__, str)
        self.assertEqual("" + u, base)
        self.assertIs((u * 0).__class__, str)
        self.assertEqual(u * 0, "")
        self.assertIs((u * 1).__class__, str)
        self.assertEqual(u * 1, base)
        self.assertIs((u * 2).__class__, str)
        self.assertEqual(u * 2, base + base)
        self.assertIs(u[:].__class__, str)
        self.assertEqual(u[:], base)
        self.assertIs(u[0:0].__class__, str)
        self.assertEqual(u[0:0], "")

        klasa sublist(list):
            dalej
        a = sublist(range(5))
        self.assertEqual(a, list(range(5)))
        a.append("hello")
        self.assertEqual(a, list(range(5)) + ["hello"])
        a[5] = 5
        self.assertEqual(a, list(range(6)))
        a.extend(range(6, 20))
        self.assertEqual(a, list(range(20)))
        a[-5:] = []
        self.assertEqual(a, list(range(15)))
        usuń a[10:15]
        self.assertEqual(len(a), 10)
        self.assertEqual(a, list(range(10)))
        self.assertEqual(list(a), list(range(10)))
        self.assertEqual(a[0], 0)
        self.assertEqual(a[9], 9)
        self.assertEqual(a[-10], 0)
        self.assertEqual(a[-1], 9)
        self.assertEqual(a[:5], list(range(5)))

        ## klasa CountedInput(file):
        ##    """Counts lines read by self.readline().
        ##
        ##     self.lineno jest the 0-based ordinal of the last line read, up to
        ##     a maximum of one greater than the number of lines w the file.
        ##
        ##     self.ateof jest true jeżeli oraz only jeżeli the final "" line has been read,
        ##     at which point self.lineno stops incrementing, oraz further calls
        ##     to readline() continue to zwróć "".
        ##     """
        ##
        ##     lineno = 0
        ##     ateof = 0
        ##     def readline(self):
        ##         jeżeli self.ateof:
        ##             zwróć ""
        ##         s = file.readline(self)
        ##         # Next line works too.
        ##         # s = super(CountedInput, self).readline()
        ##         self.lineno += 1
        ##         jeżeli s == "":
        ##             self.ateof = 1
        ##        zwróć s
        ##
        ## f = file(name=support.TESTFN, mode='w')
        ## lines = ['a\n', 'b\n', 'c\n']
        ## spróbuj:
        ##     f.writelines(lines)
        ##     f.close()
        ##     f = CountedInput(support.TESTFN)
        ##     dla (i, expected) w zip(range(1, 5) + [4], lines + 2 * [""]):
        ##         got = f.readline()
        ##         self.assertEqual(expected, got)
        ##         self.assertEqual(f.lineno, i)
        ##         self.assertEqual(f.ateof, (i > len(lines)))
        ##     f.close()
        ## w_końcu:
        ##     spróbuj:
        ##         f.close()
        ##     wyjąwszy:
        ##         dalej
        ##     support.unlink(support.TESTFN)

    def test_keywords(self):
        # Testing keyword args to basic type constructors ...
        self.assertEqual(int(x=1), 1)
        self.assertEqual(float(x=2), 2.0)
        self.assertEqual(int(x=3), 3)
        self.assertEqual(complex(imag=42, real=666), complex(666, 42))
        self.assertEqual(str(object=500), '500')
        self.assertEqual(str(object=b'abc', errors='strict'), 'abc')
        self.assertEqual(tuple(sequence=range(3)), (0, 1, 2))
        self.assertEqual(list(sequence=(0, 1, 2)), list(range(3)))
        # note: jako of Python 2.3, dict() no longer has an "items" keyword arg

        dla constructor w (int, float, int, complex, str, str,
                            tuple, list):
            spróbuj:
                constructor(bogus_keyword_arg=1)
            wyjąwszy TypeError:
                dalej
            inaczej:
                self.fail("expected TypeError z bogus keyword argument to %r"
                            % constructor)

    def test_str_subclass_as_dict_key(self):
        # Testing a str subclass used jako dict key ..

        klasa cistr(str):
            """Sublcass of str that computes __eq__ case-insensitively.

            Also computes a hash code of the string w canonical form.
            """

            def __init__(self, value):
                self.canonical = value.lower()
                self.hashcode = hash(self.canonical)

            def __eq__(self, other):
                jeżeli nie isinstance(other, cistr):
                    other = cistr(other)
                zwróć self.canonical == other.canonical

            def __hash__(self):
                zwróć self.hashcode

        self.assertEqual(cistr('ABC'), 'abc')
        self.assertEqual('aBc', cistr('ABC'))
        self.assertEqual(str(cistr('ABC')), 'ABC')

        d = {cistr('one'): 1, cistr('two'): 2, cistr('tHree'): 3}
        self.assertEqual(d[cistr('one')], 1)
        self.assertEqual(d[cistr('tWo')], 2)
        self.assertEqual(d[cistr('THrEE')], 3)
        self.assertIn(cistr('ONe'), d)
        self.assertEqual(d.get(cistr('thrEE')), 3)

    def test_classic_comparisons(self):
        # Testing classic comparisons...
        klasa classic:
            dalej

        dla base w (classic, int, object):
            klasa C(base):
                def __init__(self, value):
                    self.value = int(value)
                def __eq__(self, other):
                    jeżeli isinstance(other, C):
                        zwróć self.value == other.value
                    jeżeli isinstance(other, int) albo isinstance(other, int):
                        zwróć self.value == other
                    zwróć NotImplemented
                def __ne__(self, other):
                    jeżeli isinstance(other, C):
                        zwróć self.value != other.value
                    jeżeli isinstance(other, int) albo isinstance(other, int):
                        zwróć self.value != other
                    zwróć NotImplemented
                def __lt__(self, other):
                    jeżeli isinstance(other, C):
                        zwróć self.value < other.value
                    jeżeli isinstance(other, int) albo isinstance(other, int):
                        zwróć self.value < other
                    zwróć NotImplemented
                def __le__(self, other):
                    jeżeli isinstance(other, C):
                        zwróć self.value <= other.value
                    jeżeli isinstance(other, int) albo isinstance(other, int):
                        zwróć self.value <= other
                    zwróć NotImplemented
                def __gt__(self, other):
                    jeżeli isinstance(other, C):
                        zwróć self.value > other.value
                    jeżeli isinstance(other, int) albo isinstance(other, int):
                        zwróć self.value > other
                    zwróć NotImplemented
                def __ge__(self, other):
                    jeżeli isinstance(other, C):
                        zwróć self.value >= other.value
                    jeżeli isinstance(other, int) albo isinstance(other, int):
                        zwróć self.value >= other
                    zwróć NotImplemented

            c1 = C(1)
            c2 = C(2)
            c3 = C(3)
            self.assertEqual(c1, 1)
            c = {1: c1, 2: c2, 3: c3}
            dla x w 1, 2, 3:
                dla y w 1, 2, 3:
                    dla op w "<", "<=", "==", "!=", ">", ">=":
                        self.assertEqual(eval("c[x] %s c[y]" % op),
                                     eval("x %s y" % op),
                                     "x=%d, y=%d" % (x, y))
                        self.assertEqual(eval("c[x] %s y" % op),
                                     eval("x %s y" % op),
                                     "x=%d, y=%d" % (x, y))
                        self.assertEqual(eval("x %s c[y]" % op),
                                     eval("x %s y" % op),
                                     "x=%d, y=%d" % (x, y))

    def test_rich_comparisons(self):
        # Testing rich comparisons...
        klasa Z(complex):
            dalej
        z = Z(1)
        self.assertEqual(z, 1+0j)
        self.assertEqual(1+0j, z)
        klasa ZZ(complex):
            def __eq__(self, other):
                spróbuj:
                    zwróć abs(self - other) <= 1e-6
                wyjąwszy:
                    zwróć NotImplemented
        zz = ZZ(1.0000003)
        self.assertEqual(zz, 1+0j)
        self.assertEqual(1+0j, zz)

        klasa classic:
            dalej
        dla base w (classic, int, object, list):
            klasa C(base):
                def __init__(self, value):
                    self.value = int(value)
                def __cmp__(self_, other):
                    self.fail("shouldn't call __cmp__")
                def __eq__(self, other):
                    jeżeli isinstance(other, C):
                        zwróć self.value == other.value
                    jeżeli isinstance(other, int) albo isinstance(other, int):
                        zwróć self.value == other
                    zwróć NotImplemented
                def __ne__(self, other):
                    jeżeli isinstance(other, C):
                        zwróć self.value != other.value
                    jeżeli isinstance(other, int) albo isinstance(other, int):
                        zwróć self.value != other
                    zwróć NotImplemented
                def __lt__(self, other):
                    jeżeli isinstance(other, C):
                        zwróć self.value < other.value
                    jeżeli isinstance(other, int) albo isinstance(other, int):
                        zwróć self.value < other
                    zwróć NotImplemented
                def __le__(self, other):
                    jeżeli isinstance(other, C):
                        zwróć self.value <= other.value
                    jeżeli isinstance(other, int) albo isinstance(other, int):
                        zwróć self.value <= other
                    zwróć NotImplemented
                def __gt__(self, other):
                    jeżeli isinstance(other, C):
                        zwróć self.value > other.value
                    jeżeli isinstance(other, int) albo isinstance(other, int):
                        zwróć self.value > other
                    zwróć NotImplemented
                def __ge__(self, other):
                    jeżeli isinstance(other, C):
                        zwróć self.value >= other.value
                    jeżeli isinstance(other, int) albo isinstance(other, int):
                        zwróć self.value >= other
                    zwróć NotImplemented
            c1 = C(1)
            c2 = C(2)
            c3 = C(3)
            self.assertEqual(c1, 1)
            c = {1: c1, 2: c2, 3: c3}
            dla x w 1, 2, 3:
                dla y w 1, 2, 3:
                    dla op w "<", "<=", "==", "!=", ">", ">=":
                        self.assertEqual(eval("c[x] %s c[y]" % op),
                                         eval("x %s y" % op),
                                         "x=%d, y=%d" % (x, y))
                        self.assertEqual(eval("c[x] %s y" % op),
                                         eval("x %s y" % op),
                                         "x=%d, y=%d" % (x, y))
                        self.assertEqual(eval("x %s c[y]" % op),
                                         eval("x %s y" % op),
                                         "x=%d, y=%d" % (x, y))

    def test_descrdoc(self):
        # Testing descriptor doc strings...
        z _io zaimportuj FileIO
        def check(descr, what):
            self.assertEqual(descr.__doc__, what)
        check(FileIO.closed, "Prawda jeżeli the file jest closed") # getset descriptor
        check(complex.real, "the real part of a complex number") # member descriptor

    def test_doc_descriptor(self):
        # Testing __doc__ descriptor...
        # SF bug 542984
        klasa DocDescr(object):
            def __get__(self, object, otype):
                jeżeli object:
                    object = object.__class__.__name__ + ' instance'
                jeżeli otype:
                    otype = otype.__name__
                zwróć 'object=%s; type=%s' % (object, otype)
        klasa OldClass:
            __doc__ = DocDescr()
        klasa NewClass(object):
            __doc__ = DocDescr()
        self.assertEqual(OldClass.__doc__, 'object=Nic; type=OldClass')
        self.assertEqual(OldClass().__doc__, 'object=OldClass instance; type=OldClass')
        self.assertEqual(NewClass.__doc__, 'object=Nic; type=NewClass')
        self.assertEqual(NewClass().__doc__, 'object=NewClass instance; type=NewClass')

    def test_set_class(self):
        # Testing __class__ assignment...
        klasa C(object): dalej
        klasa D(object): dalej
        klasa E(object): dalej
        klasa F(D, E): dalej
        dla cls w C, D, E, F:
            dla cls2 w C, D, E, F:
                x = cls()
                x.__class__ = cls2
                self.assertIs(x.__class__, cls2)
                x.__class__ = cls
                self.assertIs(x.__class__, cls)
        def cant(x, C):
            spróbuj:
                x.__class__ = C
            wyjąwszy TypeError:
                dalej
            inaczej:
                self.fail("shouldn't allow %r.__class__ = %r" % (x, C))
            spróbuj:
                delattr(x, "__class__")
            wyjąwszy (TypeError, AttributeError):
                dalej
            inaczej:
                self.fail("shouldn't allow usuń %r.__class__" % x)
        cant(C(), list)
        cant(list(), C)
        cant(C(), 1)
        cant(C(), object)
        cant(object(), list)
        cant(list(), object)
        klasa Int(int): __slots__ = []
        cant(Prawda, int)
        cant(2, bool)
        o = object()
        cant(o, type(1))
        cant(o, type(Nic))
        usuń o
        klasa G(object):
            __slots__ = ["a", "b"]
        klasa H(object):
            __slots__ = ["b", "a"]
        klasa I(object):
            __slots__ = ["a", "b"]
        klasa J(object):
            __slots__ = ["c", "b"]
        klasa K(object):
            __slots__ = ["a", "b", "d"]
        klasa L(H):
            __slots__ = ["e"]
        klasa M(I):
            __slots__ = ["e"]
        klasa N(J):
            __slots__ = ["__weakref__"]
        klasa P(J):
            __slots__ = ["__dict__"]
        klasa Q(J):
            dalej
        klasa R(J):
            __slots__ = ["__dict__", "__weakref__"]

        dla cls, cls2 w ((G, H), (G, I), (I, H), (Q, R), (R, Q)):
            x = cls()
            x.a = 1
            x.__class__ = cls2
            self.assertIs(x.__class__, cls2,
                   "assigning %r jako __class__ dla %r silently failed" % (cls2, x))
            self.assertEqual(x.a, 1)
            x.__class__ = cls
            self.assertIs(x.__class__, cls,
                   "assigning %r jako __class__ dla %r silently failed" % (cls, x))
            self.assertEqual(x.a, 1)
        dla cls w G, J, K, L, M, N, P, R, list, Int:
            dla cls2 w G, J, K, L, M, N, P, R, list, Int:
                jeżeli cls jest cls2:
                    kontynuuj
                cant(cls(), cls2)

        # Issue5283: when __class__ changes w __del__, the wrong
        # type gets DECREF'd.
        klasa O(object):
            dalej
        klasa A(object):
            def __del__(self):
                self.__class__ = O
        l = [A() dla x w range(100)]
        usuń l

    def test_set_dict(self):
        # Testing __dict__ assignment...
        klasa C(object): dalej
        a = C()
        a.__dict__ = {'b': 1}
        self.assertEqual(a.b, 1)
        def cant(x, dict):
            spróbuj:
                x.__dict__ = dict
            wyjąwszy (AttributeError, TypeError):
                dalej
            inaczej:
                self.fail("shouldn't allow %r.__dict__ = %r" % (x, dict))
        cant(a, Nic)
        cant(a, [])
        cant(a, 1)
        usuń a.__dict__ # Deleting __dict__ jest allowed

        klasa Base(object):
            dalej
        def verify_dict_readonly(x):
            """
            x has to be an instance of a klasa inheriting z Base.
            """
            cant(x, {})
            spróbuj:
                usuń x.__dict__
            wyjąwszy (AttributeError, TypeError):
                dalej
            inaczej:
                self.fail("shouldn't allow usuń %r.__dict__" % x)
            dict_descr = Base.__dict__["__dict__"]
            spróbuj:
                dict_descr.__set__(x, {})
            wyjąwszy (AttributeError, TypeError):
                dalej
            inaczej:
                self.fail("dict_descr allowed access to %r's dict" % x)

        # Classes don't allow __dict__ assignment oraz have readonly dicts
        klasa Meta1(type, Base):
            dalej
        klasa Meta2(Base, type):
            dalej
        klasa D(object, metaclass=Meta1):
            dalej
        klasa E(object, metaclass=Meta2):
            dalej
        dla cls w C, D, E:
            verify_dict_readonly(cls)
            class_dict = cls.__dict__
            spróbuj:
                class_dict["spam"] = "eggs"
            wyjąwszy TypeError:
                dalej
            inaczej:
                self.fail("%r's __dict__ can be modified" % cls)

        # Modules also disallow __dict__ assignment
        klasa Module1(types.ModuleType, Base):
            dalej
        klasa Module2(Base, types.ModuleType):
            dalej
        dla ModuleType w Module1, Module2:
            mod = ModuleType("spam")
            verify_dict_readonly(mod)
            mod.__dict__["spam"] = "eggs"

        # Exception's __dict__ can be replaced, but nie deleted
        # (at least nie any more than regular exception's __dict__ can
        # be deleted; on CPython it jest nie the case, whereas on PyPy they
        # can, just like any other new-style instance's __dict__.)
        def can_delete_dict(e):
            spróbuj:
                usuń e.__dict__
            wyjąwszy (TypeError, AttributeError):
                zwróć Nieprawda
            inaczej:
                zwróć Prawda
        klasa Exception1(Exception, Base):
            dalej
        klasa Exception2(Base, Exception):
            dalej
        dla ExceptionType w Exception, Exception1, Exception2:
            e = ExceptionType()
            e.__dict__ = {"a": 1}
            self.assertEqual(e.a, 1)
            self.assertEqual(can_delete_dict(e), can_delete_dict(ValueError()))

    def test_binary_operator_override(self):
        # Testing overrides of binary operations...
        klasa I(int):
            def __repr__(self):
                zwróć "I(%r)" % int(self)
            def __add__(self, other):
                zwróć I(int(self) + int(other))
            __radd__ = __add__
            def __pow__(self, other, mod=Nic):
                jeżeli mod jest Nic:
                    zwróć I(pow(int(self), int(other)))
                inaczej:
                    zwróć I(pow(int(self), int(other), int(mod)))
            def __rpow__(self, other, mod=Nic):
                jeżeli mod jest Nic:
                    zwróć I(pow(int(other), int(self), mod))
                inaczej:
                    zwróć I(pow(int(other), int(self), int(mod)))

        self.assertEqual(repr(I(1) + I(2)), "I(3)")
        self.assertEqual(repr(I(1) + 2), "I(3)")
        self.assertEqual(repr(1 + I(2)), "I(3)")
        self.assertEqual(repr(I(2) ** I(3)), "I(8)")
        self.assertEqual(repr(2 ** I(3)), "I(8)")
        self.assertEqual(repr(I(2) ** 3), "I(8)")
        self.assertEqual(repr(pow(I(2), I(3), I(5))), "I(3)")
        klasa S(str):
            def __eq__(self, other):
                zwróć self.lower() == other.lower()

    def test_subclass_propagation(self):
        # Testing propagation of slot functions to subclasses...
        klasa A(object):
            dalej
        klasa B(A):
            dalej
        klasa C(A):
            dalej
        klasa D(B, C):
            dalej
        d = D()
        orig_hash = hash(d) # related to id(d) w platform-dependent ways
        A.__hash__ = lambda self: 42
        self.assertEqual(hash(d), 42)
        C.__hash__ = lambda self: 314
        self.assertEqual(hash(d), 314)
        B.__hash__ = lambda self: 144
        self.assertEqual(hash(d), 144)
        D.__hash__ = lambda self: 100
        self.assertEqual(hash(d), 100)
        D.__hash__ = Nic
        self.assertRaises(TypeError, hash, d)
        usuń D.__hash__
        self.assertEqual(hash(d), 144)
        B.__hash__ = Nic
        self.assertRaises(TypeError, hash, d)
        usuń B.__hash__
        self.assertEqual(hash(d), 314)
        C.__hash__ = Nic
        self.assertRaises(TypeError, hash, d)
        usuń C.__hash__
        self.assertEqual(hash(d), 42)
        A.__hash__ = Nic
        self.assertRaises(TypeError, hash, d)
        usuń A.__hash__
        self.assertEqual(hash(d), orig_hash)
        d.foo = 42
        d.bar = 42
        self.assertEqual(d.foo, 42)
        self.assertEqual(d.bar, 42)
        def __getattribute__(self, name):
            jeżeli name == "foo":
                zwróć 24
            zwróć object.__getattribute__(self, name)
        A.__getattribute__ = __getattribute__
        self.assertEqual(d.foo, 24)
        self.assertEqual(d.bar, 42)
        def __getattr__(self, name):
            jeżeli name w ("spam", "foo", "bar"):
                zwróć "hello"
            podnieś AttributeError(name)
        B.__getattr__ = __getattr__
        self.assertEqual(d.spam, "hello")
        self.assertEqual(d.foo, 24)
        self.assertEqual(d.bar, 42)
        usuń A.__getattribute__
        self.assertEqual(d.foo, 42)
        usuń d.foo
        self.assertEqual(d.foo, "hello")
        self.assertEqual(d.bar, 42)
        usuń B.__getattr__
        spróbuj:
            d.foo
        wyjąwszy AttributeError:
            dalej
        inaczej:
            self.fail("d.foo should be undefined now")

        # Test a nasty bug w recurse_down_subclasses()
        klasa A(object):
            dalej
        klasa B(A):
            dalej
        usuń B
        support.gc_collect()
        A.__setitem__ = lambda *a: Nic # crash

    def test_buffer_inheritance(self):
        # Testing that buffer interface jest inherited ...

        zaimportuj binascii
        # SF bug [#470040] ParseTuple t# vs subclasses.

        klasa MyBytes(bytes):
            dalej
        base = b'abc'
        m = MyBytes(base)
        # b2a_hex uses the buffer interface to get its argument's value, via
        # PyArg_ParseTuple 't#' code.
        self.assertEqual(binascii.b2a_hex(m), binascii.b2a_hex(base))

        klasa MyInt(int):
            dalej
        m = MyInt(42)
        spróbuj:
            binascii.b2a_hex(m)
            self.fail('subclass of int should nie have a buffer interface')
        wyjąwszy TypeError:
            dalej

    def test_str_of_str_subclass(self):
        # Testing __str__ defined w subclass of str ...
        zaimportuj binascii
        zaimportuj io

        klasa octetstring(str):
            def __str__(self):
                zwróć binascii.b2a_hex(self.encode('ascii')).decode("ascii")
            def __repr__(self):
                zwróć self + " repr"

        o = octetstring('A')
        self.assertEqual(type(o), octetstring)
        self.assertEqual(type(str(o)), str)
        self.assertEqual(type(repr(o)), str)
        self.assertEqual(ord(o), 0x41)
        self.assertEqual(str(o), '41')
        self.assertEqual(repr(o), 'A repr')
        self.assertEqual(o.__str__(), '41')
        self.assertEqual(o.__repr__(), 'A repr')

        capture = io.StringIO()
        # Calling str() albo nie exercises different internal paths.
        print(o, file=capture)
        print(str(o), file=capture)
        self.assertEqual(capture.getvalue(), '41\n41\n')
        capture.close()

    def test_keyword_arguments(self):
        # Testing keyword arguments to __init__, __call__...
        def f(a): zwróć a
        self.assertEqual(f.__call__(a=42), 42)
        a = []
        list.__init__(a, sequence=[0, 1, 2])
        self.assertEqual(a, [0, 1, 2])

    def test_recursive_call(self):
        # Testing recursive __call__() by setting to instance of class...
        klasa A(object):
            dalej

        A.__call__ = A()
        spróbuj:
            A()()
        wyjąwszy RecursionError:
            dalej
        inaczej:
            self.fail("Recursion limit should have been reached dla __call__()")

    def test_delete_hook(self):
        # Testing __del__ hook...
        log = []
        klasa C(object):
            def __del__(self):
                log.append(1)
        c = C()
        self.assertEqual(log, [])
        usuń c
        support.gc_collect()
        self.assertEqual(log, [1])

        klasa D(object): dalej
        d = D()
        spróbuj: usuń d[0]
        wyjąwszy TypeError: dalej
        inaczej: self.fail("invalid del() didn't podnieś TypeError")

    def test_hash_inheritance(self):
        # Testing hash of mutable subclasses...

        klasa mydict(dict):
            dalej
        d = mydict()
        spróbuj:
            hash(d)
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("hash() of dict subclass should fail")

        klasa mylist(list):
            dalej
        d = mylist()
        spróbuj:
            hash(d)
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("hash() of list subclass should fail")

    def test_str_operations(self):
        spróbuj: 'a' + 5
        wyjąwszy TypeError: dalej
        inaczej: self.fail("'' + 5 doesn't podnieś TypeError")

        spróbuj: ''.split('')
        wyjąwszy ValueError: dalej
        inaczej: self.fail("''.split('') doesn't podnieś ValueError")

        spróbuj: ''.join([0])
        wyjąwszy TypeError: dalej
        inaczej: self.fail("''.join([0]) doesn't podnieś TypeError")

        spróbuj: ''.rindex('5')
        wyjąwszy ValueError: dalej
        inaczej: self.fail("''.rindex('5') doesn't podnieś ValueError")

        spróbuj: '%(n)s' % Nic
        wyjąwszy TypeError: dalej
        inaczej: self.fail("'%(n)s' % Nic doesn't podnieś TypeError")

        spróbuj: '%(n' % {}
        wyjąwszy ValueError: dalej
        inaczej: self.fail("'%(n' % {} '' doesn't podnieś ValueError")

        spróbuj: '%*s' % ('abc')
        wyjąwszy TypeError: dalej
        inaczej: self.fail("'%*s' % ('abc') doesn't podnieś TypeError")

        spróbuj: '%*.*s' % ('abc', 5)
        wyjąwszy TypeError: dalej
        inaczej: self.fail("'%*.*s' % ('abc', 5) doesn't podnieś TypeError")

        spróbuj: '%s' % (1, 2)
        wyjąwszy TypeError: dalej
        inaczej: self.fail("'%s' % (1, 2) doesn't podnieś TypeError")

        spróbuj: '%' % Nic
        wyjąwszy ValueError: dalej
        inaczej: self.fail("'%' % Nic doesn't podnieś ValueError")

        self.assertEqual('534253'.isdigit(), 1)
        self.assertEqual('534253x'.isdigit(), 0)
        self.assertEqual('%c' % 5, '\x05')
        self.assertEqual('%c' % '5', '5')

    def test_deepcopy_recursive(self):
        # Testing deepcopy of recursive objects...
        klasa Node:
            dalej
        a = Node()
        b = Node()
        a.b = b
        b.a = a
        z = deepcopy(a) # This blew up before

    def test_unintialized_modules(self):
        # Testing uninitialized module objects...
        z types zaimportuj ModuleType jako M
        m = M.__new__(M)
        str(m)
        self.assertNotHasAttr(m, "__name__")
        self.assertNotHasAttr(m, "__file__")
        self.assertNotHasAttr(m, "foo")
        self.assertNieprawda(m.__dict__)   # Nic albo {} are both reasonable answers
        m.foo = 1
        self.assertEqual(m.__dict__, {"foo": 1})

    def test_funny_new(self):
        # Testing __new__ returning something unexpected...
        klasa C(object):
            def __new__(cls, arg):
                jeżeli isinstance(arg, str): zwróć [1, 2, 3]
                albo_inaczej isinstance(arg, int): zwróć object.__new__(D)
                inaczej: zwróć object.__new__(cls)
        klasa D(C):
            def __init__(self, arg):
                self.foo = arg
        self.assertEqual(C("1"), [1, 2, 3])
        self.assertEqual(D("1"), [1, 2, 3])
        d = D(Nic)
        self.assertEqual(d.foo, Nic)
        d = C(1)
        self.assertIsInstance(d, D)
        self.assertEqual(d.foo, 1)
        d = D(1)
        self.assertIsInstance(d, D)
        self.assertEqual(d.foo, 1)

    def test_imul_bug(self):
        # Testing dla __imul__ problems...
        # SF bug 544647
        klasa C(object):
            def __imul__(self, other):
                zwróć (self, other)
        x = C()
        y = x
        y *= 1.0
        self.assertEqual(y, (x, 1.0))
        y = x
        y *= 2
        self.assertEqual(y, (x, 2))
        y = x
        y *= 3
        self.assertEqual(y, (x, 3))
        y = x
        y *= 1<<100
        self.assertEqual(y, (x, 1<<100))
        y = x
        y *= Nic
        self.assertEqual(y, (x, Nic))
        y = x
        y *= "foo"
        self.assertEqual(y, (x, "foo"))

    def test_copy_setstate(self):
        # Testing that copy.*copy() correctly uses __setstate__...
        zaimportuj copy
        klasa C(object):
            def __init__(self, foo=Nic):
                self.foo = foo
                self.__foo = foo
            def setfoo(self, foo=Nic):
                self.foo = foo
            def getfoo(self):
                zwróć self.__foo
            def __getstate__(self):
                zwróć [self.foo]
            def __setstate__(self_, lst):
                self.assertEqual(len(lst), 1)
                self_.__foo = self_.foo = lst[0]
        a = C(42)
        a.setfoo(24)
        self.assertEqual(a.foo, 24)
        self.assertEqual(a.getfoo(), 42)
        b = copy.copy(a)
        self.assertEqual(b.foo, 24)
        self.assertEqual(b.getfoo(), 24)
        b = copy.deepcopy(a)
        self.assertEqual(b.foo, 24)
        self.assertEqual(b.getfoo(), 24)

    def test_slices(self):
        # Testing cases przy slices oraz overridden __getitem__ ...

        # Strings
        self.assertEqual("hello"[:4], "hell")
        self.assertEqual("hello"[slice(4)], "hell")
        self.assertEqual(str.__getitem__("hello", slice(4)), "hell")
        klasa S(str):
            def __getitem__(self, x):
                zwróć str.__getitem__(self, x)
        self.assertEqual(S("hello")[:4], "hell")
        self.assertEqual(S("hello")[slice(4)], "hell")
        self.assertEqual(S("hello").__getitem__(slice(4)), "hell")
        # Tuples
        self.assertEqual((1,2,3)[:2], (1,2))
        self.assertEqual((1,2,3)[slice(2)], (1,2))
        self.assertEqual(tuple.__getitem__((1,2,3), slice(2)), (1,2))
        klasa T(tuple):
            def __getitem__(self, x):
                zwróć tuple.__getitem__(self, x)
        self.assertEqual(T((1,2,3))[:2], (1,2))
        self.assertEqual(T((1,2,3))[slice(2)], (1,2))
        self.assertEqual(T((1,2,3)).__getitem__(slice(2)), (1,2))
        # Lists
        self.assertEqual([1,2,3][:2], [1,2])
        self.assertEqual([1,2,3][slice(2)], [1,2])
        self.assertEqual(list.__getitem__([1,2,3], slice(2)), [1,2])
        klasa L(list):
            def __getitem__(self, x):
                zwróć list.__getitem__(self, x)
        self.assertEqual(L([1,2,3])[:2], [1,2])
        self.assertEqual(L([1,2,3])[slice(2)], [1,2])
        self.assertEqual(L([1,2,3]).__getitem__(slice(2)), [1,2])
        # Now do lists oraz __setitem__
        a = L([1,2,3])
        a[slice(1, 3)] = [3,2]
        self.assertEqual(a, [1,3,2])
        a[slice(0, 2, 1)] = [3,1]
        self.assertEqual(a, [3,1,2])
        a.__setitem__(slice(1, 3), [2,1])
        self.assertEqual(a, [3,2,1])
        a.__setitem__(slice(0, 2, 1), [2,3])
        self.assertEqual(a, [2,3,1])

    def test_subtype_resurrection(self):
        # Testing resurrection of new-style instance...

        klasa C(object):
            container = []

            def __del__(self):
                # resurrect the instance
                C.container.append(self)

        c = C()
        c.attr = 42

        # The most interesting thing here jest whether this blows up, due to
        # flawed GC tracking logic w typeobject.c's call_finalizer() (a 2.2.1
        # bug).
        usuń c

        support.gc_collect()
        self.assertEqual(len(C.container), 1)

        # Make c mortal again, so that the test framework przy -l doesn't report
        # it jako a leak.
        usuń C.__del__

    def test_slots_trash(self):
        # Testing slot trash...
        # Deallocating deeply nested slotted trash caused stack overflows
        klasa trash(object):
            __slots__ = ['x']
            def __init__(self, x):
                self.x = x
        o = Nic
        dla i w range(50000):
            o = trash(o)
        usuń o

    def test_slots_multiple_inheritance(self):
        # SF bug 575229, multiple inheritance w/ slots dumps core
        klasa A(object):
            __slots__=()
        klasa B(object):
            dalej
        klasa C(A,B) :
            __slots__=()
        jeżeli support.check_impl_detail():
            self.assertEqual(C.__basicsize__, B.__basicsize__)
        self.assertHasAttr(C, '__dict__')
        self.assertHasAttr(C, '__weakref__')
        C().x = 2

    def test_rmul(self):
        # Testing correct invocation of __rmul__...
        # SF patch 592646
        klasa C(object):
            def __mul__(self, other):
                zwróć "mul"
            def __rmul__(self, other):
                zwróć "rmul"
        a = C()
        self.assertEqual(a*2, "mul")
        self.assertEqual(a*2.2, "mul")
        self.assertEqual(2*a, "rmul")
        self.assertEqual(2.2*a, "rmul")

    def test_ipow(self):
        # Testing correct invocation of __ipow__...
        # [SF bug 620179]
        klasa C(object):
            def __ipow__(self, other):
                dalej
        a = C()
        a **= 2

    def test_mutable_bases(self):
        # Testing mutable bases...

        # stuff that should work:
        klasa C(object):
            dalej
        klasa C2(object):
            def __getattribute__(self, attr):
                jeżeli attr == 'a':
                    zwróć 2
                inaczej:
                    zwróć super(C2, self).__getattribute__(attr)
            def meth(self):
                zwróć 1
        klasa D(C):
            dalej
        klasa E(D):
            dalej
        d = D()
        e = E()
        D.__bases__ = (C,)
        D.__bases__ = (C2,)
        self.assertEqual(d.meth(), 1)
        self.assertEqual(e.meth(), 1)
        self.assertEqual(d.a, 2)
        self.assertEqual(e.a, 2)
        self.assertEqual(C2.__subclasses__(), [D])

        spróbuj:
            usuń D.__bases__
        wyjąwszy (TypeError, AttributeError):
            dalej
        inaczej:
            self.fail("shouldn't be able to delete .__bases__")

        spróbuj:
            D.__bases__ = ()
        wyjąwszy TypeError jako msg:
            jeżeli str(msg) == "a new-style klasa can't have only classic bases":
                self.fail("wrong error message dla .__bases__ = ()")
        inaczej:
            self.fail("shouldn't be able to set .__bases__ to ()")

        spróbuj:
            D.__bases__ = (D,)
        wyjąwszy TypeError:
            dalej
        inaczej:
            # actually, we'll have crashed by here...
            self.fail("shouldn't be able to create inheritance cycles")

        spróbuj:
            D.__bases__ = (C, C)
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("didn't detect repeated base classes")

        spróbuj:
            D.__bases__ = (E,)
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("shouldn't be able to create inheritance cycles")

    def test_builtin_bases(self):
        # Make sure all the builtin types can have their base queried without
        # segfaulting. See issue #5787.
        builtin_types = [tp dla tp w builtins.__dict__.values()
                         jeżeli isinstance(tp, type)]
        dla tp w builtin_types:
            object.__getattribute__(tp, "__bases__")
            jeżeli tp jest nie object:
                self.assertEqual(len(tp.__bases__), 1, tp)

        klasa L(list):
            dalej

        klasa C(object):
            dalej

        klasa D(C):
            dalej

        spróbuj:
            L.__bases__ = (dict,)
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("shouldn't turn list subclass into dict subclass")

        spróbuj:
            list.__bases__ = (dict,)
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("shouldn't be able to assign to list.__bases__")

        spróbuj:
            D.__bases__ = (C, list)
        wyjąwszy TypeError:
            dalej
        inaczej:
            assert 0, "best_base calculation found wanting"


    def test_mutable_bases_with_failing_mro(self):
        # Testing mutable bases przy failing mro...
        klasa WorkOnce(type):
            def __new__(self, name, bases, ns):
                self.flag = 0
                zwróć super(WorkOnce, self).__new__(WorkOnce, name, bases, ns)
            def mro(self):
                jeżeli self.flag > 0:
                    podnieś RuntimeError("bozo")
                inaczej:
                    self.flag += 1
                    zwróć type.mro(self)

        klasa WorkAlways(type):
            def mro(self):
                # this jest here to make sure that .mro()s aren't called
                # przy an exception set (which was possible at one point).
                # An error message will be printed w a debug build.
                # What's a good way to test dla this?
                zwróć type.mro(self)

        klasa C(object):
            dalej

        klasa C2(object):
            dalej

        klasa D(C):
            dalej

        klasa E(D):
            dalej

        klasa F(D, metaclass=WorkOnce):
            dalej

        klasa G(D, metaclass=WorkAlways):
            dalej

        # Immediate subclasses have their mro's adjusted w alphabetical
        # order, so E's will get adjusted before adjusting F's fails.  We
        # check here that E's gets restored.

        E_mro_before = E.__mro__
        D_mro_before = D.__mro__

        spróbuj:
            D.__bases__ = (C2,)
        wyjąwszy RuntimeError:
            self.assertEqual(E.__mro__, E_mro_before)
            self.assertEqual(D.__mro__, D_mro_before)
        inaczej:
            self.fail("exception nie propagated")

    def test_mutable_bases_catch_mro_conflict(self):
        # Testing mutable bases catch mro conflict...
        klasa A(object):
            dalej

        klasa B(object):
            dalej

        klasa C(A, B):
            dalej

        klasa D(A, B):
            dalej

        klasa E(C, D):
            dalej

        spróbuj:
            C.__bases__ = (B, A)
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("didn't catch MRO conflict")

    def test_mutable_names(self):
        # Testing mutable names...
        klasa C(object):
            dalej

        # C.__module__ could be 'test_descr' albo '__main__'
        mod = C.__module__

        C.__name__ = 'D'
        self.assertEqual((C.__module__, C.__name__), (mod, 'D'))

        C.__name__ = 'D.E'
        self.assertEqual((C.__module__, C.__name__), (mod, 'D.E'))

    def test_evil_type_name(self):
        # A badly placed Py_DECREF w type_set_name led to arbitrary code
        # execution dopóki the type structure was nie w a sane state, oraz a
        # possible segmentation fault jako a result.  See bug #16447.
        klasa Nasty(str):
            def __del__(self):
                C.__name__ = "other"

        klasa C:
            dalej

        C.__name__ = Nasty("abc")
        C.__name__ = "normal"

    def test_subclass_right_op(self):
        # Testing correct dispatch of subclass overloading __r<op>__...

        # This code tests various cases where right-dispatch of a subclass
        # should be preferred over left-dispatch of a base class.

        # Case 1: subclass of int; this tests code w abstract.c::binary_op1()

        klasa B(int):
            def __floordiv__(self, other):
                zwróć "B.__floordiv__"
            def __rfloordiv__(self, other):
                zwróć "B.__rfloordiv__"

        self.assertEqual(B(1) // 1, "B.__floordiv__")
        self.assertEqual(1 // B(1), "B.__rfloordiv__")

        # Case 2: subclass of object; this jest just the baseline dla case 3

        klasa C(object):
            def __floordiv__(self, other):
                zwróć "C.__floordiv__"
            def __rfloordiv__(self, other):
                zwróć "C.__rfloordiv__"

        self.assertEqual(C() // 1, "C.__floordiv__")
        self.assertEqual(1 // C(), "C.__rfloordiv__")

        # Case 3: subclass of new-style class; here it gets interesting

        klasa D(C):
            def __floordiv__(self, other):
                zwróć "D.__floordiv__"
            def __rfloordiv__(self, other):
                zwróć "D.__rfloordiv__"

        self.assertEqual(D() // C(), "D.__floordiv__")
        self.assertEqual(C() // D(), "D.__rfloordiv__")

        # Case 4: this didn't work right w 2.2.2 oraz 2.3a1

        klasa E(C):
            dalej

        self.assertEqual(E.__rfloordiv__, C.__rfloordiv__)

        self.assertEqual(E() // 1, "C.__floordiv__")
        self.assertEqual(1 // E(), "C.__rfloordiv__")
        self.assertEqual(E() // C(), "C.__floordiv__")
        self.assertEqual(C() // E(), "C.__floordiv__") # This one would fail

    @support.impl_detail("testing an internal kind of method object")
    def test_meth_class_get(self):
        # Testing __get__ method of METH_CLASS C methods...
        # Full coverage of descrobject.c::classmethod_get()

        # Baseline
        arg = [1, 2, 3]
        res = {1: Nic, 2: Nic, 3: Nic}
        self.assertEqual(dict.fromkeys(arg), res)
        self.assertEqual({}.fromkeys(arg), res)

        # Now get the descriptor
        descr = dict.__dict__["fromkeys"]

        # More baseline using the descriptor directly
        self.assertEqual(descr.__get__(Nic, dict)(arg), res)
        self.assertEqual(descr.__get__({})(arg), res)

        # Now check various error cases
        spróbuj:
            descr.__get__(Nic, Nic)
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("shouldn't have allowed descr.__get__(Nic, Nic)")
        spróbuj:
            descr.__get__(42)
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("shouldn't have allowed descr.__get__(42)")
        spróbuj:
            descr.__get__(Nic, 42)
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("shouldn't have allowed descr.__get__(Nic, 42)")
        spróbuj:
            descr.__get__(Nic, int)
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("shouldn't have allowed descr.__get__(Nic, int)")

    def test_isinst_isclass(self):
        # Testing proxy isinstance() oraz isclass()...
        klasa Proxy(object):
            def __init__(self, obj):
                self.__obj = obj
            def __getattribute__(self, name):
                jeżeli name.startswith("_Proxy__"):
                    zwróć object.__getattribute__(self, name)
                inaczej:
                    zwróć getattr(self.__obj, name)
        # Test przy a classic class
        klasa C:
            dalej
        a = C()
        pa = Proxy(a)
        self.assertIsInstance(a, C)  # Baseline
        self.assertIsInstance(pa, C) # Test
        # Test przy a classic subclass
        klasa D(C):
            dalej
        a = D()
        pa = Proxy(a)
        self.assertIsInstance(a, C)  # Baseline
        self.assertIsInstance(pa, C) # Test
        # Test przy a new-style class
        klasa C(object):
            dalej
        a = C()
        pa = Proxy(a)
        self.assertIsInstance(a, C)  # Baseline
        self.assertIsInstance(pa, C) # Test
        # Test przy a new-style subclass
        klasa D(C):
            dalej
        a = D()
        pa = Proxy(a)
        self.assertIsInstance(a, C)  # Baseline
        self.assertIsInstance(pa, C) # Test

    def test_proxy_super(self):
        # Testing super() dla a proxy object...
        klasa Proxy(object):
            def __init__(self, obj):
                self.__obj = obj
            def __getattribute__(self, name):
                jeżeli name.startswith("_Proxy__"):
                    zwróć object.__getattribute__(self, name)
                inaczej:
                    zwróć getattr(self.__obj, name)

        klasa B(object):
            def f(self):
                zwróć "B.f"

        klasa C(B):
            def f(self):
                zwróć super(C, self).f() + "->C.f"

        obj = C()
        p = Proxy(obj)
        self.assertEqual(C.__dict__["f"](p), "B.f->C.f")

    def test_carloverre(self):
        # Testing prohibition of Carlo Verre's hack...
        spróbuj:
            object.__setattr__(str, "foo", 42)
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("Carlo Verre __setattr__ succeeded!")
        spróbuj:
            object.__delattr__(str, "lower")
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("Carlo Verre __delattr__ succeeded!")

    def test_weakref_segfault(self):
        # Testing weakref segfault...
        # SF 742911
        zaimportuj weakref

        klasa Provoker:
            def __init__(self, referrent):
                self.ref = weakref.ref(referrent)

            def __del__(self):
                x = self.ref()

        klasa Oops(object):
            dalej

        o = Oops()
        o.whatever = Provoker(o)
        usuń o

    def test_wrapper_segfault(self):
        # SF 927248: deeply nested wrappers could cause stack overflow
        f = lambda:Nic
        dla i w range(1000000):
            f = f.__call__
        f = Nic

    def test_file_fault(self):
        # Testing sys.stdout jest changed w getattr...
        test_stdout = sys.stdout
        klasa StdoutGuard:
            def __getattr__(self, attr):
                sys.stdout = sys.__stdout__
                podnieś RuntimeError("Premature access to sys.stdout.%s" % attr)
        sys.stdout = StdoutGuard()
        spróbuj:
            print("Oops!")
        wyjąwszy RuntimeError:
            dalej
        w_końcu:
            sys.stdout = test_stdout

    def test_vicious_descriptor_nonsense(self):
        # Testing vicious_descriptor_nonsense...

        # A potential segfault spotted by Thomas Wouters w mail to
        # python-dev 2003-04-17, turned into an example & fixed by Michael
        # Hudson just less than four months later...

        klasa Evil(object):
            def __hash__(self):
                zwróć hash('attr')
            def __eq__(self, other):
                usuń C.attr
                zwróć 0

        klasa Descr(object):
            def __get__(self, ob, type=Nic):
                zwróć 1

        klasa C(object):
            attr = Descr()

        c = C()
        c.__dict__[Evil()] = 0

        self.assertEqual(c.attr, 1)
        # this makes a crash more likely:
        support.gc_collect()
        self.assertNotHasAttr(c, 'attr')

    def test_init(self):
        # SF 1155938
        klasa Foo(object):
            def __init__(self):
                zwróć 10
        spróbuj:
            Foo()
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("did nie test __init__() dla Nic return")

    def test_method_wrapper(self):
        # Testing method-wrapper objects...
        # <type 'method-wrapper'> did nie support any reflection before 2.5

        # XXX should methods really support __eq__?

        l = []
        self.assertEqual(l.__add__, l.__add__)
        self.assertEqual(l.__add__, [].__add__)
        self.assertNotEqual(l.__add__, [5].__add__)
        self.assertNotEqual(l.__add__, l.__mul__)
        self.assertEqual(l.__add__.__name__, '__add__')
        jeżeli hasattr(l.__add__, '__self__'):
            # CPython
            self.assertIs(l.__add__.__self__, l)
            self.assertIs(l.__add__.__objclass__, list)
        inaczej:
            # Python implementations where [].__add__ jest a normal bound method
            self.assertIs(l.__add__.im_self, l)
            self.assertIs(l.__add__.im_class, list)
        self.assertEqual(l.__add__.__doc__, list.__add__.__doc__)
        spróbuj:
            hash(l.__add__)
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("no TypeError z hash([].__add__)")

        t = ()
        t += (7,)
        self.assertEqual(t.__add__, (7,).__add__)
        self.assertEqual(hash(t.__add__), hash((7,).__add__))

    def test_not_implemented(self):
        # Testing NotImplemented...
        # all binary methods should be able to zwróć a NotImplemented
        zaimportuj operator

        def specialmethod(self, other):
            zwróć NotImplemented

        def check(expr, x, y):
            spróbuj:
                exec(expr, {'x': x, 'y': y, 'operator': operator})
            wyjąwszy TypeError:
                dalej
            inaczej:
                self.fail("no TypeError z %r" % (expr,))

        N1 = sys.maxsize + 1    # might trigger OverflowErrors instead of
                                # TypeErrors
        N2 = sys.maxsize         # jeżeli sizeof(int) < sizeof(long), might trigger
                                #   ValueErrors instead of TypeErrors
        dla name, expr, iexpr w [
                ('__add__',      'x + y',                   'x += y'),
                ('__sub__',      'x - y',                   'x -= y'),
                ('__mul__',      'x * y',                   'x *= y'),
                ('__matmul__',   'x @ y',                   'x @= y'),
                ('__truediv__',  'x / y',                   'x /= y'),
                ('__floordiv__', 'x // y',                  'x //= y'),
                ('__mod__',      'x % y',                   'x %= y'),
                ('__divmod__',   'divmod(x, y)',            Nic),
                ('__pow__',      'x ** y',                  'x **= y'),
                ('__lshift__',   'x << y',                  'x <<= y'),
                ('__rshift__',   'x >> y',                  'x >>= y'),
                ('__and__',      'x & y',                   'x &= y'),
                ('__or__',       'x | y',                   'x |= y'),
                ('__xor__',      'x ^ y',                   'x ^= y')]:
            rname = '__r' + name[2:]
            A = type('A', (), {name: specialmethod})
            a = A()
            check(expr, a, a)
            check(expr, a, N1)
            check(expr, a, N2)
            jeżeli iexpr:
                check(iexpr, a, a)
                check(iexpr, a, N1)
                check(iexpr, a, N2)
                iname = '__i' + name[2:]
                C = type('C', (), {iname: specialmethod})
                c = C()
                check(iexpr, c, a)
                check(iexpr, c, N1)
                check(iexpr, c, N2)

    def test_assign_slice(self):
        # ceval.c's assign_slice used to check for
        # tp->tp_as_sequence->sq_slice instead of
        # tp->tp_as_sequence->sq_ass_slice

        klasa C(object):
            def __setitem__(self, idx, value):
                self.value = value

        c = C()
        c[1:2] = 3
        self.assertEqual(c.value, 3)

    def test_set_and_no_get(self):
        # See
        # http://mail.python.org/pipermail/python-dev/2010-January/095637.html
        klasa Descr(object):

            def __init__(self, name):
                self.name = name

            def __set__(self, obj, value):
                obj.__dict__[self.name] = value
        descr = Descr("a")

        klasa X(object):
            a = descr

        x = X()
        self.assertIs(x.a, descr)
        x.a = 42
        self.assertEqual(x.a, 42)

        # Also check type_getattro dla correctness.
        klasa Meta(type):
            dalej
        klasa X(metaclass=Meta):
            dalej
        X.a = 42
        Meta.a = Descr("a")
        self.assertEqual(X.a, 42)

    def test_getattr_hooks(self):
        # issue 4230

        klasa Descriptor(object):
            counter = 0
            def __get__(self, obj, objtype=Nic):
                def getter(name):
                    self.counter += 1
                    podnieś AttributeError(name)
                zwróć getter

        descr = Descriptor()
        klasa A(object):
            __getattribute__ = descr
        klasa B(object):
            __getattr__ = descr
        klasa C(object):
            __getattribute__ = descr
            __getattr__ = descr

        self.assertRaises(AttributeError, getattr, A(), "attr")
        self.assertEqual(descr.counter, 1)
        self.assertRaises(AttributeError, getattr, B(), "attr")
        self.assertEqual(descr.counter, 2)
        self.assertRaises(AttributeError, getattr, C(), "attr")
        self.assertEqual(descr.counter, 4)

        klasa EvilGetattribute(object):
            # This used to segfault
            def __getattr__(self, name):
                podnieś AttributeError(name)
            def __getattribute__(self, name):
                usuń EvilGetattribute.__getattr__
                dla i w range(5):
                    gc.collect()
                podnieś AttributeError(name)

        self.assertRaises(AttributeError, getattr, EvilGetattribute(), "attr")

    def test_type___getattribute__(self):
        self.assertRaises(TypeError, type.__getattribute__, list, type)

    def test_abstractmethods(self):
        # type pretends nie to have __abstractmethods__.
        self.assertRaises(AttributeError, getattr, type, "__abstractmethods__")
        klasa meta(type):
            dalej
        self.assertRaises(AttributeError, getattr, meta, "__abstractmethods__")
        klasa X(object):
            dalej
        przy self.assertRaises(AttributeError):
            usuń X.__abstractmethods__

    def test_proxy_call(self):
        klasa FakeStr:
            __class__ = str

        fake_str = FakeStr()
        # isinstance() reads __class__
        self.assertIsInstance(fake_str, str)

        # call a method descriptor
        przy self.assertRaises(TypeError):
            str.split(fake_str)

        # call a slot wrapper descriptor
        przy self.assertRaises(TypeError):
            str.__add__(fake_str, "abc")

    def test_repr_as_str(self):
        # Issue #11603: crash albo infinite loop when rebinding __str__ as
        # __repr__.
        klasa Foo:
            dalej
        Foo.__repr__ = Foo.__str__
        foo = Foo()
        self.assertRaises(RecursionError, str, foo)
        self.assertRaises(RecursionError, repr, foo)

    def test_mixing_slot_wrappers(self):
        klasa X(dict):
            __setattr__ = dict.__setitem__
        x = X()
        x.y = 42
        self.assertEqual(x["y"], 42)

    def test_slot_shadows_class_variable(self):
        przy self.assertRaises(ValueError) jako cm:
            klasa X:
                __slots__ = ["foo"]
                foo = Nic
        m = str(cm.exception)
        self.assertEqual("'foo' w __slots__ conflicts przy klasa variable", m)

    def test_set_doc(self):
        klasa X:
            "elephant"
        X.__doc__ = "banana"
        self.assertEqual(X.__doc__, "banana")
        przy self.assertRaises(TypeError) jako cm:
            type(list).__dict__["__doc__"].__set__(list, "blah")
        self.assertIn("can't set list.__doc__", str(cm.exception))
        przy self.assertRaises(TypeError) jako cm:
            type(X).__dict__["__doc__"].__delete__(X)
        self.assertIn("can't delete X.__doc__", str(cm.exception))
        self.assertEqual(X.__doc__, "banana")

    def test_qualname(self):
        descriptors = [str.lower, complex.real, float.real, int.__add__]
        types = ['method', 'member', 'getset', 'wrapper']

        # make sure we have an example of each type of descriptor
        dla d, n w zip(descriptors, types):
            self.assertEqual(type(d).__name__, n + '_descriptor')

        dla d w descriptors:
            qualname = d.__objclass__.__qualname__ + '.' + d.__name__
            self.assertEqual(d.__qualname__, qualname)

        self.assertEqual(str.lower.__qualname__, 'str.lower')
        self.assertEqual(complex.real.__qualname__, 'complex.real')
        self.assertEqual(float.real.__qualname__, 'float.real')
        self.assertEqual(int.__add__.__qualname__, 'int.__add__')

        klasa X:
            dalej
        przy self.assertRaises(TypeError):
            usuń X.__qualname__

        self.assertRaises(TypeError, type.__dict__['__qualname__'].__set__,
                          str, 'Oink')

        global Y
        klasa Y:
            klasa Inside:
                dalej
        self.assertEqual(Y.__qualname__, 'Y')
        self.assertEqual(Y.Inside.__qualname__, 'Y.Inside')

    def test_qualname_dict(self):
        ns = {'__qualname__': 'some.name'}
        tp = type('Foo', (), ns)
        self.assertEqual(tp.__qualname__, 'some.name')
        self.assertNotIn('__qualname__', tp.__dict__)
        self.assertEqual(ns, {'__qualname__': 'some.name'})

        ns = {'__qualname__': 1}
        self.assertRaises(TypeError, type, 'Foo', (), ns)

    def test_cycle_through_dict(self):
        # See bug #1469629
        klasa X(dict):
            def __init__(self):
                dict.__init__(self)
                self.__dict__ = self
        x = X()
        x.attr = 42
        wr = weakref.ref(x)
        usuń x
        support.gc_collect()
        self.assertIsNic(wr())
        dla o w gc.get_objects():
            self.assertIsNot(type(o), X)

    def test_object_new_and_init_with_parameters(self):
        # See issue #1683368
        klasa OverrideNeither:
            dalej
        self.assertRaises(TypeError, OverrideNeither, 1)
        self.assertRaises(TypeError, OverrideNeither, kw=1)
        klasa OverrideNew:
            def __new__(cls, foo, kw=0, *args, **kwds):
                zwróć object.__new__(cls, *args, **kwds)
        klasa OverrideInit:
            def __init__(self, foo, kw=0, *args, **kwargs):
                zwróć object.__init__(self, *args, **kwargs)
        klasa OverrideBoth(OverrideNew, OverrideInit):
            dalej
        dla case w OverrideNew, OverrideInit, OverrideBoth:
            case(1)
            case(1, kw=2)
            self.assertRaises(TypeError, case, 1, 2, 3)
            self.assertRaises(TypeError, case, 1, 2, foo=3)

    def test_subclassing_does_not_duplicate_dict_descriptors(self):
        klasa Base:
            dalej
        klasa Sub(Base):
            dalej
        self.assertIn("__dict__", Base.__dict__)
        self.assertNotIn("__dict__", Sub.__dict__)

    def test_bound_method_repr(self):
        klasa Foo:
            def method(self):
                dalej
        self.assertRegex(repr(Foo().method),
            r"<bound method .*Foo\.method of <.*Foo object at .*>>")


        klasa Base:
            def method(self):
                dalej
        klasa Derived1(Base):
            dalej
        klasa Derived2(Base):
            def method(self):
                dalej
        base = Base()
        derived1 = Derived1()
        derived2 = Derived2()
        super_d2 = super(Derived2, derived2)
        self.assertRegex(repr(base.method),
            r"<bound method .*Base\.method of <.*Base object at .*>>")
        self.assertRegex(repr(derived1.method),
            r"<bound method .*Base\.method of <.*Derived1 object at .*>>")
        self.assertRegex(repr(derived2.method),
            r"<bound method .*Derived2\.method of <.*Derived2 object at .*>>")
        self.assertRegex(repr(super_d2.method),
            r"<bound method .*Base\.method of <.*Derived2 object at .*>>")

        klasa Foo:
            @classmethod
            def method(cls):
                dalej
        foo = Foo()
        self.assertRegex(repr(foo.method), # access via instance
            r"<bound method .*Foo\.method of <class '.*Foo'>>")
        self.assertRegex(repr(Foo.method), # access via the class
            r"<bound method .*Foo\.method of <class '.*Foo'>>")


        klasa MyCallable:
            def __call__(self, arg):
                dalej
        func = MyCallable() # func has no __name__ albo __qualname__ attributes
        instance = object()
        method = types.MethodType(func, instance)
        self.assertRegex(repr(method),
            r"<bound method \? of <object object at .*>>")
        func.__name__ = "name"
        self.assertRegex(repr(method),
            r"<bound method name of <object object at .*>>")
        func.__qualname__ = "qualname"
        self.assertRegex(repr(method),
            r"<bound method qualname of <object object at .*>>")


klasa DictProxyTests(unittest.TestCase):
    def setUp(self):
        klasa C(object):
            def meth(self):
                dalej
        self.C = C

    @unittest.skipIf(hasattr(sys, 'gettrace') oraz sys.gettrace(),
                        'trace function introduces __local__')
    def test_iter_keys(self):
        # Testing dict-proxy keys...
        it = self.C.__dict__.keys()
        self.assertNotIsInstance(it, list)
        keys = list(it)
        keys.sort()
        self.assertEqual(keys, ['__dict__', '__doc__', '__module__',
                                '__weakref__', 'meth'])

    @unittest.skipIf(hasattr(sys, 'gettrace') oraz sys.gettrace(),
                        'trace function introduces __local__')
    def test_iter_values(self):
        # Testing dict-proxy values...
        it = self.C.__dict__.values()
        self.assertNotIsInstance(it, list)
        values = list(it)
        self.assertEqual(len(values), 5)

    @unittest.skipIf(hasattr(sys, 'gettrace') oraz sys.gettrace(),
                        'trace function introduces __local__')
    def test_iter_items(self):
        # Testing dict-proxy iteritems...
        it = self.C.__dict__.items()
        self.assertNotIsInstance(it, list)
        keys = [item[0] dla item w it]
        keys.sort()
        self.assertEqual(keys, ['__dict__', '__doc__', '__module__',
                                '__weakref__', 'meth'])

    def test_dict_type_with_metaclass(self):
        # Testing type of __dict__ when metaclass set...
        klasa B(object):
            dalej
        klasa M(type):
            dalej
        klasa C(metaclass=M):
            # In 2.3a1, C.__dict__ was a real dict rather than a dict proxy
            dalej
        self.assertEqual(type(C.__dict__), type(B.__dict__))

    def test_repr(self):
        # Testing mappingproxy.__repr__.
        # We can't blindly compare przy the repr of another dict jako ordering
        # of keys oraz values jest arbitrary oraz may differ.
        r = repr(self.C.__dict__)
        self.assertPrawda(r.startswith('mappingproxy('), r)
        self.assertPrawda(r.endswith(')'), r)
        dla k, v w self.C.__dict__.items():
            self.assertIn('{!r}: {!r}'.format(k, v), r)


klasa PTypesLongInitTest(unittest.TestCase):
    # This jest w its own TestCase so that it can be run before any other tests.
    def test_pytype_long_ready(self):
        # Testing SF bug 551412 ...

        # This dumps core when SF bug 551412 isn't fixed --
        # but only when test_descr.py jest run separately.
        # (That can't be helped -- jako soon jako PyType_Ready()
        # jest called dla PyLong_Type, the bug jest gone.)
        klasa UserLong(object):
            def __pow__(self, *args):
                dalej
        spróbuj:
            pow(0, UserLong(), 0)
        wyjąwszy:
            dalej

        # Another segfault only when run early
        # (before PyType_Ready(tuple) jest called)
        type.mro(tuple)


klasa MiscTests(unittest.TestCase):
    def test_type_lookup_mro_reference(self):
        # Issue #14199: _PyType_Lookup() has to keep a strong reference to
        # the type MRO because it may be modified during the lookup, if
        # __bases__ jest set during the lookup dla example.
        klasa MyKey(object):
            def __hash__(self):
                zwróć hash('mykey')

            def __eq__(self, other):
                X.__bases__ = (Base2,)

        klasa Base(object):
            mykey = 'z Base'
            mykey2 = 'z Base'

        klasa Base2(object):
            mykey = 'z Base2'
            mykey2 = 'z Base2'

        X = type('X', (Base,), {MyKey(): 5})
        # mykey jest read z Base
        self.assertEqual(X.mykey, 'z Base')
        # mykey2 jest read z Base2 because MyKey.__eq__ has set __bases__
        self.assertEqual(X.mykey2, 'z Base2')


klasa PicklingTests(unittest.TestCase):

    def _check_reduce(self, proto, obj, args=(), kwargs={}, state=Nic,
                      listitems=Nic, dictitems=Nic):
        jeżeli proto >= 2:
            reduce_value = obj.__reduce_ex__(proto)
            jeżeli kwargs:
                self.assertEqual(reduce_value[0], copyreg.__newobj_ex__)
                self.assertEqual(reduce_value[1], (type(obj), args, kwargs))
            inaczej:
                self.assertEqual(reduce_value[0], copyreg.__newobj__)
                self.assertEqual(reduce_value[1], (type(obj),) + args)
            self.assertEqual(reduce_value[2], state)
            jeżeli listitems jest nie Nic:
                self.assertListEqual(list(reduce_value[3]), listitems)
            inaczej:
                self.assertIsNic(reduce_value[3])
            jeżeli dictitems jest nie Nic:
                self.assertDictEqual(dict(reduce_value[4]), dictitems)
            inaczej:
                self.assertIsNic(reduce_value[4])
        inaczej:
            base_type = type(obj).__base__
            reduce_value = (copyreg._reconstructor,
                            (type(obj),
                             base_type,
                             Nic jeżeli base_type jest object inaczej base_type(obj)))
            jeżeli state jest nie Nic:
                reduce_value += (state,)
            self.assertEqual(obj.__reduce_ex__(proto), reduce_value)
            self.assertEqual(obj.__reduce__(), reduce_value)

    def test_reduce(self):
        protocols = range(pickle.HIGHEST_PROTOCOL + 1)
        args = (-101, "spam")
        kwargs = {'bacon': -201, 'fish': -301}
        state = {'cheese': -401}

        klasa C1:
            def __getnewargs__(self):
                zwróć args
        obj = C1()
        dla proto w protocols:
            self._check_reduce(proto, obj, args)

        dla name, value w state.items():
            setattr(obj, name, value)
        dla proto w protocols:
            self._check_reduce(proto, obj, args, state=state)

        klasa C2:
            def __getnewargs__(self):
                zwróć "bad args"
        obj = C2()
        dla proto w protocols:
            jeżeli proto >= 2:
                przy self.assertRaises(TypeError):
                    obj.__reduce_ex__(proto)

        klasa C3:
            def __getnewargs_ex__(self):
                zwróć (args, kwargs)
        obj = C3()
        dla proto w protocols:
            jeżeli proto >= 4:
                self._check_reduce(proto, obj, args, kwargs)
            albo_inaczej proto >= 2:
                przy self.assertRaises(ValueError):
                    obj.__reduce_ex__(proto)

        klasa C4:
            def __getnewargs_ex__(self):
                zwróć (args, "bad dict")
        klasa C5:
            def __getnewargs_ex__(self):
                zwróć ("bad tuple", kwargs)
        klasa C6:
            def __getnewargs_ex__(self):
                zwróć ()
        klasa C7:
            def __getnewargs_ex__(self):
                zwróć "bad args"
        dla proto w protocols:
            dla cls w C4, C5, C6, C7:
                obj = cls()
                jeżeli proto >= 2:
                    przy self.assertRaises((TypeError, ValueError)):
                        obj.__reduce_ex__(proto)

        klasa C8:
            def __getnewargs_ex__(self):
                zwróć (args, kwargs)
        obj = C8()
        dla proto w protocols:
            jeżeli 2 <= proto < 4:
                przy self.assertRaises(ValueError):
                    obj.__reduce_ex__(proto)
        klasa C9:
            def __getnewargs_ex__(self):
                zwróć (args, {})
        obj = C9()
        dla proto w protocols:
            self._check_reduce(proto, obj, args)

        klasa C10:
            def __getnewargs_ex__(self):
                podnieś IndexError
        obj = C10()
        dla proto w protocols:
            jeżeli proto >= 2:
                przy self.assertRaises(IndexError):
                    obj.__reduce_ex__(proto)

        klasa C11:
            def __getstate__(self):
                zwróć state
        obj = C11()
        dla proto w protocols:
            self._check_reduce(proto, obj, state=state)

        klasa C12:
            def __getstate__(self):
                zwróć "not dict"
        obj = C12()
        dla proto w protocols:
            self._check_reduce(proto, obj, state="not dict")

        klasa C13:
            def __getstate__(self):
                podnieś IndexError
        obj = C13()
        dla proto w protocols:
            przy self.assertRaises(IndexError):
                obj.__reduce_ex__(proto)
            jeżeli proto < 2:
                przy self.assertRaises(IndexError):
                    obj.__reduce__()

        klasa C14:
            __slots__ = tuple(state)
            def __init__(self):
                dla name, value w state.items():
                    setattr(self, name, value)

        obj = C14()
        dla proto w protocols:
            jeżeli proto >= 2:
                self._check_reduce(proto, obj, state=(Nic, state))
            inaczej:
                przy self.assertRaises(TypeError):
                    obj.__reduce_ex__(proto)
                przy self.assertRaises(TypeError):
                    obj.__reduce__()

        klasa C15(dict):
            dalej
        obj = C15({"quebec": -601})
        dla proto w protocols:
            self._check_reduce(proto, obj, dictitems=dict(obj))

        klasa C16(list):
            dalej
        obj = C16(["yukon"])
        dla proto w protocols:
            self._check_reduce(proto, obj, listitems=list(obj))

    def test_special_method_lookup(self):
        protocols = range(pickle.HIGHEST_PROTOCOL + 1)
        klasa Picky:
            def __getstate__(self):
                zwróć {}

            def __getattr__(self, attr):
                jeżeli attr w ("__getnewargs__", "__getnewargs_ex__"):
                    podnieś AssertionError(attr)
                zwróć Nic
        dla protocol w protocols:
            state = {} jeżeli protocol >= 2 inaczej Nic
            self._check_reduce(protocol, Picky(), state=state)

    def _assert_is_copy(self, obj, objcopy, msg=Nic):
        """Utility method to verify jeżeli two objects are copies of each others.
        """
        jeżeli msg jest Nic:
            msg = "{!r} jest nie a copy of {!r}".format(obj, objcopy)
        jeżeli type(obj).__repr__ jest object.__repr__:
            # We have this limitation dla now because we use the object's repr
            # to help us verify that the two objects are copies. This allows
            # us to delegate the non-generic verification logic to the objects
            # themselves.
            podnieś ValueError("object dalejed to _assert_is_copy must " +
                             "override the __repr__ method.")
        self.assertIsNot(obj, objcopy, msg=msg)
        self.assertIs(type(obj), type(objcopy), msg=msg)
        jeżeli hasattr(obj, '__dict__'):
            self.assertDictEqual(obj.__dict__, objcopy.__dict__, msg=msg)
            self.assertIsNot(obj.__dict__, objcopy.__dict__, msg=msg)
        jeżeli hasattr(obj, '__slots__'):
            self.assertListEqual(obj.__slots__, objcopy.__slots__, msg=msg)
            dla slot w obj.__slots__:
                self.assertEqual(
                    hasattr(obj, slot), hasattr(objcopy, slot), msg=msg)
                self.assertEqual(getattr(obj, slot, Nic),
                                 getattr(objcopy, slot, Nic), msg=msg)
        self.assertEqual(repr(obj), repr(objcopy), msg=msg)

    @staticmethod
    def _generate_pickle_copiers():
        """Utility method to generate the many possible pickle configurations.
        """
        klasa PickleCopier:
            "This klasa copies object using pickle."
            def __init__(self, proto, dumps, loads):
                self.proto = proto
                self.dumps = dumps
                self.loads = loads
            def copy(self, obj):
                zwróć self.loads(self.dumps(obj, self.proto))
            def __repr__(self):
                # We try to be jako descriptive jako possible here since this jest
                # the string which we will allow us to tell the pickle
                # configuration we are using during debugging.
                zwróć ("PickleCopier(proto={}, dumps={}.{}, loads={}.{})"
                        .format(self.proto,
                                self.dumps.__module__, self.dumps.__qualname__,
                                self.loads.__module__, self.loads.__qualname__))
        zwróć (PickleCopier(*args) dla args w
                   itertools.product(range(pickle.HIGHEST_PROTOCOL + 1),
                                     {pickle.dumps, pickle._dumps},
                                     {pickle.loads, pickle._loads}))

    def test_pickle_slots(self):
        # Tests pickling of classes przy __slots__.

        # Pickling of classes przy __slots__ but without __getstate__ should
        # fail (jeżeli using protocol 0 albo 1)
        global C
        klasa C:
            __slots__ = ['a']
        przy self.assertRaises(TypeError):
            pickle.dumps(C(), 0)

        global D
        klasa D(C):
            dalej
        przy self.assertRaises(TypeError):
            pickle.dumps(D(), 0)

        klasa C:
            "A klasa przy __getstate__ oraz __setstate__ implemented."
            __slots__ = ['a']
            def __getstate__(self):
                state = getattr(self, '__dict__', {}).copy()
                dla cls w type(self).__mro__:
                    dla slot w cls.__dict__.get('__slots__', ()):
                        spróbuj:
                            state[slot] = getattr(self, slot)
                        wyjąwszy AttributeError:
                            dalej
                zwróć state
            def __setstate__(self, state):
                dla k, v w state.items():
                    setattr(self, k, v)
            def __repr__(self):
                zwróć "%s()<%r>" % (type(self).__name__, self.__getstate__())

        klasa D(C):
            "A subclass of a klasa przy slots."
            dalej

        global E
        klasa E(C):
            "A subclass przy an extra slot."
            __slots__ = ['b']

        # Now it should work
        dla pickle_copier w self._generate_pickle_copiers():
            przy self.subTest(pickle_copier=pickle_copier):
                x = C()
                y = pickle_copier.copy(x)
                self._assert_is_copy(x, y)

                x.a = 42
                y = pickle_copier.copy(x)
                self._assert_is_copy(x, y)

                x = D()
                x.a = 42
                x.b = 100
                y = pickle_copier.copy(x)
                self._assert_is_copy(x, y)

                x = E()
                x.a = 42
                x.b = "foo"
                y = pickle_copier.copy(x)
                self._assert_is_copy(x, y)

    def test_reduce_copying(self):
        # Tests pickling oraz copying new-style classes oraz objects.
        global C1
        klasa C1:
            "The state of this klasa jest copyable via its instance dict."
            ARGS = (1, 2)
            NEED_DICT_COPYING = Prawda
            def __init__(self, a, b):
                super().__init__()
                self.a = a
                self.b = b
            def __repr__(self):
                zwróć "C1(%r, %r)" % (self.a, self.b)

        global C2
        klasa C2(list):
            "A list subclass copyable via __getnewargs__."
            ARGS = (1, 2)
            NEED_DICT_COPYING = Nieprawda
            def __new__(cls, a, b):
                self = super().__new__(cls)
                self.a = a
                self.b = b
                zwróć self
            def __init__(self, *args):
                super().__init__()
                # This helps testing that __init__ jest nie called during the
                # unpickling process, which would cause extra appends.
                self.append("cheese")
            @classmethod
            def __getnewargs__(cls):
                zwróć cls.ARGS
            def __repr__(self):
                zwróć "C2(%r, %r)<%r>" % (self.a, self.b, list(self))

        global C3
        klasa C3(list):
            "A list subclass copyable via __getstate__."
            ARGS = (1, 2)
            NEED_DICT_COPYING = Nieprawda
            def __init__(self, a, b):
                self.a = a
                self.b = b
                # This helps testing that __init__ jest nie called during the
                # unpickling process, which would cause extra appends.
                self.append("cheese")
            @classmethod
            def __getstate__(cls):
                zwróć cls.ARGS
            def __setstate__(self, state):
                a, b = state
                self.a = a
                self.b = b
            def __repr__(self):
                zwróć "C3(%r, %r)<%r>" % (self.a, self.b, list(self))

        global C4
        klasa C4(int):
            "An int subclass copyable via __getnewargs__."
            ARGS = ("hello", "world", 1)
            NEED_DICT_COPYING = Nieprawda
            def __new__(cls, a, b, value):
                self = super().__new__(cls, value)
                self.a = a
                self.b = b
                zwróć self
            @classmethod
            def __getnewargs__(cls):
                zwróć cls.ARGS
            def __repr__(self):
                zwróć "C4(%r, %r)<%r>" % (self.a, self.b, int(self))

        global C5
        klasa C5(int):
            "An int subclass copyable via __getnewargs_ex__."
            ARGS = (1, 2)
            KWARGS = {'value': 3}
            NEED_DICT_COPYING = Nieprawda
            def __new__(cls, a, b, *, value=0):
                self = super().__new__(cls, value)
                self.a = a
                self.b = b
                zwróć self
            @classmethod
            def __getnewargs_ex__(cls):
                zwróć (cls.ARGS, cls.KWARGS)
            def __repr__(self):
                zwróć "C5(%r, %r)<%r>" % (self.a, self.b, int(self))

        test_classes = (C1, C2, C3, C4, C5)
        # Testing copying through pickle
        pickle_copiers = self._generate_pickle_copiers()
        dla cls, pickle_copier w itertools.product(test_classes, pickle_copiers):
            przy self.subTest(cls=cls, pickle_copier=pickle_copier):
                kwargs = getattr(cls, 'KWARGS', {})
                obj = cls(*cls.ARGS, **kwargs)
                proto = pickle_copier.proto
                jeżeli 2 <= proto < 4 oraz hasattr(cls, '__getnewargs_ex__'):
                    przy self.assertRaises(ValueError):
                        pickle_copier.dumps(obj, proto)
                    kontynuuj
                objcopy = pickle_copier.copy(obj)
                self._assert_is_copy(obj, objcopy)
                # For test classes that supports this, make sure we didn't go
                # around the reduce protocol by simply copying the attribute
                # dictionary. We clear attributes using the previous copy to
                # nie mutate the original argument.
                jeżeli proto >= 2 oraz nie cls.NEED_DICT_COPYING:
                    objcopy.__dict__.clear()
                    objcopy2 = pickle_copier.copy(objcopy)
                    self._assert_is_copy(obj, objcopy2)

        # Testing copying through copy.deepcopy()
        dla cls w test_classes:
            przy self.subTest(cls=cls):
                kwargs = getattr(cls, 'KWARGS', {})
                obj = cls(*cls.ARGS, **kwargs)
                # XXX: We need to modify the copy module to support PEP 3154's
                # reduce protocol 4.
                jeżeli hasattr(cls, '__getnewargs_ex__'):
                    kontynuuj
                objcopy = deepcopy(obj)
                self._assert_is_copy(obj, objcopy)
                # For test classes that supports this, make sure we didn't go
                # around the reduce protocol by simply copying the attribute
                # dictionary. We clear attributes using the previous copy to
                # nie mutate the original argument.
                jeżeli nie cls.NEED_DICT_COPYING:
                    objcopy.__dict__.clear()
                    objcopy2 = deepcopy(objcopy)
                    self._assert_is_copy(obj, objcopy2)


klasa SharedKeyTests(unittest.TestCase):

    @support.cpython_only
    def test_subclasses(self):
        # Verify that subclasses can share keys (per PEP 412)
        klasa A:
            dalej
        klasa B(A):
            dalej

        a, b = A(), B()
        self.assertEqual(sys.getsizeof(vars(a)), sys.getsizeof(vars(b)))
        self.assertLess(sys.getsizeof(vars(a)), sys.getsizeof({}))
        a.x, a.y, a.z, a.w = range(4)
        self.assertNotEqual(sys.getsizeof(vars(a)), sys.getsizeof(vars(b)))
        a2 = A()
        self.assertEqual(sys.getsizeof(vars(a)), sys.getsizeof(vars(a2)))
        self.assertLess(sys.getsizeof(vars(a)), sys.getsizeof({}))
        b.u, b.v, b.w, b.t = range(4)
        self.assertLess(sys.getsizeof(vars(b)), sys.getsizeof({}))


klasa DebugHelperMeta(type):
    """
    Sets default __doc__ oraz simplifies repr() output.
    """
    def __new__(mcls, name, bases, attrs):
        jeżeli attrs.get('__doc__') jest Nic:
            attrs['__doc__'] = name  # helps when debugging przy gdb
        zwróć type.__new__(mcls, name, bases, attrs)
    def __repr__(cls):
        zwróć repr(cls.__name__)


klasa MroTest(unittest.TestCase):
    """
    Regressions dla some bugs revealed through
    mcsl.mro() customization (typeobject.c: mro_internal()) oraz
    cls.__bases__ assignment (typeobject.c: type_set_bases()).
    """

    def setUp(self):
        self.step = 0
        self.ready = Nieprawda

    def step_until(self, limit):
        ret = (self.step < limit)
        jeżeli ret:
            self.step += 1
        zwróć ret

    def test_incomplete_set_bases_on_self(self):
        """
        type_set_bases must be aware that type->tp_mro can be NULL.
        """
        klasa M(DebugHelperMeta):
            def mro(cls):
                jeżeli self.step_until(1):
                    assert cls.__mro__ jest Nic
                    cls.__bases__ += ()

                zwróć type.mro(cls)

        klasa A(metaclass=M):
            dalej

    def test_reent_set_bases_on_base(self):
        """
        Deep reentrancy must nie over-decref old_mro.
        """
        klasa M(DebugHelperMeta):
            def mro(cls):
                jeżeli cls.__mro__ jest nie Nic oraz cls.__name__ == 'B':
                    # 4-5 steps are usually enough to make it crash somewhere
                    jeżeli self.step_until(10):
                        A.__bases__ += ()

                zwróć type.mro(cls)

        klasa A(metaclass=M):
            dalej
        klasa B(A):
            dalej
        B.__bases__ += ()

    def test_reent_set_bases_on_direct_base(self):
        """
        Similar to test_reent_set_bases_on_base, but may crash differently.
        """
        klasa M(DebugHelperMeta):
            def mro(cls):
                base = cls.__bases__[0]
                jeżeli base jest nie object:
                    jeżeli self.step_until(5):
                        base.__bases__ += ()

                zwróć type.mro(cls)

        klasa A(metaclass=M):
            dalej
        klasa B(A):
            dalej
        klasa C(B):
            dalej

    def test_reent_set_bases_tp_base_cycle(self):
        """
        type_set_bases must check dla an inheritance cycle nie only through
        MRO of the type, which may be nie yet updated w case of reentrance,
        but also through tp_base chain, which jest assigned before diving into
        inner calls to mro().

        Otherwise, the following snippet can loop forever:
            do {
                // ...
                type = type->tp_base;
            } dopóki (type != NULL);

        Functions that rely on tp_base (like solid_base oraz PyType_IsSubtype)
        would nie be happy w that case, causing a stack overflow.
        """
        klasa M(DebugHelperMeta):
            def mro(cls):
                jeżeli self.ready:
                    jeżeli cls.__name__ == 'B1':
                        B2.__bases__ = (B1,)
                    jeżeli cls.__name__ == 'B2':
                        B1.__bases__ = (B2,)
                zwróć type.mro(cls)

        klasa A(metaclass=M):
            dalej
        klasa B1(A):
            dalej
        klasa B2(A):
            dalej

        self.ready = Prawda
        przy self.assertRaises(TypeError):
            B1.__bases__ += ()

    def test_tp_subclasses_cycle_in_update_slots(self):
        """
        type_set_bases must check dla reentrancy upon finishing its job
        by updating tp_subclasses of old/new bases of the type.
        Otherwise, an implicit inheritance cycle through tp_subclasses
        can przerwij functions that recurse on elements of that field
        (like recurse_down_subclasses oraz mro_hierarchy) eventually
        leading to a stack overflow.
        """
        klasa M(DebugHelperMeta):
            def mro(cls):
                jeżeli self.ready oraz cls.__name__ == 'C':
                    self.ready = Nieprawda
                    C.__bases__ = (B2,)
                zwróć type.mro(cls)

        klasa A(metaclass=M):
            dalej
        klasa B1(A):
            dalej
        klasa B2(A):
            dalej
        klasa C(A):
            dalej

        self.ready = Prawda
        C.__bases__ = (B1,)
        B1.__bases__ = (C,)

        self.assertEqual(C.__bases__, (B2,))
        self.assertEqual(B2.__subclasses__(), [C])
        self.assertEqual(B1.__subclasses__(), [])

        self.assertEqual(B1.__bases__, (C,))
        self.assertEqual(C.__subclasses__(), [B1])

    def test_tp_subclasses_cycle_error_return_path(self):
        """
        The same jako test_tp_subclasses_cycle_in_update_slots, but tests
        a code path executed on error (goto bail).
        """
        klasa E(Exception):
            dalej
        klasa M(DebugHelperMeta):
            def mro(cls):
                jeżeli self.ready oraz cls.__name__ == 'C':
                    jeżeli C.__bases__ == (B2,):
                        self.ready = Nieprawda
                    inaczej:
                        C.__bases__ = (B2,)
                        podnieś E
                zwróć type.mro(cls)

        klasa A(metaclass=M):
            dalej
        klasa B1(A):
            dalej
        klasa B2(A):
            dalej
        klasa C(A):
            dalej

        self.ready = Prawda
        przy self.assertRaises(E):
            C.__bases__ = (B1,)
        B1.__bases__ = (C,)

        self.assertEqual(C.__bases__, (B2,))
        self.assertEqual(C.__mro__, tuple(type.mro(C)))

    def test_incomplete_extend(self):
        """
        Extending an unitialized type przy type->tp_mro == NULL must
        throw a reasonable TypeError exception, instead of failing
        przy PyErr_BadInternalCall.
        """
        klasa M(DebugHelperMeta):
            def mro(cls):
                jeżeli cls.__mro__ jest Nic oraz cls.__name__ != 'X':
                    przy self.assertRaises(TypeError):
                        klasa X(cls):
                            dalej

                zwróć type.mro(cls)

        klasa A(metaclass=M):
            dalej

    def test_incomplete_super(self):
        """
        Attrubute lookup on a super object must be aware that
        its target type can be uninitialized (type->tp_mro == NULL).
        """
        klasa M(DebugHelperMeta):
            def mro(cls):
                jeżeli cls.__mro__ jest Nic:
                    przy self.assertRaises(AttributeError):
                        super(cls, cls).xxx

                zwróć type.mro(cls)

        klasa A(metaclass=M):
            dalej


def test_main():
    # Run all local test cases, przy PTypesLongInitTest first.
    support.run_unittest(PTypesLongInitTest, OperatorsTest,
                         ClassPropertiesAndMethods, DictProxyTests,
                         MiscTests, PicklingTests, SharedKeyTests,
                         MroTest)

jeżeli __name__ == "__main__":
    test_main()
