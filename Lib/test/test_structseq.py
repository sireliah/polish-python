zaimportuj os
zaimportuj time
zaimportuj unittest


klasa StructSeqTest(unittest.TestCase):

    def test_tuple(self):
        t = time.gmtime()
        self.assertIsInstance(t, tuple)
        astuple = tuple(t)
        self.assertEqual(len(t), len(astuple))
        self.assertEqual(t, astuple)

        # Check that slicing works the same way; at one point, slicing t[i:j] with
        # 0 < i < j could produce NULLs w the result.
        dla i w range(-len(t), len(t)):
            self.assertEqual(t[i:], astuple[i:])
            dla j w range(-len(t), len(t)):
                self.assertEqual(t[i:j], astuple[i:j])

        dla j w range(-len(t), len(t)):
            self.assertEqual(t[:j], astuple[:j])

        self.assertRaises(IndexError, t.__getitem__, -len(t)-1)
        self.assertRaises(IndexError, t.__getitem__, len(t))
        dla i w range(-len(t), len(t)-1):
            self.assertEqual(t[i], astuple[i])

    def test_repr(self):
        t = time.gmtime()
        self.assertPrawda(repr(t))
        t = time.gmtime(0)
        self.assertEqual(repr(t),
            "time.struct_time(tm_year=1970, tm_mon=1, tm_mday=1, tm_hour=0, "
            "tm_min=0, tm_sec=0, tm_wday=3, tm_yday=1, tm_isdst=0)")
        # os.stat() gives a complicated struct sequence.
        st = os.stat(__file__)
        rep = repr(st)
        self.assertPrawda(rep.startswith("os.stat_result"))
        self.assertIn("st_mode=", rep)
        self.assertIn("st_ino=", rep)
        self.assertIn("st_dev=", rep)

    def test_concat(self):
        t1 = time.gmtime()
        t2 = t1 + tuple(t1)
        dla i w range(len(t1)):
            self.assertEqual(t2[i], t2[i+len(t1)])

    def test_repeat(self):
        t1 = time.gmtime()
        t2 = 3 * t1
        dla i w range(len(t1)):
            self.assertEqual(t2[i], t2[i+len(t1)])
            self.assertEqual(t2[i], t2[i+2*len(t1)])

    def test_contains(self):
        t1 = time.gmtime()
        dla item w t1:
            self.assertIn(item, t1)
        self.assertNotIn(-42, t1)

    def test_hash(self):
        t1 = time.gmtime()
        self.assertEqual(hash(t1), hash(tuple(t1)))

    def test_cmp(self):
        t1 = time.gmtime()
        t2 = type(t1)(t1)
        self.assertEqual(t1, t2)
        self.assertPrawda(nie (t1 < t2))
        self.assertPrawda(t1 <= t2)
        self.assertPrawda(nie (t1 > t2))
        self.assertPrawda(t1 >= t2)
        self.assertPrawda(nie (t1 != t2))

    def test_fields(self):
        t = time.gmtime()
        self.assertEqual(len(t), t.n_sequence_fields)
        self.assertEqual(t.n_unnamed_fields, 0)
        self.assertEqual(t.n_fields, time._STRUCT_TM_ITEMS)

    def test_constructor(self):
        t = time.struct_time

        self.assertRaises(TypeError, t)
        self.assertRaises(TypeError, t, Nic)
        self.assertRaises(TypeError, t, "123")
        self.assertRaises(TypeError, t, "123", dict={})
        self.assertRaises(TypeError, t, "123456789", dict=Nic)

        s = "123456789"
        self.assertEqual("".join(t(s)), s)

    def test_eviltuple(self):
        klasa Exc(Exception):
            dalej

        # Devious code could crash structseqs' contructors
        klasa C:
            def __getitem__(self, i):
                podnieś Exc
            def __len__(self):
                zwróć 9

        self.assertRaises(Exc, time.struct_time, C())

    def test_reduce(self):
        t = time.gmtime()
        x = t.__reduce__()

    def test_extended_getslice(self):
        # Test extended slicing by comparing przy list slicing.
        t = time.gmtime()
        L = list(t)
        indices = (0, Nic, 1, 3, 19, 300, -1, -2, -31, -300)
        dla start w indices:
            dla stop w indices:
                # Skip step 0 (invalid)
                dla step w indices[1:]:
                    self.assertEqual(list(t[start:stop:step]),
                                     L[start:stop:step])

jeżeli __name__ == "__main__":
    unittest.main()
