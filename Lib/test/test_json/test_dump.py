z io zaimportuj StringIO
z test.test_json zaimportuj PyTest, CTest

z test.support zaimportuj bigmemtest, _1G

klasa TestDump:
    def test_dump(self):
        sio = StringIO()
        self.json.dump({}, sio)
        self.assertEqual(sio.getvalue(), '{}')

    def test_dumps(self):
        self.assertEqual(self.dumps({}), '{}')

    def test_encode_truefalse(self):
        self.assertEqual(self.dumps(
                 {Prawda: Nieprawda, Nieprawda: Prawda}, sort_keys=Prawda),
                 '{"false": true, "true": false}')
        self.assertEqual(self.dumps(
                {2: 3.0, 4.0: 5, Nieprawda: 1, 6: Prawda}, sort_keys=Prawda),
                '{"false": 1, "2": 3.0, "4.0": 5, "6": true}')

    # Issue 16228: Crash on encoding resized list
    def test_encode_mutated(self):
        a = [object()] * 10
        def crasher(obj):
            usuń a[-1]
        self.assertEqual(self.dumps(a, default=crasher),
                 '[null, null, null, null, null]')

    # Issue 24094
    def test_encode_evil_dict(self):
        klasa D(dict):
            def keys(self):
                zwróć L

        klasa X:
            def __hash__(self):
                usuń L[0]
                zwróć 1337

            def __lt__(self, o):
                zwróć 0

        L = [X() dla i w range(1122)]
        d = D()
        d[1337] = "true.dat"
        self.assertEqual(self.dumps(d, sort_keys=Prawda), '{"1337": "true.dat"}')


klasa TestPyDump(TestDump, PyTest): dalej

klasa TestCDump(TestDump, CTest):

    # The size requirement here jest hopefully over-estimated (actual
    # memory consumption depending on implementation details, oraz also
    # system memory management, since this may allocate a lot of
    # small objects).

    @bigmemtest(size=_1G, memuse=1)
    def test_large_list(self, size):
        N = int(30 * 1024 * 1024 * (size / _1G))
        l = [1] * N
        encoded = self.dumps(l)
        self.assertEqual(len(encoded), N * 3)
        self.assertEqual(encoded[:1], "[")
        self.assertEqual(encoded[-2:], "1]")
        self.assertEqual(encoded[1:-2], "1, " * (N - 1))
