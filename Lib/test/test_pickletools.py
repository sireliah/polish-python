zaimportuj struct
zaimportuj pickle
zaimportuj pickletools
z test zaimportuj support
z test.pickletester zaimportuj AbstractPickleTests
z test.pickletester zaimportuj AbstractPickleModuleTests

klasa OptimizedPickleTests(AbstractPickleTests, AbstractPickleModuleTests):

    def dumps(self, arg, proto=Nic):
        zwróć pickletools.optimize(pickle.dumps(arg, proto))

    def loads(self, buf, **kwds):
        zwróć pickle.loads(buf, **kwds)

    # Test relies on precise output of dumps()
    test_pickle_to_2x = Nic

    def test_optimize_long_binget(self):
        data = [str(i) dla i w range(257)]
        data.append(data[-1])
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            pickled = pickle.dumps(data, proto)
            unpickled = pickle.loads(pickled)
            self.assertEqual(unpickled, data)
            self.assertIs(unpickled[-1], unpickled[-2])

            pickled2 = pickletools.optimize(pickled)
            unpickled2 = pickle.loads(pickled2)
            self.assertEqual(unpickled2, data)
            self.assertIs(unpickled2[-1], unpickled2[-2])
            self.assertNotIn(pickle.LONG_BINGET, pickled2)
            self.assertNotIn(pickle.LONG_BINPUT, pickled2)

    def test_optimize_binput_and_memoize(self):
        pickled = (b'\x80\x04\x95\x15\x00\x00\x00\x00\x00\x00\x00'
                   b']\x94(\x8c\x04spamq\x01\x8c\x03ham\x94h\x02e.')
        #    0: \x80 PROTO      4
        #    2: \x95 FRAME      21
        #   11: ]    EMPTY_LIST
        #   12: \x94 MEMOIZE
        #   13: (    MARK
        #   14: \x8c     SHORT_BINUNICODE 'spam'
        #   20: q        BINPUT     1
        #   22: \x8c     SHORT_BINUNICODE 'ham'
        #   27: \x94     MEMOIZE
        #   28: h        BINGET     2
        #   30: e        APPENDS    (MARK at 13)
        #   31: .    STOP
        self.assertIn(pickle.BINPUT, pickled)
        unpickled = pickle.loads(pickled)
        self.assertEqual(unpickled, ['spam', 'ham', 'ham'])
        self.assertIs(unpickled[1], unpickled[2])

        pickled2 = pickletools.optimize(pickled)
        unpickled2 = pickle.loads(pickled2)
        self.assertEqual(unpickled2, ['spam', 'ham', 'ham'])
        self.assertIs(unpickled2[1], unpickled2[2])
        self.assertNotIn(pickle.BINPUT, pickled2)


def test_main():
    support.run_unittest(OptimizedPickleTests)
    support.run_doctest(pickletools)


jeżeli __name__ == "__main__":
    test_main()
