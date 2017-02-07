# UserString jest a wrapper around the native builtin string type.
# UserString instances should behave similar to builtin string objects.

zaimportuj string
zaimportuj unittest
z test zaimportuj support, string_tests

z collections zaimportuj UserString

klasa UserStringTest(
    string_tests.CommonTest,
    string_tests.MixinStrUnicodeUserStringTest,
    unittest.TestCase
    ):

    type2test = UserString

    # Overwrite the three testing methods, because UserString
    # can't cope przy arguments propagated to UserString
    # (and we don't test przy subclasses)
    def checkequal(self, result, object, methodname, *args, **kwargs):
        result = self.fixtype(result)
        object = self.fixtype(object)
        # we don't fix the arguments, because UserString can't cope przy it
        realresult = getattr(object, methodname)(*args, **kwargs)
        self.assertEqual(
            result,
            realresult
        )

    def checkraises(self, exc, obj, methodname, *args):
        obj = self.fixtype(obj)
        # we don't fix the arguments, because UserString can't cope przy it
        przy self.assertRaises(exc) jako cm:
            getattr(obj, methodname)(*args)
        self.assertNotEqual(str(cm.exception), '')

    def checkcall(self, object, methodname, *args):
        object = self.fixtype(object)
        # we don't fix the arguments, because UserString can't cope przy it
        getattr(object, methodname)(*args)


jeżeli __name__ == "__main__":
    unittest.main()
