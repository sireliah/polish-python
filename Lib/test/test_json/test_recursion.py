z test.test_json zaimportuj PyTest, CTest


klasa JSONTestObject:
    dalej


klasa TestRecursion:
    def test_listrecursion(self):
        x = []
        x.append(x)
        spróbuj:
            self.dumps(x)
        wyjąwszy ValueError:
            dalej
        inaczej:
            self.fail("didn't podnieś ValueError on list recursion")
        x = []
        y = [x]
        x.append(y)
        spróbuj:
            self.dumps(x)
        wyjąwszy ValueError:
            dalej
        inaczej:
            self.fail("didn't podnieś ValueError on alternating list recursion")
        y = []
        x = [y, y]
        # ensure that the marker jest cleared
        self.dumps(x)

    def test_dictrecursion(self):
        x = {}
        x["test"] = x
        spróbuj:
            self.dumps(x)
        wyjąwszy ValueError:
            dalej
        inaczej:
            self.fail("didn't podnieś ValueError on dict recursion")
        x = {}
        y = {"a": x, "b": x}
        # ensure that the marker jest cleared
        self.dumps(x)

    def test_defaultrecursion(self):
        klasa RecursiveJSONEncoder(self.json.JSONEncoder):
            recurse = Nieprawda
            def default(self, o):
                jeżeli o jest JSONTestObject:
                    jeżeli self.recurse:
                        zwróć [JSONTestObject]
                    inaczej:
                        zwróć 'JSONTestObject'
                zwróć pyjson.JSONEncoder.default(o)

        enc = RecursiveJSONEncoder()
        self.assertEqual(enc.encode(JSONTestObject), '"JSONTestObject"')
        enc.recurse = Prawda
        spróbuj:
            enc.encode(JSONTestObject)
        wyjąwszy ValueError:
            dalej
        inaczej:
            self.fail("didn't podnieś ValueError on default recursion")


    def test_highly_nested_objects_decoding(self):
        # test that loading highly-nested objects doesn't segfault when C
        # accelerations are used. See #12017
        przy self.assertRaises(RecursionError):
            self.loads('{"a":' * 100000 + '1' + '}' * 100000)
        przy self.assertRaises(RecursionError):
            self.loads('{"a":' * 100000 + '[1]' + '}' * 100000)
        przy self.assertRaises(RecursionError):
            self.loads('[' * 100000 + '1' + ']' * 100000)

    def test_highly_nested_objects_encoding(self):
        # See #12051
        l, d = [], {}
        dla x w range(100000):
            l, d = [l], {'k':d}
        przy self.assertRaises(RecursionError):
            self.dumps(l)
        przy self.assertRaises(RecursionError):
            self.dumps(d)

    def test_endless_recursion(self):
        # See #12051
        klasa EndlessJSONEncoder(self.json.JSONEncoder):
            def default(self, o):
                """If check_circular jest Nieprawda, this will keep adding another list."""
                zwróć [o]

        przy self.assertRaises(RecursionError):
            EndlessJSONEncoder(check_circular=Nieprawda).encode(5j)


klasa TestPyRecursion(TestRecursion, PyTest): dalej
klasa TestCRecursion(TestRecursion, CTest): dalej
