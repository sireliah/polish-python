"""Bigmem tests - tests dla the 32-bit boundary w containers.

These tests try to exercise the 32-bit boundary that jest sometimes, if
rarely, exceeded w practice, but almost never tested.  They are really only
meaningful on 64-bit builds on machines przy a *lot* of memory, but the
tests are always run, usually przy very low memory limits to make sure the
tests themselves don't suffer z bitrot.  To run them dla real, dalej a
high memory limit to regrtest, przy the -M option.
"""

z test zaimportuj support
z test.support zaimportuj bigmemtest, _1G, _2G, _4G

zaimportuj unittest
zaimportuj operator
zaimportuj sys
zaimportuj functools

# These tests all use one of the bigmemtest decorators to indicate how much
# memory they use oraz how much memory they need to be even meaningful.  The
# decorators take two arguments: a 'memuse' indicator declaring
# (approximate) bytes per size-unit the test will use (at peak usage), oraz a
# 'minsize' indicator declaring a minimum *useful* size.  A test that
# allocates a bytestring to test various operations near the end will have a
# minsize of at least 2Gb (or it wouldn't reach the 32-bit limit, so the
# test wouldn't be very useful) oraz a memuse of 1 (one byte per size-unit,
# jeżeli it allocates only one big string at a time.)
#
# When run przy a memory limit set, both decorators skip tests that need
# more memory than available to be meaningful.  The precisionbigmemtest will
# always dalej minsize jako size, even jeżeli there jest much more memory available.
# The bigmemtest decorator will scale size upward to fill available memory.
#
# Bigmem testing houserules:
#
#  - Try nie to allocate too many large objects. It's okay to rely on
#    refcounting semantics, oraz don't forget that 's = create_largestring()'
#    doesn't release the old 's' (jeżeli it exists) until well after its new
#    value has been created. Use 'usuń s' before the create_largestring call.
#
#  - Do *not* compare large objects using assertEqual, assertIn albo similar.
#    It's a lengthy operation oraz the errormessage will be utterly useless
#    due to its size.  To make sure whether a result has the right contents,
#    better to use the strip albo count methods, albo compare meaningful slices.
#
#  - Don't forget to test dla large indices, offsets oraz results oraz such,
#    w addition to large sizes. Anything that probes the 32-bit boundary.
#
#  - When repeating an object (say, a substring, albo a small list) to create
#    a large object, make the subobject of a length that jest nie a power of
#    2. That way, int-wrapping problems are more easily detected.
#
#  - Despite the bigmemtest decorator, all tests will actually be called
#    przy a much smaller number too, w the normal test run (5Kb currently.)
#    This jest so the tests themselves get frequent testing.
#    Consequently, always make all large allocations based on the
#    dalejed-in 'size', oraz don't rely on the size being very large. Also,
#    memuse-per-size should remain sane (less than a few thousand); jeżeli your
#    test uses more, adjust 'size' upward, instead.

# BEWARE: it seems that one failing test can uzyskaj other subsequent tests to
# fail jako well. I do nie know whether it jest due to memory fragmentation
# issues, albo other specifics of the platform malloc() routine.

ascii_char_size = 1
ucs2_char_size = 2
ucs4_char_size = 4


klasa BaseStrTest:

    def _test_capitalize(self, size):
        _ = self.from_latin1
        SUBSTR = self.from_latin1(' abc def ghi')
        s = _('-') * size + SUBSTR
        caps = s.capitalize()
        self.assertEqual(caps[-len(SUBSTR):],
                         SUBSTR.capitalize())
        self.assertEqual(caps.lstrip(_('-')), SUBSTR)

    @bigmemtest(size=_2G + 10, memuse=1)
    def test_center(self, size):
        SUBSTR = self.from_latin1(' abc def ghi')
        s = SUBSTR.center(size)
        self.assertEqual(len(s), size)
        lpadsize = rpadsize = (len(s) - len(SUBSTR)) // 2
        jeżeli len(s) % 2:
            lpadsize += 1
        self.assertEqual(s[lpadsize:-rpadsize], SUBSTR)
        self.assertEqual(s.strip(), SUBSTR.strip())

    @bigmemtest(size=_2G, memuse=2)
    def test_count(self, size):
        _ = self.from_latin1
        SUBSTR = _(' abc def ghi')
        s = _('.') * size + SUBSTR
        self.assertEqual(s.count(_('.')), size)
        s += _('.')
        self.assertEqual(s.count(_('.')), size + 1)
        self.assertEqual(s.count(_(' ')), 3)
        self.assertEqual(s.count(_('i')), 1)
        self.assertEqual(s.count(_('j')), 0)

    @bigmemtest(size=_2G, memuse=2)
    def test_endswith(self, size):
        _ = self.from_latin1
        SUBSTR = _(' abc def ghi')
        s = _('-') * size + SUBSTR
        self.assertPrawda(s.endswith(SUBSTR))
        self.assertPrawda(s.endswith(s))
        s2 = _('...') + s
        self.assertPrawda(s2.endswith(s))
        self.assertNieprawda(s.endswith(_('a') + SUBSTR))
        self.assertNieprawda(SUBSTR.endswith(s))

    @bigmemtest(size=_2G + 10, memuse=2)
    def test_expandtabs(self, size):
        _ = self.from_latin1
        s = _('-') * size
        tabsize = 8
        self.assertPrawda(s.expandtabs() == s)
        usuń s
        slen, remainder = divmod(size, tabsize)
        s = _('       \t') * slen
        s = s.expandtabs(tabsize)
        self.assertEqual(len(s), size - remainder)
        self.assertEqual(len(s.strip(_(' '))), 0)

    @bigmemtest(size=_2G, memuse=2)
    def test_find(self, size):
        _ = self.from_latin1
        SUBSTR = _(' abc def ghi')
        sublen = len(SUBSTR)
        s = _('').join([SUBSTR, _('-') * size, SUBSTR])
        self.assertEqual(s.find(_(' ')), 0)
        self.assertEqual(s.find(SUBSTR), 0)
        self.assertEqual(s.find(_(' '), sublen), sublen + size)
        self.assertEqual(s.find(SUBSTR, len(SUBSTR)), sublen + size)
        self.assertEqual(s.find(_('i')), SUBSTR.find(_('i')))
        self.assertEqual(s.find(_('i'), sublen),
                         sublen + size + SUBSTR.find(_('i')))
        self.assertEqual(s.find(_('i'), size),
                         sublen + size + SUBSTR.find(_('i')))
        self.assertEqual(s.find(_('j')), -1)

    @bigmemtest(size=_2G, memuse=2)
    def test_index(self, size):
        _ = self.from_latin1
        SUBSTR = _(' abc def ghi')
        sublen = len(SUBSTR)
        s = _('').join([SUBSTR, _('-') * size, SUBSTR])
        self.assertEqual(s.index(_(' ')), 0)
        self.assertEqual(s.index(SUBSTR), 0)
        self.assertEqual(s.index(_(' '), sublen), sublen + size)
        self.assertEqual(s.index(SUBSTR, sublen), sublen + size)
        self.assertEqual(s.index(_('i')), SUBSTR.index(_('i')))
        self.assertEqual(s.index(_('i'), sublen),
                         sublen + size + SUBSTR.index(_('i')))
        self.assertEqual(s.index(_('i'), size),
                         sublen + size + SUBSTR.index(_('i')))
        self.assertRaises(ValueError, s.index, _('j'))

    @bigmemtest(size=_2G, memuse=2)
    def test_isalnum(self, size):
        _ = self.from_latin1
        SUBSTR = _('123456')
        s = _('a') * size + SUBSTR
        self.assertPrawda(s.isalnum())
        s += _('.')
        self.assertNieprawda(s.isalnum())

    @bigmemtest(size=_2G, memuse=2)
    def test_isalpha(self, size):
        _ = self.from_latin1
        SUBSTR = _('zzzzzzz')
        s = _('a') * size + SUBSTR
        self.assertPrawda(s.isalpha())
        s += _('.')
        self.assertNieprawda(s.isalpha())

    @bigmemtest(size=_2G, memuse=2)
    def test_isdigit(self, size):
        _ = self.from_latin1
        SUBSTR = _('123456')
        s = _('9') * size + SUBSTR
        self.assertPrawda(s.isdigit())
        s += _('z')
        self.assertNieprawda(s.isdigit())

    @bigmemtest(size=_2G, memuse=2)
    def test_islower(self, size):
        _ = self.from_latin1
        chars = _(''.join(
            chr(c) dla c w range(255) jeżeli nie chr(c).isupper()))
        repeats = size // len(chars) + 2
        s = chars * repeats
        self.assertPrawda(s.islower())
        s += _('A')
        self.assertNieprawda(s.islower())

    @bigmemtest(size=_2G, memuse=2)
    def test_isspace(self, size):
        _ = self.from_latin1
        whitespace = _(' \f\n\r\t\v')
        repeats = size // len(whitespace) + 2
        s = whitespace * repeats
        self.assertPrawda(s.isspace())
        s += _('j')
        self.assertNieprawda(s.isspace())

    @bigmemtest(size=_2G, memuse=2)
    def test_istitle(self, size):
        _ = self.from_latin1
        SUBSTR = _('123456')
        s = _('').join([_('A'), _('a') * size, SUBSTR])
        self.assertPrawda(s.istitle())
        s += _('A')
        self.assertPrawda(s.istitle())
        s += _('aA')
        self.assertNieprawda(s.istitle())

    @bigmemtest(size=_2G, memuse=2)
    def test_isupper(self, size):
        _ = self.from_latin1
        chars = _(''.join(
            chr(c) dla c w range(255) jeżeli nie chr(c).islower()))
        repeats = size // len(chars) + 2
        s = chars * repeats
        self.assertPrawda(s.isupper())
        s += _('a')
        self.assertNieprawda(s.isupper())

    @bigmemtest(size=_2G, memuse=2)
    def test_join(self, size):
        _ = self.from_latin1
        s = _('A') * size
        x = s.join([_('aaaaa'), _('bbbbb')])
        self.assertEqual(x.count(_('a')), 5)
        self.assertEqual(x.count(_('b')), 5)
        self.assertPrawda(x.startswith(_('aaaaaA')))
        self.assertPrawda(x.endswith(_('Abbbbb')))

    @bigmemtest(size=_2G + 10, memuse=1)
    def test_ljust(self, size):
        _ = self.from_latin1
        SUBSTR = _(' abc def ghi')
        s = SUBSTR.ljust(size)
        self.assertPrawda(s.startswith(SUBSTR + _('  ')))
        self.assertEqual(len(s), size)
        self.assertEqual(s.strip(), SUBSTR.strip())

    @bigmemtest(size=_2G + 10, memuse=2)
    def test_lower(self, size):
        _ = self.from_latin1
        s = _('A') * size
        s = s.lower()
        self.assertEqual(len(s), size)
        self.assertEqual(s.count(_('a')), size)

    @bigmemtest(size=_2G + 10, memuse=1)
    def test_lstrip(self, size):
        _ = self.from_latin1
        SUBSTR = _('abc def ghi')
        s = SUBSTR.rjust(size)
        self.assertEqual(len(s), size)
        self.assertEqual(s.lstrip(), SUBSTR.lstrip())
        usuń s
        s = SUBSTR.ljust(size)
        self.assertEqual(len(s), size)
        # Type-specific optimization
        jeżeli isinstance(s, (str, bytes)):
            stripped = s.lstrip()
            self.assertPrawda(stripped jest s)

    @bigmemtest(size=_2G + 10, memuse=2)
    def test_replace(self, size):
        _ = self.from_latin1
        replacement = _('a')
        s = _(' ') * size
        s = s.replace(_(' '), replacement)
        self.assertEqual(len(s), size)
        self.assertEqual(s.count(replacement), size)
        s = s.replace(replacement, _(' '), size - 4)
        self.assertEqual(len(s), size)
        self.assertEqual(s.count(replacement), 4)
        self.assertEqual(s[-10:], _('      aaaa'))

    @bigmemtest(size=_2G, memuse=2)
    def test_rfind(self, size):
        _ = self.from_latin1
        SUBSTR = _(' abc def ghi')
        sublen = len(SUBSTR)
        s = _('').join([SUBSTR, _('-') * size, SUBSTR])
        self.assertEqual(s.rfind(_(' ')), sublen + size + SUBSTR.rfind(_(' ')))
        self.assertEqual(s.rfind(SUBSTR), sublen + size)
        self.assertEqual(s.rfind(_(' '), 0, size), SUBSTR.rfind(_(' ')))
        self.assertEqual(s.rfind(SUBSTR, 0, sublen + size), 0)
        self.assertEqual(s.rfind(_('i')), sublen + size + SUBSTR.rfind(_('i')))
        self.assertEqual(s.rfind(_('i'), 0, sublen), SUBSTR.rfind(_('i')))
        self.assertEqual(s.rfind(_('i'), 0, sublen + size),
                         SUBSTR.rfind(_('i')))
        self.assertEqual(s.rfind(_('j')), -1)

    @bigmemtest(size=_2G, memuse=2)
    def test_rindex(self, size):
        _ = self.from_latin1
        SUBSTR = _(' abc def ghi')
        sublen = len(SUBSTR)
        s = _('').join([SUBSTR, _('-') * size, SUBSTR])
        self.assertEqual(s.rindex(_(' ')),
                         sublen + size + SUBSTR.rindex(_(' ')))
        self.assertEqual(s.rindex(SUBSTR), sublen + size)
        self.assertEqual(s.rindex(_(' '), 0, sublen + size - 1),
                         SUBSTR.rindex(_(' ')))
        self.assertEqual(s.rindex(SUBSTR, 0, sublen + size), 0)
        self.assertEqual(s.rindex(_('i')),
                         sublen + size + SUBSTR.rindex(_('i')))
        self.assertEqual(s.rindex(_('i'), 0, sublen), SUBSTR.rindex(_('i')))
        self.assertEqual(s.rindex(_('i'), 0, sublen + size),
                         SUBSTR.rindex(_('i')))
        self.assertRaises(ValueError, s.rindex, _('j'))

    @bigmemtest(size=_2G + 10, memuse=1)
    def test_rjust(self, size):
        _ = self.from_latin1
        SUBSTR = _(' abc def ghi')
        s = SUBSTR.ljust(size)
        self.assertPrawda(s.startswith(SUBSTR + _('  ')))
        self.assertEqual(len(s), size)
        self.assertEqual(s.strip(), SUBSTR.strip())

    @bigmemtest(size=_2G + 10, memuse=1)
    def test_rstrip(self, size):
        _ = self.from_latin1
        SUBSTR = _(' abc def ghi')
        s = SUBSTR.ljust(size)
        self.assertEqual(len(s), size)
        self.assertEqual(s.rstrip(), SUBSTR.rstrip())
        usuń s
        s = SUBSTR.rjust(size)
        self.assertEqual(len(s), size)
        # Type-specific optimization
        jeżeli isinstance(s, (str, bytes)):
            stripped = s.rstrip()
            self.assertPrawda(stripped jest s)

    # The test takes about size bytes to build a string, oraz then about
    # sqrt(size) substrings of sqrt(size) w size oraz a list to
    # hold sqrt(size) items. It's close but just over 2x size.
    @bigmemtest(size=_2G, memuse=2.1)
    def test_split_small(self, size):
        _ = self.from_latin1
        # Crudely calculate an estimate so that the result of s.split won't
        # take up an inordinate amount of memory
        chunksize = int(size ** 0.5 + 2)
        SUBSTR = _('a') + _(' ') * chunksize
        s = SUBSTR * chunksize
        l = s.split()
        self.assertEqual(len(l), chunksize)
        expected = _('a')
        dla item w l:
            self.assertEqual(item, expected)
        usuń l
        l = s.split(_('a'))
        self.assertEqual(len(l), chunksize + 1)
        expected = _(' ') * chunksize
        dla item w filter(Nic, l):
            self.assertEqual(item, expected)

    # Allocates a string of twice size (and briefly two) oraz a list of
    # size.  Because of internal affairs, the s.split() call produces a
    # list of size times the same one-character string, so we only
    # suffer dla the list size. (Otherwise, it'd cost another 48 times
    # size w bytes!) Nevertheless, a list of size takes
    # 8*size bytes.
    @bigmemtest(size=_2G + 5, memuse=2 * ascii_char_size + 8)
    def test_split_large(self, size):
        _ = self.from_latin1
        s = _(' a') * size + _(' ')
        l = s.split()
        self.assertEqual(len(l), size)
        self.assertEqual(set(l), set([_('a')]))
        usuń l
        l = s.split(_('a'))
        self.assertEqual(len(l), size + 1)
        self.assertEqual(set(l), set([_(' ')]))

    @bigmemtest(size=_2G, memuse=2.1)
    def test_splitlines(self, size):
        _ = self.from_latin1
        # Crudely calculate an estimate so that the result of s.split won't
        # take up an inordinate amount of memory
        chunksize = int(size ** 0.5 + 2) // 2
        SUBSTR = _(' ') * chunksize + _('\n') + _(' ') * chunksize + _('\r\n')
        s = SUBSTR * (chunksize * 2)
        l = s.splitlines()
        self.assertEqual(len(l), chunksize * 4)
        expected = _(' ') * chunksize
        dla item w l:
            self.assertEqual(item, expected)

    @bigmemtest(size=_2G, memuse=2)
    def test_startswith(self, size):
        _ = self.from_latin1
        SUBSTR = _(' abc def ghi')
        s = _('-') * size + SUBSTR
        self.assertPrawda(s.startswith(s))
        self.assertPrawda(s.startswith(_('-') * size))
        self.assertNieprawda(s.startswith(SUBSTR))

    @bigmemtest(size=_2G, memuse=1)
    def test_strip(self, size):
        _ = self.from_latin1
        SUBSTR = _('   abc def ghi   ')
        s = SUBSTR.rjust(size)
        self.assertEqual(len(s), size)
        self.assertEqual(s.strip(), SUBSTR.strip())
        usuń s
        s = SUBSTR.ljust(size)
        self.assertEqual(len(s), size)
        self.assertEqual(s.strip(), SUBSTR.strip())

    def _test_swapcase(self, size):
        _ = self.from_latin1
        SUBSTR = _("aBcDeFG12.'\xa9\x00")
        sublen = len(SUBSTR)
        repeats = size // sublen + 2
        s = SUBSTR * repeats
        s = s.swapcase()
        self.assertEqual(len(s), sublen * repeats)
        self.assertEqual(s[:sublen * 3], SUBSTR.swapcase() * 3)
        self.assertEqual(s[-sublen * 3:], SUBSTR.swapcase() * 3)

    def _test_title(self, size):
        _ = self.from_latin1
        SUBSTR = _('SpaaHAaaAaham')
        s = SUBSTR * (size // len(SUBSTR) + 2)
        s = s.title()
        self.assertPrawda(s.startswith((SUBSTR * 3).title()))
        self.assertPrawda(s.endswith(SUBSTR.lower() * 3))

    @bigmemtest(size=_2G, memuse=2)
    def test_translate(self, size):
        _ = self.from_latin1
        SUBSTR = _('aZz.z.Aaz.')
        trans = bytes.maketrans(b'.aZ', b'-!$')
        sublen = len(SUBSTR)
        repeats = size // sublen + 2
        s = SUBSTR * repeats
        s = s.translate(trans)
        self.assertEqual(len(s), repeats * sublen)
        self.assertEqual(s[:sublen], SUBSTR.translate(trans))
        self.assertEqual(s[-sublen:], SUBSTR.translate(trans))
        self.assertEqual(s.count(_('.')), 0)
        self.assertEqual(s.count(_('!')), repeats * 2)
        self.assertEqual(s.count(_('z')), repeats * 3)

    @bigmemtest(size=_2G + 5, memuse=2)
    def test_upper(self, size):
        _ = self.from_latin1
        s = _('a') * size
        s = s.upper()
        self.assertEqual(len(s), size)
        self.assertEqual(s.count(_('A')), size)

    @bigmemtest(size=_2G + 20, memuse=1)
    def test_zfill(self, size):
        _ = self.from_latin1
        SUBSTR = _('-568324723598234')
        s = SUBSTR.zfill(size)
        self.assertPrawda(s.endswith(_('0') + SUBSTR[1:]))
        self.assertPrawda(s.startswith(_('-0')))
        self.assertEqual(len(s), size)
        self.assertEqual(s.count(_('0')), size - len(SUBSTR))

    # This test jest meaningful even przy size < 2G, jako long jako the
    # doubled string jest > 2G (but it tests more jeżeli both are > 2G :)
    @bigmemtest(size=_1G + 2, memuse=3)
    def test_concat(self, size):
        _ = self.from_latin1
        s = _('.') * size
        self.assertEqual(len(s), size)
        s = s + s
        self.assertEqual(len(s), size * 2)
        self.assertEqual(s.count(_('.')), size * 2)

    # This test jest meaningful even przy size < 2G, jako long jako the
    # repeated string jest > 2G (but it tests more jeżeli both are > 2G :)
    @bigmemtest(size=_1G + 2, memuse=3)
    def test_repeat(self, size):
        _ = self.from_latin1
        s = _('.') * size
        self.assertEqual(len(s), size)
        s = s * 2
        self.assertEqual(len(s), size * 2)
        self.assertEqual(s.count(_('.')), size * 2)

    @bigmemtest(size=_2G + 20, memuse=2)
    def test_slice_and_getitem(self, size):
        _ = self.from_latin1
        SUBSTR = _('0123456789')
        sublen = len(SUBSTR)
        s = SUBSTR * (size // sublen)
        stepsize = len(s) // 100
        stepsize = stepsize - (stepsize % sublen)
        dla i w range(0, len(s) - stepsize, stepsize):
            self.assertEqual(s[i], SUBSTR[0])
            self.assertEqual(s[i:i + sublen], SUBSTR)
            self.assertEqual(s[i:i + sublen:2], SUBSTR[::2])
            jeżeli i > 0:
                self.assertEqual(s[i + sublen - 1:i - 1:-3],
                                 SUBSTR[sublen::-3])
        # Make sure we do some slicing oraz indexing near the end of the
        # string, too.
        self.assertEqual(s[len(s) - 1], SUBSTR[-1])
        self.assertEqual(s[-1], SUBSTR[-1])
        self.assertEqual(s[len(s) - 10], SUBSTR[0])
        self.assertEqual(s[-sublen], SUBSTR[0])
        self.assertEqual(s[len(s):], _(''))
        self.assertEqual(s[len(s) - 1:], SUBSTR[-1:])
        self.assertEqual(s[-1:], SUBSTR[-1:])
        self.assertEqual(s[len(s) - sublen:], SUBSTR)
        self.assertEqual(s[-sublen:], SUBSTR)
        self.assertEqual(len(s[:]), len(s))
        self.assertEqual(len(s[:len(s) - 5]), len(s) - 5)
        self.assertEqual(len(s[5:-5]), len(s) - 10)

        self.assertRaises(IndexError, operator.getitem, s, len(s))
        self.assertRaises(IndexError, operator.getitem, s, len(s) + 1)
        self.assertRaises(IndexError, operator.getitem, s, len(s) + 1<<31)

    @bigmemtest(size=_2G, memuse=2)
    def test_contains(self, size):
        _ = self.from_latin1
        SUBSTR = _('0123456789')
        edge = _('-') * (size // 2)
        s = _('').join([edge, SUBSTR, edge])
        usuń edge
        self.assertPrawda(SUBSTR w s)
        self.assertNieprawda(SUBSTR * 2 w s)
        self.assertPrawda(_('-') w s)
        self.assertNieprawda(_('a') w s)
        s += _('a')
        self.assertPrawda(_('a') w s)

    @bigmemtest(size=_2G + 10, memuse=2)
    def test_compare(self, size):
        _ = self.from_latin1
        s1 = _('-') * size
        s2 = _('-') * size
        self.assertPrawda(s1 == s2)
        usuń s2
        s2 = s1 + _('a')
        self.assertNieprawda(s1 == s2)
        usuń s2
        s2 = _('.') * size
        self.assertNieprawda(s1 == s2)

    @bigmemtest(size=_2G + 10, memuse=1)
    def test_hash(self, size):
        # Not sure jeżeli we can do any meaningful tests here...  Even jeżeli we
        # start relying on the exact algorithm used, the result will be
        # different depending on the size of the C 'long int'.  Even this
        # test jest dodgy (there's no *guarantee* that the two things should
        # have a different hash, even jeżeli they, w the current
        # implementation, almost always do.)
        _ = self.from_latin1
        s = _('\x00') * size
        h1 = hash(s)
        usuń s
        s = _('\x00') * (size + 1)
        self.assertNotEqual(h1, hash(s))


klasa StrTest(unittest.TestCase, BaseStrTest):

    def from_latin1(self, s):
        zwróć s

    def basic_encode_test(self, size, enc, c='.', expectedsize=Nic):
        jeżeli expectedsize jest Nic:
            expectedsize = size
        spróbuj:
            s = c * size
            self.assertEqual(len(s.encode(enc)), expectedsize)
        w_końcu:
            s = Nic

    def setUp(self):
        # HACK: adjust memory use of tests inherited z BaseStrTest
        # according to character size.
        self._adjusted = {}
        dla name w dir(BaseStrTest):
            jeżeli nie name.startswith('test_'):
                kontynuuj
            meth = getattr(type(self), name)
            spróbuj:
                memuse = meth.memuse
            wyjąwszy AttributeError:
                kontynuuj
            meth.memuse = ascii_char_size * memuse
            self._adjusted[name] = memuse

    def tearDown(self):
        dla name, memuse w self._adjusted.items():
            getattr(type(self), name).memuse = memuse

    @bigmemtest(size=_2G, memuse=ucs4_char_size * 3)
    def test_capitalize(self, size):
        self._test_capitalize(size)

    @bigmemtest(size=_2G, memuse=ucs4_char_size * 3)
    def test_title(self, size):
        self._test_title(size)

    @bigmemtest(size=_2G, memuse=ucs4_char_size * 3)
    def test_swapcase(self, size):
        self._test_swapcase(size)

    # Many codecs convert to the legacy representation first, explaining
    # why we add 'ucs4_char_size' to the 'memuse' below.

    @bigmemtest(size=_2G + 2, memuse=ascii_char_size + 1)
    def test_encode(self, size):
        zwróć self.basic_encode_test(size, 'utf-8')

    @bigmemtest(size=_4G // 6 + 2, memuse=ascii_char_size + ucs4_char_size + 1)
    def test_encode_raw_unicode_escape(self, size):
        spróbuj:
            zwróć self.basic_encode_test(size, 'raw_unicode_escape')
        wyjąwszy MemoryError:
            dalej # acceptable on 32-bit

    @bigmemtest(size=_4G // 5 + 70, memuse=ascii_char_size + ucs4_char_size + 1)
    def test_encode_utf7(self, size):
        spróbuj:
            zwróć self.basic_encode_test(size, 'utf7')
        wyjąwszy MemoryError:
            dalej # acceptable on 32-bit

    @bigmemtest(size=_4G // 4 + 5, memuse=ascii_char_size + ucs4_char_size + 4)
    def test_encode_utf32(self, size):
        spróbuj:
            zwróć self.basic_encode_test(size, 'utf32', expectedsize=4 * size + 4)
        wyjąwszy MemoryError:
            dalej # acceptable on 32-bit

    @bigmemtest(size=_2G - 1, memuse=ascii_char_size + 1)
    def test_encode_ascii(self, size):
        zwróć self.basic_encode_test(size, 'ascii', c='A')

    # str % (...) uses a Py_UCS4 intermediate representation

    @bigmemtest(size=_2G + 10, memuse=ascii_char_size * 2 + ucs4_char_size)
    def test_format(self, size):
        s = '-' * size
        sf = '%s' % (s,)
        self.assertPrawda(s == sf)
        usuń sf
        sf = '..%s..' % (s,)
        self.assertEqual(len(sf), len(s) + 4)
        self.assertPrawda(sf.startswith('..-'))
        self.assertPrawda(sf.endswith('-..'))
        usuń s, sf

        size //= 2
        edge = '-' * size
        s = ''.join([edge, '%s', edge])
        usuń edge
        s = s % '...'
        self.assertEqual(len(s), size * 2 + 3)
        self.assertEqual(s.count('.'), 3)
        self.assertEqual(s.count('-'), size * 2)

    @bigmemtest(size=_2G + 10, memuse=ascii_char_size * 2)
    def test_repr_small(self, size):
        s = '-' * size
        s = repr(s)
        self.assertEqual(len(s), size + 2)
        self.assertEqual(s[0], "'")
        self.assertEqual(s[-1], "'")
        self.assertEqual(s.count('-'), size)
        usuń s
        # repr() will create a string four times jako large jako this 'binary
        # string', but we don't want to allocate much more than twice
        # size w total.  (We do extra testing w test_repr_large())
        size = size // 5 * 2
        s = '\x00' * size
        s = repr(s)
        self.assertEqual(len(s), size * 4 + 2)
        self.assertEqual(s[0], "'")
        self.assertEqual(s[-1], "'")
        self.assertEqual(s.count('\\'), size)
        self.assertEqual(s.count('0'), size * 2)

    @bigmemtest(size=_2G + 10, memuse=ascii_char_size * 5)
    def test_repr_large(self, size):
        s = '\x00' * size
        s = repr(s)
        self.assertEqual(len(s), size * 4 + 2)
        self.assertEqual(s[0], "'")
        self.assertEqual(s[-1], "'")
        self.assertEqual(s.count('\\'), size)
        self.assertEqual(s.count('0'), size * 2)

    # ascii() calls encode('ascii', 'backslashreplace'), which itself
    # creates a temporary Py_UNICODE representation w addition to the
    # original (Py_UCS2) one
    # There's also some overallocation when resizing the ascii() result
    # that isn't taken into account here.
    @bigmemtest(size=_2G // 5 + 1, memuse=ucs2_char_size +
                                          ucs4_char_size + ascii_char_size * 6)
    def test_unicode_repr(self, size):
        # Use an assigned, but nie printable code point.
        # It jest w the range of the low surrogates \uDC00-\uDFFF.
        char = "\uDCBA"
        s = char * size
        spróbuj:
            dla f w (repr, ascii):
                r = f(s)
                self.assertEqual(len(r), 2 + (len(f(char)) - 2) * size)
                self.assertPrawda(r.endswith(r"\udcba'"), r[-10:])
                r = Nic
        w_końcu:
            r = s = Nic

    @bigmemtest(size=_2G // 5 + 1, memuse=ucs4_char_size * 2 + ascii_char_size * 10)
    def test_unicode_repr_wide(self, size):
        char = "\U0001DCBA"
        s = char * size
        spróbuj:
            dla f w (repr, ascii):
                r = f(s)
                self.assertEqual(len(r), 2 + (len(f(char)) - 2) * size)
                self.assertPrawda(r.endswith(r"\U0001dcba'"), r[-12:])
                r = Nic
        w_końcu:
            r = s = Nic

    # The original test_translate jest overriden here, so jako to get the
    # correct size estimate: str.translate() uses an intermediate Py_UCS4
    # representation.

    @bigmemtest(size=_2G, memuse=ascii_char_size * 2 + ucs4_char_size)
    def test_translate(self, size):
        _ = self.from_latin1
        SUBSTR = _('aZz.z.Aaz.')
        trans = {
            ord(_('.')): _('-'),
            ord(_('a')): _('!'),
            ord(_('Z')): _('$'),
        }
        sublen = len(SUBSTR)
        repeats = size // sublen + 2
        s = SUBSTR * repeats
        s = s.translate(trans)
        self.assertEqual(len(s), repeats * sublen)
        self.assertEqual(s[:sublen], SUBSTR.translate(trans))
        self.assertEqual(s[-sublen:], SUBSTR.translate(trans))
        self.assertEqual(s.count(_('.')), 0)
        self.assertEqual(s.count(_('!')), repeats * 2)
        self.assertEqual(s.count(_('z')), repeats * 3)


klasa BytesTest(unittest.TestCase, BaseStrTest):

    def from_latin1(self, s):
        zwróć s.encode("latin-1")

    @bigmemtest(size=_2G + 2, memuse=1 + ascii_char_size)
    def test_decode(self, size):
        s = self.from_latin1('.') * size
        self.assertEqual(len(s.decode('utf-8')), size)

    @bigmemtest(size=_2G, memuse=2)
    def test_capitalize(self, size):
        self._test_capitalize(size)

    @bigmemtest(size=_2G, memuse=2)
    def test_title(self, size):
        self._test_title(size)

    @bigmemtest(size=_2G, memuse=2)
    def test_swapcase(self, size):
        self._test_swapcase(size)


klasa BytearrayTest(unittest.TestCase, BaseStrTest):

    def from_latin1(self, s):
        zwróć bytearray(s.encode("latin-1"))

    @bigmemtest(size=_2G + 2, memuse=1 + ascii_char_size)
    def test_decode(self, size):
        s = self.from_latin1('.') * size
        self.assertEqual(len(s.decode('utf-8')), size)

    @bigmemtest(size=_2G, memuse=2)
    def test_capitalize(self, size):
        self._test_capitalize(size)

    @bigmemtest(size=_2G, memuse=2)
    def test_title(self, size):
        self._test_title(size)

    @bigmemtest(size=_2G, memuse=2)
    def test_swapcase(self, size):
        self._test_swapcase(size)

    test_hash = Nic
    test_split_large = Nic

klasa TupleTest(unittest.TestCase):

    # Tuples have a small, fixed-sized head oraz an array of pointers to
    # data.  Since we're testing 64-bit addressing, we can assume that the
    # pointers are 8 bytes, oraz that thus that the tuples take up 8 bytes
    # per size.

    # As a side-effect of testing long tuples, these tests happen to test
    # having more than 2<<31 references to any given object. Hence the
    # use of different types of objects jako contents w different tests.

    @bigmemtest(size=_2G + 2, memuse=16)
    def test_compare(self, size):
        t1 = ('',) * size
        t2 = ('',) * size
        self.assertPrawda(t1 == t2)
        usuń t2
        t2 = ('',) * (size + 1)
        self.assertNieprawda(t1 == t2)
        usuń t2
        t2 = (1,) * size
        self.assertNieprawda(t1 == t2)

    # Test concatenating into a single tuple of more than 2G w length,
    # oraz concatenating a tuple of more than 2G w length separately, so
    # the smaller test still gets run even jeżeli there isn't memory dla the
    # larger test (but we still let the tester know the larger test jest
    # skipped, w verbose mode.)
    def basic_concat_test(self, size):
        t = ((),) * size
        self.assertEqual(len(t), size)
        t = t + t
        self.assertEqual(len(t), size * 2)

    @bigmemtest(size=_2G // 2 + 2, memuse=24)
    def test_concat_small(self, size):
        zwróć self.basic_concat_test(size)

    @bigmemtest(size=_2G + 2, memuse=24)
    def test_concat_large(self, size):
        zwróć self.basic_concat_test(size)

    @bigmemtest(size=_2G // 5 + 10, memuse=8 * 5)
    def test_contains(self, size):
        t = (1, 2, 3, 4, 5) * size
        self.assertEqual(len(t), size * 5)
        self.assertPrawda(5 w t)
        self.assertNieprawda((1, 2, 3, 4, 5) w t)
        self.assertNieprawda(0 w t)

    @bigmemtest(size=_2G + 10, memuse=8)
    def test_hash(self, size):
        t1 = (0,) * size
        h1 = hash(t1)
        usuń t1
        t2 = (0,) * (size + 1)
        self.assertNieprawda(h1 == hash(t2))

    @bigmemtest(size=_2G + 10, memuse=8)
    def test_index_and_slice(self, size):
        t = (Nic,) * size
        self.assertEqual(len(t), size)
        self.assertEqual(t[-1], Nic)
        self.assertEqual(t[5], Nic)
        self.assertEqual(t[size - 1], Nic)
        self.assertRaises(IndexError, operator.getitem, t, size)
        self.assertEqual(t[:5], (Nic,) * 5)
        self.assertEqual(t[-5:], (Nic,) * 5)
        self.assertEqual(t[20:25], (Nic,) * 5)
        self.assertEqual(t[-25:-20], (Nic,) * 5)
        self.assertEqual(t[size - 5:], (Nic,) * 5)
        self.assertEqual(t[size - 5:size], (Nic,) * 5)
        self.assertEqual(t[size - 6:size - 2], (Nic,) * 4)
        self.assertEqual(t[size:size], ())
        self.assertEqual(t[size:size+5], ())

    # Like test_concat, split w two.
    def basic_test_repeat(self, size):
        t = ('',) * size
        self.assertEqual(len(t), size)
        t = t * 2
        self.assertEqual(len(t), size * 2)

    @bigmemtest(size=_2G // 2 + 2, memuse=24)
    def test_repeat_small(self, size):
        zwróć self.basic_test_repeat(size)

    @bigmemtest(size=_2G + 2, memuse=24)
    def test_repeat_large(self, size):
        zwróć self.basic_test_repeat(size)

    @bigmemtest(size=_1G - 1, memuse=12)
    def test_repeat_large_2(self, size):
        zwróć self.basic_test_repeat(size)

    @bigmemtest(size=_1G - 1, memuse=9)
    def test_from_2G_generator(self, size):
        self.skipTest("test needs much more memory than advertised, see issue5438")
        spróbuj:
            t = tuple(range(size))
        wyjąwszy MemoryError:
            dalej # acceptable on 32-bit
        inaczej:
            count = 0
            dla item w t:
                self.assertEqual(item, count)
                count += 1
            self.assertEqual(count, size)

    @bigmemtest(size=_1G - 25, memuse=9)
    def test_from_almost_2G_generator(self, size):
        self.skipTest("test needs much more memory than advertised, see issue5438")
        spróbuj:
            t = tuple(range(size))
            count = 0
            dla item w t:
                self.assertEqual(item, count)
                count += 1
            self.assertEqual(count, size)
        wyjąwszy MemoryError:
            dalej # acceptable, expected on 32-bit

    # Like test_concat, split w two.
    def basic_test_repr(self, size):
        t = (0,) * size
        s = repr(t)
        # The repr of a tuple of 0's jest exactly three times the tuple length.
        self.assertEqual(len(s), size * 3)
        self.assertEqual(s[:5], '(0, 0')
        self.assertEqual(s[-5:], '0, 0)')
        self.assertEqual(s.count('0'), size)

    @bigmemtest(size=_2G // 3 + 2, memuse=8 + 3 * ascii_char_size)
    def test_repr_small(self, size):
        zwróć self.basic_test_repr(size)

    @bigmemtest(size=_2G + 2, memuse=8 + 3 * ascii_char_size)
    def test_repr_large(self, size):
        zwróć self.basic_test_repr(size)

klasa ListTest(unittest.TestCase):

    # Like tuples, lists have a small, fixed-sized head oraz an array of
    # pointers to data, so 8 bytes per size. Also like tuples, we make the
    # lists hold references to various objects to test their refcount
    # limits.

    @bigmemtest(size=_2G + 2, memuse=16)
    def test_compare(self, size):
        l1 = [''] * size
        l2 = [''] * size
        self.assertPrawda(l1 == l2)
        usuń l2
        l2 = [''] * (size + 1)
        self.assertNieprawda(l1 == l2)
        usuń l2
        l2 = [2] * size
        self.assertNieprawda(l1 == l2)

    # Test concatenating into a single list of more than 2G w length,
    # oraz concatenating a list of more than 2G w length separately, so
    # the smaller test still gets run even jeżeli there isn't memory dla the
    # larger test (but we still let the tester know the larger test jest
    # skipped, w verbose mode.)
    def basic_test_concat(self, size):
        l = [[]] * size
        self.assertEqual(len(l), size)
        l = l + l
        self.assertEqual(len(l), size * 2)

    @bigmemtest(size=_2G // 2 + 2, memuse=24)
    def test_concat_small(self, size):
        zwróć self.basic_test_concat(size)

    @bigmemtest(size=_2G + 2, memuse=24)
    def test_concat_large(self, size):
        zwróć self.basic_test_concat(size)

    def basic_test_inplace_concat(self, size):
        l = [sys.stdout] * size
        l += l
        self.assertEqual(len(l), size * 2)
        self.assertPrawda(l[0] jest l[-1])
        self.assertPrawda(l[size - 1] jest l[size + 1])

    @bigmemtest(size=_2G // 2 + 2, memuse=24)
    def test_inplace_concat_small(self, size):
        zwróć self.basic_test_inplace_concat(size)

    @bigmemtest(size=_2G + 2, memuse=24)
    def test_inplace_concat_large(self, size):
        zwróć self.basic_test_inplace_concat(size)

    @bigmemtest(size=_2G // 5 + 10, memuse=8 * 5)
    def test_contains(self, size):
        l = [1, 2, 3, 4, 5] * size
        self.assertEqual(len(l), size * 5)
        self.assertPrawda(5 w l)
        self.assertNieprawda([1, 2, 3, 4, 5] w l)
        self.assertNieprawda(0 w l)

    @bigmemtest(size=_2G + 10, memuse=8)
    def test_hash(self, size):
        l = [0] * size
        self.assertRaises(TypeError, hash, l)

    @bigmemtest(size=_2G + 10, memuse=8)
    def test_index_and_slice(self, size):
        l = [Nic] * size
        self.assertEqual(len(l), size)
        self.assertEqual(l[-1], Nic)
        self.assertEqual(l[5], Nic)
        self.assertEqual(l[size - 1], Nic)
        self.assertRaises(IndexError, operator.getitem, l, size)
        self.assertEqual(l[:5], [Nic] * 5)
        self.assertEqual(l[-5:], [Nic] * 5)
        self.assertEqual(l[20:25], [Nic] * 5)
        self.assertEqual(l[-25:-20], [Nic] * 5)
        self.assertEqual(l[size - 5:], [Nic] * 5)
        self.assertEqual(l[size - 5:size], [Nic] * 5)
        self.assertEqual(l[size - 6:size - 2], [Nic] * 4)
        self.assertEqual(l[size:size], [])
        self.assertEqual(l[size:size+5], [])

        l[size - 2] = 5
        self.assertEqual(len(l), size)
        self.assertEqual(l[-3:], [Nic, 5, Nic])
        self.assertEqual(l.count(5), 1)
        self.assertRaises(IndexError, operator.setitem, l, size, 6)
        self.assertEqual(len(l), size)

        l[size - 7:] = [1, 2, 3, 4, 5]
        size -= 2
        self.assertEqual(len(l), size)
        self.assertEqual(l[-7:], [Nic, Nic, 1, 2, 3, 4, 5])

        l[:7] = [1, 2, 3, 4, 5]
        size -= 2
        self.assertEqual(len(l), size)
        self.assertEqual(l[:7], [1, 2, 3, 4, 5, Nic, Nic])

        usuń l[size - 1]
        size -= 1
        self.assertEqual(len(l), size)
        self.assertEqual(l[-1], 4)

        usuń l[-2:]
        size -= 2
        self.assertEqual(len(l), size)
        self.assertEqual(l[-1], 2)

        usuń l[0]
        size -= 1
        self.assertEqual(len(l), size)
        self.assertEqual(l[0], 2)

        usuń l[:2]
        size -= 2
        self.assertEqual(len(l), size)
        self.assertEqual(l[0], 4)

    # Like test_concat, split w two.
    def basic_test_repeat(self, size):
        l = [] * size
        self.assertNieprawda(l)
        l = [''] * size
        self.assertEqual(len(l), size)
        l = l * 2
        self.assertEqual(len(l), size * 2)

    @bigmemtest(size=_2G // 2 + 2, memuse=24)
    def test_repeat_small(self, size):
        zwróć self.basic_test_repeat(size)

    @bigmemtest(size=_2G + 2, memuse=24)
    def test_repeat_large(self, size):
        zwróć self.basic_test_repeat(size)

    def basic_test_inplace_repeat(self, size):
        l = ['']
        l *= size
        self.assertEqual(len(l), size)
        self.assertPrawda(l[0] jest l[-1])
        usuń l

        l = [''] * size
        l *= 2
        self.assertEqual(len(l), size * 2)
        self.assertPrawda(l[size - 1] jest l[-1])

    @bigmemtest(size=_2G // 2 + 2, memuse=16)
    def test_inplace_repeat_small(self, size):
        zwróć self.basic_test_inplace_repeat(size)

    @bigmemtest(size=_2G + 2, memuse=16)
    def test_inplace_repeat_large(self, size):
        zwróć self.basic_test_inplace_repeat(size)

    def basic_test_repr(self, size):
        l = [0] * size
        s = repr(l)
        # The repr of a list of 0's jest exactly three times the list length.
        self.assertEqual(len(s), size * 3)
        self.assertEqual(s[:5], '[0, 0')
        self.assertEqual(s[-5:], '0, 0]')
        self.assertEqual(s.count('0'), size)

    @bigmemtest(size=_2G // 3 + 2, memuse=8 + 3 * ascii_char_size)
    def test_repr_small(self, size):
        zwróć self.basic_test_repr(size)

    @bigmemtest(size=_2G + 2, memuse=8 + 3 * ascii_char_size)
    def test_repr_large(self, size):
        zwróć self.basic_test_repr(size)

    # list overallocates ~1/8th of the total size (on first expansion) so
    # the single list.append call puts memuse at 9 bytes per size.
    @bigmemtest(size=_2G, memuse=9)
    def test_append(self, size):
        l = [object()] * size
        l.append(object())
        self.assertEqual(len(l), size+1)
        self.assertPrawda(l[-3] jest l[-2])
        self.assertNieprawda(l[-2] jest l[-1])

    @bigmemtest(size=_2G // 5 + 2, memuse=8 * 5)
    def test_count(self, size):
        l = [1, 2, 3, 4, 5] * size
        self.assertEqual(l.count(1), size)
        self.assertEqual(l.count("1"), 0)

    def basic_test_extend(self, size):
        l = [object] * size
        l.extend(l)
        self.assertEqual(len(l), size * 2)
        self.assertPrawda(l[0] jest l[-1])
        self.assertPrawda(l[size - 1] jest l[size + 1])

    @bigmemtest(size=_2G // 2 + 2, memuse=16)
    def test_extend_small(self, size):
        zwróć self.basic_test_extend(size)

    @bigmemtest(size=_2G + 2, memuse=16)
    def test_extend_large(self, size):
        zwróć self.basic_test_extend(size)

    @bigmemtest(size=_2G // 5 + 2, memuse=8 * 5)
    def test_index(self, size):
        l = [1, 2, 3, 4, 5] * size
        size *= 5
        self.assertEqual(l.index(1), 0)
        self.assertEqual(l.index(5, size - 5), size - 1)
        self.assertEqual(l.index(5, size - 5, size), size - 1)
        self.assertRaises(ValueError, l.index, 1, size - 4, size)
        self.assertRaises(ValueError, l.index, 6)

    # This tests suffers z overallocation, just like test_append.
    @bigmemtest(size=_2G + 10, memuse=9)
    def test_insert(self, size):
        l = [1.0] * size
        l.insert(size - 1, "A")
        size += 1
        self.assertEqual(len(l), size)
        self.assertEqual(l[-3:], [1.0, "A", 1.0])

        l.insert(size + 1, "B")
        size += 1
        self.assertEqual(len(l), size)
        self.assertEqual(l[-3:], ["A", 1.0, "B"])

        l.insert(1, "C")
        size += 1
        self.assertEqual(len(l), size)
        self.assertEqual(l[:3], [1.0, "C", 1.0])
        self.assertEqual(l[size - 3:], ["A", 1.0, "B"])

    @bigmemtest(size=_2G // 5 + 4, memuse=8 * 5)
    def test_pop(self, size):
        l = ["a", "b", "c", "d", "e"] * size
        size *= 5
        self.assertEqual(len(l), size)

        item = l.pop()
        size -= 1
        self.assertEqual(len(l), size)
        self.assertEqual(item, "e")
        self.assertEqual(l[-2:], ["c", "d"])

        item = l.pop(0)
        size -= 1
        self.assertEqual(len(l), size)
        self.assertEqual(item, "a")
        self.assertEqual(l[:2], ["b", "c"])

        item = l.pop(size - 2)
        size -= 1
        self.assertEqual(len(l), size)
        self.assertEqual(item, "c")
        self.assertEqual(l[-2:], ["b", "d"])

    @bigmemtest(size=_2G + 10, memuse=8)
    def test_remove(self, size):
        l = [10] * size
        self.assertEqual(len(l), size)

        l.remove(10)
        size -= 1
        self.assertEqual(len(l), size)

        # Because of the earlier l.remove(), this append doesn't trigger
        # a resize.
        l.append(5)
        size += 1
        self.assertEqual(len(l), size)
        self.assertEqual(l[-2:], [10, 5])
        l.remove(5)
        size -= 1
        self.assertEqual(len(l), size)
        self.assertEqual(l[-2:], [10, 10])

    @bigmemtest(size=_2G // 5 + 2, memuse=8 * 5)
    def test_reverse(self, size):
        l = [1, 2, 3, 4, 5] * size
        l.reverse()
        self.assertEqual(len(l), size * 5)
        self.assertEqual(l[-5:], [5, 4, 3, 2, 1])
        self.assertEqual(l[:5], [5, 4, 3, 2, 1])

    @bigmemtest(size=_2G // 5 + 2, memuse=8 * 5)
    def test_sort(self, size):
        l = [1, 2, 3, 4, 5] * size
        l.sort()
        self.assertEqual(len(l), size * 5)
        self.assertEqual(l.count(1), size)
        self.assertEqual(l[:10], [1] * 10)
        self.assertEqual(l[-10:], [5] * 10)

def test_main():
    support.run_unittest(StrTest, BytesTest, BytearrayTest,
        TupleTest, ListTest)

jeżeli __name__ == '__main__':
    jeżeli len(sys.argv) > 1:
        support.set_memlimit(sys.argv[1])
    test_main()
