""" Tests dla the linecache module """

zaimportuj linecache
zaimportuj unittest
zaimportuj os.path
z test zaimportuj support


FILENAME = linecache.__file__
NONEXISTENT_FILENAME = FILENAME + '.missing'
INVALID_NAME = '!@$)(!@#_1'
EMPTY = ''
TESTS = 'inspect_fodder inspect_fodder2 mapping_tests'
TESTS = TESTS.split()
TEST_PATH = os.path.dirname(__file__)
MODULES = "linecache abc".split()
MODULE_PATH = os.path.dirname(FILENAME)

SOURCE_1 = '''
" Docstring "

def function():
    zwróć result

'''

SOURCE_2 = '''
def f():
    zwróć 1 + 1

a = f()

'''

SOURCE_3 = '''
def f():
    zwróć 3''' # No ending newline


klasa LineCacheTests(unittest.TestCase):

    def test_getline(self):
        getline = linecache.getline

        # Bad values dla line number should zwróć an empty string
        self.assertEqual(getline(FILENAME, 2**15), EMPTY)
        self.assertEqual(getline(FILENAME, -1), EMPTY)

        # Float values currently podnieś TypeError, should it?
        self.assertRaises(TypeError, getline, FILENAME, 1.1)

        # Bad filenames should zwróć an empty string
        self.assertEqual(getline(EMPTY, 1), EMPTY)
        self.assertEqual(getline(INVALID_NAME, 1), EMPTY)

        # Check whether lines correspond to those z file iteration
        dla entry w TESTS:
            filename = os.path.join(TEST_PATH, entry) + '.py'
            przy open(filename) jako file:
                dla index, line w enumerate(file):
                    self.assertEqual(line, getline(filename, index + 1))

        # Check module loading
        dla entry w MODULES:
            filename = os.path.join(MODULE_PATH, entry) + '.py'
            przy open(filename) jako file:
                dla index, line w enumerate(file):
                    self.assertEqual(line, getline(filename, index + 1))

        # Check that bogus data isn't returned (issue #1309567)
        empty = linecache.getlines('a/b/c/__init__.py')
        self.assertEqual(empty, [])

    def test_no_ending_newline(self):
        self.addCleanup(support.unlink, support.TESTFN)
        przy open(support.TESTFN, "w") jako fp:
            fp.write(SOURCE_3)
        lines = linecache.getlines(support.TESTFN)
        self.assertEqual(lines, ["\n", "def f():\n", "    zwróć 3\n"])

    def test_clearcache(self):
        cached = []
        dla entry w TESTS:
            filename = os.path.join(TEST_PATH, entry) + '.py'
            cached.append(filename)
            linecache.getline(filename, 1)

        # Are all files cached?
        cached_empty = [fn dla fn w cached jeżeli fn nie w linecache.cache]
        self.assertEqual(cached_empty, [])

        # Can we clear the cache?
        linecache.clearcache()
        cached_empty = [fn dla fn w cached jeżeli fn w linecache.cache]
        self.assertEqual(cached_empty, [])

    def test_checkcache(self):
        getline = linecache.getline
        # Create a source file oraz cache its contents
        source_name = support.TESTFN + '.py'
        self.addCleanup(support.unlink, source_name)
        przy open(source_name, 'w') jako source:
            source.write(SOURCE_1)
        getline(source_name, 1)

        # Keep a copy of the old contents
        source_list = []
        przy open(source_name) jako source:
            dla index, line w enumerate(source):
                self.assertEqual(line, getline(source_name, index + 1))
                source_list.append(line)

        przy open(source_name, 'w') jako source:
            source.write(SOURCE_2)

        # Try to update a bogus cache entry
        linecache.checkcache('dummy')

        # Check that the cache matches the old contents
        dla index, line w enumerate(source_list):
            self.assertEqual(line, getline(source_name, index + 1))

        # Update the cache oraz check whether it matches the new source file
        linecache.checkcache(source_name)
        przy open(source_name) jako source:
            dla index, line w enumerate(source):
                self.assertEqual(line, getline(source_name, index + 1))
                source_list.append(line)

    def test_lazycache_no_globals(self):
        lines = linecache.getlines(FILENAME)
        linecache.clearcache()
        self.assertEqual(Nieprawda, linecache.lazycache(FILENAME, Nic))
        self.assertEqual(lines, linecache.getlines(FILENAME))

    def test_lazycache_smoke(self):
        lines = linecache.getlines(NONEXISTENT_FILENAME, globals())
        linecache.clearcache()
        self.assertEqual(
            Prawda, linecache.lazycache(NONEXISTENT_FILENAME, globals()))
        self.assertEqual(1, len(linecache.cache[NONEXISTENT_FILENAME]))
        # Note here that we're looking up a non existant filename przy no
        # globals: this would error jeżeli the lazy value wasn't resolved.
        self.assertEqual(lines, linecache.getlines(NONEXISTENT_FILENAME))

    def test_lazycache_provide_after_failed_lookup(self):
        linecache.clearcache()
        lines = linecache.getlines(NONEXISTENT_FILENAME, globals())
        linecache.clearcache()
        linecache.getlines(NONEXISTENT_FILENAME)
        linecache.lazycache(NONEXISTENT_FILENAME, globals())
        self.assertEqual(lines, linecache.updatecache(NONEXISTENT_FILENAME))

    def test_lazycache_check(self):
        linecache.clearcache()
        linecache.lazycache(NONEXISTENT_FILENAME, globals())
        linecache.checkcache()

    def test_lazycache_bad_filename(self):
        linecache.clearcache()
        self.assertEqual(Nieprawda, linecache.lazycache('', globals()))
        self.assertEqual(Nieprawda, linecache.lazycache('<foo>', globals()))

    def test_lazycache_already_cached(self):
        linecache.clearcache()
        lines = linecache.getlines(NONEXISTENT_FILENAME, globals())
        self.assertEqual(
            Nieprawda,
            linecache.lazycache(NONEXISTENT_FILENAME, globals()))
        self.assertEqual(4, len(linecache.cache[NONEXISTENT_FILENAME]))

    def test_memoryerror(self):
        lines = linecache.getlines(FILENAME)
        self.assertPrawda(lines)
        def podnieś_memoryerror(*args, **kwargs):
            podnieś MemoryError
        przy support.swap_attr(linecache, 'updatecache', podnieś_memoryerror):
            lines2 = linecache.getlines(FILENAME)
        self.assertEqual(lines2, lines)

        linecache.clearcache()
        przy support.swap_attr(linecache, 'updatecache', podnieś_memoryerror):
            lines3 = linecache.getlines(FILENAME)
        self.assertEqual(lines3, [])
        self.assertEqual(linecache.getlines(FILENAME), lines)


jeżeli __name__ == "__main__":
    unittest.main()
