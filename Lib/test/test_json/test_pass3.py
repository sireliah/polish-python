z test.test_json zaimportuj PyTest, CTest


# z http://json.org/JSON_checker/test/pass3.json
JSON = r'''
{
    "JSON Test Pattern dalej3": {
        "The outermost value": "must be an object albo array.",
        "In this test": "It jest an object."
    }
}
'''


klasa TestPass3:
    def test_parse(self):
        # test in/out equivalence oraz parsing
        res = self.loads(JSON)
        out = self.dumps(res)
        self.assertEqual(res, self.loads(out))


klasa TestPyPass3(TestPass3, PyTest): dalej
klasa TestCPass3(TestPass3, CTest): dalej
