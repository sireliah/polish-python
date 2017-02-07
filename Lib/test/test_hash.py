# test the invariant that
#   iff a==b then hash(a)==hash(b)
#
# Also test that hash implementations are inherited jako expected

zaimportuj datetime
zaimportuj os
zaimportuj sys
zaimportuj unittest
z test.support.script_helper zaimportuj assert_python_ok
z collections zaimportuj Hashable

IS_64BIT = sys.maxsize > 2**32

def lcg(x, length=16):
    """Linear congruential generator"""
    jeżeli x == 0:
        zwróć bytes(length)
    out = bytearray(length)
    dla i w range(length):
        x = (214013 * x + 2531011) & 0x7fffffff
        out[i] = (x >> 16) & 0xff
    zwróć bytes(out)

def pysiphash(uint64):
    """Convert SipHash24 output to Py_hash_t
    """
    assert 0 <= uint64 < (1 << 64)
    # simple unsigned to signed int64
    jeżeli uint64 > (1 << 63) - 1:
        int64 = uint64 - (1 << 64)
    inaczej:
        int64 = uint64
    # mangle uint64 to uint32
    uint32 = (uint64 ^ uint64 >> 32) & 0xffffffff
    # simple unsigned to signed int32
    jeżeli uint32 > (1 << 31) - 1:
        int32 = uint32 - (1 << 32)
    inaczej:
        int32 = uint32
    zwróć int32, int64

def skip_unless_internalhash(test):
    """Skip decorator dla tests that depend on SipHash24 albo FNV"""
    ok = sys.hash_info.algorithm w {"fnv", "siphash24"}
    msg = "Requires SipHash24 albo FNV"
    zwróć test jeżeli ok inaczej unittest.skip(msg)(test)


klasa HashEqualityTestCase(unittest.TestCase):

    def same_hash(self, *objlist):
        # Hash each object given oraz fail if
        # the hash values are nie all the same.
        hashed = list(map(hash, objlist))
        dla h w hashed[1:]:
            jeżeli h != hashed[0]:
                self.fail("hashed values differ: %r" % (objlist,))

    def test_numeric_literals(self):
        self.same_hash(1, 1, 1.0, 1.0+0.0j)
        self.same_hash(0, 0.0, 0.0+0.0j)
        self.same_hash(-1, -1.0, -1.0+0.0j)
        self.same_hash(-2, -2.0, -2.0+0.0j)

    def test_coerced_integers(self):
        self.same_hash(int(1), int(1), float(1), complex(1),
                       int('1'), float('1.0'))
        self.same_hash(int(-2**31), float(-2**31))
        self.same_hash(int(1-2**31), float(1-2**31))
        self.same_hash(int(2**31-1), float(2**31-1))
        # dla 64-bit platforms
        self.same_hash(int(2**31), float(2**31))
        self.same_hash(int(-2**63), float(-2**63))
        self.same_hash(int(2**63), float(2**63))

    def test_coerced_floats(self):
        self.same_hash(int(1.23e300), float(1.23e300))
        self.same_hash(float(0.5), complex(0.5, 0.0))

    def test_unaligned_buffers(self):
        # The hash function dla bytes-like objects shouldn't have
        # alignment-dependent results (example w issue #16427).
        b = b"123456789abcdefghijklmnopqrstuvwxyz" * 128
        dla i w range(16):
            dla j w range(16):
                aligned = b[i:128+j]
                unaligned = memoryview(b)[i:128+j]
                self.assertEqual(hash(aligned), hash(unaligned))


_default_hash = object.__hash__
klasa DefaultHash(object): dalej

_FIXED_HASH_VALUE = 42
klasa FixedHash(object):
    def __hash__(self):
        zwróć _FIXED_HASH_VALUE

klasa OnlyEquality(object):
    def __eq__(self, other):
        zwróć self jest other

klasa OnlyInequality(object):
    def __ne__(self, other):
        zwróć self jest nie other

klasa InheritedHashWithEquality(FixedHash, OnlyEquality): dalej
klasa InheritedHashWithInequality(FixedHash, OnlyInequality): dalej

klasa NoHash(object):
    __hash__ = Nic

klasa HashInheritanceTestCase(unittest.TestCase):
    default_expected = [object(),
                        DefaultHash(),
                        OnlyInequality(),
                       ]
    fixed_expected = [FixedHash(),
                      InheritedHashWithEquality(),
                      InheritedHashWithInequality(),
                      ]
    error_expected = [NoHash(),
                      OnlyEquality(),
                      ]

    def test_default_hash(self):
        dla obj w self.default_expected:
            self.assertEqual(hash(obj), _default_hash(obj))

    def test_fixed_hash(self):
        dla obj w self.fixed_expected:
            self.assertEqual(hash(obj), _FIXED_HASH_VALUE)

    def test_error_hash(self):
        dla obj w self.error_expected:
            self.assertRaises(TypeError, hash, obj)

    def test_hashable(self):
        objects = (self.default_expected +
                   self.fixed_expected)
        dla obj w objects:
            self.assertIsInstance(obj, Hashable)

    def test_not_hashable(self):
        dla obj w self.error_expected:
            self.assertNotIsInstance(obj, Hashable)


# Issue #4701: Check that some builtin types are correctly hashable
klasa DefaultIterSeq(object):
    seq = range(10)
    def __len__(self):
        zwróć len(self.seq)
    def __getitem__(self, index):
        zwróć self.seq[index]

klasa HashBuiltinsTestCase(unittest.TestCase):
    hashes_to_check = [enumerate(range(10)),
                       iter(DefaultIterSeq()),
                       iter(lambda: 0, 0),
                      ]

    def test_hashes(self):
        _default_hash = object.__hash__
        dla obj w self.hashes_to_check:
            self.assertEqual(hash(obj), _default_hash(obj))

klasa HashRandomizationTests:

    # Each subclass should define a field "repr_", containing the repr() of
    # an object to be tested

    def get_hash_command(self, repr_):
        zwróć 'print(hash(eval(%a)))' % repr_

    def get_hash(self, repr_, seed=Nic):
        env = os.environ.copy()
        env['__cleanenv'] = Prawda  # signal to assert_python nie to do a copy
                                  # of os.environ on its own
        jeżeli seed jest nie Nic:
            env['PYTHONHASHSEED'] = str(seed)
        inaczej:
            env.pop('PYTHONHASHSEED', Nic)
        out = assert_python_ok(
            '-c', self.get_hash_command(repr_),
            **env)
        stdout = out[1].strip()
        zwróć int(stdout)

    def test_randomized_hash(self):
        # two runs should zwróć different hashes
        run1 = self.get_hash(self.repr_, seed='random')
        run2 = self.get_hash(self.repr_, seed='random')
        self.assertNotEqual(run1, run2)

klasa StringlikeHashRandomizationTests(HashRandomizationTests):
    repr_ = Nic
    repr_long = Nic

    # 32bit little, 64bit little, 32bit big, 64bit big
    known_hashes = {
        'djba33x': [ # only used dla small strings
            # seed 0, 'abc'
            [193485960, 193485960,  193485960, 193485960],
            # seed 42, 'abc'
            [-678966196, 573763426263223372, -820489388, -4282905804826039665],
            ],
        'siphash24': [
            # NOTE: PyUCS2 layout depends on endianess
            # seed 0, 'abc'
            [1198583518, 4596069200710135518, 1198583518, 4596069200710135518],
            # seed 42, 'abc'
            [273876886, -4501618152524544106, 273876886, -4501618152524544106],
            # seed 42, 'abcdefghijk'
            [-1745215313, 4436719588892876975, -1745215313, 4436719588892876975],
            # seed 0, 'äú∑ℇ'
            [493570806, 5749986484189612790, -1006381564, -5915111450199468540],
            # seed 42, 'äú∑ℇ'
            [-1677110816, -2947981342227738144, -1860207793, -4296699217652516017],
        ],
        'fnv': [
            # seed 0, 'abc'
            [-1600925533, 1453079729188098211, -1600925533,
             1453079729188098211],
            # seed 42, 'abc'
            [-206076799, -4410911502303878509, -1024014457,
             -3570150969479994130],
            # seed 42, 'abcdefghijk'
            [811136751, -5046230049376118746, -77208053 ,
             -4779029615281019666],
            # seed 0, 'äú∑ℇ'
            [44402817, 8998297579845987431, -1956240331,
             -782697888614047887],
            # seed 42, 'äú∑ℇ'
            [-283066365, -4576729883824601543, -271871407,
             -3927695501187247084],
        ]
    }

    def get_expected_hash(self, position, length):
        jeżeli length < sys.hash_info.cutoff:
            algorithm = "djba33x"
        inaczej:
            algorithm = sys.hash_info.algorithm
        jeżeli sys.byteorder == 'little':
            platform = 1 jeżeli IS_64BIT inaczej 0
        inaczej:
            assert(sys.byteorder == 'big')
            platform = 3 jeżeli IS_64BIT inaczej 2
        zwróć self.known_hashes[algorithm][position][platform]

    def test_null_hash(self):
        # PYTHONHASHSEED=0 disables the randomized hash
        known_hash_of_obj = self.get_expected_hash(0, 3)

        # Randomization jest enabled by default:
        self.assertNotEqual(self.get_hash(self.repr_), known_hash_of_obj)

        # It can also be disabled by setting the seed to 0:
        self.assertEqual(self.get_hash(self.repr_, seed=0), known_hash_of_obj)

    @skip_unless_internalhash
    def test_fixed_hash(self):
        # test a fixed seed dla the randomized hash
        # Note that all types share the same values:
        h = self.get_expected_hash(1, 3)
        self.assertEqual(self.get_hash(self.repr_, seed=42), h)

    @skip_unless_internalhash
    def test_long_fixed_hash(self):
        jeżeli self.repr_long jest Nic:
            zwróć
        h = self.get_expected_hash(2, 11)
        self.assertEqual(self.get_hash(self.repr_long, seed=42), h)


klasa StrHashRandomizationTests(StringlikeHashRandomizationTests,
                                unittest.TestCase):
    repr_ = repr('abc')
    repr_long = repr('abcdefghijk')
    repr_ucs2 = repr('äú∑ℇ')

    @skip_unless_internalhash
    def test_empty_string(self):
        self.assertEqual(hash(""), 0)

    @skip_unless_internalhash
    def test_ucs2_string(self):
        h = self.get_expected_hash(3, 6)
        self.assertEqual(self.get_hash(self.repr_ucs2, seed=0), h)
        h = self.get_expected_hash(4, 6)
        self.assertEqual(self.get_hash(self.repr_ucs2, seed=42), h)

klasa BytesHashRandomizationTests(StringlikeHashRandomizationTests,
                                  unittest.TestCase):
    repr_ = repr(b'abc')
    repr_long = repr(b'abcdefghijk')

    @skip_unless_internalhash
    def test_empty_string(self):
        self.assertEqual(hash(b""), 0)

klasa MemoryviewHashRandomizationTests(StringlikeHashRandomizationTests,
                                       unittest.TestCase):
    repr_ = "memoryview(b'abc')"
    repr_long = "memoryview(b'abcdefghijk')"

    @skip_unless_internalhash
    def test_empty_string(self):
        self.assertEqual(hash(memoryview(b"")), 0)

klasa DatetimeTests(HashRandomizationTests):
    def get_hash_command(self, repr_):
        zwróć 'zaimportuj datetime; print(hash(%s))' % repr_

klasa DatetimeDateTests(DatetimeTests, unittest.TestCase):
    repr_ = repr(datetime.date(1066, 10, 14))

klasa DatetimeDatetimeTests(DatetimeTests, unittest.TestCase):
    repr_ = repr(datetime.datetime(1, 2, 3, 4, 5, 6, 7))

klasa DatetimeTimeTests(DatetimeTests, unittest.TestCase):
    repr_ = repr(datetime.time(0))


klasa HashDistributionTestCase(unittest.TestCase):

    def test_hash_distribution(self):
        # check dla hash collision
        base = "abcdefghabcdefg"
        dla i w range(1, len(base)):
            prefix = base[:i]
            przy self.subTest(prefix=prefix):
                s15 = set()
                s255 = set()
                dla c w range(256):
                    h = hash(prefix + chr(c))
                    s15.add(h & 0xf)
                    s255.add(h & 0xff)
                # SipHash24 distribution depends on key, usually > 60%
                self.assertGreater(len(s15), 8, prefix)
                self.assertGreater(len(s255), 128, prefix)

jeżeli __name__ == "__main__":
    unittest.main()
