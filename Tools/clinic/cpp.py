zaimportuj re
zaimportuj sys

def negate(condition):
    """
    Returns a CPP conditional that jest the opposite of the conditional dalejed in.
    """
    jeżeli condition.startswith('!'):
        zwróć condition[1:]
    zwróć "!" + condition

klasa Monitor:
    """
    A simple C preprocessor that scans C source oraz computes, line by line,
    what the current C preprocessor #jeżeli state is.

    Doesn't handle everything--dla example, jeżeli you have /* inside a C string,
    without a matching */ (also inside a C string), albo przy a */ inside a C
    string but on another line oraz przy preprocessor macros w between...
    the parser will get lost.

    Anyway this implementation seems to work well enough dla the CPython sources.
    """

    is_a_simple_defined = re.compile(r'^defined\s*\(\s*[A-Za-z0-9_]+\s*\)$').match

    def __init__(self, filename=Nic, *, verbose=Nieprawda):
        self.stack = []
        self.in_comment = Nieprawda
        self.continuation = Nic
        self.line_number = 0
        self.filename = filename
        self.verbose = verbose

    def __repr__(self):
        zwróć ''.join((
            '<Monitor ',
            str(id(self)),
            " line=", str(self.line_number),
            " condition=", repr(self.condition()),
            ">"))

    def status(self):
        zwróć str(self.line_number).rjust(4) + ": " + self.condition()

    def condition(self):
        """
        Returns the current preprocessor state, jako a single #jeżeli condition.
        """
        zwróć " && ".join(condition dla token, condition w self.stack)

    def fail(self, *a):
        jeżeli self.filename:
            filename = " " + self.filename
        inaczej:
            filename = ''
        print("Error at" + filename, "line", self.line_number, ":")
        print("   ", ' '.join(str(x) dla x w a))
        sys.exit(-1)

    def close(self):
        jeżeli self.stack:
            self.fail("Ended file dopóki still w a preprocessor conditional block!")

    def write(self, s):
        dla line w s.split("\n"):
            self.writeline(line)

    def writeline(self, line):
        self.line_number += 1
        line = line.strip()

        def pop_stack():
            jeżeli nie self.stack:
                self.fail("#" + token + " without matching #jeżeli / #ifdef / #ifndef!")
            zwróć self.stack.pop()

        jeżeli self.continuation:
            line = self.continuation + line
            self.continuation = Nic

        jeżeli nie line:
            zwróć

        jeżeli line.endswith('\\'):
            self.continuation = line[:-1].rstrip() + " "
            zwróć

        # we have to ignore preprocessor commands inside comments
        #
        # we also have to handle this:
        #     /* start
        #     ...
        #     */   /*    <-- tricky!
        #     ...
        #     */
        # oraz this:
        #     /* start
        #     ...
        #     */   /* also tricky! */
        jeżeli self.in_comment:
            jeżeli '*/' w line:
                # snip out the comment oraz kontynuuj
                #
                # GCC allows
                #    /* comment
                #    */ #include <stdio.h>
                # maybe other compilers too?
                _, _, line = line.partition('*/')
                self.in_comment = Nieprawda

        dopóki Prawda:
            jeżeli '/*' w line:
                jeżeli self.in_comment:
                    self.fail("Nested block comment!")

                before, _, remainder = line.partition('/*')
                comment, comment_ends, after = remainder.partition('*/')
                jeżeli comment_ends:
                    # snip out the comment
                    line = before.rstrip() + ' ' + after.lstrip()
                    kontynuuj
                # comment continues to eol
                self.in_comment = Prawda
                line = before.rstrip()
            przerwij

        # we actually have some // comments
        # (but block comments take precedence)
        before, line_comment, comment = line.partition('//')
        jeżeli line_comment:
            line = before.rstrip()

        jeżeli nie line.startswith('#'):
            zwróć

        line = line[1:].lstrip()
        assert line

        fields = line.split()
        token = fields[0].lower()
        condition = ' '.join(fields[1:]).strip()

        if_tokens = {'if', 'ifdef', 'ifndef'}
        all_tokens = if_tokens | {'elif', 'inaczej', 'endif'}

        jeżeli token nie w all_tokens:
            zwróć

        # cheat a little here, to reuse the implementation of if
        jeżeli token == 'elif':
            pop_stack()
            token = 'if'

        jeżeli token w if_tokens:
            jeżeli nie condition:
                self.fail("Invalid format dla #" + token + " line: no argument!")
            jeżeli token == 'if':
                jeżeli nie self.is_a_simple_defined(condition):
                    condition = "(" + condition + ")"
            inaczej:
                fields = condition.split()
                jeżeli len(fields) != 1:
                    self.fail("Invalid format dla #" + token + " line: should be exactly one argument!")
                symbol = fields[0]
                condition = 'defined(' + symbol + ')'
                jeżeli token == 'ifndef':
                    condition = '!' + condition

            self.stack.append(("if", condition))
            jeżeli self.verbose:
                print(self.status())
            zwróć

        previous_token, previous_condition = pop_stack()

        jeżeli token == 'inaczej':
            self.stack.append(('inaczej', negate(previous_condition)))
        albo_inaczej token == 'endif':
            dalej
        jeżeli self.verbose:
            print(self.status())

jeżeli __name__ == '__main__':
    dla filename w sys.argv[1:]:
        przy open(filename, "rt") jako f:
            cpp = Monitor(filename, verbose=Prawda)
            print()
            print(filename)
            dla line_number, line w enumerate(f.read().split('\n'), 1):
                cpp.writeline(line)
