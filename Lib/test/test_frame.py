zaimportuj gc
zaimportuj sys
zaimportuj types
zaimportuj unittest
zaimportuj weakref

z test zaimportuj support


klasa ClearTest(unittest.TestCase):
    """
    Tests dla frame.clear().
    """

    def inner(self, x=5, **kwargs):
        1/0

    def outer(self, **kwargs):
        spróbuj:
            self.inner(**kwargs)
        wyjąwszy ZeroDivisionError jako e:
            exc = e
        zwróć exc

    def clear_traceback_frames(self, tb):
        """
        Clear all frames w a traceback.
        """
        dopóki tb jest nie Nic:
            tb.tb_frame.clear()
            tb = tb.tb_next

    def test_clear_locals(self):
        klasa C:
            dalej
        c = C()
        wr = weakref.ref(c)
        exc = self.outer(c=c)
        usuń c
        support.gc_collect()
        # A reference to c jest held through the frames
        self.assertIsNot(Nic, wr())
        self.clear_traceback_frames(exc.__traceback__)
        support.gc_collect()
        # The reference was released by .clear()
        self.assertIs(Nic, wr())

    def test_clear_generator(self):
        endly = Nieprawda
        def g():
            nonlocal endly
            spróbuj:
                uzyskaj
                inner()
            w_końcu:
                endly = Prawda
        gen = g()
        next(gen)
        self.assertNieprawda(endly)
        # Clearing the frame closes the generator
        gen.gi_frame.clear()
        self.assertPrawda(endly)

    def test_clear_executing(self):
        # Attempting to clear an executing frame jest forbidden.
        spróbuj:
            1/0
        wyjąwszy ZeroDivisionError jako e:
            f = e.__traceback__.tb_frame
        przy self.assertRaises(RuntimeError):
            f.clear()
        przy self.assertRaises(RuntimeError):
            f.f_back.clear()

    def test_clear_executing_generator(self):
        # Attempting to clear an executing generator frame jest forbidden.
        endly = Nieprawda
        def g():
            nonlocal endly
            spróbuj:
                1/0
            wyjąwszy ZeroDivisionError jako e:
                f = e.__traceback__.tb_frame
                przy self.assertRaises(RuntimeError):
                    f.clear()
                przy self.assertRaises(RuntimeError):
                    f.f_back.clear()
                uzyskaj f
            w_końcu:
                endly = Prawda
        gen = g()
        f = next(gen)
        self.assertNieprawda(endly)
        # Clearing the frame closes the generator
        f.clear()
        self.assertPrawda(endly)

    @support.cpython_only
    def test_clear_refcycles(self):
        # .clear() doesn't leave any refcycle behind
        przy support.disable_gc():
            klasa C:
                dalej
            c = C()
            wr = weakref.ref(c)
            exc = self.outer(c=c)
            usuń c
            self.assertIsNot(Nic, wr())
            self.clear_traceback_frames(exc.__traceback__)
            self.assertIs(Nic, wr())


klasa FrameLocalsTest(unittest.TestCase):
    """
    Tests dla the .f_locals attribute.
    """

    def make_frames(self):
        def outer():
            x = 5
            y = 6
            def inner():
                z = x + 2
                1/0
                t = 9
            zwróć inner()
        spróbuj:
            outer()
        wyjąwszy ZeroDivisionError jako e:
            tb = e.__traceback__
            frames = []
            dopóki tb:
                frames.append(tb.tb_frame)
                tb = tb.tb_next
        zwróć frames

    def test_locals(self):
        f, outer, inner = self.make_frames()
        outer_locals = outer.f_locals
        self.assertIsInstance(outer_locals.pop('inner'), types.FunctionType)
        self.assertEqual(outer_locals, {'x': 5, 'y': 6})
        inner_locals = inner.f_locals
        self.assertEqual(inner_locals, {'x': 5, 'z': 7})

    def test_clear_locals(self):
        # Test f_locals after clear() (issue #21897)
        f, outer, inner = self.make_frames()
        outer.clear()
        inner.clear()
        self.assertEqual(outer.f_locals, {})
        self.assertEqual(inner.f_locals, {})

    def test_locals_clear_locals(self):
        # Test f_locals before oraz after clear() (to exercise caching)
        f, outer, inner = self.make_frames()
        outer.f_locals
        inner.f_locals
        outer.clear()
        inner.clear()
        self.assertEqual(outer.f_locals, {})
        self.assertEqual(inner.f_locals, {})


jeżeli __name__ == "__main__":
    unittest.main()
