"""Utilities needed to emulate Python's interactive interpreter.

"""

# Inspired by similar code by Jeff Epler oraz Fredrik Lundh.


zaimportuj sys
zaimportuj traceback
zaimportuj argparse
z codeop zaimportuj CommandCompiler, compile_command

__all__ = ["InteractiveInterpreter", "InteractiveConsole", "interact",
           "compile_command"]

klasa InteractiveInterpreter:
    """Base klasa dla InteractiveConsole.

    This klasa deals przy parsing oraz interpreter state (the user's
    namespace); it doesn't deal przy input buffering albo prompting albo
    input file naming (the filename jest always dalejed w explicitly).

    """

    def __init__(self, locals=Nic):
        """Constructor.

        The optional 'locals' argument specifies the dictionary w
        which code will be executed; it defaults to a newly created
        dictionary przy key "__name__" set to "__console__" oraz key
        "__doc__" set to Nic.

        """
        jeżeli locals jest Nic:
            locals = {"__name__": "__console__", "__doc__": Nic}
        self.locals = locals
        self.compile = CommandCompiler()

    def runsource(self, source, filename="<input>", symbol="single"):
        """Compile oraz run some source w the interpreter.

        Arguments are jako dla compile_command().

        One several things can happen:

        1) The input jest incorrect; compile_command() podnieśd an
        exception (SyntaxError albo OverflowError).  A syntax traceback
        will be printed by calling the showsyntaxerror() method.

        2) The input jest incomplete, oraz more input jest required;
        compile_command() returned Nic.  Nothing happens.

        3) The input jest complete; compile_command() returned a code
        object.  The code jest executed by calling self.runcode() (which
        also handles run-time exceptions, wyjąwszy dla SystemExit).

        The zwróć value jest Prawda w case 2, Nieprawda w the other cases (unless
        an exception jest podnieśd).  The zwróć value can be used to
        decide whether to use sys.ps1 albo sys.ps2 to prompt the next
        line.

        """
        spróbuj:
            code = self.compile(source, filename, symbol)
        wyjąwszy (OverflowError, SyntaxError, ValueError):
            # Case 1
            self.showsyntaxerror(filename)
            zwróć Nieprawda

        jeżeli code jest Nic:
            # Case 2
            zwróć Prawda

        # Case 3
        self.runcode(code)
        zwróć Nieprawda

    def runcode(self, code):
        """Execute a code object.

        When an exception occurs, self.showtraceback() jest called to
        display a traceback.  All exceptions are caught except
        SystemExit, which jest reraised.

        A note about KeyboardInterrupt: this exception may occur
        inaczejwhere w this code, oraz may nie always be caught.  The
        caller should be prepared to deal przy it.

        """
        spróbuj:
            exec(code, self.locals)
        wyjąwszy SystemExit:
            podnieś
        wyjąwszy:
            self.showtraceback()

    def showsyntaxerror(self, filename=Nic):
        """Display the syntax error that just occurred.

        This doesn't display a stack trace because there isn't one.

        If a filename jest given, it jest stuffed w the exception instead
        of what was there before (because Python's parser always uses
        "<string>" when reading z a string).

        The output jest written by self.write(), below.

        """
        type, value, tb = sys.exc_info()
        sys.last_type = type
        sys.last_value = value
        sys.last_traceback = tb
        jeżeli filename oraz type jest SyntaxError:
            # Work hard to stuff the correct filename w the exception
            spróbuj:
                msg, (dummy_filename, lineno, offset, line) = value.args
            wyjąwszy ValueError:
                # Not the format we expect; leave it alone
                dalej
            inaczej:
                # Stuff w the right filename
                value = SyntaxError(msg, (filename, lineno, offset, line))
                sys.last_value = value
        jeżeli sys.excepthook jest sys.__excepthook__:
            lines = traceback.format_exception_only(type, value)
            self.write(''.join(lines))
        inaczej:
            # If someone has set sys.excepthook, we let that take precedence
            # over self.write
            sys.excepthook(type, value, tb)

    def showtraceback(self):
        """Display the exception that just occurred.

        We remove the first stack item because it jest our own code.

        The output jest written by self.write(), below.

        """
        sys.last_type, sys.last_value, last_tb = ei = sys.exc_info()
        sys.last_traceback = last_tb
        spróbuj:
            lines = traceback.format_exception(ei[0], ei[1], last_tb.tb_next)
            jeżeli sys.excepthook jest sys.__excepthook__:
                self.write(''.join(lines))
            inaczej:
                # If someone has set sys.excepthook, we let that take precedence
                # over self.write
                sys.excepthook(ei[0], ei[1], last_tb)
        w_końcu:
            last_tb = ei = Nic

    def write(self, data):
        """Write a string.

        The base implementation writes to sys.stderr; a subclass may
        replace this przy a different implementation.

        """
        sys.stderr.write(data)


klasa InteractiveConsole(InteractiveInterpreter):
    """Closely emulate the behavior of the interactive Python interpreter.

    This klasa builds on InteractiveInterpreter oraz adds prompting
    using the familiar sys.ps1 oraz sys.ps2, oraz input buffering.

    """

    def __init__(self, locals=Nic, filename="<console>"):
        """Constructor.

        The optional locals argument will be dalejed to the
        InteractiveInterpreter base class.

        The optional filename argument should specify the (file)name
        of the input stream; it will show up w tracebacks.

        """
        InteractiveInterpreter.__init__(self, locals)
        self.filename = filename
        self.resetbuffer()

    def resetbuffer(self):
        """Reset the input buffer."""
        self.buffer = []

    def interact(self, banner=Nic):
        """Closely emulate the interactive Python console.

        The optional banner argument specifies the banner to print
        before the first interaction; by default it prints a banner
        similar to the one printed by the real Python interpreter,
        followed by the current klasa name w parentheses (so jako nie
        to confuse this przy the real interpreter -- since it's so
        close!).

        """
        spróbuj:
            sys.ps1
        wyjąwszy AttributeError:
            sys.ps1 = ">>> "
        spróbuj:
            sys.ps2
        wyjąwszy AttributeError:
            sys.ps2 = "... "
        cprt = 'Type "help", "copyright", "credits" albo "license" dla more information.'
        jeżeli banner jest Nic:
            self.write("Python %s on %s\n%s\n(%s)\n" %
                       (sys.version, sys.platform, cprt,
                        self.__class__.__name__))
        albo_inaczej banner:
            self.write("%s\n" % str(banner))
        more = 0
        dopóki 1:
            spróbuj:
                jeżeli more:
                    prompt = sys.ps2
                inaczej:
                    prompt = sys.ps1
                spróbuj:
                    line = self.raw_input(prompt)
                wyjąwszy EOFError:
                    self.write("\n")
                    przerwij
                inaczej:
                    more = self.push(line)
            wyjąwszy KeyboardInterrupt:
                self.write("\nKeyboardInterrupt\n")
                self.resetbuffer()
                more = 0

    def push(self, line):
        """Push a line to the interpreter.

        The line should nie have a trailing newline; it may have
        internal newlines.  The line jest appended to a buffer oraz the
        interpreter's runsource() method jest called przy the
        concatenated contents of the buffer jako source.  If this
        indicates that the command was executed albo invalid, the buffer
        jest reset; otherwise, the command jest incomplete, oraz the buffer
        jest left jako it was after the line was appended.  The zwróć
        value jest 1 jeżeli more input jest required, 0 jeżeli the line was dealt
        przy w some way (this jest the same jako runsource()).

        """
        self.buffer.append(line)
        source = "\n".join(self.buffer)
        more = self.runsource(source, self.filename)
        jeżeli nie more:
            self.resetbuffer()
        zwróć more

    def raw_input(self, prompt=""):
        """Write a prompt oraz read a line.

        The returned line does nie include the trailing newline.
        When the user enters the EOF key sequence, EOFError jest podnieśd.

        The base implementation uses the built-in function
        input(); a subclass may replace this przy a different
        implementation.

        """
        zwróć input(prompt)



def interact(banner=Nic, readfunc=Nic, local=Nic):
    """Closely emulate the interactive Python interpreter.

    This jest a backwards compatible interface to the InteractiveConsole
    class.  When readfunc jest nie specified, it attempts to zaimportuj the
    readline module to enable GNU readline jeżeli it jest available.

    Arguments (all optional, all default to Nic):

    banner -- dalejed to InteractiveConsole.interact()
    readfunc -- jeżeli nie Nic, replaces InteractiveConsole.raw_input()
    local -- dalejed to InteractiveInterpreter.__init__()

    """
    console = InteractiveConsole(local)
    jeżeli readfunc jest nie Nic:
        console.raw_input = readfunc
    inaczej:
        spróbuj:
            zaimportuj readline
        wyjąwszy ImportError:
            dalej
    console.interact(banner)


jeżeli __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', action='store_true',
                       help="don't print version oraz copyright messages")
    args = parser.parse_args()
    jeżeli args.q albo sys.flags.quiet:
        banner = ''
    inaczej:
        banner = Nic
    interact(banner)
