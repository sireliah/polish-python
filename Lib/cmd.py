"""A generic klasa to build line-oriented command interpreters.

Interpreters constructed przy this klasa obey the following conventions:

1. End of file on input jest processed jako the command 'EOF'.
2. A command jest parsed out of each line by collecting the prefix composed
   of characters w the identchars member.
3. A command `foo' jest dispatched to a method 'do_foo()'; the do_ method
   jest dalejed a single argument consisting of the remainder of the line.
4. Typing an empty line repeats the last command.  (Actually, it calls the
   method `emptyline', which may be overridden w a subclass.)
5. There jest a predefined `help' method.  Given an argument `topic', it
   calls the command `help_topic'.  With no arguments, it lists all topics
   przy defined help_ functions, broken into up to three topics; documented
   commands, miscellaneous help topics, oraz undocumented commands.
6. The command '?' jest a synonym dla `help'.  The command '!' jest a synonym
   dla `shell', jeżeli a do_shell method exists.
7. If completion jest enabled, completing commands will be done automatically,
   oraz completing of commands args jest done by calling complete_foo() with
   arguments text, line, begidx, endidx.  text jest string we are matching
   against, all returned matches must begin przy it.  line jest the current
   input line (lstripped), begidx oraz endidx are the beginning oraz end
   indexes of the text being matched, which could be used to provide
   different completion depending upon which position the argument jest in.

The `default' method may be overridden to intercept commands dla which there
is no do_ method.

The `completedefault' method may be overridden to intercept completions for
commands that have no complete_ method.

The data member `self.ruler' sets the character used to draw separator lines
in the help messages.  If empty, no ruler line jest drawn.  It defaults to "=".

If the value of `self.intro' jest nonempty when the cmdloop method jest called,
it jest printed out on interpreter startup.  This value may be overridden
via an optional argument to the cmdloop() method.

The data members `self.doc_header', `self.misc_header', oraz
`self.undoc_header' set the headers used dla the help function's
listings of documented functions, miscellaneous topics, oraz undocumented
functions respectively.
"""

zaimportuj string, sys

__all__ = ["Cmd"]

PROMPT = '(Cmd) '
IDENTCHARS = string.ascii_letters + string.digits + '_'

klasa Cmd:
    """A simple framework dla writing line-oriented command interpreters.

    These are often useful dla test harnesses, administrative tools, oraz
    prototypes that will later be wrapped w a more sophisticated interface.

    A Cmd instance albo subclass instance jest a line-oriented interpreter
    framework.  There jest no good reason to instantiate Cmd itself; rather,
    it's useful jako a superclass of an interpreter klasa you define yourself
    w order to inherit Cmd's methods oraz encapsulate action methods.

    """
    prompt = PROMPT
    identchars = IDENTCHARS
    ruler = '='
    lastcmd = ''
    intro = Nic
    doc_leader = ""
    doc_header = "Documented commands (type help <topic>):"
    misc_header = "Miscellaneous help topics:"
    undoc_header = "Undocumented commands:"
    nohelp = "*** No help on %s"
    use_rawinput = 1

    def __init__(self, completekey='tab', stdin=Nic, stdout=Nic):
        """Instantiate a line-oriented interpreter framework.

        The optional argument 'completekey' jest the readline name of a
        completion key; it defaults to the Tab key. If completekey jest
        nie Nic oraz the readline module jest available, command completion
        jest done automatically. The optional arguments stdin oraz stdout
        specify alternate input oraz output file objects; jeżeli nie specified,
        sys.stdin oraz sys.stdout are used.

        """
        jeżeli stdin jest nie Nic:
            self.stdin = stdin
        inaczej:
            self.stdin = sys.stdin
        jeżeli stdout jest nie Nic:
            self.stdout = stdout
        inaczej:
            self.stdout = sys.stdout
        self.cmdqueue = []
        self.completekey = completekey

    def cmdloop(self, intro=Nic):
        """Repeatedly issue a prompt, accept input, parse an initial prefix
        off the received input, oraz dispatch to action methods, dalejing them
        the remainder of the line jako argument.

        """

        self.preloop()
        jeżeli self.use_rawinput oraz self.completekey:
            spróbuj:
                zaimportuj readline
                self.old_completer = readline.get_completer()
                readline.set_completer(self.complete)
                readline.parse_and_bind(self.completekey+": complete")
            wyjąwszy ImportError:
                dalej
        spróbuj:
            jeżeli intro jest nie Nic:
                self.intro = intro
            jeżeli self.intro:
                self.stdout.write(str(self.intro)+"\n")
            stop = Nic
            dopóki nie stop:
                jeżeli self.cmdqueue:
                    line = self.cmdqueue.pop(0)
                inaczej:
                    jeżeli self.use_rawinput:
                        spróbuj:
                            line = input(self.prompt)
                        wyjąwszy EOFError:
                            line = 'EOF'
                    inaczej:
                        self.stdout.write(self.prompt)
                        self.stdout.flush()
                        line = self.stdin.readline()
                        jeżeli nie len(line):
                            line = 'EOF'
                        inaczej:
                            line = line.rstrip('\r\n')
                line = self.precmd(line)
                stop = self.onecmd(line)
                stop = self.postcmd(stop, line)
            self.postloop()
        w_końcu:
            jeżeli self.use_rawinput oraz self.completekey:
                spróbuj:
                    zaimportuj readline
                    readline.set_completer(self.old_completer)
                wyjąwszy ImportError:
                    dalej


    def precmd(self, line):
        """Hook method executed just before the command line jest
        interpreted, but after the input prompt jest generated oraz issued.

        """
        zwróć line

    def postcmd(self, stop, line):
        """Hook method executed just after a command dispatch jest finished."""
        zwróć stop

    def preloop(self):
        """Hook method executed once when the cmdloop() method jest called."""
        dalej

    def postloop(self):
        """Hook method executed once when the cmdloop() method jest about to
        return.

        """
        dalej

    def parseline(self, line):
        """Parse the line into a command name oraz a string containing
        the arguments.  Returns a tuple containing (command, args, line).
        'command' oraz 'args' may be Nic jeżeli the line couldn't be parsed.
        """
        line = line.strip()
        jeżeli nie line:
            zwróć Nic, Nic, line
        albo_inaczej line[0] == '?':
            line = 'help ' + line[1:]
        albo_inaczej line[0] == '!':
            jeżeli hasattr(self, 'do_shell'):
                line = 'shell ' + line[1:]
            inaczej:
                zwróć Nic, Nic, line
        i, n = 0, len(line)
        dopóki i < n oraz line[i] w self.identchars: i = i+1
        cmd, arg = line[:i], line[i:].strip()
        zwróć cmd, arg, line

    def onecmd(self, line):
        """Interpret the argument jako though it had been typed w response
        to the prompt.

        This may be overridden, but should nie normally need to be;
        see the precmd() oraz postcmd() methods dla useful execution hooks.
        The zwróć value jest a flag indicating whether interpretation of
        commands by the interpreter should stop.

        """
        cmd, arg, line = self.parseline(line)
        jeżeli nie line:
            zwróć self.emptyline()
        jeżeli cmd jest Nic:
            zwróć self.default(line)
        self.lastcmd = line
        jeżeli line == 'EOF' :
            self.lastcmd = ''
        jeżeli cmd == '':
            zwróć self.default(line)
        inaczej:
            spróbuj:
                func = getattr(self, 'do_' + cmd)
            wyjąwszy AttributeError:
                zwróć self.default(line)
            zwróć func(arg)

    def emptyline(self):
        """Called when an empty line jest entered w response to the prompt.

        If this method jest nie overridden, it repeats the last nonempty
        command entered.

        """
        jeżeli self.lastcmd:
            zwróć self.onecmd(self.lastcmd)

    def default(self, line):
        """Called on an input line when the command prefix jest nie recognized.

        If this method jest nie overridden, it prints an error message oraz
        returns.

        """
        self.stdout.write('*** Unknown syntax: %s\n'%line)

    def completedefault(self, *ignored):
        """Method called to complete an input line when no command-specific
        complete_*() method jest available.

        By default, it returns an empty list.

        """
        zwróć []

    def completenames(self, text, *ignored):
        dotext = 'do_'+text
        zwróć [a[3:] dla a w self.get_names() jeżeli a.startswith(dotext)]

    def complete(self, text, state):
        """Return the next possible completion dla 'text'.

        If a command has nie been entered, then complete against command list.
        Otherwise try to call complete_<command> to get list of completions.
        """
        jeżeli state == 0:
            zaimportuj readline
            origline = readline.get_line_buffer()
            line = origline.lstrip()
            stripped = len(origline) - len(line)
            begidx = readline.get_begidx() - stripped
            endidx = readline.get_endidx() - stripped
            jeżeli begidx>0:
                cmd, args, foo = self.parseline(line)
                jeżeli cmd == '':
                    compfunc = self.completedefault
                inaczej:
                    spróbuj:
                        compfunc = getattr(self, 'complete_' + cmd)
                    wyjąwszy AttributeError:
                        compfunc = self.completedefault
            inaczej:
                compfunc = self.completenames
            self.completion_matches = compfunc(text, line, begidx, endidx)
        spróbuj:
            zwróć self.completion_matches[state]
        wyjąwszy IndexError:
            zwróć Nic

    def get_names(self):
        # This method used to pull w base klasa attributes
        # at a time dir() didn't do it yet.
        zwróć dir(self.__class__)

    def complete_help(self, *args):
        commands = set(self.completenames(*args))
        topics = set(a[5:] dla a w self.get_names()
                     jeżeli a.startswith('help_' + args[0]))
        zwróć list(commands | topics)

    def do_help(self, arg):
        'List available commands przy "help" albo detailed help przy "help cmd".'
        jeżeli arg:
            # XXX check arg syntax
            spróbuj:
                func = getattr(self, 'help_' + arg)
            wyjąwszy AttributeError:
                spróbuj:
                    doc=getattr(self, 'do_' + arg).__doc__
                    jeżeli doc:
                        self.stdout.write("%s\n"%str(doc))
                        zwróć
                wyjąwszy AttributeError:
                    dalej
                self.stdout.write("%s\n"%str(self.nohelp % (arg,)))
                zwróć
            func()
        inaczej:
            names = self.get_names()
            cmds_doc = []
            cmds_undoc = []
            help = {}
            dla name w names:
                jeżeli name[:5] == 'help_':
                    help[name[5:]]=1
            names.sort()
            # There can be duplicates jeżeli routines overridden
            prevname = ''
            dla name w names:
                jeżeli name[:3] == 'do_':
                    jeżeli name == prevname:
                        kontynuuj
                    prevname = name
                    cmd=name[3:]
                    jeżeli cmd w help:
                        cmds_doc.append(cmd)
                        usuń help[cmd]
                    albo_inaczej getattr(self, name).__doc__:
                        cmds_doc.append(cmd)
                    inaczej:
                        cmds_undoc.append(cmd)
            self.stdout.write("%s\n"%str(self.doc_leader))
            self.print_topics(self.doc_header,   cmds_doc,   15,80)
            self.print_topics(self.misc_header,  list(help.keys()),15,80)
            self.print_topics(self.undoc_header, cmds_undoc, 15,80)

    def print_topics(self, header, cmds, cmdlen, maxcol):
        jeżeli cmds:
            self.stdout.write("%s\n"%str(header))
            jeżeli self.ruler:
                self.stdout.write("%s\n"%str(self.ruler * len(header)))
            self.columnize(cmds, maxcol-1)
            self.stdout.write("\n")

    def columnize(self, list, displaywidth=80):
        """Display a list of strings jako a compact set of columns.

        Each column jest only jako wide jako necessary.
        Columns are separated by two spaces (one was nie legible enough).
        """
        jeżeli nie list:
            self.stdout.write("<empty>\n")
            zwróć

        nonstrings = [i dla i w range(len(list))
                        jeżeli nie isinstance(list[i], str)]
        jeżeli nonstrings:
            podnieś TypeError("list[i] nie a string dla i w %s"
                            % ", ".join(map(str, nonstrings)))
        size = len(list)
        jeżeli size == 1:
            self.stdout.write('%s\n'%str(list[0]))
            zwróć
        # Try every row count z 1 upwards
        dla nrows w range(1, len(list)):
            ncols = (size+nrows-1) // nrows
            colwidths = []
            totwidth = -2
            dla col w range(ncols):
                colwidth = 0
                dla row w range(nrows):
                    i = row + nrows*col
                    jeżeli i >= size:
                        przerwij
                    x = list[i]
                    colwidth = max(colwidth, len(x))
                colwidths.append(colwidth)
                totwidth += colwidth + 2
                jeżeli totwidth > displaywidth:
                    przerwij
            jeżeli totwidth <= displaywidth:
                przerwij
        inaczej:
            nrows = len(list)
            ncols = 1
            colwidths = [0]
        dla row w range(nrows):
            texts = []
            dla col w range(ncols):
                i = row + nrows*col
                jeżeli i >= size:
                    x = ""
                inaczej:
                    x = list[i]
                texts.append(x)
            dopóki texts oraz nie texts[-1]:
                usuń texts[-1]
            dla col w range(len(texts)):
                texts[col] = texts[col].ljust(colwidths[col])
            self.stdout.write("%s\n"%str("  ".join(texts)))
