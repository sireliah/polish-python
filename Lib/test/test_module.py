# Test the module type
zaimportuj unittest
zaimportuj weakref
z test.support zaimportuj gc_collect
z test.support.script_helper zaimportuj assert_python_ok

zaimportuj sys
ModuleType = type(sys)

klasa FullLoader:
    @classmethod
    def module_repr(cls, m):
        zwróć "<module '{}' (crafted)>".format(m.__name__)

klasa BareLoader:
    dalej


klasa ModuleTests(unittest.TestCase):
    def test_uninitialized(self):
        # An uninitialized module has no __dict__ albo __name__,
        # oraz __doc__ jest Nic
        foo = ModuleType.__new__(ModuleType)
        self.assertPrawda(foo.__dict__ jest Nic)
        self.assertRaises(SystemError, dir, foo)
        spróbuj:
            s = foo.__name__
            self.fail("__name__ = %s" % repr(s))
        wyjąwszy AttributeError:
            dalej
        self.assertEqual(foo.__doc__, ModuleType.__doc__)

    def test_unintialized_missing_getattr(self):
        # Issue 8297
        # test the text w the AttributeError of an uninitialized module
        foo = ModuleType.__new__(ModuleType)
        self.assertRaisesRegex(
                AttributeError, "module has no attribute 'not_here'",
                getattr, foo, "not_here")

    def test_missing_getattr(self):
        # Issue 8297
        # test the text w the AttributeError
        foo = ModuleType("foo")
        self.assertRaisesRegex(
                AttributeError, "module 'foo' has no attribute 'not_here'",
                getattr, foo, "not_here")

    def test_no_docstring(self):
        # Regularly initialized module, no docstring
        foo = ModuleType("foo")
        self.assertEqual(foo.__name__, "foo")
        self.assertEqual(foo.__doc__, Nic)
        self.assertIs(foo.__loader__, Nic)
        self.assertIs(foo.__package__, Nic)
        self.assertIs(foo.__spec__, Nic)
        self.assertEqual(foo.__dict__, {"__name__": "foo", "__doc__": Nic,
                                        "__loader__": Nic, "__package__": Nic,
                                        "__spec__": Nic})

    def test_ascii_docstring(self):
        # ASCII docstring
        foo = ModuleType("foo", "foodoc")
        self.assertEqual(foo.__name__, "foo")
        self.assertEqual(foo.__doc__, "foodoc")
        self.assertEqual(foo.__dict__,
                         {"__name__": "foo", "__doc__": "foodoc",
                          "__loader__": Nic, "__package__": Nic,
                          "__spec__": Nic})

    def test_unicode_docstring(self):
        # Unicode docstring
        foo = ModuleType("foo", "foodoc\u1234")
        self.assertEqual(foo.__name__, "foo")
        self.assertEqual(foo.__doc__, "foodoc\u1234")
        self.assertEqual(foo.__dict__,
                         {"__name__": "foo", "__doc__": "foodoc\u1234",
                          "__loader__": Nic, "__package__": Nic,
                          "__spec__": Nic})

    def test_reinit(self):
        # Reinitialization should nie replace the __dict__
        foo = ModuleType("foo", "foodoc\u1234")
        foo.bar = 42
        d = foo.__dict__
        foo.__init__("foo", "foodoc")
        self.assertEqual(foo.__name__, "foo")
        self.assertEqual(foo.__doc__, "foodoc")
        self.assertEqual(foo.bar, 42)
        self.assertEqual(foo.__dict__,
              {"__name__": "foo", "__doc__": "foodoc", "bar": 42,
               "__loader__": Nic, "__package__": Nic, "__spec__": Nic})
        self.assertPrawda(foo.__dict__ jest d)

    def test_dont_clear_dict(self):
        # See issue 7140.
        def f():
            foo = ModuleType("foo")
            foo.bar = 4
            zwróć foo
        gc_collect()
        self.assertEqual(f().__dict__["bar"], 4)

    def test_clear_dict_in_ref_cycle(self):
        destroyed = []
        m = ModuleType("foo")
        m.destroyed = destroyed
        s = """class A:
    def __init__(self, l):
        self.l = l
    def __del__(self):
        self.l.append(1)
a = A(destroyed)"""
        exec(s, m.__dict__)
        usuń m
        gc_collect()
        self.assertEqual(destroyed, [1])

    def test_weakref(self):
        m = ModuleType("foo")
        wr = weakref.ref(m)
        self.assertIs(wr(), m)
        usuń m
        gc_collect()
        self.assertIs(wr(), Nic)

    def test_module_repr_minimal(self):
        # reprs when modules have no __file__, __name__, albo __loader__
        m = ModuleType('foo')
        usuń m.__name__
        self.assertEqual(repr(m), "<module '?'>")

    def test_module_repr_with_name(self):
        m = ModuleType('foo')
        self.assertEqual(repr(m), "<module 'foo'>")

    def test_module_repr_with_name_and_filename(self):
        m = ModuleType('foo')
        m.__file__ = '/tmp/foo.py'
        self.assertEqual(repr(m), "<module 'foo' z '/tmp/foo.py'>")

    def test_module_repr_with_filename_only(self):
        m = ModuleType('foo')
        usuń m.__name__
        m.__file__ = '/tmp/foo.py'
        self.assertEqual(repr(m), "<module '?' z '/tmp/foo.py'>")

    def test_module_repr_with_loader_as_Nic(self):
        m = ModuleType('foo')
        assert m.__loader__ jest Nic
        self.assertEqual(repr(m), "<module 'foo'>")

    def test_module_repr_with_bare_loader_but_no_name(self):
        m = ModuleType('foo')
        usuń m.__name__
        # Yes, a klasa nie an instance.
        m.__loader__ = BareLoader
        loader_repr = repr(BareLoader)
        self.assertEqual(
            repr(m), "<module '?' ({})>".format(loader_repr))

    def test_module_repr_with_full_loader_but_no_name(self):
        # m.__loader__.module_repr() will fail because the module has no
        # m.__name__.  This exception will get suppressed oraz instead the
        # loader's repr will be used.
        m = ModuleType('foo')
        usuń m.__name__
        # Yes, a klasa nie an instance.
        m.__loader__ = FullLoader
        loader_repr = repr(FullLoader)
        self.assertEqual(
            repr(m), "<module '?' ({})>".format(loader_repr))

    def test_module_repr_with_bare_loader(self):
        m = ModuleType('foo')
        # Yes, a klasa nie an instance.
        m.__loader__ = BareLoader
        module_repr = repr(BareLoader)
        self.assertEqual(
            repr(m), "<module 'foo' ({})>".format(module_repr))

    def test_module_repr_with_full_loader(self):
        m = ModuleType('foo')
        # Yes, a klasa nie an instance.
        m.__loader__ = FullLoader
        self.assertEqual(
            repr(m), "<module 'foo' (crafted)>")

    def test_module_repr_with_bare_loader_and_filename(self):
        # Because the loader has no module_repr(), use the file name.
        m = ModuleType('foo')
        # Yes, a klasa nie an instance.
        m.__loader__ = BareLoader
        m.__file__ = '/tmp/foo.py'
        self.assertEqual(repr(m), "<module 'foo' z '/tmp/foo.py'>")

    def test_module_repr_with_full_loader_and_filename(self):
        # Even though the module has an __file__, use __loader__.module_repr()
        m = ModuleType('foo')
        # Yes, a klasa nie an instance.
        m.__loader__ = FullLoader
        m.__file__ = '/tmp/foo.py'
        self.assertEqual(repr(m), "<module 'foo' (crafted)>")

    def test_module_repr_builtin(self):
        self.assertEqual(repr(sys), "<module 'sys' (built-in)>")

    def test_module_repr_source(self):
        r = repr(unittest)
        starts_przy = "<module 'unittest' z '"
        ends_przy = "__init__.py'>"
        self.assertEqual(r[:len(starts_with)], starts_with,
                         '{!r} does nie start przy {!r}'.format(r, starts_with))
        self.assertEqual(r[-len(ends_with):], ends_with,
                         '{!r} does nie end przy {!r}'.format(r, ends_with))

    def test_module_finalization_at_shutdown(self):
        # Module globals oraz builtins should still be available during shutdown
        rc, out, err = assert_python_ok("-c", "z test zaimportuj final_a")
        self.assertNieprawda(err)
        lines = out.splitlines()
        self.assertEqual(set(lines), {
            b"x = a",
            b"x = b",
            b"final_a.x = a",
            b"final_b.x = b",
            b"len = len",
            b"shutil.rmtree = rmtree"})

    def test_descriptor_errors_propogate(self):
        klasa Descr:
            def __get__(self, o, t):
                podnieś RuntimeError
        klasa M(ModuleType):
            melon = Descr()
        self.assertRaises(RuntimeError, getattr, M("mymod"), "melon")

    # frozen oraz namespace module reprs are tested w importlib.


jeżeli __name__ == '__main__':
    unittest.main()
