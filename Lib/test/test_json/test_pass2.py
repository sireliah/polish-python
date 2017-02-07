z test.test_json zaimportuj PyTest, CTest


# z http://json.org/JSON_checker/test/pass2.json
JSON = r'''
[[[[[[[[[[[[[[[[[[["Not too deep"]]]]]]]]]]]]]]]]]]]
'''

klasa TestPass2:
    def test_parse(self):
        # test in/out equivalence oraz parsing
        res = self.loads(JSON)
        out = self.dumps(res)
        self.assertEqual(res, self.loads(out))


klasa TestPyPass2(TestPass2, PyTest): dalej
klasa TestCPass2(TestPass2, CTest): dalej
