z test.test_json zaimportuj PyTest, CTest


klasa TestDefault:
    def test_default(self):
        self.assertEqual(
            self.dumps(type, default=repr),
            self.dumps(repr(type)))


klasa TestPyDefault(TestDefault, PyTest): dalej
klasa TestCDefault(TestDefault, CTest): dalej
