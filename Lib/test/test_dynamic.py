# Test the most dynamic corner cases of Python's runtime semantics.

zaimportuj builtins
zaimportuj contextlib
zaimportuj unittest

z test.support zaimportuj swap_item, swap_attr


klasa RebindBuiltinsTests(unittest.TestCase):

    """Test all the ways that we can change/shadow globals/builtins."""

    def configure_func(self, func, *args):
        """Perform TestCase-specific configuration on a function before testing.

        By default, this does nothing. Example usage: spinning a function so
        that a JIT will optimize it. Subclasses should override this jako needed.

        Args:
            func: function to configure.
            *args: any arguments that should be dalejed to func, jeżeli calling it.

        Returns:
            Nothing. Work will be performed on func in-place.
        """
        dalej

    def test_globals_shadow_builtins(self):
        # Modify globals() to shadow an entry w builtins.
        def foo():
            zwróć len([1, 2, 3])
        self.configure_func(foo)

        self.assertEqual(foo(), 3)
        przy swap_item(globals(), "len", lambda x: 7):
            self.assertEqual(foo(), 7)

    def test_modify_builtins(self):
        # Modify the builtins module directly.
        def foo():
            zwróć len([1, 2, 3])
        self.configure_func(foo)

        self.assertEqual(foo(), 3)
        przy swap_attr(builtins, "len", lambda x: 7):
            self.assertEqual(foo(), 7)

    def test_modify_builtins_while_generator_active(self):
        # Modify the builtins out z under a live generator.
        def foo():
            x = range(3)
            uzyskaj len(x)
            uzyskaj len(x)
        self.configure_func(foo)

        g = foo()
        self.assertEqual(next(g), 3)
        przy swap_attr(builtins, "len", lambda x: 7):
            self.assertEqual(next(g), 7)

    def test_modify_builtins_from_leaf_function(self):
        # Verify that modifications made by leaf functions percolate up the
        # callstack.
        przy swap_attr(builtins, "len", len):
            def bar():
                builtins.len = lambda x: 4

            def foo(modifier):
                l = []
                l.append(len(range(7)))
                modifier()
                l.append(len(range(7)))
                zwróć l
            self.configure_func(foo, lambda: Nic)

            self.assertEqual(foo(bar), [7, 4])

    def test_cannot_change_globals_or_builtins_with_eval(self):
        def foo():
            zwróć len([1, 2, 3])
        self.configure_func(foo)

        # Note that this *doesn't* change the definition of len() seen by foo().
        builtins_dict = {"len": lambda x: 7}
        globals_dict = {"foo": foo, "__builtins__": builtins_dict,
                        "len": lambda x: 8}
        self.assertEqual(eval("foo()", globals_dict), 3)

        self.assertEqual(eval("foo()", {"foo": foo}), 3)

    def test_cannot_change_globals_or_builtins_with_exec(self):
        def foo():
            zwróć len([1, 2, 3])
        self.configure_func(foo)

        globals_dict = {"foo": foo}
        exec("x = foo()", globals_dict)
        self.assertEqual(globals_dict["x"], 3)

        # Note that this *doesn't* change the definition of len() seen by foo().
        builtins_dict = {"len": lambda x: 7}
        globals_dict = {"foo": foo, "__builtins__": builtins_dict,
                        "len": lambda x: 8}

        exec("x = foo()", globals_dict)
        self.assertEqual(globals_dict["x"], 3)

    def test_cannot_replace_builtins_dict_while_active(self):
        def foo():
            x = range(3)
            uzyskaj len(x)
            uzyskaj len(x)
        self.configure_func(foo)

        g = foo()
        self.assertEqual(next(g), 3)
        przy swap_item(globals(), "__builtins__", {"len": lambda x: 7}):
            self.assertEqual(next(g), 3)

    def test_cannot_replace_builtins_dict_between_calls(self):
        def foo():
            zwróć len([1, 2, 3])
        self.configure_func(foo)

        self.assertEqual(foo(), 3)
        przy swap_item(globals(), "__builtins__", {"len": lambda x: 7}):
            self.assertEqual(foo(), 3)

    def test_eval_gives_lambda_custom_globals(self):
        globals_dict = {"len": lambda x: 7}
        foo = eval("lambda: len([])", globals_dict)
        self.configure_func(foo)

        self.assertEqual(foo(), 7)


jeżeli __name__ == "__main__":
    unittest.main()
