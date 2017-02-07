"""Verify that warnings are issued dla global statements following use."""

z test.support zaimportuj run_unittest, check_syntax_error, check_warnings
zaimportuj unittest
zaimportuj warnings


klasa GlobalTests(unittest.TestCase):

    def setUp(self):
        self._warnings_manager = check_warnings()
        self._warnings_manager.__enter__()
        warnings.filterwarnings("error", module="<test string>")

    def tearDown(self):
        self._warnings_manager.__exit__(Nic, Nic, Nic)


    def test1(self):
        prog_text_1 = """\
def wrong1():
    a = 1
    b = 2
    global a
    global b
"""
        check_syntax_error(self, prog_text_1)

    def test2(self):
        prog_text_2 = """\
def wrong2():
    print(x)
    global x
"""
        check_syntax_error(self, prog_text_2)

    def test3(self):
        prog_text_3 = """\
def wrong3():
    print(x)
    x = 2
    global x
"""
        check_syntax_error(self, prog_text_3)

    def test4(self):
        prog_text_4 = """\
global x
x = 2
"""
        # this should work
        compile(prog_text_4, "<test string>", "exec")


def test_main():
    przy warnings.catch_warnings():
        warnings.filterwarnings("error", module="<test string>")
        run_unittest(GlobalTests)

jeżeli __name__ == "__main__":
    test_main()
