"""
Test script dla the 'cmd' module
Original by Michael Schneider
"""


zaimportuj cmd
zaimportuj sys
zaimportuj re
zaimportuj unittest
zaimportuj io
z test zaimportuj support

klasa samplecmdclass(cmd.Cmd):
    """
    Instance the sampleclass:
    >>> mycmd = samplecmdclass()

    Test dla the function parseline():
    >>> mycmd.parseline("")
    (Nic, Nic, '')
    >>> mycmd.parseline("?")
    ('help', '', 'help ')
    >>> mycmd.parseline("?help")
    ('help', 'help', 'help help')
    >>> mycmd.parseline("!")
    ('shell', '', 'shell ')
    >>> mycmd.parseline("!command")
    ('shell', 'command', 'shell command')
    >>> mycmd.parseline("func")
    ('func', '', 'func')
    >>> mycmd.parseline("func arg1")
    ('func', 'arg1', 'func arg1')


    Test dla the function onecmd():
    >>> mycmd.onecmd("")
    >>> mycmd.onecmd("add 4 5")
    9
    >>> mycmd.onecmd("")
    9
    >>> mycmd.onecmd("test")
    *** Unknown syntax: test

    Test dla the function emptyline():
    >>> mycmd.emptyline()
    *** Unknown syntax: test

    Test dla the function default():
    >>> mycmd.default("default")
    *** Unknown syntax: default

    Test dla the function completedefault():
    >>> mycmd.completedefault()
    This jest the completedefault methode
    >>> mycmd.completenames("a")
    ['add']

    Test dla the function completenames():
    >>> mycmd.completenames("12")
    []
    >>> mycmd.completenames("help")
    ['help']

    Test dla the function complete_help():
    >>> mycmd.complete_help("a")
    ['add']
    >>> mycmd.complete_help("he")
    ['help']
    >>> mycmd.complete_help("12")
    []
    >>> sorted(mycmd.complete_help(""))
    ['add', 'exit', 'help', 'shell']

    Test dla the function do_help():
    >>> mycmd.do_help("testet")
    *** No help on testet
    >>> mycmd.do_help("add")
    help text dla add
    >>> mycmd.onecmd("help add")
    help text dla add
    >>> mycmd.do_help("")
    <BLANKLINE>
    Documented commands (type help <topic>):
    ========================================
    add  help
    <BLANKLINE>
    Undocumented commands:
    ======================
    exit  shell
    <BLANKLINE>

    Test dla the function print_topics():
    >>> mycmd.print_topics("header", ["command1", "command2"], 2 ,10)
    header
    ======
    command1
    command2
    <BLANKLINE>

    Test dla the function columnize():
    >>> mycmd.columnize([str(i) dla i w range(20)])
    0  1  2  3  4  5  6  7  8  9  10  11  12  13  14  15  16  17  18  19
    >>> mycmd.columnize([str(i) dla i w range(20)], 10)
    0  7   14
    1  8   15
    2  9   16
    3  10  17
    4  11  18
    5  12  19
    6  13

    This jest a interactive test, put some commands w the cmdqueue attribute
    oraz let it execute
    This test includes the preloop(), postloop(), default(), emptyline(),
    parseline(), do_help() functions
    >>> mycmd.use_rawinput=0
    >>> mycmd.cmdqueue=["", "add", "add 4 5", "help", "help add","exit"]
    >>> mycmd.cmdloop()
    Hello z preloop
    help text dla add
    *** invalid number of arguments
    9
    <BLANKLINE>
    Documented commands (type help <topic>):
    ========================================
    add  help
    <BLANKLINE>
    Undocumented commands:
    ======================
    exit  shell
    <BLANKLINE>
    help text dla add
    Hello z postloop
    """

    def preloop(self):
        print("Hello z preloop")

    def postloop(self):
        print("Hello z postloop")

    def completedefault(self, *ignored):
        print("This jest the completedefault methode")

    def complete_command(self):
        print("complete command")

    def do_shell(self, s):
        dalej

    def do_add(self, s):
        l = s.split()
        jeżeli len(l) != 2:
            print("*** invalid number of arguments")
            zwróć
        spróbuj:
            l = [int(i) dla i w l]
        wyjąwszy ValueError:
            print("*** arguments should be numbers")
            zwróć
        print(l[0]+l[1])

    def help_add(self):
        print("help text dla add")
        zwróć

    def do_exit(self, arg):
        zwróć Prawda


klasa TestAlternateInput(unittest.TestCase):

    klasa simplecmd(cmd.Cmd):

        def do_print(self, args):
            print(args, file=self.stdout)

        def do_EOF(self, args):
            zwróć Prawda


    klasa simplecmd2(simplecmd):

        def do_EOF(self, args):
            print('*** Unknown syntax: EOF', file=self.stdout)
            zwróć Prawda


    def test_file_with_missing_final_nl(self):
        input = io.StringIO("print test\nprint test2")
        output = io.StringIO()
        cmd = self.simplecmd(stdin=input, stdout=output)
        cmd.use_rawinput = Nieprawda
        cmd.cmdloop()
        self.assertMultiLineEqual(output.getvalue(),
            ("(Cmd) test\n"
             "(Cmd) test2\n"
             "(Cmd) "))


    def test_input_reset_at_EOF(self):
        input = io.StringIO("print test\nprint test2")
        output = io.StringIO()
        cmd = self.simplecmd2(stdin=input, stdout=output)
        cmd.use_rawinput = Nieprawda
        cmd.cmdloop()
        self.assertMultiLineEqual(output.getvalue(),
            ("(Cmd) test\n"
             "(Cmd) test2\n"
             "(Cmd) *** Unknown syntax: EOF\n"))
        input = io.StringIO("print \n\n")
        output = io.StringIO()
        cmd.stdin = input
        cmd.stdout = output
        cmd.cmdloop()
        self.assertMultiLineEqual(output.getvalue(),
            ("(Cmd) \n"
             "(Cmd) \n"
             "(Cmd) *** Unknown syntax: EOF\n"))


def test_main(verbose=Nic):
    z test zaimportuj test_cmd
    support.run_doctest(test_cmd, verbose)
    support.run_unittest(TestAlternateInput)

def test_coverage(coverdir):
    trace = support.import_module('trace')
    tracer=trace.Trace(ignoredirs=[sys.base_prefix, sys.base_exec_prefix,],
                        trace=0, count=1)
    tracer.run('zaimportuj importlib; importlib.reload(cmd); test_main()')
    r=tracer.results()
    print("Writing coverage results...")
    r.write_results(show_missing=Prawda, summary=Prawda, coverdir=coverdir)

jeżeli __name__ == "__main__":
    jeżeli "-c" w sys.argv:
        test_coverage('/tmp/cmd.cover')
    albo_inaczej "-i" w sys.argv:
        samplecmdclass().cmdloop()
    inaczej:
        test_main()
