""" Test suite dla the fixer modules """

# Python imports
zaimportuj os
zaimportuj unittest
z itertools zaimportuj chain
z operator zaimportuj itemgetter

# Local imports
z lib2to3 zaimportuj pygram, pytree, refactor, fixer_util
z lib2to3.tests zaimportuj support


klasa FixerTestCase(support.TestCase):

    # Other test cases can subclass this klasa oraz replace "fixer_pkg" with
    # their own.
    def setUp(self, fix_list=Nic, fixer_pkg="lib2to3", options=Nic):
        jeżeli fix_list jest Nic:
            fix_list = [self.fixer]
        self.refactor = support.get_refactorer(fixer_pkg, fix_list, options)
        self.fixer_log = []
        self.filename = "<string>"

        dla fixer w chain(self.refactor.pre_order,
                           self.refactor.post_order):
            fixer.log = self.fixer_log

    def _check(self, before, after):
        before = support.reformat(before)
        after = support.reformat(after)
        tree = self.refactor.refactor_string(before, self.filename)
        self.assertEqual(after, str(tree))
        zwróć tree

    def check(self, before, after, ignore_warnings=Nieprawda):
        tree = self._check(before, after)
        self.assertPrawda(tree.was_changed)
        jeżeli nie ignore_warnings:
            self.assertEqual(self.fixer_log, [])

    def warns(self, before, after, message, unchanged=Nieprawda):
        tree = self._check(before, after)
        self.assertIn(message, "".join(self.fixer_log))
        jeżeli nie unchanged:
            self.assertPrawda(tree.was_changed)

    def warns_unchanged(self, before, message):
        self.warns(before, before, message, unchanged=Prawda)

    def unchanged(self, before, ignore_warnings=Nieprawda):
        self._check(before, before)
        jeżeli nie ignore_warnings:
            self.assertEqual(self.fixer_log, [])

    def assert_runs_after(self, *names):
        fixes = [self.fixer]
        fixes.extend(names)
        r = support.get_refactorer("lib2to3", fixes)
        (pre, post) = r.get_fixers()
        n = "fix_" + self.fixer
        jeżeli post oraz post[-1].__class__.__module__.endswith(n):
            # We're the last fixer to run
            zwróć
        jeżeli pre oraz pre[-1].__class__.__module__.endswith(n) oraz nie post:
            # We're the last w pre oraz post jest empty
            zwróć
        self.fail("Fixer run order (%s) jest incorrect; %s should be last."\
               %(", ".join([x.__class__.__module__ dla x w (pre+post)]), n))

klasa Test_ne(FixerTestCase):
    fixer = "ne"

    def test_basic(self):
        b = """jeżeli x <> y:
            dalej"""

        a = """jeżeli x != y:
            dalej"""
        self.check(b, a)

    def test_no_spaces(self):
        b = """jeżeli x<>y:
            dalej"""

        a = """jeżeli x!=y:
            dalej"""
        self.check(b, a)

    def test_chained(self):
        b = """jeżeli x<>y<>z:
            dalej"""

        a = """jeżeli x!=y!=z:
            dalej"""
        self.check(b, a)

klasa Test_has_key(FixerTestCase):
    fixer = "has_key"

    def test_1(self):
        b = """x = d.has_key("x") albo d.has_key("y")"""
        a = """x = "x" w d albo "y" w d"""
        self.check(b, a)

    def test_2(self):
        b = """x = a.b.c.d.has_key("x") ** 3"""
        a = """x = ("x" w a.b.c.d) ** 3"""
        self.check(b, a)

    def test_3(self):
        b = """x = a.b.has_key(1 + 2).__repr__()"""
        a = """x = (1 + 2 w a.b).__repr__()"""
        self.check(b, a)

    def test_4(self):
        b = """x = a.b.has_key(1 + 2).__repr__() ** -3 ** 4"""
        a = """x = (1 + 2 w a.b).__repr__() ** -3 ** 4"""
        self.check(b, a)

    def test_5(self):
        b = """x = a.has_key(f albo g)"""
        a = """x = (f albo g) w a"""
        self.check(b, a)

    def test_6(self):
        b = """x = a + b.has_key(c)"""
        a = """x = a + (c w b)"""
        self.check(b, a)

    def test_7(self):
        b = """x = a.has_key(lambda: 12)"""
        a = """x = (lambda: 12) w a"""
        self.check(b, a)

    def test_8(self):
        b = """x = a.has_key(a dla a w b)"""
        a = """x = (a dla a w b) w a"""
        self.check(b, a)

    def test_9(self):
        b = """jeżeli nie a.has_key(b): dalej"""
        a = """jeżeli b nie w a: dalej"""
        self.check(b, a)

    def test_10(self):
        b = """jeżeli nie a.has_key(b).__repr__(): dalej"""
        a = """jeżeli nie (b w a).__repr__(): dalej"""
        self.check(b, a)

    def test_11(self):
        b = """jeżeli nie a.has_key(b) ** 2: dalej"""
        a = """jeżeli nie (b w a) ** 2: dalej"""
        self.check(b, a)

klasa Test_apply(FixerTestCase):
    fixer = "apply"

    def test_1(self):
        b = """x = apply(f, g + h)"""
        a = """x = f(*g + h)"""
        self.check(b, a)

    def test_2(self):
        b = """y = apply(f, g, h)"""
        a = """y = f(*g, **h)"""
        self.check(b, a)

    def test_3(self):
        b = """z = apply(fs[0], g albo h, h albo g)"""
        a = """z = fs[0](*g albo h, **h albo g)"""
        self.check(b, a)

    def test_4(self):
        b = """apply(f, (x, y) + t)"""
        a = """f(*(x, y) + t)"""
        self.check(b, a)

    def test_5(self):
        b = """apply(f, args,)"""
        a = """f(*args)"""
        self.check(b, a)

    def test_6(self):
        b = """apply(f, args, kwds,)"""
        a = """f(*args, **kwds)"""
        self.check(b, a)

    # Test that complex functions are parenthesized

    def test_complex_1(self):
        b = """x = apply(f+g, args)"""
        a = """x = (f+g)(*args)"""
        self.check(b, a)

    def test_complex_2(self):
        b = """x = apply(f*g, args)"""
        a = """x = (f*g)(*args)"""
        self.check(b, a)

    def test_complex_3(self):
        b = """x = apply(f**g, args)"""
        a = """x = (f**g)(*args)"""
        self.check(b, a)

    # But dotted names etc. nie

    def test_dotted_name(self):
        b = """x = apply(f.g, args)"""
        a = """x = f.g(*args)"""
        self.check(b, a)

    def test_subscript(self):
        b = """x = apply(f[x], args)"""
        a = """x = f[x](*args)"""
        self.check(b, a)

    def test_call(self):
        b = """x = apply(f(), args)"""
        a = """x = f()(*args)"""
        self.check(b, a)

    # Extreme case
    def test_extreme(self):
        b = """x = apply(a.b.c.d.e.f, args, kwds)"""
        a = """x = a.b.c.d.e.f(*args, **kwds)"""
        self.check(b, a)

    # XXX Comments w weird places still get lost
    def test_weird_comments(self):
        b = """apply(   # foo
          f, # bar
          args)"""
        a = """f(*args)"""
        self.check(b, a)

    # These should *not* be touched

    def test_unchanged_1(self):
        s = """apply()"""
        self.unchanged(s)

    def test_unchanged_2(self):
        s = """apply(f)"""
        self.unchanged(s)

    def test_unchanged_3(self):
        s = """apply(f,)"""
        self.unchanged(s)

    def test_unchanged_4(self):
        s = """apply(f, args, kwds, extras)"""
        self.unchanged(s)

    def test_unchanged_5(self):
        s = """apply(f, *args, **kwds)"""
        self.unchanged(s)

    def test_unchanged_6(self):
        s = """apply(f, *args)"""
        self.unchanged(s)

    def test_unchanged_7(self):
        s = """apply(func=f, args=args, kwds=kwds)"""
        self.unchanged(s)

    def test_unchanged_8(self):
        s = """apply(f, args=args, kwds=kwds)"""
        self.unchanged(s)

    def test_unchanged_9(self):
        s = """apply(f, args, kwds=kwds)"""
        self.unchanged(s)

    def test_space_1(self):
        a = """apply(  f,  args,   kwds)"""
        b = """f(*args, **kwds)"""
        self.check(a, b)

    def test_space_2(self):
        a = """apply(  f  ,args,kwds   )"""
        b = """f(*args, **kwds)"""
        self.check(a, b)

klasa Test_reload(FixerTestCase):
    fixer = "reload"

    def test(self):
        b = """reload(a)"""
        a = """zaimportuj imp\nimp.reload(a)"""
        self.check(b, a)

    def test_comment(self):
        b = """reload( a ) # comment"""
        a = """zaimportuj imp\nimp.reload( a ) # comment"""
        self.check(b, a)

        # PEP 8 comments
        b = """reload( a )  # comment"""
        a = """zaimportuj imp\nimp.reload( a )  # comment"""
        self.check(b, a)

    def test_space(self):
        b = """reload( a )"""
        a = """zaimportuj imp\nimp.reload( a )"""
        self.check(b, a)

        b = """reload( a)"""
        a = """zaimportuj imp\nimp.reload( a)"""
        self.check(b, a)

        b = """reload(a )"""
        a = """zaimportuj imp\nimp.reload(a )"""
        self.check(b, a)

    def test_unchanged(self):
        s = """reload(a=1)"""
        self.unchanged(s)

        s = """reload(f, g)"""
        self.unchanged(s)

        s = """reload(f, *h)"""
        self.unchanged(s)

        s = """reload(f, *h, **i)"""
        self.unchanged(s)

        s = """reload(f, **i)"""
        self.unchanged(s)

        s = """reload(*h, **i)"""
        self.unchanged(s)

        s = """reload(*h)"""
        self.unchanged(s)

        s = """reload(**i)"""
        self.unchanged(s)

        s = """reload()"""
        self.unchanged(s)

klasa Test_intern(FixerTestCase):
    fixer = "intern"

    def test_prefix_preservation(self):
        b = """x =   intern(  a  )"""
        a = """zaimportuj sys\nx =   sys.intern(  a  )"""
        self.check(b, a)

        b = """y = intern("b" # test
              )"""
        a = """zaimportuj sys\ny = sys.intern("b" # test
              )"""
        self.check(b, a)

        b = """z = intern(a+b+c.d,   )"""
        a = """zaimportuj sys\nz = sys.intern(a+b+c.d,   )"""
        self.check(b, a)

    def test(self):
        b = """x = intern(a)"""
        a = """zaimportuj sys\nx = sys.intern(a)"""
        self.check(b, a)

        b = """z = intern(a+b+c.d,)"""
        a = """zaimportuj sys\nz = sys.intern(a+b+c.d,)"""
        self.check(b, a)

        b = """intern("y%s" % 5).replace("y", "")"""
        a = """zaimportuj sys\nsys.intern("y%s" % 5).replace("y", "")"""
        self.check(b, a)

    # These should nie be refactored

    def test_unchanged(self):
        s = """intern(a=1)"""
        self.unchanged(s)

        s = """intern(f, g)"""
        self.unchanged(s)

        s = """intern(*h)"""
        self.unchanged(s)

        s = """intern(**i)"""
        self.unchanged(s)

        s = """intern()"""
        self.unchanged(s)

klasa Test_reduce(FixerTestCase):
    fixer = "reduce"

    def test_simple_call(self):
        b = "reduce(a, b, c)"
        a = "z functools zaimportuj reduce\nreduce(a, b, c)"
        self.check(b, a)

    def test_bug_7253(self):
        # fix_tuple_params was being bad oraz orphaning nodes w the tree.
        b = "def x(arg): reduce(sum, [])"
        a = "z functools zaimportuj reduce\ndef x(arg): reduce(sum, [])"
        self.check(b, a)

    def test_call_with_lambda(self):
        b = "reduce(lambda x, y: x + y, seq)"
        a = "z functools zaimportuj reduce\nreduce(lambda x, y: x + y, seq)"
        self.check(b, a)

    def test_unchanged(self):
        s = "reduce(a)"
        self.unchanged(s)

        s = "reduce(a, b=42)"
        self.unchanged(s)

        s = "reduce(a, b, c, d)"
        self.unchanged(s)

        s = "reduce(**c)"
        self.unchanged(s)

        s = "reduce()"
        self.unchanged(s)

klasa Test_print(FixerTestCase):
    fixer = "print"

    def test_prefix_preservation(self):
        b = """print 1,   1+1,   1+1+1"""
        a = """print(1,   1+1,   1+1+1)"""
        self.check(b, a)

    def test_idempotency(self):
        s = """print()"""
        self.unchanged(s)

        s = """print('')"""
        self.unchanged(s)

    def test_idempotency_print_as_function(self):
        self.refactor.driver.grammar = pygram.python_grammar_no_print_statement
        s = """print(1, 1+1, 1+1+1)"""
        self.unchanged(s)

        s = """print()"""
        self.unchanged(s)

        s = """print('')"""
        self.unchanged(s)

    def test_1(self):
        b = """print 1, 1+1, 1+1+1"""
        a = """print(1, 1+1, 1+1+1)"""
        self.check(b, a)

    def test_2(self):
        b = """print 1, 2"""
        a = """print(1, 2)"""
        self.check(b, a)

    def test_3(self):
        b = """print"""
        a = """print()"""
        self.check(b, a)

    def test_4(self):
        # z bug 3000
        b = """print whatever; print"""
        a = """print(whatever); print()"""
        self.check(b, a)

    def test_5(self):
        b = """print; print whatever;"""
        a = """print(); print(whatever);"""
        self.check(b, a)

    def test_tuple(self):
        b = """print (a, b, c)"""
        a = """print((a, b, c))"""
        self.check(b, a)

    # trailing commas

    def test_trailing_comma_1(self):
        b = """print 1, 2, 3,"""
        a = """print(1, 2, 3, end=' ')"""
        self.check(b, a)

    def test_trailing_comma_2(self):
        b = """print 1, 2,"""
        a = """print(1, 2, end=' ')"""
        self.check(b, a)

    def test_trailing_comma_3(self):
        b = """print 1,"""
        a = """print(1, end=' ')"""
        self.check(b, a)

    # >> stuff

    def test_vargs_without_trailing_comma(self):
        b = """print >>sys.stderr, 1, 2, 3"""
        a = """print(1, 2, 3, file=sys.stderr)"""
        self.check(b, a)

    def test_with_trailing_comma(self):
        b = """print >>sys.stderr, 1, 2,"""
        a = """print(1, 2, end=' ', file=sys.stderr)"""
        self.check(b, a)

    def test_no_trailing_comma(self):
        b = """print >>sys.stderr, 1+1"""
        a = """print(1+1, file=sys.stderr)"""
        self.check(b, a)

    def test_spaces_before_file(self):
        b = """print >>  sys.stderr"""
        a = """print(file=sys.stderr)"""
        self.check(b, a)

    def test_with_future_print_function(self):
        s = "z __future__ zaimportuj print_function\n" \
            "print('Hai!', end=' ')"
        self.unchanged(s)

        b = "print 'Hello, world!'"
        a = "print('Hello, world!')"
        self.check(b, a)


klasa Test_exec(FixerTestCase):
    fixer = "exec"

    def test_prefix_preservation(self):
        b = """  exec code w ns1,   ns2"""
        a = """  exec(code, ns1,   ns2)"""
        self.check(b, a)

    def test_basic(self):
        b = """exec code"""
        a = """exec(code)"""
        self.check(b, a)

    def test_with_globals(self):
        b = """exec code w ns"""
        a = """exec(code, ns)"""
        self.check(b, a)

    def test_with_globals_locals(self):
        b = """exec code w ns1, ns2"""
        a = """exec(code, ns1, ns2)"""
        self.check(b, a)

    def test_complex_1(self):
        b = """exec (a.b()) w ns"""
        a = """exec((a.b()), ns)"""
        self.check(b, a)

    def test_complex_2(self):
        b = """exec a.b() + c w ns"""
        a = """exec(a.b() + c, ns)"""
        self.check(b, a)

    # These should nie be touched

    def test_unchanged_1(self):
        s = """exec(code)"""
        self.unchanged(s)

    def test_unchanged_2(self):
        s = """exec (code)"""
        self.unchanged(s)

    def test_unchanged_3(self):
        s = """exec(code, ns)"""
        self.unchanged(s)

    def test_unchanged_4(self):
        s = """exec(code, ns1, ns2)"""
        self.unchanged(s)

klasa Test_repr(FixerTestCase):
    fixer = "repr"

    def test_prefix_preservation(self):
        b = """x =   `1 + 2`"""
        a = """x =   repr(1 + 2)"""
        self.check(b, a)

    def test_simple_1(self):
        b = """x = `1 + 2`"""
        a = """x = repr(1 + 2)"""
        self.check(b, a)

    def test_simple_2(self):
        b = """y = `x`"""
        a = """y = repr(x)"""
        self.check(b, a)

    def test_complex(self):
        b = """z = `y`.__repr__()"""
        a = """z = repr(y).__repr__()"""
        self.check(b, a)

    def test_tuple(self):
        b = """x = `1, 2, 3`"""
        a = """x = repr((1, 2, 3))"""
        self.check(b, a)

    def test_nested(self):
        b = """x = `1 + `2``"""
        a = """x = repr(1 + repr(2))"""
        self.check(b, a)

    def test_nested_tuples(self):
        b = """x = `1, 2 + `3, 4``"""
        a = """x = repr((1, 2 + repr((3, 4))))"""
        self.check(b, a)

klasa Test_except(FixerTestCase):
    fixer = "except"

    def test_prefix_preservation(self):
        b = """
            spróbuj:
                dalej
            wyjąwszy (RuntimeError, ImportError),    e:
                dalej"""
        a = """
            spróbuj:
                dalej
            wyjąwszy (RuntimeError, ImportError) jako    e:
                dalej"""
        self.check(b, a)

    def test_simple(self):
        b = """
            spróbuj:
                dalej
            wyjąwszy Foo, e:
                dalej"""
        a = """
            spróbuj:
                dalej
            wyjąwszy Foo jako e:
                dalej"""
        self.check(b, a)

    def test_simple_no_space_before_target(self):
        b = """
            spróbuj:
                dalej
            wyjąwszy Foo,e:
                dalej"""
        a = """
            spróbuj:
                dalej
            wyjąwszy Foo jako e:
                dalej"""
        self.check(b, a)

    def test_tuple_unpack(self):
        b = """
            def foo():
                spróbuj:
                    dalej
                wyjąwszy Exception, (f, e):
                    dalej
                wyjąwszy ImportError, e:
                    dalej"""

        a = """
            def foo():
                spróbuj:
                    dalej
                wyjąwszy Exception jako xxx_todo_changeme:
                    (f, e) = xxx_todo_changeme.args
                    dalej
                wyjąwszy ImportError jako e:
                    dalej"""
        self.check(b, a)

    def test_multi_class(self):
        b = """
            spróbuj:
                dalej
            wyjąwszy (RuntimeError, ImportError), e:
                dalej"""

        a = """
            spróbuj:
                dalej
            wyjąwszy (RuntimeError, ImportError) jako e:
                dalej"""
        self.check(b, a)

    def test_list_unpack(self):
        b = """
            spróbuj:
                dalej
            wyjąwszy Exception, [a, b]:
                dalej"""

        a = """
            spróbuj:
                dalej
            wyjąwszy Exception jako xxx_todo_changeme:
                [a, b] = xxx_todo_changeme.args
                dalej"""
        self.check(b, a)

    def test_weird_target_1(self):
        b = """
            spróbuj:
                dalej
            wyjąwszy Exception, d[5]:
                dalej"""

        a = """
            spróbuj:
                dalej
            wyjąwszy Exception jako xxx_todo_changeme:
                d[5] = xxx_todo_changeme
                dalej"""
        self.check(b, a)

    def test_weird_target_2(self):
        b = """
            spróbuj:
                dalej
            wyjąwszy Exception, a.foo:
                dalej"""

        a = """
            spróbuj:
                dalej
            wyjąwszy Exception jako xxx_todo_changeme:
                a.foo = xxx_todo_changeme
                dalej"""
        self.check(b, a)

    def test_weird_target_3(self):
        b = """
            spróbuj:
                dalej
            wyjąwszy Exception, a().foo:
                dalej"""

        a = """
            spróbuj:
                dalej
            wyjąwszy Exception jako xxx_todo_changeme:
                a().foo = xxx_todo_changeme
                dalej"""
        self.check(b, a)

    def test_bare_except(self):
        b = """
            spróbuj:
                dalej
            wyjąwszy Exception, a:
                dalej
            wyjąwszy:
                dalej"""

        a = """
            spróbuj:
                dalej
            wyjąwszy Exception jako a:
                dalej
            wyjąwszy:
                dalej"""
        self.check(b, a)

    def test_bare_except_and_inaczej_finally(self):
        b = """
            spróbuj:
                dalej
            wyjąwszy Exception, a:
                dalej
            wyjąwszy:
                dalej
            inaczej:
                dalej
            w_końcu:
                dalej"""

        a = """
            spróbuj:
                dalej
            wyjąwszy Exception jako a:
                dalej
            wyjąwszy:
                dalej
            inaczej:
                dalej
            w_końcu:
                dalej"""
        self.check(b, a)

    def test_multi_fixed_excepts_before_bare_except(self):
        b = """
            spróbuj:
                dalej
            wyjąwszy TypeError, b:
                dalej
            wyjąwszy Exception, a:
                dalej
            wyjąwszy:
                dalej"""

        a = """
            spróbuj:
                dalej
            wyjąwszy TypeError jako b:
                dalej
            wyjąwszy Exception jako a:
                dalej
            wyjąwszy:
                dalej"""
        self.check(b, a)

    def test_one_line_suites(self):
        b = """
            spróbuj: podnieś TypeError
            wyjąwszy TypeError, e:
                dalej
            """
        a = """
            spróbuj: podnieś TypeError
            wyjąwszy TypeError jako e:
                dalej
            """
        self.check(b, a)
        b = """
            spróbuj:
                podnieś TypeError
            wyjąwszy TypeError, e: dalej
            """
        a = """
            spróbuj:
                podnieś TypeError
            wyjąwszy TypeError jako e: dalej
            """
        self.check(b, a)
        b = """
            spróbuj: podnieś TypeError
            wyjąwszy TypeError, e: dalej
            """
        a = """
            spróbuj: podnieś TypeError
            wyjąwszy TypeError jako e: dalej
            """
        self.check(b, a)
        b = """
            spróbuj: podnieś TypeError
            wyjąwszy TypeError, e: dalej
            inaczej: function()
            w_końcu: done()
            """
        a = """
            spróbuj: podnieś TypeError
            wyjąwszy TypeError jako e: dalej
            inaczej: function()
            w_końcu: done()
            """
        self.check(b, a)

    # These should nie be touched:

    def test_unchanged_1(self):
        s = """
            spróbuj:
                dalej
            wyjąwszy:
                dalej"""
        self.unchanged(s)

    def test_unchanged_2(self):
        s = """
            spróbuj:
                dalej
            wyjąwszy Exception:
                dalej"""
        self.unchanged(s)

    def test_unchanged_3(self):
        s = """
            spróbuj:
                dalej
            wyjąwszy (Exception, SystemExit):
                dalej"""
        self.unchanged(s)

klasa Test_raise(FixerTestCase):
    fixer = "raise"

    def test_basic(self):
        b = """raise Exception, 5"""
        a = """raise Exception(5)"""
        self.check(b, a)

    def test_prefix_preservation(self):
        b = """raise Exception,5"""
        a = """raise Exception(5)"""
        self.check(b, a)

        b = """raise   Exception,    5"""
        a = """raise   Exception(5)"""
        self.check(b, a)

    def test_with_comments(self):
        b = """raise Exception, 5 # foo"""
        a = """raise Exception(5) # foo"""
        self.check(b, a)

        b = """raise E, (5, 6) % (a, b) # foo"""
        a = """raise E((5, 6) % (a, b)) # foo"""
        self.check(b, a)

        b = """def foo():
                    podnieś Exception, 5, 6 # foo"""
        a = """def foo():
                    podnieś Exception(5).with_traceback(6) # foo"""
        self.check(b, a)

    def test_Nic_value(self):
        b = """raise Exception(5), Nic, tb"""
        a = """raise Exception(5).with_traceback(tb)"""
        self.check(b, a)

    def test_tuple_value(self):
        b = """raise Exception, (5, 6, 7)"""
        a = """raise Exception(5, 6, 7)"""
        self.check(b, a)

    def test_tuple_detection(self):
        b = """raise E, (5, 6) % (a, b)"""
        a = """raise E((5, 6) % (a, b))"""
        self.check(b, a)

    def test_tuple_exc_1(self):
        b = """raise (((E1, E2), E3), E4), V"""
        a = """raise E1(V)"""
        self.check(b, a)

    def test_tuple_exc_2(self):
        b = """raise (E1, (E2, E3), E4), V"""
        a = """raise E1(V)"""
        self.check(b, a)

    # These should produce a warning

    def test_string_exc(self):
        s = """raise 'foo'"""
        self.warns_unchanged(s, "Python 3 does nie support string exceptions")

    def test_string_exc_val(self):
        s = """raise "foo", 5"""
        self.warns_unchanged(s, "Python 3 does nie support string exceptions")

    def test_string_exc_val_tb(self):
        s = """raise "foo", 5, 6"""
        self.warns_unchanged(s, "Python 3 does nie support string exceptions")

    # These should result w traceback-assignment

    def test_tb_1(self):
        b = """def foo():
                    podnieś Exception, 5, 6"""
        a = """def foo():
                    podnieś Exception(5).with_traceback(6)"""
        self.check(b, a)

    def test_tb_2(self):
        b = """def foo():
                    a = 5
                    podnieś Exception, 5, 6
                    b = 6"""
        a = """def foo():
                    a = 5
                    podnieś Exception(5).with_traceback(6)
                    b = 6"""
        self.check(b, a)

    def test_tb_3(self):
        b = """def foo():
                    podnieś Exception,5,6"""
        a = """def foo():
                    podnieś Exception(5).with_traceback(6)"""
        self.check(b, a)

    def test_tb_4(self):
        b = """def foo():
                    a = 5
                    podnieś Exception,5,6
                    b = 6"""
        a = """def foo():
                    a = 5
                    podnieś Exception(5).with_traceback(6)
                    b = 6"""
        self.check(b, a)

    def test_tb_5(self):
        b = """def foo():
                    podnieś Exception, (5, 6, 7), 6"""
        a = """def foo():
                    podnieś Exception(5, 6, 7).with_traceback(6)"""
        self.check(b, a)

    def test_tb_6(self):
        b = """def foo():
                    a = 5
                    podnieś Exception, (5, 6, 7), 6
                    b = 6"""
        a = """def foo():
                    a = 5
                    podnieś Exception(5, 6, 7).with_traceback(6)
                    b = 6"""
        self.check(b, a)

klasa Test_throw(FixerTestCase):
    fixer = "throw"

    def test_1(self):
        b = """g.throw(Exception, 5)"""
        a = """g.throw(Exception(5))"""
        self.check(b, a)

    def test_2(self):
        b = """g.throw(Exception,5)"""
        a = """g.throw(Exception(5))"""
        self.check(b, a)

    def test_3(self):
        b = """g.throw(Exception, (5, 6, 7))"""
        a = """g.throw(Exception(5, 6, 7))"""
        self.check(b, a)

    def test_4(self):
        b = """5 + g.throw(Exception, 5)"""
        a = """5 + g.throw(Exception(5))"""
        self.check(b, a)

    # These should produce warnings

    def test_warn_1(self):
        s = """g.throw("foo")"""
        self.warns_unchanged(s, "Python 3 does nie support string exceptions")

    def test_warn_2(self):
        s = """g.throw("foo", 5)"""
        self.warns_unchanged(s, "Python 3 does nie support string exceptions")

    def test_warn_3(self):
        s = """g.throw("foo", 5, 6)"""
        self.warns_unchanged(s, "Python 3 does nie support string exceptions")

    # These should nie be touched

    def test_untouched_1(self):
        s = """g.throw(Exception)"""
        self.unchanged(s)

    def test_untouched_2(self):
        s = """g.throw(Exception(5, 6))"""
        self.unchanged(s)

    def test_untouched_3(self):
        s = """5 + g.throw(Exception(5, 6))"""
        self.unchanged(s)

    # These should result w traceback-assignment

    def test_tb_1(self):
        b = """def foo():
                    g.throw(Exception, 5, 6)"""
        a = """def foo():
                    g.throw(Exception(5).with_traceback(6))"""
        self.check(b, a)

    def test_tb_2(self):
        b = """def foo():
                    a = 5
                    g.throw(Exception, 5, 6)
                    b = 6"""
        a = """def foo():
                    a = 5
                    g.throw(Exception(5).with_traceback(6))
                    b = 6"""
        self.check(b, a)

    def test_tb_3(self):
        b = """def foo():
                    g.throw(Exception,5,6)"""
        a = """def foo():
                    g.throw(Exception(5).with_traceback(6))"""
        self.check(b, a)

    def test_tb_4(self):
        b = """def foo():
                    a = 5
                    g.throw(Exception,5,6)
                    b = 6"""
        a = """def foo():
                    a = 5
                    g.throw(Exception(5).with_traceback(6))
                    b = 6"""
        self.check(b, a)

    def test_tb_5(self):
        b = """def foo():
                    g.throw(Exception, (5, 6, 7), 6)"""
        a = """def foo():
                    g.throw(Exception(5, 6, 7).with_traceback(6))"""
        self.check(b, a)

    def test_tb_6(self):
        b = """def foo():
                    a = 5
                    g.throw(Exception, (5, 6, 7), 6)
                    b = 6"""
        a = """def foo():
                    a = 5
                    g.throw(Exception(5, 6, 7).with_traceback(6))
                    b = 6"""
        self.check(b, a)

    def test_tb_7(self):
        b = """def foo():
                    a + g.throw(Exception, 5, 6)"""
        a = """def foo():
                    a + g.throw(Exception(5).with_traceback(6))"""
        self.check(b, a)

    def test_tb_8(self):
        b = """def foo():
                    a = 5
                    a + g.throw(Exception, 5, 6)
                    b = 6"""
        a = """def foo():
                    a = 5
                    a + g.throw(Exception(5).with_traceback(6))
                    b = 6"""
        self.check(b, a)

klasa Test_long(FixerTestCase):
    fixer = "long"

    def test_1(self):
        b = """x = long(x)"""
        a = """x = int(x)"""
        self.check(b, a)

    def test_2(self):
        b = """y = isinstance(x, long)"""
        a = """y = isinstance(x, int)"""
        self.check(b, a)

    def test_3(self):
        b = """z = type(x) w (int, long)"""
        a = """z = type(x) w (int, int)"""
        self.check(b, a)

    def test_unchanged(self):
        s = """long = Prawda"""
        self.unchanged(s)

        s = """s.long = Prawda"""
        self.unchanged(s)

        s = """def long(): dalej"""
        self.unchanged(s)

        s = """class long(): dalej"""
        self.unchanged(s)

        s = """def f(long): dalej"""
        self.unchanged(s)

        s = """def f(g, long): dalej"""
        self.unchanged(s)

        s = """def f(x, long=Prawda): dalej"""
        self.unchanged(s)

    def test_prefix_preservation(self):
        b = """x =   long(  x  )"""
        a = """x =   int(  x  )"""
        self.check(b, a)


klasa Test_execfile(FixerTestCase):
    fixer = "execfile"

    def test_conversion(self):
        b = """execfile("fn")"""
        a = """exec(compile(open("fn").read(), "fn", 'exec'))"""
        self.check(b, a)

        b = """execfile("fn", glob)"""
        a = """exec(compile(open("fn").read(), "fn", 'exec'), glob)"""
        self.check(b, a)

        b = """execfile("fn", glob, loc)"""
        a = """exec(compile(open("fn").read(), "fn", 'exec'), glob, loc)"""
        self.check(b, a)

        b = """execfile("fn", globals=glob)"""
        a = """exec(compile(open("fn").read(), "fn", 'exec'), globals=glob)"""
        self.check(b, a)

        b = """execfile("fn", locals=loc)"""
        a = """exec(compile(open("fn").read(), "fn", 'exec'), locals=loc)"""
        self.check(b, a)

        b = """execfile("fn", globals=glob, locals=loc)"""
        a = """exec(compile(open("fn").read(), "fn", 'exec'), globals=glob, locals=loc)"""
        self.check(b, a)

    def test_spacing(self):
        b = """execfile( "fn" )"""
        a = """exec(compile(open( "fn" ).read(), "fn", 'exec'))"""
        self.check(b, a)

        b = """execfile("fn",  globals = glob)"""
        a = """exec(compile(open("fn").read(), "fn", 'exec'),  globals = glob)"""
        self.check(b, a)


klasa Test_isinstance(FixerTestCase):
    fixer = "isinstance"

    def test_remove_multiple_items(self):
        b = """isinstance(x, (int, int, int))"""
        a = """isinstance(x, int)"""
        self.check(b, a)

        b = """isinstance(x, (int, float, int, int, float))"""
        a = """isinstance(x, (int, float))"""
        self.check(b, a)

        b = """isinstance(x, (int, float, int, int, float, str))"""
        a = """isinstance(x, (int, float, str))"""
        self.check(b, a)

        b = """isinstance(foo() + bar(), (x(), y(), x(), int, int))"""
        a = """isinstance(foo() + bar(), (x(), y(), x(), int))"""
        self.check(b, a)

    def test_prefix_preservation(self):
        b = """jeżeli    isinstance(  foo(), (  bar, bar, baz )) : dalej"""
        a = """jeżeli    isinstance(  foo(), (  bar, baz )) : dalej"""
        self.check(b, a)

    def test_unchanged(self):
        self.unchanged("isinstance(x, (str, int))")

klasa Test_dict(FixerTestCase):
    fixer = "dict"

    def test_prefix_preservation(self):
        b = "jeżeli   d. keys  (  )  : dalej"
        a = "jeżeli   list(d. keys  (  ))  : dalej"
        self.check(b, a)

        b = "jeżeli   d. items  (  )  : dalej"
        a = "jeżeli   list(d. items  (  ))  : dalej"
        self.check(b, a)

        b = "jeżeli   d. iterkeys  ( )  : dalej"
        a = "jeżeli   iter(d. keys  ( ))  : dalej"
        self.check(b, a)

        b = "[i dla i w    d.  iterkeys(  )  ]"
        a = "[i dla i w    d.  keys(  )  ]"
        self.check(b, a)

        b = "jeżeli   d. viewkeys  ( )  : dalej"
        a = "jeżeli   d. keys  ( )  : dalej"
        self.check(b, a)

        b = "[i dla i w    d.  viewkeys(  )  ]"
        a = "[i dla i w    d.  keys(  )  ]"
        self.check(b, a)

    def test_trailing_comment(self):
        b = "d.keys() # foo"
        a = "list(d.keys()) # foo"
        self.check(b, a)

        b = "d.items()  # foo"
        a = "list(d.items())  # foo"
        self.check(b, a)

        b = "d.iterkeys()  # foo"
        a = "iter(d.keys())  # foo"
        self.check(b, a)

        b = """[i dla i w d.iterkeys() # foo
               ]"""
        a = """[i dla i w d.keys() # foo
               ]"""
        self.check(b, a)

        b = """[i dla i w d.iterkeys() # foo
               ]"""
        a = """[i dla i w d.keys() # foo
               ]"""
        self.check(b, a)

        b = "d.viewitems()  # foo"
        a = "d.items()  # foo"
        self.check(b, a)

    def test_unchanged(self):
        dla wrapper w fixer_util.consuming_calls:
            s = "s = %s(d.keys())" % wrapper
            self.unchanged(s)

            s = "s = %s(d.values())" % wrapper
            self.unchanged(s)

            s = "s = %s(d.items())" % wrapper
            self.unchanged(s)

    def test_01(self):
        b = "d.keys()"
        a = "list(d.keys())"
        self.check(b, a)

        b = "a[0].foo().keys()"
        a = "list(a[0].foo().keys())"
        self.check(b, a)

    def test_02(self):
        b = "d.items()"
        a = "list(d.items())"
        self.check(b, a)

    def test_03(self):
        b = "d.values()"
        a = "list(d.values())"
        self.check(b, a)

    def test_04(self):
        b = "d.iterkeys()"
        a = "iter(d.keys())"
        self.check(b, a)

    def test_05(self):
        b = "d.iteritems()"
        a = "iter(d.items())"
        self.check(b, a)

    def test_06(self):
        b = "d.itervalues()"
        a = "iter(d.values())"
        self.check(b, a)

    def test_07(self):
        s = "list(d.keys())"
        self.unchanged(s)

    def test_08(self):
        s = "sorted(d.keys())"
        self.unchanged(s)

    def test_09(self):
        b = "iter(d.keys())"
        a = "iter(list(d.keys()))"
        self.check(b, a)

    def test_10(self):
        b = "foo(d.keys())"
        a = "foo(list(d.keys()))"
        self.check(b, a)

    def test_11(self):
        b = "dla i w d.keys(): print i"
        a = "dla i w list(d.keys()): print i"
        self.check(b, a)

    def test_12(self):
        b = "dla i w d.iterkeys(): print i"
        a = "dla i w d.keys(): print i"
        self.check(b, a)

    def test_13(self):
        b = "[i dla i w d.keys()]"
        a = "[i dla i w list(d.keys())]"
        self.check(b, a)

    def test_14(self):
        b = "[i dla i w d.iterkeys()]"
        a = "[i dla i w d.keys()]"
        self.check(b, a)

    def test_15(self):
        b = "(i dla i w d.keys())"
        a = "(i dla i w list(d.keys()))"
        self.check(b, a)

    def test_16(self):
        b = "(i dla i w d.iterkeys())"
        a = "(i dla i w d.keys())"
        self.check(b, a)

    def test_17(self):
        b = "iter(d.iterkeys())"
        a = "iter(d.keys())"
        self.check(b, a)

    def test_18(self):
        b = "list(d.iterkeys())"
        a = "list(d.keys())"
        self.check(b, a)

    def test_19(self):
        b = "sorted(d.iterkeys())"
        a = "sorted(d.keys())"
        self.check(b, a)

    def test_20(self):
        b = "foo(d.iterkeys())"
        a = "foo(iter(d.keys()))"
        self.check(b, a)

    def test_21(self):
        b = "print h.iterkeys().next()"
        a = "print iter(h.keys()).next()"
        self.check(b, a)

    def test_22(self):
        b = "print h.keys()[0]"
        a = "print list(h.keys())[0]"
        self.check(b, a)

    def test_23(self):
        b = "print list(h.iterkeys().next())"
        a = "print list(iter(h.keys()).next())"
        self.check(b, a)

    def test_24(self):
        b = "dla x w h.keys()[0]: print x"
        a = "dla x w list(h.keys())[0]: print x"
        self.check(b, a)

    def test_25(self):
        b = "d.viewkeys()"
        a = "d.keys()"
        self.check(b, a)

    def test_26(self):
        b = "d.viewitems()"
        a = "d.items()"
        self.check(b, a)

    def test_27(self):
        b = "d.viewvalues()"
        a = "d.values()"
        self.check(b, a)

    def test_28(self):
        b = "[i dla i w d.viewkeys()]"
        a = "[i dla i w d.keys()]"
        self.check(b, a)

    def test_29(self):
        b = "(i dla i w d.viewkeys())"
        a = "(i dla i w d.keys())"
        self.check(b, a)

    def test_30(self):
        b = "iter(d.viewkeys())"
        a = "iter(d.keys())"
        self.check(b, a)

    def test_31(self):
        b = "list(d.viewkeys())"
        a = "list(d.keys())"
        self.check(b, a)

    def test_32(self):
        b = "sorted(d.viewkeys())"
        a = "sorted(d.keys())"
        self.check(b, a)

klasa Test_xrange(FixerTestCase):
    fixer = "xrange"

    def test_prefix_preservation(self):
        b = """x =    xrange(  10  )"""
        a = """x =    range(  10  )"""
        self.check(b, a)

        b = """x = xrange(  1  ,  10   )"""
        a = """x = range(  1  ,  10   )"""
        self.check(b, a)

        b = """x = xrange(  0  ,  10 ,  2 )"""
        a = """x = range(  0  ,  10 ,  2 )"""
        self.check(b, a)

    def test_single_arg(self):
        b = """x = xrange(10)"""
        a = """x = range(10)"""
        self.check(b, a)

    def test_two_args(self):
        b = """x = xrange(1, 10)"""
        a = """x = range(1, 10)"""
        self.check(b, a)

    def test_three_args(self):
        b = """x = xrange(0, 10, 2)"""
        a = """x = range(0, 10, 2)"""
        self.check(b, a)

    def test_wrap_in_list(self):
        b = """x = range(10, 3, 9)"""
        a = """x = list(range(10, 3, 9))"""
        self.check(b, a)

        b = """x = foo(range(10, 3, 9))"""
        a = """x = foo(list(range(10, 3, 9)))"""
        self.check(b, a)

        b = """x = range(10, 3, 9) + [4]"""
        a = """x = list(range(10, 3, 9)) + [4]"""
        self.check(b, a)

        b = """x = range(10)[::-1]"""
        a = """x = list(range(10))[::-1]"""
        self.check(b, a)

        b = """x = range(10)  [3]"""
        a = """x = list(range(10))  [3]"""
        self.check(b, a)

    def test_xrange_in_for(self):
        b = """dla i w xrange(10):\n    j=i"""
        a = """dla i w range(10):\n    j=i"""
        self.check(b, a)

        b = """[i dla i w xrange(10)]"""
        a = """[i dla i w range(10)]"""
        self.check(b, a)

    def test_range_in_for(self):
        self.unchanged("dla i w range(10): dalej")
        self.unchanged("[i dla i w range(10)]")

    def test_in_contains_test(self):
        self.unchanged("x w range(10, 3, 9)")

    def test_in_consuming_context(self):
        dla call w fixer_util.consuming_calls:
            self.unchanged("a = %s(range(10))" % call)

klasa Test_xrange_with_reduce(FixerTestCase):

    def setUp(self):
        super(Test_xrange_with_reduce, self).setUp(["xrange", "reduce"])

    def test_double_transform(self):
        b = """reduce(x, xrange(5))"""
        a = """z functools zaimportuj reduce
reduce(x, range(5))"""
        self.check(b, a)

klasa Test_raw_input(FixerTestCase):
    fixer = "raw_input"

    def test_prefix_preservation(self):
        b = """x =    raw_input(   )"""
        a = """x =    input(   )"""
        self.check(b, a)

        b = """x = raw_input(   ''   )"""
        a = """x = input(   ''   )"""
        self.check(b, a)

    def test_1(self):
        b = """x = raw_input()"""
        a = """x = input()"""
        self.check(b, a)

    def test_2(self):
        b = """x = raw_input('')"""
        a = """x = input('')"""
        self.check(b, a)

    def test_3(self):
        b = """x = raw_input('prompt')"""
        a = """x = input('prompt')"""
        self.check(b, a)

    def test_4(self):
        b = """x = raw_input(foo(a) + 6)"""
        a = """x = input(foo(a) + 6)"""
        self.check(b, a)

    def test_5(self):
        b = """x = raw_input(invite).split()"""
        a = """x = input(invite).split()"""
        self.check(b, a)

    def test_6(self):
        b = """x = raw_input(invite) . split ()"""
        a = """x = input(invite) . split ()"""
        self.check(b, a)

    def test_8(self):
        b = "x = int(raw_input())"
        a = "x = int(input())"
        self.check(b, a)

klasa Test_funcattrs(FixerTestCase):
    fixer = "funcattrs"

    attrs = ["closure", "doc", "name", "defaults", "code", "globals", "dict"]

    def test(self):
        dla attr w self.attrs:
            b = "a.func_%s" % attr
            a = "a.__%s__" % attr
            self.check(b, a)

            b = "self.foo.func_%s.foo_bar" % attr
            a = "self.foo.__%s__.foo_bar" % attr
            self.check(b, a)

    def test_unchanged(self):
        dla attr w self.attrs:
            s = "foo(func_%s + 5)" % attr
            self.unchanged(s)

            s = "f(foo.__%s__)" % attr
            self.unchanged(s)

            s = "f(foo.__%s__.foo)" % attr
            self.unchanged(s)

klasa Test_xreadlines(FixerTestCase):
    fixer = "xreadlines"

    def test_call(self):
        b = "dla x w f.xreadlines(): dalej"
        a = "dla x w f: dalej"
        self.check(b, a)

        b = "dla x w foo().xreadlines(): dalej"
        a = "dla x w foo(): dalej"
        self.check(b, a)

        b = "dla x w (5 + foo()).xreadlines(): dalej"
        a = "dla x w (5 + foo()): dalej"
        self.check(b, a)

    def test_attr_ref(self):
        b = "foo(f.xreadlines + 5)"
        a = "foo(f.__iter__ + 5)"
        self.check(b, a)

        b = "foo(f().xreadlines + 5)"
        a = "foo(f().__iter__ + 5)"
        self.check(b, a)

        b = "foo((5 + f()).xreadlines + 5)"
        a = "foo((5 + f()).__iter__ + 5)"
        self.check(b, a)

    def test_unchanged(self):
        s = "dla x w f.xreadlines(5): dalej"
        self.unchanged(s)

        s = "dla x w f.xreadlines(k=5): dalej"
        self.unchanged(s)

        s = "dla x w f.xreadlines(*k, **v): dalej"
        self.unchanged(s)

        s = "foo(xreadlines)"
        self.unchanged(s)


klasa ImportsFixerTests:

    def test_import_module(self):
        dla old, new w self.modules.items():
            b = "zaimportuj %s" % old
            a = "zaimportuj %s" % new
            self.check(b, a)

            b = "zaimportuj foo, %s, bar" % old
            a = "zaimportuj foo, %s, bar" % new
            self.check(b, a)

    def test_import_from(self):
        dla old, new w self.modules.items():
            b = "z %s zaimportuj foo" % old
            a = "z %s zaimportuj foo" % new
            self.check(b, a)

            b = "z %s zaimportuj foo, bar" % old
            a = "z %s zaimportuj foo, bar" % new
            self.check(b, a)

            b = "z %s zaimportuj (yes, no)" % old
            a = "z %s zaimportuj (yes, no)" % new
            self.check(b, a)

    def test_import_module_as(self):
        dla old, new w self.modules.items():
            b = "zaimportuj %s jako foo_bar" % old
            a = "zaimportuj %s jako foo_bar" % new
            self.check(b, a)

            b = "zaimportuj %s jako foo_bar" % old
            a = "zaimportuj %s jako foo_bar" % new
            self.check(b, a)

    def test_import_from_as(self):
        dla old, new w self.modules.items():
            b = "z %s zaimportuj foo jako bar" % old
            a = "z %s zaimportuj foo jako bar" % new
            self.check(b, a)

    def test_star(self):
        dla old, new w self.modules.items():
            b = "z %s zaimportuj *" % old
            a = "z %s zaimportuj *" % new
            self.check(b, a)

    def test_import_module_usage(self):
        dla old, new w self.modules.items():
            b = """
                zaimportuj %s
                foo(%s.bar)
                """ % (old, old)
            a = """
                zaimportuj %s
                foo(%s.bar)
                """ % (new, new)
            self.check(b, a)

            b = """
                z %s zaimportuj x
                %s = 23
                """ % (old, old)
            a = """
                z %s zaimportuj x
                %s = 23
                """ % (new, old)
            self.check(b, a)

            s = """
                def f():
                    %s.method()
                """ % (old,)
            self.unchanged(s)

            # test nested usage
            b = """
                zaimportuj %s
                %s.bar(%s.foo)
                """ % (old, old, old)
            a = """
                zaimportuj %s
                %s.bar(%s.foo)
                """ % (new, new, new)
            self.check(b, a)

            b = """
                zaimportuj %s
                x.%s
                """ % (old, old)
            a = """
                zaimportuj %s
                x.%s
                """ % (new, old)
            self.check(b, a)


klasa Test_imports(FixerTestCase, ImportsFixerTests):
    fixer = "imports"
    z ..fixes.fix_imports zaimportuj MAPPING jako modules

    def test_multiple_imports(self):
        b = """zaimportuj urlparse, cStringIO"""
        a = """zaimportuj urllib.parse, io"""
        self.check(b, a)

    def test_multiple_imports_as(self):
        b = """
            zaimportuj copy_reg jako bar, HTMLParser jako foo, urlparse
            s = urlparse.spam(bar.foo())
            """
        a = """
            zaimportuj copyreg jako bar, html.parser jako foo, urllib.parse
            s = urllib.parse.spam(bar.foo())
            """
        self.check(b, a)


klasa Test_imports2(FixerTestCase, ImportsFixerTests):
    fixer = "imports2"
    z ..fixes.fix_imports2 zaimportuj MAPPING jako modules


klasa Test_imports_fixer_order(FixerTestCase, ImportsFixerTests):

    def setUp(self):
        super(Test_imports_fixer_order, self).setUp(['imports', 'imports2'])
        z ..fixes.fix_imports2 zaimportuj MAPPING jako mapping2
        self.modules = mapping2.copy()
        z ..fixes.fix_imports zaimportuj MAPPING jako mapping1
        dla key w ('dbhash', 'dumbdbm', 'dbm', 'gdbm'):
            self.modules[key] = mapping1[key]

    def test_after_local_imports_refactoring(self):
        dla fix w ("imports", "imports2"):
            self.fixer = fix
            self.assert_runs_after("import")


klasa Test_urllib(FixerTestCase):
    fixer = "urllib"
    z ..fixes.fix_urllib zaimportuj MAPPING jako modules

    def test_import_module(self):
        dla old, changes w self.modules.items():
            b = "zaimportuj %s" % old
            a = "zaimportuj %s" % ", ".join(map(itemgetter(0), changes))
            self.check(b, a)

    def test_import_from(self):
        dla old, changes w self.modules.items():
            all_members = []
            dla new, members w changes:
                dla member w members:
                    all_members.append(member)
                    b = "z %s zaimportuj %s" % (old, member)
                    a = "z %s zaimportuj %s" % (new, member)
                    self.check(b, a)

                    s = "z foo zaimportuj %s" % member
                    self.unchanged(s)

                b = "z %s zaimportuj %s" % (old, ", ".join(members))
                a = "z %s zaimportuj %s" % (new, ", ".join(members))
                self.check(b, a)

                s = "z foo zaimportuj %s" % ", ".join(members)
                self.unchanged(s)

            # test the przerwijing of a module into multiple replacements
            b = "z %s zaimportuj %s" % (old, ", ".join(all_members))
            a = "\n".join(["z %s zaimportuj %s" % (new, ", ".join(members))
                            dla (new, members) w changes])
            self.check(b, a)

    def test_import_module_as(self):
        dla old w self.modules:
            s = "zaimportuj %s jako foo" % old
            self.warns_unchanged(s, "This module jest now multiple modules")

    def test_import_from_as(self):
        dla old, changes w self.modules.items():
            dla new, members w changes:
                dla member w members:
                    b = "z %s zaimportuj %s jako foo_bar" % (old, member)
                    a = "z %s zaimportuj %s jako foo_bar" % (new, member)
                    self.check(b, a)
                    b = "z %s zaimportuj %s jako blah, %s" % (old, member, member)
                    a = "z %s zaimportuj %s jako blah, %s" % (new, member, member)
                    self.check(b, a)

    def test_star(self):
        dla old w self.modules:
            s = "z %s zaimportuj *" % old
            self.warns_unchanged(s, "Cannot handle star imports")

    def test_indented(self):
        b = """
def foo():
    z urllib zaimportuj urlencode, urlopen
"""
        a = """
def foo():
    z urllib.parse zaimportuj urlencode
    z urllib.request zaimportuj urlopen
"""
        self.check(b, a)

        b = """
def foo():
    other()
    z urllib zaimportuj urlencode, urlopen
"""
        a = """
def foo():
    other()
    z urllib.parse zaimportuj urlencode
    z urllib.request zaimportuj urlopen
"""
        self.check(b, a)



    def test_import_module_usage(self):
        dla old, changes w self.modules.items():
            dla new, members w changes:
                dla member w members:
                    new_zaimportuj = ", ".join([n dla (n, mems)
                                            w self.modules[old]])
                    b = """
                        zaimportuj %s
                        foo(%s.%s)
                        """ % (old, old, member)
                    a = """
                        zaimportuj %s
                        foo(%s.%s)
                        """ % (new_import, new, member)
                    self.check(b, a)
                    b = """
                        zaimportuj %s
                        %s.%s(%s.%s)
                        """ % (old, old, member, old, member)
                    a = """
                        zaimportuj %s
                        %s.%s(%s.%s)
                        """ % (new_import, new, member, new, member)
                    self.check(b, a)


klasa Test_input(FixerTestCase):
    fixer = "input"

    def test_prefix_preservation(self):
        b = """x =   input(   )"""
        a = """x =   eval(input(   ))"""
        self.check(b, a)

        b = """x = input(   ''   )"""
        a = """x = eval(input(   ''   ))"""
        self.check(b, a)

    def test_trailing_comment(self):
        b = """x = input()  #  foo"""
        a = """x = eval(input())  #  foo"""
        self.check(b, a)

    def test_idempotency(self):
        s = """x = eval(input())"""
        self.unchanged(s)

        s = """x = eval(input(''))"""
        self.unchanged(s)

        s = """x = eval(input(foo(5) + 9))"""
        self.unchanged(s)

    def test_1(self):
        b = """x = input()"""
        a = """x = eval(input())"""
        self.check(b, a)

    def test_2(self):
        b = """x = input('')"""
        a = """x = eval(input(''))"""
        self.check(b, a)

    def test_3(self):
        b = """x = input('prompt')"""
        a = """x = eval(input('prompt'))"""
        self.check(b, a)

    def test_4(self):
        b = """x = input(foo(5) + 9)"""
        a = """x = eval(input(foo(5) + 9))"""
        self.check(b, a)

klasa Test_tuple_params(FixerTestCase):
    fixer = "tuple_params"

    def test_unchanged_1(self):
        s = """def foo(): dalej"""
        self.unchanged(s)

    def test_unchanged_2(self):
        s = """def foo(a, b, c): dalej"""
        self.unchanged(s)

    def test_unchanged_3(self):
        s = """def foo(a=3, b=4, c=5): dalej"""
        self.unchanged(s)

    def test_1(self):
        b = """
            def foo(((a, b), c)):
                x = 5"""

        a = """
            def foo(xxx_todo_changeme):
                ((a, b), c) = xxx_todo_changeme
                x = 5"""
        self.check(b, a)

    def test_2(self):
        b = """
            def foo(((a, b), c), d):
                x = 5"""

        a = """
            def foo(xxx_todo_changeme, d):
                ((a, b), c) = xxx_todo_changeme
                x = 5"""
        self.check(b, a)

    def test_3(self):
        b = """
            def foo(((a, b), c), d) -> e:
                x = 5"""

        a = """
            def foo(xxx_todo_changeme, d) -> e:
                ((a, b), c) = xxx_todo_changeme
                x = 5"""
        self.check(b, a)

    def test_semicolon(self):
        b = """
            def foo(((a, b), c)): x = 5; y = 7"""

        a = """
            def foo(xxx_todo_changeme): ((a, b), c) = xxx_todo_changeme; x = 5; y = 7"""
        self.check(b, a)

    def test_keywords(self):
        b = """
            def foo(((a, b), c), d, e=5) -> z:
                x = 5"""

        a = """
            def foo(xxx_todo_changeme, d, e=5) -> z:
                ((a, b), c) = xxx_todo_changeme
                x = 5"""
        self.check(b, a)

    def test_varargs(self):
        b = """
            def foo(((a, b), c), d, *vargs, **kwargs) -> z:
                x = 5"""

        a = """
            def foo(xxx_todo_changeme, d, *vargs, **kwargs) -> z:
                ((a, b), c) = xxx_todo_changeme
                x = 5"""
        self.check(b, a)

    def test_multi_1(self):
        b = """
            def foo(((a, b), c), (d, e, f)) -> z:
                x = 5"""

        a = """
            def foo(xxx_todo_changeme, xxx_todo_changeme1) -> z:
                ((a, b), c) = xxx_todo_changeme
                (d, e, f) = xxx_todo_changeme1
                x = 5"""
        self.check(b, a)

    def test_multi_2(self):
        b = """
            def foo(x, ((a, b), c), d, (e, f, g), y) -> z:
                x = 5"""

        a = """
            def foo(x, xxx_todo_changeme, d, xxx_todo_changeme1, y) -> z:
                ((a, b), c) = xxx_todo_changeme
                (e, f, g) = xxx_todo_changeme1
                x = 5"""
        self.check(b, a)

    def test_docstring(self):
        b = """
            def foo(((a, b), c), (d, e, f)) -> z:
                "foo foo foo foo"
                x = 5"""

        a = """
            def foo(xxx_todo_changeme, xxx_todo_changeme1) -> z:
                "foo foo foo foo"
                ((a, b), c) = xxx_todo_changeme
                (d, e, f) = xxx_todo_changeme1
                x = 5"""
        self.check(b, a)

    def test_lambda_no_change(self):
        s = """lambda x: x + 5"""
        self.unchanged(s)

    def test_lambda_parens_single_arg(self):
        b = """lambda (x): x + 5"""
        a = """lambda x: x + 5"""
        self.check(b, a)

        b = """lambda(x): x + 5"""
        a = """lambda x: x + 5"""
        self.check(b, a)

        b = """lambda ((((x)))): x + 5"""
        a = """lambda x: x + 5"""
        self.check(b, a)

        b = """lambda((((x)))): x + 5"""
        a = """lambda x: x + 5"""
        self.check(b, a)

    def test_lambda_simple(self):
        b = """lambda (x, y): x + f(y)"""
        a = """lambda x_y: x_y[0] + f(x_y[1])"""
        self.check(b, a)

        b = """lambda(x, y): x + f(y)"""
        a = """lambda x_y: x_y[0] + f(x_y[1])"""
        self.check(b, a)

        b = """lambda (((x, y))): x + f(y)"""
        a = """lambda x_y: x_y[0] + f(x_y[1])"""
        self.check(b, a)

        b = """lambda(((x, y))): x + f(y)"""
        a = """lambda x_y: x_y[0] + f(x_y[1])"""
        self.check(b, a)

    def test_lambda_one_tuple(self):
        b = """lambda (x,): x + f(x)"""
        a = """lambda x1: x1[0] + f(x1[0])"""
        self.check(b, a)

        b = """lambda (((x,))): x + f(x)"""
        a = """lambda x1: x1[0] + f(x1[0])"""
        self.check(b, a)

    def test_lambda_simple_multi_use(self):
        b = """lambda (x, y): x + x + f(x) + x"""
        a = """lambda x_y: x_y[0] + x_y[0] + f(x_y[0]) + x_y[0]"""
        self.check(b, a)

    def test_lambda_simple_reverse(self):
        b = """lambda (x, y): y + x"""
        a = """lambda x_y: x_y[1] + x_y[0]"""
        self.check(b, a)

    def test_lambda_nested(self):
        b = """lambda (x, (y, z)): x + y + z"""
        a = """lambda x_y_z: x_y_z[0] + x_y_z[1][0] + x_y_z[1][1]"""
        self.check(b, a)

        b = """lambda (((x, (y, z)))): x + y + z"""
        a = """lambda x_y_z: x_y_z[0] + x_y_z[1][0] + x_y_z[1][1]"""
        self.check(b, a)

    def test_lambda_nested_multi_use(self):
        b = """lambda (x, (y, z)): x + y + f(y)"""
        a = """lambda x_y_z: x_y_z[0] + x_y_z[1][0] + f(x_y_z[1][0])"""
        self.check(b, a)

klasa Test_methodattrs(FixerTestCase):
    fixer = "methodattrs"

    attrs = ["func", "self", "class"]

    def test(self):
        dla attr w self.attrs:
            b = "a.im_%s" % attr
            jeżeli attr == "class":
                a = "a.__self__.__class__"
            inaczej:
                a = "a.__%s__" % attr
            self.check(b, a)

            b = "self.foo.im_%s.foo_bar" % attr
            jeżeli attr == "class":
                a = "self.foo.__self__.__class__.foo_bar"
            inaczej:
                a = "self.foo.__%s__.foo_bar" % attr
            self.check(b, a)

    def test_unchanged(self):
        dla attr w self.attrs:
            s = "foo(im_%s + 5)" % attr
            self.unchanged(s)

            s = "f(foo.__%s__)" % attr
            self.unchanged(s)

            s = "f(foo.__%s__.foo)" % attr
            self.unchanged(s)

klasa Test_next(FixerTestCase):
    fixer = "next"

    def test_1(self):
        b = """it.next()"""
        a = """next(it)"""
        self.check(b, a)

    def test_2(self):
        b = """a.b.c.d.next()"""
        a = """next(a.b.c.d)"""
        self.check(b, a)

    def test_3(self):
        b = """(a + b).next()"""
        a = """next((a + b))"""
        self.check(b, a)

    def test_4(self):
        b = """a().next()"""
        a = """next(a())"""
        self.check(b, a)

    def test_5(self):
        b = """a().next() + b"""
        a = """next(a()) + b"""
        self.check(b, a)

    def test_6(self):
        b = """c(      a().next() + b)"""
        a = """c(      next(a()) + b)"""
        self.check(b, a)

    def test_prefix_preservation_1(self):
        b = """
            dla a w b:
                foo(a)
                a.next()
            """
        a = """
            dla a w b:
                foo(a)
                next(a)
            """
        self.check(b, a)

    def test_prefix_preservation_2(self):
        b = """
            dla a w b:
                foo(a) # abc
                # def
                a.next()
            """
        a = """
            dla a w b:
                foo(a) # abc
                # def
                next(a)
            """
        self.check(b, a)

    def test_prefix_preservation_3(self):
        b = """
            next = 5
            dla a w b:
                foo(a)
                a.next()
            """
        a = """
            next = 5
            dla a w b:
                foo(a)
                a.__next__()
            """
        self.check(b, a, ignore_warnings=Prawda)

    def test_prefix_preservation_4(self):
        b = """
            next = 5
            dla a w b:
                foo(a) # abc
                # def
                a.next()
            """
        a = """
            next = 5
            dla a w b:
                foo(a) # abc
                # def
                a.__next__()
            """
        self.check(b, a, ignore_warnings=Prawda)

    def test_prefix_preservation_5(self):
        b = """
            next = 5
            dla a w b:
                foo(foo(a), # abc
                    a.next())
            """
        a = """
            next = 5
            dla a w b:
                foo(foo(a), # abc
                    a.__next__())
            """
        self.check(b, a, ignore_warnings=Prawda)

    def test_prefix_preservation_6(self):
        b = """
            dla a w b:
                foo(foo(a), # abc
                    a.next())
            """
        a = """
            dla a w b:
                foo(foo(a), # abc
                    next(a))
            """
        self.check(b, a)

    def test_method_1(self):
        b = """
            klasa A:
                def next(self):
                    dalej
            """
        a = """
            klasa A:
                def __next__(self):
                    dalej
            """
        self.check(b, a)

    def test_method_2(self):
        b = """
            klasa A(object):
                def next(self):
                    dalej
            """
        a = """
            klasa A(object):
                def __next__(self):
                    dalej
            """
        self.check(b, a)

    def test_method_3(self):
        b = """
            klasa A:
                def next(x):
                    dalej
            """
        a = """
            klasa A:
                def __next__(x):
                    dalej
            """
        self.check(b, a)

    def test_method_4(self):
        b = """
            klasa A:
                def __init__(self, foo):
                    self.foo = foo

                def next(self):
                    dalej

                def __iter__(self):
                    zwróć self
            """
        a = """
            klasa A:
                def __init__(self, foo):
                    self.foo = foo

                def __next__(self):
                    dalej

                def __iter__(self):
                    zwróć self
            """
        self.check(b, a)

    def test_method_unchanged(self):
        s = """
            klasa A:
                def next(self, a, b):
                    dalej
            """
        self.unchanged(s)

    def test_shadowing_assign_simple(self):
        s = """
            next = foo

            klasa A:
                def next(self, a, b):
                    dalej
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    def test_shadowing_assign_tuple_1(self):
        s = """
            (next, a) = foo

            klasa A:
                def next(self, a, b):
                    dalej
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    def test_shadowing_assign_tuple_2(self):
        s = """
            (a, (b, (next, c)), a) = foo

            klasa A:
                def next(self, a, b):
                    dalej
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    def test_shadowing_assign_list_1(self):
        s = """
            [next, a] = foo

            klasa A:
                def next(self, a, b):
                    dalej
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    def test_shadowing_assign_list_2(self):
        s = """
            [a, [b, [next, c]], a] = foo

            klasa A:
                def next(self, a, b):
                    dalej
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    def test_builtin_assign(self):
        s = """
            def foo():
                __builtin__.next = foo

            klasa A:
                def next(self, a, b):
                    dalej
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    def test_builtin_assign_in_tuple(self):
        s = """
            def foo():
                (a, __builtin__.next) = foo

            klasa A:
                def next(self, a, b):
                    dalej
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    def test_builtin_assign_in_list(self):
        s = """
            def foo():
                [a, __builtin__.next] = foo

            klasa A:
                def next(self, a, b):
                    dalej
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    def test_assign_to_next(self):
        s = """
            def foo():
                A.next = foo

            klasa A:
                def next(self, a, b):
                    dalej
            """
        self.unchanged(s)

    def test_assign_to_next_in_tuple(self):
        s = """
            def foo():
                (a, A.next) = foo

            klasa A:
                def next(self, a, b):
                    dalej
            """
        self.unchanged(s)

    def test_assign_to_next_in_list(self):
        s = """
            def foo():
                [a, A.next] = foo

            klasa A:
                def next(self, a, b):
                    dalej
            """
        self.unchanged(s)

    def test_shadowing_import_1(self):
        s = """
            zaimportuj foo.bar jako next

            klasa A:
                def next(self, a, b):
                    dalej
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    def test_shadowing_import_2(self):
        s = """
            zaimportuj bar, bar.foo jako next

            klasa A:
                def next(self, a, b):
                    dalej
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    def test_shadowing_import_3(self):
        s = """
            zaimportuj bar, bar.foo jako next, baz

            klasa A:
                def next(self, a, b):
                    dalej
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    def test_shadowing_import_from_1(self):
        s = """
            z x zaimportuj next

            klasa A:
                def next(self, a, b):
                    dalej
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    def test_shadowing_import_from_2(self):
        s = """
            z x.a zaimportuj next

            klasa A:
                def next(self, a, b):
                    dalej
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    def test_shadowing_import_from_3(self):
        s = """
            z x zaimportuj a, next, b

            klasa A:
                def next(self, a, b):
                    dalej
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    def test_shadowing_import_from_4(self):
        s = """
            z x.a zaimportuj a, next, b

            klasa A:
                def next(self, a, b):
                    dalej
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    def test_shadowing_funcdef_1(self):
        s = """
            def next(a):
                dalej

            klasa A:
                def next(self, a, b):
                    dalej
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    def test_shadowing_funcdef_2(self):
        b = """
            def next(a):
                dalej

            klasa A:
                def next(self):
                    dalej

            it.next()
            """
        a = """
            def next(a):
                dalej

            klasa A:
                def __next__(self):
                    dalej

            it.__next__()
            """
        self.warns(b, a, "Calls to builtin next() possibly shadowed")

    def test_shadowing_global_1(self):
        s = """
            def f():
                global next
                next = 5
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    def test_shadowing_global_2(self):
        s = """
            def f():
                global a, next, b
                next = 5
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    def test_shadowing_for_simple(self):
        s = """
            dla next w it():
                dalej

            b = 5
            c = 6
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    def test_shadowing_for_tuple_1(self):
        s = """
            dla next, b w it():
                dalej

            b = 5
            c = 6
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    def test_shadowing_for_tuple_2(self):
        s = """
            dla a, (next, c), b w it():
                dalej

            b = 5
            c = 6
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    def test_noncall_access_1(self):
        b = """gnext = g.next"""
        a = """gnext = g.__next__"""
        self.check(b, a)

    def test_noncall_access_2(self):
        b = """f(g.next + 5)"""
        a = """f(g.__next__ + 5)"""
        self.check(b, a)

    def test_noncall_access_3(self):
        b = """f(g().next + 5)"""
        a = """f(g().__next__ + 5)"""
        self.check(b, a)

klasa Test_nonzero(FixerTestCase):
    fixer = "nonzero"

    def test_1(self):
        b = """
            klasa A:
                def __nonzero__(self):
                    dalej
            """
        a = """
            klasa A:
                def __bool__(self):
                    dalej
            """
        self.check(b, a)

    def test_2(self):
        b = """
            klasa A(object):
                def __nonzero__(self):
                    dalej
            """
        a = """
            klasa A(object):
                def __bool__(self):
                    dalej
            """
        self.check(b, a)

    def test_unchanged_1(self):
        s = """
            klasa A(object):
                def __bool__(self):
                    dalej
            """
        self.unchanged(s)

    def test_unchanged_2(self):
        s = """
            klasa A(object):
                def __nonzero__(self, a):
                    dalej
            """
        self.unchanged(s)

    def test_unchanged_func(self):
        s = """
            def __nonzero__(self):
                dalej
            """
        self.unchanged(s)

klasa Test_numliterals(FixerTestCase):
    fixer = "numliterals"

    def test_octal_1(self):
        b = """0755"""
        a = """0o755"""
        self.check(b, a)

    def test_long_int_1(self):
        b = """a = 12L"""
        a = """a = 12"""
        self.check(b, a)

    def test_long_int_2(self):
        b = """a = 12l"""
        a = """a = 12"""
        self.check(b, a)

    def test_long_hex(self):
        b = """b = 0x12l"""
        a = """b = 0x12"""
        self.check(b, a)

    def test_comments_and_spacing(self):
        b = """b =   0x12L"""
        a = """b =   0x12"""
        self.check(b, a)

        b = """b = 0755 # spam"""
        a = """b = 0o755 # spam"""
        self.check(b, a)

    def test_unchanged_int(self):
        s = """5"""
        self.unchanged(s)

    def test_unchanged_float(self):
        s = """5.0"""
        self.unchanged(s)

    def test_unchanged_octal(self):
        s = """0o755"""
        self.unchanged(s)

    def test_unchanged_hex(self):
        s = """0xABC"""
        self.unchanged(s)

    def test_unchanged_exp(self):
        s = """5.0e10"""
        self.unchanged(s)

    def test_unchanged_complex_int(self):
        s = """5 + 4j"""
        self.unchanged(s)

    def test_unchanged_complex_float(self):
        s = """5.4 + 4.9j"""
        self.unchanged(s)

    def test_unchanged_complex_bare(self):
        s = """4j"""
        self.unchanged(s)
        s = """4.4j"""
        self.unchanged(s)

klasa Test_renames(FixerTestCase):
    fixer = "renames"

    modules = {"sys":  ("maxint", "maxsize"),
              }

    def test_import_from(self):
        dla mod, (old, new) w list(self.modules.items()):
            b = "z %s zaimportuj %s" % (mod, old)
            a = "z %s zaimportuj %s" % (mod, new)
            self.check(b, a)

            s = "z foo zaimportuj %s" % old
            self.unchanged(s)

    def test_import_from_as(self):
        dla mod, (old, new) w list(self.modules.items()):
            b = "z %s zaimportuj %s jako foo_bar" % (mod, old)
            a = "z %s zaimportuj %s jako foo_bar" % (mod, new)
            self.check(b, a)

    def test_import_module_usage(self):
        dla mod, (old, new) w list(self.modules.items()):
            b = """
                zaimportuj %s
                foo(%s, %s.%s)
                """ % (mod, mod, mod, old)
            a = """
                zaimportuj %s
                foo(%s, %s.%s)
                """ % (mod, mod, mod, new)
            self.check(b, a)

    def XXX_test_from_import_usage(self):
        # nie implemented yet
        dla mod, (old, new) w list(self.modules.items()):
            b = """
                z %s zaimportuj %s
                foo(%s, %s)
                """ % (mod, old, mod, old)
            a = """
                z %s zaimportuj %s
                foo(%s, %s)
                """ % (mod, new, mod, new)
            self.check(b, a)

klasa Test_unicode(FixerTestCase):
    fixer = "unicode"

    def test_whitespace(self):
        b = """unicode( x)"""
        a = """str( x)"""
        self.check(b, a)

        b = """ unicode(x )"""
        a = """ str(x )"""
        self.check(b, a)

        b = """ u'h'"""
        a = """ 'h'"""
        self.check(b, a)

    def test_unicode_call(self):
        b = """unicode(x, y, z)"""
        a = """str(x, y, z)"""
        self.check(b, a)

    def test_unichr(self):
        b = """unichr(u'h')"""
        a = """chr('h')"""
        self.check(b, a)

    def test_unicode_literal_1(self):
        b = '''u"x"'''
        a = '''"x"'''
        self.check(b, a)

    def test_unicode_literal_2(self):
        b = """ur'x'"""
        a = """r'x'"""
        self.check(b, a)

    def test_unicode_literal_3(self):
        b = """UR'''x''' """
        a = """R'''x''' """
        self.check(b, a)

    def test_native_literal_escape_u(self):
        b = r"""'\\\u20ac\U0001d121\\u20ac'"""
        a = r"""'\\\\u20ac\\U0001d121\\u20ac'"""
        self.check(b, a)

        b = r"""r'\\\u20ac\U0001d121\\u20ac'"""
        a = r"""r'\\\u20ac\U0001d121\\u20ac'"""
        self.check(b, a)

    def test_bytes_literal_escape_u(self):
        b = r"""b'\\\u20ac\U0001d121\\u20ac'"""
        a = r"""b'\\\u20ac\U0001d121\\u20ac'"""
        self.check(b, a)

        b = r"""br'\\\u20ac\U0001d121\\u20ac'"""
        a = r"""br'\\\u20ac\U0001d121\\u20ac'"""
        self.check(b, a)

    def test_unicode_literal_escape_u(self):
        b = r"""u'\\\u20ac\U0001d121\\u20ac'"""
        a = r"""'\\\u20ac\U0001d121\\u20ac'"""
        self.check(b, a)

        b = r"""ur'\\\u20ac\U0001d121\\u20ac'"""
        a = r"""r'\\\u20ac\U0001d121\\u20ac'"""
        self.check(b, a)

    def test_native_unicode_literal_escape_u(self):
        f = 'z __future__ zaimportuj unicode_literals\n'
        b = f + r"""'\\\u20ac\U0001d121\\u20ac'"""
        a = f + r"""'\\\u20ac\U0001d121\\u20ac'"""
        self.check(b, a)

        b = f + r"""r'\\\u20ac\U0001d121\\u20ac'"""
        a = f + r"""r'\\\u20ac\U0001d121\\u20ac'"""
        self.check(b, a)

klasa Test_callable(FixerTestCase):
    fixer = "callable"

    def test_prefix_preservation(self):
        b = """callable(    x)"""
        a = """zaimportuj collections\nisinstance(    x, collections.Callable)"""
        self.check(b, a)

        b = """jeżeli     callable(x): dalej"""
        a = """zaimportuj collections
jeżeli     isinstance(x, collections.Callable): dalej"""
        self.check(b, a)

    def test_callable_call(self):
        b = """callable(x)"""
        a = """zaimportuj collections\nisinstance(x, collections.Callable)"""
        self.check(b, a)

    def test_global_import(self):
        b = """
def spam(foo):
    callable(foo)"""[1:]
        a = """
zaimportuj collections
def spam(foo):
    isinstance(foo, collections.Callable)"""[1:]
        self.check(b, a)

        b = """
zaimportuj collections
def spam(foo):
    callable(foo)"""[1:]
        # same output jeżeli it was already imported
        self.check(b, a)

        b = """
z collections zaimportuj *
def spam(foo):
    callable(foo)"""[1:]
        a = """
z collections zaimportuj *
zaimportuj collections
def spam(foo):
    isinstance(foo, collections.Callable)"""[1:]
        self.check(b, a)

        b = """
do_stuff()
do_some_other_stuff()
assert callable(do_stuff)"""[1:]
        a = """
zaimportuj collections
do_stuff()
do_some_other_stuff()
assert isinstance(do_stuff, collections.Callable)"""[1:]
        self.check(b, a)

        b = """
jeżeli isinstance(do_stuff, Callable):
    assert callable(do_stuff)
    do_stuff(do_stuff)
    jeżeli nie callable(do_stuff):
        exit(1)
    inaczej:
        assert callable(do_stuff)
inaczej:
    assert nie callable(do_stuff)"""[1:]
        a = """
zaimportuj collections
jeżeli isinstance(do_stuff, Callable):
    assert isinstance(do_stuff, collections.Callable)
    do_stuff(do_stuff)
    jeżeli nie isinstance(do_stuff, collections.Callable):
        exit(1)
    inaczej:
        assert isinstance(do_stuff, collections.Callable)
inaczej:
    assert nie isinstance(do_stuff, collections.Callable)"""[1:]
        self.check(b, a)

    def test_callable_should_not_change(self):
        a = """callable(*x)"""
        self.unchanged(a)

        a = """callable(x, y)"""
        self.unchanged(a)

        a = """callable(x, kw=y)"""
        self.unchanged(a)

        a = """callable()"""
        self.unchanged(a)

klasa Test_filter(FixerTestCase):
    fixer = "filter"

    def test_prefix_preservation(self):
        b = """x =   filter(    foo,     'abc'   )"""
        a = """x =   list(filter(    foo,     'abc'   ))"""
        self.check(b, a)

        b = """x =   filter(  Nic , 'abc'  )"""
        a = """x =   [_f dla _f w 'abc' jeżeli _f]"""
        self.check(b, a)

    def test_filter_basic(self):
        b = """x = filter(Nic, 'abc')"""
        a = """x = [_f dla _f w 'abc' jeżeli _f]"""
        self.check(b, a)

        b = """x = len(filter(f, 'abc'))"""
        a = """x = len(list(filter(f, 'abc')))"""
        self.check(b, a)

        b = """x = filter(lambda x: x%2 == 0, range(10))"""
        a = """x = [x dla x w range(10) jeżeli x%2 == 0]"""
        self.check(b, a)

        # Note the parens around x
        b = """x = filter(lambda (x): x%2 == 0, range(10))"""
        a = """x = [x dla x w range(10) jeżeli x%2 == 0]"""
        self.check(b, a)

        # XXX This (rare) case jest nie supported
##         b = """x = filter(f, 'abc')[0]"""
##         a = """x = list(filter(f, 'abc'))[0]"""
##         self.check(b, a)

    def test_filter_nochange(self):
        a = """b.join(filter(f, 'abc'))"""
        self.unchanged(a)
        a = """(a + foo(5)).join(filter(f, 'abc'))"""
        self.unchanged(a)
        a = """iter(filter(f, 'abc'))"""
        self.unchanged(a)
        a = """list(filter(f, 'abc'))"""
        self.unchanged(a)
        a = """list(filter(f, 'abc'))[0]"""
        self.unchanged(a)
        a = """set(filter(f, 'abc'))"""
        self.unchanged(a)
        a = """set(filter(f, 'abc')).pop()"""
        self.unchanged(a)
        a = """tuple(filter(f, 'abc'))"""
        self.unchanged(a)
        a = """any(filter(f, 'abc'))"""
        self.unchanged(a)
        a = """all(filter(f, 'abc'))"""
        self.unchanged(a)
        a = """sum(filter(f, 'abc'))"""
        self.unchanged(a)
        a = """sorted(filter(f, 'abc'))"""
        self.unchanged(a)
        a = """sorted(filter(f, 'abc'), key=blah)"""
        self.unchanged(a)
        a = """sorted(filter(f, 'abc'), key=blah)[0]"""
        self.unchanged(a)
        a = """enumerate(filter(f, 'abc'))"""
        self.unchanged(a)
        a = """enumerate(filter(f, 'abc'), start=1)"""
        self.unchanged(a)
        a = """dla i w filter(f, 'abc'): dalej"""
        self.unchanged(a)
        a = """[x dla x w filter(f, 'abc')]"""
        self.unchanged(a)
        a = """(x dla x w filter(f, 'abc'))"""
        self.unchanged(a)

    def test_future_builtins(self):
        a = "z future_builtins zaimportuj spam, filter; filter(f, 'ham')"
        self.unchanged(a)

        b = """z future_builtins zaimportuj spam; x = filter(f, 'abc')"""
        a = """z future_builtins zaimportuj spam; x = list(filter(f, 'abc'))"""
        self.check(b, a)

        a = "z future_builtins zaimportuj *; filter(f, 'ham')"
        self.unchanged(a)

klasa Test_map(FixerTestCase):
    fixer = "map"

    def check(self, b, a):
        self.unchanged("z future_builtins zaimportuj map; " + b, a)
        super(Test_map, self).check(b, a)

    def test_prefix_preservation(self):
        b = """x =    map(   f,    'abc'   )"""
        a = """x =    list(map(   f,    'abc'   ))"""
        self.check(b, a)

    def test_trailing_comment(self):
        b = """x = map(f, 'abc')   #   foo"""
        a = """x = list(map(f, 'abc'))   #   foo"""
        self.check(b, a)

    def test_Nic_with_multiple_arguments(self):
        s = """x = map(Nic, a, b, c)"""
        self.warns_unchanged(s, "cannot convert map(Nic, ...) przy "
                             "multiple arguments")

    def test_map_basic(self):
        b = """x = map(f, 'abc')"""
        a = """x = list(map(f, 'abc'))"""
        self.check(b, a)

        b = """x = len(map(f, 'abc', 'def'))"""
        a = """x = len(list(map(f, 'abc', 'def')))"""
        self.check(b, a)

        b = """x = map(Nic, 'abc')"""
        a = """x = list('abc')"""
        self.check(b, a)

        b = """x = map(lambda x: x+1, range(4))"""
        a = """x = [x+1 dla x w range(4)]"""
        self.check(b, a)

        # Note the parens around x
        b = """x = map(lambda (x): x+1, range(4))"""
        a = """x = [x+1 dla x w range(4)]"""
        self.check(b, a)

        b = """
            foo()
            # foo
            map(f, x)
            """
        a = """
            foo()
            # foo
            list(map(f, x))
            """
        self.warns(b, a, "You should use a dla loop here")

        # XXX This (rare) case jest nie supported
##         b = """x = map(f, 'abc')[0]"""
##         a = """x = list(map(f, 'abc'))[0]"""
##         self.check(b, a)

    def test_map_nochange(self):
        a = """b.join(map(f, 'abc'))"""
        self.unchanged(a)
        a = """(a + foo(5)).join(map(f, 'abc'))"""
        self.unchanged(a)
        a = """iter(map(f, 'abc'))"""
        self.unchanged(a)
        a = """list(map(f, 'abc'))"""
        self.unchanged(a)
        a = """list(map(f, 'abc'))[0]"""
        self.unchanged(a)
        a = """set(map(f, 'abc'))"""
        self.unchanged(a)
        a = """set(map(f, 'abc')).pop()"""
        self.unchanged(a)
        a = """tuple(map(f, 'abc'))"""
        self.unchanged(a)
        a = """any(map(f, 'abc'))"""
        self.unchanged(a)
        a = """all(map(f, 'abc'))"""
        self.unchanged(a)
        a = """sum(map(f, 'abc'))"""
        self.unchanged(a)
        a = """sorted(map(f, 'abc'))"""
        self.unchanged(a)
        a = """sorted(map(f, 'abc'), key=blah)"""
        self.unchanged(a)
        a = """sorted(map(f, 'abc'), key=blah)[0]"""
        self.unchanged(a)
        a = """enumerate(map(f, 'abc'))"""
        self.unchanged(a)
        a = """enumerate(map(f, 'abc'), start=1)"""
        self.unchanged(a)
        a = """dla i w map(f, 'abc'): dalej"""
        self.unchanged(a)
        a = """[x dla x w map(f, 'abc')]"""
        self.unchanged(a)
        a = """(x dla x w map(f, 'abc'))"""
        self.unchanged(a)

    def test_future_builtins(self):
        a = "z future_builtins zaimportuj spam, map, eggs; map(f, 'ham')"
        self.unchanged(a)

        b = """z future_builtins zaimportuj spam, eggs; x = map(f, 'abc')"""
        a = """z future_builtins zaimportuj spam, eggs; x = list(map(f, 'abc'))"""
        self.check(b, a)

        a = "z future_builtins zaimportuj *; map(f, 'ham')"
        self.unchanged(a)

klasa Test_zip(FixerTestCase):
    fixer = "zip"

    def check(self, b, a):
        self.unchanged("z future_builtins zaimportuj zip; " + b, a)
        super(Test_zip, self).check(b, a)

    def test_zip_basic(self):
        b = """x = zip(a, b, c)"""
        a = """x = list(zip(a, b, c))"""
        self.check(b, a)

        b = """x = len(zip(a, b))"""
        a = """x = len(list(zip(a, b)))"""
        self.check(b, a)

    def test_zip_nochange(self):
        a = """b.join(zip(a, b))"""
        self.unchanged(a)
        a = """(a + foo(5)).join(zip(a, b))"""
        self.unchanged(a)
        a = """iter(zip(a, b))"""
        self.unchanged(a)
        a = """list(zip(a, b))"""
        self.unchanged(a)
        a = """list(zip(a, b))[0]"""
        self.unchanged(a)
        a = """set(zip(a, b))"""
        self.unchanged(a)
        a = """set(zip(a, b)).pop()"""
        self.unchanged(a)
        a = """tuple(zip(a, b))"""
        self.unchanged(a)
        a = """any(zip(a, b))"""
        self.unchanged(a)
        a = """all(zip(a, b))"""
        self.unchanged(a)
        a = """sum(zip(a, b))"""
        self.unchanged(a)
        a = """sorted(zip(a, b))"""
        self.unchanged(a)
        a = """sorted(zip(a, b), key=blah)"""
        self.unchanged(a)
        a = """sorted(zip(a, b), key=blah)[0]"""
        self.unchanged(a)
        a = """enumerate(zip(a, b))"""
        self.unchanged(a)
        a = """enumerate(zip(a, b), start=1)"""
        self.unchanged(a)
        a = """dla i w zip(a, b): dalej"""
        self.unchanged(a)
        a = """[x dla x w zip(a, b)]"""
        self.unchanged(a)
        a = """(x dla x w zip(a, b))"""
        self.unchanged(a)

    def test_future_builtins(self):
        a = "z future_builtins zaimportuj spam, zip, eggs; zip(a, b)"
        self.unchanged(a)

        b = """z future_builtins zaimportuj spam, eggs; x = zip(a, b)"""
        a = """z future_builtins zaimportuj spam, eggs; x = list(zip(a, b))"""
        self.check(b, a)

        a = "z future_builtins zaimportuj *; zip(a, b)"
        self.unchanged(a)

klasa Test_standarderror(FixerTestCase):
    fixer = "standarderror"

    def test(self):
        b = """x =    StandardError()"""
        a = """x =    Exception()"""
        self.check(b, a)

        b = """x = StandardError(a, b, c)"""
        a = """x = Exception(a, b, c)"""
        self.check(b, a)

        b = """f(2 + StandardError(a, b, c))"""
        a = """f(2 + Exception(a, b, c))"""
        self.check(b, a)

klasa Test_types(FixerTestCase):
    fixer = "types"

    def test_basic_types_convert(self):
        b = """types.StringType"""
        a = """bytes"""
        self.check(b, a)

        b = """types.DictType"""
        a = """dict"""
        self.check(b, a)

        b = """types . IntType"""
        a = """int"""
        self.check(b, a)

        b = """types.ListType"""
        a = """list"""
        self.check(b, a)

        b = """types.LongType"""
        a = """int"""
        self.check(b, a)

        b = """types.NicType"""
        a = """type(Nic)"""
        self.check(b, a)

klasa Test_idioms(FixerTestCase):
    fixer = "idioms"

    def test_while(self):
        b = """dopóki 1: foo()"""
        a = """dopóki Prawda: foo()"""
        self.check(b, a)

        b = """dopóki   1: foo()"""
        a = """dopóki   Prawda: foo()"""
        self.check(b, a)

        b = """
            dopóki 1:
                foo()
            """
        a = """
            dopóki Prawda:
                foo()
            """
        self.check(b, a)

    def test_while_unchanged(self):
        s = """dopóki 11: foo()"""
        self.unchanged(s)

        s = """dopóki 0: foo()"""
        self.unchanged(s)

        s = """dopóki foo(): foo()"""
        self.unchanged(s)

        s = """dopóki []: foo()"""
        self.unchanged(s)

    def test_eq_simple(self):
        b = """type(x) == T"""
        a = """isinstance(x, T)"""
        self.check(b, a)

        b = """jeżeli   type(x) == T: dalej"""
        a = """jeżeli   isinstance(x, T): dalej"""
        self.check(b, a)

    def test_eq_reverse(self):
        b = """T == type(x)"""
        a = """isinstance(x, T)"""
        self.check(b, a)

        b = """jeżeli   T == type(x): dalej"""
        a = """jeżeli   isinstance(x, T): dalej"""
        self.check(b, a)

    def test_eq_expression(self):
        b = """type(x+y) == d.get('T')"""
        a = """isinstance(x+y, d.get('T'))"""
        self.check(b, a)

        b = """type(   x  +  y) == d.get('T')"""
        a = """isinstance(x  +  y, d.get('T'))"""
        self.check(b, a)

    def test_is_simple(self):
        b = """type(x) jest T"""
        a = """isinstance(x, T)"""
        self.check(b, a)

        b = """jeżeli   type(x) jest T: dalej"""
        a = """jeżeli   isinstance(x, T): dalej"""
        self.check(b, a)

    def test_is_reverse(self):
        b = """T jest type(x)"""
        a = """isinstance(x, T)"""
        self.check(b, a)

        b = """jeżeli   T jest type(x): dalej"""
        a = """jeżeli   isinstance(x, T): dalej"""
        self.check(b, a)

    def test_is_expression(self):
        b = """type(x+y) jest d.get('T')"""
        a = """isinstance(x+y, d.get('T'))"""
        self.check(b, a)

        b = """type(   x  +  y) jest d.get('T')"""
        a = """isinstance(x  +  y, d.get('T'))"""
        self.check(b, a)

    def test_is_not_simple(self):
        b = """type(x) jest nie T"""
        a = """not isinstance(x, T)"""
        self.check(b, a)

        b = """jeżeli   type(x) jest nie T: dalej"""
        a = """jeżeli   nie isinstance(x, T): dalej"""
        self.check(b, a)

    def test_is_not_reverse(self):
        b = """T jest nie type(x)"""
        a = """not isinstance(x, T)"""
        self.check(b, a)

        b = """jeżeli   T jest nie type(x): dalej"""
        a = """jeżeli   nie isinstance(x, T): dalej"""
        self.check(b, a)

    def test_is_not_expression(self):
        b = """type(x+y) jest nie d.get('T')"""
        a = """not isinstance(x+y, d.get('T'))"""
        self.check(b, a)

        b = """type(   x  +  y) jest nie d.get('T')"""
        a = """not isinstance(x  +  y, d.get('T'))"""
        self.check(b, a)

    def test_ne_simple(self):
        b = """type(x) != T"""
        a = """not isinstance(x, T)"""
        self.check(b, a)

        b = """jeżeli   type(x) != T: dalej"""
        a = """jeżeli   nie isinstance(x, T): dalej"""
        self.check(b, a)

    def test_ne_reverse(self):
        b = """T != type(x)"""
        a = """not isinstance(x, T)"""
        self.check(b, a)

        b = """jeżeli   T != type(x): dalej"""
        a = """jeżeli   nie isinstance(x, T): dalej"""
        self.check(b, a)

    def test_ne_expression(self):
        b = """type(x+y) != d.get('T')"""
        a = """not isinstance(x+y, d.get('T'))"""
        self.check(b, a)

        b = """type(   x  +  y) != d.get('T')"""
        a = """not isinstance(x  +  y, d.get('T'))"""
        self.check(b, a)

    def test_type_unchanged(self):
        a = """type(x).__name__"""
        self.unchanged(a)

    def test_sort_list_call(self):
        b = """
            v = list(t)
            v.sort()
            foo(v)
            """
        a = """
            v = sorted(t)
            foo(v)
            """
        self.check(b, a)

        b = """
            v = list(foo(b) + d)
            v.sort()
            foo(v)
            """
        a = """
            v = sorted(foo(b) + d)
            foo(v)
            """
        self.check(b, a)

        b = """
            dopóki x:
                v = list(t)
                v.sort()
                foo(v)
            """
        a = """
            dopóki x:
                v = sorted(t)
                foo(v)
            """
        self.check(b, a)

        b = """
            v = list(t)
            # foo
            v.sort()
            foo(v)
            """
        a = """
            v = sorted(t)
            # foo
            foo(v)
            """
        self.check(b, a)

        b = r"""
            v = list(   t)
            v.sort()
            foo(v)
            """
        a = r"""
            v = sorted(   t)
            foo(v)
            """
        self.check(b, a)

        b = r"""
            spróbuj:
                m = list(s)
                m.sort()
            wyjąwszy: dalej
            """

        a = r"""
            spróbuj:
                m = sorted(s)
            wyjąwszy: dalej
            """
        self.check(b, a)

        b = r"""
            spróbuj:
                m = list(s)
                # foo
                m.sort()
            wyjąwszy: dalej
            """

        a = r"""
            spróbuj:
                m = sorted(s)
                # foo
            wyjąwszy: dalej
            """
        self.check(b, a)

        b = r"""
            m = list(s)
            # more comments
            m.sort()"""

        a = r"""
            m = sorted(s)
            # more comments"""
        self.check(b, a)

    def test_sort_simple_expr(self):
        b = """
            v = t
            v.sort()
            foo(v)
            """
        a = """
            v = sorted(t)
            foo(v)
            """
        self.check(b, a)

        b = """
            v = foo(b)
            v.sort()
            foo(v)
            """
        a = """
            v = sorted(foo(b))
            foo(v)
            """
        self.check(b, a)

        b = """
            v = b.keys()
            v.sort()
            foo(v)
            """
        a = """
            v = sorted(b.keys())
            foo(v)
            """
        self.check(b, a)

        b = """
            v = foo(b) + d
            v.sort()
            foo(v)
            """
        a = """
            v = sorted(foo(b) + d)
            foo(v)
            """
        self.check(b, a)

        b = """
            dopóki x:
                v = t
                v.sort()
                foo(v)
            """
        a = """
            dopóki x:
                v = sorted(t)
                foo(v)
            """
        self.check(b, a)

        b = """
            v = t
            # foo
            v.sort()
            foo(v)
            """
        a = """
            v = sorted(t)
            # foo
            foo(v)
            """
        self.check(b, a)

        b = r"""
            v =   t
            v.sort()
            foo(v)
            """
        a = r"""
            v =   sorted(t)
            foo(v)
            """
        self.check(b, a)

    def test_sort_unchanged(self):
        s = """
            v = list(t)
            w.sort()
            foo(w)
            """
        self.unchanged(s)

        s = """
            v = list(t)
            v.sort(u)
            foo(v)
            """
        self.unchanged(s)

klasa Test_basestring(FixerTestCase):
    fixer = "basestring"

    def test_basestring(self):
        b = """isinstance(x, basestring)"""
        a = """isinstance(x, str)"""
        self.check(b, a)

klasa Test_buffer(FixerTestCase):
    fixer = "buffer"

    def test_buffer(self):
        b = """x = buffer(y)"""
        a = """x = memoryview(y)"""
        self.check(b, a)

    def test_slicing(self):
        b = """buffer(y)[4:5]"""
        a = """memoryview(y)[4:5]"""
        self.check(b, a)

klasa Test_future(FixerTestCase):
    fixer = "future"

    def test_future(self):
        b = """z __future__ zaimportuj braces"""
        a = """"""
        self.check(b, a)

        b = """# comment\nz __future__ zaimportuj braces"""
        a = """# comment\n"""
        self.check(b, a)

        b = """z __future__ zaimportuj braces\n# comment"""
        a = """\n# comment"""
        self.check(b, a)

    def test_run_order(self):
        self.assert_runs_after('print')

klasa Test_itertools(FixerTestCase):
    fixer = "itertools"

    def checkall(self, before, after):
        # Because we need to check przy oraz without the itertools prefix
        # oraz on each of the three functions, these loops make it all
        # much easier
        dla i w ('itertools.', ''):
            dla f w ('map', 'filter', 'zip'):
                b = before %(i+'i'+f)
                a = after %(f)
                self.check(b, a)

    def test_0(self):
        # A simple example -- test_1 covers exactly the same thing,
        # but it's nie quite jako clear.
        b = "itertools.izip(a, b)"
        a = "zip(a, b)"
        self.check(b, a)

    def test_1(self):
        b = """%s(f, a)"""
        a = """%s(f, a)"""
        self.checkall(b, a)

    def test_qualified(self):
        b = """itertools.ifilterfalse(a, b)"""
        a = """itertools.filterfalse(a, b)"""
        self.check(b, a)

        b = """itertools.izip_longest(a, b)"""
        a = """itertools.zip_longest(a, b)"""
        self.check(b, a)

    def test_2(self):
        b = """ifilterfalse(a, b)"""
        a = """filterfalse(a, b)"""
        self.check(b, a)

        b = """izip_longest(a, b)"""
        a = """zip_longest(a, b)"""
        self.check(b, a)

    def test_space_1(self):
        b = """    %s(f, a)"""
        a = """    %s(f, a)"""
        self.checkall(b, a)

    def test_space_2(self):
        b = """    itertools.ifilterfalse(a, b)"""
        a = """    itertools.filterfalse(a, b)"""
        self.check(b, a)

        b = """    itertools.izip_longest(a, b)"""
        a = """    itertools.zip_longest(a, b)"""
        self.check(b, a)

    def test_run_order(self):
        self.assert_runs_after('map', 'zip', 'filter')


klasa Test_itertools_imports(FixerTestCase):
    fixer = 'itertools_imports'

    def test_reduced(self):
        b = "z itertools zaimportuj imap, izip, foo"
        a = "z itertools zaimportuj foo"
        self.check(b, a)

        b = "z itertools zaimportuj bar, imap, izip, foo"
        a = "z itertools zaimportuj bar, foo"
        self.check(b, a)

        b = "z itertools zaimportuj chain, imap, izip"
        a = "z itertools zaimportuj chain"
        self.check(b, a)

    def test_comments(self):
        b = "#foo\nz itertools zaimportuj imap, izip"
        a = "#foo\n"
        self.check(b, a)

    def test_none(self):
        b = "z itertools zaimportuj imap, izip"
        a = ""
        self.check(b, a)

        b = "z itertools zaimportuj izip"
        a = ""
        self.check(b, a)

    def test_import_as(self):
        b = "z itertools zaimportuj izip, bar jako bang, imap"
        a = "z itertools zaimportuj bar jako bang"
        self.check(b, a)

        b = "z itertools zaimportuj izip jako _zip, imap, bar"
        a = "z itertools zaimportuj bar"
        self.check(b, a)

        b = "z itertools zaimportuj imap jako _map"
        a = ""
        self.check(b, a)

        b = "z itertools zaimportuj imap jako _map, izip jako _zip"
        a = ""
        self.check(b, a)

        s = "z itertools zaimportuj bar jako bang"
        self.unchanged(s)

    def test_ifilter_and_zip_longest(self):
        dla name w "filterfalse", "zip_longest":
            b = "z itertools zaimportuj i%s" % (name,)
            a = "z itertools zaimportuj %s" % (name,)
            self.check(b, a)

            b = "z itertools zaimportuj imap, i%s, foo" % (name,)
            a = "z itertools zaimportuj %s, foo" % (name,)
            self.check(b, a)

            b = "z itertools zaimportuj bar, i%s, foo" % (name,)
            a = "z itertools zaimportuj bar, %s, foo" % (name,)
            self.check(b, a)

    def test_import_star(self):
        s = "z itertools zaimportuj *"
        self.unchanged(s)


    def test_unchanged(self):
        s = "z itertools zaimportuj foo"
        self.unchanged(s)


klasa Test_import(FixerTestCase):
    fixer = "import"

    def setUp(self):
        super(Test_import, self).setUp()
        # Need to replace fix_import's exists method
        # so we can check that it's doing the right thing
        self.files_checked = []
        self.present_files = set()
        self.always_exists = Prawda
        def fake_exists(name):
            self.files_checked.append(name)
            zwróć self.always_exists albo (name w self.present_files)

        z lib2to3.fixes zaimportuj fix_import
        fix_import.exists = fake_exists

    def tearDown(self):
        z lib2to3.fixes zaimportuj fix_import
        fix_import.exists = os.path.exists

    def check_both(self, b, a):
        self.always_exists = Prawda
        super(Test_import, self).check(b, a)
        self.always_exists = Nieprawda
        super(Test_import, self).unchanged(b)

    def test_files_checked(self):
        def p(path):
            # Takes a unix path oraz returns a path przy correct separators
            zwróć os.path.pathsep.join(path.split("/"))

        self.always_exists = Nieprawda
        self.present_files = set(['__init__.py'])
        expected_extensions = ('.py', os.path.sep, '.pyc', '.so', '.sl', '.pyd')
        names_to_test = (p("/spam/eggs.py"), "ni.py", p("../../shrubbery.py"))

        dla name w names_to_test:
            self.files_checked = []
            self.filename = name
            self.unchanged("zaimportuj jam")

            jeżeli os.path.dirname(name):
                name = os.path.dirname(name) + '/jam'
            inaczej:
                name = 'jam'
            expected_checks = set(name + ext dla ext w expected_extensions)
            expected_checks.add("__init__.py")

            self.assertEqual(set(self.files_checked), expected_checks)

    def test_not_in_package(self):
        s = "zaimportuj bar"
        self.always_exists = Nieprawda
        self.present_files = set(["bar.py"])
        self.unchanged(s)

    def test_with_absolute_import_enabled(self):
        s = "z __future__ zaimportuj absolute_import\nzaimportuj bar"
        self.always_exists = Nieprawda
        self.present_files = set(["__init__.py", "bar.py"])
        self.unchanged(s)

    def test_in_package(self):
        b = "zaimportuj bar"
        a = "z . zaimportuj bar"
        self.always_exists = Nieprawda
        self.present_files = set(["__init__.py", "bar.py"])
        self.check(b, a)

    def test_import_from_package(self):
        b = "zaimportuj bar"
        a = "z . zaimportuj bar"
        self.always_exists = Nieprawda
        self.present_files = set(["__init__.py", "bar" + os.path.sep])
        self.check(b, a)

    def test_already_relative_import(self):
        s = "z . zaimportuj bar"
        self.unchanged(s)

    def test_comments_and_indent(self):
        b = "zaimportuj bar # Foo"
        a = "z . zaimportuj bar # Foo"
        self.check(b, a)

    def test_from(self):
        b = "z foo zaimportuj bar, baz"
        a = "z .foo zaimportuj bar, baz"
        self.check_both(b, a)

        b = "z foo zaimportuj bar"
        a = "z .foo zaimportuj bar"
        self.check_both(b, a)

        b = "z foo zaimportuj (bar, baz)"
        a = "z .foo zaimportuj (bar, baz)"
        self.check_both(b, a)

    def test_dotted_from(self):
        b = "z green.eggs zaimportuj ham"
        a = "z .green.eggs zaimportuj ham"
        self.check_both(b, a)

    def test_from_as(self):
        b = "z green.eggs zaimportuj ham jako spam"
        a = "z .green.eggs zaimportuj ham jako spam"
        self.check_both(b, a)

    def test_import(self):
        b = "zaimportuj foo"
        a = "z . zaimportuj foo"
        self.check_both(b, a)

        b = "zaimportuj foo, bar"
        a = "z . zaimportuj foo, bar"
        self.check_both(b, a)

        b = "zaimportuj foo, bar, x"
        a = "z . zaimportuj foo, bar, x"
        self.check_both(b, a)

        b = "zaimportuj x, y, z"
        a = "z . zaimportuj x, y, z"
        self.check_both(b, a)

    def test_import_as(self):
        b = "zaimportuj foo jako x"
        a = "z . zaimportuj foo jako x"
        self.check_both(b, a)

        b = "zaimportuj a jako b, b jako c, c jako d"
        a = "z . zaimportuj a jako b, b jako c, c jako d"
        self.check_both(b, a)

    def test_local_and_absolute(self):
        self.always_exists = Nieprawda
        self.present_files = set(["foo.py", "__init__.py"])

        s = "zaimportuj foo, bar"
        self.warns_unchanged(s, "absolute oraz local imports together")

    def test_dotted_import(self):
        b = "zaimportuj foo.bar"
        a = "z . zaimportuj foo.bar"
        self.check_both(b, a)

    def test_dotted_import_as(self):
        b = "zaimportuj foo.bar jako bang"
        a = "z . zaimportuj foo.bar jako bang"
        self.check_both(b, a)

    def test_prefix(self):
        b = """
        # prefix
        zaimportuj foo.bar
        """
        a = """
        # prefix
        z . zaimportuj foo.bar
        """
        self.check_both(b, a)


klasa Test_set_literal(FixerTestCase):

    fixer = "set_literal"

    def test_basic(self):
        b = """set([1, 2, 3])"""
        a = """{1, 2, 3}"""
        self.check(b, a)

        b = """set((1, 2, 3))"""
        a = """{1, 2, 3}"""
        self.check(b, a)

        b = """set((1,))"""
        a = """{1}"""
        self.check(b, a)

        b = """set([1])"""
        self.check(b, a)

        b = """set((a, b))"""
        a = """{a, b}"""
        self.check(b, a)

        b = """set([a, b])"""
        self.check(b, a)

        b = """set((a*234, f(args=23)))"""
        a = """{a*234, f(args=23)}"""
        self.check(b, a)

        b = """set([a*23, f(23)])"""
        a = """{a*23, f(23)}"""
        self.check(b, a)

        b = """set([a-234**23])"""
        a = """{a-234**23}"""
        self.check(b, a)

    def test_listcomps(self):
        b = """set([x dla x w y])"""
        a = """{x dla x w y}"""
        self.check(b, a)

        b = """set([x dla x w y jeżeli x == m])"""
        a = """{x dla x w y jeżeli x == m}"""
        self.check(b, a)

        b = """set([x dla x w y dla a w b])"""
        a = """{x dla x w y dla a w b}"""
        self.check(b, a)

        b = """set([f(x) - 23 dla x w y])"""
        a = """{f(x) - 23 dla x w y}"""
        self.check(b, a)

    def test_whitespace(self):
        b = """set( [1, 2])"""
        a = """{1, 2}"""
        self.check(b, a)

        b = """set([1 ,  2])"""
        a = """{1 ,  2}"""
        self.check(b, a)

        b = """set([ 1 ])"""
        a = """{ 1 }"""
        self.check(b, a)

        b = """set( [1] )"""
        a = """{1}"""
        self.check(b, a)

        b = """set([  1,  2  ])"""
        a = """{  1,  2  }"""
        self.check(b, a)

        b = """set([x  dla x w y ])"""
        a = """{x  dla x w y }"""
        self.check(b, a)

        b = """set(
                   [1, 2]
               )
            """
        a = """{1, 2}\n"""
        self.check(b, a)

    def test_comments(self):
        b = """set((1, 2)) # Hi"""
        a = """{1, 2} # Hi"""
        self.check(b, a)

        # This isn't optimal behavior, but the fixer jest optional.
        b = """
            # Foo
            set( # Bar
               (1, 2)
            )
            """
        a = """
            # Foo
            {1, 2}
            """
        self.check(b, a)

    def test_unchanged(self):
        s = """set()"""
        self.unchanged(s)

        s = """set(a)"""
        self.unchanged(s)

        s = """set(a, b, c)"""
        self.unchanged(s)

        # Don't transform generators because they might have to be lazy.
        s = """set(x dla x w y)"""
        self.unchanged(s)

        s = """set(x dla x w y jeżeli z)"""
        self.unchanged(s)

        s = """set(a*823-23**2 + f(23))"""
        self.unchanged(s)


klasa Test_sys_exc(FixerTestCase):
    fixer = "sys_exc"

    def test_0(self):
        b = "sys.exc_type"
        a = "sys.exc_info()[0]"
        self.check(b, a)

    def test_1(self):
        b = "sys.exc_value"
        a = "sys.exc_info()[1]"
        self.check(b, a)

    def test_2(self):
        b = "sys.exc_traceback"
        a = "sys.exc_info()[2]"
        self.check(b, a)

    def test_3(self):
        b = "sys.exc_type # Foo"
        a = "sys.exc_info()[0] # Foo"
        self.check(b, a)

    def test_4(self):
        b = "sys.  exc_type"
        a = "sys.  exc_info()[0]"
        self.check(b, a)

    def test_5(self):
        b = "sys  .exc_type"
        a = "sys  .exc_info()[0]"
        self.check(b, a)


klasa Test_paren(FixerTestCase):
    fixer = "paren"

    def test_0(self):
        b = """[i dla i w 1, 2 ]"""
        a = """[i dla i w (1, 2) ]"""
        self.check(b, a)

    def test_1(self):
        b = """[i dla i w 1, 2, ]"""
        a = """[i dla i w (1, 2,) ]"""
        self.check(b, a)

    def test_2(self):
        b = """[i dla i  w     1, 2 ]"""
        a = """[i dla i  w     (1, 2) ]"""
        self.check(b, a)

    def test_3(self):
        b = """[i dla i w 1, 2 jeżeli i]"""
        a = """[i dla i w (1, 2) jeżeli i]"""
        self.check(b, a)

    def test_4(self):
        b = """[i dla i w 1,    2    ]"""
        a = """[i dla i w (1,    2)    ]"""
        self.check(b, a)

    def test_5(self):
        b = """(i dla i w 1, 2)"""
        a = """(i dla i w (1, 2))"""
        self.check(b, a)

    def test_6(self):
        b = """(i dla i w 1   ,2   jeżeli i)"""
        a = """(i dla i w (1   ,2)   jeżeli i)"""
        self.check(b, a)

    def test_unchanged_0(self):
        s = """[i dla i w (1, 2)]"""
        self.unchanged(s)

    def test_unchanged_1(self):
        s = """[i dla i w foo()]"""
        self.unchanged(s)

    def test_unchanged_2(self):
        s = """[i dla i w (1, 2) jeżeli nothing]"""
        self.unchanged(s)

    def test_unchanged_3(self):
        s = """(i dla i w (1, 2))"""
        self.unchanged(s)

    def test_unchanged_4(self):
        s = """[i dla i w m]"""
        self.unchanged(s)

klasa Test_metaclass(FixerTestCase):

    fixer = 'metaclass'

    def test_unchanged(self):
        self.unchanged("class X(): dalej")
        self.unchanged("class X(object): dalej")
        self.unchanged("class X(object1, object2): dalej")
        self.unchanged("class X(object1, object2, object3): dalej")
        self.unchanged("class X(metaclass=Meta): dalej")
        self.unchanged("class X(b, arg=23, metclass=Meta): dalej")
        self.unchanged("class X(b, arg=23, metaclass=Meta, other=42): dalej")

        s = """
        klasa X:
            def __metaclass__(self): dalej
        """
        self.unchanged(s)

        s = """
        klasa X:
            a[23] = 74
        """
        self.unchanged(s)

    def test_comments(self):
        b = """
        klasa X:
            # hi
            __metaclass__ = AppleMeta
        """
        a = """
        klasa X(metaclass=AppleMeta):
            # hi
            dalej
        """
        self.check(b, a)

        b = """
        klasa X:
            __metaclass__ = Meta
            # Bedtime!
        """
        a = """
        klasa X(metaclass=Meta):
            dalej
            # Bedtime!
        """
        self.check(b, a)

    def test_meta(self):
        # no-parent class, odd body
        b = """
        klasa X():
            __metaclass__ = Q
            dalej
        """
        a = """
        klasa X(metaclass=Q):
            dalej
        """
        self.check(b, a)

        # one parent class, no body
        b = """class X(object): __metaclass__ = Q"""
        a = """class X(object, metaclass=Q): dalej"""
        self.check(b, a)


        # one parent, simple body
        b = """
        klasa X(object):
            __metaclass__ = Meta
            bar = 7
        """
        a = """
        klasa X(object, metaclass=Meta):
            bar = 7
        """
        self.check(b, a)

        b = """
        klasa X:
            __metaclass__ = Meta; x = 4; g = 23
        """
        a = """
        klasa X(metaclass=Meta):
            x = 4; g = 23
        """
        self.check(b, a)

        # one parent, simple body, __metaclass__ last
        b = """
        klasa X(object):
            bar = 7
            __metaclass__ = Meta
        """
        a = """
        klasa X(object, metaclass=Meta):
            bar = 7
        """
        self.check(b, a)

        # redefining __metaclass__
        b = """
        klasa X():
            __metaclass__ = A
            __metaclass__ = B
            bar = 7
        """
        a = """
        klasa X(metaclass=B):
            bar = 7
        """
        self.check(b, a)

        # multiple inheritance, simple body
        b = """
        klasa X(clsA, clsB):
            __metaclass__ = Meta
            bar = 7
        """
        a = """
        klasa X(clsA, clsB, metaclass=Meta):
            bar = 7
        """
        self.check(b, a)

        # keywords w the klasa statement
        b = """class m(a, arg=23): __metaclass__ = Meta"""
        a = """class m(a, arg=23, metaclass=Meta): dalej"""
        self.check(b, a)

        b = """
        klasa X(expression(2 + 4)):
            __metaclass__ = Meta
        """
        a = """
        klasa X(expression(2 + 4), metaclass=Meta):
            dalej
        """
        self.check(b, a)

        b = """
        klasa X(expression(2 + 4), x**4):
            __metaclass__ = Meta
        """
        a = """
        klasa X(expression(2 + 4), x**4, metaclass=Meta):
            dalej
        """
        self.check(b, a)

        b = """
        klasa X:
            __metaclass__ = Meta
            save.py = 23
        """
        a = """
        klasa X(metaclass=Meta):
            save.py = 23
        """
        self.check(b, a)


klasa Test_getcwdu(FixerTestCase):

    fixer = 'getcwdu'

    def test_basic(self):
        b = """os.getcwdu"""
        a = """os.getcwd"""
        self.check(b, a)

        b = """os.getcwdu()"""
        a = """os.getcwd()"""
        self.check(b, a)

        b = """meth = os.getcwdu"""
        a = """meth = os.getcwd"""
        self.check(b, a)

        b = """os.getcwdu(args)"""
        a = """os.getcwd(args)"""
        self.check(b, a)

    def test_comment(self):
        b = """os.getcwdu() # Foo"""
        a = """os.getcwd() # Foo"""
        self.check(b, a)

    def test_unchanged(self):
        s = """os.getcwd()"""
        self.unchanged(s)

        s = """getcwdu()"""
        self.unchanged(s)

        s = """os.getcwdb()"""
        self.unchanged(s)

    def test_indentation(self):
        b = """
            jeżeli 1:
                os.getcwdu()
            """
        a = """
            jeżeli 1:
                os.getcwd()
            """
        self.check(b, a)

    def test_multilation(self):
        b = """os .getcwdu()"""
        a = """os .getcwd()"""
        self.check(b, a)

        b = """os.  getcwdu"""
        a = """os.  getcwd"""
        self.check(b, a)

        b = """os.getcwdu (  )"""
        a = """os.getcwd (  )"""
        self.check(b, a)


klasa Test_operator(FixerTestCase):

    fixer = "operator"

    def test_operator_isCallable(self):
        b = "operator.isCallable(x)"
        a = "hasattr(x, '__call__')"
        self.check(b, a)

    def test_operator_sequenceIncludes(self):
        b = "operator.sequenceIncludes(x, y)"
        a = "operator.contains(x, y)"
        self.check(b, a)

        b = "operator .sequenceIncludes(x, y)"
        a = "operator .contains(x, y)"
        self.check(b, a)

        b = "operator.  sequenceIncludes(x, y)"
        a = "operator.  contains(x, y)"
        self.check(b, a)

    def test_operator_isSequenceType(self):
        b = "operator.isSequenceType(x)"
        a = "zaimportuj collections\nisinstance(x, collections.Sequence)"
        self.check(b, a)

    def test_operator_isMappingType(self):
        b = "operator.isMappingType(x)"
        a = "zaimportuj collections\nisinstance(x, collections.Mapping)"
        self.check(b, a)

    def test_operator_isNumberType(self):
        b = "operator.isNumberType(x)"
        a = "zaimportuj numbers\nisinstance(x, numbers.Number)"
        self.check(b, a)

    def test_operator_repeat(self):
        b = "operator.repeat(x, n)"
        a = "operator.mul(x, n)"
        self.check(b, a)

        b = "operator .repeat(x, n)"
        a = "operator .mul(x, n)"
        self.check(b, a)

        b = "operator.  repeat(x, n)"
        a = "operator.  mul(x, n)"
        self.check(b, a)

    def test_operator_irepeat(self):
        b = "operator.irepeat(x, n)"
        a = "operator.imul(x, n)"
        self.check(b, a)

        b = "operator .irepeat(x, n)"
        a = "operator .imul(x, n)"
        self.check(b, a)

        b = "operator.  irepeat(x, n)"
        a = "operator.  imul(x, n)"
        self.check(b, a)

    def test_bare_isCallable(self):
        s = "isCallable(x)"
        t = "You should use 'hasattr(x, '__call__')' here."
        self.warns_unchanged(s, t)

    def test_bare_sequenceIncludes(self):
        s = "sequenceIncludes(x, y)"
        t = "You should use 'operator.contains(x, y)' here."
        self.warns_unchanged(s, t)

    def test_bare_operator_isSequenceType(self):
        s = "isSequenceType(z)"
        t = "You should use 'isinstance(z, collections.Sequence)' here."
        self.warns_unchanged(s, t)

    def test_bare_operator_isMappingType(self):
        s = "isMappingType(x)"
        t = "You should use 'isinstance(x, collections.Mapping)' here."
        self.warns_unchanged(s, t)

    def test_bare_operator_isNumberType(self):
        s = "isNumberType(y)"
        t = "You should use 'isinstance(y, numbers.Number)' here."
        self.warns_unchanged(s, t)

    def test_bare_operator_repeat(self):
        s = "repeat(x, n)"
        t = "You should use 'operator.mul(x, n)' here."
        self.warns_unchanged(s, t)

    def test_bare_operator_irepeat(self):
        s = "irepeat(y, 187)"
        t = "You should use 'operator.imul(y, 187)' here."
        self.warns_unchanged(s, t)


klasa Test_exitfunc(FixerTestCase):

    fixer = "exitfunc"

    def test_simple(self):
        b = """
            zaimportuj sys
            sys.exitfunc = my_atexit
            """
        a = """
            zaimportuj sys
            zaimportuj atexit
            atexit.register(my_atexit)
            """
        self.check(b, a)

    def test_names_import(self):
        b = """
            zaimportuj sys, crumbs
            sys.exitfunc = my_func
            """
        a = """
            zaimportuj sys, crumbs, atexit
            atexit.register(my_func)
            """
        self.check(b, a)

    def test_complex_expression(self):
        b = """
            zaimportuj sys
            sys.exitfunc = do(d)/a()+complex(f=23, g=23)*expression
            """
        a = """
            zaimportuj sys
            zaimportuj atexit
            atexit.register(do(d)/a()+complex(f=23, g=23)*expression)
            """
        self.check(b, a)

    def test_comments(self):
        b = """
            zaimportuj sys # Foo
            sys.exitfunc = f # Blah
            """
        a = """
            zaimportuj sys
            zaimportuj atexit # Foo
            atexit.register(f) # Blah
            """
        self.check(b, a)

        b = """
            zaimportuj apples, sys, crumbs, larry # Pleasant comments
            sys.exitfunc = func
            """
        a = """
            zaimportuj apples, sys, crumbs, larry, atexit # Pleasant comments
            atexit.register(func)
            """
        self.check(b, a)

    def test_in_a_function(self):
        b = """
            zaimportuj sys
            def f():
                sys.exitfunc = func
            """
        a = """
            zaimportuj sys
            zaimportuj atexit
            def f():
                atexit.register(func)
             """
        self.check(b, a)

    def test_no_sys_import(self):
        b = """sys.exitfunc = f"""
        a = """atexit.register(f)"""
        msg = ("Can't find sys import; Please add an atexit zaimportuj at the "
            "top of your file.")
        self.warns(b, a, msg)


    def test_unchanged(self):
        s = """f(sys.exitfunc)"""
        self.unchanged(s)


klasa Test_asserts(FixerTestCase):

    fixer = "asserts"

    def test_deprecated_names(self):
        tests = [
            ('self.assert_(Prawda)', 'self.assertPrawda(Prawda)'),
            ('self.assertEquals(2, 2)', 'self.assertEqual(2, 2)'),
            ('self.assertNotEquals(2, 3)', 'self.assertNotEqual(2, 3)'),
            ('self.assertAlmostEquals(2, 3)', 'self.assertAlmostEqual(2, 3)'),
            ('self.assertNotAlmostEquals(2, 8)', 'self.assertNotAlmostEqual(2, 8)'),
            ('self.failUnlessEqual(2, 2)', 'self.assertEqual(2, 2)'),
            ('self.failIfEqual(2, 3)', 'self.assertNotEqual(2, 3)'),
            ('self.failUnlessAlmostEqual(2, 3)', 'self.assertAlmostEqual(2, 3)'),
            ('self.failIfAlmostEqual(2, 8)', 'self.assertNotAlmostEqual(2, 8)'),
            ('self.failUnless(Prawda)', 'self.assertPrawda(Prawda)'),
            ('self.failUnlessRaises(foo)', 'self.assertRaises(foo)'),
            ('self.failIf(Nieprawda)', 'self.assertNieprawda(Nieprawda)'),
        ]
        dla b, a w tests:
            self.check(b, a)

    def test_variants(self):
        b = 'eq = self.assertEquals'
        a = 'eq = self.assertEqual'
        self.check(b, a)
        b = 'self.assertEquals(2, 3, msg="fail")'
        a = 'self.assertEqual(2, 3, msg="fail")'
        self.check(b, a)
        b = 'self.assertEquals(2, 3, msg="fail") # foo'
        a = 'self.assertEqual(2, 3, msg="fail") # foo'
        self.check(b, a)
        b = 'self.assertEquals (2, 3)'
        a = 'self.assertEqual (2, 3)'
        self.check(b, a)
        b = '  self.assertEquals (2, 3)'
        a = '  self.assertEqual (2, 3)'
        self.check(b, a)
        b = 'przy self.failUnlessRaises(Explosion): explode()'
        a = 'przy self.assertRaises(Explosion): explode()'
        self.check(b, a)
        b = 'przy self.failUnlessRaises(Explosion) jako cm: explode()'
        a = 'przy self.assertRaises(Explosion) jako cm: explode()'
        self.check(b, a)

    def test_unchanged(self):
        self.unchanged('self.assertEqualsOnSaturday')
        self.unchanged('self.assertEqualsOnSaturday(3, 5)')
