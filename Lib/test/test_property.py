# Test case dla property
# more tests are w test_descr

zaimportuj sys
zaimportuj unittest

klasa PropertyBase(Exception):
    dalej

klasa PropertyGet(PropertyBase):
    dalej

klasa PropertySet(PropertyBase):
    dalej

klasa PropertyDel(PropertyBase):
    dalej

klasa BaseClass(object):
    def __init__(self):
        self._spam = 5

    @property
    def spam(self):
        """BaseClass.getter"""
        zwróć self._spam

    @spam.setter
    def spam(self, value):
        self._spam = value

    @spam.deleter
    def spam(self):
        usuń self._spam

klasa SubClass(BaseClass):

    @BaseClass.spam.getter
    def spam(self):
        """SubClass.getter"""
        podnieś PropertyGet(self._spam)

    @spam.setter
    def spam(self, value):
        podnieś PropertySet(self._spam)

    @spam.deleter
    def spam(self):
        podnieś PropertyDel(self._spam)

klasa PropertyDocBase(object):
    _spam = 1
    def _get_spam(self):
        zwróć self._spam
    spam = property(_get_spam, doc="spam spam spam")

klasa PropertyDocSub(PropertyDocBase):
    @PropertyDocBase.spam.getter
    def spam(self):
        """The decorator does nie use this doc string"""
        zwróć self._spam

klasa PropertySubNewGetter(BaseClass):
    @BaseClass.spam.getter
    def spam(self):
        """new docstring"""
        zwróć 5

klasa PropertyNewGetter(object):
    @property
    def spam(self):
        """original docstring"""
        zwróć 1
    @spam.getter
    def spam(self):
        """new docstring"""
        zwróć 8

klasa PropertyWritableDoc(object):

    @property
    def spam(self):
        """Eggs"""
        zwróć "eggs"

klasa PropertyTests(unittest.TestCase):
    def test_property_decorator_baseclass(self):
        # see #1620
        base = BaseClass()
        self.assertEqual(base.spam, 5)
        self.assertEqual(base._spam, 5)
        base.spam = 10
        self.assertEqual(base.spam, 10)
        self.assertEqual(base._spam, 10)
        delattr(base, "spam")
        self.assertPrawda(nie hasattr(base, "spam"))
        self.assertPrawda(nie hasattr(base, "_spam"))
        base.spam = 20
        self.assertEqual(base.spam, 20)
        self.assertEqual(base._spam, 20)

    def test_property_decorator_subclass(self):
        # see #1620
        sub = SubClass()
        self.assertRaises(PropertyGet, getattr, sub, "spam")
        self.assertRaises(PropertySet, setattr, sub, "spam", Nic)
        self.assertRaises(PropertyDel, delattr, sub, "spam")

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted przy -O2 oraz above")
    def test_property_decorator_subclass_doc(self):
        sub = SubClass()
        self.assertEqual(sub.__class__.spam.__doc__, "SubClass.getter")

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted przy -O2 oraz above")
    def test_property_decorator_baseclass_doc(self):
        base = BaseClass()
        self.assertEqual(base.__class__.spam.__doc__, "BaseClass.getter")

    def test_property_decorator_doc(self):
        base = PropertyDocBase()
        sub = PropertyDocSub()
        self.assertEqual(base.__class__.spam.__doc__, "spam spam spam")
        self.assertEqual(sub.__class__.spam.__doc__, "spam spam spam")

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted przy -O2 oraz above")
    def test_property_getter_doc_override(self):
        newgettersub = PropertySubNewGetter()
        self.assertEqual(newgettersub.spam, 5)
        self.assertEqual(newgettersub.__class__.spam.__doc__, "new docstring")
        newgetter = PropertyNewGetter()
        self.assertEqual(newgetter.spam, 8)
        self.assertEqual(newgetter.__class__.spam.__doc__, "new docstring")

    def test_property___isabstractmethod__descriptor(self):
        dla val w (Prawda, Nieprawda, [], [1], '', '1'):
            klasa C(object):
                def foo(self):
                    dalej
                foo.__isabstractmethod__ = val
                foo = property(foo)
            self.assertIs(C.foo.__isabstractmethod__, bool(val))

        # check that the property's __isabstractmethod__ descriptor does the
        # right thing when presented przy a value that fails truth testing:
        klasa NotBool(object):
            def __bool__(self):
                podnieś ValueError()
            __len__ = __bool__
        przy self.assertRaises(ValueError):
            klasa C(object):
                def foo(self):
                    dalej
                foo.__isabstractmethod__ = NotBool()
                foo = property(foo)
            C.foo.__isabstractmethod__

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted przy -O2 oraz above")
    def test_property_builtin_doc_writable(self):
        p = property(doc='basic')
        self.assertEqual(p.__doc__, 'basic')
        p.__doc__ = 'extended'
        self.assertEqual(p.__doc__, 'extended')

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted przy -O2 oraz above")
    def test_property_decorator_doc_writable(self):
        sub = PropertyWritableDoc()
        self.assertEqual(sub.__class__.spam.__doc__, 'Eggs')
        sub.__class__.spam.__doc__ = 'Spam'
        self.assertEqual(sub.__class__.spam.__doc__, 'Spam')

# Issue 5890: subclasses of property do nie preserve method __doc__ strings
klasa PropertySub(property):
    """This jest a subclass of property"""

klasa PropertySubSlots(property):
    """This jest a subclass of property that defines __slots__"""
    __slots__ = ()

klasa PropertySubclassTests(unittest.TestCase):

    def test_slots_docstring_copy_exception(self):
        spróbuj:
            klasa Foo(object):
                @PropertySubSlots
                def spam(self):
                    """Trying to copy this docstring will podnieś an exception"""
                    zwróć 1
        wyjąwszy AttributeError:
            dalej
        inaczej:
            podnieś Exception("AttributeError nie podnieśd")

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted przy -O2 oraz above")
    def test_docstring_copy(self):
        klasa Foo(object):
            @PropertySub
            def spam(self):
                """spam wrapped w property subclass"""
                zwróć 1
        self.assertEqual(
            Foo.spam.__doc__,
            "spam wrapped w property subclass")

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted przy -O2 oraz above")
    def test_property_setter_copies_getter_docstring(self):
        klasa Foo(object):
            def __init__(self): self._spam = 1
            @PropertySub
            def spam(self):
                """spam wrapped w property subclass"""
                zwróć self._spam
            @spam.setter
            def spam(self, value):
                """this docstring jest ignored"""
                self._spam = value
        foo = Foo()
        self.assertEqual(foo.spam, 1)
        foo.spam = 2
        self.assertEqual(foo.spam, 2)
        self.assertEqual(
            Foo.spam.__doc__,
            "spam wrapped w property subclass")
        klasa FooSub(Foo):
            @Foo.spam.setter
            def spam(self, value):
                """another ignored docstring"""
                self._spam = 'eggs'
        foosub = FooSub()
        self.assertEqual(foosub.spam, 1)
        foosub.spam = 7
        self.assertEqual(foosub.spam, 'eggs')
        self.assertEqual(
            FooSub.spam.__doc__,
            "spam wrapped w property subclass")

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted przy -O2 oraz above")
    def test_property_new_getter_new_docstring(self):

        klasa Foo(object):
            @PropertySub
            def spam(self):
                """a docstring"""
                zwróć 1
            @spam.getter
            def spam(self):
                """a new docstring"""
                zwróć 2
        self.assertEqual(Foo.spam.__doc__, "a new docstring")
        klasa FooBase(object):
            @PropertySub
            def spam(self):
                """a docstring"""
                zwróć 1
        klasa Foo2(FooBase):
            @FooBase.spam.getter
            def spam(self):
                """a new docstring"""
                zwróć 2
        self.assertEqual(Foo.spam.__doc__, "a new docstring")



jeżeli __name__ == '__main__':
    unittest.main()
