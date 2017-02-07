zaimportuj collections
zaimportuj io
zaimportuj os
zaimportuj errno
zaimportuj pathlib
zaimportuj pickle
zaimportuj socket
zaimportuj stat
zaimportuj tempfile
zaimportuj unittest

z test zaimportuj support
TESTFN = support.TESTFN

spróbuj:
    zaimportuj grp, pwd
wyjąwszy ImportError:
    grp = pwd = Nic


klasa _BaseFlavourTest(object):

    def _check_parse_parts(self, arg, expected):
        f = self.flavour.parse_parts
        sep = self.flavour.sep
        altsep = self.flavour.altsep
        actual = f([x.replace('/', sep) dla x w arg])
        self.assertEqual(actual, expected)
        jeżeli altsep:
            actual = f([x.replace('/', altsep) dla x w arg])
            self.assertEqual(actual, expected)

    def test_parse_parts_common(self):
        check = self._check_parse_parts
        sep = self.flavour.sep
        # Unanchored parts
        check([],                   ('', '', []))
        check(['a'],                ('', '', ['a']))
        check(['a/'],               ('', '', ['a']))
        check(['a', 'b'],           ('', '', ['a', 'b']))
        # Expansion
        check(['a/b'],              ('', '', ['a', 'b']))
        check(['a/b/'],             ('', '', ['a', 'b']))
        check(['a', 'b/c', 'd'],    ('', '', ['a', 'b', 'c', 'd']))
        # Collapsing oraz stripping excess slashes
        check(['a', 'b//c', 'd'],   ('', '', ['a', 'b', 'c', 'd']))
        check(['a', 'b/c/', 'd'],   ('', '', ['a', 'b', 'c', 'd']))
        # Eliminating standalone dots
        check(['.'],                ('', '', []))
        check(['.', '.', 'b'],      ('', '', ['b']))
        check(['a', '.', 'b'],      ('', '', ['a', 'b']))
        check(['a', '.', '.'],      ('', '', ['a']))
        # The first part jest anchored
        check(['/a/b'],             ('', sep, [sep, 'a', 'b']))
        check(['/a', 'b'],          ('', sep, [sep, 'a', 'b']))
        check(['/a/', 'b'],         ('', sep, [sep, 'a', 'b']))
        # Ignoring parts before an anchored part
        check(['a', '/b', 'c'],     ('', sep, [sep, 'b', 'c']))
        check(['a', '/b', '/c'],    ('', sep, [sep, 'c']))


klasa PosixFlavourTest(_BaseFlavourTest, unittest.TestCase):
    flavour = pathlib._posix_flavour

    def test_parse_parts(self):
        check = self._check_parse_parts
        # Collapsing of excess leading slashes, wyjąwszy dla the double-slash
        # special case.
        check(['//a', 'b'],             ('', '//', ['//', 'a', 'b']))
        check(['///a', 'b'],            ('', '/', ['/', 'a', 'b']))
        check(['////a', 'b'],           ('', '/', ['/', 'a', 'b']))
        # Paths which look like NT paths aren't treated specially
        check(['c:a'],                  ('', '', ['c:a']))
        check(['c:\\a'],                ('', '', ['c:\\a']))
        check(['\\a'],                  ('', '', ['\\a']))

    def test_splitroot(self):
        f = self.flavour.splitroot
        self.assertEqual(f(''), ('', '', ''))
        self.assertEqual(f('a'), ('', '', 'a'))
        self.assertEqual(f('a/b'), ('', '', 'a/b'))
        self.assertEqual(f('a/b/'), ('', '', 'a/b/'))
        self.assertEqual(f('/a'), ('', '/', 'a'))
        self.assertEqual(f('/a/b'), ('', '/', 'a/b'))
        self.assertEqual(f('/a/b/'), ('', '/', 'a/b/'))
        # The root jest collapsed when there are redundant slashes
        # wyjąwszy when there are exactly two leading slashes, which
        # jest a special case w POSIX.
        self.assertEqual(f('//a'), ('', '//', 'a'))
        self.assertEqual(f('///a'), ('', '/', 'a'))
        self.assertEqual(f('///a/b'), ('', '/', 'a/b'))
        # Paths which look like NT paths aren't treated specially
        self.assertEqual(f('c:/a/b'), ('', '', 'c:/a/b'))
        self.assertEqual(f('\\/a/b'), ('', '', '\\/a/b'))
        self.assertEqual(f('\\a\\b'), ('', '', '\\a\\b'))


klasa NTFlavourTest(_BaseFlavourTest, unittest.TestCase):
    flavour = pathlib._windows_flavour

    def test_parse_parts(self):
        check = self._check_parse_parts
        # First part jest anchored
        check(['c:'],                   ('c:', '', ['c:']))
        check(['c:/'],                  ('c:', '\\', ['c:\\']))
        check(['/'],                    ('', '\\', ['\\']))
        check(['c:a'],                  ('c:', '', ['c:', 'a']))
        check(['c:/a'],                 ('c:', '\\', ['c:\\', 'a']))
        check(['/a'],                   ('', '\\', ['\\', 'a']))
        # UNC paths
        check(['//a/b'],                ('\\\\a\\b', '\\', ['\\\\a\\b\\']))
        check(['//a/b/'],               ('\\\\a\\b', '\\', ['\\\\a\\b\\']))
        check(['//a/b/c'],              ('\\\\a\\b', '\\', ['\\\\a\\b\\', 'c']))
        # Second part jest anchored, so that the first part jest ignored
        check(['a', 'Z:b', 'c'],        ('Z:', '', ['Z:', 'b', 'c']))
        check(['a', 'Z:/b', 'c'],       ('Z:', '\\', ['Z:\\', 'b', 'c']))
        # UNC paths
        check(['a', '//b/c', 'd'],      ('\\\\b\\c', '\\', ['\\\\b\\c\\', 'd']))
        # Collapsing oraz stripping excess slashes
        check(['a', 'Z://b//c/', 'd/'], ('Z:', '\\', ['Z:\\', 'b', 'c', 'd']))
        # UNC paths
        check(['a', '//b/c//', 'd'],    ('\\\\b\\c', '\\', ['\\\\b\\c\\', 'd']))
        # Extended paths
        check(['//?/c:/'],              ('\\\\?\\c:', '\\', ['\\\\?\\c:\\']))
        check(['//?/c:/a'],             ('\\\\?\\c:', '\\', ['\\\\?\\c:\\', 'a']))
        check(['//?/c:/a', '/b'],       ('\\\\?\\c:', '\\', ['\\\\?\\c:\\', 'b']))
        # Extended UNC paths (format jest "\\?\UNC\server\share")
        check(['//?/UNC/b/c'],          ('\\\\?\\UNC\\b\\c', '\\', ['\\\\?\\UNC\\b\\c\\']))
        check(['//?/UNC/b/c/d'],        ('\\\\?\\UNC\\b\\c', '\\', ['\\\\?\\UNC\\b\\c\\', 'd']))
        # Second part has a root but nie drive
        check(['a', '/b', 'c'],         ('', '\\', ['\\', 'b', 'c']))
        check(['Z:/a', '/b', 'c'],      ('Z:', '\\', ['Z:\\', 'b', 'c']))
        check(['//?/Z:/a', '/b', 'c'],  ('\\\\?\\Z:', '\\', ['\\\\?\\Z:\\', 'b', 'c']))

    def test_splitroot(self):
        f = self.flavour.splitroot
        self.assertEqual(f(''), ('', '', ''))
        self.assertEqual(f('a'), ('', '', 'a'))
        self.assertEqual(f('a\\b'), ('', '', 'a\\b'))
        self.assertEqual(f('\\a'), ('', '\\', 'a'))
        self.assertEqual(f('\\a\\b'), ('', '\\', 'a\\b'))
        self.assertEqual(f('c:a\\b'), ('c:', '', 'a\\b'))
        self.assertEqual(f('c:\\a\\b'), ('c:', '\\', 'a\\b'))
        # Redundant slashes w the root are collapsed
        self.assertEqual(f('\\\\a'), ('', '\\', 'a'))
        self.assertEqual(f('\\\\\\a/b'), ('', '\\', 'a/b'))
        self.assertEqual(f('c:\\\\a'), ('c:', '\\', 'a'))
        self.assertEqual(f('c:\\\\\\a/b'), ('c:', '\\', 'a/b'))
        # Valid UNC paths
        self.assertEqual(f('\\\\a\\b'), ('\\\\a\\b', '\\', ''))
        self.assertEqual(f('\\\\a\\b\\'), ('\\\\a\\b', '\\', ''))
        self.assertEqual(f('\\\\a\\b\\c\\d'), ('\\\\a\\b', '\\', 'c\\d'))
        # These are non-UNC paths (according to ntpath.py oraz test_ntpath)
        # However, command.com says such paths are invalid, so it's
        # difficult to know what the right semantics are
        self.assertEqual(f('\\\\\\a\\b'), ('', '\\', 'a\\b'))
        self.assertEqual(f('\\\\a'), ('', '\\', 'a'))


#
# Tests dla the pure classes
#

klasa _BasePurePathTest(object):

    # keys are canonical paths, values are list of tuples of arguments
    # supposed to produce equal paths
    equivalences = {
        'a/b': [
            ('a', 'b'), ('a/', 'b'), ('a', 'b/'), ('a/', 'b/'),
            ('a/b/',), ('a//b',), ('a//b//',),
            # empty components get removed
            ('', 'a', 'b'), ('a', '', 'b'), ('a', 'b', ''),
            ],
        '/b/c/d': [
            ('a', '/b/c', 'd'), ('a', '///b//c', 'd/'),
            ('/a', '/b/c', 'd'),
            # empty components get removed
            ('/', 'b', '', 'c/d'), ('/', '', 'b/c/d'), ('', '/b/c/d'),
            ],
    }

    def setUp(self):
        p = self.cls('a')
        self.flavour = p._flavour
        self.sep = self.flavour.sep
        self.altsep = self.flavour.altsep

    def test_constructor_common(self):
        P = self.cls
        p = P('a')
        self.assertIsInstance(p, P)
        P('a', 'b', 'c')
        P('/a', 'b', 'c')
        P('a/b/c')
        P('/a/b/c')
        self.assertEqual(P(P('a')), P('a'))
        self.assertEqual(P(P('a'), 'b'), P('a/b'))
        self.assertEqual(P(P('a'), P('b')), P('a/b'))

    def _check_str_subclass(self, *args):
        # Issue #21127: it should be possible to construct a PurePath object
        # z an str subclass instance, oraz it then gets converted to
        # a pure str object.
        klasa StrSubclass(str):
            dalej
        P = self.cls
        p = P(*(StrSubclass(x) dla x w args))
        self.assertEqual(p, P(*args))
        dla part w p.parts:
            self.assertIs(type(part), str)

    def test_str_subclass_common(self):
        self._check_str_subclass('')
        self._check_str_subclass('.')
        self._check_str_subclass('a')
        self._check_str_subclass('a/b.txt')
        self._check_str_subclass('/a/b.txt')

    def test_join_common(self):
        P = self.cls
        p = P('a/b')
        pp = p.joinpath('c')
        self.assertEqual(pp, P('a/b/c'))
        self.assertIs(type(pp), type(p))
        pp = p.joinpath('c', 'd')
        self.assertEqual(pp, P('a/b/c/d'))
        pp = p.joinpath(P('c'))
        self.assertEqual(pp, P('a/b/c'))
        pp = p.joinpath('/c')
        self.assertEqual(pp, P('/c'))

    def test_div_common(self):
        # Basically the same jako joinpath()
        P = self.cls
        p = P('a/b')
        pp = p / 'c'
        self.assertEqual(pp, P('a/b/c'))
        self.assertIs(type(pp), type(p))
        pp = p / 'c/d'
        self.assertEqual(pp, P('a/b/c/d'))
        pp = p / 'c' / 'd'
        self.assertEqual(pp, P('a/b/c/d'))
        pp = 'c' / p / 'd'
        self.assertEqual(pp, P('c/a/b/d'))
        pp = p / P('c')
        self.assertEqual(pp, P('a/b/c'))
        pp = p/ '/c'
        self.assertEqual(pp, P('/c'))

    def _check_str(self, expected, args):
        p = self.cls(*args)
        self.assertEqual(str(p), expected.replace('/', self.sep))

    def test_str_common(self):
        # Canonicalized paths roundtrip
        dla pathstr w ('a', 'a/b', 'a/b/c', '/', '/a/b', '/a/b/c'):
            self._check_str(pathstr, (pathstr,))
        # Special case dla the empty path
        self._check_str('.', ('',))
        # Other tests dla str() are w test_equivalences()

    def test_as_posix_common(self):
        P = self.cls
        dla pathstr w ('a', 'a/b', 'a/b/c', '/', '/a/b', '/a/b/c'):
            self.assertEqual(P(pathstr).as_posix(), pathstr)
        # Other tests dla as_posix() are w test_equivalences()

    def test_as_bytes_common(self):
        sep = os.fsencode(self.sep)
        P = self.cls
        self.assertEqual(bytes(P('a/b')), b'a' + sep + b'b')

    def test_as_uri_common(self):
        P = self.cls
        przy self.assertRaises(ValueError):
            P('a').as_uri()
        przy self.assertRaises(ValueError):
            P().as_uri()

    def test_repr_common(self):
        dla pathstr w ('a', 'a/b', 'a/b/c', '/', '/a/b', '/a/b/c'):
            p = self.cls(pathstr)
            clsname = p.__class__.__name__
            r = repr(p)
            # The repr() jest w the form ClassName("forward-slashes path")
            self.assertPrawda(r.startswith(clsname + '('), r)
            self.assertPrawda(r.endswith(')'), r)
            inner = r[len(clsname) + 1 : -1]
            self.assertEqual(eval(inner), p.as_posix())
            # The repr() roundtrips
            q = eval(r, pathlib.__dict__)
            self.assertIs(q.__class__, p.__class__)
            self.assertEqual(q, p)
            self.assertEqual(repr(q), r)

    def test_eq_common(self):
        P = self.cls
        self.assertEqual(P('a/b'), P('a/b'))
        self.assertEqual(P('a/b'), P('a', 'b'))
        self.assertNotEqual(P('a/b'), P('a'))
        self.assertNotEqual(P('a/b'), P('/a/b'))
        self.assertNotEqual(P('a/b'), P())
        self.assertNotEqual(P('/a/b'), P('/'))
        self.assertNotEqual(P(), P('/'))
        self.assertNotEqual(P(), "")
        self.assertNotEqual(P(), {})
        self.assertNotEqual(P(), int)

    def test_match_common(self):
        P = self.cls
        self.assertRaises(ValueError, P('a').match, '')
        self.assertRaises(ValueError, P('a').match, '.')
        # Simple relative pattern
        self.assertPrawda(P('b.py').match('b.py'))
        self.assertPrawda(P('a/b.py').match('b.py'))
        self.assertPrawda(P('/a/b.py').match('b.py'))
        self.assertNieprawda(P('a.py').match('b.py'))
        self.assertNieprawda(P('b/py').match('b.py'))
        self.assertNieprawda(P('/a.py').match('b.py'))
        self.assertNieprawda(P('b.py/c').match('b.py'))
        # Wilcard relative pattern
        self.assertPrawda(P('b.py').match('*.py'))
        self.assertPrawda(P('a/b.py').match('*.py'))
        self.assertPrawda(P('/a/b.py').match('*.py'))
        self.assertNieprawda(P('b.pyc').match('*.py'))
        self.assertNieprawda(P('b./py').match('*.py'))
        self.assertNieprawda(P('b.py/c').match('*.py'))
        # Multi-part relative pattern
        self.assertPrawda(P('ab/c.py').match('a*/*.py'))
        self.assertPrawda(P('/d/ab/c.py').match('a*/*.py'))
        self.assertNieprawda(P('a.py').match('a*/*.py'))
        self.assertNieprawda(P('/dab/c.py').match('a*/*.py'))
        self.assertNieprawda(P('ab/c.py/d').match('a*/*.py'))
        # Absolute pattern
        self.assertPrawda(P('/b.py').match('/*.py'))
        self.assertNieprawda(P('b.py').match('/*.py'))
        self.assertNieprawda(P('a/b.py').match('/*.py'))
        self.assertNieprawda(P('/a/b.py').match('/*.py'))
        # Multi-part absolute pattern
        self.assertPrawda(P('/a/b.py').match('/a/*.py'))
        self.assertNieprawda(P('/ab.py').match('/a/*.py'))
        self.assertNieprawda(P('/a/b/c.py').match('/a/*.py'))

    def test_ordering_common(self):
        # Ordering jest tuple-alike
        def assertLess(a, b):
            self.assertLess(a, b)
            self.assertGreater(b, a)
        P = self.cls
        a = P('a')
        b = P('a/b')
        c = P('abc')
        d = P('b')
        assertLess(a, b)
        assertLess(a, c)
        assertLess(a, d)
        assertLess(b, c)
        assertLess(c, d)
        P = self.cls
        a = P('/a')
        b = P('/a/b')
        c = P('/abc')
        d = P('/b')
        assertLess(a, b)
        assertLess(a, c)
        assertLess(a, d)
        assertLess(b, c)
        assertLess(c, d)
        przy self.assertRaises(TypeError):
            P() < {}

    def test_parts_common(self):
        # `parts` returns a tuple
        sep = self.sep
        P = self.cls
        p = P('a/b')
        parts = p.parts
        self.assertEqual(parts, ('a', 'b'))
        # The object gets reused
        self.assertIs(parts, p.parts)
        # When the path jest absolute, the anchor jest a separate part
        p = P('/a/b')
        parts = p.parts
        self.assertEqual(parts, (sep, 'a', 'b'))

    def test_equivalences(self):
        dla k, tuples w self.equivalences.items():
            canon = k.replace('/', self.sep)
            posix = k.replace(self.sep, '/')
            jeżeli canon != posix:
                tuples = tuples + [
                    tuple(part.replace('/', self.sep) dla part w t)
                    dla t w tuples
                    ]
                tuples.append((posix, ))
            pcanon = self.cls(canon)
            dla t w tuples:
                p = self.cls(*t)
                self.assertEqual(p, pcanon, "failed przy args {}".format(t))
                self.assertEqual(hash(p), hash(pcanon))
                self.assertEqual(str(p), canon)
                self.assertEqual(p.as_posix(), posix)

    def test_parent_common(self):
        # Relative
        P = self.cls
        p = P('a/b/c')
        self.assertEqual(p.parent, P('a/b'))
        self.assertEqual(p.parent.parent, P('a'))
        self.assertEqual(p.parent.parent.parent, P())
        self.assertEqual(p.parent.parent.parent.parent, P())
        # Anchored
        p = P('/a/b/c')
        self.assertEqual(p.parent, P('/a/b'))
        self.assertEqual(p.parent.parent, P('/a'))
        self.assertEqual(p.parent.parent.parent, P('/'))
        self.assertEqual(p.parent.parent.parent.parent, P('/'))

    def test_parents_common(self):
        # Relative
        P = self.cls
        p = P('a/b/c')
        par = p.parents
        self.assertEqual(len(par), 3)
        self.assertEqual(par[0], P('a/b'))
        self.assertEqual(par[1], P('a'))
        self.assertEqual(par[2], P('.'))
        self.assertEqual(list(par), [P('a/b'), P('a'), P('.')])
        przy self.assertRaises(IndexError):
            par[-1]
        przy self.assertRaises(IndexError):
            par[3]
        przy self.assertRaises(TypeError):
            par[0] = p
        # Anchored
        p = P('/a/b/c')
        par = p.parents
        self.assertEqual(len(par), 3)
        self.assertEqual(par[0], P('/a/b'))
        self.assertEqual(par[1], P('/a'))
        self.assertEqual(par[2], P('/'))
        self.assertEqual(list(par), [P('/a/b'), P('/a'), P('/')])
        przy self.assertRaises(IndexError):
            par[3]

    def test_drive_common(self):
        P = self.cls
        self.assertEqual(P('a/b').drive, '')
        self.assertEqual(P('/a/b').drive, '')
        self.assertEqual(P('').drive, '')

    def test_root_common(self):
        P = self.cls
        sep = self.sep
        self.assertEqual(P('').root, '')
        self.assertEqual(P('a/b').root, '')
        self.assertEqual(P('/').root, sep)
        self.assertEqual(P('/a/b').root, sep)

    def test_anchor_common(self):
        P = self.cls
        sep = self.sep
        self.assertEqual(P('').anchor, '')
        self.assertEqual(P('a/b').anchor, '')
        self.assertEqual(P('/').anchor, sep)
        self.assertEqual(P('/a/b').anchor, sep)

    def test_name_common(self):
        P = self.cls
        self.assertEqual(P('').name, '')
        self.assertEqual(P('.').name, '')
        self.assertEqual(P('/').name, '')
        self.assertEqual(P('a/b').name, 'b')
        self.assertEqual(P('/a/b').name, 'b')
        self.assertEqual(P('/a/b/.').name, 'b')
        self.assertEqual(P('a/b.py').name, 'b.py')
        self.assertEqual(P('/a/b.py').name, 'b.py')

    def test_suffix_common(self):
        P = self.cls
        self.assertEqual(P('').suffix, '')
        self.assertEqual(P('.').suffix, '')
        self.assertEqual(P('..').suffix, '')
        self.assertEqual(P('/').suffix, '')
        self.assertEqual(P('a/b').suffix, '')
        self.assertEqual(P('/a/b').suffix, '')
        self.assertEqual(P('/a/b/.').suffix, '')
        self.assertEqual(P('a/b.py').suffix, '.py')
        self.assertEqual(P('/a/b.py').suffix, '.py')
        self.assertEqual(P('a/.hgrc').suffix, '')
        self.assertEqual(P('/a/.hgrc').suffix, '')
        self.assertEqual(P('a/.hg.rc').suffix, '.rc')
        self.assertEqual(P('/a/.hg.rc').suffix, '.rc')
        self.assertEqual(P('a/b.tar.gz').suffix, '.gz')
        self.assertEqual(P('/a/b.tar.gz').suffix, '.gz')
        self.assertEqual(P('a/Some name. Ending przy a dot.').suffix, '')
        self.assertEqual(P('/a/Some name. Ending przy a dot.').suffix, '')

    def test_suffixes_common(self):
        P = self.cls
        self.assertEqual(P('').suffixes, [])
        self.assertEqual(P('.').suffixes, [])
        self.assertEqual(P('/').suffixes, [])
        self.assertEqual(P('a/b').suffixes, [])
        self.assertEqual(P('/a/b').suffixes, [])
        self.assertEqual(P('/a/b/.').suffixes, [])
        self.assertEqual(P('a/b.py').suffixes, ['.py'])
        self.assertEqual(P('/a/b.py').suffixes, ['.py'])
        self.assertEqual(P('a/.hgrc').suffixes, [])
        self.assertEqual(P('/a/.hgrc').suffixes, [])
        self.assertEqual(P('a/.hg.rc').suffixes, ['.rc'])
        self.assertEqual(P('/a/.hg.rc').suffixes, ['.rc'])
        self.assertEqual(P('a/b.tar.gz').suffixes, ['.tar', '.gz'])
        self.assertEqual(P('/a/b.tar.gz').suffixes, ['.tar', '.gz'])
        self.assertEqual(P('a/Some name. Ending przy a dot.').suffixes, [])
        self.assertEqual(P('/a/Some name. Ending przy a dot.').suffixes, [])

    def test_stem_common(self):
        P = self.cls
        self.assertEqual(P('').stem, '')
        self.assertEqual(P('.').stem, '')
        self.assertEqual(P('..').stem, '..')
        self.assertEqual(P('/').stem, '')
        self.assertEqual(P('a/b').stem, 'b')
        self.assertEqual(P('a/b.py').stem, 'b')
        self.assertEqual(P('a/.hgrc').stem, '.hgrc')
        self.assertEqual(P('a/.hg.rc').stem, '.hg')
        self.assertEqual(P('a/b.tar.gz').stem, 'b.tar')
        self.assertEqual(P('a/Some name. Ending przy a dot.').stem,
                         'Some name. Ending przy a dot.')

    def test_with_name_common(self):
        P = self.cls
        self.assertEqual(P('a/b').with_name('d.xml'), P('a/d.xml'))
        self.assertEqual(P('/a/b').with_name('d.xml'), P('/a/d.xml'))
        self.assertEqual(P('a/b.py').with_name('d.xml'), P('a/d.xml'))
        self.assertEqual(P('/a/b.py').with_name('d.xml'), P('/a/d.xml'))
        self.assertEqual(P('a/Dot ending.').with_name('d.xml'), P('a/d.xml'))
        self.assertEqual(P('/a/Dot ending.').with_name('d.xml'), P('/a/d.xml'))
        self.assertRaises(ValueError, P('').with_name, 'd.xml')
        self.assertRaises(ValueError, P('.').with_name, 'd.xml')
        self.assertRaises(ValueError, P('/').with_name, 'd.xml')
        self.assertRaises(ValueError, P('a/b').with_name, '')
        self.assertRaises(ValueError, P('a/b').with_name, '/c')
        self.assertRaises(ValueError, P('a/b').with_name, 'c/')
        self.assertRaises(ValueError, P('a/b').with_name, 'c/d')

    def test_with_suffix_common(self):
        P = self.cls
        self.assertEqual(P('a/b').with_suffix('.gz'), P('a/b.gz'))
        self.assertEqual(P('/a/b').with_suffix('.gz'), P('/a/b.gz'))
        self.assertEqual(P('a/b.py').with_suffix('.gz'), P('a/b.gz'))
        self.assertEqual(P('/a/b.py').with_suffix('.gz'), P('/a/b.gz'))
        # Stripping suffix
        self.assertEqual(P('a/b.py').with_suffix(''), P('a/b'))
        self.assertEqual(P('/a/b').with_suffix(''), P('/a/b'))
        # Path doesn't have a "filename" component
        self.assertRaises(ValueError, P('').with_suffix, '.gz')
        self.assertRaises(ValueError, P('.').with_suffix, '.gz')
        self.assertRaises(ValueError, P('/').with_suffix, '.gz')
        # Invalid suffix
        self.assertRaises(ValueError, P('a/b').with_suffix, 'gz')
        self.assertRaises(ValueError, P('a/b').with_suffix, '/')
        self.assertRaises(ValueError, P('a/b').with_suffix, '.')
        self.assertRaises(ValueError, P('a/b').with_suffix, '/.gz')
        self.assertRaises(ValueError, P('a/b').with_suffix, 'c/d')
        self.assertRaises(ValueError, P('a/b').with_suffix, '.c/.d')
        self.assertRaises(ValueError, P('a/b').with_suffix, './.d')
        self.assertRaises(ValueError, P('a/b').with_suffix, '.d/.')

    def test_relative_to_common(self):
        P = self.cls
        p = P('a/b')
        self.assertRaises(TypeError, p.relative_to)
        self.assertRaises(TypeError, p.relative_to, b'a')
        self.assertEqual(p.relative_to(P()), P('a/b'))
        self.assertEqual(p.relative_to(''), P('a/b'))
        self.assertEqual(p.relative_to(P('a')), P('b'))
        self.assertEqual(p.relative_to('a'), P('b'))
        self.assertEqual(p.relative_to('a/'), P('b'))
        self.assertEqual(p.relative_to(P('a/b')), P())
        self.assertEqual(p.relative_to('a/b'), P())
        # With several args
        self.assertEqual(p.relative_to('a', 'b'), P())
        # Unrelated paths
        self.assertRaises(ValueError, p.relative_to, P('c'))
        self.assertRaises(ValueError, p.relative_to, P('a/b/c'))
        self.assertRaises(ValueError, p.relative_to, P('a/c'))
        self.assertRaises(ValueError, p.relative_to, P('/a'))
        p = P('/a/b')
        self.assertEqual(p.relative_to(P('/')), P('a/b'))
        self.assertEqual(p.relative_to('/'), P('a/b'))
        self.assertEqual(p.relative_to(P('/a')), P('b'))
        self.assertEqual(p.relative_to('/a'), P('b'))
        self.assertEqual(p.relative_to('/a/'), P('b'))
        self.assertEqual(p.relative_to(P('/a/b')), P())
        self.assertEqual(p.relative_to('/a/b'), P())
        # Unrelated paths
        self.assertRaises(ValueError, p.relative_to, P('/c'))
        self.assertRaises(ValueError, p.relative_to, P('/a/b/c'))
        self.assertRaises(ValueError, p.relative_to, P('/a/c'))
        self.assertRaises(ValueError, p.relative_to, P())
        self.assertRaises(ValueError, p.relative_to, '')
        self.assertRaises(ValueError, p.relative_to, P('a'))

    def test_pickling_common(self):
        P = self.cls
        p = P('/a/b')
        dla proto w range(0, pickle.HIGHEST_PROTOCOL + 1):
            dumped = pickle.dumps(p, proto)
            pp = pickle.loads(dumped)
            self.assertIs(pp.__class__, p.__class__)
            self.assertEqual(pp, p)
            self.assertEqual(hash(pp), hash(p))
            self.assertEqual(str(pp), str(p))


klasa PurePosixPathTest(_BasePurePathTest, unittest.TestCase):
    cls = pathlib.PurePosixPath

    def test_root(self):
        P = self.cls
        self.assertEqual(P('/a/b').root, '/')
        self.assertEqual(P('///a/b').root, '/')
        # POSIX special case dla two leading slashes
        self.assertEqual(P('//a/b').root, '//')

    def test_eq(self):
        P = self.cls
        self.assertNotEqual(P('a/b'), P('A/b'))
        self.assertEqual(P('/a'), P('///a'))
        self.assertNotEqual(P('/a'), P('//a'))

    def test_as_uri(self):
        P = self.cls
        self.assertEqual(P('/').as_uri(), 'file:///')
        self.assertEqual(P('/a/b.c').as_uri(), 'file:///a/b.c')
        self.assertEqual(P('/a/b%#c').as_uri(), 'file:///a/b%25%23c')

    def test_as_uri_non_ascii(self):
        z urllib.parse zaimportuj quote_from_bytes
        P = self.cls
        spróbuj:
            os.fsencode('\xe9')
        wyjąwszy UnicodeEncodeError:
            self.skipTest("\\xe9 cannot be encoded to the filesystem encoding")
        self.assertEqual(P('/a/b\xe9').as_uri(),
                         'file:///a/b' + quote_from_bytes(os.fsencode('\xe9')))

    def test_match(self):
        P = self.cls
        self.assertNieprawda(P('A.py').match('a.PY'))

    def test_is_absolute(self):
        P = self.cls
        self.assertNieprawda(P().is_absolute())
        self.assertNieprawda(P('a').is_absolute())
        self.assertNieprawda(P('a/b/').is_absolute())
        self.assertPrawda(P('/').is_absolute())
        self.assertPrawda(P('/a').is_absolute())
        self.assertPrawda(P('/a/b/').is_absolute())
        self.assertPrawda(P('//a').is_absolute())
        self.assertPrawda(P('//a/b').is_absolute())

    def test_is_reserved(self):
        P = self.cls
        self.assertIs(Nieprawda, P('').is_reserved())
        self.assertIs(Nieprawda, P('/').is_reserved())
        self.assertIs(Nieprawda, P('/foo/bar').is_reserved())
        self.assertIs(Nieprawda, P('/dev/con/PRN/NUL').is_reserved())

    def test_join(self):
        P = self.cls
        p = P('//a')
        pp = p.joinpath('b')
        self.assertEqual(pp, P('//a/b'))
        pp = P('/a').joinpath('//c')
        self.assertEqual(pp, P('//c'))
        pp = P('//a').joinpath('/c')
        self.assertEqual(pp, P('/c'))

    def test_div(self):
        # Basically the same jako joinpath()
        P = self.cls
        p = P('//a')
        pp = p / 'b'
        self.assertEqual(pp, P('//a/b'))
        pp = P('/a') / '//c'
        self.assertEqual(pp, P('//c'))
        pp = P('//a') / '/c'
        self.assertEqual(pp, P('/c'))


klasa PureWindowsPathTest(_BasePurePathTest, unittest.TestCase):
    cls = pathlib.PureWindowsPath

    equivalences = _BasePurePathTest.equivalences.copy()
    equivalences.update({
        'c:a': [ ('c:', 'a'), ('c:', 'a/'), ('/', 'c:', 'a') ],
        'c:/a': [
            ('c:/', 'a'), ('c:', '/', 'a'), ('c:', '/a'),
            ('/z', 'c:/', 'a'), ('//x/y', 'c:/', 'a'),
            ],
        '//a/b/': [ ('//a/b',) ],
        '//a/b/c': [
            ('//a/b', 'c'), ('//a/b/', 'c'),
            ],
    })

    def test_str(self):
        p = self.cls('a/b/c')
        self.assertEqual(str(p), 'a\\b\\c')
        p = self.cls('c:/a/b/c')
        self.assertEqual(str(p), 'c:\\a\\b\\c')
        p = self.cls('//a/b')
        self.assertEqual(str(p), '\\\\a\\b\\')
        p = self.cls('//a/b/c')
        self.assertEqual(str(p), '\\\\a\\b\\c')
        p = self.cls('//a/b/c/d')
        self.assertEqual(str(p), '\\\\a\\b\\c\\d')

    def test_str_subclass(self):
        self._check_str_subclass('c:')
        self._check_str_subclass('c:a')
        self._check_str_subclass('c:a\\b.txt')
        self._check_str_subclass('c:\\')
        self._check_str_subclass('c:\\a')
        self._check_str_subclass('c:\\a\\b.txt')
        self._check_str_subclass('\\\\some\\share')
        self._check_str_subclass('\\\\some\\share\\a')
        self._check_str_subclass('\\\\some\\share\\a\\b.txt')

    def test_eq(self):
        P = self.cls
        self.assertEqual(P('c:a/b'), P('c:a/b'))
        self.assertEqual(P('c:a/b'), P('c:', 'a', 'b'))
        self.assertNotEqual(P('c:a/b'), P('d:a/b'))
        self.assertNotEqual(P('c:a/b'), P('c:/a/b'))
        self.assertNotEqual(P('/a/b'), P('c:/a/b'))
        # Case-insensitivity
        self.assertEqual(P('a/B'), P('A/b'))
        self.assertEqual(P('C:a/B'), P('c:A/b'))
        self.assertEqual(P('//Some/SHARE/a/B'), P('//somE/share/A/b'))

    def test_as_uri(self):
        P = self.cls
        przy self.assertRaises(ValueError):
            P('/a/b').as_uri()
        przy self.assertRaises(ValueError):
            P('c:a/b').as_uri()
        self.assertEqual(P('c:/').as_uri(), 'file:///c:/')
        self.assertEqual(P('c:/a/b.c').as_uri(), 'file:///c:/a/b.c')
        self.assertEqual(P('c:/a/b%#c').as_uri(), 'file:///c:/a/b%25%23c')
        self.assertEqual(P('c:/a/b\xe9').as_uri(), 'file:///c:/a/b%C3%A9')
        self.assertEqual(P('//some/share/').as_uri(), 'file://some/share/')
        self.assertEqual(P('//some/share/a/b.c').as_uri(),
                         'file://some/share/a/b.c')
        self.assertEqual(P('//some/share/a/b%#c\xe9').as_uri(),
                         'file://some/share/a/b%25%23c%C3%A9')

    def test_match_common(self):
        P = self.cls
        # Absolute patterns
        self.assertPrawda(P('c:/b.py').match('/*.py'))
        self.assertPrawda(P('c:/b.py').match('c:*.py'))
        self.assertPrawda(P('c:/b.py').match('c:/*.py'))
        self.assertNieprawda(P('d:/b.py').match('c:/*.py'))  # wrong drive
        self.assertNieprawda(P('b.py').match('/*.py'))
        self.assertNieprawda(P('b.py').match('c:*.py'))
        self.assertNieprawda(P('b.py').match('c:/*.py'))
        self.assertNieprawda(P('c:b.py').match('/*.py'))
        self.assertNieprawda(P('c:b.py').match('c:/*.py'))
        self.assertNieprawda(P('/b.py').match('c:*.py'))
        self.assertNieprawda(P('/b.py').match('c:/*.py'))
        # UNC patterns
        self.assertPrawda(P('//some/share/a.py').match('/*.py'))
        self.assertPrawda(P('//some/share/a.py').match('//some/share/*.py'))
        self.assertNieprawda(P('//other/share/a.py').match('//some/share/*.py'))
        self.assertNieprawda(P('//some/share/a/b.py').match('//some/share/*.py'))
        # Case-insensitivity
        self.assertPrawda(P('B.py').match('b.PY'))
        self.assertPrawda(P('c:/a/B.Py').match('C:/A/*.pY'))
        self.assertPrawda(P('//Some/Share/B.Py').match('//somE/sharE/*.pY'))

    def test_ordering_common(self):
        # Case-insensitivity
        def assertOrderedEqual(a, b):
            self.assertLessEqual(a, b)
            self.assertGreaterEqual(b, a)
        P = self.cls
        p = P('c:A/b')
        q = P('C:a/B')
        assertOrderedEqual(p, q)
        self.assertNieprawda(p < q)
        self.assertNieprawda(p > q)
        p = P('//some/Share/A/b')
        q = P('//Some/SHARE/a/B')
        assertOrderedEqual(p, q)
        self.assertNieprawda(p < q)
        self.assertNieprawda(p > q)

    def test_parts(self):
        P = self.cls
        p = P('c:a/b')
        parts = p.parts
        self.assertEqual(parts, ('c:', 'a', 'b'))
        p = P('c:/a/b')
        parts = p.parts
        self.assertEqual(parts, ('c:\\', 'a', 'b'))
        p = P('//a/b/c/d')
        parts = p.parts
        self.assertEqual(parts, ('\\\\a\\b\\', 'c', 'd'))

    def test_parent(self):
        # Anchored
        P = self.cls
        p = P('z:a/b/c')
        self.assertEqual(p.parent, P('z:a/b'))
        self.assertEqual(p.parent.parent, P('z:a'))
        self.assertEqual(p.parent.parent.parent, P('z:'))
        self.assertEqual(p.parent.parent.parent.parent, P('z:'))
        p = P('z:/a/b/c')
        self.assertEqual(p.parent, P('z:/a/b'))
        self.assertEqual(p.parent.parent, P('z:/a'))
        self.assertEqual(p.parent.parent.parent, P('z:/'))
        self.assertEqual(p.parent.parent.parent.parent, P('z:/'))
        p = P('//a/b/c/d')
        self.assertEqual(p.parent, P('//a/b/c'))
        self.assertEqual(p.parent.parent, P('//a/b'))
        self.assertEqual(p.parent.parent.parent, P('//a/b'))

    def test_parents(self):
        # Anchored
        P = self.cls
        p = P('z:a/b/')
        par = p.parents
        self.assertEqual(len(par), 2)
        self.assertEqual(par[0], P('z:a'))
        self.assertEqual(par[1], P('z:'))
        self.assertEqual(list(par), [P('z:a'), P('z:')])
        przy self.assertRaises(IndexError):
            par[2]
        p = P('z:/a/b/')
        par = p.parents
        self.assertEqual(len(par), 2)
        self.assertEqual(par[0], P('z:/a'))
        self.assertEqual(par[1], P('z:/'))
        self.assertEqual(list(par), [P('z:/a'), P('z:/')])
        przy self.assertRaises(IndexError):
            par[2]
        p = P('//a/b/c/d')
        par = p.parents
        self.assertEqual(len(par), 2)
        self.assertEqual(par[0], P('//a/b/c'))
        self.assertEqual(par[1], P('//a/b'))
        self.assertEqual(list(par), [P('//a/b/c'), P('//a/b')])
        przy self.assertRaises(IndexError):
            par[2]

    def test_drive(self):
        P = self.cls
        self.assertEqual(P('c:').drive, 'c:')
        self.assertEqual(P('c:a/b').drive, 'c:')
        self.assertEqual(P('c:/').drive, 'c:')
        self.assertEqual(P('c:/a/b/').drive, 'c:')
        self.assertEqual(P('//a/b').drive, '\\\\a\\b')
        self.assertEqual(P('//a/b/').drive, '\\\\a\\b')
        self.assertEqual(P('//a/b/c/d').drive, '\\\\a\\b')

    def test_root(self):
        P = self.cls
        self.assertEqual(P('c:').root, '')
        self.assertEqual(P('c:a/b').root, '')
        self.assertEqual(P('c:/').root, '\\')
        self.assertEqual(P('c:/a/b/').root, '\\')
        self.assertEqual(P('//a/b').root, '\\')
        self.assertEqual(P('//a/b/').root, '\\')
        self.assertEqual(P('//a/b/c/d').root, '\\')

    def test_anchor(self):
        P = self.cls
        self.assertEqual(P('c:').anchor, 'c:')
        self.assertEqual(P('c:a/b').anchor, 'c:')
        self.assertEqual(P('c:/').anchor, 'c:\\')
        self.assertEqual(P('c:/a/b/').anchor, 'c:\\')
        self.assertEqual(P('//a/b').anchor, '\\\\a\\b\\')
        self.assertEqual(P('//a/b/').anchor, '\\\\a\\b\\')
        self.assertEqual(P('//a/b/c/d').anchor, '\\\\a\\b\\')

    def test_name(self):
        P = self.cls
        self.assertEqual(P('c:').name, '')
        self.assertEqual(P('c:/').name, '')
        self.assertEqual(P('c:a/b').name, 'b')
        self.assertEqual(P('c:/a/b').name, 'b')
        self.assertEqual(P('c:a/b.py').name, 'b.py')
        self.assertEqual(P('c:/a/b.py').name, 'b.py')
        self.assertEqual(P('//My.py/Share.php').name, '')
        self.assertEqual(P('//My.py/Share.php/a/b').name, 'b')

    def test_suffix(self):
        P = self.cls
        self.assertEqual(P('c:').suffix, '')
        self.assertEqual(P('c:/').suffix, '')
        self.assertEqual(P('c:a/b').suffix, '')
        self.assertEqual(P('c:/a/b').suffix, '')
        self.assertEqual(P('c:a/b.py').suffix, '.py')
        self.assertEqual(P('c:/a/b.py').suffix, '.py')
        self.assertEqual(P('c:a/.hgrc').suffix, '')
        self.assertEqual(P('c:/a/.hgrc').suffix, '')
        self.assertEqual(P('c:a/.hg.rc').suffix, '.rc')
        self.assertEqual(P('c:/a/.hg.rc').suffix, '.rc')
        self.assertEqual(P('c:a/b.tar.gz').suffix, '.gz')
        self.assertEqual(P('c:/a/b.tar.gz').suffix, '.gz')
        self.assertEqual(P('c:a/Some name. Ending przy a dot.').suffix, '')
        self.assertEqual(P('c:/a/Some name. Ending przy a dot.').suffix, '')
        self.assertEqual(P('//My.py/Share.php').suffix, '')
        self.assertEqual(P('//My.py/Share.php/a/b').suffix, '')

    def test_suffixes(self):
        P = self.cls
        self.assertEqual(P('c:').suffixes, [])
        self.assertEqual(P('c:/').suffixes, [])
        self.assertEqual(P('c:a/b').suffixes, [])
        self.assertEqual(P('c:/a/b').suffixes, [])
        self.assertEqual(P('c:a/b.py').suffixes, ['.py'])
        self.assertEqual(P('c:/a/b.py').suffixes, ['.py'])
        self.assertEqual(P('c:a/.hgrc').suffixes, [])
        self.assertEqual(P('c:/a/.hgrc').suffixes, [])
        self.assertEqual(P('c:a/.hg.rc').suffixes, ['.rc'])
        self.assertEqual(P('c:/a/.hg.rc').suffixes, ['.rc'])
        self.assertEqual(P('c:a/b.tar.gz').suffixes, ['.tar', '.gz'])
        self.assertEqual(P('c:/a/b.tar.gz').suffixes, ['.tar', '.gz'])
        self.assertEqual(P('//My.py/Share.php').suffixes, [])
        self.assertEqual(P('//My.py/Share.php/a/b').suffixes, [])
        self.assertEqual(P('c:a/Some name. Ending przy a dot.').suffixes, [])
        self.assertEqual(P('c:/a/Some name. Ending przy a dot.').suffixes, [])

    def test_stem(self):
        P = self.cls
        self.assertEqual(P('c:').stem, '')
        self.assertEqual(P('c:.').stem, '')
        self.assertEqual(P('c:..').stem, '..')
        self.assertEqual(P('c:/').stem, '')
        self.assertEqual(P('c:a/b').stem, 'b')
        self.assertEqual(P('c:a/b.py').stem, 'b')
        self.assertEqual(P('c:a/.hgrc').stem, '.hgrc')
        self.assertEqual(P('c:a/.hg.rc').stem, '.hg')
        self.assertEqual(P('c:a/b.tar.gz').stem, 'b.tar')
        self.assertEqual(P('c:a/Some name. Ending przy a dot.').stem,
                         'Some name. Ending przy a dot.')

    def test_with_name(self):
        P = self.cls
        self.assertEqual(P('c:a/b').with_name('d.xml'), P('c:a/d.xml'))
        self.assertEqual(P('c:/a/b').with_name('d.xml'), P('c:/a/d.xml'))
        self.assertEqual(P('c:a/Dot ending.').with_name('d.xml'), P('c:a/d.xml'))
        self.assertEqual(P('c:/a/Dot ending.').with_name('d.xml'), P('c:/a/d.xml'))
        self.assertRaises(ValueError, P('c:').with_name, 'd.xml')
        self.assertRaises(ValueError, P('c:/').with_name, 'd.xml')
        self.assertRaises(ValueError, P('//My/Share').with_name, 'd.xml')
        self.assertRaises(ValueError, P('c:a/b').with_name, 'd:')
        self.assertRaises(ValueError, P('c:a/b').with_name, 'd:e')
        self.assertRaises(ValueError, P('c:a/b').with_name, 'd:/e')
        self.assertRaises(ValueError, P('c:a/b').with_name, '//My/Share')

    def test_with_suffix(self):
        P = self.cls
        self.assertEqual(P('c:a/b').with_suffix('.gz'), P('c:a/b.gz'))
        self.assertEqual(P('c:/a/b').with_suffix('.gz'), P('c:/a/b.gz'))
        self.assertEqual(P('c:a/b.py').with_suffix('.gz'), P('c:a/b.gz'))
        self.assertEqual(P('c:/a/b.py').with_suffix('.gz'), P('c:/a/b.gz'))
        # Path doesn't have a "filename" component
        self.assertRaises(ValueError, P('').with_suffix, '.gz')
        self.assertRaises(ValueError, P('.').with_suffix, '.gz')
        self.assertRaises(ValueError, P('/').with_suffix, '.gz')
        self.assertRaises(ValueError, P('//My/Share').with_suffix, '.gz')
        # Invalid suffix
        self.assertRaises(ValueError, P('c:a/b').with_suffix, 'gz')
        self.assertRaises(ValueError, P('c:a/b').with_suffix, '/')
        self.assertRaises(ValueError, P('c:a/b').with_suffix, '\\')
        self.assertRaises(ValueError, P('c:a/b').with_suffix, 'c:')
        self.assertRaises(ValueError, P('c:a/b').with_suffix, '/.gz')
        self.assertRaises(ValueError, P('c:a/b').with_suffix, '\\.gz')
        self.assertRaises(ValueError, P('c:a/b').with_suffix, 'c:.gz')
        self.assertRaises(ValueError, P('c:a/b').with_suffix, 'c/d')
        self.assertRaises(ValueError, P('c:a/b').with_suffix, 'c\\d')
        self.assertRaises(ValueError, P('c:a/b').with_suffix, '.c/d')
        self.assertRaises(ValueError, P('c:a/b').with_suffix, '.c\\d')

    def test_relative_to(self):
        P = self.cls
        p = P('C:Foo/Bar')
        self.assertEqual(p.relative_to(P('c:')), P('Foo/Bar'))
        self.assertEqual(p.relative_to('c:'), P('Foo/Bar'))
        self.assertEqual(p.relative_to(P('c:foO')), P('Bar'))
        self.assertEqual(p.relative_to('c:foO'), P('Bar'))
        self.assertEqual(p.relative_to('c:foO/'), P('Bar'))
        self.assertEqual(p.relative_to(P('c:foO/baR')), P())
        self.assertEqual(p.relative_to('c:foO/baR'), P())
        # Unrelated paths
        self.assertRaises(ValueError, p.relative_to, P())
        self.assertRaises(ValueError, p.relative_to, '')
        self.assertRaises(ValueError, p.relative_to, P('d:'))
        self.assertRaises(ValueError, p.relative_to, P('/'))
        self.assertRaises(ValueError, p.relative_to, P('Foo'))
        self.assertRaises(ValueError, p.relative_to, P('/Foo'))
        self.assertRaises(ValueError, p.relative_to, P('C:/Foo'))
        self.assertRaises(ValueError, p.relative_to, P('C:Foo/Bar/Baz'))
        self.assertRaises(ValueError, p.relative_to, P('C:Foo/Baz'))
        p = P('C:/Foo/Bar')
        self.assertEqual(p.relative_to(P('c:')), P('/Foo/Bar'))
        self.assertEqual(p.relative_to('c:'), P('/Foo/Bar'))
        self.assertEqual(str(p.relative_to(P('c:'))), '\\Foo\\Bar')
        self.assertEqual(str(p.relative_to('c:')), '\\Foo\\Bar')
        self.assertEqual(p.relative_to(P('c:/')), P('Foo/Bar'))
        self.assertEqual(p.relative_to('c:/'), P('Foo/Bar'))
        self.assertEqual(p.relative_to(P('c:/foO')), P('Bar'))
        self.assertEqual(p.relative_to('c:/foO'), P('Bar'))
        self.assertEqual(p.relative_to('c:/foO/'), P('Bar'))
        self.assertEqual(p.relative_to(P('c:/foO/baR')), P())
        self.assertEqual(p.relative_to('c:/foO/baR'), P())
        # Unrelated paths
        self.assertRaises(ValueError, p.relative_to, P('C:/Baz'))
        self.assertRaises(ValueError, p.relative_to, P('C:/Foo/Bar/Baz'))
        self.assertRaises(ValueError, p.relative_to, P('C:/Foo/Baz'))
        self.assertRaises(ValueError, p.relative_to, P('C:Foo'))
        self.assertRaises(ValueError, p.relative_to, P('d:'))
        self.assertRaises(ValueError, p.relative_to, P('d:/'))
        self.assertRaises(ValueError, p.relative_to, P('/'))
        self.assertRaises(ValueError, p.relative_to, P('/Foo'))
        self.assertRaises(ValueError, p.relative_to, P('//C/Foo'))
        # UNC paths
        p = P('//Server/Share/Foo/Bar')
        self.assertEqual(p.relative_to(P('//sErver/sHare')), P('Foo/Bar'))
        self.assertEqual(p.relative_to('//sErver/sHare'), P('Foo/Bar'))
        self.assertEqual(p.relative_to('//sErver/sHare/'), P('Foo/Bar'))
        self.assertEqual(p.relative_to(P('//sErver/sHare/Foo')), P('Bar'))
        self.assertEqual(p.relative_to('//sErver/sHare/Foo'), P('Bar'))
        self.assertEqual(p.relative_to('//sErver/sHare/Foo/'), P('Bar'))
        self.assertEqual(p.relative_to(P('//sErver/sHare/Foo/Bar')), P())
        self.assertEqual(p.relative_to('//sErver/sHare/Foo/Bar'), P())
        # Unrelated paths
        self.assertRaises(ValueError, p.relative_to, P('/Server/Share/Foo'))
        self.assertRaises(ValueError, p.relative_to, P('c:/Server/Share/Foo'))
        self.assertRaises(ValueError, p.relative_to, P('//z/Share/Foo'))
        self.assertRaises(ValueError, p.relative_to, P('//Server/z/Foo'))

    def test_is_absolute(self):
        P = self.cls
        # Under NT, only paths przy both a drive oraz a root are absolute
        self.assertNieprawda(P().is_absolute())
        self.assertNieprawda(P('a').is_absolute())
        self.assertNieprawda(P('a/b/').is_absolute())
        self.assertNieprawda(P('/').is_absolute())
        self.assertNieprawda(P('/a').is_absolute())
        self.assertNieprawda(P('/a/b/').is_absolute())
        self.assertNieprawda(P('c:').is_absolute())
        self.assertNieprawda(P('c:a').is_absolute())
        self.assertNieprawda(P('c:a/b/').is_absolute())
        self.assertPrawda(P('c:/').is_absolute())
        self.assertPrawda(P('c:/a').is_absolute())
        self.assertPrawda(P('c:/a/b/').is_absolute())
        # UNC paths are absolute by definition
        self.assertPrawda(P('//a/b').is_absolute())
        self.assertPrawda(P('//a/b/').is_absolute())
        self.assertPrawda(P('//a/b/c').is_absolute())
        self.assertPrawda(P('//a/b/c/d').is_absolute())

    def test_join(self):
        P = self.cls
        p = P('C:/a/b')
        pp = p.joinpath('x/y')
        self.assertEqual(pp, P('C:/a/b/x/y'))
        pp = p.joinpath('/x/y')
        self.assertEqual(pp, P('C:/x/y'))
        # Joining przy a different drive => the first path jest ignored, even
        # jeżeli the second path jest relative.
        pp = p.joinpath('D:x/y')
        self.assertEqual(pp, P('D:x/y'))
        pp = p.joinpath('D:/x/y')
        self.assertEqual(pp, P('D:/x/y'))
        pp = p.joinpath('//host/share/x/y')
        self.assertEqual(pp, P('//host/share/x/y'))
        # Joining przy the same drive => the first path jest appended to if
        # the second path jest relative.
        pp = p.joinpath('c:x/y')
        self.assertEqual(pp, P('C:/a/b/x/y'))
        pp = p.joinpath('c:/x/y')
        self.assertEqual(pp, P('C:/x/y'))

    def test_div(self):
        # Basically the same jako joinpath()
        P = self.cls
        p = P('C:/a/b')
        self.assertEqual(p / 'x/y', P('C:/a/b/x/y'))
        self.assertEqual(p / 'x' / 'y', P('C:/a/b/x/y'))
        self.assertEqual(p / '/x/y', P('C:/x/y'))
        self.assertEqual(p / '/x' / 'y', P('C:/x/y'))
        # Joining przy a different drive => the first path jest ignored, even
        # jeżeli the second path jest relative.
        self.assertEqual(p / 'D:x/y', P('D:x/y'))
        self.assertEqual(p / 'D:' / 'x/y', P('D:x/y'))
        self.assertEqual(p / 'D:/x/y', P('D:/x/y'))
        self.assertEqual(p / 'D:' / '/x/y', P('D:/x/y'))
        self.assertEqual(p / '//host/share/x/y', P('//host/share/x/y'))
        # Joining przy the same drive => the first path jest appended to if
        # the second path jest relative.
        self.assertEqual(p / 'c:x/y', P('C:/a/b/x/y'))
        self.assertEqual(p / 'c:/x/y', P('C:/x/y'))

    def test_is_reserved(self):
        P = self.cls
        self.assertIs(Nieprawda, P('').is_reserved())
        self.assertIs(Nieprawda, P('/').is_reserved())
        self.assertIs(Nieprawda, P('/foo/bar').is_reserved())
        self.assertIs(Prawda, P('con').is_reserved())
        self.assertIs(Prawda, P('NUL').is_reserved())
        self.assertIs(Prawda, P('NUL.txt').is_reserved())
        self.assertIs(Prawda, P('com1').is_reserved())
        self.assertIs(Prawda, P('com9.bar').is_reserved())
        self.assertIs(Nieprawda, P('bar.com9').is_reserved())
        self.assertIs(Prawda, P('lpt1').is_reserved())
        self.assertIs(Prawda, P('lpt9.bar').is_reserved())
        self.assertIs(Nieprawda, P('bar.lpt9').is_reserved())
        # Only the last component matters
        self.assertIs(Nieprawda, P('c:/NUL/con/baz').is_reserved())
        # UNC paths are never reserved
        self.assertIs(Nieprawda, P('//my/share/nul/con/aux').is_reserved())


klasa PurePathTest(_BasePurePathTest, unittest.TestCase):
    cls = pathlib.PurePath

    def test_concrete_class(self):
        p = self.cls('a')
        self.assertIs(type(p),
            pathlib.PureWindowsPath jeżeli os.name == 'nt' inaczej pathlib.PurePosixPath)

    def test_different_flavours_unequal(self):
        p = pathlib.PurePosixPath('a')
        q = pathlib.PureWindowsPath('a')
        self.assertNotEqual(p, q)

    def test_different_flavours_unordered(self):
        p = pathlib.PurePosixPath('a')
        q = pathlib.PureWindowsPath('a')
        przy self.assertRaises(TypeError):
            p < q
        przy self.assertRaises(TypeError):
            p <= q
        przy self.assertRaises(TypeError):
            p > q
        przy self.assertRaises(TypeError):
            p >= q


#
# Tests dla the concrete classes
#

# Make sure any symbolic links w the base test path are resolved
BASE = os.path.realpath(TESTFN)
join = lambda *x: os.path.join(BASE, *x)
rel_join = lambda *x: os.path.join(TESTFN, *x)

def symlink_skip_reason():
    jeżeli nie pathlib.supports_symlinks:
        zwróć "no system support dla symlinks"
    spróbuj:
        os.symlink(__file__, BASE)
    wyjąwszy OSError jako e:
        zwróć str(e)
    inaczej:
        support.unlink(BASE)
    zwróć Nic

symlink_skip_reason = symlink_skip_reason()

only_nt = unittest.skipIf(os.name != 'nt',
                          'test requires a Windows-compatible system')
only_posix = unittest.skipIf(os.name == 'nt',
                             'test requires a POSIX-compatible system')
with_symlinks = unittest.skipIf(symlink_skip_reason, symlink_skip_reason)


@only_posix
klasa PosixPathAsPureTest(PurePosixPathTest):
    cls = pathlib.PosixPath

@only_nt
klasa WindowsPathAsPureTest(PureWindowsPathTest):
    cls = pathlib.WindowsPath


klasa _BasePathTest(object):
    """Tests dla the FS-accessing functionalities of the Path classes."""

    # (BASE)
    #  |
    #  |-- dirA/
    #       |-- linkC -> "../dirB"
    #  |-- dirB/
    #  |    |-- fileB
    #       |-- linkD -> "../dirB"
    #  |-- dirC/
    #  |    |-- fileC
    #  |    |-- fileD
    #  |-- fileA
    #  |-- linkA -> "fileA"
    #  |-- linkB -> "dirB"
    #

    def setUp(self):
        os.mkdir(BASE)
        self.addCleanup(support.rmtree, BASE)
        os.mkdir(join('dirA'))
        os.mkdir(join('dirB'))
        os.mkdir(join('dirC'))
        os.mkdir(join('dirC', 'dirD'))
        przy open(join('fileA'), 'wb') jako f:
            f.write(b"this jest file A\n")
        przy open(join('dirB', 'fileB'), 'wb') jako f:
            f.write(b"this jest file B\n")
        przy open(join('dirC', 'fileC'), 'wb') jako f:
            f.write(b"this jest file C\n")
        przy open(join('dirC', 'dirD', 'fileD'), 'wb') jako f:
            f.write(b"this jest file D\n")
        jeżeli nie symlink_skip_reason:
            # Relative symlinks
            os.symlink('fileA', join('linkA'))
            os.symlink('non-existing', join('brokenLink'))
            self.dirlink('dirB', join('linkB'))
            self.dirlink(os.path.join('..', 'dirB'), join('dirA', 'linkC'))
            # This one goes upwards but doesn't create a loop
            self.dirlink(os.path.join('..', 'dirB'), join('dirB', 'linkD'))

    jeżeli os.name == 'nt':
        # Workaround dla http://bugs.python.org/issue13772
        def dirlink(self, src, dest):
            os.symlink(src, dest, target_is_directory=Prawda)
    inaczej:
        def dirlink(self, src, dest):
            os.symlink(src, dest)

    def assertSame(self, path_a, path_b):
        self.assertPrawda(os.path.samefile(str(path_a), str(path_b)),
                        "%r oraz %r don't point to the same file" %
                        (path_a, path_b))

    def assertFileNotFound(self, func, *args, **kwargs):
        przy self.assertRaises(FileNotFoundError) jako cm:
            func(*args, **kwargs)
        self.assertEqual(cm.exception.errno, errno.ENOENT)

    def _test_cwd(self, p):
        q = self.cls(os.getcwd())
        self.assertEqual(p, q)
        self.assertEqual(str(p), str(q))
        self.assertIs(type(p), type(q))
        self.assertPrawda(p.is_absolute())

    def test_cwd(self):
        p = self.cls.cwd()
        self._test_cwd(p)

    def _test_home(self, p):
        q = self.cls(os.path.expanduser('~'))
        self.assertEqual(p, q)
        self.assertEqual(str(p), str(q))
        self.assertIs(type(p), type(q))
        self.assertPrawda(p.is_absolute())

    def test_home(self):
        p = self.cls.home()
        self._test_home(p)

    def test_samefile(self):
        fileA_path = os.path.join(BASE, 'fileA')
        fileB_path = os.path.join(BASE, 'dirB', 'fileB')
        p = self.cls(fileA_path)
        pp = self.cls(fileA_path)
        q = self.cls(fileB_path)
        self.assertPrawda(p.samefile(fileA_path))
        self.assertPrawda(p.samefile(pp))
        self.assertNieprawda(p.samefile(fileB_path))
        self.assertNieprawda(p.samefile(q))
        # Test the non-existent file case
        non_existent = os.path.join(BASE, 'foo')
        r = self.cls(non_existent)
        self.assertRaises(FileNotFoundError, p.samefile, r)
        self.assertRaises(FileNotFoundError, p.samefile, non_existent)
        self.assertRaises(FileNotFoundError, r.samefile, p)
        self.assertRaises(FileNotFoundError, r.samefile, non_existent)
        self.assertRaises(FileNotFoundError, r.samefile, r)
        self.assertRaises(FileNotFoundError, r.samefile, non_existent)

    def test_empty_path(self):
        # The empty path points to '.'
        p = self.cls('')
        self.assertEqual(p.stat(), os.stat('.'))

    def test_expanduser_common(self):
        P = self.cls
        p = P('~')
        self.assertEqual(p.expanduser(), P(os.path.expanduser('~')))
        p = P('foo')
        self.assertEqual(p.expanduser(), p)
        p = P('/~')
        self.assertEqual(p.expanduser(), p)
        p = P('../~')
        self.assertEqual(p.expanduser(), p)
        p = P(P('').absolute().anchor) / '~'
        self.assertEqual(p.expanduser(), p)

    def test_exists(self):
        P = self.cls
        p = P(BASE)
        self.assertIs(Prawda, p.exists())
        self.assertIs(Prawda, (p / 'dirA').exists())
        self.assertIs(Prawda, (p / 'fileA').exists())
        self.assertIs(Nieprawda, (p / 'fileA' / 'bah').exists())
        jeżeli nie symlink_skip_reason:
            self.assertIs(Prawda, (p / 'linkA').exists())
            self.assertIs(Prawda, (p / 'linkB').exists())
            self.assertIs(Prawda, (p / 'linkB' / 'fileB').exists())
            self.assertIs(Nieprawda, (p / 'linkA' / 'bah').exists())
        self.assertIs(Nieprawda, (p / 'foo').exists())
        self.assertIs(Nieprawda, P('/xyzzy').exists())

    def test_open_common(self):
        p = self.cls(BASE)
        przy (p / 'fileA').open('r') jako f:
            self.assertIsInstance(f, io.TextIOBase)
            self.assertEqual(f.read(), "this jest file A\n")
        przy (p / 'fileA').open('rb') jako f:
            self.assertIsInstance(f, io.BufferedIOBase)
            self.assertEqual(f.read().strip(), b"this jest file A")
        przy (p / 'fileA').open('rb', buffering=0) jako f:
            self.assertIsInstance(f, io.RawIOBase)
            self.assertEqual(f.read().strip(), b"this jest file A")

    def test_read_write_bytes(self):
        p = self.cls(BASE)
        (p / 'fileA').write_bytes(b'abcdefg')
        self.assertEqual((p / 'fileA').read_bytes(), b'abcdefg')
        # check that trying to write str does nie truncate the file
        self.assertRaises(TypeError, (p / 'fileA').write_bytes, 'somestr')
        self.assertEqual((p / 'fileA').read_bytes(), b'abcdefg')

    def test_read_write_text(self):
        p = self.cls(BASE)
        (p / 'fileA').write_text('äbcdefg', encoding='latin-1')
        self.assertEqual((p / 'fileA').read_text(
            encoding='utf-8', errors='ignore'), 'bcdefg')
        # check that trying to write bytes does nie truncate the file
        self.assertRaises(TypeError, (p / 'fileA').write_text, b'somebytes')
        self.assertEqual((p / 'fileA').read_text(encoding='latin-1'), 'äbcdefg')

    def test_iterdir(self):
        P = self.cls
        p = P(BASE)
        it = p.iterdir()
        paths = set(it)
        expected = ['dirA', 'dirB', 'dirC', 'fileA']
        jeżeli nie symlink_skip_reason:
            expected += ['linkA', 'linkB', 'brokenLink']
        self.assertEqual(paths, { P(BASE, q) dla q w expected })

    @with_symlinks
    def test_iterdir_symlink(self):
        # __iter__ on a symlink to a directory
        P = self.cls
        p = P(BASE, 'linkB')
        paths = set(p.iterdir())
        expected = { P(BASE, 'linkB', q) dla q w ['fileB', 'linkD'] }
        self.assertEqual(paths, expected)

    def test_iterdir_nodir(self):
        # __iter__ on something that jest nie a directory
        p = self.cls(BASE, 'fileA')
        przy self.assertRaises(OSError) jako cm:
            next(p.iterdir())
        # ENOENT albo EINVAL under Windows, ENOTDIR otherwise
        # (see issue #12802)
        self.assertIn(cm.exception.errno, (errno.ENOTDIR,
                                           errno.ENOENT, errno.EINVAL))

    def test_glob_common(self):
        def _check(glob, expected):
            self.assertEqual(set(glob), { P(BASE, q) dla q w expected })
        P = self.cls
        p = P(BASE)
        it = p.glob("fileA")
        self.assertIsInstance(it, collections.Iterator)
        _check(it, ["fileA"])
        _check(p.glob("fileB"), [])
        _check(p.glob("dir*/file*"), ["dirB/fileB", "dirC/fileC"])
        jeżeli symlink_skip_reason:
            _check(p.glob("*A"), ['dirA', 'fileA'])
        inaczej:
            _check(p.glob("*A"), ['dirA', 'fileA', 'linkA'])
        jeżeli symlink_skip_reason:
            _check(p.glob("*B/*"), ['dirB/fileB'])
        inaczej:
            _check(p.glob("*B/*"), ['dirB/fileB', 'dirB/linkD',
                                    'linkB/fileB', 'linkB/linkD'])
        jeżeli symlink_skip_reason:
            _check(p.glob("*/fileB"), ['dirB/fileB'])
        inaczej:
            _check(p.glob("*/fileB"), ['dirB/fileB', 'linkB/fileB'])

    def test_rglob_common(self):
        def _check(glob, expected):
            self.assertEqual(set(glob), { P(BASE, q) dla q w expected })
        P = self.cls
        p = P(BASE)
        it = p.rglob("fileA")
        self.assertIsInstance(it, collections.Iterator)
        # XXX cannot test because of symlink loops w the test setup
        #_check(it, ["fileA"])
        #_check(p.rglob("fileB"), ["dirB/fileB"])
        #_check(p.rglob("*/fileA"), [""])
        #_check(p.rglob("*/fileB"), ["dirB/fileB"])
        #_check(p.rglob("file*"), ["fileA", "dirB/fileB"])
        # No symlink loops here
        p = P(BASE, "dirC")
        _check(p.rglob("file*"), ["dirC/fileC", "dirC/dirD/fileD"])
        _check(p.rglob("*/*"), ["dirC/dirD/fileD"])

    def test_glob_dotdot(self):
        # ".." jest nie special w globs
        P = self.cls
        p = P(BASE)
        self.assertEqual(set(p.glob("..")), { P(BASE, "..") })
        self.assertEqual(set(p.glob("dirA/../file*")), { P(BASE, "dirA/../fileA") })
        self.assertEqual(set(p.glob("../xyzzy")), set())

    def _check_resolve_relative(self, p, expected):
        q = p.resolve()
        self.assertEqual(q, expected)

    def _check_resolve_absolute(self, p, expected):
        q = p.resolve()
        self.assertEqual(q, expected)

    @with_symlinks
    def test_resolve_common(self):
        P = self.cls
        p = P(BASE, 'foo')
        przy self.assertRaises(OSError) jako cm:
            p.resolve()
        self.assertEqual(cm.exception.errno, errno.ENOENT)
        # These are all relative symlinks
        p = P(BASE, 'dirB', 'fileB')
        self._check_resolve_relative(p, p)
        p = P(BASE, 'linkA')
        self._check_resolve_relative(p, P(BASE, 'fileA'))
        p = P(BASE, 'dirA', 'linkC', 'fileB')
        self._check_resolve_relative(p, P(BASE, 'dirB', 'fileB'))
        p = P(BASE, 'dirB', 'linkD', 'fileB')
        self._check_resolve_relative(p, P(BASE, 'dirB', 'fileB'))
        # Now create absolute symlinks
        d = tempfile.mkdtemp(suffix='-dirD')
        self.addCleanup(support.rmtree, d)
        os.symlink(os.path.join(d), join('dirA', 'linkX'))
        os.symlink(join('dirB'), os.path.join(d, 'linkY'))
        p = P(BASE, 'dirA', 'linkX', 'linkY', 'fileB')
        self._check_resolve_absolute(p, P(BASE, 'dirB', 'fileB'))

    @with_symlinks
    def test_resolve_dot(self):
        # See https://bitbucket.org/pitrou/pathlib/issue/9/pathresolve-fails-on-complex-symlinks
        p = self.cls(BASE)
        self.dirlink('.', join('0'))
        self.dirlink(os.path.join('0', '0'), join('1'))
        self.dirlink(os.path.join('1', '1'), join('2'))
        q = p / '2'
        self.assertEqual(q.resolve(), p)

    def test_with(self):
        p = self.cls(BASE)
        it = p.iterdir()
        it2 = p.iterdir()
        next(it2)
        przy p:
            dalej
        # I/O operation on closed path
        self.assertRaises(ValueError, next, it)
        self.assertRaises(ValueError, next, it2)
        self.assertRaises(ValueError, p.open)
        self.assertRaises(ValueError, p.resolve)
        self.assertRaises(ValueError, p.absolute)
        self.assertRaises(ValueError, p.__enter__)

    def test_chmod(self):
        p = self.cls(BASE) / 'fileA'
        mode = p.stat().st_mode
        # Clear writable bit
        new_mode = mode & ~0o222
        p.chmod(new_mode)
        self.assertEqual(p.stat().st_mode, new_mode)
        # Set writable bit
        new_mode = mode | 0o222
        p.chmod(new_mode)
        self.assertEqual(p.stat().st_mode, new_mode)

    # XXX also need a test dla lchmod

    def test_stat(self):
        p = self.cls(BASE) / 'fileA'
        st = p.stat()
        self.assertEqual(p.stat(), st)
        # Change file mode by flipping write bit
        p.chmod(st.st_mode ^ 0o222)
        self.addCleanup(p.chmod, st.st_mode)
        self.assertNotEqual(p.stat(), st)

    @with_symlinks
    def test_lstat(self):
        p = self.cls(BASE)/ 'linkA'
        st = p.stat()
        self.assertNotEqual(st, p.lstat())

    def test_lstat_nosymlink(self):
        p = self.cls(BASE) / 'fileA'
        st = p.stat()
        self.assertEqual(st, p.lstat())

    @unittest.skipUnless(pwd, "the pwd module jest needed dla this test")
    def test_owner(self):
        p = self.cls(BASE) / 'fileA'
        uid = p.stat().st_uid
        spróbuj:
            name = pwd.getpwuid(uid).pw_name
        wyjąwszy KeyError:
            self.skipTest(
                "user %d doesn't have an entry w the system database" % uid)
        self.assertEqual(name, p.owner())

    @unittest.skipUnless(grp, "the grp module jest needed dla this test")
    def test_group(self):
        p = self.cls(BASE) / 'fileA'
        gid = p.stat().st_gid
        spróbuj:
            name = grp.getgrgid(gid).gr_name
        wyjąwszy KeyError:
            self.skipTest(
                "group %d doesn't have an entry w the system database" % gid)
        self.assertEqual(name, p.group())

    def test_unlink(self):
        p = self.cls(BASE) / 'fileA'
        p.unlink()
        self.assertFileNotFound(p.stat)
        self.assertFileNotFound(p.unlink)

    def test_rmdir(self):
        p = self.cls(BASE) / 'dirA'
        dla q w p.iterdir():
            q.unlink()
        p.rmdir()
        self.assertFileNotFound(p.stat)
        self.assertFileNotFound(p.unlink)

    def test_rename(self):
        P = self.cls(BASE)
        p = P / 'fileA'
        size = p.stat().st_size
        # Renaming to another path
        q = P / 'dirA' / 'fileAA'
        p.rename(q)
        self.assertEqual(q.stat().st_size, size)
        self.assertFileNotFound(p.stat)
        # Renaming to a str of a relative path
        r = rel_join('fileAAA')
        q.rename(r)
        self.assertEqual(os.stat(r).st_size, size)
        self.assertFileNotFound(q.stat)

    def test_replace(self):
        P = self.cls(BASE)
        p = P / 'fileA'
        size = p.stat().st_size
        # Replacing a non-existing path
        q = P / 'dirA' / 'fileAA'
        p.replace(q)
        self.assertEqual(q.stat().st_size, size)
        self.assertFileNotFound(p.stat)
        # Replacing another (existing) path
        r = rel_join('dirB', 'fileB')
        q.replace(r)
        self.assertEqual(os.stat(r).st_size, size)
        self.assertFileNotFound(q.stat)

    def test_touch_common(self):
        P = self.cls(BASE)
        p = P / 'newfileA'
        self.assertNieprawda(p.exists())
        p.touch()
        self.assertPrawda(p.exists())
        st = p.stat()
        old_mtime = st.st_mtime
        old_mtime_ns = st.st_mtime_ns
        # Rewind the mtime sufficiently far w the past to work around
        # filesystem-specific timestamp granularity.
        os.utime(str(p), (old_mtime - 10, old_mtime - 10))
        # The file mtime should be refreshed by calling touch() again
        p.touch()
        st = p.stat()
        self.assertGreaterEqual(st.st_mtime_ns, old_mtime_ns)
        self.assertGreaterEqual(st.st_mtime, old_mtime)
        # Now przy exist_ok=Nieprawda
        p = P / 'newfileB'
        self.assertNieprawda(p.exists())
        p.touch(mode=0o700, exist_ok=Nieprawda)
        self.assertPrawda(p.exists())
        self.assertRaises(OSError, p.touch, exist_ok=Nieprawda)

    def test_touch_nochange(self):
        P = self.cls(BASE)
        p = P / 'fileA'
        p.touch()
        przy p.open('rb') jako f:
            self.assertEqual(f.read().strip(), b"this jest file A")

    def test_mkdir(self):
        P = self.cls(BASE)
        p = P / 'newdirA'
        self.assertNieprawda(p.exists())
        p.mkdir()
        self.assertPrawda(p.exists())
        self.assertPrawda(p.is_dir())
        przy self.assertRaises(OSError) jako cm:
            p.mkdir()
        self.assertEqual(cm.exception.errno, errno.EEXIST)

    def test_mkdir_parents(self):
        # Creating a chain of directories
        p = self.cls(BASE, 'newdirB', 'newdirC')
        self.assertNieprawda(p.exists())
        przy self.assertRaises(OSError) jako cm:
            p.mkdir()
        self.assertEqual(cm.exception.errno, errno.ENOENT)
        p.mkdir(parents=Prawda)
        self.assertPrawda(p.exists())
        self.assertPrawda(p.is_dir())
        przy self.assertRaises(OSError) jako cm:
            p.mkdir(parents=Prawda)
        self.assertEqual(cm.exception.errno, errno.EEXIST)
        # test `mode` arg
        mode = stat.S_IMODE(p.stat().st_mode) # default mode
        p = self.cls(BASE, 'newdirD', 'newdirE')
        p.mkdir(0o555, parents=Prawda)
        self.assertPrawda(p.exists())
        self.assertPrawda(p.is_dir())
        jeżeli os.name != 'nt':
            # the directory's permissions follow the mode argument
            self.assertEqual(stat.S_IMODE(p.stat().st_mode), 0o7555 & mode)
        # the parent's permissions follow the default process settings
        self.assertEqual(stat.S_IMODE(p.parent.stat().st_mode), mode)

    def test_mkdir_exist_ok(self):
        p = self.cls(BASE, 'dirB')
        st_ctime_first = p.stat().st_ctime
        self.assertPrawda(p.exists())
        self.assertPrawda(p.is_dir())
        przy self.assertRaises(FileExistsError) jako cm:
            p.mkdir()
        self.assertEqual(cm.exception.errno, errno.EEXIST)
        p.mkdir(exist_ok=Prawda)
        self.assertPrawda(p.exists())
        self.assertEqual(p.stat().st_ctime, st_ctime_first)

    def test_mkdir_exist_ok_with_parent(self):
        p = self.cls(BASE, 'dirC')
        self.assertPrawda(p.exists())
        przy self.assertRaises(FileExistsError) jako cm:
            p.mkdir()
        self.assertEqual(cm.exception.errno, errno.EEXIST)
        p = p / 'newdirC'
        p.mkdir(parents=Prawda)
        st_ctime_first = p.stat().st_ctime
        self.assertPrawda(p.exists())
        przy self.assertRaises(FileExistsError) jako cm:
            p.mkdir(parents=Prawda)
        self.assertEqual(cm.exception.errno, errno.EEXIST)
        p.mkdir(parents=Prawda, exist_ok=Prawda)
        self.assertPrawda(p.exists())
        self.assertEqual(p.stat().st_ctime, st_ctime_first)

    def test_mkdir_with_child_file(self):
        p = self.cls(BASE, 'dirB', 'fileB')
        self.assertPrawda(p.exists())
        # An exception jest podnieśd when the last path component jest an existing
        # regular file, regardless of whether exist_ok jest true albo not.
        przy self.assertRaises(FileExistsError) jako cm:
            p.mkdir(parents=Prawda)
        self.assertEqual(cm.exception.errno, errno.EEXIST)
        przy self.assertRaises(FileExistsError) jako cm:
            p.mkdir(parents=Prawda, exist_ok=Prawda)
        self.assertEqual(cm.exception.errno, errno.EEXIST)

    def test_mkdir_no_parents_file(self):
        p = self.cls(BASE, 'fileA')
        self.assertPrawda(p.exists())
        # An exception jest podnieśd when the last path component jest an existing
        # regular file, regardless of whether exist_ok jest true albo not.
        przy self.assertRaises(FileExistsError) jako cm:
            p.mkdir()
        self.assertEqual(cm.exception.errno, errno.EEXIST)
        przy self.assertRaises(FileExistsError) jako cm:
            p.mkdir(exist_ok=Prawda)
        self.assertEqual(cm.exception.errno, errno.EEXIST)

    @with_symlinks
    def test_symlink_to(self):
        P = self.cls(BASE)
        target = P / 'fileA'
        # Symlinking a path target
        link = P / 'dirA' / 'linkAA'
        link.symlink_to(target)
        self.assertEqual(link.stat(), target.stat())
        self.assertNotEqual(link.lstat(), target.stat())
        # Symlinking a str target
        link = P / 'dirA' / 'linkAAA'
        link.symlink_to(str(target))
        self.assertEqual(link.stat(), target.stat())
        self.assertNotEqual(link.lstat(), target.stat())
        self.assertNieprawda(link.is_dir())
        # Symlinking to a directory
        target = P / 'dirB'
        link = P / 'dirA' / 'linkAAAA'
        link.symlink_to(target, target_is_directory=Prawda)
        self.assertEqual(link.stat(), target.stat())
        self.assertNotEqual(link.lstat(), target.stat())
        self.assertPrawda(link.is_dir())
        self.assertPrawda(list(link.iterdir()))

    def test_is_dir(self):
        P = self.cls(BASE)
        self.assertPrawda((P / 'dirA').is_dir())
        self.assertNieprawda((P / 'fileA').is_dir())
        self.assertNieprawda((P / 'non-existing').is_dir())
        self.assertNieprawda((P / 'fileA' / 'bah').is_dir())
        jeżeli nie symlink_skip_reason:
            self.assertNieprawda((P / 'linkA').is_dir())
            self.assertPrawda((P / 'linkB').is_dir())
            self.assertNieprawda((P/ 'brokenLink').is_dir())

    def test_is_file(self):
        P = self.cls(BASE)
        self.assertPrawda((P / 'fileA').is_file())
        self.assertNieprawda((P / 'dirA').is_file())
        self.assertNieprawda((P / 'non-existing').is_file())
        self.assertNieprawda((P / 'fileA' / 'bah').is_file())
        jeżeli nie symlink_skip_reason:
            self.assertPrawda((P / 'linkA').is_file())
            self.assertNieprawda((P / 'linkB').is_file())
            self.assertNieprawda((P/ 'brokenLink').is_file())

    def test_is_symlink(self):
        P = self.cls(BASE)
        self.assertNieprawda((P / 'fileA').is_symlink())
        self.assertNieprawda((P / 'dirA').is_symlink())
        self.assertNieprawda((P / 'non-existing').is_symlink())
        self.assertNieprawda((P / 'fileA' / 'bah').is_symlink())
        jeżeli nie symlink_skip_reason:
            self.assertPrawda((P / 'linkA').is_symlink())
            self.assertPrawda((P / 'linkB').is_symlink())
            self.assertPrawda((P/ 'brokenLink').is_symlink())

    def test_is_fifo_false(self):
        P = self.cls(BASE)
        self.assertNieprawda((P / 'fileA').is_fifo())
        self.assertNieprawda((P / 'dirA').is_fifo())
        self.assertNieprawda((P / 'non-existing').is_fifo())
        self.assertNieprawda((P / 'fileA' / 'bah').is_fifo())

    @unittest.skipUnless(hasattr(os, "mkfifo"), "os.mkfifo() required")
    def test_is_fifo_true(self):
        P = self.cls(BASE, 'myfifo')
        os.mkfifo(str(P))
        self.assertPrawda(P.is_fifo())
        self.assertNieprawda(P.is_socket())
        self.assertNieprawda(P.is_file())

    def test_is_socket_false(self):
        P = self.cls(BASE)
        self.assertNieprawda((P / 'fileA').is_socket())
        self.assertNieprawda((P / 'dirA').is_socket())
        self.assertNieprawda((P / 'non-existing').is_socket())
        self.assertNieprawda((P / 'fileA' / 'bah').is_socket())

    @unittest.skipUnless(hasattr(socket, "AF_UNIX"), "Unix sockets required")
    def test_is_socket_true(self):
        P = self.cls(BASE, 'mysock')
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.addCleanup(sock.close)
        spróbuj:
            sock.bind(str(P))
        wyjąwszy OSError jako e:
            jeżeli "AF_UNIX path too long" w str(e):
                self.skipTest("cannot bind Unix socket: " + str(e))
        self.assertPrawda(P.is_socket())
        self.assertNieprawda(P.is_fifo())
        self.assertNieprawda(P.is_file())

    def test_is_block_device_false(self):
        P = self.cls(BASE)
        self.assertNieprawda((P / 'fileA').is_block_device())
        self.assertNieprawda((P / 'dirA').is_block_device())
        self.assertNieprawda((P / 'non-existing').is_block_device())
        self.assertNieprawda((P / 'fileA' / 'bah').is_block_device())

    def test_is_char_device_false(self):
        P = self.cls(BASE)
        self.assertNieprawda((P / 'fileA').is_char_device())
        self.assertNieprawda((P / 'dirA').is_char_device())
        self.assertNieprawda((P / 'non-existing').is_char_device())
        self.assertNieprawda((P / 'fileA' / 'bah').is_char_device())

    def test_is_char_device_true(self):
        # Under Unix, /dev/null should generally be a char device
        P = self.cls('/dev/null')
        jeżeli nie P.exists():
            self.skipTest("/dev/null required")
        self.assertPrawda(P.is_char_device())
        self.assertNieprawda(P.is_block_device())
        self.assertNieprawda(P.is_file())

    def test_pickling_common(self):
        p = self.cls(BASE, 'fileA')
        dla proto w range(0, pickle.HIGHEST_PROTOCOL + 1):
            dumped = pickle.dumps(p, proto)
            pp = pickle.loads(dumped)
            self.assertEqual(pp.stat(), p.stat())

    def test_parts_interning(self):
        P = self.cls
        p = P('/usr/bin/foo')
        q = P('/usr/local/bin')
        # 'usr'
        self.assertIs(p.parts[1], q.parts[1])
        # 'bin'
        self.assertIs(p.parts[2], q.parts[3])

    def _check_complex_symlinks(self, link0_target):
        # Test solving a non-looping chain of symlinks (issue #19887)
        P = self.cls(BASE)
        self.dirlink(os.path.join('link0', 'link0'), join('link1'))
        self.dirlink(os.path.join('link1', 'link1'), join('link2'))
        self.dirlink(os.path.join('link2', 'link2'), join('link3'))
        self.dirlink(link0_target, join('link0'))

        # Resolve absolute paths
        p = (P / 'link0').resolve()
        self.assertEqual(p, P)
        self.assertEqual(str(p), BASE)
        p = (P / 'link1').resolve()
        self.assertEqual(p, P)
        self.assertEqual(str(p), BASE)
        p = (P / 'link2').resolve()
        self.assertEqual(p, P)
        self.assertEqual(str(p), BASE)
        p = (P / 'link3').resolve()
        self.assertEqual(p, P)
        self.assertEqual(str(p), BASE)

        # Resolve relative paths
        old_path = os.getcwd()
        os.chdir(BASE)
        spróbuj:
            p = self.cls('link0').resolve()
            self.assertEqual(p, P)
            self.assertEqual(str(p), BASE)
            p = self.cls('link1').resolve()
            self.assertEqual(p, P)
            self.assertEqual(str(p), BASE)
            p = self.cls('link2').resolve()
            self.assertEqual(p, P)
            self.assertEqual(str(p), BASE)
            p = self.cls('link3').resolve()
            self.assertEqual(p, P)
            self.assertEqual(str(p), BASE)
        w_końcu:
            os.chdir(old_path)

    @with_symlinks
    def test_complex_symlinks_absolute(self):
        self._check_complex_symlinks(BASE)

    @with_symlinks
    def test_complex_symlinks_relative(self):
        self._check_complex_symlinks('.')

    @with_symlinks
    def test_complex_symlinks_relative_dot_dot(self):
        self._check_complex_symlinks(os.path.join('dirA', '..'))


klasa PathTest(_BasePathTest, unittest.TestCase):
    cls = pathlib.Path

    def test_concrete_class(self):
        p = self.cls('a')
        self.assertIs(type(p),
            pathlib.WindowsPath jeżeli os.name == 'nt' inaczej pathlib.PosixPath)

    def test_unsupported_flavour(self):
        jeżeli os.name == 'nt':
            self.assertRaises(NotImplementedError, pathlib.PosixPath)
        inaczej:
            self.assertRaises(NotImplementedError, pathlib.WindowsPath)


@only_posix
klasa PosixPathTest(_BasePathTest, unittest.TestCase):
    cls = pathlib.PosixPath

    def _check_symlink_loop(self, *args):
        path = self.cls(*args)
        przy self.assertRaises(RuntimeError):
            print(path.resolve())

    def test_open_mode(self):
        old_mask = os.umask(0)
        self.addCleanup(os.umask, old_mask)
        p = self.cls(BASE)
        przy (p / 'new_file').open('wb'):
            dalej
        st = os.stat(join('new_file'))
        self.assertEqual(stat.S_IMODE(st.st_mode), 0o666)
        os.umask(0o022)
        przy (p / 'other_new_file').open('wb'):
            dalej
        st = os.stat(join('other_new_file'))
        self.assertEqual(stat.S_IMODE(st.st_mode), 0o644)

    def test_touch_mode(self):
        old_mask = os.umask(0)
        self.addCleanup(os.umask, old_mask)
        p = self.cls(BASE)
        (p / 'new_file').touch()
        st = os.stat(join('new_file'))
        self.assertEqual(stat.S_IMODE(st.st_mode), 0o666)
        os.umask(0o022)
        (p / 'other_new_file').touch()
        st = os.stat(join('other_new_file'))
        self.assertEqual(stat.S_IMODE(st.st_mode), 0o644)
        (p / 'masked_new_file').touch(mode=0o750)
        st = os.stat(join('masked_new_file'))
        self.assertEqual(stat.S_IMODE(st.st_mode), 0o750)

    @with_symlinks
    def test_resolve_loop(self):
        # Loop detection dla broken symlinks under POSIX
        # Loops przy relative symlinks
        os.symlink('linkX/inside', join('linkX'))
        self._check_symlink_loop(BASE, 'linkX')
        os.symlink('linkY', join('linkY'))
        self._check_symlink_loop(BASE, 'linkY')
        os.symlink('linkZ/../linkZ', join('linkZ'))
        self._check_symlink_loop(BASE, 'linkZ')
        # Loops przy absolute symlinks
        os.symlink(join('linkU/inside'), join('linkU'))
        self._check_symlink_loop(BASE, 'linkU')
        os.symlink(join('linkV'), join('linkV'))
        self._check_symlink_loop(BASE, 'linkV')
        os.symlink(join('linkW/../linkW'), join('linkW'))
        self._check_symlink_loop(BASE, 'linkW')

    def test_glob(self):
        P = self.cls
        p = P(BASE)
        given = set(p.glob("FILEa"))
        expect = set() jeżeli nie support.fs_is_case_insensitive(BASE) inaczej given
        self.assertEqual(given, expect)
        self.assertEqual(set(p.glob("FILEa*")), set())

    def test_rglob(self):
        P = self.cls
        p = P(BASE, "dirC")
        given = set(p.rglob("FILEd"))
        expect = set() jeżeli nie support.fs_is_case_insensitive(BASE) inaczej given
        self.assertEqual(given, expect)
        self.assertEqual(set(p.rglob("FILEd*")), set())

    def test_expanduser(self):
        P = self.cls
        support.import_module('pwd')
        zaimportuj pwd
        pwdent = pwd.getpwuid(os.getuid())
        username = pwdent.pw_name
        userhome = pwdent.pw_dir.rstrip('/')
        # find arbitrary different user (jeżeli exists)
        dla pwdent w pwd.getpwall():
            othername = pwdent.pw_name
            otherhome = pwdent.pw_dir.rstrip('/')
            jeżeli othername != username oraz otherhome:
                przerwij

        p1 = P('~/Documents')
        p2 = P('~' + username + '/Documents')
        p3 = P('~' + othername + '/Documents')
        p4 = P('../~' + username + '/Documents')
        p5 = P('/~' + username + '/Documents')
        p6 = P('')
        p7 = P('~fakeuser/Documents')

        przy support.EnvironmentVarGuard() jako env:
            env.pop('HOME', Nic)

            self.assertEqual(p1.expanduser(), P(userhome) / 'Documents')
            self.assertEqual(p2.expanduser(), P(userhome) / 'Documents')
            self.assertEqual(p3.expanduser(), P(otherhome) / 'Documents')
            self.assertEqual(p4.expanduser(), p4)
            self.assertEqual(p5.expanduser(), p5)
            self.assertEqual(p6.expanduser(), p6)
            self.assertRaises(RuntimeError, p7.expanduser)

            env['HOME'] = '/tmp'
            self.assertEqual(p1.expanduser(), P('/tmp/Documents'))
            self.assertEqual(p2.expanduser(), P(userhome) / 'Documents')
            self.assertEqual(p3.expanduser(), P(otherhome) / 'Documents')
            self.assertEqual(p4.expanduser(), p4)
            self.assertEqual(p5.expanduser(), p5)
            self.assertEqual(p6.expanduser(), p6)
            self.assertRaises(RuntimeError, p7.expanduser)


@only_nt
klasa WindowsPathTest(_BasePathTest, unittest.TestCase):
    cls = pathlib.WindowsPath

    def test_glob(self):
        P = self.cls
        p = P(BASE)
        self.assertEqual(set(p.glob("FILEa")), { P(BASE, "fileA") })

    def test_rglob(self):
        P = self.cls
        p = P(BASE, "dirC")
        self.assertEqual(set(p.rglob("FILEd")), { P(BASE, "dirC/dirD/fileD") })

    def test_expanduser(self):
        P = self.cls
        przy support.EnvironmentVarGuard() jako env:
            env.pop('HOME', Nic)
            env.pop('USERPROFILE', Nic)
            env.pop('HOMEPATH', Nic)
            env.pop('HOMEDRIVE', Nic)
            env['USERNAME'] = 'alice'

            # test that the path returns unchanged
            p1 = P('~/My Documents')
            p2 = P('~alice/My Documents')
            p3 = P('~bob/My Documents')
            p4 = P('/~/My Documents')
            p5 = P('d:~/My Documents')
            p6 = P('')
            self.assertRaises(RuntimeError, p1.expanduser)
            self.assertRaises(RuntimeError, p2.expanduser)
            self.assertRaises(RuntimeError, p3.expanduser)
            self.assertEqual(p4.expanduser(), p4)
            self.assertEqual(p5.expanduser(), p5)
            self.assertEqual(p6.expanduser(), p6)

            def check():
                env.pop('USERNAME', Nic)
                self.assertEqual(p1.expanduser(),
                                 P('C:/Users/alice/My Documents'))
                self.assertRaises(KeyError, p2.expanduser)
                env['USERNAME'] = 'alice'
                self.assertEqual(p2.expanduser(),
                                 P('C:/Users/alice/My Documents'))
                self.assertEqual(p3.expanduser(),
                                 P('C:/Users/bob/My Documents'))
                self.assertEqual(p4.expanduser(), p4)
                self.assertEqual(p5.expanduser(), p5)
                self.assertEqual(p6.expanduser(), p6)

            # test the first lookup key w the env vars
            env['HOME'] = 'C:\\Users\\alice'
            check()

            # test that HOMEPATH jest available instead
            env.pop('HOME', Nic)
            env['HOMEPATH'] = 'C:\\Users\\alice'
            check()

            env['HOMEDRIVE'] = 'C:\\'
            env['HOMEPATH'] = 'Users\\alice'
            check()

            env.pop('HOMEDRIVE', Nic)
            env.pop('HOMEPATH', Nic)
            env['USERPROFILE'] = 'C:\\Users\\alice'
            check()


jeżeli __name__ == "__main__":
    unittest.main()
