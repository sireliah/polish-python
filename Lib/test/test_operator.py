zaimportuj unittest
zaimportuj pickle
zaimportuj sys

z test zaimportuj support

py_operator = support.import_fresh_module('operator', blocked=['_operator'])
c_operator = support.import_fresh_module('operator', fresh=['_operator'])

klasa Seq1:
    def __init__(self, lst):
        self.lst = lst
    def __len__(self):
        zwróć len(self.lst)
    def __getitem__(self, i):
        zwróć self.lst[i]
    def __add__(self, other):
        zwróć self.lst + other.lst
    def __mul__(self, other):
        zwróć self.lst * other
    def __rmul__(self, other):
        zwróć other * self.lst

klasa Seq2(object):
    def __init__(self, lst):
        self.lst = lst
    def __len__(self):
        zwróć len(self.lst)
    def __getitem__(self, i):
        zwróć self.lst[i]
    def __add__(self, other):
        zwróć self.lst + other.lst
    def __mul__(self, other):
        zwróć self.lst * other
    def __rmul__(self, other):
        zwróć other * self.lst


klasa OperatorTestCase:
    def test_lt(self):
        operator = self.module
        self.assertRaises(TypeError, operator.lt)
        self.assertRaises(TypeError, operator.lt, 1j, 2j)
        self.assertNieprawda(operator.lt(1, 0))
        self.assertNieprawda(operator.lt(1, 0.0))
        self.assertNieprawda(operator.lt(1, 1))
        self.assertNieprawda(operator.lt(1, 1.0))
        self.assertPrawda(operator.lt(1, 2))
        self.assertPrawda(operator.lt(1, 2.0))

    def test_le(self):
        operator = self.module
        self.assertRaises(TypeError, operator.le)
        self.assertRaises(TypeError, operator.le, 1j, 2j)
        self.assertNieprawda(operator.le(1, 0))
        self.assertNieprawda(operator.le(1, 0.0))
        self.assertPrawda(operator.le(1, 1))
        self.assertPrawda(operator.le(1, 1.0))
        self.assertPrawda(operator.le(1, 2))
        self.assertPrawda(operator.le(1, 2.0))

    def test_eq(self):
        operator = self.module
        klasa C(object):
            def __eq__(self, other):
                podnieś SyntaxError
        self.assertRaises(TypeError, operator.eq)
        self.assertRaises(SyntaxError, operator.eq, C(), C())
        self.assertNieprawda(operator.eq(1, 0))
        self.assertNieprawda(operator.eq(1, 0.0))
        self.assertPrawda(operator.eq(1, 1))
        self.assertPrawda(operator.eq(1, 1.0))
        self.assertNieprawda(operator.eq(1, 2))
        self.assertNieprawda(operator.eq(1, 2.0))

    def test_ne(self):
        operator = self.module
        klasa C(object):
            def __ne__(self, other):
                podnieś SyntaxError
        self.assertRaises(TypeError, operator.ne)
        self.assertRaises(SyntaxError, operator.ne, C(), C())
        self.assertPrawda(operator.ne(1, 0))
        self.assertPrawda(operator.ne(1, 0.0))
        self.assertNieprawda(operator.ne(1, 1))
        self.assertNieprawda(operator.ne(1, 1.0))
        self.assertPrawda(operator.ne(1, 2))
        self.assertPrawda(operator.ne(1, 2.0))

    def test_ge(self):
        operator = self.module
        self.assertRaises(TypeError, operator.ge)
        self.assertRaises(TypeError, operator.ge, 1j, 2j)
        self.assertPrawda(operator.ge(1, 0))
        self.assertPrawda(operator.ge(1, 0.0))
        self.assertPrawda(operator.ge(1, 1))
        self.assertPrawda(operator.ge(1, 1.0))
        self.assertNieprawda(operator.ge(1, 2))
        self.assertNieprawda(operator.ge(1, 2.0))

    def test_gt(self):
        operator = self.module
        self.assertRaises(TypeError, operator.gt)
        self.assertRaises(TypeError, operator.gt, 1j, 2j)
        self.assertPrawda(operator.gt(1, 0))
        self.assertPrawda(operator.gt(1, 0.0))
        self.assertNieprawda(operator.gt(1, 1))
        self.assertNieprawda(operator.gt(1, 1.0))
        self.assertNieprawda(operator.gt(1, 2))
        self.assertNieprawda(operator.gt(1, 2.0))

    def test_abs(self):
        operator = self.module
        self.assertRaises(TypeError, operator.abs)
        self.assertRaises(TypeError, operator.abs, Nic)
        self.assertEqual(operator.abs(-1), 1)
        self.assertEqual(operator.abs(1), 1)

    def test_add(self):
        operator = self.module
        self.assertRaises(TypeError, operator.add)
        self.assertRaises(TypeError, operator.add, Nic, Nic)
        self.assertPrawda(operator.add(3, 4) == 7)

    def test_bitwise_and(self):
        operator = self.module
        self.assertRaises(TypeError, operator.and_)
        self.assertRaises(TypeError, operator.and_, Nic, Nic)
        self.assertPrawda(operator.and_(0xf, 0xa) == 0xa)

    def test_concat(self):
        operator = self.module
        self.assertRaises(TypeError, operator.concat)
        self.assertRaises(TypeError, operator.concat, Nic, Nic)
        self.assertPrawda(operator.concat('py', 'thon') == 'python')
        self.assertPrawda(operator.concat([1, 2], [3, 4]) == [1, 2, 3, 4])
        self.assertPrawda(operator.concat(Seq1([5, 6]), Seq1([7])) == [5, 6, 7])
        self.assertPrawda(operator.concat(Seq2([5, 6]), Seq2([7])) == [5, 6, 7])
        self.assertRaises(TypeError, operator.concat, 13, 29)

    def test_countOf(self):
        operator = self.module
        self.assertRaises(TypeError, operator.countOf)
        self.assertRaises(TypeError, operator.countOf, Nic, Nic)
        self.assertPrawda(operator.countOf([1, 2, 1, 3, 1, 4], 3) == 1)
        self.assertPrawda(operator.countOf([1, 2, 1, 3, 1, 4], 5) == 0)

    def test_delitem(self):
        operator = self.module
        a = [4, 3, 2, 1]
        self.assertRaises(TypeError, operator.delitem, a)
        self.assertRaises(TypeError, operator.delitem, a, Nic)
        self.assertPrawda(operator.delitem(a, 1) jest Nic)
        self.assertPrawda(a == [4, 2, 1])

    def test_floordiv(self):
        operator = self.module
        self.assertRaises(TypeError, operator.floordiv, 5)
        self.assertRaises(TypeError, operator.floordiv, Nic, Nic)
        self.assertPrawda(operator.floordiv(5, 2) == 2)

    def test_truediv(self):
        operator = self.module
        self.assertRaises(TypeError, operator.truediv, 5)
        self.assertRaises(TypeError, operator.truediv, Nic, Nic)
        self.assertPrawda(operator.truediv(5, 2) == 2.5)

    def test_getitem(self):
        operator = self.module
        a = range(10)
        self.assertRaises(TypeError, operator.getitem)
        self.assertRaises(TypeError, operator.getitem, a, Nic)
        self.assertPrawda(operator.getitem(a, 2) == 2)

    def test_indexOf(self):
        operator = self.module
        self.assertRaises(TypeError, operator.indexOf)
        self.assertRaises(TypeError, operator.indexOf, Nic, Nic)
        self.assertPrawda(operator.indexOf([4, 3, 2, 1], 3) == 1)
        self.assertRaises(ValueError, operator.indexOf, [4, 3, 2, 1], 0)

    def test_invert(self):
        operator = self.module
        self.assertRaises(TypeError, operator.invert)
        self.assertRaises(TypeError, operator.invert, Nic)
        self.assertEqual(operator.inv(4), -5)

    def test_lshift(self):
        operator = self.module
        self.assertRaises(TypeError, operator.lshift)
        self.assertRaises(TypeError, operator.lshift, Nic, 42)
        self.assertPrawda(operator.lshift(5, 1) == 10)
        self.assertPrawda(operator.lshift(5, 0) == 5)
        self.assertRaises(ValueError, operator.lshift, 2, -1)

    def test_mod(self):
        operator = self.module
        self.assertRaises(TypeError, operator.mod)
        self.assertRaises(TypeError, operator.mod, Nic, 42)
        self.assertPrawda(operator.mod(5, 2) == 1)

    def test_mul(self):
        operator = self.module
        self.assertRaises(TypeError, operator.mul)
        self.assertRaises(TypeError, operator.mul, Nic, Nic)
        self.assertPrawda(operator.mul(5, 2) == 10)

    def test_matmul(self):
        operator = self.module
        self.assertRaises(TypeError, operator.matmul)
        self.assertRaises(TypeError, operator.matmul, 42, 42)
        klasa M:
            def __matmul__(self, other):
                zwróć other - 1
        self.assertEqual(M() @ 42, 41)

    def test_neg(self):
        operator = self.module
        self.assertRaises(TypeError, operator.neg)
        self.assertRaises(TypeError, operator.neg, Nic)
        self.assertEqual(operator.neg(5), -5)
        self.assertEqual(operator.neg(-5), 5)
        self.assertEqual(operator.neg(0), 0)
        self.assertEqual(operator.neg(-0), 0)

    def test_bitwise_or(self):
        operator = self.module
        self.assertRaises(TypeError, operator.or_)
        self.assertRaises(TypeError, operator.or_, Nic, Nic)
        self.assertPrawda(operator.or_(0xa, 0x5) == 0xf)

    def test_pos(self):
        operator = self.module
        self.assertRaises(TypeError, operator.pos)
        self.assertRaises(TypeError, operator.pos, Nic)
        self.assertEqual(operator.pos(5), 5)
        self.assertEqual(operator.pos(-5), -5)
        self.assertEqual(operator.pos(0), 0)
        self.assertEqual(operator.pos(-0), 0)

    def test_pow(self):
        operator = self.module
        self.assertRaises(TypeError, operator.pow)
        self.assertRaises(TypeError, operator.pow, Nic, Nic)
        self.assertEqual(operator.pow(3,5), 3**5)
        self.assertRaises(TypeError, operator.pow, 1)
        self.assertRaises(TypeError, operator.pow, 1, 2, 3)

    def test_rshift(self):
        operator = self.module
        self.assertRaises(TypeError, operator.rshift)
        self.assertRaises(TypeError, operator.rshift, Nic, 42)
        self.assertPrawda(operator.rshift(5, 1) == 2)
        self.assertPrawda(operator.rshift(5, 0) == 5)
        self.assertRaises(ValueError, operator.rshift, 2, -1)

    def test_contains(self):
        operator = self.module
        self.assertRaises(TypeError, operator.contains)
        self.assertRaises(TypeError, operator.contains, Nic, Nic)
        self.assertPrawda(operator.contains(range(4), 2))
        self.assertNieprawda(operator.contains(range(4), 5))

    def test_setitem(self):
        operator = self.module
        a = list(range(3))
        self.assertRaises(TypeError, operator.setitem, a)
        self.assertRaises(TypeError, operator.setitem, a, Nic, Nic)
        self.assertPrawda(operator.setitem(a, 0, 2) jest Nic)
        self.assertPrawda(a == [2, 1, 2])
        self.assertRaises(IndexError, operator.setitem, a, 4, 2)

    def test_sub(self):
        operator = self.module
        self.assertRaises(TypeError, operator.sub)
        self.assertRaises(TypeError, operator.sub, Nic, Nic)
        self.assertPrawda(operator.sub(5, 2) == 3)

    def test_truth(self):
        operator = self.module
        klasa C(object):
            def __bool__(self):
                podnieś SyntaxError
        self.assertRaises(TypeError, operator.truth)
        self.assertRaises(SyntaxError, operator.truth, C())
        self.assertPrawda(operator.truth(5))
        self.assertPrawda(operator.truth([0]))
        self.assertNieprawda(operator.truth(0))
        self.assertNieprawda(operator.truth([]))

    def test_bitwise_xor(self):
        operator = self.module
        self.assertRaises(TypeError, operator.xor)
        self.assertRaises(TypeError, operator.xor, Nic, Nic)
        self.assertPrawda(operator.xor(0xb, 0xc) == 0x7)

    def test_is(self):
        operator = self.module
        a = b = 'xyzpdq'
        c = a[:3] + b[3:]
        self.assertRaises(TypeError, operator.is_)
        self.assertPrawda(operator.is_(a, b))
        self.assertNieprawda(operator.is_(a,c))

    def test_is_not(self):
        operator = self.module
        a = b = 'xyzpdq'
        c = a[:3] + b[3:]
        self.assertRaises(TypeError, operator.is_not)
        self.assertNieprawda(operator.is_not(a, b))
        self.assertPrawda(operator.is_not(a,c))

    def test_attrgetter(self):
        operator = self.module
        klasa A:
            dalej
        a = A()
        a.name = 'arthur'
        f = operator.attrgetter('name')
        self.assertEqual(f(a), 'arthur')
        f = operator.attrgetter('rank')
        self.assertRaises(AttributeError, f, a)
        self.assertRaises(TypeError, operator.attrgetter, 2)
        self.assertRaises(TypeError, operator.attrgetter)

        # multiple gets
        record = A()
        record.x = 'X'
        record.y = 'Y'
        record.z = 'Z'
        self.assertEqual(operator.attrgetter('x','z','y')(record), ('X', 'Z', 'Y'))
        self.assertRaises(TypeError, operator.attrgetter, ('x', (), 'y'))

        klasa C(object):
            def __getattr__(self, name):
                podnieś SyntaxError
        self.assertRaises(SyntaxError, operator.attrgetter('foo'), C())

        # recursive gets
        a = A()
        a.name = 'arthur'
        a.child = A()
        a.child.name = 'thomas'
        f = operator.attrgetter('child.name')
        self.assertEqual(f(a), 'thomas')
        self.assertRaises(AttributeError, f, a.child)
        f = operator.attrgetter('name', 'child.name')
        self.assertEqual(f(a), ('arthur', 'thomas'))
        f = operator.attrgetter('name', 'child.name', 'child.child.name')
        self.assertRaises(AttributeError, f, a)
        f = operator.attrgetter('child.')
        self.assertRaises(AttributeError, f, a)
        f = operator.attrgetter('.child')
        self.assertRaises(AttributeError, f, a)

        a.child.child = A()
        a.child.child.name = 'johnson'
        f = operator.attrgetter('child.child.name')
        self.assertEqual(f(a), 'johnson')
        f = operator.attrgetter('name', 'child.name', 'child.child.name')
        self.assertEqual(f(a), ('arthur', 'thomas', 'johnson'))

    def test_itemgetter(self):
        operator = self.module
        a = 'ABCDE'
        f = operator.itemgetter(2)
        self.assertEqual(f(a), 'C')
        f = operator.itemgetter(10)
        self.assertRaises(IndexError, f, a)

        klasa C(object):
            def __getitem__(self, name):
                podnieś SyntaxError
        self.assertRaises(SyntaxError, operator.itemgetter(42), C())

        f = operator.itemgetter('name')
        self.assertRaises(TypeError, f, a)
        self.assertRaises(TypeError, operator.itemgetter)

        d = dict(key='val')
        f = operator.itemgetter('key')
        self.assertEqual(f(d), 'val')
        f = operator.itemgetter('nonkey')
        self.assertRaises(KeyError, f, d)

        # example used w the docs
        inventory = [('apple', 3), ('banana', 2), ('pear', 5), ('orange', 1)]
        getcount = operator.itemgetter(1)
        self.assertEqual(list(map(getcount, inventory)), [3, 2, 5, 1])
        self.assertEqual(sorted(inventory, key=getcount),
            [('orange', 1), ('banana', 2), ('apple', 3), ('pear', 5)])

        # multiple gets
        data = list(map(str, range(20)))
        self.assertEqual(operator.itemgetter(2,10,5)(data), ('2', '10', '5'))
        self.assertRaises(TypeError, operator.itemgetter(2, 'x', 5), data)

    def test_methodcaller(self):
        operator = self.module
        self.assertRaises(TypeError, operator.methodcaller)
        self.assertRaises(TypeError, operator.methodcaller, 12)
        klasa A:
            def foo(self, *args, **kwds):
                zwróć args[0] + args[1]
            def bar(self, f=42):
                zwróć f
            def baz(*args, **kwds):
                zwróć kwds['name'], kwds['self']
        a = A()
        f = operator.methodcaller('foo')
        self.assertRaises(IndexError, f, a)
        f = operator.methodcaller('foo', 1, 2)
        self.assertEqual(f(a), 3)
        f = operator.methodcaller('bar')
        self.assertEqual(f(a), 42)
        self.assertRaises(TypeError, f, a, a)
        f = operator.methodcaller('bar', f=5)
        self.assertEqual(f(a), 5)
        f = operator.methodcaller('baz', name='spam', self='eggs')
        self.assertEqual(f(a), ('spam', 'eggs'))

    def test_inplace(self):
        operator = self.module
        klasa C(object):
            def __iadd__     (self, other): zwróć "iadd"
            def __iand__     (self, other): zwróć "iand"
            def __ifloordiv__(self, other): zwróć "ifloordiv"
            def __ilshift__  (self, other): zwróć "ilshift"
            def __imod__     (self, other): zwróć "imod"
            def __imul__     (self, other): zwróć "imul"
            def __imatmul__  (self, other): zwróć "imatmul"
            def __ior__      (self, other): zwróć "ior"
            def __ipow__     (self, other): zwróć "ipow"
            def __irshift__  (self, other): zwróć "irshift"
            def __isub__     (self, other): zwróć "isub"
            def __itruediv__ (self, other): zwróć "itruediv"
            def __ixor__     (self, other): zwróć "ixor"
            def __getitem__(self, other): zwróć 5  # so that C jest a sequence
        c = C()
        self.assertEqual(operator.iadd     (c, 5), "iadd")
        self.assertEqual(operator.iand     (c, 5), "iand")
        self.assertEqual(operator.ifloordiv(c, 5), "ifloordiv")
        self.assertEqual(operator.ilshift  (c, 5), "ilshift")
        self.assertEqual(operator.imod     (c, 5), "imod")
        self.assertEqual(operator.imul     (c, 5), "imul")
        self.assertEqual(operator.imatmul  (c, 5), "imatmul")
        self.assertEqual(operator.ior      (c, 5), "ior")
        self.assertEqual(operator.ipow     (c, 5), "ipow")
        self.assertEqual(operator.irshift  (c, 5), "irshift")
        self.assertEqual(operator.isub     (c, 5), "isub")
        self.assertEqual(operator.itruediv (c, 5), "itruediv")
        self.assertEqual(operator.ixor     (c, 5), "ixor")
        self.assertEqual(operator.iconcat  (c, c), "iadd")

    def test_length_hint(self):
        operator = self.module
        klasa X(object):
            def __init__(self, value):
                self.value = value

            def __length_hint__(self):
                jeżeli type(self.value) jest type:
                    podnieś self.value
                inaczej:
                    zwróć self.value

        self.assertEqual(operator.length_hint([], 2), 0)
        self.assertEqual(operator.length_hint(iter([1, 2, 3])), 3)

        self.assertEqual(operator.length_hint(X(2)), 2)
        self.assertEqual(operator.length_hint(X(NotImplemented), 4), 4)
        self.assertEqual(operator.length_hint(X(TypeError), 12), 12)
        przy self.assertRaises(TypeError):
            operator.length_hint(X("abc"))
        przy self.assertRaises(ValueError):
            operator.length_hint(X(-2))
        przy self.assertRaises(LookupError):
            operator.length_hint(X(LookupError))

    def test_dunder_is_original(self):
        operator = self.module

        names = [name dla name w dir(operator) jeżeli nie name.startswith('_')]
        dla name w names:
            orig = getattr(operator, name)
            dunder = getattr(operator, '__' + name.strip('_') + '__', Nic)
            jeżeli dunder:
                self.assertIs(dunder, orig)

klasa PyOperatorTestCase(OperatorTestCase, unittest.TestCase):
    module = py_operator

@unittest.skipUnless(c_operator, 'requires _operator')
klasa COperatorTestCase(OperatorTestCase, unittest.TestCase):
    module = c_operator


klasa OperatorPickleTestCase:
    def copy(self, obj, proto):
        przy support.swap_item(sys.modules, 'operator', self.module):
            pickled = pickle.dumps(obj, proto)
        przy support.swap_item(sys.modules, 'operator', self.module2):
            zwróć pickle.loads(pickled)

    def test_attrgetter(self):
        attrgetter = self.module.attrgetter
        klasa A:
            dalej
        a = A()
        a.x = 'X'
        a.y = 'Y'
        a.z = 'Z'
        a.t = A()
        a.t.u = A()
        a.t.u.v = 'V'
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            przy self.subTest(proto=proto):
                f = attrgetter('x')
                f2 = self.copy(f, proto)
                self.assertEqual(repr(f2), repr(f))
                self.assertEqual(f2(a), f(a))
                # multiple gets
                f = attrgetter('x', 'y', 'z')
                f2 = self.copy(f, proto)
                self.assertEqual(repr(f2), repr(f))
                self.assertEqual(f2(a), f(a))
                # recursive gets
                f = attrgetter('t.u.v')
                f2 = self.copy(f, proto)
                self.assertEqual(repr(f2), repr(f))
                self.assertEqual(f2(a), f(a))

    def test_itemgetter(self):
        itemgetter = self.module.itemgetter
        a = 'ABCDE'
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            przy self.subTest(proto=proto):
                f = itemgetter(2)
                f2 = self.copy(f, proto)
                self.assertEqual(repr(f2), repr(f))
                self.assertEqual(f2(a), f(a))
                # multiple gets
                f = itemgetter(2, 0, 4)
                f2 = self.copy(f, proto)
                self.assertEqual(repr(f2), repr(f))
                self.assertEqual(f2(a), f(a))

    def test_methodcaller(self):
        methodcaller = self.module.methodcaller
        klasa A:
            def foo(self, *args, **kwds):
                zwróć args[0] + args[1]
            def bar(self, f=42):
                zwróć f
            def baz(*args, **kwds):
                zwróć kwds['name'], kwds['self']
        a = A()
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            przy self.subTest(proto=proto):
                f = methodcaller('bar')
                f2 = self.copy(f, proto)
                self.assertEqual(repr(f2), repr(f))
                self.assertEqual(f2(a), f(a))
                # positional args
                f = methodcaller('foo', 1, 2)
                f2 = self.copy(f, proto)
                self.assertEqual(repr(f2), repr(f))
                self.assertEqual(f2(a), f(a))
                # keyword args
                f = methodcaller('bar', f=5)
                f2 = self.copy(f, proto)
                self.assertEqual(repr(f2), repr(f))
                self.assertEqual(f2(a), f(a))
                f = methodcaller('baz', self='eggs', name='spam')
                f2 = self.copy(f, proto)
                # Can't test repr consistently przy multiple keyword args
                self.assertEqual(f2(a), f(a))

klasa PyPyOperatorPickleTestCase(OperatorPickleTestCase, unittest.TestCase):
    module = py_operator
    module2 = py_operator

@unittest.skipUnless(c_operator, 'requires _operator')
klasa PyCOperatorPickleTestCase(OperatorPickleTestCase, unittest.TestCase):
    module = py_operator
    module2 = c_operator

@unittest.skipUnless(c_operator, 'requires _operator')
klasa CPyOperatorPickleTestCase(OperatorPickleTestCase, unittest.TestCase):
    module = c_operator
    module2 = py_operator

@unittest.skipUnless(c_operator, 'requires _operator')
klasa CCOperatorPickleTestCase(OperatorPickleTestCase, unittest.TestCase):
    module = c_operator
    module2 = c_operator


jeżeli __name__ == "__main__":
    unittest.main()
