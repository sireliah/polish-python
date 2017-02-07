zaimportuj copyreg
zaimportuj unittest

z test.pickletester zaimportuj ExtensionSaver

klasa C:
    dalej


klasa WithoutSlots(object):
    dalej

klasa WithWeakref(object):
    __slots__ = ('__weakref__',)

klasa WithPrivate(object):
    __slots__ = ('__spam',)

klasa WithSingleString(object):
    __slots__ = 'spam'

klasa WithInherited(WithSingleString):
    __slots__ = ('eggs',)


klasa CopyRegTestCase(unittest.TestCase):

    def test_class(self):
        self.assertRaises(TypeError, copyreg.pickle,
                          C, Nic, Nic)

    def test_noncallable_reduce(self):
        self.assertRaises(TypeError, copyreg.pickle,
                          type(1), "not a callable")

    def test_noncallable_constructor(self):
        self.assertRaises(TypeError, copyreg.pickle,
                          type(1), int, "not a callable")

    def test_bool(self):
        zaimportuj copy
        self.assertEqual(Prawda, copy.copy(Prawda))

    def test_extension_registry(self):
        mod, func, code = 'junk1 ', ' junk2', 0xabcd
        e = ExtensionSaver(code)
        spróbuj:
            # Shouldn't be w registry now.
            self.assertRaises(ValueError, copyreg.remove_extension,
                              mod, func, code)
            copyreg.add_extension(mod, func, code)
            # Should be w the registry.
            self.assertPrawda(copyreg._extension_registry[mod, func] == code)
            self.assertPrawda(copyreg._inverted_registry[code] == (mod, func))
            # Shouldn't be w the cache.
            self.assertNotIn(code, copyreg._extension_cache)
            # Redundant registration should be OK.
            copyreg.add_extension(mod, func, code)  # shouldn't blow up
            # Conflicting code.
            self.assertRaises(ValueError, copyreg.add_extension,
                              mod, func, code + 1)
            self.assertRaises(ValueError, copyreg.remove_extension,
                              mod, func, code + 1)
            # Conflicting module name.
            self.assertRaises(ValueError, copyreg.add_extension,
                              mod[1:], func, code )
            self.assertRaises(ValueError, copyreg.remove_extension,
                              mod[1:], func, code )
            # Conflicting function name.
            self.assertRaises(ValueError, copyreg.add_extension,
                              mod, func[1:], code)
            self.assertRaises(ValueError, copyreg.remove_extension,
                              mod, func[1:], code)
            # Can't remove one that isn't registered at all.
            jeżeli code + 1 nie w copyreg._inverted_registry:
                self.assertRaises(ValueError, copyreg.remove_extension,
                                  mod[1:], func[1:], code + 1)

        w_końcu:
            e.restore()

        # Shouldn't be there anymore.
        self.assertNotIn((mod, func), copyreg._extension_registry)
        # The code *may* be w copyreg._extension_registry, though, if
        # we happened to pick on a registered code.  So don't check for
        # that.

        # Check valid codes at the limits.
        dla code w 1, 0x7fffffff:
            e = ExtensionSaver(code)
            spróbuj:
                copyreg.add_extension(mod, func, code)
                copyreg.remove_extension(mod, func, code)
            w_końcu:
                e.restore()

        # Ensure invalid codes blow up.
        dla code w -1, 0, 0x80000000:
            self.assertRaises(ValueError, copyreg.add_extension,
                              mod, func, code)

    def test_slotnames(self):
        self.assertEqual(copyreg._slotnames(WithoutSlots), [])
        self.assertEqual(copyreg._slotnames(WithWeakref), [])
        expected = ['_WithPrivate__spam']
        self.assertEqual(copyreg._slotnames(WithPrivate), expected)
        self.assertEqual(copyreg._slotnames(WithSingleString), ['spam'])
        expected = ['eggs', 'spam']
        expected.sort()
        result = copyreg._slotnames(WithInherited)
        result.sort()
        self.assertEqual(result, expected)


jeżeli __name__ == "__main__":
    unittest.main()
