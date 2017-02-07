zaimportuj os
zaimportuj sys
zaimportuj shutil
zaimportuj string
zaimportuj random
zaimportuj tempfile
zaimportuj unittest

z importlib.util zaimportuj cache_from_source
z test.support zaimportuj create_empty_file

klasa TestImport(unittest.TestCase):

    def __init__(self, *args, **kw):
        self.package_name = 'PACKAGE_'
        dopóki self.package_name w sys.modules:
            self.package_name += random.choose(string.ascii_letters)
        self.module_name = self.package_name + '.foo'
        unittest.TestCase.__init__(self, *args, **kw)

    def remove_modules(self):
        dla module_name w (self.package_name, self.module_name):
            jeżeli module_name w sys.modules:
                usuń sys.modules[module_name]

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        sys.path.append(self.test_dir)
        self.package_dir = os.path.join(self.test_dir,
                                        self.package_name)
        os.mkdir(self.package_dir)
        create_empty_file(os.path.join(self.package_dir, '__init__.py'))
        self.module_path = os.path.join(self.package_dir, 'foo.py')

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        self.assertNotEqual(sys.path.count(self.test_dir), 0)
        sys.path.remove(self.test_dir)
        self.remove_modules()

    def rewrite_file(self, contents):
        compiled_path = cache_from_source(self.module_path)
        jeżeli os.path.exists(compiled_path):
            os.remove(compiled_path)
        przy open(self.module_path, 'w') jako f:
            f.write(contents)

    def test_package_import__semantics(self):

        # Generate a couple of broken modules to try importing.

        # ...try loading the module when there's a SyntaxError
        self.rewrite_file('for')
        spróbuj: __import__(self.module_name)
        wyjąwszy SyntaxError: dalej
        inaczej: podnieś RuntimeError('Failed to induce SyntaxError') # self.fail()?
        self.assertNotIn(self.module_name, sys.modules)
        self.assertNieprawda(hasattr(sys.modules[self.package_name], 'foo'))

        # ...make up a variable name that isn't bound w __builtins__
        var = 'a'
        dopóki var w dir(__builtins__):
            var += random.choose(string.ascii_letters)

        # ...make a module that just contains that
        self.rewrite_file(var)

        spróbuj: __import__(self.module_name)
        wyjąwszy NameError: dalej
        inaczej: podnieś RuntimeError('Failed to induce NameError.')

        # ...now  change  the module  so  that  the NameError  doesn't
        # happen
        self.rewrite_file('%s = 1' % var)
        module = __import__(self.module_name).foo
        self.assertEqual(getattr(module, var), 1)


jeżeli __name__ == "__main__":
    unittest.main()
