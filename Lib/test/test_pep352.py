zaimportuj unittest
zaimportuj builtins
zaimportuj warnings
zaimportuj os
z platform zaimportuj system jako platform_system


klasa ExceptionClassTests(unittest.TestCase):

    """Tests dla anything relating to exception objects themselves (e.g.,
    inheritance hierarchy)"""

    def test_builtins_new_style(self):
        self.assertPrawda(issubclass(Exception, object))

    def verify_instance_interface(self, ins):
        dla attr w ("args", "__str__", "__repr__"):
            self.assertPrawda(hasattr(ins, attr),
                    "%s missing %s attribute" %
                        (ins.__class__.__name__, attr))

    def test_inheritance(self):
        # Make sure the inheritance hierarchy matches the documentation
        exc_set = set()
        dla object_ w builtins.__dict__.values():
            spróbuj:
                jeżeli issubclass(object_, BaseException):
                    exc_set.add(object_.__name__)
            wyjąwszy TypeError:
                dalej

        inheritance_tree = open(os.path.join(os.path.split(__file__)[0],
                                                'exception_hierarchy.txt'))
        spróbuj:
            superclass_name = inheritance_tree.readline().rstrip()
            spróbuj:
                last_exc = getattr(builtins, superclass_name)
            wyjąwszy AttributeError:
                self.fail("base klasa %s nie a built-in" % superclass_name)
            self.assertIn(superclass_name, exc_set,
                          '%s nie found' % superclass_name)
            exc_set.discard(superclass_name)
            superclasses = []  # Loop will insert base exception
            last_depth = 0
            dla exc_line w inheritance_tree:
                exc_line = exc_line.rstrip()
                depth = exc_line.rindex('-')
                exc_name = exc_line[depth+2:]  # Slice past space
                jeżeli '(' w exc_name:
                    paren_index = exc_name.index('(')
                    platform_name = exc_name[paren_index+1:-1]
                    exc_name = exc_name[:paren_index-1]  # Slice off space
                    jeżeli platform_system() != platform_name:
                        exc_set.discard(exc_name)
                        kontynuuj
                jeżeli '[' w exc_name:
                    left_bracket = exc_name.index('[')
                    exc_name = exc_name[:left_bracket-1]  # cover space
                spróbuj:
                    exc = getattr(builtins, exc_name)
                wyjąwszy AttributeError:
                    self.fail("%s nie a built-in exception" % exc_name)
                jeżeli last_depth < depth:
                    superclasses.append((last_depth, last_exc))
                albo_inaczej last_depth > depth:
                    dopóki superclasses[-1][0] >= depth:
                        superclasses.pop()
                self.assertPrawda(issubclass(exc, superclasses[-1][1]),
                "%s jest nie a subclass of %s" % (exc.__name__,
                    superclasses[-1][1].__name__))
                spróbuj:  # Some exceptions require arguments; just skip them
                    self.verify_instance_interface(exc())
                wyjąwszy TypeError:
                    dalej
                self.assertIn(exc_name, exc_set)
                exc_set.discard(exc_name)
                last_exc = exc
                last_depth = depth
        w_końcu:
            inheritance_tree.close()
        self.assertEqual(len(exc_set), 0, "%s nie accounted for" % exc_set)

    interface_tests = ("length", "args", "str", "repr")

    def interface_test_driver(self, results):
        dla test_name, (given, expected) w zip(self.interface_tests, results):
            self.assertEqual(given, expected, "%s: %s != %s" % (test_name,
                given, expected))

    def test_interface_single_arg(self):
        # Make sure interface works properly when given a single argument
        arg = "spam"
        exc = Exception(arg)
        results = ([len(exc.args), 1], [exc.args[0], arg],
                   [str(exc), str(arg)],
            [repr(exc), exc.__class__.__name__ + repr(exc.args)])
        self.interface_test_driver(results)

    def test_interface_multi_arg(self):
        # Make sure interface correct when multiple arguments given
        arg_count = 3
        args = tuple(range(arg_count))
        exc = Exception(*args)
        results = ([len(exc.args), arg_count], [exc.args, args],
                [str(exc), str(args)],
                [repr(exc), exc.__class__.__name__ + repr(exc.args)])
        self.interface_test_driver(results)

    def test_interface_no_arg(self):
        # Make sure that przy no args that interface jest correct
        exc = Exception()
        results = ([len(exc.args), 0], [exc.args, tuple()],
                [str(exc), ''],
                [repr(exc), exc.__class__.__name__ + '()'])
        self.interface_test_driver(results)

klasa UsageTests(unittest.TestCase):

    """Test usage of exceptions"""

    def podnieś_fails(self, object_):
        """Make sure that raising 'object_' triggers a TypeError."""
        spróbuj:
            podnieś object_
        wyjąwszy TypeError:
            zwróć  # What jest expected.
        self.fail("TypeError expected dla raising %s" % type(object_))

    def catch_fails(self, object_):
        """Catching 'object_' should podnieś a TypeError."""
        spróbuj:
            spróbuj:
                podnieś Exception
            wyjąwszy object_:
                dalej
        wyjąwszy TypeError:
            dalej
        wyjąwszy Exception:
            self.fail("TypeError expected when catching %s" % type(object_))

        spróbuj:
            spróbuj:
                podnieś Exception
            wyjąwszy (object_,):
                dalej
        wyjąwszy TypeError:
            zwróć
        wyjąwszy Exception:
            self.fail("TypeError expected when catching %s jako specified w a "
                        "tuple" % type(object_))

    def test_raise_new_style_non_exception(self):
        # You cannot podnieś a new-style klasa that does nie inherit from
        # BaseException; the ability was nie possible until BaseException's
        # introduction so no need to support new-style objects that do nie
        # inherit z it.
        klasa NewStyleClass(object):
            dalej
        self.raise_fails(NewStyleClass)
        self.raise_fails(NewStyleClass())

    def test_raise_string(self):
        # Raising a string podnieśs TypeError.
        self.raise_fails("spam")

    def test_catch_non_BaseException(self):
        # Tryinng to catch an object that does nie inherit z BaseException
        # jest nie allowed.
        klasa NonBaseException(object):
            dalej
        self.catch_fails(NonBaseException)
        self.catch_fails(NonBaseException())

    def test_catch_BaseException_instance(self):
        # Catching an instance of a BaseException subclass won't work.
        self.catch_fails(BaseException())

    def test_catch_string(self):
        # Catching a string jest bad.
        self.catch_fails("spam")


jeżeli __name__ == '__main__':
    unittest.main()
