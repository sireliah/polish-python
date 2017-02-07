# Tests some corner cases przy isinstance() oraz issubclass().  While these
# tests use new style classes oraz properties, they actually do whitebox
# testing of error conditions uncovered when using extension types.

zaimportuj unittest
zaimportuj sys



klasa TestIsInstanceExceptions(unittest.TestCase):
    # Test to make sure that an AttributeError when accessing the instance's
    # class's bases jest masked.  This was actually a bug w Python 2.2 oraz
    # 2.2.1 where the exception wasn't caught but it also wasn't being cleared
    # (leading to an "undetected error" w the debug build).  Set up is,
    # isinstance(inst, cls) where:
    #
    # - cls isn't a type, albo a tuple
    # - cls has a __bases__ attribute
    # - inst has a __class__ attribute
    # - inst.__class__ jako no __bases__ attribute
    #
    # Sounds complicated, I know, but this mimics a situation where an
    # extension type podnieśs an AttributeError when its __bases__ attribute jest
    # gotten.  In that case, isinstance() should zwróć Nieprawda.
    def test_class_has_no_bases(self):
        klasa I(object):
            def getclass(self):
                # This must zwróć an object that has no __bases__ attribute
                zwróć Nic
            __class__ = property(getclass)

        klasa C(object):
            def getbases(self):
                zwróć ()
            __bases__ = property(getbases)

        self.assertEqual(Nieprawda, isinstance(I(), C()))

    # Like above wyjąwszy that inst.__class__.__bases__ podnieśs an exception
    # other than AttributeError
    def test_bases_raises_other_than_attribute_error(self):
        klasa E(object):
            def getbases(self):
                podnieś RuntimeError
            __bases__ = property(getbases)

        klasa I(object):
            def getclass(self):
                zwróć E()
            __class__ = property(getclass)

        klasa C(object):
            def getbases(self):
                zwróć ()
            __bases__ = property(getbases)

        self.assertRaises(RuntimeError, isinstance, I(), C())

    # Here's a situation where getattr(cls, '__bases__') podnieśs an exception.
    # If that exception jest nie AttributeError, it should nie get masked
    def test_dont_mask_non_attribute_error(self):
        klasa I: dalej

        klasa C(object):
            def getbases(self):
                podnieś RuntimeError
            __bases__ = property(getbases)

        self.assertRaises(RuntimeError, isinstance, I(), C())

    # Like above, wyjąwszy that getattr(cls, '__bases__') podnieśs an
    # AttributeError, which /should/ get masked jako a TypeError
    def test_mask_attribute_error(self):
        klasa I: dalej

        klasa C(object):
            def getbases(self):
                podnieś AttributeError
            __bases__ = property(getbases)

        self.assertRaises(TypeError, isinstance, I(), C())

    # check that we don't mask non AttributeErrors
    # see: http://bugs.python.org/issue1574217
    def test_isinstance_dont_mask_non_attribute_error(self):
        klasa C(object):
            def getclass(self):
                podnieś RuntimeError
            __class__ = property(getclass)

        c = C()
        self.assertRaises(RuntimeError, isinstance, c, bool)

        # test another code path
        klasa D: dalej
        self.assertRaises(RuntimeError, isinstance, c, D)


# These tests are similar to above, but tickle certain code paths w
# issubclass() instead of isinstance() -- really PyObject_IsSubclass()
# vs. PyObject_IsInstance().
klasa TestIsSubclassExceptions(unittest.TestCase):
    def test_dont_mask_non_attribute_error(self):
        klasa C(object):
            def getbases(self):
                podnieś RuntimeError
            __bases__ = property(getbases)

        klasa S(C): dalej

        self.assertRaises(RuntimeError, issubclass, C(), S())

    def test_mask_attribute_error(self):
        klasa C(object):
            def getbases(self):
                podnieś AttributeError
            __bases__ = property(getbases)

        klasa S(C): dalej

        self.assertRaises(TypeError, issubclass, C(), S())

    # Like above, but test the second branch, where the __bases__ of the
    # second arg (the cls arg) jest tested.  This means the first arg must
    # zwróć a valid __bases__, oraz it's okay dla it to be a normal --
    # unrelated by inheritance -- class.
    def test_dont_mask_non_attribute_error_in_cls_arg(self):
        klasa B: dalej

        klasa C(object):
            def getbases(self):
                podnieś RuntimeError
            __bases__ = property(getbases)

        self.assertRaises(RuntimeError, issubclass, B, C())

    def test_mask_attribute_error_in_cls_arg(self):
        klasa B: dalej

        klasa C(object):
            def getbases(self):
                podnieś AttributeError
            __bases__ = property(getbases)

        self.assertRaises(TypeError, issubclass, B, C())



# meta classes dla creating abstract classes oraz instances
klasa AbstractClass(object):
    def __init__(self, bases):
        self.bases = bases

    def getbases(self):
        zwróć self.bases
    __bases__ = property(getbases)

    def __call__(self):
        zwróć AbstractInstance(self)

klasa AbstractInstance(object):
    def __init__(self, klass):
        self.klass = klass

    def getclass(self):
        zwróć self.klass
    __class__ = property(getclass)

# abstract classes
AbstractSuper = AbstractClass(bases=())

AbstractChild = AbstractClass(bases=(AbstractSuper,))

# normal classes
klasa Super:
    dalej

klasa Child(Super):
    dalej

# new-style classes
klasa NewSuper(object):
    dalej

klasa NewChild(NewSuper):
    dalej



klasa TestIsInstanceIsSubclass(unittest.TestCase):
    # Tests to ensure that isinstance oraz issubclass work on abstract
    # classes oraz instances.  Before the 2.2 release, TypeErrors were
    # podnieśd when boolean values should have been returned.  The bug was
    # triggered by mixing 'normal' classes oraz instances were with
    # 'abstract' classes oraz instances.  This case tries to test all
    # combinations.

    def test_isinstance_normal(self):
        # normal instances
        self.assertEqual(Prawda, isinstance(Super(), Super))
        self.assertEqual(Nieprawda, isinstance(Super(), Child))
        self.assertEqual(Nieprawda, isinstance(Super(), AbstractSuper))
        self.assertEqual(Nieprawda, isinstance(Super(), AbstractChild))

        self.assertEqual(Prawda, isinstance(Child(), Super))
        self.assertEqual(Nieprawda, isinstance(Child(), AbstractSuper))

    def test_isinstance_abstract(self):
        # abstract instances
        self.assertEqual(Prawda, isinstance(AbstractSuper(), AbstractSuper))
        self.assertEqual(Nieprawda, isinstance(AbstractSuper(), AbstractChild))
        self.assertEqual(Nieprawda, isinstance(AbstractSuper(), Super))
        self.assertEqual(Nieprawda, isinstance(AbstractSuper(), Child))

        self.assertEqual(Prawda, isinstance(AbstractChild(), AbstractChild))
        self.assertEqual(Prawda, isinstance(AbstractChild(), AbstractSuper))
        self.assertEqual(Nieprawda, isinstance(AbstractChild(), Super))
        self.assertEqual(Nieprawda, isinstance(AbstractChild(), Child))

    def test_subclass_normal(self):
        # normal classes
        self.assertEqual(Prawda, issubclass(Super, Super))
        self.assertEqual(Nieprawda, issubclass(Super, AbstractSuper))
        self.assertEqual(Nieprawda, issubclass(Super, Child))

        self.assertEqual(Prawda, issubclass(Child, Child))
        self.assertEqual(Prawda, issubclass(Child, Super))
        self.assertEqual(Nieprawda, issubclass(Child, AbstractSuper))

    def test_subclass_abstract(self):
        # abstract classes
        self.assertEqual(Prawda, issubclass(AbstractSuper, AbstractSuper))
        self.assertEqual(Nieprawda, issubclass(AbstractSuper, AbstractChild))
        self.assertEqual(Nieprawda, issubclass(AbstractSuper, Child))

        self.assertEqual(Prawda, issubclass(AbstractChild, AbstractChild))
        self.assertEqual(Prawda, issubclass(AbstractChild, AbstractSuper))
        self.assertEqual(Nieprawda, issubclass(AbstractChild, Super))
        self.assertEqual(Nieprawda, issubclass(AbstractChild, Child))

    def test_subclass_tuple(self):
        # test przy a tuple jako the second argument classes
        self.assertEqual(Prawda, issubclass(Child, (Child,)))
        self.assertEqual(Prawda, issubclass(Child, (Super,)))
        self.assertEqual(Nieprawda, issubclass(Super, (Child,)))
        self.assertEqual(Prawda, issubclass(Super, (Child, Super)))
        self.assertEqual(Nieprawda, issubclass(Child, ()))
        self.assertEqual(Prawda, issubclass(Super, (Child, (Super,))))

        self.assertEqual(Prawda, issubclass(NewChild, (NewChild,)))
        self.assertEqual(Prawda, issubclass(NewChild, (NewSuper,)))
        self.assertEqual(Nieprawda, issubclass(NewSuper, (NewChild,)))
        self.assertEqual(Prawda, issubclass(NewSuper, (NewChild, NewSuper)))
        self.assertEqual(Nieprawda, issubclass(NewChild, ()))
        self.assertEqual(Prawda, issubclass(NewSuper, (NewChild, (NewSuper,))))

        self.assertEqual(Prawda, issubclass(int, (int, (float, int))))
        self.assertEqual(Prawda, issubclass(str, (str, (Child, NewChild, str))))

    def test_subclass_recursion_limit(self):
        # make sure that issubclass podnieśs RecursionError before the C stack jest
        # blown
        self.assertRaises(RecursionError, blowstack, issubclass, str, str)

    def test_isinstance_recursion_limit(self):
        # make sure that issubclass podnieśs RecursionError before the C stack jest
        # blown
        self.assertRaises(RecursionError, blowstack, isinstance, '', str)

def blowstack(fxn, arg, compare_to):
    # Make sure that calling isinstance przy a deeply nested tuple dla its
    # argument will podnieś RecursionError eventually.
    tuple_arg = (compare_to,)
    dla cnt w range(sys.getrecursionlimit()+5):
        tuple_arg = (tuple_arg,)
        fxn(arg, tuple_arg)


jeżeli __name__ == '__main__':
    unittest.main()
